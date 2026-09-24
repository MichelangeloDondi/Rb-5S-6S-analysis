---
citekey: karman1998
type: article
authors:
  - Karman, G. P.
  - Beijersbergen, M. W.
  - van Duijl, A.
  - Bouwmeester, D.
  - Woerdman, J. P.
title: 'Airy pattern reorganization and subwavelength structure in a focus'
journal: J. Opt. Soc. Am. A
volume: 15
number: 4
pages: 884-899
year: 1998
doi: 10.1364/JOSAA.15.000884
arxiv: null
pdf: PDF_papers/Karman_1998_Airy-pattern-reorganization-truncated-Gaussian-focus.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the published typeset article, the author copy the UCSB quantum-optics group hosts
    (web.physics.ucsb.edu/~quopt/airy.pdf), fetched 2026-09-22. Sections 1, 2, 4 and 5 and Appendix A
    read line by line; Section 3, the nonparaxial vector theory at NA 0.9, read through 3.B only, since
    nothing below rests on it. The text layer renders "=" as "5" and "<<" as "!", so no equation is
    quoted.'
verified_date: 2026-09-22
summary: >
  The focal field of a Gaussian beam truncated by a circular aperture, followed continuously from
  uniform illumination (the Airy pattern) to an untruncated Gaussian, in scalar paraxial Debye theory
  with a Kirchhoff check at low Fresnel number, and measured in three dimensions with a CCD. As the
  truncation ratio a/w grows the central spot widens and the Airy rings leave the focal plane by
  pairwise annihilation. The reference for what the modulator's bore does to the focal intensity
  distribution, and so to the light-shift distribution the fit reads.
loci:
  - methods/03
section: method-anchors
---

# karman1998

VERIFIED against the held article (scope in `verify_flags`).

## What it computes

A lens of focal length f and radius a is illuminated by a Gaussian beam of 1/e amplitude width w, cut off by the aperture: the input amplitude is the Gaussian inside r < a and zero outside (their Eq. 10). The truncation ratio a/w runs from zero, uniform illumination and the Airy pattern, to infinity, an untruncated Gaussian waist. The paraxial Debye integral is the model. Its validity condition is stated as "the Fresnel number N should be much larger than unity", and Appendix A repeats every case in Kirchhoff theory, where the field loses its symmetry about the focal plane and the maximum moves toward the lens (the focal shift). The authors conclude the low-Fresnel-number case changes the geometry and not the topology.

## What it finds

The abstract, verbatim: "We show that in the gradual transition from uniform toward Gaussian illumination, the Airy rings reorganize themselves by means of a creation/annihilation process of the singularities."

On the central spot, verbatim: "As the input amplitude starts to deviate from a uniform distribution, the central spot grows." And the reason, verbatim: "This is related to the reduced spread of the beam in the aperture, which gives a larger spread in the focal plane."

At NA 0.1 the innermost two dark rings of the focal plane coalesce between a/w of 1.563 and 1.621. Two extra rings are created outside the focal plane at a/w of 1.471, and the in-plane pair annihilates at 1.621 (Section 2.C and Figs. 7 and 9). The authors add, verbatim: "Note that the intensity in the first bright ring is already very small for moderate values of a/w." In the paraxial regime the pattern scales with the numerical aperture alone, transversely as its inverse and longitudinally as its inverse square.

The experiment used a helium-neon beam with w of 1.74 mm, an iris of radius 0.8 to 3 mm and a 1 m lens (NA about 2 x 10^-3, Fresnel number about 6). The first two rings meet and vanish from the focal plane near a/w of 1.6, in agreement with the scalar calculation (Fig. 19). On a second configuration, verbatim: "The asymmetry with respect to the focal plane is due to the finite Fresnel number".

## Use in this record

The 2025 beam passes the electro-optic modulator's 3 mm bore before the focusing lens, and the owner's ruling of 2026-09-17 places the focus at 40 to 45 um with the bore and M^2 in the profile, not only in the on-axis factor. This paper is the reference for the qualitative structure of that profile: a clipped Gaussian focuses to a wider central spot with weak rings, and the shape of the light-shift distribution follows the shape of the intensity distribution, not only its peak.

Two limits on how far it carries. Its aperture sits at the lens. In the bench's delivery the bore sits upstream, so the field reaching the lens is the clipped Gaussian after free propagation, and the paper's ring positions are a map, not numbers for this geometry. And it reports intensity contours, not the distribution of intensity over the atoms' positions, which is the quantity the line shape needs. That distribution is computed by the analysis side's clipped-focus profile, and no number here stands in for it.

Related on this shelf: `lim2021` (a slit-clipped beam's focal region measured, elongated along the axis), `schmidt2011b` (M^2 from a modal decomposition). 