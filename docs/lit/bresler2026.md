---
citekey: bresler2026
type: article
authors:
  - Bresler, Sean M.
  - Adkins, Erin M.
  - Eckel, Stephen P.
  - Herman, Tobias K.
  - Long, David A.
  - Reschovsky, Benjamin J.
  - Barker, Daniel S.
title: 'Electro-optic frequency comb Doppler thermometry'
journal: null
year: 2026
doi: null
arxiv: null
pdf: PDF_papers/Bresler_2026_EO-comb-Doppler-broadening-thermometry-transit-pumping-bias.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  A NIST Doppler thermometer on 85Rb vapour, accurate to about its 1 K
  statistical uncertainty, whose point is the systematic it removes.
  Transit-induced optical pumping distorts the lineshape and is named as
  the dominant systematic temperature shift in alkali Doppler
  thermometry. This record reads a temperature from a Doppler pedestal by
  the same route, so the caveat applies directly and was owed.
loci: []
section: method-anchors
---
# bresler2026

Held, ten pages, checked against the PDF.

## The result and the systematic

From the abstract, verbatim: the direct EOFC Doppler thermometer "is accurate
to within its approximately 1 K statistical uncertainty". And the finding that
matters here, verbatim: "Our results show that direct EOFC spectroscopy
mitigates transit-induced optical pumping distortion of the atomic lineshape,
which is the dominant systematic temperature shift in alkali atom Doppler
thermometry." Optical Bloch equation simulations of both schemes back it.

## Why this record needs it

The deep-trace work makes the Doppler pedestal an instrument: a thermometer
at about 8 K per per cent of width, with the 85 to 87 width ratio
`sqrt(m85/m87) = 0.988442` as a parameter-free check on it. That is alkali
Doppler thermometry from a step-scanned single-frequency probe, which is
precisely the arm this paper measures against and finds distorted.

**The mechanism is a real exposure here and not a generic caution.** An atom
crossing the beam is optically pumped during its transit, so the slow atoms,
which are the ones that make the pedestal narrow, are pumped hardest. The
distortion is therefore velocity-dependent and biases the inferred width, and
the record's own thermometer reads temperature FROM that width.

**What it does not do is invalidate the pedestal thermometer.** The
transition here is two-photon and Doppler-free at the narrow line, the
pedestal is a small residual, and the pumping physics on a 993 nm two-photon
excitation is not the same as on a D-line probe. The honest position is that
the bias exists, its sign is toward apparent cooling for the reason above, and
the record does not currently carry its size. Reaching for it needs the
optical-pumping term the twin already has for the hyperfine populations, run
against the transit rather than against the block.

## What is directly usable

The comparison arm. A chirped electro-optic comb interrogates every velocity
class at once, so the transit-time exposure does not accumulate the way it
does under a step scan. This record already builds combs with an EOM and
already runs a scan-rate ladder, so the same comparison is available on this
bench without new hardware.
