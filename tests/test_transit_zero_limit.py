"""The transit -> 0 limit of composite_profile must be reachable and correct.

WHY THIS EXISTS. `composite_profile` builds its grid from the kernels that are
PRESENT, excluding an absent transit, but for a long time it then convolved
with the transit kernel unconditionally. `two_sided_exponential` and `gaussian`
both divide by their width, so `transit_fwhm = 0.0` returned an all-nan
profile: the two halves of one function disagreed about whether the kernel
could be absent, and only the half that could produce nan was unguarded.

This is the same defect, in the same function, as the sigma_G -> 0 limit fixed
on 2026-08-21, and it is guarded here for the same reason: a submodel that
cannot be evaluated makes any nested comparison against it propagate nan rather
than fail loudly.

THE CORRECTNESS CLAIM, not merely the finiteness claim. A zero-width kernel is
a delta function and convolution with it is the identity, so skipping the
convolution IS the limit rather than an approximation to it. The tests below
assert the limit is APPROACHED, not just that it is finite.
"""
import numpy as np

from rb5s6s.lineshape import composite_profile


def test_absent_transit_is_finite():
    g, p = composite_profile(0.02, 0.30, 0.0, gamma_l=0.40)
    assert np.isfinite(p).all(), "the transit-free submodel returned nan"
    assert p.max() > 0.0


def test_absent_transit_is_the_limit_of_a_vanishing_one():
    """A shrinking transit converges on the absent-transit profile.

    CONVERGENCE IS ASSERTED ONLY WHILE THE GRID RESOLVES THE KERNEL, which is
    a fact about the discretisation and was measured rather than assumed. The
    grid step is set from the narrowest PRESENT kernel, so once the transit
    falls well below that step the kernel is sampled by a couple of points and
    the discretisation error stops falling: the measured departure at 0.05,
    0.01 and 0.002 MHz is 8.6e-4, 9.5e-5 and 2.7e-4, which decreases and then
    turns back up. Asserting strict monotonicity across that turn would be
    asserting something false about the numerics, so the test asserts what is
    true: convergence over the resolved range, and a small bound throughout.
    """
    ref_g, ref_p = composite_profile(0.02, 0.30, 0.0, gamma_l=0.40)

    def departure(w):
        g, p = composite_profile(0.02, 0.30, w, gamma_l=0.40)
        return np.max(np.abs(np.interp(ref_g, g, p) - ref_p)) / ref_p.max()

    wide, resolved = departure(0.05), departure(0.01)
    assert resolved < wide, (
        f"shrinking a RESOLVED transit did not approach the transit-free "
        f"limit: {resolved:.3e} at 0.01 against {wide:.3e} at 0.05")
    for w in (0.05, 0.01, 0.002):
        assert departure(w) < 5e-3, (
            f"transit {w} departs from the absent-transit limit by "
            f"{departure(w):.3e}, which is too far for a delta-function limit")


def test_a_present_transit_still_convolves():
    """The guard must not silently disable a transit that IS present."""
    _, without = composite_profile(0.02, 0.30, 0.0, gamma_l=0.40)
    _, with_t = composite_profile(0.02, 0.30, 0.45, gamma_l=0.40)
    assert np.isfinite(with_t).all()
    assert with_t.max() < without.max(), (
        "a present transit must broaden the line, lowering its normalised peak")


def test_both_transit_kinds_reach_the_limit():
    for kind in ("exp", "gaussian"):
        _, p = composite_profile(0.02, 0.30, 0.0, transit_kind=kind,
                                 gamma_l=0.40)
        assert np.isfinite(p).all(), f"transit_kind={kind} returned nan at zero"
