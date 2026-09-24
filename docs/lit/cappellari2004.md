---
citekey: cappellari2004
type: article
authors:
  - Cappellari, Michele
  - Emsellem, Eric
title: 'Parametric recovery of line-of-sight velocity distributions from absorption-line spectra of galaxies via penalized likelihood'
journal: Publ. Astron. Soc. Pac.
volume: 116
pages: 138-147
year: 2004
doi: 10.1086/381875
arxiv: 'astro-ph/0312201'
pdf: PDF_papers/Cappellari_2004_penalized-likelihood-LOSVD-Gauss-Hermite.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/cappellari2004.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, every checked claim confirmed within Sections 1-3.3 and the start of 3.4
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:astro-ph/0312201v1 (8 Dec 2003), read on 2026-09-22 through
    Section 3.3 and the start of 3.4. Page range and DOI confirmed against Crossref on
    2026-09-22.'
verified_date: 2026-09-22
summary: >
  The galaxy-kinematics counterpart of this record's shape channel. A velocity
  distribution is read off a spectrum through Gauss-Hermite coefficients h3 (odd,
  asymmetry) and h4 (even, peakedness) beside the centre V and width sigma. When the
  profile is under-sampled or the S/N is low, h3 trades against V and h4 against sigma
  along a narrow chi-squared valley. Fitting V and sigma first suppresses the shape
  terms; fitting all four inflates the scatter and biases sigma low and h4 high. A
  penalty proportional to chi^2 times the squared deviation from a Gaussian keeps only
  the shape the data support, with its strength calibrated on simulations.
loci:
  - methods/06
  - methods/10
section: method-anchors
---

# cappellari2004

VERIFIED through Section 3.3. Held (arXiv v1). Read on 2026-09-22.

## What it does

The model spectrum is a set of templates convolved with a velocity distribution written as a Gauss-Hermite series, L(v) proportional to a Gaussian times [1 + sum over m >= 3 of h_m H_m(y)] with y = (v - V)/sigma (Eqs. 3-4), fitted in pixel space. The test profile is a realistic double Gaussian, whose best four-term fit has h3 = -0.150 and h4 = 0.036 (Fig. 1). Three strategies are compared on simulated spectra, 1000 realizations at S/N = 60 and 100 at S/N = 600, with the width scanned from 48 to 360 km/s (0.8 to 6 pixels):

- V and sigma first, then h3 and h4 linearly (Section 3.1, Fig. 3). The shape coefficients are biased once sigma is below about 4 pixels, and the method becomes insensitive to any non-Gaussianity below about 2 pixels at any S/N, even without noise. The paper explains it: an asymmetry can be absorbed by a small shift of V, and a symmetric deviation by a change of sigma.
- All four together (Section 3.2, Figs. 4-5): almost unbiased, but at S/N = 60 below about 2 pixels h3 and h4 are unmeasurable. sigma comes out systematically low and h4 high, because of a narrow curved valley of nearly constant chi-squared in (sigma, h4).
- Penalized (Section 3.3): the penalty is the integrated squared deviation from the best Gaussian, approximately the sum of h_m^2 (Eqs. 7-8), entered by perturbing the residuals (Eq. 9) so that the objective becomes chi^2 (1 + lambda^2 D^2) (Eq. 12). A departure from a Gaussian is kept only if it lowers the residual scatter enough. The paper advises choosing lambda by simulation and uses 0.7: unbiased above 2 pixels at S/N = 60, and convergence to the true shape at S/N = 600 (Fig. 6).

## Use in this record

- The degeneracy structure is the same as this record's: the odd shape term trades against the centre and the even shape term against the width. Here it is shown with a chi-squared valley and a simulation, the evidence this record's identifiability table and twin are meant to produce for the ramp's moments.
- Sequential against joint estimation: fixing the centre and width first and then reading the shape suppresses the shape. That is a warning for any analysis that reads higher moments about a centroid fitted separately, and an argument for the joint likelihood the programme uses.
- A shrinkage prescription with a clear statistical reading: the shape parameters are pulled to the symmetric model unless the data pay for them, with the strength set by simulation. It is a candidate for the high orders of this record's moment set, and the twin is where its lambda would be calibrated.

## Limits

- Gauss-Hermite coefficients are not moments. The paper stresses that the fitted coefficients coincide with the true Gauss-Hermite moments of the distribution only when V and sigma are fixed first.
