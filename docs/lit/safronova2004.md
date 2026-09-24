---
citekey: safronova2004
type: article
authors:
  - Safronova, M. S.
  - Williams, Carl J.
  - Clark, Charles W.
title: Relativistic many-body calculations of electric-dipole matrix elements, lifetimes, and polarizabilities in rubidium
journal: Phys. Rev. A
volume: 69
number: 2
pages: 022509
year: 2004
doi: 10.1103/PhysRevA.69.022509
arxiv: physics/0307057
pdf: PDF_papers/Safronova_2004_Rb-matrix-elements-lifetimes-polarizabilities.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/safronova2004_extension.md  # p. 6 (the ionic-core polarizability paragraph, Sec. IV) read and added with its page, 2026-09-22, extending a prior stub that carried no verify_flags or verified_date
author: agent
routing: []
verify_flags:
  - 'Page 6 (Sec. IV, "Polarizabilities") read on 2026-09-22 (pdftotext -layout
    extraction, single-column layout, corroborated against the 150 dpi
    rendered page image since the paragraph carries a0^3 superscripts and a
    bracketed-reference accuracy attribution). Carries Eq. 5 (the valence ac
    polarizability formula), the core-polarizability paragraph quoted below,
    Fig. 1 and its caption, and the start of the Rydberg-state polarizability
    discussion. The rest of the paper (pp. 1-5, 7-8) is unread. This citekey
    was a stub before this pass, with no verify_flags and no verified_date.'
verified_date: 2026-09-22
summary: >
  Benchmark Rb ns matrix elements/lifetimes/polarizabilities — carries
  the 6S dynamic polarizability. P. 6 gives the Rb+ ionic-core polarizability,
  9.1 a0^3 in the random-phase approximation, with its accuracy "estimated to
  be 5%" attributed to Safronova, Johnson and Derevianko, Phys. Rev. A 60,
  4476 (1999) (their ref. [3], not separately held in this record), against a
  `DHF` value of 9.3 a0^3 and Johansson's 9.0 a0^3 from Rydberg term values.
loci:
  - M16
  - THEORY
section: method-anchors
---

# safronova2004

VERIFIED for page 6 (Sec. IV, "Polarizabilities"), read on 2026-09-22. REPORTED
for the rest: benchmark Rb ns matrix elements, lifetimes, and polarizabilities,
including the 6S dynamic polarizability. The stronger Delta\_alpha anchor for 6S.

## What page 6 gives, verbatim

The core contribution to the polarizability, the quantity the search asked
for: the paper's own `DHF` calculation gives 9.3 a0^3 for Rb, weakly dependent
on omega in the frequency range considered there, and its RPA calculation
gives 9.1 a0^3, close to the 9.0 a0^3 Johansson obtained from analysis of the
observed term values of nonpenetrating Rydberg states (p. 6, `[18]`). The
sentence carrying the accuracy figure the search asked for, verbatim: "The
accuracy of the RPA approximation for the core polarizability is estimated to
be 5 % in Ref. [3]. We use the RPA value for the core polarizability of Rb+
as a baseline, and adjust it to account for valence electron (using Eq.(5)
with n' = 2, 3, 4) and the frequency dependence by using DHF calculations.
The RPA and DHF values differ by only 2 %." The valence correction to the
core polarizability is small too, -0.3a0^3 for the 5s state in the `DHF`
approximation (p. 6, same paragraph).

Ref. [3], resolved on p. 8's reference list: "M. S. Safronova, W. R. Johnson,
and A. Derevianko, Phys. Rev. A 60, 4476 (1999)." Refs [16, 17] (the RPA
calculation itself, not the 5% accuracy estimate, which is [3]'s alone) are
"A. Derevianko, W. R. Johnson, M. S. Safronova, and J. F. Babb, Phys. Rev.
Lett. 82, 3589 (1999)" and "W. R. Johnson, D. Kolb, and K.-N. Huang, At. Data
Nucl. Data Tables 28, 333 (1983)."

Three distinct numbers for the same Rb+ core polarizability appear on this
page and must not be conflated: 9.3 a0^3 (this paper's own `DHF` calculation),
9.1 a0^3 (this paper's own RPA calculation, refs [16, 17], the one carrying
the "5 %" accuracy claim via ref. [3]), and 9.0 a0^3 (Johansson's
Rydberg-term-value inference, ref. [18], cited only as an external
cross-check, with no accuracy figure attached to it here).

## Use in this record

Sec. IV (Polarizabilities) opens with Eq. 5, the valence part of the ac
polarizability of an ns state, a sum over the (E_n'p - E_ns) energy
denominators and the squared 5s-5p dipole matrix elements, and states that ω
"is assumed to be at least several linewidths off resonance with the
corresponding transition." This paper's own total polarizability for an ns
state is this valence sum plus the small ionic-core term the paragraph above
gives (9.1 a0^3, 5% RPA-accuracy, adjusted by a DHF-calculated valence and
frequency correction that differs from RPA by only 2%). `docs/LITERATURE_INDEX.md`
already tags this citekey `M16, THEORY` as a source `rb5s6s/polarizability.py`
draws on for the record's own 6S dynamic polarizability, but which of this
paper's numbers (the core term read here, or the valence matrix elements
elsewhere in the paper) the code actually imports was not checked against
the source in this pass.
