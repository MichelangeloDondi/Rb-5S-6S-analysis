"""The guided transit kernel enters the width at SECOND order, and stays so.

WHY THIS FILE EXISTS, AND IT IS LOGIC 0d.2 APPLIED TO ITS OWN CASE.

The fraction of its own width that the guided transit kernel contributes to the
observed line was wrong three times on 2026-08-28. It was "adds exactly", the
retracted Lorentzian claim. It was corrected to "adds almost exactly", also
false. It was then given a coefficient fitted by convolving a SINGLE squared
Lorentzian at the ensemble's FWHM, when the ensemble is a MIXTURE, and a
mixture and a single component of equal FWHM have entirely different curvature
at the origin -- which is what the added width depends on.

Each time the repair was a corrected literal. LOGIC 0d.2 says a rule broken
three times should have been a guard and that the third breach buys a
mechanism, so `scripts/run_transit_additivity.py` computes the quantity and
this file holds its properties.

WHAT IS ASSERTED, AND WHY EACH ONE WOULD HAVE CAUGHT SOMETHING.

* The producer's kernel reproduces `TRANSIT_KERNEL_FACTOR`. The third defect
  was a kernel that was not the record's own; nothing compared them.
* The temperature exponent is near 1 and not near 0.5. Linear additivity gives
  0.5, because the kernel's FWHM goes as sqrt(T). Second order gives 1. This is
  the single sharpest discriminator between the retracted claim and the live
  one, and it is one number.
* The two routes agree to about a tenth on every branch, and the signed gap is
  NEGATIVE: a Gaussian of matched second moment OVERSHOOTS the convolution.
  The two agree at leading order by construction: the added width is linear in
  the kernel's second moment with a coefficient set by the base profile alone,
  and route B matches that moment, so the kernel's shape drops out and the gap
  is the first-order term. If the sign flips, check the velocity weight.

  This bullet asserted the OPPOSITE until 2026-08-28, that the convolution
  exceeds the matched Gaussian and that the gap orders with the spread of tau.
  Both were consequences of a wrong velocity weight, and the tests enforcing
  them were replaced rather than repaired.

WHAT IS NOT ASSERTED. No absolute value of the fraction is pinned here. It
depends on the Lorentzian it is convolved against, so pinning it would make
this a tripwire on the twin's configuration rather than a check on the physics.
The producer emits it; `docs/methods/09` cites the row.
"""
from __future__ import annotations

import csv

import pytest

from rb5s6s import config as C
from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR

CSV = C.RESULTS_DIR / "transit_additivity.csv"
BRANCHES = ("single_velocity", "ensemble_flux", "ensemble_speed")


def _rows():
    if not CSV.is_file():
        pytest.skip(f"{CSV.name} not produced yet")
    with CSV.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _val(rows, branch, quantity):
    for r in rows:
        if r["branch"] == branch and r["quantity"] == quantity:
            return float(r["value"])
    raise AssertionError(f"no row {branch}/{quantity} in {CSV.name}")


@pytest.mark.parametrize("branch", BRANCHES)
def test_the_producers_kernel_is_the_records_kernel(branch):
    """A producer computing its own kernel answers its own question."""
    d = _val(_rows(), branch, "kernel_fwhm_vs_package")
    assert d < 1e-3, (
        f"{branch}: this producer's kernel differs from transit_fwhm by "
        f"{d:.2%}. TRANSIT_KERNEL_FACTOR[{branch!r}] = "
        f"{TRANSIT_KERNEL_FACTOR[branch]}. The defect this file exists for was "
        "exactly a kernel that was not the record's own.")


@pytest.mark.parametrize("branch", BRANCHES)
def test_the_added_width_scales_as_T_and_not_as_its_square_root(branch):
    """The one number that separates the retracted claim from the live one."""
    p = _val(_rows(), branch, "temperature_exponent")
    assert 0.9 < p < 1.1, (
        f"{branch}: the added width scales as T**{p:.3f}. Second order gives "
        "1; LINEAR ADDITIVITY GIVES 0.5, because the kernel's own FWHM goes as "
        "sqrt(T). A value near 0.5 means the retracted 'adds exactly' claim "
        "has returned in the arithmetic even if the prose says otherwise.")


@pytest.mark.parametrize("branch", BRANCHES)
def test_the_gap_shrinks_as_the_kernel_narrows(branch):
    """The gap is a first-order term, so it must fall with temperature.

    THIS REPLACED A GUARD THAT COULD NEVER FIRE. Its predecessor asserted
    `abs(g) < 0.167` on one branch while a sibling asserted `abs(g) <= 0.15`
    over all three, so the looser one was strictly subsumed and could not fail
    first, in work whose subject was guards green by construction.

    What is worth checking per branch is the SCALING. The gap is the
    first-order correction in sigma_nu/gamma, so it must shrink as the kernel
    narrows, and the kernel narrows as sqrt(T). A gap that does not fall with
    temperature is not a first-order term, whatever its size.

    RETIRED ASSERTION, named so it is not revived: this file once required the
    gap POSITIVE, reading a value emitted through `abs()` so the assertion
    could not fail on a sign at all.
    """
    rows = _rows()
    hot = abs(_val(rows, branch, "gaussian_curvature_gap_170uK"))
    cold = abs(_val(rows, branch, "gaussian_curvature_gap_10uK"))
    assert cold < hot, (
        f"{branch}: the two-route gap is {cold} at 10 uK and {hot} at 170 uK. "
        f"It should FALL as the kernel narrows, because it is the first-order "
        f"term in sigma_nu/gamma. If it does not, the disagreement is not a "
        f"first-order effect and one of the routes is wrong.")


def test_the_two_routes_agree_to_about_a_tenth():
    """Two routes sharing no code must land on one number, or neither is it.

    THIS TEST REPLACED AN ORDERING ASSERTION THAT WAS ENCODING A BUG.
    It used to require single < flux < speed on a quantity called the
    "shortfall", which held only because the producer averaged v^2 under
    s^k instead of s^(k+1) and understated the ensemble curvatures by 3/2
    and 2. The ordering it checked was the ordering of the error, so the
    guard passed BECAUSE the physics was wrong and would have failed on the
    repair. It was found by re-deriving the weight, not by reading the test.

    What is worth asserting is the property the two routes exist for: they
    share no code -- one is a numerical convolution of the record's own
    kernel integral, the other an analytic Voigt-moment estimate -- so
    agreement is evidence and disagreement is a defect. Ten per cent is the
    scale at which curvature-matching is expected to differ from a full
    convolution, and it is checked as a magnitude with the SIGN reported
    separately, because the sign was the thing abs() hid.
    """
    rows = _rows()
    gaps = {b: _val(rows, b, "gaussian_curvature_gap_170uK")
            for b in ("single_velocity", "ensemble_flux", "ensemble_speed")}
    bad = {b: g for b, g in gaps.items() if abs(g) > 0.15}
    assert not bad, (
        f"two independent routes to the added width disagree by more than "
        f"15 per cent: {bad}. All three branches: {gaps}. They share no code, "
        f"so this is a defect in one of them and not a property of the "
        f"kernel.")


def test_the_curvature_matched_gaussian_overshoots_on_every_branch():
    """The sign is part of the answer, so it is asserted rather than absorbed.

    Matching the second moment OVERSTATES the added width on every branch. The
    two routes agree at leading order by construction, so what is left is the
    first-order term, and the kernel's time function exceeds its
    moment-matched Gaussian at third order, which makes that term negative.

    THIS TEST WAS WRITTEN ASSERTING THE OPPOSITE FOR ONE BRANCH AND THE
    PRODUCER REFUTED IT. The first draft claimed the single-velocity branch
    should come out positive, having no mixture to broaden its matched
    Gaussian. Run, it is -0.075.

    AND THE ACCOUNT THAT FIRST REPLACED IT WAS ALSO WRONG, in the flattering
    direction. It said the sign had been negative on all three branches from
    the beginning with abs() hiding it. Reconstructed from the old committed
    rows, the old signed gaps were -0.075, +0.265 and +0.454: abs() hid a
    negative on ONE branch and the wrong weight manufactured genuine positives
    on the other two. Exposing the sign alone would have caught the first and
    passed the other two, and the retired ordering test would still have
    passed, because 0.075 < 0.265 < 0.454. Two errors each concealed the
    other's signature, which is why one repair could not have found this.
    """
    rows = _rows()
    for b in ("single_velocity", "ensemble_flux", "ensemble_speed"):
        g = _val(rows, b, "gaussian_curvature_gap_170uK")
        assert g < 0, (
            f"{b}: the curvature-matched Gaussian should overshoot the full "
            f"convolution, so the signed gap should be negative and it is "
            f"{g}. If this flips, check the velocity weight in "
            f"`_second_order_prediction` before believing it.")
