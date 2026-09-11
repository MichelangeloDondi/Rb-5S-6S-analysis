---
citekey: lindvall2025
type: misc
authors:
  - Lindvall, T.
  - Hanhijärvi, K. J.
  - Fordell, T.
  - Wallin, A. E.
title: 'Measurement of the differential static scalar polarizability of the 88Sr+ clock transition'
journal: arXiv preprint
volume: null
pages: null
year: 2025
doi: null
arxiv: 2507.02603
pdf: PDF_papers/Sr-ion_2025_differential-static-scalar-polarizability-clock.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  A polarizability read off a CANCELLATION rather than off a calibrated field,
  from VTT MIKES in Finland. The differential static scalar polarizability of
  the 88Sr+ S1/2 to D5/2 clock transition is obtained from the magic ion-trap
  drive frequency where the micromotion-induced second-order Doppler and
  quadratic Stark shifts cancel, giving -4.8314(20)e-40 J m^2 / V^2. The
  methodological point this record should take is the second one: measuring at
  several Mathieu q values removes the rf-field-to-trap-axis angle, a nuisance
  that would otherwise dominate the systematic budget.
loci: []
section: prior-art
---
# lindvall2025

Held. Verified against the PDF, ten pages, on 2026-09-10.

## The construction

The differential static scalar polarizability is determined from the magic
ion-trap drive frequency at which the micromotion-induced second-order Doppler
shift and the quadratic Stark shift cancel. A single clock is run in an
interleaved scheme, switching between minimised and large micromotion. The
result is `Delta_alpha_0 = -4.8314(20) x 10^-40 J m^2 / V^2`.

## The two ideas worth taking

**A null in place of a calibration.** The quantity is read from where two
shifts cancel, not from a field whose magnitude has to be known. That is the
same family as a magic wavelength and as this record's own argument that a zero
crossing is not BOUND on the waist. It is a second, independent demonstration
that the family is productive, on a different species and a different pair of
competing shifts.

**A nuisance removed by varying a knob, not by measuring it.** The angle
between the rf electric field and the trap axis would otherwise dominate the
systematic uncertainty. Measuring at different Mathieu q values obtains
`Delta_alpha_0` without prior knowledge of that angle. **That is exactly the
design-matrix logic this record already uses on the waist ladder**, where three
widths carry three different powers of the waist and a scan over it separates
them. Seeing the same move settle an angle in an ion trap is a useful
generalisation, and the strongest argument this record has for the ladder is
that other groups reach for the same instrument when a nuisance resists direct
measurement.

## The validation they report

Measurements at different micromotion levels, and with the ion displaced in
opposite directions, are quoted as consistent. That is a plant with a sign
reversal in it, which is the shape this record's own rules ask for and is worth
citing when a guard here needs its own two-sided probe justified.
