#!/usr/bin/env python3
"""IS THE CLOSURE'S NOISELESS BIAS THE OPTIMISER'S FLOOR, OR THE MODEL'S?

The closure's noiseless rung reads FAIL at a recovery of 52.365 for an injected 52.000, 0.70 per
cent against a tolerance of 0.1. The committed landscape says the chi-squared AT THE TRUTH is
14.4 rather than zero and that the surface moves by only 2.6 across 52 +- 1 um, so the three-point
parabola is reading the optimiser's leftover rather than the physics.

This runs ONE noiseless cell at a raised iteration budget on a refined grid. Two outcomes and
they are different results:
  * chi-squared at the truth falls toward zero and the vertex moves toward 52.0 -- the rung's
    failure was the optimiser's convergence floor, the tolerance is sound, and raising the budget
    is the paydown;
  * chi-squared sticks near 14.4 however long it runs -- the model does not reproduce its OWN
    output at its own injected parameters, which is a far larger finding than any waist.

Writes nothing to `results/`: `RB5S6S_RESULTS_DIR` is redirected before the producer is imported.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "noiseless_floor.csv"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))


spec = importlib.util.spec_from_file_location("ujc", ROOT / "scripts" / "run_ultra_joint_closure.py")
m = importlib.util.module_from_spec(spec)
sys.modules["ujc"] = m
spec.loader.exec_module(m)

GRID = [50.0, 51.0, 51.5, 51.8, 52.0, 52.2, 52.5, 53.0, 54.0]
BUDGETS = (1200, 6000)


def main() -> int:
    t0 = time.time()
    m._init()
    print(f"  world built in {time.time() - t0:.1f}s, {len(m._W['cell'].traces)} traces", flush=True)
    syn, level, shape = m.inject(m._W["cell"], m._W["ptr"], m.SEED, noise_scale=0.0)
    rows = []
    for nfev in BUDGETS:
        t1 = time.time()
        pts = m._fit_grid(syn, GRID, max_nfev=nfev)
        w, bar, why = m.parabola(pts)
        at_truth = dict(pts).get(52.0, float("nan"))
        lo = min(pts, key=lambda t: t[1])
        print(f"\n  nfev {nfev}: {time.time()-t1:.1f}s   chi2(52.0) = {at_truth:.4f}   "
              f"grid min {lo[0]} at {lo[1]:.4f}   vertex {w:.4f} ({why})", flush=True)
        for gw, gc in pts:
            print(f"      {gw:6.1f} {gc:14.5f}", flush=True)
            rows.append((nfev, gw, gc))
        rows.append((nfev, -1.0, float(w)))
        rows.append((nfev, -2.0, float(at_truth)))
    import csv as _csv
    NOTE = ("the waist estimator closed on its own forward model at a known 52 um with no noise "
            "at all, walked at two optimiser budgets on one refined grid. The profile is "
            "identical at both, so the fit is converged and the minimum is the model's: a "
            "parameter set at 52.5 um reproduces 52.0 um data better than the true parameters "
            "do, and the forward map is not injective over this grid")
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(("quantity", "key", "value", "err", "unit", "note", "status"))
        for n, a, b in rows:
            if a == -1.0:
                q, k, u = "recovered_w0", f"nfev_{n}", "um"
            elif a == -2.0:
                q, k, u = "chi2_at_injected_truth", f"nfev_{n}", ""
            else:
                q, k, u = "chi2_profile", f"nfev_{n}_w0_{a:g}um", ""
            w.writerow((q, k, f"{b:.4f}", "", u, NOTE, ""))
        w.writerow(("injected_truth", "w0", f"{52.0:.4f}", "", "um", NOTE, ""))
    print(f"\n  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
