"""
Identifiability of the width decomposition (M12)
================================================

A referee's sharpest statistical question about the composite line is not "what
are gamma_coll, sigma_laser, transit?" but "are they *separately* identifiable,
or does the data only constrain some combination of them?". The three widths all
broaden the same ~5 MHz line, so they are near-degenerate -- which is exactly why
the main analysis FIXES transit from the w0 prior and reports sigma_laser as a
bound. This module makes that degeneracy quantitative instead of asserted.

It fits ONE condition with all three homogeneous/quasi-homogeneous widths free
(gamma_coll, sigma_laser, transit) plus the per-trace nuisances, then reads off
the parameter covariance (SVD of the Jacobian, `fitutil.cov_from_jac`) and
reports, for the 3x3 width block:

  * the CORRELATION MATRIX -- the pairwise trade-offs (expect sigma_laser vs
    transit near -1: the w0 degeneracy; sigma_laser vs gamma_coll strongly
    negative: the Voigt core degeneracy);
  * the CONDITION NUMBER of that 3x3 width-block COVARIANCE (the ratio of its
    largest to smallest eigenvalue -- not of the Jacobian or the Fisher matrix)
    -- large means ill-conditioned, i.e. one combination is essentially
    unconstrained;
  * the EIGENVECTORS -- the best-constrained direction (a total width) and the
    worst-constrained direction (the split), with their relative uncertainties.

The covariance is LOCAL -- a quadratic (Gaussian) approximation at the optimum --
so by itself it cannot exclude a curved ("banana") valley or a second minimum.
`width_profile_2d` supplies the GLOBAL complement: the profile-likelihood map in
the (gamma_coll, sigma_laser) plane, minimising chi2 over transit AND every
per-trace nuisance at each grid point. In the Gaussian limit the profile
contours coincide with the marginal (gamma_coll, sigma_laser) covariance
ellipse, so overlaying the two is a direct test of whether the local covariance
can be trusted: a straight elongated valley matching the ellipse validates it; a
curved valley or an unclosed contour is exactly what it would hide.

The honest headline this produces: the archive constrains the TOTAL width well
but the SPLIT poorly -- so the individual coefficients are w0-conditional bounds,
not measurements, which is what the repository claims. The knife-edge w0
measurement COLLAPSES the degeneracy -- it fixes transit to within its own
precision, so the split becomes identifiable within that uncertainty (a
perfectly-known w0 would remove it exactly; a real one greatly reduces it).
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

from .lineshape import model_profile
from .linefit import adaptive_halfwidth
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0

WIDTHS = ("gamma_coll", "sigma_laser", "transit")


def width_identifiability(freqs: List[np.ndarray], volts: List[np.ndarray],
                          law: Dict = None, seeds=(0.4, 1.3, 1.2)) -> Dict:
    """Fit one condition with (gamma_coll, sigma_laser, transit) all free and
    return the 3x3 width-block correlation matrix, its condition number, and the
    best/worst-constrained eigen-directions."""
    ntr = len(freqs)
    wf, wv, ws, c0s, a0s, b0s = [], [], [], [], [], []
    for nu, v in zip(freqs, volts):
        lev, base = signal_level(v)
        c0 = float(nu[int(np.argmax(lev))])
        m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
        wf.append(nu[m]); wv.append(v[m])
        ws.append(sigma_of_v(np.maximum(lev, 0.0), law)[m] if law is not None
                  else np.full(int(m.sum()), max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
        c0s.append(c0); a0s.append(float(lev.max())); b0s.append(base)

    ns = 3
    p0 = list(seeds)
    for i in range(ntr):
        p0 += [a0s[i], c0s[i], b0s[i], 0.0]
    p0 = np.array(p0, float)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[:ns] = 1e-6
    for i in range(ntr):
        lo[ns + 4 * i] = 0.0
    nu_grid = np.arange(-45.0, 45.0, 0.01)

    def resid(p):
        gc, sl, tr = p[0], p[1], p[2]
        prof = model_profile(nu_grid, gamma_coll=max(gc, 0.0),
                             sigma_laser_fwhm=max(sl, 1e-6), transit_fwhm=max(tr, 0.0))
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[ns + 4 * i: ns + 4 * i + 4]
            model = A * np.interp(wf[i] - c, nu_grid, prof, left=0.0, right=0.0) + b0 + b1 * wf[i]
            out.append((wv[i] - model) / ws[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=60000)
    if not sol.success:
        raise RuntimeError(f"identifiability fit failed: {sol.message}")

    cov = cov_from_jac(sol.jac)[:ns, :ns]            # width sub-block
    sd = np.sqrt(np.clip(np.diag(cov), 1e-30, None))
    corr = cov / np.outer(sd, sd)
    evals, evecs = np.linalg.eigh(cov)               # ascending eigenvalues
    cond = float(evals[-1] / max(evals[0], 1e-30))   # ill-conditioning of the split
    best = evecs[:, 0]                                # smallest variance = best constrained
    worst = evecs[:, -1]                             # largest variance = the degenerate combo
    return {
        "widths": list(WIDTHS),
        "chi2": float(2.0 * sol.cost),
        "ndata": int(sum(len(x) for x in wv)),
        "nparams": int(len(p0)),
        "fit": {"gamma_coll": float(sol.x[0]), "sigma_laser": float(sol.x[1]),
                "transit": float(sol.x[2])},
        "corr": corr, "cov": cov,
        "condition_number": cond,
        "sigma_by_width": {WIDTHS[i]: float(sd[i]) for i in range(ns)},
        "best_constrained_dir": {WIDTHS[i]: float(best[i]) for i in range(ns)},
        "best_constrained_sigma": float(np.sqrt(evals[0])),
        "worst_constrained_dir": {WIDTHS[i]: float(worst[i]) for i in range(ns)},
        "worst_constrained_sigma": float(np.sqrt(evals[-1])),
    }


def width_profile_2d(freqs: List[np.ndarray], volts: List[np.ndarray],
                     law: Dict = None, *, gc_grid, sl_grid,
                     transit_seed: float = 1.2, nu_step: float = 0.01,
                     audit_stride: int = 0) -> Dict:
    """Profile likelihood in the (gamma_coll, sigma_laser) plane.

    At each grid point (gamma_coll, sigma_laser) is FIXED and chi2 is minimised
    over the transit width AND every per-trace nuisance (A, center, baseline
    slope/offset) -- the exact frequentist profile construction, matching the
    profile bound used for the AC-Stark kappa (stark.py). The map answers the
    question the local covariance cannot: is the (gamma_coll, sigma_laser)
    degeneracy a straight Gaussian valley (covariance trustworthy), a curved
    banana (it is not), or an unclosed region running to a physical rail?

    Numerics: the grid is walked in serpentine order and each fit is WARM-STARTED
    from its neighbour's solution -- the surface is smooth, so this both speeds
    the scan up several-fold and prevents the isolated-restart optimiser noise
    that would show up as spurious dchi2 texture. Each cell is additionally fit
    from the independent warm lineage directly above (best kept), and every
    `audit_stride`-th cell from the fresh seed, so a warm-start trap must fool
    two lineages coherently AND survive the audit. Deterministic (no RNG).

    Returns the grids, dchi2[i_sl][i_gc] = chi2 - min(chi2), the raw chi2_min,
    the grid-minimum location, the per-cell profiled TRANSIT (and its railed
    mask: where transit pins at its 0 bound the Gaussian profile<->marginal-
    ellipse equivalence does not hold, so ellipse/straightness verdicts must be
    read on the unpinned region only), and closed_68/closed_95: whether the
    joint 2-parameter 68%/95% regions (dchi2 = 2.30 / 5.99) close inside the
    grid, evaluated with sub-grid (parabolic) minima along each boundary so a
    narrow valley crossing between edge nodes is not missed; edges_open names
    any open edge. audit_stride > 0 additionally refits every Nth cell from the
    fresh seed (a trapping audit for the warm start), ADOPTS any improvement,
    and reports the largest gain found -- audit_max_gain well below the 2.30
    contour scale certifies the warm-started surface. The dchi2 values are RAW
    (unscaled): this is a shape diagnostic against the raw covariance ellipse,
    not a quoted confidence region (the headline bounds carry their own
    chi2_red-scaled constructions)."""
    ntr = len(freqs)
    wf, wv, ws, c0s, a0s, b0s = [], [], [], [], [], []
    for nu, v in zip(freqs, volts):
        lev, base = signal_level(v)
        c0 = float(nu[int(np.argmax(lev))])
        m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
        wf.append(nu[m]); wv.append(v[m])
        ws.append(sigma_of_v(np.maximum(lev, 0.0), law)[m] if law is not None
                  else np.full(int(m.sum()), max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
        c0s.append(c0); a0s.append(float(lev.max())); b0s.append(base)

    gc_grid = np.asarray(gc_grid, float); sl_grid = np.asarray(sl_grid, float)
    nu_grid = np.arange(-45.0, 45.0, nu_step)
    # nonlinear params: [transit, c_1..c_ntr]; the per-trace (A, b0, b1) are
    # LINEAR given the shape and center, so they are solved exactly by weighted
    # least squares inside the residual (variable projection). This shrinks the
    # finite-difference Jacobian from 1+4*ntr to 1+ntr columns, and the
    # transit-kernel profile is cached: perturbing a center leaves it unchanged.
    lo = np.full(1 + ntr, -np.inf); hi = np.full(1 + ntr, np.inf)
    lo[0] = 1e-6                                    # transit >= 0

    def fit_at(gc, sl, seed):
        cache = {"tr": None, "prof": None}

        def profile_for(tr):
            if cache["tr"] != tr:
                cache["tr"] = tr
                cache["prof"] = model_profile(nu_grid, gamma_coll=gc,
                                              sigma_laser_fwhm=max(sl, 1e-6),
                                              transit_fwhm=max(tr, 0.0))
            return cache["prof"]

        def resid(p):
            prof = profile_for(float(p[0]))
            out = []
            # errstate: macOS Accelerate raises spurious FP flags in matmul on
            # perfectly finite inputs; the isfinite check below keeps us honest
            with np.errstate(all="ignore"):
                for i in range(ntr):
                    g = np.interp(wf[i] - p[1 + i], nu_grid, prof, left=0.0, right=0.0)
                    X = np.column_stack([g, np.ones_like(wf[i]), wf[i]]) / ws[i][:, None]
                    y = wv[i] / ws[i]
                    theta, *_ = np.linalg.lstsq(X, y, rcond=None)
                    if theta[0] < 0.0:             # amplitude rail: refit baseline only
                        Xb = X[:, 1:]
                        tb, *_ = np.linalg.lstsq(Xb, y, rcond=None)
                        theta = np.array([0.0, tb[0], tb[1]])
                    out.append(y - X @ theta)
            r = np.concatenate(out)
            if not np.isfinite(r).all():
                raise RuntimeError("non-finite residual in width_profile_2d")
            return r

        sol = least_squares(resid, feasible_p0(seed, lo, hi), bounds=(lo, hi),
                            max_nfev=20000)
        return float(2.0 * sol.cost), sol.x

    seed0 = np.array([transit_seed] + c0s, float)

    # serpentine walk: consecutive points are always grid-adjacent (within a row,
    # or vertically at the turn), so ONE running seed warm-starts every fit. A
    # single warm lineage can still drag a trapped basin along the walk, so
    # every cell (beyond the first row) is ALSO fit from the solution directly
    # above -- an independent warm lineage -- and the better chi2 kept: a trap
    # must now fool two lineages coherently, and the fresh-seed audit below
    # bounds whatever residue could survive even that.
    nsl, ngc = len(sl_grid), len(gc_grid)
    Z = np.full((nsl, ngc), np.nan)
    sols = np.empty((nsl, ngc), dtype=object)
    seed = seed0
    for i, sl in enumerate(sl_grid):
        order = list(range(ngc)) if i % 2 == 0 else list(range(ngc - 1, -1, -1))
        for j in order:
            chi2, sol = fit_at(float(gc_grid[j]), float(sl), seed)
            if i > 0:
                c2, s2 = fit_at(float(gc_grid[j]), float(sl), sols[i - 1, j])
                if c2 < chi2:
                    chi2, sol = c2, s2
            Z[i, j], sols[i, j] = chi2, sol
            seed = sol

    # trapping audit: refit a deterministic subsample from the fresh seed; any
    # improvement is ADOPTED (the map must be the best chi2 we know), and the
    # largest gain is reported as the warm-start-trapping bound
    audit_max_gain = 0.0
    if audit_stride > 0:
        for i in range(nsl):
            for j in range(ngc):
                if (i * ngc + j) % audit_stride == 0:
                    c2, s2 = fit_at(float(gc_grid[j]), float(sl_grid[i]), seed0)
                    if c2 < Z[i, j]:
                        audit_max_gain = max(audit_max_gain, Z[i, j] - c2)
                        Z[i, j], sols[i, j] = c2, s2

    chi2_min = float(Z.min())
    D = Z - chi2_min
    i_sl, i_gc = np.unravel_index(int(np.argmin(Z)), Z.shape)
    transit = np.array([[float(sols[i, j][0]) for j in range(ngc)] for i in range(nsl)])
    # sub-grid (parabolic) minimum VALUE along each boundary line, so a valley
    # narrower than the node spacing crossing an edge is still detected
    def _line_min(y):
        y = np.asarray(y, float)
        m = float(y.min())
        for jj in range(1, len(y) - 1):
            denom = y[jj - 1] - 2.0 * y[jj] + y[jj + 1]
            if denom > 1e-12:
                d = 0.5 * (y[jj - 1] - y[jj + 1]) / denom
                if abs(d) <= 1.0:          # vertex inside the cell: trust it
                    m = min(m, float(y[jj] - 0.25 * (y[jj - 1] - y[jj + 1]) * d))
        return m
    edges = {"sl_low": _line_min(D[0, :]), "sl_high": _line_min(D[-1, :]),
             "gc_low": _line_min(D[:, 0]), "gc_high": _line_min(D[:, -1])}
    return {
        "gc_grid": gc_grid, "sl_grid": sl_grid, "dchi2": D,
        "chi2_min": chi2_min,
        "gc_at_min": float(gc_grid[i_gc]), "sl_at_min": float(sl_grid[i_sl]),
        "transit": transit,
        "transit_railed": transit < 0.02,          # pinned at the 0 bound (MHz)
        "closed_68": bool(min(edges.values()) > 2.30),
        "closed_95": bool(min(edges.values()) > 5.99),
        "edge_min_dchi2": float(min(edges.values())),
        "edges_open": sorted(k for k, v in edges.items() if v <= 5.99),
        "audit_max_gain": float(audit_max_gain),
    }


def subgrid_argmin(x, y):
    """Sub-grid minimum location by parabolic-vertex refinement about the
    discrete argmin -- exact for a parabola sampled on a uniform grid; clamped
    to one grid step so a pathological row cannot extrapolate."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    j = int(np.argmin(y))
    if 0 < j < len(y) - 1:
        denom = y[j - 1] - 2.0 * y[j] + y[j + 1]
        if abs(denom) > 1e-12:
            d = 0.5 * (y[j - 1] - y[j + 1]) / denom
            return float(x[j] + max(-1.0, min(1.0, d)) * (x[j + 1] - x[j]))
    return float(x[j])


def valley_floor(gc_grid, sl_grid, dchi2, *, within: float = 5.99,
                 row_mask=None) -> Dict:
    """The profile valley's floor and its straightness (the 'banana' test).

    For each sigma_laser row whose minimum lies inside the joint-95% region
    (dchi2 < `within`), locate the sub-grid gamma_coll that minimises dchi2;
    fit a straight line gc*(sl) through the floor points. Returns the floor
    points, the ridge slope d(gamma_coll)/d(sigma_laser) (the degeneracy
    direction), and the RMS deviation of the floor about the line -- a curved
    ('banana') valley shows up as an RMS well above the gc grid step, which is
    exactly the non-Gaussianity the local covariance cannot represent.

    Rows whose discrete minimum sits ON a gamma_coll grid edge are excluded
    from the line fit (their sub-grid position is a clamp, not a minimum), and
    `row_mask` (per-sl boolean) restricts the fit further -- e.g. to rows where
    the profiled transit is not pinned at its 0 bound, where the Gaussian
    profile<->ellipse correspondence this metric feeds actually holds."""
    gc_grid = np.asarray(gc_grid, float); sl_grid = np.asarray(sl_grid, float)
    D = np.asarray(dchi2, float)
    fs, fg = [], []
    for i in range(len(sl_grid)):
        if row_mask is not None and not row_mask[i]:
            continue
        j = int(np.argmin(D[i]))
        if j == 0 or j == len(gc_grid) - 1:        # edge-clamped: not a minimum
            continue
        if np.nanmin(D[i]) < within:
            fs.append(float(sl_grid[i])); fg.append(subgrid_argmin(gc_grid, D[i]))
    fs = np.array(fs); fg = np.array(fg)
    out = {"floor_sl": fs, "floor_gc": fg,
           "ridge_slope": float("nan"), "banana_rms": float("nan"),
           "gc_step": float(gc_grid[1] - gc_grid[0]) if len(gc_grid) > 1 else float("nan")}
    if len(fs) >= 3:
        A = np.vstack([fs, np.ones_like(fs)]).T
        coef, *_ = np.linalg.lstsq(A, fg, rcond=None)
        out["ridge_slope"] = float(coef[0])
        out["banana_rms"] = float(np.sqrt(np.mean((fg - A @ coef) ** 2)))
    return out
