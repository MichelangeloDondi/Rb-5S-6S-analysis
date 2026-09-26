"""Tests for the C6b wide wave (owner O49, re-sent 15:1x: "the model... is not anymore a
convolution"): the non-convolving joint line as the DEFAULT model across
`linefit.fit_condition`, `global_fit.fit_global`, `beta.fit_beta_self`,
`lever_crosscheck.lever_crosscheck_beta`, `sharing_bic.sharing_bic` and
`forecast.synthetic_traces`. Brief: `private/cache/plan_2026-09-18/briefs_2026-09-22/
c6b_wide_brief.md`. The physics: `private/cache/plan_2026-09-16/FINDINGS_NIGHT.md` F293,
F294, F317, F318. The survey: `private/cache/plan_2026-09-18/C6B_CONVOLUTION_MAP.md`. Every
OTHER existing test of these six functions stays on `model="convolution"` (see
`private/cache/plan_2026-09-18/c6b_wide_2026-09-22/REPORT.md` for the full list and why).
This file is what tests the NEW default instead.

TWO THINGS THIS FILE CHECKS, PER THE BRIEF'S OWN ITEM 4:

1. THE MOMENTS AGREEMENT: the joint line agrees with the separable convolution on the EVEN
   windowed moments and differs on the ODD channel, as F318 measured (2026-09-22 11:1x):
   built in the corrected order (F317), the joint line agrees with the convolution to
   within 0.24 archive sd on every even-order statistic at every window 0.5-21 MHz, while
   the odd orders read up to 0.89 sd at high drive and middle windows -- "the convolution
   is adequate for the even channel and marginal for the odd one at the high powers".
   EVERY NUMBER ASSERTED HERE IS THIS FILE'S OWN, at n_path=24000 (this module's constant
   `_N_PATH_MOMENTS`), not F318's own production settings (32000 atoms, two seeds, the
   full noise-law replica ensemble): measured here, at the archive's own 130 C/225 mW/
   42.38 um corner, the EVEN orders (2, 4) agree to within 0.14 to 0.68 per cent RELATIVE
   across the four F318 windows (2, 5, 13, 21 MHz), while the windowed skewness
   (mu3/mu2^1.5) the joint line carries GROWS an order of magnitude past the convolution's
   own S0-induced skew, which stays at its 1e-5 numerical floor -- the same qualitative
   reading (even close, odd carries the real disagreement) at this file's own fast
   settings, not a reproduction of F318's sd-normalised figures.

2. INJECTION-RECOVERY CLOSURES, noiseless first: a fit recovers injected parameters from
   joint-line synthetic traces, for `fit_condition`, `fit_beta_self` and `fit_global` (the
   three fitters this wave switches) and for `forecast.synthetic_traces` paired with
   `fit_condition` (the twin/fitter pairing the brief's item 2 names). `lever_crosscheck_
   beta` and `sharing_bic` are thin wrappers around `fit_global` (every cell of their own
   grids, bands and LOO scans is a `fit_global` call), so a WIRING test -- following this
   repository's own `tests/test_lever_crosscheck_kernel_axis.py` spy convention -- checks
   `model` reaches every one of those calls, instead of re-running their (much more
   expensive, many-fit) full closures under a second model.
"""
from __future__ import annotations

import numpy as np
import pytest

from scipy import stats

from rb5s6s._compat import trapezoid
from rb5s6s.constants import GAMMA_NAT_HZ, W0_BAND_M, W0_CENTRAL_M, transit_fwhm_from_w0
from rb5s6s.moments import windowed_moments
from rb5s6s.density import density_units
from rb5s6s.volume_line import GaussianBeam, collection_half_window_m, joint_spectrum
from rb5s6s import beam_field
from rb5s6s import twin_volume as tv
from rb5s6s.linefit import _shared_profile_grid, fit_condition, joint_condition_profile
from rb5s6s.global_fit import fit_global
from rb5s6s.beta import fit_beta_self
from rb5s6s.forecast import synthetic_traces, _traces_from_shape
from rb5s6s.noise import load_noise_model

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "a unit test of the generator's own arithmetic, not a quoted number"
# lever_crosscheck_beta and sharing_bic are exercised through the LC./SB. module aliases
# inside their own wiring tests below (the spy patches the MODULE attribute, so the call
# must go through the module, not a name bound at import time)

GNAT_MHZ = GAMMA_NAT_HZ / 1e6
#: The record's own pre-wave corner (F293/F294/F318's own node): 130 C, 225 mW, the
#: record's central waist.
T_RECORD_C = 130.0
POWER_RECORD_W = 0.225
Z_RATIO = 0.6
#: This file's own atom count for the deterministic (no-noise) moments comparison --
#: enough that the residual MC noise in the joint line ITSELF (not the physics) is small
#: against the measured relative differences (module docstring's own calibration).
_N_PATH_MOMENTS = 24000


def _record_s0_mhz(power_w: float = POWER_RECORD_W, w0_m: float = W0_CENTRAL_M) -> float:
    return tv.stark_s0_mhz(power_w, w0_m)


# =============================================================================================
# 1. THE MOMENTS AGREEMENT (F318): even orders close, odd orders carry the real disagreement
# =============================================================================================

def test_even_windowed_moments_agree_closely_odd_moments_carry_the_disagreement_F318():
    """At the archive's own corner, the joint line and the convolution agree closely on
    the EVEN windowed moments and carry a real, growing disagreement on the windowed
    skewness -- F318's own qualitative reading, calibrated at this test's own settings
    (module docstring)."""
    gamma_coll = 3.2   # MHz, record-like collisional+companion width
    sigma_laser = 0.475  # MHz, record-like laser Gaussian
    s0 = _record_s0_mhz()

    g_j, p_j = joint_condition_profile(gamma_coll, sigma_laser, "gaussian", s0=s0,
                                       T_C=T_RECORD_C, w0_m=W0_CENTRAL_M, z_ratio=Z_RATIO,
                                       n_path=_N_PATH_MOMENTS, seed=1)
    transit_fwhm = transit_fwhm_from_w0(W0_CENTRAL_M, T_RECORD_C)
    g_c, p_c = _shared_profile_grid(gamma_coll, sigma_laser, transit_fwhm, s0, "gaussian",
                                    model="convolution")

    # both profiles onto the joint's own grid, both re-normalised there, for a fair
    # windowed-moment comparison (mirrors _shared_profile_grid's and JointTable.profile's
    # own convention: an area-normalised profile on the grid the moments are read from)
    nu = g_j
    p_c_on_j = np.interp(nu, g_c, p_c, left=0.0, right=0.0)
    p_c_on_j = p_c_on_j / trapezoid(p_c_on_j, nu)
    p_j_norm = p_j / trapezoid(p_j, nu)

    # F318's own window set (mu4 at 13 MHz, mu4/mu2^2 at 21 MHz are its own decisive cells)
    windows_mhz = (2.0, 5.0, 13.0, 21.0)
    # measured (module docstring): even orders 0.14-0.68 per cent relative across these
    # four windows, a factor of three of margin above the worst measured cell
    even_rel_bound = 0.02
    skew_ratio_floor = 5.0   # the joint line's |skew| is at least this many times the
                             # convolution's own numerical floor, at the wider windows
                             # where F318 reads the odd channel's real cost
    max_even_rel = 0.0
    skew_j_wide, skew_c_wide = [], []
    for wdw in windows_mhz:
        mu_j, _ = windowed_moments(nu, p_j_norm, wdw, orders=(2, 3, 4), baseline=None)
        mu_c, _ = windowed_moments(nu, p_c_on_j, wdw, orders=(2, 3, 4), baseline=None)
        for order in (2, 4):
            rel = abs(mu_j[order] - mu_c[order]) / abs(mu_c[order])
            max_even_rel = max(max_even_rel, rel)
            assert rel < even_rel_bound, (
                f"order {order} at {wdw} MHz: joint {mu_j[order]:.6g} vs convolution "
                f"{mu_c[order]:.6g}, relative difference {rel:.4f} exceeds "
                f"{even_rel_bound} (F318: the convolution is adequate for the even "
                f"channel)")
        if wdw >= 13.0:
            skew_j_wide.append(mu_j[3] / mu_j[2] ** 1.5)
            skew_c_wide.append(mu_c[3] / mu_c[2] ** 1.5)
    # the odd channel: the joint line's windowed skewness is not a numerical artefact
    # (it is the s0-driven asymmetry the atom-sampled ensemble carries) and it reads
    # substantially larger than the convolution's own residual (its S0-induced skew,
    # measured at the 1e-5 floor here -- see the module docstring)
    for skew_j, skew_c in zip(skew_j_wide, skew_c_wide):
        assert abs(skew_j) > skew_ratio_floor * max(abs(skew_c), 1e-12), (
            f"the joint line's windowed skewness {skew_j:.3g} should read well past the "
            f"convolution's own {skew_c:.3g} at a wide window (F318: the pairing of shift "
            f"and transit costs the odd channel, not the even one)")
    assert max_even_rel < even_rel_bound   # restated: the even channel stayed inside bound


# =============================================================================================
# 2. INJECTION-RECOVERY CLOSURES, noiseless first
# =============================================================================================

def test_fit_condition_noiseless_closure_on_joint_line():
    """fit_condition(model="joint") recovers gamma_coll and sigma_laser injected through
    volume_line.joint_spectrum directly, with no added noise. A small residual (a few per
    cent) is expected and bounded: the injected world and the fitter's own per-condition
    table are independent Monte Carlo draws at DIFFERENT atom counts (the world here at
    20000, the fitter's default table at `linefit.JOINT_N_PATH`), so their difference is
    exactly the quantity a real fit against a perfect world would carry."""
    T_C = 130.0
    gamma_coll_true = 1.2
    sigma_laser_true = 0.6
    s0_true = 0.5
    gamma_hom = GNAT_MHZ + gamma_coll_true

    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    nu = np.linspace(-30.0, 30.0, 2000)
    world = joint_spectrum(S0_mhz=s0_true, gamma_hom_mhz=gamma_hom, beam=beam, T_C=T_C,
                           half_window_m=half_window_m, n_path=20000, seed=1, delta_mhz=nu,
                           sigma_laser_mhz=sigma_laser_true)
    shape = world / world.max()

    freqs, volts = [], []
    for i in range(5):
        a = 1.0 * (1.0 + 0.03 * i)
        freqs.append(nu.copy())
        volts.append(a * shape)

    fit = fit_condition(freqs, volts, T_C=T_C, s0=s0_true, model="joint", joint_n_path=3000)
    assert abs(fit["gamma_coll"] - gamma_coll_true) < 0.10 * gamma_coll_true, fit
    assert abs(fit["sigma_laser"] - sigma_laser_true) < 0.10 * sigma_laser_true, fit
    assert fit["chi2_red"] < 0.05, "a noiseless closure should fit almost exactly"
    assert fit["model"] == "joint"
    # the reported transit_fwhm is the table's own emergent value, never fitted
    assert fit["transit_fitted"] is False
    assert fit["transit_fwhm"] == pytest.approx(transit_fwhm_from_w0(W0_CENTRAL_M, T_C))


def test_fit_condition_noisy_closure_on_joint_line():
    """The same closure with realistic per-point noise: truth covered within the fit's own
    reported error, the noise-ladder discipline's second rung (noiseless, then
    increasingly noisy)."""
    T_C = 130.0
    gamma_coll_true = 1.5
    sigma_laser_true = 0.7
    s0_true = 0.5
    gamma_hom = GNAT_MHZ + gamma_coll_true

    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    nu = np.linspace(-30.0, 30.0, 2000)
    world = joint_spectrum(S0_mhz=s0_true, gamma_hom_mhz=gamma_hom, beam=beam, T_C=T_C,
                           half_window_m=half_window_m, n_path=20000, seed=2, delta_mhz=nu,
                           sigma_laser_mhz=sigma_laser_true)
    shape = world / world.max()

    rng = np.random.default_rng(4)
    freqs, volts = [], []
    for i in range(5):
        a = 1.0 * (1.0 + 0.03 * i)
        clean = a * shape
        v = clean + 0.006 * rng.standard_normal(nu.size)
        freqs.append(nu.copy())
        volts.append(v)

    fit = fit_condition(freqs, volts, T_C=T_C, s0=s0_true, model="joint", joint_n_path=3000)
    assert abs(fit["gamma_coll"] - gamma_coll_true) < 3 * fit["gamma_coll_err"] + 0.1, fit
    assert abs(fit["sigma_laser"] - sigma_laser_true) < 3 * fit["sigma_laser_err"] + 0.15, fit


def test_fit_beta_self_noiseless_closure_on_joint_line():
    """beta.fit_beta_self(model="joint") recovers beta_self and sigma_laser across a
    temperature ladder, injected from volume_line.joint_spectrum at S0=0 (this fit carries
    no shift channel)."""
    beta_true = 0.05
    sigma_laser_true = 0.8
    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    nu = np.linspace(-25.0, 25.0, 1600)

    conds = []
    for T in (70.0, 90.0, 110.0):
        N = density_units(T)
        gamma_hom = GNAT_MHZ + beta_true * N
        world = joint_spectrum(S0_mhz=0.0, gamma_hom_mhz=gamma_hom, beam=beam, T_C=T,
                               half_window_m=half_window_m, n_path=15000, seed=3,
                               delta_mhz=nu, sigma_laser_mhz=sigma_laser_true)
        shape = world / world.max()
        freqs = [nu.copy() for _ in range(4)]
        volts = [shape.copy() for _ in range(4)]
        conds.append({"T_C": T, "N_units": N, "freqs": freqs, "volts": volts, "law": None})

    fit = fit_beta_self(conds, model="joint", joint_n_path=3000)
    assert abs(fit["beta_self"] - beta_true) < 0.10 * beta_true + 0.003, fit
    assert abs(fit["sigma_laser"] - sigma_laser_true) < 0.15 * sigma_laser_true, fit
    assert fit["model"] == "joint"


def test_fit_global_noiseless_closure_on_joint_line():
    """global_fit.fit_global(model="joint") recovers per-isotope beta and per-T sigma_laser
    across peaks and temperatures, injected from volume_line.joint_spectrum at S0=0."""
    beta_true = {85: 0.06, 87: 0.03}
    sigma_by_T = {70.0: 0.9, 90.0: 1.1, 110.0: 0.8}
    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    nu = np.linspace(-25.0, 25.0, 1400)

    blocks = []
    for peak, iso in (("4207", 87), ("4192", 85)):
        for T in (70.0, 90.0, 110.0):
            N = density_units(T)
            gc = beta_true[iso] * N
            sl = sigma_by_T[T]
            gamma_hom = GNAT_MHZ + gc
            world = joint_spectrum(S0_mhz=0.0, gamma_hom_mhz=gamma_hom, beam=beam, T_C=T,
                                   half_window_m=half_window_m, n_path=12000, seed=5,
                                   delta_mhz=nu, sigma_laser_mhz=sl)
            shape = world / world.max()
            freqs = [nu.copy() for _ in range(3)]
            volts = [shape.copy() for _ in range(3)]
            blocks.append({"peak": peak, "isotope": iso, "T_C": T, "N_units": N,
                           "freqs": freqs, "volts": volts, "law": None})

    fit = fit_global(blocks, model="joint", joint_n_path=3000)
    for iso in (85, 87):
        assert abs(fit["beta_by_isotope"][iso] - beta_true[iso]) < 0.10 * beta_true[iso] + 0.004, \
            fit["beta_by_isotope"]
    assert fit["beta_by_isotope"][85] > fit["beta_by_isotope"][87]
    assert fit["model"] == "joint"


def test_forecast_synthetic_traces_round_trips_with_fit_condition():
    """forecast.synthetic_traces(model="joint") paired with fit_condition(model="joint")
    (the twin/fitter pairing the brief's item 2 names): the twin's own world generator,
    round-tripped through the public forecast API instead of volume_line directly.

    A MODEST NOISE LEVEL, not the strictly noiseless case: gamma_coll and sigma_laser are
    strongly anti-correlated here (this module's own docstring, `linefit.py`'s "the
    fit-level face of the confound"), so a truly noiseless trace lets the optimiser sit
    anywhere along the near-flat degenerate ridge with an equally perfect chi2_red -- which
    a first attempt at this test hit directly (chi2_red 0.0012, sigma_laser 39 per cent off
    truth with corr_laser_coll -0.94). Recovery is checked against the fit's OWN reported
    error, the standard reading for a degenerate pair (every other closure in this
    repository that carries this degeneracy uses noisy data for exactly this reason)."""
    T_C = 120.0
    gamma_coll_true = 1.0
    sigma_laser_true = 0.5
    s0_true = 0.4
    f, v = synthetic_traces(gamma_coll_true, sigma_laser_true, transit_fwhm=float("nan"),
                            n_traces=5, n_points=1800, noise=0.006, s0=s0_true, model="joint",
                            T_C=T_C, n_path=16000, seed=9,
                            rng=np.random.default_rng(9), registry=_TWIN_STUDY)
    fit = fit_condition(f, v, T_C=T_C, s0=s0_true, model="joint", joint_n_path=4000)
    assert abs(fit["gamma_coll"] - gamma_coll_true) < 3 * fit["gamma_coll_err"] + 0.1, fit
    assert abs(fit["sigma_laser"] - sigma_laser_true) < 3 * fit["sigma_laser_err"] + 0.1, fit
    assert fit["corr_laser_coll"] < -0.3, (
        "the degeneracy this test's own docstring names should still be visible", fit)


# =============================================================================================
# WIRING: the two thin wrappers, checked at the call (test_lever_crosscheck_kernel_axis.py's
# own convention), not by re-running their much more expensive closures under a second model
# =============================================================================================

def test_lever_crosscheck_beta_threads_model_to_every_fit_global_call(monkeypatch):
    from rb5s6s import lever_crosscheck as LC

    seen = []

    def _spy(blocks, **kw):
        seen.append(kw.get("model"))
        return {"beta_by_isotope": {85: 0.0, 87: 0.0}, "beta_err_by_isotope": {85: 1.0, 87: 1.0},
               "chi2_red": 1.0, "chi2_whitened": 1.0, "sig_keys": [], "beta_keys": [85, 87],
               "sigma_laser_by_T": {}, "params_at_bound": [], "n_traces": 0}

    monkeypatch.setattr(LC, "fit_global", _spy)
    LC.lever_crosscheck_beta([{"isotope": 85, "peak": "P", "T_C": 90.0}], model="convolution",
                             do_w0_band=True, do_loo=False)
    assert seen, "lever_crosscheck_beta made no fit_global calls to check"
    assert all(m == "convolution" for m in seen), (
        f"lever_crosscheck_beta did not thread model='convolution' to every fit_global "
        f"call: saw {seen}")


def test_sharing_bic_threads_model_to_both_fit_global_calls(monkeypatch):
    from rb5s6s import sharing_bic as SB

    seen = []

    def _spy(blocks, **kw):
        seen.append(kw.get("model"))
        return {"nparams": 1, "ndata": 10, "ndata_eff": 10.0, "chi2_red": 1.0,
               "chi2_whitened": 1.0, "sig_keys": []}

    monkeypatch.setattr(SB, "fit_global", _spy)
    SB.sharing_bic([], transit_ref_mhz=0.9, model="convolution")
    assert seen == ["convolution", "convolution"], (
        f"sharing_bic did not thread model='convolution' to both fit_global calls: {seen}")


# =============================================================================================
# 4. THE LEVER CROSSCHECK'S REPLACEMENT AXES (C6b noise wave, 2026-09-22, brief
#    `private/cache/plan_2026-09-18/briefs_2026-09-22/c6b_noise_brief.md`, task (b)). Under
#    model="joint" the GRID_CELLS transit-kind axis reads exactly 0.0 (the transit is the
#    table's emergent width, not a kernel choice), so `err_transit` no longer measures
#    anything and the two axes the joint line still carries take its place: the waist inside
#    the calculated band (`constants.W0_BAND_M`, now driving `w0_m` itself under
#    model="joint" instead of the dead `transit_ref_mhz` scan `fit_global`'s joint branch
#    never reads) and the beam's clipping (GaussianBeam against `beam_field.ClippedBeam`,
#    opt-in via `lever_crosscheck.lever_crosscheck_beta`'s new `beam_factory` keyword).
# =============================================================================================

def _lever_blocks_joint(T_values=(70.0, 110.0), n_path=1500, n_points=900, span_mhz=30.0):
    """A minimal (peak, isotope, T) block set for `lever_crosscheck_beta`/`fit_global` under
    model="joint": one peak/isotope, `T_values` temperatures, injected noiseless from
    `volume_line.joint_spectrum` directly (this file's own
    `test_fit_global_noiseless_closure_on_joint_line` pattern), small enough (n_path,
    n_points, 2 repeats) to keep a multi-cell lever cross-check closure fast."""
    beta_true = 0.05
    sigma_laser_true = 0.7
    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    nu = np.linspace(-span_mhz, span_mhz, n_points)
    blocks = []
    for T in T_values:
        N = density_units(T)
        gamma_hom = GNAT_MHZ + beta_true * N
        world = joint_spectrum(S0_mhz=0.0, gamma_hom_mhz=gamma_hom, beam=beam, T_C=T,
                               half_window_m=half_window_m, n_path=n_path, seed=71,
                               delta_mhz=nu, sigma_laser_mhz=sigma_laser_true)
        shape = world / world.max()
        freqs = [nu.copy() for _ in range(2)]
        volts = [shape.copy() for _ in range(2)]
        blocks.append({"peak": "P", "isotope": 85, "T_C": T, "N_units": N,
                       "freqs": freqs, "volts": volts, "law": None})
    return blocks


@pytest.mark.slow
def test_lever_crosscheck_w0_band_axis_scans_the_waist_under_joint():
    """`lever_crosscheck_beta(model="joint")`'s w0_band: FIXED (task (b)) to scan `w0_m` itself
    over `constants.W0_BAND_M` instead of the dead `transit_ref_mhz` (never read by
    `fit_global`'s model="joint" branch, so the old scan returned a degenerate, zero-width
    band under joint). This asserts what is MEASURED: the band is genuinely non-degenerate,
    and `err_transit` -- the axis this replaces -- reads exactly the documented zero,
    confirming that reading still holds instead of silently becoming something else."""
    from rb5s6s.lever_crosscheck import lever_crosscheck_beta
    blocks = _lever_blocks_joint()
    out = lever_crosscheck_beta(blocks, model="joint", do_w0_band=True, do_loo=False)
    assert out["err_transit"][85] == 0.0, (
        "the transit-kind axis should still read exactly zero under model='joint'")
    lo, hi = out["w0_band"][85]
    spread = hi - lo
    assert spread > 1e-6, (
        f"the waist band should be measurably non-degenerate now it scans w0_m itself: "
        f"lo={lo}, hi={hi}, spread={spread:.3e}")
    print(f"\n  [C6b noise, task (b)] w0-band axis (85Rb), w0_m spanning {W0_BAND_M}: "
         f"beta lo={lo:.6f}, hi={hi:.6f}, spread={spread:.6f}")


@pytest.mark.slow
def test_lever_crosscheck_beam_clip_axis_under_joint():
    """The second replacement axis: `_fit` (hence `lever_crosscheck_beta`) with a
    `beam_field.ClippedBeam`-based `beam_factory` against the default `GaussianBeam`, at the
    SAME w0_m/T/blocks. The "hoped" case (opt-out means zero) is checked FIRST, not assumed.
    The measured size is then read and reported, not asserted to any particular value, per the
    brief's own instruction."""
    from rb5s6s.config import TRANSIT_FWHM_PLACEHOLDER_MHZ
    from rb5s6s.lever_crosscheck import PRIMARY, _fit, lever_crosscheck_beta
    blocks = _lever_blocks_joint()

    out_default = lever_crosscheck_beta(blocks, model="joint", do_w0_band=False, do_loo=False)
    assert out_default["err_beam_clip"][85] == 0.0, (
        "without a beam_factory the new axis should read exactly zero, not an assumed size")
    assert out_default["beam_clip_beta"] is None

    clipped = beam_field.ClippedBeam(w_in_m=2.46e-3, n_z=21, n_xi=140, n_rho=500, z_span_zr=3.0)

    def clipped_factory(w0v, _b=clipped):
        return _b

    base = _fit(blocks, *PRIMARY, TRANSIT_FWHM_PLACEHOLDER_MHZ, 110.0, model="joint",
               w0_m=W0_CENTRAL_M)
    clip = _fit(blocks, *PRIMARY, TRANSIT_FWHM_PLACEHOLDER_MHZ, 110.0, model="joint",
               w0_m=W0_CENTRAL_M, beam_factory=clipped_factory)
    size = abs(base["beta_by_isotope"][85] - clip["beta_by_isotope"][85])
    assert np.isfinite(size) and size >= 0.0
    print(f"\n  [C6b noise, task (b)] beam-clip axis (85Rb) at w0_m={W0_CENTRAL_M}: "
         f"default beta={base['beta_by_isotope'][85]:.6f}, ClippedBeam beta="
         f"{clip['beta_by_isotope'][85]:.6f}, size={size:.6f}")


# =============================================================================================
# 3. THE SHARED NOISE LAYER (C6b noise wave, 2026-09-22, brief
#    `private/cache/plan_2026-09-18/briefs_2026-09-22/c6b_noise_brief.md`, task (a)). Noise is
#    added AFTER the clean line exists and does not depend on the model form, so
#    `model="joint"` traces now go through `forecast._traces_from_shape`, the SAME helper the
#    convolution branch calls, instead of `twin_volume.synthetic_traces`'s own separate,
#    i.i.d.-only noise loop. The three refusals (`tau_int`, `residual_source`, non-zero
#    `halo_fraction`) are gone: this section is what replaces them.
# =============================================================================================

def _integrated_time_c6b(x, lags=30):
    """The same reading `tests/test_twin_noise_correlation.py::_integrated_time` takes."""
    ac = [float(np.corrcoef(x[:-k], x[k:])[0, 1]) for k in range(1, lags + 1)]
    return 1.0 + 2.0 * sum(ac)


def _block_resample_c6b(pool, n, rng, block=16):
    """The moving-block bootstrap `scripts/run_residual_resampling.py::block_resample` and
    `scripts/run_window_surface.py::_pool_source` both use, BLOCK=16 (the residual seam's own
    block size): keeps the pool's marginal SHAPE exactly and the correlation out to one block."""
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, len(pool) - block, size=nb)
    out = np.concatenate([pool[s:s + block] for s in starts])[:n]
    return out / max(float(np.std(pool)), 1e-300)


def test_noise_off_gives_identical_deterministic_lines_on_both_branches():
    """With noise off, the shared helper's `0.0 * a * _w` term contributes nothing, whatever the
    rng draws: two calls at DIFFERENT rng states agree exactly, on EITHER model (a bug that let
    any randomness leak through when noise=0.0 would show up here). And the joint branch's own
    noise-free line matches `twin_volume.synthetic_traces` (the simpler, still-unchanged sibling
    both now build on `twin_volume.world_shape`) byte for byte, confirming the refactor moved the
    noise-ADDING code without moving the clean line it is added to."""
    common = dict(n_traces=3, n_points=600, span_mhz=40.0, noise=0.0, amp=1.0,
                 amp_spread=0.05, offset=0.01, offset_spread=0.002)
    for model in ("joint", "convolution"):
        kw = dict(common, model=model)
        if model == "joint":
            kw.update(s0=0.3, T_C=115.0, n_path=1500, seed=7)
        f1, v1 = synthetic_traces(1.1, 0.6, 0.9575, rng=np.random.default_rng(1), **kw, registry=_TWIN_STUDY)
        f2, v2 = synthetic_traces(1.1, 0.6, 0.9575, rng=np.random.default_rng(999), **kw, registry=_TWIN_STUDY)
        for a1, a2 in zip(v1, v2):
            assert np.array_equal(a1, a2), (
                f"model={model!r}: noise=0.0 should be exactly independent of the rng draw")

    beam = GaussianBeam(W0_CENTRAL_M, 1.0)
    f_direct, v_direct = tv.synthetic_traces(
        beam=beam, T_C=115.0, S0_mhz=0.3, gamma_hom_mhz=GNAT_MHZ + 1.1, sigma_laser_mhz=0.6,
        span_mhz=40.0, n_points=600, n_traces=3, noise=0.0, amp=1.0, amp_spread=0.05,
        offset=0.01, offset_spread=0.002, n_path=1500, seed=7, rng=np.random.default_rng(1), registry=_TWIN_STUDY)
    f_forecast, v_forecast = synthetic_traces(
        1.1, 0.6, 0.9575, s0=0.3, T_C=115.0, n_path=1500, seed=7, model="joint",
        n_traces=3, n_points=600, span_mhz=40.0, noise=0.0, amp=1.0, amp_spread=0.05,
        offset=0.01, offset_spread=0.002, rng=np.random.default_rng(1), registry=_TWIN_STUDY)
    for a, b in zip(v_direct, v_forecast):
        assert np.array_equal(a, b), (
            "forecast.synthetic_traces(model='joint', noise=0.0) should match "
            "twin_volume.synthetic_traces exactly: both now build on world_shape")


def test_shared_noise_layer_reproduces_the_laws_integrated_time_directly():
    """`_traces_from_shape` is the ONE noise layer both `model=` branches of `synthetic_traces`
    now call: this is `tests/test_twin_noise_correlation.py`'s own
    `test_the_marginal_sigma_survives_and_the_integrated_time_is_hit` reading, taken of the
    SHARED helper directly (not of `_correlate` alone, which that file already covers)
    on a zero clean line, so the injected noise is read with nothing else in it."""
    n = 20000
    nu = np.linspace(-1.0, 1.0, n)
    shape = np.zeros(n)
    for tau in (1.0, 2.515, 5.0):
        f, v = _traces_from_shape(nu, shape, n_traces=1, noise=1.0, amp=1.0, amp_spread=0.0,
                                  offset=0.0, offset_spread=0.0, halo_fraction=0.0,
                                  tau_int=tau, residual_source=None,
                                  rng=np.random.default_rng(31))
        tau_meas = _integrated_time_c6b(v[0])
        assert tau_meas == pytest.approx(tau, rel=0.10), (
            f"tau_int={tau}: measured integrated time {tau_meas:.3f}")


def test_correlated_noise_under_the_joint_branch_reproduces_the_laws_integrated_time():
    """The public entry point, `model='joint'`: the committed law drives the twin without being
    asked, `tests/test_twin_noise_correlation.py::test_the_committed_law_drives_the_twin_without_
    being_asked`'s own reading, now under the model that test's own docstring names as out of
    `twin_volume`'s scope by construction -- the C6b wide wave's own refusal, lifted here."""
    law = load_noise_model("results/noise_model.csv", role="p_sweep", pool="median")
    assert law["tau_int"] > 1.0, "the committed law must carry a correlation"
    kw = dict(s0=0.0, T_C=115.0, n_path=1500, seed=13, n_traces=1, n_points=4000, model="joint")
    _, v_law = synthetic_traces(0.55, 1.6, 0.9575, noise=law, rng=np.random.default_rng(11), **kw, registry=_TWIN_STUDY)
    _, v_white = synthetic_traces(0.55, 1.6, 0.9575, noise=dict(law, tau_int=1.0),
                                  rng=np.random.default_rng(11), **kw, registry=_TWIN_STUDY)
    assert not np.array_equal(v_law[0], v_white[0]), (
        "model='joint' should carry the law's own tau_int now, exactly as model='convolution' "
        "already does")


def test_halo_fraction_under_the_joint_branch_raises_the_amplitude():
    """The third of the three previously-refused keywords: a flat, model-independent amplitude
    factor (module docstring: it does not reshape the line, the trapped photon's frequency is
    unrelated to the two-photon detuning)."""
    kw = dict(s0=0.0, T_C=115.0, n_path=1500, seed=5, n_traces=1, n_points=400, span_mhz=40.0,
             noise=0.0, amp_spread=0.0, offset_spread=0.0, offset=0.0, model="joint")
    f0, v0 = synthetic_traces(1.0, 0.5, float("nan"), halo_fraction=0.0,
                              rng=np.random.default_rng(0), **kw, registry=_TWIN_STUDY)
    f1, v1 = synthetic_traces(1.0, 0.5, float("nan"), halo_fraction=0.25,
                              rng=np.random.default_rng(0), **kw, registry=_TWIN_STUDY)
    ratio = float(np.max(v1[0]) / np.max(v0[0]))
    assert ratio == pytest.approx(1.25, rel=1e-9), f"halo_fraction=0.25 should scale the peak by 1.25x, got {ratio}"


def test_residual_seam_under_the_joint_branch_reproduces_the_pools_statistics():
    """The archive-shaped residual draw (`residual_source`, the moving-block resamples of
    `scripts/run_residual_resampling.py`, BLOCK=16) reaches a `model='joint'` trace's noise
    exactly as it reaches a `model='convolution'` one. With a FLOAT `noise` and no per-trace
    amplitude/offset spread, `v[1] - v[0]` cancels the clean line whatever it is (both traces
    share it exactly), leaving pure noise: the pool's own heavy tail then shows up in that
    difference's excess kurtosis, read IDENTICALLY under either model (same `rng`/
    `residual_source` sequence, same scalar amplitude, no clean line left to differ by), and
    both well above a Gaussian control read the same differencing way."""
    rng_pool = np.random.default_rng(20260922)
    pool = rng_pool.standard_t(11.3, 40000) / np.sqrt(11.3 / (11.3 - 2.0))  # excess kurtosis ~0.82-0.89
    pool_kurt = float(stats.kurtosis(pool, fisher=True, bias=False))
    assert pool_kurt > 0.5, "the pool itself should carry the heavy tail this test measures"

    def src(rng, n, _pool=pool):
        return _block_resample_c6b(_pool, n, rng, block=16)

    common = dict(n_traces=2, n_points=12000, span_mhz=40.0, noise=0.05, amp=1.0,
                 amp_spread=0.0, offset=0.01, offset_spread=0.0, residual_source=src)
    kurt_by_model = {}
    for model in ("joint", "convolution"):
        kw = dict(common, model=model)
        if model == "joint":
            kw.update(s0=0.0, T_C=115.0, n_path=1500, seed=17)
        f, v = synthetic_traces(0.8, 0.5, 0.9575, rng=np.random.default_rng(41), **kw, registry=_TWIN_STUDY)
        diff = v[1] - v[0]
        kurt_by_model[model] = float(stats.kurtosis(diff, fisher=True, bias=False))

    kw_g = dict(common, model="joint", s0=0.0, T_C=115.0, n_path=1500, seed=17,
               residual_source=None)
    f, v = synthetic_traces(0.8, 0.5, 0.9575, rng=np.random.default_rng(41), **kw_g, registry=_TWIN_STUDY)
    kurt_gaussian = float(stats.kurtosis(v[1] - v[0], fisher=True, bias=False))

    assert kurt_by_model["joint"] > 3.0 * max(kurt_gaussian, 0.05), kurt_by_model
    assert kurt_by_model["convolution"] > 3.0 * max(kurt_gaussian, 0.05), kurt_by_model
    # a float `noise` and no per-trace spread make the noise component independent of `shape`,
    # so the two models' readings are not merely close, they are the SAME draw: exact equality
    # is the sharpest statement that this is one shared code path and not two.
    assert kurt_by_model["joint"] == kurt_by_model["convolution"], (
        f"the joint branch's residual-seam reading should equal the convolution branch's "
        f"exactly (one shared helper, the same rng draw): {kurt_by_model}")
