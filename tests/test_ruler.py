"""
Closure tests for the M2 ruler core (rb5s6s/ruler.py).

Before a single real ruler is fit, the comb machinery must recover KNOWN
tooth spacings injected into campaign-like synthetics: warm bright combs,
cold dim combs (init fallback path), suppressed carriers, missing outer
teeth, and block combination with propagated errors.
"""

from __future__ import annotations

import numpy as np

from rb5s6s import config as C
from rb5s6s.ruler import (combine_block, estimate_delta_acf, fit_comb,
                          fit_comb_free_centers)

T_MS = np.arange(2000) * 0.5 - 500.0


def synth_comb(delta=147.3, t0=150.0, w=55.0,
               heights=(0.02, 0.09, 0.06, 0.09, 0.02),
               base=0.005, noise=0.004, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    v = np.full_like(T_MS, base)
    for n, h in zip(range(-2, 3), heights):
        x = 2.0 * (T_MS - (t0 + n * delta)) / w
        v = v + h / (1.0 + x * x)
    return v + rng.normal(0.0, noise, len(T_MS))


def test_acf_init_finds_spacing():
    got = estimate_delta_acf(T_MS, synth_comb())
    assert not got["fallback"]
    assert abs(got["delta_ms"] - 147.3) < 4.0


def test_warm_comb_recovery_and_pull():
    # Across seeds: |delta_fit - truth| must stay within ~3 reported sigmas
    # and the reported error itself must be sub-ms for bright combs.
    pulls = []
    for seed in range(1, 9):
        f = fit_comb(T_MS, synth_comb(seed=seed))
        assert f["delta_err_ms"] < 1.5
        pulls.append((f["delta_ms"] - 147.3) / f["delta_err_ms"])
    pulls = np.abs(pulls)
    assert pulls.max() < 3.5, pulls
    assert pulls.mean() < 1.5, pulls  # errors not wildly over/under-stated


def test_suppressed_carrier_no_bias():
    # HWP trick: carrier much weaker than sidebands must not bias delta.
    f = fit_comb(T_MS, synth_comb(heights=(0.02, 0.09, 0.015, 0.09, 0.02)))
    assert abs(f["delta_ms"] - 147.3) < 1.0


def test_missing_outer_teeth_no_bias():
    f = fit_comb(T_MS, synth_comb(heights=(0.0, 0.09, 0.06, 0.09, 0.0)))
    assert abs(f["delta_ms"] - 147.3) < 1.0


def test_cold_comb_fallback_path_converges():
    # Cold-block regime: teeth ~3x noise; ACF init may fall back — the fit
    # must still land within a few ms of truth.
    f = fit_comb(T_MS, synth_comb(heights=(0.004, 0.0085, 0.006, 0.008, 0.004),
                                  noise=0.0016, seed=3))
    assert abs(f["delta_ms"] - 147.3) < 4.0


def test_free_centers_recover_linear_comb():
    # On a perfectly linear comb the freed centers must sit at t0 + n*Δ, so
    # their departures (the nonlinearity-map input) are consistent with zero.
    v = synth_comb(delta=147.3, t0=150.0)
    base = fit_comb(T_MS, v)
    fc = fit_comb_free_centers(T_MS, v, base)
    assert len(fc["n"]) >= 3
    for n, c, e in zip(fc["n"], fc["centers_ms"], fc["center_err_ms"]):
        predicted = base["t0_ms"] + n * base["delta_ms"]
        assert abs(c - predicted) < max(3.0, 3.5 * e), (n, c, predicted, e)


def test_free_centers_detect_injected_nonlinearity():
    # Warp the axis quadratically: teeth placed at physical positions that
    # curve away from a straight ruler. The freed centers must reproduce the
    # curvature (departure grows toward the window edges), not flatten it.
    rng = np.random.default_rng(C.RNG_SEED)
    t0, d, curv = 150.0, 147.3, 4e-4  # ms per (n^2)
    centers = [t0 + n * d + curv * (n * d) ** 2 for n in range(-2, 3)]
    v = np.full_like(T_MS, 0.005)
    for c, h in zip(centers, (0.02, 0.09, 0.06, 0.09, 0.02)):
        v = v + h / (1.0 + (2.0 * (T_MS - c) / 55.0) ** 2)
    v = v + rng.normal(0.0, 0.004, len(T_MS))
    base = fit_comb(T_MS, v)
    fc = fit_comb_free_centers(T_MS, v, base)
    # the outermost freed tooth must show a clearly nonzero departure
    departs = [c - (base["t0_ms"] + n * base["delta_ms"])
               for n, c in zip(fc["n"], fc["centers_ms"])]
    assert max(abs(min(departs)), abs(max(departs))) > 2.0


def test_block_combination_scatter_inflation():
    fits = [fit_comb(T_MS, synth_comb(t0=150.0 + drift, seed=seed))
            for seed, drift in zip((1, 2, 3, 4, 5), (-15, -5, 0, 5, 15))]
    blk = combine_block(fits)
    assert abs(blk["delta_ms"] - 147.3) < 0.6
    assert blk["delta_err_ms"] <= min(f["delta_err_ms"] for f in fits)
    # inject one inconsistent trace: the combined error must GROW
    bad = dict(fits[0]); bad["delta_ms"] += 5.0
    blk2 = combine_block(fits[1:] + [bad])
    assert blk2["delta_err_ms"] > blk["delta_err_ms"]
    assert blk2["block_chi2_red"] > 3.0


# --------------------------------------------------------------------------
# The sweep-linearity bound quoted in fig8 and the prose must match the map.
# --------------------------------------------------------------------------
# Raised 2026-07-22: fig8's right panel showed a rightmost error bar of +/-0.74%
# under a title claiming "<=0.4%", which reads as the figure refuting itself.
# The bar is NOT anomalous (n=5, 0.9 sigma from the 1/sqrt(n) law, and its
# CENTRAL value is inside the band) -- but the sparse edge windows cannot test
# a bound their own errors exceed, so the claim belongs to the well-sampled
# windows and the number has to be the one they actually support.
def test_linearity_bound_matches_the_wellsampled_windows():
    import csv
    import sys
    import numpy as np
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    rows = list(csv.DictReader(open(root / "results" / "ruler_nlmap.csv")))
    n = np.array([int(r["n"]) for r in rows])
    dev = np.abs(np.array([float(r["rate_rel"]) for r in rows]) - 1.0)
    err = np.array([float(r["rate_rel_err"]) for r in rows])

    from make_figures import N_WELL_SAMPLED  # the split fig8 draws
    well = n >= N_WELL_SAMPLED
    assert well.sum() >= 5, "too few well-sampled windows to set a bound"
    # the quoted 0.45% must cover them, and not be loose by more than ~0.1%
    assert dev[well].max() <= 0.0045 + 1e-9, (
        f"a well-sampled window deviates {dev[well].max():.4%}, beyond the "
        f"quoted 0.45% -- update the bound in fig8, DATA.md, PAPER1_SKELETON "
        f"and make_results_ledger.py together")
    assert dev[well].max() > 0.0035, (
        "the bound is now loose; requote it nearer the data")
    # the sparse windows are the ones whose errors exceed the bound: that is
    # the whole reason they are drawn differently
    assert err[~well].max() > 0.0045, (
        "sparse-window errors no longer exceed the bound; the fig8 split by "
        "N_WELL_SAMPLED may no longer be warranted")


def test_fig8_legends_are_opaque():
    """rcParams sets legend.frameon False globally, which silently defeats
    framealpha and let plotted data show through fig8's legend text."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "scripts"
           / "make_figures.py").read_text(encoding="utf-8")
    for m in re.finditer(r"\.legend\(([^)]*framealpha[^)]*)\)", src):
        assert "frameon=True" in m.group(1), (
            "a legend asks for framealpha while legend.frameon is globally "
            f"False, so it draws no frame at all: {m.group(0)}")
