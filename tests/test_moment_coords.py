"""Tests for `rb5s6s.moment_coords` (C6c's coordinate infrastructure, plan A100, A121, A129, rule W1).

Every test is fast (synthetic traces, no disk, no repository data) and each is pinned to a SOURCED
number where the record already has one (F283's ramp anchors and S0 powers, F284's Hartlap worked
example) rather than to a number invented for the test alone.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.stats import multivariate_normal

from rb5s6s._compat import trapezoid
from rb5s6s.moments import windowed_moments
from rb5s6s.moment_coords import (
    Coordinate,
    CoordinateTrial,
    NAMED_ANCHOR,
    build_catalogue,
    cross_product_estimate,
    dodelson_schneider_factor,
    hartlap_factor,
    moment_block_nll,
    raw_window_moment,
    replica_covariance,
    s0_w0_power,
    select_coordinates,
    shrink_to_diagonal,
    tent_window_moment,
    window_derivative,
    windowed_moments_fixed_centre,
)


# ========================================================================================= (a) =====
# windowed_moments_fixed_centre: against closed forms, and against windowed_moments' own convention
# ======================================================================================================

def _gaussian_truncated_central_moment(sigma: float, half_width: float, order: int) -> float:
    """The EXACT (closed-form, via a two-term recursion from integration by parts) central moment of
    a Gaussian exp(-x^2/(2 sigma^2)) truncated to [-W, W] and centred on its own peak at 0 -- since the
    window is symmetric about the peak, the central and raw moments coincide.

    J_n = integral_{-W}^{W} x^n exp(-x^2/(2 sigma^2)) dx satisfies, by parts (u = x^{n-1}, dv = x
    exp(-x^2/(2 sigma^2)) dx = -sigma^2 d[exp(-x^2/(2 sigma^2))]):
        J_n = -2 sigma^2 W^{n-1} exp(-W^2/(2 sigma^2)) + sigma^2 (n-1) J_{n-2}   (n even, n >= 2)
        J_0 = sigma sqrt(2 pi) erf(W / (sigma sqrt(2)))
        J_n = 0                                                                  (n odd, symmetric limits)
    and the normalised central moment is J_n / J_0.
    """
    if order % 2 == 1:
        return 0.0
    w = float(half_width)
    j = sigma * math.sqrt(2 * math.pi) * math.erf(w / (sigma * math.sqrt(2)))
    j0 = j
    for n in range(2, order + 1, 2):
        j = -2 * sigma ** 2 * w ** (n - 1) * math.exp(-w ** 2 / (2 * sigma ** 2)) + sigma ** 2 * (n - 1) * j
    return j / j0


def _lorentzian_truncated_central_moment(gamma: float, half_width: float, order: int) -> float:
    """The EXACT central moment of a Lorentzian gamma^2/(x^2+gamma^2) truncated to [-W, W] and centred
    on its own peak at 0, by the polynomial-division recursion x^{2k}/(x^2+gamma^2) = x^{2k-2} -
    gamma^2 x^{2k-2}/(x^2+gamma^2), integrated termwise:
        K_0 = (2/gamma) atan(W/gamma)
        K_k = 2 W^{2k-1}/(2k-1) - gamma^2 K_{k-1}                                (k >= 1)
    and the normalised central moment of order 2k is K_k / K_0 (the gamma^2 that multiplies both the
    numerator and K_0 cancels).
    """
    if order % 2 == 1:
        return 0.0
    w = float(half_width)
    k_top = order // 2
    k = (2.0 / gamma) * math.atan(w / gamma)
    k0 = k
    for j in range(1, k_top + 1):
        k = 2.0 * w ** (2 * j - 1) / (2 * j - 1) - gamma ** 2 * k
    return k / k0


def test_fixed_centre_moments_gaussian_against_closed_form():
    sigma = 3.0
    nu = np.linspace(-30.0, 30.0, 12001)
    y = np.exp(-0.5 * (nu / sigma) ** 2)
    half_width = 8.0
    values, info = windowed_moments_fixed_centre(nu, y, 0.0, [half_width], orders=(1, 2, 3, 4, 6))
    assert info[half_width]["in_span"] == 1.0
    for order in (2, 4, 6):
        want = _gaussian_truncated_central_moment(sigma, half_width, order)
        got = values[half_width][order]
        assert got == pytest.approx(want, rel=2e-4), f"order {order}: got {got}, closed form {want}"
    for order in (1, 3):
        assert abs(values[half_width][order]) < 1e-6, f"odd order {order} should vanish by symmetry"


def test_fixed_centre_moments_lorentzian_against_closed_form():
    gamma = 2.0
    nu = np.linspace(-60.0, 60.0, 24001)
    y = gamma ** 2 / (nu ** 2 + gamma ** 2)
    half_width = 7.0
    values, info = windowed_moments_fixed_centre(nu, y, 0.0, [half_width], orders=(1, 2, 3, 4))
    assert info[half_width]["in_span"] == 1.0
    for order in (2, 4):
        want = _lorentzian_truncated_central_moment(gamma, half_width, order)
        got = values[half_width][order]
        assert got == pytest.approx(want, rel=2e-4), f"order {order}: got {got}, closed form {want}"
    for order in (1, 3):
        assert abs(values[half_width][order]) < 1e-6, f"odd order {order} should vanish by symmetry"


def test_fixed_centre_agrees_with_windowed_moments_at_its_own_converged_centre():
    """windowed_moments self-centres on the window's own first moment; windowed_moments_fixed_centre,
    called with THAT centre held fixed, must reproduce the same central moments -- the equivalence
    the module docstring promises. Same trace and window as the validated prototype's own self-test
    (private/cache/plan_2026-09-16/p18_observable_space_v2.py, lines ~561-568), whose 1e-9 tolerance is
    reused here."""
    nu = np.linspace(-40.0, 40.0, 1601)
    y0 = np.exp(-0.5 * (nu / 4.0) ** 2)
    mu_self, info_self = windowed_moments(nu, y0, 6.0, orders=(1, 2, 3, 4), baseline=None)
    centre = info_self["centre"]
    values, info_fixed = windowed_moments_fixed_centre(nu, y0, centre, [6.0], orders=(1, 2, 3, 4))
    assert info_fixed[6.0]["centre"] == centre
    for order in (2, 3, 4):
        assert values[6.0][order] == pytest.approx(mu_self[order], abs=1e-9), (
            f"order {order}: fixed-centre {values[6.0][order]} vs self-centred {mu_self[order]}")


def test_fixed_centre_refuses_a_window_reaching_past_the_trace():
    nu = np.linspace(-10.0, 10.0, 501)
    y = np.exp(-0.5 * (nu / 2.0) ** 2)
    values, info = windowed_moments_fixed_centre(nu, y, 0.0, [10.5], orders=(2,))
    assert info[10.5]["in_span"] == 0.0
    assert math.isnan(values[10.5][2])


def test_window_derivative_matches_finite_difference_of_raw_window_moment():
    """F297's closed form dM_n/dW = W^n [f(c+W) + (-1)^n f(c-W)] against a plain central finite
    difference of raw_window_moment itself -- an independent (if less elegant) way to the same
    derivative, so this checks F297's algebra rather than re-deriving the same code path."""
    nu = np.linspace(-30.0, 30.0, 6001)
    y = np.exp(-0.5 * (nu / 3.0) ** 2) + 0.15 * np.exp(-0.5 * ((nu - 4.0) / 1.5) ** 2)
    centre, w, h = 0.7, 6.0, 1e-3
    for order in (2, 3, 4):
        analytic = window_derivative(nu, y, centre, w, order)
        fd = (raw_window_moment(nu, y, centre, w + h, order)
              - raw_window_moment(nu, y, centre, w - h, order)) / (2 * h)
        assert analytic == pytest.approx(fd, rel=1e-4), f"order {order}: {analytic} vs finite diff {fd}"


def test_tent_window_moment_is_the_integral_of_raw_window_moment_over_w():
    """F297: 'the integral of M_n over W from 0 to W_max is the n-th moment under a TENT window' --
    checked as a Fubini identity between tent_window_moment's direct quadrature and a literal
    trapezoid sum of raw_window_moment over a grid of W."""
    nu = np.linspace(-30.0, 30.0, 6001)
    y = np.exp(-0.5 * (nu / 3.0) ** 2)
    centre, w_max = 0.0, 8.0
    for order in (2, 3):
        direct = tent_window_moment(nu, y, centre, w_max, order, normalize=False)
        ws = np.linspace(1e-4, w_max, 800)
        raw = np.array([raw_window_moment(nu, y, centre, w, order) for w in ws])
        via_grid = trapezoid(raw, ws)
        assert direct == pytest.approx(via_grid, rel=5e-3), f"order {order}: {direct} vs grid sum {via_grid}"


# ========================================================================================= (b) =====
# cross_product_estimate
# ======================================================================================================

def test_cross_product_estimate_unbiased_where_the_squared_estimator_is_not():
    rng = np.random.default_rng(20260922)
    mu, sigma, r = 5.0, 2.0, 40000
    a = mu + sigma * rng.standard_normal(r)
    b = mu + sigma * rng.standard_normal(r)

    naive = float(np.mean(a ** 2))                 # targets mu^2 + sigma^2 (biased)
    cross, cross_se = cross_product_estimate(a, b)  # targets mu^2 (unbiased)

    truth = mu ** 2
    naive_bias = naive - truth
    cross_bias = cross - truth
    assert abs(cross_bias) < abs(naive_bias), (
        f"cross-product bias {cross_bias:.4g} should be smaller than the naive squared bias {naive_bias:.4g}")
    assert naive_bias == pytest.approx(sigma ** 2, rel=0.05), "the naive bias should match Var(a) = sigma^2"
    assert abs(cross_bias) < 5 * cross_se, "the cross estimate should sit within a few SE of the truth"


def test_cross_product_estimate_exact_on_noiseless_replicas():
    a = np.full(10, 3.0)
    b = np.full(10, 3.0)
    est, se = cross_product_estimate(a, b)
    assert est == pytest.approx(9.0, abs=1e-12)
    assert se == pytest.approx(0.0, abs=1e-12)


def test_cross_product_estimate_generalises_to_three_replicas():
    """mu2^3-style denominators pair more than two independent replicas (A100.1's own example
    generalised, F284 point 2's 'the same for ... the mu2^3 denominator')."""
    rng = np.random.default_rng(7)
    mu, r = 4.0, 20000
    a = mu + rng.standard_normal(r)
    b = mu + rng.standard_normal(r)
    c = mu + rng.standard_normal(r)
    est, se = cross_product_estimate(a, b, c)
    assert est == pytest.approx(mu ** 3, abs=5 * se)


def test_cross_product_estimate_input_errors():
    with pytest.raises(ValueError):
        cross_product_estimate(np.ones(5))
    with pytest.raises(ValueError):
        cross_product_estimate(np.ones(5), np.ones(4))
    with pytest.raises(ValueError):
        cross_product_estimate(np.ones(1), np.ones(1))


# ========================================================================================= (c) =====
# The coordinate catalogue: S0 powers against F283's anchors, and structural wiring
# ======================================================================================================

def test_s0_power_matches_f283s_worked_examples():
    assert s0_w0_power(((4, 1), (2, -2))) == (0, 0)     # mu4/mu2^2, S0-free
    assert s0_w0_power(((3, 2), (2, -3))) == (0, 0)     # mu3^2/mu2^3, S0-free
    assert s0_w0_power(((1, 3), (3, -1))) == (0, 0)     # mu1^3/mu3, S0-free
    assert s0_w0_power(((5, 1), (3, -1))) == (0, 2)     # mu5/mu3, S0-bearing (a shift meter)
    assert s0_w0_power(((7, 1),)) == (0, 7)             # a bare order carries its own order


def test_named_anchors_match_f283s_rationals():
    assert NAMED_ANCHOR["mu4/mu2^2"] == pytest.approx(12.0 / 5.0)
    assert NAMED_ANCHOR["mu3^2/mu2^3"] == pytest.approx(8.0 / 25.0)
    assert NAMED_ANCHOR["mu1^3/mu3"] == pytest.approx(-40.0)
    assert NAMED_ANCHOR["mu5/mu3"] == pytest.approx(20.0 / 63.0)


def test_build_catalogue_structure():
    windows = (3.0, 6.0)
    cat = build_catalogue(windows, max_order=6)
    by_name_window = {(c.name, c.window): c for c in cat}
    for w in windows:
        for n in range(1, 7):
            assert ("mu%d" % n, w) in by_name_window
        assert ("mu4/mu2^2", w) in by_name_window
        assert ("mu4/mu2^2 (cross)", w) in by_name_window
        ratio = by_name_window[("mu4/mu2^2", w)]
        assert ratio.depends_on == (("mu4", w), ("mu2", w))
        assert ratio.s0_power == 0
        cross = by_name_window[("mu4/mu2^2 (cross)", w)]
        assert cross.replicas_needed == 2
        even = by_name_window[("dmu2/dW", w)]
        odd = by_name_window[("dmu3/dW", w)]
        assert even.rank_group == f"deriv_even@{w:g}"
        assert odd.rank_group == f"deriv_odd@{w:g}"
        assert even.rank_group != odd.rank_group
        integ = by_name_window[("tent_mu2", w)]
        assert integ.depends_on == ()


# ========================================================================================= (d) =====
# select_coordinates: rule W1 and A100.1's singular-covariance refusal, both ways
# ======================================================================================================

def _good_trial(coord: Coordinate, bias=0.001, bias_se=0.001, replica_sd=1.0) -> CoordinateTrial:
    """A trial engineered to pass every W1 clause easily, so the only thing that can refuse it is
    A100.1's structural check or F297's rank_group check -- exactly what these tests probe."""
    return coord.trial("archive", bias=bias, bias_se=bias_se, replica_sd=replica_sd,
                        resolved=True, forecast_ok=True, leverage=0.5)


def test_select_coordinates_refuses_a_ratio_together_with_both_its_members_ratio_first():
    cat = {(c.name, c.window): c for c in build_catalogue([6.0], max_order=4)}
    ratio = cat[("mu4/mu2^2", 6.0)]
    mu2 = cat[("mu2", 6.0)]
    mu4 = cat[("mu4", 6.0)]
    # the ratio ranks best (smallest bias/sd) so it is admitted FIRST; one member must then be refused
    table = [_good_trial(ratio, bias=0.0001), _good_trial(mu2, bias=0.01), _good_trial(mu4, bias=0.01)]
    sel = select_coordinates(table, level="archive")
    assert ("mu4/mu2^2", 6.0) in sel.admitted
    names_admitted = {k[0] for k in sel.admitted}
    assert not {"mu2", "mu4"} <= names_admitted, f"admitted {sel.admitted} contains a ratio and both members"
    refused_names = {k[0] for k in sel.refused}
    assert refused_names & {"mu2", "mu4"}, f"expected one member refused, got refused={sel.refused}"
    assert any("A100.1" in reason for reason in sel.refused.values())


def test_select_coordinates_refuses_a_ratio_together_with_both_its_members_members_first():
    cat = {(c.name, c.window): c for c in build_catalogue([6.0], max_order=4)}
    ratio = cat[("mu4/mu2^2", 6.0)]
    mu2 = cat[("mu2", 6.0)]
    mu4 = cat[("mu4", 6.0)]
    # the members rank best this time, so BOTH are admitted first; the ratio must then be refused
    table = [_good_trial(ratio, bias=0.01), _good_trial(mu2, bias=0.0001), _good_trial(mu4, bias=0.0002)]
    sel = select_coordinates(table, level="archive")
    assert ("mu2", 6.0) in sel.admitted and ("mu4", 6.0) in sel.admitted
    assert ("mu4/mu2^2", 6.0) not in sel.admitted
    assert ("mu4/mu2^2", 6.0) in sel.refused
    assert "A100.1" in sel.refused[("mu4/mu2^2", 6.0)]


def test_select_coordinates_does_not_refuse_a_non_singular_set():
    """The positive control: mu2 and mu4 alone (no ratio) are not an exact function of one another
    and must both be admitted -- A100.1's mechanism must not over-refuse."""
    cat = {(c.name, c.window): c for c in build_catalogue([6.0], max_order=4)}
    mu2 = cat[("mu2", 6.0)]
    mu4 = cat[("mu4", 6.0)]
    table = [_good_trial(mu2), _good_trial(mu4)]
    sel = select_coordinates(table, level="archive")
    assert set(sel.admitted) == {("mu2", 6.0), ("mu4", 6.0)}
    assert not sel.refused


def test_select_coordinates_rank_group_admits_at_most_one_derivative_per_window():
    cat = {(c.name, c.window): c for c in build_catalogue([6.0], max_order=4)}
    even2 = cat[("dmu2/dW", 6.0)]
    # a second even-order derivative at the SAME window, hand-tagged into the same rank_group (F297):
    # every order's derivative there is an exact scalar multiple of the same two edge values.
    even4 = Coordinate(name="dmu4/dW", window=6.0, kind="derivative", order=4,
                        rank_group=even2.rank_group)
    table = [_good_trial(even2, bias=0.0001), _good_trial(even4, bias=0.01)]
    sel = select_coordinates(table, level="archive")
    assert ("dmu2/dW", 6.0) in sel.admitted
    assert ("dmu4/dW", 6.0) not in sel.admitted
    assert "F297" in sel.refused[("dmu4/dW", 6.0)]


def test_select_coordinates_w1_clauses():
    w = 6.0
    rows = [
        CoordinateTrial("mu2", w, "archive", bias=0.01, bias_se=0.5, replica_sd=1.0,
                         leverage=0.5, forecast_ok=True),   # fails W1(a): SE/sd = 0.5 > 0.2
        CoordinateTrial("mu3", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                         resolved=False, leverage=0.5, forecast_ok=True),   # fails W1(c)
        CoordinateTrial("mu5", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                         forecast_ok=False, leverage=0.5),   # fails W1(b)
        CoordinateTrial("mu7", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                         leverage=None, forecast_ok=True),   # W1(d) unmeasured -> diagnostic (A58)
        CoordinateTrial("mu9", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                         leverage=0.001, forecast_ok=True),  # W1(d) below threshold -> diagnostic
        CoordinateTrial("mu4", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                         leverage=0.5, forecast_ok=True),    # passes everything
    ]
    sel = select_coordinates(rows, level="archive")
    assert sel.admitted == (("mu4", w),)
    assert sel.refused[("mu2", w)].startswith("W1(a)")
    assert sel.refused[("mu3", w)].startswith("W1(c)")
    assert sel.refused[("mu5", w)].startswith("W1(b)")
    assert sel.diagnostic[("mu7", w)].startswith("W1(d)")
    assert sel.diagnostic[("mu9", w)].startswith("W1(d)")


def test_select_coordinates_require_leverage_refuses_unmeasured():
    w = 6.0
    rows = [CoordinateTrial("mu2", w, "archive", bias=0.01, bias_se=0.01, replica_sd=1.0,
                             leverage=None, forecast_ok=True)]
    sel = select_coordinates(rows, level="archive", require_leverage=True)
    assert sel.admitted == ()
    assert "require_leverage" in sel.refused[("mu2", w)]


def test_select_coordinates_duplicate_cell_raises():
    w = 6.0
    rows = [CoordinateTrial("mu2", w, "archive", bias=0.0, bias_se=0.01, replica_sd=1.0),
            CoordinateTrial("mu2", w, "archive", bias=0.0, bias_se=0.02, replica_sd=1.0)]
    with pytest.raises(ValueError):
        select_coordinates(rows, level="archive")


def test_select_coordinates_no_rows_at_level_raises():
    w = 6.0
    rows = [CoordinateTrial("mu2", w, "n10", bias=0.0, bias_se=0.01, replica_sd=1.0)]
    with pytest.raises(ValueError):
        select_coordinates(rows, level="archive")


# ========================================================================================= (e) =====
# hartlap_factor, shrink_to_diagonal, moment_block_nll
# ======================================================================================================

def test_hartlap_factor_known_value():
    # F284: "About 60 coordinates from 500 replicas need the Hartlap factor
    # (N - p - 2)/(N - 1) = 0.88 on the inverse covariance"
    got = hartlap_factor(500, 60)
    assert got == pytest.approx((500 - 60 - 2) / (500 - 1), abs=1e-12)
    assert round(got, 2) == 0.88


def test_hartlap_factor_negative_when_coordinates_approach_or_exceed_replicas():
    # F287: "the Hartlap factor negative on 31 of 32 conditions at the archive level" -- the real
    # regime measured there was "198 to 302 admitted coordinates against 200 replicas" (F287 point 3),
    # i.e. p close to or above n_rep=200; this function must return it as computed, never clipped, so
    # the caller can see the budget failure (A100.7).
    assert hartlap_factor(60, 60) < 0
    assert hartlap_factor(200, 230) < 0


def test_hartlap_factor_input_errors():
    with pytest.raises(ValueError):
        hartlap_factor(1, 5)
    with pytest.raises(ValueError):
        hartlap_factor(10, 0)


def test_dodelson_schneider_factor_known_values():
    # Dodelson & Schneider 2013, PRD 88, 063537, Eqs. 27-28. B at (n_rep=500, n_data=50):
    #   d = n_rep - n_data = 450; B = (d-2)/((d-1)(d-4)) = 448/(449*446) = 2.23716e-3
    d = 500 - 50
    b = (d - 2) / ((d - 1) * (d - 4))
    assert b == pytest.approx(2.23716e-3, rel=1e-5)
    assert dodelson_schneider_factor(500, 50, 10) == pytest.approx(1.089486, rel=1e-6)
    assert dodelson_schneider_factor(500, 50, 5) == pytest.approx(1.100672, rel=1e-6)
    # 1 + B*(n_data - n_params) directly, at the same (n_rep, n_data)
    assert dodelson_schneider_factor(500, 50, 10) == pytest.approx(1.0 + b * (50 - 10), abs=1e-9)


def test_dodelson_schneider_factor_input_errors():
    with pytest.raises(ValueError):
        dodelson_schneider_factor(0, 50, 5)
    with pytest.raises(ValueError):
        dodelson_schneider_factor(51, 50, 5)   # n_rep - n_data = 1: denominator (d-1)(d-4) = 0
    with pytest.raises(ValueError):
        dodelson_schneider_factor(54, 50, 5)   # n_rep - n_data = 4: denominator (d-1)(d-4) = 0


def test_shrink_to_diagonal_keeps_the_diagonal_exact_and_improves_conditioning():
    rng = np.random.default_rng(7)
    x = rng.standard_normal((12, 10))   # p close to n: a near-singular sample covariance
    s, s_shrunk, kappa, engine = shrink_to_diagonal(x)
    assert 0.0 <= kappa <= 1.0
    assert np.allclose(np.diag(s_shrunk), np.diag(s))
    assert np.linalg.cond(s_shrunk) <= np.linalg.cond(s) + 1e-6
    assert isinstance(engine, str) and engine


def test_replica_covariance_default_is_plain_sample_covariance_hartlap_corrected():
    """shrinkage=False is the module's own default (a correction from the thesis side): the plain sample
    covariance, Hartlap-corrected, which is the regime Hartlap et al. 2007 actually licenses."""
    rng = np.random.default_rng(11)
    n_rep, n_data = 300, 8
    x = rng.standard_normal((n_rep, n_data))
    rc = replica_covariance(x)
    assert rc.hartlap is not None
    assert rc.hartlap == pytest.approx(hartlap_factor(n_rep, n_data))
    xc = x - x.mean(0)
    s = (xc.T @ xc) / (n_rep - 1)
    assert np.allclose(rc.cov, s)
    assert np.allclose(rc.cov_shrunk, s)
    assert np.allclose(rc.precision, rc.hartlap * np.linalg.pinv(s))


def test_replica_covariance_shrinkage_carries_no_hartlap_factor():
    """A shrunk covariance is biased toward its target by construction and is not Wishart-distributed,
    so Hartlap's factor does not apply to it (Hartlap, Simon & Schneider 2007's own derivation) --
    replica_covariance(shrinkage=True) must not scale its precision by any factor."""
    rng = np.random.default_rng(12)
    n_rep, n_data = 12, 10   # p close to n: the near-singular regime shrinkage exists for
    x = rng.standard_normal((n_rep, n_data))
    rc = replica_covariance(x, shrinkage=True)
    assert rc.hartlap is None
    assert np.allclose(rc.precision, np.linalg.pinv(rc.cov_shrunk))
    assert "no Hartlap factor" in rc.shrinkage_engine


def test_replica_covariance_input_errors():
    with pytest.raises(ValueError):
        replica_covariance(np.ones(5))              # not 2-D
    with pytest.raises(ValueError):
        replica_covariance(np.ones((5, 3)), coord_names=("a", "b"))   # wrong name count


def test_moment_block_nll_matches_scipy_multivariate_normal():
    rng = np.random.default_rng(0)
    p = 3
    a = rng.standard_normal((p, p))
    cov = a @ a.T + p * np.eye(p)             # SPD
    predicted = rng.standard_normal(p)
    observed = predicted + 0.1 * rng.standard_normal(p)
    precision = np.linalg.inv(cov)

    got = moment_block_nll(observed, predicted, cov, precision=precision, form="hartlap")
    r = observed - predicted
    want_direct = float(r @ precision @ r) + np.linalg.slogdet(cov)[1]
    assert got == pytest.approx(want_direct, abs=1e-9)

    logpdf = multivariate_normal.logpdf(observed, mean=predicted, cov=cov)
    want_scipy = -2.0 * logpdf - p * math.log(2 * math.pi)
    assert got == pytest.approx(want_scipy, abs=1e-6)


def test_moment_block_nll_applies_the_hartlap_factor_when_precision_is_not_given():
    rng = np.random.default_rng(1)
    p = 4
    a = rng.standard_normal((p, p))
    cov = a @ a.T + p * np.eye(p)
    predicted = rng.standard_normal(p)
    observed = predicted + 0.1 * rng.standard_normal(p)
    n_rep = 200

    got = moment_block_nll(observed, predicted, cov, n_rep=n_rep, form="hartlap")
    r = observed - predicted
    alpha = hartlap_factor(n_rep, p)
    want = alpha * float(r @ np.linalg.inv(cov) @ r) + np.linalg.slogdet(cov)[1]
    assert got == pytest.approx(want, abs=1e-9)


def test_moment_block_nll_sellentin_heavens_form():
    rng = np.random.default_rng(2)
    p = 3
    a = rng.standard_normal((p, p))
    cov = a @ a.T + p * np.eye(p)
    predicted = rng.standard_normal(p)
    observed = predicted + 0.1 * rng.standard_normal(p)
    n_rep = 150

    got = moment_block_nll(observed, predicted, cov, n_rep=n_rep, form="sellentin_heavens")
    r = observed - predicted
    quad = float(r @ np.linalg.inv(cov) @ r)
    want = n_rep * math.log1p(quad / (n_rep - 1)) + np.linalg.slogdet(cov)[1]
    assert got == pytest.approx(want, abs=1e-9)
    # as n_rep -> infinity the Sellentin-Heavens form must approach the plain (unscaled) Gaussian form
    got_big = moment_block_nll(observed, predicted, cov, n_rep=2_000_000, form="sellentin_heavens")
    want_gauss = quad + np.linalg.slogdet(cov)[1]
    assert got_big == pytest.approx(want_gauss, rel=1e-4)


def test_moment_block_nll_default_form_is_sellentin_heavens():
    """A correction from the thesis side: at this record's own p/R (about 0.1, A100.7), both Hartlap 2007 and
    Sellentin & Heavens 2016 license the plain sample covariance with the t-likelihood, so that is the
    default form, not the Hartlap-scaled Gaussian."""
    rng = np.random.default_rng(3)
    p = 3
    a = rng.standard_normal((p, p))
    cov = a @ a.T + p * np.eye(p)
    predicted = rng.standard_normal(p)
    observed = predicted + 0.1 * rng.standard_normal(p)
    n_rep = 120
    got_default = moment_block_nll(observed, predicted, cov, n_rep=n_rep)
    got_explicit = moment_block_nll(observed, predicted, cov, n_rep=n_rep, form="sellentin_heavens")
    assert got_default == got_explicit


def test_moment_block_nll_sellentin_heavens_asymptotic_coefficient():
    """n ln(1 + q/(n-1)) - q -> q(2-q)/(2n) as n grows, NOT q^2/(2n) alone -- the two coincide only at
    q=1 (a direct Taylor expansion in 1/n, verified here numerically rather than asserted)."""
    for q in (1.0, 3.0, 8.0):
        for n in (10_000, 100_000):
            f = n * math.log1p(q / (n - 1)) - q
            want = q * (2 - q) / (2 * n)
            assert f == pytest.approx(want, rel=1e-3)
            if q != 1.0:
                wrong = q * q / (2 * n)
                assert f != pytest.approx(wrong, rel=0.5)


def test_moment_block_nll_input_errors():
    cov_bad = -np.eye(2)              # not positive definite
    with pytest.raises(ValueError):
        moment_block_nll([0.0, 0.0], [0.0, 0.0], cov_bad)
    cov = np.eye(2)
    with pytest.raises(ValueError):
        moment_block_nll([0.0, 0.0], [0.0, 0.0], cov, form="not-a-form")
    with pytest.raises(ValueError):
        moment_block_nll([0.0, 0.0], [0.0, 0.0], cov, form="hartlap")   # no n_rep, no precision
    with pytest.raises(ValueError):
        moment_block_nll([0.0, 0.0], [0.0, 0.0], cov, form="sellentin_heavens")   # no n_rep


# --------------------------------------------------------------------------------------------------
# A132.1, A132.2 and A132.7 (the thesis side's section 6 of 2026-09-22)
# --------------------------------------------------------------------------------------------------

def _hankel(n: int) -> np.ndarray:
    """The raw window moments' white-noise covariance on [-1, 1]: integral t^(i+j) dt."""
    return np.array([[2.0 / (i + j + 1) if (i + j) % 2 == 0 else 0.0 for j in range(n)] for i in range(n)])


def test_the_legendre_basis_diagonalises_the_raw_moments_hankel_covariance():
    """A132.1's numbers, reproduced: condition number 2.96e8 (correlation 7.86e7) for orders 0 to 12 in
    the monomial basis, and the identity correlation in the window's Legendre basis."""
    from rb5s6s.moment_coords import monomial_to_legendre
    H = _hankel(13)
    assert np.linalg.cond(H) == pytest.approx(2.96e8, rel=0.01)
    d = np.sqrt(np.diag(H))
    assert np.linalg.cond(H / np.outer(d, d)) == pytest.approx(7.86e7, rel=0.01)
    Ti = np.linalg.inv(monomial_to_legendre(12))
    C = Ti @ H @ Ti.T
    assert np.allclose(np.diag(C), [2.0 / (2 * k + 1) for k in range(13)], rtol=1e-8)
    dc = np.sqrt(np.diag(C))
    assert np.max(np.abs(C / np.outer(dc, dc) - np.eye(13))) < 1e-8


def test_the_set_bias_reads_the_reviews_aligned_and_worst_sign_cases():
    """A bias of 0.1 sd on every raw moment reads 0.031 aligned and 5.99e5 at the worst signs (A132.1), so a
    per-coordinate clause bounds nothing, and the set statistic is what W1(a) must read."""
    import itertools
    from rb5s6s.moment_coords import whitened_set_bias
    H = _hankel(13)
    b = 0.1 * np.sqrt(np.diag(H))
    assert whitened_set_bias(b, H)["chi2"] == pytest.approx(0.0312, rel=0.01)
    worst = max(whitened_set_bias(b * np.array((1.0,) + s), H)["chi2"]
                for s in itertools.product((1.0, -1.0), repeat=12))
    assert worst == pytest.approx(5.99e5, rel=0.01)


def test_the_set_bias_null_mean_is_p_over_r_and_a_singular_set_is_refused():
    from rb5s6s.moment_coords import whitened_set_bias
    rng = np.random.default_rng(7)
    p, R = 5, 50
    A = rng.normal(size=(p, p))
    S = A @ A.T + p * np.eye(p)
    Lc = np.linalg.cholesky(S)
    chis = []
    for _ in range(2000):
        reps = (Lc @ rng.normal(size=(p, R))).T
        chis.append(whitened_set_bias(reps.mean(axis=0), S, n_rep=R)["chi2"])
    out = whitened_set_bias(np.zeros(p), S, n_rep=R)
    assert out["null_mean"] == pytest.approx(p / R)
    assert np.mean(chis) == pytest.approx(p / R, rel=0.08)
    sing = np.ones((3, 3))
    with pytest.raises(ValueError, match="not positive definite"):
        whitened_set_bias(np.zeros(3), sing)


def test_the_legendre_projections_are_the_monomial_moments_in_another_basis_and_uncorrelated_under_noise():
    """Planted two ways on a Gaussian line: the projections map exactly onto the raw moments through
    `monomial_to_legendre`, and over white-noise replicas their correlation is near the identity where the
    raw moments' is not."""
    from rb5s6s.moment_coords import legendre_window_moments, monomial_to_legendre, raw_window_moment
    nu = np.linspace(-20.0, 20.0, 4001)
    y = np.exp(-0.5 * (nu / 1.7) ** 2)
    c, W, n = 0.3, 6.0, 6
    L = legendre_window_moments(nu, y, c, W, n)
    m = np.array([raw_window_moment(nu, y, c, W, k) / W ** k for k in range(n + 1)])
    assert np.allclose(monomial_to_legendre(n) @ L, m, rtol=1e-9, atol=1e-12)
    rng = np.random.default_rng(11)
    Ls, Ms = [], []
    for _ in range(400):
        e = rng.normal(size=nu.size)
        Ls.append(legendre_window_moments(nu, e, 0.0, W, 4, n_points=1601))
        Ms.append([raw_window_moment(nu, e, 0.0, W, k, n_points=1601) / W ** k for k in range(5)])
    rl = np.corrcoef(np.array(Ls).T)
    rm = np.corrcoef(np.array(Ms).T)
    assert np.max(np.abs(rl - np.eye(5))) < 0.2
    assert abs(rm[0, 2]) > 0.6, "the raw moments of orders 0 and 2 are strongly correlated under white noise"
    assert np.all(np.isnan(legendre_window_moments(nu, y, 18.0, 6.0, 3)))


def test_the_shannon_budget_reproduces_the_review_and_refuses_bad_inputs():
    from rb5s6s.moment_coords import shannon_coordinate_budget
    assert round(shannon_coordinate_budget(21.0, 3.0, 1000.0)) == 31
    assert round(shannon_coordinate_budget(13.0, 3.0, 1000.0)) == 19
    for bad in ((0.0, 3.0, 1000.0), (21.0, 0.0, 1000.0), (21.0, 3.0, 1.0)):
        with pytest.raises(ValueError):
            shannon_coordinate_budget(*bad)


def test_a_moments_s0_support_comes_from_its_cumulant_expansion():
    """A132.2, derived by hand: mu2 = kappa2 is (0, 2); mu3 = kappa3 is (3,), homogeneous; mu4 = kappa4 +
    3 kappa2^2 is (0, 2, 4), NOT homogeneous, so the total-order rule fails for it on a real line; mu5 =
    kappa5 + 10 kappa3 kappa2 is (3, 5); and with a symmetric but non-Gaussian rest (kappa4 not clean)
    mu4 gains nothing new and mu6 keeps its zero power."""
    from rb5s6s.moment_coords import moment_s0_support
    assert moment_s0_support(2) == (0, 2)
    assert moment_s0_support(3) == (3,)
    assert moment_s0_support(4) == (0, 2, 4)
    assert moment_s0_support(5) == (3, 5)
    assert moment_s0_support(6) == (0, 2, 4, 6)
    odd_only = (3, 5, 7, 9, 11)
    assert moment_s0_support(3, clean=odd_only) == (3,)
    assert moment_s0_support(4, clean=odd_only) == (0, 2, 4)
    assert moment_s0_support(0) == (0,)
