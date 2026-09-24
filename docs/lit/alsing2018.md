---
citekey: alsing2018
type: article
authors:
  - Alsing, Justin
  - Wandelt, Benjamin
title: 'Generalized massive optimal data compression'
journal: Mon. Not. R. Astron. Soc. Lett.
volume: 476
number: 1
pages: L60-L64
year: 2018
doi: 10.1093/mnrasl/sly029
arxiv: '1712.00012'
pdf: PDF_papers/Alsing_2018_generalized-massive-optimal-data-compression.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/alsing2018.md  # line-by-line against the held PDF, 2026-09-22: every cited equation (1, 4-6, 9-18) confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1712.00012v2 (3 Apr 2018). Sections 1 to 3 (Eqs. 1-18) read on
    2026-09-22; Sections 4 and 5 (use in likelihood-free inference, failure modes) were
    not read. Volume, pages and DOI confirmed against Crossref on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  The general form of MOPED: compressing N data to n numbers, one per parameter, by
  taking the SCORE (the gradient of the log-likelihood) at a fiducial point. Its
  covariance is the Fisher matrix (Eq. 6); the quasi-maximum-likelihood estimator
  built from it saturates the Cramer-Rao bound and iterates, by Fisher scoring, to the
  maximum-likelihood estimate. For Gaussian data whose mean AND covariance depend on
  the parameters, the score has a linear term (MOPED) and a quadratic term that
  carries the -1/2 ln|C| dependence (Eqs. 12-17).
loci:
  - methods/06
section: method-anchors
---

# alsing2018

VERIFIED for Sections 1 to 3. Held (arXiv v2). Read on 2026-09-22.

## What it does

Expanding the log-likelihood to second order about a fiducial point (Eq. 4), the parameters couple to the data only through the score t = grad L at that point (Eq. 5), so the score is sufficient for the linearized problem. Its covariance equals the Fisher information (Eq. 6), which saturates the information inequality (Eq. 1). The estimator theta_hat = theta* + F*^-1 grad L* (Eq. 9) has covariance F*^-1 (Eq. 10), and iterating it (Eq. 11) is Fisher scoring, converging to the maximum-likelihood estimate. For a Gaussian likelihood with parameter-dependent mean and covariance (Eq. 12, which includes the -1/2 ln|C| term), the score (Eq. 14) is the MOPED linear term plus a term quadratic in the residuals, with the trace of C^-1 dC. The Fisher matrix is Eq. (16). Linear compression is recovered when only the mean depends on the parameters, and the optimal quadratic (power-spectrum) estimator when only the covariance does.

## Use in this record

- The theoretical form of the rule this record already enforces: an objective whose weights depend on its own parameters needs the log-determinant (the rule file's "close the loop" section and F7). Eq. (14) shows exactly which term the log-determinant contributes to the information, the trace term. When the noise law scales with the signal, a compression or fit that drops it throws away information, and in this record it also biased the waist.
- With heavens2000, the benchmark for the three-way comparison: n score statistics are the most any summary can carry about n parameters at the fiducial point. The twin can compute them (it has the model and the noise law) and so price what any moment set gives up.
- A route from the moment programme to an optimal finite set: project the windowed moments onto the score directions, or compress the trace to the score and read the moments as the robustness check.

## Limits

- Optimality is local, at the fiducial point, and assumes the regularity conditions of the information inequality. Section 5 on failure modes was not read.
