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
from rb5s6s.noise import (condition_noise_model, second_diff, robust_sigma,
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


def test_sigma_of_v_floored_at_dark_noise_even_for_negative_c():
    # The one committed negative-c law (993.4207 nm, 130 C, 125 mW) turns its
    # variance over at V = 0.756 V -- above its own 0.525 V maximum level, so
    # the pathology is latent in the data. The floor at a (raised from 0.2*a,
    # 2026-07-16) guarantees that even an OUT-OF-DOMAIN evaluation of such a
    # law can never hand out sigmas below the zero-signal noise, i.e. no
    # runaway weights, while changing nothing inside the fitted domain.
    law = {"a": 3.6e-3, "b": 1.29e-3, "c": -8.5e-4}
    V = np.array([0.0, 0.3, 0.525, 0.756, 1.6, 3.0])   # spans past the turnover
    s = sigma_of_v(V, law)
    assert np.all(s >= law["a"] - 1e-15)
    # inside the fitted domain the law itself is above the floor -> unchanged
    inside = V <= 0.525
    expect = np.sqrt(law["a"] ** 2 + law["b"] * V[inside] + law["c"] * V[inside] ** 2)
    assert np.allclose(s[inside], expect)


def test_load_noise_model_reads_the_committed_law():
    """The from-CSV loader must hand sigma_of_v a law it can evaluate.

    Exists for the unit seam the closed-loop leg found: the law lives in
    volts and a caller must be able to get the committed coefficients
    without the raw traces. An ambiguous selection refuses rather than
    averaging silently, and the median pool is the campaign-representative
    law the scenario forecast quotes.
    """
    import numpy as np
    import pytest
    from rb5s6s.noise import load_noise_model, sigma_of_v
    from pathlib import Path
    csv_path = Path(__file__).resolve().parents[1] / "results" / "noise_model.csv"
    one = load_noise_model(csv_path, role="p_sweep", peak="4121",
                           temperature_C=130, power_mW=225)
    assert 1e-4 < one["a"] < 1e-1, "the floor should be millivolts"
    med = load_noise_model(csv_path, role="p_sweep", pool="median")
    sig = sigma_of_v(np.array([0.0, 0.5]), med)
    assert sig[0] == med["a"], "zero level returns the floor"
    assert sig[1] > sig[0], "the law grows with level"
    with pytest.raises(ValueError, match="matched"):
        load_noise_model(csv_path, role="p_sweep")


def test_the_sokal_time_reads_one_on_white_noise_and_the_ar1_value_on_correlated_noise():
    """F36: the estimator that whitens a fit is measured on residuals; white noise reads one within
    a tenth at twenty thousand samples, and an AR(1) series at rho = 0.5 reads (1 + rho)/(1 - rho) = 3
    within fifteen per cent, with the window past the correlation's own length."""
    import numpy as np
    from rb5s6s.noise import integrated_time_sokal, effective_tau
    rng = np.random.default_rng(3)
    w = integrated_time_sokal(rng.standard_normal(20000))
    assert abs(w["tau"] - 1.0) < 0.1 and w["window"] <= 8, w
    e = rng.standard_normal(40000); a = np.empty_like(e); a[0] = e[0]
    for i in range(1, e.size):
        a[i] = 0.5 * a[i - 1] + e[i]
    c = integrated_time_sokal(a)
    assert abs(c["tau"] - 3.0) / 3.0 < 0.15 and c["window"] >= 10, c
    # the seam: the residual time when the table has it, the raw time otherwise, floored at one
    assert effective_tau({"tau_int": 3.8}, {"k": 1.2}, "k") == 1.2
    assert effective_tau({"tau_int": 3.8}, {"k": 0.9}, "k") == 1.0
    assert effective_tau({"tau_int": 3.8}, {}, "k") == 3.8


def test_every_whitening_site_reads_the_effective_time_and_the_loader_attaches_it():
    """F36: sixteen producers divided their residuals by the raw-segment tau_int, which the record's
    own measurement says is the line's curvature; the loader now attaches `tau_eff` (the post-fit
    residuals' own time, floored at one) and every whitening site reads it. The guard is a text
    scan of the sites that were repaired, so a site that regresses to the raw column goes red."""
    import re
    from pathlib import Path
    from rb5s6s import noise as N
    root = Path(__file__).resolve().parents[1]
    law = N.load_noise_model(root / "results" / "noise_model.csv", role="p_sweep", peak="4192", temperature_C=130.0, power_mW=225.0)
    assert "tau_eff" in law and law["tau_eff"] >= 1.0 and law["tau_eff"] <= law["tau_int"] + 1e-9
    raw = re.compile(r"tau\s*=\s*max\(\s*law(\.get\(\s*\"tau_int\"|\[\"tau_int\"\])")
    offenders = []
    for rel in ("rb5s6s/linefit.py", "scripts/run_far_wing_level.py", "scripts/run_full_dataset_fit.py",
                "scripts/run_global_dataset_fit.py", "scripts/run_stark_joint.py", "scripts/run_ultra_joint.py"):
        for i, line in enumerate((root / rel).read_text(encoding="utf-8").splitlines(), 1):
            if raw.search(line):
                offenders.append(f"{rel}:{i}")
    assert not offenders, f"whitening by the raw tau_int again: {offenders}"


def test_the_condition_key_reads_a_blank_power_as_the_temperature_arm():
    """F43: the manifest's temperature-arm rows carry no power; an unresolved key sent that arm's
    fits back to the raw tau. A blank power with a finite temperature is 225 mW; a blank
    temperature is no condition."""
    from rb5s6s.noise import condition_key
    assert condition_key("4154", "110", "") == "4154_110C_225mW"
    assert condition_key("4154", "110", None) == "4154_110C_225mW"
    assert condition_key("4154", 130.0, 25) == "4154_130C_25mW"
    assert condition_key("4154", "", 225) is None
