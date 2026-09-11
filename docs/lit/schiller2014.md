---
citekey: schiller2014
type: misc
authors:
  - Schiller, S.
  - Bakalov, D.
  - Bekbaev, A. K.
  - Korobov, V. I.
title: 'The static and dynamic polarisability, and the Stark and black-body radiation frequency shifts of the molecular hydrogen ions H2+, HD+ and D2+'
journal: arXiv preprint
volume: null
pages: null
year: 2014
doi: null
arxiv: 1404.3284
pdf: PDF_papers/Schiller_2014_polarisability-Stark-BBR-shifts-H2+-HD+-D2+.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  The molecular-ion counterpart of this record's polarizability chapter, read
  for method rather than for numbers. The DC Stark effect for H2+, HD+ and D2+
  is calculated per rovibrational AND per hyperfine state, the AC
  polarisabilities follow for several rovibrational levels, and the blackbody
  shift is evaluated from them including excited electronic states. The
  transferable point is the state resolution: a polarizability quoted for a
  transition hides a structure that a hyperfine-resolved calculation exposes.
loci: []
section: prior-art
---
# schiller2014

Held. Verified against the PDF, nineteen pages, on 2026-09-10.

## What it does

The DC Stark effect is calculated for three molecular hydrogen ions in the
non-relativistic approximation, in dependence on the rovibrational state AND on
the hyperfine state. AC polarisabilities follow for several rovibrational
levels, and from them the blackbody radiation shift is evaluated, including the
effects of excited electronic states.

## Why a rubidium two-photon record should hold it

**The state resolution is what transfers.** A polarizability quoted once per
transition hides whatever structure the hyperfine states carry. For two
J = 1/2 states the scalar term is genuinely common, so one number is
defensible, but this paper shows what the defence has to rule out: in a system
whose hyperfine states do carry a polarizability difference, the single number
conceals it entirely.

**And the blackbody route is the same route.** The AC polarisability is
computed and the thermal shift falls out of it, which is what
`run_transition_ladder.py` does per rung with a thermal occupation and a gap.
Seeing it done in a molecular system with excited electronic states included is
a check on the shape of the calculation rather than on any of its values.

## What it does not give

Nothing in it constrains a rubidium number, and no cell of this record should
cite it for one. It earns its place as a methodological comparator for how a
polarizability calculation is presented, state by state, with the systematic
it feeds named alongside.
