# Confounding by acquisition order

*[wiki index](README.md) · method*

**The question.** Whether an apparent dependence on a control variable is a
dependence on when each point was taken.
**Takes.** A measurement swept over a parameter, and the order in which its
points were acquired.
**Gives.** Why a monotone sweep cannot separate the parameter from elapsed
time, how to find a control for it inside data already taken, and what
randomising the order costs.
**Skip if.** The question is whether two parameters of a model can be
separated by the data, which is [identifiability](identifiability.md). This
page is about a variable the experiment controls being entangled with one it
does not.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An experiment sets a parameter to several values and records an observable at
each. If the values are visited in monotone order, the parameter and the
elapsed time increase together, and the two columns of the design matrix are
collinear. Anything that drifts, and something always drifts, then produces
exactly the same signature as a real dependence on the parameter.

No estimator repairs this. The information is absent from the data, not merely
obscured in them, and a more careful fit to the same points recovers nothing.
Fitting a drift term alongside the parameter does not help either, because the
two regressors are the same regressor.

**The asymmetry worth remembering**: the confound is created for free by an
ordering nobody thought about, and removed for free by an ordering that takes
the same time to acquire.

## What problem it solves

Naming it converts an unanswerable question into a design decision. Once the
collinearity is written down, there are only three moves: randomise or
interleave the order, repeat the sweep in the reverse direction, or find an
existing dataset where the ordering differed.

## The natural experiment, and how to look for one

A confound present by design in one dataset is often absent by accident in
another. Sessions run for other reasons, rehearsals, pilots and commissioning
runs, are frequently acquired in whatever order was convenient, and that
convenience is a randomisation nobody paid for.

**What to look for, in order of value.** A session that ran the same sweep in
the opposite direction, best of all inside one sitting so that instrument,
alignment and epoch are held fixed while only the ordering changes. Failing
that, a session with a non-monotone order. Failing that, a session at a
different epoch, which is weaker because it changes everything at once.

The test is then simple. Fit the same quantity in each ordering. An effect
that is a function of the parameter is invariant under the ordering. An effect
that tracks the ordering is a function of history, and the word for that is
not automatically "drift": thermal and mechanical hysteresis, detector and
amplifier settling, baseline memory and alignment history all produce order
dependence, and separating them is a later question than establishing it.

## Where this repository uses it

The 2025 campaign ran its power ladder descending in time on all four lines,
so power and elapsed time are collinear across the whole session and every
quantity measured against power there is equally a measurement against drift.
Two findings rested on it, and on 2026-08-18 the archive's own control settled
them differently.

The 2025-07-04 rehearsal ran its ladders in alternating directions, one line
descending while two ascended, each ladder complete inside minutes on one
instrument at one gain with one alignment. That is the best case above, and it
was run that way for convenience rather than by design.

Against it, the amplitude's departure from the square-of-power law is
invariant: the descending line's exponent sits inside the range spanned by the
two ascending ones, which excludes the whole class of order-dependent causes.
The concave width against power is not: a trend appears on the descending
ladder and neither ascending ladder shows one, and the concavity is
consequently carried as provisional rather than established. Both adjudications,
and the numbers, are in
[the amplitude departure note](../notes/amplitude_departure_from_p2.md) and
[limitations and identifiability](../big_picture/07_limitations-and-identifiability.md).

## What can go wrong

**Reading order dependence as drift.** Order dependence is the observation.
Drift is one mechanism for it, and hysteresis, settling and history effects are
others with different remedies. The page above says which is which.

**Treating a null as proof of no drift.** An effect invariant under ordering
in one session with a handful of points is evidence against an
order-dependent cause, not a demonstration that nothing drifted.

**Confounding the confound.** If only one of several groups was acquired in
the reversed order, then direction is entangled with group identity, and a
difference between them cannot be attributed. When the reversed group agrees
with the others, that entanglement is harmless, which is a piece of luck to
notice rather than to rely on.

**Believing randomisation is free of cost.** It is free in acquisition time
and not in operational load: a randomised order forbids the settling shortcuts
a monotone ramp allows, and can demand a wait at every step that a monotone
sweep amortises.

## Try it

Two sweeps of the same underlying flat signal, one monotone in time and one
interleaved, both subject to the same linear drift. The monotone one reports a
dependence that is not there.

```python
import numpy as np

rng = np.random.default_rng(7)
P = np.array([25.0, 75.0, 125.0, 175.0, 225.0])   # the control parameter
drift_per_step = 0.05                              # a slow instrumental walk

for name, order in (("monotone descending", P[::-1]),
                    ("interleaved", P[[2, 0, 4, 1, 3]])):
    t = np.arange(len(order))                      # acquisition index
    signal = 10.0 + drift_per_step * t             # NO dependence on P at all
    fit = np.polyfit(order, signal, 1)[0]
    print(f"{name:22s}: fitted slope against P = {fit:+.5f} per unit")
print("the truth is 0.00000: the monotone sweep reports the drift as physics")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- G. E. P. Box, J. S. Hunter and W. G. Hunter, *Statistics for Experimenters*,
  2nd ed. (Wiley, 2005), chapters on randomisation and blocking, which is the
  general theory this page applies to one variable.
- R. A. Fisher, *The Design of Experiments* (Oliver and Boyd, 1935), for the
  original argument that randomisation is what licenses the inference rather
  than a precaution added to it.

## See also

- [Identifiability](identifiability.md), the model-side analogue: two
  parameters entangled inside the model rather than two variables entangled by
  the schedule.
- [Digitisation and dynamic range](digitisation-and-dynamic-range.md), the
  other acquisition choice that becomes a physics claim.
- [Designing an acquisition](designing-an-acquisition.md), where the ordering
  is chosen alongside span and record length.
- [Influence diagnostics](influence-diagnostics.md), for which points a
  confounded fit actually rests on.

---

[← Sensitivity analysis](sensitivity-analysis.md) · *Robustness and influence, 6 of 7* · [Reversal tests →](reversal-tests.md)
