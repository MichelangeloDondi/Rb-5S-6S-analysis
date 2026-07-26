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
pdf: null
held: false
status: VERIFIED
routing: []
verify_flags:
  - 'ABSTRACT + INTRODUCTION ONLY, supplied by the experimenter 2026-07-26 (RG record). Identifier confirmed from the article header; DOI not located. Do not attribute beyond the abstract.'
verified_date: 2026-07-26
summary: >
  Monte-Carlo study of the ac Stark shift of a TWO-PHOTON transition in a
  stochastic field. In strong fields the fluctuating Stark shifts produce an
  asymmetric line shape "in a fashion analogous to inhomogeneous broadening",
  with a sublinear dependence of peak position on intensity.
loci: []
section: prior-art
---

# camparo1992

**Identifier confirmed 2026-07-26** from the article header supplied by the
experimenter: J. Opt. Soc. Am. B **9**(12), 2163 (1992), Camparo (Aerospace
Corp.) and Lambropoulos (USC), received 22 January 1992. The external audit
named this as a third precedent without a verified reference; it is real.

**The relevant sentence, verbatim from the abstract:** "In strong fields the
fluctuating Stark shifts give rise to an **asymmetric resonance line shape in a
fashion analogous to inhomogeneous broadening**. The line shape's peak position
then has a **sublinear dependence** on the stochastic field's intensity."

**Where it sits relative to this programme -- and the difference is the point.**
It is a two-photon transition whose ac Stark shift distribution produces an
asymmetric line, so at that level of description it belongs with wall2014 and
slepkov2010. But the distribution here is over a **stochastic field in time**
(amplitude and frequency fluctuations of a model laser field, treated by Monte
Carlo), not over **position in an inhomogeneous beam**. The mechanism, the
independent variable, and the experimental control are all different: their
asymmetry is set by the field's higher-order coherence functions, ours by the
spatial intensity profile and the I^2 weighting.

Two consequences worth carrying:

- **Cite it, but do not conflate it.** It is a genuine precedent for
  "shift distribution -> asymmetric two-photon line", and a referee who knows
  the light-shift literature will know it. Stating the distinction first is
  cheaper than having it raised.
- **It is also a caution about our own laser.** If field-amplitude noise alone
  can skew a two-photon line sublinearly in intensity, then laser intensity
  noise is a candidate systematic for any asymmetry measurement -- adjacent to,
  but distinct from, the shot-noise skew already identified in C3c. Worth a
  look before the ramp asymmetry is ever claimed as a detection.

**A partial, honest bound on that caution, from the archive's own noise model.**
M1 fits sigma^2 = a^2 + b*V + c*V^2, where the c term is multiplicative noise —
variance proportional to signal squared, which is what large relative intensity
fluctuations would produce. Across the 32 fitted conditions the BIC selects the
c term in **1**, and there its fitted value is **negative** (-8.5e-4), which is
unphysical for a variance contribution and marks it as a fitting artifact
rather than a detection. So there is no multiplicative-noise signature in these
data.

That is evidence, not proof, and the distinction matters: Camparo's mechanism
is a fluctuating *shift* skewing the line, whereas c bounds a fluctuating
*amplitude* inflating the variance. A laser with large intensity fluctuations
should show both, so the absence of one argues against the other — weakly.

**ACTION: obtain the PDF.** Whether the shift-skew mechanism is bounded at the
level this archive needs cannot be judged from an abstract, and the C3c
asymmetry work is where it would bite.
