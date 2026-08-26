---
citekey: biraben1979
type: article
authors:
  - Biraben, F.
  - Bassini, M.
  - Cagnac, B.
title: 'Line-shapes in Doppler-free two-photon spectroscopy: the effect of finite transit time'
journal: J. Phys. (Paris)
volume: 40
number: 5
pages: 445--455
year: 1979
doi: 10.1051/jphys:01979004005044500
arxiv: null
pdf: PDF_papers/Biraben_1979_finite-transit-time-two-photon-lineshape.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: '2026-08-03'
summary: >
  Origin of our transit kernel: Eq. (46) derives the finite-transit
  Doppler-free two-photon line as exactly a Lorentzian (width Gamma_e/2)
  convolved with a two-sided exponential (width delta*ln2, the central
  cusp), delta = <v_r>/w0. Confirmed by full read: our kernel restates
  Eq. (46) verbatim, and does not over-attribute the M9 Monte Carlo
  extension to this paper.
loci:
  - M3
  - M9
  - methods/02
section: transit-time
---

# biraben1979

Held. Verified in full against the open-access HAL deposit jpa-00209125 (J. Physique 40 (5), 445-455, 1979), received 8 December 1978 and accepted 24 January 1979.

**Abstract.** "A general formalism is developed with the aim of calculating the line-shapes in two-photon absorption for the case of non monochromatic fields." The formalism is applied to the finite transit time of atoms through the laser beam, giving a precise expression for the line-shape, the convolution of a Lorentzian curve and a double-exponential curve, compared against experimental profiles.

## The system and method

Section 1 recaps the monochromatic two-photon absorption rate published in Cagnac, Grynberg and Biraben (1973), including the Doppler-cancellation result. Section 2 develops a general formalism for non-monochromatic fields: for a field E(t) with Fourier support confined to a finite interval [T1, T2], the absorbed energy is expressed through A(Omega), the Fourier transform of E(t)^2 (Eq. 36), the two-photon analogue of the one-photon correlation-function result. The formalism also covers a mode-locked-laser interference example (Eqs. 39-40) and, in an appendix, collisional effects.

Section 3 specializes the formalism to an atom crossing a focused Gaussian TEM00 beam waist, observed over a length L small compared with the Rayleigh length z_R (citing Kogelnik and Li 1966, and Siegman 1971), with radial velocity v_r and impact parameter p. For a single trajectory the result is a Voigt profile, the convolution of a Lorentzian and a Gaussian. Averaging that Voigt over the Maxwell-Boltzmann radial-velocity distribution f(v_r) and over p gives Eq. (46), the paper's central result: the absorption profile as a function of omega_L is the convolution of a Lorentzian curve of width Gamma_e/2 with a double-exponential curve of width delta*ln2 at half maximum, with delta = <v_r>/w0, the reciprocal mean transit time. The text notes agreement with Bordé's calculation for a three-level system and attributes the cusp to slow atoms, which "stay a long time in the beam and contribute much to the absorption but very little to the broadening." The derivation is noted as not strictly valid for atoms of very low radial velocity, citing Biraben's 1977 thesis for the claim that the correction is negligible. In the long-transit limit (delta much less than Gamma_e) the double exponential collapses to a delta function and Eq. (46) reduces to the pure Lorentzian of Eq. (48).

## The experimental test

Section 4 tests Eq. (46) against the 3S-4D5/2 line in sodium at 5787.3 Angstrom, recorded with two focusing lenses: f = 25 cm (w0 ~ 25 micron, non-Lorentzian, sharp-cusped, fast-decaying wings) and f = 50 cm (w0 ~ 50 micron, closer to Lorentzian). Using the known ratio delta_4 = 2*delta_5 between the two configurations, the width difference between the traces is solved for delta_5, in agreement with the transit-time estimate from w0 and the RMS radial velocity. The width budget for the narrower trace is a natural linewidth Gamma_e/4pi = 1.6 MHz (Lorentzian FWHM), plus about 1 MHz from residual laser frequency jitter and collisional broadening from impurities in the cell. The appendix shows the two-photon lineshape is insensitive to velocity-changing collisions, because A(Omega) depends on E(t)^2 at one instant rather than a two-time correlation. Collisions enter only as an ordinary phase-interruption Lorentzian term, a mechanism distinct from transit broadening.

## Validity

Eq. (46) is exact only for the paper's own geometry: a single w0 evaluated at the waist, L << z_R, no explicit intensity-squared (saturation) weighting, and no explicit collection-solid-angle weighting. The low-v_r divergence is dismissed by citation to an unpublished thesis and not derived here. The derivation is restricted to atoms observed near the waist, over a length small compared to the Rayleigh range, and does not treat trajectories away from it: no wavefront-curvature or curvature-compensation mechanism appears anywhere in the text, and none is needed for Eq. (46).

The Voigt profile in Section 3 is the per-velocity-class result. The double-exponential of Eq. (46) appears only after the average over the Maxwell-Boltzmann radial-velocity distribution.

## Use in this record

The transit-time kernel in `methods/02_the_lineshape.md` (derivation in `docs/wiki/transit-time-broadening.md`), K_transit(nu) ~ exp(-|nu|/b) with FWHM = 2b*ln2, restates Eq. (46)'s double-exponential factor, with the natural Lorentzian (Gamma_e/2) factored out and handled separately in the convolution chain, matching how the paper separates the two terms.
