# The campaign-only Stark profile, as run

Recorded 2026-08-17. **DIAGNOSTIC. Nothing in `results/` moved, no committed
bound changed, and no number in this note is quotable as a bound of the
record.** The quoted light-shift construction remains the pooled three-session
fit in `results/stark_joint.csv`, and the adjudication between constructions is
open, argued in
[when a joint fit is legitimate](../big_picture/08_when-a-joint-fit-is-legitimate.md)
and recorded as a decision in
[RESEARCH_DECISIONS section 13](../RESEARCH_DECISIONS.md).

This note exists because that chapter states how a campaign-only refit behaved,
and an outside review observed that the chapter's claim outran the public
evidence: the refit's profile lived only in a private working area, so a reader
could not see the thing the sentences described. The construction and its
profile are recorded here so that the public claim and the public evidence
match. The raw traces stay private, as they do for every fit in this
repository, so this note documents the construction rather than making the fit
re-runnable from the mirror.

## The construction

A copy of `scripts/run_stark_joint.py` changed in one line, `traces = camp`, so
the 100 canonical campaign traces enter the residual and the 46 evening-session
and 26 campaign-morning traces do not. The parameter vector is built exactly as
in the pooled fit, so the dropped sessions' nuisances remain in the vector,
contribute no residual, and sit at their seeds. That is harmless to the bound
because the threshold construction uses the unscaled one-sided 2.706, so no
reduced chi-square bookkeeping enters. The output is redirected and an assertion
forbids the copy from ever writing the pooled record.

**The environment caveat carried by every refit in this repository applies.**
This fit ran on a newer numpy than the environment of record, so its numbers are
diagnostic rather than record-grade until reproduced there.

## What it returned

Three profile passes, ascending, descending and seeded, agree on the 95%
crossing to three decimals, 1.024, 1.025 and 1.026 MHz per W, and repeating the
scan in the opposite axis direction changes nothing at the stated precision. The
minimum sits at 0.25 MHz per W with a preference over zero of 0.00 in
chi-square, so there is no detection, only a bound-shaped profile.

The profile, each variant against its own minimum:

| kappa, MHz per W | primary, Delta chi2 | wing variant, Delta chi2 |
|---|---|---|
| 0.00 | 0.00 | 0.00 |
| 0.25 | 0.00 | 4.81 |
| 0.50 | 0.46 | 6.09 |
| 0.75 | 1.32 | 9.20 |
| 1.00 | 2.53 | 12.89 |
| 1.50 | 6.13 | 18.44 |
| 2.00 | 11.15 | 24.15 |
| 2.62 | 19.67 | 32.71 |
| 3.50 | 36.54 | 49.57 |
| 5.00 | 80.80 | 93.83 |

The primary column crosses 2.706 at 1.024 MHz per W.

## The wing column, and how not to read it

The wing variant grants the fit a shared two-parameter red-side nuisance, an
alternative explanation of the same red-side structure the light shift is read
from. Its raw chi-square is at or below the primary's at every grid point, as
profiling over more parameters requires, so the difference between the columns
is convergent arithmetic and not an optimiser artefact. With the wing free the
structure is attributed to the wing, the profile steepens sharply, and the
crossing collapses to a small fraction of the primary's.

**No bound is quoted from the wing column.** It answers a conditional question,
what the light shift could be if the red-side excess is instrumental, and a
construction that assumes away the effect it bounds cannot supply the record's
number for that effect. The table is shown because it demonstrates the
mechanism by which added nuisance freedom can TIGHTEN a profile interval, which
is the point [the chapter](../big_picture/08_when-a-joint-fit-is-legitimate.md)
makes in prose, and because the same comparison measures how sensitive this
construction's reported limit is to the treatment of the red-side structure.

## The pooled construction's own re-run, beside it

The same day's diagnostic re-run of the POOLED construction is the comparison
the chapter interprets, so its per-pass answers belong here too. Ascending
2.106, descending 1.007, seeded 1.231 MHz per W, against the committed
production value of 1.147 from the earlier pointwise-minimum construction. The
chi-square gap between the ascending and descending passes varies by up to 56
along the profile, which is why they land answers a factor of two apart.

Every profile in this note is machine-readable in
[campaign_only_stark_profile.csv](campaign_only_stark_profile.csv), one row per
grid point, each variant's chi-square given relative to its own minimum.

## The multi-start reproducibility test, run 2026-08-17, and what it did not settle

The convergence-checks table below used to say that no construction had been
given a profile-reproducibility test. One has now been attempted on the POOLED
construction, and the result refines the question rather than answering it.

**The design, frozen before the run.** Six coefficient values spanning the
bound region, five starts each. Start zero is the production initial vector and
the other four are jittered componentwise by five per cent, each jitter drawn
once per START and applied at every coefficient value, so each start yields one
coherent profile curve and therefore one bound. Every optimisation is
independent, with no warm start from a neighbouring point, which is the single
difference from the production construction and the point of the test.

**Half the starts never converged.** Fifteen of the thirty optimisations hit
the production evaluation cap of 1500 without meeting a convergence criterion,
and **only one of the five starts produced a curve with no capped point**. Among
the points that did converge, the across-start spread in chi-square runs from
about 37 at the lower coefficient values to about 21000 at the upper ones,
against the 2.706 that sets the interval.

**What that establishes.** The pooled likelihood surface is expensive to reach
from an independent start at the production budget, and the production
construction's warm-start chain, which carries each solution to the next
coefficient value, is doing essential work rather than merely saving time.
Taken at face value the spread meets the preregistered threshold for the
surface carrying more than one local optimum, **but with half the points
unconverged the test cannot separate a genuinely different optimum from a
search that stopped early**, and that separation was the purpose. What the run supports is narrower: the benign
explanation is excluded and the two remaining ones are not yet distinguished.

**What it does not establish, and this matters.** It says nothing about whether
the committed profile is wrong. Cold independent starts are worse optimisations
than a warm chain by construction, so a cold start failing to reproduce a warm
chain's profile is expected in some measure. What was not expected is the size.
No committed number moves on this, and none should.

**The budgeted re-run separated the explanations, and the answer is both.**
The identical test at four times the evaluation cap, changed in nothing else,
halved the capped points from fifteen to seven, so part of the first run's
spread was an unfinished search. What remains is not: two starts produced
complete curves with no capped point and their bounds are 1.000 and 2.133 MHz
per W, a factor of 2.13 between fully converged independent starts, and one
start CONVERGED at three coefficient values to a stationary point about
21,000 in chi-square above the best, which is a second local optimum and not a
search that ran out. **The pooled likelihood surface carries more than one
local optimum, and the production construction's warm-start chain is
load-bearing rather than merely efficient.** One start still exhausted even
the quadrupled budget at one point after thirty-one minutes, so the surface is
also genuinely expensive. The record's position is unchanged and now rests on
a completed test rather than an inconclusive one: the pooled and campaign-only
bounds cannot be compared at the size of their difference.

The thirty per-point curves are in
[the CSV](campaign_only_stark_profile.csv) under construction
`pooled_multistart`, each variant tagged `_CAPPED` where that point hit the
evaluation limit, so a reader can apply their own convergence filter.

## Which convergence checks each construction has had

| construction | checks run | outcome |
|---|---|---|
| pooled, committed 2026-08-03 | cold and seeded chains, both directions, pointwise minimum | direction variants differ by at most 8.59 pointwise |
| pooled, diagnostic re-run 2026-08-17 | three passes, ascending, descending, seeded | bounds span a factor of 2.1 |
| campaign-only, 2026-08-17 | three passes plus the reversed scan axis | agreement at the third decimal, direction indifference 0.00 |
| campaign-only wing variant | cold descending and seeded ascending | chi-square at or below the primary's at every grid point, as nesting requires |
| pooled, multi-start at the production budget | five independent starts, no warm start | half the optimisations capped, one complete curve: a second optimum and an unfinished search not separated |
| pooled, multi-start at four times the budget | identical starts, only the cap changed | **RESOLVED, both causes real**: caps halved, two complete curves disagree by a factor 2.13, and one start converged to a stationary point 21,000 above the best. More than one local optimum, and the warm-start chain is load-bearing |
| pooled, multi-start under the PINNED dependency floor | identical design, numpy 2.5.0 and scipy 1.16.0, the CI minimum leg | **REPRODUCES**: converged starts again split by about 21,300 in chi-square at three of six kappa points, per-start bounds run 0.59 to 2.19 with one degenerate curve, and the pointwise-min bound of 1.92 again sits far above the production warm-start chain's 1.147. The surface's structure is a property of the fit, not of the environment |

## What this does and does not establish

It establishes that a campaign-only construction converges, with pass agreement
at the third decimal against the pooled construction's factor-of-two pass
spread, and that its reported limit is far more sensitive to the wing model than
the pooled construction's, since the pooled pair moves by about seven per cent
under the same perturbation.

It does not establish which construction should carry the record, it does not
measure whether the three sessions shared a beam waist, and it does not make the
campaign-only number a bound of the record. Those are the open items of the
chapter, and the second is answerable only by apparatus knowledge or a
per-session waist measurement.
