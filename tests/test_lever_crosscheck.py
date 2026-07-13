"""
Closure + invariant tests for the lever cross-check for beta_self (lever_crosscheck.py).

The headline test is a SYNTHETIC CLOSURE: generate traces from the forward
model with a KNOWN, isotope-distinct beta, run the whole lever_crosscheck_beta
machinery (the 2x2 model-form matrix + the assembly of the three error bars),
and check it recovers both injected betas within the fit error. That validates
the entire 20-trace joint-fit pipeline end to end -- if the sharing indices,
the profile cache, or the isotope tying were wrong, the injected value would
not come back. A cheap fast test guards the return structure and the
error-bar invariants (the full 2x2 spread is at least each single axis).
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.lineshape import composite_profile
from rb5s6s.linefit import transit_fwhm_at_T
from rb5s6s.density import density_units
from rb5s6s.lever_crosscheck import lever_crosscheck_beta, PRIMARY, GRID_CELLS
from rb5s6s.config import TRANSIT_FWHM_PLACEHOLDER_MHZ as TREF  # ~1.2 MHz (w0 50 um)


def _synth_block(peak, iso, T, beta, sigma_laser, transit_ref, *,
                 n=3, noise=0.008, seed=0):
    """One (peak, T) block of n synthetic traces from the exact forward model
    the fit uses: A * composite_profile(beta*N(T), sigma_laser, transit(T))
    shifted by a small per-trace drift, plus white noise. law=None makes the
    fit use its std(diff) fallback (correct for white noise)."""
    rng = np.random.default_rng(seed)
    N = density_units(float(T))
    g, prof = composite_profile(beta * N, sigma_laser,
                                transit_fwhm_at_T(float(T), transit_ref))
    nu = np.arange(-25.0, 25.0, 0.25)
    freqs, volts = [], []
    for _ in range(n):
        A = 1.0 + 0.03 * rng.standard_normal()
        c = 0.25 * rng.standard_normal()            # small drift = per-trace center
        model = A * np.interp(nu - c, g, prof, left=0.0, right=0.0)
        volts.append(model + noise * rng.standard_normal(nu.size))
        freqs.append(nu.copy())
    return {"peak": peak, "isotope": iso, "T_C": float(T), "N_units": N,
            "freqs": freqs, "volts": volts, "law": None}


def _synth_dataset(beta85, beta87, *, temps=(70, 90, 110), peaks_per_iso=2,
                   sigma_laser=1.5, transit_ref=TREF, n=3, noise=0.008):
    blocks, seed = [], 0
    specs = []
    for k in range(peaks_per_iso):
        specs.append((f"P85_{k}", 85, beta85))
        specs.append((f"P87_{k}", 87, beta87))
    for peak, iso, beta in specs:
        for T in temps:
            blocks.append(_synth_block(peak, iso, T, beta, sigma_laser,
                                       transit_ref, n=n, noise=noise, seed=seed))
            seed += 1
    return blocks


def test_lever_crosscheck_structure_and_errorbar_invariants():
    # cheap: tiny dataset, no w0 band / no LOO. Check the object shape and that
    # the full 2x2 spread bounds each single model-form axis.
    blocks = _synth_dataset(0.10, 0.06, temps=(70, 110), peaks_per_iso=1,
                            n=2, noise=0.01)
    res = lever_crosscheck_beta(blocks, transit_ref_mhz=TREF,
                          do_w0_band=False, do_loo=False)
    assert res["primary"] == PRIMARY
    assert set(res["isotopes"]) == {85, 87}
    assert len(res["grid"]) == len(GRID_CELLS) == 3
    for iso in (85, 87):
        mf = res["err_modelform"][iso]
        assert mf >= 0.0
        # max-min over the 4 grid cells is >= any pairwise (single-axis) diff
        assert mf >= res["err_transit"][iso] - 1e-9
        assert mf >= res["err_sharing"][iso] - 1e-9
        assert res["err_statistical"][iso] > 0.0


@pytest.mark.slow
def test_lever_crosscheck_beta_recovers_injected_beta():
    # closure: inject isotope-distinct beta, recover both. Exercises the full
    # 2x2 grid; then a second run with the w0-band and LOO paths on to prove
    # they execute and stay finite (LOO shift small since the data is clean).
    beta85, beta87 = 0.10, 0.06
    blocks = _synth_dataset(beta85, beta87)
    res = lever_crosscheck_beta(blocks, transit_ref_mhz=TREF,
                          do_w0_band=False, do_loo=False)
    b85, e85 = res["headline"][85], res["err_statistical"][85]
    b87, e87 = res["headline"][87], res["err_statistical"][87]
    assert abs(b85 - beta85) < max(5 * e85, 0.02), (b85, e85)
    assert abs(b87 - beta87) < max(5 * e87, 0.02), (b87, e87)
    assert b85 > b87                       # isotopes distinguished
    # transit axis should be the dominant model-form term (cusp vs Voigt)
    assert res["err_transit"][85] >= res["err_sharing"][85] - 1e-6

    # path-coverage for the w0-band and LOO branches on a SMALL dataset (keeps
    # CI cheap: LOO refits once per block, so few blocks == few fits)
    small = _synth_dataset(0.10, 0.06, temps=(70, 110), peaks_per_iso=1,
                           n=2, noise=0.01)
    res2 = lever_crosscheck_beta(small, transit_ref_mhz=TREF,
                           do_w0_band=True, do_loo=True)
    lo, hi = res2["w0_band"][85]
    assert lo <= res2["headline"][85] <= hi + 1e-9   # headline inside its band
    dp, _ = res2["loo_peak"][85]
    dt, _ = res2["loo_temp"][85]
    assert np.isfinite(dp) and dp >= 0.0             # peak-LOO ran
    assert np.isfinite(dt) and dt >= 0.0             # temperature-LOO ran
