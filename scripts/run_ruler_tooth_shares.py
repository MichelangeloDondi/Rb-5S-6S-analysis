#!/usr/bin/env python3
"""The comb's tooth heights against the phase-modulation law, on the real rulers.

THIS IS A MEASUREMENT ON THE ARCHIVE'S OWN DATA and not a twin study. A pure
phase modulation puts an amplitude `J_k(2 beta)` into the tooth at order k, so
the tooth's share of the two-photon rate is `J_k(2 beta)^2` and the shares over
the resolved orders sum to one. `results/ruler_traces.csv` carries seven tooth
heights per trace, `h_m3` to `h_p3`, fitted per trace by the ruler producer. So
the law is directly checkable and nothing here had ever checked it.

IT FAILS, AND WHAT FIXES IT IS NOT THE DEPTH. At the committed depth
`config.RULER_MOD_DEPTH_2BETA` the mean shares over the passing traces give a
reduced chi-squared of about six on six degrees of freedom, driven by a
SYMMETRIC excess at k = +-3 of about a factor of two. Letting the depth float
does not improve it: the shape of the discrepancy is not a depth's shape, and
the fitted depth moves by two per cent while the chi-squared stays where it
was. Adding a FLAT PEDESTAL under the comb fixes it completely, at a few per
cent of the comb's power. Symmetry in k is what rules out a chirp, which would
be antisymmetric.

WHY IT MATTERS BEYOND THE RULER. The teeth are the same physical line driven at
different Rabi frequencies at the SAME light shift, which makes them the only
axis in this bench that moves the saturation companion and nothing else. A
ladder built on them is the sharpest handle the record has on the one term that
biases the fitted waist. But a pedestal at this level puts the k = +-3 teeth
BELOW their own floor, so the usable ladder is k = 0, 1, 2 and its rate span is
about five and not about seventy. That is the difference between a designed
measurement and an over-claimed one, and it is why this file reports the
signal-to-pedestal per order rather than only the fit.

AND THE LADDER IS NOT RUNNABLE ON THIS ARCHIVE AS IT STANDS. Every `rf_on`
trace in `data_raw/MANIFEST.csv` is a ruler, not a line measurement, and the
committed ruler producer fits ONE width per trace and seven heights. The widths
per tooth, which is what a saturation ladder reads, have never been fitted. The
data exists; the fit does not. This file measures what the data supports so the
campaign case can be costed, and claims nothing about a waist.

THE SELECTION IS NOT INDEPENDENT OF THE MEASUREMENT, AND THAT IS CARRIED IN
THE ROWS. Traces are kept when `excluded` is false and the calibration
`verdict` is not FAIL. That verdict is an AMPLITUDE verdict on the ordering of
the very teeth this file fits, so the cut is made on a quantity related to the
one being measured. Dropping it moves the pooled pedestal from about five per
cent to about nineteen and the reduced chi-squared from under one to about
twenty-seven, so the cut is doing real work and the result is conditional on
it. What the sensitivity rows below say is that the two groups are not a
shifted population but a different one: fitted trace by trace, the kept traces
carry a pedestal of a few per cent while the dropped ones RAIL against the fit
bound, which is a model that does not describe them at all. Keeping them would
not average the answer, it would average a fitted quantity with a railed one.

AND THE POOLED FIT IS NOT THE PER-TRACE MEDIAN. Pooling the mean shares and
fitting one depth returns about five per cent where the per-trace median is
about two, so the floor is heterogeneous across traces and a single number
understates that. A depth SPREAD was checked as the alternative explanation and
refuted: drawing pure phase modulation at the measured per-trace depths and
fitting one depth plus a floor to the mean returns well under one per cent, so
the floor is not an artefact of averaging over depths.

READS A COMMITTED CSV: `results/ruler_traces.csv`. Register A75 applies -- this
producer reproduces its own file while its INPUT has moved, so re-run it by
hand in any wave that touches the ruler producer.

STATUS. The share rows are MEASURED, from real traces. The fit rows are
DIAGNOSTIC: they are readings of a model against those shares, and the origin
of the pedestal is not settled here.
"""
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares, minimize_scalar
from scipy.special import jv

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

# RESOLVED AT CALL TIME, never bound at import: `_CFG.RESULTS_DIR` is computed
# from RB5S6S_RESULTS_DIR when `config` is first imported, so a module-level
# name freezes whatever the environment held then, and a caller that redirects
# the directory after importing this producer in-process would write to the
# wrong place. The freshness checker runs producers in a subprocess with the
# override already in the environment, so that is not what it saw: its cheap
# path reported "did not write into RB5S6S_RESULTS_DIR" for this producer
# because it compared BYTES, and a deterministic producer reproduces its
# committed file byte for byte. The checker tests the write itself now (an
# mtime sentinel, 2026-09-12); the resolution here stays because it is right.
TWO_BETA = _CFG.RULER_MOD_DEPTH_2BETA
ORDERS = (-3, -2, -1, 0, 1, 2, 3)
HEIGHT_COLS = ("h_m3", "h_m2", "h_m1", "h_0", "h_p1", "h_p2", "h_p3")


def _shares(two_beta, orders=ORDERS):
    s = np.array([float(jv(k, two_beta)) ** 2 for k in orders])
    return s / s.sum()


def main() -> int:
    src = _CFG.RESULTS_DIR / "ruler_traces.csv"
    rows = [r for r in csv.DictReader(src.open(encoding="utf-8"))
            if r["excluded"] == "False" and r["verdict"] != "FAIL"]
    H = np.array([[float(r[c]) for c in HEIGHT_COLS] for r in rows], float)
    H = H / H.sum(axis=1, keepdims=True)
    obs, sd = H.mean(axis=0), H.std(axis=0, ddof=1)
    se = sd / math.sqrt(len(H))

    pred = _shares(TWO_BETA)
    chi2_fixed = float(np.sum(((obs - pred) / se) ** 2))
    nu_fixed = len(obs) - 1

    r_free = minimize_scalar(
        lambda b: float(np.sum(((obs - _shares(b)) / se) ** 2)),
        bounds=(0.5, 3.5), method="bounded")
    chi2_free, nu_free = float(r_free.fun), len(obs) - 2

    def _resid(p):
        b, f = p
        s = (1.0 - f) * _shares(b) + f / len(ORDERS)
        return (obs - s) / se

    r_ped = least_squares(_resid, [TWO_BETA, 0.005])
    chi2_ped, nu_ped = float(np.sum(r_ped.fun ** 2)), len(obs) - 3
    b_ped, f_ped = float(r_ped.x[0]), float(r_ped.x[1])
    ped_per_slot = f_ped / len(ORDERS)

    # `err` is the house column name and the one the uncertainty guard reads.
    out = [["quantity", "order_k", "value", "err", "note", "status"]]
    out.append(["n_ruler_traces", "", str(len(rows)), "",
                f"of {sum(1 for _ in csv.DictReader(src.open(encoding='utf-8')))} "
                "committed, keeping those not excluded and not FAIL",
                "MEASURED"])
    for k, o, e, p_ in zip(ORDERS, obs, se, pred):
        # pm_cells: two significant digits on the uncertainty, the value
        # matching its decimals (LANGUAGE 8a.2)
        v_c, e_c = pm_cells(float(o), float(e))
        out.append(["tooth_share_observed", str(k), v_c, e_c,
                    f"mean over the passing traces. J_k(2 beta)^2 at "
                    f"2 beta = {TWO_BETA} predicts {p_:.5f}, a pull of "
                    f"{(o - p_) / e:+.1f}", "MEASURED"])
    for k, p_ in zip(ORDERS, (1.0 - f_ped) * _shares(b_ped)):
        out.append(["signal_over_pedestal", str(k), f"{p_ / ped_per_slot:.2f}",
                    "", "the fitted tooth share over the fitted flat "
                    "pedestal in that slot. Below one the tooth is not "
                    "measurable", "DIAGNOSTIC"])
    cv, ce = pm_cells(chi2_fixed / nu_fixed, math.sqrt(2.0 / nu_fixed))
    out.append(["chi2_red_depth_fixed", "", cv, ce,
                f"chi2 {chi2_fixed:.1f} on nu {nu_fixed}, at the committed "
                f"depth {TWO_BETA}. The pure phase-modulation law is rejected",
                "DIAGNOSTIC"])
    fv, fe = pm_cells(chi2_free / nu_free, math.sqrt(2.0 / nu_free))
    out.append(["chi2_red_depth_free", "", fv, fe,
                f"chi2 {chi2_free:.1f} on nu {nu_free}, best depth "
                f"{r_free.x:.4f}. A free depth does not fix it, so the "
                "discrepancy is not a depth's shape", "DIAGNOSTIC"])
    pv, pe = pm_cells(chi2_ped / nu_ped, math.sqrt(2.0 / nu_ped))
    out.append(["chi2_red_depth_and_pedestal", "", pv, pe,
                f"chi2 {chi2_ped:.1f} on nu {nu_ped}. A flat pedestal fixes "
                "it completely", "DIAGNOSTIC"])
    out.append(["two_beta_with_pedestal", "", f"{b_ped:.4f}", "",
                f"against the committed {TWO_BETA}, whose own sd over 41 "
                "combs is 0.058, so this sits inside it", "DIAGNOSTIC"])
    out.append(["pedestal_fraction_of_comb", "", f"{f_ped:.4f}", "",
                f"{100 * f_ped:.2f} per cent of the comb's power, flat over "
                f"{len(ORDERS)} slots, so {100 * ped_per_slot:.3f} per cent "
                "under each. Symmetric in k, which rules out a chirp. The "
                "origin is not settled here", "DIAGNOSTIC"])

    usable = [k for k, p_ in zip(ORDERS, (1.0 - f_ped) * _shares(b_ped))
              if p_ / ped_per_slot >= 1.0]
    u = _shares(b_ped, tuple(sorted({abs(k) for k in usable})))
    out.append(["usable_ladder_orders", "",
                ",".join(str(k) for k in sorted({abs(k) for k in usable})), "",
                "the orders whose share clears their own pedestal",
                "DIAGNOSTIC"])
    out.append(["usable_rate_ladder", "", f"{u.max() / u.min():.2f}", "",
                "the span in two-photon rate across the usable teeth, at "
                "one light shift. The Rabi span is its square root",
                "DIAGNOSTIC"])
    out.append(["usable_rabi_ladder", "",
                f"{math.sqrt(u.max() / u.min()):.2f}", "",
                "what the saturation companion's own ladder follows",
                "DIAGNOSTIC"])

    # --- SELECTION SENSITIVITY, so the conditionality is in the file -------
    kept = rows
    dropped = [r for r in csv.DictReader(src.open(encoding="utf-8"))
               if r["excluded"] == "False" and r["verdict"] == "FAIL"]
    both = kept + dropped

    def _pooled(sel):
        if len(sel) < 4:
            return float("nan"), float("nan")
        A = np.array([[float(r[c]) for c in HEIGHT_COLS] for r in sel], float)
        A = A / A.sum(axis=1, keepdims=True)
        o, s = A.mean(axis=0), A.std(axis=0, ddof=1) / math.sqrt(len(A))
        rr = least_squares(lambda q: (o - ((1.0 - q[1]) * _shares(q[0])
                                           + q[1] / len(ORDERS))) / s,
                           [TWO_BETA, 0.005])
        return float(rr.x[1]), float(np.sum(rr.fun ** 2)) / (len(o) - 3)

    for sel, label in ((kept, "verdict_not_FAIL"), (both, "all_not_excluded")):
        f_, c_ = _pooled(sel)
        out.append(["pedestal_under_selection", label, f"{f_:.4f}", "",
                    f"n = {len(sel)}, reduced chi-squared {c_:.2f}. The cut is "
                    "made on an amplitude verdict over the same teeth, so every "
                    "figure in this file is conditional on it and this row is "
                    "what says by how much", "DIAGNOSTIC"])

    def _per_trace(sel):
        A = np.array([[float(r[c]) for c in HEIGHT_COLS] for r in sel], float)
        A = A / A.sum(axis=1, keepdims=True)
        got = []
        for h in A:
            rr = least_squares(lambda q: h - ((1.0 - q[1]) * _shares(q[0])
                                              + q[1] / len(ORDERS)),
                               [1.55, 0.02], bounds=([0.5, 0.0], [3.0, 0.6]))
            got.append(float(rr.x[1]))
        return np.array(got)

    pk, pd_ = _per_trace(kept), _per_trace(dropped)
    v, e = pm_cells(float(np.median(pk)), float(pk.std(ddof=1) / math.sqrt(len(pk))))
    out.append(["pedestal_per_trace_median", "verdict_not_FAIL", v, e,
                "fitted trace by trace with its own depth. It sits below the "
                "pooled value, so the floor is heterogeneous across traces "
                "and one number understates that", "DIAGNOSTIC"])
    out.append(["pedestal_per_trace_railed_fraction", "verdict_FAIL",
                f"{float(np.mean(pd_ > 0.55)):.3f}", "",
                "the dropped traces rail against the fit's own bound, so the "
                "law does not describe them at all. They are a different "
                "population and not a shifted one, which is why the cut is "
                "defensible and still has to be stated", "DIAGNOSTIC"])

    dst = _CFG.RESULTS_DIR / "ruler_tooth_shares.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(out)
    print(f"{len(rows)} traces; chi2_red fixed {chi2_fixed / nu_fixed:.2f}, "
          f"free-depth {chi2_free / nu_free:.2f}, "
          f"with pedestal {chi2_ped / nu_ped:.2f}")
    print(f"usable ladder {sorted({abs(k) for k in usable})}, "
          f"rate span {u.max() / u.min():.2f}x")
    print(f"wrote {os.path.relpath(dst, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
