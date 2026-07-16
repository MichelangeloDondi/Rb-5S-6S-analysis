#!/usr/bin/env python3
"""
M12: is the width decomposition identifiable? -- the covariance and condition
number of (gamma_coll, sigma_laser, transit) on a representative bright line.

The three widths all broaden the same ~5 MHz line, so the analysis FIXES transit
(from the w0 prior) and reports sigma_laser as a bound. This driver quantifies
why: it fits one bright condition with all three widths free and reads off their
correlation matrix, condition number, and best/worst-constrained directions --
showing the archive constrains the TOTAL width well but the SPLIT poorly.

Writes results/identifiability.csv. Reads results/ruler_blocks.csv (rate).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.identifiability import width_identifiability, WIDTHS  # noqa: E402

# a bright, well-behaved condition gives the cleanest covariance: 993.4192 nm
# (85Rb F3, the strongest line) at 130 C / 225 mW.
PEAK, POWER = "4192", "225"


def main() -> int:
    rows = load_manifest()
    prate = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        if r["session"] == "P":
            prate.setdefault(r["peak"], []).append(2.0 * float(r["rate"]))
    rate = float(np.mean(prate[PEAK]))

    freqs, volts = [], []
    for r in rows:
        if not (r["flag"] == "canonical" and r["role"] == "p_sweep"
                and r["peak"] == PEAK and r["power_mW"] == POWER):
            continue
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate)); volts.append(v)

    law = condition_noise_model(volts)
    r = width_identifiability(freqs, volts, law=law)

    print("=" * 74)
    print(f"(M12) WIDTH IDENTIFIABILITY on 993.{PEAK} nm, 130 C / {POWER} mW "
          f"({len(volts)} repeats)")
    print("  fit with gamma_coll, sigma_laser, transit ALL free (MHz, transition):")
    print("    " + "  ".join(f"{w}={r['fit'][w]:.2f}" for w in WIDTHS))
    print("\n  correlation matrix:")
    print("             " + "  ".join(f"{w[:9]:>9s}" for w in WIDTHS))
    for i, w in enumerate(WIDTHS):
        print(f"    {w:11s} " + "  ".join(f"{r['corr'][i][j]:+9.3f}" for j in range(3)))
    print(f"\n  condition number = {r['condition_number']:.0f}  "
          f"(>>1 => the split is ill-constrained)")
    print(f"  best-constrained direction  (1sigma {r['best_constrained_sigma']:.3f} MHz): "
          + ", ".join(f"{w} {r['best_constrained_dir'][w]:+.2f}" for w in WIDTHS))
    print(f"  worst-constrained direction (1sigma {r['worst_constrained_sigma']:.3f} MHz): "
          + ", ".join(f"{w} {r['worst_constrained_dir'][w]:+.2f}" for w in WIDTHS))
    print(f"  => the degenerate split is constrained "
          f"{r['worst_constrained_sigma'] / max(r['best_constrained_sigma'], 1e-9):.0f}x worse "
          f"than the total width.")

    with open(C.RESULTS_DIR / "identifiability.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "unit"])
        w.writerow(["condition_number", "width_block", f"{r['condition_number']:.1f}",
                    "eigenvalue ratio of the (gamma_coll,sigma_laser,transit) covariance; >>1 = degenerate"])
        for i in range(3):
            for j in range(i, 3):
                w.writerow(["corr", f"{WIDTHS[i]}_{WIDTHS[j]}", f"{r['corr'][i][j]:.3f}",
                            "width-width correlation coefficient"])
        w.writerow(["best_constrained_sigma", "total_width", f"{r['best_constrained_sigma']:.4f}",
                    "MHz; 1sigma on the best-constrained width combination (~the total)"])
        w.writerow(["worst_constrained_sigma", "split", f"{r['worst_constrained_sigma']:.4f}",
                    "MHz; 1sigma on the degenerate split direction"])
    print("\n  READING: the archive pins the TOTAL width tightly but the SPLIT loosely,")
    print("  so gamma_coll / sigma_laser / transit are w0-conditional bounds, not")
    print("  measurements -- the knife-edge w0 fixes transit to within its own")
    print("  precision and COLLAPSES the degeneracy (not removes it exactly).")
    print("  Wrote results/identifiability.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
