"""The moved-value fixture fires on a synthetic moved value, and says what it cannot see.

WHY THIS EXISTS, and the reason is a failure rather than a policy. On
2026-08-29 a twelve-seat board found `scripts/check_moved_values.py` blind in
four ways at once: it read the value column at a fixed POSITION on a
docstring claim that every results CSV shares one shape (78 files, 45
shapes); it dropped every BAND, which is the dominant shape in the files it
was written for; it skipped `docs/history/` wholesale, including the `now`
column that carries the NEW value; and it graded one diff, so values that
moved one commit before a brief's base were invisible and three separate
invocations all reported clean.

It had no test file at all. A reader called it "the next unguarded guard a
docstring calls reliable", which is this repository's own recurring class:
a mechanism asserting a property it never tested against a synthetic
instance of the failure it was built for.

AND THE FIRST PLANT OF THE REWRITE FAILED, which is recorded here because it
is worth more than the repair. Three of the board's real defects were
re-inserted and the rewritten fixture caught none of them -- correctly. Two
of the CSVs involved were BORN in that wave, so nothing in them had moved,
and the third figure had never been a committed cell in any commit. The
defects were numbers that never matched the CSV rather than numbers that went
stale, and no propagation check can see those. So this file pins the class the
fixture DOES detect, on a scratch repository where a value demonstrably moved,
and pins the blind region beside it so neither is asserted.
"""
from __future__ import annotations

import importlib.util
import re
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "check_moved_values.py"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "scratch", "GIT_AUTHOR_EMAIL": "s@example.invalid",
    "GIT_COMMITTER_NAME": "scratch",
    "GIT_COMMITTER_EMAIL": "s@example.invalid",
}

HEADER = "quantity,value,unit,note,status\n"


def _run(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args],
                         capture_output=True, text=True,
                         env={**os.environ, **GIT_ENV})
    return out.stdout.strip()


@pytest.fixture
def mv():
    spec = importlib.util.spec_from_file_location("check_moved_values", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A scratch tree whose CSV holds one scalar and one band, then moves both.

    THE SHAPE IS `quantity,value,unit` ON PURPOSE. Under the old positional
    read the key embedded the changing value and the UNIT was read as the
    value, so detection on this shape was zero by construction. A fixture
    built on the shape that happened to work would have passed either way.
    """
    r = tmp_path / "scratch"
    (r / "results").mkdir(parents=True)
    (r / "docs").mkdir()
    _run(r, "init", "-q")
    _run(r, "config", "commit.gpgsign", "false")
    (r / "results" / "m.csv").write_text(
        HEADER
        + "mode_area,0.611,um^2,the azimuthal-mean convention,CALIB\n"
        + "transit_band,98 to 181,kHz,across the decay band,DIAGNOSTIC\n")
    (r / "docs" / "note.md").write_text(
        "Quoting `results/m.csv`.\n\n"
        "The effective mode area is 0.611 um^2 and the cold transit term is\n"
        "a band of 98 to 181 kHz.\n")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "base")
    (r / "results" / "m.csv").write_text(
        HEADER
        + "mode_area,0.615,um^2,the azimuthal-mean convention,CALIB\n"
        + "transit_band,73 to 98,kHz,across the decay band,DIAGNOSTIC\n")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "the values move, the prose does not")
    return r


def _point_at(mv, repo: Path):
    mv.ROOT = repo


def test_a_moved_scalar_and_a_moved_band_are_both_found(mv, repo, capsys):
    """The class the fixture exists for, on the header shape it used to miss."""
    _point_at(mv, repo)
    assert mv.main(["check_moved_values.py", "HEAD~1"]) == 1
    out = capsys.readouterr().out
    assert "0.611" in out, "the moved scalar was not reported"
    assert "98 to 181" in out, (
        "the moved BAND was not reported, which is the shape the old row "
        "filter dropped entirely")
    assert "0.615" in out and "73 to 98" in out, (
        "the finding must name what the cell holds now, or a reader cannot "
        "act on it without opening the CSV")


def test_a_corrected_copy_passes(mv, repo, capsys):
    """The false-positive direction: compliance must pass, not only defect fail.

    A guard verified only against a plant can fail every conforming file and
    look healthy. This repository has shipped exactly that once, in the
    release-note checker, whose first form passed its plant while refusing
    every paragraph that OBEYED the rule.
    """
    _point_at(mv, repo)
    (repo / "docs" / "note.md").write_text(
        "Quoting `results/m.csv`.\n\n"
        "The effective mode area is 0.615 um^2 and the cold transit term is\n"
        "a band of 73 to 98 kHz.\n")
    assert mv.main(["check_moved_values.py", "HEAD~1"]) == 0
    assert "clean" in capsys.readouterr().out


def test_a_file_that_does_not_cite_the_csv_is_out_of_scope(mv, repo, capsys):
    """The scope that makes the run readable, pinned so it is not widened by
    accident. Unscoped, the first form of this fixture returned 281 hits of
    which nearly all were numeric collisions."""
    _point_at(mv, repo)
    (repo / "docs" / "note.md").write_text(
        "A page naming no CSV at all.\n\nIt mentions 0.611 in passing.\n")
    assert mv.main(["check_moved_values.py", "HEAD~1"]) == 0


def test_the_history_now_column_is_graded_and_the_was_column_is_not(mv):
    """`docs/history/` was skipped WHOLESALE, and half that skip was right.

    Those tables are `| quantity | was | now | file |`. A hit in `was` is the
    account of the change, which is what the page is for; a hit in `now` is a
    stale disclosure, and one stood in the page a release note names as its
    own disclosure while the guard reported clean.
    """
    table = [
        "| quantity | was | now | file |",
        "|---|---|---|---|",
        "| the width | 0.611 | 0.615 | `results/m.csv` |",
    ]
    graded = mv.history_now_columns(table)
    assert graded[2] == {2}, (
        "only the `now` cell may be graded; grading the whole row reports "
        "the `was` cell, which is the account")


def test_a_csv_with_no_value_column_is_reported_as_unchecked(mv, repo, capsys):
    """A skipped file is not a checked one, and the run must say how many.

    Twenty-six of this repository's CSVs are per-trace tables with no `value`
    column. Silence about them would read as coverage.
    """
    _point_at(mv, repo)
    (repo / "results" / "trace.csv").write_text("file,peak,snr\na,1,9\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-q", "-m", "a per-trace table")
    mv.main(["check_moved_values.py", "HEAD~2"])
    out = capsys.readouterr().out
    # THE PHRASE IS PRESENT EVEN WHEN THE COUNT IS ZERO, so asserting the
    # phrase asserts nothing. A pre-commit reading found this: the run always prints
    # "N CSV(s) carry no `value` column and were NOT checked", so the original
    # assertion passed whether or not the per-trace table was detected. Parse
    # the number.
    m = re.search(r"(\d+) CSV\(s\) carry no `value` column", out)
    assert m, f"the run must report how many CSVs were skipped, got: {out[:200]}"
    assert int(m.group(1)) >= 1, (
        "the per-trace table has no `value` column and must be counted as "
        "skipped; a silence about it would read as coverage")


def test_the_blind_region_is_stated_in_the_docstring(mv):
    """The plant that FAILED must stay documented, or the next reader repeats it.

    A number that was never a committed cell is undetectable here, and three
    of the 2026-08-29 defects were exactly that. A docstring naming three
    blind regions, none of which was the live one, is what this pins against.
    """
    doc = mv.__doc__ or ""
    assert "THE PLANT FAILED" in doc
    assert "never" in doc.lower() and "ref:" in doc
