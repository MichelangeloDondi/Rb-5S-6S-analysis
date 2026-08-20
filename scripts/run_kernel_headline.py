#!/usr/bin/env python3
"""K1: what the LASER KERNEL costs the HEADLINE coefficient, with a producer.

WHY THIS FILE EXISTS AT ALL. On 2026-08-20 the headline kernel figure -- the
one every public surface quotes -- was produced by a hand-driven run in a
detached worktree and never committed as a producer. The number reached five
documents; the code that made it reached none of them. A number whose producer
is not in the tree cannot be re-run when the model changes, and the model
changed the next morning. This is that producer.

WHAT IT MEASURES. `fit_beta_self` is the record's own hierarchical estimator:
one peak, all its temperatures at once, a collisional slope beta_self shared
with a single laser width. That is the construction the headline uses, and it
is a DIFFERENT estimator from the per-condition fits of M38, with a different
degeneracy structure. Each peak is fitted twice, differing only in laser_kind.

WHY THE TWO ARMS ARE NOT SYMMETRIC, which is the whole point. At a FIXED
condition a Lorentzian laser width and a collisional width enter the profile
only through their sum, so the split between them is not identified at all
(results/kernel_identifiability.csv measures this: sum-preserving moves leave the
profile invariant to machine zero). What can break that degeneracy is DENSITY,
because the collisional part scales with it and the laser part does not, and
density is exactly what this estimator varies. So the question this producer
answers is not "how much does beta move" but the prior one:

    IS beta_self IDENTIFIED AT ALL UNDER A LORENTZIAN LASER KERNEL,
    AND IF SO, HOW WELL?

The reported correlation between beta_self and the shared laser width is the
answer. A correlation approaching -1 says the density lever is not breaking
the degeneracy and the Lorentzian arm's beta is positioned by the optimiser
rather than by the data; the shift would then be a number without a referent.

    python scripts/run_kernel_headline.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                                   # noqa: E402
from rb5s6s.ingest import load_manifest                          # noqa: E402
from rb5s6s.qc import outlier_files                              # noqa: E402
from rb5s6s.beta import fit_beta_self                            # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_beta_self import PEAKS, load_conditions, load_t_rates   # noqa: E402

OUT = C.RESULTS_DIR / "kernel_headline.csv"
KINDS = ("gaussian", "lorentzian")


def main() -> int:
    rows = load_manifest()
    dropped = outlier_files()
    if dropped:
        rows = [r for r in rows if r["file"] not in dropped]
    trates, prates = load_t_rates()

    out = []
    for peak in PEAKS:
        conds = load_conditions(rows, peak, trates, prates)
        if len(conds) < 2:
            print(f"[skip] {peak}: {len(conds)} temperatures")
            continue
        fits = {}
        for kind in KINDS:
            fits[kind] = fit_beta_self(
                conds, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ,
                laser_kind=kind)
        bg, bl = (float(fits[k]["beta_self"]) for k in KINDS)
        eg, el = (float(fits[k]["beta_self_err"]) for k in KINDS)
        sg, sl = (float(fits[k]["sigma_laser"]) for k in KINDS)
        cg, cl = (float(fits[k]["corr_beta_laser"]) for k in KINDS)
        out.append(dict(
            peak=peak, n_temperatures=len(conds),
            beta_gaussian=f"{bg:.6f}", beta_lorentzian=f"{bl:.6f}",
            beta_frac_shift=f"{(bl - bg) / bg:+.6f}",
            beta_shift_in_sigma=f"{(bl - bg) / eg:+.2f}",
            beta_err_gaussian=f"{eg:.6f}", beta_err_lorentzian=f"{el:.6f}",
            sigma_laser_gaussian=f"{sg:.6f}", sigma_laser_lorentzian=f"{sl:.6f}",
            corr_beta_laser_gaussian=f"{cg:+.4f}",
            corr_beta_laser_lorentzian=f"{cl:+.4f}",
            chi2_red_gaussian=f"{float(fits['gaussian']['chi2_red']):.6f}",
            chi2_red_lorentzian=f"{float(fits['lorentzian']['chi2_red']):.6f}",
            status="DIAGNOSTIC"))
        print(f"  {peak}: beta {bg:.4f} -> {bl:.4f} "
              f"({(bl-bg)/bg*100:+.1f}%, {(bl-bg)/eg:+.1f} sigma)   "
              f"corr(beta,laser) {cg:+.3f} -> {cl:+.3f}")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"\nwrote {OUT}  ({len(out)} peaks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
