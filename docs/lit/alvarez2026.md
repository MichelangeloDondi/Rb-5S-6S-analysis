---
citekey: alvarez2026
type: article
authors:
  - Alvarez, Luis A. F.
  - Chiann, Chang
  - Morettin, Pedro A.
title: 'Inference on model parameters with many L-moments'
journal: arXiv preprint
volume: null
number: null
pages: null
year: 2026
doi: null
arxiv: 2210.04146v5
pdf: PDF_papers/Alvarez_2026_inference-with-many-L-moments.pdf
held: true
status: REPORTED
audit: private/cache/lit_intake_2026-09-23/audits/alvarez2026.md
author: agent
routing:
  - CITE
verify_flags:
  - 'Placed by the owner 2026-09-23 beside vanvleck1948. Abstract and title page read at the PDF
    and quoted below verbatim. The body, 110 pages, is not read, so nothing below the summary
    describes a derivation, a theorem or a simulation result. The status stays REPORTED for that
    reason, with the PDF held, and may not be raised without reading the sections a claim rests on.'
  - 'Version held is v5, arXiv stamp 26 Jan 2026, title page dated November 2025. The arXiv
    identifier 2210 dates the first version to October 2022. Any citation states which version.'
verified_date: null
summary: >
  A generalised method of L-moments estimator, and a rule for how many L-moments to use. The
  abstract states the problem this record also has: "The choice of the number of L-moments used
  in estimation remains ad-hoc, though: researchers typically set the number of L-moments equal
  to the number of parameters, which is inefficient in larger samples." It claims that choosing
  the number and weighting them accordingly gives an estimator that "outperforms MLE in finite
  samples, and yet retains asymptotic efficiency", derived in an asymptotic framework where the
  number of L-moments varies with sample size, with methods to select that number automatically.
  Its own keywords name the frame: generalised method of moments, tuning parameter selection,
  higher-order expansions.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

## Why it is on this shelf

It answers, in the statistics literature and for L-moments, the question C6c asks for central
moments: how many statistics enter the vector, and how are they weighted. This record's current
answer is a per-condition Shannon count and a replica-covariance budget at R = 500. The paper's
answer is a selection rule with an asymptotic justification, so the two are comparable and the
comparison is owed before the coordinate count is fixed.

It also bears on the novelty boundary. A132 already places this record's moment block as a
minimum-distance block in the generalised method of moments sense, and this paper is in that same
frame, current, and about choosing the number of statistics. A referee who owns it reads any claim
that selecting the number of statistics is itself novel as already answered for L-moments.

## What is not yet read, and what rests on it

Nothing here rests on the body. The claim that the estimator beats maximum likelihood in finite
samples is quoted from the abstract, not checked, and it is the claim most worth checking, because
this record's main aim is an ultra-joint maximum likelihood and the paper asserts a regime where
moment matching does better. Reading sections on the asymptotic framework and the selection rule
is owed before either is cited in the thesis.
