"""The scenario forecast's pooled path: the property its byte-identity
rests on, pinned so an edit cannot quietly break it.

WHY A SEPARATE FILE AND NOT A MEASUREMENT. The producer reproduces its
committed CSV at 0, 3 and 8 workers - measured 2026-09-02 - but a
measurement taken once protects nothing: `forecast_precision` and
`_one_trial` are shared machinery, and an edit there could make the
pooled path diverge with no guard between it and a reader trusting a
committed file. Running the whole producer twice per suite is a minute
of gate time for a property that is decidable in milliseconds, so what
is pinned here is the MECHANISM: each task's forecasts depend only on
that task's own seed, so the order tasks run in cannot change any
result, and a pool imposes exactly an order.

The measurement remains reproducible by hand and the command is worth
carrying:

    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_scenario_forecast.py
    git diff --stat results/scenario_forecast.csv     # must be empty

Failure mode guarded: a shared-machinery edit that makes a pooled
producer's output depend on the worker count, which the freshness
check cannot see because it only ever runs the sequential path.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_PROD = ROOT / "scripts" / "run_scenario_forecast.py"

# THE SHARED LOADER, not a local copy of the idiom. Building a module
# object and registering it with `setdefault` gives the SECOND file to
# collect an object that is not the one in `sys.modules`, and a pool
# cannot pickle a function through it. That failed for the paired
# producer in one collection order and passed in the other.
from conftest import load_script_module        # noqa: E402

_sf = load_script_module("run_scenario_forecast", _PROD)


def _tiny_task(seed: int):
    """One task's arguments at a deliberately small trial count: the
    property under test is order-independence, not precision, and two
    trials show it as well as sixteen."""
    truth = {"gamma_coll": 1.2, "sigma_laser": 0.4,
             "transit_fwhm": 0.9, "s0": 0.35}
    design = {"noise": 0.01, "n_traces": 2, "n_points": 400, "T_C": 130.0}
    return (truth, design, 0.01, 0.8, seed, 2)


def test_a_task_depends_on_its_own_seed_and_not_on_what_ran_before():
    """Two tasks, evaluated in both orders. Identical results either
    way is what makes a pool safe, because a pool is exactly an
    arbitrary order."""
    a, b = _tiny_task(11), _tiny_task(22)
    forward = [_sf._fp_triple(a), _sf._fp_triple(b)]
    reverse = list(reversed([_sf._fp_triple(b), _sf._fp_triple(a)]))
    for (fa, fb), (ra, rb) in zip(
            [(f["gamma_coll_err"], f["gamma_coll_err_trials"])
             for f in forward[0]],
            [(r["gamma_coll_err"], r["gamma_coll_err_trials"])
             for r in reverse[0]]):
        assert fa == pytest.approx(ra, abs=0.0), (
            "a task's forecast changed with the order it ran in, so the "
            "pooled path cannot be byte-identical to the sequential one")
        assert list(fb) == pytest.approx(list(rb), abs=0.0)


def test_the_same_task_twice_gives_the_same_answer():
    """The weaker property the one above depends on, separated so a
    failure says which broke: a task is a pure function of its seed."""
    t = _tiny_task(7)
    first, second = _sf._fp_triple(t), _sf._fp_triple(t)
    for f, s in zip(first, second):
        assert f["gamma_coll_err"] == pytest.approx(s["gamma_coll_err"],
                                                    abs=0.0)


def test_a_different_seed_gives_a_different_answer():
    """Otherwise the two tests above would pass on a producer that
    ignored its seed entirely, which is the vacuous shape this record
    keeps finding."""
    one = _sf._fp_triple(_tiny_task(11))[0]["gamma_coll_err"]
    two = _sf._fp_triple(_tiny_task(99))[0]["gamma_coll_err"]
    assert one != two, (
        "two seeds gave one answer: the seed is not reaching the "
        "generator, and every task in the grid is drawing the same "
        "numbers")


def _pid_probe(_):
    """Run inside a worker so a test can prove the pool has more than
    one. Module level because a spawn child must import it by name."""
    return os.getpid()


def test_the_assembly_pairs_each_task_with_its_own_result():
    """The defect injected on 2026-09-02 that no committed test caught.

    It rotated the result list by one position before the pairing. The
    producer wrote a clean forty-row CSV, correct row count, no error -
    and every value sat on the wrong preset and waist, one case putting
    a `campaign_cell/w0_8um` number on the `dataset_2025/w0_68um` row.
    Every test in this file passed, because they all call `_fp_triple`
    directly and none of them reached the pairing.

    This one reaches it. The pairing is positional and rests entirely on
    `pool.map` preserving order, which is a property to pin rather than
    to trust."""
    tasks = [(("a", 1.0), None, None, 11), (("b", 2.0), None, None, 22),
             (("c", 3.0), None, None, 33)]
    res = ["ra", "rb", "rc"]
    got = _sf._assemble_forecasts(tasks, res)
    assert got == {("a", 1.0): "ra", ("b", 2.0): "rb", ("c", 3.0): "rc"}
    # the injection itself: rotate by one and the pairing must change,
    # or this test is pinning nothing
    rotated = _sf._assemble_forecasts(tasks, res[1:] + res[:1])
    assert rotated != got, (
        "rotating the results left the pairing unchanged, so this test "
        "cannot see the defect it exists for")


def test_the_assembly_refuses_a_length_mismatch():
    """A pool that drops or duplicates a task would otherwise pair
    silently up to the shorter list and mislabel nothing visibly -
    `zip` stops at the shorter one, which is the quiet half of the same
    failure."""
    tasks = [(("a", 1.0), None, None, 11), (("b", 2.0), None, None, 22)]
    with pytest.raises(RuntimeError, match="tasks against"):
        _sf._assemble_forecasts(tasks, ["only-one"])


@pytest.mark.slow
def test_the_pooled_and_sequential_maps_agree(monkeypatch):
    """The equality the file claimed and never ran. Four tiny tasks
    through the producer's own spawn pool, against the same tasks run
    in this process."""
    import multiprocessing as mp
    jobs = [_tiny_task(s) for s in (11, 22, 33, 44)]
    monkeypatch.delenv("RB5S6S_WORKERS", raising=False)
    sequential = [_sf._fp_triple(j) for j in jobs]
    monkeypatch.setenv("RB5S6S_WORKERS", "2")
    with mp.get_context("spawn").Pool(
            2, initializer=_sf._init_fp_worker) as pool:
        pooled = pool.map(_sf._fp_triple, jobs)
    assert len(pooled) == len(sequential)
    for a, b in zip(sequential, pooled):
        for fa, fb in zip(a, b):
            assert fa["gamma_coll_err"] == pytest.approx(
                fb["gamma_coll_err"], abs=0.0), (
                "a task's forecast changed between the sequential and "
                "pooled paths, which is the one thing the workers "
                "contract forbids")


@pytest.mark.slow
def test_the_pooled_arm_really_starts_workers(monkeypatch):
    """And the pool must be a pool. Forcing the worker count to zero
    left the sibling producer's whole determinism file green, because
    the equality then compared the sequential path against itself."""
    import multiprocessing as mp
    monkeypatch.setenv("RB5S6S_WORKERS", "3")
    assert _sf.n_workers() > 1, (
        "the workers seam did not read the environment, so the pooled "
        "path this file grades is never taken")
    with mp.get_context("spawn").Pool(
            _sf.n_workers(), initializer=_sf._init_fp_worker) as pool:
        pids = set(pool.map(_pid_probe, range(12)))
    assert len(pids) > 1, "the pool ran everything in one process"
    assert os.getpid() not in pids, "a job ran in the parent: not a spawn pool"
