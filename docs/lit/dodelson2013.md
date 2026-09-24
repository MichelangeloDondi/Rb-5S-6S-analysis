---
citekey: dodelson2013
type: article
authors:
  - Dodelson, Scott
  - Schneider, Michael D.
title: 'The Effect of Covariance Estimator Error on Cosmological Parameter Constraints'
journal: Physical Review D
volume: 88
pages: '063537'
year: 2013
doi: 10.1103/PhysRevD.88.063537
arxiv: '1304.2593'
pdf: PDF_papers/Dodelson_2013_covariance-estimator-error-cosmological-constraints.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/dodelson2013.md
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'All six pages read directly on 2026-09-22, in text and rendered page-image form: the abstract, Sect. I
    (introduction and literature comparison), Sect. II (the single-parameter diagonal toy model, Eq. 1-11),
    Sect. III (the general-case derivation, Eq. 12-27, the Gaussian-limit coefficients of Sect. III.A/Eq. 28,
    the weak-lensing non-Gaussian check of Sect. III.B, and the current-surveys table of Sect. III.C/Table I),
    Sect. IV (conclusions) and the reference list.'
verified_date: 2026-09-22
summary: >
  Derives, to quadratic order in the inverse-covariance error, the extra variance a simulation-estimated
  covariance matrix adds to every fitted parameter's error bar on top of Hartlap et al.'s debiasing, and
  gives the Gaussian-limit closed form (its own Eq. 28) that reduces, when the simulation count Ns is much
  larger than both the coordinate count Nb and the parameter count Np, to a variance inflation of order
  1 + Nb/Ns. Tabulates the resulting 5-15% degradation for three real surveys (its own Table I).
loci:
  - methods/06
section: method-anchors
---

# dodelson2013

Held. Read in full against the PDF, text and rendered page images both.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rev. D **88**, 063537 (2013) | not printed on this preprint. Full-text search finds no `063537` or `Phys. Rev. D 88` anywhere in this arXiv v2 PDF. Cross-checked directly against `sellentin2016`'s own reference list (p. 6, in its own words: Dodelson S., Schneider M. D., 2013, Phys. Rev. D, 88, 063537) and the arXiv abstract-page listing, independently agreeing |
| DOI | 10.1103/PhysRevD.88.063537 | arXiv abstract-page listing |
| arXiv identifier | 1304.2593v2, 13 Sep 2013 | p. 1 header |
| report number | LLNL-JRNL-632261 | p. 1 |
| affiliations | Fermilab Center for Particle Astrophysics / Kavli Institute for Cosmological Physics, University of Chicago (Dodelson). Lawrence Livermore National Laboratory / University of California, Davis (Schneider) | p. 1 |

## What it says, in its own terms

The abstract, verbatim: "Extracting parameter constraints from cosmological observations requires accurate
determination of the covariance matrix for use in the likelihood function. We show here that uncertainties
in the elements of the covariance matrix propagate directly to increased uncertainties in cosmological
parameters. When the covariance matrix is determined by simulations, the resulting variance of the each
parameter increases by a factor of order 1 + Nb /Ns where Nb is the number of bands in the measurement and Ns
is the number of simulations." (p. 1, abstract: "the each" is the paper's own wording, checked directly
against the page image, not a transcription error).

Where the correction sits relative to Hartlap's. The introduction places this paper explicitly downstream of
`hartlap2007`: "Previous work on covariance errors focused on the bias in the inverse covariance estimate
[14] and uncertainties in parameter errors [15]. Specifically, Ref. [14] showed that a statistical error in
the covariance matrix estimator leads to a multiplicative bias in the inverse covariance, or precision,
matrix. This bias can be easily corrected ... by multiplying the precision matrix estimator with a known
factor" (p. 1). Ref. [14] is `hartlap2007` itself. The paper's own new contribution is a QUADRATIC-order
term beyond that correction: Sect. II's single-parameter toy model (diagonal covariance) decomposes the
fluctuation Ψ_i = Ψ^t_i + ΔΨ_i (Eq. 6) and finds the estimator variance picks up a second-order piece
Δx² = (1+α)/Σ_i Ψ_i (Eq. 11) with ⟨ΔΨ_iΔΨ_j⟩ = αδ_ij Ψ_i² (Eq. 10) and α ≃ 1/Ns for Ns simulations: "We call
the new term covariance estimator error, and it simply increases the errors on our estimate of x." (p. 2).

The general-case result (Sect. III, pp. 2-4). Generalising to a full off-diagonal covariance, several
parameters p_α, and non-trivial model predictions x_i(p_α), the paper isolates the quadratic-order
contribution to the parameter covariance,

    ⟨p_α p_β⟩|s.o. = B F^-1_αβ (Nb - Np)                                          (Eq. 27, p. 4)

where F is the standard Fisher matrix (Eq. 19) and Np < Nb is the number of fitted parameters, writing the
fluctuation model ⟨ΔΨ_ijΔΨ_i'j'⟩ = A Ψ_ij Ψ_i'j' + B(Ψ_ii'Ψ_jj' + Ψ_ij'Ψ_ji') (Eq. 26) for two scalars A, B.
Section III.A (`Gaussian limit`, p. 4) gives their closed form, attributing the computation to a prior paper:
"Taylor et al. [15] computed the values of A and B in the Gaussian case (after correcting for the bias in the
inverse covariance estimator [14])". That is, after the Hartlap correction, not instead of it or before it:

    A = 2 / [(Ns-Nb-1)(Ns-Nb-4)]
    B = (Ns-Nb-2) / [(Ns-Nb-1)(Ns-Nb-4)]                                           (Eq. 28, p. 4)

"As in the toy model of §II, in the (common) limit that Ns ≫ Nb ≫ Np, the variance is enhanced over the
standard variance by a factor of (1 + Nb/Ns). This is our main conclusion." (Sect. III.A, p. 4). Section III.B
checks the Gaussian-limit prediction against weak-lensing simulations with a genuinely non-Gaussian field and
finds "Eq. (28) gives a good fit to the simulation samples" even there (p. 4, Fig. 1). Section III.C / Table I
tabulates three real surveys: BOSS (Ns=600, Nb=41, 7%), DLS (Ns=1000, Nb=60, 6%), CFHTLens (Ns=184, Nb=24,
13%): "the degradation ranges from 5-15%" (p. 4). The conclusions (Sect. IV, p. 4) restate the scope
condition directly and name Ledoit-Wolf-style shrinkage only as future work, not analysed here: "Mitigation
schemes such as shrinkage estimators [23], emulators [17, 24], and large-scale mode-resampling [25] will be
important to reduce these computational requirements to tractable levels." Ref. [23] is Pope & Szapudi
(2008), not `ledoit2004`. The paper never cites Ledoit & Wolf by name or analyses their estimator.

## Use in this record

**The leading-order figure at Ns = 500 replicas, Nb = 50 coordinates.** Direct substitution into the
abstract's own "1 + Nb/Ns": 1 + 50/500 = 1.10, i.e. a 10% inflation of every fitted parameter's variance from
the covariance's own finite-replica noise, on top of whatever the Hartlap correction has already removed.

**The exact Gaussian-limit figure at the same size, from Eq. (28).** With Ns-Nb-1 = 449, Ns-Nb-2 = 448,
Ns-Nb-4 = 446: B = 448/(449×446) = 448/200254 ≈ 0.002237. Eq. (27)'s fractional variance increase is
B×(Nb-Np). For Np ≪ Nb (Np → 0) this is 0.002237×50 ≈ 0.112 (11.2%), and for a joint fit sharing, say, ten
parameters across the moment block, 0.002237×40 ≈ 0.089 (8.9%). Both bracket the leading-order 10% estimate
from opposite sides and both sit inside the empirical 5-15% range Table I reports for real surveys whose own
Ns/Nb ratios (7.7 to 16.7) bracket this record's own Ns/Nb = 10: CFHTLens's 7.7-ratio/13% and BOSS's
14.6-ratio/7% pair bracket this record's own number in the same direction the formula predicts.

**The regime check.** The paper states its own limit condition explicitly: "in the (common) limit that
Ns ≫ Nb ≫ Np" (Sect. III.A, p. 4). Ns/Nb = 10 at this record's own numbers is a full order of magnitude, but
it is the same order as the real surveys of Table I, none of which reach much beyond 17. So the leading-order
"1 + Nb/Ns" figure is read here as the same kind of serviceable approximation Table I's own entries represent,
not as an asymptotic limit this record's numbers actually reach. The exact Eq. (27)-(28) form does not need
the limit at all and is the more defensible number of the two once Np is fixed.

**Sequencing, stated once and load-bearing.** This paper's own headline number is not independent of, and does
not precede, `hartlap2007`'s correction: its own Gaussian-limit coefficients are computed "after correcting
for the bias in the inverse covariance estimator [14]" (p. 4), so the ≈9-11% figure above is a cost that
remains even once the inverse covariance itself has been debiased by Hartlap's factor, not an alternative to
applying it and not a cost that stacks on top of an uncorrected inverse covariance.

**Which of the two likelihood corrections this paper takes a position on.** None. It is silent on the choice
between a debiased-inverse Gaussian and a marginalised t-distributed likelihood, because it was written three
years before `sellentin2016` derived the second option. Its own analysis is conducted entirely inside the
Gaussian-likelihood, point-estimated-precision-matrix framework `sellentin2016` argues against. `sellentin2016`
itself, however, names this paper on its own first page as one of two prior works it describes as similar to
the result derived there, documenting, in its own words, that statistical noise in the precision matrix
propagates into errors in the
parameters (Taylor et al. 2013; Dodelson & Schneider 2013; Hamimeche & Lewis 2009) (p. 1 of `sellentin2016`). So the size this
paper quantifies, roughly a tenth of the nominal variance at this record's own N and p, is read as an estimate
of exactly the cost `sellentin2016`'s marginalisation is built to absorb into the likelihood's own shape, not
as something patched on afterwards as a fixed inflation factor.
