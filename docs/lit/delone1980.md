---
citekey: delone1980
type: article
authors:
  - Delone, N. B.
  - Kovarskii, V. A.
  - Masalov, A. V.
  - Perel'man, N. F.
title: 'An atom in the radiation field of a multifrequency laser'
journal: Sov. Phys. Usp.
volume: 23
pages: 472
year: 1980
doi: 10.1070/PU1980v023n08ABEH005024
arxiv: null
pdf: PDF_papers/Delone_1980_atom-in-multifrequency-laser-field-review.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'The held file is the English translation in Sov. Phys. Usp. 23(8), Aug 1980.
    Its OCR text layer is poor -- equations and
    Greek are mangled -- so everything below was read from the RENDERED pages,
    not from text extraction, and equation numbers are as printed on the page.'
  - 'The DOI above is the standard IOP record for this article and was NOT
    verified against Crossref. Author order is as printed on the article.'
verified_date: 2026-07-30
summary: >
  THE origin of this programme's theoretical frame, and it is a 1980 REVIEW,
  meaning the frame was already established then. Their Eq. (4.5) states that
  the absorption lineshape IS the intensity distribution rescaled by the
  polarizability, K(Omega) ~ P(-(omega_n1 - Omega)/(alpha_1f hbar)); their
  Eq. (5.2) writes the multiphoton rate as a shifted Lorentzian integrated over
  P(F) with an F^k intensity weight; and their Eq. (5.3) gives the
  shift-dominated limit as (detuning)^k P(detuning/alpha), described as "an
  asymmetrically broadened line" from which "in principle one can reconstruct
  the distribution P(F)". Lineshape-as-a-map, the k-photon weighting, the
  asymmetry, and the inverse problem are all there. What is NOT there is a
  GEOMETRIC distribution: their P(F) is the statistics of a fluctuating field,
  unknown a priori, where this programme's is set by the beam profile and
  therefore closes in form with analytic cumulants.
loci:
  - THEORY
  - P1
section: prior-art
---

# delone1980

Held. Quotations below are transcribed by eye from the rendered page images of
the English translation (Sov. Phys. Usp. 23(8), 1980). The scan's OCR text
layer is unusable, so these carry lower confidence than machine-verified
quotations elsewhere in this record.

## The system

This 1980 paper treats an atom in the field of a multifrequency (multimode)
laser, covering resonant and nonresonant perturbation of atomic levels, and
multiphoton excitation, by a field with fluctuating intensity.

## The lineshape as a map of the intensity distribution

Section 4b (nonresonance perturbation, narrow spectrum), Eq. (4.5):

$$K(\Omega) \sim P\left(-\frac{\omega_{n1}-\Omega}{\alpha_{1f}\hbar}\right), \qquad \frac{\Omega-\omega_{n1}}{\alpha_{1f}\hbar} \gt 0$$

"Just as in the case of resonance perturbation, the shape of the line
reflects the set of positions of the atomic level that are realized in the
ensemble of random values of the radiation intensity. It can be obtained by
averaging the shape of the line in a monochromatic field over the
distribution $P(F) $." For a level shift linear in intensity and a negligibly
narrow unperturbed line, the lineshape is the intensity distribution,
rescaled by the polarizability.

The inverse problem is stated directly: "The treatment that we have carried
out above of perturbation of atomic levels in a nonmonochromatic field allows
the general conclusion that one can reconstruct the properties of the
radiation from perturbation data in the narrow-spectrum case: in the
resonance case one can reconstruct the field amplitude distribution
$\mathcal{P}(A) $, and the intensity distribution $P(F)$ in the nonresonance
case." This principle is restated, with attribution to this paper, by
Camparo and Lambropoulos (1992) for a two-photon transition ([camparo1992](camparo1992.md)).

## The multiphoton case

Section 5, Eq. (5.2):

$$W \sim \int_0^{\infty} P(F)  F^{k}  \frac{\Gamma(F)}{[\omega_f - k\omega_0 + \delta\omega(F)]^2 + [\Gamma(F)]^2}  {\rm d}F$$

a Lorentzian whose centre is displaced by a shift $\delta\omega(F) $,
integrated over the distribution of $F$ and weighted by $F^{k}$ for a
$k$-photon transition. In the shift-dominated limit $\delta\omega(F) \gg \Gamma(F)$ (subject also to resonance with the shifted level, the sign
condition $(\omega_f - k\omega_0)/(\alpha_{1f}\hbar) \gt 0$, and
$\vert \omega_f - k\omega_0\vert  \gg \Gamma(F) $), Eq. (5.3) gives

$$W \sim (\omega_f - k\omega_0)^{k}  P\left(\frac{\omega_f - k\omega_0}{\alpha_{1f}\hbar}\right)$$

described as amounting to "an asymmetrically broadened line," from which "in
principle one can reconstruct the distribution $P(F) $."

## Validity

The $F^k$ power-law picture of Section 5 holds where the field-induced shifts
and widths of the atomic levels are smaller than the natural widths. Where
the induced shift and width instead govern the process, the lineshape is
explicitly not of power-law type. Section 3 names three further exits from
the frame: tunnelling character, the appearance of intermediate resonances,
and the inapplicability of a rate description at long pulse duration.

Section 6c extends the treatment to resonance-enhanced multiphoton
absorption, $k = k_1 + k_2$ through a real intermediate resonance, and gives
the field-induced perturbations of the resonant state with their intensity
scalings:

- a field width from ground/resonant-state mixing, $\Gamma_f = d_{01}F^{k_1/2}$ (Eq. 6.6)
- a nonresonance shift, $\delta\omega_{01} = \tfrac14\alpha F$ (Eq. 6.7)
- an ionization broadening to the continuum, $\Gamma_i = \alpha_{1E}F^{k_2}$ (Eq. 6.8)

The prescription is the weak-field Lorentzian of Eq. (6.5) with $\Gamma$
replaced by a combination of $\Gamma_f$ and $\Gamma_i$.

The distribution $P(F)$ throughout is a statistical property of the light
source, generally exponential for thermal light, and it is not known a
priori. It is the quantity the inverse problem reconstructs. This differs
from a distribution set by the geometry of a coherent beam's transverse
intensity profile, which is known in advance and yields a closed form with
analytic cumulants.

## Related methods outside atomic spectroscopy

The idea of treating inhomogeneous broadening as a probability distribution
over a lineshape's parameters recurs outside atomic physics. A. Efimov and V.
Khitrov, "Analytical formulas for describing the dispersion of glass with
refractive indices that observe the continuous nature of absorption," *Fiz.
Khim. Stekla* 5(5), 583-588 (1979), give an early example. R. Brendel and D.
Bormann, "An infrared dielectric function model for amorphous solids," *J.
Appl. Phys.* 71(1), 1-6 (1992), postulate the same convolution integral for
amorphous-solid infrared spectra, though its closed form is later shown to be
noncausal. [prokopeva2025](prokopeva2025.md) extends both to a causal,
Kramers-Kronig-consistent framework that recovers the intrinsic homogeneous
linewidth and the inhomogeneous disorder distribution together from a
measured lineshape, for dielectric-function models in nanophotonic materials
(Gauss-Lorentz, Gauss-Debye, Gauss-Drude).

## Use in this record

For atoms distributed uniformly across a Gaussian transverse profile
$I(r) = I_0 e^{-2r^2/w^2}$, the area measure gives
$2\pi r {\rm d}r \propto {\rm d}I/I$, so $P(I) \propto 1/I$ (confirmed
numerically to 1 part in $10^4$ by binning $I$ over four decades with a
$2\pi r$ weight). Substituting into Eq. (5.3), $W(s) \propto s^{k}P(s/\alpha\hbar)$
with $P \propto 1/s$ gives $W(s) \propto s^{k-1}$, i.e.
$f(s) \propto \vert s\vert ^{n-1}$ with $k = n$: the power-law lineshape used elsewhere
in this record is Eq. (5.3) evaluated for the intensity distribution of a
focused Gaussian beam. At $n=2$, Eq. (5.3) with this geometric $P$ agrees
with the shipped implementation (`rb5s6s.lineshape.stark_ramp`) to a maximum
absolute difference of $7\times10^{-12}$ on the normalised profile. Because
$P$ is fixed by beam geometry rather than by unknown laser statistics, the
resulting lineshape has analytic cumulants, including an intrinsic skewness
$g_1 = +0.566$ at $n=2$ on the bounded support $[-S_0,0]$. The third cumulant
is used as a drift-immune channel for measuring $S_0$.

At the measured beam waist in this experiment, the Section 5 validity
condition holds with about a factor of ten to spare: the ramp edge is 0.348
MHz against a natural width of 3.4925 MHz. For the resonance-enhanced case of
Section 6c, applied to a third 993 nm photon reaching the real 6S population
through a 2+1 process: the intermediate state lies 345 cm⁻¹ from the
6S–8P₃⁄₂ transition, the 8P admixture is $1.7\times10^{-9}$ at the campaign
field, the combined scattering rate through all channels is 0.122 s⁻¹
against a 6S decay rate of $2.194\times10^{7}$ s⁻¹, and the associated
fourth-order shift is of order $10^{-3}$ Hz, eight orders of magnitude below
the light-shift bound (numbers in [THEORY_NOTE](../THEORY_NOTE.md), section
5.2).
