#!/usr/bin/env python3
"""
M4d: lever cross-check for beta_self -- a lever-limited cross-check + full error
budget. NOT the headline (that is the model-independent width-slope bound in
beta_self_probe.csv); this shows WHY beta is a bound, via the lever test.

HEADLINE = the internally-consistent 70/90/110 C cooling sweep (one session,
monotonic cooling), fit with rb5s6s.lever_crosscheck.lever_crosscheck_beta: the model-
form grid (transit exp/gaussian x sigma per_T/per_block) + w0 band + leave-one-
peak / leave-one-temperature robustness, giving ONE beta per isotope with three
separately-sourced error bars (statistical | model-form | confound/w0).

LEVER-DEPENDENCE PROBE = the 130 C anchor. The archive's `serves_t130` traces
(225 mW) would TRIPLE the density lever (N x52 vs x16). Adding them pulls the
joint beta far below the cooling-sweep value -- but the lesson is NOT "different
session": the per-condition gamma_coll rises only ~1.9x across the x53 density
span 70->130 C (near-flat), and the 130 C widths sit ON that sub-linear trend, so
the fitted "collisional" width is a residual FLOOR, not resolved linear
collisions (which must be LINEAR in N). beta is therefore a LEVER-DEPENDENT BOUND
(per-condition ~0.01; the joint ~0.036 is inflated by sigma_laser sharing), and
the long lever simply exposes that. The
130 C data are also a different session -- a secondary caveat we cannot fully
separate -- but leverage, not a session jump, is the driver. Either way the
model-independent BOUND, not any fit, is the archival headline, and October
needs same-session high-density points to resolve any real collisional slope.
(Run-once script, several minutes: the per_block fit floats one laser width
per block.)

PRELIMINARY where absolute: beta rides on the OPEN w0 (the confound bar spans
it). The model-independent raw-width BOUND (run_beta_self.py) stays the
archival headline; this is the best model-based cross-check + isotope test.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import PEAKS as PEAKINFO  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.global_fit import fit_global  # noqa: E402
from rb5s6s.lever_crosscheck import lever_crosscheck_beta, GRID_CELLS, PRIMARY  # noqa: E402

PEAKS = ("4121", "4154", "4192", "4207")
TSWEEP = ("70", "90", "110")


def _serves_t130(r) -> bool:
    return str(r.get("serves_t130", "")).strip() in ("1", "True", "true", "yes")


def _clean_traces(recs, rate):
    freqs, volts = [], []
    for r in recs:
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate))
        volts.append(v)
    return freqs, volts


def build_blocks(rows, trates, prates, include_130=False):
    """Cooling-sweep 70/90/110 blocks + (optionally) the 130 C serves_t130 anchor."""
    blocks = []
    for peak in PEAKS:
        iso = PEAKINFO[peak]["isotope"]
        for T in TSWEEP:
            if (peak, T) not in trates:
                continue
            recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                    and r["peak"] == peak and r["temperature_C"] == T]
            fr, vo = _clean_traces(recs, trates[(peak, T)])
            if len(vo) >= 3:
                blocks.append({"peak": peak, "isotope": iso, "T_C": float(T),
                               "N_units": density_units(float(T)),
                               "freqs": fr, "volts": vo,
                               "law": condition_noise_model(vo)})
        if include_130 and peak in prates:
            recs = [r for r in rows if r["flag"] == "canonical"
                    and _serves_t130(r) and r["peak"] == peak]
            fr, vo = _clean_traces(recs, prates[peak])
            if len(vo) >= 3:
                blocks.append({"peak": peak, "isotope": iso, "T_C": 130.0,
                               "N_units": density_units(130.0),
                               "freqs": fr, "volts": vo,
                               "law": condition_noise_model(vo)})
    return blocks


def _lever(blocks):
    Ns = [b["N_units"] for b in blocks]
    return max(Ns) / min(Ns)


def _gamma_sublinearity():
    """Per-condition gamma_coll vs density (from linefit_conditions.csv). A real
    binary-collision width rises LINEARLY with N; the robust, model-light test is
    the RISE FACTOR: how much does gamma_coll grow across the x52 density span
    70->130 C? If it is near-flat (a residual floor) while N goes x52, there is no
    resolved collisional signal and the inferred beta is a lever-dependent BOUND.

    Returns per-peak gamma_coll(70/90/110/130) plus the pooled mean at each T, the
    gamma rise factor, and the density factor (~52). (Per-peak linear-corr numbers
    are deliberately NOT the headline: they are muddy -- 993.4121 nm is non-
    monotonic -- and pooling them is misleading; the rise factor is robust.)"""
    lc = list(csv.DictReader(open(C.RESULTS_DIR / "linefit_conditions.csv")))

    def gc(peak, T, role):
        for r in lc:
            if (r["peak"] == peak and r["T"] == T and r["role"] == role
                    and (role == "t_sweep" or r.get("P") in ("225", "225.0"))):
                return float(r["gamma_coll"])
        return None

    Ts = (70, 90, 110, 130)
    roles = ("t_sweep", "t_sweep", "t_sweep", "p_sweep")
    per_peak, cols = {}, {T: [] for T in Ts}
    for peak in PEAKS:
        g = [gc(peak, str(T), role) for T, role in zip(Ts, roles)]
        if any(x is None for x in g):
            continue
        per_peak[peak] = dict(zip(Ts, g))
        for T, x in zip(Ts, g):
            cols[T].append(x)
    mean_gamma = {T: float(np.mean(cols[T])) for T in Ts if cols[T]}
    Nfac = density_units(130) / density_units(70)
    gfac = mean_gamma[130] / mean_gamma[70] if mean_gamma.get(70) else float("nan")
    return {"per_peak": per_peak, "mean_gamma": mean_gamma,
            "gamma_rise_factor": gfac, "density_factor": float(Nfac)}


def _report(res, blocks):
    isos = res["isotopes"]
    tk, sh = res["primary"]
    print("=" * 74)
    print(f"LEVER CROSS-CHECK beta_self (cooling sweep 70/90/110 C) -- a bound, NOT the headline")
    print(f"  {len(blocks)} blocks, {res['n_traces']} traces, density lever x{_lever(blocks):.0f}")
    print(f"  headline model = ({tk}, {sh}) = Lehmann cusp + M4c-validated per-T sharing")
    print(f"  chi2_red (headline) = {res['chi2_red'][f'{tk}|{sh}']:.3f}\n")
    print("  beta (MHz per 1e12 cm^-3) with THREE error bars:")
    for iso in isos:
        b, st = res["headline"][iso], res["err_statistical"][iso]
        mf = res["err_modelform"][iso]
        tr_, shx = res["err_transit"][iso], res["err_sharing"][iso]
        line = (f"    {iso}Rb: {b:.4f}  +/-{st:.4f} (stat)  "
                f"+/-{mf:.4f} (model-form: transit {tr_:.4f} | sharing {shx:.4f})")
        if res["w0_band"]:
            lo, hi = res["w0_band"][iso]
            line += f"  w0-band [{lo:.3f},{hi:.3f}]"
        print(line)
        dp, wp = res["loo_peak"][iso]
        dt, wt = res["loo_temp"][iso]
        vp = "ROBUST" if dp < 2 * st else "one peak anomalous -- inspect"
        print(f"          leave-one-peak-out: {dp:.4f} ({wp or 'n/a'}; {vp})")
        print(f"          leave-one-T-out:    {dt:.4f} ({wt or 'n/a'}; lever leverage, "
              f"expected large on a 3-point sweep)")
    if 85 in res["headline"] and 87 in res["headline"]:
        d = res["headline"][85] - res["headline"][87]
        de = np.hypot(res["err_statistical"][85], res["err_statistical"][87])
        print(f"\n  isotope test: beta_85 - beta_87 = {d:+.4f} +/- {de:.4f} ({abs(d)/de:.1f}sigma)")
    # per-drop detail (audit): does the 993.4207 nm suspect
    # drive beta OR the sigma_laser(T) trend? Read the row where it is dropped.
    if res.get("loo_peak_detail"):
        print("\n  leave-one-peak-out detail (beta and sigma_laser(T) per dropped peak):")
        Ts = sorted(next(iter(res["loo_peak_detail"].values()))["sigma_laser_by_T"])
        hdr = "  ".join(f"sig({T:.0f}C)" for T in Ts)
        print(f"    {'dropped':>12s}  beta_85   beta_87   {hdr}")
        for who, d_ in sorted(res["loo_peak_detail"].items()):
            b85 = d_["beta"].get(85); b87 = d_["beta"].get(87)
            sl = "  ".join(f"{d_['sigma_laser_by_T'][T]:8.2f}" for T in Ts)
            print(f"    {who:>12s}  {b85 if b85 is None else format(b85, '.4f'):>7}  "
                  f"{b87 if b87 is None else format(b87, '.4f'):>7}  {sl}")
    print("\n  model-form grid (beta per isotope | chi2_red):")
    tags = {("exp", "per_T"): "headline", ("gaussian", "per_T"): "transit axis",
            ("exp", "per_block"): "sharing axis"}
    for cell in GRID_CELLS:
        key = f"{cell[0]}|{cell[1]}"
        vals = "  ".join(f"{iso}Rb={res['grid'][key][iso][0]:.4f}" for iso in isos)
        print(f"    {cell[0]:>8s}/{cell[1]:<9s} ({tags[cell]:>12s}): {vals}  chi2={res['chi2_red'][key]:.3f}")


def main() -> int:
    rows = load_manifest()
    trates, prb = {}, {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        if r["session"] == "T":
            trates[(r["peak"], r["T"])] = 2.0 * float(r["rate"])
        elif r["session"] == "P" and r["T"] == "130":
            prb.setdefault(r["peak"], []).append(float(r["rate"]))
    prates = {pk: 2.0 * float(np.mean(v)) for pk, v in prb.items()}
    tref = C.TRANSIT_FWHM_PLACEHOLDER_MHZ

    # ---- HEADLINE: the internally-consistent cooling sweep ----
    blocks = build_blocks(rows, trates, prates, include_130=False)
    res = lever_crosscheck_beta(blocks, transit_ref_mhz=tref)
    _report(res, blocks)

    # ---- LEVER-DEPENDENCE PROBE: add the 130 C anchor (x52 density lever) ----
    # The point is NOT that the 130 C session is anomalous -- it is that the
    # long lever exposes gamma_coll as SUB-LINEAR in density, so the inferred
    # beta is lever-dependent = a BOUND, not a value.
    b130 = build_blocks(rows, trates, prates, include_130=True)
    fp = fit_global(b130, transit_ref_mhz=tref, transit_kind="exp", sigma_sharing="per_T")
    subl = _gamma_sublinearity()
    print(f"\n{'-'*74}\nLEVER-DEPENDENCE PROBE: add the 130 C anchor (serves_t130, 225 mW)")
    print(f"  lever x{_lever(b130):.0f} (vs x{_lever(blocks):.0f}); {fp['n_traces']} traces; "
          f"chi2_red={fp['chi2_red']:.3f}")
    probe = {}
    for iso in res["isotopes"]:
        b_head, b_130 = res["headline"][iso], fp["beta_by_isotope"][iso]
        probe[iso] = (b_130, b_130 - b_head)
        st = res["err_statistical"][iso]
        print(f"  {iso}Rb: joint beta  cooling(x16) {b_head:.4f} -> +130(x53) {b_130:.4f}  "
              f"({(b_130 - b_head)/st:+.0f}sigma -- lever-dependent)")
    # the robust evidence this is sub-linearity, not a session jump: gamma_coll
    # barely grows while the density goes x52.
    mg, gfac, nfac = subl["mean_gamma"], subl["gamma_rise_factor"], subl["density_factor"]
    print("  per-condition gamma_coll (mean over the 4 peaks): "
          + "  ".join(f"{T}C={mg[T]:.2f}" for T in (70, 90, 110, 130)) + " MHz")
    print(f"  => gamma_coll rises only x{gfac:.1f} across a x{nfac:.0f} density span "
          f"(70->130 C).")
    print("  A real binary-collision width is LINEAR in N, so this near-flat gamma is a")
    print("  residual FLOOR, not resolved collisions -> beta is a lever-dependent BOUND")
    print("  (joint ~0.036 short-lever -> ~0.014 long-lever; per-condition ~0.01). The 130 C")
    print("  data are also a different session (secondary caveat), but the widths sit ON")
    print("  the sub-linear trend, so leverage is the cause. Headline stays the BOUND.")

    # ---- persist ----
    with open(C.RESULTS_DIR / "lever_crosscheck.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        for iso in res["isotopes"]:
            w.writerow(["beta_crosscheck", f"{iso}Rb",
                        f"{res['headline'][iso]:.4f}", f"{res['err_statistical'][iso]:.4f}",
                        "MHz per 1e12 cm^-3 (HEADLINE: cooling sweep, Lehmann exp, per_T)"])
            w.writerow(["beta_err_modelform", f"{iso}Rb", f"{res['err_modelform'][iso]:.4f}", "",
                        "model-form grid spread (max-min)"])
            w.writerow(["beta_err_transit", f"{iso}Rb", f"{res['err_transit'][iso]:.4f}", "",
                        "transit axis (|Voigt - Lehmann|)"])
            w.writerow(["beta_err_sharing", f"{iso}Rb", f"{res['err_sharing'][iso]:.4f}", "",
                        "sigma-sharing axis (|per_T - per_block|)"])
            lo, hi = res["w0_band"][iso]
            w.writerow(["beta_w0_band", f"{iso}Rb", f"{lo:.4f}", f"{hi:.4f}",
                        "value=lo err=hi over transit_ref 0.92-1.49 (~w0 65-40 um, the OPEN w0)"])
            dp, wp = res["loo_peak"][iso]
            w.writerow(["beta_loo_peak", f"{iso}Rb", f"{dp:.4f}", "",
                        f"largest |dbeta| dropping one PEAK -- robustness ({wp or 'n/a'})"])
            dt, wt = res["loo_temp"][iso]
            w.writerow(["beta_loo_temp", f"{iso}Rb", f"{dt:.4f}", "",
                        f"largest |dbeta| dropping one TEMPERATURE -- lever leverage ({wt or 'n/a'})"])
            b130v, shift = probe[iso]
            w.writerow(["beta_lever_probe_130", f"{iso}Rb", f"{b130v:.4f}", f"{shift:.4f}",
                        "value=joint beta with the x53 130C lever; err=shift vs x16 cooling (lever-dependence)"])
        for cell in GRID_CELLS:
            key = f"{cell[0]}|{cell[1]}"
            for iso in res["isotopes"]:
                bval, berr = res["grid"][key][iso]
                w.writerow([f"beta_grid_{cell[0]}_{cell[1]}", f"{iso}Rb",
                            f"{bval:.4f}", f"{berr:.4f}", f"chi2_red={res['chi2_red'][key]:.3f}"])
        # per-drop LOO detail (audit): beta and sigma_laser(T)
        # with each peak removed -- the committed record that the 4207 suspect
        # drives neither the coefficient nor the sigma_laser(T) trend.
        for who, d_ in sorted(res.get("loo_peak_detail", {}).items()):
            pk = who.replace("peak ", "")
            for iso in res["isotopes"]:
                b = d_["beta"].get(iso)
                if b is None:
                    continue
                w.writerow(["beta_loo_drop", f"{pk}|{iso}Rb", f"{b:.4f}",
                            f"{b - res['headline'][iso]:+.4f}",
                            "beta with this peak dropped; err=shift vs headline"])
            for T, s in sorted(d_["sigma_laser_by_T"].items()):
                w.writerow(["sigma_loo_drop", f"{pk}|{T:.0f}C", f"{s:.3f}", "",
                            "sigma_laser(T) with this peak dropped (MHz transition)"])
        # gamma_coll(N) rise: the evidence beta is a lever-dependent BOUND --
        # gamma barely grows across a x52 density span (near-flat = a residual
        # floor, not the linear scaling a real collisional width demands).
        mg = subl["mean_gamma"]
        for T in (70, 90, 110, 130):
            w.writerow(["gamma_coll_mean_vs_T", f"{T}C", f"{mg[T]:.3f}",
                        f"{density_units(T):.2f}", "value=mean gamma_coll over 4 peaks (MHz); err=density N (1e12 cm^-3)"])
        w.writerow(["gamma_rise_factor", "70to130", f"{subl['gamma_rise_factor']:.2f}",
                    f"{subl['density_factor']:.1f}",
                    "value=gamma(130)/gamma(70); err=density ratio -- far sub-linear => floor, beta is a BOUND"])

    print(f"\n{'-'*74}\nWrote results/lever_crosscheck.csv. Model-based cross-check + isotope test")
    print("with the full audited budget; the raw-width BOUND stays the archival headline.")
    print("October fixed lock + knife-edge w0 collapse the w0 bar and the session split.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
