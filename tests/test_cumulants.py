"""`rb5s6s.cumulants`: the windowed self-centred moment with its convergence
reported and the pedestal removed.

Each test names the failure it exists to catch. The pedestal test carries its
own negative case, the twenty-pass unconverged estimator on a dim line, which
is the defect of 2026-09-06 re-instated; a guard whose plant passes against the
broken form is decoration.

Cumulants are retired from this module (owner order O49, 2026-09-22): every test
below that used to call `windowed_cumulants`/`windowed_cumulant` now calls
`windowed_moments`, which is exact at orders 2 and 3 (mu_2 == kappa_2 and
mu_3 == kappa_3 identically), so no value asserted here moved.
"""
import numpy as np
import pytest

from rb5s6s._compat import trapezoid
from rb5s6s.cumulants import linear_baseline, windowed_moments, wing_baseline
from rb5s6s.lineshape import RAMP_SIDE, lorentzian, ramp_mean_over_s0, ramp_mu3

GRID = np.linspace(-60.0, 60.0, 6001)


def _ramp_line(s0: float, sigma: float, amplitude: float = 1.0, pedestal: float = 0.0) -> np.ndarray:
    """A Gaussian kernel of rms `sigma` convolved with the ramp f(s) = 2|s|/S0^2
    on the package's side (lineshape.RAMP_SIDE, [0, S0] since the ruling of 2026-09-17): mass
    at the full shift thinning toward zero, so the mean and the third moment are the package's
    closed forms (docs/methods/03), on a flat pedestal."""
    s = RAMP_SIDE * np.linspace(0.0, s0, 2001)
    f = 2.0 * np.abs(s) / s0 ** 2
    line = np.zeros_like(GRID)
    for si, fi in zip(s, f):
        line += fi * np.exp(-0.5 * ((GRID - si) / sigma) ** 2)
    line *= (s[1] - s[0]) / (sigma * np.sqrt(2 * np.pi))
    return amplitude * line + pedestal


def test_a_symmetric_line_has_no_third_moment():
    """Failure: a centring or normalisation defect manufactures skew from a
    Gaussian."""
    y = np.exp(-0.5 * (GRID / 2.0) ** 2)
    mu, info = windowed_moments(GRID, y, 8.0, (3,))
    assert info["converged"] == 1.0
    assert abs(mu[3]) < 1e-6


def test_the_ramp_third_moment_is_s0_cubed_over_135():
    """Failure: the estimator's constant departs from the record's derivation
    where the window truncates nothing."""
    s0 = 0.5
    y = _ramp_line(s0, 1.0)
    mu, info = windowed_moments(GRID, y, 12.0, (3,), baseline=None)
    assert info["converged"] == 1.0
    assert mu[3] == pytest.approx(ramp_mu3(s0), rel=0.02)
    assert info["centre"] == pytest.approx(ramp_mean_over_s0() * s0, abs=0.01)


def test_the_pedestal_does_not_move_the_converged_estimate_and_moved_the_old_one():
    """The defect of 2026-09-06. A dim line (a twentieth of the bright one) on
    a pedestal a third of its height: the converged, baseline-subtracted
    estimator agrees with the pedestal-free line, and the old form (twenty
    passes, no baseline, clipped) does not. Both directions asserted, so the
    plant cannot pass against the broken code."""
    s0 = 0.5
    clean = _ramp_line(s0, 1.0, amplitude=0.05)
    dim = _ramp_line(s0, 1.0, amplitude=0.05, pedestal=0.01)
    mu_clean, _ = windowed_moments(GRID, clean, 24.0, (3,), baseline=None)
    mu_dim, info = windowed_moments(GRID, dim, 24.0, (3,))
    assert info["converged"] == 1.0
    assert mu_dim[3] == pytest.approx(mu_clean[3], rel=0.02)
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
    mu_old = float(trapezoid((g - m1) ** 3 * yy, g))
    assert abs(mu_old - mu_clean[3]) > 5 * abs(mu_clean[3]), "the old form must fail here, or this test tests nothing"


def test_an_unreached_tolerance_is_reported_not_hidden():
    """Failure: the flag reads converged on a run that hit the pass cap."""
    dim = _ramp_line(0.5, 1.0, amplitude=0.05, pedestal=0.01)
    _, info = windowed_moments(GRID, dim, 24.0, (3,), baseline=None, max_passes=3)
    assert info["converged"] == 0.0 and info["passes"] == 3.0
    _, info = windowed_moments(GRID, dim, 24.0, (3,), baseline=None)
    assert info["converged"] == 1.0 and info["passes"] < 400


def test_the_wing_baseline_ignores_the_line_and_a_tooth():
    """Failure: a pedestal estimate that the body of the scan moves."""
    y = 0.02 + np.exp(-0.5 * (GRID / 2.0) ** 2) + 0.3 * np.exp(-0.5 * ((GRID - 40.0) / 2.0) ** 2)
    assert wing_baseline(GRID, y) == pytest.approx(0.02, abs=1e-6)


def test_a_window_with_no_positive_mass_returns_nan():
    """Failure: an all-negative window divides by a non-positive integral."""
    y = -np.ones_like(GRID)
    v, info = windowed_moments(GRID, y, 5.0, (3,), baseline=None)
    assert np.isnan(v[3]) and info["converged"] == 0.0


def test_several_orders_from_one_centring_agree_with_the_single_order_call():
    """Failure: the multi-order path and the single-order path diverge, or the
    Gaussian's fifth and seventh moments come out non-zero on a wide window."""
    y = _ramp_line(0.5, 1.0, pedestal=0.01)
    many, info = windowed_moments(GRID, y, 12.0, (3, 5, 7))
    one3, info3 = windowed_moments(GRID, y, 12.0, (3,))
    assert many[3] == one3[3] and info["centre"] == info3["centre"] and info["converged"] == 1.0
    g = np.exp(-0.5 * (GRID / 2.0) ** 2)
    mg, _ = windowed_moments(GRID, g, 16.0, (3, 5, 7))
    assert abs(mg[3]) < 1e-6 and abs(mg[5]) < 1e-4 and abs(mg[7]) < 1e-2


def test_a_fractional_order_raises_and_an_integer_order_still_passes():
    """F451: `windowed_moments` used to coerce a fractional order to the nearest integer and
    return a DIFFERENT statistic under the requested key (order 4.5 silently became mu_4). It now
    raises, naming the order, instead of returning a wrong number under a misleading key; an
    integer order, whether given as an int or as a whole-number float, is unaffected."""
    y = _ramp_line(0.5, 1.0, pedestal=0.01)
    values, info = windowed_moments(GRID, y, 12.0, (3, 5))
    assert info["converged"] == 1.0 and 3 in values and 5 in values
    with pytest.raises(ValueError, match="not an integer"):
        windowed_moments(GRID, y, 12.0, (1.5,))
    with pytest.raises(ValueError, match="not an integer"):
        windowed_moments(GRID, y, 12.0, (3, 4.5))
    # a float that IS a whole number is not fractional and must not raise
    values2, _ = windowed_moments(GRID, y, 12.0, (3.0, 5.0))
    assert values2[3] == values[3] and values2[5] == values[5]


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
    mu_wings, _ = windowed_moments(GRID, y, 6.0, (3,))
    mu_lin, info = windowed_moments(GRID, y, 6.0, (3,), baseline=("linear", (-28.0, -12.0), (12.0, 28.0)))
    assert info["converged"] == 1.0
    assert abs(mu_lin[3]) < 1e-4, mu_lin[3]
    assert abs(mu_wings[3]) > 20 * abs(mu_lin[3]), (mu_wings[3], mu_lin[3])
    b = linear_baseline(GRID, y, (-28.0, -12.0), (12.0, 28.0))
    assert np.allclose(b, tilt, atol=1e-6)



def test_a_window_wider_than_the_trace_is_refused_not_clamped():
    """FAILS IF the estimator fabricates a moment past the end of the trace.

    `np.interp` holds the end value outside the grid, so an over-wide window is
    filled with a constant equal to the last sample: a rectangular pedestal
    whose third moment grows without bound. Before this guard the estimator
    returned that number with `converged` set to one. Found by a board's
    prior-commit seat, 2026-09-06, on code shipped in bf07e359.

    NEGATIVE case: windows past the edge must be NaN and must say why.
    """
    import numpy as np
    from rb5s6s.cumulants import windowed_moments
    from rb5s6s.lineshape import model_profile
    from rb5s6s import constants as K

    nu = np.linspace(-60.0, 60.0, 32001)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=2.0,
                      transit_fwhm=0.93, s0=5.0,
                      gamma_nat_mhz=K.GAMMA_NAT_HZ / 1e6)
    for half in (62.0, 80.0, 120.0):
        mu, info = windowed_moments(nu, y, half_width=half)
        assert np.isnan(mu[3]), f"half_width {half} past the grid returned a number"
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
    from rb5s6s.cumulants import windowed_moments
    from rb5s6s.lineshape import model_profile
    from rb5s6s import constants as K

    nu = np.linspace(-40.0, 40.0, 32001)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=2.0,
                      transit_fwhm=0.93, s0=2.0,
                      gamma_nat_mhz=K.GAMMA_NAT_HZ / 1e6)
    for half in (3.25, 4.0, 6.0, 8.0, 12.0, 16.0):
        mu, info = windowed_moments(nu, y, half_width=half)
        assert np.isfinite(mu[3]), f"half_width {half} inside the grid was refused"
        assert info["in_span"] == 1.0


def test_mu4_is_positive_everywhere_a_lorentzians_k4_changes_sign():
    """F211's finding, the reason O49 moved the record from cumulants to moments, kept as a regression guard after
    the cumulant functions left the package (restored 2026-09-25: a 2026-09-25 audit found it deleted with no successor). On
    a pure Lorentzian the fourth cumulant k4 = mu4 - 3 mu2^2, a small difference of large numbers, crosses zero
    somewhere in the window ladder, while mu4, an absolute even central moment, cannot. k4 is built here from the
    moments themselves, so the plant still discriminates: both signs of k4 are asserted, and mu4's sign at every
    window, so an edit to the centring that let mu4 go negative fails here."""
    y = lorentzian(GRID, 2.0)
    windows = (1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0)
    k4s, mu4s = [], []
    for w in windows:
        mu, _ = windowed_moments(GRID, y, w, (2, 4), baseline=None, centre0=0.0)
        k4s.append(mu[4] - 3.0 * mu[2] ** 2)
        mu4s.append(mu[4])
    assert any(v < 0.0 for v in k4s) and any(v > 0.0 for v in k4s), k4s
    assert all(v > 0.0 for v in mu4s), mu4s
