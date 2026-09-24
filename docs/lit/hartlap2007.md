---
citekey: hartlap2007
type: article
authors:
  - Hartlap, J.
  - Simon, P.
  - Schneider, P.
title: 'Why your model parameter confidences might be too optimistic - unbiased estimation of the inverse covariance matrix'
journal: Astronomy & Astrophysics
volume: 464
pages: 399-404
year: 2007
doi: 10.1051/0004-6361:20066170
arxiv: 'astro-ph/0608064'
pdf: PDF_papers/Hartlap_2007_unbiased-estimation-inverse-covariance-matrix.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/hartlap2007.md
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'All six pages read directly on 2026-09-22, in text and rendered page-image form: the abstract, the
    introduction, Sect. 2 (the estimator and the singularity proof), Sect. 3 (the debiased inverse and its
    footnote, and the Monte Carlo setup), Sect. 4 (marginalised-likelihood and confidence-region bias), Sect. 5
    (the bootstrap and non-Gaussian robustness checks) and Sect. 6 (summary). Every equation cited below (1
    through 29) and every figure caption was read from the source, not from a secondary citation.'
verified_date: 2026-09-22
summary: >
  Proves the sample covariance estimator is singular for p > n (known mean) or p > n-1 (mean estimated from
  the data), derives the "Hartlap factor" (n-p-2)/(n-1) that removes the multiplicative bias of the naive
  inverse sample covariance for p < n-2, and shows by Monte Carlo that even after this correction a
  marginalised log-likelihood and the size of a confidence region (via the Fisher matrix) can still carry
  their own residual bias. This is the literal citation for "Hartlap's factor" in this record's own
  programme description.
loci:
  - methods/06
section: method-anchors
---

# hartlap2007

Held. Read in full against the PDF, text and rendered page images both.

## Values

| field | value | where in the paper |
|---|---|---|
| title | 'Why your model parameter confidences might be too optimistic - unbiased estimation of the inverse covariance matrix' | p. 1, title block. The source sets it as one sentence across a line break, "optimistic -- / unbiased ...", lower-case after the dash. A full stop and a capital Unbiased would make it two sentences, which the source does not |
| journal reference | A&A **464**, 399-404 (2007) | not printed on this preprint. The arXiv PDF's own masthead carries only the A&A manuscript number ("manuscript no. 6170c") and a LaTeX auto-date stamp reading November 26, 2024 (a recompilation artifact unrelated to the paper's real 2006 history: the byline itself reads "Received 3 August 2006 / Accepted 24 November 2006", p. 1). Volume/page cross-checked directly against the reference lists of `sellentin2016` (p. 6, reading Hartlap J., Simon P., Schneider P., 2007, A,A, 464, 399) and `dodelson2013` (p. 5-6, ref. [14], reading J. Hartlap, P. Simon, and P. Schneider, A&A 464, 399 (2007), arXiv:astro-ph/0608064), which agree with each other |
| DOI | 10.1051/0004-6361:20066170 | not printed in this preprint. Carried from the arXiv abstract-page listing, unchanged from before |
| arXiv identifier | astro-ph/0608064v2, 5 Dec 2006 | p. 1 header |
| affiliation | Argelander-Institut für Astronomie, Universität Bonn | p. 1 |
| received / accepted | 3 August 2006 / 24 November 2006 | p. 1 |

## What it says, in its own terms

The abstract, verbatim in full: "Aims. The maximum-likelihood method is the standard approach to obtain
model fits to observational data and the corresponding confidence regions. We investigate possible sources
of bias in the log-likelihood function and its subsequent analysis, focusing on estimators of the inverse
covariance matrix. Furthermore, we study under which circumstances the estimated covariance matrix is
invertible. Methods. We perform Monte-Carlo simulations to investigate the behaviour of estimators for the
inverse covariance matrix, depending on the number of independent data sets and the number of variables of
the data vectors. Results. We find that the inverse of the maximum-likelihood estimator of the covariance is
biased, the amount of bias depending on the ratio of the number of bins (data vector variables), p, to the
number of data sets, n. This bias inevitably leads to an -- in extreme cases catastrophic -- underestimation
of the size of confidence regions. We report on a method to remove this bias for the idealised case of
Gaussian noise and statistically independent data vectors. Moreover, we demonstrate that marginalisation over
parameters introduces a bias into the marginalised log-likelihood function. Measures of the sizes of
confidence regions suffer from the same problem. Furthermore, we give an analytic proof for the fact that the
estimated covariance matrix is singular if p > n." (p. 1, abstract, complete. The commas around "p" and "n"
in the third sentence carry ordinary appositive spacing on the rendered page. The missing spaces in some
raw text extractions of this preprint are a copy artifact, checked directly against the page image).

The estimator and its bias. For n independent realisations d^(k) of a p-dimensional Gaussian vector, the
maximum-likelihood covariance estimator is Ĉ^ML_ij = (1/n) Σ_k (d_i^(k)-μ_i)(d_j^(k)-μ_j) (Eq. 3, p. 2),
unbiased when μ is known, needing a further n/(n-1) factor when μ is estimated from the same data. Section
2.2 proves Ĉ^ML is singular for p > n (known mean) or p > n-1 (estimated mean, the case the paper pursues
throughout), by exhibiting a vector orthogonal to the n-dimensional (or (n-1)-dimensional) subspace the data
vectors span. Section 3.1 shows the naive inverse Ĉ*^-1 = (Ĉ^ML)^-1 has expectation ⟨Ĉ*^-1⟩ = N/(N-p-1) Σ^-1
for p < N-1 (Eq. 16, where N = n-1 when the mean is estimated), so an unbiased estimator of Σ^-1 is

    Ĉ^-1 = [(n-p-2)/(n-1)] Ĉ*^-1  for p < n-2                              (Eq. 17, p. 3, Sect. 3.1)

Footnote 1 on the same page records that Anderson's textbook (Anderson 2003), from which Eq. (17) is
derived, itself carries a typing error, giving (n-p-2)/(n-2) in place of the correct (n-1) denominator. The
paper's own Eq. (17) is the corrected form. The domain p < n-2 is exact and not a rounding convention: at
p = n-2 the factor is precisely zero, and the paper's own summary (Sect. 6, p. 6) states this is "due to the
statistical distribution of the covariance matrix", distinct from the earlier singularity threshold at
p = n-1, which "derives from linear algebra alone."

What survives after debiasing. Section 4 shows the log-likelihood itself is unbiased under Ĉ^-1 (Eq. 22-23,
using the independence of mean and covariance proved at the end of Sect. 2.2), but two further quantities are
not: a log-likelihood marginalised over a nuisance parameter (Eq. 24) carries a residual bias the paper
measures at maximally ≈ 8% for a straight-line fit and less for a power law (Sect. 4.1, p. 4, Fig. 2), and
the square root of the determinant of the inverse Fisher matrix, a common measure of confidence-region size
(Eq. 25-26), is "significantly overestimated, for p/n approaching unity by as much as ≈ 30%" (Sect. 4.2, p.
4, Fig. 2). Section 5 stress-tests the two assumptions the derivation needs (Gaussian noise, statistically
independent data vectors) against a weak-lensing bootstrap example: even with non-independent bootstrap pairs
sharing galaxies across bins, Ĉ^-1 is wrong by only ≈ 1% (p. 5, Fig. 3, N_g = 500, N_bs = 40). Under
log-normal (non-Gaussian) noise Eq. (17) is "no longer applicable" in the strict sense but "for p/n > 0.2, one
still does much better with it than without it" (p. 5).

## Use in this record

This is the paper this record's own programme description names directly for the correction it applies when
inverting a twin-estimated covariance. Its abstract's own singularity condition, "the estimated covariance
matrix is singular if p > n" (p. 1), is the reason a naive inverse is unsafe whenever a coordinate count sits
anywhere close to a replica count.

**The Hartlap factor at n = 500 replicas, p = 50 coordinates.** Substituting directly into Eq. (17), Sect.
3.1: (n-p-2)/(n-1) = (500-50-2)/(500-1) = 448/499 ≈ 0.898. The naive inverse Ĉ*^-1 must be scaled down by
about 10.2% to be unbiased for Σ^-1 at this size, equivalently the naive inverse's own expectation over-states
the precision matrix by a factor 499/448 ≈ 1.114 (Eq. 16), which is exactly the "components... too large...
log-likelihood... too steep... confidence contours too small" direction the abstract names. The positivity
domain n > p + 2, i.e. p < n-2 (Eq. 17's own condition), is satisfied here with a wide margin: 500 > 52 by 448,
not by the single unit that would put the correction near its own zero.

**What the factor does not fix, at this same size.** Sect. 4's two residual-bias results are stated for the
paper's own straight-line and power-law toy models, not for a windowed-moment likelihood, so their ≈8% and
≈30% figures cannot be carried over as this record's own numbers. What transfers is the qualitative warning:
a debiased Ĉ^-1 makes the full log-likelihood unbiased (Sect. 4, Eq. 22-23), but any nonlinear function of it
(a likelihood marginalised over nuisance parameters, or a confidence-region size built from a Fisher
matrix) is not guaranteed unbiased merely because the inverse covariance feeding it is, and the paper's own
worked examples show the residual can be a non-trivial fraction (single-digit to tens of per cent) even well
inside the domain where Eq. (17) itself applies cleanly. A joint fit that marginalises over several nuisance
parameters at p = 50, n = 500 sits exactly in the class of computation Sect. 4.1 warns about, and the paper's
own recommendation is to check it "from case to case" (Sect. 6, p. 6), not assume it away.

**What the paper recommends, and its own limit.** Section 6's summary states its own operative rule, right
after a milder heuristic ("avoid to use more bins for your likelihood fit than you have realisations of your
data"): "If your errors are Gaussian and the data vectors are statistically independent, use the estimator"
Ĉ^-1 (given here in the note's own notation, since this PDF's text layer extracts the paper's hat accent
as a separate, non-combining modifier character instead of a combined glyph) "to obtain an
unbiased estimate of the inverse covariance matrix and the log-likelihood function. If one or both of these
two requirements are not fulfilled, the estimator is not guaranteed to work satisfactorily; this should be
checked from case to case." (p. 6). This is the paper's own, and only, recommendation: a debiased inverse
inside an otherwise unchanged Gaussian likelihood. It was published in 2007, nine years before `sellentin2016`
derived the alternative of marginalising over the covariance's own sampling distribution instead of debiasing
a point estimate of it. Nothing in this paper compares the two or anticipates the second option, so it cannot
be read as endorsing the Gaussian-plus-Hartlap route over a form it does not discuss. Which of the two this
record should use, and when, is answered from `sellentin2016`'s own side (see that note's "Use in this
record"): its conclusion recommends the t-distributed likelihood unconditionally over this paper's debiased
Gaussian, at the same computational cost, whenever the covariance is estimated from simulations at all.

Two further points the abstract raises and this paper's own Sect. 4-5 do not fully resolve here: a bias from
marginalising over parameters (distinct from the inverse-covariance bias itself, and separately quantified
above), and the same problem affecting "measures of the sizes of confidence regions" generally. Both
candidates are worth checking against this record's own coverage-study machinery
(`docs/methods/06_the_statistics.md` section 4.11) if an interval is found not to cover at its nominal rate.
The paper's own robustness checks (Sect. 5, bootstrap and log-normal noise) are worked examples of exactly
this kind of check, not a substitute for running one on this record's own twin replicas.
