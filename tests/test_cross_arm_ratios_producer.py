"""The cross-arm file carries every ratio with its bar and its three-waist
prediction, and the producer's estimator refuses what its two grids dispute.

FAILURE MODE IF THIS FILE IS DELETED: a ratio row could be without its block-scatter
bar or its predictions at 42, 56 and 85 um (`scripts/run_cross_arm_ratios.py`'s
WAISTS_UM, C6a) without anything noticing, the
isotope law could drift from the constants it must reproduce, the halved-grid
refusal could stop firing, and the model's power ratio could be without its
ordering in the waist (the P^2 terms go as w0^-4, so the 42 um prediction
sits highest), which is the whole reading the plan takes from it.
"""
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "cross_arm_ratios.csv"
PEAKS = ("4121", "4154", "4192", "4207")


def _rows():
    if not CSV.is_file():
        pytest.skip("results/cross_arm_ratios.csv not committed yet")
    return list(csv.DictReader(CSV.open(encoding="utf-8")))


def _producer():
    spec = importlib.util.spec_from_file_location("_xa", ROOT / "scripts" / "run_cross_arm_ratios.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_ratio_carries_its_bar_and_its_three_predictions():
    rows = _rows()
    for q in ("power_ratio_mu2", "temperature_difference_mu2", "window_ratio_mu2",
              "isotope_contrast_mu2", "F_contrast_mu2_87Rb", "F_contrast_mu2_85Rb"):
        per = [r for r in rows if r["quantity"] == q and not r["key"].startswith("pooled")]
        pooled = [r for r in rows if r["quantity"] == q and r["key"].startswith("pooled")]
        assert per and pooled, q
        for r in per + pooled:
            # a cell with fewer than two admitted traces is written EMPTY with
            # its reason, never as a bare value without a bar
            if not r["value"].strip():
                assert "fewer than two traces" in r["note"], f"{q} {r['key']}: empty without its reason"
                continue
            assert r["err"].strip(), f"{q} {r['key']}: errless"
            assert r["status"] == "DIAGNOSTIC"
        per = [r for r in per if r["value"].strip()]
        for r in per:
            assert all(f"{w:g} um" in r["note"] for w in (42, 56, 85)), f"{q} {r['key']}: a prediction is missing"
            assert "pulls" in r["note"], f"{q} {r['key']}: no pull"
    assert {r["key"] for r in rows if r["quantity"] == "power_ratio_mu2"} == set(PEAKS) | {"pooled"}


def test_the_model_power_ratio_falls_with_the_waist_and_exceeds_one():
    """The P^2 terms go as w0^-4, so the model's 225 over 25 mW ratio is above
    one and largest at the tightest waist. FAILS when the companion or the
    ramp stop reaching the prediction, or when the ordering flips."""
    rows = _rows()
    m = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "power_ratio_mu2_model"}
    assert set(m) == {"w42", "w56", "w85"}
    assert m["w42"] > m["w56"] > m["w85"] > 1.0, m


def test_the_isotope_law_is_the_root_of_the_mass_ratio_and_the_transit_widens_85():
    rows = _rows()
    law = next(r for r in rows if r["quantity"] == "isotope_law")
    assert abs(float(law["value"]) - (np.sqrt(K.M_RB87_KG / K.M_RB85_KG) - 1.0)) < 1e-5
    # every isotope prediction is positive: the lighter isotope is faster
    for r in rows:
        if r["quantity"] == "isotope_contrast_mu2" and not r["key"].startswith("pooled"):
            preds = [float(tok.split()[-1]) for tok in r["note"].split("changed: ")[1].split(". pulls")[0].split(", ")]
            assert len(preds) == 3 and all(p > 0 for p in preds), (r["key"], preds)
            assert preds[0] > preds[1] > preds[2], "the transit's share falls with the waist"


def test_every_mu2_cell_names_its_window_grid_check():
    rows = _rows()
    est = next(r for r in rows if r["quantity"] == "estimator")
    assert "refused beyond a relative disagreement" in est["note"]
    cells = [r for r in rows if r["quantity"].startswith("mu2_w")]
    assert len(cells) == 3 * 32, len(cells)
    assert all("refused" in r["note"] for r in cells)


def test_the_halved_grid_refusal_fires_on_a_planted_disagreement(monkeypatch):
    """Plant: with the tolerance forced to zero every reading that differs
    between the grids at all is refused, and with it restored the model's
    reading is admitted. FAILS when the check stops comparing the two grids."""
    xa = _producer()
    y = xa.full_profile(xa.MODEL_NU, gamma_coll=0.58, sigma_laser_fwhm=1.6, transit_fwhm=0.93)
    k, dis = xa.mu2_checked(xa.MODEL_NU, y, 6.0, 0.0)
    assert np.isfinite(k) and k > 0 and 0 <= dis < xa.GRID_TOL
    monkeypatch.setattr(xa, "GRID_TOL", 0.0)
    k0, dis0 = xa.mu2_checked(xa.MODEL_NU, y, 6.0, 0.0)
    assert not np.isfinite(k0) and dis0 > 0, "a nonzero disagreement passed a zero tolerance"


def test_a_window_seeded_beyond_the_trace_is_refused_not_clamped():
    xa = _producer()
    y = xa.full_profile(xa.MODEL_NU, gamma_coll=0.58, sigma_laser_fwhm=1.6, transit_fwhm=0.93)
    k, _ = xa.mu2_checked(xa.MODEL_NU, y, 6.0, 30.0)   # a strip would sit past the grid's edge
    assert not np.isfinite(k)


def test_the_model_mu2_scales_as_the_width_squared():
    """A profile stretched by a factor has a windowed mu2 that grows, and the
    isotope-only change moves it by under a per cent: the size the record
    quotes for a transit meter. FAILS when the transit stops reaching the
    model or the estimator stops reading the wider line as wider."""
    xa = _producer()
    a = xa.model_mu2(60.0, 130.0, 225.0, 0.58, 1.6, 87, "4121", (6.0,))[6.0]
    b = xa.model_mu2(60.0, 130.0, 225.0, 0.58, 1.6, 85, "4121", (6.0,))[6.0]
    wide = xa.model_mu2(60.0, 130.0, 225.0, 1.58, 1.6, 87, "4121", (6.0,))[6.0]
    assert 0 < (b - a) / a < 0.01
    assert wide > a


def test_a_task_is_bit_identical_on_a_second_run():
    """The producer's docstring claims a byte-identical CSV at every worker count,
    resting on _run_task carrying no random number; two serial runs of one
    condition's task must agree to the last bit, or the claim is unplanted."""
    # THE MIRROR HOLDS THE MANIFEST AND NOT THE TRACES (2026-09-14, the mirror's
    # stamp run): canonical_traces() returns rows there and _run_task fails on
    # the first file, so the plant skips on the directory and not on the loader.
    if not (ROOT / "data_raw" / "p_sweep").is_dir():
        pytest.skip("the raw traces are not in this checkout")
    mod = _producer()
    try:
        fits, traces, seeds = mod.conditions(), mod.canonical_traces(), mod.qc_peak_positions()
    except (FileNotFoundError, KeyError, SystemExit):
        pytest.skip("the canonical traces or the committed fits are not on this disk")
    keys = sorted(k for k in fits if k in traces)
    if not keys:
        pytest.skip("no condition carries both traces and a committed fit")
    k = keys[0]
    task = (k, fits[k], traces[k], {r["file"]: seeds[r["file"]] for r in traces[k]})
    flat = lambda x: json.dumps(x, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else repr(o))
    assert flat(mod._run_task(task)) == flat(mod._run_task(task)), "a second run of the same task moved a value"
