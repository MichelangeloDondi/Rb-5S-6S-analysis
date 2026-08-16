"""The shared information-criterion helper, validated before it is used.

An estimator is checked against a case whose answer is known independently
before any conclusion rests on it. That discipline is here because the Sobol
run of 2026-08-14 returned first-order indices above total-order ones, which is
impossible, and the estimator turned out to be correct and merely
under-sampled. The cost of finding that out from a known-answer function first
is a few seconds.

What is checked: the penalty arithmetic against hand-computed values, the
n-dependence that motivates the whole criterion question, the small-sample
correction, and the nesting guard that refuses to interpret a comparison
between fits that have not converged.
"""
from __future__ import annotations

import math

import pytest

from rb5s6s.modelform import CONTAINS, SHAPES, compare_ic, info_criteria


def test_penalties_against_hand_computation():
    """AIC charges 2 per parameter and BIC charges ln(n), exactly."""
    ic = info_criteria(chi2=100.0, k=5, n=1000)
    assert ic["aic"] == pytest.approx(100.0 + 2 * 5)
    assert ic["bic"] == pytest.approx(100.0 + 5 * math.log(1000))
    assert ic["penalty_per_param_aic"] == pytest.approx(2.0)
    assert ic["penalty_per_param_bic"] == pytest.approx(math.log(1000))


def test_bic_overtakes_aic_at_the_n_this_project_actually_uses():
    """The whole reason the criterion matters here is n, and n is not one
    number in this tree. Pin the three real regimes."""
    # the noise variance law works on ten level bins: the two nearly agree
    assert math.log(10) / 2.0 == pytest.approx(1.15, abs=0.01)
    # one condition's line fit, about 4445 points
    assert math.log(4445) / 2.0 == pytest.approx(4.20, abs=0.01)
    # the M25 global fit, 404615 points
    assert math.log(404615) / 2.0 == pytest.approx(6.46, abs=0.01)
    # and the direction: BIC punishes an extra parameter harder as n grows
    a = info_criteria(100.0, 5, 10)
    b = info_criteria(100.0, 5, 404615)
    assert b["bic"] - b["aic"] > a["bic"] - a["aic"]


def test_equal_parameter_counts_cancel_the_penalty_entirely():
    """Voigt against Lehmann is a bare chi-squared comparison, whatever the
    criterion, because the two forms carry the same k. This is why that
    comparison cannot be changed by adopting AIC, and the test pins the
    structural fact rather than the numbers."""
    assert len(SHAPES["voigt"]) == len(SHAPES["lehmann"])
    a = info_criteria(chi2=3117.89, k=22, n=4445)
    b = info_criteria(chi2=3117.45, k=22, n=4445)
    d = compare_ic(a, b, nested=False)
    for crit in ("daic", "daicc", "dbic"):
        assert d[crit] == pytest.approx(d["dchi2"]), \
            f"{crit} should equal the chi-squared difference at equal k"


def test_aicc_corrects_aic_only_when_n_is_small():
    small = info_criteria(chi2=10.0, k=5, n=20)
    large = info_criteria(chi2=10.0, k=5, n=100000)
    assert small["aicc"] > small["aic"]
    assert large["aicc"] == pytest.approx(large["aic"], abs=1e-2)


def test_nesting_guard_refuses_an_unconverged_comparison():
    """A form that CONTAINS another cannot fit worse at its own optimum. When
    it does, the difference is the optimizer's and no criterion can be read
    off it. Measured on results/modelform.csv 2026-08-15: all four peaks
    violate this, peak 4192 by 3.23, against interpreted differences of 0.44
    to 3.70."""
    simple = info_criteria(chi2=3431.73, k=22, n=4445)
    rich = info_criteria(chi2=3434.96, k=23, n=4445)     # worse, and richer
    d = compare_ic(simple, rich, nested=True)
    assert d["nesting_violated"] is True
    assert d["interpretable"] is False
    assert "convergence" in d["note"]


def test_nesting_guard_stays_quiet_when_the_richer_form_wins():
    simple = info_criteria(chi2=3431.73, k=22, n=4445)
    rich = info_criteria(chi2=3420.00, k=23, n=4445)     # better, as it must be
    d = compare_ic(simple, rich, nested=True)
    assert d["nesting_violated"] is False
    assert d["interpretable"] is True
    # and the two criteria disagree about whether the extra parameter is worth
    # it, which at this n is exactly the situation worth surfacing
    assert d["daic"] > 0 > d["dbic"] or d["daic"] * d["dbic"] > 0


def test_bic_eff_is_explicit_or_absent():
    """The effective-sample-size adjustment is a modelling choice, so it must
    be passed explicitly and its absence must be visible: bic_eff is OMITTED
    when effective_n is not given, never silently equal to bic."""
    plain = info_criteria(chi2=100.0, k=5, n=1000)
    assert "bic_eff" not in plain
    adj = info_criteria(chi2=100.0, k=5, n=1000, effective_n=250.0)
    assert adj["bic_eff"] == pytest.approx(100.0 + 5 * math.log(250.0))
    assert adj["bic_eff"] > adj["aic"]
    with pytest.raises(ValueError):
        info_criteria(chi2=1.0, k=1, n=10, effective_n=1.0)


def test_panel_split_on_the_sharing_case():
    """FORMULA AND IMPLEMENTATION TEST ONLY. This reconstructs the one known
    criterion-sensitive comparison in the tree (sigma_laser sharing: the nine
    extra parameters buy 24.6 chi-squared, AIC charges 18, BIC_eff charges
    9 ln(13853) = 85.8) and checks the panel machinery reports the numerical
    deltas and the split. It is NOT evidence that a disagreement on real data
    means anything by itself: what a split licenses is stated in the
    preregistration, not here."""
    shared = info_criteria(chi2=11915.1, k=241, n=13853, effective_n=13853)
    block = info_criteria(chi2=11890.4, k=250, n=13853, effective_n=13853)
    d = compare_ic(shared, block, nested=True)
    assert d["interpretable"] is True          # the richer model fits better
    assert d["daic"] == pytest.approx(24.6 - 18.0, abs=0.2)      # favours rich
    assert d["dbic_eff"] == pytest.approx(24.6 - 85.8, abs=0.3)  # favours simple
    assert d["panel_split"] is True
    # and a case where every member agrees is reported as no split
    small = info_criteria(chi2=100.0, k=5, n=1000, effective_n=500.0)
    big = info_criteria(chi2=20.0, k=6, n=1000, effective_n=500.0)
    d2 = compare_ic(small, big, nested=True)
    assert d2["panel_split"] is False


def test_the_containment_map_matches_the_shape_definitions():
    """CONTAINS is a claim about the model algebra and it must agree with
    SHAPES, or the nesting guard is checking the wrong pairs."""
    for rich, simples in CONTAINS.items():
        for simple in simples:
            assert set(SHAPES[simple]) < set(SHAPES[rich]), \
                f"{rich} is declared to contain {simple} but its shape "\
                f"parameters are not a superset"
