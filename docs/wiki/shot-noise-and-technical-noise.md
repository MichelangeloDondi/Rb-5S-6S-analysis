# Shot noise and technical noise

*[wiki index](README.md) · concept*

**The question.** Whether the noise limiting a measurement is the irreducible
statistics of the quanta being counted, or something the apparatus is adding.
**Takes.** Measurements at several settings of a control the experimenter can
change.
**Gives.** The scaling test that separates the two, what each implies about
what to fix, and why the distinction decides where effort goes.
**Skip if.** The question is the functional form of the variance against
signal, which is [the noise law](the-noise-law.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

**Shot noise** is the counting statistics of discrete events. Photons arrive
as a Poisson process, so a measurement collecting $N$ of them carries a
variance of $N$ and a fractional uncertainty of $1/\sqrt{N}$. It is a property
of the quanta and of nothing else, and no improvement to the apparatus removes
it. Only collecting more quanta does.

**Technical noise** is everything the apparatus adds: amplifier and Johnson
noise, digitiser quantisation, pickup, laser intensity fluctuations,
mechanical vibration, temperature drift. It is not fundamental, it can in
principle be engineered away, and the engineering differs completely by
source.

The distinction matters because the two respond to opposite interventions. A
shot-limited measurement is improved only by more signal or more time. A
technically limited one is improved by fixing the apparatus, and collecting
longer may not help at all.

## The scaling test, which is the whole method

Neither type announces itself. What separates them is how the noise responds
when a control is changed, because their dependences differ.

**Against the signal level.** Shot noise grows as the SQUARE ROOT of the
signal, so the fractional noise FALLS as the signal rises. A multiplicative
technical noise, such as laser intensity fluctuation, grows in PROPORTION to
the signal, so the fractional noise is constant. An additive technical noise
does not grow at all. Those three behaviours are the three terms of
[the noise law](the-noise-law.md) and fitting it is one way to run this test.

**Against averaging.** Shot noise falls as the square root of the number of
independent samples, indefinitely. Technical noise with a long correlation
time does not: it averages down only until the averaging window reaches its
correlation time, after which more data buys nothing. A measurement whose
uncertainty stops improving with time is technically limited by definition.

**Against a control that moves the signal without moving the apparatus.** This
is the sharpest version and it needs a designed comparison rather than a fit.
If a control changes the number of quanta collected while leaving the chain
untouched, the noise must track the square root of the signal. A departure is
technical, and the direction of the departure names the class.

## What problem it solves

It decides where effort goes, and the two answers are expensive in different
ways. Believing a shot-limited measurement is technically limited leads to
buying quieter electronics that change nothing. Believing a technically
limited measurement is shot-limited leads to integrating for hours against a
noise that does not average down.

## Where this repository uses it

The scaling test is run in both directions on the committed noise law.

**The shot term is confirmed as shot.** Its coefficient is flat against laser
power across the four hyperfine lines, with log-log exponents between $-0.08$
and $+0.10$, which is what a property of the detection chain rather than of
the condition should do.

**The excess term is essentially absent**, needed in one condition of
thirty-two, so multiplicative technical noise is not limiting this experiment
and stabilising the laser's amplitude would buy nothing.

**And the floor failed the test in an informative way.** A floor is
signal-independent by construction, yet this one rises with laser power on
every line, so it is not instrumental. It is an optical background that scales
with the drive, and the same conclusion appears in the directly measured
off-line noise, which is not a fitted quantity at all.

A second measured fact belongs here because it is the averaging half of the
test: the noise is correlated over several samples, so it averages down more
slowly than the sample count suggests. That correction has
[its own page](correlated-samples-and-effective-sample-size.md).

## What can go wrong

**Concluding from one setting.** A single condition cannot separate scalings.
The test needs the control varied, and varied enough that the predicted
behaviours differ by more than the uncertainty.

**Confusing a fitted floor with an instrumental one.** The model's floor is
whatever does not scale with the signal being fitted, which includes optical
backgrounds that scale with something else entirely.

**Assuming shot noise is the best case.** It is the best case for a given
number of collected quanta, and collection efficiency is an apparatus property
that technical effort CAN improve. Shot-limited does not mean optimised.

**Forgetting the detector's own multiplication noise.** A photomultiplier's
gain process adds excess variance above Poisson, by a factor that is a
property of the tube. A measurement can be limited by counting statistics and
still be a fixed factor worse than the ideal Poisson bound.

## Try it

How the three behaviours separate as the signal is varied, and how quickly.

```python
import math

for name, exponent in (("additive technical", 0.0),
                       ("shot", 0.5),
                       ("multiplicative technical", 1.0)):
    row = [f"{(V ** exponent):8.3f}" for V in (0.01, 0.1, 1.0, 10.0)]
    print(f"{name:26s} sigma at V=0.01,0.1,1,10: " + " ".join(row))
print("\nfractional noise, which is what a measurement actually feels:")
for name, exponent in (("additive technical", 0.0),
                       ("shot", 0.5),
                       ("multiplicative technical", 1.0)):
    row = [f"{(V ** (exponent - 1)):8.2f}" for V in (0.01, 0.1, 1.0, 10.0)]
    print(f"{name:26s} " + " ".join(row))
print("\nonly the multiplicative one is flat: that is its signature")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- A. van der Ziel, *Noise in Solid State Devices and Circuits* (Wiley, 1986),
  for the taxonomy of technical noise sources and their spectra.
- P. R. Bevington and D. K. Robinson, *Data Reduction and Error Analysis for
  the Physical Sciences*, 3rd ed. (McGraw-Hill, 2003), for Poisson statistics
  and their propagation.

## See also

- [The noise law](the-noise-law.md), which parametrises the three behaviours
- [Correlated samples and effective sample size](correlated-samples-and-effective-sample-size.md),
  the averaging half of the test
- [Photon counting](photon-counting.md), the regime where shot noise is
  counted directly rather than inferred
- [Digitisation and dynamic range](digitisation-and-dynamic-range.md), for one
  specific technical contribution and when it matters

---

[← The noise law](the-noise-law.md) · *Noise and its management, 2 of 5* · [Correlated samples and effective sample size →](correlated-samples-and-effective-sample-size.md)
