"""
M18 -- van der Waals C6 for the 5S+6S asymptote, and the beta_self it implies.

The archive bounds beta_self(6S) but the literature has no value to compare it
against: self-broadening coefficients are published for 5D and 7S (Zameroski
2014) and nothing for 6S, confirmed by four independent search framings
(LITERATURE.md 5.2). Until now the "expected ~kHz per 1e12 cm^-3" scale was
imported by analogy from the 7S measurement.

It does not have to be borrowed. The Casimir-Polder relation

    C6^AB = (3/pi) integral_0^inf alpha^A(i w) alpha^B(i w) dw

gives the van der Waals coefficient from dynamic polarizabilities at IMAGINARY
frequency, and M16 already carries a converged sum-over-states machine for
alpha_5S and alpha_6S at real frequency. The continuation is one sign:
alpha(i w) replaces (dE^2 - w^2) with (dE^2 + w^2). The same matrix elements
that produced Delta_alpha(993) therefore produce a COMPUTED expected
beta_self, with the same provenance.

Two things this module deliberately does NOT do.

Core and tail are dropped. In M16 they are static constants fitted to
reproduce measured static polarizabilities; a constant cannot enter an
imaginary-frequency integral, because it never falls off and the integral
diverges linearly with the cutoff (observed: C6 growing 4948 -> 5840 as the
cutoff went 4 -> 16 a.u. before they were removed). Including them properly
needs a frequency-dependent core polarizability, which this repo does not have.
The cost is visible in the validation below.

And the broadening prefactor is quoted, not derived. The Lindholm-Foley impact
result for a -C6/R^6 potential is used as stated in the literature; its
convention (HWHM, angular units, C6 entering as C6/hbar) is the most likely
place for an error, so it is written out in `beta_self_vdw` rather than
buried.

VALIDATION, which is the point of doing the ground state first: the same
machinery gives C6(5S+5S) = 4180 a.u. against a literature Rb2 value of
~4691 -- 11% low, in the direction and roughly the size the dropped core
predicts (valence-only alpha_5S(0) = 309.5 against the measured 318.8, and C6
goes as alpha^2). Treat every number here as ENVELOPE at the ~10-15% level.
"""

from __future__ import annotations

import math

import numpy as np

from ._compat import trapezoid
from .polarizability import LINES_5S, LINES_6S, E_6S_CM, CM_PER_HARTREE

HARTREE_J = 4.3597447e-18
BOHR_M = 5.29177211e-11
HBAR = 1.054571817e-34
KB = 1.380649e-23
M_RB87 = 86.909180527 * 1.66053907e-27

# Literature Rb2 ground-state C6, for the validation path only.
C6_RB2_GROUND_LIT_AU = 4691.0

# Zameroski 2014 (J. Phys. B 47, 225205), section 2.5: the MEASURED self-
# broadening rate of the 85Rb 5S1/2(F=2) -> 7S1/2(F=2) two-photon line,
# 129 +- 11 kHz/mTorr. Their 7S self-SHIFT could not be extracted from the data
# -- the -17.8 kHz/mTorr sometimes attributed to them is Morzynski 2013's, on
# the laser axis. This is the only measured self-broadening rate for an nS state
# in Rb, and so the only external check this module has.
ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR = 129.0
ZAMEROSKI_7S_BROADENING_ERR = 11.0

# Lindholm-Foley impact prefactor for a -C6/R^6 potential: HWHM in angular
# units. Quoted from the standard pressure-broadening literature, NOT derived
# here -- see the module docstring.
LINDHOLM_FOLEY_PREFACTOR = 8.16


def alpha_imaginary(lines, w_au: float, upper_cm: float = 0.0,
                    prefactor: float = 1.0 / 6.0) -> float:
    """Valence scalar polarizability at IMAGINARY frequency i*w_au (a.u.).

    The real-frequency sum has (dE^2 - w^2); on the imaginary axis that becomes
    (dE^2 + w^2), which is why alpha(i w) is smooth and positive-definite for a
    ground state and has no poles. Downward transitions (dE < 0, the 6S->5P
    cascade) contribute negatively, exactly as they do at real frequency.
    """
    s = 0.0
    for e, d, _ in lines:
        de = (e - upper_cm) / CM_PER_HARTREE
        s += 2.0 * de * d * d / (de * de + w_au * w_au)
    return s * prefactor


def c6_coefficient(lines_a, upper_a: float, lines_b, upper_b: float,
                   w_max: float = 25.0, n: int = 60000) -> float:
    """Casimir-Polder C6 (a.u.) between two states, from their alpha(i w).

    w_max = 25 a.u. is well past convergence: the integrand falls as 1/w^4 once
    w exceeds the largest transition energy, and the result is stable to the
    printed digits from w_max = 2 upward (checked in tests).
    """
    w = np.linspace(1e-8, w_max, n)
    fa = np.array([alpha_imaginary(lines_a, x, upper_a) for x in w])
    fb = np.array([alpha_imaginary(lines_b, x, upper_b) for x in w])
    return float(3.0 / math.pi * trapezoid(fa * fb, w))


def c6_5s5s() -> float:
    """Ground-state Rb2 C6 -- the validation number, not a result."""
    return c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0)


def c6_5s6s() -> float:
    """C6 for the Rb(5S)+Rb(6S) asymptote. No literature value exists."""
    return c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM)


def mean_relative_speed(T_K: float) -> float:
    """Mean RELATIVE speed of two Rb atoms (reduced mass m/2), m/s."""
    return math.sqrt(8.0 * KB * T_K / (math.pi * (M_RB87 / 2.0)))


def beta_self_anchored(T_K: float = 403.15, n_cm3: float = 1e12) -> dict:
    """beta_self(6S) anchored on Zameroski's MEASURED 7S rate, using this
    module only for the RATIO of C6 coefficients.

    Why not just call beta_self_vdw for 6S: it over-predicts. Run against the
    one state where a measurement exists, this module gives beta_self(7S) =
    9.0 kHz per 1e12 cm^-3 where Zameroski measured 5.4 -- high by 1.67x, well
    outside the +-10-15% the sum-over-states truncation can explain. The module
    docstring already names the suspect: the Lindholm-Foley prefactor is quoted
    from the pressure-broadening literature, not derived here, and its
    convention (HWHM vs FWHM, angular vs ordinary units) is where a factor of
    that size lives.

    Whatever that error is, it is COMMON to 6S and 7S -- same prefactor, same
    law, same units. It cancels in the ratio:

        beta(6S) = beta(7S)_measured * [C6(6S) / C6(7S)]^(2/5)

    which uses this module for the part it does well (a ratio of two sums over
    the same matrix elements) and takes the absolute scale from an experiment.
    Returns ~3.5 kHz per 1e12 cm^-3, between the raw 5.9 and the ~1 kHz that an
    older n*^7 Rydberg scaling of a MISATTRIBUTED self-shift used to give.
    """
    from .polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM
    c6_6 = c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM)
    c6_7 = c6_coefficient(LINES_5S, 0.0, LINES_7S, E_7S_CM)
    n_per_mtorr = (1e-3 * 133.322) / (KB * T_K) * 1e-6      # cm^-3 per mTorr
    beta7_meas = ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR / (n_per_mtorr / n_cm3)
    err7 = ZAMEROSKI_7S_BROADENING_ERR / (n_per_mtorr / n_cm3)
    scale = (c6_6 / c6_7) ** 0.4
    return {"beta6_khz": beta7_meas * scale,
            "beta6_err_khz": err7 * scale,
            "beta7_measured_khz": beta7_meas,
            "beta7_predicted_khz": beta_self_vdw(c6_7, T_K, n_cm3) / 1e3,
            "c6_ratio": c6_6 / c6_7,
            "prefactor_discrepancy": (beta_self_vdw(c6_7, T_K, n_cm3) / 1e3) / beta7_meas}


def beta_self_vdw(c6_au: float, T_K: float, n_cm3: float = 1e12,
                  prefactor: float = LINDHOLM_FOLEY_PREFACTOR) -> float:
    """Impact-broadening FWHM (Hz) from a van der Waals C6, at density n_cm3.

    Written out because the unit conventions are the failure mode:
      * C6 enters as C6/hbar, i.e. rad/s * m^6, NOT as an energy;
      * the prefactor gives the HALF width at half maximum in ANGULAR units;
      * the return is converted to a FULL width in ordinary Hz.
    """
    c6_si = c6_au * HARTREE_J * BOHR_M ** 6          # J m^6
    c6_rate = c6_si / HBAR                            # rad/s m^6
    v = mean_relative_speed(T_K)
    n = n_cm3 * 1e6                                   # m^-3
    hwhm_ang = prefactor * c6_rate ** 0.4 * v ** 0.6 * n
    return hwhm_ang / (2.0 * math.pi) * 2.0
