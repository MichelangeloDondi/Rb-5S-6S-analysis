"""M36: what an imperfect polarisation opens, and what it does not.

This file was missing until 2026-08-20. M36 shipped with its argument in a
docstring and no test, which is the gap rule 19.74 exists to close, and the
argument it shipped with turned out to have a leg missing.
"""

import math

import pytest

from rb5s6s.polarisation import (GF_S_HALF, doppler_photon_split_hz,
                                 rank_one_leak_rate, vector_ratio,
                                 vector_spread_mhz, zeeman_satellite_mhz)


def test_the_vector_ratio_is_small_and_comes_from_the_line_lists():
    """1.7 per cent at the drive wavelength. Small because the fine-structure
    doublet nearly cancels, which is why it needs computing rather than
    guessing."""
    assert vector_ratio(993.4) == pytest.approx(0.017363, rel=1e-3)
    assert 0.0 < vector_ratio(993.4) < 0.05


def test_the_vector_spread_is_linear_in_both_of_its_inputs():
    assert vector_spread_mhz(0.348, 1.0) == pytest.approx(0.006042, rel=1e-3)
    assert vector_spread_mhz(0.348, 0.0) == 0.0
    assert vector_spread_mhz(0.696, 1.0) == pytest.approx(
        2.0 * vector_spread_mhz(0.348, 1.0))


def test_the_single_atom_satellite_positions():
    """The Delta m_F = +-1 position, which the pair channel sits at twice."""
    assert zeeman_satellite_mhz("87Rb", 50.0) == pytest.approx(0.3499, abs=1e-3)
    assert zeeman_satellite_mhz("85Rb", 50.0) == pytest.approx(0.2333, abs=1e-3)
    assert GF_S_HALF["87Rb"] / GF_S_HALF["85Rb"] == pytest.approx(1.5)


def test_the_doppler_geometry_makes_the_two_photons_non_degenerate():
    """The energy factor rank 1 needs. The Doppler-free SUM is velocity-free,
    which is why the technique works, and the DIFFERENCE is not."""
    split = doppler_photon_split_hz(130.0, "87Rb")
    assert split / 1e6 == pytest.approx(395.0, abs=5.0)
    # the lighter isotope moves faster, so its split is the larger
    assert doppler_photon_split_hz(130.0, "85Rb") > split
    assert (doppler_photon_split_hz(130.0) / doppler_photon_split_hz(70.0)
            == pytest.approx(math.sqrt(403.15 / 343.15), rel=1e-9))


def test_rank_one_needs_both_factors_and_an_ideal_retro_closes_it():
    """Neither factor alone opens the channel. A perfect retro sets the
    polarisation factor to exactly zero whatever the atoms are doing, which
    is the leg the first version of the M36 docstring left out."""
    assert rank_one_leak_rate(0.0) == 0.0
    assert rank_one_leak_rate(5.0) == pytest.approx(2.1e-13, rel=0.1)
    r1, r5 = rank_one_leak_rate(1.0), rank_one_leak_rate(5.0)
    ratio = (math.sin(math.radians(5.0)) / math.sin(math.radians(1.0))) ** 2
    assert r5 / r1 == pytest.approx(ratio, rel=1e-9)


def test_the_rank_one_leak_stays_below_the_channels_already_dismissed():
    """The retraction's conclusion, as a guard. If a line list or the thermal
    model ever pushes this above the hyperfine route at a plausible mismatch,
    that is a result rather than a detail."""
    assert rank_one_leak_rate(10.0) < 1.2e-10


def test_the_doppler_split_beats_the_eom_sideband_split():
    """Why the docstring's original example was the wrong one to lead with:
    the geometry already supplies a larger split than the EOM would."""
    assert doppler_photon_split_hz(130.0) > 25e6 * 10


def test_the_hyperfine_mixing_amplitudes_are_computed_not_asserted():
    """1.1e-5, 6.0e-6 and 1.2e-10 lived in three files and were computed in
    none, held up by mutual citation, until 2026-08-20."""
    from rb5s6s.polarisation import hyperfine_mixing_rate
    r = hyperfine_mixing_rate()
    assert r["amplitudes"]["5P1/2"] == pytest.approx(1.08e-5, rel=0.03)
    assert r["amplitudes"]["5P3/2"] == pytest.approx(6.02e-6, rel=0.03)
    assert r["rate_dominant_leg"] == pytest.approx(1.17e-10, rel=0.05)
    assert r["rate"] == pytest.approx(1.53e-10, rel=0.05)


def test_the_mixing_rate_is_the_square_of_the_amplitude():
    from rb5s6s.polarisation import hyperfine_mixing_rate
    r = hyperfine_mixing_rate()
    assert r["rate_dominant_leg"] == pytest.approx(r["amplitudes"]["5P1/2"] ** 2)
    assert r["rate"] == pytest.approx(
        sum(a * a for a in r["amplitudes"].values()))
    assert r["rate"] > r["rate_dominant_leg"]


def test_the_mixing_follows_the_committed_detunings():
    """A line list that moves takes these numbers with it, which is the whole
    reason for computing rather than typing them."""
    from rb5s6s.polarisation import hyperfine_mixing_rate, HFS_SPLIT_5P_HZ
    from rb5s6s.polarizability import LINES_5S, E_6S_CM
    hw = E_6S_CM / 2.0
    expect = HFS_SPLIT_5P_HZ["5P1/2"] / ((LINES_5S[0][0] - hw) * 2.99792458e10)
    assert hyperfine_mixing_rate()["amplitudes"]["5P1/2"] == pytest.approx(expect)
