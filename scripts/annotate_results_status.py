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
             degeneracy-law ratios the archive's drift makes untestable).
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
status/flag column and are left untouched. Run LAST in the pipeline, after every
producer and `make_results_ledger.py`. Guarded by tests/test_results_status.py.
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
        "centre_stark.csv"}

# wide CSVs: one status for the whole file (its rows are homogeneous)
FILE_STATUS = {
    "beta_self.csv": "PRELIM",            # per-peak model fits; headline is the BOUND
    "beta_self_probe.csv": "BOUND",       # the model-independent width-slope bound = C1 headline
    "amplitude_ratios.csv": "NULL",       # degeneracy-law ratios drift-limited -> untestable in archive
    "amplitude_trapping.csv": "MEASURED", # amp ~ N, slopes 0.85-1.02, no rollover
    "modelform.csv": "NULL",              # Voigt-vs-Lehmann BIC below the gate -> no preference
    "power_sweep.csv": "MEASURED",        # width null + amp~P^2 consistency check (resid_skew=ARTIFACT, RESULTS C3c)
    "ruler_campaign.csv": "MEASURED",     # the frequency rate (axis-independent)
    "ruler_rate_model.csv": "MEASURED",
    "pilot_ruler.csv": "CALIB",           # M26: the pilot day's own rate from its 27 recovered rulers   # per-(session,peak) rate(t): a real drift, resolved (rate_model.py)
    "global_archive_fit.csv": "PRELIM",   # M25 joint archive fit, rulers-on arm; headline stays with M23
    "global_archive_fit_norulers.csv": "PRELIM",  # M25 rulers-off arm; the pair's gap is a stated systematic
    "linefit_conditions.csv": "PRELIM",   # per-condition joint fits, degenerate split
    "noise_model.csv": "DIAGNOSTIC",
    # M22: digitised from a screen photograph, not from the archive. It measures
    # what the photograph contains rather than what the unsaved log held, so it
    # is a diagnostic of the apparatus record, never an input to a fit.
    "wavemeter_reconstruction.csv": "DIAGNOSTIC",
    # the IMG_2508 cavity-scan spike integrals (rb5s6s/cavity_scan.py): same
    # standing as M22 -- it measures the photographed display, identifying the
    # scan's hyperfine reading (APPARATUS.md sec. 6); never an input to a fit.
    "cavity_scan_integrals.csv": "DIAGNOSTIC",
    "resolving_power.csv": "DIAGNOSTIC",
    # M21: the centre channel cannot measure the pull -- a NULL, not a bound,
    # because the parameter is unidentifiable rather than merely imprecise
    "stark_centres.csv": "NULL",  # measures the experiment's sensitivity, not the atom
    # M20: a reconstruction of the laser's frequency history, conditional on the
    # ruler rate and on mtime standing in for acquisition time. Not a measured
    # frequency -- the absolute scale is exactly what the archive cannot supply.
    "laser_history.csv": "DIAGNOSTIC",
    "laser_history_structure.csv": "DIAGNOSTIC",

    "ruler_blocks.csv": "CALIB",
    "ruler_traces.csv": "CALIB",
    "ruler_nlmap.csv": "CALIB",
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
        "kappa_pred": "CALIB", "S0_225mW_pred": "CALIB",
        "kappa_ub95_drop4192": "BOUND", "S0_225mW_ub95_drop4192": "BOUND",
        "gamma_coll_post": "PRELIM",
        "reh_rate": "CALIB", "pilot_rate_scale": "CALIB",
        "Vsat_camp": "DIAGNOSTIC",
        "Vsat_reh": "DIAGNOSTIC", "n_traces": "DIAGNOSTIC",
        "profile_point": "DIAGNOSTIC",
    },
    # M28: the cross-campaign full-archive joint fit. Same construction as M23
    # (one profiled kappa, the collisional term under a prior), over M25's
    # trace set with the rulers excluded. The gate_* rows are the
    # pre-registered acceptance checks of docs/notes/full_archive_fit_prereg.md
    # and are diagnostics of the RUN, not of the atom.
    "full_archive_fit.csv": {
        "kappa_ub95": "BOUND", "S0_225mW_ub95": "BOUND",
        "S0_270mW_ub95": "BOUND",
        "kappa_min": "DIAGNOSTIC", "dchi2_kappa0": "DIAGNOSTIC",
        "kappa_pred": "CALIB", "S0_225mW_pred": "CALIB",
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
        "S0_225mW_fit": "BOUND", "S0_225mW_pred": "CALIB",
        "chi2_red": "DIAGNOSTIC", "core_sigma_laser": "PRELIM",
    },
    "model_ladder.csv": {
        "summed_bic": "DIAGNOSTIC", "dBIC_rung": "DIAGNOSTIC",
    },
    "identifiability.csv": {
        "condition_number": "DIAGNOSTIC", "corr": "DIAGNOSTIC",
        "best_constrained_sigma": "DIAGNOSTIC", "worst_constrained_sigma": "DIAGNOSTIC",
        # the global profile-likelihood complements (all shape diagnostics)
        "banana_rms": "DIAGNOSTIC", "ridge_slope": "DIAGNOSTIC",
        "profile_free_gap": "DIAGNOSTIC", "closed_95": "DIAGNOSTIC",
        "audit_max_gain": "DIAGNOSTIC", "transit_railed_frac": "DIAGNOSTIC",
        "wide_free_gap": "DIAGNOSTIC", "branch": "DIAGNOSTIC",
        "branch_gap": "DIAGNOSTIC",
    },
    "coverage.csv": {
        "bias": "DIAGNOSTIC", "coverage95": "DIAGNOSTIC",
        "false_measurement_rate": "DIAGNOSTIC",
        # the minimum detectable effect: a property of THIS analysis at the
        # archive's own noise, simulated rather than measured on the data
        "mde_beta": "DIAGNOSTIC",
    },
    "polarizability.csv": {
        # M16: validation anchors are diagnostics; the unpublished design
        # numbers (magic wavelengths, alpha_6S(1064)) are model estimates
        "alpha_5s_static": "DIAGNOSTIC", "alpha_6s_static": "DIAGNOSTIC",
        "tuneout_5s": "DIAGNOSTIC", "delta_alpha_993": "DIAGNOSTIC",
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
    # the archive's own measured quantities carried in as calibration for the
    # arithmetic, and `proj_` rows are the model estimates built on them. This
    # file is keyed by quantity rather than registered whole in FILE_STATUS
    # because its rows are not homogeneous, and FILE_STATUS carries one status
    # for a whole file.
    "projections.csv": {
        "input_": "CALIB",
        "proj_": "ENVELOPE",
        # The one exception to the two prefixes, and it is deliberate. A source
        # headroom is a delivered laser power taken from a held demonstration or
        # from the archive's own bench, divided by a ceiling computed here. The
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
