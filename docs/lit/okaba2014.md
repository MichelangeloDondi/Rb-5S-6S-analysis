---
citekey: okaba2014
type: article
authors:
  - Okaba, Shoichi
  - Takano, Tetsushi
  - Benabid, Fetah
  - Bradley, Tom
  - Vincetti, Luca
  - Maizelis, Zakhar
  - Yampol'skii, Valery
  - Nori, Franco
  - Katori, Hidetoshi
title: 'Lamb-Dicke spectroscopy of atoms in a hollow-core photonic crystal fibre'
journal: Nat. Commun.
volume: 5
pages: 4096
year: 2014
doi: 10.1038/ncomms5096
arxiv: '1408.0659'
pdf: PDF_papers/Okaba_2014_Lamb-Dicke-spectroscopy-Sr-hollow-core-photonic-crystal-fibre.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/okaba2014.md  # line-by-line against the held PDF, 2026-09-22: "clock transition" corrected to the paper's own probe/clock distinction (3P1 is the probe, 3P0 is the paper's own "clock transition"), and an absolute claim about the guided-mode intensity gradient softened to what the trapping scheme actually shows
author: agent
routing: []
verify_flags:
  - 'Pages 1-2 of the held arXiv:1408.0659 preprint (title, full author list,
    all eleven affiliations including the XLIM GPPMM group that fabricated
    the fibre, and the complete abstract) read against the record on
    2026-09-21. The body, including the lattice-confinement and Lamb-Dicke
    line-narrowing analysis, is unread.'
  - 'Pages 4-6 (the start of the Results section and the Experimental Setup
    subsection, introducing the 1D magic-wavelength lattice and the
    88Sr(1S0-3P1) transition) read on 2026-09-22, during the line-by-line
    audit, solely to check the "clock transition" label and the "never
    samples the guided-mode intensity gradient" claim used below. Page 10
    (the Fig. 4a caption, "the lattice-intensity-dependent light shift") was
    also checked, for the second claim. The rest of the Results, the
    Discussion, and the Methods (including the fibre transmission/coupling
    budget and the Lamb-Dicke narrowing derivation) remain unread and
    undrawn upon.'
verified_date: 2026-09-21
summary: >
  Ultracold ⁸⁸Sr atoms transversely confined by a magic-wavelength optical
  lattice inside a kagome-lattice hollow-core photonic crystal fibre (XLIM
  fabrication), singly occupying lattice sites to suppress atom-atom
  interaction and Doppler broadening: a 7.8 kHz linewidth on the 1S0-3P1
  (m=0) transition, which this paper uses as a probe, not as its clock
  transition (its own text reserves that term for the separate, mHz-narrow
  1S0-3P0 line; corrected 2026-09-22). Named directly by the search priority
  as the HCPCF precedent beyond the Taiwan HCPCF group.
loci: []
section: prior-art
---

# okaba2014

VERIFIED for pages 1-2 (title, authors, affiliations, abstract). REPORTED
beyond that: the body sections on the lattice trapping scheme, the fibre
transmission/coupling budget, and the Lamb-Dicke narrowing mechanism are
unread.

## What pages 1-2 give, verbatim

"Unlike photons, which are conveniently handled by mirrors and optical fibres
without loss of coherence, atoms lose their coherence via atom-atom and
atom-wall interactions. This decoherence of atoms deteriorates the
performance of atomic clocks and magnetometers, and also hinders their
miniaturisation. Here we report a novel platform for precision spectroscopy.
Ultracold strontium atoms inside a kagome-lattice hollow-core photonic
crystal fibre are transversely confined by an optical lattice to prevent
atoms from interacting with the fibre wall. By confining at most one atom in
each lattice site, to avoid atom-atom interactions and Doppler effect, a
7.8-kHz-wide spectrum is observed for the" ¹S₀ − ³P₁ (m = 0) "transition. Atoms
singly trapped in a magic lattice in hollow-core photonic crystal fibres
improve the optical depth while preserving atomic coherence time."

The affiliation list on page 1 names the fibre's makers explicitly: "GPPMM
group, Xlim Research Institute, CNRS UMR7252, 123 av Albert Thomas, Limoges,
France" (Benabid and Bradley), the same XLIM group that later supplies the
Lan-group HCPCF work (wang2022, digested in `private/reviews/LAN_GROUP_DIGEST.md`).

## Use in this record

This is the search priority's named example (item 4) of atoms in HCPCF beyond
the Taiwan HCPCF group: a different species (Sr, not Rb), a different confining
strategy (a magic-wavelength optical lattice inside the fibre core, single
occupancy per site, holding each atom near the same near-centre lattice
position instead of letting it sample the fibre mode's transverse intensity
gradient the way a more loosely distributed guided ensemble would), and a
different goal (clock spectroscopy, not interferometry or light storage).
Read on 2026-09-22 against the paper's own Results section, the cancellation
is not absolute: Fig. 4a's own "lattice-intensity-dependent light shift" is a
residual, measurable dependence on the lattice beam's overall power that the
paper extrapolates to zero, so an earlier draft's "never... at all" overstated
what the scheme achieves. It is nonetheless the strongest available
counter-example to Lan's guided-mode intensity distribution: instead of
characterising or tolerating the inhomogeneous light shift the guiding mode
imposes, Okaba's scheme engineers most of it away by trapping every atom near
the same lattice-site position.
Read beside wang2020/xin2018/xin2019 (the Taiwan HCPCF group, already held
and digested) it sharpens the framing this record can offer that group: a
distribution method for the shift the guiding beam imposes, as an
alternative to Okaba's route of suppressing the distribution altogether.
