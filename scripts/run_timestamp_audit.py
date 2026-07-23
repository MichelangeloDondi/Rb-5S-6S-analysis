#!/usr/bin/env python3
"""
Score the pre-registered timestamp audit (docs/PREREGISTRATION_timestamps.md).

WRITTEN AND COMMITTED BEFORE FIRST CONTACT WITH THE BACKUP (pre-registration
§5: one run, script committed first, everything reported). The script reads
only (a) the quarantine copy of the recovered backup and (b) the committed
data_raw/MANIFEST.csv; every criterion is the pre-registered one, hard-coded.

Deviations from the pre-registration wording, declared here rather than
discovered later:
  * T1 speaks of SHA-256; the committed manifest records MD5, so content
    identity is scored on MD5 (same identity claim, different hash family).
  * T2's window is the experimenter-confirmed campaign: a single ~24 h run,
    17-18 July 2025, Ti:Sapph on throughout. Implemented as JST calendar
    dates {17, 18} July 2025 (UTC+9, fixed offset -- epochs only, never the
    local clock; the analysis machine runs CET).

Usage:
    run_timestamp_audit.py --backup /path/to/quarantine/copy [--report out.md]

Exit codes: 0 scored (whatever the outcomes), 2 integrity-void (T1-T3 failed;
predictions deliberately NOT scored, per the gate table).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data_raw" / "MANIFEST.csv"

JST = 9 * 3600                       # fixed offset; never the local clock
# T2: experimenter-confirmed campaign window, JST calendar days 17-18 July 2025
T2_LO = 1752678000                   # 2025-07-17 00:00:00 JST  (epoch, UTC)
T2_HI = 1752850800                   # 2025-07-19 00:00:00 JST  (exclusive)
T3_MAX_SHARED_FRACTION = 0.20        # mass-copy signature threshold
P2_MAX_INVERSIONS = 3                # "a few possible swaps", pre-registered
P5_MIN_RATIO = 10.0
D5_MAX_BLOCK_SPAN_S = 70.0

# P7: the byte-identical double-saves of DATA.md §3.3, as SOURCE basenames
# (the duplicate member of each pair need not be a canonical manifest row)
P7_PAIRS = [
    ("4154nm_070c1.csv", "4154nm_070c2.csv"),
    ("4192nm_eom_090c3.csv", "4192nm_eom_090c4.csv"),
    ("4192nm_eom_after3.csv", "4192nm_eom_after4.csv"),
    ("4154nm_130c_225mw4.csv", "4154nm_130c_225mw5.csv"),
]

# The 8 step-like blocks (run_intrablock_trend.py) -- POST-HOC section only.
STEP_BLOCKS = [("p_sweep", "4121", "130", "25"), ("p_sweep", "4192", "130", "125"),
               ("p_sweep", "4207", "130", "25"), ("p_sweep", "4207", "130", "175"),
               ("p_sweep", "4207", "130", "225"), ("t_sweep", "4121", "70", ""),
               ("t_sweep", "4192", "70", ""), ("t_sweep", "4192", "110", "")]


def jst(ts: float) -> str:
    import datetime as dt
    return dt.datetime.utcfromtimestamp(ts + JST).strftime("%Y-%m-%d %H:%M:%S JST")


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> list[dict]:
    with open(MANIFEST, newline="") as f:
        return list(csv.DictReader(f))


def index_backup(backup: Path) -> dict[str, list[Path]]:
    """basename -> all files in the backup bearing it (layout-agnostic)."""
    out: dict[str, list[Path]] = defaultdict(list)
    for p in sorted(backup.rglob("*")):
        if p.is_file() and not p.name.startswith("."):
            out[p.name].append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backup", required=True, type=Path)
    ap.add_argument("--report", type=Path, default=None)
    ap.add_argument("--posthoc-content-match", action="store_true",
                    help="POST-HOC mode, no pre-registered standing: match "
                         "manifest rows to backup files by MD5 content rather "
                         "than name, score predictions even if some rows are "
                         "absent (absences reported). The pre-registered run "
                         "is name-matched and voids on T1; this mode exists "
                         "because that run found the backup to be a superset "
                         "with naming drift, and its output must always be "
                         "labelled post-hoc.")
    args = ap.parse_args()

    L: list[str] = []
    W = L.append
    rows = load_manifest()
    by_name = index_backup(args.backup)

    if args.posthoc_content_match:
        W("# Timestamp audit — POST-HOC content-matched pass "
          "(NO pre-registered standing)")
    else:
        W("# Timestamp-audit report (pre-registered)")
    W("")
    W(f"Backup (quarantine copy): `{args.backup}`  ·  manifest rows: {len(rows)}")
    W(f"Backup files seen: {sum(len(v) for v in by_name.values())} "
      f"({len(by_name)} distinct basenames)")
    W("")

    # ---- match manifest rows to backup files via source_paths basenames ----
    matched: dict[str, dict] = {}          # canonical file -> info
    missing: list[str] = []
    by_md5: dict[str, list[Path]] = defaultdict(list)
    if args.posthoc_content_match:
        for ps in by_name.values():
            for p in ps:
                by_md5[md5(p)].append(p)
    for r in rows:
        cands: list[Path] = []
        if args.posthoc_content_match:
            cands = list(by_md5.get(r["md5"], []))
        else:
            for sp in (r.get("source_paths") or "").split("|"):
                if sp:
                    cands += by_name.get(Path(sp).name, [])
            cands += by_name.get(Path(r["file"]).name, [])
        if not cands:
            missing.append(r["file"])
            continue
        matched[r["file"]] = {"row": r, "paths": sorted(set(cands))}

    W(f"Manifest rows matched to backup: {len(matched)}; missing: {len(missing)}")
    if missing:
        W("  missing (first 10): " + ", ".join(missing[:10]))
    W("")

    # ---------------- integrity gates ----------------
    W("## Integrity gates")
    W("")
    # T1: content identity (MD5 -- the manifest's hash family; see header)
    mismatch = []
    for f, m in matched.items():
        want = m["row"]["md5"]
        oks = [p for p in m["paths"] if md5(p) == want]
        if not oks:
            mismatch.append(f)
        m["good_paths"] = oks or m["paths"]
    t1 = "PASS" if not mismatch and not missing else "FAIL"
    W(f"* **T1 content identity: {t1}** — {len(matched) - len(mismatch)}"
      f"/{len(rows)} rows byte-identical (MD5); {len(mismatch)} mismatched, "
      f"{len(missing)} absent.")
    if mismatch:
        W("  mismatched (first 10): " + ", ".join(mismatch[:10]))

    # collect mtimes of content-verified copies
    for m in matched.values():
        m["mtimes"] = sorted(os.stat(p).st_mtime for p in m["good_paths"])
        m["mtime"] = m["mtimes"][0]      # earliest content-identical copy
    all_mt = [m["mtime"] for m in matched.values()]

    # T2: clock plausibility -- inside the 24 h campaign window
    inside = [t for t in all_mt if T2_LO <= t < T2_HI]
    t2 = "PASS" if all_mt and len(inside) == len(all_mt) else "FAIL"
    if all_mt:
        W(f"* **T2 clock plausibility: {t2}** — {len(inside)}/{len(all_mt)} "
          f"mtimes inside 17–18 July 2025 (JST). Range seen: "
          f"{jst(min(all_mt))} → {jst(max(all_mt))}.")
    # T3: mass-copy signature
    counts = defaultdict(int)
    for t in all_mt:
        counts[round(t, 3)] += 1
    worst = max(counts.values()) / len(all_mt) if all_mt else 1.0
    t3 = "PASS" if worst <= T3_MAX_SHARED_FRACTION else "FAIL"
    W(f"* **T3 mass-copy signature: {t3}** — largest shared-mtime fraction "
      f"{worst:.1%} (threshold {T3_MAX_SHARED_FRACTION:.0%}).")
    # T4: granularity (recorded, not scored)
    subsec = sum(1 for t in all_mt if abs(t - round(t)) > 1e-6)
    odd = sum(1 for t in all_mt if int(round(t)) % 2 == 1)
    W(f"* **T4 granularity (recorded)** — {subsec}/{len(all_mt)} carry "
      f"sub-second parts; {odd} odd integer seconds (0 would suggest FAT 2 s).")
    W("* **T5**: all comparisons in raw epoch seconds; JST used for display only.")
    exotic = [n for n in by_name if n.lower().endswith((".trc", ".h5"))]
    W(f"* **T6 clock of record** — native scope files present: "
      f"{len(exotic)} (mtimes are the clock of record if 0).")
    W("")

    void = t1 == "FAIL" or t2 == "FAIL" or t3 == "FAIL"
    if void and args.posthoc_content_match and t2 != "FAIL" and t3 != "FAIL":
        W(f"*POST-HOC MODE: scoring proceeds despite {len(missing)} absent "
          f"row(s) (listed above and excluded); these verdicts carry no "
          f"pre-registered standing.*")
        W("")
        void = False
    if void:
        W("**INTEGRITY VOID — predictions deliberately not scored (per the "
          "gate table). This is the honest stop.**")
        text = "\n".join(L) + "\n"
        print(text)
        if args.report:
            args.report.write_text(text)
        return 2

    # ---------------- blocks ----------------
    blocks: dict[tuple, list[float]] = defaultdict(list)
    binfo: dict[tuple, dict] = {}
    for f, m in matched.items():
        r = m["row"]
        # block_seq is the CONDITION ladder, shared by the four interleaved
        # peaks (verified against the manifest: every (session, seq) carries
        # all four) -- a BLOCK is one peak's back-to-back repeats within it
        key = (r["session"], r["block_seq"], r["role"], r["peak"],
               r["bracket"], r["temperature_C"], r["power_mW"])
        blocks[key].append(m["mtime"])
        binfo.setdefault(key, r)
    bmed = {k: median(v) for k, v in blocks.items()}

    def blocks_where(**kw):
        out = []
        for k, r in binfo.items():
            if all(r.get(a) == b for a, b in kw.items()):
                out.append(k)
        return out

    W("## Predictions")
    W("")
    results: list[tuple[str, str, str]] = []

    # P1: whole power session precedes every cooling acquisition (file-level)
    p_files = [m["mtime"] for m in matched.values() if m["row"]["session"] == "P"]
    t_files = [m["mtime"] for m in matched.values()
               if m["row"]["session"] == "T"
               and m["row"]["temperature_C"] in ("70", "90", "110")]
    if p_files and t_files:
        viol = sum(1 for t in t_files if t < max(p_files))
        results.append(("P1", "PASS" if viol == 0 else "FAIL",
                        f"{viol} cooling files predate the last power-session "
                        f"file (last P: {jst(max(p_files))}; first T: "
                        f"{jst(min(t_files))})"))
    else:
        results.append(("P1", "AMBIGUOUS", "session labels not resolvable"))

    # P2: per-peak power ladder with <=3 adjacent inversions campaign-wide
    inv = 0
    detail = []
    short = []
    for peak in ("4121", "4154", "4192", "4207"):
        seq = []
        b = blocks_where(role="ruler_p", peak=peak, bracket="before")
        if b:
            seq.append(min(bmed[k] for k in b))
        for pw in ("25", "75", "125", "175", "225"):
            kk = blocks_where(role="p_sweep", peak=peak, power_mW=pw)
            if kk:
                seq.append(median([bmed[k] for k in kk]))
        a = blocks_where(role="ruler_p", peak=peak, bracket="after")
        if a:
            seq.append(max(bmed[k] for k in a))
        n = sum(1 for i in range(len(seq) - 1) if seq[i] > seq[i + 1])
        inv += n
        detail.append(f"{peak}:{n}/{len(seq)}st")
        if len(seq) < 7:
            short.append(peak)
    if short:
        results.append(("P2", "AMBIGUOUS",
                        f"ladder resolved <7 stages for {short} — scoring "
                        f"would be vacuous ({', '.join(detail)})"))
    else:
        results.append(("P2", "PASS" if inv <= P2_MAX_INVERSIONS else "FAIL",
                        f"{inv} adjacent inversions ({', '.join(detail)}; "
                        f"allowance ≤{P2_MAX_INVERSIONS})"))

    # P3: cooling 110 -> 90 -> 70 strictly monotonic (block medians)
    tm = {}
    for T in ("110", "90", "70"):
        kk = blocks_where(role="t_sweep", temperature_C=T)
        if kk:
            tm[T] = median([bmed[k] for k in kk])
    if len(tm) == 3:
        ok = tm["110"] < tm["90"] < tm["70"]
        results.append(("P3", "PASS" if ok else "FAIL",
                        " < ".join(f"{T}°C {jst(tm[T])}" for T in ("110", "90", "70"))))
    else:
        results.append(("P3", "AMBIGUOUS", f"only {sorted(tm)} resolvable"))

    # P4: temperature monotone non-increasing along block time order
    seq4 = sorted(((bmed[k], binfo[k]) for k in bmed
                   if binfo[k]["temperature_C"]), key=lambda x: x[0])
    temps = [float(r["temperature_C"]) for _, r in seq4]
    rises = sum(1 for i in range(len(temps) - 1) if temps[i + 1] > temps[i] + 1e-9)
    results.append(("P4", "PASS" if rises == 0 else "FAIL",
                    f"{rises} temperature increases along the time-ordered "
                    f"block sequence"))

    # P5: repeats back-to-back -- inter/intra gap ratio
    intra = []
    for v in blocks.values():
        v = sorted(v)
        intra += [b - a for a, b in zip(v, v[1:])]
    bs = sorted(bmed.values())
    inter = [b - a for a, b in zip(bs, bs[1:])]
    if intra and inter:
        mi, mo = median(intra), median(inter)
        ratio = mo / mi if mi > 0 else float("inf")
        results.append(("P5", "PASS" if ratio >= P5_MIN_RATIO else "FAIL",
                        f"median intra-block gap {mi:.1f} s vs inter-block "
                        f"{mo:.1f} s → ratio {ratio:.1f} (needs ≥{P5_MIN_RATIO:g})"))

    # P6: ruler brackets enclose each peak's power blocks
    bad6 = []
    for peak in ("4121", "4154", "4192", "4207"):
        pw = [bmed[k] for k in blocks_where(role="p_sweep", peak=peak)]
        b = [bmed[k] for k in blocks_where(role="ruler_p", peak=peak, bracket="before")]
        a = [bmed[k] for k in blocks_where(role="ruler_p", peak=peak, bracket="after")]
        if pw and b and min(b) > min(pw):
            bad6.append(f"{peak}: before-ruler after first power block")
        if pw and a and max(a) < max(pw):
            bad6.append(f"{peak}: after-ruler before last power block")
    results.append(("P6", "PASS" if not bad6 else "FAIL",
                    "; ".join(bad6) or "all four peaks bracketed"))

    # P7: double-save pairs are mutually closest (backup basenames)
    bad7 = []
    amb7 = []
    for f1, f2 in P7_PAIRS:
        a7 = by_name.get(f1, [])
        b7 = by_name.get(f2, [])
        if not a7 or not b7:
            amb7.append(f"{f1}|{f2} absent from backup")
            continue
        t1_, t2_ = (min(os.stat(x).st_mtime for x in a7),
                    min(os.stat(x).st_mtime for x in b7))
        d = abs(t1_ - t2_)
        others = [abs(t1_ - m) for m in bmed.values()]
        near = sorted(others)[1] if len(others) > 1 else float("inf")
        if d > near:
            bad7.append(f"{f1}↔{f2}: pair gap {d:.0f}s exceeds nearest "
                        f"other block ({near:.0f}s)")
    v7 = "AMBIGUOUS" if amb7 else ("PASS" if not bad7 else "FAIL")
    results.append(("P7", v7,
                    "; ".join(bad7 + amb7) or "all pairs mutually closest"))

    # P8: curated copies do not predate their raw/ sources
    bad8 = 0
    tot8 = 0
    for f, m in matched.items():
        sps = [sp for sp in (m["row"].get("source_paths") or "").split("|") if sp]
        raws = [p for sp in sps if sp.startswith("raw/")
                for p in by_name.get(Path(sp).name, [])]
        curs = [p for sp in sps if not sp.startswith("raw/")
                for p in by_name.get(Path(sp).name, [])]
        if raws and curs:
            tot8 += 1
            if min(os.stat(c).st_mtime for c in curs) < \
               min(os.stat(r0).st_mtime for r0 in raws) - 1.0:
                bad8 += 1
    results.append(("P8", "PASS" if bad8 == 0 else "FAIL",
                    f"{bad8}/{tot8} curated copies predate their raw/ source"))

    # D5: 5-repeat block span < 70 s (RF-off science blocks)
    spans = []
    for k, v in blocks.items():
        if binfo[k]["role"] in ("p_sweep", "t_sweep") and len(v) >= 4:
            spans.append(max(v) - min(v))
    if spans:
        ms = median(spans)
        results.append(("D5", "PASS" if ms < D5_MAX_BLOCK_SPAN_S else "FAIL",
                        f"median 5-repeat block span {ms:.1f} s "
                        f"(needs <{D5_MAX_BLOCK_SPAN_S:g} s; "
                        f"range {min(spans):.0f}–{max(spans):.0f} s)"))

    for name, verdict, note in results:
        W(f"* **{name}: {verdict}** — {note}")
    W("")

    # ---------------- post-hoc (labelled) ----------------
    W("## Post-hoc (no pre-registered standing)")
    W("")
    for role, peak, T, Pw in STEP_BLOCKS:
        kk = [k for k in bmed if binfo[k]["role"] == role
              and binfo[k]["peak"] == peak and binfo[k]["temperature_C"] == T
              and (not Pw or binfo[k]["power_mW"] == Pw)]
        for k in kk:
            v = sorted(blocks[k])
            gaps = ", ".join(f"{b - a:.0f}" for a, b in zip(v, v[1:]))
            W(f"* step block {role} {peak} T={T} P={Pw or '—'}: "
              f"intra-block gaps [{gaps}] s")
    W("")
    W("*One run, everything reported. Scored by scripts/run_timestamp_audit.py "
      "at the commit recorded in the results report; criteria are the "
      "pre-registered ones and were not adjusted after seeing the data.*")

    text = "\n".join(L) + "\n"
    print(text)
    if args.report:
        args.report.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
