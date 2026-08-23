# Preregistration: the coverage of the AC-Stark power-lever 95% bound (M14)

Status: pre-registered 2026-08-17, written from the frozen script while the run
was already executing and **before any summary row existed**. The construction
below is frozen in `scripts/run_stark_coverage.py`, which carries the seed, the
ladder and the two arms as module constants, and the two are committed together.

`provenance: PREREG` - Written from the frozen script while the run was already executing and before any summary row existed, by its own header. Its numbers are thresholds and cell definitions fixed in advance, and 17 of its 19 values appear in committed CSVs. **2 numeric claims on this page remain unaccounted for.** Declared 2026-08-23 after checking every three-significant-figure value on the page against `results/`, not by labelling.


## What this answers, and what it can break

`rb5s6s/stark.py` retires the Wald bound in its own docstring: the fit rails at
$\kappa = 0$, where the width handle broadens as $S_0^2$ and therefore has zero
gradient, so the linearised error "is a finite-difference artifact and carries
no 95% coverage". `docs/HISTORY.md` records the consequence, the AC-Stark row
moving from 3.1 MHz on 2026-07-16, and marks the change "interval construction,
not new data".

The replacement is a profile $\chi^2$ bound at the over-dispersion-scaled
threshold $2.706 \times \max(\chi^2_{\rm red}, 1)$. **Whether the replacement
covers 95 per cent has never been measured.** `results/coverage.csv` is the
same study for the collisional bound (M13) and its `quantity` column carries no
Stark row.

The gap is not cosmetic. At a parameter boundary the likelihood-ratio statistic
is not $\chi^2_1$: the classical result is an equal mixture of $\chi^2_0$ and
$\chi^2_1$, under which a one-sided 2.706 threshold is CONSERVATIVE rather than
exact. Conservative would mean the published bound is looser than the data
require, which matters directly, because the record already carries a separate
factor 2.21 of looseness from the deliberately omitted saturation companion.
Anti-conservative is also possible once over-dispersion scaling and a nuisance
re-minimisation sit on top of the mixture, and only simulation separates them.

**What this run can falsify.** If coverage of the profile bound comes out below
0.95 at any $\kappa_{\rm true}$ on the ladder, the quoted 95% is not 95% and the
word falls at three sites (the `rb5s6s/stark.py` docstring, the
`run_stark_sweep` banner, and the `docs/RESULTS.md` C3d row). If it comes out
far above 0.95, the bound is conservative by a measurable factor and that factor
is quotable as headroom rather than left as an unknown.

## The construction, frozen

| item | value |
|---|---|
| estimator under test | `rb5s6s.stark.fit_stark_sweep`, the shipped one, unmodified |
| data | the committed 20-cell grid, `results/power_sweep.csv`, 4 peaks by 5 powers |
| truth model | the estimator's OWN `_fwhm_of`, `companion_gamma_mhz` and `companion_transit_mhz`, at the per-peak `sigma_laser` the real fit returns |
| $T$ | 130 °C, as in production |
| seed | 20260817, one independent `SeedSequence` stream per (arm, $\kappa$, trial) |
| trials | 650 per cell (see the amendment below) |
| ladder, $\kappa_{\rm true}$ (MHz/W) | 0.00, 0.25, 0.50, 0.78, 1.15, 1.56, 2.00, 2.81, 4.00, 5.50, 7.00, 9.00 |
| arms | `nominal` ($\sigma$ = quoted `fwhm_err`) and `overdispersed` ($\sigma$ = $\sqrt{3.7047}$ times quoted) |

The ladder is chosen to span the boundary the construction exists for
($\kappa = 0$), both quoted bounds (1.15 is the joint C3f bound, 2.81 the
width-only C3d bound, since $S_0 = \kappa \times 0.225$ W), the ramp prediction
at 1.56, and then to run well PAST the typical bound, because coverage is
trivially 1 wherever the ladder sits below the bound and the informative region
is where it breaks.

**Why two arms.** The `nominal` arm drives $\chi^2_{\rm red}$ to 1, which
switches the $\max(\chi^2_{\rm red}, 1)$ scaling off and isolates the 2.706
threshold itself. The `overdispersed` arm reproduces the scatter the real grid
shows and is therefore the production path. **The `overdispersed` number is the
one that may be quoted.** The `nominal` arm is a mechanism check and is not a
statement about this experiment.

## The primary endpoint, named in advance

**Coverage of `kappa_ub95_profile` in the `overdispersed` arm**, defined as
$P(\hat\kappa_{\rm ub95} \ge \kappa_{\rm true})$, at each ladder point. Target
0.95. Monte-Carlo standard error at 650 trials and coverage 0.95 is 0.0086, so
the run resolves a departure of about 2.6 percentage points at three sigma,
which is ample for the question asked, since a boundary-mixture effect would
move coverage by several points and not by one.

Secondary, all pre-named so that none can be promoted after the fact:

1. the same coverage for the **Wald** bound, which measures the docstring's
   claim instead of repeating it.
2. bias, $\overline{\hat\kappa} - \kappa_{\rm true}$.
3. rail rate, $P(\hat\kappa = 0)$, the boundary the construction exists for.
4. mean and **median** bound, since a bound on a near-unidentified parameter is
   heavy-tailed and the mean alone would mislead.
5. the **percentile of the published bound** (2.8111 MHz/W) inside the
   simulated distribution at $\kappa_{\rm true} = 0$. This asks whether the
   archive's own realisation is typical or lucky, which no single fit can
   answer, and it was added to the frozen script before the run.

## What this study deliberately does NOT do

It does not test model misspecification. Truth and estimator share the same
forward model by construction, so a coverage number from this run is a statement
about the INTERVAL and nothing else. Mixing the two would produce a number that
cannot be attributed to either, and the misspecification arm is a separate
study.

It does not touch the joint three-session C3f bound, which reads two excluded
trees and is a different estimator.

## Standing of the output

**DIAGNOSTIC.** One row per trial to `private/run_logs/`, nothing into
`results/`, no committed number moved, following the precedent
`scripts/run_s0_block_bootstrap.py` set. A postscript to this note adjudicates
what, if anything, is promoted, and the adjudication is the owner's.

## Environment, stated because it is load bearing

The run is on the project `.venv`, which carries a newer numpy than the one the
committed digits were produced under. That is acceptable HERE and would not be
for a committed value: this study reports a probability estimated from fresh
simulation rather than a re-derivation of an archived number, and its own base
fit is printed at the top of the log so any drift against the committed
`kappa_ub95_profile` of 2.8111 is visible rather than silent.

## Amendment, 2026-08-17, before any result existed

**Trials per cell reduced from 1750 to 650.** The first run was launched at 1750
and its own progress line measured the true cost at 7.1 core-seconds per fit,
against the 3.0 seconds a single fit on the real grid takes. Simulated data cost
more because the estimator rails less often and the profile scan has further to
expand. At that rate the full design was 83 core-hours against a budget of 40.

**This is a compute-budget amendment and not a result-driven one.** The run
writes its output only on completion, so when it was stopped no summary row, no
coverage number and no trial record existed anywhere. Nothing was seen and then
optimised away.

**The reduction is exactly reproducible rather than merely smaller.** Each trial
draws from its own `SeedSequence([SEED, arm_index, round(kappa*1000), trial])`,
so trials 0 to 649 of the abandoned 1750-trial design are bit-identical to the
whole of the 650-trial design. The smaller run is a prefix of the larger one,
and extending it later to 1750 would reuse these 650 unchanged rather than
invalidate them.

The ladder was NOT trimmed, because its twelve points were chosen for physics
(the boundary, both quoted bounds, the ramp prediction, and the region past the
bound where coverage can break) while the trial count is only precision.
