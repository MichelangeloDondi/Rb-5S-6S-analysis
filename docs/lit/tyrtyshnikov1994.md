---
citekey: tyrtyshnikov1994
type: article
authors:
  - Tyrtyshnikov, Evgenij E.
title: 'How bad are Hankel matrices?'
journal: Numerische Mathematik
volume: 67
pages: 261--269
year: 1994
doi: 10.1007/s002110050027
arxiv: null
pdf: PDF_papers/Tyrtyshnikov_1994_Hankel-Vandermonde-matrix-conditioning.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/tyrtyshnikov1994.md  # partial-scope read checked against the PDF, 2026-09-22
author: agent
routing:
  - CITE
verify_flags:
  - 'Held and read: pp. 261-263 (abstract, introduction, Lemma 2.1) and pp. 266-269 (Lemma 3.3-3.4,
    Sect. 4 Vandermonde theorem, Sect. 5 Hankel theorem, closing remarks, references), 7 of 9
    pages. Pages 264-265 (the body of Sect. 3, Lemma 3.1-3.2, the base-case lower-bound technique
    for Krylov matrices) were not read; nothing below rests on them beyond the theorem statements
    that cite them. Cross-checked (independently, by the calling session): matches the
    identification "s002110050027.pdf = Tyrtyshnikov, Numer. Math. 67, 261 (1994)".'
verified_date: 2026-09-22
summary: >
  Proves worst-case exponential ill-conditioning for three families of matrices built from
  consecutive powers or moments: any real positive-definite Hankel matrix of order n has spectral
  condition number cond_2 >= 3*2^(n-6) (Theorem 5.1); a Krylov-basis matrix has cond_2 >=
  3^(1/2) 2^(n/2-3) (Lemma 3.4); a Vandermonde matrix V(x_1,...,x_n) with distinct nodes has
  cond_2 >= 2^(n-2)/n^(1/2), tightening to 2^(n-2) when all nodes lie inside or all outside the
  unit disk (Theorem 4.1-4.2). All three bounds hold for EVERY choice of (positive-definite/
  distinct) nodes, with no assumption on how they are distributed.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# tyrtyshnikov1994

VERIFIED for the sections named in the verify_flags: pp. 261-263 and 266-269 of this 9-page paper,
read directly against the held PDF.

## What it does

Evgenij E. Tyrtyshnikov (Institute of Numerical Mathematics, Russian Academy of Sciences, Moscow),
"How bad are Hankel matrices?", Numerische Mathematik **67**, 261-269 (1994). The abstract states
the three results directly:

> "Considered are Hankel, Vandermonde, and Krylov basis matrices. It is proved that for any real
> positive definite Hankel matrix of order n, its spectral condition number is bounded from below
> by 3*2^(n-6). Also proved is that the spectral condition number of a Krylov basis matrix is
> bounded from below by 3^(1/2)*2^(n/2-3). For V = V(x_1,...,x_n), a Vandermonde matrix with
> arbitrary but pairwise distinct nodes x_1,...,x_n, we show that cond_2 V >= 2^(n-2)/n^(1/2); if
> either |x_j| <= 1 or |x_j| >= 1 for all j, then cond_2 V >= 2^(n-2)." (p. 261)

The paper's own motivation (p. 261, Introduction): a code implementing three-term recurrences for
Hankel systems achieved good accuracy "only for very small, carefully chosen matrices," and rather
than blame the algorithm, the paper sets out to prove that no well-conditioned large test matrices
of this type exist at all: "perhaps the code is good, but there are no tasks that could be
resolved by it."

## The structural result linking the three (Lemma 2.1, p. 262)

An n x n matrix H is Hankel if h_ij = h_{i+j-2}. A matrix V = V(x_1,...,x_n) is Vandermonde if its
rows are the powers 1, x_i, x_i^2, ..., x_i^(n-1). Lemma 2.1 proves that any real positive-definite
Hankel matrix factors as H = V Lambda^2 V^T for some real Vandermonde matrix V and diagonal
Lambda: proved via the Cholesky factorization H = R^T R together with an upper-Hessenberg matrix
T constructed so that r_11^(-1) R = [e_1, Te_1, ..., T^(n-1)e_1], and T's own orthogonal
diagonalization T = Q^T X Q, X = diag(x_1,...,x_n), supplies the Vandermonde nodes. This
decomposition (Eq. 2.2) is the hinge the paper uses to derive the Hankel bound directly from the
Vandermonde/Krylov ones: cond_2 H = cond_2^2 (Lambda V^T) (p. 268, Eq. 5.2).

## The three theorems

Theorem 4.1 (Vandermonde, p. 267): for any real nonsingular Vandermonde matrix of order n,
cond_2 V >= 2^(n-2)/n^(1/2). Theorem 4.2 sharpens this to cond_2 V >= 2^(n-2) whenever all nodes
satisfy |x_j|<=1 or all satisfy |x_j|>=1. The paper compares this against prior bounds (Gautschi
and Inglese 1988) for two special node configurations, all-positive nodes, and symmetric nodes
x_j = -x_{n+1-j}, and notes its own general bound is tighter than the symmetric-node result for
n >= 7 (p. 268).

Theorem 5.1 (Hankel, p. 268), the paper's main result: "For any real positive definite Hankel
matrix H of order n, cond_2 H >= 3*2^(n-6)," proved in three lines directly from Lemma 2.1 (the
H = V Lambda^2 V^T decomposition) and Lemma 3.4 (the Krylov-matrix bound). The paper immediately
flags this as a floor, not the true asymptotic rate: "This theorem states that positive definite
Hankel matrices are ill-conditioned even for not very high orders. It is plausible that they are
indeed worse than suggested by (5.1)" (p. 268), citing a related family of Hankel matrices built
from the moments of a positive measure (h_{i+j-2} = integral x^{i+j-2} dξ(x), Eq. 5.4) for which
prior work (Taylor 1978) proved liminf_{n->inf} (cond_2 H_n)^(1/n) >= 4 (Eq. 5.5): the true
growth rate is conjectured to be 4^n, exponentially worse than the 2^n floor actually proved here.

Closing remarks (p. 269): for indefinite Hankel matrices the paper reports (by private
communication, G. Heinig) that cond_2 can be forced to diverge, but also exhibits a perfectly
conditioned indefinite Hankel matrix (the anti-diagonal exchange matrix J), and states the general
question, whether every leading submatrix of an indefinite Hankel matrix must eventually be
ill-conditioned, as open: "this still needs to be proved."

## Use in this record

A Hankel matrix is exactly the structure produced by stacking a distribution's own consecutive
power moments: filling H_ij = mu_{i+j-2} from a moment sequence mu_0, mu_1, ..., mu_{2n-2}
produces a positive-definite Hankel matrix whenever the moments come from a genuine positive
measure (the classical Hamburger/Stieltjes moment-problem matrix). This paper's Theorem 5.1 is a
rigorous, general proof that such a matrix's condition number grows at least like 2^n, and is
conjectured, citing prior work, to actually grow like 4^n, regardless of which specific
distribution the moments came from. It is a structural property of consecutive-moment stacking,
not a symptom of a particular estimator or a particular windowing choice.

This is a direct, external mathematical grounding for why this record's own programme of climbing
a high-order moment ladder (explicitly "much higher... let's say mu_12," per this record's own
programme note) must be read with the covariance of a raw, consecutive moment stack treated as
intrinsically, exponentially ill-conditioned once enough orders are included, independent of the
twin, the noise level, or the windowing. It supports, with a citable general bound instead of only
an empirical singularity, the record's design rule that coordinates for the joint likelihood are
chosen (by their twin bias per window) instead of accumulated as an unbroken run of consecutive
moment orders: a Hankel-like stack of many consecutive raw moments is close to the worst-conditioned
object this theorem describes, while a small, deliberately chosen set of ratios and combinations
(mu_5/mu_3, mu_1^3/mu_3, mu_4/mu_2^2, mu_3^2/mu_2^3, and their S0-bearing analogues) sidesteps the
Hankel structure the theorem's bound applies to.

## Limits

The theorem bounds a matrix built purely from the moment values (or, in the Vandermonde case, from
a set of nodes) with no additional structure. It says nothing by itself about the conditioning of a
covariance matrix built from estimated moments with correlated sampling noise, which is this
record's actual object of concern and would need its own derivation or numerical check. Pages
264-265 (Lemma 3.1-3.2, the Krylov-matrix base case the two main theorems build on) were not read
in this pass.
