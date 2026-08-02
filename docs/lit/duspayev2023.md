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

**Read here 2026-08-03, in full (12 pages).** Duspayev and Raithel, University
of Michigan. Open access, published 7 September 2023.

Verbatim abstract: "We report a measurement of the hyperfine-structure
constants of the 85Rb 4D3/2 state using two-photon optical spectroscopy of the
5S1/2 -> 4D3/2 transition. The spectra are acquired by measuring the
transmission of the low-power 795 nm lower-stage laser beam through a
cold-atom sample as a function of laser frequency, with the frequency of the
upper-stage, 1476 nm laser fixed. All 4 hyperfine components of the 4D3/2
state are well-resolved in the experimental data. The dominant systematic is
the light shift from the 1476 nm laser, which is addressed by extrapolating
line positions measured for a set of 1476 nm laser powers to zero laser
power. The analysis of our experimental data yields both the magnetic-dipole
and electric-quadrupole constants for the 85Rb 4D3/2 level, without using
earlier hyperfine measurements of other atomic levels. The respective
results, A = 7.419(35) MHz and B = 4.19(19) MHz, are discussed in context
with previous works. Our investigation may be useful for optical atomic
clocks for precision metrology and emerging atom-based quantum technologies,
all-infrared excitation of Rb Rydberg levels, and molecular physics."

## What it does

85Rb atoms are laser-cooled in a 3D MOT and loaded into an intracavity 1064 nm
optical lattice (column diameter ~20 um, length >=500 um, density <=1e11
cm^-3). A weak, frequency-scanned 795 nm beam (5S1/2 -> 5P1/2, F'=3, ~50 nW)
and a fixed-frequency 1476 nm beam (5P1/2 -> 4D3/2) drive the two-photon
transition. The 795 nm transmission is recorded as the 795 nm laser scans
through a far-detuned intermediate resonance (Delta >~150 MHz), resolving all
four 4D3/2 F'' hyperfine peaks by multi-Gaussian fit.

The dominant systematic is the AC Stark (light) shift from the 1476 nm beam,
up to ~18 MHz across the powers used (1.1-5.2 mW). It is removed by
recording spectra at seven fixed 1476 nm powers and linearly extrapolating
each hyperfine line center to zero power (figure 5). The resulting zero-field
frequency gaps between adjacent F'' states (table 1) are nu4-nu3 = 33.0(1)
MHz, nu3-nu2 = 20.4(2) MHz, nu2-nu1 = 9.7(4) MHz. Because the lowest gap
carries most of the uncertainty, the paper fits A and B two ways: Method 1
uses only the two well-determined gaps (nu4-nu3, nu3-nu2), Method 2 fits all
three gaps. Method 1 is reported as the primary result, A = 7.419(35) MHz,
B = 4.19(19) MHz. Method 2 gives A = 7.37(12) MHz, B = 4.48(63) MHz as a
consistency check. Against earlier work the A value differs from Moon et al
(2009) [46], A = 7.329(35) MHz, by slightly more than the combined
uncertainty, while B agrees. This is the first HFS determination for 4D3/2
that does not import a hyperfine-anomaly ratio from another Rb level.

The measured linewidth (<5 MHz at the lowest 1476 nm power) is more than
twice the natural linewidth of the 4D3/2 state, Gamma_4D = 2pi x 2.02 MHz
(78.7 ns lifetime), attributed to the mJ-dependence of the AC shift, laser
linewidth, and symmetric Zeeman broadening from the (<=0.5 G) MOT field. No
density-dependent or DC Stark shift is observed. Section 3.3 separately
computes the AC polarizability of 4D3/2 and 5S1/2 versus wavelength (figure
6) and finds two 'magic' wavelengths in the 1000-1200 nm band where the two
polarizabilities cross: 1036.3 nm for 4D3/2 mJ = 3/2, and 1061.8 nm for
mJ = 1/2, distinct because 4D3/2 is a J = 3/2 state with a nonzero tensor
polarizability. The paper motivates 4D_J over 5D_J as a Rydberg-excitation
intermediate specifically because 4D_J ionizes at 698 nm rather than being
susceptible to the large photoionization cross section 5D_J states have at
1064 nm, so a 1064 nm lattice can be combined with 4D_J-based schemes without
that complication.

## Bridges to this repository

**Genuine, modest.** This paper and duspayev2024 (already held, `FEED`/`M16`,
`docs/lit/duspayev2024.md`) are a sibling pair from the same group on the same
5S1/2+1476 nm -> 4D_J platform, the 2023 paper doing the HFS characterization
and the 2024 paper turning it into a clock proposal. Section 3.3's magic
wavelengths for 4D3/2 are an independent illustration of the same
polarizability-crossing method M16 uses for 5S-6S, applied to a different
state pair, so it belongs alongside duspayev2024 under the `M16` locus, not as
a numeric input but as a family cross-reference.

More specifically useful: this paper is a clean external example of *why*
`RESULTS.md`'s scalar-only 5S-6S magic wavelengths are exact only because 5S
and 6S are both J = 1/2 (their tensor term vanishes by the triangle rule).
4D3/2 is J = 3/2, and this paper shows the tensor term is not negligible
there, splitting one magic condition into two mJ-dependent wavelengths
1036.3 nm and 1061.8 nm. It is independent confirmation, from a different
group and a different state, of the J-dependence our repository states but
does not itself demonstrate on a J > 1/2 example.

**Everything else is a plain no-bridge.** The paper's actual measurement (HFS
constants of a Rydberg-adjacent D-state in a laser-cooled, optical-lattice
sample) has no collisional or Doppler broadening at all, so it does not touch
this programme's self-broadening coefficient, van der Waals, or pressure-shift
work. Its handling of the AC Stark systematic is also a genuine methodological
contrast rather than a reusable technique: with a small, laser-cooled atom
column the 1476 nm intensity each atom sees is close to a single value, so a
shift-vs-power linear extrapolation across separate spectra is sufficient. Our
warm-vapor 5S-6S line instead has atoms sampling a continuum of intensities
within one Gaussian-beam transit, which is why this programme reads a light-
shift DISTRIBUTION out of a single lineshape's cumulants rather than
extrapolating a single shift to zero power. The paper does not attempt any
lineshape-as-distribution reading, moment or cumulant analysis, or
drift-immune channel, so it does not bear on that side of the programme (the
delone1980 / Hunt-2 family of distribution-from-lineshape analogues) at all.
