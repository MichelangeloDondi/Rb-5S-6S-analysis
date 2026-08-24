*Chapter 4 of 11 of [the plan](../PLAN.md)*

**The question.** How is the drive intensity pinned, and how would the light shift be measured rather than bounded?
**Takes.** The optics of chapter 3.
**Gives.** The intensity axis, the light-shift blocks, and the geometry that sets both.
**Skip if.** You want the width programme, which is chapter 5.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> **Question.** How is the drive intensity pinned, and how would the light shift be measured rather than bounded?
> **Design.** A randomised power ladder under a fixed lock, with per-sweep normalisation and a measured beam profile.
> **Ambiguity removed.** The light shift exchanged against every other term that grows with power.
> **Success.** The fitted pull scales with power at the projected precision.
> **Residual uncertainty.** The waist, until it is measured on the day, and the transit kernel it feeds.

## 5. The intensity axis

The shift-against-(P/w₀²) collapse across configurations catches only relative
waist errors. A common scale error passes silently. The orthogonal absolute
anchor is the differential transit width: width(S) − width(L) in the same
session is ~2.7 MHz of pure transit (σ_laser, collisions and natural width
cancel in the difference), and transit ∝ v̄/w₀ is thermal physics with no
knife-edge involved. Measured to ±5–7% it anchors the intensity axis to ~15%,
independent of the stage. Knife-edge, w(z) self-consistency, calipered geometry
and the transit difference must agree before any Stark coefficient is quoted in
physical units. The ramp-law form tests never need the absolute axis. Only Δα
does.

![transit width against beam waist, in the thin single-waist limit](../../figures/fig3_transit_mc.png)

*The physics behind the anchor: the Monte-Carlo transit width against waist,
in the thin single-waist limit only. The producer filters
`results/transit_mc.csv` to its `thin` rows, so the collection-geometry
dependence that file also carries is not on this canvas, and it runs the
direction that would soften the exclusion shaded here: at the one waist where
that file computes it, 50 µm, the added transit falls from 1.254 MHz in the
thin limit to 1.134 MHz over a 6 mm collection column. The file computes no
collection variants at the small waists this figure excludes, so how far the
boundary would move there is not settled by it. The S−L width difference reads
~2.7 MHz off the
steep part of this curve, which is what makes it an intensity calibration
independent of the knife-edge stage. The abscissa is not a measured quantity:
the beam waist has not been measured and the knife-edge scan is pending, which
is what this section's anchor exists to work around. The shaded region is
excluded, because waists below about 40 µm would put the transit and natural
widths together above the observed total on their own. The laser and collisional
contributions are not in the curve, so the true waist is higher still.*

**The block that delivers the anchor, and the region it runs in.** The anchor
and the composite model's transit-kernel choice come off the same data, taken
cold and at low drive power at the small waist. That region is where transit
dominates the core, which is what makes the S minus L difference large against
everything that cancels in it, and it is also where the transit kernel the
composite model uses, the closed-form transit-limit lineshape of
[Lehmann 2021](../lit/lehmann2021.md), parts company with the Voigt profile a
referee would reach for. Lehmann's form predicts a **cusp**, a discontinuous
slope at exact resonance, which the Voigt does not have and which needs a
transit-dominated core to show at all. Every mention of the cusp in this
document means that feature. Running the anchor and the model-form
comparison on one set of blocks is not a saving of convenience: the comparison
decides which kernel the width difference is read through, so reading the anchor
through an untested kernel would leave the absolute intensity axis conditional
on the thing the same data can test.
**Needs.** Configuration S with its metrology done and configuration L already
measured, so the difference exists. The cell at the bottom of the temperature
grid, and drive power low enough that the ramp does not broaden the core, which
puts this block below the power ceiling §3 item 7 discusses rather than near it.
**Shots.** Matched low-power blocks at S and at L at one cold condition, deep
enough that the core width is photon-limited rather than block-limited. Runs as
§9 D6. **Go/no-go.** The S minus L width difference must be resolved to the
±5–7% the ~15% intensity axis above needs, and the two kernels must be separated
by the BIC of [`methods/06_the_statistics.md`](../methods/06_the_statistics.md)
§4.7 rather than by eye. **Empty.** The cusp may sit under the detection
bandwidth, in which case the comparison returns no preference between the two
kernels, and the transit difference still anchors the intensity axis with the
kernel left as a stated assumption. **Record.** The two core widths and their
difference, the implied intensity scale beside the knife-edge one, and the BIC
between the transit kernel and the Voigt.

**The wide-scan Doppler pedestal, an in-situ thermometer and an in-situ ρ.**
The retro-reflected drive makes two kinds of two-photon event. One photon from
each beam gives the Doppler-free line every number in the record is
fitted to. Two photons from the same beam give a line broadened at the
full 2kv, which sits under the narrow line as a pedestal. Its width goes
as the square root of the temperature and its area against the narrow
line's area is 4ρ/(1 + ρ²), so one wide trace measures the gas
temperature and the retro power ratio together. Both are quantities the
record adopts rather than measures, and both are quantities this
session otherwise spends stage 0 time on by other routes
(§3 item 2 for ρ) or adopts outright (temperature). The 2025 windows span a
tenth of the pedestal, so every trace in the 2025 dataset samples its flat
top and the linear baseline absorbs it as an offset. The record can
therefore bound ρ through that offset and can say nothing about the width,
which needs the
session.

**Needs.** Nothing new. A gigahertz-wide feature does not care about a
megahertz of lock drift, so the block needs no lock quality, no new source and
no new detection path (`FUTURE_TRANSITIONS_titsapph.md`, the decision-maker
table). As a rider it costs only the wider scan setting on dwells this document
already costs, which is what the register row means by no bench time of its
own, and the dedicated four-pedestal thermometry comb the same document costs
at about 1.9 plus 2.1 hours is that document's own standalone design rather than
this block. **Shots.** Wide scans over several GHz on the laser axis, stacked, run
as an acquisition setting on whatever else the session is doing. **Go/no-go.**
The pedestal must separate from the scattered-light background, which is not
modelled. If it does not, the block yields nothing and costs no bench time that
was not already being spent. **Empty.** The area ratio peaks at ρ = 1 where its
slope in ρ vanishes and is symmetric under ρ → 1/ρ, so it is a weak lever near
the value of record and could return no useful constraint on ρ even with a clean
pedestal. **Record.** The stacked wide traces, the fitted pedestal width and
area, and the implied temperature and ρ against the values of record. Stacking
times to reach the density-scale systematic and the assumed ρ prior are in
[`results/projections.csv`](../../results/projections.csv), on the four-component
hyperfine comb and on a single component.

## 6. The light-shift program

The triangular ramp predicts a parameter-free moment hierarchy: mean pull
−(2/3)S₀, variance/mean² = 1/8, standardized skew ≈ 0.566. The one-photon
case predicts zero skew, so the skew exists at all only because the signal
goes as I².

![the ramp construction](../../figures/fig12_ramp_construction.png)

*The object under test: the intensity distribution of a focused Gaussian
beam, weighted by the I² two-photon rate, maps to the triangular shift
distribution f(s) ∝ |s| whose moments the session measures. A focused beam does
not apply one light shift, it applies a distribution of them, and that is the
whole content of the construction. Radius is in units of the beam radius w, where
the intensity has fallen to 1/e² of its on-axis value. In (b) the number of atoms
diverges towards low intensity while the two-photon rate suppresses them faster,
and the product is linear in intensity. The density in (c) is normalised to unit
area and its standardized skew is +0.566, which exists at all because of the I²
weighting. Panel (d) is drawn at a light shift of 3 MHz so the asymmetry is
visible. Every item below is a functional of this one construction.*

The four items are tested in order of statistical cost. All four share one
prerequisite that is not itself an item: the collection rebuild at the end of
this section, which has to be in place before any of them runs.

1. **Mean pull against P** (configuration M or L). First order in S₀, the
   workhorse form test, alive only under the fixed lock.
   **Needs.** The fixed lock, the ramp-monitor export of §3 item 0, and the
   randomized power ordering it prescribes. **Shots.** Randomized power cycles
   of about 10 minutes each with the four lines interleaved, on a log grid of
   about 8 rungs over the dataset's own 25 to 225 mW ladder, run as the morning
   block of §9 D4. **Go/no-go.** The sentinel condition of §10.6 must reproduce
   within the day's own scatter, and a bracket tooth moving more than 0.2 MHz
   within a block excludes the block (§7a). **Empty.** If the lock does not hold
   minutes-scale stability the centres stay unusable and the block returns the
   2025 outcome. **Record.** Per-trace centres with their acquisition times, the
   per-rung power log, and the fitted pull. One morning of this would give
   0.09 MHz on S₀(225 mW), against a prediction of 0.35 MHz, at the dataset's own
   measured per-trace centre precision and its bounded held-lock drift rate
   ([`results/projections.csv`](../../results/projections.csv)).
2. **Excess variance against P²** (configuration L or M). Second order in S₀,
   and an independent functional of the same fitted amplitude.
   **Needs.** The same blocks as item 1. **Shots.** No additional shots, the
   second moment is read off the same traces. **Go/no-go.** The moment is
   reported as the measurement only where it sits above its own floor, decided
   by the pre-registration below rather than after the fit. **Empty.** The second
   moment may stay under its floor at every power, in which case item 1 carries
   the section alone. **Record.** The excess variance per condition with its
   floor, beside the pull.
3. **Skew hunt at S.** Not a promised result: sized for the pessimistic end
   (≥ 15× the 2025-equivalent trace count at one condition), which turns even
   the worst-case per-block significance into ≥ 3σ, detection or meaningful
   bound either way. The fringe-resolved tail suppresses the small-waist skew
   by ~26–28% (THEORY_NOTE §5), and the field-amplitude convention is pinned in
   `constants.py`.
   **Needs.** Configuration S with its metrology done, the collection rebuild,
   and RF-off traces only, since tooth overlap contaminates the centered moments
   (§10.5). **Shots.** The deep-integration day, §9 D5, at one condition.
   **Go/no-go.** Convergence of the bounded wing amplitude from a spread of
   starting values, checked before any outlier is interpreted. **Empty.** A bound
   rather than a detection is the designed-for outcome, and the sizing above is
   what makes that bound meaningful. **Record.** The third cumulant with its
   floor, the starting-value spread, and the trace count actually achieved.
4. **The geometry sign flip, the cleanest test in the program.** The z-average
   over the collection window has the closed form
   f(s) ∝ |s|^(n−1)·[ζₘ + ζₘ³/3] with ζₘ = min(Z_c/z_R, √(S₀/|s|−1))
   (`lineshape.stark_ramp_axial`). At configuration L the ramp stays clean
   (g₁ ≈ +0.56), and the 2025 dataset's M geometry carries only a few-percent
   correction (g1 +0.558). At configuration S the skew flips sign, with the
   crossover at Z_c/z_R ≈ 1.12. The flip condition is Z_c > 1.12 z_R ≈ 0.9 mm at
   S, while at L it would need Z_c > 12.7 mm, beyond any achievable field of
   view. With the cathode long axis along the beam (L∥ = 12 mm, the 2025 orientation)
   Z_c = 6/M mm, and the flip holds for every M < 6.6: secured by hardware,
   not tuning. Numbers from `scripts/run_ramp_geometry.py`:

   | orientation | M | Z_c | g₁ @ L (64 µm) | g₁ @ S (16 µm) | flip |
   |---|---|---|---|---|---|
   | long axis along the beam (`landscape` in `run_ramp_geometry.py`, 12 mm) | 1.9 | 3.16 mm | +0.555 | **−0.421** | yes |
   | long axis along the beam (12 mm) | 2.8 | 2.14 mm | +0.563 | **−0.367** | yes |
   | portrait (3 mm) | 1.9 | 0.79 mm | +0.566 | +0.103 | no |
   | portrait (3 mm) | 2.8 | 0.54 mm | +0.566 | +0.367 | no |

   The upright mounting removes the test at every plausible M. Keep the long axis along the beam.

   **Needs.** The two-lens relay and its slit, configuration S, and the cathode
   with the long axis along the beam (`APPARATUS.md`). **Shots.** The slit scan at four or
   five settings inside §9 D5, with atoms, power, lock and waist all held fixed.
   **Go/no-go.** The magnification M measured from the conjugates rather than
   assumed, since Z_c = L∥/2m is what places the configuration relative to the
   crossover. **Empty.** The sign is secured by hardware for every plausible M,
   so what could come back empty is the magnitude, which rides on the unmeasured
   lens conjugates. **Record.** M, u and v, the slit setting per point, and
   g₁ against Z_c.

**Collection rebuild: a two-lens relay.** Keep the f = 18 mm as L1 (it sets
the collection NA), add L2 (f₂ ≈ 35–50 mm, 2 inch) focusing onto the PMT,
the 795 nm bandpass in the collimated segment, and an adjustable slit at the
image plane. Then M = f₂/f₁ decouples field of view from collection, the
slit sets Z_c as hardware, and scanning the slit measures the collection
profile, an input the imaging formula cannot supply. The slit scan doubles
as a skew observable: at S alone, g₁ walks from +0.40 through zero
(Z_c ≈ 0.90 mm) to −0.42 on the slit, with atoms, power, lock and waist all
fixed. No instrumental asymmetry, blind to z_R, can mimic either flip.

   | slit → Z_c | g₁ @ L | g₁ @ S | signal @ S |
   |---|---|---|---|
   | 0.5 mm | +0.566 | **+0.402** | 35% |
   | 1.0 mm | +0.566 | −0.071 | 57% |
   | 2.0 mm | +0.564 | −0.354 | 76% |
   | 3.0 mm | +0.557 | −0.416 | 83% |

**Needs.** The f = 18 mm L1 in place, an L2 in the stated range, the 795 nm
bandpass, and an adjustable slit with a readable setting. **Shots.** No science
shots of its own. It is a §9 D1 build. **Go/no-go.** The image plane must be
reachable with the available focal lengths, and the slit setting must be
readable to better than the step the scan uses. **Empty.** If the relay cannot
be built, §6 item 4 loses its instrument and items 1 to 3 run at the 2025
collection geometry with Z_c unknown. **Record.** f₁, f₂, the measured
conjugates u and v, M, and the slit calibration.

**One fit, pre-registered.** The four items are one fit, not four: per
condition, fit a single ramp amplitude S₀ and compare the pull, excess
variance and third cumulant as three analytic functionals of it
(`lineshape.ramp_moment_contributions`), with a χ² for their mutual
consistency. Pre-register which moment is primary at each (P, w₀): the
lowest-order moment above its own floor. Report the primary as the
measurement and the others as consistency checks. Choosing post hoc which
moment "worked" is rejected, as is hybridizing extraction methods for one
moment: one estimator per observable, the hierarchy across moments only.
Any bounded amplitude that can exchange against the core is fitted from a spread
of starting values, and convergence is checked before an outlier is
interpreted. A single zero start once parked a wing amplitude at twenty times
the true optimum's χ² and read as physics for two days
([audit addendum 20](../PREREGISTRATION_RESULTS.md)). At S the sign is the robust
observable, since saturation bends the n = 2 magnitudes. The magnitudes belong
to L and M.

### The per-line lever, and the waist that makes it spendable

Three effects broaden the line with the same square-of-power signature: the
AC-Stark ramp, atomic saturation, and hyperfine pumping. They are degenerate in
**both** continuous knobs, since all three go as $P^2$ and all three go as
$w_0^{-4}$, so neither a power sweep nor a change of focus separates them. Only
one of the three differs between the four hyperfine lines, because the two-photon
operator is scalar and the ramp and saturation are therefore $F$-independent
while the pumping branching is not. A joint fit over the four peaks with those
branchings held fixed and one free scale is the only separation this method
admits **without a stable frequency reference**.

On the 2025 dataset that lever is 3.1 kHz at the committed $S_0(225)$ bound of
0.217 MHz, against an 88 kHz block scatter, short by
a factor of thirty, which is why it is stated and not spent
([the refit's preregistration](../notes/companion_inclusive_refit_prereg.md)). It
grows as the saturation width, so it grows as $P^2/w_0^{-4}$, and
`scripts/run_campaign_conditions.py` projects it:

| $w_0$ | P | saturation width | lever | vs 88 kHz | vs the same *fractional* stability |
|---|---|---|---|---|---|
| 64 µm | 225 mW | 53 kHz | 8 kHz | 0.09 | 0.09 |
| 40 µm | 500 mW | 1.42 MHz | 212 kHz | 2.4 | 1.7 |
| 32 µm | 500 mW | 2.94 MHz | 438 kHz | 5.0 | 2.6 |
| **16 µm** | **225 mW** | **6.84 MHz** | **1.02 MHz** | **11.6** | **3.5** |

The last column is the one to plan against: 88 kHz is 1.68 per cent of the
5.25 MHz line it was measured on, and a wider line will not hold 88 kHz, so the
lever is scored against the same fractional stability applied to the width each
condition actually produces. It still clears three at 16 µm **and at today's
power**. So the separation this record misses by thirty is bought by the waist
rather than by the laser, and that is a second and independent reason for the
small-waist configuration, alongside the shift gain §5 argues from.

The catch is the one the skew already has: the lever is spendable exactly where
the weak-field ramp law is least valid, since the saturation parameter reaches
1.0 at 16 µm. A session that intends to spend it must fit the saturation term
rather than carry it as a companion, which is the construction the refit
preregisters.

**There is a second catch, and it is a precondition rather than a caution.** The
refit ran, and it found that the per-line scale is not merely poorly determined
on this dataset but *unidentifiable*
([postscript](../notes/companion_inclusive_refit_prereg.md)). The pumping companion
enters the model only as a multiple of the saturation width, which is itself
proportional to $S_0=\kappa P$, and this record **bounds $\kappa$ from above
rather than measuring it**. Profiling over $\kappa$ instead of holding it, the
fit sets $\hat\kappa=0$ for every nonzero scale, the companion vanishes
identically, and $\chi^2$ comes back the same to four decimals across a factor
of thirty in the scale. There is no bound to quote.

The skew channel's turn-on now has a MEASURED threshold rather than an assumed
one. Pooling all one hundred campaign traces as one regression against the cube
of the power, with per-trace skew errors taken from the repeats themselves,
resolves a per-trace standardized skewness of about 0.01, while the ramp
predicts 1.1e-5 at the current bound: a factor near one thousand, which the
cube-root dependence of the coefficient compresses into a skew-channel bound
only 9.5 times looser than the width channel's. The signal reaches the measured
noise floor when $S_0$ exceeds about 2.5 MHz, and the 16 micron configuration's
predicted 5.56 MHz clears that threshold by design, which is why the skew
channel is dead in this archive and central to that proposal.

**Two ways of spending statistics on the skew were considered and neither
rescues the channel here.** Averaging over the repeats is the first, and the
pooled regression above already takes it: a hundred traces buy a factor of ten
on the skew's standard error, which is the whole of what independent repeats can
give. Against a shortfall near one thousand between the resolved per-trace
skewness and the ramp's prediction, that leaves a factor of about one hundred
still to find, so the arithmetic settles the question rather than leaving it
open. Smoothing the residuals before taking the third cumulant is the second,
and it does not work for a reason worth stating, because the same reasoning
recurs whenever a higher moment looks noisy. A moving average is a convolution,
and a convolution acts on the signal as well as on the noise. The third cumulant
is not linear in the data, so the smoothed residual's third cumulant is not an
estimate of the unsmoothed one with a smaller error, it is an estimate of a
different quantity. What the kernel removes from the variance it also removes
from the skew it was meant to measure, and the correlation it introduces between
neighbouring samples breaks the independence the error bar was computed under.
The channel's limit is set by the size of the effect against the noise floor,
which no reweighting of the same samples moves.

So the ordering the plan needs is explicit: **a positive detection of $\kappa$
comes first, and the per-line lever is spendable only afterwards.** The 16 µm
row above satisfies that on its own, since $S_0$ there is 5.56 MHz against a
natural width of 3.49 and cannot be confused with zero. The point is that the
factor of thirty in the table is not the whole requirement, and a session
designed to close only that factor would return the same empty profile this one
did. The general form is worth carrying into any future separation of this kind:
a term entering only as a multiple of another constrains nothing until the term
it multiplies is measured.

### Measure the waist in every session, and two analysis steps that come first

**A design requirement this plan did not previously carry.** The light-shift
coefficient goes as one over the beam waist squared, so pooling sessions asserts
that they shared a focus. The 2025 archive cannot support that assertion, because
no session measured its own waist, which is argued in
[big_picture/08](../big_picture/08_when-a-joint-fit-is-legitimate.md). **Every
block of a future session records a waist measurement**, and a session that
cannot is analysed alone rather than pooled.

**The waist measurement is taken at several powers, with the EOM in the beam
and thermalised at each.** The 2026-08-17 mechanism sweep left exactly two
candidates able to produce the measured non-monotone width-against-power
structure, and both are power-dependent geometry. The EOM crystal clips the raw
laser beam at its 3 mm aperture and sits before the focusing lens
([APPARATUS](../APPARATUS.md)), so absorbed power there makes a thermal lens
and the cell waist becomes a function of drive power, with a focus that can
walk through the cell and turn the transit width around. The archive tested the
slow-thermalisation branch through the five consecutive repeats of every
campaign block and found no within-block drift, minus 7.7 plus or minus 6.4 kHz
per repeat, which kills the slow branch only: a lens that equilibrates within
one sweep is untouched by that null and is discriminated exactly by measuring
w0 against power. The second candidate is the retro ratio rho drifting with
power, which moves the standing-wave contrast and the pedestal-to-line ratio
together, so **rho is measured against power in the same session**, closing the
one loophole the pedestal analysis names.

Two analysis steps precede the next session and run on data already in hand, in
this order.

**First, resolve which model component carries the power dependence the fit
cannot absorb.** The summary widths are concave in power, with an apex near 120 mW
and a fall from there to the top of the ladder that is about fifty times the whole
range the light-shift term can produce at its bound. The structure survives a
model-free half-max width, so it is in the data rather than in the fit. The
model-free statistic is smoothing-dependent and is read only where its own
validity control passes: stable in sign and size across a sixfold preregistered
range of the smoothing setting, while at the narrowest setting the estimator
fails its control for a measured reason, a single-sample level bias, and is not
read. Every
component in the production model is pinned against power already, so that
structure has nowhere to go and is sitting in the residual. The test frees one
component at a time per condition with the other two held at their physical
values, since all three at once is degenerate at a condition number of 345, and
the three kernels have different shapes so the comparison was expected to
identify the missing term as well as locate it.

**That test has since run as a diagnostic, and the expectation in the previous
sentence did not hold.** Freeing each component in turn across the campaign's
hundred traces, all three absorb the concavity at the same chi-square, 0.355
against 0.357 against 0.360, and none is singled out. Read as a curvature of the
total width, so that a Gaussian laser width, a two-sided-exponential transit
width and a Lorentzian collisional width become comparable, the three land
between minus 2.6 and minus 4.0 MHz per watt squared at about two standard
deviations, where the model-free summary statistic gives about minus 11 at four.
Two things follow, and the second was not anticipated. The kernels are
interchangeable against this structure rather than distinguishable by shape, so
the width degeneracy already recorded at condition number 345 governs the power
channel too. And the two constructions disagree about the size of the concavity
by a factor near three. Two follow-up diagnostics narrowed that second finding
without closing it. Pinning the per-trace baseline slope to zero, the mechanism
that could most easily have manufactured the gap, left both the reduced
chi-square and the recovered curvature unmoved, so the free slope was fitting
noise rather than absorbing width structure. Computing the disagreement
correctly, with both statistics taken from the same trace so that their shared
fluctuations cancel before averaging, puts the curvature of the difference at
about minus 4.7 with an uncertainty near 2.1, a little over two standard
deviations, where the naive comparison of the two published numbers had
suggested nearly minus 7. The direction survives and the size does not reach
the threshold this record would need to act on it.

**And on 2026-08-18 the concavity itself was withdrawn to provisional, which
settles the question above.** The archive holds two further power ladders
outside the frozen record, and tested against them the concavity does not
reproduce: it reaches 4.8 standard deviations only on within-cell errors and
1.4 under the between-block treatment, the pilot's independent non-monotone
ladder gives the same sign at 1.2, and in the rehearsal a width trend appears
on the descending ladder while both ascending ladders show none, which is
order dependence rather than power dependence. Section C3a's original reading,
that this variation is block scatter, stands. The estimator disagreement above
therefore concerns the size of an effect whose existence is not established,
the thermal-lens hypothesis is demoted accordingly, and the measurement that
would settle both is an interleaved power ladder rather than any further
analysis of a monotone one. Breaking the
first finding needs a channel where the kernels are not interchangeable, which
is what the waist measurement below and an independent laser-width calibration
supply. The diagnostics promote no number and the record's own concavity
statement is unchanged.

**Second, and only afterwards, free the transit reference so the cusp measures
the waist.** The transit kernel goes as the square root of temperature divided by
the waist, and the repository currently sets its reference by computing it from
the waist, which spends the information rather than collecting it. Run the other
way it becomes a waist measurement internal to the lineshape and independent of
the apparatus lineage, and the transit kernel is separable by shape rather than by
width, since neither the Lorentzian nor the Gaussian beside it can imitate a cusp.
The order matters: if the unexplained power dependence turns out to live in the
transit kernel, freeing its reference first would let a power systematic
contaminate the waist.

---

*[Configurations and optics](03_optics-protocol.md) · [Width, collisions and amplitude](05_width-collision-amplitude.md)*
