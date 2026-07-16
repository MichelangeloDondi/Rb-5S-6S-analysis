#!/usr/bin/env python3
"""
Append a machine-readable `status` column to every results/*.csv.

Design note (2026-07-12): the repo's honesty lived in `docs/RESULTS.md`
prose while the CSVs held bare numbers -- a plot script that loads
`beta_self.csv` sees `beta_self=0.0466` with no hint it is a model-dependent
PRELIM whose headline is a BOUND. The caveat must travel *with the number*. This
adds a controlled-vocabulary `status` tag to each row (the detail stays in
RESULTS.md and the `unit` column), so the key provenance survives the CSV into
any downstream table or figure.

Controlled vocabulary (the honest tag, not decoration):
  BOUND      an upper/lower limit, conditional on the OPEN w0 and/or the model;
             NOT a measurement (beta_self, sigma_laser, S0/kappa).
  NULL       below detection, or no model preference (ramp skew, BIC, the
             degeneracy-law ratios the archive's drift makes untestable).
  MEASURED   a genuine measurement from this data (the frequency rate; the
             P^2 amplitude scaling; the density-flat gamma floor).
  PRELIM     a model-dependent cross-check, superseded by a BOUND headline
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
SKIP = {"laser_epoch.csv", "qc_metrics.csv"}

# wide CSVs: one status for the whole file (its rows are homogeneous)
FILE_STATUS = {
    "beta_self.csv": "PRELIM",            # per-peak model fits; headline is the BOUND
    "beta_self_probe.csv": "BOUND",       # the model-independent width-slope bound = C1 headline
    "amplitude_ratios.csv": "NULL",       # degeneracy-law ratios drift-limited -> untestable in archive
    "amplitude_trapping.csv": "MEASURED", # amp ~ N, slopes 0.85-1.02, no rollover
    "modelform.csv": "NULL",              # Voigt-vs-Lehmann BIC below the gate -> no preference
    "power_sweep.csv": "MEASURED",        # fwhm-flat + amp~P^2 confirm the ramp law (resid_skew=ARTIFACT, RESULTS C3c)
    "ruler_campaign.csv": "MEASURED",     # the frequency rate (axis-independent)
    "linefit_conditions.csv": "PRELIM",   # per-condition joint fits, degenerate split
    "noise_model.csv": "DIAGNOSTIC",
    "ruler_blocks.csv": "CALIB",
    "ruler_traces.csv": "CALIB",
    "ruler_nlmap.csv": "CALIB",
    "sigma_laser_sharing.csv": "DIAGNOSTIC",  # the M4c in-sample consistency check
    "transit_mc.csv": "ENVELOPE",         # w0-parametric transit-broadening model
}

# long (quantity/key/value/err/unit) CSVs: status keyed by `quantity`
# (exact match, then longest-prefix). Unmapped -> hard error, so no row is
# silently left un-tagged.
QUANTITY_STATUS = {
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
    },
    "coverage.csv": {
        "bias": "DIAGNOSTIC", "coverage95": "DIAGNOSTIC",
        "false_measurement_rate": "DIAGNOSTIC",
    },
    "sharing_bic.csv": {
        "bic_eff": "DIAGNOSTIC", "chi2_red": "DIAGNOSTIC",
        "dBIC_eff_block_minus_T": "DIAGNOSTIC",
        "dBIC_raw_block_minus_T": "DIAGNOSTIC",
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
