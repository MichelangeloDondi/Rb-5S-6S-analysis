---
citekey: steck_rb
type: misc
authors:
  - Steck, Daniel A.
title: 'Rubidium 85 and 87 {D} Line Data'
journal: 'available online at \url{https://steck.us/alkalidata}'
doi: null
arxiv: null
pdf: PDF_papers/Steck_Rb87_D-line-data.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'Rb85 and Rb87 sheets both held; values below read from the Rb87 sheet 2026-07-26.'
verified_date: null
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

Reference atomic constants for Rb (line frequencies, natural widths, polarizabilities). No PDF held — standard online ref.

**Constants read from the held Rb87 sheet (2026-07-26).** Recorded so the next
calculation cites rather than re-derives them:

| quantity | D2 (780 nm) | D1 (795 nm) |
|---|---|---|
| lifetime τ | 26.2348(77) ns | 27.679(27) ns |
| natural width Γ | 2π · 6.0666(18) MHz | 2π · 5.7500(56) MHz |
| recoil temperature | 361.96 nK | 348.66 nK |

Saturation intensity: **1.66933(49) mW/cm² = 16.69 W/m²** (D2 cycling, circular
pump; the sheet also gives 3.5771(10) mW/cm² for an initially uniform F=2
sublevel population — use the one matching the polarisation being modelled).

These are what the guided-platform probe-scattering estimate uses (private
planning note). An earlier version of that estimate flagged them as coming from
outside the repo and needing sourcing; that was wrong — both Steck sheets were
already in `PDF_papers/`, and the values used match this sheet exactly.

**Both isotope tables are held**, not just the one the `pdf:` field can name:
`Steck_Rb87_D-line-data.pdf` and `Steck_Rb85_D-line-data.pdf`. The 85 tables
matter here because two of the four measured lines are 85Rb, and the
per-isotope beta_self split (M4b) needs both sets of matrix elements.
