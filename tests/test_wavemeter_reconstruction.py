"""M22 wavemeter reconstruction: the committed record, and the gate that chose
its model.

The 2025-06-11 record is fitted as a sawtooth (preregistration addendum 25): a
free level and a free ramp rate for each inter-lock interval, one shared finite
rise time for the step at each re-lock, no relaxation term, and a
three-parameter settling noise model. It replaced a shared-relaxation form on
2026-08-03 for reasons these tests keep enforced:

  * the residual must be white enough to quote from. The retired model sat at
    lag-1 autocorrelation 0.68 and a runs statistic of z = -6.3, so this
    checks the replacement stays far from both.
  * the optimum must not depend on where the search started. The retired
    model's best-of-20-restart likelihood moved by 19.8 across seeds, which is
    what the profiled likelihood removes. Three seeds must land on the same
    number.

The fit runs in about a second (the outer search covers four parameters, not
nineteen), so it is re-run here rather than trusted from the CSV, and the CSV
is checked against the fresh run.
"""

import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from rb5s6s import config as C  # noqa: E402
import run_wavemeter_reconstruction as W  # noqa: E402

CSV = C.RESULTS_DIR / "wavemeter_reconstruction.csv"

# Iterative fits do not converge bit-identically across numpy/scipy builds, and
# CI runs three. The committed CSV rounds to 2-4 decimals anyway, so compare
# against the rounding the file itself carries.
ATOL = {"settled_noise_floor": 5e-3, "noise_settling_time": 5e-3,
        "relock_rise_time": 5e-5, "pull_width": 5e-4, "residual_rms": 5e-4,
        "residual_acf1": 5e-4, "residual_runs_z": 5e-3, "nll": 5e-3,
        "ramp_rate_first_interval": 5e-3, "ramp_rate_last_interval": 5e-3}


def _rows():
    return list(csv.DictReader(open(CSV)))


def _val(quantity):
    for r in _rows():
        if r["quantity"] == quantity:
            return r["value"]
    raise KeyError(quantity)


_CACHE = {}


def _fresh():
    """One fit, shared by every test that only needs the default seed."""
    if "r" not in _CACHE:
        _CACHE["r"] = W.reconstruct()
    return _CACHE["r"]


# ---------------------------------------------------------------------------
# (a) the committed record reproduces
# ---------------------------------------------------------------------------

def test_csv_exists_and_is_tagged():
    assert CSV.exists(), "run scripts/run_wavemeter_reconstruction.py"
    assert all(r["status"] == "DIAGNOSTIC" for r in _rows()), (
        "this record is a photograph of a preliminary session, never an input "
        "to a fit")


def test_retired_quantities_are_gone():
    """The relaxation constant and the record-wide background were retired
    with the model, not merely re-fitted. The per-interval ramps absorb the
    background, so a drift and a curvature row would be double counting."""
    present = {r["quantity"] for r in _rows()}
    for gone in ("relaxation_tau", "background_drift", "background_curvature"):
        assert gone not in present, f"{gone} was retired by addendum 25"


def test_fresh_fit_reproduces_the_committed_csv():
    r = _fresh()
    fresh = {"record_length": r["record_min"], "scan_band_width": r["band_mhz"],
             "settled_noise_floor": r["sigma_inf"],
             "noise_settling_time": r["tau_sigma"],
             "n_relock_events": r["n_kicks"], "n_modelled_steps": r["n_steps"],
             "n_upward_relocks": r["n_up"], "n_downward_steps": r["n_down"],
             "n_null_events": r["n_null"], "relock_rise_time": r["rise_min"],
             "ramp_rate_first_interval": r["ramp_mhz_per_min"][0],
             "ramp_rate_last_interval": r["ramp_mhz_per_min"][-1],
             "pull_width": r["pull_width"], "residual_rms": r["resid_rms"],
             "residual_acf1": r["resid_acf1"],
             "residual_runs_z": r["resid_runs_z"], "nll": r["nll"]}
    committed = {r_["quantity"] for r_ in _rows()}
    assert committed == set(fresh), (
        f"the file and the fit disagree about which quantities exist: "
        f"{committed ^ set(fresh)}")
    for quantity, got in fresh.items():
        want = float(_val(quantity))
        tol = ATOL.get(quantity, 0.05)
        assert abs(want - got) <= tol, (
            f"{quantity}: file {want}, fresh fit {got} (tolerance {tol}). "
            "Re-run scripts/run_wavemeter_reconstruction.py")


def test_the_floor_is_where_the_documents_say_it_is():
    """APPARATUS section 6 and addendum 25 both quote 0.62 MHz. The floor is
    the only number this record publishes, so it is pinned here."""
    assert abs(float(_val("settled_noise_floor")) - 0.62) < 0.01


# ---------------------------------------------------------------------------
# (b) the optimum does not depend on the seed
# ---------------------------------------------------------------------------

def test_three_seeds_reach_the_same_optimum():
    t, f, _w, _a, _b = W.extract()
    tk = W.find_kicks(t, f)
    td, fd = t[::W.DECIMATE], f[::W.DECIMATE]
    nlls, floors = [], []
    for seed in (11, 22, 33):
        res, _mu, _sg, _r = W.fit(td, fd, tk, seed=seed)
        nlls.append(res["nll"])
        floors.append(res["sigma_inf"])
    assert max(nlls) - min(nlls) < 1e-6, (
        f"the profiled search is seed dependent: {nlls}. That is the defect "
        "which retired the model before this one")
    assert max(floors) - min(floors) < 1e-4, floors


# ---------------------------------------------------------------------------
# (c) the whiteness gate that chose this model
# ---------------------------------------------------------------------------

def test_residual_passes_the_whiteness_gate():
    r = _fresh()
    assert abs(r["resid_acf1"]) < 0.2, (
        f"lag-1 autocorrelation {r['resid_acf1']:.3f}. The retired relaxation "
        "model sat at 0.68 and that is what retired it")
    assert abs(r["resid_runs_z"]) < 2.5, (
        f"runs statistic z = {r['resid_runs_z']:.2f}. The retired model sat "
        "at -6.3")


def test_pull_width_is_unity_and_the_floor_beats_the_scatter():
    """The noise model is fitted, not chosen, so the pull width is the check
    that it is right. The floor must also sit at or below the record's own
    kick-free scatter of 0.55 MHz plus its residual spread."""
    r = _fresh()
    assert abs(r["pull_width"] - 1.0) < 0.02
    assert 0.3 < r["sigma_inf"] < r["resid_rms"] + 0.1


# ---------------------------------------------------------------------------
# (d) the census in the file is the census the fit returns
# ---------------------------------------------------------------------------

def test_event_census_matches_the_fit():
    r = _fresh()
    assert int(_val("n_relock_events")) == r["n_kicks"] == 12
    assert int(_val("n_modelled_steps")) == r["n_steps"]
    assert int(_val("n_upward_relocks")) == r["n_up"]
    assert int(_val("n_downward_steps")) == r["n_down"]
    assert int(_val("n_null_events")) == r["n_null"]


def test_the_census_partitions_the_testable_events():
    """12 detected kicks, but the first lands at 0.222 min, inside the opening
    0.4 min the likelihood excludes, so it has no fitted interval before it and
    11 steps are measurable."""
    r = _fresh()
    assert r["kick_times"][0] < W.EDGE_CUT_MIN < r["kick_times"][1]
    assert r["n_steps"] == r["n_kicks"] - 1 == len(r["steps"])
    assert r["n_up"] + r["n_down"] + r["n_null"] == r["n_steps"]
    up = [s["step_mhz"] for s in r["steps"] if s["step_mhz"] > W.STEP_MHZ]
    down = [s["step_mhz"] for s in r["steps"] if s["step_mhz"] < -W.STEP_MHZ]
    assert len(up) == r["n_up"] and len(down) == r["n_down"]
    assert min(up) > W.STEP_MHZ and max(up) < 40.0


def test_the_model_has_the_shape_addendum_25_describes():
    """A level and a ramp per fitted interval, one shared rise, three noise
    parameters, and no relaxation constant anywhere."""
    r = _fresh()
    k = r["n_kicks"]
    assert len(r["level_mhz"]) == len(r["ramp_mhz_per_min"]) == k
    assert r["n_par"] == 2 * k + 4 == 28
    assert W.RISE_BOUNDS_MIN[0] < r["rise_min"] < W.RISE_BOUNDS_MIN[1]
    # the ramps fall in magnitude across the record: the thermal settle the
    # retired model fitted with a single record-wide quadratic
    ramps = np.abs(r["ramp_mhz_per_min"])
    assert ramps[0] > 5.0 > ramps[-1]
    assert np.mean(ramps[:4]) > 3.0 * np.mean(ramps[-4:])
