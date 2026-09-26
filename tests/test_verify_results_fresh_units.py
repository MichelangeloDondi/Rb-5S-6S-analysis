"""Units of scripts/verify_results_fresh.py that run in milliseconds, apart from its slow freshness battery."""
from __future__ import annotations

from rb5s6s import config as C


def test_the_verifier_runs_each_producer_on_one_worker_while_producers_run_side_by_side():
    """V7.1: a producer with its own process pool opened a full pool inside every slot of the verifier's pool, the
    process storm of F93, found when a swept producer took eight workers in a three-slot sweep. While the verifier runs
    producers side by side each gets RB5S6S_WORKERS=1, and a serial verifier leaves the caller's setting alone."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("verify_results_fresh", C.REPO_ROOT / "scripts" / "verify_results_fresh.py")
    vrf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vrf)
    assert vrf._inner_workers(2) == "1" and vrf._inner_workers(10) == "1"
    assert vrf._inner_workers(1) is None and vrf._inner_workers(0) is None
