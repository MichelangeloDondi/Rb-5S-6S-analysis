"""M23 joint two-session Stark fit: the committed record and its premises.

The module itself needs the excluded prehistory tree and ~1 h, so these
tests check (1) the committed results CSV is internally consistent, (2) the
dnu_floor coarsening the module relies on is harmless, (3) the module
degrades gracefully without the excluded, and (4) the gamma_coll prior it
uses reproduces the archive's own beta_self x N chain.
"""

import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.linefit import _shared_profile_grid  # noqa: E402

CSV = C.RESULTS_DIR / "stark_joint.csv"


def rows():
    return list(csv.DictReader(open(CSV)))


def val(quantity, key):
    for r in rows():
        if r["quantity"] == quantity and r["key"] == key:
            return float(r["value"])
    raise KeyError((quantity, key))


# ---------------------------------------------------------------------------
# the committed record
# ---------------------------------------------------------------------------

def test_csv_exists_and_has_headline():
    assert CSV.exists(), "run scripts/run_stark_joint.py (needs excluded)"
    ub = val("kappa_ub95", "primary")
    assert 0.0 < ub < 60.0
    assert abs(val("S0_225mW_ub95", "primary") - ub * 0.225) < 1e-3
    assert abs(val("S0_270mW_ub95", "primary") - ub * 0.270) < 1e-3


def test_bound_tighter_than_m4e():
    """The whole point of M23: the full-profile fit must beat the 20-number
    width fit, else the module has no reason to exist."""
    m4e = None
    p = C.RESULTS_DIR / "stark_sweep.csv"
    for r in csv.DictReader(open(p)):
        if r["quantity"] == "S0_225mW_ub95_profile":
            m4e = float(r["value"])
    assert m4e is not None
    assert val("S0_225mW_ub95", "primary") < m4e


def test_no_detection_claim():
    """kappa_min's preference over kappa=0 must stay below detection
    strength; if a future rerun pushes it past 9 (3 sigma), the NULL
    framing of every doc that cites this file is wrong and must change."""
    assert val("dchi2_kappa0", "primary") < 9.0


def test_campaign_only_and_joint_bounds_are_same_order():
    """A subset bound need not be weaker than the joint bound: adding
    sessions tightens a profile bound only when the added data disfavour
    kappa, and the rehearsal mildly PREFERS a positive shift, so in the
    true local minimum the joint bound sits looser than the campaign-only column
    (addendum 24 logs it). The stuck-chain record had the opposite
    ordering, and an earlier version of this test asserted it as if it
    were a law. What must actually hold is that the two constructions
    describe the same physics: within a factor 4 of each other, in
    either direction."""
    joint = val("kappa_ub95", "primary")
    camp = val("kappa_ub95_camponly", "robustness")
    assert camp < 4.0 * joint, (camp, joint)
    assert joint < 4.0 * camp, (camp, joint)


def test_the_two_full_subsets_lie_below_the_nominal_prediction():
    """The primary and campaign-only bounds sit below the predicted S0.

    RENAMED AND RESCOPED 2026-08-27. This test was called
    `test_every_subset_lies_below_the_nominal_prediction` and its docstring
    called that "the load-bearing claim of C3f: ... whichever subset carries
    the weight". **The record retracts exactly that**:
    `docs/PREREGISTRATION_RESULTS.md` says the statement that every subset
    requires a lower intensity is withdrawn, and `S0_225mW_ub95_drop4192` =
    0.366 sits ABOVE the prediction. The test stayed green only because it
    excused the drop-4192 arm in a clause and read `pred` from the stale
    0.348 cell. A test whose NAME asserts a retracted proposition will revive
    it, so the name now says what the body checks: two subsets, not every
    one. The drop-4192 arm is covered by
    `test_the_leave_one_out_arms_are_checked_against_the_threshold` below.

    `pred` is READ from the CSV's own `S0_225mW_pred` row (v3.0.0: this used
    to be a 0.59 literal, hand-typed at the old 50 um prior, and went stale
    the moment the priors moved without this test noticing)."""
    pred = val("S0_225mW_pred", "prediction")
    assert val("S0_225mW_ub95", "primary") < pred
    assert val("kappa_ub95_camponly", "robustness") * 0.225 < pred


def test_direction_indifference():
    """The seeded 2026-08-02 run resolved the earlier warm-up ARTIFACT: the
    merged pointwise-min across cold and seeded chains gives 13.27 (priors
    pair; the wing pair sits at 24.84), verified by recomputation from the
    run log. The threshold is 30: generous against these converged values,
    seven orders below the 190k chi2 scale, and far below the 17.8k a
    warm-up failure produces, so a regression to non-convergence still
    fails loudly. The ARTIFACT branch stays as a self-disabling guard in
    case a future run re-tags the row."""
    row = next(r for r in rows()
               if r["quantity"] == "direction_dchi2_max" and r["key"] == "robustness")
    if row.get("status") == "ARTIFACT":
        assert float(row["value"]) > 1000.0, (
            "tagged ARTIFACT but the value is small -- retag and re-enable "
            "the strict check")
        return
    assert float(row["value"]) < 30.0


def test_the_leave_one_out_arms_are_checked_against_the_threshold():
    """The leave-one-out arms, measured against 2.706 and not against zero.

    REPLACES `test_lopo_no_single_peak_drives` on 2026-08-27. That test's
    NAME asserted the proposition the record has since withdrawn, and its
    body could not have caught the defect: it asserted only positivity, and
    only at the legacy kappa = 2.62 checkpoint, which sits far above the
    predicted coefficient. Positivity was never the test. The threshold is
    2.706, and the arms straddle it: bracketed to the value the constants
    later gave, 4121 clears at both ends, 4154 and 4207 fail at both ends,
    and 4192 straddles the threshold. No count is quotable.

    This test pins the COMMITTED ROWS so they cannot silently revert, and pins the
    2.62 checkpoint separately as the convergence check it actually is.

    NOTE THE REFERENT. The committed `lopo_dchi2_pred` rows were evaluated at
    whatever `KAPPA_PRED` the constants gave at run time, which is 1.545, the
    pre-adjudication value. This record's own predicted coefficient is now
    1.618, where each arm would sit higher by roughly the amount the full
    profile rises over that interval, about half a unit. The count below
    threshold is therefore stated at 1.545 and is provisional until the
    five-hour refit runs."""
    below = [pk for pk in ("4121", "4154", "4192", "4207")
             if val("lopo_dchi2_pred", pk) < 2.706]
    assert sorted(below) == ["4154", "4192", "4207"], (
        f"the committed leave-one-out arms below 2.706 changed: {below}. "
        f"This pins the COMMITTED ROWS at the pre-adjudication kappa_pred of "
        f"1.545; it is not a claim that the record summarises them as a "
        f"count, which it does not, because the arms are separate "
        f"likelihoods and carrying them to 1.618 leaves 4192 inside the "
        f"profile's own scatter of the threshold. If the refit has run, "
        f"restate the finding rather than re-seeding this list.")
    # the legacy checkpoint, which is a convergence check and speaks to
    # nothing about the exclusion at the prediction
    for pk in ("4121", "4154", "4192", "4207"):
        assert val("lopo_dchi2_262", pk) > 0.0


def test_saturation_fitted_linear():
    """The detector-linearity receipt: both Vsat >> the ~1 V signals."""
    assert val("Vsat_camp", "nuisance") > 10.0
    assert val("Vsat_reh", "nuisance") > 10.0


def test_pilot_rate_scale_in_band():
    """The pilot axis borrows the campaign rate through a scale bounded to
    [0.9, 1.1]; a posterior AT either bound would mean the width-licensed
    assumption failed and the pilot is pulling the axis, not riding it."""
    s = val("pilot_rate_scale", "nuisance")
    assert 0.905 < s < 1.095, s


def test_session_20250704_rates_sane():
    """~4x slower than the campaign's ~0.0426 MHz/ms, consistent across
    peaks (same generator setting; the spread is the anchor's softness)."""
    r = [val("reh_rate", pk) for pk in ("4121", "4154", "4192", "4207")]
    assert all(0.005 < x < 0.02 for x in r)
    assert max(r) / min(r) < 1.25


def test_gc_posterior_within_prior():
    """The posterior must not rail at zero (the failure the prior exists
    to prevent) nor wander far above its prior. Peak 4192 carries the 26
    pilot traces on top of its campaign rows, so its likelihood is the
    one entitled to pull against a campaign-derived prior: in the true
    local minimum it settles 4.7 prior sigmas high (addendum 24 logs it), and it
    gets a wider leash for that stated reason. The other three peaks
    stay on the campaign-only leash."""
    import re
    for r in rows():
        if r["quantity"] == "gamma_coll_post":
            post = float(r["value"])
            m = re.search(r"prior ([\d.]+)\+/-([\d.]+)", r["unit"])
            mu, sig = float(m.group(1)), float(m.group(2))
            assert post > 0.05, "gamma_coll railed at zero despite the prior"
            leash = 6.0 if r["key"] == "4192" else 4.0
            assert abs(post - mu) < leash * sig, (r["key"], post, mu, sig)


# ---------------------------------------------------------------------------
# the premises
# ---------------------------------------------------------------------------

def test_dnu_floor_equivalence():
    """M23 runs the profile builder at dnu_floor=2e-2. Against the 1e-3
    default the profile must agree to well under the campaign's per-point
    noise (5e-3 of peak at SNR 193) even at the nastiest corner the
    optimizer visits (sigma_laser at its 0.05 bound, s0 on)."""
    for gc, sl, s0 in ((0.5, 1.0, 0.0), (6.0, 2.0, 0.6), (4.0, 0.05, 1.5)):
        g1, p1 = _shared_profile_grid(gc, sl, 3.0, s0, "gaussian")
        g2, p2 = _shared_profile_grid(gc, sl, 3.0, s0, "gaussian",
                                      dnu_floor=2e-2)
        d = np.abs(np.interp(g1, g2, p2) - p1).max() / p1.max()
        assert d < 5e-5, (gc, sl, s0, d)


def test_graceful_without_the_outside_trees(tmp_path, monkeypatch):
    """Without the prehistory tree the module must exit 0 and change
    nothing (the committed CSV is the record)."""
    import run_stark_joint as M
    monkeypatch.setattr(M, "SESSION_20250704", tmp_path / "absent")
    assert M.main() == 0


def test_gc_prior_matches_beta_self_chain():
    import run_stark_joint as M
    from rb5s6s.density import number_density_cm3
    pri = M.gc_priors()
    n130 = float(number_density_cm3(np.array([130.0]))[0]) / 1e12
    for r in csv.DictReader(open(C.RESULTS_DIR / "beta_self.csv")):
        mu, sig = pri[r["peak"]]
        assert abs(mu - float(r["beta_self"]) * n130) < 1e-9
        assert abs(sig - float(r["beta_self_err"]) * n130) < 1e-9
