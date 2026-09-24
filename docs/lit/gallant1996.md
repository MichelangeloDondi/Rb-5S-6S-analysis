---
citekey: gallant1996
type: article
authors:
  - Gallant, A. Ronald
  - Tauchen, George
title: 'Which moments to match?'
journal: Econometric Theory
volume: 12
number: 4
pages: 657-681
year: 1996
doi: 10.1017/S0266466600006976
arxiv: null
pdf: PDF_papers/Gallant_1996_which-moments-to-match-EMM.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/gallant1996.md  # line-by-line against the held PDF, 2026-09-22: removed an unsupported Duke-page provenance claim from verify_flags (the cover sheet confirms only a JSTOR download); all bibliographic fields, Definition 1/Eq. 4 and the three-case framework confirmed exactly; the summary's 'EMM' label considered and kept (matches the held file's own name, though absent from the paper's own running text)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article, a 2012 JSTOR download with its own cover
    sheet. Read on 2026-09-22: abstract, Section 1 and the opening of Section 2 through
    Definition 1 and the three cases. The asymptotic theorems and the three
    applications of Section 4 were not read. The DOI and journal reference confirmed
    against Crossref on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  The efficient method of moments (EMM), the statistics answer to "which moments?".
  Instead of choosing a few low-order moments ad hoc, use the expected SCORE of an
  auxiliary model with a convenient analytic density (the "score generator"),
  evaluated at its quasi-maximum-likelihood fit to the data, as the GMM moment
  conditions, with expectations under the structural model computed by simulation,
  quadrature or formula. If the structural model is smoothly embedded in the auxiliary
  one, the estimator is as efficient as maximum likelihood; if the auxiliary model
  approximates the data well, it is nearly efficient.
loci:
  - methods/06
section: method-anchors
---

# gallant1996

VERIFIED for the sections named in the flags. Held (published version). Read on 2026-09-22.

## What it says

The paper presents a systematic alternative to the common practice of selecting a few low-order moments ad hoc (Section 1). Fit an auxiliary model with an analytic density to the data by quasi-maximum likelihood. Take its score (the derivative of its log density with respect to its own parameters) as the vector of moment conditions. Choose the structural parameters so that the score's expectation under the structural model, computed by simulation, quadrature or analytic expressions, is zero, in a GMM criterion whose optimal weighting depends only on the auxiliary model. The auxiliary model need not nest the structural one. If it does, through a smooth map from the structural to the auxiliary parameters (Definition 1, Eq. 4), the estimator has the maximum-likelihood asymptotic distribution. The estimator pays off when expectations under the structural model are easy but its likelihood is not.

## Use in this record

- A principled replacement for "moments to mu_12". Take a fast analytic line-shape model as the score generator (a Voigt with Gauss-Hermite shape terms, or the closed power-law-Lorentzian form of hilton2020), fit it to each trace, and match its score's expectation computed by the twin's full volume model. The matched quantities are then as informative as the auxiliary model is good, and ML-efficient if it nests.
- It says where the efficiency comes from, which is the point a referee will probe: a moment set is efficient to the extent that it spans the score. With alsing2018 and heavens2000 this closes the argument for the three-way comparison.
- It also shows why ad hoc low-order moments lose: they span only part of the score.

## Limits

- Asymptotic theory under stated regularity conditions (Gallant 1987 assumptions), unread here. The applications are econometric.
