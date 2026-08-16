"""The wide-scan design calculation, pinned where it is load-bearing.

This is a DESIGN script and writes no committed number, so the tests here
guard the two things a reader would act on: the settings arithmetic, and the
detectability claim that justifies the block at all.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from rb5s6s import constants as K
from run_widescan_design import (REACH_IN_SIGMA, background_degeneracy_factor,
                                 committed, narrow_to_pedestal_area,
                                 pedestal_fwhm_mhz)

PED_SIGMA = 941.955 / 2.3548200450309493


def test_pedestal_width_is_the_committed_thermometer():
    """The block's whole value rests on this width being a temperature."""
    w = pedestal_fwhm_mhz(130.0)
    assert 900 < w < 990, w
    # results/projections.csv carries 941.955 for 85Rb at 130 C
    assert abs(w - 941.955) < 1.0
    # and it must go as sqrt(T), which is what makes it a thermometer
    r = pedestal_fwhm_mhz(130.0) / pedestal_fwhm_mhz(70.0)
    assert abs(r - math.sqrt(403.15 / 343.15)) < 1e-9


def test_the_span_requirement_beats_the_2025_span_by_a_large_factor():
    """If this ratio ever drops near one, the block has stopped being needed."""
    _, _, fwhm, rate = committed()
    span25 = K.TRACE_N_POINTS * K.TRACE_DT_S * 1e3 * rate
    span_needed = 2.0 * REACH_IN_SIGMA * pedestal_fwhm_mhz(130.0) / 2.3548200450309493
    assert span_needed / span25 > 20.0
    assert 2350 < span_needed < 2450


def test_a_2000_point_record_cannot_serve_both_requirements():
    """The finding that sizes the whole block: at the 2025 record length the
    span and the shape requirements are mutually exclusive."""
    _, _, fwhm, _ = committed()
    span = 2.0 * REACH_IN_SIGMA * pedestal_fwhm_mhz(130.0) / 2.3548200450309493
    pts_across_line = fwhm / (span / K.TRACE_N_POINTS)
    assert pts_across_line < 15, pts_across_line
    # and the record length that DOES serve both
    needed = span / (fwhm / 20)
    assert 8000 < needed < 9500, needed


def test_the_background_degeneracy_factor_is_computed_not_asserted():
    """THE DEFECT THIS PINS, which is a regression guard and not a record.

    The factor is a Fisher ratio for the amplitude against a free flat
    background. It is easy to substitute a plausible number reasoning from
    where the pedestal curve has fallen at the span edge, which answers a
    question about visibility rather than about information, and the two
    differ by a factor of five at one sigma of reach. The earlier assumption
    and what it cost are in docs/HISTORY.md.
    """
    f = background_degeneracy_factor
    # bounded, and monotone in reach: a wider span always breaks more degeneracy
    reaches = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
    vals = [f(r, PED_SIGMA) for r in reaches]
    assert all(0.0 <= v <= 1.0 for v in vals), vals
    assert all(a < b for a, b in zip(vals, vals[1:])), vals
    # the specific numbers that drove the design decision
    assert abs(f(1.0, PED_SIGMA) - 0.140) < 0.01, "one sigma of reach"
    assert abs(f(3.0, PED_SIGMA) - 0.645) < 0.01, "the chosen reach"
    # and at the 2025 span the pedestal is unmeasurable against a free background
    span25 = K.TRACE_N_POINTS * K.TRACE_DT_S * 1e3 * committed()[3]
    assert f(span25 / 2 / PED_SIGMA, PED_SIGMA) < 0.01


def test_retro_area_ratio_is_flat_near_unity():
    """The block register lists this as the entry's own empty case, so the
    weakness is pinned rather than discovered on the day."""
    f = narrow_to_pedestal_area
    assert abs(f(1.0) - 2.0) < 1e-12
    # derivative near rho = 1 is small, so rho is weakly constrained there
    d = (f(0.99) - f(1.0)) / 0.01
    assert abs(d) < 0.05


def test_pedestal_height_is_a_few_tenths_of_a_percent():
    """If this grew to per-cent level the pedestal would already be visible in
    the 2025 traces, and the 2026-08-15 analysis says it is not."""
    from rb5s6s.linefit import _shared_profile_grid
    from rb5s6s import config as C
    gc, sl, _, _ = committed()
    transit = K.transit_fwhm_from_w0(K.W0_MEASURED_M, 110.0)*math.sqrt(403.15/383.15)
    _, prof = _shared_profile_grid(gc, sl, transit, 0.0, "gaussian")
    sD = pedestal_fwhm_mhz(130.0)/2.3548200450309493
    frac = (1.0/(sD*math.sqrt(2*math.pi))/narrow_to_pedestal_area(C.RHO_RETRO))/prof.max()
    assert 0.002 < frac < 0.006, frac


def test_the_script_runs_and_writes_nothing(tmp_path, capsys):
    import run_widescan_design as W
    from rb5s6s import config as C
    before = sorted(p.name for p in C.RESULTS_DIR.glob("*"))
    assert W.main() == 0
    after = sorted(p.name for p in C.RESULTS_DIR.glob("*"))
    assert before == after, "a design script wrote into results/"
    out = capsys.readouterr().out
    for must in ("RECORD LENGTH", "PIEZO SHAPE", "GO / NO-GO", "sawtooth"):
        assert must in out
