#!/usr/bin/env python3
"""
M14: is the per-T sigma_laser sharing statistically warranted? A BIC comparison.

Fits the hierarchical model two ways with the SAME machinery (global_fit) --
sigma_laser shared per temperature (Model A, per_T) vs free per (peak, T) block
(Model B, per_block) -- and compares by BIC. The archive's traces are heavily
over-sampled (correlated), so the primary score uses the correlation-corrected
effective sample size N_eff = N/tau (the naive raw-N BIC over-counts and FLIPS
the verdict -- reported as a cautionary diagnostic). Quantifies the M4c sharing
check; BIC scores PARSIMONY, not the physical sharing (rb5s6s/sharing_bic.py).

Reads results/ruler_blocks.csv; writes results/sharing_bic.csv.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # sibling-script reuse
from rb5s6s import config as C  # noqa: E402
from rb5s6s.ingest import load_manifest  # noqa: E402
from rb5s6s.sharing_bic import sharing_bic  # noqa: E402
from run_global_fit import build_blocks  # noqa: E402  (reuse the exact block loader)


def main() -> int:
    rows = load_manifest()
    trates = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        if r["session"] == "T":
            trates[(r["peak"], r["T"])] = 2.0 * float(r["rate"])
    blocks = build_blocks(rows, trates)

    res = sharing_bic(blocks, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    A, B = res["models"]["per_T"], res["models"]["per_block"]

    print("=" * 74)
    print("(M14) sigma_laser SHARING BIC: per-T (shared) vs per-block (independent)")
    print(f"  per_block adds {res['delta_k']} sigma_laser params; "
          f"raw N={A['n_raw']}, effective N={A['n_eff']:.0f} (tau~{res['tau_mean']:.1f})\n")
    print(f"  {'model':<20} {'k':>4} {'chi2_red':>9} {'BIC_eff':>10} {'BIC_raw':>10}")
    print(f"  {'A  per_T (shared)':<20} {A['k']:>4} {A['chi2_red']:>9.3f} {A['bic_eff']:>10.1f} {A['bic_raw']:>10.1f}")
    print(f"  {'B  per_block':<20} {B['k']:>4} {B['chi2_red']:>9.3f} {B['bic_eff']:>10.1f} {B['bic_raw']:>10.1f}")
    print(f"\n  PRIMARY  dBIC (effective N) = {res['dBIC']:+.1f}"
          f"  ({res['verdict']}; favours {res['favours']})")
    print(f"  diagnostic dBIC (raw N)    = {res['dBIC_raw']:+.1f}"
          f"  ({'AGREES' if res['robust'] else 'FLIPS -- the correlated-sample trap'})\n")
    print("  READING: the correlation-corrected BIC favours the shared model -- the")
    print("  archive cannot pay for per-block sigma_laser freedom once the ~3.5x")
    print("  spectral over-sampling is accounted for. This is Occam/parsimony, NOT")
    print("  proof the four peaks shared one laser width (the unlogged timing forbids")
    print("  that; M4c). That the naive raw-N BIC flips to per_block is the honest")
    print("  caveat: the archive does not ROBUSTLY resolve shared-vs-independent, so")
    print("  the headline stays the model-independent width-slope bound (C1).")

    with open(C.RESULTS_DIR / "sharing_bic.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "unit"])
        for name, m in (("per_T", A), ("per_block", B)):
            w.writerow(["bic_eff", name, f"{m['bic_eff']:.1f}",
                        f"correlation-corrected chi2 + k*ln(N_eff); k={m['k']}, N_eff={m['n_eff']:.0f}"])
            w.writerow(["chi2_red", name, f"{m['chi2_red']:.3f}", "raw chi2 / dof"])
        w.writerow(["dBIC_eff_block_minus_T", "shared", f"{res['dBIC']:.1f}",
                    f"PRIMARY: +ve favours per_T (shared); {res['verdict']} (Kass-Raftery); "
                    f"Occam on underpowered data, NOT sharing proof (M4c)"])
        w.writerow(["dBIC_raw_block_minus_T", "shared", f"{res['dBIC_raw']:.1f}",
                    "diagnostic: naive raw-N BIC (over-counts correlated samples; "
                    "flips sign -> the archive does not robustly resolve the sharing)"])
    print("  Wrote results/sharing_bic.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
