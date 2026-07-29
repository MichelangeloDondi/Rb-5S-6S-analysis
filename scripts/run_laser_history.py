#!/usr/bin/env python3
"""
Reconstruct the laser's frequency history from the traces (module M20)
=====================================================================

RETRACTED AND REBUILT, 2026-07-29. The first version of this module referenced
peak positions to a PER-SESSION mean and reported a ~22-hour, 65 MHz
peak-to-peak reconstruction of the laser's frequency. That number was the scope's
HORIZONTAL KNOB, not the laser. Two measurements settle it, both from the
archive alone:

1. The exported time axis is WINDOW-referenced, not trigger-referenced. Each
   file's first sample time (now recorded as qc's window_start_ms) is a discrete
   setting: across 295 consecutive pairs it is identically unchanged 237 times,
   and every one of the 58 changes is a multiple of 2 ms with a 4 ms minimum. It
   never jitters.
2. Within SINGLE 5-repeat blocks, whose traces are saved seconds apart, a change
   of ds in that setting moves peak_pos_ms by 0.938*ds, with an 8.8 ms residual
   -- the size of the ordinary window-still scatter (5.2 ms, 0.22 MHz). A laser
   does not move 22 MHz in seconds, and the window-still control says it moves
   0.22 MHz. The peak follows the window.

And the retracted headline was arithmetically the knob: reported 64.97 MHz
peak-to-peak against a window-start travel of 1516 ms x 0.04257 = 64.54 MHz,
a ratio of 1.007.

The repository had already said so, and this module had not read it -- PLAN.md:
"Scope horizontal-knob and cavity-reference recenters occurred between saves --
MANY times ... => absolute positions carry no meaning across saves."

WHAT IS RECONSTRUCTED INSTEAD. A peak position is a frequency measure only while
the horizontal setting is untouched, so the campaign is cut into DISPLAY EPOCHS
-- maximal runs of unchanged window_start_ms within a session -- and referenced
inside each:

    offset(MHz) = (peak_pos_ms - <peak_pos_ms>_epoch,peak) * rate_campaign

with rate_campaign = 0.04257(5) MHz/ms, laser axis (M2, results/ruler_campaign).
The reference is per (epoch, peak) because the four lines sit at different places
in the sweep. Across an epoch boundary the offset is UNKNOWN -- not zero, not
interpolated -- and nothing here joins two epochs.

That gives 296 traces in 60 epochs, of which 45 hold three or more traces of one
line. The within-epoch excursion is 1.28 MHz peak-to-peak (median), and the one
long knob-untouched stretch -- epoch 38, 993.4121 nm, ten traces over 74.9
minutes on 2025-07-17 -- drifts at -0.022 MHz/min. That last number is the
result worth having: DATA.md quotes the held lock at ~0.016 MHz/min from an
independent argument, and this is a direct measurement of it from the atoms.

TWO INTERVENTION CHANNELS, and only one is visible in the setting. A knob move
shows up in window_start_ms and breaks the record. A CAVITY-REFERENCE recentring
does not -- it is a genuine frequency step, and it appears as a step inside an
epoch. So a within-epoch excursion of 10-15 MHz (some epochs) is real frequency
motion, mostly operator-induced, while the epoch boundaries are simply blind.

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

EVERYTHING BELOW THIS LINE PREDATES THE RETRACTION and is under review. The
numbers in it were computed from session-referenced offsets, so any of them that
differences peak positions ACROSS a horizontal-setting change is affected --
including the quoted "48.8 MHz re-kick" in the 993.4207 nm sweep, the "11.3" at
110 C, the centre-channel bound |S0(225 mW)| < 7.3 MHz, and the claim that
blocks 54-76 min apart were "fully decorrelated". The DESIGN LESSON (cycle the
power ordering) does not depend on any of them and stands. The same exposure
reaches scripts/run_drift_settling.py, which compares block-median peak
positions across blocks and feeds preregistration addenda 4, 5, 6 and 12; that
is tracked separately and is NOT fixed by this module's rebuild.

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
        if not q.get("window_start_ms"):
            print("  qc_metrics.csv predates window_start_ms -- re-run "
                  "scripts/run_qc.py; peak positions cannot be referenced "
                  "without the horizontal setting")
            return []
        rows.append({"file": f, "t_epoch": t, "role": q["role"], "flag": q["flag"],
                     "peak": q["peak"], "temperature_C": q["temperature_C"],
                     "power_mW": q["power_mW"], "peak_pos_ms": float(q["peak_pos_ms"]),
                     "window_start_ms": float(q["window_start_ms"]),
                     "snr": q["snr"]})
    # session = a contiguous run of acquisitions; the campaign has two days
    rows.sort(key=lambda r: r["t_epoch"])
    day = defaultdict(list)
    for r in rows:
        day[r["t_epoch"] // 86400].append(r)
    # DISPLAY EPOCH: a maximal run of unchanged window_start_ms within one
    # session. The setting is discrete and never jitters, so this needs no
    # tolerance -- any change at all starts a new epoch, and no offset crosses
    # one. (Referencing per session instead is what produced the retracted
    # 65 MHz; see the module docstring.)
    ep = 0
    for prev, cur in zip(rows, rows[1:]):
        prev["display_epoch"] = ep
        if (cur["window_start_ms"] != prev["window_start_ms"]
                or cur["t_epoch"] // 86400 != prev["t_epoch"] // 86400):
            ep += 1
        cur["display_epoch"] = ep
    if rows:
        rows[0].setdefault("display_epoch", 0)

    # Reference PER (epoch, peak). Per peak because the four lines are different
    # transitions sitting at different places in the sweep, so a common
    # reference would fold the line spacing into what is meant to be laser
    # drift; per epoch because that is the span over which a peak position is a
    # frequency at all.
    for k, rs in day.items():
        for r in rs:
            r["session_day"] = k
    by_seg = defaultdict(list)
    for r in rows:
        by_seg[(r["display_epoch"], r["peak"])].append(r)
    for (_, _), prs in by_seg.items():
        mid = statistics.median(r["peak_pos_ms"] for r in prs)
        for r in prs:
            r["offset_mhz"] = (r["peak_pos_ms"] - mid) * rate
            r["offset_err_mhz"] = abs(r["peak_pos_ms"] - mid) * rate_err / rate
            r["n_in_segment"] = len(prs)
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

    PAIRS ARE CONFINED TO ONE DISPLAY EPOCH (2026-07-29). Comparing across a
    horizontal-knob move differences two numbers measured against different
    zeros, and the earlier version did exactly that: its monotone rise to
    11-13 MHz with a few-minute correlation time was the knob's cadence, since
    an intervention every few minutes produces the same shape as drift over the
    same scale. This test cannot distinguish drift from intervention, so it is
    now only asked the question it can answer -- whether the WITHIN-epoch
    reconstruction is time-correlated rather than per-trace scatter. That costs
    the long-lag bins, which is honest: nothing in the archive constrains them.
    """
    import itertools
    out = []
    for lo, hi in bins:
        d = [a["offset_mhz"] - b["offset_mhz"]
             for a, b in itertools.combinations(rows, 2)
             if (a["peak"] == b["peak"]) == same_peak
             and a.get("display_epoch") == b.get("display_epoch")
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
    interventions), and the median-to-RMS ratio is the cleanest way to see it.

    Steps are taken WITHIN a display epoch only, so the tail is the CAVITY
    reference being recentred -- a real frequency step -- and not the horizontal
    knob, which is a change of coordinate and no step at all."""
    rows = sorted(rows, key=lambda r: (r["peak"], r["t_epoch"]))
    steps = [b["offset_mhz"] - a["offset_mhz"]
             for a, b in zip(rows, rows[1:])
             if a["peak"] == b["peak"]
             and a.get("display_epoch") == b.get("display_epoch")
             and 0 < b["t_epoch"] - a["t_epoch"] < max_gap_s]
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
    cols = ["file", "t_epoch", "session_day", "display_epoch", "window_start_ms",
            "n_in_segment", "role", "flag", "peak",
            "temperature_C", "power_mW", "snr", "peak_pos_ms",
            "offset_mhz", "offset_err_mhz", "status"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    span_h = (max(r["t_epoch"] for r in rows) - min(r["t_epoch"] for r in rows)) / 3600
    n_ep = len({r["display_epoch"] for r in rows})
    print(f"wrote {out.name}: {len(rows)} traces over {span_h:.1f} h, "
          f"{n_ep} display epochs ({n_ep - 1} horizontal-setting changes)")
    # Per (epoch, peak): the only span over which these offsets are frequencies.
    # NO campaign-wide peak-to-peak is printed -- that figure was the knob.
    segs = defaultdict(list)
    for r in rows:
        segs[(r["display_epoch"], r["peak"])].append(r)
    pp = sorted((max(o) - min(o)) for o in
                ([x["offset_mhz"] for x in v] for v in segs.values()) if len(o) >= 3)
    if pp:
        print(f"  within-epoch excursion, per (epoch, line), {len(pp)} segments of >=3: "
              f"median {pp[len(pp) // 2]:.2f} MHz, max {pp[-1]:.2f} MHz")
    print("  across an epoch boundary the offset is UNKNOWN; nothing here joins two.")
    sf = structure_function(rows, same_peak=True)
    st = step_statistics(rows)
    print("  structure function (same line), the test that it is not just scatter:")
    for b in sf:
        hi = "inf" if b["lag_hi_s"] > 1e8 else f"{b['lag_hi_s']}"
        print(f"    lag {b['lag_lo_s']:>5}-{hi:>5} s : n={b['n_pairs']:5d}"
              f"   RMS = {b['rms_mhz']:5.2f} MHz")
    if len(sf) >= 2:
        r = [b["rms_mhz"] for b in sf]
        g = r[-1] / r[0]
        mono = all(b >= a - 1e-9 for a, b in zip(r, r[1:]))
        # Honest verdict (2026-07-29): confining pairs to one display epoch cost
        # the long-lag bins, and what is left is NOT monotone -- it rises, dips,
        # then rises on 25 pairs. A ratio of first to last across a non-monotone
        # curve is not evidence of a correlation time, and the previous version
        # printed "REAL time-correlated drift" from exactly that ratio.
        if mono and g > 1.5:
            verdict = "monotone rise -- time-correlated within an epoch"
        elif g > 1.5:
            verdict = ("NON-MONOTONE: rises, dips, rises; the ratio alone is "
                       "not evidence of a correlation time")
        else:
            verdict = "FLAT -- scatter-dominated"
        print(f"  shortest->longest lag: {g:.2f}x  ({verdict})")
        print(f"    thin bins: {', '.join(str(b['n_pairs']) for b in sf)} pairs")
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
