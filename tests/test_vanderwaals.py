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
from rb5s6s.vanderwaals import (C6_RB2_GROUND_LIT_AU, LINDHOLM_FOLEY_PREFACTOR, branch_average, c6_exchange, exchange_signs,
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
    # 5.33, AND THE ROUTE TO IT IS THE PART UNDER TEST. The rate is a SLOPE
    # fitted over 353 to 438 K, so it has no single temperature; the effective
    # one is adopted at the centre of the beta the defensible weightings give
    # and its span is a budget row. This record read 403.15 K until
    # 2026-09-15 and then 393 K for one afternoon, the second being a table
    # note about a different experiment. Both are retracted, and the assert
    # pins the effective temperature rather than any cell temperature.
    assert r["beta7_measured_khz"] == pytest.approx(5.624, abs=0.005)
    # THE EFFECTIVE TEMPERATURE IS COMPUTED, NOT TYPED, and the assert pins the
    # distinction that makes it right: a weighted MEAN of T and the regression
    # LEVERAGE must differ on this input, because the vapour pressure is
    # exponential and a slope is carried by its hot end. 397 K, this record's
    # reading for one afternoon, came from the mean family and is not reachable
    # from the leverage one.
    from rb5s6s.vanderwaals import zameroski_effective_T
    assert r["zameroski_eff_t_k"] == pytest.approx(428.9, abs=0.5)
    assert all(zameroski_effective_T(w) > 400.0
               for w in ("unit", "inv_width2", "inv_p2"))
    assert r["t_factor"] == pytest.approx((403.15 / r["zameroski_eff_t_k"]) ** 0.3, rel=1e-12)


def test_anchored_and_first_principles_values_agree_and_are_bracketed():
    """beta(6S) anchored = beta(7S)_measured * [dC6(6S)/dC6(7S)]^(2/5) sits
    below the measured 7S rate, near 3.50 kHz per 1e12 cm^-3, and the
    first-principles value beside it agrees to better than 8 per cent -- and
    that agreement is NOT two routes confirming each other. It is the same
    computation with and without the experimental scale, so the gap IS the
    recipe's absolute error on the one state where it can be measured."""
    r = beta_self_anchored()
    assert r["dc6_ratio"] < 1.0
    assert 0.0 < r["beta6_khz"] < r["beta7_measured_khz"]
    assert r["beta6_khz"] == pytest.approx(3.497, abs=0.005)
    assert r["beta6_first_principles_khz"] == pytest.approx(r["beta6_khz"], rel=0.08)


def test_record_bound_still_sits_well_above_the_anchored_expectation():
    """The conclusion that survives every route to an expected value: the
    archival bound (tens of kHz per 1e12 cm^-3) is an order above it."""
    b = beta_self_anchored()["beta6_khz"]
    assert 40 < 200.0 / b and 400.0 / b < 200

def test_the_exchange_coefficient_is_computed_and_bracketed_over_the_untabulated_sign():
    """W1k physics finding F1: typed as a quarter of Delta C6, the exchange term is
    0.35 to 0.45 for 6S whichever way the 6P products point, because the 5P legs
    dominate; for 7S it is under 5 per cent. The anchor carries the branch average
    of each rung and moves 3.55 to 3.50, inside the envelope."""
    from rb5s6s.polarizability import LINES_5S, LINES_6S, LINES_7S, E_6S_CM, E_7S_CM
    d6 = c6_direct(LINES_5S, 0.0, LINES_6S, E_6S_CM) - c6_direct(LINES_5S, 0.0, LINES_5S, 0.0)
    d7 = c6_direct(LINES_5S, 0.0, LINES_7S, E_7S_CM) - c6_direct(LINES_5S, 0.0, LINES_5S, 0.0)
    f6 = [c6_exchange(LINES_5S, LINES_6S, E_6S_CM, s) / d6 for s in (1.0, -1.0)]
    f7 = [abs(c6_exchange(LINES_5S, LINES_7S, E_7S_CM, s) / d7) for s in (1.0, -1.0)]
    assert all(0.33 < f < 0.47 for f in f6), f6
    assert all(f < 0.05 for f in f7), f7
    assert branch_average(0.0) == 1.0 and 0.97 < branch_average(0.45) < 0.975
    # THE RULE FIXES THE 6P SIGN AND NOT THE REST (physics seat, tree e53355ad).
    # The assert that stood here, `signs == (1, -1, -1, 1)`, pinned a CONVENTION:
    # the 7P and 8P terms (0.069 and 0.017) sit inside the 9P-to-12P truncation
    # tail (0.02 to 0.05), so two patterns close and the chooser picking one of
    # them is arithmetic and not physics. What is licensed is the 6P sign, at
    # about fifty tail widths, and the insensitivity of everything downstream.
    s6 = exchange_signs(LINES_5S, LINES_6S, E_6S_CM)
    assert s6["signs"][0] == 1 and s6["signs"][1] == -1, s6
    assert s6["residual"] < 0.03 * s6["gauge_f_sum"] and s6["residual_all_positive"] > 2.0 * s6["gauge_f_sum"], s6
    assert c6_exchange(LINES_5S, LINES_6S, E_6S_CM) / d6 == pytest.approx(0.349, abs=0.005)
    r = beta_self_anchored()
    assert r["beta6_khz"] == pytest.approx(3.50, abs=0.01), r["beta6_khz"]
    assert r["beta6_khz"] < r["beta6_khz_no_exchange"] == pytest.approx(3.55, rel=0.01)



def test_the_budget_reconstructs_the_anchor_and_is_dominated_by_the_measurement():
    """The bar on beta_self, every row of it measured by displacing an input.

    FAILURE MODES THIS CATCHES. `beta_self_budget` re-evaluates the anchored
    expression in closed form, so it can drift away from `beta_self_anchored`
    silently and report a budget for a different number; the reconstruction
    assert inside it is the guard and this test is its plant. A row growing
    past the anchor's own share would mean the recipe had started to matter,
    which is a finding and not a tolerance. And the double-counted 5 per cent
    density term is pinned OUT: if the quadrature ever returns 11 per cent
    again, that term has come back.
    """
    from rb5s6s.vanderwaals import beta_self_budget
    b = beta_self_budget()
    a = beta_self_anchored()
    assert b["beta6_khz"] == pytest.approx(a["beta6_khz"], rel=1e-12)
    # the anchor measurement dominates and everything else is noise beside it
    anchor = b["terms_rel"]["anchor_measurement"]
    rest = math.sqrt(sum(v * v for k, v in b["terms_rel"].items()
                         if k != "anchor_measurement"))
    # THE SOURCE'S TOTAL, 13 and not 11: Table 3 prints 129 +- 13 where section
    # 2.5 prints +- 11, and sqrt(13^2 - 6.45^2 - 1.29^2) = 11.2 reproduces the
    # second from the first, so the two are the total and the fit interval.
    assert anchor == pytest.approx(13.0 / 129.0, rel=1e-6)
    # the conversion temperature is now the second row and was zero
    assert b["terms_rel"]["anchor_conversion_temperature"] > 0.02
    assert rest < 0.04, b["terms_rel"]
    assert 0.103 < b["rel"] < 0.110, b["rel"]
    assert b["err_khz"] == pytest.approx(0.372, abs=0.01)
    # AT THE LEVERAGE-WEIGHTED TEMPERATURE THE RECIPE REPRODUCES THE ONE
    # MEASURED nS RATE IN RUBIDIUM TO BETTER THAN ONE PER CENT. Every apparent
    # discrepancy this record reported during 2026-09-15 -- 4 per cent, then
    # 6.1, then 5.4 -- was its own conversion, not the physics.
    assert abs(b["recipe_scale_error_on_7s"]) < 0.02, b["recipe_scale_error_on_7s"]


def test_the_committed_theory_row_matches_the_module():
    """The SSOT edge: results/beta_self_theory.csv against the package.

    The producer is the only writer and `verify_results_fresh` grades it, but
    that proves the CSV matches its producer and not that either matches the
    physics. This asserts the third edge, the committed cell against the module
    a reader would call, which is what a stale quote resolves through.
    """
    import csv as _csv
    from pathlib import Path
    from rb5s6s.vanderwaals import beta_self_budget
    path = Path(__file__).resolve().parents[1] / "results" / "beta_self_theory.csv"
    rows = {(r["case"], r["quantity"]): r for r in _csv.DictReader(path.open())}
    b = beta_self_budget()
    cell = rows[("beta_self_6s", "anchored")]
    assert float(cell["value"]) == pytest.approx(b["beta6_khz"], abs=5e-5)
    assert float(cell["err"]) == pytest.approx(b["err_khz"], abs=5e-5)
    # the removed double count stays on the record as ARTIFACT, so that a
    # future budget cannot quietly re-adopt it
    # the ARTIFACT row is the RETRACTION of this record's own deletion, kept so
    # the removed term cannot be removed again
    assert rows[("budget", "retracted_double_count_claim")]["status"] == "ARTIFACT"
