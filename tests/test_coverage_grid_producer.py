"""The coverage grid's producer holds no retired literal, and pools deterministically.

WHY THIS EXISTS. `results/coverage_grid.csv` carries the coverage collapse the
analysis plan is built on, and until 2026-09-05 its producer typed a transit
width some 88 per cent above the one the record derives from the measured
waist. Nothing caught it: the file sits in `verify_results_fresh`'s EXPENSIVE
set, which the gate does not run, and a physics literal inside a producer is
invisible to the freshness check by construction -- that check proves a CSV
matches its producer, never that the producer matches the record.

A grep for `coverage_grid` across `tests/` returned nothing at all before this
file. These are cheap structural checks, not a re-run of the 46-minute grid.
"""
import importlib.util
import inspect
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "scripts" / "run_coverage_grid.py"


def _module():
    spec = importlib.util.spec_from_file_location("rcg", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_transit_is_derived_and_not_typed():
    """Fails if anyone restates the transit as a literal again."""
    m = _module()
    from rb5s6s import constants as K
    assert m.TRANSIT == pytest.approx(
        K.transit_fwhm_from_w0(K.W0_MEASURED_M, T_C=130.0)), (
        "the producer's transit no longer equals the record's own derivation")
    src = inspect.getsource(m).split("TRANSIT")[1][:120]
    assert "transit_fwhm_from_w0" in src, (
        "TRANSIT is not derived from constants; a typed literal is how the "
        "retired 1.8 survived every gate")


def test_the_widths_are_positive_and_ordered_as_the_record_has_them():
    m = _module()
    assert 0 < m.GAMMA < m.SIGMA, "collisional width should sit below the laser width"
    assert 0 < m.TRANSIT < m.SIGMA, "transit should sit below the laser width"


def test_the_worker_count_respects_the_standing_ceiling():
    """Eight of ten cores, so a gate and a session stay responsive beside it."""
    m = _module()
    assert m.WORKERS <= 8, f"WORKERS={m.WORKERS} exceeds the standing ceiling of 8"
