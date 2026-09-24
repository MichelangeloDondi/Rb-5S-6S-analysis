---
citekey: taylor2013
type: article
authors:
  - Taylor, Andy
  - Joachimi, Benjamin
  - Kitching, Thomas
title: 'Putting the Precision in Precision Cosmology: How accurate should your data covariance matrix be?'
journal: Monthly Notices of the Royal Astronomical Society
volume: 432
number: 3
pages: 1928-1946
year: 2013
doi: 10.1093/mnras/stt270
arxiv: '1212.4359'
pdf: PDF_papers/Taylor_2013_precision-cosmology-data-covariance-matrix-accuracy.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/taylor2013.md  # line-by-line against the held PDF, 2026-09-22: re-confirmed the radical-sign and affiliation fixes, corrected a new overclaim (the abstract's 200-realisation and `N_S` > `N_D` rules are rounded off from equation 58's exact `N_S` > 204 + `N_D` at epsilon = 0.1, not left exact as the note had claimed), fixed a knock-on replica-margin claim, and read Section 4 in full to close a gap the note had left open
author: agent
routing:
  - CITE
  - FEED
verify_flags:
  - 'Page 1 (title, author list, full abstract, opening of the introduction) read directly from the held PDF via
    text extraction on 2026-09-21. The Wishart/inverse-Wishart derivation (the paper''s technical core) is not
    yet read.'
  - 'Page 1 re-read on 2026-09-22 as a rendered image (not text extraction) during the line-by-line audit: the
    abstract''s `< 2/ND` bound is actually `< sqrt(2/ND)` in the typeset PDF. pdftotext -layout silently drops
    the radical sign here, which the original 2026-09-21 text-extraction pass and this note''s verbatim quote
    both inherited. Sections 2-8 were read in full on 2026-09-22, including Section 4''s weak-lensing simulation
    and the Hartlap cross-check inside it (Section 4.1.2), Section 5.4''s worked accuracy argument, Section 6''s
    Figure-of-Merit, Section 7''s remedies, and Section 8''s summary. This closes the gap the note''s own "Not
    yet read" section had left around Section 4. The abstract''s 200-realisation and `N_S` > `N_D` rules are not left
    exact by equation 58, corrected 2026-09-22 from an earlier claim that they were: at epsilon = 0.1, equation
    58 reads `N_S` > 204 + `N_D`, and the body itself evaluates this as 204, not 200, at `N_D` << 100, and restates it as
    `N_S` > `N_D` + 4, not `N_S` > `N_D`, at `N_D` >> 100, dropping the same additive term the abstract also drops. Page 8 was
    rendered at 250 dpi and read directly to confirm equation (58) and this surrounding prose are typeset as
    extracted, so the rounding is the paper''s own headline simplification, not a text-extraction defect. The
    appendices and any discussion of a moment-ratio (instead of power-spectrum) data vector remain unread or
    unaddressed.'
verified_date: 2026-09-22
summary: >
  Shows that when data and precision (inverse covariance) matrices are estimated by sampling independent
  realizations, their statistical properties follow the Wishart and inverse-Wishart distributions respectively,
  and that the fractional error on a parameter variance equals the fractional variance of the precision matrix,
  independent of survey details. States a concrete rule of thumb linking the needed number of realizations to
  the coordinate count (`N_S` > `N_D` once `N_D` >> 100) and names shrinkage as one of the standard remedies when that
  many realizations are not affordable -- both numbers land close to this record's own stated N and coordinate
  count. A companion result to Hartlap et al. and Dodelson & Schneider, using the same Wishart machinery that
  nascimento2014 (already held) applies to a different bias-correction problem.
loci:
  - methods/06
section: method-anchors
---

# taylor2013

VERIFIED for the paper in full except its appendices (Sections 1-8, read across 2026-09-21 and 2026-09-22).
The appendices, describing the weak-lensing field and power-spectrum simulation Section 4.1 cites, were not
read, and no claim above depends on them.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | MNRAS **432**(3), 1928-1946 (2013) | cross-checked against secondary listings, not yet against the held PDF's own masthead |
| DOI | 10.1093/mnras/stt270 | arXiv abstract-page listing |
| arXiv identifier | 1212.4359v1, 18 Dec 2012 | p. 1 header |
| affiliations | the Scottish Universities Physics Alliance, Institute for Astronomy, University of Edinburgh (Taylor, Joachimi, and also Kitching), and Mullard Space Science Laboratory, UCL (Kitching) | p. 1 |

## What it says, in its own terms

Verbatim, the abstract in full: "Cosmological parameter estimation requires that the likelihood function of the
data is accurately known. Assuming that cosmological large-scale structure power spectra data are multivariate
Gaussian-distributed, we show the accuracy of parameter estimation is limited by the accuracy of the inverse data
covariance matrix -- the precision matrix. If the data covariance and precision matrices are estimated by
sampling independent realisations of the data, their statistical properties are described by the Wishart and
Inverse-Wishart distributions, respectively. Independent of any details of the survey, we show that the
fractional error on a parameter variance, or a Figure-of-Merit, is equal to the fractional variance of the
precision matrix. In addition, for the only unbiased estimator of the precision matrix, we find that the
fractional accuracy of the parameter error depends only on the difference between the number of independent
realisations and the number of data points, and so can easily diverge. For a 5% error on a parameter error and
ND << 10^2 data-points, a minimum of 200 realisations of the survey are needed, with 10% accuracy in the data
covariance. If the number of data-points ND >> 10^2 we need NS > ND realisations and a fractional accuracy of"
< sqrt(2/`N_D`) "in the data covariance. As the number of power spectra data points grows to ND > 10^4-10^6 this approach
will be problematic. We discuss possible ways to relax these conditions: improved theoretical modelling;
shrinkage methods; data-compression; simulation and data resampling methods." (p. 1, abstract, complete. Carets
mark the paper's own superscripts, `ND << 10^2` / `ND >> 10^2` transliterate the paper's much-less-than /
much-greater-than symbols, and `sqrt(2/ND)` transliterates the paper's own radical sign, confirmed against a
rendered image of p. 1 on 2026-09-22, since `pdftotext -layout` silently drops that sign here and reads as plain
`2/ND`, a materially smaller and different bound).

<!-- rendered-page: p. 1 -->

## Use in this record

This is, of the whole covariance-estimation cluster, the paper whose own abstract states a number closest to
actionable for this record's stated regime. At this record's own p ("about 200-300 candidate coordinates"), the
abstract's own dividing line is `N_D` >> 100, two to three times over at this record's coordinate count, which by
the paper's own rule means the realisation count `N_S` needs to exceed the coordinate count (`N_S` > `N_D`) for the
fractional accuracy bound to hold, and the required data-covariance accuracy tightens as sqrt(2/`N_D`), a
1/sqrt(`N_D`) scaling, corrected 2026-09-22 from an earlier 1/`N_D` misreading caused by a dropped radical sign in
the text-extraction pass (see Values and the verbatim quote above). Read against this
record's own stated range (N = 200-500 replicas against 200-300 coordinates), that puts the low end of the
replica range (200) at or below the coordinate count (300), exactly the p > n singular regime `hartlap2007`'s
abstract proves the covariance is unusable in directly, while the high end (500), read against the abstract's
own rounded `N_S` > `N_D` rule, looks like it clears by 200 replicas. Equation (58) itself is the more precise test,
corrected 2026-09-22 from an earlier reading that took the abstract's rule as exact (see Not yet read): at
epsilon = 0.1 it reads `N_S` > 204 + `N_D`, so 500 replicas clears with 96 to spare at the low end of this record's
own coordinate range (`N_D` = 200, threshold 404) but falls 4 replicas short at the high end (`N_D` = 300, threshold
504). The abstract's own list of remedies when raising N is not affordable ends
with "shrinkage methods" by name, alongside data-compression and resampling, which is this record's own
`ledoit2004`, so this paper is, in its own words, the reason the record needs a shrinkage estimator at the low
end of its stated N instead of only a bias-corrected inverse.

The Wishart/inverse-Wishart distributional framework named here is also the same underlying mathematical object
`nascimento2014` (already held in this record's shelf, `docs/lit/nascimento2014.md`) applies a bias correction to
in a completely different application (polarimetric radar looks). That is a useful cross-check: a treatment of
this record's own moment-covariance matrix as Wishart-distributed would let this paper's precision-matrix result
and `nascimento2014`'s Cox-Snell/Barndorff-Nielsen corrections be checked against each other on the same
distributional footing, instead of as unrelated citations. And combined with `dodelson2013`'s 1 + Nb/Ns rule,
this record now has two independently-derived, roughly consistent statements of the same cost (a finite
twin-replica count inflates reported parameter uncertainty), worth checking against each other numerically once
both derivations are read in full.

## Not yet read

The Wishart/inverse-Wishart derivation and the "Figure-of-Merit" argument (the paper's technical core, and the
source of the 200-realisation and `N_S` > `N_D` rules quoted above) were unread as of 2026-09-21, so those rules were
reported as the paper's stated conclusions, not yet checked against their own derivation. During the 2026-09-22
audit, Section 5.4's worked derivation (equation 58, `NS > 2/epsilon^2 + (ND + 4)`) was read specifically to
check this. Corrected 2026-09-22: equation 58 does not derive the abstract's 200-realisation and `N_S` > `N_D` rules
without further simplification, contrary to what this section previously said. At epsilon = 0.1, equation 58
reads `N_S` > 204 + `N_D`. The body's own next paragraph evaluates this as 204, not 200, at `N_D` << 100, and restates it
as `N_S` > `N_D` + 4, not `N_S` > `N_D`, at `N_D` >> 100. The abstract's two headline numbers are both a rounded-off version of
equation 58, dropping the same small additive term each time. Section 4's numerical weak-lensing simulation (the
Hartlap cross-check in Section 4.1.2, and the future-survey sizing in Section 4.2) and Sections 6 to 8 were also
read in full during this audit and raise no further correction. What remains genuinely unread is the appendices
and any discussion of whether the result is expected to transfer unchanged to a moment-ratio (instead of
power-spectrum) data vector, which the paper does not address either way.
