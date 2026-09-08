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
