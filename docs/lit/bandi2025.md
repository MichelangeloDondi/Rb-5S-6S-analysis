---
citekey: bandi2025
type: article
authors:
  - Obaze-Adeleke, A. C.
  - Semon, B.
  - Bandi, T. N.
title: 'A comprehensive review of rubidium two-photon vapor cell optical clock: long-term performance limitations and potential improvements'
journal: Photonics
volume: 12
number: 5
pages: 513
year: 2025
doi: 10.3390/photonics12050513
arxiv: null
pdf: PDF_papers/Bandi_2025_Rb-two-photon-vapor-cell-clock-review.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'CITEKEY NAMES THE CORRESPONDING AUTHOR, NOT THE FIRST (noted
    2026-07-30). The record here is correct and checked against the held
    PDF: the paper is Obaze-Adeleke, Semon and Bandi, and T. N. Bandi is
    the corresponding author, not the first. The key follows how the
    review is known rather than this repository''s usual first-author
    convention. Consequence to watch: docs cite it in prose as "Bandi
    2025", and expanding that to "Bandi et al. (2025)" in a manuscript
    would be WRONG -- it is "Obaze-Adeleke et al. (2025)". Do not rename
    the key (it is used in three documents); render the citation from the
    authors field, not from the key.'
  - 'Quotes Hamilton''s 5S-5D magic wavelength as 778.179(5) nm; Hamilton 2023
    itself says 776.179(5) nm in its abstract and conclusions. Transposition in
    the review -- cite Hamilton directly, not this.'
verified_date: 2026-07-26
summary: >
  Field/systematics review for the Rb two-photon clock. Names the AC Stark
  shift, the temperature-induced shift and laser drift together as the
  medium-to-long-term limiters; targets better than 1e-15 at a day.
loci:
  - P1
section: landscape-24-26
---

# bandi2025

Held. Verified in full (44 pages).

## The review

MDPI open-access review of systematics in the Rb two-photon vapor-cell optical clock.

## What limits performance

The abstract lists three limiting effects without ranking them, but the body ranks two of them above the third:

> "light shift variations (stemming from fluctuations in the laser optical power that probe the rubidium transition) [117,120,136,157] and vapor-cell temperature variations [136] predominantly limit performance for medium- to long-term averaging."

Light shift and cell temperature are named together as the predominant pair, above laser drift and the remaining effects.

## The numbers

The 5S-5D two-photon linewidth is quoted as approximately 330 kHz, against the 3.49 MHz natural width of 5S-6S: the 778 nm line is roughly an order of magnitude narrower. Field target: better than 1e-15 at one day. Reported temperature coefficient -1.09(4)e-12 per K. Helium collisional shift 0.55e-8.

The review states that measured linewidths in its Table 1 consistently exceed the natural value: "The natural linewidth of the two-photon transition in Rb is [approximately] 330 kHz; however, as shown in Table 1, the measured linewidths consistently exceed this intrinsic value." A comparable excess over the intrinsic linewidth appears in the nanofibre measurements of [patterson2018](patterson2018.md); whether the two excesses share a cause is open.

## A transcription error in the review

The review reports Hamilton's 5S-5D magic wavelength as "an experimental magic wavelength of 778.179(5) nm and a theoretical magic wavelength of 776.21 nm." Hamilton 2023 (held here) states 776.179(5) nm experimental and 776.21 nm theoretical, in both the abstract and the conclusions: the review has transposed a digit. `constants.py` carries 776.179 nm, which is correct. Hamilton also reports a second magic wavelength at 790.26 nm, close to the 5S tune-out.

## Coverage

5S-6S / 993 nm does not appear in the body text. The only hits are reference titles (Nez 1993, a 5S-5D3/2 paper). The review covers the 5S-5D line only.

## Table 1 against the transit model

The review's Table 1 lists, for ten Rb two-photon vapor-cell standards, the signal linewidth together with the cell temperature and the 1/e² beam waist. Those three quantities are what `rb5s6s.constants.transit_fwhm_from_w0` maps between. Taking the tabulated waist as a radius and the natural linewidth as 330 kHz:

| work | observed | excess over natural | transit predicted |
|---|---|---|---|
| Poulin 2002 | 410 kHz | 80 | 138 |
| Callejo 2024 | 450 | 120 | 597 |
| Lemke 2022 | 550 | 220 | 28 |
| Li 2024 | 618 | 288 | 74 |
| Erickson 2024 | 774 | 444 | 256 |
| Gerginov 2018 | 795 | 465 | 145 |
| Maurice 2020 | 2200 | 1870 | 574 |

The transit-predicted column sits below the tabulated excess in five of seven rows, by factors of 2 to 8, consistent with transit being one among several broadening terms: Bandi attribute the excess to "transit-time broadening due to the finite interaction period of atoms with the laser and self-collisional broadening, as well as the laser's linewidth."

Two rows do not check out against the review's own figures. Callejo's tabulated linewidth (450 kHz) belongs to a different cell than the tabulated waist: [callejo2025](callejo2025.md) (held) reports a 100 µm waist focused into a 2 mm x 1.5 mm MEMS cavity with a measured linewidth of 1.5-2.1 MHz, while the 450 kHz figure and the "25 mm diameter, 70 mm length" cell dimensions belong to their separate reference glass-blown cell. Against the primary numbers, 597 kHz of transit accounts for 34-51% of the 1170-1770 kHz excess over 330 kHz. Lemke's row is consistent once read at source: w0 = 2.1(3) mm, stated as an intensity radius (1/e²), giving 28 kHz of transit against 220 kHz excess (13%).

The waist column does not use one convention throughout. Lemke states a radius. Erickson's thesis (held, `theses/`) states a diameter explicitly: "310 kHz for 230 µm beam diameter at 100 °C." At Erickson's geometry (w0 = 115 µm), `transit_fwhm_from_w0` gives 513 kHz against his own reported 310 kHz, a factor of 1.65 that reflects differing definitions of what "transit-time broadening" means rather than a waist-convention error (candidates include a 1/e² crossing time, a FWHM, the Biraben-Cagnac two-sided-exponential width, and a Gaussian approximation to it).

Erickson's paper is the one row that publishes a complete budget rather than a total: 762 kHz observed (cw), from natural 330 kHz, transit 310 kHz, helium collisional 200 kHz at 4 mTorr, Rb collisional 16 kHz, Zeeman negligible.

## Use in this record

Cross-paper transit-time comparisons drawn from this table are not usable without checking each primary source's own waist and width convention. The apparent agreement in some rows may reflect matched conventions rather than a correct model. Seven of the ten primaries are held separately in this literature store: [gerginov2018](gerginov2018.md), [callejo2025](callejo2025.md), [beard2024](beard2024.md), [poulin2002](poulin2002.md), [martin2018](martin2018.md), [erickson2024](erickson2024.md) (thesis) and [lemke2022](lemke2022.md) (note pending).
