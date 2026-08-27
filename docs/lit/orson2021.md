---
citekey: orson2021
type: article
authors:
  - Orson, S. T.
  - McLaughlin, C. D.
  - Lindsay, M. D.
  - Knize, R. J.
title: 'Absolute hyperfine energy levels and isotope shift of Rb 5S–6S two-photon transition'
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
verified_date: 2026-07-29
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

Held. The article number 175001 and the sign convention and predicted Stark shift below were verified against the PDF.

## The system

Absolute hyperfine energy levels and the isotope shift of the Rb 5S-6S two-photon transition, measured by the same group (USAFA) as ayachitula2024, using the Perez Galvan hyperfine constants (since superseded by ayachitula2024's more precise values). Laser linewidth below 50 kHz.

## The numbers

No AC-Stark or light shift was detected in the line positions at 6 MHz spectral resolution across the laser powers used, and no density shift was observed for Rb densities from 3e11 cm^-3 upward. The isotope shift (87Rb minus 85Rb) is +94(12) MHz.

The differential polarizability alpha_56 = alpha(5S) - alpha(6S) is computed, not measured, in a manner similar to that of martin2019: alpha_56 = -1093 a.u., or -1.80e-38 J m^2 V^-2. At 0.8 W and a 63 um waist this predicts a Stark shift of -0.66 MHz, a red shift.

## Validity

The isotope shift, +94(12) MHz, is consistent with ayachitula2024's later, more precise value of +99.189(3) MHz. The paper's own predicted Stark shift also reproduces from its own equation: running its stated inputs (E^2 = 4.8e10 V^2/m^2 at 0.8 W and a 63 um waist) through this repository's unit conversion returns -0.653 MHz, matching the stated -0.66 MHz.

## Use in this record

**The definition, read from the paper rather than inferred.** Section 3,
"Results and analysis", which is where both this paragraph and the density
paragraph below sit. The paper has four sections in all, and section 4 is
the conclusions. It states it in words: the authors calculate "the AC Stark differential
polarizabilty of the 5S state minus 6S state alpha5 - alpha6 = alpha56",
and find alpha56 = -1093 a.u., or -1.80e-38 J m^2 V^-2. So their subtraction
runs 5S minus 6S, and converting to this record's convention gives
alpha(6S) - alpha(5S) = +1093. The disagreement with this record's -1145 is
therefore a real disagreement between two calculations, not an artefact of
which way the subtraction runs. That question was put and settled from this
paragraph on 2026-08-26.

**Their own arithmetic reproduces, and their conditions are close to this
campaign's.** The same paragraph gives a focused waist radius of 6.3e-5 m,
0.8 W, a peak intensity of 1.28e8 W m^-2 and E^2 = 4.8e10 V^2 m^-2, with the
shift as half alpha56 E^2. That returns -0.652 MHz against their stated
-0.66. Their waist is 63 um against this record's measured 64 um, so the
geometry is near enough for a direct comparison: at their conditions this
record's value predicts +0.683 MHz, the same size and the other sign.

**Their AC-Stark null does not discriminate between the two, and the
comparison has to be made on one axis.** The null search is at 6 MHz, the
figure the abstract and the conclusions both give, and the paper's own words
for it are "at our relative one-photon spectral resolution of about 6 MHz".
That is the LASER axis. The predictions near 0.65 MHz are shifts of the
transition energy and so live on the TRANSITION axis, which is twice the
laser axis, and the paper states its own conversion in section 2: a wavemeter
one-photon accuracy of 30 MHz "converted to 0.002 cm-1 = 60 MHz for the
two-photon transitions". Put on either axis consistently, the null is about
**eighteen** times the prediction: 12 against 0.66 on the transition axis,
or 6 against 0.33 on the laser axis. The paper's own Stark paragraph
compares -0.66 against 60 MHz, which is axis-consistent and uses the
wavemeter-limited absolute-energy figure and not the resolution of the
search. Either way the null is a real bound on anything large. It is not
evidence for either sign, and it should not be cited as prior art favouring
one.

**The density shift, which this record borrows.** Section 3 also records
that the density shift of the 5S-6S line "has not been measured", and
bounds it from other Rb and Cs transitions at less than 30 MHz/Torr, giving
0.09 MHz at their 140 C. That bound is the source for the collisional-shift
entry in [UNCERTAINTY.md](../UNCERTAINTY.md) section 6, and it is Zameroski
2014's by measurement: their citation for it is reference [25], and the
ceiling is set by Zameroski's 5S-5D5/2 self-shift.

**Their 0.09 rests on a vapour pressure their own density contradicts.**
They quote 3e-3 Torr at 140 C where this record's chain gives 2.2e-3, 39
per cent apart. That gap was described here as sitting inside the spread
between published vapour-pressure correlations. It does not. The spread
`rb5s6s/density.py` carries is 10 to 30 per cent, adopted at 20, so 39 is
outside it. The paper settles the question against itself: its abstract and
section 3 give an atomic density of 5e13 cm^-3 at that temperature, and
3e-3 Torr at 413 K is 7.0e13, while this record's chain gives 5.06e13.
**Orson's own stated density sits within the one significant figure they
quote it to of this record's chain, 5e13 against 5.06e13, and disagrees with
Orson's own stated pressure by a factor 1.4.** So
the discrepancy is internal to the paper and not a choice between
correlations, and their 0.09 MHz is high by that factor.


This repository's independently computed alpha(6S) - alpha(5S) is -1145 a.u., opposite in sign to this paper's implied alpha(6S) - alpha(5S) = +1093 a.u. and 4.8% different in magnitude. Since the predicted shift itself reproduces closely, the discrepancy is not a units or convention error but one of atomic-structure calculation. Resolving it in the paper's favor would require a 33% revision to the 6s-5p3/2 radial matrix element, on which this repository's value, Safronova 2004, and Arora 2012 agree to within 0.7%.

## Values

The load-bearing numbers of this source, each at its stated
location, so a prose quote anywhere in this repository can
reference a row here and be checked against it.

| field | value | where in the paper |
|---|---|---|
| alpha_56_au | -1093 | their COMPUTED differential polarizability alpha(5S)-alpha(6S) in a.u., a calculation and not a measurement (their own AC-Stark search was a null, so no experiment has set this sign), the sign the "Use in this record" section above disputes |
| null_search_resolution_mhz | 6 | their AC-Stark and density null-search resolution, **on the LASER axis**: the conclusions call it a relative one-photon spectral resolution. Doubles to 12 MHz on the transition axis where a shift prediction lives. Tabulated because a prose quote of this number drifted twice, once in its value and once in its axis |
| wavemeter_resolution_mhz | 60 | their absolute-energy resolution **on the TRANSITION axis**, 0.002 cm^-1, section 2, which states the conversion itself: a one-photon wavemeter accuracy of 30 MHz doubled for the two-photon transitions. This is the figure their own Stark paragraph compares -0.66 against, and it is NOT the resolution of the null search |
| density_shift_bound_mhz_per_torr | 30 | their borrowed ceiling on the 5S-6S density shift, section 3, taken in turn from their reference [25], Zameroski 2014. A genus-level limit from other Rb and Cs lines, since this line's density shift "has not been measured" |
| drive_power_w | 0.8 | the TOTAL power in both counterpropagating beams, which is what their I = 2P/(pi r^2) = 1.28e8 W/m^2 uses and what their stated maximum intensity of about 1e4 W/cm^2, counting both beams, implies. Their laser emits about 1000 mW in all, so 0.8 W per beam is arithmetically impossible. This record's 225 mW is the FORWARD power with the retro added separately as (1+rho), so the two power conventions differ as well as the geometries |
| null_over_own_prediction | 18 | their null, 12 MHz on the transition axis, over the 0.66 MHz shift their own alpha_56 predicts at their own conditions. The search floor sits eighteen times above the effect they were looking for, so the null tests neither the size nor the sign. This is the comparison that transports: each experiment against its own prediction, since the geometry cancels inside each ratio. A coefficient does NOT transport, because S_0 = kappa P still carries the waist and the beam architecture |
| resolution_confidence | 1 sigma | their section 2 states that every figure it calls an error, an accuracy or a spectral resolution is a one standard deviation measurement error. This record's bounds are 95 per cent one-sided, so the two cannot be ratioed until the levels match: theirs at one-sided 95 per cent is 1.645 times looser |
| quoted_density_cm3 | 5e13 | their stated atomic density at 140 C, abstract and section 3. It sits within the single significant figure they quote it to of this record's chain, 5e13 against 5.06e13, though at the other end of their stated range their 3e11 at 60 C is about 20 per cent from this chain's 2.50e11, so the agreement is an endpoint coincidence and not an agreement between chains and with their own quoted 3e-3 Torr only to a factor 1.4 |
| predicted_shift_mhz | -0.66 | their predicted shift at 0.8 W and their 63 um waist, which this record's unit chain reproduces to the digit |
| isotope_shift_mhz | +94(12) | the 87-85 isotope shift |
| laser_linewidth_khz | <50 | their stated laser linewidth |
