"""
Dynamic scalar polarizabilities of Rb 5S1/2 and 6S1/2 (M16)
===========================================================

Sum-over-states dynamic scalar polarizabilities alpha(omega) for the two states
of the 993 nm two-photon line, from PUBLISHED reduced matrix elements and NIST
energies -- every number in the tables below carries its source. Three jobs:

1. the INDEPENDENT recompute of the differential polarizability
   Delta_alpha(993 nm) that THEORY_NOTE section 5 promises a referee (the
   shipped magnitude rides on Orson et al. 2021's +-1093 a.u.);
2. VALIDATION against precision measurements that the model does not use:
   the measured 5S scalar tune-out 790.032 nm (Leonard et al. 2015) -- this
   model reproduces it to ~2 pm -- the measured static alpha_5S 318.79(1.42),
   and the Safronova-group static alpha_6S 5167(22);
3. the 5S-6S MAGIC WAVELENGTHS (alpha_5S = alpha_6S crossings, unpublished to
   the depth searched 2026-07-17) and alpha_6S(1064) (also unpublished), the
   design inputs for a state-insensitive trap on this transition.

THE SIGN FINDING (flagged, not silently adopted). With these matrix elements
the differential at 993 nm is alpha_6S - alpha_5S ~ -1150 a.u.: at 993 nm the
5S state (red of the D lines) shifts DOWN while 6S -- whose dominant couplings
6S-6P lie far to the red at 2.73/2.79 um, so the 993 field drives them far
blue-detuned -- shifts UP. The transition therefore shifts BLUE. Orson et al.
2021 print alpha_56 = alpha_5S - alpha_6S = -1093 (hence a red shift, their
Delta f = -0.66 MHz): SAME magnitude within ~5%, OPPOSITE sign. The archival
results are sign-immune (C3c is a symmetric null, C3d and the prediction band
use |Delta_alpha|), but the fixed-lock pull DIRECTION and the ramp's stated
side depend on it; the repository keeps the established convention in the
narrative until the discrepancy is adjudicated (a one-line check for a
theorist: the sign of alpha_6S at 993 nm). See docs/THEORY_NOTE.md section 5.

Matrix elements (reduced E1, atomic units) and their sources:
  5S->5P     4.231(3) / 5.978(5)      Volz & Schmoranzer, Phys. Scr. T65, 48
                                      (1996), as recommended by the
                                      Safronova-group portal
  5S->6P     0.3235(9) / 0.5230(8)    Herold et al., PRL 109, 243003 (2012)
  5S->7P,8P  0.1154(81)/0.202(11), 0.0598(57)/0.1110(74)
                                      Safronova-group portal (S&S 2011
                                      lineage, retrieved 2026-07-17)
  5S->9P..12P + tail + core           Leonard et al., PRA 92, 052501 (2015),
                                      Table II (tails 0.022(22)+0.075(75);
                                      core+vc 8.709(93))
  6S->5P..8P                          Safronova-group portal (S&S 2011
                                      lineage): 4.1462(82), 6.048(13),
                                      9.720(25), 13.645(36), 0.992(18),
                                      1.540(25), 0.3936(54), 0.6285(96)
  6S core    9.1(5)                   Safronova, Williams & Clark, PRA 69,
                                      022509 (2004); Arora et al. 2007
  6S tail    +3.4 (fixed by the Safronova-group static alpha_6S = 5167(22);
             varied +-100% in the uncertainty band; consistent with Zang
             et al. 2012's bound that states above 8P contribute < 0.1%)
Energies: NIST ASD (Rb I, cm^-1) for 5P-8P and 6S; Leonard Table II for
9P-12P. All levels relative to the 5S ground state.

The uncertainty band on every derived number is a deterministic Monte Carlo
(fixed seed): matrix elements, cores and tails drawn from their quoted
1-sigma uncertainties, the derived quantity's 16th-84th percentile reported.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy.optimize import brentq

CM_PER_HARTREE = 219474.6313632
E_6S_CM = 20132.510                       # NIST ASD

# (energy above 5S ground [cm^-1], RME [a.u.], RME 1-sigma)
LINES_5S = (
    (12578.950, 4.231, 0.003), (12816.545, 5.978, 0.005),
    (23715.081, 0.3235, 0.0009), (23792.591, 0.5230, 0.0008),
    (27835.02, 0.1154, 0.0081), (27870.11, 0.202, 0.011),
    (29834.94, 0.0598, 0.0057), (29853.79, 0.1110, 0.0074),
    (30958.91, 0.037, 0.003), (30970.19, 0.073, 0.005),
    (31653.85, 0.026, 0.002), (31661.16, 0.053, 0.004),
    (32113.55, 0.020, 0.001), (32118.52, 0.040, 0.003),
    (32433.50, 0.016, 0.001), (32437.04, 0.033, 0.002),
)
TAIL_5S, TAIL_5S_SIG = 0.097, 0.097       # Leonard tails (n>12), +-100%
CORE_5S, CORE_5S_SIG = 8.709, 0.093       # Leonard "core + vc"

LINES_6S = (
    (12578.950, 4.1462, 0.0082), (12816.545, 6.048, 0.013),
    (23715.081, 9.720, 0.025), (23792.591, 13.645, 0.036),
    (27835.02, 0.992, 0.018), (27870.11, 1.540, 0.025),
    (29834.94, 0.3936, 0.0054), (29853.79, 0.6285, 0.0096),
)
CORE_6S, CORE_6S_SIG = 9.1, 0.5
TAIL_6S, TAIL_6S_SIG = 3.4, 3.4           # fixed by static 5167(22); +-100%

# 6S->nP resonance wavelengths (nm) bound the pole-free search windows
_POLES_6S_NM = sorted(1e7 / abs(e - E_6S_CM) for e, _, _ in LINES_6S)


def _alpha(lines, lam_nm, upper_cm=0.0, tail=0.0, core=0.0, scale=None,
           prefactor=1.0 / 6.0):
    """Scalar polarizability (a.u.) of a state from its line list.
    alpha0(w) = prefactor * sum 2*dE*d^2 / (dE^2 - w^2), dE = E_line - E_state.
    prefactor = 1/(3(2J+1)): 1/6 for J=1/2 (5S/6S/7S), 1/18 for J=5/2 (5D5/2)."""
    w = (1e7 / lam_nm) / CM_PER_HARTREE if lam_nm else 0.0
    s = 0.0
    for i, (e, d, _) in enumerate(lines):
        de = (e - upper_cm) / CM_PER_HARTREE
        dd = d if scale is None else scale[i]
        s += 2.0 * de * dd * dd / (de * de - w * w)
    return s * prefactor + tail + core


def alpha_5s(lam_nm: float, scale=None, tail=TAIL_5S, core=CORE_5S) -> float:
    """Dynamic scalar polarizability of 5S1/2 (a.u.); lam_nm=0 gives static."""
    return _alpha(LINES_5S, lam_nm, 0.0, tail, core, scale)


def alpha_6s(lam_nm: float, scale=None, tail=TAIL_6S, core=CORE_6S) -> float:
    """Dynamic scalar polarizability of 6S1/2 (a.u.); lam_nm=0 gives static."""
    return _alpha(LINES_6S, lam_nm, E_6S_CM, tail, core, scale)


def delta_alpha(lam_nm: float, **kw) -> float:
    """alpha_6S - alpha_5S (a.u.) -- the light shift's differential; its SIGN
    at 993 nm is the flagged finding (module docstring)."""
    return alpha_6s(lam_nm) - alpha_5s(lam_nm)


def tuneout_5s(lo: float = 781.0, hi: float = 794.0) -> float:
    """The 5S scalar tune-out between the D lines (nm) -- the validation
    anchor: Leonard et al. measured 790.03235(3) nm."""
    return brentq(lambda x: alpha_5s(x), lo, hi, xtol=1e-6)


def magic_wavelengths(lo: float = 950.0, hi: float = 1500.0):
    """All alpha_5S = alpha_6S crossings in [lo, hi] nm, searched between the
    6S->nP poles. Returns a list of (lambda_nm, alpha_at_crossing_au)."""
    edges = [lo] + [p for p in _POLES_6S_NM if lo < p < hi] + [hi]
    out = []
    f = lambda x: alpha_6s(x) - alpha_5s(x)
    for a, b in zip(edges, edges[1:]):
        aa, bb = a + 1.5, b - 1.5                 # stay off the poles
        if bb <= aa:
            continue
        g = np.linspace(aa, bb, 300)
        v = [f(x) for x in g]
        for i in range(len(g) - 1):
            if v[i] * v[i + 1] < 0:
                x = brentq(f, g[i], g[i + 1], xtol=1e-6)
                out.append((float(x), float(alpha_5s(x))))
    return out


def mc_band(fn, n: int = 1500, seed: int = 0) -> Dict:
    """Deterministic uncertainty band: draw all matrix elements, cores and
    tails from their quoted 1-sigma; return the median and 16/84 percentiles
    of fn(draw), where fn(kw5, kw6) evaluates the derived quantity with
    kw5 = dict(scale=..., tail=..., core=...) for 5S and kw6 likewise for 6S.
    Draws where fn fails (a crossing leaving its window) are dropped and
    counted."""
    rng = np.random.default_rng(seed)
    vals, failed = [], 0
    for _ in range(n):
        s5 = [max(d + rng.normal(0.0, sd), 0.0) for _, d, sd in LINES_5S]
        s6 = [max(d + rng.normal(0.0, sd), 0.0) for _, d, sd in LINES_6S]
        kw5 = dict(scale=s5, tail=TAIL_5S + rng.normal(0.0, TAIL_5S_SIG),
                   core=CORE_5S + rng.normal(0.0, CORE_5S_SIG))
        kw6 = dict(scale=s6, tail=TAIL_6S + rng.normal(0.0, TAIL_6S_SIG),
                   core=CORE_6S + rng.normal(0.0, CORE_6S_SIG))
        try:
            vals.append(fn(kw5, kw6))
        except Exception:
            failed += 1
    if not vals:
        return {"median": float("nan"), "lo": float("nan"),
                "hi": float("nan"), "n": 0, "failed": failed}
    v = np.sort(np.asarray(vals, float))
    return {"median": float(np.median(v)), "lo": float(np.percentile(v, 16)),
            "hi": float(np.percentile(v, 84)), "n": len(v), "failed": failed}


# ---------------------------------------------------------------------------
# The Ti:Sapph ladder: 5S->7S (760 nm) and 5S->5D5/2 (778 nm).
#
# 7S is treated on the SAME footing as 6S: an S1/2 state, scalar-only, coupling
# only to nP -- an INDEPENDENT sum-over-states here, from the Safronova-group
# all-order matrix elements (physics/0307057, Table I, retrieved 2026-07-17;
# quoted accurate to <=2%, taken as the 1-sigma) and NIST energies.
#
# 5D5/2 is NOT recomputed from scratch: it is a J=5/2 state with SCALAR + TENSOR
# polarizability and nP AND nF couplings, and its magic wavelength sits on the
# near-resonant 5P3/2-5D5/2 line whose matrix element is itself contested. That
# full calculation is Hamilton et al. 2023 (Phys. Rev. A 108, 023111; PDF in
# hand), who MEASURE the 5S1/2-5D5/2 magic wavelength = 776.179(5) nm (theory
# 776.21) and the 5P3/2-5D5/2 element = 1.80(6) a.u. We ADOPT their magic (=
# the transition-shift sign-flip) as authoritative and only illustrate the
# near-776 Delta_alpha shape from the one verified near-resonant pole; a full
# independent 5D recompute needs the 5D-nF elements (not in the Safronova 2004
# tables) and the tensor treatment, and is flagged as future work.
# ---------------------------------------------------------------------------

E_7S_CM = 26311.437                        # NIST ASD, 7S1/2 above 5S ground
E_5D52_CM = 25703.498                      # NIST ASD, 5D5/2 above 5S ground

# (energy above 5S [cm^-1], <7S||D||nP> [a.u.], 1-sigma): Safronova 2004 Table I
# all-order, 2% accuracy. nP energies are the same NIST values as LINES_5S/6S.
LINES_7S = (
    (12578.950, 0.954, 0.019), (12816.545, 1.352, 0.027),   # 5P1/2, 5P3/2
    (23715.081, 9.189, 0.184), (23792.591, 13.353, 0.267),  # 6P1/2, 6P3/2
    (27835.02, 16.844, 0.337), (27870.11, 23.587, 0.472),   # 7P1/2, 7P3/2
    (29834.94, 1.865, 0.037), (29853.79, 2.833, 0.057),     # 8P1/2, 8P3/2
)
CORE_7S, CORE_7S_SIG = 9.1, 0.5            # Rb+ ionic core (state-independent)
TAIL_7S, TAIL_7S_SIG = 0.3, 0.3           # n>=9 P states (small, far-poled)

_POLES_7S_NM = sorted(1e7 / abs(e - E_7S_CM) for e, _, _ in LINES_7S)

# Hamilton et al. 2023 -- ADOPTED, not recomputed (see block header):
MAGIC_5S5D52_EXP_NM = 776.179              # +-0.005 (experimental)
MAGIC_5S5D52_THEORY_NM = 776.21            # (theoretical)
RME_5P32_5D52 = 1.80                       # +-0.06 a.u. (Hamilton, experimental)


def alpha_7s(lam_nm: float, scale=None, tail=TAIL_7S, core=CORE_7S) -> float:
    """Dynamic scalar polarizability of 7S1/2 (a.u.); lam_nm=0 gives static."""
    return _alpha(LINES_7S, lam_nm, E_7S_CM, tail, core, scale)


def delta_alpha_7s(lam_nm: float) -> float:
    """alpha_7S - alpha_5S (a.u.): the 5S->7S transition differential. Its zero
    crossings are the 5S-7S magic wavelengths = the light-shift sign-flips."""
    return alpha_7s(lam_nm) - alpha_5s(lam_nm)


def _crossings(f, lo, hi, poles, guard=1.5, n=400):
    """All sign changes of f in [lo, hi], searched between the poles."""
    edges = [lo] + sorted(p for p in poles if lo < p < hi) + [hi]
    out = []
    for a, b in zip(edges, edges[1:]):
        aa, bb = a + guard, b - guard
        if bb <= aa:
            continue
        g = np.linspace(aa, bb, n)
        v = [f(x) for x in g]
        for i in range(len(g) - 1):
            if v[i] * v[i + 1] < 0:
                out.append(float(brentq(f, g[i], g[i + 1], xtol=1e-6)))
    return out


def magic_5s7s(lo: float = 700.0, hi: float = 1000.0):
    """5S-7S magic wavelengths (= sign-flips of the 5S->7S light shift) in
    [lo, hi] nm: alpha_7S = alpha_5S crossings. Returns (lambda_nm, alpha_au)."""
    poles = sorted(set(_POLES_7S_NM) |
                   {1e7 / abs(e) for e, _, _ in LINES_5S})
    xs = _crossings(delta_alpha_7s, lo, hi, poles)
    return [(x, float(alpha_5s(x))) for x in xs]
