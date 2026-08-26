---
citekey: nasoni2026
type: misc
authors:
  - Nasoni, Francesco
title: 'Optical Trapping of Cold Atoms with a Hollow-Core Fiber'
journal: "Master's thesis, Universita di Bologna"
volume: null
pages: null
year: 2026
doi: null
arxiv: null
pdf: PDF_papers/theses/TesiLM_Nasoni_2026_Optical Trapping of Cold Atoms with a Hollow-Core Fiber.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Unpublished master''s thesis on the apparatus itself, defended July 2026.
    It is apparatus provenance, not independent literature, and must not be
    treated as a citable external source.'
  - 'the waist IT supplies IS for A different beam and A different experiment,
    and this must travel with the number. The 17.1 x 19.3 um injection waist is
    the 1064 nm optical dipole trap beam. A hollow-core guided mode depends on
    wavelength, so carrying it to a 778 nm or 993 nm line is an assumption.
    Further, per a private communication, the apparatus is headed for
    780 nm EIT cooling, and two-photon spectroscopy in that fibre is
    speculative.'
  - 'Read for the injection-waist passage (its section 2.2.2.1) and the
    abstract. The trap-depth model, the loading-efficiency result and the
    fibre-characterisation chapters are not read.'
verified_date: 2026-07-31
summary: >
  Bologna master's thesis, 103 pp, on an optical dipole trap for cold 87Rb made
  by coupling 1064 nm into a hollow-core photonic-crystal fibre, with a
  near-field imaging system for alignment; reports a loading efficiency against
  a "non-shallow trap model" and sets up a counter-propagating second beam for
  an optical conveyor belt. It is the source of a number this repository had
  carried unsourced: the CRYST3 fibre's "18 um mode field". The
  thesis makes it an injection beam waist -- a radius, settling a
  radius-vs-diameter question worth a factor of two in every transit estimate
  -- with an 18 um design target, a 13.6 +/- 0.1 um ideal thin-lens value, and
  a MEASURED 17.1 +/- 0.7 um by 19.3 +/- 0.4 um. Not stated in the thesis but
  confirmed separately: that mode belongs to the 1064 nm trapping laser, the
  planned next
  step for the apparatus is 780 nm EIT cooling, and a 778 nm two-photon line in
  the hollow core is a speculative idea for a possible separate paper rather
  than a plan. Transit numbers computed here for a 778 nm probe are answers to
  a hypothetical.
loci:
  - P1
  - P2
section: oist-lineage
---

# nasoni2026

VERIFIED, 2026-07-31. Read for the injection-waist passage and the abstract (103 pp). The trap-depth model, loading-efficiency result, and fibre-characterization chapters are not read.

Unpublished master's thesis, University of Bologna, defended July 2026. Apparatus provenance for the CRYST3 hollow-core fibre, not independent literature.

## The system

An optical dipole trap for cold 87Rb made by coupling 1064 nm light into a hollow-core photonic-crystal fibre, with a near-field imaging system for beam alignment at the injection point.

## The numbers

The injection waist is designed to approximately 18 µm:

> "the real waist at the injection is expected to be closer to the target value of approximately ~18 µm"

An ideal thin-lens calculation gives $w_{\rm inj} \simeq 13.6 \pm 0.1$ µm, and an $M^2 = 1.2$ correction gives $\simeq 15.1$ µm. The measured value:

> "the beam profile after the injection lens was characterized … yielding $w_{\rm inj\text{-}x} = (17.1 \pm 0.7\ \mu m) $, $w_{\rm inj\text{-}y} = (19.3 \pm 0.4\ \mu m) $, sufficiently close to the target waist"

is slightly elliptical, attributed by the thesis to the AOM compressing the beam in $y$ and expanding it in $x$. The 18 µm figure is therefore a beam radius, not a diameter, borne out by the measurement.

The loading efficiency is quoted against an expected value of $0.41 \pm 0.04$ per cent.

## Use in this record

The measured injection waist belongs to the 1064 nm trapping beam, not to a 778 nm or 993 nm two-photon probe. A hollow-core guided mode depends on wavelength, so applying this waist to a different wavelength is an assumption, not a measurement. Converting each waist value to a transit-time-broadening FWHM at a cell temperature of 100°C (calculated) gives:

| $w_0$ | source | transit FWHM |
|---|---|---|
| 13.6 µm | ideal thin-lens | 4.34 MHz |
| 15.1 µm | $M^2 = 1.2$ | 3.90 MHz |
| 17.1 µm | measured, $x$ | 3.45 MHz |
| 18.0 µm | design target | 3.28 MHz |
| 19.3 µm | measured, $y$ | 3.06 MHz |

Per a private communication, the fibre's next planned use is 780 nm light for EIT cooling. A 778 nm two-photon line in the hollow core is a speculative idea for a possible separate paper, not a planned measurement. Any transit-time number computed here for a 778 nm probe therefore answers a hypothetical.
