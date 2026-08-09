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
pdf: PDF_papers/wieman1987.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: '2026-08-02'
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

**VERIFIED** from the full four-page PRL (58, 1738-1741, 27 April 1987).
Earlier readings here rested on the abstract plus
[stalnaker2006](stalnaker2006.md)'s account of it. The three questions the
delineation depended on are answered below from the primary text.

**Abstract, verbatim** (published 27 April 1987). "We have observed the resonance line shape
for a very weak atomic transition excited when an atomic beam intersects a strong
standing-wave laser field. The line shape has a dramatic intensity-dependent
distortion which is Doppler free and independent of the excitation rate. We have
calculated the line shape predicted by optical Bloch equations that include a
spatially varying ac Stark shift, and find good agreement with our experimental
results."

What the abstract does not contain, the full text does not contain either:
no shift distribution, no moment, no asymmetry coefficient. It calculates a
lineshape from Bloch equations and matches it to data.

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

Four further differences, each now confirmed against the full text: atomic beam
versus hot vapour cell; a **numerical** optical-Bloch treatment, solved
atom-by-atom and averaged numerically over standing-wave phase and transverse
velocity, versus a closed form with analytic cumulants; a distribution over
*longitudinal position and velocity in a standing wave* versus over *transverse
intensity*; and the one that matters for the programme, the asymmetry treated
as a **distortion to be understood and removed**, explicit in the title of the
descendant [antypas2018](antypas2018.md), "Lineshape-asymmetry *elimination*",
against this work's use of it as the measurement channel.

**The three questions this note carried, answered from the full text
(2026-08-02).**

1. *Is the shift distribution written explicitly, and in what variable?* No.
   The AC-Stark detuning enters as a phase, proportional to
   $\varepsilon^2\cos[kz(t)]$ with $z(t)=z_0+v_z t$, and the lineshape is
   obtained by solving the Bloch equations for one atom and averaging
   numerically over the initial standing-wave phase $z_0$ and the transverse
   velocity distribution. No probability density of the shift appears. The
   transverse profile is not integrated at all: the field is taken as constant
   over the distance an atom moves in one lifetime.
2. *Is any moment or asymmetry coefficient quoted as a number?* No. The only
   asymmetry measure is an operational ratio $D=d/h$, the wing-distortion
   amplitude over the undistorted peak height, read off and compared against
   numerical output. No mean, variance, or cumulant of a shift distribution is
   computed anywhere.
3. *Is the velocity dependence separable from the spatial one?* No, and
   deliberately. Both sit inside the same cosine phase through
   $z(t)=z_0+v_z t$. The paper's physical account is a fast-atom versus
   slow-atom dichotomy: atoms crossing many fringes per lifetime see the
   fringe-averaged field and give symmetric wings, while slow atoms sit at a
   frozen fringe and skew toward the local field maximum.

**What overlaps, and what does not.** What is
genuinely prior art is the general proposition, that a spatially inhomogeneous
AC-Stark shift averaged over an atom's trajectory distorts a line
asymmetrically, computed from first principles and matched to data with no free
parameters. That is conceded without reservation. What is confirmed absent is
the closed-form distribution, any cumulant, and the $I^2$ weighting: the
transition is single-photon throughout, magnetic-dipole plus Stark-induced E1,
so the $\varepsilon^2$ in its shift coefficient is the ordinary quadratic
field dependence every AC-Stark shift has, not a two-photon rate weighting.

**The paper's own priority claim.** It states that this is to their knowledge
the first observation of this type of line-shape distortion (p. 1738). That is
correct for the general phenomenon. It does not reach the closed-form power-law
distribution, the mean pull, or the third cumulant, none of which appear in the
paper in any form.

## What the abstract alone could not settle

One inference available from the abstract is that "a very weak transition"
implies a linear, single-photon response, which cannot produce the two-photon
triangle. That inference is **not safe on the abstract alone**, and nothing
here rests on it, for two reasons. First, the point was already conceded more
strictly elsewhere: the $I^k$ weighting for $k$-photon excitation is in
[delone1980](delone1980.md), so the $I^2$ weighting was never available as an
original claim. Second, a standing wave has its own geometric intensity
distribution, so whether the Bloch treatment amounts in effect to a
shift-distribution map is a question only the full text can decide. The reading
above decides it: the transition is single-photon throughout and no shift
distribution appears.
