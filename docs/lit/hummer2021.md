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

**Read from the held arXiv PDF (2006.12855)**, after it had already been cited
here on someone else's description of it.

## What it actually does

Atoms adsorbed in the van der Waals potential of a **hot** optical nanofibre,
in weakly bound motional states with binding energies of a few MHz. The
questions are whether the motion normal to the surface stays **quantized**
despite coupling to the fibre's thermal vibrations, and how to read that
spectrum out. Their answers: it can be, in an identified parameter regime with
optimised fibre mechanics; the limiting broadening is **phonon-induced
dephasing rather than state depopulation**; and heterodyne fluorescence
spectroscopy through the guided mode can resolve the motional spectrum.

The machinery is a phonon coupling expanded to second order, giving a motional
transition linewidth $\Gamma_{\nu'\nu} = \Gamma^{(1)}_{\nu'\nu} + \Gamma^{(2)}_{\nu'\nu}$ —
depopulation by one-phonon absorption and emission,
plus elastic two-phonon scattering, the latter dominating. Worked example: the
$\nu = 261 \leftrightarrow \nu' = 262$ transition at
$\omega_{\nu'\nu} = 2\pi \times 327$ kHz, with the neighbouring transition
$2\pi \times 39$ kHz away.

## Why it is not the mechanism it was taken for

**Every linewidth in this paper is a motional-transition linewidth.** The
frequencies are hundreds of kHz between adjacent bound states; the broadening
is phonon dephasing of *that* transition. [patterson2018](patterson2018.md) and
[liu2024](liu2024.md) report an unexplained excess on the **optical** D2 line,
at the ~2 MHz and ~3.4–4.4 MHz scale on top of a ~6 MHz natural width. These
are different objects, and nothing here converts one into the other. The paper
makes no claim about the optical linewidth of near-surface atoms.

Its own statement of the limit runs the opposite way to the billing: transitions
"with larger frequencies can no longer be resolved due to their increasing
linewidths", which is why they restrict to binding energies of a few MHz. The
broadening is the obstacle to *their* proposal, not an explanation of anyone
else's excess.

## Where it is genuinely relevant

[patterson2018](patterson2018.md) parameterises the population of van der Waals
**bound states** with a single scaling $u_0$ and an $r^{-3/2}$ radial form,
having calculated the bound-state wavefunctions numerically. This paper treats
those same states properly — their quantization, their coupling to the fibre's
thermal phonons, and the conditions under which the ladder is resolvable at all.
If Patterson's bound-state term ever needs to be more than a one-parameter
scaling, this is the reference for it.

**It also weakens a rival explanation rather than supporting one.** Liu
attributes their excess to surface quality and "likely ... magnetic origin". A
phonon-dephasing channel exists here for adsorbed atoms, so a surface/thermal
route to broadening is not absurd — but at the frequencies and for the states
this paper treats, it is far too small and too narrow-band to produce megahertz
of optical width. Recorded so the connection is not assumed later.
