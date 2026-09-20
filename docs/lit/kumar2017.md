---
citekey: kumar2017
type: article
authors:
  - Kumar, S.
  - Fan, H.
  - Kübler, H.
  - Sheng, J.
  - Shaffer, J. P.
title: 'Atom-Based Sensing of Weak Radio Frequency Electric Fields Using Homodyne Readout'
journal: Scientific Reports
volume: 7
pages: '42981'
year: 2017
doi: 10.1038/srep42981
arxiv: null
pdf: PDF_papers/Kumar_2017_atom-based-RF-field-sensing-homodyne.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 (of 10) read against the PDF on 2026-09-20: the abstract
    and the start of the Materials and Methods section. The power/collisional
    /transit-time broadening data and the density-matrix comparison (most of
    the paper) are not read.
  - 2026-09-20: adversarial audit_D found the improvement-factor row cited to p. 1. The "six
    times better" sentence is on p. 2, after the Fig. 1 caption. Corrected.
verified_date: null
summary: >
  A Rydberg-EIT radio-frequency electric-field sensor in caesium vapour,
  reading out the EIT probe with a Mach-Zehnder homodyne technique to reach
  5 uV/cm/sqrt(Hz), six times better than the group's own prior direct
  -transmission result. Different atom, different platform (a bulk vapour
  cell, EIT to a Rydberg state, RF-field sensing rather than a two-photon
  clock line), and no Rb 5S-6S content, so nothing here is a source of
  numbers for this repository. What carries by analogy is its explicit
  three-way broadening decomposition (power, collisional, transit-time),
  which mirrors the channels this repository separates for its own line.
loci: []
section: unsorted
---
# kumar2017

## Values

| field | value | where in the paper |
|---|---|---|
| demonstrated RF sensitivity (this work) | 5 uV/cm/sqrt(Hz) | p. 1, abstract |
| prior sensitivity (same group's earlier direct-transmission result) | about 30 uV/cm/sqrt(Hz) | p. 1 |
| improvement factor | 6x | p. 2 |
| EIT ladder system | Cs 6S1/2(F=4) - 6P3/2(F'=5) - 52D5/2, RF resonant with 52D5/2-53P3/2 | p. 2 |
| probe / coupling wavelengths | about 852 nm / about 509 nm | p. 2 |
| probe laser linewidth (from the locking error signal) | about 50 kHz | p. 2 |
| Cs vapour cell length | 4 cm | p. 2 |
| probe beam size | 1.36 +/- 0.01 mm | p. 2 |
| local-oscillator-to-signal power ratio | about 20 | p. 2 |
| Rydberg transition dipole moments (order of magnitude) | 100-10 000 e a0 | p. 1 |

## What it says, in its own terms

The group upgrades a Rydberg-EIT radio-frequency electric-field sensor
(caesium, ladder system 6S1/2(F=4)-6P3/2(F'=5)-52D5/2, with the target RF
field tuned to the 52D5/2-53P3/2 Rydberg transition) by reading out the EIT
probe transmission with a Mach-Zehnder interferometer and homodyne detection
rather than direct transmission, so that probe-laser amplitude noise is
suppressed by the differential subtraction and the weak EIT signal is
enhanced by beating against a strong local oscillator. This raises the
demonstrated absolute RF-field sensitivity to 5 uV/cm/sqrt(Hz), six times
better than the group's own prior direct-transmission result of about
30 uV/cm/sqrt(Hz), while noting that the fundamental projection-noise
(shot-noise) limit for an ensemble of atoms in a vapour cell of the size
used is several orders of magnitude beyond what either measurement reaches,
so photon shot noise in the optical readout, not atom number, is identified
as the limiting factor at the time of writing.

With the improved signal-to-noise ratio, the paper studies the dephasing
mechanisms it identifies as dominant for this measurement: power
broadening, collisional broadening and transit-time broadening of the
EIT/Rydberg lines, comparing the observed linewidths against density-matrix
calculations of the coupled multilevel system.

## What it is worth here

A different atom (Cs), a different platform (a bulk vapour cell with EIT
readout of a Rydberg ladder for RF-field sensing, not a two-photon 5S-6S
clock transition), and a different measurement goal, so nothing here is a
source of Rb 5S-6S numbers. What carries by analogy is the broadening
decomposition itself: power, collisional and transit-time broadening are
exactly the three channels this repository separates for its own line, and
the paper's use of a Mach-Zehnder homodyne readout to push a spectroscopic
measurement toward its photon-shot-noise floor is a reminder of the kind of
technical noise floor a vapour-cell measurement eventually meets.
