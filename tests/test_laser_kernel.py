"""M38: the laser kernel as a model-form systematic, as a guard on its result.

The finding this pins is that the laser kernel's SHAPE was the largest
unexamined lever on the collisional coefficient, and that the archive
nonetheless prefers the Gaussian the record already assumed. If either half
of that changes, it is a result and not a detail.
"""

import csv
import statistics
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "laser_kernel.csv"


def _rows():
    if not CSV.exists():
        pytest.skip("results/laser_kernel.csv is not present in this checkout")
    return list(csv.DictReader(open(CSV)))


def test_every_condition_was_fitted_under_both_kernels():
    rows = _rows()
    assert len(rows) >= 30, f"only {len(rows)} conditions"
    for r in rows:
        for k in ("gamma_coll_gaussian", "gamma_coll_lorentzian",
                  "chi2_red_gaussian", "chi2_red_lorentzian"):
            assert float(r[k]) > 0.0, (k, r)


def test_the_kernel_choice_is_a_large_lever_on_the_collisional_width():
    """A median 45 per cent. If this ever falls under 10 per cent the two
    kernels have stopped competing and the degeneracy argument is wrong."""
    shifts = [float(r["gamma_coll_frac_shift"]) for r in _rows()]
    med = statistics.median(shifts)
    assert med < -0.10, f"median shift {med:.1%} is too small to be this lever"
    assert sum(1 for s in shifts if s < 0) >= 0.9 * len(shifts)


def test_the_committed_data_prefer_the_gaussian_kernel_unanimously():
    """The result that was NOT expected. The preregistered guess was that the
    archive could not tell the kernels apart. It can, on every condition."""
    diffs = [float(r["chi2_red_diff"]) for r in _rows()]
    worse = sum(1 for d in diffs if d > 0)
    assert worse == len(diffs), (
        f"the Lorentzian kernel now fits better on {len(diffs) - worse} "
        f"condition(s). That reverses a committed finding")


def test_the_lorentzian_needs_less_width_to_make_the_same_wings():
    """The mechanical check that the two kernels really are competing for the
    wings rather than differing in some unrelated way."""
    rows = _rows()
    g = statistics.median(float(r["sigma_laser_gaussian"]) for r in rows)
    l = statistics.median(float(r["sigma_laser_lorentzian"]) for r in rows)
    assert l < g, f"lorentzian width {l} is not below gaussian {g}"


def test_the_result_is_a_diagnostic_and_not_a_bound():
    """Nothing here measures a physical coefficient. It measures what an
    assumption costs and which of two the data prefer."""
    for r in _rows():
        assert r["status"] == "DIAGNOSTIC", r
