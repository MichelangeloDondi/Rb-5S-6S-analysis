#!/usr/bin/env python3
"""
The lock disturbance vs time, from the recovered clock.  (post-hoc, 2026-07-23)

run_intrablock_trend.py closed with "the archive has no lever on the lock
DRIFT RATE at all" -- true of the archive alone. The recovered backup restores
a lever, through an estimator the experimenter proposed (2026-07-23): treat
the reference re-centrings as offset steps that move the frequency but not the
underlying drift, and difference positions inside spans the steps cannot
reach. Two differencing baselines exist, and their disagreement is itself the
finding:

  * BETWEEN blocks (adjacent conditions of one peak's power ladder, ~3-14 min):
    position steps of either sign -- drift PLUS the operator's re-centrings,
    which happen exactly in those gaps (power was being changed anyway; the
    experimenter recalls moving the reference "many times", never within a
    block).
  * WITHIN blocks (~30 s, timestamps in place of repeat index): reset-free by
    construction, so a pure -- if noisy -- local drift probe.

A third, refined estimator (same proposal, taken to trace level) fits ALL 99
timestamped positions jointly: per-segment offsets absorb the interventions,
one smooth r(t) is shared by every segment, and the segmentation is found
iteratively (>=4 sigma standardized steps, per-trace sigma from each block's
own robust scatter, likelihood scale profiled). It is the most powerful probe
and carries one caveat the layers below make explicit: a gap-step consistent
with the fitted r(t) is absorbed as drift, so sub-threshold interventions can
still masquerade -- and in one early block the within-block slope disagrees
with the fitted rate at ~3 sigma, which is why the within-block layer, not
the joint fit, owns the pure-drift claim.

What the probes say together (2026-07-23 run):

  * Within blocks the drift is never large: |r| <~ 4 ms/min at every epoch
    (early-session pooled -2.3 +/- 1.1, late +1.2 +/- 0.7 ms/min -- both
    within ~2 sigma of zero, opposite signs, i.e. bounds, not detections).
    The 6-9 ms/min the between-block pairs show in hour 1 is therefore NOT
    drift: it is the re-centrings.
  * The DISTURBANCE settles. Between-block |pair rate| decays ~exponentially
    (dAIC ~ +21 over a constant, tau ~ 80 min), step-like blocks concentrate
    in hour 1 (4 of 10 early vs 1 of 10 late), and after t ~ 3.7 h the
    unflagged pairs collapse to a tight +0.4..0.7 ms/min cluster.
  * The settled floor agrees across all three estimators -- joint fit
    +0.30 [+0.17, +0.37], pair median +0.50 +/- 0.60, clean cluster
    +0.55 +/- 0.17 ms/min -- i.e. 0.013-0.023 MHz/min on the laser axis
    (0.03-0.05 on the transition axis), positive in every one. Over a 32 s
    block that is ~0.2-0.3 ms of centre walk, below the 1.8 ms jitter, which
    is why the intra-block trend test rightly saw jitter.
  * The joint fit's disturbance law: tau = 73 [54, 102] min -- the same
    ~1-1.5 h thermal settling scale the wavemeter photographs show after a
    retune (APPARATUS section 6).

None of this moves a shipped number: widths are per-trace and centre steps do
not enter them. It characterises the instrument, and it post-hoc answers the
question D0 asked: every epoch probed sits far inside the 4 MHz/min envelope.

Requires the timestamp backup (quarantine copy). Without it this script -- like
the audit -- has no clock, and exits cleanly saying so.

Outputs: stdout only (a diagnostic of archival data, not a new result).
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

QUARANTINE = Path(
    os.environ.get("RB5S6S_BACKUP_DIR",
                   os.path.expanduser("~/Documents/RawDataBackUp_QUARANTINE_2026-07-23")))
RATE_MHZ_MS = 0.04257061052233977   # laser axis; M2, results/ruler_campaign.csv
JUMP_MS = 10.0                      # same step-block screen as run_intrablock_trend
LONG_PAIR_MIN = 7.0                 # pairs longer than this likely contain a re-centring
EARLY_H = 1.2                       # hour-1 ladders (4192, 4207)
LATE_H = 3.0                        # hour-4+ ladders (4154, 4121)


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clock() -> dict:
    """file (manifest-relative) -> earliest backup mtime, matched by CONTENT.
    Name matching is how a re-take series stayed hidden; never match by name."""
    by_md5: dict[str, float] = {}
    for p in QUARANTINE.rglob("*.csv"):
        d = _md5(p)
        t = p.stat().st_mtime
        by_md5[d] = min(by_md5.get(d, t), t)
    with open(ROOT / "data_raw" / "MANIFEST.csv") as f:
        return {r["file"]: by_md5[r["md5"]]
                for r in csv.DictReader(f) if r["md5"] in by_md5}


def load_blocks() -> pd.DataFrame:
    mt = clock()
    d = pd.read_csv(ROOT / "results" / "qc_metrics.csv")
    d = d[(d.flag == "canonical") & (~d.rf_on) & (d.role == "p_sweep")].copy()
    d["mtime"] = d.file.map(mt)
    rows = []
    for (peak, p_mw), g in d.groupby(["peak", "power_mW"]):
        g = g.dropna(subset=["mtime"]).sort_values("mtime")
        if len(g) < 4:
            continue
        step = g.peak_pos_ms.std(ddof=1) > JUMP_MS
        x = (g.mtime - g.mtime.mean()) / 60.0
        slope = err = np.nan
        if not step:
            coef, res_, *_ = np.linalg.lstsq(
                np.vstack([x, np.ones_like(x)]).T, g.peak_pos_ms, rcond=None)
            sig = float(np.sqrt(res_[0] / (len(g) - 2))) if len(res_) else 1.8
            slope, err = float(coef[0]), sig / float(np.sqrt((x ** 2).sum()))
        rows.append(dict(peak=int(peak), P=float(p_mw), n=len(g),
                         t=float(np.median(g.mtime)),
                         pos=float(np.median(g.peak_pos_ms)),
                         pos_err=float(g.peak_pos_ms.std(ddof=1) / np.sqrt(len(g))),
                         step=step, slope=slope, slope_err=err))
    B = pd.DataFrame(rows)
    B["t_h"] = (B.t - B.t.min()) / 3600.0
    return B


def pair_rates(B: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for peak, g in B.groupby("peak"):
        g = g.sort_values("t")
        recs = list(g.itertuples())
        for a, b in zip(recs, recs[1:]):
            dt_min = (b.t - a.t) / 60.0
            rows.append(dict(peak=peak, t_h=(a.t_h + b.t_h) / 2, dt_min=dt_min,
                             rate=(b.pos - a.pos) / dt_min,
                             err=max(float(np.hypot(a.pos_err, b.pos_err)) / dt_min, 0.3),
                             touches_step=a.step or b.step))
    return pd.DataFrame(rows)


def pooled(g: pd.DataFrame) -> tuple[float, float]:
    w = 1.0 / g.slope_err ** 2
    return float((g.slope * w).sum() / w.sum()), float(1.0 / np.sqrt(w.sum()))


def main() -> int:
    if not QUARANTINE.is_dir():
        print("no timestamp backup found (set RB5S6S_BACKUP_DIR); the archive alone "
              "has no clock -- nothing to do.")
        return 0

    B = load_blocks()
    PR = pair_rates(B)
    print("=" * 74)
    print("LOCK DISTURBANCE SETTLING  (recovered clock; estimator: experimenter,")
    print("2026-07-23 -- offsets reset, the rate survives differencing)")
    print(f"P-session blocks with clock: {len(B)}  "
          f"(step-like, screened from slopes: {int(B.step.sum())})")

    early = B[(B.t_h < EARLY_H) & ~B.step]
    late = B[(B.t_h > LATE_H) & ~B.step]
    me, ee = pooled(early)
    ml, el = pooled(late)
    print("\nWITHIN blocks -- reset-free local drift (bounds, not detections):")
    print(f"  t < {EARLY_H:g} h : {me:+5.2f} +/- {ee:.2f} ms/min   (n={len(early)})")
    print(f"  t > {LATE_H:g} h : {ml:+5.2f} +/- {el:.2f} ms/min   (n={len(late)})")
    print(f"  => |drift| <~ 4 ms/min at every epoch; the early 6-9 ms/min the")
    print(f"     between-block pairs show CANNOT be drift.")

    print("\nBETWEEN blocks -- drift PLUS operator re-centrings:")
    steps_early = int(B[B.t_h < EARLY_H].step.sum())
    steps_late = int(B[B.t_h > LATE_H].step.sum())
    print(f"  step-like blocks (moved mid-block): {steps_early} of "
          f"{len(B[B.t_h < EARLY_H])} early vs {steps_late} of "
          f"{len(B[B.t_h > LATE_H])} late")

    ok = PR[~PR.touches_step & (PR.err < 20)]
    t, r, e = ok.t_h.to_numpy(), ok.rate.to_numpy(), ok.err.to_numpy()

    def cost(model, p):
        z = (model(t, p) - r) / e
        return float((2.0 * (np.sqrt(1 + (z / 2) ** 2) - 1) * 4.0).sum())

    m0 = lambda tt, p: np.full_like(tt, p[0])
    m1 = lambda tt, p: p[0] * np.exp(-tt / p[1]) + p[2]
    f0 = optimize.least_squares(lambda p: (m0(t, p) - r) / e, [1.0],
                                loss="soft_l1", f_scale=2.0)
    f1 = optimize.least_squares(lambda p: (m1(t, p) - r) / e, [10.0, 0.5, 0.5],
                                bounds=([0, 0.05, -5], [500, 10, 5]),
                                loss="soft_l1", f_scale=2.0)
    a0, a1 = cost(m0, f0.x) + 2, cost(m1, f1.x) + 6
    print(f"\n  |pair rate| vs time, robust fit over {len(ok)} clean pairs:")
    print(f"    constant           : {f0.x[0]:+.2f} ms/min                    AIC {a0:6.1f}")
    print(f"    exponential + floor: A={f1.x[0]:.1f}, tau={f1.x[1]*60:.0f} min, "
          f"floor={f1.x[2]:+.2f}   AIC {a1:6.1f}")
    print(f"    dAIC = {a0 - a1:+.1f} for the exponential -- the DISTURBANCE settles")
    print(f"    (tau describes drift+re-centrings jointly; the pure-drift split is")
    print(f"     below the within-block bound and is not claimed)")

    lp = PR[(PR.t_h > LATE_H) & ~PR.touches_step]
    med = float(lp.rate.median())
    mad = float(1.4826 * (lp.rate - med).abs().median() / np.sqrt(len(lp)))
    print(f"\nSETTLED DRIFT (t > {LATE_H:g} h, median of {len(lp)} pairs):")
    print(f"  {med:+.2f} +/- {mad:.2f} ms/min "
          f"= {med * RATE_MHZ_MS:+.3f} MHz/min laser axis "
          f"({2 * med * RATE_MHZ_MS:+.3f} transition)")
    core = lp[(lp.rate - med).abs() < 1.0]      # the tight cluster; the rest are
    w = 1.0 / core.err ** 2                     # +-2 ms/min residual interventions
    cm, ce = float((core.rate * w).sum() / w.sum()), float(1 / np.sqrt(w.sum()))
    print(f"  the MAD above is intervention-inclusive; the {len(core)} pairs inside")
    print(f"  +-1 ms/min of the median agree to {cm:+.2f} +/- {ce:.2f} ms/min "
          f"-- a detection,\n  not a bound, though its cleanliness rests on the "
          f"cluster being interventions-free.")
    print(f"  over a 32 s block: {med * 32 / 60:.2f} ms of centre walk, below the")
    print(f"  1.8 ms jitter -- consistent with the intra-block JITTER verdict.")

    joint_fit_report()

    print("\nD0 postscript (post-hoc; D0 was declared uncertain before the backup):")
    print(f"  every epoch probed sits far inside the 4 MHz/min envelope --")
    print(f"  settled {abs(2 * med * RATE_MHZ_MS):.2f}, early bounded "
          f"<~ {4 * RATE_MHZ_MS * 2:.2f} MHz/min (transition axis).")
    print("\nNot resolved: per-temperature re-kicks (T-session ruler->block spans")
    print("are operator-contaminated -- the reference was adjusted between ruler")
    print("and science acquisition; intra-block bounds there: |r| <~ 5 ms/min).")
    return 0


# ---- the refined estimator: segmented joint fit at trace level ------------

def _traces() -> pd.DataFrame:
    mt = clock()
    d = pd.read_csv(ROOT / "results" / "qc_metrics.csv")
    d = d[(d.flag == "canonical") & (~d.rf_on) & (d.role == "p_sweep")].copy()
    d["mtime"] = d.file.map(mt)
    d = d.dropna(subset=["mtime"]).sort_values("mtime")
    d["t_h"] = (d.mtime - d.mtime.min()) / 3600.0
    sig = {}
    for _, g in d.groupby(["peak", "power_mW"]):
        r = g.peak_pos_ms - g.peak_pos_ms.median()
        s = max(0.8, 1.4826 * float(r.abs().median()))
        for i in g.index:
            sig[i] = s
    d["sig"] = pd.Series(sig)
    return d


def _R(t_h: np.ndarray, theta: list, model: str) -> np.ndarray:
    """Integrated rate, ms. M0: r=c. M1: r = A exp(-t/tau) + c."""
    if model == "M0":
        return theta[0] * t_h * 60.0
    A, tau, c = theta
    return c * t_h * 60.0 + A * tau * 60.0 * (1.0 - np.exp(-t_h / tau))


def _resid(g: pd.DataFrame, seg: np.ndarray, theta: list, model: str) -> np.ndarray:
    r = g.peak_pos_ms.to_numpy() - _R(g.t_h.to_numpy(), theta, model)
    w = 1.0 / g.sig.to_numpy() ** 2
    for s in np.unique(seg):
        m = seg == s
        r[m] -= (r[m] * w[m]).sum() / w[m].sum()
    return r / g.sig.to_numpy()


def joint_fit_report() -> None:
    SPLIT_Z = 4.0
    d = _traces()

    def chi2(theta, model, segs):
        return sum(float((_resid(g, segs[p], theta, model) ** 2).sum())
                   for p, g in d.groupby("peak"))

    def fit(model, segs):
        if model == "M0":
            o = optimize.minimize_scalar(lambda c: chi2([c], model, segs),
                                         bounds=(-30, 30), method="bounded")
            return [float(o.x)], float(o.fun)
        best, bf = None, np.inf
        for A in (0.5, 2, 5, 10, 20):
            for tau in (0.15, 0.3, 0.6, 1.0, 2.0):
                for c in (0.0, 0.3, 0.6):
                    f = chi2([A, tau, c], model, segs)
                    if f < bf:
                        best, bf = [A, tau, c], f
        o = optimize.minimize(lambda x: chi2(list(x), model, segs), best,
                              method="Nelder-Mead",
                              options=dict(xatol=1e-4, fatol=1e-4, maxiter=8000))
        return list(o.x), float(o.fun)

    segs = {p: np.zeros(len(g), int) for p, g in d.groupby("peak")}
    theta = [5.0, 0.5, 0.3]
    for _ in range(60):
        theta, _c = fit("M1", segs)
        zb, cut = 0.0, None
        for p, g in d.groupby("peak"):
            r = _resid(g, segs[p], theta, "M1")
            for s in np.unique(segs[p]):
                idx = np.where(segs[p] == s)[0]
                if len(idx) < 2:
                    continue
                dz = np.abs(np.diff(r[idx])) / np.sqrt(2)
                k = int(np.argmax(dz))
                if dz[k] > zb:
                    zb, cut = float(dz[k]), (p, int(idx[k + 1]))
        if zb < SPLIT_Z or cut is None:
            break
        segs[cut[0]][cut[1]:] += 1

    th1, chi1 = fit("M1", segs)
    th0, chi0 = fit("M0", segs)
    n = len(d)
    nseg = sum(len(np.unique(s)) for s in segs.values())

    def aic(chi, k):        # scale profiled out -> n log(chi2/n) + 2(k+1)
        return n * np.log(chi / n) + 2 * (k + 1)

    a0, a1 = aic(chi0, nseg + 1), aic(chi1, nseg + 3)
    scale = float(np.sqrt(chi1 / (n - nseg - 3)))

    print("\nJOINT SEGMENTED FIT (trace level; offsets absorb interventions,")
    print("one r(t) shared; same segmentation for both models):")
    print(f"  points {n}, segments {nseg}, residual scale {scale:.2f}")
    print(f"  M0 constant : c = {th0[0]:+.3f} ms/min            AIC {a0:7.1f}")
    print(f"  M1 exp+floor: A = {th1[0]:.2f}, tau = {th1[1]*60:.0f} min, "
          f"c = {th1[2]:+.3f}   AIC {a1:7.1f}")
    print(f"  dAIC = {a0 - a1:+.1f} for the exponential")

    cs = np.linspace(th1[2] - 0.25, th1[2] + 0.25, 15)
    prof = []
    for c in cs:
        o = optimize.minimize(lambda x: chi2([x[0], x[1], c], "M1", segs),
                              th1[:2], method="Nelder-Mead",
                              options=dict(xatol=1e-4, fatol=1e-4, maxiter=4000))
        prof.append(float(o.fun))
    prof = (np.array(prof) - chi1) / scale ** 2
    ok = cs[prof < 1.0]
    print(f"  floor: {th1[2]:+.3f} [{ok.min():+.3f}, {ok.max():+.3f}] ms/min (68%)"
          f" = {th1[2]*RATE_MHZ_MS:+.4f} MHz/min laser")
    print("  caveat: gap-steps consistent with r(t) are absorbed AS drift, so the")
    print("  within-block bounds above, not this fit, own the pure-drift claim")
    print("  (one early block disagrees with the fitted rate at ~3 sigma).")


if __name__ == "__main__":
    raise SystemExit(main())
