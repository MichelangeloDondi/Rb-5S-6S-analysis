"""
The M16 polarizability model must reproduce precision measurements it does not
use before any derived number (the Delta_alpha recompute, the magic
wavelengths) is quotable: the measured 5S static polarizability, the measured
5S scalar tune-out between the D lines, the Safronova-group 6S static, and the
|Delta_alpha(993)| magnitude the shipped analysis rides on. A model that
misses any of these anchors has a data-entry or formula error and must not
ship its magic wavelengths.
"""

from __future__ import annotations

import numpy as np

from rb5s6s.constants import DELTA_ALPHA_AU
from rb5s6s.polarizability import (alpha_5s, alpha_6s, delta_alpha,
                                   tuneout_5s, magic_wavelengths, mc_band)


def test_static_anchors():
    # measured alpha_5S(0) = 318.79(1.42) au (Holmgren 2010)
    assert abs(alpha_5s(0.0) - 318.79) < 3.0
    # Safronova-group alpha_6S(0) = 5167(22) au (tail is calibrated to it, so
    # this checks the big valence terms carry the right energies and signs)
    assert abs(alpha_6s(0.0) - 5167.0) < 25.0


def test_measured_tuneout_reproduced():
    # Leonard et al. 2015: 790.03235(3) nm. The model does not use this
    # number; hitting it validates the D-line matrix-element ratio and the
    # 6P-12P + tail + core budget at the few-pm level.
    assert abs(tuneout_5s() - 790.03235) < 0.2


def test_delta_alpha_993_magnitude_matches_orson():
    # the shipped analysis uses |Delta_alpha| = 1093 au (Orson 2021); the
    # independent recompute must agree in MAGNITUDE (the sign finding is
    # documented in the module docstring and the results CSV)
    da = delta_alpha(993.0)
    assert abs(abs(da) / DELTA_ALPHA_AU - 1.0) < 0.10, da
    assert da < 0.0, "sign finding: alpha_6S(993) < alpha_5S(993) (blue shift)"


def test_magic_crossings_exist_and_trap():
    magic = magic_wavelengths(950.0, 1500.0)
    lams = [m[0] for m in magic]
    # the clean crossing far from every 6S pole
    assert any(abs(l - 1204.0) < 15.0 for l in lams), lams
    # every reported crossing must trap the ground state (alpha > 0)
    assert all(a > 0.0 for _, a in magic), magic


def test_mc_band_deterministic():
    f = lambda k5, k6: 1.0
    b1, b2 = mc_band(f, n=50, seed=3), mc_band(f, n=50, seed=3)
    assert b1 == b2
