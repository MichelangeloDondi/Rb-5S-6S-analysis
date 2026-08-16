# Selection rules

*[wiki index](README.md) · concept*

## What it is

An atom couples to a light field through its charges, and the coupling is not
one term but a series. Expand the interaction in powers of $k \cdot r$, the
atom's own size $r$ measured against the light's wavevector $k = 2\pi/\lambda$,
and each successive term is a different multipole order. The leading term,
independent of $k \cdot r$, is the ELECTRIC DIPOLE (E1) interaction, the
electron's charge distribution coupling to the field as if it were a single
displaced point charge. The next term, one power of $k \cdot r$ smaller in
amplitude, splits into two pieces of the same order: the MAGNETIC DIPOLE (M1)
interaction, from the current the moving charge represents, and the ELECTRIC
QUADRUPOLE (E2) interaction, from the charge distribution's departure from a
point. Further terms, octupole and beyond, continue the same ladder, each one
power of $k \cdot r$ weaker again.

The dipole term dominates because $k \cdot r$ is tiny for an atom driven by
visible or near-infrared light. The atom's size is set by the Bohr radius, a
fraction of an angstrom, while the wavelength is hundreds of nanometers, so
$k a_0$ itself sits at roughly $10^{-3}$ to $10^{-4}$. Because a transition
RATE scales with the square of the coupling amplitude, each step up the
multipole ladder costs a factor of about $(k a_0)^2$ in rate relative to the
step before it, typically six to eight orders of magnitude. A transition the
dipole term cannot drive is therefore not impossible. It proceeds through the
next term at a correspondingly reduced rate, which is why it is called
FORBIDDEN rather than absent, a statement about its speed and not about
whether it happens at all.

Which multipole order actually connects two given states follows from two
properties only. The first is PARITY. Spatial inversion sends $r \to -r$, and
the electric dipole operator, linear in $r$, is odd under that operation. A
matrix element between states of definite parity vanishes unless the
operator's parity and the two states' parities multiply to an even result, so
an odd operator connects only states of OPPOSITE parity. Every E1 photon
absorbed or emitted changes the atom's parity.

The second property is ANGULAR MOMENTUM. A photon is a spin-1 particle and
carries at least one unit of angular momentum into or out of the atom, so the
atom's own angular momentum has to be able to absorb or supply that unit. For
a dipole photon, the simplest carrier, the total angular momentum $J$ can
change by $0$ or by $\pm 1$, with one exception: $J=0$ to $J=0$ is forbidden,
because a photon always carries at least one unit and a state with no angular
momentum to reorganise has nowhere for that unit to go.

Magnetic dipole and electric quadrupole radiation differ from electric dipole
on both counts. Both operators are EVEN under spatial inversion, the magnetic
dipole because it is built from orbital or spin angular momentum, unchanged
by $r \to -r$, and the electric quadrupole because it is quadratic in $r$ and
$(-r)(-r) = rr$. Both therefore connect states of the SAME parity, the
opposite of the dipole rule, which is how a dipole-forbidden transition can
still proceed. On angular momentum the two channels part ways: magnetic
dipole radiation carries the same single unit as electric dipole and obeys the
same $J$ rule, while electric quadrupole radiation is a rank-two operator and
can carry away up to two units, opening $J$ changes of $\pm 2$ that neither
dipole channel reaches, while still excluding $J=0$ to $J=0$, $J=0$ to $J=1$,
and $J=1/2$ to $J=1/2$, none of which a two-unit carrier can bridge either.

The nucleus enters through coupling, not through a rule of its own. [Hyperfine
structure](hyperfine-structure.md) describes how nuclear spin $I$ combines
with the electronic angular momentum $J$ to give the total angular momentum
$F$ a real spectral line is labelled by. The photon interacts with the
ELECTRONS, so every rule above is a statement about $J$ and about electronic
parity, not about $F$ directly. What holds for $F$ is the ordinary
angular-momentum addition of a fixed $I$ onto both sides of the $J$ rule: $F$
follows the same shape of rule $J$ does for a given multipole order, once $I$
is added consistently to the initial and final state, rather than obeying any
nuclear selection rule of its own.

## What problem it solves

Selection rules turn a spectrum's structure into something predictable before
any matrix element is computed. Given only the parity and the angular
momentum of two states, they say at a glance which multipole order connects
them, and therefore roughly how strong or how slow the transition will be,
without touching a radial wavefunction or a coupling constant. That
bookkeeping is also what makes a level METASTABLE: a state with no
dipole-allowed path down decays only through the far slower magnetic-dipole
or electric-quadrupole channel, if even those are open, and identifying which
states qualify needs nothing beyond parity and angular momentum. Because the
rules follow from symmetry rather than from any one atom's numbers, they
generalise instantly: the argument that forbids one atom's version of a
transition forbids every atom's.

## Where this repository uses it

The transition this repository measures connects $5S_{1/2}$ and $6S_{1/2}$,
an $l=0$ state to another $l=0$ state, and both therefore share the same,
even parity. Parity forbids any electric dipole photon from connecting them
directly, at any optical wavelength, because the mismatch is exact rather
than a matter of degree. The lowest process parity allows is two dipole
steps through a virtual, far-off-resonance $nP$ state, each step flipping
the parity, so the pair returns the atom to even parity exactly where
$6S_{1/2}$ sits. That is the entire reason this experiment absorbs two
photons rather than one, worked out mechanically in
[multiphoton-transitions.md](multiphoton-transitions.md). The repository's
own accounting of which multipole channels the parity argument still leaves
open for this line, and how far below the dominant amplitude they sit, is in
[THEORY_NOTE.md, section 5.1](../THEORY_NOTE.md).

The angular-momentum half of the rule shows up once the nucleus is added.
[Hyperfine structure](hyperfine-structure.md) sets out how nuclear spin $I$
couples to $J$ to give the four labelled components this experiment
resolves, and [`constants.PEAKS`](../../rb5s6s/constants.py) records every
one of them as an $F$ to $F'$ transition with $\Delta F = 0$, consistent
with the same angular-momentum bookkeeping applied to $F$ rather than to
$J$.

## What can go wrong

The first failure is treating a selection rule as a statement that a
transition never happens rather than as a statement about which order it
happens at. A forbidden line can still appear, faintly, through the next
multipole order, through a small parity- or angular-momentum-mixing
perturbation such as an external field, or through a nearby hyperfine level
borrowing amplitude from an allowed neighbour. Reading a weak, unexpected
feature at a formally forbidden frequency as evidence of a new mechanism,
rather than as the ordinary small leak the next-order channel or a mixing
perturbation predicts, is the model failure this page exists to head off.

The second is a data-insufficiency trap that can look like a clean answer. A
single spectrum cannot usually tell a genuine higher-multipole channel apart
from residual leakage of the nominally forbidden lower one, because both
leave the same signature, a faint line at the same frequency. Separating
them needs a lever the multipole order and the leakage mechanism respond to
differently, such as the dependence on an applied field, on polarization, or,
as in this repository's own two-photon case, on photon counting and energy
conservation rather than on intensity scaling alone.

The third is an implementation trap specific to a many-electron atom. Reading
a state's parity as $(-1)^l$ from the ORBITAL angular momentum of a single
active electron is safe for an alkali like the one this repository studies,
but it is not a general recipe: for a multi-electron configuration the
relevant parity is the sum over every electron's $l$, and using the total
electronic angular momentum $J$ in place of the orbital quantum number $l$
when checking parity silently gives the wrong answer wherever the two
disagree.

The fourth is an experimental limitation rather than an approximation error.
The rules above hold for the free-atom multipole operators to all orders. An
external field strong enough to mix opposite-parity states, well above
anything this apparatus applies but not above every atomic experiment, can
partially unlock a parity-forbidden channel that the field-free rule calls
exact, which is why any strict use of these rules should note, if only in
passing, that no such field is present.

## Try it

The suppression one extra step up the multipole ladder costs, for a
hydrogen-like atom probed at a representative optical wavelength.

```python
import math
import scipy.constants as sc

a0_m = sc.physical_constants["Bohr radius"][0]
alpha_fs = sc.physical_constants["fine-structure constant"][0]

# A generic hydrogen-like atom, probed at a representative optical
# wavelength, far from any near-resonant intermediate state.
wavelength_m = 500e-9
k_per_m = 2.0 * math.pi / wavelength_m

ka0 = k_per_m * a0_m
rate_ratio = ka0 ** 2

print(f"Bohr radius a0 = {a0_m * 1e12:.1f} pm, wavelength = {wavelength_m * 1e9:.0f} nm")
print(f"multipole expansion parameter k*a0 = {ka0:.2e}")
print(f"electric quadrupole rate / electric dipole rate ~ (k*a0)^2 = {rate_ratio:.2e}")
print(f"for comparison, the fine-structure constant squared alpha^2 = {alpha_fs**2:.2e}")
print("a forbidden line is weaker by many orders of magnitude, not absent")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- C. J. Foot, *Atomic Physics* (Oxford University Press, 2005), chapter 7,
  the interaction of atoms with radiation and the multipole expansion these
  rules come from.
- [Wikipedia: Selection rule](https://en.wikipedia.org/wiki/Selection_rule)
  for the general classification this page summarises.
- [Multiphoton transitions](multiphoton-transitions.md) for the mechanism a
  parity-forbidden line actually proceeds through.
- [Hyperfine structure](hyperfine-structure.md) for how nuclear spin
  combines with the electronic angular momentum these rules constrain.

---

[← wiki index](README.md) · *Atomic structure and selection rules, 1 of 6* · [Multiphoton transitions →](multiphoton-transitions.md)
