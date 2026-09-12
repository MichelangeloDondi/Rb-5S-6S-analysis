"""The Coulomb-approximation radial integrals: what they reproduce, where they
fail, and that the failure is documented rather than silent.

FAILURE MODES THESE CATCH. A normalisation or angular-factor slip moves every
computed element by a common factor and the outer-class calibration leaves its
band. A broken Whittaker evaluation at high n* returns NaN, which the tail
sum would carry into Delta_alpha. And a future caller applying the method to
the compact 5s ladder gets a number 20 to 60 per cent off, so the test pins
that failure too, as a floor the ratio must stay below, so nobody promotes the
method where it does not hold.
"""
import warnings
import numpy as np
import pytest

from rb5s6s.coulomb_approx import (calibrate, radial_integral, reduced_e1_s_to_p,
                                   n_star, E_ION_CM, RYD_RB_CM)
from rb5s6s.polarizability import E_6S_CM

warnings.filterwarnings("ignore", message=".*roundoff error.*")


def _ratios():
    return {lab: r for lab, val, sig, comp, r, src in calibrate()}


def test_the_outer_class_is_reproduced_to_six_per_cent():
    r = _ratios()
    for lab in ("6s-7p1/2", "6s-7p3/2", "6s-8p1/2", "6s-8p3/2",
                "7s-7p1/2", "7s-7p3/2", "7s-8p1/2", "7s-8p3/2"):
        assert 0.94 <= r[lab] <= 1.06, (lab, r[lab])


def test_the_compact_5s_ladder_is_not_reproduced_and_the_test_says_so():
    """The approximation is invalid for the ground state: every 5s-np element
    with n >= 7 comes back at least 20 per cent off. A test that passed here
    would be the signal that something changed in the method, not a success."""
    r = _ratios()
    for lab in ("5s-7p1/2", "5s-8p1/2", "5s-9p1/2", "5s-10p1/2", "5s-12p1/2"):
        assert r[lab] < 0.80, (lab, r[lab])


def test_fine_structure_ratio_is_exactly_one_to_two():
    e9 = E_ION_CM - RYD_RB_CM / (9 - 2.65) ** 2
    a, b = reduced_e1_s_to_p(E_6S_CM, e9, 0.5), reduced_e1_s_to_p(E_6S_CM, e9, 1.5)
    assert b ** 2 / a ** 2 == pytest.approx(2.0, rel=1e-9)


def test_diagonal_second_moment_matches_the_hydrogenic_form():
    for e, l in ((0.0, 0), (E_6S_CM, 0)):
        ns = n_star(e)
        hyd = ns ** 2 * (5 * ns ** 2 + 1 - 3 * l * (l + 1)) / 2
        assert radial_integral(e, l, e, l, power=2) == pytest.approx(hyd, rel=0.01)


def test_the_high_n_tail_is_finite_and_falls_as_n_star_minus_three_halves():
    """hyperu lost the function above n* of about 12 on 2026-09-12; the mpmath
    path must return finite, decreasing elements with n*^1.5 d converging."""
    vals = []
    for n in (12, 20, 30):
        e = E_ION_CM - RYD_RB_CM / (n - 2.65) ** 2
        d = reduced_e1_s_to_p(E_6S_CM, e, 1.5)
        assert np.isfinite(d) and d > 0
        vals.append(d * (n - 2.65) ** 1.5)
    assert vals[0] > vals[1] > vals[2] > 0.8 * vals[1]


def test_the_deep_derivation_bounds_the_multipole_channels_and_moves_the_constant_little():
    import csv
    from pathlib import Path
    rows = {(r["quantity"], r["key"]): r for r in csv.DictReader(
        (Path(__file__).resolve().parents[1] / "results" / "polarizability_deep.csv").open())}
    assert float(rows[("E2_over_E1_shift", "at_drive")]["value"]) < 1e-3
    assert float(rows[("M1_over_E1_shift", "at_drive")]["value"]) < 1e-4
    d = rows[("delta_alpha", "at_drive")]
    assert abs(float(d["value"]) - (-1145.0)) < 30.0
    assert 0 < float(d["err"]) < 15.0
    assert abs(float(rows[("static_tail_pull", "computed_vs_SS2011")]["value"])) < 2.0
