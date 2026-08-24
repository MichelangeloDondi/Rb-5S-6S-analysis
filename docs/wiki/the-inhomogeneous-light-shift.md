# The inhomogeneous light shift

*[wiki index](README.md) · concept*

**The question.** Why the light shift of an atom in a structured beam is a
distribution and not a number, how a lineshape reads that distribution, and
why the same object grades a guided-platform design before it is built.
**Takes.** [The AC-Stark shift](ac-stark-shift.md) for the single-atom
coefficient, [the beam waist](the-beam-waist.md) for what an intensity
profile is, and [standing waves](standing-waves.md) for the fringe
structure a retro-reflected drive adds.
**Gives.** The distribution view, the intensity-squared weighting that
decides which atoms speak, the cumulant reading of what a line can recover,
and the transfer of all three to a guided mode.
**Skip if.** You want the coefficient's bound and its
construction, which is [the AC-Stark dossier](../quantities/ac-stark-light-shift.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A light shift follows intensity, and in any structured beam the intensity
depends on where the atom sits. An ensemble therefore has no single shift.
It has a distribution of shifts, one value per atom position, and the
observed line is the unshifted line convolved with that distribution. The
distribution's mean moves the line, its variance broadens it, and its skew
makes the shape asymmetric, so the first few cumulants of the position
distribution are printed directly onto the lineshape.

Which atoms contribute is itself intensity-weighted. A two-photon signal
scales as intensity squared, so the bright centre of a focused beam is
over-represented relative to the wings, and the distribution the line
reports is the intensity-squared-weighted one, narrower and pushed toward
the peak shift relative to the geometric distribution of atoms. A
retro-reflected drive adds fringe structure on top, and whether an atom
averages over fringes during its transit or samples one fringe is a
question of speed, covered in [standing waves](standing-waves.md).

The peak shift at the focus is the scale of the whole object. This
repository computes it as $S_0$, the shift at beam centre at full power,
and the distribution hangs below it.

## What problem it solves

It turns the light shift from a feared systematic into an object the
data can grade. A single shifted frequency could hide inside a drifting
lock, but a distribution has a shape, and a shape survives where absolute
positions are unusable. What this record then holds is the three-step
chain in its proper order: no shift was detected, the width channel
bounded the scale below the predicted value, and the prediction is
thereby excluded at 95 per cent. A bound is not a measurement of the
shift, and this page's object is what makes even the bound possible on a
dataset whose absolute frequencies carry no information.

The same object is the design quantity of a guided platform. Inside a
hollow core or on a nanofibre the mode profile replaces the free-space
Gaussian, every trapped or guided atom samples the mode's intensity
profile, and the spread of shifts across that profile is what limits
a cooling scheme's bandwidth and a superposition's coherence. A design
that quotes one number for the trap depth has not yet asked the question
this page is about.

## Where this repository uses it

The ramp model of [the composite lineshape](../methods/04_the_composite_model.md)
carries the shift distribution's broadening as its $S_0^2$ term, the only
live handle in the 2025 data since the pull channel is dead in the drift.
The joint three-session bound and its prediction are constructed in
[the AC-Stark dossier](../quantities/ac-stark-light-shift.md), and the
fringe-resolved treatment of the slow tail is in
[standing waves](standing-waves.md). The digital twin propagates the same
distribution into its forecasts, and the guided-platform outlook carries
it for a mode profile in
[chapter 6 of the big picture](../big_picture/06_next-nanofibre.md) and
[the guided-atoms page](guided-atoms-and-nanofibres.md).

## What can go wrong

**Quoting the peak shift as the shift.** $S_0$ is the distribution's
scale, and the line's centroid moves by an intensity-weighted average
that is smaller. The two differ by a geometry factor that depends on the
waist, the retro ratio and the transit, so a comparison of a computed
$S_0$ against a fitted centroid shift without that factor compares two
different quantities.

**Forgetting the intensity-squared weighting.** A one-photon intuition
weights atoms by intensity. The two-photon line weights them by its
square, and the difference moves every cumulant.

**Assuming the fringes wash out.** They do when the transit crosses many
fringes quickly. The slow tail of a thermal ensemble does not, it samples
the standing wave, and the resulting skew is treated in
[standing waves](standing-waves.md).

**Treating the distribution's shape as fixed while the waist varies.**
The whole object scales with the waist through $S_0 \propto 1/w_0^2$ and
through the transit time, so a waist uncertainty is not one uncertain
number but an uncertain distribution, which is why the measured waist
gates every absolute statement in the dossier.

## Try it

The committed machinery reproduces the case page's own prediction: the
peak shift at 225 mW, the measured waist and the assumed retro ratio.

```python
from rb5s6s.stark import stark_shift_S0_mhz, W0_MEASURED_M, RHO_RETRO

S0 = stark_shift_S0_mhz(0.225, W0_MEASURED_M, rho=RHO_RETRO)
print(f"peak shift S0 at 225 mW, measured waist: {S0:.3f} MHz")
```

The bound this is compared against, and the subset spread that dominates
its systematic, are constructed in the dossier with every number carried
in `results/stark_joint.csv`.

## Further reading

- R. Grimm, M. Weidemüller and Y. B. Ovchinnikov, "Optical dipole traps
  for neutral atoms," *Adv. At. Mol. Opt. Phys.* 42, 95 (2000), the
  standard treatment of the single-atom shift this page distributes.
- [`../lit/perrella2013.md`](../lit/perrella2013.md), two-photon
  spectroscopy inside a hollow-core fibre, where the guided mode's
  intensity profile is the one the atoms sample.
- [`../lit/vylegzhanin2023.md`](../lit/vylegzhanin2023.md), the nanofibre
  geometry of the same question.

## See also

- [The AC-Stark shift](ac-stark-shift.md), the single-atom coefficient
  this page turns into an ensemble object.
- [Standing waves](standing-waves.md), the fringe structure and the
  slow-tail skew.
- [Transit-time broadening](transit-time-broadening.md), the clock that
  decides how much of the profile one atom averages.
- [The beam waist](the-beam-waist.md), the geometry the distribution
  scales with.
- [Guided atoms and nanofibres](guided-atoms-and-nanofibres.md), where
  the mode profile replaces the Gaussian and the same machinery grades
  the design.

---

[← The AC-Stark shift](ac-stark-shift.md) · *Experimental spectroscopy, 7 of 11* · [Saturation →](saturation.md)
