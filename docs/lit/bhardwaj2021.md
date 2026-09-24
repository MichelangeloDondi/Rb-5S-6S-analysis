---
citekey: bhardwaj2021
type: article
authors:
  - Bhardwaj, K.
  - Ram, S. P.
  - Singh, S.
  - Tiwari, V. B.
  - Mishra, S. R.
title: 'Absorption imaging of trapped atoms in presence of AC-Stark shift'
journal: Phys. Scr.
volume: 96
number: 1
pages: 015405
year: 2021
doi: 10.1088/1402-4896/abc5f1
arxiv: '2003.05799'
pdf: PDF_papers/Bhardwaj_2021_AC-Stark-shift-dipole-trap-absorption-imaging.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:2003.05799v1 preprint (12 Mar 2020), titled "Effect of AC-Stark shift in
    optical dipole trap on absorption imaging of trapped atoms"; the published Phys. Scr. version, under
    the title above, is not held. Title, volume, article number and DOI are Crossref''s record of the
    published article, checked 2026-09-22. Read in full on 2026-09-22. The preprint carries evident typesetting slips (a "1064 bm" laser, a 7802.4 nm
    wavelength in its Table I for the 780 nm line), so its table is not quoted.'
verified_date: 2026-09-22
summary: >
  A focused 1064 nm dipole trap shifts the 87Rb levels by an amount that follows the local intensity,
  so the probe's absorption cross-section varies across the cloud; analysing the images with a
  constant cross-section undercounts the atoms about sixfold at 27.7 W. A plain instance of the error
  this record's line model is built to avoid: an observable averaged over a position-dependent light
  shift, read as though the shift were absent or uniform.
loci:
  - methods/03
section: method-anchors
---

# bhardwaj2021

VERIFIED against the held preprint (scope in `verify_flags`).

## What it does

A single-beam dipole trap at 1064 nm, focused to a 1/e^2 radius of 17 um, holds laser-cooled 87Rb. The cloud is imaged in situ with a probe resonant with the unperturbed cooling transition. The abstract, verbatim: "The spatial varying intensity of the ODT beam results in position dependent light-shift (i.e. AC-Stark shift)." The paper computes the light shift of each hyperfine sublevel from a sum over dipole-allowed transitions, builds an effective cross-section that follows the local shift of the probe transition (their Eq. 3), and integrates it over a Gaussian cloud to predict the optical density (Eq. 4).

## What it finds

The peak ground-state shift is quoted as -7.01 MHz at the focus for 1 W. With the shift carried in the image analysis, the atom number at 27.7 W is 2.12 x 10^6. With a constant cross-section it is 3.5 x 10^5 (Section III.D and Fig. 8). The authors conclude, verbatim: "The difference in the number of atoms estimated with and without incorporating light-shift shows that it is essential to consider AC-Stark shifts for correct estimation of number of trapped atoms in dipole trap."

## Use in this record

The analogy is exact and the paper is modest: an observable is the average of a response over atoms that sit at different intensities, and a model that ignores the spread of shifts returns a biased parameter, here by a factor of about six. In the 2025 line the same average is the light-shift ramp inside the line shape. The paper models a trap, not a spectroscopic line, and carries no uncertainty budget, so it is cited for the mechanism only.

A closer neighbour, from the reviewer's intake of 2026-09-21: `hilton2020`, which reads a temperature and a trap depth off a light-shift-broadened spectrum inside a hollow-core fibre.
