---
citekey: achar2025
type: article
authors:
  - Achar, Sumit
  - Sinha, Shivam
  - Ezhilarasan, M.
  - Chandankumar, R.
  - Sharma, Arijit
title: 'Determination of atomic number density in MEMS vapor cells via single-pass absorption spectroscopy (SPAS)'
journal: arXiv
volume: null
number: null
pages: '2511.00526'
year: 2025
doi: null
arxiv: 2511.00526
pdf: PDF_papers/Achar_2025_Rb-number-density-MEMS-cells-single-pass-absorption.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'the arXiv v4 of 14 July 2026 is the copy held, no journal record is cited'
verified_date: 2026-09-13
summary: >
  Rb number densities extracted from absolute single-pass absorption on the
  D2 and 420 nm lines in microfabricated cells over 293 to 353 K, with a
  density-matrix model carrying optical pumping, Doppler and transit
  broadening, compared with the Alcock-Itkin-Horrigan vapour-pressure
  relation and found to follow it closely, at a stated 2 per cent systematic
  per point. Held as the recent support for the Alcock form, the law the
  self-broadening anchor's pressure axis is on.
loci: []
section: method-anchors
---
# achar2025

Held, the arXiv v4, checked against the PDF for the passages quoted.

## What it covers

A validated method for the Rb number density in chip-scale cells from
single-pass absorption on the D2 line at 780.24 nm and the 5S to 6P line at
420.29 nm, with a Lindblad-form model that, verbatim from the abstract,
"explicitly accounts for optical pumping, Doppler broadening, and
transit-time broadening effects and exhibits quantitative agreement (> 99%)
with experimental spectra over a broad range of temperatures (293-353 K)".

## The vapour-pressure relation and the comparison

The paper states the relation it compares to: "The standard expression for
the temperature-dependent vapor pressure Pvap (T ) was first proposed by
Killian [21] and later refined by Alcock, Itkin, and Horrigan [20]", with the
liquid coefficients a = 4.312 and b = 4040 in log10 P/torr = 2.881 + a - b/T.
Its reading of the comparison, verbatim: "For both probe wavelengths, the
extracted number densities follow the empirical vaporpressure relation
closely over the entire temperature range", with the qualification that a
few points deviate by about their own uncertainties.
The per-point systematic budget at 333 K (its Table 2) totals 2.0 per cent,
dominated by the baseline normalisation (1.7 per cent) with the temperature
at 0.3 K contributing 0.01 per cent, so the comparison's own thermometry is
not what limits it.

## What this record takes from it

The Alcock form is supported at the few per cent level up to 80 C, the top
of this paper's range and ten degrees below the archive's lowest set point.
Siddons 2008 supports Nesmeyanov's form at its own temperatures. The two
forms differ by 15 to 24 per cent across the archive, so the literature
bounds the density law at about the spread `density.py` types, and the
record's choice is to put the self-broadening anchor (Zameroski 2014, on the
Alcock axis) and the archive on one law and carry the other as the envelope
(`results/density_laws.csv`).
