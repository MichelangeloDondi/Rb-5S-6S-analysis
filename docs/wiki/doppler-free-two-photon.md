# Doppler-free two-photon spectroscopy

*[wiki index](README.md) · technique*

**The question.** What makes a two-photon transition immune to the
first-order Doppler shift, and what that immunity costs.
**Takes.** The general wavevector-closure rule from
[Doppler-free geometries](doppler-free-geometries.md). No fitting, no data.
**Gives.** The retro-reflected cancellation worked out for two photons, the
same-beam pedestal it leaves behind, and the doubled laser-noise sensitivity
that follows from summing both photons' detuning.
**Skip if.** You want the general closure rule for any photon count and
colour combination, not this apparatus's two-photon case. That is
[Doppler-free geometries](doppler-free-geometries.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

In a warm vapour, atoms move, and a moving atom sees a shifted laser
frequency. Since the velocities span a thermal distribution, an ordinary
absorption line is smeared over hundreds of megahertz by the Doppler effect,
which buries every narrower feature in it.

![A fitted Doppler-free two-photon line with its fit residuals](../../figures/fig0_spectrum.png)

*A fitted Doppler-free line with its residuals, from this campaign's own data.*

Two-photon spectroscopy removes the smearing using geometry, without cooling.
Send the beam through the vapour and retro-reflect it, so every atom sees two
counter-propagating beams of the same frequency $\nu$. An atom moving with
velocity component $v$ along the beam sees the photon it meets head-on
shifted up to $\nu(1+v/c)$ and the one it runs from shifted down to
$\nu(1-v/c)$. If it absorbs one from each, the two-photon resonance condition
is

$$\nu\Big(1+\tfrac{v}{c}\Big) + \nu\Big(1-\tfrac{v}{c}\Big) = 2\nu$$

and the velocity term cancels exactly to first order, for every atom. The
cancellation covers the whole ensemble, not a single selected velocity class,
so every atom contributes to one narrow line. A second-order term
proportional to $(v/c)^2$ survives and is normally negligible.

Three consequences follow. The transition is driven at half its own
frequency, so the transition axis is twice the laser axis, and every
frequency has to be labelled with which axis it is on. Atoms that take both
photons from the same direction are not Doppler-free and produce a broad
pedestal underneath the narrow line. And because the detuning sums both
photons, laser frequency jitter enters twice, not once. It is one source
retro-reflected onto itself, so the same fluctuation reaches both photons and
adds where the Doppler shift cancels. A two-photon line is twice as sensitive
to laser noise as a single-pass one.

## What problem it solves

It makes sub-megahertz structure visible in a room-temperature vapour cell,
without a trap, a beam, or any cooling. The linewidth is set by the atom and
the apparatus, not by the temperature, which is why two-photon transitions
are used for so many optical frequency standards.

## Where this repository uses it

It is the measurement. The 5S to 6S transition in rubidium is driven by two
993 nm photons in a retro-reflected beam through a warm cell, and the
fluorescence from the decay back down is what the detector counts.

![The 5S to 6S level scheme with its resolved hyperfine components](../../figures/fig13_level_scheme.png)

*The 5S1/2 to 6S1/2 level scheme driven by two 993 nm photons, with the four resolved hyperfine components.*

[Methods chapter 1](../methods/01_the_measurement.md) derives the
cancellation and sets out the four hyperfine components the experiment
resolves.

Two of the consequences above are load-bearing here. Every frequency in the
repository is quoted on the transition axis unless its name says otherwise,
which is the convention stated at the top of
[the methods index](../methods.md), and getting it wrong is a factor-of-two
error in a width. And the doubled laser-noise sensitivity is why the laser
linewidth enters the line shape with a factor of two already applied, which
matters because no independent diagnostic of that laser's jitter exists for
this epoch.

## Crossover resonances, and why this geometry has none

**One word, three meanings, and they are unrelated.** This repository uses
"crossover" for three different things, and mixing them is easy because two
of them live on neighbouring pages. A *crossover resonance* is the spurious
extra line of saturated-absorption spectroscopy, and it is this section's
subject. A *crossover pathway* is one of the sideband pairs that feed a single
comb tooth, in [the two-photon comb](the-two-photon-comb.md). The *noise
crossover* is the signal level at which a detector's constant electronic
floor gives way to shot noise, in
[weighted least squares](weighted-least-squares.md) and
[photon counting](photon-counting.md). Nothing connects them beyond the
word.

**What a crossover resonance is**, because a reader who has not built a
saturated-absorption lock has no reason to know. Take a pump beam and a
counter-propagating probe through a warm vapour, and two transitions that
share a level, at frequencies $\nu_1$ and $\nu_2$. An atom moving at
velocity $v$ sees the two beams Doppler-shifted in opposite directions. At
one particular speed, $v = (\nu_2-\nu_1)\lambda/2$, the pump comes into
resonance with one transition at the same moment the probe comes into
resonance with the other. That single velocity class is therefore addressed
by both beams at once. The pump burns a population hole in it, the probe
reads the hole, and a signal appears at the arithmetic midpoint of the two
real lines, $(\nu_1+\nu_2)/2$, where no transition exists. Crossovers are
often taller than the lines they sit between, and the reason is not the one
usually given. The class they select sits at nonzero speed, so it is less
populated than the zero-velocity class the ordinary saturated-absorption dip
addresses. What makes them tall is that two classes feed one feature, moving
at plus and minus that speed, where the dip has only the single class at
rest. That is a factor of two before the Boltzmann reduction takes some of it
back, and optical pumping adds more in an open system.

**The mechanism needs two ingredients and this geometry supplies neither.**
It needs a *shared level*, so that a hole burnt by one transition is visible
to the other. And it needs *velocity selection*, so that one velocity class
can link two different frequencies. In Doppler-free two-photon spectroscopy
every velocity class contributes at the same summed frequency, which is the
entire point of the counter-propagating geometry, so no velocity class is
singled out and there is nothing for a second transition to be selected
against. And the hyperfine components here differ in both their ground and
their excited level, so they share no state in which a hole could be burnt.
The absence is structural. It is not a matter of the crossovers being weak
or unresolved, and a line found at the midpoint of two of these would need a
different explanation entirely.

**This is a feature and not only a curiosity.** A saturated-absorption
spectrum of four lines carries six crossovers on top of them, and telling
the two kinds apart is a standing chore. Every peak in the spectra this
record fits is a real transition, which is why the four-line assignment
needs no disentangling step.

With a modulated drive, photon pairs mixing different sidebands might seem
to make extra lines between the comb teeth. They do not, and the reason is
interference and not absence. Every pathway with the same frequency sum
lands on the same tooth, so the tooth weights are Bessel functions of the
total modulation depth and not sums over pairs. Those pathways are the
crossover pathways of the second meaning above, and
[the two-photon comb](the-two-photon-comb.md) works out what happens to
them when the retro delay stops them interfering cleanly.

## What can go wrong

The retro-reflection is an experimental limitation as much as a technique.
The cancellation is exact only if the two beams are truly counter-propagating,
and a small crossing angle leaves a residual Doppler width proportional to
that angle, which broadens the line in a way that mimics a physical
mechanism. Imperfect retro-reflection also changes the balance between the
Doppler-free peak and its pedestal.

The pedestal's size is computable and worth knowing before a scan is
designed. The Doppler-free line is driven by the cross term between the two
beams while the pedestal is driven by the same-beam terms, so their areas
stand as $4\rho$ to $1+\rho^2$ in the retro ratio, and dividing each by its
own width turns that into heights. For this apparatus the pedestal comes out
near half a per cent of the line peak, spread over a width set by the thermal
speed, not by the atom. Two consequences follow. It is far too flat to mimic
any narrow feature, and it is faint enough that seeing it at all takes a span
wide enough to show its curvature.

The pedestal is broad enough that across a narrow scan it looks flat, so a
free baseline absorbs it entirely, and it can be neither measured nor
excluded. Any analysis quoting a small excess in the wings of such a line
should ask whether the pedestal, not the atom, is what the baseline is
standing in for.

Finally, the doubled sensitivity creates a specific inference trap. A laser
whose linewidth is not independently known contributes a width that must be
fitted, and that width is degenerate with every other broadening mechanism in
the line, which is the subject of [the Voigt profile](voigt-profile.md) and
of [identifiability](identifiability.md).

## Try it

The width the line would have had without this technique, in one number.

```python
import math
from rb5s6s import LAMBDA_LASER_M

kb, m_rb = 1.380649e-23, 1.41e-25
v = math.sqrt(8 * math.log(2) * kb * 403.15 / m_rb)
print(f"one-photon Doppler width {2 * v / LAMBDA_LASER_M / 1e6:.0f} MHz")
print("counter-propagating pair: cancels to first order, for every atom")
```

## Further reading

- [`../lit/biraben1974.md`](../lit/biraben1974.md), the founding experimental
  demonstration that the Doppler pedestal vanishes only when the atom takes
  one photon from each counter-propagating beam.
- [`../lit/biraben1979.md`](../lit/biraben1979.md) for the finite-transit
  lineshape this technique actually produces.
- [Transit-time broadening](transit-time-broadening.md) for what sets the
  width once the Doppler width is gone.

## See also

- [Doppler-free geometries](doppler-free-geometries.md), the general
  closure rule this page specialises to two photons.
- [Standing waves](standing-waves.md), what the same retro-reflected beams
  do to the intensity pattern underneath the cancelled line.
- [The Voigt profile](voigt-profile.md), where the doubled laser-noise
  sensitivity enters the fitted line shape.
- [Identifiability](identifiability.md), why the laser width cannot be
  separated from the other widths on a single line.

---

[← wiki index](README.md) · *Experimental spectroscopy, 1 of 11* · [Standing waves →](standing-waves.md)
