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

The critically-evaluated Rb ns/np/nd matrix elements and scalar/tensor static
polarizabilities, the lineage this programme's polarizability elements descend
from, and an independent check on the M16 static values.

**Held and read in full.** What it contains, and the limits of what it can
settle here:

**Reduced E1 matrix elements** (Table II, "recommended values", atomic units),
the four 6S channels that dominate the 6S polarizability sum plus the two 5S
ones, each with its quoted uncertainty:

| transition | value | unc. |
|---|---|---|
| 6s(1/2)-5p(1/2) | 4.145(10) | 0.23% |
| 6s(1/2)-5p(3/2) | 6.047(13) | 0.21% |
| 6s(1/2)-6p(1/2) | 9.721(24) | 0.25% |
| 6s(1/2)-6p(3/2) | 13.647(34) | 0.25% |
| 5s(1/2)-5p(1/2) | 4.253(34) | 0.79% |
| 5s(1/2)-5p(3/2) | 6.003(24) | 0.80% |

Table I supplies the matching level energies, both their own and the NIST
values, so the sum-over-states denominators come from the same document.

**Static polarizabilities.** alpha(5s) = 322(4) a0^3 (Table V), against the
measured 319(6) and 329(23) they compare to. alpha_0(6s) = 5169(21) a0^3
(Table VI). Ionic core alpha_core = 9.076 a0^3.

That 6S value is a useful independent check rather than a duplicate.
`polarizability.py` calibrates its 6S tail to 5167(22), taken from the
Safronova-group online portal, and the paper's own Table VI gives 5169(21).
The two agree to 0.04%, well inside either uncertainty, so the tail
calibration is confirmed against the published table and not only against the
portal it was read from.

**What it cannot do, and this is the point for M16.** Every polarizability in
it is STATIC. There is no frequency-dependent formula anywhere in the paper,
so it cannot give Delta_alpha at 993 nm on its own, and it cannot be used to
adjudicate the sign disagreement with [orson2021](orson2021.md): it never
writes a light-shift equation, so it never states whether a positive alpha
pulls a level down. The dynamic evaluation belongs to
[safronova2006](safronova2006.md), which is the frequency-dependent paper and
is also held.

So its role here is inputs and anchors rather than an answer: matrix elements
and energies to feed a dynamic recompute, and static totals that such a
recompute must reproduce in the zero-frequency limit.
