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

Held. Verified in full.

A 1974 Letter to the Editor in *J. Phys. B*, not a two-photon paper and not on an alkali. It reports the hyperfine structure and isotope shifts of the ytterbium (Yb I) 555.648 nm intercombination line, 4f14 6s2 1S0 to 4f14 6s6p 3P1, a single-photon, spin-forbidden E1 transition. Ytterbium has a closed-shell 1S0 ground state, not an alkali doublet system, so there is no S-to-S two-photon transition in this paper.

## The system and method

A cw dye laser (Spectra Physics 580-01, argon-ion pumped, 17 MHz FWHM) is scanned across a collimated Yb atomic beam and the resonant fluorescence is recorded. Doppler broadening is suppressed geometrically, by beam collimation, not by a two-photon counter-propagating geometry: "Atomic beam collimation assured that frequency broadening due to Doppler spread was less than 5 MHz, compared to a natural width of the Yb line of 0.2 MHz." A stabilised confocal Fabry-Perot etalon, locked to a Lamb-dip-stabilised He-Ne laser, supplies frequency markers (300.31 MHz free spectral range, and sub-markers down to 41.7 MHz by stepping the servo-lock order), so peak centres are read to about 0.6 MHz against 17 MHz wide lines. All nine stable Yb isotopes are resolved and referenced to 174Yb. Component splittings give a 171,173Yb hyperfine anomaly of -0.47(2)%, compared with -0.367(9)% from prior level-crossing work, a discrepancy the authors note without resolving.

## The numbers

- Laser linewidth: 17 MHz FWHM.
- Natural Yb line width: 0.2 MHz.
- Doppler contribution: held below 5 MHz by beam collimation.
- Peak-centre accuracy: about ±0.6 MHz.
- Etalon free spectral range: 300.31(2) MHz.
- Hyperfine anomaly of 171,173Yb: -0.47(2)%.

These are an order of magnitude tighter than the hollow-cathode-lamp measurements the paper compares against (2000 MHz FWHM typical, 630 MHz best case).

## Use in this record

Outside the Rb 5S-6S prior-art lineage traced in `LITERATURE.md` (Levenson and Bloembergen 1974, `biraben1974`, through the OIST/USAFA 993 nm work, `orson2021` and `ayachitula2024`) on every relevant axis: different species (ytterbium, a lanthanide, not an alkali), single-photon rather than two-photon transition order, and Doppler suppression by mechanical beam collimation rather than counter-propagating two-photon cancellation. Contemporary with the first Doppler-free two-photon demonstrations (received 17 October 1974) and cites Hänsch et al. (1974) as a contemporary example of tunable-dye-laser precision spectroscopy, but supplies no prior art for this line.
