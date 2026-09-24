---
citekey: hohensee2012
type: article
authors:
  - Hohensee, Michael A.
  - Estey, Brian
  - Hamilton, Paul
  - Zeilinger, Anton
  - Müller, Holger
title: 'Force-Free Gravitational Redshift: Proposed Gravitational Aharonov-Bohm Experiment'
journal: Phys. Rev. Lett.
volume: 108
number: 23
pages: 230404
year: 2012
doi: 10.1103/PhysRevLett.108.230404
pdf: PDF_papers/atom_interferometry/Hohensee_2012_force-free-gravitational-redshift-aharonov-bohm-proposal.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/hohensee2012.md  # line-by-line against the held PDF, 2026-09-22, six content corrections found and fixed (an imprecise saddle-point description, a mis-cited page, an incorrect multiply-connected-spacetime claim removed, a backwards with/without-masses removal claim, and two related tightenings), distinctness from hohensee2011 confirmed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published Phys. Rev. Lett. 108, 230404 (2012) article
    (pdfinfo: Acrobat Distiller 6.0.1 producer, Arbortext Advanced Print
    Publisher creator, 5 pages), with no arXiv watermark, identifier or
    metadata field anywhere in the file, so arxiv is left unset instead of
    guessed. Title, authors, affiliations, DOI, volume, issue and article
    number all confirmed directly against the printed first page and the
    page-1/page-4 running footers (0031-9007/12/108(23)/230404(5)), read from
    the PDF only, no web search.'
  - 'All 5 pages read in full on 2026-09-22, including every numbered
    equation (1)-(10), Table I and the reference list. Pages 1 and 4
    additionally rendered at 150 and 300 dpi and read as images, because the
    extracted text layer substitutes plain keyboard glyphs for hbar, omega and
    other symbols throughout (for example "@" for hbar-cross, "!" for omega,
    "1: 1:1" for a ratio "1 : -1 : 1"), which would otherwise mangle every
    equation and every Table I entry.'
verified_date: 2026-09-22
summary: >
  A Berkeley proposal for a laboratory atom-interferometer test of the
  gravitational redshift that arises with no classical force acting on the
  atoms while it does, framed as a gravitational analog of the
  Aharonov-Bohm effect. Two spherical source masses of laboratory size are
  moved into place so that two held wave packets sit at saddle points of the
  combined potential, where the force vanishes but the potential itself
  still differs between the two points, and the interferometer is predicted
  to register a phase of about 0.3 rad for cesium atoms held 1 second. The
  paper's own systematics table sorts these into terms common to both
  interferometer arms that cancel on their own, terms independent of the
  source masses that cancel by comparing runs with and without them, and a
  few small residual terms tied to the masses' own position, magnetism and
  the potential's curvature that are simply computed and bounded. Nothing in
  it is a measurement, only a design study with an error budget.
loci: []
section: unsorted
---

# hohensee2012

VERIFIED. Held (the published Phys. Rev. Lett. PDF), 5 pages, read in full on 2026-09-22.

## What it does

The paper proposes a benchtop atom-interferometer test of the gravitational redshift that requires no classical force to act on the atoms while the phase builds up, and it frames the result as a gravitational counterpart of the Aharonov-Bohm effect from electromagnetism, where a charged particle's phase depends on a potential even where the field itself, and so the force, vanishes along its path (p. 1). The proposed apparatus places two identical source-mass spheres (radius R = 1 cm, density rho = 10 g/cm^3, separated by L = 3 cm) so that their combined gravitational potential has two saddle points, at the geometric centre and near one of the spheres, separated by a distance s = 1.38 cm (p. 1, Fig. 1). An atom is split into a superposition of two wave packets, each carried by a moving optical lattice to one of the two saddle points and held there for a time T (Fig. 2, p. 2). Because the wave packets sit at saddle points and are much smaller than the masses, the masses apply no force or potential gradient to them once in place, yet the potential itself differs between the two points, so a relative phase still accumulates (Eqs. 2-4, p. 2). The paper identifies that phase with the gravitational redshift between two clocks, each ticking at the atom's own Compton frequency omega_C = mc^2/hbar, held at the two locations (Eqs. 5-7, p. 2), and derives the same result from a relativistic path-integral treatment of the atom as a clock moving through the weak-field metric (Eq. 8, p. 3). The same interferometer is proposed to separately measure a time-dilation phase from moving one wave packet periodically, which the paper distinguishes from the redshift phase so that the two effects, and the equivalence between them, are each confirmed on their own (p. 4). The authors state their aim as "the first demonstration of a force-free gravitational redshift" (p. 4). They are explicit that this is a weaker condition than some other definitions of a gravitational Aharonov-Bohm effect ask for: a vanishing force on the atom is equivalent to vanishing Christoffel symbols in the atom's own rest frame, while other definitions also require a vanishing Riemann tensor, which does not hold in this setup, so a rapidly moving particle could still feel a force even though the atom held at rest at either saddle point feels none (p. 4).

## The numbers

| quantity | value | page |
|---|---|---|
| source-mass radius R, density rho | 1 cm, 10 g/cm^3 | p. 1 |
| mass separation L, saddle-point splitting s | 3 cm, 1.38 cm | p. 1 |
| Compton frequency omega_C/(2 pi), for cesium | 3x10^25 Hz | p. 1 |
| potential difference at L = 3xR | Delta U = 1.11 rho G s^2 | p. 1 |
| potential difference, optimised geometry (L = 2.61xR, s = 1.14xR) | Delta U = 1.17 G rho s^2 | p. 1 |
| Delta U / c^2 at the stated geometry | about 1.6x10^-27 | p. 1 |
| predicted signal phase, T = 1 s (Eq. 1, Table I line 1) | 0.3 rad | p. 2, p. 4 |
| target total error for a 10-sigma test of Eq. (1) | below about 30 mrad | p. 4 |
| assumed hold / coherence time | about 1 s | p. 1, p. 4 |
| time-dilation demonstration phase (oscillation amplitude 0.1 um, 1 kHz) | 207 rad per second | p. 4 |

Eq. (1) gives the predicted phase explicitly, for the geometry L = 3xR, R = 0.72s: delta phi_G = 0.16 (s/cm)^2 (rho / 10 g cm^-3) (m / m_Cs) (T/s), where m_Cs is the mass of a cesium atom (p. 2). The paper also states that reaching a laboratory-scale signal of this kind by atomic clocks alone, without matter-wave interferometry, would need kilometre-sized source masses (p. 3).

## Systematics

The paper's own error budget is Table I (p. 4), evaluated at the Fig. 1 geometry and T = 1 s, with each line marked (*) if it is common to both interferometer arms and cancels, (**) if it is independent of the source masses and removable by comparing runs with and without them, or unmarked if neither applies.

**Intensity or differential light shift the atoms sample.** Present, and the largest named systematic after the signal itself. The optical lattice that holds and moves the two wave packets contributes a common-mode lattice-shift term (V0 T / hbar, 6x10^5 rad, marked *, cancels) and a residual differential lattice shift of 0 +/- 0.02 rad (marked **), which the text attributes to diffraction of the Gaussian lattice beam if its waist sits away from the saddle point, formula -2 V0 T xw s / (zR^2 hbar), assuming V0/h = 100 kHz and xw = 0 +/- 1 mm (p. 4). At 0.02 rad this differential shift is about 7 percent of the 0.3 rad signal and is comparable in size to the paper's own 30 mrad total-error target.

**Finite size of the interrogation beam.** Present, folded into the same term. The lattice beam's transverse profile enters through its 1/e^2 intensity radius w0 = 0.5 mm and its Rayleigh range zR = pi w0^2 / lambda, with lambda = 852 nm, both of which set the size of the differential lattice shift above (p. 4). Separately, the force-free argument itself rests on a stated qualitative condition, that the wave packet be much smaller than the source masses, so that the masses apply no potential gradient across it (p. 2). No numbered budget line is attached to that condition on its own.

**Wavefront (curvature, aberration, flatness).** Not present as a laser-wavefront-quality line of the kind seen in retroreflection-based light-pulse gravimeters, where mirror flatness or beam aberration sets a budget term. The two Table I lines nearest in name, the quadratic potential shift (Eq. 9, about 2x10^-6 rad/s) and the dispersive phase shifts from Earth's gravity and from the field masses (Eq. 10, 0.26 rad and 2x10^-8 rad), concern the curvature of the gravitational potential itself, which can shift the atoms' trapped motional frequencies, and a residual classical force displacing the atoms' mean position inside the lattice, not the optical wavefront quality of the interrogation beam (p. 3-4). The distinction is the paper's own: both terms are derived from the source masses' potential and its gradient, never from a stated imperfection of the lattice beam's phase front.

**Source mass's position or alignment.** Present and central to the whole design, not a side term. The predicted signal itself is set by the masses' radius, density, separation and the resulting saddle-point splitting s through Eq. (1) (p. 2), and the masses are proposed to be moved into place and back out again with trajectories chosen to produce no significant force on the wave packets at any time (p. 2-3). Two further Table I lines tie directly to the masses' own presence, and neither carries a marking that says it cancels or subtracts out: a dispersive shift from an imperfectly cancelled force from a single source mass (Eq. 10, 2x10^-8 rad) and a Zeeman shift from the masses' own residual magnetism (2x10^-5 rad for an assumed 1 mG field, minimised by using m_F = 0 states and suppressing the masses' iron content to parts per million so they are not ferromagnetic) (p. 4). Both are simply computed and shown to be small, not removed by any procedure. Earth's own background phase (gs omega_C T / c^2, 2.8x10^8 rad) is far larger than either, but that term is marked as independent of the source masses (Table I line 2), which is exactly the class of term the paper proposes to remove by comparing the interferometer phase with and without the masses in place, leaving only the phase that depends on the masses themselves (p. 3-4).

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` is the record that reads what the atom-interferometry community can give this work and take back from it. This proposal feeds no number into this record's own Rb 5S-6S vapour-cell model. It proposes a gravitational-redshift and gravitational-Aharonov-Bohm test built from source masses and optical lattices, on a different physical system and a different kind of measurement, and none of its numbers set a parameter, a prior or a systematic term anywhere in this repository's code. It is held as lineage, and as calibration of the audience the application addresses. Holger Müller is the last-listed author of this paper and also the last-listed author of the atomic-gravitational-wave design study already on the shelf (`docs/lit/hohensee2011.md`), so the two notes mark two points of one Berkeley matter-wave-interferometry programme, a kilometre-scale gravitational-wave detector design and this benchtop force-free redshift test.

## Limits

The relativistic path-integral derivation of the phase from the weak-field metric tensor (Eq. 8, p. 3) is read but not further unpacked here beyond the one line above, since it sets no number this shelf uses. The reference list (p. 5) was read only to confirm the paper carries no arXiv self-identifier, not analysed reference by reference. Two systematics dismissed in one sentence each, and not elaborated on above because neither is one of the four classes asked for, are gravitomagnetic forces from the source masses' own motion, suppressed by at least one power of velocity over the speed of light, and phase shifts on the lattice light itself from the source masses' potential, both stated to be negligible (p. 3-4). This is a proposal with no data section, so there is no measured value anywhere in it to compare against the predicted 0.3 rad signal.
