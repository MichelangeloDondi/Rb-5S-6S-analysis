---
citekey: rahaman2022b
type: article
authors:
  - Rahaman, Bubai
  - Dutta, Sourav
title: 'Hyperfine coupling constants of the cesium 7D5/2 state measured up to the octupole term'
journal: 'Opt. Lett.'
volume: 47
number: 18
pages: 4612--4615
year: 2022
doi: 10.1364/OL.469086
arxiv: null
pdf: PDF_papers/Rahaman-Dutta_2022b_Cs-7D52-hyperfine-octupole.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - 'All 4 pages (the full letter) read against the PDF on 2026-09-20. Held as
    the publisher (Optica) PDF, not an arXiv preprint. No arXiv identifier
    appears in the text read. Same TIFR group and technique family as the
    sibling note rahaman2022 (the 7D3/2 hyperfine/ac-Stark paper),
    disambiguated with a "b" suffix on the citekey since "rahaman2022" already
    names that other paper.'
  - '2026-09-20: adversarial audit_E corrected two defects. The beam-waist row was cited to
    p. 1, but the "63 +/- 2 um" sentence is on p. 2. And the pressure-shift/linewidth prose had
    conflated two separate statements: the paper reports two different branch-specific pressure
    shifts, not one shared value, and the comparison against the expected linewidth is drawn
    against the zero-pressure-intercept linewidth, not against the pressure-broadening slope.'
verified_date: null
summary: >
  Doppler-free two-photon spectroscopy (767.2 nm) of the Cs 6S1/2 -> 7D5/2
  transition in a vapour cell, resolving all six hyperfine levels and
  reporting the magnetic-dipole (A), electric-quadrupole (B) and, for the
  first time, magnetic-octupole (C) hyperfine constants, with at least a
  20-fold precision improvement on A and B over earlier work. The same
  vapour-cell apparatus also yields the ac Stark shift, the pressure
  (collisional) shift and the pressure broadening of the transition -- the
  same measurement classes this record performs on Rb 5S-6S, on a different
  alkali line but a closely related two-photon vapour-cell technique.
loci: []
section: prior-art
---

# rahaman2022b

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Opt. Lett. **47**, 4612-4615 (2022) | p. 1 header |
| DOI | 10.1364/OL.469086 | p. 1 footer |
| received / revised / accepted / published | received 29 June 2022; revised 11 August 2022; accepted 11 August 2022; published 2 September 2022 | p. 1 |
| affiliation | Tata Institute of Fundamental Research, Mumbai, India | p. 1 |
| transition | Cs 6S1/2 -> 7D5/2, two-photon, 767.2 nm, counter-propagating and Doppler-free | p. 1 |
| magnetic-dipole constant A | -1.70867 +/- 0.00062 MHz | p. 1, p. 4 |
| electric-quadrupole constant B | 0.050 +/- 0.014 MHz | p. 1, p. 4 |
| magnetic-octupole constant C (first determination for this state) | 0.4 +/- 1.4 kHz | p. 1, p. 4 |
| precision improvement over earlier reports (A, B) | at least 20-fold | p. 1, p. 4 |
| hyperfine-splitting measurement precision | about 10 kHz | p. 2 |
| ac Stark shift | -46 +/- 4 Hz (W cm^-2)^-1 | p. 1, p. 3 |
| pressure (collisional) shift, F=3->F' / F=4->F' | -24 +/- 2 kHz mTorr^-1 / -36 +/- 3 kHz mTorr^-1 | p. 3 |
| pressure-broadening slope (average of the resolved lines) | 101 +/- 19 kHz mTorr^-1, zero-pressure intercept 2.1 +/- 0.3 MHz | p. 3 |
| expected linewidth from transit time plus laser linewidth | about 1.7 MHz | p. 3 |
| laser beam waist at the spectroscopy cell (1/e^2 radius) | 63 +/- 2 um | p. 2 |
| vapour-pressure scan range (cell temperature) | 50 C to 159 C | p. 3 |
| theoretical A (the one available calculation, agreeing with none of the experiments) | -1.42 MHz | p. 4 |

## What it says, in its own terms

The paper reports Doppler-free two-photon spectroscopy of the caesium 6S1/2 -> 7D5/2 transition at 767.2 nm in a room-temperature vapour cell, using counter-propagating beams from a tapered-amplifier-boosted external-cavity diode laser. Two technical choices drive its precision: detecting the direct 7D5/2 -> 6P3/2 fluorescence at 698 nm instead of the more common 7P3/2 -> 6S1/2 cascade at 456 nm, which avoids reabsorption of the emitted light by ground-state atoms and improves the signal-to-noise ratio. The second is a precisely linearised laser frequency scan obtained by double-passing an acousto-optic modulator in a cat's-eye configuration, driven by a signal generator with sub-Hz frequency resolution, which removes the scan nonlinearity that limited earlier measurements.

All six hyperfine levels of both the F=3 and F=4 ground-state excitation branches are resolved and fitted with a sum of Voigt profiles. The resulting splittings are fitted globally to the standard magnetic-dipole/electric-quadrupole/magnetic-octupole hyperfine energy formula, giving A, B and, for the first time for this state, a nonzero-uncertainty determination of the octupole constant C. The measurement resolves an existing sign ambiguity in B, establishing it as positive, and improves the precision of every earlier determination of A and B by at least a factor of 20. The one available theoretical value of A, -1.42 MHz, does not agree well with any of the experimental values, including this one.

Beyond the hyperfine structure, the same apparatus is used to measure three systematic effects relevant to using this transition as a frequency standard: the ac Stark (light) shift, obtained from the linear dependence of the line positions on laser power, the pressure (collisional) shift and pressure broadening of the lines, obtained by varying the vapour-cell temperature from 50 C to 159 C, and checks that a residual magnetic field of 15-20 mG and removing the focusing lens both leave the measured hyperfine splitting unchanged. The pressure shift differs between the two ground hyperfine levels (-24 +/- 2 kHz/mTorr for F=3->F' and -36 +/- 3 kHz/mTorr for F=4->F', respectively), though within each branch every F' sublevel shifts at that branch's own common rate, leaving each branch's own hyperfine splitting unchanged with temperature. Separately, the measured zero-pressure-intercept linewidth (2.1 +/- 0.3 MHz) is slightly higher than the transition's expected linewidth from transit-time and laser-linewidth estimates alone (about 1.7 MHz).

## What it is worth here

This is close prior art in the same sense as its sibling note rahaman2022: a Doppler-free two-photon vapour-cell measurement of an alkali S-D two-photon line, from the same group and apparatus family, reporting ac Stark shift, collisional shift and pressure broadening alongside the primary hyperfine result -- precisely the systematic-effects triad this record measures for Rb 5S-6S. The two papers together give two independent, same-apparatus, same-technique benchmarks (7D3/2 and 7D5/2) for how these systematics scale and are reported in a comparable vapour-cell two-photon experiment, useful as an external cross-check on the order of magnitude and reporting convention of this record's own ac-Stark, collisional-shift and pressure-broadening numbers, even though the specific atom, line and coupling constants themselves do not transfer.
