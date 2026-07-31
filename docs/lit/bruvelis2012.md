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
pdf: PDF_papers/Bruvelis_2012_transit-time-broadening-two-photon-ladder.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'HELD AND READ 2026-07-31, supplied by the experimenter. The exact-
    compensation claim in the abstract is confirmed verbatim. But reading the
    paper WEAKENED the transfer to this programme rather than strengthening it,
    reversing what this note previously said -- see the body. Their geometry is
    a CYLINDRICAL-lens sheet crossed by a collimated supersonic beam, and the
    paper states in its own words that the Voigt profile forms by a DIFFERENT
    mechanism in a thermal gas.'
  - 'CITEKEY CORRECTION: this repository cited the paper as `bevilacqua2012`
    until 2026-07-30. There is no Bevilacqua among the authors. The volume, page
    and year were right and the physics description was right; only the
    attribution was wrong, so a manuscript built on the old key would have
    carried a citation to a person who did not write it.'
  - 'The measured system is a supersonic beam of Na2 MOLECULES, not an alkali
    vapour. The result is derived for a general three-level ladder and the
    transfer is on the geometry, not on the species -- but the note must not be
    read as a vapour-cell measurement.'
verified_date: 2026-07-31
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

**Read 2026-07-31, and it weakens the transfer rather than strengthening it.**
This note previously argued from the abstract that the geometry is "the same
class as this programme's, not merely a general ladder result, which
strengthens the transfer considerably". The excitation scheme is indeed the
same class, Doppler-free and counterpropagating through a virtual intermediate
level. The geometry is not.

Their laser is focused by a **cylindrical lens** into a sheet, with measured
waists of 26.1 and 86 µm along one axis and about 1 cm along the other, and it
is crossed at right angles by a **collimated supersonic beam of Na₂ molecules**
at 1340 m/s with a 260 m/s spread. This campaign focuses a circular beam into an
isotropic thermal vapour. The compensation they derive is between wavefront
curvature along a single particle path and the transit time of particles farther
off axis, which is a statement about that crossed-beam arrangement.

The paper makes the distinction itself, which is what settles it:

> "mechanisms of the formation of Voigt profile … in the case of collimated
> beams and in the case of thermal gases are different. In the former case all
> molecules have nearly the same velocity, and the Voigt profile results from
> Gaussian switching of coupling between the molecules and the laser field,
> while in the latter case it results from the Maxwell velocity distribution"

So both geometries give a Voigt profile and they arrive at it by different
routes. Citing this paper as external support for a thermal-vapour transit
kernel would be citing the right conclusion from the wrong mechanism.

What does survive: the analytical model is validated twice, against
density-matrix numerics and against experiment, so the compensation result is
not resting on analytics alone. It is a clean statement that in a crossed-beam
geometry the divergence does not add an independent width.

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
