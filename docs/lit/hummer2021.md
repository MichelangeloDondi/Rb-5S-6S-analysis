---
citekey: hummer2021
type: article
authors:
  - Hümmer, D.
  - Romero-Isart, O.
  - Rauschenbeutel, A.
  - Schneeweiss, P.
title: 'Probing Surface-Bound Atoms with Quantum Nanophotonics'
journal: Phys. Rev. Lett.
volume: 126
pages: 163601
year: 2021
doi: 10.1103/PhysRevLett.126.163601
arxiv: '2006.12855'
pdf: PDF_papers/Hummer_2021_probing-surface-bound-atoms-quantum-nanophotonics.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Journal-ref (PRL 126, 163601, 2021) confirmed against the arXiv abstract
    page; not independently Crossref-checked.'
  - 'CITED UNDER A MISCHARACTERISATION. An external literature pass named this
    "the nearest un-applied candidate mechanism" for the unexplained OPTICAL
    linewidth excess in patterson2018 and liu2024. Reading it, that is wrong --
    see the body. The mismatch was not caught until the paper was opened.'
verified_date: 2026-07-31
summary: >
  Theory for atoms WEAKLY BOUND to the surface of a hot optical nanofibre:
  whether their motion normal to the surface is quantized despite phonon
  coupling, and how to probe it by heterodyne fluorescence spectroscopy.
  Innsbruck/Berlin (Romero-Isart, Rauschenbeutel, Schneeweiss). NOT a mechanism
  for the ONF optical-linewidth excess, contrary to how it was billed: every
  linewidth in it is the width of a transition BETWEEN MOTIONAL STATES of an
  adsorbed atom -- transition frequencies of a few hundred kHz, binding
  energies of a few MHz -- limited by phonon-induced DEPHASING rather than
  depopulation. Different physical object from the ~6-10 MHz optical D2 width
  Patterson and Liu cannot account for. Relevant instead to the van der Waals
  BOUND-STATE structure that patterson2018 parameterises with u_0.
loci:
  - P2
section: oist-lineage
---

# hummer2021

VERIFIED against the held arXiv PDF (2006.12855).

## The system

Atoms adsorbed in the van der Waals potential of a hot optical nanofiber, in weakly bound motional states with binding energies of a few MHz. The paper asks whether that motion stays quantized despite coupling to the fiber's thermal vibrations, and how to read out the spectrum.

## The method

Quantization holds in an identified parameter regime with optimized fiber mechanics, limited by phonon-induced dephasing rather than state depopulation. Heterodyne fluorescence spectroscopy through the guided mode can resolve the motional spectrum. The phonon coupling is expanded to second order, giving a motional transition linewidth $\Gamma_{\nu'\nu} = \Gamma^{(1)}_{\nu'\nu} + \Gamma^{(2)}_{\nu'\nu}$: depopulation by one-phonon absorption and emission, plus elastic two-phonon scattering, with the latter dominating. A worked example is the $\nu = 261 \leftrightarrow \nu' = 262$ transition at $\omega_{\nu'\nu} = 2\pi \times 327$ kHz, with the neighboring transition $2\pi \times 39$ kHz away.

## Scope

Every linewidth in the paper is a motional-transition linewidth: frequencies of a few hundred kHz between adjacent bound states, broadened by phonon dephasing, a different quantity from the unexplained excess reported on the optical D2 line by [patterson2018](patterson2018.md) and [liu2024](liu2024.md), at the 2 MHz and 3.4-4.4 MHz scale on a roughly 6 MHz natural width. Transitions of larger frequency become unresolvable as their linewidths grow.

## Use in this record

[patterson2018](patterson2018.md) parameterizes the population of van der Waals bound states with a single scaling $u_0$ and an $r^{-3/2}$ radial form. This paper treats the same states directly, including their quantization and coupling to the fiber's thermal phonons, and is the relevant reference if that bound-state term needs to be more than a one-parameter scaling. It also bears on liu2024's attribution of their excess to surface quality and a possible magnetic origin: a phonon-dephasing channel exists here for adsorbed atoms, but at the frequencies and states this paper treats, it is far too small and narrow-band to produce megahertz of optical width.
