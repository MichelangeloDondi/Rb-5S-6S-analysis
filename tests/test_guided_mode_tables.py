"""The guided-mode tables, graded on the commit that introduces them.

WHY THIS FILE EXISTS AND WHY IT EXISTS NOW.

`test_committed_csvs_still_match_their_producers` compares a producer's output
against `HEAD`. A file that is not yet in `HEAD` has nothing to compare
against, so **a new producer's first commit is graded by nothing while looking
graded** -- the guard passes by vacancy. This record has already paid for that
once, when `results/delta_alpha_posterior.csv` shipped a note asserting a
claim the same night had retracted.

So the rows below are pinned here, in the same commit that introduces them,
against values recomputed from the package rather than copied from the CSV.
The point is not the digits. It is that the file is inside SOME guard's
population from its first commit.

WHAT WOULD MAKE THESE NUMBERS WRONG, stated so a reader knows what is being
protected: the mode solve losing its root, the vector fields losing their
boundary conditions, or the transit kernel silently returning to the retired
form. Each has its own test in `test_fibre_mode.py`; these check that the
COMMITTED FILE still says what the package computes.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

from rb5s6s.fibre import (HE11Field, TRANSIT_KERNEL_FACTOR, solve_he11,
                          transit_fwhm)

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "guided_mode_tables.csv"


def _rows() -> dict[tuple[str, str], str]:
    with CSV.open() as fh:
        return {(r["scope"], r["quantity"]): r["value"] for r in csv.DictReader(fh)}


def test_the_file_exists_and_is_not_empty():
    assert CSV.exists(), "the producer has never been run into results/"
    assert len(_rows()) >= 108


@pytest.mark.parametrize("d", [350.0, 370.0, 400.0])
def test_the_mode_solve_rows_match_the_package(d):
    r = _rows()
    m = solve_he11(d, 993.4181)
    scope = f"mode_solve_{d:.0f}nm"
    assert float(r[(scope, "neff")]) == pytest.approx(m.neff, rel=1e-5)
    assert float(r[(scope, "amplitude_decay_length")]) == pytest.approx(
        m.amplitude_decay_nm, abs=1.0)
    assert float(r[(scope, "intensity_decay_length")]) == pytest.approx(
        m.intensity_decay_nm, abs=1.0)


@pytest.mark.parametrize("d", [350.0, 370.0, 400.0])
def test_qa_is_far_below_the_asymptotic_regime(d):
    """The row that decides whether an exponential is available at all."""
    qa = float(_rows()[(f"mode_solve_{d:.0f}nm", "qa")])
    assert 0.15 < qa < 0.40, "an exponential profile would need qa >> 1"


@pytest.mark.parametrize("dist", [100.0, 200.0, 400.0, 600.0])
def test_the_profile_rows_match_the_validated_fields(dist):
    r = _rows()
    fld = HE11Field(370.0, 993.4181)
    scope = f"evanescent_profile_370nm_at_{dist:.0f}nm"
    assert float(r[(scope, "flux_fraction")]) == pytest.approx(
        fld.intensity_at(dist * 1e-9), abs=1e-3)


@pytest.mark.parametrize("dist", [100.0, 200.0, 400.0, 600.0])
def test_the_exponential_overstates_and_worsens_with_distance(dist):
    """A single quoted factor is wrong, which is why the ratio is a row."""
    r = _rows()
    scope = f"evanescent_profile_370nm_at_{dist:.0f}nm"
    assert float(r[(scope, "exponential_overstatement")]) > 1.0


def test_the_overstatement_grows_monotonically():
    r = _rows()
    ratios = [float(r[(f"evanescent_profile_370nm_at_{d:.0f}nm", "exponential_overstatement")])
              for d in (100.0, 200.0, 400.0, 600.0)]
    assert all(a < b for a, b in zip(ratios, ratios[1:])), ratios


@pytest.mark.parametrize("kernel", sorted(TRANSIT_KERNEL_FACTOR))
def test_the_transit_rows_match_the_package(kernel):
    r = _rows()
    scope = f"transit_kernel_{kernel}"
    lam = solve_he11(370.0, 993.4181).intensity_decay_nm * 1e-9
    expect = transit_fwhm(150e-6, lam, kernel=kernel).fwhm_hz / 1e3
    assert float(r[(scope, "fwhm")]) == pytest.approx(expect, rel=1e-3)
    assert float(r[(scope, "factor")]) == pytest.approx(
        TRANSIT_KERNEL_FACTOR[kernel], rel=1e-3)


def test_the_retired_kernel_is_present_and_is_the_widest():
    """It is carried so the size of the correction stays visible."""
    r = _rows()
    widths = {k: float(r[(f"transit_kernel_{k}", "fwhm")])
              for k in TRANSIT_KERNEL_FACTOR}
    assert max(widths, key=widths.get) == "amplitude_lorentzian"
    assert widths["amplitude_lorentzian"] / widths["ensemble_speed"] > 3.0


def test_the_single_velocity_factor_is_the_closed_form():
    r = _rows()
    got = float(r[("transit_kernel_single_velocity", "factor")])
    assert got == pytest.approx(math.sqrt(math.sqrt(2.0) - 1.0), rel=1e-3)
