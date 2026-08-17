# Collisional self-broadening

*[wiki index](README.md) · physical effect*

**The question.** Why an atom's radiating phase, interrupted by collisions,
shows up as a linear, density-dependent Lorentzian width rather than a
change of line shape.
**Takes.** The impact approximation's regime, a collision duration far
shorter than the interval between collisions. No fitting, no data.
**Gives.** The self-broadening coefficient $\beta_\text{self}$, the
linear-in-density law it sets, and why this repository reports a bound
rather than a value.
**Skip if.** You want the general Lorentzian-plus-Gaussian convolution this
coefficient feeds into rather than the collisional mechanism itself. That
is [The Voigt profile](voigt-profile.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An atom radiating in a gas is interrupted. When another atom passes close
enough, the interaction shifts the emitter's levels for the duration of the
encounter, and the phase of the light it is radiating is scrambled. In the
IMPACT APPROXIMATION, where a collision lasts far less time than the mean
interval between collisions, each encounter can be treated as an instantaneous
randomisation of the optical phase.

Random phase interruptions at mean rate $1/\tau_c$ are statistically
indistinguishable from an extra decay channel: they add $1/\tau_c$ to the
decay rate of the coherence. The consequences are the two that matter.
The line STAYS LORENTZIAN, because an exponentially decaying coherence
transforms to a Lorentzian whatever the reason for the decay. And its width
grows LINEARLY with the collision rate, which for a gas at fixed temperature
means linearly with density,

$$\gamma_\text{coll}=\beta_\text{self}N$$

with $\beta_\text{self}$ the self-broadening coefficient, the slope of width
against density. When the perturber is the same species as the emitter the
effect is called self-broadening, and the interaction is generally the
van der Waals attraction between an excited atom and a ground-state one.

Because the convolution of two Lorentzians is a Lorentzian whose widths add,
a collisionally broadened line simply carries the natural width plus the
collisional one, $\Gamma_\text{nat}+\gamma_\text{coll}$, with no change of
shape at all. That is what makes the effect a clean lever: the only signature
of collisions is a width that grows with density, so density has to be varied
for the coefficient to be measurable.

## What problem it solves

The coefficient is the observable that connects a measured lineshape to an
interatomic potential, since $\beta_\text{self}$ depends on the long-range
$C_6$ coefficient between the two states involved. It is also a nuisance to
be bounded rather than a target, in any experiment where a vapour density is
raised to gain signal, because it broadens the very line being measured.

## Where this repository uses it

$\beta_\text{self}$ on the 5S to 6S transition is the repository's first
deliverable, and the measurement strategy is built entirely around the
linear-in-density law above.
[Methods chapter 2](../methods/02_the_lineshape.md) sets out the mechanism and
the validity condition, [chapter 6](../methods/06_the_statistics.md) the
inference, and [what we found](../methods/07_what_we_found.md) the outcome.
The density is swept by changing the cell temperature, so the lever arm is a
temperature sweep read as a density sweep through the vapour-pressure curve.

The result is a BOUND rather than a value, and the reason is worth reading
before reusing the number. The fitted width barely grows across the density
span, where a genuine binary-collision width would be linear in it, so the
fitted $\gamma_\text{coll}$ is better understood as a residual floor than as
resolved collisions. The rule that decides measurement against bound was set
before the data were examined, and the current numbers are in
[RESULTS.md](../RESULTS.md).

## What can go wrong

The impact approximation is a physical assumption with a checkable validity
condition, and outside it the lineshape is not Lorentzian at all: in the
opposite, quasistatic limit the wings follow the potential directly and are
strongly asymmetric. The condition compares the collision duration to the
interval between collisions, and this dataset satisfies it with a wide
margin, which chapter 2 states.

The dangerous failure is an inference one. Any effect that widens the line and
happens to grow with temperature will be absorbed into a fitted
$\beta_\text{self}$, because the fit sees only width against density.
Transit-time broadening scales as $\sqrt{T}$ and does exactly this, and so
does a laser whose linewidth drifts over a session that also happens to be a
cooling sweep. Separating them is what the joint fit and the model-independent
bound in the chapters above are for, and it is why a self-broadening
coefficient extracted from a single temperature series deserves suspicion.

Treating $\beta_\text{self}$ as temperature-independent is a further
approximation. A power-law correction is predicted for a van der Waals
potential, and on this dataset the predicted size sits an order of magnitude
below the between-block scatter, so the assumption is unresolved rather than
confirmed.

## Try it

The collisional width adds to the natural one, and only the density moves it.

```python
from rb5s6s import GAMMA_NAT_HZ

gamma_nat = GAMMA_NAT_HZ / 1e6
for N in (1.0e13, 2.9e13):
    print(f"N = {N:.1e} /cm3 -> Lorentzian {gamma_nat + 2.0e-13 * N:.3f} MHz")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## What this repository got wrong once

$\beta_\text{self}$ carries four entries in [HISTORY.md](../HISTORY.md), and
most of the movement between them is interval construction and design, not
new physics. Before 2026-07-16 the headline stood at 0.07-0.15 MHz per
$10^{12}\text{cm}^{-3}$, the between-block scatter multiplied by a hard-coded
2σ that silently assumed more degrees of freedom than the fit had. On
2026-07-16 the same scatter, read instead off the Student-t quantile
$t(0.95,1) = 6.31$ on the single residual degree of freedom the fit actually
carried, widened it to 0.2-0.4.

Separately, the per-peak, 95% bound stood on 2026-07-11 at < 0.21-0.44,
model-independent raw widths across a three-point 70-110 °C cooling sweep.
It was retired on 2026-08-02 once a fourth, 130 °C session was admitted, on
the experimenter's own firsthand authority over the apparatus configuration
rather than on an independently logged record, a provenance judgment rather
than a new measurement of the physics. Folding that point in produced the
current headline, ≲0.03-0.05, the four-point 70/90/110/130 °C construction
at dof = 2 with a ×52.5 lever.

That lever is exactly the mechanism this page opens with:
$\gamma_\text{coll}=\beta_\text{self}N$ is measurable only by varying $N$,
and a temperature sweep read as a density sweep is only as tight a lever as
the density span it actually reaches. Adding the 130 °C point lengthens that
span far more than it lengthens the point count, which is most of why the
bound tightened by roughly an order of magnitude rather than by the modest
factor a fourth point alone would buy. A reader who asked, before trusting
the three-point bound, how much of the fit's leverage sat on its single
hottest and hence least-populated end, the same question
[Resampling](resampling.md)'s leave-one-out diagnostics now ask of the
four-point fit, would have known the three-point number was starved of
exactly the lever the current construction supplies, and would have asked
for the provenance of a fourth point before quoting a bound that needed one.

## Further reading

- [`../lit/baranger1958.md`](../lit/baranger1958.md), the impact-approximation
  treatment this page follows, including its own validity bound.
- [`../lit/lewis1980.md`](../lit/lewis1980.md) for the relation between the
  broadening coefficient and the interatomic potential, and for the
  temperature dependence.
- [Wikipedia: pressure broadening](https://en.wikipedia.org/wiki/Spectral_line_shape#Pressure_broadening)
  for the family of mechanisms this one belongs to.

## See also

- [The Voigt profile](voigt-profile.md), the Lorentzian kernel this
  coefficient sets the width of.
- [The joint fit](joint-fit.md), how sharing the laser width across lines
  separates collisional broadening from the rest.
- [Resampling](resampling.md), the leave-one-out diagnostic that asks how
  much of the bound's leverage sits on one point.
- [Transit-time broadening](transit-time-broadening.md), the
  temperature-dependent mechanism most likely to be mistaken for
  collisional broadening in a temperature sweep.

---

[← Saturation](saturation.md) · *Experimental spectroscopy, 8 of 8* · [wiki index →](README.md)
