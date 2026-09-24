---
citekey: noaman2018
type: article
authors:
  - Noaman, Mohammad
  - Langbecker, Maria
  - Windpassinger, Patrick
title: 'Micro lensing induced lineshapes in a single mode cold-atom hollow-core fiber interface'
journal: Opt. Lett.
volume: 43
number: 16
pages: 3925
year: 2018
doi: 10.1364/OL.43.003925
arxiv: '1805.11391'
pdf: PDF_papers/Noaman_2018_micro-lensing-lineshapes-cold-atom-hollow-core-fibre.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/noaman2018.md  # line-by-line against the held PDF, 2026-09-22: one title-transcription fix (preprint has no internal hyphens); all other claims, quotes, figure and equation citations confirmed
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1805.11391v1 (29 May 2018), read in full on 2026-09-22.
    Journal reference and DOI from Crossref the same day; the title is transcribed
    from this preprint exactly (no internal hyphens, lineshapes as one word) and
    the published Opt. Lett. wording was not compared.'
verified_date: 2026-09-22
summary: >
  An asymmetric absorption line in a single-mode hollow-core-fibre interface that is
  NOT a light-shift distribution. A dense cold 87Rb cloud acts as a
  detuning-dependent lens on the probe (focusing on one side of resonance,
  defocusing on the other), and the fibre's mode selection turns that lensing into
  transmission. A paraxial propagation model through the cloud's susceptibility
  reproduces the asymmetry, including a false peak near -15 MHz, and shows a
  Lorentzian fit overestimating the optical depth for clouds under 14 um. The same
  effect distorts Rydberg EIT lines.
loci:
  - methods/09
section: lan-platforms
---

# noaman2018

VERIFIED. Held (arXiv v1). Read in full on 2026-09-22.

## What it does

About 1e5 atoms of 87Rb are carried by a movable optical lattice to about 5 mm from, or into, a hollow-core fibre with a 60 um core and a mode-field diameter near 42 um. They are probed on 5S1/2 F=2 to 5P3/2 F=3 with about 200 pW coupled into the same fundamental mode, and detected on a fibre-coupled PMT. The model (Eqs. 1-6) propagates the probe through a Gaussian cloud with the two-level susceptibility, using the paraxial equation solved by split-step, and then projects the emerging field onto the unperturbed mode (the overlap integral eta of Eq. 6). Near resonance the cloud's refractive index focuses the beam on one side and defocuses it on the other (Fig. 2), so the transmitted fraction depends on detuning and density as well as on absorption.

## The numbers

- For the densest clouds the transmission develops an extra off-resonant feature near -15 MHz and a strong asymmetry, which the model reproduces and a Lorentzian cannot (Fig. 3a).
- For radial cloud sizes below about 14 um, a Lorentzian fit overestimates the peak optical depth significantly (Fig. 3c).
- The behaviour persists with the atoms inside the fibre (Fig. 3b). With a 480 nm control beam on 29S1/2, the Rydberg EIT lines show the same lensing asymmetry, which the paper notes is often attributed to Rydberg interactions instead (Fig. 4, Eq. 7).

## Use in this record

- A term the shape channel has to rule out before a skewness is read as a shift distribution in a guided geometry: propagation through a dense, dispersive sample filtered by a single mode produces odd asymmetry on its own. It scales with density and cloud size, so a density knob separates it from a light-shift term, which scales with intensity.
- Background for the host group's platform: the same single-mode, hollow-core interface as xin2018 and hilton2018. Hilton2018 cites the lensing problem as its reason for not mode-filtering.

## Limits

- Cold, dense, near-resonant sample with a one-photon probe. In a hot vapour cell at 993 nm two-photon excitation, dispersion on the drive is negligible. The effect matters for this record only in the guided, cold arms.
