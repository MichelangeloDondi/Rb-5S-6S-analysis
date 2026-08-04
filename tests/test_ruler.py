"""
Closure tests for the M2 ruler core (rb5s6s/ruler.py).

Before a single real ruler is fit, the comb machinery must recover KNOWN
tooth spacings injected into campaign-like synthetics: warm bright combs,
cold dim combs (init fallback path), suppressed carriers, missing outer
teeth, and block combination with propagated errors.
"""

from __future__ import annotations

import numpy as np

import pytest

from rb5s6s import config as C
from rb5s6s import ruler as RU
from rb5s6s.ruler import (QUARANTINE_REASONS, combine_block, estimate_delta_acf,
                          fit_comb, fit_comb_free_centers, top_three_verdict,
                          validated_comb_fit)

T_MS = np.arange(2000) * 0.5 - 500.0
TRUE_DELTA = 147.3


def synth_comb(delta=147.3, t0=150.0, w=55.0,
               heights=(0.02, 0.09, 0.06, 0.09, 0.02),
               base=0.005, noise=0.004, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    v = np.full_like(T_MS, base)
    for n, h in zip(range(-2, 3), heights):
        x = 2.0 * (T_MS - (t0 + n * delta)) / w
        v = v + h / (1.0 + x * x)
    return v + rng.normal(0.0, noise, len(T_MS))


def synth_folded_comb(delta=147.3, t0_frac=-0.6, apex_frac=0.8, w=55.0,
                      heights=(0.004, 0.02, 0.09, 0.06, 0.09, 0.02, 0.004),
                      base=0.005, noise=0.004, seed=C.RNG_SEED, fold=True):
    """A seven-slot comb plus the retrace mirror the triangular sweep makes.

    Past the ramp apex the scan re-crosses the same frequencies in reverse, so
    every tooth ALREADY PASSED reappears reflected about the apex. Teeth after
    the apex have not been crossed yet and do not mirror; mirrors landing
    outside the acquisition window are not recorded. Both are enforced here, so
    the injector produces the fold the instrument produces and not a
    symmetric caricature of it.

    Positions are given in units of the tooth spacing: `t0_frac` places the
    carrier relative to the window centre and `apex_frac` places the apex
    relative to the carrier. The defaults are the pre-registered pathology, in
    which the mirror of an inner tooth occupies an OUTER slot at a smaller
    radius than that slot's own position, so the rigid grid contracts to reach
    it. Pass `fold=False` for the same comb with no apex in the window.
    """
    t0 = t0_frac * delta
    centres = [t0 + n * delta for n in range(-3, 4)]
    rng = np.random.default_rng(seed)
    v = np.full_like(T_MS, base)
    for c, h in zip(centres, heights):
        v = v + h / (1.0 + (2.0 * (T_MS - c) / w) ** 2)
    if fold:
        apex = t0 + apex_frac * delta
        for c, h in zip(centres, heights):
            if c >= apex:                       # not crossed before the turn
                continue
            m = 2.0 * apex - c
            if not (T_MS[0] <= m <= T_MS[-1]):  # mirror falls outside the window
                continue
            v = v + h / (1.0 + (2.0 * (T_MS - m) / w) ** 2)
    return v + rng.normal(0.0, noise, len(T_MS))


SEEDS = (C.RNG_SEED, 1, 2, 3, 4, 5, 6, 7)


def test_acf_init_finds_spacing():
    got = estimate_delta_acf(T_MS, synth_comb())
    assert not got["fallback"]
    assert abs(got["delta_ms"] - 147.3) < 4.0


def test_warm_comb_recovery_and_pull():
    # Across seeds: |delta_fit - truth| must stay within ~3 reported sigmas
    # and the reported error itself must be sub-ms for bright combs.
    pulls = []
    for seed in range(1, 9):
        f = fit_comb(T_MS, synth_comb(seed=seed))
        assert f["delta_err_ms"] < 1.5
        pulls.append((f["delta_ms"] - 147.3) / f["delta_err_ms"])
    pulls = np.abs(pulls)
    assert pulls.max() < 3.5, pulls
    assert pulls.mean() < 1.5, pulls  # errors not wildly over/under-stated


def test_suppressed_carrier_no_bias():
    # HWP trick: carrier much weaker than sidebands must not bias delta.
    f = fit_comb(T_MS, synth_comb(heights=(0.02, 0.09, 0.015, 0.09, 0.02)))
    assert abs(f["delta_ms"] - 147.3) < 1.0


def test_missing_outer_teeth_no_bias():
    f = fit_comb(T_MS, synth_comb(heights=(0.0, 0.09, 0.06, 0.09, 0.0)))
    assert abs(f["delta_ms"] - 147.3) < 1.0


def test_cold_comb_fallback_path_converges():
    # Cold-block regime: teeth ~3x noise; ACF init may fall back — the fit
    # must still land within a few ms of truth.
    f = fit_comb(T_MS, synth_comb(heights=(0.004, 0.0085, 0.006, 0.008, 0.004),
                                  noise=0.0016, seed=3))
    assert abs(f["delta_ms"] - 147.3) < 4.0


def test_free_centers_recover_linear_comb():
    # On a perfectly linear comb the freed centers must sit at t0 + n*Δ, so
    # their departures (the nonlinearity-map input) are consistent with zero.
    v = synth_comb(delta=147.3, t0=150.0)
    base = fit_comb(T_MS, v)
    fc = fit_comb_free_centers(T_MS, v, base)
    assert len(fc["n"]) >= 3
    for n, c, e in zip(fc["n"], fc["centers_ms"], fc["center_err_ms"]):
        predicted = base["t0_ms"] + n * base["delta_ms"]
        assert abs(c - predicted) < max(3.0, 3.5 * e), (n, c, predicted, e)


def test_free_centers_detect_injected_nonlinearity():
    # Warp the axis quadratically: teeth placed at physical positions that
    # curve away from a straight ruler. The freed centers must reproduce the
    # curvature (departure grows toward the window edges), not flatten it.
    rng = np.random.default_rng(C.RNG_SEED)
    t0, d, curv = 150.0, 147.3, 4e-4  # ms per (n^2)
    centers = [t0 + n * d + curv * (n * d) ** 2 for n in range(-2, 3)]
    v = np.full_like(T_MS, 0.005)
    for c, h in zip(centers, (0.02, 0.09, 0.06, 0.09, 0.02)):
        v = v + h / (1.0 + (2.0 * (T_MS - c) / 55.0) ** 2)
    v = v + rng.normal(0.0, 0.004, len(T_MS))
    base = fit_comb(T_MS, v)
    fc = fit_comb_free_centers(T_MS, v, base)
    # the outermost freed tooth must show a clearly nonzero departure
    departs = [c - (base["t0_ms"] + n * base["delta_ms"])
               for n, c in zip(fc["n"], fc["centers_ms"])]
    assert max(abs(min(departs)), abs(max(departs))) > 2.0


def test_block_combination_scatter_inflation():
    fits = [fit_comb(T_MS, synth_comb(t0=150.0 + drift, seed=seed))
            for seed, drift in zip((1, 2, 3, 4, 5), (-15, -5, 0, 5, 15))]
    blk = combine_block(fits)
    assert abs(blk["delta_ms"] - 147.3) < 0.6
    assert blk["delta_err_ms"] <= min(f["delta_err_ms"] for f in fits)
    # inject one inconsistent trace: the combined error must GROW
    bad = dict(fits[0]); bad["delta_ms"] += 5.0
    blk2 = combine_block(fits[1:] + [bad])
    assert blk2["delta_err_ms"] > blk["delta_err_ms"]
    assert blk2["block_chi2_red"] > 3.0


# --------------------------------------------------------------------------
# TOOTH-INDEXING VALIDITY (docs/notes/ruler_validity_and_trim_prereg.md)
# --------------------------------------------------------------------------
# The comb fit assigns slot k by proximity to the window centre and never looks
# at amplitude, so a retrace mirror sitting in an outer slot is fitted as a
# tooth and the rigid grid distorts to reach it, moving the spacing and with it
# every MHz-denominated number in the repository. These tests pin the
# detection, the bias sign at each apex phase, the recovery, the absence of
# false positives, the case the archive's fold-robustness argument is right
# about, and the known limitation that keeps the verdict from gating today.
#
# The verdict lands NOT GATING (config.RULER_TOP3_GATED is False), so tests
# about what the ladder DOES pass gated=True explicitly. Tests about what the
# pipeline does are left on the default.


def test_folded_comb_fails_top_three():
    """THE mandatory test: the injected fold must be caught. If this passes on
    a folded comb the whole validity stage is decoration."""
    for seed in SEEDS:
        f = fit_comb(T_MS, synth_folded_comb(seed=seed))
        v = top_three_verdict(f["heights"], f["fit_rms"])
        assert v["verdict"] == "FAIL", (
            f"seed {seed}: a folded comb passed the top-three rule with ranks "
            f"{v['rank_m1']}/{v['rank_p1']} and heights "
            f"{[round(x, 4) for x in f['heights']]}")


def test_folded_comb_bias():
    """The bias direction is set by the APEX PHASE, and both signs occur.

    An earlier version of this test asserted one direction, from the argument
    that a mirror lands at a smaller radius than the slot it occupies so the
    grid contracts. That is true at one apex phase and not at others. A
    parallel measurement across apex positions found both signs, so the
    prediction of a single direction was withdrawn from the pre-registration
    before any recompute was adopted. What is pinned here is the sign PER
    PHASE, which is the falsifiable statement: a fold is not a wash, and each
    phase pushes the spacing one specific way.
    """
    for apex_frac, sign in ((1.3, -1), (1.7, +1)):
        for seed in SEEDS:
            folded = fit_comb(T_MS, synth_folded_comb(t0_frac=0.0,
                                                      apex_frac=apex_frac, seed=seed))
            clean = fit_comb(T_MS, synth_folded_comb(t0_frac=0.0,
                                                     apex_frac=apex_frac, seed=seed,
                                                     fold=False))
            shift = folded["delta_ms"] - clean["delta_ms"]
            assert np.sign(shift) == sign and abs(shift) > 1.0, (
                f"apex {apex_frac} seed {seed}: fold moved the spacing by "
                f"{shift:+.2f} ms, expected sign {sign:+d}")
            # and the rate moves the other way, which is the sign that reaches
            # every MHz-denominated number in the repository
            assert np.sign(6.25 / folded["delta_ms"] - 6.25 / clean["delta_ms"]) == -sign


def test_reindex_recovers_delta_on_a_folded_comb():
    """The ladder must return the TRUE spacing, not merely a passing verdict.
    A re-index that satisfies the rule while keeping the contracted grid is the
    failure this asserts against."""
    for seed in SEEDS:
        out = validated_comb_fit(T_MS, synth_folded_comb(seed=seed), gated=True)
        assert not out["quarantined"], f"seed {seed}: {out['quarantine_reason']}"
        assert out["top3_ok"]
        assert abs(out["delta_ms"] - TRUE_DELTA) < 1.0, (
            f"seed {seed}: ladder returned {out['delta_ms']:.2f} ms against a "
            f"true {TRUE_DELTA} ms (action {out['reindex_action']})")
        assert out["reindex_action"] != "none"
        assert out["n_refits"] <= C.RULER_REINDEX_MAX_TRIALS


# --- the 2026-08-04 amendment to the acceptance ceiling ---------------------
# Seven POPULATED slots, which is what the earlier calibration synthetics did
# not have. With five teeth in a seven-slot grid a one-slot relabel trades an
# empty slot for an empty slot and costs nothing, so the old tolerance of 1e-3
# of chi2_red looked ample. With seven teeth in a window that fits 6.8 of them
# the relabel always trades a populated slot and costs a real amount, and the
# old tolerance rejected the right answer. See
# docs/notes/ruler_validity_and_trim_prereg.md, amendment of 2026-08-04.

def synth_bessel_comb(t0_frac, seed=0, two_beta=1.62, carrier=1.57, peak=0.09,
                      w=55.0, base=0.005, noise=0.004, delta=TRUE_DELTA):
    """A seven-tooth comb under the repository's own amplitude law, placed
    `t0_frac` tooth spacings from the window centre. Around one whole spacing
    off centre, `estimate_t0`'s fold to the tooth nearest the window centre
    picks the wrong tooth and the comb is labelled one slot out."""
    from scipy.special import jv
    ks = np.arange(-3, 4)
    h = np.array([jv(k, two_beta) ** 2 for k in ks], dtype=float)
    h[ks == 0] *= carrier
    h = peak * h / h.max()
    t0 = t0_frac * delta + 0.5 * (T_MS[0] + T_MS[-1])
    rng = np.random.default_rng(seed)
    v = np.full_like(T_MS, base)
    for c, hh in zip(t0 + ks * delta, h):
        v = v + hh / (1.0 + (2.0 * (T_MS - c) / w) ** 2)
    return v + rng.normal(0.0, noise, len(T_MS))


# (seed, t0_frac) pairs found by scanning 336 clean seven-tooth mislabels: on
# each of these the OLD 1e-3 tolerance rejected the correct relabel, the ladder
# fell through to the excision rung, and the excision deleted a first-order
# tooth of 22 to 23 fit_rms while worsening chi2_red by 1.2 to 5.5 sigma. This
# is the defect seen on rulers_p/4154nm_eom_before_1.csv, on a synthetic whose
# answer is known.
_OLD_TOLERANCE_CASUALTIES = [(7, -1.00), (11, -0.75), (13, -1.25),
                             (5, 1.05), (15, 0.85), (22, 0.75)]


def test_acceptance_ceiling_accepts_a_clean_seven_tooth_relabel():
    """A clean one-slot mislabel with all seven slots populated must be rescued
    by the comb-phase rung and must keep its spacing. Nothing is contaminated
    here, so any excision is a deletion of real signal."""
    for seed, frac in _OLD_TOLERANCE_CASUALTIES:
        out = validated_comb_fit(T_MS, synth_bessel_comb(frac, seed=seed), gated=True)
        assert not out["quarantined"], (seed, frac, out["quarantine_reason"])
        assert out["reindex_action"] == "phase_shift", (
            f"seed {seed} frac {frac}: clean mislabel took "
            f"{out['reindex_action']!r} instead of a comb-phase relabel")
        assert abs(out["delta_ms"] - TRUE_DELTA) < 1.0, (seed, frac, out["delta_ms"])


def test_excision_rung_is_held_to_the_acceptance_ceiling():
    """The destructive rung must not be the loosest one. Excision deletes
    samples and pins a slot to zero, so a refit it worsens past the ceiling is
    not an answer. Asserted directly: on a clean comb no excision is taken, and
    on a genuine fold excision is still taken because there it IMPROVES the fit
    by tens of sigma."""
    npar = 3 + 7 + 2
    for seed, frac in _OLD_TOLERANCE_CASUALTIES:
        v = synth_bessel_comb(frac, seed=seed)
        first = fit_comb(T_MS, v)
        ceiling = first["chi2_red"] + max(
            C.RULER_REINDEX_CHI2_TOL * first["chi2_red"],
            RU.REINDEX_CHI2_NSIGMA * np.sqrt(2.0 / (first["n_fitted"] - npar)))
        out = validated_comb_fit(T_MS, v, gated=True)
        assert out["excised_k"] == "", (seed, frac)
        assert out["chi2_red"] <= ceiling, (seed, frac, out["chi2_red"], ceiling)
    for seed in SEEDS:
        out = validated_comb_fit(T_MS, synth_folded_comb(seed=seed), gated=True)
        assert out["reindex_action"] == "excision", (seed, out["reindex_action"])


def test_acceptance_ceiling_can_only_widen_the_original_tolerance():
    """The amendment is a widening, never a narrowing. The original relative
    tolerance stays in the ceiling as a floor, so no trace that the ladder
    relabelled before can stop being relabelled because of this change."""
    assert RU.REINDEX_CHI2_NSIGMA > 0.0
    for chi2, dof in ((0.5, 1988), (1.0, 1988), (3.0, 1988), (1.0, 500)):
        old = chi2 * C.RULER_REINDEX_CHI2_TOL
        new = max(chi2 * C.RULER_REINDEX_CHI2_TOL,
                  RU.REINDEX_CHI2_NSIGMA * np.sqrt(2.0 / dof))
        assert new >= old, (chi2, dof)


def test_clean_combs_all_pass_top_three():
    """Zero false positives. Every synthetic the closure suite already fits --
    bright, suppressed carrier, missing outer teeth, cold, and drifted phase --
    must come out of the ladder valid and unquarantined, with its spacing
    intact."""
    cases = {
        "bright": dict(),
        "suppressed carrier": dict(heights=(0.02, 0.09, 0.015, 0.09, 0.02)),
        "missing outer teeth": dict(heights=(0.0, 0.09, 0.06, 0.09, 0.0)),
        "cold": dict(heights=(0.004, 0.0085, 0.006, 0.008, 0.004),
                     noise=0.0016, seed=3),
    }
    for seed in SEEDS:
        cases[f"seed {seed}"] = dict(seed=seed)
    for drift in (-15, -5, 0, 5, 15):
        cases[f"drift {drift}"] = dict(t0=150.0 + drift, seed=1)
    for name, kw in cases.items():
        out = validated_comb_fit(T_MS, synth_comb(**kw), gated=True)
        assert out["top3_ok"] and not out["quarantined"], (
            f"clean synthetic {name!r} was rejected: verdict {out['verdict']}, "
            f"reason {out['quarantine_reason']!r}")
        assert abs(out["delta_ms"] - TRUE_DELTA) < 1.0, (name, out["delta_ms"])


def _bessel_comb_heights(two_beta, peak=0.09):
    """Tooth heights under the repository's own comb amplitude law: pure phase
    modulation gives A_k proportional to J_k(2 beta)^2, symmetric in k
    (rb5s6s/constants.py, TOOTH_SPACING_LASER_HZ)."""
    from scipy.special import jv
    h = np.array([jv(k, two_beta) ** 2 for k in range(-3, 4)])
    return (peak * h / h.max()).tolist()


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN LIMITATION of the top-three rule, and the reason it lands NOT "
    "gating. Above a modulation index 2*beta of about 2.7 the SECOND-order "
    "sidebands legitimately outrank the first, so a comb obeying the "
    "repository's own amplitude law fails a rule written to detect a defect. "
    "The rule is contradicting known physics here, not finding a fault. See "
    "the open question in docs/notes/ruler_validity_and_trim_prereg.md."))
def test_clean_bessel_comb_above_modulation_index_passes_top_three():
    for two_beta in (2.7, 3.0, 3.5, 4.0):
        v = top_three_verdict(_bessel_comb_heights(two_beta), fit_rms=0.004)
        assert v["verdict"] == "PASS", (two_beta, v)


def test_bessel_comb_below_modulation_index_passes_top_three():
    """The other side of the same boundary, so the limitation above is pinned
    as a boundary and not as a blanket failure: below 2*beta of about 2.7 the
    first-order sidebands are the tallest and the rule agrees with the law."""
    for two_beta in (1.0, 1.5, 2.0, 2.5):
        v = top_three_verdict(_bessel_comb_heights(two_beta), fit_rms=0.004)
        assert v["verdict"] == "PASS", (two_beta, v)


def test_verdict_lands_advisory_and_changes_no_number():
    """The switch that makes this landing safe. Ungated, the ladder still runs
    and records everything, but the fit OF RECORD is the plain fit, byte for
    byte, and nothing is quarantined. If this test fails, a diagnostic has
    silently become a gate and every MHz in the repository moved with it."""
    assert C.RULER_TOP3_GATED is False, (
        "the top-three verdict is now gating; that is an owner decision and it "
        "changes the campaign rate. See docs/notes/ruler_validity_and_trim_prereg.md")
    v = synth_folded_comb()
    plain = fit_comb(T_MS, v)
    out = validated_comb_fit(T_MS, v)
    assert out["delta_ms"] == plain["delta_ms"]
    assert out["heights"] == plain["heights"]
    assert out["quarantined"] is False and out["top3_gated"] is False
    # the ladder's own answer is still on the record
    assert out["quarantine_advised"] or out["reindex_action"] != "none"
    gated = validated_comb_fit(T_MS, v, gated=True)
    assert gated["delta_ms"] != plain["delta_ms"]
    assert out["delta_advised_ms"] == gated["delta_ms"]


def test_suppressed_carrier_passes_top_three():
    """The rule must NOT require k=0 to be tallest. The carrier was suppressed
    on purpose (the half-wave plate was tilted), so a carrier far below its own
    neighbours is the expected comb, not a defect."""
    heights = [0.004, 0.02, 0.09, 0.002, 0.09, 0.02, 0.004]   # k=0 near zero
    v = top_three_verdict(heights, fit_rms=0.004)
    assert v["verdict"] == "PASS", v
    out = validated_comb_fit(T_MS, synth_folded_comb(
        t0_frac=0.0, heights=tuple(heights), fold=False))
    assert out["top3_ok"] and out["reindex_action"] == "none", out["verdict"]


def test_unfixable_fold_quarantines_with_a_reason():
    """A fold the ladder cannot re-index is quarantined, and the reason comes
    from the closed vocabulary rather than free text."""
    for seed in SEEDS:
        out = validated_comb_fit(T_MS, synth_folded_comb(apex_frac=0.9, seed=seed),
                                 gated=True)
        assert out["quarantined"], f"seed {seed}: verdict {out['verdict']}"
        assert out["quarantine_reason"] in QUARANTINE_REASONS, out["quarantine_reason"]
        assert out["n_refits"] <= C.RULER_REINDEX_MAX_TRIALS


def test_railed_height_is_reported():
    """A slot the fit parks on its zero bound is COUNTED, not hidden. The
    railed outer slot is the fingerprint the ruler figure has to exclude on,
    and until now the heights were never written down at all."""
    out = validated_comb_fit(T_MS, synth_comb(heights=(0.0, 0.09, 0.06, 0.09, 0.0)))
    assert out["n_railed"] >= 1, out["heights"]
    assert sum(1 for h in out["heights"] if h <= 1e-9) == out["n_railed"]
    bright = validated_comb_fit(T_MS, synth_comb())
    assert bright["n_railed"] == 0, bright["heights"]


def test_apex_on_a_tooth_is_not_flagged():
    """The bounded-claim case. The archive's fold-robustness paragraph argues a
    fold preserves tooth SPACING. That argument is right exactly when the apex
    lands on a tooth, because every mirror then lands on another tooth slot.
    The rule must not fire there, or it would contradict a true statement."""
    for apex_frac in (-1.0, 1.0, 2.0):
        for seed in SEEDS:
            v = synth_folded_comb(t0_frac=0.0, apex_frac=apex_frac, seed=seed)
            f = fit_comb(T_MS, v)
            verdict = top_three_verdict(f["heights"], f["fit_rms"])
            assert verdict["top3_ok"], (
                f"apex on tooth {apex_frac:+.0f}, seed {seed}: flagged "
                f"{verdict['verdict']} with ranks "
                f"{verdict['rank_m1']}/{verdict['rank_p1']}")
            out = validated_comb_fit(T_MS, v, gated=True)
            assert out["reindex_action"] == "none" and not out["quarantined"]
            assert abs(out["delta_ms"] - TRUE_DELTA) < 1.0, out["delta_ms"]


def test_top_three_tie_tolerance_is_marginal_not_pass():
    """The one tolerance behaves as pre-registered: fourth place within one
    fit_rms of third is MARGINAL (a pass for the pipeline, a failure for figure
    eligibility), and further away than that is a FAIL."""
    #                k: -3    -2    -1     0     1     2     3
    near = [0.010, 0.030, 0.0295, 0.040, 0.050, 0.020, 0.005]
    assert top_three_verdict(near, fit_rms=0.004)["verdict"] == "MARGINAL"
    far = list(near)
    far[2] = 0.0295 - 10 * 0.004
    assert top_three_verdict(far, fit_rms=0.004)["verdict"] == "FAIL"
    assert top_three_verdict(near, fit_rms=1e-9)["verdict"] == "FAIL"


def _run_ruler_module():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "run_ruler", Path(__file__).resolve().parents[1] / "scripts" / "run_ruler.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NEW_TRACE_COLUMNS = [
    "h_m3", "h_m2", "h_m1", "h_0", "h_p1", "h_p2", "h_p3",
    "fit_rms", "resid_norm", "n_fitted", "t0_ms",
    "top3_ok", "top3_marginal", "rank_m1", "rank_p1", "n_railed", "verdict",
    "top3_gated",
    "reindex_action", "reindex_j", "excised_k", "n_refits", "delta_advised_ms",
    "quarantine_advised", "quarantined", "quarantine_reason",
    "trimmed", "trim_start_ms", "trim_end_ms", "trim_reason",
]


def test_ruler_traces_schema_covers_the_validity_record():
    """Schema guard. The seven heights are the reason this table exists in its
    new form: 105 traces by 7 slots is the matrix an amplitude model and any
    audit of the labelling have to be tested against, and it was recomputed and
    thrown away on every run until now. The producer must declare every column
    and must be able to fill every one it declares."""
    mod = _run_ruler_module()
    missing = [c for c in NEW_TRACE_COLUMNS if c not in mod.TRACE_HEADER]
    assert not missing, f"run_ruler.TRACE_HEADER lost columns: {missing}"

    out = validated_comb_fit(T_MS, synth_comb())
    row = mod.trace_row({"file": "x.csv", "repeat_idx": "1"},
                        "T", "4192", "110", "", out, 0.0425)
    assert sorted(row) == sorted(mod.TRACE_HEADER), (
        set(mod.TRACE_HEADER) ^ set(row))


def test_committed_ruler_traces_carry_the_validity_columns():
    import csv
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "results" / "ruler_traces.csv"
    if not p.exists():
        pytest.skip("results/ruler_traces.csv not present")
    header = next(csv.reader(open(p)))
    missing = [c for c in NEW_TRACE_COLUMNS if c not in header]
    assert not missing, (
        f"results/ruler_traces.csv predates the validity columns {missing}; "
        f"re-run scripts/run_ruler.py, stage the CSV, then redraw the figures")


# --------------------------------------------------------------------------
# The sweep-linearity bound quoted in fig8 and the prose must match the map.
# --------------------------------------------------------------------------
# Raised 2026-07-22: fig8's right panel showed a rightmost error bar of +/-0.74%
# under a title claiming "<=0.4%", which reads as the figure refuting itself.
# The bar is NOT anomalous (n=5, 0.9 sigma from the 1/sqrt(n) law, and its
# CENTRAL value is inside the band) -- but the sparse edge windows cannot test
# a bound their own errors exceed, so the claim belongs to the well-sampled
# windows and the number has to be the one they actually support.
def test_linearity_bound_matches_the_wellsampled_windows():
    import csv
    import sys
    import numpy as np
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    rows = list(csv.DictReader(open(root / "results" / "ruler_nlmap.csv")))
    n = np.array([int(r["n"]) for r in rows])
    dev = np.abs(np.array([float(r["rate_rel"]) for r in rows]) - 1.0)
    err = np.array([float(r["rate_rel_err"]) for r in rows])

    from make_figures import N_WELL_SAMPLED  # the split fig8 draws
    well = n >= N_WELL_SAMPLED
    assert well.sum() >= 5, "too few well-sampled windows to set a bound"
    # the quoted 0.3% must cover them, and not be loose by more than ~0.1%
    # (0.45% until 2026-08-01; the seven-tooth refit tightened the map)
    assert dev[well].max() <= 0.0030 + 1e-9, (
        f"a well-sampled window deviates {dev[well].max():.4%}, beyond the "
        f"quoted 0.3% -- update the bound in fig8, DATA.md, PAPER1_SKELETON "
        f"and make_results_ledger.py together")
    assert dev[well].max() > 0.0020, (
        "the bound is now loose; requote it nearer the data")
    # the sparse windows are the ones whose errors exceed the bound: that is
    # the whole reason they are drawn differently
    assert err[~well].max() > 0.0030, (
        "sparse-window errors no longer exceed the bound; the fig8 split by "
        "N_WELL_SAMPLED may no longer be warranted")


def test_fig8_legends_are_opaque():
    """rcParams sets legend.frameon False globally, which silently defeats
    framealpha and let plotted data show through fig8's legend text."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "scripts"
           / "make_figures.py").read_text(encoding="utf-8")
    for m in re.finditer(r"\.legend\(([^)]*framealpha[^)]*)\)", src):
        assert "frameon=True" in m.group(1), (
            "a legend asks for framealpha while legend.frameon is globally "
            f"False, so it draws no frame at all: {m.group(0)}")
