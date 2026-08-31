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
import json
import pathlib
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


def _is_long_schema(header: list[str]) -> bool:
    """A row-per-quantity CSV, whatever its second key column is called.

    THIS GATE REQUIRED A COLUMN LITERALLY NAMED `key` UNTIL 2026-08-28, so two
    producers written that summer emitted `quantity, value, unit, basis, note,
    status` and were skipped ENTIRELY: 33 claim-class rows examined by nothing
    while this file reported green. The population of a guard is whatever its
    schema gate admits, and a gate keyed on one spelling is a gate that new
    work walks past.
    """
    if not {"quantity", "status"} <= set(header):
        return False
    return bool({"key", "arm", "lever"} & set(header)) or "value" in header


def _gaps() -> list[str]:
    gaps = []
    for path in sorted(RESULTS.glob("*.csv")):
        header, rows = _rows(path)
        if any(UNCERTAINTY_COLUMN.search(c) for c in header):
            continue                      # wide, under whatever name
        if not _is_long_schema(header):
            continue                      # not the long schema, nothing to check
        names = {r["quantity"] for r in rows}
        for r in rows:
            if (r.get("status") or "").strip() not in CLAIM:
                continue
            q = r["quantity"]
            # An uncertainty row does not need its own uncertainty. When
            # the schema gate was widened on 2026-08-28 the first thing it
            # surfaced was `gamma_coll_err` being asked for its own error bar,
            # which is the guard reading its own vocabulary as a claim.
            if q.endswith(tuple(f"_{x}" for x in SIBLING_SUFFIXES)):
                continue
            # AND A LEADING `sigma_` NAMES ONE JUST AS A TRAILING `_err` DOES.
            # The first repair recognised only the trailing forms, so
            # `gamma_coll_err` was exempted and `sigma_transit_frac` was not,
            # though both ARE the uncertainty rather than a value missing one.
            # A forecast producer names its outputs sigma_* throughout, so the
            # omission hit an entire file's worth of rows.
            if q.startswith("sigma_") or q.startswith("sigma "):
                continue
            if not any(f"{q}_{s}" in names for s in SIBLING_SUFFIXES):
                label = r.get("key") or r.get("arm") or r.get("lever") or "-"
                # THE VALUE IS NOT PART OF THE IDENTITY. It was until
                # 2026-08-28, and two lever rows re-flagged as NEW gaps the
                # first time their producer was re-run, because 0.8787 became
                # 0.8753. A debt ledger keyed on the measured value is a
                # tripwire on ordinary maintenance rather than a record of
                # what is owed. The value belongs in the failure message.
                gaps.append(f"{path.name}: {q} / {label}")
    return gaps


# The debt this guard could not see until its schema gate was widened.
#
# 2026-08-28. The gate required a column literally named `key`, so any producer
# emitting `quantity, value, unit, basis, note, status` was skipped WHOLE.
# Widening the gate surfaced the population the baseline below records --
# read `len` of the JSON rather than a number here, which drifted the same
# night it was written -- and a large share of it sits in files committed
# LONG BEFORE the producers that triggered the look: `collisional_shift_bound.csv`
# and `ruler_tooth_scatter.csv` had never once been read by this test.
#
# The rows are seeded rather than fixed in the same night, because the fix is
# per-producer and belongs with each producer's own wave. The seed FALLS ONLY:
# a new gap fails the test, and paying one down requires lowering the count
# here with its reason. That converts an invisible population into a measured
# debt, which is what this repository does with every other backlog.
# AND NINE ENTRIES ARE THIS WAVE'S OWN DEBT, NOT INHERITED, said plainly here
# on 2026-08-29 because a release board found the distinction being blurred.
# `campaign_twin_forecast.csv` and `onf_lever_ranking.csv` are CREATED by the
# commit that seeds their rows, so the defence above -- that a fix belongs with
# each producer's own wave -- does not apply to them: this IS their producer's
# wave. Four rows from the first and five from the second are therefore owed
# rather than inherited, and calling them inherited is the laundering the
# seed mechanism exists to prevent.
#
# WHY THEY ARE NOT PAID IN THIS COMMIT, stated rather than left to be inferred.
# Each of the nine has a legitimate reason to carry no uncertainty -- a solve
# output whose tolerance lives in a sibling file, a truth value fed INTO the
# twin and so an input by construction, an arithmetic difference of two
# committed constants, and one entry whose value is the word "never". But this
# guard's only escape is a sibling `_err` row, so recording those reasons means
# emitting nine new rows, four of them behind a Monte Carlo, each needing a
# physics judgement about what the error even means for that quantity. That is
# a wave, and doing it inside this one is what repeated readings have shown do
# not converge.
#
# SO IT IS OWED, dated, and named: nine rows, two files, next wave. The guard
# keeps failing anything NEW, which is what it is for.
# PAID DOWN 2026-08-29, 31 to 30, and the entry that left is the point.
# `campaign_twin_forecast.csv: minutes_per_trace / onf` was seeded as debt
# while its uncertainty was ONE DIVISION AWAY: `ONF_COUNTS_PER_MS` is the
# centre of the committed 25 to 40 counts per ms band, and minutes go as one
# over the rate, so the band propagates directly. The producer now emits the
# half-span. Exactly one entry left and none arrived, checked by diffing the
# seed against the live gaps rather than by trusting the count.
#
# AND THE SEED'S OWN JUSTIFICATION DOES NOT REACH EVERY ROW IN IT. The
# paragraph above defends seeding on the ground that the debt is inherited
# and each fix "belongs with each producer's own wave". A release board found
# that rows from `campaign_twin_forecast.csv` and `onf_lever_ranking.csv`
# were seeded in the same commit that CREATED those files, where that
# defence does not apply: for them, this IS their producer's own wave.
# One was payable and is paid. The rest are recorded as owed in
# private/cache/UNATTENDED_2026-08-29.md with two options and a
# recommendation, because closing them changes either a producer's physics or
# what this guard accepts, and neither is an unattended edit.
BASELINE = pathlib.Path(__file__).with_name("_uncertainty_gap_baseline.json")


def test_no_new_claim_class_row_lacks_an_uncertainty():
    gaps = set(_gaps())
    seeded = set(json.loads(BASELINE.read_text()))
    new = sorted(gaps - seeded)
    assert not new, (
        f"{len(new)} NEW claim-class result rows carry no uncertainty in any "
        f"of the three shapes this guard knows. Protocol 8a.1: a value carries "
        f"an uncertainty or an explicit statement of why it has none.\n  "
        + "\n  ".join(new[:12]))


def test_the_uncertainty_gap_only_falls():
    gaps = set(_gaps())
    seeded = set(json.loads(BASELINE.read_text()))
    assert len(gaps) <= len(seeded), (
        f"{len(gaps)} gaps against a seed of {len(seeded)}")
    if len(gaps) < len(seeded):
        raise AssertionError(
            f"the gap fell from {len(seeded)} to {len(gaps)}, which is the "
            f"point -- re-seed _uncertainty_gap_baseline.json and say in the "
            f"commit which producer paid it down")


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
        if not _is_long_schema(header):
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
