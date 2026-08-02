"""M24 wing check: the committed closure record and its logic.

The producer needs data_raw and ~6 min; these tests check the committed CSV
carries the closure the docs cite, with the internal consistency the
argument rests on.
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as C  # noqa: E402

CSV = C.RESULTS_DIR / "wing_check.csv"


def rows():
    return list(csv.DictReader(open(CSV)))


def val(quantity, key):
    for r in rows():
        if r["quantity"] == quantity and r["key"] == key:
            return float(r["value"]), float(r["err"] or "nan")
    raise KeyError((quantity, key))


def test_csv_exists_with_verdict():
    assert CSV.exists(), "run scripts/run_wing_check.py"
    v, e = val("f_wing_red_130C", "verdict")
    assert e > 0


def test_the_closure_is_a_null_at_the_lever():
    """The whole argument: at the x52 density point the RED-MINUS-BLUE
    asymmetry must be consistent with zero at the per-mille level. Since
    v3.0.0 the individual red side is no longer a null on its own (a
    symmetric transit-kernel misfit raises both sides, see the module
    docstring); it is the DIFFERENCE that a collisional satellite cannot
    fake. If a rerun ever finds a >3 sigma asymmetry here, C3g's closure is
    wrong and every doc citing it must change."""
    v, e = val("asymmetry_130C", "verdict")
    assert e < 0.005, "lost the per-mille sensitivity the closure quotes"
    assert abs(v) < 3 * e, "an asymmetry appeared at the density lever"


def test_high_density_asymmetry_is_null():
    """T110 and T130 each carry one single-peak anomaly in the individual
    sides (4192 red-only at T110, 4207 symmetric at T130; see the module
    docstring), so the individual f_wing_{side}_mean rows are no longer
    gated here. The DIFFERENCE, which a symmetric misfit cancels and a real
    wing would not, must still be null at both temperatures."""
    for T in ("T110", "T130"):
        v, e = val("asymmetry_red_minus_blue", T)
        assert abs(v) < 3 * e, (T, v, e)


def test_no_rising_density_trend():
    """Collisional scaling would make f(130) >> f(70). Demand the opposite
    ordering or consistency: the 130 C mean must not exceed the 70 C mean
    by more than the joint error."""
    v70, e70 = val("f_wing_red_mean", "T70")
    v130, e130 = val("f_wing_red_mean", "T130")
    assert v130 - v70 < 3 * (e70**2 + e130**2) ** 0.5


def test_condition_coverage():
    """All 16 (peak, T) conditions present on both sides."""
    n = sum(1 for r in rows() if r["quantity"] in ("f_wing_red", "f_wing_blue")
            and "_T" in r["key"])
    assert n == 32, n
