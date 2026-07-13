"""
Noise model (module M1)
=======================

Empirical, physics-blind noise law sigma(V) per condition, plus residual
correlation — the weights and error-inflation factors used by every later
fit (M2 ruler fits, M3 lineshape fits). Runs BEFORE those modules by design
(plan §3): the weights must exist before the fitting starts.

METHOD
------
1. Local noise samples from SECOND differences,
       e_i = (v_{i+1} - 2 v_i + v_{i-1}) / sqrt(6).
   For white noise of sd sigma, e_i has sd sigma. Linear signal trends
   cancel EXACTLY (first differences do not: a bright line's flank slope
   ~16 mV/sample rivals the peak noise). Residual line curvature
   contributes h * d2L/dt2 * dt^2 / sqrt(6) < ~1 mV even for 4 V lines —
   verified in the closure tests.
2. Bin e by the local smoothed signal level above baseline; robust sigma
   per bin (MAD).
3. Fit the VARIANCE law   sigma^2(V) = a^2 + b V (+ c V^2 if BIC insists):
       a — electronics/dark floor,
       b — shot-noise-like (Fano) term; its growth with TEMPERATURE is the
           radiation-trapping proxy the plan tracks (feeds M7),
       c — multiplicative (gain / intensity-noise) term.
4. Residual correlation from strictly signal-free wings (linear detrend,
   ACF, truncated integrated correlation time tau_int). Fits inflate
   parameter errors by sqrt(tau_int).

HONESTY CAVEAT (documented, tested): second differences HIGH-PASS the
noise, so correlated noise is underestimated by them. We therefore also
measure the wing "whiteness ratio" sigma_2nddiff / sigma_direct (=1 for
white); the sigma(V) law is rescaled by the measured wing ratio so that
its floor matches the DIRECT wing sigma. This assumes the correlation
structure is signal-independent — an assumption M3's fit residuals can
check after the fact.

INDEPENDENT VERIFICATION RECORD (2026-07-11, three independent estimators;
full evidence in the session workflow journal):
* V1 (sibling-pair differencing — the signal cancels exactly): the LINEAR
  variance law is confirmed decisively (beats quadratic by 12-66x in
  weighted SSE in every condition tested). Absolute (a, b) values carry
  ~x1.5-2 method-level systematics between estimators — ADEQUATE FOR FIT
  WEIGHTS, never to be quoted as physics. Both a and b are
  condition-dependent (this module already fits per condition); typical
  sigma at a 1 V peak is ~25 mV (~35 mV only at the brightest condition).
* V2 (median-filter residuals): the temperature-flatness of the LINEAR
  coefficient is confirmed (flat within ~+-12%, 70-130 C, both peaks
  tested) — the no-trapping-Fano-growth null stands. Parameterization
  trap on record: fitting a PROPORTIONAL (b*s)^2 model to shot-like data
  fakes a ~10x falling "b(T)".
* V3 (blocking method): wing noise is essentially WHITE at sample scale
  (rho1 ~ +0.05) on top of smooth slow baseline wander at >=100 ms scales
  (blocking statistic still rising at L=64). tau_int from the truncated
  ACF partly sums that slow wander, so the sqrt(tau_int) inflation is a
  CONSERVATIVE bound; per-trace fitted background terms absorb most of
  the slow component. M3's closure tests (synthetics with injected slow
  wander) will calibrate actual coverage.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from . import config as C
from .qc import boxcar, robust_sigma_from_diff


# ---------------------------------------------------------------------------
# building blocks
# ---------------------------------------------------------------------------

def second_diff(v: np.ndarray) -> np.ndarray:
    """Second-difference noise samples, unit-variance-normalized for white
    noise. Length n-2, aligned with v[1:-1]."""
    return (v[2:] - 2.0 * v[1:-1] + v[:-2]) / np.sqrt(6.0)


def robust_sigma(x: np.ndarray) -> float:
    """MAD-based sd estimate (outlier-immune)."""
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def signal_level(v: np.ndarray) -> Tuple[np.ndarray, float]:
    """Smoothed signal above robust baseline, aligned with v (same length)."""
    sm = boxcar(v, C.QC_SMOOTH_W)
    base = np.median(np.sort(sm)[: max(1, int(C.QC_BASELINE_LOW_FRACTION * len(sm)))])
    return sm - base, float(base)


def noise_vs_level(v: np.ndarray, nbins: int = None):
    """(levels, sigmas, counts) of second-diff noise binned by signal level.

    Bins are level-quantiles, so the wing-dominated low bins are huge and the
    few peak-region bins are small — the law fit weights accordingly.
    """
    nbins = nbins or C.NOISE_NBINS
    lev_full, _ = signal_level(v)
    lev = lev_full[1:-1]
    e = second_diff(v)
    edges = np.quantile(lev, np.linspace(0.0, 1.0, nbins + 1))
    edges[-1] += 1e-12
    out = []
    for i in range(nbins):
        m = (lev >= edges[i]) & (lev < edges[i + 1])
        if m.sum() >= C.NOISE_MIN_BIN_SAMPLES:
            out.append((float(np.median(lev[m])), robust_sigma(e[m]), int(m.sum())))
    arr = np.array(out)
    return arr[:, 0], arr[:, 1], arr[:, 2].astype(int)


def fit_variance_law(levels: np.ndarray, sigmas: np.ndarray, counts: np.ndarray) -> Dict:
    """Weighted LS fit of sigma^2 = a^2 + b*V (+ c*V^2 if BIC prefers).

    Weights: var(sigma_bin^2) ~ 2 sigma^4 / n  =>  w = n / sigma^4.
    Returns dict with a [V], b [V], c [1] (0 if 2-param wins), chi2_red, used_c.
    """
    y = sigmas ** 2
    w = counts / np.maximum(sigmas, 1e-12) ** 4

    def wls(X):
        Aw = X * w[:, None]
        beta, *_ = np.linalg.lstsq(Aw.T @ X, Aw.T @ y, rcond=None)
        resid = y - X @ beta
        chi2 = float(np.sum(w * resid ** 2) * (2.0 / 1.0))  # ~2 sigma^4/n var
        return beta, chi2

    X2 = np.column_stack([np.ones_like(levels), levels])
    X3 = np.column_stack([np.ones_like(levels), levels, levels ** 2])
    b2, chi2_2 = wls(X2)
    b3, chi2_3 = wls(X3)
    n = len(levels)
    bic2 = n * np.log(max(chi2_2, 1e-30) / n) + 2 * np.log(n)
    bic3 = n * np.log(max(chi2_3, 1e-30) / n) + 3 * np.log(n)
    if bic3 + C.NOISE_BIC_MARGIN < bic2:
        beta, chi2, used_c = b3, chi2_3, True
    else:
        beta, chi2, used_c = np.append(b2, 0.0), chi2_2, False
    a2 = max(float(beta[0]), 0.0)
    dof = max(n - (3 if used_c else 2), 1)
    return {"a": float(np.sqrt(a2)), "b": float(beta[1]), "c": float(beta[2]),
            "chi2_red": chi2 / dof, "used_c": used_c}


def wing_correlation(v: np.ndarray) -> Dict:
    """Correlation diagnostics on the longest strictly signal-free wing
    segment: rho1, truncated integrated correlation time tau_int, and the
    whiteness ratio sigma_2nddiff/sigma_direct (1 for white noise)."""
    lev, _ = signal_level(v)
    sigma_w = robust_sigma_from_diff(v[lev < 0.1 * lev.max()]) if (lev < 0.1 * lev.max()).sum() > 50 \
        else robust_sigma_from_diff(v)
    strict = lev < C.QC_STEP_WING_NSIGMA * sigma_w
    idx = np.where(strict)[0]
    if len(idx) == 0:
        return {"rho1": np.nan, "tau_int": np.nan, "white_ratio": np.nan, "n_wing": 0}
    breaks = np.where(np.diff(idx) > 5)[0]
    seg = max(np.split(idx, breaks + 1), key=len)
    if len(seg) < 100:
        return {"rho1": np.nan, "tau_int": np.nan, "white_ratio": np.nan, "n_wing": int(len(seg))}
    r = v[seg].astype(float)
    r = r - np.polyval(np.polyfit(np.arange(len(r)), r, 1), np.arange(len(r)))
    r = r - r.mean()
    denom = float(np.dot(r, r))
    tau, rho1 = 1.0, np.nan
    for k in range(1, min(C.NOISE_MAX_LAG, len(r) // 4)):
        rho = float(np.dot(r[:-k], r[k:]) / denom)
        if k == 1:
            rho1 = rho
        if rho < C.NOISE_ACF_TRUNC:
            break
        tau += 2.0 * rho
    white_ratio = robust_sigma(second_diff(r)) / max(np.std(r), 1e-12)
    return {"rho1": rho1, "tau_int": float(tau), "white_ratio": float(white_ratio),
            "n_wing": int(len(seg))}


# ---------------------------------------------------------------------------
# condition-level model (the M1 deliverable)
# ---------------------------------------------------------------------------

def condition_noise_model(traces: List[np.ndarray]) -> Dict:
    """Pooled noise model for one condition (its 4-5 back-to-back repeats).

    Pools (level, e) samples across traces (per-trace baselines), fits the
    variance law, rescales it so the floor matches the DIRECT wing sigma
    (whiteness correction, see module docstring), and averages the
    correlation diagnostics.
    """
    levs, es, sig_direct = [], [], []
    cors = []
    for v in traces:
        lev, _ = signal_level(v)
        levs.append(lev[1:-1])
        es.append(second_diff(v))
        wing = lev < 0.1 * lev.max()
        if wing.sum() > 50:
            sig_direct.append(robust_sigma_from_diff(v[wing]))
        cors.append(wing_correlation(v))
    lev = np.concatenate(levs)
    e = np.concatenate(es)

    nb = C.NOISE_NBINS
    edges = np.quantile(lev, np.linspace(0, 1, nb + 1)); edges[-1] += 1e-12
    L, S, N = [], [], []
    for i in range(nb):
        m = (lev >= edges[i]) & (lev < edges[i + 1])
        if m.sum() >= C.NOISE_MIN_BIN_SAMPLES:
            L.append(float(np.median(lev[m]))); S.append(robust_sigma(e[m])); N.append(int(m.sum()))
    law = fit_variance_law(np.array(L), np.array(S), np.array(N))

    # whiteness rescale: second-diff floor -> direct wing sigma
    ratio = np.nanmean([c["white_ratio"] for c in cors])
    scale = 1.0 / ratio if np.isfinite(ratio) and ratio > 0.2 else 1.0
    law["a"] *= scale
    law["b"] *= scale ** 2
    law["c"] *= scale ** 2
    law["white_ratio"] = float(ratio)
    law["tau_int"] = float(np.nanmean([c["tau_int"] for c in cors]))
    law["rho1"] = float(np.nanmean([c["rho1"] for c in cors]))
    law["sigma_wing_direct"] = float(np.mean(sig_direct)) if sig_direct else np.nan
    law["n_traces"] = len(traces)
    law["lev_max"] = float(np.quantile(lev, 0.999))
    return law


def sigma_of_v(level: np.ndarray, law: Dict) -> np.ndarray:
    """Evaluate the noise law: per-sample sigma at signal level `level`
    (volts above baseline). Floor at 20% of `a` guards degenerate weights.

    DOMAIN: the law is empirical and valid only within the level range it
    was fit on (law['lev_max']); in normal use this is automatic because
    weights are evaluated on the very traces the law came from. Do not
    extrapolate a dim condition's law to bright levels."""
    var = law["a"] ** 2 + law["b"] * np.maximum(level, 0.0) + law["c"] * np.maximum(level, 0.0) ** 2
    return np.sqrt(np.maximum(var, (0.2 * law["a"]) ** 2))
