---
citekey: steck_rb
type: misc
authors:
  - Steck, Daniel A.
title: 'Rubidium 85 and 87 D Line Data'
journal: 'available online at \url{https://steck.us/alkalidata}'
doi: null
arxiv: null
pdf: PDF_papers/Steck_Rb87_D-line-data.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'Rb85 and Rb87 sheets both held; values below read from the Rb87 sheet 2026-07-26.'
verified_date: 2026-07-26
summary: >
  Reference atomic constants for Rb (line frequencies, natural widths,
  polarizabilities).
loci:
  - M4
  - constants
  - methods/02
  - methods/03
section: method-anchors
---

# steck_rb

Held. Verified against the Rb87 sheet.

## The system

Reference atomic constants for Rb: line frequencies, natural linewidths, and polarizabilities. Available online. Both isotope sheets (Rb87 and Rb85) are held as PDFs.

## The numbers

| quantity | D2 (780 nm) | D1 (795 nm) |
|---|---|---|
| lifetime τ | 26.2348(77) ns | 27.679(27) ns |
| natural width Γ | 2π · 6.0666(18) MHz | 2π · 5.7500(56) MHz |
| recoil temperature | 361.96 nK | 348.66 nK |

Saturation intensity: 1.66933(49) mW/cm² = 16.69 W/m² (D2 cycling, circular pump). The sheet also gives 3.5771(10) mW/cm² for an initially uniform F=2 sublevel population. Use whichever value matches the polarization being modeled.

## Validity

Values above are read from the Rb87 sheet. The Rb85 sheet is needed separately because two of the four measured lines in this work are 85Rb, and a per-isotope split of self-broadening coefficients requires matrix elements from both isotopes.
