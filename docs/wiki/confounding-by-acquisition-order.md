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

An experiment sets a parameter to several values and records an observable
at each. Visited in monotone order, the parameter and elapsed time increase
together, so the two columns of the design matrix become collinear, and
anything that drifts produces the same signature as a real dependence on the
parameter.

No estimator repairs this: the information is absent, not merely obscured,
and a more careful fit to the same points recovers nothing. A drift term
fitted alongside the parameter does not help either, since the two
regressors are the same one. Avoiding the confound costs no more time than
creating it.

## What problem it solves

Naming it converts an unanswerable question into a design decision. Once
written down, there are three moves: randomise or interleave the order,
repeat the sweep in reverse, or find an existing dataset where the ordering
differed.

## The natural experiment

Sessions run for other reasons, rehearsals, pilots and commissioning runs,
are often acquired in whatever order was convenient, supplying the
randomisation a designed sweep skipped.

**In order of value.** Best is a session that ran the same sweep in the
opposite direction inside one sitting, so instrument, alignment and epoch
stay fixed. Next best is a non-monotone order, and weakest is a different
epoch, which changes everything at once.

Fit the same quantity in each ordering. An effect that is a function of the
parameter is invariant under it. One that tracks the ordering is a function
of history, not necessarily drift: thermal and mechanical hysteresis,
detector and amplifier settling, baseline memory and alignment history all
produce order dependence, and separating them comes later.

## Where this repository uses it

The 2025 campaign ran its power ladder descending in time on all four
lines, so power and elapsed time are collinear, and every quantity measured
against power is equally a measurement against drift. Two
of its findings, the amplitude's power-law exponent and the width's
concavity against power, were checked against a control dataset on
2026-08-18.

![Power ladder FWHM and peak signal plot](../../figures/fig2_power_sweep.png)

*The 2025 campaign's own power ladder: FWHM and peak signal against drive
power, acquired in monotonically descending order.*

The 2025-07-04 rehearsal ran its ladders in alternating directions, one line
descending while two ascended, each complete in minutes on one instrument,
gain and alignment. It is the best case above, run for convenience, not by
design.

Against it, the amplitude's exponent is invariant, sitting inside the range
spanned by the two ascending ladders and excluding order-dependent causes.
The width's concavity is not: it appears only on the descending ladder, so
it stays provisional. Numbers for both are in
[the amplitude departure note](../notes/amplitude_departure_from_p2.md) and
[limitations and identifiability](../big_picture/07_limitations-and-identifiability.md).

## What can go wrong

**Reading order dependence as drift.** Order dependence is the observation.
Drift is one of several mechanisms, alongside hysteresis, settling and other
history effects, each with its own remedy.

![Laser line centre drift plot](../../figures/fig15_drift_story.png)

*The laser line centre drifting across the 2025 campaign, the mechanism a
monotone sweep cannot tell apart from a real dependence on the swept
parameter.*

**Treating a null as proof of no drift.** An effect invariant under ordering
in one small session is evidence against an order-dependent cause, not proof
nothing drifted.

**Group and direction entangled.** If only one group ran in the reversed
order, direction is entangled with group identity, and a difference between
groups is unattributable. Here the reversed group agrees with the others, so
it did no harm.

**Randomising has an operational cost.** It costs nothing in acquisition
time, but forbids the settling shortcuts a monotone ramp allows, demanding a
wait at every step instead.

## Try it

Two sweeps of the same flat signal, monotone and interleaved, under the
same linear drift: the monotone one reports a dependence that is not there.

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

Every snippet here runs in `tests/test_wiki_snippets_run.py`, so one that
stops working fails the suite instead of quietly misleading a reader.

## Further reading

<!-- term-of-art: the book title is quoted verbatim -->
- G. E. P. Box, J. S. Hunter and W. G. Hunter, *Statistics for Experimenters*,
  2nd ed. (Wiley, 2005), on randomisation and blocking, this page's general
  theory.
- R. A. Fisher, *The Design of Experiments* (Oliver and Boyd, 1935):
  randomisation licenses the inference, not a precaution added afterward.

## See also

- [Identifiability](identifiability.md), the model-side analogue: parameters
  entangled inside the model instead of variables entangled by the schedule.
- [Digitisation and dynamic range](digitisation-and-dynamic-range.md), the
  other acquisition choice that becomes a physics claim.
- [Designing an acquisition](designing-an-acquisition.md), where ordering is
  chosen alongside span and record length.
- [Influence diagnostics](influence-diagnostics.md), for which points a
  confounded fit rests on.

---

[← Sensitivity analysis](sensitivity-analysis.md) · *Robustness and influence, 6 of 7* · [Reversal tests →](reversal-tests.md)
