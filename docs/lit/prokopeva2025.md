---
citekey: prokopeva2025
type: article
authors:
  - Prokopeva, Ludmila J.
  - Kildishev, Alexander V.
title: 'Inhomogeneous broadening in the time domain: Gauss-Lorentz, Gauss-Drude and Gauss-Debye material models'
journal: Nanophotonics
volume: 14
number: 23
pages: 4177-4196
year: 2025
doi: 10.1515/nanoph-2025-0044
arxiv: null
pdf: PDF_papers/Prokopeva_2025_inhomogeneous-broadening-time-domain-Gauss-Lorentz-Voigt.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Read in full from the held PDF (20 pages, main text plus three appendices and
    the reference list). Journal, volume, issue and page range are taken from the
    De Gruyter running header (Nanophotonics 2025, 14(23), 4177-4196) and the DOI
    from the article header. Received 2025-01-30, accepted 2025-04-08, published
    online 2025-08-05. No external bibliographic record was cross-checked.'
verified_date: 2026-08-03
summary: >
  A causal, physically consistent time-domain framework for inhomogeneous
  broadening: the dielectric response is an unbroadened line convolved with a
  complex probability density G(x) = G(x) + iH{G(x)}, so a measured lineshape
  can be decomposed into the intrinsic homogeneous width and the disorder
  distribution together. Worked models are Gauss-Lorentz (Voigt), Gauss-Debye
  and Gauss-Drude, made time-domain-solver-ready by a minimax rational
  approximation (MiMOSA). Corrects the noncausal Brendel-Bormann model.
loci:
  - THEORY
  - P1
section: prior-art
---

# prokopeva2025

Held. Read in full against the published PDF.

## The problem

A causal, physically consistent time-domain framework for inhomogeneous broadening. A measured dielectric response is treated as an unbroadened resonance line convolved with a complex probability density $\mathcal{G}(x) = G(x) + i\mathcal{H}\lbrace G(x)\rbrace $, so that a measured lineshape can be decomposed into an intrinsic homogeneous linewidth and a disorder distribution together. Homogeneous broadening (HB), the same for every emitter and produced by the natural linewidth plus collisions or phonons, gives the classical Lorentzian line. Inhomogeneous broadening (IB), different subgroups of emitters at different resonant frequencies, for instance from size dispersion in quantum dots, structural disorder in amorphous solids, or the Doppler shift in a gas, does not, and real measured lines mix both. The paper targets retrieving the two contributions separately from a measured lineshape, with a model that stays causal and Kramers-Kronig consistent and is cheap enough to run inside a time-stepping electromagnetic solver such as FDTD.

## The framework

The unbroadened susceptibility of an idealized, infinitely sharp oscillator is $\chi^0(t)$ in time, $\hat\chi^0(\omega)$ in frequency. Broadening is introduced by convolving the frequency-domain response with a probability density function $G_i(x) $, required to be a genuine PDF (nonnegative, unit integral), Eq. (2):

$$\hat\chi_i(\omega) = (\hat\chi_i^0 * G_i)(\omega).$$

By the convolution theorem this is a product in the time domain, Eq. (3), with $\varphi_i(t)$ the characteristic function (Fourier transform) of $G_i(x) $:

$$\chi_i(t) = \chi_i^0(t)\varphi_i(t).$$

Substituting the general unbroadened form $\chi_i^0(t) = a\sin(\Omega_i t - \phi_i)\theta(t)$ gives, for any valid broadening PDF $G_i(x) $, the fundamental dispersion relation, Eq. (5):

$$\chi_i(t) = a\varphi_i(t)\sin(\Omega_i t - \phi_i)\theta(t), \qquad
\hat\chi_i(\omega) = \frac{i\pi a}{2}\big[e^{i\phi_i}\mathcal G_i(\omega-\Omega_i) - e^{-i\phi_i}\mathcal G_i(\omega+\Omega_i)\big],$$

where $\mathcal G_i(x) = G_i(x) + i\mathcal H\lbrace G_i(x)\rbrace$ is the complex PDF, the broadening distribution plus its own Hilbert transform carried as the imaginary part. Its real part reproduces the absorption lineshape directly, with $\hat\chi_i''(\omega)$ mapping onto $G_i(\omega\mp\Omega_i) $. Kramers-Kronig consistency follows automatically because the imaginary part is by construction the Hilbert transform of the real part, and causality of $\chi_i(t)$ follows whenever $\chi_i^0(t)$ is causal (Section 2.2). The amplitude, phase and resonance parameters $[a,\phi_i,\Omega_i]$ toggle between an oscillator ($\phi=0$), a relaxation ($\phi=-\pi/2$, $\Omega=0$) and a conductivity (same phase, $\chi\to\sigma$), so one formula covers Lorentz, Debye and Drude dispersion and their disorder-broadened generalizations.

## Worked models and results

Section 3.3 (Table A, "VOIGT" row) specializes $G_i(x)$ to a Gaussian of variance $\sigma^2$ convolved with the classical Lorentzian/Cauchy PDF of HWHM $\gamma$, giving the Gauss-Lorentz (Voigt) susceptibility, Eq. (19), in closed form through the Faddeeva function $w(z) $. Because $\gamma$, the homogeneous Lorentzian component, and $\sigma$, the inhomogeneous Gaussian component, enter as two distinct, physically defined parameters rather than one lumped empirical width, fitting a measured absorption profile to Eq. (19), or its Gauss-Debye/Gauss-Drude analogues (Eqs. 20-21), separates the two. $\gamma$ recovers the intrinsic homogeneous linewidth, $\sigma$ characterizes the disorder distribution. The paper contrasts this with the empirical frequency-domain fits used in current ellipsometry software (pseudo-Voigt, Kim's $\alpha$-switch model), which are not Kramers-Kronig-derived from a genuine convolution and so do not cleanly separate the two contributions.

The complex PDF's minimax rational (pole-residue) approximation, fit under a sum-rule constraint via the equioscillation theorem (MiMOSA), turns the exact but special-function-laden model (Faddeeva/Dawson functions) into the shortest possible pole-residue stencil for a target error. This plugs directly into an FDTD time-stepping update and, run in reverse, fits a measured or ellipsometry-derived spectrum for lineshape retrieval (Section 3.4). Two to three poles give better than 1 percent accuracy.

## Correction to prior work

The paper dates the underlying convolution model to two prior attempts and corrects the second.

- A. Efimov and V. Khitrov, "Analytical formulas for describing the dispersion of glass with refractive indices that observe the continuous nature of absorption," *Fiz. Khim. Stekla*, vol. 5, no. 5, pp. 583-588, 1979.
- R. Brendel and D. Bormann, "An infrared dielectric function model for amorphous solids," *J. Appl. Phys.*, vol. 71, no. 1, pp. 1-6, 1992.

Efimov and Khitrov, and later Brendel and Bormann, introduced the convolution integral that produces Gaussian (inhomogeneous) broadening of a classical Lorentz oscillator, Eq. (B.2), and solved it in terms of Faddeeva functions, Eq. (B.3). The paper shows the Brendel-Bormann closed form (Appendix B) confuses the resonance frequency $\Omega$ with the natural frequency $\omega_0$, uses a sum instead of the difference of two Faddeeva-function terms that the correct Gauss-Lorentz derivation (their own Eq. B.9) requires, and is noncausal ($\chi_{BB}(t) \neq 0$ for negative $t$), so despite wide use in fitting infrared spectra it cannot be coupled to a time-domain Maxwell solver. The paper's Gauss-Lorentz model, Eqs. (B.8)-(B.9), is the causal replacement.

## Relation to this project

[delone1980](delone1980.md) already integrates a Lorentzian resonance against a probability distribution $P(F)$ of the perturbing variable, in the shift-dominated limit, and notes that $P(F)$ can in principle be reconstructed from the observed line. Prokopeva and Kildishev's Eqs. (2)-(5) give the same convolution/characteristic-function structure in full generality, made causal and Kramers-Kronig consistent through the complex object $\mathcal{G}(x)$ and made numerically tractable for time-domain solvers through MiMOSA.

This project's own construction, an intensity distribution $P(I) \propto 1/I$ for a focused Gaussian beam substituted into Delone's Eq. (5.3) to give $f(s) \propto \vert s\vert ^{n-1}$ with analytic cumulants, occupies the same taxonomic slot as the paper's worked models (Gauss-Lorentz, Gauss-Debye, Gauss-Drude). It is a known, first-principles-derived parametric $G$ pushed forward through the general convolution relation, rather than the fully general, data-driven inversion that the paper poses as open (Table A, row 1, "ANY Broadening").
