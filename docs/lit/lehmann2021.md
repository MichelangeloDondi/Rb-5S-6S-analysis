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

Modern closed-form transit-limit lineshape (the ``Lehmann lineshape''). Its analytic width (NNO example, HWHM 41.2 kHz) is the standard that fixed the M9 transit-MC flux bug — see docs/transit\_width\_resolved.md.

Sole author K. K. Lehmann; modern closed analytic form in the transit-time limit for a TEM00 standing wave, simpler than `borde1976`'s general case; gives spectrum proportional to exp(-|delta-nu|/gamma0(T)) with gamma0(T) proportional to sqrt(T) — matches our sqrt(T) scaling law (`transit_fwhm_at_T`). This is the "Lehmann lineshape" named in the README.

**Their own caveat on the cusp, checked against the PDF 2026-07-30 and relevant
to M4c/M8.** The cusp is explicit — "The lineshape is predicted to have a cusp,
i.e. a discontinuous slope, at exact resonance $\Delta\omega = 0$", arising from
the $1/v^2$ factor in $\rho^\infty_{ff}(b,v,\Delta\omega)$ cancelling the $v^2$ in
$vP(v)$ — but so is its limit: "both the assumption that collisions can be
neglected and that $\rho^\infty_{ff}$ can be calculated by perturbation theory
break down in this limit of small $v$. Correcting these assumptions will
'round-off' the cusp."

So the two-sided exponential is an idealisation whose sharpest feature is the
first thing collisions erode, and the slowest atoms — the ones that make the
cusp — are the ones the derivation handles worst. That is an argument for
carrying the Voigt-vs-cusp difference as a **model-form systematic** rather than
selecting one form and moving on, which is what `transit_kind` in
`lineshape.composite_profile` does. It also means M9's finding that the true
kernel is *more* cusped than the BBC idealisation should be read as a statement
about the collisionless geometry, not a prediction of what a hot cell shows.

