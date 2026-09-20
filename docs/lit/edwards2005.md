---
citekey: edwards2005
type: article
authors:
  - Edwards, C. S.
  - Barwood, G. P.
  - Margolis, H. S.
  - Gill, P.
  - Rowley, W. R. C.
title: 'Development and absolute frequency measurement of a pair of 778 nm two-photon rubidium standards'
journal: Metrologia
volume: 42
pages: 464--467
year: 2005
doi: 10.1088/0026-1394/42/5/018
arxiv: null
pdf: PDF_papers/Edwards_2005_778nm-two-photon-rubidium-standards-absolute-frequency.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Page 1 (abstract, introduction and the start of the apparatus description) read against the
    PDF on 2026-09-20. The systematic-shift budget and the absolute-frequency-measurement
    sections, the bulk of the four-page paper, are not read.
verified_date: null
summary: >
  Characterizes a pair of diode-laser frequency standards locked to the Doppler-free two-photon
  5S1/2-5D5/2 rubidium transition at 778 nm inside a build-up cavity, reporting Allan-deviation,
  repeatability and reproducibility figures and absolute frequencies for the 85Rb and 87Rb lines
  good to a few kHz. The transition (5S-5D, not the 5S-6S pair) differs, but the apparatus and
  systematics -- an enhancement cavity around a Brewster-window natural-Rb cell, light-shift and
  second-order-Doppler corrections, cell-impurity-limited reproducibility -- are the same family
  of concerns any two-photon rubidium vapour-cell measurement has to account for.
section: method-anchors
---
# edwards2005

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Metrologia 42 (2005) 464-467 | p. 1 |
| DOI | 10.1088/0026-1394/42/5/018 | p. 1 |
| Allan deviation, 85Rb Fg=3-Fe=5 line | 9.3 x 10^-13 tau^-1/2 for 1 s < tau < 100 s, floor 1x10^-13 at 100 s | p. 1, abstract |
| long-term repeatability, same line | 1.2 kHz (3.1 x 10^-12 fractional) | p. 1, abstract |
| system-to-system reproducibility, 85Rb Fg=3-Fe=5 | 4.9 kHz, limited by cell impurities | p. 1, abstract |
| system-to-system reproducibility, 87Rb Fg=2-Fe=4 | 4.5 kHz | p. 1, abstract |
| mean frequency, 85Rb 5S1/2(Fg=3)-5D5/2(Fe=5) | 385 285 142 375.1 (4.9) kHz | p. 1, abstract |
| mean frequency, 87Rb 5S1/2(Fg=2)-5D5/2(Fe=4) | 385 284 566 374.2 (4.5) kHz | p. 1, abstract |
| enhancement cavity | finesse ~100, FSR 530 MHz, mirror curvatures r=2 m / r=infinity, waist w0 ~ 0.42 mm | p. 1 |
| cell | 100 mm, Brewster-window, natural Rb (73% 85Rb, 27% 87Rb) | p. 1 |
| free-running / pre-stabilized laser linewidth | about 1 MHz / about 250 kHz FWHM | p. 1 |
| cavity mode-matching coupling efficiency | about 50% | p. 1 |

## What it says, in its own terms

The paper reports the construction and characterization of two independent diode-laser frequency
standards, NPL-Rb1 and NPL-Rb2, each locked to a Doppler-free two-photon transition of natural
rubidium at 778 nm -- specifically the 5^2S1/2-5^2D5/2 transition, whose Fg=3 to Fe=5 hyperfine
component in 85Rb was adopted by the CIPM in 1997 as a recommended radiation for realizing the
metre. Each standard pre-stabilizes an extended-cavity diode laser to a tunable reference cavity
by side-of-fringe locking, narrowing the linewidth from about 1 MHz free-running to about 250 kHz,
then drives the two-photon transition inside a rubidium cell placed in a passive optical build-up
(enhancement) cavity to reach adequate optical intensity without high input power. The cell is a
100 mm, Brewster-window design containing natural-abundance rubidium.

The abstract reports the standards' short- and long-term frequency stability via the Allan
deviation, the repeatability of a single system's lock to the 85Rb line over time, and the
reproducibility between the two independently-built systems -- the last found to be limited by
impurities in the rubidium cells rather than by the locking scheme itself. Averaging the two
systems' measurements and correcting for the AC-Stark (light) shift and the second-order
relativistic Doppler effect, the paper reports absolute frequencies for the 85Rb Fg=3-Fe=5 and
87Rb Fg=2-Fe=4 hyperfine components, each with an uncertainty of a few kHz, a few parts in 10^12.

## What it is worth here

The specific transition -- 5S1/2 to 5D5/2 at 778 nm -- is not the 5S-6S pair, so its absolute
frequencies are not directly usable numbers for that programme. What is transferable is the
apparatus and systematics template: a natural-rubidium Brewster-window cell inside a passive
build-up cavity, driven by a pre-stabilized diode laser, with light-shift and second-order-Doppler
corrections applied before quoting an absolute frequency, and a reproducibility budget that turns
out to be limited by cell impurities rather than by the optical lock. That is the same family of
systematic concerns, and the same style of error budget, any two-photon vapour-cell rubidium
measurement has to address, even though the transition, and therefore every quoted number, differs.
