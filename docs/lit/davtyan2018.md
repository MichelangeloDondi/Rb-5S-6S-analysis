---
citekey: davtyan2018
type: article
authors:
  - Davtyan, D.
  - Machluf, S.
  - Soudijn, M. L.
  - Naber, J. B.
  - van Druten, N. J.
  - van Linden van den Heuvell, H. B.
  - Spreeuw, R. J. C.
title: 'Controlling stray electric fields on an atom chip for experiments on Rydberg atoms'
journal: Phys. Rev. A
volume: 97
number: 2
pages: 023418
year: 2018
doi: 10.1103/PhysRevA.97.023418
arxiv: '1710.05301'
pdf: PDF_papers/Davtyan_2018_stray-electric-fields-atom-chip-Rydberg.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1710.05301v1 preprint (15 Oct 2017), titled "Controlling Stray Electric
    Fields on an Atom Chip for Rydberg Experiments"; the published title above, with the volume,
    article number and DOI, is Crossref''s record, checked 2026-09-22. Read in full on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  On an atom chip whose top layer is 25 nm of silica over gold, the 480 nm Rydberg laser, focused on
  the surface with a variable duty cycle, desorbs Rb adsorbates locally, mostly by light-induced
  desorption, and so tunes the stray field's perpendicular component through zero, to under 0.2 V/cm
  at 78 um; each setting takes 2.5 to 3 hours to reach steady state. A model of adsorbate dipoles at
  12 D with a laser-cut hole reproduces the field against height. A second demonstration that the
  excitation light itself sets a Rb-on-silica surface field, with its time scale.
loci:
  - methods/09
section: deep-search
---

# davtyan2018

VERIFIED against the held preprint (scope in `verify_flags`).

## The experiment

87Rb in a z-wire magnetic trap is excited to 25S by 780 nm and 480 nm beams of 100 um waist, and the loss of trapped atoms gives Stark maps against a voltage between the chip and an ITO-coated in-vacuum lens, from which the perpendicular and parallel stray-field components are fitted (their Fig. 1). The chip's surface is a stack with 25 nm of silica over 90 nm of gold. The abstract, verbatim: "We use one of the Rydberg excitation lasers to locally affect the adsorbed dipole distribution." The duty cycle of the blue laser on the chip runs from 0.2 to 86 per cent of a 21 s cycle.

## What it finds

Verbatim: "By adjusting the averaged exposure time we change the strength (with the minimal value less than 0.2 V/cm at 78 µm from the chip) and even the sign of the perpendicular field component." The time to settle, verbatim: "Each of the data sets is taken in a steady state reached ∼ 2.5 − 3 hours after changing the duty cycle." A model of Rb adsorbate dipoles, taken at 12 D and corrected by 1.25 for images in the gold, distributed as two Gaussian patches with a hole cut by the laser, fits all duty cycles at once and gives a peak density of 7.03 x 10^5 atoms per um^2, an adatom spacing near 1.2 nm (Figs. 2 to 4). A thermal simulation puts the laser spot 11 to 13 K above room temperature, and the authors judge, verbatim: "Estimates for thermal desorption and LIAD based on the numbers provided in [16, 30] suggest that the desorption is dominated by LIAD due to the high beam intensity, while the mild local heating only contributes in a minor way." On the silica layer itself, verbatim: "In previous experiments we observed large stray electric fields above a gold surface [27] and even ∼ 10 times larger fields above silica-coated gold [12]."

## Use in this record

This is the third instance on the shelf, after `ocola2024` and `sedlacek2016`, of an experiment's own light setting the field of a Rb-exposed silica surface, here through desorption by the excitation laser itself, with hours to reach steady state. For the fibre arm, whose excitation light is guided in the fibre and so illuminates its surface wherever atoms are probed, the implication is that the surface field is a function of the drive's duty cycle and history, to be logged beside the data. The adatom dipole used here, 12 D, is taken from the literature, `sedlacek2016`'s calculated value among its sources, not measured. The chip is a thin silica film on gold, not bulk silica, so its image correction does not apply to a fibre.

Related on this shelf: `ocola2024`, `sedlacek2016`, `obrecht2007`, `mcguirk2004`, and the Naber 2016 PDF (adsorbate dynamics on a silica-coated gold surface, from the same group, note pending).
