---
citekey: hilton2018
type: article
authors:
  - Hilton, A. P.
  - Perrella, C.
  - Benabid, F.
  - Sparkes, B. M.
  - Luiten, A. N.
  - Light, P. S.
title: 'High-efficiency cold-atom transport into a waveguide trap'
journal: Phys. Rev. Applied
volume: 10
number: 4
pages: 044034
year: 2018
doi: 10.1103/PhysRevApplied.10.044034
arxiv: '1802.05396'
pdf: PDF_papers/Hilton_2018_cold-atom-transport-into-hollow-core-fibre.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/hilton2018.md  # line-by-line against the held PDF, 2026-09-22; no corrections needed, all claims confirmed, including an independent cross-check of the journal/volume/number/pages fields against hilton2020's own reference list and against Crossref
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1802.05396v2 (31 Oct 2018). Journal reference and DOI from
    Crossref, 2026-09-22. Main text Sections I to VII and the start of Appendix A read
    on 2026-09-22; Appendices B and C (overlap and simulation details) not read.'
  - 'Appendices B and C read in full for the audit, 2026-09-22: both consistent with the
    main-text claims and with the "(Section III and Appendix B)" citation, since Section
    III itself points to Appendix B for the same diminishing-returns argument.'
verified_date: 2026-09-22
summary: >
  The hollow-core-fibre loading benchmark: 3.3(1)e6 cold 85Rb atoms, about 3 per
  cent of the MOT, guided into 10 cm of 45 um kagome fibre by a >1 W guide 1 THz red
  of D1, reaching an optical depth of 600(10). A Monte Carlo of 1e5 atoms with no free
  parameters reproduces the loading against guide power and wavelength, and names
  the limit, the geometric overlap of cloud and guide. The guide's inhomogeneous
  light shift is avoided by probing in the dark. The same group's hilton2020 reads it
  instead.
loci:
  - methods/09
section: lan-platforms
---

# hilton2018

VERIFIED for the main text. Held (arXiv v2). Read on 2026-09-22.

## What it does

A 3D MOT of 1e8 85Rb atoms in a 2 mm cloud, cooled below 5 uK by polarization-gradient cooling, falls 25 mm onto the tip of a 10 cm kagome fibre with a 45 um core and more than 70 per cent coupling into the fundamental mode at 780 nm (Section II). A guide beam of more than 1 W, 1 THz red of D1, is coupled from below. It diverges out of the fibre into a self-aligning optical funnel, 20 uK deep at the MOT. Ten MOT and cooling settings are optimized by a neural-network learner. A 5 nW D2 probe goes through the fibre with the guide suppressed by 90 dB. The guide's transverse intensity would broaden the probe line inhomogeneously, so the guide is chopped and the probe runs in the dark, stepping 144 MHz in 100 us with 30 ns AOM switching. No spatial-mode filter is used, because lensing in the large core would overestimate the optical depth.

A Monte Carlo (Section IV) of 1e5 atoms drawn from the measured cloud size and temperature integrates motion in the dipole potential (Eqs. 1-2) with gravity, photon scattering and background-gas loss. It reproduces the absorption images and the in-fibre spectra (Fig. 2) and the loading against guide power and wavelength (Fig. 3) with no free parameters.

## The numbers

- Peak optical depth 600(10). 3.3(1)e6 atoms in the fibre, about 3 per cent of the MOT (Section III).
- Only 3.2 per cent of the initial cloud sees a trap depth above the mean temperature: the loading is limited by the geometric overlap (Section III and Appendix B).
- Loss after loading (Eq. 3): a one-body rate of 7.6(2) per second, read as background N2 in the fibre at 1.4(2)e-7 Torr against 2.0(2)e-8 Torr in the chamber. A wavelength-dependent two-body (photoassociation) coefficient between 5e-11 and 2e-9 cm^3/s, which the paper calls qualitative (Section V).
- Photon scattering from the guide limits coherence to about 200 us. A simulated hollow blue-detuned guide of the same peak intensity raises the time between scattering events to about 10 ms (Section VI).

## Use in this record

- The reference point for the thesis's hollow-core-fibre chapter (chapter 4). The Bologna apparatus reports a dipole-trap loading efficiency of 0.161(5) per cent and no transport into the core yet. This paper is the published efficiency into the core, and its diagnosis (geometric overlap, fixable by densifying the MOT) is the comparison a reader in the field will make.
- A precedent for the twin's role: a simulation with no free parameters guided the experiment's design and named its limit. That is how this record argues for its twin, here done in a guided-atom apparatus.
- The pair with hilton2020 makes a clean contrast for the application. The same group first avoids the guide's light-shift broadening by probing in the dark, then reads it as a thermometer.

## Limits

- The atom number comes from the optical depth through an overlap model (Appendix A) that assumes a Gaussian radial density.
- The photoassociation coefficient is a two-parameter fit over a chosen window, which the paper calls qualitative.
