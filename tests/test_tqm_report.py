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
    assert all(len(r["seats"]) >= 5 for r in rows[-5:]), (
        "a recent round carries fewer seats than any era of this "
        "ledger required, so the row shape has changed under the "
        "reader")


def test_the_report_runs_end_to_end(capsys):
    """It prints, it does not raise, and every section reports itself.
    A reading instrument that dies on a malformed row is one nobody
    runs at the wave boundary the rules put it on."""
    assert tqm.main() == 0
    out = capsys.readouterr().out
    for section in ("findings per round", "calibration", "escapes",
                    "gate verdict"):
        assert section in out, f"the {section} section did not report"
