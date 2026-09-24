---
citekey: heavens2000
type: article
authors:
  - Heavens, Alan F.
  - Jimenez, Raul
  - Lahav, Ofer
title: 'Massive lossless data compression and multiple parameter estimation from galaxy spectra'
journal: Mon. Not. R. Astron. Soc.
volume: 317
number: 4
pages: 965-972
year: 2000
doi: 10.1046/j.1365-8711.2000.03692.x
arxiv: 'astro-ph/9911102'
pdf: PDF_papers/Heavens_2000_MOPED-lossless-compression-galaxy-spectra.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/heavens2000.md  # line-by-line against the held PDF, 2026-09-22: one fiducial-model claim corrected to match the paper (no bias, only error-bar loss); Eq. 11 confirmed on a rendered-page check
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:astro-ph/9911102v2 (23 May 2000). Sections 1 to 3 (the method,
    Eqs. 1-15, and the general case) read on 2026-09-22; the worked galaxy examples of
    Section 4 were skimmed. Volume, pages and DOI confirmed against Crossref on
    2026-09-22.'
  - 'Section 4.4 (Role of fiducial model, p. 6) and the Discussion (Section 6, p. 7) read
    on 2026-09-22 to check a fiducial-model claim in summary: the paper states a wrong
    fiducial model does not bias the solution, only its error bars.'
verified_date: 2026-09-22
summary: >
  MOPED: a spectrum of about 1e3 fluxes that depends on M parameters, with noise
  independent of them, is compressed to M linear combinations y_m = b_m^T x WITHOUT
  giving up Fisher information. The weights are b proportional to C^-1 dmu/dtheta,
  Gram-Schmidt orthogonalized in the C metric, so each number is an optimal
  "window" on the spectrum for one parameter. When the noise depends on the parameters
  (photon noise), the loss is small. The weights are set at a fiducial model; the paper
  states a wrong fiducial model does not bias the result, only its error bars, and makes
  combining the M likelihoods only approximate.
loci:
  - methods/06
  - methods/11
section: method-anchors
---

# heavens2000

VERIFIED for Sections 1 to 3. Held (arXiv v2). Read on 2026-09-22.

## What it does

The data are x = mu(theta) + n with noise covariance C (Eq. 1). The Fisher matrix (Eq. 5) is the best a likelihood can do. One linear combination y = b^T x has the Fisher matrix of Eq. (7). Maximizing its information on theta_1 at fixed normalization b^T C b = 1 gives b_1 = C^-1 mu_{,1} / sqrt(mu_{,1}^T C^-1 mu_{,1}) (Eq. 11). When C does not depend on the parameters, its Fisher element equals the full data's (Eq. 12): the compression is lossless. Further parameters follow by requiring each new y_m to be uncorrelated with the previous ones and maximally informative about theta_m (Eq. 14), a Gram-Schmidt in the metric C, so that the likelihood of the M numbers is a sum of independent Gaussian terms (Eq. 15). The appendix proves losslessness for any number of parameters: the y_m are locally sufficient statistics. The weights are computed at a fiducial model and can be iterated (Section 2.0.1). With parameter-dependent noise the method is no longer exactly lossless. The worked galaxy examples (Section 4) show a modest increase in the errors, smaller than for principal component analysis.

## Use in this record

- The answer, from another field, to the question of which windows to use. The Fisher-optimal linear statistics of a line are the noise-whitened derivatives of the model line with respect to each parameter. A moment is one fixed choice of weight, x^n times a window. A MOPED vector is the weight the model itself asks for. With a correct model and a known covariance, M such numbers carry everything the whole trace carries. That is the full-profile efficiency limit the record's three-way comparison should be run against.
- It sharpens the case for moments. MOPED's optimality holds at the fiducial model, and its weights inherit that model's errors. Moments with designed immunity (power-free ratios, line-following windows) are a way of buying robustness where the fiducial model is least trusted, and the twin can measure the cost of that robustness in information.
- Also the natural bridge from moments to mu_12 to a finite, well-conditioned set: one number per parameter, optimally weighted, orthogonal by construction.

## Limits

- Linear compression with Gaussian noise, exact only when the covariance does not depend on the parameters. Local, about the fiducial point.
