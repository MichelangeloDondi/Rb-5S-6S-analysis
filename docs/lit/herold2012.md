---
citekey: herold2012
type: article
authors:
  - Herold, C. D.
  - Vaidya, V. D.
  - Li, X.
  - Rolston, S. L.
  - Porto, J. V.
  - Safronova, M. S.
title: 'Precision Measurement of Transition Matrix Elements via Light Shift Cancellation'
journal: Phys. Rev. Lett.
volume: 109
number: 24
pages: 243003
year: 2012
doi: 10.1103/PhysRevLett.109.243003
arxiv: null
pdf: null
held: false
status: REPORTED
routing:
  - FEED
verify_flags:
  - 'Record confirmed on 2026-08-05 from the publisher listing and two
    independent indexes, not from the paper. Nobody here has read it. The two
    matrix elements below are quoted from the module docstring of
    rb5s6s/polarizability.py, which is the source of record in this repository
    until the PDF is held.'
verified_date: null
summary: >
  Source of the 5S to 6P reduced dipole matrix elements
  rb5s6s/polarizability.py uses, 0.3235(9) and 0.5230(8) ea0 for 5s-6p1/2 and
  5s-6p3/2. Measured by locating the magic zeros of the light shift near 421 and
  423 nm, where the shift vanishes and the ratio of the contributing matrix
  elements is fixed by that condition alone. The 6P group is one of the two
  large opposing terms in the 993 nm polarizability difference, so its
  uncertainty propagates directly into Delta alpha and into every magic
  wavelength M16 reports.
loci:
  - constants
  - M16
  - THEORY
section: method-anchors
---

# herold2012

**REPORTED. The record is confirmed, the paper is not held and has not been read
here.**

## Why this repository needs it

`rb5s6s/polarizability.py` builds the 5S and 6S dynamic polarizabilities from a
sum over states. Its 5S to 6P entry, 0.3235(9) and 0.5230(8) ea0 for the two
fine-structure components, comes from this measurement. That group is one of the
two large terms whose near-cancellation sets the 993 nm difference, so an error
in it does not average away.

The method is worth one line for the reader who meets it in the sum: the light
shift of the ground state passes through zero at particular wavelengths, near
421 and 423 nm here, and at such a zero the ratio of the matrix elements feeding
the shift is fixed by the wavelength alone. That turns a matrix-element
measurement into a wavelength measurement, which is the same move this
programme's magic-wavelength work in M16 makes on the 5S to 6S pair.

## What is missing

The paper has not been obtained, so nothing beyond the two matrix elements and
the method may be attributed to it. Upgrading this note means holding the PDF,
reading the uncertainty budget, and checking that the values in
`polarizability.py` carry the same convention as the ones printed there.
