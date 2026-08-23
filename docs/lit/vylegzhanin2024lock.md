---
citekey: vylegzhanin2024lock
type: article
authors:
  - Vylegzhanin, Alexey
  - Nic Chormaic, Sile
  - Brown, Dylan J.
title: 'Rydberg electromagnetically induced transparency based laser lock to Zeeman sublevels with 0.6 GHz scanning range'
journal: arXiv preprint
volume: null
number: null
pages: null
year: 2024
doi: null
arxiv: 2407.11323
pdf: PDF_papers/Vylegzhanin_2024_Rydberg-EIT-laser-lock-Zeeman-0p6GHz.pdf
held: true
status: VERIFIED
verified_date: 2026-08-22
section: oist-lineage
summary: >
  Read in full 2026-08-22 from the arXiv PDF (v3, 16 Oct 2024, seven pages).
  A LOCKING TECHNIQUE, demonstrated. The 480 nm pump of a Rydberg EIT ladder
  in a 87Rb vapor cell is locked to Zeeman-split EIT peaks of the 5P3/2 to
  32D5/2 transition, and tuning the applied magnetic field tunes the lock
  point continuously over 0.6 GHz. Short-term stability 0.15 MHz, long-term
  within 0.5 MHz over ten minutes, lock linewidth about 0.8 MHz with the
  field applied and about 1.8 MHz without. Without shielding and at zero
  applied field the lock point shifts peak to peak by 1.6 MHz with pump
  polarization, reduced to 0.6 MHz when locked to Zeeman sublevels. The
  authors state stray fields were NOT shielded, and the polarization
  sensitivity of the unshielded zero-field lock is measured rather than
  estimated.
relevance: >
  Same group and same first author as the OIST lineage. Method-adjacent to
  this campaign's frequency handling twice over. First, the lock's stability
  numbers, 0.15 MHz short-term against a lock linewidth of 0.8 to 1.8 MHz,
  are the same order as the effective homogeneous component this analysis
  extracts, so a lock of this class in a similar setup does not by itself
  place a laser below the widths at issue. Second, the paper quantifies a
  systematic of its own reference, the polarization-dependent lock-point
  shift, and reduces it by choosing a less polarization-sensitive line,
  which is the same discipline as this record's ruler-first treatment of a
  drifting axis. No number from this paper enters any committed result.
---

## What the paper does

Locks the 480 nm pump of a two-photon Rydberg EIT ladder (780 nm probe on
5S1/2 to 5P3/2, 480 nm pump on 5P3/2 to 32D5/2) to Zeeman-split EIT peaks in a
87Rb vapor cell. The applied field is TRANSVERSE to the beam propagation axis,
along z, from a pair of rectangular coils, with the light linearly polarized
perpendicular to it and therefore seen by the atoms as a combination of sigma
plus and sigma minus. The field splits the EIT feature by sublevel, and
stepping it moves the chosen peak, giving a lock point tunable over 0.6 GHz
without touching the laser.

## The numbers, from the paper's own abstract and figures

* Short-term stability 0.15 MHz. Long-term stability within 0.5 MHz. The
  paper's own method for the second is to take the separation between the most
  distant mean frequency values, then histogram the drift over a ten-minute
  recording and fit a Gaussian to it. The abstract's 0.5 MHz is not itself
  quoted as a ten-minute number, and an earlier version of this note tied the
  two more tightly than the paper does.
* For context the paper gives, this improves on Rajasree et al., where the
  long-term drift was about 0.5 MHz and the short-term stability about
  0.4 MHz.
* Lock linewidth about 0.8 MHz with the external field, about 1.8 MHz without.
* Unshielded, zero-field lock point moves 1.6 MHz peak to peak with pump
  polarization. Locking to a Zeeman sublevel reduces that to 0.6 MHz.

## Why it is in this corpus

The OIST lineage's frequency infrastructure. The nanofibre Rydberg experiments
of this group (vylegzhanin2023, raj2026) need a continuously tunable, stable
480 nm reference, and this is the group's own solution, with its systematics
measured and stated rather than assumed away.
