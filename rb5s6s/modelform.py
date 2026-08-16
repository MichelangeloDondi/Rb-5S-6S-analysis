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

EXPECTATION (from the two-epoch design): with the 2025 laser Gaussian
~2 MHz smearing the cusp, the archival data most likely CANNOT distinguish
voigt from lehmann (|dBIC| small). The decisive test is a fixed-lock session's narrow-laser
cold-dim data; this module is the warm-up + the infrastructure for it.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

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

# which forms contain which, so a comparison can check its own arithmetic
CONTAINS = {"full": ("voigt", "lehmann")}


def info_criteria(chi2: float, k: int, n: int,
                  effective_n: float | None = None) -> Dict:
    """The criterion PANEL for a weighted-least-squares fit, on one convention.

    Four members, a robustness check across plausible selection conventions
    rather than four votes (AIC and AICc are near-kin, as are the two BIC
    variants, so agreement between all four is two families agreeing):

        AIC     = chi2 + 2k                targets predictive efficiency
                                           under its assumptions
        AICc    = AIC + 2k(k+1)/(n-k-1)    AIC's small-sample correction,
                                           converging to AIC as n grows
        BIC     = chi2 + k ln(n)           motivated by consistency UNDER a
                                           true-model-in-the-candidate-set
                                           interpretation, which this
                                           repository's own misspecification
                                           concerns do not grant; over-counts
                                           evidence when samples correlate
        BIC_eff = chi2 + k ln(effective_n) BIC with the repository's
                                           effective-sample-size adjustment
                                           (n/tau_int in practice), a
                                           repository-defined SENSITIVITY
                                           criterion and not an established
                                           theorem

    `effective_n` is a MODELLING CHOICE and must be passed explicitly by the
    caller who can defend it (sharing_bic passes n/tau_int with tau measured
    on the wing). When it is None, `bic_eff` is omitted from the result
    rather than silently equalling `bic`, so no reader can mistake an
    unadjusted number for an adjusted one.

    Preconditions for COMPARING any of these across two fits: same likelihood
    and data basis, same objective and weights, consistent parameter
    accounting. Where those fail the panel is not comparable and should not
    be quoted. At the sites in this tree ln(n) runs from 2.30 (the noise
    law's ten level bins) to 12.91 (the global fit's 404615 points, where BIC
    charges six times what AIC does), which is why the panel is reported
    numerically everywhere instead of one member being quoted alone.
    """
    lnn = float(np.log(n)) if n > 1 else 0.0
    aic = chi2 + 2.0 * k
    denom = n - k - 1
    aicc = aic + (2.0 * k * (k + 1) / denom if denom > 0 else np.inf)
    out = {"chi2": float(chi2), "k": int(k), "n": int(n),
           "aic": float(aic), "aicc": float(aicc), "bic": float(chi2 + k * lnn),
           "penalty_per_param_aic": 2.0, "penalty_per_param_bic": lnn}
    if effective_n is not None:
        if effective_n <= 1:
            raise ValueError(f"effective_n={effective_n} is not a sample size")
        out["effective_n"] = float(effective_n)
        out["bic_eff"] = float(chi2 + k * np.log(effective_n))
    return out


def compare_ic(simple: Dict, rich: Dict, nested: bool = True,
               tol: float = 0.01) -> Dict:
    """Compare two fitted forms, positive favouring `rich`.

    `simple` and `rich` are dicts carrying chi2, k and n (what `fit_form`
    returns). Differences are reported under every criterion, because which
    one is used is a decision to be made in the open.

    THE NESTING CHECK IS THE POINT. If `rich` contains `simple` as a special
    case then its chi-squared CANNOT be larger at the true optimum, so a
    positive `chi2_rich - chi2_simple` is a statement about the optimizer and
    not about the data. Measured on the committed `results/modelform.csv`
    2026-08-15, all four peaks violate it, by up to 3.23 for peak 4192, while
    the voigt-against-lehmann differences being interpreted there run 0.44 to
    3.70. The convergence residue and the signal are the same size, so the
    comparison cannot be read until the fits converge. A criterion applied to
    unconverged fits reports the optimizer's luck under a Greek letter.
    """
    out = {"dchi2": simple["chi2"] - rich["chi2"],
           "dk": rich["k"] - simple["k"]}
    crits = ["aic", "aicc", "bic"]
    if "bic_eff" in simple and "bic_eff" in rich:
        crits.append("bic_eff")
    for crit in crits:
        out["d" + crit] = simple[crit] - rich[crit]
    # the numerical deltas are the output; agree/split as a categorical would
    # flatten three different situations (marginal, moderate, large-but-
    # opposed) into one label
    signs = {np.sign(out["d" + c]) for c in crits if out["d" + c] != 0}
    out["panel_split"] = bool(len(signs) > 1)
    viol = nested and (rich["chi2"] - simple["chi2"]) > tol
    out["nesting_violated"] = bool(viol)
    out["interpretable"] = not viol
    if viol:
        out["note"] = (f"the richer form fits worse by "
                       f"{rich['chi2'] - simple['chi2']:.2f} chi2, which it "
                       f"cannot do at its own optimum: this is a convergence "
                       f"failure and no criterion can be read off it")
    return out


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
    out = {"kind": kind, "chi2_red": chi2 / max(n - k, 1),
           "shape": {names[j]: float(sol.x[j]) for j in range(nshape)}}
    # every criterion, from the one helper, so no site rolls its own penalty
    out.update(info_criteria(chi2, k, n))
    return out


def compare_forms(freqs, volts, law=None, kinds=("voigt", "lehmann", "full")) -> Dict:
    """Fit each form; return per-form results, the voigt-vs-lehmann difference
    under every criterion, and the nesting checks on the richer form.

    Voigt and Lehmann carry the SAME parameter count (two shape parameters
    each, SHAPES above), so every penalty term cancels in their difference and
    that comparison is a bare chi-squared comparison whatever criterion is
    named. It cannot be changed by moving from BIC to AIC, at any n. The
    comparisons that DO respond to the criterion are the ones against `full`,
    which carries one shape parameter more and contains both.
    """
    res = {k: fit_form(freqs, volts, k, law) for k in kinds}
    out = {"forms": res}
    if "voigt" in res and "lehmann" in res:
        # kept under its historical name, and it is a chi-squared difference
        out["dBIC_voigt_minus_lehmann"] = res["voigt"]["bic"] - res["lehmann"]["bic"]
        out["voigt_vs_lehmann"] = compare_ic(res["voigt"], res["lehmann"],
                                             nested=False)
    for rich, simples in CONTAINS.items():
        if rich not in res:
            continue
        for simple in simples:
            if simple in res:
                out[f"{simple}_vs_{rich}"] = compare_ic(res[simple], res[rich],
                                                        nested=True)
    return out
