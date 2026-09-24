---
citekey: chernozhukov2018
type: article
authors:
  - Chernozhukov, Victor
  - Chetverikov, Denis
  - Demirer, Mert
  - Duflo, Esther
  - Hansen, Christian
  - Newey, Whitney
  - Robins, James
title: 'Double/debiased machine learning for treatment and structural parameters'
journal: Econom. J.
volume: 21
number: 1
pages: C1-C68
year: 2018
doi: 10.1111/ectj.12097
arxiv: '1608.00060'
pdf: PDF_papers/Chernozhukov_2018_double-debiased-ML-orthogonal-scores.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/chernozhukov2018.md  # line-by-line against the held PDF, 2026-09-22: Eq. 1.8, Definition 2.1/Eq. 2.3, Eqs. 2.5-2.10 and Lemma 2.1 all confirmed exactly, symbol for symbol; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1608.00060v7 (3 Nov 2024), 71 pages. Read on 2026-09-22 for
    one purpose only, the definition and construction of Neyman-orthogonal scores: the
    summary, the passage around Eq. (1.8), Definition 2.1 (Eq. 2.3) and Section 2.2.1
    (Eqs. 2.5-2.10, Lemma 2.1). The machine-learning, cross-fitting and asymptotic
    theory is unread and nothing below rests on it. Journal volume, pages and DOI
    confirmed against Crossref on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  Cited here for Neyman orthogonality: a moment condition (score) is orthogonal to a
  nuisance when its expectation has zero derivative with respect to the nuisance at
  the truth (Eq. 1.8, Definition 2.1), so an error in the nuisance does not bias the
  target to first order. Neyman's 1959 construction makes any likelihood score
  orthogonal by projecting out the nuisance score, psi = d_theta l - mu d_beta l with
  mu = J_theta_beta J_beta_beta^-1 (Eqs. 2.7-2.10, Lemma 2.1). Invariant ratios are
  the exact, global version of what this makes local.
loci:
  - methods/06
section: method-anchors
---

# chernozhukov2018

VERIFIED for the passages named in the flags. Held (arXiv v7). Read on 2026-09-22.

## What the read passages say

A naive estimating equation for theta that plugs in an estimated nuisance g inherits the nuisance's bias, because the Gateaux derivative of its expectation with respect to g does not vanish. An orthogonalized score psi has that derivative zero at the true values (Eq. 1.8): the moment conditions are locally insensitive to the nuisance, so a noisy nuisance estimate can be plugged in without strongly violating them. The formal definition, with an approximate version, is Definition 2.1 (Eq. 2.3). In a likelihood setting with a finite-dimensional nuisance beta, Neyman's construction takes the target score minus a matrix mu times the nuisance score (Eq. 2.7), with mu solving J_theta_beta - mu J_beta_beta = 0 (Eqs. 2.8-2.10), and Lemma 2.1 proves orthogonality. The paper traces this to Neyman's C(alpha) statistic.

## Use in this record

- The statistics name for what the power-free and waist-free combinations do, and a recipe for the cases where no exact invariant exists. This record's twin supplies the Jacobians J, so any chosen moment coordinate can be made locally insensitive to a named nuisance (the laser width, the transit, the waist) by subtracting its projection on that nuisance's direction.
- An exactly invariant ratio is orthogonal to the nuisance globally. An orthogonalized coordinate is orthogonal only near the fiducial point. The first is what this record derives in closed form, the second what it can compute where closed forms stop.

## Limits

- The paper's setting is high-dimensional nuisances estimated by machine learning with cross-fitting. Only the finite-dimensional likelihood construction is used here.
