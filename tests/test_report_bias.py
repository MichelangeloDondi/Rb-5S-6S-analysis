"""The bias printer's refusals, run by the suite and not only by its own self-test.

An instrument whose plant is invoked only by hand is an asserted instrument, so the module's
`_self_test` runs here as one case and the refusals it covers are asserted again through the
public call path, which is what a later reader can break.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from rb5s6s.report import BiasRefused, bias_with_coverage, format_bias, report_bias


def test_the_modules_own_plant_passes():
    from rb5s6s import report
    assert report._self_test() == 0


@pytest.mark.parametrize("what, values, truth, bars", [
    ("one realisation carries no standard error", [1.0], 0.0, [1.0]),
    ("a non-finite value is not a mean", [1.0, float("nan")], 0.0, [1.0, 1.0]),
    ("no finite bar means no coverage", [1.0, 2.0], 0.0, [float("nan"), float("inf")]),
    ("a bar per realisation or none", [1.0, 2.0, 3.0], 0.0, [1.0, 1.0]),
])
def test_a_bias_without_its_evidence_is_refused(what, values, truth, bars):
    with pytest.raises(BiasRefused):
        bias_with_coverage(values, truth, bars)


def test_the_noiseless_rung_reports_rather_than_refusing():
    """F226: at zero noise the realisations are identical by construction, and the first draft of
    this module raised on a zero scatter -- which made it useless for the rung every ladder requires
    FIRST, and would have sent every noiseless bias back to whatever each harness printed by hand."""
    s = bias_with_coverage([42.0] * 8, 42.0, [1.0] * 8)
    assert s["deterministic"] is True
    assert s["bias"] == 0.0 and s["bias_se"] == 0.0
    assert "exactly" in format_bias(s), "a zero bar must be said in words, not printed as '+- 0.0'"
    assert "+- 0" not in format_bias(s)


def test_a_refusal_prints_nothing_before_it_raises():
    """A printer that emits and then raises has already published the number."""
    printed = []
    with pytest.raises(BiasRefused):
        report_bias("planted", [1.0], 0.0, [1.0], printer=printed.append)
    assert printed == []


def test_the_uncertainty_carries_two_significant_digits_and_the_value_follows_it():
    """Owner order O35: the bias's uncertainty at two significant digits, the value to its decimals."""
    assert format_bias({"bias": 0.6094, "bias_se": 0.1372}) == "0.61 +- 0.14"
    assert format_bias({"bias": 12.3456, "bias_se": 1.7}) == "12.3 +- 1.7"
    assert "0.00012" in format_bias({"bias": -0.00066, "bias_se": 0.000123})


def test_the_standard_error_is_the_scatter_over_root_n_and_coverage_is_a_fraction():
    rng = np.random.default_rng(11)
    v = 42.0 + 0.5 + rng.normal(0.0, 0.4, 64)
    s = bias_with_coverage(v, 42.0, np.full(64, 1.0))
    assert s["bias_se"] == pytest.approx(s["sd"] / math.sqrt(s["n"]))
    assert 0.0 <= s["coverage"] <= 1.0
    assert s["n_with_bar"] == 64


def test_a_bar_that_is_absent_for_some_realisations_still_yields_a_coverage_over_those_it_has():
    """The coverage's denominator is the realisations that REPORTED a bar, and it is returned."""
    bars = [1.0, float("nan"), 1.0, 1.0]
    s = bias_with_coverage([42.1, 42.2, 41.9, 42.0], 42.0, bars)
    assert s["n"] == 4 and s["n_with_bar"] == 3
    assert s["coverage"] == pytest.approx(1.0)
