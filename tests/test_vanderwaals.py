"""
M18 closure tests: the pair coefficients, the impact prefactor and the anchor.

The ground-state C6 is the validation path -- it is the only number here with a
literature value to check against, and getting it right is what licenses the
5S+6S number that has none. Since 2026-09-14 the pair coefficients come from the
second-order sum with signed denominators, and the imaginary-frequency integral
is planted as the special case it is (exact when every transition is upward).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from rb5s6s._compat import trapezoid
from rb5s6s.polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM, alpha_5s
from rb5s6s.vanderwaals import (C6_RB2_GROUND_LIT_AU, LINDHOLM_FOLEY_PREFACTOR, branch_average, c6_exchange,
                                LINDHOLM_FOLEY_PREFACTOR_QUOTED, alpha_imaginary,
                                beta_self_anchored, beta_self_vdw, c6_5s5s, c6_5s6s,
                                c6_5s7s, c6_coefficient, c6_direct, impact_prefactors,
                                mean_relative_speed, speed_average_factor)


def test_imaginary_axis_reduces_to_the_static_value_at_zero():
    """alpha(i*0) must equal the static valence sum -- the continuation cannot
    change the w=0 point."""
    static_valence = alpha_5s(0.0, tail=0.0, core=0.0)
    assert alpha_imaginary(LINES_5S, 0.0) == pytest.approx(static_valence, rel=1e-9)


def test_imaginary_axis_is_pole_free_and_decreasing_for_the_ground_state():
    """(dE^2 + w^2) has no zero, so alpha(i w) is smooth and falls monotonically
    for a state with only upward transitions."""
    vals = [alpha_imaginary(LINES_5S, w) for w in (0.0, 0.1, 0.5, 1.0, 5.0, 25.0)]
    assert all(a > b > 0 for a, b in zip(vals, vals[1:])), vals


def test_ground_state_c6_matches_literature_within_the_dropped_core():
    """The validation that licenses everything else: C6(5S+5S) against the
    Rb2 literature value. Valence-only, so it must land LOW -- by roughly the
    amount the missing core costs, not by an arbitrary amount."""
    c = c6_5s5s()
    assert c < C6_RB2_GROUND_LIT_AU, c
    assert abs(c / C6_RB2_GROUND_LIT_AU - 1.0) < 0.15, c


def test_the_direct_sum_equals_the_integral_when_every_transition_is_upward():
    """The Casimir-Polder identity holds for positive denominators, so on the
    ground pair the two routes must agree to the integral's own precision."""
    assert c6_direct(LINES_5S, 0.0, LINES_5S, 0.0) == pytest.approx(
        c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0), rel=1e-6)


def test_the_integral_misses_the_downward_terms_by_the_sign_of_their_denominator():
    """THE PLANT of 2026-09-14. For a < 0 < b the identity returns -1/(|a|+b)
    where the sum has 1/(b-|a|); on 6S (downward to 5P) the integral is low by
    a factor near 1.9, and on 7S (downward to 5P and 6P) by near 1.9 as well.
    Locked in as a RATIO so that a change of the line tables does not fire it
    and a reversion to the integral does."""
    r6 = c6_direct(LINES_5S, 0.0, LINES_6S, E_6S_CM) / c6_coefficient(LINES_5S, 0.0, LINES_6S, E_6S_CM)
    r7 = c6_direct(LINES_5S, 0.0, LINES_7S, E_7S_CM) / c6_coefficient(LINES_5S, 0.0, LINES_7S, E_7S_CM)
    assert 1.7 < r6 < 2.1, r6
    assert 1.7 < r7 < 2.1, r7
    # and the sign error is reproduced by hand on one term: a = -0.03, b = 0.06
    a, b = -0.03, 0.06
    w = np.linspace(1e-8, 50.0, 400000)
    integral = 2.0 / math.pi * trapezoid(a * b / ((a * a + w * w) * (b * b + w * w)), w)
    assert integral == pytest.approx(-1.0 / (abs(a) + b), rel=1e-3)
    assert integral != pytest.approx(1.0 / (a + b), rel=0.5)


def test_c6_is_converged_in_the_integration_cutoff():
    """The integrand falls as 1/w^4 past the largest transition energy, so the
    result must not move with the cutoff (core and tail are constants and
    never fall off -- that bug is what this guards)."""
    lo = c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0, w_max=2.0)
    hi = c6_coefficient(LINES_5S, 0.0, LINES_5S, 0.0, w_max=25.0)
    assert lo == pytest.approx(hi, rel=1e-3), (lo, hi)


def test_excited_state_c6_is_much_larger_than_the_ground_state():
    """6S is far more polarizable than 5S (5167 vs 319 static, the near-
    degenerate 6P), so its pair coefficient must be larger by a comparable
    factor, and 7S larger again."""
    assert c6_5s6s() > 4 * c6_5s5s()
    assert c6_5s7s() > c6_5s6s()


def test_the_impact_prefactor_is_derived_and_the_quoted_one_was_a_per_cent_high():
    """The closed form on Gamma(-2/5): HWHM 4.0414, FWHM 8.0828, shift over
    HWHM tan(pi/5). The numerical phase-shift integral must reproduce the
    closed form, and the literature rounding the module carried is 1.0 per
    cent above it."""
    p = impact_prefactors()
    assert p["fwhm"] == pytest.approx(8.0828, abs=2e-4)
    assert p["shift_over_hwhm"] == pytest.approx(math.tan(0.2 * math.pi), rel=1e-9)
    assert LINDHOLM_FOLEY_PREFACTOR == p["fwhm"]
    assert 1.005 < LINDHOLM_FOLEY_PREFACTOR_QUOTED / p["fwhm"] < 1.012
    u = np.linspace(0.2, 400.0, 2_000_000)           # b in units of (3 pi C6 / 8 hbar v)^(1/5)
    i_c = trapezoid((1.0 - np.cos(u ** -5.0)) * u, u) + 0.5 * 0.2 ** 2   # the b < 0.2 core: 1 - cos averages to 1
    assert 2.0 * math.pi * i_c * (3.0 * math.pi / 8.0) ** 0.4 == pytest.approx(p["hwhm"], rel=2e-3)


def test_the_speed_average_is_a_derived_factor_below_one():
    """<v^(3/5)>/vbar^(3/5) over Maxwell relative speeds is 0.9775; at p = 1
    the two agree exactly, which pins the normalisation."""
    assert speed_average_factor(1.0) == pytest.approx(1.0, rel=1e-9)
    assert speed_average_factor(0.6) == pytest.approx(0.9775, abs=5e-4)


def test_beta_self_lands_on_the_kHz_scale_expected_for_a_van_der_Waals_S_S_pair():
    """A COMPUTED expectation: both states are S, so there is no resonant
    dipole-dipole term and the coefficient sits far below the D1 resonant
    value (69 kHz per 1e12, weller2011) while remaining on the kHz scale.
    The argument is the DIFFERENCE coefficient, upper pair minus lower pair."""
    f = beta_self_vdw(c6_5s6s() - c6_5s5s(), 403.15, 1e12)
    assert 1e3 < f < 69e3, f


def test_beta_self_scales_as_the_impact_law_requires():
    """FWHM must be linear in density and go as Delta_C6^(2/5)."""
    c = c6_5s6s() - c6_5s5s()
    assert beta_self_vdw(c, 403.15, 2e12) == pytest.approx(2 * beta_self_vdw(c, 403.15, 1e12), rel=1e-9)
    assert beta_self_vdw(2 * c, 403.15) / beta_self_vdw(c, 403.15) == pytest.approx(2 ** 0.4, rel=1e-9)


def test_the_difference_coefficient_is_what_the_anchor_ratio_uses():
    """The 2026-08-05 correction, locked in on the direct sums: subtracting the
    ground-pair term from both rungs lowers the scale factor by a few per cent."""
    r = beta_self_anchored()
    assert r["dc6_ratio"] < r["c6_ratio"], r
    assert r["dc6_ratio"] == pytest.approx(0.3166, rel=1e-3), r["dc6_ratio"]
    plain = r["beta7_measured_khz"] * r["c6_ratio"] ** 0.4
    assert 0.93 < r["beta6_khz"] / plain < 0.99, (r["beta6_khz"], plain)


def test_mean_relative_speed_uses_the_reduced_mass():
    """Two identical atoms: mu = m/2, so the relative speed is sqrt(2) times
    the single-atom mean speed."""
    import rb5s6s.vanderwaals as V
    single = math.sqrt(8 * V.KB * 403.15 / (math.pi * V.M_RB87))
    assert mean_relative_speed(403.15) == pytest.approx(math.sqrt(2) * single, rel=1e-9)


def test_first_principles_rate_agrees_with_the_one_measured_nS_rate():
    """The independent test: on 7S, the only nS state in Rb with a measured
    self-broadening rate, the first-principles prediction now sits within
    Zameroski's own 8.5 per cent bar (it read 18 per cent low while the
    integral undercounted the downward terms). Locked as a band, so a
    regression in either direction fires."""
    r = beta_self_anchored()
    assert 0.92 < r["prefactor_discrepancy"] < 1.09, r["prefactor_discrepancy"]
    assert r["beta7_measured_khz"] == pytest.approx(5.39, rel=0.02)


def test_anchored_and_first_principles_values_agree_and_are_bracketed():
    """beta(6S) anchored = beta(7S)_measured * [dC6(6S)/dC6(7S)]^(2/5) sits
    below the measured 7S rate, near 3.40 kHz per 1e12 cm^-3, and the
    first-principles value beside it agrees to better than 5 per cent."""
    r = beta_self_anchored()
    assert r["dc6_ratio"] < 1.0
    assert 0.0 < r["beta6_khz"] < r["beta7_measured_khz"]
    assert r["beta6_khz"] == pytest.approx(3.33, rel=0.03)
    assert r["beta6_first_principles_khz"] == pytest.approx(r["beta6_khz"], rel=0.05)


def test_record_bound_still_sits_well_above_the_anchored_expectation():
    """The conclusion that survives every route to an expected value: the
    archival bound (tens of kHz per 1e12 cm^-3) is an order above it."""
    b = beta_self_anchored()["beta6_khz"]
    assert 40 < 200.0 / b and 400.0 / b < 200

def test_the_exchange_coefficient_is_computed_and_bracketed_over_the_untabulated_sign():
    """W1k physics finding F1: typed as a quarter of Delta C6, the exchange term is
    0.35 to 0.45 for 6S whichever way the 6P products point, because the 5P legs
    dominate; for 7S it is under 5 per cent. The anchor carries the branch average
    of each rung and moves from 3.40 to 3.31-3.35, inside the envelope."""
    from rb5s6s.polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM
    d6 = c6_direct(LINES_5S, 0.0, LINES_6S, E_6S_CM) - c6_direct(LINES_5S, 0.0, LINES_5S, 0.0)
    d7 = c6_direct(LINES_5S, 0.0, LINES_7S, E_7S_CM) - c6_direct(LINES_5S, 0.0, LINES_5S, 0.0)
    f6 = [c6_exchange(LINES_5S, LINES_6S, E_6S_CM, s) / d6 for s in (1.0, -1.0)]
    f7 = [abs(c6_exchange(LINES_5S, LINES_7S, E_7S_CM, s) / d7) for s in (1.0, -1.0)]
    assert all(0.33 < f < 0.47 for f in f6), f6
    assert all(f < 0.05 for f in f7), f7
    assert branch_average(0.0) == 1.0 and 0.97 < branch_average(0.45) < 0.975
    r = beta_self_anchored()
    assert 3.30 < r["beta6_khz"] < 3.36, r["beta6_khz"]
    assert r["beta6_khz"] < r["beta6_khz_no_exchange"] == pytest.approx(3.40, rel=0.01)

