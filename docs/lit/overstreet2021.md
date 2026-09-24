---
citekey: overstreet2021
type: article
authors:
  - Overstreet, Chris
  - Asenbaum, Peter
  - Kasevich, Mark A.
title: 'Physically significant phase shifts in matter-wave interferometry'
journal: Am. J. Phys.
volume: 89
number: 3
pages: 324
year: 2021
doi: 10.1119/10.0002638
arxiv: null
pdf: PDF_papers/atom_interferometry/Overstreet_2021_physically-significant-phase-shifts-matter-wave-interferometry.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/overstreet2021.md  # line-by-line against the held PDF, 2026-09-22. One page-citation error found and fixed (Systematics beam-size bullet, page 326 to 327). All equation numbers, page citations and the routing framing otherwise confirmed exactly.
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published Am. J. Phys. version, volume 89, issue 3,
    pages 324 to 332, March 2021, confirmed against the running header and the
    citation line on the first page. No arXiv posting is named anywhere in the
    PDF, so arxiv is set to null and not guessed.'
  - 'Sections 1 through 6, Appendices A, B and C, and the reference list
    (pages 324 to 332) read in full on 2026-09-22. Every displayed equation,
    Eqs. (1) through (47) and (A1) through (A5), was checked against the
    extracted text. Pages 324, 327, 328, 329, 330 and 331 were additionally
    rendered as page images at 150 dpi to confirm two sign and superscript
    drops in the text layer and to pin the exact page of every closely spaced
    equation cited below.'
verified_date: 2026-09-22
summary: >
  A formal, pedagogical treatment, with no new experimental data, of when a
  matter-wave interferometer's phase carries information that a classical
  position-tracking measurement could not have given. Working from a
  three-point classical accelerometer through the midpoint theorem to a
  semiclassical wavepacket treatment, the paper shows that a potential energy
  varying as degree two or lower across the two interferometer arms leaves the
  phase fully set by the classical midpoint trajectory, while a cubic or
  higher term produces an extra closed-form contribution, called the
  potential phase, that cannot be reduced to any set of position measurements.
  A worked example gives a nonzero phase shift from a purely time-dependent
  cubic potential that never deflects either arm at all. The closing
  discussion names the electromagnetic Aharonov-Bohm effect as a known case
  where this potential phase is nonzero, states that no experiment had yet
  observed a gravitational-potential version of it, and frames that
  observation as the first demonstration of gravitational time dilation
  inside a single quantum system.
loci: []
section: unsorted
---

# overstreet2021

VERIFIED. Held (published Am. J. Phys. PDF), 10 pages, pp. 324-332. Read in full on 2026-09-22.

## What it does

A formal, pedagogical paper, published in a physics-education journal, with no new experimental data and no error budget. It asks when the phase read out by a matter-wave interferometer is physically significant, meaning it carries information that a classical measurement of the interferometer arms' positions could never give, and when it is instead equivalent to such a classical measurement. The introduction surveys several formalisms already in use for computing this phase before the paper adopts one of them, a semiclassical wavepacket treatment, as its main tool.

The argument proceeds in stages. Section 2 sets up a classical three-point accelerometer: an object is tracked at three times and its acceleration is reconstructed from the three positions. Section 3 repeats the construction for a Mach-Zehnder atom interferometer using the midpoint theorem, a standard result that writes the interferometer phase as a sum over the effective positions of the two arms at each light-pulse time, and shows the resulting phase for a free-fall accelerometer contains exactly the same information as the classical three-point measurement. Section 4 goes beyond the midpoint theorem with a semiclassical treatment in which each wavepacket's center is expanded around its own trajectory, and writes the interferometer phase as a sum of a laser phase and a loop phase evaluated around the closed spacetime trajectory of the interferometer. Section 5 proves that this semiclassical phase equals the midpoint phase plus an extra term, called the potential phase, whenever the sampled potential energy has a spatial dependence higher than quadratic across the separation between the two arms. Section 6 discusses the physical meaning of that extra term, and two worked examples close the paper as appendices, one a numerical high-order potential and the other a state-dependent potential.

## The numbers

There are no experimental headline numbers. The content is a set of formal derivations, two illustrative figures cited from prior work, and one worked numerical example.

- Page 324: the introduction cites, as motivating applications of atom interferometry in general and not as results of this paper, a matter-wave test of the equivalence principle at the 10^-12 level and a fine-structure-constant measurement accurate to 0.2 parts per billion.
- Page 326, Eq. (8): the recovered Mach-Zehnder phase for a uniform acceleration g and pulse spacing T is k g T^2, matching the classical three-point accelerometer of Section 2 term for term.
- Page 327, Eq. (23): the closed-form potential phase is defined as a sum over odd powers n = 3, 5, 7, ... of the wavepacket separation, each term weighted by the nth spatial derivative of the potential energy at the midpoint trajectory and by the coefficient (n-1) / (2^(n-1) n!), integrated over the interferometer time.
- Page 329, Eq. (47): an equivalent closed form for the same quantity, written as the difference between the potential energy difference actually sampled by the two arms and the potential energy difference that would be inferred from their average, midpoint acceleration.
- Page 330: the closing paragraphs of the discussion state that the electromagnetic Aharonov-Bohm effect is a known case with a nonzero potential phase, and that no experiment had yet observed a nonzero potential phase induced specifically by a gravitational potential. Such an observation is framed as both a gravitational analogue of the Aharonov-Bohm effect and the first observation of gravitational time dilation in a single quantum system. Appendix A opens on the same page with a symmetric Mach-Zehnder interferometer evolving under zero potential, for which the phase is zero by construction (Eq. A3).
- Page 331, Eqs. (A4)-(A5): the same interferometer is then given a purely cubic, time-dependent potential that leaves both arm trajectories exactly unperturbed. The interferometer phase is nevertheless nonzero, phi = hbar^2 k^3 A T^4 / (12 m^3), for beamsplitter wavevector k, mass m, drift time T and potential coefficient A.

## Systematics

Not applicable. The paper carries no error budget and no experimental systematics of any kind. Checked specifically for the four classes below.

- Intensity or differential light shift sampled by the atoms: not discussed. The potential energy in the formalism is left fully generic, gravitational, electromagnetic or otherwise, and no laser intensity profile or light-shift term is ever specialized out of it.
- Finite size of the interrogation beam: not discussed as an error source. The only related statement is a formal validity condition for the semiclassical approximation itself, that the wavepackets on each arm must be sufficiently narrow in position and momentum for the higher-order terms of the wavepacket's own expansion to be negligible (page 327). That is a condition on the atomic wavepacket, not on a laser beam.
- Wavefront, curvature, aberration or flatness: not discussed anywhere in the paper.
- A source mass's position or alignment: not discussed. Gravity enters only as an abstract uniform or quadratic potential used to illustrate the midpoint theorem's own validity, citing an earlier gravity-gradient measurement for the quadratic case without re-analyzing its systematics.

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` is the record synthesizing what this record's own work can give to, and get from, the atom-interferometry community, for the application. This paper is lineage and conceptual context only. It feeds no number into this record's own model. Nothing in it is stated in a form this record's own Rb 5S-6S vapour-cell spectroscopy programme could adopt directly: its subject is the formal decomposition of an interferometer phase under a semiclassical approximation, not a light-shift distribution, a lineshape, or a systematic error budget of the kind this record works with.

The connection is institutional, not technical. The paper's own reference list cites, at two of its numbered entries, a gravity-gradient interferometer phase-shift measurement and a proposal for a gravitational analogue of the Aharonov-Bohm effect, both part of the same held collection of atom-interferometry papers behind the application. The paper's own closing discussion, summarized above, states that no experiment had yet observed a gravitational-potential version of that effect and frames the observation as an open target for the field, without describing any later attempt. The introduction also states that its analysis applies broadly across matter-wave interferometer types, naming guided interferometers alongside neutron interferometers and interferometers built from material gratings, though it develops no guided-geometry example of its own. For the application, the relevant fact is only that the wider atom-interferometry community has its own established vocabulary, the midpoint theorem, the laser and loop phase decomposition, the potential phase, for a question in the same family this record asks in a different form: when does an observable depend on more than a low-order, easily parametrized description of the underlying physics. No formula or numerical result here is reused.

## Limits

Read for content and internal consistency, not re-derived from first principles term by term. The closed-form potential phase, Eq. (23), and its equivalent form, Eq. (47), were checked against the rendered page images and against the paper's own stated equivalence between them. The intermediate derivation steps of Section 5, Eqs. (24) through (41), were checked against the extracted text and not independently re-derived. The reference list runs to 52 entries and was read for the two entries relevant to routing, not exhaustively cross-checked against their own sources.
