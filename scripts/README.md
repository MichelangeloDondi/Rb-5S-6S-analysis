# The runnables

One runnable per analysis stage. They run in dependency order, each reading the
earlier stages' tables out of `results/` and writing its own output back there
as a committed CSV, so any single stage can be re-run and its output compared
against the copy in the repository. Alongside the producers sit the builders
that draw the figures and generate the documents, and two shell scripts.

`run_all.sh` runs the twenty-five analysis stages below in order, then the
figures, then `docs/RESULTS.md`, then the status column. `ci_gate.sh` runs the
lint pass and the full test battery including the slow closure tests, in the
order continuous integration runs them, and is meant to be run before a push.

`annotate_results_status.py` runs after every producer and before every reader,
because it appends the machine-readable `status` column that consumers of
`results/*.csv` read. `make_figures.py` and `make_results_ledger.py` are two of
those consumers, so it runs before them rather than last. The
controlled vocabulary is set out in
[`../results/README.md`](../results/README.md), which also lists what each
committed table holds. The `M` codes below are the pipeline stage labels of
[`../docs/methods.md`](../docs/methods.md).

## The pipeline, in the order `run_all.sh` runs it

| script | writes |
|---|---|
| `run_qc.py` (M0) | quality metrics for every trace in the manifest into `qc_metrics.csv`, each with its z-scores against its condition siblings, its residual-tail trim record and its outlier mark |
| `run_noise.py` (M1) | the variance law per condition into `noise_model.csv`, which is where every later fit takes its weights from |
| `run_ruler.py` (M2) | the frequency axis from the EOM ruler blocks into `ruler_blocks.csv`, `ruler_traces.csv`, `ruler_nlmap.csv`, `ruler_campaign.csv` and the time-resolved `ruler_rate_model.csv` |
| `run_linefit.py` (M3) | the joint lineshape fit of every canonical radio-frequency-off condition into `linefit_conditions.csv` |
| `run_trim_report.py` | every trim and every removal the earlier stages made, gathered from their own tables, into `trim_report.csv` |
| `run_beta_self.py` (M4) | collisional self-broadening into `beta_self.csv`, the model-independent width-slope bound into `beta_self_probe.csv`, and the noise-law swap check into `noise_law_swap.csv` |
| `run_global_fit.py` (M4b) | the hierarchical fit across peaks and temperatures, with the laser width shared, into `global_fit.csv` |
| `run_lever_crosscheck.py` (M4d) | the lever-limited cross-check of the collisional coefficient, with its error budget, into `lever_crosscheck.csv` |
| `run_laser_epoch.py` (M5) | the laser-width upper bound and the waist band into `laser_epoch.csv`, read off `linefit_conditions.csv` |
| `run_power_sweep.py` (M6) | width, amplitude and residual skew against drive power into `power_sweep.csv` |
| `run_stark_sweep.py` (M4e) | the AC-Stark coefficient bound from the power lever into `stark_sweep.csv` |
| `run_amplitude_trapping.py` (M7) | peak amplitude against density, and the trapping rollover, into `amplitude_trapping.csv` |
| `run_modelform.py` (M8) | Voigt against the Lehmann cusp at the cold dim corner into `modelform.csv` |
| `run_sigma_laser_sharing.py` (M4c) | the two-model test of sharing one laser width per temperature into `sigma_laser_sharing.csv` |
| `run_transit_mc.py` (M9) | the Monte-Carlo transit kernel against waist, temperature and collection geometry into `transit_mc.csv` |
| `run_amplitude_ratios.py` (M10) | cross-peak area ratios against the degeneracy law into `amplitude_ratios.csv` |
| `run_ramp_geometry.py` | the ramp-law moment coefficients at the three proposed collection geometries, printed rather than written |
| `run_model_ladder.py` (M11) | the nested-model BIC ladder into `model_ladder.csv` |
| `run_identifiability.py` (M12) | the local covariance and the profile-likelihood map of the width decomposition into `identifiability.csv` and `identifiability_profile.csv` |
| `run_coverage.py` (M13) | injection-recovery coverage of the 95% construction, and the minimum detectable coefficient, into `coverage.csv` |
| `run_sharing_bic.py` (M14) | the model-selection view of the same sharing question into `sharing_bic.csv` |
| `run_fringe_tail.py` (M15) | the fringe-resolved tail of the standing-wave AC-Stark ramp into `fringe_tail.csv` |
| `run_polarizability.py` (M16) | 5S and 6S dynamic polarizabilities, the independent difference recompute, and the first magic wavelengths, into `polarizability.csv` |
| `run_resolving_power.py` (M17) | each observable's dynamic range over the temperature sweep divided by its scatter at fixed conditions, into `resolving_power.csv` |
| `run_projections.py` | what a further campaign would buy, computed from the archive's own precision, into `projections.csv` |

## Run on their own

These are not in `run_all.sh`, either because they take too long, or because
they read a session outside the frozen archive, or because they print a
diagnostic rather than write a table.

| script | writes |
|---|---|
| `run_stark_joint.py` (M23) | the joint light-shift fit over all three sessions with one shared coefficient, into `stark_joint.csv`. A long profile-likelihood run |
| `run_global_dataset_fit.py` (M25) | one likelihood over every canonical trace, collisional and AC-Stark coefficients both free, into `global_dataset_fit.csv` |
| `_m25_norulers.py` | the same fit with the ruler arm removed, into `global_dataset_fit_norulers.csv` |
| `run_full_dataset_fit.py` (M28) | the M23 construction on the M25 data, into `full_dataset_fit.csv` |
| `run_morning_ruler.py` (M26) | the pilot day's own frequency axis, from 27 recovered EOM traces, into `morning_ruler.csv` |
| `run_wing_check.py` (M24) | whether the near-core asymmetry is a collisional wing, into `wing_check.csv`. Loads raw traces and takes several minutes |
| `run_laser_history.py` (M20) | the laser frequency within each display epoch into `laser_history.csv` and `laser_history_structure.csv` |
| `run_stark_centres.py` (M21) | what the line centres can and cannot say about the light shift, one row per drift form, into `stark_centres.csv` |
| `run_centre_stark.py` (M27) | the centre-channel coefficient from the held-lock epochs into `centre_stark.csv`, exiting cleanly if either input table is absent |
| `run_wavemeter_reconstruction.py` (M22) | the 2025-06-11 wavemeter record, digitised from its tracked photograph, into `wavemeter_reconstruction.csv` |
| `run_drift_settling.py` | the lock disturbance against time, off the committed clock, printed rather than written |
| `run_intrablock_trend.py` | whether the position scatter within a block is drift or jitter, printed rather than written |
| `run_epoch_checks.py` | the pilot and prehistory cross-checks of the clock, the disturbance model and the cross-day calibration, printed, with nothing entering `results/` |
| `run_polarizability_ladder.py` | the three-transition polarizability ladder, printed, plus `figures/fig9_polarizability_ladder.png` |
| `run_s0_block_bootstrap.py` | the block bootstrap of the power-lever limit, one row per resample, under `private/run_logs/` rather than `results/` |
| `run_cavity_scan.py` (M30) | the cavity-scan photograph digitised and integrated into `cavity_scan_integrals.csv`, the one result whose input is an image |
| `run_campaign_conditions.py` | what a next campaign's waist, power, temperature and choice of transition do to the six effects this record has measured, printed rather than written. Its three answers are the per-line lever becoming spendable at a tighter waist, the infrared halo growing thirtyfold over the hot extension the collisional programme wants, and the blackbody test that orders the transition menu |
| `run_companion_refit.py` | the preregistered refit with the two width companions inside the fitted model rather than beside it, scored against `docs/notes/companion_inclusive_refit_prereg.md`. Writes nothing, and checks the option is inert before reading any result. Its answer is that the per-line scale is unidentifiable on this dataset, because it enters only as a multiple of a light shift the dataset bounds rather than measures |

## Figures and documents

| script | writes |
|---|---|
| `make_figures.py` | the publication PNGs in `figures/`, from the committed CSVs, each stamped with a fingerprint of the tables it was drawn from |
| `make_fig0_spectrum.py` | `figures/fig0_spectrum.png`, one representative fitted spectrum |
| `make_timeline_figure.py` | `docs/apparatus/program_timeline.png`, one panel per session off `data_recovered/CLOCK.csv` |
| `make_qc_gallery.py` | the per-trace inspection gallery, all of it under `private/qc_gallery/` and none of it tracked |
| `make_results_ledger.py` | `docs/RESULTS.md`, with every headline number read from the CSV that produced it |
| `build_lit_index.py` | `docs/references.bib` from the per-paper files in `docs/lit/`, plus the holdings index for the paper collection kept outside this repository. `--check` regenerates in memory and diffs against what is committed |
| `build_clock_table.py` | `data_recovered/CLOCK.csv`, the acquisition clock serialised out of the excluded backup copies |
| `annotate_results_status.py` | the `status` column, appended to every file in `results/` |

## Utilities

| script | does |
|---|---|
| `run_all.sh` | the whole chain: the twenty-five stages in dependency order, then the figures, the ledger and the status column |
| `ci_gate.sh` | the pre-push checks, in the order and on the content continuous integration uses: `ruff` over the library, the scripts and the tests, then the full battery with the slow tests |
| `verify_results_fresh.py` | re-runs each producer into `results/`, diffs what appears against what was committed, and restores the committed files afterwards. `--all` widens the set to the producers that need raw traces |
| `import_data.py` | the one-time, idempotent import of the 2025 archive into `data_raw/`, deduplicating by MD5 and writing `MANIFEST.csv` |
| `annotate_manifest_qc.py` | refreshes the `qc_reason` provenance column of `data_raw/MANIFEST.csv` in place, leaving the other columns untouched |
| `check_release_notes.py` | the register checks applied to a release body or any other untracked prose, since a release body is not a tracked file and nothing else looks at it |
| `publish_recovered.py` | copies the backup-recovered acquisitions into `data_recovered/` under hash-suffixed names, since nine of the original names collide with different bytes |
| `run_timestamp_audit.py` | scores the preregistered timestamp criteria against a excluded copy of the recovered backup and the committed manifest |

## What runs from a clone

The 297 raw traces are held privately and are not in this repository, so any
stage that opens one cannot run here. What that leaves is set out in
[`../data_raw/README.md`](../data_raw/README.md), and the condition is visible
in each script: the ones that need traces import `load_trace` from
`rb5s6s.ingest`. Twenty-five do, and seventeen of those cannot run here at all.
They are `run_qc.py`, `run_noise.py`, `run_ruler.py`,
`run_linefit.py`, `run_beta_self.py`, `run_global_fit.py`,
`run_lever_crosscheck.py`, `run_power_sweep.py`, `run_amplitude_trapping.py`,
`run_amplitude_ratios.py`, `run_modelform.py`, `run_model_ladder.py`,
`run_identifiability.py`, `run_wing_check.py`, `make_fig0_spectrum.py`,
`make_qc_gallery.py` and `annotate_manifest_qc.py`, which is most of
`run_all.sh`.

Six write nothing at all and exist so a published number can be re-derived
rather than taken. `_m25_parallel_smoke.py` is the acceptance check for
`RB5S6S_WORKERS`: it runs a small grid of the M25 profile through both the
sequential and the parallel path and demands that every chi-squared match
exactly, since the two paths have no licence to differ. `run_saturation_probe.py` reproduces the light-shift bound
with the saturation companion in the model, in four stages, the last of which
needs the two outside trees. `run_geometry_design.py` computes the two
geometry designs of `docs/notes/running_wave_and_waist_design.md`, the
frequency-shifted retro arm and the waist, and its weak-field branch
reproduces `lineshape.stark_ramp_axial_moments`, which is what licenses the
saturated branch beside it. `run_zeeman_depletion.py` does the hyperfine
pumping on the full Zeeman manifold, every Clebsch-Gordan coefficient present,
and its seven checks include the transit depletion per isotope, the blocked
cascade paths, and the same branching recomputed as a density matrix in exact
rational arithmetic.

Two more began as questions put at the bench and became producers when their
numbers reached the documents. `run_trapping_channels.py` does radiation
trapping on the two infrared cascade legs and writes
`results/trapping_channels.csv`. `run_blackbody_channels.py` does the cell's own
thermal field, on the cascade and at the detector, and writes
`results/blackbody_channels.csv`. Both carry their own `status` and `err_kind`
columns, so `annotate_results_status.py` skips them, and both are in
`run_all.sh`. They write because `docs/STYLE.md` requires prose to quote a
committed CSV rather than restate a number independently, and once those numbers
appeared in CLAIMS and the methods chapters, not writing them was the defect.

Six need more than the traces. `run_stark_joint.py`,
`run_global_dataset_fit.py`, `_m25_norulers.py`, `run_full_dataset_fit.py` and
`run_epoch_checks.py` read the prehistory and pilot sessions, which sit outside
the frozen archive and outside the repository, and `run_morning_ruler.py` reads
the pilot tree. Given a missing tree each of them prints what it cannot find
and exits 0, so the committed CSV stays the record. `publish_recovered.py`,
`build_clock_table.py` and `run_timestamp_audit.py` want the excluded backup
copies in the same way.

Three run in part. `make_figures.py` draws everything its committed inputs
support and prints a line for each panel it skips, including the one panel that
needs a ruler trace. `run_drift_settling.py` skips the half that reads the
temperature-session rulers and returns the power-session steps, which come from
the committed quality table. `verify_results_fresh.py` checks its default set
without traces and needs them only under `--all`.

Everything else reads committed tables and runs from a clone. Among the pipeline
stages that is `run_trim_report.py`, `run_laser_epoch.py`,
`run_sigma_laser_sharing.py`, `run_stark_sweep.py`, `run_transit_mc.py`,
`run_ramp_geometry.py`, `run_coverage.py`, `run_sharing_bic.py`,
`run_fringe_tail.py`, `run_polarizability.py`, `run_resolving_power.py` and
`run_projections.py`. Outside it, the light-shift work in `run_stark_centres.py`
and `run_centre_stark.py`, the laser reconstructions in `run_laser_history.py`
and `run_wavemeter_reconstruction.py`, `run_intrablock_trend.py`,
`run_s0_block_bootstrap.py`, `run_polarizability_ladder.py`,
`make_results_ledger.py`, `make_timeline_figure.py`,
`annotate_results_status.py`, `build_lit_index.py`, and the test battery
`ci_gate.sh` runs.
