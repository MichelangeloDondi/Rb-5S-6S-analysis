---
citekey: benussi2026
type: misc
authors:
  - Benussi, Davide
  - Kosmidis, Ioannis
  - Salvan, Alessandra
  - Sartori, Nicola
title: 'Focused median bias reduction'
journal: arXiv preprint
year: 2026
doi: null
arxiv: '2606.28597'
pdf: PDF_papers/Benussi_2026_focused-median-bias-reduction.pdf
held: true
status: REPORTED
routing:
  - CITE
  - FEED
verify_flags:
  - Pages 1 and 2 read against the PDF on 2026-09-20, of 35 in total. The construction itself
    (the Cornish-Fisher solution, the third-order result and the hull-based intervals) is in
    sections not yet read, so no formula is attributed to it here.
  - 'Adversarial re-audit, 2026-09-20: the Values table had conflated two different dates on
    p. 1 into one field. The arXiv v1 timestamp printed on the page (checked with two
    independent PDF-text extractors, pypdf and pdftotext -layout) reads 26 Jun 2026, not
    30 June 2026, and that second date is the paper's own separate dateline typeset beneath
    the author list, a field the arXiv system does not set. Split into two rows. Every quoted
    passage in the What-it-says section below was re-checked against the PDF and is unchanged.'
verified_date: null
summary: >
  A maximum-likelihood estimate of a scalar focus parameter, a smooth transformation of a joint
  fit that also carries nuisances, has a finite-sample median bias, and this gives an explicit
  third-order median-unbiased correction for it that needs only the fit itself, the transformation's
  gradient and Hessian, and expectations of products of log-likelihood derivatives. That is the
  shape of every waist this record quotes, and the correction it replaces is the Monte Carlo one
  this record actually runs. It also reports near-nominal finite-sample interval coverage under
  median bias control, which is the reading the closure ladder judges its rungs on.
loci:
  - methods/06
section: method-anchors
---
# benussi2026

## Values

| field | value | where in the paper |
|---|---|---|
| arXiv identifier | 2606.28597v1, arXiv's own timestamp reading 26 Jun 2026 | p. 1 |
| paper's own dateline (separate from the arXiv timestamp, beneath the author list) | June 30, 2026 | p. 1 |
| affiliations | Padova (Statistical Sciences) and Warwick (Statistics) | p. 1 |
| order of median unbiasedness achieved | third | p. 1, abstract |
| what the estimator needs | the ML estimate at a reference parameterisation, the gradient and Hessian of the transformation, and expectations of products of log-likelihood derivatives | p. 1, abstract |

## What it says, in its own terms

**The problem is stated for a focus parameter.** Existing generally applicable median-bias-reduction
methods are "typically implicit, requiring the solution of nonlinear systems of estimating equations,
which is computationally demanding", require "a fully specified nuisance parameterization", and applying
them to a transformation of the parameters "involves tedious algebra and bespoke implementations"
(p. 1). The paper's estimator is explicit instead, obtained by solving to the required order an equation
built on the Cornish-Fisher expansion of the centred and scaled maximum-likelihood estimator of the
focus parameter.

**Why it exists.** When the information about the model parameters is "small or moderate (e.g. small to
moderate sample sizes and/or high-dimensional parameter specifications), the finite sample properties of
the maximum likelihood estimator can deviate considerably from its expected asymptotic properties", and
"any poor performance of the maximum likelihood estimator at a reference parameterization is likely to be
inherited when relying on that estimator for estimating or drawing inferences about a focus parameter"
(p. 2).

**What it replaces.** It places itself against "computationally intensive mean bias reduction techniques
such as the jackknife (Quenouille, 1956) or parametric and nonparametric bootstrap" (p. 2), and cites
Cox and Snell (1968) and Firth (1993) as the expansions the mean-bias literature rests on.

**The interval claim.** The method "improves standard asymptotic inference and integrates naturally with
hull-based confidence procedures, yielding intervals with near nominal finite-sample coverage under
median bias control" (p. 1).

## Why it is routed FEED, and the one thing it is not

Every waist this record quotes is a scalar focus parameter of a joint fit carrying nuisances, its bias is
estimated by Monte Carlo over injected realisations, and its rungs are judged on interval coverage. Those
are the three objects of the abstract. Two consequences are worth testing against the code rather than
asserted here: whether the explicit correction reproduces the twin's measured bias at the noisy rungs at a
fraction of the cost, and whether median bias control is the better target for a rung whose verdict is a
coverage.

**It does not explain a bias that survives at zero noise.** A finite-sample median bias vanishes as the
information accumulates, so it cannot produce an offset that this record measures at the noiseless rung,
where the estimator sees the model's own output with no noise in it. The structural waist offset stays a
question about the model and its kernel. This paper bears on the noisy rungs and on the intervals.
