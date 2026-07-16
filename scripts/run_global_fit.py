#!/usr/bin/env python3
"""
M4b: the hierarchical cross-peak + cross-temperature fit on real data.

Fits all 4 peaks x 3 T-sweep temperatures at once (rb5s6s.global_fit):
sigma_laser shared per temperature across peaks, beta_self per isotope,
transit shared. Reports beta_85 vs beta_87, the sigma_laser(T) drift the
sharing exposes, and a leave-one-condition-out (LOO) robustness scan of the
shared parameters.

Reads results/ruler_blocks.csv for per-block rates. All PRELIMINARY: absolute
beta still rides on the OPEN w0/transit prior, and this is a MODEL-BASED
cross-check of the model-independent raw-width bound (run_beta_self.py), not a
replacement.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import PEAKS as PEAKINFO, transit_fwhm_from_w0  # noqa: E402
from rb5s6s.density import density_units, N_SCALE_FRAC_SYST  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.global_fit import fit_global  # noqa: E402

TSWEEP = ("70", "90", "110")


def build_blocks(rows, trates):
    blocks = []
    for peak in ("4121", "4154", "4192", "4207"):
        iso = PEAKINFO[peak]["isotope"]
        for T in TSWEEP:
            if (peak, T) not in trates:
                continue
            rate = trates[(peak, T)]
            recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                    and r["peak"] == peak and r["temperature_C"] == T]
            freqs, volts = [], []
            for r in recs:
                t, v, info = load_trace(trace_path(r), with_info=True)
                m = trace_metrics(t, v)
                if any("truncated" in f or "dropout" in f
                       for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
                    continue
                freqs.append(to_frequency(t, rate)); volts.append(v)
            if len(volts) >= 3:
                blocks.append({"peak": peak, "isotope": iso, "T_C": float(T),
                               "N_units": density_units(float(T)),
                               "freqs": freqs, "volts": volts,
                               "law": condition_noise_model(volts)})
    return blocks


def main() -> int:
    rows = load_manifest()
    trates = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        if r["session"] == "T":
            # rate_err omitted deliberately: a block-coherent axis-scale error
            # moves beta by <= beta * relerr ~ 0.0006 (relerr <= 1.8%), far under
            # the +/-0.004 stat bar and the 0.01-0.03 systematics; a rigorous
            # treatment needs per-block scale nuisances, out of scope for a
            # sub-dominant term (review finding 4, 2026-07-16)
            trates[(r["peak"], r["T"])] = 2.0 * float(r["rate"])

    blocks = build_blocks(rows, trates)
    fit = fit_global(blocks, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    # same fit with a Gaussian (Voigt, no cusp) transit -> the model-form
    # systematic on beta (the third error bar: statistical | model-form | w0).
    fit_voigt = fit_global(blocks, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ,
                           transit_kind="gaussian")

    print("=" * 74)
    print("(M4b) HIERARCHICAL FIT: sigma_laser per T (shared over peaks), beta per isotope")
    print(f"  chi2_red = {fit['chi2_red']:.2f} over {fit['n_traces']} traces\n")
    print("  beta_self per isotope (MHz per 1e12 cm^-3; PRELIMINARY, w0-degenerate):")
    for iso in fit["beta_keys"]:
        b, e = fit["beta_by_isotope"][iso], fit["beta_err_by_isotope"][iso]
        print(f"     {iso}Rb: {b:.4f} +/- {e:.4f}")
    b85, b87 = fit["beta_by_isotope"][85], fit["beta_by_isotope"][87]
    de = np.hypot(fit["beta_err_by_isotope"][85], fit["beta_err_by_isotope"][87])
    print(f"     -> beta_85 - beta_87 = {b85-b87:+.4f} +/- {de:.4f} "
          f"({abs(b85-b87)/de:.1f}sigma; collisional physics may differ by isotope)")
    print("\n  sigma_laser per temperature (transition axis) -- the drift the")
    print("  cross-peak sharing EXPOSES (M4's dominant systematic, now measured):")
    for T in fit["sig_keys"]:
        s, e = fit["sigma_laser_by_T"][T], fit["sigma_laser_err_by_T"][T]
        print(f"     {T:.0f}C: {s:.2f} +/- {e:.2f} MHz  ({s/2:.2f} laser axis)")
    sl = [fit["sigma_laser_by_T"][T] for T in fit["sig_keys"]]
    print(f"     span {max(sl)-min(sl):.2f} MHz across the cooling session "
          f"({'DRIFTS' if max(sl)-min(sl) > 0.2 else 'stable'})")

    # ---- Voigt vs Lehmann model-form systematic on beta (the 3rd error bar) ----
    print(f"\n{'-'*74}\nMODEL-FORM SYSTEMATIC on beta (transit kernel: Lehmann exp vs Voigt Gaussian):")
    mf_syst = {}
    for iso in fit["beta_keys"]:
        bl = fit["beta_by_isotope"][iso]
        bv = fit_voigt["beta_by_isotope"][iso]
        mf_syst[iso] = abs(bl - bv)
        tag = ("< stat err -> INSENSITIVE to transit form"
               if mf_syst[iso] < fit["beta_err_by_isotope"][iso]
               else "COMPARABLE to stat -> quote as a systematic")
        print(f"  beta_{iso}: Lehmann {bl:.4f}, Voigt {bv:.4f}, |diff| {mf_syst[iso]:.4f}  ({tag})")
    print("  This |diff| is the transit-model-form error bar the paper quotes ALONGSIDE")
    print("  the statistical error and the w0-band systematic (three separate bars).")

    # persist the result (was stdout-only -- revision #6/round-3 gap): the
    # per-isotope beta and sigma_laser(T) belong in a committed CSV so the
    # README/ledger claim is verifiable without a run.
    with open(C.RESULTS_DIR / "global_fit.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        for iso in fit["beta_keys"]:
            w.writerow(["beta_self", f"{iso}Rb", f"{fit['beta_by_isotope'][iso]:.4f}",
                        f"{fit['beta_err_by_isotope'][iso]:.4f}", "MHz per 1e12 cm^-3"])
        for T in fit["sig_keys"]:
            w.writerow(["sigma_laser", f"{T:.0f}C", f"{fit['sigma_laser_by_T'][T]:.3f}",
                        f"{fit['sigma_laser_err_by_T'][T]:.3f}", "MHz transition"])
        w.writerow(["chi2_red", "global", f"{fit['chi2_red']:.3f}", "", ""])
        for iso in fit["beta_keys"]:
            w.writerow(["beta_modelform_syst", f"{iso}Rb", f"{mf_syst[iso]:.4f}", "",
                        "MHz per 1e12 cm^-3 (|Lehmann - Voigt transit|)"])
        for iso in fit["beta_keys"]:
            w.writerow(["beta_nscale_syst", f"{iso}Rb",
                        f"{abs(fit['beta_by_isotope'][iso]) * N_SCALE_FRAC_SYST:.4f}",
                        "",
                        f"MHz per 1e12 cm^-3 (density-SCALE systematic: beta ~ 1/N, "
                        f"so the {N_SCALE_FRAC_SYST:.0%} vapor-pressure-correlation "
                        f"spread moves beta by the same fraction; density.py)"])
        w.writerow(["noise_floor_limited", "global",
                    str(fit["noise_floor_limited"]), "",
                    "chi2_red < 0.8: the errors are set by the conservative "
                    "noise model (tau inflation), not by the fit residuals"])
        w.writerow(["params_at_bound", "global",
                    ";".join(fit["params_at_bound"]) or "none", "",
                    "shared parameters pinned at their 0 rail, where the "
                    "symmetric Gaussian error is one-sided in truth"])

    # ---- w0 systematic band on beta (review round 5 #4) ----
    # transit_ref comes from the OPEN w0 prior (central 50 um; the old 32 um is
    # EXCLUDED by the corrected transit physics). Every absolute beta rides on it,
    # so refit across the corrected-physics w0 band (65/50/40 um, bracketing the
    # inferred 45-70) and report the beta SPREAD as the w0 systematic, so the OPEN
    # quantity does not silently enter the quoted number.
    print(f"\n{'-'*74}\nw0 SYSTEMATIC on beta (transit_ref band from the OPEN w0 prior):")
    print(f"  {'transit':>8s} {'~w0':>6s} " + "  ".join(f"beta_{iso}" for iso in fit["beta_keys"]))
    band = {iso: [] for iso in fit["beta_keys"]}
    for w0_um in (65.0, 50.0, 40.0):
        tr = transit_fwhm_from_w0(w0_um * 1e-6, 110.0)
        fb = fit_global(blocks, transit_ref_mhz=tr)
        for iso in fb["beta_keys"]:
            band[iso].append(fb["beta_by_isotope"][iso])
        print(f"  {tr:>8.2f} {f'{w0_um:.0f}um':>6s} "
              + "  ".join(f"{fb['beta_by_isotope'][iso]:.4f}" for iso in fb["beta_keys"]))
    for iso in fit["beta_keys"]:
        lo, hi = min(band[iso]), max(band[iso])
        print(f"  => beta_{iso}: stat {fit['beta_by_isotope'][iso]:.3f}"
              f"({fit['beta_err_by_isotope'][iso]*1e3:.0f}) "
              f"+w0syst [{lo:.3f}, {hi:.3f}] (the w0 band DOMINATES the error)")
    print("  Conditional on w0; only the knife-edge measurement collapses this band.")

    # ---- leave-one-condition-out robustness ----
    print(f"\n{'-'*74}\nLEAVE-ONE-CONDITION-OUT (does one block move a shared parameter?):")
    base85, base87 = b85, b87
    worst = (0.0, "")
    for drop in range(len(blocks)):
        sub = [b for i, b in enumerate(blocks) if i != drop]
        try:
            f2 = fit_global(sub, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        except RuntimeError:
            continue
        d85 = abs(f2["beta_by_isotope"][85] - base85)
        d87 = abs(f2["beta_by_isotope"][87] - base87)
        dd = max(d85, d87)
        if dd > worst[0]:
            worst = (dd, f"{blocks[drop]['peak']} {blocks[drop]['T_C']:.0f}C "
                         f"(dbeta85={d85:+.4f}, dbeta87={d87:+.4f})")
    print(f"  largest beta shift from dropping any one block: {worst[0]:.4f} "
          f"by {worst[1]}")
    print(f"  (compare to the formal beta errors ~{de/np.sqrt(2):.4f}; "
          f"{'ROBUST' if worst[0] < 2*de else 'one block dominates -- inspect'})")

    print(f"\n{'-'*74}\nNOTE: model-based cross-check only; absolute beta still w0-limited, and")
    print("the headline archival result remains the model-independent raw-width BOUND")
    print("(run_beta_self.py). Here the value is: it tests beta_85 vs beta_87 and turns")
    print("the between-block laser drift into a measured sigma_laser(T).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
