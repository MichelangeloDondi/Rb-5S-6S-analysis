"""The paired-reference forecast's own guards.

The producer emits categorical verdicts (clears / fails / unresolved)
whose logic no single run is guaranteed to exercise: no seeded run had
produced the unresolved branch until the sample was raised, and the
selection state once forced unresolved on same-side candidates. These tests pin the verdict logic directly, so every
branch is exercised on every run regardless of what the seeded Monte
Carlo happens to produce. Failure mode guarded: a verdict branch that
has never fired cannot be told from one that cannot fire.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "run_paired_reference_forecast",
    ROOT / "scripts" / "run_paired_reference_forecast.py")
prf = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("run_paired_reference_forecast", prf)
_spec.loader.exec_module(prf)


def test_the_three_verdict_states_all_fire():
    """clears at +1 sigma and beyond, fails at -1 and beyond, and the
    unresolved branch — the one no run produced until the sample was
    raised — in between. The threshold is read from the module so an
    owner adjustment moves the test with it."""
    thr = prf.RATIO_THRESHOLD
    dist, state = prf._dist_and_state(thr - 0.2, 0.1)
    assert state == "clears" and dist == pytest.approx(2.0)
    dist, state = prf._dist_and_state(thr + 0.2, 0.1)
    assert state == "fails" and dist == pytest.approx(-2.0)
    dist, state = prf._dist_and_state(thr + 0.05, 0.1)
    assert state == "unresolved" and dist == pytest.approx(-0.5)


def test_the_unresolved_boundary_is_closed_at_one_sigma():
    """The licensing rule is one sigma: just past it resolves, just
    inside does not (exact float equality at the boundary is not
    asserted, only the two sides of it)."""
    thr = prf.RATIO_THRESHOLD
    assert prf._dist_and_state(thr - 0.101, 0.1)[1] == "clears"
    assert prf._dist_and_state(thr - 0.099, 0.1)[1] == "unresolved"


def test_zero_se_resolves_by_side_and_ties_do_not():
    """A zero se yields an infinite distance of the right sign on both
    sides, and the one value it cannot resolve, the exact tie, says
    unresolved."""
    thr = prf.RATIO_THRESHOLD
    dist, state = prf._dist_and_state(thr - 0.1, 0.0)
    assert np.isinf(dist) and dist > 0 and state == "clears"
    dist, state = prf._dist_and_state(thr + 0.1, 0.0)
    assert np.isinf(dist) and dist < 0 and state == "fails"
    dist, state = prf._dist_and_state(thr, 0.0)
    assert dist == 0.0 and state == "unresolved"


def test_criterion_state_every_branch():
    """The span verdict's four ways out, including the branch no seeded
    run has produced: a sub-sigma selection margin whose candidates
    disagree on the side."""
    thr = prf.RATIO_THRESHOLD
    # resolved side, wide margin: the worst's own state stands
    state, dist, margin, by = prf._criterion_state(
        thr + 0.5, 0.1, thr - 0.5, 0.1)
    assert state == "fails" and by == ""
    # unresolved by distance
    state, dist, margin, by = prf._criterion_state(
        thr + 0.05, 0.1, thr - 0.5, 0.1)
    assert state == "unresolved" and by == "the distance"
    # sub-sigma margin, candidates agreeing: the side stands
    state, dist, margin, by = prf._criterion_state(
        thr + 0.5, 0.1, thr + 0.45, 0.1)
    assert state == "fails" and margin < 1.0 and by == ""
    # sub-sigma margin, candidates disagreeing: unresolved
    state, dist, margin, by = prf._criterion_state(
        thr + 0.15, 0.1, thr - 0.05, 0.2)
    assert state == "unresolved"
    assert by == "a selection whose candidates disagree"


def test_jackknife_matches_a_hand_computation():
    """The delete-one jackknife on a four-element pair, against the
    textbook formula computed longhand here."""
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([2.0, 1.0, 4.0, 3.0])
    full, se = prf._jack_ratio(a, b)
    assert full == pytest.approx(float(np.std(b) / np.std(a)))
    reps = [float(np.std(np.delete(b, i)) / np.std(np.delete(a, i)))
            for i in range(4)]
    hand = float(np.sqrt(3 / 4 * sum((r - np.mean(reps)) ** 2
                                     for r in reps)))
    assert se == pytest.approx(hand)


def test_the_verdict_row_check_catches_every_shape():
    """The failure shapes an inline check could not be planted against:
    a row rejoining limit, a renamed criterion prefix, a note with no
    numeric distance, and a note that never names the threshold."""
    thr_word = f"{prf.RATIO_THRESHOLD:g} threshold"
    good_note = f"sits 2.0 sigma of its own se below the {thr_word}"
    rows = [
        *[(f"span_j{k}", "criterion", "clears", "", "", good_note)
          for k in range(len(prf.JITTER_SPAN_MHZ))],
        ("limit", "a", "1.0", "0.1", "ratio", good_note),
        ("limit", "b", "1.0", "0.1", "ratio", good_note),
    ]
    prf._assert_verdict_rows(rows)
    with pytest.raises(RuntimeError, match="limit group holds 3"):
        prf._assert_verdict_rows(rows + [("limit", "c", "1", "", "", good_note)])
    renamed = [(("x_j1",) + r[1:] if r[0] == "span_j1" else r) for r in rows]
    with pytest.raises(RuntimeError, match="criterion rows against"):
        prf._assert_verdict_rows(renamed)
    keyword = [r[:5] + ("the threshold can be moved and re-read in sigma",)
               for r in rows]
    with pytest.raises(RuntimeError, match="numeric sigma distance"):
        prf._assert_verdict_rows(keyword)
    no_thr = [r[:5] + ("a margin of 0.0 sigma to the runner-up",)
              for r in rows]
    with pytest.raises(RuntimeError, match="named threshold"):
        prf._assert_verdict_rows(no_thr)


def test_the_lineshape_is_unit_peak():
    """The Voigt normalisation: exactly one at the centre for any width
    pair, so amplitudes mean what the fits assume."""
    x = np.linspace(-10, 10, 2001)
    for gamma, sigma in ((3.89, 0.30), (5.6, 0.353), (1.0, 2.0)):
        y = prf._line(x, 0.0, gamma, sigma, 1.0)
        assert float(y.max()) == pytest.approx(1.0, abs=1e-9)
