---
citekey: arvanitaki2008
type: article
authors:
  - Arvanitaki, Asimina
  - Dimopoulos, Savas
  - Geraci, Andrew A.
  - Hogan, Jason
  - Kasevich, Mark
title: 'How to Test Atom and Neutron Neutrality with Atom Interferometry'
journal: Phys. Rev. Lett.
volume: 100
number: 12
pages: 120407
year: 2008
doi: 10.1103/PhysRevLett.100.120407
pdf: PDF_papers/atom_interferometry/Arvanitaki_2008_atom-neutron-neutrality-atom-interferometry.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/arvanitaki2008.md  # line by line against the held PDF, 2026-09-22, two wording corrections applied (the fast/slow voltage-exposure sentence and an unstated gravity-gradient-source inference), every number and Table I entry confirmed exact on rendered page images
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published Phys. Rev. Lett. 100, 120407 (2008) typeset
    version (Acrobat Distiller output, no arXiv watermark on any page), 4 pages,
    confirmed by pdfinfo. No arXiv identifier for this paper appears anywhere in
    the document, so the arxiv field is left out here instead of guessed.'
  - 'All four pages read in full on 2026-09-22: title, byline, abstract,
    Introduction, Experimental setup, Sensitivity, Systematics with Table I,
    Theoretical motivation, acknowledgments and the full reference list.'
  - 'pdftotext -layout drops every exponent sign and superscript in this PDF
    (for example 10^-28 extracts as 1028, and 10^-3 as 103), so every numeric
    claim below was read from pages rendered at 200 to 500 dpi with pdftoppm,
    and the extracted text was used only for the surrounding words.'
verified_date: 2026-09-22
summary: >
  A proposal to test the electric charge neutrality of atoms and neutrons with
  a 10 m atom fountain interferometer built around the scalar Aharonov-Bohm
  effect, reusing an apparatus already under construction for an
  equivalence-principle test. Evaporatively cooled 87Rb atoms travel through
  field-free regions held at a controlled voltage, so a residual atom charge of
  epsilon times the electron charge builds a phase proportional to the voltage
  and the interrogation time, and the baseline design targets an atom-charge
  reach near epsilon of 10^-26, a charge per nucleon near 10^-28, about six
  orders of magnitude below the 10^-22 laboratory limit quoted at the time,
  with a differential 87Rb versus 85Rb measurement separately bounding the
  neutron charge at a comparable level. Because the atoms see no real field
  along their path, systematics from atomic polarizability are suppressed by
  the geometry itself, and the quoted error budget is dominated instead by
  voltage-switching transients in the electrode magnetic fields and by
  gravity-gradient phase noise coupling to the atom cloud's launch position and
  velocity.
loci: []
section: unsorted
---

# arvanitaki2008

VERIFIED. Held (published Phys. Rev. Lett. version, no arXiv watermark on any page), 4 pages. Read in full on 2026-09-22.

## What it does

A proposal, not an experimental report, for testing the electric neutrality of atoms and neutrons with a large fountain atom interferometer built around the scalar Aharonov-Bohm effect. The design reuses a 10 m interferometer already under construction for a separate equivalence-principle test. Evaporatively cooled 87Rb atoms are launched vertically, and a pulsed laser beam-splitter sequence splits the atomic wavefunction into a fast and a slow trajectory with a momentum difference between them. Both trajectories pass through a lower cylindrical electrode region held at minus half the applied voltage, and only the fast component continues upward into a second electrode region held at plus half the voltage, separated from the lower one by a gap, so the two paths sample different amounts of the applied voltage over the course of the flight. Because the atoms travel through pure gauge regions where the electric and magnetic fields are ideally zero, no classical force acts on them, and any residual atom charge instead accumulates a topological Aharonov-Bohm phase proportional to the applied voltage and the time spent in it. A differential measurement between the two stable isotopes 87Rb and 85Rb sharing the same atom cloud isolates the neutron's own charge from the combined proton and electron charge, since the two isotopes differ only in neutron number.

## The numbers

| quantity | value | page |
|---|---|---|
| baseline apparatus | a 10 m atom interferometer, reused from an equivalence-principle test | p. 1 |
| launch velocity | about 10 m/s for evaporatively cooled 87Rb | p. 1 |
| trajectory separation at the apex | set by the ordinary momentum kick now, 1.07 m with large momentum transfer beam splitters giving about 1 m/s velocity splitting | p. 1 |
| interrogation time | 1.16 s between beam-splitter pulses | p. 2 |
| example phase shift | for 10^5 V and 0.7 s interaction time, about 10^20 times epsilon | p. 2 |
| detectable phase, baseline | 10^-6 rad, from 10^6 atoms, 10^-3 rad shot-noise per trial, 10^6 trials | p. 2 |
| atom-charge reach, baseline | epsilon about 10^-26, charge per nucleon eta about 10^-28 | p. 2 |
| laboratory limit quoted at the time | eta = 10^-22 | p. 2 |
| upgraded reach (10^7 to 10^8 atoms, entangled states) | eta about 10^-30 | p. 2 |
| neutron-charge reach (differential 87Rb versus 85Rb) | 10^-28 e, about 7 orders of magnitude below the bound then current | p. 2 |
| an earlier proposal's design sensitivity, compared | eta about 10^-21 per root hertz there, against eta about 10^-27 per root hertz here | p. 3 |

Every exponent above was read from a rendered page image. The extracted text layer of this PDF drops signs and superscripts throughout, so pdftotext alone would misstate every one of these numbers.

## Systematics

**Intensity or differential light shift.** Removed by construction, not carried as a budgeted term. Because the interferometer arms travel through a region built to have zero electric and magnetic field, the text states directly that systematics from the atom's finite polarizability are avoided (p. 1). Table I still carries one residual line for it: an electric polarizability systematic of order 10^-14 rad, scaling with the square of the voltage (p. 3), many orders below the 10^-6 rad detection floor. This is a static electric polarizability responding to residual field leakage near the electrode gap, not an optical light shift, since no interrogation laser drives the atoms while they sit inside the voltage region.

**Finite size of the interrogation beam.** Addressed, though for a different failure path than an intensity budget. The high-voltage electrode walls deform slightly with applied voltage through electrostatic pressure, and that deformation changes how the beam-splitter laser diffracts off the tube walls, producing a small voltage-dependent phase error. The paper states this can be pushed below the entangled-state sensitivity floor by keeping the laser beam waist under 5 mm inside a 1 cm radius electrode tube (p. 3).

**Wavefront quality.** Not discussed anywhere in the four pages, no curvature, aberration or flatness term appears. The only laser-related noise budgeted is laser phase noise, and that is suppressed by running a second, common-mode interferometer about 2 m away in the same tube, not by any wavefront specification (p. 2).

**A source mass's position or alignment.** Not applicable in the sense of a positioned test mass, because the proposal has none. Its control potential is an applied electrode voltage, not a gravitational source. The nearest related budget line is atom-cloud position and launch-velocity noise coupling to the ambient gravity gradient: a phase-noise coefficient of about 7 rad per mm of initial position offset, and about 10^4 rad per m/s of launch-velocity variation, both accumulated over the 1.16 s interrogation time (p. 2). Holding this down needs cloud-position repeatability at the 1 micron level and launch-velocity repeatability at the 1 micron per second level for shot-noise-limited operation, tightening to 10 nm and 10 nm per second for the entangled-state case, after an engineered local mass distribution cuts the ambient gradient to about a tenth of its unshielded value (p. 2). That is gravity-gradient background rejection, not a source-mass alignment systematic.

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` is the record's own account of what this repository's work can offer to, and take from, the wider atom-interferometry community, written for the application to this application's target research group. This proposal belongs there only as lineage. It feeds no number into this record's own model. It bounds the electric charge of neutral atoms and neutrons with a kilometer-class fountain interferometer and a voltage-driven Aharonov-Bohm phase, a different physical quantity, a different apparatus scale, and a systematics budget sharing no term with a bench-top two-photon vapor-cell spectroscopy record. What connects the two is institutional and methodological only: the same broad atom-interferometry toolkit, common-mode noise rejection between two simultaneous interferometers, and control-parameter scaling used to separate a signal from its systematics, developed inside the same extended research network this application addresses. It is held for that lineage, not for any quantity this repository fits or reports.

## Limits

Every number above is the paper's own design estimate for a proposed apparatus, not measured data. Nothing here says whether the experiment was ever built or run. The closing theoretical-motivation section, on frameworks that allow small non-quantized atomic charges while preserving gauge coupling unification, is not summarized beyond noting it exists, since nothing in it bears on this record's own model or its systematics.
