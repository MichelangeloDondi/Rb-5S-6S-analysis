"""Tests for `rb5s6s/twin_volume.py`, the digital twin's WORLD on the joint per-path line (owner
order O45/O46). See `private/cache/plan_2026-09-18/volume_line_report.md` and
`tests/test_volume_line.py`'s own module docstring for the findings (F290, F293, F294) this
promotes, and for why every number asserted here is this promotion's OWN calibrated reading at
its own fast settings, not the private prototype's production numbers.
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.constants import RHO_RETRO, W0_CENTRAL_M
from rb5s6s.moments import windowed_moments
from rb5s6s.lineshape import aperture_onaxis_factor_actual
from rb5s6s.volume_line import GaussianBeam, collection_half_window_m, joint_spectrum
from rb5s6s import twin_volume as tv

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "a unit test of the generator's own arithmetic, not a quoted number"

M2 = 1.0
T_C = 130.0
Z_RATIO = 0.6
GAMMA_HOM_MHZ = 3.6


@pytest.fixture(scope="module")
def beam():
    return GaussianBeam(W0_CENTRAL_M, M2)


@pytest.fixture(scope="module")
def s0_mhz(beam):
    return tv.stark_s0_mhz(0.225, beam.w0_m, RHO_RETRO)


# =============================================================================================
# stark_s0_mhz: the physical (power, waist) -> S0 bridge, through the CORRECTED on-axis factor
# =============================================================================================

def test_stark_s0_mhz_positive_and_linear_in_power(beam):
    """S0 > 0 and exactly linear in power (`stark_shift_S0_mhz`'s own I_eff is linear in P; the
    on-axis factor does not depend on power at all)."""
    s1 = tv.stark_s0_mhz(0.225, beam.w0_m, RHO_RETRO)
    s2 = tv.stark_s0_mhz(0.450, beam.w0_m, RHO_RETRO)
    assert s1 > 0.0
    assert s2 / s1 == pytest.approx(2.0, rel=1e-9)


def test_stark_s0_mhz_uses_the_actual_not_plain_aperture_factor(beam):
    """`stark_s0_mhz` must go through `aperture_onaxis_factor_actual` (F280/F291/F298's corrected
    convention), not the plain `aperture_onaxis_factor` it replaced at the bore-limited waist --
    the two disagree by about 20 per cent there (F280's own reading; measured here: 0.7154
    against 0.8884, a 19.5 per cent gap), so this is a real, discriminating check and not a
    tautology. The actual on-axis factor at `W0_CENTRAL_M` reads about 0.888 (the record's own
    cited 0.8896-0.8897 is at a slightly different input radius); a wide sanity band is asserted
    rather than that exact figure."""
    from rb5s6s.lineshape import aperture_onaxis_factor as plain_factor
    s0 = tv.stark_s0_mhz(0.225, beam.w0_m, RHO_RETRO)
    factor_actual = aperture_onaxis_factor_actual(beam.w0_m)
    factor_plain = plain_factor(beam.w0_m)
    assert 0.85 < factor_actual < 0.92
    assert factor_plain < 0.9 * factor_actual, (
        "the plain on-axis factor should read well below the actual one at this bore-limited "
        "waist (F280); if it does not, stark_s0_mhz's choice of the two is no longer verified "
        "to matter")
    from rb5s6s.lineshape import stark_shift_S0_mhz
    expected = stark_shift_S0_mhz(0.225, beam.w0_m, rho=RHO_RETRO) * factor_actual
    assert s0 == pytest.approx(expected, rel=1e-9)


def test_stark_s0_mhz_clamp_floor_matches_aperture_onaxis_factor_actual():
    """`clamp_floor` is passed straight through to `aperture_onaxis_factor_actual`: a waist below
    this bore's floor raises without it and returns a clamped, finite value with it."""
    below_floor_m = 38e-6      # under the ~40.9 um bore floor (F280)
    with pytest.raises(ValueError):
        tv.stark_s0_mhz(0.225, below_floor_m, RHO_RETRO)
    s0 = tv.stark_s0_mhz(0.225, below_floor_m, RHO_RETRO, clamp_floor=True)
    assert s0 > 0.0 and np.isfinite(s0)


# =============================================================================================
# synthetic_traces: format, determinism, and the noise modes
# =============================================================================================

def test_synthetic_traces_format_matches_forecast_convention(beam, s0_mhz):
    """Returns (freqs, volts), each a list of `n_traces` arrays of `n_points`, matching
    `rb5s6s.forecast.synthetic_traces`'s own return convention (the `fit_condition` input form)."""
    n_traces, n_points = 4, 601
    freqs, volts = tv.synthetic_traces(beam=beam, T_C=T_C, S0_mhz=s0_mhz,
                                       gamma_hom_mhz=GAMMA_HOM_MHZ, z_ratio=Z_RATIO,
                                       span_mhz=24.0, n_points=n_points, n_traces=n_traces,
                                       noise=0.01, n_path=300, seed=0,
                                       rng=np.random.default_rng(1), registry=_TWIN_STUDY)
    assert len(freqs) == n_traces and len(volts) == n_traces
    for f, v in zip(freqs, volts):
        assert f.shape == (n_points,)
        assert v.shape == (n_points,)
        assert np.all(np.isfinite(v))
    for f in freqs[1:]:
        assert np.array_equal(f, freqs[0]), "every trace shares the same frequency axis"


def test_synthetic_traces_amp_and_offset_spread(beam, s0_mhz):
    """Successive traces carry the same `amp_spread`/`offset_spread` pattern
    `forecast.synthetic_traces` uses: with noise off, trace i's peak-region level is
    `amp*(1+amp_spread*i) + offset+offset_spread*i`, exactly."""
    n_traces = 3
    freqs, volts = tv.synthetic_traces(beam=beam, T_C=T_C, S0_mhz=s0_mhz,
                                       gamma_hom_mhz=GAMMA_HOM_MHZ, z_ratio=Z_RATIO,
                                       span_mhz=24.0, n_points=801, n_traces=n_traces,
                                       noise=0.0, amp=1.0, amp_spread=0.1, offset=0.02,
                                       offset_spread=0.005, n_path=300, seed=0,
                                       rng=np.random.default_rng(0), registry=_TWIN_STUDY)
    for i, v in enumerate(volts):
        expected_peak = 1.0 * (1.0 + 0.1 * i) + 0.02 + 0.005 * i
        assert v.max() == pytest.approx(expected_peak, rel=1e-9)


def test_synthetic_traces_determinism(beam, s0_mhz):
    """The world's own Monte Carlo is controlled by `seed` (identical world at identical seed);
    the per-point noise is controlled by `rng` (identical noise at an identically-seeded
    Generator, different noise otherwise, with the world held fixed)."""
    kwargs = dict(beam=beam, T_C=T_C, S0_mhz=s0_mhz, gamma_hom_mhz=GAMMA_HOM_MHZ, z_ratio=Z_RATIO,
                 span_mhz=24.0, n_points=401, n_traces=2, noise=0.01, n_path=300, seed=7)
    _, v_a = tv.synthetic_traces(rng=np.random.default_rng(100), **kwargs, registry=_TWIN_STUDY)
    _, v_b = tv.synthetic_traces(rng=np.random.default_rng(100), **kwargs, registry=_TWIN_STUDY)
    _, v_c = tv.synthetic_traces(rng=np.random.default_rng(101), **kwargs, registry=_TWIN_STUDY)
    assert all(np.array_equal(a, b) for a, b in zip(v_a, v_b))
    assert not all(np.array_equal(a, c) for a, c in zip(v_a, v_c))


def test_synthetic_traces_world_is_monte_carlo_not_table(beam, s0_mhz):
    """THE TASK'S OWN REQUIREMENT: the world must be the Monte Carlo, never the fitter's table.
    Checked structurally: `JointTable` is not even in `twin_volume`'s own namespace, so no
    function in this module can build a trace from it (`inspect.getsource`'s full text also
    matches this module's OWN docstring, which correctly discusses `JointTable` in prose -- the
    namespace is the precise check, the source text is not)."""
    from rb5s6s import twin_volume as tv_mod
    assert not hasattr(tv_mod, "JointTable"), (
        "the twin's world must not be built from the fitter's table")


def test_synthetic_traces_noise_law_dict_mode(beam, s0_mhz):
    """The second `noise` mode (a `rb5s6s.noise`-style law dict, evaluated per point through
    `sigma_of_v`) must run and produce a finite, non-degenerate trace -- the format
    `rb5s6s.noise.condition_noise_model`/`load_noise_model` return (keys a, b, c)."""
    law = dict(a=0.002, b=0.01, c=0.05)
    freqs, volts = tv.synthetic_traces(beam=beam, T_C=T_C, S0_mhz=s0_mhz,
                                       gamma_hom_mhz=GAMMA_HOM_MHZ, z_ratio=Z_RATIO,
                                       span_mhz=24.0, n_points=601, n_traces=2, noise=law,
                                       n_path=300, seed=0, rng=np.random.default_rng(2), registry=_TWIN_STUDY)
    for v in volts:
        assert np.all(np.isfinite(v))
        assert v.std() > 0.0


def test_synthetic_traces_vanishing_line_raises(beam):
    """A window with no line on it at all (far off centre, tiny span) must raise, not return a
    silently-degenerate all-baseline trace. Only the COHERENT line (no homogeneous width) can vanish:
    a Lorentzian has a wing at every detuning, 1.3e-5 of its peak at 500 MHz here, and the exact zero
    the per-atom route returned there before F317 (2026-09-22) was its band truncation."""
    with pytest.raises(ValueError):
        tv.synthetic_traces(beam=beam, T_C=T_C, S0_mhz=0.6, gamma_hom_mhz=0.0,
                            z_ratio=Z_RATIO, span_mhz=0.05, n_points=21, n_traces=1,
                            centre_mhz=500.0, n_path=50, seed=0, rng=np.random.default_rng(0), registry=_TWIN_STUDY)


# =============================================================================================
# THE TASK'S OWN REQUIREMENT: a twin trace's windowed moments match the world line's
# =============================================================================================

def test_windowed_moments_match_world_line_within_the_noise(beam, s0_mhz):
    """A twin trace's windowed moments (`rb5s6s.moments.windowed_moments`) must match the
    world line's own, to within the noise the traces themselves carry. Ten traces (noise=0.01,
    amp/offset spread off so every trace shares one underlying shape) give the per-order mean and
    its standard error; the world's own moments (computed directly from `joint_spectrum` at the
    SAME seed and n_path the twin used internally) must sit within a few standard errors of that
    mean. CALIBRATED at this test's own settings: order 2 (variance-like) at -0.24 SEM, order 3
    (skew-like, the record's own drift-immune channel) at -0.05 SEM -- both comfortably inside
    even a tight bound; order 1 (the centroid) is ~0 on both sides by construction (no centre
    shift, no amplitude/offset spread), so it is checked on an absolute floor instead of a SEM
    ratio, which is ill-defined at a near-zero denominator."""
    n_path, seed, n_traces = 1000, 3, 10
    freqs, volts = tv.synthetic_traces(beam=beam, T_C=T_C, S0_mhz=s0_mhz,
                                       gamma_hom_mhz=GAMMA_HOM_MHZ, z_ratio=Z_RATIO,
                                       span_mhz=24.0, n_points=1201, n_traces=n_traces,
                                       noise=0.01, amp=1.0, amp_spread=0.0, offset=0.0,
                                       offset_spread=0.0, n_path=n_path, seed=seed,
                                       rng=np.random.default_rng(42), registry=_TWIN_STUDY)
    nu = freqs[0]
    half_window_m = collection_half_window_m(beam, Z_RATIO)
    world = joint_spectrum(S0_mhz=s0_mhz, gamma_hom_mhz=GAMMA_HOM_MHZ, beam=beam, T_C=T_C,
                           half_window_m=half_window_m, n_path=n_path, seed=seed, delta_mhz=nu,
                           n_tau=301, tau_edge=6.0)
    half_w = 8.0
    mu_world, _ = windowed_moments(nu, world, half_w, orders=(1, 2, 3), baseline=None)

    for order in (1, 2, 3):
        vals = np.array([windowed_moments(nu, v, half_w, orders=(order,), baseline=None)[0][order]
                         for v in volts])
        mean = float(vals.mean())
        sem = float(vals.std(ddof=1) / np.sqrt(len(vals)))
        diff = mean - mu_world[order]
        bound = max(5.0 * sem, 1e-6)
        assert abs(diff) < bound, (
            f"order {order}: trace mean {mean:.6g} vs world {mu_world[order]:.6g}, "
            f"diff {diff:.3g} exceeds max(5 sem, 1e-6) = {bound:.3g}")
