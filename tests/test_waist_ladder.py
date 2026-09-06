"""Guards for `scripts/run_waist_ladder.py`.

The file exists to stop an exponent being an assertion, so the guard checks
exactly that: each fitted exponent equals the one the derivation predicts, the
collected-signal column follows the closed form rather than the naive inverse
square, and the peak-height optimum is interior. A drift in any package
geometry function fails here rather than in a sentence nobody re-derives.
"""
from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_waist_ladder.py"


def _load():
    spec = importlib.util.spec_from_file_location("_wl", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rows(kind):
    with (ROOT / "results" / "waist_ladder.csv").open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["row_kind"] == kind]


def test_every_fitted_exponent_matches_the_derivation():
    rows = _rows("exponent")
    assert rows, "no exponent rows"
    for r in rows:
        assert float(r["fitted_exponent"]) == pytest.approx(
            float(r["predicted_exponent"]), abs=1e-6), r["term"]


def test_the_collected_signal_follows_the_closed_form_and_not_the_inverse_square():
    rungs = _rows("rung")
    ref = rungs[0]
    for r in rungs:
        want = math.atan(float(r["z_ratio"])) / math.atan(float(ref["z_ratio"]))
        # AT THE PUBLISHED PRECISION, never tighter: the cell carries six
        # decimals and comparing a recomputed double against it at 1e-9 fails
        # on the rounding the file itself performed.
        assert float(r["signal_rel"]) == pytest.approx(want, abs=5e-6)
    tight = min(rungs, key=lambda r: float(r["magnification"]))
    naive = float(tight["magnification"]) ** -2
    assert float(tight["signal_rel"]) < 0.5 * naive


def test_the_peak_height_optimum_is_interior():
    mod = _load()
    m_opt, w_opt, z_opt = mod.peak_height_optimum()
    assert min(mod.MAGNIFICATIONS) < m_opt < max(mod.MAGNIFICATIONS)
    row = _rows("peak_optimum")
    assert row and float(row[0]["magnification"]) == pytest.approx(m_opt, abs=1e-4)


def test_the_second_moment_ratio_reads_a_key_the_function_actually_returns():
    """The column read `kappa2` from a mapping
    whose keys are `pull`, `excess_var` and `kappa3`, so it fell to its NaN
    default on every rung of every run while the file's own note described it
    as computed. A `get` with a NaN default on a fixed small key set is a typo
    that cannot fail.

    Planted at the source and at the output: the key set is asserted, and
    every rung's ratio is asserted finite."""
    from rb5s6s.lineshape import ramp_moment_contributions
    keys = set(ramp_moment_contributions(1.0, z_ratio=0.26))
    assert "excess_var" in keys and "kappa2" not in keys, keys
    src = (ROOT / "scripts" / "run_waist_ladder.py").read_text(encoding="utf-8")
    assert '"kappa2"' not in src, "the retired key must not return"
    rows = _rows("rung")
    assert rows, "no rungs"
    for r in rows:
        assert math.isfinite(float(r["k2_over_pure"])), r
        assert math.isfinite(float(r["k3_over_pure"])), r


def test_the_relative_rate_and_cycle_columns_come_from_the_package():
    """Two of six guarded exponents were literal powers of the magnification,
    so the exponent guard recovered their own definition and could not fail
    on a drift in the package. They are now composed from the Rabi frequency
    squared and the transit time, and the guard can fail.

    The plant is that the two are no longer expressible as a bare power in
    the source, AND that they still recover the derived exponents, which is
    the cross-check the literal form could never provide."""
    src = (ROOT / "scripts" / "run_waist_ladder.py").read_text(encoding="utf-8")
    assert "cycles_rel=m ** -3" not in src and "rate_rel=m ** -4" not in src
    assert "RABI_ANCHOR_HZ" in src and "TRANSIT_ANCHOR_MHZ" in src
    exps = {r["term"]: float(r["fitted_exponent"]) for r in _rows("exponent")}
    assert exps["rate_rel"] == pytest.approx(-4.0, abs=1e-6)
    assert exps["cycles_rel"] == pytest.approx(-3.0, abs=1e-6)
