---
citekey: hosking1990
type: article
authors:
  - Hosking, J. R. M.
title: 'L-Moments: Analysis and Estimation of Distributions Using Linear Combinations of Order Statistics'
journal: Journal of the Royal Statistical Society, Series B (Methodological)
volume: 52
number: 1
pages: 105--124
year: 1990
doi: 10.1111/j.2517-6161.1990.tb01775.x
arxiv: null
pdf: null
held: false
status: REPORTED
audit: private/cache/lit_intake_2026-09-21/audits/hosking1990.md  # bibliographic fields checked against Crossref/Oxford Academic, 2026-09-22; exact match; no claim of having read the paper found
author: agent
routing:
  - CITE
verify_flags:
  - 'Not held. Bibliographic record confirmed via Crossref (query.bibliographic, 2026-09-21):
    exact title match, journal, volume, issue, pages and DOI as given (also independently visible
    on the Oxford Academic and Wiley listing pages for the same article). No abstract or page was
    read; the description below is a paraphrase of search-engine summaries and of the concept''s
    standard definition, not a verbatim quotation or a claim about the paper''s own derivations.'
verified_date: null
summary: >
  Defines L-moments: expectations of linear combinations of order statistics, forming an
  alternative to ordinary (power) moments that exist whenever the mean exists, are less sensitive
  to outliers and heavy tails, and whose sample estimates are more robust than ordinary sample
  moments of the same order. The paper the task names for exactly the reason ordinary moments can
  misbehave in heavy-tailed or noisy settings. Paywalled (RSS/Wiley); not fetched.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# hosking1990

REPORTED. Not held: behind the Royal Statistical Society / Wiley paywall (also listed on JSTOR),
no open-access or preprint copy located by search on 2026-09-21. Everything below is second-hand.

## What is reported about it

J. Roy. Statist. Soc. Ser. B **52**(1), 105-124 (1990), DOI 10.1111/j.2517-6161.1990.tb01775.x. A
search-engine summary of the paper's own abstract describes L-moments as "expectations of certain
linear combinations of order statistics," definable "for any random variable whose mean exists,"
forming "the basis of a general theory which covers the summarization and description of
theoretical probability distributions, the summarization and description of observed data samples,
estimation of parameters and quantiles of probability distributions, and hypothesis tests for
probability distributions" (paraphrased/summarized from search results, and not confirmed as a direct
quotation of the paper's own wording since no page was read).

The general property that motivates citing this paper, standard in the hydrology and extreme-value
literature that adopted L-moments widely, is that ordinary higher moments of a heavy-tailed or
noisy sample are dominated by a few extreme values and can have large or even undefined variance,
while the corresponding L-moment is a bounded linear functional of the order statistics and is
comparatively well-behaved.

## Use in this record

Named in the strategy document as the reason "hydrology uses L-moment ratios... precisely because
ordinary moments misbehave in heavy tails." This record's own programme uses ordinary
(power/cumulant) moments, not L-moments, and its own truncated-window machinery is a different
answer to a related problem (moments of a distribution observed only through a finite window, with
a correction that is derived, not empirical). Citing this paper supports the claim that "moments can
misbehave, and a field has built an alternative moment family to cope" as a general precedent,
without this record adopting L-moments itself. Whether an L-moment-style linear-combination-of-
order-statistics estimator could be built for a windowed atomic lineshape (as opposed to a sample
of independent draws, which is what L-moments were built for) is an open methodological question
left unanswered here, one the paper itself, unread, cannot yet inform.
