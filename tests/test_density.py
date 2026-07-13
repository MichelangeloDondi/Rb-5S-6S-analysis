"""
Tests for the Rb vapor-density model (rb5s6s/density.py).

Pin the correlation against known Rb vapor facts so a typo in a coefficient
can never silently move beta_self.
"""

import numpy as np
import pytest

from rb5s6s.density import (number_density_cm3, vapor_pressure_torr,
                            density_units, RB_MELT_C)


def test_density_order_of_magnitude_100C():
    # Rb at 100 C: N ~ few x 10^12 cm^-3 (standard vapor-cell figure).
    N = number_density_cm3(100.0)
    assert 1e12 < N < 2e13, N


def test_density_rises_about_50x_across_sweep():
    # The physics lever arm: N(130 C)/N(70 C) ~ 45-55x (brief says ~45x).
    ratio = number_density_cm3(130.0) / number_density_cm3(70.0)
    assert 40.0 < ratio < 65.0, ratio


def test_density_monotonic_increasing():
    T = np.array([70.0, 90.0, 110.0, 130.0])
    N = number_density_cm3(T)
    assert np.all(np.diff(N) > 0)


def test_pressure_positive_and_small():
    # sub-mtorr to few-mtorr across the sweep
    P = vapor_pressure_torr(np.array([70.0, 130.0]))
    assert P[0] < P[1] and P[0] > 1e-6 and P[1] < 1e-2


def test_density_units_helper_consistent():
    assert np.isclose(density_units(110.0), number_density_cm3(110.0) / 1e12)


def test_d1_optical_depth_thick_and_isotope_ratio():
    from rb5s6s.density import d1_optical_depth_per_cm
    # cell is optically THICK on D1 at high density (tau/cm >> 1 at 130 C)
    assert d1_optical_depth_per_cm(130.0, 85) > 100.0
    # rises with T, and 85Rb has ~2.6x the absorbers of 87Rb (abundance ratio)
    assert d1_optical_depth_per_cm(130.0, 85) > d1_optical_depth_per_cm(70.0, 85)
    ratio = d1_optical_depth_per_cm(110.0, 85) / d1_optical_depth_per_cm(110.0, 87)
    assert abs(ratio - 0.7217 / 0.2783) < 1e-6


def test_below_melting_raises():
    with pytest.raises(ValueError):
        number_density_cm3(RB_MELT_C - 5.0)
