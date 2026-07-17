# Paper 2 — manuscript skeleton

**Status:** scaffold for Zohreh (lead on the fibre side) + Michelangelo, gated on
optical-nanofibre (ONF) data that has **not** been taken and a collaboration that
has **not** been agreed. This is the *narrative and physics* plan, not a draft.
It reuses the validated Paper-1 pipeline unchanged; the clean vapour-cell line
(Paper 1) is Paper 2's frequency and lineshape **reference**. See
`PAPERS_PORTFOLIO.md` for how P2 depends on the other campaigns.

*House rules as Paper 1: transition (sum) frequency everywhere (laser axis = ×½,
stated once); provenance tags on every number; no citation enters without the PDF
in hand.*

## 0. Framing decisions to settle first (not for the manuscript)

- **Scope.** The safe core is the **quantitative near-surface two-photon
  lineshape** — completing Gokhroo 2022, which observed the pushing profile but
  fit no model. The trapped-platform extensions in §VI are genuine but larger and
  should be labelled future work unless the data exist.
- **Platform.** OIST **optical nanofibre** (evanescent field, ~650 nm silica
  waist in the group's fibres), cold ⁸⁷Rb delivered by a MOT around the fibre —
  Gokhroo/Rajasree/Nieddu lineage. This is **not** a hollow-core fibre; keep the
  distinction (hollow-core is a different platform and a different paper).
- **Reference.** Paper 1's cell line is the Doppler-free reference — the same role
  Gokhroo's counter-propagating cell played. A fixed-lock-refined cell reference
  makes the strongest Paper 2; the archival reference still works.
- **Authorship / journal:** Síle's call.

## Title (candidates)

- *Quantitative near-surface two-photon lineshapes of Rb 5S–6S at an optical
  nanofibre*
- *Modelling the evanescent-field pushing dip in nanofibre two-photon
  spectroscopy of rubidium*

## Abstract (draft — honest, ~150 words)

Cold-atom two-photon spectroscopy at an optical nanofibre probes atoms in the
steep evanescent-field gradient, where the AC-Stark light shift is not a number
but a broad distribution and the collected line is pushed and distorted near the
surface. Gokhroo *et al.* (2022) observed this pushing profile on the Rb
5S₁/₂→6S₁/₂ line but did not model it. We port a drift-immune,
distribution-aware lineshape framework — developed and validated on the clean
vapour-cell line (Paper 1) — to the nanofibre geometry: the evanescent-mode
intensity profile sets the light-shift distribution, and the fitted line encodes
the near-surface shift and the pushing dynamics against the cell line as
reference. [Results TBD once ONF data exist.] The same fitted moments read the
in-fibre temperature, giving a self-calibrating thermometer for guided cold
atoms.

## I. Introduction

- Guided-atom spectroscopy: why the evanescent field is the *natural* home for the
  distribution-of-light-shifts physics — the intensity gradient is steep, so the
  light-shift distribution is large and the shape effects Paper 1 works to see in a
  gentle focus are unavoidable here.
- Prior art on this exact channel, all OIST lineage (PDFs in hand): **Nieddu 2019**
  (the cell 993 nm reference), **Rajasree 2020** (5S–6S excitation *through* the
  nanofibre with cold atoms; the spin-selection / polarization law on this line),
  **Gokhroo 2022** (the two-peak pushing profile near the fibre — *observed, not
  modelled*: DOI 10.1088/1361-6455/ac6bd4, "resonance-scattering-induced pushing"
  at hypothesis level, zero fitted lineshape, no Casimir–Polder content). The gap:
  **no quantitative near-surface lineshape model exists** — verified across every
  paper citing Gokhroo 2022.
- The contribution: a physics-anchored, drift-immune lineshape for the guided
  geometry, referenced to the clean cell line.

## II. The platform and what is different from the cell

- Evanescent HE₁₁ mode of the ~650 nm waist: the transverse intensity profile
  (the I²-weighted excitation shell, the fringe scale) and the **strong
  longitudinal field component** — the physics that Rajasree 2020 shows prevents a
  pure-circular null (minimum ~13% theory / ~25% observed).
- The light-shift distribution here is set by the *mode profile*, not a Gaussian
  focus — a different f(s) to derive, same machinery (`THEORY_NOTE.md` ramp
  formalism generalised to the evanescent profile).
- Near-surface: the atom-surface potential (van der Waals / Casimir–Polder) shifts
  and truncates the sampled shell — the extra ingredient the cell does not have and
  the source of the pushing dip.
- **Nearest-platform evidence (Pennetta et al. 2026, `LITERATURE.md` §8).** On this
  exact class of platform (Cs on a 450 nm nanofibre) the Rauschenbeutel group build a
  trap from **Casimir–Polder + surface-charge** forces against a blue-detuned field —
  the atom–surface potential §IV must model, now quantified rather than hypothesised —
  and reach a record Ramsey T₂\* = 17.8 ms **precisely by suppressing the
  motional-state-dependent differential light shift** (holding atoms in low-light
  regions). That is the two pillars of this paper demonstrated on the platform: the
  near-surface force is real and harnessable, and the guided-mode differential light
  shift is the coherence-limiting systematic the moment method (§III, §V–VI) is built
  to read.

## III. Method transplanted (the reuse that de-risks this)

- The Paper-1 pipeline (M0–M16) ingests ONF traces **unchanged** — the same
  ruler/axis, noise model, composite lineshape fit, moment/bounds machinery.
- **In-fibre thermometry from the moments.** The drift-immune centred moments are
  a transit/temperature readout: transit ∝ v̄/w, so the fitted width and moments
  give the in-fibre temperature *without* a separate thermometer — a
  self-calibrating diagnostic for guided cold atoms (the same moments that read
  the light-shift distribution read T).

## IV. The near-surface lineshape (the core result)

- Derive f(s) for the evanescent mode profile; convolve with the transit kernel
  for atoms crossing the shell and the cell-referenced natural + laser widths.
- **The surface term is two parts, not one — Casimir–Polder + a calibratable
  electrostatic component.** Pennetta et al. 2026 (`LITERATURE.md` §8) show that on
  this exact platform the atom–surface potential is **CP *plus* electrostatic
  attraction from surface charges on the silica**, not CP alone. So the surface
  shift folded into the lineshape must carry (i) the universal CP term (near-field
  C₃/z³ crossing to the retarded C₄/z⁴ — the regime and z-scaling Ton, Kestler,
  Steck & Barreiro 2026 measure directly, `LITERATURE.md` §9), and (ii) a
  **device- and time-dependent electrostatic term** that must be calibrated per run
  and treated as a systematic, not a universal constant. This upgrades the model
  from a single vdW shift to a two-component surface potential and is the honest
  form of the "near-surface shift" the fit extracts.
- **Read the surface shift *from the line*, as a distribution.** The template is
  established: Ton et al. 2026 extract a kHz CP shift purely from the spectroscopic
  lineshape (Sr, 189 nm from a dielectric); the near-surface shift here is likewise a
  *distribution* over the atoms' distance-from-surface, read by the same moment
  machinery that reads the light-shift distribution — the two inhomogeneities are
  handled by one method. (To verify before citing: Dutta et al. and Sargsyan/Sarkisyan
  on higher-order-CP / selective-reflection lineshapes, `LITERATURE.md` §9.)
- **A feasibility constraint to respect:** the evanescent probe itself heats the
  trapped atoms, so near-field probing is inherently transient (Piotrowski/
  Rauschenbeutel 2026, to verify) — the measurement window and probe power are bounded.
- Fit the pushing dip vs power and detuning; extract the near-surface shift and
  test the resonance-scattering-pushing hypothesis quantitatively against the
  data — the quantitative completion of Gokhroo 2022.
- Cell line (Paper 1) as the reference that removes the laser and axis systematics.

## V. Polarization control at the nanofibre

- The two-photon rate ∝ (degree of linear polarization)² and the σ-configuration
  selection rules (Paper 1 §8.1.1) carry over — but the **longitudinal field
  modifies them**: the "circular" null is a minimum, not a zero (Rajasree 2020).
- This is both a systematic (the polarization at the atom is not the input
  polarization) and a handle (polarization tomography of the guided mode).

## VI. Extensions unique to the trapped, guided platform (future work / upside)

*These are the measurements the hot cell structurally cannot do (`PLAN.md`
§8.1.2) and the guided cold platform can — the distinctive Paper-2+ upside.*

- **The 6S vector dynamic polarizability and the differential g_J(6S−5S).** m_F
  state preparation and a defined field are impossible to maintain in a hot,
  collisional cell but natural in a trapped, cold, field-controlled sample. With
  circular light and a prepared/stretched m_F, the vector light shift ∝ m_F becomes
  a first-order, measurable shift → the 6S vector polarizability, a quantity no
  cell measurement can reach.
- **Travelling vs standing wave in the fibre.** Split the 993 nm drive with a 1×2
  fibre coupler and inject from both fibre ends: a controlled switch between a
  single-pass travelling wave and a standing wave in the guided mode — the
  in-fibre realisation of the fringe/standing-wave physics catalogued in Paper 1
  (`THEORY_NOTE.md` §6), and the basis for in-fibre interferometry.
- **Incommensurate-lattice / arcsine light-shift distribution** for a two-colour
  guided lattice — the guided analogue of the triangular ramp, a distinct f(s) the
  same moment machinery reads.
- **The method's reach beyond the fibre — optical-lattice atom interferometry.**
  The inhomogeneous light-shift distribution the fibre makes unavoidable is the
  *same* systematic that limits coherence in held-atom / optical-lattice atom
  interferometers, where the differential light shift of the trapping lattice
  dominates the interferometer phase. The drift-immune moment method plus the
  magic/tune-out-wavelength toolkit (M16) are directly a **characterisation and
  trap-design** capability there — a distribution-aware readout of the very shift
  those experiments fight, and the wavelengths that null it.
- **Atoms in a plasmonic near-field (a further near-surface extension).** A
  metal-coated fibre or a plasmonic nanostructure steepens the near-field, so the
  light-shift distribution f(s) is larger and more sharply shaped, the decay is
  Purcell-modified (a position-dependent linewidth), and the surface shift can be
  resonantly enhanced — the near-surface lineshape program of §IV with plasmonic
  enhancement. The lineshape-decomposition toolkit is in fact domain-general:
  single-particle plasmon-linewidth spectroscopy separates the homogeneous
  (single-particle damping) from the inhomogeneous (ensemble size/shape) width
  exactly as Doppler-free two-photon separates natural/collisional from Doppler
  here — the method travels even where no atom is involved. *(Forward-looking and
  deliberately hedged: a lateral reach, not a Paper-2 claim.)*

## VII. Status, dependencies, and risk

- **Needs ONF data + a collaboration** that has not been approached; gated on the
  fibre work, not on the analysis (which is ready).
- **Better with a fixed-lock-refined cell reference** (Paper 1 full) but workable
  on the archival reference.
- Risk is set by the ONF result, not by the method: if the dip is clean and the
  near-surface shift resolvable, §IV is a solid paper; §VI is the upside.

## Reference anchors (PDFs in hand; BibTeX in `references.bib`, ledger in `LITERATURE.md`)

- `nieddu2019` — the cell 993 nm reference (same line, same lens lineage).
- `rajasree2020spin` — 5S–6S through the nanofibre; the polarization law and the
  longitudinal-field limit on the circular null.
- `gokhroo2022` — the observed pushing dip this paper models (title "light
  fields"; DOI 10.1088/1361-6455/ac6bd4).
- Paper 1 (`PAPER1_SKELETON.md`, `THEORY_NOTE.md`) — the method, the ramp
  formalism, and the cell reference.

*Cross-refs: `PAPERS_PORTFOLIO.md` (scenario map), `PLAN.md` §8.1.2 (why the
vector/field physics is a guided-platform measurement, not a cell one),
`THEORY_NOTE.md` (ramp/standing-wave formalism to generalise).*
