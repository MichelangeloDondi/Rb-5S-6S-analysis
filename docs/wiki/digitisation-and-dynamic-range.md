# Digitisation and dynamic range

*[wiki index](README.md) · technique*

**The question.** How finely an analogue signal must be digitised before the
digitiser stops mattering, and what changing the vertical range mid-experiment
costs.
**Takes.** A signal, a range setting and a noise level.
**Gives.** The number of levels a measurement needs, the reason a vertical
range is a physics setting rather than a display preference, and why a range
changed between points turns one measurement into several.
**Skip if.** The question is whether to count photons instead of digitising a
current at all, which is [photon counting](photon-counting.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A digitiser maps a voltage range onto a finite number of integers. With $b$
bits there are $2^b$ of them, so the step between adjacent codes is the range
divided by $2^b$. Rounding to the nearest code adds an error uniform over one
step, whose standard deviation is

$$\sigma_q = \frac{\Delta}{\sqrt{12}} \approx 0.29 \Delta,$$

with $\Delta$ the step. That is the whole of the theory. Everything that
matters follows from comparing $\sigma_q$ with the noise already present.

**The comparison that decides the setting.** If the signal's own noise is much
larger than $\sigma_q$, digitisation is free: the noise dithers the signal
across many codes and averaging recovers resolution the single sample does not
have. If $\sigma_q$ is comparable to or larger than the noise, the digitiser
becomes the dominant error and no amount of averaging fixes it, because the
error is deterministic given the input rather than random.

A useful rule of thumb, and it is only that: a feature needs roughly thirty
codes across it before quantisation stops contributing meaningfully to a
width or an area estimate.

## What problem it solves

It converts a knob into an arithmetic problem. Given the dynamic range a
measurement must span and the noise it must not be dominated by, the number of
bits required is fixed, and so is the answer to whether one range setting can
serve a whole measurement.

## The trap: a range that moves under the measurement

This is the part that costs experiments results, and it is invisible in the
stored data unless someone looks for it.

Autoscaling, whether by the instrument or by a careful operator, keeps each
individual trace beautifully filling the screen. It does so by changing the
range between traces. Every range on a real instrument carries its own gain
and offset calibration, specified to perhaps one to three per cent, and those
errors are not common between ranges. So a series of measurements taken on
different ranges is a series of measurements on different instruments, joined
by calibration constants nobody recorded.

For a single trace this is harmless. For a measurement that compares traces,
which is what any sweep or ladder does, it is a systematic that enters
exactly where the comparison lives. The signature is characteristic: the
error tracks how much signal each point delivered, because that is what
decided which range it was measured on, so an effect that is really the
instrument's appears ordered by brightness.

The two repairs are ordinary. Hold one range across everything being compared,
which is possible only if the bit depth covers the full span. Or, where it
cannot be held, deliberately measure one point on both ranges wherever the
range changes: the ratio of the two readings of one physical signal measures
the range-to-range gain ratio, turning an unknown into a calibration.

## Where this repository uses it

The 2025 sessions did not hold the range, and the cost was measured on
2026-08-18 by reading the quantisation step out of the stored samples, since
no vertical setting was ever recorded. Across a single power ladder the step
changed by a factor of 48 to 596 depending on the line, against a signal
spanning about 80, and the number of codes actually used per trace varied by a
factor of seven. The measured departure of the two-photon amplitude from its
expected square-of-power law is ordered by line brightness rather than by any
atomic property, which is the signature above, and
[the amplitude departure note](../notes/amplitude_departure_from_p2.md)
carries the evidence.

The arithmetic that follows sets a requirement for the next session, written
out in
[the acquisition-settings chapter](../plan/07_acquisition-settings.md): the
signal goes as the square of the power, so a ladder over a factor of nine in
power spans eighty-one in amplitude, and holding one range with the top point
at 80 per cent of full scale leaves an eight-bit digitiser about two and a
half codes at the bottom rung and a twelve-bit one about forty.

## What can go wrong

**Confusing effective bits with nominal bits.** Averaging and
high-resolution modes buy resolution by exchanging bandwidth, so a nominally
eight-bit instrument can deliver far finer steps than its specification while
its response time lengthens. Both numbers matter and they exchange against each
other.

**Assuming dither is present.** The argument that noise rescues resolution
requires noise larger than a step. A quiet baseline digitised coarsely does
not dither, and its average is biased toward the nearest code rather than
converging on the truth.

**Reading the range off the specification rather than the data.** The step
actually used is visible in any stored trace as the smallest nonzero spacing
between distinct sample values, which is how this repository recovered
settings nobody had written down.

**Filling the screen.** Putting a peak at 95 per cent of full scale leaves no
headroom for the excursions a real experiment produces, and a clipped peak is
a lost trace rather than a slightly compressed one.

## Try it

The two numbers that decide a setting: how many codes a feature spans, and
whether quantisation or the signal's own noise dominates.

```python
import math

full_scale, bits, noise = 1.0, 8, 2e-3      # volts, bits, per-sample sigma
step = full_scale / 2 ** bits
sigma_q = step / math.sqrt(12)
print(f"{bits}-bit over {full_scale} V: step {step*1e3:.2f} mV, "
      f"quantisation sigma {sigma_q*1e3:.2f} mV")
print(f"signal noise {noise*1e3:.2f} mV, so noise/quantisation = "
      f"{noise/sigma_q:.1f}")
print("above about 1 the noise dithers and averaging recovers resolution")

span = 81.0                                  # a P^2 ladder over 9x in power
for b in (8, 12, 14):
    top = 0.8 * 2 ** b
    print(f"{b:2d}-bit: brightest rung {top:8.0f} codes, "
          f"dimmest {top/span:7.1f} codes")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- W. Kester, ed., *The Data Conversion Handbook* (Analog Devices, 2005), for
  the quantisation-noise result and the effective-number-of-bits definition.
- B. Widrow and I. Kollár, *Quantization Noise* (Cambridge, 2008), for when
  the uniform-error model holds and when dither is required to make it hold.

## See also

- [Photon counting](photon-counting.md), for the regime where the analogue
  chain is abandoned rather than digitised better.
- [Designing an acquisition](designing-an-acquisition.md), where span,
  resolution and record length are decided together.
- [Confounding by acquisition order](confounding-by-acquisition-order.md), the
  other way an acquisition choice becomes a physics claim.
- [The noise law](the-noise-law.md), for the measured noise that
  quantisation has to be compared against.

---

[← Correlated samples and effective sample size](correlated-samples-and-effective-sample-size.md) · *Noise and its management, 4 of 6* · [Resolution enhancement and what it costs →](resolution-enhancement-and-what-it-costs.md)
