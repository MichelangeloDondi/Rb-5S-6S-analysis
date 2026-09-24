---
citekey: juszkiewicz1993
type: article
authors:
  - Juszkiewicz, R.
  - Bouchet, F. R.
  - Colombi, S.
title: 'Skewness Induced by Gravity'
journal: The Astrophysical Journal
volume: 412
pages: L9--L12
year: 1993
doi: 10.1086/186927
arxiv: 'astro-ph/9306003'
pdf: PDF_papers/Juszkiewicz_1993_skewness-gravity-tophat-window-S3-perturbation-theory.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/juszkiewicz1993.md  # line-by-line against the held PDF, 2026-09-22; the whole paper (pp.1-10) was read to settle whether it carries the log-derivative form of S3 -- it does not, but its own eq.9 and eq.13 are confirmed, and eq.13's (3+n) form is now correctly distinguished from bernardeau1994's explicit gamma_1
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-4 of the held PDF (arXiv:astro-ph/9306003v1, 8 Jun 1993, "Accepted for publication
    in Ap. J. Letters") read directly on 2026-09-21: title, author list, abstract, Section 1
    (Introduction) and Section 2 (Perturbation theory) through the top-hat/coherence-length
    expansion (their eq. 9) and the start of Section 3 (power-law clustering models, eq. 10-11).
    Pages 5-10 (the rest of Section 3, the N-body comparison, and the conclusions) were not read.'
  - 'AUDIT, 2026-09-22: pages 5-10 (the rest of Section 3, eq. 12-17; Section 4, the N-body
    comparison; Section 5, the discussion; the references) read in full to settle whether this
    paper gives S3''s dependence on smoothing scale through a logarithmic derivative. It does not:
    a full-text search of the extracted PDF for "logarithm" and "derivative" returns zero
    occurrences anywhere in the paper. Eq. 13 (p. 5), S3 = 4 + 4*kappa(Omega) - (3+n) for a
    power-law spectrum P(k) prop. k^n with a top-hat window, is confirmed exact; it is expressed
    through the spectral index n, never through d ln sigma^2/d ln R. See the audit file for the
    settled cross-reference to bernardeau1994.'
verified_date: 2026-09-21
summary: >
  Defines the skewness factor S_3 = <delta^3>_c/<delta^2>^2 of a top-hat-SMOOTHED cosmic density
  field and derives it as an integral of the unsmoothed bispectrum against the window's Fourier
  transform at both wavenumbers (their eq. 5), then a closed-form small-window correction,
  S_3 = 4 + 4*kappa(Omega) - 2(R/R_c)^2 + O(R/R_c)^4, where R_c = sigma/sigma_1 is a "coherence
  length" (eq. 9). The direct cosmological precedent for a windowed, amplitude-free moment ratio
  whose window-dependence is a derived closed form rather than a fitted nuisance.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# juszkiewicz1993

VERIFIED for pages 1-4 (title through the start of Section 3). Held preprint, arXiv:astro-ph/9306003.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | ApJ **412**, L9 (1993), a Letter | p. 1 header, "Accepted for publication in Ap. J. Letters" |
| affiliations | Copernicus Center Warsaw; Institut d'Astrophysique de Paris; Institute for Advanced Study, Princeton | p. 1 |
| skewness definition | S_3 = <delta^3> / <delta^2>^2 | p. 3, eq. following "We define the *skewness factor* as..." |
| window kernel | S_3 = integral of P(k) P(k') W_k W_k' W\|k-k'\| T(k,k') + O(sigma^2) | p. 3, eq. 5 |
| small-window limit | S_3 = 4 + 4 kappa(Omega) - 2(R/R_c)^2 + O(R/R_c)^4 | p. 4, eq. 9 |

## What it says, in its own terms

Abstract (verbatim, p. 1): "We investigate how gravitational instability drives the distribution
of these fluctuations away from the initial state, assumed to be Gaussian. Using second order
perturbation theory, we calculate the skewness factor, S3 = <delta^3>/<delta^2>^2... We show that
S3 decreases with the slope of the fluctuation power spectrum; it depends only weakly on Omega,
the cosmological density parameter. We compare perturbative calculations with N-body experiments
and find excellent agreement over a wide dynamic range."

The object being measured is explicitly a smoothed field: "We distinguish the mass density
contrast field, delta-rho/rho, from the spatially smoothed field, delta. While the former is not
directly observable, the latter may be" (p. 2), built as a volume average of the m-point
correlation functions, eq. 1: <delta^m> = integral [dv_1...dv_m / v^m] xi_m(x_1,...,x_m), with the
filter F one of those the paper describes, in the plural, as "spherically symmetric, sweep a unit
volume" (eq. 2-3, p. 2). Three window shapes
are carried explicitly: no filtering (W_k=1), a top hat (W_k = (3/kR) j_1(kR)), and a Gaussian
(p. 3).

The window enters S_3 through three factors of its Fourier transform in the bispectrum integral
(eq. 5, p. 3), and the resulting small-window (R << R_c) expansion is a tidal correction that
"lower[s] S_3", stronger for "fields with smaller coherence length", and the paper states
explicitly: "S_3 is anticorrelated with the relative amount of small-scale power" (p. 4).

## The logarithmic-derivative question, settled (audit, 2026-09-22)

The strategy document that commissioned this search describes the top-hat window's effect on S_3
as entering through the top-hat window's logarithmic derivative (not this paper's own phrasing,
see below). This paper never uses that
form: a full-text search of the whole held PDF (all 10 pages, title through references) for the
two words `logarithm` and `derivative` returns zero hits. The window enters S_3 in exactly two forms here:
through R/R_c (a ratio of the field's rms value to its gradient's rms value, eq. 9, p. 4) for a
general spectrum, and, for power-law (scale-free) spectra P(k) prop. k^n with a top-hat window,
through the spectral index n directly (eq. 13, p. 5): S_3 = 4 + 4*kappa(Omega) - (3+n). Eq. 13 is
mathematically the same content as minus the logarithmic derivative of the variance (again, not
this paper's own phrasing), for a
top-hat-windowed power-law spectrum, d ln sigma^2/d ln R = -(n+3) is a standard identity, but
this paper never performs or names that identification. It works entirely in n.

**bernardeau1994 is confirmed as the paper that carries the explicit logarithmic-derivative form.**
Its eq. (42) (p. 12) defines gamma_p = d^p log sigma^2(R_0) / d log^p R_0, the p-th logarithmic
derivative of the variance with the smoothing scale, and the unnumbered display immediately
below it, opening Section 3.3 "Example of cumulants" (p. 13), gives S_3 = 34/7 + gamma_1. This is
exactly the "more familiar textbook form" this section used to speculate about, now read directly
off the source instead of inferred. One correction to the speculation itself: gamma_1 there
carries NO leading minus sign (gamma_1 = +d ln sigma^2/d ln R, not gamma_1 = -d ln sigma^2/d ln R
as this section previously guessed), consistent with this paper's own eq. 13, since at Omega=1,
4+4*kappa(1) = 34/7 and d ln sigma^2/d ln R = -(n+3) for a top-hat-windowed power law, so
S_3 = 34/7 - (3+n) = 34/7 + [d ln sigma^2/d ln R] only if gamma_1 carries no extra sign.

## Use in this record

This is the cosmological precedent for exactly this record's central move: an amplitude-free
ratio of windowed moments (S_3, the direct analogue of this record's mu_3/mu_2^(3/2)-type
combinations), whose bias under the window is not fitted away but derived in closed form from the
window's own shape (eq. 9), with the unwindowed limit recovered as R/R_c -> 0. The mechanism,
truncation/smoothing suppresses a higher moment by a calculable geometric factor instead of an
unknown nuisance, is structurally the same claim this record's window-limit derivations
(`docs/methods/11_the_window_limits.md`) make for the truncated-frequency window on a two-photon
lineshape, independently arrived at in gravitational large-scale structure thirty years earlier.
The physical objects (a cosmological density bispectrum vs. an atomic lineshape's light-shift
distribution) and the truncation geometry (a real-space top hat vs. a frequency-domain rectangle)
are unrelated. The borrowed structure is the general principle that a window's effect on a
moment ratio is a computable, not a fitted, quantity.
