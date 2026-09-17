"""The ramp's coded side and the adopted polarizability must agree.

WHY THIS FILE EXISTS, AND WHY IT IS THE SECOND TIME.

`DELTA_ALPHA_AU` is negative in this record. A level shifts by
`dE_i = -alpha_i E^2 / 4`, so a negative differential polarizability moves the
transition BLUE, and the signal-weighted ramp should carry its mass at positive
detuning. `lineshape.stark_ramp` puts its mass at NEGATIVE detuning, which is
the side implied by the cited `+1093` a.u. this record does not adopt.

**NO EXISTING GUARD COULD FIRE ON THAT, AND TWO OF THEM PIN OPPOSITE SIDES.**
`test_polarizability` asserts the differential is negative and calls it a blue
shift. `test_lineshape` asserts the ramp density is exactly zero above zero
detuning, which is red. Both are green in the same run, because
`stark_shift_S0_mhz` takes `abs(delta_alpha_au)` before anything numerical
happens and `stark_ramp` takes `s0` as a magnitude that never sees the sign.
Every bound in the record reads the magnitude, so nothing numerical moves and
nothing checkable objects.

That is the abs-hides-the-sign class, and this is its second recorded
instance. The first produced a cross-apparatus dispute in August 2026. After
the first, the population of guards able to catch it was empty. It still was
until this file.

WHAT THIS FILE DOES, AND WHAT IT DELIBERATELY DOES NOT DO.

It does NOT flip the kernel. Which of the two statements changes is the owner's
adjudication: either the adopted value is right and the kernel is red-sided in
error, or the kernel is right and two docstrings are. A silent reversal by the
author of the test would be the same move the `abs()` already made, performed
once more.

So the consistency assertion is marked `xfail(strict=True)`. While the two
disagree the suite records the disagreement and stays green. **The moment they
are made to agree the test XPASSES, and a strict xfail turns an unexpected pass
into a failure**, so the resolution cannot land unnoticed either. The state is
mechanised in both directions without the decision being taken.

WHAT WOULD SETTLE IT EXPERIMENTALLY: the fixed-lock pull test, which the record
names as the measurement of the sign. Set against a kernel pointing the wrong
way, that test would appear to confirm the value it was built to check, which
is why this matters beyond bookkeeping.
"""
from __future__ import annotations

import numpy as np

from rb5s6s.constants import DELTA_ALPHA_AU
from rb5s6s.lineshape import stark_ramp

_GRID = np.linspace(-2.0, 2.0, 401)


def _ramp_side() -> int:
    """+1 if the kernel carries its mass blue, -1 if red."""
    y = stark_ramp(_GRID, 1.0)
    return 1 if y[_GRID > 0].sum() > y[_GRID < 0].sum() else -1


def _polarizability_side() -> int:
    """+1 for a blue shift, from dE = -alpha E^2/4 and the adopted value."""
    return 1 if DELTA_ALPHA_AU < 0 else -1


def test_the_two_sides_are_each_well_defined():
    """Neither side is ambiguous, so a disagreement is real and not noise."""
    y = stark_ramp(_GRID, 1.0)
    blue, red = y[_GRID > 0].sum(), y[_GRID < 0].sum()
    assert min(blue, red) < 1e-6 * max(blue, red), (
        "the ramp is two-sided, so 'which side' has no answer and this "
        "guard's premise is wrong")
    assert DELTA_ALPHA_AU != 0.0


def test_the_ramp_side_matches_the_adopted_polarizability():
    """RESOLVED by the owner on 2026-09-17 (O27), in his words: use the SSOT of
    -1131.8 +- 5.9 a.u., sign included. A level shifts by dE = -alpha E^2 / 4, so a
    negative differential polarizability moves the transition BLUE, and the kernel
    was the statement that changed: `lineshape.stark_ramp` now carries its mass at
    positive detuning.

    This assertion was a STRICT xfail for as long as the two disagreed, which is why
    the resolution could not land quietly: the moment they were made to agree the
    xfail became an unexpected pass and the suite went red. It is a plain assertion
    now, and it is the guard that keeps them agreeing.
    """
    assert _ramp_side() == _polarizability_side(), (
        f"the adopted Delta_alpha = {DELTA_ALPHA_AU} a.u. implies a "
        f"{'blue' if _polarizability_side() > 0 else 'red'} shift, and "
        f"stark_ramp carries its mass on the "
        f"{'blue' if _ramp_side() > 0 else 'red'} side")


def test_both_halves_are_on_the_side_the_ruling_names():
    """Pins each half separately, so a change in either is visible here.

    The pair used to pin the DISAGREEMENT; it now pins the agreement, and it names
    both sides rather than only their equality, so a simultaneous flip of both --
    which the equality above would admit -- is refused.
    """
    assert _polarizability_side() == 1, "the adopted value no longer implies blue"
    assert _ramp_side() == 1, "the kernel is no longer blue-sided (O27)"
