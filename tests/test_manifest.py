"""
Integrity tests of the frozen dataset (data_raw/ + MANIFEST.csv).

These certify that the dataset committed to git is exactly the one decoded and
imported on 2026-07-11 (full story: docs/DATA.md): every unique trace present
and byte-identical (MD5), correctly role-classified, with the known archive
anomalies pinned so they can never silently change. Because data_raw/ ships in
the repository, a green CI run certifies code AND dataset together.
"""

import csv
import hashlib
from collections import Counter

import pytest

from rb5s6s.config import DATA_RAW_DIR, MANIFEST_CSV

# The census established at import time (2026-07-11). If this ever changes,
# someone touched the frozen dataset — that must be a deliberate, documented
# act, not an accident.
EXPECTED_CENSUS = {
    ("p_sweep", "canonical"): 100,       # 4 peaks x 5 powers x 5 repeats
    ("p_sweep", "discarded"): 1,         # shot rejected by the experimenter at curation (4207, 25 mW)
    ("t_sweep", "canonical"): 59,        # 4 x {70,90,110} x 5, minus the 4154@70C double-save
    ("t_sweep", "discarded"): 3,         # shots rejected at curation ("seemed quite bad")
    ("ruler_t", "canonical"): 61,        # per-T ruler blocks (4192@90C block has a double-save)
    ("ruler_p", "canonical"): 44,        # before/after bracket blocks (4154: underscore set)
    ("quarantine", "quarantined"): 29,   # aborted 4154 power attempt + its plausible rulers
}
EXPECTED_TOTAL = 297


@pytest.fixture(scope="module")
def rows():
    with open(MANIFEST_CSV, newline="") as f:
        return list(csv.DictReader(f))


def test_total_row_count(rows):
    assert len(rows) == EXPECTED_TOTAL


def test_paths_and_hashes_unique(rows):
    paths = [r["file"] for r in rows]
    hashes = [r["md5"] for r in rows]
    assert len(set(paths)) == len(paths), "duplicate file path in manifest"
    assert len(set(hashes)) == len(hashes), "duplicate MD5 — dedupe failed"


def test_every_file_present_and_bitexact(rows):
    # Full re-hash of the dataset (~16 MB): the strongest statement CI can
    # make that the frozen data has not rotted or been edited.
    bad = []
    for r in rows:
        p = DATA_RAW_DIR / r["file"]
        if not p.is_file():
            bad.append(f"missing: {r['file']}")
        elif hashlib.md5(p.read_bytes()).hexdigest() != r["md5"]:
            bad.append(f"hash mismatch: {r['file']}")
    assert not bad, bad


def test_role_flag_census(rows):
    census = Counter((r["role"], r["flag"]) for r in rows)
    assert dict(census) == EXPECTED_CENSUS


def test_t130_identity(rows):
    # The temperature sweep's 130 C point IS the power sweep's 225 mW point:
    # exactly 20 rows (4 peaks x 5 repeats), each hash-shared with a '130c'
    # filename in the original archive.
    t130 = [r for r in rows if r["serves_t130"] == "True"]
    assert len(t130) == 20
    assert all(r["role"] == "p_sweep" and r["power_mW"] == "225" for r in t130)
    assert all("130c" in r["source_paths"] for r in t130)


def test_known_double_saves_pinned(rows):
    # Same-bytes-two-names pairs inside the ORIGINAL curated dirs. Their
    # merged manifest rows must keep both source names — this is the guard
    # against pseudo-replication (never count repeats by filename!).
    def sources_of(file_end):
        for r in rows:
            if r["file"].endswith(file_end):
                return r["source_paths"]
        raise AssertionError(f"row not found: {file_end}")

    s = sources_of("t_sweep/4154nm_070c1.csv")
    assert "temperature/4154nm_070c1.csv" in s and "temperature/4154nm_070c2.csv" in s

    s = sources_of("rulers_t/4192nm_eom_090c3.csv")
    assert "4192nm_eom_090c3.csv" in s and "4192nm_eom_090c4.csv" in s

    s = sources_of("rulers_p/4192nm_eom_after3.csv")
    assert "4192nm_eom_after3.csv" in s and "4192nm_eom_after4.csv" in s


def test_canonical_grid_completeness(rows):
    # Every canonical condition has 5 unique repeats, EXCEPT 4154@70C which
    # has 4 (documented double-save; a 5th distinct acquisition exists as
    # flag=extra_uncurated pending QC).
    t = Counter((r["peak"], r["temperature_C"]) for r in rows
                if r["role"] == "t_sweep" and r["flag"] == "canonical")
    for (peak, temp), n in t.items():
        expected = 4 if (peak, temp) == ("4154", "70") else 5
        assert n == expected, f"t_sweep {peak}@{temp}C: {n} repeats"
    p = Counter((r["peak"], r["power_mW"]) for r in rows
                if r["role"] == "p_sweep" and r["flag"] == "canonical")
    assert all(n == 5 for n in p.values())
    assert len(p) == 20  # 4 peaks x 5 powers


def test_flags_match_folders(rows):
    # Physical separation mirrors the flag: rejected data cannot sit inside
    # the canonical role folders where a loop over files might pick it up.
    role_dirs = {"t_sweep": "t_sweep", "p_sweep": "p_sweep",
                 "ruler_t": "rulers_t", "ruler_p": "rulers_p",
                 "quarantine": "quarantine", "review": "review"}
    for r in rows:
        top = r["file"].split("/")[0]
        if r["flag"] == "quarantined":
            assert top == "quarantine", r["file"]
        elif r["flag"] == "discarded":
            assert top == "discarded", r["file"]
        else:
            assert top == role_dirs[r["role"]], r["file"]


def test_nothing_needs_review(rows):
    assert not [r for r in rows if r["flag"] == "review"]
