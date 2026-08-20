# The cascade and F-depletion

*[wiki index](README.md) · concept*

**The question.** Why an observed line amplitude is not its transition
strength, and what the de-excitation cascade does to the ground state it
returns the atom to.
**Takes.** A driven hyperfine level, a cascade, and a transit time.
**Gives.** The ground-level populations under repeated excitation, the
depletion that reduces an observed amplitude, and the reason the four lines
of this experiment deplete at different rates.
**Skip if.** The question is which lines exist and how strong they are in the
first place, which is
[hyperfine populations and branching](hyperfine-populations-and-branching.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A two-photon transition drives an atom out of one ground hyperfine level. The
atom does not stay excited: it decays through a cascade, and **the hyperfine
quantum number F is not preserved along the way**. It can therefore arrive in
the OTHER ground hyperfine level, which is thousands of linewidths away from
the drive and no longer resonant.

That atom is gone from the measurement. It is still in the beam, still
contributing to the density, and no longer contributing to the line. Repeat
this while the atom crosses the beam and the observed amplitude falls below
what the transition strength alone would predict.

The quantity that governs it is the **cascade branching** $f$: the probability
that one excitation-and-decay cycle ends in the undriven level.

## The population model

Each cycle removes a fraction $f$ of what remains in the driven level, so the
surviving population after $n$ cycles is geometric,

$$p_{\text{driven}}(n) = (1 - f p_{\text{exc}})^n,$$

with $p_{\text{exc}}$ the excitation probability per cycle. The two ground
levels always sum to one, which is the invariant any implementation of this
must satisfy and which is worth testing rather than trusting.

The detector integrates over the crossing, so what an amplitude actually sees
is the TRANSIT AVERAGE of that curve rather than its endpoint. An atom that
has just entered the beam contributes fully, and one about to leave may contribute
very little.

With repumping light present the level relaxes toward $r/(f+r)$ instead of
toward zero, where $r$ is the return rate per cycle. This experiment has no
repumping, so the unrepumped limit is the one that applies, and the driven
level empties monotonically.

## Why the four lines differ, and why it is not the degeneracy weight

The branching is NOT the naive degeneracy weight of the destination level.
Selection rules block specific paths: an atom in $5P_{3/2}$ $F=0$ of
$^{87}\text{Rb}$ cannot reach the $F=2$ ground level at all, because a $J=1$ photon
cannot connect $F=0$ to $F=2$. That block sits in the arithmetic as an exact
zero, and the leg totals come out at the naive weight times $8/9$ and $4/9$
rather than at the weight itself.

Computed on the full Zeeman manifold, with every Clebsch-Gordan coefficient
and every intermediate hyperfine level present, the four lines of this
experiment give

| line | isotope, driven F | branching $f$ |
|---|---|---|
| 993.4121 | $^{87}\text{Rb}$, $F=1$ | 0.3725 |
| 993.4154 | $^{85}\text{Rb}$, $F=2$ | 0.3476 |
| 993.4192 | $^{85}\text{Rb}$, $F=3$ | 0.2483 |
| 993.4207 | $^{87}\text{Rb}$, $F=2$ | 0.2235 |

So 993.4121 loses population fastest and 993.4207 slowest, a spread of
roughly 1.7 between the extremes. **That ordering is a prediction about
relative amplitudes**, and it is a different ordering from the one the
observed amplitude departure follows, which is what makes the comparison
informative rather than circular.

## Why populations suffice, and what would break that

This is a rate model over populations, not a density-matrix solve, and the
justification is specific rather than conventional. The two-photon operator
for two identical linearly polarised photons is a SCALAR, since rank 2 cannot
connect $J = 1/2$ to $J = 1/2$ and rank 1 is absent for identical photons. A
scalar drives $m_F$ to the same $m_F$ at a rate independent of $m_F$, so it
creates no Zeeman coherence, and spontaneous emission redistributes $m_F$
incoherently. Populations therefore close among themselves.

Three things would break that and require the full Lindblad equation: a stray
magnetic field lifting the degeneracy during the transit, any ellipticity in
the drive, or a treatment of the standing wave that resolves its polarisation
structure. None is present in the model of record, and each is a reason to
revisit.

## What can go wrong

**Reading a branching as a degeneracy weight.** The blocked paths are the
whole point, and the naive weight is wrong by factors of $8/9$ and $4/9$ on
the two legs.

**Assuming the intermediate levels are populated statistically.** They are
not, and an earlier version of this calculation made exactly that assumption
before it was corrected.

**Forgetting that the observable is a transit average.** The endpoint
survival can be much smaller than what the amplitude sees, and using it
overstates the depletion.

**Attributing an amplitude change to depletion without checking the
alternative.** Depletion, saturation broadening and the AC-Stark shift all
grow with power. They are separated by their different power laws, not by
inspection, which is what
[saturation](saturation.md) and the acquisition chapter set out.

## Which photon is counted, and why the filter is an experimental control

The cascade emits twice, and the two photons leave the cell under different
rules. The first leg, 6S to 5P, emits near 1324 and 1367 nm, carrying 34.1
and 65.9 per cent of the decays. The second leg is the D-line terminal, 795 nm
through 5P1/2 or 780 nm through 5P3/2, and those photons ARE resonant with the
GROUND state, so the bulk vapour reabsorbs them.

The infrared is not exempt, and the reason it helps is narrower than
wavelength. Its cross-sections are 1.41 and 1.50e-11 cm², the same as the D1
line's, so it absorbs just as strongly per lower-state atom and what separates
the two channels is POPULATION. Inside the driven volume both infrared lines
are inverted, 4.81 and 5.26 to one, because 5P empties in 27 ns while the
drive refills 6S, so trapped infrared stimulates 6S downward instead of
pumping 5P upward. Outside it, trapped D-line photons build a 5P halo where
there is no 6S, and there the infrared does absorb and re-excite, at about
1.07 per cent of the primary rate at 130 °C and nothing at 70 °C. The optical depth for that reabsorption
is $\tau = f_{HF} a N(T) \sigma L$ with $a$ the isotopic abundance, so
it GROWS WITH DENSITY.

That matters because density is the axis a collisional measurement is read
along. A detection channel whose efficiency falls with density puts a
density-dependent factor into every amplitude, and an analysis that reads
amplitudes against density inherits it. The choice of filter therefore sets
which systematic the experiment has, not merely how many photons it counts.

Swapping 795 nm for 780 nm does NOT remove the effect, because the D2 photon
is equally resonant. It changes the cross-section and the hyperfine
weighting, which makes the pair a MEASUREMENT of the trapping rather than an
escape from it: the two legs share one excitation and differ only in their
reabsorption, so their ratio against density is the trapping model's own
test. Collecting the 1.3 um leg instead reduces the effect by about two
orders of magnitude at the top of the sweep rather than removing it, and
moves what remains into a term `scripts/run_trapping_channels.py` has already
computed. What it costs is a detector that reaches past 900 nm.

`rb5s6s/detection.py` carries the three channels, with their wavelengths
computed from the term energies rather than typed, and with a trapped channel
that has no cross-section raising rather than returning zero, since a silent
zero would assert that the photon escapes.

## Where this is used

`rb5s6s/cascade.py` implements the population model, with the invariants
above as its tests. The exact manifold computation behind the table is
`scripts/run_zeeman_depletion.py`, whose committed output is
`results/cascade_branching.csv`.

---

[← Hyperfine populations and branching](hyperfine-populations-and-branching.md) · *Atomic structure and selection rules, 6 of 7* · [Doppler-free geometries →](doppler-free-geometries.md)
