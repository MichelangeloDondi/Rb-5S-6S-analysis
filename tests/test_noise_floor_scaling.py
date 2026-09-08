"""The noise floor's density exponents are read from the file, not retyped.

Plan chapter 7 argues that radiation trapping does not set the floor from two
log-log slopes; until 2026-09-08 they were fitted in a session and quoted by
hand, and a replay of them found the pooled value hiding a
per-peak spread. These guard the file's internal shape: the pooled exponent
lies inside the per-peak range for each quantity, every row is tagged as
computed, and the checker that reads the shape fires on a planted file whose
pooled value sits outside its own peaks.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "noise_floor_scaling.csv"


def _rows(path):
    with path.open() as fh:
        return list(csv.DictReader(fh))


def pooled_inside_per_peak(rows) -> list[str]:
    bad = []
    for q in sorted({r["quantity"] for r in rows}):
        peaks = [float(r["value"]) for r in rows if r["quantity"] == q and r["scope"].startswith("peak_")]
        pooled = [float(r["value"]) for r in rows if r["quantity"] == q and r["scope"] == "pooled"]
        if len(pooled) != 1 or len(peaks) < 2:
            bad.append(f"{q}: {len(pooled)} pooled row(s), {len(peaks)} peak rows")
        elif not (min(peaks) <= pooled[0] <= max(peaks)):
            bad.append(f"{q}: pooled {pooled[0]} outside the per-peak range {min(peaks)}..{max(peaks)}")
    return bad


def test_the_pooled_exponent_lies_inside_the_per_peak_range():
    rows = _rows(CSV)
    assert rows and not pooled_inside_per_peak(rows)


def test_every_row_is_a_diagnostic_with_an_error():
    for r in _rows(CSV):
        assert r["status"] == "DIAGNOSTIC", r
        assert float(r["err"]) > 0, r


def test_the_shape_check_fires_on_a_planted_file(tmp_path):
    planted = tmp_path / "planted.csv"
    planted.write_text("scope,quantity,value,err,temperatures_C,note,status\n"
                       "peak_a,floor_exponent,0.2,0.01,all,,DIAGNOSTIC\n"
                       "peak_b,floor_exponent,0.4,0.01,all,,DIAGNOSTIC\n"
                       "pooled,floor_exponent,0.9,0.01,all,,DIAGNOSTIC\n")
    assert pooled_inside_per_peak(_rows(planted))
