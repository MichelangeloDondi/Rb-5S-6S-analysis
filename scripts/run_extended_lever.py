"""What the 150 and 170 C blocks would buy the collisional bound, by simulation.

The self-broadening dossier's improved-bound level proposes extending the
temperature ladder to 150 and 170 C with an absorption channel measuring the
density. Its precision target was marked as requiring a calculation. This is
that calculation, the same construction as the committed coverage study
(`rb5s6s/coverage.py`) with the temperature grid as a parameter instead of a
module constant, so the production module is untouched and the committed
`results/coverage.csv` chain cannot be tripped.

CONSTRUCTION AND ASSUMPTIONS, stated so the numbers travel with them. The
simulated observable is the four-to-six-point width-versus-density line at
the archive's own error model: a between-block drift proxy of 0.12 MHz one
sigma and a within-block error of 0.05 MHz per condition, both UNCHANGED at
the new temperatures. That second assumption is optimistic by construction,
since blackbody redistribution and thermal gradients can only grow the block
scatter, and the dossier's kill criterion exists for exactly that case. The
reported numbers are therefore a FLOOR on the uncertainty and a CEILING on
the gain. Estimator: `rb5s6s.beta.collisional_slope`, the committed
model-independent construction. Reported per grid: the median 95 per cent
bound under a true beta of zero, and the minimum detectable beta at 50 and
95 per cent detection probability.

Diagnostic. Writes private/run_logs/extended_lever_<seed>.csv and prints the
summary. Nothing in results/ moves.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s.beta import collisional_slope          # noqa: E402
from rb5s6s.coverage import density_units          # noqa: E402

BLOCK_SIGMA = 0.12
SEM = 0.05
W0 = 4.8

GRIDS = {
    "committed 70-130": (70.0, 90.0, 110.0, 130.0),
    "extended to 150": (70.0, 90.0, 110.0, 130.0, 150.0),
    "extended to 170": (70.0, 90.0, 110.0, 130.0, 150.0, 170.0),
}


def study(temps, beta_true, n_trials, rng):
    N = np.array([density_units(t) for t in temps])
    E = np.full(len(temps), SEM)
    bounds, detected = [], 0
    for _ in range(n_trials):
        W = (W0 + beta_true * N
             + rng.normal(0.0, BLOCK_SIGMA, len(temps))
             + rng.normal(0.0, SEM, len(temps)))
        r = collisional_slope(N, W, E)
        bounds.append(float(r["bound95"]))
        if r["verdict"] == "MEASUREMENT":
            detected += 1
    return float(np.median(bounds)), detected / n_trials


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260818)
    a = ap.parse_args()
    rows = []
    for name, temps in GRIDS.items():
        rng = np.random.default_rng(a.seed)
        med_bound, _ = study(temps, 0.0, a.trials, rng)
        # detection curve for the MDE, same grid as the committed study
        grid = np.arange(0.0, 0.31, 0.02)
        det = []
        for bt in grid:
            rng2 = np.random.default_rng(a.seed + 1)
            _, d = study(temps, bt, max(a.trials // 4, 200), rng2)
            det.append(d)
        det = np.array(det)
        mde50 = float(np.interp(0.5, det, grid))
        mde95 = float(np.interp(0.95, det, grid))
        lever = density_units(temps[-1]) / density_units(temps[0])
        rows.append(dict(grid=name, npts=len(temps),
                         density_lever=round(lever, 1),
                         median_bound95_null=round(med_bound, 4),
                         mde_50=round(mde50, 4), mde_95=round(mde95, 4)))
    out = ROOT / "private/run_logs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"extended_lever_{a.seed}.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for r in rows:
        print(f"{r['grid']:18s} npts {r['npts']}  lever x{r['density_lever']:-7.1f}  "
              f"median null bound95 {r['median_bound95_null']:.4f}  "
              f"MDE(50%) {r['mde_50']:.4f}  MDE(95%) {r['mde_95']:.4f}")
    print(f"rows -> {path}")
    print("DIAGNOSTIC. Nothing in results/ moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
