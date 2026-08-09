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

**Read in full 2026-08-03.** Prokopeva and Kildishev, "Inhomogeneous broadening
in the time domain: Gauss-Lorentz, Gauss-Drude and Gauss-Debye material
models," *Nanophotonics* **14**(23), 4177-4196 (2025),
doi:10.1515/nanoph-2025-0044. Purdue (Elmore School of Electrical and Computer
Engineering, Birck Nanotechnology Center, Purdue Quantum Science and
Engineering Institute). Dedicated to Federico Capasso.

## Verbatim abstract

"Forty-five years after the initial attempts, first by Efimov-Khitrov in 1979,
then by Brendel-Bormann in 1992, we present a comprehensive, causal, and
physically consistent framework for modeling the dielectric function with
inhomogeneous (non-Lorentzian) broadening, where scattering becomes frequency-
or time-dependent. This theoretical framework is based on spectral diffusion,
described in the frequency domain by a complex probability density function
and in the time domain by a matching characteristic function. The proposed
approach accurately models the lineshapes resulting from multiple broadening
mechanisms and enables the retrieval of intrinsic homogeneous linewidths as
well as inhomogeneous disorder-controlled material dispersion features. To
implement the new general dispersion function in time-domain Maxwell solvers,
we have designed a constrained minimax-based semi-analytical approximation
method (MiMOSA) that generates the shortest possible numerical stencils for a
given approximation error. Application examples of exact and approximate
MiMOSA models include the Gauss-Lorentz oscillator, Gauss-Debye relaxation,
and Gauss-Drude conductivity. Although this study primarily focuses on the
optical domain, the resulting models, which account for the Doppler shift, are
equally applicable to other wave propagation phenomena in disordered
dispersive media in a broad range of areas, including acoustics, magnonics,
astrophysics, seismology, plasma, and quantum technologies."

## What it does

Nanophotonics/computational-electromagnetics theory paper, not atomic physics.
It sets up a general causal dispersion model for materials whose linewidth is
broadened by *disorder* (structural, compositional, thermal) rather than only
by the finite lifetime of the resonance, then makes that model usable inside
time-domain Maxwell solvers such as FDTD. Homogeneous broadening (HB, same for
every emitter, natural linewidth plus collisions/phonons) gives the classical
Cauchy/Lorentzian line. Inhomogeneous broadening (IB, different subgroups of
emitters at different resonant frequencies, from size dispersion in quantum
dots, structural disorder in amorphous solids, the Doppler shift in a gas) does
not, and real measured lines mix both. The paper's target is retrieving the two
pieces separately from a measured lineshape, doing so with a model that stays
causal and Kramers-Kronig consistent, and doing it in a form cheap enough to
run inside a time-stepping electromagnetic solver.

## THE FRAMEWORK

**The convolution/product pair.** The unbroadened susceptibility of an ideal,
infinitely sharp oscillator (an idealized delta-function-like resonance) is
$\chi^0(t)$ in time, $\hat\chi^0(\omega)$ in frequency. Broadening is
introduced by convolving the frequency-domain response with a probability
density function $G_i(x)$, required to be a genuine PDF (nonnegative, unit
integral), Eq. (2):

$$\hat\chi_i(\omega) = (\hat\chi_i^0 * G_i)(\omega).$$

By the convolution theorem this is a plain product in the time domain, Eq.
(3), with $\varphi_i(t)$ the characteristic function (Fourier transform) of
$G_i(x)$:

$$\chi_i(t) = \chi_i^0(t)\varphi_i(t).$$

**The fundamental dispersion relation, Eq. (5).** Substituting the general
unbroadened form $\chi_i^0(t) = a\sin(\Omega_i t - \phi_i)\theta(t)$ gives, for
*any* valid broadening PDF $G_i(x)$:

$$\chi_i(t) = a\varphi_i(t)\sin(\Omega_i t - \phi_i)\theta(t), \qquad
\hat\chi_i(\omega) = \frac{i\pi a}{2}\big[e^{i\phi_i}\mathcal G_i(\omega-\Omega_i) - e^{-i\phi_i}\mathcal G_i(\omega+\Omega_i)\big],$$

where $\mathcal G_i(x) = G_i(x) + i\mathcal H\lbrace G_i(x)\rbrace$ is the **complex PDF**:
the broadening distribution plus its own Hilbert transform carried as the
imaginary part. This single object is what makes retrieval possible. Its real
part reproduces the absorption lineshape directly, $\hat\chi_i''(\omega)$ maps
onto $G_i(\omega\mp\Omega_i)$, Kramers-Kronig consistency is automatic because
the imaginary part is by construction the Hilbert transform of the real part,
and causality of $\chi_i(t)$ follows as long as $\chi_i^0(t)$ is causal
(Section 2.2). The amplitude, phase and resonance parameters $[a,\phi_i,\Omega_i]$
toggle between an oscillator ($\phi=0$), a relaxation
($\phi=-\pi/2$, $\Omega=0$) and a conductivity (same phase, $\chi\to\sigma$),
so one formula covers Lorentz, Debye and Drude dispersion plus their
disorder-broadened generalizations.

**Retrieving the homogeneous width and the disorder distribution together.**
The worked models (Section 3.3, Table A "VOIGT" row) specialize $G_i(x)$ to a
Gaussian of variance $\sigma^2$ convolved with the classical Lorentzian/Cauchy
PDF of HWHM $\gamma$, giving the Gauss-Lorentz (Voigt) susceptibility, Eq.
(19), in closed form through the Faddeeva function $w(z)$. Because the model is
exact and the two broadening mechanisms enter as two distinct, physically
defined parameters ($\gamma$ for the homogeneous Lorentzian component,
$\sigma$ for the inhomogeneous Gaussian component) rather than as one lumped
empirical width, fitting a measured absorption profile to Eq. (19) (or its
Gauss-Debye/Gauss-Drude analogues, Eqs. 20-21) separates the two: $\gamma$
recovers the intrinsic homogeneous linewidth, $\sigma$ characterizes the
disorder distribution. The paper contrasts this with the empirical
frequency-domain fits current ellipsometry software uses (pseudo-Voigt, Kim's
$\alpha$-switch model), which are not Kramers-Kronig-derived from a genuine
convolution and so do not cleanly separate the two contributions, and with the
classical Brendel-Bormann (BB) model, corrected here (Appendix B) because the
BB integral is not causal ($\chi_{BB}(t) \neq 0$ for negative $t$) and therefore
unusable in a time-domain solver at all.

**MiMOSA is the numerical machine that makes the retrieval practical.** The
complex PDF's minimax rational (pole-residue) approximation, fit under a
sum-rule constraint via the equioscillation theorem, turns the exact but
special-function-laden model (Faddeeva/Dawson functions) into the shortest
possible pole-residue stencil for a target error, which both plugs directly
into an FDTD time-stepping update and, run the other way, is fit to a measured
or ellipsometry-derived spectrum for "ellipsometry fitting and lineshape
retrieval" (Section 3.4). Two to three poles already give better than 1
percent accuracy.

**The Efimov-Khitrov (1979) and Brendel-Bormann (1992) roots.** The paper
opens by dating the problem to these two prior attempts and closes (Appendix
B) by showing exactly what was wrong with the second one. Full references, as
printed in the paper's own list:

- A. Efimov and V. Khitrov, "Analytical formulas for describing the dispersion
  of glass with refractive indices that observe the continuous nature of
  absorption," *Fiz. Khim. Stekla*, vol. 5, no. 5, pp. 583-588, 1979.
- R. Brendel and D. Bormann, "An infrared dielectric function model for
  amorphous solids," *J. Appl. Phys.*, vol. 71, no. 1, pp. 1-6, 1992.

Efimov and Khitrov, and later Brendel and Bormann, "postulated" (the paper's
word) the convolution integral that introduces Gaussian (inhomogeneous)
broadening onto a classical Lorentz oscillator, Eq. (B.2), and solved it in
terms of Faddeeva functions, Eq. (B.3). The correction: the BB closed form
confuses the resonance frequency $\Omega$ with the natural frequency
$\omega_0$, uses a sum instead of a difference of two Faddeeva-function terms
where the correct Gauss-Lorentz derivation (their own Eq. B.9) needs a
difference, and above all is **noncausal**, so despite being widely
adopted by experimentalists fitting infrared spectra it cannot be coupled to a
time-domain Maxwell solver at all. The paper's Gauss-Lorentz model, Eq. (B.8)-
(B.9), is presented explicitly as the causal fix.

## LINEAGE BRIDGES

**This is the general inverse-problem formulation our Delone-reduction
machinery is a forward-modeled, atomic-physics instance of.** [delone1980](delone1980.md)
already contains, in a 1980 atomic-physics review, the same shape: a
Lorentzian resonance integrated against (equivalently, in the shift-dominated
limit, replaced by) a probability distribution $P(F)$ of the perturbing
variable, with the paper's own text noting "in principle one can reconstruct
the distribution $P(F)$" from the observed line. Prokopeva and Kildishev's
Eq. (2)-(3) and the fundamental dispersion relation Eq. (5) are the same
convolution/characteristic-function structure, generalized past a single
atomic transition to any homogeneous dispersion mechanism (oscillator,
relaxation, conductivity), made explicitly causal and Kramers-Kronig
consistent by carrying the broadening PDF's Hilbert transform as the imaginary
part of a single complex object $\mathcal G(x)$, and made numerically concrete
for time-domain solvers through MiMOSA. Where Delone gestures at the inverse
problem in one sentence, this paper builds the machine that actually performs
it, causally, in the time domain, and states retrieval of both pieces (the
homogeneous width and the disorder distribution) as a stated goal, achieved on
worked examples.

**Where this repository's construction sits in their taxonomy: a known
parametric family, forward-modeled, not their general inversion.** Table A's
top row, "ANY Broadening," is the fully general case: an arbitrary PDF
$G(x)$, retrieved from or imposed on a measured spectrum without assuming its
functional form beyond nonnegativity and normalization. Every worked model in
the paper (Gauss-Lorentz/Voigt, Gauss-Debye, Gauss-Drude, and the corrected
BB) instead specializes $G(x)$ to a Gaussian of known variance $\sigma^2$, a
*known parametric family*, and evaluates the resulting integral in closed
form rather than inverting it from data. The genuinely nonparametric,
data-driven case is future work (their own stated next step is extending to
asymmetric families such as Fermi-Dirac). This repository's $f(s) \propto |s|^{n-1}$
is exactly that same move, one level down: the intensity
distribution $P(I) \propto 1/I$ of a focused Gaussian beam is derived from
geometry, not fit to data, and is substituted into Delone's Eq. (5.3), the
atomic-physics analogue of Prokopeva-Kildishev's Eq. (5), to obtain a closed
form with analytic cumulants. So this repository's construction and
Prokopeva-Kildishev's worked models occupy the same taxonomic slot, a known,
first-principles-derived parametric $G$ pushed forward through the general
convolution relation, and neither performs the fully general inversion that
row 1 of Table A poses as the open problem.

**What their framework would add if the data ever warranted nonparametric
inversion.** If a measured 5S-6S lineshape ever showed structure the
triangular $|s|^{n-1}$ law cannot explain (for instance an additional disorder
mechanism not fixed by the beam geometry), MiMOSA supplies a ready-made route
to stop assuming the parametric family and instead fit a minimax rational
approximation of the complex PDF $\mathcal G(x)$ directly to the measured
profile, retrieving an unknown broadening distribution and the homogeneous
linewidth simultaneously while keeping causality and the Kramers-Kronig sum
rule exact by construction, with a stencil short enough (two to three poles)
to stay tractable. That is the retrieval Delone's Eq. (5.3) only gestures at
and this repository has never needed, because its $P$ has always been known
from geometry rather than being the unknown to be measured.
