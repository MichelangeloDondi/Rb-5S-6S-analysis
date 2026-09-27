"""The latent sweep direction (rb5s6s.orientation, owner order O69): the mixture likelihood's limits, its
posterior, and the reason it exists -- that picking each record's sign from its own asymmetry manufactures an
asymmetry from none, which the mixture does not."""
import math

import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from rb5s6s.orientation import em_fixed_point, mirror, mixture_chi2, posterior_plus


def test_equal_orientations_return_their_common_value():
    assert mixture_chi2(5.0, 5.0) == pytest.approx(5.0, abs=1e-12)
    assert mixture_chi2(5.0, 5.0, p_plus=0.3) == pytest.approx(5.0, abs=1e-12)


def test_a_large_gap_returns_the_smaller_plus_the_prior_constant_and_stays_finite():
    assert mixture_chi2(10.0, 1.0e4) == pytest.approx(10.0 + 2.0 * math.log(2.0), abs=1e-9)
    assert mixture_chi2(1.0e4, 10.0) == pytest.approx(10.0 + 2.0 * math.log(2.0), abs=1e-9)
    far = mixture_chi2(1.0e6, 1.0e6 + 1.0e5)
    assert np.isfinite(far) and far == pytest.approx(1.0e6 + 2.0 * math.log(2.0), rel=1e-12)


def test_the_posterior_reads_the_gap_and_is_symmetric_at_an_even_prior():
    assert posterior_plus(7.0, 7.0) == pytest.approx(0.5)
    assert posterior_plus(7.0, 7.0, p_plus=0.3) == pytest.approx(0.3)
    assert posterior_plus(0.0, 60.0) > 1.0 - 1e-12
    assert posterior_plus(60.0, 0.0) < 1e-12
    a, b = np.array([1.0, 4.0, 9.0]), np.array([2.0, 1.0, 9.5])
    assert np.allclose(posterior_plus(a, b) + posterior_plus(b, a), 1.0)
    # a gap of 2 ln 3 in chi-square is a likelihood ratio of three
    assert posterior_plus(0.0, 2.0 * math.log(3.0)) == pytest.approx(0.75)


@pytest.mark.parametrize("p", [0.0, 1.0, -0.1, 1.5])
def test_a_known_direction_is_refused_as_a_prior(p):
    with pytest.raises(ValueError):
        mixture_chi2(1.0, 2.0, p_plus=p)
    with pytest.raises(ValueError):
        posterior_plus(1.0, 2.0, p_plus=p)


def test_the_falling_axis_is_the_rising_one_mirrored():
    assert np.array_equal(mirror([-2.0, 0.0, 3.0]), np.array([2.0, -0.0, -3.0]))


def _records(theta, n, seed):
    rng = np.random.default_rng(seed)
    s = rng.choice([-1.0, 1.0], size=n)
    return s * theta + rng.standard_normal(n)


def _em_theta(T):
    def chi2_fn(th):
        return (T - th) ** 2, (T + th) ** 2

    def minimise(obj, th0):
        return minimize_scalar(obj, bounds=(0.0, 5.0), method="bounded", options={"xatol": 1e-10}).x

    theta, w, it = em_fixed_point(chi2_fn, 1.0, len(T), minimise=minimise, tol=1e-8, max_iter=2000)
    return theta, w, it


def test_em_reaches_the_mixture_likelihoods_maximum():
    T = _records(0.8, 400, seed=69)
    theta, w, it = _em_theta(T)
    grid = np.linspace(0.0, 3.0, 30001)
    nll = [float(np.sum(mixture_chi2((T - g) ** 2, (T + g) ** 2))) for g in grid]
    assert theta == pytest.approx(grid[int(np.argmin(nll))], abs=2e-4)
    assert abs(theta - 0.8) < 0.25
    assert w.shape == T.shape and np.all((w >= 0.0) & (w <= 1.0))


def test_picking_each_records_sign_manufactures_an_asymmetry_the_mixture_does_not():
    """theta = 0: no asymmetry at all. Orienting each record by its own sign and averaging returns about
    sqrt(2/pi) = 0.80 whatever the sample size; the mixture's estimate shrinks towards zero with it."""
    T = _records(0.0, 400, seed=70)
    picked = float(np.mean(np.abs(T)))
    theta, _, _ = _em_theta(T)
    assert picked == pytest.approx(math.sqrt(2.0 / math.pi), abs=0.08)
    assert theta < 0.45 < picked
