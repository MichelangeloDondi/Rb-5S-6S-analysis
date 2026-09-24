*Chapter 10 of 10 of [the big picture](../BIG_PICTURE.md)*

## 10. Applications and reach

This page is about value and not priority. The estimator machinery here is borrowed and
[says so](../lit/hansen1982.md). What follows is what the method measures, and where else the
same condition holds.

## The applicability condition

A spectral line is a mixture. Each atom sits in its own local environment, and the line is the sum
over that environment's distribution.

The standard treatment writes the line as a convolution and fits a width. **That is valid only when
the homogeneous kernel is the same at every collected volume element.** When the kernel itself
depends on the mixture variable, the line is not a convolution, no deconvolution recovers the
distribution, and a fitted width is not a parameter of anything.

That condition fails whenever one coordinate sets two things at once. At a focused beam, an atom's
position fixes both the light shift it feels and the transit time it spends in the beam. Near a
surface, distance fixes both the level shift and the interaction time. In a trap, position fixes
both the potential and the sampling of it.

Where the condition fails, the higher moments of the line carry the environment's distribution,
and the first moment does not. That is the whole content of the method, and it is physical rather
than statistical.

## Measurements beyond a width fit

A width fit returns one number per line and needs the other broadening terms known. The moment
family returns the shape of the environmental distribution, and its members respond differently to
each term, which is what lets the terms be separated rather than assumed.

Three consequences that are specific and not general. The shift distribution's skew carries a
sign, so a quantity whose sign is disputed can be settled without an absolute frequency
calibration. A magic wavelength is a zero crossing of the odd moments, locatable by bracketing from
both sides instead of nulling a shift that has to be calibrated. And a drifting lock removes
the centroid and leaves every central moment standing, so a channel written off as lost to drift is
not.

## Other settings satisfying the condition

| setting | the coordinate that sets two things | what the moments would measure |
|---|---|---|
| focused-beam spectroscopy, two-photon or Rydberg | position sets the light shift and the transit | the intensity distribution the atoms actually sample |
| optical lattice and tweezer clocks | position sets the trap light shift and the sampling of it | the trap's own intensity distribution, and the magic point as a sign reversal |
| atoms near a nanofibre or in a hollow core | distance sets the surface shift and the interaction time | patch potentials, adsorbate fields, and their drift in time |
| plasma Stark broadening | the microfield sets the shift and the collision rate | the field distribution, which [Baranger and Mozer](../lit/baranger1959.md) already reconstruct |
| wide-line NMR and EPR | local field sets the shift and the relaxation | the same method-of-moments problem [Van Vleck](../lit/vanvleck1948.md) posed in 1948, whose stated difficulty is the truncation this record treats |
| galaxy kinematics | orbit sets the velocity and the weight | the line-of-sight velocity distribution, where the field chose an orthogonal basis instead |

The table is a map of where to look, not a claim to have done any of it. Each row is an
independent piece of work and each needs its own forward model.

## The numbers a campaign built this way returns

Differential polarizabilities. Self-broadening rates at several temperatures. Vapour density laws
against temperature, which are an input to everything else and are known to disagree between
correlations. Surface potentials near a fibre. Gas permeation rates through a sealed cell, which
are a clock on the cell's own age.

Each is a spectroscopy number that is currently either unmeasured or measured under an assumption
the method replaces with a measurement. That list is the argument for the approach, and it is a
better one than any statement about what is new in it.

## Self-calibrated quantities

A line carries more than the quantity it is fitted for. Once the distribution is read rather than
summarised, several nuisances become readable from the same trace, which is worth more to an
experiment than any single number:

| quantity | what reads it |
|---|---|
| atomic temperature | the Doppler width against the transit width, which scale differently with the waist |
| wall temperature and the cold spot | the density law against the collisional width |
| buffer or permeated gas pressure | a width term with no power dependence and a known temperature exponent |
| magnetic field | the quadratic Zeeman shift as a separate, even term |
| scan non-linearity and hysteresis | the ruler comb against the fitted centres, forwards and backwards |
| laser frequency noise | the kernel's own shape, separated from the transit by its power dependence |
| the cell's sealing date | the permeation rate integrated over the cell's life |

Each row is a measurement the apparatus currently takes on trust. Replacing an assumption with a
reading is the practical case for the method, and it does not depend on anything being new.

## The problems it answers

| the problem | what this record does | where it stands |
|---|---|---|
| the leading systematic is suppressed and never measured | reads the light-shift distribution from the odd moments, the centroid left free | built; the 2025 data bound the shift per recorded watt at the ruled waist |
| a line is assumed to be a convolution | tests the condition: a convolution keeps the mean and the variance and drops the shift-width covariance from the third cumulant | measured ([kernel_inhomogeneity](../../results/kernel_inhomogeneity.csv)) |
| contrast loss is attributed, never measured | reads the shift distribution that sets it, through the characteristic function | derived; the thermal case tested once |
| two numbers cannot separate ten unknowns | many functionals of one trace against one forward model | designed; the joint fit is next |
| higher moments of truncated noisy curves are unusable | a bias surface on a twin of the whole measurement | measured at one condition |
| a profile fit fails silently when a term is missing | the moments as a second, robust estimator | measured ([estimator_duel](../../results/estimator_duel.csv)) |
| the apparatus is calibrated elsewhere | the atoms measure the beam, the vapour and the scan | partly in the model |
| results from different platforms cannot be combined | one laser and one likelihood across platforms | designed and forecast |
| beam time is spent by habit | the twin forecasts each design before it is run | built |

## The novelty and its boundary

The estimators are not ours and the literature naming them is [held](../LITERATURE_INDEX.md):
the generalised method of moments, indirect inference, simulated moments, moment selection
criteria. Reading a distribution off a family of threshold-indexed observables is from
[1978](../lit/breeden1978.md). Reading moments off a line is from
[1948](../lit/vanvleck1948.md).

What is ours is a measurement design: the bias of each windowed statistic forecast at every window
and noise level, on a forward twin validated against an independent Monte Carlo before it is used
to forecast anything, and coordinates chosen by their measured bias, never accumulated.
Sweeping a truncation axis is not ours. Particle physics fits central moments at many lower cuts
in one fit ([buchmueller2006](../lit/buchmueller2006.md)), and cosmology corrects amplitude-free
moment ratios for the smoothing window ([bernardeau1994](../lit/bernardeau1994.md)).

The sharper statement, and it is the one to use: the method is not new as statistics, it is new
as instrumentation. Sixty years of estimator theory exists and had not been brought to a line whose
shift and transit are set by the same coordinate, because that needs a forward twin cheap enough to
measure the bias at every window and every noise level. A statistician cannot dispute that sentence
and a spectroscopist can use it.

Conceding the statistics is the strong position and not the weak one. A referee who owns that
literature reads a broad claim as a claim on their field and stops reading. The narrow claim is
defensible, it is checkable against the held shelf, and it leaves the chapter free to spend its
pages on the physics in the table above.

---

*[The campaign cases](09_the-campaign-cases.md) · [the big picture](../BIG_PICTURE.md)*
