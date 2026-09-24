"""The archive point is read from the committed fit and the waist, never typed (F313, 2026-09-22)."""
from __future__ import annotations

import csv
import math

import pytest

from rb5s6s import config as C
from rb5s6s import constants as K
from rb5s6s.reference_point import REFERENCE_CONDITION, reference_point


def test_the_point_is_the_committed_fit_and_the_waist_transit():
    p = reference_point()
    role, peak, T, P = REFERENCE_CONDITION
    with open(C.RESULTS_DIR / "linefit_conditions.csv", newline="", encoding="utf-8") as fh:
        row = next(r for r in csv.DictReader(fh) if (r["role"], r["peak"], r["T"], r["P"]) == (role, peak, T, P))
    assert p["gamma_coll"] == float(row["gamma_coll"]) and p["sigma_laser"] == float(row["sigma_laser"])
    assert p["transit_fwhm"] == K.transit_fwhm_from_w0(C.W0_CENTRAL_M, float(T))
    assert all(math.isfinite(v) and v > 0 for v in p.values())


def test_a_missing_condition_raises_and_never_falls_back(tmp_path):
    (tmp_path / "linefit_conditions.csv").write_text("role,peak,T,P,gamma_coll,sigma_laser\np_sweep,4121,130,225,0.3,0.5\n")
    with pytest.raises(KeyError, match="no typed fallback"):
        reference_point(str(tmp_path))


def test_the_example_types_the_reference_point_to_two_decimals():
    """examples/campaign_twin.py reads no file, so it TYPES the point; the copy is held to its source here,
    which is the mechanism F313's dozen stale copies lacked."""
    import ast
    from pathlib import Path
    tree = ast.parse((Path(__file__).resolve().parents[1] / "examples" / "campaign_twin.py").read_text())
    vals = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign)
            for t in n.targets if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant)}
    p = reference_point()
    assert abs(vals["GAMMA_COLL_MHZ"] - p["gamma_coll"]) < 0.01, vals["GAMMA_COLL_MHZ"]
    assert abs(vals["SIGMA_LASER_MHZ"] - p["sigma_laser"]) < 0.01, vals["SIGMA_LASER_MHZ"]
