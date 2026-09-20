---
citekey: stroud2021
type: article
authors:
  - Stroud, Jasper R.
  - Simon, James B.
  - Wagner, Gerd A.
  - Plusquellic, David F.
title: 'Interleaved Electro-Optic Dual Comb Generation to Expand Bandwidth and Scan Rate for Molecular Spectroscopy and Dynamics Studies near 1.6 μm'
journal: Opt. Express
volume: 29
pages: 33155--33170
year: 2021
doi: 10.1364/OE.434482
arxiv: '2106.11414'
pdf: PDF_papers/Stroud_2021_interleaved-EO-dual-comb-scan-rate.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 read against the PDF on 2026-09-20 (title, abstract, introduction, and the
    outline of the paper's own sections through the start of Sec. 2). The experimental results
    in Secs. 4 and 5, including the CO2 spectra and the rapid-passage lineshape modelling, are
    not read beyond the numbers quoted in the Sec. 1 outline.
  - No DOI or journal banner is printed on the two pages read of the held PDF, which appears to
    be the author/typeset manuscript rather than the publisher's paginated PDF. The journal,
    volume, page range and DOI above were confirmed via the Optica Publishing Group and NIST
    publications listings on 2026-09-20. The companion arXiv preprint is 2106.11414.
  - 2026-09-20: adversarial audit_F corrected four page attributions. The "Section 1 outline"
    paragraph carrying all four headline numbers (bandwidth, higher-order bandwidth, scan time,
    scan rate) begins partway down manuscript page 2, not page 1.
verified_date: null
summary: >
  A NIST paper demonstrating an electro-optic (EO) dual-frequency-comb spectrometer, built from
  two chirped-pulse EOMs driven by an arbitrary waveform generator, that reaches optical scan
  rates up to 43.5 MHz/ns and bandwidth coverage up to 120 GHz while resolving CO2 molecular
  lines near 1.6 um. It is a laser-source and scanning-technique paper for molecular gas-phase
  spectroscopy, not atomic two-photon spectroscopy, and shares no species, transition or
  apparatus with this record's Rb 993 nm line. It is held as background on fast-scanning
  EO-comb technique should this record's own laser-scanning apparatus ever be reconsidered,
  not as a number or method this record currently uses.
loci: []
section: unsorted
---
# stroud2021

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | NIST Applied Physics Division (Boulder), with UC Berkeley and DLR co-authors | p. 1 |
| tunability of chirp rate and comb resolution | more than three orders of magnitude | p. 1, abstract |
| first-order optical bandwidth coverage demonstrated | 30 GHz (1 cm^-1) | p. 2, Sec. 1 outline |
| higher-order (up to 4th order) bandwidth coverage | up to 120 GHz (4 cm^-1) | p. 2, Sec. 1 outline |
| shortest demonstrated scan time | as short as 8 ms | p. 2, Sec. 1 outline |
| highest demonstrated optical scan rate | as high as 43.5 MHz/ns | p. 2, Sec. 1 outline |
| target molecule and band | CO2 near 1.6 um | p. 1 |
| balanced-detector bandwidth | 400 MHz (Thorlabs PDB570C) | p. 2 |

## What it says, in its own terms

**The technique class.** Dual optical frequency combs built from mode-locked lasers are well
established but complex. Electro-optic (EO) dual combs generated from a single free-running
seed laser through two phase modulators are simpler and maintain mutual phase coherence, at
the cost of limited bandwidth (typically a few cm^-1) when driven by a single-frequency
microwave tone, since low drive amplitudes are needed to suppress higher diffraction orders.

**The paper's method.** Driving each EOM instead with a linearly-chirped waveform from an
arbitrary waveform generator (AWG) spreads the source power evenly across the chirp bandwidth
and allows the chirp rate and comb resolution to be tuned independently over more than three
orders of magnitude, at the cost of no longer being able to resolve individual comb orders in
the down-converted RF spectrum (since all orders overlap). The paper introduces an
"interleaving" scheme to recover a unique one-to-one mapping of each diffraction order into
the RF region, using either a segmented-scan approach (limiting the down-converted bandwidth
to under 500 MHz) or a dual-chirp scheme that trades comb resolution for a large increase in
scan rate.

**The result.** First-order spectra spanning 30 GHz and higher-order (up to 4th) spectra
spanning up to 120 GHz are demonstrated on four sequential CO2 lines near 1.6 um, with scan
times as short as 8 ms and optical scan rates as high as 43.5 MHz/ns. The rapid-passage
distortions this fast scanning introduces are modelled with a Maxwell-Bloch approach (Sec.
4.4, not read here).

## What it is worth here

Little to this record directly. This is a laser-source engineering paper for dual-comb
molecular gas-phase spectroscopy at telecom wavelengths, sharing no atomic species, no
transition and no detection scheme with this record's Rb 5S-6S two-photon vapour-cell line,
whose own laser source is a single swept-frequency diode laser with EOM sidebands for
calibration, not a dual comb. It is worth keeping on file only as an example of how far
EO-comb chirped-pulse scanning can be pushed in scan rate and bandwidth, should a future
apparatus upgrade for this line's own campaign ever consider a comb-based scan instead of a
swept single-frequency laser.
