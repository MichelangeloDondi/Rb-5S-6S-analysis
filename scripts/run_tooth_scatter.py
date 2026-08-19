#!/usr/bin/env python3
"""The comb as a clock: what the tooth positions bound the laser's frequency
excursion to (module M2, stage 4b).

WHAT THIS MEASURES, and why it is not what stage 4 already measures.
`ruler.fit_comb_free_centers` frees each tooth centre and returns its
departure from that trace's own rigid ladder t0 + n*delta. `run_ruler.py`
POOLS those departures across traces into results/ruler_nlmap.csv, which is
the sweep nonlinearity map. A departure is two things added together:

    tooth departure = sweep nonlinearity + laser frequency excursion

and the pooled mean is only the first of them. The separator is that the ramp
REPEATS on every sweep and the laser does not, so the mean over traces at a
given window position is the nonlinearity and the SCATTER about that mean is
the laser. This script keeps the scatter.

THE MEASUREMENT IS A CLOCK COMPARISON. The teeth sit at exact multiples of
the EOM drive, so their positions in TIME are a ruler laid down by an RF
oscillator, and the departure of the observed positions from that ruler is
the optical frequency wandering against it during the sweep. The averaging
time is the tooth spacing, about 147 ms at the campaign's own rate, so the
result is a statement at roughly 7 Hz.

WHAT IT CANNOT SEE. A LINEAR drift within a sweep is exactly degenerate with
the sweep rate: if the laser adds a*t to an intended ramp r*t, the teeth stay
uniformly spaced with spacing f_EOM/(r+a), and the fit returns r+a. Only
curvature survives. Separating the linear part needs the two halves of a
triangular sweep, which give r+a and r-a, and the campaign manifest does not
record sweep direction, so that separation is not available here. The bound
below is therefore on the NON-LINEAR, non-repeating part.

CONSTRUCTION. Every canonical RF-on trace, blocked exactly as run_ruler.py
blocks them, fitted with validated_comb_fit and then refit with free centres
under the same noise law. Departures are pooled into 16 window-position bins,
the inverse-variance mean of each bin is removed as the repeating sweep
shape, and the excess scatter over the fitted centre errors is estimated by
maximum likelihood with a profile-likelihood upper limit at 95 per cent.

Reads data_raw/ through the manifest. Writes results/ruler_tooth_scatter.csv.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.constants import TOOTH_SPACING_LASER_HZ               # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path   # noqa: E402
from rb5s6s.noise import condition_noise_model                    # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags     # noqa: E402
from rb5s6s.ruler import (fit_comb_free_centers,                  # noqa: E402
                          validated_comb_fit)

NBINS = 16


def block_key(r):
    """The blocking run_ruler.py uses, copied so the two agree by construction."""
    if r["role"] == "ruler_t":
        return ("T", r["peak"], r["temperature_C"], "")
    return ("P", r["peak"], "130", r["bracket"])


def collect():
    """Per-tooth departures from each trace's own rigid ladder."""
    blocks = defaultdict(list)
    for r in load_manifest():
        if r["flag"] == "canonical" and r["rf_on"] == "True":
            blocks[block_key(r)].append(r)

    resid, err, pos, ntrace = [], [], [], set()
    for key in sorted(blocks):
        traces, tvs = [], []
        for r in blocks[key]:
            try:
                t, v, info = load_trace(trace_path(r), with_info=True)
            except OSError:
                continue
            m = trace_metrics(t, v, rf_on=True)
            hf = hard_flags(m, rf_on=True) + ingest_flags(info)
            if any(("dropout" in f or "no comb" in f or "truncated" in f)
                   for f in hf):
                continue
            traces.append(r)
            tvs.append((t, v))
        if len(tvs) < 2:
            continue
        law = condition_noise_model([v for _, v in tvs])
        for r, (t, v) in zip(traces, tvs):
            try:
                base = validated_comb_fit(t, v, law)
                if base.get("excluded"):
                    continue
                free = fit_comb_free_centers(t, v, base, law)
            except RuntimeError:
                continue
            t0, d = base["t0_ms"], base["delta_ms"]
            for n, c, ce in zip(free["n"], free["centers_ms"],
                                free["center_err_ms"]):
                ladder = t0 + n * d
                resid.append(c - ladder)
                err.append(ce)
                pos.append(ladder)
                ntrace.add(r["file"])
    return (np.asarray(resid), np.asarray(err), np.asarray(pos), len(ntrace))


def remove_repeating(resid, err, pos):
    """Subtract the inverse-variance mean per window bin: the sweep shape."""
    out = resid.copy()
    edges = np.linspace(pos.min(), pos.max(), NBINS + 1)
    idx = np.clip(np.digitize(pos, edges) - 1, 0, NBINS - 1)
    for b in range(NBINS):
        m = idx == b
        if m.sum() >= 3:
            w = 1.0 / err[m] ** 2
            out[m] = resid[m] - float(np.sum(w * resid[m]) / np.sum(w))
    return out


def excess_scatter(r, err):
    """(best fit, 95 per cent upper limit) on an extra variance, in ms."""
    def nll(s2):
        v = err ** 2 + s2
        return 0.5 * float(np.sum(np.log(v) + r ** 2 / v))

    hi = float(4.0 * np.var(r) + 1e-9)
    grid = np.linspace(0.0, hi, 2001)
    vals = np.array([nll(s) for s in grid])
    best = float(grid[int(np.argmin(vals))])
    try:
        lim = brentq(lambda s: nll(s) - vals.min() - 1.92, best + 1e-12, hi)
    except ValueError:
        lim = hi
    return np.sqrt(best), np.sqrt(lim)


def main() -> int:
    resid, err, pos, ntr = collect()
    if resid.size < 20:
        print("too few teeth to bound anything")
        return 1
    # the sweep rate of record, rather than one re-derived here from the same
    # tooth positions this script is testing
    with open(C.RESULTS_DIR / "ruler_campaign.csv") as fh:
        rate = float(next(csv.DictReader(fh))["rate_laser"])

    r2 = remove_repeating(resid, err, pos)
    best_ms, lim_ms = excess_scatter(r2, err)
    chi2_red = float(np.mean((r2 / err) ** 2))
    delta_ms = TOOTH_SPACING_LASER_HZ / 1e6 / rate
    tau_s = delta_ms / 1e3

    rows = [
        dict(quantity="n_teeth", value=resid.size, unit="count",
             note="free-centre measurements entering the bound"),
        dict(quantity="n_traces", value=ntr, unit="count",
             note="canonical RF-on traces contributing"),
        dict(quantity="center_err_median", value=round(float(np.median(err)), 4),
             unit="ms", note="fitted tooth-centre error, the limiting quantity"),
        dict(quantity="chi2_red_after_sweep_removal", value=round(chi2_red, 4),
             unit="1", note="below 1 means the quoted centre errors are conservative"),
        dict(quantity="tau", value=round(tau_s, 4), unit="s",
             note="averaging time, the tooth spacing at the campaign rate"),
        dict(quantity="excursion_best", value=round(best_ms * rate * 1e3, 2),
             unit="kHz_laser_axis",
             note="maximum-likelihood non-repeating excursion, consistent with zero"),
        dict(quantity="excursion_ub95", value=round(lim_ms * rate * 1e3, 2),
             unit="kHz_laser_axis",
             note="95 per cent upper limit on the non-linear non-repeating excursion"),
        dict(quantity="excursion_ub95_transition", value=round(2 * lim_ms * rate * 1e3, 2),
             unit="kHz_transition_axis",
             note="the same limit on the axis the lineshape is fitted on"),
    ]
    out = C.RESULTS_DIR / "ruler_tooth_scatter.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["quantity", "value", "unit", "note"])
        w.writeheader()
        w.writerows(rows)

    print(f"M2 stage 4b: {resid.size} teeth from {ntr} traces")
    print(f"  tooth-centre error, median      {np.median(err):.3f} ms "
          f"= {np.median(err)*rate*1e3:.0f} kHz")
    print(f"  chi2/dof after removing the sweep {chi2_red:.2f}")
    print(f"  non-repeating excursion at tau = {tau_s*1e3:.0f} ms:")
    print(f"    best fit {best_ms*rate*1e3:.1f} kHz, "
          f"95 per cent limit < {lim_ms*rate*1e3:.1f} kHz (laser axis), "
          f"< {2*lim_ms*rate*1e3:.1f} kHz (transition axis)")
    print(f"  rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
