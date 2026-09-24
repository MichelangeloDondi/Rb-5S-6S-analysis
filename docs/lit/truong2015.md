---
citekey: truong2015
type: article
authors:
  - Truong, G.-W.
  - Anstie, J. D.
  - May, E. F.
  - Stace, T. M.
  - Luiten, A. N.
title: 'Accurate lineshape spectroscopy and the Boltzmann constant'
journal: Nat. Commun.
volume: 6
pages: 8345
year: 2015
doi: 10.1038/ncomms9345
arxiv: null
pdf: PDF_papers/Truong_2015_accurate-lineshape-spectroscopy-Boltzmann-constant.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/truong2015.md  # line-by-line against the held PDF, 2026-09-22: one verbatim quotation corrected against a rendered page image and one imprecise I/Isat figure fixed in the summary, all other claims confirmed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published open-access article (nature.com), read in full on
    2026-09-22, main text and Methods. The Supplementary Discussion, where the error
    budget and the second-order correction are derived, is not held.'
verified_date: 2026-09-22
summary: >
  The vapour-cell benchmark for precision line-shape metrology. A shot-noise-limited
  Cs D1 absorption spectrometer (2 ppm in 1 s) shows that the Voigt profile breaks
  down even at I/Isat = 2.8e-3: optical pumping leaves M-shaped residuals and makes the
  fitted Doppler width depend spuriously on the probe intensity, up to about 750 ppm.
  Corrections to second order in intensity, together with modelled etalons, bring the
  residuals to the noise floor and the width's intensity dependence below the
  precision. Boltzmann's constant follows to 6 ppm precision and 71 ppm uncertainty;
  the Lorentz width dominates the budget.
loci:
  - P1
  - methods/02
  - methods/06
section: method-anchors
---

# truong2015

VERIFIED. Held (published version, open access). Main text and Methods read on 2026-09-22.

## What it does

Linear absorption on the Cs D1 line, 6S1/2 to 6P1/2, in a thermally shielded cell at 296 K, with a comb-referenced probe and shot-noise-limited balanced detection (2 ppm in 1 s at the highest power). A two-Voigt fit leaves M-shaped residuals of about 200 ppm near resonance (Fig. 1b) and a fitted Doppler width that grows linearly with the probe intensity (Fig. 2, green). The paper traces both to frequency-dependent optical pumping, which perturbs the atomic lineshape away from a Lorentzian even at I/Isat = 2.8e-3. Adding the first-order intensity correction removes most of the feature. The second-order correction (Eq. 2), written with generalized Voigt profiles, takes the residuals down to about 2 ppm and removes the intensity dependence of the fitted Doppler width below the precision (Figs. 1d and 2). Up to six low-finesse etalons and a quadratic background are fitted as a multiplicative factor (Eq. 1) until the residuals far from resonance are white.

## The numbers

- Excited-state hyperfine splitting: f_HFS = 1167.716(3) MHz.
- Doppler width per 30 s scan: 53 ppm standard error, equal to the scan-to-scan standard deviation, falling to 3.7 ppm after 200 scans.
- Lorentz width fitted from the data: 2.327(7) MHz, against an independent estimate of 2.331(19) MHz (natural 2.287(6) MHz plus laser 0.044(18) MHz). A 1 kHz change in the Lorentz width moves the fitted Doppler width by about 5 ppm.
- Budget for kB (Table 1). Statistical: 5.8 ppm. Lorentz width: 65 ppm when fitted, 190 ppm when taken independently. Laser Gaussian noise: 16 ppm. Optical pumping: 15 ppm. Etalon misidentification: 15 ppm. Total 71 ppm with the fitted Lorentz width, 191 ppm with the independent one.

## Use in this record

- The model-completeness test this record's closure needs: a parameter that must not depend on a knob (here the Doppler width against probe intensity) is fitted at several knob settings, and its slope is the diagnostic of a missing term. Voigt-only gives about 750 ppm. That is the same logic as reading a fitted waist or beta_self against power and temperature in this record.
- Residuals driven to the shot-noise floor by adding physics one term at a time, with the technical terms (etalons) modelled instead of filtered. It is a worked standard for the claim that a line-shape model "includes all of the relevant physics".
- A degeneracy stated in numbers: the homogeneous and inhomogeneous widths trade against each other, 5 ppm of Doppler width per kHz of Lorentz width, and the budget is dominated by that one correlation. This is the kind of pairing the record's identifiability table exists to name before a fit is trusted.
- Canonical in the sense the programme uses: a full-profile fit with the physics in the profile. No moments, and no simulated bias: the model is analytic in the probe intensity.

## Limits

- Weak-probe perturbation theory (corrections to second order in I/Isat), valid far below saturation. This record's 5S-6S drive is not in that regime, where saturation and depletion enter the volume model at full strength.
