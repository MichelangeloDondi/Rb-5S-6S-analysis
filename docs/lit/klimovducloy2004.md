---
citekey: klimovducloy2004
type: article
authors:
  - Klimov, V. V.
  - Ducloy, M.
title: 'Spontaneous emission rate of an excited atom placed near a nanofiber'
journal: Phys. Rev. A
volume: 69
pages: 013812
year: 2004
doi: 10.1103/PhysRevA.69.013812
arxiv: physics/0206048
pdf: PDF_papers/KlimovDucloy_2004_spontaneous-emission-atom-near-nanofiber.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'IDENTIFIER AMBIGUITY, unresolved. The held file is arXiv physics/0206048v2
    (20 December 2002), whose title matches Phys. Rev. A 69, 013812 (2004)
    exactly -- but the arXiv metadata carries an Optics Communications DOI
    (10.1016/S0030-4018(02)01802-3), not the PRA one. Either the arXiv
    journal-ref is stale/wrong, or the authors published a shorter Optics
    Communications version first and this preprint corresponds to both. The PRA
    reference above is as printed in sague2007 ref [14] and was verified against
    that bibliography; it has NOT been checked against the published PRA
    article. Settle before formal citation.'
  - 'The 31-page preprint is longer than a PRA article, which is consistent with
    it being the full manuscript behind a condensed publication. Section and
    equation numbers in the held file may therefore not match the published
    version -- do not cite an equation number from this file.'
verified_date: 2026-07-30
summary: >
  The theory input for the position-dependent free-space decay rate
  gamma_free(r) that sague2007 uses, and that patterson2018 omits from its
  width. Spontaneous decay rates of an excited atom near a DIELECTRIC CYLINDER,
  with the subwavelength (nanofiber / photonic wire) case treated specially:
  analytical expressions for the transition rates are derived for different
  dipole orientations, the dominant contribution is the QUASISTATIC interaction
  of the atomic dipole with the fibre, and guided-mode contributions are
  exponentially small in that regime. Section III READ: their
  Eq. (29) gives gamma_rad/gamma_0 in closed form for rho-, phi- and
  z-oriented dipoles, depending on position only through a^2/rho'^2, with the
  z rate unmodified and the rho and phi rates moving in OPPOSITE directions.
  THE CONCLUSION, READ THE SAME DAY, RETIRES THE PLAN TO USE THAT CLOSED FORM
  DIRECTLY: the paper proves quasistatic validity only for ka < 1/epsilon, and
  BOTH fibres of interest violate it -- patterson2018 at ka = 0.97 by a factor
  of two, sague2007 at ka = 1.84 by nearly four. Both land instead in the band
  1/eps < ka < 2.4/sqrt(eps-1) where the paper says guided-mode influence is
  SUBSTANTIAL, which is precisely why sague2007 carries a separate gamma_guid
  term. So a refit needs Section IV, not Eq. (29); and the +8.5%-vs-+27%
  discrepancy is more likely a symptom of using the formula out of range than
  the orientation-weighting effect this note first proposed.
loci:
  - P2
  - THEORY
section: method-anchors
---

# klimovducloy2004

Held. Section III and the Conclusion are read against the PDF. The remaining sections are unread. The authors are at the Lebedev Physical Institute, Moscow, and the Laboratoire de Physique des Lasers, Université Paris-Nord.

## The system

Spontaneous decay rates of an excited atom near a dielectric cylinder, with special attention to the case where the cylinder radius is small compared to the radiation wavelength (nanofiber or photonic wire). In that regime the paper derives analytical expressions for the transition rates for different dipole orientations. The main contribution to the decay rate is the quasistatic interaction of the atomic dipole with the fibre, and the contribution of guided modes is exponentially small. When the radius approaches the wavelength, guided-mode contributions instead become substantial.

For an ideally conducting nanowire, the decay rate of a radially oriented dipole tends to infinity as the cylinder radius goes to zero, so an orientation average rather than a single dipole orientation is needed near the surface. Non-radiative losses inside the fibre body are treated as a separate term.

## The quasistatic result

Section III (from p.6 of the held preprint) gives the radiative decay rate of an atom at radial distance $\rho'$ from the axis of a dielectric cylinder of radius $a$ and permittivity $\varepsilon$, their Eq. (29):

$$\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{\rho}
=\left|1+\frac{\varepsilon-1}{\varepsilon+1}\frac{a^2}{\rho'^2}\right|^2,\qquad
\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{\varphi}
=\left|1-\frac{\varepsilon-1}{\varepsilon+1}\frac{a^2}{\rho'^2}\right|^2,\qquad
\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{z}=1$$

At the surface, $\rho'=a$, their Eq. (30) reduces to $\vert 2\varepsilon/(\varepsilon+1)\vert ^2$, $\vert 2/(\varepsilon+1)\vert ^2$, and $1$.

The $z$ rate is unmodified at any distance. The $\rho$ and $\varphi$ rates move in opposite directions, so an orientation average is smaller than the radial component alone. The result depends on position only through $a^2/\rho'^2$.

## Validity

The paper states its regime of validity explicitly:

> "It is proved that quasistatic approximation works well for a nanofiber with $ka$ < $1/\varepsilon$."

> "For large enough nanofiber, $1/\varepsilon$ < $ka$ < $2.4/\sqrt{\varepsilon-1}$, the influence of guided modes on the decay rate is substantial."

For fused silica, $n = 1.4537$, $\varepsilon = 2.1132$, so $1/\varepsilon = 0.473$ and $2.4/\sqrt{\varepsilon-1} = 2.275$. The two fibres relevant to this project both fall in the band where guided modes are substantial:

| fibre | $a$ | $\lambda$ | $ka$ | quasistatic ($ka$ below 0.473)? | guided modes substantial? |
|---|---|---|---|---|---|
| [patterson2018](patterson2018.md), 240 ± 20 nm diameter | 120 nm | 780 nm | 0.967 | no, by a factor of 2 | yes |
| [sague2007](sague2007.md), 500 nm diameter | 250 nm | 852 nm | 1.844 | no, by a factor of 3.9 | yes |

Both fibres lie within the nanofibre regime overall ($ka$ below 2.275), so the paper's framework applies, but Eq. (29)/(30) alone is not sufficient for either. The full electrodynamic treatment of Section IV, or an explicit guided-mode term added to Eq. (29), is needed, which is the structure [sague2007](sague2007.md) uses: $\gamma = \gamma_{\rm free} + \gamma_{\rm guid}$, with $\gamma_{\rm guid} \simeq 0.3\gamma_0$ at the surface.

## Use in this record

[sague2007](sague2007.md) takes its position-dependent free-space decay rate $\gamma_{\rm free}(r)$ from this paper (their ref [14], checked against Sagué's own bibliography). [patterson2018](patterson2018.md) uses the same physical quantity as a detection weight and does not include it in its reported linewidth.

For fused silica at 852 nm ($n = 1.4537$, $\varepsilon = 2.113$), Eq. (30) gives, at the surface: $\gamma^{\rm rad}/\gamma_0 = 1.843$ for the radial orientation, $0.413$ for $\varphi$, $1.000$ for $z$, and $1.085$ (+8.5%) for an isotropic average. [sague2007](sague2007.md) states that its Eq. (2), this paper's $\gamma_{\rm free}$ plus their own $\gamma_{\rm guid} \simeq 0.3\gamma_0$ at the surface, predicts a 57% increase at the surface. Backing out the guided-mode contribution, $\gamma_{\rm free}$ must supply +27%. The isotropic average of Eq. (30) gives +8.5%, and the pure radial component gives +84%, so Sagué's 27% sits between the two.

Sagué's fibre has $ka = 1.84$, well outside the quasistatic bound $1/\varepsilon = 0.473$, so Eq. (30) is not expected to reproduce $\gamma_{\rm free}$ on its own regardless of orientation weighting. Whether the 8.5%-versus-27% gap reflects a mode-polarisation weighting of the orientations or simply reflects the quasistatic formula being evaluated outside its stated range is open. Section IV, the full electrodynamic treatment (about 10,600 characters, expanding the fields over cylinder harmonics and solving for the reflected field to obtain what the paper describes as "the exact expressions for decay rates, which include the contributions from guided modes"), would settle it and remains unread, along with Sections V and VI (the lossless-surface case and the graphical discussion). Klimov's ref [45], on spontaneous emission near metallic nanowires, was unpublished at the time and concerns a metallic rather than dielectric fibre.
