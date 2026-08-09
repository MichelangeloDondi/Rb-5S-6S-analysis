#!/usr/bin/env python3
"""
Cross-epoch checks from the pilot and prehistory sessions.  (addendum 11)

The recovered pilot (2025-07-16 folder) and prehistory (2025-07-03/04) are
OUTSIDE the frozen archive, but they carry six checks the archive cannot
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
   of 144.2(11) ms vs the campaign's 146.97 ms: the sweep rate agrees to
   1.9% across days and re-preparations, which is precisely why M2
   calibrates every block with its own rulers (per-block scatter 0.6%).
4. PILOT LAWS -- width flat 60.5-61.5 ms across 35-210 mW (the power null);
   amplitude x34 vs x36 predicted P^2 over the 6x span. Both are INTERNAL
   ratios, so both are immune to what the pilot's oven label means -- which
   is just as well, because check 5 shows it does not mean what it seems.
5. PILOT THERMOMETRY (addendum 17 + its postscript) -- the pilot's
   `91c650ma` pairs a temperature with a CURRENT, which is the rehearsal
   parenthetical's structure, not the campaign's, so that `91 C` should be a
   variac SET POINT and the pilot should have run at the rehearsal's internal
   ~130 C. It did: amplitude/P^2 sits within 30% of the 130 C ladder, where
   an internal-90 C pilot would be ~12x lower, and the pilot ran the MORNING
   of the campaign's own day so an unlogged gain change is unlikely. The
   WIDTH test is a NULL -- refitted with the archive's composite model the
   pilot is within 0.7 sigma of every dwell from 90 to 130 C. The first
   version of this check used the crude QC FWHM, which inflates the low-SNR
   end and manufactured a 1.9 sigma that is not there. QC metrics triage
   traces; they do not measure widths.

6. PILOT ch1 IDENTITY -- the pilot rulers' 1.92 V second channel
   is the frequency SWEEP, not a power monitor: it ramps linearly in every
   record, its slope ALTERNATES SIGN at fixed magnitude (successive legs of
   the triangle sweep), and the implied calibration ~4.7 MHz/mV reproduces
   the EOM comb's own rate. It wanders 5-9% from straight, well above the
   sweep's own 0.3% nonlinearity bound, so it monitors the scan rather than
   calibrating it -- which is why the comb ruler exists. Which actuator it
   is (piezo vs elsewhere in the scan chain) the trace cannot say.

7. REHEARSAL CHRONOLOGY (non-result, stated) -- envelope centres of the
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

The double-temperature notation 130C(90C-0.65A) is resolved -- the
parenthetical is the variac set point, the campaign temperature is the
internal-thermocouple reading -- see addendum 15, which also gives the
cold-spot-vs-reading offset its first empirical handle.

Requires the pilot/prehistory quarantines (private). Exits cleanly without
them; the committed numbers above are the record, addendum 11 the writeup.
Nothing here enters results/. RB5S6S_PILOT_DIR and RB5S6S_PREHISTORY_DIR are
needed only to re-run this script against those private working copies, and the
committed CSVs are what the repository ships.
"""

from __future__ import annotations

import collections
import csv
import datetime as dt
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

QP = Path(os.environ.get(
    "RB5S6S_PILOT_DIR", "~/rb-2025-quarantine/pilot")).expanduser()
QH = Path(os.environ.get(
    "RB5S6S_PREHISTORY_DIR", "~/rb-2025-quarantine/prehistory")).expanduser()
TOOTH_SPACING_LASER_MHZ = 6.25   # EOM 12.5 MHz tank, laser axis = Omega/2
RATE_MHZ_MS = float(next(csv.DictReader(
    open(ROOT / "results" / "ruler_campaign.csv")))["rate_laser"])
CAMPAIGN_TOOTH_MS = TOOTH_SPACING_LASER_MHZ / RATE_MHZ_MS
PILOT_TOOTH_MS = 144.2      # the pilot day's own Def-comb ACF period (check 3)


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
    print("   -> the audit's JST clock interpretation confirmed in-file.")


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
    print("   (the once-flagged ~32 ms satellites: a peak-finding artifact --")
    print("    ACF shows no coherent companion in either epoch; see the")
    print("    postscript to addendum 11)")

def pilot_thermometry() -> None:
    """Which campaign dwell does the pilot's oven setting correspond to?

    The pilot filenames pair a temperature with a CURRENT (`91c650ma`) --
    structurally the rehearsal's parenthetical (`90C-0.65A`), which addendum
    15 identified as the variac set point. If that reading is right the pilot
    ran at the same oven setting as the rehearsal, whose headline records an
    internal 130 C -- NOT at the campaign's internal 90 C.

    Two observables were put to it. The WIDTH test is a NULL: fitted with the
    archive's own composite model it cannot tell 90 from 130 C (postscript to
    addendum 17). It is computed here anyway, because the first version of
    this check used the crude QC FWHM, got a spurious 1.9 sigma, and the
    correction is worth being able to re-run. What carries the conclusion is
    the filename structure and the amplitude.
    """
    import pandas as pd
    from rb5s6s import config as C
    from rb5s6s.ingest import load_trace
    from rb5s6s.qc import trace_metrics
    from rb5s6s.noise import condition_noise_model
    from rb5s6s.linefit import fit_condition, to_frequency, transit_fwhm_at_T
    from rb5s6s.lineshape import model_profile

    def _total_fwhm(gc, sl, transit):
        # the helper run_linefit uses: sub-grid interpolated FWHM of the
        # fitted composite -- robust to how width splits laser vs collisional
        nu = np.arange(-60, 60, 0.005)
        prof = model_profile(nu, gamma_coll=max(gc, 0.0),
                             sigma_laser_fwhm=max(sl, 1e-6), transit_fwhm=transit)
        h = 0.5 * prof.max()
        ab = np.where(prof >= h)[0]
        lo, hi = ab[0], ab[-1]
        left = nu[lo] - (prof[lo] - h) / (prof[lo] - prof[lo - 1]) * (nu[lo] - nu[lo - 1])
        right = nu[hi] + (prof[hi] - h) / (prof[hi] - prof[hi + 1]) * (nu[hi + 1] - nu[hi])
        return float(right - left)

    RATE_T = 2 * 6.25 / PILOT_TOOTH_MS      # transition axis, pilot's own comb
    blocks, amps = {}, []
    for p in sorted((QP / "4192nm91c650ma").glob("*.csv")):
        mw = int(p.stem.split("650ma")[1].rstrip("0123456789").replace("mw", ""))
        t, v, _ = load_trace(p, with_info=True)
        blocks.setdefault(mw, []).append((to_frequency(t, RATE_T), v))
        amps.append((mw, trace_metrics(t, v)["height_v"]))

    transit = transit_fwhm_at_T(110.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    wid = []
    for mw in sorted(blocks):
        fr = [a for a, _ in blocks[mw]]
        vo = [b for _, b in blocks[mw]]
        fit = fit_condition(fr, vo, T_C=110.0, law=condition_noise_model(vo),
                            transit_fwhm=transit)
        wid.append(_total_fwhm(fit["gamma_coll"], fit["sigma_laser"], transit))
    wid = np.array(wid)
    pm = float(wid.mean())
    pse = float(wid.std(ddof=1) / np.sqrt(len(wid)))

    d = pd.read_csv(ROOT / "results" / "linefit_conditions.csv")
    c = d[(d.peak == 4192) & ((d.role == "t_sweep")
                              | ((d.role == "p_sweep") & (d["T"] == 130)))]
    g = c.groupby("T").agg(w=("total_fwhm", "mean"), err=("total_fwhm_err", "mean"),
                           sd=("total_fwhm", "std"))
    # block-to-block reproducibility: the 130 C ladder holds T fixed across
    # five power blocks, and width is power-independent (the C3 null)
    blk = float(g.loc[130, "sd"] / g.loc[130, "w"])

    print("\n5. PILOT THERMOMETRY -- the pilot's oven setting, from physics")
    print(f"   pilot 4192, archive composite fit: {pm:.3f} +- {pse:.3f}(block SE)"
          f" +- {pm*blk:.3f}(reproducibility {100*blk:.1f}%) MHz")
    for T, r in g.iterrows():
        dd = pm - r.w
        e = float(np.sqrt(pse**2 + (pm * blk)**2 + r.err**2 + (r.w * blk)**2))
        print(f"   vs campaign internal {int(T):3d} C ({r.w:.3f} MHz): "
              f"{dd:+.3f} +- {e:.3f} -> {dd/e:+.1f} sigma")
    print("   -> NULL. Consistent with every dwell from 90 to 130 C: the fitted")
    print("      ladder spans 3% across 60 K while one block reproduces to 2%.")
    print("      (The crude QC FWHM appears to resolve this. It does not -- it")
    print("       inflates the low-SNR end; see the postscript to addendum 17.)")

    A = pd.DataFrame(amps, columns=["mW", "amp"])
    pl = float(np.median(A.amp / (A.mW / 100.0) ** 2))
    q = pd.read_csv(ROOT / "results" / "qc_metrics.csv")
    q = q[q.peak == 4192]
    gp = q[(q.role == "p_sweep") & (q.temperature_C == 130)].dropna(subset=["power_mW"])
    cp = float(np.median(gp.height_v / (gp.power_mW / 100.0) ** 2))
    print(f"   amplitude/P^2: pilot {pl:.3f} V vs campaign 130 C ladder {cp:.3f} V "
          f"(x{pl/cp:.2f});")
    print(f"   an internal-90 C pilot would sit ~12x lower, i.e. x{12*cp/pl:.0f} below")
    print("   what is measured. Gain is untokened on both sides, but the pilot ran")
    print("   the MORNING of the campaign's own day -- so this carries the verdict,")
    print("   together with the filename structure. See addendum 17.")


def pilot_ch1_identity() -> None:
    """What is the pilot rulers' second channel? (was: "1.92 V DC, power monitor?")

    The experimenter's recollection was that it is the piezo sweeping the laser
    frequency. The data agree, and the discriminator is the SIGN. A power
    monitor sits at a level; a triangle frequency sweep is caught one leg at a
    time, so successive records must show a RAMP whose slope alternates in sign
    while its magnitude stays put. That is what they show.

    What this does NOT establish is which actuator: the trace says "a scan
    control voltage proportional to laser frequency", not specifically the
    piezo as opposed to any other element in the scan chain.
    """
    rows = []
    for f in sorted((QP / "EOM ruler" / "Def").glob("eom_def_*.csv")):
        d = np.genfromtxt(f, delimiter=",", skip_header=2)
        d = d[~np.isnan(d).any(axis=1)]
        t, c1, c2 = d[:, 0] * 1e3, d[:, 1], d[:, 2]
        pf = np.polyfit(t, c1, 1)
        resid = c1 - np.polyval(pf, t)
        v = c2 - np.median(c2)
        ac = np.correlate(v, v, "full")[len(v) - 1:]
        dtm = np.median(np.diff(t))
        lo, hi = int(100 / dtm), int(200 / dtm)
        per = (lo + int(np.argmax(ac[lo:hi]))) * dtm
        mv_tooth = abs(pf[0]) * per * 1e3
        rows.append((pf[0] * 1e3, resid.std() * 1e3,
                     1e3 * (c1.max() - c1.min()),
                     TOOTH_SPACING_LASER_MHZ / mv_tooth if mv_tooth else np.nan))
    a = np.array(rows)
    sgn = "".join("+" if x > 0 else "-" for x in a[:, 0])
    print("\n6. PILOT ch1 IDENTITY -- the 1.92 V channel is the frequency SWEEP")
    print(f"   {len(a)} ruler records; ch1 is a linear ramp in every one")
    print(f"   |slope| {np.abs(a[:, 0]).mean():.5f} mV/ms, spread "
          f"{100*np.abs(a[:, 0]).std()/np.abs(a[:, 0]).mean():.0f}%")
    print(f"   slope SIGNS across records: {sgn}")
    print("   -> alternating sign at fixed magnitude = successive legs of the")
    print("      triangle sweep. A power monitor cannot do that.")
    print(f"   implied calibration {np.nanmean(a[:, 3]):.2f} MHz/mV (laser axis), "
          f"spread {100*np.nanstd(a[:, 3])/np.nanmean(a[:, 3]):.0f}%")
    print(f"   ramp span {a[:, 2].mean():.1f} mV per ~1 s record; residual from a")
    print(f"   straight line {100*(a[:, 1]/a[:, 2]).mean():.0f}% of it -- far above the")
    print("   sweep's own 0.45% nonlinearity bound, so this is a MONITOR of the")
    print("   scan, not a usable frequency axis. The EOM comb remains the ruler.")


def main() -> int:
    if not (QP.is_dir() and QH.is_dir()):
        print("pilot/prehistory quarantines not on this machine -- the committed "
              "numbers in this docstring and addendum 11 are the record.")
        return 0
    trigtime_check()
    pilot_steps()
    pilot_ruler_rate()
    pilot_thermometry()
    pilot_ch1_identity()
    print("\n4. and 7.: pilot laws and the rehearsal chronology non-result -- see the")
    print("   docstring and addendum 11 (envelope analysis needs no re-run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
