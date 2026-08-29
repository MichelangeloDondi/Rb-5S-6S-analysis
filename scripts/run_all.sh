#!/usr/bin/env bash
# Reproduce the committed results/*.csv, figures, and docs/RESULTS.md from the
# already-committed data_raw/ (see README.md "Reproduce"). It runs the analysis
# stages listed in the loop below, then the reference graph, the figures, the
# results ledger and the CSV status column. It is not the whole repository:
# several committed CSVs are written by scripts this file never calls.
#
# THE COUNTS THAT USED TO BE HERE ARE GONE ON PURPOSE. This header said "31
# analysis stages" while the loop ran 32, and "thirteen CSVs by twelve scripts"
# while enumerating eleven. A count duplicated into prose beside the thing it
# counts goes stale the first time either moves, and both had. `results/README.md`
# maps every CSV to its producer and is regenerated, so it is the authority.
# Some of those need
# the prehistory or pilot trees, which stay outside the repository (the
# rehearsal traces sit inside the prehistory tree, and data_raw/excluded/ is
# a committed directory, not one of these):
# run_stark_joint.py, run_global_dataset_fit.py, _m25_norulers.py,
# run_morning_ruler.py and run_full_dataset_fit.py. Others do run from a clone and are left out for
# runtime or because they are diagnostics: run_wing_check.py loads raw traces
# and takes about 6 min, run_wavemeter_reconstruction.py digitises a tracked
# photograph, run_cavity_scan.py integrates the tracked cavity-scan
# digitisation, run_laser_history.py reads the committed acquisition clock,
# and run_stark_centres.py and run_centre_stark.py read committed CSVs. Run from
# the repo root with the project's virtualenv active.
#
# annotate_results_status.py runs AFTER EVERY WRITER AND BEFORE EVERY READER,
# which is not where it used to sit. It appends the status column, and
# make_figures.py and make_results_ledger.py both READ that column, so running
# it last meant a clean full run reached make_figures with a freshly written
# results/stark_sweep.csv that had no status column yet and died on
# KeyError: 'status'. Measured 2026-08-14 in an isolated worktree: the run
# failed after 27 stages, which is why this order is now load-bearing and
# guarded by tests/test_pipeline_order.py.
set -euo pipefail
cd "$(dirname "$0")/.."

for s in run_qc run_noise run_ruler run_linefit run_trim_report \
         run_beta_self run_global_fit run_lever_crosscheck run_laser_epoch \
         run_power_sweep run_stark_sweep run_amplitude_trapping run_modelform \
         run_sigma_laser_sharing run_transit_mc run_amplitude_ratios run_ramp_geometry \
         run_model_ladder run_identifiability run_coverage run_sharing_bic run_fringe_tail \
         run_polarizability run_resolving_power run_projections \
         run_trapping_channels run_blackbody_channels run_skew_scaling \
         run_polarisation_bound run_collisional_shift_bound run_delta_alpha_posterior \
         run_guided_mode_tables run_onf_lever_ranking; do
    echo "== scripts/$s.py =="
    python scripts/$s.py
done

python scripts/annotate_results_status.py

# The reference graph is regenerated HERE, between the annotator and the
# ledger, and it was left out of this sequence entirely until 2026-08-28.
# The ledger reads what the graph resolves, so the order matters.
#
# It was omitted because a person is expected to remember it, and on the night
# this line was added it had been forgotten twice in one session, costing a
# five-minute suite run each time. A step that lives only in someone's memory
# is a step that gets skipped.
python scripts/check_references.py --graph

python scripts/make_fig0_spectrum.py
python scripts/make_figures.py
python scripts/make_results_ledger.py
