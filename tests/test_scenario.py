"""The scenario layer: presets load, spans stay spans, nonsense refuses.

The refusal tests are the point, per the plan's own clause: one deliberately
impossible configuration PER SCOPE, each rejected at load with an error
naming the field and citing the manual-anchored limit. A loader that
accepted a 100-megapoint Agilent record would forecast a campaign no bench
can run, and nothing downstream could tell.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rb5s6s import fibre
from rb5s6s.scenario import Acquisition, Span, load_scenario

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "examples" / "scenarios"
PRESETS = ("dataset_2025", "campaign_cell", "campaign_cell_onf")


@pytest.mark.parametrize("name", PRESETS)
def test_preset_loads_with_full_provenance(name):
    s = load_scenario(SCEN / f"{name}.toml")
    assert s.name == name
    for key in ("waist_um", "lock_drift_mhz_per_min", "acquisition"):
        assert key in s.provenance and len(s.provenance[key]) > 10


def test_the_waist_is_a_span_not_a_point():
    """The knife-edge is open; a preset that pins it has decided physics."""
    for name in ("dataset_2025", "campaign_cell"):
        s = load_scenario(SCEN / f"{name}.toml")
        assert s.waist_um.width > 0.0, f"{name} pins the open waist"


def test_the_repaired_lock_drift_is_spanned_from_zero():
    s = load_scenario(SCEN / "campaign_cell.toml")
    assert s.lock == "fixed"
    assert s.lock_drift_mhz_per_min.low == 0.0
    assert s.lock_drift_mhz_per_min.high == pytest.approx(0.04)


@pytest.mark.parametrize("key,points", [
    ("agilent_3054a", 100_000_000),     # 64k CSV-export cap on the bench
    ("lecroy_ws3104z", 100_000_000),    # 500,001 measured
    ("rtm3004", 100_000_001),           # 80 MSample listed in the manual
])
def test_an_impossible_record_length_refuses_per_scope(key, points):
    with pytest.raises(ValueError, match="exceed"):
        Acquisition(instrument=key, record_length=points).validated()


def test_an_unoffered_resolution_mode_refuses():
    with pytest.raises(ValueError, match="no resolution mode"):
        Acquisition(instrument="agilent_3054a",
                    resolution_mode="eres_3.0").validated()


def test_a_sample_rate_past_the_printed_ceiling_refuses():
    """The Keysight guide's Table 1 prints 4 GSa/s; 10 GSa/s cannot load."""
    with pytest.raises(ValueError, match="ceiling"):
        Acquisition(instrument="agilent_3054a",
                    sample_rate_hz=10e9).validated()


def test_an_unprinted_ceiling_is_unenforced_not_invented():
    """The held LeCroy manual prints no rate spec, so no refusal exists."""
    acq = Acquisition(instrument="lecroy_ws3104z",
                      sample_rate_hz=10e9).validated()
    assert acq.sample_rate_hz == 10e9


def test_a_preset_without_provenance_refuses(tmp_path):
    src = (SCEN / "dataset_2025.toml").read_text(encoding="utf-8")
    broken = src.replace('waist_um = "rb5s6s.constants', 'waist_um_x = "rb5s6s.constants')
    p = tmp_path / "broken.toml"
    p.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="no provenance for .*waist_um"):
        load_scenario(p)


def test_an_upside_down_span_refuses():
    with pytest.raises(ValueError, match="upside down"):
        Span(3.0, 1.0)


def test_the_onf_preset_reaches_the_solved_mode():
    """The fibre fields must feed fibre.py's own solver, not a stand-in."""
    s = load_scenario(SCEN / "campaign_cell_onf.toml")
    mode = fibre.solve_he11(s.fibre.diameter_nm, 993.4)
    assert mode.neff > 1.0, "the guided mode must be bound"
    assert s.fibre.atom_temperature_k < 1e-3, "cold atoms, not vapour"
