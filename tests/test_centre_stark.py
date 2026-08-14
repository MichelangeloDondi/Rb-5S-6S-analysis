"""M27: the centre-channel Stark coefficient from held-lock epochs.

Production-shape checks on the committed CSV, in the spirit of
test_morning_ruler.py: hold the record to its own construction rather than
re-deriving the numbers. This module's headline is a NEGATIVE finding (the
apparent pull is not robust -- case 3, reported as a bound), so most of these
tests pin the DIAGNOSTICS that earned that verdict, not a point estimate.
"""

import csv
import sys
from pathlib import Path

import pytest

from rb5s6s import config as C

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

CSV = C.RESULTS_DIR / "centre_stark.csv"
pytestmark = pytest.mark.skipif(not CSV.exists(), reason="centre_stark.csv not generated")


def rows():
    return list(csv.DictReader(open(CSV)))


def _one(quantity, key=None):
    r = rows()
    matches = [x for x in r if x["quantity"] == quantity and (key is None or x["key"] == key)]
    assert matches, f"no row for quantity={quantity!r} key={key!r}"
    assert len(matches) == 1, f"ambiguous: {len(matches)} rows for {quantity!r}/{key!r}"
    return matches[0]


def test_epoch_count_matches_the_record_not_the_brief():
    """The task brief asserted 5 multi-power epochs; the archive has 3 (the
    same 3 M21's docstring already reports). If this ever becomes 5, the
    archive changed and every downstream number here needs re-deriving."""
    r = _one("n_multi_power_epochs", "found")
    assert float(r["value"]) == 3.0, r["value"]


def test_all_three_epochs_present():
    r = rows()
    keys = {x["key"] for x in r if x["quantity"] == "epoch_kappa_transition"}
    assert keys == {"23_993.4207nm", "28_993.4154nm", "33_993.4121nm"}, keys


def test_multistart_agrees_on_every_epoch():
    """Addendum 20's lesson: an un-converged single start once manufactured
    two flagged anomalies from nothing. Every per-epoch fit here is
    cross-checked against a multi-start nonlinear refit."""
    for x in rows():
        if x["quantity"] == "epoch_kappa_transition":
            assert "multistart_agrees=True" in x["unit"], x


def test_combined_point_estimate_sits_outside_the_m23_bound():
    """This is why the module runs its diagnostics at all (case 2 territory
    on the raw numbers): the combined point estimate is well above the
    width-channel's 95% bound. The verdict test below is what matters --
    this just pins the fact that triggered it."""
    combined = float(_one("combined_kappa_transition", "primary")["value"])
    m23 = float(_one("kappa_ub95_m23", "reference")["value"])
    assert combined > m23, (combined, m23)


def test_leave_one_out_is_unstable():
    """The signature of a not-robust pull: its significance should not swing
    by more than a couple of sigma depending on which single epoch is
    dropped. If a future refit makes this STABLE, the case-3 verdict needs
    re-examining, not silently keeping the old bound."""
    loo = {x["key"]: (float(x["value"]), float(x["err"]))
           for x in rows() if x["quantity"] == "diag_leave_one_out"}
    assert set(loo) == {"drop_23", "drop_28", "drop_33"}, set(loo)
    sigmas = [abs(v) / e for v, e in loo.values()]
    assert max(sigmas) - min(sigmas) > 1.0, (
        f"leave-one-out sigmas {sigmas} no longer spread by >1 sigma -- the pull may "
        "have become robust; re-examine the case-3 verdict before trusting the old bound")


def test_a_zero_signal_control_reproduces_a_comparable_pull():
    """The decisive diagnostic: at least one genuinely single-power p_sweep
    epoch, given a SYNTHETIC fake power step (true Delta-power = 0), returns
    an apparent kappa_transition at least 2 sigma from zero -- the estimator
    manufactures signal from noise alone at a rate that matters. If this
    ever stops being true, the case-3 verdict (bound, not pull) needs
    re-deriving rather than assuming it still holds."""
    controls = [x for x in rows() if x["quantity"] == "control_epoch"]
    assert len(controls) >= 4, len(controls)
    sigmas = [abs(float(x["value"])) / float(x["err"]) for x in controls]
    assert max(sigmas) >= 2.0, sigmas


def test_verdict_is_case_3_bound_not_pull():
    r = _one("verdict", "case_3")
    assert r["value"] == "3", r["value"]
    assert r["status"] == "BOUND", r["status"]
    assert "not robust" in r["unit"], r["unit"]


def test_the_quoted_bound_is_far_weaker_than_the_width_channel():
    """Matches the established pattern (M20's retracted 7.3 MHz, M21's
    9.5-17.7 MHz): every centre-channel attempt on this archive lands far
    weaker than the width channel. Pinned at 5x so a silent tightening
    cannot slip the narrative without review."""
    bound = float(_one("kappa_ub95_centre", "primary")["value"])
    m23 = float(_one("kappa_ub95_m23", "reference")["value"])
    assert bound > 5.0 * m23, (bound, m23)


def test_drift_prior_matches_run_drift_settling():
    """The prior is quoted, not re-measured, here; pin the hard-coded
    literals against run_drift_settling.py's own headline numbers."""
    import run_centre_stark as m
    assert m.DRIFT_PRIOR_MEAN == pytest.approx(0.016)
    assert m.DRIFT_PRIOR_SIGMA == pytest.approx(0.009, abs=1e-6)


def test_drift_prior_docstring_citation_present():
    """A softer version of the check above that does not depend on exact
    docstring punctuation: the drift-settling module still states a
    positive, sub-0.03 MHz/min settled drift somewhere in its source."""
    import run_drift_settling as ds
    src = ds.__doc__ or ""
    assert "0.016" in src and "0.007" in src and "0.025" in src, (
        "run_drift_settling.py's docstring no longer quotes +0.016 [+0.007, +0.025] "
        "MHz/min -- the prior this module hard-codes needs re-verifying against it")
