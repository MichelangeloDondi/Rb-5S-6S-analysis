---
citekey: wieman1987
type: article
authors:
  - Wieman, C. E.
  - Noecker, M. C.
  - Masterson, B. P.
  - Cooper, J.
title: 'Asymmetric line shapes for weak transitions in strong standing-wave fields'
journal: Phys. Rev. Lett.
volume: 58
pages: 1738
year: 1987
doi: 10.1103/PhysRevLett.58.1738
arxiv: null
pdf: null
held: false
status: REPORTED
routing:
  - CITE
verify_flags:
  - 'REPORTED, deliberately. The bibliographic record and the abstract were read
    from the publisher listing on 2026-07-30, and the physics below is taken
    from the introduction of stalnaker2006, which is held and read and which
    states that it "generalizes and extends the approach of Wieman et al." The
    paper ITSELF has not been read: it is 1987, predates arXiv, and APS returns
    403 without an institutional subscription. Upgrade to VERIFIED only after
    reading the full text -- the delineation in LITERATURE.md section 5 turns on
    what it does and does not do.'
verified_date: null
summary: >
  The foundational precedent for AC-Stark lineshape asymmetry: a weak transition
  (the forbidden 6S->7S M1 and Stark-induced line in Cs, from the JILA
  parity-violation programme) excited in an intense STANDING WAVE, whose spatial
  variation gives position- and velocity-dependent shifts and a Doppler-free,
  intensity-dependent distortion of the line, modelled with optical Bloch
  equations. Cited here as the work that owns "asymmetric lineshapes from a
  distributed AC-Stark shift" -- and, on the evidence available, as a
  ONE-PHOTON mechanism distinct from this programme's I-squared weighting.
loci:
  - THEORY
section: prior-art
---

# wieman1987

**REPORTED, 2026-07-30.** Abstract and bibliographic record read from the
publisher listing; the physics here is from the introduction of
[stalnaker2006](stalnaker2006.md), which is held, read, and describes itself as
generalising and extending this paper. The full text has not been read — PRL
1987 predates arXiv and APS returns 403 without a subscription. Everything below
is flagged accordingly, because the novelty delineation depends on it.

**What it did.** Excited a *very weak* atomic transition — the forbidden
6S → 7S magnetic-dipole and Stark-induced line in caesium, in the context of the
JILA parity-violation experiment — where an **atomic beam** crosses an intense
**standing-wave** laser field. The abstract reports "a dramatic
intensity-dependent distortion which is Doppler free and independent of the
excitation rate", and a line shape calculated from optical Bloch equations
"that include a spatially varying ac Stark shift", in good agreement with the
measurement. Stalnaker's account adds the mechanism: the standing wave's spatial
variation makes the shift **position- and velocity-dependent**, and that is what
produces the asymmetry and its sub-Doppler features.

**Why the concession to it stands.** `LITERATURE.md` §5 states that "asymmetric
lineshapes from distributed AC-Stark are new" is *not* claimable, and that is
right: a spatially varying AC-Stark shift distorting a line, measured and
modelled, is exactly this paper. Nothing in this programme's asymmetry work is
first in that general sense.

**Where it nevertheless differs, and the difference is sharp.** This is a
**one-photon** transition (M1 plus Stark-induced E1). This repository's
[THEORY_NOTE](../THEORY_NOTE.md) §2 derives the signal-weighted shift
distribution for a rate $\propto I^{n}$ as $f(s)\propto|s|^{n-1}$, and states of
the $n=1$ case — naming "a Stark-induced forbidden line", i.e. this one — that it
gives the **uniform** distribution with $\kappa_3 = 0$, *exactly zero skew*. So
the closed-form triangular ramp and its intrinsic $g_1 = +0.566$ cannot be
Wieman's mechanism: for a one-photon rate that skew vanishes identically. Their
asymmetry comes from the standing wave's node–antinode structure combined with
atomic velocity, worked through the Bloch equations; ours comes from the $I^2$
weighting of a two-photon rate over a transverse Gaussian, with the standing
wave shown *not* to move the mean at all (M19), because the Doppler-free rate
goes as $I_+I_-$ and is $z$-uniform.

Four further differences worth stating rather than assuming: atomic beam versus
hot vapour cell; a numerical Bloch treatment (which
[stalnaker2006](stalnaker2006.md) then generalised) versus a closed form with
analytic cumulants; a distribution over *position and velocity in a standing
wave* versus over *transverse intensity*; and — the one that matters for the
programme — the asymmetry treated as a **distortion to be understood and
removed**, which is explicit in the title of the descendant
[antypas2018](antypas2018.md), "Lineshape-asymmetry *elimination*", against this
work's use of it as the measurement channel.

**What must be checked in the full text before Paper 1's introduction is
written**, because each would change the delineation: whether they write the
shift distribution explicitly (and if so, in what variable); whether any moment
or asymmetry coefficient is quoted as a number rather than fitted numerically;
and whether the velocity dependence is separable from the spatial one. On the
present evidence the concession is correctly *general* and can be *narrowed* —
but narrowing it on an unread paper is exactly the error this repository has
been correcting elsewhere, so it is left conceded and flagged.
