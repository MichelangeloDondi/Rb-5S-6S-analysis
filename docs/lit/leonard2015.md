---
citekey: leonard2015
type: article
authors:
  - Leonard, R. H.
  - Fallon, A. J.
  - Sackett, C. A.
  - Safronova, M. S.
title: 'High precision measurement of the 87Rb D-line tune-out wavelength'
journal: Phys. Rev. A
volume: 92
pages: 052501
year: 2015
doi: 10.1103/PhysRevA.92.052501
arxiv: '1507.07898'
pdf: PDF_papers/Leonard_2015_Rb87-D-line-tune-out-wavelength.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'THE 2017 ERRATUM IS NOW HELD AND READ -- see leonard2017, whose PDF is
    PDF_papers/Leonard_2017_ERRATUM_Rb87-D-line-tune-out-wavelength.pdf (it was
    held under the bare APS filename PhysRevA.95.059901.pdf and renamed
    2026-07-31). It REPLACES this paper''s headline. The
    tune-out becomes 790.032326(32) nm, the ratio R = 1.99217(3), and theory
    790.0315(7). Quote the ERRATUM values, not this paper''s. The erratum is not
    on arXiv -- the arXiv record (1507.07898) is pre-erratum through v3 -- which
    is why this stood unverified until the PDF was obtained.'
  - 'This paper reports FIVE different wavelengths and they are easy to confuse:
    the headline 790.032388(32) (abstract; the constrained fit, given as
    790.032388(29) in the text), the unconstrained fit 790.032439(35), a raw
    regression intercept 790.03232, and theory 790.0312(7) and 790.02568.
    Quote the headline unless a specific fit is meant.'
verified_date: 2026-07-31
summary: >
  The source of three things rb5s6s/polarizability.py depends on, and it had no
  note until 2026-07-31 despite that. (1) The 5S scalar tune-out validation
  anchor -- measured with a BEC interferometer to fifty times better than
  previous work, and reported here as 790.032388(32) nm but CORRECTED BY THE
  2017 ERRATUM TO 790.032326(32), which is the value the repo now uses.
  (2) TAIL_5S = 0.097, which is Leonard's Table II
  (n>12) tails, 0.022(22) for P_1/2 plus 0.075(75) for P_3/2 -- both verified
  against the held PDF. (3) CORE_5S = 8.709(93), their "Core + vc" row, also
  verified. Also gives the matrix-element ratio |<5P3/2||d||5S1/2> /
  <5P1/2||d||5S1/2>|^2 = 1.99221(3) -- ALSO REPLACED, the erratum making it
  1.99217(3) -- a 100-fold improvement on previous experiment, and the 5P-12P
  energies the module uses. A further erratum result worth keeping: the
  apparent conflict with Lamporesi et al.'s 790.018(2) nm is not a discrepancy
  but a different ground state (theirs F=1); carried to F=1 this measurement
  gives 790.017496(32) against a 790.0167(7) theory, and they agree.
loci:
  - M16
  - THEORY
  - constants
section: method-anchors
---

# leonard2015

Held. Relevant sections verified against the held arXiv PDF (1507.07898).
The headline tune-out value is superseded by the 2017 erratum (see
[leonard2017](leonard2017.md)).

## The system

A Bose-Einstein-condensate atom interferometer measurement of the 87Rb
D-line tune-out wavelength, the wavelength at which the scalar
polarizabilities of the 5S ground state from the D1 and D2 lines cancel,
improving on prior measurements by a factor of fifty.

## The numbers

The paper reports five wavelengths. The headline value, from the
abstract's constrained fit, is 790.032388(32) nm (790.032388(29) nm in
the text). An unconstrained fit gives 790.032439(35) nm, a raw regression
intercept gives 790.03232 nm, and two theoretical values are given,
790.0312(7) nm and 790.02568 nm. The headline value is corrected by the
2017 erratum to 790.032326(32) nm (see [leonard2017](leonard2017.md)).

The matrix-element ratio |<5P3/2||d||5S1/2>|^2 / |<5P1/2||d||5S1/2>|^2 is
given as 1.99221(3), a hundredfold improvement on the previous
experimental value, corrected by the erratum to 1.99217(3).

## Quantities used in this analysis

| quantity | Leonard source | value |
|---|---|---|
| tune-out anchor | abstract, constrained fit | 790.032388(32) nm, superseded by the erratum's 790.032326(32) nm |
| TAIL_5S | Table II, (n>12) tails | 0.022(22) for P1/2 plus 0.075(75) for P3/2, summing to 0.097 |
| CORE_5S | Table II, "Core + vc" row | 8.709(93) |
| 5P–12P energies | Table II | as tabulated |

Both tail entries carry an uncertainty equal to their own value, a ±100%
uncertainty that is Leonard's own.

## Use in this record

The tune-out anchor used elsewhere in this analysis is the 2017 erratum's
corrected value, 790.032326(32) nm, rather than this paper's original
790.032388(32) nm. The computed tune-out (790.0339 nm) sits 1.57 pm from
the corrected anchor, about twenty-five times larger than the 0.062 pm
shift the erratum introduces, so the choice between the two published
values changes no conclusion. TAIL_5S and CORE_5S are taken from this
paper's theoretical decomposition table and not from the measured
tune-out and are not affected by the erratum's correction to the
measurement analysis, though the paper does not state this explicitly
and the table itself was not re-derived after the erratum.
