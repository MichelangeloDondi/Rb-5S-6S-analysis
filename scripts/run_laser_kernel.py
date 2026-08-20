#!/usr/bin/env python3
"""M38: what the LASER KERNEL'S SHAPE costs, as a model-form systematic.

THE GAP THIS FILLS. `laser_kind` is a parameter of `composite_profile`,
`model_profile`, `fit_condition` and `beta.py`. It is plumbed end to end
through four modules and, until 2026-08-20, was never called with anything
but "gaussian". The switch existed and had never been thrown.

WHY IT IS THE CONSEQUENTIAL SWITCH. The record already carries a model-form
systematic for the TRANSIT kernel, run under both forms with the difference
quoted as an error bar. The transit kernel is a separate convolution, so
changing it changes the shape. A Lorentzian LASER kernel is different in kind:
Lorentzians add linearly, so a Lorentzian laser width is degenerate with
gamma_coll and competes with it for the same wings. Changing that assumption
does not merely change the fit quality, it MOVES THE COLLISIONAL NUMBER.

WHAT THIS PRODUCER DOES. Each canonical condition is fitted TWICE on the same
traces, the same noise law, the same trim, differing only in `laser_kind`. It
reports gamma_coll and sigma_laser under each, their difference, and the
chi-square difference that says whether the archive can tell the two apart.

WHAT IT IS NOT. Not a claim that the laser is Lorentzian. The kernel follows
from the noise TYPE, which docs/wiki records as unmeasured, and the comb
bounds an excursion rather than identifying a spectrum. This measures what
the ASSUMPTION costs, not which assumption is right.

The reading was preregistered before the first run, in
private/reviews/PREREG_laser_kernel_2026-08-20.md.

    python scripts/run_laser_kernel.py
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path   # noqa: E402
from rb5s6s.noise import condition_noise_model                    # noqa: E402
from rb5s6s.qc import (trace_metrics, hard_flags, ingest_flags,   # noqa: E402
                       outlier_files)
from rb5s6s.linefit import (fit_condition, to_frequency,          # noqa: E402
                            transit_fwhm_at_T)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_linefit import load_block_rates, condition_rate          # noqa: E402

OUT = C.RESULTS_DIR / "laser_kernel.csv"
KINDS = ("gaussian", "lorentzian")


def main() -> int:
    rows = load_manifest()
    trate, prate = load_block_rates()
    dropped = outlier_files()

    conds = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["rf_on"] == "False":
            conds[(r["role"], r["peak"], r["temperature_C"], r["power_mW"])].append(r)

    print(f"M38: the laser kernel as a model form, {len(conds)} conditions, "
          f"each fitted under {' and '.join(KINDS)}")

    out = []
    for key in sorted(conds):
        role, peak, T, P = key
        entry = condition_rate(role, peak, T, trate, prate)
        if entry is None:
            continue
        rate, _ = entry
        freqs, volts = [], []
        for r in conds[key]:
            if r["file"] in dropped:
                continue
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f for f in
                   hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate))
            volts.append(v)
        if len(volts) < 3:
            continue
        law = condition_noise_model(volts)
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)

        fits = {}
        for kind in KINDS:
            try:
                fits[kind] = fit_condition(freqs, volts, T_C=float(T), law=law,
                                           transit_fwhm=transit, trim_tails=True,
                                           laser_kind=kind)
            except RuntimeError as e:
                print(f"  [warn] {key} {kind}: {e}")
        if len(fits) != len(KINDS):
            continue

        g_g = float(fits["gaussian"]["gamma_coll"])
        g_l = float(fits["lorentzian"]["gamma_coll"])
        s_g = float(fits["gaussian"]["sigma_laser"])
        s_l = float(fits["lorentzian"]["sigma_laser"])
        c_g = float(fits["gaussian"]["chi2_red"])
        c_l = float(fits["lorentzian"]["chi2_red"])
        frac = (g_l - g_g) / g_g if g_g > 0 else float("nan")
        out.append({
            "role": role, "peak": peak, "T": T, "P": P,
            "gamma_coll_gaussian": f"{g_g:.6f}",
            "gamma_coll_lorentzian": f"{g_l:.6f}",
            "gamma_coll_frac_shift": f"{frac:.6f}",
            "sigma_laser_gaussian": f"{s_g:.6f}",
            "sigma_laser_lorentzian": f"{s_l:.6f}",
            "chi2_red_gaussian": f"{c_g:.6f}",
            "chi2_red_lorentzian": f"{c_l:.6f}",
            "chi2_red_diff": f"{c_l - c_g:+.6f}",
        })
        print(f"  {role} {peak} {T}C {P}mW: gamma_coll {g_g:.4f} -> {g_l:.4f} "
              f"({frac:+.1%}), chi2_red {c_g:.4f} -> {c_l:.4f}")

    if not out:
        print("no conditions fitted under both kernels")
        return 1

    fr = np.array([float(r["gamma_coll_frac_shift"]) for r in out])
    dc = np.array([float(r["chi2_red_diff"]) for r in out])
    print(f"\n  median fractional shift in gamma_coll: {np.median(fr):+.1%}")
    print(f"  conditions where it falls: {int((fr < 0).sum())} of {fr.size}")
    print(f"  median chi2_red difference (lorentzian minus gaussian): "
          f"{np.median(dc):+.4f}")
    print(f"  conditions the Lorentzian kernel fits better: "
          f"{int((dc < 0).sum())} of {dc.size}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"\nwrote {OUT.relative_to(C.REPO_ROOT)}  ({len(out)} conditions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
