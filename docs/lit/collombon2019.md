---
citekey: collombon2019
type: misc
authors:
  - Collombon, M.
  - Chatou, C.
  - Hagel, G.
  - Pedregosa-Gutierrez, J.
  - Houssin, M.
  - Knoop, M.
  - Champenois, C.
title: 'Experimental demonstration of three-photon Coherent Population Trapping in an ion cloud'
journal: arXiv preprint
year: 2019
doi: null
arxiv: '1903.05386'
pdf: PDF_papers/Collombon_2019_three-photon-CPT-ion-cloud.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 (abstract, introduction and the start of the observation-conditions section)
    read against the PDF on 2026-09-20. No published journal reference is given on either page, so
    the record carries the arXiv v2 preprint (16 Jul 2019) as held. Reference [22] on the last
    page is a different Collombon paper (Opt. Lett. 44, 859 (2019)), not this one. The linewidth,
    shift and contrast analysis, the bulk of the paper, is not read.
  - 2026-09-20: adversarial audit_A found the reference-transition row cited to p. 1, Eq. (2).
    Both the equation defining omega_THz and its "(2)" tag are on p. 2. Corrected.
verified_date: null
summary: >
  Demonstrates a three-photon dark resonance in a cloud of laser-cooled 40Ca+ ions held in a
  linear RF trap, referencing the beat of three phase-locked lasers to a 1.82 THz magnetic-dipole
  transition known to +-8 Hz, and argues sub-kHz spectroscopic resolution is reachable this way.
  The system (trapped ions, a THz reference transition) is unrelated to a rubidium vapour-cell
  programme. It stands here as an adjacent-field multi-laser, optical-frequency-comb referencing
  scheme, not a source of any usable number.
section: deep-search
---
# collombon2019

## Values

| field | value | where in the paper |
|---|---|---|
| reference transition | 3D3/2-3D5/2 magnetic dipole transition in 40Ca+, omega_THz | p. 2, Eq. (2) |
| reference transition frequency | 1.82 THz, known to +-8 Hz (via Raman spectroscopy on a single trapped ion) | p. 2 |
| reference transition wavelength | lambda_THz = 165 micron | p. 2 |
| cooling / repump / quadrupole transitions | 396.85 nm (4S1/2-4P1/2), 866.21 nm (3D3/2-4P1/2), 729.15 nm (4S1/2-3D5/2) | p. 2 |
| branching ratio to the metastable 3D3/2 state | beta = 0.064 | p. 2 |
| RF trap parameters | 5.2 MHz drive, 826 Vpp, Mathieu parameter q_x = 0.24, inner radius 3.93 mm | p. 2 |
| ion cloud size | diameter 80-280 micron, length 120-740 micron, 40-2750 ions | p. 2 |
| 729 nm laser waist | 300 (+-20) micron diameter | p. 2 |
| optical frequency comb repetition rate | 80 MHz | p. 2 |
| cited CPT-microwave clock stability | vapour cell: a few x 10^-13 / sqrt(tau); cold-atom clock: about 3x10^-13 after 1 hour | p. 1 |

## What it says, in its own terms

The paper reports the first observation of a three-photon coherent-population-trapping (CPT) dark
resonance in a cloud of trapped, laser-cooled 40Ca+ ions, extending the two-photon CPT scheme used
in vapour-cell and cold-atom microwave clocks to a three-laser, N-level scheme spanning the
optical and near-infrared. Three lasers -- resonant with the 4S1/2-4P1/2 cooling transition
(396.85 nm), the 3D3/2-4P1/2 repump transition (866.21 nm), and the electric-quadrupole
4S1/2-3D5/2 transition (729.15 nm) -- are simultaneously phase-locked to the same optical
frequency comb. The three-photon dark-resonance condition ties a specific combination of the
three laser frequencies to the 1.82 THz magnetic-dipole transition between the 3D3/2 and 3D5/2
levels, which serves as the frequency reference and is itself known to +-8 Hz from prior
single-ion Raman spectroscopy.

Because the lasers co-propagate along the trap axis, the effective wave vector controlling the
first-order Doppler effect on the dark line is set by the THz transition's own (165 micron)
wavelength rather than by any of the three optical wavelengths, giving a Lamb-Dicke-like
suppression of Doppler broadening even though the ions are not laser-cooled to the Lamb-Dicke
regime for the individual optical transitions. Because all atoms are confined within the (fixed,
overlapping) laser beams throughout, the paper notes this removes the finite-interaction-time
broadening that affects two-photon CPT lines observed on an atomic beam or a room-temperature gas
cell. It argues that with this scheme, sub-kHz resolution referenced to the 1.82 THz transition is
experimentally accessible, and states it will discuss, later in the paper, the causes of shift and
broadening specific to this method.

## What it is worth here

The physical system -- a trapped, laser-cooled Ca+ ion cloud referenced through a THz magnetic
dipole transition -- has no direct overlap with a rubidium vapour-cell, 5S-6S two-photon
programme. No number here is usable. Its only point of contact is the general technique of
locking several lasers to one optical frequency comb to reference a widely separated set of
transitions, which is a generic tool rather than anything specific to any particular frequency
referencing scheme. Marginal relevance, kept as an adjacent-field record rather than a working
reference.
