---
citekey: schmidt2011
type: article
authors:
  - Schmidt, Regine
  - Nic Chormaic, Síle
  - Minogin, Vladimir G.
title: 'van der Waals interaction of a neutral atom with the surface of a metal or dielectric nanosphere'
journal: 'J. Phys. B: At. Mol. Opt. Phys.'
volume: 44
pages: 015004
year: 2011
doi: 10.1088/0953-4075/44/1/015004
arxiv: null
pdf: PDF_papers/Schmidt_2011_J._Phys._B__At._Mol._Opt._Phys._44_015004.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'abstract and front matter read; the derivations in sections 2-4 are not.
    The factors of 6 and 2 quoted below are the paper''s own abstract wording.
    Their range of validity -- which distances, which permittivities -- has not
    been checked against the derivation, and the abstract does not state it.'
  - 'wrong geometry for the nanofibre problem. This is a sphere. It is filed as a
    method anchor and as the source of the curvature result, not as an input to
    the patterson2018 refit; frawley2012 is the cylinder analogue, is held, and
    is the one actually needed. Where the two disagree, prefer Frawley -- and
    prefer Frawley''s body over either abstract, since taking the curvature
    result from an abstract alone produced a wrong claim here on 2026-07-31.'
verified_date: 2026-07-31
summary: >
  Closed analytical equations, in the electrostatic approximation, for the van
  der Waals energy of an atom near the internal and external surfaces of a metal
  or dielectric nanosphere. Tyndall/ucc/Mainz/Troitsk -- Nic Chormaic and
  Minogin, the same group as frawley2012, of which this is the spherical
  counterpart. The result that carries beyond the geometry is that curvature
  sign matters: concave (internal) surfaces enhance the vdW energy by up to a
  factor of 6 over a flat surface, convex ones weaken it by up to a factor of 2.
  note what "UP TO" hides, because it is the whole story: the two held
  cylindrical papers from the same lineage -- frawley2012 (convex) and
  afanasiev2010 (concave) -- both have their surface factor tending to unity AT
  the wall, with curvature biting only at distances comparable to the radius. So
  a flat-surface C_3/r^3 is adequate near a surface of either curvature, and the
  extreme factors apply far from it. This sphere paper is replaced for both
  geometries by those two; keep it as the method anchor and for the fact that
  curvature sign matters at all.
loci:
  - P2
section: method-anchors
---

# schmidt2011

Held. Abstract and front matter read. The derivations in Sections 2-4 are not verified.

## The system

Schmidt, Nic Chormaic, and Minogin derive closed analytical equations, in the electrostatic approximation, for the van der Waals interaction energy of an atom near the internal and external surfaces of a metal or dielectric nanosphere. The sign of the surface curvature sets the direction of the correction relative to a flat surface. Concave (internal) surfaces enhance the interaction, convex (external) surfaces weaken it.

## The numbers

From the abstract:

> "We derive closed analytical equations for the van der Waals interaction energy using an electrostatic approximation and show that the energy increases or decreases as a function of the atom's distance from the surface, depending on the surface curvature. For concave spherical surfaces, the van der Waals energy can increase by up to a factor of 6, while for convex surfaces it decreases by as much as a factor of 2, when compared to that obtained for a flat surface."

The paper states that the closed-form equations are intended for direct comparison between theory and experimental measurements of the van der Waals constant $C_3$.

## Validity

The geometry treated here is a sphere, not the cylinder relevant to an optical nanofibre or a hollow-core fibre. The cylinder analogues, from the same authors (Nic Chormaic and Minogin), are [frawley2012](frawley2012.md) for the convex exterior and [afanasiev2010](afanasiev2010.md) for the concave interior of a hollow core. Both show the curvature correction to be a far-field effect rather than a near-surface one. frawley2012's surface factor $\mu \to 1$ for $x_0 \ll R$, where curvature has no effect, and reaches only about 0.5 near $x_0 = 5R$. afanasiev2010 gives a concave enhancement factor of 4, not 6, evaluated on the axis of a hollow cylinder, with the internal surface factor likewise tending to 1 at the wall. A flat-surface $C_3/r^3$ term is therefore adequate close to a surface of either curvature, with the extreme factors from this paper applying only far from it. For the core sizes relevant to a hollow-core geometry, the 4x on-axis enhancement multiplies a $C_3/x_0^3$ term that is between $10^{-4}$ and $10^{-10}$ of its value 10 nm from the wall, so the concave correction is negligible at any distance an atom would occupy.

## Use in this record

[patterson2018](patterson2018.md) and [liu2024](liu2024.md) place their atoms close to the convex exterior of a fibre, where the flat-surface approximation is adequate, so this sphere paper is not an input to that refit. It is retained as the source of the general principle that curvature sign changes the van der Waals coupling, with the cylinder-specific numbers taken from frawley2012 and afanasiev2010.
