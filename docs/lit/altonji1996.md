---
citekey: altonji1996
type: article
authors:
  - Altonji, Joseph G.
  - Segal, Lewis M.
title: 'Small-sample bias in GMM estimation of covariance structures'
journal: J. Bus. Econ. Stat.
volume: 14
number: 3
pages: 353-366
year: 1996
doi: 10.1080/07350015.1996.10524661
arxiv: null
pdf: PDF_papers/Altonji_1996_small-sample-bias-GMM-covariance-structures.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/altonji1996.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, every checked claim confirmed within the disclosed abstract/introduction/Section-VIII scope
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the Federal Reserve Bank of Chicago working paper WP-94-8 (May
    1994, digitized by FRASER), the precursor of the JBES article. The published version
    is not held and was not compared. Read on 2026-09-22: abstract, introduction and the
    conclusion (Section VIII). The Monte Carlo designs and tables were not read.'
verified_date: 2026-09-22
summary: >
  Optimally weighted minimum distance (GMM on second moments, with the inverse of an
  estimated covariance of the moments as weight) is seriously biased in small samples,
  and in large ones for heavy-tailed data. The bias is almost always toward zero and
  comes from the correlation between the sampling errors of the moments and of the
  weighting matrix built from the same data. Equal weighting usually has smaller RMS
  error. Estimating the weights from a separate split removes the bias but adds noise.
  The bias does not go away, and may grow, as more moments are added.
loci:
  - methods/06
section: method-anchors
---

# altonji1996

VERIFIED for the sections named in the flags. Held (1994 working-paper version). Read on 2026-09-22.

## What it says

The abstract and conclusion state the finding. The optimal minimum-distance estimator is biased in small samples for many distributions, more so for heavy-tailed data, and the bias is almost always downward in absolute value. The cause is that sampling errors in the second moments are correlated with sampling errors in the weighting matrix estimated from the same observations. The equally weighted estimator usually has lower RMS and median absolute error, even where the optimal one is far more efficient asymptotically. A split-sample version, weights from one half and moments from the other, is unbiased and asymptotically equivalent, but usually loses to equal weighting because of the noise in the estimated weights. The problem does not go away, and may get worse, as the number of moments grows at fixed sample size. The authors recommend fitting both ways and treating a large difference as a warning of bias.

## Use in this record

- A direct risk for the moment likelihood if its covariance is estimated from the same traces whose moments it weights. Heavy tails, which windowed high-order moments of Lorentzian lines have, make it worse. This record weights with twin replicas, which is the split-sample remedy in spirit, since the weights are independent of the data. The paper's point about extra noise from estimated weights is then the Hartlap and Sellentin question of how many replicas are enough.
- Its recommended check, estimating both optimally weighted and equally weighted and comparing, is cheap on the twin and belongs in the closure protocol for the high orders.
- The warning that adding moments at fixed sample size can worsen the bias is the statistics side of the caution against accumulating coordinates.

## Limits

- Econometric covariance-structure models, linear in the parameters in the Monte Carlo studies. The authors themselves flag nonlinear models as open.
