# Hyperfine structure

*[wiki index](README.md) · concept*

**The question.** How nuclear spin splits one electronic level into
several closely spaced $F$ sublevels, and why the pattern differs isotope
to isotope.
**Takes.** The electronic angular momentum $J$ and nuclear spin $I$ as
separate quantum numbers, nothing else assumed.
**Gives.** The interval formula for a $J=1/2$ hyperfine splitting and the
isotope-and-sublevel identity of the four measured components.
**Skip if.** the reader wants what a further applied field does to those
sublevels instead of their zero-field structure, in which case
[Magnetic sublevels](magnetic-sublevels.md) is the right page.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Many nuclei carry a nonzero angular momentum, nuclear spin $I$. That spin
couples magnetically to the atom's total electronic angular momentum $J$, and
the two combine into a total angular momentum $F$, running from $|I-J|$ to
$I+J$ in integer steps. Each allowed $F$ sits at a slightly different energy,
so one electronic level splits into several closely spaced sublevels: this is
hyperfine structure, and a transition between two electronic levels becomes a
small cluster of transitions between their sublevels instead of one line.

![Level scheme of the driven and detected transitions](../../figures/fig13_level_scheme.png)

*Term diagram of the driven and detected transitions, showing which F sublevels this two-photon line addresses.*

The dominant interaction is magnetic dipole coupling, the nuclear magnetic
moment sensing the magnetic field the electrons produce at the nucleus, with
strength set by a constant conventionally called $A$. A second interaction,
electric quadrupole coupling with constant $B$, appears only when the
nucleus's charge distribution departs from spherical and the electron cloud
has a field gradient to couple to, which needs both $I \geq 1$ and $J \geq 1$.
For a $J=1/2$ level $B$ is identically zero and only two sublevels exist,
$F=I+1/2$ and $F=I-1/2$, with energies given by the standard interval formula

$$E(F) = \tfrac{A}{2}\big[F(F+1) - I(I+1) - J(J+1)\big]$$

so that the two sublevels sit apart by exactly $A(I+1/2)$.

Nuclear spin is a property of the isotope, not of the element, so two
isotopes of the same atom carry a different $I$, a different magnetic moment
and therefore a different $A$, and their hyperfine patterns on the very same
electronic transition differ in how many sublevels there are and how far
apart they sit. A same-isotope pair of sublevels, by contrast, is set purely
by quantities intrinsic to that one nucleus and that one electronic
transition, with nothing about a different isotope entering at all.

## What problem it solves

Hyperfine structure is why a line that looks single at modest resolution
resolves into several distinct, individually addressable lines once the
resolution is high enough, and it explains their spacing from nuclear
properties measurable on their own, independent of and often far more
precisely than the optical transition itself. Because the pattern differs
isotope to isotope, it also answers an identification question: which
isotope, and which pair of sublevels, a given narrow spectral feature belongs
to. And because the sublevel spacings are fixed by constants intrinsic to the
atom, not by anything in a particular apparatus, a same-isotope spacing
doubles as an absolute frequency reference that needs no external
calibration once the constants are known.

## Where this repository uses it

The four measured components of this experiment are exactly this: hyperfine
components of two rubidium isotopes on the same $5S_{1/2} \to 6S_{1/2}$
two-photon transition. The file-label wavelengths and their isotope
assignments live in
[`constants.PEAKS`](../../rb5s6s/constants.py): 993.4207 and 993.4121 nm are
87Rb ($I=3/2$, the F=2 to F'=2 and F=1 to F'=1 lines), and 993.4192 and
993.4154 nm are 85Rb ($I=5/2$, F=3 to F'=3 and F=2 to F'=2). The ground-state
splittings, [`constants.HFS_GROUND_RB87_HZ`](../../rb5s6s/constants.py) and
[`constants.HFS_GROUND_RB85_HZ`](../../rb5s6s/constants.py), and the excited
$6S_{1/2}$ magnetic-dipole constants,
[`constants.A_6S_RB87_HZ`](../../rb5s6s/constants.py) and
[`constants.A_6S_RB85_HZ`](../../rb5s6s/constants.py), each carry a provenance
comment in that file, sourced to [Ayachitula and co-workers](../lit/ayachitula2024.md),
the kHz-precision remeasurement that replaced an earlier, less precise
determination for the excited-state constants.

![Fit gallery of the four hyperfine components](../../figures/fig16_fit_gallery.png)

*The brightest campaign trace of each of the four hyperfine components, fitted model and residuals, in one frame.*

[docs/plan/09_the-fixed-lock.md](../plan/09_the-fixed-lock.md) section 10c.5
uses the same-isotope pair separations as an in-trace frequency reference. A
same-isotope pair carries no isotope shift, so its separation on the
transition axis is the ground splitting minus the $6S_{1/2}$ splitting, and
both are constants this repository already holds, which is what makes the
separation usable as a ruler independent of the modulator, the piezo and the
wavemeter reading.

## What can go wrong

Comparing a labelled component against the wrong reference frequency reports
real physics as a residual error. Measuring each component against an
isotope-averaged centroid instead of the specific sublevel it names folds
hyperfine structure into what should be a pure calibration offset. Read
against the centroid, the four components disagree with the labels by a
spread of several gigahertz. Read against the component each label actually
names, the spread collapses by two orders of magnitude.
[`two_photon_frequency_hz`](../../rb5s6s/constants.py) implements the second
comparison.

Hyperfine splitting and isotope shift are two different effects and are easy
to run together when a trace holds components from both isotopes. Hyperfine
splitting comes from the nuclear moment within one isotope, isotope shift
from the mass and volume difference of the electronic centroid between
isotopes, and only a same-isotope separation is free of the second effect. A
cross-isotope separation carries both at once and needs the isotope shift
identified and subtracted before it can serve as anything but a rough check.

The interval-formula multiplier is a common arithmetic slip: the total
$J=1/2$ splitting is $A(I+1/2)$, which is $2A$ for 87Rb ($I=3/2$) and $3A$
for 85Rb ($I=5/2$), and using the wrong multiplier for a given isotope shifts
a predicted spacing without raising any error on its own.

The two halves of a transition are not equally well known. A ground-state
splitting is close to a defined quantity at present precision, while an
excited-state $A$ constant rests on one spectroscopic remeasurement. An
earlier determination was replaced by a newer one that moved the constant by
a few tenths of a megahertz, small next to the one-per-cent identification
tolerance but not small next to a kilohertz-level ruler use.

Finally, a different kind of trap: dropping the $(2F+1)$ weighting when
summing hyperfine shifts back to the unperturbed term energy silently breaks
the identity that the weighted sum must vanish.

## Try it

Both same-isotope pair separations on the two-photon transition axis, built
only from the constants module: the ground splitting minus the $6S_{1/2}$
splitting, where the $6S_{1/2}$ splitting is $2A$ for the $I=3/2$ isotope and
$3A$ for the $I=5/2$ one.

```python
from rb5s6s.constants import (
    HFS_GROUND_RB87_HZ, HFS_GROUND_RB85_HZ, A_6S_RB87_HZ, A_6S_RB85_HZ)

# Total 6S1/2 hyperfine splitting of a J=1/2 level is A*(I + 1/2):
# 2A for 87Rb (I=3/2), 3A for 85Rb (I=5/2).
splitting_6s_rb87_hz = 2.0 * A_6S_RB87_HZ
splitting_6s_rb85_hz = 3.0 * A_6S_RB85_HZ

pair_rb87_hz = HFS_GROUND_RB87_HZ - splitting_6s_rb87_hz
pair_rb85_hz = HFS_GROUND_RB85_HZ - splitting_6s_rb85_hz

print(f"87Rb same-isotope pair separation: {pair_rb87_hz / 1e6:.3f} MHz")
print(f"85Rb same-isotope pair separation: {pair_rb85_hz / 1e6:.3f} MHz")
print("neither value carries the 85-87 isotope shift, both are same-isotope")
```

## Further reading

- C. J. Foot, *Atomic Physics* (Oxford University Press, 2005), chapter 6,
  a standard graduate-level treatment of hyperfine structure and the interval
  formula used above.
- [Ayachitula and co-workers](../lit/ayachitula2024.md), the kHz-precision
  two-photon remeasurement this repository's excited-state constants come
  from.
- [Wikipedia: Hyperfine structure](https://en.wikipedia.org/wiki/Hyperfine_structure)
  for the general derivation and the electric-quadrupole term this page
  only summarises.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), the
  technique that resolves these components against their Doppler width.

## See also

- [Selection rules](selection-rules.md), for the angular-momentum rule
  this page extends from $J$ to $F$.
- [Magnetic sublevels](magnetic-sublevels.md), for the further splitting
  an applied field adds to each $F$ level.
- [Hyperfine populations and branching](hyperfine-populations-and-branching.md),
  for how atoms distribute among the sublevels this page describes.

---

[← Multiphoton transitions](multiphoton-transitions.md) · *Atomic structure and selection rules, 3 of 7* · [Magnetic sublevels →](magnetic-sublevels.md)
