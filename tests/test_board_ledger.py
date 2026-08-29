"""The board ledger's own claims, tested against synthetic failures.

WHY THIS EXISTS. `private/checks/board_ledger.py` was written to close a
lapse: LOGIC 0c says the commit team reads the staged diff before every
commit, the board ran twice on a large wave and then not at all before the
two version bumps, the two ports, or the commit after them, and nothing
noticed because nothing measured it. The ledger is the measurement.

It shipped with no test file, and a board seat reading it found two
defects the same evening. Both are the same class the repository already
names: **a mechanism asserted a property it never tested against a synthetic
instance of the failure it was built for.**

  1. `record()` fingerprinted `patch_id_of("HEAD")`. At record time HEAD is
     the PARENT -- the commit under the board does not exist yet, which is the whole
     reason the ledger keys on the staged tree. So the stored fingerprint was
     the diff the parent introduced over its own parent. The docstring's
     claim that the patch-id "survives both" was false for the case it was
     added to cover, and worse than useless: `verify()` accepts any commit
     whose patch-id is in the ledger, so a stored parent patch-id could mark
     THAT PARENT covered by a board which never read it. The instrument
     against false passes was issuing one.
  2. Neither `record()` nor `verify()` checked what an entry SAID. Recording
     a single seat satisfied coverage, so the enforcement report could print
     that a board verdict exists when one seat of five had run. The row
     measured that somebody typed a command.

These tests are written from the outside, on planted commits in a scratch
repository, so they fail on the code as it was first written rather than
merely describing it.

SKIPPED WHERE `private/` IS ABSENT, which is every clone but this one, on
the same pattern `scripts/ci_gate.sh` uses for `protocol_citations.py`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER_SRC = ROOT / "private" / "checks" / "board_ledger.py"

pytestmark = pytest.mark.skipif(
    not LEDGER_SRC.is_file(),
    reason="private/checks/board_ledger.py is absent, as it is in every "
           "clone but the archive")


@pytest.fixture
def bl():
    spec = importlib.util.spec_from_file_location("board_ledger", LEDGER_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GIT_ENV = {
    "GIT_AUTHOR_NAME": "scratch", "GIT_AUTHOR_EMAIL": "s@example.invalid",
    "GIT_COMMITTER_NAME": "scratch",
    "GIT_COMMITTER_EMAIL": "s@example.invalid",
}


def _run(repo: Path, *args: str) -> str:
    """Identity comes from the environment, so the scratch repository
    commits on a machine with no global git identity configured."""
    out = subprocess.run(["git", "-C", str(repo), *args],
                         capture_output=True, text=True,
                         env={**os.environ, **GIT_ENV})
    return out.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "scratch"
    r.mkdir()
    _run(r, "init", "-q")
    _run(r, "config", "commit.gpgsign", "false")
    (r / "a.txt").write_text("one\n")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "first")
    (r / "a.txt").write_text("two\n")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "second")
    return r


def _point_at(bl, repo: Path):
    bl.ROOT = repo
    bl.LEDGER = repo / ".board_ledger.jsonl"
    bl.OPEN = repo / ".board_running"


# Derived from the ledger's own source, NOT re-typed. A seat list written in
# two places goes stale in one, and this test pinned the old five when the
# attention seat was added on 2026-08-27. The module is loaded by path
# because private/ is not importable.
def _required_seats():
    spec = importlib.util.spec_from_file_location("_bl_seats", LEDGER_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(mod.REQUIRED_SEATS)


# THE SKIPIF ABOVE WAS DEFEATED BY THIS LINE, and only the mirror could show
# it. `pytestmark` skips TESTS; it does not stop module-level code, and this
# call loaded `private/checks/board_ledger.py` during COLLECTION. In the
# archive the file is there and everything passed, so the docstring's claim
# that these tests are "SKIPPED WHERE private/ IS ABSENT" read as true for as
# long as it was only ever read in the archive. In the public mirror, where
# `private/` cannot go, collection died and took the whole suite with it --
# which is what a stranger cloning the public repository would have met.
FULL = _required_seats() if LEDGER_SRC.is_file() else []
CONFIRMS = ["CONFIRM"] * len(FULL)


def test_the_staged_patch_id_is_the_forward_diff_not_the_parents(bl, repo):
    """The defect, stated as a three-way comparison on planted commits."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")

    stored = bl.staged_patch_id()
    parent_pid = bl.patch_id_of("HEAD")          # what the old code stored
    _run(repo, "commit", "-q", "-m", "third")
    landed = bl.patch_id_of("HEAD")              # what verify() computes

    assert stored, "the staged patch-id is empty; git patch-id did not run"
    assert stored == landed, (
        "the fingerprint recorded before the commit must equal the one "
        "verify() computes after it, or the patch-id fallback can never "
        "answer. This is the assertion the file shipped without.")
    assert parent_pid != landed, (
        "the planted commits are too similar to distinguish the parent's "
        "patch from the staged one, so this test cannot detect the defect")


def test_a_partial_board_is_refused_rather_than_recorded(bl, repo):
    """One seat used to satisfy coverage. It must now be refused outright."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    with pytest.raises(SystemExit) as e:
        bl.record(["rules"], ["CONFIRM"])
    assert "missing seat" in str(e.value)
    assert not bl.LEDGER.exists(), (
        "a refused board still wrote a ledger line, so the refusal is "
        "cosmetic and verify() would count it")


def test_an_unrecognised_verdict_is_refused(bl, repo):
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    with pytest.raises(SystemExit) as e:
        bl.record(FULL, CONFIRMS[:-1] + ["LGTM"])
    assert "verdict" in str(e.value)


def test_a_release_needs_its_two_extra_seats(bl, repo):
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    with pytest.raises(SystemExit) as e:
        bl.record(FULL, CONFIRMS, release=True)
    assert "voice" in str(e.value) and "cold_reader" in str(e.value)


def test_a_full_board_records_and_confers_coverage(bl, repo):
    """The positive control: without it the tests above pass on a no-op."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    tree = bl.record(FULL, CONFIRMS, note="planted")
    assert tree, "record() returned no tree"
    _run(repo, "commit", "-q", "-m", "third")

    covered, uncovered, _grand = bl.verify("HEAD~1..HEAD")
    assert len(covered) == 1 and not uncovered, (
        "a board recorded against the staged tree did not cover the commit "
        "made from that same index")


def test_a_nonconformant_line_confers_no_coverage(bl, repo):
    """A ledger that grandfathers its own pre-check rows measures nothing."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    tree = bl.staged_tree()
    bl.LEDGER.write_text(
        '{"tree": "%s", "seats": ["rules"], "verdicts": ["CONFIRM"]}\n' % tree,
        encoding="utf-8")
    _run(repo, "commit", "-q", "-m", "third")

    covered, uncovered, _grand = bl.verify("HEAD~1..HEAD")
    assert not covered and len(uncovered) == 1, (
        "a hand-written one-seat line was accepted as coverage, which is the "
        "exact gap the seat check was added to close")


def test_recording_with_a_clean_index_is_refused(bl, repo):
    """The retroactive hole, closed at the moment it happens.

    A reader demonstrated it: commit with no board, then call record() with
    nothing staged. `staged_tree()` then equals the already-landed commit's
    tree, so verify() scored an unread commit as covered. The file's own
    premise is that a board reads the staged diff BEFORE the commit exists,
    so a clean index means there is nothing a board could have read.
    """
    _point_at(bl, repo)
    with pytest.raises(SystemExit) as e:
        bl.record(FULL, CONFIRMS)
    assert "index matches HEAD" in str(e.value)


def test_a_refute_with_no_blocking_findings_is_refused(bl, repo):
    """0c.12. A REFUTE that declares nothing blocking can never refuse a
    further round, and the convener writing the list is the one person the
    mechanism constrains. Written after the first manual check of 2026-08-28
    left no artifact on disk, so nothing could confirm it had ever run --
    the class LOGIC 0b.5 names."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    with pytest.raises(SystemExit) as e:
        bl.record(seats, ["REFUTE"] * len(seats), blocking=[])
    assert "no blocking finding was declared" in str(e.value)
    assert not bl.LEDGER.exists()


def test_begin_refuses_while_a_blocking_finding_stands(bl, repo):
    """0c.12's second refusal: no new round over an unresolved defect."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    bl.record(seats, ["REFUTE"] * len(seats), blocking=["the planted defect"])
    with pytest.raises(SystemExit) as e:
        bl.begin(seats)
    assert "REFUSING to open a round" in str(e.value)
    # and resolution with evidence clears it
    bl.resolve("planted defect", "the fix that closed it")
    bl.begin(seats)
    assert bl.OPEN.exists()


def test_resolve_without_a_reason_is_refused(bl, repo):
    """0c.12's third refusal: a resolution with no evidence is deletion."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    bl.record(seats, ["REFUTE"] * len(seats), blocking=["the planted defect"])
    with pytest.raises(SystemExit) as e:
        bl.resolve("planted defect", "   ")
    assert "needs what fixed it" in str(e.value)


def test_a_board_that_stayed_open_across_the_commit_can_still_record(bl, repo):
    """The begin -> commit-same-tree -> record flow, which was refused.

    `begin` states that committing while a board runs on the SAME tree is
    the intended flow, and the clean-index guard refused it anyway, because
    it read the index alone: after such a commit the index equals HEAD for
    the innocent reason that the board's tree became the commit's tree. A
    twelve-seat round lost its verdict to that on 2026-08-29. The guard now
    asks whether an open board names this tree, which is what separates the
    two cases; the laundering it was built for has no such board, and
    test_recording_with_a_clean_index_is_refused still pins that.
    """
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    bl.begin(seats)
    _run(repo, "commit", "-q", "-m", "landed while the board read it")
    # nothing further staged: the index now equals HEAD
    assert bl.staged_tree() == _run(repo, "rev-parse", "HEAD^{tree}")
    bl.record(seats, ["CONFIRM"] * len(seats))
    assert bl.LEDGER.exists(), (
        "the flow begin -> commit -> record wrote no ledger line, so a board "
        "that read exactly what landed still cannot be recorded"
    )


def test_begin_on_a_tree_already_head_is_refused(bl, repo):
    """The hole the previous repair opened, closed 2026-08-29.

    `record()` admits a clean index when an OPEN BOARD names the tree, which
    is what separates the legitimate begin-commit-record flow from
    laundering. But nothing said WHEN the board could open, so opening it
    AFTER the commit satisfies that condition and the laundering sequence
    becomes commit, begin, record. The round that found it exhibited the
    shape: its commit landed at 23:53:11Z and its board opened seventeen
    seconds later.

    A repair is a claim, and this one ran in the flattering direction --
    it closed the door the reader had demonstrated and left the adjacent
    one open. So `begin` refuses a tree that is already HEAD.
    """
    _point_at(bl, repo)
    assert bl.staged_tree() == _run(repo, "rev-parse", "HEAD^{tree}")
    with pytest.raises(SystemExit) as e:
        bl.begin(sorted(bl.REQUIRED_SEATS))
    assert "already HEAD" in str(e.value)
    assert not bl.OPEN.exists()


def test_a_post_commit_review_is_admitted_but_recorded_as_one(bl, repo):
    """The false-positive direction, and it is a real case, not a courtesy.

    A RELEASE board reads an artifact that is already committed -- the note,
    the tag's tree -- so refusing every board on HEAD would forbid the one
    reading the release drill requires. It is admitted by `--on-head` with a
    reason, which is stored, so a board that read a committed tree is legible
    as one instead of looking like a board that read a staged diff.
    A guard whose only passing state is unreachable blocks its own push, and
    this record has built one of those before.
    """
    _point_at(bl, repo)
    tree = bl.begin(sorted(bl.REQUIRED_SEATS),
                    "release board on the tagged artifact")
    assert tree == _run(repo, "rev-parse", "HEAD^{tree}")
    assert bl.OPEN.exists()
    assert bl.open_board()["on_head"] == "release board on the tagged artifact"


def test_abandon_records_a_row_and_clears_the_marker(bl, repo):
    """A round that ends with no verdict closes with a row, not a deletion.

    WHY THIS EXISTS. `--abandon` shipped inline in `main()` for one round with
    no test, while every other verb here is a function the tests call
    directly. A board seat found it and was right about the cause as well as
    the fact: a verb reachable only through a subprocess will not be
    unit-tested, so it was extracted to `abandon()` and pinned here.

    An abandoned round must confer NO coverage. That is the whole reason it is
    recorded rather than deleted, so the test asserts both halves.
    """
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    tree = bl.begin(seats)
    assert bl.OPEN.exists()

    assert bl.abandon("the findings moved the tree, so no verdict is honest",
                      no_findings=True) == 0
    assert not bl.OPEN.exists(), "the marker must be cleared, or the next commit trips on it"

    rows = [json.loads(x) for x in bl.LEDGER.read_text().splitlines() if x.strip()]
    row = rows[-1]
    assert row["kind"] == "abandoned"
    assert row["tree"] == tree
    assert "moved the tree" in row["reason"]

    _run(repo, "commit", "-q", "-m", "landed after the round was abandoned")
    covered, uncovered, _g = bl.verify("HEAD~1..HEAD")
    assert not covered and len(uncovered) == 1, (
        "an abandoned round must confer no coverage; if it did, abandoning "
        "would be a cheaper way to launder a commit than recording one")


def test_abandon_refuses_without_a_reason_and_with_no_open_board(bl, repo):
    """Both refusals, because either would make the row meaningless.

    A reason-less row cannot be told from a round nobody finished, and
    abandoning nothing would write a row about a board that never opened.
    """
    _point_at(bl, repo)
    # no_findings is passed so this exercises the REASON and NO-BOARD
    # refusals rather than the findings one, which has its own test below.
    assert bl.abandon("   ", no_findings=True) == 2
    assert bl.abandon("a real reason but no board is open",
                      no_findings=True) == 1
    assert not bl.LEDGER.exists() or "abandoned" not in bl.LEDGER.read_text()


def test_abandon_must_say_what_the_round_found_or_that_it_found_nothing(bl, repo):
    """Closing a round may not discard its findings into a reason string.

    WHY THIS EXISTS. `--abandon` was added to let a round end without a
    verdict, and a board seat found the hole the same day: a convener whose
    seats returned REFUTE could close with `--abandon` INSTEAD of
    `--record`, and the findings would enter no structured check at all.
    That is the close-on-prose failure this file exists to refuse, one level
    up, and the convener is the party it constrains.

    The ledger cannot see the seat reports, so it cannot verify the list.
    What it can do is make discarding them a DECLARED act with a name.
    """
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    bl.begin(seats)
    assert bl.abandon("a reason but no account of what was found") == 2, (
        "abandoning without saying what the round found must be refused")
    assert bl.OPEN.exists(), "a refused abandon must not close the board"

    assert bl.abandon("the tree moved under the seats",
                      blocking=["a defect the round found"]) == 0
    assert bl.unresolved_blocking() == ["a defect the round found"], (
        "an abandoned round's findings must still stand; if they did not, "
        "abandoning would be a cheaper way to clear a refusal than fixing it")


def test_a_row_without_findings_does_not_clear_a_standing_refusal(bl, repo):
    """The near miss: `rounds[-1]` trusted that the newest line is a verdict.

    The specific bypass was NOT reachable, because record() clears the marker
    and begin() refuses while findings stand, so no board exists to abandon.
    The guard held by an accident of ordering. This pins it at the accident,
    by appending a findings-free row directly and asserting the earlier
    round's findings survive it.
    """
    _point_at(bl, repo)
    (repo / "a.txt").write_text("four\n")
    _run(repo, "add", "-A")
    seats = sorted(bl.REQUIRED_SEATS)
    bl.record(seats, ["REFUTE"] * len(seats), blocking=["the standing defect"])
    assert bl.unresolved_blocking() == ["the standing defect"]

    with bl.LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"kind": "abandoned", "reason": "no findings key"})
                 + "\n")
    assert bl.unresolved_blocking() == ["the standing defect"], (
        "a row carrying no findings must not clear a standing refusal")


def test_a_second_record_on_one_reading_is_refused(bl, repo):
    """One reading is one row, or verify() counts the same board twice.

    A seat found that `record` never asked whether this tree already carried a
    verdict. THE FIRST REPAIR WAS WRONG in a way worth pinning: it demanded an
    OPEN board on every record and ran ahead of every other refusal in the
    function, so eight tests asserting on "missing seat", "index matches HEAD"
    and "a REFUTE declaring nothing" received that message instead. A guard
    placed ahead of its siblings does not add a check, it replaces them. This
    pins both halves: the duplicate is refused, and the sibling refusals still
    reach their own cases.
    """
    _point_at(bl, repo)
    (repo / "a.txt").write_text("four\n")
    _run(repo, "add", "-A")
    assert bl.record(FULL, CONFIRMS, note="first reading")

    with pytest.raises(SystemExit) as e:
        bl.record(FULL, CONFIRMS, note="second reading, same tree")
    assert "already carries a recorded verdict" in str(e.value)

    # AND THE SHADOWING ARM: a DIFFERENT tree with a short seat list must
    # still fail on the seat list, not on this guard.
    (repo / "a.txt").write_text("five\n")
    _run(repo, "add", "-A")
    with pytest.raises(SystemExit) as e:
        bl.record(["rules"], ["CONFIRM"])
    assert "already carries" not in str(e.value), (
        "the duplicate guard shadowed the seat-list refusal, which is the "
        "defect the first repair introduced")
