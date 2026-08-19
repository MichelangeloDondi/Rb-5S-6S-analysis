# Influence diagnostics

*[wiki index](README.md) · method*

**The question.** Which observations is a fitted answer actually resting on,
and how does that differ from which observations merely look surprising.
**Takes.** A least-squares fit already run, weighted or not, and no further
assumption about the shape of the noise law.
**Gives.** The leverage and case-deletion machinery, Cook's distance and
DFBETA among them, that separates an outlying point from an influential one.
**Skip if.** You want the weighting a fit itself should carry rather than
what to check after fitting. That is
[weighted least squares](weighted-least-squares.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A least-squares fit turns a vector of measurements $d$ into a vector of
fitted values $\hat d = X\hat\theta$, and that map is linear in $d$ itself:
$\hat d = Hd$, with the HAT MATRIX

$$H = X\left(X^\top X\right)^{-1}X^\top$$

built entirely from the design matrix $X$, which points were measured and at
which settings, and never from the measured values in $d$. For a weighted
fit, the kind [weighted least squares](weighted-least-squares.md) describes
and the kind this repository always runs, the same object generalizes to
$H = X\left(X^\top WX\right)^{-1}X^\top W$ with $W$ the diagonal weight
matrix, and everything below carries over unchanged.

The diagonal entries $h_{ii}$ are each point's LEVERAGE. Leverage is a
property of the design and not of the data: it depends on where a point sits
among the settings that were chosen, not on what it measured. Every $h_{ii}$
lies between 0 and 1, and because $H$ is idempotent its trace equals the
number of free parameters $p$, so the leverages average to $p/n$ over $n$
points whatever the data turn out to be. A design that is evenly spread keeps
every leverage close to that average. A design with one point sitting far
from the rest, on whatever axis the model is fit against, concentrates
leverage there instead.

What leverage close to one means follows directly from the algebra. As
$h_{ii}\to1$, the fitted value at that point converges to the measured value
at that point, whatever it is, so the residual there shrinks toward zero
regardless of whether the measurement is right or wrong. The fit is not
tested against such a point. It is drawn through it.

Case-deletion diagnostics are one idea, applied to different targets: refit
with point $i$ removed and ask what changed. The DELETED STUDENTIZED
RESIDUAL compares the point's own value against a fit that never saw it,
scaled by an error estimate that also excludes it, and answers whether the
point looks OUTLYING. COOK'S DISTANCE asks how far the entire fitted vector,
equivalently every parameter at once, moves when the point is dropped, and
answers whether the point is INFLUENTIAL on the fit as a whole. DFFITS asks
the same question narrowed to that point's own fitted value. DFBETA narrows
it further still, to how much one NAMED coefficient moves, which matters
whenever a fit carries several free parameters and a point could move one of
them without touching the rest.

Outlyingness and influence are different axes, and a point can sit at either
extreme without the other. A point far off the trend at low leverage is
caught by a large residual and barely moves the fit, because the rest of the
design anchors the line against it: outlying without being influential. A
point at leverage near one can carry almost no residual, having pulled the
fit to itself, and still swing the fit entirely if it is removed: influential
without being outlying. The second case is the one worth remembering, because
nothing built from the residual alone can see it.

## What problem it solves

A residual, weighted correctly or not, answers whether a point looks
surprising against the fitted model. It does not answer whether the point
matters, and the two questions come apart exactly where it counts: at high
leverage an error is absorbed into the fit rather than flagged by it, so the
point that would do the most damage if it were wrong is the one least likely
to look wrong. Case-deletion diagnostics answer the second question directly,
by actually removing a point and measuring what moves, instead of judging the
point from a residual that its own pull on the fit has already shrunk.

## Where this repository uses it

The repository's influence audit, run on 2026-08-16, computed leverage,
deleted residuals, Cook's distance and drop-one comparisons on two of its own
committed constructions, rather than reading either one from its residual
plot alone.

The first target was the four-point width-against-density construction
behind the self-broadening slope. Its design puts three cooler temperature
blocks close together in density and its hottest block, the 130 °C anchor
described on [self-broadening](self-broadening.md) and in
[methods chapter 7](../methods/07_what_we_found.md), alone at the far end of
the density axis, the same span [the chapter on the method and its
limits](../big_picture/02_the-method-and-its-limits.md) describes as
extending the density lever from a ×16.2 to a ×52.5 arm once that point is
folded in. A straight line through four points shaped like that leaves the
anchor almost nothing to be checked against, and the audit's leverage
computation confirmed it directly: on every one of the four peaks, the
anchor's leverage came out within a hair of the maximum value of one, so the
construction cannot in principle distinguish an accurate anchor from a wrong
one from its own fit.

That sharpens something the record already reports rather than contradicting
it. [`results/lever_crosscheck.csv`](../../results/lever_crosscheck.csv)
carries the same comparison read the other way: folding the 130 °C point
into the joint fit moves $\beta_\text{self}$ from 0.0534 to 0.0198 MHz per
$10^{12} \mathrm{cm^{-3}}$ for $^{85}\text{Rb}$, and from 0.0534 to 0.0219 for
$^{87}\text{Rb}$, a shift the file logs directly and one comparable in size to the
coefficient itself. That is what a leverage close to one predicts: a point
that anchors a fit moves the fit by close to its own scale whenever it is
added or removed. It is also why the density-slope coefficient in
[self-broadening](self-broadening.md) is reported as a bound rather than a
value.

The second target was the five-point power sweep behind the joint
light-shift bound in [RESULTS.md](../RESULTS.md). Here the audit found the
opposite of the usual worry: the low-power condition, the one carrying by far
the largest error bar, had the lowest leverage of the five power points on
most peaks and was neither outlying by its deleted residual nor influential
by Cook's distance on any of them, consistent with a correctly weighted fit
already discounting an imprecise point on its own account. One separate
condition on one peak did come out outlying without being influential, the
low-leverage half of the distinction above, worth a closer look rather than a
finding by itself at that rate across eight constructions checked.

The repository's practice of reporting leave-one-out subsets is the same
case-deletion idea applied by hand, at the scale of a whole condition rather
than a single point. [RESULTS.md](../RESULTS.md) records that the joint
light-shift bound survives dropping any one peak, and
[`results/lever_crosscheck.csv`](../../results/lever_crosscheck.csv) carries
the analogous rows for the self-broadening slope, one per dropped peak and
one per dropped temperature block. Both are Cook's distance and DFBETA in
spirit, run by hand at the resolution of a condition before either name was
attached to the practice.

Nothing committed moved as a result of the audit. Its use is forward-looking
rather than corrective: a future density ladder spread more evenly across
density itself, rather than evenly across temperature, would lower the
anchor's leverage and let the coefficient be checked by the fit instead of
anchored to one point in it.

## What can go wrong

A textbook Cook's-distance cutoff such as $4/n$ assumes enough degrees of
freedom for its null distribution to behave the way the rule of thumb
expects. With as few points as the four-point density construction carries,
the null is heavy tailed, and a generic cutoff calls nearly every condition
influential, which is a statement about the design rather than about any one
point. The audit above calibrates against a null built for that specific
design instead, by parametric bootstrap, rather than a fixed number carried
over from a much larger textbook example.

A studentized residual computed with the point still IN the fit lets an
outlier inflate its own yardstick and hide from the very test meant to catch
it. The repair is the externally studentized, deleted residual, whose
denominator is recomputed with the point left out, and an early version of
this repository's own instrument made exactly this mistake before its own
ceiling test caught it.

A related implementation trap sits in how a diagnostic is validated rather
than in the diagnostic itself. A synthetic check that only ever plants its
test error at a low-leverage point can show that a deleted residual finds
outliers, but it can never show that Cook's distance also finds influence,
since low leverage never exercises the part of a design a high-leverage point
would. Confirming both jobs needs two seeded checks, one at low leverage and
one at high.

Leverage is a design property, and no amount of repeated measurement at an
existing design point lowers it. Only adding points elsewhere on the axis
changes the leverage of the ones already there. Treating more repeats as a
fix for a design-driven leverage problem mistakes a data-insufficiency
question for a design one.

Finally, an interpretive trap specific to this family: a clean fit at a
leverage-near-one point is not evidence the point is correct, because the
construction is nearly incapable of returning anything else there. Reading
it as confirmation mistakes a blind spot for a validation.

## Try it

A small design with three points bunched together and a fourth pulled far
out on the axis, the shape a temperature sweep takes when read on a density
axis. The hat matrix diagonal shows how unevenly leverage falls across it,
and its entries sum to the number of free parameters regardless of where the
points sit.

```python
import numpy as np

x = np.array([1.0, 1.3, 1.7, 12.0])
X = np.column_stack([np.ones_like(x), x])

H = X @ np.linalg.inv(X.T @ X) @ X.T
leverage = np.diag(H)

n, p = X.shape
print(f"design: {n} points, {p} free parameters, mean leverage p/n = {p / n:.3f}")
for xi, h in zip(x, leverage):
    flag = "  <- fit passes through this point" if h > 0.9 else ""
    print(f"  x = {xi:6.2f}   leverage h_ii = {h:.4f}{flag}")
print(f"sum of leverages = {leverage.sum():.4f} (equals p = {p} for any design)")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- R. D. Cook, "Detection of Influential Observations in Linear Regression,"
  *Technometrics* 19(1), 15-18 (1977), the original definition of Cook's
  distance.
- D. A. Belsley, E. Kuh and R. E. Welsch, *Regression Diagnostics:
  Identifying Influential Data and Sources of Collinearity* (Wiley, 1980),
  for DFFITS and DFBETA.
- D. C. Montgomery, E. A. Peck and G. G. Vining, *Introduction to Linear
  Regression Analysis*, 5th ed. (Wiley, 2012), chapter 6, for leverage and
  the case-deletion family together.
- [Wikipedia: Leverage (statistics)](https://en.wikipedia.org/wiki/Leverage_(statistics))
  and [Wikipedia: Cook's distance](https://en.wikipedia.org/wiki/Cook%27s_distance).
- [Weighted least squares](weighted-least-squares.md), whose closing section
  this page answers.
- [Collisional self-broadening](self-broadening.md), the coefficient whose
  four-point construction motivated this audit.

## See also

- [Robust fitting](robust-fitting.md), the losses that discount a point once
  diagnostics like these say it is not simply outlying.
- [Resampling](resampling.md), for building a leverage or Cook's-distance
  threshold from the design's own null distribution rather than a textbook
  cutoff.
- [Heavy-tailed models](heavy-tailed-models.md), for treating a whole
  population of large residuals as a property of the noise rather than one
  point at a time.
- [Sensitivity analysis](sensitivity-analysis.md), the same which-input-
  matters question asked of a projection's parameters instead of a fit
  already run.

---

[← wiki index](README.md) · *Robustness and influence, 1 of 7* · [Robust fitting →](robust-fitting.md)
