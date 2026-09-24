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
    [For a stable lock, share sigma_laser globally instead.]
    ASSUMPTION (not verifiable from the analysed exports, which carry no
    acquisition time; a recovered backup's timestamps exist but the
    pre-registered audit voided at content identity -- see
    docs/PREREGISTRATION_RESULTS.md): per-T sharing is valid only if the 4 peaks at a
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

from typing import Callable, Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from .lineshape import composite_profile
from .linefit import (transit_fwhm_at_T, adaptive_halfwidth, joint_condition_profile,
                      JOINT_Z_RATIO, JOINT_N_PATH, JOINT_SEED)
from .constants import W0_CENTRAL_M
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0

#: A first-order optimality above this at exit is a stop on a tolerance, not a minimum (F258).
OPTIMALITY_CEILING = 1e3


def _grouped_jacobian(fun, lo, hi, nshared: int, lens: List[int]):
    """The '2-point' finite-difference Jacobian of `fit_global`'s residuals, computed by COLUMN GROUPS.

    The shared prefix (sigma_laser, beta, the transit) reaches every residual, while trace i's four
    nuisances (amplitude, centre, two baseline terms) reach only trace i's rows. So one perturbation
    of the k-th nuisance of EVERY trace at once differences all of them together, and the Jacobian
    costs nshared + 4 residual evaluations instead of nshared + 4 * n_traces.

    IT IS THE SAME JACOBIAN, BITWISE, AND THE SAME TRAJECTORY (F301, 2026-09-22). The step per column
    is scipy's own (`approx_derivative`, the routine `least_squares` itself calls, with the same bounds),
    and a row cannot see another trace's perturbation, so every entry is the ungrouped entry exactly.
    The array is returned in FORTRAN order because that is the layout scipy's dense differencing
    returns: a C-ordered copy of the same numbers sends the trust-region step through BLAS in a
    different summation order, and the trajectory drifted by 0.13 in a parameter within 30
    evaluations. Measured on run_global_fit's own first fit (59 traces, 241 parameters, scipy 1.18.0):
    x, cost and Jacobian bitwise equal, 14.7 s against 127.3 s. `approx_derivative` and `group_columns`
    live in scipy's private `_numdiff`; `tests/test_global_fit.py` asserts the equality, so an upgrade
    that breaks it goes red instead of drifting.
    """
    from scipy.optimize._numdiff import approx_derivative, group_columns
    from scipy.sparse import lil_matrix
    m, n = int(sum(lens)), nshared + 4 * len(lens)
    S = lil_matrix((m, n), dtype=np.int8)
    S[:, :nshared] = 1
    off = 0
    for i, L in enumerate(lens):
        S[off:off + L, nshared + 4 * i: nshared + 4 * i + 4] = 1
        off += L
    S = S.tocsc()
    groups = group_columns(S)
    lb = np.broadcast_to(np.asarray(lo, float), (n,))
    ub = np.broadcast_to(np.asarray(hi, float), (n,))

    def jac(x):
        return np.asfortranarray(approx_derivative(fun, x, method="2-point", f0=fun(x),
                                                   bounds=(lb, ub), sparsity=(S, groups)).toarray())
    return jac


def fit_global(blocks: List[Dict], *, transit_ref_mhz: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ,
               fit_transit: bool = False, T_ref_C: float = 110.0,
               transit_kind: str = "exp", sigma_sharing: str = "per_T",
               laser_kind: str = "gaussian", gamma_l: float = 0.0, fit_gamma_l: bool = False,
               p0_shared=None, max_nfev: int = 80000, _jac: str = "grouped",
               model: str = "joint", w0_m: float = W0_CENTRAL_M, m2: float = 1.0,
               z_ratio: float = JOINT_Z_RATIO, joint_n_path: int = JOINT_N_PATH,
               joint_seed: int = JOINT_SEED,
               beam_factory: Optional[Callable[[float], object]] = None) -> Dict:
    """Hierarchical fit over many (peak, T) blocks.

    `model` (owner order O49, the C6b wide wave): `"joint"` (the DEFAULT) builds each
    (sigma-group, isotope, T) profile from that temperature's own `volume_line.JointTable`
    (`linefit.joint_condition_profile`, cached, at S0=0 -- this fit carries no shift
    channel, so the table replaces `composite_profile`'s analytic two-sided-exponential
    transit kernel with the atom-sampled ensemble average at the record's own waist,
    `w0_m`, default `constants.W0_CENTRAL_M`. `"convolution"` is the pre-existing
    separable form (`lineshape.composite_profile`), kept callable as the named comparison
    arm and byte-identical to every fit made before this parameter existed.
    `fit_transit=True` is refused under `model="joint"`: the transit width is the table's
    own, an emergent property of (w0_m, T), never fit.

    `beam_factory` (C6b noise wave, 2026-09-22): threaded to `linefit.joint_condition_profile`
    under `model="joint"` only. ``None`` (the default) is byte-identical to every fit made
    before this parameter existed. `lever_crosscheck.lever_crosscheck_beta`'s beam-clipping
    axis is the reason it exists: a caller passing a `beam_field.ClippedBeam`-based factory
    gets a table built from the true, bore-clipped field instead of the default
    `volume_line.GaussianBeam`, everything else about the fit unchanged.

    _jac : 'grouped' (default) computes the finite-difference Jacobian by column groups, since each
        trace's four nuisances touch only that trace's residuals (`_grouped_jacobian`); '2-point' is
        scipy's own dense differencing. The two return the same solution BITWISE (F301, 2026-09-22),
        and 'grouped' costs about nine residual evaluations per Jacobian where '2-point' costs one per
        parameter; the argument exists so that the plant can run both.

    p0_shared : optional start for the SHARED prefix of the parameter vector, in its own order
        (sigma_laser per group, beta per isotope, then transit_ref if fit_transit). A profile by
        continuation warm-starts each point from its neighbour's solution (A11); without this
        argument every point starts from the fixed seed and a pinned point far from the minimum
        crawls for minutes (F253). The per-trace seeds stay data-derived. None = the fixed seed.
    max_nfev : the optimiser's evaluation budget, exposed so a harness can bound a cell (F253).

    blocks: list of dicts, each
        {'peak','isotope','T_C','N_units','freqs':[arr...],'volts':[arr...],'law'}
        with freqs already on the transition axis (MHz).

    transit_kind : 'exp' (Lehmann/Biraben cusp, default) | 'gaussian' (Voigt).
        The Voigt-vs-Lehmann beta spread is the transit model-form systematic.
    sigma_sharing : the lever-crosscheck Model A vs B axis --
        'per_T'     (A) one sigma_laser(T) shared across the 4 peaks at each T
                        (M4c-consistent: the 4 peaks agree on one laser width in
                        an in-sample consistency check, not a proof);
        'per_block' (B) sigma_laser free per (peak, T) block, the conservative
                        model that lets every block float its own laser width.
        The A-vs-B beta spread is the sigma-sharing systematic. Running the 2x2
        (transit_kind x sigma_sharing) gives the full model-form error bar.

    Returns per-isotope beta_self (+err), per-group sigma_laser (+err),
    transit_ref, chi2_red, and the full shared-block covariance.
    """
    if model not in ("joint", "convolution"):
        raise ValueError(f"fit_global: model must be 'joint' or 'convolution', got {model!r}")
    if model == "joint" and fit_transit:
        raise ValueError(
            "fit_global: fit_transit=True is incompatible with model='joint': the transit "
            "width is derived from (w0_m, T), never fit. Pass model='convolution' to fit a "
            "free transit width.")
    if sigma_sharing not in ("per_T", "per_block"):
        raise ValueError(f"sigma_sharing must be 'per_T'|'per_block', got {sigma_sharing!r}")
    _skey = ((lambda b: b["T_C"]) if sigma_sharing == "per_T"
             else (lambda b: (b["peak"], b["T_C"])))
    sig_keys = sorted({_skey(b) for b in blocks})          # sigma_laser groups
    beta_keys = sorted({b["isotope"] for b in blocks})     # beta per isotope
    nS, nB = len(sig_keys), len(beta_keys)
    # A PERMEATED GAS IS ONE NUMBER FOR THE WHOLE CELL, so `fit_gamma_l` adds ONE shared
    # parameter and never one per block (F245, A28: it is the single width term with no P and no T
    # dependence, which is exactly what makes it separable). `linefit.fit_condition` has carried
    # this switch since 2026-08-21 and `fit_global` never exposed it, so every committed joint
    # number pins the permeated gas at exactly zero and could not test that (O56 audit, F426).
    nshared = nS + nB + (1 if fit_transit else 0) + (1 if fit_gamma_l else 0)
    _i_gl = nS + nB + (1 if fit_transit else 0)          # gamma_l's slot when it is free

    # N(T) must be UNIQUE per temperature (all peaks at one T see one vapor
    # density). Assert rather than silently use whichever block comes first
    # (a manifest edit could otherwise bite silently).
    N_by_T = {}
    for b in blocks:
        if b["T_C"] in N_by_T and not np.isclose(N_by_T[b["T_C"]], b["N_units"]):
            raise ValueError(f"inconsistent N_units at T={b['T_C']}: "
                             f"{N_by_T[b['T_C']]} vs {b['N_units']}")
        N_by_T[b["T_C"]] = b["N_units"]

    # flatten traces; remember each trace's block, its sigma/beta indices,
    # window it about its seed center, precompute weights
    # CORRELATED-NOISE WEIGHTING: PER-BLOCK tau_int inflates
    # each trace's sigma inside the fit (sigma_eff = sigma*sqrt(tau_block)),
    # so every block contributes its true information content; previously one
    # MEAN tau multiplied the final covariance, giving shared and nuisance
    # parameters the same (wrong) correlation exposure.
    tr = []  # (freqs, volts, sigma_eff, si, bi, N, T_C, c0, amp0, base, tau_b)
    for blk in blocks:
        si = sig_keys.index(_skey(blk)); bi = beta_keys.index(blk["isotope"])
        law = blk.get("law")
        # A DENSITY OUTSIDE THE VAPOUR'S PHYSICAL BAND IS A UNITS DEFECT, NOT A FIT (F250, 2026-09-21).
        # N_units is the Rb number density in 1e12 cm^-3: 0.74 at 70 C, 35.6 at 130 C on the central law, and the
        # record's cells all sit inside [0.01, 500]. A harness passed Kelvin to a callee that takes
        # Celsius and handed this function 55468, so the first residual built gamma_coll = 5547 MHz,
        # a 66 000 MHz span and 1.3 million grid points, and hung for 7h50m. Refusing here names the
        # units; hanging names nothing.
        _N = float(blk["N_units"])
        if not (0.01 <= _N <= 500.0):
            raise ValueError(
                f"block {blk.get('peak')!r} at {blk.get('T_C')} C carries N_units={_N:.4g}, outside the "
                f"Rb vapour's physical band [0.01, 500] in 1e12 cm^-3 (0.74 at 70 C, 35.6 at 130 C on the central law). "
                f"That is a units defect in the caller (F250: Celsius given as Kelvin gives 5.5e4), and a "
                f"fit on it would not return.")
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
    p0 = ([1.5] * nS + [0.1] * nB + ([transit_ref_mhz] if fit_transit else [])
          + ([max(gamma_l, 0.05)] if fit_gamma_l else []))
    for t in tr:
        p0 += [t[8], t[7], t[9], 0.0]
    p0 = np.array(p0, float)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[:nshared] = 0.0
    if fit_transit:
        lo[nS + nB] = 0.05; hi[nS + nB] = 10.0
    if fit_gamma_l:
        lo[_i_gl] = 0.0; hi[_i_gl] = 50.0        # linefit.fit_condition's own bounds
    for i in range(ntr):
        lo[nshared + 4 * i] = 0.0

    def residuals(p):
        sig_l = p[:nS]; beta = p[nS:nS + nB]
        tref = p[nS + nB] if fit_transit else transit_ref_mhz
        gl = p[_i_gl] if fit_gamma_l else gamma_l
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
                # laser_kind reached this fit for the first time on
                # 2026-08-21. Until then the hierarchical fit was hard-wired to
                # the gaussian arm while fit_condition and fit_beta_self both
                # took the toggle, so the one fit that produces the committed
                # global numbers could not be run under the kernel the other
                # two could. gamma_l arrives with it. Both default to the
                # previous behaviour exactly.
                if model == "joint":
                    # S0=0: this fit carries no shift channel, so the table replaces the
                    # analytic transit kernel with the atom-sampled ensemble average at
                    # this block's own T (F294, see linefit.joint_condition_profile).
                    # gamma_l=gl (not the outer gamma_l parameter): fit_gamma_l's fitted
                    # value must reach this branch exactly as it reaches the convolution
                    # branch below, or model="joint" (the default) would silently ignore
                    # a free permeated-gas width (merge resolution, see b_merge report).
                    profs[key] = joint_condition_profile(
                        gc, sig_l[si_], laser_kind, gamma_l=gl, s0=0.0, T_C=T_,
                        w0_m=w0_m, m2=m2, z_ratio=z_ratio, n_path=joint_n_path,
                        seed=joint_seed, beam_factory=beam_factory)
                else:
                    profs[key] = composite_profile(gc, sig_l[si_],
                                                   transit_fwhm_at_T(T_, tref, T_ref_C),
                                                   laser_kind,
                                                   transit_kind=transit_kind,
                                                   gamma_l=gl)
        out = []
        for i, t in enumerate(tr):
            g, prof = profs[(t[3], t[4], t[6])]
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            pred = A * np.interp(t[0] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * t[0]
            out.append((t[1] - pred) / t[2])
        return np.concatenate(out)

    if p0_shared is not None:
        # a warm start for a profile by continuation (A11, F253): only the shared prefix is the
        # caller's to set; the per-trace seeds are read from the traces and stay so
        p0_shared = np.asarray(p0_shared, float)
        if p0_shared.shape != (nshared,):
            raise ValueError(f"p0_shared has shape {p0_shared.shape}; the shared prefix is {nshared} long "
                             f"({nS} sigma, {nB} beta{', 1 transit' if fit_transit else ''}"
                             f"{', 1 gamma_l' if fit_gamma_l else ''})")
        p0[:nshared] = p0_shared
    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    cost0 = 0.5 * float(np.sum(residuals(p0) ** 2))
    jac = (_grouped_jacobian(residuals, lo, hi, nshared, [len(t[1]) for t in tr])
           if _jac == "grouped" else "2-point")
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=max_nfev, jac=jac)
    if not sol.success:
        raise RuntimeError(f"global fit failed: {sol.message}")
    # A SOLUTION WORSE THAN ITS OWN START IS REPORTED, NEVER RETURNED SILENTLY (F252, 2026-09-21):
    # on data generated at the truth, the free-transit arm returned 0.19 MHz at chi2 4.30 where
    # the truth reads 0.98, and nothing in the return said the minimiser had failed. This is
    # not a bias and not a rail; it is start dependence, which A45 says enters no result
    # without a check. The reading rides in the result and is printed, so a harness that
    # ignores it does so in the open.
    worse = bool(sol.cost > cost0)
    # A SOLUTION THAT IMPROVED ON ITS START BUT IS NOT STATIONARY IS NAMED TOO (2026-09-21; F258): the free-transit arm stopped after 25 evaluations at optimality 5.4e4 where the
    # pinned control sat at 12, and `worse_than_start` was False. The ceiling is stated, not tuned:
    # scipy's default gtol is 1e-8 on a scaled gradient, and a first-order optimality above 1e3 is
    # a stop on ftol or xtol with the gradient still large, which is not a minimum.
    stalled = bool(sol.optimality > OPTIMALITY_CEILING)
    if stalled:
        import sys as _sys
        print(f"fit_global: the solver stopped at first-order optimality {sol.optimality:.3g}, above "
              f"the ceiling {OPTIMALITY_CEILING:g}: it improved on its start but is not at a stationary "
              f"point (F258). Tighten the tolerances or warm-start; do not read this fit as a result.",
              file=_sys.stderr)
    if worse:
        import sys as _sys
        print(f"fit_global: the solution's cost {sol.cost:.6g} EXCEEDS the cost at its start "
              f"{cost0:.6g}; the minimiser did not find its own minimum (start dependence, "
              f"F252). Scan the parameter or warm-start it; do not read this fit as a result.",
              file=_sys.stderr)
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
        # THE PERMEATED GAS, AND THE FLAG SAYING WHETHER IT WAS MEASURED OR ASSUMED. A caller that
        # reads `gamma_l` without `gamma_l_fitted` cannot tell a fitted 0.12 from the pinned 0.0
        # that every committed joint number carries, which is the whole point of the switch.
        "gamma_l": float(sol.x[_i_gl] if fit_gamma_l else gamma_l),
        "gamma_l_err": float(err[_i_gl]) if fit_gamma_l else float("nan"),
        "gamma_l_fitted": bool(fit_gamma_l),
        "chi2_red": chi2_red, "n_traces": ntr,
        # for BIC (M14): raw counts AND the correlation-corrected effective ones.
        # The fit whitens each residual by sqrt(tau_block), so the matching
        # effective sample size divides each block's points by its tau; using raw
        # N with the whitened chi2 (or vice-versa) double-counts the correlation.
        "ndata": ndata, "nparams": len(p0),
        "chi2_whitened": float(2.0 * sol.cost),                      # sum of whitened resid^2
        "ndata_eff": float(sum(len(t[0]) / t[10] for t in tr)),      # sum n_block / tau_block
        "noise_floor_limited": bool(chi2_red < 0.8),
        "cost_at_start": float(cost0), "cost": float(sol.cost),   # 0.5 * sum of whitened resid^2
        "worse_than_start": worse, "not_stationary": stalled,   # F258: an early stop, named                                 # F252: a failed minimiser, named
        "nfev": int(sol.nfev), "optimality": float(sol.optimality),   # K-D: how the solver stopped, not only where
        "params_at_bound": sorted(
            [f"sigma_{k}" for i, k in enumerate(sig_keys) if sol.x[i] <= 1e-9]
            + [f"beta_{iso}" for bi, iso in enumerate(beta_keys)
               if sol.x[nS + bi] <= 1e-9]),
        "sig_keys": sig_keys, "beta_keys": beta_keys,
        "sigma_sharing": sigma_sharing, "transit_kind": transit_kind, "model": model,
    }
    if sigma_sharing == "per_T":     # back-compat dicts keyed by temperature
        result["sigma_laser_by_T"] = {T: float(sol.x[i]) for i, T in enumerate(sig_keys)}
        result["sigma_laser_err_by_T"] = {T: float(err[i]) for i, T in enumerate(sig_keys)}
    return result
