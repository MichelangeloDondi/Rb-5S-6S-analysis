# Doppler-free two-photon spectroscopy

*[wiki index](README.md) · technique*

## What it is

In a warm vapour, atoms move, and a moving atom sees a shifted laser
frequency. Since the velocities span a thermal distribution, an ordinary
absorption line is smeared over hundreds of megahertz by the Doppler effect,
which buries every narrower feature in it.

Two-photon spectroscopy removes the smearing with geometry rather than with
cooling. Send the beam through the vapour and retro-reflect it, so every atom
sees two counter-propagating beams of the same frequency $\nu$. An atom
moving with velocity component $v$ along the beam sees the photon it meets
head-on shifted up to $\nu(1+v/c)$ and the one it runs from shifted down to
$\nu(1-v/c)$. If it absorbs ONE FROM EACH, the two-photon resonance condition
is

$$\nu\Big(1+\tfrac{v}{c}\Big) + \nu\Big(1-\tfrac{v}{c}\Big) = 2\nu$$

and the velocity term cancels exactly to first order, FOR EVERY ATOM. Not for
a selected velocity class: the whole ensemble contributes to one narrow line.
A second-order term proportional to $(v/c)^2$ survives and is normally
negligible.

Three consequences follow, and all three shape how such an experiment is
built. The transition is driven at half its own frequency, so the transition
axis is twice the laser axis and every frequency has to be labelled with
which axis it is on. Atoms that take both photons from the SAME direction are
not Doppler-free, and they produce a broad pedestal underneath the narrow
line. And because the detuning sums both photons, laser frequency jitter
enters TWICE rather than once: the fluctuation is common to both photons,
being one source retro-reflected onto itself, so it adds where the Doppler
shift cancels. A two-photon line is twice as sensitive to laser noise as a
single-pass one.

## What problem it solves

It makes sub-megahertz structure visible in a room-temperature vapour cell,
without a trap, a beam or any cooling. That is why two-photon transitions
carry so many optical frequency standards: the linewidth is set by the atom
and the apparatus rather than by the temperature.

## Where this repository uses it

It is the measurement. The 5S to 6S transition in rubidium is driven by two
993 nm photons in a retro-reflected beam through a warm cell, and the
fluorescence from the decay back down is what the detector counts.
[Methods chapter 1](../methods/01_the_measurement.md) derives the cancellation
and sets out the four hyperfine components the experiment resolves.

Two of the consequences above are load-bearing here. Every frequency in the
repository is quoted on the transition axis unless its name says otherwise,
which is the convention stated at the top of
[the methods index](../methods.md), and getting it wrong is a factor-of-two
error in a width. And the doubled laser-noise sensitivity is why the laser
linewidth enters the line shape with a factor of two already applied, which
matters because no independent diagnostic of that laser's jitter exists for
this epoch.

## What can go wrong

The retro-reflection is an experimental limitation as much as a technique.
The cancellation is exact only if the two beams are truly counter-propagating,
and a small crossing angle leaves a residual Doppler width proportional to
that angle, which broadens the line in a way that mimics a physical
mechanism. Imperfect retro-reflection also changes the balance between the
Doppler-free peak and its pedestal.

The pedestal's SIZE is computable and worth knowing before a scan is
designed. The Doppler-free line is driven by the cross term between the two
beams while the pedestal is driven by the same-beam terms, so their areas
stand as $4\rho$ to $1+\rho^2$ in the retro ratio, and dividing each by its
own width turns that into heights. For this apparatus the pedestal comes out
near half a per cent of the line peak, spread over a width set by the thermal
speed rather than by the atom. Two consequences follow: it is far too flat to
mimic any narrow feature, and it is faint enough that seeing it at all takes a
span wide enough to show its curvature.

The pedestal is a model failure waiting to happen. It is broad enough that
across a narrow scan it looks flat, so a free baseline absorbs it entirely
and it can be neither measured nor excluded. Any analysis quoting a small
excess in the wings of such a line should ask whether the pedestal, rather
than the atom, is what the baseline is standing in for.

Finally, an inference trap specific to the doubled sensitivity. A laser whose
linewidth is not independently known contributes a width that must be fitted,
and it is degenerate with every other broadening mechanism in the line, which
is the subject of [the Voigt profile](voigt-profile.md) and of
[identifiability](identifiability.md).

## Try it

What the technique buys, in one number: the width the line would have had.

```python
import math
from rb5s6s import LAMBDA_LASER_M

kb, m_rb = 1.380649e-23, 1.41e-25
v = math.sqrt(8 * math.log(2) * kb * 403.15 / m_rb)
print(f"one-photon Doppler width {2 * v / LAMBDA_LASER_M / 1e6:.0f} MHz")
print("counter-propagating pair: cancels to first order, for every atom")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/biraben1974.md`](../lit/biraben1974.md), the founding experimental
  demonstration that the Doppler pedestal vanishes only when the atom takes
  one photon from each counter-propagating beam.
- [`../lit/biraben1979.md`](../lit/biraben1979.md) for the finite-transit
  lineshape this technique actually produces.
- [Transit-time broadening](transit-time-broadening.md) for what sets the
  width once the Doppler width is gone.

---

[← wiki index](README.md) · *Experimental spectroscopy, 1 of 8* · [Standing waves →](standing-waves.md)
