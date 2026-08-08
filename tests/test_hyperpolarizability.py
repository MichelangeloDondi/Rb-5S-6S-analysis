"""Anchors and regression pins for rb5s6s/hyperpolarizability.py.

The anchor set mirrors the adversarial reviews that produced the
module (2026-08-08): the linear shift must reproduce the module
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


def test_position_sensitivity_restores_the_line_lists():
    """The sensitivity scan mutates module state and must put it
    back, or every later computation in the session is wrong."""
    import rb5s6s.polarizability as p
    before5, before6 = p.LINES_5S, p.LINES_6S
    hp.position_sensitivity("1203.9", 1203.886285673291, (1195.0, 1210.0))
    assert p.LINES_5S is before5 and p.LINES_6S is before6
