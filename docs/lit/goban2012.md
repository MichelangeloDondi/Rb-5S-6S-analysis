---
citekey: goban2012
type: article
authors:
  - Goban, A.
  - Choi, K. S.
  - Alton, D. J.
  - Ding, D.
  - Lacroûte, C.
  - Pototschnig, M.
  - Thiele, T.
  - Stern, N. P.
  - Kimble, H. J.
title: 'Demonstration of a state-insensitive, compensated nanofiber trap'
journal: Phys. Rev. Lett.
volume: 109
number: 3
pages: 033603
year: 2012
doi: 10.1103/PhysRevLett.109.033603
arxiv: '1203.5108'
pdf: PDF_papers/Goban_2012_state-insensitive-compensated-nanofiber-trap.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/goban2012.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, all claims and numbers confirmed exactly
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1203.5108v1 (22 Mar 2012). Journal reference and DOI from
    Crossref, 2026-09-22. Main text read in full on 2026-09-22; the appendices in the
    same file (polarization alignment, transmission model, saturation measurement)
    were not read.'
verified_date: 2026-09-22
summary: >
  Caltech's magic, compensated nanofibre trap for Cs, 215 nm from the surface of a
  430 nm fibre. Counter-propagating red (937 nm) and blue (686 nm) beams at magic
  wavelengths remove the differential scalar shift and suppress the vector shift by
  about 250. The D2 absorption line is then unshifted (0 +/- 0.5 MHz) and 5.7(1) MHz
  wide against 5.2 MHz in free space, where the uncompensated trap gave a 13 MHz shift
  and a 20 MHz width. The residual width is budgeted to decay into the fibre, tensor
  shifts, Casimir-Polder and probe noise.
loci:
  - P2
section: deep-search
---

# goban2012

VERIFIED for the main text. Held (arXiv v1). Read on 2026-09-22.

## What it does

The trap is designed in lacroute2012. A pair of counter-propagating x-polarized beams at the red magic wavelength, 937 nm (0.4 mW each), forms a 1D lattice. A pair of blue-detuned beams at the 686 nm magic wavelength (5 mW each) is detuned from each other by 382 GHz, so their standing wave averages out and the light is effectively linear everywhere. That suppresses the vector shifts by delta_fb / delta_blue, about 4e-3. The potential, computed from the full scalar, vector and tensor light-shift Hamiltonian with the Casimir-Polder surface term, is -0.27 mK deep at about 215 nm from the surface, with trap frequencies {199, 273, 35} kHz. A 0.1 pW probe on 6S1/2 F=4 to 6P3/2 F'=5 is sent through the fibre and photon-counted.

## The numbers

- Linewidth 5.7(1) MHz averaged over four data sets, against 5.2 MHz in free space. The shift of the transition is 0 +/- 0.5 MHz. For the uncompensated, non-magic Cs trap of the earlier nanofibre work, the paper quotes a shift of about 13 MHz and a width of about 20 MHz.
- Residual-width budget: decay into the fibre's guided modes is about 0.35 MHz (5.3 MHz predicted in total). Tensor shifts of the F'=5 manifold are about 0.7 MHz. Casimir-Polder is about 0.1 MHz. Probe technical noise is about 0.3 MHz.
- Optical depth is 66(17). N = 224(10) atoms from saturation. Optical depth per atom is 7.8(13) per cent.
- Lifetime 12(1) ms, or 140(11) ms with pulsed polarization-gradient cooling.

## Use in this record

- The suppression counterpart of lee2015. With magic wavelengths and counter-propagating compensation, the light-shift distribution that lee2015 reads off an asymmetric Rb line shrinks to a residual of under 1 MHz. This is the canonical state of the art the nanofibre arm is set against. Síle's programme works in this family of two-colour traps, and the magic power ratio for the 5S-6S pair is one of the items this record says it can give her.
- A near-surface term with a number on it: Casimir-Polder broadening of about 0.1 MHz at 215 nm on the D2 line. The nanofibre version of this record's volume model has to carry the surface term with its own spread over the trap site.

## Limits

- The residual-width contributions are estimates, not a fitted decomposition.
- D2 of Cs is not this record's transition. What carries over is the method (magic compensation and vector cancellation), not the numbers.
