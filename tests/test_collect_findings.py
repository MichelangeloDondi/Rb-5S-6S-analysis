"""The round collector groups the seats' findings and measures the round.

`private/checks/collect_findings.py` reads each report's machine-readable
block into the ledger's `--blocking` string and writes the round's yield
sidecar, so a round's duplication across seats is a number rather than an
impression (round one of 2026-09-08: about sixty raw findings, twenty-six
distinct, measured after the fact by hand). Its own self-test is the plant.

SKIPPED WHERE `private/` IS ABSENT, which is every clone but this one.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "private" / "checks" / "collect_findings.py"

pytestmark = pytest.mark.skipif(
    not SRC.is_file(),
    reason="private/checks/collect_findings.py is absent, as it is in every "
           "clone but the archive")


def test_the_collector_groups_duplicates_and_keeps_the_worst_severity():
    r = subprocess.run([sys.executable, str(SRC), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout + r.stderr


def test_the_collector_reads_a_round_into_a_blocking_string(tmp_path):
    (tmp_path / "a.md").write_text("report\n- SEVERE | the guard reads one line | tests/x.py:107 | grep\n")
    (tmp_path / "b.md").write_text("report\n- CRITICAL | the guard reads one line not paragraphs | tests/x.py:105 | replay\n")
    (tmp_path / "b.PROMPT.md").write_text("- CRITICAL | a prompt is not a report | x:1 | none\n")
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "CRITICAL: the guard reads one line" in r.stdout and "2 reports, 2 raw findings, 1 distinct" in r.stdout
    assert (tmp_path / "YIELD.json").is_file()


def test_the_collector_refuses_an_empty_directory_and_a_round_with_no_block(tmp_path):
    """An instrument that reads a directory refuses rather than reports zero;
    the first form printed a zero yield and wrote the sidecar (2026-09-08)."""
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 2 and "no reports" in r.stderr and not (tmp_path / "YIELD.json").exists()
    (tmp_path / "a.md").write_text("a report in prose with no block line\n")
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 2 and "no machine-readable" in r.stderr and not (tmp_path / "YIELD.json").exists()


def test_two_unrelated_findings_in_one_file_are_not_merged(tmp_path):
    """Nearness in a file is not sufficient, and the round of 2026-09-11 proved it.

    THE DEFECT: `_same` returned True on a file-and-line match alone. A round
    filed a physics finding at docs/lit/xin2018.md:72 and an unrelated
    citation finding at :74. They merged, and since only a group's worst
    severity reaches the --blocking string, the MODERATE one vanished from the
    round's record with nothing to say it had ever been filed.

    FAILURE MODE IF THIS TEST IS DELETED: a grouper silently drops findings,
    in the direction that makes a round look cleaner than it was.
    """
    (tmp_path / "physics.md").write_text(
        "report\n- SEVERE | forty-five is a linear-density ratio | docs/lit/x.md:72 | recompute\n")
    (tmp_path / "register.md").write_text(
        "report\n- MODERATE | two public notes cite a gitignored record | docs/lit/x.md:74 | git grep\n")
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    # They GROUP, because proximity is what the duplication metric wants. What
    # must not happen is that one of them vanishes: the blocking string the fix
    # pass works from carries both, because they are distinct findings.
    assert "SEVERE: forty-five is a linear-density ratio" in r.stdout
    assert "MODERATE: two public notes cite a gitignored record" in r.stdout

    # and a genuine restatement of the SAME finding is not emitted twice
    (tmp_path / "register.md").write_text(
        "report\n- MODERATE | forty-five is the wrong linear-density ratio | docs/lit/x.md:74 | git grep\n")
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert "1 distinct" in r.stdout, r.stdout
    assert r.stdout.count("linear-density ratio") == 1, r.stdout


def test_a_block_written_without_its_bullet_still_counts(tmp_path):
    """Three seats of eleven wrote the machine block with no leading '- '.

    THE DEFECT: the pattern required the bullet, so those seats' rows read 0
    raw and 0 first. A reader of the yield table takes that as a seat that
    found nothing, and one of the three had filed the round's only finding
    about the advertised-count guard's blind spot.

    FAILURE MODE IF THIS TEST IS DELETED: a seat's findings are silently
    discarded for a formatting slip, and the metrics say the seat was idle.
    """
    (tmp_path / "adoption.md").write_text(
        "report\nSEVERE | the count guard cannot see a two-digit number | tests/x.py:1113 | read the regex\n")
    r = subprocess.run([sys.executable, str(SRC), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "1 raw findings, 1 distinct" in r.stdout, r.stdout
    assert "SEVERE: the count guard cannot see a two-digit number" in r.stdout
