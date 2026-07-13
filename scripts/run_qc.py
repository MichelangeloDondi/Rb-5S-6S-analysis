#!/usr/bin/env python3
"""
Run the M0 quality-control metrics over the full manifest and audit the
experimenter's curation symmetrically (user request, 2026-07-11: "challenge
my choices on both sides").

Outputs
-------
results/qc_metrics.csv   one row per trace: manifest fields + all QC metrics
                         + hard-flag list + sibling z-scores (height, FWHM,
                         wing noise) within its condition group
stdout                   the audit:
                         (a) discarded traces vs their canonical siblings —
                             does objective QC agree they are bad?
                         (b) canonical traces failing hard QC or standing out
                             vs siblings — did curation miss anything?
                         (c) quarantine set summary
                         (d) RF-state consistency check (comb vs label)

Policy reminder (docs/PLAN.md): hard-QC failures may exclude canonical traces
from headline fits (QC-based, pre-registered). Sibling outliers and
clean-looking discards are REPORTED, not auto-acted-on — the experimenter is
the instrument for apparatus context.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s.config import RESULTS_DIR  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags, sibling_zscores  # noqa: E402


def condition_key(r):
    """Traces that should be statistically interchangeable: same role, peak,
    condition (and bracket for rulers)."""
    return (r["role"], r["peak"], r["temperature_C"], r["power_mW"], r["bracket"])


def main() -> int:
    rows = load_manifest()
    print(f"QC over {len(rows)} traces ...")

    metrics = {}
    for r in rows:
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        m["n_valid"] = float(info["n_valid"])
        m["empty_interior"] = float(info["empty_interior"])
        m["axis_rebuilt"] = float(info["axis_rebuilt"])
        m["header_variant"] = info["header_variant"]
        m["hard_flags"] = "; ".join(
            hard_flags(m, rf_on=(r["rf_on"] == "True")) + ingest_flags(info))
        metrics[r["file"]] = m

    # sibling comparison: each trace vs the CANONICAL members of its condition
    groups = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical":
            groups[condition_key(r)].append(r)
    for r in rows:
        m = metrics[r["file"]]
        sibs = [s for s in groups.get(condition_key(r), []) if s["file"] != r["file"]]
        for name in ("height_v", "fwhm_ms", "sigma_wing_v"):
            vals = np.array([metrics[s["file"]][name] for s in sibs], dtype=float)
            m[f"zsib_{name}"] = sibling_zscores(m[name], vals) if len(vals) >= 3 else np.nan

    # ---- write full metrics table ----
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "qc_metrics.csv"
    mkeys = list(next(iter(metrics.values())).keys())
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "role", "flag", "peak", "temperature_C", "power_mW",
                    "rf_on", "bracket", "repeat_idx"] + mkeys)
        for r in rows:
            m = metrics[r["file"]]
            w.writerow([r["file"], r["role"], r["flag"], r["peak"], r["temperature_C"],
                        r["power_mW"], r["rf_on"], r["bracket"], r["repeat_idx"]]
                       + [m[k] for k in mkeys])
    print(f"wrote {out}\n")

    # ---- audit (a): the discarded traces vs their siblings ----
    print("=" * 78)
    print("(a) DISCARDED traces — does objective QC agree with the rejection?")
    for r in rows:
        if r["flag"] != "discarded":
            continue
        m = metrics[r["file"]]
        print(f"\n  {r['file']}  (peak {r['peak']}, T={r['temperature_C']}C, "
              f"P={r['power_mW'] or '-'}mW)")
        print(f"     hard flags : {m['hard_flags'] or 'NONE'}")
        print(f"     vs siblings: z(height)={m['zsib_height_v']:+.1f}  "
              f"z(FWHM)={m['zsib_fwhm_ms']:+.1f}  z(noise)={m['zsib_sigma_wing_v']:+.1f}")
        print(f"     snr={m['snr']:.0f}  n_major={int(m['n_major'])}  "
              f"z_spike={m['z_spike']:.1f}  z_step={m['z_step']:.1f}  "
              f"slope={m['base_slope_vps']:+.5f} V/s  fwhm={m['fwhm_ms']:.1f} ms")

    # ---- audit (b): canonical traces that fail hard QC or stand out ----
    print("\n" + "=" * 78)
    print("(b) CANONICAL traces failing hard QC (pre-registered exclusion candidates):")
    any_hard = False
    for r in rows:
        if r["flag"] == "canonical" and metrics[r["file"]]["hard_flags"]:
            any_hard = True
            m = metrics[r["file"]]
            print(f"   {r['file']}: {m['hard_flags']}")
    if not any_hard:
        print("   none")

    print("\n    canonical sibling outliers (|z| >= 5 on height/FWHM/noise; report-only):")
    any_out = False
    for r in rows:
        if r["flag"] != "canonical":
            continue
        m = metrics[r["file"]]
        zs = {k: m[f"zsib_{k}"] for k in ("height_v", "fwhm_ms", "sigma_wing_v")}
        bad = {k: z for k, z in zs.items() if np.isfinite(z) and abs(z) >= 5}
        if bad:
            any_out = True
            print(f"   {r['file']}: " + "  ".join(f"z({k})={z:+.1f}" for k, z in bad.items()))
    if not any_out:
        print("   none")

    # ---- audit (c): quarantine summary ----
    print("\n" + "=" * 78)
    print("(c) QUARANTINE set (aborted 4154 attempt): hard-flag summary")
    qrows = [r for r in rows if r["flag"] == "quarantined"]
    nbad = sum(1 for r in qrows if metrics[r["file"]]["hard_flags"])
    print(f"   {len(qrows)} traces, {nbad} with hard flags (note: trace-level QC "
          f"cannot detect condition-level problems such as a wrong power "
          f"calibration — quarantine stays regardless)")
    for r in qrows:
        if metrics[r["file"]]["hard_flags"]:
            print(f"     {r['file']}: {metrics[r['file']]['hard_flags']}")

    # ---- audit (d): RF-state consistency ----
    print("\n" + "=" * 78)
    print("(d) RF-state check (comb periodicity vs manifest rf_on):")
    bad_rf = [r for r in rows
              if ((r["rf_on"] == "False" and "comb periodicity" in metrics[r["file"]]["hard_flags"])
                  or (r["rf_on"] == "True" and "no comb" in metrics[r["file"]]["hard_flags"]))]
    if bad_rf:
        for r in bad_rf:
            m = metrics[r["file"]]
            print(f"   MISMATCH {r['file']} (rf_on={r['rf_on']}): "
                  f"comb_score={m['comb_score']:.2f} at {m['comb_period_ms']:.0f} ms")
    else:
        print("   all traces consistent with their RF label")

    # ---- audit (e): nonstandard exports salvaged at ingest ----
    print("\n" + "=" * 78)
    print("(e) nonstandard exports (salvaged or noteworthy at ingest):")
    any_note = False
    for r in rows:
        m = metrics[r["file"]]
        notes = []
        if m["axis_rebuilt"]:
            notes.append("time axis rebuilt from row index (low-precision export)")
        if m["header_variant"]:
            notes.append(f"header variant {m['header_variant']!r}")
        if m["empty_interior"] > 0:
            notes.append(f"{int(m['empty_interior'])} interior dropout rows")
        if notes:
            any_note = True
            print(f"   {r['file']} [{r['flag']}]: " + "; ".join(notes))
    if not any_note:
        print("   none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
