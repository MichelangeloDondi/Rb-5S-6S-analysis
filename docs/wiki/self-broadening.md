# Collisional self-broadening

*[wiki index](README.md) · physical effect*

**The question.** Why an atom's radiating phase, interrupted by collisions,
shows up as a linear, density-dependent Lorentzian width and not a change of
line shape.
**Takes.** The impact approximation's regime: collision duration far
shorter than the interval between collisions. No fitting, no data.
**Gives.** The self-broadening coefficient $\beta_\text{self}$, the
linear-in-density law it sets, and why this repository reports a bound
instead of a value.
**Skip if.** You want the general Lorentzian-plus-Gaussian convolution this
coefficient feeds into, not the collisional mechanism itself. That is
[The Voigt profile](voigt-profile.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An atom radiating in a gas is interrupted: a close encounter with another
atom shifts the emitter's levels for its duration, scrambling the light's
phase. In the impact approximation, a collision lasts far less time than
the mean interval between collisions, so each encounter is treated as an
instantaneous phase randomisation.

![Line width plotted against Rb number density at four temperatures](../../figures/fig1_width_vs_density.png)

*Line width against Rb number density at four temperatures, the four
hyperfine components shown separately.*

Random phase interruptions at mean rate $1/\tau_c$ are statistically
indistinguishable from an extra decay channel, adding $1/\tau_c$ to the
coherence's decay rate. Two consequences follow: the line stays Lorentzian,
since an exponentially decaying coherence always transforms to one, and its
width grows linearly with the collision rate, hence with density at fixed
temperature,

$$\gamma_\text{coll}=\beta_\text{self}N$$

with $\beta_\text{self}$ the slope of width against density. When the
perturber is the same species as the emitter, the effect is self-broadening,
from the van der Waals attraction between an excited atom and a
ground-state one.

Two Lorentzians convolve to a Lorentzian whose widths add, so a
collisionally broadened line carries the natural width plus the collisional
one, $\Gamma_\text{nat}+\gamma_\text{coll}$, with no change of shape.
Density is therefore the only signature of collisions, and must be varied
to measure the coefficient.

## What problem it solves

The coefficient connects a measured lineshape to an interatomic potential,
since $\beta_\text{self}$ depends on the long-range $C_6$ coefficient
between the two states involved. It is also a nuisance term to bound, not a
target, in any experiment raising vapour density for signal, since doing so
broadens the line being measured.

## Where this repository uses it

$\beta_\text{self}$ on the 5S to 6S transition is the repository's first
deliverable, built on the linear-in-density law above.
[Methods chapter 2](../methods/02_the_lineshape.md) sets out the mechanism
and validity condition, [chapter 6](../methods/06_the_statistics.md) the
inference, [what we found](../methods/07_what_we_found.md) the outcome.
Density is swept by changing cell temperature, the lever arm a temperature
sweep read through the vapour-pressure curve as density.

![The width-versus-density trend from the dataset, nearly flat](../../figures/fig6_gamma_floor.png)

*The 2025 dataset's width-vs-density trend is essentially flat, the
observation behind the bound-not-value call.*

The result is a bound, not a value. The fitted width barely grows across
the density span, where a genuine binary-collision width would be linear,
so the fitted $\gamma_\text{coll}$ reads as a residual floor, not resolved
collisions. The rule that decides measurement against bound was set before
the data were examined. Current numbers are in [RESULTS.md](../RESULTS.md).

## Values that moved
This bound has been rebuilt twice, and neither time on new data. The first
rebuild replaced a hard-coded multiplier, which silently assumed more
degrees of freedom than the fit had, with the Student-t quantile for the
degrees of freedom actually present. The second admitted a fourth
temperature session, stretching the density lever and producing the
headline this page quotes. [HISTORY.md](../HISTORY.md) carries every
retired figure and its date.

## A second term

A Lorentzian-equivalent laser width adds to this channel just as the
collisional width does, since Lorentzians convolve to their exact sum. At a
fixed condition the two are unidentifiable: only the sum can be measured,
and a confident split from a fit is a numerical artefact.

Density separates them: $\beta_\text{self} N(T)$ moves with the temperature
ladder, a laser width does not, and both are recovered across the ladder.
Measured on this archive,
$\Gamma_{L,\text{equiv}} = 0.398$ MHz as an inverse-variance mean over four
peaks spanning 0.315 to 0.449 MHz, with a common scalar neither rejected nor
established at $p = 0.097$. Freeing it moves $\beta_\text{self}$ by 42 to 66
per cent ([the laser kernel](laser-frequency-noise-and-the-linewidth.md),
`results/kernel_k3.csv`).

This is the coefficient's binding systematic: the sensitivity to the kernel
representation, within the family tested, is 3.24 times the statistical
error, so repeating the same construction will not improve the number. It
is a sensitivity within that family, not an uncertainty on the coefficient.
The family's own adequacy is separate, addressed by
[identifiability](identifiability.md).

## A term this coefficient absorbs

A two-atom cooperative channel puts a satellite at twice the single-atom
magnetic position, since a pair of atoms can accept two units of angular
momentum where one atom accepts only one
([magnetic sublevels](magnetic-sublevels.md), `rb5s6s/cooperative.py`). Its
rate is linear in density, needing a second atom, and so is its width
contribution.

The two channels are degenerate under a density ladder: no number of
temperature blocks separates them, so whatever the pair channel contributes
is absorbed into $\beta_\text{self}$. This is harmless at the sizes
involved. At Earth's field and 130 °C it adds $3\times10^{-4}$ hertz to a
collisional width of 492 kHz.

A second lever, the field, separates them: this coefficient is indifferent
to it, while the satellite's contribution goes as $B^2$.

A laser contribution to the width is constant in density, not linear in
it, so density does separate it from this coefficient. That separation is
what makes the headline kernel comparison a measurement while its
per-condition version is not ([the Voigt profile](voigt-profile.md)).

## What can go wrong

The impact approximation is a physical assumption with a checkable validity
condition. Outside it the lineshape is not Lorentzian: in the quasistatic
limit, the wings follow the potential directly and are strongly asymmetric.
The condition compares collision duration to the interval between
collisions, and this dataset satisfies it with a wide margin, as chapter 2
states.

A different failure mode lies in the inference: any effect that widens the
line and grows with temperature is absorbed into a fitted
$\beta_\text{self}$, since the fit sees only width against density.
Transit-time broadening scales as $\sqrt{T}$ and does this, as does a laser
whose linewidth drifts over a cooling sweep. The joint fit and the
model-independent bound above separate them, which is why a coefficient
from a single temperature series deserves scrutiny.

Treating $\beta_\text{self}$ as temperature-independent is a further
approximation: a power-law correction is predicted for a van der Waals
potential, and on this dataset the predicted size sits an order of
magnitude below the between-block scatter, so the assumption is unresolved,
not confirmed.

## Try it

The collisional width adds to the natural one. Density alone moves it.

```python
from rb5s6s import GAMMA_NAT_HZ

gamma_nat = GAMMA_NAT_HZ / 1e6
for N in (1.0e13, 2.9e13):
    print(f"N = {N:.1e} /cm3 -> Lorentzian {gamma_nat + 2.0e-13 * N:.3f} MHz")
```

## Further reading

- [`../lit/baranger1958.md`](../lit/baranger1958.md), the impact-approximation
  treatment this page follows, with its own validity bound.
- [`../lit/lewis1980.md`](../lit/lewis1980.md), the relation between the
  broadening coefficient, the interatomic potential, and temperature.
- [Wikipedia: pressure broadening](https://en.wikipedia.org/wiki/Spectral_line_shape#Pressure_broadening),
  the family of mechanisms this one belongs to.

## See also

- [The self-broadening dossier](../quantities/self-broadening.md), the
  literature ladder, current bound, and improvement levels on one page.
- [The Voigt profile](voigt-profile.md), the Lorentzian kernel this
  coefficient's width sets.
- [The joint fit](joint-fit.md), how sharing the laser width across lines
  separates collisional broadening from the rest.
- [Resampling](resampling.md), the leave-one-out diagnostic for how much of
  the bound's leverage sits on one point.
- [Transit-time broadening](transit-time-broadening.md), the mechanism most
  likely to be mistaken for collisional broadening in a temperature sweep.

---

[← Saturation](saturation.md) · *Experimental spectroscopy, 9 of 11* · [Vapour density and temperature →](vapour-density-and-temperature.md)
