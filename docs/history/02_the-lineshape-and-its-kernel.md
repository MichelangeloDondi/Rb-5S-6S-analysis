# The lineshape and its kernel

*[History](../HISTORY.md) · the kernel family, the widths and what the fits resolve*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The 2026-08-18 corrections

| quantity | was | now | file | cause |
|---|---|---|---|---|
| width-pinning factor, both widths free vs. laser width known | 0.0396 vs 0.0235 MHz (factor 1.7), unreproducible | 0.0073 vs 0.0021 MHz (factor 3.4), on a bright synthetic condition | `scripts/run_width_pinning.py` | no committed producer existed for the retired pair |
| hierarchical β_self sensitivity, quoted in plan/05 and plan/06 | 0.036 to 0.014 | 0.0534 to 0.0198 (85Rb), 0.0219 (87Rb) | not named in the old entry | the plan chapters quoted the retired cross-check estimator, unqualified |

Both figures were requoted at their current values on 2026-08-18. The retired β_self pair, 0.036 to 0.014, is carried in this file's bound-history table above.

## The amplitude power law was described rather than tested, 2026-08-18

| quantity | was | now |
|---|---|---|
| two-photon amplitude vs power, log-log slope, 4 hyperfine lines | described as ≈ power², slopes 1.83 to 2.12, untested against 2 | tested by block bootstrap. Three of four lines exclude 2 (one below, two above). The fourth is consistent with 2 only once the between-block error term replaces the within-cell one |

No committed number or bound moves, since no published result rests on the amplitude's exponent. The claim now states that the amplitude follows the two-photon rate law approximately, not exactly, with per-peak departures of both signs. Construction in `docs/notes/amplitude_departure_from_p2.md`.

## The width-power concavity, 2026-08-18

A concave curvature of the linewidth against power, apex near 120 mW, had stood since 2026-08-17 as a measured diagnostic at 4.8 standard deviations under within-cell errors. Tested under the between-block treatment this record's width channel otherwise uses, the significance falls to 1.4, the pilot's independent ladder does not confirm it at 1.2, and the rehearsal shows it only on the descending ladder. The curvature is withdrawn to provisional. No committed number changes, since no published bound rested on it. Section C3a's reading, that the width's power variation is block scatter, stands.

## An exact degeneracy that the code broke, and the number that had no referent, 2026-08-20

The per-condition figure for how much the collisional width shifts when the laser kernel changes from Gaussian to Lorentzian, reported at a median 45 percent, is withdrawn with no replacement. A Lorentzian laser width and the collisional width enter the model only through their sum, so the split carries no information at any single condition. A finite-grid convolution had let the fitted profile depend on that split by up to 3.7e-3 of peak, where the mathematics forbids any dependence. The fix adds the Lorentzian laser width directly into the homogeneous width, pinned by `tests/test_laser_kind_degeneracy.py`. No committed number outside `laser_kernel.csv` moved.

| Quantity | Was | Now |
|---|---|---|
| Headline `beta_self` kernel-sensitivity range | 45-67%, no producer | 45-67%: 45.0, 58.0, 63.2, 66.6% across the four peaks, 9-18 sigma statistical error (`run_kernel_headline.py`) |
| Sign-test p-value, Gaussian vs Lorentzian (32 of 32) | quoted as a significance | tally unchanged, kept only as implementation evidence, not a significance |

## Three pages described the kernel systematic as unquantified or still to be done, 2026-08-22

[Chapter 7](../big_picture/07_limitations-and-identifiability.md) called the laser-kernel systematic unquantified. [BIG_PICTURE.md](../BIG_PICTURE.md) and [PLAN.md](../PLAN.md) each listed a fitted Lorentzian-equivalent width as remaining work. It had already been fitted. Freeing that width at each peak gives a component present everywhere, a nested likelihood ratio of 176 to 961, at 0.315 to 0.449 MHz per peak, 3.24 times the statistical error on a matched footing. All three pages now state that value. No published number changed. The narrative pages had not been updated after the fit was run. Two qualifications travel with the value. Whether the four peaks share one width is neither rejected nor established at p = 0.097, and attributing the component to the laser is a separate, unlicensed claim.

## The class-adequacy caveat, tested twice in one day, 2026-08-22

Three surfaces said the blind residual atlas had not been run and that class adequacy was untested. It has run twice. The first attempt detected a residual shape at the floor but voided itself. Its check used a threshold twenty times stricter than the repository's own 2e-2 standard (`verify_results_fresh.py`), tripped by a 1.7e-2 drift on one condition. A second run, preregistered against that 2e-2 standard plus a leave-one-out over all 32 conditions, detected the same shape at the floor and passed every leave-one-out. `results/kernel_k4.csv` carries it. Now, residual structure exists inside the fit window, not model inadequacy, mechanism unnamed, `R_kernel` unchanged. Its relation to the band excess outside the window was answered 2026-08-23, in [that entry](03_the-band-excess.md#the-in-window-structure-and-the-band-excess-share-a-predictor-2026-08-23).

## A published sentence called a sensitivity an uncertainty, 2026-08-22

The kernel-representation sensitivity, 3.24 times the statistical error, was called "the kernel uncertainty" in `docs/wiki/self-broadening.md` and `docs/wiki/laser-frequency-noise-and-the-linewidth.md`. Both pages now read "the sensitivity to the kernel representation, within the family tested, is 3.24 times the statistical error," stating plainly that this is a sensitivity and not an uncertainty on the coefficient. The value and its producer, `results/kernel_budget.csv`, are unchanged. The wrong noun implied the tested family spans every possible kernel. One instance escaped the phrase-bank guard when "kernel" and "uncertainty" split across a line break. `tests/test_repo_hygiene.py` now matches prose with line breaks removed.

## A results file said a finished instrument was deferred, 2026-08-23

`results/kernel_budget.csv`, row `R_kernel_scope`, stated in its note column that the blind residual atlas testing class adequacy "is deferred." By the time this was read, that atlas had been built, run, and re-run to a qualifying detection, including once across the environment migration, returning fourteen detection rows unchanged. The row now says class adequacy was tested, that no mechanism is assigned to the residual structure it found, and that its effect on the collisional coefficient is not quantified. No number moved. The false claim survived four prior sweeps because it lived in a CSV note column, a prose location no prose check reads. The propagation sweep now covers `results/` as well as `docs/`.

## Two producers disagreed about R_kernel in the fourth decimal, 2026-08-23

`results/kernel_k5.csv`'s `R_kernel` moved from 3.2403 to 3.2398, now identical to `results/kernel_k3.csv`. No published claim changes, since every quotation of this value rounds to 3.24.

`scripts/run_kernel_k3.py` computes the ratio from full-precision floats. `scripts/run_kernel_k5.py` read `kernel_k3.csv` back off disk as text and divided its rounded six-decimal display strings, 0.004530 and 0.001398, giving 3.2403 instead. `scripts/run_kernel_k5.py` now reuses `scripts/run_kernel_k3.py`'s own `R_kernel` value instead of re-deriving it from displayed intermediates.

## The twin's four-decimal correlations, retired 2026-08-24

Retired when a producer for them was built, but still quoted verbatim on
eight surfaces (BIG_PICTURE, PLAN, the tutorial, four chapter pages, and
the identifiability wiki's factor table). Every surface now quotes
`results/twin_span_sweep.csv`, and the retired digits survive only in the
twin page's retirement record and in this file. The identifiability
table's middle row moves from the unregenerable tutorial point to the
sweep's committed design condition, -0.9421 with a pin factor of 2.98.

Chapter 6 also gains an uncertainty ledger for the next campaign: one row
per component of the three headline uncertainties, with its size, limiting
factor, acting knob, expected purchase, and validating check, scoped to
the cell campaign alone.
