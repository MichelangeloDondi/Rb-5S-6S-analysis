# The noise law

*[wiki index](README.md) · method*

**The question.** How large the uncertainty on each sample is, as a function
of the signal at that sample, measured rather than assumed.
**Takes.** Repeated traces of the same condition. No model of the line.
**Gives.** The variance law that supplies every fit's weights, what each of
its terms means physically, and the checks that decide whether a term is real.
**Skip if.** The question is how to USE weights once you have them, which is
[weighted least squares](weighted-least-squares.md), or whether adjacent
samples are independent, which is
[correlated samples](correlated-samples-and-effective-sample-size.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A detector's noise is rarely constant across a trace. In almost any optical
measurement it grows with the signal, because the dominant contribution is the
counting statistics of the photons themselves. The noise law is the measured
relation between the two, and the standard form is

$$\sigma^2(V) = a^2 + bV + cV^2,$$

with $V$ the signal level above baseline. The three terms are physically
distinct and that is the point of writing them separately.

  * $a$ is the **signal-independent floor**, whatever is present when the
    signal is not: detector dark noise, amplifier and Johnson noise, digitiser
    quantisation, pickup, and any optical background that does not scale with
    the quantity being measured.
  * $b$ is the **shot term**, linear in signal because photon arrivals are
    Poisson and the variance of a Poisson count equals its mean. Its
    coefficient is a property of the detection chain, gain and quantum
    efficiency, rather than of the condition.
  * $c$ is the **multiplicative or excess term**, quadratic in signal, which
    is what fractional fluctuations produce: laser intensity noise, gain
    drift, or any effect that modulates the signal by a fixed proportion.

**The three terms dominate in different places, and that is what makes the law
useful.** The floor dominates in the wings and the baseline, the shot term
dominates over most of a bright line, and the excess term, if present at all,
dominates at the peak. A measurement limited by one of them is improved by
interventions that would do nothing for the others.

## What problem it solves

It replaces a guess with a measurement at the exact point where a guess does
the most damage. Least-squares weights are one over the variance, so a wrong
noise model does not merely mis-state the error bars, it mis-weights the data
and moves the fitted parameters themselves. It also converts "reduce the
noise" from a slogan into a decision, because the term that dominates names
the intervention that would help.

## How it is measured, and the check that matters

Take several repeats of one condition, bin the samples by their signal level,
and compute the scatter within each bin. That gives $\sigma$ against $V$
directly, with no model of the line involved, and the law is fitted to those
binned points. Weights follow from the fact that the variance of a sample
variance over $n$ points goes as $2\sigma^4/n$.

**Whether to include a term is a model-selection question, not a preference.**
Fitting a term that the data do not support inflates the uncertainty on the
others, so the extra terms are admitted only when an information criterion
prefers them.

**The check worth building in**, and the one that distinguishes a fitted
parameter from a measured one: compute the noise DIRECTLY in a region where
the signal is absent, and compare it with the fitted floor. They are the same
quantity arrived at two ways, and if they disagree, the fit is absorbing
something into the floor that does not belong there.

## Where this repository uses it

The law is fitted per condition, and it supplies the weights for every fit in
the pipeline. The committed values are in
[`results/noise_model.csv`](../../results/noise_model.csv), one row per
condition, and the fitting lives in the package's noise module.

Three findings from those thirty-two conditions are worth carrying:

  * **The excess term was needed in one condition of thirty-two.** Laser
    amplitude noise and gain drift are not what limits this measurement, which
    is worth knowing before anyone stabilises them.
  * **The floor and the shot term cross near 8.8 mV**, so above the dimmest
    conditions this is a photon-counting problem.
  * **The floor is not signal-independent here**, which the law's own form
    would not reveal. It rises with laser power on every line, and the
    direct-wing check confirms it is measured rather than fitted, so the floor
    contains an optical background that scales with the drive. That the record
    could state this at all is a consequence of having built the direct check.

## What can go wrong

**Fitting the law over too small a range of signal.** The three terms are
separated by their scaling, so a fit confined to one decade of signal cannot
tell them apart, and the coefficients trade.

**Assuming the floor is instrumental.** A floor is signal-independent by
construction of the model, which is not the same as being independent of
everything. An optical background that scales with a control parameter, but
not with the signal being fitted, lands in $a$ and looks electronic.

**Forgetting that the law describes SAMPLES.** If adjacent samples are
correlated, the law is still correct per sample and the number of independent
samples is smaller than the count, which is a separate correction and a
separate page.

**Applying one condition's law to another.** Gain, alignment and background
all move between conditions, which is why a per-condition fit exists.

## Try it

The three terms and where each dominates, at the committed scales.

```python
import math

a, b, c = 1.5e-3, 1.0e-3, 0.0        # volts, volts, dimensionless
print(f"{'level (V)':>10s} {'sigma (mV)':>11s} {'floor %':>8s} {'shot %':>7s}")
for V in (0.005, 0.02, 0.1, 1.0, 4.0):
    floor, shot = a ** 2, b * V
    tot = floor + shot + c * V ** 2
    print(f"{V:10.3f} {1e3*math.sqrt(tot):11.3f} "
          f"{100*floor/tot:8.1f} {100*shot/tot:7.1f}")
print(f"\nfloor and shot cross at V = a^2/b = {1e3*a*a/b:.2f} mV")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- P. R. Bevington and D. K. Robinson, *Data Reduction and Error Analysis for
  the Physical Sciences*, 3rd ed. (McGraw-Hill, 2003), for the propagation of
  a signal-dependent variance into least-squares weights.
- W. Kester, ed., *The Data Conversion Handbook* (Analog Devices, 2005), for
  the instrumental contributions to the floor.

## See also

- [Weighted least squares](weighted-least-squares.md), which consumes this law
- [Correlated samples and effective sample size](correlated-samples-and-effective-sample-size.md),
  the correction the law itself does not carry
- [Shot noise and technical noise](shot-noise-and-technical-noise.md), for
  telling the terms apart by how they scale with the controls
- [Photon counting](photon-counting.md), for when to abandon the analogue
  chain rather than model it

---

[← wiki index](README.md) · *Noise and its management, 1 of 5* · [Shot noise and technical noise →](shot-noise-and-technical-noise.md)
