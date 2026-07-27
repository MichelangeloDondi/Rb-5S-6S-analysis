#!/usr/bin/env python3
"""
Reconstruct the laser's frequency history from the traces (module M20)
=====================================================================

The 2025 campaign ran on a drifting, hand re-centred lock and no wavemeter log
survives. That is usually stated as a loss. It is recoverable, because every
trace carries the information: the line sits wherever the laser happened to be
within the sweep, so the FITTED PEAK POSITION IS THE LASER'S FREQUENCY OFFSET,
in units the EOM ruler converts to MHz. Joined to the recovered acquisition
clock, the 297 traces become a ~22-hour record of what the laser did.

    offset(MHz) = (peak_pos_ms - <peak_pos_ms>_session) * rate_campaign

with rate_campaign = 0.04257(5) MHz/ms, laser axis (M2, results/ruler_campaign).
The per-session mean is subtracted because the ABSOLUTE frequency is exactly
what this archive cannot supply -- only the excursions are reconstructed, which
is the same limitation the rest of the analysis carries.

WHAT THIS IS FOR, and it is not decoration.

1. IT IS A FALSIFIABLE PREDICTION, not a summary. Every point is a statement
   about where the laser was at a wall-clock instant, derived from the atoms and
   the file timestamps alone. If the original wavemeter logs are ever recovered,
   this curve can be compared to them point by point -- an out-of-sample test of
   the whole chain at once: the EOM ruler calibration, the mtime-to-acquisition
   assumption, and the peak extraction. It can fail. Nothing else in the repo
   tests those three together.

2. IT TRANSFERS TO THE FIXED-LOCK SESSION AS A CHARACTERISATION TOOL. Run live
   in 2026, the same reconstruction measures the SCAN SYSTEM rather than the
   atoms. The specific target is an effect observed at the bench but never
   quantified: the sweep amplitude falls as the sweep speed rises -- the piezo
   and its driver rolling off. Mapping amplitude against sweep frequency at
   fixed drive gives the corner frequency and any mechanical resonance.

3. AND THAT ROLL-OFF IS A SYSTEMATIC, not just a curiosity. If the optical span
   depends on sweep speed, then MHz/ms depends on sweep speed, and any campaign
   that changes the sweep rate while assuming one frequency calibration
   mis-scales every linewidth it reports. This archive is protected by accident
   -- the EOM ruler measured the rate per block rather than assuming it -- but
   the protection is invisible until the roll-off is characterised, and a future
   experimenter has no way to know how fast is too fast.

IS THE RECONSTRUCTION REAL? Yes, and it is tested here rather than asserted. A
curve like this could be nothing but per-trace scatter dressed up as history, so
`structure_function` measures how the disagreement between two traces of the
SAME line grows with the time between them. Per-trace noise would give a flat
curve. The archive gives:

    < 30 s   5.0 MHz        2-10 min  11.6 MHz       > 1 h   10.7 MHz
    30-120 s 8.5 MHz        10-60 min 13.5 MHz

a monotone rise saturating near 11-13 MHz -- the signature of a real
time-correlated process, with a CORRELATION TIME OF A FEW MINUTES and a total
excursion of ~11 MHz RMS. That is the hand re-centring cadence, measured.

Two consequences fall out of it, neither of which was available before.

* The first attempt at validation FAILED, and the failure was informative. Two
  DIFFERENT lines never agree better than ~10 MHz however close in time
  (1.06x growth across every separation bin). That is not a defect: the closest
  any two lines were ever acquired is 6.6 minutes, which is already past the
  correlation time above. The archive simply cannot cross-check itself this way.
* The blocks are 54-76 minutes apart, so the laser was FULLY DECORRELATED
  between them. That is an independent, physical justification for the M4b
  choice not to share sigma_laser across temperature -- previously argued from
  the fit's chi2 alone.

CAN THE CENTRES NOW YIELD THE AC-STARK SHIFT? No, and the reason is a design
confound rather than a statistical shortfall -- which makes it fixable.

The power was stepped MONOTONICALLY, 225 -> 175 -> 125 -> 75 -> 25 mW, for every
one of the four lines, never cycled or randomised. Power therefore decreases as
time increases, so an AC-Stark pull (proportional to P) and any drift-in-time are
collinear by construction. The only lever separating them is that the four sweeps
took different durations for the same power range (17.2 to 28.4 minutes), so
dP/dt differs by 1.65x between lines.

That lever is too weak. Fitting one shared pull coefficient against per-line
linear drift, on the (peak, power) medians and excluding 993.4207 nm whose sweep
contains a 48.8 MHz re-kick, gives

    pull = +9.6 +- 7.4 MHz/W  (1.3 sigma, consistent with zero)
    => |S0(225 mW)| < 7.3 MHz at 95%,  residual scatter 0.50 MHz

against the 0.633 MHz the WIDTH channel already delivers. The centre channel is
twelve times weaker. The drift model itself is fine -- 0.50 MHz residual on 8
degrees of freedom -- and the whole loss is the collinearity.

The same applies to temperature. The t_sweep blocks sit within +-0.5 MHz of each
other (70 C: -0.49, 90 C: +0.09, 110 C: -0.13, block scatter 0.4-0.7 MHz except
110 C where a re-kick gives 11.3), while the expected collisional self-shift
across the sweep is below 0.05 MHz -- two orders under the block-to-block drift.

THE DESIGN LESSON, which is the deliverable: cycle or randomise the power
ordering. With power no longer monotone in time, drift is orthogonal to the
Stark pull and the centre channel becomes independent evidence rather than a
weaker copy of the width channel. It costs nothing but the order of the knob
turns.

WHAT THE ARCHIVE ALREADY SETTLES ABOUT THAT ROLL-OFF: nothing, and the null is
worth recording. The 2025 campaign used one sweep speed. Across the +-6% of rate
actually sampled, rate shows no correlation with the sideband width
(corr = -0.07, p = 0.49), so the corner frequency is not inside that range.
One point and a null; the curve needs the 2026 scan.

(A trap for whoever runs that: rate and delta_ms correlate at exactly -1.000 in
results/ruler_traces.csv. That is the definition -- rate = sideband spacing /
delta_ms -- not a finding.)

Writes results/laser_history.csv, which is committed so the figure can be
redrawn in CI; qc_metrics.csv, its input, is a gitignored scratch dump.
"""

from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402

CLOCK = C.REPO_ROOT / "data_recovered" / "CLOCK.csv"


def _campaign_rate() -> tuple[float, float]:
    with open(C.RESULTS_DIR / "ruler_campaign.csv") as f:
        r = next(csv.DictReader(f))
    return float(r["rate_laser"]), float(r["rate_laser_err"])


def build() -> list[dict]:
    qc_path = C.RESULTS_DIR / "qc_metrics.csv"
    if not qc_path.exists():
        print("  qc_metrics.csv absent (gitignored scratch dump) -- nothing to do")
        return []
    qc = {r["file"]: r for r in csv.DictReader(open(qc_path))}

    # earliest mtime per trace: copies share content, and the earliest is the
    # closest thing to the acquisition instant
    first: dict[str, int] = {}
    for r in csv.DictReader(open(CLOCK)):
        f, t = r.get("manifest_file"), r.get("mtime_epoch")
        if f and t and f in qc:
            first[f] = min(int(t), first.get(f, int(t)))

    rate, rate_err = _campaign_rate()
    rows = []
    for f, t in first.items():
        q = qc[f]
        if not q.get("peak_pos_ms"):
            continue
        rows.append({"file": f, "t_epoch": t, "role": q["role"], "flag": q["flag"],
                     "peak": q["peak"], "temperature_C": q["temperature_C"],
                     "power_mW": q["power_mW"], "peak_pos_ms": float(q["peak_pos_ms"]),
                     "snr": q["snr"]})
    # session = a contiguous run of acquisitions; the campaign has two days
    rows.sort(key=lambda r: r["t_epoch"])
    day = defaultdict(list)
    for r in rows:
        day[r["t_epoch"] // 86400].append(r)
    # Reference PER (day, peak), not per day. The four lines are different
    # transitions sitting at different places in the sweep, so a common
    # reference would fold the line spacing into what is meant to be laser
    # drift. Within one peak, the excursion is the laser (plus any real shift).
    for k, rs in day.items():
        by_peak = defaultdict(list)
        for r in rs:
            by_peak[r["peak"]].append(r)
        for pk, prs in by_peak.items():
            mid = statistics.median(r["peak_pos_ms"] for r in prs)
            for r in prs:
                r["session_day"] = k
                r["offset_mhz"] = (r["peak_pos_ms"] - mid) * rate
                r["offset_err_mhz"] = abs(r["peak_pos_ms"] - mid) * rate_err / rate
    return rows


def structure_function(rows: list[dict], same_peak: bool = True,
                       robust: bool = False,
                       bins=((0, 30), (30, 120), (120, 600), (600, 3600),
                             (3600, 10 ** 9))) -> list[dict]:
    """RMS disagreement between two traces against the time between them.

    The test that separates a real frequency history from per-trace scatter: a
    reconstruction that is only noise gives a FLAT curve, while a genuine drift
    gives one that rises and then saturates at the full excursion. `same_peak`
    compares traces of one line (probing short lags, where the archive has
    ~10 s bursts); False compares different lines, which the acquisition
    pattern leaves no closer than 6.6 minutes.
    """
    import itertools
    out = []
    for lo, hi in bins:
        d = [a["offset_mhz"] - b["offset_mhz"]
             for a, b in itertools.combinations(rows, 2)
             if (a["peak"] == b["peak"]) == same_peak
             and lo <= abs(a["t_epoch"] - b["t_epoch"]) < hi]
        if len(d) > 5:
            m = sum(d) / len(d)
            rms = (sum((x - m) ** 2 for x in d) / (len(d) - 1)) ** 0.5
            sd = sorted(d)
            med = sd[len(sd) // 2]
            ad = sorted(abs(x - med) for x in d)
            mad = 1.4826 * ad[len(ad) // 2]
            out.append({"lag_lo_s": lo, "lag_hi_s": hi, "n_pairs": len(d),
                        "rms_mhz": mad if robust else rms,
                        "rms_all_mhz": rms, "robust_mhz": mad})
    return out


def step_statistics(rows: list[dict], max_gap_s: int = 120) -> dict:
    """The re-kick population, from steps between consecutive traces of one
    line. A continuously-drifting laser gives a Gaussian step distribution; a
    hand re-centred one gives a narrow core (the drift) plus a heavy tail (the
    interventions), and the median-to-RMS ratio is the cleanest way to see it."""
    rows = sorted(rows, key=lambda r: (r["peak"], r["t_epoch"]))
    steps = [b["offset_mhz"] - a["offset_mhz"]
             for a, b in zip(rows, rows[1:])
             if a["peak"] == b["peak"] and 0 < b["t_epoch"] - a["t_epoch"] < max_gap_s]
    if not steps:
        return {}
    n = len(steps)
    mean = sum(steps) / n
    rms = (sum((x - mean) ** 2 for x in steps) / (n - 1)) ** 0.5
    med_abs = sorted(abs(x) for x in steps)[n // 2]
    return {"n_steps": n, "rms_mhz": rms, "median_abs_mhz": med_abs,
            "max_abs_mhz": max(abs(x) for x in steps),
            "heavy_tail_ratio": rms / med_abs if med_abs else float("nan"),
            "frac_beyond_3sigma": sum(1 for x in steps if abs(x - mean) > 3 * rms) / n}


def main() -> int:
    rows = build()
    if not rows:
        return 0
    out = C.RESULTS_DIR / "laser_history.csv"
    for r in rows:
        # DIAGNOSTIC: a reconstruction, conditional on the ruler rate and on
        # mtime standing in for acquisition time. Not a measured frequency.
        r["status"] = "DIAGNOSTIC"
    cols = ["file", "t_epoch", "session_day", "role", "flag", "peak",
            "temperature_C", "power_mW", "snr", "peak_pos_ms",
            "offset_mhz", "offset_err_mhz", "status"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    span_h = (max(r["t_epoch"] for r in rows) - min(r["t_epoch"] for r in rows)) / 3600
    off = [r["offset_mhz"] for r in rows]
    print(f"wrote {out.name}: {len(rows)} traces over {span_h:.1f} h")
    print(f"  reconstructed offset range: {min(off):+.1f} .. {max(off):+.1f} MHz "
          f"(laser axis), peak-to-peak {max(off) - min(off):.1f} MHz")
    sf = structure_function(rows, same_peak=True)
    st = step_statistics(rows)
    print("  structure function (same line), the test that it is not just scatter:")
    for b in sf:
        hi = "inf" if b["lag_hi_s"] > 1e8 else f"{b['lag_hi_s']}"
        print(f"    lag {b['lag_lo_s']:>5}-{hi:>5} s : n={b['n_pairs']:5d}"
              f"   RMS = {b['rms_mhz']:5.2f} MHz")
    if len(sf) >= 2:
        g = sf[-1]["rms_mhz"] / sf[0]["rms_mhz"]
        print(f"  growth shortest->longest lag: {g:.2f}x "
              f"({'REAL time-correlated drift' if g > 1.5 else 'FLAT -- scatter-dominated'})")
    for b in sf:
        b["status"] = "DIAGNOSTIC"
    with open(C.RESULTS_DIR / "laser_history_structure.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sf[0].keys()))
        w.writeheader()
        w.writerows(sf)
    if st:
        print(f"  re-kicks: {st['n_steps']} consecutive steps | RMS {st['rms_mhz']:.2f} MHz"
              f" | median |step| {st['median_abs_mhz']:.2f} | max {st['max_abs_mhz']:.1f}")
        print(f"    heavy-tail ratio RMS/median = {st['heavy_tail_ratio']:.0f}x"
              f"  ({100 * st['frac_beyond_3sigma']:.1f}% beyond 3 sigma vs 0.3% Gaussian)")
        print("    -> quiet drift punctuated by discrete operator interventions")
    print("  This is a PREDICTION of what a wavemeter log would show, from the")
    print("  atoms and the file timestamps alone -- testable if a log turns up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
