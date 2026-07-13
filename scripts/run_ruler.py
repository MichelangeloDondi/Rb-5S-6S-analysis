#!/usr/bin/env python3
"""
M2 real-data run: calibrate the frequency axis from every EOM ruler block.

For each ruler block (per-T rulers, and per-peak before/after brackets):
  1. build a noise law from the block's own traces (M1 machinery is
     signal-blind, so it works on multi-tooth rulers too);
  2. constrained comb fit each trace -> per-trace Δ (ms);
  3. combine per block with scatter inflation -> block Δ, rate = 6.25/Δ MHz/ms
     on the LASER axis (constants.TOOTH_SPACING_LASER_HZ, exact);
  4. free-center diagnostic each trace -> per-tooth departures feeding the
     pooled sweep-nonlinearity map ν(t).

Then: the campaign rate (inverse-variance over blocks with scatter
inflation), before-vs-after consistency per peak (the drift-over-a-session
systematic), and the nonlinearity map (rate vs window position).

Outputs
-------
results/ruler_blocks.csv    one row per block: Δ, Δ_err, rate, block_chi2_red,
                            n_traces, n_fallback_init, mean_acf_score
results/ruler_traces.csv    one row per trace (for auditing / the map)
results/ruler_nlmap.csv     pooled local rate vs window position
stdout                      campaign rate; per-peak before/after table;
                            cold-block behaviour; nonlinearity summary
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
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.ruler import fit_comb, fit_comb_free_centers, combine_block  # noqa: E402

MHZ_PER_TOOTH = TOOTH_SPACING_LASER_HZ / 1e6  # 6.25 MHz, laser axis


def block_key(r):
    if r["role"] == "ruler_t":
        return ("T", r["peak"], r["temperature_C"], "")
    return ("P", r["peak"], "130", r["bracket"])  # before/after brackets


def rate_of(delta_ms, delta_err_ms):
    """MHz/ms (laser axis) and its error from Δ (ms)."""
    rate = MHZ_PER_TOOTH / delta_ms
    return rate, rate * delta_err_ms / delta_ms


def combine_rates(rates, errs):
    """Inverse-variance mean with PDG scatter inflation."""
    rates, errs = np.asarray(rates), np.asarray(errs)
    w = 1.0 / errs ** 2
    mean = float(np.sum(w * rates) / np.sum(w))
    err = float(1.0 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(w * (rates - mean) ** 2) / max(len(rates) - 1, 1))
    if chi2 > 1.0:
        err *= np.sqrt(chi2)
    return mean, err, chi2


def main() -> int:
    rows = load_manifest()
    blocks = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["rf_on"] == "True":
            blocks[block_key(r)].append(r)

    print(f"M2 ruler calibration over {len(blocks)} blocks ...")
    RESULTS_DIR = C.RESULTS_DIR
    RESULTS_DIR.mkdir(exist_ok=True)

    block_out, trace_out, nlmap_pts = [], [], []
    for key in sorted(blocks):
        session, peak, T, bracket = key
        traces, tvs, skipped = [], [], 0
        for r in blocks[key]:
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            # skip only traces broken as rulers (dropout-riddled / no comb);
            # low SNR is NOT a skip — the fit + combination handle it.
            hf = hard_flags(m, rf_on=True) + ingest_flags(info)
            if any("dropout" in f or "no comb" in f or "truncated" in f for f in hf):
                skipped += 1
                continue
            traces.append(r); tvs.append((t, v))
        if len(tvs) < 2:
            print(f"  [skip] {key}: only {len(tvs)} usable traces")
            continue

        law = condition_noise_model([v for _, v in tvs])
        fits, nfallback, block_nl = [], 0, []
        for (r, (t, v)) in zip(traces, tvs):
            try:
                f = fit_comb(t, v, law)
            except RuntimeError as e:
                print(f"  [warn] fit failed {r['file']}: {e}")
                continue
            nfallback += int(f["init_fallback"])
            rate, rate_err = rate_of(f["delta_ms"], f["delta_err_ms"])
            trace_out.append([r["file"], session, peak, T, bracket, r["repeat_idx"],
                              f["delta_ms"], f["delta_err_ms"], rate, f["width_ms"],
                              f["chi2_red"], f["init_fallback"], f["acf_score"]])
            fits.append(f)
            # free-center diagnostic -> local (position, rate) tooth-pair points
            try:
                fc = fit_comb_free_centers(t, v, f, law)
                cs = sorted(zip(fc["n"], fc["centers_ms"], fc["center_err_ms"]))
                for (n1, c1, e1), (n2, c2, e2) in zip(cs, cs[1:]):
                    if n2 - n1 == 1 and (c2 - c1) > 0:
                        dc = c2 - c1
                        local_rate = MHZ_PER_TOOTH / dc
                        # error on rate = rate * relative error on the spacing dc
                        rate_err_pt = local_rate * np.hypot(e1, e2) / dc
                        block_nl.append((0.5 * (c1 + c2), local_rate, rate_err_pt))
            except RuntimeError:
                pass

        if len(fits) < 2:
            continue
        blk = combine_block(fits)
        rate, rate_err = rate_of(blk["delta_ms"], blk["delta_err_ms"])
        # normalize each tooth-pair's local rate by THIS block's rate so the
        # pooled map isolates the sweep SHAPE ν(t)/⟨ν⟩, not the 0.6%
        # block-to-block rate scatter (self-review, 2026-07-11).
        for pos, lr, le in block_nl:
            nlmap_pts.append((pos, lr / rate, le / rate))
        block_out.append({
            "session": session, "peak": peak, "T": T, "bracket": bracket,
            "delta_ms": blk["delta_ms"], "delta_err_ms": blk["delta_err_ms"],
            "rate": rate, "rate_err": rate_err, "block_chi2_red": blk["block_chi2_red"],
            "n": blk["n"], "n_fallback": nfallback, "skipped": skipped,
        })

    # ---- write tables ----
    with open(RESULTS_DIR / "ruler_traces.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "session", "peak", "T", "bracket", "repeat_idx",
                    "delta_ms", "delta_err_ms", "rate_MHzms", "width_ms",
                    "chi2_red", "init_fallback", "acf_score"])
        w.writerows(trace_out)
    with open(RESULTS_DIR / "ruler_blocks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(block_out[0].keys()))
        w.writeheader(); w.writerows(block_out)

    # ---- campaign rate ----
    rates = np.array([b["rate"] for b in block_out])
    errs = np.array([b["rate_err"] for b in block_out])
    crate, cerr, cchi2 = combine_rates(rates, errs)
    # Persist the AUTHORITATIVE campaign rate (inverse-variance + PDG scatter
    # inflation) so the ledger READS it rather than re-deriving it with a
    # naive unweighted mean -- which drifted the headline to 0.04265 vs the
    # weighted 0.04257 (2026-07-12).
    with open(C.RESULTS_DIR / "ruler_campaign.csv", "w", newline="") as f:
        wc = csv.DictWriter(f, fieldnames=["rate_laser", "rate_laser_err", "block_chi2_red",
                                           "n_blocks", "scatter_pct"])
        wc.writeheader()
        wc.writerow({"rate_laser": crate, "rate_laser_err": cerr, "block_chi2_red": cchi2,
                     "n_blocks": len(block_out),
                     "scatter_pct": float(100 * rates.std() / rates.mean())})
    print(f"\n{'='*70}\nCAMPAIGN RATE (laser axis): {crate:.5f} +/- {cerr:.5f} MHz/ms"
          f"  (block chi2_red {cchi2:.1f})")
    print(f"  = {crate*2:.5f} MHz/ms transition axis; mean tooth spacing "
          f"{MHZ_PER_TOOTH/crate:.1f} ms; block spread {100*rates.std()/rates.mean():.1f}% RMS")
    print(f"  blocks: {len(block_out)}, plain range {rates.min():.4f}-{rates.max():.4f}")

    # ---- before/after per peak (P-session drift systematic) ----
    print(f"\n{'-'*70}\nBEFORE vs AFTER brackets per peak (fixed-condition session drift):")
    print(f"{'peak':>6s} {'before Δ(ms)':>16s} {'after Δ(ms)':>16s} {'Δdiff/σ':>9s}")
    for peak in ("4121", "4154", "4192", "4207"):
        b = next((x for x in block_out if x["session"] == "P" and x["peak"] == peak
                  and x["bracket"] == "before"), None)
        a = next((x for x in block_out if x["session"] == "P" and x["peak"] == peak
                  and x["bracket"] == "after"), None)
        if b and a:
            nsig = (b["delta_ms"] - a["delta_ms"]) / np.hypot(b["delta_err_ms"], a["delta_err_ms"])
            print(f"{peak:>6s} {b['delta_ms']:>8.2f}+/-{b['delta_err_ms']:<5.2f} "
                  f"{a['delta_ms']:>8.2f}+/-{a['delta_err_ms']:<5.2f} {nsig:>+9.1f}")

    # ---- cold-block behaviour ----
    print(f"\n{'-'*70}\nCold blocks (init fallbacks used / block chi2_red):")
    for b in block_out:
        if b["n_fallback"] > 0 or b["block_chi2_red"] > 3.0:
            print(f"  {b['session']} {b['peak']} T{b['T']} {b['bracket']}: "
                  f"{b['n_fallback']}/{b['n']} fallback, chi2_red {b['block_chi2_red']:.1f}, "
                  f"rate {b['rate']:.4f}, {b['skipped']} skipped")

    # ---- nonlinearity map ----
    if nlmap_pts:
        pts = np.array(nlmap_pts)
        pos, rrel, le = pts[:, 0], pts[:, 1], pts[:, 2]  # rrel = local/block rate
        edges = np.linspace(pos.min(), pos.max(), C.RULER_NLMAP_NBINS + 1)
        with open(RESULTS_DIR / "ruler_nlmap.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["pos_ms", "rate_rel", "rate_rel_err", "n"])
            rows_map = []
            for i in range(C.RULER_NLMAP_NBINS):
                mask = (pos >= edges[i]) & (pos < edges[i + 1])
                if mask.sum() >= 3:
                    ww = 1.0 / le[mask] ** 2
                    r = float(np.sum(ww * rrel[mask]) / np.sum(ww))
                    e = float(1.0 / np.sqrt(np.sum(ww)))
                    rows_map.append((0.5 * (edges[i] + edges[i + 1]), r, e, int(mask.sum())))
            w.writerows(rows_map)
        rmap = np.array([r[1] for r in rows_map])
        emap = np.array([r[2] for r in rows_map])
        # is the position dependence significant vs the per-bin errors?
        chi2_flat = float(np.sum(((rmap - 1.0) / emap) ** 2) / len(rmap))
        print(f"\n{'-'*70}\nNONLINEARITY MAP (rate normalized per block): {len(pts)} tooth-pair "
              f"points, {len(rows_map)} bins")
        print(f"  relative local rate {rmap.min():.4f}-{rmap.max():.4f} "
              f"({100*(rmap.max()-rmap.min()):.1f}% peak-to-peak); "
              f"chi2/bin vs flat = {chi2_flat:.1f} "
              f"({'significant curvature' if chi2_flat > 3 else 'consistent with a flat sweep'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
