---
citekey: humphrey2009
type: article
authors:
  - Humphrey, P. J.
  - Liu, W.
  - Buote, D. A.
title: 'χ2 and Poissonian data: biases even in the high-count regime and how to avoid them'
journal: Astrophys. J.
volume: 693
number: 1
pages: 822-829
year: 2009
doi: 10.1088/0004-637X/693/1/822
arxiv: '0811.2796'
pdf: PDF_papers/Humphrey_2009_chi-square-Poisson-bias-data-weighted-high-count.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:0811.2796v1 preprint (17 Nov 2008), marked accepted for ApJ; pages and DOI
    are Crossref''s record of the published article, checked 2026-09-22. Read in full on 2026-09-22,
    Appendices A and B included, which carry the order-of-magnitude derivations quoted below.'
verified_date: 2026-09-22
summary: >
  Fitting counts by chi-square with the data or the model as the weights biases the parameters even
  at high counts, by a fraction of the statistical error of order the number of bins over the root of
  the total counts; the Poisson likelihood (Cash's C) is unbiased to order one over that root. The
  derivation holds for Gaussian data whose variance equals their mean. The published statement of
  why an objective whose weights depend on its own parameters needs its normalisation term, which is
  this record's rule on the log-determinant.
loci:
  - methods/06
section: method-anchors
---

# humphrey2009

VERIFIED against the held preprint (scope in `verify_flags`).

## The problem

Two chi-square approximations are in common use for binned counts: the data-weighted form, with the observed counts in the denominator (Neyman's), and the model-weighted form, with the model there (Pearson's), their Eqs. 2 and 3. The Poisson likelihood, in the form of Cash's C, is their Eq. 1. The paper's figure of merit is the bias divided by the statistical error, f_b, not the fractional bias, and it is measured by Monte Carlo on two cases: a constant count rate from a light curve, and the temperature of a thermal plasma from a Chandra spectrum.

## What it finds

The mechanism, verbatim: "the dependence of the denominator in Eqn 3 on p naturally leads to a bias." And its cause, verbatim: "As pointed out by Wheaton et al. (1995), the bias arises not from deviations from Gaussianity but because of the misparameterization of the problem when these approximations are used with an arbitrary model."

The sizes, from Appendix A, to order of magnitude for a single parameter: data weighting gives f_b of order minus N over root N_c, and model weighting plus half that, with N the number of bins and N_c the total counts. The data-weighted bias is minus twice the model-weighted one. Appendix B gives the C-statistic an f_b of order one over root N_c, which vanishes as the counts grow. On the light curve the C-statistic's bias is exactly zero. On the spectra the chi-square fits reach |f_b| of 0.5 to 1 while the C-statistic stays practically unbiased (Figs. 1 and 2). For the multi-parameter case the authors expect a bias of the same order on the parameters or on some combination of them.

On whom the derivation binds, verbatim from Appendix A: "which are true for both Poisson and Gaussian distributions": the moments used, provided the Gaussian's variance in each bin equals its mean.

The conclusion, verbatim: "Conversely, we find that fits using Cash’s C-statistic give comparatively unbiased parameter estimates when the counts are high."

## Use in this record

The analysis side's rule reads that an objective whose weights depend on its own parameters is not a likelihood until its log-determinant is carried, and it was measured on the waist: without the term the estimator returned a waist well away from the one injected, with a bar that tracked the noise. This paper is the published form of that result for the variance-equals-mean case: weighting a sum of squared residuals by the fitted level, without the normalisation that the Poisson or Gaussian likelihood carries, biases the parameter by an amount that grows with the number of samples at fixed total signal, so a long trace makes it worse, not better. The 2025 noise law has a shot term that follows the signal and a floor, so its variance is not the mean and the paper's coefficients do not transfer. The mechanism and the scaling with the number of samples do.

Related, from the reviewer's intake of 2026-09-21: `alsing2018`, whose treatment of a parameter-dependent covariance the reviewer points to for the same term in the score.
