---
citekey: weyers2018
type: article
authors:
  - Weyers, S.
  - and PTB fountain team
title: 'Advances in the accuracy, stability, and reliability of the PTB primary fountain clocks'
journal: Metrologia
volume: 55
pages: 789-805
year: 2018
doi: 10.1088/1681-7575/aae008
arxiv: null
pdf: PDF_papers/Weyers_2018_Metrologia_55_789.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Author list is TRUNCATED here to "Weyers, S. and PTB fountain team". The
    full list was not transcribed from the PDF; complete it before formal
    citation.'
  - 'Held for metrological PRACTICE only. Caesium microwave fountains (CSF1,
    CSF2) -- no physics input to this programme.'
verified_date: 2026-07-30
summary: >
  The companion practice anchor to gerginov2025, and it answers a different
  question: what to do when a systematic CANNOT be cleanly separated into
  statistical and systematic parts. PTB's rule is explicit -- because the
  processing of the collisional shift coefficients in CSF1 entangles statistical
  and systematic uncertainties, they attribute an overall collisional shift
  uncertainty to the systematic uncertainty budget. It also shows two levers
  this programme lacks: operating NEAR THE NULL of a systematic (CSF1 runs close
  to the parameters that cancel the collisional shift, so the shift stays below
  1e-15), and a CONTROLLED knob for the confounded variable (CSF2 varies atomic
  density by rapid adiabatic passage rather than by changing temperature). Plus
  external validation: a 1400 km optical-fibre comparison with LNE-SYRTE
  agreeing below 3e-16.
loci:
  - methods/03
  - M4c
section: method-anchors
---

# weyers2018

**Skimmed 2026-07-30** for metrological practice, at the experimenter's
direction, alongside [gerginov2025](gerginov2025.md). **Not read in full.**
Caesium microwave fountains; no physics input here.

## The rule for an inseparable systematic

The sentence worth carrying, verbatim: **"Because the processing of the
collisional shift coefficients in CSF1 entangles statistical and systematic
uncertainties, we attribute an overall collisional shift uncertainty to ...
the systematic uncertainty budget."** <!-- not-from-pdf: verbatim across a
page break; the "..." marks a running header ("Metrologia 55 (2018) 789
S Weyers et al 794") that the source PDF inlines at that exact point, not an
elision of the authors' text -->


That is a stated decision rule for a situation this programme is in. The
$\beta_{\rm self}$ determination has exactly this character: the collisional
term is not cleanly separable from the drift, and the archival bound sits
57–113× above the expected value precisely because the two are entangled. PTB's
answer is neither to force a separation nor to quote a statistical-only bar, but
to declare the entanglement and book the whole thing as systematic. **Paper 1's
$\beta_{\rm self}$ section should say what it does with the entangled part, in
those terms, and can cite a primary standard for the practice.**

## Two levers this campaign does not have, and both are instructive

**Operating at the null.** "Since the CSF1 operation parameters are close to the
parameters that cancel the collisional shift, the measured relative collisional
frequency shift is normally less than $10^{-15}$ and its uncertainty is a few
parts in $10^{16}$." Rather than measure a large systematic well, they arrange
for it to be small. The analogue worth asking about is whether any operating
point of the 5S–6S geometry makes a dominant term vanish — the magic-wavelength
work (M16) is the same instinct applied to the light shift.

**A controlled knob for the confounded variable.** "In CSF2 the density is varied
using rapid adiabatic passage (RAP) as the atoms traverse the state selection
cavity", with a full RAP pulse selecting all atoms. Density is therefore varied
*at fixed everything else*. This campaign has no such knob: its density lever is
cell temperature, which moves the thermal velocity with it — the same degeneracy
[lee2010](lee2010.md) turns out to have, and the reason the global fit must break
it by shape rather than by design. **Worth stating in the apparatus section as a
known limitation with a known solution**, since a state-selection or
optical-pumping density knob is the standard fix and this programme should say
it knows that.

## External validation, which is the other thing a primary standard does

"The first comparison of distant fountain clocks, at PTB and LNE-SYRTE ... via a
1400 km long optical fibre link showed very good agreement, below the
$3 \times 10^{-16}$ level for all of the participating fountain clocks, which is
compatible with their statistical and systematic uncertainties." An independent
instrument, in another country, agreeing inside the quoted bars. This
programme's nearest analogues are weaker: the recovered drift bound against the
photographed $\pm 0.19$ MHz/min, and the Cs polarizability triangle, which checks
the code rather than the measurement.
