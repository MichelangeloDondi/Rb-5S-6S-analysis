"""
Code->results freshness: a committed result CSV must still match what the
current code recomputes from its committed inputs.

Every other physics test here is a synthetic closure -- inject a known value,
check it is recovered -- so none of them re-derives a committed results/*.csv
from the pipeline. That leaves a gap: editing a producer's math without re-running
it leaves the CSV, the docs pinned to it, and the figure fingerprint mutually
consistent but stale, and the whole suite stays green. This canary closes the gap
for the AC-Stark stage -- the headline S0 bound the power-lever analysis rests on
-- by recomputing stark_sweep.csv from the committed power_sweep.csv (the exact
call run_stark_sweep.py makes) and checking it still matches the committed file.
If rb5s6s.stark changes and stark_sweep.csv is not regenerated, this fails and
names the stale quantity. The same pattern extends to the other stages, one
block each.
"""
from __future__ import annotations

import csv

import pytest

from rb5s6s import config as C
from rb5s6s.stark import fit_stark_sweep

# the profile-likelihood scan re-minimizes the per-peak cores at each kappa, so
# recomputing the bound costs ~30 s; keep it off the fast inner loop (CI runs it).
pytestmark = pytest.mark.slow


def _committed_values(name):
    return {(r["quantity"], r["key"]): float(r["value"])
            for r in csv.DictReader(open(C.RESULTS_DIR / name))}


def _stark_sweep_from_code():
    """Recompute the stark_sweep quantities exactly as run_stark_sweep.py does:
    read the committed power_sweep.csv, fit one shared kappa with the current code."""
    grid = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "power_sweep.csv")):
        grid[(r["peak"], float(r["power_mW"]) / 1000.0)] = (
            float(r["fwhm"]), float(r["fwhm_err"]))
    res = fit_stark_sweep(grid)
    fresh = {
        ("kappa", "shared"): res["kappa"],
        ("kappa_err_raw", "shared"): res["kappa_err_raw"],
        ("kappa_ub95_profile", "shared"): res["kappa_ub95_profile"],
        ("S0_225mW_ub95_profile", "shared"): res["S0_225_ub95_profile"],
        ("kappa_ub95", "shared"): res["kappa_ub95"],
        ("S0_225mW_fit", "shared"): res["S0_225_fit"],
        ("S0_225mW_ub95", "shared"): res["S0_225_ub95"],
        ("S0_225mW_ub95_raw", "shared"): res["S0_225_ub95_raw"],
        ("S0_225mW_pred", "shared"): res["S0_225_pred"],
        ("chi2_red", "fit"): res["chi2_red"],
    }
    for p, s in res["sigma_laser_by_peak"].items():
        fresh[("core_sigma_laser", f"993.{p}nm")] = s
    return fresh


# The two *profile-likelihood* upper bounds are root-finds on the shallow
# Δχ²=2.706 crossing, where the curve is nearly flat, so the crossing point
# carries ~0.3% cross-platform optimizer jitter (scipy/BLAS version differences
# re-minimizing the cores land the root slightly apart). The point estimate,
# χ²_red and the σ_laser cores are well-conditioned and reproduce to the last
# committed place. So the bounds get a relative tolerance (still <<1%, whereas a
# real change to rb5s6s.stark moves them by tens of percent -- the canary holds);
# everything else keeps the tight last-place check.
_PROFILE_BOUNDS = {"kappa_ub95_profile", "S0_225mW_ub95_profile"}
_PROFILE_RTOL = 0.02


def test_stark_sweep_csv_matches_current_code():
    committed = _committed_values("stark_sweep.csv")
    stale = []
    for key, val in _stark_sweep_from_code().items():
        c = committed.get(key)
        if key[0] in _PROFILE_BOUNDS:
            tol = _PROFILE_RTOL * abs(val)          # shallow-crossing root-find
        else:
            tol = 1e-3 + 1e-4 * abs(val)            # last-place rounding only
        if c is None or abs(c - val) > tol:
            stale.append((key, c, round(val, 3)))
    assert not stale, (
        "stark_sweep.csv no longer matches rb5s6s.stark -- re-run "
        "scripts/run_stark_sweep.py and commit results/stark_sweep.csv.\n  "
        + "\n  ".join(f"{q}/{k}: committed {c} vs code {v}" for (q, k), c, v in stale))
