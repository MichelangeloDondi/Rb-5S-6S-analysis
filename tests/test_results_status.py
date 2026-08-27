"""
Guards on the machine-attached `status` provenance column (added
2026-07-12): every committed result CSV must carry the caveat *with the number*,
so a plot script that never opens RESULTS.md cannot mistake a bound for a
measurement. Pins: every result file has a status/flag column; annotated files
use the controlled vocabulary; and the headline bounds are tagged BOUND while
the replaced model fits are tagged PRELIM.
"""

from __future__ import annotations

import csv
import glob
import importlib.util
import os
import shutil
from pathlib import Path

import pytest

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
    from _fileset import tracked_and_new, ROOT as _R
    for path in [str(_R / p) for p in tracked_and_new("results/*.csv")]:
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
    # the exact concern, pinned: a bare beta/S0 must not read as a
    # measurement, and the replaced per-peak fits must not look like a headline.
    d = {r["quantity"]: r for r in _rows("lever_crosscheck.csv")}
    assert d["beta_crosscheck"]["status"] == "BOUND"
    assert d["gamma_rise_factor"]["status"] == "MEASURED"        # the floor IS measured
    s = {r["quantity"]: r for r in _rows("stark_sweep.csv")}
    # the quoted bound is the profile-likelihood row; the Wald rows (raw and
    # chi2-inflated) are replaced diagnostics -- the fit rails at kappa=0
    # where a linearized interval has no coverage.
    assert s["S0_225mW_ub95_profile"]["status"] == "BOUND"
    assert s["S0_225mW_ub95"]["status"] == "DIAGNOSTIC"
    assert s["S0_225mW_ub95_raw"]["status"] == "DIAGNOSTIC"
    assert all(r["status"] == "BOUND" for r in _rows("beta_self_probe.csv"))
    assert all(r["status"] == "PRELIM" for r in _rows("beta_self.csv"))
    assert all(r["status"] == "NULL" for r in _rows("modelform.csv"))


# --------------------------------------------------------------------------
# The annotator has to RUN
# --------------------------------------------------------------------------
def test_the_annotator_runs_clean_over_the_current_results_set(tmp_path, monkeypatch):
    """Call `main()` over the results set this commit would ship, expect 0.

    WHY THIS EXISTS. `FILE_STATUS[fname]` is a bare subscript under the comment
    `# KeyError forces every file to be mapped`: a producer may not commit a
    results file without saying what its rows are. Failing closed is the right
    design. What was missing was anything that ever CALLS it. The annotator
    runs only from `run_all.sh`, the gate runs pytest, and
    `tests/test_pipeline_order.py` checks the runner's ORDER and says in its own
    docstring that it deliberately does not check behaviour. So the KeyError
    fired for nobody. `window_attribution.csv` landed 2026-08-24 and
    `centre_fisher.csv` 2026-08-25; both sat unmapped until 2026-08-26 with
    every gate green over them, and a full `bash scripts/run_all.sh` would have
    died on the first of them alphabetically. That is the third time by this
    file's own record -- the kernel family on 2026-08-22, `quantisation.csv` and
    `twin_realism.csv` on 2026-08-24 -- which is what makes it a class rather
    than an incident.

    Over a COPY in tmp_path, because the annotator rewrites every file it tags
    and a guard may not edit the tree it is gating.

    Over `tracked_and_new` rather than a raw directory glob, for the reasons
    `tests/_fileset.py` sets out: it is the set this commit ships, it sees a
    brand-new untracked CSV (which is the case this test exists for, since a
    file is untracked on the day it lands), and it excludes ignored scratch
    dumps that would redden the gate on one machine only. `run_all.sh` globs the
    directory instead, so an ignored CSV in a development checkout can still
    stop a real run there; that is local and not a shipped defect.
    """
    from _fileset import ROOT as _R
    from _fileset import tracked_and_new

    names = [p for p in tracked_and_new("results/*.csv") if (_R / p).exists()]
    assert names, "no results CSVs found, so this guard would pass vacuously"
    for rel in names:
        shutil.copy2(_R / rel, tmp_path / Path(rel).name)

    monkeypatch.setattr(ars.C, "RESULTS_DIR", tmp_path)
    try:
        rc = ars.main()
    except KeyError as exc:
        pytest.fail(
            f"annotate_results_status.py cannot tag {exc}. A results CSV "
            f"reached the tree with no entry in FILE_STATUS, QUANTITY_STATUS "
            f"or SKIP, so `bash scripts/run_all.sh` dies here and that file's "
            f"caveat cannot travel with its numbers into any downstream table "
            f"or figure. Classify it into the vocabulary in the annotator's "
            f"docstring, or add it to SKIP if its producer already writes its "
            f"own status column.")
    assert rc == 0

    # -- and the tags it produces must be the tags the tree ships ----------
    # ADDED 2026-08-27. Until this block the test asserted rc == 0 and
    # nothing else, so it proved the annotator does not CRASH and never that
    # its output matches the committed column. `verify_results_fresh.py`
    # cannot cover the gap either: its own docstring says the status column
    # is ignored.
    #
    # WHAT THIS CATCHES, stated narrowly because the first draft of this
    # comment claimed a class it does not reach: a committed status column
    # that has drifted from the classifier, which is what a producer run
    # without the annotator afterwards leaves behind (it happened on
    # 2026-08-27 to `stark_sweep.csv`, which lost its status column
    # entirely). WHAT IT DOES NOT CATCH: a producer and the annotator
    # disagreeing about a row, because the annotator runs last and the
    # committed file then agrees with it by construction. That is a
    # different class and the collision test below is what reaches it.
    drift = []
    for rel in names:
        name = Path(rel).name
        if name in OWN_STATUS:
            continue
        fresh = list(csv.DictReader(open(tmp_path / name)))
        shipped = list(csv.DictReader(open(_R / rel)))
        if not fresh or "status" not in fresh[0]:
            continue
        for i, (a, b) in enumerate(zip(fresh, shipped), start=2):
            if a["status"] != b["status"]:
                q = a.get("quantity", f"row {i}")
                drift.append(f"{name}:{i} {q!r} committed {b['status']} "
                             f"but the annotator says {a['status']}")
    assert not drift, (
        "the committed status column disagrees with what the annotator "
        "produces, so a caveat travelling with a number is not the caveat "
        "the classifier assigns:\n  " + "\n  ".join(drift))


def test_no_exact_quantity_key_doubles_as_a_family_prefix():
    """An entry naming one quantity may not silently classify another.

    `status_for` falls back to longest-prefix matching when a quantity has no
    exact entry, which is how families like `proj_*` are tagged in one line.
    The fallback cannot tell a FAMILY prefix from a COMPLETE quantity name
    that happens to be a prefix of a longer one, and on 2026-08-27 it could
    not: `delta_alpha_993_tail_dispersion` starts with `delta_alpha_993`, an
    exact entry for a different row, so an ENVELOPE quantity shipped tagged
    DIAGNOSTIC. Its producer writes ENVELOPE, the annotator runs afterwards
    and overwrote it, and nothing in the tree compared the two: the freshness
    checker ignores the status column by its own docstring, and the
    annotator-versus-committed check above cannot see it because the
    annotator wrote the committed value.

    The collision is detectable without running anything: the offending
    prefix also names a quantity in the same file. Measured over the current
    tree, 480 rows resolve by an exact entry and 171 by the fallback, so
    banning the fallback outright is not the proportionate fix. This bans
    only the ambiguous case, and the remedy is one explicit entry.
    """
    from _fileset import ROOT as _R
    from _fileset import tracked_and_new

    collisions = []
    for rel in tracked_and_new("results/*.csv"):
        name = Path(rel).name
        if name in OWN_STATUS or name not in ars.QUANTITY_STATUS:
            continue
        path = _R / rel
        if not path.exists():
            continue
        rows = list(csv.DictReader(open(path)))
        if not rows or "quantity" not in rows[0]:
            continue
        present = {r["quantity"] for r in rows}
        mapping = ars.QUANTITY_STATUS[name]
        for q in sorted(present):
            if q in mapping:
                continue
            for pfx in mapping:
                if q.startswith(pfx) and pfx in present:
                    collisions.append(
                        f"{name}: {q!r} has no entry and falls back to the "
                        f"entry for {pfx!r}, which also names a row in this "
                        f"file, so one quantity's tag is silently deciding "
                        f"another's")
    assert not collisions, (
        "add an explicit QUANTITY_STATUS entry for each quantity below:\n  "
        + "\n  ".join(sorted(set(collisions))))


def test_no_file_is_both_skipped_and_mapped():
    """A name may carry one answer, not two.

    `main()` tests SKIP first, so a name in SKIP and in FILE_STATUS at once has
    a dead map entry saying something the code never reads. Two kernel files sat
    in exactly that state, and the contradiction is not harmless: an audit of
    this map on 2026-08-26 counted the unmapped files by asking which results
    CSVs were absent from FILE_STATUS, without subtracting SKIP, and reported
    fifteen where two were real. The two double-registered names were the ones
    that made the miscount land on a plausible number instead of an obvious one.
    """
    for name in sorted(ars.SKIP):
        assert name not in ars.FILE_STATUS, (
            f"{name} is in SKIP and in FILE_STATUS. SKIP wins in main(), so the "
            f"FILE_STATUS entry is dead. Delete whichever one is wrong.")
        assert name not in ars.QUANTITY_STATUS, (
            f"{name} is in SKIP and in QUANTITY_STATUS. SKIP wins in main(), so "
            f"the QUANTITY_STATUS entry is dead. Delete whichever is wrong.")


def test_every_skipped_file_exists_and_carries_its_own_column():
    """SKIP is the escape hatch, so it has to stay honest.

    Every entry claims the file already carries its own provenance column. If
    that is false the file is not exempt, it is simply untagged, and the guard
    above passes while the caveat never reaches the CSV. `qc_metrics.csv` is the
    one that satisfies this with `flag` rather than `status`: it is a per-trace
    QC table whose rows are traces, not results, and the vocabulary does not
    apply to it.

    Existence is checked for the same reason `test_pipeline_order.py` checks
    that its CONSUMERS still read the column: a stale entry for a retired file
    reads as protection it is not providing.
    """
    for name in sorted(ars.SKIP):
        path = RESULTS_DIR / name
        assert path.exists(), (
            f"SKIP names {name}, which is not in results/. Prune the entry, so "
            f"the set says what it protects.")
        rows = list(csv.DictReader(open(path)))
        if not rows:
            continue
        cols = {c.lower() for c in rows[0]}
        assert cols & {"status", "flag"}, (
            f"{name} is in SKIP, whose entries all claim the producer writes "
            f"the provenance column, but it carries neither `status` nor "
            f"`flag`. It is not exempt, it is untagged.")


def test_producer_written_statuses_use_the_controlled_vocab():
    """The half of the corpus nothing was checking.

    `test_annotated_statuses_use_controlled_vocab` above walks past every file
    in OWN_STATUS, and the annotator never touches them either, so the statuses
    the producers write were validated by nothing at all. That is seventeen of
    the seventy-two committed results files. A producer emitting `PRELIMINARY`
    or `NULL_RESULT` would ship a status no reader of this column can interpret,
    and both guards would stay green.
    """
    for name in sorted(ars.SKIP):
        path = RESULTS_DIR / name
        if not path.exists():
            continue
        rows = list(csv.DictReader(open(path)))
        if not rows or "status" not in rows[0]:
            continue
        for r in rows:
            assert r["status"] in VOCAB, (
                f"{name}: its producer wrote status {r['status']!r}, which is "
                f"not in {sorted(VOCAB)}. The vocabulary is the annotator's "
                f"docstring and it binds producers too.")
