"""
Closure tests for the hierarchical fit (rb5s6s/global_fit.py).

Before trusting a cross-peak/cross-temperature beta, the fit must recover
KNOWN per-isotope betas AND a KNOWN per-temperature sigma_laser drift from
campaign-like synthetics -- the whole point being that sharing sigma_laser
across the 4 peaks at each T pins sigma_laser(T) even when it drifts, so beta
is not contaminated by that drift.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s.density import density_units
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency, transit_fwhm_at_T
from rb5s6s.global_fit import fit_global

RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)
# two isotopes, two peaks each (like 87: 4207/4121; 85: 4192/4154)
PEAKS = [("4207", 87), ("4121", 87), ("4192", 85), ("4154", 85)]


def synth_blocks(beta_by_iso, sigma_by_T, transit_ref=0.9,
                 temps=(70.0, 90.0, 110.0), amp=1.0, noise_a=6e-3, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    blocks = []
    for peak, iso in PEAKS:
        for T in temps:
            N = density_units(T)
            gc = beta_by_iso[iso] * N
            sl = sigma_by_T[T]
            transit = transit_fwhm_at_T(T, transit_ref)
            freqs, volts = [], []
            for _ in range(5):
                c = rng.normal(0.0, 1.0)
                g = amp * (1.0 + rng.normal(0.0, 0.03))
                prof = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=sl,
                                     transit_fwhm=transit)
                v = g * prof / prof.max()
                sig = np.sqrt(noise_a ** 2 + 2e-5 * np.maximum(v, 0.0))
                volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
                freqs.append(NU.copy())
            blocks.append({"peak": peak, "isotope": iso, "T_C": T, "N_units": N,
                           "freqs": freqs, "volts": volts, "law": None})
    return blocks


@pytest.mark.slow
def test_recovers_per_isotope_beta_and_drifting_sigma():
    beta_true = {85: 0.05, 87: 0.02}           # isotopes genuinely differ
    sigma_true = {70.0: 1.0, 90.0: 1.4, 110.0: 0.9}  # NON-monotonic laser drift
    blocks = synth_blocks(beta_true, sigma_true)
    fit = fit_global(blocks, transit_ref_mhz=0.9)
    # per-isotope beta recovered and the two isotopes resolved as different
    for iso in (85, 87):
        assert abs(fit["beta_by_isotope"][iso] - beta_true[iso]) < \
            3 * fit["beta_err_by_isotope"][iso] + 0.02, fit["beta_by_isotope"]
    assert fit["beta_by_isotope"][85] > fit["beta_by_isotope"][87]
    # the sigma_laser(T) DRIFT is recovered, including its non-monotonicity
    sl = fit["sigma_laser_by_T"]
    for T in (70.0, 90.0, 110.0):
        assert abs(sl[T] - sigma_true[T]) < 0.25, sl
    assert sl[90.0] > sl[70.0] and sl[90.0] > sl[110.0]  # the injected bump


@pytest.mark.slow
def test_equal_isotopes_recovered_equal():
    beta_true = {85: 0.03, 87: 0.03}
    sigma_true = {70.0: 1.1, 90.0: 1.1, 110.0: 1.1}
    fit = fit_global(synth_blocks(beta_true, sigma_true, seed=3), transit_ref_mhz=0.9)
    b85, b87 = fit["beta_by_isotope"][85], fit["beta_by_isotope"][87]
    e = fit["beta_err_by_isotope"][85] + fit["beta_err_by_isotope"][87]
    assert abs(b85 - b87) < 3 * e + 0.02, (b85, b87)


def test_fit_global_runs_on_real_data():
    # DATA-VALIDATED smoke test (review round 5 #2): the headline fit must
    # RUN on the actual archive traces, not only on synthetics it generated.
    # Builds 2 peaks x 2 temperatures from data_raw at a fixed sane rate and
    # asserts convergence + a sane chi2_red. (Not a physics claim -- a
    # does-it-run-and-not-crash gate; the real rates come from M2 at pipeline
    # time.)
    import csv as _csv
    from rb5s6s.config import DATA_RAW_DIR, MANIFEST_CSV
    from rb5s6s.ingest import load_trace
    from rb5s6s.density import density_units
    from rb5s6s.constants import PEAKS
    rate_t = 0.08514  # transition axis, the M2 campaign value
    rows = list(_csv.DictReader(open(MANIFEST_CSV)))
    blocks = []
    for peak in ("4192", "4207"):          # one 85Rb, one 87Rb
        for T in ("90", "110"):
            recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                    and r["peak"] == peak and r["temperature_C"] == T][:4]
            if len(recs) < 3:
                continue
            fv = [load_trace(DATA_RAW_DIR / r["file"]) for r in recs]
            blocks.append({"peak": peak, "isotope": PEAKS[peak]["isotope"],
                           "T_C": float(T), "N_units": density_units(float(T)),
                           "freqs": [t * rate_t for t, _ in fv],
                           "volts": [v for _, v in fv], "law": None})
    assert len(blocks) >= 3
    fit = fit_global(blocks, transit_ref_mhz=0.9)          # must not raise
    assert 0.3 < fit["chi2_red"] < 5.0, fit["chi2_red"]    # sane fit on real data
    for iso in fit["beta_keys"]:
        assert np.isfinite(fit["beta_by_isotope"][iso])
        assert np.isfinite(fit["beta_err_by_isotope"][iso])
