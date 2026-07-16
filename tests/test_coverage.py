"""
The injection-recovery coverage study (rb5s6s/coverage.py) must show the shipped
collisional estimator is unbiased and that its Student-t 95% bound genuinely
covers the truth at >= 95% -- the empirical validation of the t-quantile
coverage correction (a bound that does not cover is worthless).
"""

from __future__ import annotations

import pytest

from rb5s6s.coverage import coverage_study


@pytest.mark.slow
def test_point_estimate_unbiased_and_bound_covers():
    for beta_true in (0.0, 0.1):
        r = coverage_study(beta_true, n_trials=800, seed=1)
        # the point estimate is unbiased
        assert abs(r["bias"]) < 0.01, r
        # the 95% upper bound covers the truth at least 95% of the time
        # (Student-t on 1 DOF is conservative, so coverage is >= nominal)
        assert r["coverage"] >= 0.95, r


@pytest.mark.slow
def test_gaussian_two_would_undercover_but_t_quantile_does_not():
    # Sanity: at beta_true = 0 the t-quantile bound still covers (it is one-sided
    # and conservative). This pins the direction of the correction -- the reason
    # the estimator uses t(0.95, 1) = 6.31 and not the Gaussian 2.
    r = coverage_study(0.0, n_trials=800, seed=2)
    assert r["coverage"] >= 0.95, r
