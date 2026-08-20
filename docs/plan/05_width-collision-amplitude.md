*Chapter 5 of 11 of [the plan](../PLAN.md)*

**The question.** How would the collisional coefficient be separated from the laser width, and what does the amplitude channel add?
**Takes.** The intensity axis of chapter 4.
**Gives.** The width and collision blocks, and the amplitude programme.
**Skip if.** You want acquisition settings, which is chapter 7.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> **Question.** How would the collisional coefficient be separated from the laser width, and what does the amplitude channel add?
> **Design.** An interleaved density ladder with an independent laser-width measurement.
> **Ambiguity removed.** The voigt ridge between the collisional and laser widths.
> **Success.** The pinned fit's scatter falls by the projected factor and the density trend survives block noise.
> **Residual uncertainty.** The density scale, which needs an absorption channel this session does not include.

## 7. The width and collision program

**7a. Temperature grid at L only, twice, on different days, in opposite
directions.** Cancels every drift component monotonic in time in the mean, and
the difference measures the residual. Jump-like drift does not average out. It
gets cut.
**Needs.** The fixed lock, configuration L metrology complete, and the oven
settled. **Shots.** The full T grid ascending on one day and descending on the
next, four peaks interleaved per dwell, with RF-off brackets before and after
plus an EOM ruler per block. **Go/no-go.** A pre-registered bracket veto: a
bracket tooth moving more than 0.2 MHz within a block excludes the block.
**Empty.** The residual between the two directions may exceed the physics. That
outcome is the deliverable rather than a failure, since the residual is the
systematic error bar the 2025 record had to assume. **Record.** Both grids
with their directions, the veto census, and the difference.

![the 2025 dataset's width-vs-density floor](../../figures/fig6_gamma_floor.png)

*The floor in the 2025 dataset that this program upgrades: the mean of
the four fitted collisional widths rises only ×1.47 while the density
rises ×52.5, so the 2025 slope is a bound. A binary-collision width
would be proportional to density, so these four points bound the
coefficient rather than measure it, and the bound
moves with the density range used, which is why the figure draws two of them.
Neither straight line is a fit: each is what the width would do if the
coefficient took the value fitted over the range named beside it. The dashed one
reaches 1.9 MHz at the highest density shown, where the measured mean of the four
peaks is 0.59 MHz. The density axis is logarithmic and carries the vapour-pressure
model's 20 per cent scale systematic, common to every point. The session's levers
are the two the figure lacks: densities at 150–170 °C, and block noise cut 4× by
interleaving.*

**7b. At least five temperature blocks per peak.** The record's headline runs
on four points and two residual degrees of freedom, so its error multiplier is
t(0.95,2) = 2.92 (the three-point construction it replaced paid ×6.31 on one).
Five blocks give t(0.95,3) = 2.35, a further tightening before any drift
compensation, and the cheapest statistical buy on the page.
**Needs.** Nothing beyond 7a. **Shots.** Five conditions per peak on the grid
rather than four. **Go/no-go.** None of its own. **Empty.** No empty case, the
blocks either run or they do not. **Record.** The block census per peak.
**Open item for this block.** The record's headline fits the four lines
separately. A pooled estimator with one shared slope and per-line floors is
pre-registered in
[`docs/notes/beta_self_pooling_prereg.md`](../notes/beta_self_pooling_prereg.md),
which brackets its own net gain at 1.1 to 1.8 because the between-block scatter
that dominates the error is strongly shared across the four lines. Whether the
session sizing changes under that estimator is not settled here, and it should
be settled before the shot list is frozen, since a pooled slope changes what a
fifth block buys.

**7c. 150–170 °C in the same locked session, interleaved.** Wanted for a
narrower reason than the 2025 post-mortem gave it. The 2025 dataset's lever test
shows the joint β collapses 0.0534 → 0.0198 for ⁸⁵Rb and 0.0219 for ⁸⁷Rb when
the ×53 anchor (the 130 °C block) is folded in
([`lever_crosscheck.csv`](../../results/lever_crosscheck.csv)). That collapse is not a session artifact. It is the correct
least-squares response to a line that barely moves across a 52.5× density span
(gamma_coll rises only ×1.47–1.9), which is what makes "residual floor, not
resolved collisions" a demonstrated conclusion rather than an assumption. The
2026-08-02 decision that promoted the four-point fold-in to the record's
headline, and the reasoning behind it, are recorded in
[`PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md). What a same-session
150–170 °C extension still buys, on top of that fold-in: it removes the
cross-epoch calibration step entirely rather than relying on it being handled
correctly after the fact, and it is the only route to densities where a genuine
~kHz collisional effect could clear the block-noise floor. The record's
four-point bound (≲0.03–0.05 MHz per 10¹² cm⁻³) is still roughly an order of
magnitude above the ~3.5 kHz expectation (§1,
[`BIG_PICTURE.md`](../BIG_PICTURE.md) §1), so the case for the session is about
reach, not about combining points at all.

A THIRD REASON, INDEPENDENT OF BOTH, from the influence audit of 2026-08-16.
On the density axis the three lower temperature blocks sit close together and
the 130 °C anchor sits far from them, so the anchor carries a hat-matrix
leverage of 0.996 on all four peaks. A straight line through that design passes
very nearly THROUGH the far point whatever the far point says, which has a
consequence worth stating plainly: THE FOUR-POINT CONSTRUCTION CANNOT DETECT AN
ERROR IN ITS OWN ANCHOR. An outlier planted at 130 °C leaves almost no
residual, and the audit's power ladder failed to detect one at any size up to a
hundred times the point's own error bar. Nothing about the anchor is thereby
suspect. What is established is that the construction is not able to check it,
so the anchor is an input to the slope rather than a constraint on it.

Points at 150–170 °C move the far end of that lever and put a second constraint
out there, which converts the collisional coefficient from anchor-defined to
checkable. SPACE THEM IN DENSITY RATHER THAN IN TEMPERATURE. Density rises
steeply enough with temperature that evenly spaced set points cluster at the
cold end and leave the hot end carrying the fit, which is the geometry that
produced the leverage above. The same audit found the 25 mW condition neither
outlying nor influential on any peak, so its large error bar is already doing
the right thing and it needs no special handling.

WHICH OF THIS SECTION'S ASKS ACTUALLY MOVES THE PROJECTION. A global
sensitivity analysis of the projected precision, decomposing its variance
across the plausible range of every design input, ranks them:

| design input | share of the projection's variance |
|---|---|
| the top temperature reached | 0.58 |
| the cold-spot lag | 0.33 |
| the block-noise cut from interleaving | 0.27 |
| the measured block-to-block width scatter | 0.02 |
| the NUMBER of temperature blocks | 0.002 |

THE BLOCK COUNT BUYS ALMOST NOTHING, which is the same fact as the leverage
above seen from the other side: the lever is the spread of densities about
their mean, and the hottest point dominates that spread, so intermediate blocks
near the cold end add almost none of it. The session should argue for REACH and
for MEASURING THE LAG rather than for more points. The lag deserves particular
attention because it carries a third of the variance and is currently a
face-value figure rather than a measurement, which is what makes the day-one
item that measures it worth more than its duration suggests. A caution on that
item's range: at a 70 °C coldest block a lag beyond about 31 K would put the
cold spot below the rubidium melting point, which would be a different physical
regime rather than a larger correction.
**Needs.** An oven that reaches and holds 170 °C, and the cold-spot lag
characterised (§8 item 3). **Shots.** The top of the grid taken inside the same
locked session as the rest of it, in interleaved temperature order. **Go/no-go.**
The oven must hold each set point long enough for the dwell without the cold
spot lagging outside the band §8 item 3 measures. **Empty.** The oven may not
reach or hold the top of the range, in which case the grid stops where it stops
and the bound stays where the record has it. **Record.** Set point, measured
cell temperature, and the cold-spot offset per condition.

![the EOM comb and its nonlinearity map](../../figures/fig8_ruler.png)

*The ruler as it worked in 2025: line replicas 6.25 MHz apart on the laser
axis, and the empirical sweep-linearity map they stitch. Six of the seven
labelled slots carry a tooth standing above the fit residual. The seventh does
not, because the third-order pair carries about 2% of the first-order power at
this drive depth and the scan clips an outer window, which is the case on every
recorded ruler and is why the seven-standing clause was relaxed to six
([the ruler specification](../notes/ruler_validity_and_trim_prereg.md) amendment 4).
The trace drawn is the one that clears every clause of §7 of the same note, with
the weakest of its seven heights at 0.63 of the fit residual and a reduced χ² of
1.01 against the ceiling of 2.0. In the right panel the sweep non-linearity and
any tooth-dependent pull together stay within 0.3%, and that bound is set by the
well-sampled windows alone. The open markers at the scan edges have an
uncertainty larger than the bound, so they do not constrain it. The session keeps
the comb and fixes its two hardware mismatches, below.*

**7d. The matched-PM ruler, and the two knobs a seven-tooth comb needs.** In
2025 the ruler light differed from the science light (the half-wave-plate
carrier-suppression trick), so tooth widths could not serve as a drift
compensator. The fix is to drive the EOM at modulation index β ≈ 1.202, where
the two-photon comb's central tooth nulls by pair interference (A_k ∝ J_k(2β)²)
and the ruler runs at science polarization and power. Interleave rulers with
science blocks rather than only bracketing, so that the time-resolved rate model
now standard in the pipeline is tested within a session rather than assumed
across one. The campaign rate carries a 0.2046 per cent error from an
eight-member estimator family, and the per-block relative rate errors run from
0.32 to 1.69 per cent with a median of 0.49 per cent
([`ruler_validity_and_trim_prereg.md`](../notes/ruler_validity_and_trim_prereg.md)),
which is the spread an interleaved ruler would resolve rather than carry.

The dataset also settles what the current settings can and cannot deliver, and
this block asks for the two changes that would lift them. The measured drive
depth across the campaign is 2β ≈ 1.57 median, so β ≈ 0.79, against the β ≈ 1.202
this block prescribes. `APPARATUS.md` §6 places the campaign drive at 54 to 60
per cent of full modulation, with the index scaling as 1/λ from the 780 nm
certificates, and it records that the generator's 25 MHz ceiling constrains any
higher-frequency tank. Whether the 12.5 MHz tank reaches β ≈ 1.2 is therefore an
open item for this block and is the first thing to test on the bench. Second,
the ramp is too short: no recorded ruler covers both outer tooth windows, the
k = −3 window is clipped on 52 of the 104 fitted combs and the k = +3 window on
36, and at the measured depth a fully covered third-order tooth still stands at
0.63 of the per-trace fit residual. Widening the scan by about one tooth spacing
per side and deepening the drive until the third-order pair clears the residual
is what would give every calibration trace seven standing teeth instead of six.
**Needs.** An EOM tank able to reach the prescribed index at 993 nm, a generator
inside its own frequency ceiling, and a ramp about one tooth spacing wider per
side. **Shots.** Ruler blocks interleaved with science blocks at the cadence
§10.5 measures, at science polarization and power. **Go/no-go.** Monitor
modulation purity live through the A₊ₖ = A₋ₖ symmetry. Fit the comb to ±3 orders
where the scan covers them, since truncating at five biased the 2025 rate by
0.1% ([audit addendum 19](../PREREGISTRATION_RESULTS.md)), and record the coverage
per trace rather than assuming it. Calibrate any control-variate coefficient on
dedicated dither data, and freeze all decision rules before first data. A
correction may widen a bound. It may never, by itself, flip a bound into a
measurement. **Empty.** If the tank cannot reach the index, the ruler still runs
as a bracket and the drift-compensator role is lost, which is the 2025 outcome.
**Record.** The achieved index per session, the tooth coverage per trace, and
the interleaved rate series.

**7e. A returned-to block.** Re-measure one earlier condition later in the
session. Every bound that averages block scatter assumes the scatter averages
down. A systematic common to all peaks at a setting does not, and the 2025
design cannot tell the two apart: the permutation test against the independence
null returns p = 0.21 (`results/resolving_power.csv`), neither established nor
excluded. One block settles it. This is load-bearing for S₀, whose predicted
effect is about one block scatter.
**Needs.** An earlier condition recorded well enough to reproduce exactly.
**Shots.** One repeat block at that condition, later the same session.
**Go/no-go.** The condition must be reproduced identically, since a
near-repetition tests nothing. **Empty.** One block settles the direction and
not the magnitude, so a null here is weak evidence rather than a clean answer.
**Record.** The repeat block beside its original, and the difference.

**7f. Four peaks interleaved within every block**, minutes apart, with
per-trace power logging. Cross-peak systematics drop from 30–50% to 2–4% and
the amplitude discriminators (§8) become possible. Amplitude-ratio blocks get
12–16 repeats (gain-limited), width blocks 8, with the power order randomized.
**Needs.** Nothing beyond the fixed lock. **Shots.** All four lines inside each
dwell. **Go/no-go.** None of its own. **Empty.** No empty case. **Record.**
Per-trace power beside every trace.

**7g. Per-scan timestamps in hardware metadata, not just the notebook.** The
2025 exports carried no acquisition time, which is the single reason the
σ_laser-sharing behind the hierarchical β is untestable. The recovered clock
later showed the four peaks of a dwell sat 54–76 min apart. A wall-clock on
every scan makes the sharing a tested fact, reconstructs the drift diary, and
time-orders the interleaved blocks.
**Needs.** The scope of record. On the Agilent, save the native `.h5`, whose
metadata carries the time, or take repeats as segmented acquisitions with
per-segment trigger times (`APPARATUS.md` §4.1 identifies the export signature).
Either path also needs a loader, since `rb5s6s/ingest.py` reads only the
two-column 2000-row CSV export and has no `.h5` reader. That is the one place
this programme knowingly buys software as well as shots.
**Shots.** Every science trace. **Go/no-go.** Set the scope clock at session
start and note block starts independently, so that the external log can
reconstruct the order if the metadata path fails. **Empty.** If neither path
works the block order is again the only time coordinate, which is the 2025
outcome. **Record.** A wall-clock per trace. The LeCroy's per-trace
TRIGGER_TIME is demonstrated on the 4 July evening session's files, but
its ~250× file weight buys nothing for a 60 ms feature, so choose it
only if the external time
log fails in practice.

**7h. Etalon-lock thermal discipline.** The 2025 disturbance was not drift but
dropouts inside the ~2 h etalon transient (re-kick amplitude 4.4 MHz, recapture
τ = 97 [87, 118] min, validated out of sample, `APPARATUS.md` §6). Engage the
etalon lock at least 2 h before first data, budget the transient again after any
pause of 3 h or more, and once past it keep hands off the reference. At the
held-lock rate a 43 MHz window lasts ~40 h.
**Needs.** The etalon lock engaged early enough, and a spare channel for the
lock state. **Shots.** One long off-resonance capture for the noise spectrum.
**Go/no-go.** No science block starts inside the transient. **Empty.** The
transient may run longer on the day than the dataset measured, which costs
setup time rather than data. **Record.** The lock state on its spare channel,
and the noise spectrum. The 2025 chain carried a 61 Hz line at 0.2% of peak,
harmless on a 60 ms line and not harmless on the narrower lines this session is
for.

**7i. σ_laser at L.** Transit removed by geometry, collisions bounded
externally at tens of kHz by the literature scale. Quote it with that prior
stated, or as a bound. Never as an assumption-free measurement.
**Needs.** The configuration-L waist measured (§4.2), so that transit is
removed by geometry rather than by fit. **Shots.** Falls out of the T grid.
**Go/no-go.** The three length rulers of §4.2 must agree before the transit
term is subtracted. **Empty.** It stays a bound if the external collision prior
cannot be tightened. **Record.** The fitted core width, the subtracted transit
term, and the prior with its source.

**7j. The width-to-shift ratio, a fixed-lock-only check.** A drifting lock
cannot measure a pressure *shift*. Only widths survive the 2025 dataset, so the
session's centre channel is what would let this run. Lewis (1980, Table 4.1)
predicts $2\gamma/\beta = 2.75$ for a pure $n=6$ van der Waals potential, a
second and independent test of the van der Waals anchor beyond the $T^{0.3}$
width-scaling check of
[`methods/06_the_statistics.md`](../methods/06_the_statistics.md) §4.2, and one the
dataset has no route to at all.
**Needs.** The fixed lock and the density lever of 7c. **Shots.** Rides the T
grid, with centres retained. **Go/no-go.** The centre channel must survive the
§10.6 sentinel at the densities in question. **Empty.** The pressure shift may
stay under the block scatter across the whole grid, leaving the ratio a bound.
**Record.** Width and shift against density, and their ratio against the
predicted 2.75.

## 8. The amplitude program

Amplitudes were useless in 2025 for one measured reason: within-block
statistics of 1–3% under a between-block gain, power and polarization wander
of 30–50%. Every exploit below is a ratio, a within-block slope, or a
monitored quantity, so the wander cancels identically. All five share the
prerequisite of §7f, four peaks interleaved with per-trace power logging,
without which none of them clears the wander.

1. **The degeneracy-law test.** The S→S operator is pure scalar, so line areas
   are pure initial population: within one isotope the area ratios are
   parameter-free, 5/3 for ⁸⁷Rb and 7/5 for ⁸⁵Rb, and on interleaved lines the
   test runs at the 1–3% floor. The cross-isotope total-area ratio is the flat
   abundance ratio 2.59, constant in T, whose curvature onset flags PMT
   nonlinearity.
   **Needs.** §7f. **Shots.** No shots of its own, it reads the interleaved
   blocks. **Go/no-go.** The PMT-linearity certificate of the defensive set
   below, with its ceiling pre-registered. **Empty.** PMT nonlinearity may
   swamp the 1–3% floor, which the cross-isotope curvature is there to reveal.
   **Record.** Areas per line per block, and the cross-isotope ratio against T.
2. **The four-line common-slope Δα fit.** Δα is electronic and scalar, so all
   four lines share one Stark slope: a fourfold over-determined Δα with
   line-specific pulls isolated as residuals. Since area ∝ I², √area is a
   per-trace intensity proxy that soaks up alignment wander.
   **Needs.** §7f and the §6 item 1 power blocks. **Shots.** Rides §6 item 1.
   **Go/no-go.** A pre-registered admissibility gate restricting the √area proxy
   to configuration L, since S is saturated. **Empty.** The line-specific
   residuals may not separate from the shared slope at the achieved precision.
   **Record.** The shared slope, the four residuals, and the proxy against the
   logged power.
3. **An absorption channel for N(T).** A weak D-line probe plus photodiode:
   transmission is immune to PMT gain, and its log-slope against 1/T returns the
   vapour-pressure curve. A cold spot flattens the high-T end, so the offset
   measures the cold-spot lag directly. The record prefers ΔT_cs ≈ 20 K at face
   value (0–30 K unexcluded), and at 1.4× to 7× leverage on the collisional bound
   the cold spot is plausibly a larger systematic than w₀. This is the single
   highest-value hardware addition of the session.
   **Needs.** A weak D-line probe source and a photodiode, neither on the bench
   today. The one non-PMT detector the apparatus record does list, the New Focus
   2153 infrared receiver (`APPARATUS.md` §3), is item 5's cascade detector and
   does not serve this block. **Shots.** Transmission against 1/T across the full grid, including
   the 150–170 °C points of 7c. **Go/no-go.** The probe must be weak enough not
   to perturb the ground-state population that the two-photon rate reads.
   **Empty.** The cold spot may not flatten enough at the high end for the offset
   to be read, leaving the lag where the record has it. **Record.** Transmission
   against 1/T, the fitted vapour curve, and the cold-spot offset. This is the
   measurement that would replace the density-scale systematic the
   record's bound currently carries.
4. **Fluorescence over absorption.** Absorption sees true N, fluorescence the
   trapping-distorted emission. Their within-block ratio cancels N and isolates
   the trapping-modified collection efficiency, sharpest at 150–170 °C. Real
   trapping is smooth in density. Drift is not.
   **Needs.** Item 3 running. **Shots.** Rides items 1 and 3. **Go/no-go.** The
   ratio must be formed within a block, since between-block gain wander is what
   it exists to cancel. **Empty.** Without item 3 it does not run at all.
   **Record.** The within-block ratio against density.
5. **The 1.3 µm cascade channel.** The 6S decays via 5P (1324/1367 nm) before
   the detected D-line photons, and the 1.3 µm photon is resonant with nothing
   populated, so it escapes trapping-free. Detecting it measures the degeneracy
   law without the trapping confound, and running 795 nm and 1.3 µm at the same
   condition turns any off-ratio into a verdict. The technique is proven on the
   sibling 5D lines (Hassanin 2023, Beard 2024). Only its use on this test is
   new.
   **Needs.** An InGaAs detector covering 1.32–1.37 µm. The bench already
   carries an IR receiver whose specification is in `APPARATUS.md` §3.
   **Shots.** Simultaneous 795 nm and 1.3 µm at one high-density condition.
   **Go/no-go.** The cascade rate must clear the detector's own noise floor at
   the achievable density. **Empty.** If it does not, item 1 keeps the trapping
   confound and item 4 remains the only handle on it. **Record.** Both channels
   at matched conditions, and the area ratio in each.

Defensive set, all cheap: the forbidden-polarization extinction null (§4.4),
a pre-registered radiation-trapping sentinel fencing the high-T points, area
rather than peak height as the drift-robust observable, and a PMT-linearity
certificate spanning the full fluorescence range with a pre-registered
ceiling.

## The cascade gives the amplitude channel a competing prediction

Added 2026-08-19, when `rb5s6s/cascade.py` made the pumping calculation
callable rather than a one-off script.

The amplitude programme's open question is that the departure from the
square-of-power law orders itself by peak BRIGHTNESS rather than by branching
ratio, which reads as a detection signature rather than an atomic one. That
was an observation without an alternative to test it against.

There is one now. Hyperfine pumping predicts its own ordering, and it is
DIFFERENT. Each excitation returns the atom to the undriven ground level with
probability f, so a line's amplitude falls with the number of cycles an atom
completes while crossing the beam, and the four lines have

| line | branching f | surviving fraction after three cycles |
|---|---|---|
| 4121 | 0.3725 | 0.247 |
| 4154 | 0.3476 | 0.278 |
| 4192 | 0.2483 | 0.425 |
| 4207 | 0.2235 | 0.468 |

so pumping depletes 4121 fastest and 4207 slowest, spanning a factor of about
1.9 in the surviving fraction. **The brightness ordering and the pumping
ordering are not the same ordering**, which is what turns the four-peak trace
from a descriptive measurement into a discriminating one: it does not merely
record four amplitudes, it chooses between two named mechanisms.

Two conditions on reading it, both stated before the measurement rather than
after. The comparison is between RATIOS within one trace, since a common
factor multiplies all four and cancels. And the cycle count is not known
independently, so the test is on the ORDER and on the spacing pattern rather
than on the absolute depletion, which the transit time and the excitation
probability jointly set.

If the amplitudes follow the pumping order the effect is atomic and the model
already predicts it. If they follow brightness the effect belongs to the
detection chain, and the dual-chain recording of chapter 7 is what localises
it. Either outcome closes the question, which is the property worth having.

## The laser kernel is the largest assumption the width channel rests on

Measured 2026-08-20 and worth stating before the session is designed, because
it changes what the density ladder is buying.

Fitting every canonical condition twice, differing only in whether the laser's
own contribution is modelled as a Gaussian or a Lorentzian, moves
$\gamma_{\rm coll}$ by a median **45 per cent**. Lorentzians add linearly, so
a Lorentzian laser width is degenerate with the collisional width and competes
for the same wings. That is a larger lever on the collisional coefficient than
anything else the record has examined.

The archive does discriminate, which was not expected: the Gaussian fits
better on 32 conditions of 32, never once losing. So the assumption the record
makes is the one the data prefer, and the width channel is not resting on an
arbitrary choice. **It is resting on a choice that has now been tested**, which
is a different and much better position.

**What the session should carry from this.** The comparison run here is
between two extremes. A laser kernel with a FITTED Lorentzian fraction turns
that binary into a bound on the Lorentzian content, and that bound is the
model-form error bar on $\beta_{\rm self}$ the paper should quote beside the
transit-kind one. It costs no beam time, only a fit, and it should be run
before the session rather than after
(`scripts/run_laser_kernel.py`, `results/laser_kernel.csv`).

## One term the density ladder cannot separate, and what would

The density ladder is the instrument for $\beta_{\rm self}$, so it is worth
naming a term that shares its signature exactly and therefore hides inside
it. A two-atom cooperative channel puts a satellite at twice the single-atom
magnetic position, because a PAIR can accept the two units of angular
momentum a single $J=1/2$ atom must refuse
([`rb5s6s/cooperative.py`](../../rb5s6s/cooperative.py)). Its rate is linear
in density, since it needs a second atom, and so is its contribution to the
measured width.

**Linear in density is what $\beta_{\rm self}$ is.** The two are degenerate
under the ladder, and no number of temperature blocks separates them. The
term is absorbed into the collisional coefficient.

That is harmless here only because of the size: at Earth's field and 130 °C
the satellite adds $3\times10^{-4}$ hertz to a collisional width of 492 kHz,
six parts in ten thousand million. It is named because the reasoning is what
generalises. **A design whose only lever is density cannot distinguish any
two terms that are both linear in it**, and the way out is not more density
points but a second lever. Here that lever is the FIELD: the collisional
coefficient is indifferent to it and the satellite's width contribution goes
as $B^2$, leaving the line entirely above 384 microtesla.

The coincidence block's self-calibrating field readout is therefore doing
more than housekeeping. It is the only axis along which a term of this class
is separable at all, and any future term that turns out to be
field-dependent inherits the same argument.

## The asymmetry budget, and how the model earns a new term

The record measures an asymmetry it does not explain. C3g is the open
finding, a same-side near-core asymmetry in both sessions, absorbed neither
by a detector time constant nor by the wing nuisance, and the band-excess
finding names a better profile as the next lever. So the question is not
whether the lineshape model is missing something asymmetric but WHICH
asymmetric thing, and the answer is earned by decomposition rather than by
adding a free skew parameter, because the shape channel is where the physics
lives: the AC-Stark ramp's own asymmetry is the kappa signal, and a free
skew would absorb it together with every systematic below into one
uninterpretable number.

Each candidate carries its own scaling and its own reversal knob, which is
what makes the budget separable:

| mechanism | scales with | reversal or signature | disposition |
|---|---|---|---|
| detection lag | sweep rate | odd under sweep direction, so the triangle-half difference isolates it and the mean cancels it | separable by design, needs the direction column of [chapter 8](08_the-acquisition-record.md) |
| the AC-Stark ramp | power | fixed side, follows $\kappa$ | in the model already, it is the signal |
| neighbour wings and pedestals | geometry only | none, computable | the linear part is absorbed by each trace's fitted baseline, and the surviving curvature is sized inside the residual audit's model-set stage rather than guessed here. In the wide-span design the baseline is a SUM of four pedestals by construction, per [chapter 9](09_the-fixed-lock.md) |
| speed-dependent collisions | density | third cumulant against $N$ | admitted only if the density-keyed skew demands it. The far-wing version is already nulled by M24, and the core is a separate question |
| vector light shift with pumping | power times circular admixture | REVERSES with the ambient field or a half-wave flip | the one door the magnetic field has into this lineshape, and a coil on the cell makes the test free |
| standing-wave fringe skew | geometry | suppressed by the fringe-resolved slow tail | closed |

The decision instrument exists in the record: every fit already carries a
per-trace residual skew, and stacking it per condition, keyed by rate, by
power, by density and by line, is the model-free half of the residual audit.
Whichever row reproduces C3g's signature, same physical side in both
sessions and near the core, is the term the model gains, keyed to its knob
and never free. The digital twin then sizes each row the other way round,
injecting the mechanism and reading what the SYMMETRIC fit does to
$\beta_\text{self}$ and to $\kappa$, so the cost of leaving a term out is a
number rather than a fear. That injection layer is the twin's next scheduled
extension.

## What the twin says the width programme can and cannot buy

Measured 2026-08-19 on synthetic data whose truth is known, through
`rb5s6s.forecast`, and recorded here because it changes which levers are
worth session time.

**More of the same measurement does not separate the widths.** The
correlation between the laser width and the collisional width sits near
-0.92 and STAYS there: -0.9177 at a 60 MHz span, -0.9166 at 300 MHz, and
-0.881 with ten times the traces. Both uncertainties shrink as the data
grow, and the direction the observable cannot see stays invisible. The
degeneracy is a property of the lineshape rather than of the sample size, so
no scan design defeats it.

**An external constraint is worth a factor of two to three and a half, and
it is the only thing that is.** Pinning one member of a correlated pair
reduces the other's variance to $(1-\rho^2)$ of its joint value, so the
uncertainty falls by $\sqrt{1-\rho^2}$. That factor depends on $\rho$ and on
nothing else, which is why it is not a single number here: 2.29 at the
correlation of $-0.90$ this record measures as its median across the 32
conditions, 2.52 at the twin's design point, and 2.97 at the bright condition
of `scripts/run_width_pinning.py`, whose direct Monte-Carlo scatter ratio is
$3.18 \pm 0.20$ across nine seeds. The arithmetic and the simulation agree to
7 per cent at the same condition, and
[the identifiability page](../wiki/identifiability.md) carries the
comparison. All of it is available from a measurement that never touches
the atoms.

**Consequence for this chapter's programme.** An independent laser-width
measurement is not one lever among several, it is the ONLY lever that acts on
the identifiability rather than on the noise. Session time spent widening
scans or adding repeats buys precision on a quantity the record already
declines to quote, and session time spent measuring the laser elsewhere buys
the quantity itself. The ranking follows from the arithmetic rather than from
preference.

---

*[Intensity and the light shift](04_intensity-and-light-shift.md) · [Session sizing and spending rules](06_sizing-and-spending-rules.md)*
