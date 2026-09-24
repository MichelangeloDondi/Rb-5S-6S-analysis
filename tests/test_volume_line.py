"""Tests for `rb5s6s/volume_line.py`, the non-convolving joint per-path line promoted from
`private/cache/plan_2026-09-16/p18_joint_line.py` and `p18_joint_table.py` (owner order O45/O46;
findings F290, F293, F294 and F317 in `private/cache/plan_2026-09-16/FINDINGS_NIGHT.md`; see
`private/cache/plan_2026-09-18/volume_line_report.md`).

EVERY NUMBER ASSERTED HERE IS THIS PROMOTION'S OWN, AT ITS OWN FAST SETTINGS, not the prototype's
production numbers: the prototype used n_path=8000 and a 27x11 table (minutes of compute) to
reach sub-percent and sub-0.05-sd readings; these tests use n_path and grids one to two orders
of magnitude smaller so the whole file runs in well under a minute, and each test's docstring
states its own calibrated reading beside its tolerance rather than borrowing the prototype's.
No test here uses the `slow` marker (`tests/conftest.py`): none is a high-statistics closure.
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.signal import fftconvolve

from rb5s6s._compat import trapezoid
from rb5s6s.constants import W0_BAND_M, W0_CENTRAL_M
from rb5s6s.lineshape import RAMP_SIDE, gaussian, local_ramp_density, lorentzian, ramp_mixture
from rb5s6s.volume_line import (
    B_CUT,
    GaussianBeam,
    JointTable,
    TAU_EDGE,
    collection_half_window_m,
    joint_spectrum,
    sample_atoms,
)

M2 = 1.0
T_C = 130.0
Z_RATIO = 0.6           # a representative collection ratio (F293/F294's own pre-wave node: 0.605)
S0_MHZ = 0.6             # a representative on-axis AC-Stark shift (MHz), well inside the L's band
GAMMA_HOM_MHZ = 3.6       # a representative homogeneous FWHM (MHz), near the archive's own


@pytest.fixture(scope="module")
def beam():
    return GaussianBeam(W0_CENTRAL_M, M2)


@pytest.fixture(scope="module")
def half_window_m(beam):
    return collection_half_window_m(beam, Z_RATIO)


# =============================================================================================
# GaussianBeam and sample_atoms: the interface and its port from scripts/run_kernel_mc.py
# =============================================================================================

def test_gaussian_beam_geometry():
    """w(0) == w0 (the focus); w grows away from focus; z_R_m matches pi w0^2/(M2 lambda); u is 1
    on-axis at the focus and falls both with the impact parameter and away from focus."""
    b = GaussianBeam(W0_CENTRAL_M, 1.0)
    assert b.w(0.0) == pytest.approx(b.w0_m)
    assert b.u(0.0, 0.0) == pytest.approx(1.0)
    z = np.array([0.0, b.z_R_m, 2 * b.z_R_m])
    w = b.w(z)
    assert np.all(np.diff(w) > 0), "the beam must diverge away from focus"
    assert b.z_R_m == pytest.approx(np.pi * b.w0_m ** 2 / (b.m2 * b.lambda_m))
    assert b.u(50e-6, 0.0) < b.u(0.0, 0.0), "intensity must fall off-axis"
    assert b.u(0.0, b.z_R_m) < b.u(0.0, 0.0), "on-axis intensity must fall away from focus"


def test_gaussian_beam_rejects_unphysical_inputs():
    """M^2 < 1 is not a real beam (`fullmodel.collection_z_ratio_m2`'s own guard, ported as a
    rule and not merely a convention); a non-positive waist is not a beam at all."""
    with pytest.raises(ValueError):
        GaussianBeam(-1e-6, 1.0)
    with pytest.raises(ValueError):
        GaussianBeam(42e-6, 0.5)


def test_collection_half_window_m_needs_z_r_m():
    """A beam without the GaussianBeam-only `z_R_m` convenience attribute must raise rather than
    silently guessing a window -- the future bore-clipped beam may have no single Rayleigh range."""
    class _NoRayleigh:
        def w(self, z_m):
            return np.full_like(np.asarray(z_m, dtype=float), 42e-6)

        def u(self, b_m, z_m):
            return np.ones_like(np.asarray(b_m, dtype=float))

    with pytest.raises(AttributeError):
        collection_half_window_m(_NoRayleigh(), 0.6)


def test_sample_atoms_matches_scripts_run_kernel_mc(beam, half_window_m):
    """`sample_atoms(rng, n, GaussianBeam(w0_m, m2), ...)` must reproduce
    `scripts.run_kernel_mc._sample(rng, n, w0_m, m2, ...)` BIT FOR BIT (same seed): the port
    generalised the formula over a beam interface, it did not change the arithmetic or the RNG
    draw order (z, then b, then v)."""
    from scripts import run_kernel_mc as mc

    rng_ref = np.random.default_rng(11)
    # TWO THINGS MOVED IN `_sample` ON 2026-09-23 (F372) AND NEITHER IS THE ARITHMETIC THIS ASSERTS.
    # It returns two more values -- the impact parameter and z, which the chord needs to walk the
    # REAL radial profile -- so the first four are the contract. And its DEFAULT beam is now the
    # bore-clipped one, because a node's waist is produced by an input radius through the bore
    # rather than assumed, so the Gaussian must be ASKED FOR to compare like with like. Passing the
    # waist and letting it default would compare a clipped beam against a Gaussian one, which is a
    # real difference and not a regression.
    w_ref, v_ref, u_ref, flux_ref = mc._sample(
        rng_ref, 500, beam.w0_m, beam.m2, T_C, half_window_m,
        beam=mc._GaussianBeam(beam.w0_m, beam.m2))[:4]

    rng_new = np.random.default_rng(11)
    w_new, v_new, u_new, flux_new = sample_atoms(rng_new, 500, beam, T_C, half_window_m)

    assert np.array_equal(w_ref, w_new)
    assert np.array_equal(v_ref, v_new)
    assert np.array_equal(u_ref, u_new)
    assert np.array_equal(flux_ref, flux_new)


def test_sample_atoms_point_beam_degenerate_case(beam):
    """`half_window_m <= 0` collapses every atom to z=0 (a point beam at the focus), so every
    drawn radius equals w0 exactly."""
    rng = np.random.default_rng(3)
    w, v, u_b, flux_len = sample_atoms(rng, 40, beam, T_C, 0.0)
    assert np.allclose(w, beam.w0_m)
    assert np.all(v > 0.0)
    assert np.all(u_b <= 1.0 + 1e-12)
    assert np.all(flux_len >= 0.0)


def test_sample_atoms_b_cut_respected(beam, half_window_m):
    """No impact parameter exceeds `b_cut` local beam radii (the sampler's own stated cut).
    `b` is not returned directly; it is recovered by inverting
    `u_b = (w0/w)^2 exp(-2 b^2/w^2)` -> `b = w sqrt(-0.5 ln(u_b (w/w0)^2))`."""
    rng = np.random.default_rng(4)
    n = 2000
    w, v, u_b, flux_len = sample_atoms(rng, n, beam, T_C, half_window_m, b_cut=B_CUT)
    arg = u_b * (w / beam.w0_m) ** 2
    b = w * np.sqrt(np.maximum(-0.5 * np.log(np.clip(arg, 1e-300, 1.0)), 0.0))
    assert np.all(b <= B_CUT * w + 1e-9 * w)


# =============================================================================================
# joint_spectrum: the two-time correlation line, its limits, and determinism
# =============================================================================================

def _delta_grid(dmax: float, n: int) -> np.ndarray:
    return np.linspace(-dmax, dmax, n)


def test_the_zero_shift_line_is_symmetric_and_carries_the_transit_convolutions_variance(beam):
    """F317's plant (2026-09-22). With no light shift the joint line is the flux-weighted transit
    line convolved with the homogeneous Lorentzian, a symmetric line, so its third moment over a
    symmetric window is zero and its variance is the transit-kernel convolution's
    (`lineshape.model_profile` with this record's transit width and collection factor, the form
    the kernel gate grades against the same Monte Carlo). CALIBRATED at n_path=8000 over +-30 MHz:
    the variance agrees to 1e-4 and the third moment reads 2e-13 MHz^3. The route this function used
    until 2026-09-22, the Lorentzian carried inside each atom's own transform, reads a variance 4.5
    per cent high and a third moment of -0.064 MHz^3 here, stable in the atom count, so both bounds
    below refuse it with a margin of nine and sixty."""
    from rb5s6s import constants as K
    from rb5s6s import fullmodel as FM
    from rb5s6s.lineshape import model_profile
    zr = FM.collection_z_ratio_m2(W0_CENTRAL_M, M2)
    d = _delta_grid(30.0, 3001)
    j = joint_spectrum(S0_mhz=0.0, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                       half_window_m=collection_half_window_m(beam, zr), n_path=8000, seed=0, delta_mhz=d)
    transit = K.transit_fwhm_from_w0(W0_CENTRAL_M, T_C, isotope=87) * FM.transit_collection_factor(W0_CENTRAL_M, M2)
    ref = model_profile(d, gamma_coll=0.0, sigma_laser_fwhm=0.0, transit_fwhm=transit, s0=0.0,
                        gamma_nat_mhz=GAMMA_HOM_MHZ, laser_kind="lorentzian")

    def moments(y):
        y = y / trapezoid(y, d)
        mu = trapezoid(d * y, d)
        x = d - mu
        return trapezoid(x ** 2 * y, d), trapezoid(x ** 3 * y, d)

    (vj, k3j), (vr, _) = moments(j), moments(ref)
    assert abs(vj / vr - 1.0) < 5e-3, f"zero-shift variance {vj:.4f} against the transit convolution's {vr:.4f}"
    assert abs(k3j) < 1e-3, f"zero-shift third moment {k3j:.3e} MHz^3 where the line is symmetric"


def test_the_homogeneous_widths_are_applied_after_the_ensemble_sum(beam, half_window_m):
    """The construction (F317): the coherent line on an internal grid symmetric about zero, then the
    Lorentzian and the laser's Gaussian by FFT convolution there, then the interpolation onto the
    caller's axis. Rebuilt here by hand from the zero-width call, at a non-zero shift and both widths,
    it agrees to floating point, so no second route exists for a caller to reach."""
    from rb5s6s.volume_line import HOMOG_MARGIN_MHZ, HOMOG_STEP_MHZ
    delta = _delta_grid(24.0, 801)
    kw = dict(S0_mhz=S0_MHZ, beam=beam, T_C=T_C, half_window_m=half_window_m, n_path=600, seed=0,
              n_tau=151, tau_edge=TAU_EDGE)
    got = joint_spectrum(gamma_hom_mhz=GAMMA_HOM_MHZ, sigma_laser_mhz=1.2, delta_mhz=delta, **kw)
    half = int(np.ceil((24.0 + HOMOG_MARGIN_MHZ) / HOMOG_STEP_MHZ))
    grid = np.linspace(-half * HOMOG_STEP_MHZ, half * HOMOG_STEP_MHZ, 2 * half + 1)
    coh = joint_spectrum(gamma_hom_mhz=0.0, delta_mhz=grid, **kw)
    dnu = grid[1] - grid[0]
    line = fftconvolve(coh, lorentzian(grid, GAMMA_HOM_MHZ), mode="same") * dnu
    line = fftconvolve(line, gaussian(grid, 1.2), mode="same") * dnu
    want = np.interp(delta, grid, line, left=0.0, right=0.0)
    assert np.max(np.abs(got - want)) <= 1e-12 * np.max(np.abs(want))


def test_joint_spectrum_large_gamma_asymptote(beam, half_window_m):
    """chirp_dephased.py's other named limit, ported: as gamma_hom grows, fast dephasing kills the
    coherent transit broadening before it develops, and the line tends to the quasi-static dwell
    distribution (`lineshape.ramp_mixture` at this beam's own z_ratio) convolved with a
    Lorentzian(gamma_hom) -- NOT an exact identity at any finite gamma_hom. CALIBRATED at
    gamma_hom=25 MHz (about 7x this module's GAMMA_HOM_MHZ), n_path=1000, n_tau=151: 1.5 per cent of
    peak since F317 (2026-09-22). The reading of 19.6 per cent this test carried before, and the
    prototype's 3.4 per cent at 20 MHz, were the per-atom Lorentzian's defect and not the limit's
    approach: a 25 MHz Lorentzian cannot be held inside a slow atom's own band of about +-15 MHz."""
    gamma_big = 25.0
    wide = _delta_grid(100.0, 2001)
    n_path, n_tau = 1000, 151
    s_direct = joint_spectrum(S0_mhz=S0_MHZ, gamma_hom_mhz=gamma_big, beam=beam, T_C=T_C,
                              half_window_m=half_window_m, n_path=n_path, seed=0,
                              delta_mhz=wide, n_tau=n_tau, tau_edge=TAU_EDGE)
    xg = np.linspace(0.0, 1.0, 2001)
    gx = local_ramp_density(xg)
    z_ratio_used = half_window_m / beam.z_R_m
    ramp = ramp_mixture(wide, S0_MHZ, z_ratio_used, xg, gx)
    lor_big = lorentzian(wide, gamma_big)
    dnu = wide[1] - wide[0]
    asym = np.convolve(ramp, lor_big, mode="same") * dnu
    s_direct_n = s_direct / trapezoid(s_direct, wide)
    asym_n = asym / trapezoid(asym, wide)
    rel = np.max(np.abs(asym_n - s_direct_n)) / np.max(s_direct_n)
    assert rel < 0.05, f"large-gamma asymptote relative deviation {rel:.4f} exceeds 0.05 of peak"


def test_joint_spectrum_ramp_side_is_read_not_restated(beam, half_window_m):
    """Flipping `sign` (never the module's own hardcoded default, which reads `lineshape.RAMP_SIDE`)
    mirrors the line about zero detuning: a positive-S0 line built with `sign=-RAMP_SIDE` matches
    the negate of the default-sign line, to floating point (same atom sample, deterministic FFTs)."""
    delta = _delta_grid(20.0, 401)
    n_path, n_tau = 300, 81
    default = joint_spectrum(S0_mhz=S0_MHZ, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                             half_window_m=half_window_m, n_path=n_path, seed=1, delta_mhz=delta,
                             n_tau=n_tau, tau_edge=TAU_EDGE, sign=RAMP_SIDE)
    flipped = joint_spectrum(S0_mhz=S0_MHZ, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                             half_window_m=half_window_m, n_path=n_path, seed=1, delta_mhz=delta,
                             n_tau=n_tau, tau_edge=TAU_EDGE, sign=-RAMP_SIDE)
    assert np.allclose(default, flipped[::-1], atol=1e-12, rtol=1e-9)


def test_joint_spectrum_determinism(beam, half_window_m):
    """Two calls at the same seed are IDENTICAL (bit for bit); a different seed moves the result:
    the atom sampler is the only source of randomness, and it is seeded, never left ambient."""
    delta = _delta_grid(20.0, 301)
    kwargs = dict(S0_mhz=S0_MHZ, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                 half_window_m=half_window_m, n_path=200, delta_mhz=delta, n_tau=81,
                 tau_edge=TAU_EDGE)
    a = joint_spectrum(seed=5, **kwargs)
    b = joint_spectrum(seed=5, **kwargs)
    c = joint_spectrum(seed=6, **kwargs)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_joint_spectrum_sigma_laser_zero_is_a_no_op(beam, half_window_m):
    """`sigma_laser_mhz=0.0` (the default) must be an EXACT no-op, matching
    `lineshape.model_profile`'s own zero-width-kernel convention (a delta function convolves as
    the identity) -- not a small-width approximation that merely gets close."""
    delta = _delta_grid(20.0, 301)
    kwargs = dict(S0_mhz=S0_MHZ, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                 half_window_m=half_window_m, n_path=200, seed=9, delta_mhz=delta, n_tau=81,
                 tau_edge=TAU_EDGE)
    a = joint_spectrum(sigma_laser_mhz=0.0, **kwargs)
    b = joint_spectrum(**kwargs)
    assert np.array_equal(a, b)


# =============================================================================================
# JointTable: the fast, tabulated form
# =============================================================================================

@pytest.fixture(scope="module")
def small_table():
    """A small, fast table (seconds): reused across the structural tests below. The tight
    interpolation-error target is a SEPARATE, finer table built only by its own test."""
    delta = np.linspace(-24.0, 24.0, 401)
    S0_grid = np.linspace(0.3, 1.0, 5)
    w0_grid = np.linspace(W0_BAND_M[0] + 1e-6, W0_BAND_M[1] - 1e-6, 4)
    return JointTable.build(S0_grid=S0_grid, w0_grid=w0_grid, delta_mhz=delta, m2=M2, T_C=T_C,
                            n_path=400, seed=0, z_ratio=Z_RATIO, n_tau=81, tau_edge=TAU_EDGE)


def test_joint_table_bilinear_reproduces_grid_nodes(small_table):
    """Bilinear interpolation AT an exact grid node must reproduce that node's own tabulated
    curve exactly (the prototype's own selftest plant)."""
    t = small_table
    node = t._bilinear(float(t.S0_grid[2]), float(t.w0_grid[1]))
    assert np.allclose(node, t.table[2, 1])


def test_joint_table_profile_area_normalises_and_matches_direct_at_zero_widths(small_table, beam):
    """`profile(nu, s0, w0, gamma_hom_mhz=0, sigma_laser_mhz=0)` skips both convolutions (matching
    `lineshape.model_profile`'s convention that an absent kernel is a no-op) and its output area,
    computed over the CALLER's own `nu` axis (matching `model_profile`'s own normalisation, not
    the internal grid's), is 1."""
    t = small_table
    nu = t.delta_mhz
    s0q, w0q = float(t.S0_grid[1]), float(t.w0_grid[2])
    prof = t.profile(nu, s0q, w0q, gamma_hom_mhz=0.0, sigma_laser_mhz=0.0)
    assert trapezoid(prof, nu) == pytest.approx(1.0, abs=1e-9)
    direct_shape = t._bilinear(s0q, w0q)
    ref = direct_shape / trapezoid(direct_shape, nu)
    assert np.allclose(prof, ref, atol=1e-9)


def test_joint_table_profile_fft_convolution_matches_direct_convolution(small_table):
    """The fast model's FFT convolution (`scipy.signal.fftconvolve`) must match a direct
    `np.convolve` of the SAME kernels to floating-point precision -- the one piece of `profile`
    that must be exactly right for speed to be free (the prototype's own `plant_fft_matches_direct`,
    re-run here against this promotion's own `profile`, not a synthetic random case)."""
    t = small_table
    nu = t.delta_mhz
    s0q, w0q = float(t.S0_grid[1]), float(t.w0_grid[2])
    gamma_hom, sigma_laser = 2.5, 1.0
    fast = t.profile(nu, s0q, w0q, gamma_hom_mhz=gamma_hom, sigma_laser_mhz=sigma_laser)

    m_coh = t._bilinear(s0q, w0q)
    dnu = nu[1] - nu[0]
    from rb5s6s.lineshape import gaussian
    direct = np.convolve(m_coh, lorentzian(nu, gamma_hom), mode="same") * dnu
    direct = np.convolve(direct, gaussian(nu, sigma_laser), mode="same") * dnu
    direct = direct / trapezoid(direct, nu)
    assert np.max(np.abs(fast - direct)) < 1e-10


def test_joint_table_save_load_roundtrip(small_table, tmp_path):
    """`save`/`load` round-trips every grid, the table itself, and the scalar provenance."""
    t = small_table
    p = tmp_path / "table.npz"
    t.save(p)
    t2 = JointTable.load(p)
    assert np.allclose(t2.S0_grid, t.S0_grid)
    assert np.allclose(t2.w0_grid, t.w0_grid)
    assert np.allclose(t2.table, t.table)
    assert np.allclose(t2.delta_mhz, t.delta_mhz)
    assert t2.m2 == t.m2 and t2.T_C == t.T_C and t2.n_path == t.n_path
    assert t2.seed == t.seed and t2.z_ratio == t.z_ratio


def test_joint_table_rejects_malformed_grids():
    """A shape mismatch, a non-ascending axis, or a one-point axis must all raise: a silent
    misread here would return a plausible-looking but wrong interpolation (the record's own
    `_require_density_grid` names this class of defect)."""
    delta = np.linspace(-5.0, 5.0, 11)
    with pytest.raises(ValueError):
        JointTable(S0_grid=np.array([0.1, 0.2, 0.3]), w0_grid=np.array([40e-6, 42e-6]),
                  table=np.zeros((3, 2, 10)), delta_mhz=delta, m2=1.0, T_C=130.0, n_path=10,
                  seed=0, z_ratio=0.6)
    with pytest.raises(ValueError):
        JointTable(S0_grid=np.array([0.3, 0.2, 0.4]), w0_grid=np.array([40e-6, 42e-6]),
                  table=np.zeros((3, 2, 11)), delta_mhz=delta, m2=1.0, T_C=130.0, n_path=10,
                  seed=0, z_ratio=0.6)
    with pytest.raises(ValueError):
        JointTable(S0_grid=np.array([0.3]), w0_grid=np.array([40e-6, 42e-6]),
                  table=np.zeros((1, 2, 11)), delta_mhz=delta, m2=1.0, T_C=130.0, n_path=10,
                  seed=0, z_ratio=0.6)


def test_joint_table_interpolation_error_under_a_thousandth_of_peak():
    """THE TASK'S OWN TARGET: the table's interpolation error at held-out points under 1e-3 of
    peak. Built at 17x17 (S0 in [0.3, 1.0] MHz, w0 in [41, 44] um), n_path=1000, n_tau=81 --
    CALIBRATED settings, chosen because a coarser grid (e.g. 9x9) does not clear the target
    (measured 3.8e-3 at that density during this promotion's own calibration; see the report).
    Held out at nine interior grid-cell midpoints (3x3, `p18_joint_table.pick_midpoints`'s own
    convention -- none on the grid itself), compared against a DIRECT `joint_spectrum` call at
    the same seed and n_path (so ensemble Monte Carlo roughness common to both sides cancels, the
    prototype's own reading: interpolation error here is dominated by bilinear truncation, not by
    n_path -- boosting n_path 12x at a fixed grid moved this reading by under 15 per cent, this
    promotion's own check during calibration). CALIBRATED result: 5.8e-4 of peak, under the 1e-3
    target with genuine margin. This is this file's one slow-ish test (about fifteen seconds, the
    table build) and still not `slow`-marker material (`tests/conftest.py`'s own bar is the
    ~90-second high-statistics closures)."""
    delta = np.linspace(-20.0, 20.0, 301)
    S0_grid = np.linspace(0.3, 1.0, 17)
    w0_grid = np.linspace(41.0e-6, 44.0e-6, 17)
    n_path, n_tau = 1000, 81
    table = JointTable.build(S0_grid=S0_grid, w0_grid=w0_grid, delta_mhz=delta, m2=M2, T_C=T_C,
                            n_path=n_path, seed=0, z_ratio=Z_RATIO, n_tau=n_tau, tau_edge=TAU_EDGE)

    def _pick_midpoints(grid, n_each):
        m = len(grid)
        ks = sorted(set(int(k) for k in np.clip(np.round(np.linspace(0, m - 2, n_each)), 0, m - 2)))
        return [0.5 * (grid[k] + grid[k + 1]) for k in ks]

    worst = worst_obs = 0.0
    for s0q in _pick_midpoints(S0_grid, 3):
        for w0q in _pick_midpoints(w0_grid, 3):
            beam_q = GaussianBeam(float(w0q), M2)
            hw = collection_half_window_m(beam_q, Z_RATIO)
            direct = joint_spectrum(S0_mhz=float(s0q), gamma_hom_mhz=0.0, beam=beam_q, T_C=T_C,
                                    half_window_m=hw, n_path=n_path, seed=0, delta_mhz=delta,
                                    n_tau=n_tau, tau_edge=TAU_EDGE)
            interp = table._bilinear(float(s0q), float(w0q))
            err = np.max(np.abs(interp - direct)) / direct.max()
            worst = max(worst, err)
            # THE ACCEPTANCE IN THE OBSERVABLE'S OWN UNITS (V5.2a, 2026-09-22): what a fit sees is the joint
            # line convolved with the homogeneous Lorentzian and the laser Gaussian, and the table must sit
            # under 0.05 of the per-point noise everywhere on it. The most demanding noise is the floor of the
            # archive's brightest condition, 4.6e-3 of its peak (4154 nm, 130 C, 225 mW: a = 0.0123 V on a
            # 2.648 V peak, results/noise_model.csv and results/detection_budget.csv), so 0.05 of it is 2.3e-4;
            # the bound below is 1e-4. Measured: 5.1e-5 of peak, 0.0027 of the pointwise sd.
            dnu = delta[1] - delta[0]
            obs = [fftconvolve(fftconvolve(m, lorentzian(delta, 3.714), mode="same") * dnu,
                               gaussian(delta, 0.475), mode="same") * dnu for m in (direct, interp)]
            worst_obs = max(worst_obs, np.max(np.abs(obs[1] - obs[0])) / obs[0].max())
    assert worst < 1e-3, f"worst held-out interpolation error {worst:.6f} exceeds 1e-3 of peak"
    assert worst_obs < 1e-4, f"worst held-out error on the observable line {worst_obs:.2e} exceeds 1e-4 of peak"


# =============================================================================================
# The chord (C6b, 2026-09-22): a beam that is not Gaussian is read along every atom's path
# =============================================================================================

def test_the_geometry_draw_is_the_same_draw(beam, half_window_m):
    """`return_geometry=True` adds each atom's impact parameter and axial position without moving a draw."""
    a = sample_atoms(np.random.default_rng(3), 500, beam, T_C, half_window_m)
    b = sample_atoms(np.random.default_rng(3), 500, beam, T_C, half_window_m, return_geometry=True)
    assert len(b) == 6
    for x, y in zip(a, b[:4]):
        assert np.array_equal(x, y)
    assert np.all(np.abs(b[5]) <= half_window_m) and np.all(b[4] >= 0.0)


def test_the_beam_chord_is_the_gaussian_chord_at_a_gaussian_beam(beam, half_window_m):
    """The plant of `chord="beam"`: read along the path through `GaussianBeam.u`, the intensity history is
    u_b exp(-2 tau^2) and the running phase its integral, so the two chords agree to floating point
    (measured 4e-16 of peak), with a shift and both homogeneous widths on."""
    delta = _delta_grid(15.0, 601)
    kw = dict(S0_mhz=S0_MHZ, gamma_hom_mhz=GAMMA_HOM_MHZ, sigma_laser_mhz=1.0, beam=beam, T_C=T_C,
              half_window_m=half_window_m, n_path=300, seed=2, delta_mhz=delta, n_tau=121, tau_edge=TAU_EDGE)
    g = joint_spectrum(chord="gaussian", **kw)
    b = joint_spectrum(chord="beam", **kw)
    assert np.max(np.abs(g - b)) <= 1e-12 * np.max(np.abs(g))
    assert np.array_equal(joint_spectrum(**kw), g)                  # "auto" at a GaussianBeam is the Gaussian chord


def test_a_clipped_beam_is_read_along_the_chord_by_default():
    """`chord="auto"` never reads a clipped focus through the Gaussian's chord: the two differ for it."""
    from rb5s6s.beam_field import ClippedBeam
    cb = ClippedBeam.at_focus(W0_CENTRAL_M)
    delta = _delta_grid(15.0, 601)
    kw = dict(S0_mhz=S0_MHZ, gamma_hom_mhz=0.0, beam=cb, T_C=T_C,
              half_window_m=collection_half_window_m(GaussianBeam(W0_CENTRAL_M), Z_RATIO),
              n_path=300, seed=2, delta_mhz=delta, n_tau=121, tau_edge=TAU_EDGE)
    auto = joint_spectrum(**kw)
    assert np.array_equal(auto, joint_spectrum(chord="beam", **kw))
    assert not np.allclose(auto, joint_spectrum(chord="gaussian", **kw), rtol=1e-4, atol=0.0)
    with pytest.raises(ValueError, match="chord"):
        joint_spectrum(chord="ring", **kw)


def test_a_table_can_hold_the_optics_collected_length_at_every_waist(tmp_path):
    """C6b: with `half_window_m` every waist node collects the same physical half-length, which is what the bench's
    imaging does; a node then equals a direct `joint_spectrum` at that length exactly (same seed), whatever its
    waist, and the length and the isotope survive a save and a load."""
    L = 3.375e-3
    delta = _delta_grid(15.0, 301)
    w0s = np.array([41.0e-6, 45.0e-6])
    t = JointTable.build(S0_grid=np.array([0.3, 0.8]), w0_grid=w0s, delta_mhz=delta, m2=M2, T_C=T_C,
                         n_path=200, seed=4, n_tau=81, tau_edge=TAU_EDGE, half_window_m=L, isotope=85)
    for j, w0 in enumerate(w0s):
        direct = joint_spectrum(S0_mhz=0.8, gamma_hom_mhz=0.0, beam=GaussianBeam(float(w0), M2), T_C=T_C,
                                half_window_m=L, n_path=200, seed=4, delta_mhz=delta, n_tau=81,
                                tau_edge=TAU_EDGE, isotope=85)
        assert np.array_equal(t.table[1, j], direct)
    t.save(tmp_path / "t.npz")
    back = JointTable.load(tmp_path / "t.npz")
    assert back.half_window_m == L and back.isotope == 85


def test_a_one_waist_table_reads_its_node_and_refuses_any_other_waist(tmp_path):
    """C6b: a fitter's Cell holds one waist, so its table has one waist node, is read there exactly (linear in S0
    alone), and refuses a query at any other waist instead of extrapolating one it never sampled. The cached
    builder returns the stored table on the second call and a new one when an input moves."""
    delta = _delta_grid(15.0, 301)
    kw = dict(S0_grid=np.array([0.2, 0.6, 1.0]), w0_grid=np.array([42.0e-6]), delta_mhz=delta, m2=M2, T_C=T_C,
              n_path=150, seed=1, n_tau=81, tau_edge=TAU_EDGE, half_window_m=3.375e-3)
    t = JointTable.cached(tmp_path, **kw)
    assert len(list(tmp_path.glob("joint_table_*.npz"))) == 1
    half = t._bilinear(0.4, 42.0e-6)
    assert np.allclose(half, 0.5 * (t.table[0, 0] + t.table[1, 0]), rtol=0, atol=1e-15 * np.max(np.abs(t.table)))
    with pytest.raises(ValueError, match="one-waist"):
        t._bilinear(0.4, 42.5e-6)
    again = JointTable.cached(tmp_path, **kw)
    assert np.array_equal(again.table, t.table) and len(list(tmp_path.glob("joint_table_*.npz"))) == 1
    JointTable.cached(tmp_path, **dict(kw, seed=2))
    assert len(list(tmp_path.glob("joint_table_*.npz"))) == 2
