"""Tests for rb5s6s.rate_model — the time-resolved sweep-rate overlay.

The model replaced the bracket-average scheme on 2026-08-01 after the
in-ladder drift proved real (up to 1.9%/h, 5.6 sigma on 4207) and the
variance decomposition showed peak x session x time structure explains the
block scatter down to the statistical floor. These tests pin the pieces a
regression could silently break: recovery of a known drift, the two fitting
gates, error growth away from the data, and tolerance of the annotation
column that broke the first read-back in production.
"""

import csv
import math

import numpy as np
import pytest

from rb5s6s import rate_model as RM

T0 = 1_752_780_000.0


def _rows(n=12, a=0.0425, b_per_h=0.0008, span_h=1.5, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    rows, clock = [], {}
    for i in range(n):
        t = T0 + span_h * 3600.0 * i / (n - 1)
        rate = a + b_per_h * (t - (T0 + span_h * 1800.0)) / 3600.0
        rate += noise * rng.standard_normal()
        name = f"trace{i}.csv"
        rows.append({"file": f"rulers_p/{name}", "session": "P",
                     "peak": "4121", "rate_MHzms": str(rate)})
        clock[name] = t
    return rows, clock


def test_recovers_a_known_drift():
    rows, clock = _rows(noise=1e-5)
    (m,) = RM.fit_rate_models(rows, clock)
    assert m["a_rate_laser"] == pytest.approx(0.0425, rel=2e-3)
    assert m["b_per_hour"] == pytest.approx(0.0008, rel=0.15)
    assert m["n_traces"] == 12


def test_too_few_traces_yields_no_model():
    rows, clock = _rows(n=3)
    assert RM.fit_rate_models(rows, clock) == []


def test_short_span_yields_no_model():
    rows, clock = _rows(span_h=0.2)
    assert RM.fit_rate_models(rows, clock) == []


def test_unclocked_traces_are_excluded_not_fatal():
    rows, clock = _rows(noise=1e-5)
    del clock["trace0.csv"]
    (m,) = RM.fit_rate_models(rows, clock)
    assert m["n_traces"] == 11


def test_rate_at_error_grows_away_from_the_data():
    rows, clock = _rows(noise=1e-4)
    (m,) = RM.fit_rate_models(rows, clock)
    mid = m["t0_epoch"]
    _, rel_mid = RM.rate_at(m, mid)
    _, rel_far = RM.rate_at(m, mid + 5 * 3600.0)
    assert rel_far > 3 * rel_mid


def test_scatter_based_errors_track_the_noise_not_the_claim():
    """The covariance must come from the residuals: doubling the injected
    noise roughly doubles the parameter errors."""
    (lo,) = RM.fit_rate_models(*_rows(noise=1e-5, seed=1))
    (hi,) = RM.fit_rate_models(*_rows(noise=2e-5, seed=1))
    ratio = math.sqrt(hi["var_a"] / lo["var_a"])
    assert 1.5 < ratio < 2.5


def test_read_models_tolerates_annotation_columns(tmp_path):
    """annotate_results_status appends a string `status` column; the first
    production read-back crashed on float('MEASURED'). Never again."""
    rows, clock = _rows(noise=1e-5)
    models = RM.fit_rate_models(rows, clock)
    (tmp_path / "results").mkdir()
    path = RM.write_models(models, root=tmp_path)
    with open(path) as fh:
        recs = list(csv.DictReader(fh))
    for r in recs:
        r["status"] = "MEASURED"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    back = RM.read_models(root=tmp_path)
    m = back[("P", "4121")]
    assert m["a_rate_laser"] == pytest.approx(models[0]["a_rate_laser"])
    assert m["status"] == "MEASURED"


def test_clock_uses_earliest_copy(tmp_path):
    """Backup copies can only postdate acquisition: min mtime per basename."""
    d = tmp_path / "data_recovered"
    d.mkdir()
    with open(d / "CLOCK.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "path", "md5", "mtime_epoch", "manifest_file"])
        w.writerow(["a", "x/trace.csv", "m", "100.0", ""])
        w.writerow(["b", "y/Trace.csv", "m", "50.0", ""])
    clock = RM.load_clock(root=tmp_path)
    assert clock["trace.csv"] == 50.0


def test_production_models_exist_for_all_eight_groups():
    """Both sessions, all four peaks. If a refit ever drops one, the silent
    consequence is a fallback to the wider bracket errors -- fail loudly."""
    models = RM.read_models()
    if not models:
        pytest.skip("results/ruler_rate_model.csv not generated")
    for session in ("P", "T"):
        for peak in ("4121", "4154", "4192", "4207"):
            assert (session, peak) in models
