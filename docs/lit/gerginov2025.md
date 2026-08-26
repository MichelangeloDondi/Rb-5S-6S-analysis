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

Held. Read for its uncertainty-budget structure rather than its physics. It
reports a caesium microwave fountain, distinct from gerginov2018, an earlier
two-photon Rb optical clock paper by the same lead author. No quantity here
is a physics input to Rb two-photon lineshapes, nanofibres, or
polarizabilities.

## The uncertainty budget

Table 2 lists every systematic with both a correction and a type-B
uncertainty, totalling $3019.5 \pm 2.2$ in units of $10^{-16}$: relativistic
shifts, quadratic Zeeman, blackbody, cold collisions, microwave lensing,
distributed cavity phase (split by azimuthal order $m = 0, 1, 2$), microwave
modulation and spurs, microwave leakage, cavity pulling, Rabi and Ramsey
pulling, Majorana transitions, background-gas collisions, and AC Stark.
Seven of those entries have a correction of exactly 0, and are listed anyway
with their uncertainties.

Uncertainties are asymmetric where the physics is asymmetric. Microwave
lensing is $0.9\ (^{+0.2}_{-0.4}) $. Distributed cavity phase ($m=0$) is
$0.05\ (^{+0.02}_{-0.08}) $.

The X- and Y-tilt-axis entries carry a footnote stating the shifts and
uncertainties along those axes "are given for information only, as they are
included in quadrature in the DCP $(m = 1)$ term."

The AC Stark (light) entry is $0 \pm 0.01$. It is measured in a deliberately
amplified configuration, shutters open, where it is $49(1.5) \times 10^{-15}$
and readily measurable, then attenuated by a calibrated 40 dB (two mechanical
shutters per fibre input, each at least 40 dB, for redundancy) to a scaled
residual of about $5 \times 10^{-19}$, rounded up to an upper limit of
$1.0 \times 10^{-18}$.

## Validity

The blackbody term is a Stark shift of the caesium hyperfine clock
transition, $\Delta f_{\rm BBR}/\nu_0 = k_0 E_{300}^2/\nu_0 \cdot (T/T_0)^4 [1 + \epsilon (T/T_0)^2]$ with $E_{300} = 831.9$ V/m, where a 0.2 K
temperature uncertainty propagates to $0.6 \times 10^{-16}$. This is the
microwave hyperfine differential polarizability, not the $6s \to 7s$ optical
differential relevant to the caesium validation triangle (quirk2024,
iskrenovatchoukova2007). It is a different quantity.
