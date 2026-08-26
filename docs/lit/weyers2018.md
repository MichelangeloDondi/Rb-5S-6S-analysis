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

Skimmed for metrological practice, alongside [gerginov2025](gerginov2025.md). Not read in full. Concerns caesium microwave fountain clocks (CSF1, CSF2). No physics input to this programme.

## The fountains

PTB operates two caesium fountain clocks, CSF1 and CSF2, and reports advances in their accuracy, stability, and reliability.

## The collisional shift uncertainty

For CSF1, processing the collisional shift coefficients entangles statistical and systematic uncertainties, so the overall collisional shift uncertainty is attributed entirely to the systematic uncertainty budget rather than split between the two.

## Operating near a null

CSF1 is operated close to the parameters that cancel the collisional shift. The measured relative collisional frequency shift is normally below $10^{-15}$, with an uncertainty of a few parts in $10^{16}$.

## The density knob (CSF2)

In CSF2, atomic density is varied by rapid adiabatic passage (RAP) as the atoms cross the state-selection cavity, with a full RAP pulse selecting all atoms. Density is varied while other parameters, including velocity, are held fixed.

## Comparison with LNE-SYRTE

A comparison of PTB's fountains with LNE-SYRTE over a 1400 km optical fibre link found agreement below $3 \times 10^{-16}$ for all participating clocks, compatible with their combined statistical and systematic uncertainties.

## Use in this record

No quantity from this paper enters the analysis. It is cited as a methodological precedent for treating an entangled systematic uncertainty as fully systematic, and for varying atomic density independently of velocity.
