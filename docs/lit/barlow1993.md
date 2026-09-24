---
citekey: barlow1993
type: article
authors:
  - Barlow, R.
  - Beeston, C.
title: 'Fitting using finite Monte Carlo samples'
journal: Comput. Phys. Commun.
volume: 77
number: 2
pages: 219-228
year: 1993
doi: 10.1016/0010-4655(93)90005-W
arxiv: null
pdf: PDF_papers/Barlow_1993_fitting-finite-Monte-Carlo-samples.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/barlow1993.md  # line-by-line against the held PDF via page images (OCR is column-interleaved), 2026-09-22: one correction, the 0.39 bias figure re-scoped from both chi-squared methods to the plain likelihood alone
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (Elsevier), downloaded by the owner by hand. Read in full on 2026-09-22, Sections 1 to 9. The text layer is a two-column scan whose columns interleave, so equations are cited by number and nothing is quoted. Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The standard treatment, in particle physics, of a binned fit whose templates come
  from finite Monte Carlo samples. The data are fitted as a mixture of simulated
  sources. The likelihood carries the data's Poisson terms and also a Poisson term for
  each source's Monte Carlo count in each bin, whose true expectation becomes a
  nuisance parameter. The m x (n + 1) unknowns reduce to one equation per bin, solved by
  Newton's method, with special handling for bins where a source has no Monte Carlo
  entries. In a two-source example with about ten entries per bin, every method but
  the new likelihood is biased; the plain binned likelihood's own mean sits at 0.39
  against a true 0.333. The authors add that subtracting the bias instead would need a
  simulation large enough to be better spent inside the fit.
loci:
  - P1
  - methods/06
section: method-anchors
---

# barlow1993

VERIFIED. Held (published version, scanned text). Read in full on 2026-09-22.

## What it does

The problem is to estimate the proportions p_j of several sources in a binned data sample when each source's distribution exists only as a Monte Carlo sample. With many sparse bins the chi-squared is wrong, so the binned Poisson likelihood of Eq. (6) is used. It accounts for small data counts but not for fluctuations in the Monte Carlo counts a_ji. The paper notes that the rule of thumb of ten times more simulated than real events is often unaffordable. Section 2 writes the correct likelihood (Eq. 9) with the unknown expectations A_ji of the Monte Carlo counts as parameters and f_i = sum p_j A_ji as the prediction (Eq. 8). The binomial count is taken as Poisson.

Section 3 reduces the m x (n + 1) coupled equations. With t_i = 1 - d_i/f_i (Eq. 13), every A_ji = a_ji/(1 + p_j t_i) (Eq. 14), so each bin needs one equation in one unknown t_i (Eq. 15). It has a unique solution in the allowed region and Newton's method finds it, often in one step. The normalisation then emerges on its own (Eq. 18). Section 5 treats bins where a source has no Monte Carlo entries: only the strongest such source can take a non-zero expectation (Eq. 22, Figs. 1-3). Section 6 adds event weights, with the warning that a wide spread of weights inflates the error. Section 7 gives the error from the variation of the log-likelihood, not from the inverse Hessian over all the nuisances.

## The example and its reading

The example of Section 8 fits two two-dimensional sources in the ratio 1:2, 1000 data events per fit and 500 fits per case, by four methods: the simple chi-squared, the chi-squared with the Monte Carlo error added, the simple binned likelihood and the new likelihood. With 10 000 Monte Carlo events per source in 25 bins all four agree (Fig. 4). With 1000 in 25 bins the simple methods are measurably biased (Fig. 5). With 1000 in 100 bins, about ten per bin, every method but the new one is biased (Fig. 6). The simple likelihood's distribution there is narrower than the new one's, but about a mean of 0.39, not the true 0.333. The authors consider subtracting that +0.06 bias and reject it: the bias can only be found by simulation, and a simulation large enough to measure it would be better used in the fit.

## Use in this record

- The classic statement of the problem arguelles2019 revisits: when a likelihood's prediction comes from a finite simulation, the simulation's own noise belongs in the likelihood. It applies wherever the record's forward model reads a Monte Carlo instead of a quadrature: the kernel Monte Carlo's nodes and the moment covariance estimated from twin replicas (hartlap2007, sellentin2016).
- It is the published objection the record's bias subtraction has to answer. The main aim uses the twin to compute biases and factor them out, and Barlow and Beeston argue against subtracting a simulated bias. The answer is that they treat a different bias. Theirs comes from noise in the templates and vanishes as the simulation grows. The twin's is the estimator's own finite-sample bias at the data's noise level, which remains with a noiseless model and is the object of parametric bias correction (MacKinnon and Smith 1998, not yet held) and of indirect inference (gourieroux1993). The thesis should state which of the two each twin bias is.
- Fig. 6 is a published case of a precise fit that is not accurate: the narrower distribution sits about the wrong mean, and only the injected truth shows it. That is the record's closure argument, made in 1993.

## Limits

- Binned counting data with a mixture of templates, the proportions as the only parameters of interest, and no systematic uncertainty on the templates' shapes. It says nothing about moments, covariance estimation or continuous-valued traces.
