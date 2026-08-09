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

**Held and read.** Institute of Spectroscopy, Troitsk.

## Why it was wanted

[schmidt2011](schmidt2011.md) reports that *concave* surfaces **enhance** the van
der Waals energy — up to a factor of 6 — but it is a **sphere**. This note's
predecessor flagged that carrying that into a cylindrical bore was "an
extrapolation across geometries and is not established here", and recorded it as
OPEN. **This paper is the cylinder case**, so the extrapolation is no longer
needed. The cylinder figure is **4**, not 6.

## What it gives

Same structure as its convex sibling [frawley2012](frawley2012.md) — which is
the point, since the two then compose into one consistent treatment:

$$U = -\frac{C_3}{x_0^3} \mu \qquad \text{(their Eq. 19)}$$

with $\mu$ the **internal** cylindrical surface factor (Eq. 20), a Bessel
integral summed over $m$, and $\rho_0 = R - x_0$ the distance from the axis.
Metal or dielectric; for a dielectric of permittivity $\varepsilon$ the same
equations hold with $C_3$ from their Eq. (10).

## The behaviour, verbatim

> "the potential for a concave cylindrical surface coincides with that for a
> flat surface at $\rho_0 \to R$ when $\mu \to 1$ and exceeds that for a flat
> surface by a factor of 4 near the center of the cylinder"

and against the two-plane case:

> "the absolute value of the potential for the cylindrical surface exceeds that
> for the two planes by a factor of 2 near the cent[re]"

| position | $\mu$ |
|---|---|
| at the wall ($\rho_0 \to R$, $x_0 \to 0$) | $\to 1$ |
| near the axis | $\to 4$ |

**This confirms, from the opposite geometry, the correction made today to
[frawley2012](frawley2012.md).** In *both* the convex and the concave case
$\mu \to 1$ at the surface: a flat-surface $C_3/x^3$ is the right form for an
atom close to a wall, whichever way the wall curves. Curvature only bites at
distances comparable to the radius — weakening it outside a fibre
($\mu \to 0.5$ and below), strengthening it inside a bore ($\mu \to 4$). The
paper says as much in its introduction, that the flat assumption "is evidently
fairly good for atoms located near the surface ... $x_0 \ll R$".

## What the factor of 4 is worth in practice: almost nothing

The enhancement lives near the **axis**, and $C_3/x_0^3$ at the axis is tiny.
Comparing the on-axis value $4C_3/R^3$ against the value 10 nm from the wall
(CALCULATED here, ratios only, so $C_3$ cancels):

| bore radius $R$ | on-axis $\div$ 10-nm-from-wall |
|---|---|
| 250 nm | $2.6\times10^{-4}$ |
| 2.5 µm | $2.6\times10^{-7}$ |
| 9 µm | $5.5\times10^{-9}$ |
| 22.5 µm ([perrella2013](perrella2013.md)) | $3.5\times10^{-10}$ |

So for every hollow core in this programme's sights the 4× multiplies a
vanishing quantity. **The concave enhancement is not a cost the guided-mode
extension has to carry**, and the earlier note in
[schmidt2011](schmidt2011.md) suggesting it be estimated for few-micron cores
"before the geometry is argued for on linewidth grounds alone" is answered: it
was estimated, and it is negligible. It would matter only for a *submicron*
bore, where atoms sit within a radius of the wall by construction.

## The other thing it proposes, which is not for us but is worth knowing

A **measurement scheme for $C_3$**: an atomic beam through a submicron channel
develops "a sharp transformation of the atomic beam profile, with a clear
separation of an internal narrow peak from a broad pedestal", and the transverse
density profile at different cross-sections then determines $C_3$. They note the
obvious difficulty, outgassing of submicron tubes, and argue the tube is short
enough for UHV to be realistic. Not a direction this programme is taking, but it
is a live experimental proposal on the same constant that
[patterson2018](patterson2018.md)'s bound-state analysis depends on.
