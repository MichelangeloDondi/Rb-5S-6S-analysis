---
citekey: panelli2026
type: article
authors:
  - Panelli, Guglielmo
  - Porter, Erik J.
  - Knight, V. Rose
  - Burd, Shaun C.
  - Kasevich, Mark
title: 'Microsecond-Scale Coherent Control of a Forbidden Clock Transition with Doppler-Free Multiphoton Excitations'
journal: null
volume: null
pages: null
year: 2026
doi: null
arxiv: '2607.06789'
pdf: PDF_papers/Panelli_2026_doppler-free-multiphoton-clock-excitation-Sr.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - 'Held as the arXiv preprint (2607.06789v1, dated 7 Jul 2026. The paper states
    the first two authors contributed equally). Pages 1-2 of 19 read against the
    PDF on 2026-09-20 (abstract, introduction and the start of the experimental
    overview). No journal record is visible in the pages read. The appendices,
    the systematic-effects analysis, and the two excitation-scheme sections
    (II-IV) are not yet read.'
verified_date: null
summary: >
  Demonstrates two Doppler-free multiphoton excitation schemes for the
  strontium 1S0-3P0 clock transition in free space (no lattice or tweezer
  confinement), using wavevector geometries chosen so the net first-order
  Doppler shift cancels. A three-photon simultaneous scheme reaches 190 kHz
  Rabi frequency at 76% pi-pulse efficiency. A sequential single-photon-plus-
  two-photon-Raman scheme reaches an 820 kHz effective Rabi frequency at over
  90% efficiency. Both suppress Doppler dephasing about 1000-fold and extend
  the free-space Ramsey coherence time from 4.5 microseconds to beyond 4
  milliseconds. A different atom, a different transition class (a
  single-photon-forbidden clock line, not a two-photon absorption line) and a
  different physical goal (coherent state control, not thermal-ensemble
  lineshape spectroscopy). Relevant here only as a general precedent for
  engineering multiphoton wavevector geometries that cancel the first-order
  Doppler shift.
loci: []
section: landscape-24-26
---

# panelli2026

## Values

| field | value | where in the paper |
|---|---|---|
| arXiv identifier | 2607.06789v1 [physics.atom-ph], 7 Jul 2026 | p. 1 |
| affiliations | Stanford University (Physics, Electrical Engineering, Applied Physics) and SLAC National Accelerator Laboratory | p. 1 |
| clock transition | 88Sr 1S0 - 3P0 | p. 1 |
| atom number / temperature | up to 3x10^6 atoms, 7-9 uK | p. 1, p. 2 |
| Doppler-free wavevector condition | $\vec k_1 + \vec k_2 - \vec k_3 = 0$ | p. 2 |
| Method 1 (simultaneous three-photon): Rabi frequency, pi-pulse efficiency | 190 kHz, 76% | p. 1 |
| Method 2 (sequential single-photon + two-photon Raman): effective Rabi frequency, pi-pulse efficiency | 820 kHz, over 90% | p. 1 |
| Doppler-dephasing suppression vs. single-photon excitation | about 1000-fold (three orders of magnitude) | p. 1 |
| Ramsey coherence time, free-space thermal sample | extended from 4.5 us to beyond 4 ms | p. 1 |
| Method 1 detuning / bias field (worked example) | $\Delta_1 = 2\pi\times5$ MHz, 19 G bias field, Zeeman splitting $\delta_B = 2\pi\times40$ MHz | p. 2 |

## What it says, in its own terms

The paper addresses a standard tension in optical-clock physics: the 1S0-3P0 clock transition in alkaline-earth(-like) atoms is so narrow that exploiting its coherence normally requires confining the atoms -- in an optical lattice, tweezers, or an ion trap -- well inside the Lamb-Dicke regime, because an unconfined thermal sample would otherwise dephase quickly from the first-order Doppler shift as atoms move during a single-photon excitation. The approach here is to replace single-photon excitation with a multiphoton excitation whose three wavevectors are arranged to cancel to zero, $\vec k_1+\vec k_2-\vec k_3=0$, so that the first-order Doppler shift $(\vec k_1+\vec k_2-\vec k_3)\cdot\vec v$ vanishes for every atom regardless of its velocity, removing the need for tight confinement altogether.

Two concrete schemes are demonstrated on thermal (7-9 uK, unconfined, free-space) samples of up to 3x10^6 88Sr atoms. The first drives all three photons simultaneously, coupling the ground and clock states through two intermediate levels with three phase-locked lasers referenced to a frequency comb, and reaches a 190 kHz three-photon Rabi frequency with 76% pi-pulse efficiency. The second is sequential -- a single-photon step to an intermediate state followed by a two-photon Raman step into the clock state -- and reaches a higher effective Rabi frequency (820 kHz) and pulse efficiency (over 90%) while keeping the same Doppler- and recoil-free character.

Both schemes are characterized with high-contrast Ramsey spectroscopy, and the reported headline results are a roughly thousand-fold suppression of Doppler dephasing relative to single-photon excitation and an extension of the free-space Ramsey coherence time from 4.5 microseconds to beyond 4 milliseconds. The authors frame both techniques as broadly generalizable to other atomic species and narrow-line transitions, with applications to optical clocks, matter-wave interferometry and quantum information processing, and note that although the demonstration uses the bosonic isotope 88Sr, the same schemes could apply to fermionic isotopes.

## What it is worth here

This sits well outside the vapour-cell programme's own atom, transition and measurement goal. It is strontium, not rubidium, a single-photon-forbidden narrow clock line, not a two-photon absorption line, and its object is coherent quantum-state control of a cold, confinement-free sample rather than the lineshape spectroscopy of a thermal vapour this record performs. The one transferable idea is generic rather than specific -- engineering a multiphoton wavevector geometry so the first-order Doppler shift cancels by construction is the same design principle behind any Doppler-free two-photon geometry, including the counter-propagating configuration this record's own transition already uses -- but the paper supplies no number, technique or apparatus detail that this record could cite for its own measurement.
