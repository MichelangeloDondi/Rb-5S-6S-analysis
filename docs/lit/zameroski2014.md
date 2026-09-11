---
citekey: zameroski2014
type: article
authors:
  - Zameroski, N. D.
  - Hager, G. D.
  - Rudolph, W.
  - Erickson, C. J.
  - Hostutler, D. A.
title: 'Pressure broadening and frequency shift of the 5S1/2 to 5D5/2 and 5S1/2 to 7S1/2 two photon transitions in 85Rb by the noble gases and N2'
journal: J. Phys. B
volume: 47
number: 22
pages: 225205
year: 2014
doi: null
arxiv: null
pdf: PDF_papers/Zameroski_2014_Rb-5S-5D-7S-pressure-broadening-and-shift.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'author list beyond the first is taken from the journal record, not read off the scan'
verified_date: 2026-09-10
summary: >
  The closest published self-broadening and self-shift measurement for a
  Rb two-photon transition, and the paper Ayachitula cite for the Rb-Rb
  pressure shift in their error budget. It measures foreign-gas rates for
  5S-5D and 5S-7S and, separately, the Rb-Rb self-broadening and
  self-shift with their temperature dependence.
loci: []
section: collision-series
---
# zameroski2014

Held, fifteen pages, checked against the PDF.

## What it covers

Foreign-gas broadening and shift for two 85Rb two-photon transitions, the
5S-5D at 778.105 nm and the 5S-7S at 760.126 nm, which the paper states are
reported for the first time. The rates for helium, neon and argon on the
5S-5D line are, verbatim from the text, broadening "51.1 +- 0.4, 24.7 +- 0.3
and 45.7 +- 0.4" and shift "2.06 +- 0.07, -5.23 +- 0.06, and -13.16 +- 0.06",
both in MHz per Torr.

**And the part this record needs is the self term.** The paper states that
the self-broadening and shift rates of both transitions "were also
measured", and that "The temperature dependence of the self- frequency shift
(Rb-Rb collisions) of these transitions is presented."

## Why it is the right comparison and not a substitute

This record measures `beta_self` on 5S-6S at 993 nm. Zameroski measure the
same class of quantity, Rb-Rb collisional broadening and shift of a two-photon
line, on two neighbouring transitions. The upper states differ, so the
coefficients are not transferable, and nothing here can be adopted as a value.
What it provides is independent evidence that such coefficients are of the
size this record finds, and that their temperature dependence is measurable
and not merely assumed.

It is also the source [ayachitula2024](ayachitula2024.md) cite for the Rb-Rb
pressure shift they enter at 2 kHz, so it sits under a number in the error
budget of the sharpest published measurement of this record's own transition.
