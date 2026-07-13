#!/usr/bin/env python3
"""
M3 real-data shakedown: joint lineshape fit of every canonical RF-off
condition, end-to-end through M0->M1->M2->M3.

PRELIMINARY by construction — read before using any number:
  * the transit width rides on w0 (OPEN until the October knife-edge); it is
    FIXED here at a placeholder (config.TRANSIT_FWHM_PLACEHOLDER_MHZ at 110 C
    with sqrt(T) scaling). Absolute sigma_laser and gamma_coll inherit that
    assumption AND the -0.9 laser<->coll degeneracy (see linefit.py).
  * The DEGENERACY-ROBUST observable is the TOTAL Voigt FWHM per condition
    and its temperature trend — reported first. gamma_coll(T) is shown but
    is preliminary; beta_self proper (with the confound program, N(T), and
    the w0 prior) is module M4.

Rate assignment (per condition -> its M2 block rate, transition axis):
  * T-sweep line (peak, T)  -> ruler_t block (peak, T)
  * P-sweep line (peak,130) -> mean of that peak's before/after brackets
Missing a rate -> the condition is skipped with a printed note (never a
silent fallback).

Outputs: results/linefit_conditions.csv + stdout trend tables.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ, TOOTH_SPACING_LASER_HZ  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import fit_condition, to_frequency, transit_fwhm_at_T  # noqa: E402
from rb5s6s.lineshape import voigt_fwhm  # noqa: E402

GNAT = GAMMA_NAT_HZ / 1e6
MHZ_TOOTH = TOOTH_SPACING_LASER_HZ / 1e6


def load_block_rates():
    """Read M2 results/ruler_blocks.csv -> transition-axis rate per block.
    Returns dicts keyed for T-sweep and P-sweep line lookups."""
    path = C.RESULTS_DIR / "ruler_blocks.csv"
    if not path.exists():
        raise SystemExit("run scripts/run_ruler.py first (need results/ruler_blocks.csv)")
    trate, pbrackets = {}, defaultdict(dict)
    for r in csv.DictReader(open(path)):
        rate_transition = 2.0 * float(r["rate"])  # laser -> transition axis
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = rate_transition
        else:
            pbrackets[r["peak"]][r["bracket"]] = rate_transition
    prate = {}
    for peak, br in pbrackets.items():
        vals = list(br.values())
        prate[peak] = float(np.mean(vals)) if vals else None
    return trate, prate


def condition_rate(role, peak, T, trate, prate):
    if role == "t_sweep":
        return trate.get((peak, T))
    return prate.get(peak)  # p_sweep all at 130 C, bracketed


def main() -> int:
    rows = load_manifest()
    trate, prate = load_block_rates()

    conds = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["rf_on"] == "False":
            conds[(r["role"], r["peak"], r["temperature_C"], r["power_mW"])].append(r)

    print(f"M3 shakedown: {len(conds)} canonical RF-off conditions "
          f"(transit FIXED at placeholder {C.TRANSIT_FWHM_PLACEHOLDER_MHZ} MHz@110C, w0 OPEN)")
    out = []
    for key in sorted(conds):
        role, peak, T, P = key
        rate = condition_rate(role, peak, T, trate, prate)
        if rate is None:
            print(f"  [skip] {key}: no M2 rate"); continue
        freqs, volts = [], []
        for r in conds[key]:
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f for f in
                   hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate)); volts.append(v)
        if len(volts) < 3:
            print(f"  [skip] {key}: {len(volts)} usable traces"); continue
        law = condition_noise_model(volts)
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        try:
            fit = fit_condition(freqs, volts, T_C=float(T), law=law, transit_fwhm=transit)
        except RuntimeError as e:
            print(f"  [warn] fit failed {key}: {e}"); continue
        # total width = numerical FWHM of the full composite model at the
        # fitted params (the degeneracy-robust observable: insensitive to how
        # the width splits between laser and collisional cores)
        from rb5s6s.lineshape import model_profile
        nu = np.arange(-60, 60, 0.005)

        def _total_fwhm(gc, sl):
            prof = model_profile(nu, gamma_coll=max(gc, 0.0),
                                 sigma_laser_fwhm=max(sl, 1e-6), transit_fwhm=transit)
            # sub-grid FWHM by linear interpolation of the two half-max crossings
            # (revision #6: reading nu[prof>=half] quantizes FWHM to the grid step)
            h = 0.5 * prof.max()
            above = np.where(prof >= h)[0]
            lo, hi = above[0], above[-1]
            left = nu[lo] - (prof[lo] - h) / (prof[lo] - prof[lo - 1]) * (nu[lo] - nu[lo - 1]) \
                if lo > 0 else nu[lo]
            right = nu[hi] + (prof[hi] - h) / (prof[hi] - prof[hi + 1]) * (nu[hi + 1] - nu[hi]) \
                if hi < len(nu) - 1 else nu[hi]
            return float(right - left)

        gc, sl = fit["gamma_coll"], fit["sigma_laser"]
        s_gc, s_sl = fit["gamma_coll_err"], fit["sigma_laser_err"]
        total_fwhm = _total_fwhm(gc, sl)
        # Error on the TOTAL width: propagate the fit covariance through the
        # (numerical) total-FWHM map via a central-difference Jacobian. The
        # strong sigma_laser<->gamma_coll anticorrelation (corr ~ -0.85) makes
        # this MUCH smaller than the naive quadrature sum -- which is exactly
        # why the total width is the trustworthy, degeneracy-robust observable
        # (README 2.4) while the split is not. Transit is FIXED (w0 prior, an
        # OPEN systematic handled separately), so it adds no statistical term.
        h_gc = max(0.25 * s_gc, 0.01)
        h_sl = max(0.25 * s_sl, 0.01)
        d_gc = (_total_fwhm(gc + h_gc, sl) - _total_fwhm(gc - h_gc, sl)) / (2 * h_gc)
        d_sl = (_total_fwhm(gc, sl + h_sl) - _total_fwhm(gc, sl - h_sl)) / (2 * h_sl)
        rho = fit["corr_laser_coll"]
        rho = rho if np.isfinite(rho) else 0.0
        var = (d_gc * s_gc) ** 2 + (d_sl * s_sl) ** 2 + 2 * d_gc * d_sl * rho * s_gc * s_sl
        total_fwhm_err = float(np.sqrt(max(var, 0.0)))
        out.append({
            "role": role, "peak": peak, "T": T, "P": P, "rate_t": rate,
            "n": len(volts), "gamma_coll": fit["gamma_coll"],
            "gamma_coll_err": fit["gamma_coll_err"], "sigma_laser": fit["sigma_laser"],
            "sigma_laser_err": fit["sigma_laser_err"], "total_fwhm": total_fwhm,
            "total_fwhm_err": total_fwhm_err,
            "corr": fit["corr_laser_coll"], "chi2_red": fit["chi2_red"],
        })

    with open(C.RESULTS_DIR / "linefit_conditions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    # ---- total width vs T (degeneracy-robust) ----
    print(f"\n{'='*72}\nTOTAL line FWHM (transition axis, MHz) vs T  [degeneracy-robust]")
    print(f"{'peak':>6s} {'70C':>12s} {'90C':>12s} {'110C':>12s} {'130C(P225)':>12s}")
    def cell(peak, T):
        if T == "130":
            r = next((o for o in out if o["role"] == "p_sweep" and o["peak"] == peak
                      and o["P"] == "225"), None)
        else:
            r = next((o for o in out if o["role"] == "t_sweep" and o["peak"] == peak
                      and o["T"] == T), None)
        return f"{r['total_fwhm']:.2f}" if r else "-"
    for peak in ("4121", "4154", "4192", "4207"):
        print(f"{peak:>6s} " + " ".join(f"{cell(peak,T):>12s}" for T in ("70","90","110","130")))

    # ---- preliminary gamma_coll vs T ----
    print(f"\n{'-'*72}\nPRELIMINARY gamma_coll (MHz) vs T  [degeneracy corr ~ -0.9; NOT beta_self]")
    print(f"{'peak':>6s} {'70C':>14s} {'90C':>14s} {'110C':>14s}")
    for peak in ("4121", "4154", "4192", "4207"):
        cells = []
        for T in ("70", "90", "110"):
            r = next((o for o in out if o["role"] == "t_sweep" and o["peak"] == peak
                      and o["T"] == T), None)
            cells.append(f"{r['gamma_coll']:.2f}+/-{r['gamma_coll_err']:.2f}" if r else "-")
        print(f"{peak:>6s} " + " ".join(f"{c:>14s}" for c in cells))
    print(f"\nmedian laser<->coll corr = "
          f"{np.median([o['corr'] for o in out]):.2f}; "
          f"median chi2_red = {np.median([o['chi2_red'] for o in out]):.2f}")
    print("ALL PRELIMINARY: transit fixed on the OPEN w0 prior; beta_self + "
          "confound program + N(T) are module M4.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
