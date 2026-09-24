---
citekey: dellis2016
type: article
authors:
  - Dellis, A. T.
  - Shah, V.
  - Donley, E. A.
  - Knappe, S.
  - Kitching, J.
title: 'Low helium permeation cells for atomic microsystems technology'
journal: Opt. Lett.
volume: 41
number: 12
pages: 2775-2778
year: 2016
doi: 10.1364/OL.41.002775
arxiv: null
pdf: PDF_papers/Dellis_2016_low-helium-permeation-aluminosilicate-vapour-cells.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the published typeset letter from the NIST Time and Frequency Division''s
    publication archive (tf.nist.gov/general/pdf/2830.pdf), fetched 2026-09-22; journal, volume, pages
    and DOI read from the letter and confirmed in Crossref. Read in full on 2026-09-22. The text layer
    drops the equals signs of Eq. 1 and its time constants, so no equation is quoted.'
verified_date: 2026-09-22
summary: >
  Helium entering a sealed 87Rb cell is read from the drift of the CPT clock frequency through its
  pressure shift: through Pyrex windows the permeation constant is about 3e-10 cm^2/s at 96 C and
  follows an Arrhenius law over 96 to 116 C, while an anodically bondable aluminosilicate glass is at
  least a thousand times lower at room temperature. With the time-lag solution for the pressure rise
  behind a window. The measured form of the sealed-cell law for a permeating gas, and the method of
  reading it off a line's own shift.
loci:
  - methods/02
section: method-anchors
---

# dellis2016

VERIFIED against the held letter (scope in `verify_flags`).

## The problem and the method

The abstract, verbatim: "A significant source of vacuum contamination is the permeation of gases such as helium (He) through the walls of the cell." A cell of silicon and glass, filled with 77 Torr of Ar and 125 Torr of N2 with 87Rb, sits in a vacuum chamber that is then filled with helium, and the helium arriving inside is read from the drift of the ground-state hyperfine clock frequency, whose helium pressure shift the letter takes as 108.9 x 10^-9 per Torr in fractional terms (Fig. 1). The pressure rise behind a window of area A and thickness d is the classical diffusion solution, with a time lag set by d^2 over the diffusion constant and a permeation constant K equal to the diffusion constant times the solubility, the diffusion constant following an Arrhenius law. For a degassed window and long times it reduces to a linear rise after the time lag (their Eq. 1).

## What it finds

For Pyrex windows at 96 C and 0.65 atm of helium, the fractional drift of 7.6 x 10^-9 per hour gives K of about 3 x 10^-10 cm^2/s. Measurements at 106 and 116 C agree with an Arrhenius law (Fig. 2). For the aluminosilicate glass, Hoya SD2, with 15 to 20 per cent Al2O3, K is 1.4 x 10^-12 cm^2/s at 91 C and 6 x 10^-12 cm^2/s at 110 C, the second from a heat-and-measure cycle because the resonance's contrast fell at high temperature (Fig. 3). Verbatim: "The permeation rate of the ASG under test is at least 1,000 times lower than that of Pyrex." The authors flag their own low-temperature point, verbatim: "Because it is possible that the laser power was drifting slightly during the measurement at 91°C, it is possible that some or all of the measured frequency change over time is due to the slowly-varying AC Stark shift." Scaled by an assumed activation energy, verbatim: "At 25°C the permeation rate of ASG is at least three orders of magnitude lower than that of Pyrex." And on the initial state of the glass, verbatim: "Window degassing is important to prevent rapid pressure rise after fabrication."

## Use in this record

The owner's programme lists the rate of permeation of gases over time and the cell's sealing date among the quantities the experiment should calibrate itself, and the analysis side's likelihood now carries a permeated gas's sealed-cell law. This letter is the measured form of that law: a pressure that rises linearly after a time lag, with a rate following an Arrhenius law in the window temperature, read here from a clock line's own pressure shift, which is the same inference the 5S to 6S line's width and shift would make. Its numbers are for helium through Pyrex and one aluminosilicate at 91 to 116 C. The 2025 cell's glass, its fill and its history are the analysis side's to state, and a permeation constant for them does not follow from this letter.

Related on this shelf: `carle2023` and `carle2024` (the same method on microfabricated cells, with Al2O3 coatings), `feng2026` (a Rb two-photon clock whose helium equilibration sets its long-term drift).
