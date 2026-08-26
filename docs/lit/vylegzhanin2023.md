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

Held. Verified in full against the arXiv PDF (v3).

## The system

* ONF diameter ~350 nm, tapered from SM800-5.6-125 fibre by flame brushing,
  transmission kept above 99% at 780 nm during the taper. This diameter
  sits close to the 352 nm cutoff for the TE01 and TM01 modes. HE11 is
  assumed for all three wavelengths used.
* Vacuum at 1e-9 mbar. 300 uW of 1064 nm light is propagated through the
  fibre to keep it warm and reduce 87Rb adsorption on the surface.
* MOT at ~140 uK, six 780 nm beams, cooling detuning -14 MHz from
  5S1/2(F=2) to 5P3/2(F=3), 50 mW total power, 20 G/cm gradient.
* Rydberg excitation: 480 nm from a Toptica SHG Pro, EIT-locked in an
  enriched 87Rb cell and steered by an EOM on the 780 nm probe. 30 uW exits
  the fibre out of 300 uW launched (10% transmission), with quasi-circular
  polarization giving the best result.
* Detection is indirect, from MOT loss on a PMT, after seven seconds of
  loading and ~4 s of 480 nm exposure to reach a new equilibrium.

## The numbers

States addressed: nS1/2 for n in [26,55], nD3/2 in [24,65], nD5/2 in
[24,68]. Detuning was scanned from -22 to +22 MHz in 1 MHz steps, ten
repeats per point.

Each spectrum is fit with a skewed Gaussian (Eq. 1, a two-dip form with skew
parameters A_i) "to account for the asymmetry arising from the red-shift
induced by the AC Stark shift of the 1064 nm laser and the atom-fiber
surface interaction." The mode of the fitted distribution is taken as the
resonance position.

The nD resonance position is nearly flat in n, with variances of 0.5 MHz
(nD5/2) and 0.61 MHz (nD3/2), while nS1/2 red-shifts with n and ceases to be
excited at n >= 56. nD5/2 excitation falls off and stops at n >= 68. The
authors attribute this to ionization of high-n Rydberg atoms, whose ions
stick to the fibre and shield the excitation. Moving the MOT about 0.5 mm
along the fibre waist restored normal excitation, indicating localized,
non-permanent ion coating rather than fibre damage.

## The model

A steady-state Maxwell-Bloch model (Eq. 2), averaged over 10,000 atoms
sampled from the density near the fibre, combines van der Waals shifts for
5S1/2 and 5P3/2 with a quasi-static Casimir-Polder potential for the Rydberg
states, built from dipole and quadrupole terms and the nanofibre Green's
tensor (Eq. 3), plus a resonant expression for the lifetime and resulting
linewidth change (Eq. 4).

Casimir-Polder is load-bearing: omitting it over-broadens the model
substantially. With it included, excitation is restricted to a shell
roughly 250 to 300 nm from the surface, where the Rabi frequency is of
order a few MHz. Atoms closer to the surface are shifted out of resonance.

DC Stark shifts are excluded from the model: in the authors' words, "In the
model, DC Stark shifts are not included as we have no experimental
mechanism for quantifying them," since stray-field and fibre-charging
effects are "difficult to quantify with no electrodes in the vacuum
chamber." Such shifts are assumed to stay roughly constant except where ion
deposition produces much larger shifts, and two decoherence terms are left
as free parameters for the same reason.

## Use in this record

This analysis extracts a light-shift distribution from a line profile
derived from an underlying model ([the AC Stark ramp
construction](../methods/03_the_ac_stark_ramp.md)), conditioning the
resulting bound on the prior that profile depends on, rather than from an
empirical skewed-Gaussian fit as this paper does. The DC Stark systematic
left unquantified here for lack of in-chamber electrodes is measurable on
other platforms: surface charge on a dielectric measurably shifts Rydberg
sensors in vapor cells ([patrick2025](patrick2025.md)).
