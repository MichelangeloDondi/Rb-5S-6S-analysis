#!/usr/bin/env python3
"""
The lock disturbance vs time, from the recovered clock.  (post-hoc, 2026-07-23)

run_intrablock_trend.py closed with "the archive has no lever on the lock
DRIFT RATE at all" -- true of the archive alone. The recovered backup restores
a lever, through an estimator the experimenter proposed (2026-07-23): treat
the reference re-centrings as offset steps that move the frequency but not the
underlying drift, and difference positions inside spans the steps cannot
reach. Two differencing baselines exist, and they disagree -- the
disagreement is what identifies the interventions:

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
  * The state-space refinement (the final stage below) separates what the
    joint fit could not: THE DRIFT IS ONE CONSTANT across the five-hour
    power session the fit sees (T-session probes give only bounds). The
    residual audit then revised its size: +0.38 [+0.17, +0.59] ms/min
    = +0.016 [+0.007, +0.025] MHz/min laser (68%), a ~2-sigma positive
    indication under the adequate (mixture) noise model -- the gaussian
    +0.74 was biased by three unmodelled end-of-ladder moves. Adding a
    drift-settling term buys nothing (dAIC +4.0) -- while the INTERVENTION
    amplitude settles, sigma_gap ~ 88 ms x exp(-t / 86 min). The tau ~ 73 min
    the segmented fit reported was the operator's settling, not the laser's;
    it matches the ~1-1.5 h post-retune scale the wavemeter photographs show
    (APPARATUS section 6). The earlier estimators' "settled floor"
    0.013-0.023 MHz/min sits 1-1.5 sigma below the constant because their
    exponentials leaked early drift; the state-space value supersedes them.
  * Over a 32 s block the constant drift walks the centre ~0.4 ms, below the
    1.8 ms jitter, which is why the intra-block trend test rightly saw jitter.

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
    state_space_report()
    mixture_report()
    pull_bound_report()

    print("\nD0 postscript (post-hoc; D0 was declared uncertain before the backup):")
    print("  measured constant 0.016 [0.007, 0.025] vs the 4 MHz/min envelope,")
    print("  both laser axis: ~250x inside; even the within-block hour-1 bound")
    print(f"  (<~ {4 * RATE_MHZ_MS:.2f} MHz/min laser) never approaches it.")
    print("\nThe per-temperature question, split by the refined model:")
    print("  for the DRIFT it stays unresolved (T-session baselines too short;")
    print("  intra-block bounds |r| <~ 5 ms/min per dwell). For the OPERATOR it is")
    print("  answered: the very ruler->science steps that contaminate the drift")
    print("  probe ARE the intervention amplitude, and it RE-KICKS at every dwell --")
    print("  RMS 74 / 137 / 106 ms (3-6 MHz laser) at 110/90/70 C against the")
    print("  <~20 ms it had settled to by late P-session; largest single step")
    print("  (237 ms ~ 10 MHz) right after the 9.6 h break. Each temperature change")
    print("  (with its per-peak retunes) begins a fresh re-acquisition transient --")
    print("  the 'one exponential per temperature' of the original proposal, holding")
    print("  for the disturbance. Descriptive RMS over n=3-4 single steps per dwell,")
    print("  retune and window moves included; not a fitted sig_gap.")
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


# ---- the refined model: linear-Gaussian state space, exact likelihood ------
#
# y_i = x_i + R(t_i; drift) + eps_i;  x is the cumulative-intervention offset,
# a random walk whose steps live at between-block gaps: eta ~ N(0, sig_gap(t)^2).
# Steps > 100 ms are scan-window repositionings and are freed wherever they
# occur (the 4207 excursion RETURNS mid-block -- gap-only freeing strands the
# state and poisons every later block). Drift law and intervention law each
# get {constant | exponential}: the 2x2 comparison asks directly which one
# settles. The likelihood skip set (first obs per peak + freed window moves)
# is deterministic and identical across models.

def _R_int(t_h, kind, th):
    if kind == "const":
        return th[0] * t_h * 60.0
    A, tau, c = th
    return c * t_h * 60.0 + A * tau * 60.0 * (1.0 - np.exp(-t_h / tau))


def _kalman_nll(peaks, kind_d, th_d, kind_i, th_i, s):
    nll = 0.0
    for p in peaks:
        y = p["y"] - _R_int(p["t"], kind_d, th_d)
        m, P = 0.0, 1e12
        for i in range(len(y)):
            skip = i == 0
            if i > 0:
                if p["wm"][i]:
                    P += 1e12
                    skip = True
                elif p["gap"][i]:
                    tg = 0.5 * (p["t"][i] + p["t"][i - 1])
                    sg = th_i[0] if kind_i == "const" else th_i[0] * np.exp(-tg / th_i[1])
                    P += sg ** 2
            r = y[i] - m
            S = P + (s * p["sig"][i]) ** 2
            if not skip:
                nll += 0.5 * (np.log(2 * np.pi * S) + r * r / S)
            K = P / S
            m += K * r
            P *= (1 - K)
    return nll


def _unpack(v, kind_d, kind_i):
    i = 0
    if kind_d == "const":
        th_d = [v[0]]; i = 1
    else:
        th_d = [np.exp(v[0]), float(np.clip(np.exp(v[1]), 0.05, 12.0)), v[2]]; i = 3
    if kind_i == "const":
        th_i = [np.exp(v[i])]; i += 1
    else:
        th_i = [np.exp(v[i]), float(np.clip(np.exp(v[i + 1]), 0.05, 12.0))]; i += 2
    return th_d, th_i, float(np.clip(np.exp(v[i]), 0.3, 5.0))


def _ss_fit(peaks, kind_d, kind_i):
    def nll_vec(v):
        td, ti, sc = _unpack(v, kind_d, kind_i)
        return _kalman_nll(peaks, kind_d, td, kind_i, ti, sc)
    p0 = ([0.5] if kind_d == "const" else [np.log(3.0), 0.0, 0.3])
    p0 += ([np.log(20.0)] if kind_i == "const" else [np.log(40.0), 0.0])
    p0 += [np.log(1.2)]
    p0 = np.array(p0)
    best = None
    for f in (0.0, 0.7, -0.7):
        o = optimize.minimize(nll_vec, p0 + f, method="Nelder-Mead",
                              options=dict(xatol=1e-4, fatol=1e-4, maxiter=12000))
        if best is None or o.fun < best.fun:
            best = o
    return best.x, best.fun, 2 * best.fun + 2 * len(p0)


def state_space_report() -> None:
    d = _traces()
    peaks = []
    for peak, g in d.groupby("peak"):
        g = g.sort_values("t_h")
        y = g.peak_pos_ms.to_numpy()
        blk = g.power_mW.to_numpy()
        gap = np.zeros(len(y), bool)
        gap[1:] = blk[1:] != blk[:-1]
        step = np.zeros(len(y))
        step[1:] = np.abs(np.diff(y))
        peaks.append(dict(peak=int(peak), y=y, t=g.t_h.to_numpy(),
                          sig=g.sig.to_numpy(), gap=gap, wm=step > 100.0))

    print("\nSTATE-SPACE REFINEMENT (Kalman; interventions = a random walk at the")
    print("gaps; which settles, the drift or the operator, is the 2x2 comparison):")
    out = {}
    for kd in ("const", "exp"):
        for ki in ("const", "exp"):
            out[(kd, ki)] = _ss_fit(peaks, kd, ki)
            print(f"  drift {kd:5s} x interv {ki:5s}: AIC {out[(kd, ki)][2]:7.1f}")
    (kd, ki) = min(out, key=lambda k_: out[k_][2])
    x, nll, _aic = out[(kd, ki)]
    th_d, th_i, sc = _unpack(x, kd, ki)
    d_cc = out[("const", "const")][2] - out[("const", "exp")][2]
    d_ee = out[("exp", "exp")][2] - out[("const", "exp")][2]
    print(f"  best: drift {kd.upper()} x interventions {ki.upper()}"
          f"   (interv settling dAIC {d_cc:+.1f}; adding drift settling {d_ee:+.1f})")

    # profile c by continuation
    prof = {}
    for direction in (1, -1):
        w = np.delete(x, 0)
        for k in range(11):
            cv = th_d[0] + direction * 0.1 * k
            def nllv(wv):
                td2, ti2, s2 = _unpack(np.concatenate([[cv], wv]), kd, ki)
                return _kalman_nll(peaks, kd, td2, ki, ti2, s2)
            o = optimize.minimize(nllv, w, method="Nelder-Mead",
                                  options=dict(xatol=1e-4, fatol=1e-4, maxiter=12000))
            prof[round(cv, 3)] = o.fun
            w = o.x
    ok = [k for k, v in prof.items() if v - nll < 0.5]
    print(f"\n  gaussian-noise drift: {th_d[0]:+.2f} [{min(ok):+.2f}, {max(ok):+.2f}] ms/min (68%)")
    print(f"    -- BIASED HIGH: the residual audit (addendum 7) found three")
    print(f"    end-of-ladder within-block moves this noise model cannot")
    print(f"    represent, absorbed as drift. The mixture stage below is the")
    print(f"    headline; this number is kept as the intermediate it was.")
    if ki == "exp":
        print(f"  THE SETTLING BELONGS TO THE OPERATOR: sig_gap = {th_i[0]:.0f} ms x "
              f"exp(-t/{th_i[1]*60:.0f} min)")
        print(f"    (tau_i spans ~70-160 min across analysis variants -- LOO-4207,")
        print(f"     window-move threshold 60/150 ms -- while c stays within +-0.02;")
        print(f"     early re-centrings ~1-4 MHz laser RMS, late <~0.2 MHz)")
    print(f"  obs-noise scale {sc:.2f} on the block MADs -- effective per-trace noise")
    print(f"  ~1.5-3 ms, consistent with the 1.8 ms jitter figure.")
    print("  This claims the split addendum 4 declined: the earlier tau ~ 73 min")
    print("  exponential was the INTERVENTION amplitude; the drift never settled.")


# ---- the adequate noise model: sparse within-block moves (addendum 7) ------
#
# The Gaussian state space left innovations with skew +1.9 and excess kurtosis
# +7 -- all concentrated in within-block steps at the 25 mW end-of-ladder
# blocks, i.e. rare REAL moves with no model channel, absorbed as drift and
# biasing c high. The fix: within-block transitions carry mixture process
# noise, eta ~ (1-pi_w) delta(0) + pi_w N(0, sigma_m^2), evaluated with a
# collapsed Gaussian-sum filter (exact two-branch likelihood per step,
# moment-matched collapse -- excellent for rare events). After it, the
# mixture-PIT innovations pass Shapiro-Wilk (p ~ 0.3), the observation scale
# drops to ~1.1 (the block MADs were right all along), and the 2x2 structure
# is unchanged while c halves.

def _mix_filter(peaks, c, B, tau, s, pw, sm, q=0.0):
    nll = 0.0
    for p in peaks:
        y = p["y"] - c * p["t"] * 60.0 - q * p.get("P_mw", np.zeros(len(p["y"])))
        m, P_ = 0.0, 1e12
        for i in range(len(y)):
            so = (s * p["sig"][i]) ** 2
            skip = i == 0
            if i > 0 and p["wm"][i]:
                P_ += 1e12; skip = True
            gap_i = i > 0 and not p["wm"][i] and p["gap"][i]
            within = i > 0 and not p["wm"][i] and not p["gap"][i]
            if gap_i:
                tg = 0.5 * (p["t"][i] + p["t"][i - 1])
                P_ += (B * np.exp(-tg / tau)) ** 2
            if within:
                r = y[i] - m
                S0v, S1v = P_ + so, P_ + sm ** 2 + so
                l0 = (1 - pw) * np.exp(-0.5 * r * r / S0v) / np.sqrt(2 * np.pi * S0v)
                l1 = pw * np.exp(-0.5 * r * r / S1v) / np.sqrt(2 * np.pi * S1v)
                L = max(l0 + l1, 1e-300)
                if not skip:
                    nll -= np.log(L)
                w0, w1 = l0 / L, l1 / L
                K0, K1 = P_ / S0v, (P_ + sm ** 2) / S1v
                m0, m1 = m + K0 * r, m + K1 * r
                P0, P1 = P_ * (1 - K0), (P_ + sm ** 2) * (1 - K1)
                m = w0 * m0 + w1 * m1
                P_ = w0 * (P0 + (m0 - m) ** 2) + w1 * (P1 + (m1 - m) ** 2)
                continue
            r = y[i] - m
            Sv = P_ + so
            if not skip:
                nll += 0.5 * (np.log(2 * np.pi * Sv) + r * r / Sv)
            K = P_ / Sv
            m += K * r
            P_ *= (1 - K)
    return nll


def _mix_peaks():
    d = _traces()
    peaks = []
    for peak, g in d.groupby("peak"):
        g = g.sort_values("t_h")
        y = g.peak_pos_ms.to_numpy()
        blk = g.power_mW.to_numpy()
        gap = np.zeros(len(y), bool); gap[1:] = blk[1:] != blk[:-1]
        step = np.zeros(len(y)); step[1:] = np.abs(np.diff(y))
        peaks.append(dict(peak=int(peak), y=y, t=g.t_h.to_numpy(),
                          P_mw=blk.astype(float), sig=g.sig.to_numpy(),
                          gap=gap, wm=step > 100.0))
    return peaks


def _mix_fit(peaks, c_fixed=None, q_mode=None, q_fixed=None):
    """q_mode: None (no pull), 'free', or use q_fixed."""
    def f(v):
        i = 0
        c = c_fixed if c_fixed is not None else v[i]
        i += 0 if c_fixed is not None else 1
        B = np.exp(v[i]); tau = float(np.clip(np.exp(v[i + 1]), .05, 12))
        s = float(np.clip(np.exp(v[i + 2]), .3, 5))
        pw = float(np.clip(1 / (1 + np.exp(-v[i + 3])), 1e-4, .5))
        sm = np.exp(v[i + 4]); i += 5
        q = 0.0
        if q_mode == "free":
            q = v[i]
        elif q_fixed is not None:
            q = q_fixed
        return _mix_filter(peaks, c, B, tau, s, pw, sm, q)
    p0 = ([] if c_fixed is not None else [0.4]) + [np.log(40.), 0., np.log(1.1),
                                                  -2.5, np.log(15.)]
    if q_mode == "free":
        p0 += [0.0]
    p0 = np.array(p0)
    best = None
    for off in (0.0, 0.5, -0.5):
        o = optimize.minimize(f, p0 + off, method="Nelder-Mead",
                              options=dict(xatol=1e-5, fatol=1e-5, maxiter=40000))
        if best is None or o.fun < best.fun:
            best = o
    return best


def mixture_report() -> None:
    peaks = _mix_peaks()
    b = _mix_fit(peaks)
    c0, nll0 = float(b.x[0]), float(b.fun)
    prof = {}
    for cv in np.arange(c0 - 0.45, c0 + 0.5, 0.06):
        prof[round(cv, 3)] = float(_mix_fit(peaks, c_fixed=cv).fun)
    ok68 = [k for k, v in prof.items() if v - nll0 < 0.5]
    ok95 = [k for k, v in prof.items() if v - nll0 < 1.92]
    print("\nMIXTURE REFINEMENT (sparse within-block moves; the adequate noise")
    print("model -- innovations pass Shapiro-Wilk after it, addendum 7):")
    print(f"  c = {c0:+.2f} [{min(ok68):+.2f}, {max(ok68):+.2f}] ms/min (68%)"
          f"   [{min(ok95):+.2f}, {max(ok95):+.2f}] (95%)")
    print(f"    = {c0*RATE_MHZ_MS:+.4f} [{min(ok68)*RATE_MHZ_MS:+.4f}, "
          f"{max(ok68)*RATE_MHZ_MS:+.4f}] MHz/min laser (68%)")
    print(f"  a ~2-sigma POSITIVE INDICATION, no longer a firm detection: the")
    print(f"  gaussian 3-sigma rested on three real end-of-ladder moves absorbed")
    print(f"  as drift. Converges with the segmented floor (+0.19..+0.37) and")
    print(f"  the clean-pair cluster (+0.55 +/- 0.17). Structure unchanged:")
    print(f"  interventions settle (dAIC ~ +17), drift settling buys nothing")
    print(f"  (dAIC ~ +4 against). Persisting, ~{abs(c0)*RATE_MHZ_MS*60*20.5:.0f} MHz laser over 20.5 h.")


def pull_bound_report() -> None:
    """The centre channel, attempted (experimenter's insistence, 2026-07-23).

    The AC-Stark pull (-2/3 S0, S0 = kappa P) is a DIFFERENTIAL centre
    observable: locked to the power ladder, repeated at four different times,
    so it separates from the zero-mean recapture walk (which has no reason to
    follow P) and from drift (which follows elapsed time, not P). Add q*P to
    the state-space observation and profile q. Injection closure (recorded in
    addendum 6): a pull injected at 1x / 4x / 10x the prediction is recovered
    to +-0.0001 ms/mW -- the estimator is unbiased; only the floor limits it.
    """
    d = _traces()
    peaks = []
    for peak, g in d.groupby("peak"):
        g = g.sort_values("t_h")
        y = g.peak_pos_ms.to_numpy()
        blk = g.power_mW.to_numpy()
        gap = np.zeros(len(y), bool); gap[1:] = blk[1:] != blk[:-1]
        step = np.zeros(len(y)); step[1:] = np.abs(np.diff(y))
        peaks.append(dict(y=y, t=g.t_h.to_numpy(), P=blk.astype(float),
                          sig=g.sig.to_numpy(), gap=gap, wm=step > 100.0))

    def nllq(v, q_fixed=None):
        c, lB, lt, ls = v[:4]
        q = q_fixed if q_fixed is not None else v[4]
        B, tau_i = np.exp(lB), float(np.clip(np.exp(lt), 0.05, 12))
        sc = float(np.clip(np.exp(ls), 0.3, 5))
        tot = 0.0
        for p in peaks:
            y = p["y"] - c * p["t"] * 60.0 - q * p["P"]
            m, P_ = 0.0, 1e12
            for i in range(len(y)):
                skip = i == 0
                if i > 0:
                    if p["wm"][i]:
                        P_ += 1e12; skip = True
                    elif p["gap"][i]:
                        tg = 0.5 * (p["t"][i] + p["t"][i - 1])
                        P_ += (B * np.exp(-tg / tau_i)) ** 2
                r = y[i] - m
                S = P_ + (sc * p["sig"][i]) ** 2
                if not skip:
                    tot += 0.5 * (np.log(2 * np.pi * S) + r * r / S)
                K = P_ / S
                m += K * r
                P_ *= (1 - K)
        return tot

    def fitq(q_fixed=None):
        p0 = [0.5, np.log(40.0), 0.0, np.log(1.2)] + ([] if q_fixed is not None else [0.0])
        best = None
        for off in (0.0, 0.5, -0.5):
            o = optimize.minimize(lambda v: nllq(v, q_fixed), np.array(p0) + off,
                                  method="Nelder-Mead",
                                  options=dict(xatol=1e-5, fatol=1e-5, maxiter=20000))
            if best is None or o.fun < best.fun:
                best = o
        return best

    peaks_m = _mix_peaks()
    bq = _mix_fit(peaks_m, q_mode="free")
    q = float(bq.x[-1]); nq0 = float(bq.fun)
    prof = {}
    for direction in (1, -1):
        for k in range(10):
            qv = q + direction * 0.02 * k
            prof[round(qv, 4)] = float(_mix_fit(peaks_m, q_fixed=qv).fun)
    ok95 = [k for k, v in prof.items() if v - min(prof.values()) < 1.92]
    qmax = max(abs(min(ok95)), abs(max(ok95)))
    s0 = qmax * RATE_MHZ_MS * 2 * 225 * 1.5
    print("\nTHE CENTRE CHANNEL, ATTEMPTED (pull bound under the mixture noise")
    print("model; estimator unbiased by injection closure -- addenda 6-7):")
    print(f"  q = {q:+.4f} [{min(ok95):+.3f}, {max(ok95):+.3f}] ms/mW (95%)")
    print(f"  -> S0(225 mW) < {s0:.1f} MHz transition from CENTRES alone --")
    print(f"     ~8x looser than the width channel's < 0.63 (profile), but")
    print(f"     corroborating through disjoint systematics; floor ~9x above")
    print(f"     the 0.59 MHz prediction, so it bounds, not measures. Collisional shift: bridge noise ~8 MHz")
    print(f"     across dwells -> ~1800x above the ~kHz expectation, vacuous.")
    print(f"     Isotope shift: GHz retunes, unlogged, 43 MHz windows --")
    print(f"     nothing bridges, nothing to fit.")


if __name__ == "__main__":
    raise SystemExit(main())
