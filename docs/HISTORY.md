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
| [The identifiability diagnostics](#the-identifiability-diagnostics-moved-under-the-arithmetic-environment-2026-08-22) | the ridge slope, its covariance prediction, the condition number and the valley-floor RMS all move on this floor | not yet, the migration that would land them is held |
| [Three pages on the kernel](#three-pages-described-the-kernel-systematic-as-unquantified-or-still-to-be-done-2026-08-22) | the narrative layer called a question open that the results layer had answered | no number, three pages of prose |
| [A results path](#a-results-path-was-renamed-away-from-a-collision-2026-08-22) | `lever_table.csv` became `orthogonal_levers.csv` to clear a name collision | no, the path only |
| [The class-adequacy caveat](#the-class-adequacy-caveat-tested-twice-in-one-day-2026-08-22) | the atlas ran, voided, was diagnosed and re-ran, and the fourth-level statement moved with it | no number, three surfaces of prose |

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
## A selection rule that was true of one atom and silent about two, 2026-08-20

The record closed the magnetic channel with a single-atom argument: a $J=1/2$
state has two magnetic sublevels, a rank-two operator has no reduced matrix
element between two of them, and the same-handedness content of the drive is
refused. The argument is correct. It was published on the public wiki without
saying that it was a statement about ONE atom.

A pair of ground-state atoms has four sublevel products and can accept the two
units by taking one each, so that premise does not hold for a pair and the
closure lifts. What replaced it is three things, and only the third bounds the
size. Energy conservation forbids a new line, with the nearest alternative
pair configuration 23.3 THz off. The exchange and aligned topologies have
complementary zeros, so no field arrangement closes the channel as a whole.
Only the dipole-dipole transfer amplitude over its energy denominator sets how
big it is.

**The replacement argument then had a scope defect of its own.** Its first
version summed only the $5P_{1/2}$ intermediate leg. $5P_{3/2}$ is E1 allowed
at every vertex and carries the larger reduced elements, so including it
multiplies the amplitude by 2.82 and the rate by 7.97. The published figure
moved from $1.5\times10^{-10}$ to $1.3\times10^{-9}$, which changed the
finding rather than a digit: the pair route does not match the single-atom
hyperfine route, it is about eight times larger. A scope error is not a
beginner's error made once.

## Two claims of headroom that were never sourced, 2026-08-20

The two-atom module said the channel sat "ten orders" below anything the
record could resolve in one paragraph and "nine orders" in another. Neither
number had a producer and no constant anywhere in the tree defined what the
record can resolve. Measured against the tightest bound the record does carry
on an out-of-window feature, `f_wing_red_mean` at 0.0009 of peak in
`wing_check.csv`, the margin is SIX orders. Both earlier figures were too
generous, which is the wrong direction for a claim that something is
negligible.

## A systematic sized against a bound where a prediction belonged, 2026-08-20

`run_polarisation_bound.py` hard-coded the differential scalar shift at
0.258 MHz with a comment calling it "the committed differential scalar shift".
It is not a shift. It is the 95 per cent upper BOUND, and it sits BELOW the
calibrated prediction of 0.348 MHz. Every number derived from it therefore
understated itself by a third: the vector light shift's sublevel spread was
published as 4.5 kHz where 6.0 kHz belongs.

Correcting the prose reproduced the fault one level down. The replacement
sentence cited 0.348 and did its arithmetic with 0.35 from a different file,
giving 6.1 kHz where 6.0 is right. Both values now come from
`stark_joint.csv` at run time, both spreads are emitted with the shift each
used named in its own cell, and a canonical registry entry ties the two
documents and the CSV together.

## The case page reintroduced a defect it describes as fixed, 2026-08-20

The ten-minute case page's intervention table gave the purchase from an
independent laser-width measurement as running "2.3 at the record's median
$\rho = -0.90$ to 3.5 at the pinning simulation's own $-0.94$". The
arithmetic $1/\sqrt{1-\rho^2}$ at that condition's own $-0.9417$ is 2.97,
which both [chapter 7](big_picture/07_limitations-and-identifiability.md) and
[identifiability](wiki/identifiability.md) already stated, and the nine-seed
simulated value is $3.18 \pm 0.20$. The 3.5 matches neither. It is closest to
3.45, the largest of those nine draws, which is the exact defect the entry
above this one records as closed and which the page's own next paragraph
presents as fixed.

Found by three independent readers sent at the page cold, two of whom
identified it separately. All three correlations now carry the construction
each belongs to.

## A switch wired through four modules and never thrown, 2026-08-20

`laser_kind` selects a Gaussian or a Lorentzian for the laser's own
contribution to the line. It is a parameter of `composite_profile`,
`model_profile`, `fit_condition` and `beta.py`, it is documented in three
docstrings, and it had never been called with anything but its default.

Turning it moved the headline collisional coefficient by 45 to 67 per cent,
nine to eighteen sigma on its quoted statistical error. A per-condition figure
of 45 per cent was reported the same night and WITHDRAWN the next morning: at
fixed condition a Lorentzian laser width and a collisional width enter only
through their sum, so that number described where an optimiser stopped on a
flat direction rather than a property of the data. The headline survives
because its estimator varies density, which is the only thing that separates
them.

An audit of every model-form switch in the tree found this was the only one
never exercised. `transit_kind`, `sigma_sharing`, `topology` and `scaling` are
all compared somewhere. The repository knew the technique and had applied it
everywhere but here.

## A producer whose default did not reproduce its own output, 2026-08-20

`run_skew_scaling.py` defaulted to 400 simulation draws while the file it had
committed was made at 1500, the number its own docstring calls stable across
five seeds. Rule 19.75 says the quotable number is the default invocation's
number. The default is now 1500 and the file is regenerated from it, which
moves the exclusion against the fixed-amplitude hypothesis from $p = 0.010$ to
$p = 0.011$ and the recovered scatter under the shot-noise hypothesis, a
ceiling-test diagnostic, from 0.301 to 0.532. The conclusion is unchanged and
the shot-noise p-value is unchanged at 0.083. Three pages and the generated
ledger carried the old p-value and now carry the new one, tied to the
producer's cell by a registry entry.

## An exact degeneracy that the code broke, and the number that had no referent, 2026-08-20

**What moved.** The per-condition figure reported the previous evening, a
median 45 per cent shift in the collisional width when the laser kernel is
changed from Gaussian to Lorentzian, is WITHDRAWN. It is not replaced by a
corrected value, because the quantity it reported is not identified. The
headline figure beside it, 45 to 67 per cent on `beta_self`, STANDS and is now
reproduced by a committed producer: `run_kernel_headline.py` gives 45.0, 58.0,
63.2 and 66.6 per cent across the four peaks, nine to eighteen sigma on the
statistical error quoted beside them.

**Why the per-condition number had no referent.** Lorentzians add. At a fixed
condition the model therefore depends on the collisional width and a
Lorentzian laser width only through their SUM, so the split between them
carries no information at all. The data say the same thing: between two
implementations the sum holds to 0.02 per cent while each part moves by 16 to
20 per cent, at identical reduced chi-square. The published number described
where an optimiser stopped along a flat direction.

**What positioned the optimiser, which is the part worth keeping.** The code
realised the exact identity by CONVOLVING two Lorentzians on a finite grid.
Finite grids truncate Lorentzian tails. The truncation depends on the grid
span, and the span was computed from the two widths separately. So the
implementation made the profile depend on the split by up to 3.7e-3 of peak
where the mathematics forbids any dependence at all, a numerically
manufactured separability pointing along exactly the direction the next
measurement was to be made along. Measured against the archive's own noise
over the ~1e4 points of one condition, that artefact carries up to seventy
sigma of matched-filter leverage. It was not small in the only units that
matter.

**The fix and its blast radius.** A Lorentzian laser width is now ADDED into
the homogeneous width at all three assembly sites rather than convolved:
exact by construction, and one convolution cheaper. The Gaussian path, which
every committed number in this repository rides, is bit-identical across 96
parameter combinations on identical grids, verified against the previous
commit's own modules rather than argued. No committed number outside
`laser_kernel.csv` moves. `tests/test_laser_kind_degeneracy.py` pins the
invariance bit-identically, with the Gaussian branch as the should-fail
control, and the guard was ceiling-tested against the pre-fix code.

**What survived, and why.** The headline estimator varies DENSITY, which is
the only thing that separates a collisional width from a laser one, so its
answer barely moved. The correlation between `beta_self` and the shared laser
width shows the price: -0.82 to -0.89 under the Gaussian kernel, -0.91 to
-0.98 under the Lorentzian. The density ladder converts an exact degeneracy
into a strong but finite one, which is the whole reason the headline figure is
a measurement and the per-condition one never was.

**Also withdrawn from the public surfaces.** The sign-test p-value quoted for
the Gaussian giving the lower chi-square at 32 conditions of 32. The tally is
unchanged by the fix and is kept as implementation evidence, but the
Lorentzian arm has one fewer EFFECTIVE shape parameter, since it can set the
total homogeneous width and nothing else. A comparison in which the more
flexible model wins everywhere is close to determined before any data are
taken, and a significance computed against a null that both hypotheses nearly
guarantee is not a significance.

## The identifiability diagnostics moved under the arithmetic environment, 2026-08-22

Regenerating `run_identifiability` on this floor moves numbers that
[the statistics chapter](methods/06_the_statistics.md) quotes. The measured
ridge slope goes from **0.073 to 0.086** and the covariance prediction from
**0.080 to 0.110**, so the comparison reads 0.086 against 0.110 rather than
0.073 against 0.080. The neighbourhood moves with them: the condition number
falls from **389.7 to 345.1** and the valley-floor RMS from **0.0032 to
0.0020**. The best-constrained sigma does not move.

Three things were established before anything was concluded. Nondeterminism was
ruled out, two runs being bit-identical. The cause is the arithmetic
environment and not the analysis change made the same week, since pre-change
code run under the same numpy gives the new values too, which exonerates that
change. And the relative statement the chapter rests on survives, because the
prediction still exceeds the measurement.

**A claim in that chapter did not survive and was corrected.** It had said the
ridge slope reproduces unchanged. It does not. It moves by 18 per cent, and the
chapter now says so.

**The migration that would land these values was HELD when this entry was
written, and it landed on 2026-08-23.** Its own preregistered backstop had
fired, because a moved quantity changed the interpretation of a published
claim. The hold was not discharged by correcting that claim, since discharging
a hold by editing its trigger is the move this record's discipline exists to
catch, and this same passage had already been refused once on those grounds. It
was discharged by the owner authorising the migration, and the values above are
now the committed ones. See
[the migration entry](#the-environment-migration-landed-2026-08-23), which also
records that this entry's four predictions all held and that ten further rows
moved which it did not name.

## Three pages described the kernel systematic as unquantified or still to be done, 2026-08-22

[Chapter 7](big_picture/07_limitations-and-identifiability.md) called the laser
kernel an unquantified model systematic. [BIG_PICTURE.md](BIG_PICTURE.md) and
[PLAN.md](PLAN.md) each named the remaining work, a fitted
Lorentzian-equivalent width inside the containing model, and neither recorded
that it had been done.

It had. Freeing that width at each peak gives a component present everywhere by
a nested likelihood ratio of 176 to 961, at 0.315 to 0.449 MHz per peak, and
sized against the statistical error on a matched footing it is 3.24 times
larger. So the systematic is quantified within the tested class, and the three
pages now say that instead.

No published number changed. What changed is that a reader of the narrative
layer was being told a question was open that the results layer had answered
three days earlier, which is the same failure mode as a superseded number and
is why it is recorded here.

**Two qualifications travel with the correction**, because the quantification
settles less than it appears to. Whether the four peaks share one value is
neither rejected nor established at $p = 0.097$. And attributing the component
to the laser is a separate claim that no measurement taken licenses.

## A results path was renamed away from a collision, 2026-08-22

`results/lever_table.csv` and `scripts/run_lever_table.py` are now
`results/orthogonal_levers.csv` and `scripts/run_orthogonal_levers.py`. The old
name collided with `rb5s6s.hyperpolarizability.lever_table()`, an unrelated
function that ranks candidate transitions for the Ti:Sapphire study, so a
reader grepping the tree for one found the other. No content changed. A link to
the old path from a commit before this date will not resolve.

## The class-adequacy caveat, tested twice in one day, 2026-08-22

Three surfaces carried the statement that the blind residual atlas had not been
run and that class adequacy was therefore untested. Within the same day the
atlas was built, run, declared void, diagnosed and re-run, and each of those
states was written down as it happened. The entry exists so a reader meeting an
intermediate wording knows which one is live.

**The sequence.** The first run detected a common residual shape at the
permutation floor with a clean control, and its own preregistered reproduction
check fired, so the run was declared void and the detection was not reported.
The cause was then traced to a single condition of thirty-two, already measured
by the environment migration as drifting, whose reproduction difference of
1.7e-2 sits BELOW the 2e-2 that `verify_results_fresh.py` sets as this
repository's definition of reproducing. The first run had invented a threshold
twenty times stricter than the guard that defines the term.

**What changed for the second run, and what did not.** The criterion was not
loosened after the fact. A second run was preregistered with the repository's
own standard, plus a leave-one-out over all thirty-two conditions to test what
a threshold cannot: whether one condition drives a detection. It qualified,
detected at the floor in both arms, kept a clean control, and survived every
leave-one-out with zero failures.

**The live statement AS OF THIS ENTRY** is that the tested inference family
leaves reproducible residual structure inside the fit window. It is NOT called
model inadequacy, no mechanism is named, R_kernel is unchanged and its class
caveat stands, and the relation to the excess outside the window is unresolved.

**The last clause was answered on 2026-08-23** and the entry below records it:
the in-window structure and the band excess share a multiplicative-in-signal
predictor, height at 9.41 and 8.65 sigma against density at 1.30 and -0.75.
**The rest of the statement is unchanged.** This sentence is left standing
rather than edited, because the entry is dated and closed and the pointer is
what this file is for. What earned the pointer is the words "the live
statement" in the present tense: a dated entry may hold what was believed then,
and it may not claim to be what is live now.

**Both runs stand.** `results/kernel_k4.csv` carries the second. The first is
in the version history and in the preregistration, which records the void, the
diagnosis and the criteria in the order they were written.

## A published sentence called a sensitivity an uncertainty, 2026-08-22

**The wording, live here and on the public mirror.**
`docs/wiki/self-broadening.md` read "the kernel uncertainty is 3.24 times the
statistical error". It now reads "the sensitivity to the kernel
representation, within the family tested, is 3.24 times the statistical
error", with a following sentence saying that it is a sensitivity within that
family rather than an uncertainty on the coefficient.

**The number never moved.** 3.24 is unchanged, its producer is unchanged, and
`results/kernel_budget.csv` is untouched. What was wrong was the noun.

**Why the noun matters here more than usual.** R_kernel measures how far the
inferred collisional coefficient moves when the kernel representation is
changed WITHIN the tested G, L and G plus L family. Calling it the kernel
uncertainty asserts that the family spans the possibilities, and that is the
one claim the blind residual atlas was built to test and did not establish.
The record's own statement is that class adequacy is not established either
way, so a sentence asserting a total uncertainty contradicted it.

**A SECOND page carried the same wrong noun and was found later the same
night**, by a sweep prompted by an audit of the first correction.
`docs/wiki/laser-frequency-noise-and-the-linewidth.md` read "the resulting
kernel uncertainty is 3.24 times the statistical error". It now states the
sensitivity to the kernel representation within the family tested.

**That page had been invisible to the new guard**, because "kernel" ended one
line and "uncertainty" began the next, and the phrase bank matches line by
line. A phrase that wraps was unreachable by the mechanism built to forbid it,
which is why `tests/test_repo_hygiene.py` now also checks these patterns
against prose with its line breaks removed.

**The full enumeration, corrected.** Seven tracked prose surfaces carry 3.24.
TWO carried the wrong noun and are fixed: `docs/wiki/self-broadening.md` and
`docs/wiki/laser-frequency-noise-and-the-linewidth.md`. Five were already
right: `docs/PLAN.md` calls it a model-form error bar,
`docs/BIG_PICTURE.md`, `docs/wiki/identifiability.md` and
`docs/big_picture/07_limitations-and-identifiability.md` all size it against
the statistical error on a matched footing, and
`docs/quantities/self-broadening.md` states it as a factor between two named
quantities. An earlier version of this entry said four and one, having counted
neither the second defect nor the fourth correct surface.

**What now prevents it.** `tests/test_repo_hygiene.py` banks the phrasing, so
no tracked prose file can call 3.24 the kernel uncertainty or the uncertainty
in the kernel. The bank was narrowed on the day it was written to exclude
"kernel uncertainty statement" and "kernel uncertainty budget", which name the
uncertainty budget producer whose subject is refusing to combine three terms
into one total. That usage is the opposite of this error, and the bank's own
rule is to narrow a token rather than exempt a file.

**The class of defect.** No number-checking guard could see this, because
every number was right. The canonical registry ties surfaces to producer cells
and would have reported this page as correct.

## The environment migration landed, 2026-08-23

The committed digits were made under Python 3.9.6 and numpy 2.0.2. They are now
made under Python 3.14.6, numpy 2.5.2, scipy 1.18.0, pandas 3.0.5, Apple
Accelerate, macOS 26.6.2 on arm64. `results/ENVIRONMENT_OF_RECORD.md` states
the new versions and keeps the recovery recipe for the old ones.

**What moved, measured cell by cell rather than summarised.** Of 58 committed
result files, 56 reproduce. Two moved, and they moved for one reason.

**`results/linefit_conditions.csv`.** 256 cells differ and 250 of them by 1e-7
to 1e-9, which is a different `np.convolve` and nothing else. **Exactly one row
of 32 moves above a part in a thousand**, `t_sweep / 4121 / 70 C`:

| quantity | was | now | relative |
|---|---|---|---|
| `sigma_laser` | 0.4052 | 0.3531 | 1.29e-01 |
| `corr` | -0.70340 | -0.66265 | 5.79e-02 |
| `gamma_coll_err` | 0.23210 | 0.22059 | 4.96e-02 |
| `sigma_laser_err` | 1.4270 | 1.4721 | 3.16e-02 |
| `gamma_coll` | 0.78394 | 0.79727 | 1.70e-02 |
| `total_fwhm_err` | 0.18185 | 0.17972 | 1.17e-02 |
| `total_fwhm` | 5.07133 | 5.07598 | 9.17e-04 |

**That row is flagged `noise_floor_limited`, and its `sigma_laser_err` of 1.47
is four times its `sigma_laser` of 0.35.** The data do not determine the split
there. The TOTAL width, which the data do determine, moves by 0.09 per cent
while the split moves by 13. That is the archive's documented degeneracy
behaving as documented, not a new instability.

**It is the same condition, at the same number, that voided the first run of
the blind residual atlas.** That run reported its worst per-condition
difference as 1.700e-02 on `gamma_coll`. This table's `gamma_coll` row is
1.700e-02. The K4 void and this drift were always one event seen twice.

**`results/identifiability.csv`.** Fourteen rows move. The four this file
predicted on 2026-08-22 all move exactly as predicted: the ridge slope 0.073 to
0.086, the covariance prediction 0.080 to 0.110, the condition number 389.7 to
345.1, the valley-floor RMS 0.0032 to 0.0020, and the best-constrained sigma
does not move. Ten more move that the earlier entry did not name: the three
width-width correlations, the split sigma 0.0624 to 0.0588, the two branch
chi-squares and their gap, the wide-map audit gain, and both free-fit gaps.

**Two of those ten are quoted in public documents and are corrected in this
commit.** The split sigma appears on the front page and in chapter 7, where
the ratio it forms with the total width goes from twenty to eighteen. The
collisional-to-transit and collisional-to-laser correlations appear in the plan's
opening chapter, moving from -0.964 and +0.152 to -0.958 and +0.196. The
condition number is quoted on four pages and becomes 345 on all of them.

**One certification changed character rather than value.** `profile_free_gap`
was -0.01 and is -1.30, so the zoom map now finds a point 1.3 in chi-square
below the anchored free fit rather than agreeing with it. `wide_free_gap` moved
the other way, -0.1 to +1.2. The statistics chapter no longer claims the map
minimum equals the free fit's.

**Two claims made in this file on 2026-08-22 do not survive.**
A note written in this window at 00:50 claimed
that only one of the four predicted movements reproduced, and that the other
three were a defect in this record. **That was wrong, and it was wrong for a
mechanical reason worth stating.** The comparison was made against the
verifier's worktree copy of the file, and `verify_results_fresh.py` computes
its fresh values IN MEMORY and does not write them. The worktree copy was the
committed file all along, so the comparison was committed against committed.

The same trap explains an earlier reading of `linefit_conditions.csv` in the
same window, which appeared to show zero drift. Running the PRODUCERS is the
only way to land or inspect a migration. The verifier detects and reports.

**The condition number is quoted on SEVEN pages, and the first sweep found
four.** The grep searched for the phrase "condition number of 390". Two more
pages write it without the "of", and one writes it as an inline approximation
in maths. `tests/test_docs_canonical.py`
caught the survivor by comparing the prose against the CSV row it describes,
which is what that guard exists for and what no phrasing-based search can
promise. The lesson is the same one this file recorded hours earlier about a
phrase that wrapped a line: a grep proves presence, never absence, and the
pattern that finds four of seven reports clean while doing it.

**Why the drift first appeared as a text change.** The covariance-side
prediction lived inside another row's note string, where no numeric comparison
could grade it and a 37 per cent move surfaced as a changed sentence. It is now
its own row, `ridge_slope_covariance_pred`.

**The blind residual atlas was re-run across the migration, under a freeze in
which only the environment differed, and its detection did not move.** All
fourteen detection rows are unchanged: both arms at the permutation floor with
a common shape detected, leave-one-out robust with no condition above the
preregistered alpha, and the synthetic control clean. Two rows moved, both
measuring how well K4's own refits agree with the committed inputs, and both
went to exactly zero from 1.700e-02 and 6.596e-08.

That was predicted in writing before the run, in both directions, and it closes
a loop: the atlas's first run voided itself on `t_sweep / 4121 / 70 C` at
1.700e-02, which is the same condition and the same number this migration
moved. **The void, the linefit drift and the identifiability drift were one
event seen three times.** `results/kernel_k4.csv` carries the re-run.

**Two DERIVED products were stale and the gate caught them**, which the drift
report could not have, because they are computed FROM the file that drifted.
`resolving_power.csv` and `sigma_laser_sharing.csv` are regenerated. The
sharing chi-squares still round to the 0.27, 0.58 and 0.33 this record quotes,
and the free common sigma_laser range 1.5 to 1.7 is unchanged.

**One published number moves with them.** The resolving-power ledger in
`docs/RESULTS.md` now reads 2.4 for `sigma_laser` where it read 2.3, and its
summary sentence 2.4 to 6.0 where it read 2.3 to 6.0. That number is the ratio
of a width's signal to the noise floor, it carries the verdict `cannot resolve`
at either value, and the change comes from row 21's `sigma_laser` moving 13 per
cent upstream. No conclusion depends on it.

**The hold is discharged.** The migration was held on 2026-08-21 by the
preregistered clause covering a moved quantity that a public document quotes,
which fired on `docs/methods/06_the_statistics.md`'s quoted +0.080. That
chapter now carries the new pair. The other two backstops, a classification
change and more than six moved columns, were evaluated and did not fire, at
2 of 58.

## A results file said a finished instrument was deferred, 2026-08-23

**The sentence, published in both repositories.**
`results/kernel_budget.csv`, row `R_kernel_scope`, read: "class ADEQUACY is a
separate and unresolved question: the blind residual atlas that would test
whether the true kernel lies outside this class **is deferred**".

**It was false by the time it was read.** That atlas was built, run, voided on
its own preregistered criterion, diagnosed, preregistered again, re-run to a
qualifying detection, and re-run once more across an environment migration
under a freeze in which only the environment differed, returning fourteen
detection rows bit-identical. The row now says class adequacy was TESTED, that
no mechanism is assigned, and that the structure's effect on the coefficient is
not quantified, so R_kernel still bounds sensitivity within the class the
analysis chose.

**This entry exists under a contract widened here rather than by drift.** The
stated contract is an entry for a superseded published VALUE. No value moved.
A published CLAIM moved, and a reader could have acted on it, which is the test
this file now applies.

**Why four sweeps missed it, and it is a class rather than an incident.** The
propagation protocol's second step greps for exactly this word. It ran, over
`docs/`. **The claim lives in a CSV note column, which is prose that no prose
check reads.** The same hiding place produced the migration drift that first
surfaced as a unit-string change, where no numeric comparison could grade a 37
per cent move. The remedy is general: any statement a reader could act on
belongs in a row a test can grade, not in a note column, and the future-tense
sweep now covers `results/` as well as `docs/`.

**Two sibling rows were checked and are legitimate.** `kernel_k5.csv` records a
faster-block measurement that genuinely has not been run and points at where it
is ranked, and one row in the fibre thread carries a forecast explicitly
classed PROSPECTIVE with its estimator described as not built. Both describe
work that really is future, which is the distinction that matters.

## The in-window structure and the band excess share a predictor, 2026-08-23

**What was unresolved.** K4 detects reproducible residual structure inside the
fit window and assigns no mechanism. Three surfaces said its relation to the
reproducible excess OUTSIDE the window was unresolved. It is now measured, and
those surfaces say so.

**The instrument was reused rather than invented.** The band-excess work
settled the outside structure by regressing each trace's excess amplitude on
two competing predictors at once, the model's own profile height and log10
vapour number density. Height won at +8.65 and density was null at -0.75.
Taken ONE AT A TIME density looked significant at +2.2, so only the joint form
settles it, and only the joint form is run here.

**The result** (`results/kernel_k8.csv`), n = 32 conditions, weighted by the
inverse variance of each condition's own amplitude:

| predictor | z, inside the window | z, outside, for comparison |
|---|---|---|
| the model's own profile height | **+9.41** | +8.65 |
| log10 vapour number density | +1.30 | -0.75 |

The two predictors correlate +0.488, below the preregistered 0.8, so this is a
separation and not collinearity. Height survives every leave-one-out above
+8.53, so no single condition carries it.

**Why the weights are not optional.** The arm diagnostic found the two fitting
arms disagree on 13 of 32 conditions, monotonically in power, 4 of 4 at the
dimmest rung and 0 of 4 at each of the top three. The least reliable residuals
are the dim ones and profile height is lowest there, so an unweighted fit would
confound the predictor with the reliability of the response.

**A DEVIATION from the preregistration, recorded rather than hidden.** The
preregistered secondary was the twelve conditions at the top three powers, and
all twelve sit at one temperature, because the power sweep runs at one
temperature. So density has zero variance there and the joint fit is singular
by construction. A height-only fit gives +4.96, which shows height matters and
cannot show density does not. **The lesson is that a subset selected on one
experimental axis often has no variation on another, and a preregistered
secondary must be checked for predictor variance when it is written.**

**What this does NOT establish, and it is the important half.** A residual
normalised by the per-point noise scales with the signal under ANY fractional
model error. Profile mismatch does that, and so does a detector nonlinearity,
which this record already fits as a per-session saturation nuisance, and so
does an amplitude-dependent baseline error. **So the mechanism is not named.**
What is excluded is a density-driven collisional origin, at 9.4 against 1.3.

**R_kernel is unchanged and no committed number moves.** The effect of the
structure on the collisional coefficient remains unquantified.

## A published regression had no producer, 2026-08-23

**What changed.** No number moved. What changed is what the record says about
where four of them stand.

**The claim.** [The band-excess note](notes/band_excess_is_model_form.md)
publishes a joint regression over 79 canonical traces: the excess tracks the
model's own profile height at 8.65 sigma, vapour density is null at -0.75, the
two predictors correlate 0.415, and a shared excess stands at 3.6 sigma under
per-trace cubic freedom. **No committed producer computes any of it and no
`results/` row holds it.** The commit that introduced the page, 2026-08-17,
says so in its own message: "Nothing in `results/` moved". That sentence was
written as a reassurance that no bound had changed. Six days later it is also
the description of a gap.

**Why nothing could have caught it.** Every freshness instrument in this
repository starts from a `results/` row. `verify_results_fresh` compares a CSV
to its producer, and the committed-CSV test does the same. A number that never
became a row is outside the domain of both. The documentation tests read links,
images, structure and style, and none of those is provenance. So the numbers
were public and ungraded, and no in-tree check could see it.

**And it had already propagated into a graded file.** On 2026-08-23
`run_kernel_k8.py` quoted 8.65 and -0.75 into the note column of
`results/kernel_k8.csv`, to compare them against its own freshly computed 9.41
and 1.30. A checked file now carries unchecked numbers, in prose that no check
reads. **That is the same shape as the deferred-atlas falsehood corrected on
the public page this morning**, and it is the second instance in one day of a
note column carrying a claim.

**What was done.** The numbers are not withdrawn and none is known to be wrong.
The note, the limitations chapter and the front page now each state that the
band pair stands on a weaker footing than the K8 pair beside it, because a
reader comparing 8.65 against 9.41 cannot otherwise tell that one is
regenerated on every run and the other is regenerated by nothing.
`tests/test_note_provenance_ratchet.py` records a per-file budget of numeric
claims in `docs/notes/` that declare nothing, so no new note can join them
quietly. **Ten notes carrying 86 claims are recorded as debt**, and paying it
down means checking where each number actually lives rather than labelling it,
which is why they were not declared in bulk today.

**Giving this analysis a producer and a graded row remains open.** Writing one
now would recompute six-day-old numbers under a different numpy in an
environment the record already flags as not the environment of record, so a
disagreement could not be read as either drift or a difference in
reconstruction. It belongs in a window that can do it properly.

## Seven of ten notes had no producer, 2026-08-23

**What changed.** No number moved. What changed is that every note in
`docs/notes/` now states what its numbers stand on.

**The audit.** The band-excess finding earlier the same day raised the obvious
question: how many other notes are like that? Ten notes carrying undeclared
numeric claims were read claim by claim against `results/` and `scripts/`.
**Seven of the ten have no committed producer for the numbers that carry their
own argument.** Three have a genuine `results/` home. **109 individual claims
across the corpus remain unaccounted for**, and the declarations now name them
rather than leave them to be discovered.

**Three cases are worth stating individually.**

`s0_block_bootstrap_prereg.md`. The producer's own docstring says it writes
"one row per resample to private/run_logs/, nothing into results/", and calls
its output DIAGNOSTIC "until the prereg postscript adjudicates". **The
postscript adjudicated and nothing was ever promoted.** A deliberate temporary
state became permanent. Worse, its factor of 2.4 was hand-copied into
`scripts/make_results_ledger.py` as a string literal and published in
`docs/RESULTS.md`, so a public page asserts a number whose only evidence is a
gitignored run log. **That page now says so.**

`companion_inclusive_refit_prereg.md`. Its producer contains exactly one
`open()` call, a read, and every output is a `print()`. The note says so itself,
"which writes nothing". The script is also absent from `run_all.sh`, so even a
full pipeline run leaves no artefact.

`centre_channel_cannot_be_revived.md`. A hybrid. Its comparisons against the
width channel are properly homed in two committed CSVs, and **every number
carrying its own argument, the forecast table included, has no trace anywhere**.

**One arithmetic error was found and corrected.** `model_selection_prereg.md`
printed `dAIC = -24.6 - 18 = -6.6`. The operator is wrong and the value is
right, since 9 ln(13853) is 85.8, so the chi-squared difference is -24.6 and
AIC's charge of 18 gives -6.6 by addition. **The AIC reversal it reports
stands.** The line now reads `-24.6 + 18 = -6.6`.

**What this does not do.** It does not give any of these numbers a producer.
Seven notes still rest on computations nothing regenerates, and the honest
position is that a declaration is a label on a gap rather than a repair.
`tests/test_note_provenance_ratchet.py` now holds a budget of zero, which means
every note SAYS what it stands on and not that every number is graded.

## A governed row about ungoverned numbers, 2026-08-23

**What changed.** No measured number moved. `results/unregenerated_claims.csv`
is new, and it counts how much of this record no producer regenerates.

**Why a CSV and not prose.** The declarations added earlier the same day live
in ten separate notes, in prose, which is where the problem started. **Every
freshness instrument here begins at a `results/` row**, so a gap described only
in prose is governed by nothing. As rows, the gap is graded by the same
machinery as any measurement, and a reader counts it without opening ten files.

**What it says today.** Fourteen notes carry a declaration. **Eight rest on
numbers no committed producer regenerates**, three have a real `results/` home,
three are design or index pages where none is expected, and **109 individual
claims remain unaccounted for inside declared notes.** A declared note is not a
clean note.

**The producer derives its rows rather than listing them**, by scanning the
`provenance:` tokens in `docs/notes/`. A hardcoded inventory would be a literal
in a producer, which is the failure this repository has now met twice: a figure
drew a retracted value from a literal in its generator, and a bootstrap factor
reached `docs/RESULTS.md` the same way. **The instrument is subject to the rule
it enforces**, so a declaration edited without re-running it fails the
freshness test.

**And a forward pointer was added to the K4 entry above.** That entry says "the
live statement" in the present tense and ends on the relation to the band
excess being unresolved, which K8 answered on 2026-08-23. The sentence is left
standing and now carries a pointer, because the entry is dated and closed.
**What earned the pointer is the present tense**: a dated entry may hold what
was believed then and may not claim to be what is live now.

## Two producers disagreed about R_kernel in the fourth decimal, 2026-08-23

**What moved.** `results/kernel_k5.csv`'s `R_kernel` from **3.2403 to 3.2398**,
which is now identical to `results/kernel_k3.csv`. **No published claim
changes**, because every quotation of this number in every document says 3.24
and both values round to it.

**The cause, and it is the reason the entry exists.** `run_kernel_k3.py`
computes the ratio from full-precision floats. `run_kernel_k5.py` read
`kernel_k3.csv` back off disk **as text**, took the already-rounded six-decimal
display strings 0.004530 and 0.001398, and divided them, giving 3.2403. The K5
note asserted the two were the same quantity, and they are, and the files
disagreed.

**Why it survived.** The disagreement was invisible at the precision anyone
quoted. A defect that changes nothing a reader can see is the kind that lives
longest, and the only reason it was found is that an adversarial audit compared
two committed files against each other rather than each against its own
producer.

**The general rule, which is worth more than the fix.** **A producer that reads
another producer's OUTPUT FILE inherits its display precision, not its
arithmetic.** K5 now reuses K3's own `R_kernel` value rather than re-deriving it
from displayed intermediates, so one producer owns the number.

**What this cost.** The edit restales every figure through the data
fingerprint, which is why it waited for a window with nothing else in flight.

## Two results files were committed without their status column, 2026-08-23

**What was wrong.** `cooperative_channel.csv` and `orthogonal_levers.csv` were
committed missing the `status` column that every result file carries, and the
committed figures did not match the committed CSVs. **No value was wrong.** The
files were structurally incomplete and the commit was internally inconsistent.

**The cause, and it is a process failure rather than a code one.** Producers
write their CSVs without the status column and `annotate_results_status.py`
adds it afterwards. **A batch of read-only investigation running against this
same working tree executed several producers to check their behaviour**, which
stripped the column, and the next `git add -A` committed that state along with
the intended change.

**Two gates caught it and neither diagnosis was the first one.** The first gate
failed on eleven stale figures, which reads like a forgotten redraw. The second
failed on the missing status column, which is the actual defect. **The figure
fingerprint is a downstream symptom of any results mutation**, so it fires
first and points at the wrong thing.

**The rule.** `git add -A` commits whatever is in the tree, including changes
made by something other than the work in hand. **Anything that writes
`results/` must have the tree to itself**, and that includes investigation
running beside the work rather than only the known tree-writers. The repair is
deterministic: re-run the producers, re-run the annotator, redraw, and the
values are unchanged because the producers are reproducible.
