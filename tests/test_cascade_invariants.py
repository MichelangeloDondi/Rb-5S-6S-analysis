"""Invariants of the cascade population model, checked rather than assumed.

A branching calculator can be wrong in ways a literature comparison does not
catch: populations that do not sum to one, a negative population at large cycle
counts, a limit that does not reduce to the trivial answer. These are the
checks that catch that class, and they cost nothing to run.

The table in `rb5s6s.cascade` is the committed output of a manifold computation
that needs sympy. These tests do not need it: they check the DYNAMICS the table
feeds, which is where a coding error would live.
"""
from __future__ import annotations

import math

import pytest

from rb5s6s import cascade as C


PEAKS = sorted(C.BRANCHING_F)


@pytest.mark.parametrize("peak", PEAKS)
@pytest.mark.parametrize("cycles", [0.0, 0.5, 1.0, 3.0, 10.0, 100.0])
def test_populations_sum_to_one(peak, cycles):
    """The atom is somewhere. The most basic thing a population model can fail."""
    p = C.CascadePopulations(peak, cycles=cycles)
    assert math.isclose(p.total(), 1.0, rel_tol=0, abs_tol=1e-12)


@pytest.mark.parametrize("peak", PEAKS)
@pytest.mark.parametrize("cycles", [0.0, 1.0, 10.0, 1000.0])
def test_populations_are_non_negative(peak, cycles):
    p = C.CascadePopulations(peak, cycles=cycles)
    assert p.driven >= 0.0
    assert p.undriven >= 0.0


@pytest.mark.parametrize("peak", PEAKS)
def test_branching_is_a_probability(peak):
    assert 0.0 < C.BRANCHING_F[peak] < 1.0


def test_zero_cycles_is_the_identity():
    """No excitation, no depletion. The limit that must be exactly trivial."""
    for peak in PEAKS:
        assert C.surviving_fraction(C.BRANCHING_F[peak], 0.0) == 1.0
        assert C.amplitude_factor(peak, 0.0) == 1.0


def test_zero_excitation_probability_depletes_nothing():
    """The low-excitation limit: p_exc -> 0 leaves the driven level full."""
    for peak in PEAKS:
        assert math.isclose(
            C.surviving_fraction(C.BRANCHING_F[peak], cycles=50.0, p_exc=0.0),
            1.0, abs_tol=1e-12)


def test_depletion_is_monotone_in_cycles():
    """Without repumping the driven level only empties."""
    for peak in PEAKS:
        f = C.BRANCHING_F[peak]
        vals = [C.surviving_fraction(f, c) for c in (0.0, 1.0, 2.0, 5.0, 20.0)]
        assert all(a >= b for a, b in zip(vals, vals[1:])), vals


def test_unrepumped_steady_state_is_empty():
    """With no repumping, enough cycles pump the driven level out entirely."""
    for peak in PEAKS:
        assert C.surviving_fraction(C.BRANCHING_F[peak], cycles=5000.0) < 1e-6


def test_repumping_gives_a_nonzero_steady_state():
    """The hook works: with repumping the level relaxes to r/(f+r), not to zero."""
    f = C.BRANCHING_F["4121"]
    r = 0.10
    late = C.surviving_fraction(f, cycles=10000.0, repump_rate=r)
    assert math.isclose(late, r / (f + r), rel_tol=1e-6)


def test_isotope_assignment_matches_the_repository_line_table():
    """DRIVEN_F must agree with constants.PEAKS, the repository's one line
    table, rather than restating its own claim. The first version of this
    test asserted the module's own wrong table back at it, which is the
    written-from-the-same-misunderstanding failure lesson 195 describes, so
    the assertion now goes to the independent source."""
    from rb5s6s.constants import PEAKS as LINE_TABLE
    for peak in PEAKS:
        iso_num = LINE_TABLE[peak]["isotope"]
        assert C.DRIVEN_F[peak][0] == f"{iso_num}Rb", peak
        assert C.DRIVEN_F[peak][1] == LINE_TABLE[peak]["F"], peak


def test_amplitude_factor_lies_between_the_endpoints():
    """A transit average cannot be outside the range it averages over."""
    for peak in PEAKS:
        f = C.BRANCHING_F[peak]
        for cycles in (1.0, 4.0):
            end = C.surviving_fraction(f, cycles)
            avg = C.amplitude_factor(peak, cycles)
            assert end <= avg <= 1.0, (peak, cycles, end, avg)


def test_brightness_ordering_follows_branching_not_degeneracy():
    """The finding this module exists to express: the four lines' pumping
    losses order by their CASCADE BRANCHING, and that order is not the naive
    degeneracy weight. 4121 has the largest f and therefore depletes fastest."""
    order = sorted(PEAKS, key=lambda p: C.BRANCHING_F[p], reverse=True)
    assert order == ["4121", "4154", "4192", "4207"]
    losses = [1.0 - C.surviving_fraction(C.BRANCHING_F[p], 3.0) for p in order]
    assert all(a > b for a, b in zip(losses, losses[1:])), losses


def test_arguments_out_of_range_are_rejected():
    with pytest.raises(ValueError):
        C.surviving_fraction(1.5, 1.0)
    with pytest.raises(ValueError):
        C.surviving_fraction(0.3, -1.0)
    with pytest.raises(ValueError):
        C.surviving_fraction(0.3, 1.0, p_exc=2.0)
