"""
Frequency-axis calibration from EOM ruler traces (module M2, core)
==================================================================

Each RF-on "ruler" trace holds up to five two-photon comb teeth spaced
exactly 6.25 MHz apart on the laser axis (constants.TOOTH_SPACING_LASER_HZ,
RF-oscillator exact). Measuring the tooth spacing Δ in milliseconds
calibrates the sweep: rate = 6.25 MHz / Δ. This module implements the
staged per-trace protocol of docs/PLAN.md M2 (stages 1-2 and 6; the shape
ladder and free-center diagnostic extend it):

1. ROBUST INIT — never threshold peak-picking:
   * Δ from the autocorrelation of the baseline-subtracted smoothed trace,
     searched ONLY inside config.RULER_DELTA_RANGE_MS. Verified necessity:
     an unrestricted search lets comb periodicity lock onto multiples, and
     cold-block alignment locked 3/5 traces one tooth off (independent
     audit, 2026-07-11). Weak-carrier traces are handled for free — the
     autocorrelation uses all teeth at once.
   * comb phase t0 from a direct grid scan of the summed smoothed signal at
     the 5 predicted tooth positions.
2. CONSTRAINED SIMULTANEOUS FIT — one model for the whole trace: centers
   t0 + n*Δ (n = -2..+2), ONE shared Lorentzian tooth shape (all teeth are
   the same physical line excited via different photon pairs), free
   non-negative per-tooth heights, linear background. Simultaneous fitting
   is mandatory: at ~147 ms spacing and ~60 ms width, a strong tooth's wing
   under a weak neighbor is ~20% of the weak peak — single-tooth fits or
   maxima-reading pull centers by O(ms).
   Weights come from M1's noise law (rb5s6s.noise); parameter errors are
   inflated by sqrt(tau_int) for the measured wing-noise correlation and by
   sqrt(chi2_red) when the fit is imperfect (conservative).
3. BLOCK COMBINATION — inverse-variance mean of per-trace Δ with scatter
   inflation when the block chi2_red exceeds 1 (PDG-style conservative).

Everything here returns milliseconds; the conversion to MHz/ms happens at
the caller with the exact 6.25 MHz constant, so no frequency conventions
can leak in silently.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from .noise import signal_level, sigma_of_v
from .qc import boxcar
from .fitutil import cov_from_jac, feasible_p0


# ---------------------------------------------------------------------------
# stage 1 — robust initialization
# ---------------------------------------------------------------------------

def estimate_delta_acf(t_ms: np.ndarray, v: np.ndarray) -> Dict:
    """Tooth period from the autocorrelation, restricted to the physical
    search window. Returns {'delta_ms', 'score', 'fallback'}; on a weak
    autocorrelation (cold rulers) falls back to the campaign default and
    says so."""
    lev, _ = signal_level(v)
    x = boxcar(lev, 5)
    x = x - x.mean()
    n = len(x)
    acf = np.correlate(x, x, mode="full")[n - 1:]
    acf = acf / acf[0] if acf[0] > 0 else acf
    dt = t_ms[1] - t_ms[0]
    lo = int(C.RULER_DELTA_RANGE_MS[0] / dt)
    hi = min(int(C.RULER_DELTA_RANGE_MS[1] / dt), n - 1)
    seg = acf[lo:hi]
    if len(seg) == 0 or np.max(seg) < C.RULER_ACF_MIN_SCORE:
        return {"delta_ms": C.RULER_DELTA_FALLBACK_MS,
                "score": float(np.max(seg)) if len(seg) else 0.0, "fallback": True}
    return {"delta_ms": float((lo + int(np.argmax(seg))) * dt),
            "score": float(np.max(seg)), "fallback": False}


def estimate_t0(t_ms: np.ndarray, v: np.ndarray, delta_ms: float) -> float:
    """Comb phase by brute-force scan: t0 maximizing the summed smoothed
    signal at the five predicted tooth positions (teeth outside the window
    simply do not contribute)."""
    lev, _ = signal_level(v)
    sm = boxcar(lev, C.QC_SMOOTH_W)
    best_t0, best_score = t_ms[0], -np.inf
    for t0 in np.arange(t_ms[0], t_ms[0] + delta_ms, 2.0):
        pos = t0 + delta_ms * np.arange(-2, 3)
        inside = (pos >= t_ms[0]) & (pos <= t_ms[-1])
        if not inside.any():
            continue
        score = float(np.sum(np.interp(pos[inside], t_ms, sm)))
        if score > best_score:
            best_score, best_t0 = score, float(t0)
    # fold t0 to the tooth nearest the window center for identifiability
    center = 0.5 * (t_ms[0] + t_ms[-1])
    k = round((center - best_t0) / delta_ms)
    return float(best_t0 + k * delta_ms)


# ---------------------------------------------------------------------------
# stage 2 — constrained simultaneous comb fit
# ---------------------------------------------------------------------------

def _comb(t_ms, t0, delta, w, heights, b0, b1):
    out = b0 + b1 * (t_ms - t_ms[0])
    for n, h in zip(range(-2, 3), heights):
        x = 2.0 * (t_ms - (t0 + n * delta)) / w
        out = out + h / (1.0 + x * x)
    return out


def fit_comb(t_ms: np.ndarray, v: np.ndarray, law: Optional[Dict] = None) -> Dict:
    """Weighted constrained comb fit of one ruler trace.

    Returns delta_ms, delta_err_ms (tau_int- and chi2-inflated), t0_ms,
    width_ms, heights (5), chi2_red, init metadata. Raises RuntimeError if
    the optimizer fails — callers must not silently skip rulers.
    """
    init = estimate_delta_acf(t_ms, v)
    d0 = init["delta_ms"]
    t00 = estimate_t0(t_ms, v, d0)

    lev, base = signal_level(v)
    if law is not None:
        sig = sigma_of_v(np.maximum(lev, 0.0), law)
        tau = max(law.get("tau_int", 1.0), 1.0)
    else:  # flat weights fallback (closure tests may run law-free)
        sig = np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6))
        tau = 1.0

    sm = boxcar(lev, C.QC_SMOOTH_W)
    h0 = np.clip(np.interp(t00 + d0 * np.arange(-2, 3), t_ms, sm), 1e-4, None)

    p0 = np.concatenate([[t00, d0, C.RULER_TOOTH_WIDTH_INIT_MS], h0, [base, 0.0]])
    lo = np.concatenate([[t00 - d0 / 2, C.RULER_DELTA_RANGE_MS[0], 15.0],
                         np.zeros(5), [-np.inf, -np.inf]])
    hi = np.concatenate([[t00 + d0 / 2, C.RULER_DELTA_RANGE_MS[1], 120.0],
                         np.full(5, np.inf), [np.inf, np.inf]])

    def resid(p):
        return (v - _comb(t_ms, p[0], p[1], p[2], p[3:8], p[8], p[9])) / sig

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds (round-5 fix)
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=20000)
    if not sol.success:
        raise RuntimeError(f"comb fit failed: {sol.message}")

    dof = max(len(v) - len(p0), 1)
    chi2_red = float(2.0 * sol.cost / dof)
    # covariance from the whitened Jacobian (SVD, robust to parameter scale);
    # conservative double inflation
    cov = cov_from_jac(sol.jac)
    infl = np.sqrt(max(chi2_red, 1.0)) * np.sqrt(tau)
    return {
        "delta_ms": float(sol.x[1]),
        "delta_err_ms": float(np.sqrt(max(cov[1, 1], 0.0)) * infl),
        "t0_ms": float(sol.x[0]),
        "width_ms": float(sol.x[2]),
        "heights": sol.x[3:8].tolist(),
        "b0": float(sol.x[8]), "b1": float(sol.x[9]),
        "chi2_red": chi2_red,
        "init_fallback": init["fallback"],
        "acf_score": init["score"],
    }


# ---------------------------------------------------------------------------
# stage 4 — free-center diagnostic (feeds the sweep-nonlinearity map)
# ---------------------------------------------------------------------------

def _comb_free(t_ms, centers, w, heights, b0, b1):
    out = b0 + b1 * (t_ms - t_ms[0])
    for c, h in zip(centers, heights):
        x = 2.0 * (t_ms - c) / w
        out = out + h / (1.0 + x * x)
    return out


def fit_comb_free_centers(t_ms: np.ndarray, v: np.ndarray, base_fit: Dict,
                          law: Optional[Dict] = None) -> Dict:
    """Refit with each tooth's CENTER free (shape width still shared), seeded
    from the constrained fit. Only teeth whose seeded center lies inside the
    window AND whose fitted height in `base_fit` is a real signal (> a small
    fraction of the max height) are freed — outer teeth that fell off the
    window or into the noise are dropped, not fit to noise.

    Returns per-tooth centers with errors and their n-indices. The
    center-vs-(t0+nΔ) residuals are the local departures from a linear sweep
    — pooled across all ruler traces (whose combs sit at different window
    positions from drift + recentering) they stitch the ν(t) nonlinearity
    map (plan M2 stage 4 / the recenter-enabled ensemble stitch)."""
    t0, d, w = base_fit["t0_ms"], base_fit["delta_ms"], base_fit["width_ms"]
    heights = np.array(base_fit["heights"])
    hmax = heights.max() if heights.size else 0.0
    ns, seeds, h0 = [], [], []
    for i, n in enumerate(range(-2, 3)):
        c = t0 + n * d
        if t_ms[0] <= c <= t_ms[-1] and heights[i] > C.RULER_FREE_MIN_HEIGHT_FRAC * hmax:
            ns.append(n); seeds.append(c); h0.append(max(heights[i], 1e-4))
    if len(ns) < 2:
        return {"n": [], "centers_ms": [], "center_err_ms": [], "width_ms": w}

    lev, base = signal_level(v)
    if law is not None:
        sig = sigma_of_v(np.maximum(lev, 0.0), law)
        tau = max(law.get("tau_int", 1.0), 1.0)
    else:
        sig = np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)); tau = 1.0

    nt = len(ns)
    p0 = np.concatenate([seeds, [w], h0, [base_fit["b0"], base_fit["b1"]]])
    lo = np.concatenate([np.array(seeds) - d / 2, [15.0], np.zeros(nt), [-np.inf, -np.inf]])
    hi = np.concatenate([np.array(seeds) + d / 2, [120.0], np.full(nt, np.inf), [np.inf, np.inf]])

    def resid(p):
        return (v - _comb_free(t_ms, p[:nt], p[nt], p[nt + 1:2 * nt + 1],
                               p[2 * nt + 1], p[2 * nt + 2])) / sig

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds (round-5 fix)
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=20000)
    if not sol.success:
        raise RuntimeError(f"free-center fit failed: {sol.message}")
    dof = max(len(v) - len(p0), 1)
    chi2_red = float(2.0 * sol.cost / dof)
    cov = cov_from_jac(sol.jac)
    infl = np.sqrt(max(chi2_red, 1.0)) * np.sqrt(tau)
    return {
        "n": ns,
        "centers_ms": sol.x[:nt].tolist(),
        "center_err_ms": [float(np.sqrt(max(cov[i, i], 0.0)) * infl) for i in range(nt)],
        "width_ms": float(sol.x[nt]),
        "chi2_red": chi2_red,
    }


# ---------------------------------------------------------------------------
# stage 6 — block combination
# ---------------------------------------------------------------------------

def combine_block(fits: List[Dict]) -> Dict:
    """Inverse-variance mean of per-trace delta with PDG-style scatter
    inflation: if the block chi2_red > 1, the combined error is scaled by
    sqrt(chi2_red) so genuine trace-to-trace inconsistency widens the error
    instead of being averaged away."""
    d = np.array([f["delta_ms"] for f in fits])
    e = np.array([f["delta_err_ms"] for f in fits])
    w = 1.0 / np.maximum(e, 1e-9) ** 2
    mean = float(np.sum(w * d) / np.sum(w))
    err = float(1.0 / np.sqrt(np.sum(w)))
    chi2_red = float(np.sum(w * (d - mean) ** 2) / max(len(d) - 1, 1))
    if chi2_red > 1.0:
        err *= np.sqrt(chi2_red)
    return {"delta_ms": mean, "delta_err_ms": err,
            "block_chi2_red": chi2_red, "n": len(fits)}
