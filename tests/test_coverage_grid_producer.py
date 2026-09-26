"""The coverage grid's producer holds no retired literal, and pools deterministically.

WHY THIS EXISTS. `results/coverage_grid.csv` carries the coverage collapse the
analysis plan is built on, and until 2026-09-05 its producer typed a transit
width some 88 per cent above the one the record derives from the waist
convention. Nothing caught it: the file sits in `verify_results_fresh`'s EXPENSIVE
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
        K.transit_fwhm_from_w0(K.W0_CENTRAL_M, T_C=130.0)), (
        "the producer's transit no longer equals the record's own derivation")
    src = inspect.getsource(m).split("TRANSIT")[1][:120]
    assert "transit_fwhm_from_w0" in src, (
        "TRANSIT is not derived from constants; a typed literal is how the "
        "retired 1.8 survived every gate")


def test_the_widths_are_positive_and_ordered_as_the_record_has_them():
    """RE-ORDERED 2026-09-24. At the retired waist convention the transit (0.93 MHz at 130 C) sat
    below the laser width the fit returned; at the ruled 42.38 um it is 1.45 MHz, and the reference point's
    laser width is 0.47, because the transit took the width the laser kernel had carried (the tied
    sigma_laser(T) of results/global_fit.csv fell from 2.05, 2.15 and 1.54 to 0.64, 0.98 and 0.69 MHz).
    The ordering is asserted as the record now has it, so a waist move that flips it again fails here and
    is read rather than absorbed."""
    m = _module()
    assert 0 < m.GAMMA < m.SIGMA, "collisional width should sit below the laser width"
    assert 0 < m.SIGMA < m.TRANSIT, "at the ruled waist the transit sits above the laser width"


def test_the_worker_count_respects_the_standing_ceiling():
    """Eight of ten cores, so a gate and a session stay responsive beside it."""
    m = _module()
    assert m.WORKERS <= 8, f"WORKERS={m.WORKERS} exceeds the standing ceiling of 8"


def test_the_waves_combine_to_the_one_process_run_and_a_missing_slice_refuses(tmp_path, monkeypatch):
    """The configurations are the run's units (V7.2): slices dumped by `--from/--n/--dump` and assembled by
    `--combine` write the CSV the one-process run writes, and a combine missing a configuration refuses rather than
    writing a partial grid. The hits are a stub, so this plants the plumbing and not the physics, which each unit
    computes through the same `_unit_hits` either way."""
    m = _module()
    monkeypatch.setattr(m, "_unit_hits", lambda k: 900 + 7 * k)
    monkeypatch.setattr(m, "_init", lambda: None)
    monkeypatch.setattr(m, "_RESULTS_DIR", tmp_path)
    monkeypatch.setattr("sys.argv", ["x"])
    assert m.main() == 0
    whole = (tmp_path / "coverage_grid.csv").read_text(encoding="utf-8")
    (tmp_path / "coverage_grid.csv").unlink()
    dumps = tmp_path / "dumps"
    dumps.mkdir()
    n = len(m.CONFIGS)
    for i, (lo, k) in enumerate(((0, 3), (3, 5), (8, n))):
        monkeypatch.setattr("sys.argv", ["x", "--from", str(lo), "--n", str(k), "--dump",
                                         str(dumps / f"wave_{i:04d}.json")])
        assert m.main() == 0
    monkeypatch.setattr("sys.argv", ["x", "--combine", str(dumps)])
    assert m.main() == 0
    assert (tmp_path / "coverage_grid.csv").read_text(encoding="utf-8") == whole
    (dumps / "wave_0001.json").unlink()
    with pytest.raises(SystemExit, match="have no dump"):
        m.main()
