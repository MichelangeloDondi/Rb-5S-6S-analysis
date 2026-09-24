---
citekey: arguelles2019
type: article
authors:
  - Argüelles, C. A.
  - Schneider, A.
  - Yuan, T.
title: 'A binned likelihood for stochastic models'
journal: J. High Energy Phys.
volume: 2019
number: 6
pages: 030
year: 2019
doi: 10.1007/JHEP06(2019)030
arxiv: '1901.04645'
pdf: PDF_papers/Arguelles_2019_binned-likelihood-finite-Monte-Carlo.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/arguelles2019.md  # line-by-line against the held PDF, 2026-09-22: Eqs. 2.2, 2.3-2.5, 3.12-3.16 and the public-code claim (ref. [8], a GitHub link) confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1901.04645v2 (27 May 2019). Read on 2026-09-22: abstract,
    Sections 1 and 2 (Poisson likelihood, Barlow-Beeston, the large-sample limit) and
    Section 3.3 (the effective likelihood, Eqs. 3.12-3.16). The coverage and performance
    studies of Section 4 were not read. Journal reference and DOI
    confirmed against Crossref on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  When a likelihood's expected counts come from a finite Monte Carlo (a simulation of
  the experiment), the simulation's own statistical error must be in the likelihood,
  or the fit makes overconfident and biased claims. The paper reviews the ad-hoc
  substitution, Barlow-Beeston profiling and the large-sample variance-added
  chi-squared, and derives an "effective" Poisson likelihood that integrates the
  expected count over a gamma distribution set by the Monte Carlo weights' sum mu and
  variance sigma^2 (Eqs. 3.12-3.16). It is valid for small and large samples, with better
  coverage, and code is public.
loci:
  - methods/06
  - P2
section: method-anchors
---

# arguelles2019

VERIFIED for the sections named in the flags. Held (arXiv v2). Read on 2026-09-22.

## What it does

A binned Poisson likelihood needs the expected count lambda(theta), which in complex experiments is estimated from weighted Monte Carlo events. Substituting the sum of weights directly (Eq. 2.2) ignores that the sum is itself random. Barlow and Beeston profile the unknown true Monte Carlo count per process (Eq. 2.4, their 1993 method). In the large-sample limit a Gaussian chi-squared with the Monte Carlo variance added is used. The paper instead treats the expected count as uncertain with a gamma distribution whose shape and rate come from the weights' mean and variance, alpha = mu^2/sigma^2 + 1 and beta = mu/sigma^2 (Eqs. 3.12-3.13). It integrates the Poisson term against it in closed form, giving the effective likelihood of Eqs. 3.14-3.16. The paper reports better coverage and a test statistic closer to Wilks' distribution than the alternatives.

## Use in this record

- This record's likelihood compares data with expectations computed by the twin from finite replicas: biases per window and simulated means of statistics. The same principle binds. The replicas' own scatter belongs in the likelihood, or the fit is over-confident in proportion to how few replicas were run.
- Directly applicable to the counting-mode branch the rule file requires for the fibre arm. Photon counts binned against a simulated expectation are exactly this paper's setting.

## Limits

- Poisson counts per bin, uncorrelated between bins. The Gaussian-summary case this record's moment likelihood uses is covered by Hartlap-type covariance corrections (hartlap2007, sellentin2016), not by this paper.
