---
citekey: kosmidis2010
type: article
authors:
  - Kosmidis, I.
  - Firth, D.
title: 'A generic algorithm for reducing bias in parametric estimation'
journal: Electron. J. Stat.
volume: 4
pages: 1097-1112
year: 2010
doi: 10.1214/10-EJS579
arxiv: null
pdf: PDF_papers/Kosmidis_2010_generic-algorithm-bias-reduction-parametric-estimation.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the published article as deposited in the University of Warwick repository (WRAP,
    eprint 4341), with a repository cover page; volume and pages read from the article itself, DOI
    confirmed in Crossref on 2026-09-22. Read in full on 2026-09-22 except the numerical tables of
    Section 4, which are read for their conclusions only.'
verified_date: 2026-09-22
summary: >
  The maximum-likelihood estimator's first-order bias removed by iterating a correction: each step
  takes the next likelihood step and subtracts the bias evaluated at the current corrected value,
  which converges to Firth's bias-reduced estimator; with a simulation design that checks a bias
  formula by replicating the design and watching n times the bias settle. The form the main aim's
  twin-based bias correction takes when the bias depends on the parameter it corrects.
loci:
  - methods/06
section: method-anchors
---

# kosmidis2010

VERIFIED against the held article (scope in `verify_flags`).

## The method

The maximum-likelihood estimator of a regular model has bias of order 1/n. Subtracting the first-order bias evaluated at the estimate gives the bias-corrected estimator, with bias of order 1/n^2. Firth's alternative solves an adjusted score equation, the score plus an order-one adjustment set to zero, and reaches the same order without starting from the maximum-likelihood estimate (Sections 1 and 2). The paper's contribution is a quasi-Newton iteration for the adjusted score that needs only the first-order bias b(beta) of the maximum-likelihood estimator, already derived for many models (Section 3). For the observed-information adjustment it reduces to a simple form (their Eq. 3.4), and the authors read it, verbatim: "This has a rather appealing interpretation: at each step, the next candidate value of the maximum likelihood estimate is corrected by subtracting the O(n−1) bias evaluated at the current value of the bias-reduced estimate." Started from the maximum-likelihood estimate, its first step is the bias-corrected estimate. Iterated to convergence it is the bias-reduced one.

## Checking a bias formula by simulation

The worked example, beta regression on Prater's gasoline data, disagrees with published bias-corrected values, and the authors decide which implementation is wrong with a design built for the purpose: replicate each row of the model matrix j times, so the bias of the estimator at sample size n_j is B(beta)/n_j plus higher order, and plot n_j times the simulated bias against n_j with the number of simulated samples grown in proportion to keep the simulation error fixed (Fig. 1). Their estimates settle on their own B(beta) and not on the published one. They also find a sign error in the literature that, verbatim, "approximately doubles the bias of the maximum likelihood estimator instead of eliminating it".

## Two cautions they draw

On what bias costs besides the centre, verbatim: "Because of the large bias in the estimated precision parameter φ̂, the usual standard errors based on the maximum likelihood analysis are systematically too small." And on which coordinate to correct, verbatim: "In general, bias reduction will typically make most sense when applied to estimators whose distribution is approximately symmetric, since it will then most often improve the accuracy of inferences made when using first-order asymptotic normal approximations." Their example moves the correction to the logarithm of the precision parameter for that reason (Remark 3).

## Use in this record

The owner's main aim is to use the twin to compute and factor out biases before the joint likelihood is read. When the twin's bias depends on the true value, as it does for any parameter near a boundary or a window edge, a single subtraction at the fitted value is the first step of this paper's iteration and not its end. Evaluating the bias at the corrected value and repeating is the published procedure, with its convergence argument. The replicated-design check is the twin experiment in statistical form: a bias claimed for a parameter is confirmed by the product of sample size and simulated bias settling on it. The parameterisation remark bears on the moment programme, where the coordinates are chosen per window by their twin bias: a coordinate whose sampling distribution is skewed, as a ratio of moments with a noisy denominator is, is the wrong place to subtract a mean bias. The paper treats first-order bias in regular models. Nothing in it covers a misspecified model, which is the twin's other job.

Related on this shelf: `kosmidis2014` (the same author's review of bias reduction and its side effects), `benussi2026` (median bias reduction).
