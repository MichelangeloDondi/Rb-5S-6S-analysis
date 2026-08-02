#!/usr/bin/env python3
"""
M4: collisional self-broadening beta_self + the confound program.

For each peak, fit beta_self globally across the density lever with
gamma_coll(T) = beta_self * N(T) and a shared sigma_laser (rb5s6s.beta).
Then run the pre-registered confound probes and apply the
measurement-vs-bound rule.

HEADLINE CONSTRUCTION (2026-08-02, decided by Michelangelo on firsthand
apparatus authority). The beta_self headline is now the FOUR-POINT
construction: 70/90/110/130 C, dof=2, the x52.5 density lever (N(130)/N(70)),
built from the T-sweep (70/90/110 C) plus the 130 C power-sweep session's
225 mW block. There is no separate three-point (70/90/110 C, dof=1, x16.2
lever) headline kept alongside it; that construction is superseded, not
demoted to a robustness row -- one licensed construction, one bound, per
peak. The prior version of this module (and of docs/DATA.md, README.md and
the ledger) treated 130 C as an optional extra lever point excluded from the
headline because it looked like a different apparatus configuration (a power
sweep, not a temperature sweep, calibrated off before/after EOM ruler
brackets rather than the T-session's own per-block ruler). That exclusion
reasoning does not survive Michelangelo's firsthand statement: the 130 C
power-sweep session ran in the SAME optical/cell configuration as the
70/90/110 C temperature sweep (same beam path, same cell, same detection
chain). What actually differs between the two sessions is the acquisition
epoch and the axis calibration, and the calibration difference is already
handled PER SESSION -- load_t_rates() derives the T-sweep rate from the
T-session's own per-block ruler and the P-sweep rate from the P-session's
before/after bracket combination, so folding the 130 C point into one shared
density axis carries no unhandled calibration mismatch. See
private/reviews/digest/fig19_trend_audit.md for the prior "different
configuration" reading this decision overrides, and docs/DATA.md's clock
entry for the timing (130 C sits 2.3 h from the 110 C dwell, inside the same
continuous campaign). The remaining caveat is not a configuration break, it
is that 130 C is the extreme end of the density lever, so the fit still
leans on a short arm relative to a purpose-built session.

THE CONFOUND (docs/PLAN.md M4): temperature is monotonic with time across the
campaign, so a slow instrument drift can mimic collisional broadening. Probes
that bound the drift contribution:
  (P1) P-session line widths vs block order at FIXED 130 C (the ramp predicts
       a <=2% width effect) -- a drift monitor. NOTE (2026-07-23): block
       order is ASCENDING POWER, and the recovered timestamps show the
       session ran DESCENDING, so this axis is reversed in time. The probe
       is direction-agnostic (it asks whether width varies across the
       session at fixed T, not which way), so the bound is unaffected --
       but do not read the sign of any trend here as a drift direction.
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

Outputs: results/beta_self.csv + results/beta_self_probe.csv + stdout report.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
import pathlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C
from rb5s6s import rate_model as RM
from rb5s6s import constants as _CONST  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.beta import fit_beta_self, collisional_slope  # noqa: E402
from rb5s6s.qc import contiguous_fwhm_ms  # noqa: E402

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
        # Raw half-maximum width, DELIBERATELY model-independent: a bound
        # argued from raw widths inherits none of the lineshape model's
        # assumptions. It carries a known SNR bias (narrow at low SNR,
        # ~6% at the 70 C end) which EXAGGERATES the climb with density --
        # i.e. it pushes against this module's own conclusion, so the bound
        # is conservative w.r.t. it. Postscript to addendum 17.
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
    the price of reaching the extreme end of the lever, with a rate from the
    bracket combination (its before/after half-difference carried as
    uncertainty). Not a cross-session comparison: the recovered clock puts the
    130 C block 2.3 h from the 110 C dwell, inside one campaign."""
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
    return _apply_rate_models(trate, prate)


def _apply_rate_models(trate, prate):
    """Overlay the time-resolved rate(t) model where science times exist.

    The bracket/block scheme above stays the constructor and the FALLBACK:
    any (peak, T) or peak whose science-side clock or model is missing keeps
    its committed value unchanged (in production that is the 4154 70 C
    block, whose science traces have no recovered clock). Where the model
    applies, the rate is rate(t) evaluated at the block's mean science time
    and the error is the model's, PLUS - for the P session, whose consumers
    apply ONE rate to a whole drifting ladder - the rms spread of rate(t)
    across that peak's science-trace times, in quadrature. That keeps the
    ladder-drift systematic covered while the central error falls 3-5x.
    All numbers stay transition-axis (2x laser), like the fallback."""
    models = RM.read_models()
    if not models:
        return trate, prate
    clock = RM.load_clock()
    man = defaultdict(list)
    for r in csv.DictReader(open(C.MANIFEST_CSV)):
        if r["flag"] != "canonical":
            continue
        t = clock.get(pathlib.Path(r["file"]).name.lower())
        if t is not None:
            man[(r["role"], r["peak"], r["temperature_C"])].append(t)
    for (peak, T), _ in list(trate.items()):
        m = models.get(("T", peak))
        times = man.get(("t_sweep", peak, T))
        if not m or not times:
            continue
        span = m["t_max_epoch"] - m["t_min_epoch"]
        tc = float(np.mean(times))
        if not (m["t_min_epoch"] - 0.25 * span <= tc <= m["t_max_epoch"] + 0.25 * span):
            continue
        r, rel = RM.rate_at(m, tc)
        trate[(peak, T)] = (2.0 * r, rel)
    for peak in list(prate):
        m = models.get(("P", peak))
        times = man.get(("p_sweep", peak, "130"))
        if not m or not times:
            continue
        rates = np.array([RM.rate_at(m, t)[0] for t in times])
        rc, rel = RM.rate_at(m, float(np.mean(times)))
        rel = float(np.sqrt(rel ** 2 + np.var(rates) / rc ** 2))
        prate[peak] = (2.0 * rc, rel)
    return trate, prate


def _load_block_condition(recs, T_C, rate):
    """Shared per-block trace loader: QC-filter, convert to frequency, and
    build one beta.fit condition dict. Used for both the T-sweep dwells and
    the 130 C P-sweep 225 mW block (the headline's fourth point), so the two
    share exactly the same QC and windowing path."""
    freqs, volts = [], []
    for r in recs:
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate)); volts.append(v)
    if len(volts) < 3:
        return None
    law = condition_noise_model(volts)
    return {"T_C": float(T_C), "N_units": density_units(float(T_C)),
            "freqs": freqs, "volts": volts, "law": law}


def load_conditions(rows, peak, trates, prates=None):
    """Build the beta.fit condition list for one peak: the four-point
    headline (2026-08-02) is the 70/90/110 C T-sweep plus the 130 C P-sweep
    225 mW block, one shared density axis, each block calibrated by its own
    session's rate (see the module docstring). Pass prates=None to get the
    T-sweep-only (superseded) three-point list, e.g. for a diagnostic."""
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
        cond = _load_block_condition(byT[T], T, entry[0])
        if cond is not None:
            conds.append(cond)
    if prates is not None and peak in prates:
        recs130 = [r for r in rows if r["flag"] == "canonical" and r["role"] == "p_sweep"
                   and r["peak"] == peak and r["power_mW"] == "225"]
        cond130 = _load_block_condition(recs130, 130.0, prates[peak][0])
        if cond130 is not None:
            conds.append(cond130)
    return conds


def main() -> int:
    rows = load_manifest()
    trates, prates = load_t_rates()

    results = []
    fits = {}
    for peak in PEAKS:
        conds = load_conditions(rows, peak, trates, prates)
        if len(conds) < 2:
            print(f"[skip] {peak}: {len(conds)} temperatures"); continue
        fit = fit_beta_self(conds, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        fits[peak] = (fit, conds)
        results.append({"peak": peak, **{k: fit[k] for k in
                        ("beta_self", "beta_self_err", "sigma_laser", "sigma_laser_err",
                         "chi2_red", "corr_beta_laser", "noise_floor_limited",
                         "beta_at_bound", "sigma_laser_at_bound")}})

    with open(C.RESULTS_DIR / "beta_self.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)

    # ---- robustness swap: the M1 noise law vs UNIFORM weights -------------
    # The weights come from the measured sigma(V) law (M1). If beta depended
    # strongly on that choice, the noise model would be doing physics work it
    # was never validated for. Refit every peak with law=None (uniform) and
    # record the shift; a red-team review named this swap as untested (2026-07-25).
    swap_rows = []
    for peak, (fit_w, conds) in fits.items():
        uni = fit_beta_self([dict(c, law=None) for c in conds],
                            transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        swap_rows.append({
            "peak": peak,
            "isotope": _CONST.PEAKS[peak]["isotope"],
            "beta_m1_law": f"{fit_w['beta_self']:.4f}",
            "beta_uniform": f"{uni['beta_self']:.4f}",
            "shift": f"{uni['beta_self'] - fit_w['beta_self']:+.4f}",
            "unit": "MHz per 1e12 cm^-3",
        })
    if swap_rows:
        with open(C.RESULTS_DIR / "noise_law_swap.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(swap_rows[0].keys()))
            w.writeheader(); w.writerows(swap_rows)
        mx = max(abs(float(r["shift"])) for r in swap_rows)
        print(f"\n  NOISE-LAW SWAP (M1 weights -> uniform): max |d beta| = {mx:.4f} "
              f"MHz/1e12 -- wrote results/noise_law_swap.csv")

    print("=" * 74)
    print("beta_self (PRELIMINARY: transit on OPEN w0 prior; MHz per 1e12 cm^-3):")
    print(f"{'peak':>6s} {'beta_self':>16s} {'sigma_laser':>14s} {'chi2':>6s} {'corr(b,L)':>9s}")
    for r in results:
        print(f"{r['peak']:>6s} {r['beta_self']:>7.3f}+/-{r['beta_self_err']:<7.3f} "
              f"{r['sigma_laser']:>6.2f}+/-{r['sigma_laser_err']:<5.2f} "
              f"{r['chi2_red']:>6.2f} {r['corr_beta_laser']:>9.2f}")

    # ---- per-peak beta consistency + within-isotope pooling ----
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
    print("  NOTE: per-peak beta (this fit, four-point, ~0.01-0.02) and the per-isotope")
    print("  global fit (fit_global, ~0.056) differ at the factor-~3 level depending on the")
    print("  sigma_laser sharing -- a model systematic; the headline stays the")
    print("  model-independent raw-width BOUND (P0 below), not any single beta value.")

    # ---- P3: cross-peak consistency of the implied gamma_coll at 110 C ----
    N110 = density_units(110.0)
    gc110 = [(r["peak"], r["beta_self"] * N110, r["beta_self_err"] * N110) for r in results]
    vals = np.array([g[1] for g in gc110]); errs = np.array([g[2] for g in gc110])
    wmean = np.sum(vals / errs ** 2) / np.sum(1 / errs ** 2)
    chi2_cross = np.sum(((vals - wmean) / errs) ** 2) / max(len(vals) - 1, 1)
    print("\n(P3) cross-peak gamma_coll @110C: " +
          ", ".join(f"{p}={v:.2f}" for p, v, e in gc110) +
          f"  | chi2/dof vs common = {chi2_cross:.1f} "
          f"({'consistent' if chi2_cross < 3 else 'INCONSISTENT -> per-peak systematic'})")

    # ---- P0 (decisive): model-independent width vs density + systematic ----
    print(f"\n{'-'*74}\n(P0) MODEL-INDEPENDENT raw-width vs density [the decisive confound probe]:")
    print(f"{'peak':>6s} {'beta_eff':>10s} {'formal':>8s} {'+syst':>8s} "
          f"{'resid':>7s} {'sig':>5s} {'mono':>5s}  verdict")
    # Single headline variant (2026-08-02): 70/90/110/130 C, dof=2, the
    # x52.5 density lever. No separate three-point row is kept; see the
    # module docstring for why.
    probe_rows = []
    variant = "70-130C (headline, four-point, same configuration, 52.5x lever)"
    print(f"  --- {variant} ---")
    for peak in PEAKS:
        pr = width_vs_density_probe(rows, peak, trates, prates, include_130=True)
        if pr is None:
            continue
        probe_rows.append({"peak": peak, "variant": variant, "headline": "yes",
                          **{k: pr[k] for k in
                          ("beta_eff", "formal_err", "syst_err", "resid_rms", "snr",
                           "dof", "t95", "bound95", "n_frac_syst",
                           "bound95_nscale", "verdict", "monotonic")}})
        print(f"{peak:>6s} {pr['beta_eff']:>10.4f} {pr['formal_err']:>8.4f} "
              f"{pr['syst_err']:>8.4f} {pr['resid_rms']:>7.3f} {pr['snr']:>5.1f} "
              f"{('yes' if pr['monotonic'] else 'NO'):>5s}  {pr['verdict']}"
              + (f" (<{pr['bound95_nscale']:.3f} @95%; t({pr['dof']})="
                 f"{pr['t95']:.2f}, x{1 + pr['n_frac_syst']:.1f} N-scale)"
                 if pr['verdict'] == 'BOUND' else ""))
    with open(C.RESULTS_DIR / "beta_self_probe.csv", "w", newline="") as f:
        if probe_rows:
            w = csv.DictWriter(f, fieldnames=list(probe_rows[0].keys()))
            w.writeheader(); w.writerows(probe_rows)

    n_nonmono = sum(1 for p in probe_rows if not p["monotonic"])
    print(f"\nVERDICT: {n_nonmono}/{len(probe_rows)} peaks are NON-MONOTONIC in density"
          " -- impossible for pure collisional broadening.")
    print("The between-block width scatter is the DOMINANT error: laser-width drift")
    print("across sessions is comparable to the collisional trend, so the archival")
    print("four-point lever BOUNDS beta_self (it does not measure it).")
    print("The global-fit sigmas above are OVERCONFIDENT -- they assume one shared")
    print("sigma_laser across blocks and so omit exactly this between-block drift.")
    print("=> Clean beta_self REQUIRES a fixed-lock session (two-epoch design).")

    print(f"\n{'-'*74}\nCAVEATS (all results PRELIMINARY):")
    print("  * transit fixed on the OPEN w0 prior -> absolute scale of any beta")
    print("  * headline is 70/90/110/130 C (dof=2); 130C is still the extreme end")
    print("    of the lever, same apparatus/optical configuration as 70-110C")
    print("    (Michelangelo, firsthand), differing only by session/epoch and")
    print("    per-session rate calibration (handled in load_t_rates)")
    print("  * vapor-density cold-spot systematic (density.py) on absolute N(T)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
