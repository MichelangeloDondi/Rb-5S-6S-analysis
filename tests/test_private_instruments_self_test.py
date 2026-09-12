"""The private instruments' plants are RE-RUNNABLE from the suite, so a guard
never sits in the archive as an asserted instrument (the rule file: "a guard
is an asserted instrument until its plant is re-runnable").

Three instruments landed on 2026-09-12 with a `--self-test` and nothing in the
suite ran it: the seconds floor (`precheck.py`, the pre-commit hook's refusal),
the Pareto of the defect classes (`pareto_report.py`, read at every checkpoint)
and the replaced-literal sweep (`replaced_literal.py`). This test wires
them: each self-test plants its check both ways and exits non-zero on a break.
Skipped in the public mirror, where `private/` does not exist.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "private" / "checks"
INSTRUMENTS = ("precheck.py", "pareto_report.py", "replaced_literal.py")


@pytest.mark.parametrize("name", INSTRUMENTS)
def test_the_instruments_self_test_passes(name):
    script = CHECKS / name
    if not CHECKS.is_dir():
        pytest.skip("no private/checks here (the public mirror)")
    assert script.is_file(), f"{name} is named here and absent on disk"
    run = subprocess.run([sys.executable, str(script), "--self-test"],
                         cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, (
        f"{name} --self-test failed:\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}")
    assert "self-test passed" in run.stdout or "self-test" in run.stdout, (
        f"{name} --self-test exited 0 and printed no verdict:\n{run.stdout[-500:]}")
