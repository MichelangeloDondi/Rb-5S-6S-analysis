---
citekey: varah2003
type: article
authors:
  - Varah, J. M.
title: 'Positive definite Hankel matrices of minimal condition'
journal: Linear Algebra Appl.
volume: 368
pages: 303-314
year: 2003
doi: 10.1016/S0024-3795(02)00685-7
arxiv: null
pdf: PDF_papers/Varah_2003_positive-definite-Hankel-minimal-condition.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/varah2003.md  # line-by-line against the held PDF (page images for Tables 1-3), 2026-09-22: all twelve condition-number figures confirmed exactly; one sourcing note added (Catalan's constant is not the paper's own name for its C0)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (Elsevier), downloaded by the owner by hand. Read in full on 2026-09-22, Sections 1 to 4 and Tables 1 to 3. Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The best a moment matrix can be. A real positive definite Hankel matrix, the matrix
  of moments mu_{i+j} of a positive measure, has a spectral condition number that grows
  exponentially with its order (Tyrtyshnikov; Beckermann's bounds give a rate
  gamma = exp(4C/pi), about 3.21 per order, C the paper's own alternating series, which
  is Catalan's constant though the paper does not name it so). The paper finds
  the minimally conditioned ones: they can be taken persymmetric with alternate zeros,
  the moment matrix of a measure symmetric about zero. Their condition numbers are
  computed up to order 16: 3, 5.83, 18.8, 44.9, 147 at orders 3 to 7, 3.2e4 at order
  12 and 2.9e6 at order 16. The ratio per order approaches gamma from below.
loci:
  - methods/06
  - methods/11
section: method-anchors
---

# varah2003

VERIFIED. Held (published version). Read in full on 2026-09-22.

## What it does

Section 1 recalls the lower bound: for n x n real positive definite Hankel matrices the minimal condition number lies between gamma^(n-1)/16n and gamma^n/2, with gamma = exp(4C0/pi), about 3.21, and C0 = 1 - 1/3^2 + 1/5^2 - ... (Beckermann 2000, after Tyrtyshnikov 1994). This alternating series is Catalan's constant, though the paper itself never uses that name for it. The minimal matrices are 3 at order 3 and 3 + 2 sqrt(2) at order 4. Section 2 proves that a minimally conditioned matrix can be taken persymmetric (Theorem 2.1) and with alternate zeros (Theorem 2.2). Its free entries must then decrease monotonically (Theorem 2.3), and its Vandermonde factorisation has nodes in plus-minus pairs with equal weights (Theorem 2.4). In moment language the best-conditioned moment matrix is that of a measure symmetric about zero, whose odd moments vanish.

Sections 3 and 4 compute the minima. The eigenvalues split between the odd and even submatrices (Theorems 3.1 and 4.1). Order 5 has the closed form 9 + 4 sqrt(6), about 18.8, and order 7 is 147.05, found numerically. Orders up to 15 (odd, Table 1) and 16 (even, Table 2) come from an iterative scaling of the Vandermonde factor and a direct search. The minimal condition numbers are 384.6 at order 8, 3459 at order 10, 32 035 at order 12, 104 655 at order 13 and 2 890 409 at order 16. Table 3's ratios, which match the square root of kappa_n/kappa_(n-2) from Tables 1 and 2, rise towards gamma (3.09 at order 16).

## Use in this record

- A floor on any quantity the programme builds from raw power moments. Moments mu_0 to mu_12 fill a 7 x 7 moment matrix, whose condition number cannot be below 147 whatever the line, and each further two orders multiply the floor by nine to ten. Centring the window on the line's centroid, as `docs/methods/11` does, moves the matrix toward the symmetric structure of the minimal ones. It cannot reach it, because the line's odd moments are the signal.
- The covariance of raw windowed moments is itself such a matrix. With independent noise per sample, Cov(M_i, M_j) is the sum over samples of nu^(i+j) times the sample's variance, a positive definite Hankel matrix. On a window symmetric about its centre, with a noise variance symmetric about it too, its odd and even orders decouple, which is the alternate-zero structure of the minimal matrices. For moments 0 to 12 its condition number is at least 104 655 (order 13, Table 1). The reviewer's arithmetic for a uniform window with white noise gives about 3e8 for the covariance and 8e7 for its correlation matrix. Whitening raw moments to mu_12 is therefore an inversion that amplifies errors in the estimated covariance, from finite twin replicas (hartlap2007), by up to that factor in the worst direction.
- The standard remedy, which this paper does not discuss: fit in a basis orthogonal on the window's own noise measure, such as the discrete orthogonal polynomials of the sample grid (Legendre moments in the continuum limit, for a uniform white-noise window). It carries the same information as the raw moments and has a diagonal covariance. This is an argument for the programme's choice of coordinates, not only a numerical detail. Correlated noise breaks the Hankel form of the covariance, so its conditioning has to be measured on the twin instead of bounded here.
- tagliani2001 bounds the same kind of matrix for measures on [0, 1] with moments taken about the edge, where the growth is far faster. The contrast is the case for centring.

## Limits

- A statement about the best case over all measures. It bounds a real moment matrix from below and says nothing about how far a given line sits above the floor. The condition number is spectral, which is not the same as the statistical information lost.
