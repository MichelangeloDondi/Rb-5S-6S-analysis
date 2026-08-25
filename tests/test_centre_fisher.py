"""The drift-freedom cost, and the specific way its first version was wrong.

The factor this module produces was published as 48 and measures 7.3. The
failure was not arithmetic: the ratio divided a measured row by a row this
archive cannot evaluate. So the tests that matter here are the ones that
pin the SHAPE of the comparison -- same traces, same noise, only the drift
moving -- rather than the value, because the value was never the part that
went wrong.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_centre_fisher as F  # noqa: E402

CSV = ROOT / "results" / "centre_fisher.csv"


@pytest.fixture(scope="module")
def rows():
    if not CSV.exists():
        pytest.skip("run scripts/run_centre_fisher.py")
    return {(r["quantity"], r["key"]): r for r in csv.DictReader(open(CSV))}


def test_more_drift_freedom_never_buys_information(rows):
    """Monotonicity, the one thing a Fisher table cannot violate.

    Adding a free parameter cannot reduce the error on another. If this
    fails, the rows are not the same fit with one thing changed, which is
    exactly the defect the 48 carried.
    """
    order = ["drift_known", "constant_per_epoch", "linear_per_epoch",
             "quadratic_per_epoch"]
    vals = [float(rows[("sigma_amplitude", k)]["value"]) for k in order]
    assert vals == sorted(vals), dict(zip(order, vals))


def test_the_forecast_row_is_labelled_a_forecast(rows):
    """The baseline is not a measurement, and the CSV must say so.

    This archive's centres already have their per-epoch mean removed, so a
    no-drift-freedom row describes a lock that does not exist here. Calling
    it a measurement is what let a ratio be quoted as one.
    """
    # ENVELOPE is the controlled vocabulary's term for a model
    # estimate. The word FORECAST stays in the unit text, which is
    # where a status of eight fixed values cannot say enough.
    assert rows[("sigma_amplitude", "drift_known")]["status"] == "ENVELOPE"
    assert "FORECAST" in rows[("sigma_amplitude", "drift_known")]["unit"]
    assert rows[("inflation_linear_over_drift_known", "forecast")]["status"] \
        == "ENVELOPE"
    assert rows[("inflation_linear_over_constant", "measured")]["status"] \
        == "MEASURED"


def test_the_quoted_inflation_has_both_terms_in_this_record(rows):
    """The published factor is the one whose denominator is evaluable."""
    lin = float(rows[("sigma_amplitude", "linear_per_epoch")]["value"])
    con = float(rows[("sigma_amplitude", "constant_per_epoch")]["value"])
    quoted = float(rows[("inflation_linear_over_constant", "measured")]["value"])
    # the cells are written to four places, so the identity holds to theirs
    assert quoted == pytest.approx(lin / con, rel=1e-3)


def test_the_step_lever_lies_inside_one_epoch(rows):
    """A power change spanning two epochs is not a lever.

    The first version quoted a 100 mW change; no single epoch holds one.
    Centres either side of an epoch boundary are not comparable, so the
    lever is the largest change WITHIN an epoch.
    """
    d_p = float(rows[("delta_power_max_in_epoch_w", *[
        k for (q, k) in rows if q == "delta_power_max_in_epoch_w"])]["value"])
    assert 0.0 < d_p <= 0.06, d_p


def test_a_zig_zag_ladder_collapses_the_inflation():
    """The campaign recommendation, tested rather than asserted.

    The whole design change rests on one claim: several power changes
    inside one epoch break the degeneracy with a linear drift, because a
    line cannot follow a zig-zag. Build both ladders synthetically and the
    inflation must be large for one change and near one for many.
    """
    # THE TIMING IS THE ARCHIVE'S OWN, and it has to be. Uniformly spaced
    # traces give the one-change ladder an inflation of only 2x, so a
    # synthetic built on even sampling would understate the effect and this
    # test would pass for the wrong reason. The 2025 epochs took every
    # repeat of one power back to back, leaving TWO TIGHT TIME CLUSTERS, and
    # it is the clustering that makes a step and a line the same vector.
    times = [-1.3, -1.2, -1.1, -1.0, -0.9, 0.9, 1.0, 1.1, 1.2, 1.3]

    def epoch(powers):
        return {"1": [{"offset_mhz": "0.0", "t_epoch": str(60 * t),
                       "power_mW": str(p), "display_epoch": "1"}
                      for t, p in zip(times, powers)]}

    sigma = {"1": 0.04}
    one_change = epoch([225] * 5 + [175] * 5)
    zig_zag = epoch([225, 175] * 5)
    infl_one = (F.sigma_amplitude(one_change, sigma, 1)
                / F.sigma_amplitude(one_change, sigma, 0))
    infl_zig = (F.sigma_amplitude(zig_zag, sigma, 1)
                / F.sigma_amplitude(zig_zag, sigma, 0))
    assert infl_one > 5.0, infl_one
    assert infl_zig < 1.5, infl_zig
    # and the absolute error, which is what a campaign actually gets
    assert (F.sigma_amplitude(one_change, sigma, 1)
            > 5.0 * F.sigma_amplitude(zig_zag, sigma, 1))


def test_the_ladder_forecast_is_the_gain_the_chapter_quotes(rows):
    """The design change's value, held to the rows it is computed from."""
    as_taken = float(rows[("sigma_amplitude_forecast",
                           "linear_drift_as_taken")]["value"])
    cycled = float(rows[("sigma_amplitude_forecast",
                         "linear_drift_cycled")]["value"])
    gain = float(rows[("ladder_order_gain", "cycled_over_as_taken")]["value"])
    assert gain == pytest.approx(as_taken / cycled, rel=1e-3)
    assert cycled < as_taken


def test_the_noise_scale_is_one_model_across_every_row():
    """Only the drift may move between rows.

    A comparison in which the noise is re-estimated per drift class
    measures neither term. The producer takes one sigma per epoch, so the
    same dict reaches every call.
    """
    rng = np.random.default_rng(20260825)
    traces = [{"offset_mhz": str(rng.normal(0, 0.04)), "t_epoch": str(60 * i),
               "power_mW": "175" if i < 5 else "225", "display_epoch": "1"}
              for i in range(10)]
    sigma = F.noise_per_epoch({"1": traces})
    assert set(sigma) == {"1"}
    assert 0.0 < sigma["1"] < 0.2
