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

Held. The abstract quotation, the adiabaticity condition, the first-moment
argument, and Section 3's lineshape-mapping statement are all verified against
the PDF.

## The system

A Monte Carlo study of the ac Stark shift of a two-photon transition driven by
a model stochastic (multimode, chaotic) field. J. Opt. Soc. Am. B **9**(12),
2163 (1992). Received 22 January 1992, revised 7 April 1992.

## The result

Abstract: "In strong fields the fluctuating Stark shifts give rise to an
asymmetric resonance line shape in a fashion analogous to inhomogeneous
broadening. The line shape's peak position then has a sublinear dependence on
the stochastic field's intensity."

The asymmetry is conditional on adiabaticity. Figure 5 contrasts the same
two-photon resonance at Ω₀ = 0.03 and Ω₀ = 30: the asymmetric line appears
when the field's intensity varies slowly compared with the atomic response
(Ω ≫ 1/τ_coh). When fluctuations are fast, the atom samples the whole
intensity distribution within its response time and the line stays symmetric.
In the weak-field, symmetric regime, "the line shape peak and the first
moment are equivalent. Consequently, the observed ac Stark shift displays a
linear dependence on intensity." The sublinear peak in the strong-field regime
follows from a moment argument: "the line shape's first moment should always
be proportional to the average ac Stark shift seen by the atoms ... for the
asymmetry to develop in the strong-field regime, the line shape's first
moment must be larger (in an absolute-value sense) than the line shape's peak
position."

Section 3 states the general principle: under adiabatic conditions "the
multiphoton transition line shape may be expected to act as a map of the
probability distribution of Stark shifts, which will follow the asymmetric
distribution of $(1+\epsilon)^2$." The idea is attributed there to Delone,
Kovarskii, Masalov and Perel'man, "An atom in the radiation field of a
multifrequency laser," Sov. Phys. Usp. 23, 472 (1980). The treatment concerns
a two-photon transition, closer to the process considered here than the
one-photon treatments in [wieman1987](wieman1987.md) or the one-photon
numerical treatment in [stalnaker2006](stalnaker2006.md).

## Validity

The distribution being mapped is over time: a stochastic field with a
coherence time, evaluated by Monte Carlo over the field's coherence
functions. The asymmetric line requires the strong-field, adiabatic regime.
In the weak field the observed shift is linear in intensity. This differs
from a distribution over position in a spatially structured beam, evaluated
in closed form from a measured intensity profile, where an asymmetric
two-photon line can arise from the $I^2$ weighting of the transition rate
without strong-field saturation.

## Use in this record

The transit-averaged Stark ramp used elsewhere in this record convolves a
static ramp with a transit lineshape. Propagating the weak-excitation
amplitude with the Stark shift integrated along each atomic trajectory, with
no quasi-static step, reproduces the static triangle's first two moments to
about 0.1% across $S_0$/transit-width from 0.09 to 7.6. Impact parameter and
$v\cdot t$ parametrize the same transverse plane, so motion relabels which
atom carries which shift without changing the distribution over shifts.
Separately, a multiplicative (intensity-fluctuation) variance term $c$ in
$\sigma^2 = a^2 + bV + cV^2$, fitted across 32 conditions, is selected by BIC
in only one of them and there takes a negative, unphysical value
($-8.5\times10^{-4}$). The data show no multiplicative-noise signature of the
kind a fluctuating-shift mechanism would produce, although the correspondence
is inexact, since this paper's mechanism is a fluctuating shift skewing the
line while $c$ bounds a fluctuating amplitude inflating its variance.
