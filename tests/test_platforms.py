"""The platform layer: guided lengths, detection modes, and the rate ceiling.

WHY EACH TEST EXISTS. The module was written on 2026-09-10 because every cold
or guided number in the record had been an extrapolation of a warm-cell world
builder. Three of its behaviours are easy to break silently and each has a
negative case here:

  * the guided branch, which must NOT consult the Rayleigh range;
  * the cascade dead-time ceiling, which must bind under strong driving and
    must not bind at the archive's own waist;
  * the temperature units, because `constants.transit_fwhm_from_w0` takes
    CELSIUS and reading it as kelvin silently returns a warm-cell transit
    width for a microkelvin sample. That error was made during the design of
    this very module and cost a whole wrong table, so it gets a test.
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import constants as C
from rb5s6s import platforms as PL
from rb5s6s import detection as D


def test_a_guided_mode_ignores_the_rayleigh_range():
    f = PL.PLATFORMS["hcpcf_warm"]
    assert PL.effective_length_m(f) == pytest.approx(f.length_m)
    # the negative half: z_R for this waist is far shorter, so a guided length
    # that happened to equal it would mean the branch never fired
    assert PL.rayleigh_range_m(f.w0_m) < f.length_m / 10.0


def test_a_free_beam_is_truncated_by_whichever_is_shortest():
    tight = PL.PLATFORMS["cell_130C_tight"]        # z_R = 0.81 mm < 50 mm cell
    assert PL.effective_length_m(tight) == pytest.approx(
        PL.rayleigh_range_m(tight.w0_m))
    mot = PL.PLATFORMS["mot"]                      # cloud 0.5 mm < z_R 0.81 mm
    assert PL.effective_length_m(mot) == pytest.approx(mot.length_m)


def test_the_guided_length_is_not_reachable_by_the_free_formula():
    """A fibre metres long must not be capped at its own z_R by a regression."""
    f = PL.PLATFORMS["hcpcf_warm"]
    free_would_give = min(PL.rayleigh_range_m(f.w0_m), f.length_m)
    assert PL.effective_length_m(f) > free_would_give * 10.0


def test_the_cascade_renormalises_the_saturation_and_lowers_every_rate():
    """The cascade is a saturation renormalisation, and both limits are pinned.

    **THIS TEST HAS NOW BEEN WRONG TWICE IN OPPOSITE DIRECTIONS, and the second
    form is why it is written like this.** The first required the ceiling to
    BIND, encoding the module's own error. The second required the rate to equal
    the uncapped one at a megawatt, which is satisfied by any code that never
    caps: with the cascade DELETED from the module entirely, all eleven tests in
    this file passed. A test that a term is absent is not a test of the term.

    So this one pins the two LIMITS of the three-level steady state, each
    computed from the constants and not from the code under test:

        weak drive   ->  Gamma_pop s / 2, the cascade invisible
        strong drive ->  1 / (2 tau_6S + <tau_5P>), BELOW the two-level ceiling

    Deleting the cascade fails the strong-drive limit by 30 per cent, which is
    the plant, and is stated in the commit message with it.

    **THE 5P LIFETIME IS THE BRANCHING-WEIGHTED ONE SINCE 2026-09-11.** The
    first form of this test wrote `TAU_5P12_S`, the same single lifetime the
    module used, so the test and the code shared one assumption and neither
    could see it. The weight comes from `detection.ir_branching_5p12`, computed
    from the package's own matrix elements, and the expected values here are
    built from the lifetimes and that branching rather than from the module
    under test.
    """
    tau5 = D.mean_5p_lifetime_s()
    b12 = D.ir_branching_5p12()
    assert tau5 == pytest.approx(b12 * C.TAU_5P12_S + (1 - b12) * C.TAU_5P32_S)
    assert C.TAU_5P32_S < tau5 < C.TAU_5P12_S, (
        "the weighted lifetime must lie between the two legs it averages")
    assert PL.CASCADE_DEAD_TIME_S == pytest.approx(C.TAU_6S_S + tau5)

    # the renormalisation factor, from the lifetimes alone
    factor = 1.0 + tau5 / (2.0 * C.TAU_6S_S)
    assert PL.cascade_saturation_factor() == pytest.approx(factor)

    # STRONG DRIVE. The ceiling is below the two-level one, which is the whole
    # sign of the correction: a cascade properly modelled lowers every rate.
    ceiling = 1.0 / (2.0 * C.TAU_6S_S + tau5)
    assert PL.cascade_ceiling_per_s() == pytest.approx(ceiling)
    assert ceiling < PL.GAMMA_POP_PER_S * 0.5, (
        "the three-level ceiling must lie BELOW the two-level one; if it does "
        "not, the saturation factor has lost the 5P leg")
    for name, p in PL.PLATFORMS.items():
        got = PL.excitation_rate_per_atom(1e9, p)
        assert got == pytest.approx(ceiling, rel=1e-6), (
            f"{name}: the strong-drive rate is {got:.4e} against the "
            f"three-level ceiling {ceiling:.4e}. Deleting the cascade gives "
            f"{PL.GAMMA_POP_PER_S * 0.5:.4e}, which is what this catches")

    # WEAK DRIVE. The cascade is invisible at first order in s, so the two
    # forms must agree there; this is the limit the renormalisation must not
    # break, and it is what the old two-level expression got right.
    for name, p in PL.PLATFORMS.items():
        tiny = 1e-12
        s_tiny = 2.0 * (PL.two_photon_rabi_hz(tiny, p.w0_m, 0.94)
                        / C.GAMMA_NAT_HZ) ** 2
        assert PL.excitation_rate_per_atom(tiny, p) == pytest.approx(
            PL.GAMMA_POP_PER_S * 0.5 * s_tiny, rel=1e-6), (
            f"{name}: the weak-drive limit lost its first-order form")


def test_every_cascade_leg_descends():
    """A decay leg whose upper level lies below its lower one is not a leg.

    The guard the 2026-09-11 correction owed: no test read the level ordering,
    and the right latency sat one line away in the docstring of the very
    constant the module imports.
    """
    e_6s = 2.0 / 993.4e-9 / 100.0          # cm^-1, two photons at the drive
    e_6p = 1.0 / 421.7e-9 / 100.0          # cm^-1, the 420 nm line from 5S
    assert e_6p > e_6s, "6P must lie above 6S for this test to mean anything"
    # 6P IS reached, by blackbody excitation, at 44.30 per second against a
    # decay rate of 2.194e7: a branch of 2.0e-6. Real and far too rare to set
    # a cycle time, which is the reason the leg is excluded.
    # READ FROM THE PRODUCER'S FILE, not typed (2026-09-11). The literal was
    # 44.2953 beside the constant, so a moved producer number could not fail
    # this test, which is the one thing it exists to do.
    import csv
    from rb5s6s import config as _CFG
    with (_CFG.RESULTS_DIR / "blackbody_channels.csv").open() as _fh:
        bbr_6s_to_6p_per_s = next(
            float(r["value"]) for r in csv.DictReader(_fh)
            if r.get("quantity") == "bbr_transfer" and r.get("key") == "6S_to_6P")
    branch = bbr_6s_to_6p_per_s / (1.0 / C.TAU_6S_S + bbr_6s_to_6p_per_s)
    assert branch < 1e-5, f"the 6P branch is {branch:.2e}, no longer negligible"
    # so the dead time may not carry a 6P lifetime
    assert PL.CASCADE_DEAD_TIME_S < (C.TAU_6S_S + C.TAU_5P12_S) * 1.01, (
        "the dead time carries a leg longer than 6S plus 5P, which on this "
        "transition can only be a level the atom never visits")


def test_the_excited_fraction_saturates_at_one_half_and_not_at_one():
    p = PL.PLATFORMS["cell_130C_tight"]
    assert PL.excited_fraction(1e6, p) < 0.5 + 1e-9
    assert PL.excited_fraction(1e6, p) > 0.49


def test_the_saturation_parameter_reproduces_the_published_value():
    """0.033 at the archive's waist, computed elsewhere by another route."""
    from rb5s6s.hyperpolarizability import two_photon_rabi_hz
    p = PL.PLATFORMS["cell_130C"]
    om = two_photon_rabi_hz(0.225, p.w0_m, 0.94)
    assert 2.0 * (om / C.GAMMA_NAT_HZ) ** 2 == pytest.approx(0.033, abs=0.003)


def test_transit_width_is_computed_in_celsius_not_kelvin():
    """The units trap, with a number that separates the two readings.

    A 150 microkelvin sample has a transit width of a few kilohertz. Reading
    its temperature as 150 kelvin instead returns hundreds of kilohertz, and
    reading it as 150 CELSIUS returns megahertz, so any of the three wrong
    conversions fails this by orders of magnitude.
    """
    mot = PL.PLATFORMS["mot"]
    assert mot.temperature_k == pytest.approx(150e-6)
    got = PL.transit_fwhm_mhz(mot)
    assert got < 0.01, f"transit {got} MHz is a warm-cell width, not a cold one"
    assert got > 1e-5


def test_absorption_and_fluorescence_are_different_observables():
    fib = PL.PLATFORMS["hcpcf_warm"]
    cell = PL.PLATFORMS["cell_130C"]
    a = PL.signal_and_noise(0.020, fib, 1.0)
    f = PL.signal_and_noise(0.225, cell, 1.0)
    assert 0.0 < a["absorbed_fraction"] < 1.0
    assert np.isnan(f["absorbed_fraction"])


def test_an_unknown_detection_mode_is_refused():
    bad = PL.Platform("x", "cell", 400.0, 1e13, 64e-6, 0.05, 1.0,
                      "telepathy", False)
    with pytest.raises(ValueError, match="detection"):
        PL.signal_and_noise(0.225, bad, 1.0)


def test_every_catalogued_platform_is_self_consistent():
    for key, p in PL.PLATFORMS.items():
        assert p.detection in ("fluorescence", "absorption"), key
        assert p.temperature_k > 0 and p.density_cm3 > 0, key
        assert 0.0 < p.duty_cycle <= 1.0, key
        assert PL.atoms_in_probe(p) > 0, key
        assert p.guided == (p.kind in ("hcpcf", "onf")), key


def test_the_profile_integral_is_not_the_on_axis_rate_times_a_cylinder():
    """The saturated rate must be integrated over the mode, not sampled on axis.

    FOUND BY A BOARD (2026-09-11, the physics seat), and it is the largest
    number this module ever got wrong. `two_photon_rabi_hz` takes the on-axis
    intensity, so `excitation_rate_per_atom` is the rate at the centre of the
    beam; the table multiplied it by every atom in `pi w0^2 L_eff`. Where the
    drive saturates that is not an approximation but a different quantity: at
    the tight-waist row the profile integral is five times larger, because the
    centre has stopped growing and the wings have not.

    Both limits here are ANALYTIC and neither is read from the module:

    * guided, weak drive: a Gaussian's `I^2` integrates to `pi w0^2 / 4` over an
      area `pi w0^2`, so the ratio to the conventional number is exactly 1/4;
    * free space, weak drive: the axial tail past the Rayleigh range that the
      `min(z_R, L)` truncation throws away brings it to `atan(L / 2 z_R) / 2`.

    FAILURE MODE GUARDED: a return to the on-axis convention, in either of the
    two functions, which is invisible in the weak rows and a factor of five at
    the row the campaign proposes.
    """
    import math

    tiny = 1e-9  # far below saturation everywhere
    for name, p in PL.PLATFORMS.items():
        prof = PL.events_per_s_profile(tiny, p)
        conv = PL.events_per_s_on_axis(tiny, p)
        if p.guided:
            want = 0.25
        else:
            # the conventional volume truncates at min(z_R, L), so the ratio
            # is z_R atan(L / 2 z_R) / (2 L_eff); where the cloud is shorter
            # than the Rayleigh range that is NOT atan(L/2z_R)/2, which is the
            # form this test first wrote and the trapped rows refused
            z_r = PL.rayleigh_range_m(p.w0_m)
            want = (z_r * math.atan(p.length_m / (2.0 * z_r))
                    / (2.0 * PL.effective_length_m(p)))
        assert prof / conv == pytest.approx(want, rel=2e-3), (
            f"{name}: weak-drive ratio {prof / conv:.4f} against the analytic "
            f"{want:.4f}; the profile integral has stopped being one")

    tight = PL.PLATFORMS["cell_130C_tight"]
    ratio = (PL.events_per_s_profile(0.225, tight)
             / PL.events_per_s_on_axis(0.225, tight))
    assert ratio > 4.0, (
        f"the saturated row's profile integral is only {ratio:.2f} times the "
        "on-axis convention; at a saturation parameter near eight it must be "
        "several, and a ratio near one means the on-axis rate came back")

    # AND THE CALLER USES IT. The first form of this test graded the two
    # helpers against each other and never asked which one `signal_and_noise`
    # calls, so reverting that ONE line passed all thirteen tests -- the
    # "widened pattern beside an unchanged caller" the rule file names, found
    # by running the plant rather than by reading it.
    for name, p in PL.PLATFORMS.items():
        out = PL.signal_and_noise(0.225, p, 1.0)
        assert out["events_per_s"] == pytest.approx(
            PL.events_per_s_profile(0.225, p), rel=1e-12), (
            f"{name}: signal_and_noise is not reporting the profile integral")


def test_every_fluorescence_row_carries_the_branch_it_collects():
    """795 nm is one leg of two, and the detected rate must say so.

    The docstring of `signal_and_noise` named the branching from the day it was
    written and the code never applied it, so every fluorescence SNR was high
    by `1/sqrt(0.341) = 1.71` where signal shot noise dominates (2026-09-11,
    the physics seat). The branching is not a literal here: it comes from
    `detection.ir_branching_5p12`, which computes it from the package's own
    matrix elements and reproduces the committed
    `results/trapping_channels.csv` cell.

    FAILURE MODE GUARDED: the factor dropped again, which raises every
    fluorescence SNR by 1.71 and is invisible in any comparison of one
    fluorescence row against another.
    """
    b12 = D.ir_branching_5p12()
    assert 0.3 < b12 < 0.4, f"the 5P1/2 branching reads {b12}, not near 0.341"
    seen = 0
    for name, p in PL.PLATFORMS.items():
        if p.detection != "fluorescence":
            continue
        seen += 1
        out = PL.signal_and_noise(1e-3, p, 1.0)
        # `detected` is a COUNT over the effective integration time, so the
        # duty cycle rides with it
        want = (out["events_per_s"] * b12 * p.collection_eff * p.detector_qe
                * 1.0 * p.duty_cycle)
        assert out["detected"] == pytest.approx(want, rel=1e-9), (
            f"{name}: the detected rate is not the events times the branching, "
            "the solid angle and the quantum efficiency")
    assert seen >= 3, (
        f"only {seen} fluorescence platforms found; this guard is grading an "
        "almost empty population")
