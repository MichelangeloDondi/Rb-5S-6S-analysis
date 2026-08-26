---
citekey: kirankumar2011
type: article
authors:
  - Kiran Kumar, P. V.
  - Suryanarayana, M. V.
title: 'Isotope shift and hyperfine structure measurements of 4s ²S₁/₂ → 6s ²S₁/₂ two-photon transition of potassium isotopes'
journal: J. Phys. B At. Mol. Opt. Phys.
volume: 44
number: 5
pages: 055003
year: 2011
doi: 10.1088/0953-4075/44/5/055003
arxiv: null
pdf: PDF_papers/KiranKumar_2011_K-4S-6S-two-photon-isotope-shift-hyperfine.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Family name confirmed as "Kiran Kumar" (not "Kumar") against the CrossRef
    record for the DOI 2026-08-03: given "P V", family "Kiran Kumar". The
    citekey follows the repository''s existing convention for compound family
    names collapsed with no separator (IskrenovaTchoukova, CaracasNunez).'
verified_date: 2026-08-03
summary: >
  Sub-Doppler two-photon fluorescence spectroscopy of K 4s-6s (728.58 nm
  photons) in a heated vapour cell, EOM-sideband frequency calibration.
  Measures hyperfine splittings and the isotope shift to kHz-MHz precision
  and corrects an earlier isotope-shift value by 19 MHz. Measures NO
  density-dependent or intensity-dependent environmental coefficient: AC
  Stark, blackbody and pressure-broadening terms are CALCULATED or
  extrapolated from an unrelated 1937 absorption study and used only as
  systematic-error line items in a differential measurement, never as a
  reported coefficient.
loci:
  - P1
section: prior-art
---

# kirankumar2011

VERIFIED. P V Kiran Kumar and M V Suryanarayana, J. Phys. B: At. Mol. Opt. Phys. 44, 055003 (2011), National Centre for Compositional Characterisation of Materials, Hyderabad, India. DOI 10.1088/0953-4075/44/5/055003, confirmed against CrossRef and the printed PDF header. The family name is "Kiran Kumar" (given name "P V"), per the CrossRef record.

## The system and method

Natural-abundance potassium vapor (93.26% ³⁹K, 6.73% ⁴¹K) in a sealed pyrex cell heated to about 250°C (350°C for the weaker ⁴¹K lines), excited on the forbidden 4s ²S₁/₂ → 6s ²S₁/₂ two-photon line at 728.58 nm per photon with a cw Ti:Sapphire laser, retro-reflected for Doppler-free excitation, detected via cascade fluorescence at 405 nm. The laser scan is calibrated by passing the beam through a broadband electro-optic modulator and reading the equally spaced sideband peaks, removing the nonlinearity of a swept reference cavity. The wavemeter used for the absolute-frequency axis is itself calibrated against the Rb 5S₁/₂ → 7S₁/₂ two-photon transition at 394 397 906.983 kHz, a frequency-comb value from a separate group. Laser power density at the cell was about 636 W/cm² (200 mW over a roughly 200 µm beam diameter).

Potassium's ground state is 4s, so 4s→6s is a Δn=2 transition, the same class as Rb 5S→7S (zameroski2014), rather than a Δn=1 analogue of a Rb 5S→6S line.

## The numbers

- ³⁹K hyperfine splitting (F=2→F′=2 to F=1→F′=1): 418.2(5) MHz, against a prior 420(3) MHz.
- ⁴¹K hyperfine splitting: 230.4(1.3) MHz, against a prior 232(8) MHz.
- Transition isotope shift (⁴¹K − ³⁹K): 500.8(6) MHz, about 19 MHz lower than the previously reported 520(3) MHz, corrected by this measurement.
- Absolute frequency (center of gravity): ³⁹K 411 475 860 ± 10 MHz, ⁴¹K 411 476 106 ± 10 MHz, a precision improvement of about two orders over the prior ±2 GHz wavemeter measurement.
- Magnetic dipole constant A(6²S₁/₂): ³⁹K 21.8(5) MHz against an atomic-beam magnetic-resonance value of 21.81(18) MHz, and ⁴¹K 11.8(1.3) MHz against 12.03(40) MHz.
- Observed two-photon linewidths span 3.5 to 5 MHz FWHM (average 4.7 MHz), with a natural-broadening contribution estimated at about 2.04 MHz.
- Total systematic uncertainty 212 kHz against a statistical uncertainty of 480 kHz (³⁹K hyperfine splitting), overall uncertainty 525 kHz.

## Validity

The paper is a differential measurement: because only frequency differences are extracted, common-mode systematic errors cancel, and no density- or intensity-dependent environmental coefficient is reported as a measured result. Three candidate mechanisms are handled as corrections to be bounded and subtracted, not as measured physics.

- AC Stark shift: calculated from the known Rabi frequencies at the one fixed power density used (636 W/cm²), giving −212 kHz. Not measured as a function of laser power or intensity.
- Pressure (collisional) broadening: not measured in this experiment. Estimated at about 60 kHz by extrapolation from an unrelated 1937 absorption study of homogeneous K vapor (Hughes and Lloyd). No self-broadening rate or pressure-shift coefficient is fit from this paper's own data, and vapor density is not varied as an independent variable.
- Blackbody-radiation-induced dynamic Stark shift: calculated at 250°C from published dynamic polarizabilities, −1.89 kHz.

## Use in this record

This is the closest same-family alkali reference for an nS two-photon transition to a higher S state measured by isotope shift and hyperfine structure rather than by lineshape systematics. It confirms that a directly measured self-broadening or intensity-dependent shift coefficient for an alkali nS state is rare: even this measurement, aimed at hyperfine structure and isotope shift, treats every density- and intensity-dependent shift as a subtracted nuisance. zameroski2014 (Rb 7S) remains the one directly measured alkali nS self-broadening rate, and lee2010/lee2012 (Cs 6S→8S) remain the exception that reports a light shift and a power/pressure Voigt decomposition.
