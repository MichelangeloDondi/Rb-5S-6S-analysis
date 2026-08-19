# History: the one place a superseded number is licensed

**The question.** What did this repository once say, when did it change, and
what changed it?
**Takes.** Nothing. Every row here is dated and closed.
**Gives.** The lineage of every quantity that has moved, so that no other
document has to carry a value it no longer believes.
**Skip if.** You want the current numbers. They are in
[RESULTS.md](RESULTS.md) and the CSVs it names, and every other page in this
repository states only what is live today.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## Why this file exists

A repository that keeps its old numbers in place, marked or footnoted, reads
as careful and behaves as a trap: a wrong value in a working document is
indistinguishable from a live one to a reader who has just arrived, and on
2026-08-15 a superseded beam waist repeated across three forward-looking
documents outvoted the one page that was right, which produced a wrong edit
to the front page.

Deleting the history instead is not the answer either, because the reason a
number moved is often the most useful thing about it.

So the rule this file implements: **history is confined here, and every other
document states only what is live.** Where another page must refer to a
superseded value it links to this file rather than repeating the number. The
version-control history remains the complete record. This file is the curated
part a reader needs without running `git log`.

## What is in here, newest last

The entries run in the order they were made, so the file reads as a record
rather than as a ranking. This index exists because a reader arrives looking
for one quantity rather than for the sequence.

| entry | what moved | did a published number change |
|---|---|---|
| [The bound history](#the-bound-history) | the three quantities that have moved repeatedly, as one lineage table | yes, repeatedly |
| [The 60 µm working waist](#the-60-µm-working-waist-retired-2026-08-15) | a waist that three forward-looking documents kept alive after it was retired | yes |
| [2026-08-15](#the-2026-08-15-band-and-design-corrections) | the extrapolated-band reading and two design numbers | yes |
| [2026-08-17](#the-2026-08-17-corrections) | the joint-fit comparison, found to be between quantities that cannot be compared | yes |
| [2026-08-18](#the-2026-08-18-corrections) | the pooled-versus-campaign bound and its naming | yes |
| [The amplitude power law](#the-amplitude-power-law-was-described-rather-than-tested-2026-08-18) | a power law asserted from a description rather than from a test | yes |
| [The width concavity](#the-width-concavity-is-withdrawn-to-provisional-2026-08-18) | a curvature claim withdrawn to provisional | yes |
| [2026-08-19](#the-2026-08-19-corrections) | four record corrections, three of them found by widening a guard | yes |
| [The cascade line table](#the-cascade-line-table-was-wrong-on-three-of-four-lines-caught-same-day-2026-08-19) | which isotope and hyperfine level each line drives | no, and nothing was pushed |
| [The width degeneracy in a draft](#a-claim-about-the-width-degeneracy-was-wrong-in-a-tutorial-draft-2026-08-19) | a teaching claim about scan span, refuted before it shipped | no |
| [Six counts and one rounding](#six-counts-and-one-rounding-corrected-in-a-single-audited-sweep-2026-08-19) | published counts and a rounding, each now guarded | yes, none of them physics |
| [The pinning factor](#the-pinning-factor-was-one-monte-carlo-draw-and-the-largest-of-nine-2026-08-19) | a Monte-Carlo ratio quoted from one seed in four documents | yes, 3.4 to 3.18 plus or minus 0.20 |
| [A hardware argument](#a-hardware-argument-used-the-wrong-geometry-caught-same-day-2026-08-19) | a plan chapter justified an EOM purchase from the geometry its own proposal had removed | no, and nothing was pushed |
| [The tooth-height model](#the-tooth-height-model-was-a-limit-and-the-plan-priced-two-designs-outside-it-2026-08-19) | the Bessel weights are a zero-delay limit, and two same-day designs were priced outside it | no committed number, two plan tables same day |
| [A depth menu](#a-depth-menu-compared-per-sweep-what-the-budget-offers-at-the-margin-2026-08-19) | a per-sweep comparison answered a question the budget never poses | no, one local commit for under an hour |

The last three rows are here on purpose. A history that records only the
corrections a reader could otherwise discover teaches that the record is
audited from outside, and these three were caught by the record auditing
itself. The last of them was caught by running a committed producer with its
own default arguments, which is the cheapest audit available and had never
been run.

## The bound history

Three quantities have moved repeatedly, and their histories are collected here
so that a reader can tell which value is live. A row's value is as this file
recorded it on the row's date, which is why replaced numbers appear. A
history table is the one place they are licensed.

The live value of anything marked current is the one in
[RESULTS.md](RESULTS.md) and in the results tables it names. This file's copy is
not yet mechanically checked against those tables for the light-shift bound, for
its predicted coefficient, or for the polarizability bracket, so read those
three from RESULTS.md and treat the rows below as the lineage rather than as
the citation.

| quantity | value | date | construction | what moved it | standing |
|---|---|---|---|---|---|
| β_self, MHz per 10¹² cm⁻³ | 0.07–0.15 | before 2026-07-16 | between-block scatter with a hard-coded 2σ multiplier | the multiplier hid its own assumption about degrees of freedom | replaced |
| β_self | 0.2–0.4 | 2026-07-16 | the same scatter at the Student-t quantile *t*(0.95,1) = 6.31 on one residual degree of freedom | interval construction, not new data | replaced as the headline 2026-08-02 |
| β_self, per peak, 95% | < 0.21–0.44 | 2026-07-11 | model-independent raw widths across the three-point 70–110 °C cooling sweep | the 130 °C session was found to share the optical and cell configuration | retired 2026-08-02 |
| β_self, per peak, 95% | ≲0.03–0.05 | 2026-08-02 | four-point 70/90/110/130 °C construction, dof = 2, ×52.5 lever | the experimenter's firsthand apparatus authority on the configuration | **current headline** |
| β_self, joint hierarchical fit | 0.036 → 0.014 | 2026-07-12 | the same fit with and without the ×53 130 °C anchor | lengthening the lever, which is the lever test itself | a cross-check estimator, never the headline |
| AC-Stark S₀ at 225 mW | 3.1 MHz | before 2026-07-16 | Wald interval linearised at a fit that rails at κ = 0 | no coverage at a boundary | replaced, kept in `stark_sweep.csv` as a labelled diagnostic |
| AC-Stark S₀ at 225 mW | 0.63 MHz | 2026-07-16 | profile likelihood on the width channel, over-dispersion scaled | interval construction, not new data | the independent width-only bracket |
| AC-Stark S₀ at 225 mW | 0.14 MHz | 2026-08-01 | joint fit over every point of every profile across all three sessions, the campaign, the 4 July evening and the campaign morning | a construction change rather than a correction. Both bounds stand and the tighter is quoted | **superseded by later re-runs of the same construction, so this number is lineage and NOT the live bound.** Requote from RESULTS.md, never from this row |
| AC-Stark S₀ at 225 mW, predicted | 0.59 MHz | 2026-07-16 | the ramp prediction evaluated at the 50 µm measured waist | the measured waist moved to 64 µm on 2026-08-01 | a prediction at a retired input. Read RESULTS.md |
| Δα bracket | ~5800 → ~1200 a.u. | 2026-07-16 | the light-shift bound divided through by the predicted coefficient | the profile-likelihood rebuild above | tracks whichever bound is quoted |
| beam waist w₀ | 32 µm | nominal | the design value | the transit Monte Carlo's missing crossing-flux factor, fixed 2026-07-13 | excluded |
| beam waist w₀ | ~90 µm | before 2026-07-13 | a note that carried a factor-of-2 error | arithmetic | retracted |
| beam waist w₀ | ~50 µm | 2026-07-13 | the corrected transit Monte Carlo, validated against Lehmann's 41.2 kHz example | a direct measurement became available | replaced |
| beam waist w₀ | 64 µm | 2026-08-01 | Rajasree 2020's direct measurement on the same laser | nothing yet | **the adopted prior**, and still open |

Each row's argument, and what it taught, is in §6.

## The 60 µm working waist, retired 2026-08-15

| quantity | value | date | construction | what moved it | standing |
|---|---|---|---|---|---|
| proposed working waist, configuration L | 60 µm | 2026-08-02 | a round stand-in for the working beam, written before the waist was stated as measured | the beam is the 64 µm one [Rajasree 2020](lit/rajasree2020thesis.md) and [Nieddu 2019](lit/nieddu2019.md) recorded, and no telescope was ever specified to produce 60 | retired |
| two-waist intensity ratio | ×14 | 2026-08-02 | (60/16)² at the stand-in above | recomputed at the measured waist, (64/16)² | replaced by ×16 |
| $g_1$ sign-flip table, L column | computed at 60 µm | 2026-08-02 | the axial-moment integral at $z_R = 11$ mm | RECOMPUTED at 64 µm, $z_R = 13$ mm | replaced. The conclusion survives: the flip holds for every $M$ from 0.5 to 6, and the largest change is the $M = 0.5$ row, $+0.044 \to +0.142$, which does not approach zero |

Why this one is worth a section rather than a row. The 60 µm figure survived
the re-pin in three forward-looking documents while the measured value was
recorded in a fourth, and on 2026-08-15 a consistency sweep counted the three
against the one and "corrected" the page that was right. Corroboration between
documents is not independent evidence when they share an ancestor. The rule
this file now implements exists because of it.

## The 2026-08-15 band and design corrections

Six numbers were published inside the private record on 2026-08-15 and
corrected the same day, four of them by an adversarial pass and two by the
author anticipating one. None of them ever reached a committed result, and they
are here because this file is the only place a superseded number is licensed to
appear.

| quantity | value | date | construction | what moved it | standing |
|---|---|---|---|---|---|
| band-holdout replication | 7 of 7 conditions low, p = 0.0078 | 2026-08-15 | the calibration-sound subset of a sixteen-condition cohort | two of the seven were the pilot's own traces regrouped by peak, and the numeric soundness threshold was never in the frozen script | replaced by 11 of 14 fresh conditions, p = 0.029 |
| infinite-window collisional width | γ(∞) = 0.246 MHz | 2026-08-15 | a 1/w extrapolation of the window scan on peak 4154 | the frozen spec required a form SPREAD, and 1/w² gives 0.446 against an exponential approach at 0.504, and 4154 is the lowest of the four peaks | RETRACTED. Only the direction survives: every physical form on every peak lands below the committed value |
| wide-scan span | 800 MHz, ±400 | 2026-08-15 | one Gaussian σ of the Doppler pedestal, chosen so the pedestal visibly falls | the free per-trace background is a degeneracy, not a haircut: the retained SNR is √(1 − ⟨g⟩²/⟨g²⟩), which is 0.140 at 1σ of reach and not the 0.7 assumed | replaced by 2400 MHz, ±1200, at 3σ of reach |
| wide-scan record length | 3000 points | 2026-08-15 | 20 points across the line at the 800 MHz span | the span moved | replaced by 10000 points |
| pedestal detectability | ~29σ per trace | 2026-08-15 | the naive count with the 0.7 degeneracy factor and τ = 2.0 | both inputs were wrong, since the degeneracy factor is 0.645 at the new reach and the record's τ_int median is 3.81 | replaced by ~31σ per trace, 13σ at the record's worst τ |
| residual-Doppler retro tilt | 1.6 mrad | 2026-08-15 | the co-propagating pedestal width scaled by θ | double-counting: the pedestal already carries k_eff = 2k, while two beams at angle θ carry k·θ, so the coefficient is 471 MHz/rad and not 942 | replaced by 3.2 to 3.5 mrad |
| in-campaign wavemeter records | one | 2026-08-16 | the register held a single 17:03 photograph and the drift synthesis was written around it | a second in-campaign record, 2025-07-18 02:37, was already among photographs the register had never taken in | replaced by two, and the section count by ten |
| wide-scan shape requirement | 20 points across the line FWHM | 2026-08-16 | stated in the design script before any simulation tested it | the B5 and B6 runs measured the width recovery at the committed noise law and about 22 points across the line FAILS a frozen recovery criterion | replaced by 90, which is what the 40000-point record of PLAN section 10a delivers |
| pedestal detectability | ~31σ per trace | 2026-08-16 | the same calculation at a 10000-point record | the record length rose with the shape requirement above, and the significance follows it | replaced by ~61σ per trace, 27σ at the record's worst τ |

Two further corrections were to SCOPE rather than to value, and no number
moved. The fitted `sigma_laser` was described as "three to eight times what
this bench's own in-campaign measurements allow", where only one of the eight
wavemeter records falls inside the campaign and that one supports three to
four. And the window scan and the ridge holdout were called "two instruments
that share no machinery", where they share the profile, the noise law with its
τ convention, and the same linear nuisance solve, differing only in estimator.

What this section is for. Five of the six rows moved in the direction that had
made the result look stronger, which is a measurement of the review rather than
six coincidences, and the protocol's section 6 now requires the direction of a
refutation tally to be recorded alongside its count.

## The 2026-08-17 corrections

Four values were retired in one day, and each was retired by a measurement
rather than by an argument.

| quantity | value | date | construction | what moved it | standing |
|---|---|---|---|---|---|
| the saturation companion's factor on the joint light-shift bound | 2.21 | 2026-08-09 | inferred from the width-only channel's factor, never run on the joint fit | the joint refit RAN, so the factor is measured rather than inferred | replaced by the measured value. Read `RESULTS.md` |
| `kappa_ub95_camponly` read as a bound on the campaign alone | 0.674 MHz per W | 2026-08-01 | the campaign's chi-square along the POOLED profile, whose nuisances were fitted on all three sessions | a genuine campaign-alone refit was run and disagreed, so the row was never the campaign-alone answer | the row keeps its value and loses that reading. It is a subset column of the pooled profile |
| the subset spread of the light-shift bound across constructions | a factor of 2.4 | 2026-08-17 | the pooled bound against the campaign-rows column, treating the latter as a campaign-alone bound | the campaign-rows column is not a campaign-alone bound, so it cannot be one end of the comparison | withdrawn. The committed rows support a leave-one-peak-out factor of 1.42 and nothing wider |
| the excess outside the fit window | no candidate mechanism | 2026-08-16 | a per-trace baseline ladder that swung the offset by more than the offset | one joint fit over 79 traces with per-trace free polynomials, plus a regression of the amplitude on two competing predictors | replaced. The candidate is the lineshape model, and the limitation itself stands |

**A scar about naming rather than about a value.** The second and third rows are
one defect seen twice. A results row whose NAME implies a provenance its
COMPUTATION does not have will be read as what its name says, including by the
people who wrote it, and the arithmetic done on that reading enters documents
downstream before anyone checks. The rule the record now applies is that a row
identifies its quantity, its construction and its source, and that a name
implying any of the three without carrying it is a defect rather than shorthand.
The same rule was extended to module constants the same day, after one was found
named for a placeholder while holding a value computed from a measurement.

**The sweep-linearity claim, corrected 2026-08-17 late.** The ruler figure and
its caption said the local sweep rate never departs from the block rate by more
than the bound in any well-sampled window, with the thinly-sampled edge windows
excluded as carrying uncertainties larger than the bound. Checked against
`results/ruler_nlmap.csv`, that justification was true of two of the five
excluded windows, and the two leading-edge windows are PRECISE departures,
minus 1.75 plus or minus 0.40 per cent and plus 0.73 plus or minus 0.18 per
cent, which are 4.4 and 4.0 standard deviations from flat. The claim the record
now makes is stronger and different: the conversion from scan time to frequency
is linear to 0.25 per cent across the interior and is NOT linear at the leading
edge, where the ramp is turning, and the analysis windows do not reach into it.
The figure draws the sample count and marks the departing windows rather than
hiding them behind a reason that did not apply.

**One session date was inconsistent rather than wrong.** The campaign-morning
session of 17 July 2025 was named 2025-07-18 in the joint fit's docstring, in
the same sentence that named its `20250717` directory. `GLOSSARY.md` and
`DATA.md` both say 17 July and are the canonical naming.

## The 2026-08-18 corrections

**The width-pinning comparison had no producer, and its numbers did not
survive getting one.** Four documents quoted the same pair, a collisional
width recovered with a scatter of 0.0396 MHz with both widths free against
0.0235 MHz with the laser width known, a factor of 1.7, attributed to a
simulation at the measured noise law. No committed script produced those
numbers, and the construction behind them was never recorded.
`scripts/run_width_pinning.py` now exists as the committed producer, states
its construction in its docstring, and measures 0.0073 against 0.0021 MHz, a
factor of 3.4, on a bright synthetic condition. The retired pair is not known
to be wrong, it is unreproducible, which for this record is the same
disqualification. All four sites now quote the producer's numbers with the
construction named, and the qualitative conclusion, that an independent
laser-width measurement is worth more than any fitting improvement, is
unchanged and strengthened.

**Two plan chapters quoted a superseded lever collapse.** The hierarchical
beta_self sensitivity was stated as 0.036 to 0.014 in `plan/05` and
`plan/06`, unqualified, where the record's current values are 0.0534 to
0.0198 for 85Rb and 0.0219 for 87Rb. The old pair remains in this file's
retired-values table, which is where it belongs.

## The amplitude power law was described rather than tested, 2026-08-18

The record stated that the two-photon amplitude scales as the square of the
power, supported by log-log slopes of 1.83 to 2.12 across the four hyperfine
lines, and flagged only the low line as unresolved. The four slopes carried
errors throughout and were never compared with 2. Tested, under a block
bootstrap that respects this sweep's power-time collinearity, three of the four
exclude 2, one from below and two from above, and the fourth becomes consistent
with 2 only once the between-block term replaces the within-cell error. No
committed number changes and no bound moves, since no published result rests on
the amplitude's exponent. What changes is the claim: the amplitude follows the
two-photon rate law approximately and not exactly, the departures are per-peak
and of both signs, and no inventoried mechanism predicts that.

The general defect is worth more than this instance. A fitted parameter was
quoted with its uncertainty and then read qualitatively as a band, and the
arithmetic that would have tested it against its own null was never done.
`docs/notes/amplitude_departure_from_p2.md` carries the construction.

**The same day found the archive's own control for it.** Two further power
ladders exist outside the frozen record, and the 2025-07-04 rehearsal ran its
ladders in ALTERNATING DIRECTIONS inside one session, which varies acquisition
order while holding scope, gain, cell, alignment, epoch and temperature fixed.
Against that control the amplitude departure is invariant, so it is not an
artefact of the campaign's power-time collinearity, and its ordering across
lines follows brightness rather than branching.

## The width concavity is withdrawn to provisional, 2026-08-18

A concave curvature of the linewidth against power, apex near 120 mW, has been
carried since 2026-08-17 as a measured diagnostic and it motivated a channel
sweep, a component-resolved decomposition and an EOM thermal-lens hypothesis.
Tested with the same care as the amplitude channel, it does not survive. It
reaches 4.8 standard deviations only on within-cell errors, falls to 1.4 under
the between-block treatment this record's own width channel uses, is not
confirmed by the pilot's independent non-monotone ladder at 1.2, and in the
rehearsal appears on the descending ladder while both ascending ladders show
none, which is an order-dependence signature. Section C3a's original statement,
that the width's power variation is block scatter rather than power
broadening, is the accurate reading and it stands.

No committed number changes, because no published bound rested on the
concavity. What changes is its standing: it is provisional, the thermal-lens
hypothesis is demoted to a mechanism for an effect whose existence is not
established, and an interleaved power ladder is what would settle it.

## The 2026-08-19 corrections

Four corrections to the record, listed first, and one to working memory that
never reached a file, listed second, since a reader counting the entries below
is owed the distinction. The first two run in the record's favour and are
recorded here for that reason rather than despite it.

**The multi-start pointwise-minimum bound was an artefact of a display
normalisation, and the headline light-shift bound is safer than the record
had claimed.** `docs/notes/campaign_only_stark_profile.md` reported a
pointwise-minimum bound near 1.92 MHz per W from the pinned multi-start run
and read it as evidence that the pooled likelihood surface threatened the
committed profile. The curves in that note's CSV are stored OWN-NORMALISED,
each start against its own best point, and a minimum taken across them
corresponds to no single fit. The instrument that produced them writes
ABSOLUTE chi-square and its output survives beside it. Anchored to the
committed production minimum of 186370.92, the best independent start at each
coefficient value sits above it by 7.54, 4.84, 4.66, 5.32, 7.78 and 26.29,
every one past the 2.706 threshold, so the independent-start ensemble never
enters the confidence region. The production warm chain is pointwise-dominant
everywhere tested. The superseded reading is retired here, and the note
carries the corrected one.

**The correction that never reached a file: the 2.35 saturation companion
factor never existed.** A factor of 2.35 was
carried in working notes as a measured saturation tightening. There is no
such number: the committed factors are 2.8 for the width-only construction
and 2.21 for the joint one, both predicted before the run and both recorded
in `docs/notes/two_photon_saturation_companion.md`. The only 2.35-like values
in the repository are the FWHM-to-sigma constant 2.3548 and a Student-t
critical value in plan chapter 5.

**`results/linefit_conditions.csv` was stale, and it did not travel alone.**
Regenerated under the environment of record after four commits changed the
producer's numerics, including a selectable transit kernel and an isotope
correction to the transit width. Ten columns moved across all 32 rows, the
largest being `sigma_laser` at 21 per cent, which is expected when the
transit kernel changes because transit, laser width and collisional width are
the three degenerate components. Two committed files READ that file as input,
`sigma_laser_sharing.csv` and `resolving_power.csv`, and both were
regenerated in the same commit. The file is PRELIM and is cited in no claim.

**`results/wing_check.csv` was stale without consequence.** Regenerated under
the environment of record. The producer is deterministic there, two runs
returning byte-identical files. The value RESULTS.md quotes, the 130 C
asymmetry of -0.0007 +/- 0.0013, is unchanged to every digit, and the
assertion that no temperature exceeds 0.7 sigma survives with its worst case
improving from 0.68 to 0.67.

**`results/projections.csv` carried a stale vocabulary sweep.** Fifty-five
string cells still read "archive" where the producer says "record". One numeric cell moved in its eighth significant figure. Nothing
else changed.

### What made these four visible on the same day

Not a hunt for them. The freshness guard's coverage was widened on 2026-08-19
from 27 of 46 committed CSVs to 42, with the remaining four registered as
deliberately uncovered and their reasons stated. **Nineteen files, 41 per cent
of the record, had been compared against nothing in either mode**, and three of
the four corrections above are in files that widening reached. The guard had
been returning green on the 59 per cent it could see, which reads identically
to a green on the whole.

The fourth correction, the multi-start reading, came from a different
direction: the committed diagnostic stored its curves in a form that could not
be combined, and the producer's raw output, which could, was still on disk one
directory away.

### A number that did NOT move, recorded because it was expected to

`rb5s6s/stark.py` carried its own literal copies of the four cascade branching
values and of the natural width, while their sources of truth lived elsewhere.
Both now import from those sources. The natural width is byte-identical, three
of the four branchings are unchanged, and one gains precision, 0.372478 to
0.372478177, a relative move of 5 in 10 million. No committed result moves on
this, and it is recorded here so that a future reader who finds the old
literals in the history does not mistake the collapse for a correction.


## The cascade line table was wrong on three of four lines, caught same day, 2026-08-19

`rb5s6s/cascade.py` shipped with a `DRIVEN_F` table assigning 993.4154 and
993.4207 to the wrong isotope and 993.4192 to the wrong hyperfine level. The
branching FRACTIONS were never wrong, because they are keyed by wavelength
directly from the committed manifold output, so no number moved. What was
wrong was the labelling of which isotope and which ground F each line drives,
in the module and in the wiki page's table, for the hours between the
module's commit and this correction. Nothing was pushed in that window.

How it was caught is the useful part. The campaign digital twin, being built
the same evening, reads `constants.PEAKS` for the four lines' positions, and
the two tables disagreed on contact. The module's own test did not catch it
because the test asserted the module's table back at itself, the
written-from-the-same-misunderstanding failure this record has met before.
The test now asserts against `constants.PEAKS`, the repository's independent
line table, and the twin gets credit as the first consumer strict enough to
find the defect.

## A claim about the width degeneracy was wrong in a tutorial draft, 2026-08-19

An unreleased draft of `docs/TUTORIAL.md` taught that widening the scan span
breaks the degeneracy between the laser width and the collisional width. It
does not, and the same digital twin refuted it before the page shipped.

Measured on synthetic data whose truth is known: the correlation between the
two widths runs -0.9177 at a 60 MHz span and -0.9166 at 300 MHz, and ten
times the traces reaches only -0.881. Both uncertainties shrink with more
data while the correlation does not move, because the degeneracy belongs to
the LINESHAPE, a Lorentzian core convolved with a Gaussian, rather than to
the sample size.

Nothing public ever carried the wrong claim, so this entry records a
correction that did not reach a reader. It appears here because the
replacement is a result rather than a repair: pinning one side of a
correlated pair reduces the other's variance to (1 - rho^2), so an
independent laser-width measurement is worth 1/sqrt(1 - rho^2) on the
collisional width, which no achievable increase in scan span or repeat count
approaches. That factor is now `rb5s6s.forecast.external_constraint_gain`,
and it is guarded by a test written specifically because the earlier draft
asserted the opposite.

## A depth menu compared per sweep what the budget offers at the margin, 2026-08-19

Plan chapter 7's modulation menu shipped with the sentence that teeth are
never free statistics, from a comparison of an RF-on sweep against an RF-off
sweep for the same slot. The budget holds no such choice: the ruler brackets
are mandatory calibration, recorded regardless, and the M25 joint fit already
ingests them, with its no-rulers arm as the robustness check. Against the
budget's real alternative their width information is free and additive, a
factor 1.26 to 1.33 per block at 2025-like proportions, propagating linearly
to the collisional coefficient. The menu now splits the depth by the trace's
job, deep brackets because ruler information is lever-weighted and climbs
with depth, shallow in-block interleaves because width information falls
with it, and the per-sweep sentence survives only where it applied, dim-rung
science sweeps. The wrong frame lived in one local commit for under an hour.

## The tooth-height model was a limit, and the plan priced two designs outside it, 2026-08-19

Every tooth weight this record had ever written was $J_s(2\beta)^2$, treated
as a property of the modulation depth alone. It is the ZERO-DELAY limit of an
interference: a tooth is fed by every sideband pair summing to the same
offset, one photon of each pair arrives on the retro beam late by the
round-trip to the mirror, and the pathway sum collapses to a single tone at
effective depth $2\beta\cos(\pi f\tau)$, cell-averaged. The experimenter
supplied the physics in its sharpest form, that the carrier carries every
crossover pair on top of the pristine Bessel value, and the closed form
above reproduces the explicit pathway sum to ten digits.

At the 12.5 MHz drive of the 2025 campaign the delay phase is 0.05 rad and
the usable teeth correct by at most 0.2 per cent, so NOTHING COMMITTED
MOVES, and the ruler machinery is untouched. The two designs the plan
committed EARLIER THE SAME EVENING were priced in the wrong limit: the
sub-GHz coincidence tooth is 0.003 on the common path rather than 0.16, a
factor of fifty, and the cascade's main-line survival at 579.6 MHz is 0.62
rather than 0.076, which inverts its operating mode from
calibration-sweeps-only to gentle enough for science sweeps. Both sections
now carry cell-averaged numbers, the coincidence block moves its modulator
between the cell and the retro mirror, where single-arm pathways cannot
interfere and the zero-delay weights are exact at any drive, and
`rb5s6s.forecast.comb_tooth_weights` computes all three cases under test.

## A hardware argument used the wrong geometry, caught same day, 2026-08-19

Plan chapter 8 gained a section recommending a sub-GHz EOM drive, and its
stated justification was that a tooth-to-pair coincidence removes a
185-tooth-spacing sweep-rate extrapolation between the two lines of an
isotope pair. That extrapolation belongs to the 2025 narrow-span geometry,
where no trace held both lines of a pair. In the wide-span design the same
chapter proposes, the existing 12.5 MHz comb lays about 192 teeth between the
pairs and the extrapolation is already gone, so the argument recommended
buying hardware to fix a problem the proposal had already fixed without it.

The section survives with a different and honest justification. The
coincidence is an optional metrology block rather than axis hardware: the
ground splittings are clock-grade, so the pair separation is the 6S hyperfine
splitting, and reading the coincidence doublet at the measured per-crossing
centre precision reaches 0.3 kHz in about one hundred crossings against
constants known to 2 kHz. The chapter now also states the division of labour
the wrong version obscured, the pairs as the absolute anchor and the comb as
the dense interpolator and clock, and folds the 27 MHz recommendation and the
coincidence into one hardware conclusion, since neither runs on the resonant
tank and one broadband modulator serves both.

**The correction itself then over-corrected, caught the same evening.** The
replacement text claimed the wide span retires the extrapolation because 192
teeth join the pairs. That number counts tooth POSITIONS. A tooth needs a
position and a resonance, and its height carries the Bessel weight, so the
usable comb is four clusters of about five teeth with gaps up to 1155 MHz
carrying no marks, a figure this record had itself computed the same day. The
section now prices the interpolation across those gaps honestly and carries
the two-tone cascade design that converts it into a measurement on
interleaved calibration sweeps. Three versions of one section in one day,
each error smaller: a wrong geometry, then a wrong count inside the right
geometry, then the count with its construction attached.

Nothing was pushed. The wrong argument lived in one local commit for a day.

## Six counts and one rounding, corrected in a single audited sweep, 2026-08-19

No physics number moved, and the entries are recorded because each was a
PUBLISHED figure a reader could have quoted. The light-shift width-only bound
was printed as 0.64 MHz in two documents where the committed cell reads
0.632, which rounds to 0.63 and is written so everywhere else. The wiki index
claimed nineteen pages carry a scar section where fourteen did. The runner's
own header claimed 25 analysis stages against the 27 in its loop three lines
below. The methods summary stopped its module range one module short of its
own table, the glossary four short, and the reproduction guide counted
twelve CSVs as twelve scripts where eleven scripts wrote them. Each fix
landed with a guard where none had existed, or a widened one where the guard
knew only one spelling of what it checked: the module-range guard now reads
every separator this tree has ever used for a range, and the wiki's two
spelled-out counts are compared against the pages on every run.

## The pinning factor was one Monte-Carlo draw, and the largest of nine, 2026-08-19

Four documents quoted a factor of 3.4 for what an independent laser-width
measurement buys the collisional width, from `scripts/run_width_pinning.py`.
The producer's own default seed does not return it. Run at nine seeds of the
same construction, 200 trials each, the ratio comes out 3.18 with a standard
deviation of 0.20 and a range of 2.86 to 3.48, and the quoted 3.4 is the
largest of the nine.

The number was not wrong, it was quoted to two significant figures with no
uncertainty, which for a ratio of two Monte-Carlo standard deviations is the
same defect as the unreproducible pair this producer was written to replace
one day earlier. All four sites now carry 3.18 plus or minus 0.20, and the
producer's DEFAULT is now an ensemble of nine seeds rather than one, so the
quotable number and the reproducible number are the same number.

**The arithmetic behind the factor is what makes it checkable at all.**
Conditioning on one member of a correlated pair leaves the other with
sqrt(1 - rho^2) of its uncertainty, so the purchase is 1/sqrt(1 - rho^2) and
depends on the correlation alone. That is 2.29 at this record's median
correlation of -0.90 and 2.97 at the pinning condition's own -0.9417, against
the 3.18 measured there, a 7 per cent gap carried by twenty per-trace nuisance
parameters, a boundary at zero collisional width and the non-Gaussian tail of
a nonlinear fit. The correlation is identical to four decimals in all nine
seeds, which is what the arithmetic predicts, since a correlation is a
property of the design rather than of the noise draw. So the apparent
disagreement between the 2.5 this record briefly quoted from the twin and the
3.4 it quoted from the simulation was never two results. It was one formula
evaluated at three different correlations, and
[identifiability](wiki/identifiability.md) now carries all three in one table.