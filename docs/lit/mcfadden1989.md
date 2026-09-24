---
citekey: mcfadden1989
type: article
authors:
  - McFadden, Daniel
title: 'A Method of Simulated Moments for Estimation of Discrete Response Models Without Numerical Integration'
journal: Econometrica
volume: 57
number: 5
pages: 995-1026
year: 1989
doi: 10.2307/1913621
arxiv: null
pdf: PDF_papers/McFadden_1989_simulated-method-of-moments-discrete-response.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand/audits/mcfadden1989.md  # all 33 pages read as rendered page images, 2026-09-22; three corrections (a quotation misattributed to a footnote instead of the main text; a mis-pathed internal cross-reference; a two-sentence quote spliced with an editorial "[or]"), all fixed below; no defect found that a downgrade from VERIFIED would follow from
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'All 33 pages of the held PDF (the JSTOR cover sheet plus the full published text, Econometrica 57(5), pp. 995-1026)
    were read directly as rendered page images on 2026-09-22, not by text extraction: Sections 1-8 in full
    (Introduction; Definitions and Notation; the formal MSM construction and the efficiency-versus-draws result;
    Computational Issues and Statistical Efficiency; the three application sections on panel data, measurement error,
    and nonnormal response models; and Section 8''s Theorem 1 with Lemmas 1-10 and Assumptions A1-A13), the closing
    affiliation line, and the full reference list. Four pages (pp. 995, 998, 1004, 1006 -- the introduction, the MSM
    definition, the instrument-construction discussion, and the efficiency formula) were re-read individually at full
    resolution to fix every quoted formula and sentence against the image a second time before this note was written.'
  - 'The formal statements -- the MSM definition (Eq. 7, p. 998), the two simulator restrictions A10-A11 (p. 999,
    formalized pp. 1013-1014), Theorem 1 (p. 1014), and the efficiency formula (p. 1006) -- were read closely and are
    the basis of every claim below. Lemmas 2-10 (pp. 1012-1025), which supply the measure-theoretic and
    empirical-process machinery proving specific simulators satisfy A3-A5 and A10-A13, were read for their statements
    and role in the argument, not re-derived step by step: their own algebra (Bernstein''s-inequality chaining,
    pp. 1017-1018; the metric-entropy bracketing argument citing Dudley 1984 and Alexander 1987, p. 1021; the
    spherical-transformation cylinder-function construction, pp. 1002-1003) got a lighter pass than the main text and
    Theorem 1''s own proof (pp. 1014-1016).'
  - 'DOI: no field labelled "DOI" is printed anywhere in the held PDF. The cover sheet prints a JSTOR "Stable URL:
    http://www.jstor.org/stable/1913621"; doi: 10.2307/1913621 is that same digit string transcribed from the image
    under JSTOR''s standard, Crossref-registered 10.2307/<stable-id> prefix, not a number recalled from memory. The
    same value is independently given in this repository''s own
    private/cache/lit_intake_2026-09-21/OWNER_DOWNLOADS_MERGED.md.'
verified_date: 2026-09-22
summary: >
  Defines the method of simulated moments (MSM): replace a method-of-moments estimator's exact but
  intractable expected-response function with an unbiased Monte Carlo simulator of it, and rely on
  the law of large numbers across observations, not across simulation draws, to control the added
  noise. Proves consistency and asymptotic normality (Theorem 1, p. 1014) for a FIXED number of
  draws per observation, and gives the exact efficiency cost of that fixed count: with r independent
  draws per observation the simulated estimator's asymptotic covariance is (1+1/r) times the
  infeasible exact estimator's, i.e. 50% relative efficiency at r=1 and 90% at r=9 (p. 1006).
  Motivated by multinomial probit, whose exact response probabilities need infeasible numerical
  integration. Task item 8's other half, paired with gourieroux1993, which names this paper among
  the origins of the SMM special case of indirect inference.
loci:
  - methods/06
section: method-anchors
---

# mcfadden1989

VERIFIED. Held at `PDF_papers/McFadden_1989_simulated-method-of-moments-discrete-response.pdf`
(read in place at the intake path, then moved on 2026-09-22, bytes unchanged: see "PDF filename"
below). All 33 pages read directly as rendered page images on 2026-09-22, with
four of them re-read individually at full resolution to check every quoted formula and sentence.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | *Econometrica* **57**(5), pp. 995-1026 (Sep. 1989) | p. 1 (JSTOR cover sheet) and p. 995 (paper's own masthead: "Econometrica, Vol. 57, No. 5 (September, 1989), 995-1026") |
| author and affiliation | Daniel McFadden, Department of Economics, Massachusetts Institute of Technology, Cambridge, MA 02139, U.S.A. | p. 995 (byline "BY DANIEL McFADDEN") and p. 1025 (closing affiliation line) |
| manuscript dates | received October, 1987. Final revision received September, 1988 | p. 1025, final line before the references |
| stable URL / DOI source | `http://www.jstor.org/stable/1913621` | p. 1 (JSTOR cover sheet) |
| held-PDF page count | 33 | matches pp. 995-1026 (32 article pages) plus one JSTOR cover sheet |

## What it says, in its own terms

Verbatim, the abstract (p. 995): "This paper proposes a simple modification of a conventional method
of moments estimator for a discrete response model, replacing response probabilities that require
numerical integration with estimators obtained by Monte Carlo simulation. This method of simulated
moments (MSM) does not require precise estimates of these probabilities for consistency and asymptotic
normality, relying instead on the law of large numbers operating across observations to control
simulation error, and hence can use simulations of practical size. The method is useful for models
such as high-dimensional multinomial probit (MNP), where computation has restricted applications."
Keywords (p. 995): "Method of moments, simulation, multinomial probit, discrete response."

The introduction (p. 995) opens by defining the classical estimator the paper modifies: "A CLASSICAL
method of moments estimator" θ_mm "of an unknown parameter vector" θ* "minimizes the (generalized)
distance from zero of empirical moments," followed by a display summing, over observations, an
"Instrument Vector" against the difference of the "Observed Response" and the "Expected Response at
θ_mm". Then comes the paper's own reason to simulate instead of computing that expected response
exactly: "For some problems, the expected response function may be difficult to express analytically
or to compute, but relatively easy to simulate. When this function is replaced by an unbiased
simulator such that the simulation errors are independent across observations and sufficiently" θ
"the variance introduced by simulation will be controlled by the law of large numbers
operating across observations, making it unnecessary to consistently estimate each expected response.
This is the basis for the estimation method developed in this paper, the method of simulated moments
(MSM)."

Footnote 2 (p. 995, attached to `(MSM).²` in the main text) distinguishes MSM's concern from prior
simulation-based estimation: "The idea of simulating response probabilities from an underlying latent
variable model, generating the response probabilities by stochastic integration, is standard in the
area of computer simulation; see Hammersley and Handscomb (1964), Fishman (1973), and Lerman and
Manski (1981). This literature has concentrated on simulating the response probabilities to a level of
accuracy that enables their use in standard maximum likelihood procedures." MSM's point is the opposite:
per-observation simulation accuracy need not be high, because the law of large numbers acting across
the *sample*, not across draws, does the averaging.

## The formal construction

Section 2 (pp. 996-997) sets up a discrete-response latent-variable model: alternatives
$C=\lbrace 1,\dots,m\rbrace$, a latent index $u_i=\alpha x_i$ with $\alpha=a(\theta,\eta)$ a smooth function of
the parameter $\theta$ and a random vector $\eta$ with known density $g(\eta)$, response $i$ observed
when $u_i\geq u_j$ for all $j\in C$, and response probability $P_C(i|\theta,X_C)$ the corresponding
orthant probability (Eq. 2, p. 996). For multinomial probit (MNP), $\alpha$ is Gaussian and $P_C$ is
an $(m-1)$-dimensional orthant probability of a multivariate normal (Eq. 3, p. 997). Direct numerical
integration is, in the paper's own words, "practical for $m\leq4$ using a method of Owen (1956)" and,
separately, "otherwise, unless" $\alpha$ "has a factor-analytic covariance structure with less than four
factors, it is usually impractical to carry out the large number of numerical integrations required" (both
p. 997).

Section 3 (pp. 998-999) states the classical estimator formally,
$\theta_{mm}=\arg\min_\theta (d-P(\theta))'W'W(d-P(\theta))$ (Eq. 6, p. 998, with $d$ the stacked response-indicator residuals and
$W$ a $K\times mN$ instrument array of rank $K\geq k$), and gives two conditions (p. 998) sufficient
for classical method-of-moments estimation to be CAN (consistent, asymptotically normal): "(i) The
instruments are asymptotically correlated with the score... (ii) The conditional expectation of the
residuals $d-P(\theta)$, given the instruments, is zero if and only if $\theta=\theta^*$." It then
defines MSM, verbatim: "The method of simulated moments (MSM) avoids the computation of" $P(\theta)$
"required for (6), replacing it with a simulator" $f(\theta)$ "that is (asymptotically) conditionally
unbiased, given $W$ and $d$, independent across observations, and 'well behaved' in" $\theta$ (p. 998),
with the worked example being the *simple frequency simulator*: "independently drawing, for each
observation, one or more vectors" $\eta$ "from the density" $g(\eta)$ ", and then for any trial" $\theta$
"calculating" $u_{in}=a(\theta,\eta)x_{in}$ "and counting the frequency with which the" $u_{in}$ "for each
alternative is maximized" (p. 998). The estimator itself is defined by an inequality, not an
exact minimum, "to assure existence... even if the infimum cannot be attained" (p. 998): $\theta_{sm}$
is any argument satisfying
$(d-f(\theta_{sm}))'W'W(d-f(\theta_{sm})) \leq \inf_{\theta\in\Theta}(d-f(\theta))'W'W(d-f(\theta)) + O(1)$ (Eq. 7, p. 998).

Beyond the classical CAN conditions, MSM needs two more (p. 999, formalized as Assumptions A10-A11,
pp. 1013-1014): (iii) the simulation bias $B(\theta)=N^{-1/2}W(Ef(\theta)-P(\theta))$ is either exactly
zero or $\sup_\theta|B(\theta)|=o(1)$ (Eq. 8). (iv) The simulation residual process
$\zeta(\theta)=N^{-1/2}W(f(\theta)-Ef(\theta))$ is uniformly stochastically bounded and equicontinuous
in $\theta$ (Eqs. 9-10). Theorem 1 (p. 1014, proof pp. 1014-1016) is the main result, stated in the
paper's own symbols: the MSM estimator $\theta_{sm}$ defined by (7), satisfying Assumptions A1 to A11,
is consistent, with $N^{1/2}(\theta_{sm}-\theta^*)$ converging in distribution to a normal vector with
mean zero and covariance matrix
$\Sigma_{sm}=(\bar R'\bar R)^{-1}\bar R'G_{sm}\bar R(\bar R'\bar R)^{-1}$, with $\bar R=\lim N^{-1}WP_\theta(\theta^*)$ and
$G_{sm}=\lim N^{-1}EW(d-f(\theta^*))(d-f(\theta^*))'W'$. Assumptions A1-A11 do not require the number of simulation draws per observation to
grow with $N$: a *fixed* draw count is admissible for consistency and asymptotic normality on its own.
What a fixed count costs is quantified next.

## The efficiency-versus-draws result

This is the formula the task flags as directly relevant to the record's own twin, and it is stated in
the subsection "Estimators for the Asymptotic Covariance Matrix" within Section 3. Having given
$\Sigma_{sm}=(\bar R'\bar R)^{-1}\bar R'G_{sm}\bar R(\bar R'\bar R)^{-1}$ with $G_{sm}=G_{mm}+G_{ss}$
(Eq. 20, p. 1006) and identifying $G_{ss}=\lim N^{-1}\sum_n\sum_{i,j\in C}W_{in}W'_{jn}E(Y_{in}Y_{jn})$,
$Y_{in}=f_{in}(\theta^*)-P_{Cn}(i|\theta^*,X_{Cn})$, as "the contribution of the simulation to the
asymptotic variance," the paper states, verbatim (p. 1006, checked against the rendered page at full
resolution):

> "If" $f(\theta)$ "is the simple frequency simulator obtained by" $r$ "independent Monte Carlo draws for
> each observation, then" $G_{ss}=r^{-1}G_{mm}$ and $\Sigma_{sm}=(1+r^{-1})\Sigma_{mm}$. "In this case,
> one draw per observation gives fifty percent of the asymptotic efficiency of the corresponding
> classical method of moments estimator, and nine draws per observation gives ninety percent relative
> efficiency. Use of Monte Carlo variance reduction techniques such as antithetic variates, or use of
> smooth simulators, may improve further the relative efficiency of MSM."

So the closed-form efficiency-loss law is $\Sigma_{sm}=(1+1/r)\Sigma_{mm}$: relative efficiency
$r/(r+1)$, i.e. 50% at $r=1$, 90% at $r=9$, 99% at $r=99$, approaching 100% only as $r\to\infty$. This
holds for a *fixed* $r$ as the number of observations $N\to\infty$: the mechanism is that the $r$-draw
simulation noise at each of the $N$ observations is *independent across observations*. This is explicit in
the simple-frequency-simulator construction ("independently drawing, for each observation, ... $\eta$
... independently across observations," p. 998) and in Assumption A9 (p. 1013: the draws "are drawn...
independently of $W$ and $d$, and independently for different $n$"). So it averages away under the
same law of large numbers that makes the classical estimator itself consistent, leaving only a
residual variance *inflation* by $(1+1/r)$, not an inconsistency or a bias.

A separate, easily conflated point (p. 1004): getting $\theta_{sm}$ itself CAN with fixed $r$
(Theorem 1) is not the same as making MSM asymptotically *efficient* relative to maximum likelihood.
That stronger property needs near-optimal instruments $W\propto\partial\ln P(\theta^*)/\partial\theta$
estimated from simulation too, and for that, verbatim: "The number of draws per observation must go to
infinity with sample size if the ideal instruments are to be estimated consistently, permitting MSM to
be asymptotically efficient. However, modestly efficient instruments can be obtained with relatively
few draws" (p. 1004). The same paragraph adds a third, distinct independence requirement beyond A9's
across-observations one: "It is essential for the asymptotic statistics of the MSM estimator that
simulators of the response probabilities and their derivatives used to construct instruments be
*independent* of the simulator" $f(\theta)$ "used in the moment condition (7)" (p. 1004). That is, the
draws used to build $W$ must be a separate Monte Carlo sample from the draws used to build $f(\theta)$
itself. So the paper draws its own distinction between (a) a fixed, finite $r$ costing a computable,
bounded efficiency loss under a *given* instrument array $W$ (the $(1+1/r)$ law), and (b) $r\to\infty$
being required only if the instruments themselves are to be simulated to the point of reaching the MLE
efficiency bound, using draws independent of the moment simulator's own.

## The discrete-response motivation

Sections 5-7 (pp. 1007-1010) carry the method to three further discrete-response settings: panel data
with autoregressive errors (Section 5, introducing an acceptance/rejection unbiased score simulator,
p. 1008, as an alternative to the frequency simulator when $T$ is large), measurement error in the
explanatory variables (Section 6, an MNP model with a latent factor structure), and nonnormal or
rank-based discrete response (Section 7). Section 4 (pp. 999-1006) catalogues specific simulators for
the MNP response probability and their properties: the *smooth unbiased simulator* built from an
importance density $\gamma$ (Eqs. 11-12, p. 1000), *kernel-smoothed frequency simulators* that satisfy
the summing-up constraint the plain frequency simulator lacks (Eqs. 13-16, pp. 1000-1002, including a
variant due to Stern (1987)), and a *conditional chi-square frequency simulator* built from spherical
transformations of the latent normal vector (p. 1003), whose accuracy for 5-20 alternatives is reported
(p. 1004, footnote 4, pointing to the author's own unpublished numerical experiments and a GAUSS/FORTRAN
program available on request) to be improved by antithetic variates via a construction from Deák
(1980, p. 1003).

## Contemporaneous companion, and the link to gourieroux1993

The main text of the introduction (pp. 995-996) names the paper this one is usually cited alongside,
verbatim: "This paper focuses on application of MSM to discrete response models, particularly the
multinomial probit (MNP) model. However, the method is more general and can be applied to most moment
estimation problems. In a related paper, Pakes and Pollard (1989) have independently proposed minimum
distance" (footnote 1 marker interrupts here) "estimators using simulation, and have established their
statistical properties using combinatorial empirical process methods. Most of the statistical results
in this paper could also be obtained by application of their methods." Footnote 1 (p. 995, attached to
the byline) shows the relationship was closer than a shared citation: "I have particularly benefited
from discussions with Ariel Pakes and David Pollard, who pointed out a lacuna in my original analysis
of this problem. I have shortened the proof of the main theorem by adapting arguments from Pakes and
Pollard's independent investigation of the asymptotic behavior of simulation experiments." Pakes and
Pollard (1989), "The
Asymptotic Distribution of Simulation Experiments," ran in the *same issue* of Econometrica,
immediately after this paper: "PAKES, A., AND D. POLLARD (1989): ... Econometrica, 57, 1027-1057"
(reference list, p. 1026).

This is the same pairing `gourieroux1993`'s own introduction uses when it lists the works its
indirect-inference construction generalizes: (McFadden, 1989; Pakes and Pollard, 1989; Duffie and
Singleton, 1989; Smith, 1993; Gourieroux and Monfort, 1993)
(`private/cache/lit_intake_2026-09-21/notes/gourieroux1993.md`, quoting p. 3/S86 of that paper). Two
independent sources (McFadden's own footnote 1 here, written in 1988-89, and Gourieroux, Monfort and
Renault's 1993 citation list) pair the same two 1989 papers for the same underlying reason (both
proposed simulation-based moment/distance matching at essentially the same time, by different routes),
which is a real, if modest, cross-check, not a coincidence of citation convention.

This paper cannot cite `gourieroux1993` (it is four years earlier), so there is no direct textual claim
to check the other way. What can be checked is whether McFadden's own description of MSM is consistent
with being a *special case* of the more general indirect-inference construction `gourieroux1993` states
it to be. It is, structurally: MSM (Eqs. 6-7 above) requires the simulator $f(\theta)$ to be an unbiased
simulator of the same quantity the classical, exact estimator would use, $P(\theta)$ itself: a
narrower requirement than indirect inference's, which lets the auxiliary criterion be any convenient,
tractable estimator matched between real and simulated data, with no requirement that it be an unbiased
simulator of the structural moment itself. McFadden's own framing supports this reading: the abstract
calls MSM "a simple modification of a conventional method of moments estimator" (p. 995), not a new
class of estimator, and Section 3's whole construction is phrased as a substitution inside the classical
method-of-moments objective, not as a new criterion. So `gourieroux1993`'s *special case*
characterization is structurally consistent with how this paper presents itself, though this paper
never uses the phrase *indirect inference* or anything equivalent to it: "simulated" here always means
simulating the moment/response function itself, never matching two runs of a separate auxiliary model.

## What received a lighter pass

Lemmas 1-10 (pp. 1012-1025) establish that specific simulators and regularity structures satisfy the
technical assumptions Theorem 1 needs. Four of their targets are stated explicitly enough to record with
confidence: Lemma 1 (p. 1012) concludes 'Then A3 and A4 hold'. Lemma 2 (p. 1012) concludes 'Then A5
holds'. Lemma 6 (p. 1020) concludes 'Then A13 holds'. Lemma 8 (pp. 1022-1023) concludes 'Then A11
holds,' building on Lemma 7's bracketing-entropy central limit theorem (p. 1021, citing Dudley 1984,
Theorem 6.2.1, and a restatement from Alexander 1987, Theorem 2.1). Lemma 9 (p. 1023) establishes
consistency of the covariance-matrix estimators (21)-(22). Lemma 10 (pp. 1024-1025) derives MNP
instrument-construction formulas $\partial P_C/\partial\beta$ and $\partial P_C/\partial\Gamma$. All ten
were read for their statement and role in the argument, not independently re-derived line by line.
Their own proof techniques (the covering-and-chaining argument on $[0,1]^k$ with $2^{kj}$ cubes in
Lemma 8, the Bernstein's-inequality bound in Lemma 4 (pp. 1017-1018), and the cylinder-function/spherical-
transformation simulator (pp. 1002-1003)) got a lighter pass than the main text and Theorem 1's own proof.
None of this rests on those proofs' internal correctness. It rests on the theorem statement, the
assumptions it discharges, and the efficiency formula on p. 1006, all read closely and re-checked at full
resolution.

## PDF filename

Read in place at `PDF_papers/_intake_2026-09-22/mcfadden1989.pdf`, then moved on 2026-09-22, bytes
unchanged (its sha256 matches that folder's SHA256SUMS line), to the standard-form name for this
shelf, following the
`Lastname_Year_kebab-case-slug.pdf` convention already in use (e.g.
`Alcock_1984_vapour-pressure-equations-metallic-elements.pdf`,
`Arguelles_2019_binned-likelihood-finite-Monte-Carlo.pdf`): that name is
`McFadden_1989_simulated-method-of-moments-discrete-response.pdf`, which is what the `pdf:` frontmatter
field above names.

## Use in this record

This record's own stated method (using the twin to compute and factor out biases) and the task's
own framing of this paper point at the same thing: this is the formal origin of using simulation to
compute a moment (or a statistic, or a bias correction to one) whose exact form is intractable, and
fitting or correcting via those simulated values instead of the exact ones. `docs/methods/06_the_statistics.md`
already runs a version of exactly this shape for at least one estimator: `results/estimator_duel.csv`'s
bias figures are quoted there as carrying the spread over 120 realisations, not the bias's own error,
which is $\sqrt{120}$ smaller, and the record states its general practice for a fitted parameter's
finite-sample bias as injecting through the twin and subtracting the measured offset (methods/06 §5).
A fixed, finite realization count feeding a bias correction is exactly MSM's regime, not the
$r\to\infty$ regime McFadden reserves for instrument-efficiency (p. 1004). So Theorem 1's basic
legitimacy claim (a fixed $r$ suffices for consistency and asymptotic normality, not merely as a
stopgap awaiting more draws) already licenses this record's practice of using a bounded number of twin
realizations per trial point, instead of treating a finite realization count as inherently provisional.

The $(1+1/r)$ formula (p. 1006) is the natural quantitative target to check the record's own
realization counts against, but two of the formula's structural conditions need to be stated explicitly
before importing its numbers, because both bear on whether it applies as-is or only in spirit:

1. **Independence across the units the law of large numbers runs over.** McFadden's result needs the
   $r$-draw simulation noise to be independent across the $N$ observations being averaged over
   (Assumption A9, p. 1013, and the construction on p. 998). The noise then cancels at the same
   $N^{-1/2}$ rate as the rest of the estimator, leaving only the bounded $(1+1/r)$ inflation. If this
   record's twin instead computes one bias estimate from $r$ realizations at a trial parameter and then
   applies that same fixed correction across many traces or across a grid, the $r$-draw noise in that
   correction is *shared* across those downstream uses, not independent per use, and does not average
   away the way McFadden's does. The formula's precise 50% at $r=1$ / 90% at $r=9$ numbers are the right
   benchmark for the case they were derived for. This record's own case needs the same accounting
   redone for shared, not per-observation, simulation noise before those exact numbers can be
   quoted for it, a gap flagged here, not closed.
2. **The formula bounds a covariance inflation for a consistent estimator, not a bias.** McFadden's A10
   (p. 1013) requires the simulator to be unbiased, or asymptotically so, uniformly in $\theta$. The
   $(1+1/r)$ result is the extra variance a finite $r$ costs on top of that. It says nothing about how
   large $r$ needs to be to drive a simulator's own bias below a stated tolerance, which is closer to the
   question `docs/methods/06_the_statistics.md` §5's statement that the bias's own error, which is
   $\sqrt{120}$ smaller than the spread, is actually answering: that is an ordinary Monte Carlo standard-error
   argument (a mean's standard error shrinks as $1/\sqrt{r}$), not McFadden's covariance-inflation law.

Read together, McFadden 1989 gives this record two distinct, precise, and citable things: the formal
license for using a fixed, finite simulation count at all in a moment-based estimator (Theorem 1, not a
heuristic), and a closed-form efficiency-cost law for the one case (independent per-observation draws
feeding a method-of-moments objective directly) that matches this record's twin only if its bias
corrections are re-derived independently at each point they are applied. That independence is not yet
asserted anywhere in this record and would need to be checked, not assumed, before citing the
$(1+1/r)$ number here as a rule for sizing the twin's own realization count.
