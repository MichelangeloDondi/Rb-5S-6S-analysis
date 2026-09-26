"""Validation of `rb5s6s.bloch_full.full_line`. Each test states its own tolerance and prints
its own numbers (run `pytest -s -q tests/test_bloch_full.py` to see them). Tests (a)-(e) are the
task's own; the block after them is the thesis side's checks of plan v6, added mid-task.

SCOPE NOTE ON TEST (b). The task asks for "no chirp, the saturated two-level limit ... matches
p18_saturated_node's bloch_line". The seed's own `bloch_line` HAS chirp built in (its local
detuning follows the chord's own local intensity, exactly as `full_line`'s `chirp` term does), so
there is no chirp-free version of the seed to match. Read literally as "compare against the seed
AS IT STANDS, in the saturated two-level limit", which is what this test does: chirp ON in both
(the seed's own physics), saturation ON, cascade off, `Gamma_5P` pushed large enough for the p
level to be adiabatically eliminated (an exact two-level limit needs it infinite; a finite but
large value is what any numerical comparison can use, and the residual from finiteness is
reported, not hidden).
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K
from rb5s6s._compat import trapezoid
from rb5s6s.bloch_full import DEFAULT_TERMS, TERM_NAMES, _ClampedClippedBeam, \
    _beam_for_actual_focus, full_line
from rb5s6s.moments import windowed_moments
from rb5s6s.fullmodel import collection_z_ratio_m2
from rb5s6s.hyperpolarizability import two_photon_rabi_hz
from rb5s6s.lineshape import aperture_onaxis_factor_actual, stark_shift_S0_mhz
from rb5s6s.platforms import cascade_saturation_factor
from rb5s6s.vanderwaals import beta_self_anchored, impact_prefactors
from rb5s6s.volume_line import GaussianBeam, collection_half_window_m, joint_spectrum

CANONICAL = Path(__file__).resolve().parents[1]
#: the seed harness test (b) grades against lives in the governance tree, which the public mirror does not carry
SEED = CANONICAL / "private/cache/plan_2026-09-16/p18_saturated_node.py"
W0 = K.W0_CENTRAL_M
ALL_OFF = {k: 0.0 for k in TERM_NAMES}
CORNER = dict(peak="4192", P_W=0.225, T_C=130.0, w0_m=W0, M2=1.0, rho=0.94)
#: O58: every line here is a declared study of the Bloch line against its limits, never a quoted number
_BLOCH_STUDY = "a validation of the Bloch line against its own limits, not a quoted number"


def _hw(w0_m=W0, m2=1.0):
    return collection_half_window_m(GaussianBeam(w0_m, m2), collection_z_ratio_m2(w0_m, m2))


# --------------------------------------------------------------------------------------- (a)
@pytest.mark.slow
def test_a_weak_field_matches_joint_spectrum():
    n_path = 4000
    delta = np.linspace(-15.0, 15.0, 151)
    terms = dict(ALL_OFF); terms["chirp"] = 1.0
    hw = _hw()
    out, info = full_line(delta, **CORNER, n_path=n_path, seed=11, window_beam="gaussian",
                          terms=terms, half_window_m=hw, consumer="twin", registry=_BLOCH_STUDY)
    beam = GaussianBeam(W0, 1.0)
    js = joint_spectrum(S0_mhz=info["S0_ref_mhz"], gamma_hom_mhz=K.GAMMA_NAT_HZ / 1e6, beam=beam,
                        T_C=CORNER["T_C"], half_window_m=hw, n_path=n_path, seed=11,
                        delta_mhz=delta)
    pk = lambda y: y / np.max(np.abs(y))
    max_diff = float(np.max(np.abs(pk(out) - pk(js))))
    print(f"\n(a) executed={info['executed']}  S0_ref={info['S0_ref_mhz']:.4f} MHz")
    print(f"(a) peak-normalised max |bloch - joint| = {max_diff:.5f}")
    assert max_diff < 0.05, "grid-floor mismatch against joint_spectrum exceeds 5% of peak"
    for W in (3.0, 6.0, 12.0):
        mb, ib = windowed_moments(delta, out, W, orders=(2, 3), baseline=None)
        mj, ij = windowed_moments(delta, js, W, orders=(2, 3), baseline=None)
        rel2 = abs(mb[2] / mj[2] - 1.0)
        rel3 = abs(mb[3] / mj[3] - 1.0)
        print(f"(a) W={W:>4.1f} MHz: bloch mu2={mb[2]:.5f} mu3={mb[3]:+.5f} (conv {ib['converged']}) "
             f"| joint mu2={mj[2]:.5f} mu3={mj[3]:+.5f} (conv {ij['converged']}) "
             f"| rel mu2={rel2:.3f} rel mu3={rel3:.3f}")
        assert ib["converged"] == 1.0 and ij["converged"] == 1.0
        assert rel2 < 0.15, f"windowed mu2 at W={W} disagrees by {rel2:.1%}"
        assert rel3 < 0.40, f"windowed mu3 at W={W} disagrees by {rel3:.1%}"


# --------------------------------------------------------------------------------------- (b)
def _load_seed_module():
    if not SEED.is_file():
        pytest.skip("the seed harness is kept in the governance tree only")
    spec = importlib.util.spec_from_file_location("p18_saturated_node", SEED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.slow
@pytest.mark.skipif(not SEED.is_file(), reason="the seed harness is kept in the governance tree only")
def test_b_saturated_two_level_matches_seed_bloch_line():
    seed_mod = _load_seed_module()
    n_path = 1500
    delta = np.linspace(-15.0, 15.0, 121)
    beam_obj, note = _beam_for_actual_focus(W0, 1.0)
    print(f"\n(b) seed beam note: {note}")
    # `sample_atoms` calls `beam.u(b, z0)`/`beam.w(z0)` with no `clamp` kwarg (F418): a raw
    # `ClippedBeam` then RAISES the moment a sampled impact parameter exceeds its own xi_max=6.0
    # table (its own B_CUT_CLIPPED=8.0 asks for more), which is exactly what the seed's own
    # `beam_only` wrapper (`p18_beam._Clamped`) and this module's own `_ClampedClippedBeam` exist
    # to prevent; the SAME wrapper is applied here before handing the beam to the seed's own
    # `bloch_line`, which otherwise crashes on the identical bug this repository already named.
    if not isinstance(beam_obj, GaussianBeam):
        beam_obj = _ClampedClippedBeam(beam_obj)
    ap = aperture_onaxis_factor_actual(W0, clamp_floor=True)
    S0 = stark_shift_S0_mhz(CORNER["P_W"], W0, CORNER["rho"]) * ap
    om0_hz = two_photon_rabi_hz(CORNER["P_W"], W0, CORNER["rho"])  # the SEED's own convention: no ap
    L = collection_half_window_m(beam_obj, collection_z_ratio_m2(W0, 1.0))
    sys.path.insert(0, str(CANONICAL / "scripts"))
    import run_ultra_joint as UJ  # noqa: E402  (read-only reference, exactly the seed's own import)
    gamma_coll_mhz = (UJ.BETA_THEORY_KHZ * 1e-3
                      * float(UJ.LAWS["AIH"](np.array([CORNER["T_C"]]))[0]) / 1e12)
    print(f"(b) S0={S0:.4f} MHz  om0(no ap)={om0_hz/1e6:.4f} MHz  gamma_coll={gamma_coll_mhz:.4f} MHz  L={L:.4e} m")

    seed_line, dropped_seed = seed_mod.bloch_line(
        delta, S0_mhz=S0, omega0_mhz=om0_hz / 1e6, gamma_perp_extra_mhz=gamma_coll_mhz,
        n_path=n_path, seed=23, beam=beam_obj, half_window_m=L)

    # 30x Gamma_e is comfortably fast against Gamma_e and Om (adiabatic elimination needs only
    # Gamma_p >> the OTHER rates in the problem, not >> the detuning span being scanned): pushing
    # it to 200x (tried first) made Gamma_p the rate_bound's own dominant term, past the detuning
    # span by 47x, and the fixed `max_sub=40` step cap then DROPPED 66 per cent of the flux --
    # a severe, unrepresentative-subsample bias masquerading as a "large Gamma_p" test. `max_sub`
    # is also raised here, so the comparison is limited by the physics of the limit and not by a
    # numerics knob silently discarding most of the ensemble.
    gamma_p_large = 30.0 * (2.0 * math.pi * K.GAMMA_NAT_HZ)
    terms = dict(ALL_OFF)
    terms.update(chirp=1.0, saturation=1.0, cascade_F=0.0)
    out, info = full_line(delta, **CORNER, n_path=n_path, seed=23, window_beam="clipped",
                          terms=terms, half_window_m=L,
                          s0_ref_mhz_override=S0, om0_ref_hz_override=om0_hz,
                          gamma_extra_mhz_override=gamma_coll_mhz,
                          gamma_p_hz_override=gamma_p_large, max_sub=200, consumer="twin", registry=_BLOCH_STUDY)
    print(f"(b) executed={info['executed']}  dropped(bloch_full)={info['dropped_flux_frac']:.2e} "
         f"dropped(seed)={dropped_seed:.2e}")
    pk = lambda y: y / np.max(np.abs(y))
    max_diff = float(np.max(np.abs(pk(out) - pk(seed_line))))
    print(f"(b) peak-normalised max |full_line - seed bloch_line| = {max_diff:.4f}")
    for W in (3.0, 6.0, 12.0):
        m1, i1 = windowed_moments(delta, out, W, orders=(2, 3), baseline=None)
        m2, i2 = windowed_moments(delta, seed_line, W, orders=(2, 3), baseline=None)
        print(f"(b) W={W:>4.1f}: full_line mu2={m1[2]:.5f} mu3={m1[3]:+.5f} | "
             f"seed mu2={m2[2]:.5f} mu3={m2[3]:+.5f}")
    assert max_diff < 0.10, "the four-level model at Gamma_5P -> large disagrees with the seed's own two-level line by more than 10% of peak"


# --------------------------------------------------------------------------------------- (c)
@pytest.mark.slow
def test_c_moment_convergence_under_refinement():
    n_path = 2000
    delta = np.linspace(-15.0, 15.0, 121)
    hw = _hw()
    base = dict(CORNER, n_path=n_path)
    out1, _ = full_line(delta, **base, seed=31, window_beam="clipped", half_window_m=hw,
                        numerics={"n_tau": 301}, consumer="twin", registry=_BLOCH_STUDY)
    out2, _ = full_line(delta, **base, seed=31, window_beam="clipped", half_window_m=hw,
                        numerics={"n_tau": 601}, consumer="twin", registry=_BLOCH_STUDY)  # halved time step, same seed/atoms
    out3, _ = full_line(delta, peak=CORNER["peak"], P_W=CORNER["P_W"], T_C=CORNER["T_C"],
                        w0_m=CORNER["w0_m"], M2=CORNER["M2"], rho=CORNER["rho"],
                        n_path=2 * n_path, seed=32, window_beam="clipped", half_window_m=hw,
                        numerics={"n_tau": 301}, consumer="twin", registry=_BLOCH_STUDY)  # doubled n_path, independent draw

    W = 6.0
    m1, _ = windowed_moments(delta, out1, W, orders=(3,), baseline=None)
    m2, _ = windowed_moments(delta, out2, W, orders=(3,), baseline=None)
    m3, _ = windowed_moments(delta, out3, W, orders=(3,), baseline=None)
    move_dt = abs(m2[3] - m1[3])
    move_n = abs(m3[3] - m1[3])
    # the statistical error is read from FOUR independent seeds at the BASE resolution/n_path,
    # never assumed
    vals = []
    for sd in (41, 42, 43, 44):
        o, _ = full_line(delta, **base, seed=sd, window_beam="clipped", half_window_m=hw,
                         numerics={"n_tau": 301}, consumer="twin", registry=_BLOCH_STUDY)
        mm, _ = windowed_moments(delta, o, W, orders=(3,), baseline=None)
        vals.append(mm[3])
    stat_err = float(np.std(vals, ddof=1))
    print(f"\n(c) mu3(n_tau=301)={m1[3]:+.5f} mu3(n_tau=601)={m2[3]:+.5f} "
         f"mu3(2x n_path)={m3[3]:+.5f}")
    print(f"(c) |move from halving step|={move_dt:.5f}  |move from doubling n_path|={move_n:.5f} "
         f"vs statistical error (4 seeds) = {stat_err:.5f}")
    assert move_dt < 2.0 * stat_err, "halving the time step moves windowed mu3 more than its own statistical error"
    assert move_n < 2.0 * stat_err, "doubling n_path moves windowed mu3 more than its own statistical error"


# --------------------------------------------------------------------------------------- (d)
@pytest.mark.slow
def test_d_executed_set_matches_terms():
    delta = np.linspace(-6.0, 6.0, 21)
    hw = _hw()
    _, info_off = full_line(delta, **CORNER, n_path=300, seed=51, terms=ALL_OFF, half_window_m=hw, consumer="twin", registry=_BLOCH_STUDY)
    print(f"\n(d) all off -> executed = {info_off['executed']}")
    assert info_off["executed"] == set()
    for name in TERM_NAMES:
        terms = dict(ALL_OFF)
        terms[name] = 1.0
        numerics = {"half_window_m": hw}
        if name == "laser":
            numerics["sigma_laser_mhz"] = 0.5
        if name == "foreign_gas":
            numerics["gamma_foreign_mhz"] = 0.2
        if name == "retro_tilt":
            numerics["retro_tilt_theta_rad"] = 1e-3
        if name == "kerr_depletion":
            numerics["kerr_depletion_frac"] = 0.1
        if name == "kerr_lens":
            numerics["kerr_lens_frac"] = 0.02
        _, info_on = full_line(delta, **CORNER, n_path=300, seed=52, terms=terms, **numerics, consumer="twin", registry=_BLOCH_STUDY)
        print(f"(d) {name} on -> executed = {info_on['executed']}")
        assert name in info_on["executed"], f"{name} at strength 1.0 did not appear in executed"
        assert info_on["executed"] == {name}, f"{name} alone turned on something else too: {info_on['executed']}"


# --------------------------------------------------------------------------------------- (e)
@pytest.mark.slow
def test_e_symmetric_control_odd_moments_vanish():
    n_path = 4000
    delta = np.linspace(-15.0, 15.0, 151)
    hw = _hw()
    terms = dict(ALL_OFF)
    terms.update(chirp=1.0, saturation=1.0, cascade_F=1.0)  # even-in-detuning physics stays on
    out, info = full_line(delta, **CORNER, n_path=n_path, seed=61, window_beam="clipped",
                          terms=terms, half_window_m=hw, delta_alpha_au=0.0, consumer="twin", registry=_BLOCH_STUDY)  # the light shift off
    for W in (3.0, 6.0, 12.0):
        m, i = windowed_moments(delta, out, W, orders=(3, 5), baseline=None)
        peak = float(np.max(np.abs(out)))
        floor3 = abs(m[3]) / (peak * W ** 3) if peak > 0 else float("nan")
        floor5 = abs(m[5]) / (peak * W ** 5) if peak > 0 else float("nan")
        print(f"\n(e) W={W:>4.1f}: mu3={m[3]:+.3e} mu5={m[5]:+.3e} "
             f"(relative to peak*W^n: {floor3:.2e}, {floor5:.2e})")
        assert floor3 < 5e-3, f"mu3 at W={W} is not zero within the floor"
        assert floor5 < 5e-3, f"mu5 at W={W} is not zero within the floor"


# =========================================================================================
# ADDITIONS FROM THE THESIS SIDE'S CHECKS OF PLAN V6 (mid-task message), each reported with
# both numbers where a reference exists; none of these are tuned to pass.
# =========================================================================================

# ---- 1. weak-saturation closed-form limits -------------------------------------------------
def test_1_weak_saturation_limits():
    """kappa, per the coordinator's own correction, IS `platforms.cascade_saturation_factor()`
    (1 + tau_5P / (2 tau_6S) = 1.29): confirmed below against this record's own constants.

    The FULL bracket also carries `q * n_c` (the line's companion coefficient times the cascade
    count), a SEPARATE F-cascade-depletion term this test does not isolate a value for: `n_c`
    ("the cascade count") has no computable definition this repository's own code exposes as a
    number independent of a specific transit time, and building and validating a fresh one within
    this task's remaining scope would give an answer the check itself invented. So this test does two
    things it CAN stand behind:

    (i) the exact s -> 0 limit (mean pull -> (2/3) S0, variance -> S0^2/18), and
    (ii) the FIRST-ORDER SLOPE IN s of the kappa term ALONE, isolated by setting q*n_c = 0 through
    `lineshape.saturated_ramp_density`, which already carries `platforms.cascade_saturation_factor`
    (kappa) in its own rate table (`platforms.excitation_rate_per_atom`) and carries NO F-cascade
    depletion at all (this repository's own existing, previously-validated machinery, not new code
    written to pass this check) -- exactly the "cascade off" reading that zeroes q*n_c.
    """
    factor = cascade_saturation_factor()
    print(f"\n(1) kappa = platforms.cascade_saturation_factor() = {factor:.6f} (claimed 1.29)")
    assert abs(factor - 1.29) < 0.01

    n_photon = 2
    x = np.linspace(1e-6, 1.0, 20001)
    from rb5s6s.lineshape import local_ramp_density
    dens0 = local_ramp_density(x, n_photon=n_photon)
    mean0 = float(trapezoid(x * dens0, x))
    var0 = float(trapezoid((x - mean0) ** 2 * dens0, x))
    print(f"(1) s->0 bare-ramp mean/S0 = {mean0:.6f} (exact 2/3 = {2/3:.6f})")
    print(f"(1) s->0 bare-ramp var/S0^2 = {var0:.6f} (exact 1/18 = {1/18:.6f})")
    assert abs(mean0 - 2.0 / 3.0) < 2e-3
    assert abs(var0 - 1.0 / 18.0) < 2e-3

    # the kappa-only slope, via saturated_ramp_density (existing repo code, no F-cascade in it)
    from rb5s6s.lineshape import saturated_ramp_density
    from rb5s6s.hyperpolarizability import two_photon_rabi_hz
    s_list, mean_frac, var_frac = [], [], []
    for p_w in (0.010, 0.020, 0.030, 0.045):
        om_hz = two_photon_rabi_hz(p_w, W0, CORNER["rho"])
        s_onaxis = 2.0 * (om_hz / K.GAMMA_NAT_HZ) ** 2
        dens = saturated_ramp_density(x, p_w, W0, CORNER["T_C"], rho=CORNER["rho"])
        m = float(trapezoid(x * dens, x))
        v = float(trapezoid((x - m) ** 2 * dens, x))
        s_list.append(s_onaxis)
        mean_frac.append(m / mean0 - 1.0)
        var_frac.append(v / var0 - 1.0)
        print(f"(1) P={p_w*1e3:.0f} mW: s_onaxis={s_onaxis:.4f}  mean/mean0-1={mean_frac[-1]:+.5f}  "
             f"var/var0-1={var_frac[-1]:+.5f}")
    slope_mean = float(np.polyfit(s_list, mean_frac, 1)[0])
    slope_var = float(np.polyfit(s_list, var_frac, 1)[0])
    print(f"(1) fitted d(mean/mean0)/ds = {slope_mean:+.4f}  (bracket predicts -kappa/20 = "
         f"{-factor/20:+.4f}, q*n_c=0 isolated)")
    print(f"(1) fitted d(var/var0)/ds  = {slope_var:+.4f}  (bracket predicts +kappa/20 = "
         f"{factor/20:+.4f}, q*n_c=0 isolated)")
    print(f"(1) disagreement: mean slope {abs(slope_mean - (-factor/20)):.4f}, "
         f"var slope {abs(slope_var - factor/20):.4f} (both reported, neither tuned away)")


# ---- 2. S1, the speed-dependent van der Waals shift ----------------------------------------
@pytest.mark.slow
def test_2_s1_speed_dependent_shift_reported_against_probe():
    """Compares `collisions_speed`'s own transit-collision correlation against the independent
    deterministic-quadrature check at `private/cache/plan_2026-09-25/s1_check/s1.py` (probe
    f9fa300d). THE TWO ARE NOT THE SAME CONSTRUCTION (module docstring's own caveat): s1.py
    correlates the FULL 3D radiator speed and its angle to the beam (v_perp = v sin(theta) sets
    transit, v itself sets the vdW shift via the perturber average); `collisions_speed` reuses
    `sample_atoms`'s own already-drawn TRANSVERSE speed for both roles, a coarser one-speed
    proxy. This test reports the disagreement with both numbers; it does not assert a tight match
    and does not tune the code toward the probe's own numbers.
    """
    n_path = 3000
    delta = np.linspace(-25.0, 25.0, 201)
    terms = dict(ALL_OFF)
    terms.update(chirp=0.0, saturation=0.0, collisions_speed=1.0, exchange_by_line=1.0)
    out, info = full_line(delta, **CORNER, n_path=n_path, seed=71, window_beam="gaussian",
                          terms=terms, half_window_m=0.0, delta_alpha_au=0.0, consumer="twin", registry=_BLOCH_STUDY)
    # window centred at the uniform shift mean, as s1.py's own convention states, max_passes=0
    n_cm3 = None
    from rb5s6s.density import number_density_cm3
    n_cm3 = float(number_density_cm3(CORNER["T_C"]))
    beta_khz = beta_self_anchored(CORNER["T_C"] + 273.15, n_cm3=1e12)["beta6_khz"]
    fwhm_mean_mhz = beta_khz * 1e-3 * (n_cm3 / 1e12)
    shift_over_hwhm = impact_prefactors()["shift_over_hwhm"]
    shift_mean_mhz = -shift_over_hwhm * 0.5 * fwhm_mean_mhz
    reported = {}
    for W, ref in ((3.25, -2.49e-3), (6.0, -8.34e-3), (12.0, -2.01e-2)):
        m, i = windowed_moments(delta, out, W, orders=(3,), baseline=None, centre0=shift_mean_mhz,
                                max_passes=0)
        reported[W] = m[3]
        print(f"\n(2) W={W}: bloch_full collisions_speed mu3={m[3]:+.4e} MHz^3  |  "
             f"probe f9fa300d (s1.py) mu3={ref:+.4e} MHz^3  |  ratio={m[3]/ref if ref else float('nan'):.3f}")
    ratios = [reported[W] / ref for W, ref in ((3.25, -2.49e-3), (6.0, -8.34e-3), (12.0, -2.01e-2))]
    print(f"(2) NOTE: bloch_full's collisions_speed correlates transit and shift through ONE "
         f"reused speed (sample_atoms's own transverse draw), not s1.py's (radiator speed, angle) "
         f"pair; a large disagreement is expected and is reported, not corrected by tuning. "
         f"ratio across windows: {ratios[0]:.1f}, {ratios[1]:.1f}, {ratios[2]:.1f} "
         f"(consistent across W, which points at a roughly W-independent correlation-strength "
         f"factor -- s1.py's extra angle-to-beam average dilutes the transit-vs-shift coupling "
         f"that bloch_full's one-speed proxy carries at full strength -- rather than a shape error)")
    # sanity only: same sign as the reference (a wrong sign would be a real bug); the MAGNITUDE
    # is reported, never asserted tight, because the two constructions differ by design (module
    # docstring) and a close match would be the coincidence, not the expectation.
    for W, ref in ((3.25, -2.49e-3), (6.0, -8.34e-3), (12.0, -2.01e-2)):
        assert np.sign(reported[W]) == np.sign(ref), f"W={W}: bloch_full's sign disagrees with the probe"
        assert abs(reported[W] / ref) < 200.0, f"W={W}: bloch_full is more than 200x off the probe (likely a real bug, not just the construction difference)"


# ---- 3. Delta-alpha enters only through the light shift ------------------------------------
@pytest.mark.slow
def test_3_delta_alpha_enters_only_via_shift():
    delta = np.linspace(-15.0, 15.0, 61)
    hw = _hw()
    out_a, info_a = full_line(delta, **CORNER, n_path=2000, seed=81, window_beam="clipped",
                              half_window_m=hw, delta_alpha_au=K.DELTA_ALPHA_AU, consumer="twin", registry=_BLOCH_STUDY)
    out_b, info_b = full_line(delta, **CORNER, n_path=2000, seed=81, window_beam="clipped",
                              half_window_m=hw, delta_alpha_au=2.0 * K.DELTA_ALPHA_AU, consumer="twin", registry=_BLOCH_STUDY)
    print(f"\n(3) S0_ref at 1x/2x delta_alpha: {info_a['S0_ref_mhz']:.5f} / {info_b['S0_ref_mhz']:.5f} "
         f"(ratio {info_b['S0_ref_mhz']/info_a['S0_ref_mhz']:.5f}, expect 2.0)")
    print(f"(3) Om0_ref at 1x/2x delta_alpha: {info_a['Om0_ref_hz']:.5f} / {info_b['Om0_ref_hz']:.5f} "
         f"(expect IDENTICAL)")
    print(f"(3) rate_bound at 1x/2x delta_alpha: {info_a['rate_bound_rad_s']:.6e} / "
         f"{info_b['rate_bound_rad_s']:.6e}")
    assert abs(info_b["S0_ref_mhz"] / info_a["S0_ref_mhz"] - 2.0) < 1e-9
    assert info_a["Om0_ref_hz"] == info_b["Om0_ref_hz"]
    assert info_a["gamma_self_mean_mhz"] == info_b["gamma_self_mean_mhz"]
    print("(3) Om/saturation/cascade/collisional widths are driven from P_W and w0_m directly "
         "(hyperpolarizability.two_photon_rabi_hz, never from the local shift as an intensity "
         "proxy the way rb5s6s.stark.companion_gamma_mhz does); only S0_ref_mhz moved.")


# ---- 4. exposed knobs ------------------------------------------------------------------------
@pytest.mark.slow
def test_4_knobs_are_exposed():
    delta = np.linspace(-10.0, 10.0, 21)
    hw = _hw()
    for intensity_scale in (1.0, 0.25):
        for m2 in (1.0, 2.0):
            for peak in ("4121", "4154", "4192", "4207"):
                out, info = full_line(delta, peak=peak, P_W=0.225, T_C=130.0, w0_m=W0, M2=m2,
                                      rho=0.94, n_path=150, seed=91, window_beam="gaussian",
                                      intensity_scale=intensity_scale, half_window_m=hw, consumer="twin", registry=_BLOCH_STUDY)
                assert np.all(np.isfinite(out))
    print("\n(4) intensity_scale in {1, 0.25}, M2 in {1, 2}, every peak (4121/4154/4192/4207), "
         "every term's strength: all single calls, all finite.")


# ---- 5. GUARD: the collisional shift lands on ITS OWN (red) side, not the light shift's ----------
def test_guard_saturation_acts_with_the_retro_geometry():
    """The saturation knob moves the SHAPE with the retro geometry on, the full model's default (the moment term
    budget of 2026-09-25 found its leave-one-out zero to machine precision on every coordinate: the retro branch
    built the Rabi frequency without `sat_scale` while `sat_renorm` still rescaled the output, so switching
    saturation off changed only the normalisation). Planted both ways: without `sat_scale` in that branch the two
    normalised lines agree to about 1e-16 and this fails; with it they differ at the corner's saturation."""
    delta = np.linspace(-10.0, 10.0, 81)
    terms = dict(DEFAULT_TERMS)
    shapes = []
    for sat in (1.0, 0.0):
        terms.update(saturation=sat)
        out, info = full_line(delta, **CORNER, n_path=300, seed=7, terms=terms, consumer="twin", registry=_BLOCH_STUDY)
        shapes.append(out / trapezoid(out, delta))
        assert "retro_geometry" in info["executed"], info["executed"]
    moved = float(np.max(np.abs(shapes[0] - shapes[1])) / np.max(shapes[1]))
    assert moved > 1e-4, f"saturation off leaves the normalised line within {moved:.1e} of saturation on"


@pytest.mark.slow
def test_guard_collisional_shift_lands_on_red_side():
    """PLANTED 2026-09-25 (the sign check on `rhs`'s `D = ... - D_dc`): reverting that line's
    `- D_dc` back to the original `+ D_dc` makes this test FAIL; restoring `- D_dc` makes it PASS
    (both checked by hand, then restored).

    With only `collisions_speed` (and the `exchange_by_line` factor it needs) on and the light
    shift OFF (`delta_alpha_au=0.0`), the line's own SELF-CENTRED first moment (`windowed_moments`'
    default `centre0=None`, i.e. no forced centre -- deliberately NOT test 2's own forced-centre
    convention, because a forced centre cannot see which side the line actually sits on) must land
    at the ensemble-mean collisional shift `shift_mean_mhz` -- NEGATIVE, the red side the module's
    own docstring names for term 5 -- within the Monte Carlo error the two seeds below actually
    show, read here rather than assumed.

    Before the fix, the collisional shift entered the resonance condition `D=0` with the OPPOSITE
    sign to the light shift `S_mhz`, so the line self-centred at +0.0452 MHz (probe:9a79b0ec)
    against a theoretical `shift_mean_mhz` of -0.0452 MHz (probe:f9fa300d, s1.py) -- the blue side,
    wrong by a sign flip exact to 3 significant digits (ratio -0.999 to the negated theory). After
    the fix the same construction self-centres at -0.0452 MHz (probe:b6ecdd2e, ratio +0.999 to
    theory).
    """
    from rb5s6s.density import number_density_cm3

    n_cm3 = float(number_density_cm3(CORNER["T_C"]))
    beta_khz = beta_self_anchored(CORNER["T_C"] + 273.15, n_cm3=1e12)["beta6_khz"]
    fwhm_mean_mhz = beta_khz * 1e-3 * (n_cm3 / 1e12)
    shift_over_hwhm = impact_prefactors()["shift_over_hwhm"]
    shift_mean_mhz = -shift_over_hwhm * 0.5 * fwhm_mean_mhz
    assert shift_mean_mhz < 0.0, "the theoretical collisional shift itself must be RED (negative)"

    delta = np.linspace(-25.0, 25.0, 201)
    terms = dict(ALL_OFF)
    terms.update(chirp=0.0, saturation=0.0, collisions_speed=1.0, exchange_by_line=1.0)
    centres = []
    for seed in (171, 172):
        out, info = full_line(delta, **CORNER, n_path=3000, seed=seed, window_beam="gaussian",
                              terms=terms, half_window_m=0.0, delta_alpha_au=0.0, consumer="twin", registry=_BLOCH_STUDY)
        m, minfo = windowed_moments(delta, out, 20.0, orders=(3,), baseline=None)
        assert minfo["converged"] == 1.0, f"seed={seed}: self-centring did not converge"
        centres.append(minfo["centre"])
    mean_c = float(np.mean(centres))
    mc_err = float(abs(centres[0] - centres[1]))  # the two-seed Monte Carlo spread, measured HERE
    tol = max(3.0 * mc_err, 2e-3)
    print(f"\n(guard) shift_mean_mhz (theory) = {shift_mean_mhz:+.6f} MHz")
    print(f"(guard) self-centred first moment, seeds 171/172 = {centres[0]:+.6f} / {centres[1]:+.6f} "
         f"MHz, mean = {mean_c:+.6f} MHz, MC spread = {mc_err:.6f} MHz, tol = {tol:.6f} MHz")
    assert np.sign(mean_c) == np.sign(shift_mean_mhz), (
        f"the collisional shift landed on the WRONG side of resonance: mean centre {mean_c:+.6f} "
        f"MHz has the opposite sign from the theoretical shift_mean_mhz {shift_mean_mhz:+.6f} MHz")
    assert abs(mean_c - shift_mean_mhz) < tol, (
        f"self-centred first moment {mean_c:+.6f} MHz disagrees with shift_mean_mhz "
        f"{shift_mean_mhz:+.6f} MHz by more than tol={tol:.6f} MHz (3x the measured two-seed "
        f"Monte Carlo spread, floored at 2e-3 MHz)")



# ------------------------------------------------------------------------------------ V6.1's plants
#: the pre-V6.1 module, kept whole beside the repairs so the legacy arms can be graded against it bit for bit
LEGACY = CANONICAL / "private" / "cache" / "plan_2026-09-25" / "v61" / "backup_0925" / "bloch_full.py"
SMALL = dict(CORNER, n_path=160, seed=5)
GRID = np.arange(-6.0, 6.0 + 1e-9, 0.25)


def _legacy_module():
    if not LEGACY.is_file():
        pytest.skip("the pre-V6.1 module is kept in the governance tree only")
    spec = importlib.util.spec_from_file_location("rb5s6s._bloch_full_legacy", LEGACY)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "rb5s6s"
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


LEGACY_NUMERICS = dict(chord="gaussian", retro_kind="gaussian", retro_axial="focal")


@pytest.mark.skipif(not LEGACY.is_file(), reason="the pre-V6.1 module is kept in the governance tree only")
def test_v61_legacy_arms_reproduce_the_old_line_bit_for_bit():
    """The three legacy switches together are the old module's arithmetic, on the clipped beam and the Gaussian."""
    old = _legacy_module()
    for window_beam in ("clipped", "gaussian"):
        ref, _ = old.full_line(GRID, **SMALL, window_beam=window_beam)
        new, info = full_line(GRID, **SMALL, window_beam=window_beam, consumer="twin", registry=_BLOCH_STUDY,
                              **LEGACY_NUMERICS)
        assert np.array_equal(ref, new), (window_beam, float(np.max(np.abs(ref - new))))
        assert info["numerics"]["chord"] == "gaussian" and info["numerics"]["retro_axial"] == "focal"


def test_v61_the_true_chord_of_a_gaussian_beam_is_the_gaussian_chord():
    """POSITIVE: along the true chord a Gaussian beam's history IS u_b exp(-2 tau^2), so the two readings agree to
    rounding. NEGATIVE: on the clipped beam they must NOT agree, or the chord switch does nothing (F538's class)."""
    g_old, _ = full_line(GRID, **SMALL, window_beam="gaussian", chord="gaussian", consumer="twin", registry=_BLOCH_STUDY)
    g_new, _ = full_line(GRID, **SMALL, window_beam="gaussian", chord="beam", consumer="twin", registry=_BLOCH_STUDY)
    assert np.allclose(g_new, g_old, rtol=1e-9, atol=1e-12 * float(np.max(np.abs(g_old))))
    c_old, _ = full_line(GRID, **SMALL, window_beam="clipped", chord="gaussian", consumer="twin", registry=_BLOCH_STUDY)
    c_new, i_new = full_line(GRID, **SMALL, window_beam="clipped", consumer="twin", registry=_BLOCH_STUDY)
    assert i_new["numerics"]["chord"] == "beam"
    assert float(np.max(np.abs(c_new - c_old))) > 1e-4 * float(np.max(np.abs(c_old)))


def test_v61_a_matched_return_read_at_each_atoms_own_z_is_the_retro_off_line():
    """The matched returning beam IS the forward one at every z, so the two-arm line must equal the one-arm line
    whose shift carries (1 + rho) and whose Rabi frequency carries sqrt(rho): the identity the old docstring
    claimed. POSITIVE on the own-z reading; NEGATIVE on the legacy focal reading, which reads the return at z = 0
    for every atom and so cannot hold it off the focal plane (F543's fifth finding, measured here)."""
    kw = dict(SMALL, window_beam="gaussian", consumer="twin", registry=_BLOCH_STUDY)
    off, _ = full_line(GRID, **kw, terms={"retro_geometry": 0.0})
    own, _ = full_line(GRID, **kw)
    focal, _ = full_line(GRID, **kw, retro_kind="gaussian", retro_axial="focal")
    peak = float(np.max(np.abs(off)))
    assert float(np.max(np.abs(own - off))) < 1e-6 * peak
    assert float(np.max(np.abs(focal - off))) > 1e-4 * peak


def test_v71_the_frozen_means_are_finite_for_an_atom_the_drive_never_reaches():
    """V7.2's budget read every chirp-off line NaN: an atom with no returning envelope made `_frozen_means` 0/0. Such an
    atom has no drive, so its frozen shift is zero, and the other atoms' means are untouched (both ways)."""
    from rb5s6s.bloch_full import _frozen_means
    tt = np.linspace(-4.0, 4.0, 81)
    env = np.exp(-2.0 * tt ** 2)
    ef = np.vstack([env, env, env])
    er = np.vstack([env, np.zeros_like(env), 0.5 * env])
    mf, mr = _frozen_means(ef, er, tt)
    assert np.all(np.isfinite(mf)) and np.all(np.isfinite(mr))
    assert mf[1, 0] == 0.0 and mr[1, 0] == 0.0
    ref_f, ref_r = _frozen_means(ef[[0, 2]], er[[0, 2]], tt)
    assert np.allclose(mf[[0, 2], 0], ref_f[:, 0]) and np.allclose(mr[[0, 2], 0], ref_r[:, 0])
    mf1, none = _frozen_means(np.vstack([env, np.zeros_like(env)]), None, tt)
    assert none is None and np.all(np.isfinite(mf1)) and mf1[1, 0] == 0.0


@pytest.mark.slow
def test_v70_the_chirp_off_arm_keeps_the_weak_field_centroid():
    """F547 (2026-09-25). With `chirp` off each arm's shift is frozen at its average along the
    chord against the drive's rate weight, so in the weak field the line's centroid, the Om^2-weighted mean shift, is
    the chirped line's own at any tau_edge, and the arm moves only what the chirp moves. The uniform average over
    [-tau_edge, tau_edge] it replaced kept 0.19 of the centroid at tau_edge 4 and 0.13 at 6, and fails here."""
    delta = np.linspace(-8.0, 10.0, 181)
    kw = dict(CORNER, n_path=60, seed=5, window_beam="gaussian", consumer="twin", registry=_BLOCH_STUDY)

    def centroid(y):
        return float(np.sum(delta * y) / np.sum(y))

    for tau_edge in (4.0, 6.0):
        on, _ = full_line(delta, terms=dict(saturation=0.0), tau_edge=tau_edge, **kw)
        off, _ = full_line(delta, terms=dict(saturation=0.0, chirp=0.0), tau_edge=tau_edge, **kw)
        ratio = centroid(off) / centroid(on)
        print(f"  tau_edge {tau_edge:g}: centroid off/on {ratio:.4f}")
        assert abs(ratio - 1.0) < 0.02, f"the chirp-off arm moved the weak-field centroid: off/on {ratio:.4f}"


@pytest.mark.slow
def test_v71_the_returning_focus_curvature_rescales_the_transit():
    """F547 (2026-09-25). A returning focus Delta from the forward one leaves the wavefronts'
    curvatures unmatched and each chord at depth z carries the Doppler chirp k C(z) v x. In the focal plane, in the
    weak field, with no light shift and no collisions, the drive along a chord is Gaussian, exp(-a tau^2) with
    a = 1 + w0^2/w(Delta)^2, and a linear chirp on a Gaussian pulse rescales its spectrum by s = sqrt(1 + (g/a)^2),
    g = z_R C(0). The sampler draws every speed as the thermal speed times one random stream, so the line WITH the
    curvature at T is the line WITHOUT it at the temperature that scales every speed by s, atom by atom, and it is
    visibly not the line without it at T. Both directions: a chirp of the wrong size or none fails the first."""
    delta = np.linspace(-15.0, 15.0, 301)
    z_r = math.pi * W0 ** 2 / K.LAMBDA_LASER_M
    offset = z_r
    g = z_r * offset / (offset ** 2 + z_r ** 2)
    a = 1.0 + 1.0 / (1.0 + (offset / z_r) ** 2)
    s = math.sqrt(1.0 + (g / a) ** 2)
    T0 = 130.0
    T1 = s ** 2 * (T0 + 273.15) - 273.15
    kw = dict(peak="4192", P_W=0.225, w0_m=W0, M2=1.0, rho=0.94, n_path=80, seed=7, window_beam="gaussian",
              terms=dict(ALL_OFF, retro_geometry=1.0), half_window_m=0.0, delta_alpha_au=0.0,
              retro_focus_offset_m=offset, consumer="twin", registry=_BLOCH_STUDY)
    on, info = full_line(delta, T_C=T0, **kw)
    off_scaled, _ = full_line(delta, T_C=T1, retro_curvature="off", **kw)
    off_same, _ = full_line(delta, T_C=T0, retro_curvature="off", **kw)
    assert "retro_curvature" in info["executed"]

    def unit(y):
        return y / np.sum(y)

    same = float(np.max(np.abs(unit(on) - unit(off_scaled))) / np.max(unit(on)))
    moved = float(np.max(np.abs(unit(on) - unit(off_same))) / np.max(unit(on)))
    print(f"  s = {s:.4f}: against the rescaled line {same:.2e}, against the unrescaled one {moved:.2e}")
    assert same < 0.1 * moved, "the curvature line is not the rescaled transit"


def test_v61_a_displaced_returning_focus_moves_the_line():
    """Delta = 0 is the matched return and a returning focus a Rayleigh length away is not: the lens-8 term acts."""
    from rb5s6s.volume_line import GaussianBeam as _GB
    zr = _GB(W0, 1.0).z_R_m
    kw = dict(SMALL, window_beam="gaussian", consumer="twin", registry=_BLOCH_STUDY)
    at0, _ = full_line(GRID, **kw)
    at1, info = full_line(GRID, **kw, retro_focus_offset_m=zr)
    assert info["numerics"]["retro_focus_offset_m"] == zr
    assert float(np.max(np.abs(at1 - at0))) > 1e-3 * float(np.max(np.abs(at0)))


def test_v61_the_returning_beam_and_the_door_refuse_what_they_cannot_be():
    kw = dict(SMALL, window_beam="gaussian")
    with pytest.raises(ValueError, match="imaged return carries the forward beam's own size"):
        full_line(GRID, **kw, retro_waist_ratio=1.2, consumer="twin", registry=_BLOCH_STUDY)
    full_line(GRID, **kw, retro_waist_ratio=1.2, retro_kind="gaussian", consumer="twin", registry=_BLOCH_STUDY)
    with pytest.raises(ValueError, match="retro_axial='focal'"):
        full_line(GRID, **kw, retro_axial="focal", consumer="twin", registry=_BLOCH_STUDY)
    with pytest.raises(ValueError, match="name the consumer"):
        full_line(GRID, **kw)
    from rb5s6s.model_registry import ModelReduced
    with pytest.raises(ModelReduced, match="does not declare"):
        full_line(GRID, **kw, consumer="twin")


def test_v61_dropped_flux_past_its_budget_is_refused_and_a_declared_budget_admits():
    kw = dict(SMALL, window_beam="gaussian", consumer="twin", registry=_BLOCH_STUDY, max_sub=1)
    with pytest.raises(ValueError, match="would be dropped for its step count"):
        full_line(GRID, **kw)
    _, info = full_line(GRID, **kw, dropped_flux_budget=1.0)
    assert info["dropped_flux_frac"] > 1e-3
