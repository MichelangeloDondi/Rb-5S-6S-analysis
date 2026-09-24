---
citekey: carle2023
type: article
authors:
  - Carlé, C.
  - Keshavarzi, S.
  - Mursa, A.
  - Karvinen, P.
  - Chutani, R.
  - Bargiel, S.
  - Queste, S.
  - Vicarini, R.
  - Abbé, P.
  - Abdel Hafiz, M.
  - Maurice, V.
  - Boudot, R.
  - Passilly, N.
title: 'Reduction of helium permeation in microfabricated cells using aluminosilicate glass substrates and Al2O3 coatings'
journal: J. Appl. Phys.
volume: 133
number: 21
pages: 214501
year: 2023
doi: 10.1063/5.0151899
arxiv: '2303.13927'
pdf: PDF_papers/Carle_2023_helium-permeation-aluminosilicate-Al2O3-microfabricated-cells.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:2303.13927v1 preprint (24 Mar 2023); journal, volume, article number and
    DOI are Crossref''s record of the published article, checked 2026-09-22 (the arXiv page links the
    DOI). Read in full on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  Helium leaving 13 sealed Cs-He microcells, read over tens of days from a CPT clock's pressure shift
  at 70 C, follows a single exponential toward the atmosphere's 3.98 mTorr: the time constant is 75
  days through borosilicate windows and 35 000 days through aluminosilicate ones, 20 nm of Al2O3 cuts
  the borosilicate rate 110-fold and the aluminosilicate one 5.8-fold, and three temperatures give the
  aluminosilicate an activation energy near 0.49 eV. Cites helium permeation as the limit of a Rb 778
  nm two-photon clock. The exponential sealed-cell law with measured time constants and its Arrhenius
  slope.
loci:
  - methods/02
section: method-anchors
---

# carle2023

VERIFIED against the held preprint (scope in `verify_flags`).

## The law and the method

The buffer-gas pressure in a sealed cell relaxes exponentially to the outside partial pressure, with a time constant equal to the cell volume times the window thickness over the permeation constant, the window area and a reference pressure (their Eqs. 1 and 2). The outside helium pressure is the atmosphere's 3.98 mTorr. The pressure is read from the Cs clock transition's buffer-gas shift with its linear and quadratic temperature coefficients (Eq. 3), on a table-top CPT clock whose rotating platform cycles six cells through one beam, all at 70 C, against a hydrogen maser (Fig. 1). The cells were filled with helium, so the clock frequency falls as it leaves.

## What it finds

Verbatim: "The corresponding time constant τ is 75 ± 6 days, whereas it is extended to 35000 ± 3000 days in ASG-based cells." The permeation constants are 5.9 +- 0.7 x 10^-19 and 1.3 +- 0.2 x 10^-21 m^2 s^-1 Pa^-1 for borosilicate (Borofloat 33) and aluminosilicate (Hoya SD2), and a Cs-Ne borosilicate cell set the setup's background at -0.3 Hz per day against -1182 Hz per day for Cs-He in borosilicate (Fig. 2). With 20 nm of Al2O3 by atomic layer deposition on the inner face of the windows, the abstract reports, verbatim: "The permeation through BSG is thereby reduced by a factor 110 whereas the one through ASG is decreased by a factor up to 5.8 compared to uncoated substrates." Coated cells scatter more, which the authors attribute to inhomogeneous deposition or damage during fabrication and dispenser activation (Fig. 3). Measuring one aluminosilicate cell at three temperatures gives an Arrhenius slope of 5680 K, an activation energy near 0.49 eV against 0.52 eV quoted for Corning 1720 (Fig. 5).

The introduction ties the effect to this record's family of lines, verbatim: "For instance, the limitation of the long-term stability of an optical clock based on the Rb 778 nm two-photon transition has been attributed to He permeation". It adds that contaminants in microcell optical references broaden the optical resonance.

## Use in this record

The analysis side's permeated-gas term needs a law and its parameters. This paper measures the law's form, a single exponential to the outside pressure with a time constant set by geometry and a permeation constant, and gives that constant an Arrhenius temperature dependence. For a glass-blown cell of the 2025 kind the time constant is set by its own volume, wall thickness and glass, and the helium's pressure broadening and shift of the 5S to 6S line are the analysis side's to carry. What the paper supplies is the functional form in time, including the approach to equilibrium that a linear law misses, and the evidence that the effect is measurable on a two-photon rubidium line.

Related on this shelf: `dellis2016` (helium entering a cell, the same readout), `carle2024` (the coating's thickness dependence), `feng2026` (helium equilibration in a Rb 778 nm fibre-laser clock).
