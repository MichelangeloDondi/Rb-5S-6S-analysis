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

**Table VI in full.** Scalar static polarizabilities of the excited states, a0^3, with the paper's own uncertainties:

| state | alpha_0 | state | alpha_0 |
|---|---|---|---|
| 6s(1/2) | 5169(21) | 4d(3/2) | 574(25) |
| 7s(1/2) | 32630(140) | 4d(5/2) | 541(26) |
| 8s(1/2) | 133200(650) | 5d(3/2) | 17880(160) |
| 9s(1/2) | 417200(2200) | 5d(5/2) | 17500(150) |
| 10s(1/2) | 1094000(6000) | 6d(3/2) | 93900(600) |
| 5p(1/2) | 814(8) | 6d(5/2) | 91580(620) |
| 5p(3/2) | 875(7) | 6p(1/2) | 12420(120) |
| 7p(1/2) | 83270(300) | 6p(3/2) | 13440(70) |
| 7p(3/2) | 90350(270) | | |

**7d is absent from that table**, which is the one rung inside the Ti:Sapph band this paper cannot supply.

Table II gives the reduced E1 matrix elements themselves for the channels behind these, including the full 7s set, 8s to 5p, 6p and 7p, and 4d, 5d, 7d and 8d to 5p, 6p, 7p and 8p, with the d-f channels beside them. Those are what a FREQUENCY-DEPENDENT sum needs.

## Validity

Every polarizability in the paper is static. It contains no frequency-dependent formula, so it cannot give Delta_alpha at 993 nm and cannot settle the sign disagreement with [orson2021](orson2021.md), which turns on a light-shift equation this paper does not write. The frequency-dependent evaluation is in [safronova2006](safronova2006.md).

## Use in this record

`polarizability.py` calibrates its 6S tail to 5167(22) a0^3, taken from the Safronova-group online portal. Table VI here gives 5169(21) a0^3, agreement to 0.04%, confirming the tail calibration against a published table independent of the portal.

**And since 2026-09-10 the module carries Table VI's excited-state column as `STATIC_ALPHA_A011`**, for the rungs of the Ti:Sapph ladder it has no line list for. The reading was cross-checked where both exist: this module's own static sums give 5166.95 for 6s against the table's 5169(21) and 32410.97 for 7s against 32630(140), 0.04 and 0.7 per cent. That agreement is what licenses reading the table for 8s, 9s and the nd states.

**The static caveat above is what governs its use.** These values rank the rungs and close the omega to zero limit of a dynamic sum. They are not the light shift's differential at any drive wavelength, and `results/transition_ladder.csv` keeps its dynamic entries empty until that sum is built.
