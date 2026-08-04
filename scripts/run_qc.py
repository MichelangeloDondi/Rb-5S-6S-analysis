#!/usr/bin/env python3
"""
Run the M0 quality-control metrics over the full manifest and audit the
experimenter's curation symmetrically (pre-registered 2026-07-11: "challenge
my choices on both sides").

Outputs
-------
results/qc_metrics.csv   one row per trace: manifest fields + all QC metrics
                         + hard-flag list + sibling z-scores (height, FWHM,
                         wing noise) within its condition group + the
                         residual-tail trim record + the outlier mark
stdout                   the audit:
                         (a) discarded traces vs their canonical siblings —
                             does objective QC agree they are bad?
                         (b) canonical traces failing hard QC or standing out
                             vs siblings — did curation miss anything?
                         (c) quarantine set summary
                         (d) RF-state consistency check (comb vs label)

Policy reminder (docs/PLAN.md): hard-QC failures may exclude canonical traces
from headline fits (QC-based, pre-registered). Clean-looking discards are
REPORTED, not auto-acted-on. The experimenter is the instrument for apparatus
context.

Sibling outliers used to be report-only too. Since 2026-08-04 a single
pre-registered rule (docs/notes/ruler_validity_and_trim_prereg.md, amendment 2
B4, with the threshold recalibrated against the null in amendment 3) removes at
most one member per condition group from the CONDITION FITS, and
marks it in the table with `outlier` and `outlier_reason`. That removal is not a
hard flag and never enters `hard_flags`: a trace whose height or width its own
siblings do not share is a different statement from a trace that failed quality
control, and the archive-wide fit's admission gate reads the second, not the
first.
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
from rb5s6s import config as C  # noqa: E402
from rb5s6s.qc import (trace_metrics, hard_flags, ingest_flags,  # noqa: E402
                       sibling_zscores, outlier_threshold)

OUTLIER_REASON = "sibling_outlier"
"""The one token population B can carry (pre-registration amendment 2 B4).
Closed vocabulary, and it is NOT a hard flag: an outlier is removed from the
condition fits and keeps its row, which is a different decision from failing
quality control."""

_Z_METRICS = ("zsib_height_v", "zsib_fwhm_ms")


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
        m = trace_metrics(t, v, rf_on=(r["rf_on"] == "True"))
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
        m["outlier"] = 0
        m["outlier_reason"] = ""

    # ---- the group outlier rule, population B (amendment 2 B4) ----
    # One pass, at most one removal per condition group, on the LARGER of the
    # two sibling z scores the table already carries. Those are deviations in
    # scaled median-absolute-deviation units against the trace's own siblings,
    # so they are the statistic the rule was written for and no second scale is
    # applied. Only radio frequency off lines are tested here: the rulers have
    # their own population and their own statistic in run_ruler.py.
    outliers = []
    for key, members in sorted(groups.items()):
        n = len(members)
        if n < C.OUTLIER_MIN_GROUP or any(s["rf_on"] == "True" for s in members):
            continue
        dev = [max(abs(metrics[s["file"]][z]) for z in _Z_METRICS) for s in members]
        if not all(np.isfinite(d) for d in dev):
            continue
        # The z scores ARE the rule's deviation: sibling_zscores already centred
        # each metric on its siblings' median and scaled it by their scaled
        # median absolute deviation. So the threshold is applied to them
        # directly and the centring is not done twice. It is also why the
        # threshold reads the SIBLING null: a member left out of its own scale
        # deviates further than one included in it, and amendment 3 measures how
        # much further.
        thr = outlier_threshold(n, len(_Z_METRICS), scaling="sibling")
        i = int(np.argmax(dev))
        if dev[i] <= thr:
            continue
        f = members[i]["file"]
        metrics[f]["outlier"] = 1
        metrics[f]["outlier_reason"] = OUTLIER_REASON
        outliers.append((f, key, dev[i], thr, n))

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

    print("\n    SIBLING OUTLIERS REMOVED (the pre-registered rule, one pass, at "
          "most one per condition). These are excluded from the condition fits:")
    for f, key, d, thr, n in outliers:
        print(f"   {f}: deviation {d:.2f} against a threshold of {thr:.2f} "
              f"(n={n}, condition {key[1]} T{key[2]} P{key[3] or '-'})")
    if not outliers:
        print("   none")
    ntrim = sum(1 for r in rows if metrics[r["file"]]["trimmed"])
    nrefuse = sum(1 for r in rows
                  if metrics[r["file"]]["trim_reason"].startswith("refused"))
    nna = sum(1 for r in rows
              if metrics[r["file"]]["trim_reason"].startswith("not applicable"))
    print(f"\n    RESIDUAL-TAIL TRIM over {len(rows)} traces: {ntrim} trimmed, "
          f"{nrefuse} refused, {nna} not applicable (rulers), "
          f"{len(rows) - ntrim - nrefuse - nna} untouched")
    for r in rows:
        m = metrics[r["file"]]
        if m["trimmed"]:
            print(f"   {r['file']}: keeps {m['trim_start_ms']:.0f} to "
                  f"{m['trim_end_ms']:.0f} ms ({m['trim_reason']})")

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
