---
citekey: hamilton2023
type: article
authors:
  - Hamilton, R.
  - Roberts, B. M.
  - Scholten, S. K.
  - Locke, C.
  - Luiten, A. N.
  - Ginges, J. S. M.
  - Perrella, C.
title: 'Experimental and theoretical study of dynamic polarizabilities in the 5S₁/₂–5D₅/₂ clock transition in rubidium-87 and determination of E1 matrix elements'
journal: Phys. Rev. Applied
volume: 19
number: 5
pages: '054059'
year: 2023
doi: 10.1103/PhysRevApplied.19.054059
arxiv: 2212.10743
pdf: PDF_papers/Hamilton_2023_dynamic-polarizabilities-5S-5D-clock-Rb87.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'The journal, volume, article number and DOI were read from the held PDF's
    own header line on 2026-09-18 (Phys. Rev. Applied 19, 054059, DOI
    10.1103/PhysRevApplied.19.054059), replacing a bare "Phys. Rev. A" and a null
    DOI that had stood since the note was written. The issue number is 5, printed directly in
    the PDF''s own page-1 footer line (2331-7019/23/19(5)/054059(10)), a journal line and not
    an inference from the article number.'
  - 'Pages 1 and 2 of PDF_papers/Hamilton_2023_dynamic-polarizabilities-5S-5D-clock-Rb87.pdf
    (the published Phys. Rev. Applied typeset PDF, 10 pages, matching the
    footer count "054059(10)") read against the record on 2026-09-20. The
    pdf: path above now names this file instead of
    PDF_papers/Hamilton_2023_Rb-5D-dynamic-polarizability-E1-elements.pdf
    (the arXiv:2212.10743v1 preprint, 9 pages), which held the same paper
    under a second, separately downloaded filename -- confirmed by an
    identical title, author list, abstract and headline results on its own
    pages 1-2. Both files remain on disk. Only the published one is named in
    pdf: now.'
verified_date: null
summary: >
  Rigor template for the polarizability side (+ magic-lambda idea).
loci:
  - M16
  - P1
  - THEORY
section: method-anchors
---

# hamilton2023

VERIFIED.

## The system and method

A retro-reflected two-photon transition in Rb-87 vapor, 5S₁/₂→5D₅/₂, driven by two colors (780 and 776 nm) through the near-resonant 5P₃/₂ intermediate state, distinct from the degenerate single-color transition at 993 nm (5S→6S) this repository studies. The signal is the two-color product I(r)_780 × I(r)_776, integrated over the transverse beam profile as F(Δ) = ∫ F(Δ,r) r dr with the cylindrical Jacobian. The paper reduces this integral to a single spatially averaged shift, related to the peak differential polarizability Δα by a factor of about 3.6, and does not retain the shift distribution. Axial standing-wave fringes are not treated: the average is over the transverse profile only.

The drive lasers are 1552 nm and 1560 nm fibre lasers, combined, amplified through an erbium-doped fibre amplifier, and frequency-doubled to 776 nm and 780 nm, so the light originates as telecom-band fibre-laser light, not from free-running diode or Ti:sapphire sources.

## The numbers

A magic wavelength of 776.179(5) nm (experimental) and 776.21 nm (theoretical) is reported near the 5P₃/₂-5D₅/₂ resonance, together with the reduced E1 matrix element for that transition: 1.80(6) ea₀ (experimental, from the light-shift measurement) and 1.96(15) ea₀ (theoretical, from the group's all-order many-body calculation). The paper states these values resolve a prior discrepancy between an earlier theoretical determination and an earlier experimental determination of the same matrix element.

## Use in this record

The closed-form wedge distribution, f(s) ∝ |s|, and its third moment are absent from this reduction. The reported magic wavelength is the target of a proposed Ti:Sapphire asymmetry scan (`FUTURE_TRANSITIONS_titsapph.md`).
