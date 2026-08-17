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

## Which convergence checks each construction has had

| construction | checks run | outcome |
|---|---|---|
| pooled, committed 2026-08-03 | cold and seeded chains, both directions, pointwise minimum | direction variants differ by at most 8.59 pointwise |
| pooled, diagnostic re-run 2026-08-17 | three passes, ascending, descending, seeded | bounds span a factor of 2.1 |
| campaign-only, 2026-08-17 | three passes plus the reversed scan axis | agreement at the third decimal, direction indifference 0.00 |
| campaign-only wing variant | cold descending and seeded ascending | chi-square at or below the primary's at every grid point, as nesting requires |
| any construction | profile-reproducibility, independent starts agreeing on the Delta chi-square CURVE | **not yet run for any of them, and required before the pooled and campaign-only bounds can be compared** |

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
