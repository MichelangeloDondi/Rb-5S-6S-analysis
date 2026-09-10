"""The focused waist is a function of the drive wavelength, and the ceilings
that forgot it.

Failure mode this module exists to catch: a quantity measured at one drive
wavelength carried to another as though the beam were unchanged. Register A136
records it reaching a design recommendation and A137 records it reaching a
committed CSV, where three drive-power ceilings were computed at the 993 nm
waist for rungs at 760 and 778 nm.
"""
from __future__ import annotations

import csv
import re
import math
from pathlib import Path

import pytest

from rb5s6s import constants as K

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
        K.W0_MEASURED_M, rel=1e-12)


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
    w_in = REF * 1e-9 * K.DRIVE_LENS_F_M / (math.pi * K.W0_MEASURED_M)
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
        assert a < r < K.W0_MEASURED_M
        assert abs(K.W0_MEASURED_M - a) > abs(K.W0_MEASURED_M - r)


def test_the_shift_gain_bracket_matches_the_register():
    """A137's table: the on-axis shift goes as 1/w0^2, so the 760 nm rung gains
    between 1.32 and 1.74 at equal power. Both ends are quoted in the register
    and in the degeneracy map, so both are frozen here."""
    lo = (K.W0_MEASURED_M / K.waist_at_drive(760.126, input_beam="resonator")) ** 2
    hi = (K.W0_MEASURED_M / K.waist_at_drive(760.126, input_beam="aperture")) ** 2
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
                 / K.W0_MEASURED_M - 1.0)
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
def test_every_ceiling_row_names_the_waist_its_own_rung_can_reach():
    """A137. `run_projections.py` computed all three drive-power ceilings from
    `W0_MEASURED_M`, the 993 nm waist, while varying only the polarizability,
    so two of the three rows described a bench no single lens realises. The
    common-waist row is a legitimate comparison and stays; what this asserts is
    that it is not the only row, and that the achievable-waist ceiling sits
    below it on every rung away from the reference."""
    path = ROOT / "results" / "projections.csv"
    rows = [r for r in csv.DictReader(path.open())]
    common = {r["key"]: float(r["value"]) for r in rows
              if r["quantity"] == "proj_light_shift_ceiling"}
    own = {r["key"]: float(r["value"]) for r in rows
           if r["quantity"] == "proj_light_shift_ceiling_at_drive_waist"}
    assert common, "the producer emits no ceiling rows at all"
    assert set(own) == set(common), (
        "every common-waist ceiling needs the achievable-waist ceiling beside "
        f"it; missing {sorted(set(common) - set(own))}")
    moves = {k: abs(v / common[k] - 1.0) for k, v in own.items()}
    ref = next(k for k in moves if "993" in k)
    # The reference rung is not asserted equal: its label wavelength is 993.4
    # and its term-energy drive is 993.418, so the two ceilings differ by four
    # parts in a hundred thousand. What must hold is that this residual is
    # negligible against the effect the guard exists for, which is a factor of
    # a few on the other rungs.
    assert moves[ref] < 1e-3, (
        f"the reference rung moved by {moves[ref]:.2e}, which is too much to "
        "be the label-against-term-energy residual")
    for key, value in own.items():
        if key == ref:
            continue
        assert value < common[key], (
            f"{key}: the achievable waist is tighter than the reference "
            "one, so its ceiling must be lower")
        assert moves[key] > 100 * moves[ref], (
            f"{key}: the drive-waist correction is not distinguishable from "
            "the reference rung's rounding residual")
        # AND THE SIZE OF THE MOVE, not only its direction. Asserting only
        # `own < common` passes for ANY law in which the waist falls with the
        # wavelength, so it could not tell the aperture-limited w0 ~ lambda
        # from the resonator-mode w0 ~ sqrt(lambda), which differ by 14 per
        # cent on this ladder. The ceiling is a POWER, and a given shift is
        # reached at a power going as the waist squared, so the ratio is
        # pinned to (w0_drive / w0_ref)^2 and the guard now reads the same
        # function the producer calls.
        lam = float(re.match(r"\s*([0-9.]+)\s*nm", key).group(1))
        predicted = (K.waist_at_drive(lam, input_beam="aperture")
                     / K.W0_MEASURED_M) ** 2
        assert value / common[key] == pytest.approx(predicted, rel=2e-3), (
            f"{key}: the ceiling ratio is {value / common[key]:.4f} against "
            f"the aperture law's {predicted:.4f}. The resonator law would give "
            f"{(K.waist_at_drive(lam, input_beam='resonator') / K.W0_MEASURED_M) ** 2:.4f}, "
            "and this guard exists to tell them apart")
