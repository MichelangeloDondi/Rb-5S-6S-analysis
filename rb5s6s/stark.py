"""
AC-Stark power-sweep analysis (module M4e -- the power-lever twin of beta.py)
============================================================================

beta.py bounds the collisional coefficient from width-vs-DENSITY; this bounds
the AC-Stark coefficient kappa (S0 = kappa * P) from width-vs-POWER at fixed T.

The physics that makes this only a BOUND in the 2025 archive: the drifted lock
killed the line CENTRES, so the AC-Stark *shift* (the pull, ~S0, the sensitive
handle) is absorbed by each trace's free centre and unusable. What survives is
the ramp's contribution to the line WIDTH -- the intensity-averaged triangular
ramp of on-axis shift S0 adds an excess variance ~S0^2/18, i.e. it BROADENS the
line as P^2. That is a weak handle (a ~0.6 MHz S0 inflates a ~5 MHz line by
<~0.1 MHz), so we get a one-sided UPPER BOUND on kappa, not a measurement. The
skew handle (~S0^3) is weaker still and shot-noise-dominated (M6 C3c). The fixed-lock session's
a fixed lock would measure the pull ~S0 directly and at a smaller waist (S0 several-fold larger),
which is the actual measurement -- this archival bound just brackets it.

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

import numpy as np
from scipy.optimize import least_squares

from .lineshape import model_profile, stark_shift_S0_mhz
from .linefit import transit_fwhm_at_T
from .constants import GAMMA_NAT_HZ, W0_BAND_M, W0_PRIOR_M
from .config import TRANSIT_FWHM_PLACEHOLDER_MHZ


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
                    gamma_coll: float = 0.6, w0_um: float = W0_PRIOR_M * 1e6,
                    rho: float = 1.0, profile: bool = True,
                    nu_step: float = 0.01) -> Dict:
    """Bound the AC-Stark coefficient kappa from FWHM-vs-power at fixed T.

    grid: {(peak, P_watts): (fwhm_mhz, fwhm_err_mhz)} on the transition axis.
    Shared parameter: kappa (MHz per W, S0 = kappa*P). Per-peak nuisance: the
    core sigma_laser (power-independent). gamma_coll and the transit width are
    fixed at their T_C values (they only set the baseline the per-peak core
    absorbs; kappa rides on the power-DEPENDENT part).

    The QUOTED 95% bound is the PROFILE-LIKELIHOOD one (profile=True): scan
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
    # S0 prediction BAND over the OPEN w0 (S0 ~ 1/w0^2, so the small-waist edge
    # gives the high S0). At rho=1; a real rho<1 lowers both edges. From the
    # W0_BAND_M constant so the 45-70 um band is never hand-typed here.
    _w0_lo_m, _w0_hi_m = W0_BAND_M
    s0_225_pred_hi = stark_shift_S0_mhz(0.225, _w0_lo_m, rho=rho)   # 45 um -> larger S0
    s0_225_pred_lo = stark_shift_S0_mhz(0.225, _w0_hi_m, rho=rho)   # 70 um -> smaller S0
    lo = np.array([0.0] * npk + [0.0], float)
    hi = np.array([np.inf] * (npk + 1), float)

    def resid(p):
        sl = p[:npk]; kappa = p[npk]
        out = []
        for (peak, P), (f, ferr) in items:
            si = peaks.index(peak)
            fm = _fwhm_of(gamma_coll, sl[si], transit, kappa * P, nu)
            out.append((fm - f) / ferr)
        return np.array(out)

    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=4000)
    ndata = len(items)
    dof = max(ndata - len(p0), 1)
    chi2_red = float(np.sum(sol.fun ** 2) / dof)
    # covariance from the Jacobian. The fit is over-dispersed (chi2_red > 1,
    # block-to-block width scatter), so we CONSERVATIVELY inflate the parameter
    # error by sqrt(chi2_red) -- the standard over-dispersion rescale. This is
    # load-bearing: the inflated bound BRACKETS the predicted ~0.6 MHz (w0 = 50 um;
    # was 1.43 at the old 32 um nominal), while the raw (un-inflated) bound would be
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

    # -- profile-likelihood one-sided 95% bound (the quoted construction) -----
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
                    fm = _fwhm_of(gamma_coll, sl[idx[peak]], transit,
                                  kappa_fixed * P, nu)
                    out.append((fm - f) / ferr)
                return np.array(out)
            s = least_squares(r, sl_seed, bounds=(np.zeros(npk),
                                                  np.full(npk, np.inf)),
                              max_nfev=2000)
            return float(np.sum(s.fun ** 2)), s.x

        # bracket the crossing: expand upward from the minimum
        sl_seed = sol.x[:npk].copy()
        k_lo, c_lo = kappa, chi2_min
        step = max(kpred, 1.0)
        k_hi = kappa + step
        c_hi, sl_seed = chi2_at(k_hi, sl_seed)
        n_exp = 0
        while c_hi - chi2_min < profile_thresh and n_exp < 40:
            k_lo, c_lo = k_hi, c_hi
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
                k_lo, c_lo = k_mid, c_mid
            else:
                k_hi, c_hi = k_mid, c_mid
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
