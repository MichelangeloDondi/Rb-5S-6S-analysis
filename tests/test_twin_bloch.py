"""The twin's clean line from the full-model line (O59 W1): the same line, cached honestly, with the twin's own noise.

Each test runs the full-model line at a few dozen atoms on a short grid, where its Monte Carlo is noisy but
deterministic under its seed, so an equality here is exact and an interpolation error is read against a direct solve.
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.interpolate import CubicSpline

from rb5s6s import bloch_full, twin_bloch
from rb5s6s import constants as K
from rb5s6s.forecast import _traces_from_shape

STUDY = "the W1 tests of the twin's full-model line path, at a few dozen atoms"
COND = dict(peak="4192", P_W=0.225, T_C=130.0, w0_m=float(K.W0_CENTRAL_M), M2=1.0, n_path=48, seed=3)


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("RB5S6S_TWIN_LINE_CACHE", str(tmp_path / "lines"))
    return tmp_path / "lines"


@pytest.mark.slow
def test_the_twin_line_is_the_full_model_line(cache):
    grid = np.linspace(-6.0, 6.0, 25)
    line, info = twin_bloch.clean_line(grid, registry=STUDY, use_cache=False, **COND)
    ref, _ = bloch_full.full_line(grid, consumer="twin", registry=STUDY, **COND)
    ref = np.asarray(ref, float) / np.max(ref)
    assert np.array_equal(line, ref)
    assert info["cache"] == "miss" and info["code_digest"] == twin_bloch.code_digest()


@pytest.mark.slow
def test_the_cache_returns_the_same_line_and_misses_on_any_change(cache, monkeypatch):
    grid = np.linspace(-6.0, 6.0, 25)
    first, i1 = twin_bloch.clean_line(grid, registry=STUDY, **COND)
    again, i2 = twin_bloch.clean_line(grid, registry=STUDY, **COND)
    assert i1["cache"] == "miss" and i2["cache"] == "hit" and np.array_equal(first, again)
    moved, i3 = twin_bloch.clean_line(grid, registry=STUDY, **dict(COND, P_W=0.175))
    assert i3["cache"] == "miss" and not np.array_equal(first, moved)
    monkeypatch.setattr(twin_bloch, "code_digest", lambda: "a-different-code")
    _, i4 = twin_bloch.clean_line(grid, registry=STUDY, **COND)
    assert i4["cache"] == "miss", "a code change must be a cache miss, never a stale line"


def test_the_code_digest_is_derived_from_the_lines_imports():
    files = {p.name for p in twin_bloch._KG.import_closure(["bloch_full"], exclude=twin_bloch._NOT_THE_LINE)}
    assert "bloch_full.py" in files and "volume_line.py" in files and "beam_field.py" in files
    assert "model_registry.py" not in files and "kernel_gate.py" not in files


@pytest.mark.slow
def test_the_traces_carry_the_twins_own_noise_layer(cache):
    kw = dict(span_mhz=8.0, n_points=161, n_traces=3, noise=0.01, registry=STUDY, **COND)
    f1, v1 = twin_bloch.synthetic_traces(rng=np.random.default_rng(7), **kw)
    grid = np.linspace(-8.0, 8.0, int(round(16.0 / twin_bloch.LINE_STEP_MHZ)) + 1)
    line, _ = twin_bloch.clean_line(grid, registry=STUDY, **COND)
    nu = np.linspace(-8.0, 8.0, 161)
    shape = CubicSpline(grid, line)(nu)
    f2, v2 = _traces_from_shape(nu, shape / shape.max(), n_traces=3, noise=0.01, amp=1.0, amp_spread=0.05,
                                offset=0.010, offset_spread=0.002, halo_fraction=0.0, tau_int=None,
                                residual_source=None, rng=np.random.default_rng(7))
    for a, b in zip(v1, v2):
        assert np.array_equal(a, b)


@pytest.mark.slow
def test_the_line_grid_reads_the_trace_axis_as_a_direct_solve_would(cache):
    nu = np.linspace(-8.0, 8.0, 81)
    f, v = twin_bloch.synthetic_traces(span_mhz=8.0, n_points=81, n_traces=1, noise=0.0, amp=1.0, amp_spread=0.0,
                                       rng=np.random.default_rng(0),
                                       offset=0.0, offset_spread=0.0, registry=STUDY, **COND)
    direct, _ = bloch_full.full_line(nu, consumer="twin", registry=STUDY, **COND)
    direct = np.asarray(direct, float) / np.max(direct)
    assert np.max(np.abs(v[0] - direct)) < 2e-4, "the line grid's reader must sit below the twin's lowest noise rung"
