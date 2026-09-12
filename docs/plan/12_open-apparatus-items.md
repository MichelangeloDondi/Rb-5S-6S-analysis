*Chapter 12 of 12 of [the plan](../PLAN.md)*

**The question.** Which cell-side numbers has nobody measured, what would each change, and how does the forecast proceed without them?
**Takes.** Every chapter that quotes an apparatus number, chapters 3, 4 and 9 above all.
**Gives.** The open list, the cost of closing each, and the span the forecast uses in place of a value.
**Skip if.** You want the measurements that are already made, which are chapters 3 to 11.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 13. The open apparatus items, and how the forecast handles each

Every cell-side number in this plan that nobody has measured is listed here,
with what it would change and how the forecast proceeds without it. The
guided-platform unknowns live in the fibre thread, per the skip promise
[the big picture](../BIG_PICTURE.md) declares. **An open item is
spanned, never assumed**, and the span lives in a committed producer so a
reader can see how far the answer moves across it.

**This chapter exists because the alternative failed.** On 2026-08-28 a
forecast of the next campaign used the 2025 archive's lock drift rate as
though it described the repaired lock. The apparatus had changed, this plan
already said so in two chapters, and the forecast contradicted the plan
instead of reading it. A list of what is genuinely unknown is what stops the
next session inventing a value, or asking for one nobody has.

| item | status | what it changes | how the forecast proceeds |
|---|---|---|---|
| **repaired lock, residual drift** | not measured. The lock was repaired 2026-08-16 and no longer drifts. Its rate is unknown, and [chapter 9](09_the-fixed-lock.md) section 10c.2 already calls for measuring it | every centre-channel measurement on either platform. Absolute line centres become available with a stable lock, which is what the 2025 campaign could not do | spanned from 0 to 40 kHz per minute, with the recovered precision reported at each point, in `results/projections.csv` and its guided-platform counterpart |
| **repaired lock, per-sweep excursion** | not measured. The same characterisation run [chapter 9](09_the-fixed-lock.md) calls for reads it beside the drift | every centre measurement on either platform rides it, as the drift row above | spanned in the fibre thread ([the campaign chapter](../big_picture/09_the-campaign-cases.md)): its paired-acquisition forecast covers the comb best-fit class to the wavemeter ceiling and the acquisition-geometry verdict there turns on exactly this item. The cell-side three-channel forecast now spans the drift over a tenfold range and finds the pull channel's spread unmoved, because the twin generates the drift as strictly linear in acquisition order and the fit carries that order as a free nuisance, so the term is a column of the design matrix and costs nothing. **The lever's worth cannot be established until the world's drift has structure**, which is the modelling item below |
| **the cell's own dimensions** | owner-stated 2026-09-09 as about 25 mm bore and 100 mm long, a standard size not measured precisely, with the beam about 2.0 plus or minus 1.0 mm from the wall; carried in [the apparatus chapter](../APPARATUS.md) | they set how often an atom returns to the beam against how often it reaches a wall, which decides whether the vapour around the beam is hyperfine-pumped in steady state; the cascade model assumes each atom arrives unpumped | no forecast rests on it, and the span is why: over every plausible cell an atom reaches a wall many hundreds of times between beam crossings, and an uncoated glass wall relaxes the hyperfine state on adsorption, so atoms arrive reset whatever the dimensions are. The item is recorded because the argument for that needs a number the record does not carry, not because a result does |
| **beam waist in the interaction volume** | not measured in this cell. The working 64 um is a same-conditions measurement from an earlier thesis on this apparatus lineage | the largest open systematic in the record. Every intensity-denominated number rides it | spanned across the band the data allow in `results/transit_mc.csv`, and [chapter 5](05_width-collision-amplitude.md) specifies the profile measurement that closes it. A second, atom-based route in the cell itself: a 778 nm diode driving 5S to 5D through the same optics reads the waist from the measured light-shift coefficient of that line, 2.5(2) e-13 per mW per square millimetre ([Martin 2019](../lit/martin2019.md), held), a twenty-linewidth shift at this bench's power on a 330 kHz line, so the waist follows to about four per cent from a number that imports none of the disputed theory, with the waist at 778 nm scaling as the wavelength for the same optics |
| **cell temperature against the cold spot** | instrumented but the gradient is not resolved | the density lever, and through it the collisional coefficient. And the meaning of any Doppler thermometer: with the record's densities the mean free path exceeds the cell below about 110 C and falls to millimetres at 130, so the vapour is a flux-weighted mixture of the walls' Maxwellians at the cold end and a local temperature at the hot end, and a pedestal fitted as one Gaussian reads a temperature that moves against the thermocouple across the lever by up to the gradient itself | carried as a stated systematic in `results/beta_self_probe.csv`, and the thermometer's regime dependence is an item for the deep-trace producer's landing |
| **retro-reflection intensity ratio** | not measured. The working value is a stated prior, carried with its spread in `results/delta_alpha_posterior.csv`'s notes, and [chapter 7](07_acquisition-settings.md) records one in-record reading that contradicts it outright | the effective intensity, and through it every light-shift prediction. [Chapter 6](06_sizing-and-spending-rules.md) already schedules turning the assumption into a measurement | carried as the prior in `results/delta_alpha_posterior.csv`, whose limit row states how far the priors move it, and inside the predicted envelope of `results/stark_joint.csv` |

**The residual drift's shape, not its size**, an analysis unknown the same rules
govern and one the forecast now needs. A drift that is exactly linear in acquisition
order is removed for free by a fit that carries the order, whatever its rate, so the
three-channel forecast's lock cells are a null by construction and not a measurement
of what the repair bought. What a real residual does is wander, and a wander is not in
the span of a straight line in order. **What it changes**: whether the repaired lock is
worth the characterisation run at all, and what the pull channel costs on a drifting
arm. **How the forecast proceeds**: the lock cells are reported as a construction null
and no beam-time argument rests on them until the world builder carries a drift with
curvature or a random walk.

**The saturated two-photon rate law**, the same kind of unknown and the one that bounds
the tight-waist case. The world carries saturation as a width, through the companion,
and not as a limit on the rate. At the archive that is right to a part in thirty: the
saturation parameter is 0.033. At the campaign's 16 micron waist and top rung the shift
is seventeen times the archive's, so the parameter is some three hundred times larger
and the two-photon rate no longer grows as the power squared. **What it changes**: every
amplitude and every summed tooth area at the tight waist, and with them the area sum
rule's own null. **How the forecast proceeds**: those cells are read as upper bounds on
the signal and the file's note says so, and the summed tooth area is not read as a
sum-rule test at the tight waist at all. **The size is measured** (2026-09-06, on
quiet traces so no noise enters): with the term switched off the power ladder's area
follows the two-photon square law at a log-log slope of 1.978 and the depth ladder
stands still to seven per cent, while with it on the slope reads 2.209 and the depth
ladder falls by nineteen. The Bessel weights are innocent, summing to 1.000000 at the
lowest depth and 0.997587 at the highest over the seven modelled teeth, and so is the
wing baseline, which moves by three per cent across the ladder while the raw integral
falls by fourteen.

**The world builder carries the axial collection window and the standing wave's
fringe-resolved tail since 2026-09-08**, through `forecast.build_world_trace(z_ratio,
fringe_density)` and `lineshape.ramp_mixture`, and both forecast producers pass them
from the cell's waist and retro ratio. What stays open is narrower and is an apparatus
item: the mixture weights the window uniformly along the beam, where the measured
collection profile (the lens, the image distance and the cathode's 12 mm axis, the item
below) sets the true weight, so the window's correction is exact in form and stated to
the tolerance of that profile, which is 8 to 16 per cent on the coefficient at
16 microns: integrating the mixture's mean over a uniform weight, a linear
taper, a Gaussian at half at the edge and a window half again as long gives
0.585, 0.677, 0.615 and 0.555, against 0.818 to 0.942 at 40 microns. **And the
realised factor is not that geometric ratio**: `pull_factor_quiet` at a fixed
16 micron geometry reads [0.5752](../../results/three_channel_forecast.csv "ref:three_channel_forecast:base::pull_factor_quiet"), 0.5578, [0.4802](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_8MHz::pull_factor_quiet") and [0.5542](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_12.5MHz::pull_factor_quiet") across the base,
the 0.5 W ladder and two comb spacings, because the centre is fitted in a
window that moves with the comb, so a campaign supplying the geometric number
reads 1.7 to 18 per cent low. The two quantities are named apart: the
mixture's centroid ratio is geometry, `pull_factor_quiet` is what the
estimator realises. `results/waist_ladder.csv` reports what the window does
against the pure ramp (the windowed third cumulant at -1.035831 of it at 16 microns, a
reversed sign, and the mean pull at 0.585), which is now what the world builds. The
exhibit twin (`examples/campaign_twin.py`, at the archive's 64 microns, where both terms
are a few per cent) keeps the default until its regeneration, and says so. The guided
arm carries neither: an evanescent field has no focus, and the record holds no fringe
model for a retro-reflected guided mode, so that item is the fibre thread's.

**The single-waist kernel at a tight waist**, an analysis unknown and the third of
this kind. The forward model gives the interaction volume a single beam radius, and the
collected region is fixed by the optics, so the description holds only while the
Rayleigh range is long against that region. Measured over the collected length at
the campaign's own optics, the transit width's spread about its mean runs 0.1 per
cent at 128 microns, 1.0 at 64, 5.5 at 40, 23 at 24 and 47 at 16, where the beam
radius at the edge of the collected region is 4.3 times the waist. **That one
per cent licenses nothing for the shape channels, and this item said it
licensed the convolution until 2026-09-09.** It is the axial spread of the
transit kernel alone, and the second mechanism is radial. The saturation
companion follows the local light shift, the ramp's own variable, so the broad
elements are the shifted ones and shortening the collected region cannot reach
it. Measured element by element
(`scripts/run_kernel_inhomogeneity.py`), the windowed third cumulant is wrong
by [106.911](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:k3_error") per cent at the
archive's own waist, [96.452](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w24um:k3_error") at
24 microns and [89.701](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:k3_error") at 16:
**the archive is the worst of the four and not the licensed one.** The centre
channel splits. The centroid is exactly immune at every waist
([0.000](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:centroid_pull_error") per cent),
while the fitted centre the campaign actually inverts moves by
[-0.265](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:fitted_centre_error") per cent at
64 microns and [-56.972](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:fitted_centre_error")
at 16. **A campaign waist has no measured band of its own**, so the
tolerance producer applies the archive's 62 to 68 micron band as the same
fraction of each proposed waist, paired with the retro-ratio error as the
record's convention pairs them. That is a borrowed uncertainty, not a spanned
one, and it is an open item: a knife-edge at each proposed waist is what
replaces it. **What it changes**: any reading that depends on the line shape at a
tight waist, the third cumulant above all. The width's spread does not threaten the fitted
centre, because it is symmetric in the axial coordinate and a symmetric
broadening does not move a centre. The shift's own integral over the collected
length does move it, by the 2, 11, 31 and 42 per cent the collection-window
item above puts on a pure-form centre estimator, which is why the forecast
carries the window and the fringe tail in its world since 2026-09-08 and
inverts its centre through the quiet curve's own pull factor and no longer
through the pure ramp's. **How the forecast proceeds**: the centre channel is read at
every waist. **The shape channels are the conflict**:
the single-waist description is good at 40 microns and wider, and the third
cumulant only carries signal at 24 and below, where the shift approaches the
line. The forecast reads the shape channel exactly where this item says the
model is weakest. That tension is the finding, and it is not a rule for
choosing a waist. **The design choice at a tight waist (owner statement, 2026-09-06)**: at 64 microns with the
present magnification of about 2.5 the convolution model is already marginal,
so a smaller waist means one of two things and the plan must say which. Either
the twin's line becomes the volume integral, the transit kernel and the shift
integrated over the collected length together, of which only the shift's half
exists in the tree as `stark_ramp_axial`, or the collection magnification
rises to hold the collected length at the archive's fraction of the Rayleigh
range, where the convolution holds to a per cent, a range that scales as
the waist squared: from about 2.5 at 64 microns to about 6 at 40, 18 at 24 and
40 at 16, at a cost in collected light proportional to the collected length at
fixed numerical aperture, sixteenfold at 16 microns. The geometry sign flip of
chapter 4 exists only on the first route, since the second removes the window
that makes it. And the second route pays in photons where the campaign is
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

**The fit-window systematic on the collisional width**, not an apparatus
number but an analysis unknown the same rules govern: the window scan
(`results/fit_window_scan.csv`) shows a coherent drift of the fitted width
with the fit window that no committed error bar carries
(`docs/UNCERTAINTY.md` §3a). What closes it: the committed shared-slope
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
budget from meter to cell, and the window transmission at 993 nm. Those are
systematic offsets of the power at the atoms and not the drive's stability,
so they bias $\kappa_\mathrm{pred}$ in one direction where the 0.5 per cent
merely widens it.

What it would change: whether the prediction band reaches the bound, and the
guided arm's per-run power ruler, since a calibrated power at the fibre is the
same measurement.

### The collection lens and its image distance

The fluorescence collection optics set the axial window of the interaction
volume, which is the `z_ratio` of `stark_ramp_axial`. That function has carried
the closed form since July with its window flagged open, and
`constants.collection_z_ratio()` now closes it from the focal length, the
image distance and the cathode's 12 mm dimension along the beam. Two of the
three are stated to a tolerance and not yet measured: $f = 18 \pm 1$ mm and an
image distance of $50 \pm 10$ mm. An owner statement puts the magnification at about 2.5
(2026-09-06), which the stated conjugates give as 1.8 at their centre and reach
at their tolerance's edge, so the imaging geometry is the first ruler
measurement of the campaign.

They close with a ruler and no atoms. What they change: the window is
[0.26](../../results/prediction_band.csv "ref:prediction_band:collection_window:z_ratio")
Rayleigh ranges, where the ramp is exact over most of the shift range and the
recovered shift is biased low by
[-1.97](../../results/prediction_band.csv "ref:prediction_band:collection_window:shift_bias_width_pct")
per cent. That correction stays conservative only while the window is below
[1.691](../../results/prediction_band.csv "ref:prediction_band:collection_window:width_bias_sign_flip_z_ratio"),
and the third cumulant's own null sits at
[1.117](../../results/prediction_band.csv "ref:prediction_band:collection_window:skew_null_z_ratio").
**The largest of the three uncertainties is how the 50 mm is read**: as the
image distance it gives the window above, and as the object distance it would
give one about three times wider, a twelvefold larger bias with the null within
reach. `constants.COLLECTION_IMAGE_DIST_M` names the reading it takes.

### The background scattering reaching the detector

**Is background scattering in the model?** It is
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
steeply with temperature. And the cascade's own D1 light scattered off the
walls and windows after being trapped, which exists only with hot atoms,
scales with the signal, and is therefore the halo term of the twin and not a
background at all.

**Why it is an apparatus item and not a derivation.** All three enter the trace
the same way, as an **additive pedestal** under the line, and the fitter already
carries a per-trace linear baseline, `b0` and `b1`, which absorbs a constant and
a slope exactly. So a flat background is not a model error at all: it is
absorbed, and it costs only the two degrees of freedom already spent. **The term
that would matter is one that varies across the scan on the scale of the line**,
and nothing in the apparatus is known to do that. Whether anything does is a
measurement and not an argument, which is what opens it as an item here.

**What closes it, in two readings.** A scan with the drive blocked, at the
working temperature, reads the dark rate plus the wall's thermal emission and
nothing else, since neither depends on the drive. A scan with the drive on and
detuned from the two-photon resonance by many linewidths, at the same
temperature, adds whatever drive light the filter passes. Neither reading can
be taken cold: the thermal term is the one that matters and it needs the hot
cell. What the pair does not measure is the trapped D1 light, because it is
not separable from the signal, and the twin carries it as the halo fraction
from `results/trapping_channels.csv`.

**What it would change if it is not flat.** A background with curvature on the
line's own scale biases the widths, since the baseline model cannot follow it,
and a background whose scan dependence is **asymmetric** is the one term that could
imitate the third cumulant. That is the channel the campaign now rests on, and
it is the single reason this item is worth an afternoon: **a shift-like
asymmetry from the detection path would be read as a light shift by every
estimator in this record.** The power ladder is what separates them, since the
true shift's third cumulant goes as the cube of the power and a detection
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
behind the cell, so this is an apparatus number and not a derivation.

The record already bounds its effect. Any speed-borne term must grow as the
square root of the temperature, about eight per cent from 70 to 130 C and monotone,
and the fitted Gaussian across the ladder
(`results/global_dataset_fit.csv`, `sigma_laser` by session) is
non-monotonic and smallest at 130 C across the campaign sessions, which reads
as a small residual, though those rows carry no stated error and a
session-to-session spread near a few tenths of a megahertz, so the reading is
a bound and not a resolution. What closes it is a measurement without atoms at the line: the
angle from the beam positions at two distances along the return path, or the
width of a Doppler-broadened single-photon line under the same alignment. What
it would change: the Gaussian nuisance gains a derived, temperature-scaling
share, and the laser's own width is read from what remains. No forecast in
this repository rests on the angle: the forecast spans the term by treating
it as absent and naming it here.

### The piezo's first resonance, and the lock's servo bandwidth

**The piezo's first mechanical resonance, and the lock's servo bandwidth if the
scan runs under lock**, both bench facts and both newly load-bearing. The scan
rate is the cleanest degeneracy-breaking knob in the record, leaving every
spectral width exactly untouched while every drift term goes as its reciprocal
([chapter 7](07_acquisition-settings.md)). **What it changes**: how far a rate
ladder can be pushed, and therefore whether the drift's shape can be measured
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
apparatus numbers. What they change: the centre channel's fit window stops
just short of half the spacing, so a spacing of 25 MHz or more opens the full
window the tight-waist line needs, while the moment channel's science trace is
taken with the RF off whatever the spacing, since the teeth's tails enter the
window at any spacing the record had tried when this was written. **The run
refutes that half**: the comb-free trace is where the moment channel is least
accurate, and the 25 and 40 MHz combs are where it recovers the coefficient.

**MEASURED 2026-09-06, and the spacing threshold above is refuted**
([`results/three_channel_forecast.csv`](../../results/three_channel_forecast.csv)).
The fit window is 12 MHz of half-width at 25 MHz and at 40, so truncation is
not what separates them, and the reasoning above stopped at truncation. What
separates them is the teeth's tails: at 25 MHz the first teeth stand 13 MHz
beyond the window edge and reach in, and the depth null reads 13 against a
scatter of 52, which is no measurement. At 40 MHz they stand 28 MHz clear and
the null reads 0.009 against 0.024, under half a standard error from zero.
**So the lever is specified at 40 MHz**, and which resonances the tank offers is
the apparatus number this item still wants.

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

**What is not recorded is whether the transmitted optical power is actually
invariant across the switch.** A drive-dependent insertion loss changes the
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

### The power of the 105 ruler traces, which the manifest does not carry

`data_raw/MANIFEST.csv` lists 61 traces in the `ruler_t` role and 44 in
`ruler_p`, every one with the RF on, and **every one with an empty `power_mW`
cell**. The ruler traces were calibration traces and their power was never
logged into the manifest. What it changes: an external analysis proposes
reading the beam waist from the saturation of the teeth in those traces, which
needs both a power above about 100 mW and a spread of powers across the set,
and neither can be established from the record as it stands. The same analysis
finds by injection and recovery that the estimator is unusable at 64 microns
and usable at 32, so the proposal is in any case a new session and not a
reanalysis, and the missing power is what decides whether the archive can even
serve as its rehearsal. It is an apparatus fact the bench notebook may hold.

### The wavemeter's averaging mode and its environmental readings

Screenshots from the campaign show the wavemeter in a floating average over ten
measurements, with cell readings near 26 C and 1006 to 1007 mbar, and one shows
a settle of about an hour and a half after power-up. None of this is in
`APPARATUS.md`. What it changes: a ten-sample floating average smooths the
jitter that the offset analysis of chapter 9 reads, so the scatter between the
two logged offsets of 119.6 and 133.4 MHz is a scatter of averages and not of
single readings, and the settle time bounds how early in a session any absolute
reading can be trusted. Both are apparatus facts and both are one line each.

**And the readout's own step is the larger term, which nobody had separated.**
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
quantisation only when the jitter dithers across the step. Under that condition
the campaign's own ten-sample average would give 5.5 MHz on the transition
axis, and nothing at all without it.

### The piezo's triangle frequency, which now binds the acquisition

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

### The adjustable expander's magnification, and what is known about it

The campaign wants a waist ladder taken at fixed power and fixed retro ratio
through an adjustable beam expander (owner design, 2026-09-06), because the
magnification is a ratio, of focal lengths where the optics are ideal and of
spot sizes on a camera where they are not, and can be known far better than the
absolute waist, which makes the ladder's abscissa calibrated. What the record
does not have is the instrument's own numbers: the magnification range, the
accuracy with which the magnification is known at each setting, whether the
mode quality survives at the extremes, and how the assembly behaves thermally
under the beam, which matters because the record already carries a
power-dependent thermal lens in the modulator. What they change: the ladder
measures the reference waist through two different powers of the
magnification, the transit's inverse and the shift's inverse square, so the
accuracy of the abscissa sets how tightly the two agree and therefore how much
the largest open systematic in this record shrinks. **No committed forecast rests
on this item either.** The analytic ladder that spans it is drafted and its
exponents check against the package functions that own them, and until its file
is committed the campaign case quotes nothing from it. A second number rides with
it, the retro ratio at each setting, since expanding the beam changes the
returning mode's overlap unless the retro is re-matched, and the light shift
takes one combination of the two arms while the two-photon coupling takes
another.

### The beam's mode at the cell, and the collection aperture

Two bench facts the analysis assumes and no measurement in the record fixes.
**The mode at the atoms.** The ramp's shape, and with it the minus two thirds
pull coefficient and the 0.566 skewness, is a property of a Gaussian beam. The
source is a single-frequency titanium-sapphire laser, so the beam leaves TEM00,
but an electro-optic modulator, the lenses and the cell windows sit between the
laser and the atoms, and a mode that is no longer Gaussian changes the ramp's
shape and not merely its scale. **What settles it.** One camera image at a
plane equivalent to the interaction volume, the same image the waist ladder of
chapter 4 already needs. **The collection aperture.** The solid angle sets what a count-rate forecast
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
new block, so the ladder would carry block scatter along its own axis. **What it decides.** A factor of three on the waist's
share of the error budget: under a per cent with a pointing-stable zoom,
about three per cent with discrete pairs realigned each time, and about half
of that if every block is bracketed by a reference condition at one
magnification, one power and one temperature. **What settles it.** Image the
beam position at each setting of the expander before the campaign commits to
interleaving, which is the same camera step the profile and the magnification
already need. **Cost.** An hour inside the optics day. Raised from outside the
record on 2026-09-07.

### The oven's block-to-block reproducibility at one setpoint

Temperature cannot be interleaved inside a block, so the collisional
coefficient inherits the block-to-block scatter directly and no number of
traces at one setpoint reduces it. **What it decides.** Whether that
coefficient's error stays at the ten per cent the record's own block scatter
implies or falls. **What settles it.** Either a better-controlled oven, or a
reference condition at one fixed temperature repeated in every block so the
block term is measured and divided out. The second costs traces and no
hardware, and it is the one the campaign can choose today. **Cost.** About a
tenth of each block. Raised from outside the record on 2026-09-07.

### The retro power ratio, an assumption the twin carries as a number

The forward-to-return intensity ratio at the atoms enters the light shift as
one plus the ratio and the prediction band through its spread, and the record
labels it an assumption at 0.94 with a spread of 0.04 that its own docstring
calls deliberately modest. The physical range is wider: with every surface the
return beam crosses uncoated, at four per cent each, the ratio falls to about
0.7 before mirror loss, and coated it sits near 0.97. At the uncoated end the
predicted coefficient falls by about twelve per cent and still clears the
bound, so the tension survives the range, and the forecast should span it
until it is measured. **What settles it.** The window coating and the retro
mirror's reflectivity from the bench, and one measurement: a calibrated
attenuator in the return path, at which the narrow line goes as the ratio
times the attenuator's transmission taken twice and the pedestal as one plus
the square of that product, so a run at full and at half transmission reads
the ratio to a few per cent where the area ratio at full transmission alone is
nearly stationary in it. **Cost.** Two blocks in one session with the wide window,
since the pedestal must be fitted. Raised by an external reading on 2026-09-06
and derived here on rung 1.

### The retro path length, which sets the comb's effective depth

**What is known.** Nothing. The retro mirror is a flat behind the cell
([APPARATUS](../APPARATUS.md)) and no page records its distance from the atoms.

**What it decides.** The retro beam's modulation lags the forward beam's by
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

**It decides a second thing, found 2026-09-09, and this one rides on the retro
ratio.** Lens (8) and the flat mirror form a retro whose returning mode matches
the forward one exactly when the mirror sits one focal length beyond the lens,
and not otherwise: the round trip returns the waist onto itself with a power
overlap of 1.000000 at that distance, 0.9967 at 50 mm and 0.9610 at 500 mm.
So the `rho = 0.94` of record may be carrying an unmeasured mode-mismatch factor
beside the surface losses it is meant to describe, and the item below on the
retro power ratio cannot separate the two without this length. The same
geometry is what makes `rho` non-transferable across drive wavelengths, since a
retro aligned at 993 nm returns the 760 nm mode with an overlap of 0.9859 at
the design distance.

**It closes with a tape measure**, and the
same distance enters the misalignment item above and the mode-overlap reading
here.

### The input beam at the focusing lens, and whether L1 is a single element

**What is known.** The beam reaches L1 free-space from the laser through the
EOM's 3 mm clear aperture, which an infrared card recalls clipping
([APPARATUS](../APPARATUS.md) 1.2), and nothing records how much of the beam
that aperture removes. L1 itself is quoted from the source as "a plano-convex
lens", which is a single element, and no page states an achromat.

**What it decides.** Nothing at all while the campaign drives one line, and the
whole cross-transition programme once it drives two. The focused waist is
`lambda f / (pi w_in)`, so a retune moves the waist even with no optic touched,
and the ratio of light shifts between two drives carries `(w_in at one / w_in
at the other)` squared. If the aperture fixes the input radius the factor is
one and the waist follows the wavelength. If the beam is an unclipped
fixed-geometry resonator mode the radius follows the root of the wavelength and
so does the waist. Between 993.4 and 760.1 nm that is 48.59 um against
55.55 um, and 31 per cent on every shift ratio built from them (register A136).
The element type is the small term, worth 0.8 per cent through `1/(n-1)` and
insensitive to the glass, but it is not free: an achromat holds the focal
length and a singlet also moves the focus 1.17 mm, which is a third of the
collection half-window.

**What closes it.** A beam profile at the lens, on the same afternoon and the
same stage as the waist measurement the plan already schedules, with no atoms
and no lock, with one look at the lens mount for a cemented doublet. Until then
the campaign's own line closes it in situ, since the transit width carries the
same geometry to the first power and separates the two regimes by 14 per cent.

**How the forecast handles it.** `rb5s6s.constants.waist_at_drive` takes the
regime as a required argument with no default, and
`results/projections.csv` carries the aperture reading in its cells with the
resonator reading quoted beside it in the note, so every multi-drive number is
a bracket until the profile exists.

### The composition of the transit kernel and the light shift, an analysis unknown

The twin's line composes the transit kernel with the ramp as a convolution.
Computed on rung 3 against the two-time correlation spectrum of a chirped
chord with the dephasing carried (chapter 4's closing block), the composition
leaves the mean exactly the composition's at every waist (rung 2, the first
moment of the two-time spectrum), holds the archive's width and interior
residual to a fifth of a per cent, narrows the line by about two per cent at
the campaign's tightest waist, and adds ten to twenty per cent to the
collection window's third cumulant there. **What settles
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
the rate there. **What settles it.** Nothing on the bench: it is a derivation,
the transient two-level response along a Gaussian chord, owed to the methods
chapter before the 16 micron cells are quoted. Raised by an external reading on
2026-09-06.

### The analog chain's linearity at the peak rate

The amplitude against density runs sub-linear across the 2025 grid, and two
mechanisms bend it the same way: radiation trapping, which follows the optical
depth (chapter 10), and the detection chain's linearity, which follows the
rate. The chain is analog, a photomultiplier into a transimpedance stage into
the oscilloscope, so a counting dead time does not apply to it, and what would
is the photomultiplier's and the pre-amplifier's linearity at the peak anode
current, which the record has not measured. The pedestal separates the two,
since its rate is hundreds of times below the peak's and free of any rate
effect while it shares the optical depth: a peak-to-pedestal ratio that moves
with density at fixed rate is trapping, one that moves with rate at fixed
density is the chain. **What settles it.** A neutral-density ladder in front of the detector, which
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

### The detection chain's time constant, and the sweep rate it admits

**What is known.** [Chapter 10](10_the-fixed-lock-instrument.md) bounds the
chain faster than 10 microseconds at 10^6 V/A from the rehearsal's LeCroy
traces, a bound at that instrument's sampling limit and not a curve. **What
is not.** The time constant itself, at the gain the next session uses.

**What it decides.** Whether a full-span triangle can be swept fast enough to
put many line crossings in one record. On the bound as it stands, a lag of
10 microseconds costs a third of a per cent of width at 12 MHz per ms and
17 per cent at 120, and a triangle over the four peaks' 5.2 GHz sweeps
10 MHz per ms at 1 Hz and 100 at 10 Hz. The campaign's proposed settings,
24 to 6000 MHz per second, all sit far below the first figure, so the bound
admits every one of them and chapter 9 is right that the chain does not bind
them, while a 10 Hz full-span triangle would be refused and nobody proposes
one. The atomic cascade lag, about 72 ns, costs under a hundredth of a per cent of
width at either and a tenth of a per cent as a shift at the faster, and never
enters. **Until the time constant is measured, a setting
above about 20 MHz per ms, three times the fastest proposed and where the
lag's width cost approaches one per cent, is forecast across the bound and not
at a value.** The ceiling of 8.1e6 MHz per second the piezo item above quotes
for the chain rests on an assumed constant, and this bound replaces it.
[Chapter 7](07_acquisition-settings.md) and
[chapter 9](09_the-fixed-lock.md) carry the consequence.

### Whether the radio-frequency gate can be synchronised to the sweep trigger

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

### The piezo's sweep nonlinearity and its hysteresis, as fractions of its travel

The rate variation across an analysis window that forges the whole light-shift
signal in the third cumulant is computed in
[chapter 7](07_acquisition-settings.md): about one and a half parts in ten thousand
at the campaign's tightest licensed waist and two parts in a hundred thousand
at the 2025 configuration. The nonlinearity that matters is the actuator's own over its
travel, and the span scanned does not enter it, so what is needed is the
piezo's departure from linearity as a fraction of its full travel and the
hysteresis between the two halves of a triangle. A bow of two per cent clears
the 40 micron tolerance by 1.2 and ten per cent fails it by four, so an
open-loop actuator needs its bow measured from the anchors the sweep crosses
and taken out. A ripple of fifty cycles at a tenth of a per cent exceeds the
tolerance three hundredfold and is what the ramp monitor is for. **Cost.**
The bow from the anchors is free once the ramp is recorded. A linearised
actuator is a purchase the answer decides.

### Whether the R&S RTM3004 can be borrowed for the campaign

Chapter 7 names it the instrument the design wants, on three documented
counts: disjoint high resolution at sixteen-bit words, a record-length menu,
and history segments that capture a whole ladder without touching the
horizontal control. Whether it is available to this bench for the campaign's
weeks is a fact the record does not hold. If it is not, the four-peak traces
go to the LeCroy run raw, as chapter 7 already provides. **Cost.** A question
to whoever holds it. The design works either way and the difference is the
LeCroy's two lost bits.

### What each item costs to close

**The lock residual is the cheapest and the highest leverage.** It needs no
atoms: step the lock, record the recovery, and read an Allan deviation of line
centres across a session. [Chapter 9](09_the-fixed-lock.md) already specifies
it. Until it exists, every centre-channel forecast in this repository is
reported across a span instead of at a value.

**The waist closes in an afternoon with no atoms at all**, and it is the one
measurement that sharpens every existing bound at once. The atom-based route
beside it in the row above costs a 778 nm diode and one session with atoms,
and it is a check on the first route and not its replacement.

**The chain's time constant closes in an hour with a step response on the
3104z's deep fast record and no atoms**, chapter 10's second item, and it is
what decides how fast the deep trace of chapter 7 may run.

**The beam's mode at the cell closes with one camera image**, taken at a plane
equivalent to the interaction volume, and the aperture closes with the same
ruler as the distances below. **The input beam at the lens closes with the same
camera on the same afternoon**, and it is the item that decides whether a
cross-transition ratio is quotable at all.

**The collection distances close in a minute with a ruler**, and they are the
only items on this page already carried into a committed result instead of
being spanned around it.

### The collection solid angle, which the record has never measured

**What is missing.** The platform table's fluorescence rows multiply the
emitted rate by 0.162, and that number is the fraction of the emission inside
the axial collection window, `2 arctan(z_ratio) / pi`, derived in
`results/prediction_band.csv` from the lens and the cathode. It is not a solid
angle, and no solid angle enters anywhere. So every absolute fluorescence rate
in that table is an upper bound by whatever fraction of the emitted sphere the
collection optics actually subtend.

**What closing it needs.** The collection lens's clear aperture and its
distance from the beam, which together give the subtended fraction. The
transmission of the filter stack at 795 nm. And whether a second element or a
condenser sits in the path. All are bench facts.

**What it changes.** The absolute fluorescence signal-to-noise of the cell, the
trap and the molasses rows, by one common factor, so it does not move any
comparison between those rows, and it moves every comparison against an
absorption row. The axial window's own weighting is a second, smaller question:
0.162 is computed on the ramp's axial weight, and the table now integrates the
saturated rate, whose weight is different.

### The saturation parameter's linewidth, a modelling item and not a bench one

**What is wrong.** `platforms.excitation_rate_per_atom` takes
`s = 2 (Omega / Gamma_nat)^2`, so the resonant rate goes as one over the
natural width alone, while the same row carries a transit width of 3.83 MHz
beside a natural 3.49. The detuning-integrated weak-drive rate is fixed by the
Rabi frequency alone, so the peak rate scales as one over the total homogeneous
width. On the record's own kernel the composite width over the natural runs
1.62 at 64 microns, 2.58 at 19 and 2.92 at 16, and every rate, saturation
parameter and absorbed fraction in the platform table is overstated by that
factor at its own waist.

**Why it is listed and not fixed.** It predates the wave that found it
(2026-09-11), it moves every cell of a committed table and the three pages that
cite it, and `scripts/run_waist_ladder.py` already carries the right
construction, so the repair is a migration and not a derivation. It is the
next wave's first item.

**And the regime beneath it.** The three-level steady state those rates assume
needs the atom back from 5P and driven again while it is still in the beam. At
the tight-waist row the chord time is about 102 ns against a 72.3 ns cascade
dead time, a ratio of 1.4, so the atom leaves in under two cycles. The table's
note says the row sits outside the approximations and does not say which. This
is which.

### The trapping producer's own copy of the cascade's first leg

`rb5s6s/detection.ir_branching_5p12` computes the 6S branching from the
package's matrix elements and reproduces the committed cell to four parts in
ten million. `scripts/run_trapping_channels.py` still computes the same
quantity from its own `_leg` and its own copies of four SI constants. The two
agree by retyping and not by wiring. Migrating the producer also moves the
halo and escape-factor arms that read those literals, so it is its own change.

### The drive beam's quality factor, which no number here carries

**What is open.** The beam-quality factor of the drive at the cell. Nothing in
this record has measured it and no function takes it as an argument, so every
waist-dependent quantity assumes a diffraction-limited beam.

**Why it matters, and where.** It enters in one place, the Rayleigh range, which
goes as the waist squared over the quality factor. Everything axial follows: the
collection window's ratio, which the record carries as a signed correction with
two sign reversals, the fringe Monte Carlo, and the kernel spread that licenses
writing the model as a convolution. Because the window ratio goes as the quality
factor over the waist squared, the strain falls on a *small* waist with a poor
beam. At 55 microns the third cumulant keeps 86 per cent of its value at a
quality factor of 1, 48 per cent at 2, and reverses sign past 3.17. At 64
microns the reversal needs 4.29 and at 85 it needs 7.56.

**Why the bench is not obviously diffraction-limited.** The drive passes a
modulator whose clear aperture is 3 mm, sourced from the manufacturer's own
table, with an input radius of 1.5 mm, so the aperture sits at the beam's
$1/e^2$ radius and transmits 86.5 per cent. A viewer-card observation of
clipping there is on record as a recollection and not a measurement.

**What would close it.** One afternoon with a commercial beam profiler, on the
same bench and ideally in the same session as the knife-edge waist measurement,
since the two answer one question between them and neither needs atoms, a lock
or a cell to be running.

**What the forecast does until then.** It spans the pair. A working region of 55
to 85 microns with a quality factor under about two keeps every term inside its
licence with a factor of two to spare, and that pair, not an interval in the
waist alone, is what the guided and tight-waist cases are sized against.

**A second route reaches the same bound, 2026-09-12.** The paragraph above sizes
the pair on the third cumulant's sign reversal. The convolution licence sizes it
independently, on the rms spread of the transit width over the collected region:
that spread is 1.73 per cent at 55 microns and a quality factor of 1, 3.61 at
1.5, 4.70 at 1.75 and 5.84 at 2.0, against the 5.5 per cent edge the record sets
at 40 microns. **The bottom of the band leaves the licence at a quality factor
of 1.93**, which is the "about two" above reached through a different term. The
joint condition is `w0 >= 40 um * sqrt(M^2)`: 49 microns at 1.5, 57 at 2, 69 at
3. So the waist band and the quality-factor bound are one assumption, not two,
and writing either alone writes half of it.

**The threshold is a band, not a line.** The collection ratio carries its own
uncertainty from the optics: `L/z_R = 0.26 +- 0.14` at a quality factor of 1,
propagated from `f = 18 +- 1` mm, an image distance of `50 +- 5` mm and the 62
to 68 micron waist band, which is 54 per cent relative. Scaled, `0.52 +- 0.28`
at 2 and `0.78 +- 0.42` at 3, so at 3 the licence boundary sits inside the error
bar and no clean yes or no is available there. A fit reports the probability its
licence holds, never a sharp verdict against a 54 per cent input.

### The retro-reflection's tilt, which nothing here monitors

Two counter-propagating photons cancel the first-order Doppler shift only when
they are exactly anti-parallel. At a tilt $\theta$ the residual two-photon
wave-vector is $2k\sin(\theta/2)$, so the Doppler-free line regains a Gaussian
width of that times the thermal speed. Derived, not simulated, at 110 °C. **The angle in this table is the crossing angle at the atoms**, which is what the residual Doppler width is set by. A mirror tilt reaches it multiplied by `2(1 - d/f)` = 4/3 for the bench's 50 mm and f = 150, so a mirror tilt of 3.2 mrad is a crossing angle of 4.27 and gives 1.94 MHz, not the 1.45 the mirror angle alone would give:

| tilt | residual FWHM | against the transit at 64 µm |
|---|---|---|
| 0.5 mrad | 0.23 MHz | 0.24 |
| 1 mrad | 0.45 MHz | 0.49 |
| 2 mrad | 0.91 MHz | 0.97 |
| 5 mrad | 2.27 MHz | 2.43 |

No forecast rests on it: these are the term's size at tilts nobody measured,
and no committed cell carries a mirror tilt.

**A milliradian is half the transit width and two milliradians double the
line.** But the tilt this bench can have is bounded far below that, and the
bound is already measured.

**The offset binds long before the Doppler does.** The retro mirror sits about
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

**Nothing measures the overlap, and $\rho$ is not a measurement.** The retro
ratio carried in `constants.RHO_RETRO` is an assumption of 0.94, and the
epistemic ledger records it as never informed by these data. The area ratio that
*would* measure it needs the Doppler pedestal, which is 931 MHz wide, and the
archive's traces span under 100 MHz, so they cover about a tenth of it and see a
flat offset in their wings. **The wide scan that would measure $\rho$ is the
same one the pedestal needs, and neither has been run.**

**What does bound the tilt is the line's own presence**, and it needs nothing
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

**The term is self-limiting**: the same misalignment that would supply the
missing width destroys the signal that carries it. Even at one per cent of
aligned strength the tilt supplies a fifth of the gap. So it is disfavoured as
the whole answer, not excluded as a contributor, and the gap stays open. No
forecast rests on it: the 2.36 mrad is the tilt a refuted hypothesis would have
needed and not a bench number, and nothing in `results/` carries it.

**The standing wave is where this should be tested, and nobody has.**
The fringe Monte Carlo assumes a perfect retro and has no offset axis. Under a
tilt the fringe planes rotate by $\theta/2$ and gain a transverse period
$\lambda/\sin\theta$. With the beams offset the local contrast
$2\sqrt{I_1I_2}/(I_1+I_2)$ is unity only on the bisector. And near the focus the
two wavefronts no longer match, which washes fringes out over the interaction
volume by a third mechanism. The fringe-resolved suppression the record carries,
about 7 per cent at this waist, is a contrast-weighted quantity, so all three
reach it.

**Measured, 2026-09-12**, by `fullmodel.fringe_survival_mc`, which carries all
three and reduces to the ideal contrast at zero tilt, zero offset and unit beam
quality. **The tilt angle is negligible and the offset is not.** The transverse
fringe wave-vector $k\sin\theta$ is four orders below the axial $2k$, so at
0.5 mrad the mean fringe survival moves by under 2 per cent, while an offset of
one waist takes the mean contrast from 0.9995 to 0.836. Beam quality enters
through the axial sampling instead, taking the mean radius over the collected
region from 1.011 to 1.083 waists at $M^2 = 3$ and the survival down by 6 per
cent. What a tilt does to this bench, it does through the offset it produces.
The wavefront mismatch is still not modelled, so these are an upper bound on the
fringe effect at non-zero tilt.

**What the item is for, then.** The tolerance itself, for the campaign. The
offset per unit tilt does not change with the waist while the waist does, so a
tighter focus makes the alignment requirement proportionately sharper: at 16 µm
the same 0.053 mrad costs a quarter of the overlap and not six per cent.
That is a real constraint on the tight-waist configuration and it was not
written down.

**What would close it.** A shear-plate or far-field overlap check at the cell,
minutes, with the residual walk-off recorded. The data alone already bound it
through $\rho$, which is why this is a tolerance to respect and not an unknown
to span.

**What the forecast does until then.** `rb5s6s.fullmodel.residual_doppler_fwhm_mhz`
carries the term and `build_world_trace` takes it as an opt-in argument, off by
default, so the campaign case and the Sobol ranking can weigh it against the
waist instead of assuming it away.

### The modulator's amplitude admixture is a setting and not a defect

**Owner-stated, 2026-09-12.** The polarisation axis into the modulator was
tilted deliberately, to give phase-amplitude coupling, so that the carrier would
not bury the other teeth even at small modulation depth. The residual amplitude
modulation this record measures is therefore the intended consequence of a
control that was exercised, and not an imperfection of the device.

**What that changes.** The ruler chapter localises the admixture to the carrier
and reports its height running from 0.360 to 1.188 of the first order across the
clean combs, standing taller than the first order on ten of forty-one, while the
second-to-first ratio holds to four per cent. Read as a defect that scatter is a
purity failure to be bounded. Read as a setting it is the signature the tilt was
introduced to produce, and the contrast between the carrier's spread and the
second-to-first ratio's tightness is what a deliberate phase-amplitude coupling
looks like.

**What it does not do is retire the comb as a lever** (owner, correcting a
first reading of this item the same day). The coupling redistributes power among
the teeth and modulates it at the drive frequency, but the time-averaged total
is unchanged and stays at the operating power. The transit is about 260 ns
against a 12.5 MHz drive, so the atoms respond to that average, and **the light
shift is the same with the modulator on as off**. What the admixture breaks is
the prediction of the tooth shares from $J_k^2$, not the constancy of the total.

**And the shares are observable, which is better than predicting them.** A
two-photon height goes as the share squared, so each tooth's share is read from
the same trace it is used on. The lever therefore stands with a measured
abscissa instead of a nominal depth. From the comb the ruler chapter measures,
heights $0 : 1.00 : 0.69 : 0.15$ at $k = 0, \pm1, \pm2, \pm3$ with the carrier
at 0.360 to 1.188 of the first order, the tallest tooth carries **0.18 to
0.20**. At those shares the saturation companion sits **25 to 31 times** below
the unmodulated line's, at identical light shift, collisional width, laser
width and transit. Nothing else in this model separates saturation from the
Lorentzian sum.

[The ramp chapter](../methods/03_the_ac_stark_ramp.md) already designs its first
test to measure the admixture and never assume it away, which is the correct
handling and is unchanged by the intent. What the intent adds is that the
admixture will not be reduced by a better modulator, because it was not the
modulator.

**What remains open**: the tilt angle itself, which nobody recorded, and
therefore the size of the coupling as a number and not as a measured
scatter. No forecast rests on it: the comb enters the analysis as a frequency
ruler, whose calibration the second-to-first ratio carries and the carrier does
not.

### The guided-platform items

The nanofibre arm has open items of its own, and they are listed in the fibre
thread rather than here so that a reader with no fibre keeps the skip promise
of [BIG_PICTURE](../BIG_PICTURE.md):
[chapter 6](../big_picture/06_next-nanofibre.md).


---

*[Beyond 993 nm](11_beyond-993.md) · [the plan](../PLAN.md)*
