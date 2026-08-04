#!/usr/bin/env python3
"""
M2 real-data run: calibrate the frequency axis from every EOM ruler block.

For each ruler block (per-T rulers, and per-peak before/after brackets):
  1. build a noise law from the block's own traces (M1 machinery is
     signal-blind, so it works on multi-tooth rulers too);
  2. constrained comb fit each trace, through the tooth-indexing VALIDITY
     ladder (ruler.validated_comb_fit: top-three amplitude rule, comb-phase
     re-index, mirror excision, quarantine) -> per-trace Δ (ms);
  3. combine per block with scatter inflation -> block Δ, rate = 6.25/Δ MHz/ms
     on the LASER axis (constants.TOOTH_SPACING_LASER_HZ, exact);
  4. free-center diagnostic each trace -> per-tooth departures feeding the
     pooled sweep-nonlinearity map ν(t).

Quarantined traces keep their row in ruler_traces.csv and enter nothing else.

Then: the campaign rate (inverse-variance over blocks with scatter
inflation), before-vs-after consistency per peak (the drift-over-a-session
systematic), and the nonlinearity map (rate vs window position).

Outputs
-------
results/ruler_blocks.csv    one row per block: Δ, Δ_err, rate, block_chi2_red,
                            n_traces, n_fallback_init, mean_acf_score
results/ruler_traces.csv    one row per trace (for auditing / the map), now
                            carrying the seven fitted tooth heights, the
                            top-three verdict, the ladder action and the
                            quarantine record
results/ruler_nlmap.csv     pooled local rate vs window position
stdout                      campaign rate; per-peak before/after table;
                            cold-block behaviour; nonlinearity summary
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import TOOTH_SPACING_LASER_HZ  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.ruler import (fit_comb_free_centers, combine_block,  # noqa: E402
                          validated_comb_fit)
from rb5s6s import rate_model as RMOD  # noqa: E402

MHZ_PER_TOOTH = TOOTH_SPACING_LASER_HZ / 1e6  # 6.25 MHz, laser axis

# results/ruler_traces.csv schema. The seven HEIGHTS are persisted here for the
# first time: 105 traces x 7 slots is the matrix any amplitude model, and any
# audit of the tooth labelling, has to be tested against, and until now it was
# recomputed-and-discarded on every run.
TRACE_HEADER = [
    "file", "session", "peak", "T", "bracket", "repeat_idx",
    "delta_ms", "delta_err_ms", "rate_MHzms", "width_ms", "chi2_red",
    "init_fallback", "acf_score",
    # the seven fitted tooth heights, k = -3 .. +3
    "h_m3", "h_m2", "h_m1", "h_0", "h_p1", "h_p2", "h_p3",
    "fit_rms", "resid_norm", "n_fitted", "t0_ms",
    # the top-three amplitude verdict. top3_gated says whether it was allowed
    # to ACT on this run (config.RULER_TOP3_GATED, False on landing) or was
    # only recorded, which is the difference between a diagnostic and a gate.
    "top3_ok", "top3_marginal", "rank_m1", "rank_p1", "n_railed", "verdict",
    "top3_gated",
    # what the re-index ladder decided. delta_advised_ms is the spacing the
    # ladder would have returned, so the size of the effect is on the record
    # even while the verdict is advisory. quarantine_advised is the ladder's
    # recommendation; quarantined is what actually happened.
    "reindex_action", "reindex_j", "excised_k", "n_refits", "delta_advised_ms",
    "quarantine_advised", "quarantined", "quarantine_reason",
    # the trim record (written by Phase 2's trimmer; empty until then)
    "trimmed", "trim_start_ms", "trim_end_ms", "trim_reason",
]
_H_COLS = ["h_m3", "h_m2", "h_m1", "h_0", "h_p1", "h_p2", "h_p3"]


def trace_row(r, session, peak, T, bracket, f, rate):
    """One ruler trace as a TRACE_HEADER-ordered dict. Quarantined traces get a
    row like any other: the calibration drops them, the record keeps them, and
    a removal nobody can see is a removal nobody can check."""
    row = {"file": r["file"], "session": session, "peak": peak, "T": T,
           "bracket": bracket, "repeat_idx": r["repeat_idx"],
           "delta_ms": f["delta_ms"], "delta_err_ms": f["delta_err_ms"],
           "rate_MHzms": rate, "width_ms": f["width_ms"],
           "chi2_red": f["chi2_red"], "init_fallback": f["init_fallback"],
           "acf_score": f["acf_score"]}
    row.update(dict(zip(_H_COLS, f["heights"])))
    for k in ("fit_rms", "resid_norm", "n_fitted", "t0_ms", "rank_m1", "rank_p1",
              "n_railed", "verdict", "top3_gated", "reindex_action", "reindex_j",
              "excised_k", "n_refits", "delta_advised_ms", "quarantine_advised",
              "quarantined", "quarantine_reason", "trimmed",
              "trim_start_ms", "trim_end_ms", "trim_reason"):
        row[k] = f[k]
    row["top3_ok"] = f["top3_ok"]
    row["top3_marginal"] = f["marginal"]
    return row


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
                f = validated_comb_fit(t, v, law)
            except RuntimeError as e:
                print(f"  [warn] fit failed {r['file']}: {e}")
                continue
            rate, rate_err = rate_of(f["delta_ms"], f["delta_err_ms"])
            trace_out.append(trace_row(r, session, peak, T, bracket, f, rate))
            # A quarantined trace keeps its row and contributes NOTHING: not to
            # the block spacing, not to the campaign rate, not to the
            # nonlinearity map. Its tooth labelling did not survive the ladder,
            # so its spacing is not a measurement of the comb.
            if f["quarantined"]:
                continue
            nfallback += int(f["init_fallback"])
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
        w = csv.DictWriter(f, fieldnames=TRACE_HEADER)
        w.writeheader(); w.writerows(trace_out)
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

    # ---- time-resolved rate models (rate_model.py) ----
    # The per-block constants above stay authoritative as constructor and
    # fallback; the models overlay them in load_t_rates where the recovered
    # clocks license it. Fitted here so one run_ruler pass regenerates both.
    # Quarantined traces are excluded here for the same reason they are
    # excluded from the blocks: a spacing whose tooth labelling did not survive
    # the ladder is not a measurement of the rate, and rate(t) is a rate model.
    trace_dicts = [{k: str(row[k]) for k in TRACE_HEADER}
                   for row in trace_out if not row["quarantined"]]
    models = RMOD.fit_rate_models(trace_dicts, RMOD.load_clock())
    if models:
        RMOD.write_models(models)
        print(f"  rate(t) models: {len(models)} (session,peak) fits -> "
              f"results/{RMOD.MODEL_CSV}")

    # ---- tooth-indexing validity census ----
    # Printed BEFORE the physics tables so a reader meets the calibration's own
    # health before any number derived from it. Pre-registered in
    # docs/notes/ruler_validity_and_trim_prereg.md.
    gated = bool(C.RULER_TOP3_GATED)
    verdicts = Counter(r["verdict"] for r in trace_out)
    actions = Counter(r["reindex_action"] for r in trace_out)
    reasons = Counter(r["quarantine_reason"] for r in trace_out
                      if r["quarantine_advised"])
    nq = sum(1 for r in trace_out if r["quarantined"])
    nadv = sum(1 for r in trace_out if r["quarantine_advised"])
    shifts = [abs(r["delta_advised_ms"] - r["delta_ms"]) for r in trace_out]
    print(f"\n{'-'*70}\nTOOTH-INDEXING VALIDITY over {len(trace_out)} fitted ruler traces "
          f"({'ACTING' if gated else 'RECORDED ONLY, config.RULER_TOP3_GATED is False'}):")
    print("  top-three verdict: " + ", ".join(
        f"{v} {verdicts.get(v, 0)}" for v in ("PASS", "MARGINAL", "FAIL")))
    print("  ladder action:     " + ", ".join(
        f"{a} {actions.get(a, 0)}" for a in ("none", "phase_shift", "excision")))
    print(f"  largest spacing the ladder would have moved: {max(shifts):.2f} ms "
          f"({sum(1 for s in shifts if s > 0.01)} traces would move at all)")
    if gated:
        print(f"  QUARANTINE CENSUS: {nq} trace(s) excluded from every block, "
              f"from the campaign rate and from the nonlinearity map")
    else:
        print(f"  QUARANTINE CENSUS: {nq} excluded. {nadv} trace(s) would be "
              f"quarantined if the verdict were gating, and are NOT:")
    for reason, n in sorted(reasons.items()):
        print(f"    {n:>3d}  {reason}")
        for r in trace_out:
            if r["quarantine_reason"] == reason:
                print(f"         {r['file']}  (delta {r['delta_ms']:.2f} ms, "
                      f"ranks {r['rank_m1']}/{r['rank_p1']}, "
                      f"{r['n_railed']} railed, {r['n_refits']} refits)")
    if not reasons:
        print("    none")

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
