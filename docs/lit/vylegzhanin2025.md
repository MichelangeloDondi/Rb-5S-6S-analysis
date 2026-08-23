---
citekey: vylegzhanin2025
type: article
authors:
  - Vylegzhanin, Alexey
  - Brown, Dylan J.
  - Kornovan, Danil F.
  - Brion, Etienne
  - Nic Chormaic, Sile
title: 'Towards a fictitious magnetic field trap for both ground and Rydberg state 87Rb atoms via the evanescent field of an optical nanofiber'
journal: New Journal of Physics
volume: 27
number: 7
pages: 073203
year: 2025
doi: 10.1088/1367-2630/adf058
arxiv: null
pdf: PDF_papers/Vylegzhanin_2025_fictitious-magnetic-trap-ground-and-Rydberg-nanofiber.pdf
held: true
status: VERIFIED
verified_date: 2026-08-22
section: oist-lineage
summary: >
  Read in full 2026-08-22 from the open-access PDF. A PROPOSAL, not a
  measurement. A trap for 87Rb near a 175 nm radius nanofibre built from the
  vector light shift at the 790.2 nm tune-out wavelength, which acts as a
  light-induced fictitious magnetic field, plus a bias field. Trap depths of
  0.1 to 0.85 mK with minima about 320 nm from the surface, set that far out
  because the Casimir-Polder shift for Rydberg states is of order GHz inside
  300 nm. A common trap for ground 5S1/2 F=1 and Rydberg 68G9/2 is reached by
  detuning to 788.1 nm, giving minima within 10 nm and depths differing by
  about 40 per cent.
routing:
  - CITE
---

# vylegzhanin2025

Read in full 2026-08-22 from the open-access PDF. New J. Phys. 27 (2025)
073203, CC-BY. Same first author and group as
[vylegzhanin2023](vylegzhanin2023.md), and the direction that paper's
conclusions named when they proposed trapping Rydberg atoms "potentially
through the use of magic wavelengths".

**This is a PROPOSAL and says so.** The title begins "Towards", and the text
states the concept may be experimentally challenging. Nothing in it is a
measurement, and this record classes it PROSPECTIVE for that reason.

## The mechanism

At the **tune-out wavelength of the 5S1/2 ground state, 790.2 nm**, the scalar
light shifts from the D1 and D2 lines cancel, so the scalar shift vanishes and
only the vector and tensor parts remain. The vector part depends on the
magnetic quantum number and can be written as a **light-induced fictitious
magnetic field**, which is vector-added to a real bias field. Where the total
effective field passes through zero, low-field-seeking atoms are trapped.

The ellipticity that makes this work is not incidental. It is present for both
quasi-linear and quasi-circular fundamental guided modes of a nanofibre,
because a guided mode carries a longitudinal field component.

## The numbers, as stated

* Fibre: silica, refractive index **1.44, radius a = 175 nm**, supporting only
  HE11 at every wavelength used. That is the same 350 nm diameter as the
  experiment in [vylegzhanin2023](vylegzhanin2023.md).
* Rydberg state for the single-state trap: **49D5/2**. At 790.2 nm its vector
  polarisability is -9.7e-5 Hz m^2 V^-2, its scalar -7.2e-6, and its
  ponderomotive -15e-6. The last two are only an order of magnitude below the
  first, so neither the scalar nor the ponderomotive shift may be dropped.
* Quasi-circular mode at 20 mW and 60 G gives a trap **207 uK deep with its
  minimum 319 nm from the surface**. Quasi-linear at 10 mW and 6 G gives
  **0.77 mK at about 316 nm**. Their table 1 spans 103 to 846 uK with radial
  and azimuthal frequencies of tens to hundreds of kHz and Lamb-Dicke
  parameters of 0.11 to 0.25.
* **Why the trap sits that far out.** The nanofibre imposes an attractive
  Casimir-Polder shift on Rydberg states **of order GHz up to 300 nm from the
  fibre**, so the trap minimum has to be held beyond it.
* Joint ground and Rydberg trapping uses **5S1/2 F=1 with 68G9/2**. The nS and
  nP Rydberg states can NEVER reach a vector polarisability comparable to the
  ground state at this wavelength, so no fictitious field similar to the ground
  state's can be made for them. n is capped at 80 so the Rydberg electron
  wavefunction, mean radius about 450 nm at n = 80, does not overlap the fibre.
* Matching the two potentials is done by **detuning away from tune-out**. At
  **788.1 nm** the two trap minima lie **less than 10 nm apart** with trap
  depths differing by about **0.18 mK**, a ratio of roughly 40 per cent.
* Lifetimes: ground-state trap about 20 s against recoil heating, but Raman
  scattering at about 50 per second sets a worst-case **20 ms**. The Rydberg
  trap lifetime is blackbody-limited at about **100 us**.

## Why it sits next to our own record

The whole construction is polarisability bookkeeping. Scalar, vector and tensor
components separated, a tune-out wavelength located, and then a deliberate
detuning from it to trade one shift against another so that **two states see
the same potential**. That is differential-light-shift engineering, and this
record's own machinery is its measurement counterpart: reading the
DISTRIBUTION of light shifts an inhomogeneous field imposes out of a line shape
([the ramp construction](../methods/03_the_ac_stark_ramp.md)), and the magic
and tune-out crossings computed in
[the polarizability module](../methods.md).

One asymmetry is worth recording. This proposal removes a differential shift by
design. Our record measures the spread that a real field leaves behind. A
proposal of this kind eventually needs the second thing, because a trap
engineered to cancel a shift on paper still has to be shown to have cancelled
it on the bench.
