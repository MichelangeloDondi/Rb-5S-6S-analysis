# A fixed-lock session for Rb 5S₁/₂→6S₁/₂: proposal and measurement protocol

**The question.** What would a next session measure, what would it cost, and
what does each block return if the effect is not there?
**Takes.** [CLAIMS.md](CLAIMS.md), for what is bounded rather than measured
today.
**Gives.** The session blocks with their instruments, their durations and their
empty cases, ranked by what a shrinking budget should cut.
**Skip if.** You want what has been delivered rather than what is proposed.
Every verb here is conditional on a session that is not scheduled.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## The proposal in five lines

**The research question.** Can the collisional self-broadening and the
AC-Stark light shift of the 993 nm two-photon line be measured rather than
bounded?

**The bottleneck.** The 2025 session ran under a lock that drifted, so line
positions carried no information and only shapes did. Reading shapes alone
leaves the collisional width degenerate with the laser width, and leaves the
light shift bounded at below 0.26 MHz at 225 mW against 0.35 MHz predicted,
with the collisional coefficient bounded at 0.03-0.05 MHz per 10¹² cm⁻³.

**And the degeneracy has a second face, measured 2026-08-20.** It is not only
the laser width that competes with the collisional one. The laser kernel's
SHAPE does too, and by more. Fitting every peak twice, differing only in
whether the laser's contribution is a Gaussian or a Lorentzian, moves the
headline collisional coefficient by 45 to 67 per cent, nine to eighteen sigma
on its own quoted error. A per-condition version of the same comparison was
withdrawn on 2026-08-20: at fixed condition the two widths enter only through
their sum, so the split is unidentified and only the density ladder separates
them. The mechanism is that Lorentzians add linearly and a Lorentzian laser width is degenerate with a collisional one in
a way a Gaussian is not. The two kernels are not alternatives: the pure-Lorentzian
model is NESTED inside the Gaussian one, reached by letting the Gaussian width
go to zero, so the Gaussian cannot fit worse and the 32-of-32 tally is
arithmetic rather than evidence. The informative quantity is the SIZE of the
improvement as a nested likelihood ratio, a median delta chi-square of 232 for
one boundary parameter, which excludes a purely Lorentzian laser contribution
at 26 of the 32 conditions at better than three sigma. What the session should carry from it is that a fitted
Lorentzian-equivalent WIDTH inside the containing model turns that comparison
into the model-form error bar on the collisional coefficient, and costs a fit
rather than beam time
(`scripts/run_laser_kernel.py`).

**The proposed measurement.** A vapour-cell session under the repaired cavity
lock, with an independent measurement of the laser width, a span wide enough
to fit the Doppler pedestal as a pedestal, two same-isotope frequency rulers
inside every sweep, and a randomised power ladder.

**What it would establish.** The two bounds above become measurements, the
frequency axis becomes calibratable, and the baseline becomes data rather than
a modelling choice.

![where each bound stands today and where the campaign is projected to put it](../figures/fig34_campaign_projection.png)

*The proposal in one figure. Three quantities, each against its own reference
with the reference named in the row label, filled for what the 2025 archive
supports and open for what one designed campaign projects, with the single
lever that moves each named on the segment. The AC-Stark row is the cheapest
and the closest to turning a bound into a measurement. The collisional row
moves furthest, and its two markers are different kinds of number, a bound
today and a precision after. The width split moves least, which is the
argument for a fixed lock and against simply taking more traces. Every value
is read from a committed CSV.*

**Where the detailed design lives.** In the eleven chapters below, with
[the case in ten minutes](plan/00_the-case.md) as their opening summary.
Nothing
here is scheduled, no date is assumed, and the specification names no
operator. It is a specification, not a booking.

![the drift problem, what was extracted from it, and what a fixed lock buys](../figures/fig15_drift_story.png)

*The reason this document exists, before any of its procedure. The 2025 lock
was re-centred by hand between blocks, so the line's absolute position carries
no meaning across a step and every result is a bound read out of the line
SHAPE. The bottom panel is what a fixed lock converts, and each block below is
costed against exactly that.*

## The chapters

| # | chapter | what it covers |
|---|---|---|
| 0 | [The case in ten minutes](plan/00_the-case.md) | what was measured, what is not identified, the one intervention that breaks each, what a campaign is projected to achieve, and what this record refuted with its own instruments. Start here |
| 1 | [The aim and the objections](plan/01_aim-and-failure-modes.md) | what the session is for, and the objections a referee would raise first |
| 2 | [Priorities if the budget shrinks](plan/02_priorities.md) | the order in which blocks would be cut, and the one lever that acts on identifiability rather than on noise, the independent laser width |
| 3 | [Configurations and optics](plan/03_optics-protocol.md) | the optical layout and the alignment protocol |
| 4 | [Intensity and the light shift](plan/04_intensity-and-light-shift.md) | the intensity axis and the light-shift programme |
| 5 | [Width, collisions and amplitude](plan/05_width-collision-amplitude.md) | the width and collision programme, the amplitude programme, the cascade's competing prediction that makes the four-peak trace discriminating, and the asymmetry budget that decomposes the open C3g finding by reversal knobs, the laser kernel as the largest assumption the width channel rests on, and the one term a density ladder cannot separate from collisions |
| 6 | [Session sizing and spending rules](plan/06_sizing-and-spending-rules.md) | the block register, session sizing, the rules drawn from the 2025 post-mortem, and costing by information per unit of effort |
| 7 | [Acquisition settings](plan/07_acquisition-settings.md) | span, sweep and instrument settings, the three-oscilloscope comparison measured from the files, the settings card, and the modulation-and-rate menu that assigns the depth and the scan rate per scan purpose |
| 8 | [The acquisition record](plan/08_the-acquisition-record.md) | what every block must log, the comb read as a ruler and as a clock, the EOM drive menu with the coincidence and cascade designs, the coincidence block's own in-cell field readout, the sweep-direction and mains-phase columns, and the wavemeter shots |
| 9 | [The fixed lock, and what it buys](plan/09_the-fixed-lock.md) | identifiability, drift, the sweep and the scan axis, and the two rulers with their division of labour, the atomic pairs as the light-shift-immune anchor and the comb as the interpolator and the clock |
| 10 | [The instrument and the session](plan/10_the-fixed-lock-instrument.md) | the oscilloscopes, the pedestal thermometer, the day-one list including the split-signal dual recording, polarisation, and the comb as a statistical instrument |
| 11 | [Beyond 993 nm](plan/11_beyond-993.md) | the riders that cost no drive time, and the analysis plan of record |

**The block register**, which is the table a session actually runs from, is at
the head of [chapter 6](plan/06_sizing-and-spending-rules.md).

## This proposal can be run before it is run

Everything below is a prediction about a session that has not happened, and a
prediction is worth what it costs to check. The forward model that fits the
2025 data also GENERATES data, so the campaign specified here exists in
software before it exists on an optical table.

`examples/campaign_twin.py` is that digital twin. It builds the dataset this
proposal aims to collect, with the physics the chapters argue about actually
present: hyperfine amplitudes with cascade depletion, the saturation
companions, the AC-Stark ramp, the blackbody shift, the measured
signal-dependent noise law, and chapter 7's acquisition design including its
one-range quantisation and a session drift. Then it fits that dataset back and
reports what the campaign would establish.

Two runs, not one. The predicted light shift is injected in the first, and
NOTHING is injected in the second, because a design that detects an effect
that was put in has proved only half of what matters. The second run asks
whether it stays quiet when there is nothing to find. What no run of the twin
establishes is the physics itself: agreement means the record is internally
consistent, never that the model describes nature, and
[the digital twin](wiki/the-digital-twin.md) states that boundary in full.
The reader's own version of the loop, on a line of their choosing, is
[TUTORIAL.md](TUTORIAL.md).

What this changes for a reader of the proposal is the standing of its numbers.
A claim that some block improves a quantity by a factor is either supported by
a simulation or it is an expectation, and the chapters now say which. Where the
twin refuted a claim, the record says so: an early draft of the tutorial taught
that widening the scan span breaks the width degeneracy, and the twin measured
the correlation moving from -0.9177 to -0.9166 across a factor of five in span,
which is no movement at all. That correction is in
[HISTORY.md](HISTORY.md), and the surviving lever is in
[chapter 5](plan/05_width-collision-amplitude.md).

The 2026-08-19 design review of chapters 7 and 8 was run the same way: every
modulation depth, drive frequency and scan rate now in those chapters was
adjudicated by computing the design's information under the measured noise
law rather than by preference, five of the six candidate arguments failed
under computation before they could ship, and the corrections are each
recorded in [HISTORY.md](HISTORY.md). The general form of the discipline,
separating effects by parity under a knob before any fit is asked to, is
[reversal tests](wiki/reversal-tests.md), and the sharpest instance cost
nothing because the hyperfine g-factor's sign structure supplied the flip.

## Roles, so that four documents need not be reconciled by the reader

This file owns procedure: what would be set up, in what order, against which
go/no-go criteria. [`FUTURE_TRANSITIONS_titsapph.md`](FUTURE_TRANSITIONS_titsapph.md)
owns the cost, yield and failure-mode table across all candidate lines,
[`quantities/`](quantities/README.md) owns the per-quantity view of the same
material, where each page states the three levels of improvement available for
one quantity and the recipe for each, and
[`quantities/campaign.md`](quantities/campaign.md) compares candidate sessions.
[`BIG_PICTURE.md`](BIG_PICTURE.md) owns the map of what each measurement would
add, and [`APPARATUS.md`](APPARATUS.md) owns the hardware of record and its
provenance. Where a number in this file disagrees with the table or the map,
the table and the map win on numbers and this file wins on procedure. Where it
disagrees with `APPARATUS.md` the split is by kind rather than by number:
hardware facts are APPARATUS's and priorities are PLAN's. Projected precisions
are not restated here beyond the two headline figures above: they live in
[`results/projections.csv`](../results/projections.csv), which is computed from
the dataset's own measured precision and the session parameters these chapters
state.

**The schema, applied to every costed block.** Each block states, in this order
and in these words: **Needs** (its prerequisites, with hardware facts cited to
[`APPARATUS.md`](APPARATUS.md) rather than restated), **Shots** (what to
acquire, or the section that holds the list of record), **Go/no-go** (the
criterion that decides whether the block proceeds or aborts, frozen before
data), **Empty** (what it looks like if the block returns nothing), and
**Record** (what leaves the bench).

**What becomes reusable regardless of these sessions.** The analysis pipeline
ingests session data unchanged as long as the export keeps the 2025 shape, a
two-column InfiniiVision CSV of exactly 2000 rows, which `rb5s6s/ingest.py`
requires and rejects anything else against. On that path a session buys shots
and not software. Two blocks deliberately leave it: the native `.h5` export of
section 7g, which carries the per-scan timestamp and which no reader in this
package reads today, and any segmented or longer acquisition. Each of those
costs a loader, which is costed with the block that asks for it.

The adaptation seams for another line or species are named in
[`ADAPTING.md`](ADAPTING.md), and the record's data products and their
provenance tags in [`RESULTS.md`](RESULTS.md) and
[`results/README.md`](../results/README.md).

*Producers this document depends on:
[`scripts/run_ramp_geometry.py`](../scripts/run_ramp_geometry.py) for the
section 6 geometry tables,
[`scripts/run_resolving_power.py`](../scripts/run_resolving_power.py) for the
signal-against-noise verdicts, and
[`scripts/run_projections.py`](../scripts/run_projections.py), which reads
eleven session parameters from the sections named in its own header and writes
[`results/projections.csv`](../results/projections.csv). Changing a parameter
these chapters state moves that table, so the two are edited together. The
analysis plan of record, as executed, is in
[chapter 11](plan/11_beyond-993.md) and documented in
[`methods.md`](methods.md).*

## Section index

The chapters keep the section numbers this document has always used, so a
citation of the form `PLAN §7a` still names exactly what it named before. This
index maps each section to the chapter that now holds it.

**1.** Aim, in [chapter 1](plan/01_aim-and-failure-modes.md).
**2.** The objections a referee would raise, in [chapter 1](plan/01_aim-and-failure-modes.md).
**3.** Priorities if the budget shrinks, in [chapter 2](plan/02_priorities.md).
**4.** Configurations and optics protocol, in [chapter 3](plan/03_optics-protocol.md), whose sub-items are
**4.1.** the geometry of record,
**4.2.** the alignment protocol,
**4.3.** the collection arm and
**4.4.** the modulator.
**5.** The intensity axis, in [chapter 4](plan/04_intensity-and-light-shift.md).
**6.** The light-shift program, in [chapter 4](plan/04_intensity-and-light-shift.md), which now closes with a per-session waist requirement and the two analysis steps that run before the next session.
**7.** The width and collision program, in [chapter 5](plan/05_width-collision-amplitude.md), which now closes with the asymmetry budget and its reversal table, and whose blocks run
**7a.** through
**7j.**, including
**7d.** the matched-modulation ruler and
**7f.** the interleaved density ladder.
**8.** The amplitude program, in [chapter 5](plan/05_width-collision-amplitude.md), whose sub-items include
**8.1.** the cascade branch and
**8.3.** the saturation check.
**9.** Session sizing, in [chapter 6](plan/06_sizing-and-spending-rules.md).
**10.** Spending rules from the 2025 post-mortem, in [chapter 6](plan/06_sizing-and-spending-rules.md), whose rules run
**10.1.** through
**10.7.**, including
**10.3.** the interleaving rule and
**10.5.** the calibration-bracket rule.
**10a.** Acquisition settings, in [chapter 7](plan/07_acquisition-settings.md), whose card now closes with
**10a.1.** the modulation and rate menu, one setting per purpose.
**10b.** The acquisition record, in [chapter 8](plan/08_the-acquisition-record.md), whose sub-items include
**10b.4a.** the sub-multiple coincidence, where the pair separation becomes a measurement of the 6S hyperfine splitting,
**10b.4b.** the sweep-direction and mains-phase columns, which the comb clock is blocked on, and
**10b.4c.** the two-tone cascade for the gaps between the line clusters.
**10c.** The fixed cavity lock, in [chapter 9](plan/09_the-fixed-lock.md) and [chapter 10](plan/10_the-fixed-lock-instrument.md).
**11.** Wavemeter calibration shots, in [chapter 8](plan/08_the-acquisition-record.md).
**12.** Beyond 993 nm, in [chapter 11](plan/11_beyond-993.md).
