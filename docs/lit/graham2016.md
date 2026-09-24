---
citekey: graham2016
type: article
authors:
  - Graham, Peter W.
  - Hogan, Jason M.
  - Kasevich, Mark A.
  - Rajendran, Surjeet
title: 'Resonant mode for gravitational wave detectors based on atom interferometry'
journal: Phys. Rev. D
volume: 94
number: 10
pages: 104022
year: 2016
doi: 10.1103/PhysRevD.94.104022
pdf: PDF_papers/atom_interferometry/Graham_2016_resonant-mode-atom-interferometric-gravitational-wave-detector.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/graham2016.md  # line-by-line against the held PDF, 2026-09-22, five section or page citations corrected in the narrative (all misattributions, not content errors), every number, equation, the quotation and the systematics findings confirmed exactly against rendered page images
author: agent
routing:
  - CITE
verify_flags:
  - 'Held PDF is the published Phys. Rev. D 94, 104022 (2016) version (received 7 June 2016,
    published 10 November 2016), 10 pages, confirmed with pdfinfo. No arXiv identifier is
    printed anywhere in the PDF, so arxiv is left out instead of guessed.'
  - 'Read in full on 2026-09-22 with pdftotext -layout: the introduction, the resonant-mode
    section with its response-function and stochastic-sensitivity parts, the strain-sensitivity
    section, the discussion section with its detector-design, cosmology-and-astrophysics,
    sensitivity-curve-constraints and noise-constraints parts, the conclusions, Eqs. (1)-(15),
    Figs. 1-4 with captions, the acknowledgments and the reference list.'
  - 'Pages 1, 4, 5, 6, 7 and 8 additionally rendered at 150 dpi and read as images, because
    pdftotext systematically turns a division slash into an equals sign in inline text (a pi/2
    pulse prints as pi=2) and drops radical and stacked-fraction glyphs from exponents and
    square roots (the stochastic-sensitivity scaling prints as a bare Q-2 in the text layer and
    resolves to Q to the power of minus three halves on the page image, and a swept-resonance
    scaling that prints as broken fragments resolves to the square root of Q). Every number
    quoted below with a page number was confirmed on the rendered page for that page.'
verified_date: 2026-09-22
summary: >
  Proposes a resonant operating mode for an atom-interferometric gravitational-wave detector
  built from two widely separated atom interferometers run on common lasers along a single
  baseline. Replacing the standard three-pulse sequence with a train of Q pi-pulses that
  periodically swap the interferometer arms lets phase shifts from a passing gravitational wave
  accumulate coherently across every pulse pair, trading bandwidth for a Q-fold gain in peak
  response around a tunable resonance frequency, stacked on top of the usual n-fold gain from
  large-momentum-transfer beam splitters. The same hardware switches between broadband and
  resonant operation purely by changing the pulse sequence in software. An example space-based
  design (baseline 4.4x10^7 m, an assumed atom shot-noise-limited phase readout of 10^-5 rad
  per root Hz, a 50 cm telescope) is worked through for both a coherent source, where resonant
  follow-up sharpens direction and parameter estimation for an inspiraling binary, and a
  stochastic background, reaching a projected energy-density spectrum near 10^-14 for
  inflationary gravitational waves. The sensitivity curve is atom-shot-noise limited throughout,
  and the paper states plainly that it leaves out every other noise source, budgeting only
  photon shot noise, laser frequency noise from timing jitter, platform kinematic noise and
  laser wavefront aberration as the requirements a real design would need to meet.
loci: []
section: unsorted
---

# graham2016

VERIFIED. Held (published Phys. Rev. D 94, 104022 version), 10 pages. Read in full on
2026-09-22.

## What it does

The paper proposes a resonant pulse-sequence scheme for an atom-interferometric
gravitational-wave detector built around two widely separated atom interferometers, run with
common lasers along a single baseline (p. 1). Each interferometer is described as effectively
an optical clock comparing the laser's phase against the atom's phase, and a passing
gravitational wave changes the relation between the two clocks in proportion to the baseline
length, which is the differential, gradiometer phase the detector reads out (p. 1). The abstract
describes this differential signal as "functioning like a lock-in amplifier for astrophysical
events" before noting that the same enhanced sensitivity also opens up stochastic cosmological
searches (p. 1). The proposal builds on an existing broadband single-photon-transition design
and states that it applies equally to a two-photon Bragg or Raman atom-optics implementation
(p. 1-2).

The standard broadband sequence is a pi/2, pi, pi/2 pulse triplet, maximally sensitive to a
gravitational wave whose half-period matches the interrogation time T. The resonant sequence
instead applies Q pi pulses in a row, equally spaced in time by T, so the interferometer arms
are periodically swapped and the phase contributions from successive half-cycles of the
gravitational wave add instead of cancelling (p. 2). The response is peaked at a
resonance frequency and has a bandwidth that narrows as the pulse count Q grows (p. 4).
Large-momentum-transfer beam splitters can be folded into each pulse, so that every pulse in
the sequence is really n closely spaced pulses transferring n times the single-photon recoil
(Section 2, subsection A, p. 2, 4). The peak on-resonance phase shift, in the low-frequency
limit, reduces to about 2 Q k_eff h L (Eq. 10, p. 4), proportional to the resonant enhancement
Q, the large-momentum-transfer order n through k_eff, the strain amplitude h and the baseline
length L, giving independent n-fold and Q-fold sensitivity gains. Because switching between
broadband and resonant operation is only a change of pulse sequence, the paper states the same
hardware can move between the two modes in real time, in software (p. 4, 8).

Two uses are developed at length. For a coherent, long-lived source such as an inspiraling
binary, a resonant follow-up after a broadband detection raises the signal-to-noise ratio and
sharpens the inferred direction and parameters (Section 4, subsection B, p. 7). For a stochastic
background such as the one expected from cosmic inflation, the paper derives a sensitivity
estimate, a 95 per cent confidence limit following an existing cross-correlation method, from the
same peak-response curve integrated over the resonance bandwidth (Section 2, subsection B,
Eq. 11, p. 4-5).

An example design (Section 3, p. 5) sets a baseline of 4.4x10^7 m using heterodyne laser links,
targets the 0.1 to 1 Hz band, and works through several resonant sequences at fixed practical
constraints, a maximum of 1000 total pulses and a maximum interferometer duration of 300
seconds. Section 4 then works through the trade-off between large-momentum-transfer enhancement
and resonant enhancement for the physical size of the interferometer region, the astrophysical
and cosmological use cases in more detail, the practical constraints that shape the example
sensitivity curve, and the noise sources budgeted against the assumed atom shot-noise floor.

## The numbers

| quantity | value | page |
|---|---|---|
| projected stochastic sensitivity, two-satellite example | gravitational-wave energy-density spectrum about 10^-14 for inflationary waves | p. 1 |
| example baseline length | L = 4.4x10^7 m | p. 5 |
| assumed atom interferometer phase noise floor | 10^-5 rad per root Hz | p. 5 |
| assumed telescope diameter | d = 50 cm | p. 5 |
| maximum total pulse count | n_max = 1000 | p. 5, 7 |
| maximum interferometer duration | T_max = 300 s | p. 5, 7 |
| vacuum and temperature needed to reach T_max | about 10^-10 Torr or better, about 10 pK atom ensembles by delta-kick cooling | p. 7 |
| repetition rate | `f_rep = chi/(2T)`, with chi = 10 samples per gravitational-wave period | p. 5 |
| example resonant sequences (Q, momentum-transfer order in single-photon recoils) | (12, 6), (71, 4), (166, 2), (450, 1) | p. 5 |
| stochastic scaling with resonance, fixed resonance frequency | energy-density spectrum proportional to Q^(-3/2) | p. 5 |
| coherent-source scaling with resonance, swept mode | strain sensitivity improves roughly as the square root of Q | p. 7 |
| geometric factor in the stochastic estimate, maximum value | 8pi/5 | p. 5 |
| wave-packet separation, equal sensitivity with and without resonance | about 8 m at Q=1, n=284 versus about 10 cm at Q=71, n=4 | p. 6 |
| assumed atom flux at the phase-noise floor | 10^10 atoms per second unsqueezed, or 10^8 per second with 20 dB of spin squeezing | p. 5 |
| minimum telescope diameter scaling at fixed photon shot noise | d_min proportional to L^(2/5) n^(1/5) | p. 8 |
| example stochastic sequence, Fig. 4 red curve | resonance frequency 0.15 Hz, Q = 44, 6-photon-recoil optics, 1 year integration | p. 6 |

## Systematics

The paper's own sensitivity curve, Fig. 3, is explicitly atom-shot-noise limited only. The
noise-constraints part of Section 4 opens by stating plainly that the curve does not take into
account all the other possible noise sources, and that implementing any further constraint in a
realistic design is left undiscussed (p. 7). Four noise budgets are given, each as the
requirement that would keep that source below the atom shot noise floor, and none of the four is
a light-shift or intensity-sampling term.

- Intensity or differential light shift the atoms sample: not found. No equation or budget line
  in the noise-constraints part depends on laser intensity or on an intensity-dependent Stark
  shift. The atoms are treated as free-falling point sensors driven by discrete pulses from a
  distant telescope, not as continuously immersed in a trapping or probe beam whose intensity
  they sample.
- Finite size of the interrogation beam: not present in the sense of atoms sampling a spatially
  varying beam profile. What the paper does budget is the transmitting telescope's aperture: the
  minimum diameter, 50 cm in the example, is set so that the diverging laser beam over the
  4.4x10^7 m baseline keeps photon shot noise below the atom shot noise floor (Eq. 12, p. 7-8),
  and it scales as roughly L^(2/5) and weakly with the large-momentum-transfer order n (p. 8). A
  related but distinct size constraint is the physical spread of the interferometer region
  itself, set by the wave-packet separation from large-momentum-transfer recoil, which resonant
  enhancement can shrink from meters to centimeters at fixed sensitivity (p. 6).
- Wavefront, curvature, aberration, flatness: present and explicit. Laser wavefront aberrations
  couple to the satellite's transverse position noise, and because the phase error from an
  aberration adds coherently with every pulse, the sequences with the most total pulses are the
  most demanding (Eq. 13, p. 8). The wavefront tolerance can be traded against the position-noise
  budget, and the paper notes it might be relaxed by imaging the atom ensemble and resolving the
  phase imprint of the aberration directly (p. 8).
- A source mass's position or alignment: not applicable. The design has no local source mass. It
  is a free-fall gradiometer reading the differential phase between two atom clocks linked by
  laser pulses over an ultra-long baseline, not a local-source or gravity-gradient measurement.
  The nearest related budget is platform kinematic noise, from a relative velocity between the
  two satellite interferometers caused by orbital perturbations, not by any source mass (Eq. 15,
  p. 8).

Beyond these four, the paper also budgets laser frequency noise arising from timing jitter in
the heterodyne laser link (Eq. 14, p. 8).

## Routing

Named in `private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` as part of the free-fall,
large-momentum-transfer design lineage among the fundamental-physics atom-interferometry papers
held for this application. No number in this paper feeds this record's own vapor-cell model, its
twin, or any file under results. The connection to this record is institutional and historical
only: a resonant pulse-sequence scheme for a laser-linked satellite gravitational-wave detector,
read here for the application's own use of the wider atom-interferometry field, not because it
shares an observable or a systematic with the 5S-6S line this record measures.

## Limits

The paper is a design proposal with a projected, atom-shot-noise-limited sensitivity curve, not
a report of a built instrument or a measured systematics budget. It says so directly: a full
experimental design is beyond its scope, and the example parameters in Fig. 3 are not optimized
for science reach or for avoiding technical noise sources (p. 6). Sections 1 through 5 were all
read in full and every number above that comes from a boxed equation or a fractional exponent
was checked against a rendered page image. The reference list, p. 9-10, and the earlier
phase-derivation equations, Eqs. 1-8, p. 3-4, were read but are drawn on above only through the
response-function result, Eqs. 9-10, that they feed into.
