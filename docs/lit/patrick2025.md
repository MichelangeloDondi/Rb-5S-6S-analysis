---
citekey: patrick2025
type: article
authors:
  - Patrick, Link
  - Schlossberger, Noah
  - Hammerland, Daniel F.
  - Prajapati, Nikunjkumar
  - McDonald, Tate
  - Berweger, Samuel
  - Talashila, Rajavardhan
  - Artusio-Glimpse, Alexandra B.
  - Holloway, Christopher L.
title: 'Imaging of induced surface charge distribution effects in glass vapor cells used for Rydberg atom-based sensors'
journal: AVS Quantum Sci.
volume: 7
number: 2
pages: 024401
year: 2025
doi: 10.1116/5.0264378
arxiv: '2502.07018'
pdf: PDF_papers/Patrick_2025_surface-charge-imaging-Rydberg-vapor-cells.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'The held PDF is the arXiv preprint (2502.07018v1, physics.atom-ph, dated
    12 February 2025) and carries no journal reference at all. The journal
    line (AVS Quantum Sci. 7, 024401, DOI 10.1116/5.0264378, published June
    2025) is taken from the AIP Publishing record, confirmed by resolving the
    DOI and getting redirected to pubs.aip.org/aqs/article/7/2/024401. VERIFY
    the journal line again if the published PDF is ever pulled in place of
    the preprint.'
verified_date: 2026-08-03
summary: >
  Fluorescence-imaging measurement of EIT lineshapes along a vapor-cell axis
  localizes surface E fields from induced charge on the glass walls, 85Rb
  two-photon and 133Cs two-photon and 85Rb three-photon Rydberg EIT. Visible
  coupling light (480 nm or 511 nm, both under the roughly 1.9-2.1 eV alkali
  work function boundary near 600 nm) photoionizes the condensed alkali film
  where it strikes the glass, charging that spot positive. A near-IR-only
  three-photon scheme shows no measurable induced field.
loci: []
section: deep-search
---

# patrick2025

Identified from the held PDF against the request: Link Patrick, Noah
Schlossberger, Daniel F. Hammerland, Nikunjkumar Prajapati, Tate McDonald,
Samuel Berweger, Rajavardhan Talashila, Alexandra B. Artusio-Glimpse and
Christopher L. Holloway (Univ. of Colorado Boulder and NIST, Boulder). Dated
12 February 2025 on the preprint, DARPA SAVaNT and NIST-on-a-Chip funded.

**Verbatim abstract:** "We demonstrate the imaging of localized surface
electric (E) field effects on the atomic spectrum in a vapor cell used in
Rydberg atom-based sensors. These surface E-fields can result from an
induced electric charge distribution on the surface. Induced surface charge
distributions can dramatically perturb the atomic spectrum, hence degrading
the ability to perform electrometry. These effects become pronounced near
the walls of the vapor cell, posing challenges for vapor cell
miniaturization. Using a fluorescence imaging technique, we investigate the
effects of surface charge on the atomic spectrum generated with
electromagnetically induced transparency (EIT). Our results reveal that
visible light (480 nm and 511 nm), i.e., the coupling laser used in
two-photon Rydberg EIT schemes, generates localized patches of charge or
dipoles where this light interacts with the glass walls of the vapor cell,
while a three-photon Rydberg EIT scheme using only near-infrared wavelength
lasers shows no measurable field induction. Additionally, imaging in a
vacuum chamber where a glass plate is placed between large electrodes
confirms that the induced charge is positive. We further validate these
findings by studying the photoelectric effect with broadband light during
EIT and impedance measurements. These results demonstrate the power of the
fluorescence imaging technique to study localized E-field distributions in
vapor cells and to target the photoelectric effect of the alkali-exposed
glass of vapor cells as a major disruptor in Rydberg atom-based sensors."

## What it does

A camera images the fluorescence along the propagation axis of a vapor cell
while the coupling laser of an EIT ladder is swept, turning the usual single
photodetector EIT trace into a 2D map (frequency detuning against position
z). Because the DC Stark shift of a Rydberg m_J sublevel scales with the
local field squared, fitting the local lineshape at each z (their Eq. 2, a
sum of Gaussians centered at m_J-dependent Stark-shifted detunings) returns
an E-field value at that point, so the image becomes a 1D field profile
along the beam rather than one path-integrated number.

Three excitation schemes carry the argument. An 85Rb two-photon ladder
(780 nm probe, 480 nm coupling, to 50D5/2 and 50D3/2, in a 25 mm by 78 mm
cylindrical cell) shows fields concentrated at the two points where the
laser beams enter and exit the cell, decaying away from each wall, matching
a finite-element model of a localized charge patch rather than a uniform
surface charge. Recycling the 480 nm coupling light back into the cell at a
chosen re-entry point on the side wall reproduces a Stark shift exactly
there, showing the visible light itself is what charges the glass at the
spot it hits. A 133Cs two-photon EIT run (6S1/2-6P3/2-42D3/2, 850 nm probe,
511 nm coupling) inside a vacuum chamber with a glass plate between plate
electrodes shows the same localized charging from the 511 nm light, and
applying +-4 V to the plates shows the induced charge is positive (a
negative plate voltage enhances the field, a positive one suppresses it).
A broadband source (490-900 nm) scanned through the Cs EIT signal, and
separately through the glass impedance, shows the effect switching on below
about 600 nm (2.1 eV), matching the literature work function of bulk Cs
(about 1.9-2.1 eV), which is their case for photoionization of the alkali
metal film condensed on the cell wall as the mechanism. An 85Rb
three-photon ladder (780, 776 and 1259 nm, to 49F7/2, no visible light at
all) shows little to no induced field, and only develops one again once a
480 nm beam is deliberately added, co-linear or orthogonal to the EIT beams.

## Key numbers

- Wall-adjacent field magnitude, 85Rb two-photon, roughly 0.3 to 2 V/cm
  (their Fig. 2c and 2g y-axis, while the prose text states "on the order
  of 1 V/m" for the same feature, an internal V/m-vs-V/cm inconsistency in
  the paper, not resolved here).
- Field grows with coupling power and saturates: max(|E|) at the coupling
  re-entry point rises from about 0.3 V/cm at 1.2 mW to about 0.85 V/cm
  above roughly 100 mW (Fig. 4c), over the range 1.2 to 192 mW.
- Photoionization onset near 600 nm (2.1 eV) in both the EIT signal and the
  glass/cell impedance, against a literature Cs work function of about
  1.9 to 2.1 eV.
- Imaging resolution 50 micron, pixel-projected in the beam plane,
  0.2 percent fluorescence collection efficiency.
- Positive induced charge, from the +-4 V electrode polarity test.
- Data are deposited at doi.org/10.18434/mds2-3685.

## Lineage bridge: reading a distribution from a lineshape

This is the closest modern atomic-vapor analogue on record here of the
programme's own central move, reading a spatially varying perturbation
distribution off a spectroscopic observable rather than a single fitted
shift. `patrick2025` reads an E-field distribution along the cell axis from
the local EIT lineshape at each imaged point. This repository's own method
(the fringe-averaged closed-form f(s) proportional to |s| to the n-1,
`docs/LITERATURE.md` section 1, and the third-cumulant work built on it)
reads a shift DISTRIBUTION off a single lineshape too, but from one
photodetector trace integrated over the whole illuminated volume, with no
camera and no spatial axis at all.

The paper states its own reason for adding imaging in almost the same words
this repository uses for its own construction: "the photodetector EIT
signal is a path-integrated measurement of all the broadening and shifting
mechanisms as the light propagates through the entire cell. As a result,
isolated local effects are difficult to detect and locate in a simple
photodetector EIT signal." That sentence is a precise statement of what a
spatially-integrated method can and cannot recover. It can recover a
distribution of shifts present in the ensemble (their own photodetector EIT
trace still broadens and shifts when charge is present, and this
programme's fringe-averaged f(s) recovers a shape from exactly that kind of
trace). It cannot recover WHERE along the beam each part of that
distribution originates, which is the one thing their added camera axis
buys and a purely spectroscopic, spatially-integrated measurement cannot.
So the two approaches are not competing solutions to the same problem, they
answer different questions from the same class of lineshape distortion, one
recovers the shape of a perturbation's distribution, the other recovers its
map.

## Cell-relevant finding

The mechanism here is photoionization of a thin alkali metal film condensed
on the inner glass wall by resonant or above-threshold visible light,
charging the glass locally where the light lands, positive by their
electrode test. `docs/APPARATUS.md` section 5 records this repository's own
cell only as "glass vapor cell in a copper block" with no documented glass
type, and separately records Rb condensation visible on the cell windows
once unwrapped (PHOTO 2025-07-01), so the same kind of alkali film this
paper photoionizes is confirmed present on this repository's own glass. The
protective boundary they establish is wavelength: the effect requires light
under about 600 nm (2.1 eV, at or above the alkali work function), and it is
absent for an all-near-infrared three-photon scheme with no visible beam at
all. This programme drives the 5S1/2 to 6S1/2 transition directly with a single
colour, two 993 nm photons through a virtual level below 5P1/2, and detects
on the 795 nm cascade arm. Every wavelength on this bench sits far above
the 600 nm boundary, so by the paper's own criterion this photoionization
channel should not be active on this cell's windows. It is a reassurance
about the present single-colour drive, not a new open risk, though it would
become one if a visible beam were ever added to this apparatus (an
alignment or fluorescence-monitoring laser, for instance), and it adds a
second, independent, physical account of how a glass-vapor-cell wall
carrying a condensed alkali film can go electrically active under light,
alongside the He-permeation account already on record via
`docs/lit/feng2026.md`.
