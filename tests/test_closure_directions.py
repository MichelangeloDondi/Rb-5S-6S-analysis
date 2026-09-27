"""The closure's direction options (owner order O69): the Monte Carlo world reaches the workers for every orientation
and every direction model, and a mirrored injected trace is its line read on the mirrored axis.

The first test is board 1c1e452c6b30's mechanism for F592: a block inserted between the world's `if` and its body
closed that `if` early, so the world was set for two-sign runs alone and the one-sign arms injected the separable line,
while ruff and the anchored applier both passed the edit. It runs `main`'s argument handling for every combination of
the flags and stops at the producer lock, before anything computes."""
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from conftest import load_script_module        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
_uc = load_script_module("run_ultra_joint_closure", ROOT / "scripts" / "run_ultra_joint_closure.py")

_KEYS = ("RB5S6S_CLOSURE_WORLD", "RB5S6S_CLOSURE_DIRECTIONS", "RB5S6S_CLOSURE_ORIENTATION",
         "RB5S6S_CLOSURE_POSTERIOR_LOG", "RB5S6S_CLOSURE_FITTER", "RB5S6S_CLOSURE_GRID_UM", "RB5S6S_CLOSURE_BELOW_FLOOR")


class _Stop(Exception):
    pass


def _args_only(monkeypatch, argv):
    """Run `main` until it takes the producer lock and return the environment and the ladder id it set."""
    import _producer_lock
    saved_env = {k: os.environ.get(k) for k in _KEYS}
    saved_id, saved_spec = _uc.ANALYSIS_ID, _uc._W.get("world_spec")

    def stop(*_a, **_k):
        raise _Stop

    monkeypatch.setattr(_producer_lock, "producer_lock", stop)
    monkeypatch.setattr(sys, "argv", ["run_ultra_joint_closure.py", *argv])
    try:
        for k in _KEYS:
            os.environ.pop(k, None)
        with pytest.raises(_Stop):
            _uc.main()
        return {k: os.environ.get(k) for k in _KEYS}, _uc.ANALYSIS_ID
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        _uc.ANALYSIS_ID = saved_id
        _uc._W["world_spec"] = saved_spec


@pytest.mark.parametrize("world", ["model", "volume"])
@pytest.mark.parametrize("orientation", ["rising", "two_sign"])
@pytest.mark.parametrize("directions", ["rising", "random"])
def test_the_world_reaches_the_workers_whatever_the_direction_flags(monkeypatch, world, orientation, directions):
    env, ladder = _args_only(monkeypatch, ["--world", world, "--orientation", orientation, "--directions", directions])
    assert (env["RB5S6S_CLOSURE_WORLD"] is not None) == (world != "model"), env
    assert (env["RB5S6S_CLOSURE_DIRECTIONS"] == "random") == (directions == "random")
    assert (env["RB5S6S_CLOSURE_ORIENTATION"] == "two_sign") == (orientation == "two_sign")
    assert ("@volume" in ladder) == (world == "volume")
    assert ("@dirs-random" in ladder) == (directions == "random")
    assert ("@two-sign" in ladder) == (orientation == "two_sign")


def test_a_falling_trace_is_its_line_read_on_the_mirrored_axis():
    x = np.linspace(-40.0, 40.0, 801)
    v = np.exp(-0.5 * ((x - 3.0) / 2.0) ** 2) + 0.01 * x
    traces = [dict(x=x, v=v.copy(), ones=np.ones_like(x), n=x.size) for _ in range(16)]
    out = _uc._random_directions(traces, seed=69)
    signs = [t["true_sign"] for t in out]
    assert 0 < signs.count(-1.0) < len(signs)
    for t in out:
        want = np.interp(-x, x, v) if t["true_sign"] < 0 else v
        assert np.allclose(t["v"], want, rtol=0.0, atol=1e-12)
    # seeded per realisation: the same seed draws the same directions
    assert [t["true_sign"] for t in _uc._random_directions(traces, seed=69)] == signs
