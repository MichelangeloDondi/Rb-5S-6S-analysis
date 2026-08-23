---
citekey: vylegzhanin2023
type: article
authors:
  - Vylegzhanin, Alexey
  - Brown, Dylan J.
  - Raj, Aswathy
  - Kornovan, Danil F.
  - Everett, Jesse L.
  - Brion, Etienne
  - Robert, Jacques
  - Nic Chormaic, Sile
title: 'Excitation of 87Rb Rydberg atoms to nS and nD states (n<=68) via an optical nanofiber'
journal: Optica Quantum
volume: 1
number: 1
pages: 6-13
year: 2023
doi: null
arxiv: 2305.05186
pdf: PDF_papers/Vylegzhanin_2023_Rb-Rydberg-nS-nD-via-optical-nanofiber.pdf
held: true
status: VERIFIED
verified_date: 2026-08-22
section: oist-lineage
summary: >
  Read in full 2026-08-22 (arXiv v3, eight pages). Cold 87Rb in a MOT around a
  350 nm optical nanofibre, two-photon excitation 780 + 480 nm with the 480 nm
  guided in the fibre, to nS(26-55), nD3/2(24-65), nD5/2(24-68). Detection is
  indirect, by MOT loss. Spectra are fitted with a SKEWED Gaussian to absorb
  the asymmetry from the 1064 nm AC Stark shift and the atom-surface
  interaction. A Maxwell-Bloch model including Casimir-Polder reproduces the
  dip. DC Stark shifts are EXCLUDED from it because the group has no mechanism
  to quantify them.
routing:
  - CITE
---

# vylegzhanin2023

Read in full 2026-08-22 from the arXiv PDF (v3, 30 Aug 2023). Same group and
same platform as [gokhroo2022](gokhroo2022.md), which drives our own
5S -> 6S transition at 993 nm beside a nanofibre.

## Apparatus, as stated

* ONF diameter **d ~ 350 nm**, tapered from SM800-5.6-125 by H:O flame
  brushing, transmission kept above 99 per cent for 780 nm during the taper.
  The diameter sits very close to the **352 nm cutoff** for the TE01 and TM01
  modes. HE11 is assumed for all three wavelengths.
* UHV at **1e-9 mbar**. **300 uW of 1064 nm is propagated through the fibre to
  keep it hot and reduce 87Rb adsorption on its surface.**
* MOT at **~140 uK**, six 780 nm beams, cooling detuning **-14 MHz** from
  5S1/2(F=2) -> 5P3/2(F=3), 50 mW total, 20 G/cm.
* Rydberg drive: **480 nm** from a Toptica SHG Pro, EIT-locked in an enriched
  87Rb cell, its wavelength steered by an EOM on the 780 nm probe. **30 uW out
  of the ONF** against 300 uW in, so 10 per cent transmission. Quasi-circular
  polarisation is optimal.
* Detection is INDIRECT: Rydberg excitation is inferred from MOT loss measured
  on a PMT. Seven seconds of loading, then 480 nm on for about four seconds to
  a new equilibrium.

## What was measured

* States **nS1/2 for n in [26,55]**, **nD3/2 in [24,65]**, **nD5/2 in
  [24,68]**. Detuning scanned -22 to +22 MHz in 1 MHz steps, ten repeats.
* Each spectrum is fitted with a **SKEWED Gaussian** (their Eq. 1, a two-dip
  form with skew parameters A_i) "to account for the asymmetry arising from
  the red-shift induced by the AC Stark shift of the 1064 nm laser and the
  atom-fiber surface interaction". The mode of the distribution is taken as
  the resonance position.
* The nD resonance position is nearly flat in n, with **variances of 0.5 MHz
  (nD5/2) and 0.61 MHz (nD3/2)**, while **nS1/2 red-shifts clearly and ceases
  to be excited at n >= 56**.
* nD5/2 excitation falls until **n >= 68**, where it stops. They attribute this
  to ionisation of high-n Rydberg atoms, with the ions sticking to the fibre
  and shielding the excitation, and they TESTED it: moving the MOT about
  0.5 mm along the waist restored normal behaviour, so that region of fibre was
  ion-coated but undamaged.

## The model, and the gap it leaves open

Steady-state Maxwell-Bloch (their Eq. 2) averaged over 10,000 atoms sampled
from the density near the fibre, with van der Waals for 5S1/2 and 5P3/2 and a
quasi-static Casimir-Polder potential for the Rydberg states built from
dipole and quadrupole terms and the nanofibre Green's tensor (Eq. 3), plus a
resonant expression for the lifetime and hence linewidth change (Eq. 4).

Casimir-Polder is load-bearing: without it the model over-broadens badly, and
with it **the excitation is restricted to a shell roughly 250 to 300 nm from
the surface**, where the Rabi frequency is of order a few MHz. Closer atoms are
shifted out of resonance.

**The stated gap, which is the reason this note matters to us.** In their own
words: *"In the model, DC Stark shifts are not included as we have no
experimental mechanism for quantifying them."* And earlier: the impact of DC
Stark shifts from stray fields or charging of the ONF is *"difficult to
quantify with no electrodes in the vacuum chamber"*. They assume those shifts
stay roughly constant, except where ion deposition causes what they call
enormous shifts. Two decoherence terms in the model are left as **free
parameters** because they are hard to determine experimentally.

**Their own stated next steps** include an optical dipole trap to hold atoms at
a fixed distance from the surface, and adapting a two-colour dipole trap to
trap Rydberg atoms *"potentially through the use of magic wavelengths"*.
That is the direction [vylegzhanin2025](vylegzhanin2025.md) takes up.

## Why this sits next to our own record

They read a near-surface shift out of a line shape by fitting an EMPIRICAL skew
and absorbing two effects into it. This record reads a light-shift distribution
out of a line shape with a DERIVED profile
([the ramp construction](../methods/03_the_ac_stark_ramp.md)) and carries the
bound conditioned on the prior it depends on. Same observable, different
inference, and their unquantified DC Stark term is a field that no electrode is
available to measure. See also [patrick2025](patrick2025.md), where surface
charge on a dielectric measurably shifts Rydberg sensors in vapour cells.
