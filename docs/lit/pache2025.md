---
citekey: pache2025
type: misc
authors:
  - Pache, Lucas
  - Cordier, Martin
  - Letellier, Hector
  - Schemmer, Max
  - Schneeweiss, Philipp
  - Volz, Jürgen
  - Rauschenbeutel, Arno
title: 'Magic-wavelength nanofiber-based two-color dipole trap with sub-lambda/2 spacing'
journal: arXiv preprint
volume: null
pages: null
year: 2025
doi: null
arxiv: 2407.02278v3
pdf: PDF_papers/Pache_2025_magic-wavelength-nanofibre-two-color-trap.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  CAESIUM, D2, single photon -- not this programme's species or transition, and
  the note exists to say so. A nanofibre two-colour dipole trap (a = 200 nm
  radius) run at MAGIC wavelengths, 685.4 nm blue and 935.7 nm red about the
  852.3 nm D2 line, for the stated purpose of suppressing the inhomogeneous
  broadening that trap-induced Stark shifts cause. That is the idea this
  repository was about to propose for its own ONF arm, realised and
  characterised: 165 +- 13 atoms, 8.5 +- 0.4 ms lifetime, 7 per cent peak
  filling. It also shows the vector light shift being managed rather than
  cancelled, by a 150 GHz detuning between the counter-propagating red fields
  and by a blue-magic vector polarizability two orders of magnitude below the
  red one, both of which are species- and wavelength-specific and do NOT
  transfer to Rb 5S-6S.
loci: []
section: prior-art
---
# pache2025

Held. Verified against the PDF, pages 1 to 6, on 2026-09-10.

## What it is, and what it is not

Rauschenbeutel's group at Humboldt-Universität zu Berlin. A two-colour
nanofibre dipole trap for **caesium**, addressing the **D2 line at 852.3 nm**,
a single-photon transition. It is not rubidium, not a two-photon nS to n'S
transition, and not the OIST apparatus lineage. It supplies no magic power
ratio for 5S to 6S, and nothing in it is specific to a two-photon line.

## The trap

A tapered fibre of nanofibre-waist radius `a = 200 nm`. Blue- and red-detuned
fields are launched from both ends and tuned to `lambda_blue = 685.4 nm` and
`lambda_red = 935.7 nm`, close to the magic wavelengths of the caesium D2
transition, so as to suppress the differential scalar light shifts between the
ground and excited states.

The two counter-propagating blue fields are deliberately power-unbalanced,
`P_blue,1 = 0.6 mW` against `P_blue,2 = 16 mW`, so that the partial standing
wave still presents a barrier against atoms escaping to the fibre surface at
its nodes. The red fields carry `P_red = 1 mW` in total. Adjacent trapping
sites sit `d = lambda_blue / (2n) = 300 nm` apart, which is `0.35 lambda` with
`n = 1.14` the effective mode index, and the trapping minima are about 350 nm
from the fibre surface at a depth of approximately 110 microkelvin.

## Why it matters here, and it is a caution rather than an input

**The purpose is stated in the paper's own words:** the magic wavelengths are
used, verbatim, "in order to minimize the inhomogeneous broadening of the optical transition frequency due to trap-induced Stark shifts".

That is precisely the argument this repository had drafted for its own guided
arm. It is realised, characterised and published, in caesium, so a proposal
that offers magic trapping as the way to suppress a trap-induced light-shift
distribution offers nothing new. What is left for a 5S to 6S guided proposal
is the RESIDUAL after magic trapping, not the idea of magic trapping.

**The vector light shift is managed, not eliminated,** and by two routes that
do not transfer. The counter-propagating red fields are detuned from each
other by about 150 GHz, which both prevents a standing wave and minimises the
inhomogeneous Zeeman broadening the vector shift causes. And the paper notes, of the vector polarizability, that it is verbatim "cesium for the blue-detuned magic wavelength is two orders of magnitude smaller than that for the red-detuned magic wavelength". Both facts are properties of caesium at those two wavelengths.
This repository's own vector-light-shift debt for two J = 1/2 states is not
discharged by either.

## The numbers a guided forecast has to answer to

| quantity | value |
|---|---|
| trapped atom number | 165 +- 13 |
| on-resonance optical depth | 6.9 +- 0.8 |
| trap lifetime | 8.5 +- 0.4 ms |
| peak local filling factor | 7 per cent |
| radial trap frequency | 109 kHz calculated, minima at 116 and 232 kHz |
| axial trap frequency | 134 kHz calculated, minimum at 139 kHz |
| azimuthal trap frequency | 10 to 20 kHz, predicted, not excited by their drives |

**The lifetime is the one to read against our own forecast.** 8.5 ms is short
against any per-trace integration this record has costed for a guided arm, and
a trap that must be reloaded on that cadence sets the duty cycle rather than
the count rate. `results/campaign_twin_forecast.csv` prices the fibre arm at
about 69 minutes per trace at the demonstrated count rate. That figure was
built from a different platform's demonstration and this paper is the sharper
comparator for a trapped-atom arm.

## The fibre is the same size as ours, once the units are read

**Pache quotes `a = 200 nm` as a RADIUS, so a 400 nm diameter, and this
repository works in diameters throughout.** Read without that conversion the
paper appears to introduce a third fibre size. It does not.

`rb5s6s.fibre.solve_he11` takes `diameter_nm`
and halves it internally, and `docs/methods/09` tabulates 350 and 400 nm
fibres. So the 400 nm this record commits from the 2020 OIST measurement is
the SAME size as Pache's fibre, and `vylegzhanin2025`'s `a = 175 nm` radius is
the 350 nm diameter already in that table, which its own note says outright.

Two fibre sizes are in play across this literature, not three. The intensity
decay length at 993.4 nm runs 312 nm at 400 nm diameter against 492 nm at
350 nm, a factor of 1.58, so which of the two a statement belongs to still has
to be named. The reason is a real 50 nm of diameter.
