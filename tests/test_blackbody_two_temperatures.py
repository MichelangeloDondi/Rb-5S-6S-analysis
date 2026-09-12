"""The radiation temperature is the walls', not the atoms'.

A heated cell is its own oven, so the two coincide and every committed cell row
is unaffected. A MOT holds atoms at 150 microkelvin inside a chamber at ROOM
TEMPERATURE, and a cold hollow-core fibre is the same case, so a twin that
passes the kinetic temperature computes the blackbody shift of a sample at
absolute zero. These guards fail if that conflation returns.

The switch is checked in BOTH directions, because a no-op switch that reports
success is the trap `run_three_channel_forecast` already fell into: the default
must be byte-identical AND a passed temperature must change the trace.
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import blackbody as B
from rb5s6s import platforms as P


def _kw():
    return dict(positions={"4192": 0.0}, shares={"4192": 1.0}, gamma_coll=0.55,
                sigma_laser_fwhm=1.6, transit_fwhm=0.9575, power_max_w=1.0,
                cycles_at_max=1.0, drift_mhz_total=0.0, noise_frac_bright=0.004,
                adc_levels=4096)


_LAYERS = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
           "drift": False, "quantise": True, "randomise": False}


def test_the_default_radiation_temperature_is_byte_identical():
    """t_bbr_k=None must reproduce the cell's old behaviour exactly, or every
    committed twin CSV silently moved."""
    from rb5s6s.forecast import build_world_trace
    a = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), _LAYERS, **_kw())[1]
    b = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), _LAYERS,
                          t_bbr_k=None, **_kw())[1]
    assert np.array_equal(a, b)
    # and passing the cell's OWN wall temperature explicitly is the same thing
    c = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), _LAYERS,
                          t_bbr_k=403.15, **_kw())[1]
    assert np.array_equal(a, c)


def test_a_room_temperature_environment_changes_the_trace():
    """The other half: a switch that does nothing reports success."""
    from rb5s6s.forecast import build_world_trace
    a = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), _LAYERS, **_kw())[1]
    cold = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), _LAYERS,
                             t_bbr_k=293.15, **_kw())[1]
    assert not np.array_equal(a, cold)


def test_the_cell_minus_cold_differential_is_about_a_hundred_and_twenty_hertz():
    """The number the two-temperature repair exists to make representable."""
    cell = B.shift_hz(403.15)
    lo, hi = B.shift_envelope_hz(293.15)
    assert 160.0 < cell < 162.0
    assert 40.0 < lo < 41.0 and 44.5 < hi < 45.5
    assert 115.0 < cell - hi and cell - lo < 121.5


def test_the_room_temperature_shift_is_flagged_as_an_extrapolation():
    assert B.is_extrapolated(293.15)
    assert not B.is_extrapolated(403.15)


def test_inside_the_fitted_range_the_envelope_is_the_committed_error_bar():
    v, e = B.shift_hz(403.15, with_error=True)
    lo, hi = B.shift_envelope_hz(403.15)
    assert lo == pytest.approx(v - e) and hi == pytest.approx(v + e)


def test_the_envelope_brackets_the_single_valued_shift_below_the_fitted_range():
    """The fitted exponent is the LOW end below the range, so quoting shift_hz
    alone there understates the shift. That direction flatters a cold platform,
    which is why it is planted."""
    lo, hi = B.shift_envelope_hz(293.15)
    assert lo == pytest.approx(B.shift_hz(293.15))
    assert hi > lo


def test_a_kinetic_temperature_is_refused_as_a_radiation_temperature():
    """The wrong answer here is small, plausible and silent, so it raises."""
    for name in ("mot", "molasses", "hcpcf_cold", "onf"):
        p = P.PLATFORMS[name]
        assert p.temperature_k < P.ENCLOSURE_FLOOR_K, name
        assert P.bbr_temperature_k(p) == pytest.approx(293.15), name
    # strip the declaration and the refusal must fire
    import dataclasses
    bare = dataclasses.replace(P.PLATFORMS["mot"], t_bbr_k=None)
    with pytest.raises(ValueError, match="kinetic temperature"):
        P.bbr_temperature_k(bare)


def test_a_heated_cell_is_its_own_enclosure():
    for name in ("cell_130C", "cell_130C_tight", "hcpcf_warm"):
        p = P.PLATFORMS[name]
        assert P.bbr_temperature_k(p) == pytest.approx(p.temperature_k), name
