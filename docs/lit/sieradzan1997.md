---
citekey: sieradzan1997
type: article
authors:
  - Sieradzan, A.
  - Stoleru, R.
  - Yei, Wo
  - Havey, M. D.
title: 'Measurement of hyperfine coupling constants in the 3d 2Dj levels of 39K, 40K, and 41K by polarization quantum-beat spectroscopy'
journal: Phys. Rev. A
volume: 55
number: 5
pages: 3475--3483
year: 1997
doi: 10.1103/PhysRevA.55.3475
arxiv: null
pdf: PDF_papers/Sieradzan_1997_K-3d-hyperfine-constants-polarization-quantum-beats.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1, 5 and 9 read against the PDF on 2026-09-20 (title/abstract/introduction, Table I
    of results, and the summary/conclusion with references). Pages 2 to 4 and 6 to 8, carrying
    the theory of the polarization quantum-beat method and the experimental apparatus, are not
    read.
  - The abstract's own worked example (p. 1) names a value pair A = 0.96(4) MHz, B = 0.37(8)
    MHz and attributes it, in the PDF's extracted text, to "the 3d 2D3/2 level of 40K". Table I
    (p. 3479) assigns that exact value pair to the 39K column of the 3d 2D3/2 row instead, and
    the 40K column there reads A = 1.07(2), B = 0.4(1). Old Physical Review issues sometimes
    render isotope-label superscripts as ordinary digits under text extraction, so this is
    read as an extraction artefact on the abstract's isotope label, not as a second value for
    A = 0.96(4). The Values table below follows Table I's own column headers, which are
    unambiguous.
  - 2026-09-20: adversarial audit_F found the nuclear-spin row cited to p. 1. The spin values
    appear only on p. 5, in the theory section following Eq. (4). Page 1 (title, abstract,
    introduction) names no isotope spin at all. Corrected.
verified_date: null
summary: >
  A polarization quantum-beat spectroscopy measurement of the magnetic-dipole (A) and
  electric-quadrupole (B) hyperfine coupling constants in the 3d 2D3/2 and 3d 2D5/2 levels of
  all three stable potassium isotopes, the first such measurement for these levels, resolving
  splittings smaller than the natural linewidth by using a subnatural-linewidth technique. The
  species (potassium, not rubidium), the states (3d, not 5S/6S), and the method (pulsed
  pump-probe quantum beats on a fluorescence/polarization signal, not continuous-wave
  two-photon absorption) are all outside this record's own programme, so it is held as
  adjacent-field background rather than as usable prior art or a numeric input.
loci: []
section: unsorted
---
# sieradzan1997

## Values

Table I (p. 3479), magnetic-dipole (A) and electric-quadrupole (B) hyperfine coupling
constants in MHz, cited errors representing two standard deviations. C is a dimensionless
amplitude fitting parameter:

| level | parameter | 39K | 40K | 41K |
|---|---|---|---|---|
| 3d 2D3/2 | A | 0.96(4) | 1.07(2) | 0.55(3) |
| 3d 2D3/2 | B | 0.37(8) | 0.4(1) | 0.51(8) |
| 3d 2D3/2 | C | 1.024(9) | 0.939(13) | -- |
| 3d 2D5/2 | A | 0.62(4) | 0.71(4) | 0.40(2) |
| 3d 2D5/2 | B | < 0.3 | 0.8(8) | < 0.2 |
| 3d 2D5/2 | C | 0.95(3) | 0.98(2) | -- |

| field | value | where in the paper |
|---|---|---|
| nuclear spin | I = 3/2 for 39K and 41K; I = 4 for 40K | p. 5 |
| technique's stated resolution floor | coupling constants as small as 0.1 times the natural width | p. 9 |
| range of A demonstrated across the whole quantum-beat programme (Na, K, Cs) | about 0.5 MHz to nearly 50 MHz | p. 9 |

## What it says, in its own terms

**The technique.** Pulsed, linearly polarized light excites the 3d levels from 4d 2S1/2 on an
electric-quadrupole transition, preparing a coherent superposition across the magnetic
sublevels. The hyperfine interaction, acting between the nucleus and the electron cloud,
redistributes this alignment over time, producing quantum-beat oscillations at the hyperfine
frequencies. A time-delayed, polarization-resolved probe on the 3d 2Dj -> 9p 2Pj transition
reads out the beats through the linear polarization degree of the induced fluorescence, and
fitting that time dependence to a theoretical model (built from Racah coefficients and the
alignment-depolarization function) extracts A and B. Because the observable is a polarization
ratio rather than an absolute frequency, the method achieves subnatural-linewidth resolution:
several of these levels have a total hyperfine splitting smaller than their own natural
width, which would defeat a direct frequency-resolved measurement.

**The result.** All twelve A and B values (three isotopes times two fine-structure levels) are
reported for the first time (p. 9), each to a few percent precision, with a stated
demonstrated capability down to hyperfine splittings as small as one-tenth of the natural
linewidth. Systematic checks (varying which fine-structure component of the 9p decay is
probed, and rotating the probe polarization relative to the detector) found no measurable
effect on the extracted A and B, attributed to strong collisional depolarization erasing any
angular-distribution anisotropy from the intermediate 9p levels before it could bias the
signal.

## What it is worth here

Little, honestly. This is a potassium 3d-level hyperfine measurement by pulsed quantum-beat
spectroscopy, sharing no species, no electronic states and no experimental technique with this
record's Rb 5S-6S continuous-wave two-photon vapour-cell line. It is held as a well-executed
example of extracting structure smaller than a natural linewidth from a polarization
observable rather than a frequency one, which is a technique class this record does not use
(the record's own sub-linewidth information comes from the AC-Stark-shift distribution across
an intensity profile, not from a temporal coherence beat), so the relevance stops at general
atomic-physics background.
