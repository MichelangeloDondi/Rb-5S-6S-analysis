# Doppler-free geometries

*[wiki index](README.md) · concept*

**The question.** Which beam geometries cancel the first-order Doppler shift
for every atom at once, and which only appear to.
**Takes.** A wavevector and a velocity. No fitting, no data.
**Gives.** The summing rule for multiphoton shifts, the two-photon
counter-propagating case, why three equal-colour photons cannot close
collinearly, and the harmonic pair that can.
**Skip if.** You want the frequency axis rather than the geometry. That is
[the wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md) defines
> every term and symbol used anywhere in this repository.

## What it is

An atom moving with velocity $\vec v$ sees a photon of wavevector $\vec k$
shifted, to first order in $v/c$, by an amount proportional to the dot
product $\vec k \cdot \vec v$. That single fact is the whole content of the
Doppler effect in spectroscopy, and it stays true no matter how many photons a transition
absorbs at once. When several photons are absorbed together, each one
contributes its own wavevector to the resonance condition, and the total
first-order Doppler shift is proportional to the sum of those wavevectors
dotted into the atom's velocity, $\big(\sum_i \vec k_i\big)\cdot \vec v$. It
is that sum, not any individual photon's shift, that a multiphoton resonance
actually sees. The shift therefore vanishes for every atom, whatever its
velocity, exactly when the absorbed wavevectors sum to zero,

$$\sum_i \vec k_i = 0.$$

This is a statement about the geometry of the beams the atom sits in, and it
holds for the whole velocity distribution at once rather than for one part
of it.

For two photons of the same colour taken from counter-propagating beams,
$\vec k_1=-\vec k_2$ by construction, and the sum is exactly zero for every
atom in the ensemble. It is worth stating plainly why that matters: this is
a cancellation for all atoms, not a selection of a favourable few. Contrast
it with saturated-absorption spectroscopy, where a strong pump beam and a
weak probe beam counter-propagate through the same single-photon transition
and only the narrow slice of the population whose velocity along the beam
happens to sit near zero is simultaneously resonant with both, so the narrow
feature there is carved out of the broad background by throwing away
everything else. A retro-reflected two-photon geometry needs no such
selection: every atom, at every velocity, contributes its cancelled shift to
the same narrow line, which is what makes the whole thermal population count
toward the signal rather than only a sliver of it.

Two qualifications keep the cancellation honest. It is exact only to first
order in $v/c$, and a second-order, relativistic term proportional to
$(v/c)^2$ survives and does not cancel, small at ordinary vapour-cell speeds
but present in principle. And the same two beams that cancel a cross pair
also, unavoidably, drive a second process: an atom can take both photons
from the same beam rather than one from each. That same-direction pair is
not cancelled at all, since its wavevector sum is $2\vec k$ rather than
zero, and the ensemble of atoms taking it produces a broad Doppler-broadened
pedestal sitting directly underneath the sharp cancelled line. Both
processes are driven by the same two beams and neither can be switched off
without the other, so the pedestal is a fixed companion of the technique
rather than an avoidable flaw in it.

Then the three-photon case. Suppose three photons of the same colour are
absorbed together. Their wavevectors all share one magnitude $k$, and the
condition $\vec k_1+\vec k_2+\vec k_3=0$ with equal magnitudes
$|\vec k_1|=|\vec k_2|=|\vec k_3|=k$ has a solution, but only one shape: three
vectors of equal length summing to zero must close a triangle, and the only
triangle with three equal sides is equilateral, which forces the three
vectors apart by 120 degrees in a plane. There is no way to satisfy that
condition with three equal-length vectors lying along one line. Closing the
triangle needs a genuinely non-collinear, three-beam geometry.

That geometric fact costs more than it looks like it should. Three beams
crossing at wide angles overlap only inside a small shared volume, unlike a
beam retro-reflected onto itself, where the forward and backward beams fill
exactly the same volume by construction, so the interaction region, and
with it the achievable signal, collapses relative to the two-photon case. A
three-photon rate is already a high power of the intensity, so a smaller
interaction volume does not merely cost signal, it costs signal against a
process that was already weak. Alignment and wavefront quality now have to
be held in three directions simultaneously instead of one, since each of
the three crossing beams brings its own pointing and wavefront error into
the shared overlap region. And any collinear compromise, such as sending two
photons one way along a single axis and the third photon the other way,
leaves a residual wavevector $\vec k_1+\vec k_2+\vec k_3=\pm\vec k$, the same
order as a single uncancelled photon, so the residual Doppler width stays a
large fraction of the width the transition would show with no cancellation
attempted at all, and the geometry buys nothing worth having.

The collinear three-photon case, which the equal-colour argument above hides.
Everything above assumed three photons of the same colour. Drop that and the
triangle is free to degenerate into a line, because a closing polygon with
unequal side lengths can be flat. The case that matters is
$\vec k+\vec k-2\vec k=0$: two photons of frequency $\omega$ taken from one
beam, and one photon of frequency $2\omega$ taken from a beam pointing the
other way. The magnitudes are $k$, $k$ and $2k$, the third opposes the first
two, and the sum vanishes exactly. The transition sits at $4\omega$, and the
cancellation is again exact for every atom whatever its velocity, not for a
selected class.

What makes this better than a coincidence is where the ratio comes from. A
closure that needed two independently tuned lasers to hold a $2:1$ frequency
ratio would drift out of it, and the residual wavevector would grow with the
mismatch. Here the second beam is naturally the second harmonic of the first,
produced by doubling it, so the ratio is fixed by the harmonic generation
rather than by tuning. If the fundamental drifts, the harmonic drifts with it
and the closure is preserved, which makes the arrangement robust in exactly
the place a two-colour scheme would normally be fragile.

What it still costs. A doubling stage and the power that leaves in it. Two
colours to overlap and focus together, whose diffraction and optics differ.
The transition must lie at four times the fundamental with the parity a
three-photon process reaches, which is a constraint on the level scheme rather
than on the geometry. And the rate is still third order in the intensity, so
the signal problem that motivates a Doppler-free scheme in the first place
does not go away.

The general statement is therefore about magnitudes rather than about photon
number. A collinear closure exists whenever the wavevector magnitudes can be
signed to cancel along one axis, which for equal colours needs an even count
and for unequal colours needs one side to equal the sum of the others. Equal
colours at odd photon number is the case with no collinear solution, and that
is what forces the crossing-beam geometry above.

The rule this page exists to state: a Doppler-free multiphoton geometry needs
its wavevectors to close, $\sum_i \vec k_i=0$, and the cost of closing them
depends on whether they can close flat. Two equal wavevectors close
collinearly, a single beam retro-reflected onto itself, which is why the
two-photon case keeps its full spatial overlap for free. Three equal
wavevectors cannot close flat, so they demand crossing beams and spend the
interaction volume, the alignment tolerance and the signal. Three unequal
wavevectors can close flat when one balances the other two, which the
fundamental and its second harmonic do exactly, so the crossing-beam cost is
avoidable at odd photon number provided the colours are chosen to make the
polygon degenerate.

## What problem it solves

It answers the geometric question sitting underneath every Doppler-cancelling
scheme: given a set of photons and their colours, which beam arrangement, if
any, cancels the first-order Doppler shift for the whole thermal ensemble
rather than for one velocity class. Stated this generally, it also explains
why the two-photon case is the practical sweet spot rather than an arbitrary
starting point: it is the lowest order at which the Doppler-cancelling
geometry and the fully-overlapping geometry coincide, and it reaches that
coincidence with one colour. Higher orders can also be made collinear, but
only by choosing the colours so the wavevectors cancel along a line, which
buys the overlap back and costs a second beam at a different frequency.

## Where this repository uses it

The whole measurement rests on the two-photon instance of this rule: one
beam retro-reflected through the vapour cell, so every atom sees a forward
and a backward photon of the same colour and the two-sided polygon closes
trivially. [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md)
works out that cancellation for this apparatus in detail, and
[standing waves](standing-waves.md) works out what the same retro-reflected
geometry does to the same-direction pairs that are not cancelled.

The Doppler pedestal that geometry produces is treated as a designed
observable rather than a nuisance to be modelled away.
[The fixed-lock instrument, section 10c.7](../plan/10_the-fixed-lock-instrument.md)
sets out what a wide enough scan reads from that pedestal once it is
visible, a consistency check on the atoms actually being probed rather than
a density axis.

No committed measurement in this repository drives a three-or-more-photon
geometry, but the repository's own forward planning has already run into
both halves of the three-photon argument above for a proposed future line.
[`docs/FUTURE_TRANSITIONS_titsapph.md`, section 3.5](../FUTURE_TRANSITIONS_titsapph.md)
considers a one-colour three-photon transition out of $5S_{1/2}$, for which
the equal-magnitude case above applies exactly: a collinear geometry leaves
a residual far too broad for the natural linewidths involved, so the
proposal turns to a STAR geometry of three coplanar beams at 120 degrees.
Its two other absorption channels there, two photons from one beam and one
from another rather than one from each, leave residual wavevectors of
$\sqrt3 k$ and $3k$, the three-beam analogue of the same-beam pedestal
described above for the two-photon case. The same document also runs into
the narrow different-colour exception this page names: two photons of one
colour against a third, doubled-frequency photon the other way closes
collinearly, $\vec k+\vec k-2\vec k=0$, with no crossing beams needed at
all, though that particular combination is ruled out there on energy
grounds rather than on geometry.

## What can go wrong

The first failure is treating the two-photon cancellation as if it selected
a velocity class the way saturated absorption does, rather than cancelling
the shift across the whole ensemble. The two techniques narrow a line by
different mechanisms, and confusing them produces the wrong expectation for
how the signal should scale with vapour density or cell length, since a
selection method throws away population that a cancellation method keeps.

The second is forgetting the residual. The first-order cancellation is
exact, but only to first order, and treating a two-photon line as carrying
no Doppler contribution whatsoever, rather than none to first order,
overstates the geometry's reach at extreme precision.

The third is a design trap rather than a modelling one: assuming a
multiphoton scheme with more photons automatically buys more resolution or
more signal for the same work. Going from two photons to three does not
add a photon onto an existing collinear beam. It forces a non-collinear
geometry that spends the very overlap that made the two-photon signal
strong, and a design that has not budgeted for that exchange will find the
interaction volume, not the atom, setting the achievable signal.

The fourth is assuming any collinear arrangement of more than two photons is
Doppler-free because it superficially resembles the two-photon geometry. Two
photons one way and one the other along a single axis is still collinear
and easy to build, but for equal-colour photons it does not sit on the
cancelling polygon, and its residual width is the same order as an ordinary
single-photon Doppler width rather than a small correction to a narrow line.

## Try it

The first-order Doppler width of a multiphoton resonance, computed by summing
signed wavevectors rather than counting photons, which is what lets the
two-colour case be expressed at all.

```python
import math

from rb5s6s.constants import K_B_J_PER_K, LAMBDA_LASER_M, M_RB87_KG

T_K = 403.15  # K, the reference cell temperature used elsewhere in this record
v_sigma = math.sqrt(K_B_J_PER_K * T_K / M_RB87_KG)  # 1D thermal speed
k_fund = 2.0 * math.pi / LAMBDA_LASER_M             # the fundamental wavevector


def doppler_fwhm_hz(signed_k_in_units_of_fundamental):
    """FWHM from the NET wavevector, the signed sum along the beam axis.

    Each entry is a photon's wavevector magnitude in units of the fundamental,
    signed by the direction it travels. Photon COUNT is not enough: a harmonic
    photon carries twice the wavevector of the fundamental it came from.
    """
    net = abs(sum(signed_k_in_units_of_fundamental))
    return net * k_fund * math.sqrt(8.0 * math.log(2.0)) * v_sigma / (2.0 * math.pi)


cases = [
    ("single photon",                              [+1]),
    ("two counter-propagating, one colour",        [+1, -1]),
    ("three collinear, one colour, all one way",   [+1, +1, +1]),
    ("three collinear, one colour, two and one",   [+1, +1, -1]),
    ("three collinear, harmonic: k + k - 2k",      [+1, +1, -2]),
]
for label, ks in cases:
    print(f"{label:<44}{doppler_fwhm_hz(ks) / 1e6:8.1f} MHz")
print()
print("Only the closures summing to zero cancel, and the harmonic case does it")
print("collinearly, which the equal-colour argument cannot reach at odd order.")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## A tilt coefficient that counted the same wavevector twice, 2026-08-15

On 2026-08-15 the residual Doppler width expected from a tilted retro-reflector
was budgeted from the co-propagating pedestal's own
coefficient. That pedestal is the same-beam pair this page describes above,
two photons taken from one beam, whose wavevector sum is $2\vec k$, not
$\vec k$. A retro tilted by angle $\theta$ instead drives a cross pair, one
photon from each of the two nearly-antiparallel beams, whose sum is
$|\vec k_1+\vec k_2| = 2k\sin(\theta/2) \approx k\theta$, half the pedestal's
coefficient because the pedestal already carries the doubled wavevector. The
budget was recomputed at 471 MHz per radian rather than 942, which loosened
the tilt tolerance by about a factor of two. Both tolerances, the first and
the corrected one, are in [docs/HISTORY.md](../HISTORY.md), which is the one
place this repository licenses a replaced number to appear.

The rule stated above, that a multiphoton shift comes from summing signed
wavevectors rather than counting photons, is exactly what this error skipped.
Writing out $\sum_i \vec k_i$ for the two pairs separately, rather than
carrying one coefficient across from a different pair by resemblance, would
have shown the factor of two before it reached a design document.

## Further reading

- G. Grynberg and B. Cagnac, Rep. Prog. Phys. 40, 791 (1977), the general
  $\sum_i \vec k_i \cdot \vec v = 0$ theory of Doppler-free multiphoton
  spectroscopy this page summarises.
- I. I. Ryabtsev and co-workers, Phys. Rev. A 84, 053409 (2011), which
  proposes the three-beam star geometry for a non-collinear three-photon
  excitation.
- [`../lit/biraben1974.md`](../lit/biraben1974.md), the founding experimental
  demonstration of the two-photon case this page generalises from.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), the
  two-photon instance of the rule stated here, worked out for this
  apparatus.
- [Standing waves](standing-waves.md), for what the same retro-reflected
  geometry does to the uncancelled same-direction pairs.

## See also

- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), the
  two-photon instance of the geometry rule stated here, worked out in full
  for this apparatus.
- [Standing waves](standing-waves.md), what the same retro-reflected
  geometry does to the uncancelled same-direction pairs sitting under the
  cancelled line.
- [Multiphoton transitions](multiphoton-transitions.md), the broader
  multiphoton framework this geometry rule sits inside.

---

[← The cascade and F-depletion](the-cascade-and-f-depletion.md) · *Atomic structure and selection rules, 7 of 7* · [wiki index →](README.md)
