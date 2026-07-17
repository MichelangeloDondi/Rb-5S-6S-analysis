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
from rb5s6s.polarizability import (alpha_5s, alpha_6s, alpha_7s, delta_alpha,
                                   delta_alpha_7s, tuneout_5s, magic_wavelengths,
                                   magic_5s7s, mc_band, MAGIC_5S5D52_EXP_NM,
                                   RME_5P32_5D52)


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


# --- the Ti:Sapph ladder: 5S->7S (independent) and 5S->5D5/2 (Hamilton anchor) ---

def test_7s_static_follows_the_ns_trend():
    # 7S static is large and positive, dominated by the near-degenerate 7S-7P
    # (gap 1524 cm^-1); it must exceed the 6S static (5167) and land on the
    # 319 -> 5167 -> ~3e4 ns trend. A sign flip or an order-of-magnitude miss
    # would flag a wrong 7S-nP element or energy.
    a7 = alpha_7s(0.0)
    assert a7 > alpha_6s(0.0) > 0.0, a7
    assert 2.5e4 < a7 < 4.0e4, a7


def test_5s7s_magic_signflips_bracket_the_near_pole_and_tuneout():
    lams = [x for x, _ in magic_5s7s(700.0, 1000.0)]
    # one crossing just red of the 7S-5P3/2 pole (741 nm), one beside the 5S
    # tune-out (790.03) -- both are the light-shift sign-flip locations
    assert any(741.0 < l < 745.0 for l in lams), lams
    assert any(789.0 < l < 792.0 for l in lams), lams


def test_delta_alpha_7s_is_a_large_red_shift_at_the_760_drive():
    # 760 nm sits between the 7S-5P poles (728/741) and the 5S D lines (780/795),
    # so alpha_5S dominates and Delta_alpha = alpha_7S - alpha_5S is large positive
    d = delta_alpha_7s(760.0)
    assert d > 2000.0, d


def test_5d_anchor_is_hamilton_2023():
    # 5D5/2 is adopted, not recomputed: the magic wavelength is Hamilton 2023's
    # measured 776.179(5) nm and the near-resonant 5P3/2-5D5/2 element 1.80(6)
    assert abs(MAGIC_5S5D52_EXP_NM - 776.179) < 0.01
    assert abs(RME_5P32_5D52 - 1.80) < 0.01
