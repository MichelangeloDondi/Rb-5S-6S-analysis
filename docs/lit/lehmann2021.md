---
citekey: lehmann2021
type: article
authors:
  - Lehmann, Kevin K.
title: Two-photon absorption lineshapes in the transit-time limit
journal: J. Chem. Phys.
volume: 154
number: 10
pages: 104105
year: 2021
doi: 10.1063/5.0040868
arxiv: null
pdf: PDF_papers/Lehmann_2021_transit-time-limited-two-photon-lineshape.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Modern closed-form transit-limit lineshape (the ``Lehmann lineshape'').
loci:
  - M8
  - M9
  - constants
  - methods/02
section: transit-time
---

# lehmann2021

VERIFIED.

## The system and method

A closed analytic form for the two-photon lineshape in the transit-time limit, for a TEM00 standing wave, simpler than the general case in `borde1976`. The spectrum is proportional to exp(-|delta-nu|/gamma0(T)), with gamma0(T) proportional to sqrt(T), matching the sqrt(T) scaling law used in `transit_fwhm_at_T`. Its analytic width, HWHM 41.2 kHz for the NNO example, is the standard against which the M9 transit-MC flux bug was fixed (see `docs/transit\_width\_resolved.md`).

## The cusp

The lineshape has a cusp at exact resonance ($\Delta\omega = 0$), a discontinuous slope from the $1/v^2$ factor in $\rho^\infty_{ff}(b,v,\Delta\omega)$ canceling the $v^2$ in $vP(v) $. The same low-velocity limit that produces the cusp is where the derivation's own assumptions break down: the neglect of collisions and the perturbative calculation of $\rho^\infty_{ff}$ both fail for small $v$, and correcting them would round off the cusp.

## Use in this record

The two-sided exponential is accordingly an idealization at its sharpest feature. `transit_kind` in `lineshape.composite_profile` carries the Voigt-versus-cusp difference as a model-form systematic rather than selecting one form, and a finding that the true kernel is more cusped than the BBC idealisation is a statement about the collisionless geometry, not a prediction of what a hot cell shows.
