"""The treatment matrix on the twin: the main aim's MLE across the observables, one treatment
per cell, the waist recovered against a known truth (O22; the plan's step 3, the order of 0d).

A CELL is (form, the laser-width treatment, the shift treatment, the waist treatment, the noise
level): the twin is injected at a known waist through the closure's own route (the archive's axes,
levels, per-condition laws and, at the archive's level, its residual shape), and the fit's
profile over the ansatz grid returns the waist, its bar and the three meters' disagreement when
they float. The primary matrix pins alpha and beta at theory (the 00:30 ruling) and runs the tied
forms first; the free arms are the second angle. Every cell is admitted by the size gate and
climbs the noise ladder on its own analysis id, coarse first (0d): worlds 0.1, 0.6, 1.5, 2.8 MHz
and the free fit; levels 0, 0.1, 1.0 of the law; the mixed form; tied/tied and free/free.

Cache class until the matrix wave lands its CSV.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]     # scripts/ -> the repository
sys.path.insert(0, str(ROOT))
from rb5s6s import ladder_gate  # noqa: E402
from rb5s6s.constants import W0_CENTRAL_M  # noqa: E402

_s = importlib.util.spec_from_file_location("closure_for_treatments", ROOT / "scripts" / "run_ultra_joint_closure.py")
CL = importlib.util.module_from_spec(_s); _s.loader.exec_module(CL)   # ladder-exempt: the injection's own source
UJ = CL.UJ

ANALYSIS_ID = "ultra_joint_treatments"
WORLDS = (0.1, 0.6, 1.5, 2.8)            # coarse first (owner 02:40); the free fit beside them
GRID = (41.0, 42.0, 44.0, 46.0, 48.0, 52.0, 56.0)   # the scan grid about the 40 to 45 um band, from the lowest waist whose kernel nodes all pass (38 um fails depleted_line_abs)


def _spec(form, w0, treat, truth_sigma=None):
    """The fit's spec for one treatment at one scanned waist. The world "truth" pins the laser
    widths at the injected values (the arithmetic rung: the recovery must be exact there); a
    number pins both sessions at that width (a world); "free" fits them."""
    kw = dict(beta_profile=False)                  # the log-determinant rides only at a noisy level (F7): set per rung below
    if treat["sigma_l"] == "truth":
        kw["fixed"] = dict(truth_sigma)
    elif treat["sigma_l"] != "free":
        kw["fixed"] = {"sigma_l_P": float(treat["sigma_l"]), "sigma_l_T": float(treat["sigma_l"])}
    if treat["s0"] == "free":
        kw["s0_free"] = True
    if treat["w0"] == "free":
        kw["w0_free"] = True
    if treat.get("free"):
        kw["free"] = tuple(treat["free"])
    return UJ._spec(form, w0, **kw)


def _fit_grid(traces, form, treat, grid, noise_scale, truth_sigma=None, noisy=True):
    out = []
    for w0 in grid:
        c = UJ.Cell(dict(_spec(form, w0, treat, truth_sigma), noise_scale=noise_scale, logdet=bool(noisy)), traces)
        best = None
        for p0 in c.starts():
            f = c.fit(list(p0)) if noisy else c.fit(list(p0), max_nfev=CL.NOISELESS_NFEV)
            if best is None or f["chi2"] < best["chi2"]:
                best = f
        out.append((float(w0), float(best["chi2"]), c.unpack(best["p"])))
    return out


def _cell(args):
    form, treat, truth, scale, r, pool = args
    if "real" not in CL._W:                      # the closure's worker state, which its own pool initialiser fills
        CL._W["real"] = CL._synthetic_source()
    cell, ptr = CL._truth(truth, True)
    src = None
    if pool and scale >= 1.0:
        z = np.load(pool); pools = {k: np.asarray(z[k], float) for k in z.files}
        def src(t, n, rng, _p=pools):
            key = f"cond_{t['peak']}_{t['T']:.0f}C_{1e3 * t['P_W']:.0f}mW"; p = _p.get(key, _p["shared"])
            nb = int(np.ceil(n / 16)); st = rng.integers(0, len(p) - 16, size=nb)
            o = np.concatenate([p[s:s + 16] for s in st])[:n]; return o / max(float(np.std(p)), 1e-300)
    syn, level, shape = CL.inject(cell, ptr, CL.SEED + 1 + r, noise_scale=scale, residual_source=src)
    # NOTHING BELOW THE BORE'S FLOOR (F291, V5.8c item iii; the sibling's own pattern at
    # `run_ultra_joint_closure.py:91`). The fine points are built as `truth + k/2`, so when the
    # truth moved off the typed 42.0 onto the SSOT constant the grid's low end walked to 40.38 um
    # -- below the 40.892 um this bore can produce -- and `aperture_onaxis_factor_actual` RAISED,
    # correctly. **A grid anchored on a value that moves, with a fixed offset, walks off a physical
    # edge the moment the anchor moves**, and nothing in the offset says where the edge is. Filter
    # against GRID[0], which is chosen above the floor, exactly as the closure does.
    grid = tuple(sorted({w for w in set(GRID) | {truth + k * 0.5 for k in range(-4, 5)}
                         if w >= GRID[0]}))
    d_truth = cell.unpack(ptr)
    truth_sigma = {k: float(v) for k, v in d_truth.items() if k.startswith("sigma_l")}
    pts = _fit_grid(syn, form, treat, grid, scale if scale > 0 else 1.0, truth_sigma, noisy=scale > 0)
    w, bar, why = CL.parabola([(a, b) for a, b, _ in pts])
    if scale <= 0.0:
        # THE NOISELESS RUNG READS THE GRID'S OWN ARGMIN, not the parabola's vertex (amendment A3, applied
        # to the closure on 2026-09-18 and owed here for the same reason: the one rung whose whole job is to
        # show the arithmetic is exact must not report a fitting artefact as a bias).
        #
        # MEASURED HERE RATHER THAN INHERITED (2026-09-19). A3's motivating asymmetry -- a factor 2.9
        # between the two sides at +-0.5 um, which pulled the closure's vertex to 42.4374 for a walk
        # bottoming ON the truth -- is the CLOSURE's profile and is NOT this producer's. On this grid and
        # this spec the walk is very nearly symmetric (1.2997 and 1.2312 at +-1 um at four conditions), so
        # the vertex sits 42.0385 and the repair moves the reading by 0.039 um at one condition and 0.039 at
        # four. It is worth making anyway, because it takes `max_abs_rel_error` from 9.2e-4 to exactly 0
        # against a tolerance of 1e-3, so the stage gate stops passing by a fifth of its margin; but the
        # number that motivated it belongs to the other producer and saying otherwise would be inheriting a
        # measurement instead of taking one. The parabola stays the diagnostic it already is at the noisy
        # rungs, where the bar is what it reads.
        w = float(min(pts, key=lambda q: q[1])[0])
    best = min(pts, key=lambda q: q[1])[2]
    meters = {k: float(best.get(k, float("nan"))) for k in ("w0_transit_rel", "w0_shift_rel", "w0_sat_rel")}
    return dict(form=form, treat=treat, truth=truth, scale=scale, real=r, w0=w, bar=bar, why=why, level=level, profile=[(a, b) for a, b, _ in pts],
                meters=meters, s0_scales={k: float(v) for k, v in best.items() if k.startswith("s0_scale_")})


NOTE = ("one treatment of the matrix at one truth and one noise level. The shift and the waist are tied "
        "through the exponent table and the theory constants are pinned, so the free set is the laser "
        "width per session with the Rabi scale and the Lorentzian floor. The bar is the parabola's "
        "delta-chi2 = 1 over the grid and the rows predate the whitening re-run of F36. A world's rail "
        "or its waist is the matrix's content, and no world is called believable before its "
        "per-condition decomposition (F37)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", default="mixed"); ap.add_argument("--truth", type=float, default=round(W0_CENTRAL_M * 1e6, 4))  # SSOT: the record's central waist
    ap.add_argument("--worlds", default=",".join(str(w) for w in WORLDS) + ",free")
    ap.add_argument("--s0", default="tied", choices=("tied", "free")); ap.add_argument("--w0", default="tied", choices=("tied", "free"))
    ap.add_argument("--noise", type=float, default=0.0); ap.add_argument("--reals", type=int, default=1)
    ap.add_argument("--conditions", default="all"); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--pool", default=None); ap.add_argument("--out", required=True)
    ap.add_argument("--reason", default="", help="the reading that licensed this stage (a refinement names it)")
    a = ap.parse_args(argv)
    if a.conditions != "all":
        os.environ["RB5S6S_CLOSURE_CONDITIONS"] = str(a.conditions)
    n_cond = len({(t["session"], t["peak"], round(t["P_W"], 4), t["T"]) for t in CL._synthetic_source()})
    worlds = [w for w in a.worlds.split(",") if w]
    treats = [dict(sigma_l=w, s0=a.s0, w0=a.w0) for w in worlds]
    # the laser-width worlds ride the size gate's "forms" axis (treatment arms) until the gate
    # gains an axis of its own; the growth rule per axis is what matters and it applies the same
    size = {"conditions": n_cond, "forms": len(treats), "truths": 1, "realisations": max(1, a.reals)}
    cells = n_cond * len(treats) * max(1, a.reals)
    stage = 0 if cells <= 1 else int(math.ceil(math.log(cells, 4) - 1e-9))
    adm = ladder_gate.launch(ANALYSIS_ID, stage, size, pool_speedup=max(1.0, a.workers), reason=a.reason)
    print(f"  size ladder: stage {stage} admitted {adm}", flush=True)
    t0 = time.time()
    jobs = [(a.form, tr, a.truth, a.noise, r, a.pool) for tr in treats for r in range(max(1, a.reals))]
    import concurrent.futures as cf
    res = []
    if a.workers > 1 and len(jobs) > 1:
        with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
            for fut in cf.as_completed([ex.submit(_cell, j) for j in jobs]):
                res.append(fut.result()); d = res[-1]
                print(f"  {d['form']} sigma_l={d['treat']['sigma_l']} s0={d['treat']['s0']} w0={d['treat']['w0']} x{d['scale']:g} r{d['real']}: "
                      f"w0 {d['w0']:.3f} +- {d['bar']:.3f} [{d['why']}] meters {d['meters']}", flush=True)
    else:
        for j in jobs:
            d = _cell(j); res.append(d)
            print(f"  {d['form']} sigma_l={d['treat']['sigma_l']} s0={d['treat']['s0']} w0={d['treat']['w0']} x{d['scale']:g} r{d['real']}: "
                  f"w0 {d['w0']:.3f} +- {d['bar']:.3f} [{d['why']}] meters {d['meters']}", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["form", "sigma_l", "s0", "w0_treatment", "truth_um", "noise_scale", "real", "w0_um", "bar_um", "verdict",
                    "w0_transit_rel", "w0_shift_rel", "w0_sat_rel", "n_conditions", "s0_scales", "profile",
                    "note", "status"])
        for d in sorted(res, key=lambda q: (str(q["treat"]["sigma_l"]), q["real"])):
            w.writerow([d["form"], d["treat"]["sigma_l"], d["treat"]["s0"], d["treat"]["w0"], d["truth"], d["scale"], d["real"],
                        f"{d['w0']:.4f}", f"{d['bar']:.4f}", d["why"], *[f"{d['meters'][k]:.4f}" for k in ("w0_transit_rel", "w0_shift_rel", "w0_sat_rel")],
                        n_cond, json.dumps(d["s0_scales"]), json.dumps(d.get("profile", [])), NOTE, "DIAGNOSTIC"])
    cost = time.time() - t0
    # THE STAGE'S EVIDENCE IS THE ARITHMETIC, read on the truth's own world (or the free fit when no
    # truth world ran); the other worlds' recoveries and rails are the matrix's CONTENT, the
    # trade rate and the ex-post believability the owner asked for, never a stage's pass or fail.
    # Coverage is evidence only where it can be read: eight or more realisations on the L.
    ref = [d for d in res if d["treat"]["sigma_l"] == "truth"] or [d for d in res if d["treat"]["sigma_l"] == "free"] or res
    worst = max(abs(d["w0"] - d["truth"]) / d["truth"] for d in ref if np.isfinite(d["w0"])) if any(np.isfinite(d["w0"]) for d in ref) else float("inf")
    ev = {"max_abs_rel_error": float(worst)} if (a.noise <= 0 or n_cond < 32 or a.reals < 8) else \
         {"coverage": float(np.mean([abs(d["w0"] - d["truth"]) <= d["bar"] for d in ref if np.isfinite(d["w0"])] or [0.0])), "nominal": 0.68}
    ladder_gate.size_rung(ANALYSIS_ID, stage, size, cost, ev)
    print(f"  wrote {a.out} ({len(res)} cells) in {cost:.0f} s; size stage {stage} recorded with {ev}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
