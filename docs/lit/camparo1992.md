---
citekey: camparo1992
type: article
authors:
  - Camparo, J. C.
  - Lambropoulos, P.
title: 'ac Stark shift of a two-photon transition induced by a model stochastic field'
journal: J. Opt. Soc. Am. B
volume: 9
number: 12
pages: 2163
year: 1992
doi: null
arxiv: null
pdf: PDF_papers/Camparo_1992_two-photon-ac-Stark-shift-stochastic-field-asymmetric-lineshape.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-07-26
summary: >
  Monte-Carlo study of the ac Stark shift of a TWO-PHOTON transition in a
  stochastic field. Whether a distribution of shifts skews the line is set by
  ADIABATICITY: slow (adiabatic) intensity fluctuations give an asymmetric line
  whose peak moves sublinearly with intensity, while fast fluctuations average
  to a symmetric line at the mean shift. The line's first moment tracks the
  ensemble-average shift; its peak does not.
loci:
  - M19
  - THEORY
section: prior-art
---

# camparo1992

**Read in full 2026-07-26**, from the PDF supplied by the experimenter. This
replaces an abstract-level entry that carried the action "obtain the PDF" —
and the full text changes the reading in the programme's favour, while adding
one objection the abstract did not contain.

## What the abstract already gave

J. Opt. Soc. Am. B **9**(12), 2163 (1992), Camparo (Aerospace Corp.) and
Lambropoulos (USC), received 22 January 1992, revised 7 April 1992. Verbatim:
"In strong fields the fluctuating Stark shifts give rise to an **asymmetric
resonance line shape in a fashion analogous to inhomogeneous broadening**. The
line shape's peak position then has a **sublinear dependence** on the
stochastic field's intensity."

## What only the full text gives — and it is the important part

**The asymmetry is conditional on adiabaticity, and they say so explicitly.**
Their Fig. 5 contrasts the same two-photon resonance at Ω₀ = 0.03 and Ω₀ = 30.
The asymmetry appears in the adiabatic case, where the field's intensity varies
slowly compared with the atomic response; in the fast-fluctuation case the atom
samples the whole distribution within its response time and the line is
symmetric. Verbatim on the weak-field side: "In weak fields for which the line
shape is symmetric, the line shape peak and the first moment are equivalent.
Consequently, the observed ac Stark shift displays a **linear** dependence on
intensity."

Their explanation of the sublinearity is a moment argument: "If we consider
that the line shape's **first moment should always be proportional to the
average ac Stark shift** seen by the atoms... for the asymmetry to develop in
the strong-field regime, the line shape's first moment must be larger (in an
absolute-value sense) than the line shape's peak position."

## Why this is not a scoop, and where it does bite

Not a scoop, for the reason the earlier entry already gave and the full text
confirms: their distribution is over a **stochastic field in time**, ours over
**position in a structured beam**. Theirs is Monte Carlo over a model field's
coherence functions; ours is a closed form over a measured profile. Their
asymmetry needs the strong-field/adiabatic regime; ours arises in the weak,
unsaturated field purely from the I² weighting of a two-photon rate.

**Two things it does bite on.**

*First, it supplies a referee's objection to the ramp itself, and a sharp one.*
If a distribution of shifts only skews a line when it is sampled adiabatically,
then an atom **flying through** the beam — which sweeps its own shift from zero
to the on-axis maximum and back within a transit time comparable to 1/Γ — might
average the ramp away exactly as Camparo's fast fluctuations do. The composite
model convolves a static ramp with a transit lineshape as though the two were
independent, and this paper is the reason that cannot simply be asserted.
**Checked, and it survives: M19 (`rb5s6s/ramp_transit.py`)** propagates the
weak-excitation amplitude with the shift integrated along each trajectory, no
quasi-static step, and recovers the static triangle's first two moments to
~0.1% across S₀/transit-width from 0.09 to 7.6. The reason is a change of
variables — impact parameter and v·t *are* the transverse plane — so motion
re-labels which atom carries which shift without changing the distribution over
shifts. This paper is what prompted the check; cite it where the check is
reported.

*Second, their sublinearity does not threaten the ramp law here, and the
distinction is worth stating before a referee draws it the wrong way.* The
archival prediction is a pull **linear** in S₀ and hence in power. Camparo's
sublinear peak arises in the strong-field adiabatic regime through saturation
between intensity spikes; in the weak-field regime they report the linear
behaviour this programme predicts. Quote their own weak-field sentence rather
than arguing the point.

## The laser-noise caution, and the bound on it

Retained from the earlier reading: if field-amplitude noise alone can skew a
two-photon line, laser intensity noise is a candidate systematic for any
asymmetry measurement. M1 fits σ² = a² + b·V + c·V², where c is the
multiplicative (intensity-fluctuation) term. Across the 32 fitted conditions
the BIC selects c in **1**, and there its value is **negative** (−8.5e−4),
unphysical for a variance contribution and so a fitting artifact. No
multiplicative-noise signature in these data.

That remains evidence rather than proof, and the mismatch is the same one as
before: Camparo's mechanism is a fluctuating *shift* skewing the line, while c
bounds a fluctuating *amplitude* inflating the variance. What the full text
adds is a reason the gap may matter less here — their skew needs the
fluctuation to be slow compared with the atomic response.

## Audited against the PDF, 2026-07-30 — and it turned up a sentence this note
## should have carried

Every claim above checks out: the abstract quotation is verbatim, the
adiabaticity condition is theirs ($\Omega \gg 1/\tau_{\rm coh}$), the
first-moment statement is theirs ("the line shape's first moment should always
be proportional to the average ac Stark shift seen by the atoms"), and the
bibliographic record is right.

**What the note omitted, and it is the closest sentence in the holdings to this
programme's own thesis.** In their §3 they write that under adiabatic conditions

> the multiphoton transition line shape may be expected to act as a map of the
> probability distribution of Stark shifts,⁸ which will follow the asymmetric
> distribution of $(1+\epsilon)^2$.

That is *the lineshape maps the shift distribution*, stated in 1992, for a
**two-photon** transition, with an asymmetric distribution arising from an
intensity that enters quadratically. It is materially closer to the frame used here
than [wieman1987](wieman1987.md) (one-photon) or
[stalnaker2006](stalnaker2006.md) (one-photon, numerical), and the concession in
`LITERATURE.md` §5 should name it.

**What still separates the two, and it is not small.** Their distribution is over
**temporal** intensity fluctuations of a stochastic field — a chaotic multimode
laser, characterised by a coherence time — and the whole paper is a Monte-Carlo
study of when those fluctuations are adiabatic enough to inhomogeneously
broaden. This programme's distribution is over the **spatial** transverse
intensity profile of a coherent beam, is quasistatic by construction rather than
by a $\Omega\tau_{\rm coh}$ criterion, and closes in analytic form with
cumulants. The $(1+\epsilon)^2$ they name is the field's own fluctuation
statistics, not $f(s)\propto|s|^{n-1}$.

**A lead not followed.** They attribute the mapping idea itself to their ref [8],
N. B. Delone, V. A. Kovarskii, A. V. Massalov & N. F. Perel'man, "An atom in the
radiation field of a multifrequency laser", *Sov. Phys. Usp.* **23**, 472 (1980).
If the mapping statement is to be attributed correctly, that review is where it
comes from and it predates everything else in this section. **Not held, not
read.** Worth one search before the introduction here is written.

