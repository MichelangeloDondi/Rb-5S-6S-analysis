"""
Closure tests for the M3 lineshape kernels (rb5s6s/lineshape.py).

These pin the PHYSICS of the model before any data is fit: every kernel is
area-normalized, has the FWHM it claims, and the composite convolution obeys
the analytic limits (pure Lorentzian, Lorentzian(X)Gaussian = Voigt, added
Lorentzian widths). Kernel math is axis-calibration-independent, so these
run without any real data.
"""

from __future__ import annotations

import numpy as np

from rb5s6s._compat import trapezoid
from rb5s6s.lineshape import (lorentzian, gaussian, two_sided_exponential,
                              stark_ramp, model_profile, voigt_fwhm)
from rb5s6s.constants import GAMMA_NAT_HZ

GNAT = GAMMA_NAT_HZ / 1e6


def _fwhm(nu, y):
    ypk = y.max()
    above = np.where(y >= 0.5 * ypk)[0]
    # linear-interpolate the two half-max crossings for sub-grid accuracy
    lo, hi = above[0], above[-1]
    return nu[hi] - nu[lo]


def _area(nu, y):
    return trapezoid(y, nu)


def test_kernels_area_normalized():
    # Gaussian and two-sided-exponential have thin tails: area 1 on a modest
    # grid. The Lorentzian's arctan tails need a much wider grid (on +-200 it
    # captures only ~99.2%) — that is real physics, and model_profile
    # renormalizes on its own grid regardless.
    nu = np.arange(-300, 300, 0.01)
    assert abs(_area(nu, gaussian(nu, 5.0)) - 1.0) < 1e-6
    assert abs(_area(nu, two_sided_exponential(nu, 5.0)) - 1.0) < 1e-3
    nu_wide = np.arange(-20000, 20000, 0.02)
    assert abs(_area(nu_wide, lorentzian(nu_wide, 5.0)) - 1.0) < 1e-3


def test_kernels_have_claimed_fwhm():
    nu = np.arange(-200, 200, 0.005)
    for k in (lorentzian, gaussian, two_sided_exponential):
        assert abs(_fwhm(nu, k(nu, 6.0)) - 6.0) < 0.05, k.__name__


def test_stark_ramp_shape_and_mean():
    # density ∝ |s| on [-s0,0] => mean shift = -2/3 s0 (the "2/3 of on-axis").
    nu = np.arange(-40, 40, 0.005)
    s0 = 6.0
    r = stark_ramp(nu, s0)
    assert abs(_area(nu, r) - 1.0) < 1e-3
    mean = trapezoid(nu * r, nu)
    assert abs(mean - (-2.0 / 3.0 * s0)) < 0.05
    # strictly red: no weight at nu > half a grid cell
    dnu = nu[1] - nu[0]
    assert np.all(r[nu > dnu] == 0.0)


def test_stark_ramp_small_s0_continuous_and_mean_exact():
    # Review fix regression lock: the old implementation switched
    # DISCONTINUOUSLY from ramp to grid spike at s0 <= dnu (a false-minimum
    # trap for October fits that float s0). The cell-integral + moment-
    # corrected version must (a) keep exact unit mass, (b) keep the exact
    # -2/3 s0 mean even for s0 far below the grid step, and (c) evolve
    # continuously as s0 sweeps through the grid scale.
    nu = np.arange(-30.0, 30.0, 0.05)
    dnu = 0.05
    prev = None
    for s0 in np.arange(0.2 * dnu, 6.0 * dnu, 0.1 * dnu):
        r = stark_ramp(nu, float(s0))
        assert abs(np.sum(r) * dnu - 1.0) < 1e-9
        mean = float(np.sum(nu * r) * dnu)
        assert abs(mean - (-(2.0 / 3.0) * s0)) < 1e-6, (s0, mean)
        if prev is not None:
            gap = float(np.sum(np.abs(r - prev)) * dnu)  # L1 distance
            assert gap < 0.35, (s0, gap)  # old code jumped by O(2) here
        prev = r


def test_stark_ramp_small_s0_continuous_and_mean_exact():
    # Review fix: the old grid-spike fallback switched the shape
    # DISCONTINUOUSLY at s0 ~ dnu (false-minimum trap for October fits that
    # float s0). Now: exact area at every s0, exact mean -2/3 s0 even far
    # below the grid step, and no large L1 jumps along a fine s0 sweep.
    nu = np.arange(-30.0, 30.0, 0.05)
    dnu = 0.05
    prev = None
    for s0 in np.arange(0.2 * dnu, 6.0 * dnu, 0.1 * dnu):
        r = stark_ramp(nu, float(s0))
        assert abs(np.sum(r) * dnu - 1.0) < 1e-9          # exact area
        mean = float(np.sum(nu * r) * dnu)
        assert abs(mean - (-(2.0 / 3.0) * s0)) < 1e-6      # exact mean
        if prev is not None:                                # continuity
            assert np.sum(np.abs(r - prev)) * dnu < 0.35, s0
        prev = r


def test_composite_reduces_to_lorentzian():
    # kill every extra mechanism => pure natural Lorentzian.
    nu = np.arange(-60, 60, 0.02)
    y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=1e-3,
                      transit_fwhm=1e-3, s0=0.0)
    assert abs(_fwhm(nu, y) - GNAT) < 0.08


def test_collisional_adds_to_lorentzian_width():
    # natural + collisional are both Lorentzian => widths add.
    nu = np.arange(-80, 80, 0.02)
    y = model_profile(nu, gamma_coll=4.0, sigma_laser_fwhm=1e-3,
                      transit_fwhm=1e-3, s0=0.0)
    assert abs(_fwhm(nu, y) - (GNAT + 4.0)) < 0.12


def test_lorentzian_gaussian_is_voigt():
    # Lorentzian(X)Gaussian FWHM must match the Olivero-Longbothum value.
    nu = np.arange(-100, 100, 0.01)
    y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=5.0,
                      transit_fwhm=1e-3, s0=0.0, laser_kind="gaussian")
    expected = voigt_fwhm(5.0, GNAT)
    assert abs(_fwhm(nu, y) - expected) < 0.1


def test_stark_ramp_pulls_peak_red():
    # with a Stark ramp the peak of the composite line moves to NEGATIVE nu.
    nu = np.arange(-40, 40, 0.01)
    y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=1.0,
                      transit_fwhm=1.0, s0=6.0)
    assert nu[np.argmax(y)] < -0.1


def test_composite_area_normalized():
    nu = np.arange(-120, 120, 0.02)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=1.5,
                      transit_fwhm=1.0, s0=3.0)
    assert abs(_area(nu, y) - 1.0) < 5e-3


def test_axial_ramp_recovers_triangle_at_zero_window():
    # z_ratio -> 0: pure transverse triangle. mean = -2/3 s0,
    # var/mean^2 = 1/8, standardized skew = 18^1.5/135.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(3.0, 1e-4)
    assert abs(m["mean"] / 3.0 + 2.0 / 3.0) < 1e-3
    assert abs(m["var"] / m["mean"] ** 2 - 0.125) < 1e-3
    assert abs(m["skew_standardized"] - 18.0 ** 1.5 / 135.0) < 1e-3


def test_axial_ramp_one_photon_has_zero_skew():
    # n=1 (one-photon weighting) at zero window is the UNIFORM ramp:
    # mean -s0/2 and exactly zero skew -- the skew observable exists only
    # because the two-photon signal goes as I^2.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(3.0, 1e-4, n_photon=1)
    assert abs(m["mean"] / 3.0 + 0.5) < 1e-3
    assert abs(m["skew_standardized"]) < 1e-3


def test_axial_ramp_dilutes_mean_pull_monotonically():
    # a longer collection window mixes in weaker-shift regions: |mean|
    # must decrease monotonically with z_ratio.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    pulls = [abs(stark_ramp_axial_moments(3.0, zr)["mean"])
             for zr in (0.01, 0.3, 1.0, 3.0)]
    assert all(a > b for a, b in zip(pulls, pulls[1:]))


def test_axial_ramp_grid_density_matches_moments():
    # the on-grid density (fit kernel) must reproduce the quadrature
    # moments and stay area-normalized with support in [-s0, 0].
    import numpy as np
    from rb5s6s.lineshape import stark_ramp_axial, stark_ramp_axial_moments
    nu = np.arange(-6.0, 6.0 + 1e-9, 0.01)
    s0, zr = 3.0, 2.0
    f = stark_ramp_axial(nu, s0, zr)
    dnu = nu[1] - nu[0]
    assert abs(f.sum() * dnu - 1.0) < 1e-9
    assert f[nu > 1e-9].max() == 0.0 and f[nu < -s0 - dnu].max() == 0.0
    m = stark_ramp_axial_moments(s0, zr)
    assert abs((f * nu).sum() * dnu - m["mean"]) < 5e-3


def test_stark_S0_convention_and_scaling():
    # Pinned standard convention (constants.DELTA_ALPHA_AU): S0 at the archival
    # reference is 1.43 MHz transition (0.72 laser). Locks the factor-of-2.
    from rb5s6s.lineshape import stark_shift_S0_mhz
    s0 = stark_shift_S0_mhz(0.225, 32e-6, rho=1.0)
    assert abs(s0 - 1.43) < 0.02, s0
    # scaling: linear in P, 1/w0^2, and (1+rho)
    assert abs(stark_shift_S0_mhz(0.450, 32e-6, 1.0) / s0 - 2.0) < 1e-9
    assert abs(stark_shift_S0_mhz(0.225, 16e-6, 1.0) / s0 - 4.0) < 1e-9
    assert abs(stark_shift_S0_mhz(0.225, 32e-6, 0.0) / s0 - 0.5) < 1e-9


def test_stark_S0_reproduces_orson2021():
    # LITERATURE ANCHOR (the Stark analogue of the Lehmann transit test): Orson
    # et al. 2021 (J. Phys. B 54, 175001), prior art on THIS 5S-6S line, compute
    # the differential polarizability alpha_56 = alpha(5S)-alpha(6S) = -1093 a.u.
    # (our DELTA_ALPHA_AU = +1093, opposite sign by definition) and predict an
    # AC-Stark shift |Df| = 0.66 MHz at their conditions -- 0.8 W into a 63 um
    # waist radius, single beam (rho=0, their I = 2P/pi r^2). Reproducing it locks
    # DELTA_ALPHA_AU + the light-shift convention to a published external number.
    from rb5s6s.lineshape import stark_shift_S0_mhz
    assert abs(stark_shift_S0_mhz(0.8, 63e-6, rho=0.0) - 0.66) < 0.03


def test_ramp_moment_contributions_forward_model():
    # The three moment-functionals of one S0 (pure-triangle limit): the
    # forward model the October joint fit checks the data against.
    from rb5s6s.lineshape import ramp_moment_contributions
    S0 = 3.0
    m = ramp_moment_contributions(S0, z_ratio=0.0)
    assert abs(m["pull"] - (-2.0 / 3.0 * S0)) < 2e-3
    assert abs(m["excess_var"] - S0 ** 2 / 18.0) < 2e-3
    assert abs(m["kappa3"] - S0 ** 3 / 135.0) < 2e-3
    # all three scale with the ONE parameter S0 (pull ~S0, var ~S0^2, k3 ~S0^3)
    m2 = ramp_moment_contributions(2 * S0, z_ratio=0.0)
    assert abs(m2["pull"] / m["pull"] - 2) < 1e-2
    assert abs(m2["excess_var"] / m["excess_var"] - 4) < 1e-2
    assert abs(m2["kappa3"] / m["kappa3"] - 8) < 1e-2


def test_composite_transit_kind_voigt_vs_lehmann():
    # The transit_kind knob (the model-form systematic for beta): the exp
    # (Lehmann) transit has FATTER WINGS than the gaussian (Voigt) of the same
    # FWHM, so it WIDENS the composite more (broader, lower core). The two
    # profiles genuinely differ, which is what shifts beta between model forms.
    from rb5s6s.lineshape import composite_profile
    g_e, p_e = composite_profile(0.1, 2.0, 1.0, transit_kind="exp")
    g_v, p_v = composite_profile(0.1, 2.0, 1.0, transit_kind="gaussian")
    assert g_e.shape == g_v.shape           # same self-sized grid

    def fwhm(g, p):
        a = np.where(p >= 0.5 * p.max())[0]
        return g[a[-1]] - g[a[0]]

    assert fwhm(g_e, p_e) > fwhm(g_v, p_v)   # exp fat wings -> broader composite
    assert float(np.max(np.abs(p_e - p_v))) > 1e-3   # genuinely different form
