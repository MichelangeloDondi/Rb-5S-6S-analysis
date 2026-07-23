#!/usr/bin/env python3
"""
One-time (idempotent) import of the 2025 archival CSVs into data_raw/.
=======================================================================

WHY THIS SCRIPT EXISTS
----------------------
The original archive (old repo, ``Rb-5S-to-6S-broadening/data/``) holds 722
CSVs that are ~2x duplicated across six directories, with three structural
facts that were only decoded on 2026-07-11 (hash comparison + experimenter
answers; full story in docs/DATA.md):

1. The RF-off "130 °C" temperature-sweep files are byte-identical renames of
   the 225 mW power-sweep files (the power session ran at 130 °C, and that
   condition serves both sweeps).
2. The oversampled ``*_eom_130c{1..12}`` ruler files are byte-identical
   renames of the per-peak ``eom_after{...}`` + ``eom_before{...}`` bracket
   rulers of the power session (in that order).
3. Two pairs of files are literal double-saves (identical bytes, both names
   kept): ``4192nm_eom_after3/4`` and ``raw/4154nm_130c_225mw4/5``.

This script therefore deduplicates BY MD5 (never by filename), classifies
each unique trace into a role, copies it once into ``data_raw/<role>/``, and
writes ``data_raw/MANIFEST.csv`` — one row per unique trace with role,
condition, chronology, flags, hash, and every original path it came from.
After this runs once, the new repository is fully self-contained.

NOTE: after any regeneration, run ``scripts/annotate_manifest_qc.py`` to
restore the ``qc_reason`` provenance column (the recorded per-trace exclusion
reason for every non-canonical row — audit commission 2026-07-12; the reasons
are curation facts, deliberately not recomputable from the data alone).

QUARANTINE (pre-registered, never entered in headline fits)
-----------------------------------------------------------
* ``raw/4154nm_130c_{025,125,225}mw*`` — an aborted first attempt at the power
  sweep; the experimenter does not remember why it was stopped and flags it
  as suspicious (2026-07-11).
* ``4154nm_eom_before{1..5}`` / ``4154nm_eom_after{1..5}`` (NON-underscore) —
  4154 is the only peak with two bracket sets; the underscore re-take is the
  one that was pooled into the canonical ruler set, so the non-underscore set
  is plausibly the aborted attempt's ruler and is held out with it.

FLAGS
-----
* ``canonical``   — the curated measurement set (the experimenter's selection)
* ``discarded``   — exists only in the old ``raw/`` dump because the
                    experimenter discarded it at curation time ("seemed quite
                    bad", statement 2026-07-11) and renumbered the keepers —
                    which is also why raw/'s indices are shifted vs the
                    curated dirs. Stored under ``data_raw/discarded/``; NEVER
                    enters a headline fit. The M0 objective QC runs on these
                    only as a consistency check on the curation (appendix).
* ``quarantined`` — see above
* ``review``      — did not match any known naming pattern; needs a human

CHRONOLOGY ENCODING
-------------------
``session`` ('P' or 'T') and ``block_seq`` label the CONDITION LADDER:
before=0, powers=1..5 by ASCENDING POWER, after=6; T: 110=1, 90=2, 70=3.

*** block_seq IS NOT AN ACQUISITION ORDER (corrected 2026-07-23). *** It was
assigned in 2026-07-11 from a recollection that the power session ran
25 -> 225 mW. The recovered acquisition timestamps prove the ladder ran
DESCENDING -- before-rulers -> 225 -> 175 -> 125 -> 75 -> 25 mW ->
after-rulers -- so for the power session block_seq counts BACKWARDS in time
(block_seq 5 = 225 mW ran FIRST). The values are deliberately left as they
are: they are a stable join key, the manifest's md5s are computed over them,
and no analysis consumes block_seq as a time proxy (verified: it appears only
here and in run_timestamp_audit.py, which keys blocks by it without ordering
them). Anything that DOES need acquisition order must take it from the
recovered timestamps -- docs/PREREGISTRATION_RESULTS.md.

The temperature session's 110 -> 90 -> 70 ordering IS the true time order
(audit prediction P3, PASS).

Repeat indices are chronological within a block (audit P5: repeats a median
8 s apart, vs 383 s between blocks). The order of the four peaks within the
power session, previously OPEN, is now known from the timestamps:
4192 -> 4207 -> 4154 -> 4121, overnight 17->18 July 2025 JST.

Usage:  python scripts/import_data.py          (reads rb5s6s.config paths)
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# Allow running as a plain script from the repo root without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s.config import ARCHIVE_SOURCE_DIR, DATA_RAW_DIR, MANIFEST_CSV  # noqa: E402

# Filename grammar of the whole archive:  <peak>nm_<rest><index>.csv
# e.g. 4154nm_110c3.csv / 4207nm_eom_before2.csv / 4154nm_eom_before_7.csv /
#      4154nm_130c_125mw8.csv.  Lazy <rest> + greedy trailing digits handles
# two-digit indices (…130c10.csv -> rest='eom_130c', idx=10) correctly.
NAME_RE = re.compile(r"^(?P<peak>4121|4154|4192|4207)nm_(?P<rest>.+?)(?P<idx>\d+)\.csv$")

ROLE_DIRS = {
    "t_sweep": "t_sweep",
    "p_sweep": "p_sweep",
    "ruler_t": "rulers_t",
    "ruler_p": "rulers_p",
    "quarantine": "quarantine",
    "review": "review",
}

# Preference score for choosing the CANONICAL name of a hash-duplicate group.
# Lower = preferred. Rationale:
#  - bracket names (eom_before/after) beat their pooled 'eom_130c' renames;
#  - '225mw' beats its '130c' rename (the power grid is the primary role);
#  - curated directories beat the raw/ dump;
#  - alphabetical last, so ties (e.g. double-saves) resolve deterministically.
_DIR_RANK = {
    "power copy": -25,
    "temperature": -24,
    "temperature_EOM": -23,
    "power_eom": -22,
    "power": -10,
    "raw": 0,
}


def _pref_key(path: Path):
    name = path.name
    score = 0
    if "eom_before" in name or "eom_after" in name:
        score -= 40
    if re.search(r"nm_\d{3}mw\d+\.csv$", name):
        # plain power names like 4154nm_225mw3.csv (the combined 130c_XXXmw
        # quarantine names have 'nm_130c_' in between and do not match)
        score -= 30
    score += _DIR_RANK.get(path.parent.name, 0)
    return (score, name)


def classify(peak: str, rest: str):
    """Map a canonical filename's <rest> to (role, fields...).

    Returns dict with: role, temperature_C, power_mW, rf_on, bracket,
    session, block_seq.  Raises nothing: unknown patterns get role='review'.
    """
    d = {
        "role": "review", "temperature_C": "", "power_mW": "", "rf_on": False,
        "bracket": "", "session": "", "block_seq": "",
    }
    m = re.fullmatch(r"(070|090|110)c", rest)
    if m:
        t = int(m.group(1))
        d.update(role="t_sweep", temperature_C=t, session="T",
                 block_seq={110: 1, 90: 2, 70: 3}[t])
        return d
    m = re.fullmatch(r"(025|075|125|175|225)mw", rest)
    if m:
        p = int(m.group(1))
        d.update(role="p_sweep", temperature_C=130, power_mW=p, session="P",
                 block_seq={25: 1, 75: 2, 125: 3, 175: 4, 225: 5}[p])
        return d
    m = re.fullmatch(r"eom_(070|090|110)c", rest)
    if m:
        t = int(m.group(1))
        d.update(role="ruler_t", temperature_C=t, rf_on=True, session="T",
                 block_seq={110: 1, 90: 2, 70: 3}[t])
        return d
    m = re.fullmatch(r"eom_(before|after)(_?)", rest)
    if m:
        bracket, underscore = m.group(1), m.group(2)
        # 4154 has two bracket sets; the NON-underscore one is quarantined
        # (plausibly belongs to the aborted power attempt — see module docstring).
        role = "quarantine" if (peak == "4154" and underscore == "") else "ruler_p"
        d.update(role=role, temperature_C=130, rf_on=True, bracket=bracket,
                 session="P" if role == "ruler_p" else "Q",
                 block_seq={"before": 0, "after": 6}[bracket] if role == "ruler_p" else "")
        return d
    m = re.fullmatch(r"130c_(025|125|225)mw", rest)
    if m:
        d.update(role="quarantine", temperature_C=130, power_mW=int(m.group(1)),
                 session="Q")
        return d
    if rest == "eom_130c":
        # Only reachable if an eom_130c file failed to hash-match a bracket
        # file (should not happen; decoded 2026-07-11). Send to review.
        d.update(role="review", temperature_C=130, rf_on=True)
        return d
    if rest == "130c":
        # Only reachable if a 130c file failed to hash-match a 225mw file.
        d.update(role="review", temperature_C=130)
        return d
    return d


def main() -> int:
    src = ARCHIVE_SOURCE_DIR
    if not src.is_dir():
        print(f"ERROR: archive source not found: {src}\n"
              "(This script only runs on the machine holding the old repo; "
              "everyone else already has data_raw/ in git.)")
        return 1

    # ---- 1. hash every CSV in the old archive --------------------------------
    all_csvs = sorted(src.rglob("*.csv"))
    by_hash = defaultdict(list)
    for p in all_csvs:
        h = hashlib.md5(p.read_bytes()).hexdigest()
        by_hash[h].append(p)
    print(f"scanned {len(all_csvs)} CSVs -> {len(by_hash)} unique by MD5")

    # ---- 2. choose canonical name per unique trace, classify, copy ----------
    DATA_RAW_DIR.mkdir(exist_ok=True)
    rows = []
    counts = defaultdict(int)
    claimed = {}  # dest path -> md5; guards against filename collisions:
    # the raw/ dump's repeat numbering is SHIFTED vs the curated dirs for a
    # few stems, so a raw-only trace (different bytes) can carry the same
    # (peak, condition, index) name as a curated trace. Such traces get a
    # deterministic '__altN' suffix; the manifest 'file' column is always
    # the actual on-disk path, so downstream code never needs to know.
    for h, paths in sorted(by_hash.items(), key=lambda kv: _pref_key(sorted(kv[1], key=_pref_key)[0])):
        canon = sorted(paths, key=_pref_key)[0]
        m = NAME_RE.match(canon.name)
        if not m:
            info = {"role": "review", "temperature_C": "", "power_mW": "",
                    "rf_on": False, "bracket": "", "session": "", "block_seq": ""}
            peak, idx = "", ""
        else:
            peak, rest, idx = m.group("peak"), m.group("rest"), int(m.group("idx"))
            info = classify(peak, rest)

        # discarded: the trace exists ONLY in the raw/ dump — the experimenter
        # rejected it at curation time (see module docstring, FLAGS).
        curated = any(p.parent.name != "raw" for p in paths)
        if info["role"] in ("t_sweep", "p_sweep", "ruler_t", "ruler_p") and not curated:
            flag = "discarded"
        elif info["role"] == "quarantine":
            flag = "quarantined"
        elif info["role"] == "review":
            flag = "review"
        else:
            flag = "canonical"

        dest_dir = DATA_RAW_DIR / ("discarded" if flag == "discarded"
                                   else ROLE_DIRS[info["role"]])
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / canon.name
        k = 0
        while str(dest) in claimed and claimed[str(dest)] != h:
            k += 1
            dest = dest_dir / f"{canon.stem}__alt{k}{canon.suffix}"
        claimed[str(dest)] = h
        if dest.exists():
            if hashlib.md5(dest.read_bytes()).hexdigest() != h:
                raise RuntimeError(
                    f"stale file with wrong content at {dest}; "
                    "delete data_raw/ subfolders and re-run for a clean rebuild"
                )
        else:
            shutil.copy2(canon, dest)

        rows.append({
            "file": str(dest.relative_to(DATA_RAW_DIR)),
            "md5": h,
            "role": info["role"],
            "peak": peak,
            "temperature_C": info["temperature_C"],
            "power_mW": info["power_mW"],
            "rf_on": info["rf_on"],
            "bracket": info["bracket"],
            "repeat_idx": idx,
            "serves_t130": info["role"] == "p_sweep" and info["power_mW"] == 225,
            "flag": flag,
            "session": info["session"],
            "block_seq": info["block_seq"],
            "n_source_copies": len(paths),
            "source_paths": "|".join(str(p.relative_to(src)) for p in sorted(paths)),
        })
        counts[(info["role"], flag)] += 1

    # ---- 3. write the manifest ------------------------------------------------
    rows.sort(key=lambda r: (r["role"], r["peak"], str(r["temperature_C"]),
                             str(r["power_mW"]), r["bracket"], r["repeat_idx"]))
    fieldnames = list(rows[0].keys())
    with open(MANIFEST_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # ---- 4. report -------------------------------------------------------------
    print(f"\nwrote {MANIFEST_CSV} with {len(rows)} unique traces:")
    for (role, flag), n in sorted(counts.items()):
        print(f"   {role:12s} {flag:16s} {n:4d}")
    review = [r for r in rows if r["flag"] == "review"]
    if review:
        print("\nFILES NEEDING HUMAN REVIEW:")
        for r in review:
            print(f"   {r['file']}  <- {r['source_paths']}")
    # Design-grid sanity: the canonical grid the analysis expects.
    # t_sweep is 59, not 60: the curated archive double-saved one 4154@70C
    # repeat (two filenames, identical bytes), so that condition has only 4
    # unique curated repeats (a distinct 5th shot exists but was discarded by
    # the experimenter => that condition runs on N=4). Documented in
    # docs/DATA.md; statistics must always count manifest rows, never files.
    expect = {
        ("t_sweep", "canonical"): 59,    # 4 peaks x {70,90,110} x 5 repeats, minus the 4154@70C double-save
        ("p_sweep", "canonical"): 100,   # 4 peaks x 5 powers x 5 repeats
    }
    ok = True
    for k, n in expect.items():
        if counts.get(k, 0) != n:
            print(f"WARNING: expected {n} for {k}, found {counts.get(k, 0)}")
            ok = False
    print("\ndesign-grid check:", "OK" if ok else "MISMATCH (see warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
