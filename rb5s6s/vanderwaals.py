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
gap this module carried until 2026-09-14 between its 7S prediction and
Zameroski's measured rate; that gap was the integral's sign error on the
downward lines (next paragraph), and with the direct sum the 7S prediction
sits 4 per cent above the measurement, inside its bar.

THE INTEGRAL IS EXACT ONLY FOR UPWARD TRANSITIONS (found 2026-09-14, the day the
owner asked whether this coefficient is trustable). The Casimir-Polder identity
rests on 1/(a+b) = (2/pi) int ab/((a^2+w^2)(b^2+w^2)) dw, which holds for a, b > 0.
A 6S or 7S atom has DOWNWARD transitions (6S -> 5P; 7S -> 5P, 6P), whose energy
denominators are negative, and for a < 0 < b the integral returns -1/(|a|+b)
where the second-order sum has 1/(b-|a|). The two differ in sign and size, so
the integral undercounted C6(5S+6S) by a factor 1.87 and C6(5S+7S) by 1.94. The
pair coefficients now come from `c6_direct`, the second-order sum with signed
denominators, which is exact for a non-degenerate pair and equals the integral
to eight digits on the ground pair, where every transition is upward. The
integral stays as the ground-state validation path. The 18 per cent gap the
docstring below used to attribute to the dropped core and tail was this sign
error: with the direct sum the first-principles 7S rate sits 4 per cent ABOVE
Zameroski's measurement, inside its 10.08 per cent bar (his Table 3 total,
not the 8.5 per cent this line read until 2026-09-18). The anchored 6S value
barely moves (3.38 to 3.40 kHz per 1e12 cm^-3), because the error is common
to both rungs and cancels in the ratio, which is what the anchor was for.

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
from . import constants as _C

HARTREE_J = _C.HARTREE_J  # the same, and it differed from cooperative's
                          # copy in its eighth digit
BOHR_M = _C.A0_M  # constants.py, since 2026-09-11: this was a fifth
                  # copy of the Bohr radius, and the promotion that
                  # named four missed it, which is repairing the name
                  # last found missing rather than the population
HBAR = _C.HBAR_JS  # one home for the trio, constants.py, since 2026-09-11
KB = _C.K_B_J_PER_K   # one home: constants.py (2026-09-12)
M_RB87 = _C.M_RB87_KG   # one home: constants.py (2026-09-13)

# Literature Rb2 ground-state C6, for the validation path only. SOURCED
# 2026-08-26, having stood uncited while the module's other SOURCED values
# carry their journal and section.
#
# WHOSE NUMBER THIS IS, corrected 2026-09-18 after the thesis session read the
# attribution and this side audited it against the held PDF. 4691 is a
# CALCULATION: Derevianko, Johnson, Safronova and Babb, Phys. Rev. Lett. 82,
# 3589 (1999), whose own words are "Our result C6 = 4691(23) is in excellent
# agreement with this experiment" -- journal page 3592, the letter's last, read
# from PDF_papers/derevianko1999.pdf. (This side first wrote that quote as "Our
# value" on "page 3", both wrong, from memory rather than from the page; the
# rule that a value read from a two-column PDF is read twice covers the words
# around it too.) The block used to open on Stewart, which read
# as though 4691 were his measurement; it is the value he TABULATES beside his
# own. Stewart, Shen, Booth and Madison, Phys. Rev. A 106, 052812 (2022),
# arXiv:2208.12805, measure 4688(198)(95) E_h a_0^6 from atom-trap loss-rate
# diffractive-collision universality, which is an independent EXPERIMENTAL check
# that 4691 sits well inside -- and at 4.7 per cent it is the least precise
# determination in the literature, so it is a check and not an anchor.
#
# OPEN: van Kempen et al., Phys. Rev. Lett. 88, 093201 (2002) give 4703(9) from a
# molecular fit, twenty-two times tighter, which would make this module's own
# truncated sum decisively low rather than in tension. That determination is not
# held here and is queued as `c6-anchor-audit`; nothing moves on it until its PDF
# is read, because the errors in this class have been in the READING.
C6_RB2_GROUND_LIT_AU = 4691.0

# Zameroski 2014 (J. Phys. B 47, 225205), section 2.5: the MEASURED self-
# broadening rate of the 85Rb 5S1/2(F=2) -> 7S1/2(F=2) two-photon line,
# 129 +- 11 kHz/mTorr. Their 7S self-SHIFT could not be extracted from the data
# -- the -17.8 kHz/mTorr sometimes attributed to them is Morzynski 2013's, on
# the laser axis. This is the only measured self-broadening rate for an nS state
# in Rb, and so the only independent validation this module has.
ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR = 129.0
# THE SOURCE PRINTS TWO BARS AND THE LARGER IS THE TOTAL. Section 2.5 quotes
# 129 +- 11; TABLE 3 quotes 129 +- 13; Table 4's 107 +- 11 is 0.83 x 13. The
# arithmetic closes on the paper's own recipe -- sqrt(11^2 + (0.05 x 129)^2 +
# (0.01 x 129)^2) = 12.8, printed 13 -- so the +-11 is the LINEAR-FIT INTERVAL
# WITHOUT the density term and the +-13 is the total WITH it. This module
# carried 11 and then, on 2026-09-15, removed the 5 per cent density term from
# its own budget as a double count: it was not double counted, it was the
# difference between the two bars, and removing it narrowed a bar that was
# already right. Both readings are retracted and the source's TOTAL is adopted.
ZAMEROSKI_7S_BROADENING_ERR = 13.0

# THE RATE IS A SLOPE OVER A TEMPERATURE RANGE, NOT A RATE AT A TEMPERATURE.
# Retracted 2026-09-15, the same day it was written, and verified against the
# held PDF: figure 7's caption, the plot the 129
# kHz/mTorr slope is fitted from, reads "The temperature of VC Exp ranged from
# 353 K to 438 K". The 393 K this module carried for one afternoon is Table 4's
# note, which gives the self-broadening contribution for a different
# experiment's linewidth budget at that experiment's temperature -- a number
# about a different quantity that happened to agree with the reading.
#
# A slope in pressure across 85 K has no single temperature. Its effective one
# is set by where the fit's leverage sits, and the Rb pressure runs 0.056 mTorr
# at 353 K to 9.3 at 438, so the hot end carries it: weighting by pressure gives
# 428.5 K, equal weight in T gives 420.4, and weighting by 1/width^2 gives
# 368.3. The paper weights by the standard deviation of its own linewidths,
# which it does not print, so the effective temperature is UNKNOWN INSIDE THAT
# SPAN and the span is a budget row rather than a choice. Adopted: the centre of
# the beta it implies, with the span carried at 3.2 per cent.
ZAMEROSKI_7S_FIT_T_RANGE_K = (353.0, 438.0)


def zameroski_effective_T(weighting: str = "unit", n: int = 601) -> float:
    """The effective temperature of a SLOPE fitted over `ZAMEROSKI_7S_FIT_T_RANGE_K`.

    NOT A WEIGHTED MEAN, and that distinction is the whole function. A point's
    influence on a fitted SLOPE is `w * (P - Pbar)`, not `w`: the regression
    leverage. Because the Rb vapour pressure is exponential in temperature,
    `Pbar` sits near the cold end and the hot points carry the slope whatever
    their weight. The constant this replaced, 397 K, came from a weighted MEAN
    of T and is not reachable by any leverage weighting -- the secondary physics
    leverage family gives 402 to 429 K, against a mean family of 368 to 428. That was the third reading of this
    temperature in one day and the first computed from the estimator the paper
    actually used.

    `weighting` names what multiplies the leverage: "unit" (equal weight in T),
    "inv_width2" (1/nu^2, the paper's own family), "inv_p2" (the extreme that
    pushes the answer lowest). The span across them is a budget row.
    """
    import numpy as _np
    T = _np.linspace(*ZAMEROSKI_7S_FIT_T_RANGE_K, n)
    P = 10.0 ** (7.193 - 4040.0 / T)                 # torr, Alcock liquid branch
    w = {"unit": _np.ones_like(T),
         "inv_width2": (P * T ** -0.7) ** -2.0,
         "inv_p2": P ** -2.0}[weighting]
    lev = w * (P - _np.average(P, weights=w))        # the regression leverage
    lev = _np.abs(lev)
    return float(_np.average(T, weights=lev * P))


#: Adopted: the leverage-weighted effective temperature under equal weight in T.
ZAMEROSKI_7S_EFF_T_K = zameroski_effective_T("unit")

# AND HIS BAR IS NOT A 1-SIGMA BAR, which is why it is carried as quoted and
# never unpacked: "The largest sources contributing to the uncertainty in the
# measured rates are the linear fit error (95% confidence intervals) ... and
# the calibration uncertainty of the 2 Torr pressure transducer which is
# estimated at 1%. ... For the self-broadening and shift rates, a 5%
# uncertainty is used for the temperature dependent vapor pressure (density)."
# So the 5 per cent density term is ALREADY INSIDE the +-11 and a budget that
# adds it again double-counts it, which docs/wiki/self-broadening.md did until
# 2026-09-15. Carrying +-11 whole is conservative, since part of it is a 95 per
# cent interval. His rates are on the ATOMIC axis (nu = 2 nu_L), stated in the
# same paragraph, which is the axis this module wants.

# Lindholm-Foley impact prefactor for a -C6/R^6 potential: FULL width at half
# maximum (FWHM) in angular units -- 2x the bare eq.(4.17) HALF-width value
# (2 * 4.04 = 8.08, matching this constant to 0.9%, plausible literature
# rounding). Quoted from the standard pressure-broadening literature, NOT
# derived here -- see the module docstring.
LINDHOLM_FOLEY_PREFACTOR_QUOTED = 8.16   # the literature rounding this module carried until 2026-09-14


def impact_prefactors() -> dict:
    """The Lindholm-Foley prefactors for a -C6/R^6 potential, DERIVED.

    Straight-line path, impact parameter b, relative speed v: the phase
    accumulated in one collision is eta(b) = (3 pi / 8) C6 / (hbar v b^5). The
    width and shift cross-sections are

        sigma_w = 2 pi int_0^inf [1 - cos eta(b)] b db,
        sigma_d = 2 pi int_0^inf  sin eta(b)      b db,

    and with t = eta the integrals close on the Gamma function:
    int_0^inf (1 - cos t) t^(-7/5) dt = -Gamma(-2/5) cos(pi/5) and
    int_0^inf  sin t      t^(-7/5) dt = -Gamma(-2/5) sin(pi/5), each times 1/5
    from the substitution. So

        HWHM = n v sigma_w = 4.0414 n (C6/hbar)^(2/5) v^(3/5),
        FWHM = 8.0828 ...,   shift / HWHM = tan(pi/5) = 0.7265.

    The quoted 8.16 was 1.0 per cent high. Returns the three numbers.
    """
    g = -math.gamma(-0.4)
    i_c = g * math.cos(0.2 * math.pi) / 5.0
    i_s = g * math.sin(0.2 * math.pi) / 5.0
    a = (3.0 * math.pi / 8.0) ** 0.4
    hwhm = 2.0 * math.pi * i_c * a
    return {"hwhm": hwhm, "fwhm": 2.0 * hwhm, "shift_over_hwhm": i_s / i_c}


LINDHOLM_FOLEY_PREFACTOR = impact_prefactors()["fwhm"]   # 8.0828, derived above


def speed_average_factor(p: float = 0.6) -> float:
    """<v^p> over the Maxwell distribution of the RELATIVE speed, divided by
    vbar^p with vbar the mean relative speed: the impact width goes as v^(3/5),
    and averaging the power of the speed is not the power of the average.
    <v^p> = (2kT/mu)^(p/2) 2 Gamma((p+3)/2) / sqrt(pi); vbar = sqrt(8kT/(pi mu)).
    At p = 3/5 the factor is 0.9775, so the mean-speed form is 2.3 per cent high.
    """
    return 2.0 * math.gamma((p + 3.0) / 2.0) / math.sqrt(math.pi) / (4.0 / math.pi) ** (p / 2.0)


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


def c6_direct(lines_a, upper_a: float, lines_b, upper_b: float) -> float:
    """C6 (a.u.) as the second-order sum with SIGNED denominators,

        C6 = (1/6) sum_k sum_l d_k^2 d_l^2 / (Delta_k + Delta_l),

    Delta the transition energy from the state (negative for a downward
    line), d the reduced E1 matrix element, 1/6 the scalar J = 1/2 angular
    factor (the same 1/6 as `alpha_imaginary`'s prefactor squared times the
    3/pi of the integral, which is how the two agree when every Delta > 0).
    The direct term of the pair; the imaginary-frequency integral is its special
    case for a ground-state pair. The exchange term of the same order, which
    couples |6S,5S> to |5S,6S> through |nP,n'P>, is `c6_exchange` and splits
    the pair potential into C6 (1 +- f) branches, f 0.35 to 0.45 for 6S.
    """
    s = 0.0
    for ea, da, _ in lines_a:
        d_a = (ea - upper_a) / CM_PER_HARTREE
        for eb, db, _ in lines_b:
            d_b = (eb - upper_b) / CM_PER_HARTREE
            s += da * da * db * db / (d_a + d_b)
    return s / 6.0


def _np_groups(lines_g, lines_x):
    """The nP levels both tables reach, matched by energy and grouped by n (a fine-
    structure pair lies within 300 cm^-1); returns (g, x, groups)."""
    g = {round(e, 2): d for e, d, _ in lines_g}
    x = {round(e, 2): d for e, d, _ in lines_x}
    groups: list = []
    for e in sorted(set(g) & set(x)):
        if groups and e - groups[-1][-1] < 300.0:
            groups[-1].append(e)
        else:
            groups.append([e])
    return g, x, groups


def exchange_signs(lines_g, lines_x, e_x: float) -> dict:
    """The relative signs of the products d(g,k) d(x,k) over the nP legs, DERIVED
    from the off-diagonal Thomas-Reiche-Kuhn rule (A253, the W1l round):
    for orthogonal g and x,

        sum_k (Delta_k(g) + Delta_k(x)) d(g,k) d(x,k) = 0,

    which the tabulated magnitudes constrain UNEVENLY across the legs, and the
    docstring that stood here until 2026-09-15 -- "satisfy for exactly one sign
    pattern up to the truncation tail" -- is RETRACTED, all eight patterns
    replayed and the truncation tail scaled from the tables' own fall-off.

    WHAT THE RULE ACTUALLY FIXES. The per-group terms for 6S, all positive, are
    5P 1.3078, 6P 1.2837, 7P 0.0690, 8P 0.0168, so the residual is dominated by
    the two big legs: every 6P-POSITIVE pattern leaves 2.51 to 2.68 against 0.028
    to 0.110 for the 6P-negative ones. **The 6P sign is fixed, at about fifty
    tail widths. The 7P and 8P signs are not.** The 9P-to-12P tail, scaled from
    the 5s table with the 6s leg going as n*^-1.5 to n*^-3, is 0.013 to 0.020
    before the continuum, so a tail of 0.02 to 0.05 -- which covers the 8P term
    (0.017) outright and the gap between the two best patterns (0.034), and
    leaves the 7P term (0.069) at one and a half to three tail widths. Two
    patterns close inside the tail, not one.

    WHAT MOVES ACROSS THE CLOSING PATTERNS, so that a caller knows what is
    licensed: `c6_exchange` 17367 to 17510 a.u., the fraction 0.3481 to 0.3516,
    the anchored beta 3.3479 to 3.3491 and the first-principles 3.4895 to 3.4907
    at the retired conversion. So the published three figures stand and a
    five-figure exchange coefficient carries three digits nothing licenses. On
    the 7S rung two patterns are degenerate outright, differing by the 5P sign
    relative to the block, and the fraction reads -0.045 or -0.039 with the
    branch factor 0.99976 or 0.99981: the anchor is untouched and "4.5 per cent
    on the 7S rung" is one of two readings.

    The 5P sign is fixed positive, every pattern over the other legs is tried,
    and the residual is gauged against the diagonal f-sum of the ground state
    on the same tables and in the SAME normalisation as the residual, which is
    what makes the two comparable. Returns the signs per group, the residual of
    the chosen pattern, the all-positive residual and the gauge."""
    import itertools
    g, x, groups = _np_groups(lines_g, lines_x)
    def resid(signs):
        return abs(sum(s * (e / CM_PER_HARTREE + (e - e_x) / CM_PER_HARTREE) * g[e] * x[e]
                       for s, grp in zip(signs, groups) for e in grp))
    best = min(((resid((1,) + p), (1,) + p) for p in itertools.product((1, -1), repeat=len(groups) - 1)), key=lambda t: t[0])
    gauge = sum((e / CM_PER_HARTREE) * d * d for e, d, _ in lines_g) / 3.0
    return {"signs": best[1], "groups": [round(grp[0]) for grp in groups], "residual": best[0],
            "residual_all_positive": resid((1,) * len(groups)), "gauge_f_sum": gauge}


def c6_exchange(lines_g, lines_x, e_x: float, sign_6p=None) -> float:
    """The EXCHANGE coefficient (a.u.) of a homonuclear pair with one atom excited:
    the second-order amplitude that carries the excitation from atom A to atom B
    through |nP, n'P>, which splits the pair potential into C6 (1 +- f) branches,

        C6_exch = (1/6) sum_k sum_l [d(g,k) d(x,k)] [d(g,l) d(x,l)] / (Delta_k(x) + Delta_l(g)),

    k and l over the nP levels both tables reach (matched by energy), the same
    angular factor as `c6_direct` because both atoms keep their spin. The reduced
    matrix elements are tabulated as magnitudes; the relative signs of the legs are
    DERIVED by `exchange_signs` from the off-diagonal sum rule (A253: opposed on 6P
    and 7P, parallel on 8P for 6S, so the fraction is 0.35 of Delta C6, and the
    older bracket 0.35 to 0.45 had no physical upper end). `sign_6p` is kept for the
    plant only: +1 or -1 flips every leg above 5P together, which is what the W1k
    bracket did and what the sum rule refutes."""
    g, x, groups = _np_groups(lines_g, lines_x)
    if sign_6p is None:
        signs = exchange_signs(lines_g, lines_x, e_x)["signs"]
    else:
        signs = (1.0,) + (float(sign_6p),) * (len(groups) - 1)
    sg = {e: s for s, grp in zip(signs, groups) for e in grp}
    common = sorted(sg)
    s = 0.0
    for ek in common:
        pk = sg[ek] * g[ek] * x[ek]
        d_k = (ek - e_x) / CM_PER_HARTREE
        for el in common:
            pl = sg[el] * g[el] * x[el]
            s += pk * pl / (d_k + el / CM_PER_HARTREE)
    return s / 6.0


def branch_average(f: float) -> float:
    """The width factor of a pair potential split into C6 (1 +- f) branches sampled
    with equal weight: the impact width goes as C6^(2/5), so the factor is
    ((1+f)^(2/5) + (1-f)^(2/5)) / 2, which is 0.974 at f = 0.45 and 0.985 at 0.35."""
    return 0.5 * ((1.0 + f) ** 0.4 + (1.0 - f) ** 0.4)


def c6_5s5s() -> float:
    """Ground-state Rb2 C6 -- the validation number, not a result."""
    return c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0)


def c6_5s6s() -> float:
    """C6 for the Rb(5S)+Rb(6S) asymptote. No literature value exists.

    This is the pair coefficient, not the broadening input: what enters
    `beta_self_vdw` is this minus `c6_5s5s`.
    """
    return c6_direct(LINES_5S, 0.0, LINES_6S, E_6S_CM)


def c6_5s7s() -> float:
    """C6 for the Rb(5S)+Rb(7S) asymptote, the anchor rung's pair coefficient."""
    from .polarizability import LINES_7S, E_7S_CM
    return c6_direct(LINES_5S, 0.0, LINES_7S, E_7S_CM)


def mean_relative_speed(T_K: float) -> float:
    """Mean RELATIVE speed of two Rb atoms (reduced mass m/2), m/s."""
    return math.sqrt(8.0 * KB * T_K / (math.pi * (M_RB87 / 2.0)))


def beta_self_anchored(T_K: float = 403.15, n_cm3: float = 1e12) -> dict:
    """beta_self(6S) anchored on Zameroski's MEASURED 7S rate, using this
    module only for the RATIO of van der Waals coefficients -- of their
    DIFFERENCES against the ground pair, for the reason set out below.

    Why anchor at all when beta_self_vdw runs on 6S directly: the absolute
    recipe depends on the matrix-element tables' completeness and on the
    dropped core, and the anchor takes its scale from an experiment. Run
    against the one state where a measurement exists, the recipe now gives
    beta_self(7S) = 5.61 kHz per 1e12 cm^-3 where Zameroski measured 5.39,
    4 per cent high and inside his bar (it read 4.40, 18 per cent low, while
    the pair coefficients came from the integral: A250). An earlier version
    double-applied the HWHM->FWHM conversion in `beta_self_vdw` and reported
    "high by 1.67x"; that was a bug in the code, not a physical discrepancy
    (docs/PREREGISTRATION_RESULTS.md Addendum 23). NOT the same thing as
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

    Returns ~3.35 kHz per 1e12 cm^-3 with the exchange branches carried at the
    sum-rule signs (3.33 with the W1l bracket averaged; 3.40 without them; 3.38 with the integral's pair coefficients, 2026-08-05 to
    2026-09-14; 3.53 before the difference correction of 2026-08-05). The quoted error is Zameroski's alone; the
    error budget of the recipe itself is in docs/wiki/self-broadening.md. Both sit between the raw 5.9 and the ~1 kHz that an older
    n*^7 Rydberg scaling of a MISATTRIBUTED self-shift used to give.
    """
    from .polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM
    c6_5 = c6_direct(LINES_5S, 0.0, LINES_5S, 0.0)
    c6_6 = c6_direct(LINES_5S, 0.0, LINES_6S, E_6S_CM)
    c6_7 = c6_direct(LINES_5S, 0.0, LINES_7S, E_7S_CM)
    dc6_6, dc6_7 = c6_6 - c6_5, c6_7 - c6_5
    # THE EXCHANGE BRANCHES (W1l): each rung's width carries the branch average of its
    # own split, bracketed over the untabulated sign of the 6P products; the anchor
    # carries the ratio of the two factors and the first-principles value the 6S one.
    # THE SIGNS ARE DERIVED (A253), so each rung has one exchange fraction and one factor
    ex6 = [c6_exchange(LINES_5S, LINES_6S, E_6S_CM) / dc6_6]
    ex7 = [c6_exchange(LINES_5S, LINES_7S, E_7S_CM) / dc6_7]
    br6 = [branch_average(abs(f)) for f in ex6]
    br7 = [branch_average(abs(f)) for f in ex7]
    branch_ratio = br6[0] / br7[0]
    # THE MEASUREMENT IS CONVERTED AT ITS OWN CELL TEMPERATURE AND THEN CARRIED
    # TO T_K, which are two separate steps and were one wrong step until
    # 2026-09-15. A rate per mTorr becomes a rate per density through n = P/(kT)
    # at the temperature of THAT cell (393 K, his own table-note); the impact
    # width then goes as <v^(3/5)> and so as T^0.3 at fixed density, which
    # `beta_self_vdw` reproduces to six digits. Together they leave
    # (T_Z/T_K)^-0.7, worth 1.8 per cent between 393 and 403.15 K.
    n_per_mtorr = (1e-3 * _C.TORR_PA) / (KB * ZAMEROSKI_7S_EFF_T_K) * 1e-6   # cm^-3 per mTorr
    t_factor = (T_K / ZAMEROSKI_7S_EFF_T_K) ** 0.3
    beta7_meas = ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR / (n_per_mtorr / n_cm3) * t_factor
    err7 = ZAMEROSKI_7S_BROADENING_ERR / (n_per_mtorr / n_cm3) * t_factor
    scale = (dc6_6 / dc6_7) ** 0.4 * branch_ratio
    return {"beta6_khz": beta7_meas * scale,
            "beta6_err_khz": err7 * scale,
            "beta6_first_principles_khz": beta_self_vdw(dc6_6, T_K, n_cm3) / 1e3 * (sum(br6) / len(br6)),
            "exchange_fraction_6s": tuple(ex6), "exchange_fraction_7s": tuple(ex7),
            "branch_factor_6s": tuple(br6), "branch_factor_7s": tuple(br7),
            "beta6_khz_no_exchange": beta7_meas * (dc6_6 / dc6_7) ** 0.4,
            "c6_5s5s_au": c6_5, "c6_5s6s_au": c6_6, "c6_5s7s_au": c6_7,
            "beta7_measured_khz": beta7_meas,
            "zameroski_eff_t_k": ZAMEROSKI_7S_EFF_T_K, "t_factor": t_factor,
            "beta7_predicted_khz": beta_self_vdw(dc6_7, T_K, n_cm3) / 1e3,
            "dc6_ratio": dc6_6 / dc6_7,
            "c6_ratio": c6_6 / c6_7,
            "prefactor_discrepancy": (beta_self_vdw(dc6_7, T_K, n_cm3) / 1e3) / beta7_meas}


def beta_self_budget(T_K: float = 403.15, n_cm3: float = 1e12) -> dict:
    """The error budget of beta_self(6S), every row MEASURED by moving the input.

    THE ROUTE TO RE-DERIVE THE BAR that `beta_self_anchored` returns only the
    anchor's share of. Each row here re-evaluates the anchored expression with
    one input displaced and reads the fractional move in beta; nothing is an
    exponent typed into a comment, and the unperturbed reconstruction is
    asserted equal to `beta_self_anchored`'s own value before any row is taken,
    so this function drifting away from that one is a failure and not a
    silently different number.

    WHAT IS IN THE QUADRATURE and why each enters where it does:

      * Zameroski's quoted bar, 13 on 129 (TABLE 3's total), which enters LINEARLY because the
        anchor takes its whole scale from that measurement. It dominates: every
        other row together is 2.0 per cent in quadrature, which moves the total
        from 8.5 to 8.8, so the coefficient
        is known exactly as well as the one measured nS rate in rubidium is.
      * his cell temperature, +-5 K on a stated 393, entering at the 0.7 power
        (the density conversion's T against the speed average's T^0.3).
      * the ground-pair sum's truncation, sized by swapping this module's own
        4180 a.u. for the literature 4691 -- a 12 per cent move on C6(5S+5S)
        that moves beta by 0.28 per cent, because it enters both rungs of a
        RATIO raised to 2/5 and very largely cancels.
      * the matrix elements, 2 per cent (Safronova's stated accuracy) applied
        DIFFERENTIALLY to the 6S sum alone, since a common-mode error cancels
        in the ratio exactly and only the differential part survives.
      * the exchange branches, whose WHOLE term size is carried as its bar --
        conservative, the signs being fixed by the sum rule (A253).

    WHAT IS NOT, and it is named rather than absorbed:

      * the recipe's absolute scale error. Measured against the one experiment
        it can be measured against, `beta_self_vdw` sits 6.1 per cent above
        Zameroski's 7S rate at the same temperature. The anchor divides that
        out on the assumption it is COMMON to 6S and 7S; whether it carries an
        n-dependence has no second measurement, and inventing a bar for it
        would be a number about nothing.
      * the inelastic channel 6S+5S -> 4D+5S, 777 cm^-1 released, still unsized
        (docs/notes/vdw_difference_potential_and_4d_channel.md).

    WHAT WAS REMOVED, because it was counted twice: the 5 per cent vapour-
    pressure(density) uncertainty the wiki's budget carried as OPEN. His paper
    states it is already inside the +-13 (see ZAMEROSKI_7S_CELL_T_K's note), so
    the budget's one open row closed by DELETION and the bar fell from the 11
    per cent that double count gave to 8.8.

    FALSE-PASS DIRECTION: a green reconstruction says this function and
    `beta_self_anchored` agree on the centre, never that either is right about
    the physics; the 6.1 per cent row above is what bounds that, on one state.
    """
    a = beta_self_anchored(T_K, n_cm3)
    c5, c6, c7 = a["c6_5s5s_au"], a["c6_5s6s_au"], a["c6_5s7s_au"]
    branch = a["branch_factor_6s"][0] / a["branch_factor_7s"][0]

    def beta6(g=ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR, t_z=ZAMEROSKI_7S_EFF_T_K,
              c5_=c5, c6_=c6, c7_=c7, br=branch):
        n_pm = (1e-3 * _C.TORR_PA) / (KB * t_z) * 1e-6
        b7 = g / (n_pm / n_cm3) * (T_K / t_z) ** 0.3
        return b7 * ((c6_ - c5_) / (c7_ - c5_)) ** 0.4 * br

    centre = beta6()
    assert abs(centre / a["beta6_khz"] - 1) < 1e-12, (centre, a["beta6_khz"])

    terms = {
        "anchor_measurement": beta6(g=ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR
                                    + ZAMEROSKI_7S_BROADENING_ERR),
        # THE ROW THAT WAS ZERO AND IS THE SECOND LARGEST. The rate is a slope
        # over 353 to 438 K and the paper does not print the weights that fix
        # its effective temperature, so beta is displaced across the span the
        # defensible weightings give, 368.3 to 428.5 K, and half that spread
        # read as a flat prior is the row. The 0.89 per cent this carried on
        # 2026-09-15 carried +-5 K on a temperature the source never states.
        # the span is over the WEIGHTING, not over the raw temperature range:
        # every leverage weighting is a defensible reading of the same fit.
        "anchor_conversion_temperature": max(
            abs(beta6(t_z=zameroski_effective_T(wt)) / beta6() - 1.0)
            for wt in ("unit", "inv_width2", "inv_p2")) / math.sqrt(3.0),
        "ground_pair_truncation": beta6(c5_=C6_RB2_GROUND_LIT_AU),
        # 4 PER CENT ON C6 AND NOT 2. Safronova's stated accuracy is on the
        # REDUCED MATRIX ELEMENTS and C6 goes as their square, so a coherent 2
        # per cent on d is 4 on C6. This row applied 1.02 to C6 and was half its
        # intended size.
        "matrix_elements_2pc_differential": beta6(c6_=c6 * 1.04),
        "exchange_branches": beta6(br=1.0),
    }
    # the conversion-temperature row is already a FRACTION, not a displaced value
    frac = {k: (v if k == "anchor_conversion_temperature" else abs(v / centre - 1.0))
            for k, v in terms.items()}
    rel = math.sqrt(sum(f * f for f in frac.values()))
    return {"beta6_khz": centre, "err_khz": centre * rel, "rel": rel,
            "terms_rel": frac,
            "recipe_scale_error_on_7s": a["prefactor_discrepancy"] - 1.0,
            "open_terms": (
            # THE DOMINANT ONE, and it is not in the quadrature because no
            # reading of the paper spans it. Zameroski cites Steck for his
            # vapour pressure, and this package's density.py uses the same
            # correlation -- but his own table notes give 0.83 mTorr at 393 K
            # and 0.23 at 373 where that curve gives 0.671 and 0.184, a ratio
            # of 1.24 (equivalently a constant +3.4 K offset). Either his
            # pressure axis is 1.24x this record's, and his slope is ~20 per
            # cent low on this record's density scale, or his temperature
            # labels are 3.4 K low and it is benign. Nothing in the paper
            # distinguishes them, and it is larger than every row above.
            "his Rb pressure axis against this record's density curve, ~20 per cent",
            # ON THE ANCHOR RUNG, where it does not cancel: 7S+5S -> 5P+5P is
            # open by 678 cm^-1 and first-order dipole-dipole coupled, worth
            # ~1 to 3 per cent of the width. The 6S+5S -> 4D+5S channel this
            # tuple named is on the TARGET rung, is not dipole-dipole allowed
            # at first order, and largely cancels in the anchor.
            "the 7S+5S -> 5P+5P inelastic exit, ~1 to 3 per cent",
            "the recipe's scale error carrying an n-dependence")}


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
    # <v^(3/5)> over the Maxwell relative-speed distribution, not vbar^(3/5)
    fwhm_ang = prefactor * c6_rate ** 0.4 * v ** 0.6 * speed_average_factor(0.6) * n
    return fwhm_ang / (2.0 * math.pi)
