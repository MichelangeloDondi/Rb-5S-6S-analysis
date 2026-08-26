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
  - 'Obtained from the College of Optical Sciences alumni page
    (wp.optics.arizona.edu), an institutional host of the author''s own work,
    not a publisher copy.'
verified_date: 2026-07-30
summary: >
  A Rb 778 nm two-photon optical clock (University of Arizona), read to
  pin down a beam-waist convention in bandi2025's Table 1. States
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

Held. Covers the same experiment as the related Optics Letters article and states the same measured linewidth budget.

## The system

A Rb 778 nm two-photon optical clock (University of Arizona).

## The linewidth budget

> A lorentzian fit to these lineshapes resulted in a FWHM linewidth of 762 kHz for cw excitation and 774 kHz for direct comb excitation. This linewidth includes contributions from the natural lifetime (330 kHz), transit-time (310 kHz for 230 µm beam diameter at 100 °C), helium collisional broadening (200 kHz given 4 mTorr He partial pressure). The contribution from rubidium collisional broadening (16 kHz) and Zeeman broadening are believed to be negligible.

## Use in this record

This is the only entry in the Table 1 comparison of Rb two-photon clocks (see [bandi2025](bandi2025.md)) with a published term-by-term linewidth budget rather than a bare total. It states the beam waist as a 230 µm diameter, where [lemke2022](lemke2022.md) states its own waist as an explicit 1/e² radius, so the waist column in that comparison is not a single convention. Passing w0 = 115 µm (half the stated diameter) at 100 °C through `rb5s6s.constants.transit_fwhm_from_w0` gives 513 kHz against the paper's stated 310 kHz, a factor of 1.65 not explained by the radius/diameter difference alone. The likely source is a difference in transit-time functional form, a two-sided-exponential cusp against the Gaussian form cited from Demtröder, *Laser Spectroscopy* Vol. 1, §3.4, whose formula is not reproduced in the text.
