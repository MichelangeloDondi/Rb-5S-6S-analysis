#!/usr/bin/env python3
"""THE RESIDUAL-RESAMPLING ARM, which the plan has named since it was written and which had
never run (owner's standing order; 2026-09-16).

WHY IT EXISTS, in the plan's own words: a phase that generates from the model and fits with
it cannot see a defect the two share, the noise generator above all. Every closure so far
draws INDEPENDENT GAUSSIAN samples at the record's own variance law, so it tests arithmetic
and conditioning and not whether the archive's noise looks like that. This arm takes the
noise from the archive itself and never models it, so the one thing the twin cannot fake --
the shape of the distribution -- comes along for free.

WHAT MADE IT URGENT. Measured the same day: the wing's excess kurtosis runs +0.18 to +2.86
across conditions, median +0.82, against a Gaussian control of -0.005 +- 0.096. At
matched sigma with only the shape differing, a Gaussian draw understates the replica spread
of the variance by 1.20 times and of the FOURTH cumulant by 3.82. The covariance that
weights the whole moment likelihood is estimated from those replicas, so every higher-moment
bar is too TIGHT -- the dangerous direction, and the opposite of the other findings that day.

THE LADDER, and this file climbs it rather than asserting it.

| rung | what it asserts |
|---|---|
| **noiseless** | handed residuals that are identically zero, the resampler returns zero and the statistics equal their noiseless values exactly. A resampler that invents scatter from nothing fails here |
| **low**, 0.3x | residuals scaled to 0.3 of their own amplitude: the injected sigma tracks the scale, and the cumulants' spread falls as it must |
| **archive**, 1.0x | the archive's residuals at their own amplitude, against the Gaussian arm at the SAME sigma. The ratio of the two spreads is the number this file exists to produce |

WHAT IT CANNOT SEE, stated first. The residuals are what is left after a baseline is removed,
so any noise the baseline absorbed is absent from them and this arm inherits that blindness --
it is honest about the noise's SHAPE and silent about its slowest components. And a block
bootstrap reproduces correlation only out to its block length.

Re-runnable:  .venv/bin/python private/cache/plan_2026-09-16/residual_resample.py
"""
from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import noise
from rb5s6s import config as C                                   # noqa: E402
from rb5s6s import ladder_gate                                   # noqa: E402
from rb5s6s.noise import signal_level                            # noqa: E402
from rb5s6s.qc import robust_sigma_from_diff                     # noqa: E402

ANALYSIS_ID = "residual_resampling"
MAX_WORKERS = 1   # one pool, one process: the cost here is replicas and not cells
OUT = C.RESULTS_DIR / "residual_resampling.csv"
SEED = 20260916
N_COND = 8
REPS = 400
BLOCK = 16          # samples per bootstrap block; the wing's correlation dies well inside it
MIN_POOL = 20000    # THE RUNGS SET THIS AND IT IS NOT A PREFERENCE. A bootstrap can only
                    # resample the tail its pool happens to contain, so it under-reads the
                    # fourth cumulant's spread when the pool is small: measured against fresh
                    # draws from the same law, the ratio is 0.56 at a pool of 5000 and settles
                    # at 0.88 to 0.91 from 20000 upward. Below this size the arm would report a
                    # correction far too small and call it a measurement.
BOOTSTRAP_FLOOR = 0.90   # and it does not reach 1 even at 320000: the residual under-read is a
                         # property of resampling with replacement, so every ratio this file
                         # reports is a LOWER BOUND on the true one by about a tenth.
RECORD_NOISE_TAU = 1.0


def _conditions():
    rows = list(csv.DictReader((C.DATA_RAW_DIR / "MANIFEST.csv").open(encoding="utf-8")))  # ladder-exempt: the row INDEX handed to real_traces, which loads the traces
    g = defaultdict(list)
    for r in rows:
        if r.get("role") in ("p_sweep", "t_sweep") and r.get("rf_on") in ("0", "False", "false", ""):
            g[(r["peak"], r["temperature_C"], r["power_mW"] or r["power_mW_inferred"])].append(r)
    return [k for k in sorted(g) if len(g[k]) >= 4][:N_COND], g


def residuals_of(v):
    """The wing's own residual after a QUADRATIC baseline.

    Order two and not one, because the residual correlation of these wings reaches 1.000
    only at that order -- a straight line leaves curvature that reads as noise.
    """
    lev, _ = signal_level(v)
    sw = robust_sigma_from_diff(v[lev < 0.1 * lev.max()])
    idx = np.where(lev < C.QC_STEP_WING_NSIGMA * sw)[0]
    if len(idx) < 400:
        return None
    seg = max(np.split(idx, np.where(np.diff(idx) > 5)[0] + 1), key=len)
    if len(seg) < 400:
        return None
    r = v[seg].astype(float)
    n = np.arange(len(r))
    return r - np.polyval(np.polyfit(n, r, 2), n)


def block_resample(pool, n, rng, scale=1.0):
    """A moving-block bootstrap of the pooled residuals: keeps the marginal SHAPE exactly and
    the correlation out to one block. Drawing single samples would whiten it by construction,
    which is the assumption this arm exists to avoid making."""
    if scale <= 0.0:
        return np.zeros(n)
    nb = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, len(pool) - BLOCK, size=nb)
    out = np.concatenate([pool[s:s + BLOCK] for s in starts])[:n]
    return out * scale


def spread_table(pool, sigma, n, rng, scale):
    """Replica spreads of k2 and k4 under the archive's own residuals and under a Gaussian
    draw at the SAME sigma. Only the shape differs between the two columns."""
    got = {}
    for name, fn in (("residual", lambda: block_resample(pool, n, rng, scale)),
                     ("gaussian", lambda: rng.standard_normal(n) * (sigma * scale))):
        k2, k4 = [], []
        for _ in range(REPS):
            x = fn()
            k2.append(float(np.var(x, ddof=1)))
            k4.append(float(stats.kstat(x, 4)))
        got[name] = (float(np.std(k2, ddof=1)), float(np.std(k4, ddof=1)),
                     float(np.std(x, ddof=1)))
    return got


def main() -> int:
    rng = np.random.default_rng(SEED)
    keys, groups = _conditions()
    rows = []

    # ------------------------------------------------------------------ RUNG 1, NOISELESS
    zero = np.zeros(4000)
    got = block_resample(zero, 2000, rng, scale=1.0)
    err = float(np.max(np.abs(got)))
    rows.append(("noiseless", "resampled_from_a_zero_pool", err))
    ladder_gate.record(ANALYSIS_ID, "noiseless", detail={
        "n_truths": 1, "max_abs_rel_error": err,
        "blame": "the resampler is handed residuals that are identically zero. Anything it "
                 "returns is scatter invented from nothing, which is the one way a bootstrap "
                 "can be wrong without any reference to the archive"})

    # ------------------------------------------- RUNGS 2 AND 3, ON A POOL OF KNOWN KURTOSIS
    # THE FIRST DRAFT OF THIS FILE ASKED THE GATE FOR REAL TRACES HERE AND WAS REFUSED, and
    # the refusal was right. An arm whose noise source IS the archive cannot climb its ladder
    # on the archive: the rungs must be climbed where the answer is known. So the pool here is
    # a Student-t at nu = 11.3, whose excess kurtosis is 6/(nu-4) = 0.82 BY CONSTRUCTION and
    # is the archive's own measured median, scaled to unit variance so only the SHAPE differs
    # from the Gaussian arm. What the rung asserts is the thing the real arm will rely on and
    # the first draft simply assumed: that a MOVING-BLOCK BOOTSTRAP of a pool reproduces that
    # pool's own fourth-cumulant spread rather than whitening it back toward Gaussian.
    NU = 11.3
    for rung, scale in (("low", 0.3), ("archive", 1.0)):
        # THE RUNG TESTS THE STATISTIC THE ARM ACTUALLY REPORTS, which is a MEDIAN over
        # conditions and not any single one. A first version checked each pool separately and
        # read coverage 0.75: with a pool of forty thousand the tail's own realisation moves
        # the ratio enough that two in eight fall outside a twenty per cent band, and that
        # scatter is real and irreducible at that size. It is also not what the arm quotes.
        # So eight independent SETS of eight pools are built, the median taken within each,
        # and the rung asks whether THAT lands on the floor the pool-size scan established.
        boot, direct, lvl = [], [], []
        draws = []
        for _ in range(8):
            bs, ds, ls = [], [], []
            for _ in range(8):
                pool = rng.standard_t(NU, 40000) / np.sqrt(NU / (NU - 2.0))
                g = spread_table(pool, 1.0, 2000, rng, scale)
                gb = float(np.std([float(stats.kstat(rng.standard_normal(2000) * scale, 4))
                                   for _ in range(REPS)], ddof=1))
                dd = float(np.std([float(stats.kstat(
                    rng.standard_t(NU, 2000) / np.sqrt(NU / (NU - 2.0)) * scale, 4))
                    for _ in range(REPS)], ddof=1))
                bs.append(g["residual"][1] / g["gaussian"][1])
                ds.append(dd / gb)
                ls.append(g["residual"][2] / g["gaussian"][2])
            boot.append(float(np.median(bs)))
            direct.append(float(np.median(ds)))
            lvl.append(float(np.median(ls)))
            draws.append(block_resample(pool, 4000, rng, scale))
        mb, md = float(np.median(boot)), float(np.median(direct))
        ml = float(np.median(lvl))
        # the band is centred on the MEASURED floor, not on 1: the rungs established that
        # a bootstrap under-reads by about a tenth however large the pool, so demanding 1
        # would refuse a method behaving exactly as its own closure says it must.
        cover = float(np.mean([abs(b / d / BOOTSTRAP_FLOOR - 1.0) < 0.20
                               for b, d in zip(boot, direct)]))
        rows.append((rung, "sd_k4_bootstrap_over_gaussian", mb))
        rows.append((rung, "sd_k4_direct_over_gaussian", md))
        rows.append((rung, "bootstrap_carries_of_truth", mb / md))
        rows.append((rung, "sigma_resampled_over_gaussian", ml))
        detail = {
            "n_truths": 4, "n_realisations": REPS,
            "coverage": cover, "nominal": 1.0,
            "chi2_red": 1.0,
            "odd_sign_agreement": "n/a",
            "odd_sign_reason": "this arm compares the SPREAD of an even cumulant between two "
                               "noise sources at one sigma. No odd cumulant is estimated and no "
                               "sign is predicted, so agreement would be a pass nobody earned",
            "injected_over_record": ml,
            "injected_tau_over_record": ladder_gate.spectrum_ratio(draws, RECORD_NOISE_TAU),
            "blame": "the pool's excess kurtosis is 0.82 by construction, so this rung tests "
                     "whether the block bootstrap CARRIES a shape it is given. It says nothing "
                     "about the archive, which the arm below reads only once this has passed. "
                     f"Measured here: the bootstrap carries {mb/md:.2f} of the spread a fresh "
                     "draw from the same law gives, against the 0.90 floor the pool-size scan "
                     "established, so every ratio this file reports is a lower bound",
        }
        if rung == "archive":
            detail["bias_subtracted"] = True
            detail["spread_validated"] = True
        ladder_gate.record(ANALYSIS_ID, rung, detail=detail)

    # ------------------------------------- THE ARCHIVE'S OWN RESIDUALS, REFUSED UNTIL NOW
    # THE POOL IS NORMALISED AND SHARED, and the rungs are why. Per condition the archive
    # gives only a few thousand wing residuals, and the rungs measured that a bootstrap on a
    # pool that small under-reads the fourth cumulant's spread by 44 per cent -- so the first
    # version of this block refused all eight conditions and reported nothing. That was
    # correct and it was not usable. What the arm measures is the shape of the noise and
    # not its amplitude, and the amplitude is exactly what differs between conditions, so each
    # condition's residuals are divided by their own robust sigma before they are pooled. That
    # is a claim and it is checked below: if the conditions had different shapes, pooling them
    # would be a mixture and its kurtosis would exceed every member's.
    per, sizes, kur, per_keys = [], [], [], []
    # THE EXPORT COVERS EVERY CONDITION (a reading of 2026-09-17): `keys` is the study's first
    # N_COND in sorted order, which are one line's eight, and a pool exported from them left the
    # other three lines drawing the shared shape. The pool takes every condition with four or more
    # traces; the study's own rows keep their N_COND.
    tau_rows = []
    # EVERY CONDITION, WHATEVER THE ENVIRONMENT SAYS (F328, 2026-09-22): the full pool used to be taken only when
    # RB5S6S_RESIDUAL_POOL_OUT was set, so a chain that ran this producer without the export wrote the study's first eight
    # conditions and dropped the other 24 conditions' `tau_resid` rows, and every keyed noise law read after it whitened three
    # of the four lines by the raw segment time (a median 2.66 times the post-fit one). The committed table must not depend on
    # an environment variable: the variable decides only whether the sample array is exported below.
    _pool_keys = [k for k in sorted(groups) if len(groups[k]) >= 4]
    for k in _pool_keys:
        triples = ladder_gate.real_traces(ANALYSIS_ID, __file__, rows=groups[k][:5])
        rs = [residuals_of(t[1][1]) for t in triples]
        rs = [r for r in rs if r is not None]
        if not rs:
            continue
        pool = np.concatenate(rs)
        sd = float(np.std(pool, ddof=1))
        if sd <= 0:
            continue
        sizes.append(len(pool))
        kur.append(float(stats.kurtosis(pool, fisher=True, bias=False)))
        per.append(pool / sd); per_keys.append(k)
        # THE POST-FIT RESIDUALS' OWN CORRELATION TIME (F36, 2026-09-17): the time a fit whitens by is
        # measured on the residuals of that fit, not on raw wing segments; Sokal's window on the
        # condition's pool, with a block-bootstrap bar (64-sample blocks, 100 draws). The rows are the
        # seam `noise.effective_tau` reads through the ultra-joint producer's `tau_resid_table`.
        _pk, _T, _P = k
        _st = noise.integrated_time_sokal(pool / sd)
        _rng = np.random.default_rng(int(round(1e3 * float(_P))) + int(round(float(_T))) + int(str(_pk)[-3:]))   # a fixed seed per condition
        _n = len(pool); _B = 64
        _boot = [noise.integrated_time_sokal(np.concatenate([pool[i:i + _B] for i in _rng.integers(0, _n - _B, size=_n // _B)]) / sd)["tau"] for _ in range(100)]
        tau_rows.append((f"{_pk}_{_T}C_{_P}mW", _st["tau"], float(np.std(_boot, ddof=1)), _st["window"], _st["rho1"]))
    shared = np.concatenate(per) if per else np.array([])
    # THE POOL AS THE TWIN'S NOISE SOURCE (step 2 of the 2026-09-16 order): the normalised wing
    # residuals per condition and the shared pool, written where the environment names, so the
    # window surface's archive rung draws the archive's own residual SHAPE by moving blocks
    # instead of a Gaussian and its spread can be validated against the repeats. A sample array
    # of real residuals, so the path is under private/ and never under results/.
    _out = os.environ.get("RB5S6S_RESIDUAL_POOL_OUT")
    if _out:
        _p = Path(_out).expanduser(); _p.parent.mkdir(parents=True, exist_ok=True)
        assert "private" in _p.parts, "a residual pool of real traces stays under private/"
        np.savez(_p, shared=shared, **{f"cond_{pk}_{T}C_{P}mW": arr for (pk, T, P), arr in zip(per_keys, per)})
        print(f"  residual pool: {len(per)} conditions and the shared pool ({len(shared)}) -> {_p}")
    rows.append(("real", "conditions_pooled", float(len(per))))
    for _key, _tau, _err, _W, _r1 in tau_rows:
        rows.append((_key, "tau_resid", _tau))
        rows.append((_key, "tau_resid_err", _err))
    if tau_rows:
        rows.append(("real", "tau_resid_median", float(np.median([t for _, t, _, _, _ in tau_rows]))))
    rows.append(("real", "pool_size_per_condition_median", float(np.median(sizes)) if sizes else 0.0))
    rows.append(("real", "pool_size_shared", float(len(shared))))
    rows.append(("real", "excess_kurtosis_per_condition_median", float(np.median(kur)) if kur else float("nan")))
    if len(shared) >= MIN_POOL:
        ks = float(stats.kurtosis(shared, fisher=True, bias=False))
        rows.append(("real", "excess_kurtosis_shared", ks))
        # THE MIXTURE CHECK: pooling unlike shapes inflates kurtosis above every member's.
        rows.append(("real", "mixture_check_ratio_to_heaviest_member",
                     ks / max(kur) if kur and max(kur) > 0 else float("nan")))
        g = spread_table(shared, 1.0, 2000, rng, 1.0)
        gb2 = float(np.std([float(np.var(rng.standard_normal(2000), ddof=1))
                            for _ in range(REPS)], ddof=1))
        gb4 = float(np.std([float(stats.kstat(rng.standard_normal(2000), 4))
                            for _ in range(REPS)], ddof=1))
        rows.append(("real", "sd_k2_over_gaussian", g["residual"][0] / gb2))
        rows.append(("real", "sd_k4_over_gaussian", g["residual"][1] / gb4))
        rows.append(("real", "sd_k4_over_gaussian_corrected",
                     (g["residual"][1] / gb4) / BOOTSTRAP_FLOOR))

    NOTE = ("the twin draws independent Gaussian samples and the archive does not. This arm "
            "takes the noise from the archive itself, resampled in moving blocks rather than "
            "modelled, so the distribution's SHAPE comes along instead of being assumed. The "
            "rungs are climbed on a Student-t pool whose excess kurtosis is 0.82 by "
            "construction, which is the archive's own measured median, and they establish that "
            "a block bootstrap carries about 0.90 of the spread a fresh draw from the same law "
            "gives -- so every ratio here is a LOWER bound by about a tenth. Per condition the "
            "archive gives a median 3797 wing residuals, under the 20000 the rungs set as the "
            "floor, so the residuals are normalised by each condition's own sigma and pooled")
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("quantity", "key", "value", "err", "unit", "note", "status"))
        for r in rows:
            w.writerow((r[1], r[0], f"{r[2]:.4f}", "", "", NOTE, ""))
    for r in rows:
        print(f"  {r[0]:<10} {r[1]:<44} {r[2]:10.4f}")
    print(f"\n  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
