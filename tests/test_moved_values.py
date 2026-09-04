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
    bound = [
        "| quantity | value | date | construction | what moved it | standing |",
        "|---|---|---|---|---|---|",
        "| beam waist | 0.611 | 2026-07-13 | a note | arithmetic | retracted |",
    ]
    assert mv.history_now_columns(bound)[2] == set(), (
        "a bound-history row is a value as recorded on its date, retired by "
        "design; no cell of it is a live claim")
    dated = [
        "| quantity | value | date | file |",
        "|---|---|---|---|",
        "| the width | 0.611 | 2026-07-13 | `results/m.csv` |",
    ]
    assert mv.history_now_columns(dated)[2] == {0, 1, 2, 3}, (
        "a table with a date column and no standing column is not a bound "
        "history: every cell is graded (the carve-out needs both names, "
        "a seat reverted it in a clone and the suite stayed green, 2026-09-04)")
    apparatus = [
        "| date | etalon lock | ref-cav lock | ecd lock |",
        "|---|---|---|---|",
        "| 2026-08-16 | locked | 0.611 | free |",
    ]
    assert mv.history_now_columns(apparatus)[2] == {0, 1, 2, 3}, (
        "a live apparatus log with a date column (docs/APPARATUS.md carries "
        "three) is graded in every cell")
    standing_only = [
        "| quantity | value | standing |",
        "|---|---|---|",
        "| the width | 0.611 | open |",
    ]
    assert mv.history_now_columns(standing_only)[2] == {0, 1, 2}, (
        "a standing column alone is not a bound history either")


def test_the_hub_index_is_graded_by_its_now_cell_like_the_chapter_tables(mv, repo, capsys):
    """docs/HISTORY.md is the same table as the chapter tables and joined the
    now-cell rule on 2026-09-04, when two of its rows carried a retired literal
    in their title and was cells at a board's open."""
    _point_at(mv, repo)
    base = _run(repo, "rev-parse", "HEAD~1").strip()  # the fixture's first commit, before the values moved
    hub = repo / "docs" / "HISTORY.md"
    hub.write_text("| quantity | was | now | live value in |\n|---|---|---|---|\n"
                   "| the mode area (0.611 in the title) | 0.611 | 0.615 | `results/m.csv` |\n")
    (repo / "docs" / "note.md").write_text("Quoting `results/m.csv`: the area is 0.615 um^2.\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-q", "-m", "the hub row and a corrected note")
    rc = mv.main(["check_moved_values.py", base])
    assert rc in (0, 2), capsys.readouterr().out
    hub.write_text("| quantity | was | now | live value in |\n|---|---|---|---|\n"
                   "| the mode area | 0.615 | 0.611 | `results/m.csv` |\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-q", "-m", "a stale now cell")
    rc = mv.main(["check_moved_values.py", base])
    out = capsys.readouterr().out
    assert rc == 1 and "docs/HISTORY.md" in out, out


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
    assert "rounded-copy" in doc.lower() and "markdown only" in doc.lower(), "the advisory's blind region (markdown only) must be stated in the docstring"


# --- appended 2026-09-04 by the landing board's second round (concision seat, SEVERE:
# the advisory shipped without a test) -----------------------------------------
def test_rounded_forms_round_half_up_and_keep_every_collision():
    """The rounded-copy advisory's core: a retired literal's two-decimal form is
    the writer's rounding (half-up: 0.415 is 0.42, not the binary 0.41), a
    literal with fewer than three significant digits or a band is skipped, and
    two literals that round alike are BOTH kept under the one key (0.386 and
    0.393 both round to 0.39; the first version silently dropped one, a near
    miss the physics seat measured). Failure mode if this regresses: a rounded
    echo of a retired cell passes the scan, which is how four of them lived on a
    wiki page through a clean run on 2026-09-04 (private/ANALYSIS_FINDINGS_2026-09-03.md, A26)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cm", ROOT / "scripts" / "check_moved_values.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    retired = {"0.415": ("a", "0.527", True), "0.386": ("b", "0.492", True), "0.393": ("c", "0.497", True),
               "0.5": ("d", "0.6", True), "1.08 to 1.25": ("e", "row", True), "0.201": ("f", "0.494", True)}
    out = m._rounded_forms(retired)
    assert out["0.42"] == ["0.415"]
    assert sorted(out["0.39"]) == ["0.386", "0.393"], "a collision must keep both literals"
    assert out["0.20"] == ["0.201"]
    assert "0.50" not in out and "0.5" not in out, "fewer than three significant digits is not distinctive"
    assert not any(" to " in k for k in out), "bands are never rounded"


def test_prose_under_a_results_page_row_inherits_its_file_and_a_second_page_does_not(mv, repo, capsys):
    """The per-line rule for pages under results/ (2026-09-04): a line naming
    no file inherits the nearest earlier row's CSVs, a row of another file
    keeps its own numbers, and the inheritance is reset per page. The fixture
    covers both directions: a bullet under a table row that quotes a
    retired value without naming the file (must be found), and the first
    line of the NEXT page quoting the same digits (must not be attributed to
    the previous page's file)."""
    _point_at(mv, repo)
    (repo / "results" / "A.md").write_text(
        "| `results/m.csv` | the mode area | 0.615 um^2 |\n"
        "\n"
        "* the area is 0.611 um^2 in the row above, a stale copy quoted with no file named\n")
    (repo / "results" / "B.md").write_text(
        "0.611 is a number of this page's own, naming no file, and must not inherit A's\n"
        "\n"
        "| `results/m.csv` | the mode area | 0.615 um^2 |\n")
    _run(repo, "add", "-A")   # the scan's population is git-defined: an unadded page is invisible to it
    assert mv.main(["check_moved_values.py", "HEAD~1"]) == 1
    out = capsys.readouterr().out
    assert "results/A.md" in out and "0.611" in out, "the bullet under A's row must be found through the inheritance"
    assert "results/B.md" not in out, "the inheritance leaked across the page boundary"


def test_a_base_that_is_not_a_commit_is_refused_with_the_reason(mv, repo, capsys):
    """A tree hash resolves as an object but cannot bound git log; the scan used to accept it
    and report a false completeness (2026-09-04). It now says so and falls back."""
    _point_at(mv, repo)
    tree = _run(repo, "write-tree").strip()
    rc = mv.main(["check_moved_values.py", tree])
    out = capsys.readouterr().out
    assert rc == 1, "the fixture's moved value is a finding, so the scan exits 1 after the fallback"
    assert "0.611" in out, "after the fallback the scan must still find the fixture's moved value"
    assert "as a commit" in out and "falling back" in out
