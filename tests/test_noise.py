"""
Closure tests for the M1 noise model (rb5s6s/noise.py).

Discipline as ever: before the noise model may weight a single real fit, it
must recover KNOWN noise laws injected into campaign-like synthetics —
floor a, shot term b, correlation time — within stated tolerances, and the
second-difference estimator must be demonstrably immune to the line's slope
(the failure mode that motivates it).
"""

from __future__ import annotations

import numpy as np

from rb5s6s import config as C
from rb5s6s.noise import (condition_noise_model, fit_variance_law,
                          noise_vs_level, second_diff, robust_sigma,
                          wing_correlation, sigma_of_v)

T_MS = np.arange(2000) * 0.5 - 500.0


def lorentz_line(center=80.0, fwhm=60.0, height=1.0, base=0.007):
    x = 2.0 * (T_MS - center) / fwhm
    return base + height / (1.0 + x * x)


def with_shot_noise(clean, a=0.003, b=2e-5, rng=None, base=0.007):
    """White noise with variance a^2 + b*(signal above baseline)."""
    rng = rng or np.random.default_rng(C.RNG_SEED)
    lev = np.maximum(clean - base, 0.0)
    sig = np.sqrt(a ** 2 + b * lev)
    return clean + rng.normal(0.0, 1.0, len(clean)) * sig


def test_second_diff_unbiased_on_white_noise():
    rng = np.random.default_rng(C.RNG_SEED)
    x = rng.normal(0.0, 5e-3, 200_000)
    assert abs(robust_sigma(second_diff(x)) / 5e-3 - 1.0) < 0.02


def test_second_diff_immune_to_line_slope():
    # A noiseless bright line must contribute (almost) nothing: the flank
    # slope (~16 mV/sample at 1 V) cancels exactly; only curvature remains.
    e = second_diff(lorentz_line(height=4.0))
    assert np.max(np.abs(e)) < 2e-3  # < 2 mV from a 4 V line


def test_variance_law_recovery():
    # Pool 4 repeats like a real condition block: recover a and b.
    a_true, b_true = 0.003, 2e-5
    traces = [with_shot_noise(lorentz_line(), a=a_true, b=b_true,
                              rng=np.random.default_rng(s)) for s in (1, 2, 3, 4)]
    law = condition_noise_model(traces)
    assert abs(law["a"] / a_true - 1.0) < 0.10, law
    assert abs(law["b"] / b_true - 1.0) < 0.35, law
    # evaluated law must be monotone and sane at the peak
    s_peak = sigma_of_v(np.array([1.0]), law)[0]
    assert abs(s_peak / np.sqrt(a_true ** 2 + b_true) - 1.0) < 0.2


def test_flat_trace_gives_flat_law():
    # No signal => the law must be flat WITHIN ITS FITTED DOMAIN (evaluating
    # far outside law['lev_max'] is documented misuse: a ~2 mV lever arm
    # cannot constrain the slope at 50 mV, and never needs to).
    rng = np.random.default_rng(C.RNG_SEED)
    v = 0.007 + rng.normal(0.0, 3e-3, 2000)
    law = condition_noise_model([v, 0.007 + rng.normal(0.0, 3e-3, 2000)])
    lo, hi = sigma_of_v(np.array([0.0, law["lev_max"]]), law)
    assert abs(hi / lo - 1.0) < 0.15


def test_correlation_time_recovery():
    # AR(1) wings with rho=0.5: tau_int = (1+rho)/(1-rho) = 3, and the
    # whiteness ratio must drop well below 1.
    rng = np.random.default_rng(C.RNG_SEED)
    n, rho = 2000, 0.5
    eps = rng.normal(0.0, 3e-3 * np.sqrt(1 - rho ** 2), n)
    ar = np.zeros(n)
    for i in range(1, n):
        ar[i] = rho * ar[i - 1] + eps[i]
    v = lorentz_line(height=0.2) + ar
    c = wing_correlation(v)
    assert 2.0 < c["tau_int"] < 4.5, c
    assert c["white_ratio"] < 0.85, c


def test_white_trace_correlation_neutral():
    v = with_shot_noise(lorentz_line())
    c = wing_correlation(v)
    assert c["tau_int"] < 1.5
    assert 0.9 < c["white_ratio"] < 1.1
