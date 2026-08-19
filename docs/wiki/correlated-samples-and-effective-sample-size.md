# Correlated samples and effective sample size

*[wiki index](README.md) · method*

**The question.** How many INDEPENDENT measurements a dataset actually
contains, when adjacent points are not independent.
**Takes.** Any series whose points were acquired in order, and its residuals.
**Gives.** The autocorrelation time, the design effect it implies, and the
places an uncorrected sample count silently inflates a result.
**Skip if.** The question is how large each point's uncertainty is, which is
[the noise law](the-noise-law.md). This page is about how many of them count.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Almost every statistical formula in ordinary use assumes independent samples.
The standard error of a mean falls as one over the square root of $n$, a
chi-square has as many degrees of freedom as there are points, and an
information criterion penalises parameters against $\log n$. All of them take
$n$ to be a count of independent things.

Real measurements rarely oblige. A detection chain with a finite response time
smooths the noise, so consecutive samples share it. A drifting apparatus makes
consecutive traces share an offset. Any correlation means the effective number
of independent samples is smaller than the count, sometimes by a lot.

The standard summary is the **integrated autocorrelation time**,

$$\tau = 1 + 2\sum_{k \ge 1} \rho_k,$$

with $\rho_k$ the autocorrelation at lag $k$. It is one for independent
samples and larger otherwise, and it is a divisor:

$$n_{\text{eff}} = n / \tau.$$

In the survey literature the same quantity appears as the **design effect**,
the factor by which a clustered design's variance exceeds an independent
one's, and the vocabulary is worth knowing because the correction is
identical.

## What problem it solves

It stops a measurement from claiming precision it does not have. Every one of
the following is wrong by the square root of $\tau$, or by $\tau$ itself, when
the correction is skipped: the error on a mean, the significance of a trend,
the width of a confidence interval, and the verdict of a model comparison.
Since $\tau$ is often between two and ten, the resulting overstatement is
routinely a factor of two or three in significance, which is exactly the range
that turns a null into a finding.

## Where this repository uses it, and where it once bit

The correlation is measured per condition alongside the noise law and
committed beside it, as an integrated autocorrelation time and a white-noise
ratio. The median across the campaign's conditions is about **3.8 samples**,
so a trace's effective sample count is roughly a quarter of its raw one.

It enters the record in three distinct places, and they are worth
distinguishing because the mechanism is the same and the unit is not.

  * **Within a trace**, where adjacent samples are not independent. This is
    the 3.8 above. **Attributing it correctly took two attempts and the
    lesson generalises**: it was first read as the detection chain's own
    response time, and it is in fact the acquisition's high-resolution mode,
    which averages adjacent samples in hardware. The distinction matters
    because a chain's response is a constraint while a smoothing mode is a
    SETTING, and the second can be reduced when bandwidth is wanted. Either
    way, oversampling beyond the correlation length adds points without
    adding information.
  * **Within a condition**, where the repeats of one cell share drift and
    alignment. Here the correction is a cluster or block treatment rather than
    a per-sample one, and the residual scatter about a fit is used as a
    between-block term.
  * **In model comparison**, where an information criterion's parameter
    penalty must be computed on the effective count rather than the raw one.
    The record carries both versions of one such comparison, and they DISAGREE
    in their verdict, which is the sharpest available demonstration that the
    correction is not cosmetic.

**Where it bit.** An apparently significant trend in one channel, at better
than three standard deviations, collapsed to an interval consistent with zero
once a block bootstrap accounted for an intraclass correlation of 0.38 across
the repeats of each cell. The estimator was not at fault and five independent
versions of it agreed. The sample count was.

## What can go wrong

**Correcting once and forgetting the other level.** Correlation within a trace
and correlation between traces are different quantities with different
divisors, and fixing one says nothing about the other.

**Estimating $\tau$ from too short a series.** The sum over lags is noisy, and
a naive sum over all lags diverges. Practical estimators truncate the sum
self-consistently, and a $\tau$ estimated from a few hundred samples is itself
uncertain by tens of per cent.

**Assuming smoothing is harmless.** Any filter, hardware or software, imposes
correlation. A high-resolution acquisition mode that averages adjacent samples
has bought effective bits by spending independence, and the arithmetic
downstream must know.

**Confusing correlation with a wrong noise law.** Both inflate a chi-square. A
noise law fitted per condition and validated against a directly measured
scatter separates them, because a mis-scaled law fails that comparison and
correlation does not.

## Try it

How badly an uncorrected count overstates a significance, at the measured
correlation length.

```python
import math

n = 2000
for tau in (1.0, 2.0, 3.79, 8.0):
    n_eff = n / tau
    print(f"tau = {tau:4.2f}: n_eff = {n_eff:7.0f}, "
          f"error bars widen by {math.sqrt(tau):.2f}x, "
          f"a naive 4.0 sigma becomes {4.0/math.sqrt(tau):.1f} sigma")
print("\nat the measured 3.79 a four-sigma claim is really about two")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- A. Sokal, "Monte Carlo methods in statistical mechanics", in *Functional
  Integration* (Springer, 1997), for the integrated autocorrelation time and
  the self-consistent truncation its estimation requires.
- L. Kish, *Survey Sampling* (Wiley, 1965), which introduced the design effect,
  the same correction reached from clustered sampling rather than from time
  series.

## See also

- [The noise law](the-noise-law.md), which describes each sample's variance
  while this page counts the samples
- [Resampling](resampling.md), where the block bootstrap applies this
  correction without estimating tau explicitly
- [Information criteria](information-criteria.md), whose penalty depends on
  the effective count
- [Confounding by acquisition order](confounding-by-acquisition-order.md), the
  other way an acquisition's structure enters an inference

---

[← Shot noise and technical noise](shot-noise-and-technical-noise.md) · *Noise and its management, 3 of 5* · [Digitisation and dynamic range →](digitisation-and-dynamic-range.md)
