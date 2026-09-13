"""The window-laws producer's rows carry the ordering the estimator rests on.

FAILURE MODE IF THIS FILE IS DELETED: the plan's reading that the window scan
separates the transit from the Lorentzian sum (their W-laws differ) and removes
the tilt (steeper than any physics term) would rest on one night's scratch
output, and a change to `windowed_cumulants` or `full_profile` that inverted
the ordering would ship unread. The numbers are read from the committed CSV,
never typed here; only the ORDERINGS and the bounds a sign change would break
are asserted.
"""
import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "window_laws.csv"


def _rows():
    if not CSV.is_file():
        pytest.skip("results/window_laws.csv not committed yet")
    return {(r["quantity"], r["window_mhz"]): r for r in csv.DictReader(CSV.open(encoding="utf-8"))}


def _v(rows, q, w=""):
    return float(rows[(q, w)]["value"])


def test_the_tilt_is_steeper_than_every_physics_term_on_k3():
    rows = _rows()
    tilt = _v(rows, "law_tilt_k3", "4-20")
    for term in ("transit", "lorentzian_sum", "gaussian_laser"):
        assert tilt > _v(rows, f"law_{term}_k3", "4-20") + 1.0, (
            f"the tilt's window law ({tilt}) is not steeper than {term}'s on k3; the scan cannot separate them")


def test_the_lorentzian_laser_form_shares_the_lorentzian_sums_law():
    rows = _rows()
    for n in (2, 4, 6):
        a = _v(rows, f"law_lorentzian_laser_form_k{n}", "4-20"); b = _v(rows, f"law_lorentzian_sum_k{n}", "4-20")
        assert abs(a - b) < 0.4, f"k{n}: a Lorentzian laser ({a}) and the Lorentzian sum ({b}) are one term for the widths, or gamma_l no longer absorbs laser_kind"


def test_the_transit_grows_slower_than_the_lorentzian_sum_in_k2():
    rows = _rows()
    assert _v(rows, "law_transit_k2", "4-20") < _v(rows, "law_lorentzian_sum_k2", "4-20"), (
        "a bounded kernel's second moment saturates while the Lorentzian's grows; the ordering inverted")


def test_the_even_ladder_keeps_most_of_the_transit_after_the_tilt():
    rows = _rows()
    assert _v(rows, "kept_transit_k6", "1.5-20") > 0.8
    assert _v(rows, "kept_transit_k2", "1.5-20") > 0.3


def test_correlated_noise_costs_information_and_the_white_form_is_the_floor():
    rows = _rows()
    white = _v(rows, "sigma_ln_transit_white", "1.5-20")
    for f in ("ar1_tau_int", "white_plus_wander"):
        assert _v(rows, f"sigma_ln_transit_{f}", "1.5-20") > white, f"{f} reads more precise than white noise, which no noise form can be"


def test_every_error_cell_has_two_significant_digits():
    rows = _rows()
    bad = []
    for (q, w), r in rows.items():
        e = r["err"].strip()
        if e:
            sig = e.lstrip("0.").replace(".", "")
            if len(sig.rstrip("0") or "0") > 2 and not e.endswith("0"):
                bad.append(f"{q}: {e}")
    assert not bad, "\n".join(bad)
