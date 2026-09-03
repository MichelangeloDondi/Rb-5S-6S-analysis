"""The worker seam's own guards.

The seam exists to state one contract in one place, so these tests pin
the three behaviours a producer relies on: zero is the default and the
path of record, a bad value falls back to zero rather than guessing,
and a request above the ceiling is clamped loudly. Failure mode
guarded: a seam that silently honoured an over-request would starve a
gate running beside it, which is the condition unattended operation
runs in.
"""
from __future__ import annotations

import pytest

from rb5s6s.workers import ENV_VAR, MAX_WORKERS, n_workers


def test_absent_or_zero_is_sequential():
    assert n_workers({}) == 0
    assert n_workers({ENV_VAR: "0"}) == 0
    assert n_workers({ENV_VAR: "-4"}) == 0


def test_a_bad_value_falls_back_to_the_path_of_record():
    assert n_workers({ENV_VAR: "eight"}) == 0
    assert n_workers({ENV_VAR: ""}) == 0


def test_a_request_is_honoured_up_to_the_ceiling():
    assert n_workers({ENV_VAR: "1"}) == 1
    assert n_workers({ENV_VAR: str(MAX_WORKERS)}) == MAX_WORKERS


def test_an_over_request_is_clamped_and_says_so(capsys):
    assert n_workers({ENV_VAR: str(MAX_WORKERS + 5)}) == MAX_WORKERS
    assert "MAX_WORKERS" in capsys.readouterr().err


def test_the_producer_reads_the_seam_and_not_its_own_copy():
    """U1's available plant, and the commit says why it is this one.

    The seam's stated plant was `scripts/_m25_parallel_smoke.py`, which
    asserts exact equality of the sequential and pooled paths of
    run_global_dataset_fit. That smoke fits the real three-session
    residual and refuses on a machine without the excluded session
    trees, which this one is. So the property actually checkable here
    is the one the refactor could break: that the producer's wrapper
    delegates to this module rather than keeping a second read of the
    environment, which is what the wave existed to end.
    """
    import importlib.util
    import os
    from pathlib import Path
    prod = (Path(__file__).resolve().parents[1] / "scripts"
            / "run_global_dataset_fit.py")
    src = prod.read_text(encoding="utf-8")
    assert "from rb5s6s.workers import n_workers" in src, (
        "the producer no longer reads the seam; the environment is "
        "being read in two places again")
    assert src.count('environ.get("RB5S6S_WORKERS"') == 0, (
        "the producer kept its own environment read beside the seam, "
        "which is the duplication this unit removed")
    # and the delegation actually returns the seam's answer
    spec = importlib.util.spec_from_file_location("_gdf_probe", prod)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except ModuleNotFoundError as exc:
        # NARROWED, and it re-raises for the module this test is about.
        # A bare `except Exception: return` here reported "7 passed" while
        # the producer could not be imported at all, which is the house
        # rule "a check whose precondition is absent must never report
        # success" broken inside a check. A missing HEAVY dependency is a
        # real skip; a missing scripts/-local module means the producer's
        # own imports are broken and that is the subject.
        if exc.name in (None, "_producer_lock"):
            raise
        pytest.skip(f"the producer needs {exc.name}, absent here")
    old = os.environ.get(ENV_VAR)
    try:
        os.environ[ENV_VAR] = "3"
        assert mod.n_workers() == 3
        os.environ[ENV_VAR] = str(MAX_WORKERS + 4)
        assert mod.n_workers() == MAX_WORKERS
    finally:
        if old is None:
            os.environ.pop(ENV_VAR, None)
        else:
            os.environ[ENV_VAR] = old
def test_the_real_environment_path_is_the_one_callers_use(monkeypatch):
    """The four tests above inject a dict, which buys them hermeticity
    and costs coverage of `env=None` - the path every real caller
    takes. A seam that read a snapshot taken at import would pass all
    of them and serve a stale number to every producer."""
    monkeypatch.setenv(ENV_VAR, "2")
    assert n_workers() == 2
    monkeypatch.setenv(ENV_VAR, "0")
    assert n_workers() == 0
    monkeypatch.delenv(ENV_VAR, raising=False)
    assert n_workers() == 0


def test_the_ceiling_leaves_the_machine_room_to_work():
    """MAX_WORKERS is derived, so it is asserted against the machine
    rather than against a literal: the stated reason is that a gate and
    a session stay responsive beside a pooled run, which is false the
    moment the ceiling reaches the core count."""
    import os
    cores = os.cpu_count() or 4
    assert MAX_WORKERS == max(1, cores - 2), (
        f"the ceiling is {MAX_WORKERS} on {cores} cores, which is not the "
        "derivation rb5s6s/workers.py states. Equality is deliberate: an "
        "inequality would also pass a hardcoded low value, which looks "
        "safe and silently wastes the machine. If the holdback policy "
        "changes on purpose, UPDATE THIS TEST - a deliberate change "
        "should read as an update, not as a break")
