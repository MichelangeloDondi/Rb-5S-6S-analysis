#!/usr/bin/env bash
# Reproduce every committed results/*.csv, figure, and docs/RESULTS.md from the
# already-committed data_raw/ (see README.md "Reproduce"). Run from the repo
# root with the project's virtualenv active. annotate_results_status.py must
# run LAST: it appends the machine-readable status column read by every other
# consumer of results/*.csv.
set -euo pipefail
cd "$(dirname "$0")/.."

for s in run_qc run_noise run_ruler run_linefit \
         run_beta_self run_global_fit run_lever_crosscheck run_laser_epoch \
         run_power_sweep run_stark_sweep run_amplitude_trapping run_modelform \
         run_sigma_laser_sharing run_transit_mc run_amplitude_ratios run_ramp_geometry; do
    echo "== scripts/$s.py =="
    python scripts/$s.py
done

python scripts/make_fig0_spectrum.py
python scripts/make_figures.py
python scripts/make_results_ledger.py
python scripts/annotate_results_status.py
