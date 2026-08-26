---
citekey: lahad2019
type: article
authors:
  - Lahad, Ohr
  - Finkelstein, Ran
  - Davidson, Omri
  - Michel, Ohad
  - Poem, Eilon
  - Firstenberg, Ofer
title: 'Recovering the Homogeneous Absorption of Inhomogeneous Media'
journal: Phys. Rev. Lett.
volume: 123
pages: 173203
year: 2019
doi: 10.1103/PhysRevLett.123.173203
arxiv: '1904.06233'
pdf: PDF_papers/Lahad_2019_recovering-homogeneous-absorption-inhomogeneous-media.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'DOI and arXiv identity cross checked against the arXiv abstract page for
    1904.06233 (submitted 12 April 2019, revised 21 November 2019). The
    journal-ref given there is Phys. Rev. Lett. 123, 173203 (2019), matching
    the held PDF exactly on title, all six authors, and DOI.'
verified_date: 2026-08-03
summary: >
  A light-shift COMPENSATION scheme, not a distribution inversion, from the
  Firstenberg group at Weizmann. A second, correlated recovery field cancels
  the inhomogeneous light shift a coupling field induces on a two-photon
  transition, bringing the whole ensemble into resonance together. Measures
  enhancement of the absorption cross section over the inhomogeneous limit,
  4.8 +/- 0.4 in an N-type Rb vapor scheme and 4.6 +/- 0.3 in a ladder scheme
  through a Rydberg state.
loci: []
section: prior-art
---

# lahad2019

Held. DOI and arXiv identity confirmed against the arXiv abstract page for
1904.06233. Title, authors, and DOI match the held PDF, the published
Physical Review Letters version.

Lahad, Finkelstein (equal contribution), Davidson, Michel, Poem, and
Firstenberg, Department of Physics of Complex Systems, Weizmann Institute
of Science. Physical Review Letters 123, 173203 (2019), received 18 April
2019, published 25 October 2019.

## The system

A two-level transition with homogeneous half linewidth gamma,
inhomogeneously shifted by a Gaussian random detuning delta of standard
deviation sigma much larger than gamma, loses absorption amplitude by a
factor beta0 = sqrt(2/pi) sigma/gamma, the "inhomogeneous limit." For the
Rb D1 line at 50 C, gamma = 2.875 MHz against a Doppler sigma = 220 MHz,
beta0 is about 60. For silicon-vacancy centers in diamond, gamma about 50
MHz against a strain-broadened sigma about 5 GHz, beta0 is about 80.

A three-level Raman (two-photon) transition does not evade this limit even
though its bare linewidth is much narrower. A coupling field detuned by
Delta from the intermediate state shifts the final state by roughly
Omega^2/Delta, and because Delta itself carries the inhomogeneous spread
delta, that light shift becomes Omega^2/Delta + (Omega/Delta)^2 delta. The
two-photon resonance inherits an induced broadening (Omega/Delta)^2 sigma
on top of a homogeneous width that scales the same way, so the ratio
sigma/gamma, and beta0 with it, carries over unchanged.

The fix adds a fourth level. A second, far-detuned "recovery" field drives
a separate transition from the ground state and shifts it by
Omega_r^2/(Delta_r - delta_r). If delta and delta_r are correlated (both
linear in atomic velocity for copropagating beams, delta = kv and delta_r
= k_r v), tuning Omega_r and Delta_r to satisfy the compensation condition

    Omega^2/(Delta - delta) = Omega_r^2/(Delta_r - delta_r)

makes the ground and final state track the same shift for every atom, so
the two-photon resonance frequency becomes common to the whole ensemble
regardless of delta. The enhancement beta, the ratio of the two-photon
peak absorption to the one-photon peak absorption, is bounded above by
beta0 and given in the symmetric case (gamma = gamma_r, Omega = Omega_r)
by

    beta = beta0 * [gamma/(gamma+gamma_r)] * [mu^2/(1+mu^2)]

with a saturation parameter mu^2 that scales linearly with intensity.

## The numbers

Two hot 87Rb experiments test the mechanism. An N-type scheme in a 75 mm
natural-abundance cell at 33-42 C gives beta = 4.8 +/- 0.4, with Omega =
29 MHz, Omega_r = 29.6 MHz, Delta = -270 MHz, Delta_r = -300 MHz, a bare
two-photon width gamma_sg = 0.35 MHz, gamma = 2.875 MHz, gamma_r = 3.033
MHz, and a 375 um probe waist. A ladder scheme through a Rydberg state
(5S1/2 ground, 5P3/2 probed at 780 nm, 5D5/2 coupled at 776 nm, 31F7/2
driven by a 1270 nm recovery field), in a 5 mm isotopically pure cell,
gives beta = 4.6 +/- 0.3, with Omega = 55 MHz, Omega_r = 45 MHz on
resonance, gamma_sg about 1.25 MHz, gamma_r about 1 MHz, a residual
two-photon Doppler width sigma_2 = 1 MHz, and an 85 um probe waist. Both
results exceed the inhomogeneous limit by design and are matched by a
calculation with no free parameters once the extra hyperfine structure
and finite beam size are included.

An ideal far-detuned calculation puts the enhancement ceiling at beta0 *
gamma/(gamma+gamma_r), about 30 for beta0 = 60 and gamma about gamma_r.
The measured enhancement tops out near 5, limited by an extra excited
hyperfine level and nonuniform beam intensity rather than by the
mechanism itself.

## Validity

The mechanism is a compensation scheme, not a reconstruction of an
unknown distribution. The inhomogeneous width sigma is taken as given,
read from a known temperature or a known strain distribution, and the
recovery field is tuned in advance so that sigma and the correlated
sigma_r cancel. The measured observable is a single scalar, the
enhancement ratio beta between two peak heights, compared against a
closed-form expression or a parameter-free calculation, and there is no
inverse problem to regularize. The paper places the scheme alongside
earlier ensemble-wide suppression techniques: Cohen-Tannoudji, Hoffbeck
and Reynaud's 1978 proposal that a light shift can counteract Doppler
broadening, hole burning, Doppler-free methods, and spin echo, all of
which act on the whole ensemble without inferring anything from it.

## Use in this record

No quantity in this analysis is adopted from this paper. It is cited as
prior art for light-shift-based line narrowing, distinguished from the
distribution-reconstruction method used elsewhere for a two-photon
lineshape (see [delone1980](delone1980.md)): here the inhomogeneous width
is specified in advance and cancelled, and not inferred from an
observed profile.
