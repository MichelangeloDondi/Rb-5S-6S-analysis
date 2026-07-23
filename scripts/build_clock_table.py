#!/usr/bin/env python3
"""
Build data_recovered/CLOCK.csv — the acquisition clock, committed as data.

The 2025 archive was assembled without timestamps; a backup carrying FAT
mtimes surfaced 2026-07-22 and its quarantined copies are the only clock the
campaign has (results report, addenda 1-9). This script serialises that clock
so the repository no longer depends on a private folder: every quarantined
file's content hash, source tree, mtime, and — where the content matches the
frozen archive — its manifest identity.

Columns: source, path, md5, mtime_epoch, manifest_file
  source        main | rawdata2 | pilot | prehistory
  path          file path inside that source tree
  md5           content hash (identity is ALWAYS by hash, never by name —
                nine backup names collide with different archive bytes)
  mtime_epoch   integer epoch seconds (FAT granularity is 2 s; the campaign
                medium's fingerprint). Interpret in JST (UTC+9) for
                acquisition-local wall time.
  manifest_file the data_raw/MANIFEST.csv `file` whose md5 matches, else ""

Deterministic: rows sorted by (source, path); regeneration from the
quarantines is byte-stable. Consumers: scripts/run_drift_settling.py (which
prefers this table and falls back to hashing a live quarantine), and the
guard tests/test_recovered_layer.py.

Requires the quarantine copies (private, read-only). Without them the
committed CLOCK.csv is the record; this script is how it was made and how it
is verified.
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES = {
    "main": "~/Documents/RawDataBackUp_QUARANTINE_2026-07-23",
    "rawdata2": "~/Documents/RawData2_QUARANTINE_2026-07-24",
    "pilot": "~/Documents/RawDataPilot_QUARANTINE_2026-07-24",
    "prehistory": "~/Documents/RawDataPrehistory_QUARANTINE_2026-07-24",
}


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    missing = [k for k, v in SOURCES.items()
               if not Path(os.path.expanduser(v)).is_dir()]
    if missing:
        print(f"quarantine(s) not on this machine: {missing} -- the committed "
              f"CLOCK.csv is the record; nothing to do.")
        return 0

    by_md5 = {}
    with open(ROOT / "data_raw" / "MANIFEST.csv") as f:
        for r in csv.DictReader(f):
            by_md5[r["md5"]] = r["file"]

    rows = []
    for source, base in SOURCES.items():
        basep = Path(os.path.expanduser(base))
        for p in sorted(basep.rglob("*")):
            if not p.is_file():
                continue
            d = _md5(p)
            rows.append(dict(
                source=source,
                path=str(p.relative_to(basep)),
                md5=d,
                mtime_epoch=int(p.stat().st_mtime),
                manifest_file=by_md5.get(d, ""),
            ))
    rows.sort(key=lambda r: (r["source"], r["path"]))

    out = ROOT / "data_recovered" / "CLOCK.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "path", "md5",
                                          "mtime_epoch", "manifest_file"])
        w.writeheader()
        w.writerows(rows)
    matched = sum(1 for r in rows if r["manifest_file"])
    print(f"wrote {out.relative_to(ROOT)}: {len(rows)} rows "
          f"({matched} manifest-matched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
