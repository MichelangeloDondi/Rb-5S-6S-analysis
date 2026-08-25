"""The package carries this record's polarizability, and the cited one stays named.

WHY THIS FILE EXISTS. Until 2026-08-24 `rb5s6s.__all__` exported two
things that name the same quantity by the same definition, alpha(6S) -
alpha(5S) at 993 nm, with OPPOSITE SIGNS: the constant carried Orson et
al. 2021's +1093 while the package's own model computed -1144.6. Nothing
was looking: every place the suite touched the constant divided by its
magnitude, so a sign could disagree with the package's own physics in
the open for a month.

The experimenter adjudicated it that night, on the evidence of
docs/THEORY_NOTE.md section 5 (the measured static polarizability, the
measured 5S tune-out wavelength, and the 6S lifetime that Orson's sign
would place about 210 sigma from its measured value). The package now
defaults to THIS RECORD'S value and keeps the cited one named beside it.

**That adjudication is a decision, not a measurement.** No experiment has
set the sign: Orson's own AC-Stark search was a null at 6 MHz resolution,
and the fixed-lock pull direction that would settle it has not been run.
This file therefore pins the STATE, not the truth: which value the
package hands out, that the cited alternative is still reachable by name,
and that the two continue to disagree exactly as section 5 describes. If
an experiment ever settles the sign, this file is what must be rewritten,
with the resolution stated rather than inferred from a changed number.
"""
from __future__ import annotations

import math

from rb5s6s import DELTA_ALPHA_AU, alpha_5s, alpha_6s, delta_alpha
from rb5s6s.constants import DELTA_ALPHA_AU_ORSON2021

LAM_NM = 993.4
OURS = -1145.0
CITED = 1093.0
DISPUTE_HOME = "docs/THEORY_NOTE.md"


def test_the_package_defaults_to_this_records_value():
    assert DELTA_ALPHA_AU == OURS, (
        f"DELTA_ALPHA_AU is no longer {OURS}, the value adopted on the "
        f"2026-08-24 adjudication and the one results/polarizability.csv "
        f"carries. A change here is a change of physics policy and belongs "
        f"in {DISPUTE_HOME} section 5 first.")
    assert math.isclose(DELTA_ALPHA_AU, delta_alpha(LAM_NM), rel_tol=2e-3), (
        "the constant and the model that reproduces it have come apart, "
        "which is the divergence this file was created to end")


def test_the_cited_value_is_still_reachable_by_name():
    assert DELTA_ALPHA_AU_ORSON2021 == CITED, (
        "the cited literature value moved or vanished. It is kept named so "
        "the comparison in section 5 stays runnable and so a reader meeting "
        "+1093 in the literature can find out here which value it is.")


def test_the_two_still_disagree_exactly_as_the_record_describes():
    """Opposite signs, magnitudes within about five per cent."""
    assert DELTA_ALPHA_AU * DELTA_ALPHA_AU_ORSON2021 < 0, (
        "the two values now agree in sign. If an experiment settled it, "
        "rewrite this file with the resolution and its evidence.")
    ratio = abs(DELTA_ALPHA_AU) / abs(DELTA_ALPHA_AU_ORSON2021)
    assert 0.95 < ratio < 1.06, (
        f"the magnitudes now differ by {abs(1 - ratio) * 100:.1f} per cent. "
        f"The argument that this is a SIGN disagreement rather than a "
        f"matrix-element one rests on them staying close, so a change here "
        f"changes the claim in {DISPUTE_HOME} section 5.")


def test_the_model_still_computes_its_own_definition():
    assert math.isclose(delta_alpha(LAM_NM),
                        alpha_6s(LAM_NM) - alpha_5s(LAM_NM), rel_tol=1e-9)


def test_the_shift_depth_is_a_magnitude_whatever_the_sign():
    """S0 is the ramp's depth, so it is non-negative under either value."""
    from rb5s6s.lineshape import stark_shift_S0_mhz
    ours = stark_shift_S0_mhz(0.225, 64e-6, rho=0.94)
    theirs = stark_shift_S0_mhz(0.225, 64e-6, rho=0.94,
                                delta_alpha_au=DELTA_ALPHA_AU_ORSON2021)
    assert ours > 0 and theirs > 0, (
        "stark_shift_S0_mhz returned a negative depth. Its consumers all "
        "assume S0 >= 0: the ramp runs on [-S0, 0] and every bound is "
        "one-sided positive. The shift's DIRECTION lives in the sign of "
        "Delta_alpha, not in this magnitude.")
    assert math.isclose(ours / theirs, abs(OURS / CITED), rel_tol=1e-6)
