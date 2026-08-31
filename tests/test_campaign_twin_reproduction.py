"""The twin example must keep reprinting its five checks under its seeds.

T1 merged the example's world builder into `rb5s6s.forecast`, and the merge
was licensed to change NOTHING the example prints: the five checks are the
twin's standing validation of the record against itself, and a refactor
that moves their numbers has changed the physics, not the plumbing. This
test runs `examples/campaign_twin.py` and compares every number in its
output against `tests/_campaign_twin_expected.txt`, captured from the
pre-merge builder on 2026-08-31 and identical to the post-merge output.

Failure mode it exists for: a quiet drift of the promoted builder -- a
default that moves, an RNG call reordered, a layer decoupled from its
constant -- which would leave the example running green while forecasting a
different campaign. Numbers compare to a stated tolerance (2e-2 absolute)
rather than byte-identity so a BLAS least-squares digit on another platform
cannot fail it; the verdict words compare exactly. A LEGITIMATE change to
the example updates the expected file in the same commit, with the shift
logged against the old output in the message, never waved through.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = Path(__file__).parent / "_campaign_twin_expected.txt"

NUM = re.compile(r"-?\d+\.\d+")
TOL = 2e-2


@pytest.mark.slow
def test_the_twin_reprints_its_checks():
    run = subprocess.run([sys.executable, str(ROOT / "examples" / "campaign_twin.py")],
                         capture_output=True, text=True, cwd=ROOT, timeout=1200)
    assert run.returncode == 0, f"the twin example itself failed:\n{run.stdout}\n{run.stderr}"
    got_lines = [ln for ln in run.stdout.splitlines() if ln.strip()]
    want_lines = [ln for ln in EXPECTED.read_text(encoding="utf-8").splitlines()
                  if ln.strip()]
    assert len(got_lines) == len(want_lines), (
        f"the twin printed {len(got_lines)} lines against {len(want_lines)} "
        "expected: its report changed shape, which is a physics or wiring "
        "change, not noise")
    for got, want in zip(got_lines, want_lines):
        g_nums = [float(x) for x in NUM.findall(got)]
        w_nums = [float(x) for x in NUM.findall(want)]
        assert len(g_nums) == len(w_nums), f"number count moved on: {want!r}"
        for g, w in zip(g_nums, w_nums):
            assert abs(g - w) <= TOL, (
                f"a check's number moved past {TOL}: {w} -> {g} on line\n"
                f"  {want!r}")
        assert NUM.sub("#", got) == NUM.sub("#", want), (
            f"the words around the numbers changed:\n  want {want!r}\n"
            f"  got  {got!r}")
    assert any("VERDICT: PASS" in ln for ln in got_lines)
