"""A ratchet on frequency-like rows that do not name their axis.

WHY THIS EXISTS. A frequency-like number is correct under the convention it was
computed in and wrong under the other, and every local check passes either way.
The species has now appeared four times in this repository: a discrete trim
boundary, the laser_kind default, the quadratic-Zeeman coefficients (quoted
transition-axis in the literature while a laser width budget needs the
laser-axis halves), and a cold-atom transit width computed with a Gaussian-beam
convention and scaled onto an exponential profile. Rule 19.88 names the
species; this file mechanises what can be mechanised.

WHY A RATCHET AND NOT A BAN. Twenty rows in the settings family carry a
frequency unit and three name an axis. A hard requirement would fail on its
first run and be switched off on its second, which is the failure mode the
prose ratchet in this repository was built to avoid. So this records a
per-file budget of unlabelled rows and fails only when a file gets WORSE.
The budget can only fall, which makes the repository monotonically more
explicit without demanding one large rewrite first.

WHAT COUNTS AS NAMING AN AXIS. The row says "transition axis" or "laser axis"
anywhere in its note or unit, in either spelling. The two-photon detuning sums
both photons, so a width on the laser axis is half the same width on the
transition axis, and a reader who cannot tell which one a row means cannot use
the number at all.

LOWERING THE NUMBERS IS THE WORK. Add the axis to a row's note, then re-record
with `python tests/test_axis_ratchet.py --relax`.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "_axis_baseline.json"

# Files whose rows carry apparatus and settings numbers a reader converts by
# hand. Fit outputs are excluded: their axis is fixed by the pipeline and
# stated once in the methods chapter rather than per row.
WATCHED = ("onf_candidate.csv",)

_FREQ_UNIT = re.compile(r"\b(m?k?M?G?Hz)\b")
_AXIS = re.compile(r"(transition|laser)[ _-]axis", re.I)


def _unlabelled(rel: str) -> list[str]:
    path = ROOT / "results" / rel
    if not path.exists():
        return []
    out = []
    with path.open() as fh:
        for row in csv.DictReader(fh):
            unit = (row.get("unit") or "")
            if not _FREQ_UNIT.search(unit):
                continue
            blob = " ".join(str(v) for v in row.values() if v)
            if not _AXIS.search(blob):
                out.append(row.get("quantity") or "?")
    return out


def _budget() -> dict:
    if BASELINE.exists():
        return json.loads(BASELINE.read_text())
    return {}


@pytest.mark.parametrize("rel", WATCHED)
def test_axis_labelling_does_not_get_worse(rel):
    """The count of frequency-like rows with no axis may fall, never rise."""
    now = _unlabelled(rel)
    allowed = _budget().get(rel)
    assert allowed is not None, (
        f"results/{rel} has no recorded axis budget. Record one with "
        f"`python {Path(__file__).name} --relax`.")
    assert len(now) <= allowed, (
        f"results/{rel}: {len(now)} frequency-like rows name no axis, budget "
        f"is {allowed}. New unlabelled rows: {now[:8]}. A frequency-like "
        "number travels with its axis (rule 19.88): on the transition axis a "
        "width is twice the same width on the laser axis, and nothing else in "
        "the row says which one is meant.")


@pytest.mark.parametrize("rel", WATCHED)
def test_the_budget_is_not_slack(rel):
    """A budget above what the file needs would let a regression in unseen."""
    now = _unlabelled(rel)
    allowed = _budget().get(rel)
    if allowed is None:
        pytest.skip("no budget recorded")
    assert allowed == len(now), (
        f"results/{rel}: budget {allowed} but only {len(now)} rows are "
        "unlabelled. Re-record so the ratchet bites at the current state.")


def test_the_guard_can_actually_fire():
    """A ratchet that matches nothing is not a ratchet.

    Ceiling test: a synthetic row with a frequency unit and no axis must be
    counted, and the same row with an axis must not be.
    """
    blob_no_axis = {"quantity": "x", "unit": "kHz", "note": "a width"}
    blob_axis = {"quantity": "x", "unit": "kHz", "note": "a width, laser axis"}
    assert _FREQ_UNIT.search(blob_no_axis["unit"])
    assert not _AXIS.search(" ".join(blob_no_axis.values()))
    assert _AXIS.search(" ".join(blob_axis.values()))


if __name__ == "__main__":
    BASELINE.write_text(json.dumps(
        {rel: len(_unlabelled(rel)) for rel in WATCHED}, indent=1) + "\n")
    for rel in WATCHED:
        print(f"{rel}: {len(_unlabelled(rel))} unlabelled")
