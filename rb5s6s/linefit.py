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
  * the TOTAL Voigt width (their combination) is robust and the individual
    split is not, so never quote a single-condition sigma_laser or gamma_coll
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

from typing import Callable, Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import fftconvolve

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


def _shared_profile_grid(gamma_coll, sigma_laser, transit_fwhm, s0, laser_kind,
                         dnu_floor: float = 1e-3,
                         profile: Callable[[np.ndarray, float], np.ndarray] = stark_ramp):
    """Build the area-normalized shared line shape ONCE on a fine grid; the
    per-trace fit interpolates it at (nu - center). Returns (grid, profile).

    dnu_floor is the coarsest the internal grid step may get when a width
    parameter collapses. The 1e-3 MHz default reproduces every committed
    result bit-for-bit. M23's optimizer probes near-zero sigma_laser, where
    a 1e-3 step means ~1e5-point grids and the direct convolutions here go
    quadratic (minutes per profile); it passes 2e-2, which changes the
    profile by < 3e-6 of peak against lines that are never narrower than
    4 MHz (test_stark_joint has the equivalence test). The convolutions are
    FFT-based since 2026-08-01 -- identical to within float noise at any
    floor, and what makes the M23 corner cheap.
    """
    homog = GNAT_MHZ + max(gamma_coll, 0.0)
    widths = [homog, max(sigma_laser, 1e-6), max(transit_fwhm, 1e-6)] + ([s0] if s0 > 0 else [])
    span = 6.0 * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / 12.0, dnu_floor)
    n = int(np.ceil(span / dnu))
    g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    lk = gaussian(g, sigma_laser) if laser_kind == "gaussian" else lorentzian(g, sigma_laser)
    prof = fftconvolve(prof, lk, "same") * dnu
    prof = fftconvolve(prof, two_sided_exponential(g, transit_fwhm), "same") * dnu
    if s0 > 0:
        prof = fftconvolve(prof, profile(g, s0), "same") * dnu
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


def transit_fwhm_at_T(T_C: float, transit_ref_mhz: float, T_ref_C: float = 110.0,
                      isotope: int | None = None) -> float:
    """Transit FWHM at temperature T from a reference value, enforcing the
    sqrt(T) thermal scaling (T in kelvin).

    ISOTOPE (added 2026-08-10, owner instruction, OPT-IN). The transit width
    goes as the thermal speed, which goes as 1/sqrt(mass), so the two isotopes
    do not share it: 85Rb is 1.169 per cent faster than 87Rb at the same
    temperature and its transit kernel is wider by the same fraction, 11 kHz at
    130 C. Passing isotope=85 or 87 applies that, referenced to the
    abundance-weighted mean so a shared reference value keeps its meaning.

    THE DEFAULT IS None, WHICH REPRODUCES THE SHARED BEHAVIOUR BYTE FOR BYTE,
    and that is deliberate. Every committed fit shares one transit width across
    both isotopes, and the misassignment that causes is almost entirely a
    constant OFFSET rather than a density slope: the gap runs 10.53 to
    11.42 kHz across the 52-fold density lever, so a straight line through it
    has a slope of 0.000026 MHz per 1e12 cm^-3, which is 0.4 per cent of one
    sigma on the measured beta85 minus beta87. The offset is absorbed by the
    per-peak core width, which is free in every construction here. So the
    isotope split does NOT move the collisional coefficients and switching it
    on silently would produce a diff with no physics in it.

    Where it does matter, and why the argument exists: the quoted transit width
    itself, which is stated to 0.01 MHz; the transit TIME, 1.17 per cent
    shorter for 85Rb, which sets the hyperfine-pumping depletion of
    scripts/run_zeeman_depletion.py; and the Doppler pedestal a wide scan would
    measure, where 1.17 per cent of 942 MHz is 11 MHz and is resolvable, which
    makes the mass difference a handle rather than a nuisance.
    """
    # transit_ref_mhz is a WIDTH IN MHZ, not a waist. The distinction needs
    # a guard because the wrong call is the natural one and it did not raise:
    # `transit_fwhm_at_T(130.0, W0_MEASURED_M)` accepted a waist of 6.4e-5 m
    # and returned 0.0001 MHz, four orders of magnitude low, silently. Found
    # by the clean-install-from-GitHub gate on 2026-08-13, where it was the
    # first thing a reader of the public surface tried.
    #
    # The band separates the two quantities rather than pinning the physics:
    # every transit width in the committed record lies between 0.0026 and
    # 5.65 MHz, while a waist in metres is of order 1e-5. Anything outside
    # [1e-3, 1e3) MHz is a unit error, not an unusual apparatus.
    if not (1e-3 <= float(transit_ref_mhz) < 1e3):
        raise ValueError(
            f"transit_ref_mhz={transit_ref_mhz!r} is not a transit width in "
            f"MHz. Values of order 1e-5 are a beam waist in metres passed "
            f"where a width was wanted: use transit_fwhm_from_w0(w0, T_C) "
            f"for that. The committed record spans 0.0026 to 5.65 MHz.")
    scaled = transit_ref_mhz * np.sqrt((T_C + 273.15) / (T_ref_C + 273.15))
    if isotope is None:
        return scaled
    from .constants import (ABUNDANCE_RB85, ABUNDANCE_RB87, M_RB85_KG,
                            M_RB87_KG)
    ratio = np.sqrt(M_RB87_KG / M_RB85_KG)          # v(85) / v(87)
    mean = ABUNDANCE_RB85 * ratio + ABUNDANCE_RB87  # keeps the shared value's meaning
    return scaled * (ratio if int(isotope) == 85 else 1.0) / mean


def _profile_fwhm(g: np.ndarray, prof: np.ndarray) -> float:
    """Full width at half maximum of a profile sampled on a grid."""
    above = np.flatnonzero(prof >= 0.5 * prof.max())
    return float(g[above[-1]] - g[above[0]]) if above.size else 0.0


def fit_condition(freqs: List[np.ndarray], volts: List[np.ndarray], *,
                  T_C: float, law: Optional[Dict] = None, s0: float = 0.0,
                  transit_fwhm: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ, fit_transit: bool = False,
                  laser_kind: str = "gaussian", trim_tails: bool = False,
                  profile: Callable[[np.ndarray, float], np.ndarray] = stark_ramp) -> Dict:
    """Joint fit of one condition's repeats. `freqs` already in transition MHz.

    Shared free params: gamma_coll, sigma_laser (+ transit_fwhm if fit_transit).
    Per-trace free params: A_i, center_i, b0_i, b1_i.
    Returns dict with shared values+errors, per-trace params, chi2_red, cov of
    the shared block, and the sigma_laser<->gamma_coll correlation.

    `profile` is the light-geometry seam, with the same contract as
    lineshape.model_profile's: profile(grid, s0) -> the area-normalized shift
    density convolved in when s0 > 0. The stark_ramp default is the
    focused-beam triangle every committed fit used; an adapted geometry
    passes a closure over lineshape.stark_from_intensity_profile.

    `trim_tails` runs the residual-tail trimmer (rb5s6s.trim) as a SINGLE
    second pass: fit once, cut any sustained positive residual tail outside a
    core of one fitted full width either side of each fitted centre, refit
    once, stop. It does not touch the adaptive fit window, which is a separate
    and earlier decision, and it cannot reach the line because of the core
    guard. The per-trace record comes back as `trim_records`. Default off, so a
    plain call reproduces the fit as it stood before the trimmer existed.
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

    # Window each trace about its seed center, EXCLUDING any off-center-sweep
    # mirror crossing (~40 MHz away) that the full-window single-line fit would
    # otherwise treat as unmodelled signal and let bias the baseline/width.
    # (flagged 2026-07-11.) The half-width is ADAPTIVE -- a multiple of the
    # trace's own measured FWHM, clipped to [MIN, MAX] -- not the fixed
    # FIT_HALFWIDTH_MHZ this comment used to name, which no longer exists:
    # see adaptive_halfwidth() and config.FIT_HALFWIDTH_FWHM_MULT.
    wf, wv, ws = [], [], []
    for i in range(ntr):
        hw = adaptive_halfwidth(freqs[i], volts[i])
        m = np.abs(freqs[i] - centers0[i]) <= hw
        wf.append(freqs[i][m]); wv.append(volts[i][m]); ws.append(sigmas[i][m])
    freqs, volts, sigmas = wf, wv, ws

    # CORRELATED-NOISE WEIGHTING: each sample's sigma
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
                                       s0, laser_kind, profile=profile)
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            out.append((volts[i] - model) / sigmas[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=40000)
    if not sol.success:
        raise RuntimeError(f"condition fit failed: {sol.message}")

    # --- second pass: cut sustained residual tails, once ---
    trim_records = [{"trimmed": False, "trim_start_ms": float("nan"),
                     "trim_end_ms": float("nan"), "trim_reason": "",
                     "n_trimmed": 0} for _ in range(ntr)]
    if trim_tails:
        from .trim import tail_trim
        gc0, sl0, tr0 = unpack(sol.x)
        g, prof = _shared_profile_grid(
            gc0, sl0, transit_fwhm_at_T(T_C, tr0) if fit_transit else tr0,
            s0, laser_kind, profile=profile)
        guard = C.TRIM_CORE_GUARD_FWHM_MULT * _profile_fwhm(g, prof)
        any_trim = False
        for i in range(ntr):
            A, c, b0, b1 = sol.x[nshared + 4 * i: nshared + 4 * i + 4]
            model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            inside = np.flatnonzero(np.abs(freqs[i] - c) <= guard)
            if inside.size == 0:
                continue
            rec = tail_trim(freqs[i], volts[i] - model,
                            int(inside[0]), int(inside[-1]))
            trim_records[i] = {k: rec[k] for k in
                               ("trimmed", "trim_start_ms", "trim_end_ms",
                                "trim_reason", "n_trimmed")}
            if rec["trimmed"]:
                any_trim = True
                keep = rec["mask"]
                freqs[i], volts[i] = freqs[i][keep], volts[i][keep]
                sigmas[i], sigmas_raw[i] = sigmas[i][keep], sigmas_raw[i][keep]
        if any_trim:
            # Seeded from the ORIGINAL start, not from the contaminated
            # optimum. The trim changed the data, so the refit is a fresh
            # answer to a different question, and seeding it at a parameter
            # sitting on its own bound is how a fit that railed on the
            # contamination stays railed after the contamination is gone.
            sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=40000)
            if not sol.success:
                raise RuntimeError(f"condition refit after trim failed: {sol.message}")

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
                                       s0, laser_kind, profile=profile)
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
        # bound_active flags (2026-07-16): scipy's covariance ignores active
        # bounds, so a parameter pinned at its 0 rail wears a symmetric
        # Gaussian error where the true interval is one-sided. The flag
        # travels with the number so a reader can see which errors carry
        # that caveat.
        "gamma_coll_at_bound": bool(gc <= 1e-9),
        "sigma_laser_at_bound": bool(sl <= 1e-9),
        "corr_laser_coll": corr_gs,
        "centers": [float(sol.x[nshared + 4 * i + 1]) for i in range(ntr)],
        "amps": [float(sol.x[nshared + 4 * i]) for i in range(ntr)],
        "per_trace_diag": diag,
        # one record per input trace, in input order, whether or not trimming
        # ran: the caller writes these into results/trim_report.csv
        "trim_records": trim_records,
    }
