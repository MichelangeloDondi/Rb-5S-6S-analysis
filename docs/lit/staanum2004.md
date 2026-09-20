---
citekey: staanum2004
type: article
authors:
  - Staanum, Peter
  - Jensen, Inger S.
  - Martinussen, Randi G.
  - Voigt, Dirk
  - Drewsen, Michael
title: 'Lifetime measurement of the metastable 3d 2D5/2 state in the 40Ca+ ion using the shelving technique on a few-ion string'
journal: Phys. Rev. A
volume: 69
pages: 032503
year: 2004
doi: 10.1103/PhysRevA.69.032503
arxiv: null
pdf: PDF_papers/Staanum_2004_metastable-D52-lifetime-Ca-ion-shelving.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Page 1 read against the PDF on 2026-09-20 (title, abstract, and the opening of the
    introduction and experimental-setup sections). The data-analysis, maximum-likelihood and
    systematics sections (Secs. III-IV) are not read.
verified_date: null
summary: >
  A trapped-ion measurement of the 40Ca+ 3d 2D5/2 metastable-state lifetime, tau =
  1149 +- 14 (stat) +- 4 (sys) ms, using the electron-shelving technique on a string of five
  laser-cooled ions in a linear Paul trap, with a maximum-likelihood analysis of 6805 shelving
  events. The species (a trapped Ca+ ion), the technique (quantum-jump/shelving detection of a
  metastable-state decay) and the physical quantity (a state lifetime relevant to optical
  clocks and qubits) are all unrelated to this record's Rb 5S-6S warm-vapour two-photon line,
  so relevance here is marginal, at most a general instance of maximum-likelihood treatment of
  a systematics-limited atomic measurement.
loci: []
section: unsorted
---
# staanum2004

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | QUANTOP, Department of Physics and Astronomy, University of Aarhus | p. 1 |
| DOI (printed on the paper itself) | 10.1103/PhysRevA.69.032503 | p. 1 |
| measured lifetime, this work | tau = 1149 +- 14 (stat) +- 4 (sys) ms | p. 1, abstract |
| number of shelving events | 6805 | p. 1, abstract |
| comparison lifetime, Barton et al. (single ion, same technique) | tau = 1168 +- 7 ms | p. 1 |
| number of ions in the string | 5 | p. 1, abstract |
| rf trap drive | 600 V peak-peak, 3.894 MHz | p. 1 |
| radial trap frequency | about 2 pi x 550 kHz | p. 1 |
| axial trap frequency | about 2 pi x 350 kHz | p. 1 |
| oven temperature (Ca source) | 420 C | p. 1 |
| chamber pressure at load / after 1 h | 6.0e-11 Torr / about 3.6e-11 Torr | p. 1 |
| Doppler-cooling transition and power | 4s 2S1/2 -> 4p 2P1/2 at 397 nm, about 15 mW | p. 1 |

## What it says, in its own terms

**Why the state matters.** The 3d 2D5/2 metastable state in 40Ca+ is a test case for
valence-core interaction and core-polarization calculations, its long lifetime implies a
sub-Hz natural linewidth for the 729 nm electric-quadrupole clock transition to the 2S1/2
ground state, and the same long lifetime makes it a candidate qubit state for trapped-ion
quantum computation (p. 1). Prior measurements and calculations of its lifetime were scattered
over a wide range, motivating a fresh, more precise measurement.

**The method.** Five 40Ca+ ions, Doppler-cooled and forced into a linear string in a linear
Paul trap, are prepared and then probed via the electron-shelving technique: population
transferred to the long-lived 2D5/2 state stops fluorescing on the cooling transition
("shelved"), and the statistics of how long each of the 6805 observed shelving events lasts,
analysed by a maximum-likelihood method (Sec. III, not read here), yields the state lifetime.
Systematic effects considered include unwanted excitation processes and collisions with
background gas, tracked in part through the chamber pressure (6.0e-11 Torr at load, falling to
3.6e-11 Torr over a 1-hour measurement session).

**The result.** tau = 1149 +- 14 (stat) +- 4 (sys) ms, in agreement with the most recent prior
measurement (Barton et al., 1168 +- 7 ms, on a single ion with the same shelving technique),
extending the shelving method to a multi-ion string.

## What it is worth here

Little. This is a trapped-ion metastable-state lifetime measurement by electron shelving, in a
different species (Ca+, not Rb), a different technique (quantum-jump/shelving detection of
discrete events, not continuous Doppler-broadened two-photon absorption), and aimed at a
different physical quantity (a state lifetime for optical-clock and qubit applications, not a
self-broadening coefficient or an AC-Stark distribution). The one generic point worth carrying
is methodological: the paper's use of a maximum-likelihood analysis of a systematics-limited
atomic observable is the same broad statistical posture this record's own main aim calls for
across its own observables, but that is a shared vocabulary, not a transferable result.
