---
citekey: baranger1958
type: article
authors:
  - Baranger, M.
title: General Impact Theory of Pressure Broadening
journal: Phys. Rev.
volume: 112
number: 3
pages: 855--865
year: 1958
doi: 10.1103/PhysRev.112.855
arxiv: null
pdf: PDF_papers/Baranger_1958_general-impact-theory-pressure-broadening.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-08-03
summary: >
  Full text read (Phys. Rev. 112, 855-865, 1958). Synthesizes Baranger's
  papers I (quantum-mechanical perturbers, elastic collisions only) and II
  (classical perturber paths, but inelastic collisions, degeneracy, and
  overlapping lines) into one general impact theory. When collisions are on
  average weak and well separated in time (Eqs. 41a/41b, equivalently the
  dilute-gas condition U << n^-1, Eq. 42, plus w, d << perturber kinetic
  energy, Eqs. 43a/43b), the line is Lorentzian, and for an isolated
  nondegenerate one-state line the width is w = (1/2) n v sigma via the
  optical theorem (Eq. 72c) -- explicitly linear in perturber density n. This
  is the specific result docs/methods/02_the_lineshape.md Sec. 2.2 invokes
  for gamma_coll = beta_self * N (the derivation now lives in
  docs/wiki/self-broadening.md), and it is also the n*v*sigma scaling
  rb5s6s/vanderwaals.py (M18) uses to turn a computed C6 into a predicted
  beta_self(6S). Baranger does not supply the C6-to-sigma step itself; that
  is the module's separately-flagged Lindholm-Foley prefactor.
loci:
  - THEORY
  - M4
  - M18
section: collision-series
---

# baranger1958

Held. Read in full (11 pages). Bibliographic details (title, journal, volume 112, number 3, pages 855-865, 1 November 1958) check against the printed masthead.

## Abstract

"The work of two previous papers is extended and a theory of pressure broadening is developed which treats the perturbers quantum mechanically and allows for inelastic collisions, degeneracy, and overlapping lines. The impact approximation is used. It consists in assuming that it takes, on the average, many collisions to produce an appreciable disturbance in the wave function of the atom, and it results in an isolated line having a Lorentz shape. Validity criteria are given. When the approximation is valid, it is allowable to replace the exact, fluctuating interaction of the perturbers with the atom by a constant effective interaction. The effective interaction is expressed in terms of the one-perturber quantum mechanical transition amplitudes on and near the energy shell and its close relationship to the scattering matrix is stressed. The calculation of the line shape in terms of the effective interaction is the same as when the perturbers move on classical paths. Results are written explicitly for isolated lines. If the interaction of the perturbers with the final state can be neglected, the shift and width are proportional to the real and imaginary part of the forward elastic scattering amplitude, respectively. By the optical theorem, the width can also be written in terms of the total cross section. When the interaction in the final state cannot be neglected, the shift and width are still given in terms of the elastic scattering amplitudes, in a slightly more complicated fashion. Finally, rules are given for taking into account rotational degeneracy of the radiating states."

## The series

This is paper III of a series (I: Phys. Rev. 111, 481, 1958; II: Phys. Rev. 111, 494, 1958). Paper I treated perturbers quantum mechanically for elastic collisions on a nondegenerate atom only. Paper II allowed inelastic collisions, degeneracy, and overlapping lines, but moved the perturbers on classical paths. This paper synthesizes both: quantum-mechanical perturbers together with inelastic collisions, degeneracy, and overlapping lines, needed for a consistent theory of electron broadening, though the machinery is general and not restricted to electrons.

## The result

When the impact approximation holds, the exact, fluctuating atom-perturber interaction can be replaced by a constant, non-Hermitian effective interaction, $\mathfrak{K} = nR_{Nu}$ (Eqs. 37-38), built from the near-energy-shell one-perturber transition operator $R$, averaged over the Boltzmann-weighted perturber velocity distribution and scaled by the perturber density $n$. Once $\mathfrak{K}$ is known, the line shape follows exactly as in the classical-path theory of paper II (Eq. 69).

For an isolated, nondegenerate line, one-state case (only the initial atomic state interacts with the perturbers), the shift and width are the real part and minus the imaginary part of the diagonal element of $\mathfrak{K}$ (Eqs. 70a-b), which reduce to the real and imaginary parts of the forward elastic scattering amplitude $f(0)$ (Eqs. 71-72b), and, by the optical theorem, to

$$w = \left(\tfrac{1}{2}nv\sigma\right)_{Nu}$$

(Eq. 72c), the thermal average over the total (elastic + inelastic) cross section $\sigma$ and relative speed $v$, explicitly linear in the perturber density $n$.

For the two-state case (both initial and final atomic states interact), the width is richer than pure elastic dephasing (Eq. 77c):

$$w = \left\lbrace \tfrac12 nv\Big[\sigma_{i,\text{in}}+\sigma_{f,\text{in}}
 +\int d\Omega |f_i(\Omega)-f_f(\Omega)|^2\Big]\right \rbrace_{Nu}$$

The inelastic cross sections of both states add to the width directly, and the elastic contribution enters as the integral of the squared difference of the initial- and final-state elastic amplitudes. This generalizes the one-state, elastic-only limit, in which phase-interrupting collisions alone set the width: state-changing inelastic collisions contribute to the width as well, on top of dephasing.

## Validity

Defining the collision time $\tau$ via the collision volume $U=\tfrac12 v\sigma\tau$ (Eqs. 19-20), the impact approximation requires

$$w\tau\ll1\ \ (41\mathrm{a}), \qquad d\tau\ll1\ \ (41\mathrm{b})$$

Condition (41a) is equivalent, via (72c), to the dilute-gas condition

$$U\ll n^{-1}\ \ (42)$$

collision volume much smaller than the volume per perturber. Condition (41b) has no analog in paper I, whose simplified additive-force model made it automatic. Here it must be imposed separately. The Lorentz shape itself needs only (41a). Condition (41b) is needed in addition for the effective interaction to reduce to the near-shell scattering-amplitude formulas above.

Because $\tau$ cannot be smaller than $\epsilon^{-1}$ ($\epsilon$ the kinetic energy of a perturber), condition (41) implies

$$w\ll\epsilon\ \ (43\mathrm{a}), \qquad d\ll\epsilon\ \ (43\mathrm{b})$$

width and shift must be small compared with the perturbers' own kinetic energy. When (41a) holds, the Boltzmann population factor varies negligibly across the width of a line, so no correction for finite-temperature population smearing is needed inside the impact approximation.

The paper states that computing the scattering amplitudes or cross sections for a specific potential is outside the scope of pressure broadening: it supplies the general relation between $w$ and $\sigma$, not $\sigma$ itself.

## Use in this record

This repository's collisional term, $\gamma_\text{coll}=\beta_\text{self}N$ (`docs/methods/02_the_lineshape.md` Sec. 2.2, derived in `docs/wiki/self-broadening.md`), is the one-state, isolated-line result above, Eq. (72c), $w=(1/2)nv\sigma$, with $n$ the Rb density from `rb5s6s/density.py`. The same $w\propto nv\sigma$ scaling is used in `rb5s6s/vanderwaals.py` (M18) to turn a computed $C_6$ into a predicted $\beta_\text{self}$, via a cross-section-like quantity multiplied by $n$ and $v^{0.6}$ and a literature Lindholm-Foley prefactor. That prefactor, the step from a $-C_6/R^6$ potential to a cross section, is not supplied by Baranger and is flagged in the code as taken from the pressure-broadening literature rather than derived. A double-applied HWHM-to-FWHM conversion in `beta_self_vdw` had been read as a 1.7x over-prediction against the one state with a measured self-broadening rate (7S, [zameroski2014](zameroski2014.md)). Corrected, the module sits about 17% low against that measurement, inside the envelope the valence-only truncation already predicts.

Checked against this repository's own densities, Baranger's validity conditions hold by wide margins across the full 70-130 C sweep. At 130 C the vapour-cell density is about $2.9\times10^{13} \text{cm}^{-3}$ (about $5.6\times10^{11} \text{cm}^{-3}$ at 70 C), giving a mean interatomic spacing $n^{-1/3}\approx326$ nm against a van der Waals interaction radius $\rho_W=(C_6/\hbar v)^{1/5}\approx2.3$ nm (using $C_6(5S{+}6S)\approx2.9\times10^4$ a.u. from M18): a factor of about 140 in spacing, or about $10^6$ in volume, inside the binary-collision regime. The energy condition holds by a similar margin: $kT/h\approx8.4$ THz at 130 C against widths of order kHz-MHz, a factor of $10^7$ to $10^9$. What remains open is not the impact approximation but the Lindholm-Foley $C_6\to\sigma$ conversion built on top of it, against which the archival self-broadening bound sits 8-15x above the $C_6$-anchored expectation ([zameroski2014](zameroski2014.md)).
