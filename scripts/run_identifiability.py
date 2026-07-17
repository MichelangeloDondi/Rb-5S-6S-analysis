#!/usr/bin/env python3
"""
M12: is the width decomposition identifiable? -- the LOCAL covariance and
condition number of (gamma_coll, sigma_laser, transit) on a representative
bright line, plus the GLOBAL profile-likelihood map in the
(gamma_coll, sigma_laser) plane (chi2 minimised over transit and every
per-trace nuisance at each grid point).

The three widths all broaden the same ~5 MHz line, so the analysis FIXES transit
(from the w0 prior) and reports sigma_laser as a bound. This driver quantifies
why, twice over: the covariance shows the archive constrains the TOTAL width
well but the SPLIT poorly; the profile map shows that local picture is the
whole picture -- a single valley, straight (no 'banana'), whose 95% region runs
to the physical rails rather than closing. Two maps: a WIDE one for the
topology (does the region close? where is the transit->0 wall?) and a ZOOM one
around the free-fit minimum for the quantitative test against the local
covariance ellipse (in the Gaussian limit the profile contours ARE the marginal
ellipse, so overlaying them is the trust test for every covariance-based
statement in the analysis). The bright condition is identifiability's BEST case
(highest SNR): if the split is degenerate here it is worse everywhere else, so
one condition is the conservative probe.

Writes results/identifiability.csv and results/identifiability_profile.csv
(the grids + dchi2, drawn by figures/fig7). Reads results/ruler_blocks.csv.
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
from rb5s6s.identifiability import (width_identifiability, width_profile_2d,  # noqa: E402
                                    valley_floor, WIDTHS)

# a bright, well-behaved condition gives the cleanest covariance: 993.4192 nm
# (85Rb F3, the strongest line) at 130 C / 225 mW.
PEAK, POWER = "4192", "225"

# WIDE map: the physically meaningful (gamma_coll, sigma_laser) range -- from
# no-collisions to ~2x the fitted collisional width, and laser widths from
# narrow to wider-than-the-line. Coarser model grid (nu_step) is fine for
# topology. ZOOM map: +/- ZOOM_NSD marginal sigmas around the free-fit minimum,
# fine grid, for the ellipse comparison and the banana metric.
WIDE_GC = (1e-3, 1.4, 21)
WIDE_SL = (0.2, 2.8, 21)
ZOOM_NSD, ZOOM_N = 6.0, 21


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
    # the (gamma_coll, sigma_laser, transit) chi2 surface carries TWO basins --
    # a Gaussian-dominated one (large sigma_laser, transit railed at 0) and a
    # cusp-dominated one (transit near the w0-prior value, narrow laser). A
    # single-start fit can land in either, so the local analysis is anchored at
    # the DEEPER one and the branch gap is reported as its own diagnostic (the
    # profile maps below are what established the second basin).
    r_gauss = width_identifiability(freqs, volts, law=law)
    r_cusp = width_identifiability(freqs, volts, law=law, seeds=(0.21, 0.60, 1.45))
    r = r_cusp if r_cusp["chi2"] <= r_gauss["chi2"] else r_gauss
    branch_gap = abs(r_gauss["chi2"] - r_cusp["chi2"])
    print(f"  two-start branches: Gaussian-dominated chi2={r_gauss['chi2']:.1f} "
          f"(gc={r_gauss['fit']['gamma_coll']:.2f}, sl={r_gauss['fit']['sigma_laser']:.2f}, "
          f"tr={r_gauss['fit']['transit']:.2f});")
    print(f"                      cusp-dominated     chi2={r_cusp['chi2']:.1f} "
          f"(gc={r_cusp['fit']['gamma_coll']:.2f}, sl={r_cusp['fit']['sigma_laser']:.2f}, "
          f"tr={r_cusp['fit']['transit']:.2f})")
    print(f"  anchoring the local analysis at the deeper "
          f"({'cusp' if r is r_cusp else 'Gaussian'}) branch; gap = {branch_gap:.1f}")

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

    # ---- GLOBAL: the profile-likelihood maps --------------------------------
    gc0, sl0 = r["fit"]["gamma_coll"], r["fit"]["sigma_laser"]
    sd_gc = r["sigma_by_width"]["gamma_coll"]; sd_sl = r["sigma_by_width"]["sigma_laser"]
    print(f"\n{'-'*74}\nPROFILE LIKELIHOOD in (gamma_coll, sigma_laser), transit + nuisances")
    print("  re-minimised at every grid point (the global complement of the local")
    print("  covariance above). WIDE map first (topology), then the ZOOM map")
    print("  (ellipse comparison). This is the slow step (~1 h).")

    wide = width_profile_2d(
        freqs, volts, law=law, transit_seed=r["fit"]["transit"], nu_step=0.02,
        gc_grid=np.linspace(*WIDE_GC), sl_grid=np.linspace(*WIDE_SL),
        audit_stride=5)
    print(f"\n  WIDE ({WIDE_GC[2]}x{WIDE_SL[2]}, gc {WIDE_GC[0]:.3f}-{WIDE_GC[1]:.1f}, "
          f"sl {WIDE_SL[0]:.1f}-{WIDE_SL[1]:.1f}; topology at this grid resolution):")
    print(f"    grid-min at gamma_coll={wide['gc_at_min']:.3f}, sigma_laser={wide['sl_at_min']:.3f}"
          f" (free fit {gc0:.3f}, {sl0:.3f})")
    print(f"    dchi2=5.99 region closed inside grid: {wide['closed_95']}"
          + (f"  (open edges: {', '.join(wide['edges_open'])})" if wide["edges_open"] else ""))
    print(f"    transit railed (<0.02 MHz) on {wide['transit_railed'].mean() * 100:.0f}% of cells")
    # is the free fit the GLOBAL optimum, or just a local one? the map's retries
    # explore basins the single free fit cannot; a positive gap means the map
    # found deeper chi2 elsewhere -- the strongest possible argument that the
    # split is a bound, not a measurement
    gap_wide = r["chi2"] - wide["chi2_min"]
    print(f"    free-fit chi2 - wide-map chi2_min = {gap_wide:+.1f}"
          + ("  (the free fit is a LOCAL optimum; the profile found deeper)"
             if gap_wide > 6.0 else "  (the free fit is the map's optimum)"))
    print(f"    fresh-seed audit (every 5th cell): max gain {wide['audit_max_gain']:.3f}")
    wfl = valley_floor(wide["gc_grid"], wide["sl_grid"], wide["dchi2"])

    zg = np.linspace(max(gc0 - ZOOM_NSD * sd_gc, 1e-3), gc0 + ZOOM_NSD * sd_gc, ZOOM_N)
    zs = np.linspace(sl0 - ZOOM_NSD * sd_sl, sl0 + ZOOM_NSD * sd_sl, ZOOM_N)
    zoom = width_profile_2d(freqs, volts, law=law,
                            transit_seed=r["fit"]["transit"], nu_step=0.01,
                            gc_grid=zg, sl_grid=zs, audit_stride=5)
    # the ellipse/straightness verdicts hold only where the profiled transit is
    # NOT pinned at its 0 bound (there the Gaussian profile<->marginal-ellipse
    # equivalence fails), so the floor fit is restricted to unpinned rows
    unpinned_rows = ~np.asarray(zoom["transit_railed"]).all(axis=1)
    zfl = valley_floor(zoom["gc_grid"], zoom["sl_grid"], zoom["dchi2"],
                       row_mask=unpinned_rows)
    dmin = zoom["chi2_min"] - r["chi2"]
    slope_pred = r["corr"][0][1] * sd_gc / sd_sl
    chi2_red = r["chi2"] / max(r["ndata"] - r["nparams"], 1)
    print(f"\n  ZOOM ({ZOOM_N}x{ZOOM_N}, +/-{ZOOM_NSD:.0f} marginal sigmas):")
    print(f"    profile chi2_min - free-fit chi2 = {dmin:+.2f} (should be ~0: same model space)")
    print(f"    warm-start trapping audit (every 5th cell refit fresh): "
          f"max gain {zoom['audit_max_gain']:.3f} (<<2.30 certifies the surface)")
    print(f"    transit railed on {zoom['transit_railed'].mean() * 100:.0f}% of zoom cells; "
          f"floor fit restricted to the {int(unpinned_rows.sum())}/{ZOOM_N} unpinned rows")
    print(f"    ridge slope d(gc)/d(sl) = {zfl['ridge_slope']:+.3f}  (local covariance predicts "
          f"{slope_pred:+.3f})")
    slope_ok = (np.isfinite(zfl["ridge_slope"])
                and abs(zfl["ridge_slope"] - slope_pred) < 0.5 * abs(slope_pred) + 0.1)
    straight = zfl["banana_rms"] < 1.5 * zfl["gc_step"]
    print(f"    banana RMS = {zfl['banana_rms']:.4f} MHz vs gc step {zfl['gc_step']:.4f} => "
          + ("STRAIGHT" if straight else "CURVED")
          + f"; slope {'AGREES with' if slope_ok else 'DISAGREES with'} the covariance")

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
        w.writerow(["banana_rms", "zoom_profile", f"{zfl['banana_rms']:.4f}",
                    f"MHz; RMS of the zoom-map valley floor about a straight line, "
                    f"transit-unpinned rows only (vs gc grid step {zfl['gc_step']:.4f}; "
                    f"the trust verdict needs this AND the slope agreement below)"])
        w.writerow(["ridge_slope", "zoom_profile", f"{zfl['ridge_slope']:.3f}",
                    f"d(gamma_coll)/d(sigma_laser) along the profile valley; the local "
                    f"covariance predicts {slope_pred:.3f} (agreement = the Gaussian "
                    f"profile<->ellipse correspondence holds where transit is unpinned)"])
        w.writerow(["profile_free_gap", "zoom_profile", f"{dmin:.2f}",
                    "profile chi2_min minus the free-fit chi2 (same model space; ~0 = consistent)"])
        w.writerow(["audit_max_gain", "zoom_profile", f"{zoom['audit_max_gain']:.3f}",
                    "largest chi2 improvement when every 5th cell is refit from the fresh "
                    "seed (warm-start trapping bound; <<2.30 certifies the surface)"])
        w.writerow(["audit_max_gain", "wide_profile", f"{wide['audit_max_gain']:.3f}",
                    "same fresh-seed audit on the wide map"])
        w.writerow(["transit_railed_frac", "zoom_profile", f"{zoom['transit_railed'].mean():.2f}",
                    "fraction of zoom cells whose profiled transit pins at its 0 bound "
                    "(there the Gaussian ellipse equivalence does not apply)"])
        for nm, rb in (("gaussian", r_gauss), ("cusp", r_cusp)):
            w.writerow(["branch", nm, f"{rb['chi2']:.1f}",
                        f"raw chi2; gc={rb['fit']['gamma_coll']:.3f}, "
                        f"sl={rb['fit']['sigma_laser']:.3f}, tr={rb['fit']['transit']:.3f} MHz "
                        f"(two-start local fit; the analysis anchors at the deeper branch)"])
        w.writerow(["branch_gap", "local", f"{branch_gap:.1f}",
                    "chi2 gap between the Gaussian- and cusp-dominated local basins "
                    "(the branch choice was invisible to a single-start fit)"])
        w.writerow(["wide_free_gap", "wide_profile", f"{gap_wide:.1f}",
                    "free-fit chi2 minus the wide-map chi2_min; >6 means the free fit "
                    "(and hence the local covariance analysis above) sits at a LOCAL "
                    "optimum and the global valley is deeper -- the map-level statement "
                    "of the split's non-identifiability"])
        closed_scaled = wide["edge_min_dchi2"] > 5.99 * max(chi2_red, 1.0)
        w.writerow(["closed_95", "wide_profile", str(wide["closed_95"]),
                    f"does the dchi2=5.99 region (raw, shape diagnostic) close inside the "
                    f"wide grid (sub-grid edge minima; edge min dchi2 = "
                    f"{wide['edge_min_dchi2']:.1f})? open edges: "
                    f"{','.join(wide['edges_open']) or 'none'}; at the chi2_red-scaled "
                    f"threshold 5.99x{max(chi2_red, 1.0):.2f} the verdict is "
                    f"{'the same' if closed_scaled == wide['closed_95'] else 'DIFFERENT'}"])

    # the grids + surfaces, for fig7 (long CSV: map|axis|index rows, then map|cell rows)
    with open(C.RESULTS_DIR / "identifiability_profile.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "unit"])
        for name, p in (("wide", wide), ("zoom", zoom)):
            for i, g in enumerate(p["gc_grid"]):
                w.writerow([f"{name}_gc", str(i), f"{g:.5f}", "MHz gamma_coll axis"])
            for i, s in enumerate(p["sl_grid"]):
                w.writerow([f"{name}_sl", str(i), f"{s:.5f}", "MHz sigma_laser axis"])
            for i in range(len(p["sl_grid"])):
                for j in range(len(p["gc_grid"])):
                    w.writerow([f"{name}_dchi2", f"{i}|{j}", f"{p['dchi2'][i][j]:.3f}",
                                "delta chi2 (raw) [sl_index|gc_index]"])
            for i in range(len(p["sl_grid"])):
                for j in range(len(p["gc_grid"])):
                    w.writerow([f"{name}_transit", f"{i}|{j}", f"{p['transit'][i][j]:.4f}",
                                "MHz; profiled transit at this cell (<0.02 = pinned at "
                                "the 0 bound, where the ellipse equivalence fails)"])
        for a, b, nm in ((0, 0, "gc_gc"), (1, 1, "sl_sl"), (0, 1, "gc_sl")):
            w.writerow(["cov", nm, f"{r['cov'][a][b]:.6e}",
                        "MHz^2; local (gamma_coll, sigma_laser) covariance for the ellipse overlay"])
        w.writerow(["fit", "gamma_coll", f"{gc0:.5f}", "MHz free-fit gamma_coll"])
        w.writerow(["fit", "sigma_laser", f"{sl0:.5f}", "MHz free-fit sigma_laser"])
        # raw chi2 anchors, so the wide-vs-free gap is reproducible from this
        # file alone (dchi2 grids are each relative to their own map minimum)
        w.writerow(["chi2", "free_fit", f"{r['chi2']:.2f}", "raw chi2 of the free 3-width fit"])
        w.writerow(["chi2", "wide_min", f"{wide['chi2_min']:.2f}", "raw chi2 at the wide-map minimum"])
        w.writerow(["chi2", "zoom_min", f"{zoom['chi2_min']:.2f}", "raw chi2 at the zoom-map minimum"])
        w.writerow(["floor_n", "wide", str(len(wfl["floor_sl"])), "valley-floor rows inside dchi2<5.99"])

    print("\n  READING: the archive pins the TOTAL width tightly but the SPLIT loosely;")
    print(f"  locally the profile {'CONFIRMS' if straight and slope_ok and abs(dmin) < 6 else 'QUALIFIES'} "
          f"the covariance ({'straight' if straight else 'curved'} valley, "
          f"slope {'agreeing' if slope_ok else 'disagreeing'}, min gap {dmin:+.1f});")
    print(f"  globally the wide map "
          + (f"finds DEEPER chi2 ({gap_wide:+.1f}) away from the free fit -- the free "
             f"fit is one of several near-degenerate optima -- "
             if gap_wide > 6.0 else "confirms the free fit as its optimum, ")
          + f"and the dchi2=5.99 region (raw, at this grid resolution) "
          f"{'closes inside the physical range' if wide['closed_95'] else 'runs off the grid edges'}.")
    print("  Either way the split stays a w0-conditional statement: the knife-edge w0")
    print("  fixes transit to within its own precision and COLLAPSES the degeneracy")
    print("  (not removes it exactly). Wrote identifiability.csv + identifiability_profile.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
