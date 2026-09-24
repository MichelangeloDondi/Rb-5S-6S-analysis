---
citekey: carle2024
type: article
authors:
  - Carlé, C.
  - Mursa, A.
  - Karvinen, P.
  - Keshavarzi, S.
  - Abdel Hafiz, M.
  - Maurice, V.
  - Boudot, R.
  - Passilly, N.
title: 'On the reduction of gas permeation through the glass windows of micromachined vapor cells using Al2O3 coatings'
journal: J. Appl. Phys.
volume: 136
number: 8
pages: 085102
year: 2024
doi: 10.1063/5.0213432
arxiv: '2404.07144'
pdf: PDF_papers/Carle_2024_gas-permeation-Al2O3-coated-glass-windows-vapour-cells.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:2404.07144v1 preprint (10 Apr 2024); journal, volume, article number and
    DOI are Crossref''s record of the published article, checked 2026-09-22. Read in full on
    2026-09-22.'
verified_date: 2026-09-22
summary: >
  The companion to carle2023: helium permeation through borosilicate windows coated with 5 to 40 nm of
  Al2O3, read from a CPT clock at 70 C, drops by almost two orders of magnitude between 10 and 20 nm
  and barely further at 40 nm, whose best cell reaches 1.4 times the uncoated aluminosilicate rate;
  neon permeation falls likewise, giving a Cs-Ne clock 4e-12 at one day. It restates the 20 nm
  reduction on borosilicate as 130-fold where carle2023 reports 110. The table of per-cell time
  constants a permeation prior can be read against.
loci:
  - methods/02
section: method-anchors
---

# carle2024

VERIFIED against the held preprint (scope in `verify_flags`).

## What it measures

Ten further Cs-He microcells with borosilicate (Borofloat 33) windows coated on their inner faces with 5, 10 or 40 nm of Al2O3 join the uncoated and 20 nm cells of `carle2023`. Each is followed for weeks on the same six-cell CPT clock at 70 C, and the time constant of the exponential decay of the clock frequency gives the permeation constant (their Section II, Fig. 1 and Table I). Neon-filled Cs cells with 20 nm coatings test the same barrier for the buffer gas itself (Section III).

## What it finds

Verbatim: "Note that a significant improvement by almost two orders of magnitude is observed between 10 nm and 20 nm." And at the thickest, verbatim: "Interestingly, we do not observe a relevant reduction of the permeation rate for a thickness of 40 nm, in comparison with layers of 20 nm." The time constants run from 62 to 66 days for uncoated windows to 11 400 to 21 200 days at 40 nm, whose best cell gives a permeation constant of (2.0 +- 0.2) x 10^-21 m^2 s^-1 Pa^-1, 1.4 times the uncoated aluminosilicate value of the earlier paper (Table I, Fig. 2). For neon, the coated cells drift about 0.02 Hz per day against -0.28 Hz per day uncoated, and one coated cell under a Ramsey-type interrogation reaches a fractional stability of 4 x 10^-12 at 4 x 10^4 s, which the authors attribute to light shifts, not permeation (Figs. 3 and 4). The introduction notes that the impact of helium permeation on the long-term stability of both microwave and optical rubidium cell standards has been emphasised in earlier work.

One discrepancy between the two papers of this group is recorded, not resolved: this paper states that the earlier study found the 20 nm coating reduced the helium rate through borosilicate by a factor of 130, where `carle2023`'s own abstract, text and conclusion give 110.

## Use in this record

Beside `carle2023` this supplies a table of measured per-cell time constants with their scatter among nominally identical cells, a few per cent for the uncoated ones and up to nearly a factor of two for the 40 nm ones, which bounds how tightly a prior on a permeation parameter can be borrowed from nominally similar glass. Its cells are microfabricated and their glass is not the 2025 cell's, so its constants are not the analysis side's parameters. The scatter among identical cells is the transferable reading.

Related on this shelf: `carle2023`, `dellis2016`.
