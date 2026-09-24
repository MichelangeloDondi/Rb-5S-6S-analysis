---
citekey: gourieroux2000
type: inproceedings
authors:
  - Gourieroux, C.
  - Renault, E.
  - Touzi, N.
title: 'Calibration by simulation for small sample bias correction'
journal: 'Simulation-based Inference in Econometrics: Methods and Applications (Cambridge University Press)'
pages: 328-358
year: 2000
doi: 10.1017/CBO9780511751981.018
arxiv: null
pdf: PDF_papers/Gourieroux_2000_calibration-simulation-small-sample-bias-correction.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/gourieroux2000.md  # line-by-line against the held 1995 working paper, 2026-09-22: every cited proposition, corollary and Table 2.1 figure confirmed exactly (including all six AR(2) Monte Carlo numbers); no corrections needed
routing:
  - CITE
verify_flags:
  - 'The held PDF is the working-paper version (July 1994, revised July 1995), posted for a Federal Reserve Bank of Minneapolis conference of November 1995, not the book chapter of 2000; the chapter''s page range and DOI are from Crossref, and its numbering may differ from the preprint''s. Read on 2026-09-22: the abstract, introduction, Section 1 (Proposition 1.1 and Examples 1 and 2), the statements of Section 2 (Proposition 2.1 and Corollary 2.1) and Section 3''s tables; the appendix proofs are not read.'
verified_date: 2026-09-22
summary: >
  Indirect inference as an exact small-sample bias correction. When the auxiliary
  estimator has as many parameters as the model, indirect inference with infinitely
  many simulations returns the parameter at which the finite-sample mean of the
  simulated estimates equals the observed estimate: the inverse of the finite-sample
  binding function. That estimator is exactly unbiased in the sense of a generalized
  mean, and unbiased to second order under an Edgeworth expansion, like the bootstrap.
  Unlike the bootstrap, the second-order property fails for a fixed number of
  simulations, although the first-order bias still vanishes. It is the mean analogue of
  Andrews' median-unbiased estimator for AR models. In AR(1) and AR(2) simulations it and
  the median-unbiased estimator are close, while least squares is strongly biased.
loci:
  - P1
  - methods/06
section: method-anchors
---

# gourieroux2000

VERIFIED for the parts named in the flags. Held (1995 working-paper version).

## What it does

Section 1 recalls indirect inference (Smith, then Gallant and Tauchen, then Gourieroux, Monfort and Renault): an auxiliary estimator beta_hat summarises the data, the same estimator is applied to paths simulated at theta, and theta is chosen to match the two. The paper studies the case where the auxiliary model has as many parameters as the true one, so the weighting matrix drops out. With infinitely many simulations the estimator is theta_hat = b_T^-1(beta_hat), where b_T(theta) = E[beta_hat(theta)] is the finite-sample binding function (Eqs. 1.5-1.7). Proposition 1.1 shows it is exactly b_T-mean unbiased, and that it reduces to the first-step estimator when that is already unbiased. Two examples follow: a normal variance, where the binding function is linear and the correction gives the familiar T/(T - 1) factor, and a binding function that is a power of the parameter. The connection to Andrews (1993) is that his estimator inverts the median of the least-squares estimator where this one inverts its mean.

Section 2 assumes an Edgeworth expansion of the auxiliary estimator and shows that the indirect-inference estimator with infinitely many simulations is unbiased to second order (Proposition 2.1, Corollary 2.1). With a fixed number H of simulations the first-order bias still vanishes but the second-order bias does not, which is where it differs from the bootstrap. The authors compare the two to third order and find no dominance. Section 3 simulates AR(1) and AR(2) models at T = 40 with H = 5000 over 1000 experiments. For AR(2) coefficients of 1.2 and -0.4, least squares averages 0.936 and -0.191, the median-unbiased procedure 1.191 and -0.396, and indirect inference 1.202 and -0.406 (Table 2.1).

## Use in this record

- The formal version of calibrating the twin to the data. Find the truth at which the twin's mean fitted value equals the data's fitted value. The fit itself is the auxiliary estimator, with as many parameters as the model, and the twin's grid of truths samples the finite-sample binding function. Interpolating that grid and inverting it is this estimator, and mackinnon1998 gives its variance, 1/(1 + b') times the uncorrected spread per parameter.
- The number of twin replicas enters the bias as well as the noise. With few replicas per truth the second-order correction is lost, so the replica count behind each grid point is part of the correction's specification.
- It sits with gourieroux1993 (indirect inference), mackinnon1998 (the same inversion as a bias correction), barlow1993 (bias from template noise) and newey2004 (the analytic bias of moment estimators).

## Limits

- Exactly identified auxiliary models, a correctly specified simulator, and small autoregressive examples. It gives no guidance when the binding function is known only at a few grid points, and nothing on intervals.
