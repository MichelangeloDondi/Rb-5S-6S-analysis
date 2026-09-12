# Identifiability

*[wiki index](README.md) · method*

**The question.** Whether the data can actually separate two parameters, or
only determine some combination of them.
**Takes.** A fitted model and its parameter covariance.
**Gives.** The structural-versus-practical distinction, three diagnostics
for a degeneracy, and what breaking one is worth.
**Skip if.** The question is building a confidence interval that already
accounts for a nuisance parameter's freedom, instead of whether two
parameters are separable at all. That is
[the profile likelihood](profile-likelihood.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A parameter is identifiable if the data could, in principle, distinguish its
true value from any other. This is a property of the model and the
experiment together, not of the fitting routine, and it is decided before
any data are collected. If two different parameter values predict exactly
the same observation, no amount of data, no better optimiser and no
cleverer algorithm will separate them.

The clean case is structural non-identifiability: the model is written so
that only a combination of parameters appears. If a prediction depends only
on the product $ab$, then $a$ and $b$ are separately unknowable and the
product is the only thing measured. A fit will still return values for
both, because software returns whatever the optimiser stopped at, and their
apparent precision is an artefact of where it started.

The commoner case is practical non-identifiability: the parameters are
distinguishable in principle, but only through a feature the data do not
resolve at the available signal-to-noise. Here the likelihood has a long
flat valley instead of an exactly flat direction, and estimates slide along
it. The same three diagnostics apply in both cases:

- the parameter covariance, whose near-unit correlations name the degenerate pairs
- the condition number of the sensitivity matrix, which says how nearly singular the problem is
- the [profile likelihood](profile-likelihood.md), which maps the valley directly instead of approximating it with an ellipse at one point

The remedy is to change the experiment, either by adding a measurement that
moves one parameter and not the other, or by reporting only the combination
the data determine.

## What problem it solves

It decides whether a number should be published, by asking whether the
dataset determines the quantity itself or only something the quantity is
part of. Answering it early turns an unfalsifiable result into either a
measurement or a stated bound.

## Where this repository uses it

It is the reason several quantities here are reported as bounds instead of
values. The analysis is worked in full in
[methods chapter 6 section 4.10](../methods/06_the_statistics.md), with the
numbers committed to
[`results/identifiability.csv`](../../results/identifiability.csv) and
drawn in the figure below.

![Profile-likelihood map of collisional and laser width](../../figures/fig7_identifiability_profile.png)

*The collisional-versus-laser-width plane at one bright condition: the
profile-likelihood valley against the local covariance ellipse a single fit
would report alone.*

The degeneracy is physical: the collisional width, the laser width and the
transit width all broaden the same line, so a single line constrains their
sum far better than their split. The chapter quantifies this at one bright
condition using a local covariance analysis and a global profile map, with
all three widths free.

A single-start fit of all three widths settles in one minimum. The profile
map exposed a second, deeper minimum elsewhere in the plane, separated from
the first by a gap the chapter records instead of smoothing over. A fit
that converges is not the same as a parameter that is determined, which is
why the map exists.

## What breaking it is worth

Non-identifiability is not always permanent. Where a degenerate pair can be
separated by measuring one member independently, the gain is concrete and
worth computing before deciding whether the measurement is affordable.

![Parameter identifiability status by design increment](../../figures/fig33_identifiability_matrix.png)

*Parameter status across four campaign design increments, from the 2025
archive to a beam profile measured on the day: bounded, identified, or
measured.*

In this repository the collisional and laser widths are the degenerate
pair. On a bright synthetic condition with signal-dependent noise
(`python scripts/run_width_pinning.py`), a fit with both widths free
recovers the collisional width with a scatter of 0.0070 MHz, and the same
fit with the laser width fixed recovers it with 0.0022 MHz, a ratio of 3.18
with a spread of 0.20 across nine seeds, since Monte Carlo ratios vary by
seed. An earlier version of this page quoted a single draw of 3.4, the
largest of the nine. The absolute scatters belong to this idealised
condition. The real record adds block drift and gain scatter on top, and
the ratio is what transfers: an independent laser diagnostic reduces the
collisional-width scatter by about this factor.

### The general formula for the factor

The general answer is arithmetic: conditioning a multivariate normal on one
member of a correlated pair reduces the other's variance to $(1-\rho^2)$ of
its joint value, so its uncertainty falls by $\sqrt{1-\rho^2}$, a factor of
$1/\sqrt{1-\rho^2}$ that depends only on the correlation and does not
improve with more traces.

| where the correlation was measured | $\rho$ | factor $1/\sqrt{1-\rho^2}$ |
|---|---|---|
| median across the 32 committed conditions | $-0.90$ | 2.29 |
| the twin's committed design condition ([`twin_span_sweep.csv`](../../results/twin_span_sweep.csv), 60 MHz span) | $-0.9421$ | 2.98 |
| the bright condition of the pinning simulation above | $-0.9417$ | 2.97 |

The last row checks the first two: the pinning simulation's measured
$3.18 \pm 0.20$ agrees with the arithmetic's 2.97, to 7 per cent, at the
same fitted correlation of $-0.9417$.

These are floor numbers, not numbers of record. The producer is a
diagnostic that writes to `private/run_logs/` and moves nothing in
`results/`, so it runs on the declared support floor (Python 3.12, numpy
2.5) instead of the older versions that reproduce the committed CSV
digits. [`results/ENVIRONMENT_OF_RECORD.md`](../../results/ENVIRONMENT_OF_RECORD.md)
explains why those are two different statements, and the producer stamps
the versions it ran under into every row it writes.

## Breaking a degeneracy by design

Two Lorentzian widths in one line, a collisional one and a laser one,
convolve to their sum exactly. At a fixed condition this is an exact
degeneracy, not one managed with priors: the sum is measurable and the
split is not, at any signal to noise. Six injected values confirm it, the
recovered sum tracking truth to a part in a thousand while the split
wanders.

No fit breaks that degeneracy. A change to the experiment does: the
collisional width scales with density and the laser width does not, so a
temperature ladder makes both widths identifiable. Injecting 0.600 MHz on
the ladder already in this archive returns 0.599 with a spread of 0.013
(`tests/test_gamma_l_identity.py`). The lever was already in the data. The
question was which measurements to compare, not which fit to run.

More generally, two quantities that reach the data only through their
product cannot be separated by any fit at a fixed setting: a control
scaling one factor and not the other turns repeated measurements into a
line instead of a point, with the two factors as slope and intercept.

No such control exists within one *platform* for the *Gaussian* laser width
against the collisional Lorentzian, which is a different pair from the two
Lorentzians above and is the one that correlates at
[-0.9411](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:cell:corr_laser_coll_5traces").
The search was
run over acquisition settings, not assumed:
[`twin_span_sweep.csv`](../../results/twin_span_sweep.csv) rebuilds it in
the [digital twin](the-digital-twin.md) from a named committed condition.
The correlation between the laser and collisional widths moves by 0.0075
when the span widens from 60 to 300 MHz and by 0.0000 at ten times the
repeats, because a Lorentzian core inside a Gaussian envelope exchanges
the same way at every sample size. Repeats buy precision as sampling
predicts, a factor 3.16 at ten times the traces, while widening the span
costs a factor 2.72 at fixed points per trace, since the same points
spread over more baseline. Among the acquisition settings the asymmetric
knob does not exist, which is why the pinning approach above is used
instead.

**The scope of that sentence is the acquisition settings, and a platform
change is a knob it never searched.** The sweep behind it varied the span and
the repeat count inside one vapour cell. Changing where the atoms are changes
the width budget term by term, and asymmetrically:

| platform | collisional | transit | what it isolates |
|---|---|---|---|
| vapour cell | large, set by the vapour curve | set by the waist and the temperature | nothing on its own |
| magneto-optical trap, 150 uK | about a thousandth of the cell's | a sixteen-hundredth | the laser width alone, against a natural width this record fixes at 210 sigma |
| molasses, 20 uK | about a three-thousandth | a four-thousand-five-hundredth | the same, colder and thinner |
| vapour-filled fibre | identical to the cell's, same vapour and temperature | different, and set by a manufactured mode diameter | the collisional width, and with it the cell's own unmeasured waist |
| trapped guided sample | negligible | not a crossing at all | the light shift, as a displacement |

**Both transit ratios are waist-free**, the square root of the temperature
ratio with the beam radius cancelling, which is why they are a property of the
platform and not of the optics. A figure taken by dividing one platform's
transit by another's at a *different* waist is not that property, and an earlier
form of this row carried such a figure.

The cold rows are the strongest and the vapour-filled fibre row is the one that
reaches the waist.

**The rung, because this table is a ranking and not a result.** Every entry is
a closed form evaluated at a committed cell, rung 2. The twin has not fitted
any of these arms jointly, so nothing here is a forecast and no error bar
belongs to it. Neither is available inside a cell at any
acquisition setting, which is why the sentence above is a statement about a
subspace and not about the problem.

## The trapped regime, where the ramp stops being the observable

Every degeneracy above is stated for atoms that fly through the beam. A sample
held by the probe itself, which the guided arm has no choice about because
gravity clears an untrapped atom out of a 19 micron mode in about two
milliseconds, changes three of them at once. The derivation is in
[the ramp chapter](../methods/03_the_ac_stark_ramp.md): the shift weight
becomes the free ramp times a Boltzmann factor, and it reduces to the free
ramp exactly when the trap depth goes to zero.

**The transit degeneracy disappears, because the transit does.** The
correlation of
[-0.958](../../results/identifiability.csv "ref:identifiability:corr:gamma_coll_transit")
between the collisional width and the transit is a
correlation between two terms of a crossing-time kernel. A trapped atom does
not cross the beam, so the kernel is not a transit at all and
`constants.transit_fwhm_from_w0`, which is a Maxwell-Boltzmann flux-weighted
crossing, is the wrong function for those rows. What replaces it is the trap's
own motional structure.

**The shift stops being a shape and becomes a displacement.** The spread of
sampled shifts is $k_BT/U_0$ of the shift itself, and because the depth and
the shift are the same light the power cancels: the sample temperature alone
sets it. At a microkelvin the line is homogeneous to a few parts in a
thousand, and the third cumulant falls by about a million, so the asymmetry
channel closes and the whole light shift arrives in the line centre.

**And that hands the problem straight back to the free centre.** The section
above shows a per-trace free centre removing the first-order term of the ramp
exactly while leaving a second-order residue, which is what makes the profile
quartic at the boundary. When the ramp collapses to a displacement there is no
residue left: a free centre absorbs the shift at *every* order, not merely the
first. So the trapped configuration is not self-evidently better. It is better
only when the centre is referenced, by a lock that does not drift within the
comparison or by a power ladder whose slope the free centre cannot span. The
exchange is a clean, strong channel wholly dependent on the reference,
against a weak, contaminated channel that needs none.

## The beam waist is the one input this bench takes from outside itself

Nearly every other quantity here is calibrated by the system itself, from the
same traces the physics is fitted to:

| quantity | the observable that returns it | state |
|---|---|---|
| absolute frequency | the two shift-immune hyperfine pairs, from ground-state $A$ constants | in use |
| relative frequency, and the scan's non-linearity | the modulator's comb teeth at $k f_\text{mod}$, one ruler per trace | in use |
| gas temperature | the Doppler pedestal's width, which goes as $\sqrt{T}$ | designed, [chapter 5](../methods/05_the_frequency_ruler.md) |
| retro power ratio $\rho$ | the pedestal's area against the narrow line's, $4\rho/(1+\rho^2)$ | designed, same trace |
| isotope consistency | the width ratio $\sqrt{m_{85}/m_{87}}=0.988442$, parameter-free | available |
| density | the vapour-pressure law with the collisional ladder over it | in use |
| lock drift | the acquisition-order regression against a drawn rung order | in use |
| laser noise, band by band | a fast block's tooth clock sampling the band the slow blocks integrate | designed |
| magnetic field | the quadratic-Zeeman injector | designed |
| **the beam waist $w_0$** | **nothing** | **from an external measurement** |

The waist is measured once, on the predecessor laser, and every absolute result
here is a bound because of it. It is the last quantity on the bench still taken
on trust, and the case for measuring it inside the system is that everything
around it already is.

### The waist appears in every observable, with a different exponent

`results/waist_ladder.csv` carries these and fits each slope back against the
derivation of [methods chapter 3](../methods/03_the_ac_stark_ramp.md):

| observable | goes as | confounded with |
|---|---|---|
| transit width | $w_0^{-1}$ | the collisional width at $-0.958$, and a per-block laser width |
| light shift $S_0$ | $w_0^{-2}$ | $\Delta\alpha$, and a free centre per trace |
| two-photon Rabi frequency | $w_0^{-2}$ | the drive calibration |
| axial collection ratio | $w_0^{-2}$ | the optics |
| excitation cycles per crossing | $w_0^{-3}$ | the transit time |
| rate per atom | $w_0^{-4}$ | density and detection efficiency |
| saturation parameter | $w_0^{-4}$ at fixed power | hyperfine pumping, which the temperature ladder separates |

Different powers of one knob is exactly the structure this page says turns
repeated measurements into a line instead of a point. What has been missing is
not the leverage but the inversion: the waist has never been a free parameter.
`fit_transit` exists in three fitters and no caller in this repository has ever
passed it `True`, which by the switch rule makes the waist an untested
assumption and not merely an unmeasured one.

### One exact cancellation, which is where to start

Since the transit goes as $\sqrt{T}/w_0$ and the shift as
$\Delta\alpha(1+\rho)P/w_0^2$,

$$\frac{S_0}{(\text{transit})^2}\ \propto\ \frac{\Delta\alpha (1+\rho)P}{T},$$

and **the waist cancels exactly**. So the same data that cannot pin $w_0$ can
return $\Delta\alpha$ without it, provided $T$ and $\rho$ come from somewhere
else, which is precisely what the Doppler pedestal supplies from one wide
trace. Run the other way, with $T$ known, the transit width *is* a waist
measurement. Two channels, one consistency test, and the headline quantity no
longer inherits the waist it is currently bounded by.

**And this is one member of a family, not a lucky ratio.** Eliminating $w_0$ is
a linear condition on a monomial's exponents, so the set of such combinations
is a null space and can be enumerated. Two facts make the family small enough
to write down. **Beam quality enters this model in exactly one place**, the
Rayleigh range $z_R = \pi w_0^2/(M^2\lambda)$ and so the collection ratio.
Every other term is already free of it. And **the transit is the only term
carrying an odd power of $w_0$**, everything else carrying even powers, so
$(\text{transit})^2$ is the universal unit in which the waist divides out.
Verified at three waists crossed with three beam qualities, agreeing to machine
precision at all nine:

| combination | returns | free of |
|---|---|---|
| $(\text{transit})^2/\sqrt{s}$ | the two-photon rate coefficient | $w_0$, $M^2$ |
| $S_0/(\text{transit})^2$ | $\Delta\alpha(1+\rho)P/T$ | $w_0$, $M^2$ |
| $\sqrt{\kappa_2}/(\text{transit})^2$ | the same, through the **width** channel | $w_0$, $M^2$ |
| $\gamma_\text{coll}(\text{transit})^2/\text{area}$ | $\beta_\text{self}$ with the **density cancelling** | $w_0$, $M^2$, $N$ |
| $z_\text{ratio}/(\text{transit})^2$ | proportional to $M^2$: a beam-quality meter | $w_0$ |

The third matters more than the second: they carry identical physics, but this
archive's fitted shift sits at zero while the excess width is the channel the
record measures as carrying several thousand times the third cumulant's
information. The fourth exchanges the vapour-pressure law's density-scale
systematic for the collection chain's own calibration, which pays off only once
that chain is measured. The fifth is the answer to the beam-quality question
that no function here used to carry.

### Rounds of joint fits, in the order that breaks the confounds

1. **The wide trace first.** One gigahertz-wide scan returns $T$ and $\rho$
   together from the pedestal, needs no lock quality and no new hardware, and
   replaces two external numbers with two measured here.
2. **The density ladder separates the transit from the collisional width.**
   Across the archive's own temperatures the collisional width moves by a
   factor of fifty-two and the transit by 1.08, so the pair that correlates at
   $-0.958$ at one condition is separated by the ladder. This is the same
   argument that already makes the two Lorentzian widths identifiable.
3. **A cold arm separates the transit from the laser width.** In a trap or a
   molasses both the collisional width and the transit fall away and the laser
   width stands alone against a natural width fixed at 210 sigma.
4. **The cusp carries shape information a Gaussian cannot imitate.** The
   two-sided exponential and the Voigt branch differ by a large margin in this
   record's own fits, so the transit is not only an amplitude in the width
   budget.
5. **Then free the waist and fit everything at once**, with $T$ and $\rho$
   pinned by step 1, the ladder from step 2, the cold arm from step 3, and
   $\Delta\alpha$ either free or held at the sum-over-states value, both ways
   round. The two answers must agree, and the disagreement is the result.

### And the strongest lever is that the waist belongs to the beam, not the line

A fixed lens focuses a fixed input beam to $w_0=\lambda f/\pi w_\text{in}$, so
the waist goes as the *wavelength* and every two-photon transition the same
source reaches shares one $w_\text{in}$. The reachable set is catalogued in
[`FUTURE_TRANSITIONS_titsapph.md`](../FUTURE_TRANSITIONS_titsapph.md), and the
transit ratios among them carry no free parameter at all:

| upper state | two-photon $\lambda$ | transit, relative to 5S-6S |
|---|---|---|
| 5D | 778.10 nm | 1.2767 |
| 7S | 760.13 nm | 1.3069 |
| 6S | 993.42 nm | 1 |
| 4D | 1033.30 nm | 0.9614 |

Four measured transits over-determine one input radius, and the residual is the
test. Each transition also carries its own $\Delta\alpha$, so the light shifts
give a second family over the same waist. The $n\mathrm{D}$ states add a knob the $n\mathrm{S}$
states do not have: a tensor polarizability, hence a dependence on the drive's
polarisation angle that the scalar $S$ states are blind to, which separates the
geometry from the atomic structure again.

### What the inventory above overstates

**"The waist is the only one still taken from outside" is false**, and the list
of others is not short: the differential polarizability itself, from a sum over
states with literature matrix elements, the natural width from a measured 6S
lifetime, the vapour-pressure law from published correlations about twenty per
cent apart, the collection lens focal length and image distance with one of them
a recollection, and the beam quality, which no function here carries at all. The
defensible claim is narrower and is the one to keep: **the waist is the only
apparatus *geometry* term not calibrated inside the system, and the differential
polarizability the only *atomic* one that matters.** Those two are exactly the
pair the ratio below separates, which is what makes the ratio worth having.

### The archive is an L, and both of its axes are known

The design is in the manifest's own `role` column, and reading it settles what
the ratio below costs. One arm sweeps the power at a pinned temperature and the
other sweeps the temperature at a pinned power, sharing a vertex:

| arm | traces | temperature | power | peaks |
|---|---|---|---|---|
| power sweep | 101 | 130 C, pinned | 25 to 225 mW | all four |
| temperature sweep | 62 | 70, 90, 110 C | 225 mW, pinned | all four |

So the power and the temperature are not quantities the archive fails to
measure. **They are the two axes the design varies**, known to 0.5 and 1 per
cent, and every width in the model has a different exponent along them:

| term | $\mathrm{d}\ln/\mathrm{d}\ln P$ | $\mathrm{d}\ln/\mathrm{d}\ln T$ |
|---|---|---|
| the light shift $S_0$ | 1.00 | 0.00 |
| the transit width | 0.00 | **0.50** |
| the collisional width, through $N(T)$ | 0.00 | **22.42** |
| the laser and natural widths | 0.00 | 0.00 |
| the saturation companion | 1.00 | 0.00 |
| the amplitude | 2.00 | 22.42 |

**So the transit is an observable, and the temperature arm is what makes it
so.** The $-0.958$ correlation is a property of a fit at a single temperature.
The density runs as the 22nd power of the temperature where the transit runs as
its square root, a separation of a factor of 45. The power arm then moves
the shift alone, with every width standing still. Three exponents across two
axes, and the design was already in the data.

**What the ratio costs, propagated.** The relation
$S_0/(\text{transit})^2 = \Delta\alpha(1+\rho)P/T$ is exact, the waist cancels,
and inverting it at the vertex returns the record's own differential
polarizability to machine precision at waists of 40, 64 and 85 microns alike.
The apparatus terms it takes from outside are exactly three:

| term | relative |
|---|---|
| the power, the drive's own stability | 0.50 per cent |
| the temperature, on the absolute scale | 1.0 per cent |
| $(1+\rho)$, from the retro ratio's stated error | 2.1 per cent |
| **the apparatus floor** | **2.3 per cent** |
| the waist | **nothing, by construction** |

**That third row is softer than it looks, and it is the one to watch.** The
retro ratio is an assumption, 0.94, which this record's own epistemic ledger
marks as never informed by these data, and the 2.1 per cent is the spread
attached to that assumption and not a measured error. The measurement that
would replace it is the narrow-to-pedestal area ratio, which needs a scan wide
enough to see a 931 MHz pedestal where the archive's traces span under 100. So
the apparatus floor above is conditional on an unmeasured quantity, and **the
same wide scan that measures the pedestal measures $\rho$**, which is one more
reason it is the first thing a campaign should run.

**The retro ratio is now the largest apparatus term**, twice the power and the
temperature together, so it and not the waist is what this route would next pay
to measure. Carrying the observables, a shift known to 2 per cent and a transit
to 1 gives the polarizability to 3.7 per cent, and to 1 and 0.5 per cent gives
2.7.

**The pedestal's retro ratio is two-valued.** The area ratio is
$4\rho/(1+\rho^2)$, which is symmetric under $\rho\to1/\rho$: 0.80 and 1.25
both give 1.9512. One wide trace therefore returns $\rho$ or its reciprocal. The
branch is settled by knowing which beam is the weaker, which is a bench fact and
not a fit output.

**Half the inventory is designed and not taken.** The pedestal supplies the
temperature and the retro ratio in principle, and in the 2025 archive it cannot:
the pedestal is 942 MHz wide and the windows span 85, so every trace samples its
flat top and the baseline takes it up as an offset. Listing a designed calibration beside a
working one overstates what the bench has done.

**And the transition ladder's ratios carry an assumption, not zero parameters.**
$w_0=\lambda f/\pi w_\text{in}$ needs the input radius to be the same at every
wavelength, and a titanium-sapphire cavity's own mode radius is not. If it goes
as the square root of the wavelength then the waist does too, and the transit
ratios move from 1.2767 to 1.1299 at 5D and from 1.3069 to 1.1432 at 7S, a
thirteen to fourteen per cent difference that is larger than the effect the
ladder is meant to measure. The defensible form fits the input radius as a
one-parameter power law in the wavelength and reports the exponent, which four
rungs still over-determine. A smaller term the first statement also ignored is that the
focusing lens is not achromatic, so its focal length moves about one per cent
across the family in the same direction.

### The wavemeter can be calibrated by the atoms as well

The peak labels come from an uncalibrated wavemeter, which is why they identify
lines and do not measure them. Two transitions the same laser reaches turn that
into an interpolation.

The D1 line at 794.9789 nm is an absolute optical frequency known to well under
a megahertz, it lies inside the laser's own band, and this bench already passes
795 nm because that is the leg it collects. The 5S to 4D two-photon at 1033.30
nm has its interval from the same NIST term energies the polarizability module
uses. **The drive at 993.42 nm sits 83 per cent of the way between them**, so
its absolute wavelength is interpolated between two knowns instead of
extrapolated from one.

Two anchors matter because a wavemeter carries two error terms and one anchor
fixes only the smaller. A five-picometre offset is 1.5 MHz on the optical axis.
A one-part-per-million scale error is 302 MHz. **The scale is the term that
hurts, and it takes two points to see it.**

The obstacle is optics, and it is stated here instead of left to the bench. This
record's own transition table puts 993.4 nm at the edge of the 700 to 1000
range and inside 950 to 1050, 1033.3 only in the second, and 795 only in the
first. So the two anchors cannot be taken in one configuration, and the
calibration takes two sessions, and the repeatability of the wavemeter across a
mirror change enters the error budget of the result.

### The beam quality is a second axis, and no function here carries it

Every waist-dependent quantity in this repository assumes a diffraction-limited
beam, and the bench has a reason not to be one. The drive passes a modulator
whose 3 mm clear aperture is sourced from the manufacturer's table. The 1.5 mm
input radius beside it is not pinned by the record, and a viewer-card
observation of clipping there is a recollection and not a measurement. Taken
together they put the aperture at the $1/e^2$ radius, transmitting 86.5 per
cent, which is the most-clipping end of what the pair admits and not a measured
ratio. The open item and what would close it are in
[plan chapter 12](../plan/12_open-apparatus-items.md).

Beam quality enters in one place, the Rayleigh range $z_R = \pi w_0^2/(M^2 \lambda)$,
and therefore everything axial. The window ratio the collection
optics impose goes as $M^2/w_0^2$, so **the strain falls on a small waist
with a poor beam**, which is the opposite end from where a reader looks. Against
the two sign reversals the record carries, the second cumulant past a window
ratio of 1.69 and the third past 1.117, the beam quality that reaches the third
cumulant's reversal is $M^2=3.17$ at 55 microns, 4.29 at 64 and 7.56 at 85. The
damage arrives earlier than the reversal: at 55 microns the third cumulant keeps
86 per cent of its value at $M^2=1$, 69 at 1.5, 48 at 2 and 26 at 2.5.

**So a working range for the waist is a region in $(w_0, M^2)$ and not an
interval in $w_0$.** The convolution condition holds across 55 to 85
microns with room to spare, the kernel spread over the collected region running
1.75, 0.98 and 0.32 per cent and reproduces the record's own measured 1.0 at 64. The collection
window is what strains, and it strains at the small end. A range of 55 to 85
microns with $M^2$ under about two keeps every term inside its licence with a
factor of two to spare.

**None of this is a forecast.** Every relation above is closed form, rung 2.
The twin has not fitted a multi-transition arm, `fit_transit` has not been
thrown in a producer, and the knife-edge measurement remains the cheapest
single answer to the question. What the programme offers is that the knife edge
would then be a *check* on a number the system had already produced, instead of
the only number there is.

### The modulator is a knob this page never listed

Every knob above moves the light shift and the widths together, which is why so
few of them separate anything. The modulator does not. A phase modulation
redistributes the drive among teeth and leaves the time-averaged intensity
alone, so the light shift, the collisional width, the laser width and the
transit are all unmoved, while each tooth is driven at its own share $f$ of the
power. The two-photon rate goes as $f^2$, so the saturation companion does too.

The shares follow from the comb [the ruler chapter](../methods/05_the_frequency_ruler.md)
measures, heights $0 : 1.00 : 0.69 : 0.15$ at $k = 0, \pm1, \pm2, \pm3$ with the
carrier running 0.360 to 1.188 of the first order. A two-photon height goes as
the share squared, so the tallest tooth carries **0.18 to 0.20** and the carrier
0.12 to 0.20. At those shares the saturation companion sits **25 to 31 times**
below the unmodulated line's, at otherwise identical conditions. Nothing else in this model separates saturation from the Lorentzian
sum, which it otherwise joins and does not break.

**And the shares are measured, not predicted.** A two-photon height goes as the
share squared, so each tooth's share is read from the same trace it is used on.
That matters here because the polarisation axis into the modulator was tilted
deliberately, to stop the carrier burying the other teeth, so the shares do not
follow $J_k^2$ and a predicted abscissa would be wrong. A measured one is correct.

**What limits it is the width scatter and not the physics.** The predicted
narrowing is 60 to 72 kHz against a single-block width scatter near 88, so with
the traces the archive holds the test is about 1.3 sigma a line and 2.5 pooled
over four. Real, the right sign, and not decisive here. What makes it decisive
is the fixed lock, which is what the scatter is made of.

### And the polarisation is not a detail of the ruler

For this line only rank 0 survives: rank 1 is absent by the exchange symmetry,
since both photons come from one laser, and rank 2 is zero for $J = 1/2$. Rank 0
goes as $\mathbf{e}_1\cdot\mathbf{e}_2$, so **the Doppler-free rate carries
$\cos^2$ of the angle between the forward and retro polarisations**, and the
standing-wave contrast carries $\cos$ of it.

Two consequences for this page's subject. Amplitudes are **not** comparable
across traces whose polarisation differed, which rules out using them as a power
meter beyond excluding a gross setting. And the light shift is set by the total
intensity, which is polarisation-independent, so the modulator lever above
survives a varying axis even though amplitude comparisons do not.

## Leverage in a channel

Identifiability asks whether the data determine a parameter. A prior
question is whether the observable used is even sensitive to it: a channel
can be correctly modelled, well measured, and still nearly empty of the
parameter. The relevant number is the derivative of the observable with
respect to the parameter, in units of the observable's own scatter, its
leverage. Appearing in the forward model is not leverage. Constraining
such a channel harder adds almost no information.

### A summary statistic is not an estimator, and the bar differs

A statistic used in a joint fit is compared against its own forward
prediction. It does not have to converge to anything. Asking it to is a
category error that has twice cost this record a usable channel. The windowed
fifth and seventh cumulants of a Lorentzian-cored line grow without bound as
the window widens, which struck them as estimators of the ramp's own cumulants.
As statistics they are neither redundant nor empty. Measured on the production
path, adding them to the excess width and the third cumulant **raises the
sensitivity matrix's rank from three to four and nearly quadruples its second
singular value**, and the seventh order at an intermediate window is the only
statistic in the set that probes the widths hard while still carrying the
shift.

**And the ratio of the fifth to the third is a systematic discriminator, not an
empty number.** It is shift-free, which is why it was read as carrying no
information. Measured across a twenty-four-fold span in the shift it sits at
minus forty, stable to two and a half per cent, and negative while the third
cumulant is positive. A sloped baseline, a detection nonlinearity or an
unresolved neighbour carries its own value of that ratio, generically not minus
forty, so the pair discriminates an instrumental asymmetry from the ramp's.
The earlier reading that no ratio among the odd orders can see a common
asymmetry holds only for their magnitudes and not for their signs.

### But on this archive's noise the odd ladder is not a channel at all

Everything above is about the signal and is silent about the noise, and the
noise settles it. Measured on the twin's world under the correlation time
`results/noise_model.csv` reports, over the eight orders and three windows, the
statistics split exactly by parity at a per-trace signal-to-noise of three:
[21](../../results/moment_admission.csv "ref:moment_admission:n_admitted:") of
42 are admitted and they are precisely the even orders and the even ratios. The
second cumulant at the six-megahertz window carries
[1667](../../results/moment_admission.csv "ref:moment_admission:snr_k2:6") per
trace. The third carries
[0.00543](../../results/moment_admission.csv "ref:moment_admission:snr_k3:6"),
and `k5/k3`, `k7/k5` and `k9/k7` are refused at every window. A windowed
cumulant of pure noise is largest exactly where the signal is smallest, so a
refused statistic averaged into a joint fit does not dilute the answer, it
inverts it.

Two things follow that a rank count hides. The admitted set carries about
[2.85](../../results/moment_admission.csv "ref:moment_admission:effective_rank_admitted:")
independent numbers and not twenty-one, so "three equations or one equation
three times" is answered, and the answer is nearer three. And the same measure
over every statistic including the refused ones reads
[8.42](../../results/moment_admission.csv "ref:moment_admission:effective_rank_all:")
which is higher, because pure noise is nearly full rank. Quoting that one as the
information content is the trap this page would otherwise set.

The odd orders stay in the model's order tuple because they are the shift
channel and a campaign at a larger light shift reads them. On the 2025 archive
a fit drops them on their measured signal-to-noise, never on their name.

### rho and Delta-alpha are exactly degenerate in the shift, and only one channel breaks it

The light shift enters as $S_0 \propto (1+\rho) \Delta\alpha P/w_0^2$, so
every observable built on the shift constrains the product $(1+\rho)\Delta\alpha$
and no amount of shift data separates the retro's power ratio from the
differential polarizability. The fringe contrast, $2\sqrt{\rho}/(1+\rho)$,
carries $\rho$ alone, and it is the only observable in this archive that does.
So the fringe channel is not a correction to a lineshape: it is what makes
$\Delta\alpha$ reachable at all.

It has one structural virtue and one structural defect. The virtue: the
contrast is a ratio in which the local beam radius cancels when the two beams
are concentric, so $M^2$, the largest open geometric unknown on this bench,
does not enter it at all, at any waist. **That is an algebraic identity and not
a simulation result**, and it is worth saying which: with the beams concentric
the return intensity is $\rho$ times the forward one at every point, so the
ratio is $2\sqrt{\rho}/(1+\rho)$ everywhere and the local radius has already
cancelled before any atom is drawn. The Monte Carlo returns it across the whole licensed grid, which tests the
implementation: the cell grid's
[2.98e-08](../../results/fringe_rho_recovery.csv "ref:fringe_rho_recovery:max_rho_bias_clean:")
residual is floating-point noise. What the grid does measure is everything that
breaks the identity: the retro offset a tilt implies, and the polarisation. The defect: the contrast is
**stationary at $\rho = 1$**, its derivative vanishing identically there, and
this bench sits near that point. At $\rho = 0.94$ a ten per cent determination
of $\rho$ needs the contrast measured to about $1.5\times10^{-3}$. At
$\rho = 0.5$ the same determination needs only $1.6\times10^{-2}$.

**The design consequence is concrete, and it costs signal: unbalance the retro on
purpose.** Attenuating the return beam moves the contrast's derivative by an
order of magnitude and turns a stationary channel into an informative one,
and it costs signal, since the Doppler-free rate goes as the ratio itself
([methods 3](../methods/03_the_ac_stark_ramp.md)), a factor 1.9 at one half,
and the shift being measured, which goes as one plus the ratio, a factor 1.3. It
belongs to a campaign and not to the 2025 data, which is why the archive's
$\Delta\alpha$ stays where the record puts it.

### Matching the summary statistic to the perturbation

A one-sided perturbation moves the line's centre and asymmetry strongly
while barely changing its width, since a symmetric summary of an
antisymmetric perturbation is insensitive by construction. A width can be
the natural-seeming handle and the wrong one: in this repository the
light-shift term moves the composite width by a few kilohertz at its bound
but the line centre by a hundred and fifty kilohertz against an
eighty-eight kilohertz block scatter, a factor of forty in the same fit.
The fixed natural linewidth alone, 3.493 ± 0.013 MHz on the transition axis
from the measured 6S lifetime of 45.57 ± 0.17 ns
([Gomez 2005](../lit/gomez2005.md)), is about 0.65 of the observed 5.4 MHz
composite, a ratio of two defined widths, not an additive share, since a
convolution's width does not decompose additively.

The practical order is to build the component budget, compute the leverage
in each channel, and only then ask whether the parameter is identifiable in
the channel that carries it.

## What a free centre removes, derived

The AC-Stark ramp of [the light shift](the-inhomogeneous-light-shift.md) is a shift density $w(u) = 2u$ on $[0,1]$, scaled by $S_0$. Writing the observed profile as $P(\nu \mid S_0) = \int_0^1 P_0(\nu - S_0 u) w(u) \mathrm{d}u$ keeps every moment used below a moment of $w$, which is finite by construction. No moment of the observed line enters, so the Lorentzian's divergent cumulants (see [the ramp chapter](../methods/03_the_ac_stark_ramp.md)) never do.

Expanding to second order, $P = P_0 - \tfrac{2S_0}{3}P_0' + \tfrac{S_0^2}{4}P_0'' + O(S_0^3)$. The first-order term is exactly the first-order form of a translation. A per-trace free centre spans that direction, and the choice $c = 2S_0/3$ removes it identically. What a fit can still see is the residual after that absorption, $P - P_0(\nu - \tfrac{2S_0}{3}) = \tfrac{S_0^2}{36}P_0''$, where $1/36$ is half the variance of $w$, $\mathrm{Var}[u] = 1/18$.

Two consequences follow without any fit. The residual is second order in $S_0$, so the derivative of the observable response vanishes at $S_0 = 0$: the Fisher information for the shift is zero at the boundary and the log-likelihood is quartic there. That is why the bound is one-sided and the profile is flat at the boundary. (A coefficient linear in the data is negative half the time under a null at the boundary, so a rail rate near one half is that argument's expectation there. The coverage study's zero-shift cell rails 6 per cent of the time in the nominal arm, the one the postscript finds the real data behave like, and 14 per cent in the over-dispersed arm. The postscript records the discrepancy with one half as open.) And the width channel is even in $S_0$, so it cannot see the sign of the shift at any precision.

The size of what survives, computed by `scripts/run_identifiability.py` with `rb5s6s.lineshape.total_fwhm_mhz` at the archive's two fitted branches and never by prose arithmetic: at the predicted shift of [0.364](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz (envelope [0.316](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred_lo:shared") to [0.396](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred_hi:shared")) the line broadens by [7.23](../../results/identifiability.csv "ref:identifiability:width_signature_broadening_khz:cusp_branch") kHz at the cusp branch and [6.48](../../results/identifiability.csv "ref:identifiability:width_signature_broadening_khz:gaussian_branch") kHz at the Gaussian branch, on lines of [5.3179](../../results/identifiability.csv "ref:identifiability:width_signature_fwhm_mhz:cusp_branch") and [5.4036](../../results/identifiability.csv "ref:identifiability:width_signature_fwhm_mhz:gaussian_branch") MHz, so the centre pull the free centre discards is [33.6](../../results/identifiability.csv "ref:identifiability:width_signature_centre_over_width:cusp_branch") to [37.4](../../results/identifiability.csv "ref:identifiability:width_signature_centre_over_width:gaussian_branch") times the width signal. The pure-Gaussian estimate a withdrawn draft carried was about half of this, because the real line is about two thirds Lorentzian, and the two-branch cells above are the record's own.

**Which side the centre sits on is now a fitted choice, shown and not only
derived.** The expansion above is a statement about the forward
model: the ramp's density is $|s|$ on $[-S_0, 0]$, fixed by the beam geometry
and the polarizability, with no free shape anywhere in it. `fullmodel.fit_full`
carries the centre as a term, so the two regimes can be run against the same
trace. On noiseless data **both find the injected shift exactly**, and the difference
shows only in the spread across starts: four parts in $10^{14}$ with the centre
pinned against $1.2\times10^{-1}$ with it freed.

**That is the benign case, and quoting it alone understates the cost.** At the
archive's own noise level the free-centre fit is not merely start-dependent, it
is biased:

| noise | $S_0$, centre pinned | $S_0$, centre free |
|---|---|---|
| 0 | 0.36400 | 0.36400 |
| 0.004, the archive's | 0.36558 | **0.28530** |
| 0.020 | 0.36842 | **0.85509** |

against an injected 0.364. At the level these traces carry, freeing the centre
costs **twenty-two per cent, low**. At four times it the answer is wrong by
more than a factor of two, while the pinned fit is still good to one per cent.

So the operational rule, which this page could state only as a derivation
before. Pin the centre and the asymmetry is a prediction the fit must match.
Free it and the asymmetry is largely absorbed. Neither is wrong. **Fitting the
shift with a free centre and reporting its error as though it were pinned is.**

### What the estimator can and cannot take out, computed

A closed loop means something only where the world and the estimator carry the
same terms. `fullmodel.term_coverage` reports that split from the fitter's own
table. The two tables are maintained by hand. The census column that used to restate them is computed from them now, so the hand-kept text lives in one place and not two, as the census column it replaced
was. What it gains is sitting beside the code it describes, with a test
asserting every entry carries a reason and not a label. The split does not
close: six terms the world can generate cannot be fitted at all, each for a
stated reason. Beam quality is degenerate with the waist at fixed collection
ratio. The polarisation overlap scales the fringe contrast, which the profile
model does not carry. The radiation temperature, the cascade depletion, the
quantisation and the lock drift are each absorbed exactly by a free per-trace
parameter.

Asking the fitter to free one of those raises, and never pins it silently,
because **a pinned term the caller believes is free is how a recovery test reads
as a success it did not earn**. That is the failure mode this page's subject
keeps producing in new costumes, and it is worth naming once here: an
identifiability claim is a claim about a pair, the world and the estimator, and
a loop run through one term list proves only that the optimiser can invert a
function it was handed.

A note on two numbers this page and its neighbours quote. The split-against-total anisotropy is [0.0032](../../results/identifiability.csv "ref:identifiability:best_constrained_sigma:total_width") MHz against [0.0588](../../results/identifiability.csv "ref:identifiability:worst_constrained_sigma:split") MHz, a factor of [18.6](../../results/identifiability.csv "ref:identifiability:anisotropy_ratio:split_over_total"). [The statistics chapter](../methods/06_the_statistics.md) calls the same pair twenty-fold worse. The producer divides the unrounded sigmas and writes [18.6](../../results/identifiability.csv "ref:identifiability:anisotropy_ratio:split_over_total"). The two committed digits give a ratio a fifth of a unit smaller, which is what the campaign-projection figure prints from the same cells, and the difference is rounding, not physics.

## The exact Lorentzian-sum degeneracy

**Saturation joins this sum, it does not break it.** The two-photon Rabi
frequency broadens the homogeneous core, and that broadening is added to
$\gamma_\text{coll}$, so a fit carrying saturation has three terms entering as
one measurable total. Measured on sixteen moment statistics against six
parameters, the sensitivity matrix is formally full rank but with **two** null
directions, and the weakest is $\gamma_l$ against $\gamma_\text{coll}$ with the
Rabi frequency alongside them. The consequence is a design constraint and not a
curiosity: the moments are computed on an area-normalised profile, so they see
saturation only through its width, where it is degenerate. Its identifying
power is in the **amplitude against power**, which no moment carries and which
goes as the inverse fourth power of the waist, the steepest dependence in the
model. A joint fit over moments alone gives that lever up.

**The ruler's teeth are the lever that isolates it, and the ladder puts a number on it.** A phase
modulation holds the total intensity, so the light shift and every width are
the same on every tooth while the two-photon rate follows the tooth's share of
the drive: across the orders the archive's rulers admit the rate spans [5.50](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:ladder_rate_span:")
at one light shift, which no power ladder can do. Fitting one tooth with the
waist alone free and the companion unmodelled biases the transit by
[1.378](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:one_tooth_waist_only") ± [0.027](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:one_tooth_waist_only:err") per cent.
Fitting every usable tooth jointly with one shared Rabi frequency free returns
[-0.034](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:ladder_waist_only_omega_free") ± [0.061](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:ladder_waist_only_omega_free:err"), the bias gone, and holding
that frequency at the truth gives [-0.019](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:ladder_waist_only_omega_pinned") ± [0.018](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:ladder_waist_only_omega_pinned:err"), so the
ladder is not limited by the extra parameter. An arm with the Lorentzian width
free instead measures nothing here, [-0.17](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:one_tooth_gamma_l_free") ± [0.13](../../results/rf_saturation_ladder.csv "ref:rf_saturation_ladder:transit_bias_pct:one_tooth_gamma_l_free:err"), because
it absorbs the companion one for one, which is this section's degeneracy read
the other way round.

Every other case here is a degeneracy the data cannot resolve well. This
one is different: the mathematics makes it exact, and the implementation
once broke that exactness by accident.

![Lever map for the collisional and laser width components](../../figures/fig35_orthogonal_information.png)

*Which lever moves which width component: density resolves the collisional
width, and an independent laser diagnostic is the lever this record has
costed on the laser width. Without it the two add to a single measured sum,
and a waist ladder carrying different powers of the magnification into each is
the proposed second route.*

Lorentzians add: convolving one of FWHM $a$ with one of FWHM $b$ gives a
Lorentzian of FWHM $a+b$, exactly. If the laser's contribution is modelled
as a Lorentzian, the predicted line at a fixed condition depends on
$\gamma_{\rm coll}$ and the laser width only through their sum, and the
orthogonal direction is flat to machine zero. Any number reported for
$\gamma_{\rm coll}$ alone under that kernel marks only where the optimiser
stopped. A per-condition figure was withdrawn for exactly this reason
([the Voigt profile](voigt-profile.md)).

The code did not preserve that flat direction. It realised the sum
identity by convolving the two Lorentzians on a finite grid, and the grid
span was computed from the two widths separately, so grid truncation of
the Lorentzian tails made the predicted line depend on how a fixed total
width was split, by up to $3.7\times10^{-3}$ of peak. That size matters:
per-point noise here is $5.3\times10^{-3}$ of peak across about $10^4$
points, so a distortion at $3.7\times10^{-3}$ carries up to seventy sigma
of matched-filter leverage, enough for round-off alone to separate the two
widths confidently.

The fix imposes the identity instead of computing it: the laser width is
now added directly into the homogeneous width instead of convolved, exact
by construction and cheaper by one convolution, with a bit-identical guard
and a control confirming the Gaussian branch still moves under the same
transformation.

Density is what resolves the degeneracy here: the collisional part scales
with it and the laser part does not, so an estimator that varies density
separates them. The headline kernel result survived the fix almost
unchanged, while the per-condition number had no referent, and a density
ladder turns the exact degeneracy into one that is strong but finite. The
cost is visible in the correlation between $\beta_{\rm self}$ and the
shared laser width: $-0.82$ to $-0.89$ under the Gaussian kernel, $-0.91$
to $-0.98$ under the Lorentzian.
Measured in
[`results/kernel_identifiability.csv`](../../results/kernel_identifiability.csv),
which runs in seconds and needs no data.

### The collisional component across the archive

At a fixed condition the sum is all that exists, since the flatness is
algebraic, not statistical. Density moves one term of the sum and leaves
the other alone, which is why the collisional coefficient is estimated
across a temperature ladder instead of from any single condition, and why
the per-condition version was withdrawn.

Running that separation over the archive finds a component present at
every peak, by a nested likelihood ratio of 176 to 961 for one parameter on
its boundary, with peak-conditioned values of 0.315 to 0.449 MHz
(`results/kernel_k3.csv`), sized at 3.24 times the statistical error on a
matched footing (`results/kernel_budget.csv`): the model form, not the
noise, limits that coefficient.

This does not establish that the four peaks share one value, open at
$p = 0.097$, or what the component is (calling it the laser is a separate
claim, `results/kernel_k5.csv`), or that the model class is adequate, since
3.24 is only a sensitivity within the two forms tested. A residual check
finds a common cross-condition structure with no named mechanism and no
quantified effect on the coefficient (`results/kernel_k4.csv`). The lever
map above marks the one measurement that would settle its origin, still
untaken.

## The retro ratio and the polarizability, and the one channel that splits them

The peak shift goes as `S0 ~ (1 + rho) * Delta-alpha * P / w0^2`, so once the
waist is known the shift channel constrains only the product `(1 + rho) *
Delta-alpha`. **No amount of shift data separates them**: they enter through one
factor and a fit that reports both from the shift alone is reporting its priors.

**The fringe contrast is the one observable that carries rho and not
Delta-alpha.** A retro-reflected standing wave has contrast `2 sqrt(rho) / (1 +
rho)`, a function of the power ratio alone, so the fringe-resolved suppression
measured per waist and per quality factor is a rho measurement, not a
correction to one. With rho in hand, Delta-alpha follows from the product.
`rb5s6s.fullmodel.fringe_survival_mc` is where that measurement lives, and it
carries the beam quality, the retro tilt, the retro offset and the polarisation
overlap that `fringe_tail` does not.

**Consequence for any joint fit on this page**: rho and Delta-alpha are never
both free against the shift alone. Either one is pinned, or the fringe channel
is in the fit, or the result is stated as the product.

## Values that moved
Three figures on this page's subject were withdrawn or rebuilt. A
per-condition collisional-width split was traced to a grid-truncation
artefact rather than to physics. A background span sized on an assumed
signal retention was rebuilt once the true fraction was computed. And a
campaign-only bound that appeared to move across commits was traced to a
sample-count change landing on a discrete trim boundary in a nearly flat
profile direction. the private correction record carries each row with its
before and after.

### The collisional coefficient's apparent excess is the omitted Lorentzian

**This is the sharpest identifiability result the record holds, and it is a
committed cell and not an argument.** Fitted with the laser's Lorentzian
component pinned at zero, the collisional coefficient comes back at 0.0534
MHz per density unit, sixteen times the van der Waals anchor of 0.003383 and
far outside either error. Fitted with that component carried at the value the
kernel study measures, it comes back at **0.0057 plus or minus 0.0043, which
sits 0.54 of a sigma from the anchor**. The extra-homogeneous-component axis
alone moves the coefficient by 0.0477, which is nearly the whole apparent
excess.

**That setting is not a measurement of the coefficient**, and the reason is this
page's own subject. At a fixed condition the extra component is exactly
degenerate with the collisional width, since both are Lorentzian and Lorentzians
add, so it is identified only across the density ladder. The fit holding it at
zero puts a density-independent floor through the origin, which is the same
floor the lever test reports. The coefficient stays a bound, and what the setting
establishes is the size of a systematic. The component's origin is a separate
arrow: calling it the laser is an attribution this record classifies as not
established.

What does generalise is the reading: **an excess in a fitted parameter is
evidence about the model's term list before it is evidence about the physics**,
and the first place to look is an axis a model-form grid already spans.

### The third error bar is larger than the first

The same grid of refits measures the model-form systematic, across the
transit-kernel and sharing axes. On the collisional coefficient the
model-form spread is **0.0142 against a statistical error of 0.0043**, so the
choice of kernel form costs more than three times what the data's own noise
does. Any sigma quoted on this page against a theory anchor carries all three
error bars or it is not a sigma. A gap divided by the anchor's error alone
overstated this one by a factor of fifty before the crosscheck was read.

### The reduced chi-squared carries its own uncertainty

For $\nu$ degrees of freedom $\mathrm{Var}(\chi^2) = 2\nu$, so
$\mathrm{sd}(\chi^2_\text{red}) = \sqrt{2/\nu}$. At the several thousand
degrees of freedom these fits carry that is about 0.02, so a reduced
chi-squared of 0.85 is several sigma below one and the error model is
miscalibrated and not fluctuating. **A difference between two points of one
profile on the same data does not carry $\sqrt{2\nu}$**, because the
fluctuation is common to both and cancels, which is why an interval can be read
at unity while the absolute statistic is uncertain by tens. Conflating the two
is the error that produced an uncalibrated waist interval on this page's own
subject.

## What can go wrong

The failure that matters is mistaking a converged fit for a determined
parameter: an optimiser always returns a point, a covariance matrix always
returns error bars, and neither is evidence the data chose the answer. A
near-unit correlation between two parameters signals that their individual
values are not results.

A local covariance is a quadratic approximation at a single point,
describing the valley only near where the fit stopped. If the likelihood
has more than one minimum, the covariance around one says nothing about
the other, and its error bars imply a global statement the analysis did
not make.

An implementation failure can imitate non-identifiability exactly, through
a parameter railed at a bound, a mis-scaled Jacobian, or a wrong
derivative step size, all artefacts of the code and not genuine
degeneracy, distinguishable only by examining the model. Resolution is
also easy to overstate: adding data that moves the degenerate combination
only a little makes the valley shorter without making it narrower, and a
parameter that goes from unmeasurable to poorly measured is still not a
measurement.

## Try it

How similar the line looks when you widen the collisional part against
when you widen the laser part. An overlap near one means the data cannot
tell the two changes apart.

```python
import numpy as np
from rb5s6s import composite_profile, transit_fwhm_from_w0

t = transit_fwhm_from_w0(64e-6, 130.0)
grid = composite_profile(0.60, 1.40, t)[0]

def shape(gc, sl):
    g, p = composite_profile(gc, sl, t)
    return np.interp(grid, g, p / p.max(), left=0, right=0)

d_gamma = shape(0.66, 1.40) - shape(0.54, 1.40)
d_sigma = shape(0.60, 1.47) - shape(0.60, 1.33)
overlap = (d_gamma @ d_sigma) / np.sqrt((d_gamma @ d_gamma) * (d_sigma @ d_sigma))
print(f"overlap of the two shape changes: {overlap:+.3f}")
print("near +1 means one can be exchanged for the other almost freely")
```

Every snippet on these pages runs in `tests/test_wiki_snippets_run.py`, so
one that stops working fails the suite instead of sitting here misleading a
reader.

## Further reading

- A. Raue et al., "Structural and practical identifiability analysis of
  partially observed dynamical models by exploiting the profile likelihood",
  *Bioinformatics* **25**, 1923 (2009): the source of the distinction and the
  profile-based diagnostic used on this page.
- [The profile likelihood](profile-likelihood.md), the tool that maps the
  valley.
- [Injection-recovery testing](injection-recovery.md), for whether the
  intervals a degenerate problem produces actually cover.

## See also

- [The AC-Stark light shift](../quantities/ac-stark-light-shift.md) and
  [collisional self-broadening](../quantities/self-broadening.md), the
  quantity dossiers with their own limiting degeneracy and the measurement
  that would break it.
- [The profile likelihood](profile-likelihood.md), which maps a degenerate
  valley directly instead of approximating it by an ellipse.
- [Injection-recovery testing](injection-recovery.md), for whether a
  degenerate problem's intervals actually cover.
- [The joint fit](joint-fit.md), for what sharing a parameter across
  repeats does and does not do to a shared degeneracy.
- [Information criteria](information-criteria.md), for comparing models
  instead of separating a model's own parameters.

---

[← Information criteria](information-criteria.md) · *Statistical inference, 5 of 9* · [Reduced chi-squared →](reduced-chi-squared.md)
