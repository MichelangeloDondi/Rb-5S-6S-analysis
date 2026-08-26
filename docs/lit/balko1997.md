---
citekey: balko1997
type: article
authors:
  - Balko, B.
  - Kay, I. W.
  - Vuduc, R.
  - Neuberger, J. W.
title: 'Recovery of superfluorescence in inhomogeneously broadened systems through rapid relaxation'
journal: Phys. Rev. B
volume: 55
number: 18
pages: 12079-12085
year: 1997
doi: 10.1103/PhysRevB.55.12079
arxiv: null
pdf: PDF_papers/Balko_1997_superfluorescence-inhomogeneous-broadening-rapid-relaxation.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'DOI, volume, issue and page range confirmed against the APS record
    (link.aps.org/doi/10.1103/PhysRevB.55.12079) via a search snippet, not by
    loading the APS page directly (it returned 403). The PDF itself carries
    the same volume/issue/page header on every page, so the record and the
    held file agree independently of the APS fetch.'
verified_date: 2026-08-03
summary: >
  Nuclear superfluorescence (Institute for Defense Analyses / Cornell / North
  Texas), read for its perturbation-parameter-as-random-variable formalism.
  Section III writes a hyperfine perturbation alpha = delta_0 - delta_1 as a
  random variable with a probability density gamma, worked for Gaussian and
  Lorentzian gamma, and integrates gamma against an elementary time-domain
  response G(Omega,alpha,t) to build the inhomogeneously broadened emission.
  Structurally the same lineshape-as-a-probability-map logic as delone1980,
  independently arrived at in a third, unrelated field (nuclear Mossbauer
  physics), fourteen years later. No geometric distribution and no power-law
  family: both worked examples are the two textbook closed forms, not members
  of the |s|^(n-1) family this programme's triangular law belongs to.
loci:
  - THEORY
section: prior-art
---

# balko1997

Held. The DOI, volume, issue, and page range were confirmed against the APS record. Section III was read in full for its formalism.

## The system

Superfluorescence is the cooperative, directional, N-squared-intensity emission pulse from an inverted ensemble of dipoles that correlate their phases before spontaneous decay destroys the correlation. Inhomogeneous broadening, in which each radiator sits at a slightly different transition frequency, dephases that correlation and can suppress superfluorescence outright. The target system is nuclear: a gamma-ray laser candidate in which the radiators are nuclei whose transition energies are shifted by isomer shifts, quadrupole interactions, magnetic hyperfine interactions, dipole-dipole interactions, and gravitational shifts. A relaxation of the perturbing field faster than the superfluorescence delay can collapse the spectrum toward the unbroadened limit and recover superfluorescence that inhomogeneous broadening would otherwise destroy.

## The formalism

Section III.A sets up the perturbed Hamiltonian for a single resonator,

> "H(t) = H0 + delta_i f(t)," (Eq. 8)

with f(t) a random function of time and delta_i the perturbation energy of level i. The emission probability is the real part of a Fourier-Laplace transform of the dipole correlation function (Eq. 9), whose stochastic average is

> "<e^(i*alpha*Integral_0^t f(t')dt')>_av = (cos(x*Omega*t) + (1/x)sin(x*Omega*t))e^(-Omega*t) = G(Omega, alpha, t)," (Eq. 11, with x = [alpha^2/Omega^2 - 1]^(1/2))

where alpha = delta_0 - delta_1 is the perturbation-energy difference between the two levels and Omega is the rate at which the field f(t) jumps between +1 and -1 with equal probability. G(Omega,alpha,t) is the elementary, per-value response. It interpolates between a pure oscillation at frequency alpha (Omega much less than alpha) and a featureless decay (Omega much greater than alpha).

Section III.A then treats alpha as a random variable with a probability density gamma, worked for both Gaussian and Lorentzian forms. The observed, inhomogeneously broadened response is the density integrated against the elementary kernel,

> "Ḡ(Omega,sigma,t) = Integral_{-inf}^{inf} gamma(alpha,sigma) G(Omega,alpha,t) d alpha," (Eq. 13)

with the Gaussian form gamma(alpha,sigma) = (1/(sigma*sqrt(2*pi))) * exp(-alpha^2/(2*sigma^2)), and the Lorentzian form (footnote 13) gamma(alpha,a) = (a*Gamma/2*pi) / [alpha^2 + (a*Gamma/2)^2], with a the inhomogeneous broadening parameter normalized to the natural linewidth Gamma. The Lorentzian choice is described as a mathematical convenience giving an exponential time dependence, and the paper notes that other line shapes may be more appropriate in specific cases. Section III.B repeats the same construction for the superfluorescence intensity (Eqs. 14-16), and Section III.C feeds the resulting time-dependent coupling into the Maxwell-Bloch pulse-shape equations of the group's earlier paper.

## Validity

The Gaussian and Lorentzian forms are presented as the two standard textbook comparisons, not derived from the stated physical sources of broadening (isomer shifts, quadrupole interactions, magnetic hyperfine and dipole-dipole interactions, gravitational shifts). No power-law family and no geometric argument connecting gamma to a spatial distribution appears in the paper.

## Use in this record

The construction, an observed response built from a probability density over a perturbation parameter integrated against an elementary per-value response, matches the skeleton used elsewhere in this analysis for the ac-Stark-shift lineshape, where a density f(s) over the local shift is convolved with a Lorentzian. Two differences stand: alpha here carries an additional field-flip-rate parameter Omega with no counterpart in a static beam-intensity distribution, and neither the Gaussian nor the Lorentzian example anticipates a power-law density of the |s|^(n-1) form used there.
