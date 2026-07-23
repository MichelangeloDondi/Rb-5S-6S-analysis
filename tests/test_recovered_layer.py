"""Guards on data_recovered/ -- the backup-recovered layer.

The layer's contract: CLOCK.csv is the serialized acquisition clock
(hash -> mtime, manifest identity by content); RECOVERED_MANIFEST.csv maps
every published recovered file; nothing in the layer duplicates the frozen
archive, and identity is always by hash (nine recovered names collide with
different archive bytes).
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data_recovered"

# the audit's campaign window (T2): 2025-07-17 00:00 -> 2025-07-19 00:00 JST
T2_LO, T2_HI = 1752678000, 1752850800


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _clock():
    with open(BASE / "CLOCK.csv") as f:
        return list(csv.DictReader(f))


def test_clock_matches_the_manifest_by_content():
    """Every manifest identity CLOCK.csv asserts must agree with
    data_raw/MANIFEST.csv on the md5 -- the clock may never re-identify a
    file by name."""
    man = {r["file"]: r["md5"] for r in
           csv.DictReader(open(ROOT / "data_raw" / "MANIFEST.csv"))}
    rows = _clock()
    named = [r for r in rows if r["manifest_file"]]
    assert len(named) >= 297, f"only {len(named)} manifest-matched clock rows"
    bad = [r["path"] for r in named
           if man.get(r["manifest_file"]) != r["md5"]]
    assert not bad, f"clock rows whose md5 disagrees with the manifest: {bad[:5]}"


def test_clock_campaign_rows_sit_inside_the_audit_window():
    """Main-source rows with a manifest identity are campaign acquisitions;
    their mtimes must fall inside the pre-registered T2 window, as the audit
    established. A row outside it means the table was rebuilt from a
    corrupted or re-copied source."""
    rows = [r for r in _clock()
            if r["source"] == "main" and r["manifest_file"]]
    out = [r["path"] for r in rows
           if not (T2_LO <= int(r["mtime_epoch"]) <= T2_HI)]
    assert not out, f"campaign clock rows outside the T2 window: {out[:5]}"


def test_clock_is_sorted_and_unique():
    rows = _clock()
    keys = [(r["source"], r["path"]) for r in rows]
    assert keys == sorted(keys), "CLOCK.csv is not deterministically sorted"
    assert len(keys) == len(set(keys)), "duplicate (source, path) rows"


def test_recovered_files_match_their_manifest_and_stay_out_of_the_archive():
    """Every published recovered file: exists, hashes to its recorded md5
    (and to the __hash suffix in its own name), and its content is ABSENT
    from data_raw/MANIFEST.csv -- the layer holds only what the frozen
    archive does not."""
    archive = {r["md5"] for r in
               csv.DictReader(open(ROOT / "data_raw" / "MANIFEST.csv"))}
    rows = list(csv.DictReader(open(BASE / "RECOVERED_MANIFEST.csv")))
    assert len(rows) == 20, f"expected 20 recovered files, got {len(rows)}"
    for r in rows:
        p = BASE / r["file"]
        assert p.is_file(), f"missing: {r['file']}"
        d = _md5(p)
        assert d == r["md5"], f"{r['file']}: content changed"
        assert d.startswith(p.stem.rsplit("__", 1)[1]), (
            f"{r['file']}: name-suffix does not match content hash")
        assert d not in archive, (
            f"{r['file']}: duplicates the frozen archive -- does not belong here")


def test_every_recovered_file_has_a_clock_row():
    """Time lives in CLOCK.csv, content in the layer: each recovered file's
    hash must appear in the clock so it is datable."""
    clock_md5 = {r["md5"] for r in _clock()}
    rows = list(csv.DictReader(open(BASE / "RECOVERED_MANIFEST.csv")))
    missing = [r["file"] for r in rows if r["md5"] not in clock_md5]
    assert not missing, f"recovered files with no clock row: {missing}"
