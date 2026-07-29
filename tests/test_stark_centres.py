"""M21: the centre channel is a NULL, and the null must stay stated.

The AC-Stark pull was once reported from the centres as |S0(225 mW)| < 7.3 MHz.
That came from session-referenced peak positions, i.e. the scope's horizontal
setting (see run_laser_history.py's retraction). Recomputed with a free offset on
every display epoch -- the correct handling, and the experimenter's own
suggestion of "the re-kicks as extra free parameters" -- the pull is
unidentifiable: only 3 of 26 power-sweep epochs contrast two powers, no epoch
spans two lines, and inside those three power still descends with time.

The tell is not the width of the interval but its behaviour: the pull's SIGN
flips between the linear and exponential drift forms, and the bound degrades
monotonically as the drift model gains freedom. A merely imprecise parameter
does neither. These tests pin that shape, so nobody reports the tightest of the
three as though it were a measurement -- the tightest is simply the most
constrained drift model, and tighter is not better here.
"""

from __future__ import annotations

import csv

import pytest

from rb5s6s.config import RESULTS_DIR

CSV = RESULTS_DIR / "stark_centres.csv"
pytestmark = pytest.mark.skipif(not CSV.exists(), reason="stark_centres.csv not built")


def _rows():
    return {r["drift_model"]: r for r in csv.DictReader(open(CSV))}


def test_all_three_drift_models_are_present_and_tagged_null():
    r = _rows()
    assert set(r) == {"linear", "exp", "exp2"}, sorted(r)
    for k, v in r.items():
        assert v["status"] == "NULL", (k, v["status"])


def test_the_pull_is_consistent_with_zero_in_every_drift_model():
    for k, v in _rows().items():
        lo, hi = float(v["pull_lo95"]), float(v["pull_hi95"])
        assert lo < 0.0 < hi, f"{k}: 95% interval [{lo}, {hi}] excludes zero"


def test_the_bound_degrades_as_the_drift_model_gains_freedom():
    """The signature of unidentifiability. If a future edit makes the bound
    IMPROVE with more drift freedom, the fit has started borrowing information
    from somewhere and needs re-deriving, not celebrating."""
    r = _rows()
    ub = [float(r[k]["S0_abs_ub95"]) for k in ("linear", "exp", "exp2")]
    assert ub[0] < ub[1] < ub[2], (
        f"|S0| bounds {ub} no longer degrade monotonically with drift freedom; "
        "the parameter was unidentifiable and this is how that showed")


def test_the_pull_sign_flips_between_linear_and_exponential_drift():
    r = _rows()
    a = float(r["linear"]["pull_mhz_per_w_laser"])
    b = float(r["exp"]["pull_mhz_per_w_laser"])
    assert a * b < 0, (
        f"pull is {a} (linear) and {b} (exp); the sign flip is the evidence that "
        "the centre channel does not determine it. If both signs now agree, "
        "re-derive before claiming a measurement.")


def test_the_centre_channel_stays_far_weaker_than_the_width_channel():
    """The paper's claim is that the WIDTH channel carries the light-shift
    information and the centres cannot. Pinned at an order of magnitude so a
    silent improvement cannot slip the narrative."""
    r = _rows()
    best = min(float(v["S0_abs_ub95"]) for v in r.values())
    width = float(r["linear"]["width_channel_bound_mhz"])
    assert best > 5.0 * width, (
        f"best centre bound {best:.2f} MHz is within 5x of the width channel's "
        f"{width} MHz -- if real, the centre channel is no longer negligible and "
        "the Paper-1 narrative needs updating")
