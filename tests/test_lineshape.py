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
import pytest

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
    # density ∝ s on [0,s0] => mean shift = +2/3 s0 (the "2/3 of on-axis").
    # BLUE since the adopted Delta alpha is negative (O27, the owner's SSOT ruling).
    nu = np.arange(-40, 40, 0.005)
    s0 = 6.0
    r = stark_ramp(nu, s0)
    assert abs(_area(nu, r) - 1.0) < 1e-3
    mean = trapezoid(nu * r, nu)
    assert abs(mean - (+2.0 / 3.0 * s0)) < 0.05
    # strictly blue: no weight at nu < minus half a grid cell
    dnu = nu[1] - nu[0]
    assert np.all(r[nu < -dnu] == 0.0)


def test_stark_ramp_small_s0_continuous_and_mean_exact():
    # Fix regression lock: the old implementation switched
    # DISCONTINUOUSLY from ramp to grid spike at s0 <= dnu (a false-minimum
    # trap for fixed-lock fits that float s0). The cell-integral + moment-
    # corrected version must (a) keep exact unit mass, (b) keep the exact
    # +2/3 s0 mean even for s0 far below the grid step, and (c) evolve
    # continuously as s0 sweeps through the grid scale.
    nu = np.arange(-30.0, 30.0, 0.05)
    dnu = 0.05
    prev = None
    for s0 in np.arange(0.2 * dnu, 6.0 * dnu, 0.1 * dnu):
        r = stark_ramp(nu, float(s0))
        assert abs(np.sum(r) * dnu - 1.0) < 1e-9
        mean = float(np.sum(nu * r) * dnu)
        assert abs(mean - (+(2.0 / 3.0) * s0)) < 1e-6, (s0, mean)
        if prev is not None:
            gap = float(np.sum(np.abs(r - prev)) * dnu)  # L1 distance
            assert gap < 0.35, (s0, gap)  # old code jumped by O(2) here
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


def test_stark_ramp_pulls_peak_blue():
    # with a Stark ramp the peak of the composite line moves to POSITIVE nu,
    # the adopted Delta alpha being negative (O27).
    nu = np.arange(-40, 40, 0.01)
    y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=1.0,
                      transit_fwhm=1.0, s0=6.0)
    assert nu[np.argmax(y)] > 0.1


def test_composite_area_normalized():
    nu = np.arange(-120, 120, 0.02)
    y = model_profile(nu, gamma_coll=2.0, sigma_laser_fwhm=1.5,
                      transit_fwhm=1.0, s0=3.0)
    assert abs(_area(nu, y) - 1.0) < 5e-3


def test_axial_ramp_recovers_triangle_at_zero_window():
    # z_ratio -> 0: pure transverse triangle. mean = +2/3 s0,
    # var/mean^2 = 1/8, standardized skew = -18^1.5/135.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(3.0, 1e-4)
    assert abs(m["mean"] / 3.0 - 2.0 / 3.0) < 1e-3
    assert abs(m["var"] / m["mean"] ** 2 - 0.125) < 1e-3
    assert abs(m["skew_standardized"] + 18.0 ** 1.5 / 135.0) < 1e-3   # mirrored with the support


def test_axial_ramp_one_photon_has_zero_skew():
    # n=1 (one-photon weighting) at zero window is the UNIFORM ramp:
    # mean +s0/2 and exactly zero skew -- the skew observable exists only
    # because the two-photon signal goes as I^2.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(3.0, 1e-4, n_photon=1)
    assert abs(m["mean"] / 3.0 - 0.5) < 1e-3
    assert abs(m["skew_standardized"]) < 1e-3


def test_axial_ramp_three_photon_is_the_parabola():
    """n=3 at zero window is the PARABOLIC ramp f(s) = 3 s^2 / s0^3.

    Exact cumulants by direct integration: mean +3/4 s0, variance 3/80 s0^2,
    third central moment - s0^3/160, standardised skew -2 sqrt(15)/9 = -0.8607.
    Added 2026-08-09 when a one-colour three-photon rung entered the future
    programme: a three-photon rate goes as intensity cubed, so the same
    machinery that gives the two-photon triangle gives this parabola with
    n_photon=3, and its intrinsic skew is 1.52 times the triangle's 0.566,
    which is what makes the rung interesting for the shape method.
    """
    from math import sqrt
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(3.0, 1e-4, n_photon=3)
    assert abs(m["mean"] / 3.0 - 0.75) < 1e-3
    assert abs(m["var"] / 9.0 - 3.0 / 80.0) < 1e-3
    assert abs(m["skew_standardized"] + 2.0 * sqrt(15.0) / 9.0) < 1e-3   # mirrored (O27)


def test_the_ramp_cumulants_follow_the_general_n_law():
    """The closed forms in THEORY_NOTE section 2, checked at n = 1, 2, 3.

        mean = -n/(n+1) S0,  Var = n/((n+1)^2 (n+2)) S0^2,
        g1   = +2(n-1)/(n+3) sqrt((n+2)/n)

    The sign of g1 is the part worth pinning: substituting u = -s/S0 gives a
    Beta(n,1) law whose own skew is NEGATIVE, and the reflection flips it, so
    the ramp's standardised skew is negative. A first write-up of the general
    law on 2026-08-09 had it negative, and this test is what would have caught
    that.
    """
    from math import sqrt
    from rb5s6s.lineshape import stark_ramp_axial_moments
    s0 = 2.0
    for n in (1, 2, 3):
        m = stark_ramp_axial_moments(s0, 1e-4, n_photon=n)
        assert abs(m["mean"] / s0 - n / (n + 1)) < 1e-3
        assert abs(m["var"] / s0**2 - n / ((n + 1) ** 2 * (n + 2))) < 1e-3
        g1 = 2.0 * (n - 1) / (n + 3) * sqrt((n + 2) / n)
        assert abs(m["skew_standardized"] + g1) < 1e-3   # mirrored with the support (O27)


def test_axial_ramp_dilutes_mean_pull_monotonically():
    # a longer collection window mixes in weaker-shift regions: |mean|
    # must decrease monotonically with z_ratio.
    from rb5s6s.lineshape import stark_ramp_axial_moments
    pulls = [abs(stark_ramp_axial_moments(3.0, zr)["mean"])
             for zr in (0.01, 0.3, 1.0, 3.0)]
    assert all(a > b for a, b in zip(pulls, pulls[1:]))


def test_axial_ramp_grid_density_matches_moments():
    # the on-grid density (fit kernel) must reproduce the quadrature
    # moments and stay area-normalized with support in [0, s0], the blue side.
    import numpy as np
    from rb5s6s.lineshape import stark_ramp_axial, stark_ramp_axial_moments
    nu = np.arange(-6.0, 6.0 + 1e-9, 0.01)
    s0, zr = 3.0, 2.0
    f = stark_ramp_axial(nu, s0, zr)
    dnu = nu[1] - nu[0]
    assert abs(f.sum() * dnu - 1.0) < 1e-9
    assert f[nu < -1e-9].max() == 0.0 and f[nu > s0 + dnu].max() == 0.0
    m = stark_ramp_axial_moments(s0, zr)
    assert abs((f * nu).sum() * dnu - m["mean"]) < 5e-3


def test_stark_S0_convention_and_scaling():
    # Pinned standard convention. The 1.43 MHz checkpoint (225 mW, the old
    # 32 um nominal, rho=1) was computed under the cited 1093, so the
    # convention lock keeps using that constant EXPLICITLY: since the
    # 2026-08-24 adjudication the package default is this record's own value,
    # under which the same point is 1.48. The factor-of-2 is what this
    # pins, and it is Delta_alpha-independent.
    from rb5s6s.constants import DELTA_ALPHA_AU_ORSON2021
    from rb5s6s.lineshape import stark_shift_S0_mhz
    s0 = stark_shift_S0_mhz(0.225, 32e-6, rho=1.0,
                            delta_alpha_au=DELTA_ALPHA_AU_ORSON2021)
    assert abs(s0 - 1.43) < 0.02, s0
    # scaling: linear in P, 1/w0^2, and (1+rho), checked at ONE constant
    kw = dict(delta_alpha_au=DELTA_ALPHA_AU_ORSON2021)
    assert abs(stark_shift_S0_mhz(0.450, 32e-6, 1.0, **kw) / s0 - 2.0) < 1e-9
    assert abs(stark_shift_S0_mhz(0.225, 16e-6, 1.0, **kw) / s0 - 4.0) < 1e-9
    assert abs(stark_shift_S0_mhz(0.225, 32e-6, 0.0, **kw) / s0 - 0.5) < 1e-9


def test_stark_S0_reproduces_orson2021():
    # LITERATURE ANCHOR (the Stark analogue of the Lehmann transit test): Orson
    # et al. 2021 (J. Phys. B 54, 175001), prior art on THIS 5S-6S line, compute
    # the differential polarizability alpha_56 = alpha(5S)-alpha(6S) = -1093 a.u.
    # and predict an AC-Stark shift |Df| = 0.66 MHz at their conditions -- 0.8 W
    # into a 63 um waist radius, single beam (rho=0, their I = 2P/pi r^2).
    # Reproducing it locks the light-shift CONVENTION to a published external
    # number. Since 2026-08-24 this passes THEIR constant explicitly: the
    # package default is now this record's own -1131.8, the dynamic sum (this record's
    # adjudication of the sign dispute), so reproducing Orson's arithmetic
    # needs Orson's input, and using the default here would silently test the
    # convention against a different number than the one it was pinned to.
    from rb5s6s.constants import DELTA_ALPHA_AU_ORSON2021
    from rb5s6s.lineshape import stark_shift_S0_mhz
    got = stark_shift_S0_mhz(0.8, 63e-6, rho=0.0,
                             delta_alpha_au=DELTA_ALPHA_AU_ORSON2021)
    assert abs(got - 0.66) < 0.03


def test_ramp_moment_contributions_forward_model():
    # The three moment-functionals of one S0 (pure-triangle limit): the
    # forward model the fixed-lock joint fit checks the data against.
    from rb5s6s.lineshape import ramp_moment_contributions
    S0 = 3.0
    m = ramp_moment_contributions(S0, z_ratio=0.0)
    assert abs(m["pull"] - (+2.0 / 3.0 * S0)) < 2e-3
    assert abs(m["excess_var"] - S0 ** 2 / 18.0) < 2e-3
    assert abs(m["mu3"] + S0 ** 3 / 135.0) < 2e-3   # the odd moment mirrors (O27)
    # all three scale with the ONE parameter S0 (pull ~S0, var ~S0^2, mu3 ~S0^3)
    m2 = ramp_moment_contributions(2 * S0, z_ratio=0.0)
    assert abs(m2["pull"] / m["pull"] - 2) < 1e-2
    assert abs(m2["excess_var"] / m["excess_var"] - 4) < 1e-2
    assert abs(m2["mu3"] / m["mu3"] - 8) < 1e-2


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


def test_axial_ramp_matches_the_independent_closed_form():
    """The z-integrated ramp weight also has a closed form, derived by hand
    and integrated with its own quadrature, so it holds this module against a
    different parametrisation and a different implementation. In the long-cell
    limit it gives

        w(u) propto sqrt((1-u)/u) (1+2u),
        mean S0/3,  variance 11 S0^2/144,  |skew| (5/432)/(11/144)^1.5 = 0.5482

    and a skew zero crossing at z_ratio = 1.1172, where this repo had quoted
    ~1.12 from its own numerics. Hold the two implementations together: the
    module must reproduce the closed-form limits and the crossover."""
    from rb5s6s.lineshape import stark_ramp_axial_moments
    m = stark_ramp_axial_moments(1.0, 200.0)
    assert abs(m["mean"]) == pytest.approx(1.0 / 3.0, rel=5e-3)
    assert m["var"] == pytest.approx(11.0 / 144.0, rel=5e-3)
    assert abs(m["skew_standardized"]) == pytest.approx(0.5482, rel=2e-2)

    # the crossover, previously "~1.12": bracket it tightly
    lo = stark_ramp_axial_moments(1.0, 1.10)["skew_standardized"]
    hi = stark_ramp_axial_moments(1.0, 1.13)["skew_standardized"]
    assert lo * hi < 0, f"skew does not change sign in [1.10, 1.13]: {lo}, {hi}"

    # spot-check the interpolation against the closed form's own table
    # the skews MIRROR with the support (O27); the |mean| notes are unchanged
    for z, mean_note, skew_note in ((0.5, 0.6209, -0.4793), (2.0, 0.4538, +0.3016),
                                    (5.0, 0.3800, +0.4460)):
        mm = stark_ramp_axial_moments(1.0, z)
        assert abs(mm["mean"]) == pytest.approx(mean_note, rel=2e-3)
        assert mm["skew_standardized"] == pytest.approx(skew_note, rel=2e-2)


def test_model_profile_is_converged_in_its_internal_grid(monkeypatch):
    """model_profile convolves on an internal grid of min(width)/12. Nothing
    checked that 12 is enough, and the composite FWHM is exactly what the
    beta_self and kappa regressions fit, so a grid bias goes straight into
    those slopes. It cannot be caught downstream: the synthetic closure tests
    build their data with this same routine, so the bias cancels identically
    (mutation test, 2026-07-29 -- coarsening to /4 moved the FWHM ~0.1% with
    the suite green).

    Varies the divisor directly. An earlier attempt compared the shipped
    profile against one built from 4x-smaller physical widths, which is
    vacuous: shrinking every width shrinks the step in proportion, so the
    step-to-width ratio -- the only thing convergence depends on -- never
    moved, and the test passed at /4 too. The widths below also keep the
    profile clear of GRID_STEP_FLOOR_MHZ, where the floor binds and the
    divisor stops mattering at all."""
    import rb5s6s.lineshape as LS

    nu = np.linspace(-40.0, 40.0, 400_001)
    for kw in (dict(gamma_coll=0.5, sigma_laser_fwhm=1.0, transit_fwhm=1.5),
               dict(gamma_coll=0.5, sigma_laser_fwhm=1.0, transit_fwhm=1.5,
                    s0=2.0)):
        shipped = _fwhm(nu, model_profile(nu, **kw))
        monkeypatch.setattr(LS, "GRID_STEPS_PER_KERNEL", 4.0 * LS.GRID_STEPS_PER_KERNEL)
        finer = _fwhm(nu, model_profile(nu, **kw))
        monkeypatch.undo()
        rel = abs(shipped - finer) / finer
        assert rel < 5e-4, (
            f"model_profile is not grid-converged for {kw}: the shipped "
            f"divisor gives {shipped:.6f} MHz, 4x finer {finer:.6f} "
            f"({rel:.2%}) -- raise GRID_STEPS_PER_KERNEL in lineshape.py")


# ---------------------------------------------------------------------------
# the general intensity-profile seam (stark_from_intensity_profile)
# ---------------------------------------------------------------------------

def test_general_profile_reproduces_focused_beam_triangle():
    """The transverse-Gaussian case through the general machinery must
    reproduce stark_ramp: I = exp(-2r^2/w^2) with measure r dr is the
    geometry whose signal-weighted shift density is the triangle (the
    docstring's du/u derivation). The axial Lorentzian is a DIFFERENT
    geometry (mean -3/4 s0, checked below) -- an early version of this
    test conflated them."""
    from rb5s6s.lineshape import stark_from_intensity_profile, stark_ramp
    s0 = 2.0
    nu = np.arange(-1.0, 4.0, 0.002)          # the window follows the blue support (O27)
    r = np.linspace(0.0, 5.0, 400001)
    intensity = np.exp(-2.0 * r ** 2)
    general = stark_from_intensity_profile(nu, s0, intensity, r, n_photon=2)
    triangle = stark_ramp(nu, s0)
    # compare the three lowest moments, the physics the fits consume
    for pw, tol in ((1, 5e-3), (2, 2e-2)):
        mg = float(np.sum(nu ** pw * general) * (nu[1] - nu[0]))
        mt = float(np.sum(nu ** pw * triangle) * (nu[1] - nu[0]))
        assert abs(mg - mt) < tol * max(abs(mt), 1.0), (pw, mg, mt)


def test_general_profile_n1_uniform_mean():
    """n_photon=1 on the same geometry: mean pull +s0/2 (the flat case)."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 1.5
    nu = np.arange(-1.0, 3.0, 0.002)          # blue window (O27)
    r = np.linspace(0.0, 5.0, 400001)
    f = stark_from_intensity_profile(nu, s0, np.exp(-2.0 * r ** 2), r,
                                     n_photon=1)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert abs(mean - (+s0 / 2.0)) < 5e-3


def test_general_profile_evanescent_is_not_a_triangle():
    """A nanofibre-like evanescent field (I ~ e^{-2r/L}, measure r dr)
    must give a different distribution: the measure grows outward while the
    intensity dies, boosting the small-shift tail, so the mean pull is
    SHALLOWER than the focused beam's +2/3 s0 (an early version of this
    test asserted the opposite; the machinery corrected the intuition)."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 2.0
    nu = np.arange(-1.0, 4.0, 0.002)          # blue window (O27)
    r = np.linspace(120.0, 800.0, 200001)      # nm, from the fibre surface
    L = 100.0
    inten = np.exp(-2.0 * (r - r[0]) / L)
    f = stark_from_intensity_profile(nu, s0, inten, r, n_photon=2)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert +0.2 * s0 < mean < (2.0 / 3.0) * s0 - 0.02, mean       # mirrored (O27)
    assert abs(float(np.sum(f) * (nu[1] - nu[0])) - 1.0) < 1e-9


def test_general_profile_axial_lorentzian_mean():
    """The axial line I(z) = 1/(1+z^2) with uniform measure: weight u^2 dz
    with dz ~ du/(u^1.5 sqrt(1-u)) gives mean +3/4 s0 for n=2 -- a genuinely
    different geometry from the transverse triangle, kept as the example
    that the seam distinguishes geometries the summary widths cannot."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 2.0
    nu = np.arange(-1.0, 4.0, 0.002)          # blue window (O27)
    z = np.linspace(-200.0, 200.0, 400001)
    f = stark_from_intensity_profile(nu, s0, 1.0 / (1.0 + z ** 2),
                                     np.ones_like(z), n_photon=2)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert abs(mean - (+0.75 * s0)) < 5e-3, mean


def test_model_profile_default_profile_is_stark_ramp_bitwise():
    """The light-geometry seam (`profile`) defaults to stark_ramp, and the
    default must be the IDENTICAL code path, not merely a close one: every
    committed fit ran through the hard-coded ramp, so omitting the argument
    has to reproduce passing it exactly, bit for bit."""
    nu = np.arange(-30.0, 15.0, 0.01)
    kw = dict(gamma_coll=1.5, sigma_laser_fwhm=1.2, transit_fwhm=0.9, s0=2.0)
    assert np.array_equal(model_profile(nu, **kw),
                          model_profile(nu, **kw, profile=stark_ramp))


def test_model_profile_plumbed_general_seam_matches_ramp():
    """The plumbed path end-to-end: a closure over
    stark_from_intensity_profile with the focused-beam geometry, passed
    through model_profile's profile argument, must reproduce the default
    (hard-coded-ramp) line. The density equivalence is tested above on a
    fine grid; here the check is on the model's own internal grid, after
    convolution with the smooth core, which is what a fit consumes."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    r = np.linspace(0.0, 5.0, 200001)
    inten = np.exp(-2.0 * r ** 2)

    def focused(g, s0):
        return stark_from_intensity_profile(g, s0, inten, r, n_photon=2)

    nu = np.arange(-30.0, 15.0, 0.01)
    kw = dict(gamma_coll=1.5, sigma_laser_fwhm=1.2, transit_fwhm=0.9, s0=2.0)
    ref = model_profile(nu, **kw)
    gen = model_profile(nu, **kw, profile=focused)
    assert np.max(np.abs(gen - ref)) < 5e-3 * ref.max(), np.max(np.abs(gen - ref))


def test_model_profile_custom_geometry_changes_line():
    """A different geometry through the same seam must actually reach the
    model: the n=1 flat density pulls the line by +s0/2 against the
    triangle's +2/3 s0 (BLUE since O27), so the two composite lines' means
    must differ by -s0/6. Differencing the two means cancels the shared symmetric core and
    its truncation error."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    r = np.linspace(0.0, 5.0, 200001)
    inten = np.exp(-2.0 * r ** 2)

    def flat(g, s0):
        return stark_from_intensity_profile(g, s0, inten, r, n_photon=1)

    s0 = 3.0
    nu = np.arange(-40.0, 40.0, 0.01)
    kw = dict(gamma_coll=1.5, sigma_laser_fwhm=1.2, transit_fwhm=0.9, s0=s0)
    dnu = nu[1] - nu[0]

    def mean(y):
        return float(np.sum(nu * y) * dnu / (np.sum(y) * dnu))

    dm = mean(model_profile(nu, **kw, profile=flat)) - mean(model_profile(nu, **kw))
    assert abs(dm + s0 / 6.0) < 0.05, dm


def test_the_aperture_on_axis_factor_matches_its_closed_form_table():
    """F39: the modulator's 3 mm bore ahead of the 150 mm lens clips the input Gaussian; the
    on-axis intensity per recorded watt is (1 - e^{-a^2/w^2})^2 / (1 - e^{-2 a^2/w^2}) with
    w = lam f / (pi w0). The thesis session's table, checked both sides: 28.4, 12.4, 5.3 and 0.6
    per cent lost at 42.4, 52.1, 60 and 76 um; the factor tends to one for a wide focus (a
    narrow input beam) and to zero for a tight one."""
    from rb5s6s.lineshape import aperture_onaxis_factor
    for w0_um, loss_pct in ((42.4, 28.4), (52.1, 12.4), (60.0, 5.3), (76.0, 0.6)):
        assert abs(100.0 * (1.0 - aperture_onaxis_factor(w0_um * 1e-6)) - loss_pct) < 0.1, w0_um
    assert aperture_onaxis_factor(300e-6) > 0.9999 and aperture_onaxis_factor(5e-6) < 0.05


def test_the_actual_focus_on_axis_factor_matches_f280_and_the_unclipped_limit():
    """F280 (2026-09-21): the Cell's w0 is the ACTUAL (same-reading) focus, not the free-focus
    convention `aperture_onaxis_factor` takes, and reading it through the wrong function read S0
    about 20 per cent low at the archive's own waist (0.716 against 0.890). This is the carry:
    0.890 at 42.42 um (the finding's own reading, a 2.46 mm input), and -> 1 once the beam is loose
    enough that the bore barely clips it -- checked at the SAME default geometry rather than a
    second bore, whose floor sits far enough from this one that the table's node grid (tuned for
    the default 1.5 mm bore) is not asserted accurate there. Plants both ways: the reading a real
    call must hit, and the floor a call below it must refuse rather than silently extrapolate."""
    from rb5s6s.lineshape import aperture_onaxis_factor_actual
    assert abs(aperture_onaxis_factor_actual(42.42e-6) - 0.890) < 2e-3
    assert aperture_onaxis_factor_actual(300e-6) > 0.999, "a loosely focused beam is barely clipped"
    with pytest.raises(ValueError):
        aperture_onaxis_factor_actual(38e-6)      # F280's floor sits near 41 um for this bore
    # clamp_floor=True (stark.fit_stark_sweep's prediction-band use, W0_BAND_M's own low edge
    # sitting under the floor): no raise, and the clamped value equals the floor's own reading.
    # THE PROBE POINT IS 40.87 UM, NOT 41.0 (C6c): since this function now RETURNS the
    # `beam_field.ClippedBeam` route's value (one implementation per term, closing the 6.877e-5
    # discrepancy `tests/test_volume_world.py` found between the two routes), its floor is
    # `ClippedBeam`'s own (about 40.865 um at this bore, a 30 mm input), a genuine ~27 nm move from
    # the old table's own ~40.892 um floor -- close enough that a probe at 41.0 um sits far enough
    # above EITHER floor for the ratio's steep near-floor slope to clear this assertion's 5e-3 by
    # itself under the old floor and miss it by less than a per cent under the new one.
    clamped = aperture_onaxis_factor_actual(38e-6, clamp_floor=True)
    at_floor = aperture_onaxis_factor_actual(40.87e-6)
    assert abs(clamped - at_floor) < 5e-3, (clamped, at_floor)


def test_the_actual_and_free_focus_conventions_disagree_at_the_same_number():
    """The two are NOT interchangeable (F108): `aperture_onaxis_factor(w)` reads w as an
    unclipped input's own diffraction limit, `aperture_onaxis_factor_actual(w)` reads w as the
    bench-ACTUAL reading, and calling the first on an actual reading is exactly F280's bug -- the
    actual-convention factor is always the larger of the two, because the clipped beam's actual
    focus is always wider than the free-focus number of the same input."""
    from rb5s6s.lineshape import aperture_onaxis_factor, aperture_onaxis_factor_actual
    for w0_um in (42.4, 52.1, 60.0):
        free_convention = aperture_onaxis_factor(w0_um * 1e-6)
        actual_convention = aperture_onaxis_factor_actual(w0_um * 1e-6)
        assert actual_convention > free_convention, (w0_um, free_convention, actual_convention)


def test_the_aperture_spread_factor_reproduces_the_reviewed_column_and_its_unclipped_anchor():
    """F39: the width channel reads the spread of the shift distribution under the rate weighting,
    which the clipped focus moves by a factor F that differs from the on-axis one; the
    column (0.699, 0.860, 0.936, 0.992 at 42.4, 52.1, 60 and 76 um) reproduces here to 0.3 per
    cent, and the unclipped rms over the peak is 1/sqrt(18)."""
    from rb5s6s.lineshape import aperture_spread_factor, aperture_onaxis_factor
    from rb5s6s.constants import W0_CENTRAL_M
    for w0_um, F in ((42.4, 0.699), (52.1, 0.860), (60.0, 0.936), (76.0, 0.992)):
        got = aperture_spread_factor(w0_um * 1e-6)
        assert abs(got - F) < 0.004, (w0_um, got)
        assert got < aperture_onaxis_factor(w0_um * 1e-6), "the spread factor sits below the on-axis one at every waist"
    # n_r RAISED, NOT the change reverted (2026-09-21): C5 normalised the focal-plane power by
    # Parseval and asserted the on-axis peak against its closed form (rb5s6s/lineshape.py's
    # `_spread`), a strictly stronger check than the trapezoid-over-rho it replaced. A 50 mm bore
    # against the central waist's input radius is a span of tens, and the default n_r=1200 resolves
    # the truncated Gaussian too coarsely over it to hold the closed-form check to 1e-3, so the
    # corrected function REFUSES rather than returning a silently wrong ratio (its own message says
    # "raise n_r"). At n_r=20000 the ratio comes back inside this tolerance by orders of magnitude.
    assert abs(aperture_spread_factor(W0_CENTRAL_M, a_m=50e-3, n_r=20000) - 1.0) < 2e-3, (
        "a bore far wider than the beam clips nothing")


def test_the_aperture_spread_factor_actual_carries_the_same_reading_correction():
    """F280's own open item, closed in C6b (A136): the width channel's spread factor gains an
    ACTUAL-convention form, `aperture_spread_factor_actual`, exactly as the on-axis factor already
    has in `aperture_onaxis_factor_actual`. Reproduced here against an independent closed-form
    correction rather than the raw quadrature `aperture_spread_factor` needs: for an unclipped
    Gaussian the spread statistic scales as the peak per watt, 2/(pi w^2), so the same
    (w_act/w_free)^2 reading correction `aperture_onaxis_factor_actual` derives applies to it too."""
    from rb5s6s.lineshape import (aperture_spread_factor, aperture_spread_factor_actual,
                                  aperture_onaxis_factor_actual, _actual_focus_quadrature)
    from rb5s6s.constants import EOM_APERTURE_RADIUS_M, DRIVE_LENS_F_M, LAMBDA_LASER_M, W0_CENTRAL_M
    a, f, lam = EOM_APERTURE_RADIUS_M, DRIVE_LENS_F_M, LAMBDA_LASER_M

    # the closed-form cross-check, independent of the module's own node table: pick an input
    # radius, find its actual focus by the SAME quadrature `aperture_onaxis_factor_actual` uses,
    # and check the module's answer against `aperture_spread_factor(w_free) * (w_act/w_free)^2`
    # computed here by hand.
    for w_in_mm in (1.12, 2.46):
        w_in = w_in_mm * 1e-3
        w_act, _ = _actual_focus_quadrature(w_in, a, f, lam, n_r=500, n_rho=900)
        w_free = lam * f / (np.pi * w_in)
        by_hand = aperture_spread_factor(w_free) * (w_act / w_free) ** 2
        got = aperture_spread_factor_actual(w_act)
        assert abs(got - by_hand) / by_hand < 5e-3, (w_in_mm, got, by_hand)

    # F280's own reading at the archive's central waist: about 0.858, and BELOW the on-axis factor
    # at the same waist (0.890), the same ordering `aperture_spread_factor` already carries in the
    # free-focus convention.
    got_central = aperture_spread_factor_actual(W0_CENTRAL_M)
    assert abs(got_central - 0.858) < 0.02, got_central
    assert got_central < aperture_onaxis_factor_actual(W0_CENTRAL_M)

    # the floor is shared with the on-axis table (same input-radius grid, same bore): below it
    # RAISES, and clamp_floor=True holds the floor's own ratio for an envelope calculation
    with pytest.raises(ValueError, match="below this bore's floor"):
        aperture_spread_factor_actual(30e-6)
    floor_val = aperture_spread_factor_actual(30e-6, clamp_floor=True)
    assert floor_val == pytest.approx(aperture_spread_factor_actual(40.89e-6, clamp_floor=True), abs=5e-3)

    # a grid of waists, since a Monte Carlo prior draw is exactly what this function exists to serve
    grid = np.array([42.4e-6, W0_CENTRAL_M, 60.0e-6])
    on_grid = aperture_spread_factor_actual(grid)
    assert np.shape(on_grid) == (3,)
    for w, one in zip(grid, on_grid):
        assert abs(one - aperture_spread_factor_actual(float(w))) < 1e-12
    assert isinstance(aperture_spread_factor_actual(W0_CENTRAL_M), float)


@pytest.mark.xfail(strict=True, reason=(
    "F527, plan V6.9: the same-reading spread factor lifts the posterior bound from 404 to 1201 and makes the "
    "geometry 0.60 of its variance, so V6.0 keeps the producer at its published convention and the change is "
    "its own wave with the physics chair; this marker comes off in that wave"))
def test_the_delta_alpha_posterior_reads_the_same_reading_spread_factor():
    """F280/A136: `run_delta_alpha_posterior.py` fed its same-reading w0 into the free-focus
    `aperture_spread_factor`, so the shift (already same-reading since F280) and the spread it
    divided by disagreed about which beam they meant. C6b closes it: the producer now imports
    `aperture_spread_factor_actual` and its conversion factor moves with the fix. The producer's
    OWN function is called here, never its `main()`, so nothing is written."""
    from pathlib import Path
    from conftest import load_script_module
    from rb5s6s.lineshape import aperture_spread_factor, aperture_spread_factor_actual, stark_shift_S0_mhz

    root = Path(__file__).resolve().parents[1]
    src = (root / "scripts" / "run_delta_alpha_posterior.py").read_text(encoding="utf-8")
    assert "aperture_spread_factor_actual" in src
    assert "aperture_spread_factor(W0_PRIOR_M)" not in src, "the free-focus call at the same-reading w0 must be gone"

    if not (root / "results" / "stark_joint.csv").is_file():
        pytest.skip("results/stark_joint.csv not committed")
    dap = load_script_module("run_delta_alpha_posterior", root / "scripts" / "run_delta_alpha_posterior.py")
    rows = {r[1]: r for r in dap._rows()}
    limit_new = float(rows["delta_alpha_abs_ub95_profile"][2])

    named, kap, _ = dap._joint()
    k_ub95 = float(named["kappa_ub95"]["value"])
    conv_old = dap.P_REF_W / (stark_shift_S0_mhz(dap.P_REF_W, dap.W0_PRIOR_M, dap.RHO_PRIOR, 1.0)
                              * aperture_spread_factor(dap.W0_PRIOR_M))
    conv_new = dap.P_REF_W / (stark_shift_S0_mhz(dap.P_REF_W, dap.W0_PRIOR_M, dap.RHO_PRIOR, 1.0)
                              * aperture_spread_factor_actual(dap.W0_PRIOR_M, clamp_floor=True))
    assert conv_new != pytest.approx(conv_old), "the two conventions differ at the bore-limited waist"
    # the row is written to the nearest a.u. (f"{ub_profile:.0f}"), so the comparison allows the
    # rounding a formatted CSV cell carries and no more
    assert limit_new == pytest.approx(k_ub95 * conv_new, abs=0.5), (
        "the committed row must be built from the same-reading conversion, not the free-focus one")
    assert limit_new != pytest.approx(k_ub95 * conv_old, abs=0.5), (
        "and must NOT still match the free-focus conversion this fix replaced")


def test_the_predicted_shift_per_recorded_watt_carries_the_on_axis_factor_once():
    """F39, F280: three producers computed the prediction identically, so it lives in the package;
    it is the ideal relation times the ACTUAL-focus on-axis factor at the same waist (corrected
    2026-09-21 from the free-focus convention, which read the wrong beam), and nothing else."""
    from rb5s6s.stark import kappa_pred_per_watt
    from rb5s6s.lineshape import aperture_onaxis_factor_actual, stark_shift_S0_mhz
    from rb5s6s import constants as K
    for w0_um in (42.4, 45.0, 52.1):
        w0 = w0_um * 1e-6
        want = stark_shift_S0_mhz(1.0, w0, rho=K.RHO_RETRO) * aperture_onaxis_factor_actual(w0)
        assert abs(kappa_pred_per_watt(w0, K.RHO_RETRO) / want - 1.0) < 1e-12, w0_um
    # the defaults are the record's own geometry, and the factor is applied once, not twice; at
    # the bore-limited central value the actual-convention factor reads about 0.888 (F280), below
    # the free-convention 0.9-to-1.0 band the pre-F280 test asserted here
    d = kappa_pred_per_watt()
    ideal = stark_shift_S0_mhz(1.0, K.W0_CENTRAL_M, rho=K.RHO_RETRO)
    assert 0.85 < d / ideal < 1.0, (d, ideal)


def test_a_design_point_below_the_bore_floor_must_name_its_unclipped_convention():
    """C6a (plan A127): a 16 um design point is below the bore's floor (about 40.9 um, F291), so
    the bench convention REFUSES it and only `bore_in_path=False`, the unclipped Gaussian of a
    design with the bore out of the focusing path, computes it. Planted both ways: the default
    raises at the design point, the flag returns the ideal relation exactly, and at the bench's
    own focus the flag's only effect is the on-axis factor it removes."""
    from rb5s6s.stark import kappa_pred_per_watt
    from rb5s6s.lineshape import stark_shift_S0_mhz
    from rb5s6s import constants as K
    with pytest.raises(ValueError, match="below this bore's floor"):
        kappa_pred_per_watt(16e-6, K.RHO_RETRO)
    got = kappa_pred_per_watt(16e-6, K.RHO_RETRO, bore_in_path=False)
    assert got == stark_shift_S0_mhz(1.0, 16e-6, rho=K.RHO_RETRO)
    bench = kappa_pred_per_watt(K.W0_CENTRAL_M, K.RHO_RETRO)
    free = kappa_pred_per_watt(K.W0_CENTRAL_M, K.RHO_RETRO, bore_in_path=False)
    assert 0.85 < bench / free < 1.0, (bench, free)


def test_both_aperture_factors_take_a_waist_grid_and_agree_with_the_scalar_call():
    """A GRID OF WAISTS IS THE NATURAL CALL AND IT RAISED (F57, 2026-09-17).

    `run_delta_alpha_posterior.py` passes its whole waist grid to the spread factor, and the
    wiring of 2026-09-17 had both factors doing `float(w0_m)`, so the producer died on the
    first row and left `results/delta_alpha_posterior.csv` holding its header alone. Fourteen
    bound references into that table went dangling, which is how it surfaced: as fourteen
    documentation defects rather than as a broken producer. Both paths are checked here, and
    the grid must agree with the scalar element by element or the vectorisation is a different
    computation wearing the same name.
    """
    import numpy as np
    from rb5s6s.lineshape import aperture_onaxis_factor, aperture_spread_factor
    from rb5s6s.constants import W0_CENTRAL_M
    grid = np.array([42.4e-6, 52.1e-6, W0_CENTRAL_M, 76.0e-6])

    on_grid = aperture_onaxis_factor(grid)
    assert np.shape(on_grid) == (4,)
    for w, got in zip(grid, on_grid):
        assert abs(got - aperture_onaxis_factor(float(w))) < 1e-12

    sp_grid = aperture_spread_factor(grid)
    assert np.shape(sp_grid) == (4,)
    for w, got in zip(grid, sp_grid):
        assert abs(got - aperture_spread_factor(float(w))) < 1e-12

    # and a scalar still returns a python float, which is what every committed caller stores
    assert isinstance(aperture_onaxis_factor(W0_CENTRAL_M), float)
    assert isinstance(aperture_spread_factor(W0_CENTRAL_M), float)


def test_the_composite_convolution_is_the_direct_sum_whichever_method_runs(monkeypatch):
    """C6b item 6: `composite_profile` convolves by whichever of the direct sum and the FFT scipy predicts faster,
    and on its own grids the result is the direct sum to the transform's rounding (measured 7e-16 of peak), from a
    grid where the direct sum is chosen (about 1 000 points) to one where the FFT is (about 12 000, eleven times
    faster). A change of alignment or scale in either path would show here at order one."""
    import rb5s6s.lineshape as LS
    cases = [dict(gamma_coll=0.12, sigma_laser=1.6, transit_fwhm=1.39),
             dict(gamma_coll=0.5, sigma_laser=0.3, transit_fwhm=0.9, transit_kind="gaussian"),
             dict(gamma_coll=0.02, sigma_laser=0.1, transit_fwhm=0.3)]
    for kw in cases:
        g_auto, p_auto = LS.composite_profile(**kw)
        monkeypatch.setattr(LS, "_COMPOSITE_CONVOLVE", np.convolve)
        g_dir, p_dir = LS.composite_profile(**kw)
        monkeypatch.undo()
        assert np.array_equal(g_auto, g_dir)
        assert np.max(np.abs(p_auto - p_dir)) <= 1e-13 * np.max(p_dir)
