"""
Model-form comparison: Voigt vs the Lehmann cusp (module M8)
===========================================================

Beyond the fixed natural Lorentzian, the ~2 MHz of extra broadening can be
modelled as a smooth GAUSSIAN (a Voigt: what you get from laser jitter) or as
a cusped two-sided EXPONENTIAL (the Lehmann transit lineshape, README 2.5).
They have the same parameter count, so a Bayesian-information-criterion (BIC)
comparison is essentially a chi^2 comparison: which shape the data prefer.

  BIC = chi2 + k*ln(N)   (weighted LS; the constant common to all models on
  the same data drops out, so only differences matter). Lower BIC wins;
  |dBIC| < 2 is "indistinguishable", > 10 is "decisive" (Kass-Raftery).

Candidate forms (all share their shape across a condition's repeats, with
per-trace amplitude/center/tilted-baseline; all windowed like the main fits):
  'voigt'   : Lorentz(Gamma_nat + gamma_coll) (x) Gaussian(w)        [2 shape]
  'lehmann' : Lorentz(Gamma_nat + gamma_coll) (x) two-sided-exp(w)   [2 shape]
  'full'    : Lorentz (x) Gaussian(w_g) (x) two-sided-exp(w_e)       [3 shape]

EXPECTATION (honest, from the two-epoch design): with the 2025 laser Gaussian
~2 MHz smearing the cusp, the archival data most likely CANNOT distinguish
voigt from lehmann (|dBIC| small). The decisive test is a fixed-lock session's narrow-laser
cold-dim data; this module is the warm-up + the infrastructure for it.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from ._compat import trapezoid
from .constants import GAMMA_NAT_HZ
from .lineshape import lorentzian, gaussian, two_sided_exponential
from .linefit import adaptive_halfwidth
from .noise import signal_level, sigma_of_v
from .fitutil import feasible_p0

GNAT = GAMMA_NAT_HZ / 1e6
SHAPES = {"voigt": ("gamma_coll", "gauss"),
          "lehmann": ("gamma_coll", "exp"),
          "full": ("gamma_coll", "gauss", "exp")}


def _profile(kind, shape, grid_pad=6.0):
    """Build (grid, area-normalized profile) for a model form from its shape
    params dict {gamma_coll, gauss?, exp?}."""
    homog = GNAT + max(shape.get("gamma_coll", 0.0), 0.0)
    widths = [homog] + [max(shape[k], 1e-6) for k in ("gauss", "exp") if k in shape]
    span = grid_pad * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / 12.0, 1e-3)
    n = int(np.ceil(span / dnu)); g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    if "gauss" in shape:
        prof = np.convolve(prof, gaussian(g, shape["gauss"]), "same") * dnu
    if "exp" in shape:
        prof = np.convolve(prof, two_sided_exponential(g, shape["exp"]), "same") * dnu
    area = trapezoid(prof, g)
    return g, (prof / area if area > 0 else prof)


def fit_form(freqs: List[np.ndarray], volts: List[np.ndarray], kind: str,
             law: Dict = None) -> Dict:
    """Joint fit of one condition's repeats with model form `kind`. Returns
    chi2 (total), k (n free params), n (data pts), bic, and shape params."""
    names = SHAPES[kind]
    ntr = len(freqs)
    # window + seeds + weights
    wf, wv, ws, c0s, a0s, b0s = [], [], [], [], [], []
    for nu, v in zip(freqs, volts):
        lev, base = signal_level(v)
        c0 = float(nu[int(np.argmax(lev))])
        m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
        wf.append(nu[m]); wv.append(v[m])
        ws.append(sigma_of_v(np.maximum(lev, 0.0), law)[m] if law is not None
                  else np.full(int(m.sum()), max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
        c0s.append(c0); a0s.append(float(lev.max())); b0s.append(base)
    nshape = len(names)
    seed_shape = {"gamma_coll": 0.3, "gauss": 1.5, "exp": 1.0}
    p0 = [seed_shape[n] for n in names]
    for i in range(ntr):
        p0 += [a0s[i], c0s[i], b0s[i], 0.0]
    p0 = np.array(p0)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[:nshape] = 0.0
    for i in range(ntr):
        lo[nshape + 4 * i] = 0.0

    def resid(p):
        shape = {names[j]: p[j] for j in range(nshape)}
        g, prof = _profile(kind, shape)
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[nshape + 4 * i: nshape + 4 * i + 4]
            model = A * np.interp(wf[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * wf[i]
            out.append((wv[i] - model) / ws[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=40000)
    if not sol.success:
        raise RuntimeError(f"{kind} fit failed: {sol.message}")
    n = sum(len(x) for x in wv); k = len(p0)
    chi2 = float(2.0 * sol.cost)
    return {"kind": kind, "chi2": chi2, "k": k, "n": n,
            "bic": chi2 + k * np.log(n),
            "chi2_red": chi2 / max(n - k, 1),
            "shape": {names[j]: float(sol.x[j]) for j in range(nshape)}}


def compare_forms(freqs, volts, law=None, kinds=("voigt", "lehmann", "full")) -> Dict:
    """Fit each form; return per-form results and the voigt-vs-lehmann dBIC
    (positive => lehmann/cusp preferred)."""
    res = {k: fit_form(freqs, volts, k, law) for k in kinds}
    out = {"forms": res}
    if "voigt" in res and "lehmann" in res:
        out["dBIC_voigt_minus_lehmann"] = res["voigt"]["bic"] - res["lehmann"]["bic"]
    return out
