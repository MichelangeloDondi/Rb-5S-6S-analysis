---
citekey: lacroute2012
type: article
authors:
  - Lacroûte, C.
  - Choi, K. S.
  - Goban, A.
  - Alton, D. J.
  - Ding, D.
  - Stern, N. P.
  - Kimble, H. J.
title: 'A state-insensitive, compensated nanofiber trap'
journal: New J. Phys.
volume: 14
number: 2
pages: 023056
year: 2012
doi: 10.1088/1367-2630/14/2/023056
arxiv: '1110.5372'
pdf: PDF_papers/Lacroute_2012_compensated-nanofiber-trap-magic-wavelengths.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/lacroute2012.md  # line-by-line against the held PDF, 2026-09-22: one bias-fields overclaim and a verify_flags scope understatement fixed; all quotations confirmed verbatim
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1110.5372v1 (24 Oct 2011). Journal reference and DOI from
    Crossref, 2026-09-22. Read on 2026-09-22: abstract, Section 1, the light-shift
    Hamiltonian of Section 2 (Eq. 3 and the tensor-term paragraph), Sections 2.4-2.5
    in part, and Section 3.2 through its Fig. 8 azimuthal-splitting discussion. The
    remaining ab initio trap figures and the coherence-time estimates were not read.'
verified_date: 2026-09-22
summary: >
  The design paper behind goban2012. In a nanofibre's evanescent field the
  longitudinal component, out of phase with the transverse one, makes the local
  polarization elliptical even for linear input. The resulting vector shift acts as a
  fictitious magnetic field and broadens the ground-state Zeeman sublevels
  inhomogeneously. A backward-propagating beam, detuned slightly, cancels it; magic
  wavelengths cancel the differential scalar shift. The tensor term vanishes for J=1/2
  at large detuning, so on the Cs D2 line it acts only on the excited state.
loci:
  - P2
section: deep-search
---

# lacroute2012

VERIFIED for the sections named in the flags. Held (arXiv v1). Read on 2026-09-22.

## What it does

Section 1 states the mechanism. The strongly guiding fibre gives evanescent fields a longitudinal component E_z out of phase with the transverse one, so the local polarization is elliptical even for linear input. The vector shift that follows is a "fictitious magnetic field", an inhomogeneous Zeeman broadening that varies on sub-wavelength scales and so is difficult to cancel with bias fields. The scheme cancels the differential scalar shift with magic wavelengths, and the vector shift of a forward-propagating blue field with a backward-propagating one detuned by a small delta_fb. Section 2 gives the vector term proportional to the ellipticity (Eq. 3) and notes that for elliptical light it can be as large as the scalar shift. The tensor term vanishes for F = 1/2 and, at detunings large compared with the excited hyperfine structure, for J = 1/2, so on the Cs D2 line it acts only on 6P3/2. Section 3.2 revisits the earlier non-magic trap (1064 nm lattice, 2 x 2.2 mW, and one 780 nm blue beam, 25 mW, on a 250 nm-radius fibre, 0.4 mK deep at 230 nm). Its ground sublevels split strongly away from the two azimuthal trap minima, and its excited state is not trapped at all.

## Use in this record

- For the nanofibre arm of the 5S-6S programme: both levels are J = 1/2, so the tensor term drops out by the paper's own argument, but the vector term does not. The evanescent ellipticity is a property of the fibre mode, not of the input polarization. So a nanofibre version of this record's shift distribution needs the differential vector polarizability of 5S1/2 and 6S1/2 weighted by the local ellipticity, not the scalar term alone. The requirement is stated here. The size is not settled.
- Background for goban2012 and lee2015: why an uncompensated Rb nanofibre trap gives the asymmetric line lee2015 reads, and what compensation removes.

## Limits

- The design is for Cs D2. The 5S-6S magic conditions and vector coefficients have to come from this record's polarizability code, not from this paper.
