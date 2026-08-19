# Sweep rate and detection lag

*[wiki index](README.md) · physical effect*

**The question.** How does a fast continuous sweep forge width and
asymmetry that a slow one would not, and how is that instrumental
component separated from the atoms' own.
**Takes.** That a fit reads skew as light-shift information, established
in [The third cumulant](third-cumulant.md) and assumed here rather than
re-argued.
**Gives.** The regression of apparent width against inverse sweep rate,
the causal-kernel argument for why a lag forges asymmetry and not only
width, and the two-rate design this repository specifies.
**Skip if.** The question is how densely a line is sampled rather than how
fast it can be crossed, a case covered by
[Designing an acquisition](designing-an-acquisition.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A line can be measured two ways. STEP AND SETTLE parks the laser at one
frequency, waits for the detector and its amplifier to reach a steady
reading, records it, and moves on, so every point is a measurement of the
line alone. A CONTINUOUS SWEEP instead moves the frequency throughout the
whole record, and every sample now carries a small residue of the detector's
own response to whatever the light was doing an instant before, because no
real detector or amplifier reports a change in optical power instantly.

That residue is not noise, it is structure. The trace a continuous sweep
actually records is the true line convolved with the detector's response,
with the convolution taken IN TIME, since the response is a property of the
electronics reacting moment to moment, not of frequency as such. A fit that
converts the time axis to a frequency axis through the sweep rate and reads
the convolved trace as though it were the line itself reports a width that
is too large, because it is measuring the shape of a convolution rather than
the shape of the line.

The scaling follows from timing alone. Crossing a true linewidth $\Delta\nu$
at a sweep rate $R$ (frequency per unit time) takes a time $\Delta\nu / R$,
which is the line's own contribution to how long the feature lasts on the
oscilloscope. The detector adds a further smearing on a timescale set by its
own electronics, a rise time or an integration window, call it $\tau$, and
that timescale does not depend on how fast the laser happens to be moving.
The apparent width measured on the time axis is therefore close to

$$w(R) \approx \frac{\Delta\nu}{R} + \tau$$

linear in the inverse of the rate, with slope $\Delta\nu$ and intercept
$\tau$. Measuring the same line at several sweep rates and regressing the
apparent time-width against $1/R$ recovers both quantities from one
consistent dataset: the slope is the physical width the line actually has,
and the intercept is the lag the electronics contribute regardless of speed.

The part that matters most is not the width at all. A detector or amplifier
can only respond to what has already happened, never to what is about to
happen, so its impulse response is CAUSAL and therefore ONE-SIDED in time,
zero before the event and decaying after it. Convolving a symmetric line
with a one-sided kernel does not produce a symmetric result, it smears one
side of the trace more than the other, and an asymmetric TRACE is exactly
what a symmetric LINE looks like once a one-sided response has acted on it.
A detection lag therefore forges asymmetry, not only width, and it does so
in the one observable that a light-shift measurement of this kind is built
to read. The separation still works for the same reason it works for the
width: a physical asymmetry belongs to the line and does not care how fast
the line is crossed, while an instrumental one belongs to the response, so
it grows with sweep rate and reverses if the sweep direction reverses.
Measuring the same line at several rates therefore separates a real
asymmetry from a manufactured one exactly as it separates a real width from
an inflated one, and neither a better model at one rate nor more averaging
at one rate can substitute for the comparison across rates.

## What problem it solves

A single trace, taken at one sweep rate, cannot tell a physical width and
asymmetry apart from an instrumental one, because both a real line and a
convolved one produce a trace that some model can fit. Sweeping the same
line at more than one rate turns that ambiguity into a resolved question: a
component that scales with rate is the acquisition, and a component that
does not is the atoms. It converts a design choice, how fast to scan, from a
matter of convenience into a testable claim about what the recorded shape
actually contains.

This is a different question from how densely a line is sampled, which
[designing an acquisition](designing-an-acquisition.md) covers. That page
asks how many points sit across a feature at a given span and record
length. This one asks how fast those points can be taken before the
detection chain's own response time starts writing itself into the shape
the points describe, and both questions have to be answered before a scan
rate is chosen.

## Where this repository uses it

[Section 10c.3 of the fixed-lock chapter](../plan/09_the-fixed-lock.md)
specifies a two-speed sweep, slow across each line and fast between them,
and states plainly that the slow segment is required rather than merely
convenient, because a detection lag degrades the standardised skew faster
than it degrades the width, and the skew is the channel the light-shift
measurement reads, as [the third cumulant](third-cumulant.md) page's own
account of the same mechanism sets out in full. [Section 10c.10 of the
following chapter](../plan/10_the-fixed-lock-instrument.md) turns the
regression above into a design requirement rather than a convenience of its
own: the two sweep rates are specified to run INTERLEAVED within each block,
with nothing else in the block changed, because the lag separation needs the
same line measured at several rates under otherwise identical conditions.

**Nothing on this page has been run on real data.** The 2025 campaign
acquired at a single sweep rate throughout, so the rate-scaled and
rate-independent components have never been separated in this experiment:
the separation is a design of the next session, and the paragraph above
states a requirement rather than a result.

One instrument detail decides whether the rate-scaled component exists at
all. A causal smoothing filter delays the trace by about half its window, so
its lag is rate-scaled and the up and down halves of a triangular sweep
split symmetrically about the true centre. A zero-phase filter, which is
what the LeCroy's ERes math function specifies, produces no delay and
therefore no splitting, so the same design measures a lag on one instrument
and confirms its absence on the other. Where the smoothing sits and what it
does to phase is
[resolution enhancement and what it costs](resolution-enhancement-and-what-it-costs.md).

## What can go wrong

The first failure is a model one. The scaling above assumes a single,
first-order response with one characteristic timescale, and a real
detection chain, photodiode, transimpedance stage, any following filter, can
have more than one time constant or a response that is not exponential at
all. The qualitative separation still holds as long as the instrumental
component is genuinely rate-scaled and the physical one genuinely is not,
but the intercept of the regression above then no longer maps onto a single
clean number the way the formula suggests.

The second is data insufficiency dressed as a clean result. Two rates that
are too close together barely move the apparent width or skew at all, and a
regression through two similar points is dominated by noise rather than by
the underlying line, which can return a slope or an intercept that looks
plausible without actually constraining either quantity. A spread of rates,
together with a check that the intercept vanishes when no lag is present,
is what turns the regression into an actual test rather than a curve drawn
through too few points.

The third is an implementation trap specific to this repository. Two
different documents in the plan both ask for a second sweep rate, and they
test two different pieces of physics. This page and
[section 10c.3](../plan/09_the-fixed-lock.md) are about a detection lag that
inflates width and forges skew.
[Section 10b.6 of the acquisition record](../plan/08_the-acquisition-record.md)
asks for a second rate for an unrelated reason, that a laser linewidth
accumulates over the time the scan takes to cross the line while a
collisional width does not, so the two rates there separate a laser
contribution from a collisional one. Treating the two requirements as one
test because both mention a second sweep rate misses whichever effect the
chosen pair of rates does not happen to probe.

The fourth is an experimental limitation worth naming rather than assuming
away. A rate-scaled detection lag is not the only route to a convolution
that fakes a line asymmetry. Correlated amplitude and frequency noise on the
driving light produces an asymmetric field spectrum of its own, and the
measured line is the convolution of that spectrum with the atomic response,
which skews the line with no detector involved at all, a distinct mechanism
documented in [Camparo and Klimcak](../lit/camparo1992b.md). That route does
not scale with sweep rate, so the multi-rate regression above cannot see
it, and it needs its own discriminator, principally that it does not scale
with the optical power at the atoms the way a light shift does.

## Try it

A synthetic symmetric line convolved with a one-sided exponential response
at two sweep rates, with a fixed detector time constant. The half-maximum
width and the third standardised moment (the skew) both grow with rate, and
the skew, zero for the true line, grows in relative terms far faster than
the width does.

```python
import numpy as np


def gaussian(x, sigma):
    y = np.exp(-0.5 * (x / sigma) ** 2)
    return y / np.trapezoid(y, x)


def causal_exponential(x, scale):
    """A one-sided response kernel: zero for x < 0, decaying for x >= 0."""
    y = np.where(x >= 0, np.exp(-x / scale), 0.0)
    return y / np.trapezoid(y, x)


def fwhm(x, y):
    half = y.max() / 2.0
    above = x[y >= half]
    return above[-1] - above[0]


def skewness(x, y):
    """Third standardised moment of y(x), treated as a density."""
    p = y / np.trapezoid(y, x)
    mean = np.trapezoid(x * p, x)
    var = np.trapezoid((x - mean) ** 2 * p, x)
    m3 = np.trapezoid((x - mean) ** 3 * p, x)
    return m3 / var ** 1.5


dx = 0.01
x = np.arange(-60.0, 60.0, dx)                  # MHz, a synthetic axis
true_line = gaussian(x, sigma=1.0)               # the true, symmetric line
true_fwhm = fwhm(x, true_line)
print(f"true line: FWHM = {true_fwhm:.3f} MHz, skew = "
      f"{skewness(x, true_line):+.4f} (symmetric)")

tau_ms = 0.25                                    # a fixed detector time constant
results = []
for rate in (1.0, 5.0):                          # MHz per ms
    lag_mhz = tau_ms * rate                      # the fixed lag, read on this axis
    kernel = causal_exponential(x, lag_mhz)
    trace = np.convolve(true_line, kernel, mode="same") * dx
    w, s = fwhm(x, trace), skewness(x, trace)
    results.append((rate, w, s))
    print(f"rate {rate:>4.1f} MHz/ms: apparent FWHM = {w:.3f} MHz "
          f"({(w / true_fwhm - 1) * 100:+.1f}% over true), skew = {s:+.4f}")

(r1, w1, s1), (r2, w2, s2) = results
width_growth = (w2 - true_fwhm) / (w1 - true_fwhm)
skew_growth = s2 / s1
print(f"from {r1:.0f} to {r2:.0f} MHz/ms the width excess grew "
      f"{width_growth:.1f}x and the skew grew {skew_growth:.1f}x: "
      "the asymmetry is the more sensitive of the two")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [Camparo and Klimcak](../lit/camparo1992b.md), the distinct correlated
  amplitude-and-frequency-noise mechanism that convolves a driving field's
  own asymmetric spectrum into the line without any detector involved.
- P. Horowitz and W. Hill, *The Art of Electronics*, 3rd ed. (Cambridge
  University Press, 2015), for amplifier bandwidth, rise time, and the
  first-order response this page's lag kernel stands in for.
- [Wikipedia: exponentially modified Gaussian
  distribution](https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution),
  the closed form for a symmetric line convolved with a one-sided
  exponential, and its standard skewness formula.
- [The third cumulant](third-cumulant.md), for the cumulant-additivity
  argument that makes the skew a clean channel for an asymmetric mechanism
  in the first place, and for the same lag mechanism developed in terms of
  the standardised skew this repository's own fit reads.
- [Designing an acquisition](designing-an-acquisition.md), the companion
  question of how densely a line is sampled, including the raw-storage and
  per-sweep timestamp requirements a multi-rate regression of the kind
  described above needs in order to run at all.

## See also

- [The third cumulant](third-cumulant.md) for why skew is the channel a
  light-shift fit reads, and the same lag mechanism developed there in
  standardised-skew terms.
- [Designing an acquisition](designing-an-acquisition.md), the companion
  question of point density rather than sweep speed.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md),
  the previous page, for the calibration this convolution acts on top of.
- [Photon counting](photon-counting.md), the next page, another
  detection-chain property that can be mistaken for the atoms' own signal.

---

[← Laser frequency noise and the linewidth](laser-frequency-noise-and-the-linewidth.md) · *Driving, modulating and detecting, 5 of 8* · [Designing an acquisition →](designing-an-acquisition.md)
