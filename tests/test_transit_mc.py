"""
Closure tests for the transit-broadening Monte-Carlo (rb5s6s/transit_mc.py).

The MC has no free parameters beyond geometry + temperature. Once the crossing-
FLUX weight is included (the 2026-07-12 fix), the transit kernel is a FINITE
two-sided exponential (Biraben-Cagnac cusp), so its bare FWHM is well-defined and
n_atoms-independent -- and equals the closed form constants.transit_fwhm_from_w0,
itself validated against Lehmann 2021's NNO worked example (41.2 kHz). We test
BOTH: the bare FWHM against that analytic/literature anchor, and the convolved
added-FWHM metric (what actually enters the line budget) for its w0, sqrt(T) and
collection-range scalings. (Before the fix the ensemble was weighted ~1/v, giving
a spurious log-divergent, n_atoms-dependent cusp that ran ~2x too narrow.)
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s._compat import trapezoid  # np.trapezoid is numpy 2.0+; shim for 1.24
from rb5s6s.constants import transit_fwhm_from_w0
from rb5s6s.transit_mc import transit_added_fwhm_mc, transit_lineshape_mc

THIN = dict(z_half_range_m=0.3e-3, n_atoms=200_000)  # << Rayleigh range -> one w0
_U_KG = 1.660_539_066_60e-27


def _bare_fwhm(*, n_atoms=200_000, seed=0, **kw) -> float:
    """Bare transit-kernel FWHM (MHz) in the thin-column limit (w ~ w0)."""
    nu = np.arange(-8.0, 8.0, 0.005)
    y = transit_lineshape_mc(nu, z_half_range_m=1e-5, n_atoms=n_atoms, seed=seed, **kw)
    y = y / y.max()
    above = nu[y >= 0.5]
    return float(above[-1] - above[0])


def test_reproduces_lehmann_nno():
    # LITERATURE ANCHOR. Lehmann 2021 works a transit example (NNO, m = 44 u,
    # w0 = 0.90 mm, 300 K = 26.85 C) with transit HWHM 41.2 kHz. The flux-fixed
    # MC must reproduce it; the old ~1/v-weighted cusp could not. (A wide band
    # still cleanly separates the fixed value from the buggy near-divergence.)
    hwhm_khz = _bare_fwhm(w0_m=0.9e-3, T_C=26.85, mass_kg=44 * _U_KG,
                          n_atoms=300_000) / 2 * 1e3
    assert 33.0 < hwhm_khz < 50.0, hwhm_khz


def test_bare_fwhm_finite_and_matches_analytic():
    # The bare kernel FWHM is now FINITE and equals the closed form
    # transit_fwhm_from_w0 (~1.87 MHz at 32 um, 110 C) within MC + grid tolerance.
    ana = transit_fwhm_from_w0(32e-6, 110.0)      # ~1.867 MHz
    mc = _bare_fwhm(w0_m=32e-6, T_C=110, n_atoms=300_000)
    assert abs(mc - ana) / ana < 0.12, (mc, ana)


@pytest.mark.slow
def test_bare_fwhm_converges_in_n_atoms():
    # THE bug-fix evidence: a finite peak converges in n_atoms. The old
    # log-divergent cusp shrank without bound as n_atoms grew.
    a = _bare_fwhm(w0_m=32e-6, T_C=110, n_atoms=80_000, seed=1)
    b = _bare_fwhm(w0_m=32e-6, T_C=110, n_atoms=320_000, seed=1)
    assert abs(a - b) / b < 0.08, (a, b)


@pytest.mark.slow
def test_inverse_w0_scaling():
    # thin slice: the added FWHM ~ 1/w0. Halving w0 ~doubles it.
    f_narrow = transit_added_fwhm_mc(w0_m=16e-6, T_C=110, **THIN)
    f_wide = transit_added_fwhm_mc(w0_m=32e-6, T_C=110, **THIN)
    assert 1.7 < f_narrow / f_wide < 2.4, (f_narrow, f_wide)


@pytest.mark.slow
def test_sqrtT_scaling():
    fa = transit_added_fwhm_mc(w0_m=32e-6, T_C=70, **THIN)
    fb = transit_added_fwhm_mc(w0_m=32e-6, T_C=130, **THIN)
    assert abs(fb / fa - np.sqrt((130 + 273.15) / (70 + 273.15))) < 0.15, (fa, fb)


def test_magnitude_order_mhz():
    # At the (now-excluded) 32 um nominal the transit ADDS ~2 MHz to the
    # observable line -- so large that natural(3.49) (X) transit already exceeds
    # the observed ~5.25 MHz line, which is exactly why w0 must be larger (~50 um).
    assert 1.7 < transit_added_fwhm_mc(w0_m=32e-6, T_C=110, **THIN) < 2.6


@pytest.mark.slow
def test_convolved_metric_converges_in_n_atoms():
    # The convolved added metric converges (as does the bare FWHM, post-fix).
    a = transit_added_fwhm_mc(w0_m=32e-6, T_C=110, z_half_range_m=0.3e-3, n_atoms=100_000)
    b = transit_added_fwhm_mc(w0_m=32e-6, T_C=110, z_half_range_m=0.3e-3, n_atoms=300_000)
    assert abs(a - b) < 0.1, (a, b)


def test_lineshape_is_cusped():
    # The transit kernel is a two-sided exponential -- more peaked than a
    # Gaussian (strongly positive excess kurtosis), finite peak (not divergent).
    nu = np.arange(-12, 12, 0.01)
    L = transit_lineshape_mc(nu, w0_m=32e-6, T_C=110, **THIN)
    Ln = L / trapezoid(L, nu)
    m2 = trapezoid(nu ** 2 * Ln, nu)
    m4 = trapezoid(nu ** 4 * Ln, nu)
    assert m4 / m2 ** 2 - 3.0 > 1.0, m4 / m2 ** 2 - 3.0  # Gaussian = 0


@pytest.mark.slow
def test_collection_range_matters():
    # Objection #1: collecting the diverging far-field changes the transit at
    # the tens-of-% level (real, not dominant).
    tight = transit_added_fwhm_mc(w0_m=32e-6, T_C=110, z_half_range_m=0.3e-3, n_atoms=200_000)
    longcol = transit_added_fwhm_mc(w0_m=32e-6, T_C=110, z_half_range_m=6e-3, n_atoms=200_000)
    assert abs(longcol - tight) > 0.05 and longcol != tight
