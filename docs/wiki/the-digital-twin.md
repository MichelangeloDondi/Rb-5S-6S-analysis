# The digital twin of an experiment

*[wiki index](README.md) · method*

**The question.** How do you find out what an apparatus would measure before
the apparatus exists?
**Takes.** A forward model of the measurement and a fitter that consumes it.
[Monte Carlo methods](monte-carlo-methods.md) supplies the sampling, and
[injection-recovery testing](injection-recovery.md) is the closure test this
builds on.
**Gives.** The achievable uncertainty on each parameter at a proposed design,
which pairs stay degenerate no matter how the design is changed, and the
false-alarm behaviour of the design when there is nothing to find.
**Skip if.** You want to know whether an ANALYSIS is correct, which is
[injection recovery](injection-recovery.md). This page is about whether an
EXPERIMENT is worth building.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A digital twin is the forward model of a measurement, run in the direction
that generates data rather than the direction that fits it, and then fitted
back with the same machinery the real data would meet.

The loop has five steps and the fifth is the point of it.

1. State the truth: the line, the widths, the shift coefficient, the
   populations, whatever the physics of the measurement contains.
2. State the design: power, temperature, span, points across the line,
   repeats, vertical range, sweep order, and the noise the detector actually
   produces.
3. Generate the traces that apparatus would record under that truth.
4. Fit them back with the production fitter, unchanged.
5. Read the achievable uncertainties, the parameter correlations and the
   detection significance, then CHANGE THE DESIGN AND REPEAT.

Steps 1 to 4 are an injection-recovery test. Step 5 is what makes it a twin:
the object under study stops being the analysis and becomes the experiment.

## What problem it solves

Designing a measurement means choosing among options that all sound
reasonable. More power, a wider span, more repeats, a hotter cell, a tighter
focus. Each is defended with an argument about scaling, and arguments about
scaling are cheap and frequently wrong, because the quantity that matters is
not the signal-to-noise of a trace but the uncertainty on a PARAMETER after a
fit that has several other parameters in it.

A twin replaces the argument with a measurement. Doubling the points is worth
whatever the twin says it is worth at this design, and the answer arrives in
minutes rather than in a session.

It also makes a projection falsifiable in the way this repository's
[preregistration](preregistration.md) discipline requires. A sentence of the
form "this change improves the coefficient by a factor of two" is either
backed by a simulation that produced the two, or it is an expectation wearing
a number.

## The arithmetic that decides whether a twin is even needed

The single most useful thing a twin reports is not an uncertainty. It is a
CORRELATION, because a correlation says whether more data can help at all.

When two parameters are correlated at $\rho$ in the fit, measuring one of them
independently and holding it fixed reduces the other's variance to
$(1-\rho^2)$ of its joint value, so its uncertainty falls by
$\sqrt{1-\rho^2}$. That factor depends on $\rho$ alone. It does not care how
many traces were taken.

The consequence is sharp. If $\rho$ is small, an external constraint buys
almost nothing and more data is the right purchase. If $\rho$ is close to one,
more data is nearly worthless for separating the pair and an external
constraint is worth a large factor. A design study that reports only
uncertainties will always show improvement, because more data always shrinks
an error bar, and will never reveal that the pair stays degenerate.

`rb5s6s.forecast.external_constraint_gain` is that factor, and the
identifiability page carries what it is worth on this experiment's own
degenerate pair.

## What it cannot establish

**A twin never validates the physics it was given.** It generates data from a
model and fits them with the same model, so agreement means the code is
internally consistent and means nothing whatever about whether the model
describes nature. A twin that reproduces its own truth has demonstrated
exactly that.

This is not a weakness to be apologised for, it is the boundary of the
instrument. Everything a twin says is conditional on the forward model, and
the forward model is validated against real data elsewhere, by
[injection recovery](injection-recovery.md) on the analysis side and by
residual structure and [information criteria](information-criteria.md) on the
physics side.

Three further limits, each of which has produced a wrong conclusion somewhere:

**A twin cannot see a systematic nobody modelled.** The 2025 campaign's
vertical-range switching was invisible to any simulation that did not contain
a quantiser, and it changed a published analysis.

**A twin's noise is as good as its noise law.** Independent Gaussian noise at
a constant fraction of the peak is the tutorial default and is optimistic.
Real detectors give signal-dependent, partly correlated noise, and a forecast
made under the optimistic law is a lower bound on the uncertainty rather than
an estimate of it. See [the noise law](the-noise-law.md) and
[correlated samples and effective sample size](correlated-samples-and-effective-sample-size.md).

**A twin reports what its fitter can do, not what is possible.** A different
estimator might extract more. The forecast is a statement about the pipeline
that will actually analyse the data, which is the useful statement, but it is
not an information-theoretic bound.

**A twin cannot add information, only expose it.** Asked whether an
apparatus can serve some new purpose, a magnetometer say, the twin computes
the response of every channel to the new quantity and reports sensitivities,
which is design work. What it cannot do is make a dataset sensitive to
something its channels never coupled to: a simulation of the data adds no
information to the data, and a twin that appears to extract a quantity the
response matrix says is absent is measuring its own priors.

## Where this repository uses it

`rb5s6s/forecast.py` is the layer: `synthetic_traces` generates data under
either a constant noise fraction or a measured noise law, and
`forecast_precision` runs the Monte Carlo over `synthetic_traces` into
`fit_condition`, returning median parameter uncertainties together with
scalings measured by RE-RUNNING the study at scaled designs rather than by
asserting exponents.

`examples/campaign_twin.py` is the worked case: the twin of the next
measurement campaign, carrying the hyperfine amplitudes with cascade
depletion, the saturation companions, the AC-Stark ramp, the blackbody shift,
the measured noise law, and the acquisition design of
[PLAN chapter 7](../plan/07_acquisition-settings.md), including its
single-vertical-range quantisation and a session drift.

`docs/TUTORIAL.md` walks the loop for a line of the reader's own choosing, and
every code block in it runs as `examples/tutorial_forecast.py`.

## What can go wrong

**Running only the injected world.** A twin that injects an effect and then
detects it has shown that the design responds to a signal. It has NOT shown
that the design stays quiet when there is no signal. Run a null world beside
every injected one and report both, because a design that false-alarms is
worse than a design that misses.

**Letting the twin read the committed results.** A twin that loads the
repository's own output files and then agrees with them has proved nothing at
all. Embed the constants it needs, tag each with where it came from, and let
the agreement be a real comparison between two paths to the same number.

**Layers that cannot be switched off.** If the cascade depletion, the
saturation companions and the Stark ramp are welded together, nobody can find
out what each contributes, and a wrong layer hides inside a right total. Every
physical effect a twin carries should be independently disableable, and the
twin should print what each one moved.

**A twin that cannot contradict its author.** The failure mode that matters
most. If every layer is written to confirm the claim being tested, the twin is
an expensive restatement. Each layer should be phrased as a claim with a
source, and the twin should print a verdict per claim, including the ones that
fail.

## Try it

```bash
python examples/tutorial_forecast.py
```

The script defines a line, generates traces from it, fits them back, degrades
the design until the fit fails honestly, and forecasts a design that has not
been built, printing a verdict at each stage. Then:

```bash
python examples/campaign_twin.py
```

which runs the same method on a real planned campaign, with an injected truth
and with a null.

## Two claims this twin refuted, 2026-08-19

The twin was written to demonstrate the record and immediately contradicted
it twice, which is the only reason it is worth the page.

**A table was wrong in the library.** `rb5s6s/cascade.py` shipped with a
mapping of which isotope and which ground hyperfine level each of the four
lines drives, and three of the four assignments were wrong. Fifty-three tests
passed over it, because the test asserted the module's table back against
itself. The twin read the repository's independent line table for a different
purpose entirely, and the two disagreed on contact.

**A teaching claim was wrong in a draft.** An unreleased draft of the tutorial
taught that widening the scan span breaks the width degeneracy. The twin
measured the correlation at $-0.9177$ across a 60 MHz span and $-0.9166$
across 300 MHz, and at ten times the traces it reached only $-0.881$. Both
uncertainties fell and the correlation did not move, because the degeneracy
belongs to the lineshape rather than to the sample size. The claim was
replaced by the arithmetic above before the page shipped.

Both are recorded in [HISTORY.md](../HISTORY.md).

## Further reading

Digital twins as a term come from engineering, where a simulation of a
physical asset is kept synchronised with the asset itself. The usage here is
the design-stage half of that idea, which in the statistics literature is
closer to DESIGN OF EXPERIMENTS and to simulation-based power analysis. The
underlying arithmetic, that conditioning on a correlated parameter reduces
variance by $(1-\rho^2)$, is the standard partitioned-inverse result for a
multivariate normal and appears in any regression text under partial
correlation.

## See also

[Injection-recovery testing](injection-recovery.md), the closure test this
extends · [Identifiability](identifiability.md), which is the quantity a twin
is most useful for reporting · [Monte Carlo methods](monte-carlo-methods.md),
the sampling underneath · [Designing an acquisition](designing-an-acquisition.md),
the settings a twin evaluates · [Sensitivity analysis](sensitivity-analysis.md),
for which input a projection depends on · [The noise law](the-noise-law.md),
without which a forecast is optimistic

---

[← Monte Carlo methods](monte-carlo-methods.md) · *Simulation and computation, 2 of 5* · [Grids and discretisation →](grids-and-discretisation.md)
