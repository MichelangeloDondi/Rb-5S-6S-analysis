---
citekey: kaplan2005
type: article
authors:
  - Kaplan, A.
  - Andersen, M. F.
  - Grünzweig, T.
  - Davidson, N.
title: 'Hyperfine spectroscopy of optically trapped atoms'
journal: J. Opt. B
volume: 7
number: 8
pages: R103-R125
year: 2005
doi: 10.1088/1464-4266/7/8/R01
arxiv: 'physics/0409146'
pdf: PDF_papers/Kaplan_2005_hyperfine-spectroscopy-optically-trapped-atoms.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/kaplan2005.md  # line-by-line against the held PDF, 2026-09-22: one imprecise Limits-section sentence corrected (claimed Sections 8-13 wholly unread, contradicting the flags' own "start of Section 9"); every other equation, Table 1 and Fig. 7-9 number confirmed exactly, and the frontmatter cross-checked against Crossref
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:physics/0409146v1 (28 Sep 2004), a 49-page review. The
    journal reference and DOI are from Crossref, 2026-09-22. Read on 2026-09-22:
    Sections 2.5, 4, 5 and 6 in full, and the start of Section 9. The quantum model
    (8), the rest of the Ramsey treatment (9), echo spectroscopy (10) and quantum
    dynamics (11 and 13) were not read and nothing below rests on them.'
verified_date: 2026-09-22
summary: >
  Weizmann review of microwave spectroscopy of 85Rb in far-detuned dipole traps,
  where the hyperfine levels see slightly different light shifts. A stationary model
  gives the ensemble shift through a darkness factor (<U>/<E_k>) and the inhomogeneous
  width as the spread of the potential, sqrt(<U^2> - <U>^2), with a stated validity
  condition that the trap frequency be much smaller than that width. Trap geometry
  alone moves the width from kHz to 47 Hz. A weak mode-matched beam tuned between
  the hyperfine levels cancels the differential shift: the first and second moments
  of the Rabi line are nulled, down to a Fourier-limited 13 Hz.
loci:
  - THEORY
  - methods/09
section: prior-art
---

# kaplan2005

VERIFIED for the sections named in the flags. Held (arXiv v1). Read on 2026-09-22.

## What it does

Section 2.5 writes the ground-state light shift of a multi-level atom (Eqs. 18-21). The two hyperfine levels have detunings differing by the hyperfine splitting, so they "feel" slightly different trap shapes, and a thermal ensemble dephases on the microwave transition much faster than photon scattering would make it.

Section 4 builds a stationary classical model: atoms frozen during a pulse short against the trap period, and in thermal equilibrium. The ensemble shift is (omega_HF / hbar delta)(3/2) kB T kappa, with the darkness factor kappa = <U>/<E_k> (Eqs. 27-28). The inhomogeneous width is the spread of the potential, sigma = (omega_HF / hbar delta) sqrt(<U^2> - <U>^2) (Eq. 30), which in a harmonic trap is (omega_HF / delta) sqrt(3/2) kB T / hbar (Eq. 32). Its ratio to the scattering rate is of order omega_HF / gamma, about 1e3 (Eq. 33), so the light-shift spread and not scattering limits the coherence. The model is valid and useful only when the oscillation frequency is much smaller than sigma (Eq. 34).

Section 5 compares four geometries at 1 W, 5 uK and a depth of three times the mean kinetic energy (Table 1). The inhomogeneous width is 1.9 kHz for a red-detuned crossed trap, 5 kHz for a Laguerre-Gaussian trap, 3.8 kHz for a rotating-beam trap and 47.2 Hz for an "optimal" dark trap.

Section 6 adds a weak beam, mode-matched to the trap and tuned midway between the hyperfine levels. At the intensity ratio eta, about (omega_HF / 2 delta)^2 (Eq. 36), it cancels the differential shift everywhere. The experiment: 785 nm, 50 mW, w0 = 50 um, U0 about 34 uK. A 3 ms Rabi line of trapped atoms is shifted by -756 Hz and widened to an RMS width of 320 Hz, against 110 Hz Fourier-limited. The compensating beam, 25 +/- 10 nW, brings both back (Figs. 7-8). With 25 ms pulses the width is 13 Hz, a 25-fold narrowing, and 50 ms is nearly Fourier limited. The paper notes that a magic wavelength does the same with one laser, where one exists.

## Use in this record

- The moments of a light-shift line as control observables: Fig. 8 tunes the compensating power by nulling the line centre and the RMS width of the Rabi spectrum together, the first two moments of the shift distribution. This record reads the higher ones as well.
- Eq. (30) is the second-moment counterpart of this record's ramp variance for a trapped ensemble, and the darkness factor is the geometric knob that sets it. Table 1 shows a geometry lever of about 40 in the width at fixed power and depth, which is the kind of lever the record's exponent table prices.
- Eq. (34), trap motion slow against the shift spread, is the trapped-atom analogue of this record's quasi-static condition on the ramp (S0^2 much larger than the transit kernel's variance term). It is the regime statement a trapped-atom version of the moment programme would need to make first.
- For a guided-atom group, this is the suppression side of the ledger: geometry, compensation, magic wavelengths. The programme's stance, reading the distribution instead of cancelling it, is set against it.

## Limits

- The stationary model neglects motion during the pulse. The paper treats the quantum and dynamical regimes separately in Section 8 and the rest of Sections 9 to 13, which were not read here.
- The Table 1 numbers are calculations for idealized geometries, and gravity raises them by 10 to 60 per cent for Rb, as the paper states.
