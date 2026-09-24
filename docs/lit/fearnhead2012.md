---
citekey: fearnhead2012
type: article
authors:
  - Fearnhead, Paul
  - Prangle, Dennis
title: 'Constructing summary statistics for approximate Bayesian computation: semi-automatic approximate Bayesian computation'
journal: Journal of the Royal Statistical Society, Series B
volume: 74
number: 3
pages: 419-474
year: 2012
doi: 10.1111/j.1467-9868.2011.01010.x
arxiv: '1004.1112'
pdf: PDF_papers/Fearnhead_2012_semi-automatic-ABC-summary-statistics.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/fearnhead2012.md  # line-by-line against the held PDF, 2026-09-22, upgraded to VERIFIED: the title was confirmed as the published JRSS-B form by a Crossref lookup on the DOI, the held preprint's own abbreviated page-1 subtitle is the pre-publication form, no other defects found
author: agent
routing:
  - FEED
verify_flags:
  - 'Page 1 (title, author list, abstract) read directly from the held PDF via text extraction on 2026-09-21.
    The theoretical result on optimal summary statistics and the simulation-based estimation procedure that
    constructs them (the paper''s technical core) are not yet read.'
  - 'Sections 1-4.3 (introduction, ABC algorithms, Theorems 1-5 on calibration/accuracy/optimality, the
    semi-automatic construction procedure, and the first two of five worked examples), the references, and the
    final two appendix figures were read on 2026-09-22 during the line-by-line audit -- roughly two-thirds of
    the 44-page PDF by line count. This confirmed the note''s existing claims about Theorem 3 (posterior means
    are optimal, under quadratic loss with any full-rank weight matrix, as h -> 0) and the Section 3 linear-
    regression construction without finding any misattribution. Page 1 was also rendered as a PNG, which found
    that this held preprint''s own title reads "...: Semi-automatic ABC" (abbreviated), not the frontmatter''s
    fully spelled-out "...: semi-automatic approximate Bayesian computation" -- see Values. Sections 4.4-4.6
    (the remaining three examples) and the discussion/conclusion remain unread; nothing in this note draws on
    them.'
verified_date: 2026-09-22
summary: >
  A JRSS-B "read paper" showing that the optimal ABC summary statistics, for accurate inference about a
  parameter of interest, are the posterior means of the parameters, and proposing an extra simulation stage to
  estimate how those posterior means vary as a function of the data, then using those estimates as the summary
  statistics. Task-specified item 9 (arXiv:1004.1112). Relevant to this record's own choice of coordinates
  (which windowed-moment ratios) as a semi-automatic alternative to choosing them by hand from twin-measured
  bias behaviour.
loci:
  - methods/06
section: method-anchors
---

# fearnhead2012

VERIFIED for the abstract, Sections 1-4.3, the references and the final two appendix figures
(roughly two-thirds of the paper by line count, including Theorem 3 and the Section 3 construction
in full). Sections 4.4-4.6 and the discussion/conclusion are named only by topic, cited to what they
cover, not reproduced, and were not read here.

## Values

<!-- not-from-pdf: the published-title row below is quoted from a Crossref bibliographic lookup on
     the DOI, 2026-09-22, not from the held arXiv preprint's own title page. -->
| field | value | where in the paper |
|---|---|---|
| journal reference | J. R. Stat. Soc. B **74**(3), 419-474 (2012) | cross-checked against secondary listings, not the held PDF's own masthead |
| DOI | 10.1111/j.1467-9868.2011.01010.x | secondary listing (RSS Wiley Online Library) |
| arXiv identifier | 1004.1112v2, 13 Apr 2011 | p. 1 header |
| affiliation | Department of Mathematics and Statistics, Lancaster University, UK | p. 1 |
| paper length | 44 pages (held PDF) | consistent with a JRSS-B `read paper`, published with discussion (companion discussion papers exist, e.g. arXiv:1201.1893, not held here) |
| title, as this held PDF's own p. 1 gives it | "Constructing Summary Statistics for Approximate Bayesian Computation: Semi-automatic ABC" | p. 1, confirmed by rendering it as an image on 2026-09-22: the subtitle abbreviates to `ABC` here |
| title, as published (matches the frontmatter `title:` field) | Crossref's record for this DOI gives "Constructing Summary Statistics for Approximate Bayesian Computation: Semi-Automatic Approximate Bayesian Computation", the subtitle spelled out in full, matching the frontmatter field. The held preprint's own page 1, row above, carries the shorter pre-publication subtitle instead | Crossref lookup on the DOI, 2026-09-22, not from the held PDF |

## What it says, in its own terms

Verbatim, the abstract: "Many modern statistical applications involve inference for complex stochastic models,
where it is easy to simulate from the models, but impossible to calculate likelihoods. Approximate Bayesian
computation (ABC) is a method of inference for such models. It replaces calculation of the likelihood by a step
which involves simulating artificial data for different parameter values, and comparing summary statistics of
the simulated data to summary statistics of the observed data. Here we show how to construct appropriate summary
statistics for ABC in a semi-automatic manner. We aim for summary statistics which will enable inference about
certain parameters of interest to be as accurate as possible. Theoretical results show that optimal summary
statistics are the posterior means of the parameters. While these cannot be calculated analytically, we use an
extra stage of simulation to estimate how the posterior means vary as a function of the data; and then use these
estimates of our summary statistics within ABC." (p. 1).

## Use in this record

This record already has a design principle for choosing coordinates, windowed moments and ratios chosen by
their twin bias per window, never accumulated (this repository's own rule file), which is a hand-driven,
physics-informed version of exactly the problem this paper automates: which summary statistics of a
simulator-generated dataset carry the most information about the parameters of interest. The paper's central
result, that the optimal summaries are the posterior means of the parameters (themselves estimated by an extra
simulation stage), is a candidate cross-check for this record's hand-chosen coordinate set: if a
semi-automatically constructed summary (regressing a trial parameter on twin-simulated moment vectors) picks out
combinations close to the ones already chosen by twin-bias reasoning, that is evidence the manual choice is
close to optimal. If it picks out something different, that is either a gap in the manual coordinate set or a
sign the automatic procedure needs the parameter of interest correctly specified (which, for a design question
like this record's "which conditions break which degeneracies," is not always a single scalar).

## Not yet read (as of 2026-09-21, updated 2026-09-22)

As of 2026-09-21 the theorem establishing posterior means as optimal (Section 2) and the practical procedure
for estimating them by simulation (Section 3) were unread. Both were read in full during the 2026-09-22 audit
(see verify_flags). The exact conditions are: Theorem 3 holds for quadratic loss `L(theta0, theta_hat; A) =
(theta0 - theta_hat)^T A (theta0 - theta_hat)` for any full-rank positive-definite weight matrix A (so the
record is free to weight parameters unevenly), in the asymptotic regime h -> 0 (the ABC bandwidth shrinking to
zero), the two conditions that needed checking here. Section 3's construction fits
`theta_i = beta_0 + beta^(i) f(y) + noise` by linear regression of simulated parameter draws on (possibly
nonlinear) functions of simulated data, per parameter of interest. Sections 4.4-4.6 (the ecological, queueing,
and epidemiological examples) and the discussion/conclusion remain unread. Nothing claimed here
depends on them.
