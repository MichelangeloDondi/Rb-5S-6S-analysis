---
citekey: gerginov2025
type: article
authors:
  - Gerginov, V.
  - and NIST-F4 team
title: 'Accuracy evaluation of primary frequency standard NIST-F4'
journal: Metrologia
volume: 62
pages: 035002
year: 2025
doi: 10.1088/1681-7575/adbf99
arxiv: null
pdf: PDF_papers/Gerginov_2025_Metrologia_62_035002.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Author list is TRUNCATED here to "Gerginov, V. and NIST-F4 team" -- the full
    list was not transcribed from the PDF. Complete it before any formal
    citation.'
  - 'The DOI is the standard IOP record for Metrologia 62 035002 and was NOT
    checked against Crossref.'
  - 'NOT a Rb two-photon paper and NOT the Gerginov 2018 row in bandi2025 Table 1
    -- that is a different, earlier paper on a Rb two-photon optical clock. This
    one is a caesium MICROWAVE FOUNTAIN. Held for metrological PRACTICE only; no
    number in it is a physics input to this programme.'
verified_date: 2026-07-30
summary: >
  Held for how it PRESENTS an uncertainty budget, not for its physics. The
  accuracy evaluation of a caesium fountain primary frequency standard: Table 2
  lists every systematic with BOTH a correction and a type-B uncertainty
  (total 3019.5 +- 2.2, in units of 1e-16), including the terms whose correction
  is exactly zero, uses asymmetric error bars where the physics is asymmetric,
  and footnotes explicitly which entries are shown "for information only" to
  prevent double-counting. Its light-shift entry, 0 +- 0.01, is bounded by a
  technique worth copying: measure the effect AMPLIFIED where it is large
  (49(1.5)e-15 with the shutters open), then scale by a calibrated 40 dB
  attenuation to assign an upper limit of 1.0e-18.
loci:
  - methods/03
section: method-anchors
---

# gerginov2025

**Skimmed 2026-07-30** for metrological practice, at the experimenter's
direction. **Not read in full**, and deliberately not mined for physics: this is
a caesium *microwave* fountain, and nothing in it bears on Rb two-photon
lineshapes, nanofibres, or the polarizabilities this programme computes. What it
offers is a worked example of how a primary standard states what it does not
know.

*A misidentification to record.* This was first taken here for the "Gerginov
2018" row of [bandi2025](bandi2025.md)'s Table 1. It is not — that is a separate,
earlier paper on a Rb two-photon optical clock, and it remains unheld.

## The four practices worth copying

**1. Every systematic gets a correction *and* an uncertainty, including the
zeros.** Their Table 2 runs relativistic shifts, quadratic Zeeman, blackbody,
cold collisions, microwave lensing, distributed cavity phase (split by azimuthal
order $m = 0, 1, 2$), microwave modulation and spurs, microwave leakage, cavity
pulling, Rabi and Ramsey pulling, Majorana transitions, background-gas
collisions, and AC Stark — to a total of $3019.5 \pm 2.2$ in units of
$10^{-16}$. Seven of those entries have a correction of exactly **0**, and they
are listed anyway with their uncertainties. **A term considered and found
negligible is reported, not omitted.** That is the opposite of the usual habit,
and it is what makes a budget auditable: a reader can tell the difference
between "we bounded it and it is small" and "we did not think of it".

**2. Asymmetric uncertainties where the physics is asymmetric.** Microwave
lensing is $0.9\ (^{+0.2}_{-0.4})$; DCP $(m=0)$ is $0.05\ (^{+0.02}_{-0.08})$.
They do not symmetrise for tidiness.

**3. An explicit anti-double-counting note.** The X- and Y-tilt-axis entries
carry a footnote: the shifts and uncertainties along those axes "are given for
information only, as they are included in quadrature in the DCP $(m = 1)$ term".
Diagnostic decompositions are shown *and* flagged as already counted.

**4. Bounding a systematic by amplification, which is the one to steal.** Their
AC Stark (light) entry is $0 \pm 0.01$, and it is not a guess. They measure the
light shift in a deliberately *amplified* configuration — shutters open, where it
is $49(1.5) \times 10^{-15}$ and comfortably measurable — then attenuate by a
calibrated 40 dB (two mechanical shutters per fibre input, for redundancy, each
at least 40 dB) and assign the scaled residual, $\approx 5 \times 10^{-19}$,
rounded up to an upper limit of $1.0 \times 10^{-18}$.

**Why that last one matters here.** This programme's AC-Stark shift is confounded
with frequency drift at operating power — that confound is what forced the M20
retraction and what makes the centre channel unusable. The fountain answer is not
a better drift model: it is to measure the systematic where it *dominates*, in a
configuration built to amplify it, and then transfer the bound through a
calibrated attenuation. The analogue would be a deliberately over-powered or
tightly-focused configuration in which $S_0$ is large enough to measure against
the drift, with the operating-point bound obtained by scaling. **Not proposed as
a shot-list item here — recorded as a method this repository does not currently
use.**

## What is not transferable

The blackbody section is a Stark shift of the caesium *hyperfine* clock
transition — $\Delta f_{\rm BBR}/\nu_0 = k_0 E_{300}^2/\nu_0 \cdot (T/T_0)^4
[1 + \epsilon (T/T_0)^2]$ with $E_{300} = 831.9$ V/m — and the 0.2 K temperature
uncertainty propagates to $0.6 \times 10^{-16}$. That is a differential
polarizability known to great precision, but it is the microwave one, not the
$6s \to 7s$ optical differential in the Cs validation triangle
([quirk2024](quirk2024.md), [iskrenovatchoukova2007](iskrenovatchoukova2007.md)).
**Different quantity; not a target.**
