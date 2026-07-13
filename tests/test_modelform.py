"""
Closure tests for the model-form comparison (rb5s6s/modelform.py).

The BIC comparison must (a) recover the right shape parameters, and (b) point
to the RIGHT model when the truth is known: data generated with a strong
transit exponential and no laser must prefer 'lehmann'; data generated as a
pure Voigt must prefer 'voigt'. This is what licenses trusting the archival
dBIC verdict.
"""

from __future__ import annotations

import numpy as np

from rb5s6s import config as C
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency
from rb5s6s.modelform import fit_form, compare_forms

RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)


def synth(gc, sl, tr, amp=1.0, noise=4e-3, ntr=5, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    fs, vs = [], []
    for _ in range(ntr):
        c = rng.normal(0.0, 0.5)
        prof = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=max(sl, 1e-3),
                             transit_fwhm=max(tr, 1e-3))
        v = amp * prof / prof.max()
        vs.append(v + rng.normal(0.0, noise, len(v))); fs.append(NU.copy())
    return fs, vs


def test_prefers_lehmann_when_cusp_present():
    # Strong transit exponential, negligible laser -> 'lehmann' must win, and
    # by a decisive margin at good SNR.
    fs, vs = synth(gc=0.3, sl=0.05, tr=2.5, noise=3e-3)
    out = compare_forms(fs, vs, kinds=("voigt", "lehmann"))
    assert out["dBIC_voigt_minus_lehmann"] > 10, out["dBIC_voigt_minus_lehmann"]


def test_prefers_voigt_when_gaussian_present():
    # Strong Gaussian, negligible transit -> 'voigt' must win.
    fs, vs = synth(gc=0.3, sl=2.5, tr=0.05, noise=3e-3)
    out = compare_forms(fs, vs, kinds=("voigt", "lehmann"))
    assert out["dBIC_voigt_minus_lehmann"] < -10, out["dBIC_voigt_minus_lehmann"]


def test_shape_params_recovered():
    fs, vs = synth(gc=1.0, sl=2.0, tr=0.05, noise=3e-3)
    r = fit_form(fs, vs, "voigt")
    assert abs(r["shape"]["gauss"] - 2.0) < 0.4, r["shape"]
    assert 0.6 < r["chi2_red"] < 1.5, r["chi2_red"]
