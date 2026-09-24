---
citekey: tagliani2001
type: article
authors:
  - Tagliani, A.
title: 'Discrete probability distributions and moment problem: numerical aspects'
journal: Appl. Math. Comput.
volume: 119
number: 1
pages: 47-56
year: 2001
doi: 10.1016/S0096-3003(99)00228-3
arxiv: null
pdf: PDF_papers/Tagliani_2001_maximum-entropy-moment-problem-numerics.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/tagliani2001.md  # line-by-line against the held PDF (page images for Section 6), 2026-09-22: every equation (1.1-1.9, 2.3-2.8, 3.1-3.7, 4.2, 5.1-5.2, 6.1-6.14) and the Tyrtyshnikov/Taylor attributions confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (Elsevier), downloaded by the owner by hand. Read in full on 2026-09-22, Sections 1 to 6. The text layer drops minus signs and exponents in places, so the note states the bounds in words and by equation number and does not reproduce the determinant bound of Eq. (6.5). Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The numerical fragility of reconstructing a distribution from its moments by maximum
  entropy. For discrete distributions on [0, 1] constrained by the first M moments, a
  uniform relative error in all the moments changes the reconstruction by the same
  small amount, but an error in the highest moment alone is amplified by at least
  2^(2M-1) in root-mean-square relative terms, because the range of values the M-th
  moment can take shrinks exponentially with M. The Hankel matrix of the moments then
  has a condition number above 2^(4M-2). Newton's method for the Lagrange multipliers
  becomes unreliable when many moments are kept. The paper recommends fitting the
  multipliers so that the relative moment errors are equal, and warns that entropy
  estimates fail near the boundary of the moment space.
loci:
  - THEORY
  - methods/11
section: method-anchors
---

# tagliani2001

VERIFIED. Held (published version). Read in full on 2026-09-22.

## What it does

The object is a discrete distribution on N + 1 points in [0, 1] whose first M moments are assigned. The maximum-entropy solution is the exponential of a polynomial of degree M (Eq. 1.1), with the Lagrange multipliers fixed by the moment constraints (Eq. 1.2). Section 1 recalls the geometry: the moment space is a convex polyhedron, and once the first M - 1 moments are fixed the M-th can range only over an interval whose width is bounded by a power of two falling with M (Eq. 1.6), expressed through canonical moments (Eqs. 1.7-1.8). The Jacobian of the multipliers with respect to the moments is the inverse of the Hankel matrix of the moments (Eq. 1.9).

Section 2 propagates errors. If every moment carries the same relative error, the distribution changes by that relative error (Eqs. 2.3-2.5). If only the last moment changes, the change is carried by the M-th orthogonal polynomial of the distribution (Eqs. 2.6-2.7), and its mean-square size is at least 2^(4M-2) times the squared change (Eq. 2.8). Section 3 treats the entropy: it is stable under a uniform relative error, but its estimate becomes meaningless when the mass at the interval's edge tends to zero, as happens when the M-th moment approaches its extreme value (Eqs. 3.6-3.7). Section 4 shows that averages of bounded functions are stable under a uniform relative error of the moments (Eq. 4.2). Section 5 draws the practical conclusion: accurate multipliers are not needed, and they should be computed so that the relative errors between assigned and computed moments are equal, for instance by least squares, instead of by Newton's method on Eq. (1.2). Section 6 bounds the spectrum. It quotes Tyrtyshnikov's lower bound for any real positive definite Hankel matrix (Eq. 6.1) and Taylor's asymptotic rate of at least 16 per order for moment matrices on [0, 1] (Eq. 6.2). It derives, for its own class, a smallest eigenvalue below 2^-(4M-2) and a condition number above 2^(4M-2) (Eqs. 6.13-6.14).

## Use in this record

- The caution for any step that reconstructs the light-shift distribution f(s) from moments instead of fitting a forward model to them. A maximum-entropy reconstruction constrained by the moments up to mu_12 (M = 12) amplifies an error in mu_12 alone by at least 2^23, about 8e6, in root-mean-square relative terms. For the paper's class, the moment matrix holding mu_0 to mu_12 (order 7, M = 6) has a condition number above 2^22, about 4e6. The record's route, comparing each windowed statistic with its own forward prediction (`docs/methods/11`), avoids the inversion.
- The bounds are for moments taken about the interval's edge. varah2003 shows the best a symmetric, centred moment matrix of the same order can reach, 147 at order 7. The gap between the two, four orders of magnitude, is the case for self-centred windows.
- Section 5's recommendation, fitting the moments in the least-squares sense of their relative errors instead of solving the moment equations exactly, is a weighted fit, as the moment likelihood is. The likelihood's weights come from the noise, not from the moments' sizes.
- The failure of the entropy estimate near the boundary of the moment space is a reminder that moments near their extreme values, as for a nearly degenerate distribution, carry little stable information.

## Limits

- Discrete distributions on a fixed finite grid in [0, 1], maximum-entropy reconstructions only, and exact moments perturbed deterministically. It treats no noise model, no window and no estimator, and its bounds are for its own class of Hankel matrices, not all.
