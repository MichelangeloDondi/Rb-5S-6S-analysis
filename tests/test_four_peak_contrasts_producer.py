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

    # THE WAIST LADDER WAS UNGRADED, AND THAT IS WHERE THE DEFECT LIVED. The
    # checks above read only the five _w64 power rows, so a cycles row that FELL
    # from 25 to 16 microns passed: the closed form multiplied the saturated
    # on-axis rate by the weak-drive profile integral.
    #
    # MONOTONICITY IS NOT THE LAW, and the first version of this guard said it
    # was (2026-09-13). Weak drive gives cycles proportional to w0^-3 and strong
    # drive to w0, so the count TURNS OVER: at 225 mW it peaks near 16 microns
    # (0.7935 at 17, 0.7946 at 16, 0.7908 at 15). The committed ladder happens to
    # end at that maximum, so it was monotone by a 0.1 per cent coincidence and
    # this guard would have gone RED on a correct 15-micron cell. What the defect
    # actually violated is that the count RISES across the committed span; that
    # is what is asserted, and the turnover is left to the physics.
    ladder = [r for r in rows if r["quantity"] == "cycles_per_crossing_axis"
              and r["key"].startswith("P225_w")]
    by_waist = sorted(ladder, key=lambda r: -float(r["key"].split("_w")[1]))
    assert len(by_waist) >= 4, f"the waist ladder is {len(by_waist)} rows"
    vals_w = [float(r["value"]) for r in by_waist]
    # THE LICENCE FIRST, THEN THE SHAPE. Monotonicity holds only at or above the
    # turnover, so it is asserted only where it is true, and the licence is
    # checked so a future tighter rung fails with a message that says to revisit
    # this rather than with a bare shape error. "Rises across the span" was tried
    # and is too weak: the defective ladder rose overall (0.0805 to 0.448) and
    # fell only between the last two rungs, which is exactly what it got wrong.
    waists = [float(r["key"].split("_w")[1]) for r in by_waist]
    # THE TURNOVER IS MEASURED FROM THE PRODUCER, NOT TYPED AS 16 (corrected 2026-09-13). The previous licence asserted `min(waists) >= 16.0` and
    # called ~16 um the turnover; it is 16.3, so the committed 16 um rung sits
    # BELOW it and the licence was admitting exactly the region it claimed to
    # exclude. The ladder was still monotone, because the fall from 16.3 to 16.0
    # is 0.02 per cent and smaller than the rise from 17, so the guard passed by
    # a second coincidence one rung along from the first one it was written for.
    # What is asserted now is the physics itself: the count is single-peaked in
    # the waist, so of any two rungs the one NEARER the turnover carries the
    # larger value, on either side of it.
    import importlib.util as _il
    _s = _il.spec_from_file_location("_fp", ROOT / "scripts" / "run_four_peak_contrasts.py")
    _fp = _il.module_from_spec(_s); _s.loader.exec_module(_fp)
    _grid = [14.0 + 0.1 * i for i in range(61)]          # 14.0 to 20.0 um
    _cyc = [_fp._cycles_per_crossing(0.225, w * 1e-6) for w in _grid]
    turnover = _grid[max(range(len(_grid)), key=lambda i: _cyc[i])]
    assert 15.0 < turnover < 18.0, f"the turnover moved to {turnover} um; re-read this guard"
    for (wa, va), (wb, vb) in zip(zip(waists, vals_w), list(zip(waists, vals_w))[1:]):
        near_a, near_b = abs(wa - turnover), abs(wb - turnover)
        if near_a == near_b:
            continue
        closer_is_b = near_b < near_a
        assert (vb > va) == closer_is_b, (
            f"the cycles per crossing are not single-peaked about the measured "
            f"turnover at {turnover:.2f} um: w={wa} gives {va} and w={wb} gives "
            f"{vb}, but {'the latter' if closer_is_b else 'the former'} is the "
            "rung nearer the peak and should carry the larger value. This is "
            "what the weak-drive closed form got wrong, and asserting bare "
            "monotonicity hid it twice: "
            + ", ".join(f"{r['key']}={r['value']}" for r in by_waist))
