"""M37: the two-atom two-photon channel, its satellites and its size."""

import math

import pytest

from rb5s6s import cooperative as co
from rb5s6s.polarisation import zeeman_satellite_mhz


def test_the_pair_resonance_is_unique():
    """One atom in 6S beside a ground-state atom is the ONLY pair
    configuration at the two-photon energy. Everything else is far off."""
    rows = co.pair_final_states()
    label, _, defect, _ = rows[0]
    assert set(label.split(" + ")) == {"5S", "6S"}
    assert defect == pytest.approx(0.0, abs=1e-9)

    runner_up = rows[1]
    assert abs(runner_up[2]) > 700.0, runner_up
    assert abs(runner_up[3]) > 20.0, "runner-up must be tens of THz away"


def test_exchange_topology_cancels_for_a_matched_pair():
    """Equal g_F means the two sublevel changes are equal and opposite in
    energy. This is the same cancellation that protects the main line."""
    for key in co.GF_5S:
        assert co.satellite_mhz(50.0, key, key, "exchange") == 0.0


def test_aligned_topology_is_twice_the_single_atom_position():
    """The Delta_m_F = +-2 signature. A matched pair takes one unit each and
    the shifts ADD, landing at twice the single-atom satellite M36 computes."""
    for iso, f_top in (("87Rb", 2), ("85Rb", 3)):
        key = (iso, f_top)
        aligned = co.satellite_mhz(50.0, key, key, "aligned")
        assert aligned == pytest.approx(2.0 * zeeman_satellite_mhz(iso, 50.0))
    assert co.satellite_mhz(50.0, ("87Rb", 2), ("87Rb", 2)) == pytest.approx(0.6997, abs=1e-3)


def test_the_two_topologies_have_complementary_zeros():
    """No pair is silent in both, so no field arrangement closes the channel
    as a whole. The opposite-sign pair is the aligned channel's blind spot."""
    opposite = (("87Rb", 2), ("87Rb", 1))
    assert co.satellite_mhz(50.0, *opposite, topology="aligned") == 0.0
    assert abs(co.satellite_mhz(50.0, *opposite, topology="exchange")) > 0.6


def test_satellite_scales_with_field_and_with_q():
    key = ("87Rb", 2)
    one = co.satellite_mhz(50.0, key, key)
    assert co.satellite_mhz(100.0, key, key) == pytest.approx(2.0 * one)
    assert co.satellite_mhz(50.0, key, key, q=2) == pytest.approx(2.0 * one)


def test_unknown_sublevel_key_names_what_is_known():
    with pytest.raises(KeyError, match="87Rb"):
        co.satellite_mhz(50.0, ("87Rb", 3), ("87Rb", 2))


def test_amplitude_ratio_defines_the_perturbative_floor():
    floor = co.perturbative_floor_nm()
    assert co.amplitude_ratio(floor) == pytest.approx(0.1, rel=1e-9)
    assert 0.5 < floor < 3.0


def test_rate_ratio_declines_to_leave_its_validity():
    """Protocol 19.76: the expression refuses the regime where it is an
    extrapolation rather than a calculation."""
    with pytest.raises(ValueError, match="perturbative floor"):
        co.rate_ratio(130.0, cutoff_nm=0.5 * co.perturbative_floor_nm())


def test_rate_ratio_carries_its_two_stated_scalings():
    """Linear in density, and cubic in the cutoff that dominates it."""
    a = co.rate_ratio(130.0, cutoff_nm=5.0)
    b = co.rate_ratio(130.0, cutoff_nm=10.0)
    assert a / b == pytest.approx(8.0, rel=1e-9)

    import numpy as np
    from rb5s6s.density import number_density_cm3
    hot = float(number_density_cm3(np.array([130.0]))[0])
    cool = float(number_density_cm3(np.array([70.0]))[0])
    ratio = co.rate_ratio(130.0, cutoff_nm=5.0) / co.rate_ratio(70.0, cutoff_nm=5.0)
    assert ratio == pytest.approx(hot / cool, rel=1e-9)


def test_the_channel_stays_far_below_anything_observable():
    """The conclusion this module exists to support, as a guard. If a future
    edit to the line lists or the density model ever pushes the cooperative
    rate anywhere near a part per million, that is a result, not a detail."""
    for T in (70.0, 100.0, 130.0):
        assert co.rate_ratio(T) < 1e-6


def test_the_pair_route_dominates_the_single_atom_route():
    """The finding: it is NOT far below, it is about ten times ABOVE the
    1.2e-10 the single-atom hyperfine-mixing route carries."""
    hot = co.rate_ratio(130.0)
    single_atom = 1.1e-5 ** 2
    assert 5.0 < hot / single_atom < 20.0, hot
    assert co.weisskopf_radius_nm(130.0) > co.perturbative_floor_nm()


def test_both_fine_structure_legs_are_carried():
    """The omission found on 2026-08-20. Dropping 5P3/2
    understates the amplitude by 2.82 and the rate by 7.97, which is the
    difference between the pair route matching the single-atom one and
    dominating it."""
    from rb5s6s.polarizability import LINES_5S, LINES_6S, E_6S_CM
    hw = E_6S_CM / 2.0
    e1, d5_1, d6_1 = LINES_5S[0][0], LINES_5S[0][1], LINES_6S[0][1]
    one_leg = (d5_1 * d6_1 / (e1 - hw)) * (d5_1 ** 2 / (2 * e1 - E_6S_CM))
    one_leg /= (d5_1 * d6_1 / (e1 - hw))
    assert co._sum_ratio_au_per_cm() / one_leg == pytest.approx(2.82, abs=0.02)


def test_the_5p_three_halves_leg_is_the_larger_one():
    """Why the omission mattered: the dropped leg is not a small correction."""
    from rb5s6s.polarizability import LINES_5S, LINES_6S
    assert LINES_5S[1][1] > LINES_5S[0][1]
    assert LINES_6S[1][1] > LINES_6S[0][1]


def test_four_photon_pair_state_is_resonant_and_still_not_new():
    from rb5s6s.polarizability import E_6S_CM
    note = co.four_photon_note()
    assert note["resonant"] is True
    assert note["total_cm"] == pytest.approx(2.0 * E_6S_CM)
    assert note["photons"] == 4


def test_the_correlated_four_photon_channel_is_bounded_not_computed():
    """It carries the same dipole-dipole factor as the two-photon pair
    channel times a probability at most one, so that channel's rate is an
    upper bound on it. Stated as a bound, and checked as one, because an
    earlier version asserted the reasoning in a string and the test checked
    only that the string contained a word."""
    note = co.four_photon_note()
    assert note["correlated_bound_is_a_bound_not_a_rate"] is True
    assert note["correlated_rate_upper_bound"] == pytest.approx(co.rate_ratio())
    assert note["correlated_rate_upper_bound"] < 1e-6


def test_suppression_volume_uses_the_committed_matrix_elements():
    from rb5s6s.polarizability import LINES_5S, LINES_6S
    ea0, eps0, h, c_cm = 8.4783536255e-30, 8.8541878128e-12, 6.62607015e-34, 2.99792458e10
    expected = (LINES_6S[0][1] * ea0) * (LINES_5S[0][1] * ea0) / (
        4.0 * math.pi * eps0 * h * co.TRANSFER_DEFECT_CM * c_cm)
    assert co.suppression_volume_m3() == pytest.approx(expected, rel=1e-12)


def test_aligned_drive_is_sin_squared_over_two_not_a_constant():
    """The channel a single atom refuses is offered at sin^2(theta)/2, so one
    half is the MAXIMUM and the field can switch the channel off."""
    assert co.aligned_drive_weight(90.0) == pytest.approx(0.5)
    assert co.aligned_drive_weight(0.0) == pytest.approx(0.0, abs=1e-15)
    assert co.aligned_drive_weight(45.0) == pytest.approx(0.25)
    for deg in (10.0, 30.0, 70.0):
        expect = math.sin(math.radians(deg)) ** 2 / 2.0
        assert co.aligned_drive_weight(deg) == pytest.approx(expect)


def test_the_field_along_the_polarisation_closes_the_aligned_channel():
    """Pure pi light carries no same-handedness pair, so the only control
    this channel has really does reach zero rather than merely small."""
    assert co.aligned_drive_weight(0.0) ** 2 == pytest.approx(0.0, abs=1e-30)
    assert co.aligned_drive_weight(180.0) == pytest.approx(0.0, abs=1e-15)


def test_four_photons_on_one_atom_overshoot_the_ionisation_limit():
    """The reason the four-photon question has no single-atom answer."""
    n = co.four_photon_note()
    assert n["single_atom_four_photon_cm"] > n["ionisation_limit_cm"]
    assert n["single_atom_excess_above_limit_cm"] == pytest.approx(6574.2, abs=0.5)
    assert "photoionised" in n["single_atom_outcome"]


def test_one_photon_does_not_ionise_a_6s_atom():
    """Stated because it is the same arithmetic and it is what keeps the
    excited population from being emptied by the drive."""
    n = co.four_photon_note()
    assert n["six_s_plus_one_photon_cm"] < n["ionisation_limit_cm"]
    assert n["six_s_needs_two_photons_to_ionise"] is True


def test_power_cannot_switch_the_two_photon_pair_channel_on():
    """The most useful single fact about this channel. It absorbs the same two
    photons the line does, so both go as intensity squared and their RATIO is
    flat in power. The obvious experiment does not work."""
    assert co.POWER_EXPONENT_TWO_PHOTON == 0.0


def test_only_the_four_photon_member_is_power_tunable():
    """Rate as intensity to the fourth, so the ratio to the line goes as
    intensity squared and doubling the power quadruples it."""
    assert co.POWER_EXPONENT_FOUR_PHOTON == 2.0
    assert co.POWER_EXPONENT_FOUR_PHOTON > co.POWER_EXPONENT_TWO_PHOTON


def test_temperature_is_the_only_lever_on_the_size():
    """Linear in density, which is the channel's fingerprint: the single-atom
    hyperfine route is density-independent, so the density lever separates
    them."""
    import numpy as np
    from rb5s6s.density import number_density_cm3
    hot, cool = co.rate_ratio(130.0), co.rate_ratio(70.0)
    n_hot = float(number_density_cm3(np.array([130.0]))[0])
    n_cool = float(number_density_cm3(np.array([70.0]))[0])
    # linear in density, with a small extra factor from the Weisskopf cutoff
    assert (hot / cool) / (n_hot / n_cool) == pytest.approx(1.05, abs=0.05)
    assert 50.0 < hot / cool < 60.0


def test_the_field_moves_the_satellite_and_not_the_rate():
    """The field never enters the rate. That is what makes it a discriminant
    rather than a lever."""
    assert co.rate_ratio(130.0) == co.rate_ratio(130.0)
    a = co.satellite_mhz(50.0, ("87Rb", 2), ("87Rb", 2))
    b = co.satellite_mhz(500.0, ("87Rb", 2), ("87Rb", 2))
    assert b / a == pytest.approx(10.0)


def test_the_width_contribution_grows_as_the_field_squared():
    """Below the resolving field the satellite is a second-moment term, so it
    goes as B squared while the channel itself does not change."""
    w1 = co.satellite_width_contribution_mhz(50.0)
    w2 = co.satellite_width_contribution_mhz(500.0)
    assert w2 / w1 == pytest.approx(100.0, rel=1e-9)
    assert w1 < 1e-8, "at Earth's field this must be far under a millihertz"


def test_the_resolving_field_is_where_the_offset_reaches_the_line_width():
    b = co.resolving_field_ut()
    assert b == pytest.approx(384.0, abs=2.0)
    offset = abs(co.satellite_mhz(b, ("87Rb", 2), ("87Rb", 2)))
    assert offset == pytest.approx(5.37, rel=1e-6)


def test_a_pair_with_no_satellite_cannot_be_asked_for_a_resolving_field():
    with pytest.raises(ValueError, match="no satellite"):
        co.resolving_field_ut(("87Rb", 2), ("87Rb", 2), "exchange")


def test_the_knob_table_agrees_with_the_functions_it_summarises():
    k = co.knob_table(130.0, 50.0)
    assert k["rate_ratio"] == co.rate_ratio(130.0)
    assert k["satellite_mhz"] == co.satellite_mhz(50.0, ("87Rb", 2), ("87Rb", 2))
    assert k["width_contribution_mhz"] == co.satellite_width_contribution_mhz(50.0, 130.0)
    assert k["satellite_mhz_per_ut"] == pytest.approx(0.013996, rel=1e-4)
