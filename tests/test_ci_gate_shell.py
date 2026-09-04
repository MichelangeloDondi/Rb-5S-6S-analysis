"""The gate's advisory stanza is driven under the gate's own shell options.

On 2026-09-04 the landing board found `advisory_chapter_check` dead on every
exit code but zero: under `set -euo pipefail` a plain assignment from a failing
command substitution ends the script before the exit code is read, so a missing
chapter crashed the gate instead of skipping and a divergence failed it with no
diagnostics. The convener's plant had run the stanza WITHOUT the preamble and
passed. This test extracts the stanza from scripts/ci_gate.sh verbatim, prefixes
the file's own `set -euo pipefail`, points it at fake checkers exiting 0, 1, 2
and 3, and asserts what the stanza's comment promises: 0 passes silently, 2
prints a skip and continues, 1 and 3 print a FAIL with the checker's tail and
exit 1, and every call leaves its line in the advisory sink. Failure mode if it
regresses: the chapter checkers are wired in name and inert in effect.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "ci_gate.sh"


def _stanza() -> str:
    text = GATE.read_text(encoding="utf-8")
    m = re.search(r"ADVISORY_SINK=.*?advisory_chapter_check private/checks/check_chapter_xrefs\.py\n(?:#[^\n]*\n)*(?:sed [^\n]*ADVISORY_SINK[^\n]*\n)?", text, re.S)
    assert m, "the advisory stanza is not where this test expects; read scripts/ci_gate.sh"
    return m.group(0)


def _run(tmp_path: Path, rc_bib: int, rc_xrefs: int):
    (tmp_path / "private" / "checks").mkdir(parents=True)
    (tmp_path / "private/checks/check_chapter_bibliography_sync.py").write_text(f"import sys; print('bib last line'); sys.exit({rc_bib})\n")
    (tmp_path / "private/checks/check_chapter_xrefs.py").write_text(f"import sys; print('xrefs last line'); sys.exit({rc_xrefs})\n")
    script = "set -euo pipefail\nPY=python3\nGATE_ROOT=\"$PWD\"\n" + _stanza() + "echo AFTER_STANZA\n"
    r = subprocess.run(["bash", "-c", script], cwd=tmp_path, capture_output=True, text=True, env={**os.environ, "PATH": os.environ["PATH"]})
    sink = (tmp_path / ".ci_gate_advisory").read_text() if (tmp_path / ".ci_gate_advisory").exists() else ""
    return r, sink


def test_exit_zero_passes_and_sinks(tmp_path):
    r, sink = _run(tmp_path, 0, 0)
    assert r.returncode == 0 and "AFTER_STANZA" in r.stdout
    assert "ci_gate: advisory: check_chapter_xrefs exit 0" in r.stdout, "the sink must be printed into the gate's own log"
    assert "check_chapter_bibliography_sync exit 0" in sink and "check_chapter_xrefs exit 0" in sink


def test_exit_two_skips_and_continues(tmp_path):
    r, sink = _run(tmp_path, 2, 0)
    assert r.returncode == 0, r.stderr
    assert "skipped" in r.stdout and "AFTER_STANZA" in r.stdout
    assert "check_chapter_bibliography_sync exit 2" in sink


@pytest.mark.parametrize("rc", [1, 3])
def test_a_divergence_fails_with_its_tail(tmp_path, rc):
    r, sink = _run(tmp_path, 0, rc)
    assert r.returncode == 1, "a divergence must fail the gate with exit 1, not with the checker's raw code"
    assert "ci_gate: FAIL" in r.stderr and "xrefs last line" in r.stderr
    assert "AFTER_STANZA" not in r.stdout
    assert f"ci_gate: advisory: check_chapter_xrefs exit {rc}" in r.stdout, "the sink is printed on the failing path too"
    assert f"check_chapter_xrefs exit {rc}" in sink
