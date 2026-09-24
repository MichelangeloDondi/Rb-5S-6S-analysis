---
citekey: haupl2025
type: article
authors:
  - Häupl, Daniel R.
  - Higgins, Clare R.
  - Pizzey, Danielle
  - Briscoe, Jack D.
  - Wrathmall, Steven A.
  - Hughes, Ifan G.
  - Löw, Robert
  - Joly, Nicolas Y.
title: 'Modelling spectra of hot alkali vapour in the saturation regime'
journal: New J. Phys.
volume: 27
number: 3
pages: 033003
year: 2025
doi: 10.1088/1367-2630/adb77c
arxiv: '2410.19916'
pdf: PDF_papers/Haupl_2025_hot-alkali-vapour-spectra-saturation-model.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/haupl2025.md  # line-by-line against the held PDF, 2026-09-22: every equation citation and experimental number (beam diameters, temperatures, transit rate) confirmed exactly; no corrections needed
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:2410.19916v1 (25 Oct 2024), the version submitted to NJP;
    the published version (Crossref: NJP 27, 033003, 2025) was not compared. Sections 1,
    2 (Hamiltonian, master equation, transit time, propagation), the beam-shaping
    paragraph of Section 3 and the conclusion read on 2026-09-22. The results figures of
    Section 4 were looked at but not checked value by value.'
verified_date: 2026-09-22
summary: >
  The ElecSus lineage (Durham, Erlangen, Stuttgart) carried beyond the weak probe:
  steady-state Lindblad equations for all hyperfine states in a field, with optical
  pumping, transit time as ONE effective uniform decay rate v/d, Doppler as a
  convolution over the axial velocity, and propagation through ten slices. Tested on
  87Rb D2 at 0.6 T over five decades of intensity, up to 1000 Isat, with three beam
  diameters. The beams are apertured to flat tops so that the intensity is uniform:
  the design removes exactly the intensity distribution this record reads. Software
  public.
loci:
  - P1
  - methods/04
section: method-anchors
---

# haupl2025

VERIFIED for the sections named in the flags. Held (arXiv v1). Read on 2026-09-22.

## What it does

The atomic Hamiltonian, with hyperfine and Zeeman terms, is diagonalized in the uncoupled basis, as in ElecSus. The steady-state Lindblad master equation (Eqs. 1-3) gives the susceptibility (Eqs. 4-6). Transit time enters as an additional uniform "decay" of every state back to the ground manifold at the rate Gamma_t = v/d, the mean transverse speed over the mean chord (Eq. 7), which for a circular beam is sqrt(8 kB T / pi m) / D_FWHM (Eq. 8): about 0.27 MHz, or 3.7 us, for 1 mm at room temperature. The paper states that its simulations showed only marginal differences between this average rate and an integration over the distribution of rates. Doppler broadening is a convolution of the susceptibility over the axial velocity (Eq. 10), and the attenuation of the beam along the 2 mm cell is followed through ten slices (Eq. 11). The experiment uses 87Rb D2 at 0.6 T, in the hyperfine Paschen-Back regime, to isolate open and closed transitions, with iris-cut flat-top beams of 0.5, 1 and 2 mm at 67 and 81 C.

## The numbers

- Agreement between model and data for three beam diameters over five orders of magnitude in intensity, up to about 1000 times saturation (Conclusion).
- The transit rate example: 0.27 MHz for a 1 mm FWHM beam in room-temperature Rb (Section 2.4).

## Use in this record

- The canonical vapour-cell model at high intensity: optical pumping, saturation and transit are in, and the code is public. It is the model the volume model should be compared with on the terms they share.
- Two design choices mark the difference. Transit is one effective rate instead of a kernel that varies across the beam, and the paper reports that averaging costs little in its regime (millimetre flat-top beams, one-photon D2). This record measures the opposite at a 42.4 um Gaussian focus with a light shift, where the averaged kernel gets the third cumulant wrong by about a factor of two (results/kernel_inhomogeneity). The two statements are consistent. The regime decides, and this paper is a clean citation for the regime where averaging works.
- The flat-top beams are chosen so that the intensity is uniform along the cell, which removes the spatial light-shift distribution by construction. That is the canonical instinct this record's programme reverses.

## Limits

- No light shift and no spatially varying intensity by design. Buffer-gas and velocity-changing collisions are left for future work, by the authors' own statement.
