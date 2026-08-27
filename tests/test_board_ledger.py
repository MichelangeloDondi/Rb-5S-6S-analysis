"""The board ledger's own claims, tested against synthetic failures.

WHY THIS EXISTS. `private/checks/board_ledger.py` was written to close a
lapse: LOGIC 0c says five board seats read the staged diff before every
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


FIVE = ["rules", "protocols", "propagation", "physics", "strategy"]
CONFIRMS = ["CONFIRM"] * 5


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
        bl.record(FIVE, ["CONFIRM", "CONFIRM", "CONFIRM", "CONFIRM", "LGTM"])
    assert "verdict" in str(e.value)


def test_a_release_needs_its_two_extra_seats(bl, repo):
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    with pytest.raises(SystemExit) as e:
        bl.record(FIVE, CONFIRMS, release=True)
    assert "voice" in str(e.value) and "cold_reader" in str(e.value)


def test_a_full_board_records_and_confers_coverage(bl, repo):
    """The positive control: without it the tests above pass on a no-op."""
    _point_at(bl, repo)
    (repo / "a.txt").write_text("three\n")
    _run(repo, "add", "-A")
    tree = bl.record(FIVE, CONFIRMS, note="planted")
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
        bl.record(FIVE, CONFIRMS)
    assert "index matches HEAD" in str(e.value)
