"""M26: the pilot day's own ruler. Production-shape checks on the committed CSV.

The producer needs the private pilot quarantine; these tests hold the
committed record to its own construction: the Def group carries the scale,
the pre-adjustment railed traces are excluded from every mean, and the
measured scale sits in the physically sane band around 1.
"""

import csv

import pytest

from rb5s6s import config as C

CSV = C.RESULTS_DIR / "pilot_ruler.csv"


def rows():
    if not CSV.exists():
        pytest.skip("results/pilot_ruler.csv not generated")
    return list(csv.DictReader(open(CSV)))


def test_def_group_present_and_full():
    g = [r for r in rows() if r["quantity"] == "group_rate" and r["key"] == "def"]
    assert len(g) == 1
    assert "n=10" in g[0]["unit"]


def test_railed_traces_are_flagged_not_averaged():
    r = rows()
    railed = [x for x in r if x["quantity"] == "trace_railed"]
    assert len(railed) >= 5, "the pre-adjustment sub-series should rail"
    for x in railed:
        assert "excluded from every mean" in x["unit"]


def test_measured_scale_sane_and_tight():
    r = rows()
    s = next(x for x in r if x["quantity"] == "pilot_rate_scale_measured")
    val, err = float(s["value"]), float(s["err"])
    assert 0.98 < val < 1.02, val
    assert err < 0.005, "the measurement should beat the fitted nuisance's box"


def test_def_and_adjusted_initial_agree():
    """The post-adjustment remainder of 'Initial attempts' must agree with
    Def at the few-sigma level, since both are the final configuration."""
    r = rows()
    g = {x["key"]: (float(x["value"]), float(x["err"]))
         for x in r if x["quantity"] == "group_rate"}
    if "initial" not in g:
        pytest.skip("initial group too small after the rail cut")
    d, i = g["def"], g["initial"]
    pull = abs(d[0] - i[0]) / (d[1] ** 2 + i[1] ** 2) ** 0.5
    assert pull < 4.0, pull
