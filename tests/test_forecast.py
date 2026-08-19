"""The digital twin's guards: generation, forecasting, and the no-data rule.

Class III validation (design machinery): sensitivity checks with stated
limits, plus one ladder-step-1 test reproducing the known-truth recovery the
package already commits to in examples/synthetic_recovery.py. Every test here
runs without data_raw, because the twin's whole point is an experiment that
does not exist yet.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from rb5s6s.forecast import (external_constraint_gain, forecast_precision,
                             n_eff, synthetic_traces)
from rb5s6s.linefit import fit_condition

TRUTH = {"gamma_coll": 0.5, "sigma_laser": 1.5, "transit_fwhm": 1.8}


def test_n_eff_definition_and_guards():
    assert n_eff(2000, 4.0) == pytest.approx(500.0)
    assert n_eff(100, 1.0) == pytest.approx(100.0)
    with pytest.raises(ValueError):
        n_eff(0, 2.0)
    with pytest.raises(ValueError):
        n_eff(100, 0.5)


def test_traces_have_the_promised_shape():
    f, v = synthetic_traces(**TRUTH, n_traces=4, n_points=600,
                            rng=np.random.default_rng(0))
    assert len(f) == len(v) == 4
    assert all(len(x) == 600 for x in f)
    # per-trace amplitude spread means the repeats genuinely differ
    peaks = [x.max() for x in v]
    assert peaks == sorted(peaks) and peaks[-1] > peaks[0]


def test_fraction_of_peak_noise_scales_with_amplitude():
    """The simple noise mode is a fraction of THIS trace's peak, so doubling
    the amplitude doubles the absolute noise and preserves SNR."""
    rng = np.random.default_rng(3)
    _, v1 = synthetic_traces(**TRUTH, n_traces=1, noise=0.01, amp=1.0, rng=rng)
    rng = np.random.default_rng(3)
    _, v2 = synthetic_traces(**TRUTH, n_traces=1, noise=0.01, amp=2.0, rng=rng)
    wing1 = np.std(v1[0][:100])
    wing2 = np.std(v2[0][:100])
    assert wing2 == pytest.approx(2.0 * wing1, rel=1e-9)


def test_measured_law_mode_is_signal_dependent():
    """Under a noise-law dict the wings are quieter than the peak, which the
    fraction-of-peak mode cannot produce."""
    law = {"a": 0.001, "b": 0.004, "c": 0.0}
    f, v = synthetic_traces(**TRUTH, n_traces=1, noise=law, n_points=4000,
                            rng=np.random.default_rng(7))
    clean_wing = np.std(v[0][:400])
    # residual scatter near the peak, detrended crudely by differencing
    core = v[0][1800:2200]
    core_sig = np.std(np.diff(core)) / math.sqrt(2)
    assert core_sig > 1.5 * clean_wing


def test_ladder_step_one_known_truth_recovery():
    """The public API reproduces the committed example's discipline: every
    injected width recovered within three of the fit's own standard errors."""
    f, v = synthetic_traces(**TRUTH, n_traces=5, noise=0.004,
                            rng=np.random.default_rng(20260819))
    res = fit_condition(f, v, T_C=130.0, transit_fwhm=TRUTH["transit_fwhm"])
    for name in ("gamma_coll", "sigma_laser"):
        pull = abs(res[name] - TRUTH[name]) / res[f"{name}_err"]
        assert pull < 3.0, (name, res[name], res[f"{name}_err"])


def test_forecast_reports_the_degeneracy():
    """The width pair's anticorrelation is a property of the physics, and the
    twin must show it on synthetic data or it is not a twin."""
    r = forecast_precision(TRUTH, {"n_traces": 3, "n_points": 800},
                           n_trials=3, scalings=False)
    assert r["corr_laser_coll"] < -0.7


def test_forecast_carries_its_assumptions():
    r = forecast_precision(TRUTH, {"n_traces": 3, "n_points": 600},
                           n_trials=2, scalings=False)
    assert "assumptions" in r and "noise model as stated" in r["assumptions"]


@pytest.mark.slow
def test_scalings_move_the_right_way():
    """Doubling power, repeats or points must not WORSEN the forecast. The
    exact exponents are measured, not asserted, so the guard is one-sided."""
    r = forecast_precision(TRUTH, {"n_traces": 4, "n_points": 800,
                                   "noise": 0.006},
                           n_trials=6, seed=2)
    ratios = r["gamma_coll_err_ratio"]
    for label, ratio in ratios.items():
        assert ratio < 1.1, (label, ratio)
    assert ratios["power_x2"] < ratios["repeats_x2"] + 0.15


def test_external_constraint_gain_is_the_conditional_factor():
    """sqrt(1 - rho^2), the factor pinning one side buys the other."""
    assert external_constraint_gain(0.0) == pytest.approx(1.0)
    assert external_constraint_gain(-0.918) == pytest.approx(0.3968, abs=1e-3)
    assert external_constraint_gain(0.918) == pytest.approx(0.3968, abs=1e-3)
    with pytest.raises(ValueError):
        external_constraint_gain(1.0)


def test_more_data_does_not_break_the_width_degeneracy():
    """The tutorial's chapter 6 claim, guarded: span and trace count shrink
    the uncertainties while leaving the correlation essentially where it was,
    because the degeneracy belongs to the lineshape. An earlier draft of the
    tutorial asserted the opposite and this test is why it does not."""
    truth = (TRUTH["gamma_coll"], TRUTH["sigma_laser"], TRUTH["transit_fwhm"])
    corrs = []
    for kw in ({}, {"span_mhz": 300.0, "n_points": 9000}):
        f, v = synthetic_traces(*truth, n_traces=5, noise=0.004,
                                rng=np.random.default_rng(5), **kw)
        r = fit_condition(f, v, T_C=130.0, transit_fwhm=truth[2])
        corrs.append(r["corr_laser_coll"])
    assert abs(corrs[0] - corrs[1]) < 0.05, corrs
    assert all(c < -0.8 for c in corrs), corrs

# ---- the comb tooth weights, beyond the zero-delay limit (2026-08-19) ----
from scipy.special import jv  # noqa: E402
from rb5s6s.forecast import comb_tooth_weights  # noqa: E402

def test_pathway_identity():
    """The averaged model equals the explicit pathway sum, not just a guess."""
    b, phi = 1.1, 1.7
    for s in range(4):
        coh = sum(jv(n, b) * jv(s - n, b) * np.exp(1j * (s - n) * phi)
                  for n in range(-30, 31))
        eff = jv(s, 2 * b * np.cos(phi / 2))
        assert abs(abs(coh) - abs(eff)) < 1e-10


def test_normalisation_both_limits():
    for kw in ({}, {"drive_hz": 579.634e6, "retro_delay_s": (0.5e-9, 1.17e-9)}):
        w = comb_tooth_weights(5.32, n_orders=40, **kw)
        assert abs(w[0] + 2 * w[1:].sum() - 1.0) < 1e-6


def test_campaign_drive_is_the_zero_delay_limit():
    """At 12.5 MHz the correction on the teeth the record USES is 2e-3.

    The bound covers s = 0..2, which carry more than 99 per cent of the
    comb's light and every committed use (the fold evidence reads slots
    +-1 and +-2). The far teeth s >= 3 correct by up to half a per cent of
    values that are themselves below 5e-3 of the comb, which moves nothing.
    """
    p = comb_tooth_weights(1.569, 3)
    a = comb_tooth_weights(1.569, 3, drive_hz=12.5e6,
                           retro_delay_s=(0.5e-9, 1.17e-9))
    assert np.all(np.abs(a - p) / p < 3e-3)


def test_smeared_carrier_never_nulls():
    w = comb_tooth_weights(2.405, 3, drive_hz=579.634e6,
                           retro_delay_s=(0.5e-9, 1.17e-9))
    assert w[0] > 0.5                      # against 0.0 in the pristine limit


def test_coincidence_tooth_dies_on_the_common_path():
    p = comb_tooth_weights(5.32, 5)
    a = comb_tooth_weights(5.32, 5, drive_hz=579.634e6,
                           retro_delay_s=(0.5e-9, 1.17e-9))
    assert p[4] > 0.15 and a[4] < 0.01     # the 50x collapse, both asserted
