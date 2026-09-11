---
citekey: fendel2007
type: article
authors:
  - Fendel, P.
  - Bergeson, S. D.
  - Udem, Th.
  - Haensch, T. W.
title: 'Two-photon frequency comb spectroscopy of the 6s-8s transition in cesium'
journal: Opt. Lett.
volume: 32
year: 2007
doi: null
arxiv: null
pdf: PDF_papers/Fendel_2007_Cs-6s-8s-two-photon-comb-average-not-peak-AC-Stark.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  The nearest published analogue of this record's transition driven by a
  comb and not a single-frequency laser. An alkali S-to-S two-photon
  line, in cesium, excited directly by a picosecond frequency comb from
  the Haensch group, with the comb both driving the transition and
  calibrating its own axis.
loci: []
section: prior-art
---
# fendel2007

Held, three pages, checked against the PDF.

## What they do

Direct two-photon excitation of the cesium 6s-8s line by a picosecond
frequency comb. The comb drives the transition and rules the frequency axis at
once, which is the property that makes it interesting here: the axis needs no
separate reference.

Their stability figures, from the text: a low-bandwidth feedback loop on the
repetition rate, a long-term drift "measured with the fs comb to be less than
50 Hz/s", and the frequency instability of a single comb mode "less than 10
kHz in a 1 s measurement time".

## Where it sits against this record

The cesium 6s-8s transition is the closest structural analogue to rubidium
5S-6S that the literature drives: both are alkali S-to-S two-photon lines with
a scalar two-photon operator and no fine structure in the upper state. That is
also why [lee2010](lee2010.md), on the same cesium transition, is this
record's worked example of a symmetric Voigt fitted to a light-shifted line.

**What differs is the drive.** A comb spreads the power over many teeth, so
the peak intensity per tooth is low and the light shift with it, while the
pulse structure introduces its own effects. This record drives with a
single-frequency laser and wants the shift large. The two approaches sit at
opposite ends of the same axis the EOM comb lever explores, where the drive is
divided among teeth at fixed total intensity.

## The AC Stark statement, which is the reason to hold this paper

From the abstract, verbatim: "it is shown that the AC Stark shift of the
transition is determined by the average rather than the much larger peak
intensity." The body puts it again: "the AC Stark effect derives from the
average laser intensity rather than the peak intensity."

**That is this record's own question asked on the time axis instead of the
space axis.** A pulse train presents an atom with an intensity that varies
enormously and fast. The shift follows the MEAN because the modulation is fast
against the atomic response, which is exactly the criterion
[camparo1992](camparo1992.md) draws between fast fluctuations, which average
to a symmetric line at the mean shift, and slow ones, which skew it. This
record lives deliberately at the opposite end: the intensity varies in space,
an atom samples it slowly as it crosses, the distribution does NOT collapse to
its mean, and the residual asymmetry is the signal.

**And it is concordant with the comb lever's own derivation here.** A pure
phase modulation holds the total intensity constant in time, so the light
shift is the same for the carrier and every sideband at any depth, which is
the record's statement that `S0 = kappa P` with `P` the total power. Fendel's
"average intensity" is that statement for a pulse train. The two agree, and
the agreement is a check on the comb model and not a new input.

## What it does not settle

No light-shift distribution or lineshape asymmetry is extracted. The comb is a
metrology tool here, not a probe of the intensity distribution.
