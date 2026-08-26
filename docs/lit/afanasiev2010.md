---
citekey: afanasiev2010
type: article
authors:
  - Afanasiev, Anton
  - Minogin, Vladimir
title: 'van der Waals interaction of an atom with the internal surface of a hollow submicrometer-size cylinder'
journal: Phys. Rev. A
volume: 82
pages: 052903
year: 2010
doi: 10.1103/PhysRevA.82.052903
arxiv: null
pdf: PDF_papers/Afanasiev_2010_vdW-atom-internal-surface-hollow-nanocylinder.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'The Bessel integrand of Eq. (20) does not extract cleanly from the PDF.
    "Km(kR) Im(kR)" is almost certainly a stacked fraction rendered as a
    product, and note it is inverted relative to frawley2012 Eq. (20) -- there
    the ratio runs I/K with K-squared brackets, here K/I with I-squared
    brackets, which is what one expects for interior vs exterior, but it has not
    been confirmed off the rendered page. Do not code from this note.'
  - 'The prose, the abstract, the conclusion and all the factors below were read
    directly and are reliable. Only the explicit integrand is uncertain.'
  - 'Authors: this is Afanasiev and Minogin. It is not a Frawley/Nic Chormaic
    paper, though it was surfaced through that group''s citation network and
    shares Minogin and the method.'
verified_date: 2026-07-31
summary: >
  The concave counterpart of frawley2012, by Minogin with Afanasiev, held and
  read. Closed analytical equations, electrostatic approximation, for
  an atom inside a metal or dielectric hollow cylinder. Same factorised form
  U = -(C_3/x_0^3) mu, with an internal cylindrical surface factor mu that goes
  to 1 at the wall and rises to 4 near the axis -- so a flat-surface C_3/x^3 is
  right at the wall in the concave case too, and curvature only matters at
  distances comparable to the bore radius. It also exceeds the two-parallel-
  planes result by a factor 2 near the centre. Together with frawley2012 this
  settles the geometry question for both the nanofibre exterior and the
  hollow-core interior from primary sources, and it retires the sphere->cylinder
  extrapolation that schmidt2011 had been carrying. For realistic hollow cores
  the 4x is practically irrelevant -- see the body, it multiplies a quantity
  ~1e-9 of the near-wall value.
loci:
  - P2
section: method-anchors
---

# afanasiev2010

Held. The prose, abstract, and conclusion were verified directly against the PDF. The Bessel integrand of Eq. (20) could not be extracted cleanly from the rendered page and is not used here.

## The system

An atom inside a hollow metal or dielectric cylinder, the concave counterpart of the exterior treatment in [frawley2012](frawley2012.md), solved in the electrostatic approximation with closed analytical results.

## The potential

$$U = -\frac{C_3}{x_0^3} \mu \qquad \text{(Eq. 19)}$$

with $\mu$ the internal cylindrical surface factor (Eq. 20), a Bessel integral summed over $m$, and $\rho_0 = R - x_0$ the distance from the axis. For a dielectric of permittivity $\varepsilon$, the same equations hold with $C_3$ from Eq. (10).

> "the potential for a concave cylindrical surface coincides with that for a flat surface at $\rho_0 \to R$ when $\mu \to 1$ and exceeds that for a flat surface by a factor of 4 near the center of the cylinder"

> "the absolute value of the potential for the cylindrical surface exceeds that for the two planes by a factor of 2 near the cent[re]"

| position | $\mu$ |
|---|---|
| at the wall ($\rho_0 \to R$, $x_0 \to 0$) | $\to 1$ |
| near the axis | $\to 4$ |

In both the convex and concave geometries, $\mu \to 1$ at the surface, so a flat-surface $C_3/x^3$ form holds for an atom close to a wall regardless of the curvature direction. Curvature effects appear only at distances comparable to the radius. They weaken the potential outside a fibre ($\mu \to 0.5$ and below, per frawley2012) and strengthen it inside a bore ($\mu \to 4$, here).

## Magnitude for realistic bores

Ratio of the on-axis value $4C_3/R^3$ to the value 10 nm from the wall, by bore radius (ratios only, so $C_3$ cancels):

| bore radius $R$ | on-axis $\div$ 10-nm-from-wall |
|---|---|
| 250 nm | $2.6\times10^{-4}$ |
| 2.5 µm | $2.6\times10^{-7}$ |
| 9 µm | $5.5\times10^{-9}$ |
| 22.5 µm ([perrella2013](perrella2013.md)) | $3.5\times10^{-10}$ |

For bore radii of a few hundred nanometres and above, the concave enhancement multiplies a vanishing quantity and is negligible. It matters only for a sub-micron bore, where atoms sit within one radius of the wall by construction.

## A proposed measurement of C3

The paper also proposes measuring $C_3$ from an atomic beam through a sub-micron channel. The transverse density profile develops "a sharp transformation of the atomic beam profile, with a clear separation of an internal narrow peak from a broad pedestal," and its shape at different cross-sections determines $C_3$. The main obstacle is outgassing of sub-micron tubes. The authors argue the required tube length is short enough for UHV to remain realistic.

## Use in this record

Together with [frawley2012](frawley2012.md), this settles the surface-curvature question for both the nanofibre exterior and the hollow-core interior from primary sources, replacing an earlier sphere-to-cylinder extrapolation. For the hollow-core radii relevant here (≥250 nm), the concave correction is negligible and a flat-surface treatment is used.
