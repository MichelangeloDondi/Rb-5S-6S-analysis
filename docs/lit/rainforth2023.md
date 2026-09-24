---
citekey: rainforth2023
type: article
authors:
  - Rainforth, Tom
  - Foster, Adam
  - Ivanova, Desi R.
  - Bickford Smith, Freddie
title: 'Modern Bayesian Experimental Design'
journal: Statistical Science
year: 2023
doi: null
arxiv: '2302.14545'
pdf: PDF_papers/Rainforth_2023_modern-bayesian-experimental-design.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/rainforth2023.md  # line-by-line against the held PDF, 2026-09-22: re-confirmed no factual defect, re-confirmed the summary's gradient-based/amortized claim against Sections 3.4.1 and 4, one overclaim candidate considered and refuted. Promoted to VERIFIED for the pages read
author: agent
routing:
  - FEED
verify_flags:
  - 'Page 1 (title, author list, abstract, opening) read directly from the held PDF via text extraction on
    2026-09-21. The technical review of estimators and design algorithms (the paper''s body) is not yet read.'
  - 'Sections 3.4.1 and 4 (pp. 6-8) were additionally read on 2026-09-22, during the line-by-line audit, solely
    to check the summary''s "(gradient-based and amortized methods)" characterization against the paper''s
    actual content: Section 3.4.1 is titled "Stochastic Gradient Schemes" and Section 4 introduces Deep
    Adaptive Design (DAD), which amortizes cost via an upfront-trained policy network (ref. [42]''s own title
    is "Deep adaptive design: amortizing sequential Bayesian experimental design"). The characterization holds.
    Nothing else in the body is drawn upon; the specific estimators, equations, and comparative results remain
    unread.'
  - 'Reference [23], cited on p. 1 among the earlier reviews the paper follows on from, is Chaloner and
    Verdinelli (1995) in the reference list (p. 11). That page lies outside the verified scope stated in the
    body. The identification rests on the first line-by-line audit
    (private/cache/lit_intake_2026-09-21/audits/rainforth2023.md, 2026-09-22), and only the section on the
    relation to chaloner1995 draws on it, marked there as outside the pages verified.'
verified_date: 2026-09-22
summary: >
  A current review of Bayesian experimental design: the decision-theoretic framework for choosing which
  experiment (or which condition, in this record's language) to run next, and recent computational advances
  (gradient-based and amortized methods) that make it tractable at scale. It is the recent-advances companion
  to the classic Chaloner and Verdinelli (1995) review, which is held and read in full as chaloner1995. Held
  since 2026-09-21, when it stood in for that review because no freely downloadable copy of it had been found.
loci:
  - methods/06
section: method-anchors
---

# rainforth2023

VERIFIED for page 1 (title, authors, abstract, keywords) and Sections 3.4.1 and 4 (pp. 6-8). The specific
estimators, equations and design algorithms elsewhere in the body, and Section 5's future-directions content,
were not read, and their detail is not claimed above.

## Values

| field | value | where in the paper |
|---|---|---|
| venue | "Accepted for Publication in Statistical Science" | p. 1, printed above the title |
| arXiv identifier | 2302.14545v2, 29 Nov 2023 | p. 1 header |
| authors | Tom Rainforth, Adam Foster, Desi R. Ivanova, Freddie Bickford Smith | p. 1 (matches the arXiv-listed author metadata exactly, including the title extraction) |

## What it says, in its own terms

Verbatim, the abstract: "Bayesian experimental design (BED) provides a powerful and general framework for
optimizing the design of experiments. However, its deployment often poses substantial computational challenges
that can undermine its practical use. In this review, we outline how recent advances have transformed our
ability to overcome these challenges and thus utilize BED effectively, before discussing some key areas for
future development in the field." (p. 1). Key words listed: "Bayesian optimal design, Bayesian adaptive design,
active learning, adaptive design optimization, information maximization." (p. 1).

## Relation to Chaloner and Verdinelli (1995)

The literature intake of 2026-09-21 named either Chaloner and Verdinelli (1995) or a recent arXiv review for
this slot. That review was searched for the same day: it is hosted on Project Euclid, but a freely
downloadable PDF was not confirmed there, and the other copies found (a UC Berkeley course-readings mirror, a
Semantic Scholar listing) are third-party teaching mirrors, not an arXiv or publisher open-access copy, so it
was not downloaded under that intake's sourcing rule. This 2023 review, arXiv-hosted and current, was held in
its place.

A copy of Chaloner and Verdinelli (1995) was obtained on 2026-09-22 and read in full, and it has its own note,
[`chaloner1995`](chaloner1995.md). This paper is therefore no longer a stand-in but the complementary review of
recent advances in the same decision-theoretic BED framework the older review set out: its abstract presents
it as an outline of how "recent advances" have transformed the ability to use that framework effectively
(p. 1). Its introduction also cites earlier reviews of the field (p. 1), and the first line-by-line audit found
Chaloner and Verdinelli (1995) among them, as ref. [23] in the reference list on p. 11, a page outside those
verified here. The classical criteria (Bayesian D-, A-, c-, E- and G-optimality, local optimality, sequential
and batch-sequential design) are read from chaloner1995. What this paper adds is the computational side the
older review predates, gradient-based and amortized design, and of that only Sections 3.4.1 and 4 (pp. 6-8)
have been read here.

## Use in this record

This record's own design question ("which conditions break which degeneracies," priced by the twin in hours)
is a Bayesian-experimental-design problem in this paper's own terms: choosing among candidate experimental
conditions (power, temperature, waist, platform) to maximize information about the parameters that matter,
under a simulator (the twin) that can be run at any candidate condition but has no tractable likelihood. The
"computational challenges" the abstract names as BED's practical obstacle are presumably the same ones this
record already works around by hand (pricing conditions by twin-hours instead of by a formal information
criterion). The "recent advances" reviewed here are, confirmed 2026-09-22 by reading Sections 3.4.1 and 4,
gradient-based optimization schemes and amortized policy networks such as Deep Adaptive Design. Whether either
could replace or augment this record's own hand-pricing is the open question left here for whoever reads the
rest of the body next.

## Not yet read

The technical content beyond the two section headings checked in the audit (Section 3.4.1, "Stochastic
Gradient Schemes", and Section 4, "Deep Adaptive Design"), the specific estimators, equations, and design
algorithms, and what "key areas for future development" the authors identify in Section 5, is unread. Beyond
the "(gradient-based and amortized methods)" characterization confirmed in the audit, no specific method's
mechanics or claimed results should be attributed to this paper beyond that.
