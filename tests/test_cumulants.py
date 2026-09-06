"""`rb5s6s.cumulants`: the windowed self-centred cumulant with its convergence
reported and the pedestal removed.

Each test names the failure it exists to catch. The pedestal test carries its
own negative case, the twenty-pass unconverged estimator on a dim line, which
is the defect of 2026-09-06 re-instated; a guard whose plant passes against the
broken form is decoration.
"""
import numpy as np
import pytest

from rb5s6s._compat import trapezoid
from rb5s6s.cumulants import cumulants_from_central_moments, linear_baseline, windowed_cumulant, windowed_cumulants, wing_baseline

GRID = np.linspace(-60.0, 60.0, 6001)


def _ramp_line(s0: float, sigma: float, amplitude: float = 1.0, pedestal: float = 0.0) -> np.ndarray:
    """A Gaussian kernel of rms `sigma` convolved with the ramp f(s) = 2|s|/S0^2
    on [-S0, 0]: mass at the full shift thinning toward zero, so the mean sits
    at -2 S0/3 and the third cumulant is +S0^3/135 (docs/methods/03), on a
    flat pedestal."""
    s = np.linspace(-s0, 0.0, 2001)
    f = 2.0 * np.abs(s) / s0 ** 2
    line = np.zeros_like(GRID)
    for si, fi in zip(s, f):
        line += fi * np.exp(-0.5 * ((GRID - si) / sigma) ** 2)
    line *= (s[1] - s[0]) / (sigma * np.sqrt(2 * np.pi))
    return amplitude * line + pedestal


def test_a_symmetric_line_has_no_third_cumulant():
    """Failure: a centring or normalisation defect manufactures skew from a
    Gaussian."""
    y = np.exp(-0.5 * (GRID / 2.0) ** 2)
    k3, info = windowed_cumulant(GRID, y, 8.0, 3)
    assert info["converged"] == 1.0
    assert abs(k3) < 1e-6


def test_the_ramp_third_cumulant_is_s0_cubed_over_135():
    """Failure: the estimator's constant departs from the record's derivation
    where the window truncates nothing."""
    s0 = 0.5
    y = _ramp_line(s0, 1.0)
    k3, info = windowed_cumulant(GRID, y, 12.0, 3, baseline=None)
    assert info["converged"] == 1.0
    assert k3 == pytest.approx(s0 ** 3 / 135.0, rel=0.02)
    assert info["centre"] == pytest.approx(-2 * s0 / 3, abs=0.01)


def test_the_pedestal_does_not_move_the_converged_estimate_and_moved_the_old_one():
    """The defect of 2026-09-06. A dim line (a twentieth of the bright one) on
    a pedestal a third of its height: the converged, baseline-subtracted
    estimator agrees with the pedestal-free line, and the old form (twenty
    passes, no baseline, clipped) does not. Both directions asserted, so the
    plant cannot pass against the broken code."""
    s0 = 0.5
    clean = _ramp_line(s0, 1.0, amplitude=0.05)
    dim = _ramp_line(s0, 1.0, amplitude=0.05, pedestal=0.01)
    k_clean, _ = windowed_cumulant(GRID, clean, 24.0, 3, baseline=None)
    k_dim, info = windowed_cumulant(GRID, dim, 24.0, 3)
    assert info["converged"] == 1.0
    assert k_dim == pytest.approx(k_clean, rel=0.02)
    # the negative case: the retired form, re-instated here on a copy
    c = 0.0
    for _ in range(20):
        g = np.linspace(c - 24.0, c + 24.0, 4001)
        yy = np.clip(np.interp(g, GRID, dim), 0, None)
        yy = yy / trapezoid(yy, g)
        c = trapezoid(g * yy, g)
    g = np.linspace(c - 24.0, c + 24.0, 4001)
    yy = np.clip(np.interp(g, GRID, dim), 0, None); yy = yy / trapezoid(yy, g)
    m1 = trapezoid(g * yy, g)
    k_old = float(trapezoid((g - m1) ** 3 * yy, g))
    assert abs(k_old - k_clean) > 5 * abs(k_clean), "the old form must fail here, or this test tests nothing"


def test_an_unreached_tolerance_is_reported_not_hidden():
    """Failure: the flag reads converged on a run that hit the pass cap."""
    dim = _ramp_line(0.5, 1.0, amplitude=0.05, pedestal=0.01)
    _, info = windowed_cumulant(GRID, dim, 24.0, 3, baseline=None, max_passes=3)
    assert info["converged"] == 0.0 and info["passes"] == 3.0
    _, info = windowed_cumulant(GRID, dim, 24.0, 3, baseline=None)
    assert info["converged"] == 1.0 and info["passes"] < 400


def test_the_recursion_returns_the_known_cumulants():
    """Failure: the moment-to-cumulant recursion mis-weights a term. A
    Gaussian's fourth and fifth cumulants vanish, and its central moments are
    known in closed form."""
    sigma = 1.7
    mu = np.array([0.0, sigma ** 2, 0.0, 3 * sigma ** 4, 0.0])
    kappa = cumulants_from_central_moments(mu)
    assert kappa[1] == pytest.approx(sigma ** 2)
    assert kappa[2] == 0.0
    assert abs(kappa[3]) < 1e-12 and abs(kappa[4]) < 1e-12
    # kappa_5 = mu_5 - 10 mu_2 mu_3 on a hand case
    mu = np.array([0.0, 2.0, 0.5, 12.0, 3.0])
    assert cumulants_from_central_moments(mu)[4] == pytest.approx(3.0 - 10 * 2.0 * 0.5)


def test_the_wing_baseline_ignores_the_line_and_a_tooth():
    """Failure: a pedestal estimate that the body of the scan moves."""
    y = 0.02 + np.exp(-0.5 * (GRID / 2.0) ** 2) + 0.3 * np.exp(-0.5 * ((GRID - 40.0) / 2.0) ** 2)
    assert wing_baseline(GRID, y) == pytest.approx(0.02, abs=1e-6)


def test_a_window_with_no_positive_mass_returns_nan():
    """Failure: an all-negative window divides by a non-positive integral."""
    y = -np.ones_like(GRID)
    v, info = windowed_cumulant(GRID, y, 5.0, 3, baseline=None)
    assert np.isnan(v) and info["converged"] == 0.0


def test_several_orders_from_one_centring_agree_with_the_single_order_call():
    """Failure: the multi-order path and the single-order path diverge, or the
    Gaussian's fifth and seventh cumulants come out non-zero on a wide window."""
    y = _ramp_line(0.5, 1.0, pedestal=0.01)
    many, info = windowed_cumulants(GRID, y, 12.0, (3, 5, 7))
    one3, info3 = windowed_cumulant(GRID, y, 12.0, 3)
    assert many[3] == one3 and info["centre"] == info3["centre"] and info["converged"] == 1.0
    g = np.exp(-0.5 * (GRID / 2.0) ** 2)
    kg, _ = windowed_cumulants(GRID, g, 16.0, (3, 5, 7))
    assert abs(kg[3]) < 1e-6 and abs(kg[5]) < 1e-4 and abs(kg[7]) < 1e-2


def test_a_tilted_pedestal_is_a_fake_third_moment_that_the_linear_baseline_removes():
    """The finding of 2026-09-06 at a 40 MHz comb spacing: a distant tooth's
    tail is a tilt across the window, and the cubic weight turns a tilt of a
    fraction of a per cent of the peak into a third moment comparable to the
    ramp's. A symmetric line on a tilted pedestal must read zero skew once the
    tilt is removed through two clear strips, and must NOT read zero with the
    level-only wing baseline, or this test tests nothing."""
    line = np.exp(-0.5 * (GRID / 2.7) ** 2)
    tilt = 0.01 + 0.0005 * GRID / 12.0              # a tenth of a per cent of the peak across a 12 MHz window
    y = line + tilt
    k_wings, _ = windowed_cumulant(GRID, y, 6.0, 3)
    k_lin, info = windowed_cumulant(GRID, y, 6.0, 3, baseline=("linear", (-28.0, -12.0), (12.0, 28.0)))
    assert info["converged"] == 1.0
    assert abs(k_lin) < 1e-4, k_lin
    assert abs(k_wings) > 20 * abs(k_lin), (k_wings, k_lin)
    b = linear_baseline(GRID, y, (-28.0, -12.0), (12.0, 28.0))
    assert np.allclose(b, tilt, atol=1e-6)



def test_a_window_wider_than_the_trace_is_refused_not_clamped():
    """FAILS IF the estimator fabricates a cumulant past the end of the trace.

    `np.interp` holds the end value outside the grid, so an over-wide window is
    filled with a constant equal to the last sample: a rectangular pedestal
    whose third moment grows without bound. Before this guard the estimator
    returned that number with `converged` set to one. Found by a board's
    prior-commit seat, 2026-09-06, on code shipped in bf07e359.

    NEGATIVE case: windows past the edge must be NaN and must say why.
    """
    import numpy as np
    from rb5s6s.cumulants import windowed_cumulants
    from rb5s6s.lineshape import model_profile
    from rb5s6s import constants as K

    nu = np.linspace(-60.0, 60.0, 32001)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=2.0,
                      transit_fwhm=0.93, s0=5.0,
                      gamma_nat_mhz=K.GAMMA_NAT_HZ / 1e6)
    for half in (62.0, 80.0, 120.0):
        k, info = windowed_cumulants(nu, y, half_width=half)
        assert np.isnan(k[3]), f"half_width {half} past the grid returned a number"
        assert info["in_span"] == 0.0
        assert info["converged"] == 0.0


def test_windows_inside_the_trace_are_untouched_by_that_guard():
    """POSITIVE and TOLERANCE case for the guard above.

    Every window a committed producer uses sits well inside its grid, and the
    guard must not disturb them: it adds no arithmetic, so these must remain
    finite, converged, and flagged in-span. A guard that refused here would be
    worse than the defect it closes.
    """
    import numpy as np
    from rb5s6s.cumulants import windowed_cumulants
    from rb5s6s.lineshape import model_profile
    from rb5s6s import constants as K

    nu = np.linspace(-40.0, 40.0, 32001)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=2.0,
                      transit_fwhm=0.93, s0=2.0,
                      gamma_nat_mhz=K.GAMMA_NAT_HZ / 1e6)
    for half in (3.25, 4.0, 6.0, 8.0, 12.0, 16.0):
        k, info = windowed_cumulants(nu, y, half_width=half)
        assert np.isfinite(k[3]), f"half_width {half} inside the grid was refused"
        assert info["in_span"] == 1.0
