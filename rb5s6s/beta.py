"""
Global collisional-self-broadening fit beta_self (module M4, estimator)
======================================================================

NAMING NOTE (2026-07-11): beta_self here is the COLLISIONAL
self-broadening coefficient (paper deliverable C1, an archival target) — NOT
the EOM modulation index "beta", which is a different quantity entirely and
remains DESCOPED for archival data (2025 drive voltage unrecorded; the
HWP-rotated ruler traces are AM-enhanced, so their sideband ratios carry no
modulation index). A reviewer conflated the two from the filename alone, so
the collision of names is recorded here permanently.

The per-condition fit (linefit.py) cannot cleanly separate sigma_laser from
gamma_coll (corr ~ -0.9). This module breaks that degeneracy by fitting ALL
temperatures of one peak SIMULTANEOUSLY with the collisional width tied to a
single law:

    gamma_coll(T) = beta_self * N(T)          # N in units of 1e12 cm^-3

so gamma_coll is forced to track the ~50x density rise across 70->130 C,
while sigma_laser is a SINGLE shared value pinned by every temperature at
once. The huge density lever arm is what makes beta_self identifiable where a
single Voigt decomposition is not.

Shared free params:  beta_self [MHz per 1e12 cm^-3], sigma_laser [MHz],
                     optionally transit_ref [MHz @ T_ref] (else fixed on the
                     w0 prior; w0 OPEN => absolute beta_self PRELIMINARY).
Per-trace nuisance:  A_i, center_i, b0_i, b1_i.

Weights from the M1 noise law; errors inflated by sqrt(tau_int)*sqrt(chi2_red)
(conservative, matching M2/M3).

WHAT THIS DOES AND DOES NOT GIVE:
  * gives the collisional broadening SLOPE vs density from within-session
    data (the shape of gamma_coll(T)); this is the beta_self estimate.
  * does NOT by itself settle the confound (a monotonic session drift can
    mimic a density trend) — that is the job of the confound probes in
    scripts/run_beta_self.py and the pre-registered measurement-vs-bound rule.
  * absolute value inherits the transit/w0 prior and the vapor-density
    (cold-spot) systematic (see density.py).
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import t as student_t

from . import config as C
from .density import N_SCALE_FRAC_SYST
from .lineshape import composite_profile
from .linefit import transit_fwhm_at_T
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0


def collisional_slope(N_units, widths_mhz, width_errs_mhz, snr_measure=3.0):
    """Model-independent collisional slope from raw widths vs density.

    Fits  W(N) = W0 + beta_eff * N  (weighted), then treats the RMS residual
    about that line as a BETWEEN-BLOCK systematic (laser-width drift over the
    session) added in quadrature to each point's error. This is the decisive
    confound test: pure collisional broadening is monotonic in N, so residual
    scatter beyond the within-block errors bounds how much of the trend can be
    collisional.

    Returns beta_eff, formal_err (within-block only), syst_err (with the
    between-block systematic), resid_rms, snr (=|beta|/syst_err), verdict
    ('MEASUREMENT' iff snr >= snr_measure else 'BOUND'), dof, t95, bound95,
    n_frac_syst, bound95_nscale, monotonic.

    COVERAGE of the bound (corrected 2026-07-16): the between-block scatter
    that dominates syst_err is estimated on only dof = n - 2 degrees of
    freedom (1 for the 3-point headline variant), so a one-sided 95% limit
    needs the Student-t quantile t(0.95, dof) -- 6.31 at dof=1, 2.92 at
    dof=2 -- NOT the Gaussian-asymptotic 2 that was hard-coded before. This
    is conservative where the well-determined within-block part contributes,
    which is the right direction for a bound. bound95 = |beta| + t95*syst.

    DENSITY SCALE (propagated 2026-07-16): beta ~ slope vs N, so a fractional
    error f on the N calibration moves beta by the same fraction
    (beta_true = beta_fit * N_assumed/N_true); the cold-spot direction makes
    the fitted beta an UNDERestimate, so the upper bound is inflated on the +
    side: bound95_nscale = bound95 * (1 + N_SCALE_FRAC_SYST). That final
    number is the quotable per-peak bound.

    'monotonic' is a DESCRIPTOR, not evidence: with <=4 points monotonicity is
    a 1-in-24 coincidence and, worse, a monotonic session drift aliased onto
    the monotonic T-vs-time acquisition (the 2025 confound) produces monotonic
    W-vs-N with ZERO collisional content -- so the flag cannot discriminate the
    one confound that matters. Non-monotonic (3/4 peaks) is the useful reading
    (widths falling with density cannot be pure collisions); the confound is
    handled by the BOUND framing, not by this flag.
    """
    N = np.asarray(N_units, float)
    W = np.asarray(widths_mhz, float)
    E = np.asarray(width_errs_mhz, float)
    A = np.vstack([np.ones_like(N), N]).T
    Winv = np.diag(1.0 / E ** 2)
    cov = np.linalg.inv(A.T @ Winv @ A)
    coef = cov @ A.T @ Winv @ W
    # Between-block scatter estimate: divide the summed squared residuals by
    # the DEGREES OF FREEDOM (n - p, p=2), not by n. np.mean would divide by n
    # and bias the scatter LOW by sqrt(n/(n-p)) -- for the 3-point headline
    # variant that is sqrt(3) ~ 1.7, tightening the "conservative" bound by
    # ~40% (2026-07-12). With n-p = 1-2 this estimate is itself very noisy;
    # that used to be a prose caveat ("~factor-2 own-uncertainty") and is now
    # FORMALIZED by the Student-t multiplier below (2026-07-16).
    dof = max(len(N) - 2, 1)
    resid_rms = float(np.sqrt(np.sum((W - A @ coef) ** 2) / dof))
    E_sys = np.sqrt(E ** 2 + resid_rms ** 2)
    syst_err = float(np.sqrt(np.linalg.inv(A.T @ np.diag(1.0 / E_sys ** 2) @ A)[1, 1]))
    beta_eff = float(coef[1])
    snr = abs(beta_eff) / syst_err if syst_err > 0 else 0.0
    # one-sided 95% multiplier with the scatter's own dof honoured (see docstring)
    t95 = float(student_t.ppf(0.95, dof))
    bound95 = abs(beta_eff) + t95 * syst_err
    return {
        "beta_eff": beta_eff, "formal_err": float(np.sqrt(cov[1, 1])),
        "syst_err": syst_err, "resid_rms": resid_rms, "snr": float(snr),
        "dof": int(dof), "t95": t95,
        "bound95": bound95,
        "n_frac_syst": N_SCALE_FRAC_SYST,
        "bound95_nscale": bound95 * (1.0 + N_SCALE_FRAC_SYST),
        "verdict": "MEASUREMENT" if snr >= snr_measure else "BOUND",
        "monotonic": bool(np.all(np.diff(W[np.argsort(N)]) > 0)),
    }


# composite kernel now lives in lineshape.composite_profile (revision #9);
# imported above — the fit machinery below is unchanged.


def fit_beta_self(conditions: List[Dict], *, transit_ref_mhz: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ,
                  fit_transit: bool = False, T_ref_C: float = 110.0,
                  laser_kind: str = "gaussian") -> Dict:
    """Global beta_self fit for one peak across temperatures.

    conditions: list of dicts, each
        {'T_C': float, 'N_units': float, 'freqs': [arr...], 'volts': [arr...],
         'law': <M1 law dict or None>}
      freqs already on the transition axis (MHz) via the M2 block rate.

    Returns beta_self (+err), sigma_laser (+err), transit_ref (+err if fit),
    per-condition implied gamma_coll, chi2_red, and the beta<->laser
    correlation.
    """
    # index bookkeeping: flatten all traces, remember which condition each
    # belongs to and its (N_units, T_C)
    tr_cond, freqs, volts, sigmas = [], [], [], []
    seeds_A, seeds_c, seeds_b0, tr_tau = [], [], [], []
    for ci, cond in enumerate(conditions):
        law = cond.get("law")
        tau_c = max(law.get("tau_int", 1.0), 1.0) if law else 1.0
        for nu, v in zip(cond["freqs"], cond["volts"]):
            lev, base = signal_level(v)
            ipk = int(np.argmax(lev))
            tr_cond.append(ci); freqs.append(nu); volts.append(v); tr_tau.append(tau_c)
            seeds_A.append(float(lev.max())); seeds_c.append(float(nu[ipk]))
            seeds_b0.append(float(base))
            if law is not None:
                sigmas.append(sigma_of_v(np.maximum(lev, 0.0), law))
            else:
                sigmas.append(np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
    ntr = len(freqs)

    # window each trace about its seed center, excluding off-center-sweep
    # mirror crossings (adaptive half-width; see linefit.adaptive_halfwidth)
    from .linefit import adaptive_halfwidth
    for i in range(ntr):
        m = np.abs(freqs[i] - seeds_c[i]) <= adaptive_halfwidth(freqs[i], volts[i])
        freqs[i] = freqs[i][m]; volts[i] = volts[i][m]; sigmas[i] = sigmas[i][m]

    # CORRELATED-NOISE WEIGHTING (round-3 fix): PER-BLOCK tau enters the fit
    # weights (sigma_eff = sigma * sqrt(tau_block)), so blocks with more
    # correlated noise get proportionally less pull -- previously one MEAN tau
    # multiplied the final covariance, throwing away the per-block structure.
    sigmas_raw = [s.copy() for s in sigmas]
    sigmas = [s * np.sqrt(t) for s, t in zip(sigmas, tr_tau)]

    nshared = 3 if fit_transit else 2
    p0 = [0.1, 1.0] + ([transit_ref_mhz] if fit_transit else [])
    for i in range(ntr):
        p0 += [seeds_A[i], seeds_c[i], seeds_b0[i], 0.0]
    p0 = np.array(p0, float)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[0] = 0.0            # beta_self >= 0
    lo[1] = 0.0            # sigma_laser >= 0
    if fit_transit:
        lo[2] = 0.05; hi[2] = 10.0
    for i in range(ntr):
        lo[nshared + 4 * i] = 0.0  # A_i >= 0

    def residuals(p):
        beta, sl = p[0], p[1]
        tref = p[2] if fit_transit else transit_ref_mhz
        # one profile per distinct condition (γ_coll, transit depend on T)
        profs = {}
        for ci, cond in enumerate(conditions):
            gc = beta * cond["N_units"]
            tr = transit_fwhm_at_T(cond["T_C"], tref, T_ref_C) if fit_transit \
                else transit_fwhm_at_T(cond["T_C"], transit_ref_mhz, T_ref_C)
            profs[ci] = composite_profile(gc, sl, tr, laser_kind)
        out = []
        for i in range(ntr):
            g, prof = profs[tr_cond[i]]
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            out.append((volts[i] - model) / sigmas[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds (round-5 fix)
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=60000)
    if not sol.success:
        raise RuntimeError(f"beta_self fit failed: {sol.message}")
    ndata = sum(len(v) for v in volts)
    dof = max(ndata - len(p0), 1)
    # raw chi2 (unscaled sigma) for diagnostics: undo the per-sample sqrt(tau)
    sqrt_tau = np.concatenate([np.full(len(freqs[i]), np.sqrt(tr_tau[i]))
                               for i in range(ntr)])
    chi2_red = float(np.sum((sol.fun * sqrt_tau) ** 2) / dof)
    # tau already lives in the whitened Jacobian; the max(chi2,1) rescale is a
    # documented one-sided conservative choice (see linefit.py).
    cov = cov_from_jac(sol.jac) * max(chi2_red, 1.0)
    err = np.sqrt(np.clip(np.diag(cov), 0, None))
    corr_bl = float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])) \
        if cov[0, 0] > 0 and cov[1, 1] > 0 else np.nan
    beta, sl = float(sol.x[0]), float(sol.x[1])
    return {
        "beta_self": beta, "beta_self_err": float(err[0]),
        "sigma_laser": sl, "sigma_laser_err": float(err[1]),
        "transit_ref": float(sol.x[2] if fit_transit else transit_ref_mhz),
        "transit_fitted": bool(fit_transit),
        "chi2_red": chi2_red, "corr_beta_laser": corr_bl,
        "noise_floor_limited": bool(chi2_red < 0.8),
        "beta_at_bound": bool(sol.x[0] <= 1e-9),
        "sigma_laser_at_bound": bool(sol.x[1] <= 1e-9),
        "gamma_coll_by_cond": [beta * c["N_units"] for c in conditions],
        "T_by_cond": [c["T_C"] for c in conditions],
        "N_units_by_cond": [c["N_units"] for c in conditions],
    }
