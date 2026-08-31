#!/usr/bin/env python3
"""
Append a machine-readable `status` column to every results/*.csv.

Design note (2026-07-12): the caveats lived in `docs/RESULTS.md`
prose while the CSVs held bare numbers -- a plot script that loads
`beta_self.csv` sees `beta_self=0.0466` with no hint it is a model-dependent
PRELIM whose headline is a BOUND. The caveat must travel *with the number*. This
adds a controlled-vocabulary `status` tag to each row (the detail stays in
RESULTS.md and the `unit` column), so the key provenance survives the CSV into
any downstream table or figure.

Controlled vocabulary:
  BOUND      an upper/lower limit, conditional on the OPEN w0 and/or the model;
             NOT a measurement (beta_self, sigma_laser, S0/kappa).
  NULL       below detection, or no model preference (ramp skew, BIC, the
             degeneracy-law ratios the dataset's drift makes untestable).
  MEASURED   a genuine measurement from this data (the frequency rate; the
             P^2 amplitude scaling; the density-flat gamma floor).
  PRELIM     a model-dependent cross-check, replaced by a BOUND headline
             (the per-peak/per-cell beta fits; per-condition linefits).
  ARTIFACT   an identified statistical/instrumental artifact, not physics.
  DIAGNOSTIC a fit-quality or intermediate quantity (chi^2, noise law, LOO).
  CALIB      a calibration intermediate (ruler blocks/traces/nonlinearity map).
  ENVELOPE   an order-of-magnitude / literature-scaled / model estimate
             (the transit-MC widths, which are w0-parametric).

Idempotent (re-run refreshes the column in place; all other columns are
byte-preserved). `laser_epoch.csv` and `qc_metrics.csv` already carry their own
status/flag column and are left untouched. Runs after every PRODUCER and
before every READER of the column, which is not the same as running last:
`make_figures.py` and `make_results_ledger.py` both read `status`, so placing
this script after them made a clean `run_all.sh` die on KeyError: 'status'.
Guarded by tests/test_results_status.py and tests/test_pipeline_order.py.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402

VOCAB = {"BOUND", "NULL", "MEASURED", "PRELIM", "ARTIFACT", "DIAGNOSTIC",
         "CALIB", "ENVELOPE"}

# files that already carry their own provenance column -> leave untouched
SKIP = {"laser_epoch.csv", "qc_metrics.csv",
        # M27 writes its own per-row statuses (the bound and the case
        # verdict are BOUND, every diagnostic row says so itself)
        "centre_stark.csv",
        # the two radiation-environment producers, same reason: their rows
        # are a mix of exact line-data quantities and geometry-dominated
        # envelopes, and only the producer knows which is which. They also
        # carry an err_kind column, which nothing else here does yet.
        "trapping_channels.csv", "blackbody_channels.csv",
        # the cascade branching, same reason, and its producer needs the
        # optional sympy extra so it is not in run_all.sh either
        "cascade_branching.csv",
        # THE KERNEL FAMILY, all seven. Each producer writes its own `status`
        # per row, and several also write an `evidence_class` column that only
        # the producer can fill. They were added to results/ without being
        # added here, so `annotate_results_status.py` raised
        # KeyError: 'kernel_budget.csv' on the FIRST of them alphabetically and
        # took `run_all.sh` down with it. The gate never saw this because the
        # gate runs pytest and this script runs only from run_all.sh.
        # Found 2026-08-22 while registering orthogonal_levers.csv.
        "kernel_budget.csv", "kernel_headline.csv",
        "kernel_identifiability.csv", "kernel_k3.csv", "kernel_k5.csv",
        "kernel_k4.csv", "kernel_k7.csv", "kernel_worlds.csv",
        # the fibre twin, same reason: its producer writes per-row statuses
        "fibre_twin.csv",
        # the transit-additivity producer, same reason and one more: it mixes
        # ENVELOPE forecast rows with DIAGNOSTIC rows that exist to be COMPARED
        # with each other (the kernel-versus-package check and the
        # non-Gaussian shortfall), and only the producer knows which is which.
        # Registered in the same commit that created it, because a results CSV
        # absent from this dict takes run_all.sh down with a KeyError that the
        # gate cannot see.
        "transit_additivity.csv",
        # the two-arm twin forecast, same reason: its producer writes CALIB
        # for solved mode quantities, ENVELOPE for forecast precisions and
        # DIAGNOSTIC for the measured correlations, within one quantity column.
        "campaign_twin_forecast.csv",
        # the scenario forecasts, same mixed class: forecast precisions are
        # ENVELOPE, solved-mode quantities CALIB, so the producer tags rows.
        "scenario_forecast.csv",
        # the closed-loop leg: recovered medians and preregistered verdict
        # booleans, all diagnostics of the twin, tagged by the producer.
        "twin_closed_loop.csv",
        # the lever ranking: every row is a Fisher forecast about a DESIGN, and
        # its inputs split measured from estimated, so the producer tags them.
        "onf_lever_ranking.csv",
        # the guided-mode tables. Rows carry their own status because a mode
        # solve is CALIB, a profile ratio is DIAGNOSTIC and the retired
        # transit kernel is an ARTIFACT kept so its size stays visible.
        "guided_mode_tables.csv",
        # M28's window attribution and M29's centre Fisher, added 2026-08-24
        # and 2026-08-25 and the last two files to reach results/ without
        # entering this map, so the deliberate KeyError below was live in both
        # trees until 2026-08-26 and nothing ran to see it.
        #
        # They belong here rather than in either map below, and the reason is
        # structural rather than a preference. Both producers write their own
        # per-row `status`, and in both the status varies WITHIN a single
        # `quantity`, across its `key` values: centre_fisher's
        # `sigma_amplitude` is MEASURED for the three per-epoch drift classes
        # this archive can evaluate and ENVELOPE for the fixed-lock forecast,
        # and window_attribution's `window_attributed_pct` is MEASURED for the
        # primary grouping and DIAGNOSTIC for the finer one, which is reported
        # only to show the fraction is not the grouping's. `status_for()` reads
        # `row["quantity"]` and never `row["key"]`, so QUANTITY_STATUS cannot
        # express either file, and FILE_STATUS carries one status for a whole
        # file, which neither of these is.
        "window_attribution.csv", "centre_fisher.csv",
        # the collisional-shift bound, added 2026-08-27. Same structural
        # reason: its rows are a BOUND (the borrowed ceiling through the
        # vapour-pressure chain), an ENVELOPE (this atom's own expected
        # shift, which is not a bound and must not be read as one) and two
        # DIAGNOSTIC ratios, and only the producer knows which is which.
        # Registered here in the same commit that created the file, which is
        # the discipline the two entries above were added for failing.
        "collisional_shift_bound.csv",
        # the posterior: two BOUND limits from two constructions of one
        # likelihood, and the rest DIAGNOSTIC, including a point value the
        # committed grid does not resolve. The status varies within the file
        # and only the producer knows which row is which.
        "delta_alpha_posterior.csv"}

# wide CSVs: one status for the whole file (its rows are homogeneous)
FILE_STATUS = {
    # Every row is a count of the repository's own provenance declarations,
    # not a measurement of the atom, so the whole file is DIAGNOSTIC. It
    # measures how much of the record no producer regenerates, and a row
    # saying NO_PRODUCER is a label on a gap rather than a result.
    # every row is a probe result that moves no committed bound, by the
    # probe's own statement, so the whole file is DIAGNOSTIC.
    # every row is a twin result about a DESIGN, not a measurement of the
    # atom, so the whole file is DIAGNOSTIC.
    # a reconstruction of a note's construction, judged on the claim and not
    # the digits, so every row is DIAGNOSTIC.
    # Both files below were added 2026-08-24 and reached results/ without
    # entering this map, so a full run_all.sh died on the deliberate
    # KeyError below. That is the map working: a producer may not add a
    # committed file without saying what its rows are. The noise budget
    # measures the INSTRUMENT rather than the atom, and the twin's
    # recovery ratios measure the twin against its own injected truth, so
    # every row of each is DIAGNOSTIC. Both producers already write their
    # own status column, which is why nothing downstream noticed.
    "quantisation.csv": "DIAGNOSTIC",
    # A TWIN RESULT ABOUT TWO ESTIMATORS, not a measurement of the atom.
    # Every row is a bias or a spread recovered from injected truth under a
    # deliberately wrong model, so the whole file is DIAGNOSTIC and no row of
    # it is a value of anything the apparatus has.
    "estimator_duel.csv": "DIAGNOSTIC",
    # A ROBUSTNESS AXIS, NOT A MEASUREMENT. Every row is the committed fit
    # re-run at a window the record does not use, so no row is a value of
    # anything: the gamma_coll rows are the same quantity at deliberately
    # wrong windows, and the slope rows are indicative of beta_self, not its
    # committed shared-slope construction. The whole file is DIAGNOSTIC, and
    # a row of it may never be quoted as a result.
    "fit_window_scan.csv": "DIAGNOSTIC",
    # THE ARBITER ROWS for the three-layer cumulant statement: survival
    # fractions of the model line, pure quadrature, no apparatus quantity.
    "cumulant_window_check.csv": "DIAGNOSTIC",
    "twin_term_census.csv": "DIAGNOSTIC",
    "twin_realism.csv": "DIAGNOSTIC",
    "band_excess.csv": "DIAGNOSTIC",
    "twin_span_sweep.csv": "DIAGNOSTIC",
    "saturation_companion.csv": "DIAGNOSTIC",
    "unregenerated_claims.csv": "DIAGNOSTIC",
    # B2: every row is a design statement about what a configuration would
    # separate, not a measurement, so the whole file is DIAGNOSTIC.
    "orthogonal_levers.csv": "DIAGNOSTIC",
    "beta_self.csv": "PRELIM",            # per-peak model fits; headline is the BOUND
    "beta_self_probe.csv": "BOUND",       # the model-independent width-slope bound = C1 headline
    "amplitude_ratios.csv": "NULL",       # degeneracy-law ratios drift-limited -> untestable in the dataset
    "amplitude_trapping.csv": "MEASURED", # amp ~ N, slopes 0.85-1.02, no rollover
    "modelform.csv": "NULL",              # Voigt-vs-Lehmann BIC below the gate -> no preference
    "power_sweep.csv": "MEASURED",        # width null + amp~P^2 consistency check (resid_skew=ARTIFACT, RESULTS C3c)
    "ruler_campaign.csv": "MEASURED",     # the frequency rate (axis-independent)
    "ruler_rate_model.csv": "MEASURED",
    "morning_ruler.csv": "CALIB",           # M26: the campaign morning's own rate from its 27 recovered rulers   # per-(session,peak) rate(t): a real drift, resolved (rate_model.py)
    "global_dataset_fit.csv": "PRELIM",   # M25 joint dataset fit, rulers-on arm; headline stays with M23
    "global_dataset_fit_norulers.csv": "PRELIM",  # M25 rulers-off arm; the pair's gap is a stated systematic
    "linefit_conditions.csv": "PRELIM",   # per-condition joint fits, degenerate split
    "noise_model.csv": "DIAGNOSTIC",
    # M22: digitised from a screen photograph, not from the dataset. It measures
    # what the photograph contains rather than what the unsaved log held, so it
    # is a diagnostic of the apparatus record, never an input to a fit.
    "wavemeter_reconstruction.csv": "DIAGNOSTIC",
    # the IMG_2508 cavity-scan spike integrals (rb5s6s/cavity_scan.py): same
    # standing as M22 -- it measures the photographed display, identifying the
    # scan's hyperfine reading (APPARATUS.md sec. 6); never an input to a fit.
    "cavity_scan_integrals.csv": "DIAGNOSTIC",
    "resolving_power.csv": "DIAGNOSTIC",
    # M37 sizes a channel in order to CLOSE it: nothing here feeds a
    # committed bound, and the rate column is a ceiling, not a detection.
    "cooperative_channel.csv": "DIAGNOSTIC",
    # M38 measures what an ASSUMPTION costs and which of two the data
    # prefer. Nothing here is a bound on a physical coefficient.
    "laser_kernel.csv": "DIAGNOSTIC",
    "onf_candidate.csv": "DIAGNOSTIC",
    # M21: the centre channel cannot measure the pull -- a NULL, not a bound,
    # because the parameter is unidentifiable rather than merely imprecise
    "stark_centres.csv": "NULL",  # measures the experiment's sensitivity, not the atom
    # M20: a reconstruction of the laser's frequency history, conditional on the
    # ruler rate and on mtime standing in for acquisition time. Not a measured
    # frequency -- the absolute scale is exactly what the dataset cannot supply.
    "laser_history.csv": "DIAGNOSTIC",
    "laser_history_structure.csv": "DIAGNOSTIC",

    "ruler_blocks.csv": "CALIB",
    "ruler_traces.csv": "CALIB",
    "ruler_nlmap.csv": "CALIB",
    # M2 stage 4b is a BOUND rather than a calibration intermediate: its
    # deliverable is an upper limit on the laser's non-repeating frequency
    # excursion, not a number any later stage consumes.
    "ruler_tooth_scatter.csv": "BOUND",
    # every trim and every outlier removal the pipeline made, collected from
    # the tables that made them. A record of what was cut, never an input.
    "trim_report.csv": "DIAGNOSTIC",
    "sigma_laser_sharing.csv": "DIAGNOSTIC",  # the M4c in-sample consistency check
    "transit_mc.csv": "ENVELOPE",         # w0-parametric transit-broadening model
    "identifiability_profile.csv": "DIAGNOSTIC",  # the M12 profile-likelihood grids (fig7)
    "noise_law_swap.csv": "DIAGNOSTIC",   # robustness swap of the fit WEIGHTS, not physics
}

# long (quantity/key/value/err/unit) CSVs: status keyed by `quantity`
# (exact match, then longest-prefix). Unmapped -> hard error, so no row is
# silently left un-tagged.
QUANTITY_STATUS = {
    # M24: the wing check -- a NULL that closes C3f's open structure. The
    # per-condition and mean f_wing rows are bounds on a wing fraction; the
    # verdict row is the closure statement itself.
    "wing_check.csv": {
        "f_wing_red": "BOUND", "f_wing_blue": "BOUND",
        "f_wing_red_mean": "BOUND", "f_wing_blue_mean": "BOUND",
        # M24 restructure (2026-08-01): the licensed observable is red minus
        # blue (a symmetric transit mismatch cancels in the difference). The
        # 130 C closure is its null check; the individual red side at 130 C
        # is context (it is a real nonzero floor from the symmetric misfit,
        # not itself a null since the v3.0.0 reprior narrowed the transit).
        "f_wing_red_130C": "MEASURED", "density_lever": "DIAGNOSTIC",
        "asymmetry_red_minus_blue": "MEASURED", "asymmetry_130C": "NULL",
    },
    # M23: the joint two-session profile-likelihood bound. The headline rows
    # are BOUNDs (one-sided by construction -- the ramp model only broadens
    # red); the kappa_min/dchi2 preference is DIAGNOSTIC, not a detection.
    # Both files are DIAGNOSTIC throughout, deliberately. commit_sweep counts
    # what a historical commit loads, which is a property of the tree rather
    # than of the atoms. skew_scaling measures an exponent whose competing
    # hypotheses are separated by simulation, and until the campaign gives it
    # a second lever it characterises a residual rather than bounding a
    # physical coefficient.
    "commit_sweep.csv": {
        "fit_points": "DIAGNOSTIC", "fit_traces": "DIAGNOSTIC",
        "fit_points_boundary": "DIAGNOSTIC",
        "fit_points_boundaries": "DIAGNOSTIC",
    },
    "polarisation_bound.csv": {
        "mean_fwhm": "DIAGNOSTIC",
        "isotope_width_difference": "DIAGNOSTIC",
        "dmf1_broadening_ub95": "BOUND",
        # the channel these rows answered is retracted. The arithmetic
        # stands and the question does not arise, which is ARTIFACT here.
        "mismatch_ub95_at_field": "ARTIFACT",
        "vector_ratio": "DIAGNOSTIC",
        "vector_spread_at_225mW_pred": "DIAGNOSTIC",
        "vector_spread_at_225mW_bound": "DIAGNOSTIC",
        "vector_centre_shift_per_projection": "DIAGNOSTIC",
    },
    "skew_scaling.csv": {
        "skew_amp_exponent": "DIAGNOSTIC",
        "skew_amp_fit_chi2_red": "DIAGNOSTIC",
        "skew_amp_exponent_line_scatter": "DIAGNOSTIC",
        "skew_hypothesis_recovered_shot_noise": "DIAGNOSTIC",
        "skew_hypothesis_recovered_fixed_amplitude": "DIAGNOSTIC",
        "skew_hypothesis_p_shot_noise": "DIAGNOSTIC",
        "skew_hypothesis_p_fixed_amplitude": "DIAGNOSTIC",
    },
    "stark_joint.csv": {
        "kappa_ub95": "BOUND", "S0_225mW_ub95": "BOUND",
        "S0_270mW_ub95": "BOUND",
        "kappa_min": "DIAGNOSTIC", "dchi2_kappa0": "DIAGNOSTIC",
        "kappa_ub95_camponly": "BOUND", "kappa_min_wing": "DIAGNOSTIC",
        "kappa_ub95_wing": "BOUND",
        # 2026-08-02, resolved: the earlier 17.8k value was a cold-start
        # warm-up gap (tagged ARTIFACT at the time). The seeded run's own
        # merged pointwise-min gives 13.27 (priors pair; wing pair 24.84),
        # verified by recomputation from the run log. Direction indifference
        # holds at the 1e-4 level of the 190k chi2 profile.
        "direction_dchi2_max": "DIAGNOSTIC",
        "lopo_dchi2_262": "DIAGNOSTIC", "lopo_dchi2_pred": "DIAGNOSTIC",
        # ENVELOPE, not CALIB: both depend on an effective waist never
        # measured in the cell and on RHO_RETRO, which constants.py calls
        # an assumption. UNCERTAINTY.md section 1 caps a result at
        # ENVELOPE when an ENVELOPE input feeds it, and an ENVELOPE
        # must never carry a published digit. A 95 per cent significance
        # was computed against these while they were tagged CALIB.
        "kappa_pred": "ENVELOPE", "S0_225mW_pred": "ENVELOPE",
        "kappa_ub95_drop4192": "BOUND", "S0_225mW_ub95_drop4192": "BOUND",
        "gamma_coll_post": "PRELIM",
        "reh_rate": "CALIB", "pilot_rate_scale": "CALIB",
        "Vsat_camp": "DIAGNOSTIC",
        "Vsat_reh": "DIAGNOSTIC", "n_traces": "DIAGNOSTIC",
        "profile_point": "DIAGNOSTIC",
    },
    # M28: the cross-campaign full-dataset joint fit. Same construction as M23
    # (one profiled kappa, the collisional term under a prior), over M25's
    # trace set with the rulers excluded. The gate_* rows are the
    # pre-registered acceptance checks of docs/notes/full_dataset_fit_prereg.md
    # and are diagnostics of the RUN, not of the atom.
    "full_dataset_fit.csv": {
        "kappa_ub95": "BOUND", "S0_225mW_ub95": "BOUND",
        "S0_270mW_ub95": "BOUND",
        "kappa_min": "DIAGNOSTIC", "dchi2_kappa0": "DIAGNOSTIC",
        # EXPLICIT, 2026-08-27. Each of these was resolving through the
        # prefix fallback onto an entry that NAMES A DIFFERENT ROW of this
        # same file,
        # so one quantity's tag was deciding another's. Every one of them
        # happened to inherit the right answer; `sigma_laser_sp` inheriting
        # `sigma_laser_s` is the one that shows how thin the luck was. The
        # values below are what the fallback produced, so nothing changes
        # except that it is now written down.
        "S0_225mW_ub95_drop4192": "BOUND", "kappa_min_wing": "DIAGNOSTIC",
        "kappa_ub95_camponly": "BOUND", "kappa_ub95_drop4192": "BOUND",
        "kappa_ub95_pladder": "BOUND", "kappa_ub95_wing": "BOUND",
        "profile_point_pladder": "DIAGNOSTIC", "sigma_laser_sp": "PRELIM",
        # ENVELOPE, not CALIB: both depend on an effective waist never
        # measured in the cell and on RHO_RETRO, which constants.py calls
        # an assumption. UNCERTAINTY.md section 1 caps a result at
        # ENVELOPE when an ENVELOPE input feeds it, and an ENVELOPE
        # must never carry a published digit. A 95 per cent significance
        # was computed against these while they were tagged CALIB.
        "kappa_pred": "ENVELOPE", "S0_225mW_pred": "ENVELOPE",
        "direction_dchi2_max": "DIAGNOSTIC", "basin_gap_max": "DIAGNOSTIC",
        "lopo_dchi2": "DIAGNOSTIC",
        "beta_self_post": "PRELIM", "gamma_coll_post_130C": "PRELIM",
        "sigma_laser_s": "PRELIM",
        "reh_rate": "CALIB", "pilot_rate_scale": "CALIB",
        "Vsat": "DIAGNOSTIC", "n_traces": "DIAGNOSTIC",
        "qc_gate": "DIAGNOSTIC", "gate_": "DIAGNOSTIC",
        "railed_": "DIAGNOSTIC",
        "profile_point": "DIAGNOSTIC",
    },
    "global_fit.csv": {
        "beta_self": "BOUND", "sigma_laser": "BOUND",
        "beta_modelform_syst": "BOUND", "beta_nscale_syst": "BOUND",
        "chi2_red": "DIAGNOSTIC", "noise_floor_limited": "DIAGNOSTIC",
        "params_at_bound": "DIAGNOSTIC",
    },
    "lever_crosscheck.csv": {
        "beta_crosscheck": "BOUND", "beta_err_modelform": "BOUND",
        "beta_err_transit": "BOUND", "beta_err_sharing": "BOUND",
        "beta_w0_band": "BOUND", "beta_lever_probe_130": "BOUND",
        "beta_loo_peak": "DIAGNOSTIC", "beta_loo_temp": "DIAGNOSTIC",
        "beta_loo_drop": "DIAGNOSTIC", "sigma_loo_drop": "DIAGNOSTIC",
        "beta_grid_": "PRELIM",
        "gamma_coll_mean_vs_T": "MEASURED", "gamma_rise_factor": "MEASURED",
    },
    "stark_sweep.csv": {
        "kappa_ub95_profile": "BOUND", "S0_225mW_ub95_profile": "BOUND",
        # kappa is the raw fit point (its err is the chi2-inflated Wald sigma,
        # invalid at the kappa=0 rail) -- the quotable rows are the _ub95_profile
        # bounds, so the point estimate is a DIAGNOSTIC, not a BOUND.
        "kappa_ub95": "DIAGNOSTIC", "kappa_err_raw": "DIAGNOSTIC", "kappa": "DIAGNOSTIC",
        "S0_225mW_ub95_raw": "DIAGNOSTIC", "S0_225mW_ub95": "DIAGNOSTIC",
        "S0_225mW_fit": "BOUND", "S0_225mW_pred": "ENVELOPE",
        # EXPLICIT, 2026-08-27: the two sensitivity anchors were inheriting
        # ENVELOPE from `S0_225mW_pred` through the prefix fallback, which
        # is the right tag reached by the wrong mechanism.
        "S0_225mW_pred_lo": "ENVELOPE", "S0_225mW_pred_hi": "ENVELOPE",
        "chi2_red": "DIAGNOSTIC", "core_sigma_laser": "PRELIM",
    },
    "model_ladder.csv": {
        "summed_bic": "DIAGNOSTIC", "dBIC_rung": "DIAGNOSTIC",
    },
    "kernel_k8.csv": {
        "n_conditions": "DIAGNOSTIC", "height_z": "DIAGNOSTIC",
        "density_z": "DIAGNOSTIC", "predictor_corr": "DIAGNOSTIC",
        "loo_height_z_min": "DIAGNOSTIC", "loo_height_z_median": "DIAGNOSTIC",
        "verdict": "DIAGNOSTIC", "mechanism_note": "DIAGNOSTIC",
        "r_kernel_effect": "DIAGNOSTIC",
    },
    "identifiability.csv": {
        "condition_number": "DIAGNOSTIC", "corr": "DIAGNOSTIC",
        "best_constrained_sigma": "DIAGNOSTIC", "worst_constrained_sigma": "DIAGNOSTIC",
        # the global profile-likelihood complements (all shape diagnostics)
        "banana_rms": "DIAGNOSTIC", "ridge_slope": "DIAGNOSTIC",
        "ridge_slope_covariance_pred": "DIAGNOSTIC",
        "profile_free_gap": "DIAGNOSTIC", "closed_95": "DIAGNOSTIC",
        "audit_max_gain": "DIAGNOSTIC", "transit_railed_frac": "DIAGNOSTIC",
        "wide_free_gap": "DIAGNOSTIC", "branch": "DIAGNOSTIC",
        "branch_gap": "DIAGNOSTIC",
    },
    "coverage.csv": {
        "bias": "DIAGNOSTIC", "coverage95": "DIAGNOSTIC",
        "false_measurement_rate": "DIAGNOSTIC",
        # the minimum detectable effect: a property of THIS analysis at the
        # dataset's own noise, simulated rather than measured on the data
        "mde_beta": "DIAGNOSTIC",
        # 2026-08-10: the sd of beta_eff across trials, computed all along
        # and only reported once its own Monte-Carlo error existed to quote
        # beside it
        "scatter": "DIAGNOSTIC",
    },
    "polarizability.csv": {
        # M16: validation anchors are diagnostics; the unpublished design
        # numbers (magic wavelengths, alpha_6S(1064)) are model estimates
        "alpha_5s_static": "DIAGNOSTIC", "alpha_6s_static": "DIAGNOSTIC",
        "tuneout_5s": "DIAGNOSTIC", "delta_alpha_993": "DIAGNOSTIC",
        # EXPLICIT, 2026-08-27. Without this entry the prefix fallback below
        # matched it to "delta_alpha_993" and silently retagged an ENVELOPE
        # row DIAGNOSTIC, dropping the caveat from figures that quote its
        # 4.2-to-21.7 a.u. range. The collision was an accident of naming,
        # which is why the fallback needs an exact entry to beat it.
        "delta_alpha_993_tail_dispersion": "ENVELOPE",
        # the two states separately at 993 nm -- the evidence behind the sign
        "alpha_5s_993": "DIAGNOSTIC", "alpha_6s_993": "DIAGNOSTIC",
        "alpha_6s_1064": "ENVELOPE", "magic_5s6s": "ENVELOPE",
    },
    "sharing_bic.csv": {
        "bic_eff": "DIAGNOSTIC", "chi2_red": "DIAGNOSTIC",
        "dBIC_eff_block_minus_T": "DIAGNOSTIC",
        "dBIC_raw_block_minus_T": "DIAGNOSTIC",
    },
    # What a further campaign would buy. Every row is a projection of an
    # instrument's reach, never a measurement, so nothing here may be tagged
    # MEASURED or BOUND. The two prefixes are the whole map: `input_` rows are
    # the dataset's own measured quantities carried in as calibration for the
    # arithmetic, and `proj_` rows are the model estimates built on them. This
    # file is keyed by quantity rather than registered whole in FILE_STATUS
    # because its rows are not homogeneous, and FILE_STATUS carries one status
    # for a whole file.
    "projections.csv": {
        "input_": "CALIB",
        "proj_": "ENVELOPE",
        # The one exception to the two prefixes, and it is deliberate. A source
        # headroom is a delivered laser power taken from a held demonstration or
        # from this project's own bench, divided by a ceiling computed here. The
        # row's content is a carried instrument fact rather than a projection of
        # reach, so it is tagged CALIB and the longest-prefix rule below picks
        # this entry over the generic `proj_`.
        "proj_source_": "CALIB",
    },
    "fringe_tail.csv": {
        # fringe-tail leverage on the Stark ramp: the sign and magnitude at the
        # small (16 um, config S) waist ride on the OPEN coherence window and collection
        # geometry, so the coefficients are ENVELOPE (a bracket, re-derive with
        # the measured collection profile); the MC error and window fraction are
        # diagnostics of that bracket.
        "d_skew": "ENVELOPE", "d_kappa3": "ENVELOPE",
        "excess_var_frac": "ENVELOPE", "frac_resolved": "ENVELOPE",
        "d_skew_mc_err": "DIAGNOSTIC", "window_frac": "DIAGNOSTIC",
        # 2026-08-10: the three siblings d_skew_mc_err had none of, same
        # construction and same tag.
        "d_kappa3_mc_err": "DIAGNOSTIC", "excess_var_frac_mc_err": "DIAGNOSTIC",
        "frac_resolved_mc_err": "DIAGNOSTIC",
    },
}
# CALIB is a valid tag for a prediction row; extend VOCAB check accordingly.


def status_for(fname: str, row: dict) -> str:
    if fname in QUANTITY_STATUS:
        m = QUANTITY_STATUS[fname]
        q = row["quantity"]
        if q in m:
            return m[q]
        cand = [(len(p), s) for p, s in m.items() if q.startswith(p)]
        if cand:
            return max(cand)[1]
        raise KeyError(f"{fname}: unmapped quantity {q!r}")
    return FILE_STATUS[fname]   # KeyError forces every file to be mapped


def main() -> int:
    tagged = 0
    for path in sorted(C.RESULTS_DIR.glob("*.csv")):
        if path.name in SKIP:
            continue
        rows = list(csv.DictReader(open(path)))
        if not rows:
            continue
        fields = [f for f in rows[0].keys() if f != "status"] + ["status"]
        for r in rows:
            st = status_for(path.name, r)
            if st not in VOCAB:
                raise SystemExit(f"{path.name}: status {st!r} not in vocab")
            r["status"] = st
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        tagged += 1
    print(f"tagged {tagged} result CSVs with a `status` column "
          f"({len(SKIP)} already carried their own; vocab {sorted(VOCAB)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
