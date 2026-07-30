---
citekey: weller2011
type: article
authors:
  - Weller, Lee
  - Bettles, Robert J.
  - Siddons, Paul
  - Adams, Charles S.
  - Hughes, Ifan G.
title: 'Absolute absorption on rubidium D1 line: including resonant dipole-dipole interactions'
journal: J. Phys. B At. Mol. Opt. Phys.
volume: 44
number: 19
pages: 195006
year: 2011
doi: 10.1088/0953-4075/44/19/195006
arxiv: '1107.3092'
pdf: PDF_papers/Weller_2011_Rb-D1-absolute-absorption-self-broadening-coefficient.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'Journal/volume/pages taken from the standard record for arXiv:1107.3092; the arXiv ID and the coefficient are read from the PDF. VERIFY the journal line at submission.'
verified_date: 2026-07-26
summary: >
  Absolute Rb D1 absorption to 170 C and 3e14 cm^-3; extracts the RESONANT
  dipole-dipole self-broadening coefficient beta/2pi = (0.69 +/- 0.04)e-7
  Hz cm^3, agreeing with impact theory to 0.1% in the spectra.
loci: []
section: collision-series
---

# weller2011

**Read here 2026-07-26.** Verbatim: "Analysis of the absolute absorption
spectra allow us to ascertain the value of the self-broadening coefficient for
the rubidium D1 line: **beta/2pi = (0.69 +/- 0.04) x 10^-7 Hz cm^3**, in
excellent agreement with the theoretical prediction." Spectra match theory to
0.1% up to 3e14 cm^-3, over temperatures to ~170 C.

**Audited against the PDF 2026-07-30.** The quotation above is verbatim, and
every number checks. Three things worth adding that the note did not carry:

- **Their Table gives theory alongside measurement for three alkalis**, which is
  what makes this a *calibration* of the impact-theory prediction rather than a
  single number: Rb D1 theory 0.73 against measured **0.69 ± 0.04** (this work);
  Rb D2 theory 1.03 against 1.10 ± 0.17; Na D1 0.51 / 0.49 ± 0.07; Cs D1
  0.83 / 0.75 ± 0.11 — all in $10^{-7}$ Hz cm³. Theory is good to a few percent
  across the series, which is the reason it can be extrapolated at all.
- **The same fit returns the natural linewidth as its intercept**,
  $\Gamma_0/2\pi = (5.7 \pm 0.7)$ MHz, against 5.75 MHz for the Rb D1 line. A
  linewidth-vs-density fit that recovers the natural width from the intercept is
  the same construction this programme uses for $\beta_{\rm self}$, and it is
  worth citing as precedent for the method and not only for the coefficient.
- **Why it bounds 6S from above.** Their coefficient is *resonant*
  dipole-dipole on an allowed D1 transition, the strongest case there is: the
  ground state is one of the two levels, so every ground-state atom is a
  perturber in resonance. The 5S–6S pair has no such resonant channel, so the 6S
  self-broadening coefficient should sit **below** this, and 0.69e-7 Hz cm³ is a
  ceiling rather than an estimate. That is the sense in which `LITERATURE.md`
  §5.2 calls it an anchor "from above", and the reasoning is recorded here
  because the phrase alone does not carry it.

**Why it matters here: it is the UPPER anchor for the expected 6S scale.**
0.69e-7 Hz cm^3 is **69 kHz per 1e12 cm^-3** -- and D1 is the *resonant*
dipole-dipole case, the largest such mechanism, because the ground and excited
states are dipole-coupled to each other. A 5S-6S self-broadening coefficient
cannot work that way: both states are S, so there is no resonant dipole
coupling and the interaction is van der Waals, which should place it well
below this figure. That independently supports the ~kHz-per-1e12 expectation
this programme has been quoting from the Zameroski 7S analogy alone, and it
frames the archival bound (0.2-0.4 MHz per 1e12) as loose by the stated
15-30x rather than by guesswork.

**Second use: the temperature range is the one PLAN wants.** Their absolute
absorption method works to 170 C and 3e14 cm^-3 -- the regime PLAN section 8
proposes for the high-density lever -- so it is also a methodological
reference for getting the density scale right up there, where the
vapour-pressure correlation carries its own systematic.
