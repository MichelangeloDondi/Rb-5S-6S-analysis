---
citekey: leonard2015
type: article
authors:
  - Leonard, R. H.
  - Fallon, A. J.
  - Sackett, C. A.
  - Safronova, M. S.
title: 'High-precision measurements of the 87Rb D-line tune-out wavelength'
journal: Phys. Rev. A
volume: 92
number: 5
pages: 052501
year: 2015
doi: 10.1103/PhysRevA.92.052501
arxiv: null
pdf: PDF_papers/Leonard_2015_Rb87-D-line-tune-out-wavelength.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags: []
verified_date: 2026-09-10
summary: >
  A condensate interferometer puts the 87Rb tune-out wavelength at
  790.032388(32) nm and turns it into a matrix-element RATIO measured to
  fifteen parts per million. Tested against this record's own adopted 5S
  elements the ratio agrees at 0.93 sigma, and it is 146 times tighter
  than they are, so with Volz fixing the two magnitudes the 5S pair
  becomes over-determined and consistent.
loci:
  - constants
section: method-anchors
---
# leonard2015

Held, seven pages, checked against the PDF.

## What they measure

From the abstract, verbatim: "The wavelength lies between the D1 and D2
spectral lines at 790.032388(32) nm. The measurement is sensitive to the
tensor contribution to the polarizability, which has been removed so that the
reported value is the zero of the scalar polarizability. The precision is 50
times better than previous tune-out wavelength measurements."

And the quantity that matters here, verbatim: "Our result can be used to
determine the ratio of matrix elements" giving `1.99221(3)`, described as "a
100-fold improvement over previous experimental values".

## The test it gives this record, and the result

The tune-out sits where the scalar polarizability of 5S crosses zero, which
depends on the two D-line elements only through their ratio. So this is a
direct check on `polarizability.LINES_5S`:

| | value |
|---|---|
| this record's elements | 4.231(3) and 5.978(5) a.u. |
| their squared ratio | 1.99630 +- 0.00438 |
| Leonard measured | 1.99221(3) |
| agreement | **0.93 sigma**, a fractional difference of +0.205 per cent |

**And it is 146 times more precise than the record's own ratio.** Taken with
[volz1996](volz1996.md), which fixes the two lifetimes and therefore both
magnitudes, the 5S side is now over-determined: two lifetimes and one ratio
for two elements, mutually consistent. That is a stronger statement than
either check alone, and neither was available to this record before both
papers were held.

## What it does not settle

Nothing on the 6S side, where the record has one lifetime for two elements and
the ratio remains free. The tensor removal is theirs and is taken as stated.
