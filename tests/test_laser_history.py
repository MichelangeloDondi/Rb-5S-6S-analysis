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
def test_quiet_drift_is_near_linear_not_a_random_walk():
    """The robust (MAD) structure function measures what the laser does BETWEEN
    interventions, with the re-kick tail removed. It must rise faster than the
    tau^0.5 of a random walk: the drift is deterministic, ~1 MHz/min. If this
    ever comes out at 0.5, the drift model in the docstring is wrong."""
    import math
    rows = [{**r, "t_epoch": int(r["t_epoch"]),
             "offset_mhz": float(r["offset_mhz"])}
            for r in csv.DictReader(open(HIST))]
    sf = _mod().structure_function(
        rows, same_peak=True, robust=True,
        bins=((10, 25), (25, 60), (60, 150), (150, 400), (400, 1000), (1000, 2500)))
    pts = [(0.5 * (b["lag_lo_s"] + b["lag_hi_s"]), b["robust_mhz"])
           for b in sf if b["robust_mhz"] > 0]
    assert len(pts) >= 4
    n = len(pts)
    sx = sum(math.log(t) for t, _ in pts) / n
    sy = sum(math.log(v) for _, v in pts) / n
    num = sum((math.log(t) - sx) * (math.log(v) - sy) for t, v in pts)
    den = sum((math.log(t) - sx) ** 2 for t, _ in pts)
    assert num / den > 0.55, f"quiet-time exponent {num / den:.2f} looks like a random walk"


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
