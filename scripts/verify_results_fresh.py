#!/usr/bin/env python3
"""
Do the committed result CSVs still match what their producers generate?

WHY THIS EXISTS. On 2026-07-25 the beta_self producer was corrected: a variant
it had labelled a "cross-session" comparison is not one, and the script now says
so in as many words. Its output was never regenerated. For two days
results/beta_self_probe.csv carried the retracted label while the script that
writes it carried the retraction, and the whole battery stayed green -- because
every test read the CSV, and the CSV was self-consistent. Nothing compared it
against the code.

That is a defect class the existing guards cannot see. tests/test_figures_fresh
catches a stale FIGURE by embedding a fingerprint of the CSVs in each PNG, so a
figure drawn from old numbers is detectable. Nothing plays that role one level
up: a CSV drifting from its own producer is invisible.

WHAT THIS DOES. Re-runs each producer into the real results/ directory, diffs
what appears against what was committed, and puts the committed files back --
always, including on failure. Numeric cells compare with a relative tolerance
(fits are iterative; the last digit is not meaningful), string cells compare
exactly, which is what catches a stale label. The `status` column is ignored
because annotate_results_status.py adds it last, after every producer has run.

WHAT IT DOES NOT COVER. The heavy fitting producers (run_linefit,
run_beta_self, run_global_fit, run_stark_sweep and the rest of the C-series) are
not in the default set: they take minutes and need the raw traces, so a checkout
without data_raw/ cannot run them at all. Pass --all to include them where the
traces exist. The default set is the cheap producers, which is a partial answer
-- but the file that actually drifted is in it.

    python scripts/verify_results_fresh.py          # cheap producers
    python scripts/verify_results_fresh.py --all    # everything, needs raw traces
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# Producer -> the CSVs it writes. Cheap enough to re-run in a test.
CHEAP = {
    # reads only the provenance declarations in docs/notes/ and counts them;
    # milliseconds, no traces, and deliberately checkable because the whole
    # point of the file is that the gap it measures is graded like any number.
    "run_unregenerated_claims": ["unregenerated_claims.csv"],
    # pure quadrature over the model line, a few seconds, no traces
    "run_cumulant_window_check": ["cumulant_window_check.csv"],
    "make_twin_term_census": ["twin_term_census.csv"],
    "run_kernel_identifiability": ["kernel_identifiability.csv"],
    # a Fisher forecast over five rungs per lever, milliseconds, no traces.
    "run_onf_lever_ranking": ["onf_lever_ranking.csv"],
    # three closed-form tables: a root of the HE11 characteristic equation at
    # three diameters, one quadrature of the Poynting flux, and a lookup of
    # the transit kernel factors. Well under a second and it reads no traces.
    "run_guided_mode_tables": ["guided_mode_tables.csv"],
    # reads two committed CSVs and does arithmetic; seconds.
    "run_kernel_budget": ["kernel_budget.csv"],
    # reads the vapour-pressure chain, the van der Waals anchor and the
    # committed stark_joint.csv; milliseconds. Cheap on purpose: every row it
    # writes used to be a digit typed into prose, and four of them were wrong.
    "run_collisional_shift_bound": ["collisional_shift_bound.csv"],
    # inverts the committed kappa profile against the stated geometry
    # priors; seconds. Cheap on purpose: the number it emits was headed
    # for eight reader-facing surfaces with no row behind it.
    "run_delta_alpha_posterior": ["delta_alpha_posterior.csv"],
    "run_orthogonal_levers": ["orthogonal_levers.csv"],
    "run_onf_candidate": ["onf_candidate.csv"],
    "run_cooperative_channel": ["cooperative_channel.csv"],
    "run_polarisation_bound": ["polarisation_bound.csv"],
    "run_skew_scaling": ["skew_scaling.csv"],
    "run_noise": ["noise_model.csv"],
    "run_ruler": [
        "ruler_traces.csv",
        "ruler_blocks.csv",
        "ruler_campaign.csv",
        # These two are the same run_ruler invocation's 4th and 5th outputs and
        # cost nothing extra to check, ruler_rate_model.csv via
        # rb5s6s.rate_model.write_models called at run_ruler.py:443.
        "ruler_nlmap.csv",
        "ruler_rate_model.csv",
    ],
    "run_tooth_scatter": ["ruler_tooth_scatter.csv"],
    "run_blackbody_channels": ["blackbody_channels.csv"],
    "run_cavity_scan": ["cavity_scan_integrals.csv"],
    "run_laser_epoch": ["laser_epoch.csv"],
    "run_qc": ["qc_metrics.csv"],
    "run_trapping_channels": ["trapping_channels.csv"],
    "run_wavemeter_reconstruction": ["wavemeter_reconstruction.csv"],
    "run_trim_report": ["trim_report.csv"],
    "run_sigma_laser_sharing": ["sigma_laser_sharing.csv"],
    "run_polarizability": ["polarizability.csv"],
    "run_modelform": ["modelform.csv"],
    "run_amplitude_ratios": ["amplitude_ratios.csv"],
    "run_transit_mc": ["transit_mc.csv"],
    "run_sharing_bic": ["sharing_bic.csv"],
    "run_resolving_power": ["resolving_power.csv"],
    "run_stark_centres": ["stark_centres.csv"],
    "run_laser_history": ["laser_history.csv", "laser_history_structure.csv"],
    "run_fringe_tail": ["fringe_tail.csv"],
    "run_window_attribution": ["window_attribution.csv"],
    "run_centre_fisher": ["centre_fisher.csv"],
}

# Minutes each, and they need data_raw/ traces.
EXPENSIVE = {
    # 1.7 s, but it refits 16 conditions from the raw traces, so it belongs
    # with the producers a clone without data_raw cannot run.
    "run_band_excess": ["band_excess.csv"],
    # 13 s, and it refits all 32 canonical conditions at six fit windows from
    # the raw traces, so like run_band_excess it belongs with the producers a
    # clone without data_raw cannot run.
    "run_fit_window_scan": ["fit_window_scan.csv"],
    # about two minutes of Monte-Carlo over two estimators at four
    # configurations, deterministic under its fixed seed. No traces needed,
    # but far too slow for the cheap set.
    "run_estimator_duel": ["estimator_duel.csv"],
    # 24 Monte-Carlo datasets per configuration through synthetic_traces and
    # fit_condition, about three minutes, deterministic under its fixed seed.
    "run_campaign_twin_forecast": ["campaign_twin_forecast.csv"],
    # three presets x three waist points x two fitter variants through
    # forecast_precision, about four minutes, deterministic under crc32
    # seeds. The scenario layer's end-to-end proof.
    "run_scenario_forecast": ["scenario_forecast.csv"],
    # 2000 multi-condition fits at ~1.05 s each, about five minutes on eight
    # lanes. Deterministic despite being Monte-Carlo: every trial's seed is its
    # index, so the CSV reproduces exactly and IS checkable rather than merely
    # re-runnable.
    # eight multi-condition fits on real traces, a few minutes.
    "run_kernel_k3": ["kernel_k3.csv"],
    # reads two committed CSVs and does arithmetic; seconds.
    "run_kernel_k5": ["kernel_k5.csv"],
    # 32 conditions refitted once in the G arm, then a weighted joint
    # regression and a leave-one-out over it. A few minutes.
    # re-runs the C3d profile-likelihood scan three times, about a minute,
    # and needs only committed CSVs. Its --emit flag writes the C3d half
    # only: the joint factor needs trees outside this repository and is
    # recorded as a classification rather than a digit.
    # a small Monte-Carlo over synthetic traces, seconds, no raw data. Its
    # truth is READ from linefit_conditions.csv rather than chosen, and its
    # seed is fixed, which is the whole repair: the run it replaces recorded
    # neither and could not be reproduced by anyone.
    "run_twin_span_sweep": ["twin_span_sweep.csv"],
    "run_quantisation_check": ["quantisation.csv"],
    "run_twin_realism": ["twin_realism.csv"],
    "run_saturation_probe --emit": ["saturation_companion.csv"],
    "run_kernel_k8": ["kernel_k8.csv"],
    "run_kernel_k7": ["kernel_k7.csv"],
    "run_kernel_worlds": ["kernel_worlds.csv"],
    # 32 conditions fitted three ways (two arms plus a synthetic control)
    # with a 1000-draw permutation null, plus a leave-one-out over every
    # condition. MEASURED at 8.75 s wall on 2026-08-22, from a clean worktree
    # at HEAD, reproducing the committed CSV byte for byte. This comment
    # previously said about twenty minutes, which is wrong by two orders of
    # magnitude and had been used to budget a re-run. The permutation null
    # flips signs on residuals that are already computed, so it costs almost
    # nothing next to the fits. It stays in EXPENSIVE because that map is
    # about which producers the cheap freshness path may run, not about
    # wall-clock alone.
    "run_kernel_k4": ["kernel_k4.csv"],
    # nine synthetic worlds at five hundred trials, about eight minutes.
    # Deterministic despite being Monte-Carlo: every trial is seeded by its
    # index, so the CSV reproduces exactly. It sat in CHEAP for one commit
    # and timed the freshness check out at nine hundred seconds, leaving
    # nineteen CSVs regenerated and unannotated.
    "run_fibre_twin": ["fibre_twin.csv"],
    "run_laser_kernel": ["laser_kernel.csv"],
    "run_kernel_headline": ["kernel_headline.csv"],
    "run_linefit": ["linefit_conditions.csv"],
    # noise_law_swap.csv is this same run's third output, free to check here.
    "run_beta_self": ["beta_self.csv", "beta_self_probe.csv", "noise_law_swap.csv"],
    "run_centre_stark": ["centre_stark.csv"],
    "run_projections": ["projections.csv"],
    "run_wing_check": ["wing_check.csv"],
    "run_lever_crosscheck": ["lever_crosscheck.csv"],
    "run_full_dataset_fit": ["full_dataset_fit.csv"],
    "run_global_dataset_fit": ["global_dataset_fit.csv"],
    "run_global_fit": ["global_fit.csv"],
    "run_stark_sweep": ["stark_sweep.csv"],
    "run_power_sweep": ["power_sweep.csv"],
    "run_amplitude_trapping": ["amplitude_trapping.csv"],
    "run_model_ladder": ["model_ladder.csv"],
    "run_identifiability": ["identifiability.csv", "identifiability_profile.csv"],
    "run_coverage": ["coverage.csv"],
}


# Deliberately OUT of both dicts, with the reason. Nothing else may be absent:
# tests/test_freshness_covers_every_result.py fails if a committed CSV appears
# in none of the three. The point is that a coverage gap must be a written
# decision rather than an omission nobody noticed. Before this registry existed,
# 19 of 46 committed CSVs were unchecked and nothing said so.
UNCOVERED = {
    "transit_additivity.csv": (
        "run_transit_additivity.py performs fifteen convolutions on a 600,000 "
        "point grid and takes minutes, so it is not in the cheap set. It is "
        "deterministic and depends on no raw trace, so `--all` would cover it "
        "at that cost; it is listed here rather than there because the "
        "quantity it computes is a property of the kernel and moves only when "
        "rb5s6s.fibre does, which the fibre tests already guard."),
    "commit_sweep.csv": (
        "run_commit_sweep.py counts the samples the joint fit loads at each "
        "commit of a historical range, so it needs BOTH excluded-session "
        "trees and a git worktree per commit. Without the trees each commit's "
        "own code returns early and leaves its committed CSV in place, which "
        "reads as a perfect reproduction, so a freshness comparison here "
        "would be worse than vacuous. The file exists because the numbers in "
        "it were previously typed into the ledger by hand."
    ),
    "stark_joint.csv": (
        "run_stark_joint.py declares ~5 h single-process runtime over three "
        "sessions and 172 traces, and its evening-session arm needs the "
        "excluded 2025-07-04 tree. Without that tree it prints what is missing "
        "and exits 0, so a freshness comparison would be vacuous rather than "
        "green. This is the most-cited uncovered file, appearing in 26 "
        "documents, so the gap is stated here rather than left implicit."
    ),
    "global_dataset_fit_norulers.csv": (
        "the second arm of M25, produced by _m25_norulers.py against the same "
        "private working copies as its partner. The partner "
        "global_dataset_fit.csv IS checked, which covers the shared machinery."
    ),
    "morning_ruler.csv": (
        "run_morning_ruler.py needs the campaign-morning excluded tree, which "
        "is private and read in place. Not runnable in any ordinary checkout, "
        "so the committed CSV stands as the only available record."
    ),
    "cascade_branching.csv": (
        "run_zeeman_depletion.py needs an optional dependency that the default "
        "install does not provide, so the producer is absent from a plain "
        "environment rather than merely slow."
    ),
}


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# Iterative fits do not converge bit-identically across numpy versions, and CI
# runs three (3.9-minimum, 3.9-latest, 3.11-latest). Measured spread on the
# committed set, 2026-07-29: amplitude_ratios err_stat 3.2e-4 relative,
# laser_history offset_err 5.5e-5, modelform chi2 1.8e-5, noise a_V 2.8e-5,
# ruler block chi2 3.0e-5. A 1e-6 tolerance therefore fails on every CI job
# while passing locally, which is a flaky guard and worse than none. 5e-3 sits
# an order above the observed spread and still catches any change that means
# anything. The sharp edge of this check is the STRING comparison anyway -- a
# stale label is what actually drifted -- and that stays exact.
# RECALIBRATED 2026-08-11. The 2026-07-29 spreads above were measured across
# numpy versions that all shared ONE np.convolve implementation. numpy 2.5
# replaced it (measured on this machine: 10x faster on the 9000-point
# convolution this whole lineshape model is built from), and a different
# algorithm rounds differently. Re-measured across numpy 1.26.4, 2.0.2 (the
# environment the committed CSVs were produced in) and 2.5.2, the largest
# well-conditioned drift is 1.2e-2. 5e-3 no longer covers that.
#
# 2e-2 is chosen against what the guard is FOR. Its own note says a real change
# to rb5s6s.stark moves these by tens of percent, so 2e-2 keeps a factor of 5
# to 50 of margin against a change that means something, while sitting above
# arithmetic that means nothing. The STRING skeleton comparison stays exact,
# which is where this check's real sharpness lives.
NUMERIC_RTOL = 2e-2

# One column cannot hold any fixed tolerance, and it is worth naming rather
# than hiding in the default: dBIC is a DIFFERENCE of two BICs of order 1e4, so
# cancellation multiplies a 1e-15 input perturbation by ~1e4. Observed 1.4e-1
# across the three numpy versions. The conclusion it carries does not move:
# |dBIC| < 2 is "no preference between Voigt and Lehmann" and it reads 0.38 to
# 0.44 everywhere.
# Measured on 2026-08-11 by re-running all 16 producers under numpy 2.5.2 and
# recording EVERY differing column rather than the first (_differs returns on
# the first, which is right for a guard and useless for calibrating one). Of
# 2421 columns that moved at all, exactly SIX moved by more than 2e-2, and they
# belong to only two families. Both are quantities this record already declines
# to quote, which is the reassuring part: the arithmetic is unstable precisely
# where the physics was already declared unidentifiable.
_COLUMN_RTOL = {
    # THE DEGENERATE SPLIT. full_gauss and full_exp are the Gaussian and
    # exponential widths of the three-component "full" model form, fitted
    # against a total width that constrains only their combination. This is
    # the degeneracy docs/RESEARCH_DECISIONS.md 1 refuses to quote as physics
    # and fig10 exists to draw: the split moves freely along the direction the
    # observable does not see, so a different rounding of the same convolution
    # lands it somewhere else on the same contour. Observed 1.3e-1; the total
    # width and chi2_full, which ARE well conditioned, move by under 5e-3 in
    # the same runs and keep the default.
    "full_gauss": 0.25,
    "full_exp": 0.25,
    # CATASTROPHIC CANCELLATION. dBIC is a difference of two BICs of order 1e4,
    # so a 1e-15 perturbation of the profile is multiplied by ~1e4. Observed
    # 1.4e-1 across numpy 1.26.4, 2.0.2 and 2.5.2. The conclusion it carries
    # does not move: |dBIC| < 2 is "no preference between Voigt and Lehmann",
    # and it reads between 0.38 and 0.93 everywhere.
    "dBIC_voigt_minus_lehmann": 0.30,
    # RESIDUAL SKEW OF A NEARLY SYMMETRIC FIT. resid_skew is the third moment
    # of fit residuals whose symmetric part cancels, so like dBIC above it is a
    # small difference of large sums, and the cells where the skew is nearest
    # zero are the ones whose relative move is largest.
    #
    # CALIBRATED BY A FULL-COLUMN SWEEP on 2026-08-19, not from a first
    # difference, because `_differs` returns on the first disagreement per file
    # and a tolerance set from that undercounts. Across all 20 rows:
    #
    #   resid_skew      max 7.5e-2, median 1.8e-3, 2 of 20 cells over 2e-2
    #   resid_skew_err  max 5.5e-2, median 3.7e-3, 2 of 20 cells over 2e-2
    #   chi2_red        max 1.4e-3      fwhm  max 1.5e-11   (default is ample)
    #
    # So the column is quiet almost everywhere and loud on two cells, which is
    # the cancellation signature rather than a moved measurement. 0.15 keeps a
    # factor of two over the observed maximum, matching the headroom dBIC
    # carries. These columns exist only in power_sweep.csv.
    "resid_skew": 0.15,
    "resid_skew_err": 0.15,
}

# LONG-FORMAT FILES PUT EVERY QUANTITY IN ONE COLUMN, so a column tolerance
# cannot single one out: 24 committed CSVs carry a `value` column, and four of
# them are bounds. These two tables key on (csv name, the row's `quantity`
# field) instead, so the loosening reaches exactly the unstable quantity and
# nothing else. Calibrated 2026-08-19 by running --all under BOTH the pinned
# environment of record (numpy 2.5.0) and the current venv (2.5.2):
#
#   condition_number read 389.7 committed, 438.2 pinned, 345.1 unpinned. It is
#   the eigenvalue ratio of the (gamma_coll, sigma_laser, transit) covariance,
#   whose own unit string reads ">>1 = degenerate". A ratio built on a
#   near-zero eigenvalue moves at the tens-of-percent level between LAPACK
#   builds, and committing any one of the three values would encode a build
#   accident. The conclusion it carries, "the split is degenerate", is the
#   same at all three.
#
#   wide_dchi2 is a raw delta-chi2 map over the wide profile grid. Observed
#   3.3e-2 on single cells between environments, different cell each run.
_ROW_QUANTITY_RTOL = {
    # Cells of the wide profile map that sit ABOVE the pin floor still live on
    # the multi-optimum surface the map exists to draw, so their per-cell
    # values move between builds while the map's shape does not. Observed
    # 4.6e-2 on a single cell, a different cell each run.
    ("identifiability_profile.csv", "wide_transit"): 0.10,
    # wide_dchi2 is a raw delta-chi2 map over the wide profile grid, observed
    # moving 3.3e-2 on single cells between environments, a different cell each
    # run. This is a per-quantity tolerance and not a per-file one: the sibling
    # quantities in the same file keep the default.
    ("identifiability_profile.csv", "wide_dchi2"): 0.10,
}

# EXPECTED-INSTABILITY ALLOWLIST, dated, per (file, quantity), WITH A REASON.
# A tolerance raised to the largest move ever seen is a detector tuned to its
# own signal: it can no longer fail on that move or anything smaller. So the
# tight default STAYS and specific known-unstable quantities are listed here
# instead, which keeps a genuinely NEW move able to fire.
#
# The justification is no longer an assertion. docs/notes/campaign_only_stark_profile.md
# documents a pooled likelihood surface carrying more than one local optimum,
# and the 2026-08-19 anchored re-reading of its pinned run shows independent
# starts landing 4.66 to 26.29 in chi-square above the production optimum. The
# identifiability files MAP that surface, so their per-cell values are expected
# to move between linear-algebra builds while the conclusion they carry, that
# the split is degenerate, does not.
_EXPECTED_INSTABILITY = {
    # PER FILE, with the wildcard quantity "*", because THE INSTABILITY ROVES.
    # Three independent runs under the environment of record fired on a
    # DIFFERENT quantity each time: condition_number, then corr, then
    # worst_constrained_sigma in identifiability.csv; wide_transit twice at
    # different cells, then zoom_gc, in the profile. Entries keyed to single
    # quantities chase a moving target and would have to be extended after
    # every run, which is how an allowlist becomes a rubber stamp nobody reads.
    #
    # The claim being made is about the FILES rather than about a threshold:
    # both map a likelihood surface that docs/notes/campaign_only_stark_profile.md
    # documents as carrying more than one local optimum, and the 2026-08-19
    # anchored re-reading measured independent starts landing 4.66 to 26.29 in
    # chi-square above the production optimum. A map of an ill-conditioned
    # surface has cells whose last digits are set by where an optimiser
    # stopped, and the map's SHAPE, which is what these files are read for, is
    # identical across all three runs.
    #
    # WHAT THIS DOES NOT EXEMPT, and the reason it is not a blanket pass:
    # string cells still compare exactly, so a renamed quantity or a changed
    # unit still fails; the row count still has to match, so a structural
    # change still fails. Only numeric drift within these two DIAGNOSTIC files
    # is forgiven.
    ("identifiability.csv", "*"): (
        "2026-08-19, three runs. Maps the (gamma_coll, sigma_laser, transit) "
        "degeneracy, whose own unit strings read '>>1 = degenerate'. Every "
        "numeric cell rests on a near-zero eigenvalue or on where an optimiser "
        "stopped in a valley the observable does not constrain."
    ),
    ("identifiability_profile.csv", "*"): (
        "2026-08-19, three runs. The per-cell profile map of the same surface, "
        "1857 cells, a different one moving each run. The bound the map "
        "delivers is stable; individual cells are not."
    ),
}


def _instability_note(csv_name: str, quantity: str) -> str | None:
    """The dated reason a cell is allowed to move, or None if it is not.

    A "*" quantity marks a whole file as expected-unstable. That is a stronger
    exemption than a per-quantity one and is used only where the instability
    has been observed to ROVE between quantities, which per-quantity entries
    cannot track.
    """
    return (_EXPECTED_INSTABILITY.get((csv_name, quantity))
            or _EXPECTED_INSTABILITY.get((csv_name, "*")))


# Rows whose own committed unit string declares a pin floor: two values both
# under it are two spellings of "pinned at the bound", so they compare equal.
# This is the file's OWN threshold rather than a number chosen here.
_ROW_QUANTITY_FLOOR = {
    ("identifiability_profile.csv", "wide_transit"): 0.02,
}

# WHETHER A CELL IS ZERO IS A QUESTION ABOUT ITS COLUMN, not about an absolute
# constant. ruler_traces h_m2 runs from 7.7e-37 to 0.31 with a median of 4e-3,
# and 8.7 per cent of its rows sit below 1e-10: those are comb teeth that are
# ABSENT, railed to zero by the fit, whose remaining digits are optimizer noise
# and carry no information. Comparing two of those relatively is meaningless.
#
# A global floor cannot express that. Set it low (1e-20) and absent teeth still
# read as disagreements; set it high (1e-10) and the blackbody channel rates,
# which are genuinely of order 1e-12 per second, get silently declared zero.
# So the floor is RELATIVE TO THE COLUMN'S OWN SCALE: a cell smaller than this
# fraction of its column's median magnitude is not a small measurement, it is
# a zero.
ZERO_FRACTION_OF_COLUMN = 1e-6


def _column_scales(rows: list[dict]) -> dict:
    """Median absolute value per numeric column, for the zero test above."""
    import statistics
    out = {}
    for k in (rows[0] if rows else {}):
        vals = []
        for r in rows:
            try:
                f = abs(float(r.get(k, "")))
            except (TypeError, ValueError):
                continue
            if f > 0.0:
                vals.append(f)
        if vals:
            out[k] = statistics.median(vals)
    return out


def _same_but_for_numbers(a: str, b: str, rtol: float) -> bool:
    """True when two strings differ only in embedded numbers, within rtol.

    The skeleton (everything that is not a number) must match EXACTLY, so a
    renamed field or a changed formula still fails. Only the numbers are
    allowed to drift, and only by the same tolerance a numeric column gets.
    """
    num = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
    if num.sub("#", a) != num.sub("#", b):
        return False
    na, nb = num.findall(a), num.findall(b)
    if len(na) != len(nb):
        return False
    for x, y in zip(na, nb):
        fx, fy = float(x), float(y)
        if fx == fy:
            continue
        if abs(fx - fy) > rtol * max(abs(fx), abs(fy), 1e-300):
            return False
    return True


# ---------------------------------------------------------------------------
# Rule 19.7, EXTENDED 2026-08-20. A difference is read in units of the
# quantity's OWN error wherever the producer emits one.
#
# On 2026-08-20 this script reported drifts of up to 13 per cent and they read
# as the most serious possible finding about the record. In units of each
# value's committed error the worst move anywhere was 0.081 sigma. The 13 per
# cent came from a parameter whose error at that condition is 1.43 on a value
# of 0.41, a condition `resolving_power.csv` already publishes as
# CANNOT_RESOLVE. A relative-difference check reads the curvature of an
# unconstrained likelihood, not the reproducibility of a pipeline, so it fires
# LOUDEST on exactly the quantities the record has declined to quote.
#
# The error columns were sitting in the same rows, unused. This is the fix.
SIGMA_TOL = 0.25
"""How far a value may move, in units of its own committed error, and still
count as reproducing. Deliberately tight: the 2026-08-20 worst case was
0.081, and a genuine code change moves a well-conditioned number by far more
than a quarter of its error."""


def _paired_error(row: dict, col: str) -> float | None:
    """The committed error beside `col` in the same row, or None.

    Two conventions live in results/: a `value` column paired with `err`, and
    a named column paired with `<name>_err`. Both are read here, and anything
    else returns None so the caller falls back to the relative tolerance.
    """
    for cand in ((col + "_err"), ("err" if col == "value" else None)):
        if not cand or cand not in row:
            continue
        try:
            e = float(row[cand])
        except (TypeError, ValueError):
            return None
        return e if e > 0.0 else None
    return None


def _differs(committed: list[dict], fresh: list[dict], rtol: float = NUMERIC_RTOL,
             csv_name: str = ""):
    """Return a short description of the first meaningful difference, or None."""
    if len(committed) != len(fresh):
        return f"row count {len(committed)} committed vs {len(fresh)} fresh"
    scales = _column_scales(committed)
    for i, (a, b) in enumerate(zip(committed, fresh)):
        keys = (set(a) | set(b)) - {"status"}      # annotator adds status last
        qty = a.get("quantity", "")
        row_floor = _ROW_QUANTITY_FLOOR.get((csv_name, qty))
        allowed = _instability_note(csv_name, qty)
        for k in sorted(keys):
            va, vb = a.get(k, ""), b.get(k, "")
            if va == vb:
                continue
            col_rtol = _ROW_QUANTITY_RTOL.get((csv_name, qty),
                                              _COLUMN_RTOL.get(k, rtol))
            try:
                fa, fb = float(va), float(vb)
            except (TypeError, ValueError):
                # A NUMBER INSIDE A STRING is still a number. sharing_bic's
                # "unit" column embeds its own effective sample size, as
                # "...k=241, N_eff=13853", so an N_eff that moved by 2 in
                # 13853 failed an EXACT string comparison and read as a stale
                # label. Compare the words exactly and the embedded numbers
                # numerically, which keeps the sharp edge this check relies on
                # (a changed label still fails) without pretending a count is
                # text. The proper fix is for that producer to write N_eff as
                # its own numeric column; until then this stops a schema
                # defect from masquerading as a reproducibility failure.
                if _same_but_for_numbers(va, vb, col_rtol):
                    continue
                return f"row {i} column {k!r}: committed {va!r} vs fresh {vb!r}"
            zero = scales.get(k, 0.0) * ZERO_FRACTION_OF_COLUMN
            if abs(fa) <= zero and abs(fb) <= zero:
                continue                      # both zero, for this column
            if row_floor is not None and abs(fa) < row_floor and abs(fb) < row_floor:
                continue          # both under the row's own declared pin floor
            scale = max(abs(fa), abs(fb))
            if scale == 0.0:
                continue
            if fa != fb and abs(fa - fb) > col_rtol * scale:
                if allowed:
                    continue          # dated, reasoned, in _EXPECTED_INSTABILITY
                err = _paired_error(a, k)
                sigma = abs(fa - fb) / err if err else None
                if sigma is not None and sigma <= SIGMA_TOL:
                    continue      # inside its own error bar, so it reproduces
                shown = f"{abs(fa - fb) / scale:.1e} relative"
                if sigma is not None:
                    shown = f"{sigma:.3f} sigma of its own error, {shown}"
                return (f"row {i} column {k!r}: committed {fa!r} vs fresh {fb!r} "
                        f"({shown})")
    return None


def _committed(name: str, dest: Path) -> bool:
    """Write results/<name> AS COMMITTED AT HEAD into dest. Reading the working
    copy instead would compare a dirty tree against itself and pass -- which is
    exactly the blind spot this script exists to close, so it must not have it."""
    proc = subprocess.run(["git", "show", f"HEAD:results/{name}"],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    dest.write_text(proc.stdout)
    return True


def verify(producers: dict) -> list[str]:
    """Re-run each producer and report CSVs that no longer match what is
    COMMITTED. The working copies are restored unconditionally -- this must
    never leave the tree dirty."""
    stash = Path(tempfile.mkdtemp(prefix="results_committed_"))
    working = Path(tempfile.mkdtemp(prefix="results_working_"))
    problems: list[str] = []
    try:
        for f in RESULTS.glob("*.csv"):
            shutil.copy2(f, working / f.name)        # to put back afterwards
            _committed(f.name, stash / f.name)       # to compare against

        for script, outputs in producers.items():
            proc = subprocess.run([sys.executable, f"scripts/{script}.py"],
                                  cwd=ROOT, capture_output=True, text=True)
            if proc.returncode != 0:
                tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
                problems.append(f"{script}.py exited {proc.returncode}: {tail[0]}")
                continue
            for name in outputs:
                fresh, committed = RESULTS / name, stash / name
                if not committed.is_file():
                    problems.append(f"{name}: produced but not committed at HEAD")
                    continue
                d = _differs(_rows(committed), _rows(fresh), csv_name=name)
                if d:
                    problems.append(f"{name} drifted from {script}.py -- {d}")
    finally:
        for f in working.glob("*.csv"):
            shutil.copy2(f, RESULTS / f.name)
        shutil.rmtree(stash, ignore_errors=True)
        shutil.rmtree(working, ignore_errors=True)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="include the heavy fitting producers (needs data_raw/)")
    args = ap.parse_args()

    producers = dict(CHEAP)
    if args.all:
        if not (ROOT / "data_raw" / "p_sweep").is_dir():
            print("--all needs the raw traces, which this checkout does not have")
            return 2
        producers.update(EXPENSIVE)

    problems = verify(producers)
    n = sum(len(v) for v in producers.values())
    if problems:
        print(f"{len(problems)} of {n} committed CSVs no longer match their producer:")
        for p in problems:
            print(f"  {p}")
        print("\nRe-run the producer and commit its output, then re-run "
              "annotate_results_status.py to restore the status column.")
        return 1
    print(f"all {n} committed CSVs match a fresh run of their producer "
          f"({len(producers)} producers checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
