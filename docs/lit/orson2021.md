---
citekey: orson2021
type: article
authors:
  - Orson, S. T.
  - McLaughlin, C. D.
  - Lindsay, M. D.
  - Knize, R. J.
title: 'Absolute hyperfine energy levels and isotope shift of Rb 5S–6S two-photon transition'
journal: 'J. Phys. B: At. Mol. Opt. Phys.'
volume: 54
number: 17
pages: 175001
year: 2021
doi: 10.1088/1361-6455/ac2812
arxiv: null
pdf: PDF_papers/Orson_2021_Rb-5S-6S-absolute-hyperfine-isotope-shift.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-07-29
summary: >
  Source of DELTA\_ALPHA\_AU: they compute alpha\_56=alpha(5S)-alpha(6S)
  =-1093 a.u.
loci:
  - M16
  - M4e
  - P1
  - THEORY
  - constants
section: usafa-lineage
---

# orson2021

Held. The article number 175001 and the sign convention and predicted Stark shift below were verified against the PDF.

## The system

Absolute hyperfine energy levels and the isotope shift of the Rb 5S-6S two-photon transition, measured by the same group (USAFA) as ayachitula2024, using the Perez Galvan hyperfine constants (since superseded by ayachitula2024's more precise values). Laser linewidth below 50 kHz.

## The numbers

No AC-Stark or light shift was detected in the line positions at 6 MHz spectral resolution across the laser powers used, and no density shift was observed for Rb densities from 3e11 cm^-3 upward. The isotope shift (87Rb minus 85Rb) is +94(12) MHz.

The differential polarizability alpha_56 = alpha(5S) - alpha(6S) is computed, not measured, in a manner similar to that of martin2019: alpha_56 = -1093 a.u., or -1.80e-38 J m^2 V^-2. At 0.8 W and a 63 um waist this predicts a Stark shift of -0.66 MHz, a red shift.

## Validity

The isotope shift, +94(12) MHz, is consistent with ayachitula2024's later, more precise value of +99.189(3) MHz. The paper's own predicted Stark shift also reproduces from its own equation: running its stated inputs (E^2 = 4.8e10 V^2/m^2 at 0.8 W and a 63 um waist) through this repository's unit conversion returns -0.653 MHz, matching the stated -0.66 MHz.

## Use in this record

This repository's independently computed alpha(6S) - alpha(5S) is +1145 a.u., opposite in sign to this paper's implied alpha(6S) - alpha(5S) = +1093 a.u. and 4.8% different in magnitude. Since the predicted shift itself reproduces closely, the discrepancy is not a units or convention error but one of atomic-structure calculation. Resolving it in the paper's favor would require a 33% revision to the 6s-5p3/2 radial matrix element, on which this repository's value, Safronova 2004, and Arora 2012 agree to within 0.7%.

## Values

The load-bearing numbers of this source, each at its stated
location, so a prose quote anywhere in this repository can
reference a row here and be checked against it.

| field | value | where in the paper |
|---|---|---|
| alpha_56_au | -1093 | their COMPUTED differential polarizability alpha(5S)-alpha(6S) in a.u., a calculation and not a measurement (their own AC-Stark search was a null at 6 MHz resolution, so no experiment has set this sign), the sign this record's section 5 dispute is about |
| predicted_shift_mhz | -0.66 | their predicted shift at 0.8 W and their 63 um waist, which this record's unit chain reproduces to the digit |
| isotope_shift_mhz | +94(12) | the 87-85 isotope shift |
| laser_linewidth_khz | <50 | their stated laser linewidth |
