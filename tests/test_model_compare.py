"""Model comparison returns evidence, and only the interpreter judges.

The invariant this file exists to protect: NO SINGLE STATISTIC IN THE OUTPUT
CAN RETURN "model preferred". That property is easy to lose in a later edit
and impossible to notice from a passing pipeline, so it is tested directly.
"""
from __future__ import annotations

import math

import pytest

from rb5s6s.model_compare import (ModelFit, compare,
                                  interpret_model_comparison as interpret)


def _pair(chi2_a=1000.0, chi2_b=900.0, ka=3, kb=4, n=500, n_eff=None,
          tau=None):
    """A nested pair. When n_eff is given, the whitened chi2 travels with it,
    which is the only combination the effective criteria accept."""
    ea = eb = None
    if n_eff is not None:
        t = tau if tau else n / n_eff
        ea, eb = chi2_a / t, chi2_b / t
    return (ModelFit("simpler", chi2_a, ka, n, n_eff, ea),
            ModelFit("richer", chi2_b, kb, n, n_eff, eb))


def test_no_single_statistic_returns_a_preference():
    """THE INVARIANT. The evidence object exposes directions per criterion and
    never one boolean answer, and no field is named to invite that reading."""
    a, b = _pair()
    ev = compare(a, b)
    assert not hasattr(ev, "preferred")
    assert not hasattr(ev, "winner")
    assert not hasattr(ev, "best_model")
    assert isinstance(ev.favours_richer(), dict)
    assert len(ev.favours_richer()) >= 3


def test_the_verdict_lives_only_in_the_interpreter():
    a, b = _pair()
    ev = compare(a, b)
    verdict = interpret(ev)["verdict"]
    assert verdict in {"robust", "convention-dependent",
                       "assumption-dependent", "unresolved"}
    assert "verdict" not in ev.__dict__


def test_f_statistic_always_carries_its_validity():
    a, b = _pair(n_eff=120.0)
    ev = compare(a, b)
    assert ev.f_validity == "conditional"
    assert "reference distribution is not F" in ev.f_reason
    assert "120" in ev.f_reason      # names the measured independence


def test_non_nested_models_get_no_f_statistic():
    a, b = _pair()
    ev = compare(a, b, nested=False)
    assert ev.f_statistic is None
    assert ev.f_validity == "not applicable"
    assert not ev.likelihood_ratio_valid


def test_effective_criteria_are_absent_rather_than_equal_without_n_eff():
    """Silently reporting the raw value as the effective one would hide the
    correlation question instead of raising it."""
    a, b = _pair(n_eff=None)
    ev = compare(a, b)
    assert ev.delta_bic_eff is None
    assert ev.delta_aicc_eff is None
    assert any("not equal to their raw" in n for n in ev.notes)


def test_the_effective_form_is_more_conservative_because_both_terms_change():
    """Correlation admitted properly makes the evidence WEAKER: the whitened
    chi2 gain shrinks by tau, which outweighs the smaller parameter penalty.
    Changing only the penalty would move it the other way, which is the
    bookkeeping error rb5s6s.sharing_bic records as flipping a verdict."""
    a, b = _pair(n=2000, n_eff=500.0)          # tau = 4
    ev = compare(a, b)
    assert ev.delta_bic_eff < ev.delta_bic


def test_the_effective_form_refuses_a_half_treatment():
    """n_eff without a whitened chi2 must raise, not silently reuse chi2."""
    m = ModelFit("m", 1000.0, 3, 2000, n_eff=500.0)
    with pytest.raises(ValueError, match="chi2_eff"):
        m.bic(effective=True)
    with pytest.raises(ValueError):
        ModelFit("bad", 1000.0, 3, 2000, None, 250.0)


def test_weak_evidence_is_unresolved_not_a_coin_flip():
    a, b = _pair(chi2_a=1000.0, chi2_b=999.0)
    assert interpret(compare(a, b))["verdict"] == "unresolved"
    assert interpret(compare(a, b))["favours_richer"] is None


def test_disagreement_between_raw_and_effective_is_assumption_dependent():
    """The case the whole split exists for: AIC wants the richer model, BIC on
    the effective count does not, so the answer is about the correlation
    treatment rather than about the models."""
    a = ModelFit("simpler", 1000.0, 2, 5000, 40.0, 8.0)
    b = ModelFit("richer", 985.0, 6, 5000, 40.0, 7.88)
    out = interpret(compare(a, b))
    assert out["verdict"] in {"assumption-dependent", "convention-dependent"}
    assert out["favours_richer"] is None


def test_uncalibrated_is_stated_in_the_output_not_only_the_docstring():
    a, b = _pair()
    ev = compare(a, b, bootstrap_p=0.2)
    assert any("UNCALIBRATED" in n for n in ev.notes)
    assert interpret(ev)["uncalibrated"] is True


def test_bic_and_aicc_reduce_correctly():
    m = ModelFit("m", chi2=100.0, k=3, n=50)
    assert m.bic() == pytest.approx(100.0 + 3 * math.log(50))
    assert m.aic() == pytest.approx(106.0)
    assert m.aicc() == pytest.approx(106.0 + 2 * 3 * 4 / (50 - 3 - 1))


def test_aicc_is_infinite_when_parameters_exhaust_the_data():
    assert math.isinf(ModelFit("m", 1.0, 10, 11).aicc())


def test_bad_pairs_are_rejected():
    a, b = _pair()
    with pytest.raises(ValueError):
        compare(b, a)                       # richer must be richer
    with pytest.raises(ValueError):
        compare(ModelFit("a", 1.0, 1, 100), ModelFit("b", 1.0, 2, 200))
    with pytest.raises(ValueError):
        ModelFit("bad", -1.0, 1, 10)
    with pytest.raises(ValueError):
        ModelFit("bad", 1.0, 1, 10, n_eff=20.0)


def test_reproduces_the_committed_ladder_rung_direction():
    """Ladder step 1, on the committed C->D rung: BIC disfavours the richer
    Stark model, and the interpreter must agree with the committed sign."""
    c = ModelFit("C_collisions", 43811.1, 4, 2000, 527.0, 11548.0)
    d = ModelFit("D_stark", 43909.7, 5, 2000, 527.0, 11574.0)
    ev = compare(c, d)
    assert ev.delta_bic < 0
    assert interpret(ev)["favours_richer"] is False
