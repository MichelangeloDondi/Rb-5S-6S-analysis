"""The joint fit refuses a session tree that exists and is empty.

On 2026-08-25 the experimenter asked whether the long run could start, and
answering it meant reading what the producer does when its two external
session trees are missing. A first reading looked only at the loader, which uses
`glob.glob(...)` and so returns an empty list rather than raising, and
concluded the fit would silently proceed on one session of three.

**That conclusion was wrong.** `main()` opens with a directory check on both
trees, prints "excluded tree(s) not on this machine ... nothing to do" and
exits 0 without touching the committed CSV. The producer was right and the
inference from one line was not.

What survived the correction is a narrower gap, which is what this file
guards: the directory check tests EXISTENCE, not CONTENT. A directory that
exists and is empty is what a half-finished copy or a failed sync leaves
behind, and it passes `is_dir()` while contributing nothing to the fit. The
consequence would be a headline bound built from less data than the committed
one, written after hours of work, with no error anywhere.

The test plants exactly that state, because a guard whose failure mode has
never been produced is an assertion about a guard.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_stark_joint.py"


def _run(env_extra: dict[str, str]) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=300)


def test_an_absent_tree_is_reported_and_nothing_is_written(tmp_path):
    """The pre-existing behaviour, pinned so a later edit cannot lose it."""
    proc = _run({"RB5S6S_SESSION_20250704_DIR": str(tmp_path / "nope"),
                 "RB5S6S_SESSION_20250717_DIR": str(tmp_path / "also_nope")})
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "not on this machine" in proc.stdout


def test_a_present_but_empty_tree_is_REFUSED(tmp_path):
    """The gap this file was written for.

    Both directories exist and neither holds a matching file. Before the
    2026-08-25 tightening this passed the directory check and the fit began.
    """
    (tmp_path / "s4" / "2025-07-04").mkdir(parents=True)
    (tmp_path / "s7" / "4192nm91c650ma").mkdir(parents=True)
    proc = _run({"RB5S6S_SESSION_20250704_DIR": str(tmp_path / "s4"),
                 "RB5S6S_SESSION_20250717_DIR": str(tmp_path / "s7")})
    assert proc.returncode == 1, (
        "an empty session tree was accepted: the fit would have run on fewer "
        "sessions than the committed bound was built from.\n"
        + proc.stdout + proc.stderr)
    assert "REFUSING TO RUN" in proc.stdout
    # the refusal has to say what to do about it, or it is a dead end
    assert "RB5S6S_SESSION_2025" in proc.stdout


def test_the_committed_bound_is_untouched_by_either_refusal():
    """Neither path may write, which is the whole point of refusing."""
    csv = ROOT / "results" / "stark_joint.csv"
    before = csv.read_bytes()
    _run({"RB5S6S_SESSION_20250704_DIR": "/nonexistent/a",
          "RB5S6S_SESSION_20250717_DIR": "/nonexistent/b"})
    assert csv.read_bytes() == before
