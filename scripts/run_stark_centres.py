#!/usr/bin/env python3
"""
Can the CENTRES yield the AC-Stark shift? No, and the knob is why (M21).

The question was answered once before, in M20's docstring, as
|S0(225 mW)| < 7.3 MHz -- computed on session-referenced peak positions, which
were the scope's horizontal setting rather than the laser (see
run_laser_history.py's retraction). This module re-asks it on a defensible
model and reports the answer as a producer, because the result is a NULL that
the paper has to state rather than a number it can use.

THE MODEL is the one the experimenter proposed: put a free offset on every
display epoch -- which is exactly "the re-kicks as extra free parameters",
since an epoch boundary IS a horizontal-knob move and the offset across it is
unknown -- then fit a shared drift and a shared pull on top. Three drift forms,
because a smooth settling curve is shaped differently from a piecewise-constant
power schedule and might separate from it:

    linear      d * tau                                    (tau = min into epoch)
    exp         A * (1 - exp(-tau_abs / T))                (tau_abs = min into run)
    exp2        A1*(1-exp(-tau_abs/T1)) + A2*(1-exp(-tau_abs/T2))

WHY IT FAILS, sharply. Of 26 display epochs covering the power sweep, only THREE
contrast two powers at all (75/125, 175/225, 175/225 -- each a 50 mW step), and
no epoch spans two lines. Inside those three, power still DESCENDS with time,
because that is how the campaign was run. So drift and pull stay collinear at
every scale: the linear fit returns them 94% correlated.

The result, and the shape of it is the argument:

    linear   pull +3.45  95% [-6.9, +13.8] MHz/W  ->  |S0(225)| < 9.50 MHz
    exp      pull -3.26  95% [-6.5, +21.2]        ->  |S0(225)| < 14.59 MHz
    exp2     pull -3.21  95% [-14.4, +25.6]       ->  |S0(225)| < 17.67 MHz

The sign FLIPS between linear and exponential, and the bound degrades
monotonically as the drift model gains freedom. That is an unidentifiable
parameter, not a marginally measured one. Against the width channel's
S0(225 mW) < 0.633 MHz the best of these is 15x weaker.

Note the direction of the correction: handling the knob CORRECTLY makes the
bound worse than the retracted 7.3 MHz, because the free epoch offsets remove
cross-block leverage the old number was borrowing from comparisons that were not
valid. A tighter number is not a better one.

A SECOND, STRONGER ATTEMPT, AND WHY IT ALSO FAILS (2026-07-30). The free-offset
model above throws away the fact that the horizontal setting is RECORDED. A knob
move shifts peak_pos_ms and window_start_ms together, so

    rel = (peak_pos_ms - window_start_ms) * rate

should be invariant under the move and vary only with the laser. It does collapse
the scatter of the 158 canonical science traces from 7.75 MHz sd to 0.28 MHz over
20.5 h -- a factor 28, reproduced independently -- and restores the campaign as
one continuous record. Fitting rel = c_peak + pull*P on the 99 canonical p_sweep
traces returns S0(225 mW) = +0.894 +- 0.274 MHz, apparently 3.3 sigma, with the
four lines agreeing at chi2/dof = 1.27 and residuals showing no trend in time.

It is not a detection, for four reasons, and the FIRST is the one that should
have been tested before any of the drift modelling:

1. THE PULL'S OWN SHAPE IS REJECTED. An AC-Stark shift is linear in P by
   construction. Replacing pull*P with four free power-level offsets gives
   F(3, 91) = 4.48, p = 0.0055, and the rung means are not monotone --
   +0.243 MHz at 25 mW, then -0.088, -0.050, +0.025, -0.137 at 75 to 225 mW.
   The HIGHEST power, where the shift must be largest, sits above 125 and 175.
   That is a one-level step, not a pull. Five drift forms were tested here
   before the signal's own mandatory form ever was.
2. THE WHOLE EFFECT IS THE BOTTOM RUNG. Dropping 25 mW: S0 = +0.100 +- 0.222,
   0.45 sigma, over a threefold power range. Three of the four lines change
   sign. And 25 mW is the worst rung to lean on -- SNR 18 against 193 at
   225 mW, residual scatter 4.6x larger, and the only level at which the
   triangular sweep's RETRACE produces a second above-half-max region (8 of its
   20 traces, against 0 of the other 79).
3. THE SIGMA IS INFLATED BY REPLICATES. The 99 traces are 20 conditions of ~5
   repeats saved seconds apart; the residual intraclass correlation is 0.38, a
   design effect of 2.5. Cluster-robust on 20 blocks gives p = 0.077, a block
   bootstrap gives a 95% interval of [-0.31, +1.86] that includes zero, and a
   structure-preserving permutation test gives p = 0.086. Every honest variance
   treatment lands at 1.6-1.9 sigma.
4. THE CONSTRUCTION IS NOT LICENSED. The retraction established that the knob is
   not a PROXY for drift. This use needs the strictly stronger claim that it is
   not a RESPONSE to drift, and the archive cannot decide between them: the
   licensing regression d(peak_pos)/d(window_start) = 1.005 +- 0.009 is predicted
   equally by "the knob relabels the axis" and by "the line moved and the
   operator followed it", 64% of its leverage sits on a single event, and no
   knob-immune reference was exported -- the triangle ramp was on scope CH1
   (APPARATUS section 1) and only CH2 was saved.

What is worth keeping from the attempt: the centre estimator is NOT the problem.
Five independent estimators -- smoothed argmax, above-half centroid, half-max
midpoint, parabolic top, and full Gaussian least squares on the raw trace with a
linear background -- all return +0.88 to +0.91 MHz, and the baseline-tilt
displacement of the mode is 3e-4 MHz against a 0.27 MHz residual. The unit chain
(laser-to-transition factor 2, ramp first moment -0.653) was also checked end to
end and is correct.

THE DESIGN CONSEQUENCE, which is what this is for. The existing lesson -- cycle
or randomise the power ordering, so drift is orthogonal to the pull -- is
necessary and now demonstrably not sufficient. (The 2025-07-04 LeCroy dress
rehearsal already ran its ladders in ALTERNATING directions -- descending on
4192, ascending on 4207 and 4121 -- which is exactly this design; what wasted
it there was the scope auto-triggering, so the sweep phase is random per
trace and the centres carry no frequency anyway. M23 uses the rehearsal's
shapes and widths instead; the centre channel stays dead in both sessions,
each for its own missing reference.) A second requirement joins it:
DO NOT MOVE THE SCOPE'S HORIZONTAL POSITION during a session, and if it must
move, record it, because every move severs the centre record. Both cost nothing
but the order and discipline of knob turns.

A third joins them, and it is the cheapest of the three: EXPORT THE RAMP MONITOR.
The triangle drive was already on scope CH1 and only CH2 was saved, which is why
the knob-immune construction above cannot be licensed -- with the ramp channel in
the file, the time origin is fixed independently of both the knob and the laser
and the question answers itself. One extra column.

And a fourth, from the bottom rung: DO NOT PUT THE LOWEST POWER AT THE END OF A
DESCENDING LADDER. At 25 mW the line is weak enough that the sweep retrace makes
a second above-half-max region in 8 of 20 traces, and being last it is also the
most drifted. Cycling the power ordering fixes both at once.

Outputs: results/stark_centres.csv (one row per drift form).
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402

MEAN_OVER_S0 = -0.653               # archival ramp geometry, methods/03
# All three READ from the pipeline rather than hand-typed (v3.0.0, extended
# 2026-08-01): the rate from M2's committed CSV, the width bound from M4e's,
# the prediction from the constants. They used to be literals and went stale
# together whenever the priors (or the rate) moved.
RATE = float(next(csv.DictReader(
    open(REPO / "results/ruler_campaign.csv")))["rate_laser"])  # MHz/ms, laser
WIDTH_BOUND = float(next(
    r["value"] for r in csv.DictReader(open(REPO / "results/stark_sweep.csv"))
    if r["quantity"] == "S0_225mW_ub95_profile"))   # MHz, width channel 95%
PREDICTED = stark_shift_S0_mhz(0.225, C.W0_MEASURED_M, rho=C.RHO_RETRO)  # MHz

rows = [r for r in csv.DictReader(open(REPO / "results/laser_history.csv"))]
sci = [r for r in rows if r["role"] == "p_sweep" and r["flag"] == "canonical"]
eps = sorted({r["display_epoch"] for r in sci}, key=int)
ei = {e: i for i, e in enumerate(eps)}
t_first = min(int(r["t_epoch"]) for r in sci)
t0 = {e: min(int(r["t_epoch"]) for r in sci if r["display_epoch"] == e) for e in eps}

E = np.array([ei[r["display_epoch"]] for r in sci])
TAU = np.array([(int(r["t_epoch"]) - t0[r["display_epoch"]]) / 60.0 for r in sci])
TABS = np.array([(int(r["t_epoch"]) - t_first) / 60.0 for r in sci])
P = np.array([float(r["power_mW"]) / 1000.0 for r in sci])       # W
Y = np.array([float(r["peak_pos_ms"]) * RATE for r in sci])      # MHz, laser
NE = len(eps)


def model(theta, kind):
    """theta = [offsets(NE), pull, *drift]"""
    off, pull, rest = theta[:NE], theta[NE], theta[NE + 1:]
    mu = off[E] + pull * P
    if kind == "linear":
        mu = mu + rest[0] * TAU
    elif kind == "exp":
        A, T = rest[0], abs(rest[1]) + 1e-6
        mu = mu + A * (1.0 - np.exp(-TABS / T))
    elif kind == "exp2":
        A1, T1, A2, T2 = rest[0], abs(rest[1]) + 1e-6, rest[2], abs(rest[3]) + 1e-6
        mu = mu + A1 * (1 - np.exp(-TABS / T1)) + A2 * (1 - np.exp(-TABS / T2))
    return mu


def fit(kind, pull_fixed=None):
    n_extra = {"linear": 1, "exp": 2, "exp2": 4}[kind]
    x0 = np.concatenate([np.full(NE, Y.mean()), [0.0],
                         {"linear": [0.0], "exp": [0.0, 10.0],
                          "exp2": [0.0, 3.0, 0.0, 60.0]}[kind]])

    def resid(free):
        th = free.copy()
        if pull_fixed is not None:
            th = np.concatenate([free[:NE], [pull_fixed], free[NE:]])
        return model(th, kind) - Y

    if pull_fixed is not None:
        x0 = np.concatenate([x0[:NE], x0[NE + 1:]])
    r = least_squares(resid, x0, method="lm", max_nfev=200000)
    return r, n_extra


print(f"{len(sci)} p_sweep canonical traces, {NE} display epochs "
      f"({NE} free offsets = the knob moves)")
print(f"powers present per epoch: "
      f"{sum(1 for e in eps if len({r['power_mW'] for r in sci if r['display_epoch']==e})>1)}"
      f" epochs contrast two powers\n")

out_rows = []
for kind in ("linear", "exp", "exp2"):
    r, n_extra = fit(kind)
    dof = len(Y) - (NE + 1 + n_extra)
    chi2 = float(r.fun @ r.fun)
    s = np.sqrt(chi2 / dof)
    pull = r.x[NE]
    # profile likelihood on the pull: scan until chi2 rises by the 95% 1-dof step
    lo = hi = pull
    step = max(0.5, abs(pull) * 0.5)
    for sign in (-1, +1):
        v = pull
        while abs(v - pull) < 400:
            v += sign * step
            rr, _ = fit(kind, pull_fixed=v)
            if float(rr.fun @ rr.fun) - chi2 > 3.841 * (chi2 / dof):
                break
        if sign < 0:
            lo = v
        else:
            hi = v
    s0 = 2 * pull * 0.225 / MEAN_OVER_S0
    s0_lo = 2 * lo * 0.225 / MEAN_OVER_S0
    s0_hi = 2 * hi * 0.225 / MEAN_OVER_S0
    ub = max(abs(s0_lo), abs(s0_hi))
    print(f"[{kind}]  dof={dof}  residual {s:.4f} MHz")
    print(f"   pull = {pull:+.3f}  95% profile [{lo:+.2f}, {hi:+.2f}] MHz/W (laser)")
    print(f"   S0(225 mW) = {s0:+.2f}  95% [{min(s0_lo,s0_hi):+.2f}, "
          f"{max(s0_lo,s0_hi):+.2f}] MHz -> |S0| < {ub:.2f} MHz")
    print(f"   vs width channel {WIDTH_BOUND} MHz, prediction {PREDICTED} MHz "
          f"-> {ub/WIDTH_BOUND:.0f}x weaker\n")
    out_rows.append({"drift_model": kind, "n_traces": len(Y), "n_epochs": NE,
                     "dof": dof, "resid_mhz": round(s, 5),
                     "pull_mhz_per_w_laser": round(pull, 4),
                     "pull_lo95": round(lo, 4), "pull_hi95": round(hi, 4),
                     "S0_225mW_mhz": round(s0, 4),
                     "S0_lo95": round(min(s0_lo, s0_hi), 4),
                     "S0_hi95": round(max(s0_lo, s0_hi), 4),
                     "S0_abs_ub95": round(ub, 4),
                     "width_channel_bound_mhz": WIDTH_BOUND,
                     "times_weaker_than_width": round(ub / WIDTH_BOUND, 2)})

# ---- the knob-immune check, and the test that actually decides it ----------
# rel = (peak_pos - window_start) removes the horizontal setting exactly, so it
# is the strongest form the centre channel can take. Its power dependence is
# then asked the ONE question a pull must answer: is it linear in P?
S = np.array([float(r["window_start_ms"]) for r in sci])
REL = (np.array([float(r["peak_pos_ms"]) for r in sci]) - S) * RATE
PMW = np.array([float(r["power_mW"]) for r in sci])
NL = len(set(E))
KL = E


def _ls(X, y):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ b
    return b, float(r @ r)


nrow = len(REL)
peaks = sorted({r["peak"] for r in sci})
kp = np.array([peaks.index(r["peak"]) for r in sci])
X_lin = np.zeros((nrow, len(peaks) + 1))
X_lin[np.arange(nrow), kp] = 1.0
X_lin[:, -1] = PMW / 1000.0
b_lin, rss_lin = _ls(X_lin, REL)

levels = sorted(set(PMW))
X_fac = np.zeros((nrow, len(peaks) + len(levels) - 1))
X_fac[np.arange(nrow), kp] = 1.0
for i, v in enumerate(PMW):
    j = levels.index(v)
    if j > 0:
        X_fac[i, len(peaks) + j - 1] = 1.0
_, rss_fac = _ls(X_fac, REL)

df_lin = nrow - (len(peaks) + 1)
df_fac = nrow - (len(peaks) + len(levels) - 1)
F = ((rss_lin - rss_fac) / (df_lin - df_fac)) / (rss_fac / df_fac)
try:
    from scipy import stats as _st
    pF = float(_st.f.sf(F, df_lin - df_fac, df_fac))
except Exception:
    pF = float("nan")

keep = PMW > min(levels)
Xk = np.zeros((int(keep.sum()), len(peaks) + 1))
Xk[np.arange(int(keep.sum())), kp[keep]] = 1.0
Xk[:, -1] = PMW[keep] / 1000.0
bk, rssk = _ls(Xk, REL[keep])
dofk = int(keep.sum()) - (len(peaks) + 1)
cvk = np.linalg.pinv(Xk.T @ Xk) * (rssk / dofk)
s0_drop = 2 * bk[-1] * 0.225 / MEAN_OVER_S0
s0_drop_e = abs(2 * np.sqrt(cvk[-1, -1]) * 0.225 / MEAN_OVER_S0)
s0_all = 2 * b_lin[-1] * 0.225 / MEAN_OVER_S0

print("knob-immune variable (peak_pos - window_start):")
print(f"  sd {REL.std(ddof=1):.3f} MHz on {nrow} p_sweep traces")
print(f"  S0(225) all five rungs        {s0_all:+.3f} MHz")
print(f"  linear-in-P vs rung-as-factor F({df_lin-df_fac},{df_fac}) = {F:.2f}, "
      f"p = {pF:.4f}   <- a pull MUST be linear in P")
print(f"  S0(225) dropping the {min(levels):.0f} mW rung  {s0_drop:+.3f} "
      f"+- {s0_drop_e:.3f} MHz ({abs(s0_drop/s0_drop_e):.2f} sigma)")
print("  -> the apparent effect is a step at the bottom rung, not a pull")

out_rows.append({"drift_model": "knob_immune_linearity", "n_traces": nrow,
                 "n_epochs": NL, "dof": df_fac,
                 "resid_mhz": round(float(np.sqrt(rss_fac / df_fac)), 5),
                 "pull_mhz_per_w_laser": round(float(b_lin[-1]), 4),
                 "pull_lo95": "", "pull_hi95": "",
                 "S0_225mW_mhz": round(float(s0_all), 4),
                 "S0_lo95": round(float(s0_drop - 2 * s0_drop_e), 4),
                 "S0_hi95": round(float(s0_drop + 2 * s0_drop_e), 4),
                 "S0_abs_ub95": round(float(abs(s0_drop) + 2 * s0_drop_e), 4),
                 "width_channel_bound_mhz": WIDTH_BOUND,
                 "times_weaker_than_width": round(
                     (abs(s0_drop) + 2 * s0_drop_e) / WIDTH_BOUND, 2),
                 "linearity_F": round(float(F), 3),
                 "linearity_p": round(pF, 5),
                 "S0_drop_lowest_rung": round(float(s0_drop), 4),
                 "S0_drop_lowest_rung_err": round(float(s0_drop_e), 4)})

RES = REPO / "results" / "stark_centres.csv"
with open(RES, "w", newline="") as f:
    cols = list(out_rows[-1].keys())
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(out_rows)
print(f"wrote {RES.name}: {len(out_rows)} drift models")
print("  the pull's SIGN flips between linear and exponential and the bound "
      "degrades as the\n  drift model gains freedom -- an unidentifiable "
      "parameter. The centre channel is a NULL.")
