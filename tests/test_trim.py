"""
Closure tests for the residual-tail trimmer (rb5s6s/trim.py) and for the group
outlier rule that lands with it (rb5s6s/qc.py).

A tool that DELETES data has to be held to a harder standard than one that
merely computes: the tests below pin what it must never cut as tightly as what
it must. Spikes, clean synthetics, and anything inside the core guard are
untouchable. A known injected mirror must be found and the width it was biasing
must come back.

Pre-registered in docs/notes/ruler_validity_and_trim_prereg.md, sections 5 and
6 for the trimmer and amendment 2 for the outlier rule.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s import trim as TR
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import fit_condition, to_frequency
from rb5s6s.qc import boxcar, group_outlier, outlier_threshold, trace_metrics
from rb5s6s.ruler import validated_comb_fit

ROOT = Path(__file__).resolve().parents[1]
RATE_T = 0.08514                       # transition MHz/ms, the campaign value
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)


# --------------------------------------------------------------------------
# the detector
# --------------------------------------------------------------------------

def _noise(seed, n=2000, sd=1.0):
    return np.random.default_rng(seed).normal(0.0, sd, n)


@pytest.mark.parametrize("height", [10.0, 100.0, 1000.0])
def test_a_single_spike_never_looks_like_a_tail(height):
    """The property that makes the detector usable at all.

    A glitch is spread over exactly TRIM_SMOOTH_W samples by the smoother, so
    it can accumulate for at most that many, and TRIM_MIN_RUN sits above it.
    The immunity is therefore independent of how tall the glitch is, which is
    what the three heights here assert. A detector that merely resisted SMALL
    spikes would pass at 10 and fail at 1000.
    """
    for seed in range(6):
        r = _noise(seed)
        r[1200] += height
        assert TR.cusum_onset(r) is None, (seed, height)


def test_a_sustained_rise_is_found_near_where_it_starts():
    """The other side of the same coin: a real step must be found, and found
    close to its own onset rather than at the far end of the excursion."""
    onsets = []
    for seed in range(6):
        r = _noise(seed)
        r[1200:] += 1.5
        i = TR.cusum_onset(r)
        assert i is not None, seed
        onsets.append(i)
    onsets = np.array(onsets)
    # the smoother's own half width plus the samples it takes to accumulate:
    # a two-sided tolerance, so a detector that fired early on noise would fail
    assert np.all(np.abs(onsets - 1200) <= 60), onsets


def test_the_detector_is_one_sided():
    """A retrace mirror ADDS signal. A negative excursion is not the defect the
    trimmer exists for, and cutting on one would remove the very samples that
    constrain a background."""
    for seed in range(6):
        r = _noise(seed)
        r[1200:] -= 3.0
        assert TR.cusum_onset(r) is None, seed


@pytest.mark.slow
def test_the_cusum_threshold_clears_the_null():
    """The section 6 null calibration, re-run.

    10,000 traces of pure noise through the full two-sided trim path at the
    hardest geometry any stage presents. The pre-registered target is at most
    one false trim across the 297-trace archive. TRIM_CUSUM_H was set to the
    smallest integer at which the calibration produced no false alarm at all,
    which is stricter, so this test asserts the pre-registered target and
    reports the margin.
    """
    rng = np.random.default_rng(C.RNG_SEED)
    n, lo, hi, ntr = 2000, 890, 1110, 10000
    t = np.arange(n) * 0.5
    fired = 0
    for _ in range(ntr):
        if TR.tail_trim(t, rng.standard_normal(n), lo, hi)["trimmed"]:
            fired += 1
    assert fired / ntr <= 1.0 / 297.0, (
        f"{fired} false trims in {ntr} traces, above the pre-registered "
        f"1 in 297. Re-calibrate TRIM_CUSUM_H rather than loosening this.")


# --------------------------------------------------------------------------
# the core guard, and refusing rather than eating
# --------------------------------------------------------------------------

def test_the_core_guard_is_inviolable():
    """Whatever sits inside the guard, however loud, is never cut. This is the
    property that stops the trimmer eating a dim cold line whose wings are the
    only thing it has."""
    t = np.arange(2000) * 0.5
    r = _noise(1)
    r[900:1100] += 20.0                  # a mountain, entirely inside the core
    out = TR.tail_trim(t, r, 890, 1110)
    assert not out["trimmed"], out["trim_reason"]
    assert out["mask"].all()


def test_a_tail_reaching_into_the_guarded_half_is_refused():
    """The standing rule of section 5. A cut that would start closer to the
    core than half the way to the window edge is not a tail, it is the thing
    being measured, and it is not taken."""
    t = np.arange(2000) * 0.5
    r = _noise(2)
    r[1150:] += 3.0                      # begins just outside the core
    out = TR.tail_trim(t, r, 890, 1110)
    assert not out["trimmed"]
    assert out["trim_reason"] == "refused, trim would reach into the guarded half"
    assert out["mask"].all()


def test_a_far_tail_is_cut_and_the_record_bounds_what_was_kept():
    t = np.arange(2000) * 0.5
    r = _noise(3)
    r[1700:] += 3.0
    out = TR.tail_trim(t, r, 890, 1110)
    assert out["trimmed"] and out["n_trimmed"] > 0
    assert out["trim_reason"] == "sustained positive residual, upper tail"
    assert out["mask"][:1111].all()      # nothing at or below the core went
    assert not out["mask"][1750:].any()  # the tail itself did
    kept = np.flatnonzero(out["mask"])
    assert out["trim_start_ms"] == t[kept[0]]
    assert out["trim_end_ms"] == t[kept[-1]]


# --------------------------------------------------------------------------
# the model-free envelope the quality pass uses
# --------------------------------------------------------------------------

def _line(mirror=None, mirror_amp=0.6, gamma=1.5, seed=C.RNG_SEED, noise=3e-3):
    rng = np.random.default_rng(seed)
    p = model_profile(NU, gamma_coll=gamma, sigma_laser_fwhm=1.2, transit_fwhm=0.9)
    v = p / p.max()
    if mirror is not None:
        m = model_profile(NU - mirror, gamma_coll=gamma, sigma_laser_fwhm=1.2,
                          transit_fwhm=0.9)
        v = v + mirror_amp * m / m.max()
    return v + rng.normal(0.0, noise, len(v))


def test_the_envelope_residual_is_flat_on_a_single_line():
    """A Lorentzian's own far tail is smooth SIGNAL far above noise, and a
    residual against a baseline would read it as a tail to be cut. The envelope
    is a decaying shape rather than a level, so it does not."""
    for seed in (1, 2, 3):
        r = TR.envelope_residual(T_MS, _line(seed=seed))
        sm = boxcar(_line(seed=seed), C.TRIM_SMOOTH_W)
        assert np.max(np.abs(r)) < 0.05 * sm.max(), seed


def test_the_envelope_residual_carries_ordinary_sample_noise():
    """The scale the detector's threshold is written in. Subtracting the
    envelope from the SMOOTHED trace instead would leave a residual that is
    identically zero over every strictly falling flank, collapsing its median
    absolute deviation to a tenth of the real noise and making every excursion
    read as ten sigma. That was measured, and it is why the subtraction is from
    the raw trace."""
    v = _line(seed=5)
    r = TR.envelope_residual(T_MS, v)
    sample_sd = float(np.std(np.diff(v)) / np.sqrt(2.0))
    assert 0.5 * sample_sd < TR._robust_sigma(r) < 1.5 * sample_sd


def test_the_envelope_residual_finds_a_second_structure():
    r = TR.envelope_residual(T_MS, _line(mirror=25.0))
    i = int(np.argmax(boxcar(r, C.TRIM_SMOOTH_W)))
    assert abs(NU[i] - 25.0) < 6.0, NU[i]


# --------------------------------------------------------------------------
# integration 1: the ruler ladder
# --------------------------------------------------------------------------

def _comb(delta=147.3, t0=0.0, w=55.0, heights=(0.004, 0.02, 0.09, 0.06, 0.09, 0.02, 0.004),
          base=0.005, noise=0.004, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    v = np.full_like(T_MS, base)
    for n, h in zip(range(-3, 4), heights):
        v = v + h / (1.0 + (2.0 * (T_MS - (t0 + n * delta)) / w) ** 2)
    return v + rng.normal(0.0, noise, len(T_MS))


def test_a_centred_ruler_has_no_room_to_trim():
    """Refuse rather than eat, in its structural form. A centred campaign comb
    spans 882 ms of a 999 ms window, so one fitted width of guard on each side
    leaves a few samples, far below the minimum run. The trimmer cannot fire
    there whatever the residual does, and this pins that the ladder therefore
    returns the plain fit."""
    for seed in range(4):
        v = _comb(seed=seed)
        out = validated_comb_fit(T_MS, v)
        assert not out["trimmed"], out["trim_reason"]


def test_clean_combs_are_never_trimmed():
    """Zero false positives on every comb shape the closure suite already
    fits."""
    cases = {"bright": dict(),
             "suppressed carrier": dict(heights=(0.004, 0.02, 0.09, 0.006, 0.09, 0.02, 0.004)),
             "missing outer teeth": dict(heights=(0.0, 0.02, 0.09, 0.06, 0.09, 0.02, 0.0)),
             "cold": dict(heights=(0.002, 0.004, 0.0085, 0.006, 0.008, 0.004, 0.002),
                          noise=0.0016, seed=3)}
    for drift in (-40.0, 0.0, 40.0):
        cases[f"drift {drift:+.0f}"] = dict(t0=drift, seed=2)
    for name, kw in cases.items():
        out = validated_comb_fit(T_MS, _comb(**kw))
        assert not out["trimmed"], (name, out["trim_reason"])
        assert abs(out["delta_ms"] - 147.3) < 1.0, (name, out["delta_ms"])


# --------------------------------------------------------------------------
# integration 2: the condition fit
# --------------------------------------------------------------------------

def _condition(mirror=None, mirror_amp=0.6, gamma=1.5, ntr=5, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    freqs, volts = [], []
    for _ in range(ntr):
        c = rng.normal(0.0, 0.5)
        g = 1.0 + rng.normal(0.0, 0.03)
        p = model_profile(NU - c, gamma_coll=gamma, sigma_laser_fwhm=1.2, transit_fwhm=0.9)
        v = g * p / p.max()
        if mirror is not None:
            m = model_profile(NU - c - mirror, gamma_coll=gamma,
                              sigma_laser_fwhm=1.2, transit_fwhm=0.9)
            v = v + mirror_amp * g * m / m.max()
        sig = np.sqrt(3e-3 ** 2 + 2e-5 * np.maximum(v, 0.0))
        volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
        freqs.append(NU.copy())
    return freqs, volts


def test_a_known_mirror_is_trimmed_and_the_width_comes_back():
    """The plant. A mirror at plus 28 MHz sits inside the adaptive fit window,
    which is the case that window cannot handle, and it drags the collisional
    width 0.6 MHz below truth. The trim must find it and give the width back.
    """
    truth = 1.5
    f, v = _condition(mirror=28.0)
    plain = fit_condition([x.copy() for x in f], [x.copy() for x in v],
                          T_C=110.0, transit_fwhm=0.9)
    trimmed = fit_condition([x.copy() for x in f], [x.copy() for x in v],
                            T_C=110.0, transit_fwhm=0.9, trim_tails=True)
    assert abs(plain["gamma_coll"] - truth) > 0.5, plain["gamma_coll"]
    assert abs(trimmed["gamma_coll"] - truth) < 0.4, trimmed["gamma_coll"]
    assert trimmed["chi2_red"] < 0.5 * plain["chi2_red"]
    n = sum(r["trimmed"] for r in trimmed["trim_records"])
    assert n == len(f), [r["trim_reason"] for r in trimmed["trim_records"]]
    for r in trimmed["trim_records"]:
        assert r["trim_end_ms"] < 28.0        # the mirror is outside what was kept
        assert r["trim_end_ms"] > 6.0         # and the line's own wings are not


def test_a_clean_condition_is_untouched_by_the_trimmer():
    """The no-op that makes turning it on safe."""
    f, v = _condition()
    plain = fit_condition([x.copy() for x in f], [x.copy() for x in v],
                          T_C=110.0, transit_fwhm=0.9)
    trimmed = fit_condition([x.copy() for x in f], [x.copy() for x in v],
                            T_C=110.0, transit_fwhm=0.9, trim_tails=True)
    assert not any(r["trimmed"] for r in trimmed["trim_records"])
    assert trimmed["gamma_coll"] == plain["gamma_coll"]


def test_the_adaptive_window_still_excludes_the_far_mirror():
    """The pre-existing guarantee the trimmer must not disturb: a mirror 40 MHz
    out is excluded by the fit WINDOW, before the trimmer is consulted at all.
    This is tests/test_linefit.py's own case, re-asserted with trimming on."""
    f, v = _condition(mirror=40.0)
    fit = fit_condition(f, v, T_C=110.0, transit_fwhm=0.9, trim_tails=True)
    assert abs(fit["gamma_coll"] - 1.5) < 0.4, fit["gamma_coll"]


# --------------------------------------------------------------------------
# integration 3: the quality pass
# --------------------------------------------------------------------------

def test_a_ruler_reports_the_trim_as_not_applicable():
    """One record of one decision. A ruler's trim is decided by the M2 ladder
    and written to results/ruler_traces.csv, so the quality table must not
    carry a second answer that can disagree with it."""
    m = trace_metrics(T_MS, _comb(), rf_on=True)
    assert m["trim_reason"] == "not applicable, multi-peak trace"
    assert m["trimmed"] == 0.0
    assert np.isnan(m["trim_start_ms"]) and np.isnan(m["trim_end_ms"])


def test_a_clean_line_is_not_trimmed_by_the_quality_pass():
    for seed in range(12):
        m = trace_metrics(T_MS, _line(seed=seed))
        assert m["trimmed"] == 0.0, (seed, m["trim_reason"])


def test_the_quality_pass_finds_a_retrace_crossing():
    """The case the archive actually has: the down ramp re-crosses the same
    line about 40 MHz away and the crossing sits in the far tail of the window.
    The quality pass must find it without any lineshape model."""
    for seed in range(6):
        m = trace_metrics(T_MS, _line(mirror=38.0, seed=seed))
        assert m["trimmed"] == 1.0, (seed, m["trim_reason"])
        assert m["trim_reason"] == "sustained positive residual, upper tail"
        # what is kept stops short of the crossing and keeps the line's wings
        assert 100.0 < m["trim_end_ms"] < 38.0 / RATE_T, m["trim_end_ms"]


def test_a_close_crossing_is_refused_rather_than_eaten():
    """The other half of the same behaviour, stated so it is not mistaken for a
    miss. A crossing closer in than half the way to the window edge is inside
    the guarded half, and the pre-registered rule refuses the cut instead of
    taking one that could reach the line."""
    m = trace_metrics(T_MS, _line(mirror=25.0))
    assert m["trimmed"] == 0.0
    assert m["trim_reason"] == "refused, trim would reach into the guarded half"


def test_the_quality_pass_trim_never_enters_hard_flags():
    """A forbidden change, named in the pre-registration. The archive-wide
    fit's first admission gate excludes every non-second-structure hard-flag
    class outright, so a trim written into that text would silently empty the
    gate's census."""
    from rb5s6s.qc import hard_flags
    m = trace_metrics(T_MS, _line(mirror=25.0))
    for f in hard_flags(m, rf_on=False):
        assert "trim" not in f.lower(), f


def test_qc_metrics_table_carries_the_trim_and_outlier_record():
    """Schema guard on the committed table."""
    p = ROOT / "results" / "qc_metrics.csv"
    if not p.exists():
        pytest.skip("results/qc_metrics.csv not present (run scripts/run_qc.py)")
    header = next(csv.reader(open(p)))
    missing = [c for c in ("trimmed", "trim_start_ms", "trim_end_ms",
                           "trim_reason", "outlier", "outlier_reason")
               if c not in header]
    assert not missing, (
        f"results/qc_metrics.csv predates {missing}. Re-run scripts/run_qc.py, "
        f"stage the CSV, then redraw the figures")


# --------------------------------------------------------------------------
# the group outlier rule
# --------------------------------------------------------------------------

def _null_dev_group(x):
    """Largest deviation in each group, scaled by the WHOLE group. `x` is
    (groups, n, m) of independent standard Gaussians, which is the null
    amendment 3 calibrates against."""
    med = np.median(x, axis=1, keepdims=True)
    mad = 1.4826 * np.median(np.abs(x - med), axis=1, keepdims=True)
    return (np.abs(x - med) / np.maximum(mad, 1e-12)).max(axis=(1, 2))


def _null_dev_sibling(x):
    """The same, with each member centred and scaled by the OTHER n-1 members,
    which is what qc.sibling_zscores does to population B."""
    out = np.empty_like(x)
    for i in range(x.shape[1]):
        sib = np.delete(x, i, axis=1)
        med = np.median(sib, axis=1)
        mad = 1.4826 * np.median(np.abs(sib - med[:, None, :]), axis=1)
        out[:, i, :] = np.abs(x[:, i, :] - med) / np.maximum(mad, 1e-12)
    return out.max(axis=(1, 2))


_RETIRED_T_QUANTILE_THRESHOLDS = {
    (4, 1): 5.392, (5, 1): 4.604, (6, 1): 4.219, (7, 1): 3.997, (8, 1): 3.855,
    (4, 2): 6.895, (5, 2): 5.598, (6, 2): 4.983, (7, 2): 4.632, (8, 2): 4.408,
}
"""Amendment 2 B4's table, kept here so the retirement is testable. These fired
at 7.9 to 13.3 per cent per group against the 5 per cent they claimed, because
they came from a t quantile and the statistic is not a t."""


def test_the_threshold_table_matches_the_amendment():
    """The numbers written into amendment 3, read back from the table."""
    expected = {(4, 1): 6.909, (5, 1): 7.926, (6, 1): 5.530, (7, 1): 5.854,
                (8, 1): 4.915, (4, 2): 9.902, (5, 2): 11.411, (6, 2): 7.163,
                (7, 2): 7.611, (8, 2): 6.072}
    for (n, m), want in expected.items():
        got = outlier_threshold(n, m)
        assert abs(got - want) < 5e-4, (n, m, got)
    sibling = {(4, 1): 61.520, (5, 1): 13.847, (6, 1): 13.004, (7, 1): 8.252,
               (8, 1): 8.102, (4, 2): 122.507, (5, 2): 19.884, (6, 2): 18.771,
               (7, 2): 10.677, (8, 2): 10.506}
    for (n, m), want in sibling.items():
        got = outlier_threshold(n, m, scaling="sibling")
        assert abs(got - want) < 5e-4, (n, m, got)


def test_every_calibrated_threshold_is_stricter_than_the_one_it_replaces():
    """Amendment 3 corrects an under-strict rule, so no cell may loosen. A cell
    that fell would mean the recalibration had removed a trace the old rule
    kept, which is the direction that would need its own argument."""
    for (n, m), old in _RETIRED_T_QUANTILE_THRESHOLDS.items():
        for scaling in ("group", "sibling"):
            assert outlier_threshold(n, m, scaling=scaling) > old, (n, m, scaling)


def test_a_group_beyond_the_calibrated_range_refuses_to_extrapolate():
    """The table is measured, not a formula, so there is nothing to evaluate off
    its end. A ninth member has to send someone back to the null."""
    with pytest.raises(ValueError, match="calibrated"):
        outlier_threshold(9, 1)
    with pytest.raises(ValueError, match="calibrated"):
        outlier_threshold(500, 1)


def test_the_sibling_scaling_is_never_the_easier_one():
    """Dropping a member from its own scale can only lengthen the tail of its
    deviation, so the sibling threshold has to sit above the group one at every
    size. If this ever inverts, the two nulls have been swapped at a call site."""
    for m in (1, 2):
        for n in range(4, 9):
            assert (outlier_threshold(n, m, scaling="sibling")
                    > outlier_threshold(n, m, scaling="group")), (n, m)


@pytest.mark.slow
def test_the_calibrated_thresholds_return_five_per_cent_on_the_null():
    """Amendment 3's calibration, re-run at a tenth of its size.

    200,000 Gaussian groups per cell, which is the size of the measurement that
    found the miscalibration. The tolerance is the binomial error on that count,
    widened to a round half a per cent, so this fails on a threshold that has
    drifted and not on Monte Carlo noise.
    """
    for scaling, stat in (("group", _null_dev_group),
                          ("sibling", _null_dev_sibling)):
        for m in (1, 2):
            for n in range(4, 9):
                rng = np.random.default_rng(C.RNG_SEED + 10 * n + m)
                s = stat(rng.standard_normal((200_000, n, m)))
                rate = float((s > outlier_threshold(n, m, scaling=scaling)).mean())
                assert abs(rate - C.OUTLIER_ALPHA) < 0.005, (
                    f"{scaling} n={n} m={m} fires at {100 * rate:.2f}% against "
                    f"the pre-registered {100 * C.OUTLIER_ALPHA:.0f}%")


def test_only_one_member_is_ever_removed():
    x = [10.0, 10.1, 10.2, 10.05, 20.0, 21.0]
    i, dev, thr = group_outlier(x)
    assert i in (4, 5)                    # exactly one index, never a list
    assert dev > thr


def test_a_group_that_agrees_has_no_outlier():
    for seed in range(8):
        x = np.random.default_rng(seed).normal(147.0, 0.3, 5)
        i, _, _ = group_outlier(x, floor_frac=C.OUTLIER_MAD_FLOOR_FRAC)
        assert i is None or abs(x[i] - np.median(x)) > 0.5, (seed, x)


def test_a_small_group_is_never_tested():
    """With three members the scaled median absolute deviation is one number,
    so a rule built on it reports the arithmetic of three points."""
    for n in range(1, C.OUTLIER_MIN_GROUP):
        i, _, _ = group_outlier([1.0, 1.0, 50.0][:n] or [1.0])
        assert i is None, n


def test_the_floor_stops_a_tight_group_manufacturing_an_outlier():
    """Three identical members give a scaled median absolute deviation of zero,
    which without a floor divides by nothing and calls the fourth member
    infinitely deviant."""
    x = [147.0, 147.0, 147.0, 147.02, 147.0]
    assert group_outlier(x)[0] is not None                        # no floor
    assert group_outlier(x, floor_frac=C.OUTLIER_MAD_FLOOR_FRAC)[0] is None


# --------------------------------------------------------------------------
# the collected record
# --------------------------------------------------------------------------

def _run_trim_report():
    spec = importlib.util.spec_from_file_location(
        "run_trim_report", ROOT / "scripts" / "run_trim_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_trim_report_declares_every_column_it_fills():
    mod = _run_trim_report()
    row = mod._row({}, "x.csv", "qc", trimmed=1, start=1.0, end=2.0, reason="r")
    assert sorted(row) == sorted(mod.HEADER), set(mod.HEADER) ^ set(row)


def test_trim_report_leaves_the_unrecorded_stage_empty():
    """An empty cell is not a claim that nothing was trimmed. The condition fit
    runs the trimmer but does not persist a per-trace record, and filling a
    zero there would be an assertion this script cannot check."""
    mod = _run_trim_report()
    assert mod._row({}, "x.csv", "linefit", trimmed=None)["trimmed"] == ""


def test_committed_trim_report_covers_every_stage():
    p = ROOT / "results" / "trim_report.csv"
    if not p.exists():
        pytest.skip("results/trim_report.csv not present "
                    "(run scripts/run_trim_report.py)")
    stages = {r["stage"] for r in csv.DictReader(open(p))}
    assert {"qc", "ruler", "linefit"} <= stages, stages
