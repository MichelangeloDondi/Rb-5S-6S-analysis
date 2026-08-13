#!/usr/bin/env python3
"""`transit_fwhm_at_T` refuses a beam waist where it wants a transit width.

THE INCIDENT. The clean-install gate of 2026-08-13 cloned the published
repository, installed it on the declared floor, and tried the first call a
reader of the public surface would try:

    transit_fwhm_at_T(130.0, W0_MEASURED_M)   ->  0.0001 MHz

The second parameter is a reference transit WIDTH in MHz. `W0_MEASURED_M` is
a beam WAIST in metres, 6.4e-5. The function accepted it and returned a width
four orders of magnitude too small, with no error and no warning. The true
value is 0.9575 MHz, reached through the exported
`transit_fwhm_from_w0(w0, T_C)`.

WHY THE WRONG CALL IS THE NATURAL ONE, which is what makes this worth a
guard rather than a docstring: the function is named for a temperature and a
transit width, `W0_MEASURED_M` is the geometry constant a reader meets first
in `__all__`, and `transit_fwhm_at_T` is not exported at all, so anyone
reaching into the submodule gets no steer from the public surface.

A silently wrong number is the one failure mode this record cannot afford,
since its whole argument is about numbers that can be trusted. The other two
first-contact errors that gate hit raised immediately and cost nothing.
"""
from __future__ import annotations

import pytest

from rb5s6s import W0_MEASURED_M, transit_fwhm_from_w0
from rb5s6s.linefit import transit_fwhm_at_T


@pytest.mark.parametrize("bad", [
    W0_MEASURED_M,        # the incident: a waist in metres, 6.4e-5
    1.6e-5,               # the 16 um waist a future session proposes
    0.0,                  # a width of zero is not an apparatus
    -1.0,
    5e3,                  # far above any width this apparatus class produces
])
def test_a_waist_or_a_nonsense_width_is_refused(bad):
    with pytest.raises(ValueError, match="not a transit width in MHz"):
        transit_fwhm_at_T(130.0, bad)


@pytest.mark.parametrize("good", [0.0026, 0.9575, 3.8, 5.65])
def test_every_width_the_record_actually_holds_is_accepted(good):
    """The band separates units, it does not pin the physics.

    These span the committed record, from its smallest transit-related width
    to its largest, so a guard that rejected any of them would be narrowing
    the apparatus rather than catching a unit error.
    """
    assert transit_fwhm_at_T(130.0, good) > 0.0


def test_the_correct_path_still_gives_the_published_number():
    """0.9575 MHz at 130 C and the measured waist, as every gate reports."""
    assert transit_fwhm_from_w0(W0_MEASURED_M, 130.0) == pytest.approx(
        0.9575, abs=5e-4)


def test_the_guard_does_not_change_a_valid_call():
    """Scaling from a reference is untouched: sqrt(T) in kelvin."""
    ref, t_ref, t = 0.9575, 110.0, 130.0
    expected = ref * ((t + 273.15) / (t_ref + 273.15)) ** 0.5
    assert transit_fwhm_at_T(t, ref) == pytest.approx(expected, rel=1e-12)
