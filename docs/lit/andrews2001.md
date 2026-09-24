---
citekey: andrews2001
type: article
authors:
  - Andrews, Donald W. K.
  - Lu, Biao
title: 'Consistent model and moment selection procedures for GMM estimation with application to dynamic panel data models'
journal: Journal of Econometrics
volume: 101
number: 1
pages: 123-164
year: 2001
doi: 10.1016/S0304-4076(00)00077-4
arxiv: null
pdf: PDF_papers/Andrews_2001_consistent-model-and-moment-selection-GMM-panel.pdf
held: true
section: method-anchors
status: VERIFIED
verified_date: 2026-09-24
summary: 'Extends moment selection to choose a model and its moment conditions together, and cautions that asking one dataset every question at once degrades finite-sample behaviour.'
audit: private/cache/lit_intake_2026-09-24_audits/finance_intake.md
routing:
  - CITE
  - FEED
verify_flags:
---

# Andrews and Lu 2001: selecting the model and the moments together, with a warning this record should read

**Why this record holds it.** This record's problem is joint by construction: which terms belong
in the forward model and which coordinates belong in the likelihood vector are decided together,
because a coordinate's bias depends on the term list. This paper is the joint version of
andrews1999 and carries a caution aimed squarely at the ultra-joint ambition.

## What it does

It extends the moment selection criteria to select a model and its moment conditions
simultaneously, and studies the finite-sample behaviour by Monte Carlo on dynamic panel data.

## The caution, which is the reason to cite it

The paper says plainly that asking one dataset everything at once is not free: "in any one
application, one would not want to try to use the data to answer all of these questions
simultaneously". The general framework exists for theoretical coverage, not as an instruction to
estimate everything jointly.

**Against this record's own main aim that is a tension.**
The aim is an ultra-joint MLE across every observable. This paper's authors, who built the joint
machinery, warn that the joint question degrades finite-sample behaviour. The reconciliation this
record can offer is its twin: where their finite-sample cost is unmeasurable without one, here it
is exactly what the bias surface measures. That is a real answer rather than a dismissal, and it
is also a claim that has to be demonstrated on the twin before the chapter leans on it.
