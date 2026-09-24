---
citekey: obrecht2007
type: article
authors:
  - Obrecht, J. M.
  - Wild, R. J.
  - Cornell, E. A.
title: 'Measuring electric fields from surface contaminants with neutral atoms'
journal: Phys. Rev. A
volume: 75
number: 6
pages: 062903
year: 2007
doi: 10.1103/PhysRevA.75.062903
arxiv: '0705.2027'
pdf: PDF_papers/Obrecht_2007_electric-fields-surface-contaminants-neutral-atoms.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:0705.2027v2 preprint (22 Jun 2007); volume, article number and DOI are
    Crossref''s record, checked 2026-09-22. Read in full on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  A condensate driven resonantly by an applied AC field grows in amplitude at a rate set by the
  gradient of a surface's stray field, which yields the vector field of deliberately deposited Rb
  adsorbates with micron resolution. The dipole per adatom is about 35 debye on yttrium and 3.2 on
  fused silica; heating shortens the field's decay with an activation energy near 0.42 eV on both, and
  an attempt rate ten orders below desorption's points to surface diffusion. The adsorbate numbers and
  the thermal law for the material of a nanofibre.
loci:
  - methods/09
section: deep-search
---

# obrecht2007

VERIFIED against the held preprint (scope in `verify_flags`).

## The method

The abstract, verbatim: "We apply an alternating external electric field that adds to (or subtracts from) the stray field in such a way as to resonantly drive the trapped atoms into a mechanical dipole oscillation." The amplitude grows linearly in time at a rate proportional to the product of the applied field and the stray-field gradient (their Eq. 5), and reversing the drive's polarity shifts the oscillation's phase by pi, so the sign is read as well as the size (Fig. 2). Measured along x, y and z and at several places along the surface, the gradients integrate to a two-dimensional vector map of the field (Fig. 3). The conclusion gives the sensitivity as gradients of about 300 nV/um^2.

## What it finds

Deposited Rb on the yttrium film spreads more diffusely than it was put down: the measured map fits a pattern with a width of 26 um, not the deposited one. The field gradient grows linearly with the number of clouds deposited and the trap-frequency shift quadratically, as the model predicts (Fig. 4). From the linear range, the dipole per adsorbed Rb atom, in the paper's words, verbatim: "Using the procedure described above, we find that the dipole moment per Rb atom adsorbed onto our yttrium surface is ∼35 Debye [16]". And, verbatim: "We also measure a dipole moment of ∼3.2 Debye for Rb on fused silica, ∼5.4 Debye for Rb on a metallic hafnium surface, and ∼19 Debye for Rb on a metallic lutetium surface."

On the thermal law: heating the substrate from behind with a laser, the field decays exponentially with a time following an Arrhenius form (their Eq. 12), and verbatim: "The similar fits to the data suggest that rubidium has similar activation energies on fused silica and yttrium (EA ≈ 0.42 eV on each) and also reveal γo to be approximately 15–25 s−1 ." The authors read the attempt rate as about ten orders below a desorption process's and as characteristic of surface diffusion. The abstract, verbatim: "We show that baking the substrate can reduce the electric fields emanating from adsorbate, and that the mechanism for reduction is likely surface diffusion, not desorption." At room temperature on yttrium they see no significant desorption or diffusion over minutes, rather over several days.

## Use in this record

A nanofibre is fused silica exposed to rubidium, and its patch field on a nearby Rydberg atom is the term the owner hopes the campaign measures. This paper supplies the numbers a model of that term starts from: a dipole near 3.2 debye per Rb adatom on fused silica, and a field lifetime that falls with temperature along an Arrhenius law with an activation energy near 0.42 eV, set by diffusion, not desorption. Two cautions. The same group's earlier measurement on BK7 (`mcguirk2004`) bounded the dipole five to ten times below the conductors' 3 debye, an order of magnitude under this paper's fused-silica value. Glass and method differ, and the difference is the present uncertainty. And the paper's surfaces are flat and its atoms 5 to 20 um away, so the fibre's curvature and the Rydberg atom's range remain the model's to carry.

Related on this shelf: `mcguirk2004`, `sedlacek2016` (Rb on quartz, electron binding cancels the field), `abel2011`, and the Hattermann 2012 PDF (adsorbate fields on cold Rydberg atoms, note pending).
