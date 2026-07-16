#!/usr/bin/env python3
"""
M4e: the AC-Stark power-lever bound -- the power-lever twin of the beta_self fit.

Bounds the AC-Stark coefficient kappa (S0 = kappa*P) by jointly fitting the
committed 130 C FWHM-vs-power curve (results/power_sweep.csv, 4 peaks x 5
powers) with ONE shared kappa and a per-peak core width (rb5s6s.stark). In the
2025 archive the shift (pull ~S0) is dead (drifted lock), so kappa is
constrained ONLY through the ramp's width broadening (~S0^2) -- a weak handle,
hence a one-sided UPPER BOUND, not a measurement. It brackets the predicted S0
and validates the fixed-lock session method; the fixed lock measures the pull ~S0
directly (and at a smaller waist, S0 ~4x larger).

Writes results/stark_sweep.csv. Reads results/power_sweep.csv (run M6 first).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.stark import fit_stark_sweep  # noqa: E402


def main() -> int:
    grid = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "power_sweep.csv")):
        grid[(r["peak"], float(r["power_mW"]) / 1000.0)] = (
            float(r["fwhm"]), float(r["fwhm_err"]))
    res = fit_stark_sweep(grid)

    print("=" * 74)
    print("(M4e) AC-STARK POWER-LEVER BOUND: kappa from FWHM-vs-power at 130 C")
    print(f"  {res['n']} width points (4 peaks x 5 powers), chi2_red = {res['chi2_red']:.2f}")
    print(f"  (chi2>1: block-to-block width scatter exceeds statistical; the covariance")
    print(f"   is rescaled by it, so the bound below is conservative.)\n")
    print(f"  kappa = {res['kappa']:.2f} +/- {res['kappa_err']:.2f} MHz/W "
          f"(consistent with 0 and with the predicted {res['kappa_pred']:.2f})")
    print(f"  => S0(225 mW):  fit {res['S0_225_fit']:.2f}   "
          f"predicted {res['S0_225_pred']:.2f}")
    print(f"  **95% UPPER BOUND (profile likelihood) {res['S0_225_ub95_profile']:.2f} MHz**")
    print(f"  (The fit rails at kappa=0 where the width handle has zero gradient, so")
    print(f"   the Wald bounds -- raw {res['S0_225_ub95_raw']:.2f}, chi2-inflated "
          f"{res['S0_225_ub95']:.2f} -- have no valid coverage there;")
    print(f"   they are kept in the CSV as diagnostics. The profile scans kappa with the")
    print(f"   per-peak cores re-minimized, threshold Dchi2 = 2.706 x chi2_red = "
          f"{res['profile_delta_chi2']:.2f}.)")
    verdict = ("brackets the prediction (cannot distinguish it from 0)"
               if res["S0_225_ub95_profile"] > res["S0_225_pred"] else
               "BELOW the prediction -- tension, inspect")
    print(f"  The archive {verdict}.")
    print(f"  per-peak core sigma_laser (transition): "
          + "  ".join(f"993.{p}={s:.2f}" for p, s in res["sigma_laser_by_peak"].items()))
    print("\n  This is a BOUND because the shift (pull ~S0) is dead in the 2025 drift;")
    print("  only the ramp's width broadening (~S0^2) constrains kappa here. The fixed-lock session's")
    print("  fixed lock measures the pull ~S0 directly -> the actual coefficient.")

    with open(C.RESULTS_DIR / "stark_sweep.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerow(["kappa", "shared", f"{res['kappa']:.3f}", f"{res['kappa_err']:.3f}",
                    "MHz per W (S0 = kappa*P, transition axis); err is chi2-INFLATED"])
        w.writerow(["kappa_err_raw", "shared", f"{res['kappa_err_raw']:.3f}",
                    f"{res['chi2_inflation']:.2f}",
                    "value=un-inflated kappa error; err=inflation factor sqrt(chi2_red) applied to get kappa_err"])
        w.writerow(["kappa_ub95_profile", "shared", f"{res['kappa_ub95_profile']:.3f}", "",
                    "one-sided 95% upper bound on kappa (MHz per W), profile likelihood: Dchi2 = 2.706 x max(chi2_red,1) with per-peak cores re-minimized at each kappa -- THE quoted construction (the fit rails at kappa=0 where the Wald error has no coverage)"])
        w.writerow(["S0_225mW_ub95_profile", "shared", f"{res['S0_225_ub95_profile']:.3f}", "",
                    "95% upper bound on S0 at 225 mW (MHz, transition), profile likelihood -- the archival BOUND"])
        w.writerow(["kappa_ub95", "shared", f"{res['kappa_ub95']:.3f}", "",
                    "SUPERSEDED diagnostic: linearized (Wald) bound from the chi2-inflated error; evaluated at the kappa=0 rail where the width handle's gradient vanishes, so its sigma is a finite-difference artifact without 95% coverage"])
        w.writerow(["S0_225mW_fit", "shared", f"{res['S0_225_fit']:.3f}", "",
                    "fitted on-axis AC-Stark shift at 225 mW (MHz, transition)"])
        w.writerow(["S0_225mW_ub95", "shared", f"{res['S0_225_ub95']:.3f}", "",
                    "SUPERSEDED diagnostic: Wald chi2-inflated bound (MHz); kept for continuity with earlier ledgers -- quote the profile row instead"])
        w.writerow(["S0_225mW_ub95_raw", "shared", f"{res['S0_225_ub95_raw']:.3f}", "",
                    "SUPERSEDED diagnostic: un-inflated Wald bound (MHz)"])
        w.writerow(["S0_225mW_pred", "shared", f"{res['S0_225_pred']:.3f}", "",
                    "predicted S0 at 225 mW (w0=50um prior, rho=1) for comparison"])
        w.writerow(["S0_225mW_pred_lo", "shared", f"{res['S0_225_pred_lo']:.3f}", "",
                    "predicted S0 at 225 mW, w0=70um (band LOW edge, rho=1)"])
        w.writerow(["S0_225mW_pred_hi", "shared", f"{res['S0_225_pred_hi']:.3f}", "",
                    "predicted S0 at 225 mW, w0=45um (band HIGH edge, rho=1)"])
        w.writerow(["chi2_red", "fit", f"{res['chi2_red']:.3f}", "",
                    f"over {res['n']} width points"])
        for p, s in res["sigma_laser_by_peak"].items():
            w.writerow(["core_sigma_laser", f"993.{p}nm", f"{s:.3f}", "",
                        "per-peak power-independent core width (MHz, transition)"])
    print("\n  Wrote results/stark_sweep.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
