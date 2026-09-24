---
citekey: frazier2024
type: article
authors:
  - Frazier, David T.
  - Nott, David J.
  - Drovandi, Christopher
title: 'Synthetic likelihood in misspecified models'
journal: J. Am. Stat. Assoc.
volume: 120
number: 550
pages: 884-895
year: 2024
doi: 10.1080/01621459.2024.2370594
arxiv: '2104.03436'
pdf: PDF_papers/Frazier_2024_synthetic-likelihood-misspecified-models.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/frazier2024.md  # line-by-line against the held PDF, 2026-09-22: Eq. 4, the tempering and robust-adjustment (exponential-prior Gamma) claims all confirmed exactly, including the unusual "16 Apr 2026" watermark date itself; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:2104.03436v2 (16 Apr 2026), 85 pages. Read on 2026-09-22:
    abstract, Section 1, Section 2 (the definition of misspecification, Eq. 4, and its
    consequences), the tempering and robust-adjustment passages of Section 4, and the
    Discussion. The asymptotic theory of Section 3 and the appendices were not read and
    nothing below rests on them. Journal reference (JASA 120, 884-895) and DOI confirmed
    against Crossref on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  What happens to a Gaussian likelihood of simulated summary statistics (Bayesian
  synthetic likelihood) when no parameter value lets the model reproduce the observed
  summaries, i.e. "incompatibility" (Eq. 4). The posterior can concentrate on a
  boundary, go multimodal, flatten, or stay Gaussian around a wrong point, and this is
  intrinsic, not Monte Carlo noise. Likelihood tempering does not fix it. A robust
  variant that lets the summaries' variances inflate, with the adjustment parameters
  given priors, recovers reliable inference and flags which summary is incompatible.
loci:
  - methods/06
section: method-anchors
---

# frazier2024

VERIFIED for the sections named in the flags. Held (arXiv v2). Read on 2026-09-22.

## What it says

In synthetic likelihood the summaries are matched through a Gaussian with a simulated mean b(theta) and covariance. Misspecification means that no theta brings b(theta) to the observed summaries' limit: the whitened distance stays positive (Eq. 4), which the paper calls incompatibility after Marin et al. On a moving-average running example the posterior then shows Gaussian-like concentration, bimodality, concentration on the parameter boundary, or flat regions, depending on the degree of misspecification (Section 2.2). The paper stresses that these come from the synthetic likelihood's own asymptotics, not from Monte Carlo error or small samples (Section 1). Tempering the likelihood by a power does not cure them, because a Gaussian synthetic likelihood raised to a power only rescales its covariance (Section 4.1). The robust variant of Frazier and Drovandi (2021) adds variance-adjustment parameters Gamma with exponential priors, so that a summary the model cannot match can have its variance inflated. It gives Gaussian, correctly located posteriors across the misspecification levels tested, and the posterior on Gamma points at the incompatible summary (Section 4, Fig. 4). The Discussion notes that the type of misbehaviour cannot be measured without first doing some inference.

## Use in this record

- This record's moment likelihood is a synthetic likelihood: windowed moments whose mean and covariance come from the twin. Where the twin is incomplete (the closure failing at the archive's noise, the lock re-centring the twin does not reproduce), the model is misspecified in exactly this sense. Boundary concentration and multimodality are then expected behaviours, not bad luck, and fits running to grid edges should be read against this paper before being read as physics.
- Inflating all variances (tempering) is shown not to help. Per-summary variance adjustment is the robust route, and it is diagnostic as well: it names which summary the model cannot reproduce. That is the per-statistic version of this record's per-session admission test, and a way to learn which moment carries the missing term.

## Limits

- The theory is asymptotic and the demonstrations use a toy moving-average model. Performance on a many-summary spectroscopic problem is untested.
