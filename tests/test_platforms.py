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


def test_the_cascade_ceiling_cannot_bind_because_the_cascade_is_short():
    """The ceiling exists and is unreachable, which is the corrected physics.

    THIS TEST ASSERTED THE OPPOSITE until 2026-09-11 and encoded the same
    error as the module: it required the ceiling to bind at the tight waist.
    The dead time was `TAU_6S + 120.7 ns + TAU_5P12`, a cascade "through 6P",
    and 6P lies 3581 cm^-1 ABOVE 6S, so it is not a decay route. The real
    cascade is 6S to 5P1/2 to 5S at 73.27 ns, whose reciprocal sits above the
    two-level steady state's own ceiling, so no platform at any power reaches
    it. A test that asserts a cap binds is not a check on the cap; it is a
    check that nobody shortens the dead time, which is exactly backwards.
    """
    assert PL.CASCADE_DEAD_TIME_S == pytest.approx(C.TAU_6S_S + C.TAU_5P12_S)
    ceiling = PL.cycle_limited_rate_per_s()
    # the two-level steady state can never exceed Gamma_pop / 2
    assert PL.GAMMA_POP_PER_S * 0.5 < ceiling, (
        "the cascade ceiling has fallen below the two-level ceiling, so it "
        "would bind; check the dead time's legs against the level ordering")
    for name in PL.PLATFORMS:
        p = PL.PLATFORMS[name]
        unc = PL.GAMMA_POP_PER_S * PL.excited_fraction(1e6, p)
        assert PL.excitation_rate_per_atom(1e6, p) == pytest.approx(unc), (
            f"{name}: the cap bound at a megawatt, which it cannot")


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
    bbr_6s_to_6p_per_s = 44.2953
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
