"""The governance instruments' own plants run, here, in the suite.

WHY THIS TEST EXISTS. `private/checks/instrument_msa.py` measures how many
governance instruments carry a re-runnable validation and runs each one it
finds. Nothing ran IT, and a harness nothing runs is exactly the class it was
written to measure: a plant that has stopped discriminating without saying so.
Wiring it here puts every plant in the suite, so a broken refusal fails the
gate rather than waiting for someone to think of checking.

The archive-only skip is deliberate: `private/` is absent from the public
mirror, and its absence there is correct rather than a failure.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MSA = ROOT / "private" / "checks" / "instrument_msa.py"


@pytest.mark.skipif(not MSA.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_every_governance_plant_still_discriminates():
    """Run instrument_msa, which runs every plant it can find.

    A non-zero exit means one of the planted refusals no longer fires. That is
    worse than an unplanted instrument, because the coverage number counts it
    as validated while it validates nothing.
    """
    proc = subprocess.run([sys.executable, str(MSA)],
                          capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0, (
        "a governance plant failed, so a refusal it covers has stopped "
        "firing:\n" + proc.stdout[-3000:] + proc.stderr[-2000:])


@pytest.mark.skipif(not MSA.is_file(), reason="private/ is absent")
def test_the_coverage_reading_is_present_and_honest():
    """The harness must report a fraction, not fall silent.

    Its own failure once printed as a value rather than as NOT MEASURED, which
    is the self-report class the whole exercise is about.
    """
    proc = subprocess.run([sys.executable, str(MSA)],
                          capture_output=True, text=True, timeout=600)
    line = next((ln for ln in proc.stdout.splitlines()
                 if "governance instruments carry" in ln), "")
    assert line, "instrument_msa printed no coverage reading at all"
    assert "per cent)" in line, f"the reading lost its fraction: {line!r}"
