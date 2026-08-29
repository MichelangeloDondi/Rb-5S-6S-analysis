"""The HE11 mode solve: does it reproduce numbers it was not fitted to?

WHY THIS FILE EXISTS. Every evanescent quantity in this record used to derive
from `neff_band = 1.08 to 1.25`, tagged `assumed_parameter`. That band
corresponds at 993 nm to fibres of 485 to 796 nm diameter, while the fibres
this group runs are 350 to 400 nm, so the assumption did not contain the
apparatus. A mode is computable, so these tests hold the computation to
external evidence rather than to itself.
"""
from __future__ import annotations

import csv
import math
import pathlib

import pytest

from rb5s6s.fibre import (HE11Field, evanescent_intensity, n_silica_malitson,
                          solve_he11)
from rb5s6s.polarizability import E_6S_CM

_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _committed_row(quantity):
    """Read a row from the committed CSV, so no number is retyped here."""
    with open(_ROOT / "results" / "onf_candidate.csv") as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == quantity:
                return row
    raise AssertionError(f"no {quantity} row in results/onf_candidate.csv")

# Effective index for a 400 nm silica nanofibre at two standard wavelengths.
#
# THESE ARE NOT CITED TO A PAPER IN THIS TREE, and the comment here claimed
# they were until 2026-08-28. It read "from the published ONF trapping and
# spectroscopy work this record cites" and named no citekey; grepping the whole
# of docs/lit/ for these values returns nothing. It was found by a seat reading
# as an outside physicist would, and it matters because these two numbers are
# what anchors a brand-new solver to the outside world.
#
# WHAT THEY ARE, stated honestly until a citekey is added: values of this order
# are standard for this geometry and appear widely in the nanofibre literature,
# and the record holds no note quoting them. So this test is a sanity check
# against the accepted scale, NOT a validation against a named source. The
# independent evidence that does exist is a separately written solver, run to
# refute this one, which reproduced the module to 2e-16.
#
# Held to 1 per cent, which is far looser than the solver's own precision.
# OPEN ITEM: name the source, or retire the word "published" from every
# surface that describes this solver's validation.
LITERATURE_NEFF = [
    (400.0, 780.0, 1.10),
    (400.0, 852.0, 1.065),
]


@pytest.mark.parametrize("diameter_nm, lambda_nm, expected", LITERATURE_NEFF)
def test_neff_reproduces_the_standard_values(diameter_nm, lambda_nm, expected):
    mode = solve_he11(diameter_nm, lambda_nm)
    assert mode.neff == pytest.approx(expected, rel=0.01)


@pytest.mark.parametrize("diameter_nm", [350.0, 370.0, 400.0])
def test_the_groups_fibres_are_single_mode_at_the_probe(diameter_nm):
    """Every fibre this record contemplates guides HE11 alone at 993 nm."""
    mode = solve_he11(diameter_nm, 993.4181)
    assert mode.single_mode
    assert 1.0 < mode.neff < n_silica_malitson(993.4181)


def test_neff_rises_with_diameter_and_falls_with_wavelength():
    """Monotonicity, which no single point can check."""
    a = solve_he11(350.0, 993.4181).neff
    b = solve_he11(370.0, 993.4181).neff
    c = solve_he11(400.0, 993.4181).neff
    assert a < b < c
    assert solve_he11(400.0, 993.4181).neff < solve_he11(400.0, 780.0).neff


def test_thick_fibre_approaches_the_core_index():
    """The far limit, which pins the solver's other end."""
    assert solve_he11(4000.0, 993.4181).neff == pytest.approx(1.44, abs=0.02)


def test_the_two_decay_conventions_differ_by_exactly_two():
    """The factor this record currently mislabels, pinned so it cannot drift.

    `scripts/run_onf_candidate.py:_lambda_evanescent_nm` computes
    `lambda / (2 pi sqrt(neff^2 - 1))`, which is 1/q, the AMPLITUDE 1/e
    length, and its docstring calls it "1/e decay length of evanescent
    intensity". Intensity goes as exp(-2qr), so the intensity length is half
    of it. The mislabel feeds the effective mode area and therefore every
    intensity, S0 and rate this record quotes for a fibre.

    Written after a plant that did NOT fire: breaking the intensity length to
    equal the amplitude one left all ten other tests in this file green.
    """
    mode = solve_he11(370.0, 993.4181)
    assert mode.amplitude_decay_nm == pytest.approx(
        2.0 * mode.intensity_decay_nm, rel=1e-12)


def test_the_committed_decay_band_is_read_from_the_csv_not_hardcoded():
    """This test used to HARDCODE the band it checked, and went stale at once.

    It asserted the solved amplitude length falls outside 211 to 388 nm, which
    was the band the producer emitted when the band was an assumed index range.
    The producer now COMPUTES the band from the solve, so it reads 543 to 732
    and the solved 624 sits inside it, correctly. A test carrying a copy of the
    number it checks is measuring a historical value, not the current one.

    The live invariant is the one the original finding was about: the band and
    the value it is compared against must be on the SAME convention, amplitude
    against amplitude.
    """
    row = _committed_row("evanescent_decay_length")
    lo, hi = (float(x) for x in row["value"].split(" to "))
    solved = solve_he11(400.0, 2e7 / E_6S_CM).amplitude_decay_nm
    assert lo <= solved <= hi
    assert "AMPLITUDE" in row["note"]


def test_evanescent_intensity_is_not_the_exponential_where_the_atoms_are():
    """The factor is 2.4, and this test asserted 5 while the code said 6.

    Both numbers were wrong in the same way. `evanescent_intensity` evaluated
    K1(qr)^2, which is the E_z component alone, and its own docstring said so
    two paragraphs below the figure it quoted. The validated field solution
    gives 0.156 at the trap distance against the exponential's 0.369.

    So the assertion is now BRACKETED rather than one-sided: the exponential
    overstates, and the K1-only form understated by nearly as much again.
    """
    mode = solve_he11(370.0, 993.4181)
    exponential = math.exp(-400.0 / mode.intensity_decay_nm)
    true_profile = evanescent_intensity(400.0, 370.0, 993.4181)
    assert 2.0 < exponential / true_profile < 3.0
    assert 0.0 < true_profile < 1.0


def test_evanescent_intensity_agrees_with_the_validated_field_solution():
    """The function delegates, so this pins the delegation rather than a value."""
    fld = HE11Field(370.0, 993.4181)
    assert evanescent_intensity(400.0, 370.0, 993.4181) == pytest.approx(
        fld.intensity_at(400e-9), rel=1e-9)


# ---------------------------------------------------------------------------
# The HE11 field solution, guarded by the physics that found its defect.
#
# The first implementation of `HE11Field.H` used one `s` parameter in both
# regions. `test_hphi_is_continuous` fails on it at 53 per cent, which is how
# the defect was found AND located, since the ratio is exactly n1^2. Four
# computations of the mode area had disagreed by a factor of six before the
# fields were made to state their own correctness. Checked both ways:
# restoring the single `s` fails this test and the power-fraction test, and
# restoring the region-dependent one passes all of them.
# ---------------------------------------------------------------------------


def test_ez_is_continuous_across_the_glass_boundary():
    m = HE11Field(400.0, 993.4181)
    inside = m.E(m.a * (1 - 1e-9))[2]
    outside = m.E(m.a * (1 + 1e-9))[2]
    assert abs(inside - outside) / abs(inside) < 1e-6


def test_hphi_is_continuous_across_the_glass_boundary():
    """PLANT: one `s` for H in both regions fails this at rel 5.3e-01."""
    m = HE11Field(400.0, 993.4181)
    inside = m.H(m.a * (1 - 1e-9))[1]
    outside = m.H(m.a * (1 + 1e-9))[1]
    assert abs(inside - outside) / abs(inside) < 1e-6


def test_power_fraction_inside_the_glass_matches_an_independent_value():
    """23.3 per cent here against an independently computed 23."""
    m = HE11Field(400.0, 993.4181)
    total, inner, _ = m.power()
    assert 0.20 < inner / total < 0.26


def test_the_shell_approximation_is_refuted_by_the_field_solution():
    """The withdrawn shell gave 1.98 um^2. The fields give three times less."""
    m = HE11Field(400.0, 993.4181)
    assert m.effective_area_m2("azimuthal_mean") * 1e12 < 1.98 / 2.5


def test_the_peak_area_is_smaller_than_the_mean_area():
    """A_eff = P/I, so a PEAK intensity must give the SMALLER area.

    THIS TEST ASSERTED THE OPPOSITE UNTIL 2026-08-28 and passed, because the
    field components were swapped and `Sz(r, 0)` was returning the azimuthal
    MINIMUM. The check costs no solver and was available all night: a peak
    cannot be below the mean it is the peak of.
    """
    m = HE11Field(400.0, 993.4181)
    assert m.effective_area_m2("peak") < m.effective_area_m2("azimuthal_mean")


@pytest.mark.parametrize("d", [350.0, 370.0, 400.0])
def test_the_flux_peaks_on_the_polarisation_axis(d):
    """The discriminating check the boundary conditions could not make.

    E_z and H_phi continuity hold for BOTH the correct fields and the swapped
    ones, because H_r is continuous too when mu is uniform, so the validator
    that found the region-dependent s defect was blind to this one. The
    orientation of the intensity pattern is what tells them apart: for an
    x-polarised HE11 the flux must be largest ON the polarisation axis.
    """
    m = HE11Field(d, 993.4181)
    r = m.a * 1.000001
    azimuths = [i * math.pi / 180.0 for i in range(0, 181, 5)]
    fluxes = [m.Sz(r, p) for p in azimuths]
    assert azimuths[fluxes.index(max(fluxes))] == pytest.approx(0.0, abs=1e-9)
    assert m.Sz(r, 0.0) > m.Sz_azimuthal_mean(r)


def test_tangential_continuity_is_checked_AWAY_from_the_polarisation_axis():
    """E_phi carries sin(phi), so checking it at phi=0 measures nothing.

    The first validator did exactly that and reported a continuity error of
    identically zero, which reads as a perfect result and is an empty one.
    """
    m = HE11Field(400.0, 993.4181)
    phi = math.pi / 4
    inside, outside = m.E(m.a * (1 - 1e-9), phi), m.E(m.a * (1 + 1e-9), phi)
    assert abs(inside[1]) > 1e-12, "the check must not be evaluated where E_phi vanishes"
    assert abs(inside[1] - outside[1]) / abs(inside[1]) < 1e-6
    hin, hout = m.H(m.a * (1 - 1e-9), phi), m.H(m.a * (1 + 1e-9), phi)
    assert abs(hin[1]) > 1e-12
    assert abs(hin[1] - hout[1]) / abs(hin[1]) < 1e-6


# ---------------------------------------------------------------------------
# The guided transit kernel. A MODEL-FORM SWITCH, so every branch is exercised
# here -- this record has already paid once for a form parameter that was only
# ever called with its default (`laser_kind`, which moved the collisional
# coefficient by a median 45 per cent the first time it was thrown).
# ---------------------------------------------------------------------------


def test_every_transit_kernel_branch_is_reachable_and_ordered():
    from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR, transit_fwhm
    widths = {k: transit_fwhm(150e-6, 397e-9, kernel=k).fwhm_hz
              for k in TRANSIT_KERNEL_FACTOR}
    assert (widths["amplitude_lorentzian"] > widths["single_velocity"]
            > widths["ensemble_flux"] > widths["ensemble_speed"])


def test_the_squared_lorentzian_factor_is_the_analytic_one():
    """0.6436 is sqrt(sqrt(2)-1), not a fitted number.

    Setting (1+x^2)^2 = 2 with x = 2*pi*nu*tau gives the half width, and the
    full width in nu is then x/(pi*tau) against the unsquared Lorentzian's
    1/(pi*tau), so the ratio IS x.
    """
    from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR
    analytic = math.sqrt(math.sqrt(2.0) - 1.0)
    assert TRANSIT_KERNEL_FACTOR["single_velocity"] == pytest.approx(
        analytic, rel=1e-3)


def test_the_retired_transit_form_is_still_nameable_but_not_default():
    """The old v/(pi*Lambda) was the DEFAULT and overstated the width."""
    from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR, transit_fwhm
    assert TRANSIT_KERNEL_FACTOR["amplitude_lorentzian"] == 1.0
    default = transit_fwhm(150e-6, 397e-9).fwhm_hz
    retired = transit_fwhm(150e-6, 397e-9, kernel="amplitude_lorentzian").fwhm_hz
    assert retired / default > 2.0


def test_an_unknown_transit_kernel_is_refused():
    from rb5s6s.fibre import transit_fwhm
    with pytest.raises(ValueError, match="unknown transit kernel"):
        transit_fwhm(150e-6, 397e-9, kernel="lorentzian")


def test_an_ensemble_kernel_refuses_a_non_mean_velocity_convention():
    """The two switches interact and the combination double-counts.

    The ensemble factors were measured against the MEAN speed, so pairing one
    with convention='rms' applies sqrt(3*pi/8) twice. Found by the
    string-default switch audit on the night the kernel was added.
    """
    from rb5s6s.fibre import transit_fwhm
    with pytest.raises(ValueError, match="normalised to the MEAN speed"):
        transit_fwhm(150e-6, 397e-9, convention="rms", kernel="ensemble_flux")
    # a single-velocity kernel carries no such assumption
    assert transit_fwhm(150e-6, 397e-9, convention="rms",
                        kernel="single_velocity").fwhm_hz > 0


@pytest.mark.parametrize("weight,key",
                         [("flux", "ensemble_flux"), ("speed", "ensemble_speed")])
def test_the_cached_ensemble_factors_match_their_quadrature(weight, key):
    """The check whose absence let a wrong constant ship.

    `run_guided_mode_tables.py` claimed in its docstring that the ensemble
    averages were checked against a closed form by a test. They were not. The
    only test touching them compared the committed CSV cell against the same
    `TRANSIT_KERNEL_FACTOR` dict the producer had read it from, which is a
    self-comparison and cannot detect a wrong constant. Self-reference is not
    provenance.

    The unchecked constant was wrong: `ensemble_speed` read 0.245 against a
    true 0.2422, from a scratch integration that started at a lower velocity
    limit of 1e-3 m/s. The speed-weighted branch is dominated by slow atoms, so
    it is the branch a lower cutoff biases.
    """
    from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR, transit_kernel_factor
    assert transit_kernel_factor(weight) == pytest.approx(
        TRANSIT_KERNEL_FACTOR[key], abs=5e-4)


def test_the_speed_weighted_factor_is_not_cutoff_limited():
    """The specific failure: a lower integration limit biases this branch.

    Re-deriving with a deliberately truncated lower limit reproduces the
    retired 0.245, which is how the defect is known to be a cutoff artefact
    rather than a different convention.
    """
    from rb5s6s.fibre import transit_kernel_factor
    assert transit_kernel_factor("speed") == pytest.approx(0.2422, abs=5e-4)
    assert transit_kernel_factor("speed") < 0.245
