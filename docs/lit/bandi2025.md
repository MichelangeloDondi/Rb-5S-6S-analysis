---
citekey: bandi2025
type: article
authors:
  - Obaze-Adeleke, A. C.
  - Semon, B.
  - Bandi, T. N.
title: 'A comprehensive review of rubidium two-photon vapor cell optical clock: long-term performance limitations and potential improvements'
journal: Photonics
volume: 12
number: 5
pages: 513
year: 2025
doi: 10.3390/photonics12050513
arxiv: null
pdf: PDF_papers/Bandi_2025_Rb-two-photon-vapor-cell-clock-review.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'CITEKEY NAMES THE CORRESPONDING AUTHOR, NOT THE FIRST (noted
    2026-07-30). The record here is correct and checked against the held
    PDF: the paper is Obaze-Adeleke, Semon and Bandi, and T. N. Bandi is
    the corresponding author, not the first. The key follows how the
    review is known rather than this repository''s usual first-author
    convention. Consequence to watch: docs cite it in prose as "Bandi
    2025", and expanding that to "Bandi et al. (2025)" in a manuscript
    would be WRONG -- it is "Obaze-Adeleke et al. (2025)". Do not rename
    the key (it is used in three documents); render the citation from the
    authors field, not from the key.'
  - 'Quotes Hamilton''s 5S-5D magic wavelength as 778.179(5) nm; Hamilton 2023
    itself says 776.179(5) nm in its abstract and conclusions. Transposition in
    the review -- cite Hamilton directly, not this.'
verified_date: 2026-07-26
summary: >
  Landscape/systematics review for the Rb two-photon clock. Names the AC Stark
  shift, the temperature-induced shift and laser drift together as the
  medium-to-long-term limiters; targets better than 1e-15 at a day.
loci:
  - P1
section: landscape-24-26
---

# bandi2025

MDPI open access (not yet held as PDF; MDPI and preprints.org both refuse
automated fetch -- download by hand from the DOI page). The single best
landscape/systematics-benchmark review for the Rb two-photon clock.

**Full text read 2026-07-26** (44 pp; PDF supplied by the experimenter after
MDPI and preprints.org both refused automated fetch).

**What it actually ranks.** The abstract lists three limiters without ordering
them, but the body does order them:

> "light shift variations (stemming from fluctuations in the laser optical power
> that probe the rubidium transition) [117,120,136,157] and vapor-cell
> temperature variations [136] **predominantly limit performance for medium- to
> long-term averaging**."

So the pair -- light shift AND cell temperature -- is named as predominant
together, above laser drift and the rest. Both halves matter here: the light
shift is what the ramp method reads, and the cell-temperature term is the
density-coefficient territory this archive bounds.

**Numbers worth having.** The 5S-5D two-photon working linewidth is quoted as
**~330 kHz**, against the 3.49 MHz natural width of 5S-6S -- the 778 nm line is
roughly an order of magnitude narrower, which is the quantitative form of why
993 nm is not a better clock line. Field target: better than 1e-15 at one day.
Reported temperature coefficient -1.09(4)e-12 per K; He collisional shift
0.55e-8.

**A transcription error to route around.** The review reports Hamilton's 5S-5D
magic wavelength as "an experimental magic wavelength of 778.179(5) nm and a
theoretical magic wavelength of 776.21 nm". Hamilton 2023 (held here) says
**776.179(5) nm** experimental and 776.21 nm theoretical, repeatedly, in both
abstract and conclusions -- the review has transposed a digit. `constants.py`
carries 776.179, which is correct. Hamilton also reports a SECOND magic
wavelength at 790.26 nm, close to the 5S tune-out.

**Coverage gap, confirmed by search.** 5S-6S / 993 nm appears nowhere in the
body -- the only hits are reference titles (Nez 1993, a 5S-5D3/2 paper). The
review is a 5S-5D landscape; it does not touch this line.

**Citation scope.** "The review identifies light shift and cell temperature as
predominantly limiting medium-to-long-term performance" is supported verbatim.
"The review identifies the light shift as THE limiting systematic" is not --
that claim was written and withdrawn on 2026-07-26, before the full text was
available.
