"""The gate's verdict sentinel, tested by exercising it rather than reading it.

WHY THIS EXISTS. Protocol rule 19.24 says to read the exit code of the gate
itself. On 2026-08-15 that rule was defeated three times in one evening by
callers of the form `./scripts/ci_gate.sh > log; echo "EXIT: $?"`, which
reports the echo's status, and once more by `check_invariants.py | tail -3`,
which reports tail's. Every one read green over a red run.

Audit 5 had already recorded the general finding: of the rules written that
week, the only ones that ran without their author were the MECHANISED ones. A
habit that has been broken four times is not a control. So `ci_gate.sh` now
writes its verdict where a later shell construct cannot reach it, and this
test pins the behaviour that makes that worth relying on.

The sentinel block is EXTRACTED FROM THE SCRIPT rather than restated here, so
that editing the script's mechanism breaks this test instead of silently
leaving it testing a copy that no longer exists.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[1] / "scripts" / "ci_gate.sh"


def _sentinel_block() -> str:
    """The verdict lines from the real script, from GATE_VERDICT to the trap."""
    text = GATE.read_text()
    start = text.index("GATE_VERDICT=")
    end = text.index("EXIT\n", start) + len("EXIT\n")
    return text[start:end]


def _run(cmd: str, tmp_path: Path, caller: str = "{probe}") -> str:
    """Run the extracted sentinel around `cmd`, then read the verdict file.

    `caller` models how a careless caller invokes the gate, e.g. piping it.
    """
    verdict = tmp_path / "verdict"
    probe = tmp_path / "probe.sh"
    probe.write_text("set -euo pipefail\n" + _sentinel_block() + cmd + "\n")
    invocation = caller.format(probe=f"bash {probe}")
    subprocess.run(["bash", "-c", invocation], capture_output=True,
                   env={"CI_GATE_VERDICT_FILE": str(verdict), "PATH": "/usr/bin:/bin"})
    return verdict.read_text().strip() if verdict.exists() else "<absent>"


def test_the_extracted_block_is_the_real_one():
    """If the script stops carrying a sentinel, this test must not pass quietly."""
    block = _sentinel_block()
    assert "printf 'RUNNING\\n'" in block, "the pre-write is what makes a crash safe"
    assert "trap" in block and "EXIT" in block
    assert "PASS 0" in block and "FAIL" in block


def test_a_passing_run_records_pass(tmp_path):
    assert _run("true", tmp_path) == "PASS 0"


def test_a_failing_run_records_the_real_status(tmp_path):
    assert _run("exit 3", tmp_path) == "FAIL 3"


def test_a_trailing_echo_cannot_mask_a_failure(tmp_path):
    """The 2026-08-15 defeat, three times in one evening."""
    assert _run("exit 3", tmp_path, caller="{probe} > /dev/null; echo done") == "FAIL 3"


def test_a_pipe_cannot_mask_a_failure(tmp_path):
    """The same trap in the other direction, `checker | tail`.

    This is the case worth having a test for: the shell genuinely reports 0
    here, so nothing at the call site could have caught it.
    """
    masked = subprocess.run(["bash", "-c", "(exit 7) | tail -1"])
    assert masked.returncode == 0, "if this ever fails, the shell changed, not us"
    assert _run("exit 7", tmp_path, caller="{probe} 2>&1 | tail -1") == "FAIL 7"


def test_an_interrupted_run_never_reads_as_a_pass(tmp_path):
    """A killed gate leaves RUNNING, which is the whole point of pre-writing."""
    assert _run("kill -9 $$", tmp_path) == "RUNNING"


def test_a_stale_verdict_cannot_be_read_as_this_run(tmp_path):
    """A previous run's PASS must not survive into a run that dies early."""
    verdict = tmp_path / "verdict"
    verdict.write_text("PASS 0\n")
    assert _run("kill -9 $$", tmp_path) == "RUNNING"


def test_the_verdict_file_is_ignored_by_git():
    """It is run state. A tracked one would differ per machine and per run."""
    root = GATE.parents[1]
    assert ".ci_gate_verdict" in (root / ".gitignore").read_text()
    out = subprocess.run(["git", "-C", str(root), "check-ignore", ".ci_gate_verdict"],
                         capture_output=True, text=True)
    if out.returncode == 128:
        pytest.skip("not a git checkout")
    assert out.returncode == 0, ".ci_gate_verdict is not actually ignored"
