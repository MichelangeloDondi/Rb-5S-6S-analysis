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
convention (FWHM, angular units, C6 entering as C6/hbar) is the most likely
place for an error, so it is written out in `beta_self_vdw` rather than
buried. The C6 that enters that formula is the DIFFERENCE of the upper- and
lower-state interactions with the perturber, not the upper state's alone. That
was got wrong until 2026-08-05 and is adjudicated in `beta_self_vdw` below and
in docs/notes/vdw_difference_potential_and_4d_channel.md. The primary source
for this whole construction is Lewis, Phys. Rep.
58, 1-71 (1980) (docs/lit/lewis1980.md), section 4.2: the scalar
Anderson/phase-shift cross-section for a -C6/R^6 potential, eq. (4.15)-(4.17),
specialized to n=6 gives exactly the (C6/hbar)^0.4 * v^0.6 powers used below,
and eq. (4.18) is the w = <N*sigma*v> step this module evaluates. Lewis's own
error bound on the Lindholm-Foley approximation (~4%, section 4.3.2) is for a
J=1 excited-state ANGULAR average that our S-S pair does not have (S states
carry no such tensor to average over, so the scalar formula is exact in that
respect); it is quoted here only to note that it is far smaller than the
~18% gap between this module's corrected 7S prediction and Zameroski's
measured rate (see `beta_self_anchored` below), and so cannot explain that
gap either -- the gap is attributed to the dropped core/tail and the mean-
speed approximation, both already named above.

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

# Lindholm-Foley impact prefactor for a -C6/R^6 potential: FULL width at half
# maximum (FWHM) in angular units -- 2x the bare eq.(4.17) HALF-width value
# (2 * 4.04 = 8.08, matching this constant to 0.9%, plausible literature
# rounding). Quoted from the standard pressure-broadening literature, NOT
# derived here -- see the module docstring.
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
    """C6 for the Rb(5S)+Rb(6S) asymptote. No literature value exists.

    This is the pair coefficient, not the broadening input: what enters
    `beta_self_vdw` is this minus `c6_5s5s`.
    """
    return c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM)


def mean_relative_speed(T_K: float) -> float:
    """Mean RELATIVE speed of two Rb atoms (reduced mass m/2), m/s."""
    return math.sqrt(8.0 * KB * T_K / (math.pi * (M_RB87 / 2.0)))


def beta_self_anchored(T_K: float = 403.15, n_cm3: float = 1e12) -> dict:
    """beta_self(6S) anchored on Zameroski's MEASURED 7S rate, using this
    module only for the RATIO of van der Waals coefficients -- of their
    DIFFERENCES against the ground pair, for the reason set out below.

    Why not just call beta_self_vdw for 6S: run against the one state where a
    measurement exists, this module gives beta_self(7S) = 4.40 kHz per
    1e12 cm^-3 where Zameroski measured 5.4 -- 18% low, just past the
    +-10-15% envelope the dropped core/tail and the mean-speed-vs-full-
    Boltzmann-average approximation already predict (see module docstring).
    An earlier version of this module double-applied the HWHM->FWHM
    conversion in `beta_self_vdw` and reported this as "high by 1.67x";
    that was a bug in the code, not a physical discrepancy -- see
    docs/PREREGISTRATION_RESULTS.md Addendum 23. NOT the same thing as
    Lewis 1980's own quoted ~4% Lindholm-Foley error (docs/lit/lewis1980.md):
    that 4% is for a J=1 angular average this S-S pair does not carry.

    Whatever that error is, it is COMMON to 6S and 7S -- same prefactor, same
    law, same units. It cancels in the ratio:

        beta(6S) = beta(7S)_measured * [Delta_C6(6S) / Delta_C6(7S)]^(2/5)

    which uses this module for the part it does well (a ratio of sums over the
    same matrix elements) and takes the absolute scale from an experiment.

    Delta_C6(nS) = C6(5S+nS) - C6(5S+5S), because the impact phase is set by
    the difference of the upper- and lower-state interactions with the
    ground-state perturber (`beta_self_vdw` carries the adjudication and its
    Lewis 1980 sources). The ground-state term is this module's own 4180 a.u.
    rather than the 4691 a.u. literature value, so that both rungs are built
    from the same truncated sum and the truncation partly cancels. Using 4691
    instead moves the answer to 3.36, half a per cent, far inside the envelope.

    Returns ~3.38 kHz per 1e12 cm^-3. Before the difference correction of
    2026-08-05 this read 3.53, a 4.1 per cent shift and inside the +-0.30
    quoted error. Both sit between the raw 5.9 and the ~1 kHz that an older
    n*^7 Rydberg scaling of a MISATTRIBUTED self-shift used to give.
    """
    from .polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM
    c6_5 = c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0)
    c6_6 = c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM)
    c6_7 = c6_coefficient(LINES_5S, 0.0, LINES_7S, E_7S_CM)
    dc6_6, dc6_7 = c6_6 - c6_5, c6_7 - c6_5
    n_per_mtorr = (1e-3 * 133.322) / (KB * T_K) * 1e-6      # cm^-3 per mTorr
    beta7_meas = ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR / (n_per_mtorr / n_cm3)
    err7 = ZAMEROSKI_7S_BROADENING_ERR / (n_per_mtorr / n_cm3)
    scale = (dc6_6 / dc6_7) ** 0.4
    return {"beta6_khz": beta7_meas * scale,
            "beta6_err_khz": err7 * scale,
            "beta7_measured_khz": beta7_meas,
            "beta7_predicted_khz": beta_self_vdw(dc6_7, T_K, n_cm3) / 1e3,
            "dc6_ratio": dc6_6 / dc6_7,
            "c6_ratio": c6_6 / c6_7,
            "prefactor_discrepancy": (beta_self_vdw(dc6_7, T_K, n_cm3) / 1e3) / beta7_meas}


def beta_self_vdw(delta_c6_au: float, T_K: float, n_cm3: float = 1e12,
                  prefactor: float = LINDHOLM_FOLEY_PREFACTOR) -> float:
    """Impact-broadening FWHM (Hz) from a van der Waals C6, at density n_cm3.

    WHICH C6. The argument is the DIFFERENCE of the two levels' interactions
    with the perturber,

        Delta_C6 = C6(upper state + perturber) - C6(lower state + perturber)

    not the upper state's coefficient alone. A referee raised this on
    2026-08-04 and it is adjudicated here, on the module's own primary source.
    Lewis 1980 carries it in three places. His eq. (2.39) gives the impact
    width and shift as w + i*d = <1 - S_ii * S_ff^*>, a product over the UPPER
    and LOWER state S-matrices, which for a central potential is
    exp{-(i/hbar) * integral [V_i(R(t)) - V_f(R(t))] dt}. His eq. (4.13), the
    phase-shift cross-section this function specializes, therefore integrates
    [1 - cos(Phi_i - Phi_f)] and sin(Phi_i - Phi_f), never a single-level
    phase. And section 4.2 says it in words: the sign of the shift
    cross-section depends on the overall sign of "the difference in the
    interactions for the two levels involved".

    Passing the upper state's C6 alone is the correct limit when the lower
    state is a spectator, which is the usual excited-to-ground case in the
    broadening literature and is NOT this one. Here the lower level is a
    ground-state Rb atom facing a ground-state Rb perturber, and
    C6(5S+5S) = 4180 a.u. is 14 per cent of C6(5S+6S) and 5 per cent of
    C6(5S+7S). It does not cancel in the 6S-over-7S anchor ratio either,
    because the two rungs subtract the same term from different-sized
    numbers. See docs/notes/vdw_difference_potential_and_4d_channel.md.

    Written out because the unit conventions are the other failure mode:
      * C6 enters as C6/hbar, i.e. rad/s * m^6, NOT as an energy;
      * the prefactor gives the FULL width at half maximum in ANGULAR units
        (LINDHOLM_FOLEY_PREFACTOR is already 2x the bare eq.(4.17) half-width
        value -- see the constant's comment above);
      * the return divides by 2*pi only, to convert ANGULAR to ordinary Hz.
        A second factor of 2 here would double-count the HWHM->FWHM step
        already folded into the prefactor -- that double-count was the M18
        bug (see docs/PREREGISTRATION_RESULTS.md Addendum 23).
    """
    c6_si = delta_c6_au * HARTREE_J * BOHR_M ** 6    # J m^6
    c6_rate = c6_si / HBAR                            # rad/s m^6
    v = mean_relative_speed(T_K)
    n = n_cm3 * 1e6                                   # m^-3
    fwhm_ang = prefactor * c6_rate ** 0.4 * v ** 0.6 * n
    return fwhm_ang / (2.0 * math.pi)
