---
citekey: bruvelis2012
type: article
authors:
  - Bruvelis, M.
  - Ulmanis, J.
  - Bezuglov, N. N.
  - Miculis, K.
  - Andreeva, C.
  - Mahrov, B.
  - Tretyakov, D.
  - Ekers, A.
title: 'Analytical model of transit time broadening for two-photon excitation in a three-level ladder and its experimental validation'
journal: Phys. Rev. A
volume: 86
pages: 012501
year: 2012
doi: 10.1103/PhysRevA.86.012501
arxiv: null
pdf: null
held: false
status: REPORTED
routing:
  - CITE
verify_flags:
  - 'REPORTED. Record taken from Crossref (authoritative for the DOI) and the
    abstract from the publisher listing, 2026-07-30; the paper itself has not
    been read and APS returns 403 without a subscription. Upgrade after reading
    the full text -- the exact-compensation claim below is the one that matters
    here and should be checked against their derivation, not against a summary.'
  - 'CITEKEY CORRECTION: this repository cited the paper as `bevilacqua2012`
    until 2026-07-30. There is no Bevilacqua among the authors. The volume, page
    and year were right and the physics description was right; only the
    attribution was wrong, so a manuscript built on the old key would have
    carried a citation to a person who did not write it.'
  - 'The measured system is a supersonic beam of Na2 MOLECULES, not an alkali
    vapour. The result is derived for a general three-level ladder and the
    transfer is on the geometry, not on the species -- but the note must not be
    read as a vapour-cell measurement.'
verified_date: null
summary: >
  Analytical model of transit-time broadening for two-photon excitation in a
  three-level ladder, validated on a collimated supersonic Na2 beam crossing two
  counterpropagating laser beams. A two-level model with a virtual intermediate
  level gives a VOIGT excitation profile, with a stated validity range -- and the
  key geometric result: broadening from the curvature of the laser wavefronts
  along the particle path is EXACTLY compensated by the longer transit of
  particles farther off axis, so the width is set solely by the beam waist w0.
  Direct support for this programme's treatment of w0 as the dominant
  systematic. Cited under the wrong first author (`bevilacqua2012`) until
  2026-07-30.
loci:
  - M9
  - THEORY
section: prior-art
---

# bruvelis2012

**REPORTED, 2026-07-30.** Bibliographic record from Crossref, which is
authoritative for the DOI; **full abstract supplied by the experimenter from the
publisher listing the same day**, which confirms the author list and the
correction below. Not held and not read in full — APS returns 403 without a
subscription.

**Abstract, verbatim.** "We revisit transit time broadening for one of the
typical experiment designs in molecular spectroscopy, that of a collimated
supersonic beam of particles crossing a focused Gaussian laser beam. In
particular, we consider a Doppler-free arrangement of a collimated supersonic
beam of Na₂ molecules crossing two counterpropagating laser beams that excite a
two-photon transition in a three-level ladder scheme. We propose an analytical
two-level model with a virtual intermediate level to show that the excitation
line shape is described by a Voigt profile and provide the validity range of this
model with respect to significant experimental parameters. The model also shows
that line broadening due to the curvature of laser field wave fronts on the
particle beam path is exactly compensated by increased transit time of particles
farther away from the beam axis, such that the broadening is determined solely by
the size of the laser beam waist. The analytical model is validated by comparing
it with numerical simulations of density-matrix equations of motion using a split
propagation technique and with experimental results."

Two things that abstract settles, and one it sharpens. The geometry is
**Doppler-free, counterpropagating, two-photon through a virtual intermediate
level** — the same class as this programme's, not merely a general ladder
result, which strengthens the transfer considerably. And the analytical model is
validated twice over, against density-matrix numerics (split propagation) *and*
against experiment, so the exact-compensation claim is not resting on the
analytics alone. What it sharpens rather than settles is the thing still worth
reading the paper for: the abstract says a **validity range** is provided but not
what it is, and whether this programme's geometry sits inside it is exactly the
question.

**The result this programme needs.** For two-photon excitation in a three-level
ladder, an analytical two-level treatment with a virtual intermediate level gives
an excitation lineshape that is a **Voigt profile**, with the validity range
stated against the experimental parameters. The geometric part is the one that
matters here: line broadening caused by the **curvature of the laser wavefronts**
along the particle path is *exactly compensated* by the **increased transit time
of particles farther from the axis**, so the broadening is determined **solely by
the size of the beam waist**.

That is precisely the assumption underneath M9 and the whole
`w0`-as-dominant-systematic story: the transit contribution is a function of
$w_0$ alone, and the beam's divergence does not add a second, independent width.
**A correction to how this note first described the transit kernel, because it
had the repository's own position backwards.** Neither
[biraben1979](biraben1979.md) nor [lehmann2021](lehmann2021.md) gives a Voigt:
Biraben, Bassini & Cagnac obtain a *convolution of a Lorentzian and a
double-exponential* — the cusped kernel — and Lehmann's form is the same family.
In this repository the **Voigt is the rival**, not the inherited assumption: it
is the `transit_kind='gaussian'` leg of the M4c/M8 model-form systematic on
$\beta_{\rm self}$, run precisely so the difference against the two-sided
exponential can be quoted as an error bar. So Bruvelis reporting a **Voigt**
excitation profile is not a confirmation of what this repository assumes — it is
a data point on the side of the rival form, for a different geometry (supersonic
molecular beam) and a different observable. What transfers cleanly is the
geometric result below; the lineshape claim needs the full text and a careful
look at whether their two-level-with-virtual-intermediate reduction is doing the
Gaussianising.

**Two things to hold onto rather than assume.** The measurement is a collimated
supersonic beam of **Na₂ molecules**, not a hot alkali vapour — the derivation is
for a general ladder and the transfer is geometric, but this is not a vapour-cell
result and should not be cited as one. And the exact-compensation claim is
strong enough that it should be read in the original before this analysis leans on it.
a summary is not a derivation.

**Citekey correction.** This paper was carried as `bevilacqua2012` from the
literature audit onward. The volume, page, year and physics description were all
correct; the first author was not — there is no Bevilacqua among
Bruvelis, Ulmanis, Bezuglov, Miculis, Andreeva, Mahrov, Tretyakov and Ekers. The
old key is retired rather than aliased, so nothing can cite it by accident.
