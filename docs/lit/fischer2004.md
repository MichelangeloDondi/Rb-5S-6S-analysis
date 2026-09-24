---
citekey: fischer2004
type: article
authors:
  - Fischer, M.
  - Kolachevsky, N.
  - Zimmermann, M.
  - Holzwarth, R.
  - Udem, Th.
  - Hänsch, T. W.
  - Abgrall, M.
  - Grünert, J.
  - Maksimovic, I.
  - Bize, S.
  - Marion, H.
  - Pereira Dos Santos, F.
  - Lemonde, P.
  - Santarelli, G.
  - Laurent, P.
  - Clairon, A.
  - Salomon, C.
  - Haas, M.
  - Jentschura, U. D.
  - Keitel, C. H.
title: 'New Limits on the Drift of Fundamental Constants from Laboratory Measurements'
journal: Phys. Rev. Lett.
volume: 92
number: 23
pages: 230802
year: 2004
doi: 10.1103/PhysRevLett.92.230802
arxiv: 'physics/0312086'
pdf: PDF_papers/Fischer_2004_hydrogen-1S-2S-drift-fundamental-constants-lineshape-model.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/fischer2004.md  # line-by-line against the held PDF, 2026-09-22: one number corrected (5.8 K was parthey2011's, not this paper's; this paper's own nozzle runs 5-6 K), one overclaim candidate considered and refuted
author: agent
routing: []
verify_flags:
  - 'Page 1 of the held arXiv:physics/0312086v2 preprint (title, full author
    list, abstract, PACS numbers, and the opening two paragraphs of the
    introduction) read against the record on 2026-09-21. The remaining three
    pages, including the systematic-correction and line-shape-fit sections,
    are unread; nothing below draws on them.'
  - 'One further sentence on p. 2 ("Hydrogen atoms from a radio-frequency (rf)
    gas discharge are cooled to 5-6 K by collisions with the walls of a copper
    nozzle") was read on 2026-09-22, during the line-by-line audit, solely to
    check the apparatus-temperature figure used below; nothing else on pages
    2-4 was read or is drawn upon.'
verified_date: 2026-09-21
summary: >
  MPQ/SYRTE remeasurement of the hydrogen 1S-2S transition against the Cs
  hyperfine splitting, bounding the drift of alpha and of the Rb/Cs nuclear
  moment ratio. Co-authored by M. Haas, U. D. Jentschura and C. H. Keitel, the
  theory group whose 2006 trajectory-resolved two-photon excitation/AC-Stark/
  ionization model (Haas et al., PRA 73, 052501) this search could not obtain
  open access to; this is its experimental sibling and the direct predecessor
  of Parthey et al. 2011 (parthey2011).
loci: []
section: transit-time
---

# fischer2004

VERIFIED for page 1 (title, authors, abstract, PACS line, opening
introduction). REPORTED for everything past it: the systematic-budget and
line-shape-fitting sections that would show the atomic-trajectory/AC-Stark
treatment in numerical form are unread.

## What page 1 gives, verbatim

"We have remeasured the absolute 1S-2S transition frequency νH in atomic
hydrogen. A comparison with the result of the previous measurement performed
in 1999 sets a limit of (−29 ± 57) Hz for the drift of νH with respect to the
ground state hyperfine splitting νCs in 133Cs. Combining this result with the
recently published optical transition frequency in 199Hg+ against νCs and a
microwave 87Rb and 133Cs clock comparison, we deduce separate limits on
α̇/α = (−0.9 ± 2.9) × 10⁻¹⁵ yr⁻¹ and the fractional time variation of the ratio
of Rb and Cs nuclear magnetic moments μRb/μCs equal to (−0.5 ± 1.7) × 10⁻¹⁵
yr⁻¹. The latter provides information on the temporal behavior of the constant
of strong interaction."

## Why this record holds it

The owner's search priority named Haas et al. 2006 (PRA 73, 052501, titled `Two-photon excitation
dynamics in bound two-body Coulomb systems including ac
Stark shift and ionization`) as the closest published precedent for a
trajectory-resolved, non-convolving fitted line-shape model. That paper has no
arXiv posting and no open-access copy surfaced in a deep search (arXiv export
API query for its exact title returns zero results. See the intake report's
paywalled list). This 2004 PRL is the experimental measurement that motivated
it, sharing three authors (Haas, Jentschura, Keitel) with the 2006 theory
paper, and its own text is what Parthey et al. 2011 (parthey2011) cites by
name when reporting an improvement "by a factor of 3.3." Holding this paper
keeps the lineage on the shelf even where the specific theory paper could not
be fetched. Its own unread systematic-correction sections are exactly where an
early version of the 2006 model's AC-Stark treatment would appear.

## Use in this record

Precedent lineage only, at this stage: this record's own AC-Stark ramp and
transit model (`rb5s6s/ramp_transit.py`, `rb5s6s/lineshape.py`) is Rb 5S-6S at
a heated vapour cell, not a cryogenic atomic hydrogen beam at 5-6 K (this
paper's own figure, p. 2, corrected 2026-09-22 against the PDF. The "5.8 K"
this sentence carried before is `parthey2011`'s own later apparatus, not this
paper's), so no numerical value transfers. What transfers is the methodological precedent the search
was asked to find: a two-photon transition whose systematic budget forces a
joint, non-convolving treatment of the atomic trajectory and the AC-Stark
shift, from the same lineage as Haas 2006 (paywalled, not held), Parthey 2011
(parthey2011), Matveev 2013 (paywalled, not held) and Grinin 2020
(grinin2020).
