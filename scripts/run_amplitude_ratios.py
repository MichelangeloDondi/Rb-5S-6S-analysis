#!/usr/bin/env python3
"""
M10: cross-peak AREA ratios vs the scalar-operator degeneracy law.

For each temperature, integrate every canonical trace's line area (V*MHz, on
its own block's frequency axis), average over repeats, and compare the
four-peak shares/ratios with the parameter-free prediction

    S(peak) ∝ abundance x (2F+1) / G_iso        (pure scalar operator)

Within-isotope ratios (4207/4121 -> 5/3, 4192/4154 -> 7/5) are the cleanest:
abundance AND all common detection factors cancel; only between-block power /
alignment drift and differential trapping survive. The temperature trend of
measured/predicted is the differential-trapping probe.

Outputs: results/amplitude_ratios.csv + stdout.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.amplitudes import peak_area, predicted_shares  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402

PEAKS = ("4121", "4154", "4192", "4207")
TEMPS = ("70", "90", "110", "130")


def load_rates():
    trate, prate = {}, defaultdict(list)
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        rr = 2.0 * float(r["rate"])
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = rr
        else:
            prate[r["peak"]].append(rr)
    return trate, {k: float(np.mean(v)) for k, v in prate.items()}


def main() -> int:
    rows = load_manifest()
    trate, prate = load_rates()
    pred = predicted_shares()

    areas = {}  # (peak, T) -> (mean, sem)
    for peak in PEAKS:
        for T in TEMPS:
            if T == "130":
                recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "p_sweep"
                        and r["peak"] == peak and r["power_mW"] == "225"]
                rate = prate.get(peak)
            else:
                recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                        and r["peak"] == peak and r["temperature_C"] == T]
                rate = trate.get((peak, T))
            if rate is None or len(recs) < 3:
                continue
            vals = []
            for r in recs:
                t, v = load_trace(trace_path(r))
                vals.append(peak_area(to_frequency(t, rate), v))
            areas[(peak, T)] = (float(np.mean(vals)),
                                float(np.std(vals, ddof=1) / np.sqrt(len(vals))))

    from rb5s6s.constants import peak_label
    print("=" * 76)
    print("(M10) AREA RATIOS vs the scalar-operator degeneracy law")
    print("  peaks: " + ", ".join(peak_label(p, isotope=True, line=True) for p in PEAKS))
    print("  (columns below use the 4-digit key for width; full labels above)")
    print("  prediction: S ∝ abundance x (2F+1)/G_iso  (two identical photons ->")
    print("  purely scalar operator for J=1/2 -> J=1/2: same rate for every F, m_F)\n")

    out = []
    print("  WITHIN-ISOTOPE ratios (abundance & detection cancel -> pure degeneracy):")
    print(f"  {'T':>5s} {'4207/4121':>12s} {'pred 5/3':>9s} {'4192/4154':>12s} {'pred 7/5':>9s}")
    for T in TEMPS:
        cells = []
        for a, b, p in (("4207", "4121", 5 / 3), ("4192", "4154", 7 / 5)):
            if (a, T) in areas and (b, T) in areas:
                (ma, ea), (mb, eb) = areas[(a, T)], areas[(b, T)]
                r = ma / mb
                er = r * np.hypot(ea / ma, eb / mb)
                cells.append((r, er, p))
                out.append({"T": T, "ratio": f"{a}/{b}", "measured": r, "err": er,
                            "predicted": p, "pull_sigma": (r - p) / er if er > 0 else np.nan})
        if len(cells) == 2:
            (r1, e1, _), (r2, e2, _) = cells
            print(f"  {T:>4s}C {r1:>7.2f}+/-{e1:<4.2f} {5/3:>9.3f} "
                  f"{r2:>7.2f}+/-{e2:<4.2f} {7/5:>9.3f}")

    print("\n  CROSS-ISOTOPE ratio (adds the abundance test):")
    print(f"  {'T':>5s} {'4192/4207':>12s} {'pred':>7s}")
    for T in TEMPS:
        if ("4192", T) in areas and ("4207", T) in areas:
            (ma, ea), (mb, eb) = areas[("4192", T)], areas[("4207", T)]
            r = ma / mb; er = r * np.hypot(ea / ma, eb / mb)
            p = pred["4192"] / pred["4207"]
            out.append({"T": T, "ratio": "4192/4207", "measured": r, "err": er,
                        "predicted": p, "pull_sigma": (r - p) / er if er > 0 else np.nan})
            print(f"  {T:>4s}C {r:>7.2f}+/-{er:<4.2f} {p:>7.3f}")

    with open(C.RESULTS_DIR / "amplitude_ratios.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    pulls = [abs(o["pull_sigma"]) for o in out if np.isfinite(o["pull_sigma"])]
    print(f"\n{'-'*76}")
    print(f"  |pull| median {np.median(pulls):.1f} sigma, max {max(pulls):.1f} sigma "
          f"-- against STATISTICAL errors only.")
    print("\nVERDICT (2026-07-11 archival run): the within-block statistics are ~1-3%,")
    print("but the ratios swing 30-50% BETWEEN temperatures and NON-monotonically")
    print("(e.g. 993.4207/993.4121 nm: 1.10 -> 0.98 -> 2.53 -> 1.97 vs constant 5/3 the")
    print("physics demands). Genuine differential trapping would be smooth in density;")
    print("this is BETWEEN-BLOCK power/alignment drift (each peak = its own block,")
    print("hours apart, with knob/cavity re-tweaks -- corroborated by the M0 audit's")
    print("block amplitude anomalies). CONCLUSION: the archival data cannot test the")
    print("degeneracy law beyond the ~40% level; the parameter-free prediction stands")
    print("ready, and the OCTOBER task is to measure the four peaks INTERLEAVED (or")
    print("with continuous power logging) so the ~% -level test becomes possible.")
    print("Corollary: cross-peak AMPLITUDE comparisons in this archive carry ~30-50%")
    print("systematics (per-peak, within-block analyses -- M7's slopes -- are safe).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
