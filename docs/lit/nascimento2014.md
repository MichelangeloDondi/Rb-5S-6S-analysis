---
citekey: nascimento2014
type: article
authors:
  - Nascimento, Abraão D. C.
  - Frery, Alejandro C.
  - Cintra, Renato J.
title: 'Bias Correction and Modified Profile Likelihood under the Wishart Complex Distribution'
journal: IEEE Transactions on Geoscience and Remote Sensing
year: 2014
doi: 10.1109/TGRS.2013.2285927
arxiv: '1404.4880'
pdf: PDF_papers/Nascimento_2014_bias-correction-modified-profile-likelihood-Wishart.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Held since 2026-09-20 (the owner downloaded it). Only page 1, the abstract, has been
    read against the PDF. The Cox-Snell and Barndorff-Nielsen expressions it carries are in
    sections not yet read, so nothing below attributes an equation to it.
  - Misjudged on first recommendation. A search summary presented this as a general treatment
    of maximum-likelihood bias in terms of cumulants of log-likelihood derivatives, and it was
    recommended to the owner as the first paper to obtain on that basis. The abstract shows it
    is a polarimetric-radar paper applying two known corrections to one parameter of one
    distribution. Its general content is the two corrections it cites, not a general theory.
verified_date: null
summary: >
  Applies the Cox-Snell second-order bias expression and Barndorff-Nielsen's modified profile
  likelihood to the equivalent number of looks of a scaled complex Wishart distribution, for
  polarimetric synthetic aperture radar. Its value to this record is as a pointer to those two
  corrections and to a worked case where a profile likelihood's maximum-likelihood estimator
  carries a second-order bias that is corrected analytically rather than numerically.
loci:
  - methods/06
section: method-anchors
---
# nascimento2014

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | IEEE Trans. Geosci. Remote Sens. **52**(8), 4932–4941 (2014) | arXiv listing |
| DOI | 10.1109/TGRS.2013.2285927 | arXiv listing |
| distribution treated | scaled complex Wishart | p. 1, abstract |
| parameter treated | the equivalent number of looks $L$ | p. 1, abstract |
| what the speckle is | coherent-illumination granular noise in PolSAR images | p. 1, abstract |

## What the abstract states

The paper proposes improved methods for the maximum-likelihood estimation of $L$.
The second-order bias expression of Cox and Snell is presented for the maximum-likelihood
estimator of $L$, and the profile likelihood modified by Barndorff-Nielsen is discussed in
terms of $L$. Two new estimators follow, assessed by Monte Carlo and on real polarimetric
radar data.

## What it does not contain

No general statement of maximum-likelihood bias in terms of cumulants of the log-likelihood
derivatives appears on the page read. The setting is one distribution and one parameter.
**The general treatment this record wanted is `benussi2026`**, which the owner downloaded in the
same batch and which states the focus-parameter case explicitly.

## The two corrections it points at

Cox and Snell's second-order bias expression and Barndorff-Nielsen's modified profile
likelihood are the general results. Their primary sources, not this application of them, are
what a treatment of a profile-likelihood bias in this record would cite.
