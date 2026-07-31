---
citekey: schmidt2011
type: article
authors:
  - Schmidt, Regine
  - Nic Chormaic, Síle
  - Minogin, Vladimir G.
title: 'van der Waals interaction of a neutral atom with the surface of a metal or dielectric nanosphere'
journal: 'J. Phys. B: At. Mol. Opt. Phys.'
volume: 44
pages: 015004
year: 2011
doi: 10.1088/0953-4075/44/1/015004
arxiv: null
pdf: PDF_papers/Schmidt_2011_J._Phys._B__At._Mol._Opt._Phys._44_015004.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'ABSTRACT AND FRONT MATTER READ; the derivations in sections 2-4 are NOT.
    The factors of 6 and 2 quoted below are the paper''s own abstract wording.
    Their range of validity -- which distances, which permittivities -- has not
    been checked against the derivation, and the abstract does not state it.'
  - 'WRONG GEOMETRY for the nanofibre problem. This is a SPHERE. It is filed as a
    method anchor and as the source of the curvature result, not as an input to
    the patterson2018 refit; frawley2012 is the cylinder analogue, is HELD, and
    is the one actually needed. Where the two disagree, prefer Frawley -- and
    prefer Frawley''s BODY over either abstract, since taking the curvature
    result from an abstract alone produced a wrong claim here on 2026-07-31.'
verified_date: 2026-07-31
summary: >
  Closed analytical equations, in the electrostatic approximation, for the van
  der Waals energy of an atom near the INTERNAL and EXTERNAL surfaces of a metal
  or dielectric NANOSPHERE. Tyndall/UCC/Mainz/Troitsk -- Nic Chormaic and
  Minogin, the same group as frawley2012, of which this is the spherical
  counterpart. The result that carries beyond the geometry is that CURVATURE
  SIGN MATTERS: concave (internal) surfaces enhance the vdW energy by up to a
  factor of 6 over a flat surface, convex ones weaken it by up to a factor of 2.
  NOTE WHAT "UP TO" HIDES, because it is the whole story: the two held
  CYLINDRICAL papers from the same lineage -- frawley2012 (convex) and
  afanasiev2010 (concave) -- both have their surface factor tending to UNITY AT
  THE WALL, with curvature biting only at distances comparable to the radius. So
  a flat-surface C_3/r^3 is adequate near a surface of either curvature, and the
  extreme factors apply far from it. This SPHERE paper is superseded for both
  geometries by those two; keep it as the method anchor and for the fact that
  curvature sign matters at all.
loci:
  - P2
section: method-anchors
---

# schmidt2011

**Held and abstract read 2026-07-31**, supplied by the experimenter alongside
[boustimi2017](boustimi2017.md) while chasing the paywalled `boustimi2002`.

## The geometry is wrong, and the cylinder papers are the ones to use

This is a **sphere**, not a cylinder, so it is not an input to the
[patterson2018](patterson2018.md) refit. It is by **Nic Chormaic and Minogin**,
the same authors as [frawley2012](frawley2012.md), whose cylinder paper is the
one actually needed.

**Correction, recorded in place (2026-07-31).** This section previously said
this paper was useful because it "establishes in a primary source we hold the
claim that frawley2012 is currently carried on the strength of a search-engine
paraphrase". That was written in the few hours when frawley2012 was believed
unheld. It *was* held, and has since been read — so this paper underwrites
nothing about it, and where the two differ, Frawley's body governs. What
survives is narrower: this is an independent primary statement that **curvature
sign matters at all**, and it is the method anchor for the family.

## The result worth taking

Verbatim from the abstract:

> "We derive closed analytical equations for the van der Waals interaction
> energy using an electrostatic approximation and show that the energy increases
> or decreases as a function of the atom's distance from the surface, depending
> on the surface curvature. For concave spherical surfaces, the van der Waals
> energy can increase by up to a factor of 6, while for convex surfaces it
> decreases by as much as a factor of 2, when compared to that obtained for a
> flat surface."

And on what they are for:

> "The derived analytical equations are very simple and can be used for a
> comparison between theory and experimental measurements of the van der Waals
> constant, $C_3$."

## Two consequences for this programme

**Convex, factor of 2 down — but read the distance carefully.** The abstract's
"as much as" is doing real work. The cylindrical counterpart,
[frawley2012](frawley2012.md), is held and read, and it is explicit that the
weakening is a *far-field* effect: its surface factor $\mu \to 1$ for
$x_0 \ll R$, where "the curvature of the surface is of no importance", and only
reaches ~0.5 around $x_0 = 5R$. A flat-surface $C_3/r^3$ is therefore **fine
close to a nanofibre** and wrong far from it — the opposite of the reading this
note first took from the sphere abstract alone. That bears on
[patterson2018](patterson2018.md) and [liu2024](liu2024.md), both of which sit
on the convex exterior of a fibre with their atoms *close* to it, and for which
the flat-surface form is consequently adequate.

**Concave, factor of 6 up — and this is now CLOSED, without needing the
extrapolation.** A hollow-core experiment would put atoms *inside* a
hollow core: a concave dielectric surface. This note previously asked whether
the spherical 6× carries over to a cylindrical bore and recorded it as OPEN and
unquantified, warning that the sphere→cylinder step was exactly the kind of
geometric extrapolation this repository has been burned by. **The extrapolation
turned out to be unnecessary**: [afanasiev2010](afanasiev2010.md) (Minogin
again, PRA **82**, 052903) is the hollow-*cylinder* case, was obtained the same
day, and gives the factor directly. It is **4**, not 6, and it applies near the
axis; at the wall the internal surface factor goes to 1, exactly as the convex
factor does.

**And the enhancement is negligible in practice.** The 4× multiplies $C_3/x_0^3$
evaluated on the axis, which for any core in this programme's sights is between
$10^{-4}$ and $10^{-10}$ of the value 10 nm from the wall — see the table in
[afanasiev2010](afanasiev2010.md). So a hollow-core geometry would carry no van
der Waals cost from concavity, and the estimate this note asked for has been
done rather than deferred.
