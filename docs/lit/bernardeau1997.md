---
citekey: bernardeau1997
type: article
authors:
  - Bernardeau, F.
  - Van Waerbeke, L.
  - Mellier, Y.
title: 'Weak Lensing Statistics as a Probe of Omega and Power Spectrum'
journal: Astronomy & Astrophysics
volume: 322
pages: 1--18
year: 1997
doi: null
arxiv: 'astro-ph/9609122'
pdf: PDF_papers/Bernardeau_1997_weak-lensing-skewness-breaks-Omega-sigma8-degeneracy.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/bernardeau1997.md  # line-by-line against the held PDF, 2026-09-22; two corrections applied (a mislocated journal-reference citation, and a quote that had silently dropped four words)
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-3 of the held PDF (arXiv:astro-ph/9609122v2, revised 7 Jul 1997) read directly on
    2026-09-21: title, abstract, Section 1 (Introduction) and the start of Section 2 (the physical
    model for the galaxy and mass distributions) through the definition of the convergence kappa
    and the deformation matrix (their eq. 1-14). Sections 3-5 (the variance and skewness
    derivations, the error budget, and the conclusions, pages 4-18) were NOT read, so the specific
    scaling exponents quoted below are taken from the abstract, not derived or checked here.'
verified_date: 2026-09-21
summary: >
  States that the variance of the weak-lensing convergence scales approximately as
  P(k) Omega_0^1.5 z_s^1.5 while its skewness scales as Omega_0^-0.8 z_s^-1.35 (abstract), so the
  two moments of one filtered field, jointly, constrain both the power spectrum P(k) and the
  matter density Omega_0 where either moment alone leaves a degeneracy -- the paper the strategy
  document's "lensing skewness breaking the Omega_m-sigma_8 degeneracy" line names.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# bernardeau1997

VERIFIED for pages 1-3 (title through the deformation-matrix formalism). The variance and
skewness scaling laws quoted in the abstract, and used below, are not independently re-derived or
checked against Sections 3-4, which were not read.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | A&A **322**, 1-18 (1997) | bibliographic record (ADS/Crossref). Not printed on the held preprint, whose own p. 1 masthead carries only the pre-publication placeholder "A&A manuscript no. (will be inserted by hand later)". No DOI found via a Crossref title search on 2026-09-21 |
| affiliations | SPhT Saclay, Observatoire Midi-Pyrenees, IAP and Observatoire de Paris | p. 1 |
| variance scaling | variance of convergence ~ P(k) Omega_0^1.5 z_s^1.5 | abstract, p. 1 |
| skewness scaling | skewness of convergence ~ Omega_0^-0.8 z_s^-1.35 (the abstract's own skewness clause carries no explicit P(k) factor, unlike its variance clause) | abstract, p. 1 |
| convergence definition | kappa(xi) = 1 - tr[A^-1_ij(xi)] / 2 | p. 3, eq. 11 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "The possibility of detecting weak lensing effects from deep wide field
imaging surveys has opened new means of probing the large-scale structure of the Universe and
measuring cosmological parameters. In this paper we present a systematic study of the expected
dependence of the low order moments of the filtered gravitational local convergence on the power
spectrum of the density fluctuations and on the cosmological parameters Omega_0 and Lambda...
More precisely we show that the variance of the convergence varies approximately as P(k)
Omega_0^1.5 z_s^1.5, whereas the skewness varies as Omega_0^-0.8 z_s^-1.35... Thus, used jointly
they can provide both P(k) and Omega_0. However, the dependence on the redshift of the sources is
large and could be a major concern for a practical implementation."

Section 1 (p. 2, in the Introduction's closing paragraphs, before the Section 2 header on the same
page) states explicitly that the choice of statistic matters: "For the third moment however, the
choice of the local convergence (or any other scalar quantity) is crucial. The distortion is
intrinsically irrelevant since its third moment, for obvious symmetry reasons, should vanish. The
first non-trivial moment would then be its kurtosis": not every candidate observable carries
a usable third moment. The convergence is singled out because its own symmetry does not kill it,
exactly the kind of per-observable screening this record's own exponent table performs for which
windowed-moment/ratio combinations survive a given symmetry or nuisance.

## Use in this record

This is the named precedent, in the strategy document's own words, for lensing skewness breaking
the Omega_m-sigma_8 degeneracy: one filtered (windowed) field's variance alone constrains a
degenerate combination of the power spectrum and Omega_0 (their P(k) Omega_0^1.5 scaling mixes
the two), and a second moment of the same filtered field, with a different power-law dependence on
the same two parameters (Omega_0^-0.8 versus Omega_0^1.5), breaks the degeneracy when the two are
used jointly. That is structurally identical to this record's own logic for combining moment
ratios with different exponents in the design knobs (S_0, w_0): no single windowed moment or ratio
resolves every nuisance, but two with different power-law sensitivities, taken together, can. The
paper's own caveat, that the redshift dependence is "large and could be a major concern for a
practical implementation", is the same caution this record's own MAIN_AIM guard raises about
biases that must be measured through the twin, not assumed away: a theoretically clean
degeneracy-breaking pair can still be dominated, in practice, by a nuisance neither moment was
designed to track.
