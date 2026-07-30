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
authoritative for the DOI; abstract from the publisher listing. Not held and not
read in full — APS returns 403 without a subscription.

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
This repository has been asserting the transit-Voigt form from
[biraben1979](biraben1979.md) and [lehmann2021](lehmann2021.md); this is the
paper that says the curvature term cancels rather than being neglected.

**Two things to hold onto rather than assume.** The measurement is a collimated
supersonic beam of **Na₂ molecules**, not a hot alkali vapour — the derivation is
for a general ladder and the transfer is geometric, but this is not a vapour-cell
result and should not be cited as one. And the exact-compensation claim is
strong enough that it should be read in the original before Paper 1 leans on it;
a summary is not a derivation.

**Citekey correction.** This paper was carried as `bevilacqua2012` from the
literature audit onward. The volume, page, year and physics description were all
correct; the first author was not — there is no Bevilacqua among
Bruvelis, Ulmanis, Bezuglov, Miculis, Andreeva, Mahrov, Tretyakov and Ekers. The
old key is retired rather than aliased, so nothing can cite it by accident.
