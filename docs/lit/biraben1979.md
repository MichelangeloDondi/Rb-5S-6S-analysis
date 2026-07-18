---
citekey: biraben1979
type: article
authors:
  - Biraben, F.
  - Bassini, M.
  - Cagnac, B.
title: 'Line-shapes in {Doppler}-free two-photon spectroscopy: the effect of finite transit time'
journal: J. Phys. (Paris)
volume: 40
number: 5
pages: 445--455
year: 1979
doi: null
arxiv: null
pdf: PDF_papers/Biraben_1979_finite-transit-time-two-photon-lineshape.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Origin of our transit kernel: the finite-transit Doppler-free two-photon
  line is a Lorentzian convolved with a two-sided exponential (the central
  cusp).
loci:
  - M3
  - M9
  - methods/02
section: transit-time
---

# biraben1979

HAL jpa-00209125. Origin of our transit kernel: the finite-transit Doppler-free two-photon line is a Lorentzian convolved with a two-sided exponential (the central cusp).

Our transit kernel (`lineshape.two_sided_exponential`, exp(-|nu|/b), convolved with the natural Lorentzian) is not a phenomenological guess -- it is the canonical result: the finite-transit Doppler-free two-photon line is exactly a Lorentzian convolved with a two-sided-exponential ("double-exponential meeting at a cusp"). This IS our model. Part of a chain with `borde1976` (the earlier, more general treatment) and `lehmann2021` (the modern closed analytic form).

Why this matters for the paper: it upgrades the transit model from "assumed shape" to "literature-standard analytic form," and it means the M8 Voigt-vs-Lehmann BIC test is Gaussian-core (Voigt) vs the BBC-1979 cusp -- a test between two published forms, not against a made-up one. Our M9 Monte-Carlo then refines the BBC idealization for our exact 3D-Maxwell-Boltzmann + w(z) + I^2 + collection conditions (finding the real kernel slightly MORE cusped, excess kurtosis ~4.6).
