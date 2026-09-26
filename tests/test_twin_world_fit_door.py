"""The twin's world/fitter door (F559, F560, 2026-09-26): a synthetic trace carries the world it was drawn from, the
twin's fitter refuses a world it does not describe, and no twin harness calls the fitter around the door.

Each refusal is planted on its own defect's instance and both ways: F560's world drawn at 110 C and fitted at 130 C;
F559's separable world fitted by the joint fitter; the transit a joint fitter never reads, which left the coverage
grid's broken-kernel plant inert; a declared reason at its minimum length and one word short of it; a trace with no
world; and the tag surviving what the harnesses do to a trace before they fit it.
"""
import ast
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import forecast as F
from rb5s6s.forecast import (MIN_WORLD_REASON_WORDS, WorldFitterMismatch, WorldTrace, build_world_trace,
                             check_world_fit, fit_world, synthetic_traces, world_disagreements)

ROOT = Path(__file__).resolve().parents[1]
FIT_DEFAULTS = F._defaults(F.fit_condition)

#: the generators whose traces carry a world, and the fitters a twin harness reaches only through the door
GENERATORS = {"synthetic_traces", "build_world_trace"}
BARE_FITTERS = {"fit_condition", "fit_beta_self"}
#: where the door itself and the fitters live, so their own calls are not a harness's
DOOR_HOMES = {"rb5s6s/forecast.py", "rb5s6s/linefit.py", "rb5s6s/beta.py"}
#: the registry reads a twin run with layers off as a study, and this is one: a tag check on a reduced world
_TWIN_STUDY = "the world door's own plant, a tag check on a reduced world"


def _joint(T=130.0, s0=0.0, **over):
    w = {"form": "joint", "T_C": T, "s0": s0, "w0_m": FIT_DEFAULTS["w0_m"], "m2": FIT_DEFAULTS["m2"],
         "z_ratio": FIT_DEFAULTS["z_ratio"], "transit_fwhm": None, "laser_kind": "gaussian", "gamma_l": 0.0}
    w.update(over)
    return w


def _fit(**over):
    kw = dict(model=FIT_DEFAULTS["model"], T_C=130.0, s0=FIT_DEFAULTS["s0"], w0_m=FIT_DEFAULTS["w0_m"],
              m2=FIT_DEFAULTS["m2"], z_ratio=FIT_DEFAULTS["z_ratio"], transit_fwhm=FIT_DEFAULTS["transit_fwhm"],
              fit_transit=FIT_DEFAULTS["fit_transit"], transit_default=FIT_DEFAULTS["transit_fwhm"],
              laser_kind=FIT_DEFAULTS["laser_kind"], gamma_l=FIT_DEFAULTS["gamma_l"],
              fit_gamma_l=FIT_DEFAULTS["fit_gamma_l"])
    kw.update(over)
    return kw


def _trace(world, n=64):
    return WorldTrace(np.linspace(0.0, 1.0, n), world)


def test_a_world_the_fitter_describes_passes():
    assert world_disagreements(_joint(), **_fit()) == []
    assert check_world_fit([_trace(_joint())] * 3, where="t", reason=None, **_fit()) == []


def test_f560_a_world_drawn_at_110_c_and_fitted_at_130_c_is_refused():
    msgs = world_disagreements(_joint(T=110.0), **_fit(T_C=130.0))
    assert len(msgs) == 1 and "temperature" in msgs[0] and "F560" in msgs[0], msgs
    with pytest.raises(WorldFitterMismatch, match="110"):
        check_world_fit([_trace(_joint(T=110.0))], where="t", reason=None, **_fit(T_C=130.0))


def test_f559_a_separable_world_is_refused_by_the_joint_fitter_and_passed_by_its_own():
    sep = {"form": "separable", "T_C": 130.0, "s0": 0.3, "w0_m": None, "m2": 1.0, "z_ratio": None,
           "transit_fwhm": 0.96}
    msgs = world_disagreements(sep, **_fit(s0=0.3))
    assert len(msgs) == 1 and "form" in msgs[0] and "F559" in msgs[0], msgs
    assert world_disagreements(sep, **_fit(model="convolution", s0=0.3, transit_fwhm=0.96)) == []
    # and the separable world's own keys still bind under its own form
    assert any("transit" in m for m in world_disagreements(sep, **_fit(model="convolution", s0=0.3,
                                                                       transit_fwhm=0.48)))


def test_the_joint_worlds_beam_and_window_and_shift_bind():
    for key, other in (("w0_m", FIT_DEFAULTS["w0_m"] * 1.1), ("m2", 1.3), ("z_ratio", 0.3)):
        msgs = world_disagreements(_joint(**{key: other}), **_fit())
        assert len(msgs) == 1 and key in msgs[0], (key, msgs)
    msgs = world_disagreements(_joint(s0=0.6), **_fit())
    assert len(msgs) == 1 and "shift" in msgs[0], msgs


def test_the_laser_kernel_and_a_fixed_gas_width_bind_and_a_free_one_does_not():
    """V7.2's board (the physics seat): the coverage grid's Lorentzian and form-flip rows passed undeclared."""
    msgs = world_disagreements(_joint(laser_kind="lorentzian"), **_fit())
    assert len(msgs) == 1 and "laser kernel" in msgs[0], msgs
    msgs = world_disagreements(_joint(gamma_l=0.3), **_fit())
    assert len(msgs) == 1 and "gas width" in msgs[0], msgs
    assert world_disagreements(_joint(gamma_l=0.3), **_fit(fit_gamma_l=True)) == []


def test_a_transit_passed_to_the_joint_fitter_is_refused_as_unread():
    """The coverage grid's broken-kernel plant halved an injected transit that neither the joint world nor the joint
    fitter reads, so the leg's own gage could not fail: the door names the no-op."""
    msgs = world_disagreements(_joint(), **_fit(transit_fwhm=FIT_DEFAULTS["transit_fwhm"] / 2.0))
    assert len(msgs) == 1 and "never reads" in msgs[0], msgs


def test_a_declared_reason_admits_only_its_own_kind_and_only_at_its_length():
    """V7.2's board (the twin seat): a ramp-only reason admitted a world with its temperature wrong too."""
    world, fit = _joint(s0=0.6), _fit()
    ok = " ".join(["word"] * MIN_WORLD_REASON_WORDS)
    assert check_world_fit([_trace(world)], where="t", reason={"shift": ok}, **fit)
    short = " ".join(["word"] * (MIN_WORLD_REASON_WORDS - 1))
    with pytest.raises(WorldFitterMismatch, match="naming each kind"):
        check_world_fit([_trace(world)], where="t", reason={"shift": short}, **fit)
    with pytest.raises(WorldFitterMismatch, match="temperature"):
        check_world_fit([_trace(_joint(T=110.0, s0=0.6))], where="t", reason={"shift": ok}, **_fit(T_C=130.0))
    with pytest.raises(WorldFitterMismatch, match="keyed by the disagreement"):
        check_world_fit([_trace(world)], where="t", reason=ok, **fit)
    # across forms the kinds that do not depend on the form are still read
    sep = {"form": "separable", "T_C": 110.0, "s0": 0.0, "transit_fwhm": 0.96}
    msgs = world_disagreements(sep, **_fit(T_C=130.0))
    assert [m.split(":")[0] for m in msgs] == ["form", "temperature"], msgs


def test_a_trace_with_no_world_is_refused_whatever_the_reason():
    ok = {"shift": " ".join(["word"] * MIN_WORLD_REASON_WORDS)}
    with pytest.raises(WorldFitterMismatch, match="carry no world"):
        check_world_fit([np.linspace(0.0, 1.0, 8)], where="t", reason=ok, **_fit())
    with pytest.raises(WorldFitterMismatch, match="carry no world"):
        check_world_fit([np.asarray(_trace(_joint()))], where="t", reason=None, **_fit())


def test_an_array_added_after_the_draw_is_refused_and_a_scalar_is_not():
    """V7.2's board (the physics seat): world C of the kernel worlds added a quadratic tilt after the draw and the
    tag, which then recorded only the generator's arguments, passed it. An array operation now marks the world, a
    scalar one does not, and a declared reason still admits the marked world."""
    v = _trace(_joint())
    tilted = v + 2.0e-5 * np.linspace(-1.0, 1.0, v.size) ** 2
    assert tilted.world.get("post_draw") is True and v.world.get("post_draw") is None
    with pytest.raises(WorldFitterMismatch, match="post-draw"):
        check_world_fit([tilted], where="t", reason=None, **_fit())
    ok = {"post-draw": " ".join(["word"] * MIN_WORLD_REASON_WORDS)}
    assert check_world_fit([tilted], where="t", reason=ok, **_fit())
    scaled = np.round(1.07 * v + 0.01, 6)
    assert "post_draw" not in scaled.world and check_world_fit([scaled], where="t", reason=None, **_fit()) == []
    acc = v.copy()
    acc += np.linspace(0.0, 1e-3, v.size)
    assert acc.world.get("post_draw") is True, "an in-place array operation marks the world too"


def test_fit_world_refuses_before_it_fits():
    freqs = [np.linspace(-5.0, 5.0, 64)]
    with pytest.raises(WorldFitterMismatch, match="F560"):
        fit_world(freqs, [_trace(_joint(T=110.0))], T_C=130.0)


def test_the_tag_survives_what_a_harness_does_to_a_trace():
    v = _trace(_joint(T=90.0))
    m = np.abs(np.linspace(-1.0, 1.0, v.size)) < 0.5
    for label, got in (("mask", v[m]), ("slice", v[3:]), ("arith", 2.0 * v - 0.01), ("round", np.round(v * 4096)),
                       ("pickle", pickle.loads(pickle.dumps(v)))):
        assert isinstance(got, WorldTrace) and got.world["T_C"] == 90.0, label
    assert type(v.max()) is np.float64 and type(v.sum()) is np.float64
    assert not isinstance(np.asarray(v), WorldTrace)


def test_both_generators_tag_what_they_draw():
    rng = np.random.default_rng(0)
    _, conv = synthetic_traces(0.2, 0.5, 0.96, n_traces=2, n_points=200, model="convolution", rng=rng,
                               registry=_TWIN_STUDY)
    assert all(isinstance(v, WorldTrace) for v in conv)
    assert conv[0].world["form"] == "convolution" and conv[0].world["transit_fwhm"] == 0.96
    _, joint = synthetic_traces(0.2, 0.5, 0.96, n_traces=1, n_points=200, span_mhz=20.0, model="joint",
                                T_C=90.0, n_path=400, rng=rng, registry=_TWIN_STUDY)
    assert joint[0].world["form"] == "joint" and joint[0].world["T_C"] == 90.0
    layers = {"cascade": False, "saturation": False, "stark": False, "bbr": False, "drift": False, "quantise": False}
    nu, v, _ = build_world_trace(0.1, 0.0, 130.0, 0, 1, rng, layers, positions={"4121": 0.0},
                                 shares={"4121": 1.0}, gamma_coll=0.2, sigma_laser_fwhm=0.5, transit_fwhm=0.96,
                                 power_max_w=0.1, cycles_at_max=0.0, drift_mhz_total=0.0, noise_frac_bright=0.004,
                                 adc_levels=4096, registry=_TWIN_STUDY)
    assert isinstance(v, WorldTrace) and v.world["form"] == "separable" and v.world["T_C"] == 130.0
    assert v.world["transit_fwhm"] == 0.96 and v.world["s0"] == 0.0


def _calls(tree) -> set:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if name:
                out.add(name)
    return out


def harnesses_around_the_door(sources: dict) -> list:
    """Every source that calls a twin generator AND a bare fitter: a twin harness fitting around the door. Read on
    the syntax tree, so a name in a comment or a docstring is not a call."""
    bad = []
    for rel, text in sorted(sources.items()):
        if rel in DOOR_HOMES:
            continue
        try:
            calls = _calls(ast.parse(text))
        except SyntaxError:
            continue
        if calls & GENERATORS and calls & BARE_FITTERS:
            bad.append(f"{rel}: {sorted(calls & GENERATORS)} fitted by {sorted(calls & BARE_FITTERS)}")
    return bad


def test_the_scan_is_planted_both_ways():
    around = ("from rb5s6s.forecast import synthetic_traces\nfrom rb5s6s.linefit import fit_condition\n"
              "f, v = synthetic_traces(0.2, 0.5, 1.0, T_C=130.0)\nfit_condition(f, v, T_C=130.0)\n")
    through = around.replace("fit_condition(f", "fit_world(f")
    mention = '"""synthetic_traces( then fit_condition( in words"""\nx = 1\n'
    got = harnesses_around_the_door({"scripts/a.py": around, "scripts/b.py": through, "scripts/c.py": mention,
                                     "rb5s6s/forecast.py": around})
    assert got == ["scripts/a.py: ['synthetic_traces'] fitted by ['fit_condition']"], got


def test_no_twin_harness_fits_around_the_door():
    files = subprocess.run(["git", "ls-files", "scripts/*.py", "examples/*.py", "rb5s6s/*.py"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    sources = {}
    for rel in files:
        p = ROOT / rel
        if p.exists():
            sources[rel] = p.read_text(encoding="utf-8", errors="ignore")
    assert len(sources) > 50, len(sources)
    bad = harnesses_around_the_door(sources)
    assert not bad, ("a twin harness calls the fitter around the world door; fit through forecast.fit_world or "
                     "forecast.fit_world_beta:\n  " + "\n  ".join(bad))
