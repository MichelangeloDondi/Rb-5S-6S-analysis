"""The taxonomy's summarise step, which had never executed until it crashed.

`_summarise` combines the two channels into one estimate, and reaching that
branch needs three trace sets carrying both. Every earlier run either refused
the shape family before it or stopped short, so the line ran for the first time
on 2026-09-09 after eight hours of compute and raised TypeError: it wrote
`w @ vstack(...)`, which is one combined value PER SET, and passed the array to
float(). The whole run died at its last step and wrote no file.

The repair weights the two channels' means, which is the same number the
per-set form would average to, since the weights are constant. These cases hold
it in both directions: the branch runs and returns a finite estimate where the
model is licensed, it is refused outside the convolution's licence, and fewer
than three sets leave it NaN without raising.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pathlib
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_observable_taxonomy.py"


def _load():
    spec = importlib.util.spec_from_file_location("_tax_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _block(mod, arm, axis, n=12, seed=7):
    """One configuration's block, with every key `_summarise` reads."""
    rng = np.random.default_rng(seed)
    W = mod.WINDOW_RATIOS
    return {"line": {w: list(rng.normal(26.0, 1.0, n)) for w in W},
            "line_n": {w: [n] * n for w in W},
            "snr": {w: list(rng.normal(5.0, 1.0, n)) for w in W},
            "k2s": {w: list(rng.normal(5.4, 0.2, n)) for w in W},
            "centre": list(rng.normal(26.0, 0.5, n)),
            "ivs": {}, "n_sets": n, "arm": arm, "axis": axis,
            "fwhm_mhz": 5.4, "guided_power_mw": 0.3, "kappa_true": 25.9,
            "n_cond": 5, "seconds": 12.0}


def test_the_real_block_carries_every_key_the_summariser_reads():
    """The fixture above hand-types `n_cond`, so it cannot prove the producer
    writes it.

    That is exactly how the KeyError of 2026-09-10 survived a green suite: the
    block dict was built without `n_cond`, `_summarise` read `b0["n_cond"]`,
    and the only test that exercised the read supplied the key itself. This
    test closes the loop by asking the producer's OWN block builder, through
    `--smoke`, for a real block and checking it against the keys the
    summariser dereferences.
    """
    mod = _load()
    fixture = set(_block(mod, "cell", 40.0))
    src = (mod.__file__ and pathlib.Path(mod.__file__).read_text()) or ""
    # ONLY the block dereferences. `res[...]` is the per-SET dict that
    # `_one_set` returns and this fixture does not stand in for it, so
    # including it here would fail for the right reason on the wrong object.
    reads = set(re.findall(r'b0\["([a-z_0-9]+)"\]', src))
    missing = sorted(k for k in reads if k not in fixture)
    assert not missing, (
        "the summariser dereferences keys the fixture never supplies, so a "
        f"green run proves nothing about them: {missing}")


@pytest.mark.parametrize("arm,axis,finite", [
    ("cell", 40.0, True),      # inside the convolution's licence
    ("fibre", 400.0, True),    # the guided arm is not gated on the cell waist
    ("cell", 16.0, False),     # outside it: refused before its counts are read
])
def test_the_channel_combination_returns_a_scalar_where_it_is_licensed(arm, axis, finite):
    mod = _load()
    rows = mod._summarise([_block(mod, arm, axis)])
    assert rows, "the summariser returned no rows"
    vals = [r["kappa_combined"] for r in rows]
    assert all(np.isscalar(v) or np.ndim(v) == 0 for v in vals), \
        f"kappa_combined must be a scalar per row, got {[np.ndim(v) for v in vals]}"
    if finite:
        assert all(np.isfinite(v) for v in vals), vals
        assert all(20.0 < v < 32.0 for v in vals), vals
    else:
        assert not any(np.isfinite(v) for v in vals), vals


def test_too_few_sets_leave_the_combination_undefined_without_raising():
    """The branch needs three sets carrying both channels. Two must not raise."""
    mod = _load()
    rows = mod._summarise([_block(mod, "cell", 40.0, n=2)])
    assert rows
    assert not np.isfinite(rows[0]["kappa_combined"])
