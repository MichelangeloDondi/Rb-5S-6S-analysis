---
citekey: sherman2008
type: article
authors:
  - Sherman, J. A.
  - Andalkar, A.
  - Nagourney, W.
  - Fortson, E. N.
title: 'Precision measurement of light shifts at two off-resonant wavelengths in a single trapped Ba+ ion and the determination of atomic dipole matrix elements'
journal: Phys. Rev. A
volume: 78
pages: 052514
year: 2008
doi: 10.1103/PhysRevA.78.052514
arxiv: '0808.1826'
pdf: PDF_papers/Sherman_2008_light-shift-ratio-two-wavelengths-Ba-ion.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Page 1 read against the PDF on 2026-09-20 (title, abstract, Fig. 1 level diagram, and the
    opening of the introduction and theory sections). The measurement and analysis sections
    are not read.
  - The held PDF is the arXiv v1 preprint (arXiv:0808.1826v1, posted 13 Aug 2008) and prints no
    journal reference or DOI on the page read. The journal, volume, page and DOI above are the
    published record, confirmed via the APS journals listing (journals.aps.org) on 2026-09-20:
    Phys. Rev. A 78, 052514 (2008).
  - 2026-09-20: adversarial audit_F corrected the Fig. 1 diagram reading. A pixel-level render
    at 200-600 dpi shows the branching and lifetime pairs were transposed between the two 6P
    fine-structure levels. 6P3/2 carries the shorter lifetime (about 6 ns) and the 74%/3%/23%
    branching, 6P1/2 the longer lifetime (about 8 ns) and the 73%/27% branching, not the reverse.
verified_date: null
summary: >
  A University of Washington precision measurement of the ratio of vector AC-Stark (light)
  shifts between the 6S1/2 and 5D3/2 states of a single trapped Ba+ ion, at two off-resonant
  wavelengths, used to pin down a previously unmeasured atomic dipole matrix element. The
  method's core idea, measuring a ratio of light shifts simultaneously in two states rather
  than a single shift, cancels the need to know or control the driving laser's intensity, a
  common-mode-rejection strategy this record's own AC-Stark work does not use but could
  compare against conceptually. The species, transition and physical quantity are all
  different from this record's Rb 5S-6S line, so nothing here transfers numerically.
loci: []
section: prior-art
---
# sherman2008

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | University of Washington, Department of Physics | p. 1 |
| light-shift ratio at 514.531 nm (earlier work, restated here) | R = ΔS/ΔD = -11.494(13) | p. 1, abstract |
| light-shift ratio at 1111.68 nm (this paper's new measurement) | R = +0.4176(8) | p. 1, abstract |
| stated accuracy | 0.2% | p. 1, abstract |
| light-shift formula (two-level, first order) | ΔE(1,2) = ± ħΩ^2 / (4δ) | p. 1, Eq. (1) |
| decay branching, 6P1/2 to 6S1/2 / 5D3/2 | 73% / 27% | p. 1, Fig. 1 |
| decay branching, 6P3/2 to 6S1/2 / 5D3/2 / 5D5/2 | 74% / 3% / 23% | p. 1, Fig. 1 |
| state lifetimes shown | 6P3/2 about 6 ns; 6P1/2 about 8 ns; 5D3/2 about 80 s; 5D5/2 about 32 s | p. 1, Fig. 1 |

## What it says, in its own terms

**The problem.** Among the low-lying Ba+ electric-dipole transitions, only ⟨6S\|\|er\|\|6P⟩ had
been measured to about 1% at the time of writing. ⟨5D\|\|er\|\|4F⟩ was unknown (p. 1). Precise
matrix elements are needed to test modern many-body atomic theory in this alkali-like ion and
to interpret proposed atomic-parity-violation measurements in Ba+ and Ra+.

**The method.** An off-resonant light beam shifts the Zeeman sublevels of the 6S1/2 and
5D3/2 states through the vector AC-Stark effect. Rather than measure either shift absolutely,
which requires precise knowledge of the beam intensity at the ion, the paper measures the
ratio R = ΔS/ΔD of the two simultaneously-measured shifts. Because both states see the same
beam, the ratio is independent of the laser intensity, and by choosing the off-resonant
wavelength the technique can be tuned to target a specific, otherwise weakly-constrained
matrix element. The paper states this generalizes to other atoms and ions with a convenient
metastable state.

**The result.** Combining the newly measured R = +0.4176(8) at 1111.68 nm with the previously
reported R = -11.494(13) at 514.531 nm yields the previously unknown ⟨5D\|\|er\|\|4F⟩ matrix
element. The paper frames the outcome as both a test of ab initio coupled-cluster calculations
and, more broadly, input toward the atomic theory needed for the proposed parity-violation
programme in Ba+ and Ra+.

## What it is worth here

Marginal directly, useful as a methodological contrast. The species (Ba+, a trapped ion), the
transitions (6S1/2-5D3/2 vector light shifts at two off-resonant IR/visible wavelengths) and
the quantity extracted (an unknown E1 matrix element) are all unrelated to this record's Rb
5S-6S two-photon vapour-cell line, so no number here is usable. The transferable piece is the
strategy: a ratio of two simultaneously measured light shifts cancels an intensity-calibration
systematic that would otherwise dominate, which is the same class of common-mode-rejection
idea behind the zero-crossing measurements already held in this list's prior-art section
(chanu2020, jayjong2026) for the same broad trapped-ion light-shift lineage. This record's own
method extracts a shift distribution rather than cancelling the shift, so the relationship is
one of contrast (a precedent for what a light-shift measurement can look like when the shift
itself is the nuisance) rather than of shared technique.
