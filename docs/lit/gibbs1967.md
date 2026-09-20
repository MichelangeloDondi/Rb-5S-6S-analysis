---
citekey: gibbs1967
type: article
authors:
  - Gibbs, H. M.
  - Hull, R. J.
title: 'Spin-Exchange Cross Sections for Rb87-Rb87 and Rb87-Cs133 Collisions'
journal: Phys. Rev.
volume: 153
pages: 132--151
year: 1967
doi: null
arxiv: null
pdf: PDF_papers/Gibbs_1967_Rb87-Rb87-Rb87-Cs133-spin-exchange-cross-sections.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 and 2 (abstract, introduction and the start of the experiment description) read
    against the PDF on 2026-09-20. The density-measurement analysis (Sec. V) and the results
    discussion (Sec. VI) are not read. The article runs from p. 132 to p. 151 by its own running
    headers. Three further unnumbered pages of figures follow it in the PDF.
  - 2026-09-20: adversarial audit_B corrected three page/section attributions. The
    signal-vs-polarization correction sentence ("as large as 12%") is in the introduction, not on
    p. 2. Circularly polarized light is named in Sec. II, not the p. 1 abstract, so the method row
    now splits its two page citations. And the three-term relaxation formula quoted in prose is
    the abstract's own wording, not the paper's numbered Eq. (2), which is a different, unlabelled
    four-term expression on p. 2.
verified_date: null
summary: >
  Measures the total spin-exchange cross sections for Rb87-Rb87 and Rb87-Cs133 collisions at
  78 C using a transient hyperfine-optical-pumping (Franzen) method, reporting
  sigma(Rb87-Rb87) = (1.9 +- 0.2) x 10^-14 cm^2 and sigma(Rb87-Cs133) = (2.3 +- 0.2) x 10^-14
  cm^2, with density determined independently via Fabry-Perot absorption spectroscopy rather than
  a vapour-pressure curve. It is a direct, same-species (Rb87 self-exchange) collisional cross
  section of the kind a collisional-broadening discussion for rubidium draws on.
section: collision-series
---
# gibbs1967

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rev. 153, 132-151 (1967) | p. 1, running headers |
| sigma(Rb87-Rb87) | (1.9 +- 0.2) x 10^-14 cm^2 | p. 1, abstract |
| sigma(Rb87-Cs133) | (2.3 +- 0.2) x 10^-14 cm^2 | p. 1, abstract |
| temperature of measurement | 78 C | p. 1, abstract |
| correction for signal-vs-polarization nonlinearity | as large as about 10-12% | p. 1, abstract and introduction |
| method | Franzen transient method, hyperfine optical pumping with circularly polarized light | p. 1, abstract (Franzen method, hyperfine pumping); p. 2 (circularly polarized light) |

## What it says, in its own terms

The paper determines total spin-exchange cross sections for Rb87 colliding with Rb87 (self
exchange) and with Cs133, using a transient hyperfine-optical-pumping technique. Circularly
polarized light that only one hyperfine ground level can absorb creates a large population
difference between the ground hyperfine levels. A resonant rf field is then applied to destroy
any residual longitudinal (Zeeman) polarization, isolating the hyperfine population difference,
whose relaxation is monitored via the transmitted light (the Franzen method) and fit to a single
exponential with rate 1/tau = 1/T + 1/T_SI + 1/T_EI, where T is the non-spin-exchange relaxation
time and T_SI, T_EI are the self- and cross-species spin-exchange times (their abstract). The
paper's own numbered Eq. (2) is the exponential decay relation S_A = exp(-t/tau), with the
unlabelled four-term breakdown 1/tau = 1/T1' + 1/T1'' + 1/T_EI + 1/T_SI given immediately
afterward on p. 2.

The paper states only three quantities need to be measured to get a cross section: the total
relaxation rate 1/tau, the non-spin-exchange relaxation rate 1/T (the zero-density intercept of a
1/tau versus density plot), and the absolute density itself. Density is obtained not from a
vapour-pressure curve but directly, from the frequency-integrated absorption coefficient measured
with a scanning Fabry-Perot interferometer, after correcting the observed profile for the
instrument's own transmission function to recover the true emission/absorption profile (Sec. V,
not read in detail here). The cross section then follows from the slope of 1/tau against density.
The paper notes its result for Rb87-Rb87 agrees with several earlier measurements (Moos and
Sands, Jarrett, and a corrected reading of Davidovits and Knable), serving as a cross-check by an
independent method.

## What it is worth here

This is a same-species (Rb87 self-exchange) collisional cross section measured directly from
independently-calibrated density and relaxation-rate data, in the same family as other
collision-series holdings on rubidium spin-exchange cross sections. It is a natural literature
anchor for a rubidium self-broadening / collisional discussion, both for the Rb87-Rb87 number
itself and for its density-determination method (absorption-derived, not vapour-pressure-derived),
which is the same discipline a record's own vapour-density checks should meet.
