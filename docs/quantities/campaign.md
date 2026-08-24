# The campaign

*[quantities index](README.md) · synthesis*

**The question.** The dossiers are written one quantity at a time, and a
measurement session is not. Which re-centrings move which quantities, which
ones move several at once, and what would one session actually buy?
**Takes.** The dossiers and the plan chapters. Nothing new.
**Gives.** The coupling between the quantities, the leverage of each
re-centring across all of them, a comparison of candidate sessions, and the
smallest version of each that is already worth running.
**Skip if.** The question is the ordering of the whole programme by leverage,
which is [big picture chapter 5](../big_picture/05_next-vapour-cell.md), or the
detailed design of one block, which is [the plan](../PLAN.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md) defines
> every term and symbol used anywhere in this repository.

## The quantities are one coupled system

Reading the dossiers separately gives a misleading picture of the experiment,
because the quantities are not independent and the couplings are the reason a
single session can be efficient.

**The waist is the hub.** It sets the intensity, and therefore the light shift,
quadratically. It sets the transit width, inversely. Those two enter the same
composite line, so an error in the waist moves the light-shift prediction and
the transit kernel in the same stroke and in different directions. It is one
number that two dossiers both depend on, measured on this bench by Rajasree
but never re-read during the campaign itself, which is why it is the first
item of
[big picture chapter 5](../big_picture/05_next-vapour-cell.md).

**Power raises the signal and three contaminants together.** The light shift
grows linearly in power, and so do atomic saturation and hyperfine pumping,
which broaden the same width channel. That shared power law is not a nuisance
to be minimised, it is the reason the width channel cannot separate them and
the reason the centre channel is the route to a measurement.

**Temperature raises the density and the background together.** Higher density
is the whole lever for self-broadening, and it arrives with blackbody
redistribution, thermal gradients, and a vapour-pressure extrapolation carrying
more weight.

**The laser width and the collisional width trade directly.** They broaden the
same line and sit on a ridge at condition number 345. Measuring either one
externally is worth more to the other than any improvement in fitting.

**The frequency axis underwrites everything with a centre in it.** A light
shift read from line centres is a measurement of the axis as much as of the
atom, which is why the fixed lock appears in the light-shift dossier rather
than only in a calibration chapter.

## What each re-centring moves

Qualitative, and deliberately so. A numeric leverage would need a simulation
per cell, and only the cells marked with a computed factor have one. Every
entry points at the section that argues it.

| re-centring | light shift | self-broadening | laser width | waist | transit | axis | band excess |
|---|---|---|---|---|---|---|---|
| beam profile on the day, several powers, EOM thermalised | +++ | | | +++ | +++ | | + |
| fixed cavity lock | +++ | | | | | +++ | + |
| randomised power ladder | ++ | + | | | | + | |
| external laser-width calibration | + | +++ (factor 1.7, computed) | +++ | | | | + |
| temperatures to 150 and 170 C | | +++ | | | | | + |
| absorption channel for the density | | +++ | | | | | |
| atomic-pair rulers within every trace | + | | | | | +++ | |
| EOM modulation-depth ladder | | | + | | | ++ | |
| fitting every EOM tooth rather than the carrier | | | + | | | ++ | + |
| photon counting in the wings | | | | | | | +++ |
| polarisation blocks | ++ | | | | + | | +++ |
| a tighter focus near 16 microns | +++ | | | ++ | +++ | | |

Two readings of that table matter more than any single cell.

**The first two rows carry most of the programme.** A beam profile and a fixed
lock between them touch five of the seven quantities, and neither requires
apparatus that does not exist. The lock is now available rather than proposed.

**The external laser-width calibration is the only row that buys by removing.**
Every other re-centring raises a sensitivity and brings a new systematic with
it. That one takes a competitor out of the fit and is the only cell in the table
with a computed factor behind it, the 1.7 in
[identifiability](../wiki/identifiability.md).

## Four candidate sessions, compared

Information gain is stated against what the archive currently establishes, and
the time column is order-of-magnitude rather than a schedule. No utility score
is computed, because the inputs to one do not exist.

| session | what it buys | time | apparatus change | dominant failure mode |
|---|---|---|---|---|
| **A. Beam characterisation** | the waist measured at several powers with the EOM thermalised, and the retro ratio against power | half a day | none, a profiler in the beam | the waist may not be stable against power, which would withdraw the pooling rather than tighten it |
| **B. Fixed-lock power ladder** | absolute centres across the ladder, opening the sensitive moment for the light shift | one to two days | the lock, now available | lock drift imitating the pull, which a zero-signal control epoch has already produced once at 2.7 standard deviations |
| **C. Extended temperature ladder** | 150 and 170 C with an absorption channel, extending the density lever about fivefold and measuring rather than inferring the density | two days | absorption path on the cell | blackbody and thermal gradients broadening the line, which would make the added points uninterpretable |
| **D. External laser-width calibration** | the sigma-gamma ridge broken from outside the fit | one day, mostly setup | a delayed self-heterodyne or cavity reference | that the ridge is not what limits the bound, which would be a real result and a negative one |

**The efficient order is A, then B or D, then C.** A is the cheapest, feeds
every other session, and is the only one that can invalidate the joint
constructions the record already carries. B and D are independent of each other
and buy different things, an identifying channel and a broken degeneracy
respectively. C is the most expensive and the most exposed to a systematic that
would spoil it, so it goes last and only after A has fixed the geometry.

**The minimum entry into the whole programme is session A at its minimum
viable version**, which is one profiler measurement at three powers with the
EOM in the beam and thermalised. That is an afternoon, it converts the
programme's largest open systematic from set point to measured, and it can return
a result that changes what the rest of the plan should be. A programme that can
be entered that cheaply should be.

## What the equipment can already do

This section is deliberately incomplete. The apparatus record establishes what
was used in 2025, and what a bench can do today is the owner's knowledge rather
than the record's. Rows are marked accordingly, and a row marked as requiring
bench confirmation is not evidence of feasibility.

| requirement | in the record | needs bench confirmation |
|---|---|---|
| beam profiler in the 993 nm path | not documented in this campaign | yes |
| cavity lock | repaired 2026-08-16, acquisition design in [plan 9](../plan/09_the-fixed-lock.md) and [plan 10](../plan/10_the-fixed-lock-instrument.md) | yes, its stability over a ladder, the stage-0 go/no-go |
| EOM with variable modulation depth | used as the frequency ruler | yes, the accessible depth range |
| four hyperfine peaks in one scan | the four lines are the campaign's own | yes, whether one span covers all four |
| temperatures to 170 C | the ladder reached 130 C | yes, the oven's ceiling and gradient |
| absorption channel | proposed, not built | yes |
| photon counting | proposed in [plan 7](../plan/07_acquisition-settings.md) | yes |
| a 12-bit or better acquisition | **already delivered**: the campaign's own files carry an 11.86-bit grid from the Agilent's High Resolution mode, measured 2026-08-19, and the LeCroy channel export is the eight-bit one | no. The open item moved: holding one vertical range across the ladder, feasible at a dither ratio of 0.99 with the bright range set tight, per [plan 7](../plan/07_acquisition-settings.md) |
| a measured detector response curve | bounded but never traced: the rehearsal's finer-sampled records put the chain faster than 10 us at the 10^6 V/A gain, and the range-to-range gain remains the leading candidate for the amplitude departure | yes, converting the bound into a curve, and it needs no atoms, only a calibrated variable source |

## See also

- [The AC-Stark light shift](ac-stark-light-shift.md) and
  [collisional self-broadening](self-broadening.md), the two written dossiers
- [Big picture chapter 5](../big_picture/05_next-vapour-cell.md), the whole
  programme ordered by leverage
- [The plan](../PLAN.md), where each session's blocks carry their own needs,
  shots, go-no-go and failure branch
