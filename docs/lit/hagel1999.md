---
citekey: hagel1999
type: article
authors:
  - Hagel, G.
  - Nesi, C.
  - Jozefowski, L.
  - Schwob, C.
  - Nez, F.
  - Biraben, F.
title: 'Accurate measurement of the frequency of the 6S-8S two-photon transitions in cesium'
journal: Optics Communications
volume: 160
pages: '1--4'
year: 1999
doi: null
arxiv: null
pdf: PDF_papers/Hagel_1999_Cs-6S-8S-two-photon-frequency-light-shift-pressure-shift.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 and 2 (of 4) read against the PDF on 2026-09-20. No DOI is printed
    on these pages. The Elsevier PII, S0030-4018(98)00662-2, is printed
    instead and is recorded as-is rather than converted to a DOI. The
    remaining two pages (the frequency-standard discussion and the final
    extrapolated result) are not read.
  - 2026-09-20: adversarial audit_C found the applications sentence naming "the Yb
    2S1/2-2D3/2 line at 411 nm". A 300 dpi render of the garbled source line shows the paper
    names the Yb+ ion's 2S1/2-2D5/2 line, not neutral Yb's 2D3/2 line. Corrected.
verified_date: null
summary: >
  A Biraben-group Doppler-free two-photon measurement of the Cs 6S-8S
  transition frequency at 822 nm, with its light shift and pressure shift
  measured and extrapolated away to reach 3e-10 fractional uncertainty. It
  is prior art on a sibling atom and transition, not on Rb 5S-6S itself: the
  apparatus is explicitly stated to be the same family used for the Rb 5S-5D
  transition, and the paper separates and extrapolates the same two
  systematics (light shift and pressure shift) this repository tracks for
  its own line, with a transit-time-broadened lineshape of the same kind.
loci: []
section: prior-art
---
# hagel1999

## Values

| field | value | where in the paper |
|---|---|---|
| final fractional frequency uncertainty | 3 x 10^-10 | p. 1, abstract |
| mean light shift, F=3 and F=4 lines | -54(11) Hz/mW | p. 2 |
| theoretical light-shift prediction | -58 Hz/mW | p. 2 |
| pressure range studied | 5 x 10^-5 to 10^-3 Torr | p. 2 |
| intracavity optical power range | 0.1-2 W | p. 2 |
| build-up cavity length | 280 mm | p. 2 |
| mirror curvature radii / transmissions | 4 m / 5.4% and 2 m / 0.03% | p. 2 |
| resulting beam waist | 0.38 mm | p. 2 |
| earlier lambdameter measurement (1985) uncertainty | about 7 MHz | p. 1 |
| line shape used for the fit | Lorentzian convolved with a double-exponential (transit-time) curve, not a Voigt profile | p. 2 |

## What it says, in its own terms

Using a titanium-sapphire laser locked to a stable Fabry-Perot reference
cavity, and a caesium vapour cell placed inside a second, 280 mm long
build-up cavity (to define the two-photon excitation geometry and cancel the
first-order Doppler effect), the group measures the 6S(F=3,4)-8S(F=3,4)
two-photon transition frequencies in caesium via the 456 nm 8S-7P-6S
fluorescence cascade. The best fit to the line shape is not a Voigt profile
but a Lorentzian convolved with a double-exponential curve, which the paper
attributes to transit-time broadening. Each line is recorded over a pressure
range of 5e-5 to 1e-3 Torr and an intracavity power range of 0.1-2 W.

Extrapolating the fitted line centre to zero optical power gives a mean
light shift of -54(11) Hz/mW for the F=3 and F=4 lines together, in
reasonable agreement with a theoretical estimate of -58 Hz/mW quoted from
earlier work. Extrapolating separately to zero pressure removes the
collisional (pressure) shift. Combined, the two extrapolations bring the
overall frequency measurement to a fractional uncertainty of 3e-10, well
below an earlier lambdameter-based measurement of the same lines (about
7 MHz uncertainty). The explicit motivation is to establish the 822 nm
6S-8S line as a secondary optical frequency standard, useful in particular
for referencing measurements of the hydrogen 1S-3S interval and other nearby
lines (the Yb+ 2S1/2-2D5/2 line at 411 nm, the He 2^3S1-2^3P0 line at
1.083 um).

## What it is worth here

Same experimental family as this repository's own line: a single-species,
cavity-enhanced, Doppler-free two-photon standard, tracking the same two
systematics this record tracks for its own transition, a light shift and a
collisional (pressure) shift, each extrapolated away, with the same
transit-time-broadened Lorentzian line shape. The paper states its own
apparatus is basically the one used for the Rb 5S-5D transition, so this is
Biraben-lineage prior art on a different atom and a different transition
(Cs 6S-8S rather than Rb 5S-6S), useful mainly as a check on how a closely
related group separated and reported the same two systematics, not as a
source of any number this repository would use directly.
