---
citekey: smith1993
type: article
authors:
  - Smith, Anthony A., Jr.
title: 'Estimating Nonlinear Time-Series Models Using Simulated Vector Autoregressions'
journal: Journal of Applied Econometrics
volume: 8
number: S1
pages: S63-S84
year: 1993
doi: 10.1002/jae.3950080506
arxiv: null
pdf: PDF_papers/Smith_1993_simulated-vector-autoregressions-nonlinear-time-series.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/smith1993.md  # line-by-line against the held PDF, 2026-09-22: one citation-year attribution ("Smith 1990" vs "Smith 1993" in gourieroux1993's introduction, independently re-checked against gourieroux1993's own PDF) and one imprecise OCR-run-together description corrected, with Table II's RMSE ratios (1.063-1.129) reconfirmed
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'Pages 1-2 read directly from the held PDF via text extraction on 2026-09-21 (title, author, journal header,
    summary, opening of the introduction). The two estimators'' construction and the Monte Carlo comparison
    (the paper''s technical core) are not yet read.'
  - 'Full text (all 22 pages, including Sections 2-6, the two Technical Appendices, the acknowledgements, and
    the reference list) was read on 2026-09-22 for the line-by-line audit -- beyond the "Pages 1-2" the note
    itself draws on -- specifically to confirm the OCR-run-together observation below, the Table II
    mean-squared-error finding already summarized below, and to resolve the "Smith (1990)" citation traced in
    "Use in this record". Nothing else from the body is newly asserted from it; the estimators'' formal
    construction and the Monte Carlo/empirical mechanics remain outside what this note claims to know.'
verified_date: 2026-09-22
summary: >
  Develops two simulation-based estimators for nonlinear dynamic economic models that require little analytical
  tractability, relying on numerical simulation of the model's own dynamics rather than a tractable likelihood;
  reports that the less asymptotically-efficient of the two has smaller mean squared error in realistic sample
  sizes. Task-specified item 8 (paired with Gourieroux, Monfort & Renault 1993, an early companion to indirect
  inference published in the same JAE special issue, immediately adjacent in the volume, S63-S84 against
  S85-S118).
loci:
  - methods/06
section: method-anchors
---

# smith1993

VERIFIED: the full held PDF (all 22 pages) was read on 2026-09-22. Every claim below is grounded in that
read. Sections 2-6's formal estimator construction, propositions and Monte Carlo and empirical mechanics
were seen but are not asserted here (see "Read but not drawn upon").

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | J. Appl. Econ. **8**(S1), S63-S84 (1993) | p. 1 (held PDF's own masthead) |
| author and affiliation | A. A. Smith, Jr., Graduate School of Industrial Administration, Carnegie Mellon University, and Department of Economics, Queen's University, Kingston, Ontario | p. 1 |
| held-PDF page count | 22 | matches the S63-S84 range (22 pages) exactly |
| special issue | Special Issue on Econometric Inference Using Simulation Techniques | shared with `gourieroux1993`, immediately preceding it in the same volume |

## What it says, in its own terms

Verbatim, the summary (this paper's own term for its abstract): "This paper develops two new methods for
conducting formal statistical inference in nonlinear dynamic economic models. The two methods require very
little analytical tractability, relying instead on numerical simulation of the model's dynamic behaviour."
(p. 1). The summary continues (OCR of the scan runs some words together throughout the summary, already twice
within the quotation above, 'simulationof' and 'dynamicbehaviour,' silently despaced there as ordinary
transcription, and more disruptively past this point, e.g. 'meansquarederror' for 'mean squared error,' so the
remainder is paraphrased instead of quoted): a Monte Carlo study is reported to
show that, for a specific application, the less asymptotically-efficient of the two estimators has smaller mean
squared error at sample sizes typical of macroeconomics, and the estimator with the better small-sample
performance is then used to fit a real-business-cycle model to observed US time-series data.

## Use in this record

Published in the same 1993 JAE special issue as `gourieroux1993`, immediately before it (S63-S84 against
S85-S118). `gourieroux1993`'s own introduction credits this author's method as the origin of 'this kind of
method' (see `gourieroux1993`'s note), but under the citation 'Smith (1990)', not 'Smith (1993)'. Checked
against this paper's own text for this audit (2026-09-22): 'Smith (1990)' is, precisely, "the author's PhD
dissertation at Duke University" (this paper's own acknowledgements, p. S83), of which "this paper is based on
Chapters 2 and 3" (same acknowledgement): full citation in this paper's own reference list as "Smith, Jr,
A. A. (1990), *Three Essays on the Solution and Estimation of Dynamic Macroeconomic Models*, PhD dissertation,
Duke University" (p. S84). That is an earlier, closely related document by the same author, not this exact
1993 article. `gourieroux1993`'s own bibliography, however, carries no separate 1990 entry, only "Smith, A.
(1993) ... this issue", so its own accounting treats the two as one reference despite the year mismatch in its
running text. The "first proposed" credit to this author's lineage stands. The identification of it with this
exact 1993 article is now stated precisely instead of assumed.

Its reported finding, that a less asymptotically-efficient simulation-based estimator
can have smaller mean squared error than a more efficient one, at realistic sample sizes, is a direct, and
useful, caution against this record reading "asymptotically efficient" as the only criterion for choosing among
its own candidate estimators of a windowed-moment coordinate (this record's own methods chapter already makes
exactly this distinction for a different pair of estimators, `docs/methods/06_the_statistics.md` section 4.14's
*a summary statistic is not an estimator* discussion and the profile-likelihood-versus-cumulant duel in
`results/estimator_duel.csv`). Worth reading in full alongside that section once the technical core is read: this
paper may be the origin, in the indirect-inference literature, of the same efficient-but-fragile-versus-
inefficient-but-robust pattern this record has already found empirically in its own duel.

## Read but not drawn upon

Sections 2-6 (the formal construction of the extended method of simulated moments and of simulated
quasi-maximum likelihood, Propositions 1-5 and their proofs in the
two Technical Appendices, and the Monte Carlo and empirical mechanics beyond Table II's own numbers) were
read but are not asserted above: the specific mechanism behind the efficiency and robustness trade-off
reported in the summary is seen but not built upon. The claims above rest on the summary (p. 1), the
acknowledgements (p. S83) and the reference list (p. S84), and, for the mean-squared-error finding,
Table II (p. S75).
