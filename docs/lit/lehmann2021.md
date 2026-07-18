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

Modern closed-form transit-limit lineshape (the ``Lehmann lineshape''). Its analytic width (NNO example, HWHM 41.2 kHz) is the standard that fixed the M9 transit-MC flux bug -- see docs/transit\_width\_resolved.md.

Sole author K. K. Lehmann; modern closed analytic form in the transit-time limit for a TEM00 standing wave, simpler than `borde1976`'s general case; gives spectrum proportional to exp(-|delta-nu|/gamma0(T)) with gamma0(T) proportional to sqrt(T) -- matches our sqrt(T) scaling law (`transit_fwhm_at_T`). This is the "Lehmann lineshape" named in the README.
