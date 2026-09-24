---
citekey: transtrum2011
type: article
authors:
  - Transtrum, Mark K.
  - Machta, Benjamin B.
  - Sethna, James P.
title: 'Geometry of nonlinear least squares with applications to sloppy models and optimization'
journal: Phys. Rev. E
volume: 83
number: 3
pages: 036701
year: 2011
doi: 10.1103/PhysRevE.83.036701
arxiv: '1010.1449'
pdf: PDF_papers/Transtrum_2011_geometry-nonlinear-least-squares-sloppy-models.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/transtrum2011.md  # line-by-line against the held PDF, 2026-09-22, upgraded to VERIFIED: one correction (a "Fisher matrix" gloss on "the metric" that the read passages never use) plus one summary-line rescoping (parameter evaporation is a naive-algorithm failure mode in the read pages, not a stated "before the stiff combinations are fitted" sequencing)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1010.1449v1 (7 Oct 2010), 41 pages. Read on 2026-09-22: the
    abstract, Section I, the opening of Section II, the parameter-evaporation passage of
    Section III and the opening of Section V (priors). Sections IV, VI and VII (model
    graph, geodesic coordinates, curvature measures) and the algorithms were not read.
    REPORTED because most of the paper is unread; the statements below are limited to
    the passages named. Journal reference and DOI confirmed against Crossref on
    2026-09-22.'
verified_date: 2026-09-22
summary: >
  The geometric account of sloppy fits: a multi-parameter model's predictions form a
  manifold in data space shaped like a hyper-ribbon, with a geometric hierarchy of
  widths, so the metric has a hierarchy of eigenvalues. Naive fits can run to the
  manifold's boundaries, where parameters "evaporate" to extreme, unphysical values,
  a failure of blindly following the local fit direction, not of the stiff
  combinations themselves. Priors entered as extra residuals,
  (theta - theta0)/sigma, remove the boundaries. The best-fit values along sloppy
  directions should not be read as physical values.
loci:
  - methods/06
section: method-anchors
---

# transtrum2011

VERIFIED for the abstract, Section I, the opening of Section II, the parameter-evaporation passage
of Section III and the opening of Section V (priors). Sections IV, VI and VII (the model graph,
geodesic coordinates, curvature measures) and the algorithms are named only by topic, cited to what
they cover, not reproduced, and were not read here.

## What the read passages say

- Least squares as geometry: the parameters map to a manifold of predictions, and the fit is the nearest point to the data (abstract, Section I). For sloppy models the manifold has a geometric series of widths and curvatures, a hyper-ribbon (Section I).
- Successive parameter directions have a hierarchy of vanishing effect on the model, so the metric has a hierarchy of eigenvalues. Only a few stiff combinations need tuning, and the fit is a kind of multidimensional interpolation. The best-fit parameters need not represent physical values, while predictions from an ensemble of good fits can still be falsifiable (Section III).
- Parameter evaporation, the drift of parameters to extreme values, is a direct consequence of the manifold's boundaries, where the metric becomes singular because the basis vectors dr/dtheta become linearly dependent (Eq. 16). Following the Gauss-Newton direction blindly can point at a boundary (Section III).
- Pragmatic priors, added as residuals (theta - theta0)/sigma (Eq. 18), use the data's own scales to keep a fit off the boundaries, and should be relaxed late in the fit (Section V).

## Use in this record

- The general picture behind two of this record's own rules: a fit that runs to the edge of a scan grid (the waist before the log-determinant was restored), and the rule that a boxed nuisance is a wall while a calibrated nuisance is a prior with a width. Here the wall is a manifold boundary, and the remedy is the prior residual.
- The warning that fitted values along sloppy directions are not measurements supports reporting identifiable combinations. That is what the power-free and waist-free combinations do by construction.

## Not yet read

The model graph (Section IV), geodesic coordinates (Section VI), the curvature analysis (Section VII) and the geodesic-acceleration algorithm.
