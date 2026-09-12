"""Coulomb-approximation radial integrals for Rb ns-n'p and ns-n'd channels,
calibrated on the held 6s-8p pair with the step from the 6s-7p pair as its
spread, every other held element a check on the class (M41).

WHY THIS EXISTS. The 6S dynamic polarizability at the 993 nm drive is a
difference of large terms: the drive sits BETWEEN the 6S-8P resonance at
1030 nm and the 6S-9P resonance at 924 nm, so the 6S-nP terms with n >= 9 are
enhanced three to seven times over their static size, and no held table
carries a 6S-nP element beyond 8P (Safronova & Safronova 2011, Table II, stops
at 6s-6p; the group's portal supplies 7p and 8p). `polarizability.py` carried
everything above 8P as a static tail, which at the drive understates it. Those
elements have to be computed, and a computed element is worth exactly what its
calibration against the held ones says it is.

THE METHOD: Bates-Damgaard (1949). Outside the ionic core the valence electron
sees a Coulomb field, so the radial function is the Whittaker function of the
EFFECTIVE quantum number n* = sqrt(R / (E_ion - E)) read from the measured
term energy:

    P_{n*l}(r) = N W_{n*, l+1/2}(2 r / n*),
    W_{k,m}(z) = exp(-z/2) z^{m+1/2} U(m - k + 1/2, 1 + 2m, z),

normalised numerically on [r_min, inf). The dipole radial integral
R = int P_a r P_b dr gives the reduced matrix element through the angular
factor for s -> p_J, |<ns||d||n'p_J>|^2 = (2J+1)/3 R^2, which reproduces the
1:2 ratio of the two fine-structure components exactly; the 5s-5p radial
integral comes back at 4.4 a0 against the held 5.2, the compact ground state
being outside the approximation's reach (the module's own calibration table
says so, and the outer 6s, 7s and 8s classes are where it is used).

WHAT IT IS GOOD FOR, AND WHAT IT IS NOT. The approximation holds where the
integrand lives outside the core, so it is best for the outer channels and
worst for compact ones and for integrals that cancel. The calibration table
(`calibrate()`) is the instrument: every ns-n'p element the record holds is
recomputed here and the ratio tabulated/computed is reported, so a class of
transitions carries a measured accuracy and a computed element for 6s-9p is
quoted with that class's scatter and not with a hope.

The E2 channel ns-n'd uses the same functions with the r^2 integral, for the
quadrupole polarizability bound the differential-polarizability budget owes.
"""
from __future__ import annotations
from typing import Iterable, Tuple
import numpy as np
from scipy.special import hyperu
from scipy.integrate import quad

from .constants import RYD_RB_CM            # Rydberg constant for Rb (reduced mass), cm^-1
from .cooperative import IONISATION_LIMIT_CM as E_ION_CM   # Rb I ionisation limit above 5S (NIST ASD), one copy
R_MIN = 0.02                    # a0; the Coulomb function is not the true function inside the core


def n_star(e_cm: float) -> float:
    """Effective quantum number of a level at term energy `e_cm` above 5S."""
    return float(np.sqrt(RYD_RB_CM / (E_ION_CM - e_cm)))


def _whittaker(k: float, m: float, z: np.ndarray) -> np.ndarray:
    """W_{k,m}(z). scipy's hyperu drops the function above n* of about 12
    (it returned NaN for 6s-15p on 2026-09-12); mpmath's arbitrary-precision
    whitw takes over wherever hyperu is not finite, which keeps the fast path
    for the low states and the correct one for the tail."""
    scalar = np.ndim(z) == 0
    z = np.atleast_1d(np.asarray(z, float))
    with np.errstate(all="ignore"):
        out = np.exp(-z / 2.0) * z ** (m + 0.5) * hyperu(m - k + 0.5, 1.0 + 2.0 * m, z)
    bad = ~np.isfinite(out)
    if np.any(bad):
        import mpmath
        mpmath.mp.dps = 30
        out = np.array(out, float)
        for i in np.flatnonzero(bad):
            out[i] = float(mpmath.whitw(k, m, z[i]))
    return out[0] if scalar else out


def radial_function(nstar: float, l: int, r: np.ndarray) -> np.ndarray:
    """P(r) = r R(r), Coulomb approximation, unnormalised."""
    return _whittaker(nstar, l + 0.5, 2.0 * np.asarray(r, float) / nstar)


def _norm(nstar: float, l: int) -> float:
    f = lambda r: radial_function(nstar, l, r) ** 2
    rmax = 8.0 * nstar * nstar + 60.0
    val, _ = quad(f, R_MIN, rmax, limit=400)
    return 1.0 / np.sqrt(val)


def radial_integral(e_a_cm: float, l_a: int, e_b_cm: float, l_b: int, power: int = 1) -> float:
    """int P_a r^power P_b dr in atomic units, both functions normalised on [R_MIN, inf)."""
    na, nb = n_star(e_a_cm), n_star(e_b_cm)
    Na, Nb = _norm(na, l_a), _norm(nb, l_b)
    f = lambda r: Na * radial_function(na, l_a, r) * r ** power * Nb * radial_function(nb, l_b, r)
    rmax = 8.0 * max(na, nb) ** 2 + 60.0
    val, _ = quad(f, R_MIN, rmax, limit=600)
    return float(val)


def reduced_e1_s_to_p(e_s_cm: float, e_p_cm: float, j_p: float) -> float:
    """|<ns||d||n'p_J>| in a.u.: sqrt((2J+1)/3) times the radial integral."""
    return float(np.sqrt((2.0 * j_p + 1.0) / 3.0) * abs(radial_integral(e_s_cm, 0, e_p_cm, 1)))


#: Every ns-n'p reduced element the record holds with a quoted uncertainty,
#: as (label, E_s, E_p, J_p, value, sigma, source). Energies are NIST term
#: values above 5S; the 9P-12P energies are Leonard 2015 Table II as carried in
#: polarizability.LINES_5S.
HELD: Tuple[Tuple, ...] = (
    ("5s-5p1/2", 0.0, 12578.950, 0.5, 4.231, 0.003, "Volz&Schmoranzer 1996"),
    ("5s-5p3/2", 0.0, 12816.545, 1.5, 5.978, 0.005, "Volz&Schmoranzer 1996"),
    ("5s-6p1/2", 0.0, 23715.081, 0.5, 0.3235, 0.0009, "Herold 2012"),
    ("5s-6p3/2", 0.0, 23792.591, 1.5, 0.5230, 0.0008, "Herold 2012"),
    ("5s-7p1/2", 0.0, 27835.02, 0.5, 0.1154, 0.0081, "S&S portal"),
    ("5s-7p3/2", 0.0, 27870.11, 1.5, 0.202, 0.011, "S&S portal"),
    ("5s-8p1/2", 0.0, 29834.94, 0.5, 0.0598, 0.0057, "S&S portal"),
    ("5s-8p3/2", 0.0, 29853.79, 1.5, 0.1110, 0.0074, "S&S portal"),
    ("5s-9p1/2", 0.0, 30958.91, 0.5, 0.037, 0.003, "Leonard 2015"),
    ("5s-9p3/2", 0.0, 30970.19, 1.5, 0.073, 0.005, "Leonard 2015"),
    ("5s-10p1/2", 0.0, 31653.85, 0.5, 0.026, 0.002, "Leonard 2015"),
    ("5s-10p3/2", 0.0, 31661.16, 1.5, 0.053, 0.004, "Leonard 2015"),
    ("5s-11p1/2", 0.0, 32113.55, 0.5, 0.020, 0.001, "Leonard 2015"),
    ("5s-11p3/2", 0.0, 32118.52, 1.5, 0.040, 0.003, "Leonard 2015"),
    ("5s-12p1/2", 0.0, 32433.50, 0.5, 0.016, 0.001, "Leonard 2015"),
    ("5s-12p3/2", 0.0, 32437.04, 1.5, 0.033, 0.002, "Leonard 2015"),
    ("6s-5p1/2", 20132.510, 12578.950, 0.5, 4.145, 0.010, "S&S 2011 Table II"),
    ("6s-5p3/2", 20132.510, 12816.545, 1.5, 6.047, 0.013, "S&S 2011 Table II"),
    ("6s-6p1/2", 20132.510, 23715.081, 0.5, 9.721, 0.024, "S&S 2011 Table II"),
    ("6s-6p3/2", 20132.510, 23792.591, 1.5, 13.647, 0.034, "S&S 2011 Table II"),
    ("6s-7p1/2", 20132.510, 27835.02, 0.5, 0.992, 0.018, "S&S portal"),
    ("6s-7p3/2", 20132.510, 27870.11, 1.5, 1.540, 0.025, "S&S portal"),
    ("6s-8p1/2", 20132.510, 29834.94, 0.5, 0.3936, 0.0054, "S&S portal"),
    ("6s-8p3/2", 20132.510, 29853.79, 1.5, 0.6285, 0.0096, "S&S portal"),
    ("7s-5p1/2", 26311.437, 12578.950, 0.5, 0.953, 0.005, "S&S 2011 Table II"),
    ("7s-5p3/2", 26311.437, 12816.545, 1.5, 1.350, 0.008, "S&S 2011 Table II"),
    ("7s-6p1/2", 26311.437, 23715.081, 0.5, 9.226, 0.017, "S&S 2011 Table II"),
    ("7s-6p3/2", 26311.437, 23792.591, 1.5, 13.396, 0.021, "S&S 2011 Table II"),
    ("7s-7p1/2", 26311.437, 27835.02, 0.5, 16.888, 0.040, "S&S 2011 Table II"),
    ("7s-7p3/2", 26311.437, 27870.11, 1.5, 23.625, 0.056, "S&S 2011 Table II"),
    ("7s-8p1/2", 26311.437, 29834.94, 0.5, 1.858, 0.018, "S&S 2011 Table II"),
    ("7s-8p3/2", 26311.437, 29853.79, 1.5, 2.819, 0.025, "S&S 2011 Table II"),
    ("8s-5p1/2", 29046.816, 12578.950, 0.5, 0.502, 0.003, "S&S 2011 Table II"),
    ("8s-5p3/2", 29046.816, 12816.545, 1.5, 0.708, 0.005, "S&S 2011 Table II"),
    ("8s-6p1/2", 29046.816, 23715.081, 0.5, 1.851, 0.011, "S&S 2011 Table II"),
    ("8s-6p3/2", 29046.816, 23792.591, 1.5, 2.597, 0.016, "S&S 2011 Table II"),
)


def calibrate(rows: Iterable[Tuple] = HELD):
    """Tabulated over computed for every held element. Returns a list of
    (label, tabulated, sigma, computed, ratio, source)."""
    out = []
    for label, es, ep, jp, val, sig, src in rows:
        comp = reduced_e1_s_to_p(es, ep, jp)
        out.append((label, val, sig, comp, val / comp if comp else float("nan"), src))
    return out


if __name__ == "__main__":
    print(f"{'channel':10s} {'held':>9s} {'computed':>9s} {'ratio':>7s}  source")
    for label, val, sig, comp, ratio, src in calibrate():
        print(f"{label:10s} {val:9.4f} {comp:9.4f} {ratio:7.3f}  {src}")
