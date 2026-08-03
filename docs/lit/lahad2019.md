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

**Read here 2026-08-03, in full.** Identification: Ohr Lahad and Ran
Finkelstein contributed equally, with Omri Davidson, Ohad Michel, Eilon Poem
and Ofer Firstenberg, Department of Physics of Complex Systems, Weizmann
Institute of Science. Physical Review Letters 123, 173203 (2019), received
18 April 2019, published 25 October 2019, DOI 10.1103/PhysRevLett.123.173203.
This is the published version of arXiv 1904.06233.

**Abstract, verbatim.** "The resonant absorption of light by an ensemble of
absorbers decreases when the resonance is inhomogeneously broadened.
Recovering the lost absorption cross section is of great importance for
various applications of light-matter interactions, particularly in quantum
optics, but no recovery mechanism has yet been identified and successfully
demonstrated. Here, we formulate the limit set by the inhomogeneity on the
absorption, and present a mechanism able to circumvent this limit and fully
recover the homogeneous absorption of the ensemble. We experimentally study
this mechanism using two different level schemes in atomic vapors and
demonstrate up to fivefold enhancement of the absorption above the
inhomogeneous limit. Our scheme relies on light shifts induced by auxiliary
fields and is thus applicable to various physical systems and inhomogeneity
mechanisms."

## What it does

A two-level transition with homogeneous half linewidth gamma, inhomogeneously
shifted by a Gaussian random detuning delta of standard deviation sigma much
larger than gamma, loses absorption amplitude by a factor beta0 = sqrt(2/pi)
sigma/gamma, their "inhomogeneous limit." Worked examples in the paper: the
Rb D1 line at 50 C, gamma = 2.875 MHz against a Doppler sigma = 220 MHz,
beta0 is about 60. Silicon-vacancy centers in diamond, gamma about 50 MHz
against a strain-broadened sigma about 5 GHz, beta0 is about 80.

The paper's first result is that a three-level Raman (two-photon) transition
does not evade this limit even though its bare linewidth is much narrower.
A coupling field detuned by Delta from the intermediate state shifts the
final state by roughly Omega squared over Delta, and because Delta itself
carries the inhomogeneous spread delta, that light shift becomes
Omega^2/Delta + (Omega/Delta)^2 delta. The two-photon resonance inherits an
induced broadening (Omega/Delta)^2 sigma on top of a homogeneous width that
scales the same way, so the ratio sigma/gamma, and therefore beta0, carries
over unchanged.

The fix is a fourth level. A second, far detuned "recovery" field drives a
separate transition from the ground state and shifts it by Omega_r^2 over
(Delta_r minus delta_r). If delta and delta_r are correlated, both linear in
atomic velocity for copropagating beams since delta = kv and delta_r =
k_r v, then tuning Omega_r and Delta_r to satisfy their compensation
condition Omega^2/(Delta - delta) = Omega_r^2/(Delta_r - delta_r) makes the
ground and final state track the same shift for every atom, so the
two-photon resonance frequency becomes common to the whole ensemble
regardless of delta. The enhancement beta, defined as the ratio of the
two-photon peak absorption to the one-photon peak absorption, is bounded
above by beta0 and given in the symmetric case (gamma equal to gamma_r,
Omega equal to Omega_r) by beta = beta0 [gamma/(gamma+gamma_r)]
[mu^2/(1+mu^2)], with a saturation parameter mu^2 that scales linearly with
intensity.

Two hot 87Rb experiments demonstrate it. An N-type scheme in a 75 mm natural
abundance cell at 33 to 42 C measures beta = 4.8 +/- 0.4. A ladder scheme
through a Rydberg state, in a 5 mm isotopically pure cell, measures beta =
4.6 +/- 0.3. Both exceed the inhomogeneous limit by design, and both are
matched by a full calculation with no free parameters once the extra
hyperfine structure and finite beam size are included.

## Key numbers

- beta0 = sqrt(2/pi) sigma/gamma, the inhomogeneous amplitude loss factor.
- Rb D1 worked example: gamma = 2.875 MHz, sigma(50 C) = 220 MHz, beta0
  about 60.
- Silicon-vacancy diamond example: gamma about 50 MHz, sigma about 5 GHz,
  beta0 about 80.
- Compensation condition, their Eq. (1): Omega^2/(Delta - delta) =
  Omega_r^2/(Delta_r - delta_r).
- Enhancement, their Eq. (2), symmetric case: beta = beta0
  [gamma/(gamma+gamma_r)] [mu^2/(1+mu^2)].
- N-type measurement: beta = 4.8 +/- 0.4, Omega = 29, Omega_r = 29.6 MHz,
  Delta = -270 MHz, Delta_r = -300 MHz, bare two-photon width gamma_sg =
  0.35 MHz, gamma = 2.875 MHz, gamma_r = 3.033 MHz, probe waist 375 um.
- Ladder Rydberg measurement: beta = 4.6 +/- 0.3, Omega = 55, Omega_r = 45
  MHz on resonance, gamma_sg about 1.25 MHz, gamma_r about 1 MHz, residual
  two-photon Doppler width sigma_2 = 1 MHz, probe waist 85 um.
- Ladder level scheme: 5S1/2 ground, 5P3/2 probed at 780 nm, 5D5/2 coupled
  at 776 nm, and a 31F7/2 Rydberg state driven by the 1270 nm recovery field.
- Ideal far detuned calculation: enhancement saturates at beta0
  gamma/(gamma+gamma_r), about 30 for beta0 = 60 and gamma about gamma_r.
  The real experiment tops out near beta = 5, limited by an extra excited
  hyperfine level and nonuniform beam intensity, not by the mechanism.

## BRIDGES: what this paper actually inverts, and where it sits in the lineage

**Nothing is inverted here.** This repository reads a light-shift
DISTRIBUTION f(s) from a two-photon lineshape, the Delone 1980 reduction
recorded in [delone1980](delone1980.md). This paper's title, "recovering
the homogeneous absorption," reads like the same operation on first sight,
but the mechanism is not a reconstruction of anything. Its random variable
delta is a Doppler shift whose width sigma is taken as GIVEN, read off a
known temperature or a known crystal strain distribution, never extracted
from an observed lineshape. Its measured observable is a single scalar, the
enhancement ratio beta between two peak heights, compared point by point
against a closed form formula or a parameter free calculation. There is no
regularisation anywhere in the paper because there is no ill posed inverse
problem to regularise. The task solved is a forward design problem, choose
Omega_r and Delta_r so that an already known sigma and sigma_r cancel, which
is the opposite operation from reading an unknown distribution off data.

This corrects an earlier, second hand characterization of this paper inside
this repository's own literature reconnaissance (private/claude_literature.md,
its Hunt 2), which filed it as "a light-shift-based scheme to invert an
inhomogeneous frequency distribution... a modern forward-analogue of the
Delone-Krainov map." That description was drawn from the title rather than
from the mechanism, and does not survive a full reading. It is the second
instance inside this repository of the same failure mode documented in
[hummer2021](hummer2021.md)'s verify_flags, a reconnaissance summary that
turned out wrong only once the source itself was opened.

**What does survive as kinship, and it is narrow.** Both this paper and this
repository's construction start from the same first order light-shift
identity, a light shift proportional to intensity or detuning, linearised
against whatever variable the ensemble is spread over. Lahad's version is
Omega^2/Delta plus (Omega/Delta)^2 delta, this repository's is a light shift
linear in a spatially varying intensity. That identity is already Delone's
Eq. (4.5), the lineshape as a rescaled copy of the underlying spread, so
neither paper originates it. Past that point the two programmes diverge.
Delone's F^k weighting for a k-photon transition, this repository's
|s|^(n-1) closed form family, and the third cumulant used as a drift immune
channel have no counterpart here: Lahad never integrates a distribution
against an intensity weight to predict a lineshape, characterizes the
spread by one moment only (the Gaussian standard deviation sigma), and never
needs a closed form family because delta is never reconstructed, only
cancelled.

**Where it belongs instead.** The paper's own introduction places it beside
Cohen-Tannoudji, Hoffbeck and Reynaud's 1978 proposal that a light shift can
counteract Doppler broadening, next to hole burning, Doppler-free methods
and spin echo, all suppression techniques that engage the whole ensemble
without reading anything off it. That is a different lineage from delone1980,
Efimov and Khitrov 1979, and Prokopeva and Kildishev 2025, which all read an
unknown distribution off a measured profile. [delone1980](delone1980.md) is
updated to say so explicitly: this paper is not a member of that family, and
is recorded here only as a checked and corrected identification rather than
an added one.

**One thing from the reconnaissance survives.** Its opening paragraph is
citable on its own, separate from the inversion question. Verbatim: "Inhomogeneous
broadening of spectral lines is a prevalent limiting factor in experiments and
applications involving light-matter interactions in ensembles. This common
impediment occurs for various atomic and atomlike absorbers, including quantum
dots, diamond color centers, rare-earth ions in crystals, hot atoms, and
particularly with Rydberg excitations. The broadening originates from a
distribution of resonant frequencies of the individual absorbers." Excluded
from the inversion family on method, but this introduction is citable for its
cross-platform framing of inhomogeneous broadening as a distribution of
resonant frequencies.
