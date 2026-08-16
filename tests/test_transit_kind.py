"""The transit_kind knob in linefit._shared_profile_grid, pinned both ways.

The knob existed in lineshape.composite_profile (the beta_self path) and was
promised for the production fits by that function's own docstring, but
linefit hardcoded the cusp until 2026-08-15, so the promised model-form check
could not run through the global fits at all (the near-miss register's
"a promise the code cannot keep").

Two properties matter and each is pinned in both directions:
  * the DEFAULT is byte-identical to the behaviour before the parameter
    existed, so no committed number can move by this edit;
  * the 'gaussian' branch actually changes the profile, so the knob is live
    rather than decorative.
"""
import numpy as np

from rb5s6s._compat import trapezoid
from rb5s6s.linefit import _shared_profile_grid


ARGS = dict(gamma_coll=0.58, sigma_laser=1.56, transit_fwhm=0.96, s0=0.0,
            laser_kind="gaussian")


def test_default_is_byte_identical_to_exp():
    g0, p0 = _shared_profile_grid(**ARGS)
    g1, p1 = _shared_profile_grid(**ARGS, transit_kind="exp")
    assert np.array_equal(g0, g1)
    assert np.array_equal(p0, p1), (
        "the default drifted from 'exp', so committed numbers can move")


def test_gaussian_branch_is_live_and_lowers_the_tails():
    g, pe = _shared_profile_grid(**ARGS, transit_kind="exp")
    g2, pg = _shared_profile_grid(**ARGS, transit_kind="gaussian")
    assert np.array_equal(g, g2)
    assert not np.array_equal(pe, pg), "the knob is decorative"
    # The two-sided exponential kernel carries HEAVIER tails than a Gaussian
    # of the same FWHM, so at equal area the exp composite has the LOWER peak
    # and fatter shoulders. (First written the other way round from kernel
    # intuition; the measured sigma_laser shift under the swap, 1.69 to 2.42,
    # says the gaussian composite is the narrower one, and it is.)
    assert pg.max() > pe.max()
    # and the redistribution is a few per cent of peak, not a rescaling
    assert 0.03 < (pg.max() - pe.max())/pe.max() < 0.20
    # both stay area-normalized
    for p_ in (pe, pg):
        assert abs(trapezoid(p_, g) - 1.0) < 1e-6


def test_shoulders_carry_the_difference():
    """The kernels differ in their TAILS, so the composites differ most in the
    shoulder region a few MHz out, while far inside the Lorentzian-dominated
    wing (but away from the grid boundary, where same-mode convolution bleeds)
    the two agree to a few per cent."""
    g, pe = _shared_profile_grid(**ARGS, transit_kind="exp")
    _, pg = _shared_profile_grid(**ARGS, transit_kind="gaussian")
    shoulder = (np.abs(g) > 2.0) & (np.abs(g) < 6.0)
    mid_wing = (np.abs(g) > 15.0) & (np.abs(g) < 25.0)
    d_sh = np.max(np.abs(pe[shoulder] - pg[shoulder]))/pe.max()
    d_mw = np.max(np.abs(pe[mid_wing] - pg[mid_wing]))/pe.max()
    assert d_sh > 3*d_mw, (pe.max(), d_sh, d_mw)
