"""The process-metric report's own guards.

WHY THIS EXISTS AND NOT A `NOT_WIRED` ENTRY. The report is a reading
instrument rather than a pass/fail gate: it prints four metrics and the
consequence each carries, and a session acts on the reading. That would
argue for exempting it from the wiring guard. What argues against the
exemption is its own first run: the escape parser read table rows
against a file written in headings, reported ZERO escapes over the
thirteen entries the ledger then held, and looked entirely healthy doing it. A metric that
fails silently to zero is worse than no metric, because it is
reassuring. So the parsers are pinned here, and the wiring guard gets a
caller that is a guard rather than an excuse.

Failure mode guarded: a report whose population is empty for a reason
nobody notices - which is the class the record has been closing all
week, arriving this time inside the instrument built to measure it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_MOD = ROOT / "private" / "checks" / "tqm_report.py"

pytestmark = pytest.mark.skipif(
    not _MOD.is_file(),
    reason="the governance tree is private and absent from the mirror")

if _MOD.is_file():
    _spec = importlib.util.spec_from_file_location("tqm_report", _MOD)
    tqm = importlib.util.module_from_spec(_spec)
    sys.modules.setdefault("tqm_report", tqm)
    _spec.loader.exec_module(tqm)


def test_the_escape_parser_finds_the_entries_that_exist():
    """The bug this file was written after: a parser shaped for one
    markdown form against a file written in another, reporting zero and
    looking healthy. If the ledger holds entries, the parser sees them.
    """
    if not tqm.ESCAPES.is_file():
        pytest.skip("no escape ledger on this checkout")
    text = tqm.ESCAPES.read_text(encoding="utf-8")
    if "## E" not in text:
        pytest.skip("no escape entries to count")
    ids = tqm._escape_ids(text)
    assert ids, (
        "the escape ledger holds '## E<n>' headings and the report's "
        "parser found none: the metric would read zero over real "
        "escapes, which is how it failed on 2026-09-02")


def test_the_escape_count_agrees_with_the_ledgers_own_total():
    """The cross-check that caught a stale total on its first run, kept
    as a test so the two numbers cannot drift apart again unnoticed."""
    if not tqm.ESCAPES.is_file():
        pytest.skip("no escape ledger on this checkout")
    import re
    text = tqm.ESCAPES.read_text(encoding="utf-8")
    ids = tqm._escape_ids(text)
    stated = re.search(r"Running totals:\s*(\d+)\s+escapes", text)
    if not (ids and stated):
        pytest.skip("nothing to cross-check on this checkout")
    assert int(stated.group(1)) == len(ids), (
        f"the ledger says {stated.group(1)} escapes and carries "
        f"{len(ids)} headings. The file is the record; reconcile it "
        "before the rate is read.")


def test_the_round_reader_sees_the_recorded_rounds():
    """The findings-per-round and calibration metrics both read the
    ledger through one function. An empty read would make both metrics
    silently vacuous."""
    if not tqm.LEDGER.is_file():
        pytest.skip("no board ledger on this checkout")
    rows = tqm._rounds()
    assert rows, (
        "the ledger file exists and the round reader found no rounds: "
        "the shape it parses has changed and two metrics are now empty")
    # not `any(seats)`, which _rounds() already filters for and which
    # would therefore assert nothing: the ledger's rounds carry the
    # required seat set, so check the shape a reader relies on.
    #
    # THE FLOOR IS READ, NOT TYPED (2026-09-13). This asserted `>= 5`, which
    # was the seat count of one era and is not a shape at all. The owner has
    # moved that number twice since: LOGIC 0c.25 made `physics` and `strategy`
    # the required pair, and CREDIT MODE cut it to `physics` alone plus at most
    # two Sonnet extras. A three-seat credit-mode round is correct and turned
    # this test red. The rule file already says the seat count lives in
    # `REQUIRED_SEATS` and never as a number written elsewhere; that binds a
    # test as much as it binds prose, so the floor comes from the ledger.
    import importlib.util as _il
    _s = _il.spec_from_file_location("_bl", ROOT / "private" / "checks" / "board_ledger.py")
    _bl = _il.module_from_spec(_s); _s.loader.exec_module(_bl)
    floor = _bl.MIN_SEATS
    assert all(len(r["seats"]) >= floor for r in rows[-5:]), (
        f"a recent round carries fewer than {floor} seats, the current floor "
        "from board_ledger.MIN_SEATS, so the row shape has changed under the "
        "reader")
    # AND THE SHAPE THAT IS NOT VACUOUS. With MIN_SEATS down to 1 and _rounds()
    # already filtering for any(seats), the assertion above cannot fail and
    # asserts nothing, which is the vacuity the comment above it warns
    # against (corrected 2026-09-13). What the reader actually depends on is
    # that a verdict aligns with a seat, which is what record() refuses to
    # write and what a stale fixture had been seeding wrongly.
    for r in rows[-5:]:
        assert len(r["verdicts"]) == len(r["seats"]), (
            f"round {r.get('tree', '?')[:12]} carries {len(r['seats'])} seats "
            f"and {len(r['verdicts'])} verdicts; the reader pairs them by "
            "position and a mismatch silently mislabels every verdict after it")


def test_the_report_runs_end_to_end(capsys):
    """It prints, it does not raise, and every section reports itself.
    A reading instrument that dies on a malformed row is one nobody
    runs at the wave boundary the rules put it on."""
    assert tqm.main() == 0
    out = capsys.readouterr().out
    for section in ("findings per round", "calibration", "escapes",
                    "gate verdict"):
        assert section in out, f"the {section} section did not report"


def test_every_plan_the_debt_reader_names_is_on_disk():
    """`plan_debts()` reads the plans BY FILENAME. From 2026-09-17 20:02 to
    2026-09-22 one member named nothing: the static-tail sweep had moved the
    night plan of 2026-09-12 whole into `private/history/records/`, and the
    loop skipped the absent path in silence, so every report read three plans
    as the whole population. The report now names an absent member NOT
    MEASURED; this test makes the floor refuse one, so the tuple is repaired
    in the wave that moves the plan and not days later."""
    absent = tqm._absent_plan_files(tqm.ROOT, tqm.PLAN_FILES)
    assert not absent, (
        f"tqm_report.PLAN_FILES names {absent} and no file is there, so the "
        "plan-debt totals are a floor. private/history/records/MOVED.tsv logs "
        "every sweep's move: repoint the member at the plan that replaced it, "
        "or remove it, and say why beside the tuple")


def test_an_absent_plan_is_named_and_the_totals_called_a_floor(tmp_path, monkeypatch, capsys):
    """The plant, through `plan_debts()` itself and on the exact member that
    dangled. Absent, it is named NOT MEASURED and both totals are called a
    floor while the present plan is still counted; with every member present,
    neither line appears. The old loop (a bare `continue`) fails the first
    half, and that failure is the defect."""
    present = "private/PLAN_PRESENT.md"
    dangling = "private/cache/ultra_joint_2026-09-12/PLAN_NIGHT_2026-09-12.md"
    (tmp_path / "private").mkdir()
    (tmp_path / present).write_text("OWED: a planted debt\nand one more owed in prose\n")
    monkeypatch.setattr(tqm, "ROOT", tmp_path)

    monkeypatch.setattr(tqm, "PLAN_FILES", (present, dangling))
    tqm.plan_debts()
    out = capsys.readouterr().out
    assert f"{dangling}: NOT MEASURED" in out, out
    assert "FLOOR" in out, out
    assert "PLAN_PRESENT.md: 1 OWED: line(s), 2 prose mention(s)" in out, out

    monkeypatch.setattr(tqm, "PLAN_FILES", (present,))
    tqm.plan_debts()
    out = capsys.readouterr().out
    assert "NOT MEASURED" not in out and "FLOOR" not in out, out


def test_the_escape_total_is_derived_from_the_parser_and_not_typed(tmp_path):
    """The count and the thing counted have drifted inside ESCAPE_LEDGER.md four times.

    `fix_escape_total` rewrites the stated number from `_escape_ids`, so the line is derived. Planted
    both ways: a stale file is rewritten and an in-sync one is left byte-identical.
    """
    p = tmp_path / "L.md"
    p.write_text("## E1, a\n## E2, b\n## E3, c\nRunning totals: 1 escapes, each with its sweep.\n")
    seen = tqm.fix_escape_total(p)
    assert seen[:2] == (1, 3) and "Running totals: 1 escapes" in p.read_text(), (
        "the default call READS and must not rewrite a governance record")
    was, now, _ = tqm.fix_escape_total(p, write=True)
    assert (was, now) == (1, 3), (was, now)
    assert "Running totals: 3 escapes" in p.read_text()
    before = p.read_text()
    was2, now2, _ = tqm.fix_escape_total(p, write=True)
    assert was2 == now2 == 3 and p.read_text() == before, "an in-sync ledger is not rewritten"
