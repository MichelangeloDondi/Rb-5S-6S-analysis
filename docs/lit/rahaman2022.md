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

**Held 2026-07-29** (preprint; front matter and abstract read). Rahaman and
Dutta, TIFR Mumbai: the hyperfine splitting and the ac Stark shift of the
6s²S₁/₂ → 7d²D₃/₂ two-photon transition at 767 nm, measured together.

**"Kumar 2022" does not exist, and this note used to invent it.** The summary
here, and the audit's Priority-2 table, treated `arXiv:2210.01481` as a
companion paper by Kumar carrying the ac-Stark and collisional coefficients.
That arXiv ID *is* this paper. Rahaman and Dutta state plainly that "there are
no prior reports on the measurement of ac Stark shift and collisional shift for
the cesium 6s ²S₁/₂ → 7d ²D₃/₂ two-photon transition", so no such companion can
exist. There is a real Kumar *et al.* on Cs 6s–7d **hyperfine structure** (their
ref [25], which they criticise for a 420 kHz internal inconsistency) — a
different paper with different content. Corrected 2026-07-30; the
mean-collapse count drops from five instances to four.

**The numbers, reduced to this repository's convention**
($S_0 = \Delta\alpha I_\text{eff}/2\varepsilon_0 c h$, 1 a.u. =
0.046871 Hz/(W/cm²)):

| quantity | Rahaman & Dutta (Cs 6s–7d₃/₂, 767.8 nm) | this programme (Rb 5S–6S, 993 nm) |
|---|---|---|
| ac Stark, measured | **−49 ± 5 Hz/(W/cm²)** → Δα = 1045 ± 107 a.u. | never measured |
| ac Stark, calculated | −54 → Δα = 1152 a.u. | −51.23 → Δα = 1093 a.u. |
| self-broadening | 99(6) kHz/mTorr @135 °C → **4.18 kHz per 10¹² cm⁻³** | β_self(6S) = 3.4 ± 0.3 (expectation) |
| self-shift | −32.6 ± 2.0 kHz/mTorr → **−1.38 kHz per 10¹² cm⁻³** | never constrained |

Their convention is *identical* to ours — 1152 a.u. reproduces 54.0 Hz/(W/cm²)
through this repo's own conversion constant — so the comparison is exact rather
than approximate, and our unmeasured coefficient sits inside the 1σ band of
their measured one.

Two things this hands us for nothing. Their **shift/width ratio is −0.33 of
FWHM**, which predicts an Rb 6S self-shift of ≈−1.2 kHz per 10¹² cm⁻³, about
24 kHz across the archival 70→130 °C lever — permanently invisible, so C1 is a
bound by physics rather than by bad luck. And −0.66 of HWHM is roughly *twice*
the classical van der Waals impact ratio, which is a live cross-check for M18.
Their temperature span, 50–175 °C with most data at 135 °C, is also the
citation for this repo's 150–170 °C requirement: they needed all of it to
resolve a 99 kHz/mTorr slope on a 2 MHz line.

**And they are the published answer to M20.** Scan nonlinearity is named as the
dominant historical error on this Cs line ("the nonlinearity of the laser
frequency scans", "calibration jitter"), and their remedy is architectural: the
frequency axis is co-recorded on the same oscilloscope trace as the signal from
an rf-synthesiser voltage linear in frequency, the scanning AOM is cat's-eye
double-passed so pointing does not move with frequency, power is held to 0.2%
across a scan, and — the precedent that matters here — the multi-month results
are **published stratified by oscilloscope acquisition mode** and shown to
agree. Treating a scope setting as an experimental variable is exactly what
`window_start_ms` epoching became. Cite them in the methods section that
explains it.

What none of the family does — and what remains this programme's territory — is
treat the shift as a distribution over a focused profile rather than a single
coefficient.
