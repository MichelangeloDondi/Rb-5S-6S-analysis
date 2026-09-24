"""The kernel Monte Carlo gate: a node of the full model is used only after its Monte Carlo
agrees with it (owner, 2026-09-16). Every refusal is planted through the gate's real call path
with a temporary cache, and the interpolation between two validated nodes is checked against
its own arithmetic. FAILURE MODE: a refusal that stops firing here is a fit evaluating the full
model at a node nothing validated."""
import json
import math

import pytest

from rb5s6s import kernel_gate as G


def _pass_readings():
    return {name: {"mc": (0.0 if name.endswith("_abs") else 1.0), "model": (0.0 if name.endswith("_abs") else 1.0),
                   **({"grid_movement": 0.0} if name == "ramp_k3_rel" else {})}
            for name in G.READINGS}


def _write(cache, w0, widening, verdict_ok=True):
    r = _pass_readings()
    if not verdict_ok:
        r["transit_fwhm_rel"] = {"mc": 1.1, "model": 1.0}
    key = G.node_key(w0, 1.0, 0.94, 130.0, 225.0)
    G.record_node(key, r, detail={"node": {}, "depletion_widening_rel": {"4121": widening, "4154": widening, "4192": widening, "4207": widening},
                                  "depletion_fwhm_rel": {"4121": 10 * widening}, "depletion_note": "plant"}, cache=cache)
    return key


def test_the_gates_own_plants_pass():
    assert G._self_test() == []


def test_a_node_without_an_artefact_is_refused(tmp_path):
    with pytest.raises(G.KernelUnvalidated):
        G.require_node(G.node_key(60.0), tmp_path)


def test_an_artefact_written_against_another_model_is_refused(tmp_path):
    key = _write(tmp_path, 60.0, 0.05)
    f = G.mc_dir(tmp_path) / f"{key}.json"
    row = json.loads(f.read_text()); row["model_sha"] = "0" * 16; f.write_text(json.dumps(row))
    with pytest.raises(G.KernelUnvalidated):
        G.require_node(key, tmp_path)


def test_the_depletion_factor_interpolates_across_validated_nodes_and_refuses_otherwise(tmp_path):
    # the planted factor falls by 0.006 per 4 um, straight, as the real one nearly does (a part in
    # a thousand per micron, 2026-09-16); the bend case below is the refusal
    _write(tmp_path, 74.0, 0.052); _write(tmp_path, 78.0, 0.046)     # a 4 um gap, coarse first
    assert math.isclose(G.depletion_factor(74.0, "4121", cache=tmp_path), 1.052)
    assert math.isclose(G.depletion_factor(76.0, "4121", cache=tmp_path), 1.049)
    assert math.isclose(G.depletion_factor(75.0, "4121", cache=tmp_path), 1.0505)
    with pytest.raises(G.KernelUnvalidated):          # outside the validated span
        G.depletion_factor(73.0, "4121", cache=tmp_path)
    _write(tmp_path, 90.0, 0.028)                     # a 12 um gap is over the bound
    with pytest.raises(G.KernelUnvalidated):
        G.depletion_factor(84.0, "4121", cache=tmp_path)
    _write(tmp_path, 82.0, 0.040); _write(tmp_path, 86.0, 0.034)
    assert math.isclose(G.depletion_factor(84.0, "4121", cache=tmp_path), 1.037)
    _write(tmp_path, 94.0, 0.010); _write(tmp_path, 98.0, 0.030)     # a bend over the tolerance refuses
    with pytest.raises(G.KernelUnvalidated):
        G.depletion_factor(96.0, "4121", cache=tmp_path)
    _write(tmp_path, 80.0, 0.030, verdict_ok=False)   # a FAILING node is simply not a validated one: its own
    assert math.isclose(G.depletion_factor(80.0, "4121", cache=tmp_path), 1.043)   # value (0.030) is not what comes back


def test_the_fit_reaches_the_gate_through_its_own_call_path(tmp_path, monkeypatch):
    """A Cell with the gate on refuses without artefacts and admits with them: the require path
    itself, not the helper's legacy door (2026-09-17)."""
    import importlib.util
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if not (root / "data_raw" / "p_sweep").is_dir():
        pytest.skip("the raw traces are not in this checkout")
    monkeypatch.setenv("RB5S6S_KERNEL_MC_DIR", str(tmp_path))
    spec = importlib.util.spec_from_file_location("uj_gate_test", root / "scripts" / "run_ultra_joint.py")
    uj = importlib.util.module_from_spec(spec); sys.modules["uj_gate_test"] = spec.loader and spec.loader.exec_module(uj) or uj
    tr = [dict(T=130.0, P_W=0.225, iso=87, session="P", peak="4121", axis="mhz")]
    with pytest.raises(G.KernelUnvalidated):
        uj.Cell(uj._spec("mixed", 76.0), tr)
    for w in (76.0,):
        G.record_node(G.node_key(w, 1.0, 0.94, 130.0, 225.0), _pass_readings(),
                      detail={"node": {}, "depletion_widening_rel": {"4121": 0.005, "4154": 0.004, "4192": 0.003, "4207": 0.003},
                              "depletion_fwhm_rel": {"4121": 0.05}, "depletion_note": "plant"}, cache=None)
    c = uj.Cell(uj._spec("mixed", 76.0), tr)
    assert math.isclose(c.per[0]["dep"], 1.005)
