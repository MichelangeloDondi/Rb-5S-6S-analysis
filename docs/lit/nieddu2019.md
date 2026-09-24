---
citekey: nieddu2019
type: article
authors:
  - Nieddu, T.
  - Ray, T.
  - Rajasree, K. S.
  - Roy, R.
  - Nic Chormaic, S.
title: 'A simple, narrow, and robust atomic frequency reference at 993 nm exploiting the rubidium 5S₁/₂ to 6S₁/₂ transition using one-color two-photon excitation'
journal: Opt. Express
volume: 27
number: 5
pages: 6528
year: 2019
doi: 10.1364/OE.27.006528
arxiv: 1812.07874
pdf: PDF_papers/Nieddu_2019_993nm-5S-6S-two-photon-frequency-reference.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  OIST apparatus lineage with the previous laser generation. Page 6530 states
  "The 1/e^2 beam diameter is 128 um" (their f = 150 mm). Rajasree-KP 2020
  section 5.2 quotes the same number but is the SAME data (its footnote: the
  section 5.2 data "were collected by T. Nieddu"), so this is one measurement,
  not two. RETIRED AS THE WAIST AUTHORITY on the owner's ruling, 2026-09-10:
  choosing between two reports of one measurement taken on the earlier laser
  cannot recover a beam this campaign ever had, and a focused waist is a
  property of the INPUT beam, which is what changed. Retired again as the
  convention itself, owner order O44, 2026-09-21: the record now carries
  constants.W0\_CENTRAL\_M, the bore-limited actual focus it calculates for
  this bench's EOM bore and lens (42.38 um, at an input radius nothing on the
  bench measures), in place of a value adopted from this lineage, and every
  absolute result stays BOUND on it.
loci:
  - M7
  - P1
  - P2
  - constants
  - methods/02
section: oist-lineage
---

# nieddu2019

Held. Page 6528 and the DOI verified against the publisher PDF.

## The system

One-colour two-photon excitation of the Rb 5S1/2 to 6S1/2 transition at 993 nm, in a natural-abundance Rb cell at 130 C (OIST apparatus, an earlier laser generation than the current campaign). The retroreflector is a concave mirror (f = 75 mm) at twice its focal length from the focus, self-imaging the beam. Detection collects the 780 nm and 795 nm decay fluorescence together through an 800 nm short-pass filter.

## The numbers

Four hyperfine peaks were fit with FWHM 2.43-2.60 MHz on the laser-frequency axis, about 5 MHz on the two-photon transition axis. The laser (an MBR-110) has a quoted linewidth of about 100 kHz, a stated figure rather than a measurement in the paper. The 1/e^2 beam diameter, measured with a beam profiler, is 128 um (page 6530), giving a waist w0 = 64 um for f = 150 mm.

## Use in this record

The waist this repository once carried from this lineage was attributed to rajasree2020thesis, not to this paper: its section 5.2 reports the same 128 um figure on the same bench, crediting the underlying data collection to T. Nieddu. The two reports are one measurement, and this paper's setup carried the earlier laser generation. Owner order O44 (2026-09-21) retired that transferred value, and `constants.W0_CENTRAL_M` now holds this record's own calculated bore-limited focus (42.38 um) in its place.

## Values

The load-bearing numbers of this source, each at its stated
location, so a prose quote anywhere in this repository can
reference a row here and be checked against it.

| field | value | where in the paper |
|---|---|---|
| beam_diameter_um | 128 | page 6530, the 1/e^2 diameter by beam profiler. The same figure on the same bench is reported by rajasree2020thesis section 5.2, the source of the transferred waist this record carried until owner order O44 retired it (2026-09-21) |
| fwhm_laser_axis_mhz | 2.43-2.60 | the four peaks' fitted FWHM on the laser axis, about 5 MHz on the transition axis |
| laser_linewidth_khz | ~100 | the MBR-110 linewidth as stated for their laser, a quoted figure and not a measurement reported in the paper |
