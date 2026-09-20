---
citekey: klimov2001
type: article
authors:
  - Klimov, V. V.
  - Ducloy, M.
  - Letokhov, V. S.
title: 'Spontaneous emission of an atom in the presence of nanobodies'
journal: Quantum Electronics
volume: 31
number: 7
pages: '569--586'
year: 2001
doi: 10.1070/QE2001v031n07ABEH002007
arxiv: null
pdf: PDF_papers/Klimov_2001_spontaneous-emission-near-nanobodies-QE-english.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 and 2 (of 18) read against the PDF on 2026-09-20: the abstract,
    table of contents, and the start of Sec. 2 (the classical Purcell/cavity
    -QED framing). Secs. 3-6, which carry the microsphere, cylinder,
    spheroid and cone results the table of contents lists, are not read.
verified_date: null
summary: >
  A review, translated into English from Kvantovaya Elektronika, of how a
  nearby sub-wavelength dielectric or conducting body changes an atom's
  spontaneous-emission rate, for a microsphere, an infinite cylinder, a
  prolate spheroid, and a conducting cone. It carries no Rb 5S-6S content,
  but its infinite-cylinder case is the immediate theoretical predecessor
  of the same authors' later nanofibre-specific paper already in this
  literature set (klimovducloy2004), and the orientation-dependent
  enhancement/inhibition result it states is the general form of the
  Purcell-factor physics this repository's nanofibre addendum would need.
loci: []
section: method-anchors
---
# klimov2001

A companion file, `Klimov_2001b_spontaneous-emission-near-nanobodies-KvantElektr-russian.pdf`,
holds the original Russian-language Kvantovaya Elektronika printing of this
same review. The English Quantum Electronics translation above is the one
held and described below.

## Values

| field | value | where in the paper |
|---|---|---|
| decay-rate enhancement, dipole normal to surface, near a nanocylinder or spheroid pole | tens to hundreds of times the free-space rate | p. 1, abstract |
| decay-rate enhancement, particular (negative) dielectric constants | up to 1e5-1e6 times or more | p. 1, abstract |
| decay behaviour, dipole tangential to the nanobody surface | substantially slowed relative to free space | p. 1, abstract |
| original journal / translation | Kvantovaya Elektronika 31 (7) 569-586 (2001); English translation, Quantum Electronics 31 (7) 569-586 (2001) | p. 1 |
| received date | 19 January 2001 | p. 1 |
| review's shape-by-shape structure | Sec. 3 dielectric microsphere; Sec. 4 infinite circular cylinder; Sec. 5 dielectric prolate spheroid; Sec. 6 perfectly conducting cone | p. 1, contents |

## What it says, in its own terms

A review of how a nearby sub-wavelength dielectric or conducting body (a
"nanobody") modifies the spontaneous-emission rate of a nearby excited atom,
worked out in both classical electrodynamics (the radiative back-reaction on
an oscillating dipole, and the far-field energy flux) and a quantum
-mechanical formalism, for several canonical shapes in turn: a dielectric
microsphere, an infinite dielectric circular cylinder, a dielectric prolate
spheroid, and a perfectly conducting cone. The result stated in the
abstract is that the orientation of the atomic transition dipole relative to
the nanobody's surface controls the sign of the effect: a dipole oriented
normal to the surface, near a nanocylinder or at a spheroid's pole, can
decay tens to hundreds of times faster than in free space, and for
particular negative dielectric constants (surface-plasmon-like resonances)
the enhancement can reach five to six orders of magnitude, while a dipole
oriented tangential to the surface instead decays more slowly than in free
space. The review also treats absorbing, dispersive media explicitly,
showing that the nonradiative-decay channel grows substantially once the
nanobody has loss.

Because the review proceeds shape by shape, its infinite-circular-cylinder
section (Sec. 4) is the closest treatment here to an atom near a bare
dielectric fibre, one step before the same authors' later paper specific to
a step-index nanofibre (docs/lit/klimovducloy2004.md, Phys. Rev. A 69,
013812 (2004)), and together the two form a single lineage running from the
general nanobody problem to the guided-mode nanofibre case.

## What it is worth here

This repository's programme is a vapour cell first and a nanofibre addendum
second, and the addendum's spontaneous-emission and Purcell-factor physics
near a sub-wavelength dielectric cylinder is exactly this review's subject,
one step upstream of the more specific 2004 nanofibre calculation already
in this literature set. It carries no Rb 5S-6S content and no number to
import directly, but it is the right general reference for why an atom's
decay rate and branching depend on its dipole orientation relative to a
nearby fibre surface.
