"""The twin-bias reader recovers a planted bias exactly and refuses every cell it does not hold.

WHY (PLAN v2 Phase 2, 2026-09-18): the window surface was computed and read by nothing because the
producer's windows and the surface's grid intersected nowhere. `rb5s6s.twin_bias` is the one reader,
and its two failure modes are the tests: a bias read between cells (interpolated) would be a number
nobody measured, so a missing case, statistic or level must RAISE; and a subtraction that quietly
dropped its standard error would shrink every bar it touched, so the standard error must come back
with the bias.
"""
from __future__ import annotations

import pathlib

import pytest

from rb5s6s import twin_bias


HEADER = "case,quantity,value,err,unit,basis,note,status\n"


def _surface(path: pathlib.Path, rows):
    path.write_text(HEADER + "".join(f"{c},{q},{v!r},{e},MHz^n,twin,plant,DIAGNOSTIC\n" for c, q, v, e in rows))
    return path


def test_a_planted_bias_is_recovered_to_1e_12_with_its_standard_error(tmp_path):
    truth = _surface(tmp_path / "L0.csv", [("P_4121_225mW_130C", "k4@8", 1.25, ""), ("P_4121_225mW_130C", "k2@2", 0.5, "")])
    noisy = _surface(tmp_path / "L100.csv", [("P_4121_225mW_130C", "k4@8", 1.25 + 0.0375, 0.004),
                                            ("P_4121_225mW_130C", "k2@2", 0.5 - 0.02, 0.001)])
    tb = twin_bias.load(truth, {1.0: noisy})
    b, se = tb.bias("P_4121_225mW_130C", "k4@8", 1.0)
    assert abs(b - 0.0375) < 1e-12 and se == 0.004
    b2, se2 = tb.bias("P_4121_225mW_130C", "k2@2", 1.0)
    assert abs(b2 + 0.02) < 1e-12 and se2 == 0.001
    assert tb.bias("P_4121_225mW_130C", "k4@8", 0.0) == (0.0, 0.0)


def test_a_missing_cell_raises_and_is_never_interpolated(tmp_path):
    truth = _surface(tmp_path / "L0.csv", [("P_4121_225mW_130C", "k4@8", 1.25, "")])
    noisy = _surface(tmp_path / "L100.csv", [("P_4121_225mW_130C", "k4@8", 1.30, 0.01)])
    tb = twin_bias.load(truth, {1.0: noisy})
    with pytest.raises(KeyError):
        tb.bias("P_4121_225mW_130C", "k4@13", 1.0)          # a window the surface lacks
    with pytest.raises(KeyError):
        tb.bias("P_4154_225mW_130C", "k4@8", 1.0)           # a case the surface lacks
    with pytest.raises(KeyError):
        tb.bias("P_4121_225mW_130C", "k4@8", 0.3)           # a level the surface lacks
    with pytest.raises(KeyError):
        tb.bias("P_4154_225mW_130C", "k4@8", 0.0)           # a missing case is not "unbiased"
    assert tb.missing([("P_4121_225mW_130C", "k4@8"), ("P_4121_225mW_130C", "k4@13")], 1.0) == [("P_4121_225mW_130C", "k4@13")]
    assert tb.missing([("P_4121_225mW_130C", "k4@8")], 1.0) == []


def test_a_file_that_is_not_a_surface_is_refused(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text(HEADER + "a,verdict,PASS,,,,,\n")
    with pytest.raises(ValueError):
        twin_bias.load(p, {})
