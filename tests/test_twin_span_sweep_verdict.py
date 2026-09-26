"""F552: the span sweep's claim row is computed from its own moves, never written as a constant.

Until V7.1 `run_twin_span_sweep.py` wrote DEGENERACY_IS_A_LINESHAPE_PROPERTY whatever its moves read, and the table
rebuilt at the calculated waist carried the correlation moving by 0.15 at ten times the traces under that claim. Two
halves: `_verdict` names a different claim for each of its four cases (so a claim cannot outlive the reading that
refutes it), and the committed table's claim is the one `_verdict` names from the table's own z rows."""
import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _producer():
    spec = importlib.util.spec_from_file_location("run_twin_span_sweep", ROOT / "scripts" / "run_twin_span_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_reading_names_its_own_claim():
    mod = _producer()
    claims = {mod._verdict(a, b)[0] for a in (True, False) for b in (True, False)}
    assert len(claims) == 4
    assert mod._verdict(True, True)[0] == "DEGENERACY_IS_A_LINESHAPE_PROPERTY"
    assert mod._verdict(True, False)[0] != "DEGENERACY_IS_A_LINESHAPE_PROPERTY"


def test_the_committed_claim_is_the_one_its_own_moves_name():
    mod = _producer()
    path = ROOT / "results" / "twin_span_sweep.csv"
    if not path.exists():
        pytest.skip("twin_span_sweep.csv not present")
    rows = {(r["scope"], r["quantity"]): r["value"] for r in csv.DictReader(path.open())}
    z_span = float(rows[("VERDICT", "corr_move_with_span_z")])
    z_n = float(rows[("VERDICT", "corr_move_with_traces_z")])
    d_span = float(rows[("VERDICT", "pin_change_with_span")])
    d_n = float(rows[("VERDICT", "pin_change_with_traces")])
    want = mod._verdict(mod._inert(z_span, d_span), mod._inert(z_n, d_n))[0]
    assert rows[("VERDICT", "claim")] == want


def test_a_move_counts_only_when_resolved_and_material():
    """The instance that earned the second test: 47 standard errors and a 6 per cent change is inert."""
    mod = _producer()
    assert mod._inert(47.0, 0.061)
    assert mod._inert(1.0, 0.5)
    assert not mod._inert(47.0, -0.2)


def test_the_pin_factor_is_the_conditioning_arithmetic():
    mod = _producer()
    assert mod._pin_factor(0.0) == 1.0
    assert abs(mod._pin_factor(-0.8) - 1.0 / 0.6) < 1e-12
    assert mod._pin_factor(-0.8) == mod._pin_factor(0.8)
