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


PARALLEL = ROOT / "private" / "checks" / "parallel_budget.py"


@pytest.mark.skipif(not PARALLEL.is_file(), reason="private/ is absent")
def test_the_parallel_budget_refuses_to_oversubscribe_this_machine():
    """The worker count beside a gate is measured, and its own plant runs here.

    WHY IT EXISTS (owner, 2026-09-11). The rule that a gate and a computation
    belong on opposite halves of this machine was in the rule file and was not
    followed, because the number it turns on, how many workers fit beside
    whatever is running, was left to be recalled. A rule whose quantity is
    recalled is a rule that gets skipped when the recall is inconvenient.

    FAILURE MODE IF THIS TEST IS DELETED: the budget stops subtracting the
    gate's own footprint, a pool is sized as though the machine were idle, and
    this part goes into swap, which is A186: the gate took 0.4 seconds of CPU
    in six minutes and the producer's progress line stood still for 1500
    seconds, and the obvious story was the wrong one.
    """
    proc = subprocess.run([sys.executable, str(PARALLEL), "--self-test"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (
        "the parallel budget's own plant failed:\n" + proc.stdout + proc.stderr)

    sys.path.insert(0, str(PARALLEL.parent))
    try:
        import parallel_budget as pb
    finally:
        sys.path.pop(0)

    # THE ASSERTIONS ARE INVARIANTS, NOT A LIVE COUNT. The first cut of this
    # test asserted the beside-a-gate budget equals the performance core count,
    # and the gate failed it within the hour: that equality holds only while
    # free memory is ample, and this test runs with a gate on the machine by
    # construction. An expectation that depends on the host's live memory is
    # the class E27 names.
    #
    # A pool is never empty and never exceeds the half of the machine it is on.
    assert pb.workers(job_gib=0.001, beside_gate=True) >= 1
    assert pb.workers(job_gib=0.001, beside_gate=True) <= pb.PERF_CORES
    # A gate never increases the budget.
    assert (pb.workers(job_gib=2.0, beside_gate=True)
            <= pb.workers(job_gib=2.0, beside_gate=False))
    # A heavier job never gets more workers, and memory binds for a huge one.
    assert (pb.workers(job_gib=8.0, beside_gate=False)
            <= pb.workers(job_gib=0.001, beside_gate=False))
    assert pb.workers(job_gib=1000.0, beside_gate=False) == 1
