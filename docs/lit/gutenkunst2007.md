---
citekey: gutenkunst2007
type: article
authors:
  - Gutenkunst, Ryan N.
  - Waterfall, Joshua J.
  - Casey, Fergal P.
  - Brown, Kevin S.
  - Myers, Christopher R.
  - Sethna, James P.
title: 'Universally sloppy parameter sensitivities in systems biology models'
journal: PLoS Comput. Biol.
volume: 3
number: 10
pages: e189
year: 2007
doi: 10.1371/journal.pcbi.0030189
arxiv: 'q-bio/0701039'
pdf: PDF_papers/Gutenkunst_2007_universally-sloppy-parameter-sensitivities.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/gutenkunst2007.md  # line-by-line against the held PDF, 2026-09-22, upgraded to VERIFIED: two corrections (a Hessian-in-log-parameters construction, Eq. 2, presented as read when only Eq. 1 was) plus one summary-line rescoping (a PC12-specific "predictions before parameters" sequencing generalized to all 17 models, which the read pages do not do)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:q-bio/0701039v3 (27 Jul 2007). Read on 2026-09-22: abstract,
    non-technical summary, introduction and the opening of Results (the chi-squared
    sensitivity measure, Eq. 1). The eigenvalue spectra of the seventeen models and the
    tests on parameter measurements (the rest of Results and Methods) were not read.
    REPORTED for that reason.'
verified_date: 2026-09-22
summary: >
  Seventeen systems-biology models from the literature all show a "sloppy" spectrum:
  the eigenvalues of the chi-squared sensitivity measure are roughly evenly spaced
  over many decades. Collective fits can leave many individual parameters poorly
  constrained even with abundant, ideal data, a prediction tested across the
  collection. In the PC12 signalling model, 48 parameters fitted to 68 points each
  have a 95 per cent interval wider than a factor of 50, yet the predictions are
  tight. Direct parameter measurements must be very precise and complete to help.
  The paper argues for focusing on predictions, not parameters.
loci:
  - methods/06
section: method-anchors
---

# gutenkunst2007

VERIFIED for the abstract, the non-technical summary, the introduction and the opening of Results
through Eq. 1 (the chi-squared sensitivity measure). The Hessian-in-log-parameters construction
that produces the eigenvalue spectra (Eq. 2), the spectra themselves, the direct-measurement tests
and the Methods are cited only by what they cover, not reproduced, and were not read here.

## What the read passages say

- The sensitivity measure is a continuous chi-squared between time courses at the varied and at the published parameters, normalized per species (Eq. 1). The abstract and introduction describe the resulting sensitivity eigenvalues as roughly evenly spaced over many decades. The Hessian-in-log-parameters construction that produces them (Eq. 2) is past what was read here.
- The motivating case: 48 parameters fitted to 68 points, with every 95 per cent interval wider than a factor of 50, while the interventions predicted were tight enough to verify experimentally.
- The claim tested across the collection is that every one of the 17 models is sloppy, and that collective fits leave many parameters poorly constrained even with extensive ideal data.

## Use in this record

- A counterweight to reading every fitted number as a measurement. When the spectrum of this record's sensitivity matrix is spread over decades, the stiff combinations are the results and the sloppy ones are nuisance directions to be reported as such.
- Why the record's exponent table works where it does: when each model term is close to a monomial in the knobs, the sensitivities in log parameters are linear in the exponents, and the stiff and sloppy directions can be read from the exponent matrix before any fit. The paper reports computing the same spectrum numerically for its model collection (Results, beyond Eq. 1, not read here).

## Not yet read

The Hessian-in-log-parameters construction of the sensitivity measure (Eq. 2), the spectra of the seventeen models, the tests of direct parameter measurement, and the Methods.
