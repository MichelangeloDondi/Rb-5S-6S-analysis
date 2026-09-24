"""The focused waist is a function of the drive wavelength, and the ceilings
that forgot it.

Failure mode this module exists to catch: a quantity measured at one drive
wavelength carried to another as though the beam were unchanged. Register A136
records it reaching a design recommendation and A137 records it reaching a
committed CSV, where three drive-power ceilings were computed at the 993 nm
waist for rungs at 760 and 778 nm.
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from rb5s6s import constants as K
from rb5s6s.config import RESULTS_DIR as RESULTS

ROOT = Path(__file__).resolve().parents[1]

REF = K.W0_REFERENCE_LAMBDA_NM
DRIVES = (993.418, 778.104, 760.126)


# --------------------------------------------------------------------------
# positive cases
# --------------------------------------------------------------------------
@pytest.mark.parametrize("regime", ["aperture", "resonator"])
def test_the_reference_wavelength_returns_the_measured_waist(regime):
    """Both regimes are anchored on the same measurement, so neither may move
    it. A regime that rescaled its own anchor would be reporting a units bug
    as physics."""
    assert K.waist_at_drive(REF, input_beam=regime) == pytest.approx(
        K.W0_CENTRAL_M, rel=1e-12)


@pytest.mark.parametrize("regime", ["aperture", "resonator"])
def test_the_waist_rises_with_the_wavelength(regime):
    """Diffraction sets the sign: a longer drive focuses to a larger spot
    through the same lens. A sign error here would make the shorter rungs look
    weaker rather than stronger."""
    waists = [K.waist_at_drive(lam, input_beam=regime)
              for lam in sorted(DRIVES)]
    assert waists == sorted(waists)
    assert waists[0] < waists[-1]


def test_the_closed_form_is_reproduced_independently():
    """Recompute w0 = lambda f / (pi w_in) from the reference rather than
    calling the function again, so the test is evidence about the physics and
    not a restatement of the implementation."""
    w_in = REF * 1e-9 * K.DRIVE_LENS_F_M / (math.pi * K.W0_CENTRAL_M)
    for lam in DRIVES:
        f = K.drive_lens_focal_m(lam)
        expected = lam * 1e-9 * f / (math.pi * w_in)
        assert K.waist_at_drive(lam, input_beam="aperture") == pytest.approx(
            expected, rel=1e-9)


def test_the_two_regimes_bracket_and_the_aperture_branch_moves_further():
    """The record does not pin the input beam, so the pair is the result. The
    aperture branch carries the full wavelength and the resonator branch its
    root, so the first must always sit further from the anchor."""
    for lam in (760.126, 778.104):
        a = K.waist_at_drive(lam, input_beam="aperture")
        r = K.waist_at_drive(lam, input_beam="resonator")
        assert a < r < K.W0_CENTRAL_M
        assert abs(K.W0_CENTRAL_M - a) > abs(K.W0_CENTRAL_M - r)


def test_the_shift_gain_bracket_matches_the_register():
    """A137's table: the on-axis shift goes as 1/w0^2, so the 760 nm rung gains
    between 1.32 and 1.74 at equal power. Both ends are quoted in the register
    and in the degeneracy map, so both are frozen here."""
    lo = (K.W0_CENTRAL_M / K.waist_at_drive(760.126, input_beam="resonator")) ** 2
    hi = (K.W0_CENTRAL_M / K.waist_at_drive(760.126, input_beam="aperture")) ** 2
    assert lo == pytest.approx(1.328, abs=0.005)
    assert hi == pytest.approx(1.735, abs=0.005)


# --------------------------------------------------------------------------
# tolerance cases: the glass matters far less than the wavelength
# --------------------------------------------------------------------------
def _n_bk7(lam_nm: float) -> float:
    l2 = (lam_nm / 1e3) ** 2
    return math.sqrt(1.0
                     + 1.03961212 * l2 / (l2 - 0.00600069867)
                     + 0.231792344 * l2 / (l2 - 0.0200179144)
                     + 1.01046945 * l2 / (l2 - 103.560653))


def test_the_singlet_dispersion_is_insensitive_to_the_glass():
    """The record does not name L1's glass, only that it is plano-convex. If
    the choice moved the answer this function would need an apparatus item; it
    does not, and this is the probe that says so."""
    n_ref_bk7, n_bk7 = _n_bk7(REF), _n_bk7(760.126)
    f_bk7 = K.DRIVE_LENS_F_M * (n_ref_bk7 - 1.0) / (n_bk7 - 1.0)
    assert abs(f_bk7 - K.drive_lens_focal_m(760.126)) < 2e-5   # under 0.02 mm


def test_the_focal_shift_is_small_against_the_wavelength_factor():
    """Probe on both sides of the claim that dispersion is the small term: the
    focal length moves under one per cent while the waist moves by a quarter."""
    f_frac = abs(K.drive_lens_focal_m(760.126) / K.DRIVE_LENS_F_M - 1.0)
    w_frac = abs(K.waist_at_drive(760.126, input_beam="aperture")
                 / K.W0_CENTRAL_M - 1.0)
    assert f_frac < 0.01
    assert w_frac > 0.20


def test_an_achromat_holds_the_focal_length():
    """The alternative reading of the apparatus, computed and not argued."""
    assert K.drive_lens_focal_m(760.126, singlet=False) == K.DRIVE_LENS_F_M


# --------------------------------------------------------------------------
# negative cases
# --------------------------------------------------------------------------
def test_an_unnamed_input_beam_regime_is_refused():
    """A silent default would be the defect this module exists for: the caller
    must state which regime the number is quoted under.

    PROBED ON BOTH SIDES SINCE 2026-09-10. The first version tried only a
    MISNAMED regime and passed while the signature carried
    `input_beam = "aperture"`, so the OMITTED case, which is the one a stranger
    writes, went unchecked and the function did exactly the hiding its own
    docstring disclaimed."""
    with pytest.raises(ValueError, match="input_beam"):
        K.waist_at_drive(760.126, input_beam="fibre")
    with pytest.raises(TypeError):
        K.waist_at_drive(760.126)


@pytest.mark.parametrize("lam", [100.0, 8000.0])
def test_the_sellmeier_range_is_guarded(lam):
    """Outside the fit the form returns a number from the wrong side of a
    pole, which would come back as a plausible index rather than as an error."""
    with pytest.raises(ValueError, match="Sellmeier"):
        K.refractive_index_fused_silica(lam)


# --------------------------------------------------------------------------
# the guard for the defect itself
# --------------------------------------------------------------------------

# THE DRIVE-POWER CEILING TEST IS GONE WITH ITS SUBJECT (O32, 2026-09-18). It guarded
# `proj_light_shift_ceiling` and its achievable-waist sibling: that a common-waist ceiling was not
# the only row, and that the achievable-waist one sat below it away from the reference rung. A137's
# defect was real and the guard was right about it, but the construct it guarded is retracted -- this
# record models the light shift rather than capping the power at a tenth of a width -- so the rows it
# read no longer exist. The waist-against-polarizability lesson it carries survives in this module's
# other tests, which assert that a per-rung quantity is computed at that rung's own waist.

def test_the_producer_still_emits_a_waist_and_a_polarizability_per_rung():
    """RUNGS is consumed, and the two rows that ride on it reach the CSV.

    WHY THIS EXISTS (2026-09-18). Stripping the retracted light-shift ceiling (owner order O32)
    deleted the loop that emitted the ceiling rows, and `input_rung_delta_alpha` and
    `input_rung_waist_at_drive` were emitted from INSIDE it, so two row families that have nothing to
    do with a ceiling went with it and `RUNGS` was left consumed by nothing. Nothing failed. The loss
    surfaced only because `docs/FUTURE_TRANSITIONS_titsapph.md` happened to bind one of the values and
    `check_references` reported it DANGLING -- which is luck, not coverage: a row nothing quotes can be
    deleted in silence.

    This asserts the rows EXIST, one per rung, and that each waist is the reference waist scaled by the
    drive wavelength, so a future strip cannot take them quietly again.
    """
    import csv as _csv
    rows = [r for r in _csv.DictReader(open(RESULTS / "projections.csv"))]
    for quantity in ("input_rung_delta_alpha", "input_rung_waist_at_drive"):
        got = [r for r in rows if r["quantity"] == quantity]
        assert got, (
            f"{quantity} is absent from projections.csv. RUNGS is defined in run_projections.py and "
            "something has stopped consuming it; the rows are not a ceiling concept and do not leave "
            "with one.")
        assert len(got) == 3, f"{quantity}: {len(got)} rows against the three rungs"
    waists = {r["key"]: float(r["value"]) for r in rows
              if r["quantity"] == "input_rung_waist_at_drive"}
    ref = [k for k in waists if k.startswith("993")]
    assert ref, "no 993 nm rung among the waist rows"
    assert waists[ref[0]] == pytest.approx(K.W0_CENTRAL_M * 1e6, rel=1e-3), (
        "the 993 nm rung's drive waist should reproduce the measured waist")
    for key, value in waists.items():
        if key.startswith("993"):
            continue
        assert value < waists[ref[0]], (
            f"{key} drives at a shorter wavelength than 993 nm, so its waist must be smaller")
