"""The window-noise surface of the twin (night order 3c.2, owner 2026-09-16).

For ONE declared noise level per run (the level is the serial axis; windows, orders, conditions and
replicas fan out), the windowed cumulants of orders 2 to 7 at half-windows 0.5 to 21 MHz on traces
the model itself generated with the archive's own axes, levels and noise laws. Two things per row:

* at the noiseless rung, the package's self-centred estimator (`cumulants.windowed_moments` on the
  archive's grid) against the DIRECT truncated moments of the same model line on a tenfold finer
  grid, self-centred the same way: the estimator recovers what the model's own line carries at that
  window, or it does not. That is the rung's `max_abs_rel_error`, each order scaled by k2^(n/2);
* at a noisy rung, the replica mean and spread per statistic, the noise bias (replica mean minus the
  noiseless value) that the likelihood subtracts, and a split-half coverage: the bias from one half
  of the replicas, the other half's corrected mean against the noiseless value with its own bar.

Registered on the ladder's MOMENTS profile (seven levels in order); declares its size to the size
gate and records the stage; the archive rung stays FAIL until the spread is validated against the
archive's own residual resampling (`spread_validated`), which is step 2's covariance. Writes
`window_surface.csv` under `RB5S6S_RESULTS_DIR` when set, else `results/`.
"""
from __future__ import annotations
import argparse
import os
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from rb5s6s import config as C
from rb5s6s import windows as _WINDOWS, ladder_gate                       # noqa: E402
from rb5s6s.cumulants import windowed_moments                     # noqa: E402

_s = importlib.util.spec_from_file_location("closure_for_surface", ROOT / "scripts" / "run_ultra_joint_closure.py")
CL = importlib.util.module_from_spec(_s); _s.loader.exec_module(CL)   # ladder-exempt: the injection's own source, the closure's route
UJ = CL.UJ

ANALYSIS_ID = "window_surface"
# BOUND TO THE ONE SOURCE (2026-09-19). These eight half-widths were a literal identical to
# `windows.SURFACE`, which is the shape that lets a set drift silently: nothing compared them and
# a change to either would have gone unnoticed until a producer and a consumer disagreed.
ALL_WINDOWS = _WINDOWS.SURFACE
ALL_ORDERS = (2, 3, 4, 5, 6, 7)
STRIPS = ((28.0, 36.0), (-36.0, -28.0))    # mirror-free (the mirror band starts near 38 MHz); clear of a 21 MHz window
NOISELESS_TOL = ladder_gate.NOISELESS_TOL
FINE = 10                                  # the direct reference's grid refinement
MIN_REPS_FOR_RUNG = 8                      # halves of four are the least a coverage statement can rest on


def _debaseline(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """A straight line through the two outer strips, fitted jointly, subtracted."""
    sel = np.zeros_like(x, bool)
    for lo, hi in STRIPS:
        sel |= (x >= lo) & (x <= hi)
    if sel.sum() < 8:
        raise ValueError("window_surface: the outer strips hold fewer than eight grid points")
    A = np.column_stack([np.ones(sel.sum()), x[sel]])
    c, *_ = np.linalg.lstsq(A, y[sel], rcond=None)
    return y - (c[0] + c[1] * x)


def _direct(nu: np.ndarray, m: np.ndarray, W: float, orders) -> dict:
    """The truncated central moments of a sampled line, self-centred on the window's own centroid."""
    # THE BOUNDARY SAMPLE IS WEIGHTED BY ITS OVERLAP WITH THE WINDOW, as the package's estimator
    # does: a hard edge leaves an odd residual of the grid-spacing order (3e-3 scaled at 1 MHz on
    # the tenfold grid, measured 2026-09-16), which is not the line's and not the estimator's.
    dx = float(np.median(np.diff(nu)))
    def _weights(c):
        return np.clip((W - np.abs(nu - c) + 0.5 * dx) / dx, 0.0, 1.0) * np.clip(m, 0.0, None)
    c = float(nu[np.argmax(m)])
    for _ in range(80):
        w = _weights(c); n = np.sum(w)
        if n <= 0:
            return {k: float("nan") for k in orders}
        c_new = float(np.sum(nu * w) / n)
        if abs(c_new - c) < 1e-10:
            c = c_new; break
        c = c_new
    w = _weights(c); x = nu - c; w = w / np.sum(w)
    mu = {k: float(np.sum(x ** k * w)) for k in range(1, 8)}
    # THE REFERENCE IS THE ESTIMATOR'S OWN QUANTITY (F274, 2026-09-21): the central MOMENT of order n,
    # which is what `_estimate` returns since O33 and what every row is keyed `mu<n>@W` by. This
    # function returned the CUMULANT map here, so the noiseless admission compared mu_n with kappa_n
    # (negative for mu4 at 0.5 to 5 MHz and mu6 at 8 and 13) and refused or admitted on a quantity
    # mismatch; mu2 = kappa2 and mu3 = kappa3 identically, so nothing below fourth order moves.
    return {n: mu[n] for n in orders}


def _estimate(x: np.ndarray, y: np.ndarray, W: float, orders) -> dict:
    # MOMENTS ARE THE SURFACE'S STATISTIC (O33, A72). This producer fills the bias table the owner
    # asked for, and a bias measured on a cumulant carries that cumulant's cancellation into the
    # correction: near its zero, k4 is a four per cent residue of mu4 and 3 mu2^2, so the bias and
    # its standard error both inherit a precision loss the moments simply do not have.
    vals, _info = windowed_moments(x, _debaseline(x, y), W, tuple(orders), baseline=None)
    return {n: float(vals[n]) for n in orders}


def _condition_key(t) -> str:
    return f"{t['session']}_{t['peak']}_{1e3 * t['P_W']:.0f}mW_{t['T']:.0f}C"


def _model_line(cell, d, i, t, v_grid=None):
    """The model line on a FINE grid. With `v_grid` (the injected clean trace on the archive's
    grid) the injected amplitude, offset and slope are recovered by the same least squares the
    injection used and applied to the fine line, so the reference carries the trace's own
    baseline and can be de-baselined exactly as the estimator de-baselines the trace."""
    nu = cell.axis(d, t)
    fine = np.linspace(float(nu.min()), float(nu.max()), (nu.size - 1) * FINE + 1)
    m = np.asarray(cell.model(fine, d, cell.per[i], t["peak"], t["session"]), float)
    if v_grid is None:
        return fine, m
    mg = np.asarray(cell.model(nu, d, cell.per[i], t["peak"], t["session"]), float)
    A = np.column_stack([mg, np.ones_like(nu), nu])
    c, *_ = np.linalg.lstsq(A, np.asarray(v_grid, float), rcond=None)
    return fine, c[0] * m + c[1] + c[2] * fine


_W: dict = {}


POOL_BLOCK = 16     # samples per moving block, the residual-resampling producer's own


def _init_worker(truth: float, pool_path=None):
    tr = CL._synthetic_source()
    cell, ptr = CL.truth_params(tr, truth, prior_mean=True)
    _W.update(tr=tr, cell=cell, ptr=ptr, d=cell.unpack(ptr), syn0=CL.inject(cell, ptr, CL.SEED, noise_scale=0.0)[0])
    _W["pool"] = None
    if pool_path:
        z = np.load(pool_path)
        _W["pool"] = {k: np.asarray(z[k], float) for k in z.files}


def _pool_source(t, n, rng):
    """Moving-block resamples of the trace's own condition's normalised residual pool (the shared
    pool where the condition has none): the archive's residual SHAPE in the twin's draw."""
    pools = _W["pool"]
    key = f"cond_{t['peak']}_{t['T']:.0f}C_{1e3 * t['P_W']:.0f}mW"
    pool = pools.get(key, pools["shared"])
    nb = int(np.ceil(n / POOL_BLOCK))
    starts = rng.integers(0, len(pool) - POOL_BLOCK, size=nb)
    out = np.concatenate([pool[s:s + POOL_BLOCK] for s in starts])[:n]
    return out / max(float(np.std(pool)), 1e-300)


def _noiseless_task(args):
    """One condition's noiseless estimate, its de-baselined reference and its bare reference, per window."""
    k, ids, windows, orders = args
    cell, d, tr, syn0 = _W["cell"], _W["d"], _W["tr"], _W["syn0"]
    out = {}
    for W in windows:
        acc_r, acc_b, acc_e = [], [], []
        for i in ids:
            x, v = np.asarray(syn0[i]["x"], float), np.asarray(syn0[i]["v"], float)
            fine, m_bare = _model_line(cell, d, i, tr[i])
            fine, v_fine = _model_line(cell, d, i, tr[i], v_grid=v)
            acc_r.append(_direct(fine, _debaseline(fine, v_fine), W, orders))
            acc_b.append(_direct(fine, m_bare, W, orders))
            acc_e.append(_estimate(x, v, W, orders))
        out[W] = ({n: float(np.mean([r[n] for r in acc_r])) for n in orders},
                  {n: float(np.mean([b[n] for b in acc_b])) for n in orders},
                  {n: float(np.mean([e[n] for e in acc_e])) for n in orders})
    return k, out


def _noisy_task(args):
    """One replica of every condition at one level: the per-condition estimates per window."""
    r, scale, keys, idx, windows, orders = args
    syn, level, shape = CL.inject(_W["cell"], _W["ptr"], CL.SEED + 1 + r, noise_scale=scale,
                                  residual_source=(_pool_source if _W.get("pool") else None))
    out = {}
    for k in keys:
        for W in windows:
            acc = [_estimate(np.asarray(syn[i]["x"], float), np.asarray(syn[i]["v"], float), W, orders) for i in idx[k]]
            out[(k, W)] = {n: float(np.mean([e[n] for e in acc])) for n in orders}
    return r, level, shape, out


def _spread_check(vals, refused_keys, half, reps, scale, has_pool):
    """THE ARCHIVE RUNG'S SPREAD VALIDATION, COMPUTED (step 2): the twin's replica scatter of each
    condition mean against the five repeats' own scatter in `results/ultra_joint_moments.csv`
    (err over its t-factor is the standard error of the mean over the repeats, the same quantity
    as the sd across replicas of a condition mean), at the record's windows, over the admitted
    statistics. Validated when the median ratio sits inside the band the order set, 0.85 to 1.30;
    the per-order medians ride in the artefact. Without the archive's residual shape in the draw
    it is not validated, whatever the ratio, because the shape is what the rung is about."""
    import csv as _csv
    import re as _re
    out = {"validated": False, "ratios_by_order": {}, "n_compared": 0, "band": [0.85, 1.30], "source": "pool" if has_pool else "gaussian"}
    if scale < 1.0 or not has_pool:
        out["reason"] = "below the archive's level" if scale < 1.0 else "the draw is Gaussian, not the archive's residual shape"
        return out
    # THE REFERENCE IS ITS OWN ARTEFACT (A286, 2026-09-19): `results/ultra_joint_moments.csv` became the
    # twin's vector with D11, so the repeats' scatter it used to carry is read from the file named by
    # RB5S6S_SPREAD_REFERENCE (columns case, quantity, se_mean, null_median; `p18_repeat_noise.py` writes
    # it), and from the moments file only when no reference is named. A check that compares nothing says
    # ABSENT, which the ladder gate prints as the reason, distinct from a ratio outside the band.
    ref = os.environ.get("RB5S6S_SPREAD_REFERENCE", "")
    p = Path(ref) if ref else Path(C.RESULTS_DIR) / "ultra_joint_moments.csv"
    if not p.is_file():
        p = ROOT / "results" / "ultra_joint_moments.csv"
    out["reference"] = str(p)
    # THE NULL IS NOT ONE (a reading of 2026-09-17 03:40): the repeats' standard error comes
    # from four or five traces, so sigma/s has a median of sqrt(nu / median chi2_nu), 1.092 for
    # five repeats and 1.127 for four, and a twin whose scale is exactly right reads 1.09 here.
    # Every ratio is divided by its own row's null median before the band is read. And the
    # draw is a moving-block bootstrap, which carries about 0.90 of a fresh draw's spread
    # (run_residual_resampling's BOOTSTRAP_FLOOR), so an even-order reading a few per cent under
    # one is the resampler's under-read and is reported as such, not as the physics.
    from scipy.stats import chi2 as _chi2
    rec, null = {}, {}
    for row in _csv.DictReader(p.open()):
        if "se_mean" in row and "null_median" in row:                  # the reference artefact's own columns
            try:
                rec[(row["case"], row["quantity"])] = float(row["se_mean"])
                null[(row["case"], row["quantity"])] = float(row["null_median"])
            except (TypeError, ValueError):
                pass
            continue
        m = _re.search(r"(\d+) repeats.*t-factor ([\d.]+)", row.get("basis", ""))
        if not m or not row.get("err"):
            continue
        nrep = int(m.group(1)); nu = max(nrep - 1, 1)
        rec[(row["case"], row["quantity"])] = float(row["err"]) / float(m.group(2))
        null[(row["case"], row["quantity"])] = math.sqrt(nu / float(_chi2.median(nu)))
    ratios, raw = {}, {}
    for (k, W, n), v in vals.items():
        q = f"mu{n}@{W:g}"
        if (k, W, n) in refused_keys or (k, q) not in rec or rec[(k, q)] <= 0:
            continue
        v = np.asarray(v); sd_twin = float(v.std(ddof=1))
        raw.setdefault(n, []).append(sd_twin / rec[(k, q)])
        ratios.setdefault(n, []).append(sd_twin / rec[(k, q)] / null[(k, q)])
    allr = [x for xs in ratios.values() for x in xs]
    out["n_compared"] = len(allr)
    out["absent"] = not allr
    out["null_median_note"] = "each ratio divided by sqrt(nu / median chi2_nu) of its row's repeat count (1.092 at five repeats, 1.127 at four)"
    out["ratios_by_order_raw"] = {int(n): float(np.median(xs)) for n, xs in raw.items()}
    out["ratios_by_order"] = {int(n): float(np.median(xs)) for n, xs in ratios.items()}
    out["bootstrap_floor"] = 0.90
    out["band_note"] = ("the band is read on the null-corrected median; the statistics are correlated across orders "
                        "and windows, so the median's own width is not that of 567 independent draws and is not quoted here")
    if allr:
        med = float(np.median(allr)); out["median_ratio"] = med
        # PER ORDER, NOT POOLED (a reading of 2026-09-17): a pooled median cannot see an even-odd
        # split it records, so every order's own median must sit inside the band, and the parity
        # medians ride in the artefact for the per-order resampler floor to read.
        per = out["ratios_by_order"]
        out["validated"] = bool(per) and all(0.85 <= x <= 1.30 for x in per.values())
        evens = [x for n, x in per.items() if n % 2 == 0]; odds = [x for n, x in per.items() if n % 2 == 1]
        out["parity_medians"] = {"even": float(np.median(evens)) if evens else None, "odd": float(np.median(odds)) if odds else None}
        out["worst_order"] = max(per, key=lambda n: abs(per[n] - 1.0)) if per else None
    else:
        out["reason"] = "no archive rows at these windows: run with the record's windows 3.25, 6 and 12 MHz"
    return out


def main() -> int:
    global ANALYSIS_ID
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=3, help="the size stage. the default is the full noiseless surface the committed CSV carries")
    ap.add_argument("--noise", type=float, default=0.0, help="the level, a multiple of each condition's law. one per run")
    ap.add_argument("--truth", type=float, default=64.0)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--windows", default=",".join(str(w) for w in ALL_WINDOWS))
    ap.add_argument("--orders", default=",".join(str(o) for o in ALL_ORDERS))
    ap.add_argument("--conditions", default="all", help="'all' or the number of conditions taken in design order")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None, help="the CSV to write. default results/window_surface.csv. A cache-class run names a path under private/cache/")
    ap.add_argument("--analysis-id", default=ANALYSIS_ID, choices=("window_surface", "moment_window_bias"),
                    help="the ladder id the run climbs and records under. `moment_window_bias` is O34's bias surface "
                         "(plan V2, RT4), whose profile carries the 0.01 rung this producer's own profile lacks; the "
                         "estimator is the same, the likelihood's own (F270), so the surface is one artefact under "
                         "the id its consumer gates on")
    ap.add_argument("--noise-source", default=None, help="an .npz of normalised residual pools (RB5S6S_RESIDUAL_POOL_OUT of run_residual_resampling.py): the twin draws the archive's own residual shape")
    a = ap.parse_args()
    ANALYSIS_ID = a.analysis_id
    windows = tuple(float(w) for w in a.windows.split(","))
    orders = tuple(int(o) for o in a.orders.split(","))
    scale = float(a.noise)
    rung = {v: k for k, v in ladder_gate.NOISE_SCALE.items()}.get(scale)
    if rung is None or rung not in ladder_gate.rungs_of(ANALYSIS_ID):
        raise SystemExit(f"window_surface: noise {scale} is not a rung of the {ladder_gate.profile_of(ANALYSIS_ID)} profile")
    try:                                    # the level below must read PASS before this one is COMPUTED
        ladder_gate.climbable(ANALYSIS_ID, rung)
    except ladder_gate.LadderRefused as exc:
        print(f"  rung {rung} refused before any computation: {exc}", flush=True)
        return 2
    t0 = time.time()
    tr = CL._synthetic_source()          # the design's conditions; the truth is fitted in each worker
    keys = []
    for t in tr:
        k = _condition_key(t)
        if k not in keys:
            keys.append(k)
    n_cond = len(keys) if a.conditions == "all" else int(a.conditions)
    keys = keys[:n_cond]
    size = {"conditions": n_cond, "windows": len(windows), "orders": len(orders), "realisations": max(1, a.reps),
            "forms": 1, "truths": 1}
    adm = ladder_gate.launch(ANALYSIS_ID, a.stage, size, pool_speedup=max(1.0, float(a.workers)))
    print(f"  size ladder: stage {a.stage} admitted {adm}. rung {rung} at x{scale:g}; {n_cond} condition(s), "
          f"{len(windows)} windows, {len(orders)} orders, {max(1, a.reps)} replica(s)", flush=True)
    idx = {k: [i for i, t in enumerate(tr) if _condition_key(t) == k] for k in keys}
    rows, ref, bare, est0 = [], {}, {}, {}
    # ---- the noiseless reference and estimate, per condition (the mean over its traces), pooled
    import concurrent.futures as cf
    tasks = [(k, idx[k], windows, orders) for k in keys]
    if a.workers > 1:
        with cf.ProcessPoolExecutor(max_workers=a.workers, initializer=_init_worker, initargs=(a.truth,)) as ex:
            results = list(ex.map(_noiseless_task, tasks))
    else:
        _init_worker(a.truth); results = [_noiseless_task(t) for t in tasks]
    for k, out in results:
        for W, (r_, b_, e_) in out.items():
            ref[(k, W)], bare[(k, W)], est0[(k, W)] = r_, b_, e_
    # ADMISSION PER STATISTIC (2026-09-16): the seventh cumulant at a 0.5 MHz window holds two dozen
    # samples and the sixth at 21 MHz is set by the strip baseline; measured at stage 1, k7@0.5
    # missed the reference by 8.3e-2 while every order 2 to 4 at every window and every order at
    # 1 to 8 MHz sat under 1e-3. A statistic whose numerics are unresolved at the archive's own
    # sampling is REFUSED from the vector with its reason, and the rung is judged on the admitted
    # set, which is the set the likelihood will use. The tolerance is not moved.
    worst, admitted, refused = 0.0, [], []
    for (k, W), r in ref.items():
        e = est0[(k, W)]
        for n in orders:
            sc = max(abs(r[2]), 1e-12) ** (n / 2.0)     # every order in the units of k2^(n/2)
            rel = abs(e[n] - r[n]) / sc
            if rel <= NOISELESS_TOL:
                admitted.append([k, W, n, rel]); worst = max(worst, rel)
            else:
                refused.append([k, W, n, rel])
            b = bare[(k, W)][n]
            rows.append([k, f"mu{n}@{W:g}", f"{e[n]:.6g}", "", f"MHz^{n}",
                         f"estimator on the archive grid against the direct truncated moment {r[n]:.6g} of the same de-baselined line on a {FINE}x finer grid, both self-centred, scaled error {rel:.2e}. the bare model's truncated moment is {b:.6g}, so the strip baseline's bias at this window is {e[n] - b:+.4g} ({((e[n] - b) / max(abs(b), 1e-300) * 100) if n % 2 == 0 else (e[n] - b) / sc:+.3g} {'per cent' if n % 2 == 0 else 'in units of k2^(n/2), the odd orders of a symmetric line being zero'})",
                         f"noiseless, truth {a.truth:g} um at the prior means, {CL.FORM} form, strips {STRIPS[0]} MHz"
                         + ("" if rel <= NOISELESS_TOL else ". REFUSED from the vector: unresolved at the archive's sampling"), "DIAGNOSTIC"])
    print(f"  noiseless: {len(admitted)} statistics admitted (worst scaled error {worst:.3e}), {len(refused)} refused as "
          f"unresolved at the archive's sampling: " + ", ".join(sorted({f'k{n}@{W:g}' for _, W, n, _ in refused})), flush=True)
    detail = {"n_truths": 1, "n_statistics": len(ref) * len(orders), "max_abs_rel_error": worst,
              "n_admitted": len(admitted), "n_refused": len(refused),
              "refused_statistics": sorted({f"mu{n}@{W:g}" for _, W, n, _ in refused}),
              "admission_rule": f"a statistic enters only where the estimator meets the direct truncated moment within {NOISELESS_TOL:g} of k2^(n/2) on every condition",
              "windows": list(windows), "orders": list(orders), "conditions": n_cond}
    refused_keys = {(k, W, n) for k, W, n, _ in refused}
    # ---- the noisy replicas
    if scale > 0.0:
        reps = max(2, a.reps)
        if reps < MIN_REPS_FOR_RUNG:
            print(f"  x{scale:g}: {reps} replicas sample the level but do not judge it. the noise rung is recorded at {MIN_REPS_FOR_RUNG} or more", flush=True)
        vals = {(k, W, n): [] for k in keys for W in windows for n in orders}
        levels, shapes = [], []
        jobs = [(r, scale, keys, idx, windows, orders) for r in range(reps)]
        if a.workers > 1:
            with cf.ProcessPoolExecutor(max_workers=a.workers, initializer=_init_worker, initargs=(a.truth, a.noise_source)) as ex:
                res = list(ex.map(_noisy_task, jobs))
        else:
            _init_worker(a.truth, a.noise_source)
            res = [_noisy_task(j) for j in jobs]
        for r, level, shape, out in sorted(res, key=lambda z: z[0]):
            levels.append(level); shapes.append(shape)
            for (k, W), e in out.items():
                for n in orders:
                    vals[(k, W, n)].append(e[n])
        half = reps // 2
        cov, pulls, odd_ok, odd_n = [], [], 0, 0
        for (k, W, n), v in vals.items():
            if (k, W, n) in refused_keys:
                continue                                  # a refused statistic is not judged, nor used
            v = np.asarray(v); e0 = est0[(k, W)][n]
            bias = float(v.mean() - e0); sd = float(v.std(ddof=1))
            # SPLIT HALVES (2026-09-16): the bias from half A, half B's corrected mean against the
            # noiseless value with half B's own bar. A pull built from the same replicas that set
            # the bias is zero by construction, which is what the first n01 run reported as
            # chi2_red 0.00; only the split makes the coverage and the pull statements.
            bA = float(v[:half].mean() - e0); mB = float(v[half:].mean())
            # THE CORRECTED MEAN CARRIES BOTH HALVES' VARIANCE (2026-09-16): half A's bias has its
            # own bar, sd_A/sqrt(n_A); omitting it read chi2_red 2.65 and coverage 0.51 at 0.3x
            # where the physics gives about 1.3 and 0.6. The statement is on mB - bA - e0.
            sA = float(v[:half].std(ddof=1) / math.sqrt(half)); sB = float(v[half:].std(ddof=1) / math.sqrt(reps - half))
            s_corr = math.sqrt(sA * sA + sB * sB)
            cov.append(abs(mB - bA - e0) <= s_corr)
            pulls.append(((mB - bA - e0) / max(s_corr, 1e-300)) ** 2)
            # A FLIP COUNTS ONLY WHERE THE NOISELESS VALUE IS RESOLVED (2026-09-16 night): among
            # statistics barely above their bar a sign flip is a one-sigma event, and three of 360
            # failed the n01 rung on a rule that read them as a disagreement. Four bars of the
            # replica mean resolves the sign at 3e-5 per statistic, so a flip there is a defect.
            if n % 2 == 1 and abs(e0) > 4.0 * sd / math.sqrt(reps):
                odd_n += 1; odd_ok += int(np.sign(v.mean()) == np.sign(e0))
            rows.append([k, f"mu{n}@{W:g}", f"{v.mean():.6g}", f"{sd:.3g}", f"MHz^{n}",
                         f"replica mean over {reps} at x{scale:g} of the law. noise bias {bias:+.4g} against the noiseless {e0:.6g}; sd {sd:.3g}",
                         f"rung {rung}, truth {a.truth:g} um at the prior means, {CL.FORM} form", "DIAGNOSTIC"])
        sv = _spread_check(vals, refused_keys, half, reps, scale, bool(a.noise_source))
        detail.update(n_realisations=reps, coverage=float(np.mean(cov)), nominal=0.68,
                      chi2_red=float(np.mean(pulls)),
                      odd_sign_agreement=(bool(odd_ok == odd_n) if odd_n else "n/a"),
                      odd_sign_reason=("no odd statistic is resolved at four bars at this level" if not odd_n else
                                       f"{odd_ok} of {odd_n} odd statistics resolved at four bars keep the noiseless sign"),
                      injected_over_record=float(np.median(levels)), injected_tau_over_record=float(np.median(shapes)),
                      bias_subtracted=True,
                      coverage_meaning=("the split-half coverage and pull are the replica SPREAD's self-consistency (the "
                                        "corrected mean m_B - b_A - e0 is m_B - m_A, in which e0 cancels): they test that "
                                        "the bar is right, never that the bias is; the bias itself is the replica mean "
                                        "minus the noiseless value with its bar, subtracted downstream, and the archive "
                                        "rung's spread validation is the test against the data"),
                      spread_validated=sv["validated"], spread_check=sv,
                      blame=("the generator is the model with a GAUSSIAN draw at the condition's law. the archive's residual "
                             "resampling gives k4 a spread 4.99x this draw's, so the spread is not validated until step 2's "
                             "covariance replaces the draw"))
        print(f"  x{scale:g}: split-half coverage {detail['coverage']:.2f}, bias-corrected chi2_red {detail['chi2_red']:.2f}, "
              f"level {detail['injected_over_record']:.3f}, shape {detail['injected_tau_over_record']:.3f}", flush=True)
    cost = time.time() - t0
    # ---- the two ladders
    if scale > 0.0 and max(2, a.reps) < MIN_REPS_FOR_RUNG:
        verdict = "NOT JUDGED (too few replicas)"
    else:
        try:
            art = ladder_gate.record(ANALYSIS_ID, rung, detail=detail)
            verdict = json.loads(art.read_text())["verdict"]
            print(f"  rung {rung}: {verdict} ({art.name})", flush=True)
        except ladder_gate.LadderRefused as exc:
            verdict = "NOT CLIMBED"; print(f"  rung {rung} NOT CLIMBED: {exc}", flush=True)
    ladder_gate.size_rung(ANALYSIS_ID, a.stage, size, cost,
                          {"max_abs_rel_error": worst} if (scale <= 0 or max(2, a.reps) < MIN_REPS_FOR_RUNG) else
                          {"coverage": detail.get("coverage"), "nominal": 0.68})
    rows.append([f"rung_{rung}", "verdict", verdict, "", "", f"stage {a.stage}, {cost:.0f} s, worst scaled error {worst:.2e}", "", "DIAGNOSTIC"])
    out = Path(a.out) if a.out else Path(C.RESULTS_DIR) / "window_surface.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case", "quantity", "value", "err", "unit", "basis", "note", "status"]); w.writerows(rows)
    print(f"  wrote {out} ({len(rows)} rows) in {cost:.0f} s", flush=True)
    return 0 if verdict.startswith(("PASS", "NOT JUDGED")) else 1   # a chain stops at a FAIL


if __name__ == "__main__":
    sys.exit(main())
