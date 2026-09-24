---
citekey: villaverde2021
type: article
authors:
  - Villaverde, Alejandro F.
  - Massonis, Gemma
title: 'On testing structural identifiability by a simple scaling method: relying on scaling symmetries can be misleading'
journal: PLoS Comput. Biol.
volume: 17
number: 10
pages: e1009032
year: 2021
doi: 10.1371/journal.pcbi.1009032
arxiv: null
pdf: PDF_papers/Villaverde_2021_scaling-symmetries-misleading-identifiability.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/villaverde2021.md  # line-by-line against the held PDF, 2026-09-22: extended verify_flags to record the References-list confirmation that ref. [1] is castro2020, the basis for the summary's own attribution (previously outside the disclosed read-scope); all other claims and the FitzHugh-Nagumo equations confirmed exactly
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published open-access formal comment. Read on 2026-09-22:
    abstract, definitions, the description of the SIM test and the first
    counter-example (FitzHugh-Nagumo) up to its scaling equations. The second
    counter-example was not read. The References list (p. 7) was additionally read
    to confirm ref. [1] is castro2020 (Castro M, de Boer RJ, PLOS Comput. Biol.
    16(11):e1008248, 2020).'
verified_date: 2026-09-22
summary: >
  Formal comment on castro2020. The scaling-invariance test detects only scaling
  symmetries. A model whose only symmetries are of another kind is declared
  identifiable and observable when it is not. So the existence of a scaling invariance
  proves non-identifiability, but its absence proves nothing. Shown on the
  FitzHugh-Nagumo model and a second example.
loci:
  - methods/06
section: method-anchors
---

# villaverde2021

VERIFIED for the sections named in the flags. Held (published version). Read on 2026-09-22.

## What it says

Symmetries of a model's equations permit transformations of parameters and states that leave the output unchanged, and whatever they move is unidentifiable or unobservable. The scaling-invariance test searches for one family only, scalings. It gives the right answer if a model has only scaling symmetries or none. It wrongly returns identifiable when the model's symmetries are of another kind. The comment cites castro2020's own acknowledgement that the test finds one type of symmetry, related to scale invariance, and objects to its broader claim. The first counter-example is FitzHugh-Nagumo with only x1 observed (Eqs. 1-3), where the scaling equations (Eqs. 4 onward) return factors of one while the literature shows a non-scaling symmetry.

## Use in this record

- A necessary caution on the knob table. The exponent analysis finds every scaling degeneracy of a monomial model, which is most of what this record's forward model has. It cannot certify identifiability where terms are not monomials: the saturation law, the hypergeometric line shapes, the transit kernel and window truncation. There the twin's closure test, injecting and recovering, is the check, and the table is not. This matches the rule file's ladder: a table first, then the twin to price and test it.

## Limits

- A short formal comment. The second counter-example was not read here.
