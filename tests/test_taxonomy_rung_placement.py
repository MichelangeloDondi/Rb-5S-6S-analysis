"""`_by_rung` places a trace by its own recorded power, and refuses a clash.

WHY THIS EXISTS (escape E45, 2026-09-10). `run_observable_taxonomy.py` draws
the rung order per condition -- that draw IS the campaign's design rule, and it
is what separates the drift from the pull -- then appended each trace's
cumulants in ACQUISITION order. `_lineshape_kappa` reshaped that flat list to
`(n_cond, n_pow)`, so column j was the j-th acquisition SLOT and held a
different rung in every condition, while the quiet curve divided into it was
indexed by RUNG. The estimator returned the true coefficient times 13.995,
2.339, 1.233, 0.865 and 0.738 by rung.

A reshape cannot fail, which is why nothing caught it: the run is
deterministic, reproducible and wrong, so every determinism plant passes. The
repair makes the placement a LOOKUP that can refuse, and this module is the
negative case that lookup needs. The retired reshape ACCEPTS the duplicated
rung these tests refuse, which is what makes them a discriminating plant
rather than an assertion.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
POWERS = np.array([0.025, 0.075, 0.125, 0.175, 0.225])
NCOND, NPOW = 3, 5


@pytest.fixture(scope="module")
def taxo():
    """Import the producer as a module; it must not run anything on import."""
    spec = importlib.util.spec_from_file_location(
        "taxo_for_test", ROOT / "scripts" / "run_observable_taxonomy.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["taxo_for_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _res(order_per_cond):
    """A res dict whose traces ARRIVE in the given per-condition rung order.

    `k3` encodes `100*condition + rung`, so a correct placement is checkable
    cell by cell rather than by a summary statistic.
    """
    powers, block, k3 = [], [], []
    for ci, order in enumerate(order_per_cond):
        for ri in order:
            powers.append(POWERS[ri])
            block.append(ci)
            k3.append(100 * ci + ri)
    return ({"powers": np.array(powers), "block": np.array(block)},
            np.array(k3, float))


WANT = np.array([[100 * c + r for r in range(NPOW)] for c in range(NCOND)],
                float)


def test_a_shuffled_draw_still_lands_each_trace_on_its_own_rung(taxo):
    rng = np.random.default_rng(7)
    orders = [list(rng.permutation(NPOW)) for _ in range(NCOND)]
    res, flat = _res(orders)
    out = taxo._by_rung(res, flat, POWERS, NCOND, NPOW)
    assert np.array_equal(out, WANT), f"misplaced:\n{out}\nwant\n{WANT}"


def test_the_monotone_draw_is_the_case_the_retired_reshape_got_right(taxo):
    res, flat = _res([list(range(NPOW))] * NCOND)
    assert np.array_equal(taxo._by_rung(res, flat, POWERS, NCOND, NPOW), WANT)


def test_the_retired_reshape_disagrees_on_a_shuffled_draw():
    """The defect, shown rather than described.

    If this ever passes, the fixture below is not exercising E45 and the
    negative case beneath it proves nothing.
    """
    rng = np.random.default_rng(7)
    orders = [list(rng.permutation(NPOW)) for _ in range(NCOND)]
    _, flat = _res(orders)
    assert not np.array_equal(flat.reshape(NCOND, NPOW), WANT), (
        "the retired reshape agreed with the lookup on a shuffled draw, so "
        "this module is no longer testing the defect it exists for")


def test_two_traces_at_one_rung_are_refused_not_averaged(taxo):
    res, flat = _res([[0, 0, 2, 3, 4]] + [list(range(NPOW))] * (NCOND - 1))
    with pytest.raises(SystemExit, match="second trace"):
        taxo._by_rung(res, flat, POWERS, NCOND, NPOW)


def test_an_off_ladder_power_does_not_land_silently(taxo):
    """Tolerance case: a power between two rungs must refuse or leave a NaN.

    Placing it on a neighbouring rung would reintroduce E45 quietly, since a
    near-miss is exactly what a searchsorted would absorb.
    """
    res, flat = _res([list(range(NPOW))] * NCOND)
    res["powers"] = res["powers"].copy()
    res["powers"][0] = 0.05
    try:
        out = taxo._by_rung(res, flat, POWERS, NCOND, NPOW)
    except SystemExit:
        return
    assert np.isnan(out).any(), (
        "an off-ladder power was placed on a neighbouring rung with no NaN "
        "and no refusal")
