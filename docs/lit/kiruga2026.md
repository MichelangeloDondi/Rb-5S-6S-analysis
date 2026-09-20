---
citekey: kiruga2026
type: article
authors:
  - Kiruga, A.
  - Cheung, C.
  - Filin, D.
  - Barakhshan, P.
  - Bhosale, A.
  - Badhan, V.
  - Arora, B.
  - Eigenmann, R.
  - Safronova, M. S.
title: 'Portal for high-precision atomic data and computation'
journal: Computer Physics Communications
volume: 319
pages: '109951'
year: 2026
doi: 10.1016/j.cpc.2025.109951
arxiv: null
pdf: PDF_papers/Kiruga_2026_portal-high-precision-atomic-data-computation.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 and 2 read against the PDF on 2026-09-20. The uncertainty
    -assessment workflow and the per-element results (most of the paper) are
    not read. The numbers below come from the introduction and the
    transition-rate/lifetime formula section.
  - 2026-09-20: adversarial audit_C corrected two defects. The "28 atoms and ions" figure is
    tied to Version 3 and April 2025 only on p. 2, not p. 1. And the methods sentence had
    asserted CI+all-order for the whole, monovalent-labelled portal, when the paper ties
    coupled-cluster to the monovalent systems and CI+all-order specifically to the divalent
    additions (Mg, Ca, Sr).
verified_date: null
summary: >
  A description of the University of Delaware's open-access online atomic
  -data portal (energies, matrix elements, transition rates, lifetimes,
  branching ratios, hyperfine constants, polarizabilities, magic and
  tune-out wavelengths) for 28 atoms and ions, including neutral Rb,
  computed with the group's relativistic coupled-cluster and CI+all-order
  codes. It reports no new physics result of its own. Its value here is as a
  live, structured, citable data source and cross-check point for Rb atomic
  constants computed with the same all-order method family behind several of
  this repository's other theory anchors.
loci: []
section: method-anchors
---
# kiruga2026

## Values

| field | value | where in the paper |
|---|---|---|
| atoms/ions covered (Version 3, April 2025) | 28 | p. 2 |
| Version 1 (April 2021) coverage | 12 monovalent atoms/ions: Li, Be+, Na, Mg+, K, Ca+, Rb, Sr+, Cs, Ba+, Fr, Ra+ | p. 2 |
| Version 2 (March 2022) addition | energies beyond NIST for 9 of those systems, plus 13 highly charged ions | p. 2 |
| Version 3 addition | neutral Mg, Ca, Sr; polarizability and magic/tune-out wavelength plots | p. 2 |
| portal usage since release | over 5900 users, 95 countries, 14 200 sessions, 88 500 pageviews | p. 2 |
| methods used | relativistic coupled-cluster (all-order); CI+all-order (configuration interaction + coupled cluster) | p. 1 |
| CI+all-order code | published, on GitHub at ud-pci/pCI | p. 1 |
| portal address | udel.edu/atom | p. 1 |

## What it says, in its own terms

The paper documents an online, open-access atomic-data portal, hosted at the
University of Delaware, that publishes precomputed, uncertainty-quantified
atomic properties: energies, E1/E2/E3/M1/M2/M3 transition matrix elements
and rates, radiative lifetimes, branching ratios, hyperfine constants,
quadrupole moments, and scalar and dynamic polarizabilities including magic
and tune-out wavelength plots, for a set of atoms and ions that is mostly
monovalent plus three divalent alkaline-earth atoms (Mg, Ca, Sr) added in
Version 3, computed with the group's own relativistic coupled-cluster
(all-order) method for the monovalent systems and CI+all-order for the
multivalent ones. It records the underlying formulas (the Wigner-Eckart reduction of
multipole matrix elements, the transition-rate and lifetime formulas, and
the scalar/tensor decomposition of the dynamic polarizability, including its
angle dependence on an applied magnetic field) and describes the software
behind the portal itself: a new automated data pipeline and workflow system
replacing an earlier ad hoc setup, with automated comparison of computed
values against the NIST Atomic Spectra Database.

Version 1 (April 2021) covered 12 monovalent atoms and ions, including
neutral Rb. Version 2 (March 2022) added recommended energies beyond the
NIST tabulation plus 13 highly charged ions. Version 3, the release this
paper documents, extends coverage to 28 atoms and ions, adds neutral Mg, Ca
and Sr, and adds polarizability and magic/tune-out wavelength plots to the
interface. By the time of writing, the portal had recorded over 5900 users
from 95 countries.

## What it is worth here

A live, citable, cross-checkable data source for Rb (and other alkali)
energies, matrix elements, lifetimes and polarizabilities, computed with the
same family of all-order methods behind several of this repository's other
theory anchors (the Safronova group's earlier Rb papers among them), rather
than a new physics result in its own right. Its use here would be as a
quick, structured lookup and cross-check point, not as a source this
repository currently draws a number from.
