"""The Sobol producer's estimators, closed on an analytic case.

The producer exists because docs/plan/07 carried a hand-typed index
table with no route to re-derive it. These tests hold the estimators to
a model whose indices are known exactly, pin the committed CSV's
internal consistency, and keep the producer's numbers deterministic.

Plant, verified at introduction: swapping the AB_i column for A's in
the ST estimator drives Jansen's total order to zero on the additive
case and test_estimators_close_on_an_additive_model fails; restoring
the pairing passes it.
"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "rsa", ROOT / "scripts" / "run_sobol_acquisition.py")
rsa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rsa)


def _saltelli_on(f, k, n=4096, seed=7):
    g = np.random.default_rng(seed)
    a, b = g.random((n, k)), g.random((n, k))
    fa, fb = f(a), f(b)
    var = np.var(np.concatenate([fa, fb]))
    s1, st = [], []
    for i in range(k):
        ab = a.copy()
        ab[:, i] = b[:, i]
        fab = f(ab)
        s1.append(np.mean(fb * (fab - fa)) / var)
        st.append(np.mean((fa - fab) ** 2) / (2.0 * var))
    return np.array(s1), np.array(st)


def test_estimators_close_on_an_additive_model():
    """Y = 3*X1 + 1*X2: S1 = ST = (9, 1)/10 exactly, no interaction."""
    s1, st = _saltelli_on(lambda x: 3.0 * x[:, 0] + 1.0 * x[:, 1], 2)
    assert s1 == pytest.approx([0.9, 0.1], abs=0.04)
    assert st == pytest.approx([0.9, 0.1], abs=0.04)


def test_estimators_see_a_pure_interaction():
    """Y = (X1-1/2)(X2-1/2): S1 = 0 for both and ST = 1 for EACH,
    because the variance is pure interaction and each input takes part
    in all of it (Jansen: E[(f_A-f_ABi)^2] = 2V here) -- the case a
    one-at-a-time sweep misses, which is the method's whole point. A
    first version of this test expected 1/2 each; the analytic value
    is 1, and the estimator was right."""
    s1, st = _saltelli_on(
        lambda x: (x[:, 0] - 0.5) * (x[:, 1] - 0.5), 2)
    assert s1 == pytest.approx([0.0, 0.0], abs=0.04)
    assert st == pytest.approx([1.0, 1.0], abs=0.08)


def test_the_run_is_deterministic():
    """Same seed, same indices: the committed CSV is reproducible."""
    _, s1a, sta, _, _ = rsa.sobol_rows()
    _, s1b, stb, _, _ = rsa.sobol_rows()
    assert np.array_equal(s1a, s1b) and np.array_equal(sta, stb)


def test_closed_form_moments_match_hand_values():
    """The log-uniform second-moment ratio for eta's (0.5, 2) band at
    c = -1 is 1.35255/1.08202^2 = 1.15525 by hand; the uniform one for
    repeats' (3, 20) at c = -1/2 likewise. A wrong moment formula moves
    every index, so the two hand anchors pin the helpers directly."""
    m1 = rsa._mom_loguniform(0.5, 2.0, -1.0)
    m2 = rsa._mom_loguniform(0.5, 2.0, -2.0)
    assert m2 / m1 ** 2 == pytest.approx(1.15525, abs=2e-5)
    u1 = rsa._mom_uniform(3.0, 20.0, -0.5)
    u2 = rsa._mom_uniform(3.0, 20.0, -1.0)
    assert u1 == pytest.approx((20.0 ** 0.5 - 3.0 ** 0.5) / 8.5, abs=1e-12)
    assert u2 == pytest.approx(np.log(20.0 / 3.0) / 17.0, abs=1e-12)


def test_closed_form_agrees_with_the_estimators_on_the_real_model():
    """Exact against Saltelli/Jansen on the committed noise facts: every
    index within four bootstrap sigma. The estimators are unbiased, so
    a miss here means the sampler or the model wiring broke -- this is
    the producer's mc_max_z row as a test."""
    p_floor, _, pw_lo, pw_hi, tau_lo, tau_hi = rsa.committed_noise_facts()
    s1, st = rsa.exact_indices(p_floor, pw_lo, pw_hi, tau_lo, tau_hi)
    _, s1_mc, st_mc, e1_mc, et_mc = rsa.sobol_rows()
    assert np.all(np.abs(s1 - s1_mc) / e1_mc < 4.0)
    assert np.all(np.abs(st - st_mc) / et_mc < 4.0)


CSV_PATH = ROOT / "results" / "sobol_acquisition.csv"


@pytest.mark.skipif(not CSV_PATH.is_file(),
                    reason="producer not yet run in this checkout")
def test_committed_indices_are_internally_consistent():
    """The committed rows are exact, so the inequalities hold strictly:
    ST > S1 for every input (the model interacts), S1 sums below one,
    interaction_share carries an err (propagated from the floor fit), the
    cross-check z sits under 4, and every index err has two significant
    digits (LOGIC 8a.2)."""
    rows = {r["key"]: r for r in csv.DictReader(CSV_PATH.open())}
    assert float(rows["sum_S1"]["value"]) < 1.0
    assert float(rows["interaction_share"]["err"]) > 0.0
    for key in ("sum_S1", "interaction_share", "p_floor_fit"):
        digs = rows[key]["err"].replace(".", "").lstrip("0")
        assert 1 <= len(digs) <= 2, (key, rows[key]["err"])
    assert float(rows["mc_max_z"]["value"]) < 4.0
    for name in rsa.INPUTS:
        s1r, str_ = rows[f"S1_{name}"], rows[f"ST_{name}"]
        assert float(str_["value"]) > float(s1r["value"]), name
        for r in (s1r, str_):
            digs = r["err"].replace(".", "").lstrip("0")
            assert 1 <= len(digs) <= 2, (name, r["err"])
