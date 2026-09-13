"""The density-law rows say what the laws are and what the archive cannot tell.

FAILURE MODE IF THIS FILE IS DELETED: the producer could silently swap the
laws' ordering (Alcock above Steck across the archive is what the anchor's
conversion rests on), leave out the thermometry-offset reading, or report the
ladder fit as preferring a law when the fit is degenerate by construction.
"""
import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "density_laws.csv"


def _rows():
    if not CSV.is_file():
        pytest.skip("results/density_laws.csv not committed yet")
    return list(csv.DictReader(CSV.open(encoding="utf-8")))


def test_alcock_sits_above_steck_across_the_ladder_by_a_few_kelvin():
    rows = _rows()
    for T in ("T70", "T90", "T110", "T130"):
        r = next(x for x in rows if x["quantity"] == "ratio_AIH_over_Steck" and x["key"] == T)
        assert 1.15 < float(r["value"]) < 1.35, (T, r["value"])
        k = next(x for x in rows if x["quantity"] == "ratio_as_kelvin_AIH" and x["key"] == T)
        assert 2.0 < float(k["value"]) < 5.0, (T, k["value"])


def test_the_ladder_cannot_pick_a_law():
    """The fit's chi-squared is the same under every law to the precision the
    three temperatures allow: beta and the cold spot are degenerate."""
    rows = _rows()
    chi = [float(x["value"]) for x in rows if x["quantity"].startswith("ladder_fit_") and x["key"] == "chi2"]
    assert len(chi) == 3
    assert max(chi) - min(chi) < 0.05, chi


def test_the_theory_pinned_row_is_present_for_every_law():
    rows = _rows()
    pinned = [x for x in rows if x["key"] == "dT_with_beta_pinned"]
    assert len(pinned) == 3
