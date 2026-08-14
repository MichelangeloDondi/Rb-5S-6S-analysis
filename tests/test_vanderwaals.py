"""
M18 closure tests: the imaginary-frequency continuation and the C6 it yields.

The ground-state C6 is the validation path -- it is the only number here with a
literature value to check against, and getting it right is what licenses the
5S+6S number that has none.
"""

from __future__ import annotations

import math

import pytest

from rb5s6s.polarizability import LINES_5S, LINES_6S, E_6S_CM, alpha_5s
from rb5s6s.vanderwaals import (C6_RB2_GROUND_LIT_AU, alpha_imaginary,
                                beta_self_vdw, c6_5s5s, c6_5s6s,
                                c6_coefficient, mean_relative_speed)


def test_imaginary_axis_reduces_to_the_static_value_at_zero():
    """alpha(i*0) must equal the static valence sum -- the continuation cannot
    change the w=0 point."""
    static_valence = alpha_5s(0.0, tail=0.0, core=0.0)
    assert alpha_imaginary(LINES_5S, 0.0) == pytest.approx(static_valence, rel=1e-9)


def test_imaginary_axis_is_pole_free_and_decreasing_for_the_ground_state():
    """(dE^2 + w^2) has no zero, so alpha(i w) is smooth and falls monotonically
    for a state with only upward transitions. A pole here would mean the sign
    of the continuation was wrong."""
    vals = [alpha_imaginary(LINES_5S, w) for w in (0.0, 0.1, 0.5, 1.0, 5.0, 25.0)]
    assert all(a > b > 0 for a, b in zip(vals, vals[1:])), vals


def test_ground_state_c6_matches_literature_within_the_dropped_core():
    """The validation that licenses everything else: C6(5S+5S) against the
    Rb2 literature value. Valence-only, so it must land LOW -- by roughly the
    amount the missing core costs, not by an arbitrary amount."""
    c = c6_5s5s()
    assert c < C6_RB2_GROUND_LIT_AU, c
    assert abs(c / C6_RB2_GROUND_LIT_AU - 1.0) < 0.15, c


def test_c6_is_converged_in_the_integration_cutoff():
    """The integrand falls as 1/w^4 past the largest transition energy, so the
    result must not move with the cutoff. It DID move before core and tail were
    dropped (they are constants and never fall off) -- that bug is what this
    guards."""
    lo = c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM, w_max=2.0)
    hi = c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM, w_max=25.0)
    assert lo == pytest.approx(hi, rel=1e-3), (lo, hi)


def test_excited_state_c6_is_much_larger_than_the_ground_state():
    """6S is far more polarizable than 5S (5167 vs 319 static, the near-
    degenerate 6P), so its C6 must be larger by a comparable factor."""
    assert c6_5s6s() > 4 * c6_5s5s()


def test_beta_self_lands_on_the_kHz_scale_expected_for_a_van_der_Waals_S_S_pair():
    """The whole point: a COMPUTED expectation, not one borrowed from 7S.
    Both states are S, so there is no resonant dipole-dipole term and the
    coefficient must sit far below the D1 resonant value (69 kHz per 1e12,
    weller2011) while remaining on the kHz scale. The argument is the
    DIFFERENCE coefficient, upper pair minus lower pair, which is what the
    impact phase sees (Lewis 1980 eq. 2.39 and 4.13, adjudicated 2026-08-05
    in the module docstring)."""
    f = beta_self_vdw(c6_5s6s() - c6_5s5s(), 403.15, 1e12)
    assert 1e3 < f < 69e3, f


def test_beta_self_scales_as_the_impact_law_requires():
    """FWHM must be linear in density and go as Delta_C6^(2/5)."""
    c = c6_5s6s() - c6_5s5s()
    assert beta_self_vdw(c, 403.15, 2e12) == pytest.approx(
        2 * beta_self_vdw(c, 403.15, 1e12), rel=1e-9)
    assert beta_self_vdw(2 * c, 403.15) / beta_self_vdw(c, 403.15) == pytest.approx(
        2 ** 0.4, rel=1e-9)


def test_the_difference_coefficient_is_what_the_anchor_ratio_uses():
    """The 2026-08-05 correction, locked in. Subtracting the ground-pair term
    from both rungs lowers the scale factor, because the same number is taken
    off a smaller numerator and a larger denominator, so it must move the
    anchor DOWN and by a few per cent rather than by a factor. If a future
    edit reverts to the plain pair ratio this fires."""
    from rb5s6s.vanderwaals import beta_self_anchored
    r = beta_self_anchored()
    assert r["dc6_ratio"] < r["c6_ratio"], r
    assert r["dc6_ratio"] == pytest.approx(0.3128, rel=1e-3), r["dc6_ratio"]
    plain = r["beta7_measured_khz"] * r["c6_ratio"] ** 0.4
    assert 0.93 < r["beta6_khz"] / plain < 0.99, (r["beta6_khz"], plain)


def test_mean_relative_speed_uses_the_reduced_mass():
    """Two identical atoms: mu = m/2, so the relative speed is sqrt(2) times
    the single-atom mean speed. Getting this wrong shifts beta by v^0.6."""
    import rb5s6s.vanderwaals as V
    single = math.sqrt(8 * V.KB * 403.15 / (math.pi * V.M_RB87))
    assert mean_relative_speed(403.15) == pytest.approx(math.sqrt(2) * single, rel=1e-9)


def test_module_underpredicts_the_one_measured_nS_rate():
    """The external check this module lacked until Zameroski's 7S broadening
    rate was read off the held PDF. Run on 7S -- the only nS state in Rb with a
    measured self-broadening rate -- the absolute prediction sits ~18% low,
    just past the +-10-15% envelope the dropped core/tail and the mean-speed
    approximation already predict (docs/PREREGISTRATION_RESULTS.md
    Addendum 23). Lock the size in: if it moves a lot, something regressed."""
    from rb5s6s.vanderwaals import beta_self_anchored
    r = beta_self_anchored()
    assert 0.7 < r["prefactor_discrepancy"] < 0.95, r["prefactor_discrepancy"]
    assert r["beta7_measured_khz"] == pytest.approx(5.39, rel=0.02)


def test_anchored_beta_is_bracketed_by_its_two_inputs():
    """beta(6S) anchored = beta(7S)_measured * [dC6(6S)/dC6(7S)]^(2/5). Since
    C6(6S) < C6(7S), the result must sit BELOW the measured 7S rate -- the
    ordering the raw prediction appeared to violate before the prefactor error
    was isolated."""
    from rb5s6s.vanderwaals import beta_self_anchored
    r = beta_self_anchored()
    assert r["dc6_ratio"] < 1.0
    assert 0.0 < r["beta6_khz"] < r["beta7_measured_khz"]
    assert r["beta6_khz"] == pytest.approx(3.38, rel=0.05)


def test_record_bound_still_sits_well_above_the_anchored_expectation():
    """The conclusion that survives every route to an expected value: the
    archival bound (0.2-0.4 MHz per 1e12 cm^-3) is orders above it."""
    from rb5s6s.vanderwaals import beta_self_anchored
    b = beta_self_anchored()["beta6_khz"]
    assert 40 < 200.0 / b and 400.0 / b < 200
