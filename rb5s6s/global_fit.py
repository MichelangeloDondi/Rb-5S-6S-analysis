"""
Hierarchical cross-peak + cross-temperature fit (module M4b, `fit_global`)
=========================================================================

The "level-3" pooling: fit ALL peaks and temperatures at once,
sharing each parameter at the level the physics licenses (PLAN M4 addendum).
The sharing structure is chosen to respect our own M4 finding that the
between-block laser width DRIFTS across the 2025 cooling session:

  * sigma_laser  -- shared PER TEMPERATURE across the 4 peaks (they are
    measured within one T-dwell, so they share one laser at that T; the four
    lines then OVER-constrain sigma_laser(T) and let its drift across T be
    MEASURED rather than mistaken for collisions). NOT shared across T --
    that global-sharing is exactly what made the M4 global fit overconfident.
    [For October's stable lock, share sigma_laser globally instead.]
    ASSUMPTION (review round 5, cannot be fully verified -- NO timestamps
    exist in the archive): per-T sharing is valid only if the 4 peaks at a
    given T were acquired close enough in time that the laser did not drift
    between them. If they were minutes apart at ~4 MHz/min drift, forcing one
    sigma_laser(T) reintroduces the very overconfidence the cross-T split
    avoids. The only internal check available is the fit's own chi2_red: if
    the 4 peaks did NOT share sigma_laser(T), the shared-per-T model would fit
    poorly. Observed chi2_red ~0.86 (good) is weak evidence they are
    consistent with a shared sigma_laser(T), not a proof.
  * beta_self    -- shared PER ISOTOPE (gamma_coll = beta[iso]*N(T)); collision
    physics does not license one common beta across isotopes, and this lets us
    TEST beta_85 vs beta_87 rather than assume them equal.
  * transit_ref  -- shared GLOBALLY (same beam, same sqrt(T) law).
  * A, center, b0, b1 -- per trace (drift + gain live here).

Why this is more powerful than the per-peak fit: the sigma_laser<->gamma_coll
Voigt degeneracy (corr ~ -0.9 in a single condition) is broken two ways at
once -- the density lever arm (N x50 across T) AND the four peaks sharing one
sigma_laser(T). What it does NOT remove: the transit/w0 degeneracy (absolute
beta still rides on w0) and, being model-based, model-form error. So its beta
is the best MODEL-BASED cross-check of the model-independent raw-width bound
(M4), not a replacement for it.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from .lineshape import composite_profile
from .linefit import transit_fwhm_at_T, adaptive_halfwidth
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0


def fit_global(blocks: List[Dict], *, transit_ref_mhz: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ,
               fit_transit: bool = False, T_ref_C: float = 110.0,
               transit_kind: str = "exp", sigma_sharing: str = "per_T") -> Dict:
    """Hierarchical fit over many (peak, T) blocks.

    blocks: list of dicts, each
        {'peak','isotope','T_C','N_units','freqs':[arr...],'volts':[arr...],'law'}
        with freqs already on the transition axis (MHz).

    transit_kind : 'exp' (Lehmann/Biraben cusp, default) | 'gaussian' (Voigt).
        The Voigt-vs-Lehmann beta spread is the transit model-form systematic.
    sigma_sharing : the lever-crosscheck Model A vs B axis --
        'per_T'     (A) one sigma_laser(T) shared across the 4 peaks at each T
                        (M4c-validated: the 4 peaks agree on one laser width);
        'per_block' (B) sigma_laser free per (peak, T) block, the conservative
                        model that lets every block float its own laser width.
        The A-vs-B beta spread is the sigma-sharing systematic. Running the 2x2
        (transit_kind x sigma_sharing) gives the full model-form error bar.

    Returns per-isotope beta_self (+err), per-group sigma_laser (+err),
    transit_ref, chi2_red, and the full shared-block covariance.
    """
    if sigma_sharing not in ("per_T", "per_block"):
        raise ValueError(f"sigma_sharing must be 'per_T'|'per_block', got {sigma_sharing!r}")
    _skey = ((lambda b: b["T_C"]) if sigma_sharing == "per_T"
             else (lambda b: (b["peak"], b["T_C"])))
    sig_keys = sorted({_skey(b) for b in blocks})          # sigma_laser groups
    beta_keys = sorted({b["isotope"] for b in blocks})     # beta per isotope
    nS, nB = len(sig_keys), len(beta_keys)
    nshared = nS + nB + (1 if fit_transit else 0)

    # N(T) must be UNIQUE per temperature (all peaks at one T see one vapor
    # density). Assert rather than silently use whichever block comes first
    # (review round 3: a manifest edit could otherwise bite silently).
    N_by_T = {}
    for b in blocks:
        if b["T_C"] in N_by_T and not np.isclose(N_by_T[b["T_C"]], b["N_units"]):
            raise ValueError(f"inconsistent N_units at T={b['T_C']}: "
                             f"{N_by_T[b['T_C']]} vs {b['N_units']}")
        N_by_T[b["T_C"]] = b["N_units"]

    # flatten traces; remember each trace's block, its sigma/beta indices,
    # window it about its seed center, precompute weights
    # CORRELATED-NOISE WEIGHTING (round-3 fix): PER-BLOCK tau_int inflates
    # each trace's sigma inside the fit (sigma_eff = sigma*sqrt(tau_block)),
    # so every block contributes its true information content; previously one
    # MEAN tau multiplied the final covariance, giving shared and nuisance
    # parameters the same (wrong) correlation exposure.
    tr = []  # (freqs, volts, sigma_eff, si, bi, N, T_C, c0, amp0, base, tau_b)
    for blk in blocks:
        si = sig_keys.index(_skey(blk)); bi = beta_keys.index(blk["isotope"])
        law = blk.get("law")
        tau_b = max(law.get("tau_int", 1.0), 1.0) if law else 1.0
        for nu, v in zip(blk["freqs"], blk["volts"]):
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
            sig = (sigma_of_v(np.maximum(lev, 0.0), law)[m] if law is not None
                   else np.full(int(m.sum()), max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
            tr.append([nu[m], v[m], sig * np.sqrt(tau_b), si, bi, blk["N_units"],
                       blk["T_C"], c0, float(lev.max()), base, tau_b])
    ntr = len(tr)

    # seeds
    p0 = [1.5] * nS + [0.1] * nB + ([transit_ref_mhz] if fit_transit else [])
    for t in tr:
        p0 += [t[8], t[7], t[9], 0.0]
    p0 = np.array(p0, float)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[:nshared] = 0.0
    if fit_transit:
        lo[nS + nB] = 0.05; hi[nS + nB] = 10.0
    for i in range(ntr):
        lo[nshared + 4 * i] = 0.0

    def residuals(p):
        sig_l = p[:nS]; beta = p[nS:nS + nB]
        tref = p[nS + nB] if fit_transit else transit_ref_mhz
        # one profile per (sigma-group, isotope, T) actually present: sigma_laser
        # is p[si] (grouped by the sharing axis), gamma_coll = beta[iso]*N(T),
        # transit scales with sqrt(T). Keyed by the block's REAL T (t[6]) so
        # Model B (per-block sigma) and any T not 1:1 with a group works; the
        # cache dedupes shared profiles (Model A: ~one per (T,iso)).
        profs = {}
        for t in tr:
            key = (t[3], t[4], t[6])           # (si, bi, T_C)
            if key not in profs:
                si_, bi_, T_ = key
                gc = beta[bi_] * N_by_T[T_]
                profs[key] = composite_profile(gc, sig_l[si_],
                                               transit_fwhm_at_T(T_, tref, T_ref_C),
                                               transit_kind=transit_kind)
        out = []
        for i, t in enumerate(tr):
            g, prof = profs[(t[3], t[4], t[6])]
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            model = A * np.interp(t[0] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * t[0]
            out.append((t[1] - model) / t[2])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds (round-5 fix)
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=80000)
    if not sol.success:
        raise RuntimeError(f"global fit failed: {sol.message}")
    ndata = sum(len(t[1]) for t in tr)
    dof = max(ndata - len(p0), 1)
    # raw chi2 for diagnostics (undo the per-sample sqrt(tau) whitening)
    sqrt_tau = np.concatenate([np.full(len(t[0]), np.sqrt(t[10])) for t in tr])
    chi2_red = float(np.sum((sol.fun * sqrt_tau) ** 2) / dof)
    # tau lives in the whitened Jacobian; max(chi2,1) is the documented
    # one-sided conservative rescale (see linefit.py).
    cov = cov_from_jac(sol.jac) * max(chi2_red, 1.0)
    err = np.sqrt(np.clip(np.diag(cov), 0, None))

    result = {
        "beta_by_isotope": {iso: float(sol.x[nS + bi]) for bi, iso in enumerate(beta_keys)},
        "beta_err_by_isotope": {iso: float(err[nS + bi]) for bi, iso in enumerate(beta_keys)},
        "sigma_laser": [float(sol.x[i]) for i in range(nS)],
        "sigma_laser_err": [float(err[i]) for i in range(nS)],
        "transit_ref": float(sol.x[nS + nB] if fit_transit else transit_ref_mhz),
        "chi2_red": chi2_red, "n_traces": ntr,
        "sig_keys": sig_keys, "beta_keys": beta_keys,
        "sigma_sharing": sigma_sharing, "transit_kind": transit_kind,
    }
    if sigma_sharing == "per_T":     # back-compat dicts keyed by temperature
        result["sigma_laser_by_T"] = {T: float(sol.x[i]) for i, T in enumerate(sig_keys)}
        result["sigma_laser_err_by_T"] = {T: float(err[i]) for i, T in enumerate(sig_keys)}
    return result
