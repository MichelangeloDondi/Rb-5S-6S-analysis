# Committed results

These CSVs are the outputs of the documented run of the pipeline (the numbers
quoted in the top-level README §5 and `docs/DATA.md`), committed so the claims
are verifiable without re-running. They regenerate exactly by running the
scripts in order (see the top-level README §8); `results/qc_metrics.csv` (the
~112 KB per-trace QC dump) is the one output kept out of git.

**Every row carries a machine-readable `status` column** (`scripts/annotate_results_status.py`,
run last in the pipeline) so the caveat travels *with the number* into any plot
or table — a bound never reads as a measurement. The controlled vocabulary:
**`BOUND`** (a limit, NOT a measurement — β_self, σ_laser, S₀; conditional on the
OPEN beam waist w₀, now re-centred to ~50 µm after the transit-MC flux bug was
fixed and propagated — see `docs/notes/transit_width_resolved.md`); **`NULL`**
(below detection / no model preference); **`MEASURED`** (a genuine result — the
frequency rate, the P² scaling, the γ-floor); **`PRELIM`** (a model-dependent
cross-check superseded by a BOUND headline); **`ARTIFACT`** (identified noise,
not physics); **`DIAGNOSTIC`** / **`CALIB`** (fit-quality / calibration
intermediates); **`ENVELOPE`** (order-of-magnitude / w₀-parametric estimate).
`laser_epoch.csv` and `qc_metrics.csv` carry their own `status`/`flag` instead.

| file | produced by | holds |
|---|---|---|
| `noise_model.csv` | `run_noise.py` (M1) | per-condition noise law a, b, τ_int |
| `ruler_blocks.csv`, `ruler_traces.csv`, `ruler_nlmap.csv` | `run_ruler.py` (M2) | sweep rate per block/trace; nonlinearity map |
| `ruler_campaign.csv` | `run_ruler.py` (M2) | the authoritative campaign rate (inverse-variance + PDG scatter inflation) — the ledger reads this rather than re-averaging the blocks |
| `linefit_conditions.csv` | `run_linefit.py` (M3) | per-condition joint-fit widths |
| `beta_self.csv`, `beta_self_probe.csv` | `run_beta_self.py` (M4, C1) | two DIFFERENT quantities (mind the names): `beta_self.csv` = per-peak model fits; **`beta_self_probe.csv` = the model-independent width-slope bound `bound95` — the C1 HEADLINE.** ("probe" here = the width-vs-density *probe*, NOT the 130 °C lever — that is `beta_lever_probe_130` in `lever_crosscheck.csv`.) **Axis note:** the `sigma_laser` column is the fitted Gaussian FWHM on the **transition axis** (halve for laser axis) and is CONDITIONAL on the transit prior (transit is a separate fixed kernel, degenerate with σ_laser via w₀). So per-peak 2.0–2.2 MHz transition = 1.0–1.1 MHz laser, consistent with the C2 headline bound (<1.2 MHz laser); it is NOT transit-subtracted and is an upper end, not a measurement. **β error columns here (and in `global_fit.csv`) are STAT-only** — the dominant C1 uncertainty is the ~factor-2 spread ACROSS estimators (this fit vs the hierarchical fit vs the model-independent bound), which is not a per-fit column; script against the bound in `beta_self_probe.csv` (`bound95`), not these central values, if you need the conservative headline. |
| `global_fit.csv` | `run_global_fit.py` (M4b) | **AUTHORITATIVE hierarchical β** (shared σ_laser per-T across peaks, β per isotope). This SUPERSEDES the per-peak `beta_self.csv` for the isotope question: the per-peak fits let σ_laser float per line and so absorb per-peak systematics — the 1.6σ ⁸⁷Rb internal spread (β 0.030 vs 0.047) and the unphysical 10% σ_laser spread (1.89–2.17; the laser cannot differ per hyperfine line) — whereas the global fit constrains σ_laser jointly and finds β₈₅=β₈₇ (no isotope difference). **σ_laser(T) caveat (updated by M4c, `sigma_laser_sharing.csv`):** the per-T sharing across peaks is now **validated** — at each T the four peak-blocks agree on one σ_laser (χ²/dof < 1), answering the acquisition-timing worry positively. But the 2.13/2.23/1.60 *trend* is NOT a physical laser drift: the free per-condition σ_laser is ~flat (1.6–1.8), so the tied fit's inflation-then-drop is the β↔σ_laser degeneracy under the density constraint. STAT-only errors; not clean per-temperature laser-width measurements. |
| `lever_crosscheck.csv` | `run_lever_crosscheck.py` (M4d) | **a lever-limited cross-check ESTIMATOR — NOT the headline β** (that stays the model-independent width-slope bound in `beta_self_probe.csv`). The cooling-sweep (70/90/110 °C) joint fit with its statistical precision and systematics: `beta_crosscheck` (value=β, err=statistical — **read as this estimator's precision, not β's**: the lever test below moves the central value ~8σ, so β is a bound, and `beta_lever_probe_130` + `gamma_rise_factor` show why), `beta_err_transit`/`beta_err_sharing`/`beta_err_modelform` (the model-form grid), `beta_w0_band` (value=lo err=hi over the OPEN w₀), `beta_loo_peak`/`beta_loo_temp` (drop-a-peak robustness vs drop-a-temperature lever-leverage), and `beta_grid_*` (the three model cells). **`beta_lever_probe_130` + `gamma_coll_mean_vs_T` + `gamma_rise_factor` are the lever test:** the joint β collapses 0.036→0.014 when the ×53 130 °C anchor is added, because γ_coll rises only ×1.85 across a ×52 density span (a residual floor, not resolved collisions) → β is a lever-dependent **BOUND**. The `beta_crosscheck` value SUPERSEDES `global_fit.csv` (same headline, byte-stable) by adding the auditable budget; the model-independent bound in `beta_self_probe.csv` remains the archival headline. |
| `sigma_laser_sharing.csv` | `run_sigma_laser_sharing.py` (M4c) | the σ_laser Model-A-vs-B test: per-T χ²/dof of the 4 peak-blocks (sharing validated, χ²<1) + free vs β·N-tied common σ_laser (the trend is degeneracy, not drift) |
| `laser_epoch.csv` | `run_laser_epoch.py` (M5, C2) | σ_laser upper bound + w₀ band |
| `power_sweep.csv` | `run_power_sweep.py` (M6, C3) | FWHM/amplitude/skew vs power. **`resid_skew` is the residual skew of a SYMMETRIC fit** — large & positive at low power (up to ~10σ) but it is shot-noise skewness (∝1/√counts, falls with power), NOT the ac-Stark ramp (which would grow as P³); see RESULTS.md C3c. |
| `stark_sweep.csv` | `run_stark_sweep.py` (M4e, C3d) | the AC-Stark coefficient BOUND from the power lever: one shared κ (S₀=κP) fit to the 130 °C FWHM-vs-power (from `power_sweep.csv`). **`S0_225mW_ub95_profile`** is the headline — a 95% profile-likelihood upper bound S₀(225 mW) < 0.63 MHz, just above `S0_225mW_pred` (0.59). (The Wald `S0_225mW_ub95`=3.1 / `_ub95_raw`=1.5 are SUPERSEDED diagnostics: the fit rails at κ=0, where a linearized error has no coverage.) A BOUND, not a measurement: the shift is dead in the 2025 drift, so only the ramp's width broadening (∝S₀²) constrains κ; `chi2_red`≈4 (block-to-block width scatter) is folded into the bound. a fixed lock would measure the pull ∝S₀ directly. |
| `amplitude_trapping.csv` | `run_amplitude_trapping.py` (M7) | amplitude vs density |
| `modelform.csv` | `run_modelform.py` (M8) | Voigt-vs-Lehmann BIC |
| `transit_mc.csv` | `run_transit_mc.py` (M9) | Monte-Carlo transit-broadening FWHM vs (w₀, T, collection geometry), with the crossing-flux factor (fixed 2026-07-13; validated against Lehmann's 41.2 kHz NNO example): the transit kernel adds ~2.1 MHz at w₀=32 µm in the thin single-waist limit, but only ~1.6 MHz over a realistic multi-mm collection column (the beam defocuses across it), so the line alone does not decisively exclude 32 µm — the ~50 µm prior rests on the direct waist measurement (w₀≈64 µm, Nieddu/Rajasree). At the 50 µm prior transit is ~1.2 MHz — degenerate with σ_laser through the OPEN w₀. Seeded on `C.RNG_SEED`, so byte-reproducible. |
| `amplitude_ratios.csv` | `run_amplitude_ratios.py` (M10) | degeneracy-law area ratios: measured vs predicted abundance×(2F+1), with `pull_sigma`. The measured ratios swing 30–50% between blocks (common-mode drift), so the law is **untestable in the archive** — a cross-peak systematic that interleaving in a fixed-lock session would fix; per-peak/within-block analyses are unaffected. |

All values are PRELIMINARY where they carry an absolute scale: they ride on
the OPEN beam waist w₀ (see the top-level README). The headline β_self is a
bound, not a measurement.
