"""The laser_kind knob's DEGENERACY STRUCTURE, pinned at both assembly sites.

WHAT THESE GUARD. Two Lorentzians of FWHM a and b convolve to a single
Lorentzian of FWHM a+b. So under laser_kind="lorentzian" the profile at a
fixed condition can depend on gamma_coll and sigma_laser ONLY through their
sum, and the split between them carries no information whatsoever.

Until 2026-08-20 the code realised that identity by CONVOLVING the two
Lorentzians on a finite grid. Finite grids truncate Lorentzian tails, the
truncation depends on the grid span, and the span depends on how a given
total width is split -- so the implementation made the profile depend on the
split by up to 3.7e-3 of peak when the mathematics says it cannot depend on
it at all. That is a numerically manufactured separability pointing along
exactly the direction a laser-width inference has to measure, and against the
archive's own noise over ~1e4 points per condition it carried up to 70-sigma
matched-filter leverage. Fitting it would have been fitting round-off.

The fix folds a Lorentzian laser width into `homog` instead. These tests pin
the fix in both directions, because a degeneracy test that can only pass is
uninterpretable (protocol rule 19.53):

  * the Lorentzian branch IS exactly sum-degenerate -- bit-identical, not
    merely close, since the identity is exact and any tolerance would hide a
    return of the artefact;
  * the GAUSSIAN branch is NOT, under the very same move, which is the
    should-fail control proving the instrument can see a split when one
    exists;
  * the Gaussian branch is unchanged by the edit, so no committed number moves.
"""
import numpy as np
import pytest

from rb5s6s.lineshape import composite_profile, model_profile, GAMMA_NAT_HZ
from rb5s6s.linefit import _shared_profile_grid

GC, SL, TR = 0.5848, 1.5334, 0.35          # a canonical 4121 / 130 C / 225 mW point
D = 0.25                                    # a large sum-preserving move, not a nudge


def _resample(builder, gc, sl):
    """Both builders self-size their grid, so compare on a common axis."""
    nu = np.linspace(-8.0, 8.0, 801)
    g, p = builder(gc, sl)
    return np.interp(nu, g, p)


BUILDERS = {
    "composite_profile":
        lambda kind: (lambda gc, sl: composite_profile(gc, sl, TR, kind)),
    "shared_profile_grid":
        lambda kind: (lambda gc, sl: _shared_profile_grid(gc, sl, TR, 0.0, kind)),
}


@pytest.mark.parametrize("site", sorted(BUILDERS))
def test_lorentzian_branch_is_exactly_sum_degenerate(site):
    build = BUILDERS[site]("lorentzian")
    base = _resample(build, GC, SL)
    moved = _resample(build, GC + D, SL - D)
    assert np.array_equal(base, moved), (
        f"{site}: moving gamma_coll and sigma_laser in opposite directions by "
        f"{D} MHz changed the profile, but the sum is unchanged and two "
        f"Lorentzians convolve to their summed width exactly. The laser width "
        f"is being convolved rather than added again, which manufactures a "
        f"split-dependence out of grid truncation.")


@pytest.mark.parametrize("site", sorted(BUILDERS))
def test_gaussian_branch_is_not_sum_degenerate(site):
    """The should-fail control: without it the test above could pass on a
    function that returns a constant."""
    build = BUILDERS[site]("gaussian")
    base = _resample(build, GC, SL)
    moved = _resample(build, GC + D, SL - D)
    rel = float(np.max(np.abs(moved - base)) / np.max(np.abs(base)))
    assert rel > 1e-3, (
        f"{site}: the SAME move left the Gaussian profile unchanged too "
        f"(rel {rel:.2e}), so the degeneracy test above is measuring a dead "
        f"function rather than the model.")


def test_lorentzian_branch_has_the_summed_width():
    """The identity itself, stated as the quantity it is about: the WIDTH.

    Uses model_profile rather than composite_profile because only the former
    can be asked for no transit kernel at all (composite_profile always
    convolves one, and a zero width divides by zero inside the two-sided
    exponential). With transit and Stark off, the model must reduce to a
    single Lorentzian of FWHM gamma_nat + gamma_coll + sigma_laser.

    The assertion is on the half-maximum width, not on a pointwise difference
    against `lorentzian`. A pointwise comparison here is dominated by the
    finite grid's truncation of Lorentzian tails, which shifts the area
    normalisation by a few parts in a thousand and says nothing about whether
    the widths add. The width is the claim; the width is what is tested.
    """
    nu = np.linspace(-12.0, 12.0, 4801)
    prof = model_profile(nu, gamma_coll=GC, sigma_laser_fwhm=SL,
                         transit_fwhm=0.0, laser_kind="lorentzian")
    half = prof / prof.max() - 0.5
    left = nu[:len(nu) // 2][np.argmin(np.abs(half[:len(nu) // 2]))]
    right = nu[len(nu) // 2:][np.argmin(np.abs(half[len(nu) // 2:]))]
    got = right - left
    want = GAMMA_NAT_HZ / 1e6 + GC + SL
    assert abs(got - want) / want < 5e-3, (
        f"lorentzian branch FWHM {got:.4f} MHz, expected the summed width "
        f"{want:.4f} MHz: the laser width is not being added")


def test_the_split_is_unidentified_but_the_sum_is_not():
    """State the consequence the way a reader of the results needs it.

    Under a Lorentzian laser kernel a fit at one condition can measure the
    SUM and cannot measure either part. This pins that as a property of the
    forward model, which is why results/laser_kernel.csv's per-condition
    gamma_coll column is not a measurement under that kernel.
    """
    build = BUILDERS["composite_profile"]("lorentzian")
    base = _resample(build, GC, SL)
    same_sum = _resample(build, GC + D, SL - D)
    bigger_sum = _resample(build, GC + D, SL)
    assert np.array_equal(base, same_sum)
    rel = float(np.max(np.abs(bigger_sum - base)) / np.max(np.abs(base)))
    assert rel > 1e-3, "changing the SUM did not move the line either"
