---
citekey: kosmidis2014
type: article
authors:
  - Kosmidis, I.
title: 'Bias in parametric estimation: reduction and useful side-effects'
journal: WIREs Comput. Stat.
volume: 6
number: 3
pages: 185-196
year: 2014
doi: 10.1002/wics.1296
arxiv: '1311.6311'
pdf: PDF_papers/Kosmidis_2014_bias-parametric-estimation-reduction-side-effects-review.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1311.6311v1 preprint (25 Nov 2013); journal, volume, pages and DOI are
    Crossref''s record of the published review, checked 2026-09-22. Read in full on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  A review that puts every bias-reduction method under one equation, the estimate minus the bias at
  the true value: explicit methods (jackknife, parametric bootstrap, the Cox-Snell correction)
  evaluate the bias at the estimate and subtract it once; implicit ones (indirect inference, Firth's
  adjusted score) evaluate it at the corrected value and solve. The map for choosing how the twin's
  bias is removed, with two warnings that bind the moment programme: bias depends on the
  parameterisation, and removing it can inflate the mean squared error.
loci:
  - methods/06
section: method-anchors
---

# kosmidis2014

VERIFIED against the held preprint (scope in `verify_flags`).

## The frame

The review's organising equation is the estimate minus the corrected estimate equal to the bias function at the true value (their Eq. 3). In the author's words, verbatim: "The importance of equation (3) is that, despite of its limited practical value, all known methods to reduce bias can be usefully thought of as attempts to approximate its solution."

Explicit methods estimate the bias once and subtract it (Section 4): the jackknife, by linear extrapolation in 1/n of leave-one-out estimates. The bootstrap's parametric form simulates from the fitted model and removes the mean shift, giving order 1/n^2 bias. The asymptotic correction subtracts the Cox-Snell first-order bias evaluated at the estimate. Implicit methods evaluate the bias at the target estimator and solve (Section 5): indirect inference, which approximates the bias at the corrected value by parametric bootstrap, and Firth's adjusted score equations, which share the maximum-likelihood estimator's asymptotic normal distribution, so Wald intervals and score tests keep their form. On explicit methods the review says, verbatim: "Nevertheless because of their explicit dependence on θ̂, explicit methods directly inherit any of the instabilities of the original estimator."

## The warnings

On parameterisation, verbatim: "Hence, correction of the bias of the maximum likelihood estimator comes at the cost of destroying its invariance properties under reparameterization." And in the conclusion, verbatim: "At this point, we should also stress that improving bias does not always have desirable effects; an improvement in bias can sometimes result in inflation of the mean squared error, through an inflation in the estimator’s variance." The recommended check is a simple simulation study, and where the inflation occurs the reduced-bias estimates are not recommended for test statistics or intervals.

## The case studies

A precision parameter of a beta regression is biased strongly upward while the regression coefficients are not, and the bias of that one nuisance parameter makes every Wald interval under-cover, near 80 per cent at a nominal 90 (Tables 1 and 2). Corrected, the standard errors inflate and the coverage returns. In an ordinal model, maximum-likelihood estimates that run to infinity under separation come back finite under the adjusted score (Table 4).

## Use in this record

This is the vocabulary for the twin's bias step. Correcting the joint fit by the twin's mean shift at the fitted parameters is the parametric-bootstrap explicit method. Running the twin at the corrected parameters until the fitted value is reproduced is indirect inference, whose source paper the shelf holds as a PDF with no note yet (`Gourieroux_1993_indirect-inference.pdf`). The case study of a biased nuisance parameter that spoils the coverage of the parameters of interest is the analysis side's own experience with a boxed nuisance, and the parameterisation warning is why the owner's S0-free and w0-free coordinates are a choice to be made before a bias is removed, not after. The review covers regular models. The twin's other purpose, a misspecified model, is outside it.

Related on this shelf: `kosmidis2010` (the iterated first-order correction), `benussi2026` (median bias reduction), and the Gourieroux 1993 PDF (indirect inference, not yet noted).
