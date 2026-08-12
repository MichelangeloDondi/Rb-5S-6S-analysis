#!/usr/bin/env python3
"""Does the parallel profile2d path give exactly the sequential answers?

This is the acceptance gate for RB5S6S_WORKERS, run on a deliberately small
grid so it finishes in minutes rather than hours: two kappas, two betas, the
full residual over the whole trace assembly, a reduced nfev. The comparison is
EXACT EQUALITY of every chi-squared, not a tolerance, because the parallel
path runs the same solver on the same inputs from the same starting points and
has no licence to differ: the benchmark that motivated it measured a maximum
absolute difference of 0.00e+00 across ten production-sized rows.

Exact equality is the right bar here and a tolerance would be a smell. If this
ever fails, the two paths have diverged in what they FIT, most likely because
main()'s trace assembly changed and _load_everything() did not follow, which
is the one seam this construction has.

Prints PASS or the first differing cell, exits nonzero on any difference.
Writes nothing. The full-scale acceptance (reproducing the committed
results/global_archive_fit.csv end to end with workers on) is a separate,
deliberate run recorded in its own right, not this smoke.

    ./.venv/bin/python scripts/_m25_parallel_smoke.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import run_global_archive_fit as G  # noqa: E402

KAPPAS = (0.0, 0.5)
BETAS = (0.005, 0.035)
NFEV = 120


def main() -> int:
    if not (G.PREHISTORY.is_dir() and G.PILOT.is_dir()):
        print("quarantine trees absent: this smoke needs the full assembly.")
        return 0

    t0 = time.time()
    resid, Sf, lo, hi = G._load_everything()
    q0 = np.asarray(G.build_q0_for_smoke() if hasattr(G, "build_q0_for_smoke")
                    else G.build(G_traces())[0][1:], float)
    print(f"assembly {time.time()-t0:.0f} s, {q0.size} free parameters")

    # sequential, through the production function with workers forced off
    os.environ["RB5S6S_WORKERS"] = "0"
    t0 = time.time()
    seq = {}
    for kap in KAPPAS:
        seq.update(G._p2d_row((kap, BETAS, q0, NFEV)))
    t_seq = time.time() - t0

    # parallel, two workers
    import multiprocessing as mp
    jobs = [(kap, BETAS, q0.copy(), NFEV) for kap in KAPPAS]
    t0 = time.time()
    with mp.get_context("spawn").Pool(2, initializer=G._init_worker) as pool:
        rows = pool.map(G._p2d_row, jobs)
    par = {}
    for r in rows:
        par.update(r)
    t_par = time.time() - t0

    bad = [(k, seq[k], par[k]) for k in seq if seq[k] != par[k]]
    print(f"sequential {t_seq:.0f} s, parallel {t_par:.0f} s")
    if bad:
        for k, a, b in bad:
            print(f"DIFFERS at {k}: sequential {a!r} parallel {b!r}")
        return 1
    print(f"PASS: all {len(seq)} cells exactly equal")
    return 0


def G_traces():
    camp = G.load_campaign_all()
    reh, _ = G.load_rehearsal()
    _, prates = G.load_t_rates()
    pil = G.load_pilot(prates["4192"][0])
    rul = G.load_rulers_t() if G.USE_RULERS else []
    for t in reh:
        t["T"] = 130.0
        t["sl"] = "reh"
    for t in pil:
        t["T"] = 130.0
        t["sl"] = "pil"
    return camp + reh + pil + rul


if __name__ == "__main__":
    # the sequential leg here runs in-process, so it needs the same worker
    # state the pool initializer builds
    G._W["resid"], G._W["Sf"], G._W["lo"], G._W["hi"] = (None,) * 4
    G._init_worker()
    raise SystemExit(main())
