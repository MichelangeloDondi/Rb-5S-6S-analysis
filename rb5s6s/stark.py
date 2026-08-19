"""
AC-Stark power-sweep analysis (module M4e -- the power-lever twin of beta.py)
============================================================================

beta.py bounds the collisional coefficient from width-vs-DENSITY; this bounds
the AC-Stark coefficient kappa (S0 = kappa * P) from width-vs-POWER at fixed T.

The physics that makes this only a BOUND in the 2025 archive: the drifted lock
destroyed the line CENTRES, so the AC-Stark *shift* (the pull, ~S0, the sensitive
handle) is absorbed by each trace's free centre and unusable. What survives is
the ramp's contribution to the line WIDTH -- the intensity-averaged triangular
ramp of on-axis shift S0 adds an excess variance ~S0^2/18, i.e. it BROADENS the
line as P^2. That is a weak handle (a ~0.6 MHz S0 inflates a ~5 MHz line by
<~0.1 MHz), so we get a one-sided UPPER BOUND on kappa, not a measurement. The
skew handle (~S0^3) is weaker still and shot-noise-dominated (M6 C3c). A fixed
lock would measure the pull ~S0 directly, and at a smaller waist (S0 several-fold
larger) -- that is the actual measurement; this archival bound brackets it.

AND THE P^2 BROADENING THIS FITS IS NOT ONLY THE RAMP (2026-08-10). Two other
effects broaden the line with the identical P^2 signature and are absent from
the forward model here, so whatever P^2 growth the fit sees, it attributes all
of it to kappa and the bound comes out LOOSE. They are atomic saturation, the
larger at about 3.7 times the ramp at the predicted S0, and hyperfine pumping
through the real 5P cascade, whose decay does not preserve F. Injecting the
saturation term and re-profiling moves this width-only bound from 0.6325 to
about 0.23 MHz (factor 2.8) and the joint C3f bound by 2.21. NEITHER COMMITTED
BOUND MOVES, because the injected law is the two-level homogeneous form used
with a two-photon Rabi frequency, standard practice rather than a derivation
for this level structure, so the looseness is carried with its size stated.

The degeneracy is complete in both CONTINUOUS knobs this module has. All three
terms go as P^2, and all three go as the inverse fourth power of the waist (the
ramp because its increment goes as S0^2 and S0 goes as w0^-2, the companions
because the saturation parameter carries Omega^2 and Omega is two-photon). So
neither a power sweep nor a change of focus separates them.

TWO THINGS DO. The centroid pull, because the companions broaden the line
without moving it. And the LINE INDEX (2026-08-10): this module fits ONE shared
kappa across the four peaks, which is right for the ramp and for the saturation
since both are F-independent, and wrong for the pumping, whose branching runs
0.223, 0.248, 0.348, 0.372 across 4207, 4192, 4154 and 4121. Those come from
the two-step cascade with 6j symbols, not from a degeneracy weight, because the
scalar two-photon operator leaves 6S in a single hyperfine level. A per-line
pumping term with those FIXED coefficients and one free scale would be
separable from the shared kappa in principle. In practice the spread is 4 kHz
against an 88 kHz single-block width scatter, so this archive cannot resolve
it, and the sharing stays. Reproduce with scripts/run_saturation_probe.py; write-up in
docs/notes/two_photon_saturation_companion.md, drawn in
figures/fig23_hyperfine_pumping.png.

One kappa is SHARED across the four peaks (the Stark coefficient is an
atomic+beam property, ~common to the hyperfine components), while each peak
floats its own power-INDEPENDENT core width -- so kappa is constrained purely by
the common power-DEPENDENT growth, separable from the per-peak baseline. We fit
the committed per-power FWHMs (results/power_sweep.csv, M6) rather than re-
fitting every trace: the width is the entire S0 handle here and M6 already
measured it per power with proper errors, so the width-vs-power curve carries
all the kappa information without a redundant trace-level joint fit.
"""

from __future__ import annotations

from typing import Dict, Tuple

import math

import numpy as np
from scipy.optimize import least_squares

from .lineshape import model_profile, stark_shift_S0_mhz
from .linefit import transit_fwhm_at_T
from .constants import (GAMMA_NAT_HZ, RHO_RETRO, RHO_RETRO_ERR, W0_BAND_M,
                        W0_MEASURED_M)
from .cascade import BRANCHING_F as F_PER_LINE
from .config import TRANSIT_FWHM_PLACEHOLDER_MHZ


# --- the two width companions, OFF unless a caller turns them on -----------
#
# Preregistered at docs/notes/companion_inclusive_refit_prereg.md. Three effects
# broaden the Doppler-free core with the same P^2 signature as the AC-Stark
# ramp, and only the ramp is in the fitted model. This is the committed,
# opt-in form of the wrappers scripts/run_saturation_probe.py used as
# monkeypatches, promoted so the refit is reproducible.
#
# DEFAULT IS None AND THAT IS LOAD-BEARING: every committed bound was produced
# without these terms and is quoted with its looseness stated. Turning them on
# retires that framing, which is an owner decision and not a code path.
#
# The saturation term is line-independent and the pumping term is not, so the
# per-line factor is applied where the peak is known, at the two call sites
# below, rather than threaded through _fwhm_of, whose signature three scripts
# import and one of them replaces.
COMPANIONS: dict | None = None

# from run_zeeman_depletion checks 3 and 7, verified two independent ways
# The cascade branching per line, imported at the top of this file. These four
# numbers were duplicated here as literals until 2026-08-19, while their source
# of truth is the manifold computation whose committed output rb5s6s.cascade
# carries.

# The natural width on the transition axis. Was a private literal carrying no
# uncertainty while the record quotes 3.493 +/- 0.013 MHz from a cited
# lifetime; taken from the constant so the two cannot diverge again.
_GAMMA_MHZ = GAMMA_NAT_HZ / 1e6


def companion_gamma_mhz(s0: float, peak: str) -> float:
    """Extra HOMOGENEOUS width from saturation and hyperfine pumping, in MHz.

    Added to gamma_coll, which is where the probe put it and where it belongs:
    both broaden the homogeneous core rather than the whole profile. Returns
    zero when COMPANIONS is None, and zero at s0 = 0 whatever it is, which is
    why the two models agree exactly where the production fit rails.
    """
    if COMPANIONS is None:
        return 0.0
    om = COMPANIONS.get("ratio", 1.2367) * max(s0, 0.0)
    sat = _GAMMA_MHZ * (math.sqrt(1.0 + 2.0 * (om / _GAMMA_MHZ) ** 2) - 1.0)
    return sat * (1.0 + COMPANIONS.get("scale", 1.0) * F_PER_LINE[peak])


def companion_transit_mhz(transit: float, s0: float, peak: str) -> float:
    """Transit width after depletion, in MHz.

    Pumping shortens the interaction time, and a shorter time is a wider
    transit kernel, so this DIVIDES rather than adding a Lorentzian. Off with
    COMPANIONS, and off unless COMPANIONS asks for it, because the depletion
    rests on a cascade rate this record carries as an envelope.
    """
    if COMPANIONS is None or not COMPANIONS.get("deplete"):
        return transit
    om = COMPANIONS.get("ratio", 1.2367) * max(s0, 0.0)
    s = 2.0 * (om / _GAMMA_MHZ) ** 2
    lost = F_PER_LINE[peak] * (s / 2.0) / (1.0 + s) * COMPANIONS.get("cycles", 1.0)
    return transit / max(1.0 - lost, 0.05)


def _fwhm_of(gamma_coll: float, sigma_laser: float, transit: float, s0: float,
             nu: np.ndarray) -> float:
    y = model_profile(nu, gamma_coll=max(gamma_coll, 0.0), sigma_laser_fwhm=sigma_laser,
                      transit_fwhm=transit, s0=max(s0, 0.0))
    ypk = y.max()
    above = np.where(y >= 0.5 * ypk)[0]
    lo, hi = above[0], above[-1]
    # sub-grid linear interpolation of the two half-max crossings
    def cross(i, j):
        y1, y2 = y[i], y[j]
        return nu[i] + (0.5 * ypk - y1) * (nu[j] - nu[i]) / (y2 - y1) if y2 != y1 else nu[i]
    left = cross(lo - 1, lo) if lo > 0 else nu[lo]
    right = cross(hi, hi + 1) if hi + 1 < len(nu) else nu[hi]
    return right - left


def fit_stark_sweep(grid: Dict[Tuple[str, float], Tuple[float, float]], *,
                    T_C: float = 130.0,
                    transit_ref_mhz: float = TRANSIT_FWHM_PLACEHOLDER_MHZ,
                    gamma_coll: float = 0.6, w0_um: float = W0_MEASURED_M * 1e6,
                    rho: float = RHO_RETRO, profile: bool = True,
                    nu_step: float = 0.01) -> Dict:
    """Bound the AC-Stark coefficient kappa from FWHM-vs-power at fixed T.

    grid: {(peak, P_watts): (fwhm_mhz, fwhm_err_mhz)} on the transition axis.
    Shared parameter: kappa (MHz per W, S0 = kappa*P). Per-peak nuisance: the
    core sigma_laser (power-independent). gamma_coll and the transit width are
    fixed at their T_C values (they only set the baseline the per-peak core
    absorbs; kappa rides on the power-DEPENDENT part).

    The QUOTED 95% bound is the over-dispersion-adjusted PROFILE-chi2 one
    (profile=True): scan
    kappa upward from the minimum, re-minimizing the per-peak nuisances at each
    point, and place the one-sided 95% limit where the chi2 rises by
    2.706 x max(chi2_red, 1) -- the over-dispersion scaling equivalent to the
    sqrt(chi2_red) error inflation used elsewhere. This construction is needed
    because the best fit rails at kappa = 0, where the width handle (broadening
    ~ S0^2) has zero gradient: the linearized Wald bound kappa + 1.645 sigma is
    evaluated where the Jacobian column vanishes, so its "sigma" is a
    finite-difference artifact and carries no 95% coverage. The Wald numbers
    are retained in the output as diagnostics/continuity, not as the bound.

    Returns kappa, its Wald error, both Wald bounds (raw / chi2-inflated), the
    profile bound kappa_ub95_profile (and S0 at 225 mW for each), the predicted
    kappa from stark_shift_S0_mhz, and chi2_red.
    """
    peaks = sorted({p for p, _ in grid})
    items = sorted(grid.items())
    transit = transit_fwhm_at_T(T_C, transit_ref_mhz)
    nu = np.arange(-45.0, 45.0, nu_step)
    npk = len(peaks)

    # seeds: per-peak sigma_laser ~1.6, kappa ~ predicted
    kpred = stark_shift_S0_mhz(1.0, w0_um * 1e-6, rho=rho)   # MHz per W (S0 at 1 W)
    p0 = np.array([1.6] * npk + [kpred], float)
    # S0 prediction BAND over the measured w0 band AND the rho uncertainty. S0 ~
    # (1+rho)/w0^2, so the widest credible interval pairs the tight-waist edge
    # with the high rho and the wide-waist edge with the low rho. Both bands
    # come from constants (W0_BAND_M, RHO_RETRO +/- RHO_RETRO_ERR) so no edge
    # is ever hand-typed here.
    _w0_lo_m, _w0_hi_m = W0_BAND_M
    s0_225_pred_hi = stark_shift_S0_mhz(0.225, _w0_lo_m, rho=rho + RHO_RETRO_ERR)
    s0_225_pred_lo = stark_shift_S0_mhz(0.225, _w0_hi_m, rho=rho - RHO_RETRO_ERR)
    lo = np.array([0.0] * npk + [0.0], float)
    hi = np.array([np.inf] * (npk + 1), float)

    def resid(p):
        sl = p[:npk]; kappa = p[npk]
        out = []
        for (peak, P), (f, ferr) in items:
            si = peaks.index(peak)
            fm = _fwhm_of(gamma_coll + companion_gamma_mhz(kappa * P, peak),
                          sl[si],
                          companion_transit_mhz(transit, kappa * P, peak),
                          kappa * P, nu)
            out.append((fm - f) / ferr)
        return np.array(out)

    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=4000)
    ndata = len(items)
    dof = max(ndata - len(p0), 1)
    chi2_red = float(np.sum(sol.fun ** 2) / dof)
    # covariance from the Jacobian. The fit is over-dispersed (chi2_red > 1,
    # block-to-block width scatter), so we CONSERVATIVELY inflate the parameter
    # error by sqrt(chi2_red) -- the standard over-dispersion rescale. This is
    # load-bearing: the inflated bound BRACKETS the predicted 0.35 MHz at the
    # adopted w0 = 64 um (constants.W0_MEASURED_M). It was quoted here against
    # ~0.6 MHz while the central waist was 50 um, and 1.43 at the older 32 um
    # nominal; both are retired. The raw (un-inflated) bound would be
    # tighter, so we surface both (kappa_err_raw, chi2_inflation) for verifiability.
    infl = float(max(chi2_red, 1.0) ** 0.5)
    J = sol.jac
    try:
        cov_raw = np.linalg.inv(J.T @ J)
        kerr_raw = float(np.sqrt(max(cov_raw[npk, npk], 0.0)))
    except np.linalg.LinAlgError:
        kerr_raw = float("inf")
    kerr = kerr_raw * infl
    kappa = float(sol.x[npk])

    # -- over-dispersion-adjusted profile-chi2 one-sided 95% bound (quoted) ---
    # chi2 profiled over the per-peak nuisances at fixed kappa; the limit sits
    # where chi2 rises by 2.706 x max(chi2_red, 1) above the minimum. Scaling
    # the threshold by chi2_red is algebraically the same over-dispersion
    # rescale as multiplying errors by sqrt(chi2_red) in the Wald path.
    kappa_ub95_prof = float("nan")
    profile_thresh = float("nan")
    if profile:
        chi2_min = float(np.sum(sol.fun ** 2))
        profile_thresh = 2.706 * max(chi2_red, 1.0)
        idx = {p: i for i, p in enumerate(peaks)}

        def chi2_at(kappa_fixed: float, sl_seed: np.ndarray):
            def r(sl):
                out = []
                for (peak, P), (f, ferr) in items:
                    fm = _fwhm_of(
                        gamma_coll + companion_gamma_mhz(kappa_fixed * P, peak),
                        sl[idx[peak]],
                        companion_transit_mhz(transit, kappa_fixed * P, peak),
                        kappa_fixed * P, nu)
                    out.append((fm - f) / ferr)
                return np.array(out)
            s = least_squares(r, sl_seed, bounds=(np.zeros(npk),
                                                  np.full(npk, np.inf)),
                              max_nfev=2000)
            return float(np.sum(s.fun ** 2)), s.x

        # bracket the crossing: expand upward from the minimum
        sl_seed = sol.x[:npk].copy()
        k_lo = kappa
        step = max(kpred, 1.0)
        k_hi = kappa + step
        c_hi, sl_seed = chi2_at(k_hi, sl_seed)
        n_exp = 0
        while c_hi - chi2_min < profile_thresh and n_exp < 40:
            k_lo = k_hi
            k_hi = kappa + (k_hi - kappa) * 2.0
            c_hi, sl_seed = chi2_at(k_hi, sl_seed)
            n_exp += 1
        # bisect to the threshold crossing
        for _ in range(60):
            if k_hi - k_lo <= 1e-3 * max(k_hi, 1.0):
                break
            k_mid = 0.5 * (k_lo + k_hi)
            c_mid, sl_seed = chi2_at(k_mid, sl_seed)
            if c_mid - chi2_min < profile_thresh:
                k_lo = k_mid
            else:
                k_hi = k_mid
        kappa_ub95_prof = 0.5 * (k_lo + k_hi)

    return {
        "peaks": peaks,
        "sigma_laser_by_peak": {p: float(sol.x[i]) for i, p in enumerate(peaks)},
        "kappa": kappa, "kappa_err": kerr, "kappa_err_raw": kerr_raw,
        "chi2_inflation": infl,
        "kappa_ub95": max(kappa + 1.645 * kerr, 0.0),
        "kappa_ub95_profile": kappa_ub95_prof,
        "profile_delta_chi2": profile_thresh,
        "S0_225_fit": kappa * 0.225, "S0_225_ub95": max(kappa + 1.645 * kerr, 0.0) * 0.225,
        "S0_225_ub95_raw": max(kappa + 1.645 * kerr_raw, 0.0) * 0.225,
        "S0_225_ub95_profile": kappa_ub95_prof * 0.225,
        "kappa_pred": float(kpred), "S0_225_pred": float(kpred) * 0.225,
        "S0_225_pred_lo": float(s0_225_pred_lo), "S0_225_pred_hi": float(s0_225_pred_hi),
        "chi2_red": chi2_red, "n": ndata,
    }
