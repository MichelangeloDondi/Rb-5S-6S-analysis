"""
Nested model ladder: is each physical component statistically warranted? (M11)
=============================================================================

A skeptic's question about the composite lineshape is not "does the full model
fit?" but "does the archive *require* each piece, or is a simpler model just as
good?". This module answers it the standard way — fit a ladder of nested models
of increasing physics and compare by BIC:

    A  Voigt            Lorentz(Gamma_nat) (x) Gaussian(sigma_laser)
    B  + transit        A (x) transit(FIXED at the w0 prior)
    C  + collisions     Lorentz(Gamma_nat + gamma_coll) (x) Gaussian (x) transit
    D  + AC-Stark ramp  C (x) triangular ramp(S0)

Each rung adds one physical mechanism. Transit is a FIXED convolution (its width
comes from the OPEN w0 prior, not a fit parameter), so A->B adds no free
parameter and is a pure goodness-of-fit test of whether the transit shape helps.
C adds gamma_coll (1 param); D adds S0 (1 param).

    BIC = chi2 + k*ln(N)    (weighted LS; lower is better)
    dBIC(rung) = BIC(simpler) - BIC(richer) > 0  favours the richer model.
    Kass-Raftery: |dBIC| < 2 "not worth a mention", 2-6 "positive",
                  6-10 "strong", > 10 "decisive".

WHAT WE EXPECT, AND WHY IT SUPPORTS THE THESIS. The archive's headline is
"bounds, not measurements". This ladder makes that quantitative rather than
asserted: A->B should be decisive (transit is real, ~1.2 MHz on a ~5 MHz line),
but C (free collisions) and especially D (free AC-Stark) should NOT clear the
gate on the drifted-lock archive -- the collisional width is a floor and the
Stark signature (skew ~ S0^3) is below detection, so adding those parameters
does not buy enough fit to justify them. A model-comparison that *declined* to
add the AC-Stark term is the statement of "we do not
claim to have measured it here."

The converse is tested on synthetics (tests/test_model_ladder.py):
on SYNTHETIC data built WITH a large S0 the ladder must pick D; on synthetic
data built with S0 = 0 it must stop at C -- i.e. the ladder cannot invent an
AC-Stark shift that is not there, and cannot miss one that is.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np
from scipy.optimize import least_squares

from .lineshape import model_profile
from .linefit import adaptive_halfwidth
from .noise import signal_level, sigma_of_v
from .fitutil import feasible_p0

# (name, free shape params, whether the fixed transit kernel is included)
LADDER = (
    ("A_voigt", (), False),
    ("B_transit", (), True),
    ("C_collisions", ("gamma_coll",), True),
    ("D_stark", ("gamma_coll", "s0"), True),
)
# sigma_laser is free in EVERY model (it is the Gaussian that a Voigt always has);
# gamma_coll / s0 switch on up the ladder; transit is a FIXED width when present.
_SEED = {"sigma_laser": 1.6, "gamma_coll": 0.3, "s0": 0.4}


def fit_ladder_model(freqs: List[np.ndarray], volts: List[np.ndarray], *,
                     free: Sequence[str], transit_fwhm: float, use_transit: bool,
                     law: Dict = None) -> Dict:
    """Joint fit of one condition's repeats under a ladder model.

    `free` lists the shape params switched on beyond the always-free
    sigma_laser (a subset of {'gamma_coll', 's0'}). `use_transit` includes the
    fixed transit kernel at `transit_fwhm`. Returns chi2 (total), k (free
    params), n (points), bic, chi2_red, and the fitted shape params.
    """
    shape_names = ["sigma_laser"] + list(free)          # order fixed for indexing
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

    ns = len(shape_names)
    p0 = [_SEED[n] for n in shape_names]
    for i in range(ntr):
        p0 += [a0s[i], c0s[i], b0s[i], 0.0]
    p0 = np.array(p0, float)
    lo = np.full_like(p0, -np.inf); hi = np.full_like(p0, np.inf)
    lo[:ns] = 0.0
    for i in range(ntr):
        lo[ns + 4 * i] = 0.0

    tr = transit_fwhm if use_transit else 0.0

    def resid(p):
        sp = {shape_names[j]: p[j] for j in range(ns)}
        nu_grid = np.arange(-45.0, 45.0, 0.01)
        prof = model_profile(nu_grid, gamma_coll=sp.get("gamma_coll", 0.0),
                             sigma_laser_fwhm=max(sp["sigma_laser"], 1e-6),
                             transit_fwhm=tr, s0=sp.get("s0", 0.0))
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[ns + 4 * i: ns + 4 * i + 4]
            model = A * np.interp(wf[i] - c, nu_grid, prof, left=0.0, right=0.0) + b0 + b1 * wf[i]
            out.append((wv[i] - model) / ws[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=40000)
    if not sol.success:
        raise RuntimeError(f"ladder fit failed: {sol.message}")
    n = sum(len(x) for x in wv); k = len(p0)
    chi2 = float(2.0 * sol.cost)
    return {"chi2": chi2, "k": k, "n": n, "bic": chi2 + k * np.log(n),
            "chi2_red": chi2 / max(n - k, 1),
            "shape": {shape_names[j]: float(sol.x[j]) for j in range(ns)}}


def _verdict(dbic: float) -> str:
    a = abs(dbic)
    return ("not worth a mention" if a < 2 else "positive" if a < 6
            else "strong" if a < 10 else "decisive")


def fit_ladder(freqs, volts, *, transit_fwhm: float, law: Dict = None) -> Dict:
    """Fit the full A->B->C->D ladder to one condition and return per-model BIC
    plus the per-rung dBIC (BIC of the simpler minus the richer; >0 favours the
    richer) and its Kass-Raftery verdict."""
    models = {}
    for name, free, use_tr in LADDER:
        models[name] = fit_ladder_model(freqs, volts, free=free,
                                        transit_fwhm=transit_fwhm, use_transit=use_tr, law=law)
    order = [m[0] for m in LADDER]
    rungs = {}
    for simpler, richer in zip(order, order[1:]):
        d = models[simpler]["bic"] - models[richer]["bic"]
        rungs[f"{simpler}->{richer}"] = {"dBIC": d, "verdict": _verdict(d),
                                         "favours": "richer" if d > 0 else "simpler"}
    return {"models": models, "rungs": rungs, "order": order}
