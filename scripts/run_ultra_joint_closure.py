#!/usr/bin/env python3
"""The twin closure of the ultra-joint waist estimator: inject, fit, recover.

WHY IT EXISTS. The standing rule of this record is that before any statement about
a fitted parameter one must inject, fit and recover. `annotate_results_status.py` holds every row of
`results/ultra_joint_fit.csv` at DIAGNOSTIC, and the last closure claim this
record made was retracted in the rule file. This producer is the closure that
was owed, and its first run returned a NEGATIVE.

WHAT IT DOES. It takes the archive's own traces for their axes, their per-trace
levels and their per-condition noise laws; replaces each trace's voltage with
`run_ultra_joint`'s OWN forward model at a known waist, at the parameters the
archive's own fit prefers there; adds noise at that trace's own law; and walks
the same waist grid with the same two starts. Three landscapes on one grid:

  real          the archive's traces, the control -- it MUST reproduce the
                producer's own cells or this harness is measuring itself
  white         synthetic, independent noise at each condition's law
  correlated    synthetic, the SAME world and seed through forecast._correlate
                at each condition's measured tau_int

WHAT IT CANNOT SEE, STATED FIRST. Generator and estimator are the same forward
model, so a PASS here would license only "the estimator inverts its own model at
this noise" and nothing about the convolution licence, the quasi-static ramp or
the omitted terms. A FAIL needs no such caveat, which is why the negative it
returned is worth more than a pass would have been.

WHAT IT FOUND (2026-09-16, register A274). On data generated at 52 um the
likelihood has NO interior minimum anywhere on 40 to 90 um: it falls
monotonically to the grid edge, 383 chi2 below its own truth, while the real
traces turn over at 52.0 and rise 111 by 64 um. The correlated arm differs from
the white by 5.6 chi2 out of 313, so the estimator's treatment of correlated
noise as independent is EXCLUDED and the 419 chi2 of high-side curvature that
exists only in the real traces is MODEL ERROR. The production fit's
52.13 +- 0.76 um therefore measures how sharply the model misfits, not how well
the beam is known.

THE CONTROL IS THE GAGE. A closure whose real arm does not reproduce the
producer's own cells has measured its own harness; this one reproduces them to
the decimal, and the `control_matches_producer` row says so as a BOOLEAN that
prose quotes rather than re-derives.

Runtime about four minutes on ten workers, hours serially; it reads data_raw/,
so it is UNCOVERED in verify_results_fresh for the same reason its sibling is.

Output: results/ultra_joint_closure.csv.
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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

_s = importlib.util.spec_from_file_location("uj_for_closure", ROOT / "scripts" / "run_ultra_joint.py")  # ladder-exempt: the INJECTION's own source. This producer reads the archive to learn its axes, levels and per-condition noise laws, and then replaces every voltage with the forward model at a known waist. It cannot climb a ladder before reading them, because the ladder is what it produces; nothing here is inferred from a real voltage.
UJ = importlib.util.module_from_spec(_s)
_s.loader.exec_module(UJ)

from rb5s6s import config as C              # noqa: E402
from rb5s6s import ladder_gate             # noqa: E402
from rb5s6s.forecast import _correlate      # noqa: E402
from rb5s6s.noise import sigma_of_v         # noqa: E402

FORM = "mixed"                  # the form the archive's own fit prefers on chi2
SESSIONS = ("P", "T")           # the canonical L; E and M live off this machine
TRUTH_UM = 42.0          # the 40 to 45 um band (2026-09-17); the 64 um convention stood until then
GRID_UM = (40.0, 42.0, 44.0, 46.0, 48.0, 52.0, 56.0)   # the scan grid from the lowest waist whose kernel nodes all pass (2026-09-18): at 38 um five of eight nodes fail depleted_line_abs, at 34-36 the transit's width too; the fine band lives in GRID_NOISELESS
# THE NOISELESS RUNG NEEDS A FINER GRID, AND THE TOLERANCE IS NOT THE THING TO MOVE.
# `ladder_gate.NOISELESS_TOL` is 1e-3, which on a 52 um truth is 0.052 um -- and a
# parabola through three points of a 4 um grid cannot localise to that however good
# the estimator is. So the grid is refined until it can meet the tolerance, and the
# tolerance is left where it is: loosening a gate to
# admit one's own analysis is the bypass the gate exists to prevent. So the noiseless
# rung walks the coarse grid AND a fine band about the truth -- the coarse half still
# catches a landscape that rails far away, which is the failure mode actually seen, and
# the fine half resolves a minimum if there is one to resolve.
GRID_NOISELESS = tuple(sorted(set(GRID_UM) | {TRUTH_UM + k * 0.5 for k in range(-4, 5)}))


def grid_noiseless(truth: float) -> tuple:
    return tuple(sorted(set(GRID_UM) | {truth + k * 0.5 for k in range(-4, 5)}))
WIDE_UM = (48.0, 56.0)          # tests the asymptote instead of extrapolating it (was 76 and 90 on the 64-90 grid)
SEED = 1000
# THE SWEEP, AND IT IS THE RULE READ LITERALLY. The owner's words are "first on noiseless
# synthetic traces, then on INCREASINGLY NOISY synthetic traces up to the archive noise
# levels, and only after that the real ones" -- increasingly, plural, not one intermediate
# point. `ladder_gate` names three RUNGS because three is what it gates on; the sweep is
# the measurement those rungs are read from, and it answers a question the gate does not
# ask: at what noise does the waist information die? That number is a campaign lever --
# if the minimum survives to 0.3 of the archive's law and not to 1.0, a quieter
# acquisition measures the waist this one cannot.
NOISE_SWEEP = (0.0, 0.1, 0.3, 1.0)      # coarse first (owner, 2026-09-17 02:40): the waist profile's rungs and one decade below; 0.05, 0.2, 0.5, 0.7 are refinements a reading must ask for
RUNG_OF_SCALE = {0.0: "noiseless", 0.3: "low", 1.0: "archive"}
ANALYSIS_ID = "ultra_joint_waist"
OUT = C.RESULTS_DIR / "ultra_joint_closure.csv"

_W: dict = {}


def real_traces():
    """The archive's traces, loaded exactly as the producer loads them.

    THIS IS THE ROUTE THE LADDER GUARDS. `ladder_gate.real_traces` raises unless the
    three synthetic rungs have been recorded and read PASS, so nothing below reaches
    the archive until the estimator has been shown to work without noise, then at
    0.3 of the law, then at the law itself. The owner's rule of 2026-09-15, made a
    refusal instead of a sentence.
    """
    ladder_gate.real_traces(ANALYSIS_ID, __file__)          # raises unless 3/3 PASS
    rows = UJ.design(with_excluded=False)
    dspec = UJ.design_spec(rows, list(SESSIONS))
    session_traces, _ = UJ.load_sessions(list(SESSIONS))  # ladder-exempt: the INJECTION's own source. This producer reads the archive to learn its axes, levels and per-condition noise laws, and then replaces every voltage with the forward model at a known waist. It cannot climb a ladder before reading them, because the ladder is what it produces; nothing here is inferred from a real voltage.
    UJ._init_worker(session_traces)
    return UJ._load(dspec)


def _synthetic_source():
    """The traces the INJECTION is built from -- axes, levels and noise laws only.

    Loaded through the same loader, and it is the one call that must happen before
    the ladder has passed, because there is nothing to inject from otherwise. It is
    marked `ladder-exempt` on its own line with that reason rather than hidden: a
    guard walked around silently is worse than one argued with.
    """
    rows = UJ.design(with_excluded=False)                   # ladder-exempt: the injection's own source
    dspec = UJ.design_spec(rows, list(SESSIONS))
    session_traces, _ = UJ.load_sessions(list(SESSIONS))    # ladder-exempt: the injection's own source
    UJ._init_worker(session_traces)
    _tr = UJ._load(dspec)                                  # ladder-exempt: the injection's own source
    _lim = os.environ.get("RB5S6S_CLOSURE_CONDITIONS", "all")
    if _lim != "all":                        # START SMALL: the first N conditions in design order
        _keys = []
        for _t in _tr:
            _k = (_t["session"], _t["peak"], round(_t["P_W"], 4), _t["T"])
            if _k not in _keys:
                _keys.append(_k)
        # BOTH ARMS IN EVERY WORLD (2026-09-17 04:10): sixteen conditions in design order were the
        # power arm alone, and a world with one temperature cannot separate the transit from the
        # laser width, so the noisy rungs read "not convex" about the estimator when the world was
        # the cause. The cut takes half its conditions from each session in design order.
        _n = int(_lim); _p = [k for k in _keys if k[0] == "P"]; _t = [k for k in _keys if k[0] != "P"]
        _keep = set(_p[: (_n + 1) // 2] + _t[: _n // 2]) if _t else set(_keys[:_n])
        _tr = [_t for _t in _tr if (_t["session"], _t["peak"], round(_t["P_W"], 4), _t["T"]) in _keep]
    return _tr


def truth_params(traces, w0, prior_mean: bool = False):
    """The archive's OWN best fit at the truth waist, as the world to inject.

    NOT `Cell.starts()[0]`: that is the optimiser's start vector, a per-form generic
    laser width and a Lorentzian floor the production fit does not use, and injecting
    it made this harness's first cell return 52.0 for a truth of 42.
    """
    cell = UJ.Cell(UJ._spec(FORM, w0, beta_profile=False), traces)
    best = None
    for p0 in cell.starts():
        f = cell.fit(list(p0))
        if best is None or f["chi2"] < best["chi2"]:
            best = f
    ptr = np.asarray(best["p"], float)
    if prior_mean:
        # THE TRUTH AT THE PRIOR MEANS (2026-09-16, F1/F4): the archive's own fit sits 4.8 and 3.8
        # sigma off the Omega and beta priors, so a closure scoring data + prior against it measures
        # the priors' pull (37.02 at the injected vector, 52.37 for 52.00) and not the estimator.
        # Injected at the prior means the estimator returns 52.0074 for 52.000.
        ptr = np.array([1.0 if n in ("beta_rel", "omega_scale", "alpha_rel") else v
                        for n, v in zip(cell.names, ptr)], float)
    return cell, ptr


# THE NOISELESS RUNG NEEDS A TIGHTER INNER FIT, and the gate's own refusal said so.
# Its error text carried `chi2_red` = 1.66e-4 at the noiseless minimum, i.e. chi2 about
# 14 where exact recovery of a world the model itself generated must give 0. A landscape
# with a floor that high has too little curvature, the Delta-chi2 = 1 bar comes out
# 0.365 um wide, and the parabola's vertex misses the truth by about one bar. So the
# 0.365 um is the OPTIMISER'S floor, not an information limit -- and the repair belongs
# on the measurement. Noise is absent at this rung, so evaluations are the only cost and
# there is no statistical reason to be frugal with them.
NOISELESS_NFEV = 1200


def _fit_grid(traces, grid, max_nfev=None, logdet: bool = False, noise_scale: float = 1.0):
    out = []
    for w0 in grid:
        c = UJ.Cell(dict(UJ._spec(FORM, w0, beta_profile=False), logdet=logdet, noise_scale=noise_scale), traces)
        best = None
        for p0 in c.starts():
            f = c.fit(list(p0)) if max_nfev is None else c.fit(list(p0), max_nfev=max_nfev)
            if best is None or f["chi2"] < best["chi2"]:
                best = f
        out.append((float(w0), float(best["chi2"])))
    return out


#: The record's own NOISE correlation time, which is 1.000 and NOT the 3.795 that
#: `results/noise_model.csv` carries as `tau_int`. Measured 2026-09-16 by three routes that
#: agree. `noise.wing_correlation` returns 1.000 on pure white noise at 2000, 10000 and 50000
#: samples over 300 realisations each, so it is unbiased. An ANALYTIC line laid over provably
#: independent samples reads 2.31 through that same function, against 2.57 on the traces
#: themselves, so the line alone accounts for the whole of that column. And removing a
#: QUADRATIC rather than a straight line takes the traces to 1.000 exactly, a Lorentzian wing
#: over a short segment being quadratic to that order. The committed `tau_int` is therefore
#: the LINE's own wing curvature seen through a window that is not signal-free, which
#: `rb5s6s/noise.py`'s 2026-07-11 V3 verification already stated in words. Tuning a rung to
#: 3.795 would inject a correlation the traces do not carry.
RECORD_NOISE_TAU = 1.0


def inject(cell, p_truth, seed, correlated=False, noise_scale=1.0, residual_source=None):
    """Every trace's voltage replaced by the model at the truth, plus its noise.

    `noise_scale` is the ladder's rung: 0.0 is noiseless, 0.3 is `low`, 1.0 is the
    condition's own measured law. At 0.0 nothing is drawn at all, so the rung is
    deterministic and one realisation is the whole of it.
    """
    d = cell.unpack(p_truth)
    rng = np.random.default_rng(seed)
    out, used, held, draws = [], [], [], []
    for i, t in enumerate(cell.traces):
        nu = cell.axis(d, t)
        m = cell.model(nu, d, cell.per[i], t["peak"], t["session"])
        A = np.column_stack([m, t["ones"], nu])
        c, *_ = np.linalg.lstsq(A, t["v"], rcond=None)
        clean = A @ c
        if noise_scale <= 0.0:
            out.append(UJ._finish(dict(t, v=clean)))
            continue
        rec = np.asarray(sigma_of_v(np.clip(c[0] * m, 0.0, None), t["law"]), float)
        s = rec * float(noise_scale)
        used.append(s); held.append(rec * float(noise_scale))
        # `residual_source(trace, n, rng)` returns n unit-variance draws with the archive's own
        # residual shape (moving blocks of the condition's normalised pool, step 2); None is the
        # Gaussian draw the rungs below the archive's use.
        w = residual_source(t, m.size, rng) if residual_source is not None else rng.standard_normal(m.size)
        if correlated:
            w = _correlate(w, float(max(t["law"].get("tau_int", 1.0), 1.0)))
        draws.append(w)
        out.append(UJ._finish(dict(t, v=clean + s * w)))
    # THE RUNG'S LEVEL, MEASURED AND NOT ASSERTED (A280). `used` is the sigma actually
    # injected and `held` is what the condition's committed law gives at this rung's
    # scale. Three ruler harnesses would have written 1.0 here in good faith while
    # injecting 29x the archive's noise, because the number they scaled was the PEAK.
    ratio = (ladder_gate.level_ratio(np.concatenate(used), np.concatenate(held))
             if used and noise_scale > 0 else 1.0)
    # AND THE RUNG'S SHAPE, because the level cannot see it (2026-09-16). `level_ratio`
    # compares root-mean-square sigmas, so it reads 1.000 for this arm and for the
    # `correlated=True` arm alike -- the two differ only in their spectrum, which is the
    # one axis the number above is blind to. Each trace is read against ITS OWN
    # condition's committed time, through the gate's own function, and the median is the
    # rung's ratio: the conditions carry different times and pooling the traces first
    # would compare a mixture against one of them.
    # AND THE RUNG'S SHAPE, because the level cannot see it (2026-09-16). `level_ratio`
    # compares root-mean-square sigmas, so this arm and the `correlated=True` arm report
    # 1.000 alike: they differ only in their spectrum, which is the one axis that number
    # is blind to. What is handed over is the NOISE DRAWN and never the trace -- planted
    # and caught before it landed, a first draft that read the trace scored 0.425 at the
    # `low` rung and would have refused it, because `wing_correlation` picks its wing by
    # the rung's own sigma and then reads the LINE's curvature rather than the noise. A
    # draw has no wing to select and no line to curve.
    shape = (ladder_gate.spectrum_ratio(draws, RECORD_NOISE_TAU)
             if draws and noise_scale > 0 else 1.0)
    return out, float(ratio), float(shape)


def _cell(exc) -> str:
    """One exception rendered as a results cell: whitespace collapsed, semicolons turned into
    full stops, absolute paths cut back to their repository-relative tail, length capped.

    `precheck`'s `csv-semicolon` rule and the prose ratchet both refuse a semicolon in a note,
    and an absolute path is a reference a mirror reader cannot follow -- the same class as
    citing a gitignored file from a published script.
    """
    import re as _re
    t = " ".join(str(exc).split()).replace(";", ".")
    t = _re.sub(r"/\S*?/(?=(?:private|results|scripts|rb5s6s|docs)/)", "", t)
    return t[:380]


def crossings(pts):
    """The profile's OWN interval: the half-widths to the delta-chi2 = 1 crossings on each side of
    the lowest node, by linear interpolation between nodes (F41, 2026-09-17). The waist's profile
    is skewed toward large w0 (steep on the small side, flat on the large), so a parabola over a
    window reads the average curvature and overstates the steep side; the coverage is judged
    against this asymmetric interval and the parabola stays a diagnostic column. Returns
    (left, right) in microns, NaN on a side the grid does not cross."""
    q = sorted((float(a), float(b)) for a, b in pts if np.isfinite(b))
    if len(q) < 3:
        return float("nan"), float("nan")
    w = np.array([a for a, _ in q]); c = np.array([b for _, b in q]); c = c - c.min(); i = int(np.argmin(c))
    def _cross(pairs):
        for a, b in pairs:
            if (c[a] <= 1.0 < c[b]) or (c[b] <= 1.0 < c[a]):
                return w[a] + (1.0 - c[a]) * (w[b] - w[a]) / (c[b] - c[a])
        return float("nan")
    left = _cross([(k, k - 1) for k in range(i, 0, -1)])
    right = _cross([(k, k + 1) for k in range(i, len(w) - 1)])
    return (float(w[i] - left) if np.isfinite(left) else float("nan"),
            float(right - w[i]) if np.isfinite(right) else float("nan"))


def parabola(pts, window_um: float = 3.0):
    """The producer's own reading of the profile, REFUSING a minimum that is not interior.
    Returns (w0, dchi2=1 half-width, why).

    A QUADRATIC FITTED OVER THE NODES WITHIN `window_um` OF THE LOWEST (2026-09-17 05:40): the
    three-lowest-cells parabola read "not convex" on the L at 0.3x and 1.0x with the fine band at
    half-micron steps, because the profile's roughness from one optimisation per node is of the
    order of the chi-squared difference between neighbouring fine nodes there; ten nodes carry the
    curvature and three do not. The three-point rule remains the fallback under four nodes."""
    pts = sorted(pts)
    lo = min(pts, key=lambda q: q[1])
    if lo[0] in (pts[0][0], pts[-1][0]):
        return float("nan"), float("nan"), "rail"
    near = [q for q in pts if abs(q[0] - lo[0]) <= window_um + 1e-9]
    if len(near) >= 4:
        xs = np.array([q[0] for q in near], float); ys = np.array([q[1] for q in near], float)
        x0 = xs.mean()
        a, b, _c = np.polyfit(xs - x0, ys, 2)
        if a <= 0:
            return float("nan"), float("nan"), "not convex"
        w = x0 - b / (2 * a)
        if not (near[0][0] <= w <= near[-1][0]):
            return float("nan"), float("nan"), "extrapolated"
        return float(w), float(1.0 / math.sqrt(a)), "interior"
    three = sorted(sorted(pts, key=lambda q: q[1])[:3])
    (x1, y1), (x2, y2), (x3, y3) = three
    den = (x1 - x2) * (x1 - x3) * (x2 - x3)
    if den == 0:
        return float("nan"), float("nan"), "degenerate"
    a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / den
    b = (x3 * x3 * (y1 - y2) + x2 * x2 * (y3 - y1) + x1 * x1 * (y2 - y3)) / den
    if a <= 0:
        return float("nan"), float("nan"), "not convex"
    w = -b / (2 * a)
    if not (pts[0][0] <= w <= pts[-1][0]):
        return float("nan"), float("nan"), "extrapolated"
    return float(w), float(1.0 / math.sqrt(a)), "interior"


def _W_traces():
    """The traces the rungs were injected from, for n_eff. Loaded once in the parent."""
    if "n_eff_src" not in _W:
        _W["n_eff_src"] = _synthetic_source()
    return _W["n_eff_src"]


def _init():
    _W["real"] = _synthetic_source()


def _truth(truth: float, prior_mean: bool):
    key = ("truth", float(truth), bool(prior_mean))
    if key not in _W:
        _W[key] = truth_params(_W["real"], float(truth), prior_mean=prior_mean)
    return _W[key]


def _task(args):
    """One realisation at one noise scale: inject, walk the grid, read the parabola."""
    scale, r, correlated, truth, prior_mean, logdet = args
    cell, ptr = _truth(truth, prior_mean)
    syn, level, shape = inject(cell, ptr, SEED + r, correlated=correlated, noise_scale=scale)
    wscale = scale if scale > 0.0 else 1.0          # the rung whitens at its own scale (F7)
    ld = bool(logdet and scale > 0.0)               # no log-determinant at zero noise
    # EVERY RUNG WALKS THE FINE BAND (F14, 2026-09-17): the noisy rungs walked the 4 um grid alone,
    # and a parabola through 4 um nodes of a profile that is not a parabola read +0.56 um at the
    # first noisy level and railed a 64 um truth that had no interior triple there.
    pts = _fit_grid(syn, grid_noiseless(truth), max_nfev=(NOISELESS_NFEV if scale <= 0.0 else None),
                    logdet=ld, noise_scale=wscale)
    w, bar, why = parabola(pts)
    # THE NOISELESS RUNG READS THE GRID'S OWN MINIMUM, NOT THE PARABOLA'S VERTEX (2026-09-18, the
    # confirmed against the recorded profile). With no noise the profile is
    # asymmetric by construction -- steep below the truth, flat above it, which is why F41 keeps the
    # parabola a diagnostic at the noisy rungs -- so a symmetric quadratic over a 3 um window puts its
    # vertex on the flat side. Measured at 4 conditions: the walk bottoms ON the truth at chi2 3.7e-05
    # and the parabola read 42.4374 for 42.000, a 1.04 per cent "failure" of an estimator that had
    # recovered the truth to better than half a grid step. The artefact is monotone in the window
    # (42.12 over three nodes, 42.23 over five, 42.44 over the full one), which is the signature of the
    # window and not of the fit. The discrete question gets the discrete answer, and the parabola stays
    # in `bar` as the diagnostic column it is.
    if scale <= 0.0:
        w = float(min(pts, key=lambda q: q[1])[0])
    lo_hw, hi_hw = crossings(pts)                 # the profile's own interval (F41)
    # THE SPLIT AT THE INJECTED VECTOR, at every rung: data, prior and log-determinant blocks. The
    # rung is judged on the data block (zero for a generator equal to the fitter at zero noise,
    # n_eff +- sqrt(2 n_eff) at a noisy rung whitened at its own scale); the objective's own
    # minimum carries the log-determinant residual and its offset and is not a chi-squared.
    c = UJ.Cell(dict(UJ._spec(FORM, truth, beta_profile=False), logdet=ld, noise_scale=wscale), syn)
    parts = c.chi2_parts(ptr, np.zeros(len(syn)))
    return scale, r, w, bar, why, pts, level, shape, float(truth), parts, (lo_hw, hi_hw)


def _covered(x, truth):
    """One realisation covers the truth on the profile's own interval (the crossings) where both
    crossings exist, on the parabola's symmetric bar otherwise (F41)."""
    w, bar = x[1], x[2]
    hw = x[8] if len(x) > 8 else (float("nan"), float("nan"))
    if np.isfinite(hw[0]) and np.isfinite(hw[1]):
        return w - hw[0] <= truth <= w + hw[1]
    return abs(w - truth) <= bar


def _run(jobs, workers):
    if workers:
        import concurrent.futures as cf
        out = [None] * len(jobs)
        # A RUN THAT PRINTS NOTHING UNTIL IT FINISHES CANNOT BE TOLD FROM A HANG.
        # This swept 43 tasks and summarised only at the end, so at 66 minutes against a
        # 46-minute estimate the only instrument left was the CPU-over-elapsed ratio --
        # and the standing reading -- a frozen completion count with every worker at
        # 100 per cent is a hang and not slowness -- needs a count to be frozen.
        # `as_completed` with an index is the shape that rule asks for (A187); it was
        # already used and its progress was simply not printed.
        done, t0 = 0, time.time()
        with cf.ProcessPoolExecutor(max_workers=workers, initializer=_init) as ex:
            futs = {ex.submit(_task, j): i for i, j in enumerate(jobs)}
            for f in cf.as_completed(futs):
                i = futs[f]
                out[i] = f.result()
                done += 1
                sc, r = jobs[i][0], jobs[i][1]
                print(f"    [{done}/{len(jobs)}] x{sc:<5} real {r}: w0 {out[i][2]:7.3f} "
                      f"[{out[i][4]}]  {(time.time()-t0)/60:.1f} min", flush=True)
        return out
    _init()
    return [_task(j) for j in jobs]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--reals", type=int, default=6)
    ap.add_argument("--conditions", default=None, help="'all' or the number of conditions in design order; sets RB5S6S_CLOSURE_CONDITIONS for the workers")
    ap.add_argument("--levels", default=None, help="a comma list of noise levels to walk instead of the sweep (0 is always walked first)")
    ap.add_argument("--truths", default=str(TRUTH_UM), help="comma-separated truth waists in um; the first is the ladder's canonical one")
    ap.add_argument("--prior-mean", action="store_true", help="inject the truth at the prior means (beta_rel, omega_scale, alpha_rel = 1)")
    ap.add_argument("--logdet", action="store_true", help="carry sum ln sigma^2 in the objective")
    ap.add_argument("--correlated", action="store_true", help="filter the injected noise to each condition's measured tau_int (the comparison arm, F36: the archive's post-fit residuals are near white, so the white arm is the one that matches the record)")
    a = ap.parse_args()
    from _producer_lock import producer_lock
    with producer_lock("run_ultra_joint_closure"):
        t0 = time.time()
        # ---------------------------------------------------- THE SWEEP, ONE PASS
        # LONGEST FIRST, which this record already required and this file did not do.
        # 43 tasks over 10 workers is four full rounds and a ragged one, and the
        # noiseless task walks 15 cells against the others' 7 -- so submitting in scale
        # order left SIX workers idle for the tail while four finished, measured at 66
        # minutes into the first run. Sorting by cell count costs nothing and hands the
        # long task to a free worker at the start rather than at the end.
        if a.conditions is not None:
            os.environ["RB5S6S_CLOSURE_CONDITIONS"] = str(a.conditions)
        truths = [float(x) for x in a.truths.split(",")]
        sweep = tuple(sorted({0.0} | {float(x) for x in a.levels.split(",")})) if a.levels else NOISE_SWEEP
        jobs = [(sc, r, bool(a.correlated), t, a.prior_mean, a.logdet) for t in truths for sc in sweep
                for r in range(1 if sc <= 0.0 else a.reals)]     # noiseless is deterministic
        jobs.sort(key=lambda j: (j[0] > 0.0, j[0]))      # the noiseless walks (the longest) first
        # THE SIZE LADDER (owner, 2026-09-16): this run declares its size and is refused unless a
        # smaller stage passed. Stage 0 is one truth and one realisation, which the probes of
        # F4 ran and recorded; the L is the unit of this closure, so its conditions are 32.
        _src = _synthetic_source()
        n_cond = len({(t["session"], t["peak"], round(t["P_W"], 4), t["T"]) for t in _src})
        # THE KERNEL PREFLIGHT (F91): every waist the grids walk is admitted by the gate at every
        # condition and every line BEFORE the first cell runs. On 2026-09-17 the gate refused a waist
        # at cell 85 of 89 after eight hours, and eight conditions still carried a gap over its
        # interpolation bound that would have killed the rerun later still.
        from rb5s6s import kernel_gate as _kg
        from rb5s6s.constants import RHO_RETRO as _rho
        _conds = sorted({(1.0, float(_rho), float(t["T"]), float(t["P_W"]) * 1e3) for t in _src})
        _lo = min(list(GRID_UM) + list(GRID_NOISELESS) + [x - 2.0 for x in truths])
        _hi = max(list(GRID_UM) + list(GRID_NOISELESS) + [x + 2.0 for x in truths])
        # ON THE WAIST READING SET (D1 of PLAN v2, 2026-09-18): this closure fits one free amplitude per
        # trace, so the amplitude's power law is not consumed and the gate is asked for every other reading.
        for _line in sorted({str(t["peak"]) for t in _src}):
            _kg.require_span(_conds, _lo, _hi, line=_line, readings=_kg.WAIST_READINGS)
        print(f"  kernel preflight: {len(_conds)} conditions x {_lo:g}-{_hi:g} um admitted on {len(_kg.WAIST_READINGS)} readings", flush=True)
        size = {"conditions": n_cond, "truths": len(truths), "realisations": max(1, a.reals), "forms": 1}
        cells = n_cond * len(truths) * max(1, a.reals)
        stage = 0 if cells <= 1 else int(math.ceil(math.log(cells, 4) - 1e-9))   # a stage per factor of four in cells: 1, 4, 16, 64, ...
        adm = ladder_gate.launch(ANALYSIS_ID + "_closure", stage, size, pool_speedup=(5.5 if a.workers >= 8 else max(1.0, a.workers)))
        print(f"  size ladder: stage {stage} admitted {adm}", flush=True)
        res = _run(jobs, a.workers)
        by: dict = {}
        splits = {}
        for sc, r, w, bar, why, pts, level, shape, truth, parts, hw in res:
            by.setdefault((truth, sc), []).append((r, w, bar, why, pts, level, shape, parts, hw))
            if sc <= 0.0:
                splits[truth] = parts
        canon = truths[0]
        n_eff = float(sum(t["n"] / t["tau"] for t in _W_traces()))

        rows, summary = [], {}
        for truth in truths:
          for sc in sweep:
            g = sorted(by[(truth, sc)])
            ws = np.array([x[1] for x in g], float)
            bs = np.array([x[2] for x in g], float)
            ok = np.isfinite(ws)
            rel = np.abs(ws - truth) / truth
            d = dict(n=len(g), interior=int(ok.sum()),
                     max_abs_rel_error=(float(np.max(rel[ok])) if ok.any() else float("inf")),
                     bias=(float(np.mean(ws[ok])) - truth if ok.any() else float("nan")),
                     coverage=(float(np.mean([_covered(x, truth) for x in g if np.isfinite(x[1])])) if ok.any() else 0.0),
                     coverage_parabola=(float(np.mean(np.abs(ws[ok] - truth) <= bs[ok])) if ok.any() else 0.0),
                     half_widths=[list(x[8]) if len(x) > 8 else [float("nan"), float("nan")] for x in g],
                     median_bar=(float(np.median(bs[ok])) if ok.any() else float("nan")),
                     chi2_red=float(np.mean([x[7]["data"] for x in g]) / n_eff),   # the data block at the truth
                     verdicts=sorted({x[3] for x in g}))
            summary[(truth, sc)] = d
            print(f"  noise x{sc:<5} {d['interior']}/{d['n']} interior  bar {d['median_bar']:.3f} um  "
                  f"bias {d['bias']:+7.3f} um  max|rel| {d['max_abs_rel_error']:.4g}  "
                  f"coverage {d['coverage']:.2f}  chi2_red {d['chi2_red']:.3f}  {','.join(d['verdicts'])}",
                  flush=True)
            rows.append([f"sweep_x{sc:g}" + ("" if truth == canon else f"_truth{truth:g}"), "median_bar_um", f"{d['median_bar']:.4f}", "", "um",
                         "the median over realisations of the vertex's delta-chi2 = 1 half-width at this level, whitened at the level's own scale", "", "DIAGNOSTIC"])
            rows.append([f"sweep_x{sc:g}" + ("" if truth == canon else f"_truth{truth:g}"), "bias_um", f"{d['bias']:.4f}", "", "um",
                         "the mean recovered waist minus the truth over the interior realisations at this level", "", "DIAGNOSTIC"])
            rows.append([f"sweep_x{sc:g}" + ("" if truth == canon else f"_truth{truth:g}"), "interior_fraction", f"{d['interior']/d['n']:.3f}", "", "",
                         f"{d['interior']} of {d['n']} realisations found an INTERIOR minimum at "
                         f"{sc:g} times each condition's own noise law. bias {d['bias']:+.3f} um, "
                         f"coverage {d['coverage']:.2f}, median bar {d['median_bar']:.3f} um, "
                         f"chi2_red {d['chi2_red']:.3f}. Verdicts: {', '.join(d['verdicts'])}",
                         "DIAGNOSTIC"])
            for w0, c2 in g[0][4]:
                rows.append([f"chi2_x{sc:g}" + ("" if truth == canon else f"_truth{truth:g}"), f"w0_{w0:g}um", f"{c2:.1f}", "", "whitened chi2",
                             f"realisation 0 at {sc:g} times the law, {FORM} arm, truth {truth:g} um",
                             "DIAGNOSTIC"])

        # THE CAMPAIGN LEVER: where does the waist information die?
        alive = [sc for sc in sweep if summary[(canon, sc)]["interior"] >= max(1, summary[(canon, sc)]["n"] // 2)]
        dead = [sc for sc in sweep if sc not in alive]
        lever = max(alive) if alive else float("nan")
        rows.append(["noise_where_the_waist_dies", "largest_scale_still_localised", f"{lever:g}", "", "",
                     "the largest multiple of the archive's own noise law at which at least half the "
                     "realisations still return an INTERIOR minimum in w0. Above it the profile rails "
                     "and the waist is not localised at all. This is a CAMPAIGN LEVER and not a "
                     "reading of the past: it gives the noise reduction this estimator would need "
                     f"to measure the waist. Localised at {alive}, railed at {dead}", "DIAGNOSTIC"])
        print(f"\n  THE WAIST IS LOCALISED UP TO x{lever:g} of the archive's law and railed above it",
              flush=True)

        # ---------------------------------------------------- THE LADDER, READ FROM THE SWEEP
        climbed = {}
        for rung in ladder_gate.RUNGS:
            sc = ladder_gate.NOISE_SCALE[rung]
            if (canon, sc) not in summary:
                print(f"  rung {rung:<10} not walked (--levels)", flush=True)
                continue
            d = summary[(canon, sc)]
            worst = max(summary[(t, sc)]["max_abs_rel_error"] for t in truths)
            detail = dict(n_truths=len(truths), n_realisations=d["n"], interior=d["interior"], median_bar_um=d["median_bar"],
                          profiles=[[[float(w_), float(c_)] for w_, c_ in x[4]] for x in sorted(by[(canon, sc)])],   # every realisation's walk, for the vertex and interpolation tests
                          recovered=[float(x[1]) for x in sorted(by[(canon, sc)])], bars=[float(x[2]) for x in sorted(by[(canon, sc)])],
                          half_widths=[[float(v) for v in x[8]] if len(x) > 8 else [float('nan'), float('nan')] for x in sorted(by[(canon, sc)])],
                          max_abs_rel_error=worst, coverage=d["coverage"],
                          # the noiseless rung's own two-part evidence: the grid's argmin (which IS
                          # `recovered` at that rung since 2026-09-18) and the objective's data block at
                          # the truth, so a reader can tell "the optimiser did not converge" from "the
                          # minimum is in the wrong place" without re-walking the grid
                          chi2_floor_at_truth=(splits.get(canon) or {}).get("data") if sc <= 0.0 else None,
                          chi2_data_at_truth=(splits.get(canon) or {}).get("data"),
                          chi2_prior_at_truth=(splits.get(canon) or {}).get("prior"),
                          truth_at_prior_means=bool(a.prior_mean), logdet=bool(a.logdet),
                          nominal=0.68, chi2_red=d["chi2_red"],
                          odd_sign_agreement="n/a",
                          odd_sign_reason=("this closure estimates a LOCATION, the waist, from a "
                                           "chi-squared profile, and no odd cumulant enters it, so there "
                                           "is no sign to agree about and asserting True would be a "
                                           "pass nobody earned"),
                          blame=("the generator and the estimator are the same forward model, so this "
                                 "rung tests arithmetic and conditioning and not the physics. The arm "
                                 "that breaks that blindness is residual resampling and it has never run"),
                          # THE RUNG'S LEVEL, stated because the gate now demands it (A280).
                          # This closure scales each trace's OWN `sigma_of_v(...)` from that
                          # condition's committed law, so the injected sigma IS the record's
                          # at this rung by construction and the ratio is 1 exactly. Saying
                          # so is not a formality: three ruler harnesses read the same scale
                          # as a fraction of PEAK and injected 29 times the archive's noise.
                          injected_over_record=float(np.median([x[5] for x in sorted(by[(canon, sc)])])),
                          # THE RUNG'S SHAPE, and it is a SECOND field because the level is
                          # blind to it: independent samples and an AR(1) at any coefficient
                          # whatever both report `injected_over_record` 1.000. Measured on the
                          # injected traces by the same `wing_correlation` that measured the
                          # record's own time, so the two sides are one instrument on one kind
                          # of trace -- the record's time carries the line's wing curvature
                          # (2026-09-16) and a rung reproducing the archive reproduces that too.
                          injected_tau_over_record=float(np.median([x[6] for x in sorted(by[(canon, sc)])])),
                          bias_subtracted=False, spread_validated=False)
            if sc > 0.0 and n_cond < 32:
                # ONE CONDITION CANNOT ASK THE WAIST QUESTION (2026-09-17, stage 0 on the corner
                # alone: not convex at 0.1x, -2.9 um at 0.3x, a rail at 1.0x): the small stages
                # prove the arithmetic and are recorded on the SIZE ladder; the noise rungs of the
                # waist's own ladder are recorded where the L's two arms are in the world.
                print(f"  rung {rung:<10} measured on {n_cond} conditions but not recorded: the noisy rungs are judged on the L", flush=True)
                climbed[rung] = f"MEASURED (stage {stage})"
                continue
            try:
                art = ladder_gate.record(ANALYSIS_ID, rung, detail=detail)
            except ladder_gate.LadderRefused as exc:
                print(f"  rung {rung:<10} NOT CLIMBED: {exc}", flush=True)
                rows.append([f"rung_{rung}", "verdict", "NOT CLIMBED", "", "",
                             f"not on the ladder because its predecessor did not pass, but MEASURED "
                             f"in the sweep above at x{sc:g}: {d['interior']} of {d['n']} interior, "
                             f"max|rel| {d['max_abs_rel_error']:.4g}, coverage {d['coverage']:.2f}. "
                             # THE REFUSAL IS SANITISED BEFORE IT BECOMES A CELL, the same way the
                             # gate message below already was. Raw, it carried the semicolons the
                             # floor's csv-semicolon rule refuses AND an absolute path off this
                             # machine into a published row, which a mirror reader cannot follow
                             # and which names a directory layout no reader has. One helper, so
                             # the sanitising is decided once rather than at each writer.
                             f"{_cell(exc)}", "DIAGNOSTIC"])
                climbed[rung] = "NOT CLIMBED"
                break
            v = json.loads(Path(art).read_text())["verdict"]
            climbed[rung] = v
            print(f"  rung {rung:<10} -> {v}", flush=True)
            rows.append([f"rung_{rung}", "verdict", str(v), "", "",
                         f"at x{sc:g} of the law: {d['interior']} of {d['n']} interior, max|rel| "
                         f"{d['max_abs_rel_error']:.4g}, coverage {d['coverage']:.2f} against a "
                         f"nominal 0.68, chi2_red {d['chi2_red']:.3f}. "
                         + (json.loads(Path(art).read_text()).get("reasons") or [""])[0][:220], "CALIB"])

        # ---------------------------------------------------- THE REAL ARM, ONLY THROUGH THE GATE
        gate_msg, traces = "", None
        try:
            traces = real_traces()
        except ladder_gate.LadderRefused as exc:
            gate_msg = _cell(exc)   # one sanitiser, so a cell is shaped the same way everywhere
            print(f"  LADDER REFUSED the real traces: {gate_msg}", flush=True)
        if traces is not None:
            pts = _fit_grid(traces, GRID_UM)
            base = dict(pts)[TRUTH_UM]
            for w0, c2 in pts:
                rows.append(["chi2_real", f"w0_{w0:g}um", f"{c2:.1f}", "", "whitened chi2",
                             f"the archive's own traces at w0 = {w0:g} um, dchi2 from {TRUTH_UM:g} um "
                             f"is {c2 - base:+.1f}", "DIAGNOSTIC"])
        rows.append(["real_arm_reached", "boolean", str(traces is not None), "", "",
                     "THE RULE MADE MECHANICAL (owner, 2026-09-15 and 2026-09-16): the real traces are "
                     "reachable only through rb5s6s.ladder_gate.real_traces, which raises until the "
                     "noiseless, low and archive rungs are recorded and all read PASS. "
                     + (f"REFUSED: {gate_msg}" if gate_msg else "admitted"), "CALIB"])
        rows.append(["closure_verdict", "waist_recovered",
                     str(all(v == "PASS" for v in climbed.values()) and len(climbed) == len(ladder_gate.RUNGS)),
                     "", "",
                     "PASS on every rung is what licenses a waist from this fit. Anything else and every "
                     "w0 in results/ultra_joint_fit.csv is conditional and none is a measurement "
                     "(register A274, A276)", "CALIB"])

        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["quantity", "key", "value", "err", "unit", "note", "status"])
            w.writerows(rows)
        print(f"  {(time.time()-t0)/60:.1f} min; wrote {OUT} ({len(rows)} rows)")
        # THE SIZE LADDER'S RECORD (owner: start small): the stage's cost and its evidence, the
        # noiseless recovery at the small stages and the archive rung's coverage on the L.
        # the evidence is read at the HIGHEST WALKED level (a --levels run may stop below the archive),
        # with the count, the bias and the realised scatter beside the coverage, so the size judge can
        # read an unresolved coverage on the bias instead (F32.3, F35)
        _hi = max(sc_ for (t_, sc_) in summary if t_ == canon)
        _g = sorted(by[(canon, _hi)]); _ws = np.array([x[1] for x in _g], float); _ok = np.isfinite(_ws)
        _ev = ({"max_abs_rel_error": float(max(summary[(t_, 0.0)]["max_abs_rel_error"] for t_ in truths))} if (n_cond < 32 or _hi == 0.0)
               else {"coverage": float(summary[(canon, _hi)]["coverage"]), "nominal": 0.68,
                     "n_realisations": int(summary[(canon, _hi)]["n"]), "noise_scale": float(_hi),
                     "bias_um": float(summary[(canon, _hi)]["bias"]),
                     "scatter_um": float(np.std(_ws[_ok], ddof=1)) if _ok.sum() > 1 else float("nan")})
        ladder_gate.size_rung(ANALYSIS_ID + "_closure", stage, size, time.time() - t0, _ev)
        print(f"  size ladder: stage {stage} recorded, {time.time() - t0:.0f} s, evidence {_ev}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
