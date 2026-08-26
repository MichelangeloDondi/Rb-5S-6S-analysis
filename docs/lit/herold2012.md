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

REPORTED. Not held. Bibliographic record confirmed from the publisher listing
and two independent indexes. Content not verified against the paper.

## The method

The atomic ground-state light shift passes through zero near 421 nm and
423 nm. At each such zero the ratio of the two contributing matrix elements
is fixed by the wavelength alone, turning a matrix-element measurement into
a wavelength measurement.

## The numbers

Reduced dipole matrix elements for 5S to 6P: 0.3235(9) ea0 (5s-6p1/2) and
0.5230(8) ea0 (5s-6p3/2), quoted from the `rb5s6s/polarizability.py`
docstring, the source of record until the PDF is held.

## Use in this record

`rb5s6s/polarizability.py` builds the 5S and 6S dynamic polarizabilities
from a sum over states. The 5S-6P group is one of the two large opposing
terms setting the 993 nm polarizability difference, so its uncertainty
propagates directly into every magic wavelength computed for that
transition.
