"""Anchors and regression pins for rb5s6s/hyperpolarizability.py.

The anchor set covers what the module can get wrong: the linear
shift must reproduce the module
polarizabilities at every crossing, the Einstein-A chain must
reproduce the measured D2 width and 6S lifetime, the radial-sign
table's physical content is pinned through a gauge-invariant loop
product, the vector sum must be polarization-trace invariant, and
every published coefficient is pinned against drift.
"""
import numpy as np
import pytest

from rb5s6s import hyperpolarizability as hp
from rb5s6s.constants import TAU_6S_S
from rb5s6s.polarizability import LINES_5S, LINES_6S, E_6S_CM


def test_linear_shift_reproduces_the_polarizabilities():
    """E2 at a magic crossing must equal minus the depth for BOTH
    states: this exercises the z matrix, the basis and the
    tail-plus-core channel against polarizability.py."""
    for name, lam in hp.crossings():
        for g in ("5S", "6S"):
            e2, _ = hp._rspt4(g, lam)
            assert abs(e2 / 1e6 + 1.0) < 2e-3, (name, g, e2)


def test_einstein_chain_d2_width_and_6s_lifetime():
    """The width chain that scattering_rates() uses, anchored at
    both ends: the D2 natural width (6.0666 MHz) from the 5P3/2 row
    and the measured 6S lifetime from the two 6S-5P rows with the
    emitter's degeneracy. The second anchor is the one that
    falsified an earlier convention at 49 percent."""
    de = LINES_5S[1][0] / hp.CM
    gamma_mhz = hp.einstein_a(de, LINES_5S[1][1], 3) * hp.AU_RATE_HZ \
        / (2 * np.pi) / 1e6
    assert abs(gamma_mhz - 6.0666) / 6.0666 < 5e-3
    a_sum = 0.0
    for (e, d, _s) in LINES_6S[:2]:
        a_sum += hp.einstein_a((e - E_6S_CM) / hp.CM, d, 1) * hp.AU_RATE_HZ
    tau_ns = 1e9 / a_sum
    assert abs(tau_ns - TAU_6S_S * 1e9) / (TAU_6S_S * 1e9) < 0.02


def test_radial_sign_loop_product_is_physical_and_pinned():
    """Closed loops through different intermediate states are
    invariant under any per-state phase choice, so their sign is
    physics. Pin the loop that two independent integrations agree
    on: 6S to 5P to 7S to 6P and back is NEGATIVE."""
    z = hp._zmat()
    loop = (z[("6S", "5P1/2")] * z[("5P1/2", "7S")]
            * z[("7S", "6P1/2")] * z[("6P1/2", "6S")])
    assert loop < 0.0
    # and the same loop through the other fine-structure branch
    loop32 = (z[("6S", "5P3/2")] * z[("5P3/2", "7S")]
              * z[("7S", "6P3/2")] * z[("6P3/2", "6S")])
    assert loop32 < 0.0


def test_vector_sum_is_trace_invariant():
    """The polarizability trace is polarization independent at
    second order: summing the sigma-plus shifts over m = +-1/2 must
    equal twice the linear m = 1/2 shift, per state. Recomputed
    here with the module's own angular machinery."""
    lam = 1203.886285673291
    om = (1e7 / lam) / hp.CM
    j_list = [hp._H, hp._TH] * 4

    def e2(lines, upper_cm, m, circ):
        tot = 0.0
        for (e, d, _s), jp in zip(lines, j_list):
            de = (e - upper_cm) / hp.CM
            if circ:
                w_abs = d * hp.w3j(jp, 1, hp._H, -(m + 1), 1, m)
                w_em = d * hp.w3j(jp, 1, hp._H, -(m - 1), -1, m)
            else:
                w_abs = w_em = d * hp.w3j(jp, 1, hp._H, -m, 0, m)
            tot += w_abs ** 2 / (om - de) - w_em ** 2 / (om + de)
        return tot

    for lines, upper in ((LINES_5S[:8], 0.0), (LINES_6S, E_6S_CM)):
        s_cir = e2(lines, upper, hp._H, True) \
            + e2(lines, upper, -hp._H, True)
        s_lin = 2.0 * e2(lines, upper, hp._H, False)
        assert abs(s_cir - s_lin) < 1e-9 * abs(s_lin)


PINNED_C = {
    "1203.9": +0.8736, "1287.9": -12.2667, "1339.6": +62.0149,
    "1297.5": +10.9817, "1029.7": +9.8191, "1031.9": +1.2898,
}


@pytest.mark.slow
def test_quartic_coefficients_pinned():
    cs = hp.quartic_coefficients()
    for name, ref in PINNED_C.items():
        assert abs(cs[name] - ref) / abs(ref) < 1e-3, (name, cs[name])


def test_vector_coefficient_pinned():
    v1 = hp.vector_coefficient(1203.886285673291)
    assert abs(v1 + 280207.0) < 30.0


def test_scattering_rates_pinned():
    r5, r6 = hp.scattering_rates(1203.886285673291)
    assert abs(r5 - 0.228) < 0.005
    assert abs(r6 - 5.757) < 0.02


def test_steepness_matches_the_worked_case():
    """FUTURE_TRANSITIONS section 5.1 computed the 1297.5 nm root by
    hand at 11.3 atomic units per picometre. The module must agree,
    since the whole lever budget there rides on it."""
    s = hp.steepness(1297.5332)
    assert abs(abs(s) - 11.3) / 11.3 < 0.02, s


def test_the_trap_crossing_is_the_flattest():
    """The practical crossing is the flattest of the six, which is
    the same fact as its being the best trap and the worst lever."""
    flat = min(hp.crossings(), key=lambda c: abs(hp.steepness(c[1])))
    assert flat[0] == "1203.9"


@pytest.mark.slow
def test_lever_table_names_the_element_each_crossing_speaks_to():
    """Pins the inverse-use result: the two best levers reach about
    two per cent, they are NOT the same crossing as the best trap,
    and the crossings that read the 6S-5P3/2 element are the ones
    that bear on the differential-polarizability sign question."""
    rows = {r["crossing"]: r for r in hp.lever_table()}
    assert rows["1339.6"]["frac_precision"] < 0.02
    assert rows["1297.5"]["frac_precision"] < 0.02
    # the trap crossing is an order of magnitude worse as a lever
    assert rows["1203.9"]["frac_precision"] > 0.10
    # and the element each speaks to
    assert rows["1339.6"]["element"] == "6S-5P3/2"
    assert rows["1297.5"]["element"] == "6S-7P1/2"
    assert rows["1203.9"]["element"] == "6S-5P3/2"
    # THE POINT, and the thing an earlier version of this test missed:
    # precision is worthless without the comparison to what is already
    # known. Exactly one crossing would improve on the present state,
    # and it is the steep root, because steepness and ignorance are
    # correlated through proximity to a weak high-lying line.
    gains = {k: v["gain"] for k, v in rows.items()}
    assert gains["1297.5"] > 1.0
    assert max(g for k, g in gains.items() if k != "1297.5") < 0.5
    # and the apparent better lever reads an already-tight element
    assert rows["1339.6"]["known_frac"] < 0.005


@pytest.mark.slow
def test_steepness_cancels_out_of_the_delivered_precision():
    """The correction of 2026-08-09. Section 5.1 selected crossings on
    steepness and the first amendment called it one of three deciding
    quantities. It decides none of it: the localisation and the
    position sensitivity both scale as one over the steepness, so it
    cancels exactly. Pinned two ways, since the whole account of what
    the lever measures rests on it."""
    rows = hp.lever_table()
    # the localisation is a fixed differential polarizability, in a.u.
    prods = [r["localisation_pm"] * abs(r["steepness_au_per_pm"])
             for r in rows]
    assert max(prods) - min(prods) < 1e-6 * prods[0]
    assert abs(prods[0] - 288.011) < 0.01, prods[0]
    # and so the delivered precision times the element's response is
    # the same constant at every crossing, over a factor of 900 in
    # steepness
    resp = [r["localisation_pm"] / (r["frac_precision"] / 0.01)
            * abs(r["steepness_au_per_pm"]) for r in rows]
    consts = [p * rr for p, rr in
              zip((r["frac_precision"] for r in rows), resp)]
    assert max(consts) - min(consts) < 1e-6 * consts[0]
    steeps = [abs(r["steepness_au_per_pm"]) for r in rows]
    assert max(steeps) / min(steeps) > 500.0


def test_position_sensitivity_restores_the_line_lists():
    """The sensitivity scan mutates module state and must put it
    back, or every later computation in the session is wrong."""
    import rb5s6s.polarizability as p
    before5, before6 = p.LINES_5S, p.LINES_6S
    hp.position_sensitivity("1203.9", 1203.886285673291, (1195.0, 1210.0))
    assert p.LINES_5S is before5 and p.LINES_6S is before6


def test_every_crossing_stays_clear_of_the_two_photon_pole():
    """_rspt4 has a pole where two photons hit the partner S state.

    The Floquet basis carries |partner, n-2>, so E4 diverges wherever
    2*h*nu equals a real S-to-S interval. For 5S-6S that is 993.4181 nm,
    which is the wavelength the 2025 campaign drove. Every crossing the
    module publishes coefficients at must stay far from it, and this
    pins that clearance so a future crossing cannot quietly land on it.
    """
    pole_cm = E_6S_CM / 2.0
    clearances = [abs(1e7 / lam - pole_cm) for _, lam in hp.crossings()]
    assert min(clearances) > 300.0, (
        f"a crossing sits {min(clearances):.1f} cm^-1 from the two-photon "
        "pole, where E4 is level repulsion and not hyperpolarizability")
    # and the drive really is on the pole, which is why this test exists
    assert abs(1e7 / 993.4192 - pole_cm) < 0.05


def test_the_two_photon_pole_is_the_delta_n_two_sector_alone():
    """At the drive wavelength E4 is one Floquet term, not a coefficient.

    Diagnosed 2026-08-09. nmax=1 excludes the delta-n = 2 sector and
    leaves the genuine non-resonant remainder, which is five orders of
    magnitude smaller. Pinned so nobody reads the resonant number as a
    hyperpolarizability, and so a change to the Floquet truncation that
    silently altered this is caught.
    """
    lam, u = 993.4192, 0.08271
    d4 = (_rspt4_e4(hp, "6S", lam, u, 3) - _rspt4_e4(hp, "5S", lam, u, 3))
    d4_no2 = (_rspt4_e4(hp, "6S", lam, u, 1) - _rspt4_e4(hp, "5S", lam, u, 1))
    assert abs(d4) > 100.0                    # the pole term dominates
    assert abs(d4_no2) < 0.01                 # the non-resonant remainder
    assert abs(d4) / abs(d4_no2) > 1e4
    # the truncation above the two-photon sector changes nothing
    for n in (2, 4, 5):
        dn = (_rspt4_e4(hp, "6S", lam, u, n) - _rspt4_e4(hp, "5S", lam, u, n))
        assert abs(dn - d4) < 1e-3 * abs(d4)


def _rspt4_e4(mod, state, lam, u, nmax):
    """E4 alone, so the pole tests read as arithmetic on one number."""
    return mod._rspt4(state, lam, u_mhz=u, nmax=nmax)[1]


def test_two_photon_matrix_element_and_its_ratio_to_the_light_shift():
    """T = +707.75 a.u. and 2T/|Delta_alpha| = 1.237 at the drive wavelength.

    Verified independently on 2026-08-09: a sum without the radial signs gives
    4588/6 = 765 a.u., 8 per cent high, because the 6P, 7P and 8P families
    oppose the 5P pair. The ratio is the saturation companion note's input, and
    its first value, 1.294, mixed two field conventions, so this pin also
    records the corrected number.
    """
    from rb5s6s.polarizability import delta_alpha
    T = hp.two_photon_matrix_element(993.4192)
    assert abs(T - 707.75) < 0.5
    ratio = 2.0 * abs(T) / abs(delta_alpha(993.4192))
    assert abs(ratio - 1.2367) < 0.002
    # the fine-structure paths through 5P must ADD (the sign theorem)
    from rb5s6s.hyperpolarizability import _RADIAL_SIGN
    s12 = _RADIAL_SIGN[("5S", "5P")] * _RADIAL_SIGN[("6S", "5P")]
    assert s12 > 0
