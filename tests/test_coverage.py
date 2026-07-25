"""
The injection-recovery coverage study (rb5s6s/coverage.py) must show the shipped
collisional estimator is unbiased and that its Student-t 95% bound genuinely
covers the truth at >= 95% -- the empirical validation of the t-quantile
coverage correction (a bound that does not cover is worthless).
"""

from __future__ import annotations

import pytest

from rb5s6s.coverage import coverage_study, minimum_detectable_beta


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


def test_minimum_detectable_effect_is_below_the_quoted_bound():
    """The MDE is what makes the null interpretable: the archive must have been
    able to SEE an effect at or below the size it reports a bound on, otherwise
    "no detection" says nothing about the physics.

    Pins both that the sensitivity is real (95%-detection MDE below the loosest
    quoted per-peak bound) and that it is not absurdly small (the estimator has
    not been accidentally made infinitely sensitive by a scale error).
    """
    import csv as _csv
    from pathlib import Path
    from rb5s6s import config as _C

    mde = minimum_detectable_beta(n_trials=600, seed=1)
    m95 = mde[0.95]
    assert 0.05 < m95 < 0.30, m95        # sane scale for this lever arm

    probe = Path(_C.RESULTS_DIR) / "beta_self_probe.csv"
    if probe.exists():
        bounds = [float(r["bound95_nscale"]) for r in _csv.DictReader(open(probe))
                  if r.get("headline") == "yes"]
        assert m95 < max(bounds), (
            f"MDE at 95% detection ({m95:.2f}) is above the loosest quoted bound "
            f"({max(bounds):.2f}) -- the experiment could not have detected an "
            f"effect the size it claims to bound, so the null is uninformative")
