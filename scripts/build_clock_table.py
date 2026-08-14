#!/usr/bin/env python3
"""
Build data_recovered/CLOCK.csv — the acquisition clock, committed as data.

The 2025 archive was assembled without timestamps; a backup carrying FAT
mtimes surfaced 2026-07-22 and its excluded copies are the only clock the
campaign has (results report, addenda 1-9). This script serialises that clock
so the repository no longer depends on a private folder: every excluded
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
outside session trees is byte-stable. Consumers: scripts/run_drift_settling.py (which
prefers this table and falls back to hashing a live excluded), and the
guard tests/test_recovered_layer.py.

Requires the excluded copies (private, read-only). Without them the
committed CLOCK.csv is the record; this script is how it was made and how it
is verified. The four RB5S6S_*_DIR environment variables below are needed only
to re-run this script against those private working copies, and the committed
CSVs are what the repository ships.
"""

from __future__ import annotations

import csv
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES = {
    "main": Path(os.environ.get(
        "RB5S6S_BACKUP_DIR", "~/rb-2025-sessions/backup")).expanduser(),
    "rawdata2": Path(os.environ.get(
        "RB5S6S_RAWDATA2_DIR", "~/rb-2025-sessions/rawdata2")).expanduser(),
    "pilot": Path(os.environ.get(
        "RB5S6S_SESSION_20250717_DIR", "~/rb-2025-sessions/pilot")).expanduser(),
    "prehistory": Path(os.environ.get(
        "RB5S6S_SESSION_20250704_DIR", "~/rb-2025-sessions/prehistory")).expanduser(),
}


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    missing = [k for k, v in SOURCES.items() if not v.is_dir()]
    if missing:
        print(f"excluded(s) not on this machine: {missing} -- the committed "
              f"CLOCK.csv is the record; nothing to do.")
        return 0

    by_md5 = {}
    with open(ROOT / "data_raw" / "MANIFEST.csv") as f:
        for r in csv.DictReader(f):
            by_md5[r["md5"]] = r["file"]

    rows = []
    for source, basep in SOURCES.items():
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
