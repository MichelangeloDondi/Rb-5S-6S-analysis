---
citekey: vandermarel1993
type: article
authors:
  - van der Marel, Roeland P.
  - Franx, Marijn
title: 'A New Method for the Identification of Non-Gaussian Line Profiles in Elliptical Galaxies'
journal: The Astrophysical Journal
volume: 407
pages: 525--539
year: 1993
doi: 10.1086/172534
arxiv: null
pdf: PDF_papers/VanDerMarel_1993_Gauss-Hermite-line-of-sight-velocity-non-Gaussian-line-profiles.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/vandermarel1993.md  # line-by-line against the held PDF, 2026-09-22; two page citations off by one fixed (526->527, twice), and a silently-dropped parenthetical now marked; the Gauss-Hermite-orthogonality question is confirmed already phrased as a question, not a claim
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-4 (the paper''s own pp. 525-528) of the held PDF, a NASA ADS scanned reproduction of
    the published ApJ pages (no arXiv preprint was found for this paper; astro-ph submission was
    not yet universal in 1992-1993), read directly on 2026-09-21: title, abstract, introduction,
    Section 2.2 (The Line Profile as a Sum of Orthogonal Functions) through the correlation
    matrix and the rms-deviation definition (their eq. 3-14). Sections 3-4 (the application to the
    three observed galaxies IC 1459, NGC 1374, NGC 4278, and the discussion) were NOT read.'
verified_date: 2026-09-21
summary: >
  Introduces the Gauss-Hermite series as a parametrization of a galaxy's line-of-sight velocity
  distribution (its spectral line profile): a best-fit Gaussian (line strength, mean velocity,
  dispersion) plus an orthogonal-function expansion in h3, h4, ... whose lowest orders measure
  antisymmetric (h3) and symmetric (h4) departures from Gaussian, explicitly constructed so the
  shape coefficients are only weakly correlated with the Gaussian parameters and with each other.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# vandermarel1993

VERIFIED for the paper's own pages 525-528 (title through the correlation-matrix and rms-deviation
formalism). The application to real galaxy spectra (pp. 529-539) was not read.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | ApJ **407**, 525-539 (1993 April 20) | p. 525 masthead |
| affiliations | Sterrewacht Leiden; Harvard-Smithsonian CfA | p. 525 |
| the series | L(v) = [gamma*alpha(w)/sigma] * sum_{j=0}^N h_j H_j(w), w = (v-V)/sigma | p. 527, eq. 5 |
| lowest-order deviation parameters | h_3 (odd, antisymmetric deviation), h_4 (even, symmetric deviation) | p. 525 abstract; p. 527 text below eq. 6 |
| rms deviation from best-fit Gaussian | D = (sum_{j>=3} h_j-hat^2)^(1/2) | p. 528, eq. 14 |

## What it says, in its own terms

Abstract (verbatim, p. 525): "It is usually assumed that the line profiles (i.e., the
distributions of stars over line-of-sight velocities) of elliptical galaxies have Gaussian shapes,
characterized by a line strength gamma, mean radial velocity V, and velocity dispersion sigma. We
relax this unnecessarily restrictive assumption and propose a decomposition of the line profile
into orthogonal functions: the Gauss-Hermite series. This series naturally leads to two extra
parameters that measure deviations of the line profile from a Gaussian: a parameter h3 measuring
asymmetric deviations and a parameter h4 measuring symmetric deviations... The new method is used
to derive line profiles for the elliptical galaxies IC 1459, NGC 1374, and NGC 4278. All three
galaxies have asymmetric line profiles on the major axis... By fitting Gaussians to these
asymmetric line profiles the amplitude of the rotation curve can be overestimated by 30% or more."

The paper's own stated design goal for the parametrization (p. 527, Section 2.2) is explicitly a
decorrelation goal: choosing the expansion point at the best-fit Gaussian's own (gamma, V, sigma),
which the paper states have the further advantage of being easy to obtain for real data, and the resulting correlation
matrix (eq. 11, p. 528) shows "the only zeroth-order correlation is that between gamma and sigma...
All other correlations are at least of order h_l (l in {3,...,6}), and thus generally small for
realistic line profiles... This constitutes a major advantage of the present parameterization over
most alternatives, such as, e.g., a decomposition of the line profile into the sum of two
Gaussians" (p. 528).

## Use in this record

The closest-worded analogue on the task's own list, and structurally one of the nearest of the
whole cluster: a line profile (there, a galaxy's line-of-sight stellar-velocity distribution, and here,
a two-photon absorption/fluorescence lineshape) is parametrized by its deviations from a Gaussian
through low-order shape coefficients (h3, h4, playing the same role this record's windowed
skewness- and kurtosis-type ratios play), explicitly engineered so the shape coefficients are
decorrelated from the location/scale parameters and from each other by construction (eq. 11).
That is the same goal this record pursues by choosing S0-free or w0-free ratios of moments, but
the method differs importantly and is worth naming as a live question instead of only a
precedent: Gauss-Hermite decorrelation is a property of the orthogonal basis itself (guaranteed by
eq. 6's orthogonality relation, valid for the true infinite series on an untruncated line), while
this record's moment-ratio correlations are not guaranteed by any orthogonality and must instead be
MEASURED through the twin, window by window. Whether a Gauss-Hermite-like reparametrization of a
truncated, windowed lineshape would reduce the correlated-bias problem this record's own twin
currently exists to measure is an open question this paper does not answer (its own convergence
theorem, p. 527, requires the line profile and its first two derivatives finite and continuous
with v^3*L_0(v) -> 0 as v -> +-infinity, conditions for an untruncated, well-behaved profile, not
proof of anything for a truncated one) but is a natural one to ask given how closely its stated
goal matches this record's own.
