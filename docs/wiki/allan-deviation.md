# Allan deviation

*[wiki index](README.md) · concept, supporting topic*

**The question.** How can a record's own wander identify which noise
process produced it, and how long is worth averaging.
**Takes.** An evenly sampled time series. No other wiki page is required
first.
**Gives.** The Allan variance definition, the slope that separates white
noise from a random walk on a log-log plot, and why an ordinary standard
deviation fails on a drifting record.
**Skip if.** You want the reason this repository has no timestamped record
to run this statistic on. That is
[designing an acquisition](designing-an-acquisition.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

The Allan deviation measures how much a quantity wanders when you average it
over a window of length $\tau$, as a function of $\tau$. Take a record,
divide it into consecutive blocks of $\tau$ samples, average each block, and
look at the differences between neighbouring block averages. The Allan
variance is half the mean squared difference,

$$\sigma_y^2(\tau) = \tfrac{1}{2}\big\langle (\bar y_{k+1}-\bar y_k)^2 \big\rangle$$

and the Allan deviation is its square root. Taking differences of adjacent
blocks is what makes it useful: a slow drift shifts both members of a pair
by nearly the same amount and cancels, isolating the wander between
neighbouring windows from the record's total excursion.

![Two synthetic time series and their Allan deviation curves](figures/wiki_allan_deviation.png)

*Two synthetic records that a plain standard deviation cannot tell apart,
separated cleanly by slope once read as an Allan deviation.*

The ordinary standard deviation cannot do this: for a record whose mean is
drifting it depends on how long you watched, and grows without limit as you
keep watching. The Allan deviation is finite for those records and its shape
identifies the noise: on a log-log plot, white frequency noise falls as
$\tau^{-1/2}$, because averaging longer helps, a random walk rises as
$\tau^{+1/2}$, because averaging longer hurts, and flicker noise is flat. A
minimum in the curve marks the averaging time beyond which drift overtakes
the benefit of averaging.

## What problem it solves

An oscillator, a laser lock or any reference has more than one noise process
acting at once, and they matter over different timescales. The question a
measurement actually asks is "how long should I average", and that has an
answer only if the noise types can be told apart. The Allan deviation turns
that into a reading off a slope.

## Where this repository uses it

Not in the committed analysis: the 2025 campaign saved no long-term
wavemeter logs, so the laser-frequency record is dated screen photographs,
distinct from an evenly sampled time series, with nothing for the statistic
to run on. What the record does carry about laser drift is in
[APPARATUS.md section 6](../APPARATUS.md) and in
[`constants.DRIFT_RATE_LASER_HZ_PER_MIN`](../../rb5s6s/constants.py), an
envelope bounding every photograph, distinct from a measured stability
curve.

![Wavemeter drift recorded as a dated screen photograph](../apparatus/2025-06-11_wavemeter_drift_23min.jpg)

*One of the dated wavemeter screen photographs that stands in for a
continuous log in the 2025 record, the reason this statistic has nothing to
run on yet.*

[PLAN.md](../plan/10_the-fixed-lock-instrument.md) asks for the wavemeter
log to be saved instead of photographed, and for a comb on every block,
giving both a frequency record and a repeated width measurement. The Allan
deviation of the tooth width across a session would then be the check on
whether the ruler itself is stable over the times the fits assume, a
question no current dataset can answer.

## The estimator that saturates

The reason this statistic exists is that the obvious one has no limit.
Under $1/f$ noise the variance of a record grows with the record, because
each decade of duration admits another decade of low-frequency power, so the
raw scatter of a series is an estimate of a quantity that does not exist.
Its sampling spread then saturates instead of shrinking: measured on
synthetic flicker in this repository, the fractional spread of the raw
scatter sits near 23 per cent at one hundred points and near 23 per cent at
ten thousand, while the Allan deviation at fixed averaging time tightens
from 7 to 0.8 per cent over the same records. A precision that stops
improving with data is the signature to watch for. See
[laser frequency noise and the linewidth](laser-frequency-noise-and-the-linewidth.md)
for where this decided a design question.

## What can go wrong

The commonest error mistakes data insufficiency for a real drift branch: a
curve computed from too few blocks at long $\tau$ has enormous scatter, and
the last two or three points of a log-log plot routinely look like a rising
trend when they are noise on the estimator. Confidence intervals narrow
roughly with the number of blocks, so the tail of the curve deserves the
least trust and usually gets the most attention.

Two further pitfalls concern what the statistic is defined on. A record
with a deterministic linear ramp removed is a different record, and the
Allan deviation of the residual is not the Allan deviation of the
instrument. Dead time between samples also changes the estimator's meaning,
which is why the overlapping and modified variants exist. Quoting a bare
"Allan deviation" without saying which one is quoting an ambiguous number.

Finally, an implementation trap: the factor of one half in the definition
above is what makes the white-noise Allan deviation equal the ordinary
standard deviation at $\tau$ of one sample. An implementation that drops it
is wrong by $\sqrt2$ everywhere and looks entirely plausible.

## Try it

Two records a plain standard deviation cannot tell apart, separated by how
they average down.

```python
import numpy as np

rng = np.random.default_rng(11)
n = 1 << 13
white = rng.standard_normal(n)
walk = np.cumsum(rng.standard_normal(n)) * 0.02

def adev(y, m):
    k = len(y) // m
    a = y[:k * m].reshape(k, m).mean(axis=1)
    return np.sqrt(0.5 * np.mean(np.diff(a) ** 2))

print(f"{"tau":>6}{"white":>12}{"random walk":>14}")
for m in (1, 10, 100, 1000):
    print(f"{m:6d}{adev(white, m):12.4f}{adev(walk, m):14.4f}")
print("white falls as tau^-1/2, the walk rises as tau^+1/2")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite instead of sitting here misleading
a reader.

## Further reading

- D. W. Allan, "Statistics of atomic frequency standards", *Proc. Ieee* **54**,
  221 (1966), the original definition.
- W. J. Riley, *Handbook of Frequency Stability Analysis*, NIST Special
  Publication 1065 (2008), free and the standard practical reference for the
  variants and their confidence intervals.
- [Wikipedia: Allan variance](https://en.wikipedia.org/wiki/Allan_variance)
  for the slope table at a glance.

## See also

- [Designing an acquisition](designing-an-acquisition.md), the per-sweep
  timestamp channel this statistic needs and this repository's own record
  lacks.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md),
  the frequency record whose own stability this statistic would
  characterise.
- [The third cumulant](third-cumulant.md), the other mathematical
  descriptor on this wiki, isolating a lineshape's asymmetry instead of a
  noise process.

---

[← The third cumulant](third-cumulant.md) · *Mathematical descriptors, 2 of 2* · [wiki index →](README.md)
