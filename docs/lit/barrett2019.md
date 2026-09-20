---
citekey: barrett2019
type: misc
authors:
  - Barrett, M. D.
  - Arnold, K. J.
  - Safronova, M. S.
title: 'Polarizability assessments of ion-based optical clocks'
journal: arXiv preprint
year: 2019
doi: null
arxiv: '1905.04976'
pdf: PDF_papers/Barrett_2019_polarizability-assessments-ion-based-optical-clocks.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 (abstract, introduction, Table I and Fig. 1) read against the PDF on
    2026-09-20. No published journal version is named on either page, so the record carries the
    arXiv preprint (v2, 11 Oct 2019) as held. The rest of the paper (Appendix A and the discussion
    of Sr+ and Ca+) is not read.
verified_date: null
summary: >
  Proposes determining the dynamic differential scalar polarizability of the 138Ba+ clock
  transition to below 0.5 percent inaccuracy for wavelengths above 700 nm using only measurements
  that do not require an absolute laser-intensity calibration, by fixing three dominant transition
  poles and one weak quadratic background term. The species (a trapped Ba+ ion clock transition)
  and the physics (a blackbody-radiation-shift assessment) are different from a neutral-rubidium
  5S-6S programme. Its value here is the general pattern of a differential polarizability curve
  dominated by a few poles plus a slowly varying background, not any specific number.
section: deep-search
---
# barrett2019

## Values

| field | value | where in the paper |
|---|---|---|
| target inaccuracy on the differential polarizability | < 0.5% for lambda > 700 nm (138Ba+ S1/2-D5/2) | p. 1, abstract |
| dominant poles (S1/2 side) | 6p 2P1/2 at 493.5 nm, 6p 2P3/2 at 455.5 nm | p. 1-2, Table I |
| dominant pole (D5/2 side) | 6p 2P3/2 at 614.3 nm | p. 2, Table I |
| Table I total, 6s 2S1/2 | 113.14 a.u. | p. 2, Table I |
| Table I total, 5d 2D5/2 (J=3/2 channel) | 25.39 a.u. | p. 2, Table I |
| Table I total, 5d 2D5/2 (J=5/2 channel) | 0.725 a.u. | p. 2, Table I |
| Table I total, 5d 2D5/2 (J=7/2 channel) | 14.71 a.u. | p. 2, Table I |
| single-pole fit to the uv + core terms | c0 = 15.23 a.u., omega0 = 0.20479 a.u. (lambda0 = 222.49 nm) | p. 2 |
| max fractional discrepancy of that single-pole approximation | about 2 x 10^-5 over omega < 0.065 a.u. | p. 2 |
| zero crossing of the differential polarizability | omega ~ 0.07 a.u. (lambda ~ 653 nm) | p. 2, Fig. 1 |

## What it says, in its own terms

The paper targets the dynamic differential scalar polarizability of the S1/2-D5/2 clock
transition in 138Ba+, whose dc value sets the blackbody-radiation shift, a leading term in the
error budget of several ion clocks (Al+, Yb+, In+ and Lu+ are named). Existing determinations
either need the dc polarizability to be negative, which does not hold for every candidate ion, or
rely on near/mid-infrared measurements whose accuracy is capped by how well the laser intensity at
the ion is known -- limited to about 1% by detector calibration and further degraded by beam
aberration and etaloning.

Its proposed route avoids intensity calibration altogether. For 138Ba+, the differential
polarizability above 700 nm is dominated by three poles (614, 493 and 455 nm) plus ultraviolet
contributions from transitions below 240 nm. The uv part and a small valence-core correction term
are shown to be well approximated, to second order in frequency, by a single effective pole with a
weak quadratic form (their Eq. (1)-(2)). Table I tabulates the contributing matrix elements and
polarizability contributions computed with a linearized coupled-cluster method (the 6s-6p matrix
elements are taken from experiment instead). Fixing the three dominant poles from existing
measurements and locating the curve's zero crossing (near 653 nm) to fix the single quadratic term
is argued to reconstruct the whole curve to high accuracy without ever needing an absolute
intensity. The paper states the approach generalizes to 88Sr+ and 40Ca+, with the latter directly
relevant to Al+/Ca+ quantum-logic clocks.

## What it is worth here

138Ba+ is a trapped-ion clock transition, not neutral rubidium, and the physics being solved
(a blackbody-shift budget for optical clocks) is a different problem from a rubidium 5S-6S
lineshape and AC-Stark programme. Nothing here is a number such work would import. What is
transferable is the shape of the argument -- a differential polarizability written as a handful of
dominant poles plus one weak background term, calibrated without needing an absolute drive
intensity -- as a pattern worth having in mind when a differential-polarizability construction is
described, but not as an anchor or a cross-check value.
