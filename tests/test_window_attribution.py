"""The between-block attribution, and the two things that could make it lie.

This number decides what the whole 2025 dataset can be asked, and it was
published on four surfaces before it had a producer. The tests below are
the ones that would have caught the ways it could be wrong rather than the
ones that confirm it is right: a fraction can be inflated by its
denominator, and a fraction of a difference can be manufactured by
correlating a series with itself.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_window_attribution as W  # noqa: E402

CSV = ROOT / "results" / "window_attribution.csv"


@pytest.fixture(scope="module")
def rows():
    if not CSV.exists():
        pytest.skip("run scripts/run_window_attribution.py")
    return {(r["quantity"], r["key"]): r for r in csv.DictReader(open(CSV))}


def test_the_headline_is_committed_and_high(rows):
    v = float(rows[("window_attributed_pct", "peak_power")]["value"])
    assert 99.0 < v <= 100.0, v


def test_the_fraction_is_not_the_grouping(rows):
    """Two groupings, and the claim is only a claim if both give it.

    The published millisecond values come from a third grouping again, so
    if the fraction moved with the cut, the record would hold three numbers
    and no measurement.
    """
    a = float(rows[("window_attributed_pct", "peak_power")]["value"])
    b = float(rows[("window_attributed_pct", "epoch_peak_power")]["value"])
    assert abs(a - b) < 0.5, (a, b)


def test_the_residual_and_the_fraction_are_the_same_statement(rows):
    """The two published numbers must be each other, or one of them is loose.

    The caption prints a fraction and the inset prints a residual, and a
    reader is entitled to assume they describe one decomposition. They do
    only if resid/move is sqrt(1 - frac), so that identity is the test
    rather than a threshold somebody chose.
    """
    resid = float(rows[("rms_residual_ms", "peak_power")]["value"])
    move = float(rows[("rms_d_peak_position_ms", "peak_power")]["value"])
    frac = float(rows[("window_attributed_pct", "peak_power")]["value"]) / 100.0
    assert resid / move == pytest.approx(np.sqrt(1.0 - frac), rel=1e-3)


def test_a_planted_atom_signal_lowers_the_fraction():
    """CEILING TEST: the measure must be able to come back low.

    A fraction near 100 per cent is only evidence if the construction can
    report 40. Feed it traces whose positions carry a large move the window
    setting does not explain, and the attributed fraction must fall.
    """
    traces = []
    rng = np.random.default_rng(20260825)
    for i in range(20):
        win = 100.0 * i
        pos = win + rng.normal(0.0, 120.0)          # a real, unexplained move
        traces.append({"peak": "4121", "power_mW": str(i), "display_epoch": "1",
                       "peak_pos_ms": str(pos), "window_start_ms": str(win),
                       "t_epoch": str(i)})
    d = W.decompose(traces, lambda r: (r["peak"], r["power_mW"]))
    assert d["attributed_pct"] < 90.0, d["attributed_pct"]


def test_an_exactly_following_peak_reads_as_all_window():
    """The other ceiling: a peak that IS the window reads 100 per cent."""
    traces = [{"peak": "4121", "power_mW": str(i), "display_epoch": "1",
               "peak_pos_ms": str(37.0 * i), "window_start_ms": str(37.0 * i),
               "t_epoch": str(i)} for i in range(12)]
    d = W.decompose(traces, lambda r: (r["peak"], r["power_mW"]))
    assert d["attributed_pct"] == pytest.approx(100.0, abs=1e-9)


def test_the_producer_is_idempotent():
    """Self-reference is not provenance: run it twice, get the same file."""
    if not CSV.exists():
        pytest.skip("run scripts/run_window_attribution.py")
    before = CSV.read_text()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "run_window_attribution.py")],
                   check=True, capture_output=True)
    assert CSV.read_text() == before
