"""The four-peak design's rows carry the contrasts the record can read.

FAILURE MODE IF THIS FILE IS DELETED: the producer's isotope law could drift
from the constants it must reproduce, and a contrast row could lack its
prediction or its error without anything noticing; the pooled rows are what
the plan reads for the P- and N-dependence signature.
"""
import csv
import math
from pathlib import Path

import pytest

from rb5s6s import constants as K

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "four_peak_contrasts.csv"


def _rows():
    if not CSV.is_file():
        pytest.skip("results/four_peak_contrasts.csv not committed yet")
    return list(csv.DictReader(CSV.open(encoding="utf-8")))


def test_the_isotope_law_is_the_root_of_the_mass_ratio():
    rows = _rows()
    law = next(r for r in rows if r["quantity"] == "predicted_isotope_contrast")
    assert abs(float(law["value"]) - (math.sqrt(K.M_RB87_KG / K.M_RB85_KG) - 1.0)) < 1e-5


def test_every_contrast_carries_an_error_and_a_pooled_row():
    rows = _rows()
    for name in ("isotope", "F87", "F85", "interaction"):
        per = [r for r in rows if r["quantity"] == f"contrast_{name}" and not r["key"].startswith("pooled")]
        pooled = [r for r in rows if r["quantity"] == f"contrast_{name}" and r["key"].startswith("pooled")]
        assert per and pooled, name
        assert all(r["err"].strip() for r in per + pooled), f"{name}: an errless contrast"
        assert all("predicted" in r["note"] for r in per), f"{name}: a contrast without its prediction"


def test_the_branching_differences_are_the_cascade_tables():
    from rb5s6s.cascade import BRANCHING_F
    rows = _rows()
    b87 = next(r for r in rows if r["quantity"] == "branching_difference" and r["key"] == "87Rb_F2_minus_F1")
    assert abs(float(b87["value"]) - (BRANCHING_F["4207"] - BRANCHING_F["4121"])) < 1e-4


def test_the_amplitude_face_is_carried_with_its_sign_and_its_bar():
    """The F-dependent term has two faces: the width contrasts and the
    amplitudes' deviation from the thermal law. FAILS when the predicted face
    lacks its sign (the higher-branching line is depleted more, so the ratio
    sits above the thermal law), when the cycles stop growing with power, or
    when a measured row lacks its statistical error or the note naming the
    record's between-block systematic as the bar."""
    rows = _rows()
    pred = [r for r in rows if r["quantity"] == "amplitude_face_predicted"]
    meas = [r for r in rows if r["quantity"] == "amplitude_face_measured"]
    cyc = [r for r in rows if r["quantity"] == "cycles_per_crossing_axis" and r["key"].endswith("_w64")]
    assert pred and meas and len(cyc) == 5
    assert all(float(r["value"]) > 0 for r in pred)
    vals = [float(r["value"]) for r in cyc]
    assert vals == sorted(vals) and vals[-1] > 10 * vals[0]
    assert all(r["err"].strip() and "between-block systematic" in r["note"] for r in meas)
