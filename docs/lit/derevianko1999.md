---
citekey: derevianko1999
type: article
authors:
  - Derevianko, A.
  - Johnson, W. R.
  - Safronova, M. S.
  - Babb, J. F.
title: 'High-Precision Calculations of Dispersion Coefficients, Static Dipole Polarizabilities, and Atom-Wall Interaction Constants for Alkali-Metal Atoms'
journal: Phys. Rev. Lett.
volume: 82
number: 18
pages: 3589-3592
year: 1999
doi: 10.1103/PhysRevLett.82.3589
arxiv: null
pdf: PDF_papers/Derevianko_1999_dispersion-coefficients-polarizabilities-atom-wall-alkali.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags:
  - 'No DOI is printed on the letter. The APS pattern for this volume and page
    gives 10.1103/PhysRevLett.82.3589. Volume 82, number 18, the date 3 May 1999
    and the page range are all printed on the running heads and in the footer
    line 0031-9007/99/82(18)/3589(4).'
verified_date: 2026-09-18
loci:
  - constants
  - THEORY
  - P2
section: method-anchors
summary: >
  The source of the 4691 this record carries for the ground-state rubidium pair,
  and the reason this record's valence-only sums fail on the dispersion
  coefficient while succeeding on the polarizability. Its Table I tabulates what
  fraction of each quantity survives when core excitations are dropped, and those
  fractions reproduce both of this module's shortfalls to three digits.
---
# derevianko1999

Held, four journal pages, read in full on 2026-09-18 against
`PDF_papers/Derevianko_1999_dispersion-coefficients-polarizabilities-atom-wall-alkali.pdf`.

## What it covers

Van der Waals coefficients for the ground-state alkali dimers from sodium to
francium, by relativistic ab initio methods. The accuracy of the wave functions
is tested by computing two further quantities from the same dynamic
polarizability: the static electric-dipole polarizability and the constant for
the interaction of the atom with a perfectly conducting wall (abstract, p. 3589).
The polarizability is split into three parts, a valence term, a core
polarizability and a valence-core coupling term, and two methods are carried
through every table: method I takes measured matrix elements for the principal
transition, method II takes all-order single-double values instead (p. 3590).

## The numbers, each with its table

1. **The dispersion coefficient, Table IV.** For rubidium 4691(23) by method I
   and 4628 by method II, against 4768, 4531 and 4426 from Refs. [19], [18]
   and [17].
2. **What measurement says, Table IV and p. 3592.** Photoassociation limits the
   rubidium coefficient to 4400-4900, and a Feshbach resonance in elastic
   collisions of the 85 isotope gives 4700(50). The letter's own words are "Our
   result C6 = 4691(23) is in excellent agreement with this experiment."
3. **The static polarizability, Table II.** Rubidium 318.6(6) by method I, 316.4
   by method II, against a weighted experimental average of 319.9(6.1) from
   Refs. [14,15].
4. **The atom-wall constant, Table III.** Rubidium 3.426 by integrating the
   dynamic polarizability (Eq. 3) and 3.410 by the all-order variant, with 3.362
   from the expectation value of the squared radius (Eq. 4). The text puts the
   agreement of the two routes at one per cent for rubidium (p. 3591).
5. **Table I, the core fractions, which is the part this record needs most.**
   Dropping core excitations leaves, for rubidium, 0.97 of the static
   polarizability, 0.65 of the atom-wall constant and 0.89 of the dispersion
   coefficient. The point of the table is that the core matters more for the
   heavier atoms, and more for the wall constant than for the polarizability.
6. **The error budget, p. 3590.** Five per cent assumed on the core
   polarizabilities and ten per cent on the remaining contributions to the static
   polarizability. The dispersion coefficient's error comes from the accuracy of
   the measured principal-transition elements, plus the core error scaled from
   the wall constant to the dispersion coefficient through Table I.

## Validity

A letter, so the methods are named and not set out, and the uncertainties are
estimated from the two assumed percentages of item 6 and not propagated. What
supports them is that only two of the three quantities computed from one polarizability
function land on their measured values, the dispersion coefficient on the Feshbach
result and the polarizability on the experimental average. **The wall constant has
no measurement in the letter at all**: Table III carries no experimental column,
and its check is the agreement of two computational routes, the integral of
Eq. (3) against the expectation value of Eq. (4). A reading that counts three
agreements with measurement is counting one that is not there.

## Use in this record

- **It is the origin of `C6_RB2_GROUND_LIT_AU = 4691.0`.** The constant's
  attribution block used to open on Stewart, which read as though 4691 were his
  measurement. It is the value he tabulates beside his own. The block now names
  this letter.
- **Item 5 explains both of this record's valence-only shortfalls, to three
  digits.** `vanderwaals.py` records that its own machinery gives 4180 against
  the literature 4691, and 4180/4691 = 0.891 against the tabulated 0.89. The same
  module records a valence-only 5S polarizability of 309.5, and 309.5/318.6 =
  0.971 against the tabulated 0.97. Both gaps are the core excitations the module
  does not sum, in the proportions this letter tabulates, and neither is a defect
  in the module. The agreement is a real test rather than a restatement: the ratio
  formed is this record's valence sum over the letter's total, so it equals the
  letter's valence fraction only if the two valence parts agree.
- **It says which quantities the omission spoils.** The core carries three per
  cent of the polarizability and eleven per cent of the dispersion coefficient,
  so a valence-only sum is a good polarizability and a poor dispersion
  coefficient. That asymmetry in this record's own chains needs no further
  explanation.
- **The ground-pair coefficient has three determinations that agree, and their
  inputs are worth naming instead of the word itself.** This letter's
  4691(23) is a calculation fed by measured principal-transition matrix elements
  (Ref. [7]). The 4700(50) is a Feshbach resonance. Stewart, Shen, Booth and
  Madison, Phys. Rev. A 106, 052812 (2022), give 4688(198)(95) from a
  diffractive-collision measurement (no note in this library yet). Disjoint from each other,
  but the first is not a route disjoint from experiment.
- **The atom-wall constant is new to this record.** Nothing under `rb5s6s/`
  carries a surface interaction constant. The module's Casimir-Polder code is
  atom-atom only. The perfectly conducting value for rubidium is 3.426 atomic
  units, which is the starting point a dielectric fibre surface corrects
  downward, and item 5 warns that a valence-only estimate of it would be a third
  too small. That is the fibre arm's entry point, not this record's.

## Open against this letter

- **The denominator 318.8.** `vanderwaals.py` calls 318.8 "the measured" static
  polarizability. This letter gives neither: its experimental weighted average is
  319.9(6.1) and its own method-I value is 318.6(6). The ratio of item 5 is
  unharmed at three digits either way, but the provenance of 318.8 is unnamed in
  this record and is queued as `c6-anchor-audit`.
- **van Kempen 2002.** Phys. Rev. Lett. 88, 093201 give 4703(9) from a molecular
  fit, twenty-two times tighter than this letter, which would make this module's
  truncated sum decisively low instead of in tension. Not held, and nothing moves on
  it until its PDF is read.
