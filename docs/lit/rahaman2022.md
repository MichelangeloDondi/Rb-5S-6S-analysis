---
citekey: rahaman2022
type: article
authors:
  - Rahaman, B.
  - Dutta, S.
title: 'High precision measurement of the hyperfine splitting and ac Stark shift of the 7d 2D3/2 state in atomic cesium'
journal: Phys. Rev. A
volume: 106
pages: 042811
year: 2022
doi: 10.1103/PhysRevA.106.042811
arxiv: '2210.01481'
pdf: PDF_papers/Rahaman-Dutta_2022_Cs-7D32-hyperfine-ac-Stark-767nm.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'Journal reference located 2026-07-30 (Phys. Rev. A 106, 042811; the held
    PDF is the preprint, arXiv:2210.01481 -- confirmed the same paper by its
    A = 7.3509(9) MHz, B = -0.041(8) MHz, ac Stark -49 +- 5 Hz/(W/cm^2) and
    collisional shift -32.6 +- 2.0 kHz/mTorr). Verify the DOI at submission.'
  - 'pdftotext on the held PDF DROPS the +- glyph: the text renders
    "-32.62.0 kHz/mTorr" and "-495 Hz/(W/cm^2)" and "633 um". The true values
    are -32.6 +- 2.0, -49 +- 5, and 63 +- 3 um. Confirmed arithmetically:
    w = 63 um reproduces their stated 16 mm Rayleigh range (633 um would give
    1.64 m), and -1.18(4) MHz/W at 1.5P bidirectional through w = 63 um gives
    -49.5, not -495. The corrupted -495 has propagated to secondary web
    sources -- do not re-derive it from the text layer.'
  - 'Re-verified 2026-08-03 against a fresh full read of the held PDF (86
    pdftotext -layout pages of running text, all of Sections I-V plus both
    supplements). The pdftotext corruption stands: independently rederived
    -49 Hz/(W/cm^2) from I_peak/P = 3/(pi w0^2) with w0 = 63 um and
    kappa = -1.18 MHz/W, matching their stated value to within their quoted
    +-5 rounding. The APS abstract (link.aps.org/doi/10.1103/PhysRevA.106.042811)
    independently confirms Phys. Rev. A 106, 042811, published 17 Oct 2022,
    and quotes the same -49 +- 5 Hz/(W/cm^2) in its own abstract text, so the
    coefficient is now cross-confirmed by three independent readings (this
    PDF, the arithmetic check, and the published abstract) rather than one.
    No other numbers in this file changed. PDF_papers/2210.01481v1.pdf, a
    byte-identical raw-arxiv-named duplicate of the held, correctly-named PDF,
    appeared in PDF_papers/ during this pass and was removed as clutter -- it
    was never referenced by any lit file, the bib, the index, or the
    holdings README, all of which already point to
    Rahaman-Dutta_2022_Cs-7D32-hyperfine-ac-Stark-767nm.pdf.'
verified_date: 2026-08-03
summary: >
  Precision two-photon spectroscopy of Cs 6s -> 7d 2D3/2 at 767 nm (TIFR):
  hyperfine splitting AND the ac Stark shift of the transition measured in one
  experiment, plus the collisional shift and self-broadening. THE closest
  measured analogue of what this programme attempts: ac Stark
  -49 +- 5 Hz/(W/cm^2) (Delta_alpha = 1045 +- 107 a.u.) against our predicted
  51.23 Hz/(W/cm^2) (1093 a.u.) in an identical convention, and self-broadening
  4.18 kHz per 1e12 cm^-3 against our beta_self(6S) anchor of 3.4. They had a
  trustworthy frequency axis and therefore never needed the lineshape.
loci: []
section: prior-art
---

# rahaman2022

Held. Front matter and abstract verified against the preprint (arXiv:2210.01481).

## The system

Rahaman and Dutta (TIFR Mumbai) measure the hyperfine splitting, ac Stark
shift, collisional shift, and self-broadening of the caesium 6s²S₁/₂ →
7d²D₃/₂ two-photon transition at 767 nm, in a single experiment.

A separate paper by Kumar et al. (their ref [25]) reports the Cs 6s-7d
hyperfine structure, with a noted 420 kHz internal inconsistency. Rahaman
and Dutta state that no prior measurement exists of the ac Stark shift or
collisional shift for this transition.

## The numbers

Reduced to this repository's convention ($S_0 = \Delta\alpha I_\text{eff}/2\varepsilon_0 c h$, 1 a.u. = 0.046871 Hz/(W/cm²)):

| quantity | Rahaman & Dutta (Cs 6s–7d₃/₂, 767.8 nm) | this programme (Rb 5S–6S, 993 nm) |
|---|---|---|
| ac Stark, measured | −49 ± 5 Hz/(W/cm²) → Δα = 1045 ± 107 a.u. | never measured |
| ac Stark, calculated | −54 → Δα = 1152 a.u. | −51.23 → Δα = 1093 a.u. |
| self-broadening | 99(6) kHz/mTorr @135 °C → 4.18 kHz per 10¹² cm⁻³ | β_self(6S) = 3.4 ± 0.3 (expectation) |
| self-shift | −32.6 ± 2.0 kHz/mTorr → −1.38 kHz per 10¹² cm⁻³ | never constrained |

Their convention matches this repository's exactly: 1152 a.u. reproduces
54.0 Hz/(W/cm²) through the same conversion constant. Their shift-to-width
ratio, −0.33 of FWHM, predicts an Rb 6S self-shift near −1.1 kHz per
10¹² cm⁻³ and about **32 kHz** across the 70-130 °C archival range. That
figure is the `shift_expected_differential` row of
`results/collisional_shift_bound.csv`, which re-anchors the rate at each
temperature instead of holding it flat, and it is computed rather than
typed: this sentence carried 24 kHz, which is arithmetically the 110-130 °C
span and not the range it names.

**That ratio agrees with classical impact theory rather than differing from
it, and the appearance of a factor of two is a normalisation.** −0.33 of
FWHM is the same quantity as −0.66 of HWHM. The Lindholm-Foley value for a
−C6/R⁶ potential is about −0.73 of HWHM, i.e. −0.36 of FWHM, so measurement
and theory are ten per cent apart. This sentence had compared an
FWHM-referred measurement against an HWHM-referred theory value and read the
resulting two as physics, which in turn licensed calling this an independent
route from the van der Waals model when it is the same physics.

## Method

Scan nonlinearity is identified as the dominant historical error source on
this line. Their remedy:

- the frequency axis is co-recorded on the same oscilloscope trace as the
  signal, referenced to an rf-synthesiser voltage linear in frequency
- the scanning AOM is cat's-eye double-passed, so beam pointing does not
  move with frequency
- power is held to 0.2% across a scan
- results taken over several months are reported stratified by
  oscilloscope acquisition mode, and shown to agree

## Validity

Their temperature range, 50-175 °C with most data at 135 °C, was needed to
resolve a 99 kHz/mTorr slope on a 2 MHz line.

## Use in this record

The calculated Rb 5S-6S ac Stark coefficient (−51.23 Hz/(W/cm²)) falls
within the 1σ band of this paper's measured caesium analogue
(−49 ± 5 Hz/(W/cm²)).
