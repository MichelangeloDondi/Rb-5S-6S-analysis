#!/usr/bin/env bash
# Reproduce the committed results/*.csv, figures, and docs/RESULTS.md from the
# already-committed data_raw/ (see README.md "Reproduce"). It runs 23 analysis
# stages, then the figures, the results ledger and the CSV status column. It is
# not the whole repository. Ten committed CSVs are written by nine scripts this
# file never calls, listed in README.md "Reproduce". Four of those need the
# rehearsal, quarantine or pilot trees, which stay outside the repository:
# run_stark_joint.py, run_global_archive_fit.py, _m25_norulers.py and
# run_pilot_ruler.py. The other five do run from a clone and are left out for
# runtime or because they are diagnostics: run_wing_check.py loads raw traces
# and takes about 6 min, run_wavemeter_reconstruction.py digitises a tracked
# photograph, run_laser_history.py reads the committed acquisition clock, and
# run_stark_centres.py and run_centre_stark.py read committed CSVs. Run from
# the repo root with the project's virtualenv active. annotate_results_status.py
# must run LAST: it appends the machine-readable status column read by every
# other consumer of results/*.csv.
set -euo pipefail
cd "$(dirname "$0")/.."

for s in run_qc run_noise run_ruler run_linefit \
         run_beta_self run_global_fit run_lever_crosscheck run_laser_epoch \
         run_power_sweep run_stark_sweep run_amplitude_trapping run_modelform \
         run_sigma_laser_sharing run_transit_mc run_amplitude_ratios run_ramp_geometry \
         run_model_ladder run_identifiability run_coverage run_sharing_bic run_fringe_tail \
         run_polarizability run_resolving_power; do
    echo "== scripts/$s.py =="
    python scripts/$s.py
done

python scripts/make_fig0_spectrum.py
python scripts/make_figures.py
python scripts/make_results_ledger.py
python scripts/annotate_results_status.py
