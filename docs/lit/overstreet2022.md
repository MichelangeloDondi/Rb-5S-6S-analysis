---
citekey: overstreet2022
type: article
authors:
  - Overstreet, Chris
  - Asenbaum, Peter
  - Curti, Joseph
  - Kim, Minjeong
  - Kasevich, Mark A.
title: 'Observation of a gravitational Aharonov-Bohm effect'
journal: Science
volume: 375
number: 6577
pages: 226-229
year: 2022
doi: 10.1126/science.abl7152
arxiv: null
pdf: PDF_papers/atom_interferometry/Overstreet_2022_observation-gravitational-aharonov-bohm-effect.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/overstreet2022.md  # line-by-line against the held PDF, 2026-09-22, the source-mass geometry and the headline statistics also confirmed on 400 dpi page renderings, one overclaim (the source mass read as experimentally varied) caught and corrected during drafting
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published Science typeset article (PDF version 1.4 per
    pdfinfo, whose Subject field reads Science 2022.375:226-229), 5 pages: the
    4-page Report, pp. 226-229, carrying a Research Report running header on
    each page, plus the journal abstract card. No arXiv identifier is printed
    anywhere in the document, so arxiv is set to null. Read in full on
    2026-09-22: the abstract, the complete running text of all four Report
    pages, the Fig. 2 and Fig. 3 captions (Fig. 1 is the apparatus schematic,
    not separately cited below), the references and notes list, and the
    abstract card.'
  - 'Page 3 was additionally rendered to PNG at 400 dpi and read as a cropped
    image, specifically to confirm the sign of the exponent in the printed
    likelihood ratio against the plain-text extraction, whose layout drops
    superscript minus signs. The rendered page confirms 2 x 10^-13, matching
    the 7-sigma significance the same sentence states, not 2 x 10^13.'
  - 'The Materials and Methods, Supplementary Text and Figs. S1-S2 that the
    references list as note (15) are a separate Supplementary Materials
    document at the paper''s own DOI and are not part of the held 5-page PDF.
    Nothing below draws on them. Every place the running text defers a number
    to them is flagged as such.'
verified_date: 2026-09-22
summary: >
  A light-pulse atom interferometer splits a rubidium-87 wave packet with a
  large-momentum-transfer beam splitter, 52 photon recoils, into two arms 25 cm
  apart, holding one arm as close as 7.5 cm from a 1.25 kg tungsten ring while
  the other stays far away. A second, low-momentum-transfer interferometer
  pair (4 photon recoils each) measures how much the ring deflects the atoms
  directly, and once that deflection-induced phase is subtracted from the main
  interferometer's own signal, a nonzero phase shift remains, -125 +/- 24 mrad
  and -182 +/- 28 mrad at two source-mass heights, a 7-sigma rejection of no
  effect. The paper reads this leftover phase as a gravitational analogue of
  the Aharonov-Bohm effect, a phase a spatial superposition acquires from a
  potential even where the trajectories themselves are not measurably altered.
  The theory curves plotted against the data carry an explicit uncertainty
  band from the source mass's position, though the size of that positional
  uncertainty is not stated in the held pages. The same apparatus operates as
  a gravity gradiometer at a stated shot noise level, which the paper connects
  to a possible future measurement of Newton's gravitational constant.
loci: []
section: unsorted
---

# overstreet2022

VERIFIED. Held (published Science PDF, no arXiv identifier printed), 5 pages (4-page Report plus the journal abstract card). Read in full on 2026-09-22.

## What it does

The abstract opens, verbatim, "Gravity curves space and time." and the paper reports a laboratory test of what that curvature does to a particle held in a spatial quantum superposition (p. 1). The apparatus is a light-pulse atom interferometer built around a cloud of rubidium-87 launched into a 10-meter vertical vacuum chamber at 13 meters per second by an optical lattice, after evaporative cooling to about 1 millikelvin in a magnetic trap and velocity narrowing to 2 millimeters per second by magnetic lensing (p. 1). Two clouds, decelerated to a relative momentum of 2 photon recoils by Bragg transitions, feed a single-source gradiometer with a 24 cm baseline (p. 1).

The main interferometer uses large-momentum-transfer atom optics that impart 52 photon recoils to the atoms, written 52 hbar k in the paper where k is the laser wave number, giving a wave packet separation of 25 cm, large enough that one arm can be brought within 7.5 cm of a source mass while the other stays far away (p. 1). A second pair of interferometers with only 4 photon recoils each and a 2 cm wave packet separation runs alongside the main one, in separate shots, and is used purely as a deflection sensor: because its wave packets stay close together its phase shift is close to a direct measure of how far the source mass pulls the atoms off their unperturbed trajectory (p. 1 to 2). The time between the first beam splitter pulse and the mirror pulse is 0.82 seconds (p. 1 to 2).

The physical question is whether the spatial superposition picks up a phase from gravity beyond what the measured deflection of its arms already accounts for, the gravitational analogue of the effect a charged particle shows in a vector potential with no local field along its path. The paper's own framing splits the total phase into a midpoint phase, computed from the measured deflections at the laser pulses, and a beyond-midpoint phase left over after that part is subtracted, which is the signature the paper attributes to the effect (p. 2). The source mass is a tungsten ring, and the core measurement compares the gradiometer phase with and without the ring installed, as a function of how close the interferometer trajectory passes to it (p. 1 to 2). A further check compares the 52-photon-recoil data against the upper 4-photon-recoil data, scaled by their momentum ratio, as a function of the approach distance, against two theoretical scaling limits, one where the shift tracks the momentum kick and not the atom mass and one where it tracks the mass and not the momentum kick, and reports that the transition between the two matches a quantum-mechanical bound relating the information a measurement retrieves to the disturbance it must cause (p. 3). The paper states its own result is the first observation of a gravitational phase shift intrinsically proportional to the test particle's mass (p. 3 to 4).

## The numbers

| quantity | value | page |
|---|---|---|
| Source mass | 1.25 kg, 99.95 per cent pure tungsten, 170-degree ring, inner radius 6.8 cm, outer radius 7.8 cm, height 3 cm | p. 2 |
| Source mass reference position | 27 cm below the magnetic shield's end cap, defining the zero of the scanned approach distance Rx | p. 2 |
| Main interferometer | 52 photon recoils, wave packet separation 25 cm, closest approach to the source mass 7.5 cm | p. 1 |
| Deflection-sensing interferometers | 4 photon recoils each, wave packet separation 2 cm, run as an upper and lower gradiometer pair | p. 1 |
| Gradiometer baseline | 24 cm | p. 1 |
| Interferometer time T | 0.82 s | p. 1 to 2 |
| Single-shot phase uncertainty, main interferometer | about 30 mrad | p. 2 |
| Beyond-midpoint phase shift at Rx = 4 cm | -125 +/- 24 mrad | p. 3 |
| Beyond-midpoint phase shift at Rx = 9 cm | -182 +/- 28 mrad | p. 3 |
| Statistical significance against no gravitational Aharonov-Bohm effect | 7 sigma, likelihood ratio 2x10^-13 | p. 3 |
| Deviation from the deflection-only (midpoint) prediction | 13 sigma at Rx = 4 cm, 19 sigma at Rx = 9 cm | p. 3 |
| Fit quality against the full phase-shift prediction | reduced chi^2 = 0.6 | p. 3 |
| Agreement with the quantum-limit scaling curve near Rx = 0 | within 20 per cent | p. 3 |
| Gravity gradient resolution | 5x10^-10 s^-2 per shot | p. 3 |
| Differential acceleration resolution | 1.1x10^-11 g per shot, 1.4x10^-12 g after 70 shots | p. 3 |
| Velocity kick imparted to the atoms by the source mass | about 1 nm/s, seven orders of magnitude below the beam-splitter recoil velocity | p. 4 |

## Systematics

The held pages are a 4-page Report, and the running text repeatedly defers technical detail to a separate Supplementary Materials document (materials and methods, supplementary text, Figs. S1 and S2) at the paper's own DOI, which is not part of this PDF (see Limits). Against each of the four classes, what the four Report pages themselves carry is:

Intensity or differential light shift the atoms sample: not mentioned anywhere in the held text. The word intensity does not appear, and no light-shift term is named in either the phase-shift derivation or the discussion of what limits the measurement's uncertainty.

Finite size of the interrogation beam: not mentioned anywhere in the held text. No beam waist, diameter or truncation figure is given for the Bragg beam-splitter and mirror pulses, and no size-dependent term appears in the phase-shift expression or in the discussion of the 52-photon-recoil and 4-photon-recoil interferometers.

Wavefront, curvature, aberration or flatness of a beam: not mentioned anywhere in the held text. The only use of the word curvature in the four pages refers to spacetime curvature, in a footnote defining what the paper means by a local system, and not to an optical wavefront.

Source mass position or alignment: this is the systematic the held pages do carry, and it sits at the center of the measurement. The tungsten ring's geometry and its reference position, 27 cm below the magnetic shield's end cap, defining Rx = 0, are stated exactly (p. 2). The paper states plainly that the source mass was verified to be nonmagnetic at the level the measurement needs, with the verification itself deferred to the Supplementary Materials (p. 1 to 2). The theoretical prediction curves plotted against the data, in both the approach-distance scan and the scaling analysis, carry an explicit 1-sigma uncertainty band, and both figure captions state directly that curve widths are derived from uncertainty in source mass position (p. 2 to 3). No numeric size for that positional uncertainty, in millimeters or any other unit, appears anywhere in the four held pages. The paper does state that the uncertainties in the extracted beyond-midpoint phase are limited primarily by the resolution of the 4-photon-recoil deflection-sensing gradiometers, not by the source-mass term (p. 3), which places the position uncertainty as a budgeted contribution the held pages do not put a number on, and names it as a secondary limit, not the dominant one.

Beyond the four classes, the paper names two further systematic controls in passing. Comparing the gradiometer phase with and without the source mass installed suppresses Earth's gravity gradient and any other systematic effect common to both configurations (p. 2), and reversing the direction of the horizontal detection fringe used for phase readout suppresses imaging-related systematic effects (p. 2). Neither is quantified in the held pages.

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` is a private record synthesising what this record's own work can offer to, and draw from, the wider gravitational atom-interferometry community, written for the application. This paper is the demonstration result behind the gravitational Aharonov-Bohm line that record's survey of interferometer systematics places alongside precision gradiometry and curvature-sensitive interferometry, and its central systematic, trusting a theory curve only as far as the source mass feeding it is characterized, is the same class of problem as trusting a lineshape model only as far as its own geometry and windowing are characterized. Nothing in the paper feeds a number into any file under `results/`. The apparatus is a free-space, fountain-launched, large-momentum-transfer interferometer measuring a phase shift from a kilogram-scale laboratory source mass, sharing no observable, transition or apparatus with a vapour-cell two-photon line, a differential polarizability, or a guided-atom platform. It is held for lineage and application context only.

## Limits

The Materials and Methods, Supplementary Text and Figs. S1 and S2 that the references and notes list as note (15) are a separate document at the paper's own DOI and are not part of the held 5-page PDF. Every deferred quantitative point named above, the size of the source-mass position uncertainty, the level at which the nonmagnetic verification was carried out, and the derivation of the kinetic-energy phase term, sits there, unread here. The 33-entry references and notes list was not read entry by entry beyond locating the numbered citations the running text points to.
