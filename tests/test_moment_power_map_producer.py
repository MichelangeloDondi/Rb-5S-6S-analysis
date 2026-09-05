"""Guards for `scripts/run_moment_power_map.py`, the moment-power map.

WHY EACH TEST IS HERE. The producer measures the power of S0 that each windowed
odd cumulant carries, across the Lorentzian component, the noise level, the
oscilloscope and the window. Its first build called `model_profile` directly and
added hand-rolled noise, which exercised none of the physics layers and could
not vary the oscilloscope at all -- a narrower study wearing the right name,
caught by reading the design back against the code and by nothing automatic.
These tests are what would catch it next time.
"""
from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_moment_power_map.py"


def _load():
    spec = importlib.util.spec_from_file_location("_mpm", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_generator_is_the_unified_production_path():
    """It must build traces through `build_world_trace`, not `model_profile`.

    The distinction is the whole point: only the world builder carries
    blackbody, cascade depletion, saturation, drift and the ADC, so only it can
    answer a question whose axes include the oscilloscope. A producer that
    reached for the bare profile would silently answer a different question.
    """
    src = SCRIPT.read_text(encoding="utf-8")
    assert "build_world_trace" in src
    assert "from rb5s6s.lineshape import model_profile" not in src


def test_every_physics_layer_is_on_except_the_one_the_estimator_cannot_see():
    mod = _load()
    for layer in ("cascade", "saturation", "stark", "bbr", "quantise"):
        assert mod.LAYERS[layer] is True, layer
    # drift is off DELIBERATELY: the self-centred estimator is exactly immune
    # to a rigid shift, so a drift arm would vary an axis the answer cannot
    # see and would report that insensitivity as a result.
    assert mod.LAYERS["drift"] is False


def test_the_grid_is_the_full_factorial_and_names_every_scope_mode():
    mod = _load()
    assert len(mod._grid()) == (len(mod.GAMMA_L) * len(mod.NOISE_LEVEL)
                                * len(mod.SCOPES) * len(mod.WINDOW)
                                * len(mod.RESOLVE))
    # a scope with several resolution modes does not define an axis until the
    # mode is named, so each entry carries one
    from rb5s6s import instruments as I
    for name, mode, bits in mod.SCOPES:
        assert name in I.INSTRUMENTS, name
        assert mode in I.INSTRUMENTS[name].modes, (name, mode)
        assert I.INSTRUMENTS[name].modes[mode].bits == pytest.approx(bits)


def test_the_worker_count_is_capped_at_eight():
    src = SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"workers = (max\(1, min\(8, int\(os\.environ\.get\(\"RB5S6S_WORKERS\", \"8\"\)\)\)\))", src)
    assert m, "the worker expression moved; re-anchor this test on it"
    import os
    os.environ["RB5S6S_WORKERS"] = "64"
    try:
        assert eval(m.group(1)) == 8, "the ten-core machine keeps two cores free"
    finally:
        os.environ.pop("RB5S6S_WORKERS", None)


def test_the_noiseless_resolved_limit_returns_the_cubic_law():
    """The verification that decides whether any row may be believed.

    With the shift resolved, no noise and the layers off, the windowed third
    cumulant must go as S0 cubed, reproducing the analytic producer's 3.000.
    This is re-runnable on purpose: the same check as a number in a commit
    message would not re-validate itself, and it is the check that located A33.
    """
    mod = _load()
    from rb5s6s.forecast import build_world_trace
    layers = {"cascade": False, "saturation": False, "stark": True,
              "bbr": False, "drift": False, "quantise": False,
              "randomise": False}
    xs, ys = [], []
    for s0 in (0.364, 1.0, 2.0):
        nu, y, _ = build_world_trace(
            1.0, s0, mod.T_C, 0, 1, np.random.default_rng(4), layers,
            positions={mod.PEAK: 0.0}, shares={mod.PEAK: 1.0},
            gamma_coll=mod.GAMMA_COLL, sigma_laser_fwhm=mod.SIGMA_LASER,
            transit_fwhm=mod.TRANSIT, power_max_w=1.0, cycles_at_max=1.0,
            drift_mhz_total=0.0, noise_frac_bright=1e-9, adc_levels=2 ** 16,
            gamma_l=0.0, resolve_shift=True, offset=0.0)
        xs.append(math.log(s0))
        ys.append(math.log(abs(mod.selfcentred_cumulant(y, 8.0, 3, grid=nu))))
    slope = float(np.polyfit(np.asarray(xs), np.asarray(ys), 1)[0])
    assert slope == pytest.approx(3.0, abs=0.05), slope


def test_the_unresolved_grid_biases_small_shifts_and_not_the_campaign():
    """A33 as a standing measurement, and as the REGION it applies to.

    The fitted slope alone would mislead: it mixes rungs. Rung by rung the
    unresolved grid overstates the third cumulant by 68 per cent at S0 = 0.18,
    reads 5 per cent low at the archive's 0.364, and is exact at 1.0 and above
    -- so the campaign's own regime is untouched and the archive's is not.
    Guarding the structure rather than one number is what stops this being
    restated as "the twin is biased", which is the overstatement it replaced.
    """
    mod = _load()
    from rb5s6s.forecast import build_world_trace
    layers = {"cascade": False, "saturation": False, "stark": True,
              "bbr": False, "drift": False, "quantise": False,
              "randomise": False}

    def k3(s0, resolve):
        nu, y, _ = build_world_trace(
            1.0, s0, mod.T_C, 0, 1, np.random.default_rng(4), layers,
            positions={mod.PEAK: 0.0}, shares={mod.PEAK: 1.0},
            gamma_coll=mod.GAMMA_COLL, sigma_laser_fwhm=mod.SIGMA_LASER,
            transit_fwhm=mod.TRANSIT, power_max_w=1.0, cycles_at_max=1.0,
            drift_mhz_total=0.0, noise_frac_bright=1e-9, adc_levels=2 ** 16,
            gamma_l=0.0, resolve_shift=resolve, offset=0.0)
        return mod.selfcentred_cumulant(y, 8.0, 3, grid=nu)

    # small shift: the unresolved grid is badly wrong
    assert k3(0.18, False) / k3(0.18, True) > 1.3
    # the campaign's regime: resolving the shift changes nothing
    for s0 in (1.0, 2.0):
        assert k3(s0, False) == pytest.approx(k3(s0, True), rel=1e-6), s0


def test_the_default_generator_path_is_unchanged_by_the_new_switch():
    """The opt-in must be a true no-op at its default, and NOT a no-op when on.

    Both halves matter. A switch that changes nothing when thrown is the trap
    this record has hit before, and a switch that changes something at its
    default would move every committed CSV in the commit that introduced it.
    """
    from rb5s6s.forecast import build_world_trace
    layers = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
              "drift": False, "quantise": True, "randomise": False}
    kw = dict(positions={"4192": 0.0}, shares={"4192": 1.0}, gamma_coll=0.55,
              sigma_laser_fwhm=1.6, transit_fwhm=0.9575, power_max_w=1.0,
              cycles_at_max=1.0, drift_mhz_total=0.0, noise_frac_bright=0.004,
              adc_levels=4096)

    def trace(**extra):
        return build_world_trace(1.0, 0.364, 130.0, 0, 1,
                                 np.random.default_rng(7), layers,
                                 **kw, **extra)[1]

    assert np.array_equal(trace(), trace(resolve_shift=False))
    assert not np.array_equal(trace(), trace(resolve_shift=True))
