#!/usr/bin/env python3
"""
The pilot day's own frequency ruler, from 27 never-used EOM traces (M26).

WHY THIS EXISTS. The pilot session (2025-07-16) enters M23 and M25 through a
frequency axis borrowed from the campaign: pilot rate = campaign 4192 rate
times a fitted scale, boxed to [0.9, 1.1]. Both fits put the scale near 1.02
anyway, but a fitted nuisance is an assumption wearing a posterior. The
recovered pilot quarantine holds 27 EOM ruler traces from the pilot day
itself that no analysis had ever opened: two groups, "Def" (10 traces,
three columns, the 1.92 V piezo ramp co-recorded beside the signal) and
"Initial attempts" (17 traces, two columns, a coarser 1 ms time base). They
are Agilent-format 2000-point files, so the archive's own seven-tooth comb
machinery (M2, `rb5s6s.ruler.fit_comb`) fits them unchanged.

WHAT IT MEASURES. Per trace: the comb spacing Delta and the laser-axis rate
6.25/Delta. Per group: the inverse-variance rate with PDG scatter inflation,
exactly the M2 combination. The number that matters downstream is the
Def-group rate divided by the campaign 4192 rate: a MEASURED pilot_rate_scale
to replace the fitted one. The "Initial attempts" group is reported beside it
and not used for the scale: its name, its different time base, and its "adj"
subseries all say the configuration was still being adjusted.

CROSS-DAY CAUTION, inherited from run_epoch_checks check 3: a ruler measures
its OWN day's scan configuration. These traces are the pilot day's, which is
exactly why they are usable for the pilot axis and would not be for anything
else. The earlier ACF estimate on the Def combs (tooth period 144.2(11) ms)
was a seed; this module replaces it with the constrained comb fit.

Needs the pilot quarantine tree (private, read in place, never copied).
Without it the committed results/pilot_ruler.csv is the record; exits 0.
RB5S6S_PILOT_DIR is needed only to re-run this script against that private
working copy, and the committed CSVs are what the repository ships.

Writes results/pilot_ruler.csv.
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.ruler import fit_comb  # noqa: E402
from run_ruler import MHZ_PER_TOOTH, combine_rates  # noqa: E402

QP = Path(os.environ.get(
    "RB5S6S_PILOT_DIR", "~/rb-2025-quarantine/pilot")).expanduser()
GROUPS = {
    "def": QP / "EOM ruler" / "Def",
    "initial": QP / "EOM ruler" / "Initial attempts",
}
CAMPAIGN_4192_KEY = "4192"


def load_trace(path: Path):
    """Agilent 2-line-header CSV; the signal is the LAST voltage column
    (the Def group co-records the piezo ramp as its first one)."""
    d = np.genfromtxt(path, delimiter=",", skip_header=2)
    d = d[~np.isnan(d).any(axis=1)]
    return d[:, 0] * 1e3, d[:, -1]


def campaign_4192_rate() -> float:
    """The campaign 4192 P-session rate the pilot axis is scaled against,
    combined from its two brackets exactly as load_t_rates does (laser axis)."""
    rows = [r for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv"))
            if r["session"] == "P" and r["peak"] == CAMPAIGN_4192_KEY]
    rates = [float(r["rate"]) for r in rows]
    return float(np.mean(rates))


def main() -> int:
    if not QP.is_dir():
        print(f"pilot quarantine not on this machine ({QP}) -- the committed "
              f"results/pilot_ruler.csv is the record; nothing to do.")
        return 0

    out_rows = []
    group_rates = {}
    for gname, gdir in GROUPS.items():
        fits = []
        for p in sorted(gdir.glob("*.csv")):
            t, v = load_trace(p)
            try:
                f = fit_comb(t, v)
            except Exception as e:  # a ruler that cannot fit is reported, not hidden
                print(f"  {p.name}: fit failed ({e})")
                out_rows.append(["trace_failed", f"{gname}/{p.name}", "", "",
                                 "comb fit did not converge"])
                continue
            rate = MHZ_PER_TOOTH / f["delta_ms"]
            err = rate * f["delta_err_ms"] / f["delta_ms"]
            railed = (f["delta_ms"] - C.RULER_DELTA_RANGE_MS[0] < 0.5 or
                      C.RULER_DELTA_RANGE_MS[1] - f["delta_ms"] < 0.5)
            if railed:
                # nine pre-adjustment "Initial attempts" traces pin the comb
                # spacing at the fit's own lower bound: a different (not yet
                # adjusted) scan configuration, reported and never averaged
                out_rows.append(["trace_railed", f"{gname}/{p.name}",
                                f"{rate:.6f}", "",
                                f"delta at the {f['delta_ms']:.1f} ms fit "
                                f"bound: pre-adjustment configuration, "
                                f"excluded from every mean"])
                continue
            fits.append((p.name, rate, err, f["delta_ms"], f["chi2_red"]))
            out_rows.append(["trace_rate", f"{gname}/{p.name}", f"{rate:.6f}",
                            f"{err:.6f}",
                            f"MHz/ms laser; delta {f['delta_ms']:.2f} ms, "
                            f"chi2_red {f['chi2_red']:.2f}"])
        if len(fits) >= 3:
            r = np.array([x[1] for x in fits])
            e = np.array([x[2] for x in fits])
            mean, err, chi2 = combine_rates(r, e)
            group_rates[gname] = (mean, err, len(fits), chi2)
            print(f"  {gname}: {len(fits)} traces -> rate "
                  f"{mean:.6f} +/- {err:.6f} MHz/ms (chi2_red {chi2:.2f}, "
                  f"tooth {MHZ_PER_TOOTH/mean:.2f} ms)")
            out_rows.append(["group_rate", gname, f"{mean:.6f}", f"{err:.6f}",
                            f"MHz/ms laser; n={len(fits)}, PDG-inflated, "
                            f"chi2_red {chi2:.2f}"])

    if "def" in group_rates:
        camp = campaign_4192_rate()
        mean, err, n, _ = group_rates["def"]
        scale = mean / camp
        out_rows.append(["pilot_rate_scale_measured", "def_vs_camp4192",
                        f"{scale:.5f}", f"{err/camp:.5f}",
                        "the MEASURED replacement for M23/M25's fitted "
                        "pilot_rate_scale (which both fits put at 1.02-1.03 "
                        "inside a [0.9, 1.1] box); Def group only -- the "
                        "'Initial attempts' group is configuration-adjustment "
                        "data and is reported above, not used"])
        print(f"  MEASURED pilot_rate_scale = {scale:.5f} +/- {err/camp:.5f} "
              f"(fitted nuisance was 1.023-1.029)")

    C.RESULTS_DIR.mkdir(exist_ok=True)
    with open(C.RESULTS_DIR / "pilot_ruler.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(out_rows)
    print("  Wrote results/pilot_ruler.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
