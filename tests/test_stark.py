"""
Tests for the AC-Stark power-sweep bound (rb5s6s/stark.py, M4e).

The headline is a SYNTHETIC CLOSURE: build FWHM-vs-power points from the forward
model with a KNOWN kappa (large enough that the ramp broadening is well above
the injected noise), then check fit_stark_sweep recovers it. Plus monotonicity
unit checks (kappa=0 -> flat width; bigger kappa -> more broadening) that pin
the physics the archival bound rests on.
"""

from __future__ import annotations

import numpy as np

from rb5s6s.stark import fit_stark_sweep, _fwhm_of
from rb5s6s.linefit import transit_fwhm_at_T
from rb5s6s.config import TRANSIT_FWHM_PLACEHOLDER_MHZ

# the synthetic forward model must use the SAME transit the fit assumes, else the
# power-independent core absorbs the mismatch and the closure breaks (this is the
# corrected placeholder, ~1.2 MHz at the 50 um w0 prior; was 0.9 at 32 um).
_TREF = TRANSIT_FWHM_PLACEHOLDER_MHZ

POWERS = (0.025, 0.075, 0.125, 0.175, 0.225)   # W
PEAKS = ("4121", "4154", "4192", "4207")
NU = np.arange(-45.0, 45.0, 0.01)


def _synth_grid(kappa_true, core_by_peak, *, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    transit = transit_fwhm_at_T(130.0, _TREF)
    grid = {}
    for peak in PEAKS:
        for P in POWERS:
            f = _fwhm_of(0.6, core_by_peak[peak], transit, kappa_true * P, NU)
            f += noise * rng.standard_normal()
            grid[(peak, P)] = (f, max(noise, 0.02))
    return grid


def test_kappa_zero_is_flat_and_more_kappa_broadens():
    transit = transit_fwhm_at_T(130.0, _TREF)
    f_lo = _fwhm_of(0.6, 1.6, transit, 0.0, NU)
    f_hi = _fwhm_of(0.6, 1.6, transit, 4.0, NU)          # S0 = 4 MHz on-axis
    assert f_hi > f_lo + 0.3                              # the ramp broadens
    # width is monotonic in S0
    ws = [_fwhm_of(0.6, 1.6, transit, s0, NU) for s0 in (0.0, 1.0, 2.0, 4.0)]
    assert all(b >= a - 1e-6 for a, b in zip(ws, ws[1:]))


def test_stark_sweep_recovers_injected_kappa():
    # strong, cleanly-detectable kappa so the closure is meaningful
    kappa_true = 15.0                                    # MHz/W (S0@225mW = 3.4)
    cores = {"4121": 1.55, "4154": 1.70, "4192": 1.60, "4207": 1.75}
    grid = _synth_grid(kappa_true, cores, noise=0.02, seed=3)
    res = fit_stark_sweep(grid, profile=False)
    assert abs(res["kappa"] - kappa_true) < max(4 * res["kappa_err"], 2.0), res
    # the per-peak cores come back close to injected
    for peak in PEAKS:
        assert abs(res["sigma_laser_by_peak"][peak] - cores[peak]) < 0.15


def test_stark_sweep_upper_bound_brackets_zero_signal():
    # kappa_true = 0: the fit must be consistent with 0 and return a finite,
    # positive one-sided upper bound (the archival situation).
    cores = {p: 1.6 for p in PEAKS}
    grid = _synth_grid(0.0, cores, noise=0.03, seed=7)
    res = fit_stark_sweep(grid, profile=False)
    assert res["kappa_ub95"] > 0.0 and np.isfinite(res["kappa_ub95"])
    assert res["kappa"] < res["kappa_ub95"]
    assert res["S0_225_ub95"] == res["kappa_ub95"] * 0.225


def test_stark_profile_bound_covers_truth_and_zero_case():
    # The QUOTED bound is the profile-likelihood one. Two closures on a coarse
    # frequency grid (nu_step=0.1 -- the profile curve was checked grid-stable
    # at 0.01 vs 0.02 on the real data; the tolerance here is generous):
    # (a) strong injected kappa: the one-sided 95% UB must sit ABOVE the truth
    #     and above the best fit;
    # (b) zero signal (the archival situation): the UB must be finite, positive,
    #     and BELOW the Wald bound evaluated at the kappa=0 rail, where the
    #     vanishing gradient makes the Wald sigma a finite-difference artifact
    #     (that inflated Wald "bound" is exactly what this construction replaces).
    cores = {p: 1.6 for p in PEAKS}
    grid = _synth_grid(15.0, cores, noise=0.02, seed=3)
    res = fit_stark_sweep(grid, profile=True, nu_step=0.1)
    assert np.isfinite(res["kappa_ub95_profile"])
    assert res["kappa_ub95_profile"] > res["kappa"]
    assert res["kappa_ub95_profile"] > 15.0
    assert res["S0_225_ub95_profile"] == res["kappa_ub95_profile"] * 0.225

    grid0 = _synth_grid(0.0, cores, noise=0.03, seed=7)
    res0 = fit_stark_sweep(grid0, profile=True, nu_step=0.1)
    assert np.isfinite(res0["kappa_ub95_profile"]) and res0["kappa_ub95_profile"] > 0.0
    assert res0["kappa_ub95_profile"] < res0["kappa_ub95"]
