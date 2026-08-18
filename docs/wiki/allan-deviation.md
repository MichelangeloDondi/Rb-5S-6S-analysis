# Allan deviation

*[wiki index](README.md) · concept, supporting topic*

**The question.** How can a record's own wander identify which noise
process produced it, and how long is worth averaging.
**Takes.** An evenly sampled time series. No other wiki page is required
first.
**Gives.** The Allan variance definition, the slope that separates white
noise from a random walk on a log-log plot, and why an ordinary standard
deviation fails on a drifting record.
**Skip if.** You want to know why this repository has no timestamped
record to run this statistic on, rather than the statistic itself. That is
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
blocks is what makes it useful: a slow drift shifts both members of a pair by
nearly the same amount and cancels, so the statistic reports the wander
between neighbouring windows rather than the total excursion of the record.

The ordinary standard deviation cannot do this. For a record whose mean is
drifting, the standard deviation depends on how long you watched, and it
grows without limit as you keep watching. The Allan deviation is finite for
those records and its SHAPE identifies the noise: on a log-log plot,
white frequency noise falls as $\tau^{-1/2}$, because averaging longer helps,
a random walk rises as $\tau^{+1/2}$, because averaging longer hurts, and
flicker noise is flat. A minimum in the curve marks the averaging time beyond
which drift overtakes the benefit of averaging.

![two synthetic records and their Allan deviations](figures/wiki_allan_deviation.png)

*Two synthetic records. In the time series on the left the white noise is
obviously noisier, and nothing about the picture says which one you can
average away. On the right the two separate cleanly by slope, and the
crossing marks where the quieter-looking record becomes the worse one.*

## What problem it solves

An oscillator, a laser lock or any reference has more than one noise process
acting at once, and they matter over different timescales. The question a
measurement actually asks is "how long should I average", and that has an
answer only if the noise types can be told apart. The Allan deviation turns
that into a reading off a slope.

## Where this repository uses it

Not in the committed analysis. The 2025 campaign saved no long-term
wavemeter logs, so the laser-frequency record consists of dated screen
photographs rather than a time series, and a statistic that needs evenly
sampled data has nothing to run on. What the record does carry about laser
drift is in [APPARATUS.md section 6](../APPARATUS.md) and in
[`constants.DRIFT_RATE_LASER_HZ_PER_MIN`](../../rb5s6s/constants.py), which
is an envelope bounding every photograph rather than a measured stability
curve.

The page is here because the next session should produce data this applies
to. [PLAN.md](../plan/10_the-fixed-lock-instrument.md) asks for the wavemeter log to be saved rather than
photographed, and for a comb on every block, which together would give both a
frequency record and a repeated width measurement. The Allan deviation of the
tooth width across a session is then the natural check on whether the ruler
itself is stable over the times the fits assume, which no current dataset can
answer.

## What can go wrong

The commonest error is a data-insufficiency one wearing a model's clothes: a
curve computed from too few blocks at long $\tau$ has enormous scatter, and
the last two or three points of a log-log plot routinely look like a rising
drift branch when they are noise on the estimator. Confidence intervals
narrow roughly as the number of blocks, so the tail of the curve deserves the
least trust and usually gets the most attention.

Two more, both about what the statistic is defined on. A record with a
deterministic linear ramp removed is a different record, and the Allan
deviation of the residual is not the Allan deviation of the instrument. And
dead time between samples changes the estimator's meaning, which is why the
overlapping and modified variants exist. Quoting a bare "Allan deviation"
without saying which one is quoting an ambiguous number.

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
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- D. W. Allan, "Statistics of atomic frequency standards", *Proc. IEEE* **54**,
  221 (1966), the original definition.
- W. J. Riley, *Handbook of Frequency Stability Analysis*, NIST Special
  Publication 1065 (2008), which is free, thorough and the standard practical
  reference for the variants and their confidence intervals.
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
  descriptor on this wiki, isolating a lineshape's asymmetry rather than a
  noise process.

---

[← The third cumulant](third-cumulant.md) · *Mathematical descriptors, 2 of 2* · [wiki index →](README.md)
