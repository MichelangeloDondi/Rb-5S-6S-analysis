# Preregistration

*[wiki index](README.md) · method*

**The question.** What has to be written down and dated before a result
exists for a criterion to mean anything.
**Takes.** The idea of a statistical threshold and a detection claim. No
other wiki page is required first.
**Gives.** The criterion, census and analysis-chain framework, and the null
test and ceiling test that bracket what a frozen criterion is allowed to
claim.
**Skip if.** You want the test that validates the estimator a criterion is
built on, rather than the act of freezing the criterion itself. That is
[injection-recovery testing](injection-recovery.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Preregistration is a written commitment, made and dated before a result is
available, to the exact quantity a procedure will report, the exclusion rule
that decides which data points enter it, and the analysis that turns those
points into a number. The commitment covers three things: the criterion
itself (what counts as an effect, a detection, or a preferred model), the
census (which traces, conditions or trials are in scope, and on what stated
grounds one could be dropped), and the analysis chain (the estimator, the
weighting, the starting values, the stopping rule). Once written down, the
procedure runs against data that did not yet exist when the commitment was
made, or against data set aside and not yet read, and its output is either a
confirmation of the committed prediction or a stated failure of it.

The reasoning behind this is that an analysis chosen after the answer is
already visible is not one procedure applied but the best of however many
procedures were tried, whether or not every one of them was written down. A
dataset admits many defensible choices: which points count as outliers, which
functional form to fit, which threshold marks a detection, and each choice
moves the answer a little. Trying several and reporting the one that looks
cleanest turns an analysis into a search for a result that was there all
along, in the freedom to choose among defensible options rather than in the
data. Freezing the choices first removes that freedom at the one point where
it can be exercised, before the numbers are read.

A preregistration is not a promise never to look further. It is a commitment
about what the FIRST look counts as, so that later exploration is labelled as
exploration and does not borrow the standing of a confirmed result.

## What problem it solves

Preregistration solves the correlation between having many defensible
analysis choices available and getting to keep only the ones that flatter the
result. Without a frozen record, a criterion that happens to be satisfied by
the data at hand cannot be told apart from a criterion that would be satisfied
by almost any data, because the choice of criterion and the look at the data
are not ordered. A preregistered criterion is scored once, at a threshold and
against an exclusion rule fixed while the answer was still unknown, so the
outcome is a real test rather than a description of what was already found.

Two checks decide whether a criterion is worth freezing at all, and this
repository requires both of any procedure it preregisters for a simulated or
synthetic study.

A NULL TEST asks what the procedure reports when there is nothing to find:
run it many times on data built to contain no effect, at a stated threshold,
and record how often it claims one anyway. A trustworthy criterion's
false-positive rate matches its stated threshold. If the rate is
systematically higher, the criterion does not measure the effect, it invents
it, whatever the real data later show.

A CEILING TEST asks the opposite question, in a regime where the true answer
is already known independently, usually because the input was injected by
hand at a size no reasonable procedure could miss. If the procedure fails to
recover that known answer, the fault is in the setup rather than in the
physics: a threshold set wrong, an exclusion rule that removes the signal
along with the noise, a simulated noise law that does not match the one the
real data carry. Running a criterion on real data before it passes its own
ceiling test invites reading an experimental limitation as a physical absence.

Together the two tests bracket what a criterion is allowed to claim. One that
fails its null test is too loose: ordinary noise clears it, so a report of
detection carries no information. One that fails its ceiling test, or that
would need a signal far larger than the experiment's own error bars to clear
at all, is too tight: it can never be satisfied by data at the achievable
precision, so it decides nothing regardless of what is really there. A
criterion that a trivial estimator satisfies is not a criterion, and neither
is one so far beyond the experiment's own error bars that no real measurement
could ever cross it.

## Where this repository uses it

Every dated preregistration in this repository lives under
[`docs/notes/`](../notes/README.md), written and committed before the run it
scores, with the estimator, the census and the stop conditions fixed while the
outcome was still unknown.
[`docs/PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md) is where
each one is scored against what happened, including the runs that failed
their own gate outright rather than only the ones that went well, and a
correction to an earlier reading enters as a dated addendum placed after the
original text rather than as a silent edit. Where a number in the record has
since been replaced, [`docs/HISTORY.md`](../HISTORY.md) is the one place
licensed to carry the retired value alongside the current one, so that a
reader can see what changed and why without every other document having to
repeat the old figure to explain it.

Two dated notes name both tests described above explicitly.
[`docs/notes/model_selection_prereg.md`](../notes/model_selection_prereg.md)
predicts, before recomputing anything, which of several stated comparisons a
change of selection criterion can and cannot flip, and commits in advance to
reporting a null outcome as plainly as a flip. The two-speed sweep design in
[`docs/plan/09_the-fixed-lock.md`](../plan/09_the-fixed-lock.md) preregisters
a detection-lag simulation with a null test and a ceiling test named as such,
and the pedestal chain in
[`docs/big_picture/07_limitations-and-identifiability.md`](../big_picture/07_limitations-and-identifiability.md)
excludes a candidate mechanism for a residual excess by a ceiling test at many
times the mechanism's predicted size, leaving the excess unexplained rather
than assigning it to a cause the test rules out.

Preregistration in this repository never stands alone. A frozen criterion
still has to be validated the way [injection-recovery testing](injection-recovery.md)
validates any estimator, by recovering known truth under the analysis exactly
as it will run, and a model comparison scored against a preregistered
threshold is usually one member of the panel
[information criteria](information-criteria.md) describes, since a single
criterion at a single threshold is one vote and the panel is what shows
whether a conclusion is robust to the convention used to reach it.

## What can go wrong

The commonest failure is the one preregistration exists to stop from slipping
back in through a side door: an amendment made after seeing partial results
and folded into the original text rather than added as a dated, visible
correction. This repository's notes are append-only for exactly this reason,
a correction enters as a dated addition placed after the passage it corrects,
and the passage that made the original prediction is left exactly as written,
so that what was fixed in advance of the data can be told apart from what was
fixed afterward.

A second failure sits inside the null test itself, and is a data-insufficiency
problem wearing the clothes of a broken criterion. A false-positive rate
measured from a few dozen trials carries a binomial uncertainty of several
percentage points, so an observed rate that misses its nominal threshold by a
little may be sampling noise on the null test rather than evidence the
criterion is loose. The number of trials belongs beside the reported rate for
the same reason it belongs beside a coverage number in an injection-recovery
study.

A third is an implementation trap inside the null test's own machinery. If the
"no effect" data are generated with a residual signal left in by mistake, a
random-number generator shared with some part of the analysis it is meant to
test, or a normalisation that does not actually zero the quantity under test,
the check is not measuring what it claims to and can pass or fail for the
wrong reason. The ceiling test carries the same trap in reverse: a "known
regime" that is not as clean as assumed, contaminated by an effect the test
did not account for, produces a failure that gets charged to the procedure
when the fault is in what the regime was assumed to contain.

Fourth, a criterion can pass every check above and still be the wrong one to
have frozen, because the census it was written against does not match the
data that arrive. An exclusion rule fixed before a session can find that the
actual acquisition supplies fewer or different points than planned, and the
honest response is to state that plainly and score the criterion as attempted
rather than to relax it quietly until it fits what came back.

## Try it

A detection rule with a stated five per cent threshold, run on data
engineered to contain nothing. A trustworthy rule's false-positive rate should
land on that threshold regardless of how the "nothing" is drawn.

```python
import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(7)
n_points, n_trials, alpha = 200, 20000, 0.05
z_crit = norm.ppf(1 - alpha / 2)

noise = rng.standard_normal((n_trials, n_points))
z = noise.mean(axis=1) / (noise.std(axis=1, ddof=1) / np.sqrt(n_points))
claims = np.abs(z) > z_crit
rate = claims.mean()

print(f"threshold set for a nominal {alpha:.3f} false-positive rate")
print(f"{n_trials} trials of pure noise, no injected effect, {n_points} points each")
print(f"claimed a detection in {rate:.4f} of trials")
print(f"expected under the null: {alpha:.4f}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## The band-holdout threshold that never entered the frozen script

On 2026-08-15 a band-holdout replication was reported inside the private
record as a clean sweep of the held-out conditions at a decisive p-value,
built from "the calibration-sound subset of a sixteen-condition cohort". Two
of those conditions were the pilot's own traces regrouped by peak, and the numeric soundness threshold that carved out
the "calibration-sound subset" was never written into the frozen script, so
the census that actually ran was not the census that had been committed. The
result was replaced the same day by 11 of 14 fresh conditions, p = 0.029. A
preregistered census, stated with its exclusion grounds before the run the way
this page describes, would have fixed the soundness threshold and the
pilot/fresh boundary in advance, leaving no room for a subset drawn after the
traces were already visible.

The same 2026-08-15 record closes on a stronger finding than any single row.
Of six numbers corrected that day, five moved in the direction that had made
the result look stronger, "which is a measurement of the review rather than
six coincidences", and the protocol changed so that the direction of a
refutation tally is recorded beside its count, not the count alone. That is a
preregistration lesson in its own right: a null test scores whether a
criterion's failure rate matches its stated threshold, and a review whose
corrections run five-to-one toward the flattering answer is failing the same
kind of test on itself. Recording the direction as well as the count is what
lets a review catch that bias the way a preregistered null test catches a
loose criterion, and it is the check this page's own null-test description
would have called for first. See
[HISTORY.md](../HISTORY.md) for both rows.

## Further reading

- B. A. Nosek et al., "The preregistration revolution", *PNAS* **115**,
  2600 (2018), the canonical statement of the practice this page applies.
- [Wikipedia: Preregistration (science)](https://en.wikipedia.org/wiki/Preregistration_(science)),
  for the general history and the distinction between a preregistration and a
  registered report.
- [Injection-recovery testing](injection-recovery.md), the technique that
  validates the estimator a preregistered criterion is built on.
- [Information criteria](information-criteria.md), the panel a preregistered
  model-selection threshold is usually one member of.
- [`docs/notes/`](../notes/README.md) for this repository's own
  preregistrations, and
  [`docs/PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md) for how
  each one was scored.

## See also

- [Injection-recovery testing](injection-recovery.md), the estimator
  validation a preregistered criterion still needs after it is frozen.
- [Information criteria](information-criteria.md), the panel a
  preregistered model-selection threshold is usually one vote within.
- [Monte Carlo methods](monte-carlo-methods.md), the simulation technique
  behind a null test's false-positive rate and a ceiling test's known
  regime.

---

[← Injection-recovery testing](injection-recovery.md) · *Statistical inference, 8 of 8* · [wiki index →](README.md)
