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
  * the CONDITION NUMBER of that block (ratio of largest to smallest eigenvalue)
    -- large means ill-conditioned, i.e. one combination is essentially
    unconstrained;
  * the EIGENVECTORS -- the best-constrained direction (a total width) and the
    worst-constrained direction (the split), with their relative uncertainties.

The honest headline this produces: the archive constrains the TOTAL width well
but the SPLIT poorly -- so the individual coefficients are w0-conditional bounds,
not measurements, which is what the repository claims. The knife-edge w0
measurement is what lifts the degeneracy (it removes transit as a free width).
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
