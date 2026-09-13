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
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# Producer -> the CSVs it writes. Cheap enough to re-run in a test.
CHEAP = {
    # measured 1.8 s and 0.5 s, needing no raw trace: they belong in the
    # every-pass set, and entering EXPENSIVE with no comment removed them from
    # the freshness canary that runs without --all.
    "run_moment_admission": ["moment_admission.csv"],
    "run_density_laws": ["density_laws.csv"],
    "run_four_peak_contrasts": ["four_peak_contrasts.csv"],
    "run_detection_budget": ["detection_budget.csv"],
    "run_ruler_tooth_shares": ["ruler_tooth_shares.csv"],
    # Closed form throughout, no traces and no RNG, so it reproduces exactly.
    "run_platform_twins": ["platform_twins.csv"],
    "run_sobol_acquisition": ["sobol_acquisition.csv"],  # <1 s, exact
    # reads only the provenance declarations in docs/notes/ and counts them;
    # milliseconds, no traces, and deliberately checkable because the whole
    # point of the file is that the gap it measures is graded like any number.
    "run_unregenerated_claims": ["unregenerated_claims.csv"],
    # pure quadrature over the model line, a few seconds, no traces
    "run_cumulant_window_check": ["cumulant_window_check.csv"],
    "make_twin_term_census": ["twin_term_census.csv"],
    # closed forms over the package's own geometry functions, under a second
    "run_waist_ladder": ["waist_ladder.csv"],
    "run_kernel_identifiability": ["kernel_identifiability.csv"],
    # a Fisher forecast over five rungs per lever, milliseconds, no traces.
    "run_onf_lever_ranking": ["onf_lever_ranking.csv"],
    "run_sweep_linearity": ["sweep_linearity.csv"],
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
    # Gate A: propagation only, no fitting, so it is milliseconds and belongs
    # here rather than in EXPENSIVE.
    "run_prediction_band": ["prediction_band.csv"],
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
    # seconds: one least-squares fit and closed forms, no raw trace and no
    # simulation. IT SAT IN EXPENSIVE FOR ONE GATE with this same comment
    # beside it saying it belonged here, which is a note contradicting its own
    # code and is why the gate of 2026-09-09 never checked it.
    "run_transition_ladder": ["transition_ladder.csv"],
}

# Minutes each, or needing data_raw/ traces, or both - everything the
# per-pass cheap set must not pay for.
EXPENSIVE = {
    # the kernel-inhomogeneity study: about two and a half minutes, measured,
    # not asserted. THIS COMMENT SAID "minutes rather than seconds" WHEN THE
    # PRODUCER TOOK TEN (2026-09-09): it was timed twice independently in
    # isolated clones, both at 9.9 s, while the wave's own brief said ten
    # seconds on the same page. It is minutes NOW only because the physics
    # findings of that day widened the frequency span fourfold and doubled the
    # axial grid, so the classification became true by accident after being
    # written false. It enters this map on the day it lands, because a results
    # file registered for annotation and absent from freshness is invisible
    # when it is MISSING, which is how a chapter came to cite a file nobody had
    # produced (A128).
    "run_kernel_inhomogeneity": ["kernel_inhomogeneity.csv"],
    # measured 43 s and 39 s, which is why these two stay here; two of the
    # producers registered beside them (moment_admission, ruler_tooth_shares)
    # went to CHEAP on their own measured cost and the twin-completeness one
    # is a first registration below.
    "run_fringe_rho_recovery": ["fringe_rho_recovery.csv"],
    "run_rf_saturation_ladder": ["rf_saturation_ladder.csv"],
    # measured 56 s through the producer alone and 61 s through verify()
    # (measured 2026-09-12), above the bar the two rows above set
    "run_polarizability_deep": ["polarizability_deep.csv"],
    "run_window_laws": ["window_laws.csv"],
    # reads raw traces, so it cannot run on a clone without data_raw/ and is
    # not SYNTHETIC_ONLY; measured 3 s.
    "run_twin_completeness": ["twin_completeness.csv"],
    # the digitiser scale: reads thirty-two raw traces and returns in seconds,
    # but it READS RAW TRACES so a public clone cannot regenerate it.
    "run_digitiser_scale": ["digitiser_scale.csv"],
    # about nine minutes on eight workers, twenty-three cells of four hundred
    # trace sets each through every physics layer, so it is re-run only under
    # --all. Synthetic throughout: it reads no raw trace.
    "run_three_channel_forecast": ["three_channel_forecast.csv"],
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
    # Monte-Carlo over the excursion-drift grid and both detection
    # branches, deterministic under its fixed seeds and needing no
    # traces, but far too slow for the cheap set's every-pass run.
    # ELEVEN TO THIRTEEN MINUTES sequentially, up from about three: the
    # grid gained six replicates per configuration on 2026-09-02 and
    # this dict is what `--all` re-runs, so the manual post-edit
    # freshness pass now costs that for this producer alone. Setting
    # RB5S6S_WORKERS brings it to under three minutes. Measured three
    # times on a ten-core machine that day, spanning 668 to 789 s
    # sequential and 153 to 170 s at six workers, the spread being
    # other load.
    "run_paired_reference_forecast": ["paired_reference_forecast.csv"],
    # 200 Monte-Carlo datasets per configuration through synthetic_traces
    # and fit_condition, about forty-six minutes measured 2026-09-02,
    # deterministic under its fixed seed. The trial count rose from 24 on
    # 2026-08-31 and this comment kept the old number and the old runtime
    # until the twin was timed: a gate reader budgeting three minutes for
    # a forty-six minute producer is how gates get killed.
    "run_campaign_twin_forecast": ["campaign_twin_forecast.csv"],
    # three presets x three waist points x two fitter variants through
    # forecast_precision, about fifty seconds sequential, deterministic under crc32
    # seeds. The scenario layer's end-to-end proof.
    "run_scenario_forecast": ["scenario_forecast.csv"],
    # two full closed-loop passes (base and gage-shifted), about eight
    # minutes, seed-pinned. Leg 1 of the twin validation.
    "run_twin_closed_loop": ["twin_closed_loop.csv"],
    "run_quantisation_crosscheck": ["quantisation_crosscheck.csv"],
    # fifteen configurations at a thousand law-weighted trials each on
    # eight workers, about forty minutes. Leg 2 of the twin validation.
    "run_coverage_grid": ["coverage_grid.csv"],
    # 432 cells at 2000 traces per S0 rung through the forecast path, about
    # twenty-nine minutes on eight workers, measured by timing ONE cell before
    # the grid was launched rather than guessed. Deterministic: every task is
    # seeded from its own cell coordinates and the cells are collected in
    # order, planted one worker against eight (`--plant`). The trace count is
    # capped by re-runnability, not by ambition: the deep configuration
    # measured that forty thousand traces leave the archive's own rung a
    # per-trace coin flip, so no affordable count makes it one here, and a
    # freshness entry nobody can afford to re-run is a dead check.
    "run_moment_power_map": ["moment_power_map.csv", "moment_power_map_rungs.csv"],
    # the deep configuration: 24 cells at forty thousand traces from the
    # archive's rung up, about ninety minutes on six workers, measured on
    # 2026-09-05; its wrapper sets the environment the map reads
    "run_moment_power_map_deep": ["moment_power_map_deep.csv", "moment_power_map_deep_rungs.csv"],
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
    "run_noise_floor_scaling": ["noise_floor_scaling.csv"],
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
    # BOTH of the next two early-return without writing when the
    # excluded session trees are absent, so on a checkout without them
    # each comparison reads the committed CSV against itself: green
    # because nothing ran, not because it matched. Verified by runtime
    # probe on 2026-09-02, on the OWNER'S OWN machine, where
    # ~/rb-2025-sessions/prehistory does not exist: exit 0, CSV md5
    # unchanged.
    #
    # This comment used to sit BETWEEN the two entries and describe
    # only the second. A reader scanning whether the first was covered
    # met a paragraph immediately under it describing exactly its
    # defect, and stopped looking. A comment between two entries
    # documents one of them and reassures about both.
    "run_full_dataset_fit": ["full_dataset_fit.csv"],
    # The workers seam's contract names this second file as its
    # enforcer, so that limit belongs here where a reader meets it.
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
    "power_time_sign_test.csv": (
        "run_power_time_sign_test.py reads the excluded 2025-07-04 and "
        "campaign-morning trees through run_stark_joint's loaders; without "
        "them it prints what is missing and exits 0, so a freshness "
        "comparison would be vacuous rather than green, exactly as for "
        "stark_joint.csv above."
    ),
    "global_dataset_fit_norulers.csv": (
        "the second arm of M25, produced by _m25_norulers.py against the same "
        "private working copies as its partner. The partner "
        "global_dataset_fit.csv is LISTED as checked, but that producer "
        "early-returns without writing when the excluded session trees are "
        "absent, so on such a checkout the comparison reads the committed "
        "file against itself and covers nothing. The shared machinery is "
        "genuinely checked only where those trees exist."
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
#   4.4e-2 on single cells between environments, different cell each run.
_ROW_QUANTITY_RTOL = {
    # Cells of the wide profile map that sit ABOVE the pin floor still live on
    # the multi-optimum surface the map exists to draw, so their per-cell
    # values move between builds while the map's shape does not. Observed
    # 4.6e-2 on a single cell, a different cell each run.
    ("identifiability_profile.csv", "wide_transit"): 0.10,
    # wide_dchi2 is a raw delta-chi2 map over the wide profile grid, observed
    # moving 4.4e-2 on single cells between environments, a different cell each
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
    """Write results/<name> AS STAGED into dest: the git INDEX, not the working
    tree and not HEAD.

    NOT THE WORKING TREE, which is what this docstring used to defend: reading
    the working copy would compare a dirty tree against itself and pass, the
    blind spot this script exists to close.

    **AND AN UNSTAGED HAND EDIT IS NOT CAUGHT HERE, which this docstring and
    the rule file both claimed until 2026-09-12.** Reproduced in an isolated
    clone: `_one` compares the producer's output against the
    INDEX blob, and the working tree's `results/` is read only for the mtime
    fingerprint, so a CSV edited by hand and left unstaged returns no drift.
    The only arm that ever used the working copy as an operand is
    `_serial_legacy`, and `LEGACY_SERIAL` is empty. What catches an unstaged
    edit is `targeted.sh`, which refuses to stamp while anything is unstaged,
    and the gate, which refuses to start without that stamp -- not this
    script. Its own `plant()` has no arm for the case, which is why the claim
    stood: arm 3 stales the INDEX side and asserts drift, and nothing ever
    hand-edited the working tree.

    NOT HEAD, which is where that defence went one step too far. A producer
    changed TOGETHER WITH its CSV cannot match HEAD's CSV by construction,
    because the change is the point, so grading against HEAD made the ordinary
    shape of a wave a guaranteed red at every gate until the commit landed.
    That is common-cause register entry 2, and it was eleven of the twelve gate
    failures measured across 7.7 hours of gate on 2026-09-11, none of them a
    defect. The index is what will BECOME the commit, and the commit is this
    repository's certification boundary.

    Conservative by construction: where nothing is staged for a path the index
    equals HEAD, so this differs from the old behaviour only in the case it
    exists to fix. It also closes a second hole -- a new CSV `git add`ed before
    the redraw, as the standing rule requires, is in the index and not at HEAD,
    and the old code called that "produced but not committed".

    FAILURE MODE: returns False when the path is in neither the index nor HEAD,
    which is an untracked new CSV that was never staged.
    """
    proc = subprocess.run(["git", "show", f":results/{name}"],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    dest.write_text(proc.stdout)
    return True


def _one(job):
    """Run ONE producer in a private results directory and report its drift.

    The directory is seeded with the COMMITTED CSVs, so a producer that reads
    another producer's output reads it as git holds it and never as this loop
    has just regenerated it. That removes an order dependence the serial
    version carried silently, and it is what makes the pool safe: no two
    producers share a file.
    """
    script, outputs, stash, root = job
    priv = Path(root) / script.split()[0]
    priv.mkdir(parents=True, exist_ok=True)
    for f in Path(stash).glob("*.csv"):
        shutil.copy2(f, priv / f.name)
    # ONE BLAS THREAD PER WORKER. Every other pooled producer here sets these,
    # and the rule file states the reason unconditionally: eleven threads per
    # worker read as a load of forty on ten cores on 2026-09-08. The first
    # version of this pool set none of them (2026-09-11).
    env = dict(os.environ, RB5S6S_RESULTS_DIR=str(priv),
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               OMP_NUM_THREADS="1")
    # THE SEED'S TIMESTAMP, so a producer that ignores the override is caught
    # LOUDLY. Without this the private copy stays as seeded, the comparison
    # measures the committed file against itself, and the check passes while
    # verifying nothing. The plant of 2026-09-11 found exactly that on its
    # first run, from a producer that built its path with os.path.join instead
    # of resolving it through the config.
    #
    # THE TEST IS THE MTIME AND NOT THE BYTES, and the difference is a false
    # positive this check carried against two producers. Comparing CONTENT
    # cannot separate "did not write" from "wrote correctly and
    # deterministically", because a producer that reproduces its committed CSV
    # byte for byte is doing exactly what this whole script exists to verify.
    # `moment_admission` and `ruler_tooth_shares` carry no timestamp and no
    # last-digit jitter, so they reproduced themselves exactly and were
    # accused of never having run. Stamping each seeded output to the epoch
    # and asking afterwards whether it moved tests the failure mode itself:
    # any real write updates the mtime whatever it writes, and a producer that
    # ignores the override leaves the sentinel untouched. The 2026-09-11 plant
    # still fires, because a producer writing elsewhere still never touches
    # this file.
    SENTINEL_MTIME = 0
    for o in outputs:
        if (priv / o).is_file():
            os.utime(priv / o, (SENTINEL_MTIME, SENTINEL_MTIME))
    seeded = {o: (priv / o).is_file() for o in outputs}
    # a registry key may carry CLI arguments after the script name
    # ("run_saturation_probe --emit"); the first full --all of 2026-08-31
    # found the join producing a filename with a flag inside it, unrunnable
    # for the whole life of the entry
    name_and_args = script.split()
    proc = subprocess.run(
        [sys.executable, f"scripts/{name_and_args[0]}.py", *name_and_args[1:]],
        cwd=ROOT, capture_output=True, text=True, env=env)
    problems = []
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
        return [f"{script.split()[0]}.py exited {proc.returncode}: {tail[0]}"]
    for name in outputs:
        fresh, committed = priv / name, Path(stash) / name
        if not committed.is_file():
            problems.append(f"{name}: produced but not staged (neither in the "
                            f"index nor at HEAD -- git add it)")
            continue
        if not fresh.is_file():
            problems.append(f"{name}: producer wrote nothing")
            continue
        if seeded.get(name) and fresh.stat().st_mtime == SENTINEL_MTIME:
            problems.append(
                f"{name}: {script.split()[0]}.py did not write into "
                f"RB5S6S_RESULTS_DIR, so this check verified nothing. Resolve "
                f"the output path through rb5s6s.config.RESULTS_DIR.")
            continue
        d = _differs(_rows(committed), _rows(fresh), csv_name=name)
        if d:
            problems.append(f"{name} drifted from {script}.py -- {d}")
    return problems


#: Producers that must still run the OLD way, serially against the live
#: `results/`, because they do not resolve their output through
#: `rb5s6s.config.RESULTS_DIR`.
#:
#: **It is empty, and the earlier prose around it claimed more than that.** It
#: said sixteen of the forty-seven bypassed and "All sixteen were migrated",
#: presented as a defended invariant. A count of the migration on 2026-09-11
#: gave: ten producers gained a resolved path and five gained only the
#: relpath repair, which is fifteen, and `run_kernel_inhomogeneity.py` still
#: builds its path by hand and was in neither group. **There was also an
#: `ISOLATED` set here whose docstring called itself the mechanism while
#: nothing consulted it**; it is deleted rather than wired, because what
#: actually protects the pool is the per-output seed-byte check and the
#: per-run live-tree fingerprint below, and those are detectors rather than
#: admission gates. A declared list that gates nothing is worse than none.
LEGACY_SERIAL: set[str] = set()



#: Producers PROVEN to resolve their output through `rb5s6s.config.RESULTS_DIR`
#: and therefore safe to run isolated and pooled. Membership is declared, never
#: inferred, and it is earned one producer at a time.
#:
#: **The other 16 of the 47 do not honour it** (2026-09-11, found by the plant's
#: own first full run): eleven build the path by hand and write into the live
#: tree whatever the environment says, and five call `relative_to(REPO_ROOT)` on
#: an output that is no longer under the repository and die. Migrating them is
#: mechanical and it is a wave of its own; until a producer is migrated it runs
#: the old way, serially, against the live directory.


def _serial_legacy(producers: dict) -> list[str]:
    """The pre-2026-09-11 path, for producers that still write the live tree.

    Kept verbatim in behaviour: stash the working copies, run each producer
    into `results/`, compare against the committed copies, restore. Its two
    known hazards are why the isolated path exists: a hard kill skips the
    restore, and a producer late in the loop reads its inputs as this loop has
    just regenerated them.
    """
    stash = Path(tempfile.mkdtemp(prefix="results_committed_"))
    working = Path(tempfile.mkdtemp(prefix="results_working_"))
    problems: list[str] = []
    try:
        for f in RESULTS.glob("*.csv"):
            shutil.copy2(f, working / f.name)
            _committed(f.name, stash / f.name)
        for script, outputs in producers.items():
            name_and_args = script.split()
            proc = subprocess.run(
                [sys.executable, f"scripts/{name_and_args[0]}.py",
                 *name_and_args[1:]],
                cwd=ROOT, capture_output=True, text=True)
            if proc.returncode != 0:
                tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
                problems.append(f"{script.split()[0]}.py exited {proc.returncode}: {tail[0]}")
                continue
            for name in outputs:
                fresh, committed = RESULTS / name, stash / name
                if not committed.is_file():
                    problems.append(f"{name}: produced but not staged (neither "
                                    f"in the index nor at HEAD -- git add it)")
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


def verify(producers: dict, workers: int | None = None) -> list[str]:
    """Re-run each producer and report CSVs that no longer match what is
    COMMITTED.

    **THIS NO LONGER TOUCHES `results/`.** Every producer runs against a
    private directory through `RB5S6S_RESULTS_DIR`, so the working tree is
    never written and never needs restoring. The stash-and-restore the serial
    version used had a standing hazard, that a hard kill skipped its `finally`
    and left the tree dirty, and that hazard is gone by construction rather
    than by remembering to check `git status` afterwards.

    Producers are independent once isolated, so they run in a pool. `workers`
    of 1 forces the serial path, which `--plant` uses to prove the two agree.
    """
    stash = Path(tempfile.mkdtemp(prefix="results_committed_"))
    root = Path(tempfile.mkdtemp(prefix="results_private_"))
    problems: list[str] = []
    # THE LIVE TREE'S FINGERPRINT BEFORE ANYTHING RUNS. The isolated path has
    # no stash-and-restore by design, so a producer that ignores the override
    # writes the real `results/` and nothing puts it back. On 2026-09-11 four
    # of them did exactly that and left five CSVs modified, which the per-output
    # guard reported but only AFTER the damage. This makes the damage itself a
    # reported problem, so a bypass can never be discovered by a later test
    # failing forty-two ways.
    live = {f.name: f.stat().st_mtime_ns for f in RESULTS.glob("*.csv")}
    try:
        for f in RESULTS.glob("*.csv"):
            _committed(f.name, stash / f.name)       # to compare against
        legacy = {k: v for k, v in producers.items()
                  if k.split()[0] in LEGACY_SERIAL}
        jobs = [(script, outputs, str(stash), str(root))
                for script, outputs in producers.items()
                if script.split()[0] not in LEGACY_SERIAL]
        if legacy:
            problems.extend(_serial_legacy(legacy))
        # THROUGH THE SEAM, never a fresh reading of the environment.
        # `rb5s6s.workers` exists because a contract stated in four places
        # drifts in three and is enforced in none, and the first version of
        # this pool was the fourth place (2026-09-11). An operator
        # setting RB5S6S_WORKERS=1 beside a gate now gets one.
        from rb5s6s.workers import n_workers
        n = workers if workers is not None else min(n_workers(), len(jobs))
        if n <= 1:
            for j in jobs:
                problems.extend(_one(j))
        else:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=n) as ex:
                for out in ex.map(_one, jobs):
                    problems.extend(out)
        now = {f.name: f.stat().st_mtime_ns for f in RESULTS.glob("*.csv")}
        touched = sorted(k for k in set(live) | set(now)
                         if live.get(k) != now.get(k))
        if touched:
            problems.append(
                "THE LIVE results/ WAS WRITTEN during an isolated verify, so a "
                f"producer ignored RB5S6S_RESULTS_DIR: {', '.join(touched)}. "
                "Restore them with `git restore results/` AND remove any new "
                "stray file with `git clean -f results/`, because `git restore` "
                "reverts tracked files and does not delete untracked ones, "
                "which it was proved on a planted bypassing producer. Then "
                "resolve those producers' output paths through "
                "rb5s6s.config.RESULTS_DIR.")
    finally:
        shutil.rmtree(stash, ignore_errors=True)
        shutil.rmtree(root, ignore_errors=True)
    return problems


def plant(subset=("run_waist_ladder", "run_platform_twins",
                  "run_transition_ladder")) -> int:
    """Probe the isolation, the pool, the detector and the write sentinel, on
    the real path.

    Four claims, two of them negatives, because a pooled verifier that
    silently stops detecting drift, or that accuses a deterministic producer
    of never running, is worse than a slow one. The fourth claim is the mtime
    sentinel of 2026-09-12: with that arm deleted the three older claims
    stayed green.
    """
    fails = []
    prod = {k: v for k, v in dict(CHEAP, **EXPENSIVE).items() if k in subset}
    if len(prod) < 2:
        print("plant: subset not in the registry", file=sys.stderr)
        return 1

    # 1. RESULTS/ IS NOT TOUCHED. The whole point of the override.
    before = {f.name: (f.stat().st_mtime_ns, f.stat().st_size)
              for f in RESULTS.glob("*.csv")}
    ser = verify(prod, workers=1)
    after = {f.name: (f.stat().st_mtime_ns, f.stat().st_size)
             for f in RESULTS.glob("*.csv")}
    if before != after:
        moved = sorted(k for k in before if before.get(k) != after.get(k))
        fails.append(f"results/ was written during a verify: {moved}")

    # 2. THE POOL AGREES WITH THE SERIAL PATH, exactly.
    par = verify(prod, workers=min(4, len(prod)))
    if sorted(ser) != sorted(par):
        fails.append(f"pool disagrees with serial: serial={sorted(ser)} "
                     f"pool={sorted(par)}")

    # 3. THE DETECTOR STILL FIRES. A stash whose committed copy has been
    #    altered must be reported as drift, or this verifier has become a
    #    green light that means nothing.
    import tempfile as _tf
    stash = Path(_tf.mkdtemp(prefix="plant_stash_"))
    root = Path(_tf.mkdtemp(prefix="plant_priv_"))
    try:
        for f in RESULTS.glob("*.csv"):
            _committed(f.name, stash / f.name)
        # a producer whose CSV is NEW in this commit has no committed copy to
        # stale, which the plant's own first run found; pick one that has.
        cand = [(k, o) for k in sorted(prod) for o in prod[k]
                if (stash / o).is_file()]
        if not cand:
            fails.append("no producer in the subset has a committed CSV to stale")
            cand = [(sorted(prod)[0], prod[sorted(prod)[0]][0])]
        script, target = cand[0]
        rows = (stash / target).read_text().splitlines()
        if len(rows) < 2:
            fails.append(f"{target} too short to stale")
        else:
            cells = rows[1].split(",")
            for k, c in enumerate(cells):
                try:
                    cells[k] = repr(float(c) * 2.0 + 1.0)
                    break
                except ValueError:
                    continue
            else:
                fails.append(f"{target} row 1 carries no numeric cell to stale")
            rows[1] = ",".join(cells)
            (stash / target).write_text("\n".join(rows) + "\n")
            got = _one((script, [target], str(stash), str(root)))
            if not any("drifted from" in g for g in got):
                fails.append(f"a deliberately staled {target} was NOT reported: {got}")
    finally:
        shutil.rmtree(stash, ignore_errors=True)
        shutil.rmtree(root, ignore_errors=True)

    # 4. THE WRITE SENTINEL, BOTH WAYS. A byte-deterministic producer that
    #    rewrites its committed CSV must PASS (the false positive the byte
    #    comparison carried), and a seeded file the producer never writes
    #    must be reported as "did not write" (the negative the sentinel exists
    #    for). One call carries both: the real cheap producer plus a decoy
    #    output seeded from a committed copy under a name it does not write.
    stash = Path(_tf.mkdtemp(prefix="plant_stash4_"))
    root = Path(_tf.mkdtemp(prefix="plant_priv4_"))
    try:
        for f in RESULTS.glob("*.csv"):
            _committed(f.name, stash / f.name)
        det, out = "run_moment_admission", "moment_admission.csv"
        decoy = "moment_admission_decoy.csv"
        if not (stash / out).is_file():
            fails.append(f"{out} has no committed copy, the sentinel claim did not run")
        else:
            shutil.copy2(stash / out, stash / decoy)
            got = _one((det, [out, decoy], str(stash), str(root)))
            if any(g.startswith(out) and "did not write" in g for g in got):
                fails.append(f"a deterministic producer was accused of not writing: {got}")
            if not any(g.startswith(decoy) and "did not write" in g for g in got):
                fails.append(f"an unwritten seeded output was NOT reported: {got}")
    finally:
        shutil.rmtree(stash, ignore_errors=True)
        shutil.rmtree(root, ignore_errors=True)

    for f in fails:
        print(f"PLANT FAIL: {f}", file=sys.stderr)
    print(f"plant: {len(prod)} producers, 4 claims probed, {len(fails)} failure(s)")
    return 1 if fails else 0


# EXPENSIVE producers that read no raw trace: `--all` covers them on a checkout
# without data_raw/, which is every public clone. Membership is declared per
# producer, never inferred; the others in EXPENSIVE are audited one by one.
SYNTHETIC_ONLY = {"run_fringe_rho_recovery", "run_rf_saturation_ladder",
                  "run_moment_power_map", "run_moment_power_map_deep",
                  "run_three_channel_forecast"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="include the heavy fitting producers (needs data_raw/)")
    ap.add_argument("--plant", action="store_true",
                    help="probe the isolation, the pool and the detector")
    args = ap.parse_args()
    if args.plant:
        return plant()

    producers = dict(CHEAP)
    if args.all:
        if (ROOT / "data_raw" / "p_sweep").is_dir():
            producers.update(EXPENSIVE)
        else:
            synthetic = {k: v for k, v in EXPENSIVE.items() if k in SYNTHETIC_ONLY}
            print("--all without the raw traces covers only the producers declared "
                  f"synthetic-only: {', '.join(sorted(synthetic))}")
            producers.update(synthetic)

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
