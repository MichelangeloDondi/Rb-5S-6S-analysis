# Injection-recovery testing

*[wiki index](README.md) · method*

**The question.** Can an analysis recover a truth it was handed in advance,
and what does passing that test actually prove.
**Takes.** A complete analysis pipeline, already built and ready to run
start to finish. No other wiki page is required first.
**Gives.** The bias, coverage and pull diagnostics a recovery test produces,
and the boundary between what a closure test validates and what it cannot.
**Skip if.** You want the general Monte Carlo machinery a recovery test is
built from, rather than the closure test itself. That is
[Monte Carlo methods](monte-carlo-methods.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An injection-recovery test asks whether an analysis can find an answer it
already knows. Choose true parameter values $\theta_\text{true}$, generate
synthetic data from them with realistic noise, run the ENTIRE analysis
unchanged, and compare the estimate $\hat\theta$ with the truth. Repeat many
times.

Three things come out of it, and only the first is usually remembered. The
BIAS is the mean of $\hat\theta - \theta_\text{true}$, and it says whether
the estimator systematically misses. The COVERAGE is the fraction of trials
whose quoted interval contains the truth, which should equal the nominal
confidence level and frequently does not. And the PULL distribution, the
error-normalised residual $(\hat\theta - \theta_\text{true})/\sigma$, should
be standard normal. If it is too wide the uncertainties are understated, and
if it is too narrow they are inflated.

The discipline that makes it meaningful is that the recovery must run the
analysis as it is actually run, including the window choices, the weighting,
the starting values and any automated cuts. An injection test on a simplified
version of the pipeline validates the simplification.

## What problem it solves

It replaces trust with a measurement. Every analysis rests on assumptions
about its own machinery being unbiased and its error bars being honest, and
those assumptions are checkable at the cost of computer time. It is also the
only practical way to calibrate a bound, because a bound's whole value is its
coverage.

## What it cannot establish

This deserves its own heading because it is where the method is most often
oversold. Generating synthetic data FROM the model and recovering the
injected truth validates the IMPLEMENTATION: the estimator is unbiased, the
optimiser converges, the intervals cover, the degeneracies behave, all of it
UNDER the simulated model. It cannot validate the model. Whether the physical
lineshape is the right one, whether a mechanism is missing, whether the real
noise resembles the simulated law, none of these is tested by a closure test,
because the same assumption generated the data and analysed it.

Those questions need different evidence: a nested model comparison that lets
the data reject a component, a measured rather than assumed noise law, and
residual audits that look for structure no fitted component absorbs.

## Where this repository uses it

No fitter is allowed near real data here until it recovers known injected
truths from campaign-like synthetics, which is the rule stated in
[methods chapter 6 section 4.6](../methods/06_the_statistics.md), and the
coverage study for the headline bound is section 4.11 of the same chapter.
Several bugs in this repository's own history were caught exactly this way.

The technique also reaches the public surface. The package's worked example,
[`examples/synthetic_recovery.py`](../../examples/synthetic_recovery.py),
is an injection-recovery test on data it generates itself: it states its
assumptions before fitting, builds traces from the public line-shape builder,
fits them with the same function the committed results used, and reports each
parameter's pull against the fit's own error rather than asserting that the
fit looks reasonable. It runs from a bare clone with no measured data
present, which is the point.

Injection is used adversarially too, not only as a closure check. Contaminants
of a known shape can be injected into real traces to ask what a mechanism the
model does NOT contain would do to the fitted parameters, which is a way of
bounding a systematic rather than validating an estimator.

## What can go wrong

The dominant failure is the one under its own heading above: reporting a
closure test as evidence that the physics is right. A green injection test on
a wrong model is exactly as green as one on a right model.

A data-insufficiency failure hides inside the coverage number. Coverage
estimated from a few dozen trials has a binomial uncertainty of several per
cent, so "95 per cent coverage" from 40 trials is consistent with a good deal
less, and the number of trials belongs beside the result.

Two implementation traps. If the synthetic noise is drawn from the same
generator seed as some part of the analysis, or if the injected traces reuse
the fitted values from the real data as truth, the test is partly circular
and will pass more easily than it should. And a synthetic that omits a
feature the real data have, an uneven sweep, a baseline slope, an occasional
bad trace, tests a pipeline that never meets those, which is how a validated
estimator can still fail on arrival.

## Try it

Twelve injections of a known width, recovered through the same builder the
fits use. The scatter is the number that matters, not any single recovery.

```python
import numpy as np
from scipy.optimize import least_squares
from rb5s6s import composite_profile, transit_fwhm_from_w0

t = transit_fwhm_from_w0(64e-6, 130.0)
grid, p = composite_profile(0.60, 1.40, t)
nu = np.linspace(-15, 15, 1200)
shape = np.interp(nu, grid, p / p.max(), left=0, right=0)

errors = []
for seed in range(12):
    data = shape + 0.01 * np.random.default_rng(seed).standard_normal(nu.size)
    def r(q):
        g, pp = composite_profile(abs(q[1]), abs(q[2]), t)
        return q[0] * np.interp(nu, g, pp / pp.max(), left=0, right=0) - data
    errors.append(abs(least_squares(r, [1.0, 0.60, 1.40]).x[1]) - 0.60)
print(f"{len(errors)} injections, truth 0.600 MHz")
print(f"  mean recovery error {np.mean(errors):+.4f} MHz")
print(f"  scatter             {np.std(errors):.4f} MHz")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## A held-out cohort that was not held out

On 2026-08-15 a band-holdout replication was reported inside the private
record as a clean sweep of the held-out conditions, at a p-value that would
have been decisive, drawn from "the calibration-sound subset of a
sixteen-condition cohort". Two of those conditions were not fresh at all. They were the pilot's own traces,
regrouped by peak, counted a second time as if they were independent
evidence. The numeric threshold that had carved out the "calibration-sound
subset" was never written into the frozen script, so nothing on the page
that produced the 7 of 7 tally recorded which conditions the pilot had
already touched. Replaced the same day by a count built from 11 of 14 fresh
conditions, the tally weakened to p = 0.029. [HISTORY.md](../HISTORY.md)
carries both numbers.

This is the same trap this page names above under "Two implementation
traps", stated there for a synthetic injection reusing the real data's own
fitted values as truth and here for a real-data holdout reusing the pilot's
own traces as a fresh condition: a check that is not independent of the
material used to build the thing it is checking passes more easily than it
should, for a reason that has nothing to do with whether the underlying
result is sound. An injection-recovery discipline that insists the recovery
run on data no part of the analysis has already seen, the same discipline
this page states for synthetic truths, applied equally to which real
conditions were allowed into the confirmatory cohort would have flagged the
two pilot-derived entries before the 7 of 7 count was ever reported.

## Further reading

- S. R. Cook, A. Gelman and D. B. Rubin, "Validation of software for
  Bayesian model-fitting using posterior quantiles", *J. Comput. Graph.
  Stat.* **15**, 675 (2006), the standard reference for checking an
  inference pipeline by injecting known truths.
- [Methods chapter 6](../methods/06_the_statistics.md), sections 4.6 and 4.11,
  for this repository's own closure and coverage studies.
- [`examples/synthetic_recovery.py`](../../examples/synthetic_recovery.py),
  which is a runnable version of everything on this page.
- [Identifiability](identifiability.md) for the case where recovery fails not
  because the code is wrong but because the parameter was never determined.

## See also

- [Monte Carlo methods](monte-carlo-methods.md), the general simulation
  technique a recovery test applies to an estimator's bias and coverage.
- [Preregistration](preregistration.md), which freezes the criterion a
  recovery test is later asked to validate.
- [Identifiability](identifiability.md), for the case where recovery fails
  because a parameter was never determined rather than because the code is
  wrong.

---

[← The profile likelihood](profile-likelihood.md) · *Statistical inference, 7 of 8* · [Preregistration →](preregistration.md)
