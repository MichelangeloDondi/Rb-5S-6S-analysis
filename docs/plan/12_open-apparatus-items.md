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
| **beam waist in the interaction volume** | not measured in this cell. The working 64 um is a same-conditions measurement from an earlier thesis on this apparatus lineage | the largest open systematic in the record. Every intensity-denominated number rides it | spanned across the band the data allow in `results/transit_mc.csv`, and [chapter 5](05_width-collision-amplitude.md) specifies the profile measurement that closes it |
| **cell temperature against the cold spot** | instrumented but the gradient is not resolved | the density lever, and through it the collisional coefficient | carried as a stated systematic in `results/beta_self_probe.csv` |
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

**The world builder carries no axial collection window**, and it is the largest open
defect in the tree. `rb5s6s/forecast.py` names neither `collection_z_ratio` nor
`ramp_moment_contributions`, so every trace it builds carries the pure transverse ramp.
`results/waist_ladder.csv`, committed beside it, reports the ratio of the windowed third
cumulant to the pure ramp's as -1.035831 at 16 microns, a reversed sign, and the mean
pull at 0.585 of the pure ramp. **What it changes**: the world and the estimator share
the omission, so the forecast recovers the coefficient it injects and would not recover
this bench's. Reading the window's own correction against the pure ramp, a centre
estimator built on the pure form would sit low by about 2, 11, 31 and 42 per cent at
64, 40, 24 and 16 microns. **How the forecast proceeds**: every absolute recovery figure
in `results/three_channel_forecast.csv` is a statement about a world without collection
optics, and the surfaces that quote one say so until the window is threaded through the
builder. The relative comparisons between levers are unaffected, since the omission is
common to every cell.

**The single-waist kernel at a tight waist**, an analysis unknown and the third of
this kind. The forward model gives the interaction volume a single beam radius, and the
collected region is fixed by the optics, so the description holds only while the
Rayleigh range is long against that region. Measured over the collected length at
the campaign's own optics, the transit width's spread about its mean runs 0.1 per
cent at 128 microns, 1.0 at 64, 5.5 at 40, 23 at 24 and 47 at 16, where the beam
radius at the edge of the collected region is 4.3 times the waist. **The one per
cent that licenses treating the model as a convolution was measured at the
archive's waist**, and the campaign's tightest configuration is a factor of forty
outside it. **What it changes**: any reading that depends on the line shape at a
tight waist, the third cumulant above all. It does not threaten the fitted centre,
because the spread is symmetric in the axial coordinate and a symmetric broadening
does not move a centre, which is why the forecast's centre channel stands at 16
microns while its shape channel is refused there. **How the forecast proceeds**: the
centre channel is read at every waist. **The shape channels are the conflict**:
the single-waist description is good at 40 microns and wider, and the third
cumulant only carries signal at 24 and below, where the shift approaches the
line. The forecast reads the shape channel exactly where this item says the
model is weakest. That tension is the finding, and it is not a rule for
choosing a waist.

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
and the retro-ratio error and nothing for the power. Nobody holds the figure,
so it is a measurement here and not a question. It needs the meter's calibration
certificate, the loss budget between meter and cell, and the window
transmission at 993 nm. Until it exists the prediction band spans it at 5 per
cent, which moves $\kappa_\mathrm{pred}$ by the same 5 per cent, and
`results/prediction_band.csv` carries that span in its worst-case edges.

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
image distance of $50 \pm 10$ mm.

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
beyond the window edge and reach in, and the depth null reads 12.5 against a
scatter of 51.3, which is no measurement. At 40 MHz they stand 28 MHz clear and
the null reads -0.0084 against 0.0262, a third of a standard error from zero.
**So the lever is specified at 40 MHz**, and which resonances the tank offers is
the apparatus number this item still wants.

### The adjustable expander's magnification, and what is known about it

The campaign wants a waist ladder taken at fixed power and fixed retro ratio
through an adjustable beam expander (owner design, 2026-09-06), because the
magnification is a ratio of focal lengths and can be known far better than the
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

### What each item costs to close

**The lock residual is the cheapest and the highest leverage.** It needs no
atoms: step the lock, record the recovery, and read an Allan deviation of line
centres across a session. [Chapter 9](09_the-fixed-lock.md) already specifies
it. Until it exists, every centre-channel forecast in this repository is
reported across a span instead of at a value.

**The waist closes in an afternoon with no atoms at all**, and it is the one
measurement that sharpens every existing bound at once.

**The collection distances close in a minute with a ruler**, and they are the
only items on this page already carried into a committed result instead of
being spanned around it.

### The guided-platform items

The nanofibre arm has open items of its own, and they are listed in the fibre
thread rather than here so that a reader with no fibre keeps the skip promise
of [BIG_PICTURE](../BIG_PICTURE.md):
[chapter 6](../big_picture/06_next-nanofibre.md).

---

*[Beyond 993 nm](11_beyond-993.md) - [The plan](../PLAN.md)*
