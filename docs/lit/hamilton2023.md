---
citekey: hamilton2023
type: article
authors:
  - Hamilton, R.
  - Roberts, B. M.
  - Scholten, S. K.
  - Locke, C.
  - Luiten, A. N.
  - Ginges, J. S. M.
  - Perrella, C.
title: 'Experimental and theoretical study of dynamic polarizabilities in the $5S_{1/2}$--$5D_{5/2}$ clock transition in rubidium-87 and determination of {E1} matrix elements'
journal: Phys. Rev. A
year: 2023
doi: null
arxiv: 2212.10743
pdf: PDF_papers/Hamilton_2023_Rb-5D-dynamic-polarizability-E1-elements.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - Journal vol/page/DOI VERIFY at submission
verified_date: null
summary: >
  Rigor template for the polarizability side (+ magic-lambda idea).
loci:
  - M16
  - P1
  - THEORY
section: method-anchors
---

# hamilton2023

Rigor template for the polarizability side (+ magic-lambda idea). Journal vol/page/DOI VERIFY at submission.

The nearest prior art for our specific CONSTRUCTION, and geometrically closer than stalnaker2006: a retro-reflected Rb-87 vapour two-photon line (5S->5D, two-colour 780+776 nm via the near-resonant 5P intermediate). They build the identical focus average -- fluorescence amplitude proportional to I(r)_780 * I(r)_776, integrated as F(Delta) = integral of F(Delta,r) r dr with the cylindrical Jacobian -- the same I^n * (linear shift) * (r dr) integral we reduce to the wedge.

**Delineation (what is genuinely NOT in Hamilton):**
- they collapse the integral to a single spatially-averaged shift (a ~3.6 factor from mean shift to Delta-alpha) and never keep the shift DISTRIBUTION -- so the closed-form wedge f(s) proportional to |s| and its third moment are not there. The novelty is "keep the distribution, close it in form, read the drift-immune skew," not "set up the integral";
- their signal is a two-colour PRODUCT I_780*I_776 (near-resonant ladder), not the degenerate single-colour I^2 of the 993 nm 5S->6S virtual-state two-photon;
- they do not treat the axial standing-wave fringes at all (transverse-profile average only) -- fringe-*ignored*, not fringe-*averaged*, which reinforces rather than threatens our fringe delineation.

MUST be delineated in the paper's introduction: a referee who knows Hamilton will see the integral parallel immediately, so we state up front what we add. Their **776.179 nm magic wavelength** on the 5D_5/2 clock transition is also the target of a proposed Ti:Sapph asymmetry scan (`FUTURE_TRANSITIONS_titsapph.md`).
