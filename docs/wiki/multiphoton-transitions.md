# Multiphoton transitions

*[wiki index](README.md) · concept*

**The question.** How a transition a single photon's parity rule forbids
can still be driven by absorbing more than one photon, and what sets the
required photon count.
**Takes.** The one-photon parity and angular-momentum rules from
[Selection rules](selection-rules.md), nothing else assumed.
**Gives.** The virtual, non-resonant two-photon amplitude, its
intensity-squared scaling, and the polarisation-dependent tensor
decomposition that separates the Doppler-free line from its pedestal.
**Skip if.** the reader wants the one-photon parity argument on its own
rather than its extension to more than one photon, in which case
[Selection rules](selection-rules.md) is the right page.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A transition between two atomic states can be driven by absorbing more than
one photon at once, provided the photon energies sum to the energy gap
between the states. Which photon count actually reaches a given pair of
states is not a free choice. It is fixed by a structural constraint on the
interaction, and that constraint is parity.

In the electric-dipole approximation, each photon couples to the atom
through an operator that is odd under spatial inversion, the same operator
that gives an ordinary one-photon transition its Laporte parity rule.
Absorbing $N$ photons applies that odd operator $N$ times, and $N$ factors
of an odd sign combine to an overall sign of $(-1)^N$. A one-photon
transition connects states of OPPOSITE parity. A two-photon transition
connects states of the SAME parity, because the two flips cancel, which is
precisely why an S to S transition is drivable by two photons and not by
one: both S levels have the same, even parity, so a single photon cannot
join them and two of the same photon can. A three-photon transition flips
parity back to opposite, and the alternation continues with every photon
added.

The rate is not resonant with any single level lying between the initial
and final state. Perturbation theory writes a two-photon amplitude as a sum
over every intermediate state $n$ the atom could pass through virtually,

$$M_{fi} \propto \sum_n \frac{\langle f|\hat d \cdot \vec\epsilon_2|n\rangle\langle n|\hat d \cdot \vec\epsilon_1|i\rangle}{E_n - E_i - \hbar\omega_1}$$

and each term in the sum is weighted by how far the light sits from that
particular intermediate state's own one-photon resonance, the energy
denominator above. No population ever passes through a real intermediate
level. The sum runs over virtual paths and stays finite even when every
denominator is large, provided the total two-photon energy still matches
the gap between the initial and final state. States with the smallest
denominators, typically the nearest opposite-parity levels, dominate the
sum, though it runs in principle over the whole spectrum including the
continuum. For the two 993 nm photons this repository drives, no single
photon is anywhere near resonant with a real intermediate level, which is
what makes the process two-photon and virtual rather than a two-step,
population-passing cascade.

At low drive the two-photon rate scales with the square of the intensity,
since each of the two absorption steps contributes one power of the field to
the amplitude. What happens once the drive is no longer weak, where that
square law bends over, is the subject of [Saturation](saturation.md).

Because a two-photon step carries two polarisation vectors, $\vec\epsilon_1$
and $\vec\epsilon_2$, the operator driving the transition decomposes into
pieces of tensor rank zero, one and two: a scalar part built from the plain
dot product $\vec\epsilon_1\cdot\vec\epsilon_2$, a vector part built from
their cross product, and a rank-two tensor part. Which parts can act on a
given pair of levels is set by angular-momentum selection rules on each
piece's own rank, and for a transition between two S states that carries no
change in the total hyperfine quantum number, only the scalar and vector
parts survive. The consequence is published for this exact transition. The
scalar term, proportional to the degree of linear polarisation squared, is
what the two-photon rate reduces to, and it vanishes identically for two
photons of the same circular handedness, since two vectors of equal helicity
have a self dot product of zero. [Rajasree 2020](../lit/rajasree2020spin.md)
reports this law directly on the $5S_{1/2} \to 6S_{1/2}$ transition in warm
rubidium vapour, the rate following the squared degree of linear
polarisation and dropping to zero for circular light.

Adding a third photon flips the parity balance back. A three-photon
transition connects states of OPPOSITE parity, the same relation a single
photon obeys, so it can reach a level two photons cannot and the reverse of
what two photons alone permit. The rate follows the same construction one
step further: three factors of the field in the amplitude give a rate that
scales as the CUBE of the intensity rather than its square. Each extra
photon order also adds another off-resonant energy denominator to the
amplitude, so at a given available power the achievable rate falls sharply
as the photon count grows, and a process absorbing more photons responds
more strongly, fractionally, to any drift or noise in the driving
intensity than one absorbing fewer does.

## What problem it solves

Multiphoton absorption is what makes an otherwise Laporte-forbidden
transition observable at all, and it explains why the photon count matters
as much as the total energy supplied: reaching the same pair of levels with
a different number of photons is not just a different way to add up the
same energy, it engages a different parity channel and a different
angular-momentum structure in the coupling. The tensor decomposition turns
polarisation into a lever on that structure directly. Rather than inferring
after the fact, by fitting a lineshape, which part of a signal came from
which term, an experiment can switch a whole tensor component of the
coupling off at the source by choosing a polarisation combination, and read
the difference between settings as a separation made in hardware rather
than a modelling assumption.

## Where this repository uses it

The polarisation configurations of
[The fixed-lock instrument, section 10c.9](../plan/10_the-fixed-lock-instrument.md)
follow directly from the scalar-and-vector-only structure above. Parallel
linear polarisation is the standard configuration, with both the
Doppler-free line, driven by the cross term between the two
counter-propagating beams, and its broad pedestal, driven by the same-beam
terms, present together. Orthogonal linear polarisation kills the cross
term and leaves the pedestal alone, separating the line from its own
baseline by hardware rather than by a fitted baseline model, the same cross
term and same-beam term that
[Doppler-free geometries](doppler-free-geometries.md) derives from the
wavevector-cancellation condition rather than from polarisation. Circular
polarisation is not a third way of isolating one of
those two pieces. Because the whole coupling for this transition reduces to
the scalar term, and that term vanishes identically for two photons of the
same handedness, circular light removes the cross term and the same-beam
term together. It is an EXTINCTION NULL, useful for measuring whatever the
detector reports with the atoms switched off by polarisation alone, and not
a line-only or pedestal-only mode.

## What can go wrong

The clearest model failure is carrying a one-photon intuition about
polarisation into the two-photon case unchanged, expecting circular light
to remove the pedestal while leaving the line, or the reverse. It does
neither: since an S to S two-photon transition keeps only the scalar and
vector parts of the coupling, and both die together for two photons of the
same handedness, circular light is a null test on the whole transition
rather than a filter that separates the line from its pedestal the way
orthogonal linear polarisation does.

A near-null is easy to mistake for a perfect one, a data-insufficiency trap
rather than a model one. A polarisation optic set a few degrees off its
nominal angle leaves a small residual scalar term rather than an exact
zero, and if the residual signal sits below the detection floor the trace
looks identical to a true extinction. An extinction test on its own bounds
how close to circular the light was, it does not certify that the light was
exactly circular, and the bound is only as tight as the noise floor the
residual has to clear.

An implementation trap sits in which dot product is meant. The operator in
the two-photon amplitude is the plain, unconjugated
$\vec\epsilon_1\cdot\vec\epsilon_2$, not the conjugated
$\vec\epsilon_1\cdot\vec\epsilon_2^{*}$ that ordinary intensity-based
polarimetry reports. The two agree for real, linear vectors and diverge for
elliptical ones, so predicting where a null should sit from an instrument
reading the conjugated quantity, rather than from the polarisation state
itself, can place the predicted null at the wrong angle entirely.

Finally, an experimental limitation stated plainly. A real wave plate is
not an ideal one: its retardance is exact at one design wavelength and
drifts away from a quarter wave with wavelength and temperature, and any
birefringence elsewhere in the beam path, a window, a lens, a mirror
coating, adds its own small elliptical component on top. [The fixed-lock
instrument](../plan/10_the-fixed-lock-instrument.md) records that this
apparatus does not yet carry the insertable quarter-wave plates the
configuration needs at all, so for now the extinction null is a hardware
gap to close rather than a floor already measured on this bench.

## Try it

The scalar two-photon coupling, $\vec\epsilon_1\cdot\vec\epsilon_2$ with no
conjugate, for one fixed beam against a second beam whose polarisation is
set by a quarter-wave plate at a rotating angle. The rate falls to its
extinction null where the plate turns the fixed linear input circular.

```python
import numpy as np

def qwp_output(theta_rad, e_in):
    """Jones vector after a quarter-wave plate whose fast axis sits at
    theta_rad from the lab x axis, acting on the input Jones vector e_in."""
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    to_plate_frame = np.array([[c, s], [-s, c]])
    to_lab_frame = np.array([[c, -s], [s, c]])
    quarter_wave = np.diag([1.0, 1.0j])  # pi/2 retardance, fast vs slow axis
    return to_lab_frame @ (quarter_wave @ (to_plate_frame @ e_in))

e_fixed = np.array([1.0, 0.0], dtype=complex)  # the other beam, fixed linear

print("QWP angle (deg)   degree of linear pol.   two-photon rate")
for deg in (0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 90.0):
    e_rotated = qwp_output(np.deg2rad(deg), e_fixed)
    scalar_term = e_rotated[0] ** 2 + e_rotated[1] ** 2  # e.e, not |e|^2
    assert abs(scalar_term.imag) < 1e-9
    degree_linear = scalar_term.real                     # cos(2 * theta)
    rate = degree_linear ** 2
    print(f"{deg:6.1f}                 {degree_linear:+.4f}"
          f"                {rate:.4f}")

print("rate is null at 45 degrees: the quarter-wave plate has turned the "
      "fixed linear input into purely circular light there")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/bjorkholm1976.md`](../lit/bjorkholm1976.md), the sum-over-states
  theory of two-photon absorption strength the amplitude expression above
  follows.
- [Rajasree 2020](../lit/rajasree2020spin.md), the same-transition report of
  the polarisation law this page states above.
- G. Grynberg and B. Cagnac, "Doppler-free multiphotonic spectroscopy,"
  Reports on Progress in Physics 40, 791 (1977), the review that develops
  the scalar, vector and tensor decomposition of the two-photon operator
  used above.
- C. J. Foot, *Atomic Physics* (Oxford University Press, 2005), chapter 7,
  the electric-dipole selection rules and the parity rule the one-photon
  case rests on.
- [Selection rules](selection-rules.md), the one-photon parity and
  angular-momentum rules this page builds on and extends to more than one
  photon.
- [Saturation](saturation.md) for what the square law becomes once the
  drive is no longer weak.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md) for the
  beam geometry the cross and same-beam terms above belong to.
- [Doppler-free geometries](doppler-free-geometries.md) for the same cross
  and same-beam terms derived from wavevector cancellation rather than from
  polarisation.

## See also

- [Selection rules](selection-rules.md), the one-photon parity and
  angular-momentum rules this page extends to more than one photon.
- [Saturation](saturation.md), for what the intensity-squared law becomes
  once the drive is no longer weak.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), the
  beam geometry the cross and same-beam terms above belong to.

---

[← Selection rules](selection-rules.md) · *Atomic structure and selection rules, 2 of 6* · [Hyperfine structure →](hyperfine-structure.md)
