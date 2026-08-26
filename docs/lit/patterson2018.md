---
citekey: patterson2018
type: article
authors:
  - Patterson, B. D.
  - Solano, P.
  - Julienne, P. S.
  - Orozco, L. A.
  - Rolston, S. L.
title: 'Spectral asymmetry of atoms in the van der Waals potential of an optical nanofiber'
journal: Phys. Rev. A
volume: 97
pages: 032509
year: 2018
doi: 10.1103/PhysRevA.97.032509
arxiv: '1801.01585'
pdf: PDF_papers/Patterson_2018_ONF-vdW-spectral-asymmetry-Rb.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags:
  - 'Held as arXiv v1 (1801.01585, 4 January 2018). The journal fields are the
    published PRA reference as given by the citing paper sadeghi2026 and should
    be confirmed against the published article before formal citation; the arXiv
    record carries no journal-ref.'
verified_date: 2026-07-30
summary: >
  The direct precedent for the nanofibre extension: an ASYMMETRIC lineshape produced by a
  spatially distributed level shift in an optical-nanofibre geometry, quantified
  and fitted. Cold Rb-87 around a 240 nm ONF; the van der Waals surface
  potential U = -C3/r^3 red-shifts atoms nearer the silica, and the transmission
  spectrum is modelled as a Lorentzian of position-dependent centre averaged
  over a density times coupling weight -- structurally the same construction as
  this programme's shift-distribution convolution, with a static surface
  potential in place of the AC-Stark shift. Reports an integral asymmetry
  parameter A = (L-R)/(L+R) rising to 0.36 and back down as the desorption laser
  is powered, and an UNEXPLAINED ~2 MHz of excess width (their Gamma_0 = 8.1(3)
  MHz is the total homogeneous width; the Rb D2 natural 6.065 MHz is supplied
  here, not by them) after Doppler, collective, Purcell, continuum-atom and
  Zeeman explanations are each excluded.
loci:
  - P2
  - THEORY
section: oist-lineage
---

# patterson2018

Held as arXiv v1 (1801.01585, 4 January 2018). The journal reference fields above are as cited by sadeghi2026 and have not been confirmed against the published article.

## The system

A ⁸⁷Rb magneto-optical trap (about 10⁸ atoms, a few hundred µK), at the Joint Quantum Institute (Maryland/NIST), surrounding an optical nanofibre of diameter 240 ± 20 nm. A weak, near-resonant 780 nm probe, held below a tenth of saturation intensity so there is no power broadening, is launched through the guided mode and its transmission recorded across the 5S₁/₂ F=2 → 5P₃/₂ F′=3 line. A far-off-resonance 750 nm laser in the same guided mode heats the fibre, thermally exciting physisorbed atoms into van der Waals bound states near the surface.

## Method

The surface potential is $U(r) = -C_3/r^3$, with $C_3 = 4.94 \times 10^{-49}$ J·m³ for 5S₁∕₂ and $7.05 \times 10^{-49}$ J·m³ for 5P₃∕₂, larger for the excited state and therefore red-shifting. The spectrum is modelled (their Eqs. 8–9) as

$$P_{\rm abs}(\omega) = \int r {\rm d}r ~ p_{\rm abs}(r,\omega) ~ \rho_{\rm tot}(r) ~ \alpha(r),$$

a homogeneous Lorentzian $p_{\rm abs}$, with detuning $\delta_{\rm vdW}(r) + \delta_L$, convolved with a signal-weighted distribution of level shifts: $\rho_{\rm tot}(r)$ is the atomic density and $\alpha(r) \propto I(r)$ is the position-dependent emission-enhancement weight. Atoms bound in the higher states move slowly enough for the quasistatic theory of line broadening to apply, so the spectrum is set by the local potential each atom feels. The density is modelled as $\rho(r) \propto 1/(1 - U(r)/E)$ with $E = k_BT/2$, plus a bound-state term $u_0 r^{-3/2}$.

## The numbers

| heating power (µW) | $\Gamma_0/2\pi$ (MHz) | $u_0$ | $A$ | $\chi^2_r$ |
|---|---|---|---|---|
| 0 | 8.1 ± 0.3 | 0 (fixed) | 0.14 | 1.11 |
| 40 | 8.1 (fixed) | 0.19 ± 0.09 | 0.19 | 1.16 |
| 120 | 9.2 ± 1.0 | 7182 ± 269 | 0.36 | 1.91 |
| 250 | 8.4 ± 0.9 | 5897 ± 612 | 0.26 | 1.32 |
| 350 | 9.5 ± 2.4 | 0.11 ± 0.11 | 0.12 | 1.29 |

The MOT-only spectrum has FWHM 8.9 ± 0.2 MHz with very little asymmetry. The asymmetry parameter $A = (L-R)/(L+R)$ (their Eq. 11), with $L$ and $R$ the absorption integrated red and blue of centre, is zero for a symmetric line and positive here because the van der Waals shift is red. It rises and falls with the heating-beam power (the probe stays fixed and is never scanned), peaking near 120 µW: at low heating too few atoms reach the high bound states, at high heating they desorb. Fitting $N \propto 1 - {\rm Erf}[b_o\sqrt{P}]$ with $T \propto P^{1/g}$, holding $b_o$ at its calculated value of 0.142 gives $g = 2.26 \pm 0.05$. Freeing $b_o$ gives $b_o = 0.156 \pm 0.019$ and $g = 2.15 \pm 0.136$, consistent with the first fit within error (both below the expected bound of 3).

The total homogeneous width, $\Gamma_0 = 8.1 \pm 0.3$ MHz (the 0 µW row), exceeds the ⁸⁷Rb D2 natural linewidth of 6.065 MHz (not stated in the paper) by about 2 MHz. The paper reports this excess as unexplained after excluding Doppler broadening (would require 72 mK against a measured few hundred µK), collective or superradiant enhancement (linear in atom number, and the width does not move with MOT density), Purcell modification (about 10% for similar distributions), continuum hot atoms (would add hundreds of MHz), Zeeman broadening (no response to the MOT coils), and power broadening (the probe stays below a tenth of saturation).

## Validity

Fit quality is $\chi^2_r$ 1.11–1.91 across the table, worse at higher heating power. The canonical $\Gamma_0 = 8.1 \pm 0.3$ MHz comes from the 0 µW row, whose fitted line centre ($\omega_0/2\pi = 5.9 \pm 0.2$ MHz) sits about five times higher than the other four rows (0.7–1.0 MHz). The paper checks $\Gamma_0$ against MOT temperature for covariance but not against line centre. The transition is single-photon, in cold atoms (5S→5P at a few hundred µK), so there is no transit-time broadening and no Doppler pedestal, and the shift is a static property of the dielectric rather than proportional to a driving field, so the asymmetry tracks heating-beam power rather than probe intensity. A similar unexplained excess, about 1 MHz over a natural linewidth of 5.2 MHz, was reported in Cs by Sagué et al. (2007) using a comparable analysis.
