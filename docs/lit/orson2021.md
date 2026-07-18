---
citekey: orson2021
type: article
authors:
  - Orson, S. T.
  - McLaughlin, C. D.
  - Lindsay, M. D.
  - Knize, R. J.
title: 'Absolute hyperfine energy levels and isotope shift of {Rb} 5S--6S two-photon transition'
journal: 'J. Phys. B: At. Mol. Opt. Phys.'
volume: 54
number: 17
pages: 175001
year: 2021
doi: 10.1088/1361-6455/ac2812
arxiv: null
pdf: PDF_papers/Orson_2021_Rb-5S-6S-absolute-hyperfine-isotope-shift.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Source of DELTA\_ALPHA\_AU: they compute alpha\_56=alpha(5S)-alpha(6S)
  =-1093 a.u.
loci:
  - M16
  - M4e
  - P1
  - THEORY
  - constants
section: usafa-lineage
---

# orson2021

Source of DELTA\_ALPHA\_AU: they compute alpha\_56=alpha(5S)-alpha(6S) =-1093 a.u. (our +1093). Prior nulls: no AC-Stark and no density shift at 6 MHz resolution. Our stark\_shift\_S0\_mhz reproduces their -0.66 MHz shift to the digit.

Absolute hyperfine energy levels + isotope shift of the 5S-6S transition (same USAFA group as ayachitula2024). Load-bearing prior nulls: they "find no AC Stark or light shift of the lines at 6 MHz spectral resolution" (varied laser power) and "no density shift ... for a range of Rb atom densities from 3e11 cm^-3" upward -- both are prior NULLS on our AC-Stark and collisional self-shift channels, refined by our archival bounds (S0 < 0.63 MHz profile likelihood; beta_self a bound). They compute the differential polarizability alpha_56 = alpha(5S)-alpha(6S) = -1093 a.u. (-1.80e-38 J m^2/V^2), "in a manner similar to Martin 2019" (martin2019) -- the source of our DELTA_ALPHA_AU=+1093, never a loose in-house estimate. Our stark_shift_S0_mhz reproduces their predicted -0.66 MHz shift (0.8 W, 63 um waist) to the digit (`test_stark_S0_reproduces_orson2021`); their 63 um waist coincidentally echoes nieddu2019's 64 um, a different apparatus. Isotope shift (87-85) = +94(12) MHz -- cross-checks ayachitula2024's more precise +99.189(3). Laser linewidth <50 kHz; they use the Perez Galvan hyperfine constants, now superseded by ayachitula2024.

**Intro framing:** prior groups looked for these shifts on THIS line and saw nulls at ~MHz resolution; our drift-immune ramp method + two-epoch design is the route to the coefficients below that floor.
