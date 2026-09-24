---
citekey: hansen1982
type: article
authors:
  - Hansen, Lars Peter
title: 'Large Sample Properties of Generalized Method of Moments Estimators'
journal: Econometrica
volume: 50
number: 4
pages: 1029-1054
year: 1982
doi: 10.2307/1912775
arxiv: null
pdf: PDF_papers/Hansen_1982_large-sample-properties-GMM-estimators.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/hansen1982.md  # line-by-line against the held PDF, 2026-09-22: read as rendered images past the cover sheet through Theorem 3.2 (the efficiency result), the McFadden 1989 "not downloadable" claim corrected (stale), and the prior round's unhedged-vs-hedged fix stays in place
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'The held PDF is a bare page-image scan (a JSTOR reprint the author self-archived on his own site,
    larspeterhansen.org) with no embedded text layer: pdftotext extracts zero characters from every page
    tried (27 form-feed bytes, one per page, and nothing else, reconfirmed 2026-09-22). No word-for-word
    quotation is possible from this copy, so the one quotation below is drawn from `gourieroux1993`''s held
    PDF and is attributed there.'
  - 'Read as rendered page images (pdftoppm -r 150 -png), 2026-09-22: scan page 1 (the JSTOR cover sheet)
    and scan pages 2-6, 9, 13 and 15-21, which are article pp. 1029-1033 (title, abstract, the introduction,
    and Section 2''s setup through Assumption 2.4), p. 1036 (Theorem 2.2, consistency), p. 1040 (the start
    of Section 3, Lemma 3.1, Assumptions 3.5-3.6), and pp. 1042-1048 (Theorem 3.1, the asymptotic normality
    result for a general limiting weighting matrix, the five worked cases for computing S_w, and Theorem 3.2
    with Eq. 11, the efficient-weighting-matrix result). Scan pages 7-8, 10-12 and 14 (intervening
    consistency-proof and special-case material) and scan pages 22-27 (Section 4 on overidentifying-
    restriction tests, Section 5''s concluding remarks, and the two technical appendices'' proofs of
    Theorems 2.2, 3.1 and 3.2) were not read: no claim below draws on them.'
verified_date: 2026-09-22
summary: >
  Defines the generalized method of moments (GMM) estimator -- choose parameters to make sample averages of
  theoretical moment (orthogonality) conditions as close to zero as possible under a chosen weighting matrix
  (Section 2) -- derives its asymptotic distribution for a general limiting weighting matrix (Theorem 3.1,
  p. 1042), and shows the efficient weighting matrix is the inverse of the moment conditions' own asymptotic
  covariance matrix (Theorem 3.2 and Eq. 11, p. 1048). Task-specified item 7 (paired with `mcfadden1989`,
  held and VERIFIED). A general framework this record's own twin-calibrated, covariance-weighted joint fit
  structurally resembles -- moment conditions as windowed-moment residuals, weighting as inverse covariance
  -- though whether it inherits GMM's efficiency property still needs checking against Theorem 3.2's own
  conditions (moment-condition asymptotic normality, a nonsingular S_w, and a consistent estimator of it).
  See "Use in this record" below.
loci:
  - methods/06
section: method-anchors
---

# hansen1982

VERIFIED for the JSTOR cover sheet and scan pages 2-6, 9, 13 and 15-21 (article pp. 1029-1033, 1036, 1040
and 1042-1048), read as rendered images since this copy carries no text layer. Section 4, Section 5 and the
two appendices' proofs (scan pp. 22-27) were not read. See "Not yet read" below.

## Values

| field | value | where in the paper |
|---|---|---|
| title | Large Sample Properties of Generalized Method of Moments Estimators | p. 1 (JSTOR cover sheet, read as a rendered image. Not quoted, since this scan carries no text layer at all: see below) |
| author | Lars Peter Hansen | p. 1 |
| journal reference | Econometrica, Vol. 50, Issue 4 (Jul., 1982), pp. 1029-1054 | p. 1 |
| copyright | (c) 1982 The Econometric Society | p. 1 |
| held-PDF page count | 27 | matches the 26-page article range plus a JSTOR cover sheet |
| Theorem 3.1 | asymptotic normality of the GMM estimator for a general limiting weighting matrix a*_0: sqrt(N)(b*_N - beta_0) is asymptotically normal, mean zero, covariance (a*_0 d_0)^-1 a*_0 S_w a*_0' (a*_0 d_0)^-1' | article p. 1042, read as a rendered image |
| Theorem 3.2, Eq. (11) | the optimal (efficient) limiting weighting matrix is a*_0 = e d_0' S_w^-1 for a nonsingular e, with resulting asymptotic covariance (d_0' S_w^-1 d_0)^-1 | article p. 1048, read as a rendered image |

## What it is

GMM estimation chooses a parameter vector to set sample averages of a vector of theoretical orthogonality or
moment conditions, functions of the data and the parameters that should average to zero at the true
parameter value, as close to zero as a chosen quadratic form allows, when there are more moment conditions
than parameters and an exact solution is not generally available (Section 2, article pp. 1032-1033: the
stationary ergodic process x_n, the orthogonality function f, the weighting matrices a_N, and the estimator
as the minimizer of the quadratic form in a_N g_N(beta)). Theorem 2.2 (p. 1036) gives consistency. Theorem
3.1 (p. 1042) gives the estimator's asymptotic normality for an arbitrary limiting weighting matrix a*_0,
with a covariance depending on a*_0, on d_0 (the limit of the sample moment average's own derivative) and on
S_w, the moment conditions' own asymptotic covariance, the sum over all lags of their autocovariances.
Theorem 3.2 and Eq. (11) (p. 1048) then show the covariance is minimized, among weighting matrices meeting
Eq. (10), by a*_0 proportional to d_0' S_w^-1, built from the inverse of the moment conditions' own
asymptotic covariance matrix, with the resulting optimal covariance (d_0' S_w^-1 d_0)^-1. This is the general
theorem that the simulated method of moments (`mcfadden1989`, task item 7's other half, held and VERIFIED as
of 2026-09-22), and indirect inference (`gourieroux1993`, `smith1993`) are later shown, in their own papers,
to be special or extended cases of: `gourieroux1993`'s own introduction (read directly, see that note)
states that indirect inference "contains, as a special case, the simulated method of moments (SMM)
(McFadden...)".

## Use in this record

This record's own plan, one Gaussian likelihood across many experimental conditions, built from windowed
moments whose covariance is twin-estimated, is, in this paper's vocabulary, close to a GMM problem where the
"moment conditions" are the windowed-moment residuals (model prediction minus twin-debiased data) and the
efficient weighting matrix is exactly the (Hartlap-corrected or Ledoit-Wolf-shrunk) inverse covariance this
record already plans to build, matching Theorem 3.2's own a*_0 proportional to S_w^-1. What Theorem 3.2 does
not by itself settle is whether the planned joint fit meets its conditions: S_w nonsingular, the moment
conditions asymptotically normal (Assumption 3.5, p. 1040), and a consistent estimator of S_w and of d_0
(Lemmas 3.2-3.3, cited here by name only, their own proofs unread). The last of those three is the one
already flagged elsewhere in this record: a covariance that is itself only known up to the finite-replica
noise `dodelson2013` and `taylor2013` quantify is not yet the consistent S_w Theorem 3.2 assumes, so the
optimality is a target to check against, not a property to assume inherited.

## Not yet read

Scan pages 7-8, 10-12 and 14 (intervening consistency-proof and special-case material inside Sections 2-3),
and scan pages 22-27: Section 4 (tests of the overidentifying restrictions), Section 5 (concluding remarks),
and the two technical appendices, which carry the proofs of Theorems 2.2, 3.1 and 3.2 and not merely their
statements. No claim above draws on any of these.
