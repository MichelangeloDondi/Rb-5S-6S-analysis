#!/usr/bin/env python3
"""
Publish the backup-recovered files into data_recovered/ (addenda 3, 8).

Two groups, from the quarantined backup copies:

  discarded_backup/       the 16 discarded acquisitions that survive only in
                          the backup (results report, addendum 3) -- the
                          evidence behind the curation test.
  lineage_4192nm_225mw1/  the four variants of the archive's one degraded
                          trace, whose dated chain addendum 8 closed:
                          pristine original, headerless degraded re-export,
                          header-restored intermediate (RawData2), and the
                          analysed bytes are the intermediate modulo CRLF.

Filenames carry an __<md5-8> suffix because NINE of the original names
collide with different bytes in data_raw/ -- the collision that hid a
re-take series until content hashing exposed it. Match by hash, never by
name; RECOVERED_MANIFEST.csv maps both.

data_raw/ itself stays byte-frozen; this is a separate, labelled layer.
Requires the quarantines; without them the committed tree is the record.
"""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QMAIN = Path(os.path.expanduser("~/Documents/RawDataBackUp_QUARANTINE_2026-07-23"))
QR2 = Path(os.path.expanduser("~/Documents/RawData2_QUARANTINE_2026-07-24"))
VARIANT_STEM = "4192nm_225mw1"


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not (QMAIN.is_dir() and QR2.is_dir()):
        print("quarantines not on this machine -- the committed tree is the "
              "record; nothing to do.")
        return 0

    known = {r["md5"] for r in csv.DictReader(open(ROOT / "data_raw" / "MANIFEST.csv"))}
    uniq_main = [p for p in sorted(QMAIN.glob("*.csv")) if _md5(p) not in known]
    variants = [p for p in uniq_main if p.stem.startswith(VARIANT_STEM)]
    discards = [p for p in uniq_main if not p.stem.startswith(VARIANT_STEM)]
    r2_new = [p for p in sorted(QR2.glob("*.csv"))
              if _md5(p) not in known
              and _md5(p) not in {_md5(q) for q in uniq_main}]
    assert len(discards) == 16, f"expected 16 backup discards, got {len(discards)}"
    assert len(variants) == 3 and len(r2_new) == 1, (len(variants), len(r2_new))

    base = ROOT / "data_recovered"
    rows = []

    def place(src: Path, sub: str, role: str, source: str):
        d = _md5(src)
        dest = base / sub / f"{src.stem}__{d[:8]}{src.suffix}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)          # content only; the CLOCK carries time
        rows.append(dict(file=f"{sub}/{dest.name}", original_name=src.name,
                         source=source, role=role, md5=d,
                         bytes=dest.stat().st_size))

    for p in discards:
        place(p, "discarded_backup", "discarded acquisition", "main backup")
    for p in variants:
        place(p, "lineage_4192nm_225mw1",
              "pristine original" if p.name == f"{VARIANT_STEM}.csv"
              else "degraded re-export", "main backup")
    place(r2_new[0], "lineage_4192nm_225mw1",
          "header-restored intermediate (analysed bytes modulo CRLF)", "RawData2")

    rows.sort(key=lambda r: r["file"])
    with open(base / "RECOVERED_MANIFEST.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "original_name", "source",
                                          "role", "md5", "bytes"])
        w.writeheader()
        w.writerows(rows)
    print(f"placed {len(rows)} files + RECOVERED_MANIFEST.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
