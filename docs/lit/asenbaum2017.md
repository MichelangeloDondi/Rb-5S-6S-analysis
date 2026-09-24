---
citekey: asenbaum2017
type: article
authors:
  - Asenbaum, Peter
  - Overstreet, Chris
  - Kovachy, Tim
  - Brown, Daniel D.
  - Hogan, Jason M.
  - Kasevich, Mark A.
title: 'Phase Shift in an Atom Interferometer due to Spacetime Curvature across its Wave Function'
journal: Phys. Rev. Lett.
volume: 118
number: 18
pages: 183602
year: 2017
doi: 10.1103/PhysRevLett.118.183602
arxiv: null
pdf: PDF_papers/atom_interferometry/Asenbaum_2017_tidal-phase-shift-spacetime-curvature-wave-function.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/asenbaum2017.md  # line-by-line against the held PDF, 2026-09-22. Fixed one real overclaim in Routing, where the private exchange file does not discuss this paper by name. All numbers, equations and page attributions confirmed exactly against text and rendered pages. One quotation removed as a precaution against a text-layer hyphenation artifact
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published Physical Review Letters typeset article,
    carrying the standard journal identifier line in its page footer and a
    banner naming it as selected for a Viewpoint commentary, 5 pages, 183602-1 to
    183602-5, PDF version 1.4 per pdfinfo. No arXiv identifier is printed
    anywhere in the document, so arxiv is set to null. Read in full on
    2026-09-22: the abstract, the complete running text, all four figures with
    captions, Eq. (1), and every displayed phase-shift formula.'
  - 'All five pages were rendered to page images at 150 dots per inch and read
    against the pdftotext -layout extraction, specifically to check the
    stacked sub/superscripts in the phase-shift formulas and in Eq. (1), and
    a footer line found to differ between the two (a slash-separated journal
    identifier code that the text layer renders with equals signs instead of
    slashes). No other discrepancy was found between the rendered pages and
    the extracted text for any number, subscript or equation used below.'
verified_date: 2026-09-22
summary: >
  A dual light-pulse atom interferometer using an ultracold rubidium-87 fountain
  reports the first observation of a phase shift caused by spacetime curvature
  across the width of a single atom's wave function, distinct from the phase
  shift caused by ordinary local acceleration. Large momentum transfer atom
  optics and long interrogation times give wave packet separations up to 16 cm,
  comparable to the length scale over which a nearby 84 kg lead source mass
  changes the local gravity gradient, and the tidal phase shift is isolated by
  comparing the gradiometer phase with and without the source mass present, as a
  function of both the momentum-transfer order and the launch height. The
  measurements rule out a model that keeps only the ordinary local-acceleration
  phase and agree with a model that adds the tidal term. The same apparatus is
  demonstrated as a gravity gradiometer near its estimated shot-noise limit and
  used to map the gravity gradient produced by the Earth and the surrounding
  building as a function of height. The paper closes by naming the gravitational
  Aharonov-Bohm effect and a laboratory measurement of the gravitational
  constant as further uses of the same single-source dual-interferometer
  geometry.
loci: []
section: unsorted
---

# asenbaum2017

VERIFIED. Held (published Phys. Rev. Lett. PDF, no arXiv identifier printed), 5 pages. Read in full on 2026-09-22.

## What it does

A dual light-pulse Mach-Zehnder atom interferometer, built around an ultracold
rubidium-87 cloud launched vertically into a 10 meter atomic fountain, isolates
and measures a phase shift that comes specifically from spacetime curvature
acting across the spatial extent of a single atom's wave function, distinct
from the phase shift produced by ordinary local acceleration (p. 1, abstract
and p. 1 introduction). The introduction frames this with a single-geodesic
comparison: for lasers that either follow a particle's geodesic or stay fixed
in the lab frame, the ordinary phase shift works out to phi_lab = n k g_i T^2 +
n k v_i T_zz T^3 + (7/12) n k g_i T_zz T^4, where n is the momentum-transfer
order, k the laser wave number, g_i and v_i the local acceleration and velocity
at the first beam splitter, T_zz a gravity-gradient component and T the pulse
spacing, and this expression carries no tidal contribution (p. 1). Large
momentum transfer atom optics based on two-photon Bragg transitions and long
interrogation times give wave packet separations of up to 16 centimeters (p. 1
to 2). A single atom cloud is split into two vertically separated wave packets,
each of which sources its own Mach-Zehnder interferometer, so that vibration
noise common to both interferometers cancels in their differential,
gradiometer phase (p. 2).

Because a perfectly uniform gravity gradient would produce the same tidal
phase in both interferometers and cancel out of the gradiometer signal, the
paper places lead bricks (seven of them, 84 kg total, per the Fig. 2 caption,
though the running text calls them several bricks) near the top of the
interferometer trajectory to create a gradient that varies enough over the
wave packet separation to
leave a signature in the gradiometer phase (p. 2 to 3). The tidal phase shift
is identified by comparing the measured gradiometer phase, with and without
the bricks present, against a full trajectory calculation and against a
calculation that keeps only the ordinary local-acceleration phase, as a
function of both the momentum-transfer order and the launch height (p. 2 to
4). The data deviate strongly from the local-acceleration-only model and agree
with the full calculation that includes the tidal term (p. 3). A further
comparison, splitting the total phase into the local-acceleration
contributions along each interferometer arm through a standard midpoint
theorem for light-pulse interferometers, shows that the upper and lower arms
of at least one interferometer experience resolvably different accelerations,
which the paper reads as direct evidence that the atomic wave function acts as
a nonlocal probe of the spacetime manifold and not a single populated
trajectory (p. 3 to 4).

The same apparatus is also demonstrated as a precision gravity gradiometer. It
is used, separately from the tidal-shift measurement, to map the gravity
gradient produced by the Earth and the surrounding building as a function of
launch height in the apparatus, fitting the local surface density as the one
free parameter of an Earth model (p. 4).

## The numbers

| quantity | value | page |
|---|---|---|
| Maximum measured wave packet separation | 16 cm, with L = 20 cm, n = 38, T = 700 ms | p. 2 |
| Source mass | seven lead bricks, 84 kg total | p. 2 to 3 |
| Phase shift produced by the bricks | 1.0 rad | p. 2 |
| Tidal phase shift, uniform-gradient example | phi_tidal about (hbar / 2m) n^2 k^2 T_zz T^3 = (1/2) n k Delta_z T_zz T^2 | p. 3 |
| Gradiometer tidal-phase difference (the measured quantity) | Delta_phi_tidal about (hbar / 2m) n^2 k^2 (Delta_T_zz) T^3 | p. 3 |
| Gradiometer resolution | 3 E per shot, with L = 32 cm, n = 20, T = 600 ms (1 E = 10^-9 per s^2) | p. 4 |
| Differential acceleration sensitivity | 1x10^-10 g per shot, 5x10^-10 g per sqrt(Hz) at a 22 s cycle time | p. 4 |
| Estimated shot-noise limit | about 1 E per shot | p. 4 |
| Fitted local Earth surface density | rho = 2.3 g/cm^3 | p. 4 |
| Gravity-gradient statistical uncertainty | about 6 E per point, 50-shot average | p. 4 |
| Gradiometer phase stability | 130 mrad per shot, with L = 32 cm, n = 30, T = 550 ms | p. 4 |
| Atom number and temperature after launch and collimation | about 10^6 atoms, about 50 nK transverse effective temperature | p. 1 to 2 |

Sources: the running text and the captions of Figs. 1 to 4. The single-shot
phase-stability figure is used to bound extensions of quantum mechanics that
would add noise to the gradient measurement, citing anomalous wave packet
localization at a length scale of about 10 cm as one example (p. 4).

## Systematics

This is a five-page Letter, and several of the quantities it discusses by name
are quantified only in its Supplemental Material, which is not part of the
held PDF (see Limits). What follows is what the five held pages themselves
say, or do not say, against each of the four classes.

Intensity or differential light shift the atoms sample: the beam-splitter and
mirror pulses are two-photon Bragg transitions described as fully compensated
for the ac Stark shift (p. 2), citing the group's own longer methods paper for
how the compensation is implemented. No numeric error-budget line for a
residual differential light shift, or for laser intensity noise, appears in
the held text.

Finite size of the interrogation beam: the only beam waist given anywhere in
the paper belongs to the optical dipole lens used to collimate the launched
atom cloud after the fountain launch, stated as a 1 mm waist on a red-detuned
laser beam (p. 1 to 2). That is a state-preparation element, not the Bragg
beams that drive the interferometer pulses, and no size, truncation or
error-budget figure is given for the interrogation beams themselves, nor is
one attached to the dipole lens.

Wavefront, curvature, aberration or flatness of a beam: not mentioned anywhere
in the held text. No term of this kind appears in the phase-shift discussion
or in either error-budget sentence the paper does carry.

Source mass position or alignment: the source mass is seven lead bricks, 84 kg
total, placed near the top of the interferometer trajectory (p. 2 to 3). Its
effect on the gradiometer phase is obtained by numerically calculating the
propagation, laser and separation phases along the perturbed interferometer
trajectories (p. 2), and the paper states in one sentence that the systematic
error of the gradiometer phase from changes in the horizontal position of the
atoms was found to be small, with the supporting figures deferred to the
paper's own Supplemental Material (p. 2). No stated placement tolerance or
resulting phase uncertainty for the bricks themselves appears in the held
text.

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` is a private record
synthesising what this record's own work can offer to, and draw from, the
wider gravitational atom-interferometry community, written for the
application. It does not discuss this specific paper or its tidal-curvature
result by name. The connection is institutional, not a shared number: the
paper's own closing paragraph names the gravitational Aharonov-Bohm effect
and a laboratory measurement of the gravitational constant as further uses of
its single-source dual-interferometer geometry, placing it in the same
precision-gradiometry community the private record addresses when it surveys
that field's systematics and inference methods. Nothing in the paper feeds a
number into any file under results. It is a fountain-launched, free-space,
large-momentum-transfer interferometer probing a curvature effect at the
centimeter-to-meter scale against a laboratory source mass, sharing no
observable, transition or apparatus with a vapour-cell two-photon line, a
differential polarizability, or a guided-atom platform. It is held for lineage
and application context only.

## Limits

The paper's own Supplemental Material is cited repeatedly, for the phase
determination between the two interferometers, the size of the
horizontal-position systematic, and the gradiometer-resolution derivation, but
it is not part of the five-page PDF held here and was not read. The 45-entry
reference list was not read individually beyond confirming its presence and
locating the entries the main text cites by number.
