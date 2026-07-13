#!/usr/bin/env python3
"""
Populate the `qc_reason` provenance column of data_raw/MANIFEST.csv.

Curation audit (2026-07-12): "recoverable by rerunning the code" is a
weaker standard than "recorded" -- a referee asking *why* each of the 33
non-canonical traces was excluded should read the answer in the manifest, not
reconstruct it. This matters doubly here because the two exclusion classes have
DIFFERENT kinds of reasons, and neither is fully recomputable from the data:

  * the 29 QUARANTINED traces are individually CLEAN (no hard QC flags --
    verified at annotate time below, and in results/qc_metrics.csv): they are
    excluded SESSION-GRAIN as the aborted first 4154 130 C power attempt
    (redone in full), plus its EOM ruler brackets. The reason is a curation
    fact, not a per-trace defect, so it must be recorded.
  * the 4 DISCARDED traces are real excluded shots (NOT md5-dedup leftovers --
    each is a distinct measurement; only 4207nm_025mw2 has a same-name
    canonical twin). Their reasons come from the committed curation
    audit (DATA.md): one objective defect, three kept-excluded-by-
    pre-registration.

Idempotent: re-running refreshes the column in place; all other columns are
preserved. After a MANIFEST regeneration by import_data.py, run this to
restore the column.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s.config import MANIFEST_CSV  # noqa: E402
from rb5s6s.ingest import load_trace, trace_path  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402

# per-file reasons for the four curation discards -- sourced from the committed
# curation audit (DATA.md) and results/qc_metrics.csv
REASON_DISCARDED = {
    "4154nm_070c4.csv": (
        "curation discard: ~27% dimmer than its repeat siblings "
        "(zsib_height=-3.1, the one objective per-trace defect; "
        "curation audit, DATA.md)"),
    "4192nm_090c3.csv": (
        "curation discard: supernumerary 6th repeat, content clean -- "
        "stays excluded by pre-registration (DATA.md)"),
    "4207nm_025mw2.csv": (
        "curation discard: duplicate-name save superseded by canonical "
        "p_sweep/4207nm_025mw2.csv; the retrace-crossing structure is "
        "block-wide, not this trace's own defect (DATA.md)"),
    "4207nm_070c2.csv": (
        "curation discard: indistinguishable from kept siblings (flagged "
        "features are block-wide) -- stays excluded by pre-registration "
        "(DATA.md)"),
}

REASON_Q_RULER = (
    "session quarantine: EOM ruler bracket of the aborted first 4154 130 C "
    "power attempt -- a ruler for an aborted block is meaningless, excluded "
    "session-grain with it (DATA.md; trace individually clean, no hard flags)")
REASON_Q_POWER = (
    "session quarantine: aborted first 4154 130 C power attempt, redone in full "
    "(the canonical p_sweep covers all 5 powers; this partial retry only 25/125/"
    "225 mW, so REDUNDANT and not a serves_t130 anchor). Lines individually clean "
    "-- height/width match the redo to <2% -- but the 225 mW set carries a ~80x "
    "steeper baseline slope (high-power drift, the likely abort cause). Kept "
    "excluded by pre-registration: including them only TIGHTENS the S0 bound "
    "(2.04->1.92 MHz) and leaves beta untouched, so re-admitting previously-cut, "
    "drift-flagged data to improve a number is declined. See DATA.md.")


def reason_for(row: dict) -> str:
    if row["flag"] == "canonical":
        return ""
    if row["flag"] == "discarded":
        return REASON_DISCARDED[Path(row["file"]).name]
    # quarantined: ruler brackets vs power traces
    return REASON_Q_RULER if "eom" in Path(row["file"]).name else REASON_Q_POWER


def main() -> int:
    rows = list(csv.DictReader(open(MANIFEST_CSV)))
    fields = list(rows[0].keys())
    if "qc_reason" not in fields:
        fields.append("qc_reason")

    # self-check 1: the discard map covers exactly the discarded files
    disc = {Path(r["file"]).name for r in rows if r["flag"] == "discarded"}
    if disc != set(REASON_DISCARDED):
        raise SystemExit(f"discard map mismatch: manifest {disc} vs map "
                         f"{set(REASON_DISCARDED)} -- update REASON_DISCARDED")

    # self-check 2: the 'individually clean' claim written for quarantined rows
    # must be TRUE -- recompute hard flags on every quarantined trace now.
    dirty = []
    for r in rows:
        if r["flag"] != "quarantined":
            continue
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        hf = hard_flags(m, rf_on=(r["rf_on"] == "True")) + ingest_flags(info)
        if hf:
            dirty.append((r["file"], hf))
    if dirty:
        raise SystemExit(f"quarantined traces DO hard-flag -- fix the reason "
                         f"text before writing: {dirty[:3]}")

    for r in rows:
        r["qc_reason"] = reason_for(r)

    with open(MANIFEST_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    n = sum(1 for r in rows if r["qc_reason"])
    print(f"wrote qc_reason for {n} non-canonical rows "
          f"({len(rows)} total) to {MANIFEST_CSV}")
    print("self-checks passed: discard map exact; all 29 quarantined traces "
          "individually clean (no hard flags) -- the recorded reasons are true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
