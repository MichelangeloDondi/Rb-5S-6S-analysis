"""The far-wing file carries every condition with its bar and its prediction,
and the producer's estimator reads a known line correctly.

FAILURE MODE IF THIS FILE IS DELETED: a far-wing cell could be without its noise
bar or its model prediction without anything noticing, the temperature-arm
lines could silently drop a peak or a law, the homogeneous-width inversion
could drift from the profile it inverts, and the window mask could admit a
side that reaches past the trace, which fills with the last sample and reads
as a pedestal.
"""
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "far_wing_level.csv"
PEAKS = ("4121", "4154", "4192", "4207")


def _rows():
    if not CSV.is_file():
        pytest.skip("results/far_wing_level.csv not committed yet")
    return list(csv.DictReader(CSV.open(encoding="utf-8")))


def _producer():
    spec = importlib.util.spec_from_file_location("_fw", ROOT / "scripts" / "run_far_wing_level.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_condition_carries_a_level_with_its_bar_and_its_predictions():
    rows = _rows()
    levels = [r for r in rows if r["quantity"] == "far_wing_level"]
    assert len(levels) == 32, f"{len(levels)} conditions, the L design has 32"
    for r in levels:
        assert r["err"].strip(), f"{r['key']}: a level without its bar"
        assert "composite predicts" in r["note"] and "Lorentzian" in r["note"], r["key"]
        assert r["status"] == "DIAGNOSTIC"
    for q in ("far_wing_asymmetry", "far_wing_pred_composite", "far_wing_pred_lorentzian",
              "far_wing_gamma_hom", "far_wing_gamma_excess"):
        keys = {r["key"] for r in rows if r["quantity"] == q}
        assert keys == {r["key"] for r in levels}, f"{q} does not cover every condition"


def test_the_composite_predicts_more_wing_than_its_bare_lorentzian():
    """The level is relative to the PEAK, and the Gaussian and cusp
    convolutions lower the peak while leaving the far wing untouched, so the
    composite's relative level sits above the bare Lorentzian's at every
    condition. A producer that normalised by area instead would invert this."""
    rows = _rows()
    comp = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "far_wing_pred_composite"}
    lor = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "far_wing_pred_lorentzian"}
    for k in comp:
        assert comp[k] > lor[k] > 0, (k, comp[k], lor[k])


def test_the_temperature_arm_is_fitted_under_every_law_per_peak_and_pooled():
    """The producer's `LAWS` tuple renamed "Steck" to "Nesmeyanov" (F259, O42, 2026-09-21): before
    the Alcock switch, "Steck" named the correlation the held Steck document then tabulated
    (Nesmeyanov's); the held Steck now adopts Alcock instead, so keeping the old label here would
    name the wrong law under an unchanged word. The rows and their physics are unchanged."""
    rows = _rows()
    for law in ("Nesmeyanov", "AIH", "SMI"):
        for peak in PEAKS:
            slope = [r for r in rows if r["quantity"] == "far_wing_level_slope" and r["key"] == f"{law}_{peak}"]
            assert slope, f"{law} {peak}: no level slope row"
        for q in ("far_wing_beta", "far_wing_level_slope"):
            for suffix in ("pooled", "pooled_shared"):
                r = [x for x in rows if x["quantity"] == q and x["key"] == f"{law}_{suffix}"]
                assert r and r[0]["err"].strip(), f"{q} {law}_{suffix}: missing or errless"
        floor = next(r for r in rows if r["quantity"] == "far_wing_floor" and r["key"] == f"{law}_pooled_shared")
        gamma0 = next(r for r in rows if r["quantity"] == "far_wing_gamma0" and r["key"] == f"{law}_pooled_shared")
        # the floor is gamma0 minus the natural width, in the same decimals
        assert abs(float(gamma0["value"]) - float(floor["value"]) - K.GAMMA_NAT_HZ / 1e6) < 0.01


def test_the_inversion_reproduces_the_profile_it_inverts():
    """Plant: the level the composite gives at a known collisional width,
    fed back through the table, returns that width to well inside the grid's
    quarter-MHz step. FAILS when the table's lower edge, its interpolation or
    its monotonicity check drift from the profile builder."""
    fw = _producer()
    transit = fw.transit_fwhm_at_T(130.0, fw._CFG.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    table = fw.gamma_hom_table(0.58, 1.6, transit)
    for gc in (0.10, 0.58, 2.0):
        g, prof = fw._shared_profile_grid(gc, 1.6, transit, 0.0, "gaussian", 0.0)
        level = 1e3 * fw.model_level(g, prof)
        h, err = fw.invert_gamma_hom(level, 0.1, table)
        assert abs(h - (fw.GNAT + gc)) < 0.02, (gc, h)
        assert err > 0
    # below the natural width nothing is invertible, and the producer says so rather than clamping
    h, _ = fw.invert_gamma_hom(0.5 * table[1][0], 0.1, table)
    assert not np.isfinite(h)


def test_the_window_mask_takes_both_sides_and_nothing_inside_fifteen():
    fw = _producer()
    d = np.linspace(-50.0, 50.0, 2001)
    both = fw.wing_mask(d, 0)
    assert both.sum() > 0 and np.all(np.abs(d[both]) >= 15.0) and np.all(np.abs(d[both]) <= 40.0)
    assert (fw.wing_mask(d, +1) | fw.wing_mask(d, -1)).sum() == both.sum()
    assert np.all(d[fw.wing_mask(d, +1)] > 0) and np.all(d[fw.wing_mask(d, -1)] < 0)


def test_the_level_of_a_synthetic_trace_reads_its_own_wing():
    """Plant: a noiseless trace built from the committed profile with a known
    amplitude, offset and slope, seeded a little off its centre, comes back
    with its far-wing level equal to the profile's own to a part in a
    thousand, and a re-solved centre within a hundredth of a MHz. FAILS when
    the linear solve, the centre scan or the peak normalisation drift."""
    fw = _producer()
    transit = fw.transit_fwhm_at_T(130.0, fw._CFG.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    g, prof = fw._shared_profile_grid(0.58, 1.6, transit, 0.0, "gaussian", 0.0)
    nu = np.arange(-1000, 1000) * 0.0425
    c_true, A, b0, b1 = 0.37, 3.0, 0.02, 1e-4
    v = A * np.interp(nu - c_true, g, prof, left=0.0, right=0.0) + b0 + b1 * nu
    law = {"a": 3e-3, "b": 1e-3, "c": 0.0}
    c, beta, cov, sig, chi2 = fw.solve_trace(nu, v, law, 2.0, g, prof, c_true + 0.4)
    assert abs(c - c_true) < 0.01
    assert abs(beta[0] - A) / A < 1e-3 and abs(beta[2] - b1) < 1e-5
    level, var, n = fw.wing_level(nu, v, sig, 2.0, c, beta, cov, float(prof.max()), 0)
    assert n > 500 and var > 0
    # a half-sample at the window's edge is a few parts in a thousand of the
    # level (the sample at 15 MHz carries four times the mean), and the planted
    # centre sits off the grid by a fraction of a step, so the bar is 5e-3
    assert abs(level - fw.model_level(g, prof)) < 5e-3 * fw.model_level(g, prof)


def test_the_weighted_line_recovers_a_planted_slope():
    fw = _producer()
    x = np.array([0.56, 2.45, 9.10, 29.4])
    y = 4.0 + 0.0075 * x
    a, b, ea, eb, chi2, dof = fw.weighted_line(x, y, np.full(4, 0.05))
    assert abs(a - 4.0) < 1e-9 and abs(b - 0.0075) < 1e-9 and chi2 < 1e-12 and dof == 2
    slope, es, ints, chi2s, dofs = fw.shared_slope_line([(x, y, np.full(4, 0.05)), (x, y + 1.0, np.full(4, 0.05))])
    assert abs(slope - 0.0075) < 1e-9 and abs(ints[1] - ints[0] - 1.0) < 1e-9 and dofs == 5


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
