"""The detection channel is chosen by the caller, and trapping follows it."""

import pytest

from rb5s6s.detection import (CHANNEL_780_D2, CHANNEL_795_D1,
                              CHANNEL_1300_CASCADE, DetectionChannel,
                              default_channel)
from rb5s6s.density import d1_optical_depth_per_cm


def test_the_default_channel_is_the_record_s_own():
    assert default_channel() is CHANNEL_795_D1
    assert default_channel().trapped


def test_the_d1_channel_reproduces_the_existing_function():
    """One source of truth: the channel must not become a second D1 model."""
    for T in (70.0, 90.0, 110.0, 130.0):
        for iso in (85, 87):
            assert CHANNEL_795_D1.optical_depth_per_cm(T, iso) == pytest.approx(
                d1_optical_depth_per_cm(T, iso), rel=1e-12)


def test_the_infrared_channel_carries_no_ground_state_depth():
    """Zero at every temperature because the infrared photon is not resonant
    with the GROUND state, not because a default happened to be zero.

    This is deliberately narrower than "untrapped". The infrared IS resonant
    with 5P at D1's cross-section, and what saves it is population: both legs
    are inverted inside the driven volume, and outside it a halo re-excites
    at about one per cent of the primary rate at 130 C. That term belongs to
    run_trapping_channels.py, not to this flag."""
    for T in (70.0, 130.0, 200.0):
        assert CHANNEL_1300_CASCADE.optical_depth_per_cm(T, 85) == 0.0


def test_a_trapped_channel_without_a_cross_section_raises():
    """The record ships no D2 cross-section. Returning zero would assert that
    the D2 photon escapes, which is false."""
    with pytest.raises(ValueError, match="sigma_cm2"):
        CHANNEL_780_D2.optical_depth_per_cm(130.0, 85)


def test_a_caller_supplied_channel_works_and_scales_with_its_sigma():
    mine = DetectionChannel(name="mine", wavelength_nm=780.24, trapped=True,
                            sigma_cm2=2e-11)
    twice = DetectionChannel(name="mine2", wavelength_nm=780.24, trapped=True,
                             sigma_cm2=4e-11)
    a = mine.optical_depth_per_cm(130.0, 87)
    b = twice.optical_depth_per_cm(130.0, 87)
    assert b == pytest.approx(2.0 * a, rel=1e-12)
    assert a > 0.0


def test_the_isotope_ratio_is_the_robust_part():
    """SIGMA_D1 is an envelope, but the 85/87 ratio is the abundance ratio and
    is what drives differential trapping between the four lines."""
    from rb5s6s.constants import ABUNDANCE_RB85, ABUNDANCE_RB87
    r = (CHANNEL_795_D1.optical_depth_per_cm(130.0, 85)
         / CHANNEL_795_D1.optical_depth_per_cm(130.0, 87))
    assert r == pytest.approx(ABUNDANCE_RB85 / ABUNDANCE_RB87, rel=1e-12)


def test_the_wavelengths_are_computed_from_the_record_not_typed():
    """Each channel's wavelength must fall out of the NIST term energies this
    package already carries, not out of a literal. A typed wavelength is a
    number whose source no check can see, which is the defect class that put
    a retracted value on a public figure on 2026-08-20."""
    from rb5s6s.polarizability import E_5P12_CM, E_5P32_CM, E_6S_CM
    nm = lambda hi, lo: 1.0e7 / (hi - lo)
    assert CHANNEL_795_D1.wavelength_nm == pytest.approx(nm(E_5P12_CM, 0.0), rel=1e-12)
    assert CHANNEL_780_D2.wavelength_nm == pytest.approx(nm(E_5P32_CM, 0.0), rel=1e-12)
    both = 0.5 * (nm(E_6S_CM, E_5P12_CM) + nm(E_6S_CM, E_5P32_CM))
    assert CHANNEL_1300_CASCADE.wavelength_nm == pytest.approx(both, rel=1e-12)


def test_the_d_lines_land_where_rubidium_puts_them():
    """An independent sanity bound on the same numbers, so a wrong term energy
    cannot pass the test above by agreeing with itself."""
    assert 794.0 < CHANNEL_795_D1.wavelength_nm < 796.0
    assert 779.0 < CHANNEL_780_D2.wavelength_nm < 781.0
    assert 1300.0 < CHANNEL_1300_CASCADE.wavelength_nm < 1400.0
    assert CHANNEL_780_D2.wavelength_nm < CHANNEL_795_D1.wavelength_nm
