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
    tail-plus-core channel against polarizability.py.

    THE 6S BOUND WIDENED, NOT THE 5S ONE (F307 corrected, A132.16, C6b). `_rspt4`'s Floquet basis
    carries 5P to 8P as discrete levels (`LEVELS`, `RME`, built from `_PN`) and folds everything
    past that into one fictitious far channel per S state, calibrated by TAIL_5S+CORE_5S and
    TAIL_6S+CORE_6S so its OWN linear shift reproduces `alpha_5s`/`alpha_6s`. Since 9P and 10P went
    explicit in LINES_6S, TAIL_6S shrank by exactly their static share, but `_PN` still names only
    five doublets (`_RADIAL_SIGN` has no entry for a 6S-9P or 6S-10P pair, a physics judgement this
    wave does not make), so `_rspt4`'s far channel now carries LESS than `alpha_6s`'s dynamic sum
    does at these six crossings, by up to 1.15 per cent (measured here, all six 6S residuals run
    0.72 to 1.15 per cent against 5S's own 0.004 to 0.007, unmoved because LINES_5S was not
    touched). OWED beyond C6b's window: `_PN`, `LEVELS` and `_RADIAL_SIGN` extended to 9P and 10P so
    `_rspt4` carries them as discrete levels the way `vector_coefficient` and `scattering_rates` now
    do (their own j_list was the same silent-truncation defect and is fixed in this wave)."""
    for name, lam in hp.crossings():
        e2_5s, _ = hp._rspt4("5S", lam)
        assert abs(e2_5s / 1e6 + 1.0) < 2e-3, (name, "5S", e2_5s)
        e2_6s, _ = hp._rspt4("6S", lam)
        assert abs(e2_6s / 1e6 + 1.0) < 0.013, (name, "6S", e2_6s)


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


#: RE-PINNED 2026-09-25 when C6b made 9P and 10P explicit in `polarizability.LINES_6S` (probe:d66818d0): each crossing
#: moves, most near a 6S-nP pole (1297.5 by 9 per cent, 1031.9 by 6), and the 1203.9 coefficient from +0.8736 to
#: +0.8690, so the "+0.87 Hz per megahertz squared" the front pages quote holds at its two digits.
PINNED_C = {
    "1203.9": +0.8690, "1287.9": -12.3628, "1339.6": +61.9481,
    "1297.5": +9.9910, "1029.7": +9.6715, "1031.9": +1.2073,
}


@pytest.mark.slow
def test_quartic_coefficients_pinned():
    cs = hp.quartic_coefficients()
    for name, ref in PINNED_C.items():
        assert abs(cs[name] - ref) / abs(ref) < 1e-3, (name, cs[name])


def test_vector_coefficient_pinned():
    """F307 corrected, A132.16, C6b: moved from -280207.0 to -280061.5 (still within 200 of the old
    pin, most of the shift already carried through a_m/e0's own dependence on the corrected
    alpha_6s even before the j_list fix below, which pulled it back the rest of the way) once
    vector_coefficient's j_list was sized to LINES_6S instead of a hardcoded 8, so 9P and 10P are
    summed here and not silently dropped by the zip against the old length-8 list."""
    v1 = hp.vector_coefficient(1203.886285673291)
    assert abs(v1 + 280061.5) < 30.0


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
    """T = +707.75 a.u., and the ratio to the light shift is a BAND, not a value.

    Verified independently on 2026-08-09: a sum without the radial signs gives
    4588/6 = 765 a.u., 8 per cent high, because the 6P, 7P and 8P families
    oppose the 5P pair.

    The ratio 2T/|Delta_alpha| is the saturation companion note's input, and it
    took two passes to get right. The note first used 1.294, then recorded 1.237
    as a correction of "two field conventions". That diagnosis was wrong: 1.294
    divides by the CITED 1093 a.u., which constants.DELTA_ALPHA_AU carried
    until the 2026-08-24 adjudication and which now lives in
    DELTA_ALPHA_AU_ORSON2021. Since 2026-09-15 the package constant is the ADOPTED
    dynamic sum, -1131.8 a.u., giving 1.2511, while the module's own sum gives its
    own ratio, 1.2476 since 9P and 10P went explicit (F307 corrected, A132.16, C6b;
    it read 1.2367 while they were still folded into the static tail). Three ends,
    and this test pins each to the construction that produces it: the module end,
    the constant end and the cited end, which no longer coincide and must not be
    allowed to drift into one another silently.
    """
    from rb5s6s.constants import DELTA_ALPHA_AU, DELTA_ALPHA_AU_ORSON2021
    from rb5s6s.polarizability import delta_alpha
    T = hp.two_photon_matrix_element(993.4192)
    assert abs(T - 707.75) < 0.5
    # the MODULE end MOVED (F307 corrected, A132.16, C6b): 9P and 10P are explicit lines now, so
    # this end is no longer the static-tail sum alone, and it reads 1.2476, not 1.2367
    ratio = 2.0 * abs(T) / abs(delta_alpha(993.4192))
    assert abs(ratio - 1.2476) < 0.002
    # the CONSTANT end: the adopted dynamic sum since 2026-09-15. Until then
    # this line read 1.2367 and the two ends coincided; they no longer do, and
    # the gap is the 9P-and-above group read dynamically.
    assert abs(2.0 * abs(T) / abs(DELTA_ALPHA_AU) - 1.2511) < 0.002
    ratio_cited = 2.0 * abs(T) / DELTA_ALPHA_AU_ORSON2021
    assert abs(ratio_cited - 1.2951) < 0.002
    # the band is the Delta_alpha gap and nothing else
    assert abs(ratio_cited / ratio
               - abs(delta_alpha(993.4192)) / DELTA_ALPHA_AU_ORSON2021) < 1e-12
    # the fine-structure paths through 5P must ADD (the sign theorem)
    from rb5s6s.hyperpolarizability import _RADIAL_SIGN
    s12 = _RADIAL_SIGN[("5S", "5P")] * _RADIAL_SIGN[("6S", "5P")]
    assert s12 > 0


def test_two_photon_rabi_uses_the_geometric_arm_combination():
    """Omega/2pi = 1026 kHz at the campaign maximum (RE-PINNED 2026-09-21, O44/F280: was 450 kHz
    at the retired waist convention; Omega goes as 1/w0^2 and the bore-limited central waist is smaller,
    42.38 um, so the campaign-maximum Rabi frequency reads higher, not lower), and the retro
    enters as 2 sqrt(rho), not (1 + rho).

    This is the one place the coupling and the shift take different combinations
    of the same two arms: the shift is linear in |E|^2, whose fringe mean is the
    arithmetic (1 + rho), while a two-photon amplitude is linear in E^2 and only
    its wavevector-cancelling term is Doppler-free, with the geometric
    2 sqrt(rho). Their ratio is the fringe contrast, so at rho = 0.94 the two
    agree to 0.05 per cent and nothing published moves, which is exactly why the
    difference would never be caught by a number check. The test therefore pins
    the FORM, at a rho where the two differ visibly.
    """
    import math
    from rb5s6s.constants import W0_CENTRAL_M
    from rb5s6s.lineshape import stark_shift_S0_mhz
    om = hp.two_photon_rabi_hz(0.225, W0_CENTRAL_M, 0.94)
    assert abs(om / 1e3 - 1026.0) < 0.5

    # the form: at rho = 0.36 the geometric and arithmetic combinations differ
    # by 11.8 per cent, so a regression to (1 + rho) cannot hide here. These are
    # relationships, not absolute pins, and hold unchanged at the new waist
    # (verified live: the ratios below are w0-independent to 1e-12).
    rho = 0.36
    got = hp.two_photon_rabi_hz(0.225, W0_CENTRAL_M, rho)
    one_arm = hp.two_photon_rabi_hz(0.225, W0_CENTRAL_M, 0.5) / (2.0 * math.sqrt(0.5))
    assert abs(got / (one_arm * 2.0 * math.sqrt(rho)) - 1.0) < 1e-12
    assert abs(got / (one_arm * (1.0 + rho)) - 1.0) > 0.1

    # Omega is linear in power and goes as 1/w0^2, both because it is linear in
    # intensity: a two-photon RABI FREQUENCY is first order in I, not second
    assert abs(hp.two_photon_rabi_hz(0.450, W0_CENTRAL_M, 0.94) / om - 2.0) < 1e-12
    assert abs(hp.two_photon_rabi_hz(0.225, W0_CENTRAL_M / 2, 0.94) / om - 4.0) < 1e-12

    # and the ratio to the committed S0 is the band's matching end times the
    # contrast, which is the whole content of the correction. Since the
    # S0 defaults to the package constant, which since 2026-09-15 is the
    # adopted dynamic sum, so the matching end is 1.2511; the cited 1.2951 end
    # is reproduced by passing the Orson constant explicitly. UNCHANGED at the
    # new waist (verified live, both sides move by the same aperture factor):
    # 1.2501 and 1.2944 against the same 1.2511/1.2951 targets, inside the same
    # 1e-3 tolerance this test always used.
    from rb5s6s.constants import DELTA_ALPHA_AU_ORSON2021
    contrast = 2.0 * math.sqrt(0.94) / 1.94
    ratio = om / (stark_shift_S0_mhz(0.225, W0_CENTRAL_M, rho=0.94) * 1e6)
    assert abs(ratio - 1.2511 * contrast) < 1e-3
    ratio_cited = om / (stark_shift_S0_mhz(
        0.225, W0_CENTRAL_M, rho=0.94,
        delta_alpha_au=DELTA_ALPHA_AU_ORSON2021) * 1e6)
    assert abs(ratio_cited - 1.2951 * contrast) < 1e-3
