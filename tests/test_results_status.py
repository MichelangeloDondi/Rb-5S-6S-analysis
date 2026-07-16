"""
Guards on the machine-attached `status` provenance column (review commission,
2026-07-12): every committed result CSV must carry the caveat *with the number*,
so a plot script that never opens RESULTS.md cannot mistake a bound for a
measurement. Pins: every result file has a status/flag column; annotated files
use the controlled vocabulary; and the headline bounds are tagged BOUND while
the superseded model fits are tagged PRELIM.
"""

from __future__ import annotations

import csv
import glob
import importlib.util
import os
from pathlib import Path

from rb5s6s.config import RESULTS_DIR

# load the annotator (scripts/ is not a package) so the vocab has one source
_spec = importlib.util.spec_from_file_location(
    "annotate_results_status",
    Path(__file__).resolve().parents[1] / "scripts" / "annotate_results_status.py")
ars = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ars)

VOCAB = ars.VOCAB
OWN_STATUS = ars.SKIP  # files carrying their own status/flag column


def _rows(name):
    return list(csv.DictReader(open(RESULTS_DIR / name)))


def test_every_result_csv_carries_provenance():
    for path in glob.glob(str(RESULTS_DIR / "*.csv")):
        rows = list(csv.DictReader(open(path)))
        if not rows:
            continue
        cols = {c.lower() for c in rows[0]}
        assert cols & {"status", "flag"}, f"{os.path.basename(path)}: no status/flag column"


def test_annotated_statuses_use_controlled_vocab():
    for path in glob.glob(str(RESULTS_DIR / "*.csv")):
        name = os.path.basename(path)
        if name in OWN_STATUS:
            continue
        rows = list(csv.DictReader(open(path)))
        if not rows or "status" not in rows[0]:
            continue
        for r in rows:
            assert r["status"] in VOCAB, f"{name}: {r['status']!r} not in {sorted(VOCAB)}"


def test_headline_bounds_tagged_bound_not_measurement():
    # the reviewer's exact concern, pinned: a bare beta/S0 must not read as a
    # measurement, and the superseded per-peak fits must not look like a headline.
    d = {r["quantity"]: r for r in _rows("lever_crosscheck.csv")}
    assert d["beta_crosscheck"]["status"] == "BOUND"
    assert d["gamma_rise_factor"]["status"] == "MEASURED"        # the floor IS measured
    s = {r["quantity"]: r for r in _rows("stark_sweep.csv")}
    # the quoted bound is the profile-likelihood row; the Wald rows (raw and
    # chi2-inflated) are superseded diagnostics -- the fit rails at kappa=0
    # where a linearized interval has no coverage.
    assert s["S0_225mW_ub95_profile"]["status"] == "BOUND"
    assert s["S0_225mW_ub95"]["status"] == "DIAGNOSTIC"
    assert s["S0_225mW_ub95_raw"]["status"] == "DIAGNOSTIC"
    assert all(r["status"] == "BOUND" for r in _rows("beta_self_probe.csv"))
    assert all(r["status"] == "PRELIM" for r in _rows("beta_self.csv"))
    assert all(r["status"] == "NULL" for r in _rows("modelform.csv"))
