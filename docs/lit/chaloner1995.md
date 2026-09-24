---
citekey: chaloner1995
type: article
authors:
  - Chaloner, Kathryn
  - Verdinelli, Isabella
title: 'Bayesian Experimental Design: A Review'
journal: Statistical Science
volume: 10
number: 3
pages: 273-304
year: 1995
doi: null
arxiv: null
pdf: PDF_papers/Chaloner-Verdinelli_1995_bayesian-experimental-design-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand/audits/chaloner1995.md  # claim-by-claim against the held PDF, 2026-09-22: fixed a quote's page citation (pp. 287-288, not 288 alone) and removed one uncounted reference-list estimate; the Example 2 two-prior mixup was caught and fixed before first publication of this note; no other defect
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'Full 33-page held PDF read directly, in full, via rendered page images on 2026-09-22 (all nine sections,
    the acknowledgments and the reference list, pp. 273-304). This is a JSTOR page-image scan with no separate
    machine-readable text layer exposed to this note, so every quotation, equation and number below was read
    off the rendered page image directly -- checked against the rendered page throughout, not against
    extracted or OCR text. No JSTOR cover sheet precedes the article: PDF page 1 is printed page 273 directly.
    PDF page 33, the last, is an unnumbered, higher-resolution duplicate scan of Figure 1, which already
    appears, numbered, as printed page 285; the review''s own content is the 32 printed pages 273-304.'
  - 'No DOI is printed anywhere on any of the 33 pages, consistent with a 1995 Statistical Science article of
    that era. Left null rather than filled from a remembered or guessed value, per this task''s own
    instruction not to guess a JSTOR-style DOI''s trailing digits from memory.'
  - 'Depth of read is uneven by design and is stated here rather than left implicit. The decision-theoretic
    framework and taxonomy (Sections 1.3, 2.2-2.4, 4, 5.1-5.6, 9) got a close, quote-checked read. The three
    running worked examples (Sections 1.2, 3.3/3.5, 6.2, 6.4) were read for their own stated numbers and
    conclusions but not independently re-derived. The long one-paragraph-per-citation literature surveys
    inside Sections 2.3, 3.4, 6.1, 6.3, 6.5-6.9, 7 and 8 were read for what this review itself credits to each
    cited work, at the level the review states it, not against any of the many underlying cited papers filling
    the reference list (pp. 299-304), none of which are held in this record and none independently counted for
    this note.'
  - 'Read in place at PDF_papers/_intake_2026-09-22/chaloner1995.pdf, then moved on 2026-09-22, bytes
    unchanged (its sha256 matches that folder''s SHA256SUMS line), to the standard filename the pdf field above
    names. The name follows this repository''s two-author convention of hyphenating both surnames (cf.
    PDF_papers/Arora-Sahoo_2012_..., PDF_papers/Camparo-Klimcak_1992_...), chosen over the intake''s own
    single-surname suggestion after checking the holdings directory.'
  - 'docs/lit/rainforth2023.md stood in for this review from 2026-09-21, when no freely downloadable copy of
    it had been found. Once this copy was held and read, on 2026-09-22, that note was reframed as the
    complementary review of recent computational advances, and the generated LITERATURE_INDEX.md and
    references.bib were rebuilt from both notes.'
verified_date: 2026-09-22
summary: >
  The classic decision-theoretic review of Bayesian experimental design: a design maximizes expected utility
  (eq. 1-2, p. 275) under a prior over the parameters, which recovers Bayesian D-, A-, c-, E- and G-optimality
  as special cases of different utility functions (Sec. 2.2-2.4, pp. 277-281) and extends to nonlinear models
  through approximations to the expected Fisher information (Sec. 4-5, pp. 284-291). Section 5.5 (pp. 290-291)
  argues sequential design should in principle gain over a fixed design for nonlinear problems, then lists,
  from a real worked example, exactly the practical objections -- prolonged duration, drifting conditions,
  compounding calculation error -- that favour batch-sequential procedures instead. Held and read in full as
  of 2026-09-22, with rainforth2023, its stand-in until then, kept as the complementary review of recent
  computational advances.
loci:
  - methods/06
section: method-anchors
---

# chaloner1995

VERIFIED. Held (`PDF_papers/Chaloner-Verdinelli_1995_bayesian-experimental-design-review.pdf`, 33 pages).
Read in full, directly, on 2026-09-22, title through references, pp. 273-304, via the rendered page images
(see `verify_flags` for which sections got a close read versus an orientation-level pass).

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | *Statistical Science* **10**(3), 273-304 (1995) | p. 273, masthead |
| authors and affiliations | Kathryn Chaloner, Associate Professor, School of Statistics, University of Minnesota, St. Paul; Isabella Verdinelli, Associate Professor, Dipartimento di Statistica, Probabilità e Statistiche Applicate, Università di Roma `La Sapienza`, and Visiting Associate Professor, Department of Statistics, Carnegie Mellon University | p. 273, footnote |
| key words and phrases | Decision theory, hierarchical linear models, logistic regression, nonlinear models, optimal design, optimality criteria, utility functions | p. 273 |
| held-PDF page count | 33 (32 printed pages, 273-304, plus one unnumbered duplicate scan of Figure 1) | p. 285 (Fig. 1, numbered) vs. the unnumbered last page |
| DOI | not printed anywhere in the held scan | n/a |

This scan carries no extractable text layer (`verify_flags`), so the paper's own wording below is
given without quotation marks throughout, checked word for word against the rendered page
images, not against any text layer. The abstract (p. 273), in that sense verbatim: This paper
reviews the literature on Bayesian experimental design. A unified
view of this topic is presented, based on a decision-theoretic approach. This framework casts criteria from
the Bayesian literature of design as part of a single coherent approach. The decision-theoretic structure
incorporates both linear and nonlinear design problems and it suggests possible new directions to the
experimental design problem, motivated by the use of new utility functions. We show that, in some special
cases of linear design problems, Bayesian solutions change in a sensible way when the prior distribution and
the utility function are modified to allow for the specific structure of the experiment. The decision-theoretic
approach also gives a mathematical justification for selecting the appropriate optimality criterion.

## What it says, in its own terms

### The decision-theoretic framework (Sections 1.3, 2.2-2.4, pp. 275-281)

Following Lindley (1972, pp. 19-20), a design $\eta$ is chosen from a set $\mathscr{N}$, data $\mathbf{y}$ are
observed from a sample space $\mathscr{Y}$, and a decision $d$ (the choice of $\eta$, then a terminal decision)
is made from a set $\mathscr{D}$. The unknown parameters $\theta$ live in $\Theta$. The expected utility of the
best decision (eq. 1 below, transcribed and checked against the rendered page, p. 275) is

$$U(\eta) = \int_{\mathscr{Y}} \max_{d \in \mathscr{D}} \int_{\Theta} U(d,\theta,\eta,\mathbf{y}) p(\theta|\mathbf{y},\eta) p(\mathbf{y}|\eta) d\theta d\mathbf{y},$$

and the Bayesian design $\eta^*$ maximizes this over $\eta \in \mathscr{N}$ (eq. 2, p. 275). In the paper's own
words (p. 275): Lindley's
argument suggests that a good way to design experiments is to specify a utility function reflecting the purpose
of the experiment, to regard the design choice as a decision problem and to select a design that maximizes the
expected utility.

Different choices of $U$ recover different named criteria, all pp. 277-278. The expected gain in Shannon
information / Kullback-Leibler distance between posterior and prior (eq. 3-4, p. 277) gives, for the normal
linear model, $\phi_1(\eta) = \det\lbrace nM(\eta)+R\rbrace$, known as Bayes $D$-optimality (p. 277). A quadratic loss
utility (eq. 7, p. 278) gives Bayes $A$-optimality, $\phi_2(\eta) = -\mathrm{tr}\lbrace A(nM(\eta)+R)^{-1}\rbrace$, whose
rank-one special case is Bayes $c$-optimality. A minimax argument over linear combinations gives Bayesian
$E$-optimality (eq. 8, p. 278), flagged by the review itself as not cleanly utility-derived, in its own words:
this criterion
appears not to correspond to any utility function and so, although it is referred to as Bayesian $E$-optimality,
its Bayesian justification, in a decision-theoretic context, is unclear (p. 278). And Bayesian $G$-optimality
minimizes the maximum predictive variance over the design region (p. 278). Section 2.4 (pp. 280-281) adds
predictive utilities: expected Shannon information on a future observation $y_{n+1}$ (eq. 9, p. 280), and two
combined inference-plus-prediction utilities (eq. 10 after Verdinelli and Kadane 1992, eq. 11 after Verdinelli 1992), both
p. 280.

A structural point the review makes explicitly, and one that bears directly on whether any of this transfers to
a data-starved regime, in the paper's own words (p. 279): any differences between a Bayesian design and its corresponding non-Bayesian
one are unimportant if $n$ is large; when a noninformative prior distribution is used for inference, as may
often be the case, there is no advantage to using the Bayesian approach for design. But, immediately after:
this limiting behavior is not seen in design for nonlinear models where usual non-Bayesian optimal designs are
again special cases of Bayesian design but correspond to a point mass prior distribution rather than
noninformativeness (p. 279).

### Nonlinear design and local optimality (Sections 4-5.4, pp. 284-290)

For a nonlinear model the exact expected utility of Section 2 is generally intractable, so Section 4 builds
normal approximations to the posterior (eq. 12-13, p. 286) and derives approximate criteria referred to as
Bayesian $D$-optimality, Bayesian $c$-optimality and Bayesian $A$-optimality (p. 286, eq. 15, 18, 20), each an
integral of a local criterion over the prior $p(\theta)$, e.g.
$\phi_1(\eta) = \int \log\det\lbrace n\mathscr{I}(\theta,\eta)\rbrace p(\theta) d\theta$ (eq. 15, p. 286), with
$\mathscr{I}(\theta,\eta)$ the expected Fisher information: in the paper's own words, the matrix of moments $M$, used in the previous
sections on linear design, is a very special case of $\mathscr{I}(\theta,\eta)$, where $\mathscr{I}(\theta,\eta)$
does not depend on $\theta$ (p. 284). Section 4.6's own verdict (p. 288), paraphrased: apart from the ideal approach of
maximizing the exact expected utility, as in the paper's Eq. (1), no single approach is the
definitive Bayesian nonlinear design criterion. The criteria derived in this section are all approximations
to the ideal.

Section 4.4 (pp. 287-288) singles out **local optimality**: approximating the marginal distribution of the
MLE $\hat\theta$ by a one-point mass at a best guess $\theta_0$ (Chernoff 1953, 1962), giving e.g. local
$D$-optimality $\phi_{1\theta_0}(\eta) = \det\lbrace\mathscr{I}(\theta_0,\eta)\rbrace$ (eq. 25, p. 288). The review is
explicit that this is a weak substitute for the full Bayesian criterion, not a synonym for it. The sentence
spans the page break, checked against both rendered pages, in its own words (pp. 287-288): as local optimality is a very crude
approximation to expected utility, it can be considered as being approximately Bayesian, although it is
typically not [p. 288 begins here] justified in this way and is usually used in a non-Bayesian framework.
It also notes the asymmetry a non-Bayesian use of local optimality accepts and a Bayesian one does not, in its own words (p.
288): such criteria are appealing in a non-Bayesian framework where it is accepted that prior information must
be used in design, but should not be used in the analysis.

Section 5.2 (pp. 289-290) draws a genuine linear/nonlinear distinction with a design-checking consequence:
unlike linear $D$-optimal designs, whose support-point count is bounded by the parameter count, for nonlinear
models there is no such bound available on the number of support points (p. 289). And, in its own words: for more dispersed
prior distributions, there are more support points. This is a useful feature for a design because if there are
more support points than unknown parameters, the model assumptions can be checked with data from the
experiment (p. 289).

### Sequential design (Section 5.5, pp. 290-291)

This is the section closest to the task's own framing. Its opening argument, in its own words (p. 290): In any design
problem an optimal sequential design procedure must be at least as good as a fixed design procedure. In most
linear design problems, however, both Bayesian and non-Bayesian, the optimal sequential procedure is the fixed,
nonsequential procedure. There is nothing to be gained by designing sequentially. For nonlinear problems the
posterior utility clearly depends on the data $\mathbf{y}$, or a function of $\mathbf{y}$ such as $\hat\theta$,
and there should be a gain from choosing design points sequentially.

The review immediately qualifies this with a real example (the University of Minnesota drug-potency trials,
introduced as Example 2, p. 274), in its own words (p. 290, continuing p. 291): Sequential design, however, may be
unrealistic in practice. Theoretically the dose for each one of the 60 animals could be decided upon one at
a time; however, in practice the following problems arise: 1. Because death over the seven days following
injection of the drug is the response, the experiment would be prolonged from a total of seven days to many
months. 2. Time trends or seasonal effects may be introduced if the experimental conditions change over time.
Similar animals might not always be available and the drugs deteriorate over time. 3. The probability of error
in doses and calculations is increased when 60 calculations are done to determine the next dose. A nonsequential
procedure is easily implemented and requires less training of laboratory staff. It closes by naming
batch-sequential design (citing Zacks 1977 and Ridout 1995) as a practical middle ground, with its own caveat,
in its own words (p. 291): there is a practical concern, however, that the experimental conditions from one batch to the next
might be different.

### The worked examples, and their own moral (Sections 1.2, 3.3/3.5, 6.2, 6.4)

Three running examples carry the paper: a one-way ANOVA / dose-response design (Example 1, p. 274, continued
§3.3/3.5, pp. 282-284), the University of Minnesota logistic-regression LD50 drug-potency trials just quoted
above (Example 2, p. 274, continued §6.2, pp. 291-292), and an 18-point pharmacokinetic blood-sampling design
for a three-parameter compartmental model, from Atkinson, Chaloner, Juritz and Herzberg (1993) (Example 3, pp.
274-275, continued §6.4, pp. 292-293).

Example 2's continuation (§6.2, pp. 291-292) is worth reading carefully instead of summarizing to one number,
because it uses **two different priors and gets two different verdicts**. The 54 past experiments' own LD50
estimates first build an informative Beta(4,4) prior matched to their sample moments (p. 291-292). Under that
prior, the six-dose design the lab actually used has a $\phi_2$-criterion value 1.52 times that of the
$\phi_2$-optimal design (p. 292), improvable to 1.29 times by dropping its highest dose and to 1.13 times
by dropping both extreme doses, and the paper's own reading is that they could have reduced the variability of
their estimates considerably (p. 292) had they used the Bayesian-optimal four-point design instead. A second,
more diffuse prior, uniform over the same interval, meant to represent what might have represented beliefs
before the experiments were done (p. 292), gives a different answer for the *same* six-dose design: only
1.13 times the optimum (p. 292), and it is *this* comparison the paper's headline verdict is actually about,
in its own words: this example has, therefore, not illustrated that Bayesian design could have greatly improved efficiency of
estimation in this laboratory, but rather that what they were doing may well have been close to being optimal
in a Bayesian sense (p. 292). The two readings are not in tension. They are two different priors, and which one
is the fair standard to judge the lab's design against is left unsettled by the paper.

Example 3's continuation (§6.4, p. 293) is more uniformly favourable to the design used: the 18-point blood-
sampling design's efficiency ratio against the Bayesian optimum is 1.3 for $t_{\max}$ and 1.4 for $c_{\max}$,
but 3.2 for the area under the curve (p. 293), so, close to its own words, the 18-point design is not
as efficient for estimating
the AUC as it is for $t_{\max}$ and $c_{\max}$ (pp. 293-294). Near-optimality here is criterion-dependent,
not blanket.

### Concluding remarks (Section 9, pp. 298-299)

In its own words (p. 298): Bayesian design is an exciting and fast-developing area of research. The Bayesian
methodology has much to offer in experimental design, where prior information has always been used for the
choice of experiment, explanatory factors, sample size and model. A Bayesian approach to design gives a
mechanism for formally incorporating such information into the design process. And, immediately after,
unsoftened: it does remain regrettable, however, that so few real case studies appear in the statistical
literature of Bayesian optimal design. The same can be said of non-Bayesian nonlinear design where there is
considerable theoretical research but few real case studies (p. 298).

## Use in this record

The task's own framing is "Chaloner and Verdinelli for design." Read in full, the paper substantiates that
framing in one precise sense and one limited sense, and the two should not be blurred.

**What transfers cleanly: the vocabulary, and one structural parallel.** This record's own philosophy,
ordering the computations so the early ones license skipping the later ones, and the
identifiability page's own language of a knob that breaks a degeneracy, priced at a committed cell
before it is trusted as a forecast
(`private/thesis_mirror/identifiability_degeneracies_knobs_uncertainties_2026-09-16.md`, its Breaking a
degeneracy by design and The knobs of a new campaign sections), is, in this paper's own taxonomy, closest
to **local optimality** (§4.4, pp. 287-288): a criterion evaluated at one committed best guess point, not
averaged over a prior. The paper is explicit, in its own words, that this is a very crude approximation to expected utility
and typically used in a non-Bayesian framework (pp. 287-288, the sentence spans the page break), which is
an accurate description of this record's own current practice, not a criticism specific to it. The place the
paper's own material lines up most
closely with this record's actual situation is Example 2's origin story, close to its own words (p. 274): fifty-four past experiments
were used to build a prior distribution for designing future ones: the 54 estimates of LD50 can be thought of
as a sample from a distribution of possible values, and the paper considers a prior distribution for the
LD50 that reasonably reflects the observed sample (p. 274). That is structurally this record's own situation,
the 2025 archive as the information a next vapour-cell campaign's design would be built from, more closely
than anything else in the paper, and Section 6.2's two-prior exercise (pp. 291-292, above) is a template for how
such a design question would actually be scored: as an efficiency ratio against a fixed protocol, and the
answer depends on how sharp a prior the archive is allowed to supply.

**What does not transfer without a step this record has deliberately not taken.** Every criterion in Sections
2-5, $D$-, $A$-, $c$-, $E$-, $G$-optimality and the predictive utilities alike, is an integral over an
explicit prior $p(\theta)$ (eq. 1, 4, 7, 9-11, 15, 18, 20) or, in the crude local case, a single committed point
(eq. 25). This record's own methods note gives a stated reason for not doing the equivalent for its own
dominant open parameter: a posterior needs a prior on $w_0$, and marginalizing folds that prior invisibly into
the quoted number, so keeping $w_0$ out of the likelihood and quoting an explicit $w_0$-band keeps the
conditionality on the page (`docs/methods/06_the_statistics.md` §4.12, point 2). The same section states the
record's general position on Bayesian machinery plainly: Bayesian machinery is used where it is the right
tool, model selection, as the BIC ladder of §4.9 (§4.12), i.e. a Bayesian criterion (BIC, an asymptotic
approximation to the log Bayes factor) is already in use, but for model choice, not for design, and the
record's headline results are profile-likelihood bounds calibrated by injection-recovery (frequentist
coverage), not posterior summaries. Page 279's own remark, that the Bayesian/non-Bayesian design distinction
washes out for large $n$, diffuse-prior linear problems but persists for nonlinear ones, says, in the paper's
own terms, that this shortfall does not wash out here: this record's regime is nonlinear and frequently
data-poor in the same sense the paper's own small-sample cases are (this record's own words, four densities
and two residual degrees of freedom, `docs/methods/06_the_statistics.md` §4.12, point 3), so a literal
Chaloner-Verdinelli criterion, if computed, would not obviously collapse onto whatever answer this record's
local, single-point knob-table already gives.

The review's own p. 274 origin story for Example 2 (fifty-four past experiments built into a prior for
designing future ones, quoted above) is itself an argument for why this gap is worth closing instead of
leaving as a permanent difference in kind: it is exactly the situation this record is already in, an existing
archive informing the design of a next campaign.

**What formalizing it would actually require**, stated as an open path, not a claim already acted on:
(1) a prior over the physical parameters the twin simulates at ($w_0$, $\sigma_L$, density, ...), which this
record has deliberately withheld for $w_0$ specifically, for the reason quoted above. (2) A tractable or
normal-approximated posterior at each candidate condition, which the twin does not currently supply (it
supplies simulated data and a likelihood evaluated against it, not a posterior integral). And (3) a utility
matched to what the record actually wants from a next campaign, most plausibly the nonlinear Bayesian
$A$-optimality of eq. (18)/(20), p. 286, summed or weighted across the several physical quantities of interest
(the moments and their ratios the main aim names), since the record's own stated goal is precision on several
named combinations at once, not one scalar. None of this is derived or attempted here. It is named as the
concrete next step the paper's own apparatus would require, distinct from and additional to the record's
current coarse-to-fine heuristic, which is not claimed here to already be a Bayesian design in disguise.

**Relation to `rainforth2023` (already held).** `docs/lit/rainforth2023.md` was adopted, on 2026-09-21, as a
held substitute for exactly this citation, in the same method-anchors cluster and at the same
`loci: [methods/06]`, because a freely downloadable copy of Chaloner and Verdinelli (1995) had not yet been
found. That 2023 review covers recent advances (gradient-based and amortized computation) in the same
decision-theoretic BED framework this paper originates. The original framework is now supplied directly,
read in full, instead of through rainforth2023's partially-read secondary coverage of it. The two
are complementary and neither substitutes for the other: the classical taxonomy and the
sequential-design discussion above are read directly from Chaloner and Verdinelli, while rainforth2023
(VERIFIED only for page 1 and Sections 3.4.1 and 4, and not further read here) would be the place to look
for whether the recent advances it names have addressed the computational obstacle this record's own
hand-pricing already works around. The rainforth2023 note was rewritten on 2026-09-22 to describe the two
the same way.

## Not yet read

The technical machinery beyond what is reported above is not independently re-derived here: the ANOVA algebra of
Section 3 (its square-root rule, the hierarchical-prior formulas, pp. 282-284), the dense one-paragraph
citation pointers filling Sections 2.3, 3.4, 6.1, 6.3, 6.5-6.9, 7 and 8 (read for what this review credits to
each, not checked against any of those other papers, none held here, nor independently counted here),
and the algebraic detail of the turning-point singularity example in Section 7 (pp. 295-296) beyond its stated
moral (a locally optimal
design can make the quantity of interest inestimable). None of this is drawn on in the section above.
