"""The detection budget's rows say which waist power the geometry realises and
how far the measured photoelectron rate sits from the chain's prediction.

FAILS when the weak-drive exponent leaves the interval the derivation fixes
(-2 to 0), when the short-window limit does not return -2, when the record's
12 mm orientation stops reproducing the prediction band's collected fraction,
when a predicted or measured rate row lacks its uncertainty, or when the gap
rows stop spanning both cathode orientations and both density laws, any of
which would let the budget be quoted with a term silently omitted.
"""
import csv
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "detection_budget.csv"


def _rows():
    with CSV.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _module():
    spec = importlib.util.spec_from_file_location("run_detection_budget", ROOT / "scripts" / "run_detection_budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_weak_drive_exponent_runs_from_minus_two_to_zero():
    m = _module()
    assert abs(m.weak_drive_exponent(1e-4) + 2.0) < 1e-3       # the short-window limit
    assert -0.1 < m.weak_drive_exponent(1e3) <= 0.0            # the whole Rayleigh range inside
    xs = [0.05, 0.26, 1.0, 4.2]
    es = [m.weak_drive_exponent(x) for x in xs]
    assert all(-2.0 <= e <= 0.0 for e in es)
    assert es == sorted(es)                                    # monotone toward zero


def test_the_record_orientation_reproduces_the_prediction_band_fraction():
    rows = _rows()
    frac = next(r for r in rows if r["quantity"] == "collected_fraction" and r["key"] == "along12")
    with (ROOT / "results" / "prediction_band.csv").open(encoding="utf-8") as fh:
        band = next(r for r in csv.DictReader(fh) if r.get("key") == "fluorescence_collected_frac")
    assert abs(float(frac["value"]) - float(band["value"])) < 0.005


def test_every_rate_row_carries_its_uncertainty_and_the_gap_spans_the_open_axes():
    rows = _rows()
    rates = [r for r in rows if r["quantity"] in ("measured_pe_rate", "predicted_pe_rate_log10", "gap_log10_predicted_over_measured")]
    assert rates and all(r["err"].strip() for r in rates)
    gaps = [r for r in rows if r["quantity"] == "gap_log10_predicted_over_measured"]
    keys = {tuple(r["key"].split("_")[:2]) for r in gaps}
    for law in ("Steck", "AIH"):
        for orient in ("along12", "along3"):
            assert (law, orient) in keys, (law, orient)
    assert all(math.isfinite(float(r["value"])) for r in gaps)


def test_the_open_terms_are_rows_and_not_numbers():
    rows = _rows()
    for q in ("filter_transmission", "excess_noise_factor", "D1_trapping_effect_on_collection"):
        r = next(r for r in rows if r["quantity"] == q)
        assert "OPEN" in r["note"], q
