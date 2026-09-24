---
citekey: price2018
type: article
authors:
  - Price, Leah F.
  - Drovandi, Christopher C.
  - Lee, Anthony
  - Nott, David J.
title: 'Bayesian Synthetic Likelihood'
journal: Journal of Computational and Graphical Statistics
volume: 27
number: 1
pages: 1-11
year: 2018
doi: 10.1080/10618600.2017.1302882
arxiv: null
pdf: PDF_papers/Price_2018_bayesian-synthetic-likelihood.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand/audits/price2018.md  # held copy read in full 2026-09-22; determined to be the published Taylor and Francis typeset Version of Record, not a preprint
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'VERSION: this held copy is the published Taylor and Francis Version of Record (VoR), not a preprint and
    not the WRAP author-accepted manuscript flagged restricted in the 2026-09-21 audit. Evidence, read directly
    off the rendered pages: PDF page 1 is a Taylor and Francis citation/access cover sheet ("To cite this
    article...", "Accepted author version posted online: 07 Mar 2017", "Published online: 31 Jul 2017",
    Crossmark, "Citing articles: 6", full Terms and Conditions boilerplate) of the kind tandfonline.com
    auto-prepends to a downloaded reprint; page 1 of the article itself (PDF page 2) carries the full journal
    masthead "JOURNAL OF COMPUTATIONAL AND GRAPHICAL STATISTICS 2018, VOL. 27, NO. 1, 1-11" with the Taylor
    and Francis logo and a copyright line reading (c) 2018 American Statistical Association, Institute of
    Mathematical Statistics, and Interface Foundation of North America; every page carries Taylor and Francis
    running headers and logos in the final two-column typeset layout. No arXiv identifier, no arXiv header,
    footer or watermark, and no accepted-manuscript banner appears on any of the 12 pages. This goes beyond
    the 2026-09-21 stub, which checked for an arXiv preprint (none exists) and for the WRAP repository copy
    (restricted) but not for a Version of Record circulating outside WRAP. Where this particular copy came
    from is not stated by the file itself and is not something this note can determine.'
  - 'The intake filename price2017.pdf and the PDF Subject metadata ("Journal of Computational and Graphical
    Statistics, 2017. doi:...", read via pdfinfo) both track the DOI-registration / online-first date (Article
    History box, PDF page 2: "Accepted author version posted online: 07 Mar 2017", "Published online: 31 Jul
    2017"), not the final volume year; the final citation "2018, Vol. 27, No. 1" is what this note and the
    citekey use, per the firstauthor+publication-year convention this record follows.'
  - 'The byline on PDF page 2 gives only initials (L. F. Price, C. C. Drovandi, A. Lee, and D. J. Nott); the
    full given names in the authors list above (Leah F., Christopher C., David J.) are not printed anywhere in
    this PDF and are carried over from the WRAP repository page checked in the 2026-09-21 audit, not verified
    against this document. Surnames, initials and author order are confirmed directly against this PDF.'
  - 'The explicit MCMC BSL and MCMC uBSL pseudocode (Appendix B), the general psBIL framework (Appendix A),
    and Appendices C through I (the toy-example and g-and-k details, the irregular-summary-statistic example,
    and so on) are in a separate Appendices.pdf supplementary-materials file named on page 10 under
    Supplementary Materials, not part of this 12-page main-article PDF and not read; likewise Code.zip.
    Everything below is drawn from the main text only.'
  - 'The file was read in place at PDF_papers/_intake_2026-09-22/price2017.pdf (sha256
    4cb61dea863bf743557117aeef5f686c132fbac2b919162d1eab3f2ea4a9d773 per that directory''s SHA256SUMS),
    then moved on 2026-09-22, bytes unchanged, to the standard path the pdf field above names,
    matching the PDF_papers naming convention.'
verified_date: 2026-09-22
summary: >
  Casts Wood's (2010) synthetic likelihood (SL) as the auxiliary likelihood inside a Bayesian
  posterior sampled by MCMC ("BSL"), following Drovandi, Pettitt, and Lee's (2015) psBIL framework
  (pp. 2-3, Eq. 2-5); proposes a second algorithm, MCMC uBSL, built on an exactly unbiased Gaussian
  density estimator (Ghurye and Olkin 1969) that targets the Bayesian SL posterior exactly for any n
  rather than only as n -> infinity (p. 3). Across a toy Poisson-Gamma example, Wood's own Ricker
  model, and a 145-dimensional cell-biology summary statistic, finds the BSL/uBSL posterior
  "remarkably insensitive" to the simulation count n and increasingly more efficient than ABC as the
  summary-statistic dimension grows (820 vs. 67 model simulations per second in the high-dimensional
  example, p. 9). States its own limits: the multivariate-normal auxiliary assumption, no robustness
  guarantee under model misspecification, and a non-geometrically-ergodic MCMC kernel (pp. 9-10).
loci:
  - methods/06
section: method-anchors
---

# price2018

VERIFIED. Read in place at `PDF_papers/_intake_2026-09-22/price2017.pdf`, then moved on 2026-09-22,
bytes unchanged, to `PDF_papers/Price_2018_bayesian-synthetic-likelihood.pdf`, and read in full on
2026-09-22: all 12 pages (a Taylor & Francis citation/cover sheet, PDF page 1, followed
by the article's own pp. 1-11, PDF pages 2-12). Every quotation, equation, and page number below was checked
against the rendered page. Page numbers below are the article's own printed page numbers (PDF page = article
page + 1, because of the prepended cover sheet), matching how the paper itself would be cited.

## Which version this held copy is

The published Taylor & Francis **Version of Record**, not a preprint, and not the WRAP author-accepted
manuscript that the 2026-09-21 audit found and left undownloaded because WRAP marked it "Restricted or
Subscription Access."

Four independent markers on the rendered pages, none of which a preprint or an author manuscript would
carry:

1. PDF page 1 is Taylor & Francis's own citation/access cover sheet: "To cite this article: L. F. Price,
   C. C. Drovandi, A. Lee & D. J. Nott (2018) Bayesian Synthetic Likelihood, Journal of Computational and
   Graphical Statistics, 27:1, 1-11, DOI: 10.1080/10618600.2017.1302882," with "To link to this article,"
   "View supplementary material," an article-history box ("Accepted author version posted online: 07 Mar
   2017," "Published online: 31 Jul 2017"), "Article views: 1108," "View Crossmark data," "Citing articles:
   6," and the full "Terms & Conditions of access and use" boilerplate, exactly the sheet tandfonline.com
   auto-prepends to a downloaded article PDF.
2. The article's own page 1 (PDF page 2) carries the full journal masthead in the header: "JOURNAL OF
   COMPUTATIONAL AND GRAPHICAL STATISTICS" (2018, Vol. 27, No. 1, pp. 1-11,
   https://doi.org/10.1080/10618600.2017.1302882), with the Taylor & Francis roundel logo and a 'Check for
   updates' Crossmark button.
3. The same page carries the publisher copyright line at the foot, © 2018: "American Statistical Association,
   Institute of Mathematical Statistics, and Interface Foundation of North America," plus the standard
   'CONTACT' box, ORCID icons, and a note about color figures online, all Taylor & Francis production
   furniture, not something an author's own manuscript carries.
4. Every one of the 12 pages is fully typeset in the final two-column journal layout with running headers
   alternating 'L. F. PRICE ET AL.' (even pages) and the same 'JOURNAL OF COMPUTATIONAL AND GRAPHICAL
   STATISTICS' masthead title (odd pages). No arXiv identifier appears anywhere, no `arXiv:YYMM.NNNNN`
   string, no arXiv header, footer, or timestamp watermark on any page, and no *accepted manuscript* or
   *author's version* banner appears either.

(A minor, resolved wrinkle: `pdfinfo`'s Subject field reads "Journal of Computational and Graphical
Statistics, 2017. doi:...", and the file was handed over named `price2017.pdf`. Both track the online-first
/ DOI-registration date on the article-history box above, 31 Jul 2017, not the final 2018 volume
assignment. The two facts are consistent, not in tension. The citekey above uses the final citation,
2018, Vol. 27, No. 1, per this record's firstauthor+publication-year convention.)

This is a stronger finding than the "open preprint" possibility the task raised: the shelf holds the actual
publisher-typeset article, not merely an accessible manuscript version of it. The 2026-09-21 stub's search
was for an arXiv copy (none exists) and for the WRAP repository's own holding (restricted). It did not, and
had no reason to, anticipate a Version of Record turning up by some other route. Nothing in the file states
how this copy was obtained, and none is speculated here.

## What BSL is, and how it differs from Wood (2010)

Wood (2010) introduced the *synthetic likelihood* (SL): approximate an intractable summary-statistic
likelihood `p(s_y|θ)` by a multivariate normal `N(s_y; μ(θ), Σ(θ))` fitted from `n` simulated datasets, and
embed that estimate inside an MCMC scheme. But Wood's own aim with that MCMC chain was a point estimate, the
maximum-SL estimator, a classical (frequentist) procedure, not a posterior. The paper's own framing of the
gap it fills, from the end of the Introduction (p. 1):

> "Even though Wood (2010) incorporated the SL within a Markov chain Monte Carlo (MCMC) algorithm, the focus
> of Wood (2010) is to determine the maximum SL estimator, that is, a classical approach. It is trivial to
> consider a Bayesian version of this, by assigning a prior distribution on the parameter. Then the output of
> the MCMC algorithm of Wood (2010) would be a sample from an approximated probability distribution of the"
> (a 'CONTACT' sidebar block interrupts the extracted text here) "parameter conditional on the observed
> summary statistic. We refer to this approach as Bayesian synthetic
> likelihood (BSL), which is the focus of this article."

So the headline move, attach a prior and read the same MCMC output as a posterior sample instead of as a
random walk toward a maximum, is explicitly called "trivial" by the authors themselves. It is not where
they locate their contribution. What the paper actually adds, on top of that reframing:

- It places BSL formally inside the more general **parametric Bayesian indirect likelihood (psBIL)**
  framework of Drovandi, Pettitt, and Lee (2015) (p. 2: "This general framework is referred to as parametric
  Bayesian indirect likelihood (psBIL) by Drovandi, Pettitt, and Lee (2015)... though the focus of this
  article is on BSL, which is a natural and convenient choice in many applications"), and states the BSL
  target as the specific pseudo-marginal construction in Eq. (4)-(5) below, "[f]ollowing Drovandi, Pettitt,
  and Lee (2015)" (p. 3). The general Bayesian pseudo-marginal machinery is credited to that 2015 paper. This
  paper's own contribution is applying and studying it for the multivariate-normal SL case specifically.
- It derives a second, **exactly unbiased** estimator of the SL (the *uBSL* algorithm, via Ghurye and Olkin
  1969, see below), explicitly called "the novel MCMC uBSL algorithm" (p. 3).
- It runs a systematic empirical study, the paper's largest single component, of BSL/uBSL's sensitivity to
  the tuning parameter `n` and their computational efficiency against ABC, across three examples of
  increasing summary-statistic dimension (Section 4, pp. 5-9, detailed below).

## The formal construction

The BSL auxiliary-likelihood estimate (p. 2, Eq. 2):

> `p_{A,n}(s_y|θ) = N(s_y; μ_n(θ), Σ_n(θ))`

with the plug-in moment estimators from `n` simulated summary-statistic replicates `s_1,...,s_n ~ p(·|θ)`
(p. 3, Eq. 3):

> `μ_n(θ) = (1/n) Σ_{i=1}^n s_i`,
> `Σ_n(θ) = (1/(n-1)) Σ_{i=1}^n (s_i - μ_n(θ))(s_i - μ_n(θ))ᵀ`.

Combined with a prior `p(θ)`, following Drovandi, Pettitt, and Lee (2015), BSL samples from (p. 3, Eq. 4-5):

> `p_{A,n}(θ|s_y) ∝ p_{A,n}(s_y|θ) p(θ)`, where
> `p_{A,n}(θ|s_y) = ∫_{S^n} N(s_y; μ_n(θ), Σ_n(θ)) ∏_{i=1}^n p(s_i|θ) ds_{1:n}`.

A single draw of `s_{1:n}` gives an unbiased estimate of `N(s_y; μ_n(θ), Σ_n(θ))`, which under Andrieu and
Roberts (2009) makes plugging that stochastic estimate into MCMC a valid pseudo-marginal algorithm targeting
`p_{A,n}(θ|s_y)` exactly, for *any* finite `n`, even though `p_{A,n}(θ|s_y)` itself is not the "ideal" BSL
target `p_A(θ|s_y) ∝ N(s_y; μ(θ), Σ(θ))p(θ)` except in the `n → ∞` limit (p. 3, citing Drovandi, Pettitt, and
Lee 2015 for that limiting result).

The second algorithm, **uBSL**, replaces the plug-in normal density with an exactly unbiased estimator of a
multivariate normal density due to Ghurye and Olkin (1969, sec. 3.4), valid whenever the summary statistic is
genuinely multivariate normal and `n > d + 3` (`d` = summary-statistic dimension) (p. 3):

> `p̂_A(s_y|θ) = (2π)^{-d/2} [c(d,n-2) / (c(d,n-1)(1-1/n)^{d/2})] |M_n(θ)|^{-(n-d-2)/2} ψ(M_n(θ) -
> (s_y-μ_n(θ))(s_y-μ_n(θ))ᵀ/(1-1/n))^{(n-d-3)/2}`,

with `M_n(θ) = (n-1)Σ_n(θ)`, `ψ(A) = |A|` for `A` positive definite and `0` otherwise, and `c(k,v) =
2^{-kv/2}π^{-k(k-1)/4} / ∏_{i=1}^k Γ(½(v-i+1))`. "The estimated likelihood," `p̂_A(s_y|θ)` "replaces"
`N(s_y;μ_n(θ),Σ_n(θ))` "in MCMC BSL to create the novel MCMC uBSL algorithm. We stress that this algorithm
targets" `p_A(θ|s_y)` (not `p(θ|s_y)`) "under the multivariate normality assumption of the summary statistic"
(p. 3).

## The algorithm

Both are MCMC schemes (not importance sampling): "We use an MCMC algorithm with" `T` "iterations to sample
from" `p_{A,n}(θ|s_y)` ", which is shown in Appendix B of the supplementary materials. The approach is similar
to a standard MCMC algorithm but includes, at each iteration, a simulation step to obtain" `μ_n(θ)` "and"
`Σ_n(θ)` "of the SL. Wood (2010) adopted the same approach but uses the output to maximize the SL, rather than
using the samples to construct a posterior distribution. We refer to this algorithm as MCMC BSL" (p. 3).
**The explicit pseudocode itself is in Appendix B of the online supplementary materials, not in this held
PDF**: see the verify_flags entry on the appendices.

MCMC BSL is likened to the grouped-independence Metropolis–Hastings (GIMH) pseudo-marginal algorithm of
Beaumont (2003) / Andrieu and Roberts (2009): the stochastic likelihood estimate is not re-drawn at every
iteration but carried over with the current `θ` (p. 3, Section 2.2 "Choice of n").

**Guidance for choosing `n`**, borrowed from the pseudo-marginal literature (pp. 3-4): "Borrowing the
theoretical" (a page-header interrupts the extracted text here) "result for the GIMH method outlined in
Doucet et al. (2015), the value of" `n` "should be chosen such that the log SL at some" `θ` "with high BSL
posterior support should be estimated with a standard deviation of roughly 1." Table 1 (p. 5) reports this
directly for the toy example at the true parameter: sd
of log SL falls from "large" at `n=2` to 5 at `n=5`, 0.8 at `n=10`, 0.4 at `n=20`, illustrating that the
`sd≈1` heuristic sits around `n=6-7` there.

For uBSL this guidance breaks down: "the random variable describing the uSL is a mixture of a discrete and a
continuous random variable; it may be identically 0 if the argument of" `ψ(·)` "is not positive definite,
implying that the log uSL is" `-∞` "in such cases. Hence, the standard deviation of the log uSL is infinite
generally, meaning that we cannot consider the guidance of Doucet et al. (2015)" (p. 4).

## The worked examples (Section 4, pp. 5-9)

Three examples of increasing summary-statistic dimension `d`, each comparing BSL/uBSL against ABC:

- **Toy example, `d=1`** (Poisson data, gamma prior, sample mean as the sufficient summary statistic,
  Section 4.1, pp. 5-6): the true posterior is available analytically for comparison. On efficiency, ABC
  wins here: "the normalized ESS for ABC is 25, indicating that ABC is more efficient than BSL and uBSL for
  this one parameter and summary statistic example" (p. 5), matching the paper's own theoretical crossover
  claim in Section 3 (p. 4): for this toy setup "an ABC rejection sampler is more computationally efficient
  when `d = 1`, equally computationally efficient when `d = 2`, and becomes significantly less efficient as
  `d` increases beyond 2." On robustness to non-normality, the same toy model is re-run at `N=10, λ=1` (built
  to violate the normality assumption) against `N=100, λ=30` (where it holds), checked with an
  Anderson–Darling test: "[t]he BSL approaches appear to have very accurate estimates of the posterior
  distribution in both cases, which is remarkable given the strong departure from normality when λ=1"
  (Section 4.1.3, p. 6).
- **Ricker model, `d=13`** (Wood's 2010 own ecological population model, Section 4.2, pp. 6-7): 13
  non-Gaussian summary statistics (the mean observation, the zero count, lag-0-5 autocovariances, two
  autoregression coefficients, and cubic-regression coefficients of the ordered differences, following
  Wood 2010's own choice, "This constitutes a total of 13 summary statistics," p. 6-7). An Anderson–Darling
  test confirms non-normality component by component, though "it does not appear that the distributions of
  the summary statistics are highly irregular for `θ` with high posterior support" (p. 7). Sensitivity to
  `n`: "the BSL target distributions are again remarkably insensitive to `n`, given the lack of normality of
  the summary statistic," with an optimal `n≈50` (normalized ESS 30/35/45 for the three parameters) and a
  useful range of 30-100 (p. 7). Comparison to ABC: despite the non-normality, "the BSL approaches produce
  an approximate posterior in the vicinity of the ABC approximation despite the mild departure from normality
  of the summary statistics" (p. 7), though "[t]here is some discrepancy between the (u)BSL and ABC
  posteriors for `σ_e`" (p. 7).
- **Cell-biology / scratch-assay model, `d=145`** (Johnston et al. 2014's collective cell-spreading model,
  Section 4.3, pp. 7-9): a 145-dimensional summary statistic (144 Hamming-distance-based motility terms plus
  a final cell count). Headline efficiency result: "ABC performs on average 67 model simulations per second,
  whereas BSL is able to produce 820 model simulations per second" (p. 9), and "[i]n the cell biology
  application, we found an order of magnitude improvement to the computing time when using a computer node
  with 16 cores" (p. 9), BSL's larger optimal `n` (found to be `n=5000` here, p. 8) lets it exploit
  embarrassingly parallel simulation across cores far more effectively than ABC's serial rejection loop.

Across all three: "It is again remarkable how insensitive the (u)BSL posteriors are to `n`, given the
high-dimensional summary statistic" (p. 8), and in the Discussion: "even though uBSL has an estimated log SL
with infinite variance, in practice it gives an efficiency that appears similar to BSL" (p. 9).

## What the authors say BSL cannot yet do

Stated directly in Section 5, Discussion (pp. 9-10):

- **The normality assumption is the acknowledged weak point**: "Overall the BSL approaches appear to be
  useful methods for approximating `p(θ|s_y)`. The method requires less tuning than ABC, is more
  computationally efficient than ABC in challenging scenarios, shows some robustness to the normality
  assumption, and is embarrassingly parallelizable. **The clear drawback of the method is the normality
  assumption**, which will be increasingly violated with an increasing dimension of the summary statistic"
  (p. 10).
- **No robustness guarantee under model misspecification**: "when the model is unable to recover the
  observed statistic, `s_y`... a larger value of `n` is required to achieve a reasonable acceptance
  probability in MCMC (u)BSL and... the BSL methods are not necessarily robust to such misspecifications. The
  reason for the poor efficiency is that `s_y` is always in the tails of the SL and is thus harder to
  estimate" (p. 10).
- **No convergence guarantee for the chain actually used**: Lee and Łatuszyński (2014) "showed that the ABC
  MCMC kernel that we use in this article is not geometrically ergodic" (p. 10). Chains initialized away from
  the posterior support "can become stuck there for long periods."
- On a genuinely irregular summary statistic (their Appendix I, not held here), the authors say plainly "the
  output of BSL cannot be trusted, while ABC represents a robust alternative in such cases" (p. 9).

## Use in this record

`frazier2023` (already on this shelf, held) independently corroborates this paper's place in the field: Price
et al. (2018) were the first to consider in detail its [Wood 2010's synthetic likelihood] use for Bayesian
inference (frazier2023, p. 4), that is frazier2023's retrospective framing of price2018, not a claim
price2018 makes about itself. Nothing in this paper's own text claims priority. Having now read the paper
directly instead of only frazier2023's abstract-level description, that characterization holds up: the
paper's actual content, the BSL/uBSL constructions above, and the systematic study of `n`-sensitivity and
ABC-efficiency across three examples, is squarely about Bayesian inference within the SL framework, which is
exactly the sense in which this record cites it as **the standard reference for Bayesian inference inside a
synthetic-likelihood framework**, relevant wherever this record's own statistics (Section 06,
`docs/methods/06_the_statistics.md`) treats the windowed-moment / joint-likelihood construction in Bayesian
terms, not purely frequentist ones.

Separately, and kept explicitly separate as this record's own observation and not a claim about this
paper's content: this record's stated plan pins some parameters from theory and frees others later (a
delta-function-or-tight-prior-then-relaxed move). Having now read the full text, price2018 contains **no**
discussion of staged parameter pinning, degenerate/tight-then-broadened priors, or anything resembling a
pin-then-free mechanic: its `n` is a *computational* tuning parameter (the number of simulated replicates
used to build the auxiliary Gaussian, Eq. 3), not a physical or statistical parameter being progressively
freed, and none of the three worked examples stage a prior in that way. The generic apparatus this paper
supplies, a prior `p(θ)` combined with a synthetic-likelihood auxiliary model via MCMC, Eq. (4)-(5), is a
natural place to *mount* such a pin-then-free strategy (e.g., a near-degenerate prior on a theory-pinned
nuisance parameter such as Δα or β_self, later relaxed to an informative or flat prior), but that specific
move remains this record's own construction to make, not something price2018 states, examples, or
anticipates.
