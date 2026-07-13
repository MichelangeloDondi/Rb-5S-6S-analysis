"""
Closure tests for the M0 QC metrics (rb5s6s/qc.py) and the trace loader.

Philosophy (docs/PLAN.md §1, "closure testing before real data"): before QC is allowed
to judge real traces, it must demonstrate on synthetic traces that
  - a clean trace raises NO hard flag (no over-rejection), and
  - each injected defect (spike, wing step, clipping, edge-cut peak, double
    peak, comb-in-RF-off) trips exactly the metric designed for it.
Synthetic traces mimic the campaign format: 2000 points, 0.5 ms step, a
~60 ms FWHM Lorentzian line on a small baseline with signal-dependent noise.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s.ingest import load_trace
from rb5s6s.qc import trace_metrics, hard_flags

T_MS = np.arange(2000) * 0.5 - 500.0  # matches the campaign window

# RNG hygiene: every synthetic gets its OWN freshly-seeded generator. A
# module-level shared generator makes each test's noise depend on how many
# draws earlier tests consumed — i.e., on test ORDER (bug caught 2026-07-11:
# the same test passed or failed depending on which tests ran before it).


def synth_line(center_ms=80.0, fwhm_ms=60.0, height=1.0, base=0.007,
               noise=0.008, rng=None):
    """Clean campaign-like RF-off trace: Lorentzian + baseline + noise whose
    sigma grows toward the peak (like the measured residuals)."""
    rng = rng if rng is not None else np.random.default_rng(C.RNG_SEED)
    x = 2.0 * (T_MS - center_ms) / fwhm_ms
    v = base + height / (1.0 + x * x)
    sig = noise * (1.0 + 4.0 * (v - base) / height)
    return v + rng.normal(0.0, 1.0, len(v)) * sig


def synth_comb(spacing_ms=147.0, center_ms=150.0, tooth_fwhm_ms=55.0,
               heights=(0.02, 0.09, 0.06, 0.09, 0.02), base=0.005,
               noise=0.004, rng=None):
    """Campaign-like RF-on ruler: 5 teeth, suppressed carrier."""
    rng = rng if rng is not None else np.random.default_rng(C.RNG_SEED)
    v = np.full_like(T_MS, base)
    for n, h in zip(range(-2, 3), heights):
        x = 2.0 * (T_MS - (center_ms + n * spacing_ms)) / tooth_fwhm_ms
        v = v + h / (1.0 + x * x)
    return v + rng.normal(0.0, noise, len(v))


def flags_of(v, rf_on=False):
    return hard_flags(trace_metrics(T_MS, v.copy()), rf_on=rf_on)


# ---------------------------------------------------------------------------
# no over-rejection
# ---------------------------------------------------------------------------

def test_clean_line_passes():
    for seed in (1, 2, 3):
        v = synth_line(rng=np.random.default_rng(seed))
        assert flags_of(v) == [], f"clean trace flagged (seed {seed})"


def test_clean_ruler_passes():
    v = synth_comb()
    assert flags_of(v, rf_on=True) == []


# ---------------------------------------------------------------------------
# each defect trips its own metric
# ---------------------------------------------------------------------------

def test_point_glitch_detected():
    v = synth_line()
    v[400] += 0.5  # cosmic/PMT spike far from the peak
    assert any("glitch" in f for f in flags_of(v))


def test_wing_step_detected():
    # z_step's honest scope (see config.QC_STEP_Z): SMALL background steps on
    # strictly signal-free ground — most relevant for dim traces, where a few
    # mV of level jump is a meaningful fraction of the line. Larger steps
    # leave the signal-free mask and are M3's job (fit residuals). Hence a
    # dim synthetic with a 3-sigma step whose edge sits in the far wing.
    # 5 mV chosen empirically: detected on every probed seed (z 5.5-7.8),
    # while 6 mV already self-hides on some seeds by leaving the 3-sigma
    # signal-free mask — the documented scope boundary.
    v = synth_line(height=0.05, noise=0.002)
    v[:150] += 0.005
    assert any("step" in f for f in flags_of(v))


def test_clean_dim_line_passes():
    # The dim regime (real 70 C traces) must not false-positive on steps.
    v = synth_line(height=0.05, noise=0.002, rng=np.random.default_rng(4))
    assert flags_of(v) == []


def test_clipping_detected():
    v = synth_line()
    v[v > 0.8] = 0.8  # ADC ceiling
    assert any("clipped" in f for f in flags_of(v))


def test_edge_cut_peak_detected():
    v = synth_line(center_ms=-495.0)  # line centered at the window edge
    assert any("cut by window" in f for f in flags_of(v))


def test_double_peak_detected():
    v = synth_line() + synth_line(center_ms=280.0, height=0.8) - 0.007
    assert any("second structure" in f for f in flags_of(v))


def test_fwhm_uses_contiguous_region():
    # A retrace-like second crossing far from the main line must NOT inflate
    # the FWHM (the union-of-regions bug caught by independent verification).
    from rb5s6s.qc import trace_metrics
    v = synth_line() + synth_line(center_ms=400.0, height=0.7) - 0.007
    m = trace_metrics(T_MS, v)
    assert m["fwhm_ms"] < 120.0          # main line only, not 320+ ms
    assert m["n_half_regions"] >= 2.0    # but the second region is counted


def test_low_snr_detected():
    v = synth_line(height=0.02, noise=0.008)
    assert any("SNR" in f for f in flags_of(v))


def test_lf_pickup_detected():
    # 50 Hz-like pickup (20 ms period) is nearly invisible to diff-based
    # sigma (critic finding) — the lf_ratio metric must catch it. Detection
    # floor by design: ratio = sqrt(1 + A^2/(2 sigma^2)) > 1.5 requires
    # pickup amplitude A >~ 1.6 sigma; test at A = 2.5 sigma.
    v = synth_line(height=0.05, noise=0.002)
    v += 0.005 * np.sin(2 * np.pi * T_MS / 20.0)
    assert any("low-frequency" in f for f in flags_of(v))


def test_strong_baseline_slope_detected():
    v = synth_line(height=0.05, noise=0.002)
    v += (T_MS - T_MS[0]) * 5e-6   # 5 mV across the window on a 50 mV line
    assert any("baseline slope" in f for f in flags_of(v))


def test_clean_traces_pass_lf_metrics():
    for seed in (1, 2, 3):
        v = synth_line(rng=np.random.default_rng(seed))
        fl = flags_of(v)
        assert not any("low-frequency" in f or "baseline slope" in f for f in fl)


def test_contiguous_fwhm_ignores_retrace_bump():
    # The shared retrace-safe FWHM helper must return the MAIN line's width,
    # not the span to a second bump near the window edge (the sweep-retrace
    # crossing that inflated 4207 25mW to "29 MHz" until fixed). Locks the fix.
    from rb5s6s.qc import contiguous_fwhm_ms
    main = synth_line(center_ms=80.0, fwhm_ms=60.0, height=1.0)
    retrace = synth_line(center_ms=440.0, fwhm_ms=55.0, height=0.7) - 0.007
    v = main + retrace
    w = contiguous_fwhm_ms(T_MS, v)
    assert 45.0 < w < 80.0, w   # ~60 ms main line, NOT ~360 ms span


def test_comb_in_rfoff_detected():
    # A comb-bearing trace mislabeled RF-off must be caught...
    v = synth_comb()
    assert any("comb periodicity" in f for f in flags_of(v, rf_on=False))


def test_missing_comb_in_rfon_detected():
    # ...and a single line mislabeled RF-on likewise.
    v = synth_line()
    assert any("no comb" in f for f in flags_of(v, rf_on=True))


# ---------------------------------------------------------------------------
# loader validation
# ---------------------------------------------------------------------------

def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p


def test_loader_accepts_valid_file(tmp_path):
    rows = "\n".join(f"{-0.5 + i * 0.0005:.6f},{0.001 * i:.6f}" for i in range(2000))
    p = _write(tmp_path, "ok.csv", "x-axis,2\nsecond,Volt\n" + rows + "\n")
    t, v = load_trace(p)
    assert len(t) == 2000 and abs((t[1] - t[0]) - 0.5) < 1e-9  # ms axis


def test_loader_rejects_bad_header(tmp_path):
    p = _write(tmp_path, "bad.csv", "nonsense\nsecond,Volt\n0,0\n")
    with pytest.raises(ValueError):
        load_trace(p)


def test_loader_rejects_wrong_row_count(tmp_path):
    p = _write(tmp_path, "short.csv", "x-axis,2\nsecond,Volt\n0.0,0.0\n0.0005,0.1\n")
    with pytest.raises(ValueError):
        load_trace(p)


def _rows_with_dropouts(empty_at):
    """2000 campaign-like rows; indices in `empty_at` get no voltage field
    (the LeCroy 'time-without-voltage' export quirk found in ~180 files)."""
    out = []
    for i in range(2000):
        t = -0.5 + i * 0.0005
        out.append(f"{t:.6f}," if i in empty_at else f"{t:.6f},{0.001:.6f}")
    return "\n".join(out) + "\n"


def test_loader_drops_edge_incomplete_rows(tmp_path):
    from rb5s6s.qc import ingest_flags
    p = _write(tmp_path, "tail.csv",
               "x-axis,2\nsecond,Volt\n" + _rows_with_dropouts({0, 1, 1998, 1999}))
    t, v, info = load_trace(p, with_info=True)
    assert (info["n_valid"], info["empty_head"], info["empty_tail"],
            info["empty_interior"]) == (1996, 2, 2, 0)
    assert info["axis_rebuilt"] == 0 and info["header_variant"] == ""
    assert ingest_flags(info) == []  # benign edge quirk, no flag


def test_loader_salvages_low_precision_time_axis(tmp_path):
    # The 4192nm_225mw1.csv pathology: stray header label + time column
    # printed at 3 significant figures (0.5 ms steps alias to duplicates).
    # Content is healthy, so the loader rebuilds the axis from row index
    # and records both anomalies instead of rejecting.
    rows = "\n".join(f"{-0.5 + i * 0.0005:.3g},{0.001:.6f}" for i in range(2000))
    p = _write(tmp_path, "round.csv", "jj,nj\nsecond,Volt\n" + rows + "\n")
    t, v, info = load_trace(p, with_info=True)
    assert info["axis_rebuilt"] == 1
    assert info["header_variant"] == "jj,nj"
    assert np.allclose(np.diff(t), 0.5)  # rebuilt, uniform ms grid


def test_loader_flags_dropout_riddled(tmp_path):
    # ~every other sample missing (the 4192nm_eom_070c3 pathology): loads on
    # a coarser-but-valid grid, and QC hard-flags it twice.
    from rb5s6s.qc import ingest_flags
    p = _write(tmp_path, "sick.csv",
               "x-axis,2\nsecond,Volt\n" + _rows_with_dropouts(set(range(1, 2000, 2))))
    t, v, info = load_trace(p, with_info=True)
    assert info["n_valid"] == 1000 and info["empty_interior"] >= 998
    fl = ingest_flags(info)
    assert any("truncated" in f for f in fl) and any("riddled" in f for f in fl)
