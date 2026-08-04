#!/usr/bin/env python3
"""
One place to read every trim and every removal the pipeline made.

The residual-tail trimmer runs at three stages and each stage writes its
decision into its own table: the quality pass into `results/qc_metrics.csv`,
the ruler ladder into `results/ruler_traces.csv`, and the condition fit inside
`rb5s6s.linefit`. The pre-registered group outlier rule removes traces from two
different populations into two more places. A reader who wants to know what the
pipeline cut, and why, should not have to know any of that.

This script collects all of it into `results/trim_report.csv`, one row per
trace per stage, from the committed tables alone. It fits no data and loads no
raw trace, so it is cheap, deterministic, and re-runnable in a checkout with no
`data_raw/`.

Stages
------
`qc`       every manifest trace, from `results/qc_metrics.csv`. Rulers report
           `not applicable, multi-peak trace`, because their authoritative trim
           record is the ruler stage below.
`ruler`    every fitted ruler, from `results/ruler_traces.csv`.
`linefit`  every canonical radio frequency off trace. The condition fit runs the
           trimmer, but `run_linefit.py` does not persist its per-trace record,
           so `trimmed` is left EMPTY here rather than filled with a zero this
           script cannot verify. An empty cell is not a claim that nothing was
           trimmed. `run_linefit.py` prints the count it took, and a nonzero
           count there is the signal that the record has to start being written.
`outlier`  one row per trace the pre-registered group rule removed, from either
           population, with the token that removed it.

Outputs
-------
results/trim_report.csv   the collected record
stdout                    the census, by stage and by reason
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.ingest import load_manifest  # noqa: E402

HEADER = ["file", "stage", "role", "peak", "T", "power_mW", "bracket",
          "trimmed", "trim_start_ms", "trim_end_ms", "trim_reason",
          "removed", "removed_reason"]

LINEFIT_UNRECORDED = "per-trace record not persisted by run_linefit.py"


def _rows(name):
    path = C.RESULTS_DIR / name
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _ctx(man, file):
    r = man.get(file, {})
    return {"role": r.get("role", ""), "peak": r.get("peak", ""),
            "T": r.get("temperature_C", ""), "power_mW": r.get("power_mW", ""),
            "bracket": r.get("bracket", "")}


def _row(man, file, stage, *, trimmed=0, start="", end="", reason="",
         removed=0, removed_reason=""):
    return {"file": file, "stage": stage, **_ctx(man, file),
            "trimmed": "" if trimmed is None else int(trimmed),
            "trim_start_ms": start, "trim_end_ms": end,
            "trim_reason": reason, "removed": int(removed),
            "removed_reason": removed_reason}


def _truthy(x):
    """The source tables write this flag three ways: the quality table as a
    float ("1.0", every metric there is a float), the ruler table as a Python
    bool, and the outlier columns as an int. All three have to read the same
    here, and the first version of this helper missed the float and silently
    reported a census of zero next to thirty-four reasons."""
    s = str(x).strip().lower()
    if s in {"true", "yes"}:
        return True
    try:
        return float(s) != 0.0
    except ValueError:
        return False


def main() -> int:
    man = {r["file"]: r for r in load_manifest()}
    out = []

    for r in _rows("qc_metrics.csv"):
        out.append(_row(man, r["file"], "qc",
                        trimmed=_truthy(r.get("trimmed")),
                        start=r.get("trim_start_ms", ""),
                        end=r.get("trim_end_ms", ""),
                        reason=r.get("trim_reason", "")))

    for r in _rows("ruler_traces.csv"):
        out.append(_row(man, r["file"], "ruler",
                        trimmed=_truthy(r.get("trimmed")),
                        start=r.get("trim_start_ms", ""),
                        end=r.get("trim_end_ms", ""),
                        reason=r.get("trim_reason", "")))

    for f, r in sorted(man.items()):
        if r["flag"] == "canonical" and r["rf_on"] == "False":
            out.append(_row(man, f, "linefit", trimmed=None,
                            reason=LINEFIT_UNRECORDED))

    for name in ("ruler_traces.csv", "qc_metrics.csv"):
        for r in _rows(name):
            if _truthy(r.get("outlier")):
                out.append(_row(man, r["file"], "outlier", removed=1,
                                removed_reason=r.get("outlier_reason", "")))

    C.RESULTS_DIR.mkdir(exist_ok=True)
    with open(C.RESULTS_DIR / "trim_report.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(out)
    print(f"wrote results/trim_report.csv ({len(out)} rows over "
          f"{len({r['file'] for r in out})} traces)\n")

    for stage in ("qc", "ruler", "linefit", "outlier"):
        rows = [r for r in out if r["stage"] == stage]
        if not rows:
            continue
        n = sum(r["trimmed"] for r in rows if r["trimmed"] != "")
        removed = sum(r["removed"] for r in rows)
        print(f"{stage:>8s}: {len(rows):>3d} rows, {n} trimmed, {removed} removed")
        for reason, k in sorted(Counter(
                r["trim_reason"] or r["removed_reason"] for r in rows).items()):
            print(f"          {k:>3d}  {reason or 'nothing to report'}")
    for r in out:
        if r["trimmed"]:
            print(f"\n  {r['stage']:>7s}  {r['file']}: keeps "
                  f"{float(r['trim_start_ms']):.0f} to {float(r['trim_end_ms']):.0f} ms")
    for r in out:
        if r["removed"]:
            print(f"  removed  {r['file']}: {r['removed_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
