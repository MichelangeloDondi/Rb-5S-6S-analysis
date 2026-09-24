---
citekey: frazier2023
type: misc
authors:
  - Frazier, David T.
  - Drovandi, Christopher
  - Nott, David J.
title: 'Bayesian Synthetic Likelihood'
journal: arXiv preprint (forthcoming in Wiley StatsRef -- Statistics Reference Online)
year: 2023
doi: null
arxiv: '2305.05120'
pdf: PDF_papers/Frazier_2023_bayesian-synthetic-likelihood-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/frazier2023.md  # line-by-line against the held PDF, 2026-09-22: the exact quotation, affiliations, arXiv id and every Sec. 2.2/2.3 claim confirmed, and the price2018/wood2010 "not held" framing corrected (both PDFs arrived in PDF_papers/ before this audit)
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'Page 1 (title, author list, abstract) read directly from the held PDF via text extraction on 2026-09-21.
    The body sections on the BSL construction and its scalable/robust extensions are not yet read.'
  - 'Full text (all 13 pages, Sections 1-2.3, acknowledgements and references) read on 2026-09-22 during the
    line-by-line audit. This confirmed rather than contradicted the note''s existing claims: the body does
    cover the BSL construction (Wood 2010''s synthetic-likelihood definition, Price et al. 2018''s BSL
    posterior), the "scalable" extensions (Sec. 2.2: KDE-based, transformation-KDE, whitening, variational BSL,
    GP-surrogate methods) and the "robust" extensions (Sec. 2.3: R-BSL and the two-step correction for model
    misspecification), matching the abstract''s own framing. No claim in this note was found to rest on
    anything outside what it already said it read.'
verified_date: 2026-09-22
summary: >
  A 2023 reference-work entry by two of the four original Bayesian-synthetic-likelihood authors (Drovandi, Nott),
  giving a high-level presentation of BSL and its extensions for scalable and robust posterior inference. Held
  as an arXiv-hosted, more current treatment of the same method by two of price2018's own four authors.
  `PDF_papers/` separately gained price2018's and wood2010's own full text on 2026-09-22, though neither yet
  has its own `docs/lit/` entry.
loci:
  - methods/06
section: method-anchors
---

# frazier2023

VERIFIED for the full held PDF (all 13 pages, arXiv:2305.05120v2). Read in full on 2026-09-22. Every claim
below is grounded in that read except the reported StatsRef venue, named as unconfirmed against this PDF's
own text where it appears in the Values table.

## Values

| field | value | where in the paper |
|---|---|---|
| arXiv identifier | 2305.05120v2, 10 May 2023 | p. 1 header |
| affiliations | Monash University (Frazier), Queensland University of Technology (Drovandi), National University of Singapore (Nott) | p. 1 |
| intended venue | Wiley StatsRef: Statistics Reference Online | reported by a secondary source (WebFetch of the arXiv abstract page on 2026-09-21), not yet independently confirmed against the held PDF's own text |

## What it says, in its own terms

Verbatim, the abstract: "Bayesian statistics is concerned with conducting posterior inference for the unknown
quantities in a given statistical model. Conventional Bayesian inference requires the specification of a
probabilistic model for the observed data, and the construction of the resulting likelihood function. However,
sometimes the model is so complicated that evaluation of the likelihood is infeasible, which renders exact
Bayesian inference impossible. Bayesian synthetic likelihood (BSL) is a posterior approximation procedure that
can be used to conduct inference in situations where the likelihood is intractable, but where simulation from the
model is straightforward. In this entry, we give a high-level presentation of BSL, and its extensions aimed at
delivering scalable and robust posterior inferences." (p. 1). The keyword line: "Synthetic likelihood.
Approximate Bayesian comput[ation...]" (p. 1: the extracted first page ends here).

## Use in this record

This is a reference-work entry, not a research paper: it is meant as a signpost to the field, not as the
primary source for any specific result. Its value here is threefold. It was, when first held, arXiv-hosted and actually on
this record's shelf where `price2018` (the original 2018 paper) was not: `PDF_papers/` has since also gained
price2018's and wood2010's own full text (2026-09-22), though neither yet has its own `docs/lit/` entry. It is
written by two of that paper's own authors, so it is a reasonable proxy for what that paper says at the level this record currently needs (the
overall BSL construction, not a specific equation). And being 2023, not 2018, its "extensions aimed at
delivering scalable and robust posterior inferences" section is reported to cover developments after the original
paper, which may matter for a record whose own coordinate count (about 200-300) is large enough that scalability
is a live concern, not a hypothetical one.

## Not yet read (as of 2026-09-21, updated 2026-09-22)

As of 2026-09-21 the body, the actual BSL construction, and whatever the "scalable and robust" extensions
specifically are, was unread. It was read in full during the 2026-09-22 audit (see verify_flags). Sec. 1
sets up ABC's kernel-based likelihood estimate. Sec. 2 defines Wood (2010)'s synthetic likelihood
(a Gaussian approximation to the summary-statistic likelihood) and Price et al. (2018)'s BSL posterior built
from its noisy, Monte-Carlo-estimated version. Sec. 2.2 catalogues scalability extensions (semi-parametric/KDE
forms, a whitening transformation that relaxes the required number of model simulations from O(d_s^2) to
O(d_s) in the summary-statistic dimension d_s, variational BSL). Sec. 2.3 catalogues two robustness extensions
for model misspecification (R-BSL, and a two-step correction). None of the claims made here turned out to
rest on anything unread or misattributed. This update narrows the scope of what remains genuinely
unread (the underlying proofs in Frazier et al. 2022/2021, cited but not reproduced here) instead of flagging a
defect.
