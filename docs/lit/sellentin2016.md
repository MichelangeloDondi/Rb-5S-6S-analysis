---
citekey: sellentin2016
type: article
authors:
  - Sellentin, Elena
  - Heavens, Alan F.
title: 'Parameter inference with estimated covariance matrices'
journal: 'Monthly Notices of the Royal Astronomical Society: Letters'
volume: 456
number: 1
pages: L132-L136
year: 2015
doi: 10.1093/mnrasl/slv190
arxiv: '1511.05969'
pdf: PDF_papers/Sellentin_2016_parameter-inference-estimated-covariance-matrices.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/sellentin2016.md
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'All six pages read directly on 2026-09-22, in text and rendered page-image form: the abstract, Sect. 1
    (introduction), Sect. 2 (the Wishart/inverse-Wishart derivation of the multivariate-t likelihood, Eq.
    1-13), Sect. 3 (the Hartlap-scaled Gaussian and its own bias/scatter argument), Sect. 4 (the univariate and
    chi-squared/T-squared/H-squared comparisons, Eq. 16-20, and the MCMC-reweighting scheme), Sect. 5
    (conclusions) and the reference list.'
verified_date: 2026-09-22
summary: >
  Derives the exact likelihood for Gaussian data whose covariance is itself estimated from N simulations, by
  marginalising the true covariance out against its own inverse-Wishart distribution conditioned on the
  sample estimate. The result is a modified multivariate t-distribution (its own Eq. 12), computed at the
  same cost as the Gaussian. Its own conclusion states this is a strict improvement on Hartlap et al.'s
  debiased-inverse-covariance Gaussian likelihood, not a companion to it, and recommends adopting it
  unconditionally whenever a covariance matrix is estimated from simulations.
loci:
  - methods/06
section: method-anchors
---

# sellentin2016

Held. Read in full against the PDF, text and rendered page images both.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | MNRAS Letters **456**(1), L132-L136 (2015) | not printed on this preprint (the arXiv masthead reads "Mon. Not. R. Astron. Soc. 000, 1-6 (2015) Printed January 6, 2016", a pre-typesetting placeholder, p. 1). Volume/page/year cross-checked against the Oxford Academic listing, as before |
| DOI | 10.1093/mnrasl/slv190 | arXiv abstract-page listing |
| arXiv identifier | 1511.05969v2, 5 Jan 2016 | p. 1 header |
| affiliations | Institut für Theoretische Physik, Ruprecht-Karls-Universität Heidelberg (Sellentin), and Imperial Centre for Inference and Cosmology (ICIC), Department of Physics, Imperial College London (Heavens) | p. 1 |

## What it says, in its own terms

The abstract, verbatim in full: "When inferring parameters from a Gaussian-distributed data set by computing
a likelihood, a covariance matrix is needed that describes the data errors and their correlations. If the
covariance matrix is not known a priori, it may be estimated and thereby becomes a random object with some
intrinsic uncertainty itself. We show how to infer parameters in the presence of such an estimated covariance
matrix, by marginalising over the true covariance matrix, conditioned on its estimated value. This leads to a
likelihood function that is no longer Gaussian, but rather an adapted version of a multivariate t-distribution,
which has the same numerical complexity as the multivariate Gaussian. As expected, marginalisation over the
true covariance matrix improves inference when compared with Hartlap et al.'s method, which uses an unbiased
estimate of the inverse covariance matrix but still assumes that the likelihood is Gaussian." (p. 1, abstract,
complete).

The derivation (Sect. 2, pp. 1-3). With N simulations Xi, the unbiased sample covariance is
S = 1/(N-1) Σ_i (Xi-X̄)(Xi-X̄)^T (Eq. 3), and, writing n = N-1, S follows a Wishart distribution
W(S|Σ/n, n) (Eq. 4). Adopting the independence-Jeffreys prior π(Σ) ∝ |Σ|^-(p+1)/2 (Eq. 6, chosen because
"the determinant of the positive-definite covariance matrix is strictly positive, ... a scaling parameter",
p. 2) and applying Bayes' theorem gives an inverse-Wishart posterior for the true Σ conditioned on S (Eq. 7-8).
Marginalising the Gaussian likelihood over this posterior (Eq. 9-10) and using the matrix identity
|A+bb^T| = |A|(1+b^T A^-1 b) (Eq. 11) yields the closed form

    P(Xo|μ,S,N) = c̄_p |S|^-1/2 [1 + (Xo-μ)^T S^-1 (Xo-μ)/(N-1)]^-N/2                    (Eq. 12, p. 3)

with normalisation c̄_p = Γ(N/2) / {[π(N-1)]^(p/2) Γ[(N-p)/2]} (Eq. 13), 'requir[ing] N > p' (p. 3). The paper
names this "a cosmologist's version of a multivariate t-distribution", distinct from the standard Frequentist
multivariate-t because here one data vector fixes the peak and N simulated vectors separately fix the spread
(p. 3).

The comparison with Hartlap's method (Sect. 3, p. 3). The standard practice the paper argues against replaces
Σ^-1 → αS^-1 with α = (N-p-2)/(N-1) (Eq. 14-15, identical in form to `hartlap2007`'s Eq. 17, with this paper's
N playing the role of that paper's n), "motivated by the fact that S^-1 follows an inverse Wishart
distribution, which has a biased expectation value ⟨S^-1⟩ = α^-1 Σ^-1" (p. 3). The paper's own objection is
precise: debiasing the point estimate of the inverse covariance is not the same as accounting for its
randomness, so "αS^-1 applied to a single given S^-1 should not be interpreted as a reliable 'debiasing' but
rather a scaling that widens up the Gaussian likelihood ... in an essentially random way" (p. 3), producing a
scatter of likelihood contours illustrated in its Fig. 2. The text introducing Fig. 1 (p. 3, not the figure's
own caption, which instead names the example values N=5, p=1, α=0.5) states the resulting shape difference
directly: "the Hartlap-scaled and the unscaled Gaussian only differ in width, whereas the t-distribution has a
more sharply peaked central region but broader extreme wings than a Gaussian" (p. 3).

The quantitative comparison (Sect. 4, pp. 3-5). A univariate frequentist test (10,000 Gaussian data sets, 150
covariance estimates) shows "only the t-distribution correctly reproduces the cumulative distribution... The
Hartlap-scaled Gaussian does not capture the scatter around the peak correctly, which will lead to a
mis-estimate of the parameter errors, even on average" (Sect. 4.1, p. 4, Fig. 3). In higher dimensions, three
quadratic forms are compared: the true χ² = (Xo-μ)^T Σ^-1 (Xo-μ) (Eq. 16), T² using S^-1 in its place (Eq.
17), and the Hartlap-scaled H² = (Xo-μ)^T αS^-1 (Xo-μ) (Eq. 18). By construction ⟨H²⟩ = ⟨χ²⟩ (the scaling
does debias the mean) but "[t]he distribution of the Hartlap-scaled H² is more sharply peaked than that of
χ², thereby suggesting that the experiment has less statistical scatter than the χ²_p distribution on
average. This is impossible since the χ²_p distribution is subject to scatter of the random vector Xo only."
(Sect. 4.2, p. 4). T² instead follows an F-distribution exactly, T²(n-p+1)/(pn) ~ F_{p,n-p+1} (Eq. 19, n=N-1),
which is broader than χ²_p and converges to it only as N → ∞.

## Use in this record

Its own regime statement bears directly on a moment block: "For expensive simulations, when a feasible N is
still comparable to p, the differences between a Gaussian and the t-distribution become important." (p. 3).

**At N = 500 replicas, p = 50 coordinates: the domain condition and what it buys.** Eq. (13)'s normalisation
needs only N > p, satisfied here by a wide margin (500 vs. 50, N-p = 450). This is a weaker requirement than
`hartlap2007`'s own Eq. (17), which needs p < N-2 for its correction to stay positive at all, so at any size
where the Hartlap-scaled Gaussian is even well-defined, the t-distribution of this paper is too, at no extra
evaluation cost (Sect. 5, p. 5: "The numerical complexity will not be increased by this. It stays constant
since both distributions must evaluate the quantity (Xo-µ)^T S^-1 (Xo-µ)."). The excess degrees of freedom in
the equivalent F-distribution (Eq. 19) are n-p+1 = 499-50+1 = 450, a large excess: the t-distribution's
own departure from a Gaussian shrinks as this excess grows (Fig. 4's caption: "For N ≫ p, the T²-distribution
approximates the χ²_p-distribution"), but the paper's point in Sect. 3 is that the Hartlap-scaled Gaussian's
error is a shape error (heavy-vs-short wings, Fig. 1), not merely a width error that shrinks away at large N.
Nothing in the derivation restricts Eq. (12) to small N, and the paper never recommends switching back to a
Gaussian once N is "large enough".

**What the paper itself recommends, and when.** Its conclusions (Sect. 5, p. 5) state the choice directly and
without qualification: "An earlier proposal, by Hartlap et al. (2007), uses the unbiased estimate αS^-1 of
the inverse covariance matrix, but keeping a Gaussian likelihood. The statistical scatter of the estimator
S^-1 is not fully accounted for, and this yields posteriors that are on average simultaneously too broad in
their centres, yet not broad enough in the extremes. The principled approach is to recognise that we have a
sample of the covariance matrix S, and compute the likelihood by marginalising over the inverse-Wishart
distribution of the true covariance matrix Σ, conditioned on S. This gives a modified multivariate
t-distribution ... This is what we require for parameter inference and is the main result of this paper." And
again, as an instruction: "For parameter inference in the presence of a covariance matrix estimated from a
finite number of simulations, our results imply that MCMC chains should evaluate the modified t-distribution
Eq. (12) at each sample point, instead of a Gaussian distribution." (p. 5). No condition on N or p qualifies
this recommendation anywhere in the paper: it is offered as a strict replacement for `hartlap2007`'s
debiased Gaussian whenever a covariance is estimated from simulations at all, including at N = 500, p = 50,
where the Hartlap correction is defined and the two likelihoods would still differ in shape per
Fig. 1 even though both are well inside their respective domains.

The one practical accommodation the paper makes for an existing Gaussian-likelihood pipeline is retrospective:
Sect. 4.3 (p. 4) gives unnormalised weights G(Xo,µ,S^-1)/P(Xo,µ,S^-1,n) (Fig. 5) for reweighting an MCMC chain
that already sampled exp(-χ²/2), "provided that the chains adequately sample the parameter space that the
t-distribution favours" (p. 2): a route to correct an existing Gaussian-based run without re-running it, not
an argument for preferring the Gaussian on the merits.

Its own introduction (p. 1) names both other papers audited alongside it here as documenting the same
underlying difficulty from the other end: "the number of simulated datasets is small, with the consequence
that statistical noise in the precision matrix propagates into errors in the parameters (Taylor et al. 2013;
Dodelson & Schneider 2013; Hamimeche & Lewis 2009)": see `dodelson2013`'s own "Use in this record" for the
size of that propagated error at this record's own N and p.
