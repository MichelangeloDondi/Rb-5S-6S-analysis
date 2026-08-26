---
citekey: frawley2012
type: article
authors:
  - Frawley, Mary C.
  - Nic Chormaic, Síle
  - Minogin, Vladimir G.
title: 'The van der Waals interaction of an atom with the convex surface of a nanocylinder'
journal: Phys. Scr.
volume: 85
pages: 058103
year: 2012
doi: 10.1088/0031-8949/85/05/058103
arxiv: null
pdf: PDF_papers/Frawley_2012_Phys._Scr._85_058103.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'the integrands OF eqs (18), (20) and (23) DO not survive PDF text
    extraction cleanly. In particular the leading factor extracts as
    "Im(kR) Km(kR)", which is almost certainly a stacked fraction (a ratio of
    modified Bessel functions, possibly of derivatives) rendered as a product.
    DO not code these equations from this note -- read them off the rendered
    page first. The mu values quoted below are from prose and are reliable.'
  - 'The abstract and the body state the curvature effect at different
    distances, and the abstract is the outlier rather than merely the looser of
    the two -- this flag said only "looser" until it was checked. The abstract
    puts the halving "at distances of the order of a cylinder radius"; the body
    puts "less than 0.75" at x_0 = R and "a little more than 0.5" only at
    x_0 = 5R. Prefer the body; its wording is reproduced below. Reading the
    curvature
    result off the abstract alone is exactly what produced a wrong claim in this
    repo on 2026-07-31.'
  - 'its own electrostatic derivation has A validity BOUND, stated in section 1
    and easy to miss: nanobody size less than lambda/2pi ~= 100 nm, i.e. Ka < 1.
    patterson2018 sits at ka = 0.967 (inside, but only just) and sague2007 at
    1.844 (outside). See the body.'
verified_date: 2026-07-31
summary: >
  Closed analytical equations, in the electrostatic approximation, for the van
  der Waals potential and force of an atom outside a nanocylinder -- metal and
  dielectric. Writes the result as the flat-surface form times a dimensionless
  surface factor, U = -(C_3/x_0^3) mu, with mu given by a Bessel integral. The
  operationally important fact is the opposite of what this repo briefly
  recorded from a paraphrase: mu -> 1 at short range (x_0 << R), where "the
  curvature of the surface is of no importance"; the weakening sets in only at
  x_0 ~ R (mu < 0.75) and reaches ~0.5 near x_0 = 5R. So a flat-surface C_3/x^3
  is good close to a nanofibre and fails far from it. Its Conclusion also
  proposes that this sharp decrease "can be responsible for the strong
  asymmetry of the spontaneous emission line of an atom into an optical
  nanofiber" -- an asymmetry-from-a-surface-potential suggestion predating
  patterson2018 by six years.
loci:
  - P2
section: method-anchors
---

# frawley2012

Held.

## The model

The van der Waals potential of an atom outside a cylinder of radius $R$ at
distance $x_0$ from the surface, in the electrostatic approximation, for metal
and dielectric cylinders. Eq. (19) factorises the result into the flat-surface
potential times a dimensionless surface factor:

$$U = -\frac{C_3}{x_0^3} \mu$$

with $\mu$ (Eq. 20) an integral of modified Bessel functions summed over $m$,
and a matching force factor $\nu$ (Eqs. 22-23) with $F = -3C_3\nu/x_0^4$.

## The numbers

Verbatim from the body:

> "At short distances, i.e. When $x_0 \ll R$, this factor is close to unity and
> therefore the curvature of the surface is of no importance in the evaluation
> of the van der Waals interaction energy."

> "For example at $x_0 = R$, the cylindrical case is less than 0.75 that of the
> flat case, and this factor reduces to a little more than 0.5 for a dipole at
> $x_0/R = 5$."

> "at a distance $x_0 = 100R$, the value of the $\mu$-factor is about 0.2"

$\nu$ behaves the same way: near unity at the surface, about 0.5 by
$x_0 \simeq 10R$.

| $x_0/R$ | $\mu$ |
|---|---|
| $\ll 1$ | $\to 1$ |
| 1 | below $0.75$ |
| 5 | $\approx 0.5$ |
| 100 | $\approx 0.2$ |

The abstract states the halving of the surface factor at "distances of the
order of a cylinder radius," while the body gives $\mu \lt  0.75$ at $x_0 = R$ and
$\mu \approx 0.5$ only near $x_0 = 5R$. The body's figures are used here.

For caesium around a silica fibre of radius $a = 100$ nm, the paper's worked
example gives $C_3 = 1.6$ mHz $\mu\mathrm{m}^3$.

## Validity

The paper states the condition under which the electrostatic route replaces
the full QED problem:

> "if one is dealing specifically with nanobodies of sizes less than
> $\lambda/2\pi \simeq 100$ nm and if one assumes that the distance between the
> atom and the nanobody is of the same order of magnitude, the van der Waals
> energy can be determined using a relatively simple electrostatic approach"

The size condition is $a$ below $\lambda/2\pi$, i.e. $ka$ below 1. This is the
same $ka$ that governs klimovducloy2004, with a looser threshold than that
paper's quasistatic bound of $ka$ below $1/\varepsilon = 0.473$.

| fibre | $\lambda/2\pi$ | $a$ | $ka$ | Frawley ($ka$ below 1) | Klimov ($ka$ below 0.473) |
|---|---|---|---|---|---|
| patterson2018 | 124.1 nm | 120 nm | 0.967 | inside, marginally | violated |
| sague2007 | 135.6 nm | 250 nm | 1.844 | violated | violated |

The electrostatic approximation is marginally valid at Patterson's fibre ($a$
is 97 percent of the stated limit) and outside its range at Sagué's. The
companion distance condition, that the atom sits at roughly the nanobody's own
size scale from the surface, is satisfied for near-surface atoms tens of
nanometres from the wall.

The companion interior-geometry solution (afanasiev2010) gives the hollow-core
case in the same factorised form, and the two agree that the surface factor
approaches unity at the wall in either curvature, making curvature a
distance-scale effect rather than a near-surface one.

## The asymmetry proposal

The Conclusion states:

> "the sharp decrease in the potential with distance can be responsible for
> the strong asymmetry of the spontaneous emission line of an atom into an
> optical nanofiber"

This attributes line asymmetry to a distance-dependent surface potential,
predating patterson2018's measurement and naming of such an asymmetry by six
years. The paper does not develop the idea. There is no lineshape, moment, or
fit to data. Eq. (24) folds $\mu$ into an effective potential with the
centrifugal term, giving "expanded atomic orbits around the nanofibers, and
... Lowering the corresponding rotational frequencies."

## Use in this record

For patterson2018's fibre geometry (120 nm radius silica, near-surface atoms
tens of nanometres out), $x_0/R \lesssim 1$ and $\mu$ lies between 0.75 and 1,
so the flat-surface $C_3/x^3$ form holds there to within tens of percent. The
correction becomes significant only at $x_0 \gtrsim 5R$.
