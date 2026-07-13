"""
Joint lineshape fit per condition (module M3, fit layer)
========================================================

Takes a condition's back-to-back repeats (already loaded as time/volt), maps
time -> transition frequency with that block's M2 rate, and jointly fits the
composite model of rb5s6s.lineshape:

  SHARED across the repeats (the physics of the condition):
    gamma_coll       collisional Lorentzian FWHM  (the beta_self target)
    sigma_laser      laser-kernel FWHM (already x2 for two photons)
    [transit_fwhm]   optional; usually FIXED per T by sqrt(T) scaling
  PER TRACE (nuisance):
    A_i              amplitude
    center_i         line center (floats freely — 2025 drift lives here)
    b0_i, b1_i       linear background

Weights come from the M1 noise law (sigma(V)); reported parameter errors are
inflated by sqrt(tau_int) for wing-noise correlation and sqrt(chi2_red) when
the fit is imperfect (conservative, matching M2).

WHY joint-with-shared-shape: the 5 repeats see the SAME physical line at
(nearly) the same conditions; only the drift-shifted center and PMT gain
differ. Sharing the shape is what turns 5 noisy traces into one precise width
while letting each center float — the design that makes the drifted 2025 data
usable at all.

THE HARD PART (documented, closure-tested): sigma_laser (a Gaussian core) and
gamma_nat+gamma_coll (a Lorentzian) form a Voigt whose two widths are
partially degenerate — the "fit-level face of the confound". fit_condition
returns the full covariance so the sigma_laser<->gamma_coll correlation is
visible, and test_linefit quantifies the recoverable precision at campaign
SNR before any real number is trusted.

CONSEQUENCES OF THE DEGENERACY (closure-measured at SNR~130, 5 repeats):
corr(sigma_laser, gamma_coll) ~ -0.9. So:
  * the TOTAL Voigt width (their combination) is robust; the individual
    split is not — never quote a single-condition sigma_laser or gamma_coll
    as physics without its error and this correlation.
  * beta_self must ride on the gamma_coll DIFFERENCE across temperature
    (density lever arm), where the shared/systematic laser contribution
    largely cancels, NOT on absolute per-condition gamma_coll.
  * these synthetics generate AND fit with the SAME model, so they bound the
    fitter's numerics and the statistical degeneracy ONLY — not model
    mismatch (is the laser kernel really Gaussian? the transit really a
    two-sided exponential?). Model-form sensitivity is a separate study
    (laser_kind toggle + the cold-dim cusp BIC test) and its spread is a
    systematic on top of these statistical errors.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from .constants import GAMMA_NAT_HZ
from ._compat import trapezoid
from .lineshape import lorentzian, gaussian, two_sided_exponential, stark_ramp
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0

GNAT_MHZ = GAMMA_NAT_HZ / 1e6


def to_frequency(t_ms: np.ndarray, rate_transition_mhz_per_ms: float) -> np.ndarray:
    """Map the raw time axis to TRANSITION frequency (MHz). The origin is
    arbitrary (per-trace center absorbs it), so we reference to t=0."""
    return t_ms * rate_transition_mhz_per_ms


def _shared_profile_grid(gamma_coll, sigma_laser, transit_fwhm, s0, laser_kind):
    """Build the area-normalized shared line shape ONCE on a fine grid; the
    per-trace fit interpolates it at (nu - center). Returns (grid, profile)."""
    homog = GNAT_MHZ + max(gamma_coll, 0.0)
    widths = [homog, max(sigma_laser, 1e-6), max(transit_fwhm, 1e-6)] + ([s0] if s0 > 0 else [])
    span = 6.0 * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / 12.0, 1e-3)
    n = int(np.ceil(span / dnu))
    g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    lk = gaussian(g, sigma_laser) if laser_kind == "gaussian" else lorentzian(g, sigma_laser)
    prof = np.convolve(prof, lk, "same") * dnu
    prof = np.convolve(prof, two_sided_exponential(g, transit_fwhm), "same") * dnu
    if s0 > 0:
        prof = np.convolve(prof, stark_ramp(g, s0), "same") * dnu
    area = trapezoid(prof, g)
    return g, (prof / area if area > 0 else prof)


def adaptive_halfwidth(freqs: np.ndarray, volts: np.ndarray) -> float:
    """Fit half-width (MHz) for one trace: FIT_HALFWIDTH_FWHM_MULT times the
    trace's own model-independent FWHM, clipped to [MIN, MAX]. Scales with the
    line so the same fraction of Lorentzian wing is kept whether narrow or
    collisionally broadened, while the MAX cap always excludes the ~40 MHz
    off-center-sweep mirror. `freqs` is the transition-frequency axis (MHz);
    contiguous_fwhm_ms is axis-agnostic (returns the x-span in freqs' units)."""
    from .qc import contiguous_fwhm_ms
    fwhm = contiguous_fwhm_ms(freqs, volts)  # MHz here (freqs axis)
    hw = C.FIT_HALFWIDTH_FWHM_MULT * fwhm
    return float(min(max(hw, C.FIT_HALFWIDTH_MIN_MHZ), C.FIT_HALFWIDTH_MAX_MHZ))


def transit_fwhm_at_T(T_C: float, transit_ref_mhz: float, T_ref_C: float = 110.0) -> float:
    """Transit FWHM at temperature T from a reference value, enforcing the
    sqrt(T) thermal scaling (T in kelvin)."""
    return transit_ref_mhz * np.sqrt((T_C + 273.15) / (T_ref_C + 273.15))


def fit_condition(freqs: List[np.ndarray], volts: List[np.ndarray], *,
                  T_C: float, law: Optional[Dict] = None, s0: float = 0.0,
                  transit_fwhm: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ, fit_transit: bool = False,
                  laser_kind: str = "gaussian") -> Dict:
    """Joint fit of one condition's repeats. `freqs` already in transition MHz.

    Shared free params: gamma_coll, sigma_laser (+ transit_fwhm if fit_transit).
    Per-trace free params: A_i, center_i, b0_i, b1_i.
    Returns dict with shared values+errors, per-trace params, chi2_red, cov of
    the shared block, and the sigma_laser<->gamma_coll correlation.
    """
    ntr = len(freqs)
    # per-trace seeds from simple moments
    centers0, amps0, b0s = [], [], []
    sigmas = []
    for nu, v in zip(freqs, volts):
        lev, base = signal_level(v)
        ipk = int(np.argmax(lev))
        centers0.append(float(nu[ipk])); amps0.append(float(lev.max())); b0s.append(float(base))
        if law is not None:
            sigmas.append(sigma_of_v(np.maximum(lev, 0.0), law))
        else:
            sigmas.append(np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
    tau = max(law.get("tau_int", 1.0), 1.0) if law is not None else 1.0

    # Window each trace to +-FIT_HALFWIDTH_MHZ about its seed center, EXCLUDING
    # any off-center-sweep mirror crossing (~40 MHz away) that the full-window
    # single-line fit would otherwise treat as unmodelled signal and let bias
    # the baseline/width. (user-flagged 2026-07-11; see config.FIT_HALFWIDTH_MHZ)
    wf, wv, ws = [], [], []
    for i in range(ntr):
        hw = adaptive_halfwidth(freqs[i], volts[i])
        m = np.abs(freqs[i] - centers0[i]) <= hw
        wf.append(freqs[i][m]); wv.append(volts[i][m]); ws.append(sigmas[i][m])
    freqs, volts, sigmas = wf, wv, ws

    # CORRELATED-NOISE WEIGHTING (review round 3 fix): each sample's sigma
    # is inflated by sqrt(tau_int) INSIDE the fit, so the optimizer sees each
    # trace's true information content (tau correlated samples ~ one
    # independent one). Diagnostics (chi2, per-trace residuals) use the
    # UNSCALED sigma, for which E[chi2_red]=1 for a perfect model regardless
    # of correlation. Previously tau multiplied the final covariance as one
    # scalar -- wrong exposure for shared vs nuisance parameters.
    sigmas_raw = sigmas
    sigmas = [s * np.sqrt(tau) for s in sigmas_raw]

    # parameter vector: [gamma_coll, sigma_laser, (transit?)] + per-trace [A, c, b0, b1]
    nshared = 3 if fit_transit else 2
    p0 = [0.5, 1.0] + ([transit_fwhm] if fit_transit else [])
    for i in range(ntr):
        p0 += [amps0[i], centers0[i], b0s[i], 0.0]
    p0 = np.array(p0)
    lo = [0.0, 0.0] + ([0.05] if fit_transit else []) + [(-np.inf)] * (4 * ntr)
    hi = [50.0, 50.0] + ([10.0] if fit_transit else []) + [np.inf] * (4 * ntr)
    lo = np.array(lo, float); hi = np.array(hi, float)
    # keep amplitudes non-negative, widths in-range
    for i in range(ntr):
        lo[nshared + 4 * i] = 0.0  # A_i >= 0

    def unpack(p):
        gc, sl = p[0], p[1]
        tr = p[2] if fit_transit else transit_fwhm
        return gc, sl, tr

    def residuals(p):
        gc, sl, tr = unpack(p)
        g, prof = _shared_profile_grid(gc, sl, transit_fwhm_at_T(T_C, tr) if fit_transit else tr,
                                       s0, laser_kind)
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            out.append((volts[i] - model) / sigmas[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds (round-5 fix)
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=40000)
    if not sol.success:
        raise RuntimeError(f"condition fit failed: {sol.message}")
    ndata = sum(len(v) for v in volts)
    dof = max(ndata - len(p0), 1)
    # raw chi2 (unscaled sigma) is the goodness-of-fit diagnostic; with the
    # uniform per-condition tau it is exactly tau x the fitted chi2.
    chi2_red = float(2.0 * sol.cost / dof) * tau
    # Covariance: the tau weighting already lives in the whitened Jacobian.
    # The max(chi2_red, 1) rescale is a DOCUMENTED ONE-SIDED (conservative)
    # choice: model imperfection inflates errors, but chi2_red < 1 (noise
    # model overestimates sigma, or overfitting) does NOT shrink them -- the
    # noise model then sets the error floor. That state is flagged below.
    cov = cov_from_jac(sol.jac) * max(chi2_red, 1.0)

    # Per-trace residual diagnostics (audit request, 2026-07-11): a good
    # joint fit must be good for EVERY trace, not on average. For each trace
    # we report its own chi2_red, the lag-1 autocorrelation of standardized
    # residuals (structure/misfit shows as positive lag-1), and their skew
    # (asymmetric misfit, e.g. an unmodelled shoulder).
    diag = []
    for i in range(ntr):
        gc0, sl0, tr0 = unpack(sol.x)
        g, prof = _shared_profile_grid(gc0, sl0,
                                       transit_fwhm_at_T(T_C, tr0) if fit_transit else tr0,
                                       s0, laser_kind)
        A, c, b0, b1 = sol.x[nshared + 4 * i: nshared + 4 * i + 4]
        model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
        r = (volts[i] - model) / sigmas_raw[i]   # diagnostics on UNSCALED sigma
        r0 = r - r.mean()
        lag1 = float(np.dot(r0[:-1], r0[1:]) / max(np.dot(r0, r0), 1e-12))
        diag.append({"chi2_red": float(np.mean(r ** 2)),
                     "lag1": lag1,
                     "skew": float(np.mean(r0 ** 3) / max(np.std(r0) ** 3, 1e-12))})

    gc, sl, tr = unpack(sol.x)
    err = np.sqrt(np.clip(np.diag(cov), 0, None))
    corr_gs = float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])) if cov[0, 0] > 0 and cov[1, 1] > 0 else np.nan
    return {
        "gamma_coll": float(gc), "gamma_coll_err": float(err[0]),
        "sigma_laser": float(sl), "sigma_laser_err": float(err[1]),
        "transit_fwhm": float(transit_fwhm_at_T(T_C, tr) if fit_transit else tr),
        "transit_fitted": bool(fit_transit),
        "chi2_red": chi2_red, "n_traces": ntr,
        "noise_floor_limited": bool(chi2_red < 0.8),  # errors set by the noise model, not the fit
        "corr_laser_coll": corr_gs,
        "centers": [float(sol.x[nshared + 4 * i + 1]) for i in range(ntr)],
        "amps": [float(sol.x[nshared + 4 * i]) for i in range(ntr)],
        "per_trace_diag": diag,
    }
