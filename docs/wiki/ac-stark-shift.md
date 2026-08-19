# The AC-Stark shift

*[wiki index](README.md) · physical effect*

**The question.** How a focused two-photon drive's own light shift turns from
a single number into a shaped, asymmetric blur on the measured line.
**Takes.** The beam waist that converts power into intensity, and no fitted
data of its own.
**Gives.** The shift distribution's shape, its dependence on the two-photon
exponent, and where the derivation of record and the current bound live.
**Skip if.** You want the length that sets the intensity in the first place
rather than what the intensity does to the line, covered in
[the beam waist](the-beam-waist.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

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

## One coefficient across the whole manifold

A hyperfine-resolved spectrum invites the question of whether each component
carries its own shift coefficient, and for an S-to-S line the answer is no
at any measurable level, through two channels that were both computed here.
DISPERSION: the four lines are driven at slightly different wavelengths, and
the differential polarizability evaluated at each line's own drive spans
$1.2\times10^{-5}$ of itself across the manifold. HYPERFINE MIXING: the
F-dependent correction scales as the hyperfine constant over the optical
detuning, near $4.5\times10^{-5}$. Together they put the per-line shift
DIFFERENCES at 4 to 16 Hz where the common shift is 0.35 MHz.

Two consequences carry weight. Every separation between components is
light-shift-immune twice over, once because the scalar shift moves all $m_F$
together and once because the coefficient is flat across the manifold, so
the internal geometry of the spectrum is a null channel at full power. And
no magic wavelength hides between the components: the differential
polarizability holds its full value across the whole span, with its genuine
zeros hundreds of nanometres away, where the record's polarizability model
puts them.

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

## What this repository got wrong once

The ramp law turns a beam waist into a predicted shift, and on 2026-07-16 that
prediction was published at $S_0 = 0.59$ MHz, evaluated at the transit Monte
Carlo's 50 µm waist. On 2026-08-01 the adopted waist moved to 64 µm, Rajasree's
direct measurement on the same laser replacing the transit estimate as the
prior, and the 0.59 MHz figure kept standing without being recomputed against
the new input. [HISTORY.md](../HISTORY.md) names the standing plainly: "a
prediction at a retired input." This is exactly the coupling the page above
describes: the shift a spectroscopist predicts depends on the intensity the
atoms sit in, and the intensity a fixed power produces depends on the spot
size, so a predicted shift carries its waist as a silent assumption unless
that assumption is stated and re-checked. Treating the waist as part of the
prediction's provenance, not as a fixed constant behind it, would have flagged
the 0.59 MHz number as stale the day the waist changed rather than leaving it
to circulate.

The same table shows the "single number" failure this page's own "What can go
wrong" section opens with. The bound $S_0$ at 225 mW itself moved three times,
3.1 MHz before 2026-07-16, 0.63 MHz from that date, 0.14 MHz from 2026-08-01,
each a construction change rather than new data. Alongside it the
polarizability bracket $\Delta\alpha \approx 5800 \to 1200$ a.u., the bound
divided through by its predicted coefficient, moved with it. HISTORY records
that this bracket "tracks whichever bound is quoted" rather than settling on a
value, which means a $\Delta\alpha$ figure copied without the $S_0$ bound it
was computed from is not a fixed number at all, only a ratio waiting to be
re-divided the next time the bound tightens.

## Further reading

- [`../lit/stalnaker2006.md`](../lit/stalnaker2006.md), the nearest prior art,
  which measures light shifts by a fringe-resolved one-photon method.
- [Methods chapter 3](../methods/03_the_ac_stark_ramp.md), the derivation of
  record for this repository's ramp law.
- [The third cumulant](third-cumulant.md) for the statistic the asymmetry is
  read through.

## See also

- [The AC-Stark dossier](../quantities/ac-stark-light-shift.md), where the
  bound per construction, the literature benchmark and the recipes that would
  convert the bound into a measurement live on one page.
- [The beam waist](the-beam-waist.md) for the length that converts power into
  the intensity this shift responds to.
- [Saturation](saturation.md) for the boundary where the underlying I-squared
  law this shift assumes starts to fail.
- [The third cumulant](third-cumulant.md) for the statistic that reads the
  shift distribution's asymmetry out of a fitted line.
- [Blackbody radiation](blackbody-radiation.md) for the cell's own thermal
  field, a second source of level shift acting on the same states.

---

[← The beam waist](the-beam-waist.md) · *Experimental spectroscopy, 6 of 9* · [Saturation →](saturation.md)
