---
citekey: cranmer2020
type: article
authors:
  - Cranmer, Kyle
  - Brehmer, Johann
  - Louppe, Gilles
title: 'The frontier of simulation-based inference'
journal: Proceedings of the National Academy of Sciences
volume: 117
number: 48
pages: 30055-30062
year: 2020
doi: 10.1073/pnas.1912789117
arxiv: '1911.01429'
pdf: PDF_papers/Cranmer_2020_frontier-of-simulation-based-inference.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/cranmer2020.md  # line-by-line against the held PDF, 2026-09-22: re-confirmed both prior corrections against the full text and a page-1 render (no "synthetic likelihood" or Wood/Price citation anywhere, no "Colloquium Paper" branding anywhere), no new defect found. Promoted to VERIFIED, full paper read
author: agent
routing:
  - FEED
verify_flags:
  - 'Page 1 (title, author list, abstract, opening of the introduction) read directly from the held PDF via
    text extraction on 2026-09-21. The technical review of specific SBI methods (later sections) is not yet
    read.'
  - 'Full text (all 10 pages, Sections 1-4 plus references) read on 2026-09-22 during the line-by-line audit,
    specifically to check the "Use in this record" section''s claim that the paper''s own vocabulary names a
    "synthetic likelihood" branch. It does not: the string "synthetic likelihood" does not occur anywhere in
    this PDF (checked by full-text search), and the only "Wood" cited (refs. 58, 66, 90) is Frank Wood, a
    probabilistic-programming researcher unrelated to Simon N. Wood''s synthetic-likelihood method that
    `wood2010`/`frazier2023` describe; "Price" is not cited at all. Page 1 was also rendered as a PNG to check
    the "article type: Colloquium Paper, Statistics" row, which is likewise absent from this PDF (see Values).
    Section 3.D ("Recommendations") was read in full and does give concrete guidance, but organised around
    what auxiliary quantities (scores, likelihood ratios) are extractable from the simulator, never by name
    against "synthetic likelihood".'
verified_date: 2026-09-22
summary: >
  A colloquium-paper review of simulation-based inference across the sciences: what unifies likelihood-free /
  implicit-model inference, and how neural density estimation and related methods are changing what is
  tractable. Task-specified item 10 (arXiv:1911.01429). Read as orientation and vocabulary rather than for a
  citable technique this record adopts directly.
loci:
  - methods/06
section: method-anchors
---

# cranmer2020

VERIFIED for the paper in full (all 10 pages, Sections 1-4 and the reference list). Read cover to cover on
2026-09-22.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | PNAS **117**(48), 30055-30062 (2020) | cross-checked against secondary listings, not yet against the held PDF's own masthead |
| DOI | 10.1073/pnas.1912789117 | arXiv abstract-page listing |
| arXiv identifier | 1911.01429v3, 2 Apr 2020 | p. 1 header |
| affiliations | Center for Cosmology and Particle Physics / Center for Data Science, NYU (Cranmer, Brehmer). Montefiore Institute, University of Liege (Louppe) | p. 1 |
| article type | Colloquium Paper, Statistics | reported by a secondary source (the published PNAS record), not present anywhere in this held arXiv preprint. Checked by full-text search and by rendering p. 1 as an image on 2026-09-22. The arXiv version carries no PNAS branding, category label, or sidebar at all |

## What it says, in its own terms

Verbatim, the abstract: "Many domains of science have developed complex simulations to describe phenomena of
interest. While these simulations provide high-fidelity models, they are poorly suited for inference and lead to
challenging inverse problems. We review the rapidly developing field of simulation-based inference and identify
the forces giving new momentum to the field. Finally, we describe how the frontier is expanding so that a broad
audience can appreciate the profound change these developments may have on science." (p. 1). Its own keyword line
names the vocabulary: "Statistical inference | Implicit models | Likelihood-free inference | Approximate Bayesian
Computation | Neural density estimation" (p. 1).

## Use in this record

This record's own approach, a physics simulation (the twin) whose likelihood is not written down analytically
but whose output is compared statistically against data, through summary statistics (windowed moments) whose
bias and covariance the simulation itself measures, is, in this paper's own vocabulary, an implicit-model /
likelihood-free inference problem (both terms are the paper's own, p. 1: "Such models are often referred to as
implicit models" and "dubbed likelihood-free inference"), for which the paper's own preferred umbrella term is
`simulation-based inference`. Corrected 2026-09-22: this paper itself never uses the term `synthetic
likelihood` and never cites Wood (2010) or Price et al. (2018). This was checked by a full-text search of all 10
pages, which found zero occurrences of `synthetic likelihood` and confirmed the only `Wood` in the reference
list (refs. 58, 66, 90) is Frank Wood, a probabilistic-programming researcher, not Simon N. Wood. So `the
synthetic likelihood branch` is this record's own classification, cross-referencing this record's separately-held
`wood2010` and `frazier2023` notes, layered onto this paper's terms, not a branch this review itself names or
covers. What the paper does present as a comparable `traditional` approach (Sec. 1.C) is "creating a model for
the likelihood by estimating the distribution of simulated data with histograms or kernel density estimation",
which is philosophically adjacent to synthetic likelihood (both approximate an intractable likelihood from
simulated summary-statistic distributions) but is not named that way here, and sits alongside ABC as one of the
two `traditional` methods the paper contrasts against its main subject: the newer neural-network-based methods
(normalizing flows, likelihood/likelihood-ratio estimation, probabilistic programming). Its value here is
orientation: placing this record's method inside the field's own taxonomy using the paper's own terms, and
checking (Sec. 3.D, now read) whether the neural or ABC alternatives it surveys would outperform the current
Gaussian-synthetic-likelihood plan at this record's own coordinate count and replica budget.

## Not yet read (as of 2026-09-21, updated 2026-09-22)

As of 2026-09-21 the technical review of specific method families (ABC, neural likelihood/posterior/ratio
estimation) was unread. It was read in full during the 2026-09-22 audit (see verify_flags): the paper covers
ABC (including classifier ABC and active-learning variants), classical density estimation, neural surrogates
for the likelihood/posterior/likelihood-ratio, normalizing flows, GANs, probabilistic programming, and
score/ratio-augmented training. Its Sec. 3.D `Recommendations` gives concrete guidance, but organised around
what auxiliary quantities (scores, likelihood ratios, gradients) can be extracted from the simulator and
whether good hand-built summary statistics already exist. It never frames the choice as `synthetic likelihood
vs. neural alternatives` by name, since it does not use the term `synthetic likelihood` at all (see the
Use-in-this-record section above, corrected there). So the specific comparison sought here is not something this paper makes. What
it does offer is the more general decision criteria above, which this record could still apply to a
synthetic-likelihood-style summary-statistic construction without the paper naming it as such.
