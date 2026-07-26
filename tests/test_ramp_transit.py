"""M19 -- the ramp survives atomic motion, so the ramp/transit convolution is
legitimate. See rb5s6s/ramp_transit.py for why this is not self-evident."""

import numpy as np
import pytest

from rb5s6s.ramp_transit import (
    moving_atom_moments,
    TRIANGLE_MEAN_OVER_S0,
    TRIANGLE_EXCESS_VAR_OVER_MEAN_SQ,
)
from rb5s6s.lineshape import ramp_moment_contributions


def test_transit_scale_is_the_expected_fraction_of_the_beam():
    """Sanity on the units: with w = v = 1 the pure-transit FWHM is ~0.53, so
    the s0 values below really do straddle it."""
    m = moving_atom_moments(0.2, n_b=201, n_t=20001)
    assert 0.4 < m["transit_fwhm"] < 0.7


@pytest.mark.parametrize("s0", [0.05, 0.5, 2.0])
def test_moving_atoms_reproduce_the_static_ramp_moments(s0):
    """The load-bearing check. Atoms crossing the beam, with the shift
    integrated along each trajectory and NO quasi-static approximation, give
    the same first two moments as the static triangle -- non-adiabatic
    (s0 << transit width) and adiabatic (s0 >> it) alike."""
    m = moving_atom_moments(s0, n_b=301, n_t=40001)
    assert m["mean_over_s0"] == pytest.approx(TRIANGLE_MEAN_OVER_S0, rel=0.01)
    assert m["excess_var_over_mean_sq"] == pytest.approx(
        TRIANGLE_EXCESS_VAR_OVER_MEAN_SQ, rel=0.02)


@pytest.mark.slow
def test_invariance_holds_across_the_whole_adiabaticity_range():
    """Sweep s0 over ~40x. If motion washed the ramp out at all, the moments
    would DRIFT with s0/transit_width -- that drift is the thing being
    excluded, so scatter across the sweep matters more than any single value."""
    means, variances = [], []
    for s0 in (0.05, 0.2, 0.5, 1.0, 2.0):
        m = moving_atom_moments(s0, n_b=401, n_t=60001)
        means.append(m["mean_over_s0"])
        variances.append(m["excess_var_over_mean_sq"])
    assert np.ptp(means) < 0.005, f"mean drifts with adiabaticity: {means}"
    assert np.ptp(variances) < 0.005, f"variance drifts: {variances}"
    assert np.mean(means) == pytest.approx(TRIANGLE_MEAN_OVER_S0, rel=0.01)


def test_agrees_with_the_shipped_ramp_moment_predictions():
    """Close the loop against the functions the fit actually calls, rather
    than against the hard-coded triangle constants."""
    s0_mhz = 0.5
    pred = ramp_moment_contributions(s0_mhz, z_ratio=1e-6)
    assert pred["pull"] / s0_mhz == pytest.approx(TRIANGLE_MEAN_OVER_S0, rel=1e-3)
    assert pred["excess_var"] / pred["pull"] ** 2 == pytest.approx(
        TRIANGLE_EXCESS_VAR_OVER_MEAN_SQ, rel=1e-3)


def test_excess_variance_is_quadratic_in_the_shift():
    """Guard on the transit subtraction. The RATIO excess_var/mean^2 is
    scale-free, so it cannot detect a mis-subtracted baseline; the absolute
    excess variance can, because the ramp contributes at order s0^2 and a
    leaked transit baseline would contribute at order s0^0. Quadrupling s0
    must quadruple the excess variance four-fold, not shift it by a constant."""
    lo = moving_atom_moments(0.25, n_b=201, n_t=20001, nu_window=6.0)
    hi = moving_atom_moments(1.00, n_b=201, n_t=20001, nu_window=6.0)
    assert hi["excess_var"] / lo["excess_var"] == pytest.approx(16.0, rel=0.05)


def test_standing_wave_fringes_do_not_move_the_pull():
    """The retro geometry is a standing wave. The fringe modulates the shift
    over the full lambda/2 period but not the Doppler-free coupling, so the
    pull must be untouched in BOTH limits -- an atom sweeping fringes fast
    (large v_z) and one frozen at a single fringe phase (small v_z). This is
    the fringe-immunity of the mean that constants.py asserts and M15 builds
    on, checked here from the trajectory rather than from the argument."""
    swept = moving_atom_moments(0.5, n_b=121, n_t=60001, t_max=6.0,
                                fringe_per_transit=113.0)
    frozen = moving_atom_moments(0.5, n_b=121, n_t=30001,
                                 frozen_fringe_phases=16)
    for m in (swept, frozen):
        assert m["mean_over_s0"] == pytest.approx(TRIANGLE_MEAN_OVER_S0, rel=0.01)


def test_fringe_on_the_coupling_would_be_detected():
    """Guard on the physics above, not on the code path. Putting the fringe on
    the coupling as well as the shift -- the natural mistake, and one made once
    here -- inflates the frozen-fringe pull by <u^3>/<u^2> = 5/3 for
    u = 2cos^2(phi). Assert the shipped result is NOT that value, so the two can
    never be silently swapped."""
    m = moving_atom_moments(0.5, n_b=121, n_t=30001, frozen_fringe_phases=16)
    wrong = TRIANGLE_MEAN_OVER_S0 * 5.0 / 3.0
    assert abs(m["mean_over_s0"] - wrong) > 0.2


def test_maxwell_boltzmann_speed_mixture_inherits_the_moments():
    """Real atoms have a thermal spread of transverse speeds, not one speed.
    Every speed class shares the mean and the ramp variance and differs only in
    transit width, so the mixture must inherit both."""
    rng = np.random.default_rng(11)
    v = np.hypot(rng.normal(0, 1, 4000), rng.normal(0, 1, 4000))
    sel = rng.choice(v, size=10, p=v / v.sum())      # crossing-flux weighted
    m = moving_atom_moments(0.5, n_b=101, n_t=30001, speeds=sel)
    assert m["mean_over_s0"] == pytest.approx(TRIANGLE_MEAN_OVER_S0, rel=0.015)
    assert m["excess_var_over_mean_sq"] == pytest.approx(
        TRIANGLE_EXCESS_VAR_OVER_MEAN_SQ, rel=0.03)
