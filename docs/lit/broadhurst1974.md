---
citekey: broadhurst1974
type: article
authors:
  - Broadhurst, J. H.
  - Cage, M. E.
  - Clark, D. L.
  - Greenlees, G. W.
  - Griffith, J. A. R.
  - Isaak, G. R.
title: 'High resolution measurements of isotope shifts and hyperfine splittings for ytterbium using a cw tunable laser'
journal: 'J. Phys. B: At. Mol. Phys.'
volume: 7
number: 18
pages: L513-L517
year: 1974
doi: 10.1088/0022-3700/7/18/001
arxiv: null
pdf: PDF_papers/Broadhurst_1974_Yb-hyperfine-isotope-shifts-cw-dye-laser.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'The PDF text layer is badly garbled on a handful of tokens (superscript
    isotope labels and units render as stray punctuation, e.g. the
    1S0-3P1 term prints as "1S,-3P,", 5556 A prints as "5556 .A", and
    +/-0.6 MHz prints as "k0.6 Wiz"). Confirmed with pypdf directly, so this
    is the actual embedded layer, not a rendering artefact of one reader.
    Quotations below were chosen to avoid those spans. The accuracy and
    wavelength figures are reported in prose, not as quotations, for that
    reason.'
verified_date: 2026-08-03
summary: >
  Yb I 555.6 nm intercombination-line (1-photon, 1S0-3P1) hyperfine
  structure and isotope shifts from a cw dye laser on a collimated atomic
  beam, accuracy about +/-0.6 MHz. Ytterbium, not an alkali. Single-photon,
  not two-photon. No bridge to the Rb 5S-6S line or its prior-art chain.
loci: []
section: unsorted
---

# broadhurst1974

**Read in full 2026-08-03.** This is a 1974 J. Phys. B Letter to the Editor,
not a two-photon paper and not on an alkali. It reports the hyperfine
structure and isotope shifts of the ytterbium (Yb I) 555.648 nm
intercombination line, 4f14 6s2 1S0 to 4f14 6s6p 3P1, a single-photon,
spin-forbidden E1 transition. Ytterbium is a lanthanide with a closed-shell
1S0 ground state, not an alkali doublet system, so there is no S-to-S
two-photon transition anywhere in this paper.

**Abstract, verbatim (the method clause):** the isotope shifts and hyperfine
structure "have been measured by observing the resonant scattering of light
from a cw tunable dye laser incident on a collimated atomic beam." Results
for all stable Yb isotopes are reported to about +/-0.6 MHz (+/-0.02 mK),
and the abstract closes: "Improved relative isotope shifts are obtained, and
the hyperfine anomaly of 171,173Yb is also calculated."

**Opening, verbatim:** "The present work uses a continuous-wave tunable dye
laser, and the resonant scattering from a well collimated atomic beam is
studied. This method suffers less from the limitations in frequency range
associated with other scanning techniques, and yet retains the high
resolution features of atomic beams."

**What it does.** A cw dye laser (Spectra Physics 580-01, argon-ion pumped,
17 MHz FWHM) is scanned across a collimated Yb atomic beam and the resonant
fluorescence is recorded. Doppler broadening is suppressed geometrically, by
beam collimation, not by a two-photon counter-propagating geometry: "Atomic
beam collimation assured that frequency broadening due to Doppler spread was
less than 5 MHz, compared to a natural width of the Yb line of 0.2 MHz." A
stabilised confocal Fabry-Perot etalon, itself locked to a Lamb-dip-stabilised
He-Ne laser, supplies frequency markers (300.31 MHz free spectral range, and
sub-markers down to 41.7 MHz by stepping the servo-lock order) so that peak
centres are read to about 0.6 MHz against 17 MHz wide lines. All nine stable
Yb isotopes are resolved and referenced to 174Yb. Component splittings give a
171,173Yb hyperfine anomaly of -0.47(2)%, compared with -0.367(9)% from prior
level-crossing work, a discrepancy the authors note without resolving.

**Key numbers.**

- Laser linewidth: 17 MHz FWHM.
- Natural Yb line width: 0.2 MHz.
- Doppler contribution: held below 5 MHz by beam collimation.
- Peak-centre accuracy: about +/-0.6 MHz.
- Etalon free spectral range: 300.31(2) MHz.
- Hyperfine anomaly of 171,173Yb: -0.47(2)%.

These are an order of magnitude tighter than the prior hollow-cathode-lamp
measurements the paper compares against (2000 MHz FWHM typical, 630 MHz best
case).

**Bridge to the Rb 5S-6S prior-art chain: none.** This paper sits outside
the lineage `LITERATURE.md` traces (Levenson and Bloembergen 1974,
`biraben1974`, through the OIST/USAFA 993 nm work and
`orson2021`/`ayachitula2024`) on every axis that lineage is built from.
Species: ytterbium, not rubidium or any alkali. Transition order: one-photon
resonant scattering, not two-photon absorption or fluorescence. Doppler
strategy: mechanical beam collimation, not the counter-propagating
two-photon cancellation that defines the founding-era papers. The only
contact point is the calendar: it was received 17 October 1974, the same
year as the Doppler-free two-photon demonstrations, and its own
introduction cites Hänsch et al 1974 (the H2-D2 saturation-spectroscopy
letter, PRL 32, 1336) as a contemporary example of tunable-dye-laser
precision spectroscopy. That places it as a same-year, unrelated route to
sub-Doppler resolution, useful only as period colour for how varied 1974
laser spectroscopy already was, not as prior art this programme needs to
delineate itself from. It is catalogued here and left uncited in the
manuscript docs.
