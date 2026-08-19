# Magnetic sublevels

*[wiki index](README.md) · concept*

**The question.** What the $2F+1$ magnetic sublevels of a level are, and
when averaging over them versus resolving one individually changes what a
measurement reports.
**Takes.** The $F$ levels [Hyperfine structure](hyperfine-structure.md)
builds, nothing else assumed beyond that.
**Gives.** The Zeeman splitting per sublevel and the scalar, vector and
tensor decomposition of the light shift across them.
**Skip if.** the reader wants the $F$ levels themselves rather than the
$m_F$ structure inside each one, in which case
[Hyperfine structure](hyperfine-structure.md) is the right page.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A level of total angular momentum $F$ is not one state but $2F+1$ of them,
labelled by the projection $m_F$, running in integer steps from $-F$ to $F$.
In zero external field every one of these MAGNETIC SUBLEVELS carries the
same energy: nothing in the level's internal structure picks out a
direction, so nothing separates them. A magnetic field breaks that symmetry.
Coupling to the field through the level's magnetic moment, each sublevel
shifts by an amount proportional to $m_F$, to leading order
$\Delta E(m_F) = g_F \mu_B B m_F$, with $\mu_B$ the Bohr magneton and $g_F$
the level's own g-factor, the ZEEMAN EFFECT. The adjacent-sublevel spacing
$g_F \mu_B B$ is set entirely by $g_F$, so two levels sitting at the same
energy in zero field can respond completely differently once a field is
applied, and the size of that response is itself built from how the
electronic and nuclear angular momenta compose to make $F$ in the first
place, the subject of [hyperfine structure](hyperfine-structure.md).

That internal structure has a direct consequence for what an ordinary
measurement reports. In an unpolarised sample, with no field defining a
preferred direction and no process favouring one sublevel over another, the
$2F+1$ sublevels sit at equal population, weighted only by their own
degeneracy. Whatever a bulk measurement reads off, a rate, a shift, a line
strength, is an average over that whole manifold, not the property of any
one sublevel. Give the sample a defined quantisation axis, an applied field
of known direction, and a way to prepare or select a single $m_F$, optical
pumping or state-selective detection, and the average collapses into one
specific number that belongs to that sublevel alone.

The light shift is where this distinction stops being bookkeeping. The
AC-Stark shift of a level under off-resonant light separates into three
pieces by tensor rank. The SCALAR part is the same for every sublevel: it
has no $m_F$ dependence and no sensitivity to the light's polarisation
state, so it is what survives any averaging. The VECTOR part depends
linearly on $m_F$ and on the light's degree of circular polarisation, acting
like a fictitious magnetic field pointed along the light's propagation
direction, and it vanishes for purely linearly polarised light regardless of
$m_F$. The TENSOR part depends quadratically on $m_F$, through a factor
proportional to $3m_F^2-F(F+1)$, and it needs the level's own angular
momentum to be at least one: a rank-2 operator cannot be built from an
angular momentum of $1/2$, so it is identically absent for any such level no
matter how the light is polarised. In an unpolarised, unprepared sample the
vector and tensor pieces average to zero across the equally populated
sublevels and only the scalar part survives, which is why a bulk
measurement can report a single polarizability. In a trapped, field-defined,
state-prepared sample none of that averaging happens, and the vector and
tensor pieces become quantities in their own right rather than a
correction folded into one number.

## What problem it solves

It draws the line between when "the $F$ level" is a sufficient description
and when the finer structure inside it has to be tracked. It also explains
why a light shift that looks like an unavoidable, single-number systematic
in one kind of sample turns into several independently informative
quantities in another: the scalar part is a background to subtract, while
the vector part reports on the light's circular character and the tensor
part reports on the level's own angular structure, both otherwise
invisible.

## Where this repository uses it

This repository's two levels, $5S_{1/2}$ and $6S_{1/2}$, are both $J=1/2$,
so their tensor light shift does not exist to find, at either wavelength
and under any polarisation, the same triangle rule stated for the
magic-wavelength crossings in
[BIG_PICTURE, why this line](../big_picture/01_why-this-line.md). The
vector part is not forbidden for either level, only switched off by the
apparatus itself:
[the optics protocol](../plan/03_optics-protocol.md) fixes the precision
path at one shared linear polarisation axis, under which the two-photon
line is $m_F$-blind by construction and the vector channel is brought in
only as an optional circular diagnostic, off that precision path. Between
the two, [`rb5s6s/polarizability.py`](../../rb5s6s/polarizability.py)
computes a single scalar polarizability for each level (`alpha_5s`,
`alpha_6s`, `delta_alpha`), and that is not a simplification of convenience,
it is the whole content a $J=1/2$ pair under linear light has to give.

The degeneracy weighting this page opens with is exactly what predicts the
four measured line strengths.
[`rb5s6s/amplitudes.py`](../../rb5s6s/amplitudes.py) derives each peak's
relative area from abundance times $(2F+1)$ over the isotope's total
ground-sublevel count, 8 for $^{87}\text{Rb}$ and 12 for $^{85}\text{Rb}$
(the same $F$ values [`constants.PEAKS`](../../rb5s6s/constants.py)
carries), with no preference for any one $m_F$ built in anywhere, a
prediction that only holds because the driving operator is scalar in the
first place.

What a defined quantisation axis and a prepared sublevel can buy is not
speculative. [Duspayev and Raithel](../lit/duspayev2023.md) trap
$^{85}\text{Rb}$ in an optical lattice and resolve a $J=3/2$ level's magic wavelength
splitting by $m_J$, a tensor effect with nothing analogous available to a
$J=1/2$ pair in a warm cell. The residual this repository's own record
still carries once the tensor and vector channels are both closed off is a
shift proportional to $\Delta g_J$ alone, at the sub-kilohertz-per-gauss
level ([the optics protocol](../plan/03_optics-protocol.md)), small enough
that no field-dependent term appears in any fitted model here.

## An S-to-S two-photon line is magnetically quiet, twice over

The 5S to 6S line is protected against a laboratory field by two independent
cancellations, and the numbers are worth carrying because they say when the
protection runs out.

FIRST ORDER. With identical linear photons the two-photon operator is
scalar, driving $m_F$ to the same $m_F$, so a component shifts by
$m_F (g_F^{6S} - g_F^{5S}) \mu_B B$. Both states are $S_{1/2}$ with the
same hyperfine structure: the nuclear part of $g_F$ cancels exactly, and the
electronic $g_J$ difference between the two S states is a core correction of
order $10^{-4}$, leaving under 140 Hz of spread at the Earth's 50 uT against
a line millions of hertz wide.

SECOND ORDER. The Breit-Rabi quadratic term scales as
$(g_J \mu_B B)^2 / \Delta_\text{hf}$, under 3 kHz per state at Earth field.
The LINE barely moves, but a hyperfine PAIR SEPARATION inherits the
difference of two such terms, near one to two kHz, which matters exactly
once in this record's plans, at the coincidence block that reads the 6S
splitting to a few hundred hertz.

WHERE THE PROTECTION ENDS. The scalar selection assumes linear polarisation.
A circular admixture opens the rank-1 vector light shift, odd in $m_F$ with
its axis set by the ambient field, and the same admixture pumps orientation,
so an imperfectly polarised beam acquires a power-dependent line asymmetry
that REVERSES when the field reverses. The reversal is the diagnostic: a
coil on the cell turns the one magnetic effect this line can show into a
switchable signature.

## What can go wrong

The first failure is a model one: reading a population-averaged
measurement as if it described one sublevel, or the opposite mistake,
concluding a sublevel-dependent effect is absent because an unresolved
measurement washed it out. Averaging over $2F+1$ equally weighted
sublevels is a description of what the measurement did, not evidence about
what any one sublevel would show.

The second is an apparatus limitation dressed as a result. Without an
applied field of known, stable direction, $m_F$ is not a meaningful label
at all, an ambient stray field of unspecified and drifting orientation does
not define a quantisation axis, it only adds a small, uncontrolled scatter
on top of the degeneracy-weighted average that was already there. Calling
that scatter a measured vector or tensor shift claims more than an
unprepared sample supports.

The third is an implementation trap: writing the Lande g-factor formula
with the fine-structure quantum number $J$ where the hyperfine one $F$
belongs, or the reverse. The two formulas share the same shape and differ
only in which angular momenta enter, so the wrong one returns a plausible
number for the wrong level and raises no error on its own, the same class
of slip [hyperfine structure](hyperfine-structure.md) flags for the
interval-formula multiplier.

The fourth is an experimental limitation, not a fixable oversight. State
preparation only converts the vector or tensor channel into a measurable
quantity if the level carries that rank to begin with. For a pair of
$J=1/2$ levels the tensor channel is not merely small or hard to resolve,
it does not exist, so no trap, no field and no state preparation manufacture
one. That is why this record's own magic-wavelength search stays scalar by
right rather than by an unexamined omission.

## Try it

The $2F+1$ degeneracies and the linear Zeeman splitting per unit field for
the two ground hyperfine levels of one isotope, with the $F$ values read
from this repository's own `PEAKS` table rather than typed from memory.

```python
from rb5s6s.constants import PEAKS, H_PLANCK_JS

# Bohr magneton, CODATA 2018 (a universal constant, not a repository number).
MU_B_J_PER_T = 9.274_010_078_3e-24

# Lande g_J of an L=0 (S-state) level is, to leading order, the free-electron
# spin g-factor: a J=1/2 alkali ground state measures within 0.01% of it, and
# the (much smaller) nuclear contribution is dropped here.
G_J_S_STATE = 2.002_319_304_4


def ground_state_f_values(isotope):
    """The two ground F values this repository's own hyperfine components
    name (PEAKS), read rather than typed from memory."""
    return sorted({p["F"] for p in PEAKS.values() if p["isotope"] == isotope})


def lande_g_f(F, I, J=0.5):
    """Fine-structure-only Lande g_F for a hyperfine level F built from J and I."""
    return G_J_S_STATE * (F * (F + 1) + J * (J + 1) - I * (I + 1)) / (2 * F * (F + 1))


isotope = 87
f_lo, f_hi = ground_state_f_values(isotope)
nuclear_spin_i = f_hi - 0.5  # F_max = I + J, J = 1/2 for an S1/2 level

print(f"{isotope}Rb 5S1/2 ground state, I = {nuclear_spin_i:.1f}, "
      f"from the F values PEAKS already names:")
for F in (f_lo, f_hi):
    degeneracy = int(2 * F + 1)
    g_f = lande_g_f(F, nuclear_spin_i)
    hz_per_tesla = g_f * MU_B_J_PER_T / H_PLANCK_JS
    mhz_per_gauss = hz_per_tesla * 1e-4 / 1e6
    print(f"  F={F}: {degeneracy} sublevels (m_F = {-F:g}..{F:g}), "
          f"g_F = {g_f:+.3f}, Zeeman splitting {mhz_per_gauss:+.4f} MHz/G per unit m_F")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/steck_rb.md`](../lit/steck_rb.md), the standard compilation of Rb
  atomic-structure constants against which this repository's own numbers are
  checked, and the usual source for the Lande g-factor and Zeeman-splitting
  formulas used above.
- C. Cohen-Tannoudji, J. Dupont-Roc and G. Grynberg, *Atom-Photon
  Interactions: Basic Processes and Applications* (Wiley, 1998), the standard
  graduate treatment of the scalar, vector and tensor light-shift operators
  for a degenerate atomic level.
- [Duspayev and Raithel](../lit/duspayev2023.md), a trapped, cold-atom
  measurement whose tensor polarizability visibly splits a magic-wavelength
  condition by $m_J$, the kind of result a $J=1/2$ pair in a warm cell
  cannot produce.
- [Hyperfine structure](hyperfine-structure.md), for the $F$ levels a field
  splits further.
- [The AC-Stark shift](ac-stark-shift.md), for the scalar shift a warm cell
  actually measures and the beam geometry that turns it into a lineshape.

## See also

- [Hyperfine structure](hyperfine-structure.md), the $F$ levels this
  page's sublevels sit inside.
- [Hyperfine populations and branching](hyperfine-populations-and-branching.md),
  for how atoms distribute among the sublevels this page describes.
- [Selection rules](selection-rules.md), for the angular-momentum rule
  that fixes which $J$ combines with nuclear spin to build each $F$.

---

[← Hyperfine structure](hyperfine-structure.md) · *Atomic structure and selection rules, 4 of 7* · [Hyperfine populations and branching →](hyperfine-populations-and-branching.md)
