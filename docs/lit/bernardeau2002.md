---
citekey: bernardeau2002
type: article
authors:
  - Bernardeau, F.
  - Colombi, S.
  - Gaztañaga, E.
  - Scoccimarro, R.
title: 'Large-Scale Structure of the Universe and Cosmological Perturbation Theory'
journal: Physics Reports
volume: 367
pages: 1--248
year: 2002
doi: 10.1016/S0370-1573(02)00135-7
arxiv: 'astro-ph/0112551'
pdf: PDF_papers/Bernardeau_2002_large-scale-structure-cosmological-perturbation-theory-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/bernardeau2002.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, every TOC page/section pairing and the abstract quote verified exactly
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1 and 3-4 of the held PDF (arXiv:astro-ph/0112551v1, 27 Dec 2001) read directly on
    2026-09-21: title, author list, abstract, and the table of contents (pages 3-4 of the PDF,
    covering the review''s Sections 4-6 headings and subheadings). The review''s actual technical
    content (its remaining roughly 244 pages) was NOT read; this note is a map of what the review
    covers, sourced from its own table of contents, not a verification of any formula inside it.'
verified_date: 2026-09-21
summary: >
  A 248-page review consolidating, in one document with its own section numbering, essentially
  every cosmology item this search cluster was asked to fetch: the density-field skewness and
  kurtosis under smoothing (Section 5.1-5.4, pp. 84-99, the juszkiewicz1993/bernardeau1994
  material), and the cosmic-bias/cosmic-error decomposition of counts-in-cells estimators
  (Section 6.2-6.7, pp. 129-169, the szapudi1996 material). Held as the single citable synthesis
  of the cosmology sub-cluster rather than a fifth primary source.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# bernardeau2002

VERIFIED only for the abstract (p. 1) and the table of contents (pp. 3-4 of the PDF). What follows
maps the review's structure and does not check any equation inside it.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rept. **367**, 1-248 (2002) | Crossref lookup, 2026-09-21, exact title match |
| affiliations | SPhT Saclay, IAP Paris, INAOE / IEEC Barcelona, New York University & IAS Princeton | p. 1 |
| relevant sections (from the table of contents, pp. 3-4) | Sec. 5.1 "The Density Field Third Moment: Skewness" (p. 84, with 5.1.2 "The Smoothed Case" p. 85 and 5.1.3 "Physical Interpretation of Smoothing" p. 86). Sec. 5.2 "The Fourth-Order Density Cumulant: Kurtosis" (p. 89). Sec. 5.4 "The Density Cumulants Hierarchy" (p. 91). Sec. 6.2.1 "Cosmic Bias and Cosmic Error" (p. 132). Sec. 6.7.5 "Cosmic Error and Cosmic Bias of Cumulants" (p. 159) | pp. 3-4 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "We review the formalism and applications of non-linear perturbation
theory (PT) to understanding the large-scale structure of the Universe. We first discuss the
dynamics of gravitational instability, from the linear to the non-linear regime... We then cover
the basic statistical tools used in cosmology to describe cosmic fields, such as correlations
functions in real and Fourier space, probability distribution functions, cumulants and generating
functions. In subsequent sections we review the use of PT to make quantitative predictions about
these statistics according to initial conditions, including effects of possible non Gaussianity of
the primordial fields. Results are illustrated by detailed comparisons of PT predictions with
numerical simulations. The last sections deal with applications to observations. First we review
in detail practical estimators of statistics in galaxy catalogs and related errors, including
traditional approaches and more recent developments... and some applications to weak gravitational
lensing."

The table of contents, read directly instead of inferred, confirms the review's Section 5
("From Dynamics to Statistics: The Local Cosmic Fields", starting p. 84) walks through exactly the
skewness/kurtosis/hierarchy sequence this cluster's other three cosmology papers (juszkiewicz1993,
bernardeau1994, and by extension bernardeau1997's application of the same statistics to lensing)
each cover individually, and its Section 6 ("From Theory to Observations: Estimators and Errors",
starting p. 129) contains a subsection literally titled "Cosmic Bias and Cosmic Error" (6.2.1, p.
132) and "Cosmic Error and Cosmic Bias of Cumulants" (6.7.5, p. 159), the szapudi1996 material,
generalized to arbitrary cumulant order.

## Use in this record

Not a fifth independent source: a single, dated, citable synthesis of the entire cosmology
sub-cluster (juszkiewicz1993, bernardeau1994, szapudi1996, and the statistical toolkit
bernardeau1997 applies), useful specifically because it gives each piece its own numbered section
in one document, so a reader of this record's own novelty argument can be pointed at one review
instead of four original papers, and because its Section 6 explicitly generalizes the
finite-sample bias-and-error decomposition to cumulants of any order, not only the second and
third: the same generalization this record's own moment ladder makes (mu_2 and mu_3 to mu_12 and
beyond) relative to the classical centroid-and-width analysis. Because only the abstract and table
of contents were read, only the claim that the review covers these topics with these section
headings is supported here, not any specific formula inside them. A claim resting on a formula from
this review needs its own page read first.
