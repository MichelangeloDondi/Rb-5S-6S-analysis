"""The two radiation-environment producers, and the contract they carry.

They are the first results files with an `err_kind` column and the first that
tag their own rows, so the guard checks the two properties that make that safe:
the status vocabulary is the annotator's, and an ENVELOPE row whose error is a
range must actually bracket its own point value. The second is the one that
would have caught a band computed about the wrong centre.
"""
import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VOCAB = {"BOUND", "NULL", "MEASURED", "PRELIM", "ARTIFACT", "DIAGNOSTIC",
         "CALIB", "ENVELOPE"}
FILES = ("trapping_channels.csv", "blackbody_channels.csv",
         "cascade_branching.csv")


def _rows(name):
    with open(ROOT / "results" / name, newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("name", FILES)
def test_schema_and_vocabulary(name):
    rows = _rows(name)
    assert rows, f"{name} is empty"
    for r in rows:
        assert set(r) >= {"quantity", "key", "value", "err", "err_kind",
                          "unit", "status"}, f"{name}: schema"
        assert r["status"] in VOCAB, f"{name}: {r['status']!r} not in vocab"
        float(r["value"])                       # parses, or the test fails here
        for col in ("err", "err_lo", "err_hi"):
            if r.get(col):
                assert float(r[col]) >= 0.0
                assert r["err_kind"], (
                    f"{name}: {r['quantity']} has {col}, no err_kind")


# cascade_branching carries no error bars: every row is exact given the line
# list, which is the claim its blank err column makes
@pytest.mark.parametrize("name", FILES[:2])
def test_every_error_bar_names_what_kind_it_is(name):
    """An err_kind of its own is the point of this schema: 'geometry' and
    'polarizability' are different claims about what is uncertain, and a reader
    who cannot tell them apart cannot use either."""
    kinds = {r["err_kind"] for r in _rows(name)
             if r["err"] or r.get("err_lo") or r.get("err_hi")}
    assert kinds, f"{name}: no row carries an error bar at all"
    assert all(k for k in kinds), f"{name}: an error bar with no kind"


def test_the_halo_band_brackets_its_own_point_value():
    """The standoff band is computed at the ends of a range whose interior
    holds the quoted point. If the point ever falls outside its own error bar,
    the band was taken about the wrong centre, which is exactly the failure a
    half-range invites."""
    import math
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import run_trapping_channels as T
    from rb5s6s import config as C
    from run_geometry_design import ramp_moments

    lam12, a12 = T._leg(*T.LINES_6S[0][:2])
    lam32, a32 = T._leg(*T.LINES_6S[1][:2])
    b12 = a12 / (a12 + a32)
    s12 = T._sigma_peak_cm2(lam12, a12, 2, 2)
    m = ramp_moments(C.W0_MEASURED_M, 0.225, 2.2e-3)
    f_ex = (m["sat_w"] / 2.0) / (1.0 + m["sat_w"])
    z_r = math.pi * C.W0_MEASURED_M ** 2 / 993.4e-9
    v_beam = math.pi * C.W0_MEASURED_M ** 2 * (2.0 * z_r) * 1e6

    for r in _rows("trapping_channels.csv"):
        if r["quantity"] != "halo_reexcitation" or not r.get("err_hi"):
            continue
        t_c = float(r["key"].strip("TC"))
        pt = float(r["value"])
        lo, hi = T.halo_band(t_c, f_ex, b12, s12, v_beam)
        assert lo - 1e-12 <= pt <= hi + 1e-12, (
            f"{t_c} C: point {pt} outside its band {lo} to {hi}")
        # ASYMMETRIC, so the two ends are stored separately. A symmetric err
        # was the first version and reconstructed [0.39, 1.75] at 130 C where
        # the band is [0.49, 1.85]: the point sits at a 2 mm standoff, the
        # band runs over 1 to 5 mm, and the halo is not linear in between.
        assert not r["err"], (
            "a symmetric err on an asymmetric band says the wrong interval")
        assert float(r["err_lo"]) == pytest.approx(pt - lo, rel=1e-3)
        assert float(r["err_hi"]) == pytest.approx(hi - pt, rel=1e-3)


def test_the_cascade_sum_rule_is_in_the_committed_csv():
    """Every leg ratio is exactly 8/9 or 4/9, and every line has a blocked
    intermediate level. Both are the content of figure 28, so if the producer
    ever stops reproducing them the figure is quietly wrong."""
    rows = _rows("cascade_branching.csv")
    ratios = {r["key"]: float(r["value"]) for r in rows
              if r["quantity"].startswith("leg_ratio_")}
    assert len(ratios) == 4, "expected four lines"
    for r in rows:
        if r["quantity"] == "leg_ratio_5P12":
            assert float(r["value"]) == pytest.approx(8 / 9, rel=1e-6)
        if r["quantity"] == "leg_ratio_5P32":
            assert float(r["value"]) == pytest.approx(4 / 9, rel=1e-6)
    blocked = [r for r in rows
               if r["quantity"] == "resolved_branch_5P32"
               and float(r["value"]) == 0.0]
    assert len(blocked) == 4, (
        "each of the four lines feeds exactly one 5P3/2 level that cannot "
        f"reach the undriven ground level, found {len(blocked)}")
