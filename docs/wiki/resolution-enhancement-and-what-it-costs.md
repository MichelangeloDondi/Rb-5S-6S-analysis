# Resolution enhancement and what it costs

*[wiki index](README.md) · technique*

**The question.** Where the extra bits come from when an eight-bit instrument
delivers twelve, what they cost, and why the same feature on two makes of
oscilloscope behaves differently enough to change an experiment's design.
**Takes.** An instrument, a smoothing setting, and a signal slower than the
converter.
**Gives.** The two different rates at which averaging buys bits, the reason a
smoothed trace can still export as eight bits, and the one case where smoothing
shifts a line centre.
**Skip if.** The question is how many bits the measurement needs at all, which
is [digitisation and dynamic range](digitisation-and-dynamic-range.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Every oscilloscope in ordinary laboratory use has an eight-bit converter, and
eight bits is 256 levels across the screen. That is far too coarse for a
measurement that wants a per cent of a line height, and instruments therefore
offer a smoothing feature that trades bandwidth for resolution. The trade is
real rather than cosmetic, because averaging genuinely reduces the uncertainty
of each reported number. What is easy to get wrong is how much resolution is
bought, where the feature sits in the instrument, and what else it changes.

## Two different rates, and mistaking one for the other

Averaging $N$ samples buys resolution at two different rates, and instrument
documentation quotes both, sometimes on the same page.

**Word length grows by one bit for every factor of two.** Averaging two
eight-bit readings can land halfway between codes, so the result needs a ninth
bit to be written down. This is the number that sets the quantisation grid in
an exported file, and it is what you recover by looking at the smallest voltage
step present in the data.

**Noise falls by one bit for every factor of four.** Averaging $N$ independent
samples reduces the standard deviation by $\sqrt{N}$, and a factor of two in
noise is one bit, so

$$\text{bits gained} = \log_4 N = \tfrac{1}{2}\log_2 N.$$

This is the physically meaningful figure, the one that says how much better the
measurement actually is.

The two differ by a factor of two in the exponent, so at 256 averages the word
length has grown by eight bits while the noise has fallen by four. **Reading the
word-length number as if it were the noise number overstates the improvement by
a factor of two in bits**, which is a factor of four in variance. The
Agilent manual states both: an extra bit per factor of two, and noise reduced by
one half per factor of four.

In this repository the distinction has a concrete use. The quantisation grid of
the campaign traces gives 11.86 bits, which is a word length. It says the
instrument wrote fine-grained numbers. It does not say the measurement is
twelve-bit good, and the question of whether the grid matters at all is settled
separately by the dither ratio below.

## Whether any of it matters: the dither ratio

Quantisation is harmless whenever the step is small against the noise, because
the noise itself moves the signal across codes and averaging recovers what
rounding discarded. The quantisation contribution adds in quadrature,

$$\sigma_{\text{total}} = \sqrt{\sigma^2 + \Delta^2/12},$$

so with $\sigma / \Delta = 30$, as measured on the campaign traces, the
quantisation term inflates the noise by 0.008 per cent. At a ratio of
$\sigma / \Delta = 1.37$, as measured on the rehearsal traces, it inflates it
by 1.8 per cent.
**Neither instrument was resolution-limited as it was used**, and the four-bit
difference between them bought nothing on the traces that were taken. The bits
are unspent headroom, and the place they would be spent is holding one vertical
range across a power ladder rather than switching range at every rung.

## Where the feature lives, which is the trap

The same capability is an acquisition mode on one make and a math function on
the other, and the difference decides what ends up in the file.

| | acquisition mode | math function |
|---|---|---|
| example | Agilent High Resolution | LeCroy ERes |
| acts on | the samples as they are acquired | a stored trace, producing a second trace |
| what the channel export contains | the smoothed samples | the raw eight-bit samples |

**A smoothed trace on the screen does not imply a smoothed trace in the file.**
Where the feature is a math function it creates a separate trace, and saving the
channel saves the unsmoothed data no matter what is displayed. This is not a
hypothetical. The 2025-07-04 rehearsal traces measure 7.74 bits across their
signal swing, which is raw eight-bit behaviour, while the campaign traces from
the other instrument measure 11.86, which an eight-bit converter cannot produce
at any record length.

**What the measurement does not settle is why.** A math-function smoothing that
was configured but exported from the channel, and a smoothing that was never
enabled, leave identical files. The lesson is therefore the operational one
rather than a diagnosis of either session: where the feature is a math function,
the export has to be checked, because the two cases are indistinguishable
afterwards.

The practical rule is to check the exported file rather than the front panel.
The smallest nonzero voltage difference in the file is the quantisation step,
and $\log_2(\text{swing}/\text{step})$ is the delivered word length. It takes
one pass over the data and it cannot be fooled by the display.

## What it costs, and the part that can move a line centre

Smoothing is low-pass filtering, so it costs bandwidth. ERes states the
exchange exactly, each half bit halving the passband:

| resolution increase (bits) | -3 dB bandwidth (× Nyquist) | filter length (samples) |
|---|---|---|
| 0.5 | 0.5 | 2 |
| 1.0 | 0.241 | 5 |
| 2.0 | 0.058 | 24 |
| 3.0 | 0.016 | 117 |

For a spectroscopic line crossed in tens of milliseconds against a converter
running at gigasamples per second, this cost is unreachable. Bandwidth is not
the scarce resource in this experiment and it is not a reason to leave
smoothing off.

**The phase response is the part that can bite.** A filter with a constant zero
phase does not move features in time, and ERes is specified that way, its manual
stating that the filters do not distort the relative position of different
events and that the usual filtering delay is exactly compensated. A plain
causal average does move features, by roughly half its window.

That distinction matters as soon as the frequency axis is swept in both
directions. On a triangular scan a causal filter delays the line on the
ascending and descending halves in opposite directions along the frequency
axis, so the two halves disagree about the centre by twice the lag, and the
midpoint of the two recovers the true centre while the splitting measures the
lag. Under a zero-phase filter there is no such splitting, because there is no
lag, and the two halves are simply two independent crossings.

**So the same experimental design yields a free lag calibration on one
instrument and nothing to calibrate on the other**, and which of those is true
is a property of the filter's phase rather than of the experiment.

## What can go wrong

The most common error is the one above, reading a word-length figure as a noise
figure and claiming twice the improvement actually obtained. The second is
assuming the exported data carries what the screen showed. The third is
reaching for more bits when the dither ratio already says quantisation
contributes a fraction of a per cent, which spends bandwidth to buy nothing.

A fourth is subtler and worth stating because smoothing invites it. Averaging
adjacent samples correlates them, so a smoothed record contains fewer
independent points than it has samples, and any uncertainty computed as if the
samples were independent is too small. That is the subject of
[correlated samples and effective sample size](correlated-samples-and-effective-sample-size.md),
and a smoothing setting is one of the things that can put the correlation there.
Where the smoothing decimates to the output rate the stored samples can still be
independent, and where it filters without decimating they are not, so the
setting alone does not settle it and the autocorrelation has to be measured.

## Where this is used

The instrument comparison and the per-rung range analysis are in
[the acquisition settings chapter](../plan/07_acquisition-settings.md). The
apparatus record carries the unresolved question of which mode the campaign
actually ran in, in [APPARATUS.md](../APPARATUS.md).

---

[← Digitisation and dynamic range](digitisation-and-dynamic-range.md) · *Noise and its management, 5 of 6* · [Photon counting →](photon-counting.md)
