#!/usr/bin/env python3
"""
The block bootstrap of the power-lever profile limit, per its
preregistration (docs/notes/s0_block_bootstrap_prereg.md, committed with
this script). The ledger's own text names the gap this fills: the
committed bound carries block-level over-dispersion as one global
threshold factor, and the block bootstrap is the sharper construction,
until now not run on the archive.

Construction (frozen in the prereg): stratified-by-peak resampling of
the committed 20-cell FWHM-vs-power grid, B = 1000, seed 20260807.
Primary estimator: the 95th percentile of the resampled kappa_hat
minimizers (rail-safe percentile bound). Secondary, diagnostic: raw
profile bounds at unscaled threshold 2.706 on the first B2 = 200
resamples. Output is DIAGNOSTIC until the prereg postscript
adjudicates: one row per resample to private/run_logs/, nothing into
results/.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _producer_lock import take_producer_lock     # noqa: E402
from rb5s6s import config as C  # noqa: E402
from rb5s6s.stark import fit_stark_sweep  # noqa: E402

B_PRIMARY = 1000
B_SECONDARY = 200
SEED = 20260807
POWER_225_W = 0.225


def load_grid() -> dict:
    grid = {}
    with open(C.RESULTS_DIR / "power_sweep.csv") as f:
        for r in csv.DictReader(f):
            grid[(r["peak"], float(r["power_mW"]) / 1000.0)] = (
                float(r["fwhm"]), float(r["fwhm_err"]))
    return grid


def committed_bound() -> float:
    with open(C.RESULTS_DIR / "stark_sweep.csv") as f:
        for r in csv.DictReader(f):
            if r.get("quantity") == "S0_225mW_ub95_profile":
                return float(r["value"])
    raise SystemExit("committed S0_225_ub95_profile not found in stark_sweep.csv")


def resample(grid: dict, rng: np.random.Generator) -> dict:
    """One stratified resample: per peak, five cells drawn with
    replacement from that peak's five power cells. The peak NAME is
    preserved so the fitter keeps its four per-peak nuisances (renaming
    duplicates would hand it twenty). A cell drawn twice enters twice
    via a microscopic relative power perturbation (1e-12 per draw
    index), which distinguishes the dict keys while leaving S0 = kappa*P
    numerically unchanged."""
    peaks = sorted({p for p, _ in grid})
    out = {}
    for pk in peaks:
        cells = [(P, v) for (p, P), v in grid.items() if p == pk]
        draws = rng.integers(0, len(cells), size=len(cells))
        for j, d in enumerate(draws):
            P, v = cells[d]
            out[(pk, P * (1.0 + 1e-12 * j))] = v
    return out


def main() -> int:
    take_producer_lock("run_s0_block_bootstrap")
    rng = np.random.default_rng(SEED)
    grid = load_grid()
    target = committed_bound()
    out_path = Path("private/run_logs/s0_block_bootstrap.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    rows = []
    n_fail = 0
    for b in range(B_PRIMARY):
        g = resample(grid, rng)
        want_profile = b < B_SECONDARY
        try:
            res = fit_stark_sweep(g, profile=want_profile)
        except Exception:
            n_fail += 1
            rows.append({"resample": b, "converged": 0, "kappa_hat": "",
                         "S0_225_fit": "", "S0_225_ub95_profile_raw": ""})
            continue
        rows.append({
            "resample": b,
            "converged": 1,
            "kappa_hat": f"{res['kappa']:.6f}",
            "S0_225_fit": f"{res['kappa'] * POWER_225_W:.6f}",
            "S0_225_ub95_profile_raw":
                (f"{res['S0_225_ub95_profile']:.6f}" if want_profile else ""),
        })
        if b == 19:
            per = (time.time() - t0) / 20.0
            proj_h = per * B_PRIMARY / 3600.0
            print(f"pilot: {per:.1f} s/resample, projected {proj_h:.1f} h "
                  f"(prereg stop condition at 12 h)", flush=True)
        if (b + 1) % 50 == 0:
            print(f"  {b + 1}/{B_PRIMARY} done, {n_fail} failed, "
                  f"{(time.time() - t0) / 60.0:.1f} min", flush=True)

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    ok = [r for r in rows if r["converged"] == 1]
    fail_frac = n_fail / B_PRIMARY
    s0_hats = np.array([float(r["S0_225_fit"]) for r in ok])
    railed = float(np.mean(s0_hats <= 1e-9))
    primary = float(np.percentile(s0_hats, 95))
    prof = np.array([float(r["S0_225_ub95_profile_raw"]) for r in ok[:B_SECONDARY]
                     if r["S0_225_ub95_profile_raw"] != ""])

    print("=" * 74)
    print("BLOCK BOOTSTRAP OF THE POWER-LEVER LIMIT (prereg: "
          "docs/notes/s0_block_bootstrap_prereg.md)")
    print(f"  resamples: {B_PRIMARY}, failed: {n_fail} "
          f"({100 * fail_frac:.1f}%, stop condition at 10%)")
    print(f"  railed at kappa=0: {100 * railed:.1f}% of converged resamples")
    print(f"  PRIMARY  percentile bound  S0(225 mW) 95th pct = {primary:.3f} MHz")
    if len(prof):
        print(f"  SECONDARY raw-profile bounds (B2={len(prof)}): "
              f"median {np.median(prof):.3f}, "
              f"IQR [{np.percentile(prof, 25):.3f}, {np.percentile(prof, 75):.3f}] MHz")
    print(f"  committed profile bound (comparison target) = {target:.3f} MHz")
    print(f"  P1 (primary <= committed): {'HOLDS' if primary <= target else 'FAILS -> P2 fires'}")
    print(f"  P3 (>=50% railed): {'HOLDS' if railed >= 0.5 else 'FAILS'}")
    print(f"  wrote {out_path} ({len(rows)} rows), DIAGNOSTIC standing")
    if fail_frac > 0.10:
        print("  STOP CONDITION FIRED: convergence failures exceed 10%, "
              "nothing is quotable from this run")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
