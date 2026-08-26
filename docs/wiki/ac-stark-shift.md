# The AC-Stark shift

*[wiki index](README.md) · physical effect*

**The question.** How a focused two-photon drive's light shift turns from a
single number into a shaped, asymmetric blur on the line.
**Takes.** The beam waist that converts power into intensity, and no fitted
data.
**Gives.** The shift distribution's shape, its dependence on the two-photon
exponent, and where the derivation and current bound live.
**Skip if.** You want the length that sets intensity in the first place, not
what intensity does to the line, covered in
[the beam waist](the-beam-waist.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An oscillating electric field shifts atomic energy levels, and far from
resonance the shift is proportional to the intensity and to the level's
dynamic polarizability. A spectroscopist measures the differential shift
between the two levels of the transition, so the line moves in proportion
to intensity, with a constant set by the atom and the wavelength.

In a real experiment intensity is not one number: a focused beam has an
intensity profile, so atoms at different places see different shifts, and
the line is blurred by a distribution of shifts instead of moved by one.
This adds a kernel set by the geometry, how intensity is distributed over
the atoms that contribute signal.

That kernel is generally asymmetric, and the asymmetry is useful: a
symmetric broadening mechanism cannot be told apart from another in a
fitted width, but a skew is a distinct signature, sized by how the signal
responds to intensity. A process whose rate goes as $I^n$ weights the
bright regions by $I^n$, so the shape of the shift distribution depends on
$n$: a one-photon process gives a uniform distribution with no skew from a
focused Gaussian beam, and the skew here exists only because the two-photon
signal goes as $I^2$.

## What problem it solves

Read one way it is a systematic: the drive shifts the very transition it is
probing, so a measured line centre depends on power and must be
extrapolated to zero. Read the other way it is an observable: the shift
distribution's shape, set by geometry and by $n$, carries information about
the light field the atoms experienced, otherwise inaccessible.

## Where this repository uses it

This is the repository's most developed piece of theory, and this page is
an on-ramp, not the derivation. The closed-form distribution for a focused
beam with an $I^2$ weighting, its cumulants, the sign flip from
diverging-beam collection, and its behaviour under standing-wave fringes are
in [methods chapter 3](../methods/03_the_ac_stark_ramp.md), with the fuller
treatment in [THEORY_NOTE.md](../THEORY_NOTE.md). This page does not restate
them.

![the shift distribution built from the beam geometry](../../figures/fig12_ramp_construction.png)

*How the shift distribution is built from the beam geometry and the signal's
intensity weighting, from the closed form with no fitted data.*

What is worth carrying here is the delineation from the nearest prior art, a
one-photon, fringe-resolved method giving a uniform distribution: the
dependence on the signal exponent $n$ separates this channel from it. The
asymmetry is measured through [the third cumulant](third-cumulant.md). The
current light-shift parameter is a bound, not a measurement, in
[RESULTS.md](../RESULTS.md).

## One coefficient across the whole manifold

For an S-to-S line, whether each hyperfine component carries its own shift
coefficient has a clean answer: no, at any measurable level, through two
channels computed here. Dispersion: the four lines are driven at slightly
different wavelengths, and the differential polarizability at each line's
own drive spans $1.2\times10^{-5}$ of itself across the manifold. Hyperfine
mixing: the F-dependent correction scales as the hyperfine constant over the
optical detuning, near $4.5\times10^{-5}$, putting the per-line shift
differences at 4 to 16 Hz against a 0.35 MHz common shift.

![computed polarizability curves and their zero crossings](../../figures/fig17_magic_wavelengths.png)

*Computed 5S and 6S polarizability curves and their three zero crossings,
three hundred to nine hundred nanometres from the 993 nm drive.*

Every separation between components is light-shift-immune twice over, once
because the scalar shift moves all $m_F$ together and once because the
coefficient is flat across the manifold, making the internal spectrum
geometry a null channel at full power. No magic wavelength falls between the
components either: the differential polarizability holds its full value
across the whole span, with genuine zeros hundreds of nanometres away, where
the record's polarizability model puts them.

## What can go wrong

The dominant failure is treating the shift as a single number. "The light
shift" for a focused beam can mean the peak axial shift, the mean over the
illuminated atoms, or the mean weighted by the signal, and not saying which
makes a factor-of-order-one ambiguity that propagates into every derived
quantity: which one a fitted parameter matches depends on the model that
produced it.

The second is a geometry assumption: the kernel depends on which atoms are
collected as well as illuminated, so the collection optics enter the
lineshape, and changing the collection solid angle can change the sign of
the skew. A kernel transferred between benches without recomputing the
geometry is likely wrong in a way no fit will reveal.

Third, an inference limitation: the shift kernel broadens as well as shifts,
so at fixed power it is degenerate with the other broadening mechanisms, and
separating it needs a power sweep, not a better fit at one power.

Finally, a data-insufficiency point: a skew is a third-moment quantity,
needing far more signal-to-noise than a width, so a dataset that determines
a width well may only bound the skew.

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

Every snippet here is executed by `tests/test_wiki_snippets_run.py`, so one
that stops working fails the suite instead of misleading a reader.

## Values that moved
The ramp prediction published in July was evaluated at the beam waist
accepted at the time, and that waist was later replaced by a direct
same-bench measurement. The prediction has not been recomputed against the
replacement, so it stands at a retired input.
[HISTORY.md](../HISTORY.md) carries both rows and the live figures.

## Further reading

- [`../lit/stalnaker2006.md`](../lit/stalnaker2006.md), the nearest prior art,
  which measures light shifts by a fringe-resolved one-photon method.
- [Methods chapter 3](../methods/03_the_ac_stark_ramp.md), the derivation of
  record for this repository's ramp law.
- [The third cumulant](third-cumulant.md) for the statistic the asymmetry is
  read through.

## See also

- [The AC-Stark dossier](../quantities/ac-stark-light-shift.md), for the
  bound per construction, the literature benchmark, and the recipes to
  convert it into a measurement.
- [The beam waist](the-beam-waist.md) for the length that converts power into
  the intensity this shift responds to.
- [Saturation](saturation.md) for the boundary where this shift's I-squared
  law starts to fail.
- [The third cumulant](third-cumulant.md) for the statistic that reads the
  shift distribution's asymmetry out of a fitted line.
- [Blackbody radiation](blackbody-radiation.md) for the cell's own thermal
  field, a second source of level shift acting on the same states.
- [Magnetic sublevels](magnetic-sublevels.md) for the vector piece of this
  light shift, 1.7 per cent of the scalar coefficient at the drive
  wavelength. It cancels in the mean over a symmetric population and only
  spreads the line, but ellipticity that pumps the population shifts it,
  uncovered by this page's scalar treatment.

---

[← The beam waist](the-beam-waist.md) · *Experimental spectroscopy, 6 of 11* · [The inhomogeneous light shift →](the-inhomogeneous-light-shift.md)
