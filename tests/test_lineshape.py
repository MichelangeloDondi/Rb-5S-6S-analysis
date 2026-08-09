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
    # trap for fixed-lock fits that float s0). The cell-integral + moment-
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
    # forward model the fixed-lock joint fit checks the data against.
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
    for z, mean_note, skew_note in ((0.5, 0.6209, 0.4793), (2.0, 0.4538, -0.3016),
                                    (5.0, 0.3800, -0.4460)):
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
    nu = np.arange(-4.0, 1.0, 0.002)
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
    """n_photon=1 on the same geometry: mean pull -s0/2 (the flat case)."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 1.5
    nu = np.arange(-3.0, 1.0, 0.002)
    r = np.linspace(0.0, 5.0, 400001)
    f = stark_from_intensity_profile(nu, s0, np.exp(-2.0 * r ** 2), r,
                                     n_photon=1)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert abs(mean - (-s0 / 2.0)) < 5e-3


def test_general_profile_evanescent_is_not_a_triangle():
    """A nanofibre-like evanescent field (I ~ e^{-2r/L}, measure r dr)
    must give a different distribution: the measure grows outward while the
    intensity dies, boosting the small-shift tail, so the mean pull is
    SHALLOWER than the focused beam's -2/3 s0 (an early version of this
    test asserted the opposite; the machinery corrected the intuition)."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 2.0
    nu = np.arange(-4.0, 1.0, 0.002)
    r = np.linspace(120.0, 800.0, 200001)      # nm, from the fibre surface
    L = 100.0
    inten = np.exp(-2.0 * (r - r[0]) / L)
    f = stark_from_intensity_profile(nu, s0, inten, r, n_photon=2)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert -(2.0 / 3.0) * s0 + 0.02 < mean < -0.2 * s0, mean
    assert abs(float(np.sum(f) * (nu[1] - nu[0])) - 1.0) < 1e-9


def test_general_profile_axial_lorentzian_mean():
    """The axial line I(z) = 1/(1+z^2) with uniform measure: weight u^2 dz
    with dz ~ du/(u^1.5 sqrt(1-u)) gives mean -3/4 s0 for n=2 -- a genuinely
    different geometry from the transverse triangle, kept as the example
    that the seam distinguishes geometries the summary widths cannot."""
    from rb5s6s.lineshape import stark_from_intensity_profile
    s0 = 2.0
    nu = np.arange(-4.0, 1.0, 0.002)
    z = np.linspace(-200.0, 200.0, 400001)
    f = stark_from_intensity_profile(nu, s0, 1.0 / (1.0 + z ** 2),
                                     np.ones_like(z), n_photon=2)
    mean = float(np.sum(nu * f) * (nu[1] - nu[0]))
    assert abs(mean - (-0.75 * s0)) < 5e-3, mean


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
    model: the n=1 flat density pulls the line by -s0/2 against the
    triangle's -2/3 s0, so the two composite lines' means must differ by
    s0/6. Differencing the two means cancels the shared symmetric core and
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
    assert abs(dm - s0 / 6.0) < 0.05, dm
