"""
M17 -- resolving power: can an observable answer the question being asked of it?

An observable is only as informative as the ratio between how much it MOVES
across the conditions of interest and how much it scatters when nothing
physical is changing. Both halves are measurable in this archive, so the
question is arithmetic rather than judgement:

  dynamic range   ln(max/min) of the per-condition mean across the sweep
  block noise     relative scatter between blocks at FIXED conditions
  ratio           the range expressed in block-noise units

Log space throughout, because these are multiplicative quantities; mixing a
log ratio for one observable against a fractional range for another is what
made the first draft of this analysis wrong.

The second half of the module tests an assumption rather than an observable.
Bounds that absorb block scatter by inflating errors (the sqrt(chi2) rescale
in `beta`, `global_fit`, `ruler`, `stark`) are applying the right remedy only
if that scatter is INDEPENDENT between blocks -- independent noise averages
down as 1/sqrt(N), a systematic common to every peak at a given setting does
not average at all. `averaging_test` puts a permutation null under that
assumption.

Both functions are pure: they take frames or arrays and return numbers, so
the script drives them and the tests can inject synthetic data with a known
answer.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def block_noise(frame, col: str, group: str = "peak") -> float:
    """Relative scatter between blocks at fixed conditions, averaged over groups.

    `frame` must already be restricted to one physical condition (e.g. the
    130 C power ladder, where width is power-independent by the C3 null, so
    whatever separates the blocks is instrumental).
    """
    g = frame.groupby(group)[col]
    return float((g.std() / g.mean()).mean())


def dynamic_range(frame, col: str, by: str) -> float:
    """ln(max/min) of the per-`by` mean of `col` -- the signal, in log space."""
    per = frame.groupby(by)[col].mean()
    return float(np.log(per.max() / per.min()))


def verdict(ratio: float) -> str:
    """Three coarse bands. The boundaries are conventions, not physics: 3 is
    where a signal starts to stand out of block scatter at all, 10 is where it
    does so with margin enough to carry a measurement rather than a bound."""
    if ratio > 10:
        return "RESOLVES"
    return "MARGINAL" if ratio > 3 else "CANNOT_RESOLVE"


def variance_reduction(resid: np.ndarray) -> float:
    """How much the scatter shrinks when the rows are averaged.

    `resid` is (n_groups, n_conditions), each row already mean-zero. Under
    independence this is sqrt(n_groups); if every row carries the same
    per-condition systematic it is 1.
    """
    resid = np.asarray(resid, dtype=float)
    return float(resid.std(ddof=1) / resid.mean(axis=0).std(ddof=1))


def averaging_test(resid: np.ndarray, n_perm: int = 20000,
                   seed: int = 1) -> dict:
    """Does the block scatter average down, or is part of it common?

    Permuting each row independently across conditions destroys any common
    per-condition component while preserving each row's own distribution --
    that is the independence null. A LOW observed reduction relative to the
    null indicates a shared systematic, so the p-value is left-tailed.

    Returns the observed statistic, the null's median and 90% band, and p.
    The band matters as much as p: with few groups and few conditions the
    null itself is wide, and a test that cannot resolve the question should
    say so rather than return a reassuring p.
    """
    resid = np.asarray(resid, dtype=float)
    obs = variance_reduction(resid)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = variance_reduction(
            np.array([rng.permutation(row) for row in resid]))
    return {
        "observed": obs,
        "null_median": float(np.median(null)),
        "null_lo90": float(np.percentile(null, 5)),
        "null_hi90": float(np.percentile(null, 95)),
        "p_common": float((null <= obs).mean()),
    }


def common_variance_fraction(observed: float, n_groups: int) -> float:
    """Fraction of the block variance shared across groups, from `observed`.

    var(mean) = var_common + var_indep/n, so with f = var_common/var_total
    the reduction R satisfies 1/R^2 = f + (1-f)/n. A point estimate only --
    it is meaningless unless `averaging_test` shows the null is narrow enough
    to resolve it, which for four peaks and five powers it is not.
    """
    inv = 1.0 / observed**2
    f = (inv - 1.0 / n_groups) / (1.0 - 1.0 / n_groups)
    return float(min(max(f, 0.0), 1.0))


def projection(signal_mhz: Sequence[float], noise_mhz: float,
               noise_cut: float = 1.0) -> list:
    """Signal-to-block-noise for a set of candidate signal sizes."""
    return [float(s / (noise_mhz / noise_cut)) for s in signal_mhz]
