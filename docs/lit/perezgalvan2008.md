---
citekey: perezgalvan2008
type: article
authors:
  - Pérez Galván, A.
  - Zhao, Y.
  - Orozco, L. A.
title: 'Measurement of the hyperfine splitting of the 6S1/2 level in rubidium'
journal: Phys. Rev. A
volume: 78
number: 1
pages: 012502
year: 2008
doi: 10.1103/PhysRevA.78.012502
arxiv: '0807.1438'
pdf: PDF_papers/PerezGalvan_2008_Rb-6S-hyperfine-splitting-anomaly.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:0807.1438v1 preprint (9 Jul 2008); volume, article number and DOI are
    Crossref''s record, checked 2026-09-22. Read in full on 2026-09-22; Section II''s nuclear-structure
    background is read for its conclusions, since nothing below rests on its formulas.'
verified_date: 2026-09-22
summary: >
  The 6S1/2 hyperfine splitting of both isotopes by stepwise excitation, 795 nm locked on 5S to 5P1/2
  and 1.324 um scanned to 6S, in a room-temperature glass cell, with electro-optic sidebands as an in
  situ frequency scale interpolated to zero separation: A = 239.18(3) MHz for 85Rb and 807.66(8) MHz
  for 87Rb, a hyperfine anomaly of -0.0036(2), with a systematic budget (Table III, printed p. 10)
  covering optical pumping, both lasers' powers, atomic density, the line-centre fit and the field,
  and the scan's piezo non-linearity and hysteresis checked only qualitatively (up and down scans
  compared, no effect found, printed p. 9). The earlier 6S
  hyperfine constants beside orson2021 and ayachitula2024, and a sideband-ruler method of the kind the
  2025 record uses.
loci:
  - constants
section: method-anchors
---

# perezgalvan2008

VERIFIED against the held preprint (scope in `verify_flags`).

## The method

Counter-propagating 795 nm and 1.324 um beams cross a natural-abundance Rb cell in a shielded solenoid. The 795 nm Ti:sapphire laser is locked to the D1 line and the diode at 1.3 um is scanned over the 6S1/2 hyperfine pair, the signal being the change in 795 nm absorption (their Figs. 2 and 5). A five-level density-matrix model explains why that absorption can rise or fall at resonance, through optical pumping into or out of the other ground hyperfine level (Figs. 3, 4 and 8). The frequency scale is set by sidebands on the 1.3 um beam: the sideband-to-carrier separation is measured against the modulation frequency above and below half the splitting, and, verbatim, "We interpolate to zero separation to obtain half the hyperfine splitting (see Fig. 7)." In the authors' words, verbatim: "This technique transfers an optical frequency measurement to a much easier frequency measurement in the RF range."

## What it finds

The splittings are 717.54(10) MHz for 85Rb and 1615.32(16) MHz for 87Rb, so A = 239.18(03) MHz and 807.66(08) MHz (Table IV). With the nuclear g-factor ratio of their reference 44 the hyperfine anomaly difference is -0.0036(2), matching the 5S1/2 value and attributed to the Bohr-Weisskopf effect. The statistical error dominates, 0.100 and 0.160 MHz, against total systematics of at most 0.047 MHz each (Table III).

On line shape: Voigt fits converge to their Lorentzian limit, the counter-propagating geometry and the stepwise velocity selection suppressing the Doppler part, and verbatim: "Of the fitted functions Lorentzians yield the smallest χ2 ." The reduced chi-square averages 2.4 over twenty fits, the Lorentzian and Gaussian separations differ by 0.35(68) MHz, and the residuals share structure within the linewidth, which the authors explain, verbatim: "We have determined that these features come about from the high sensitivity from deviations from a perfect fit that a difference of two peak profiles has." On the scan, verbatim: "Non-linearities in the piezo driving the feedback grating, hysteresis effects as well as a slow thermal drift on the 1.3 µm laser can generate undesired systematics in the measurement." They compared up- and down-going scans and found no systematic effect.

## Use in this record

The 2025 line's four peaks are the 5S to 6S hyperfine components, so the 6S constants set their separations. This paper is the earlier measurement beside the shelf's `orson2021` and `ayachitula2024`, which report the constants at higher precision and are the ones to feed a number. Its own values are for comparison. Its method is closer to this record's than the numbers: electro-optic sidebands as an in situ ruler, as in the 2025 RF-on traces, and a systematic budget that names piezo non-linearity and scan hysteresis, two of the quantities the owner's programme wants the experiment to calibrate itself. Its lines, 30 to 40 MHz wide from a stepwise excitation through the resonant 5P1/2 level, are not the 2025 lines, whose excitation is degenerate two-photon at 993 nm far from any intermediate resonance.

Related on this shelf: `orson2021` (the 5S to 6S hyperfine and isotope shifts at 993 nm), `ayachitula2024` (the 6S hyperfine constants and isotope shift at kilohertz precision), `nieddu2019` (the 993 nm frequency reference of this line's lineage).
