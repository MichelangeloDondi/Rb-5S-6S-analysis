---
citekey: borde1976b
type: article
authors:
  - 'Bordé, C. J.'
  - Hall, J. L.
  - Kunasz, C. V.
  - Hummer, D. G.
title: 'Saturated absorption line shape: Calculation of the transit-time broadening by a perturbation approach'
journal: Phys. Rev. A
volume: 14
pages: 236--263
year: 1976
doi: null
arxiv: null
pdf: PDF_papers/Borde_1976b_saturated-absorption-transit-time-broadening-perturbation.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Page 1 (title, abstract, introduction) read in full against the PDF on 2026-09-20. The
    running headers of several later pages of the scan were also checked to confirm the page
    range (236 to 263). The density-matrix derivation (Secs. II-VI) and the closed-form results
    (Sec. VII) are not read, so this record carries only the introduction's own framing of the
    problem.
verified_date: null
summary: >
  A third-order perturbation, density-matrix calculation of the saturated-absorption
  (single-photon Lamb-dip) line shape that, for the first time, keeps the Gaussian transverse
  structure of the laser beam rather than treating it as a plane wave, so the line width and an
  induced shift are obtained as functions of the relaxation and transit times and of the beam's
  wave-front curvature. It is the single-photon, saturated-absorption counterpart of the citekey
  borde1976 two-photon transit-time treatment already held here, by the same first author. The
  latter is the one an existing two-photon transit-time treatment draws on, and this record exists
  so the two Bordé 1976 papers are kept apart rather than conflated.
section: transit-time
---
# borde1976b

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rev. A 14, 236-263 (1976) | p. 1 (title page) and running headers |
| order of perturbation theory | third order in the field | p. 1, abstract |
| geometry included, new to this theory | Gaussian transverse spatial structure of the laser beam(s) | p. 1, abstract |
| regime addressed | the free-flight (low-pressure) regime, molecules crossing a beam of finite width | p. 1, Sec. I |
| effects explicitly left for later papers | strong-field saturation, recoil splitting | p. 1, Sec. I |

## What it says, in its own terms

The paper opens by noting that every prior detailed theory of the Lamb dip / saturated-absorption
line shape had treated the laser field as a plane wave, ignoring the beam's transverse geometry,
and was therefore not applicable to the low-pressure, high-resolution regime where the line shape
is set instead by the transit time of molecules across a finite-width beam. It identifies three
distinct channels by which the beam geometry can enter: a time-dependent field seen by a molecule
in free flight (jointly controlled by radiative lifetime, collisions and transit time), a
space-dependent saturation parameter even at high pressure or short lifetime, and a resulting
self-focusing or self-defocusing deformation of the beam from the nonuniform, saturation-dependent
index of refraction. This paper restricts itself to the first channel, in a perturbative
(third-order) framework.

The stated method is to extend Lamb's third-order density-matrix calculation to Gaussian beams:
density-matrix equations for a two-level molecular system are set up for classical trajectories,
combined with the electromagnetic description of a Gaussian beam, and solved first for linear
absorption, then for the spatial and velocity-space profile of the population changes the
saturating beam induces, and finally for the third-order polarization that gives the
saturated-absorption line shape itself. The introduction states the paper will present the
resonance half-width as a function of relaxation rate and predict a line shift that arises when
the wave fronts are not flat, i.e. from wave-front curvature, together with simplified asymptotic
forms of the width's and shift's dependence on lifetime and beam geometry, and a treatment of a
frequency-modulated laser. The second-order Doppler effect is carried in some of the formulas "for
future application to the question of the accuracy of optical frequency standards" (p. 1).

## What it is worth here

This is the single-photon, saturated-absorption sibling of the two-photon transit-time paper
already held under the citekey borde1976 (Bordé, C. R. Acad. Sci. Ser. B 282, 341 (1976)), by the
same first author and built on the same density-matrix-plus-Gaussian-beam machinery. An existing
two-photon transit-time treatment draws on that other paper, via Biraben 1979 and Lehmann 2021's
closed forms, not on this one. The two Bordé 1976 papers are kept under separate citekeys
precisely so they are not conflated. This paper's own contribution -- the perturbative machinery
for a Gaussian beam in the single-photon Lamb-dip geometry, and the wave-front-curvature shift it
predicts -- is adjacent prior art rather than a direct input to a two-photon model, but it is the
same author working the same transit-time problem one photon order down, and is worth reading in
full if the single-photon case or the wave-front-shift result is ever needed.
