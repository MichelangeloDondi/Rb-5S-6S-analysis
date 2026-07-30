---
citekey: erickson2024
type: misc
authors:
  - Erickson, S. E.
title: 'An Optical Atomic Clock Based on Frequency Comb Spectroscopy'
journal: 'PhD dissertation, University of Arizona'
volume: null
pages: null
year: 2024
doi: null
arxiv: null
pdf: PDF_papers/theses/Erickson_2024_PhD-thesis_optical-clock-frequency-comb-spectroscopy.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'This is the dissertation, NOT the related Optics Letters journal article
    (which is paywalled and has no arXiv preprint -- checked 2026-07-30 by
    author search, title search and topic search). The dissertation covers the
    same experiment and states the same measured linewidth budget.'
  - 'Fetched from the College of Optical Sciences alumni page
    (wp.optics.arizona.edu), an institutional host of the author''s own work,
    not a publisher copy.'
verified_date: 2026-07-30
summary: >
  A Rb 778 nm two-photon optical clock (University of Arizona), fetched
  2026-07-30 to pin down a beam-waist convention in bandi2025's Table 1. States
  a COMPLETE, term-by-term linewidth budget rather than a total: 762 kHz
  observed FWHM (cw) = natural 330 kHz + transit-time 310 kHz (for a 230 um
  beam DIAMETER at 100 C) + helium collisional 200 kHz (4 mTorr He) + Rb
  collisional 16 kHz (negligible) + Zeeman (negligible). The explicit
  "diameter" contradicts lemke2022's explicit "radius" for the same tabulated
  column, so the column is not a single convention. Feeding this repository's
  own transit_fwhm_from_w0 the same geometry gives 513 kHz against Erickson's
  stated 310 kHz (w0=115 um) -- a 1.65x mismatch that is a TRANSIT-FORM
  difference (this repo's Biraben-Cagnac cusp vs. Erickson's cited
  Demtroeder Gaussian form), not a waist-convention error.
loci:
  - M9
  - methods/03
section: method-anchors
---

# erickson2024

**Read (relevant sections) 2026-07-30** from the held PDF, fetched to resolve an
apparent anomaly in [bandi2025](bandi2025.md)'s Table 1 review of Rb two-photon
clocks. See that note for the full M9 comparison; this note carries the
bibliographic record and the passage it depends on.

## The budget, verbatim

> A lorentzian fit to these lineshapes resulted in a FWHM linewidth of 762 kHz
> for cw excitation and 774 kHz for direct comb excitation. This linewidth
> includes contributions from the natural lifetime (330 kHz), transit-time
> (310 kHz for 230 µm beam diameter at 100 °C), helium collisional broadening
> (200 kHz given 4 mTorr He partial pressure). The contribution from rubidium
> collisional broadening (16 kHz) and Zeeman broadening are believed to be
> negligible.

## Why it is here

It is the only row in [bandi2025](bandi2025.md)'s Table 1 with a published
**term-by-term** budget rather than a bare total, which makes it checkable
against this repository's own model piece by piece rather than only in
aggregate.

It also settles, and then re-opens, a question about that table. It settles
that the waist column is **not a single convention**: this paper states "230 µm
beam **diameter**" where [lemke2022](lemke2022.md) states its own waist as an
explicit 1/e² **radius**. And feeding $w_0 = 115$ µm (half the stated diameter)
at 100 °C through `rb5s6s.constants.transit_fwhm_from_w0` gives **513 kHz**
against Erickson's own **310 kHz** — a factor of 1.65 that widens rather than
narrows the question, because it is not explained by the radius/diameter
ambiguity already found. The candidate explanation is a **transit-form**
mismatch: this repository's function is the FWHM of the Biraben–Cagnac
two-sided-exponential (the cusp), while Erickson cites Demtröder, *Laser
Spectroscopy* Vol. 1, §3.4 for "transit-time broadening" without reproducing
the formula in the text. **Not resolved here** — reading Demtröder §3.4 is the
cheap next step, and it would convert this from a suggestive mismatch into a
quantitative statement about which transit form his 310 kHz actually is.
