---
citekey: bernardeau1994
type: article
authors:
  - Bernardeau, Francis
title: 'The Effects of Smoothing on the Statistical Properties of Large-Scale Cosmic Fields'
journal: Astronomy & Astrophysics
volume: 291
pages: 697--712
year: 1994
doi: null
arxiv: 'astro-ph/9403020'
pdf: PDF_papers/Bernardeau_1994_Sp-cumulant-hierarchy-tophat-smoothing.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/bernardeau1994.md  # line-by-line against the held PDF, 2026-09-22; pp.1-5 confirmed exactly, and pp.12-13 additionally read to settle juszkiewicz1993's open question about the log-derivative form of S3
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-5 of the held PDF (arXiv:astro-ph/9403020v1, 10 Mar 1994, "Submitted to Astronomy
    & Astrophysics") read directly on 2026-09-21: title, abstract, Section 1 (Introduction),
    Section 2.1 (Definition of the cumulants) and Section 2.2 (Large-scale behaviour of the
    cumulants) through the generating-function/spherical-collapse relation (their eq. 12-14).
    Section 3 onward (the top-hat smoothing derivation itself, which is the paper''s main new
    result per its own abstract) was NOT read, so the actual smoothing formulas are unverified
    here.'
  - 'No DOI is printed on the preprint and a Crossref bibliographic/title search on 2026-09-21
    returned no matching DOI for this A&A 291 (1994) article; VERIFY at submission whether EDP
    Sciences has since backfilled one.'
  - 'AUDIT, 2026-09-22: pages 12-13 (within the still-otherwise-unread Section 3) additionally
    read, specifically to check the juszkiewicz1993 note''s open question about a logarithmic-
    derivative form of S3. Confirmed: eq. (42), p. 12, defines gamma_p = d^p log sigma^2(R_0) /
    d log^p R_0; the unnumbered display opening Section 3.3 "Example of cumulants", p. 13, gives
    S_3 = 34/7 + gamma_1 (and S_4 through S_7 in gamma_1, gamma_2, gamma_3). No other part of
    Section 3 (the top-hat smoothing derivation proper, eq. 15-41, or Section 3.4 onward) was
    read; this remains unverified here beyond eq. 41-42 and the S_p-in-gamma_p series of p. 13.'
verified_date: 2026-09-21
summary: >
  Defines the hierarchical amplitude S_p(a) = lim_{<delta^2> -> 0} <delta^p>_c / <delta^2>^(p-1),
  the amplitude-free ratio of the p-th cumulant to the variance to the (p-1) power (their eq. 9),
  and states the paper's purpose as deriving "the whole series of the S_p parameters when the
  density field is smoothed with a top-hat window function" (abstract) -- the paper the strategy
  document's "cosmology's hierarchical amplitudes S_n = kappa_n/kappa_2^(n-1)" line names.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# bernardeau1994

VERIFIED for pages 1-5 (title through the cumulant generating-function formalism), plus pages
12-13 read separately on 2026-09-22 (audit) for the one specific result below. The paper's own
central result, the top-hat smoothing corrections to S_p in closed form, eq. 15-41, sits in
the rest of Section 3 and was not read. Nothing below quotes or draws on that derivation.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | A&A **291**, 697-712 (1994) | Crossref bibliographic lookup, 2026-09-21, not printed on the preprint itself |
| affiliation | CITA, 60 St George St., Toronto, Ontario | p. 1 |
| S_p definition | S_p(a) = <delta^p>_c / <delta^2>^(p-1), in the limit <delta^2> -> 0 | p. 5, eq. 9 |
| cumulant recursion | <delta>_c=0, <delta^2>_c=<delta^2>=sigma^2, <delta^3>_c=<delta^3>, <delta^4>_c=<delta^4>-3<delta^2>_c^2, <delta^5>_c=<delta^5>-10<delta^2>_c<delta^3>_c | p. 3, Section 2.1 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "It has been shown that the large-scale correlation functions of the
density field (and velocity divergence field) follow a specific hierarchy in the quasilinear
regime and for Gaussian initial conditions (Bernardeau 1992). The exact relationships between the
cumulants of the probability distribution functions (the so-called S_p parameters) are however
sensitive to the smoothing window function applied to the fields. In this paper, I present a
method to derive the whole series of the S_p parameters when the density field is smoothed with a
top-hat window function. The results are valid for any power spectrum and any cosmological
parameters... The resulting shapes of the one-point probability distribution functions of the
cosmic density and the velocity divergence fields are given as a function of the power spectrum
and Omega... Comparisons with numerical simulations prove these analytical results to be extremely
accurate."

Section 2.1 (p. 3) gives the general cumulant-from-moment recursion (table above) and states that
it is worth noticing that rho/rho-bar and delta have the same cumulants. Section 2.2 (pp. 3-5)
shows each cumulant's leading term scales as <delta^2>^(p-1), so the ratio S_p tends to a finite,
time-and-smoothing-scale-independent limit (eq. 9, p. 5) that is closely related to the vertices
nu_p of perturbation theory and obeys a closed generating-function relation to the spherical
collapse dynamics (eq. 10-14): the density contrast field's cumulant hierarchy, at leading order,
is exactly the Taylor series of a single nonlinear function (the spherical-collapse density
contrast as a function of linear overdensity).

## The logarithmic-derivative form of S_3 (audit, 2026-09-22)

Read specifically to settle a question raised while auditing juszkiewicz1993's note: which paper,
if either, gives S_3's dependence on the smoothing scale through an explicit logarithmic
derivative instead of through R/R_c or the spectral index n. This one does. Eq. (42), p. 12,
defines the p-th logarithmic derivative of the variance with the smoothing scale,
gamma_p = d^p log sigma^2(R_0) / d log^p R_0 (no leading minus sign), and the unnumbered display
immediately below it, opening Section 3.3 "Example of cumulants" (p. 13), gives
S_3 = 34/7 + gamma_1, with S_4 through S_7 given as longer polynomials in gamma_1, gamma_2,
gamma_3. juszkiewicz1993's own eq. 13 (S_3 = 4 + 4*kappa(Omega) - (3+n) for a power-law top-hat
case) is the same content in different variables: since d ln sigma^2/d ln R = -(n+3) for a
top-hat-windowed power-law spectrum, gamma_1 = -(n+3) and 34/7 + gamma_1 = 34/7 - (3+n), matching
juszkiewicz1993's eq. 13 at Omega=1 exactly. Section 3.3 also notes (p. 13) that the first two
coefficients have already been given by Bernardeau (1994b) from a direct calculation using
perturbation theory up to the third order, i.e. this Section 3.3 result and juszkiewicz1993's
own eq. 13 were cross-checked against each other by their own authors at the time.

## Use in this record

This is the paper that names and defines the hierarchical amplitude S_p = kappa_p/kappa_2^(p-1)
the strategy document's section 5.2 cites by that exact combination, and its own abstract states
the research programme this record's own moment-ladder work is the closest thing to outside
cosmology: derive the whole series of amplitude-free cumulant ratios under a specific window
(there, top-hat in real space, and here, a truncated frequency band), for any spectrum/model, and
validate the closed forms against a direct simulation: comparisons with numerical simulations
prove these analytical results to be extremely accurate, in the paper's own words (p. 1, abstract).
That three-part structure, (1) define
amplitude-free ratios of cumulants to remove the overall normalization, (2) derive their window
dependence in closed form instead of fitting it, (3) validate the closed form against simulated
realizations, is the same three-part structure this record's own `ladder_gate` and
`docs/methods/11_the_window_limits.md` programme follows for the truncated-window limits of its
own moment ratios (mu_4/mu_2^2, mu_3^2/mu_2^3, mu_1^3/mu_3, mu_5/mu_3). The physics is unrelated
(gravitational clustering vs. an atomic lineshape's light-shift distribution). This record's own
combination of an amplitude-free hierarchy, a derived window correction and simulation validation
is the borrowed structure, and predates this record's own version by three decades.
