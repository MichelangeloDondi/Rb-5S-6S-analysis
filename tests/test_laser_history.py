"""M20 -- the reconstructed laser frequency history, and the test that it is a
measurement rather than per-trace scatter drawn as a curve."""

import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HIST = ROOT / "results" / "laser_history.csv"
STRUCT = ROOT / "results" / "laser_history_structure.csv"


def _mod():
    spec = importlib.util.spec_from_file_location(
        "run_laser_history", ROOT / "scripts" / "run_laser_history.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_structure_function_rises_so_the_history_is_real():
    """The load-bearing check. A reconstruction that is only per-trace noise
    gives a FLAT structure function; a real time-correlated drift gives one that
    rises with lag and saturates. If this ever goes flat, fig11 is meaningless
    and must not be shown."""
    rows = [{**r, "t_epoch": int(r["t_epoch"]),
             "offset_mhz": float(r["offset_mhz"])}
            for r in csv.DictReader(open(HIST))]
    sf = _mod().structure_function(rows, same_peak=True)
    assert len(sf) >= 3
    rms = [b["rms_mhz"] for b in sf]
    assert max(rms) / rms[0] > 1.5, f"structure function is flat: {rms}"
    # and it must rise before it saturates, not jump
    assert rms[1] > rms[0]


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_cross_peak_agreement_is_absent_and_that_is_expected():
    """Recorded so nobody reads the missing cross-check as a defect. Two
    different lines were never acquired closer than 6.6 minutes, which is past
    the correlation time the structure function measures, so their offsets
    cannot agree. The archive cannot cross-validate this way."""
    rows = [{**r, "t_epoch": int(r["t_epoch"]),
             "offset_mhz": float(r["offset_mhz"])}
            for r in csv.DictReader(open(HIST))]
    closest = min(abs(a["t_epoch"] - b["t_epoch"])
                  for i, a in enumerate(rows) for b in rows[i + 1:]
                  if a["peak"] != b["peak"])
    assert closest > 300, f"cross-peak gap {closest} s -- the cross-check is now possible"


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_offsets_are_referenced_per_peak_not_globally():
    """The four lines are different transitions at different sweep positions.
    Referencing them together would fold the line spacing into what is reported
    as laser drift, so each peak's offsets must be centred on their own median."""
    rows = list(csv.DictReader(open(HIST)))
    by = {}
    for r in rows:
        by.setdefault((r["session_day"], r["peak"]), []).append(float(r["offset_mhz"]))
    for key, vals in by.items():
        if len(vals) >= 5:
            vals = sorted(vals)
            med = vals[len(vals) // 2] if len(vals) % 2 else \
                0.5 * (vals[len(vals) // 2 - 1] + vals[len(vals) // 2])
            assert abs(med) < 1e-6, f"{key} not centred: median {med}"


@pytest.mark.skipif(not STRUCT.exists(), reason="structure csv not built")
def test_structure_csv_matches_the_committed_history():
    """Guard against the two CSVs drifting apart -- the figure reads both."""
    sf = list(csv.DictReader(open(STRUCT)))
    assert sf and all(int(b["n_pairs"]) > 5 for b in sf)
    assert float(sf[0]["rms_mhz"]) < float(max(sf, key=lambda b: float(b["rms_mhz"]))["rms_mhz"])


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_the_quiet_drift_exponent_claim_stays_retracted():
    """RETRACTED 2026-07-29, and pinned retracted rather than deleted.

    This test used to assert that the robust structure function rises faster
    than tau^0.5 -- "the drift is deterministic, ~1 MHz/min", measured at
    tau^0.79. That exponent was fitted across HORIZONTAL-KNOB moves, which
    difference two peak positions measured against different zeros, so it
    described the operator's re-centring cadence and not the laser.

    Confining pairs to one display epoch (the only span over which a peak
    position is a frequency) leaves a structure function that is thin and NOT
    monotone -- it rises, dips, then rises again on ~25 pairs. That cannot
    support an exponent, and this asserts so, so that nobody re-derives one from
    it. What the archive does still support is the step distribution, guarded
    below, and the quietest epoch's 0.17 MHz peak-to-peak over 3.4 min.
    """
    rows = [{**r, "t_epoch": int(r["t_epoch"]),
             "offset_mhz": float(r["offset_mhz"]),
             "display_epoch": r["display_epoch"]}
            for r in csv.DictReader(open(HIST))]
    sf = _mod().structure_function(
        rows, same_peak=True, robust=True,
        bins=((10, 25), (25, 60), (60, 150), (150, 400), (400, 1000), (1000, 2500)))
    vals = [b["robust_mhz"] for b in sf if b["robust_mhz"] > 0]
    monotone = all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))
    assert not monotone or len(vals) < 4, (
        f"the within-epoch structure function came out monotone over {len(vals)} "
        f"bins ({vals}). If that is real it is a NEW result and needs its own "
        "derivation -- it is not the retracted tau^0.79, which was fitted across "
        "knob moves. Do not simply restore the old assertion.")


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_step_distribution_is_heavy_tailed_from_the_re_kicks():
    """A continuously drifting laser gives Gaussian steps (RMS ~ 1.5x the
    median |step|). Hand re-centring gives a narrow core plus rare large jumps.
    The ratio here is ~20x, and that IS the detection of the interventions."""
    rows = [{**r, "t_epoch": int(r["t_epoch"]),
             "offset_mhz": float(r["offset_mhz"])}
            for r in csv.DictReader(open(HIST))]
    st = _mod().step_statistics(rows)
    assert st["heavy_tail_ratio"] > 5.0, st
    assert st["max_abs_mhz"] > 10.0
    assert st["median_abs_mhz"] < 1.0, "the quiet core should be well under a linewidth"


@pytest.mark.skipif(not HIST.exists(), reason="laser_history.csv not built")
def test_offsets_are_referenced_inside_a_display_epoch_not_across_the_knob():
    """The retraction, pinned (2026-07-29).

    The first version of M20 referenced peak positions to a per-session mean and
    reported a 65 MHz peak-to-peak laser excursion. That excursion was the
    scope's HORIZONTAL KNOB: the exported time axis is window-referenced, so
    moving the horizontal position re-zeros it and carries peak_pos_ms along.
    The evidence, from the archive alone: the setting is discrete and never
    jitters (237 of 295 consecutive pairs identical, every change a multiple of
    2 ms), and inside single 5-repeat blocks saved SECONDS apart a change of ds
    moves peak_pos_ms by 0.938*ds. The retracted headline was arithmetically the
    knob -- 64.97 MHz quoted against 1516 ms of window travel x 0.04257 =
    64.54 MHz, ratio 1.007.

    So this asserts the three properties that keep it retracted: the epoch
    column exists, an epoch never spans two horizontal settings, and no offset
    is referenced across one. The last is the load-bearing one -- if a future
    edit reverts to a per-session reference, the campaign-wide spread returns to
    the knob's ~65 MHz and this fails.
    """
    rows = list(csv.DictReader(open(HIST)))
    assert rows and "display_epoch" in rows[0] and "window_start_ms" in rows[0], (
        "laser_history.csv must carry display_epoch and window_start_ms; "
        "without the horizontal setting the offsets cannot be referenced")

    # one epoch, one horizontal setting
    by_ep = {}
    for r in rows:
        by_ep.setdefault(r["display_epoch"], set()).add(r["window_start_ms"])
    bad = {e: s for e, s in by_ep.items() if len(s) > 1}
    assert not bad, f"epochs spanning more than one horizontal setting: {bad}"

    # every (epoch, peak) segment is referenced to itself: its median offset is 0
    seg = {}
    for r in rows:
        seg.setdefault((r["display_epoch"], r["peak"]), []).append(float(r["offset_mhz"]))
    for key, v in seg.items():
        v = sorted(v)
        med = v[len(v) // 2] if len(v) % 2 else 0.5 * (v[len(v) // 2 - 1] + v[len(v) // 2])
        assert abs(med) < 1e-6, f"segment {key} is not referenced to itself (median {med})"

    # and the campaign-wide spread must NOT be the knob's travel again
    off = [float(r["offset_mhz"]) for r in rows]
    assert max(off) - min(off) < 45.0, (
        f"campaign-wide offset spread is {max(off) - min(off):.1f} MHz, back in the "
        "range of the retracted 65 MHz knob-travel figure -- has the reference "
        "reverted to per-session?")
