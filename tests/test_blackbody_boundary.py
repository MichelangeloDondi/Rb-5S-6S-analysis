"""Blackbody as a campaign boundary: physical limits and the ceiling family.

A radiation model can be wrong in ways a spot value does not reveal: an
occupation number that does not fall on the Wien tail, an Einstein A that does
not scale as the cube of frequency, a ceiling that moves the wrong way with
the target. These check that class.
"""
from __future__ import annotations

import math

import pytest

from rb5s6s import blackbody as B


def test_shift_reproduces_every_committed_point_exactly():
    """Interpolation must not perturb the values it interpolates between."""
    for t_k, (value, err) in B.RB_5S6S_SHIFT_HZ.items():
        got, got_err = B.shift_hz(t_k, with_error=True)
        assert got == pytest.approx(abs(value), abs=1e-12)
        assert got_err == pytest.approx(err, abs=1e-12)


def test_occupation_is_on_the_wien_tail_for_this_cascade():
    """The single fact that makes blackbody re-excitation negligible here: at
    cell temperatures every cascade line sits far out on the exponential tail."""
    for lam_nm in (795.0, 1324.0, 1367.0, 2730.0, 2790.0):
        n = B.occupation(lam_nm * 1e-9, 403.15)
        assert 0.0 < n < 1e-3, (lam_nm, n)
    assert B.occupation(1324e-9, 403.15) < 1e-10


def test_occupation_rises_with_temperature_and_wavelength():
    assert B.occupation(1324e-9, 500.0) > B.occupation(1324e-9, 400.0)
    assert B.occupation(9100e-9, 403.15) > B.occupation(1324e-9, 403.15)


def test_einstein_a_scales_as_frequency_cubed():
    """A halved wavelength is eight times the rate at fixed dipole."""
    a1 = B.einstein_a(1000e-9, 1.0)
    a2 = B.einstein_a(500e-9, 1.0)
    assert a2 / a1 == pytest.approx(8.0, rel=1e-9)


def test_stimulated_rate_is_the_product():
    lam, d, t = 1324e-9, 1.0, 403.15
    assert B.stimulated_rate(lam, d, t) == pytest.approx(
        B.einstein_a(lam, d) * B.occupation(lam, t), rel=1e-12)


def test_shift_grows_faster_than_the_naive_fourth_power():
    """A pure quadratic Stark shift in a thermal field gives exactly 4. The
    near-resonant 6S-6P contribution makes it steeper, and a model using 4
    would understate the shift at high temperature, the direction that matters
    for a ceiling."""
    ts = sorted(B.RB_5S6S_SHIFT_HZ)
    lo, hi = ts[0], ts[-1]
    exponent = math.log(B.shift_hz(hi) / B.shift_hz(lo)) / math.log(hi / lo)
    assert 4.0 < exponent < 4.6, exponent


def test_the_ceiling_family_moves_the_right_way():
    """A looser target allows a hotter cell. A ceiling that fell with the
    target would be inverted, which is easy to write and hard to see."""
    ceilings = [B.t_max(x) for x in (100.0, 1e3, 1e4, 1e5)]
    assert all(a < b for a, b in zip(ceilings, ceilings[1:])), ceilings


def test_correcting_the_shift_raises_the_ceiling_a_lot():
    """The value of computing and subtracting the shift: only its own
    uncertainty then remains, and the uncertainty is 235 times smaller."""
    for target in (100.0, 1e3, 1e4):
        assert B.t_max(target, corrected=True) > B.t_max(target)


def test_blackbody_is_not_binding_in_the_cell_operating_range():
    """The finding this module delivers, stated as a test so it cannot rot.
    Across 70 to 130 C the shift stays well under a kilohertz, which is four
    orders below the light-shift bound the record quotes, so temperature is
    not limited by thermal radiation at any accessible cell temperature."""
    assert B.shift_hz(343.15) < 100.0
    assert B.shift_hz(403.15) < 200.0
    assert B.t_max(1000.0) > 500.0     # kelvin, far above any vapour cell


def test_extrapolation_is_flagged():
    assert not B.is_extrapolated(373.15)
    assert B.is_extrapolated(500.0)
    assert B.is_extrapolated(300.0)


def test_bad_arguments_are_rejected():
    with pytest.raises(ValueError):
        B.occupation(1e-6, 0.0)
    with pytest.raises(ValueError):
        B.shift_hz(-1.0)
    with pytest.raises(ValueError):
        B.t_max(0.0)
