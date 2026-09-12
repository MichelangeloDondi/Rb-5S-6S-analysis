"""The full model adds terms without moving the default path.

Every new term is checked in BOTH directions: the default reproduces
`lineshape.model_profile` byte for byte, and the term actually changes the
trace when switched on. A no-op switch that reports success is the trap this
record has hit twice (`stark.COMPANIONS` unwired, `tooth_of` unthreaded).
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import stark
from rb5s6s.lineshape import model_profile
from rb5s6s.fullmodel import (doppler_pedestal_fwhm_mhz, saturation_companion_mhz,
                              collection_z_ratio_m2, full_profile)

NU = np.linspace(-40, 40, 8001)
B = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575, gamma_l=0.40, s0=0.364)


def test_the_default_path_is_byte_identical_to_model_profile():
    a = model_profile(NU, **B)
    b = full_profile(NU, **B)
    assert np.array_equal(a, b)


@pytest.mark.parametrize("kw", [
    dict(omega_mhz=0.45),
    dict(pedestal_height_frac=3e-3),
    dict(omega_mhz=0.45, peak="4121"),
])
def test_every_added_term_changes_the_trace(kw):
    """The other half: a switch that does nothing reports success."""
    a = full_profile(NU, **B)
    b = full_profile(NU, **B, **kw)
    assert not np.array_equal(a, b)


def test_the_pumping_term_is_the_only_F_dependent_one():
    """Saturation is F-independent; pumping carries the per-line branching."""
    plain = saturation_companion_mhz(0.45)
    per_peak = {p: saturation_companion_mhz(0.45, p) for p in stark.F_PER_LINE}
    assert all(v > plain for v in per_peak.values())
    lo, hi = min(per_peak.values()), max(per_peak.values())
    # the branching spans 0.2235 to 0.3725, so the companion spans (1+f) over that
    assert hi / lo == pytest.approx(
        (1 + max(stark.F_PER_LINE.values())) / (1 + min(stark.F_PER_LINE.values())))


def test_saturation_survives_a_zero_light_shift():
    """The whole point: stark.companion_gamma_mhz vanishes at s0 = 0 and this
    does not, because Omega is its own parameter."""
    assert stark.companion_gamma_mhz(0.0, "4121") == 0.0
    assert saturation_companion_mhz(0.45, "4121") > 0.0
    a = full_profile(NU, **{**B, "s0": 0.0})
    b = full_profile(NU, **{**B, "s0": 0.0}, omega_mhz=0.45, peak="4121")
    assert not np.array_equal(a, b)


def test_the_pedestal_width_is_the_two_photon_doppler_width():
    w = doppler_pedestal_fwhm_mhz(130.0)
    assert 900.0 < w < 960.0, w                      # the record's traces give ~942
    assert doppler_pedestal_fwhm_mhz(70.0) < w       # narrower when colder
    assert doppler_pedestal_fwhm_mhz(130.0, isotope=85) > w   # lighter isotope, faster


def test_the_pedestal_moves_a_wide_window_cumulant_and_a_narrow_one_barely():
    """The measurement that motivated the term: it is invisible at 6 MHz and
    dominant at 40, which is why wide-window moments need it carried."""
    from rb5s6s.cumulants import windowed_cumulants
    grid = np.linspace(-200, 200, 200001)
    a = full_profile(grid, **B)
    b = full_profile(grid, **B, pedestal_height_frac=3e-3)
    k_a6, _ = windowed_cumulants(grid, a, 6.0, orders=(3,))
    k_b6, _ = windowed_cumulants(grid, b, 6.0, orders=(3,))
    k_a40, _ = windowed_cumulants(grid, a, 40.0, orders=(3,))
    k_b40, _ = windowed_cumulants(grid, b, 40.0, orders=(3,))
    near = abs(k_b6[3] / k_a6[3] - 1.0)
    far = abs(k_b40[3] / k_a40[3] - 1.0)
    assert near < 0.05, near
    assert far > 1.0, far


def test_m2_enters_the_collection_ratio_and_refuses_to_be_a_no_op():
    """The earlier version of this test asserted that full_profile has NO m2
    argument, which enshrined a hole as a specification: beam quality reached
    the line only if a caller wired it through the `profile` seam, and one who
    forgot got a silently diffraction-limited beam."""
    base = collection_z_ratio_m2(64e-6, 1.0)
    assert collection_z_ratio_m2(64e-6, 2.0) == pytest.approx(2.0 * base)
    import inspect
    assert "m2" in inspect.signature(full_profile).parameters
    with pytest.raises(ValueError, match="needs w0_m"):
        full_profile(NU, m2=2.0, **B)
    # AND THE ARGUMENT MUST REACH THE PROFILE. The refusal above passing is not
    # evidence that the term works: the first version refused the bad
    # combination and then ignored the good one, so the refusal concealed a
    # no-op. Both halves, as every switch in this module is checked.
    ideal = full_profile(NU, **B)
    assert np.array_equal(ideal, full_profile(NU, m2=1.0, w0_m=64e-6, **B))
    worse = full_profile(NU, m2=3.0, w0_m=64e-6, **B)
    assert not np.array_equal(ideal, worse)
    assert np.max(np.abs(worse - ideal)) / np.max(ideal) > 1e-3


def test_the_twin_carries_the_two_campaign_terms_in_both_directions():
    """build_world_trace routes to full_profile only when a new term is asked
    for, so the default path is byte-identical and each term changes the trace."""
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
         "drift": False, "quantise": True, "randomise": False}
    kw = dict(positions={"4192": 0.0}, shares={"4192": 1.0}, gamma_coll=0.55,
              sigma_laser_fwhm=1.6, transit_fwhm=0.9575, power_max_w=1.0,
              cycles_at_max=1.0, drift_mhz_total=0.0, noise_frac_bright=0.004,
              adc_levels=4096)
    base = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, **kw)[1]
    same = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L,
                             pedestal_height_frac=0.0, retro_tilt_rad=0.0, **kw)[1]
    assert np.array_equal(base, same)
    for extra in (dict(pedestal_height_frac=3e-3), dict(retro_tilt_rad=2.36e-3)):
        moved = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7),
                                  L, **extra, **kw)[1]
        assert not np.array_equal(base, moved), extra


def test_the_retro_tilt_broadens_without_shifting():
    """The property that makes the term worth carrying: every other broadener
    here moves with the intensity and so shows in the light shift too."""
    from rb5s6s.fullmodel import residual_doppler_fwhm_mhz
    assert residual_doppler_fwhm_mhz(0.0, 110.0) == 0.0
    w = residual_doppler_fwhm_mhz(2.36e-3, 110.0)
    assert 1.0 < w < 1.15, w                      # the gap between 42 and 64 um
    assert residual_doppler_fwhm_mhz(4.72e-3, 110.0) == pytest.approx(2 * w, rel=1e-3)
    # broadens the line and leaves its centroid alone
    a = full_profile(NU, **B)
    b = full_profile(NU, **B, retro_tilt_rad=2.36e-3, T_C=110.0)
    c = lambda y: float(np.sum(NU * y) / np.sum(y))
    assert np.std(b) < np.std(a)                  # flatter, because wider
    assert c(b) == pytest.approx(c(a), abs=2e-3)  # same centroid


def test_the_generalised_fringe_mc_reproduces_fringe_tails_own_answer():
    """The real plant, replacing one that tested nothing.

    The first version only checked that the position-dependent contrast averages
    to `2 sqrt(rho)/(1+rho)`. At zero offset the two envelopes are proportional
    everywhere, so that contrast IS the constant at every point and its mean is
    trivially the constant: the test confirmed the formula had been typed.

    What has to hold is that this routine reproduces the ANSWER of the one it
    generalises. It is checked over SEEDS, because `frac_resolved` is a weighted
    tail whose effective sample size is a few per cent of the atoms drawn, and a
    single seed disagreed by twenty per cent while eight agreed to 0.3 sigma.
    """
    from rb5s6s.fringe_tail import fringe_tail_mc
    from rb5s6s.fullmodel import fringe_survival_mc
    a, b = [], []
    for s in range(6):
        a.append(fringe_tail_mc(w0_m=64e-6, s0_mhz=0.364, rho=0.94, T_C=130.0,
                                n_atoms=120_000, seed=s)["frac_resolved"])
        b.append(fringe_survival_mc(w0_m=64e-6, rho=0.94, T_C=130.0,
                                    n_atoms=120_000, seed=s,
                                    half_window_m=0.0)["frac_resolved"])
    a, b = np.array(a), np.array(b)
    err = np.hypot(a.std(ddof=1), b.std(ddof=1)) / np.sqrt(len(a))
    assert abs(b.mean() - a.mean()) < 3.0 * err, (a.mean(), b.mean(), err)


def test_frac_resolved_reports_an_effective_sample_size_far_below_the_draw():
    """The quantity is a weighted tail, so the nominal atom count overstates it
    by more than an order of magnitude. Quoting it to three digits off one seed
    is what that shortfall punishes."""
    from rb5s6s.fullmodel import fringe_survival_mc
    r = fringe_survival_mc(w0_m=64e-6, rho=0.94, n_atoms=200_000, seed=7)
    assert 0.0 < r["n_eff"] < 0.2 * 200_000, r["n_eff"]
    assert r["frac_resolved_se"] > 0.05 * r["frac_resolved"]


def test_the_contrast_carries_the_polarisation_overlap():
    """Only rank 0 survives for J = 1/2 and rank 0 goes as e1.e2, so a standing
    wave interferes only to the extent the two fields share a polarisation. The
    parallel case is an upper bound, not a neutral default."""
    from rb5s6s.fullmodel import fringe_survival_mc
    base = dict(w0_m=64e-6, rho=0.94, n_atoms=120_000, seed=7)
    par = fringe_survival_mc(**base)["mean_contrast"]
    for f in (0.8, 0.5, 0.0):
        got = fringe_survival_mc(**base, e1_dot_e2=f)["mean_contrast"]
        assert got == pytest.approx(f * par, rel=1e-9), (f, got, par)
    assert not fringe_survival_mc(**base, e1_dot_e2=0.8,
                                  half_window_m=0.0)["reduces_to_ideal"]


@pytest.mark.parametrize("kw,key,direction", [
    (dict(m2=3.0), "mean_w_over_w0", "up"),      # a worse beam diverges faster
    (dict(m2=3.0), "mean_F", "down"),            # and so washes fringes harder
    (dict(offset_m=64e-6), "mean_contrast", "down"),   # a displaced retro
])
def test_each_new_axis_moves_the_right_quantity_the_right_way(kw, key, direction):
    from rb5s6s.fullmodel import fringe_survival_mc
    base = dict(w0_m=64e-6, rho=0.94, n_atoms=200_000, seed=7)
    a = fringe_survival_mc(**base)[key]
    b = fringe_survival_mc(**base, **kw)[key]
    assert (b > a) if direction == "up" else (b < a), (a, b)


def test_the_tilt_angle_alone_is_negligible_and_the_offset_is_not():
    """Measured, not asserted: the transverse fringe wave-vector k sin(theta) is
    four orders below the axial 2k, so the tilt ANGLE barely washes fringes out.
    What a tilt does to this bench it does through the OFFSET it produces."""
    from rb5s6s.fullmodel import fringe_survival_mc
    base = dict(w0_m=64e-6, rho=0.94, n_atoms=200_000, seed=7)
    ideal = fringe_survival_mc(**base)["mean_F"]
    tilted = fringe_survival_mc(**base, tilt_rad=5e-4)["mean_F"]
    offset = fringe_survival_mc(**base, offset_m=64e-6)["mean_contrast"]
    assert abs(tilted / ideal - 1.0) < 0.02, (ideal, tilted)
    assert offset < 0.9 * fringe_survival_mc(**base)["mean_contrast"]


def test_the_ultra_joint_statistics_carry_the_shift_free_ratios():
    from rb5s6s.fullmodel import ultra_joint_statistics
    grid = np.linspace(-60, 60, 120001)
    s = ultra_joint_statistics(grid, **B)
    assert any(k.startswith("k5/k3@") for k in s)
    assert any(k.startswith("k7/k5@") for k in s)
    # k5/k3 is shift-free: move S0 and the ratio must barely move
    a = ultra_joint_statistics(grid, **{**B, "s0": 0.364})["k5/k3@6"]
    b = ultra_joint_statistics(grid, **{**B, "s0": 2.0})["k5/k3@6"]
    assert abs(b / a - 1.0) < 0.10, (a, b)
    assert a < 0, a                       # and opposite in sign to k3


def test_the_joint_likelihood_refuses_an_empty_comparison():
    """A chi-squared summed over no statistic is zero, which reads as a perfect
    fit. That is the shrinking-population failure this record keeps finding."""
    from rb5s6s.fullmodel import ultra_joint_nll
    grid = np.linspace(-40, 40, 8001)
    with pytest.raises(ValueError, match="no statistic was comparable"):
        ultra_joint_nll({"k3@6": 1.0}, {"k3@6": 0.0}, grid, **B)
    obs = {"k3@6": 1e-4}
    assert ultra_joint_nll(obs, {"k3@6": 1e-5}, grid, **B) >= 0.0


def test_aic_bic_reproduce_the_grids_own_preference_for_the_cusp():
    """The committed grid: cusp chi2_red 0.857, Voigt 0.863, five parameters
    each. The cusp must lead, which is why the form is selectable and not only
    spannable."""
    from rb5s6s.fullmodel import aic_bic
    n = 4000
    cusp = aic_bic(0.857 * (n - 5), 5, n)
    voigt = aic_bic(0.863 * (n - 5), 5, n)
    assert voigt["aic"] - cusp["aic"] > 10.0
    assert voigt["bic"] - cusp["bic"] > 10.0
    with pytest.raises(ValueError):
        aic_bic(10.0, 20, 5)


def test_the_twin_carries_beam_quality_and_the_rabi_parameterisation():
    """Both halves for both, because m2 was a no-op in the twin twice.

    The first time full_profile took m2 and ignored it. The second time it used
    it, but build_world_trace passes its own `profile` closure, so full_profile's
    m2 branch stood down and the twin ignored it again. A refusal firing on the
    bad combination is not evidence that the good one works.
    """
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
         "drift": False, "quantise": True, "randomise": False}
    kw = dict(positions={"4192": 0.0}, shares={"4192": 1.0}, gamma_coll=0.55,
              sigma_laser_fwhm=1.6, transit_fwhm=0.9575, power_max_w=1.0,
              cycles_at_max=1.0, drift_mhz_total=0.0, noise_frac_bright=0.004,
              adc_levels=4096)
    g = lambda **e: build_world_trace(1.0, 0.364, 130.0, 0, 1,
                                      np.random.default_rng(3), L, **e, **kw)[1]
    base = g()
    assert np.array_equal(base, g(m2=1.0))
    for m2 in (2.0, 3.0):
        v = g(m2=m2, w0_m=64e-6)
        assert not np.array_equal(base, v), m2
        assert np.max(np.abs(v - base)) / np.max(base) > 1e-3, m2
    with pytest.raises(ValueError, match="needs w0_m"):
        g(m2=3.0)
    # THE RABI PARAMETERISATION AND THE SATURATION LAYER ARE ONE TERM, so asking
    # for both double counts it: with both, the built line ran 5.4809 MHz against
    # 5.4209 for either alone (physics seat, 2026-09-12). The refusal is checked
    # here, and the switch is then thrown on the layer-OFF world so that this
    # test still proves omega_mhz REACHES the trace and does not merely refuse.
    with pytest.raises(ValueError, match="double counts"):
        g(omega_mhz=0.45)
    L_off = dict(L, saturation=False)
    h = lambda **e: build_world_trace(1.0, 0.364, 130.0, 0, 1,
                                      np.random.default_rng(3), L_off, **e, **kw)[1]
    assert not np.array_equal(h(), h(omega_mhz=0.45))


def test_the_fitter_recovers_what_the_world_injects_when_the_terms_match():
    """The symmetric closed loop the census says the twin could not do: the
    same term list on both sides, so a recovery means something."""
    from rb5s6s.fullmodel import fit_full
    truth = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
                 gamma_l=0.40, s0=0.364)
    y = full_profile(NU, peak="4192", **truth)
    y = 2.5 * y / y.max() + 0.01                      # amplitude and offset
    for free in (("transit_fwhm",), ("transit_fwhm", "gamma_l")):
        r = fit_full(NU, y, free=free, peak="4192",
                     fixed={k: v for k, v in truth.items() if k not in free})
        for f in free:
            assert r[f] == pytest.approx(truth[f], rel=1e-6), (free, f, r[f])
        assert not r["start_dependent"], free


def test_the_fitter_flags_a_start_dependent_degeneracy_instead_of_hiding_it():
    """Freeing the Rabi frequency alongside the Lorentzian component puts two
    terms into one measurable homogeneous sum. The fit still returns a number;
    what makes it readable is that it says the number depends on the start."""
    from rb5s6s.fullmodel import fit_full
    truth = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
                 gamma_l=0.40, s0=0.364, omega_mhz=0.45)
    y = full_profile(NU, peak="4192", **truth)
    y = 2.5 * y / y.max() + 0.01
    r = fit_full(NU, y, free=("transit_fwhm", "gamma_l", "omega_mhz"),
                 peak="4192", fixed={"gamma_coll": 0.55, "sigma_laser_fwhm": 1.6,
                                     "s0": 0.364}, n_starts=4)
    assert r["start_dependent"], r["start_spread"]


def test_an_unfittable_term_raises_instead_of_being_silently_pinned():
    """A pinned term the caller believes is free is how a recovery test reads
    as a success it did not earn."""
    from rb5s6s.fullmodel import fit_full, term_coverage
    y = full_profile(NU, **B)
    for bad in ("m2", "t_bbr_k", "e1_dot_e2"):
        with pytest.raises(ValueError, match="cannot be fitted"):
            fit_full(NU, y, free=("transit_fwhm", bad))
    with pytest.raises(ValueError, match="not fittable"):
        term_coverage(("no_such_term",))


def test_the_asymmetry_is_computed_and_not_kept_by_hand():
    """The census kept this in a CSV column that went stale within a day of the
    terms being added."""
    from rb5s6s.fullmodel import term_coverage, FIT_TERMS, UNFITTABLE
    c = term_coverage(("transit_fwhm", "gamma_l"))
    assert set(c["free"]) | set(c["pinned"]) == set(FIT_TERMS)
    assert not set(c["free"]) & set(UNFITTABLE)
    assert c["closed_loop_is_symmetric"] is False    # while UNFITTABLE is non-empty
    for why in UNFITTABLE.values():
        assert len(why) > 30, why                    # a reason, not a label


def test_a_pinned_term_takes_the_generators_default_and_not_its_fitting_start():
    """The bug this test was written for: a term neither freed nor fixed was
    held at its FITTING START, so the fitter carried `omega_mhz = 0.45` against
    a world built without it and a one-parameter transit recovery came back six
    per cent wrong. The asymmetry the fitter exists to remove, reintroduced
    inside the fitter."""
    import inspect
    from rb5s6s.fullmodel import _GENERATOR_DEFAULTS, FIT_TERMS
    sig = inspect.signature(full_profile)
    assert set(_GENERATOR_DEFAULTS) == set(FIT_TERMS)
    for k, v in _GENERATOR_DEFAULTS.items():
        if k in sig.parameters and sig.parameters[k].default is not inspect.Parameter.empty:
            assert sig.parameters[k].default == v, (k, sig.parameters[k].default, v)
    # and at least one start differs from its default, or the test is vacuous
    assert any(FIT_TERMS[k][2] != _GENERATOR_DEFAULTS[k] for k in FIT_TERMS)


def test_a_free_centre_absorbs_the_first_order_shift_and_the_fit_says_so():
    """The asymmetry is a FORWARD-MODEL quantity, not a free shape.

    The ramp's density is |s| on [-S0, 0], fixed by the beam geometry and the
    polarizability. Expanding, a free centre spans the O(S0) term exactly, so
    freeing it removes that channel and leaves O(S0^2): the information becomes
    quartic at the origin. On noiseless data both fits still find the truth,
    which is why a best-fit value alone cannot show this. What shows it is the
    START SPREAD, and the fitter reports it rather than hiding it behind a
    covariance.
    """
    from rb5s6s.fullmodel import fit_full
    truth = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
                 gamma_l=0.40, s0=0.364)
    y = full_profile(NU, peak="4192", **truth)
    y = 2.5 * y / y.max() + 0.01
    fixed = {k: v for k, v in truth.items() if k != "s0"}
    pinned = fit_full(NU, y, free=("s0",), fixed=fixed, peak="4192", n_starts=4)
    freed = fit_full(NU, y, free=("s0", "centre_mhz"), fixed=fixed,
                     peak="4192", n_starts=4)
    assert pinned["s0"] == pytest.approx(0.364, rel=1e-6)
    assert not pinned["start_dependent"]
    # the centre is what changes, not the optimum
    assert freed["start_spread"]["s0"] > 1e4 * pinned["start_spread"]["s0"]
    assert freed["start_dependent"]
