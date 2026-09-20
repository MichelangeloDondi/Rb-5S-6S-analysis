---
citekey: goldschmidt2015
type: article
authors:
  - Goldschmidt, E. A.
  - Norris, D. G.
  - Roller, S. B.
  - Wyllie, R.
  - Brown, R. C.
  - Porto, J. V.
  - Safronova, U. I.
  - Safronova, M. S.
title: 'Magic wavelengths for the 5s-18s transition in rubidium'
journal: Phys. Rev. A
volume: 91
pages: '032518'
year: 2015
doi: 10.1103/PhysRevA.91.032518
arxiv: null
pdf: PDF_papers/Goldschmidt_2015_magic-wavelengths-5s-18s-rubidium.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 read against the PDF on 2026-09-20. The magic-wavelength
    crossing plot, the dipole-trap light-shift measurement, and the full
    uncertainty budget in Secs. III-IV are not read, so this note's numbers
    stop at the introduction and the theoretical method section.
  - 2026-09-20: adversarial audit_B corrected four defects. The measured and calculated magic
    wavelengths sit in the introduction's body text, not the boxed abstract. The numerical-check
    row named one figure, 0.01-0.05%, for a comparison that actually reads 0.01% and 0.004%
    for the two named transitions, that figure belonging to a different check further down the
    same page. And the dominant-channel list named 18s-19p, drawn from an earlier predictive
    sentence, where Table I's own five channels are 18s-6p3/2, 17p1/2, 17p3/2, 18p1/2 and 18p3/2.
verified_date: null
summary: >
  A relativistic all-order calculation of magic wavelengths for the 5s-18s
  transition in rubidium near 1064 nm, checked against a light-shift
  measurement in a crossed-beam optical dipole trap. It is adjacent field for
  this repository: the transition, the Rydberg state, and the trapping
  application are unrelated to the 5S-6S line studied here. Its value is as a
  methodology anchor, since it is a published, worked example of the same
  all-order method family (and largely the same authorship) behind the
  atomic-structure inputs this repository's own polarizability work draws on,
  including a case where theory and a careful experiment still differ by a
  few standard deviations after both state their own uncertainty.
loci: []
section: method-anchors
---
# goldschmidt2015

## Values

| field | value | where in the paper |
|---|---|---|
| measured magic wavelength (near the 18s-6p3/2 resonance) | 1063.529(4) nm | p. 1, Introduction |
| calculated magic wavelength | 1063.514(4) nm | p. 1, Introduction |
| measured 6p3/2-18s transition wavelength | 1063.6278(2) nm | p. 1 |
| prior literature value for the same transition | 1063.627(1) nm | p. 1 |
| dominant matrix element at the magic wavelength, SDpT (final), 18s-6p3/2 | 0.1874 a.u., 0.8% uncertainty | p. 2, Table I |
| basis set | 150 B-spline orbitals per relativistic angular quantum number, spherical cavity R = 600 a0 | p. 2 |
| numerical check | 18s-6p and 18s-18p Dirac-Fock matrix elements agree to 0.01% and 0.004% respectively between the 500-point and 10 000-point integration grids | p. 2 |

## What it says, in its own terms

The paper computes magic wavelengths near 1064 nm for the 5s-18s two-photon
transition of rubidium, where a magic wavelength is one at which the ground
and excited state see the same ac Stark shift. Using a relativistic
all-order (linearized coupled-cluster) method with single-double and partial
triple excitations, the group locates the crossing of the 5s and 18s dynamic
polarizability curves and compares it with an experimental light shift
measured in a crossed-beam optical dipole trap operating near 1064 nm, in
the range used by standard high-power fibre amplifiers. The calculated
value, 1063.514(4) nm, differs from the measured value, 1063.529(4) nm, by
about 2.8 standard deviations (the two central values and their quoted
uncertainties are unambiguous in the text. The sigma count itself is stated
in a symbol the text extraction renders as a garbled character), which the
paper treats as a modest but real tension rather than agreement.

The calculation extends the all-order method, previously applied mainly to
low-lying states, to a highly excited Rydberg level (n = 18) by building a
large finite basis (150 B-spline orbitals per relativistic angular quantum
number, in a 600 a0 cavity) and checking its numerical stability against a
much finer integration grid and against NIST removal energies. The dominant
contributions to the 18s polarizability at the magic wavelength come from
the 18s-6p3/2, 18s-17p1/2, 18s-17p3/2, 18s-18p1/2 and 18s-18p3/2 channels (Table I), with correlation
corrections of order 1-3% relative to the lowest-order Dirac-Fock values.

## What it is worth here

Little of the physics transfers directly: the transition (5s-18s), the
excited-state type (a Rydberg level intended for gate schemes), and the
trapping wavelength (1064 nm, for a crossed dipole trap) are all unrelated
to the 5S-6S clock line this repository studies. Its use here is as a
methodology anchor, a worked, published instance of the same relativistic
all-order approach (and largely the same Safronova-group authorship) behind
the atomic-structure inputs this repository's own polarizability
calculations rely on, including a demonstration that even a careful
combination of theory and experiment can still disagree by a few sigma once
both sides state their own uncertainty budget.
