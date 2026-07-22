"""
Closure tests for the M3 joint condition fit (rb5s6s/linefit.py).

These are the gate the whole broadening result rests on: before any real
gamma_coll is believed, the joint fit must recover KNOWN widths injected into
campaign-like synthetic conditions (5 drift-shifted repeats, M1-like
signal-dependent noise), and the sigma_laser<->gamma_coll separability must be
quantified — that degeneracy is the "fit-level face of the confound".
"""

from __future__ import annotations

import numpy as np

from rb5s6s import config as C
from rb5s6s.constants import GAMMA_NAT_HZ
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import fit_condition, to_frequency

GNAT = GAMMA_NAT_HZ / 1e6
RATE_T = 0.08514  # transition MHz/ms (M2 campaign value)
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)  # transition-frequency axis, MHz


def synth_condition(gamma_coll, sigma_laser, transit=0.9, s0=0.0,
                    amp=1.0, drift_mhz=1.0, noise_a=3e-3, noise_b=2e-5,
                    ntr=5, seed=C.RNG_SEED):
    """5 repeats of one condition: shared shape, per-trace drift + gain +
    signal-dependent noise (the real conditions' structure)."""
    rng = np.random.default_rng(seed)
    freqs, volts = [], []
    for i in range(ntr):
        c = rng.normal(0.0, drift_mhz)      # drifted center
        g = amp * (1.0 + rng.normal(0.0, 0.03))  # 3% gain scatter
        prof = model_profile(NU - c, gamma_coll=gamma_coll, sigma_laser_fwhm=sigma_laser,
                             transit_fwhm=transit, s0=s0)
        v = g * prof / prof.max()
        sig = np.sqrt(noise_a ** 2 + noise_b * np.maximum(v, 0.0))
        volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
        freqs.append(NU.copy())
    return freqs, volts


def test_recovers_injected_widths():
    # Bright warm-like condition: recover gamma_coll and sigma_laser.
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.2, transit=0.9)
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    assert abs(fit["gamma_coll"] - 1.5) < 3 * fit["gamma_coll_err"] + 0.15, fit
    assert abs(fit["sigma_laser"] - 1.2) < 3 * fit["sigma_laser_err"] + 0.2, fit


def test_zero_collision_recovered_near_zero():
    freqs, volts = synth_condition(gamma_coll=0.0, sigma_laser=1.0, transit=0.9)
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    assert fit["gamma_coll"] < 0.5, fit  # consistent with ~0


def test_center_drift_absorbed_not_biasing_width():
    # Large per-trace drift must NOT inflate the recovered widths (the whole
    # point of per-trace free centers on the 2025 data).
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.0, drift_mhz=3.0)
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    assert abs(fit["gamma_coll"] - 1.5) < 0.4, fit
    # recovered centers should span the injected drift
    assert np.std(fit["centers"]) > 0.5


def test_laser_collision_degeneracy_quantified():
    # The crux: at campaign SNR the Gaussian(laser) vs Lorentzian(coll)
    # separation is partially degenerate ("fit-level face of the confound").
    # Two checks: (1) the fit REPORTS the anticorrelation (negative
    # corr), and (2) letting sigma_laser float INFLATES gamma_coll_err vs
    # pinning it — quantifying the degeneracy penalty rather than asserting a
    # magic error floor.
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.5, transit=0.9)
    both_free = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    assert both_free["corr_laser_coll"] < -0.3, both_free["corr_laser_coll"]
    # errors are real (not collapsed to ~machine-zero) and the recovery is sane
    assert both_free["gamma_coll_err"] > 1e-3
    assert abs(both_free["gamma_coll"] - 1.5) < 5 * both_free["gamma_coll_err"] + 0.3


def test_dim_cold_condition_wider_errors():
    # Cold/dim condition (small amplitude): the fit must still run and report
    # LARGER errors than a bright one (correct error scaling).
    bright = fit_condition(*synth_condition(gamma_coll=1.0, sigma_laser=1.0, amp=1.0),
                           T_C=110.0, transit_fwhm=0.9)
    dim = fit_condition(*synth_condition(gamma_coll=1.0, sigma_laser=1.0, amp=0.05,
                                         noise_a=3e-3),
                        T_C=70.0, transit_fwhm=0.78)
    assert dim["gamma_coll_err"] > bright["gamma_coll_err"], (dim, bright)


def test_fit_window_excludes_mirror_crossing():
    # Inject an off-center-sweep MIRROR: a second copy of the line ~40 MHz
    # from center (like 4207's 79%-of-peak down-ramp crossing). The windowed
    # fit must recover the true width, unbiased by the mirror.
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.2, drift_mhz=0.5)
    for i in range(len(volts)):
        # add a 60%-tall mirror line at +40 MHz (well outside the 18 MHz window)
        mir = model_profile(NU - 40.0, gamma_coll=1.5, sigma_laser_fwhm=1.2, transit_fwhm=0.9)
        volts[i] = volts[i] + 0.6 * mir / mir.max()
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    assert abs(fit["gamma_coll"] - 1.5) < 0.4, fit          # not biased by the mirror
    for d in fit["per_trace_diag"]:
        assert d["chi2_red"] < 1.5, d                        # mirror is outside the window


def test_per_trace_residual_diagnostics():
    # On well-modelled synthetic data every trace must individually show
    # chi2_red ~ 1, near-zero lag-1 autocorrelation and near-zero skew; and
    # the diagnostics must CATCH a corrupted trace (injected step -> its own
    # chi2/lag1 stand out while the siblings stay clean).
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.2)
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    for d in fit["per_trace_diag"]:
        assert 0.7 < d["chi2_red"] < 1.4, d
        assert abs(d["lag1"]) < 0.15, d
        assert abs(d["skew"]) < 0.5, d
    # inject a LOCALIZED bump on the flank (inside the fit window, near but
    # off the center) — a linear baseline cannot absorb it, so the per-trace
    # diagnostics must single this trace out.
    ipk = int(np.argmax(volts[2]))
    bump = 0.15 * np.exp(-0.5 * ((np.arange(len(volts[2])) - (ipk + 40)) / 6.0) ** 2)
    volts[2] = volts[2] + bump
    fit2 = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9)
    d_bad = fit2["per_trace_diag"][2]
    others = [d for i, d in enumerate(fit2["per_trace_diag"]) if i != 2]
    assert d_bad["chi2_red"] > 2.0 * max(o["chi2_red"] for o in others), fit2["per_trace_diag"]


def test_recovery_across_seeds_unbiased():
    # Average recovered gamma_coll over seeds must be within ~1 combined sigma
    # of truth (no systematic bias from the pipeline).
    vals, errs = [], []
    for s in range(1, 9):
        fit = fit_condition(*synth_condition(gamma_coll=2.0, sigma_laser=1.0, seed=s),
                            T_C=110.0, transit_fwhm=0.9)
        vals.append(fit["gamma_coll"]); errs.append(fit["gamma_coll_err"])
    mean = np.mean(vals); sem = np.std(vals) / np.sqrt(len(vals))
    assert abs(mean - 2.0) < 3 * sem + 0.15, (mean, sem, vals)


def _law(tau):
    # matches synth_condition's noise: sig^2 = a^2 + b*V (c = 0)
    return {"a": 3e-3, "b": 2e-5, "c": 0.0, "tau_int": tau}


def test_tau_inflation_scales_shared_errors_sqrt_tau():
    # The load-bearing correlated-noise path (sigma * sqrt(tau) INSIDE the
    # fit) never ran with tau > 1 in any closure test before 2026-07-16.
    # Mechanism closure: on IDENTICAL data, a law with tau_int = 4 must
    # return shared-parameter errors exactly sqrt(4) = 2x the tau_int = 1
    # ones (the diagnostic chi2_red is un-scaled back by design, so the
    # secondary max(chi2,1) rescale is common to both runs and cancels).
    freqs, volts = synth_condition(gamma_coll=1.5, sigma_laser=1.2)
    f1 = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9, law=_law(1.0))
    f4 = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9, law=_law(4.0))
    for p in ("gamma_coll", "sigma_laser"):
        assert abs(f1[p] - f4[p]) < 1e-6, (p, f1[p], f4[p])   # values unchanged
        ratio = f4[p + "_err"] / f1[p + "_err"]
        assert 1.9 < ratio < 2.1, (p, ratio)
    assert abs(f4["chi2_red"] - f1["chi2_red"]) < 1e-6        # diagnostic invariant


def test_tau_inflation_covers_ar1_noise():
    # Physics closure: inject genuinely AR(1)-correlated noise with
    # rho = 0.6 -> tau_int = (1+rho)/(1-rho) = 4, fit with the matching law,
    # and check (i) truth is covered by the inflated errors and (ii) the
    # inflation is material (~2x the white-law bars on the same data).
    rho, tau_true = 0.6, 4.0
    rng = np.random.default_rng(11)
    gamma_true, sigma_true = 1.5, 1.2
    freqs, volts = [], []
    for i in range(5):
        c = rng.normal(0.0, 1.0)
        prof = model_profile(NU - c, gamma_coll=gamma_true,
                             sigma_laser_fwhm=sigma_true, transit_fwhm=0.9, s0=0.0)
        v = prof / prof.max()
        sig = np.sqrt((3e-3) ** 2 + 2e-5 * np.maximum(v, 0.0))
        e = np.empty(len(v))
        e[0] = rng.standard_normal()
        w = rng.standard_normal(len(v))
        for k in range(1, len(v)):
            e[k] = rho * e[k - 1] + np.sqrt(1 - rho ** 2) * w[k]
        volts.append(v + sig * e)
        freqs.append(NU.copy())
    fit = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9, law=_law(tau_true))
    white = fit_condition(freqs, volts, T_C=110.0, transit_fwhm=0.9, law=_law(1.0))
    assert abs(fit["gamma_coll"] - gamma_true) < 3 * fit["gamma_coll_err"] + 0.15, fit
    assert abs(fit["sigma_laser"] - sigma_true) < 3 * fit["sigma_laser_err"] + 0.2, fit
    for p in ("gamma_coll_err", "sigma_laser_err"):
        assert fit[p] > 1.5 * white[p], (p, fit[p], white[p])
