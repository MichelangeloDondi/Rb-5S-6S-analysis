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
| AC-Stark S₀ at 225 mW | 0.14 MHz | 2026-08-01 | joint fit over every point of every profile across all three sessions, the campaign, the 4 July evening and the campaign morning | a construction change rather than a correction. Both bounds stand and the tighter is quoted | the tighter of the two, as quoted here since 2026-08-01. Requote from RESULTS.md |
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
