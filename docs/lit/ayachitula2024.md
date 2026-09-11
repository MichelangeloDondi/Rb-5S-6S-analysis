---
citekey: ayachitula2024
type: article
authors:
  - Ayachitula, R.
  - Anderson, M. D.
  - McLaughlin, C. D.
  - Knize, R. J.
  - Mungan, C. E.
  - Lindsay, M. D.
title: 'Precision measurement of hyperfine constants and isotope shift of the Rb 6S₁/₂ state via a two-photon transition'
journal: Phys. Rev. A
volume: 110
number: 2
pages: 022803
year: 2024
doi: 10.1103/PhysRevA.110.022803
arxiv: null
pdf: PDF_papers/Ayachitula_2024_Rb-6S-hyperfine-constants-isotope-shift-kHz.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Source of A\_6S\_RB87/85\_HZ in rb5s6s/constants.py (807.355(2),
  239.065(2) MHz), and the sharpest published measurement of this
  record's own transition: an EOM sideband locked to an ultrastable
  cavity, kHz-level splittings, and the 5S-6S isotope shift far
  tighter than Orson's. It is also the closest FOIL this record has.
  The line centres come from symmetric Voigt fits and the AC Stark
  shift is entered as zero in the differential budget, because the
  beams are unfocused and wide. The body carries the numbers, and
  this record's own stark_shift_S0_mhz reproduces their calculated
  shift at their geometry.
loci:
  - P1
  - constants
section: usafa-lineage
---

# ayachitula2024

## The system

kHz-precision Doppler-free two-photon measurement of the Rb 6S1/2 hyperfine structure, both isotopes.

## The numbers

A_6S(87Rb) = 807.355(2) MHz, A_6S(85Rb) = 239.065(2) MHz. Isotope shift (85−87) = −99.189(3) MHz. 6S splitting F=3−F=2: 1614.709(3) MHz (87Rb), 717.195(3) MHz (85Rb). Line-center drift control below 0.5 kHz over 50 minutes, with centers stable to 3 kHz.

## The apparatus, which is why the Voigt is correct THERE

Read from the PDF, verbatim: "the beams are not focused and both have a FWHM diameter of
about 2.5 mm in the cell", the laser at 160 mW split 50/50 into two
counterpropagating beams, the cell at 60 C. Their error budget carries "the AC
Stark shift for any one of the four allowed transitions is calculated to be
-0.2 kHz" and sets the DIFFERENTIAL AC Stark entry to zero, alongside a
line-pulling shift of -0.6(1) kHz. Voigt fits, reduced chi-squared 1.10 to
2.05. Lorentzian fits give larger values.

A 2.5 mm intensity FWHM is a 1/e^2 radius of 2.123 mm, so at rho = 1 this
package's `stark_shift_S0_mhz` returns S0 = 0.121 kHz at 80 mW per beam and
0.243 kHz at 160 mW forward, bracketing their -0.2 kHz. Their text does not
say which side of the 50/50 split the 160 mW is quoted on. This record's
archive sits at S0 = 364 kHz, fifteen hundred times higher. **Their symmetric
Voigt is the right model at their waist**, and the difference between the two
benches is a design curve, not a disagreement.

## Validity

Supersedes Perez Galvan, Zhao & Orozco, Phys. Rev. A 78, 012502 (2008): 807.66(8) MHz (87Rb) and 239.18(3) MHz (85Rb), a shift of about 0.3 MHz, negligible for peak identification.

## Use in this record

Source of A_6S_RB87/85_HZ in rb5s6s/constants.py.
