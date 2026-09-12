---
citekey: levenson1974
type: article
authors:
  - Levenson, M. D.
  - Bloembergen, N.
title: 'Observation of Two-Photon Absorption without Doppler Broadening on the 3S-5S Transition in Sodium Vapor'
journal: Physical Review Letters
volume: '32'
pages: '645'
year: 1974
doi: 10.1103/PhysRevLett.32.645
arxiv: null
pdf: PDF_papers/Levenson_1974_doppler-free-two-photon-standing-wave.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-11
summary: >
  One of the three 1974 papers that founded Doppler-free two-photon
  spectroscopy, and the one that used counter-propagating circularly
  polarised beams so the selection rule removes the Doppler pedestal
  rather than leaving it under the narrow line. This record's geometry is
  the other choice, a retro-reflected linear standing wave, which keeps
  the pedestal and uses it: it is the thermometer and the retro-ratio
  probe the guided arm has no substitute for.
loci:
  - methods/01
  - THEORY
section: method-anchors
---
# levenson1974

Held and read on 2026-09-11.

## What it is

Sodium 3S-5S driven by two photons, "one each from two circularly polarized
beams traveling in opposite directions through the vapor", quoted verbatim from
the abstract, which also states verbatim that "Doppler broadening is absent and
the hyperfine structure is resolved". The hyperfine constant of the 5S state is
the measurement it reports.

## Why it is held

It is the technique's own founding literature, alongside Biraben, Cagnac and
Grynberg and the Stanford work of the same year, and this record's measurement
is the same technique three species and fifty years later.

## The one thing that transfers, and it is a design choice this record made differently

Levenson and Bloembergen drive the transition with two counter-propagating
*circularly* polarised beams. In that configuration the sigma-sigma selection rule
forbids absorbing two photons from the same beam, so the Doppler-broadened
background is not merely small, it is absent.

This record drives a retro-reflected *linear* standing wave, where both photons
may come from the same travelling component, so the Doppler pedestal survives
under the narrow line. That is a cost and this record spends it deliberately:
the pedestal carries the sample temperature and the retro power ratio, and both
are read from it in `docs/methods/01`. A circular geometry would remove the
pedestal and with it the thermometer.

## What it does not settle

Different species, different transition and a pulsed dye laser of much larger
bandwidth than anything here, so no number in it constrains a rubidium 5S-6S
width, shift or branching.

## A caution about the held scan

The file is a scan of the journal page, and the page's first column is the
closing column of the preceding article. Text extracted from the head of this PDF belongs to
that paper and not to this one. The quotations above are from Levenson and
Bloembergen's own abstract, which begins partway down the file.
