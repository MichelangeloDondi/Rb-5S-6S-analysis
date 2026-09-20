---
citekey: derevianko2001
type: article
authors:
  - Derevianko, A.
  - Babb, J. F.
  - Dalgarno, A.
title: 'High-precision calculations of van der Waals coefficients for heteronuclear alkali-metal dimers'
journal: Phys. Rev. A
volume: 63
pages: 052704
year: 2001
doi: 10.1103/PhysRevA.63.052704
arxiv: null
pdf: PDF_papers/Derevianko_2001_van-der-Waals-coefficients-heteronuclear-alkali-dimers.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 (the derivation and the results Table I) read against the PDF on 2026-09-20.
    The remaining two pages (further discussion and the reference list) are not read.
verified_date: null
summary: >
  Extends the same group's high-precision homonuclear alkali-dimer van der Waals coefficients,
  the source of a record's own C6(Rb-Rb) constant held here as derevianko1999, to heteronuclear
  pairs -- Li, Na, K, Rb, Cs and Fr in every combination -- using relativistic ab initio dynamic
  polarizabilities and the Casimir-Polder integral, claiming about 1 percent uncertainty. A
  record's own rubidium self-broadening constant is homonuclear Rb-Rb and already comes from the
  companion 1999 letter, so the new heteronuclear numbers here (rubidium paired with a different
  alkali) are not currently in use, but are the natural reference if a foreign-alkali buffer-gas
  or mixed-vapour broadening term is ever added.
section: method-anchors
---
# derevianko2001

## Values

| field | value | where in the paper |
|---|---|---|
| method | relativistic ab initio dynamic polarizabilities + Casimir-Polder integral, Eq. (3) | p. 1 |
| claimed uncertainty | about 1% | p. 1, abstract |
| C6(Li-Rb) | 2545(7) a.u. | p. 2, Table I |
| C6(Na-Rb) | 2683(7) a.u. | p. 2, Table I |
| C6(K-Rb) | 4274(13) a.u. | p. 2, Table I |
| C6(Rb-Rb), homonuclear, cited from Ref. [15] (= derevianko1999) | 4691(23) a.u. | p. 2, Table I |
| C6(Rb-Cs) | 5663(34) a.u. | p. 2, Table I |
| C6(Rb-Fr) | 4946(44) a.u. | p. 2, Table I |
| C6(Li-Li), cross-check against a nonrelativistic variational calculation | 1389(2) a.u. here vs. 1393.39 (Ref. [22]) | p. 2 |

## What it says, in its own terms

The paper computes the van der Waals C6 dispersion coefficient, defined through
V_AB(R) = -C6_AB / R^6, for every heteronuclear pair drawn from the alkali-metal series Li, Na, K,
Rb, Cs and Fr, motivated by trap-loss and photoassociation experiments on mixed alkali vapours
(Na-K, Na-Rb, Na-Cs mixtures are named) and by proposals to search for a permanent electric dipole
moment using magnetically trapped Na-Cs or Na-K pairs. C6_AB is written as the frequency integral
of the product of the two atoms' dynamic dipole polarizabilities, the Casimir-Polder form (their
Eq. (3)), each polarizability built from a sum over intermediate states using high-precision
matrix elements and energies: experimental values for the principal (resonance) transitions,
all-order many-body values for a few more excited states, and Dirac-Hartree-Fock values for the
remaining valence-electron excitations.

The homonuclear coefficients on the diagonal of the results table (Table I) are taken from the
same group's earlier work (Ref. [15], the 1999 letter held here as derevianko1999). The new
content is the off-diagonal, heteronuclear entries. For lithium, where an independent
high-precision nonrelativistic variational calculation exists, the paper's own C6(Li-Li) = 1389(2)
agrees with the variational 1393.39 to about 0.3%, offered as a check on the method before it is
applied to the heavier, purely ab initio pairs. The paper also gives an approximate closed-form
combination rule (its Eq. (6)) that estimates a heteronuclear C6_AB from the two homonuclear
coefficients and the two atoms' principal-transition energy separations, without needing the full
calculation.

## What it is worth here

A rubidium self-broadening (beta_self) constant anchored in this record is built on the
homonuclear Rb-Rb coefficient, C6 = 4691(23) a.u., which this very paper states it is only
reproducing from its own 1999 predecessor (already held here as derevianko1999, which is where
the `C6_RB2_GROUND_LIT_AU` constant is attributed). This paper's actual new numbers -- rubidium
paired with lithium, sodium, potassium, caesium or francium -- are not currently used anywhere in
this record, since the vapour cell's own broadening is rubidium self-collision, not a
foreign-alkali mixture. They are the natural first place to look if a foreign-gas or mixed-alkali
broadening term, a buffer gas or a cross-contaminated cell, is ever added to the model.
