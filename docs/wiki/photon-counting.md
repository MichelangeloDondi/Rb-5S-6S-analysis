# Photon counting

*[wiki index](README.md) · technique*

## What it is

A detector that turns incident light into a number can do it two ways.
An analog chain integrates the photocurrent continuously: a photodiode or a
photomultiplier feeds a transimpedance amplifier, and the resulting voltage is
digitized on a continuous scale. A counting chain instead registers each
detected photoelectron as one discrete event, above a fixed discriminator
threshold, and reports a count or a rate. The two differ in more than
hardware. An analog voltage always carries a fixed electronic noise floor,
from Johnson noise in the amplifier, input-referred amplifier noise, ADC
quantization and dark current, all present with no light at all, on top of
the shot noise the photocurrent itself carries once light arrives. A counting
chain has no such floor: with the atoms and every light source switched off
it reports zero, on average, and what noise remains once light does arrive is
purely the statistics of how many photons were counted, which grows with the
count itself rather than sitting on top of a fixed offset.

In the variance language [Weighted least squares](weighted-least-squares.md)
sets out, $\sigma^2(V) = a^2 + bV$ for an analog signal at level $V$, with $a$
the electronic floor and $b$ the shot-noise coefficient, sometimes called a
Fano term. A counting chain measuring the same light carries only the $bV$
part, because it never inherits $a$. The two variances are therefore equal
exactly where $a^2$ equals $bV$, and that crossing is not a preference to
argue about, it is a signal level fixed by the ratio of the two measured
coefficients. Below it the floor dominates the analog chain and counting wins
outright. Above it both chains are limited by the same shot term and the
choice between them stops mattering.

Counting is not available at every rate, though. Each registered event needs
a minimum resolvable separation from the next, the dead time $\tau_d$ of the
discriminator and the electronics behind it. Two photons arriving closer
together than $\tau_d$ cannot both be registered, and for photons arriving as
a Poisson process at rate $R$ the probability of such an overlap grows with
$R\tau_d$. A discriminator and time-to-digital chain with $\tau_d$ near a
nanosecond keeps that product small out past hundreds of millions of counts
per second, while a slower gate or an older counter card with $\tau_d$ near a
microsecond saturates a thousand times sooner. A peak rate a nanosecond chain
shrugs off can put a microsecond chain deep into pile-up, so whether counting
is available is a property of the actual electronics against the actual peak
rate, not a property of counting as an idea.

Nor is counting a free upgrade even where the crossover favors it. A
threshold discriminator keeps only whether a pulse crossed the line, not how
tall it was, so two photoelectrons close enough to blur into one pulse
register as a single count indistinguishable from one photoelectron, while an
analog integrator still reports the extra charge. Below the crossover that
lost amplitude usually costs less than the floor it removes. Above the
crossover it costs the same for no gain at all. The decision is a comparison
of both effects at the level and the rate actually in use, not a rule that
favors one technology on principle.

## What problem it solves

It replaces a habit or an equipment default with a computation. Given the
measured noise law of a detection chain and the signal level an experiment
actually operates at, the crossover says whether the electronic floor a
counter removes is even the dominant term there, and the dead time says
whether a counter can keep up with the peak rate at all. Both answers come
from the same handful of measured numbers, so the choice does not have to
rest on which detector happened to be on the bench.

## Where this repository uses it

The committed noise law lives in
[`results/noise_model.csv`](../../results/noise_model.csv), one row per
condition with the fitted $a_V$ and $b_V$ coefficients, produced by
[`rb5s6s/noise.py`](../../rb5s6s/noise.py) exactly as
[Weighted least squares](weighted-least-squares.md) describes.
[`docs/plan/10_the-fixed-lock-instrument.md`](../plan/10_the-fixed-lock-instrument.md),
section 10c.6, inverts that law for the 2025 analog chain and finds the
crossover sits at a small percentage of a typical line peak, in the same
range where the Doppler pedestal and the far line wings sit, which is
where this record's open questions live. The same section works out the
peak photoelectron rate the committed coefficients imply and finds pile-up
negligible at a nanosecond dead time, so a counter would be available there,
not merely favored on paper. Two of the day-one measurements in section
10c.8, the single-pulse shape and peak count rate and a fresh noise law for
whatever chain is on the bench that day, exist to check both halves of that
argument directly rather than carry the 2025 numbers forward unmeasured. No
counting hardware has been run yet, so this is a planned instrument, not a
result.

## What can go wrong

The clearest model failure is treating "below the crossover, counting wins"
as "counting is worth switching to regardless of what it costs," which skips
the amplitude argument above and can trade a real electronic floor for a
lost-count problem that is just as large.

An implementation trap sits in the discriminator itself. Set its threshold
too low and electronic noise pulses start crossing it, so the count rate
carries a floor of its own, dark counts and afterpulses, in exactly the
regime the counting law promised would be floor-free. No single reported
count rate announces that this has happened, since a few extra counts per
second look like signal until compared against a light-off measurement.

A noise law belongs to the chain it was measured on, and the caveat
[Weighted least squares](weighted-least-squares.md) states for fit weights
applies again here: a crossover computed from an old $a_V$ and $b_V$ says
nothing reliable about a chain whose tube, gain or termination has since
changed, and reusing it can call the wrong technology the winner just as
easily as it can misweight a fit.

Finally, an experimental limitation. Running near or above the dead-time
ceiling without correcting for missed coincident photons produces a
rate-dependent shortfall that grows with signal level in the same direction a
real physical saturation would, so an uncorrected pile-up loss and an actual
saturating response are easy to mistake for each other unless the dead time
and the peak rate are checked on their own terms first.

## Try it

The signal level at which the electronic floor and the shot term are equal,
read from the committed noise law rather than assumed, and how much quieter
counting is than the analog chain a factor of ten below that level.

```python
import csv
import math

with open("results/noise_model.csv", newline="") as f:
    rows = list(csv.DictReader(f))

crossover_mv = sorted(float(r["a_V"]) ** 2 / float(r["b_V"]) * 1000.0 for r in rows)
median_mv = crossover_mv[len(crossover_mv) // 2]
print(f"{len(rows)} committed conditions in results/noise_model.csv")
print(f"median crossover level (a^2 = b*V): {median_mv:.2f} mV")
print(f"across all conditions: {crossover_mv[0]:.2f} to {crossover_mv[-1]:.2f} mV")

ratios = []
for r in rows:
    a_v, b_v = float(r["a_V"]), float(r["b_V"])
    v_star = a_v ** 2 / b_v          # the crossover level for this condition
    v = v_star / 10.0                # a factor of ten below it
    analog_sigma = math.sqrt(a_v ** 2 + b_v * v)
    counting_sigma = math.sqrt(b_v * v)   # counting never carries the a^2 floor
    ratios.append(analog_sigma / counting_sigma)

print(f"analog-to-counting noise ratio at one tenth of the crossover: "
      f"{min(ratios):.3f} to {max(ratios):.3f}")
print(f"(every condition gives the same ratio, sqrt(11) = {math.sqrt(11):.3f}, "
      "because the floor is defined to equal the shot term at the crossover)")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- G. F. Knoll, *Radiation Detection and Measurement*, 4th ed. (Wiley, 2010),
  the standard treatment of pulse counting, dead time and the paralyzable and
  nonparalyzable pile-up models used above.
- B. E. A. Saleh and M. C. Teich, *Fundamentals of Photonics*, 2nd ed.
  (Wiley, 2007), the photodetection chapter, for the shot-noise and
  electronic-noise budget of an analog receiver.
- [Weighted least squares](weighted-least-squares.md), the noise law this
  page inverts and the fit the same coefficients ultimately weight.

---

[← Sweep rate and detection lag](sweep-rate-and-detection-lag.md) · *Driving, modulating and detecting, 5 of 8* · [Designing an acquisition →](designing-an-acquisition.md)
