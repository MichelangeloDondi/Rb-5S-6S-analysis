"""M38: the laser kernel as a model-form systematic, as a guard on its result.

WHAT THIS FILE PINS, and what it deliberately no longer pins.

The finding is that the laser kernel's SHAPE is the largest unexamined lever
on the collisional coefficient. That stands, at the HEADLINE: run under the
record's own hierarchical estimator the kernel moves beta_self by 45 to 67 per
cent (results/kernel_headline.csv).

TWO THINGS THIS FILE USED TO ASSERT AND NO LONGER DOES, because both were
withdrawn on 2026-08-20.

  * A median 45 per cent shift in the PER-CONDITION gamma_coll. Under a
    Lorentzian laser kernel the model at a fixed condition depends on
    gamma_coll and sigma_laser only through their SUM, so neither is
    identified there and the "shift" was where an optimiser stopped along a
    flat direction. This file asserted `med < -0.10` on exactly that number,
    which made a retracted quantity a guarded invariant. Removed.

  * "The archive prefers the Gaussian on 32 conditions of 32." The
    pure-Lorentzian model is NESTED inside the Gaussian one: send the Gaussian
    width to zero and a delta function remains, leaving a single Lorentzian
    whose width the free gamma_coll can set to anything the other arm reaches.
    A containing model cannot fit worse, so unanimity was guaranteed before
    any data existed. The tally is kept below but its MEANING is inverted: it
    now guards the OPTIMISER, because a Lorentzian win would mean the fit had
    failed to find a minimum the containing model provably has.

What replaces the withdrawn preference is the SIZE of the improvement read as
the nested likelihood ratio it is, which is why the producer now emits `dof`
and `delta_chi2`.
"""

import csv
import statistics
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "laser_kernel.csv"
HEADLINE = ROOT / "results" / "kernel_headline.csv"


def _rows(path=CSV):
    if not path.exists():
        pytest.skip(f"{path.name} is not present in this checkout")
    return list(csv.DictReader(open(path)))


def test_every_condition_was_fitted_under_both_kernels():
    rows = _rows()
    assert len(rows) >= 30, f"only {len(rows)} conditions"
    for r in rows:
        for k in ("gamma_coll_gaussian", "gamma_coll_lorentzian",
                  "chi2_red_gaussian", "chi2_red_lorentzian"):
            assert float(r[k]) > 0.0, (k, r)


def test_the_kernel_choice_is_a_large_lever_on_the_HEADLINE_coefficient():
    """The lever claim, moved to the quantity that actually carries it.

    The per-condition version of this guard asserted on gamma_coll_frac_shift,
    which is not identified. The headline is, because its estimator varies
    density and density is the only thing separating a collisional width from
    a laser one.
    """
    rows = _rows(HEADLINE)
    shifts = [abs(float(r["beta_frac_shift"])) for r in rows]
    med = statistics.median(shifts)
    assert med > 0.30, (
        f"median headline shift {med:.1%} is too small to be this lever; "
        f"the kernel was the largest single assumption on beta_self")
    for r in rows:
        assert abs(float(r["beta_shift_in_sigma"])) > 5.0, (
            f"{r['peak']}: kernel shift {r['beta_shift_in_sigma']} sigma no "
            f"longer exceeds the quoted statistical error")


def test_the_gaussian_arm_cannot_fit_worse_because_it_CONTAINS_the_other():
    """Not evidence about the laser. A guard on the optimiser.

    The Lorentzian model is a boundary case of the Gaussian one, so the
    Gaussian arm's minimum chi-square is at most the Lorentzian arm's, as a
    matter of arithmetic. A condition where the Lorentzian wins is therefore
    not a discovery about the laser, it is a fit that failed to reach a
    minimum known to exist.
    """
    diffs = [float(r["chi2_red_diff"]) for r in _rows()]
    worse = sum(1 for d in diffs if d >= 0)
    assert worse == len(diffs), (
        f"the Lorentzian kernel fits better at {len(diffs) - worse} "
        f"condition(s). The Lorentzian model is CONTAINED in the Gaussian "
        f"one, so this cannot happen from the data. It means the Gaussian "
        f"arm's optimiser did not converge there")


def test_the_nested_likelihood_ratio_is_reported_and_self_consistent():
    """The quantity that replaced the withdrawn sign test.

    delta_chi2 must equal chi2_red_diff times the degrees of freedom, so a
    reader can recompute the comparison from this file alone rather than
    trusting a number quoted in prose.
    """
    rows = _rows()
    for k in ("n_points", "dof", "delta_chi2"):
        assert k in rows[0], (
            f"{k} is missing: the nested likelihood ratio cannot be "
            f"recomputed from the CSV, so the numbers quoted in the docs "
            f"would be orphan literals")
    for r in rows:
        want = float(r["chi2_red_diff"]) * int(r["dof"])
        assert abs(float(r["delta_chi2"]) - want) < 0.5 * max(1.0, abs(want) * 1e-3), (
            f"delta_chi2 {r['delta_chi2']} does not match chi2_red_diff x dof "
            f"({want:.1f}) at {r['peak']} {r['T']}C {r['P']}mW")


def test_a_pure_lorentzian_laser_is_excluded_at_most_conditions():
    """The surviving claim, stated as a count rather than as a p-value.

    A sign test on a nested comparison has no null to test against. The number
    of conditions where the improvement is large IS informative.
    """
    dchi2 = [float(r["delta_chi2"]) for r in _rows()]
    strong = sum(1 for d in dchi2 if d > 9.0)      # three sigma, one parameter
    assert strong >= 20, (
        f"only {strong} of {len(dchi2)} conditions exclude a purely "
        f"Lorentzian laser contribution above three sigma; the record's "
        f"Gaussian assumption rests on this margin")
    assert statistics.median(dchi2) > 50.0, (
        f"median delta chi2 {statistics.median(dchi2):.1f} has collapsed")


def test_the_result_is_a_diagnostic_and_not_a_bound():
    """Nothing here measures a physical coefficient. It measures what an
    assumption costs, and how strongly the line rejects one corner of it."""
    for r in _rows():
        assert r["status"] == "DIAGNOSTIC", r
