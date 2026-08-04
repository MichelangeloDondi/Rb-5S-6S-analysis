"""
Residual-tail trimming (module M2b, remedy layer)
=================================================

A triangular sweep whose apex falls inside the acquisition window re-crosses
the same frequencies in reverse, so a copy of the line reappears reflected
about the apex. Where that copy lands outside the fitted structure it is
unmodelled signal sitting in the residual, and a least-squares fit pays for it
by moving the parameters that CAN reach it: the tooth spacing of a comb, the
wings of a line, the background under both.

This module cuts such a tail out of the fit sample. It never removes a trace
and it never writes a quality flag. It is a remedy, and the pre-registration
(docs/notes/ruler_validity_and_trim_prereg.md, sections 5 and 6 and amendment
2) forbids it from entering `hard_flags`, where an exclusion gate would read it
as a class of failure and empty its own census.

Three functions, in the order they compose:

* :func:`cusum_onset` finds where a sustained positive excursion begins in a
  residual. One-sided, because a mirror ADDS signal.
* :func:`tail_trim` walks outward from a guarded core on each side of the
  window independently and turns onsets into a sample mask, refusing any cut
  that would reach too far in.
* :func:`envelope_residual` builds a residual with no lineshape model in it, so
  the quality pass can use the same detector while staying physics blind.

SUSTAINED MEANS LASTING, NOT LARGE. The accepted run is one whose cumulative
sum keeps rising for at least `TRIM_MIN_RUN` samples after the onset. A point
glitch is spread over exactly `TRIM_SMOOTH_W` samples by the smoother, so it
can accumulate for at most that many however tall it is, and the minimum run
sits above the smoother width. That is why the detector is immune to a spike
rather than merely resistant to a small one.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from . import config as C
from .qc import boxcar


TRIM_REASONS = (
    "sustained positive residual, upper tail",
    "sustained positive residual, lower tail",
    "sustained positive residual, both tails",
    "refused, trim would reach into the guarded half",
    "not applicable, multi-peak trace",
)
"""Closed vocabulary for `trim_reason`. The empty string means no trim was
taken and none was refused. Adding a token is a change to the pre-registration
first."""


def _robust_sigma(x: np.ndarray) -> float:
    """Scaled median absolute deviation of the RAW residual.

    The order matters and it is fixed here. The residual is normalized by its
    own sample noise FIRST and smoothed afterwards, so one unit of the
    accumulated statistic is one sample sigma of the trace. Smoothing then
    divides the noise by the root of the window while leaving any feature wider
    than the window untouched, which is what puts the detector's allowance
    (half a sample sigma) far above the smoothed noise and far below any real
    structure. Normalizing after smoothing instead would rescale the noise back
    up and leave the threshold to absorb the smoother's own correlation, which
    made it a factor of twenty larger and strongly dependent on how much tail
    happened to be scanned.
    """
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return 0.0
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def cusum_onset(resid: np.ndarray, *, sigma: Optional[float] = None,
                smooth_w: int = C.TRIM_SMOOTH_W,
                drift: float = C.TRIM_CUSUM_DRIFT,
                h: float = C.TRIM_CUSUM_H,
                min_run: int = C.TRIM_MIN_RUN) -> Optional[int]:
    """Index at which a sustained POSITIVE excursion begins, or None.

    `resid` is a signed residual in the trace's own units, scanned in the order
    given. Callers that walk outward from a core pass the reversed slice.

    The statistic is the standard one-sided cumulative sum with reset,
    S_i = max(0, S_(i-1) + z_i - drift), computed here in closed form as
    S = c - running_min(c) with c the cumulative sum of z - drift. Only
    positive excursions accumulate, because a retrace mirror adds signal and a
    negative excursion is not the defect being looked for.

    A crossing of `h` is ACCEPTED only when the excursion's cumulative sum is
    still rising `min_run` samples after the onset. A rejected crossing resets
    the detector past itself rather than being scanned again, so one glitch
    cannot be re-read as a tail once the smoother's own footprint has passed.
    """
    z = np.asarray(resid, dtype=float)
    if z.size == 0:
        return None
    s0 = _robust_sigma(z) if sigma is None else float(sigma)
    if not np.isfinite(s0) or s0 <= 0:
        return None
    z = boxcar(z / s0, smooth_w)

    start, n = 0, z.size
    while start < n:
        seg = z[start:]
        # c[i] is the accumulated excess after consuming seg[:i], so c[0] = 0
        # and an onset at c-index i means the excursion starts at seg[i].
        c = np.concatenate([[0.0], np.cumsum(seg - drift)])
        m = np.minimum.accumulate(c)
        s = c - m
        idx = np.arange(c.size)
        reset = np.maximum.accumulate(np.where(c <= m, idx, 0))
        cross = np.flatnonzero(s >= h)
        if cross.size == 0:
            return None
        ic = int(cross[0])
        i0 = int(reset[ic])
        # the excursion ends where the statistic returns to its reset level
        back = np.flatnonzero(s[ic:] <= 0.0)
        iend = ic + int(back[0]) if back.size else c.size - 1
        imax = i0 + int(np.argmax(s[i0:iend + 1]))
        if imax - i0 >= min_run:
            return start + i0
        start += ic + 1
    return None


def tail_trim(t_ms: np.ndarray, resid: np.ndarray, core_lo: int, core_hi: int,
              **kw) -> Dict:
    """Trim sustained residual tails outside a guarded core, each side alone.

    `core_lo` and `core_hi` are SAMPLE INDICES bounding the inviolable core,
    inclusive. Nothing inside them is ever cut: on a ruler the core is the
    fitted comb span widened by the fitted tooth width, on a line it is the
    fitted centre widened by `TRIM_CORE_GUARD_FWHM_MULT` full widths, and in
    both cases the guard is what keeps the trimmer away from the signal it is
    protecting.

    REFUSING IS THE DEFAULT. A cut is taken only if it starts beyond half the
    distance from the core edge to the window edge. A tail that begins closer
    in than that is not a tail, it is the thing being measured, and the trace
    is reported untrimmed with the refusal recorded. That is the standing rule
    of section 5 and it is why a trimmer cannot quietly eat a dim cold line.

    Returns `trimmed`, the keep-`mask`, the KEPT interval as `trim_start_ms`
    and `trim_end_ms` (both nan when nothing was cut), `trim_reason` from
    :data:`TRIM_REASONS`, and `n_trimmed`.
    """
    t_ms = np.asarray(t_ms, dtype=float)
    resid = np.asarray(resid, dtype=float)
    n = resid.size
    mask = np.ones(n, dtype=bool)
    out = {"trimmed": False, "mask": mask, "n_trimmed": 0,
           "trim_start_ms": float("nan"), "trim_end_ms": float("nan"),
           "trim_reason": ""}
    core_lo = int(np.clip(core_lo, 0, n - 1))
    core_hi = int(np.clip(core_hi, 0, n - 1))
    if core_hi < core_lo:
        core_lo, core_hi = core_hi, core_lo

    # One noise scale for the whole trace, estimated once and shared by both
    # sides. Estimating it inside each slice would let a mirror that fills one
    # tail set the scale it is then measured against, which is the way a strong
    # contaminant hides itself from a robust statistic.
    kw.setdefault("sigma", _robust_sigma(resid))

    refused, cut_hi, cut_lo = False, None, None

    # upper side: scan outward from the core edge toward the last sample
    room = n - 1 - core_hi
    if room > 0:
        j = cusum_onset(resid[core_hi:], **kw)
        if j is not None:
            i = core_hi + j
            if i - core_hi >= 0.5 * room:
                cut_hi = i
            else:
                refused = True

    # lower side: the same scan, walking outward means walking backwards
    room = core_lo
    if room > 0:
        j = cusum_onset(resid[:core_lo + 1][::-1], **kw)
        if j is not None:
            i = core_lo - j
            if core_lo - i >= 0.5 * room:
                cut_lo = i
            else:
                refused = True

    if cut_hi is None and cut_lo is None:
        out["trim_reason"] = TRIM_REASONS[3] if refused else ""
        return out

    if cut_hi is not None:
        mask[cut_hi:] = False
    if cut_lo is not None:
        mask[:cut_lo + 1] = False
    kept = np.flatnonzero(mask)
    out.update(trimmed=True, mask=mask, n_trimmed=int(n - kept.size),
               trim_start_ms=float(t_ms[kept[0]]),
               trim_end_ms=float(t_ms[kept[-1]]))
    if cut_hi is not None and cut_lo is not None:
        out["trim_reason"] = TRIM_REASONS[2]
    elif cut_hi is not None:
        out["trim_reason"] = TRIM_REASONS[0]
    else:
        out["trim_reason"] = TRIM_REASONS[1]
    return out


def _isotonic_decreasing(y: np.ndarray) -> np.ndarray:
    """Least-squares fit of a non-increasing sequence (pool adjacent violators).

    This is the whole model: away from its own maximum a single line goes down
    and does not come back up. Fitting that and nothing else keeps the quality
    pass physics blind, which is the property that lets a QC exclusion stay
    unbiased.
    """
    y = np.asarray(y, dtype=float)
    if y.size == 0:
        return y
    vals = np.empty(y.size)
    wts = np.empty(y.size)
    lens = np.empty(y.size, dtype=int)
    k = 0
    for x in y:
        vals[k], wts[k], lens[k] = x, 1.0, 1
        k += 1
        while k > 1 and vals[k - 2] < vals[k - 1]:
            w = wts[k - 2] + wts[k - 1]
            vals[k - 2] = (vals[k - 2] * wts[k - 2] + vals[k - 1] * wts[k - 1]) / w
            wts[k - 2], lens[k - 2] = w, lens[k - 2] + lens[k - 1]
            k -= 1
    return np.repeat(vals[:k], lens[:k])


def _wing_trend(t_ms: np.ndarray, v: np.ndarray, sm: np.ndarray) -> np.ndarray:
    """Linear background fitted on the wings, evaluated everywhere.

    The wings are the samples the quality module already calls signal-free, so
    the trend is fitted where there is nothing but background to fit. With too
    few of them the trace is signal everywhere and the trend is taken as flat,
    which is the conservative answer: a flat trend can only make the detector
    fire more readily, and refusing is still the standing rule.
    """
    from .qc import wing_mask
    w = wing_mask(v)
    if w.sum() < 50:
        return np.zeros_like(sm)
    p = np.polyfit(t_ms[w], v[w], 1)
    return np.polyval(p, t_ms)


def envelope_residual(t_ms: np.ndarray, v: np.ndarray,
                      smooth_w: int = C.TRIM_SMOOTH_W) -> np.ndarray:
    """Residual against a model-free decaying envelope, for the quality pass.

    The smoothed trace is split at its own maximum and each side is fitted with
    the best non-increasing sequence away from that maximum. Subtracting that
    envelope from the RAW trace leaves a residual that is sample noise on a
    single line however wide, however bright and whatever its shape, and a
    sustained positive excursion wherever a second structure sits.

    A LINEAR BACKGROUND is removed first, on the wings, and put back after.
    Every physics fit in this repository carries a linear background term, so a
    stand-in for them has to as well. Without it the envelope is monotone while
    the trace is not, a background rising by a per cent of the line height
    across the window violates the model by construction, and on a bright trace
    that is several sigma of sustained positive residual. Measured on the
    archive before this term was added: the traces the detector cut had nine
    times the median background slope of the traces it left alone, and only
    four of thirty-eight carried a second structure the quality module could
    also see.

    Three further properties earn this over the obvious alternatives.
    Subtracting a BASELINE instead of an envelope would read a Lorentzian's own
    far tail as a tail to be cut, which is the trap the quality module's step
    detector already fell into once. Taking a running minimum outward would put
    the envelope below the noise and leave a residual positive by construction,
    so the detector would fire on noise alone. And the subtraction is from the
    RAW trace rather than the smoothed one because the monotone fit reproduces
    a strictly falling flank exactly, so a smoothed-minus-envelope residual is
    identically zero over most of a clean trace and its median absolute
    deviation collapses to a tenth of the real noise, making every excursion
    read as ten sigma.
    """
    v = np.asarray(v, dtype=float)
    sm = boxcar(v, smooth_w)
    trend = _wing_trend(t_ms, v, sm)
    flat = sm - trend
    ipk = int(np.argmax(flat))
    env = np.empty_like(flat)
    env[ipk:] = _isotonic_decreasing(flat[ipk:])
    env[:ipk + 1] = _isotonic_decreasing(flat[:ipk + 1][::-1])[::-1]
    return v - trend - env
