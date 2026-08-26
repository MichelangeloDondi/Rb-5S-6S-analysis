---
citekey: safronovaSS2011
type: article
authors:
  - Safronova, M. S.
  - Safronova, U. I.
title: 'Critically evaluated theoretical energies, lifetimes, hyperfine constants, and multipole polarizabilities in ⁸⁷Rb'
journal: Phys. Rev. A
volume: 83
pages: 052508
year: 2011
doi: 10.1103/PhysRevA.83.052508
arxiv: null
pdf: PDF_papers/Safronova_2011_Rb87-energies-lifetimes-multipole-polarizabilities.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags: []
verified_date: 2026-08-02
summary: >
  The critically-evaluated Rb ns/np/nd matrix elements + scalar/tensor
  static polarizabilities (the S and S 2011 lineage our polarizability
  elements descend from), and the independent source to validate the M16
  7S static (~3.2e4 a.u.).
loci:
  - M16
  - THEORY
section: method-anchors
---

# safronovaSS2011

Held. Verified in full against the PDF.

## The system

Critically evaluated theoretical energies, lifetimes, hyperfine constants, and multipole polarizabilities for atomic Rb-87, from relativistic many-body calculations.

## The numbers

Reduced E1 matrix elements (Table II, recommended values, atomic units) for the four 6S channels that dominate the 6S polarizability sum, and the two 5S channels, each with its quoted uncertainty:

| transition | value | unc. |
|---|---|---|
| 6s(1/2)-5p(1/2) | 4.145(10) | 0.23% |
| 6s(1/2)-5p(3/2) | 6.047(13) | 0.21% |
| 6s(1/2)-6p(1/2) | 9.721(24) | 0.25% |
| 6s(1/2)-6p(3/2) | 13.647(34) | 0.25% |
| 5s(1/2)-5p(1/2) | 4.253(34) | 0.79% |
| 5s(1/2)-5p(3/2) | 6.003(24) | 0.80% |

Table I gives the matching level energies, both the paper's own values and the NIST values, so the sum-over-states denominators come from the same document.

Static polarizabilities: alpha(5s) = 322(4) a0^3 (Table V), compared against measured values of 319(6) and 329(23). alpha_0(6s) = 5169(21) a0^3 (Table VI). Ionic core alpha_core = 9.076 a0^3.

## Validity

Every polarizability in the paper is static. It contains no frequency-dependent formula, so it cannot give Delta_alpha at 993 nm and cannot settle the sign disagreement with [orson2021](orson2021.md), which turns on a light-shift equation this paper does not write. The frequency-dependent evaluation is in [safronova2006](safronova2006.md).

## Use in this record

`polarizability.py` calibrates its 6S tail to 5167(22) a0^3, taken from the Safronova-group online portal. Table VI here gives 5169(21) a0^3, agreement to 0.04%, confirming the tail calibration against a published table independent of the portal.
