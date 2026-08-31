# Committed results

These CSVs are the outputs of the documented run of the pipeline (the numbers
quoted in the top-level README "Results at a glance" and `docs/DATA.md`), committed so the claims
are verifiable without re-running. They regenerate exactly by running the
scripts in order (see the top-level README "Reproduce" section). Every output the
pipeline writes is committed, the per-trace QC dump `results/qc_metrics.csv`
included, which is what lets the drift path reproduce from a clone.

Reproducing them to the printed digit also takes a stated environment, and
that statement is [`ENVIRONMENT_OF_RECORD.md`](ENVIRONMENT_OF_RECORD.md) in
this directory. The supported floor and the environment these files were
produced in are two different claims, and only the second reproduces the
digits the CSVs store.

**Every row carries a machine-readable `status` column** (`scripts/annotate_results_status.py`,
run after every producer and before anything that reads the column) so the caveat travels *with the number* into any plot
or table, so a bound never reads as a measurement. The controlled vocabulary:
**`BOUND`** (a limit and not a measurement, so β_self, σ_laser and S₀ each sit
conditional on the beam waist w₀, which is **64 µm, measured** on this apparatus
lineage by Rajasree 2020 on the same laser model, lens and retro geometry, and
which this dataset cannot re-measure because transit and laser width are
degenerate through it. A 2026-07-13 fix to the transit Monte Carlo first
re-centred it from a 32 µm nominal to about 50 µm, before the lineage
measurement replaced the estimate. See `docs/notes/transit_width_resolved.md`).
**`NULL`**
(below detection, or no model preference). **`MEASURED`** (a fitted value with
no open systematic, which is the frequency rate, the P² scaling and the
γ-floor). **`PRELIM`** (a model-dependent
cross-check replaced by a BOUND headline). **`ARTIFACT`** (identified noise,
not physics). **`DIAGNOSTIC`** and **`CALIB`** (fit-quality and calibration
intermediates). **`ENVELOPE`** (order-of-magnitude, or w₀-parametric,
estimate).
`laser_epoch.csv` and `qc_metrics.csv` carry their own `status`/`flag` instead.

| file | produced by | holds |
|---|---|---|
| `noise_model.csv` | `run_noise.py` (M1) | per-condition noise law a, b, τ_int |
| `commit_sweep.csv` | `run_commit_sweep.py` | samples and traces the joint light-shift fit loads at each commit of a range, and the adjacent pairs across which that count changes. Diagnostic: it is how the 2026-08-14 instability was traced to a rename that regenerated the ruler CSVs |
| `polarisation_bound.csv` | `run_polarisation_bound.py` | a ceiling on any magnetic term carrying an uncancelled g_F, from the isotope width difference. Broadening goes as g_F squared, fixed at 2.25 between the isotopes, so the difference bounds it. The forward-to-retro mismatch this was written for is retracted (docs/wiki/magnetic-sublevels.md), and what it now bounds is the two-atom cooperative satellite |
| `cooperative_channel.csv` | `run_cooperative_channel.py` | the two-atom two-photon channel. A pair can accept the two units of angular momentum a single J=1/2 atom must refuse, which puts a satellite at the Delta m_F = +-2 position. Three blocks: the pair resonance is unique and the runner-up is 23 THz off, the satellite positions for both topologies, and the rate as a fraction of the single-atom rate at a stated cutoff |
| `laser_kernel.csv` | `run_laser_kernel.py` | what the laser kernel's shape costs. Every canonical condition fitted twice on the same traces and the same noise law, differing only in `laser_kind`. A Lorentzian laser width is degenerate with gamma_coll and competes for the same wings, so at fixed condition only their sum is identified: the per-condition gamma_coll column is not a measurement under the lorentzian kernel and the sum column is. The Gaussian gives the lower chi2 at 32 of 32, which is a comparison at unequal effective parameter count -- see kernel_identifiability.csv and kernel_headline.csv |
| `kernel_identifiability.csv` | `run_kernel_identifiability.py` | what the archive can and cannot identify about the laser kernel, before anything is fitted. The Jacobian, the direct sum-invariance test with its should-fail control, the mixed G+L model validated against the shipped code in both limits, and the hierarchical Fisher matrix with the intercept slots free as well as frozen. Runs in seconds so the contract exists before the inference |
| `kernel_worlds.csv` | `run_kernel_worlds.py` | K2: whether a fitted Gamma_L,equiv may be read as a measurement, and under which conditions. Five hostile worlds at 500 preregistered trials each, all multi-condition because at a fixed condition Gamma_L,equiv is exactly degenerate with gamma_coll and only their sum is identified. A true-Gaussian world for the false-positive rate, a true-mixed world for interval coverage, a wrong-baseline and a wrong-transit world for whether misspecification manufactures a kernel, and an exact-symmetry world that tests the instrument rather than the model. A, C, D and E holding is what licenses K3 as a measurement; world B's coverage qualifies its intervals |
| `kernel_k3.csv` | `run_kernel_k3.py` | K2.5 and K3 against the real archive. Each peak fitted twice across its 70/90/110/130 C ladder, G with the Lorentzian-equivalent width pinned at zero and G+L with it free, compared by a nested likelihood ratio with the null on its boundary. Carries the validation that the G arm reproduces the committed beta_self, without which the difference is between producers rather than between kernels, the per-peak heterogeneity test that decides whether one global scalar is admissible at all, and a provisional U_statistical, U_kernel and R_kernel computed over the fallback class before K5 has classified. **The final values live in `kernel_k5.csv` under key `K6`**, and a reader after R_kernel wants that file: K6 runs after K5 because K5's classification is the class its numerator is taken over. G+L winning supports a non-gaussian homogeneous component and attributes nothing to the laser |
| `kernel_k5.csv` | `run_kernel_k5.py` | K5's attribution triangle and K6, which runs after it. Leg A is K3's finding. Leg B carries the one in-situ laser measurement, the comb read as a clock, through the transfer that would be needed to predict a kernel from it, and finds that transfer not established: the conversion requires a noise type the record measures nowhere, and even granting the most favourable type the bound permits a width 1857 times the one measured while sampling a Fourier band 5.9e4 away from it. Leg C is therefore not attempted and laser attribution is not licensed. K6 then takes R_kernel over the class K5 leaves, the data-allowed fallback |
| `kernel_k7.csv` | `run_kernel_k7.py` | K7: which routes could close the kernel question, ranked by what they reach rather than by cost, because K6 fired the stop condition and K5 found the attribution unlicensed. The tooth clock's Fourier reach is scan rate over tooth spacing and is computed at every campaign setting, including the tunable modulator drive: the best reachable is 17 kHz against the 398 kHz band that carries the answer, so the comb route is demoted from a route to the Lorentzian content to what it actually measures. A direct frequency-noise spectrum is ranked first and costs no cell time |
| `estimator_duel.csv` | `run_estimator_duel.py` | A twin injects a known light shift and estimates it by the profile fit and by an odd-cumulant likelihood. The fit wins at the injected 3 MHz and loses at the archive's 0.35 MHz; under an asymmetric defect its bias moves 65 times further. Earlier centrings are rows of their own. A mechanism, not the archive: [methods §4.14](../docs/methods/06_the_statistics.md) carries the table. |
| `fit_window_scan.csv` | `run_fit_window_scan.py` | The fit window as a robustness axis: every canonical condition refitted at six windows. **The fitted collisional width falls with widening window in 30 of 32 conditions over the wing-safe range** (`n_drift_negative`, `wing_safe_mults`, `sign_test_p` rows) while fit quality stays flat (`chi2_red_median` rows), and the indicative slope spans the `gamma_density_slope` rows. The full treatment is [methods §4.14](../docs/methods/06_the_statistics.md). Every row is DIAGNOSTIC and none may be quoted as a value. |
| `cumulant_window_check.csv` | `run_cumulant_window_check.py` | What a self-centred windowed third cumulant keeps of the ramp's own $S_0^3/135$, for this record's line, kernel conventions named in every note: the `survival` rows (0.42 to 0.34 full line, 0.58 to 0.49 bare core at the 3 MHz reference), the `survival_vs_S0` rows (finite at small shifts, 0.20 at the archive's own 0.35 MHz), and the mean pull's sub-quarter-per-cent windowed deficit, every row convergence-checked at doubled resolution. The rows every prose statement of the three-layer result quotes ([methods §4.14](../docs/methods/06_the_statistics.md)). |
| `band_excess.csv` | `run_band_excess.py` | The band-excess construction reconstructed with a committed producer, which the 2026-08-17 note never had. **The census reproduces exactly (79 traces) and the verdict row reads NO**: the low-order positive amplitude survives, the cubic-surviving amplitude and the joint height significance do not, and the reconstructed predictors are collinear at 0.896 where the note reported 0.415, so the note's construction was under-specified. The note's historical values ride along in the note fields for the side-by-side. |
| `saturation_companion.csv` | `run_saturation_probe.py --emit` | The C3d half of the saturation companion probe: the committed width-only bound reproduced by the unpatched arm, the same bound with the saturation increment folded in at both ends of the Omega-over-S0 band, and the two tightening factors documents quote as about 2.8. **The joint factor is not here as a digit**, because stage 4 needs data trees outside this repository, and it is recorded as a classification with the date of the run that produced it. No committed bound moves on any of this. |
| `quantisation.csv` | `run_quantisation_check.py` | Is the digitiser step below the noise? Across all 35 quality-passed conditions the baseline noise is 5.2 to 246 times the true quantisation step (median 37), so the quantiser is dithered and contributes at most 0.155 per cent of the noise. The budget rows carry what binds instead: the baseline noise grows linearly with power (light-linked background), the level term is constant (cathode shot), and the electronics floor sits well under both, so the transimpedance gain is in the right decade. |
| `twin_realism.csv` | `run_twin_realism.py` | What the redesigned twin records and recovers. Each instrument at its own record length and vertical step, one-peak and four-peak traces, the production fitter recovering a known truth to within a few per cent, and the two platforms side by side: the heated cell radiates against itself while the nanofibre radiates against a 300 K room whatever its microkelvin atoms do. |
| `twin_span_sweep.csv` | `run_twin_span_sweep.py` | Does widening the scan span break the width degeneracy? The twin says no, on ground anyone can regenerate: truth read from a named committed condition, seed fixed. The correlation moves 0.0075 over a five times wider span and **0.0000** at ten times the repeats, while the collisional-width uncertainty falls by 3.16, the root of ten. **It does not reproduce the historical -0.9177/-0.9166/-0.881**, whose run recorded neither truth nor seed, and it says so. |
| `unregenerated_claims.csv` | `run_unregenerated_claims.py` | A governed row about ungoverned numbers. Every freshness instrument here starts from a `results/` row, so a published number that never became one is outside all of them. This scans the `provenance:` declarations in `docs/notes/` and counts them, including how many notes rest on computations nothing regenerates and how many individual claims remain unaccounted for inside declared notes. It measures the gap and does not repair it. |
| `kernel_k8.csv` | `run_kernel_k8.py` | K8: whether the in-window residual structure K4 detects is the same phenomenon as the band excess outside the window. Each condition's in-window amplitude is regressed on the model's own profile height and log10 vapour density at once, weighted by that condition's own amplitude error, because the least reliable residuals are the dim ones and height is lowest there. Height wins at 9.4 sigma and density gives 1.3, predictors correlated only 0.49, height surviving every leave-one-out above 8.5. The band excess gives 8.65 and -0.75 on the same predictors by the same method, so both structures share a predictor and both exclude density. The mechanism is not named: a normalised residual scales with signal under any fractional model error, so profile mismatch, a detector nonlinearity and an amplitude-dependent baseline all predict it. A density-driven collisional origin is excluded |
| `kernel_budget.csv` | `run_kernel_budget.py` | A1: the kernel uncertainty statement, deliberately three quantities side by side rather than a total. U_stat and R_kernel are carried through as established; the peak-to-peak variation of Gamma_L,equiv is a DIAGNOSTIC and is not combined with them, because the four peaks are estimates under four different spectral conditions rather than exchangeable draws of one parameter, and p = 0.097 does not establish a random-effects model. Its three readings each state the question they answer. The most useful rows are the discriminator table: each candidate origin of the spread with the measurement that would distinguish it |
| `orthogonal_levers.csv` | `run_orthogonal_levers.py` | B2: the five orthogonal levers, each with what it separates, its role in the information geometry, and the assumption its orthogonality rests on. Deliberately not a ranking: spectroscopy measures the integrated homogeneous response, so the levers are complements and K5's attribution triangle needs the independent laser diagnostic whichever spectroscopic lever is chosen. The guided transit kernel enters at second order (`transit_additivity.csv`), so exact additivity holds for the Lorentzian pair and not for the set. Only the density row is demonstrated, and the rest are prospective |
| `campaign_twin_forecast.csv` | `run_campaign_twin_forecast.py` | what one new campaign buys, vapour cell alone against cell plus nanofibre, run through the twin. Reports what each arm identifies, and not a single scalar: the collisional-against-Gaussian correlation is about -0.94 in both arms, and the fibre's cost is about 69 minutes per trace at the demonstrated count rate |
| `guided_mode_tables.csv` | `run_guided_mode_tables.py` | the three tables `docs/methods/09` prints, as rows: the HE11 solve at 350, 370 and 400 nm, the evanescent flux against distance beside the exponential it replaces, and the transit FWHM under all four kernel treatments. Written because those numbers were typed into prose from a computation run once, which is the published-number-with-no-producer class this record names. Runs from a clone in under a second |
| `onf_lever_ranking.csv` | `run_onf_lever_ranking.py` | which nanofibre knob buys the most per hour, as a Fisher forecast over each lever's rungs. The centre-channel levers are lock-limited and not signal-limited, which the input rows separate |
| `transit_additivity.csv` | `run_transit_additivity.py` | how much of the guided transit kernel's own width actually reaches the observed line.  It enters at second order, not linearly, so it contributes a fraction of itself and what a temperature ladder reads grows as T and not as sqrt(T). Two independent routes, and their difference is emitted as a row because the defect this producer was built after survived by two computations disagreeing with nothing comparing them |
| `fibre_twin.csv` | `run_fibre_twin.py` | B3/O2: coverage of the temperature-ladder design under synthetic worlds, at both decay-length band edges, plus world D (ladder collapsed to one rung, inverted pass condition) and world F (a wrong temperature law as an alpha ladder). The world's information content is calibrated to the archive's demonstrated per-condition width precision rather than chosen. Simulation-backed at best and never demonstrated |
| `kernel_k4.csv` | `run_kernel_k4.py` | K4, the blind residual atlas. **Read its first row before any other**: the 2026-08-22 run is inadmissible, because the preregistered void check fired at one condition of thirty-two while the other thirty-one reproduce to a median of 6.6e-08. The detection rows it carries may not be cited. The file is committed rather than discarded because a void run with its cause localised is evidence about the instrument, and because the criterion was not loosened after the result was visible |
| `onf_candidate.csv` | `run_onf_candidate.py` | the nanofiber candidate, sized. What a measurement beside the lab's ONF would buy: the cold mode as a laser-width instrument once a trap fixes the atom-surface distance, the atom-surface tail as a C3 measurement for the 6S state, hot vapor as a transit-kernel test, and the Stark geometry seam exercised for free. Every row carries its basis (committed_input, cited_literature, assumed_parameter, derived_expectation) and nothing in it is a measurement. Runs from a clone in under a second |
| `kernel_headline.csv` | `run_kernel_headline.py` | what the laser kernel costs the headline coefficient, per peak, under the record's own hierarchical estimator. Carries the correlation between beta_self and the shared laser width under each kernel, which is what says whether the density ladder is breaking the degeneracy or not |
| `skew_scaling.csv` | `run_skew_scaling.py` | the exponent of the residual skew against line amplitude, per line and pooled, with each competing hypothesis' own simulated sampling distribution rather than the fit covariance |
| `ruler_blocks.csv`, `ruler_traces.csv`, `ruler_nlmap.csv` | `run_ruler.py` (M2) | sweep rate per block/trace, and the nonlinearity map |
| `ruler_tooth_scatter.csv` | `run_tooth_scatter.py` (M2 stage 4b) | the comb read as a CLOCK rather than as a ruler. Each tooth centre is refit freely and compared with its own trace's rigid ladder. The mean of those departures across traces is the sweep nonlinearity, because the ramp repeats, and the scatter about it is the laser, because it does not. Over 509 teeth from 104 canonical RF-on traces the scatter sits at chi2/dof = 0.53, so there is no excess and the row to quote is `excursion_ub95_transition`, a 95 per cent limit of 28.3 kHz on the transition axis at an averaging time of 0.15 s. The limit covers the non-linear part only: a linear drift within a sweep is exactly degenerate with the sweep rate, and separating it needs the two halves of a triangular sweep, which the manifest does not label. A BOUND, and the record's only direct in-situ statement about the laser's frequency noise. |
| `ruler_campaign.csv` | `run_ruler.py` (M2) | the authoritative campaign rate (inverse-variance + PDG scatter inflation), the ledger reads this rather than re-averaging the blocks. Since 2026-08-04 it also carries `rate_est_spread` (half the range of eight legitimate estimators of the same blocks), `position_mismatch_relerr` (the rulers and the lines sit at different places in the acquisition window, read against `ruler_nlmap.csv`) and `rate_err_total` (the statistical error and the estimator spread in quadrature). The two fractional terms are folded into the block-coherent rate error every width carries. `rate_laser_err` is not folded again, since the per-block statistical error already is it. |
| `trim_report.csv` | `run_trim_report.py` | DIAGNOSTIC. Every residual-tail trim and every outlier removal the pipeline made, one row per trace per stage (`qc`, `ruler`, `linefit`, `outlier`), collected from the tables that made them. A record of what was cut, never an input to anything. The `linefit` rows leave `trimmed` empty: the condition fit runs the trimmer but `run_linefit.py` does not persist a per-trace record, and an empty cell is not a claim that nothing was cut. That producer prints the count it took. |
| `linefit_conditions.csv` | `run_linefit.py` (M3) | per-condition joint-fit widths |
| `beta_self.csv`, `beta_self_probe.csv` | `run_beta_self.py` (M4, C1) | two different quantities despite the similar names. `beta_self.csv` holds the per-peak model fits. **`beta_self_probe.csv` holds the model-independent width-slope bound `bound95`, which is the C1 headline.** Four things travel with these columns and are set out below, under [beta_self.csv and beta_self_probe.csv](#beta_selfcsv-and-beta_self_probecsv) |
| `global_fit.csv` | `run_global_fit.py` (M4b) | the **authoritative hierarchical β**, with σ_laser shared per temperature across peaks and β fitted per isotope. It replaces the per-peak file for the isotope question, and its σ_laser trend is not a physical laser drift. See [global_fit.csv](#global_fitcsv) |
| `lever_crosscheck.csv` | `run_lever_crosscheck.py` (M4d) | **a lever-limited cross-check estimator, not the headline β**, with the systematic budget as separate columns and the lever test that makes β a bound. Column by column in [lever_crosscheck.csv](#lever_crosscheckcsv) |
| `sigma_laser_sharing.csv` | `run_sigma_laser_sharing.py` (M4c) | the σ_laser Model-A-vs-B test: per-T χ²/dof of the 4 peak-blocks (χ²<1: an in-sample check that cannot discriminate, not a validation) + free vs β·N-tied common σ_laser (the trend is degeneracy, not drift) |
| `laser_epoch.csv` | `run_laser_epoch.py` (M5, C2) | σ_laser upper bound + w₀ band |
| `power_sweep.csv` | `run_power_sweep.py` (M6, C3) | FWHM/amplitude/skew vs power. **`resid_skew` is the residual skew of a symmetric fit**, large & positive at low power (up to ~10σ) but it is shot-noise skewness (∝1/√counts, falls with power), not the AC-Stark ramp (which would grow as P³); see RESULTS.md C3c. |
| `stark_sweep.csv` | `run_stark_sweep.py` (M4e, C3d) | the AC-Stark coefficient BOUND from the power lever: one shared κ (S₀=κP) fit to the 130 °C FWHM-vs-power (from `power_sweep.csv`). **`S0_225mW_ub95_profile`** is a 95% profile-likelihood upper bound of 0.63 MHz on S₀ at 225 mW, just above `S0_225mW_pred` (0.35); replaced as the headline by `stark_joint.csv` (three sessions, < 0.26 MHz) and kept as the independent width-only bracket. (The Wald `S0_225mW_ub95`=3.1 / `_ub95_raw`=1.5 are replaced diagnostics: the fit rails at κ=0, where a linearized error has no coverage.) A BOUND, not a measurement: the shift is dead in the 2025 drift, so only the ramp's width broadening (∝S₀²) constrains κ, and `chi2_red`≈4 (block-to-block width scatter) is folded into the bound. a fixed lock would measure the pull ∝S₀ directly. |
| `stark_joint.csv` | `run_stark_joint.py` (M23, C3f) | **the headline light-shift bound, S₀(225 mW) < 0.26 MHz**, from a joint fit over the full profiles of 172 traces in three sessions. The construction, the robustness spread that is its dominant systematic, and the conservatism since measured on it are in [stark_joint.csv](#stark_jointcsv) |

**A known lag, 2026-08-25**: this file's two prediction cells (`kappa_pred` 1.545, `S0_225mW_pred` 0.348) were computed under the previous differential polarizability. This record's own value became the package default that day, under which they are 1.618 and 0.364, and `stark_sweep.csv` regenerated to the new numbers while this file cannot: its producer needs about five hours and the excluded 2025-07-04 tree. **Its bounds are unaffected** (data-driven, and they use the magnitude), and the exclusion strengthens. The two files therefore disagree by 4.6 per cent on the same predicted quantity until this one runs again, which is stated here so a reader meets it beside the file.

| `amplitude_trapping.csv` | `run_amplitude_trapping.py` (M7) | amplitude vs density |
| `morning_ruler.csv` | `run_morning_ruler.py` (M26) | the campaign-morning session's own frequency axis, from 27 recovered EOM rulers no analysis had opened: Def-group rate 0.042538(51) MHz/ms → a **measured** `pilot_rate_scale` = 1.0022(12) against the campaign 4192 rate, replacing the fitted [0.9, 1.1]-boxed nuisance both joint fits put at 1.02–1.03. The 17σ gap between measured and fitted is an open question the next joint re-run answers: either the campaign-morning science scan differed from its own rulers, or the fitted scale was absorbing width physics. Nine pre-adjustment traces rail at the fit bound and are flagged, never averaged. Producer needs the private campaign-morning tree, so the committed CSV is the record. |
| `modelform.csv` | `run_modelform.py` (M8) | Voigt-vs-Lehmann BIC |
| `transit_mc.csv` | `run_transit_mc.py` (M9) | Monte-Carlo transit-broadening FWHM vs (w₀, T, collection geometry), with the crossing-flux factor (fixed 2026-07-13, validated against Lehmann's 41.2 kHz NNO example): the transit kernel adds ~2.1 MHz at w₀=32 µm in the thin single-waist limit, but only ~1.6 MHz over a realistic multi-mm collection column (the beam defocuses across it), so the line alone does not decisively exclude 32 µm, that exclusion now rests on the direct waist measurement instead (w₀≈64 µm, Rajasree 2020). The grid's nearest point, 65 µm, gives transit ≈0.88 MHz, and at the measured 64 µm `TRANSIT_FWHM_PLACEHOLDER_MHZ` (`constants.py`) gives 0.93 MHz, and it stays degenerate with σ_laser through w₀, which this dataset cannot re-measure even though the apparatus lineage did. Seeded on `C.RNG_SEED`, so byte-reproducible. |
| `amplitude_ratios.csv` | `run_amplitude_ratios.py` (M10) | degeneracy-law area ratios: measured vs predicted abundance×(2F+1), with `pull_sigma`. The measured ratios swing 30–50% between blocks (common-mode drift), so the law is **untestable in the dataset**, a cross-peak systematic that interleaving in a fixed-lock session would fix. Per-peak and within-block analyses are unaffected. |
| `model_ladder.csv` | `run_model_ladder.py` (M11) | DIAGNOSTIC. Nested-model ΔBIC ladder, which kernels the data actually demand. |
| `identifiability.csv`, `identifiability_profile.csv` | `run_identifiability.py` (M12) | DIAGNOSTIC. The σ_laser↔transit↔β degeneracy made explicit: correlation structure and 1-d profile-likelihood curves. `identifiability_profile.csv` is the dense profile scan (~1.9k rows), not a results table, read the summary file first. |
| `coverage.csv` | `run_coverage.py` (M13) | DIAGNOSTIC. Injection-recovery coverage of the 95% constructions (are the bounds honest?), plus the minimum detectable β. Validates the intervals, and is not itself a physical result. |
| `sharing_bic.csv` | `run_sharing_bic.py` (M14) | DIAGNOSTIC. Model-selection view of σ_laser sharing (per-T vs per-block), companion to the M4c χ² check in `sigma_laser_sharing.csv`. Neither validates the sharing, see the C2 note above. |
| `fringe_tail.csv` | `run_fringe_tail.py` (M15) | DIAGNOSTIC/ENVELOPE. Standing-wave fringe-resolved tail of the AC-Stark ramp: how much the slow-v_z population skews the ramp, ~26–28% skew suppression at a 16 µm waist. Seeded, byte-reproducible. |
| `polarizability.csv` | `run_polarizability.py` (M16) | DIAGNOSTIC/ENVELOPE. Independent Δα(993 nm) recompute (−1145 a.u.; \|Δα\| within ~5% of Orson 2021 but opposite sign, adjudicated 2026-08-24 and now the package default, THEORY_NOTE §5; a decision on the theory, the sign being unset by experiment), validated against tune-out and static-polarizability anchors the model does not use, plus the first 5S–6S magic wavelengths (scalar only, ENVELOPE). |
| `resolving_power.csv` | `run_resolving_power.py` (M17) | DIAGNOSTIC. Whether each observable can answer the density question at all: dynamic range over the 70–130 °C sweep divided by block-to-block scatter at fixed conditions. Amplitude clears its floor ~45×, the widths 1.5–5.3, which reproduces this ledger's own MEASURED-vs-BOUND assignments. Also carries the fixed-lock projection and a permutation test of the averaging assumption under the S₀ bound (p = 0.11: untested, not contradicted). |
| `noise_law_swap.csv` | `run_beta_self.py` (M1/M4) | DIAGNOSTIC. Robustness of the headline bound to swapping the M1 noise law, a sensitivity check, not a separate measurement. |
| `projections.csv` | `run_projections.py` | ENVELOPE and CALIB only, never a result. What a further campaign would buy, computed from the dataset's own measured precision and the session parameters `docs/PLAN.md` states: the fixed-lock pull channel, β_self, the 7S adjudication, the 778 nm calibration rung, the magic-wavelength scan, and the guided-mode option. `proj_*` rows are the projections, `input_*` rows the dataset quantities they are built from, and every row carries its own formula, assumption set and source. Every input quoted in MHz rides on the current sweep-rate calibration, so re-running the producer after the ruler re-validation re-derives the whole table with no edit. |
| `global_dataset_fit.csv`, `global_dataset_fit_norulers.csv` | `run_global_dataset_fit.py`, `_m25_norulers.py` (M25) | BOUND. The two arms of the same construction over every canonical trace, with both the AC-Stark coefficient and `beta_self` free rather than one held under a prior. The no-rulers arm is a deliberate duplicate rather than a wrapper, which is the point: a defect fixed in one has to be fixed in the other, and one was. Each carries `beta_grid_step` and a `beta_profile` scan, and the 95% edges are interpolated in sqrt(dchi2) on a grid refined until the interval spans four steps (PREREGISTRATION_RESULTS addendum 30). Quote the step whenever the interval is quoted. |
| `full_dataset_fit.csv` | `run_full_dataset_fit.py` (M28) | BOUND. The third vertex of the same triangle: the full dataset in one likelihood, the collisional term under this repository's own four-point measurement as a prior, and one profiled coefficient. Its contract is preregistered at `docs/notes/full_dataset_fit_prereg.md`. |
| `centre_stark.csv` | `run_centre_stark.py` (M27) | BOUND, and self-statused. The AC-Stark coefficient from the line centre inside single display epochs, which is the channel the dataset's frame problem closes. It reports a bound rather than its own point estimate, and its five control epochs, where the true power difference is zero, are its own false-positive floor. |
| `stark_centres.csv` | `run_stark_joint.py` (M23) | DIAGNOSTIC. The per-trace centres the joint fit reads, kept so the frame argument can be checked against the numbers rather than the prose. |
| `centre_fisher.csv` | `run_centre_fisher.py` (M29) | Measurement. What a freely fitted drift costs the centre channel, measured instead of asserted. It corrects a factor published in the design chapter on 2026-08-25: that figure divided by a baseline this archive cannot evaluate, because a centre here already has its per-epoch mean removed. The conclusion is unchanged and the number is smaller. |
| `window_attribution.csv` | `run_window_attribution.py` (M28) | Measurement. How much of the between-block peak-position move is the oscilloscope's horizontal setting, not the atom. This is why the campaign has line shapes and no line centres, and the number had been published on four surfaces with no producer until this module was written. Two groupings are reported because the grouping is a choice: the fraction is common to both, the millisecond values are not. |
| `collisional_shift_bound.csv` | `run_collisional_shift_bound.py` | Bound and expectation. The collisional shift the lineshape does not model, given a number: the borrowed 30 MHz/Torr ceiling through this record's own vapour-pressure chain, inflated by the density-scale systematic `density.py` mandates, beside what this atom is expected to shift from the measured shift-to-width ratio. The expectation uses about seven eighths of the ceiling, so the two agreeing in size says the ceiling is nearly saturated, not that two routes corroborate. Every figure here was hand arithmetic in prose until four of them were found wrong at once. |
| `delta_alpha_posterior.csv` | `run_delta_alpha_posterior.py` | Estimator and limit. what the width channel alone says about |Delta_alpha|, taking the beam geometry as a stated prior instead of computing the shift from atomic structure and comparing. The estimator is consistent with zero, so the licensed statement is the one-sided limit and not the value. The error budget row answers a question the record could not previously answer: the geometry priors contribute a fraction of a per cent of the variance, so tighter geometry would not sharpen the posterior, though it would sharpen the quoted limit, whose whole error bar is geometric. |
| `laser_history.csv`, `laser_history_structure.csv` | `run_laser_history.py` (M20) | DIAGNOSTIC. The laser's behaviour across the campaign and whether that behaviour has structure in it. Both are read under the 2026-07-30 window-reference correction, which withdrew the licence for either knob frame, so they bound within-block behaviour and not between-block motion. |
| `wavemeter_reconstruction.csv` | `run_wavemeter_reconstruction.py` (M22) | CALIB. What the wavemeter readings can and cannot carry, with a settled noise floor of 0.62 ± 0.03 MHz from a 400-replicate residual bootstrap. The Hessian was rejected deliberately, since the profiled surface is piecewise smooth by that module's own docstring. |
| `wing_check.csv` | `run_wing_check.py` (M24) | NULL. Whether the fitted line has structure in its wings that the composite model does not contain. It does not. |
| `ruler_rate_model.csv` | `run_ruler.py` (M2) | CALIB. The rate model behind the frequency axis, kept separately from the per-block table so the model and the blocks it was fitted to can be compared without re-running either. |
| `cavity_scan_integrals.csv` | `run_cavity_scan.py` (M30) | DIAGNOSTIC. The digitised cavity-scan photograph, integrated. It is the one result in this directory whose input is an image rather than a trace, and APPARATUS section 6 records what that costs. |
| `trapping_channels.csv` | `run_trapping_channels.py` | DIAGNOSTIC and ENVELOPE, self-statused with its own `err_kind`. Radiation trapping on the two infrared cascade legs at 1324 and 1367 nm, which absorb as strongly per lower-state atom as the detected D1 line does. Inside the driven volume both are inverted and cannot re-excite. Outside it they do, at about one per cent of the primary rate at 130 °C. The halo rows carry `err_kind = geometry`, because the standoff they ride on was never recorded and the band over the plausible range is the error rather than a repeatability. |
| `blackbody_channels.csv` | `run_blackbody_channels.py` | DIAGNOSTIC and ENVELOPE, self-statused with its own `err_kind`. The cell's own thermal field, on the cascade and at the detector. Every line of this cascade sits far to the blue of where the thermal photons are, so the occupation numbers run 1e-12 to 1e-20 and nothing is driven. The two rows that are not negligible are the 6S to 6P transfer at 2.7 µm and the thermal AC-Stark shift, which is a converged principal value through those poles and carries the committed `alpha_6s_static` band as its `err_kind = polarizability`. |
| `cascade_branching.csv` | `run_zeeman_depletion.py` | DIAGNOSTIC, self-statused. The hyperfine pumping branching per line, resolved by intermediate F, with the levels that cannot reach the undriven ground level at all appearing as exact zeros. Its producer needs the optional `cascade` extra for exact Wigner symbols, so it is not in `run_all.sh` and this file is committed and read rather than recomputed. |

All values are preliminary where they carry an absolute scale: they ride on
the beam waist w₀, measured on this apparatus lineage rather than by this
dataset (see the top-level README). The headline β_self is a
bound, not a measurement.

## Four files that need more than a table cell

These four rows carried between a hundred and fifty and two hundred words each,
which is a wall inside a table and unreadable at any window width. Nothing
stated in them has been dropped. It is set out here instead, in sentences.

### `beta_self.csv` and `beta_self_probe.csv`

**The names are close and the quantities are not.** `beta_self.csv` holds the
per-peak model fits. `beta_self_probe.csv` holds the model-independent
width-slope bound in its `bound95` column, and that bound is the C1 headline.
Since 2026-08-02 both are built on the four-point 70/90/110/130 °C
construction, two degrees of freedom over a 52.5-fold density lever. The
earlier three-point 70 to 110 °C headline is replaced, and the module docstring
records why.

The word "probe" here means the width-against-density probe. It is not
`lever_crosscheck.csv`'s separate 130 °C anchor test, which is called
`beta_lever_probe_130` and is a different computation that happens to use the
same 130 °C block.

**The axis, which is the easiest column here to misread.** `sigma_laser` is the
fitted Gaussian FWHM on the transition axis, so halve it for the laser axis. It
is conditional on the transit prior, transit being a separate fixed kernel that
is degenerate with σ_laser through the waist. The per-peak values run 1.69 to
2.03 MHz on the transition axis, which is 0.85 to 1.01 MHz on the laser axis
and consistent with the C2 headline bound of under 1.2 MHz. It is not
transit-subtracted, and it is an upper end rather than a measurement.

**The β error columns here and in `global_fit.csv` are statistical only.** The
dominant C1 uncertainty is the roughly twofold spread across estimators, this
fit against the hierarchical fit against the model-independent bound, and that
spread is not a column in any per-fit file. Script against `bound95` in
`beta_self_probe.csv` rather than against these central values if what you want
is the conservative headline.

### `global_fit.csv`

**The authoritative hierarchical β**, fitted with σ_laser shared per
temperature across peaks and β free per isotope. It replaces the per-peak
`beta_self.csv` for the isotope question, and the reason is mechanical: the
per-peak fits let σ_laser float per line, so they absorb per-peak systematics
into it. Two symptoms of that show in the per-peak file, a 1.6σ internal spread
in ⁸⁷Rb between β of 0.016 and 0.018, and a σ_laser spread of 1.69 to 2.03 MHz
that cannot be physical because the laser does not differ per hyperfine line.
Constraining σ_laser jointly, the global fit finds β₈₅ equal to β₈₇ and so no
isotope difference.

**The σ_laser(T) caveat, updated by M4c in `sigma_laser_sharing.csv`.** The
per-temperature sharing across peaks is untested rather than validated. At each
temperature the four peak-blocks agree on one σ_laser only within error bars
that are themselves inflated, χ² per degree of freedom below one, which is an
in-sample check that cannot discriminate. The recovered acquisition clock then
showed the peaks were taken 54 to 76 minutes apart, so the close-in-time
justification for sharing was never true in the first place.

**The 2.054, 2.166, 1.540 MHz trend is not a laser drift.** Fitting each
condition freely gives a flat 1.53 to 1.71 MHz, so the tied fit's rise and drop
is the β against σ_laser degeneracy working under the density constraint. The
errors are statistical only, and these are not clean per-temperature
laser-width measurements.

### `lever_crosscheck.csv`

**A lever-limited cross-check estimator, and not the headline β.** The headline
stays the model-independent width-slope bound in `beta_self_probe.csv`. This
file is the cooling-sweep joint fit over 70, 90 and 110 °C with its statistical
precision and its systematic budget broken out.

Reading the columns: `beta_crosscheck` carries the value and a statistical
error, and that error is this estimator's precision rather than β's, because
the lever test below moves the central value by about 8σ.
`beta_err_transit`, `beta_err_sharing` and `beta_err_modelform` are the
model-form grid. `beta_w0_band` carries the low value and the high value over
the waist measurement band. `beta_loo_peak` and `beta_loo_temp` separate
drop-a-peak robustness from drop-a-temperature lever leverage, which are
different questions. `beta_grid_*` are the three model cells.

**The lever test is `beta_lever_probe_130` with `gamma_coll_mean_vs_T` and
`gamma_rise_factor`.** The joint β collapses from 0.036 to 0.014 when the
52.5-fold 130 °C anchor is added, because the collisional width rises only
1.85-fold across a 52-fold density span. That is a residual floor rather than
resolved collisions, and it is what makes β a lever-dependent bound rather than
a measurement.

The `beta_crosscheck` value replaces `global_fit.csv`, reproducing the same
headline byte for byte while adding the auditable budget. The
model-independent bound remains the headline of record.

### `stark_joint.csv`

**The headline light-shift bound, S₀(225 mW) below 0.26 MHz** at 95 per cent
from a one-sided profile likelihood, with `S0_270mW_ub95` giving the same
construction at the 4 July evening session's top rung. An earlier 0.15 was cold-start
inflated and is retracted in preregistration addendum 24.

**The construction.** A joint maximum-likelihood fit of the full profiles of
100 campaign, 46 4 July evening-session (LeCroy) and 26 campaign-morning
traces under one shared κ, with
per-peak widths under the β_self times N(130 °C) prior, per-trace free centres
so the drift is profiled out exactly, and per-session σ_laser and
detector-saturation nuisances, both fitted linear. Every quoted profile is the
pointwise minimum over cold, backward and search-seeded chains, and
`kappa_min` with `dchi2_kappa0` show the minimum is consistent with zero rather
than a detection.

**The robustness rows are the dominant systematic, in one direction.** Dropping
peak 4192, which removes the entire campaign-morning session with it, gives 0.37
MHz at 225 mW against the primary's 0.26, and that looseness is larger than any
single fit's error.

**`kappa_ub95_wing` is tighter than the primary, and it is a conditional bound
rather than a looser alternative.** Marginalising the red-wing nuisance gives 0.24
MHz at 225 mW. The wing and the light shift are competing explanations of the same
red-side structure, so granting the wing freedom attributes that structure to the
wing and leaves less to support a light shift, which steepens the profile and
tightens the bound. Read it as what the light shift can be if the red-side excess
is instrumental, not as a bracket around the primary. Two things follow and they
pull in different directions, so both are stated. The gap between the two bounds
is not an additive systematic to be split, because the two are answers to
different questions rather than two estimates of one quantity. And the existence
of the alternative construction is itself model dependence, which stays in the
sensitivity record rather than being dismissed: the inference changes materially
with the treatment of the red-side structure, and the primary is quoted because
it is the construction that does not assume that structure away.

**`kappa_ub95_camponly` is not the campaign-alone BOUND, despite its name.** It
is the campaign's own chi-square read along the joint profile, whose nuisances
were fitted using all three sessions, which is what its own description in the
CSV says. It gives 0.15 MHz at 225 mW and an earlier version of this paragraph
quoted that as the campaign-only result. A genuine campaign-only refit was run
on 2026-08-17 and does not reproduce it: re-fitting the campaign with its own
nuisances gives a looser bound, so this row overstates what the campaign alone
constrains. The refit's value is not quoted here because its adjudication is
open. Treat this row as a decomposition of the joint profile and not as a
subset bound. The primary and campaign-only
subsets sit below the 0.35 MHz nominal prediction and the drop-4192 subset does
not, and `lopo_dchi2_pred` was read as showing no single peak driving the result. That reading is retired: positivity was never the test, the threshold is 2.706, and no count of arms is quotable because the arms are separate likelihoods. The committed note text was brought into line with the corrected producer by hand in this commit, since the producer needs five hours and an excluded tree. The numeric cells are untouched. They carry the older note text, because this file's producer needs five hours and an excluded tree. The
4 July evening-session axis-direction row is converged and indifferent, at a maximum
absolute Δχ² of 8.6.

**Two things to know before quoting it.** The producer needs the private
source trees, since raw traces never enter the repository, and without them
the committed CSV is the record. And the bound is loose by a measured
factor rather than by argument, because two effects broaden the line with the
ramp's own square-of-power signature and are absent from the model behind it.
Injecting the saturation term and re-profiling tightens it by 2.21
(`docs/notes/two_photon_saturation_companion.md`).
