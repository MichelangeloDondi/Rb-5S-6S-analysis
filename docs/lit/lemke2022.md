---
citekey: lemke2022
type: article
authors:
  - Lemke, N. D.
  - Martin, K. W.
  - Beard, R.
  - Stuhl, B. K.
  - Metcalf, A. J.
  - Elgin, J. D.
title: 'Measurement of Optical Rubidium Clock Frequency Spanning 65 Days'
journal: Sensors
volume: 22
number: 5
pages: 1982
year: 2022
doi: 10.3390/s22051982
arxiv: null
pdf: PDF_papers/Lemke_2022_Rb-optical-clock-frequency-65-days.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Open-access MDPI journal; PDF fetched via PubMed Central (PMC8915036), an
    NIH mirror of the publisher copy, not the author''s own upload. No arXiv
    preprint exists or is needed.'
verified_date: 2026-07-30
summary: >
  A Rb two-photon optical clock (AFRL/Space Dynamics Lab), fetched 2026-07-30 to
  pin down a beam-waist convention in bandi2025's Table 1. States their waist
  EXPLICITLY as an intensity radius (1/e^2), w0 = 2.1(3) mm, at 10(1) mW one-way
  power giving a calculated light shift of -183 Hz (55 Hz uncertainty). Also
  reports a 65-day drift rate of 4e-15/day, a 10-day Allan deviation below
  5e-15, and an absolute Rb-87 two-photon transition frequency of
  385,284,566,371,190(1970) Hz.
loci:
  - M9
  - methods/03
section: method-anchors
---

# lemke2022

**Read (relevant sections) 2026-07-30** from the held PDF, fetched to resolve a
waist-convention question in [bandi2025](bandi2025.md)'s Table 1 review. See
that note for the full M9 comparison.

## The waist, verbatim

> With an intensity radius (1/e2) of w0 = 2.1(3) mm and one-way laser power of
> 10(1) mW, we calculate a light shift of −183 Hz, and an uncertainty in this
> correction of 55 Hz.

Explicit and unambiguous: **radius**, not diameter — the opposite convention
from [erickson2024](erickson2024.md)'s "230 µm beam **diameter**" in the same
tabulated column of the review. That contrast is what shows the column mixes
conventions rather than being a single one, mishandled.

## Other headline results, not otherwise used here

A 65-day continuous measurement quantifying helium contamination of the glass
vapour cell (by gradually removing it under vacuum), giving a drift rate of
$4\times10^{-15}$/day, a 10-day Allan deviation below $5\times10^{-15}$, and an
absolute frequency for the Rb-87 two-photon clock transition of
$385~284~566~371~190(1970)$ Hz. None of this has been used against this
programme's own measurements; recorded for completeness of the note.
