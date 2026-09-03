"""The paired forecast's pooled grid: the property its byte-identity
rests on, pinned so an edit cannot quietly break it.

WHY THIS PRODUCER NEEDS ITS OWN GUARD. It is the wave's only unit that
added NEW parallelism, and the board that read the seam set the
condition plainly: such a unit is severe without an equality plant
that runs on a checkout WITHOUT the private session trees. This
producer reads no session tree, so its plant runs anywhere - which is
exactly why it can carry the condition the joint fit's could not.

WHAT IS PINNED, AND WHY NOT THE WHOLE PRODUCER. The grid is 32
configurations of 384 sweeps; running it twice per suite would cost
minutes for a property decidable in seconds. What makes the pool safe
is that a configuration is a pure function of its own identity: the
seed comes from `_task_seed("cfg", branch, jitter, drift)`, so the
order configurations run in cannot reach the numbers, and a pool is
exactly an arbitrary order. That is what these tests hold.

The full equality remains reproducible by hand and the command belongs
where a reader will find it:

    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_paired_reference_forecast.py
    git diff --stat results/paired_reference_forecast.csv   # must be empty

Measured 2026-09-02 over the whole producer, AFTER the grid gained six
replicates per configuration, on a ten-core machine and varying with
what else is running: 668 to 789 s sequential, about 240 s at three
workers, 153 to 170 s at six and 142 s at eight, byte-identical at all
four. The figures
before the replication were about five times smaller and are not
comparable to these.

Failure mode guarded: a change to the sweep or fit machinery that makes
a configuration depend on what ran before it, which the freshness check
cannot see because it only ever runs the sequential path.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_PROD = ROOT / "scripts" / "run_paired_reference_forecast.py"

# scripts/ joins sys.path BEFORE the module is loaded under its real
# name, and both halves are load-bearing for the pooled arm below: a
# spawn child imports the function's defining module BY NAME and
# inherits the parent's sys.path, so a module loaded under a synthetic
# name - or a real name the child cannot find - leaves the child unable
# to import it and the pool hangs rather than failing. Measured
# 2026-09-02 by hanging exactly that way.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location(
    "run_paired_reference_forecast", _PROD)
# ONE MODULE OBJECT, WHATEVER ORDER PYTEST COLLECTS IN. See
# tests/conftest.py:load_script_module - the explanation lives there,
# once, rather than in each caller.
from conftest import load_script_module        # noqa: E402

_pf = load_script_module("run_paired_reference_forecast", _PROD)

# a deliberately small sweep count: the property is order-independence,
# not precision, and four sweeps show it as well as three hundred
_N = 4


def _run(branch, jitter, drift):
    """The job's key and arrays. The pid is the third element and is
    deliberately dropped here: it differs between processes by design,
    so an equality test must not see it."""
    return _pf._cfg_job((jitter, drift, branch, _N, 0))[:2]


def test_a_configuration_does_not_depend_on_what_ran_before_it():
    """Two configurations in both orders. A pool imposes an arbitrary
    order, so identical results either way is the whole licence for
    pooling this grid."""
    a = ("analog", 0.028, 5.0)
    b = ("counting", 0.05, 20.0)
    fwd = [_run(*a), _run(*b)]
    rev = list(reversed([_run(*b), _run(*a)]))
    for (ka, va), (kb, vb) in zip(fwd, rev):
        assert ka == kb
        for arr_a, arr_b in zip(va, vb):
            assert np.array_equal(np.asarray(arr_a), np.asarray(arr_b)), (
                f"{ka} changed with the order it ran in, so the pooled "
                "grid cannot be byte-identical to the sequential one")


def test_the_same_configuration_twice_gives_the_same_arrays():
    """The weaker property the one above rests on, separated so a
    failure says which broke."""
    first, second = _run("analog", 0.028, 5.0), _run("analog", 0.028, 5.0)
    assert first[0] == second[0]
    for x, y in zip(first[1], second[1]):
        assert np.array_equal(np.asarray(x), np.asarray(y))


def test_the_task_seed_separates_the_identities():
    """The seed must actually differ per configuration. Comparing two
    configurations' ARRAYS cannot show this - they differ in jitter or
    drift, which change the physics whatever the seed does, so that
    comparison passes even on a producer seeded with a constant. It
    did: planting `default_rng(0)` left an earlier version of this file
    entirely green."""
    ids = [("cfg", str(r), b, j, d)
           for j in _pf.JITTER_SPAN_MHZ
           for d in _pf.DRIFT_SPAN_KHZ_MIN
           for b in ("analog", "counting")
           for r in range(_pf.N_GRID_REPLICATES)]
    seeds = [_pf._task_seed(*i) for i in ids]
    assert len(set(seeds)) == len(seeds), (
        "two configurations share a seed, so the grid is drawing the "
        "same numbers twice somewhere")


def test_the_seed_survives_a_fresh_interpreter():
    """The property no in-process test can see, and the one a spawn
    pool actually rests on.

    `_task_seed` derives from `zlib.crc32`, which is a fixed function of
    the bytes. Python's own str hashing is SALTED per interpreter,
    so a producer built on it would give every configuration a different
    seed in every spawn child - and would pass every fast test in this
    file, because within one process a salted hash is perfectly stable.
    Only the slow pooled-versus-sequential test could catch such a swap,
    and only by running the whole grid.

    So: two subprocesses, each with its own salt, must agree. Two
    interpreter starts, well under a second."""
    import subprocess
    code = ("import sys; sys.path.insert(0, %r);"
            "import run_paired_reference_forecast as m;"
            "print(m._task_seed('cfg', 'analog', 0.028, 5.0),"
            " m._task_seed('sens', '3'))" % str(ROOT / "scripts"))
    outs = []
    for salt in ("1", "12345"):
        env = dict(os.environ, PYTHONHASHSEED=salt)
        r = subprocess.run([sys.executable, "-c", code], env=env,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        outs.append(r.stdout.strip())
    assert outs[0] == outs[1], (
        "the task seed changed with the interpreter's hash salt, so "
        "every spawn worker derives different seeds from the same "
        "identity and the pooled output cannot be byte-identical to "
        f"the sequential one: {outs[0]!r} against {outs[1]!r}")


def test_the_seed_reaches_the_physics():
    """And the seed must change what is drawn. Same configuration, two
    generators: identical arrays would mean the seed is decorative and
    every task in the grid draws one stream."""
    j, d, b = 0.028, 5.0, "analog"
    a = _pf._config_arrays(j, d, b, _N, np.random.default_rng(1))
    c = _pf._config_arrays(j, d, b, _N, np.random.default_rng(2))
    assert not np.array_equal(np.asarray(a[0]), np.asarray(c[0])), (
        "two generators gave one answer: the rng is not reaching the "
        "sweeps, so per-task seeding buys nothing and the pool is not "
        "safe for the reason this producer claims")


def test_the_job_draws_from_the_seed_its_identity_gives():
    """The wiring, which the two tests above cannot see. They check
    that identities give distinct seeds and that a generator changes
    the sweeps - both true of a job that ignores its seed entirely and
    passes a constant to the generator. Planting exactly that
    (`default_rng(0)` inside the job) left this file green until this
    test existed, so what is asserted here is the join: the job's
    arrays are the ones its own task seed produces."""
    j, d, b = 0.028, 5.0, "analog"
    from_job = _pf._cfg_job((j, d, b, _N, 0))[1]
    expected = _pf._config_arrays(
        j, d, b, _N,
        np.random.default_rng(_pf._task_seed("cfg", "0", b, j, d)))
    for x, y in zip(from_job, expected):
        assert np.array_equal(np.asarray(x), np.asarray(y)), (
            "the job's arrays are not the ones its task seed gives, so "
            "the per-task seeding is decorative and the pool's safety "
            "rests on nothing")


def test_the_grid_builder_covers_the_whole_span_once():
    """The pool's job list is the grid: if it missed a configuration or
    repeated one, `_run_grid`'s dict would silently drop or overwrite a
    row and the CSV would be short without failing anything."""
    grid = _pf._run_grid(1)
    expected = {(b, j, d)
                for j in _pf.JITTER_SPAN_MHZ
                for d in _pf.DRIFT_SPAN_KHZ_MIN
                for b in ("analog", "counting")}
    assert set(grid) == expected
    assert len(grid) == len(expected) == (
        2 * len(_pf.JITTER_SPAN_MHZ) * len(_pf.DRIFT_SPAN_KHZ_MIN))


@pytest.mark.slow
def test_the_pooled_and_sequential_grids_agree(monkeypatch):
    """The equality itself, at a sweep count small enough to run in the
    suite. Marked slow because it starts real worker processes, and the
    board's condition for this wave is that it runs on a checkout
    without the private trees - which it does, because this producer
    reads none."""
    monkeypatch.delenv("RB5S6S_WORKERS", raising=False)
    sequential = _pf._run_grid(_N)
    monkeypatch.setenv("RB5S6S_WORKERS", "2")
    pooled = _pf._run_grid(_N)
    assert set(sequential) == set(pooled)
    for k in sequential:
        for x, y in zip(sequential[k], pooled[k]):
            assert np.array_equal(np.asarray(x), np.asarray(y)), (
                f"{k} differs between the sequential and pooled grids: "
                "the worker count reached the numbers, which is the one "
                "thing the contract forbids")


@pytest.mark.slow
def test_the_pooled_arm_really_starts_workers(monkeypatch):
    """The test above compares a pooled grid against a sequential one -
    but only if the pooled one is pooled. Forcing the worker count to
    zero inside `_run_grid` left every test in this file green, because
    the equality then compared the sequential path against itself: a
    plant that cannot see its own subject. The pid rides out of the job
    for exactly this assertion."""
    monkeypatch.setenv("RB5S6S_WORKERS", "3")
    jobs = [(j, d, b, _N, r)
            for j in _pf.JITTER_SPAN_MHZ
            for d in _pf.DRIFT_SPAN_KHZ_MIN
            for b in ("analog", "counting")
            for r in range(_pf.N_GRID_REPLICATES)]
    pids = {pid for _k, _v, pid in
            _pf._pooled_map(_pf._cfg_job, jobs, _pf.n_workers())}
    assert len(pids) > 1, (
        "the pooled map ran everything in one process, so the equality "
        "test above is comparing the sequential path against itself")
    assert os.getpid() not in pids, (
        "a job ran in the parent process: this is not a spawn pool")


def test_perturbing_nothing_moves_nothing():
    """The pairing plant, and the sharpest test in this file.

    Each sensitivity replicate draws ONE stream, and every perturbation
    in that replicate reuses it - common random numbers - so evaluating
    the same replicate twice with nothing perturbed must agree to the
    last bit. Seeding per tag instead broke that silently: thirteen
    genuinely insensitive rows scattered to +-1.9 sigma and four rows
    read "Distinguishable: yes" with nothing perturbed at all. Nothing
    in the suite saw it, because every other test here asks about the
    GRID, whose seeding was never touched.

    This is the test that fails on that mistake, and it costs
    milliseconds."""
    a = _pf._sens_job((0, None, 1.0))[1][:2]
    b = _pf._sens_job((0, None, 1.0))[1][:2]
    assert a == b, "a replicate is not reproducible from its own identity"
    # and a DIFFERENT replicate must differ, or the replicates are one
    # sample wearing six hats and the reported scatter is a fiction
    c = _pf._sens_job((1, None, 1.0))[1][:2]
    assert a != c, (
        "two replicates gave one answer, so the base seeds are not "
        "reaching the draws and the +- on every sensitivity row is "
        "measuring nothing")


def test_a_sensitivity_row_is_paired_against_its_own_replicate():
    """The join the test above cannot make: that a PERTURBED evaluation
    shares its replicate's stream. If it did not, the difference would
    carry two samples' worth of noise instead of the constant's effect,
    which is the defect this block was repaired for. Setting the
    perturbation factor to 1.0 makes the perturbation a no-op, so the
    perturbed job must reproduce the baseline exactly."""
    base = _pf._sens_job((2, None, 1.0))[1][:2]
    noop = _pf._sens_job((2, "GAMMA_FIBRE", 1.0))[1][:2]
    assert base == noop, (
        "multiplying a constant by one changed the answer, so the "
        "perturbed evaluation is not drawing its replicate's stream "
        "and every distance in the block carries sampling noise the "
        "pairing was supposed to remove")


def test_the_grid_replicates_are_actually_different_samples():
    """The plant the grid's replication shipped without.

    `N_GRID_REPLICATES` independent base seeds are CONCATENATED, and
    every standard error in the grid rows falls by root six on the
    strength of that. If the replicates all drew one stream the
    concatenation would be one sample repeated, every error would be
    understated by root six, and the CSV would look entirely well
    formed.

    Removing `str(rep)` from the job's seed failed exactly ONE test in
    this file, and only incidentally: that test exists to check job
    wiring at a hardcoded replicate, not to assert distinctness. The
    worker-count equality could never see it, because six collapsed
    replicates agree with themselves on both paths.

    The sensitivity block has had this pair since the day it gained
    replicates. The grid did not, and this is it."""
    a = _pf._cfg_job((0.028, 5.0, "analog", _N, 0))[1]
    again = _pf._cfg_job((0.028, 5.0, "analog", _N, 0))[1]
    for x, y in zip(a, again):
        assert np.array_equal(np.asarray(x), np.asarray(y)), (
            "one replicate is not reproducible from its own identity")
    b = _pf._cfg_job((0.028, 5.0, "analog", _N, 1))[1]
    assert not np.array_equal(np.asarray(a[0]), np.asarray(b[0])), (
        "two replicates of the same configuration drew the same "
        "sample, so the concatenation is one sample repeated and "
        "every grid error is understated by root "
        f"{_pf.N_GRID_REPLICATES}")


def test_the_grid_gathers_every_replicate_it_claims():
    """A dropped replicate shortens the concatenation silently.

    Monkeypatching the pooled map to drop one task returned a
    configuration with twenty samples where twenty-four were claimed,
    raising nothing: the CSV would be short and valid, and its errors
    inflated. `_run_grid` now proves its own gather, and this is the
    plant for that."""
    real = _pf._pooled_map

    def lossy(fn, tasks, nw):
        out = real(fn, tasks, nw)
        return [r for r in out if not (r[0][3] == 1 and r[0][0] == "analog")]

    _pf._pooled_map = lossy
    try:
        with pytest.raises(RuntimeError, match="replicates, not"):
            _pf._run_grid(_N)
    finally:
        _pf._pooled_map = real


def test_the_gather_reads_every_array_not_only_the_first():
    """A replicate is six arrays and the checks used to read one.

    `_run_grid`'s length and distinctness checks originally inspected
    `arrays[0]`, `s_unref`, because that is the array the rest of the
    function already had in scope. `shift_err_ratio` - the row this
    file exists to report, and the one the fibre scenario quotes to a
    reader deciding whether to expose a nanofibre - is built from
    `s_joint`, at position 1.

    So this duplicates one replicate's `s_joint` onto another, leaving
    `s_unref` distinct and correctly sized. Both original checks passed
    that and it reached the CSV, with the errors on the central ratio
    understated and the file well formed."""
    real = _pf._pooled_map

    def corrupt(fn, tasks, nw):
        out = list(real(fn, tasks, nw))
        by_key = {}
        for i, (k, arrays, pid) in enumerate(out):
            by_key.setdefault(k[:3], []).append(i)
        for _cfg, idxs in by_key.items():
            if len(idxs) >= 2:
                a0 = out[idxs[0]]
                a1 = out[idxs[1]]
                new = list(a1[1])
                new[1] = list(a0[1][1])        # s_joint duplicated
                out[idxs[1]] = (a1[0], tuple(new), a1[2])
        return out

    _pf._pooled_map = corrupt
    try:
        with pytest.raises(RuntimeError, match="identical draws in array 1"):
            _pf._run_grid(_N)
    finally:
        _pf._pooled_map = real
