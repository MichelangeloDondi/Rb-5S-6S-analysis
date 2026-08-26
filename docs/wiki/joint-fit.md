# The joint fit

*[wiki index](README.md) · method*

**The question.** Whether repeated measurements of the same quantity should
be fitted together with the physics shared, or fitted separately and
averaged.
**Takes.** A per-point weight for each measurement, already in hand. That is
the subject of [weighted least squares](weighted-least-squares.md).
**Gives.** The shared-versus-per-trace structure, the physical claim each
sharing level makes, and the over-sharing failure that looks like success.
**Skip if.** The question is whether an extra parameter is justified by the
data, not how repeats of one condition are combined. That is
[information criteria](information-criteria.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

When an experiment records the same quantity several times, the repeats can
be fitted one at a time and averaged, or fitted together with the physics
shared and the nuisances free. The second is a joint fit, and the two are
not the same operation.

![four drifted repeats, and the widths recovered two ways](figures/wiki_joint_fit_toy.png)

*Four synthetic repeats with independent centres, fitted separately
(scattered widths) and jointly with one shared width (recovers the truth).*

The structure is the useful part. A shared parameter is one the repeats
genuinely have in common, typically the physics: a linewidth, a
cross-section, a shift coefficient. A per-trace parameter is one that
legitimately differs between repeats, such as an amplitude that follows
detector gain, a centre that follows drift, or a baseline that follows the
background at the time. All are fitted at once, minimising a single
objective over the whole dataset.

The gain is that every repeat contributes to the shared parameter with its
full weight, while the things that drifted are absorbed where they belong.
Averaging independent fits cannot do this, because each independent fit has
already paid for its own nuisances with its own degrees of freedom, and
information about the shared quantity is lost before the averaging starts.

Deciding which level to share at is where the physics enters: a modelling
choice, not a technical one. Sharing across repeats taken minutes apart is
usually safe. Sharing across conditions recorded hours apart asserts that
the quantity did not change in between, and that assertion is the substance
of the fit.

## What problem it solves

It makes drifting data usable. If an instrument wanders between repeats but
the physics does not, a joint fit puts the wander in the per-trace
parameters and keeps the physics in the shared ones.

## Where this repository uses it

Everywhere the widths are extracted.
[Methods chapter 6 section 4.2](../methods/06_the_statistics.md) sets out the
hierarchy and [`rb5s6s/linefit.py`](../../rb5s6s/linefit.py) implements it.
Each condition has several back-to-back repeats of the same line, and the
2025 laser drifted while the detector gain wandered, so the repeats are
fitted jointly with the line-shape parameters shared and the amplitude,
centre and a tilted baseline free per trace.

![five repeats of one condition fitted with a shared line shape](../../figures/fig21_joint_fit_five.png)

*Five back-to-back repeats of one campaign condition (993.4192 nm, 130 C,
225 mW) under a single shared line shape, with per-repeat centre, amplitude
and residuals shown separately.*

The sharing continues upward, and the chapter is explicit that each level is
a physical claim. The laser width is shared per temperature across the four
hyperfine lines, because those four are measured within one dwell and see
the same laser at that moment, which lets its drift across a session be
measured instead of mistaken for collisions. The self-broadening coefficient
is shared per isotope, not globally, so the two isotopes can be tested
against each other instead of assumed equal. The transit width is shared
globally, since it follows the beam and the temperature law.

## What can go wrong

Over-sharing is the characteristic failure of joint fitting. A large shared
fit returns a small formal error, and if the shared quantity varied between
the blocks it was shared across, that variation is absorbed by whichever
parameter can imitate it: a confident number that reflects instrument
drift, not physics. Sharing the laser width across blocks recorded hours
apart, in a session where the laser was drifting, is exactly this failure.

A second form of over-sharing is a shared parameter that depends on
something the groups differ in and no nuisance represents. Over-sharing a
drifting laser width is caught eventually because the width has an
independently known scale. This is not, because nothing in the fit is out
of range. Suppose the shared quantity scales as one over the square of a
beam radius, and the groups were recorded at different, unlogged focus
settings. Each group then has its own true value of the shared parameter,
the fit returns an average of them, the formal error is small, and no
per-trace audit or goodness-of-fit reports anything, because every group is
fitted well by its own free offset and gain.

The test is mechanical, not statistical. Write down what the shared
parameter depends on, list the ways the groups differ, and look for a
dependency that appears in the first list, differs between groups, and has
no nuisance opposite it in the model. [Pooling across
groups](pooling-across-groups.md) works this through with a runnable
demonstration where adding a group with three times the leverage makes the
answer worse.

The next failure is a correlated-data one. A joint fit assumes the repeats
contribute independent information, and repeats that share a systematic do
not. The effective number of independent samples is then smaller than the
number of points, which matters both for the error bars and for any
[information criterion](information-criteria.md) computed from the same fit.

Third, an implementation trap: adding traces grows the parameter vector, and
a fit with many per-trace nuisances can converge to a local optimum where
one trace's parameters land somewhere unphysical while the shared value
compensates. A per-trace residual audit catches this and a global
goodness-of-fit does not, because a joint fit must be good for every trace,
not merely on average.

Finally, sharing does not remove a degeneracy that the whole dataset
carries. If every repeat has the same degenerate pair, sharing improves the
precision of the degenerate combination and leaves the split as poorly
determined as before, which is the subject of
[identifiability](identifiability.md).

## Try it

Four drifted repeats of one line, fitted separately and then jointly with a
single shared width. The joint estimate is not the average of the others.

```python
import numpy as np
from scipy.optimize import least_squares

rng = np.random.default_rng(7)
x = np.linspace(-8, 8, 400)
w_true, offs = 2.0, [-1.2, -0.4, 0.5, 1.1]
traces = [1 / (1 + ((x - o) / w_true) ** 2)
          + 0.15 * rng.standard_normal(x.size) for o in offs]
lor = lambda a, c, w: a / (1 + ((x - c) / w) ** 2)

alone = [abs(least_squares(lambda p, y=y: lor(p[0], p[1], abs(p[2])) - y,
                           [1, 0, 1.5]).x[2]) for y in traces]
joint = abs(least_squares(
    lambda p: np.concatenate([lor(p[1 + 2 * i], p[2 + 2 * i], abs(p[0])) - y
                              for i, y in enumerate(traces)]),
    [1.5] + [1.0, 0.0] * len(traces)).x[0])
print("fitted alone: " + ", ".join(f"{v:.3f}" for v in alone))
print(f"fitted jointly: {joint:.3f}   truth: {w_true}")
```

## Further reading

- A. Gelman and J. Hill, *Data Analysis Using Regression and
  Multilevel/Hierarchical Models* (Cambridge, 2006), for the shared-versus-free
  structure in its general form.
- [Methods chapter 6](../methods/06_the_statistics.md) for this repository's
  hierarchy and the leave-one-out checks on it.
- [Identifiability](identifiability.md) for what joint fitting cannot fix.

## See also

- [Weighted least squares](weighted-least-squares.md), for the per-point
  weights a joint fit shares across every trace.
- [Identifiability](identifiability.md), for the degeneracy that sharing a
  parameter improves the precision of without ever resolving.
- [Information criteria](information-criteria.md), for how the effective
  sample size of correlated repeats affects a criterion built from the same
  fit.

---

[← Weighted least squares](weighted-least-squares.md) · *Statistical inference, 2 of 8* · [Pooling across groups →](pooling-across-groups.md)
