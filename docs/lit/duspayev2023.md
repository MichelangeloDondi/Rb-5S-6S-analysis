---
citekey: duspayev2023
type: article
authors:
  - Duspayev, Alisher
  - Raithel, Georg
title: 'Spectroscopy of the ⁸⁵Rb 4D₃/₂ state for hyperfine-structure determination'
journal: New J. Phys.
volume: 25
pages: 093015
year: 2023
doi: 10.1088/1367-2630/acf405
arxiv: null
pdf: PDF_papers/Duspayev_2023_Rb-4D32-hyperfine-structure-two-photon-cold-atoms.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'No arXiv preprint identified for this record. Journal/volume/pages/DOI are
    read directly off the PDF header (New J. Phys. 25 (2023) 093015, DOI
    10.1088/1367-2630/acf405), not inferred from a database.'
verified_date: 2026-08-03
summary: >
  Two-photon (795 nm + 1476 nm) spectroscopy of laser-cooled,
  optical-lattice-trapped 85Rb resolves all four 4D3/2 hyperfine components and
  extracts A = 7.419(35) MHz, B = 4.19(19) MHz from line positions extrapolated
  to zero 1476 nm power, without using hyperfine ratios from other atomic
  levels. Also computes 4D3/2-5S1/2 magic wavelengths, 1036.3 nm for
  mJ = 3/2 and 1061.8 nm for mJ = 1/2, the tensor polarizability splitting the
  magic condition by mJ for this J = 3/2 state.
loci:
  - M16
section: landscape-24-26
---

# duspayev2023

Held. Read in full. Duspayev and Raithel, University of Michigan. Open access, published 7 September 2023.

## The system

Laser-cooled 85Rb in a 3D MOT is loaded into an intracavity 1064 nm optical lattice (column diameter ~20 um, length >=500 um, density <=1e11 cm^-3). A weak, frequency-scanned 795 nm beam (5S1/2 -> 5P1/2, F'=3, ~50 nW) and a fixed-frequency 1476 nm beam (5P1/2 -> 4D3/2) drive the 5S1/2 -> 4D3/2 two-photon transition. The 795 nm transmission is recorded while scanning through a far-detuned intermediate resonance (Delta >~150 MHz), resolving all four 4D3/2 F'' hyperfine peaks by a multi-Gaussian fit.

## The measurement

The dominant systematic is the AC Stark shift from the 1476 nm beam, up to ~18 MHz across the powers used (1.1-5.2 mW). It is removed by recording spectra at seven fixed 1476 nm powers and linearly extrapolating each hyperfine line center to zero power. The resulting zero-field frequency gaps between adjacent F'' states are nu4-nu3 = 33.0(1) MHz, nu3-nu2 = 20.4(2) MHz, nu2-nu1 = 9.7(4) MHz. Because the lowest gap carries most of the uncertainty, A and B are fit two ways: Method 1 uses only the two well-determined gaps (nu4-nu3, nu3-nu2) and is the primary result, A = 7.419(35) MHz, B = 4.19(19) MHz. Method 2 fits all three gaps, giving A = 7.37(12) MHz, B = 4.48(63) MHz as a consistency check. Against Moon et al. (2009), A = 7.329(35) MHz, the Method 1 value differs by slightly more than the combined uncertainty, while B agrees. This is the first hyperfine-structure determination for 4D3/2 that does not import a hyperfine-anomaly ratio from another Rb level.

The measured linewidth (<5 MHz at the lowest 1476 nm power) is more than twice the natural linewidth of the 4D3/2 state, Gamma_4D = 2pi x 2.02 MHz (78.7 ns lifetime), attributed to the mJ-dependence of the AC shift, the laser linewidth, and symmetric Zeeman broadening from the (<=0.5 G) MOT field. No density-dependent or DC Stark shift is observed.

## Magic wavelengths

The AC polarizability of 4D3/2 and 5S1/2 is computed versus wavelength, giving two magic wavelengths in the 1000-1200 nm band where the two polarizabilities cross: 1036.3 nm for 4D3/2 mJ = 3/2, and 1061.8 nm for mJ = 1/2, distinct because 4D3/2 is a J = 3/2 state with a nonzero tensor polarizability. 4D_J is proposed over 5D_J as a Rydberg-excitation intermediate because 4D_J ionizes at 698 nm rather than being susceptible to the large photoionization cross section 5D_J states have at 1064 nm, allowing a 1064 nm lattice to be combined with 4D_J-based excitation schemes.

## Use in this record

The two mJ-dependent magic wavelengths for 4D3/2 (J = 3/2) show, on an independent state and platform, that the tensor polarizability term is nonzero for J = 3/2 and splits the magic condition by mJ. The 5S-6S magic wavelengths used elsewhere in this record are scalar-only and exact because both 5S and 6S are J = 1/2 states, for which the tensor term vanishes by the triangle rule.
