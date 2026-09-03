"""The producer lock, and the failure that bought it.

Two producers were each launched twice on 2026-08-27/28 while the first launch
was still running, eighteen minutes apart, and both pairs wrote the same CSV
concurrently. The rule requiring a lock on any long job was already written in
this repository, and was broken twice in one night by the person who wrote it,
which is the argument for a lock over a reminder.

The shape of the damage is what makes it worth a guard: a CSV written by two
processes at once is still a VALID CSV, so no downstream check can see that it
is a mixture of two runs.

Checked both ways: with the lock held, a second acquisition exits 3 and names the
holding pid; with it released, the same call exits 0.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _producer_lock import LOCK_DIR, producer_lock  # noqa: E402

CHILD = """
import sys
sys.path.insert(0, {scripts!r})
from _producer_lock import producer_lock
with producer_lock("pytest_lock_probe"):
    print("acquired")
"""


def _child() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", CHILD.format(scripts=str(ROOT / "scripts"))],
        capture_output=True, text=True, cwd=ROOT)


def test_a_second_holder_is_refused_while_the_lock_is_held():
    with producer_lock("pytest_lock_probe"):
        r = _child()
    assert r.returncode == 3, r.stderr
    assert "holds this producer's lock" in r.stderr


def test_the_lock_is_released_and_the_next_run_proceeds():
    with producer_lock("pytest_lock_probe"):
        pass
    r = _child()
    assert r.returncode == 0, r.stderr
    assert "acquired" in r.stdout


def test_a_leftover_lock_file_from_a_dead_process_does_not_block():
    """There is no stale state to recover from, which is the point of flock.

    The first implementation kept an O_EXCL file and recovered from a dead
    holder by reading its pid and unlinking. That path has a measured race:
    29 of 30 contended trials raised an unhandled EEXIST and one produced a
    DOUBLE ACQUISITION, because two callers can both judge the pid dead and
    the second then unlinks the winner's fresh lock.

    The kernel releases an flock when the process dies by any means, SIGKILL
    included, so a leftover FILE is just a file and carries no lock at all.
    """
    LOCK_DIR.mkdir(exist_ok=True)
    leftover = LOCK_DIR / "pytest_lock_probe.lock"
    leftover.write_text("999999")        # a pid that cannot be alive
    try:
        r = _child()
        assert r.returncode == 0, r.stderr
    finally:
        leftover.unlink(missing_ok=True)


def test_two_racing_processes_never_both_acquire():
    """The contention test, run against PROCESSES because flock is per-fd.

    Two threads in one process share an open file description and would both
    succeed, which is not the population this lock protects: the failure it
    exists for is two `python scripts/run_*.py` invocations.
    """
    child = (
        "import sys, time\n"
        f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
        "from _producer_lock import producer_lock\n"
        "with producer_lock('pytest_race_probe'):\n"
        "    print('ACQUIRED', flush=True)\n"
        "    time.sleep(0.4)\n")
    procs = [subprocess.Popen([sys.executable, "-c", child], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=ROOT) for _ in range(2)]
    outs = [p.communicate() for p in procs]
    acquired = sum(1 for out, _ in outs if "ACQUIRED" in out)
    codes = sorted(p.returncode for p in procs)
    (LOCK_DIR / "pytest_race_probe.lock").unlink(missing_ok=True)
    assert acquired == 1, f"{acquired} processes acquired the same lock"
    assert codes == [0, 3], codes


def test_the_lock_is_released_even_though_the_file_remains():
    """Under flock the FILE persisting is correct and carries no lock.

    This test asserted the file was unlinked on release, which was true of the
    O_EXCL implementation and is the wrong thing to assert now. What matters
    is not whether a file exists but whether the next run can proceed, so that
    is what it checks.
    """
    with producer_lock("pytest_lock_probe"):
        assert _child().returncode == 3
    assert _child().returncode == 0


def test_every_results_producer_that_takes_minutes_holds_a_lock():
    """The producers that write `results/` and run for minutes hold a lock.

    Named explicitly rather than globbed, because a glob over `scripts/` would
    demand a lock from the fast annotators and figure drawers too, and a guard
    that fires on things it should not is a guard people switch off.

    THE NAME SAYS "EVERY" AND THE POPULATION IS A HAND-MAINTAINED LIST, which
    a reader named as a completeness claim the guard cannot make. Both
    halves are true and the tension is the point: this cannot be derived,
    because "takes minutes" is a property of running the thing, not of reading
    it. The list IS the population, and a new slow producer joins it only by
    an edit to this tuple.

    **THE OBLIGATION THAT FOLLOWS, stated here because nothing else can see
    it**: adding a producer that writes `results/` and runs for more than a
    few seconds means adding it below in the SAME commit. Nothing detects the
    omission. This wave's producers all TAKE the lock, and three of them were
    absent from the list, so the guard was passing over them rather than
    checking them. They are named below now.

    THE POPULATION IS NAMED HERE AND IT IS NOT ALL OF `scripts/`. It is the
    guided producers, which collided in fact, plus the heavy fitters that
    `verify_results_fresh.py` names as taking minutes and needing the raw
    traces. The docstring said "the four" while the tuple held four and the
    tree held more; a lock that reaches the forecast producers and not the
    fitters leaves the headline coefficients unprotected, which is the
    corruption this mechanism exists to prevent. Adding a producer that writes
    `results/` and runs for minutes means adding it here.
    """
    # A SET, not a tuple, and sorted: the tuple carried
    # run_campaign_twin_forecast, run_onf_candidate and
    # run_guided_mode_tables TWICE, which a membership test cannot
    # notice and which made the population look larger than it was.
    slow = {
        "run_beta_self", "run_campaign_twin_forecast",
        # found by the reverse check below on its first run: three
        # producers held the lock and were absent from this set, which
        # is the omission the docstring above says nothing detects
        "run_cumulant_window_check", "run_estimator_duel",
        "run_fit_window_scan", "run_fibre_twin",
        "run_global_fit", "run_guided_mode_tables", "run_linefit",
        "run_onf_candidate", "run_onf_lever_ranking", "run_power_sweep",
        "run_s0_block_bootstrap", "run_stark_sweep",
        "run_transit_additivity", "run_transit_mc", "run_wing_check",
        # the three pooled producers, added 2026-09-02 with the locks
        # themselves. They hold most of the machine for their whole run,
        # so a second copy started because the first looked stuck is both
        # likelier and more damaging than for any sequential producer.
        "run_global_dataset_fit", "run_paired_reference_forecast",
        "run_scenario_forecast",
    }
    missing = sorted(s for s in slow
                     if "take_producer_lock"
                     not in (ROOT / "scripts" / f"{s}.py").read_text())
    assert not missing, f"these producers write results/ without a lock: {missing}"
    # THE OTHER DIRECTION, which the docstring above says nothing detects.
    # A producer that TAKES the lock and is absent from this set means the
    # set is no longer the population it claims to be - which is exactly
    # what happened when three producers were locked on 2026-09-02 and
    # this guard passed anyway.
    holds = {p.stem for p in (ROOT / "scripts").glob("run_*.py")
             if "take_producer_lock(" in p.read_text()}
    unlisted = sorted(holds - slow)
    assert not unlisted, (
        "these producers hold the lock and are not in the set above, so "
        f"the set has stopped being the population it names: {unlisted}")


@pytest.fixture(autouse=True)
def _clean():
    yield
    (LOCK_DIR / "pytest_lock_probe.lock").unlink(missing_ok=True)
