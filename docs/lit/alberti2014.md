---
citekey: alberti2014
type: article
authors:
  - Alberti, Andrea
  - Gambino, Paolo
  - Healey, Kristopher J.
  - Nandi, Soumitra
title: 'Precision determination of the CKM element Vcb'
journal: Physical Review Letters
volume: 114
pages: '061802'
year: 2015
doi: 10.1103/PhysRevLett.114.061802
arxiv: '1411.6560'
pdf: PDF_papers/Alberti_2014_Vcb-precision-global-moment-fit-semileptonic-B-decay.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/alberti2014.md  # line-by-line against the held PDF, 2026-09-22; one overclaim corrected (the paper does not bound mu_pi^2's scale sensitivity at <0.5%, only |Vcb| and m_b^kin)
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-3 of the held PDF (arXiv:1411.6560v2, 31 Jan 2015) read directly on 2026-09-21:
    title, abstract, introduction and the global-fit section through the results tables (their
    Tables I-III and Fig. 1-2). The derivation of the O(alpha_s Lambda^2_QCD/m_b^2) corrections
    themselves (cited to other papers, not reproduced here) was not read.'
verified_date: 2026-09-21
summary: >
  The successor, eight years later, to buchmueller2006's global moment fit: an expanded set of
  inclusive semileptonic B-decay moments, still fit jointly for a shared Heavy Quark Expansion
  parameter set, now including a newly completed order of corrections, reporting |Vcb| =
  (42.21 +/- 0.78)e-3 with chi^2/d.o.f. about 0.4 (p. 3). The "later global fit of moments with
  cuts" the task asked for alongside buchmueller2006.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# alberti2014

VERIFIED for pages 1-3 (title through the results tables and the scale-dependence figures). The
underlying perturbative calculation is cited, not reproduced, and was not read here.

## Values

<!-- not-from-pdf: the published-journal title in the row below is quoted from a Crossref
     bibliographic lookup, 2026-09-21, not from the held arXiv preprint's own title page. -->
| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rev. Lett. **114**, 061802 (2015). The published title reads "Precision Determination of the Cabibbo-Kobayashi-Maskawa Element Vcb", one word longer than the held preprint's own title page | Crossref lookup, 2026-09-21 |
| affiliations | Universita di Torino & INFN. Indian Institute of Technology, Guwahati | p. 1 |
| headline result | \|Vcb\| = (42.21 +/- 0.78) x 10^-3, m_b^kin(1 GeV) = (4.553 +/- 0.020) GeV | abstract, p. 1, and Table II, p. 2 |
| fit quality | "The chi^2/d.o.f. is very good, about 0.4." | p. 3 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "We extract the magnitude of the CKM matrix element Vcb and the most
relevant parameters of the Heavy Quark Expansion from data of inclusive semileptonic B decays."
The abstract goes on to say the calculation includes the recently completed O(alpha_s *
Lambda_QCD^2 / m_b^2) corrections and a careful estimate of the residual theoretical uncertainty,
and that, "using a recent determination of the charm quark mass, we obtain \|Vcb\| = (42.21 +/-
0.78) x 10^-3" and m_b^kin(1GeV) = (4.553 +/- 0.020) GeV (p. 1, both values also in the table
above).

The introduction states plainly that this is a refinement of the buchmueller2006-type analysis
made possible by new theory input: "In this Letter we focus on the inclusive extraction of
\|Vcb\|", including all contributions of the newly-completed O(alpha_s * Lambda_QCD^2/m_b^2)
corrections, "whose calculation has been recently completed [13-15], and discuss how this
improvement affects the results" (p. 1). The fit
itself is described as using "the semileptonic data listed in Table 1 of Ref. [8]" (the
buchmueller2006-lineage compilation) with updated inputs for the charm-quark mass and the
electroweak/theory uncertainties (p. 2), i.e. the same moment-compilation strategy, re-fit as
theory and world-average inputs improve, not a new observable.

## Use in this record

Two things this record can use beyond buchmueller2006 itself. First, a windowed-moment
global-fit programme in a mature field is not a one-shot analysis but an iterated one, re-run as
theoretical corrections and external inputs (here, an improved charm-mass determination) are
folded in, each iteration reporting the same kind of fit-quality statistic. Second, the explicit
number given for that statistic, "chi^2/d.o.f. is very good, about 0.4" (p. 3), is stated as
evidence the fit is not merely converged but well-calibrated: a value near unity, not far below or
above it, is treated as the marker of trustworthiness, the same reading this record's
own reduced-chi-squared admission tests apply to a windowed-moment joint fit. The paper's own
scale-dependence check (Fig. 2, p. 3) is a form of the same discipline this record's own
model-form grids apply: before trusting a fitted parameter, show it is insensitive to an arbitrary
theoretical choice that should not matter physically. The paper's own bound is narrower than that,
though: |Vcb| and m_b^kin, it states, "increase by less than 0.5% if we perform the whole analysis
using alpha_s(m_b/2)" (p. 3), while mu_pi^2 and the other OPE parameters are named as slightly
more sensitive than that. Only |Vcb| and m_b^kin are shown to sit under the 0.5% bound.
mu_pi^2 is explicitly named as more scale-sensitive than that, not as another parameter inside the
same bound.
