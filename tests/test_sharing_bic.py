"""
Closure for the sigma_laser sharing BIC (rb5s6s/sharing_bic.py).

The score must DETECT real sharing structure when the data have the power: on
synthetic blocks where the four peaks genuinely share one sigma_laser it must
favour per_T (shared), and on blocks where they carry grossly different
sigma_laser it must favour per_block. That the archive itself is underpowered to
resolve this (M4c) is exactly why the closure uses clean, high-SNR synthetics.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.density import density_units
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency, transit_fwhm_at_T
from rb5s6s.sharing_bic import sharing_bic

RATE_T = 0.08514
NU = to_frequency(np.arange(2000) * 0.5 - 500.0, RATE_T)
PEAKS = [("4207", 87), ("4121", 87), ("4192", 85), ("4154", 85)]


def _blocks(sigma_of_peak, *, beta=(0.03, 0.03), noise_a=3e-3, nrep=7, seed=7):
    """Synthetic (peak, T) blocks with sigma_laser set by sigma_of_peak(peak).
    beta = (beta85, beta87). Low noise + several repeats give the BIC the power
    the real archive lacks."""
    b85, b87 = beta
    rng = np.random.default_rng(seed)
    blocks = []
    for peak, iso in PEAKS:
        for T in (70.0, 90.0, 110.0):
            N = density_units(T)
            gc = (b85 if iso == 85 else b87) * N
            sl = sigma_of_peak(peak)
            transit = transit_fwhm_at_T(T, 0.9)
            freqs, volts = [], []
            for _ in range(nrep):
                c = rng.normal(0.0, 1.0)
                g = 1.0 * (1.0 + rng.normal(0.0, 0.03))
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
def test_shared_synthetic_favours_per_T():
    # all four peaks share one sigma_laser -> the per-block freedom is not
    # warranted, so BIC favours the shared per_T model (dBIC > 0).
    r = sharing_bic(_blocks(lambda peak: 1.6), transit_ref_mhz=0.9)
    assert r["dBIC"] > 2.0, r
    assert r["favours"].startswith("per_T")
    # nesting sanity: the richer per_block model fits at least as well (lower
    # chi2, up to optimiser slop) -- but not enough to pay for its 9 extra params
    assert r["models"]["per_block"]["chi2_eff"] <= r["models"]["per_T"]["chi2_eff"] + 1.0


@pytest.mark.slow
def test_split_synthetic_favours_per_block():
    # grossly different sigma_laser per peak -> the shared model fits badly, so
    # the 9 extra parameters pay for themselves and BIC favours per_block.
    sig = {"4207": 1.0, "4121": 2.0, "4192": 3.0, "4154": 4.0}
    r = sharing_bic(_blocks(lambda peak: sig[peak], noise_a=2.5e-3, nrep=8, seed=11),
                    transit_ref_mhz=0.9)
    assert r["dBIC"] < -2.0, r
    assert r["favours"].startswith("per_block")
