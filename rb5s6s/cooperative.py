"""
M37 -- two-atom (cooperative) two-photon channels, and the sublevel satellites
they open that a single atom must refuse.

WHY THIS MODULE EXISTS. Every selection-rule argument in M36 and in
docs/wiki/selection-rules.md is a SINGLE-ATOM argument, and one of its two legs
is a statement about one atom's electronic angular momentum: a J=1/2 state has
two magnetic sublevels, so the rank-2 part of the two-photon operator has no
reduced matrix element between 5S1/2 and 6S1/2 and the sigma+sigma+ content of
the drive is refused. That leg does NOT survive being asked about two atoms. A
PAIR of ground-state atoms has four sublevel products, it can accept two units
of angular momentum by taking one unit each, and the triangle rule that closed
the single-atom channel says nothing about it. The question was put by the
owner on 2026-08-19 and this module is the answer.

The answer has three parts, and only the third is a suppression.

PART 1, ENERGY CONSERVATION, is the strongest constraint and it is exact. At
the two-photon energy the pair has exactly one resonant final configuration,
one atom in 6S and one still in the ground state. `pair_final_states` lists
every alternative the committed level table can build. The nearest is
5S + 4D5/2, off by 777 cm^-1, which is 23.3 THz, about 4 million line widths.
No pair channel competes for the resonance, so a cooperative process cannot
produce a new LINE. It can only redistribute magnetic sublevels within the one
resonance that already exists.

PART 2, THE TOPOLOGY, is where the owner's point lands and it is real. Two
absorption vertices on two different atoms, joined by one dipole-dipole
transfer, reach |6S(m+q), 5S(m'+q')| with q and q' each +-1. Two topologies
matter and they behave oppositely under the field:

  EXCHANGE, q' = -q. The pair takes zero net angular momentum, which is what
  the pi-pi and sigma+sigma- content of linear light offers. The two Zeeman
  shifts are equal and opposite and CANCEL whenever the two atoms share a g_F.
  Same isotope and same F therefore puts this channel exactly under the main
  line, where it is not a satellite at all.

  ALIGNED, q' = +q. The pair takes two units, which is exactly the
  sigma+sigma+ content that a SINGLE atom refuses. Linear light offers it at
  amplitude sin^2(theta)/2, where theta is the angle between the field that
  sets the quantisation axis and the linear polarisation, so the drive is 1/2
  at MOST and reaches that only with the field perpendicular to the
  polarisation. With the field along the polarisation the light is pure pi
  and this channel is off entirely. `aligned_drive_weight` carries it, and
  the sin^4 dependence in rate is the one experimental handle this channel
  has. Here the two Zeeman shifts ADD, and a same-F pair puts
  a satellite at 2 * g_F * mu_B * B, twice the single-atom Delta_m_F = +-1
  position. This is the Delta_m_F = +-2 signature, carried by a pair rather
  than by one atom.

`satellite_mhz` gives both, and their zeros are complementary: the exchange
channel vanishes for same-F pairs and the aligned channel vanishes for the
opposite-sign pair (87Rb F=2 with F=1), so no field orientation closes both.

PART 3, THE SIZE. The transfer vertex costs one factor V_dd / Delta, where
Delta = 5025 cm^-1 = 150.7 THz is how far the pair virtual state |5P, 5P| sits
above the two-photon energy. That ratio is K / R^3 with K a volume this module
computes from the SAME committed reduced matrix elements the polarizability
sum uses. Integrated over the pair distribution the rate ratio is

    4 pi n K^2 / (3 Rc^3)

and it is dominated by the closest pairs, so the cutoff Rc carries it. Two
cutoffs are defensible and both are provided. The perturbative floor is where
K / Rc^3 reaches 0.1, about 1.04 nm, and BELOW it this expression is not a
calculation, it is an extrapolation into a regime where the pair is a molecule.
The physical cutoff is the Weisskopf radius of the same van der Waals
difference M18 already uses for beta_self: inside it the collision is strong
and fully dephasing, which is not a new coherent channel but the collisional
broadening the record has already MEASURED. `rate_ratio` refuses a cutoff
below the perturbative floor rather than quoting a number from outside its own
validity, per protocol 19.76.

WHAT COMES OUT. At the campaign's hottest condition, 130 C, the cooperative
rate at the Weisskopf cutoff is 1.3e-9 of the single-atom rate, falling to
2.3e-11 at 70 C because the ratio is linear in density. The single-atom
hyperfine-mixing route is computed by M36's `hyperfine_mixing_rate`, which
squares the intermediate-state admixture on each fine-structure leg and sums
them, giving 1.5e-10. The pair route is therefore about EIGHT TIMES it. The
long-quoted 1.2e-10 is the dominant leg alone and is returned beside it. The pair route does not sit far below
the single-atom one the way a higher-order process usually would, it dominates
the forbidden-channel budget, and the owner's instinct that asking about two
atoms reaches something the single-atom argument had not covered is correct on
both counts.

THE FACTOR OF TEN REPLACES AN EARLIER NUMBER. The first version of this
module summed only the 5P1/2 intermediate leg and reported 1.5e-10, which
made the two routes look equal. That omission surfaced on 2026-08-20.
5P3/2 is E1 allowed at every vertex, its reduced matrix elements are the
larger pair, and its energy denominators are not much worse, so carrying all
four leg combinations multiplies the amplitude ratio by 2.82 and the rate by
7.97.

It is also the only one of the two that can put amplitude at the
Delta_m_F = +-2 POSITION. The single-atom rank-2 channel is closed outright,
so the single-atom analysis has nothing at 2 * g_F * mu_B * B at any order.
The aligned pair topology does, at 700 kHz for 87Rb in 50 microtesla.

HOW FAR BELOW VISIBILITY, with the floor named rather than asserted. The
tightest bound this record carries on an out-of-window feature is
`f_wing_red_mean` at 130 C in `results/wing_check.csv`, 0.0009 as a fraction
of peak, so roughly 0.0018 at 95 per cent. The pair channel sits SIX orders
below that and the single-atom hyperfine route seven. An earlier version of
this module was wrong here: it said nine orders in one paragraph and ten in
another, both earlier claims, neither sourced and both too generous. The exchange topology does not move the line at all,
and nothing here is proposed as a fitted component.

FOUR PHOTONS. |5S, 5S| + 4 photons -> |6S, 6S| is exactly resonant, since four
photon energies are two 6S energies. It is nonetheless not a new feature. Its
uncorrelated part is two independent single-atom events, each with Delta_m_F=0
at the unshifted frequency. Its correlated part carries the same V_dd / Delta
factor AND the square of an already small excitation probability, and its
resonance condition per photon is unchanged. `four_photon_note` states this.

VALIDITY. Angular factors of order unity are not carried: this module sizes a
channel in order to close it, and a factor of two or three does not change a
conclusion that has six orders of headroom. It would have to be carried if
the channel were ever promoted to a fitted component, which nothing here
proposes.
"""

from __future__ import annotations

import itertools
import math

__all__ = ["pair_final_states", "TRANSFER_DEFECT_CM", "suppression_volume_m3",
           "amplitude_ratio", "rate_ratio", "satellite_mhz",
           "perturbative_floor_nm", "weisskopf_radius_nm", "GF_5S",
           "aligned_drive_weight", "four_photon_note", "IONISATION_LIMIT_CM",
           "POWER_EXPONENT_TWO_PHOTON", "POWER_EXPONENT_FOUR_PHOTON",
           "satellite_width_contribution_mhz", "resolving_field_ut",
           "knob_table"]

# Rb I first ionisation limit, NIST ASD. Used only to show that four photons
# on ONE atom overshoot it, which is why the four-photon question has no
# single-atom answer.
IONISATION_LIMIT_CM = 33690.81

# CODATA, and the atomic unit of electric dipole moment.
_EA0 = 8.4783536255e-30          # C m
_EPS0 = 8.8541878128e-12         # F/m
_H = 6.62607015e-34              # J s
_HBAR = _H / (2.0 * math.pi)
_C_CM = 2.99792458e10            # cm/s
_MU_B_MHZ_PER_UT = 9.2740100783e-24 / _H * 1e-6 / 1e6

# Lande g_F in the 5S1/2 ground state, by isotope and F. The 6S1/2 values are
# the same to the g_J difference, which is why the main line's first-order
# shift cancels (M36). The signs are what make the two topologies below have
# complementary zeros.
GF_5S = {("87Rb", 2): 0.5, ("87Rb", 1): -0.5,
         ("85Rb", 3): 1.0 / 3.0, ("85Rb", 2): -1.0 / 3.0}


def pair_final_states(limit: int = 8):
    """Two-atom configurations ranked by their defect from the two-photon
    energy, as (label, total_cm, defect_cm, defect_thz).

    Built from M17's committed level table, so it moves if that table moves.
    The first row is the resonance and every other row is the argument.
    """
    from .hyperpolarizability import LEVELS
    from .polarizability import E_6S_CM

    rows = []
    for a, b in itertools.combinations_with_replacement(sorted(LEVELS), 2):
        total = LEVELS[a][2] + LEVELS[b][2]
        if total == 0.0:
            continue
        defect = total - E_6S_CM
        rows.append((f"{a} + {b}", total, defect, defect * _C_CM * 1e-12))
    rows.sort(key=lambda r: abs(r[2]))
    return rows[:limit]


def _legs():
    """The two 5P fine-structure legs, each with the term energy and the two
    reduced matrix elements the pair sum needs. BOTH are E1-allowed at every
    vertex. The first version of
    this module silently carried only 5P1/2, found on 2026-08-20."""
    from .polarizability import LINES_5S, LINES_6S
    return ((LINES_5S[0][0], LINES_5S[0][1], LINES_6S[0][1]),
            (LINES_5S[1][0], LINES_5S[1][1], LINES_6S[1][1]))


def _transfer_defect_cm() -> float:
    """The lowest pair virtual state, |5P1/2, 5P1/2|, above the two-photon
    energy. Quoted as THE defect for scale. The sum below carries all four
    combinations, of which this is the closest and the weakest."""
    from .polarizability import LINES_5S, E_6S_CM
    return 2.0 * LINES_5S[0][0] - E_6S_CM


TRANSFER_DEFECT_CM = _transfer_defect_cm()


def _sum_ratio_au_per_cm() -> float:
    """S_pair / S_single, in atomic units of dipole squared per reciprocal
    centimetre. This is the whole angular-momentum-free content of the
    suppression, and it is a RATIO of two sums rather than one term.

    The single-atom second-order sum is

        S_single = sum_j  d(5S,5P_j) d(6S,5P_j) / (E_j - hw)

    The pair third-order sum runs over BOTH atoms' intermediate legs. One atom
    absorbs, then the other, then one dipole-dipole vertex takes
    |5P_j, 5P_j'| to |6S, 5S|, so its numerator carries the partner's dipole
    TWICE, once to reach 5P_j' and once to come back down:

        S_pair = sum_jj'  d(5S,5P_j) d(6S,5P_j) d(5S,5P_j')^2
                          / [(E_j - hw)(E_j + E_j' - E_6S)]

    Including 5P3/2 multiplies the ratio by 2.82 and therefore the RATE by
    7.97, because the 5P3/2 reduced elements are the larger pair and its
    energy denominators are not much worse.
    """
    from .polarizability import E_6S_CM
    hw = E_6S_CM / 2.0
    legs = _legs()
    s_single = sum(d5 * d6 / (e - hw) for e, d5, d6 in legs)
    s_pair = 0.0
    for e, d5, d6 in legs:
        for e2, d52, _ in legs:
            s_pair += (d5 * d6 / (e - hw)) * (d52 * d52 / (e + e2 - E_6S_CM))
    return s_pair / s_single


def suppression_volume_m3() -> float:
    """K, the volume with V_dd / Delta = K / R^3.

    Built from `_sum_ratio_au_per_cm` and nothing else, so it moves if the
    committed line lists move. Angular factors of order unity are still not
    carried, which is stated in the module docstring and is why this is a
    ceiling rather than a prediction.
    """
    return (_sum_ratio_au_per_cm() * _EA0 * _EA0
            / (4.0 * math.pi * _EPS0 * _H * _C_CM))


def perturbative_floor_nm(ceiling: float = 0.1) -> float:
    """Separation at which V_dd / Delta reaches `ceiling`. Below this the
    third-order expression is outside its own validity and `rate_ratio`
    declines to evaluate."""
    return (suppression_volume_m3() / ceiling) ** (1.0 / 3.0) * 1e9


def amplitude_ratio(sep_nm: float) -> float:
    """Cooperative amplitude relative to the single-atom one, at separation
    `sep_nm`. Rate goes as the square."""
    if sep_nm <= 0.0:
        raise ValueError("separation must be positive")
    return suppression_volume_m3() / (sep_nm * 1e-9) ** 3


def weisskopf_radius_nm(T_C: float = 130.0) -> float:
    """Radius at which the van der Waals phase shift over a thermal collision
    reaches one radian, (Delta_C6 / (hbar v))^(1/5).

    Inside it the collision is strong and completely dephasing, which is the
    impact regime M18 computes for beta_self. Using it as the cutoff is what
    keeps this module from counting measured collisional broadening a second
    time as a new coherent channel.
    """
    from .vanderwaals import c6_5s5s, c6_5s6s, mean_relative_speed
    hartree_j = 4.3597447222071e-18
    a0 = 5.29177210903e-11
    delta_c6 = abs(c6_5s6s() - c6_5s5s()) * hartree_j * a0 ** 6
    v = mean_relative_speed(T_C + 273.15)
    return (delta_c6 / (_HBAR * v)) ** 0.2 * 1e9


def rate_ratio(T_C: float = 130.0, cutoff_nm: float | None = None) -> float:
    """Cooperative rate as a fraction of the single-atom two-photon rate,
    integrated over a uniform pair distribution outside `cutoff_nm`.

    Default cutoff is the Weisskopf radius at the same temperature. The
    integral is dominated by the cutoff, so the cutoff is stated, never
    implied, and a value below the perturbative floor raises.
    """
    import numpy as np
    from .density import number_density_cm3

    if cutoff_nm is None:
        cutoff_nm = weisskopf_radius_nm(T_C)
    floor = perturbative_floor_nm()
    if cutoff_nm < floor:
        raise ValueError(
            f"cutoff {cutoff_nm:.2f} nm is inside the perturbative floor "
            f"{floor:.2f} nm, where V_dd/Delta exceeds 0.1 and this third-order "
            f"expression is an extrapolation rather than a calculation")

    n_m3 = float(number_density_cm3(np.array([T_C]))[0]) * 1e6
    k = suppression_volume_m3()
    return 4.0 * math.pi * n_m3 * k * k / (3.0 * (cutoff_nm * 1e-9) ** 3)


def satellite_mhz(b_field_ut: float, pair_a: tuple, pair_b: tuple,
                  topology: str = "aligned", q: int = 1) -> float:
    """Position of the two-atom sublevel satellite, MHz from the main line.

    `pair_a` and `pair_b` are (isotope, F) keys of GF_5S. The excited atom
    takes +q, the partner takes +q for `aligned` and -q for `exchange`. The
    two shifts add in the first case and cancel in the second, so the same
    pair can be silent in one topology and 700 kHz away in the other.
    """
    try:
        g_a, g_b = GF_5S[pair_a], GF_5S[pair_b]
    except KeyError as exc:
        raise KeyError(f"unknown (isotope, F) key {exc.args[0]!r}, "
                       f"known keys are {sorted(GF_5S)}") from None
    if topology == "aligned":
        net = g_a + g_b
    elif topology == "exchange":
        net = g_a - g_b
    else:
        raise ValueError("topology must be 'aligned' or 'exchange'")
    return q * net * _MU_B_MHZ_PER_UT * abs(b_field_ut)


def aligned_drive_weight(theta_deg: float) -> float:
    """Amplitude the drive offers the ALIGNED pair channel, for linear light.

    `theta_deg` is the angle between the quantisation axis, which the field
    sets, and the linear polarisation. Decomposing a unit linear vector on
    the spherical basis gives a pi component cos(theta) and sigma components
    of magnitude sin(theta)/root two each, so the sigma+sigma+ product is
    sin^2(theta)/2. It is 1/2 at most, reached only at 90 degrees, and it is
    exactly zero when the field lies along the polarisation.

    The RATE weight is the square of this, so the channel goes as sin^4, and
    rotating the field against the polarisation is the only control that
    turns it off.
    """
    return math.sin(math.radians(theta_deg)) ** 2 / 2.0


# HOW THE CHANNEL RESPONDS TO THE THREE KNOBS, as exponents of the RATIO to
# the main line. The ratio is what matters, because an experiment sees the
# satellite against the line and not against the vacuum.
POWER_EXPONENT_TWO_PHOTON = 0.0
"""The two-photon pair channel absorbs the same two photons the line does, so
both rates go as intensity SQUARED and the ratio is flat in power. Power
cannot switch this channel on, which is the single most useful thing to know
about it."""

POWER_EXPONENT_FOUR_PHOTON = 2.0
"""The four-photon pair channel goes as intensity to the fourth, so its ratio
to the line goes as intensity squared. It is the only power-tunable member of
the family, and doubling the power quadruples it."""


def satellite_width_contribution_mhz(b_field_ut: float, t_c: float = 130.0,
                                     pair_a: tuple = ("87Rb", 2),
                                     pair_b: tuple = ("87Rb", 2),
                                     topology: str = "aligned",
                                     fwhm_mhz: float = 5.37) -> float:
    """What the pair satellite adds to the measured WIDTH, in MHz.

    Below the field at which it separates, the satellite is not a feature a
    fitter sees. It is a contribution to the second moment: a weak pair at
    plus and minus s with fractional intensity f adds f s^2, and a
    Gaussian-equivalent width grows by (FWHM / 2) times that over the existing
    variance. The same small-f expansion M36 uses.

    The field enters ONLY through s. The rate fraction f is field-independent,
    so this grows as B squared while the channel itself does not change.
    """
    s = satellite_mhz(b_field_ut, pair_a, pair_b, topology)
    f = rate_ratio(t_c)
    var = (fwhm_mhz / 2.3548) ** 2
    return fwhm_mhz * 0.5 * f * s * s / var


def resolving_field_ut(pair_a: tuple = ("87Rb", 2),
                       pair_b: tuple = ("87Rb", 2),
                       topology: str = "aligned",
                       fwhm_mhz: float = 5.37) -> float:
    """Field at which the satellite's offset equals the line width, so it
    stops adding to the width and starts being a separate feature.

    Above this a search for the channel is a search for a RESOLVED line at a
    known position, which is a completely different measurement from a width
    excess and a far better one.
    """
    per_ut = abs(satellite_mhz(1.0, pair_a, pair_b, topology))
    if per_ut == 0.0:
        raise ValueError("this pair and topology have no satellite to resolve")
    return fwhm_mhz / per_ut


def knob_table(t_c: float = 130.0, b_field_ut: float = 50.0) -> dict:
    """The channel against the three knobs an experiment actually has.

    Returned rather than printed so the producer and the tests read the same
    numbers. Everything here follows from `rate_ratio` and `satellite_mhz`.
    """
    import numpy as np
    from .density import number_density_cm3
    return {
        "rate_ratio": rate_ratio(t_c),
        "density_cm3": float(number_density_cm3(np.array([t_c]))[0]),
        "power_exponent_two_photon": POWER_EXPONENT_TWO_PHOTON,
        "power_exponent_four_photon": POWER_EXPONENT_FOUR_PHOTON,
        "satellite_mhz_per_ut": abs(satellite_mhz(1.0, ("87Rb", 2),
                                                  ("87Rb", 2), "aligned")),
        "satellite_mhz": satellite_mhz(b_field_ut, ("87Rb", 2),
                                       ("87Rb", 2), "aligned"),
        "width_contribution_mhz": satellite_width_contribution_mhz(
            b_field_ut, t_c),
        "resolving_field_ut": resolving_field_ut(),
    }


def four_photon_note() -> dict:
    """The four-photon question. It has no single-atom answer at all, because
    four photon energies overshoot the ionisation limit, and its pair answer
    is resonant but carries nothing new."""
    from .polarizability import E_6S_CM
    photon_cm = E_6S_CM / 2.0
    return {
        "final_state": "6S + 6S",
        "resonant": True,
        "total_cm": 2.0 * E_6S_CM,
        "photons": 4,
        "single_atom_four_photon_cm": 4.0 * photon_cm,
        "ionisation_limit_cm": IONISATION_LIMIT_CM,
        "single_atom_excess_above_limit_cm": 4.0 * photon_cm - IONISATION_LIMIT_CM,
        "single_atom_outcome": (
            "photoionised rather than excited, so four photons on one atom "
            "cannot make a line and the question has only a pair answer"),
        "six_s_plus_one_photon_cm": E_6S_CM + photon_cm,
        "six_s_needs_two_photons_to_ionise": True,
        # The correlated four-photon pair channel is BOUNDED, not computed.
        # It carries the same dipole-dipole factor as the two-photon pair
        # channel times the probability that the pair is already excited,
        # which is at most one, so the two-photon pair rate is an upper bound
        # on it. Stated as a bound because that is what it is.
        "correlated_rate_upper_bound": rate_ratio(),
        "correlated_bound_is_a_bound_not_a_rate": True,
        "why_not_new": (
            "the uncorrelated part is two independent single-atom events at "
            "the unshifted frequency, and the correlated part carries the same "
            "dipole-dipole suppression as the two-photon pair channel times "
            "the square of an already small excitation probability"),
    }
