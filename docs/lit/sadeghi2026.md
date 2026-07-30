---
citekey: sadeghi2026
type: article
authors:
  - Sadeghi, M.
  - Crump, W.
  - Parkins, S.
  - Hoogerland, M. D.
title: 'Long-distance feedback to cold atoms coupled to an optical nanofiber'
journal: null
volume: null
pages: null
year: 2026
doi: null
arxiv: '2412.01099'
pdf: PDF_papers/Sadeghi_2026_cold-Cs-ONF-cascaded-fluorescence-64m.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held as arXiv v1 (2412.01099v1, 2 December 2024), whose title is
    "Long-distance feedback to cold atoms coupled to an optical nanofiber". The
    current arXiv listing carries a DIFFERENT title, "Long-distance cascaded
    fluorescence of cold Cesium atoms coupled to an optical nanofiber", so the
    paper was retitled between versions -- check which title the published
    version uses before citing.'
  - 'A journal reference of Phys. Rev. A 113, 023719 (2026) reached this
    repository from a secondary summary. The arXiv record shows no journal-ref
    and the held v1 is a preprint, so the citekey year and the journal fields
    are UNCONFIRMED. Verify before formal citation.'
verified_date: 2026-07-30
summary: >
  Cold Cs coupled to an optical nanofibre, with spontaneously emitted photons
  sent down 64 m of fibre, reflected by a Bragg mirror, and returned to the same
  ensemble -- a delayed-feedback / cascaded geometry aimed at quantum
  networking. Relevant here for its lineshape rather than its networking: the
  observed linewidth is ~16 MHz against a 5.2 MHz natural width, the fit gives
  an additional Gamma_0 = 8.44(80) MHz beyond Gamma = 6.45(1.17) MHz attributed
  to surface interactions, magnetic gradients and laser width, and the shift
  between direct and returned fluorescence GROWS WITH EXCITATION POWER at
  (0.25 +- 0.06) MHz slope, which the authors attribute to surface-shifted
  atoms being excited preferentially at higher intensity. The nearest
  competitor to Paper 2's ONF lineshape programme.
loci:
  - P2
section: oist-lineage
---

# sadeghi2026

**Read 2026-07-30** from the held arXiv v1. Auckland (Dodd-Walls Centre).

**What it is.** Not primarily a lineshape paper. Photons spontaneously emitted
by a strongly driven laser-cooled Cs ensemble into an optical nanofibre travel
down ~64 m of conventional fibre, reflect from a fibre-Bragg-grating mirror, and
return to interact with the same ensemble after a delay — a one-way cascaded /
delayed-feedback atom–photon interface, motivated by distributed quantum
computing.

**Why it matters to Paper 2 anyway, and this is the part to cite.** The ONF
lineshape they report is dominated by things that are not the atom:

- observed linewidth **~16 MHz** against a natural **5.2 MHz**;
- fitting Γ and an additional Γ₀ gives **Γ = 6.45 ± 1.17 MHz** and
  **Γ₀ = 8.44 ± 0.80 MHz**, the latter attributed to surface interactions,
  magnetic-field gradients and laser linewidth together;
- the frequency shift between direct and returned fluorescence **increases with
  excitation power**, slope **(0.25 ± 0.06) MHz**, which they explain as atoms
  whose resonance is surface-shifted being excited preferentially as the drive
  strengthens.

That last mechanism is a *power-dependent shift arising from a spatially varying
potential selecting which atoms are excited* — structurally the same kind of
statement this programme makes about the AC-Stark ramp, in the geometry Paper 2
targets, and with the roles of the two effects reversed: for them the surface
potential is the nuisance, for us the intensity distribution is the signal. A
Paper-2 lineshape treatment has to account for their Γ₀ before it can claim to
have modelled anything.

**A correction to how this repository described it.** The intake files call it
"power-dependent surface shift … atoms redistributing in the van der Waals
range". On the abstract alone that looked wrong, because the abstract is about
the networking result. Reading it, the intake description is essentially right —
the effect is there in the paper, with the numbers above. The initial suspicion
is recorded because it is a reminder that an abstract can foreground a different
paper than the one you need.

**The lead it turned up, which may matter more than the paper.** Its ref [25] is
B. Patterson, P. Solano, P. Julienne, L. Orozco and S. Rolston, *"Spectral
asymmetry of atoms in the van der Waals potential of an optical nanofiber"*,
Phys. Rev. A **97**, 032509 (2018). Lineshape **asymmetry** produced by a
distributed potential, in the ONF geometry — a direct precedent for Paper 2's
central object, and absent from these holdings entirely when this note was
written. **Obtained and read the same day**: see
[patterson2018](patterson2018.md). It confirms the reasoning that made
[wieman1987](wieman1987.md) matter for Paper 1, and it turns this paper's Γ₀ into
part of a pattern — Patterson report the same ~2 MHz of unexplained excess width
in Rb that this paper reports in Cs, and say explicitly that they cannot account
for it.
