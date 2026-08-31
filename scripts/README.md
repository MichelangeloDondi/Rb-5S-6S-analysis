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

<!-- term-of-art: rows cite private reviews directory paths verbatim -->
| script | writes |
|---|---|
| `run_qc.py` (M0) | quality metrics for every trace in the manifest into `qc_metrics.csv`, each with its z-scores against its condition siblings, its residual-tail trim record and its outlier mark |
| `port_to_mirror.sh` | the measured whole-tree port to the public mirror: tracked set against tracked set, data_raw/ excluded in both directions because the two copies differ by design, deletions carried (a copy-only port cannot carry a rename), refusing to run unless both worktrees are clean |
| `run_kernel_budget.py` (A1) | the uncertainty statement as three side-by-side quantities, the peak spread reported as a diagnostic in three labelled readings rather than folded into a budget, and the source-discriminator table naming the measurement that would distinguish each candidate origin |
| `run_orthogonal_levers.py` (B2) | the orthogonal levers as roles in an information geometry rather than a ranking, because the homogeneous components add exactly and each lever supplies one coordinate while the others are held fixed. Every row carries the assumption its orthogonality rests on; the temperature row states that its orthogonality is intended and not established, and names the controls a campaign would need |
| `run_campaign_twin_forecast.py` | both campaign arms through the twin, Monte Carlo over simulate, fit and read the covariance. The comparison axis is what each arm identifies, after an earlier Delta_alpha-only framing was withdrawn |
| `_producer_lock.py` | an exclusive lock for any producer that writes `results/`. Not a producer itself. Two producers were each launched twice while still running on 2026-08-27/28, and a CSV written by two processes is still a valid CSV, so nothing downstream could see the mixture |
| `run_guided_mode_tables.py` | the guided-mode tables of `docs/methods/09`, made regenerable: the mode solve at three diameters, the evanescent profile against the exponential, and the transit kernel span. Derived, not simulated, so the rows stand on mathematics |
| `run_onf_lever_ranking.py` | the three nanofibre levers ranked by information per hour, as a Fisher forecast, with the lock span that could reorder them. Separates the measured width precision from the estimated centre precision, because the committed fitter reports width channels only |
| `run_transit_additivity.py` | the guided transit kernel's second-order entry into the line width, computed two ways so a construction error cannot hide. Built after the same quantity was wrong three times in one day as a hand-fitted literal |
| `run_fibre_twin.py` (B3/O2) | the fibre twin, preregistered in `private/reviews/O2_PREREG_2026-08-22.md`. A DESIGN validation, not an experimental result: it validates that a temperature ladder can identify the intended quantities under specified synthetic worlds, and does not demonstrate that the real fibre experiment will. Carries world D, the same generator with the ladder collapsed to one rung, whose pass condition is inverted because at one rung the split must fail |
| `run_kernel_k4.py` (K4) | the blind residual atlas, the one K-chain item that speaks to whether the model class is adequate rather than to a sensitivity within it. Stacks per-condition residuals on a common axis and asks whether conditions share a shape, against a per-condition sign-flip null. Carries a synthetic control built from the fitted model, whose job is to invalidate a detection if the machinery manufactures one, and a preregistered void check. **The 2026-08-22 run is VOID by that check** and its first row says so |
| `run_kernel_k7.py` (K7) | ranks the routes to the kernel by the Fourier band each reaches, computing the tooth clock's reach from scan rate and tooth spacing at every setting the campaign could run |
| `run_kernel_k8.py` (K8) | asks whether K4's in-window structure and the out-of-window band excess share a cause, by regressing each condition's in-window amplitude on profile height and vapour density at once, weighted, with a leave-one-out. Both structures track height and neither tracks density. The mechanism is not named, because any fractional model error scales with signal |
| `run_unregenerated_claims.py` | scans the `provenance:` declarations in `docs/notes/` and emits them as rows, so the size of the no-producer gap is graded by the freshness machinery like any other number. Derived rather than listed, because a hardcoded inventory here would be the literal-in-a-producer failure it exists to measure. Writes `results/unregenerated_claims.csv`. |
| `run_saturation_probe.py --emit` | writes `results/saturation_companion.csv`, the C3d half only. Without `--emit` it writes nothing, which was its original opt-in design and is why the factors it reports reached RESULTS.md with no row behind them. The joint factor is never written here, because stage 3 states that quoting a joint number before the fit runs would be inventing one. |
| `run_cumulant_window_check.py` | computes the self-centred windowed third cumulant's survival fractions for this record's own composite line and its bare-core textbook case, at a stated window and reference shift, writing `results/cumulant_window_check.csv`. A few seconds, no traces. Exists because three hand quantifications of the same ratio disagreed in two days. The producer is the arbiter and every prose surface quotes its rows. |
| `make_twin_term_census.py` | inspects `rb5s6s.forecast`, the example's layer switches and the physics modules, and writes `results/twin_term_census.csv`: one row per model term, four answers and a provenance note each. Instant, no traces. Exists so the census is measured from signatures and layer keys, never recalled, which is the class the correction history is made of. |
| `run_scenario_forecast.py` | loads every preset under `examples/scenarios/`, refuses any the named scope cannot realise, and forecasts each across its open spans through `forecast_precision`, writing `results/scenario_forecast.csv`. About four minutes, crc32-seeded so the CSV reproduces exactly. The scenario layer's end-to-end proof. |
| `run_twin_closed_loop.py` | generates dataset_2025 worlds through the public builder, fits them by the record's own joint five-repeat protocol, and stands the recovered medians against the preregistered bands, writing `results/twin_closed_loop.csv` with verdict booleans the prose quotes verbatim. Includes its own gage: a shifted truth must fail. About eight minutes, seed-pinned. |
| `run_quantisation_crosscheck.py` | joins each condition's measured lattice step to its wing sigma, derives the range the manual's twelve bits imply, and stands every condition against the scope's settable ranges, writing `results/quantisation_crosscheck.csv`. Instant, no traces. One number checks the manual reading and the ingest chain at once. |
| `run_coverage_grid.py` | measures interval coverage under model defects the fitter lacks, fifteen configurations at a thousand law-weighted trials on eight workers, writing `results/coverage_grid.csv` with its nominal gage and its broken-kernel plant. About forty minutes, one trial one seed, a lock against a second copy. |
| `run_estimator_duel.py` | pits the full-profile likelihood against a likelihood on kappa_3 and kappa_5 under a model error the fitter lacks, writing `results/estimator_duel.csv`. Exists because sufficiency settles the comparison only when the model is right, and `fit_window_scan.csv` shows this one is not. Reports how far each estimator's bias moves when the defect appears, which is what robustness means, and not the bias itself. About two minutes, seed-pinned. |
| `run_fit_window_scan.py` | refits all 32 canonical conditions at six fit windows, scaling each trace's own adaptive half-width, and writes `results/fit_window_scan.csv`. Exists because the window was the one tunable analysis choice with no robustness axis, and it is the cheapest probe of tail model error: the tail is where a core-weighted chi-square has least leverage. Reads the narrow end as wing-clipping and not as physics, and records each realised half-width because the mirror cap makes widening saturate. |
| `run_band_excess.py` | reconstructs the band-excess ladder and joint regression from the raw traces, writing `results/band_excess.csv` with the note's historical values alongside for the side-by-side. Judged on the claim at thresholds fixed in the producer, and the verdict is NO. |
| `run_quantisation_check.py` | measures the true quantisation step of every stored trace against its baseline noise, answering whether bit depth binds (it does not, dither is 5 to 246 steps), and reads the committed noise law for what does: the power scaling of the floor, the constancy of the shot term, and the electronics intercept. Writes `results/quantisation.csv`. |
| `simulate_campaign.py` | writes a twin campaign to a directory of two-column trace files with a manifest and a README, one file per trace in the shape the real instrument exports, for either platform and either trace kind. Plots are opt-in through `--plot`, because the traces are the artefact and a figure is a reading of them. |
| `run_twin_realism.py` | exercises the redesigned digital twin across the instruments, trace kinds and platforms of the next campaign, and writes `results/twin_realism.csv`. The recovery rows fit twin output with the production fitter, so a bias there is a bias in the analysis. |
| `run_twin_span_sweep.py` | runs the digital twin at 60 and 300 MHz spans and at ten times the repeats, writing `results/twin_span_sweep.csv`. Truth is read from `linefit_conditions.csv` at a named condition and the seed is fixed, because the run whose numbers ten public surfaces quote recorded neither and cannot be reproduced by anyone. |
| `run_kernel_k5.py` (K5, K6) | whether the non-Gaussian component K3 found may be called the laser. Computes what the comb-as-clock bound would have to be converted through to predict a kernel, how far short of that it falls, and how far apart the two Fourier bands are, then classifies the transfer and takes R_kernel over whatever class survives |
| `run_kernel_k3.py` (K2.5, K3) | the mixed kernel against real data: per-peak density-ladder fits with the Lorentzian-equivalent width pinned and free, the nested likelihood ratio between them, the heterogeneity test across peaks, and the three uncertainty quantities. Validates its own G arm against the committed `beta_self` first |
| `run_kernel_worlds.py` (K2) | the five hostile worlds that decide whether a fitted `Gamma_L,equiv` is a measurement: false-positive rate against a true zero, interval coverage against a true mixed kernel, and whether a wrong baseline, a wrong transit kernel or the grid itself manufactures one. Trial count is a command-line argument defaulting to the preregistered 500, and the count used is written into the CSV |
| `run_tooth_scatter.py` | M2 stage 4b: the comb read as a clock. Keeps the per-trace tooth-position departures that `run_ruler.py` pools into the nonlinearity map, separates the repeating sweep shape from the non-repeating remainder, and bounds the laser's frequency excursion at the tooth spacing |
| `run_width_pinning.py` | what pinning the laser width buys the collisional width, the committed producer for the pinning comparison four documents quote, writing only to `private/run_logs/` |
| `run_extended_lever.py` | what the 150 and 170 C blocks would buy the collisional bound, at the committed coverage construction with the temperature grid as a parameter, writing only to `private/run_logs/` |
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
| `run_modelform.py` (M8) | Voigt against the Lehmann cusp at the cold dim extreme into `modelform.csv` |
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
| `run_projections.py` | what a further campaign would buy, computed from the record's own precision, into `projections.csv` |

## Run on their own

These are not in `run_all.sh`, either because they take too long, or because
they read a session outside the frozen record, or because they print a
diagnostic rather than write a table.

| script | writes |
|---|---|
| `run_commit_sweep.py` | how many samples the joint fit loads at each commit of a historical range, into `commit_sweep.csv`. Needs both excluded-session trees and a git worktree per commit, so it is not runnable from a plain clone. It exists because the 2026-08-14 instability was traced with it: the point count changes at one commit that regenerated the committed ruler CSVs while renaming a vocabulary |
| `run_stark_joint.py` (M23) | the joint light-shift fit over all three sessions with one shared coefficient, into `stark_joint.csv`. A long profile-likelihood run |
| `run_global_dataset_fit.py` (M25) | one likelihood over every canonical trace, collisional and AC-Stark coefficients both free, into `global_dataset_fit.csv` |
| `_m25_norulers.py` | the same fit with the ruler arm removed, into `global_dataset_fit_norulers.csv` |
| `run_full_dataset_fit.py` (M28) | the M23 construction on the M25 data, into `full_dataset_fit.csv` |
| `run_morning_ruler.py` (M26) | the campaign morning's own frequency axis, from 27 recovered EOM traces, into `morning_ruler.csv` |
| `run_wing_check.py` (M24) | whether the near-core asymmetry is a collisional wing, into `wing_check.csv`. Loads raw traces and takes several minutes |
| `run_laser_history.py` (M20) | the laser frequency within each display epoch into `laser_history.csv` and `laser_history_structure.csv` |
| `run_stark_centres.py` (M21) | what the line centres can and cannot say about the light shift, one row per drift form, into `stark_centres.csv` |
| `run_centre_stark.py` (M27) | the centre-channel coefficient from the held-lock epochs into `centre_stark.csv`, exiting cleanly if either input table is absent |
| `run_wavemeter_reconstruction.py` (M22) | the 2025-06-11 wavemeter record, digitised from its tracked photograph, into `wavemeter_reconstruction.csv` |
| `run_window_attribution.py` (M28) | how much of the between-block peak-position move is the oscilloscope's horizontal setting, into `window_attribution.csv`. This is why the campaign has line shapes and no line centres, and the number had been published on four surfaces with no producer until this module was written |
| `run_centre_fisher.py` (M29) | what a freely fitted drift costs the centre channel, into `centre_fisher.csv`. Its ladder-order rows say what cycling the power through a display epoch would buy, on the campaign's own traces and times |
| `run_collisional_shift_bound.py` | the collisional (pressure) shift the model omits, into `collisional_shift_bound.csv`: the borrowed genus-level ceiling through the vapour-pressure chain with the density-scale systematic applied by construction, this atom's own expected shift beside it, and the ratio against the light-shift bound. The temperature grid is an argument, which is what makes a differential over the wrong range unwriteable |
| `run_delta_alpha_posterior.py` | the differential polarizability the data alone support, into `delta_alpha_posterior.csv`: the one-sided 95 per cent limit in both constructions of the committed profile, their ratio, the distance of the fit from zero, and how the error splits between the data and the geometry priors. It reconstructs nothing: the committed profile is the likelihood, and its provenance row reports that profile's own numerical scatter, so the resolution floor is visible instead of assumed |
| `run_drift_settling.py` | the lock disturbance against time, off the committed clock, printed rather than written |
| `run_intrablock_trend.py` | whether the position scatter within a block is drift or jitter, printed rather than written |
| `run_epoch_checks.py` | the campaign-morning and 4 July cross-checks of the clock, the disturbance model and the cross-day calibration, printed, with nothing entering `results/` |
| `run_polarizability_ladder.py` | the three-transition polarizability ladder, printed, plus `figures/fig9_polarizability_ladder.png` |
| `run_s0_block_bootstrap.py` | the block bootstrap of the power-lever limit, one row per resample, under `private/run_logs/` rather than `results/` |
| `run_stark_coverage.py` | M14, the injection-recovery coverage of the power-lever 95% bound, which had never been measured for this estimator. Two noise arms across a ladder of true kappa, one row per trial under `private/run_logs/` rather than `results/`. Preregistered in `docs/notes/stark_coverage_prereg.md` |
| `run_cavity_scan.py` (M30) | the cavity-scan photograph digitised and integrated into `cavity_scan_integrals.csv`, the one result whose input is an image |
| `run_campaign_conditions.py` | what a next campaign's waist, power, temperature and choice of transition do to the six effects this record has measured, printed rather than written. Its three answers are the per-line lever becoming spendable at a tighter waist, the infrared halo growing thirtyfold over the hot extension the collisional programme wants, and the blackbody test that orders the transition menu |
| `run_companion_refit.py` | the preregistered refit with the two width companions inside the fitted model rather than beside it, scored against `docs/notes/companion_inclusive_refit_prereg.md`. Writes nothing, and checks the option is inert before reading any result. Its answer is that the per-line scale is unidentifiable on this dataset, because it enters only as a multiple of a light shift the dataset bounds rather than measures |

## Figures and documents

| script | writes |
|---|---|
| `make_figures.py` | the publication PNGs in `figures/`, from the committed CSVs, each stamped with a fingerprint of the tables it was drawn from |
| `make_fig0_spectrum.py` | `figures/fig0_spectrum.png`, one representative fitted spectrum |
| `make_wiki_figures.py` | the teaching panels in `docs/wiki/figures/`, drawn from closed forms and fixed-seed synthetics, reading no results |
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
| `import_data.py` | the one-time, idempotent import of the 2025 dataset into `data_raw/`, deduplicating by MD5 and writing `MANIFEST.csv` |
| `annotate_manifest_qc.py` | refreshes the `qc_reason` provenance column of `data_raw/MANIFEST.csv` in place, leaving the other columns untouched |
| `check_moved_values.py` | greps for every literal a `results/` cell held anywhere in the unpushed range, scoped to files that cite that CSV, with bands graded as bands and `docs/history/`'s `now` column graded while its `was` column is not. The complement of `check_references.py`, whose population is the values carrying a `ref:` tag: a plain typed copy is outside it, and eighteen such copies survived a correction wave until this was written. **It cannot see a number that never matched the CSV**, which its own plant demonstrated; that class belongs to the `ref:` tag |
| `check_references.py` | resolves every inline data reference (a markdown link whose title is a `ref:` key) against its CSV cell or literature values row, with `--fix` for pure-value link texts and `--graph` for the derived dependents map |
| `check_release_notes.py` | the register banks plus the release-note style rules (word ceiling, shorthand-code ban, narrative markers, `docs/RELEASE_NOTE_STYLE.md`) applied to a release body or any other untracked prose, since a release body is not a tracked file and nothing else looks at it |
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
needs the two outside trees. `update_test_counts.py` rewrites the three
places `docs/methods.md` advertises the suite size, reading them from a
pytest collection rather than from memory. It exists because that number went
stale five times in three days: several tests are parametrized over
documentation files, so adding a page changes the count, and one wiki wave
moved it by more than a hundred. Run it after adding or removing tests or
documents, or `--check` to ask whether the file is current. `run_geometry_design.py` computes the two
geometry designs of `docs/notes/running_wave_and_waist_design.md`, the
frequency-shifted retro arm and the waist, and its weak-field branch
reproduces `lineshape.stark_ramp_axial_moments`, which is what licenses the
saturated branch beside it. `run_widescan_design.py` sizes the wide-scan
block of `docs/notes/widescan_block_design.md` and PLAN section 10a, deriving
the span, record length and piezo shape from the 2025 acquisition it has to
beat, forward-modelling the pedestal the settings would reveal, and printing
the go/no-go checks for the day. It prints the naive detection significance
beside the corrected one deliberately, because the naive count over-promises
by two once correlated noise and the free background are taken out. `run_zeeman_depletion.py` does the hyperfine
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
`run_epoch_checks.py` read the campaign-morning and 4 July sessions, which sit outside
the frozen record and outside the repository, and `run_morning_ruler.py` reads
the campaign-morning tree. Given a missing tree each of them prints what it cannot find
and exits 0, so the committed CSV stays the record. `publish_recovered.py`,
`build_clock_table.py` and `run_timestamp_audit.py` want the excluded backup
copies in the same way.

Three run in part. `make_figures.py` draws everything its committed inputs
support and prints a line for each panel it skips, including the one panel that
needs a ruler trace. `run_drift_settling.py` skips the half that reads the
temperature-session rulers and returns the power-session steps, which come from
the committed quality table. `verify_results_fresh.py` checks its default set
without traces and needs them only under `--all`.

Three producers added on 2026-08-19 and 2026-08-20 answer questions the
campaign raised rather than stages of it. `run_skew_scaling.py` fits the
residual skew's amplitude exponent and tests each competing hypothesis by
simulation rather than from the fit covariance.
`run_polarisation_bound.py` turns the two isotopes' width difference into a
ceiling on any magnetic term carrying an uncancelled g_F.
`run_cooperative_channel.py` computes the two-atom two-photon channel, which
opens the Delta m_F = +-2 position a single atom must refuse, and shows it
sits ten orders below the line.

`run_laser_kernel.py` (M38) fits every canonical condition twice, differing
only in the laser kernel's shape, and reports what that assumption costs the
collisional coefficient. It needs the raw traces. Read its per-condition
`gamma_coll` columns with `run_kernel_identifiability.py`'s result in hand:
under a Lorentzian kernel only their sum is identified at fixed condition.

`run_kernel_headline.py` (K1) asks the same question of the headline
coefficient, fitting each peak twice under the record's own hierarchical
estimator, where varying density is what separates a collisional width from a
laser one. It reports the correlation between beta_self and the shared laser
width under each kernel, which is what says whether the density ladder is
breaking the degeneracy. It needs the raw traces.

`run_onf_candidate.py` sizes the nanofiber candidate for the campaign
ranking: every number in docs/notes/onf_candidate.md, each row labelled with
its basis so an expectation can never be quoted as a measurement. It runs
from a clone in under a second.

`run_kernel_identifiability.py` (K0) takes no data at all and runs in seconds.
It asks what the model can identify before anything is fitted: the Jacobian at
a fixed condition under each kernel, a direct sum-invariance test with a
should-fail control, the mixed G+L model validated against the shipped code in
both limits, and the hierarchical Fisher matrix with the intercept slots free
as well as frozen. It runs from a clone.

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
