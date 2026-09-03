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
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "run_paired_reference_forecast",
    ROOT / "scripts" / "run_paired_reference_forecast.py")
# ONE MODULE OBJECT, WHATEVER ORDER PYTEST COLLECTS IN. See
# tests/conftest.py:load_script_module - the explanation lives there,
# once, rather than in each caller.
from conftest import load_script_module        # noqa: E402

prf = load_script_module("run_paired_reference_forecast", ROOT / "scripts" / "run_paired_reference_forecast.py")


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
    # a complete sensitivity block, because the prover now grades those
    # rows too - they state a verdict word and a scale, and they were
    # outside the check until a board found a column contradicted by its
    # own error column
    sens_note = ("X at x2 shifts the ratio by +0.10 +- 0.02 times the"
                 " error one run has on it, over 6 base seeds, and the"
                 " shift itself is resolved at 4 sigma of its own paired"
                 " error. Matters at one run's error: no")
    sens = [("sensitivity", f"{n}_{tag}", "0.6", "0.03", "ratio", sens_note)
            for n in prf.SENS_NAMES for tag in ("x2", "half")]
    # check rows too: the prover grades them since 2026-09-02, because
    # their notes carry the file's strongest universals - a raise
    # threshold and a population count - and were outside it
    checks = [
        ("check", "clean_lock_decomposition_sigma_analog", "1.78", "",
         "sigma", "separation in the measured row's se, and the"
                  " producer raises on the absolute gap at 0.05"),
        ("check", "width_ratio_within_2sigma", "29", "32", "count",
         "29 of 32 rows sit within two sigma of parity"),
    ]
    rows = [
        *checks,
        *[(f"span_j{k}", "criterion", "clears", "", "", good_note)
          for k in range(len(prf.JITTER_SPAN_MHZ))],
        ("limit", "a", "1.0", "0.1", "ratio", good_note),
        ("limit", "b", "1.0", "0.1", "ratio", good_note),
        *sens,
    ]
    prf._assert_verdict_rows(rows)
    with pytest.raises(RuntimeError, match="limit group holds 3"):
        prf._assert_verdict_rows(rows + [("limit", "c", "1", "", "", good_note)])
    renamed = [(("x_j1",) + r[1:] if r[0] == "span_j1" else r) for r in rows]
    with pytest.raises(RuntimeError, match="criterion rows against"):
        prf._assert_verdict_rows(renamed)
    # the sensitivity rows keep their own good notes in the plants
    # below: the prover grades them FIRST, so corrupting every note at
    # once would raise on the wrong shape and the plant would prove
    # nothing about the one it names
    keyword = [r[:5] + ("the threshold can be moved and re-read in sigma",)
               for r in rows if r[0] not in ("sensitivity", "check")
               ] + sens + checks
    with pytest.raises(RuntimeError, match="numeric sigma distance"):
        prf._assert_verdict_rows(keyword)
    no_thr = [r[:5] + ("a margin of 0.0 sigma to the runner-up",)
              for r in rows if r[0] not in ("sensitivity", "check")
              ] + sens + checks
    with pytest.raises(RuntimeError, match="named threshold"):
        prf._assert_verdict_rows(no_thr)
    # the two shapes the sensitivity half of the prover exists for
    short = [r for r in rows if r[1] != "GAMMA_FIBRE_x2"]
    with pytest.raises(RuntimeError, match="sensitivity rows for"):
        prf._assert_verdict_rows(short)
    unscaled = [r[:5] + (r[5].replace(
        "times the error one run has on it", "sigma combined"),)
        if r[0] == "sensitivity" else r for r in rows]
    with pytest.raises(RuntimeError, match="naming the denominator"):
        prf._assert_verdict_rows(unscaled)


def test_the_lineshape_is_unit_peak():
    """The Voigt normalisation: exactly one at the centre for any width
    pair, so amplitudes mean what the fits assume."""
    x = np.linspace(-10, 10, 2001)
    for gamma, sigma in ((3.89, 0.30), (5.6, 0.353), (1.0, 2.0)):
        y = prf._line(x, 0.0, gamma, sigma, 1.0)
        assert float(y.max()) == pytest.approx(1.0, abs=1e-9)


def test_the_sensitivity_verdict_has_three_states_and_uses_them():
    """`_sens_verdict` answers whether a doubled or halved constant
    moves the ratio by more than the error ONE run has on it.

    Three states, and the third is the point. The rule this replaces
    forced a side on an estimate that straddled the bar, and shipped a
    "yes" clearing by 0.005 that reversed when the replicate count
    went up. A quantity whose interval contains 1.0 has no side, and
    a third state says that instead of choosing one."""
    v = prf._sens_verdict
    assert v(1.85, 0.20) == "yes", "clear of the bar at its own lower edge"
    assert v(-1.85, 0.20) == "yes", "the sign must not matter"
    assert v(0.09, 0.01) == "no", "small and precisely known is still small"
    assert v(1.02, 0.10) == "at the bar", (
        "an estimate whose interval contains the bar was forced to a "
        "side, which is exactly the defect this rule was extracted for")
    assert v(0.95, 0.10) == "at the bar"


def test_the_sensitivity_verdict_refuses_a_collapsed_denominator():
    """A non-finite shift means the run error it divides by was zero,
    so the row would state a verdict about nothing. It raises rather
    than printing `no`, which is what an unguarded division would have
    produced: the reassuring answer."""
    import math
    with pytest.raises(RuntimeError, match="non-finite"):
        prf._sens_verdict(math.inf, 0.1)
    with pytest.raises(RuntimeError, match="non-finite"):
        prf._sens_verdict(math.nan, 0.1)




def test_the_decomposition_tolerance_refuses_and_permits_where_it_should():
    """The raise path that had no coverage anywhere.

    `grep decomp tests/` returned nothing before this: a producer that
    refuses to write its CSV, whose refusal condition nothing had ever
    exercised. Reaching it used to need a monkeypatched
    `_config_arrays` and a full run, which is why it was extracted.

    The tolerance is ABSOLUTE and that is the point. A sigma bar
    tightens as the sample grows, so a check calibrated at one draw
    refuses at six and refuses harder at twelve, while a wrong
    decomposition does not move with the sample at all."""
    tol = prf.DECOMP_ABS_TOL
    # inside the tolerance: writes, whatever the sigma says
    prf._assert_decomposition("analog", 0.96, 0.96 + tol * 0.5, 99.0)
    # past it: refuses, and names the gap and the tolerance
    with pytest.raises(RuntimeError, match="past the absolute tolerance"):
        prf._assert_decomposition("analog", 0.96, 0.96 + tol * 1.01, 0.1)
    # and the sign does not matter
    with pytest.raises(RuntimeError, match="past the absolute tolerance"):
        prf._assert_decomposition("counting", 0.96, 0.96 - tol * 1.01, 0.1)


def test_the_tolerance_is_absolute_and_not_a_sigma_bar():
    """The property the repair turned on, pinned so a later edit
    cannot quietly put the sigma back. A huge sigma inside the
    tolerance must pass, and a tiny sigma outside it must fail -
    exactly the two cases a sigma bar gets backwards."""
    tol = prf.DECOMP_ABS_TOL
    prf._assert_decomposition("analog", 0.96, 0.96 + tol * 0.9, 1e6)
    with pytest.raises(RuntimeError):
        prf._assert_decomposition("analog", 0.96, 0.96 + tol * 2, 0.0)
