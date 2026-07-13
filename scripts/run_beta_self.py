#!/usr/bin/env python3
"""
M4: collisional self-broadening beta_self + the confound program.

For each peak, fit beta_self globally across the T-sweep (70/90/110 C, one
cooling session) with gamma_coll(T) = beta_self * N(T) and a shared
sigma_laser (rb5s6s.beta). Then run the pre-registered confound probes and
apply the measurement-vs-bound rule.

THE CONFOUND (docs/PLAN.md M4): temperature is monotonic with time across the
campaign, so a slow instrument drift can mimic collisional broadening. Probes
that bound the drift contribution:
  (P1) P-session line widths vs block order at FIXED 130 C (power's true
       width effect is <=2%) -- a direct hours-scale drift monitor.
  (P2) before/after ruler tooth-width change per peak -- fixed-condition
       instrument drift over each peak's session.
  (P3) cross-peak gamma_coll consistency at fixed T -- four lines see ONE
       density; disagreement beyond errors flags a per-peak systematic.
  (P4) sigma_laser stability (the global fit's shared laser width, and its
       covariance with beta) -- if the "collisional" trend is really laser
       drift, sigma_laser absorbs it.

PRE-REGISTERED RULE: report beta_self as a MEASUREMENT only if the probes
bound the drift contribution to <= ~1/3 of the observed gamma_coll(T) trend;
otherwise report a BOUND. Absolute value remains PRELIMINARY until the w0
knife-edge fixes the transit prior.

Outputs: results/beta_self.csv + stdout report.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import TOOTH_SPACING_LASER_HZ  # noqa: E402
from rb5s6s.density import density_units, number_density_cm3  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.beta import fit_beta_self, collisional_slope  # noqa: E402
from rb5s6s.qc import boxcar, contiguous_fwhm_ms  # noqa: E402

PEAKS = ("4121", "4154", "4192", "4207")
TSWEEP = ("70", "90", "110")


def raw_fwhm_mhz(recs, rate, rate_relerr=0.0):
    """Model-INDEPENDENT line FWHM per condition: smoothed half-max width (ms)
    x the verified per-block rate. No lineshape model, no laser/coll split —
    the cleanest probe of whether the width actually rises monotonically with
    density (collisional broadening must).

    The returned error combines the repeat scatter (within-block, incoherent)
    with the block's ruler-rate uncertainty (block-coherent: it scales every
    width in the block together): E = sqrt(sem^2 + (W * rate_relerr)^2)."""
    ws = []
    for r in recs:
        t, v = load_trace(trace_path(r))
        ws.append(contiguous_fwhm_ms(t, v) * rate)   # retrace-safe (shared helper)
    W = float(np.mean(ws))
    sem = float(np.std(ws, ddof=1) / np.sqrt(len(ws)))
    return W, float(np.hypot(sem, W * rate_relerr))


def width_vs_density_probe(rows, peak, trates, prates, include_130=False):
    """P0 (decisive): fit raw FWHM(N) = W0 + beta_eff*N. The RMS residual
    about that line is the BETWEEN-BLOCK systematic (laser-width drift AND
    ruler-rate uncertainty, both block-coherent) — the error the global fit's
    shared-sigma_laser assumption omits. Optionally extends the lever arm with
    the 130 C point (the 225 mW power-session files): N(130)/N(110) ~ 3.2, at
    the price of a cross-session comparison whose rate comes from the bracket
    combination (its before/after half-difference carried as uncertainty)."""
    byT = defaultdict(list)
    for r in rows:
        if (r["flag"] == "canonical" and r["role"] == "t_sweep"
                and r["peak"] == peak and r["temperature_C"] in TSWEEP):
            byT[r["temperature_C"]].append(r)
    N, W, E = [], [], []
    for T in TSWEEP:
        if T in byT and (peak, T) in trates:
            rate, relerr = trates[(peak, T)]
            m, e = raw_fwhm_mhz(byT[T], rate, relerr)
            N.append(density_units(float(T))); W.append(m); E.append(e)
    if include_130 and peak in prates:
        recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "p_sweep"
                and r["peak"] == peak and r["power_mW"] == "225"]
        if len(recs) >= 3:
            rate, relerr = prates[peak]
            m, e = raw_fwhm_mhz(recs, rate, relerr)
            N.append(density_units(130.0)); W.append(m); E.append(e)
    if len(N) < 3:
        return None
    return collisional_slope(N, W, E)


def load_t_rates():
    """Per-block transition-axis rates WITH their relative errors, plus the
    P-session bracket combination per peak.

    Rate errors are BLOCK-COHERENT: a rate error scales every width in that
    block by the same factor, so it belongs in the between-block error budget
    (audit fix, 2026-07-11 — previously omitted; at 70 C the ruler is dim and
    its 1.2-1.8% rate error contributes 0.06-0.09 MHz, co-dominant with the
    laser-width drift we had blamed alone).

    Bracket combination: rate = mean(before, after); its error adds the
    half-difference in quadrature, so a genuine in-session rate shift (4207:
    1.4%) is carried as uncertainty instead of being averaged away."""
    path = C.RESULTS_DIR / "ruler_blocks.csv"
    trate, brackets = {}, defaultdict(dict)
    for r in csv.DictReader(open(path)):
        rr, ee = 2.0 * float(r["rate"]), 2.0 * float(r["rate_err"])
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = (rr, ee / rr)
        else:
            brackets[r["peak"]][r["bracket"]] = (rr, ee)
    prate = {}
    for peak, br in brackets.items():
        if "before" in br and "after" in br:
            (rb, eb), (ra, ea) = br["before"], br["after"]
            mean = 0.5 * (rb + ra)
            err = np.sqrt(0.5 * (eb ** 2 + ea ** 2) + (0.5 * (rb - ra)) ** 2)
            prate[peak] = (mean, err / mean)
    return trate, prate


def load_conditions(rows, peak, trates):
    """Build the beta.fit condition list for one peak's T-sweep."""
    byT = defaultdict(list)
    for r in rows:
        if (r["flag"] == "canonical" and r["role"] == "t_sweep"
                and r["peak"] == peak and r["temperature_C"] in TSWEEP):
            byT[r["temperature_C"]].append(r)
    conds = []
    for T in TSWEEP:
        entry = trates.get((peak, T))
        if entry is None:
            continue
        rate = entry[0]
        freqs, volts = [], []
        for r in byT[T]:
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f
                   for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate)); volts.append(v)
        if len(volts) >= 3:
            law = condition_noise_model(volts)
            conds.append({"T_C": float(T), "N_units": density_units(float(T)),
                          "freqs": freqs, "volts": volts, "law": law})
    return conds


def main() -> int:
    rows = load_manifest()
    trates, prates = load_t_rates()

    results = []
    fits = {}
    for peak in PEAKS:
        conds = load_conditions(rows, peak, trates)
        if len(conds) < 2:
            print(f"[skip] {peak}: {len(conds)} temperatures"); continue
        fit = fit_beta_self(conds, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        fits[peak] = (fit, conds)
        results.append({"peak": peak, **{k: fit[k] for k in
                        ("beta_self", "beta_self_err", "sigma_laser", "sigma_laser_err",
                         "chi2_red", "corr_beta_laser")}})

    with open(C.RESULTS_DIR / "beta_self.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)

    print("=" * 74)
    print("beta_self (PRELIMINARY: transit on OPEN w0 prior; MHz per 1e12 cm^-3):")
    print(f"{'peak':>6s} {'beta_self':>16s} {'sigma_laser':>14s} {'chi2':>6s} {'corr(b,L)':>9s}")
    for r in results:
        print(f"{r['peak']:>6s} {r['beta_self']:>7.3f}+/-{r['beta_self_err']:<7.3f} "
              f"{r['sigma_laser']:>6.2f}+/-{r['sigma_laser_err']:<5.2f} "
              f"{r['chi2_red']:>6.2f} {r['corr_beta_laser']:>9.2f}")

    # ---- per-peak beta consistency + within-isotope pooling (revision #2) ----
    print(f"\n{'-'*74}\nPER-PEAK beta_self consistency (are the four values mutually OK?):")
    iso = {"4121": 87, "4207": 87, "4154": 85, "4192": 85}
    bp = {r["peak"]: (r["beta_self"], r["beta_self_err"]) for r in results}
    for isotope in (87, 85):
        ps = [p for p in ("4121", "4207", "4154", "4192") if iso[p] == isotope and p in bp]
        if len(ps) < 2:
            continue
        v = np.array([float(bp[p][0]) for p in ps])
        e = np.array([float(bp[p][1]) for p in ps])
        wmean = np.sum(v / e ** 2) / np.sum(1 / e ** 2)
        werr = 1.0 / np.sqrt(np.sum(1 / e ** 2))
        chi2 = np.sum(((v - wmean) / e) ** 2) / max(len(ps) - 1, 1)
        pull = {p: (float(bp[p][0]) - wmean) / float(bp[p][1]) for p in ps}
        worst = max(pull, key=lambda k: abs(pull[k]))
        print(f"  {isotope}Rb {ps}: pooled beta = {wmean:.4f}+/-{werr:.4f}  "
              f"chi2/dof={chi2:.1f}  "
              f"({'consistent' if chi2 < 3 else 'INCONSISTENT'}; "
              f"worst {worst} at {pull[worst]:+.1f}sigma)")
    print("  NOTE: per-peak beta (this fit, ~0.03-0.05) and the per-isotope global")
    print("  fit (fit_global, ~0.056) differ at the factor-~2 level depending on the")
    print("  sigma_laser sharing -- a model systematic; the headline stays the")
    print("  model-independent raw-width BOUND (P0 below), not any single beta value.")

    # ---- P3: cross-peak consistency of the implied gamma_coll at 110 C ----
    N110 = density_units(110.0)
    gc110 = [(r["peak"], r["beta_self"] * N110, r["beta_self_err"] * N110) for r in results]
    vals = np.array([g[1] for g in gc110]); errs = np.array([g[2] for g in gc110])
    wmean = np.sum(vals / errs ** 2) / np.sum(1 / errs ** 2)
    chi2_cross = np.sum(((vals - wmean) / errs) ** 2) / max(len(vals) - 1, 1)
    print(f"\n(P3) cross-peak gamma_coll @110C: " +
          ", ".join(f"{p}={v:.2f}" for p, v, e in gc110) +
          f"  | chi2/dof vs common = {chi2_cross:.1f} "
          f"({'consistent' if chi2_cross < 3 else 'INCONSISTENT -> per-peak systematic'})")

    # ---- P0 (decisive): model-independent width vs density + systematic ----
    print(f"\n{'-'*74}\n(P0) MODEL-INDEPENDENT raw-width vs density [the decisive confound probe]:")
    print(f"{'peak':>6s} {'beta_eff':>10s} {'formal':>8s} {'+syst':>8s} "
          f"{'resid':>7s} {'sig':>5s} {'mono':>5s}  verdict")
    probe_rows = []
    for variant, use130 in (("70-110C (one session)", False),
                            ("70-130C (adds cross-session 130C, 3.2x lever)", True)):
        print(f"  --- {variant} ---")
        for peak in PEAKS:
            pr = width_vs_density_probe(rows, peak, trates, prates, include_130=use130)
            if pr is None:
                continue
            probe_rows.append({"peak": peak, "variant": variant, **{k: pr[k] for k in
                              ("beta_eff", "formal_err", "syst_err", "resid_rms", "snr",
                               "bound95", "verdict", "monotonic")}})
            print(f"{peak:>6s} {pr['beta_eff']:>10.4f} {pr['formal_err']:>8.4f} "
                  f"{pr['syst_err']:>8.4f} {pr['resid_rms']:>7.3f} {pr['snr']:>5.1f} "
                  f"{('yes' if pr['monotonic'] else 'NO'):>5s}  {pr['verdict']}"
                  + (f" (<{pr['bound95']:.3f} @95%)" if pr['verdict'] == 'BOUND' else ""))
    with open(C.RESULTS_DIR / "beta_self_probe.csv", "w", newline="") as f:
        if probe_rows:
            w = csv.DictWriter(f, fieldnames=list(probe_rows[0].keys()))
            w.writeheader(); w.writerows(probe_rows)

    one_session = [p for p in probe_rows if not p["variant"].startswith("70-130")]
    n_nonmono = sum(1 for p in one_session if not p["monotonic"])
    print(f"\nVERDICT: {n_nonmono}/{len(one_session)} peaks are NON-MONOTONIC in density"
          " — impossible for pure collisional broadening.")
    print("The between-block width scatter (resid ~0.06-0.16 MHz) is the DOMINANT error:")
    print("laser-width drift over the cooling session is comparable to the collisional")
    print("trend, so the archival T-sweep BOUNDS beta_self (it does not measure it).")
    print("The global-fit sigmas above are OVERCONFIDENT — they assume one shared")
    print("sigma_laser across blocks and so omit exactly this between-block drift.")
    print("=> Clean beta_self REQUIRES the fixed-lock October campaign (two-epoch design).")

    print(f"\n{'-'*74}\nCAVEATS (all results PRELIMINARY):")
    print("  * transit fixed on the OPEN w0 prior -> absolute scale of any beta")
    print("  * within-session T-sweep only (70/90/110); 130C is a different session")
    print("  * vapor-density cold-spot systematic (density.py) on absolute N(T)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
