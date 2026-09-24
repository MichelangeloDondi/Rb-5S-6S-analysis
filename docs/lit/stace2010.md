---
citekey: stace2010
type: article
authors:
  - Stace, T. M.
  - Luiten, A. N.
title: 'Theory of spectroscopy in an optically pumped effusive vapor'
journal: Phys. Rev. A
volume: 81
number: 3
pages: 033848
year: 2010
doi: 10.1103/PhysRevA.81.033848
arxiv: null
pdf: PDF_papers/Stace_2010_theory-spectroscopy-optically-pumped-effusive-vapour.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/stace2010.md  # line-by-line against the held PDF, 2026-09-22: every cited equation (13, 17-18, 23, 31-34, 36), the Fresnel-number and 1/(40 nu^3) figures confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article as deposited in the University of Queensland repository (UQ203330, open access); the owner downloaded it by hand. Read in full on 2026-09-22, Sections I to IX and the Appendix. The text layer splits some equations, so equations are cited by number only. Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The theory behind the Luiten group's line-shape thermometry (truong2015): absorption
  in a thermal, effusive vapour of multilevel atoms at any optical depth. A master
  equation, reduced to rate equations by adiabatic elimination, is solved along each
  atom's straight path from a thermalised wall, per velocity class. It is coupled
  self-consistently to the axial attenuation of the beam. The optically pumped
  populations do not follow the intensity: each velocity class leaves a wake of pumped
  atoms downstream of the beam. Under saturation Beer's law fails, the line is more
  sharply peaked than a Gaussian, and a Gaussian and a top-hat profile of equal power
  absorb differently. In the weak-beam limit the Voigt profile is recovered, with a
  doubly peaked first correction derived in the Appendix.
loci:
  - P1
  - methods/02
  - methods/04
section: transit-time
---

# stace2010

VERIFIED. Held (published version, UQ repository copy). Read in full on 2026-09-22.

## What it does

The introduction names what earlier vapour models left out: a uniform transverse beam profile, the intensity dependence of the absorption, a phenomenological ground-state relaxation rate standing in for transit, and the beam's own evolution along the cell. Section II takes a master equation for driven hyperfine manifolds (Eq. 1) and reduces it to a three-level model with a dark state and branching ratio beta (Eq. 4). Atoms enter the beam in the thermal state, justified by rapid rethermalisation at the cell walls (Eq. 5). The coherences are eliminated adiabatically (Eqs. 6-7), which leaves population rate equations (Eq. 8).

Section III moves to the laboratory frame, where the total time derivative becomes the material derivative (Eq. 9). The steady state is then a first-order partial differential equation for each velocity class (Eq. 10), with the thermal populations as the boundary condition far upstream. The transverse velocity sets the time envelope an atom sees crossing the beam, and the axial velocity its Doppler shift. In the laboratory frame this leaves a wake of pumped atoms that extends beyond the beam in the direction each velocity class moves (Fig. 4). Section IV couples the populations to the beam: diffraction is dropped on a Fresnel-number estimate, under 1 per cent over a 10 cm cell for a 1 mm beam (Eq. 13), and absorption couples the intensity to the velocity-averaged populations (Eqs. 17-18).

## The limits and the numbers

Far from saturation the absorption is a Voigt profile and the beam decays exponentially, so the Voigt form is expected only when the populations are far from saturation (Section VI, Eq. 23). The Appendix derives the first correction: an amplitude rescaling plus a doubly peaked function of the detuning (Fig. 7), with a peak-to-trough height of about 1/(40 nu^3) in the reduced units. Section VII states the approximations of the saturated solution. The absorption length is much longer than the beam width, so about 0.1 per cent of atoms, those moving nearly along the beam, are ignored. The Doppler width is much larger than the natural width, which leaves far tails that are Gaussian, not Lorentzian. The beam is cylindrically symmetric.

Section VIII solves three cases. Two-level atoms under uniform illumination reproduce the known saturated and unsaturated limits (Eqs. 31-34, Figs. 2-3). An optically thin three-level vapour gives an absorption with a Gaussian dependence on the detuning (Eq. 36). An optically thick three-level vapour is solved by iterating the populations and the intensity to self-consistency. The velocity and angle integrals are done by Monte Carlo, converging to 0.1 per cent between iterations. The wings absorb more than the saturated centre, which narrows the beam transversely. Beer's law fails near zero detuning, where the absorption curves at different optical depths do not coincide, and the line becomes more sharply peaked than a Gaussian (Fig. 5). At equal input power a Gaussian profile absorbs more than a top-hat, because part of its power sits in unsaturated wings (Section VIII D, Fig. 6).

## Use in this record

- The published framework for the non-equilibrium process that `docs/methods/02` describes in section 2.5b and its F-statistics section. Atoms leave a thermalising wall with the thermal populations, cross the beam on straight chords and are pumped along the chord by rate equations. Solved per velocity class, as here, the same process carries the record's velocity selection (slow atoms dwell longer and are pumped more) and the reweighting of the surviving atoms toward low intensity. The wake of Fig. 4 shows the consequence in space: the pumped populations lag the intensity.
- The paper's central statement, that the pumped populations do not follow the intensity profile, is why a line built by convolving the intensity with one kernel misses the depletion's shape. It is a published instance of the convolution condition of `docs/methods/04`: the kernel differs between volume elements, here through the pumping history an atom carries in.
- truong2015 is the experimental use of this theory: the Voigt profile fails at I/Isat = 3e-3 through optical pumping. haupl2025 carries transit as one effective decay rate across a flat-top beam and reports that the averaging costs little there. The two papers together bracket when a phenomenological transit term suffices and when the trajectory has to be solved.
- The top-hat versus Gaussian comparison is the published precedent for the record's point that the beam's profile, not only its peak intensity, enters the line. The bore-clipped focus is a third profile of the same kind.

## Limits

- One-photon absorption in an effusive vapour, a three-level model and no collisions. It has no light shift, no two-photon excitation, no fluorescence detection and no treatment of moments or estimator bias. Its numbers are in reduced units for an illustrative parameter set, not a fit to data.
