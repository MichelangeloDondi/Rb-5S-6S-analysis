#!/usr/bin/env python3
"""Does the parallel profile2d path give exactly the sequential answers?

This is the acceptance gate for RB5S6S_WORKERS, and it covers BOTH parallel
paths: the kappa rows of profile2d and the waists of w0_scan. It was written
covering only the first, and the second was added the day w0_scan was
parallelised, because a smoke that certifies one of two paths certifies half
a claim and the half it omits is the one written later and read less.

It runs on a deliberately small grid so it finishes in minutes rather than
hours: two kappas, two betas, two waists, the
full residual over the whole trace assembly, a reduced nfev. The comparison is
EXACT EQUALITY of every chi-squared, not a tolerance, because the parallel
path runs the same solver on the same inputs from the same starting points and
has no licence to differ: the benchmark that motivated it measured a maximum
absolute difference of 0.00e+00 across ten production-sized rows.

Exact equality is the right bar here and a tolerance would be a smell. If this
ever fails, the two paths have diverged in what they FIT, most likely because
main()'s trace assembly changed and _load_everything() did not follow, which
is the one seam this construction has.

Prints PASS or the first differing cell, exits nonzero on any
difference, and exits 77 when the trees it needs are absent, so a
checkout that cannot run it never reads a pass.
Writes nothing. The full-scale acceptance (reproducing the committed
results/global_dataset_fit.csv end to end with workers on) is a separate,
deliberate run recorded in its own right, not this smoke.

    ./.venv/bin/python scripts/_m25_parallel_smoke.py
"""
from __future__ import annotations

import math
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import run_global_dataset_fit as G  # noqa: E402

KAPPAS = (0.0, 0.5)
BETAS = (0.005, 0.035)
NFEV = 120
W0S = (60e-6, 64e-6)          # two assumed waists, enough to compare rows


def _same(a, b) -> bool:
    """Exact equality, except that two NaNs in the same slot count as equal.

    IEEE 754 says nan != nan, so a plain tuple comparison reported the w0
    rows as DIFFERING while printing two lines of identical digits. The nan
    is real and expected here: ub95 interpolates a chi-squared crossing, and
    this smoke deliberately runs two kappas at nfev=40, which is far too
    coarse to bracket one. It resolves in production, where the grid has ten
    kappas and nfev=1200, and the committed CSV carries a finite bound.

    The bar is still EXACT: this widens equality to cover nan-at-the-same-
    position, not to tolerate a numerical difference.
    """
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if isinstance(x, float) and isinstance(y, float):
            if math.isnan(x) and math.isnan(y):
                continue
        if x != y:
            return False
    return True


# The house code for "the precondition is absent, so this check did not
# run". NOT 0: a check that cannot run must never be readable as one
# that passed, and this smoke returned 0 on every checkout without the
# private session trees - which is every checkout but the owner's, CI
# included - for as long as it has existed. Found 2026-09-02 while the
# worker seam was being checked: the seam had named this smoke as its
# own plant and would have inherited the false green.
COULD_NOT_RUN = 77


def main() -> int:
    if not (G.SESSION_20250704.is_dir() and G.SESSION_20250717.is_dir()):
        print("excluded trees absent: this smoke needs the full assembly. "
              f"Exiting {COULD_NOT_RUN}, which is NOT a pass: the check did "
              "not run.")
        return COULD_NOT_RUN

    t0 = time.time()
    W = G._load_everything()
    q0 = np.asarray(W["p0"][1:], float)
    print(f"assembly {time.time()-t0:.0f} s, {q0.size} free parameters")

    # --only-w0 re-verifies the second leg alone. profile2d's legs cost 22
    # minutes, so a fix to the COMPARISON should not have to re-earn a result
    # the same run already proved.
    if "--only-w0" in sys.argv:
        return _w0_leg(W, mp_import())

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
    print(f"profile2d: sequential {t_seq:.0f} s, parallel {t_par:.0f} s")
    if bad:
        for k, a, b in bad:
            print(f"DIFFERS at {k}: sequential {a!r} parallel {b!r}")
        return 1
    print(f"profile2d PASS: all {len(seq)} cells exactly equal")
    if "--only-2d" in sys.argv:
        return 0

    return _w0_leg(W, mp)


def mp_import():
    import multiprocessing as _mp
    return _mp


def _w0_leg(W, mp):
    # ---- the second worker kind, added when w0_scan was parallelised ----
    # A smoke that covers one of two parallel paths certifies half a claim,
    # and the half it leaves out is the one that was written later and read
    # less. Same bar: exact equality, two waists, a short chain.
    jobs = [(w, KAPPAS, 40) for w in W0S]
    t0 = time.time()
    w_seq = [G._w0_row(j) for j in jobs]
    t_wseq = time.time() - t0
    t0 = time.time()
    with mp.get_context("spawn").Pool(2, initializer=G._init_worker) as pool:
        w_par = pool.map(G._w0_row, jobs)
    t_wpar = time.time() - t0
    print(f"w0_scan: sequential {t_wseq:.0f} s, parallel {t_wpar:.0f} s")
    wbad = [(a, b) for a, b in zip(w_seq, w_par) if not _same(a, b)]
    if wbad:
        for a, b in wbad:
            print(f"DIFFERS: sequential {a!r} parallel {b!r}")
        return 1
    print(f"w0_scan PASS: all {len(w_seq)} rows exactly equal")
    return 0




if __name__ == "__main__":
    # the sequential leg here runs in-process, so it needs the same worker
    # state the pool initializer builds
    G._init_worker()
    raise SystemExit(main())
