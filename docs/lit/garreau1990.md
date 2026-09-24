---
citekey: garreau1990
type: article
authors:
  - Garreau, J. C.
  - Allegrini, M.
  - Julien, L.
  - Biraben, F.
title: 'High resolution spectroscopy of the hydrogen atom. II. Study of line profiles'
journal: J. Phys. France
volume: 51
number: 20
pages: 2275-2292
year: 1990
doi: 10.1051/jphys:0199000510200227500
arxiv: null
pdf: PDF_papers/Garreau_1990_hydrogen-two-photon-line-profiles-light-shift.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/garreau1990.md  # line-by-line against the held PDF, 2026-09-22: every cited equation/section/figure/table number and quantity confirmed against page images; four small corrections (an anachronistic lab name, a working-role mention, an incomplete species list, a dangling citekey)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (EDP Sciences archive, downloaded directly; the HAL copy is behind a bot check). Its text layer is OCR, so the equations are images and are cited by number only. Read in full on 2026-09-22 (Sections 1 to 5; the appendix on dipole matrix elements skimmed). Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The classic two-photon line-shape analysis with the light shift varying along each
  atomic trajectory (hydrogen 2S-nD at the Laboratoire de Spectroscopie Hertzienne de
  l'ENS, towards the Rydberg constant). Each straight trajectory through the Gaussian
  standing wave sees a varying excitation rate and light shift. The destruction
  probability is summed over all trajectories between two diaphragms, and the
  remaining broadenings enter as a Gaussian convolution. The fit returns the light
  power and the light-shift-corrected position. The line's ASYMMETRY fixes a
  geometric parameter of the atom-beam overlap (a virtual diaphragm radius
  R1 = 1.5 mm), and the extrapolation's residual slope checks it. The line-shape
  uncertainty is 13 kHz, 1.7e-11.
loci:
  - THEORY
  - methods/03
  - methods/04
section: prior-art
---

# garreau1990

VERIFIED. Held (published version, OCR text). Read in full on 2026-09-22.

## What it does

The 2S-nD lines of hydrogen and deuterium are excited in a metastable beam collinear with a standing wave in an enhancement cavity (beam radius about 0.6 mm, diaphragms 7 mm in diameter 956 mm apart). The observed width is about 1 MHz against a 296 kHz natural width for 10D (Section 2). The light shift at the beam centre is about 560 kHz at 50 W per direction. Section 2.4 names the light shift and saturation as the dominant broadenings, both through the intensity an atom sees varying along its trajectory. Section 3 computes the two-photon rate and light-shift coefficients from second-order perturbation theory, with the continuum included (Eqs. 3-7, Table I). Along each straight trajectory the intensity follows the Gaussian mode (Eq. 8), and the transition probability integrates the local rate with the local detuning, including the shift (Eq. 9). This assumes the intensity varies slowly against the excited-state lifetime. Hyperfine pumping and cascade repopulation of 2S enter through rate equations (Eq. 10). The signal sums Eq. (10) over trajectories whose impacts are uniform on the exit diaphragm and on a virtual entrance diaphragm of radius R1 (Eq. 11), with a mean velocity replacing the velocity distribution, which is tested at 3 per cent at 50 W (Section 3.3). The computed lines are blue-shifted and asymmetric at high power, and the apparent light shift is slightly non-linear because of saturation (Figs. 5-7).

## The fit and the numbers

Every broadening left out of the calculation (laser width, transit, second-order Doppler, Stark, Zeeman) enters as a convolution with a Gaussian. Each recording is fitted with four parameters: the off-resonance metastable yield, the light power P, the light-shift-corrected line position (CLP) and the Gaussian width (Section 4.1). The residuals show no systematic error (Fig. 8). R1 is chosen by the line shape itself. At R1 = 3.5 mm the computed asymmetry is too large, and at 1.5 mm the discrepancy disappears (Fig. 9). The CLP-against-power slope, which should be zero, is very sensitive to R1 and nearly zero at 1.5 mm (Figs. 11-12). The fitted power tracks the intracavity photodiode, but the fitted straight line does not pass through the origin, a systematic the authors say shows the limits of the procedure (Fig. 10, Table III). The light-shift correction is better than 91 per cent in all but one transition (Table IV). The line-shape uncertainty is the sum of the CLP-against-P versus CLP-against-photodiode difference (mean -11 kHz, taken as +/- 8 kHz) and the R1 dependence (5 kHz): 13 kHz, a relative 1.7e-11, rounded to 2e-11 (Section 4.3, Table V).

## Use in this record

- The earliest held precedent for this record's volume idea in a two-photon line: the shift and the excitation computed along each trajectory through a Gaussian mode and summed, not a single shift convolved with a kernel. It sits beside kolachevsky2006 (a Monte Carlo of the same kind for 1S-2S) and Haas 2006 (paywalled, not held).
- The line's odd shape as a measurement of the sampled intensity distribution: the asymmetry fixed R1, the parameter setting which intensities the atoms see, and the power was fitted from the line. That is the move this record makes with the waist and S0, made in 1990 through a trajectory model instead of through moments. A novelty claim about reading geometry off a light-shifted two-photon line has to be positioned against this paper.
- A hybrid worth naming: trajectory physics for the intensity-dependent terms, with a Gaussian convolution for the rest. That is the canonical compromise this record's convolution-condition section discusses. Here it is justified because the convolved terms do not depend on position.

## Limits

- Collinear geometry with long transit times, hydrogen and deuterium beams, and the mean-velocity approximation. The paper does not treat moments, window truncation or estimator bias, and the fitted parameters carry the systematic shown in Fig. 10.
