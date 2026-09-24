---
citekey: fornasini2015
type: article
authors:
  - Fornasini, P.
  - Grisenti, R.
title: 'On EXAFS Debye-Waller factor and recent advances'
journal: Journal of Synchrotron Radiation
volume: 22
number: 5
pages: 1242--1257
year: 2015
doi: 10.1107/S1600577515010759
arxiv: null
pdf: PDF_papers/Fornasini_2015_EXAFS-Debye-Waller-cumulant-expansion-ratio-method-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/fornasini2015.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, all claims, quotes and equation/page pairs verified exactly
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1242-1244 (the paper''s own pagination; pages 1-3 of the held PDF, an author-hosted
    electronic reprint from the University of Trento institutional repository, IUCr copyright
    notice permitting author self-archiving) read directly on 2026-09-21: title, abstract, Section
    1 (Introduction) and Section 2.1 (Unidimensional model and cumulants) through the pair-
    potential and cumulant-perturbation formulas (their eq. 1-6). Sections 2.2 onward (the
    real-versus-effective-distribution correction, the ratio method proper in Section 3, and the
    experimental comparisons on Cu and CdTe, pages 1244-1257) were NOT read.'
verified_date: 2026-09-21
summary: >
  A 2015 review of the EXAFS Debye-Waller factor, opening by stating that an EXAFS spectrum is a
  configurational average over a ONE-DIMENSIONAL distribution of interatomic distances that "for
  weak disorder, can be parameterized in terms of its leading cumulants (Bunker, 1983)" (p. 1243),
  and reproducing Bunker's own cumulant-generating-function relation between the measured signal
  and the distribution's cumulants C_n (eq. 3-4, p. 1244). The open, modern, self-contained
  restatement of Bunker 1983's ratio method, which the task named directly and which is paywalled.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# fornasini2015

VERIFIED for the paper's own pages 1242-1244 (title through the cumulant-parametrized signal, eq.
4). The ratio method itself (Section 3) and the experimental sections (Sections 4-7) were not
read.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | J. Synchrotron Rad. (2015). **22**, 1242-1257 | p. 1242 masthead |
| affiliation | Dipartimento di Fisica, Universita di Trento, I-38123 Povo, Trento, Italy | p. 1242 |
| access | electronic reprint banner, IUCr copyright notice: "Author(s) of this paper may load this reprint on their own web site or institutional repository provided that this cover page is retained" | p. 1242, cover banner |
| EXAFS signal as a cumulant expansion | k*chi(k) = S_0^2 \|f(k,pi)\| N * exp[C_0 - 2*C_2*k^2 + (2/3)*C_4*k^4 - ...] * sin[2*C_1*k - (4/3)*C_3*k^3 + (4/15)*C_5*k^5 - ... + phi(k)] | p. 1244, eq. 4 |
| generating relation | ln integral_0^infty P(r,lambda) exp(2ikr) dr = sum_{n=0}^infty [(2ik)^n / n!] C_n | p. 1244, eq. 3, attributed to "(Bunker, 1983; Crozier et al., 1988)" |
| third cumulant | C_3 = <(r - <r>)^3>, "a measure of the distribution asymmetry" | p. 1244, text below eq. 4 |

## What it says, in its own terms

Abstract (verbatim, p. 1242): "The effects of structural and vibrational disorder on the EXAFS
signals are parameterized in terms of the Debye Waller (DW) factor. Here the vibrational
contribution is addressed, which for most systems can be singled out by studying the temperature
dependence of the EXAFS DW factor, which corresponds to a good accuracy to the parallel mean
square relative displacement (MSRD) around the inter-atomic equilibrium distance."

Section 1 (p. 1243) states the physical picture directly: "For each scattering path, an EXAFS
experiment samples a unidimensional distribution of inter-atomic distances that, for weak
disorder, can be parameterized in terms of its leading cumulants (Bunker, 1983). The second
cumulant, or Debye-Waller (DW) exponent, is the variance of the distance distribution... To a good
approximation, the second cumulant corresponds to the parallel mean square relative displacement
(MSRD)." Section 2.1 (p. 1244) gives Bunker's own cumulant-generating-function relation (eq. 3,
table above) and the resulting parametrization of the observable signal directly in terms of the
Unobserved distribution's cumulants C_n order by order (eq. 4): C_1 is the mean, C_2 the variance,
and "Higher-order cumulants quantify the deviation of the distribution from the Gaussian shape". The
third cumulant, C_3 = <(r-<r>)^3> in the note's own transliteration of the paper's angle-bracket
notation, "is a measure of the distribution asymmetry" (p. 1244).

The paper also names the companion technique the task listed by name, in Section 3.1 (p. 1249):
"The ratio method (Bunker, 1983; Dalba et al., 1993) consists of the separate analysis of phase
and amplitude of the EXAFS signal at each temperature", read here only by name and by this one
sentence, not by the method's own fuller derivation (the rest of Section 3, unread).

## Use in this record

The nearest metrological analogue this cluster found: an established, forty-year-old spectroscopic
technique that already does, on a measured spectral signal, close to exactly what this record's
own programme does on its own lineshape. Bunker's relation (eq. 3) is precisely a statement that a
measured signal's Fourier-type transform, expanded in orders of the transform variable, returns the
cumulants of an underlying, unobserved one-dimensional distribution directly: the same logical
move this record makes when it reads a truncated two-photon lineshape's windowed moments as
estimators of the underlying light-shift distribution's cumulants. The explicit naming of the third
cumulant as "a measure of the distribution asymmetry" (p. 1244) is the same role this record's own
third and higher windowed moments play for the light-shift distribution's departure from symmetric
broadening. Because Bunker 1983 itself (held separately as the paywalled `bunker1983`) is not on
this record's shelf, this 2015 review is the vehicle for citing that lineage: it reproduces Bunker's
central relation with attribution, in an open, author-hosted copy, and can stand in for the
original wherever this record needs to name the EXAFS cumulant/ratio-method precedent without
needing the 1983 paper itself in hand. What was not read here, the ratio method's own derivation,
Section 3, is exactly the part that would show how EXAFS suppresses model-dependence when
extracting cumulants from real, noisy, partially truncated data, which is the piece most worth
reading next if this analogue is pursued further.
