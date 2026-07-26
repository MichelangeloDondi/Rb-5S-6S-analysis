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

Absolute hyperfine energy levels + isotope shift of the 5S-6S transition (same USAFA group as ayachitula2024). Load-bearing prior nulls: they "find no AC Stark or light shift of the lines at 6 MHz spectral resolution" (varied laser power) and "no density shift ... for a range of Rb atom densities from 3e11 cm^-3" upward — both are prior NULLS on our AC-Stark and collisional self-shift channels, refined by our archival bounds (S0 < 0.63 MHz profile likelihood; beta_self a bound). They compute the differential polarizability alpha_56 = alpha(5S)-alpha(6S) = -1093 a.u. (-1.80e-38 J m^2/V^2), "in a manner similar to Martin 2019" (martin2019) — the source of our DELTA_ALPHA_AU=+1093, never a loose in-house estimate. Our stark_shift_S0_mhz reproduces their predicted -0.66 MHz shift (0.8 W, 63 um waist) to the digit (`test_stark_S0_reproduces_orson2021`); their 63 um waist coincidentally echoes nieddu2019's 64 um, a different apparatus. Isotope shift (87-85) = +94(12) MHz — cross-checks ayachitula2024's more precise +99.189(3). Laser linewidth <50 kHz; they use the Perez Galvan hyperfine constants, now superseded by ayachitula2024.

**Intro framing:** prior groups looked for these shifts on THIS line and saw nulls at ~MHz resolution; our drift-immune ramp method + two-epoch design is the route to the coefficients below that floor.

## The polarizability convention and sign, read from the PDF (2026-07-26)

Quoted verbatim, because an external literature audit proposed that the
programme's "sign disagreement" was a convention artifact and this settles it:

> "We have calculated the AC Stark differential polarizabilty of the 5S state
> minus 6S state α5 − α6 = α56 in a manner similar to that of Martin, et al
> [24], and find **α56 = −1093** in atomic units, which in SI units is
> −1.80 × 10−38 J m2 V−2."

So both halves are now fixed by the paper itself: the convention **is**
α56 ≡ α5S − α6S (the audit had this right), and the printed value **is
negative**. Orson therefore implies α6S − α5S = **+1093**, against this
repo's recompute of **−1145**. The disagreement is real, not bookkeeping.

**Orson is internally consistent**: α56 = −1.80e-38 J m²/V² with their
E² = 4.8e10 V²/m² gives ½α56E²/h = −0.65 MHz, matching the −0.66 MHz they
state, and a negative transition shift is the red shift they describe.

**What their sign would require.** With α5S(993) = +832 (our value, and the
robust one — every 5S term is red-detuned at 993 nm, so it is sign-unanimous),
α56 = −1093 implies α6S(993) = **+1925**. Reaching a large positive α6S needs
993 nm to sit RED of the strong 6S upward transitions; it does not — the
dominant 6S–6P lines are at 2.7/2.8 µm, so 993 nm is far blue of them and
those terms are negative. Our −312 is the sum of that negative upward group
(−947) and the positive downward 5P cascade (+623).

The audit's own supporting evidence points the same way: Safronova 2004's
all-order 6S–5P elements (4.119 / 6.013 a.u.) and the Gomez 2005 / Arora–Sahoo
2012 lifetimes (45.57(17) / 45.44(8) ns) pin the cascade term at the
sub-percent level, leaving no room for the ~33% revision a flip would need.

