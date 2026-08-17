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

**The proposed measurement.** A vapour-cell session under the repaired cavity
lock, with an independent measurement of the laser width, a span wide enough
to fit the Doppler pedestal as a pedestal, two same-isotope frequency rulers
inside every sweep, and a randomised power ladder.

**What it would establish.** The two bounds above become measurements, the
frequency axis becomes calibratable, and the baseline becomes data rather than
a modelling choice.

**Where the detailed design lives.** In the eleven chapters below. Nothing
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
| 1 | [The aim and the risks](plan/01_aim-and-risks.md) | what the session is for, and the objections a referee would raise first |
| 2 | [Priorities if the budget shrinks](plan/02_priorities.md) | the order in which blocks would be cut |
| 3 | [Configurations and optics](plan/03_optics-protocol.md) | the optical layout and the alignment protocol |
| 4 | [Intensity and the light shift](plan/04_intensity-and-light-shift.md) | the intensity axis and the light-shift programme |
| 5 | [Width, collisions and amplitude](plan/05_width-collision-amplitude.md) | the width and collision programme, and the amplitude programme |
| 6 | [Session sizing and spending rules](plan/06_sizing-and-spending-rules.md) | the block register, session sizing, and the rules drawn from the 2025 post-mortem |
| 7 | [Acquisition settings](plan/07_acquisition-settings.md) | span, record length and sweep rate, and why the 2025 choices bounded what could be learned |
| 8 | [The acquisition record](plan/08_the-acquisition-record.md) | what every block must log, and the wavemeter shots |
| 9 | [The fixed lock, and what it buys](plan/09_the-fixed-lock.md) | identifiability, drift, the sweep, the scan axis, the modulator and the atomic rulers |
| 10 | [The instrument and the session](plan/10_the-fixed-lock-instrument.md) | the oscilloscopes, the pedestal, the day-one list, polarisation, and the comb as a statistical instrument |
| 11 | [Beyond 993 nm](plan/11_beyond-993.md) | the riders that cost no drive time, and the analysis plan of record |

**The block register**, which is the table a session actually runs from, is at
the head of [chapter 6](plan/06_sizing-and-spending-rules.md).

## Roles, so that four documents need not be reconciled by the reader

This file owns procedure: what would be set up, in what order, against which
go/no-go criteria. [`FUTURE_TRANSITIONS_titsapph.md`](FUTURE_TRANSITIONS_titsapph.md)
owns the cost, yield and risk table across all candidate lines,
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

**1.** Aim, in [chapter 1](plan/01_aim-and-risks.md).
**2.** Risks a referee would raise, in [chapter 1](plan/01_aim-and-risks.md).
**3.** Priorities if the budget shrinks, in [chapter 2](plan/02_priorities.md).
**4.** Configurations and optics protocol, in [chapter 3](plan/03_optics-protocol.md), whose sub-items are
**4.1.** the geometry of record,
**4.2.** the alignment protocol,
**4.3.** the collection arm and
**4.4.** the modulator.
**5.** The intensity axis, in [chapter 4](plan/04_intensity-and-light-shift.md).
**6.** The light-shift program, in [chapter 4](plan/04_intensity-and-light-shift.md), which now closes with a per-session waist requirement and the two analysis steps that run before the next session.
**7.** The width and collision program, in [chapter 5](plan/05_width-collision-amplitude.md), whose blocks run
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
**10a.** Acquisition settings, in [chapter 7](plan/07_acquisition-settings.md).
**10b.** The acquisition record, in [chapter 8](plan/08_the-acquisition-record.md).
**10c.** The fixed cavity lock, in [chapter 9](plan/09_the-fixed-lock.md) and [chapter 10](plan/10_the-fixed-lock-instrument.md).
**11.** Wavemeter calibration shots, in [chapter 8](plan/08_the-acquisition-record.md).
**12.** Beyond 993 nm, in [chapter 11](plan/11_beyond-993.md).
