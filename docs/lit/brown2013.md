---
citekey: brown2013
type: misc
authors:
  - Brown, Roger C.
  - Wu, Saijun
  - Porto, J. V.
  - Sansonetti, Craig J.
  - Simien, C. E.
  - Brewer, Samuel M.
  - Tan, Joseph N.
  - Gillaspy, J. D.
title: 'Quantum interference and light polarization effects in unresolvable atomic lines: application to a precise measurement of the 6,7Li D2 lines'
journal: arXiv preprint
year: 2013
doi: null
arxiv: '1212.2220'
pdf: PDF_papers/Brown_2013_quantum-interference-unresolvable-lines-Li-D2.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 (abstract, introduction, and the start of the dipole-scattering derivation)
    read against the PDF on 2026-09-20. No published journal reference is given on either page, so
    the record carries the arXiv v3 preprint (4 Jul 2013) as held. Sections III and IV, which
    carry the fit to the Li data and the extracted frequencies and charge-radius difference, are
    not read.
verified_date: null
summary: >
  When two or more excited-state hyperfine components are separated by about a natural linewidth
  or less, the fluorescence line shape is not a sum of Lorentzians: quantum interference between
  the scattering pathways through the different components adds polarization-dependent cross
  terms, which the paper shows can shift a fitted line centre by as much as 1 MHz if ignored, while
  the corrected treatment reaches an uncertainty of 25 kHz or better on 6,7Li D2 transition
  frequencies. The atom (lithium) and application (nuclear charge radius) are different from a
  rubidium 5S-6S programme, but the mechanism -- interference between not-quite-resolved
  excited-state components distorting an apparent line centre -- is a methodology worth having on
  hand wherever a multi-peak or overlapping-structure fit is concerned.
section: prior-art
---
# brown2013

## Values

| field | value | where in the paper |
|---|---|---|
| claimed uncertainty on absolute transition frequencies | <= 25 kHz | p. 1, abstract |
| largest line-centre shift from ignoring interference | up to 1 MHz | p. 1, abstract |
| regime where interference matters | excited-state splittings of order the natural linewidth | p. 1, abstract |
| scattering formula used | Kramers-Heisenberg, second order in the electric-dipole coupling | p. 1-2, Eq. (1)-(2) |
| other systems flagged with the same unresolved-hyperfine-interference issue | H, Li, K, Fr, Be+, Mg+ D2-type lines | p. 1, Sec. I |

## What it says, in its own terms

The paper's subject is what happens to an atomic line shape when two or more excited-state
hyperfine (or otherwise closely spaced) sublevels are separated by an amount comparable to or
smaller than their natural linewidth, so that the transition is not fully resolved "in a
fundamental sense not limited by instrumentation" (p. 1). In that regime the fluorescence or
absorption line shape is not simply a sum of independent Lorentzians: because the scattering
amplitude is a coherent sum over the intermediate excited states before the modulus-squared is
taken (their Eq. (2), a Kramers-Heisenberg expression), cross terms between different excited
hyperfine components survive and distort the line shape. The paper shows these cross terms depend
on the polarization of the exciting and collection light, so the same partially-resolved line
looks different, and its apparent centre shifts, depending on the polarization geometry used.

Working through the angular-momentum algebra (Wigner-Eckart reduction of the dipole matrix
elements) for hyperfine sublevels of a single electronic ground and excited state, the paper
derives closed-form corrected line shapes (their Eq. (5)-(7)) that include both the ordinary
Lorentzian terms and the interference cross terms, and shows the cross terms are not negligible
whenever the hyperfine splitting is of order the natural linewidth. Applying the corrected line
shape to new spectroscopic data on the 6Li and 7Li D2 lines, the paper reports that failing to
account for interference shifts the inferred line centres by as much as 1 MHz, while the corrected
analysis reaches absolute-frequency uncertainties at or below 25 kHz, feeding an improved value
for the difference in mean-square nuclear charge radius between 6Li and 7Li.

## What it is worth here

Lithium D2 hyperfine structure and nuclear charge radii are unrelated to a rubidium 5S-6S
programme, and no number here transfers. What is directly relevant is the mechanism: any line fit
that carries two or more not-fully-resolved sublevels (hyperfine components, isotope shifts, or
otherwise) is subject to the same coherent-interference distortion of the apparent centre, at the
same order of magnitude relative to the natural linewidth, and the fix is the same
Kramers-Heisenberg bookkeeping rather than an ad hoc lineshape correction. Worth revisiting if a
multi-peak fit's own regime -- whether this effect matters for it or not -- is ever argued.
