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
  - 'THE INTEGRANDS OF EQS (18), (20) AND (23) DO NOT SURVIVE PDF TEXT
    EXTRACTION CLEANLY. In particular the leading factor extracts as
    "Im(kR) Km(kR)", which is almost certainly a stacked FRACTION (a ratio of
    modified Bessel functions, possibly of derivatives) rendered as a product.
    DO NOT CODE THESE EQUATIONS FROM THIS NOTE -- read them off the rendered
    page first. The mu VALUES quoted below are from prose and are reliable.'
  - 'The abstract and the body state the curvature effect at DIFFERENT
    DISTANCES, and the abstract is the OUTLIER rather than merely the looser of
    the two -- this flag said only "looser" until it was checked. The abstract
    puts the HALVING "at distances of the order of a cylinder radius"; the body
    puts "less than 0.75" at x_0 = R and "a little more than 0.5" only at
    x_0 = 5R. Prefer the body; its wording is reproduced below. Reading the
    curvature
    result off the abstract alone is exactly what produced a wrong claim in this
    repo on 2026-07-31.'
  - 'ITS OWN ELECTROSTATIC DERIVATION HAS A VALIDITY BOUND, stated in section 1
    and easy to miss: nanobody size less than lambda/2pi ~= 100 nm, i.e. ka < 1.
    patterson2018 sits at ka = 0.967 (inside, but only just) and sague2007 at
    1.844 (outside). See the body.'
verified_date: 2026-07-31
summary: >
  Closed analytical equations, in the electrostatic approximation, for the van
  der Waals potential AND force of an atom outside a nanocylinder -- METAL AND
  DIELECTRIC. Supplied by the experimenter on 2026-07-31 after being named as
  the top outstanding want; a claim in this note that it had been held all along
  was itself wrong and is corrected in the body. Writes the result as the flat-surface form times a dimensionless
  SURFACE FACTOR, U = -(C_3/x_0^3) mu, with mu given by a Bessel integral. The
  operationally important fact is the OPPOSITE of what this repo briefly
  recorded from a paraphrase: mu -> 1 at SHORT range (x_0 << R), where "the
  curvature of the surface is of no importance"; the weakening sets in only at
  x_0 ~ R (mu < 0.75) and reaches ~0.5 near x_0 = 5R. So a flat-surface C_3/x^3
  is GOOD close to a nanofibre and fails far from it. Its Conclusion also
  proposes that this sharp decrease "can be responsible for the strong
  asymmetry of the spontaneous emission line of an atom into an optical
  nanofiber" -- an asymmetry-from-a-surface-potential suggestion predating
  patterson2018 by six years.
loci:
  - P2
section: method-anchors
---

# frawley2012

**Held and read 2026-07-31.** University College Cork / Tyndall National
Institute, with Minogin at Troitsk. Síle Nic Chormaic is now at **OIST**.

**How it arrived, stated correctly.** This note first recorded the paper as
"NOT HELD — FETCH" from a search-engine paraphrase, then, a few minutes later,
as having been "in `PDF_papers/` the whole time" after an orphan scan found it.
**The second version was wrong**, and is corrected here: the file's birth time
is 2026-07-31 01:21:11, minutes after the scan was proposed and well after the
other papers supplied that night (Boustimi 01:09, Schmidt 01:10). The
experimenter supplied it during the session, in response to it being named as
the top outstanding want. Nobody failed to check the holdings; the holdings
changed. The paraphrase the first version rested on did get the physics
backwards, and that correction stands (below).

## What it gives

The van der Waals potential of an atom outside a cylinder of radius $R$ at
distance $x_0$ from the surface, in the electrostatic approximation, for
**metal and dielectric** cylinders. The useful form is their Eq. (19), which
factorises the answer into the flat-surface result times a dimensionless
**surface factor**:

$$U = -\frac{C_3}{x_0^3} \mu$$

with $\mu$ (their Eq. 20) a sum-over-$m$ integral of modified Bessel functions,
and a matching force factor $\nu$ (Eqs. 22–23) with $F = -3C_3\nu/x_0^4$. That
factorisation is what makes the paper usable: an existing $C_3/x^3$ model is
corrected by multiplying by one position-dependent scalar.

## The numbers, and the correction they force

Verbatim from the body:

> "At short distances, i.e. when $x_0 \ll R$, this factor is close to unity and
> therefore the curvature of the surface is of no importance in the evaluation
> of the van der Waals interaction energy."

> "For example at $x_0 = R$, the cylindrical case is less than 0.75 that of the
> flat case, and this factor reduces to a little more than 0.5 for a dipole at
> $x_0/R = 5$."

> "at a distance $x_0 = 100R$, the value of the $\mu$-factor is about 0.2"

$\nu$ behaves the same way — unity near the surface, ~0.5 by $x_0 \simeq 10R$.

| $x_0/R$ | $\mu$ |
|---|---|
| $\ll 1$ | $\to 1$ |
| 1 | $< 0.75$ |
| 5 | $\approx 0.5$ |
| 100 | $\approx 0.2$ |

**This inverts the claim this repository briefly carried.** On 2026-07-31 a
paraphrase of the abstract was recorded here, and propagated into
[patterson2018](patterson2018.md) and `LITERATURE.md`, as "a flat-surface
$C_3/r^3$ used at nanofibre distances overestimates the shift by about a factor
of two". **That is wrong.** The factor of two lives at $x_0 \sim 5R$, and at the
distances that dominate near-surface spectroscopy — tens of nanometres from a
120 nm-radius fibre, so $x_0/R \lesssim 1$ — $\mu$ is between about 0.75 and 1.
The flat-surface form is *good* there, to tens of percent, not wrong by two. The
correction has been made in both places.

(The abstract is the source of the confusion: it puts the halving "at distances
of the order of a cylinder radius", where the body says $x_0 = R$ gives $<0.75$
and $0.5$ arrives around $x_0 = 5R$. Where they differ, the body governs.)

## Where its own derivation is licensed — and it is not unconditional

**VERIFIED from section 1.** Frawley states the condition under which the
electrostatic route replaces the full QED problem:

> "if one is dealing specifically with nanobodies of sizes less than
> $\lambda/2\pi \simeq 100$ nm and if one assumes that the distance between the
> atom and the nanobody is of the same order of magnitude, the van der Waals
> energy can be determined using a relatively simple electrostatic approach"

The size condition is $a < \lambda/2\pi$, i.e. **$ka < 1$** — the same $ka$ that
governs [klimovducloy2004](klimovducloy2004.md), just with a looser threshold
(Klimov's quasistatic bound is the stricter $ka < 1/\varepsilon = 0.473$).
Evaluated (CALCULATED 2026-07-31):

| fibre | $\lambda/2\pi$ | $a$ | $ka$ | Frawley ($ka<1$) | Klimov ($ka<0.473$) |
|---|---|---|---|---|---|
| [patterson2018](patterson2018.md) | 124.1 nm | 120 nm | **0.967** | inside, **marginally** | violated |
| [sague2007](sague2007.md) | 135.6 nm | 250 nm | **1.844** | **violated** | violated |

So this paper is usable at Patterson's fibre but **only just** — $a$ is 97% of
the stated limit — and it is **out of range at Sagué's**. That must be carried
into any refit rather than discovered afterwards. The companion distance
condition is comfortably met for the near-surface atoms that matter, which sit
tens of nanometres out.

**Also useful, from their worked example:** for caesium around a silica fibre of
radius $a = 100$ nm they take $C_3 = 1.6$ mHz µm³ — a concrete constant for this
geometry, and the same alkali-on-silica combination as `sague2007`.

## The claim in its Conclusion that matters for the nanofibre extension

> "the sharp decrease in the potential with distance can be responsible for the
> **strong asymmetry of the spontaneous emission line** of an atom into an
> optical nanofiber"

That is asymmetry-of-a-line attributed to a distance-dependent surface
potential, proposed in 2012 — **six years before**
[patterson2018](patterson2018.md) measured it and named it. It is a
*suggestion*, not a derivation: there is no lineshape, no moment, no fit to
data here, and the paper does not develop it. But it belongs in the priority
discussion alongside [delone1980](delone1980.md), and it should be cited rather
than discovered by a referee. **Recorded for the the nanofibre extension novelty audit.**

It also draws the trapping consequence — Eq. (24) puts $\mu$ into an effective
potential with the centrifugal term, giving "expanded atomic orbits around the
nanofibers, and ... lowering the corresponding rotational frequencies".

## Status

The formulae are **not yet coded**, and per the verify flag they must be read
off the rendered page before they are — the Bessel integrands do not extract
reliably. Together with [klimovducloy2004](klimovducloy2004.md) (whose
quasistatic form, note, is *not* valid at either fibre of interest) this is one
of the two theory inputs the Patterson refit needs. **Recorded as OPEN.**

Its concave counterpart, [afanasiev2010](afanasiev2010.md) (Minogin again), was
obtained the same day and gives the interior case in the identical factorised
form. The two together settle the geometry question for the nanofibre exterior
and the hollow-core interior from primary sources, and they agree on the point
that matters most: **the surface factor tends to unity at the wall in both
curvatures**, so a flat-surface $C_3/x^3$ is the right form close in and
curvature is a distance-scale effect, not a near-surface one.
