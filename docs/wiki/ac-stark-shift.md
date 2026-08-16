# The AC-Stark shift

*[wiki index](README.md) · physical effect*

## What it is

An oscillating electric field shifts atomic energy levels. For light far from
any resonance the shift of a level is proportional to the intensity and to
that level's dynamic polarizability, and what a spectroscopist measures is
the DIFFERENTIAL shift, the difference between the two levels of the
transition. The line moves in proportion to intensity, and the constant of
proportionality is a property of the atom and the wavelength.

The complication in real experiments is that intensity is not one number. A
focused beam has an intensity profile, so atoms at different places see
different shifts, and the observed line is not shifted by a single amount but
BLURRED BY A DISTRIBUTION of shifts. The lineshape acquires an extra kernel
whose form is set by the geometry: how intensity is distributed over the
atoms that actually contribute signal.

That kernel is generally ASYMMETRIC, and the asymmetry is the useful part. A
symmetric broadening mechanism cannot be told apart from any other symmetric
mechanism in a fitted width, but a skew is a distinct signature. Its size
depends on how the signal responds to intensity: a process whose rate goes as
$I^n$ weights the bright regions by $I^n$, and the shape of the resulting
shift distribution depends on $n$. For a one-photon process the distribution
that emerges from a focused Gaussian beam is uniform and carries no skew at
all. The skew exists only because a two-photon signal goes as $I^2$.

## What problem it solves

Read one way it is a systematic: the drive light shifts the very transition
it is probing, so a measured line centre depends on power and must be
extrapolated to zero. Read the other way it is an observable. Because the
shift distribution has a shape set by geometry and by $n$, a lineshape
carries information about the light field the atoms actually experienced,
which is not otherwise accessible.

## Where this repository uses it

It is the subject of the repository's most developed piece of theory, and
this page is an on-ramp rather than the derivation. The closed-form
distribution for a focused beam with an $I^2$ weighting, its cumulants, the
sign flip that diverging-beam collection produces, and the behaviour under
standing-wave fringes are all in
[methods chapter 3](../methods/03_the_ac_stark_ramp.md), with the fuller
theoretical treatment in [THEORY_NOTE.md](../THEORY_NOTE.md). Those are the
derivation of record and this page does not restate them.

![the shift distribution built from the beam geometry](../../figures/fig12_ramp_construction.png)

*How the distribution is built: the beam sets the shift each atom sees, the
signal weights each atom, and the result is the kernel the line is convolved
with. Drawn from the closed form at unit shift, with no data and no fitted
parameters.*

What is worth carrying here is the delineation. The dependence on the signal
exponent $n$ is what separates this channel from the nearest prior art, which
used a one-photon, fringe-resolved method where the distribution is uniform.
The asymmetry is measured through [the third cumulant](third-cumulant.md), and
the current status of the light-shift parameter, a bound rather than a
measurement, is in [RESULTS.md](../RESULTS.md).

## What can go wrong

The dominant model failure is treating the shift as a single number. Quoting
"the light shift" for a focused beam without saying whether it means the peak
axial shift, the mean over the illuminated atoms, or the mean weighted by the
signal, makes a factor-of-order-one ambiguity that propagates into every
derived quantity. The three differ, and which one a fitted parameter
corresponds to depends on the model that produced it.

The second is a geometry assumption. The kernel depends on which atoms are
COLLECTED as well as which are illuminated, so the collection optics enter
the lineshape. Changing the collection solid angle can change the sign of the
skew, which means a shift kernel transferred between benches without
recomputing the geometry is likely to be wrong in a way no fit will reveal.

Third, an inference limitation. The shift kernel broadens as well as shifts,
so at fixed power it is partly degenerate with the other broadening
mechanisms, and separating it needs a power sweep rather than a better fit at
one power.

Finally, a data-insufficiency point specific to the asymmetry. A skew is a
third-moment quantity, and third moments need far more signal-to-noise than
widths do, so a dataset that determines a width comfortably may bound only
the skew.

## Try it

The moments of the shift distribution, and the exponent that decides whether
it is skewed at all.

```python
from rb5s6s import stark_ramp_axial_moments

for n in (1, 2):
    m = stark_ramp_axial_moments(1.0, 1e-4, n_photon=n)
    print(f"n = {n}: mean {m['mean']:+.4f} S0, "
          f"skew {m['skew_standardized']:+.4f}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/stalnaker2006.md`](../lit/stalnaker2006.md), the nearest prior art,
  which measures light shifts by a fringe-resolved one-photon method.
- [Methods chapter 3](../methods/03_the_ac_stark_ramp.md), the derivation of
  record for this repository's ramp law.
- [The third cumulant](third-cumulant.md) for the statistic the asymmetry is
  read through.

---

[← The beam waist](the-beam-waist.md) · *Experimental spectroscopy, 7 of 9* · [Saturation →](saturation.md)
