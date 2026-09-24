---
citekey: castro2020
type: article
authors:
  - Castro, Mario
  - de Boer, Rob J.
title: 'Testing structural identifiability by a simple scaling method'
journal: PLoS Comput. Biol.
volume: 16
number: 11
pages: e1008248
year: 2020
doi: 10.1371/journal.pcbi.1008248
arxiv: null
pdf: PDF_papers/Castro_2020_structural-identifiability-scaling-method.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/castro2020.md  # line-by-line against the held PDF, 2026-09-22: Eqs. 1-13, Table 1 and the elasticity-matrix definition confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published open-access article. Read on 2026-09-22: abstract,
    Introduction and the Method section through Box 1. The worked biological examples
    and the comparison with other methods were not read. Read beside villaverde2021,
    which qualifies its central claim.'
verified_date: 2026-09-22
summary: >
  The scaling-invariance method (SIM) for structural identifiability. Scale each
  unknown parameter and latent variable by an unknown factor, equate each functionally
  independent term of the model to its scaled version, and solve the resulting sparse
  equations for the factors. Any solution other than all factors equal to one is a
  scaling symmetry, and the parameters it moves are unidentifiable. The elasticity
  matrix d log x / d log lambda has linearly dependent columns exactly there. Simple
  enough to do by hand, and the same linear algebra on exponents as this record's
  knob table.
loci:
  - methods/06
section: method-anchors
---

# castro2020

VERIFIED for the sections named in the flags. Held (published version). Read on 2026-09-22.

## What it does

Structural identifiability, whether parameters can be recovered from noiseless data at all, is distinguished from practical identifiability, which depends on the data (Introduction). In the sensitivity-matrix language, identifiability needs linearly independent columns, each with at least one large entry. The method works with the elasticity matrix K_ij = d log x_i / d log lambda_j (Eq. 4). Two examples fix the idea. In dx/dt = -lambda1 lambda2 x only the product is identifiable: scaling lambda1 -> u lambda1 and lambda2 -> lambda2/u leaves the solution unchanged and makes the two columns of K proportional (Eqs. 1-8). Adding a constant immigration term breaks the symmetry, and both become identifiable (Eq. 9). The general procedure (Box 1) decomposes each equation into functionally independent terms (Eq. 12, Table 1), scales every unknown parameter and unobserved variable, and requires each term to be invariant.

## Use in this record

- The same move as the rule file's rule that a knob question is answered first by a table of every term against the knob. When every term is close to a monomial in the knobs, a nuisance-free combination is a solution of a linear system in the exponents. This paper is a published, peer-reviewed statement of that method in another field, and a citation for it.
- Its worked examples show a symmetry broken by adding a term with a different structure: immigration against death. That is the logic of adding a platform or a knob that moves one term and not another.

## Limits

- It finds scaling symmetries only. villaverde2021 shows that non-scaling symmetries can make a model unidentifiable while this test declares it identifiable. The absence of a scaling symmetry is necessary for identifiability, not sufficient.
