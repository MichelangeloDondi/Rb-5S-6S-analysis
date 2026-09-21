---
citekey: stewart2022
type: article
authors:
  - Stewart, Riley A.
  - Shen, Pinrui
  - Booth, James L.
  - Madison, Kirk W.
title: 'Measurement of Rb-Rb van der Waals coefficient via Quantum Diffractive Universality'
journal: Phys. Rev. A
volume: 106
pages: 052812
year: 2022
doi: 10.1103/PhysRevA.106.052812
arxiv: '2208.12805'
pdf: PDF_papers/Stewart_2022_Rb-Rb-C6-quantum-diffractive-collision-universality.pdf
held: true
status: VERIFIED
audit: ../../../PhD-Thesis/private/lit_audits_2026-09-21/stewart2022.md  # line-by-line against the held PDF, 2026-09-21. the two-bracket caption (statistical, systematic) confirmed on the page
routing:
  - CITE
verify_flags:
  - Page 1 read against the PDF on 2026-09-20 (title, abstract, and the opening of the
    introduction and theory through Eq. 6). The experimental method, fit and systematics
    sections are not read.
  - The held PDF is the arXiv v1 preprint (arXiv:2208.12805v1, posted 26 Aug 2022) and prints
    no journal reference or DOI on the pages read. The journal, volume, page and DOI above are
    the published record, confirmed via the APS journals listing (journals.aps.org) on
    2026-09-20: Phys. Rev. A 106, 052812 (2022).
verified_date: 2026-09-21
summary: >
  A UBC Madison-group measurement of the ground-state Rb-Rb van der Waals coefficient, C6 =
  4688(198)(95) atomic units, obtained from the trap-depth dependence of collisional loss in a
  cold trapped Rb sample colliding with room-temperature background gas, via the "quantum
  diffractive universality" framework this group also uses for atom-based pressure sensing
  (see shen2023, vandongen2011 in this list). The measurement agrees with ab initio
  calculations and with an independent atom-interferometry determination of the Rb ground-
  state polarizability. It is adjacent, not central, to this record: it is the ground-state
  Rb-Rb potential's leading coefficient, not the excited-vs-ground difference potential that
  sets this record's own Rb-Rb self-broadening (beta_self) of the 5S-6S line, so no number
  here is directly usable, but it is a precisely measured reference value for the ground-state
  half of any such calculation.
loci: []
section: collision-series
---
# stewart2022

## Values

| field | value | where in the paper |
|---|---|---|
| measured Rb-Rb collision rate coefficient | ⟨σ_tot v⟩ = 6.44(11)(5)e-15 m^3/s | p. 1, abstract |
| deduced Rb-Rb van der Waals coefficient | C6 = 4688(198)(95) E_h a0^6 | p. 1, abstract |
| interaction potential form used | V(R) = -C6/R^6 | p. 1, Eq. (1) region |
| background-gas temperature | 294 K (room temperature) | p. 1 |
| characteristic quantum-diffractive energy scale | U_d = 4 pi hbar^2 v_p / (m_t ⟨σ_tot v⟩) | p. 1, Eq. (5) |

## What it says, in its own terms

**The idea.** Room-temperature background-gas particles colliding with ultracold trapped
atoms transfer energy across a broad range, from thermal down to the microkelvin trap-depth
scale, because of the long-range, soft-potential nature of the 1/R^6 van der Waals
interaction (the phrasing is vandongen2011's, on the same collision framework. Page 1 of this
paper's own held text is not read past the abstract and Eq. 6). The paper's own
prior work established that both the total collision rate and the post-collision energy-
transfer distribution (the fraction of atoms that remain trapped after a collision, as a
function of trap depth) are universal functions of a single parameter set by C6 alone. That
universality already underlies a self-calibrating, atom-based vacuum-pressure standard
(Booth et al. 2019, and Shen, Madison and Booth 2020, both cited as refs [1]-[2]).

**This paper's contribution.** Rather than use the universal function to infer a pressure from
a known C6, the paper runs the inference the other way: it measures the trapped-Rb loss rate
as a function of trap depth in a controlled background gas, fits the universal function, and
extracts ⟨σ_tot v⟩ and hence C6 for the Rb-Rb pair itself (the trapped ⁸⁷Rb atoms colliding with the room-temperature background Rb gas, both isotopes. Intra-trap collisions between trapped atoms are the systematic the method removes, not the signal, corrected 2026-09-21 against the PDF).

**The result.** C6 = 4688(198)(95) E_h a0^6, stated to be "in excellent agreement with
predictions based upon ab initio calculated and previously measured C6 values" (p. 1,
abstract) and with a separate atom-interferometry determination of the Rb ground-state
polarizability. The two quoted uncertainties are presented together in the abstract without
their individual statistical/systematic labels being read here (not examined beyond page 1).

## What it is worth here

Adjacent field, useful as a reference number rather than as an input. This measures the
ground-state Rb-Rb C6 coefficient via cold-atom trap-loss collisions with a room-temperature
background gas, a different process from this record's own warm-vapour Rb-Rb self-broadening
of the 5S-6S optical line, which through impact theory depends on the difference potential
between the excited 6S state and the ground state, not on the ground-state potential alone.
vandongen2011's own C6 values in this list, 280.0 E_h a_B for ground-state Rb-Ar against
924.1 and 545.1 for two excited-state Rb-Ar potentials, show directly how far an excited-state
C6 can sit from its ground-state counterpart for the same atom pair, which is the caution
against treating this paper's number as a proxy for this record's own self-broadening
coefficient. What transfers is the number itself as an independently measured, precise
ground-state Rb-Rb C6, useful if this record ever builds an impact-theory estimate of
beta_self from first principles and needs a validated ground-state input.
