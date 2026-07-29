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

THE DESIGN CONSEQUENCE, which is what this is for. The existing lesson -- cycle
or randomise the power ordering, so drift is orthogonal to the pull -- is
necessary and now demonstrably not sufficient. A second requirement joins it:
DO NOT MOVE THE SCOPE'S HORIZONTAL POSITION during a session, and if it must
move, record it, because every move severs the centre record. Both cost nothing
but the order and discipline of knob turns.

Outputs: results/stark_centres.csv (one row per drift form).
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

REPO = Path("/Users/michelangelodondi/Documents/GitHub/Rb-5S-6S-analysis")
sys.path.insert(0, str(REPO))

RATE = 0.04257061052233977          # MHz/ms, laser axis (M2)
MEAN_OVER_S0 = -0.653               # archival ramp geometry, methods/03
WIDTH_BOUND = 0.633                 # MHz, the width channel's 95% bound
PREDICTED = 0.59                    # MHz, S0(225 mW) predicted

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

RES = REPO / "results" / "stark_centres.csv"
with open(RES, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)
print(f"wrote {RES.name}: {len(out_rows)} drift models")
print("  the pull's SIGN flips between linear and exponential and the bound "
      "degrades as the\n  drift model gains freedom -- an unidentifiable "
      "parameter. The centre channel is a NULL.")
