# Hyperfine populations and branching

*[wiki index](README.md) · concept*

## What it is

A hyperfine level $F$ carries $2F+1$ magnetic sublevels, one for every
allowed $m_F$, and with no external field to single one out they sit at the
same energy. Left to reach thermal equilibrium, the population any level
holds follows a Boltzmann factor $\exp(-E/k_BT)$, but a hyperfine splitting
runs from a few megahertz to a few gigahertz while $k_BT$ at any temperature
a vapour cell reaches corresponds to hundreds of gigahertz. Between two
hyperfine levels of one atom the Boltzmann factor is therefore
indistinguishable from one at any cell temperature, and the population a
level holds collapses to its degeneracy alone: a level with quantum number
$F$ carries a share $(2F+1)/G$ of the atoms in its manifold, where $G$ is the
degeneracy summed over every $F$ the ground state offers. Counting sublevels,
not solving a rate equation, is what fixes how many atoms sit in each
hyperfine level.

A second element carries its own atoms of a different isotope, and natural
abundance multiplies the same counting by one more factor: the population
feeding a given isotope's hyperfine level is the product of how common that
isotope is and how many sublevels its own level offers relative to its own
total. Nothing about one isotope's nuclear spin or abundance enters the
other isotope's count.

When the driving field couples every populated sublevel alike, which holds
for a two-photon operator built from identical photons on a transition that
carries no rank able to prefer one $m_F$ over another, the strength of each
observed hyperfine line is exactly the population feeding it. No transition
rate, no matrix element and no lineshape parameter enters the ratio between
two such lines: it is counting, gated by degeneracy and by abundance, and
nothing dynamical.

Population statistics reappear on the way down. An excited atom does not
fall straight back to the ground hyperfine level that launched it. It decays
through an intermediate electronic level first, and that intermediate decay
answers to its own selection rules and branching ratios, which know nothing
about which ground level the atom started in. An atom driven from the
ground level the laser addresses can therefore land, after the round trip,
in the ground level the laser does not address, detuned by a splitting
thousands of times its own linewidth. It has left the experiment while still
physically inside the beam. This is hyperfine pumping, built entirely from
branching probabilities rather than from any coherent dynamics.

That departure is a lineshape effect, not only a signal-size one. An atom
that is pumped out partway through its crossing stops contributing after a
shorter stretch of time than an atom that survives the whole transit, and a
shorter interaction time broadens the response the same way any early
truncation does: a measurement cut short reads out with a wider spectrum,
whatever cut it short.

## What problem it solves

It replaces a transition-rate calculation with an arithmetic one. Predicting
the relative strength of several hyperfine lines from a driven cascade would
otherwise need the two-photon matrix element, the collection efficiency and
every other factor common to the lines, all evaluated well enough to trust a
ratio. Population counting needs none of that: two numbers per line,
degeneracy and abundance, fix the ratio exactly, so the prediction is a
closed-form null hypothesis that data can be checked against without first
fitting anything.

It also separates two distinct costs of an atom leaving mid-transit. One is
that fewer photons are collected, which affects amplitude. The other is that
the atoms still being collected were, on average, interrupted earlier in
their crossing, which affects width. A population argument that stops at
counting misses the second cost entirely, and it is the one that couples
hyperfine pumping to every other broadening mechanism this repository has to
separate from the light shift.

## Where this repository uses it

The population weight for each of the four observed lines, abundance times
degeneracy share, is the prediction committed in the `predicted` column of
[`results/amplitude_ratios.csv`](../../results/amplitude_ratios.csv),
produced by [`predicted_shares`](../../rb5s6s/amplitudes.py) from
[`constants.PEAKS`](../../rb5s6s/constants.py) and the isotopic abundances
[`constants.ABUNDANCE_RB85`](../../rb5s6s/constants.py) and
[`constants.ABUNDANCE_RB87`](../../rb5s6s/constants.py). Because abundance
cancels between two lines of the same isotope, that file predicts the
993.4207/993.4121 nm ratio at exactly $5/3$ and the 993.4192/993.4154 nm
ratio at exactly $7/5$ from degeneracy alone, and the cross-isotope
993.4192/993.4207 nm ratio at a little over $2.4$, where abundance enters
too. The measured column in the same file is the comparison against those
counting-only numbers, drawn in
[`figures/fig4_amplitude_ratios.png`](../../figures/fig4_amplitude_ratios.png).
The same module also reads the temperature dependence of the
measured-to-predicted ratio as a probe of radiation trapping, the emitted
795 nm decay photons being reabsorbed on the way out, a density-dependent
effect the pure counting law above does not include.

The branching side is not a single shared number. Because it is a two-step
cascade through the intermediate $5P$ levels rather than a degeneracy count,
the branching fraction that lands a decaying atom in the ground level the
laser is not addressing differs line to line, and the four values are
committed in `F_PER_LINE` in [`rb5s6s/stark.py`](../../rb5s6s/stark.py). The
resulting extra width enters through
[`companion_gamma_mhz`](../../rb5s6s/stark.py), one of two effects this
repository has identified that broaden the line with exactly the light
shift's own power and waist signature, so that no power sweep or focus
change this dataset can run separates them from each other. That argument,
and the size of the bound it costs, is worked out in
[the method and its limits, section 1.3a](../big_picture/02_the-method-and-its-limits.md)
and in
[the saturation companion note](../notes/two_photon_saturation_companion.md).

## What can go wrong

The most direct mistake is comparing peak heights rather than integrated
areas. Height is area divided by width times a shape factor, so a height
comparison folds in whatever makes the width drift from one measurement
block to the next, typically laser alignment, and quietly turns a
population comparison into a width comparison. The area is what the
population argument actually predicts, which is why `peak_area` in
[`rb5s6s/amplitudes.py`](../../rb5s6s/amplitudes.py) integrates the trace
rather than reading its maximum.

A second trap is conflating two different fractions that both get called
"pumping". The share of transiting atoms that decay at least once is
larger than the share that lands specifically in the wrong ground level,
because only some of those decays cross over, so quoting the first number
while describing the second overstates the effect. The two are kept as
separate quantities wherever this repository states them.

A third is treating the per-line branching fraction as one shared constant
across all four lines because the ramp and the saturation companion are
both line-independent and it is tempting to assume the third companion is
too. It is not: it is a cascade product through two intermediate fine
structure levels, not a degeneracy ratio, so nothing guarantees it repeats
across lines the way a population weight does.

A fourth is experimental rather than a modelling error. Each hyperfine line
in this campaign is its own measurement block, taken hours apart from the
others, so a cross-peak amplitude ratio inherits whatever power or
alignment drift happened between those blocks on top of the population
prediction, and a departure from the predicted ratio is not evidence
against the counting law unless that drift has been accounted for.

## Try it

The degeneracy-and-abundance weight of each observed line, built only from
`rb5s6s.constants`, reproduces the exact ratios committed in
`results/amplitude_ratios.csv`.

```python
from rb5s6s.constants import PEAKS, ABUNDANCE_RB85, ABUNDANCE_RB87

# Nuclear spin I, a fixed property of each isotope: 87Rb has I = 3/2, 85Rb
# has I = 5/2. For the J = 1/2 ground state F runs over |I - 1/2| and
# I + 1/2, so the two F levels together carry (2*I + 1) * 2 sublevels.
NUCLEAR_SPIN = {87: 1.5, 85: 2.5}
ABUNDANCE = {87: ABUNDANCE_RB87, 85: ABUNDANCE_RB85}


def ground_sublevels(isotope: int) -> int:
    spin = NUCLEAR_SPIN[isotope]
    return round((2 * spin + 1) * 2)


weight = {}
for label, info in PEAKS.items():
    isotope, F = info["isotope"], info["F"]
    weight[label] = ABUNDANCE[isotope] * (2 * F + 1) / ground_sublevels(isotope)

total = sum(weight.values())
share = {label: w / total for label, w in weight.items()}

print("predicted relative line strength, counting only:")
for label, info in PEAKS.items():
    print(f"  993.{label} nm ({info['isotope']}Rb F={info['F']}): "
          f"{share[label]:.4f}")

r_87 = share["4207"] / share["4121"]
r_85 = share["4192"] / share["4154"]
r_cross = share["4192"] / share["4207"]
print(f"\n4207/4121 (same isotope, abundance cancels): {r_87:.4f} (= 5/3)")
print(f"4192/4154 (same isotope, abundance cancels): {r_85:.4f} (= 7/5)")
print(f"4192/4207 (cross isotope, abundance also enters): {r_cross:.4f}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- C. J. Foot, *Atomic Physics* (Oxford University Press, 2005), chapter 6,
  for the thermal-population argument behind the degeneracy weighting above.
- W. Happer, "Optical pumping," *Rev. Mod. Phys.* 44, 169 (1972), the
  founding treatment of population transfer by branching through an
  intermediate level.
- [`../lit/arora2012.md`](../lit/arora2012.md), the coupled-cluster
  branching of the $6S$ decay between $5P_{1/2}$ and $5P_{3/2}$ that starts
  the cascade this page's pumping fraction runs through.
- [`../lit/steck_rb.md`](../lit/steck_rb.md), the standard reference for the
  D-line branching ratios and hyperfine constants this repository's cascade
  calculations draw on.
- [Hyperfine structure](hyperfine-structure.md), for the levels this page
  puts populations on.
- [Transit-time broadening](transit-time-broadening.md), for the general
  relation between a shortened interaction time and a broader line that the
  pumping argument above uses.

---

[← Magnetic sublevels](magnetic-sublevels.md) · *Atomic structure and selection rules, 5 of 6* · [Doppler-free geometries →](doppler-free-geometries.md)
