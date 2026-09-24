---
citekey: arora2007
type: article
authors:
  - Arora, Bindiya
  - Safronova, M. S.
  - Clark, Charles W.
title: 'Magic wavelengths for the np-ns transitions in alkali-metal atoms'
journal: Phys. Rev. A
volume: 76
pages: 052509
year: 2007
doi: 10.1103/PhysRevA.76.052509
arxiv: '0709.0130'
pdf: PDF_papers/Arora_2007_magic-wavelengths-nP-nS-transitions-alkali-metal-atoms.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/arora2007.md  # restored a dropped clause in the `verbatim` abstract quote; flagged (not asserted) a closer core-polarizability link to this record's own code than `no reusable number` states; struck two frontmatter/body quote marks that were never the paper's own words (2026-09-22, lit-quotes repair)
author: agent
routing: []
verify_flags:
  - 'Page 1 of the held arXiv:0709.0130v1 preprint (title, authors,
    affiliations, complete abstract, and the opening two paragraphs of the
    introduction) read against the record on 2026-09-21. The body, including
    the per-species tables of scalar/tensor ac polarizabilities and the
    computed magic wavelengths themselves, is unread.'
  - 'Table I on p. 2 (Rb 5p3/2 scalar/tensor polarizability contributions at
    790 nm, specifically its `alpha_core 9.1(5)` row) was read on 2026-09-22,
    during the line-by-line audit, solely to check whether `Arora et al.
    2007` as cited in `rb5s6s/polarizability.py`''s docstring for the 6S
    ionic-core polarizability could be this paper; the rest of the body,
    including the full per-species magic-wavelength tables, remains unread.'
verified_date: 2026-09-21
summary: >
  Relativistic all-order (coupled-cluster) calculation of magic wavelengths
  in Na, K, Rb and Cs for which the ns ground state and the np1/2 or np3/2
  excited state share the same ac Stark shift, from electric-dipole matrix
  elements computed with stated uncertainties. Companion paper to the
  already-held arora2012 and safronova2006/goldschmidt2015, and the specific
  nP-nS magic-wavelength calculation the search priority asked for.
loci: []
section: method-anchors
---

# arora2007

VERIFIED for page 1 (title, authors, affiliations, abstract, opening
introduction). REPORTED beyond that: the actual computed magic wavelengths
and the polarizability tables for Rb specifically are unread.

## What page 1 gives, verbatim

"Extensive calculations of the electric-dipole matrix elements in
alkali-metal atoms are conducted using the relativistic all-order method.
This approach is a linearized version of the coupled-cluster method, which
sums infinite sets of many-body perturbation theory terms. All allowed
transitions between the lowest ns, np1/2, np3/2 states and a large number of
excited states are considered in these calculations and their accuracy is
evaluated. The resulting electric-dipole matrix elements are used for the
high-precision calculation of frequency-dependent polarizabilities of the
excited states of alkali-metal atoms. We find "magic" wavelengths in
alkali-metal atoms for which the ns and np1/2 and np3/2 atomic levels have the
same ac Stark shifts, which facilitates state-insensitive optical cooling and
trapping."

Its own framing of the method, verbatim: "We accomplish this by matching the
ac polarizabilities of the atomic ns and npj states. We conduct extensive
calculations of the relevant electric-dipole matrix elements using the
relativistic all-order method and evaluate the uncertainties of the resulting
ac polarizabilities."

## Use in this record

Same author pair (Arora, Safronova) and the same coupled-cluster / relativistic
all-order machinery as the already-held arora2012 (this record's independent
cross-check on the 6S-5P matrix elements and the sign of the downward cascade
term in Delta-alpha_6S). This record's own scalar 5S-6S magic-wavelength
calculation (`rb5s6s/polarizability.py`, noted elsewhere as scalar-only magic
wavelengths being exact for J=1/2, per `docs/CLAIMS.md`) shares arora2007's
general condition (a sum-over-states dynamic polarizability for each state,
the magic wavelength at their crossing) but not the ab initio machinery
(corrected 2026-09-22): the module's own docstring says it uses `PUBLISHED
reduced matrix elements and NIST energies`, not a relativistic all-order
calculation of its own. One link is closer than that and worth flagging,
not resolving, here: the docstring cites `Arora et al. 2007` for the
6S ionic-core polarizability it borrows, 9.1(5) a.u., and that exact figure
is this paper's own Table I core-polarizability entry (p. 2, unread
otherwise, and itself sourced there from Johnson/Kolb/Huang 1983's RPA
calculation, not original to this paper). This is plausible, since the Rb+
core value is commonly reused across the Safronova group's alkali papers,
but not confirmed by a page-1 read alone.

It is not the 5S-6S transition itself. It is the np-ns family, ground state
to the first excited p states, not 5S-6S which is an s-s two-photon
transition. So its own headline results, the np-ns magic wavelengths
themselves, do not supply a directly reusable number for 5S-6S. It is the
method precedent the search priority named (item 7) for Rb magic-wavelength
calculations from the Safronova/Arora programme, complementing the
transition-specific goldschmidt2015 (5s-18s) and the already-held
safronova2006 polarizability survey.
