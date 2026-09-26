"""Guards for `scripts/run_moment_power_map.py`, the moment-power map.

WHY EACH TEST IS HERE. The producer measures the power of S0 that each windowed
odd moment carries, across the Lorentzian component, the noise level, the
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

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "a unit test of the generator's own arithmetic, not a quoted number"

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
    moment must go as S0 cubed, reproducing the analytic producer's 3.000.
    This is re-runnable on purpose: the same check as a number in a commit
    message would not re-validate itself, and it is the check that located A33.
    """
    mod = _load()
    from rb5s6s.forecast import build_world_trace
    layers = {"cascade": False, "saturation": False, "stark": True,
              "bbr": False, "drift": False, "quantise": False,
              "randomise": False}
    xs, ys = [], []
    for s0 in (0.364, 1.0, 2.0):   # the producer's ladder rungs, a design of its date
        nu, y, _ = build_world_trace(
            1.0, s0, mod.T_C, 0, 1, np.random.default_rng(4), layers,
            positions={mod.PEAK: 0.0}, shares={mod.PEAK: 1.0},
            gamma_coll=mod.GAMMA_COLL, sigma_laser_fwhm=mod.SIGMA_LASER,
            transit_fwhm=mod.TRANSIT, power_max_w=1.0, cycles_at_max=1.0,
            drift_mhz_total=0.0, noise_frac_bright=1e-9, adc_levels=2 ** 16,
            gamma_l=0.0, resolve_shift=True, offset=0.0, registry=_TWIN_STUDY)
        xs.append(math.log(s0))
        ys.append(math.log(abs(mod.selfcentred_moment(y, 8.0, 3, grid=nu))))
    slope = float(np.polyfit(np.asarray(xs), np.asarray(ys), 1)[0])
    assert slope == pytest.approx(3.0, abs=0.05), slope


def test_the_unresolved_grid_biases_small_shifts_and_not_the_campaign():
    """A33 as a standing measurement, and as the REGION it applies to.

    The fitted slope alone would mislead: it mixes rungs. At the retired waist convention, until
    2026-09-22, the unresolved grid overstated the third moment by 68 per cent at S0 = 0.18 and read
    5 per cent low at the 0.364 rung. At the ruled waist the line is wider (its transit 1.45 MHz), the
    grid is resolved further down, and the bias region moves to smaller shifts: a factor 4.3 at
    S0 = 0.02 and a sign flip at 0.05, 9 per cent low at 0.1, within 2 per cent from 0.18 up, exact at
    1.0 and above (2026-09-24). The campaign's own regime is untouched either way. Guarding the
    structure rather than one number is what stops this being restated as "the twin is biased",
    which is the overstatement it replaced.
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
            gamma_l=0.0, resolve_shift=resolve, offset=0.0, registry=_TWIN_STUDY)
        return mod.selfcentred_moment(y, 8.0, 3, grid=nu)

    # small shift: the unresolved grid is badly wrong (at the ruled waist, below about 0.05 MHz)
    assert k3(0.02, False) / k3(0.02, True) > 1.3
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
                                 **kw, **extra, registry=_TWIN_STUDY)[1]

    assert np.array_equal(trace(), trace(resolve_shift=False))
    assert not np.array_equal(trace(), trace(resolve_shift=True))


def test_the_rung_status_reads_the_sign_against_the_true_sign_and_never_against_zero():
    """The defect the deep-producer board found (two seats): the first status
    rule tagged every settled fifth-order rung NULL because it keyed on the
    fraction NEGATIVE while the fifth cumulant's true sign is positive (the
    table read cumulant signs then; owner order O49, 2026-09-22, moved it to
    the moment basis the producer's own quadrature already used, and mu_5's
    sign is negative, opposite the cumulant's -- see test_the_true_signs_are_the_ramps_own).
    The rule now keys on the fraction with the WRONG sign, published to three
    decimals, and is re-derived from the file's own columns below."""
    mod = _load()
    from rb5s6s.lineshape import RAMP_SIDE
    assert mod.TRUE_SIGN == {3: -RAMP_SIDE, 5: -RAMP_SIDE, 7: -RAMP_SIDE}
    assert mod.rung_status(0.004) == "DIAGNOSTIC"          # a settled sign
    assert mod.rung_status(0.349) == "DIAGNOSTIC"
    assert mod.rung_status(0.35) == "NULL"                 # the bar itself is not admitted
    assert mod.rung_status(0.5) == "NULL"                  # a coin flip
    assert mod.rung_status(0.996) == "NULL"                # settled on the WRONG side is not a measurement
    assert mod.rung_status(float("nan")) == "NULL"
    # the published value decides, not the unrounded one: 0.3494 rounds to 0.349
    assert mod.rung_status(0.3494) == "DIAGNOSTIC" and mod.rung_status(0.3496) == "NULL"


def test_the_true_signs_are_the_ramps_own():
    """Failure: the sign table drifts from the physics it encodes. TRUE_SIGN is read
    against the CENTRAL MOMENT (owner order O49, 2026-09-22: the producer's own quadrature,
    `windowed_orders`, returns moments through `windowed_moments`, and the table must match
    what is actually compared against it, never a different basis). The ramp's density
    2|s|/S0^2 on the package's side (lineshape.RAMP_SIDE, blue since the ruling of 2026-09-17)
    gives mu_3 negative and mu_7 negative, same sign as their cumulants (mu_3 == kappa_3
    exactly; mu_7 and kappa_7 merely agree in sign for this shape), but mu_5 negative where
    kappa_5 is positive: kappa_5 = mu_5 - 10 mu_2 mu_3 EXACTLY, so mu_5 = kappa_5 + 10 mu_2 mu_3
    = 1/567 + 10 (1/18)(-1/135) = -4/1701, the cross-term's sign prevailing over kappa_5's own.
    The density is built on RAMP_SIDE and not by hand: this test built the red side itself
    and so agreed with a table the kernel had left (P3)."""
    from rb5s6s._compat import trapezoid          # the seam, never the numpy name
    mod = _load()
    from rb5s6s.lineshape import RAMP_SIDE
    x = np.linspace(0.0, 1.0, 200001); f = 2.0 * x; f /= trapezoid(f, x); s = RAMP_SIDE * x
    m1 = trapezoid(s * f, x)
    mu = {k: trapezoid((s - m1) ** k * f, x) for k in range(1, 8)}
    for order, sign in mod.TRUE_SIGN.items():
        assert np.sign(mu[order]) == sign, (order, mu[order])
    # mu_5's exact closed form at this S0 = 1, so a future re-measurement has something to
    # check against (RAMP_SIDE flips the sign, an odd order, never its magnitude)
    assert mu[5] == pytest.approx(RAMP_SIDE * (-4.0 / 1701.0), rel=1e-6)


def test_every_committed_rung_status_is_re_derivable_from_its_own_columns():
    """The prevention two seats asked for: a producer-written status that
    nothing re-derives is a claim nobody grades. For both committed per-rung
    files, the status must equal the rule applied to the published
    frac_wrong_sign, and a settled fifth-order rung must not read NULL."""
    import csv
    mod = _load()
    for name in ("moment_power_map_rungs.csv", "moment_power_map_deep_rungs.csv"):
        path = ROOT / "results" / name
        # NOT `continue`: a guard whose subject is absent passes on nothing,
        # which is the commonest class in this record and was named inside
        # this very test by a round-two seat.
        assert path.exists(), f"{path.name} is missing, so this guard would grade nothing"
        rows = list(csv.DictReader(open(path)))
        assert rows and "frac_wrong_sign" in rows[0], name
        bad = [r for r in rows if mod.rung_status(float(r["frac_wrong_sign"])) != r["status"]]
        assert not bad, (name, bad[:3])
        settled5 = [r for r in rows if r["order"] == "5" and float(r["frac_wrong_sign"]) < 0.05]
        assert all(r["status"] == "DIAGNOSTIC" for r in settled5), name


def test_the_deep_wrapper_is_guarded_and_sets_its_trace_count():
    """Failure: importing the wrapper launches a ninety-minute grid, or an
    inherited environment silently changes the file it writes."""
    src = (ROOT / "scripts" / "run_moment_power_map_deep.py").read_text()
    assert 'if __name__ == "__main__":' in src
    assert 'os.environ["RB5S6S_MPM_TRACES"] = "40000"' in src
    assert "os.environ.setdefault" not in src


def test_the_deep_grid_starts_at_the_2025_rung_and_has_twenty_four_cells(monkeypatch):
    """Failure: the deep arm drifts while only the shallow arm is graded (a
    three-point plant passed against the old suite)."""
    monkeypatch.setenv("RB5S6S_MPM_DEEP", "1")
    spec = importlib.util.spec_from_file_location("_mpm_deep", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.S0_LADDER[0] == 0.364 and len(mod.S0_LADDER) == 5
    cells = mod._grid()
    assert len(cells) == 24
    assert {c[1] for c in cells} == {0.004} and {c[4] for c in cells} == {True}
    assert {c[2][0] for c in cells} == {"rtm3004"}


def test_the_rung_notes_typed_threshold_still_matches_the_constant_that_governs_it():
    """The note in every rung row types 0.35 and two sigma distances.

    Nothing computed them, so moving `WRONG_SIGN_MAX` or `N_TRACES` would leave
    thousands of published cells asserting a retired bar. Computing the note
    instead would change every row and cost a regeneration of both maps for a
    sentence, so the note stays typed and this guard ties it to the constants:
    it fails the moment they diverge, and the fix is the regeneration the
    change would need anyway.
    """
    import math
    import re
    src = SCRIPT.read_text(encoding="utf-8")
    mod = _load()
    m = re.search(r"frac_sign_sign is below|frac_wrong_sign is below ([0-9.]+)", src)
    assert m and float(m.group(1)) == mod.WRONG_SIGN_MAX, (m and m.group(1), mod.WRONG_SIGN_MAX)
    for n, typed in ((2000, 13), (40000, 60)):
        want = (0.5 - mod.WRONG_SIGN_MAX) / (0.5 / math.sqrt(n))
        assert round(want) == typed, (n, want, typed)
    assert mod.N_TRACES == 2000, "the shallow arm's own trace count is the first figure the note names"
