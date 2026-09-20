---
citekey: dzuba2012
type: article
authors:
  - Dzuba, V. A.
  - Flambaum, V. V.
  - Roberts, B.
title: 'Calculation of the parity-violating 5s-6s E1 amplitude in the rubidium atom'
journal: Phys. Rev. A
volume: 86
pages: 062512
year: 2012
doi: 10.1103/PhysRevA.86.062512
arxiv: null
pdf: PDF_papers/Dzuba_2012_parity-violating-5s-6s-E1-amplitude-rubidium.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 to 3 (abstract, introduction, the RPA / Brueckner-orbital method, and the results
    Tables I-IV through the neutron-skin discussion) read against the PDF on 2026-09-20. The
    remainder of the discussion and the conclusion are not read.
verified_date: null
summary: >
  A relativistic many-body (RPA plus Brueckner-orbital correlation-potential) calculation of the
  parity-violating 5s-6s electric-dipole transition amplitude in rubidium, the same 5s-6s pair a
  rubidium spectroscopy record addresses, reporting the spin-independent amplitude to about
  0.4-0.5 percent and, as a by-product, ordinary 5s-5p E1 matrix elements and 5s/6s energies and
  hyperfine constants checked against experiment to 0.1-0.6 percent. It argues rubidium is a
  competitive parity-violation target because its atomic-structure calculations can be more
  accurate than caesium's despite a parity-violating amplitude only seven times smaller. It is not
  a source of the ordinary (non-parity-violating) 5s-6s Stark-shift polarizability this kind of
  record needs, but it is a precision anchor for the same atom's 5s/6s energies, hyperfine
  constants and nearby E1 matrix elements.
section: method-anchors
---
# dzuba2012

## Values

| field | value | where in the paper |
|---|---|---|
| spin-independent E_PNC, RPA + correlations only | 1.400 x 10^-12 i e a_B (-Q_W/N) | p. 2, Eq. (8) |
| spin-independent E_PNC, full (with Breit, QED, neutron skin) | 1.390 x 10^-12 i e a_B (-Q_W/N) | p. 3, Table III |
| Breit correction to E_PNC | -0.4% (Rb) vs. -0.6% (Cs) | p. 3, Table III |
| QED correction to E_PNC | -0.24(4)% (Rb) | p. 3 |
| neutron-skin correction to E_PNC | -0.06% (Rb) vs. -0.2% (Cs) | p. 3, Table III |
| correlation correction to E_PNC | 4% (Rb) vs. 2% (Cs) | p. 3, Table III |
| PNC amplitude ratio | the Rb amplitude is 7x smaller than the Cs amplitude | p. 1, Sec. I |
| 5s1/2 ionization energy, expt / calc | 33691 / 33666 cm^-1 | p. 2, Table I |
| 6s1/2 ionization energy, expt / calc | 13558 / 13509 cm^-1 | p. 2, Table I |
| 6s1/2 hyperfine constant A, expt / calc | 239.18(3) / 239.2 MHz | p. 2, Table I |
| 5s1/2-5p1/2 E1 reduced matrix element, expt / calc | 4.231(3) / 4.246 a.u. | p. 2, Table II |
| 5s1/2-5p3/2 E1 reduced matrix element, expt / calc | 5.977(4) / 5.994 a.u. | p. 2, Table II |
| stated accuracy of the calculations | about 0.1% (energies), 0.4-0.6% (hyperfine), 0.3% (E1 amplitudes) | p. 2 |

## What it says, in its own terms

The paper calculates the parity-nonconserving (PNC) electric-dipole transition amplitude for the
5s-6s transition in rubidium, motivated by the fact that atomic PNC measurements are currently
limited by the accuracy of the atomic-structure calculation needed to interpret them, not by the
measurement itself -- true even for caesium's benchmark PNC measurement, accurate to 0.35% against
a 0.4-0.5% theoretical uncertainty. Rubidium is proposed as a competitive alternative to caesium:
its PNC amplitude is only about seven times smaller, but because its lower nuclear charge means
smaller relativistic (Breit, QED) corrections and a smaller neutron-skin uncertainty, the
calculation itself can potentially be more accurate.

The method builds Brueckner orbitals for the valence 5s and 6s states from an all-order
correlation potential, then solves a self-consistent set of random-phase-approximation (RPA)
equations for the core's response to the weak-interaction and electric-dipole (laser) fields
simultaneously, giving the PNC amplitude as a sum of terms (their Eq. (6)) without ever needing the
ordinary (non-PNC) 5s-6s E1 matrix element itself, which is dipole-forbidden between two s-states
and proceeds only via mixing with p states. As a check on the method's accuracy, the same
machinery is used to compute ordinary quantities that do have direct experimental counterparts --
the 5s, 5p and 6s energies and hyperfine structure constants, and the 5s-5p E1 matrix elements --
finding agreement at the 0.1% (energies), 0.4-0.6% (hyperfine) and 0.3% (E1 matrix element) level
(Tables I-II). The final spin-independent PNC amplitude, corrected for Breit interaction, QED and
the nuclear neutron skin, is 1.390 x 10^-12 i e a_B(-Q_W/N) (their Eq. and Table III), with each
correction computed and compared side by side against the equivalent correction for caesium's
6s-7s PNC amplitude. A spin-dependent part, needed to extract the nuclear anapole moment, is also
calculated, not read here.

## What it is worth here

This is a precision theoretical anchor for the same 5s-6s pair of states a rubidium spectroscopy
record addresses, from an independent, well-benchmarked all-order relativistic many-body method --
its 5s1/2 and 6s1/2 energies, the 6s1/2 hyperfine constant, and the 5s-5p E1 matrix elements
(Tables I-II) are ordinary atomic-structure numbers with direct experimental counterparts a record
can check its own inputs against. What it does not give is the ordinary (non-parity-violating)
5s-6s static or dynamic polarizability or Stark-shift amplitude an AC-Stark ramp actually needs.
The parity-violating amplitude calculated here is a different, far smaller quantity computed for a
different purpose (searching for physics beyond the standard model), and none of its central
results transfer directly. It earns a CITE for its atomic-structure cross-checks on the 5s/6s
pair, not for its own headline PNC number.
