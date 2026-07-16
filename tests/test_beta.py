"""
Closure tests for the global beta_self fit (rb5s6s/beta.py).

The gate for the headline collisional-broadening result: before any real
beta_self is believed, the global multi-temperature fit must recover a KNOWN
injected beta_self from campaign-like synthetic data, demonstrate that it
does so where a single-condition fit could not (degeneracy broken by the
density lever arm), and report zero collisional broadening as consistent
with zero.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s.constants import GAMMA_NAT_HZ
from rb5s6s.density import density_units
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency, transit_fwhm_at_T, fit_condition
from rb5s6s.beta import fit_beta_self, collisional_slope

GNAT = GAMMA_NAT_HZ / 1e6
RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)


def synth_peak(beta_self, sigma_laser, transit_ref=0.9, temps=(70.0, 90.0, 110.0),
               amp=1.0, drift=1.0, noise_a=5e-3, ntr=5, seed=C.RNG_SEED):
    """One peak's worth of synthetic conditions at several temperatures, with
    gamma_coll(T) = beta_self * N(T) (density units), shared sigma_laser."""
    rng = np.random.default_rng(seed)
    conds = []
    for T in temps:
        N = density_units(T)
        gc = beta_self * N
        transit = transit_fwhm_at_T(T, transit_ref)
        freqs, volts = [], []
        for _ in range(ntr):
            c = rng.normal(0.0, drift)
            g = amp * (1.0 + rng.normal(0.0, 0.03))
            prof = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=sigma_laser,
                                 transit_fwhm=transit)
            v = g * prof / prof.max()
            sig = np.sqrt(noise_a ** 2 + 2e-5 * np.maximum(v, 0.0))
            volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
            freqs.append(NU.copy())
        conds.append({"T_C": T, "N_units": N, "freqs": freqs, "volts": volts, "law": None})
    return conds


def test_recovers_injected_beta():
    beta_true = 0.15  # MHz per 1e12 cm^-3
    conds = synth_peak(beta_self=beta_true, sigma_laser=1.2)
    fit = fit_beta_self(conds, transit_ref_mhz=0.9)
    assert abs(fit["beta_self"] - beta_true) < 3 * fit["beta_self_err"] + 0.02, fit
    assert abs(fit["sigma_laser"] - 1.2) < 0.25, fit


def test_zero_beta_recovered_near_zero():
    conds = synth_peak(beta_self=0.0, sigma_laser=1.2)
    fit = fit_beta_self(conds, transit_ref_mhz=0.9)
    # consistent with zero within ~3 sigma (bounded below at 0)
    assert fit["beta_self"] < 3 * fit["beta_self_err"] + 0.03, fit


def test_global_beats_single_condition_degeneracy():
    # At a SINGLE temperature the laser/coll split is degenerate and gamma_coll
    # is poorly determined; the GLOBAL fit across 3 T pins beta_self far
    # better. Compare the implied gamma_coll error at 110 C.
    beta_true = 0.20
    conds = synth_peak(beta_self=beta_true, sigma_laser=1.5, noise_a=8e-3)
    single = fit_condition(conds[2]["freqs"], conds[2]["volts"], T_C=110.0,
                           transit_fwhm=transit_fwhm_at_T(110.0, 0.9))
    glob = fit_beta_self(conds, transit_ref_mhz=0.9)
    # global gamma_coll error at 110 C = beta_err * N(110)
    N110 = density_units(110.0)
    glob_gc_err = glob["beta_self_err"] * N110
    assert glob_gc_err < single["gamma_coll_err"], (glob_gc_err, single["gamma_coll_err"])
    assert abs(glob["beta_self"] - beta_true) < 3 * glob["beta_self_err"] + 0.03


@pytest.mark.slow
def test_unbiased_across_seeds():
    beta_true = 0.15
    vals, errs = [], []
    for s in range(1, 8):
        fit = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2, seed=s),
                            transit_ref_mhz=0.9)
        vals.append(fit["beta_self"]); errs.append(fit["beta_self_err"])
    mean, sem = np.mean(vals), np.std(vals) / np.sqrt(len(vals))
    assert abs(mean - beta_true) < 3 * sem + 0.02, (mean, sem, vals)


def test_collisional_slope_clean_monotonic_is_measurement():
    # Widths rising cleanly with density, tiny within-block errors and small
    # residual => a MEASUREMENT-quality slope.
    N = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    beta = 0.05
    W = 5.0 + beta * N          # perfectly on the line
    E = np.array([0.01, 0.01, 0.01])
    res = collisional_slope(N, W, E)
    assert res["monotonic"] and res["verdict"] == "MEASUREMENT"
    assert abs(res["beta_eff"] - beta) < 0.01
    assert res["resid_rms"] < 0.02


def test_collisional_slope_nonmonotonic_is_bound():
    # A non-monotonic width sequence (higher density -> narrower somewhere)
    # cannot be pure collisional broadening: large residual, BOUND verdict,
    # and the between-block systematic must dwarf the formal error.
    N = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    W = np.array([5.11, 4.87, 5.28])  # the real 4207 pattern
    E = np.array([0.07, 0.03, 0.02])
    res = collisional_slope(N, W, E)
    assert not res["monotonic"] and res["verdict"] == "BOUND"
    assert res["syst_err"] > 2 * res["formal_err"]  # systematic dominates


def test_collisional_slope_bound_coverage_construction():
    # The 95% bound must honour the scatter's own degrees of freedom (Student-t,
    # NOT the asymptotic 2) and carry the density-scale systematic on top.
    from scipy.stats import t as student_t
    from rb5s6s.density import N_SCALE_FRAC_SYST

    # 3 points -> dof = 1 -> t95 = 6.31; 4 points -> dof = 2 -> t95 = 2.92
    N3 = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    r3 = collisional_slope(N3, np.array([5.11, 4.87, 5.28]),
                           np.array([0.07, 0.03, 0.02]))
    assert r3["dof"] == 1
    assert abs(r3["t95"] - student_t.ppf(0.95, 1)) < 1e-9      # 6.314
    assert abs(r3["bound95"] - (abs(r3["beta_eff"]) + r3["t95"] * r3["syst_err"])) < 1e-12

    N4 = np.array([density_units(t) for t in (70.0, 90.0, 110.0, 130.0)])
    r4 = collisional_slope(N4, np.array([5.11, 4.87, 5.28, 5.35]),
                           np.array([0.07, 0.03, 0.02, 0.03]))
    assert r4["dof"] == 2
    assert abs(r4["t95"] - student_t.ppf(0.95, 2)) < 1e-9      # 2.920

    # the N-scale inflation rides on the + side of the bound
    for r in (r3, r4):
        assert r["n_frac_syst"] == N_SCALE_FRAC_SYST
        assert abs(r["bound95_nscale"] - r["bound95"] * (1 + N_SCALE_FRAC_SYST)) < 1e-12
        assert r["bound95_nscale"] > r["bound95"]


@pytest.mark.slow
def test_with_130C_extends_lever_arm():
    # Adding the 130 C (highest-density) point should tighten beta_self.
    beta_true = 0.15
    three = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2,
                                     temps=(70.0, 90.0, 110.0)), transit_ref_mhz=0.9)
    four = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2,
                                    temps=(70.0, 90.0, 110.0, 130.0)), transit_ref_mhz=0.9)
    assert four["beta_self_err"] < three["beta_self_err"], (four, three)
