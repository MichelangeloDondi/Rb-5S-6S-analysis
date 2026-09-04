# Bounds and the light shift

*[History](../HISTORY.md) · the headline bounds, the AC-Stark channel and the drifting lock*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The package exported a polarizability the record disagreed with, 2026-08-25

This record computed alpha(6S) - alpha(5S) = -1145 a.u. on 2026-07-17
([`results/polarizability.csv`](../../results/polarizability.csv), row
`delta_alpha_993`), finding the cited magnitude and the opposite sign.
`rb5s6s.constants.DELTA_ALPHA_AU` exported +1093 for five more weeks and
the shift predictor defaulted to it. Reconciled on 2026-08-25 by owner
decision on the theory, not by a measurement, with the published value
kept beside it as `DELTA_ALPHA_AU_ORSON2021`.

No committed bound moved, so nothing caught it: every bound reads
the magnitude. Three consumers written against +1093 broke when the
constant caught up, repaired 2026-08-26. Two further defects in the value were
found the same day, one now closed and one open.

| defect | was | now |
|---|---|---|
| evaluation wavelength | 993.0 nm, which made the value more negative | 993.4181 nm, the literature line; the repair moved it 0.70 a.u. less negative |
| 6S line-list truncation | open, its size unstated | still open, and sized at 4.2 to 21.7 a.u., which is 0.8 to 3.9 half-widths of the quoted band, so its top end puts the value outside that band entirely, because the tail standing in for the omitted states is calibrated at the static limit while the drive sits between 8P and 9P where the first omitted term is enhanced sevenfold |

An earlier wording called both "making it less negative", true of the
repairs and false of the defects. [RESULTS.md](../RESULTS.md) and the
`delta_alpha_993` note were given the open one on 2026-08-26, disclosed
here alone until then.

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

`run_polarisation_bound.py` hard-coded the differential scalar shift at 0.258 MHz, calling it "the committed differential scalar shift." That value is the 95 per cent upper bound, not a shift. The predicted shift, an ENVELOPE conditional on a waist never measured in the cell, is 0.348 MHz. The understated shift propagated into the published sublevel spread. The first correction repeated the fault one level down, pulling a rounded duplicate from a different file instead of the source CSV.

| stage | shift used | sublevel spread reported |
|---|---|---|
| original | 0.258 MHz, mislabeled bound | 4.5 kHz |
| first correction | 0.35 MHz, rounded, wrong file | 6.1 kHz |
| second correction | 0.348 MHz, from `stark_joint.csv` | 6.0 kHz |
| live | [0.364](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz, from `stark_sweep.csv` | 6.3 kHz |

The prediction now comes from `stark_sweep.csv` and the bound from `stark_joint.csv`, each cell naming the shift it used. `scripts/run_polarisation_bound.py` carries the reason they differ. The systematic had fallen 4.5 per cent short.

## The saturation companion factor, 2026-08-23

`run_saturation_probe.py` gained `--emit` and now writes `results/saturation_companion.csv`. The probe had been opt-in and kept nothing, so `docs/RESULTS.md` and the README quoted its factors with no row behind them. The file carries the width-only bound, both saturated bounds, and the factor at each saturation arm, [2.75](../../results/saturation_companion.csv "ref:saturation_companion:C3d:factor_with_saturation_ratio_-1p2362") (documents round it to 2.8). No committed bound changed. The joint factor of 2.21 stays unwritten as a digit: the row records `NEEDS_EXTERNAL_TREE`, dated to the run that produced it. Corrected 2026-08-26: this entry and `docs/RESULTS.md` had both carried a stale second-arm value predating the current arm set. Both were fixed the same day through the ledger's generator. The one ungoverned reader-facing value is now zero. Corrected again 2026-08-31: the freshness registry entry had never been runnable. The rows stay ungraded pending the investigation docs/RESULTS.md C3d records.

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

## The collisional-shift entry and Orson's own axis, 2026-08-27

The entry was checked the night it was written, and four of
its numbers did not survive. The sharpest sat inside a sentence the previous
round had just corrected: fixing *which* resolution Orson's null used broke
the *axis* that resolution belongs to. The entry now has a producer,
[`run_collisional_shift_bound.py`](../../scripts/run_collisional_shift_bound.py),
so its figures are rows rather than hand arithmetic.

| quantity | was | now |
|---|---|---|
| Orson's null against the Stark prediction | nine times, mixing a laser-axis 6 MHz against a transition-axis 0.65 | eighteen times, both on the transition axis, where their one-photon 6 MHz is 12 |
| this record's AC-Stark bound against Orson's null, on two pages | 23x (plan/01), twenty times (big_picture/04), both dividing shifts taken at different powers | about 13x, on the coefficient: their null is 12 MHz on the transition axis at 0.8 W, this bound is at 225 mW, and dividing the two shifts credits this record with the power ratio 3.56 |
| this record's self-broadening column against Orson's density null (LITERATURE) | three orders of magnitude coarser | about [24](../../results/collisional_shift_bound.csv "ref:collisional_shift_bound:comparison:orson_density_null_over_implied") times, and a scale comparison rather than a bound against a bound, since their null constrains a shift and this column a width. **The original was overstated by roughly forty-fold**, in the opposite direction from the two above. (This cell read "five to eight times" until 2026-08-27, which was an intermediate draft of the same correction and not its result; the 160x that stood beside it was computed against that draft.) |
| the collisional differential across 70-130 C | 0.036 MHz, with no density-scale systematic | 0.044 MHz, inflated by (1 + `N_SCALE_FRAC_SYST`) as `density.py` instructs every consumer to |
| that differential against the light-shift bound | seven times smaller | 5.9 times smaller |
| the Rahaman extrapolation across the same range | 24 kHz, which is arithmetically the 110-130 C span | 32 kHz, the rate re-anchored at each temperature |
| the two sources' relation | "an independent direction" | one route: both run through Zameroski 2014 |
| the ceiling beside the expectation | read as two routes corroborating | the expectation uses 0.87 of the ceiling raw against raw, so the ceiling is very nearly saturated |
| Rahaman's shift-to-width against classical theory | "roughly twice" it | agrees to ten per cent; the two was an FWHM-against-HWHM normalisation |
| `vanderwaals.py`'s shift machinery | "already carries" it | a width prefactor only; no shift prefactor exists in the package |
| Orson's 0.09 MHz at 140 C | explained by the vapour-pressure correlation spread | their own stated density contradicts their own stated pressure by 1.4 |
| Orson's section number | section 4, three times, plus a section 5 | section 3; the paper has four sections |

## The duel's injected shift labelled as the archive's, 2026-09-04

`docs/methods/06_the_statistics.md`, in its estimator-duel section, called
the duel's injected shift "the archive's own". The archive's predicted shift at
225 mW is the [0.364](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz of `results/stark_sweep.csv`,
and the duel's is a literal in `scripts/run_estimator_duel.py`, the retired
prediction rounded. The
sentence was corrected to name it as the duel's, near the archive's predicted
value.
Corrected on 2026-09-04. The cause: the retired prediction of
[0.348](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_pred:prediction") MHz,
which is this shift under Orson's polarizability and not under the value this
record adopts, carried rounded as a literal in the duel's producer and quoted
as the archive's own.
