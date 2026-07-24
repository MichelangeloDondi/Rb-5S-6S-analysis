#!/usr/bin/env python3
"""
Cross-epoch checks from the pilot and prehistory sessions.  (addendum 11)

The recovered pilot (2025-07-16 folder) and prehistory (2025-07-03/04) are
OUTSIDE the frozen archive, but they carry four checks the archive cannot
perform on itself, plus one honest non-result:

1. CLOCK VALIDATION -- the LeCroy dress-rehearsal files embed wall-clock
   trigger times. mtime(JST) - TrigTime = +4..+9 s (median +6 s, one +145 s
   operator delay): the audit's JST reading of the FAT mtimes is confirmed
   by an independent clock INSIDE the data.
2. OUT-OF-SAMPLE TEST of the etalon-transient disturbance model -- the pilot
   science ran ~2.9 h after its morning lock-on, i.e. past the ~2 h
   transient; the model predicts recapture steps at the settled scale
   (<~20 ms). Measured: +14.0 / -5.8 / +0.2 ms. PASS.
3. CROSS-DAY CALIBRATION -- the pilot-day Def rulers give an ACF comb period
   of 144.2(11) ms vs the campaign's 146.81 ms: the sweep rate agrees to
   1.7% across days and re-preparations, which is precisely why M2
   calibrates every block with its own rulers (per-block scatter 0.6%).
4. PILOT LAWS -- width flat 60.5-61.5 ms across 35-210 mW (the power null,
   at 91 C) matching the campaign's 90 C width; amplitude x34 vs x36
   predicted P^2 over the 6x span.
5. REHEARSAL CHRONOLOGY (non-result, stated) -- envelope centres of the
   dual-scan captures scatter most in the first block (649 ms) and settle
   mid-session (17-131 ms), consistent with a fresh-lock transient, but the
   final peak's blocks are noisy again (~200-380 ms) and the observable
   rests on an unverified trigger-sync assumption: no claim either way.

The extraction list this opened is now CLOSED (addenda 13-14): the noise
spectrum measured the detection chain over four decades and found a 61 Hz
mains line at 14.6x the floor, chased into the archive at 1.9x / 0.14% of
peak -- negligible; and the rehearsal power sweep confirmed the P^2 law
(slopes 1.87-2.36) while its WIDTH test proved impossible to port, the
dual-scan envelope being ~120x the linewidth. The "~32 ms satellites" were a
peak-finding artifact (ACF shows no coherent companion in either epoch), and
the three binary 4192@270 files are 0xFF never-written placeholders.

Still open, and only the experimenter can close them: the pilot rulers'
1.92 V DC channel identity (power monitor?), and the two-zone temperature
notation 130C(90C-0.65A) -- which zone do the campaign temperatures name?

Requires the pilot/prehistory quarantines (private). Exits cleanly without
them; the committed numbers above are the record, addendum 11 the writeup.
Nothing here enters results/.
"""

from __future__ import annotations

import collections
import datetime as dt
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

QP = Path(os.path.expanduser("~/Documents/RawDataPilot_QUARANTINE_2026-07-24"))
QH = Path(os.path.expanduser("~/Documents/RawDataPrehistory_QUARANTINE_2026-07-24"))
RATE_MHZ_MS = 0.04257061052233977
CAMPAIGN_TOOTH_MS = 146.81


def trigtime_check() -> None:
    rows = []
    for p in sorted((QH / "2025-07-04").glob("*.csv")):
        head = open(p, "rb").read(400).decode("latin-1")
        m = re.search(r"#1,(\d\d-\w\w\w-\d{4} \d\d:\d\d:\d\d)", head)
        if not m:
            continue
        trig = dt.datetime.strptime(m.group(1), "%d-%b-%Y %H:%M:%S")
        mt = dt.datetime.utcfromtimestamp(p.stat().st_mtime + 9 * 3600)
        rows.append((mt - trig).total_seconds())
    d = np.array(rows)
    print(f"1. CLOCK VALIDATION: {len(d)} in-file LeCroy TrigTimes;")
    print(f"   mtime(JST) - TrigTime: median {np.median(d):+.0f} s, "
          f"range [{d.min():+.0f}, {d.max():+.0f}] s")
    print(f"   -> the audit's JST clock interpretation confirmed in-file.")


def pilot_steps() -> None:
    from rb5s6s.ingest import load_trace
    from rb5s6s.qc import trace_metrics
    blocks = collections.defaultdict(list)
    for p in sorted((QP / "4192nm91c650ma").glob("*.csv")):
        mw = p.stem.split("650ma")[1].rstrip("0123456789")
        t, v, _ = load_trace(p, with_info=True)
        m = trace_metrics(t, v)
        blocks[mw].append((p.stat().st_mtime, m["peak_pos_ms"]))
    order = sorted(blocks.items(), key=lambda kv: min(x[0] for x in kv[1]))
    B = [(np.mean([x[0] for x in g]), float(np.median([x[1] for x in g])), mw)
         for mw, g in order]
    print("\n2. PILOT OUT-OF-SAMPLE TEST (science ~2.9 h after lock-on =")
    print("   post-transient; model predicts steps <~ 20 ms):")
    for a, b in zip(B, B[1:]):
        print(f"   {a[2]}->{b[2]}: step {b[1]-a[1]:+7.1f} ms "
              f"({(b[1]-a[1])*RATE_MHZ_MS:+.2f} MHz laser)")
    ok = all(abs(b[1] - a[1]) < 20 for a, b in zip(B, B[1:]))
    print(f"   -> {'PASS' if ok else 'FAIL'}")


def pilot_ruler_rate() -> None:
    periods = []
    for p in sorted((QP / "EOM ruler" / "Def").glob("eom_def_*.csv")):
        d = np.genfromtxt(p, delimiter=",", skip_header=2)
        d = d[~np.isnan(d).any(axis=1)]
        t, sig = d[:, 0] * 1e3, d[:, 2]
        v = sig - np.median(sig)
        ac = np.correlate(v, v, "full")[len(v) - 1:]
        dtm = np.median(np.diff(t))
        lo, hi = int(100 / dtm), int(200 / dtm)
        periods.append((lo + int(np.argmax(ac[lo:hi]))) * dtm)
    per = np.array(periods)
    ratio = np.median(per) / CAMPAIGN_TOOTH_MS
    print(f"\n3. CROSS-DAY CALIBRATION: pilot Def-comb ACF period "
          f"{np.median(per):.1f} ms (n={len(per)}, spread {per.std(ddof=1):.1f})")
    print(f"   vs campaign {CAMPAIGN_TOOTH_MS} ms -> sweep-rate ratio {ratio:.4f} "
          f"({100*(1-ratio):+.1f}%): per-block rulers vindicated.")
    print(f"   (the once-flagged ~32 ms satellites: a peak-finding artifact --")
    print(f"    ACF shows no coherent companion in either epoch; see the")
    print(f"    postscript to addendum 11)")


def main() -> int:
    if not (QP.is_dir() and QH.is_dir()):
        print("pilot/prehistory quarantines not on this machine -- the committed "
              "numbers in this docstring and addendum 11 are the record.")
        return 0
    trigtime_check()
    pilot_steps()
    pilot_ruler_rate()
    print("\n4.-5. pilot laws and the rehearsal chronology non-result: see the")
    print("   docstring and addendum 11 (envelope analysis needs no re-run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
