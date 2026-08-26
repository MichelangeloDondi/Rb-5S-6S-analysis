# Bounds and the light shift

*[History](../HISTORY.md) · the headline bounds, the AC-Stark channel and the drifting lock*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The 2026-08-17 corrections

Four joint-fit quantities, a sweep-linearity claim, and a session-date label were corrected on 2026-08-17.

| quantity | was | now | cause |
|---|---|---|---|
| saturation-companion factor, joint light-shift bound | 2.21, inferred from the width-only channel | measured value, see RESULTS.md | the joint refit ran |
| `kappa_ub95_camponly` | read as a campaign-alone bound | keeps its 0.674 MHz/W value, reclassified as a pooled-profile subset column | a genuine campaign-alone refit disagreed |
| light-shift-bound subset spread across constructions | factor of 2.4 | withdrawn. Committed rows support a leave-one-peak-out factor of 1.42 | the campaign-rows column is not a campaign-alone bound |
| excess outside the fit window | no candidate mechanism | candidate is the lineshape model, the limitation itself stands | a joint fit over 79 traces with per-trace polynomials, plus an amplitude regression |
| sweep-rate linearity claim | unquantified, stated as never departing beyond the bound in any well-sampled window | linear to 0.25 per cent in the interior, not linear at the leading edge (−1.75 per cent ± 0.40, +0.73 per cent ± 0.18, 4.4σ and 4.0σ from flat), see `results/ruler_nlmap.csv` | checked against the CSV |
| campaign-morning session date | 2025-07-18, in the joint-fit docstring | 2025-07-17 | GLOSSARY.md and DATA.md name 17 July as canonical |

## The 2026-08-19 corrections

Several unrelated values were corrected on this date, tabulated below with the file that now holds each live number.

| quantity | was | now | cause |
|---|---|---|---|
| light-shift bound, multi-start pointwise minimum | about 1.92 MHz per W, read as a threat to the pooled likelihood surface | retired. Anchored to the committed minimum of 186370.92, the independent starts sit 4.66 to 26.29 above the 2.706 threshold and never enter the confidence region. Corrected in `docs/notes/campaign_only_stark_profile.md` | the curves were stored own-normalised, so a minimum taken across them matches no single fit |
| two-photon saturation companion factor | 2.35, circulating in working notes as measured | no such number exists. The committed factors are 2.8 (width-only) and 2.21 (joint), predicted before the run, in `docs/notes/two_photon_saturation_companion.md` | conflated with the FWHM-to-sigma constant 2.3548 or a Student-t value in plan chapter 5 |
| `results/linefit_conditions.csv` | stale against four commits that changed the producer's numerics | regenerated. Ten columns move across all 32 rows, `sigma_laser` by up to 21 percent. `sigma_laser_sharing.csv` and `resolving_power.csv`, which read it, are regenerated with it | a selectable transit kernel and an isotope correction to the transit width |
| `results/wing_check.csv` | stale | regenerated. Every digit is unchanged, including the 130 C asymmetry of -0.0007 +/- 0.0013, and the worst case improves from 0.68 to 0.67 sigma | the producer is deterministic |
| `results/projections.csv` | 55 cells reading the word "archive" | regenerated to "record." One numeric cell moves in its eighth significant figure | a vocabulary rename swept the file |
| cascade branching and natural-width constants in `rb5s6s/stark.py` | literal copies, diverged from their source | imported from the source. The natural width is unchanged, three of four branchings are unchanged, and one gains precision, 0.372478 to 0.372478177 | literals do not update when their source does |

## The vector light shift's sublevel spread, 2026-08-20

`run_polarisation_bound.py` hard-coded the differential scalar shift at 0.258 MHz, calling it "the committed differential scalar shift." That value is the 95 per cent upper bound, not a shift. The calibrated prediction is 0.348 MHz. The understated shift propagated into the published sublevel spread. The first correction repeated the fault one level down, pulling a rounded duplicate from a different file instead of the source CSV.

| stage | shift used | sublevel spread reported |
|---|---|---|
| original | 0.258 MHz, mislabeled bound | 4.5 kHz |
| first correction | 0.35 MHz, rounded, wrong file | 6.1 kHz |
| live | 0.348 MHz, from `stark_joint.csv` | 6.0 kHz |

Both values now come from `stark_joint.csv` at run time, each cell naming the shift it used, tied to the two documents by a registry entry.

## The saturation companion factor, 2026-08-23

`run_saturation_probe.py` gained `--emit` and now writes `results/saturation_companion.csv`. The probe had been opt-in and kept nothing, so `docs/RESULTS.md` and the README quoted its factors with no row behind them. The file carries the width-only bound, both saturated bounds, and the factor at each saturation arm, [2.75](../../results/saturation_companion.csv "ref:saturation_companion:C3d:factor_with_saturation_ratio_-1p2362") (documents round it to 2.8). No committed bound changed. The joint factor of 2.21 stays unwritten as a digit: the row records `NEEDS_EXTERNAL_TREE`, dated to the run that produced it. Corrected 2026-08-26: this entry and `docs/RESULTS.md` had both carried a stale second-arm value predating the current arm set. Both were fixed the same day through the ledger's generator. The one ungoverned reader-facing value is now zero.

## The drift-freedom factor of 48, retracted 2026-08-25

The data-collection chapter said letting each display epoch of the 2025
campaign carry a freely fitted drift inflates the centre channel's error on
the light-shift amplitude by a factor of 48 over its noise limit, computed
once and quoted without a producer. Once built, the producer did not
reproduce it: the 48 divided a measured quantity by a fixed-lock baseline
that is not a measurement of this dataset, since every centre here is
already referenced to the mean of its own display epoch. It instead
publishes [14.4](../../results/centre_fisher.csv
"ref:centre_fisher:inflation_linear_over_drift_known:forecast") as the
fixed-lock forecast and [7.3](../../results/centre_fisher.csv
"ref:centre_fisher:inflation_linear_over_constant:measured") as the cost
measured with both terms on the same traces (`run_centre_fisher.py`). The
design recommendation survives: re-ordering the powers is forecast to take
the error from [3.48](../../results/centre_fisher.csv
"ref:centre_fisher:sigma_amplitude:linear_per_epoch") to
[0.48](../../results/centre_fisher.csv
"ref:centre_fisher:sigma_amplitude_forecast:linear_drift_cycled"). Corrected
on the v4.3 release pages of both repositories.
