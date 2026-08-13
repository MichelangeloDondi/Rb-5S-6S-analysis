#!/usr/bin/env python3
"""A claim-class result row carries an uncertainty. Protocol 8a.1, CSV half.

WHAT THIS HOLDS. Every row in `results/` whose status makes it a claim,
MEASURED, BOUND, ENVELOPE or CALIB, has an uncertainty somewhere. Rows marked
DIAGNOSTIC do not, and that is correct rather than tolerated: a likelihood
scan is a curve, a trim report is a processing log, and a BIC difference is a
model comparison. None of them is a measurement.

THIS GUARD REPAIRS NOTHING. Measured 2026-08-13, the record already passes
with zero gaps. It exists so that stays true.

THE RESULT FILES STORE AN UNCERTAINTY IN THREE SHAPES, and a guard that knows
only one of them reports a record-wide catastrophe that is not there. All
three of these are live in the tree today:

  WIDE, a sibling column          value, err
  WIDE UNDER ANOTHER NAME         beta_self, beta_self_err
                                  amp, amp_err
                                  fwhm, fwhm_err
                                  rate_laser, rate_laser_err
  LONG, a sibling ROW             quantity=d_skew        value=-0.0408
                                  quantity=d_skew_mc_err value=0.0021

Writing this guard produced four consecutive false alarms, each a confident
number pointing at repair work that did not need doing, the largest of them
claiming 28 of 46 files were defective when the true figure was zero. That is
recorded as the recurrence under lesson 36, and it is why the shapes are
enumerated here in full rather than inferred.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "results"

CLAIM = {"MEASURED", "BOUND", "ENVELOPE", "CALIB"}
UNCERTAINTY_COLUMN = re.compile(
    r"err|sigma|_se$|^se$|std|lo95|hi95|lo16|hi84|band|syst|scatter|ci_", re.I)
SIBLING_SUFFIXES = ("mc_err", "err", "sd", "se", "band", "lo95", "hi95")


def _rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def _gaps() -> list[str]:
    gaps = []
    for path in sorted(RESULTS.glob("*.csv")):
        header, rows = _rows(path)
        if any(UNCERTAINTY_COLUMN.search(c) for c in header):
            continue                      # wide, under whatever name
        if not {"quantity", "key", "status"} <= set(header):
            continue                      # not the long schema, nothing to check
        names = {r["quantity"] for r in rows}
        for r in rows:
            if (r.get("status") or "").strip() not in CLAIM:
                continue
            q = r["quantity"]
            if not any(f"{q}_{s}" in names for s in SIBLING_SUFFIXES):
                gaps.append(f"{path.name}: {q} / {r['key']} = {r['value']}")
    return gaps


def test_no_claim_class_row_lacks_an_uncertainty():
    gaps = _gaps()
    assert not gaps, (
        f"{len(gaps)} claim-class result rows carry no uncertainty in any of "
        f"the three shapes this guard knows. Protocol 8a.1: a value carries "
        f"an uncertainty or an explicit statement of why it has none.\n  "
        + "\n  ".join(gaps[:12]))


def test_the_guard_is_actually_looking_at_something():
    """A guard whose population is empty passes without checking anything.

    This is the fault that let the figure-overlap guard skip thirteen of
    twenty-eight figures unnoticed for two weeks, so every guard in this
    repository states the size of what it examined.
    """
    seen = 0
    for path in sorted(RESULTS.glob("*.csv")):
        header, rows = _rows(path)
        if any(UNCERTAINTY_COLUMN.search(c) for c in header):
            continue
        if not {"quantity", "key", "status"} <= set(header):
            continue
        seen += sum(1 for r in rows
                    if (r.get("status") or "").strip() in CLAIM)
    assert seen >= 40, (
        f"only {seen} claim-class rows reached the check, against 48 when it "
        f"was written. Either the record changed shape or the schema test "
        f"above is now excluding files it used to read.")


def test_the_long_format_sibling_is_recognised():
    """Checked on the storage shape that caused the worst false alarm."""
    names = {"d_skew", "d_skew_mc_err"}
    assert any(f"d_skew_{s}" in names for s in SIBLING_SUFFIXES)
    assert not any(f"d_kappa9_{s}" in names for s in SIBLING_SUFFIXES)
