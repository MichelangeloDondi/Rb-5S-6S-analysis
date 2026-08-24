"""The digital twin: does it record what the instrument would record.

A twin earns its name by two properties. It must produce traces the REAL
analysis can consume and recover a known truth from, and it must carry the
instrument's own limits rather than an idealisation of them. Both are tested
here, and the platform distinction that motivated the redesign is tested
hardest, because it is the one a plausible-looking twin gets silently wrong.
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import instruments as inst, twin
from rb5s6s.linefit import fit_condition

LAW = dict(a=0.004, b=1.0e-3, c=0.0, lev_max=1.0, tau_int=1.0)
TRUTH = dict(gamma_coll_mhz=0.58, sigma_laser_mhz=1.56, transit_fwhm_mhz=0.96)


def test_the_twin_round_trips_through_the_real_fitter():
    """Generate from a known truth, fit with production code, recover it.

    This is the property that separates a twin from a plot: the estimator
    under test is the one the campaign uses, not a copy living beside it.
    """
    cell = twin.vapour_cell(130.0, **TRUTH)
    acq = twin.Acquisition(instrument="agilent_3054a", n_traces=5,
                           span_mhz=40.0, tau_int_samples=1.0)
    f, v, _ = twin.acquire(cell, acq, kind="one_peak", noise_law=LAW,
                           rng=np.random.default_rng(7))
    fit = fit_condition(f, v, T_C=130.0, law=LAW,
                        transit_fwhm=TRUTH["transit_fwhm_mhz"],
                        trim_tails=True, gamma_l=0.0, fit_gamma_l=False)
    assert fit["gamma_coll"] == pytest.approx(TRUTH["gamma_coll_mhz"], rel=0.20)
    assert fit["sigma_laser"] == pytest.approx(TRUTH["sigma_laser_mhz"], rel=0.20)


@pytest.mark.parametrize("key,kind", [
    ("agilent_3054a", "one_peak"),
    ("lecroy_ws3104z", "four_peak"),
    ("rtm3004", "four_peak"),
])
def test_each_instrument_records_at_its_own_depth_and_length(key, kind):
    cell = twin.vapour_cell(130.0, **TRUTH)
    acq = twin.Acquisition(instrument=key, n_traces=1, n_points=None)
    f, v, meta = twin.acquire(cell, acq, kind=kind, noise_law=LAW,
                              rng=np.random.default_rng(1))
    ins = inst.get(key)
    assert f[0].size == ins.default_points == meta["n_points"]
    assert meta["lsb_volts"] == pytest.approx(
        ins.lsb_volts(acq.full_scale_v), rel=1e-12)


def test_a_record_longer_than_the_instrument_allows_is_refused():
    """The failure mode is a design that cannot be run, passing in silence."""
    acq = twin.Acquisition(instrument="agilent_3054a", n_points=10_000_000)
    with pytest.raises(ValueError, match="stores at most"):
        acq.resolved()


def test_four_peak_traces_carry_all_four_lines_on_one_range():
    cell = twin.vapour_cell(130.0, **TRUTH)
    acq = twin.Acquisition(instrument="lecroy_ws3104z", n_traces=1,
                           n_points=200_000)
    f, v, meta = twin.acquire(cell, acq, kind="four_peak", noise_law=LAW,
                              rng=np.random.default_rng(3))
    pos = twin.line_positions_mhz()
    assert f[0].min() <= min(pos.values()) and f[0].max() >= max(pos.values())
    # each line shows as a local maximum well above the baseline
    for centre in pos.values():
        i = int(np.argmin(np.abs(f[0] - centre)))
        window = v[0][max(0, i - 200): i + 200]
        assert window.max() > 0.5 * v[0].max()


def test_the_enhanced_mode_correlates_neighbours_and_the_boxcar_does_not():
    """The two resolution mechanisms are not interchangeable, in code.

    Enhanced resolution is a moving average ACROSS stored samples, so it
    imposes correlation the analysis would later read as physics. High
    resolution is a disjoint boxcar and leaves neighbours independent. A twin
    that modelled both as "more bits" would hide the artefact class this
    record spent two days removing.
    """
    assert inst.get("lecroy_ws3104z").modes["eres_3.0"].correlates_neighbours
    assert not inst.get("agilent_3054a").modes["hires"].correlates_neighbours
    rng = np.random.default_rng(11)
    white = rng.standard_normal(4096)
    smoothed = inst.apply_resolution_mode(
        white, inst.get("lecroy_ws3104z").modes["eres_3.0"])
    boxcarred = inst.apply_resolution_mode(
        white, inst.get("agilent_3054a").modes["hires"])
    def lag1(x):
        x = x - x.mean()
        return float(np.corrcoef(x[:-1], x[1:])[0, 1])
    assert lag1(smoothed) > 0.5
    assert lag1(boxcarred) == pytest.approx(lag1(white), abs=1e-12)


def test_the_nanofibre_radiates_against_the_room_and_not_against_its_atoms():
    """The distinction the redesign exists for, asserted as an invariant.

    Nanofibre atoms are laser-cooled to microkelvin and sit microns from a
    fibre in a room-temperature laboratory. The blackbody shift they carry is
    the ROOM's, and evaluating it at the atomic temperature would zero a term
    that is the same size as the cell's. The test pins both halves: the
    radiation temperature is 300 K whatever the atoms do, and it does not
    move when the atom temperature does.
    """
    cold = twin.nanofibre(atom_temperature_uk=5.0)
    warm = twin.nanofibre(atom_temperature_uk=300.0)
    assert cold.radiation_temperature_k == twin.NANOFIBRE_RADIATION_K == 300.0
    assert warm.radiation_temperature_k == 300.0
    assert cold.blackbody_shift_mhz() == warm.blackbody_shift_mhz()
    assert cold.atom_temperature_k != warm.atom_temperature_k
    # and the cell's DOES follow its own temperature, which is the contrast
    assert (twin.vapour_cell(130.0).radiation_temperature_k
            > twin.vapour_cell(70.0).radiation_temperature_k)
    assert (twin.vapour_cell(130.0).blackbody_shift_mhz()
            > twin.nanofibre().blackbody_shift_mhz())


def test_sample_correlation_reduces_independent_information():
    """tau_int is carried, because a white twin overstates every trace."""
    cell = twin.vapour_cell(130.0, **TRUTH)
    out = {}
    for tau in (1.0, 10.0):
        acq = twin.Acquisition(instrument="agilent_3054a", n_traces=1,
                               tau_int_samples=tau, quantise=False)
        _, v, _ = twin.acquire(cell, acq, kind="one_peak", noise_law=LAW,
                               rng=np.random.default_rng(5))
        resid = v[0] - np.convolve(v[0], np.ones(51) / 51, mode="same")
        r = resid - resid.mean()
        out[tau] = float(np.corrcoef(r[:-1], r[1:])[0, 1])
    assert out[10.0] > out[1.0] + 0.2
