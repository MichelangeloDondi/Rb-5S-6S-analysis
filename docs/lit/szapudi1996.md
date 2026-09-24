---
citekey: szapudi1996
type: article
authors:
  - Szapudi, István
  - Colombi, Stéphane
title: 'Cosmic Error and Statistics of Large-Scale Structure'
journal: The Astrophysical Journal
volume: 470
pages: '131'
year: 1996
doi: 10.1086/177855
arxiv: 'astro-ph/9510030'
pdf: PDF_papers/Szapudi_1996_cosmic-error-finite-volume-bias-higher-moments-simulation-calibrated.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/szapudi1996.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, all claims and quotes verified exactly
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-4 of the held PDF (arXiv:astro-ph/9510030, submitted 5 Oct 1995, "Submitted to
    Astrophysical Journal") read directly on 2026-09-21: title, abstract, Section 1
    (Introduction) and the start of Section 2 (General Formalism) through the factorial-moment
    generating functions (their eq. 1-6). Sections 3-6 (the hierarchical-model calculation, the
    explicit error formulas to fourth order, the Rayleigh-Levy simulation comparison, and the
    conclusions, pages 5-28) were NOT read, so no specific error formula or simulation result is
    used or quoted below beyond what the abstract states.'
verified_date: 2026-09-21
summary: >
  Decomposes the total statistical error on a moment measured from a finite galaxy survey into a
  measurement error (removable) and an irreducible "cosmic error" with three contributions --
  finite-volume, edge, and discreteness effects -- and validates the theoretical error formulas
  against a large number of simulated (Rayleigh-Levy) mock catalogues, finding the errors are
  systematically biased LOW when uncorrected. The paper the strategy document's "finite-volume
  bias of higher moments calibrated on simulations" line names.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# szapudi1996

VERIFIED for pages 1-4 (title through the general factorial-moment formalism). The explicit error
formulas and the simulation comparison (Sections 3-6) were not read. What follows describes only the
problem statement and the taxonomy of error sources given in the introduction.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | ApJ **470**, 131 (1996) | Crossref lookup, 2026-09-21, exact title match |
| affiliations | NASA/Fermilab Astrophysics Center; CITA Toronto | p. 1 |
| the three cosmic-error sources | finite volume effect, edge effect, discreteness effect | p. 1 (abstract) and p. 3 (Section 1) |
| factorial moments | F_k = <(N)_k> = sum_N (N)_k P_N, with (N)_k the k-th falling factorial | p. 4, eq. 1 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "We use a generating function approach to examine the errors on
quantities related to counts in cells extracted from galaxy surveys. The measurement error,
related to the finite number of sampling cells, is disentangled from the 'cosmic error', due to
the finiteness of the survey. Using the hierarchical model and assuming locally Poisson behavior,
we identified three contributions to the cosmic error: The finite volume effect is proportional to
the average of the two-point correlation function over the whole survey. It accounts for possible
fluctuations of the density field at scales larger than the sample size. The edge effect is
related to the geometry of the survey... The discreteness effect is due to the fact that the
underlying smooth random field is sampled with finite number of objects... To check the validity
of our results, we measured the factorial moments of order N<=4 in a large number of small
subsamples randomly extracted from a hierarchical sample realized by Raighley-Levy random walks.
The measured statistical errors are in excellent agreement with our predictions... 'cosmic errors'
tend to be systematic: it is likely to underestimate the true value of the... factorial moments."

Section 1 (p. 3) states plainly why higher moments specifically are the hard case: "it is"
difficult "to measure and interpret the N-point correlation functions, especially when N >= 5,
mostly because of the large number of parameters involved. In particular, the expected
uncertainties on the measurements are rather" difficult to estimate, and that the alternative to
costly repeated N-body realizations is "a full scale analytic calculation" (p. 3), validated
after the fact against simulated mocks, not derived from them.

## Use in this record

This is the paper the strategy document's own *the finite-volume bias of higher moments
calibrated on simulations* line names, and its problem statement is close to a direct restatement
of this record's own truncated-window ladder problem: a moment of a field (there, galaxy counts in
survey cells, and here, a spectral lineshape in a truncated frequency window) measured over a finite
sampling domain carries a bias relative to its infinite-domain value, the bias is systematic (their
own words: it "tend[s] to... underestimate the true value") instead of a symmetric statistical
error, and the theoretical bias formula is checked against many independent simulated realizations
before being trusted, exactly this record's own noise/window ladder gate. The specific mechanism
differs, their *cosmic error* is a survey-VOLUME truncation of a spatial field, this record's is
a frequency-WINDOW truncation of a spectral line, but the three-way decomposition itself (a
finite-domain bias from long-range correlations entering and leaving the sample, a geometry/edge
term from how the domain boundary interacts with what is counted near it, and a discreteness/shot-noise
term from finite sampling) is a useful taxonomy to check this record's own window-limit derivations
against: the "edge effect... related to the geometry of the survey" is the nearest published
analogue to whatever a truncated frequency window's own boundary terms turn out to be.
