"""The Hamilton-anchored 5D differential, which two producers now share.

Failure mode this module exists to catch: the routine was a private copy inside
`scripts/run_projections.py` until 2026-09-09, and a second producer wanted it.
A copy is what A76 already cost this record once, so it was promoted into the
package and this is the test that promotion owes.
"""
from __future__ import annotations

import math

import pytest

from rb5s6s import polarizability as pol


def test_it_vanishes_at_the_measured_magic_wavelength():
    """The construction's DEFINING property, and the one anchor it has.

    Hamilton's measured magic wavelength is where the differential crosses
    zero. The construction is built as the motion away from that crossing, so
    it must return exactly zero there or it is not that construction.
    """
    assert pol.delta_alpha_5d(pol.MAGIC_5S5D52_EXP_NM) == pytest.approx(0.0, abs=1e-9)


def test_the_drive_value_is_the_one_the_projections_producer_publishes():
    """The magnitude `results/projections.csv` carries for this rung.

    Pinned because the promotion moved the routine between files, and a
    promotion that changes a published number silently is the failure mode a
    move like this has.
    """
    lam = 2e7 / pol.E_5D52_CM
    assert abs(pol.delta_alpha_5d(lam)) == pytest.approx(28648.7, rel=1e-4)


def test_the_sign_is_opposite_to_the_6S_differential():
    """The 5D rung sits on the far side of its own pole from 5S, so its
    differential carries the opposite sign to 6S's. A sign flip here would
    invert every shift direction the transition ladder quotes."""
    lam = 2e7 / pol.E_5D52_CM
    assert pol.delta_alpha_5d(lam) * pol.delta_alpha(2e7 / pol.E_6S_CM) < 0.0


@pytest.mark.parametrize("lam", [778.1042e-9, 7.781e-7, 1.0])
def test_the_units_trap_is_inherited(lam):
    """It calls `alpha_5s`, which traps metres passed for nanometres.

    Probed on BOTH sides: values under the module's 50 nm trap raise, and the
    test below shows the routine answers normally just above it. The first
    draft of this test asserted a range guard the module does not have, and
    got two plausible numbers back at 200 and 5000 nm.
    """
    with pytest.raises(ValueError, match="NANOMETRES"):
        pol.delta_alpha_5d(lam)


def test_just_above_the_trap_it_answers():
    """The other side of the same probe, so the guard is shown to be a trap on
    a unit mistake and not a range restriction.

    THIS ASSERTED `f(60.0) == approx(f(60.0))` until 2026-09-10, a call
    compared with itself, which is true of any deterministic function and of a
    broken one. It is the class the previous commit had just removed from
    `test_ramp_threading`, reintroduced in a new file the same wave. What the
    probe means is that the trap has a boundary and that the routine answers on
    the far side of it. The trap admits 50.0 and refuses below, so both sides
    are probed one step apart and neither assertion is a tautology.
    """
    value = pol.delta_alpha_5d(60.0)
    assert math.isfinite(value), "just above the trap the routine must answer"
    assert abs(value) < 1e6
    assert math.isfinite(pol.delta_alpha_5d(50.0)), \
        "50.0 is inside the trap's admitted range and must answer"
    with pytest.raises(ValueError, match="NANOMETRES"):
        pol.delta_alpha_5d(49.0)


def test_it_moves_away_from_the_anchor_and_in_one_direction():
    """A tolerance probe on both sides: the differential is monotone in the
    1.9 nm between the magic wavelength and the drive, since one near-resonant
    pole dominates it there. A non-monotone answer means a second pole entered
    the window and the construction's cancellation argument has failed."""
    mag = pol.MAGIC_5S5D52_EXP_NM
    vals = [pol.delta_alpha_5d(mag + d) for d in (0.4, 0.8, 1.2, 1.6, 1.9)]
    assert all(b > a for a, b in zip(vals, vals[1:])) or \
           all(b < a for a, b in zip(vals, vals[1:]))
