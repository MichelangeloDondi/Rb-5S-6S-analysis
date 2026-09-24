---
citekey: hilton2020
type: article
authors:
  - Hilton, Ashby P.
  - Luiten, Andre N.
  - Light, Philip S.
title: 'Light-shift spectroscopy of optically trapped atomic ensembles'
journal: New J. Phys.
volume: 22
number: 3
pages: 033042
year: 2020
doi: 10.1088/1367-2630/ab753a
arxiv: '1911.02708'
pdf: PDF_papers/Hilton_2020_light-shift-spectroscopy-optically-trapped-ensembles.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/hilton2020.md  # line-by-line against the held PDF, 2026-09-22: one word corrected (product, not sum, of weighted spectra) and the cited role of Eqs. (9), (13), (15) confirmed; all other claims and the Table 1 numbers verified exactly
routing:
  - CITE
verify_flags:
  - 'The held PDF is the arXiv:1911.02708v1 preprint (7 Nov 2019). The published
    NJP version was not compared with it. Journal reference and CC-BY 4.0 licence
    from the Crossref record of the DOI, read 2026-09-22.'
  - 'Read in full, main text and both appendices, on 2026-09-22. The mapping of
    this record''s ramp onto the paper''s power-law family, and the skewness
    formula in the body, are DERIVED here from the paper''s Eqs. (9), (13) and
    (15). The paper states neither.'
verified_date: 2026-09-22
summary: >
  The nearest cold-atom precedent for reading a light-shift DISTRIBUTION off a
  line as an observable. A dipole-trapped 85Rb ensemble inside 45 um kagome
  hollow-core fibre is probed with the trap left on, and the transmission is fitted
  with a closed form, a Lorentzian integrated against a power-law shift density
  (Eq. 15, a hypergeometric function), returning temperature, trap depth, optical
  depth and linewidth from one 98 us sweep. A full-profile fit with four parameters:
  no moments, no transit or chirp, and a density taken in the harmonic approximation.
loci:
  - THEORY
  - methods/03
  - methods/09
section: prior-art
---

# hilton2020

VERIFIED. Held (arXiv v1). Read in full on 2026-09-22.

## What it does

A collimated Gaussian dipole beam holds a thermal ensemble. The radial population density comes from the Boltzmann factor with the potential expanded to second order about the axis (Appendix A), giving Eq. (4), a Gaussian of 1/e radius w/sqrt(2 alpha) with alpha = -U0/(kB T) the trap depth in units of the thermal energy. The paper then changes variable to the light shift using the exact Gaussian intensity (Eqs. 10-13): the shift density is a power law, proportional to delta^(alpha-1) on (0, -U0/hbar]. The probe, mode-matched to the trap beam, weights each atom by the local intensity, so the absorbing weight goes as delta^alpha, and its integral is the geometric overlap eta = alpha/(1 + alpha) (Eq. 9). Integrating a Lorentzian of width Gamma_p against that weight gives the transmission in closed form through 2F1(1, alpha+1; alpha+2; z) (Eq. 15), which the authors fit in real time over four parameters: alpha, U0, Gamma_p and the optical depth.

Section 3 and Fig. 2 give each parameter's signature. alpha shapes the low-frequency side, U0 sets the extent, Gamma_p sharpens the high-detuning edge made by the atoms nearest the axis, and the optical depth scales the whole. The paper notes that alpha and U0 are interdependent at fixed temperature. Section 4 and Appendix B build a ring-like (circular-orbit) density as an alternative. It matches depth, position and width but not the asymmetry, and its fitted parameters are unphysical, so the Gaussian density is retained.

The experiment (Section 5): an 85Rb MOT of about 1e9 atoms above 10 cm of 45 um-core kagome hollow-core photonic-crystal fibre. A 1 W dipole beam is detuned 1 THz below D1 and coupled from below. A counter-propagating D2 probe on F=3 to F'=4 is stepped over 144 MHz in a single 98 us window by pre-programmed AOM waveforms, with the trap on throughout.

## The numbers (Table 1, Gaussian model)

| data | alpha | T (mK) | -U0/h (MHz) | optical depth | Gamma_p/2pi (MHz) |
|---|---|---|---|---|---|
| this paper | 1.0(1) | 4.0(4) | 81(1) | 2.8(3) | 16(2) |
| Peyronel et al. data | 1.59(7) | 5.4(2) | 177(1) | 8.0(6) | 17(1) |

The fitted linewidth is 16 to 17 MHz against a natural width near 6 MHz. The paper attributes the excess to differential light shifts between m_F sublevels, which its model leaves out, and proposes a product of 2n+1 weighted spectra as the fuller fit.

## Mapping onto this record's ramp (derived here, not in the paper)

From Eqs. (9) and (13), the normalized absorbing weight over the shift is (alpha+1) delta^alpha / S^(alpha+1) on (0, S], with S = -U0/hbar: a Beta(alpha+1, 1) density scaled by S. This record's static ramp, f(s) = 2 s / S0^2, is the member with exponent one. Here the power comes from a uniform vapour density with the two-photon excitation weight going as the square of the intensity, where the paper's comes from a thermal density with a linear probe weight. The absorbance inside Eq. (15) at alpha = 1 is therefore, algebraically, the Lorentzian convolved with the static ramp. That is the canonical convolution this record tests at 42.4 um, not the volume model.

The family's standardized skewness follows from the Beta form:

skewness(alpha) = -2 alpha sqrt(alpha + 3) / ((alpha + 4) sqrt(alpha + 1)),

which gives -2 sqrt(2)/5 = -0.566 at alpha = 1, the ramp's own value. It runs monotonically from 0 at alpha = 0 to -2 as alpha goes to infinity, and it does not contain U0 or the optical depth. A power-free shape coordinate would therefore return alpha, the trap depth over the temperature, with no calibration of the depth. With a Lorentzian kernel the untruncated moments do not exist, so in practice this is a windowed statistic whose bias the twin must supply, which is this record's method.

## Use in this record

- Prior art to cite and delineate from. Reading the parameters of an optically trapped ensemble from the shape of its light-shift-broadened line is published, by a hollow-core-fibre group, with a full-profile fit. This record's additions are the windowed moments with their bias measured on the twin, the transit and its chirp, the two-photon weighting, and the comparison between the two estimators.
- For the application to a guided-atom group: the derived skewness-alpha map shows, in their own geometry, what a power-free coordinate gives: the ratio of trap depth to temperature from the shape alone.
- The unmodelled m_F spread, which roughly triples the fitted width, is the kind of missing term that the twin's residual tests exist to name before a width is read.

## Limits

- The density uses the harmonic expansion of Appendix A, while the paper's own fitted alpha is 1.0(1), where atoms sample the anharmonic part of the potential. The paper does not discuss validity at that alpha.
- The density is uniform along the fibre over a length L. In a collimated guided mode that is plausible, but it is assumed, not tested.
- The quoted uncertainties are fit errors. The paper gives no systematic budget.
