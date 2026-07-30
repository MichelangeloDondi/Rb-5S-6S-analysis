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
  exponentially small in that regime. Held because it makes the proposed refit
  of Patterson's spectra tractable rather than a project.
loci:
  - P2
  - THEORY
section: method-anchors
---

# klimovducloy2004

**Held and skimmed 2026-07-30**, fetched at the experimenter's request. Lebedev
Physical Institute (Moscow) and Laboratoire de Physique des Lasers,
Université Paris-Nord. **Skimmed, not read in full** — the abstract, the
regime statements and the reference structure were checked; the derivations
were not.

## Why it is here

[sague2007](sague2007.md) builds its lineshape from a position-dependent decay
rate $\gamma(r) = \gamma_{\rm free}(r) + \gamma_{\rm guid}(r)$ and takes
$\gamma_{\rm free}(r)$ from this paper (their ref [14], verified against
Sagué's own bibliography). [patterson2018](patterson2018.md) uses the same
physical quantity as a detection weight and leaves it out of the width, which is
the candidate explanation for its unexplained 2 MHz. **This is the paper that
decides whether testing that is a day's work or a project.**

## What it provides, from the abstract

Spontaneous decay rates of an excited atom near a **dielectric cylinder**, with
"special attention paid to the case when the cylinder radius is small in
comparison with radiation wavelength (nanofiber or photonic wire)". In that
regime:

- "the **analytical expressions** of the transition rates for different
  orientations of dipole are derived";
- "the main contribution to decay rates is due to **quasistatic interaction** of
  atom dipole momentum with nanofiber and the contributions of guided modes are
  **exponentially small**";
- when the radius is only slightly less than the wavelength, guided modes can be
  substantial instead.

So for the 240 nm fibre of `patterson2018` at 780 nm — comfortably subwavelength
— there is a closed form, and the guided-mode part is negligible in
$\gamma_{\rm free}$. That is what makes the refit tractable.

**One caution the paper states itself:** the decay rate of a *radially* oriented
dipole "tends to infinity when cylinder radius tends to zero" for an ideally
conducting nanowire. Any refit has to handle the orientation average rather than
take a single dipole orientation, and the near-surface limit needs care.
Non-radiative losses inside the body are also discussed and are a separate term.

## What has not been done

The functional form has not been extracted, coded, or checked against Sagué's
57%-at-surface figure — which would be the natural first validation, since
Sagué computes exactly that number from this paper plus their own
$\gamma_{\rm guid}$. Doing so, then refitting Patterson's published spectra with
$\Gamma(r)$ inside $p_{\rm abs}$, is the falsification test recorded in
[patterson2018](patterson2018.md). **Recorded as OPEN.**
