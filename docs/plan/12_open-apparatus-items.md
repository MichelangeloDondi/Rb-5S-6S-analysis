*Chapter 12 of 12 of [the PLAN](../PLAN.md)*

This chapter builds on every chapter that quotes an APPARATUS number, chapters 3, 4 and 9 above all and sets out the open list, the cost of closing each, and the span the forecast uses in place of a value. The measurements that are already made, which are chapters 3 to 11.

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## 13. Open APPARATUS items

Every cell-side number in this PLAN that nobody has MEASURED is listed here,
with what it would change and how the forecast proceeds without it. The
guided-platform unknowns live in the fibre thread, per the skip promise
[the big picture](../BIG_PICTURE.md) declares. **An open item is
spanned, never assumed**, and the span lives in a committed producer so a
reader can see how far the answer moves across it.

This chapter exists because the alternative failed. On 2026-08-28 a
forecast of the next campaign used the 2025 archive's lock drift rate as
though it described the repaired lock. The APPARATUS had changed, this PLAN
already said so in two chapters, and the forecast contradicted the PLAN
instead of reading it. A list of what is genuinely unknown is what stops the
next session inventing a value, or asking for one nobody has.

| item | status | what it changes | how the forecast proceeds |
|---|---|---|---|
| **repaired lock, residual drift** | not MEASURED. The lock was repaired 2026-08-16 and no longer drifts. Its rate is unknown, and [chapter 9](09_the-fixed-lock.md) section 10c.2 already calls for measuring it | every centre-channel measurement on either platform. Absolute line centres become available with a stable lock, which is what the 2025 campaign could not do | spanned from 0 to 40 kHz per minute, with the recovered precision reported at each point, in `results/projections.csv` and its guided-platform counterpart |
| **repaired lock, per-sweep excursion** | not MEASURED. The same characterisation run [chapter 9](09_the-fixed-lock.md) calls for reads it beside the drift | every centre measurement on either platform rides it, as the drift row above | spanned in the fibre thread ([the campaign chapter](../big_picture/09_the-campaign-cases.md)): its paired-acquisition forecast covers the comb best-fit class to the wavemeter ceiling and the acquisition-geometry verdict there turns on exactly this item. The cell-side three-channel forecast now spans the drift over a tenfold range and finds the pull channel's spread unmoved, because the twin generates the drift as strictly linear in acquisition order and the fit carries that order as a free nuisance, so the term is a column of the design matrix and costs nothing. **The lever's worth cannot be established until the world's drift has structure**, which is the modelling item below |
| **the cell's own dimensions** | owner-stated 2026-09-09 as about 25 mm bore and 100 mm long, a standard size not MEASURED precisely, with the beam about 2.0 plus or minus 1.0 mm from the wall; carried in [the APPARATUS chapter](../APPARATUS.md) | they set how often an atom returns to the beam against how often it reaches a wall, which decides whether the vapour around the beam is hyperfine-pumped in steady state; the cascade model assumes each atom arrives unpumped | no forecast rests on it, and the span is why: over every plausible cell an atom reaches a wall many hundreds of times between beam crossings, and an uncoated glass wall relaxes the hyperfine state on adsorption, so atoms arrive reset whatever the dimensions are. The item is recorded because the argument for that needs a number the record does not carry, not because a result does |
| **beam radius at the focusing lens** | not stated in any document. It is the one input the Gaussian-optics estimate of the focus needs and the only one nothing on this bench measures, so the 42 to 53 micron band the finite-Hankel calculation returns through the 3 mm bore spans an input and does not resolve it | it sets the focus, and with it every intensity-denominated number, through the bore's truncation. It also sets how much of the beam the bore removes, which is a power loss of a third to a half over the same range | no forecast rests on it: every forecast spans the waist band the bore returns, not the input radius behind it. [Chapter 4 section 4.5](03_optics-protocol.md) proposes the delivery that removes the question instead of answering it: behind a single-mode fibre the focus is the mode radius times the ratio of two focal lengths, so the input radius stops being an input |
| **beam waist in the interaction volume** | not MEASURED in this cell. The working 42.38 um is calculated as the bore-limited actual focus this apparatus makes of its own input beam (order O44, 2026-09-21), which replaced the same-conditions measurement from an earlier thesis on this apparatus lineage that this record carried through that date | the largest open systematic in the record. Every intensity-denominated number rides it | spanned across the band the data allow in `results/transit_mc.csv`, and [chapter 5](05_width-collision-amplitude.md) specifies the profile measurement that closes it. A second, atom-based route in the cell itself: a 778 nm diode driving 5S to 5D through the same optics reads the waist from the MEASURED light-shift coefficient of that line, 2.5(2) e-13 per mW per square millimetre ([Martin 2019](../lit/martin2019.md), held), a twenty-linewidth shift at this bench's power on a 330 kHz line, so the waist follows to about four per cent from a number that imports none of the disputed theory, with the waist at 778 nm scaling as the wavelength for the same optics |
| **cell temperature against the cold spot** | instrumented but the gradient is not resolved | the density lever, and through it the collisional coefficient. And the meaning of any Doppler thermometer: with the record's densities the mean free path exceeds the cell below about 110 C and falls to millimetres at 130, so the vapour is a flux-weighted mixture of the walls' Maxwellians at the cold end and a local temperature at the hot end, and a pedestal fitted as one Gaussian reads a temperature that moves against the thermocouple across the lever by up to the gradient itself | carried as a stated systematic in `results/beta_self_probe.csv`, and the thermometer's regime dependence is an item for the deep-trace producer's landing |
| **retro-reflection intensity ratio** | not MEASURED. The working value is a stated prior, carried with its spread in `results/delta_alpha_posterior.csv`'s notes, and [chapter 7](07_acquisition-settings.md) records one in-record reading that contradicts it outright | the effective intensity, and through it every light-shift prediction. [Chapter 6](06_sizing-and-spending-rules.md) already schedules turning the assumption into a measurement | carried as the prior in `results/delta_alpha_posterior.csv`, whose limit row states how far the priors move it, and inside the predicted envelope of `results/stark_joint.csv` |

The residual drift's shape, not its size, an analysis unknown the same rules
govern and one the forecast now needs. A drift that is exactly linear in acquisition
order is removed for free by a fit that carries the order, whatever its rate, so the
three-channel forecast's lock cells are a null by construction and not a measurement
of what the repair bought. What a real residual does is wander, and a wander is not in
the span of a straight line in order. **What it changes**: whether the repaired lock is
worth the characterisation run at all, and what the pull channel costs on a drifting
arm. **How the forecast proceeds**: the lock cells are reported as a construction null
and no beam-time argument rests on them until the world builder carries a drift with
curvature or a random walk.

The saturated two-photon rate law, the same kind of unknown and the one that bounds
the tight-waist case. The world carries saturation as a width, through the companion,
and not as a limit on the rate. At the archive that is right to about a part in six: the
saturation parameter is [0.1726](../../results/platform_twins.csv "ref:platform_twins:cell_130C:cell:saturation_s").

At the campaign's 16 micron waist the shift
is about 7.02 times the archive's for an unclipped design, the bore out of the
focusing path, so the parameter is about 49 times larger before any further power
increase, and at the top rung of the power ladder it is larger still (its own
re-derivation owed), and the two-photon rate no longer grows as the power squared. **What it changes**: every
amplitude and every summed tooth area at the tight waist, and with them the area sum
rule's own null. **How the forecast proceeds**: those cells are read as upper bounds on
the signal and the file's note says so, and the summed tooth area is not read as a
sum-rule test at the tight waist at all.

The size is MEASURED (2026-09-06, on
quiet traces so no noise enters): with the term switched off the power ladder's area
follows the two-photon square law at a log-log slope of 1.978 and the depth ladder
stands still to seven per cent, while with it on the slope reads 2.209 and the depth <!-- other-quantity: a power-ladder slope figure, not an identifiability-profile cell -->
ladder falls by nineteen. The Bessel weights are innocent, summing to 1.000000 at the
lowest depth and 0.997587 at the highest over the seven modelled teeth, and so is the
wing baseline, which moves by three per cent across the ladder while the raw integral
falls by fourteen.

The world builder carries the axial collection window and the standing wave's
fringe-resolved tail since 2026-09-08, through `forecast.build_world_trace(z_ratio,
fringe_density)` and `lineshape.ramp_mixture`, and both forecast producers pass them
from the cell's waist and retro ratio. What stays open is narrower and is an APPARATUS
item: the mixture weights the window uniformly along the beam, where the MEASURED
collection profile (the lens, the image distance and the cathode's 12 mm axis, the item
below) sets the true weight, so the window's correction is exact in form and stated to
the tolerance of that profile, which is 8 to 16 per cent on the coefficient at
16 microns: integrating the mixture's mean over a uniform weight, a linear
taper, a Gaussian at half at the edge and a window half again as long gives
0.585, 0.677, 0.615 and 0.555, against 0.818 to 0.942 at 40 microns. <!-- other-quantity: a mixture mean -->

And the realised factor is not that geometric ratio: `pull_factor_quiet` at a fixed 16
micron geometry reads [0.5753](../../results/three_channel_forecast.csv
"ref:three_channel_forecast:base::pull_factor_quiet"),
[0.5582](../../results/three_channel_forecast.csv
"ref:three_channel_forecast:power_top_0.5W::pull_factor_quiet"),
[0.4843](../../results/three_channel_forecast.csv
"ref:three_channel_forecast:eom_comb_8MHz::pull_factor_quiet") and
[0.5522](../../results/three_channel_forecast.csv
"ref:three_channel_forecast:eom_comb_12.5MHz::pull_factor_quiet") across the base, the
0.5 W ladder and two comb spacings, because the centre is fitted in a window that moves
with the comb, so a campaign supplying the geometric number reads 1.7 to 18 per cent
low.

The two quantities are named apart: the mixture's centroid ratio is geometry,
`pull_factor_quiet` is what the estimator realises. `results/waist_ladder.csv` reports
what the window does against the pure ramp (the windowed third moment at -1.035831 of it
at 16 microns, a reversed sign, and the mean pull at 0.585), which is now what the world
builds. The exhibit twin (`examples/campaign_twin.py`, at the archive's 42.38 microns,
where both terms are a few per cent) now reads its waist default from
`constants.W0_CENTRAL_M` (owner order O44, 2026-09-21), no longer the retired lineage
convention.

The guided
arm carries neither: an evanescent field has no focus, and the record holds no fringe
model for a retro-reflected guided mode, so that item is the fibre thread's.

The single-waist kernel at a tight waist, an analysis unknown and the third of
this kind. The forward model gives the interaction volume a single beam radius, and the
collected region is fixed by the optics, so the description holds only while the
Rayleigh range is long against that region. Measured over the collected length at
the campaign's own optics, the transit width's spread about its mean runs 0.1 per
cent at 128 microns, 4.5 at the calculated 42.4, 5.5 at 40, 23 at 24 and 47 at 16, where the beam
radius at the edge of the collected region is 4.3 times the waist. **That spread
licenses nothing for the shape channels, and this item said it
licensed the convolution until 2026-09-09.** It is the axial spread of the
transit kernel alone, and the second mechanism is radial.

The saturation companion follows the local light shift, the ramp's own variable, so the
broad elements are the shifted ones and shortening the collected region cannot reach it.
Measured element by element (`scripts/run_kernel_inhomogeneity.py`), the windowed third
moment is wrong by [103.942](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w42um:k3_error") per cent at the archive's own waist,
[96.571](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w24um:k3_error") at 24 microns and
[89.992](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w16um:k3_error") at 16: **the band's two waists are the worst
of the four and not the licensed ones.** The centre channel splits.

The centroid is exactly immune at every waist
([-0.000](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w42um:centroid_pull_error") per cent), while the fitted centre
the campaign actually inverts moves by [-1.563](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w42um:fitted_centre_error") per cent at 42.38 microns and
[-60.912](../../results/kernel_inhomogeneity.csv
"ref:kernel_inhomogeneity:w16um:fitted_centre_error") at 16. **A campaign waist has no
MEASURED band of its own**, so the tolerance producer applies the archive's 40 to 45
micron band as the same fraction of each proposed waist, paired with the retro-ratio
error as the record's convention pairs them.

That is a borrowed uncertainty, not a spanned
one, and it is an open item: a knife-edge at each proposed waist is what
replaces it. **What it changes**: any reading that depends on the line shape at a
tight waist, the third moment above all. The width's spread does not threaten the fitted
centre, because it is symmetric in the axial coordinate and a symmetric
broadening does not move a centre. The shift's own integral over the collected
length does move it, by the 2, 11, 31 and 42 per cent the collection-window
item above puts on a pure-form centre estimator, which is why the forecast
carries the window and the fringe tail in its world since 2026-09-08 and
inverts its centre through the quiet curve's own pull factor and no longer
through the pure ramp's. **How the forecast proceeds**: the centre channel is read at
every waist.

The shape-only waist closure has the same open cost: its fitted interval
covers the injected truth zero or one time in four realisations against a
nominal 68 per cent once noise is added, so its bar and not its centre is
unresolved (2026-09-20). A campaign that holds the repaired lock steady
removes the need for each scan's own free centre and so can read the plain
centroid the 2025 drifted dataset never could, a lever this coverage gap
makes worth taking.

The shape channels are the conflict:
the single-waist description is good at 40 microns and wider, and the third
moment only carries signal at 24 and below, where the shift approaches the
line. The forecast reads the shape channel exactly where this item says the
model is weakest. That tension is the finding, and it is not a rule for
choosing a waist. **The design choice at a tight waist (owner statement, 2026-09-06)**: at the
calculated 42.38 microns with the present magnification of about 2.5 the convolution model is already marginal
(more so than at the retired waist convention this statement was made against),
so a smaller waist means one of two things and the PLAN must say which.

Either
the twin's line becomes the volume integral, the transit kernel and the shift
integrated over the collected length together, of which only the shift's half
exists in the tree as `stark_ramp_axial`, or the collection magnification
rises to hold the collected length at the archive's fraction of the Rayleigh
range, where the convolution holds to a per cent, a range that scales as
the waist squared: from about 2.5 at 42.38 microns to about 2.8 at 40, 7.8 at 24 and
17.5 at 16, at a cost in collected light proportional to the collected length at
fixed numerical aperture (the fold-increase this sentence stated at the retired
waist convention is an open item pending re-derivation at the calculated
waist, since it is entangled with the arctangent-law figures below). The geometry sign flip of
chapter 4 exists only on the first route, since the second removes the window
that makes it.

And the second route pays in photons where the campaign is
already shot-noise limited at the peak (chapter 10 puts the analog floor equal
to the shot term at under two per cent of the median peak), a factor 2.6 in
signal-to-noise at 16 microns on the collected fraction's arctangent law, so
the volume model is the route that costs no
light. The volume model costs analysis days and no beam time, the
magnification a relay redesign and a bench day without atoms before the light
cost. **The owner chose on 2026-09-07: the volume model, and the light stays**
([chapter 4](04_intensity-and-light-shift.md) carries the numbers), so what
this item now waits on is the analysis and not a decision. The light cost
follows the collected fraction's arctangent law and not the collected length,
so it is a factor of seven at 16 microns and 2.6 in signal-to-noise, five and
2.2 at 24, 2.4 and 1.5 at 40.

The fit-window systematic on the collisional width, not an APPARATUS
number but an analysis unknown the same rules govern: the window scan
(`results/fit_window_scan.csv`) shows a coherent drift of the fitted width
with the fit window that no committed error bar carries
(`docs/uncertainty.md` §3a). What closes it: the committed shared-slope
$\beta$ construction re-run per window. Until then the headline bound's own
line in [RESULTS.md](../RESULTS.md) points at that section, and the
forecast proceeds unchanged because every per-window indicative slope is
consistent with zero.

### The 225 mW point's power calibration

The predicted light shift and its coefficient scale as the power at the atoms,
and the record carries the 225 mW operating point without a calibration
uncertainty: the sweep's envelope (`rb5s6s/stark.py`) propagates the waist band
and the retro-ratio error and nothing for the power. The owner holds the
drive's own figure and states it at 0.5 per cent, so the prediction band spans
that and `results/prediction_band.csv` carries it in its worst-case edges.

What his number does not cover, and what is still owed here, is the chain
between the meter and the atoms: the meter's calibration certificate, the loss
budget between meter and cell, and the window transmission at 993 nm. Those are
systematic offsets of the power at the atoms and not the drive's stability,
so they bias $\kappa_\mathrm{pred}$ in one direction where the 0.5 per cent
merely widens it.

The direction is upward, and the first form of this item had the geometry the
other way about. It read "the loss budget from meter to cell", which puts the
meter upstream of the atoms. The meter is downstream of them. [APPARATUS](../APPARATUS.md)
section 1.2 has the second $f = 150$ mm lens re-collimating the beam "toward the
flip-in power meter and the retro mirror", tagged PHOTO against the annotated
bench photograph, so the exit window and that lens sit between the focus and the
meter. The recorded watt is therefore smaller than the watt at the atoms, and
the correction multiplies $\kappa_\mathrm{pred}$ up and not down.

Its size is computable from the record's own numbers, and it is larger than the
aperture term it sits beside. [Priorities](02_priorities.md) item 2 writes the
retro leg as exit-window, lens, mirror, lens, exit-window, so
$\rho = T_\mathrm{window}^2 T_\mathrm{lens}^2 R_\mathrm{mirror}$. That names the
same two surfaces for the round trip. The forward leg from the focus out to the
meter crosses them once each and is carried in no module.

At the clean values of
that item, 0.99 each, the missing factor is $1/0.980 = 1.020$. At its filmed <!-- other-quantity: two transmissions -->
scenario, 0.90 per pass, it is $1/0.891 = 1.122$. The EOM aperture's on-axis
factor moves the same prediction by $-3.3$ per cent at the convention waist, so
this uncarried term is between two thirds and four times its size and opposite
in sign. Which end applies is unmeasured: [the sizing rules](06_sizing-and-spending-rules.md)
row 8 records the 0.99-to-0.90 film as an assumption and "not observed on
these windows". The condensation that was actually seen was on a cooled,
unwrapped cell, which says nothing about the film during operation.

And it is monotone in temperature, which is the axis the analysis uses as a
lever. The film grows as the cell cools, so this multiplier drifts across the
70 to 130 °C arm that separates the collisional term from the laser width. The
hazard is already stated one item below for $\rho$, an optics drift that
"uncorrected reads as a temperature-dependent light shift", and the same two
surfaces enter the forward normalisation a second time, in the same direction.
A systematic monotone in the lever's own axis is the one shape that can
manufacture the lever's signal, so the transmission is MEASURED per condition
and not once.

What it would change: whether the prediction band reaches the bound, and the
guided arm's per-run power ruler, since a calibrated power at the fibre is the
same measurement.

### The collection lens and its image distance

The fluorescence collection optics set the axial window of the interaction
volume, which is the `z_ratio` of `stark_ramp_axial`. That function has carried
the closed form since July with its window flagged open, and
`constants.collection_z_ratio()` now closes it from the focal length, the
image distance and the cathode's 12 mm dimension along the beam. Two of the
three are stated to a tolerance and not yet MEASURED: $f = 18 \pm 1$ mm and an
image distance of $50 \pm 5$ mm, the owner's own figure, restated on 2026-09-22 with
the reason it is a tolerance and not a measurement. An owner statement puts the magnification at about 2.5
(2026-09-06), which the stated conjugates give as 1.8 at their centre and reach
at their tolerance's edge, so the imaging geometry is the first ruler
measurement of the campaign.

They close with a ruler and no atoms. What they change: the window is
[0.59](../../results/prediction_band.csv "ref:prediction_band:collection_window:z_ratio")
Rayleigh ranges, where the ramp is exact over most of the shift range and the
recovered shift is biased low by
[-6.02](../../results/prediction_band.csv "ref:prediction_band:collection_window:shift_bias_width_pct")
per cent. That correction stays conservative only while the window is below
[1.691](../../results/prediction_band.csv "ref:prediction_band:collection_window:width_bias_sign_flip_z_ratio"),
and the third moment's own null sits at
[1.117](../../results/prediction_band.csv "ref:prediction_band:collection_window:skew_null_z_ratio").
**The largest of the three uncertainties is how the 50 mm is read**: as the
image distance it gives the window above, and as the object distance it would
give one about three times wider, a twelvefold larger bias with the null within
reach. `constants.COLLECTION_IMAGE_DIST_M` names the reading it takes.

#### The cathode's other dimension, and what it truncates

The same imaging fixes a transverse half-acceptance of about 0.8 mm from the
cathode's 3 mm side, and two things emit inside it. The drive beam does not
reach it: at the axial window's own edge its radius is tens of microns against
that acceptance, a margin above ten at every beam quality the band allows, and
the two-photon rate goes as the square of the intensity, so the weight outside
the acceptance is not small but absent. The radial integral, which is the
AC-Stark ramp itself, is therefore untouched, and the optics stay a pure axial
window for the signal.

The radiation-trapped halo does reach it. `run_trapping_channels.py` sets the
halo's radius equal to the standoff from the near window, which is not
recorded and is carried as a band from one to five millimetres, and at its
central value about half the halo's cross-section falls outside the cathode.
That truncation is two-dimensional, the model carries none of it, and the
trapping that feeds the halo follows the optical depth, which runs by about
fifty across the temperature arm. The halo is flat in laser frequency, so it
enters the free per-trace baseline and not the lineshape, and the
consequence is a collection efficiency that varies with temperature. **So the
standoff is load-bearing for the collected rate and not only for the one per
cent re-excitation it was introduced to bound.** A ruler measurement of the
focus position in the cell closes it, alongside the imaging geometry above.

### The background scattering reaching the detector

Is background scattering in the model? It is
not, in either the forward model or the twin, and the reason it has never
mattered is worth stating before the item is opened. The detection is at
795 nm, the D1 photon of the cascade, behind about 50 dB of 795 nm filtering,
with the drive at 993 nm, so the filter rejects elastically scattered drive
light and the model never has to carry it. What the filter does not reject is
795 nm light that does not come from the interaction volume. Three sources
are known. The detector's own dark rate. The cell wall's thermal emission in
the passband, which `results/blackbody_channels.csv` bounds at
[2994.39](../../results/blackbody_channels.csv "ref:blackbody_channels:bbr_detector_background:T70C")
photons per second at 70 C before any collection solid angle, and which rises
steeply with temperature.

And the cascade's own D1 light scattered off the
walls and windows after being trapped, which exists only with hot atoms,
scales with the signal, and is therefore the halo term of the twin and not a
background at all.

**Grounds for an APPARATUS item, not a derivation.** All three enter the trace
the same way, as an **additive pedestal** under the line, and the fitter already
carries a per-trace linear baseline, `b0` and `b1`, which absorbs a constant and
a slope exactly. So a flat background is not a model error at all: it is
absorbed, and it costs only the two degrees of freedom already spent. **The term
that would matter is one that varies across the scan on the scale of the line**,
and nothing in the APPARATUS is known to do that. Whether anything does is a
measurement and not an argument, which is what opens it as an item here.

**Closure, in two readings.** A scan with the drive blocked, at the
working temperature, reads the dark rate plus the wall's thermal emission and
nothing else, since neither depends on the drive. A scan with the drive on and
detuned from the two-photon resonance by many linewidths, at the same
temperature, adds whatever drive light the filter passes. Neither reading can
be taken cold: the thermal term is the one that matters and it needs the hot
cell. What the pair does not measure is the trapped D1 light, because it is
not separable from the signal, and the twin carries it as the halo fraction
from `results/trapping_channels.csv`.

**Consequences of a non-flat response.** A background with curvature on the
line's own scale biases the widths, since the baseline model cannot follow it,
and a background whose scan dependence is **asymmetric** is the one term that could
imitate the third moment. That is the channel the campaign now rests on, and
it is the single reason this item is worth an afternoon: **a shift-like
asymmetry from the detection path would be read as a light shift by every
estimator in this record.** The power ladder is what separates them, since the
true shift's third moment goes as the cube of the power and a detection
background does not, so the discriminator exists and is already in the design.
Until the measurement is made the forecast spans the term by treating it as
absent and naming it here.

### The angle between the counter-propagating beams

Doppler cancellation in the two-photon line is exact only for exactly
anti-parallel beams. An angle $\theta$ between them leaves a first-order
residual $k v_\perp \theta$, a Gaussian in the line whose width goes as the
rms of one velocity component, $\sqrt{k_B T/m}$: at 130 C that is about
200 m/s, so the residual Gaussian has an rms width of **about a fifth of a
megahertz per milliradian** at 993 nm (near half a megahertz full width), and a
one to two milliradian misalignment adds a few hundredths to a few tenths of a
megahertz in quadrature under a Gaussian the fits put near two. (The first
form of this item quoted the three-dimensional mean speed, which is neither
width.)
Nobody has recorded the angle, and the retro path is set by a flat mirror
behind the cell, so this is an APPARATUS number and not a derivation.

The record already bounds its effect. Any speed-borne term must grow as the
square root of the temperature, about eight per cent from 70 to 130 C and monotone,
and the fitted Gaussian across the ladder
(`results/global_dataset_fit.csv`, `sigma_laser` by session) is
non-monotonic and smallest at 130 C across the campaign sessions, which reads
as a small residual, though those rows carry no stated error and a
session-to-session spread near a few tenths of a megahertz, so the reading is
a bound and not a resolution. What closes it is a measurement without atoms at the line: the
angle from the beam positions at two distances along the return path, or the
width of a Doppler-broadened single-photon line under the same alignment.

What
it would change: the Gaussian nuisance gains a derived, temperature-scaling
share, and the laser's own width is read from what remains. No forecast in
this repository rests on the angle: the forecast spans the term by treating
it as absent and naming it here.

### The piezo's first resonance, and the lock's servo bandwidth

The piezo's first mechanical resonance, and the lock's servo bandwidth if the
scan runs under lock, both bench facts and both newly load-bearing. The scan
rate is the cleanest degeneracy-breaking knob in the record, leaving every
spectral width exactly untouched while every drift term goes as its reciprocal
([chapter 7](07_acquisition-settings.md)). **What it changes**: how far a rate
ladder can be pushed, and therefore whether the drift's shape can be MEASURED
instead of assumed linear. **How the forecast proceeds**: the two computed
ceilings are known and neither binds, rapid passage at 2.9e7 MHz/s and the
detection chain at 8.1e6 against a fastest proposed setting of 6000 MHz/s, so
the forecast spans the rate between the 2025 setting's 24 MHz/s and that
6000 and states that the piezo, not the physics, sets the upper end.

### The EOM drive's available resonances and depths

The new RF drive reaches a higher modulation depth without residual
amplitude modulation and can sit at a resonance other than the 2025 spacing
(owner statement, 2026-09-06). What is not recorded is which resonances the
tank or its replacement offers and what depth each reaches, and both are
APPARATUS numbers. What they change: the centre channel's fit window stops
just short of half the spacing, so a spacing of 25 MHz or more opens the full
window the tight-waist line needs, while the moment channel's science trace is
taken with the RF off whatever the spacing, since the teeth's tails enter the
window at any spacing the record had tried when this was written. **The run
refutes that half**: the comb-free trace is where the moment channel is least
accurate, and the 25 and 40 MHz combs are where it recovers the coefficient.

Measured 2026-09-06, and the spacing threshold above is refuted
([`results/three_channel_forecast.csv`](../../results/three_channel_forecast.csv)).
The fit window is 12 MHz of half-width at 25 MHz and at 40, so truncation is
not what separates them, and the reasoning above stopped at truncation. What
separates them is the teeth's tails: at 25 MHz the first teeth stand 13 MHz
beyond the window edge and reach in, and the depth null reads 13 against a
scatter of 52, which is no measurement. At 40 MHz they stand 28 MHz clear and
the null reads 0.009 against 0.024, under half a standard error from zero.
**So the lever is specified at 40 MHz**, and which resonances the tank offers is
the APPARATUS number this item still wants.

### The RF gate's optical-power invariance, and its switching transient

The RF can be switched on and off inside a single triangular scan, which puts
the saturated and the de-saturated line in the same sweep under the same atoms,
the same density and the same moment of the lock (owner statement, 2026-09-06).
The design rests entirely on one property: a pure phase modulation holds the
total intensity, so the light shift is the same with the drive on and off, and
only the rate-driven terms move. At the campaign's 16 micron base point that is
a saturation-companion width running from 9.09 MHz with the drive off to 0.087
MHz at the third tooth, a hundredfold ladder in the one width, while the shift,
the transit width and the natural width stand still.

What is not recorded is whether the transmitted optical power is actually
invariant across the switch. A drive-dependent insertion loss changes the
power, hence the shift, and the on-minus-off difference would then contain the
quantity the design exists to isolate. **This is the item that decides whether
the lever works at all**, and it fails in the flattering direction: a power
change that tracks the drive produces a clean, repeatable, entirely spurious
difference. It needs a power meter after the modulator and no atoms.

The same measurement carries a second number, the settling time of the drive
and of the crystal's thermal state after a switch, which sets how much of the
sweep either side of a transition is unusable and must be excluded.

The instrument for the first number is already derived, not assumed. A
residual amplitude modulation of index `m` tilts the tooth pattern as
`d ln W_s / dm = 2 s / beta`, so the plus-k against minus-k asymmetry is
`4 k m / beta` and grows with the tooth index: one per cent of amplitude
modulation shows as fifteen per cent of asymmetry at the third tooth. The
blind region is stated with it, since quadrature amplitude modulation is a pure
phase to first order and does not appear in the tooth heights at all, so the
tooth pattern bounds one quadrature and the power meter is what bounds the
other.

### Power of the 105 ruler traces

`data_raw/MANIFEST.csv` lists 61 traces in the `ruler_t` role and 44 in
`ruler_p`, every one with the RF on, and **every one with an empty `power_mW`
cell**. The ruler traces were calibration traces and their power was never
logged into the MANIFEST. What it changes: an external analysis proposes
reading the beam waist from the saturation of the teeth in those traces, which
needs both a power above about 100 mW and a spread of powers across the set,
and neither can be established from the record as it stands.

The same analysis
finds by injection and recovery that the estimator's usability tracks the
saturation it is tested at: unusable at a wide, lightly saturated probe waist
and usable at 32 microns, a tighter focus than this record's own calculated
waist. Saturation there depends on the delivery convention assumed for the
beam (the bore clipped or not), so whether the estimator is usable at the
calculated 42.38 µm waist, and under which delivery, sits unread and is owed. The proposal is
in any case a new session and not a reanalysis, and the missing power is what
decides whether the archive can even serve as its rehearsal. It is an APPARATUS fact the bench notebook may hold.

### The wavemeter's averaging mode and its environmental readings

Screenshots from the campaign show the wavemeter in a floating average over ten
measurements, with cell readings near 26 C and 1006 to 1007 mbar, and one shows
a settle of about an hour and a half after power-up. None of this is in
`APPARATUS.md`. What it changes: a ten-sample floating average smooths the
jitter that the offset analysis of chapter 9 reads, so the scatter between the
two logged offsets of 119.6 and 133.4 MHz is a scatter of averages and not of
single readings, and the settle time bounds how early in a session any absolute
reading can be trusted. Both are APPARATUS facts and both are one line each.

And the readout's own step is the larger term, which nobody had separated.
The peak labels are logged to four decimal places in nanometres. At 993.4 nm a
step of one part in ten thousand of a nanometre is 30.4 MHz on the laser axis
and 60.8 on the transition axis, so a single logged reading carries a uniform
error of standard deviation 8.8 and 17.5 MHz on those axes. **The two logged
offsets differ by 13.8 MHz, which sits inside that**, so the observed scatter is
consistent with the step alone and is not evidence of drift. Every figure of
order sixty megahertz this record has quoted for its absolute axis is this step
and not the instrument, which is a class better. **What settles it costs
nothing**: log the digits the instrument already supplies, and check on any
logged sequence whether the last digit ever moves, because averaging beats
quantisation only when the jitter dithers across the step.

Under that condition
the campaign's own ten-sample average would give 5.5 MHz on the transition
axis, and nothing at all without it.

### The piezo's triangle frequency

[Chapter 7](07_acquisition-settings.md) section 9 shows that the memory of a
modern instrument allows of order a hundred triangles in one record while
keeping each crossing fittable alone, and that the count is what buys the drift
and hysteresis diagnostics. **What limits it is then the scan piezo and its
servo, and the record has no statement of either.** What settles it: a
frequency response taken by driving the ramp and reading the transmitted
fringe, an afternoon with no atoms. **What it changes**: whether the campaign
takes one triangle per record, as 2025 did, or the hundred the analysis wants,
which is the difference between having the drift diagnostic and assuming the
drift away. **Cost.** Half a day inside the optics day.

### Magnification of the adjustable expander

The campaign wants a waist ladder taken at fixed power and fixed retro ratio
through an adjustable beam expander (owner design, 2026-09-06), because the
magnification is a ratio, of focal lengths where the optics are ideal and of
spot sizes on a camera where they are not, and can be known far better than the
absolute waist, which makes the ladder's abscissa calibrated. What the record
does not have is the instrument's own numbers: the magnification range, the
accuracy with which the magnification is known at each setting, whether the
mode quality survives at the extremes, and how the assembly behaves thermally
under the beam, which matters because the record already carries a
power-dependent thermal lens in the modulator.

What they change: the ladder
measures the reference waist through two different powers of the
magnification, the transit's inverse and the shift's inverse square, so the
accuracy of the abscissa sets how tightly the two agree and therefore how much
the largest open systematic in this record shrinks.

**No committed forecast rests
on this item either.** The analytic ladder that spans it is drafted and its
exponents check against the package functions that own them, and until its file
is committed the campaign case quotes nothing from it. A second number rides with
it, the retro ratio at each setting, since expanding the beam changes the
returning mode's overlap unless the retro is re-matched, and the light shift
takes one combination of the two arms while the two-photon coupling takes
another.

### Beam mode at the cell and collection aperture

Two bench facts the analysis assumes and no measurement in the record fixes.
**The mode at the atoms.** The ramp's shape, and with it the plus two thirds
pull coefficient and the 0.566 skewness magnitude, is a property of a Gaussian beam. The
source is a single-frequency titanium-sapphire laser, so the beam leaves TEM00,
but an electro-optic modulator, the lenses and the cell windows sit between the
laser and the atoms, and a mode that is no longer Gaussian changes the ramp's
shape and not merely its scale. **Settlement.** One camera image at a
plane equivalent to the interaction volume, the same image the waist ladder of
chapter 4 already needs.

**The collection aperture.** The solid angle sets what a count-rate forecast
for a geometry this bench has not run is worth, the tighter-waist relay above all, where the
record's present rate is inverted from the committed noise law and already
carries the aperture it was taken with, and the record does not state the
collection lens's clear aperture, and at the object distance the
stated conjugates give, near 28 mm, a half-inch against a one-inch lens moves
the collected fraction by a factor of about three and a half, rising toward
four in the small-angle limit. **What settles
it.** A ruler. **Cost.** Both close inside the optics day.

### The expander's pointing stability across its zoom range

The waist ladder of chapter 4 item 3c is interleavable only if changing the
magnification does not move the beam. A realignment between settings acts as a
new block, so the ladder would carry block scatter along its own axis. **Bearing on the forecast.** A factor of three on the waist's
share of the error budget: under a per cent with a pointing-stable zoom,
about three per cent with discrete pairs realigned each time, and about half
of that if every block is bracketed by a reference condition at one
magnification, one power and one temperature. **Settlement.** Image the
beam position at each setting of the expander before the campaign commits to
interleaving, which is the same camera step the profile and the magnification
already need. **Cost.** An hour inside the optics day. Raised from outside the
record on 2026-09-07.

### The oven's block-to-block reproducibility at one setpoint

Temperature cannot be interleaved inside a block, so the collisional
coefficient inherits the block-to-block scatter directly and no number of
traces at one setpoint reduces it. **Bearing on the forecast.** Whether that
coefficient's error stays at the ten per cent the record's own block scatter
implies or falls. **Settlement.** Either a better-controlled oven, or a
reference condition at one fixed temperature repeated in every block so the
block term is MEASURED and divided out. The second costs traces and no
hardware, and it is the one the campaign can choose today. **Cost.** About a
tenth of each block. Raised from outside the record on 2026-09-07.

### The retro power ratio

The forward-to-return intensity ratio at the atoms enters the light shift as
one plus the ratio and the prediction band through its spread, and the record
labels it an assumption at 0.94 with a spread of 0.04 that its own docstring
calls deliberately modest. The physical range is wider: with every surface the
return beam crosses uncoated, at four per cent each, the ratio falls to about
0.7 before mirror loss, and coated it sits near 0.97. At the uncoated end the
predicted coefficient falls by about twelve per cent and still clears the
bound, so the tension survives the range, and the forecast should span it
until it is MEASURED.

**Settlement.** The window coating and the retro
mirror's reflectivity from the bench, and one measurement: a calibrated
attenuator in the return path, at which the narrow line goes as the ratio
times the attenuator's transmission taken twice and the pedestal as one plus
the square of that product, so a run at full and at half transmission reads
the ratio to a few per cent where the area ratio at full transmission alone is
nearly stationary in it. **Cost.** Two blocks in one session with the wide window,
since the pedestal must be fitted. Raised by an external reading on 2026-09-06
and derived here on rung 1.

And the attenuator is worth more than a calibration: unbalance the retro on purpose. The
fringe contrast, the one lineshape channel that separates the retro ratio from the
polarisability, goes as twice the root of the ratio over one plus the ratio, and that
expression is stationary at a ratio of one.

Its logarithmic slope reads [0.01546](../../results/fringe_rho_recovery.csv
"ref:fringe_rho_recovery:dcontrast_dlnrho:rho=0.94") at the working value against
[0.15713](../../results/fringe_rho_recovery.csv
"ref:fringe_rho_recovery:dcontrast_dlnrho:rho=0.5") at one half, ten times larger, and
it costs the Doppler-free rate, which goes as the ratio itself ([methods
3](../methods/03_the_ac_stark_ramp.md)), a factor 1.9 in signal at one half, and of the
shift under measurement, which goes as one plus the ratio, a factor 1.3, with
[0.08685](../../results/fringe_rho_recovery.csv
"ref:fringe_rho_recovery:dcontrast_dlnrho:rho=0.7") between them, so a return beam
deliberately attenuated to half turns a channel this bench cannot read into one it can,
and the same run supplies the calibration above.

Where the contrast is
MEASURED with the polarisation axis known and the two beams superimposed it
returns the ratio to [2.98e-08](../../results/fringe_rho_recovery.csv "ref:fringe_rho_recovery:max_rho_bias_clean:single_valued") over the admitted grid. Assuming the axis
instead costs up to [0.9738](../../results/fringe_rho_recovery.csv "ref:fringe_rho_recovery:worst_rho_bias_polarisation_assumed:single_valued") in the ratio and an unthreaded tilt up to
[0.8739](../../results/fringe_rho_recovery.csv "ref:fringe_rho_recovery:worst_rho_bias_tilt_and_offset:single_valued"), so the run records the axis and the retro alignment beside the
attenuation. The ratio it returns is exactly immune to the beam quality.

### The retro path length

State of knowledge. Nothing. The retro mirror is a flat behind the cell
([APPARATUS](../APPARATUS.md)) and no page records its distance from the atoms.

Bearing on the forecast. The retro beam's modulation lags the forward beam's by
the round trip, so the two-photon comb's depth is the drive's depth times
$\cos(2\pi f d/c)$ ([methods chapter 5](../methods/05_the_frequency_ruler.md)).
The committed ruler is untouched, because the depth is fitted from the tooth
heights on every trace and is therefore the effective one. What the length
decides is the prediction of a depth from a drive setting, which the
comb-spacing lever of [chapter 4](04_intensity-and-light-shift.md) needs: at
12.5 MHz the factor is 0.997 for 0.3 m and 0.966 for 1 m, at 25 MHz 0.988 for
0.3 m, at 40 MHz 0.969. It also sets a zero-parameter check of the geometry,
since at $f = c/4d$ every tooth collapses into the carrier whatever the drive
(250 MHz for 0.3 m, 125 for 0.6 m).

It decides a second thing, found 2026-09-09, and this one rides on the retro
ratio. Lens (8) and the flat mirror form a retro whose returning mode matches
the forward one exactly when the mirror sits one focal length beyond the lens,
and not otherwise: the round trip returns the waist onto itself with a power
overlap of 1.000000 at that distance, 0.9967 at 50 mm and 0.9610 at 500 mm <!-- other-quantity: the retro mode-overlap power fraction, not the collection-window kappa2 ratio -->.
So the `rho = 0.94` of record may be carrying an unmeasured mode-mismatch factor
beside the surface losses it is meant to describe, and the item below on the
retro power ratio cannot separate the two without this length. The same
geometry is what makes `rho` non-transferable across drive wavelengths, since a
retro aligned at 993 nm returns the 760 nm mode with an overlap of 0.9859 at
the design distance.

It closes with a tape measure, and the
same distance enters the misalignment item above and the mode-overlap reading
here.

### The waist measurement against its analysis substitute

The waist is the open item every absolute result here is conditional on, and
the two ways of closing it can now be compared in the same units instead of
argued about.

Measuring it directly, with a knife edge or a camera at the focal plane, pins
one parameter and lets the centroid carry the polarizability on its own. Not
measuring it leaves the waist free in the joint fit, where the second and
fourth moments constrain it and so free the centroid indirectly. Both routes
were costed on the twin, by two independent calculations that agree: **a
measured waist is about one and a half times better on the polarizability than
the entire moment stack with the waist free, and the moment analysis recovers
around two thirds of what the measurement would give.**

Two consequences follow and neither is optional.

The first is that the two are **alternatives and are never summed**. Once the
waist is pinned the moments add nothing further to the polarizability, because
their own sensitivity to it is zero: their contribution was always the waist
and never the shift. A forecast that adds the analysis gain to the measurement
gain is double counting.

The second is that the measurement is the cheaper of the two by a wide margin.
It is an afternoon at the bench against a campaign of analysis, and it buys
more. What the moment analysis buys instead is the ability to work without it,
which is what makes the existing data analysable at all and is worth exactly
its two thirds.

None of this narrows what the higher moments do elsewhere. They carry the waist
itself, the collisional coefficient, the systematics monitors and the
model-form discrimination, and the substitution argument applies to the
polarizability alone.

One caveat travels with the ratio. Both calculations perturb with white noise,
while the real traces carry a correlated tilt across the window, and a tilt is
the one disturbance that moves a centroid without moving a central moment. The
centroid's side of the comparison is therefore the optimistic one, and the
ratio may move toward the moments when the measured correlation is injected.

### Mode content at the bore

State of knowledge. Nothing records how the drive beam's power is distributed
across transverse modes, and this is a separate item from the input radius below
and not a refinement of it.

Bearing on the forecast, and it removes an axis instead of widening one. A
beam-quality figure is the natural thing to ask a laser supplier for, and behind
a hard aperture it does not answer the question. Propagating the clipped bore
with the same beam-quality figure carried in different mode compositions gives
focal radii from the bore's own limit up to a few per cent above it, because a
high-order halo is removed by the bore before the lens and never focused by
it.

A beam three times worse than diffraction-limited, with its excess in high
modes, focuses to the same spot as a perfect one. **So beam quality does not
predict this focus and there is no beam-quality axis to scan**, and what does
predict it is the radial profile arriving at the bore.

What the bench already constrains, added 2026-09-23 and the first quantitative handle on
this item. The power through the modulator drops by about 60 per cent of roughly a watt,
and the power the record logs is read after it. Two things follow. The transmitted
fraction divides out of the light shift per recorded watt, so it is not a systematic on
that quantity. And the same number bounds the mode content, because every non-clipping
loss in that path lowers the total further, so the bore's own transmission is bounded
from below by the measured drop.

A pure high-order input passes far less than that at any input radius from 1.6 mm up. It
survives only near 1.2 mm, where an ideal Gaussian would pass more than nine tenths and
nearly the whole drop would have to be something other than clipping. **So the
measurement disfavours the halo-dominated end of the family without excluding it**,
which is weaker than a profile and is not nothing: before it, that end was an assumption
with no evidence either way.

What closes it. A camera image at the bore plane, or equivalently at a relay of
it, since the profile is what the propagation needs and a single number is not.
The measurement is the same one the item below asks for, read as a profile
instead of as a radius, so the two close together. The transmission above
narrows the prior the profile has to overturn. It does not replace it, because
one number cannot separate the input radius from the halo weight, and the pair
moves together along exactly the direction the measurement fixes.

Until it is closed the forward model states its own convention and not
implying a measurement, and any axial extent it reports is the propagated
field's, not a free-space Rayleigh range.

### The input beam at the focusing lens

State of knowledge. The beam reaches L1 free-space from the laser through the
EOM's 3 mm clear aperture, which an infrared card recalls clipping
([APPARATUS](../APPARATUS.md) 1.2), and nothing records how much of the beam
that aperture removes. L1 itself is quoted from the source as "a plano-convex
lens", which is a single element, and no page states an achromat.

Bearing on the forecast. Nothing at all while the campaign drives one line, and the
whole cross-transition programme once it drives two. The focused waist is
`lambda f / (pi w_in)`, so a retune moves the waist even with no optic touched,
and the ratio of light shifts between two drives carries `(w_in at one / w_in
at the other)` squared.

If the aperture fixes the input radius the factor is
one and the waist follows the wavelength. If the beam is an unclipped
fixed-geometry resonator mode the radius follows the root of the wavelength and
so does the waist. Between 993.4 and 760.1 nm the two regimes differ by 31 per
cent on every shift ratio built from them (register A136). That spread is the
ratio of the two scaling laws, so it does not depend on which waist anchors it.
The absolute pair this line used to quote was anchored on the retired waist
convention and went with it.

The element type is the small term, worth 0.8 per cent through `1/(n-1)` and
insensitive to the glass, but it is not free: an achromat holds the focal
length and a singlet also moves the focus 1.17 mm, which is a third of the
collection half-window.

Closure. A beam profile at the lens, on the same afternoon and the
same stage as the waist measurement the PLAN already schedules, with no atoms
and no lock, with one look at the lens mount for a cemented doublet. Until then
the campaign's own line closes it in situ, since the transit width carries the
same geometry to the first power and separates the two regimes by 14 per cent.

**Treatment in the forecast.** `rb5s6s.constants.waist_at_drive` takes the
regime as a required argument with no default, and
`results/projections.csv` carries the aperture reading in its cells with the
resonator reading quoted beside it in the note, so every multi-drive number is
a bracket until the profile exists.

### The EOM bore's distance before the focusing lens

**State of knowledge.** [APPARATUS.md](../APPARATUS.md) places the EOM's 3 mm
bore ahead of the first f = 150 mm lens (section 1.2) and states no distance
between them. Paraxially the bore-to-lens distance `d` sets the focus's axial
asymmetry, which goes as `(1 - d/f)`: at a 2.46 mm input the axial intensity
peak sits 0.80 mm toward the lens at `d = 0`, on the focal plane at `d = f`
and 1.54 mm beyond it at `d = 3f`, against a collection half-window near
3.4 mm (an independent Collins-integral computation, 2026-09-22). The
focal-plane intensity itself does not depend on `d`, so the bore-limited
central waist and its band are unaffected. What moves is where along the axis
the peak sits relative to the collected length.

Bearing on the forecast. A shifted axial peak moves the effective
collection geometry the campaign's ramp and kernel machinery assume, at a
scale, 0.8 to 1.5 mm, that is a sizeable fraction of the 3.4 mm collection
half-window above. Nothing today reads `d`, so every axial-window calculation
in this record implicitly assumes whichever default the field call carries.

**Closure.** A ruler measurement of the bore-to-lens separation, on the same
afternoon and the same optical-bench access as the other open distances this
chapter lists, with no atoms and no lock.

**Treatment in the forecast.** The model carries `d` explicitly:
`rb5s6s.beam_field.ClippedBeam`'s `d_ap_m` parameter, defaulting to 0.0 (the
`d = 0` case) to match the existing focal-plane table until the distance is
read off the bench, and spans it in the twin's world beside the input beam
radius above.

### Composition of the transit kernel and light shift

The twin's line composes the transit kernel with the ramp as a convolution.
Computed on rung 3 against the two-time correlation spectrum of a chirped
chord with the dephasing carried (chapter 4's closing block), the composition
leaves the mean exactly the composition's at every waist (rung 2, the first
moment of the two-time spectrum), holds the archive's width and interior
residual to a fifth of a per cent, narrows the line by about two per cent at
the campaign's tightest waist, and adds ten to twenty per cent to the
collection window's third moment there. **What settles
it.** No bench time: the second-order coherent term derived for the methods
chapter, the chord harness landed as a producer with its table and a
convergence arm so the figures become the record's, and the world builder
carrying the two-time line above half a transit width of shift together with
the collection window, which is the larger omission. **Cost.** Analysis days.

Until then the forecast's width at a tight waist carries a two per cent model
term and its coefficient stands at the forecast's own precision.

### The saturation companion's steady-state form at a tight waist

The companion width the twin carries is the steady-state power broadening of
a two-level system, and the note that derives it licenses that form at the
archive's waist because the chord there is about ten natural lifetimes. At
the campaign's 16 micron waist the chord is a quarter of that, between two and
three lifetimes, so the excited fraction has not reached its steady value when
the atom leaves and the steady-state companion overstates both the width and
the rate there. **Settlement.** Nothing on the bench: it is a derivation,
the transient two-level response along a Gaussian chord, owed to the methods
chapter before the 16 micron cells are quoted. Raised by an external reading on
2026-09-06.

**Partly answered, and at the archive's waist too (F324, 2026-09-22).** The
optical Bloch equations integrated along each atom's crossing, at five nodes
over 41 to 45 um, 70 and 130 C and 125 and 225 mW, give a collected line whose
saturation is still one extra homogeneous Lorentzian, at an effective Rabi
frequency near half the on-axis one: the steady-state average over the
collected atoms, a closed form, times the crossing's own transient, which is
the coherence's lag and not a population's. So the steady-state form at the
on-axis Rabi frequency is not licensed at the archive's waist either, and the
premise above, ten lifetimes along the chord, does not rescue it. The model
takes the ensemble's scale in its next window, with the companion among the
readings a kernel node must pass on a coarse set of Bloch nodes (plan A134).
The 16 micron cells still wait for the same integration at their own waist.

### The analog chain's linearity at the peak rate

The amplitude against density runs sub-linear across the 2025 grid, and two
mechanisms bend it the same way: radiation trapping, which follows the optical
depth (chapter 10), and the detection chain's linearity, which follows the
rate. The chain is analog, a photomultiplier into a transimpedance stage into
the oscilloscope, so a counting dead time does not apply to it, and what would
is the photomultiplier's and the pre-amplifier's linearity at the peak anode
current, which the record has not MEASURED. The pedestal separates the two,
since its rate is hundreds of times below the peak's and free of any rate
effect while it shares the optical depth: a peak-to-pedestal ratio that moves
with density at fixed rate is trapping, one that moves with rate at fixed
density is the chain.

**Settlement.** A neutral-density ladder in front of the detector, which
is the one attenuation that changes the rate without touching the light shift
or the saturation, at one condition. The counting chain of chapter 10 run
beside the analog one on the same photons answers it too. The curvature of the response
against attenuation gives the chain's own deficit with no lineshape model at
all. **What it is not**: a counting dead time. That mechanism is
absent from an analog chain, and at the peak photoelectron rate chapter 10
inverts from the committed noise law, a few hundred thousand per second, a
three-nanosecond dead time would cost about a tenth of a per cent, where a
megacount-per-second rate would imply several. **Cost.** An
hour at one condition. Raised by an external reading on 2026-09-06, which proposed a
counting dead time the chain cannot have.

### The detection chain's time constant

State of knowledge. [Chapter 10](10_the-fixed-lock-instrument.md) bounds the
chain faster than 10 microseconds at 10^6 V/A from the rehearsal's LeCroy
traces, a bound at that instrument's sampling limit and not a curve. **What
is not.** The time constant itself, at the gain the next session uses.

**Bearing on the forecast.** Whether a full-span triangle can be swept fast enough to
put many line crossings in one record. On the bound as it stands, a lag of
10 microseconds costs a third of a per cent of width at 12 MHz per ms and
17 per cent at 120, and a triangle over the four peaks' 5.2 GHz sweeps
10 MHz per ms at 1 Hz and 100 at 10 Hz. The campaign's proposed settings,
24 to 6000 MHz per second, all sit far below the first figure, so the bound
admits every one of them and chapter 9 is right that the chain does not bind
them, while a 10 Hz full-span triangle would be refused and nobody proposes
one. The atomic cascade lag, about 72 ns, costs under a hundredth of a per cent of
width at either and a tenth of a per cent as a shift at the faster, and never
enters.

Until the time constant is MEASURED, a setting
above about 20 MHz per ms, three times the fastest proposed and where the
lag's width cost approaches one per cent, is forecast across the bound and not
at a value. The ceiling of 8.1e6 MHz per second the piezo item above quotes
for the chain rests on an assumed constant, and this bound replaces it.
[Chapter 7](07_acquisition-settings.md) and
[chapter 9](09_the-fixed-lock.md) carry the consequence.

### Synchronisation of the radio-frequency gate

The oscilloscope records four channels and the campaign has five things worth
recording. Three supply information nothing else does: the cell fluorescence,
the ramp monitor and the cavity error signal. The fourth is contended between a
marker for the modulator state and a second detector. If the modulator's
radio-frequency drive can be gated from the same trigger that starts the
sweep, its state is a known function of the sample index, the marker records
something already known, and the channel is freed for a second platform's
detector on paired blocks or for the retro-reflected power on cell-only ones.
If it cannot, the marker is mandatory and a second detector needs a second
instrument. **What the record can say without it is nothing**: it is a
property of the drive electronics and the trigger distribution on this bench.
**Cost.** One afternoon with the drive and the trigger, no atoms, and the answer
is a yes or a no.

### Sweep nonlinearity and hysteresis of the piezo

The rate variation across an analysis window that forges the whole light-shift
signal in the third moment is computed in
[chapter 7](07_acquisition-settings.md): about one and a half parts in ten thousand
at the campaign's tightest licensed waist and about 1.4 parts in ten thousand
at the 2025 configuration. The nonlinearity that matters is the actuator's own over its
travel, and the span scanned does not enter it, so what is needed is the
piezo's departure from linearity as a fraction of its full travel and the
hysteresis between the two halves of a triangle. The 40 micron tolerance
assumes the unclipped design, the bore out of the focusing path. A bow of
two per cent fails it by 1.6 and ten per cent fails it by about eight, so an
open-loop actuator needs its bow MEASURED from the anchors the sweep crosses
and taken out.

A ripple of fifty cycles at a tenth of a per cent exceeds the
tolerance three hundredfold and is what the ramp monitor is for. **Cost.**
The bow from the anchors is free once the ramp is recorded. A linearised
actuator is a purchase the answer decides.

### Availability of the R&S RTM3004

Chapter 7 names it the instrument the design wants, on three documented
counts: disjoint high resolution at sixteen-bit words, a record-length menu,
and history segments that capture a whole ladder without touching the
horizontal control. Whether it is available to this bench for the campaign's
weeks is a fact the record does not hold. If it is not, the four-peak traces
go to the LeCroy run raw, as chapter 7 already provides. **Cost.** A question
to whoever holds it. The design works either way and the difference is the
LeCroy's two lost bits.

### Cost of closing each item

The lock residual is the cheapest and the highest leverage. It needs no
atoms: step the lock, record the recovery, and read an Allan deviation of line
centres across a session. [Chapter 9](09_the-fixed-lock.md) already specifies
it. Until it exists, every centre-channel forecast in this repository is
reported across a span instead of at a value.

The waist closes in an afternoon with no atoms at all, and it is the one
measurement that sharpens every existing bound at once. The atom-based route
beside it in the row above costs a 778 nm diode and one session with atoms,
and it is a check on the first route and not its replacement.

The chain's time constant closes in an hour with a step response on the
3104z's deep fast record and no atoms, chapter 10's second item, and it is
what decides how fast the deep trace of chapter 7 may run.

The beam's mode at the cell closes with one camera image, taken at a plane
equivalent to the interaction volume, and the aperture closes with the same
ruler as the distances below. **The input beam at the lens closes with the same
camera on the same afternoon**, and it is the item that decides whether a
cross-transition ratio is quotable at all.

The collection distances close in a minute with a ruler, and they are the
only items on this page already carried into a committed result instead of
being spanned around it.

### The collection solid angle

The collection solid angle, which the record has never MEASURED, is the open item of this
section, and a board deferral of 2026-09-16 points here for it.

The deferred finding in its own words: the profile integral counts fluorescence outside the
record's collection window. The collection solid angle, which the record has never measured, is
the quantity that closes it, and this section carries the debt until a measurement exists.

**The gap.** The platform table's fluorescence rows multiply the
emitted rate by 0.341, and that number is the fraction of the emission inside
the axial collection window, `2 arctan(z_ratio) / pi`, derived in
`results/prediction_band.csv` from the lens and the cathode. It is not a solid
angle, and no solid angle enters anywhere. So every absolute fluorescence rate
in that table is an upper bound by whatever fraction of the emitted sphere the
collection optics actually subtend.

**Requirements for closure.** The collection lens's clear aperture and its
distance from the beam, which together give the subtended fraction. The
transmission of the filter stack at 795 nm. And whether a second element or a
condenser sits in the path. All are bench facts.

**Consequences.** The absolute fluorescence signal-to-noise of the cell, the
trap and the molasses rows, by one common factor, so it does not move any
comparison between those rows, and it moves every comparison against an
absorption row. The axial window's own weighting is a second, smaller question:
0.341 is computed on the ramp's axial weight, and the table now integrates the
saturated rate, whose weight is different.

### The detection budget from the bench facts

State of knowledge (owner, 2026-09-13): the 795 nm photons are collected by
an f = 18 ± 1 mm lens at 50 ± 5 mm from a 3 × 12 mm cathode whose quantum
efficiency in the chain is 6 ± 1 per cent. `results/detection_budget.csv`
(`scripts/run_detection_budget.py`) writes the chain out. The object plane
sits [28.12](../../results/detection_budget.csv "ref:detection_budget:object_distance:along12") mm from
the lens and the collected length along the beam is
[6.75](../../results/detection_budget.csv "ref:detection_budget:collected_length:along12") mm with the 12 mm
dimension along it (the record's reading) or
[1.69](../../results/detection_budget.csv "ref:detection_budget:collected_length:along3") mm with the 3 mm
dimension along it (the owner's 2026-09-12 "portrait"), the two readings still
open above.

The waist power the signal carries, derived. The integrated weak-drive two-photon signal
in a collected length $L$ is $(P^2/\lambda) 2\arctan(L/2z_R)$: the prefactor holds no
waist, and the whole dependence sits in the arctangent, whose logarithmic slope in the
waist runs from $-2$ where $L \ll z_R$ to $0$ where the Rayleigh range sits inside the
window. At 42.38 µm that slope is [-1.638](../../results/detection_budget.csv
"ref:detection_budget:exponent_weak_drive:along12_w42.38um") (12 mm along) or
[-1.971](../../results/detection_budget.csv
"ref:detection_budget:exponent_weak_drive:along3_w42.38um") (3 mm along), and with the
archive's own saturation carried on the strong-drive integral it is
[-1.364](../../results/detection_budget.csv
"ref:detection_budget:exponent_saturated:along12_w42.38um").

The on-axis rate per atom goes as $w_0^{-4}$. The mode holds $w_0^2 L$ atoms, which is
where two of the four powers go. Along the campaign's ladder the slope weakens to
[-0.340](../../results/detection_budget.csv
"ref:detection_budget:exponent_weak_drive:along12_w16um") at 16 µm in the weak-drive
form and changes sign, [0.606](../../results/detection_budget.csv
"ref:detection_budget:exponent_saturated:along12_w16um"), once the centre saturates, so
the absolute amplitude is a waist channel at the archive's geometry and not at a tight
one.

A 15 per cent absolute budget at the
archive's orientation would hold the waist to
[9.2](../../results/detection_budget.csv "ref:detection_budget:waist_from_a_15pct_budget:along12") per cent.

**Position of the MEASURED rate.** The noise law's shot term gives the
photoelectron rate per volt as $2FB/b$ with neither the gain nor the
transimpedance needed, $B$ the boxcar's 1 kHz and $F$ the excess-noise factor
at one. At the 4192 line and 225 mW the peak reads
[8.97](../../results/detection_budget.csv "ref:detection_budget:measured_pe_rate:4192_P225") ±
[0.90](../../results/detection_budget.csv "ref:detection_budget:measured_pe_rate:4192_P225:err") million
photoelectrons per second. The chain's prediction (the excitations in the
collected length at that line's share of the atoms, the branching, the
aperture's solid angle, the quantum efficiency, with $f$, the image distance and
the quantum efficiency drawn) exceeds it by
[3.15](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along12_D6mm") ±
[0.22](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along12_D6mm:err")
in the log at a 6 mm aperture and
[4.35](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along12_D25.4mm") ±
[0.22](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along12_D25.4mm:err")
at the largest aperture spanned, one inch (12 mm along, and [2.59](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along3_D6mm")
to [3.78](../../results/detection_budget.csv "ref:detection_budget:gap_log10_predicted_over_measured:Steck_along3_D25.4mm")
with 3 mm along).

Exclusions from the gap, by name: the filter's
transmission, the excess-noise factor, the retro ratio's span, the density law
(the Alcock form adds under a tenth of a decade), and the D1 photons' own trapping, whose
optical depth is [22.47](../../results/detection_budget.csv "ref:detection_budget:D1_optical_depth_per_mm:Steck")
per millimetre at 130 °C on the envelope cross-section, so the emission the
lens sees is the cell's and not the beam's, and the collected fraction of a
trapped emission is unpriced. **What closing it needs**: the clear aperture,
the filter's transmission and the cathode's orientation (above), the
excess-noise factor from the datasheet, a photon-transfer gain calibration on
the campaign, and the trapping cell owed to `trapping_channels`. The image
distance's one-sigma is 5 mm in the owner's 2026-09-13 statement and 10 mm in
`constants.COLLECTION_IMAGE_DIST_ERR_M`, which the prediction band's committed
cells still rest on.

### Linewidth in the saturation parameter

The saturation parameter's linewidth is a modelling item and not a bench one, and a board
deferral of 2026-09-16 points here for it.

**The defect.** `platforms.excitation_rate_per_atom` takes
`s = 2 (Omega / Gamma_nat)^2`, so the resonant rate goes as one over the
natural width alone, while the same row carries a transit width of 3.83 MHz
beside a natural 3.49. The detuning-integrated weak-drive rate is fixed by the
Rabi frequency alone, so the peak rate scales as one over the total homogeneous
width. On the record's own kernel (the archive point's collisional and laser widths with each
row's transit and light shift) the composite width over the natural runs
1.54 at the calculated 42.4 microns, 2.20 at 19 and 2.74 at 16, and every rate, saturation <!-- other-quantity: a composite-to-natural width ratio, not the predicted coefficient -->
parameter and absorbed fraction in the platform table is overstated by that
factor at its own waist.

**Grounds for listing, not fixing.** It predates the wave that found it
(2026-09-11), it moves every cell of a committed table and the three pages that
cite it, and `scripts/run_waist_ladder.py` already carries the right
construction, so the repair is a migration and not a derivation. It is the

**The regime beneath it.** The three-level steady state those rates assume
needs the atom back from 5P and driven again while it is still in the beam. At
the tight-waist row the chord time is about 102 ns against a 72.3 ns cascade
dead time, a ratio of 1.4, so the atom leaves in under two cycles. The table's
note says the row sits outside the approximations and does not say which. This
is which.

### The trapping producer's cascade copy

`rb5s6s/detection.ir_branching_5p12` computes the 6S branching from the
package's matrix elements and reproduces the committed cell to four parts in
ten million. `scripts/run_trapping_channels.py` still computes the same
quantity from its own `_leg` and its own copies of four SI constants. The two
agree by retyping and not by wiring. Migrating the producer also moves the
halo and escape-factor arms that read those literals, so it is its own change.

### Quality factor of the drive beam

The open part. The beam-quality factor of the drive at the cell. Nothing in
this record has MEASURED it and no function takes it as an argument, so every
waist-dependent quantity assumes a diffraction-limited beam.

**Bearing, and where.** It enters in one place, the Rayleigh range, which
goes as the waist squared over the quality factor. Everything axial follows: the
collection window's ratio, which the record carries as a signed correction with
two sign reversals, the fringe Monte Carlo, and the kernel spread that licenses
writing the model as a convolution. Because the window ratio goes as the quality
factor over the waist squared, the strain falls on a *small* waist with a poor
beam. At 55 microns the third moment keeps 86 per cent of its value at a
quality factor of 1, 48 per cent at 2, and reverses sign past 3.17. At the
calculated 42.4 microns the reversal needs 1.88 and at 85 it needs 7.56, so at
the calculated waist a beam of quality near 2 already reverses it.

**The bench's diffraction limit in question.** The drive passes a
modulator whose clear aperture is 3 mm, sourced from the manufacturer's own
table, with an input radius of 1.5 mm, so the aperture sits at the beam's
$1/e^2$ radius and transmits 86.5 per cent. A viewer-card observation of
clipping there is on record as a recollection and not a measurement.

**Closure.** One afternoon with a commercial beam profiler, on the
same bench and ideally in the same session as the knife-edge waist measurement,
since the two answer one question between them and neither needs atoms, a lock
or a cell to be running.

**Forecast treatment until then.** It spans the pair. A working region of 55
to 85 microns with a quality factor under about two keeps every term inside its
licence with a factor of two to spare, and that pair, not an interval in the
waist alone, is what the guided and tight-waist cases are sized against.

A second route reaches the same bound, 2026-09-12. The paragraph above sizes
the pair on the third moment's sign reversal. The convolution licence sizes it
independently, on the rms spread of the transit width over the collected region:
that spread is 1.73 per cent at 55 microns and a quality factor of 1, 3.61 at
1.5, 4.70 at 1.75 and 5.84 at 2.0, against the 5.5 per cent edge the record sets
at 40 microns. **The bottom of the band leaves the licence at a quality factor
of 1.93**, which is the "about two" above reached through a different term.

(The convolution licence inverted directly from `collection_z_ratio_m2` puts the
same edge at 1.891 for this waist: the two routes agree to three per cent and<!-- other-quantity: a waist edge, not global_dataset_fit's per-peak sigma_laser in MHz. The digits coincide -->
the difference is the spread model, not a disagreement about the bound.) The
joint condition is `w0 >= 40 um * sqrt(M^2)`: 49 microns at 1.5, 57 at 2, 69 at
3.

So the waist band and the quality-factor bound are one assumption, not two,
and writing either alone writes half of it.

The threshold is a band, not a line. The collection ratio carries its own
uncertainty from the optics: `L/z_R = 0.59 +- 0.35` at a quality factor of 1
(`results/prediction_band.csv`), propagated from `f = 18 +- 1` mm, an image distance
of `50 +- 10` mm and the 40 to 45 micron waist band, which is 59 per cent relative.
At the calculated waist the licence boundary of 0.667 therefore sits inside the error
bar already at a quality factor of 1, and at 2 the central value, `1.19 +- 0.70`, is
outside it, so no clean yes or no is available anywhere in the band. A fit reports
the probability its licence holds, never a sharp verdict against a 59 per cent input.

### Tilt of the retro-reflection

Two counter-propagating photons cancel the first-order Doppler shift only when
they are exactly anti-parallel. At a tilt $\theta$ the residual two-photon
wave-vector is $2k\sin(\theta/2)$, so the Doppler-free line regains a Gaussian
width of that times the thermal speed. Derived, not simulated, at 110 °C. **The angle in this table is the crossing angle at the atoms**, which is what the residual Doppler width is set by. A mirror tilt reaches it multiplied by `2(1 - d/f)` = 4/3 for the bench's 50 mm and f = 150, so a mirror tilt of 3.2 mrad is a crossing angle of 4.27 and gives 1.94 MHz, not the 1.45 the mirror angle alone would give:

| tilt | residual FWHM | against the transit at 42.38 µm |
|---|---|---|
| 0.5 mrad | 0.23 MHz | 0.16 |
| 1 mrad | 0.45 MHz | 0.32 |
| 2 mrad | 0.91 MHz | 0.65 |
| 5 mrad | 2.27 MHz <!-- other-quantity: this table's own retro-tilt residual-Doppler width, not a detection-budget gap --> | 1.61 |

No forecast rests on it: these are the term's size at tilts nobody MEASURED,
and no committed cell carries a mirror tilt.

A milliradian is half the transit width and two milliradians double the
line. But the tilt this bench can have is bounded far below that, and the
bound is already MEASURED.

The offset binds long before the Doppler does. The retro mirror sits about
50 mm from an $f = 150$ mm lens, so $d/f = 1/3$ and this is not a cat's eye,
which would need $d = f$ and turn a tilt into pure displacement. Propagating a
mirror tilt $\theta$ back to the atoms gives a lateral offset
$2\theta[d + s(1 - d/f)]$, which is **300 mm per radian**, so the two beams walk
apart at the atoms 300 times faster in position than they tilt in angle.

| mirror tilt | offset at the atoms, in waists | overlap |
|---|---|---|
| 0.1 mrad | 30 µm, 0.47 | 0.80 |
| 0.5 mrad | 150 µm, 2.34 | 0.004 |
| 2.36 mrad | 708 µm, 11.1 | $7\times10^{-54}$ |

No forecast rests on it: the offsets are the geometry's own arithmetic, not a
bench measurement.

Nothing measures the overlap, and $\rho$ is not a measurement. The retro
ratio carried in `constants.RHO_RETRO` is an assumption of 0.94, and the
epistemic ledger records it as never informed by these data. The area ratio that
*would* measure it needs the Doppler pedestal, which is 931 MHz wide, and the
archive's traces span under 100 MHz, so they cover about a tenth of it and see a
flat offset in their wings. **The wide scan that would measure $\rho$ is the
same one the pedestal needs, and neither has been run.**

What does bound the tilt is the line's own presence, and it needs nothing
assumed. The only premise is that the Doppler-free signal is there and not
suppressed beyond some factor:

| narrow line at | offset | tilt | residual width | against the 1.07 MHz gap |
|---|---|---|---|---|
| 90 % of aligned | 21 µm | 0.069 mrad | 0.031 MHz | 34× short |
| 50 % | 53 µm | 0.178 mrad | 0.081 MHz | 13× short |
| 10 % | 97 µm | 0.324 mrad | 0.147 MHz | 7× short |
| 1 % | 137 µm | 0.458 mrad | 0.208 MHz | 5× short |

No forecast rests on it: the rows are what the narrow line's own presence
allows, and no committed cell depends on any of them.

The term is self-limiting: the same misalignment that would supply the
missing width destroys the signal that carries it. Even at one per cent of
aligned strength the tilt supplies a fifth of the gap. So it is disfavoured as
the whole answer, not excluded as a contributor, and the gap stays open. No
forecast rests on it: the 2.36 mrad is the tilt a refuted hypothesis would have
needed and not a bench number, and nothing in `RESULTS/` carries it.

The standing wave is where this should be tested, and nobody has.
The fringe Monte Carlo assumes a perfect retro and has no offset axis. Under a
tilt the fringe planes rotate by $\theta/2$ and gain a transverse period
$\lambda/\sin\theta$. With the beams offset the local contrast
$2\sqrt{I_1I_2}/(I_1+I_2)$ is unity only on the bisector. And near the focus the
two wavefronts no longer match, which washes fringes out over the interaction
volume by a third mechanism. The fringe-resolved suppression the record carries,
about 7 per cent at this waist, is a contrast-weighted quantity, so all three
reach it.

Measured, 2026-09-12, by `fullmodel.fringe_survival_mc`, which carries all
three and reduces to the ideal contrast at zero tilt, zero offset and unit beam
quality. **The tilt angle is negligible and the offset is not.** The transverse
fringe wave-vector $k\sin\theta$ is four orders below the axial $2k$, so at
0.5 mrad the mean fringe survival moves by under 2 per cent, while an offset of
one waist takes the mean contrast from 0.9995 to 0.836. Beam quality enters
through the axial sampling instead, taking the mean radius over the collected
region from 1.011 to 1.083 waists <!-- other-quantity: a mean radius in waist units, not paired_reference_forecast's width_err_ratio --> at $M^2 = 3$ and the survival down by 6 per
cent. What a tilt does to this bench, it does through the offset it produces.
The wavefront mismatch is still not modelled, so these are an upper bound on the
fringe effect at non-zero tilt.

**The item's purpose.** The tolerance itself, for the campaign. The
offset per unit tilt does not change with the waist while the waist does, so a
tighter focus makes the alignment requirement proportionately sharper: at 16 µm
the same 0.053 mrad costs a quarter of the overlap and not six per cent.
That is a real constraint on the tight-waist configuration and it was not
written down.

**Closure.** A shear-plate or far-field overlap check at the cell,
minutes, with the residual walk-off recorded. The data alone already bound it
through $\rho$, which is why this is a tolerance to respect and not an unknown
to span.

**Forecast treatment until then.** `rb5s6s.fullmodel.residual_doppler_fwhm_mhz`
carries the term and `build_world_trace` takes it as an opt-in argument, off by
default, so the campaign case and the Sobol ranking can weigh it against the
waist instead of assuming it away.

### The modulator's amplitude admixture

**Owner-stated, 2026-09-12.** The polarisation axis into the modulator was
tilted deliberately, to give phase-amplitude coupling, so that the carrier would
not bury the other teeth even at small modulation depth. The residual amplitude
modulation this record measures is therefore the intended consequence of a
control that was exercised, and not an imperfection of the device.

**Consequences.** The ruler chapter localises the admixture to the carrier
and reports its height running from 0.360 to 1.188 of the first order across the <!-- other-quantity: the carrier's height against the first-order tooth, not the light-shift prediction -->
clean combs, standing taller than the first order on ten of forty-one, while the
second-to-first ratio holds to four per cent. Read as a defect that scatter is a
purity failure to be bounded. Read as a setting it is the signature the tilt was
introduced to produce, and the contrast between the carrier's spread and the
second-to-first ratio's tightness is what a deliberate phase-amplitude coupling
looks like.

What it does not do is retire the comb as a lever (owner, correcting a
first reading of this item the same day). The coupling redistributes power among
the teeth and modulates it at the drive frequency, but the time-averaged total
is unchanged and stays at the operating power. The transit is about 260 ns
against a 12.5 MHz drive, so the atoms respond to that average, and **the light
shift is the same with the modulator on as off**. What the admixture breaks is
the prediction of the tooth shares from $J_k^2$, not the constancy of the total.

And the shares are observable, which is better than predicting them. A
two-photon height goes as the share squared, so each tooth's share is read from
the same trace it is used on. The lever therefore stands with a MEASURED
abscissa instead of a nominal depth. From the comb the ruler chapter measures,
heights $0 : 1.00 : 0.69 : 0.15$ at $k = 0, \pm1, \pm2, \pm3$ with the carrier
at 0.360 to 1.188 of the first order, the tallest tooth carries **0.18 to <!-- other-quantity: the carrier's height against the first-order tooth, not the light-shift prediction -->
0.20**. At those shares the saturation companion sits **25 to 31 times** below
the unmodulated line's, at identical light shift, collisional width, laser
width and transit. Nothing else in this model separates saturation from the
Lorentzian sum.

[The ramp chapter](../methods/03_the_ac_stark_ramp.md) already designs its first
test to measure the admixture and never assume it away, which is the correct
handling and is unchanged by the intent. What the intent adds is that the
admixture will not be reduced by a better modulator, because it was not the
modulator.

The remaining open part: the tilt angle itself, which nobody recorded, and
therefore the size of the coupling as a number and not as a MEASURED
scatter. No forecast rests on it: the comb enters the analysis as a frequency
ruler, whose calibration the second-to-first ratio carries and the carrier does
not.

### The flat floor under the comb

The comb's MEASURED tooth shares reject the pure phase-modulation law
$J_k(2\beta)^2$ at a reduced chi-squared of
[6.11](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:chi2_red_depth_fixed:")
± 0.58, and a *flat pedestal* carrying
[0.0479](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:pedestal_fraction_of_comb:")
of the comb's power fixes it completely
([the ruler chapter](../methods/05_the_frequency_ruler.md)). Letting the
modulation depth float does not. What that floor is was not determined: the
MEASURED shares at $k=\pm3$ differ by [-0.0001](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:tooth_share_antisymmetry:k3"), which refuses an
antisymmetric excess of the observed $|k|=3$ size there and leaves a small one
open at $|k|=2$,
and scattered light, a
detector offset and an unresolved broad background all reproduce it equally
well from the shares alone.

**Bearing beyond bookkeeping.** The floor puts about 0.68 per cent under
every tooth slot, against a third-order tooth standing at [0.58](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:signal_over_pedestal:-3") of that floor, so the
$k=\pm3$ teeth sit below it and cannot carry a rung of a depth ladder. That
cuts the ladder's usable span from about seventy-fold to
[5.51](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:usable_rate_ladder:"),
which is still enough for the saturation measurement the ramp chapter sets out,
but a design that assumes the third orders is designing on a floor.

Read it as conditional on a cut over the same teeth. The combs kept are
those whose calibration verdict passes, which is an amplitude verdict on the
teeth being fitted, and keeping every non-excluded comb moves the floor to about
nineteen per cent. The dropped combs rail against the fit's own bound rather
than sitting at a different value, so the cut separates a population the law
describes from one it does not, and the number above belongs to the first.

Two origins are already excluded, and the leading one is not optical. The
comb fit carries a linear baseline under the teeth, so a flat background or a
detector offset is absorbed by it. The third-order heights sit at about 0.4 of
the fit residual, below unity signal-to-noise, where a non-negative height
estimator has a positive expectation under noise alone of about the residual
size, against a fitted floor per slot of about 0.35 of it. So this may be an
estimator artefact and not an APPARATUS fact, which changes what the test
below can settle.

Closure, and it is cheap. Block the modulator drive and record
the same trace: a floor that survives is scattered light or a detector offset,
one that vanishes is optical. Then repeat at two detector gains, since an
offset scales with gain and scattered light does not. Neither needs atoms, a
lock, or more than an hour.

### The guided-platform items

The nanofibre arm has open items of its own, and they are listed in the fibre
thread and not here so that a reader with no fibre keeps the skip promise
of [BIG_PICTURE](../BIG_PICTURE.md):
[chapter 6](../big_picture/06_next-nanofibre.md).


---


## Waist estimator validation on noisy synthetic traces (2026-09-19)

The waist estimator's closure was climbed to three noise levels on the repaired whitening. The rung table
and its two readings live in [injection and recovery](../wiki/injection-recovery.md), which is where the
injection analysis belongs, and its 2026-09-20 withdrawal is recorded there and below.

Two readings followed, on the bias's growth with noise and on the bars' calibration. Both live in
[injection and recovery](../wiki/injection-recovery.md) with their numbers, and the 2026-09-20
re-measurement recorded there and below replaces both.

### The waist closure's open offset (2026-09-20)

The closure was climbed to three noise levels and the offset it shows is still unexplained. The scaling
analysis, the prior's exoneration and the rung tables all live in
[injection and recovery](../wiki/injection-recovery.md). The readings taken before the whitening repair
no longer stand, and the 2026-09-20 re-measurement replaces them.

What the open item carries today: the offset is absent at zero noise and appears with it, so it is not a
term of the forward model by the argument that was made for one. It does not grow as the square of the
noise either, which is what a finite-sample estimator bias must do, so it is not that. No twin-subtracted
waist is quoted at any noisy rung, and the interval's coverage reads well under nominal, which makes the
bar the next quantity to interrogate. **This is the open item that gates every absolute number on this
page, and the external measurement of the waist is what would close it independently of the fit.**


## The drive power measurement point

**OPEN, and it is worth more than the focus width.** The bore transmits 51.5 per cent of an ideal
Gaussian at the bench's input radius and 26.1 per cent of an LG(1) of the same scale, so two input beams
of one beam-quality number deliver light differing by a factor of two. `S0` goes as the transmitted
power over the focal radius squared, so at one `M^2` the composition moves the light shift by about 2.5.

**Which of two questions that is depends on one bench fact.** If the recorded 225 mW is read after the
modulator, the transmitted fraction divides out and only the focal radius matters. If it is read before it,
the composition enters every `S0` the record holds. A power meter after the modulator is already wanted
here and is not on record, which points at the second.

The owner is the instrument for this one. Until he states it, the twin spans both conventions.

## The cell's glass, wall thickness and sealing date (2026-09-23)

What is unknown. Which glass the 2025 cell is made of, how thick its wall is, and when it was
sealed. The record discusses borosilicate permeation as a documented drift
([`docs/APPARATUS.md`](../APPARATUS.md)) without stating any of the three for this cell.

Why it bounds a term of the model and not a detail. The permeated gas enters the line as
a constant Lorentzian, and its temperature behaviour is set by the permeation clock, not
by the collision. That clock is Arrhenius ([`carle2023`](../lit/carle2023.md), an
activation energy measured at three temperatures), so a sealed cell's time constant
falls by about an order of magnitude across the 70 to 130 C ladder. Scaling
[`feng2026`](../lit/feng2026.md)'s own borosilicate figure for a cell of comparable
geometry puts it at weeks near the cold end and a day or two near the hot one, and
[`carle2023`](../lit/carle2023.md)'s microcells are slower again while their
aluminosilicate is slower by orders.

A cell that has equilibrated at room temperature sheds helium when heated, because a
fixed amount in a fixed volume puts its internal partial pressure above the
atmosphere's. Across the ladder that is a change in the gas's own content of the
opposite sign to the velocity average of the collision, and of the same size. The
arithmetic and its figures are in the private finding record. This page states the
consequence and not the numbers, because they rest on a borrowed permeability and this
cell's glass is the unknown.

What would close it. The cell's fabrication record: the glass, the wall thickness and the date.
Failing that, a repeat of one temperature block after a long hold at that temperature, which reads
the clock directly from the line, with no permeability table needed.

How the forecast spans it meanwhile. The permeated gas's temperature exponent runs as a
model-form arm with a negative branch, not as a fixed velocity exponent, and no number is quoted for
its drift across the ladder.

---

*[Beyond 993 nm](11_beyond-993.md) · [the PLAN](../PLAN.md)*
