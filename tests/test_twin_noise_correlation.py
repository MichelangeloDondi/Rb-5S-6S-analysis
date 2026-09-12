"""The twin injects the measured noise correlation, which the charter requires.

The repository's standing rules bind the exhibit to a twin that injects the
measured noise correlation. Until 2026-09-12 all three generator sites drew independent
samples, and `synthetic_traces` read the committed law's amplitude
coefficients while leaving `tau_int` unused in the same dictionary. White noise
overstates the information in every statistic the twin produces: on a fitted
transit width the error bar comes out too small by a factor of 1.58, against a
closed-form sqrt(tau_int) of 1.59.
"""
import math

import numpy as np
import pytest

from rb5s6s.forecast import _correlate, synthetic_traces
from rb5s6s.noise import load_noise_model


def _integrated_time(x, lags=30):
    ac = [float(np.corrcoef(x[:-k], x[k:])[0, 1]) for k in range(1, lags + 1)]
    return 1.0 + 2.0 * sum(ac)


def test_the_default_is_white_and_byte_identical():
    """The opt-in shape: a default that changes nothing that already shipped."""
    w = np.random.default_rng(0).standard_normal(50_000)
    assert np.array_equal(_correlate(w, 1.0), w)


def test_a_correlation_time_below_one_sample_is_refused():
    """NEGATIVE case, matching `n_eff`'s own refusal on the same quantity."""
    w = np.random.default_rng(0).standard_normal(100)
    with pytest.raises(ValueError, match="not a correlation time"):
        _correlate(w, 0.5)


def test_the_marginal_sigma_survives_and_the_integrated_time_is_hit():
    """The amplitude law must be untouched: only the ORDER of the samples
    changes, never their spread, or the noise model would be double-counted."""
    w = np.random.default_rng(1).standard_normal(200_000)
    for tau in (1.5, 2.515, 5.0):
        x = _correlate(w, tau)
        assert x.std() == pytest.approx(1.0, abs=0.01)
        assert _integrated_time(x) == pytest.approx(tau, rel=0.08)


def test_the_variance_of_a_mean_rises_by_the_correlation_time():
    """This is the behaviour the charter is actually asking for: a statistic
    over correlated samples carries less information, by about tau_int."""
    rng = np.random.default_rng(3)
    n = 4000
    for tau in (1.0, 2.515):
        means = [_correlate(rng.standard_normal(n), tau).mean() for _ in range(300)]
        assert np.var(means, ddof=1) * n == pytest.approx(tau, rel=0.35)


def test_the_committed_law_drives_the_twin_without_being_asked():
    """A caller who passes the measured law gets the measured correlation.

    That is the charter sentence: the coefficients and the correlation time
    live in one dictionary and the generator reads both, where it used to read
    only the first.
    """
    law = load_noise_model("results/noise_model.csv", role="p_sweep",
                           pool="median")
    assert law["tau_int"] > 1.0, "the committed law must carry a correlation"
    # an explicit generator on both sides: the same draws, one filtered
    _, v_law = synthetic_traces(0.55, 1.6, 0.9575, n_traces=1, noise=law,
                                n_points=4000,
                                rng=np.random.default_rng(11))
    _, v_white = synthetic_traces(0.55, 1.6, 0.9575, n_traces=1,
                                  noise=dict(law, tau_int=1.0), n_points=4000,
                                  rng=np.random.default_rng(11))
    assert not np.array_equal(v_law[0], v_white[0])


def test_the_committed_law_is_not_self_consistent_and_the_twin_takes_the_safe_branch():
    """`tau_int` and `rho1` in the same committed row disagree under an AR(1),
    and the conservative branch is the integrated time.

    An AR(1) at the measured first lag would imply an integrated time of about
    1.22 against a measured 2.52, so matching `rho1` instead would understate
    the correlation by about two and OVERSTATE the information. This test
    exists so that a future edit to the law re-reads the choice rather than
    inheriting it.
    """
    law = load_noise_model("results/noise_model.csv", role="p_sweep",
                           pool="median")
    implied = (1.0 + law["rho1"]) / (1.0 - law["rho1"])
    assert implied < law["tau_int"], (
        "the law's first lag now implies an integrated time at or above the "
        "measured one, so the branch this module takes needs re-reading")
    a = (law["tau_int"] - 1.0) / (law["tau_int"] + 1.0)
    assert a > law["rho1"], "the synthesised first lag should exceed the measured"
    assert math.isclose((1 + a) / (1 - a), law["tau_int"], rel_tol=1e-9)
