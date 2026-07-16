"""
Adversarial validation of the nested model ladder (rb5s6s/model_ladder.py).

This is the test that answers the referee's "could your pipeline invent a
signal?" -- and its converse. On synthetic spectra built with a KNOWN AC-Stark
shift the ladder must decide D (+Stark) is warranted; on spectra built with
S0 = 0 it must STOP at C, i.e. it must not add an AC-Stark parameter the data
do not support. Both use BIC on the same nested models the real analysis uses.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency
from rb5s6s.model_ladder import fit_ladder
from rb5s6s import config as C

RATE_T = 0.08514
NU = to_frequency(np.arange(2000) * 0.5 - 500.0, RATE_T)
_TRANSIT = 1.2   # MHz, the fixed transit width the ladder assumes (w0 prior)


def _synth(s0, *, drift, noise, ntr, gamma_coll=0.4, sigma_laser=1.4,
           transit=_TRANSIT, seed=3):
    """`drift` = per-scan centre jitter (MHz); the drifted-lock vs stable-lock
    knob. `noise` = the a-term of the M1-like signal-dependent noise."""
    rng = np.random.default_rng(seed)
    freqs, volts = [], []
    for _ in range(ntr):
        c = rng.normal(0.0, drift)
        prof = model_profile(NU - c, gamma_coll=gamma_coll, sigma_laser_fwhm=sigma_laser,
                             transit_fwhm=transit, s0=s0)
        v = prof / prof.max()
        sig = np.sqrt(noise ** 2 + 2e-5 * np.maximum(v, 0.0))
        volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
        freqs.append(NU.copy())
    return freqs, volts


@pytest.mark.slow
def test_ladder_detects_stark_under_a_stable_lock():
    # STABLE lock (no per-scan drift): an injected S0 IS identifiable per
    # condition, so the ladder must decisively warrant the +Stark rung and
    # recover S0. This is the fixed-lock epoch -- the ladder *can* find a Stark
    # shift when the data support it (so the null result below is not blindness).
    freqs, volts = _synth(s0=5.0, drift=0.0, noise=5e-4, ntr=8)
    r = fit_ladder(freqs, volts, transit_fwhm=_TRANSIT)
    assert r["rungs"]["A_voigt->B_transit"]["dBIC"] > 10           # transit real too
    assert r["rungs"]["C_collisions->D_stark"]["dBIC"] > 10, r["rungs"]
    assert abs(r["models"]["D_stark"]["shape"]["s0"] - 5.0) < 0.5  # S0 recovered


@pytest.mark.slow
def test_ladder_cannot_measure_stark_under_drift():
    # DRIFTED lock (the 2025 archive): even a large S0 = 8 MHz is NOT warranted,
    # because the free per-scan centres that absorb the drift also absorb the
    # ramp's pull, leaving only the sub-detectable skew. This is the two-epoch
    # thesis as a model-comparison: the archive can only BOUND the Stark.
    freqs, volts = _synth(s0=8.0, drift=1.0, noise=3e-3, ntr=5)
    d = r = fit_ladder(freqs, volts, transit_fwhm=_TRANSIT)["rungs"]["C_collisions->D_stark"]["dBIC"]
    assert d < 6, f"drifted archive should not warrant +Stark, got dBIC={d:.1f}"


@pytest.mark.slow
def test_ladder_does_not_invent_a_stark_shift():
    # S0 = 0 in clean data: even with NO drift the +Stark rung must NOT clear the
    # gate -- the ladder cannot fabricate a shift that is not there.
    freqs, volts = _synth(s0=0.0, drift=0.0, noise=5e-4, ntr=8)
    d = fit_ladder(freqs, volts, transit_fwhm=_TRANSIT)["rungs"]["C_collisions->D_stark"]["dBIC"]
    assert d < 6, f"ladder invented +Stark on S0=0 data (dBIC={d:.1f})"
