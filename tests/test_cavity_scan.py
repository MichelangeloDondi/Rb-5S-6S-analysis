"""
The 2025-06-12 cavity-scan reading (rb5s6s/cavity_scan.py).

Three layers. A synthetic closure: plant spikes of known area on a planted
triangular ramp and check the finder, the flank-fit apex and the pairing
recover what was planted. The real record: the committed digitisation must
keep giving the eight-spike mirror-pair reading and the two quoted ratios.
Freshness: `results/cavity_scan_integrals.csv` and the APPARATUS.md sec. 6
paragraph must both match what the current code computes, so neither can go
stale against a rule change silently (the pre-2026-08-05 state of that
paragraph -- integrals quoted with no committed procedure -- is what this
module exists to end).
"""

from __future__ import annotations

import csv

import numpy as np
import pytest

from rb5s6s import cavity_scan as cs
from rb5s6s import config as C


# ---------------------------------------------------------------------------
# synthetic closure
# ---------------------------------------------------------------------------

def _synthetic_record(apex=2.55, seed=7):
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 5.0, 700)
    ch1 = np.where(t < apex, 0.3 + 2.5 * t, 0.3 + 2.5 * apex - 2.6 * (t - apex))
    ch1 = ch1 + rng.normal(0.0, 0.01, t.size)
    ch2 = 0.95 + rng.normal(0.0, 0.01, t.size)
    # four mirror pairs about the apex, heights well above 5 MAD; the outermost
    # pair stays clear of the record's ends (a spike ON the edge would keep
    # only the half of its area the grid covers)
    offsets = (2.3, 1.8, 0.9, 0.1)
    heights = (0.6, 4.0, 2.8, 1.2)
    width = 0.015
    areas = []
    for dt, h in zip(offsets, heights):
        for tc in (apex - dt, apex + dt):
            ch2 = ch2 + h * np.exp(-0.5 * ((t - tc) / width) ** 2)
        areas.append(h * width * np.sqrt(2 * np.pi))
    return t, ch1, ch2, areas


def test_synthetic_spikes_recovered():
    t, _, ch2, areas = _synthetic_record()
    spikes = cs.find_spikes(t, ch2)
    assert len(spikes) == 8
    planted = np.repeat(areas, 2)  # each pair plants its area twice
    got = np.array([s.integral_div_s for s in spikes])
    # threshold truncation and the 7 ms grid cost a few percent, no more
    assert np.allclose(np.sort(got), np.sort(planted), rtol=0.10)


def test_synthetic_apex_and_masking():
    t, ch1, _, _ = _synthetic_record()
    ch1 = ch1.copy()
    bad = slice(150, 160)          # ten cross-talk points mid-flank
    ch1[bad] = 0.2
    apex = cs.fit_apex(t, ch1)
    assert apex.t_apex_s == pytest.approx(2.55, abs=0.01)
    assert apex.n_masked >= 10     # the planted outliers all fall


def test_synthetic_pairing_and_ratios():
    t, ch1, ch2, _ = _synthetic_record()
    reading_apex = cs.fit_apex(t, ch1)
    r = cs._ratios(cs.find_spikes(t, ch2), reading_apex.t_apex_s)
    # heights (0.6, 4.0, 2.8, 1.2) in time order = labels 4207, 4192, 4154,
    # 4121, mirrored; so the 85 ratio is 4.0/2.8 on both sweeps
    assert r["ratio_85_up"] == pytest.approx(4.0 / 2.8, rel=0.05)
    assert r["ratio_85_down"] == pytest.approx(4.0 / 2.8, rel=0.05)


# ---------------------------------------------------------------------------
# the real record
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reading():
    return cs.read_scan()


def test_record_reads_as_four_mirror_pairs(reading):
    mids = list(reading.pair_midpoint_s.values())
    assert len(mids) == 4
    assert all(2.55 < m < 2.67 for m in mids)
    assert reading.apex.t_apex_s == pytest.approx(2.594, abs=0.005)
    assert reading.apex.t_argmax_s == pytest.approx(2.618, abs=0.005)


def test_record_up_sweep_order_matches_population_law(reading):
    up = [reading.up[k].integral_div_s for k in cs.UP_SWEEP_ORDER]
    pred = [reading.predicted[k] for k in cs.UP_SWEEP_ORDER]
    assert np.argsort(up).tolist() == np.argsort(pred).tolist()


def test_record_quoted_ratios(reading):
    assert reading.ratio_85_up == pytest.approx(1.421, abs=0.005)
    assert reading.ratio_85_up_band[0] == pytest.approx(1.340, abs=0.005)
    assert reading.ratio_85_up_band[1] == pytest.approx(1.421, abs=0.005)
    assert reading.iso_pair_up == pytest.approx(2.446, abs=0.01)
    # the compression diagnostic: the down-sweep inverts the 85 pair
    assert reading.ratio_85_down == pytest.approx(0.651, abs=0.01)


# ---------------------------------------------------------------------------
# freshness: the committed CSV and the APPARATUS paragraph track the code
# ---------------------------------------------------------------------------

def test_committed_integrals_csv_is_fresh(reading):
    """Value-wise, not byte-wise: annotate_results_status.py appends a
    `status` column after the pipeline, which this diff must tolerate."""
    fresh = {(r[0], r[1]): (r[2], r[3]) for r in cs.results_rows(reading)[1:]}
    with open(C.RESULTS_DIR / "cavity_scan_integrals.csv", newline="") as f:
        committed = {(r["quantity"], r["key"]): (r["value"], r["unit"])
                     for r in csv.DictReader(f)}
    assert committed == fresh


def test_apparatus_paragraph_quotes_the_module(reading):
    """The sec. 6 IMG_2508 paragraph quotes these numbers as prose; if a rule
    constant changes, this names the stale document."""
    text = (C.REPO_ROOT / "docs" / "APPARATUS.md").read_text(encoding="utf-8")
    start = text.index("IMG_2508's two channels are digitised")
    para = text[start:text.index("Still open", start)]
    for pin in (f"{reading.ratio_85_up:.2f}",
                f"{reading.ratio_85_up_band[0]:.2f}",
                f"{reading.ratio_85_down:.2f}",
                f"{reading.apex.t_apex_s:.2f}",
                f"{reading.apex.n_masked} of {reading.apex.n_flank}"):
        assert pin in para, f"APPARATUS.md sec. 6 no longer quotes {pin}"
