"""
Guards on the MANIFEST.csv `qc_reason` provenance column (audit commission,
2026-07-12): every excluded trace carries its recorded reason; the reasons
match the committed curation audit; and the quarantine's "individually clean"
claim stays TRUE against the actual data (the session-grain fact that makes
the recorded reason -- not a recomputed flag -- the only possible provenance).
"""

from __future__ import annotations

import csv

from rb5s6s.config import MANIFEST_CSV
from rb5s6s.ingest import load_manifest, load_trace, trace_path
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags


def _rows():
    return list(csv.DictReader(open(MANIFEST_CSV)))


def test_qc_reason_column_complete_and_consistent():
    rows = _rows()
    assert len(rows) == 297
    assert "qc_reason" in rows[0]
    flags = {"canonical": 0, "quarantined": 0, "discarded": 0}
    for r in rows:
        flags[r["flag"]] += 1
        if r["flag"] == "canonical":
            assert r["qc_reason"] == "", r["file"]
        else:
            assert r["qc_reason"].strip(), f"missing reason: {r['file']}"
    assert flags == {"canonical": 264, "quarantined": 29, "discarded": 4}


def test_discard_reasons_match_curation_audit():
    rows = {r["file"].split("/")[-1]: r for r in _rows() if r["flag"] == "discarded"}
    assert rows["4154nm_070c4.csv"]["qc_reason"].startswith("curation discard: ~27% dimmer")
    assert "supernumerary" in rows["4192nm_090c3.csv"]["qc_reason"]
    assert "superseded by canonical" in rows["4207nm_025mw2.csv"]["qc_reason"]
    assert "block-wide" in rows["4207nm_070c2.csv"]["qc_reason"]


def test_quarantine_reasons_are_session_grain():
    q = [r for r in _rows() if r["flag"] == "quarantined"]
    assert len(q) == 29
    rulers = [r for r in q if "eom" in r["file"]]
    powers = [r for r in q if "eom" not in r["file"]]
    assert len(rulers) == 10 and len(powers) == 19
    assert all(r["qc_reason"].startswith("session quarantine: EOM ruler") for r in rulers)
    assert all(r["qc_reason"].startswith("session quarantine: aborted") for r in powers)


def test_quarantined_traces_really_are_individually_clean():
    # The recorded reason asserts "trace individually clean (no hard flags)".
    # Pin that against the data on a sample of both kinds, so the manifest can
    # never silently claim a cleanliness the QC would contradict.
    rows = load_manifest()
    q = [r for r in rows if r["flag"] == "quarantined"]
    sample = ([r for r in q if "eom" in r["file"]][:2]
              + [r for r in q if "eom" not in r["file"]][:3])
    for r in sample:
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        hf = hard_flags(m, rf_on=(r["rf_on"] == "True")) + ingest_flags(info)
        assert hf == [], (r["file"], hf)
