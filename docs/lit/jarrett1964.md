---
citekey: jarrett1964
type: article
authors:
  - Jarrett, S. M.
title: 'Spin-Exchange Cross Section for Rb85-Rb87 Collisions'
journal: Phys. Rev.
volume: 133
number: 1A
pages: A111--A117
year: 1964
doi: null
arxiv: null
pdf: PDF_papers/Jarrett_1964_spin-exchange-cross-section-Rb85-Rb87.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'No DOI is printed on the scan. The APS pattern for this volume and page gives 10.1103/PhysRev.133.A111, verify at submission.'
  - 'The scan ends with the first page of the next article (Zernik, p. A117), which is not part of this paper.'
verified_date: 2026-09-14
summary: >
  Ground-state spin-exchange cross section for Rb85-Rb87 collisions,
  (1.70 +- 0.21)e-14 cm^2 at a 70 per cent confidence level, by optical
  pumping with the vapour density measured interferometrically from D1
  absorption in the same cell. The one measured Rb-Rb ground-state
  collision cross section this record needs for the hyperfine
  repopulation term its four-peak contrasts leave uncarried, and a
  documented case of a Pyrex cell holding half the vapour-pressure
  density at its set temperature.
loci: []
section: collision-series
---
# jarrett1964

Held, seven pages (A111 to A117), read in full against the PDF on
2026-09-14. The numbers below read twice.

## What it covers

Optical pumping of the 87Rb constituent of natural rubidium in a Pyrex
cell with 28 mm of neon, the relaxation of the 87Rb polarisation by spin
exchange with the 85Rb majority, and an interferometric absorption
measurement of the 87Rb density in the same cell, from which the cross
section follows as R / (N v_r).

## The claims, with pages

1. The cross section: (1.70 +- 0.21)e-14 cm^2 (abstract p. A111. P. A117),
   the total error being about a 70 per cent confidence interval
   (p. A117).
2. The relaxation rate R = (413 +- 21) s^-1 (p. A116), from the recovery of
   the transmitted pumping light at 50 to 90 C, with R for 85Rb and 87Rb
   equal within 5 per cent.
3. The 87Rb density at 90 C from the D1 high-frequency hyperfine
   component: N = (3.33 +- 0.37)e11 atoms/cm^3 (p. A116), through eq. (3)
   N = 9.07e12 times the integrated absorption coefficient, good to 3 per
   cent (p. A112), with a D1 lifetime of (2.85 +- 0.09)e-8 s taken from
   Stephenson (p. A112). The absorption line half-width was 0.039 cm^-1
   at 90 C, about twice the Doppler width, in the neon (p. A116). The
   cell is 1.4 cm long with 70 per cent peak absorption at 90 C
   (footnote 13, p. A112). The density carries 11 per cent (p. A117).
4. The relative velocity v_r = (4.59 +- 0.05)e4 cm/s, an rms value, whose
   error is the 10 C uncertainty of the mercury thermometer in the oven
   (pp. A116 to A117). The paper notes the choice of rms over mean is
   arbitrary (footnote 14).
5. Isotope ratio a = 2.59 from the 72.15 and 27.85 per cent abundances
   (p. A116).
6. The earlier Franken, Sands and Hobart, and Novick and Peters, values
   (5e-14 for Na-K, 2e-14 for Na-Rb85) were reliable to a factor 3 for
   want of a density measurement. The interferometric density is what
   removes that (p. A117).

## Validity

A ground-state, total-spin-conserving cross section. It carries no
phase-shift information and is not a line-broadening coefficient. The
density is measured in the cell, so the cross section does not depend on
a vapour-pressure law. The cell temperature carries 10 C.

## What this record takes from it

1. **The hyperfine repopulation rate the four-peak contrasts leave open.**
   `scripts/run_four_peak_contrasts.py` says spin exchange "differs by an
   F-dependent coefficient and grows as N" and that the record carries no
   coefficient for it. This paper supplies the cross section. On the
   record's own ladder (`density.number_density_cm3`) and with Jarrett's
   rms convention, N sigma v_r is 4.2e2, 1.9e3, 7.3e3 and 2.4e4 s^-1 at
   70, 90, 110 and 130 C (calculated here. V_r = sqrt(3 k T / (m/2)) = 4.81e4
   cm/s at 403 K, matching the paper's 4.59e4 at 363 K to 0.6 per cent).
   Against the transit rate v_th / w0 = 6.6e6 s^-1 at the calculated 42.38 um
   waist and 130 C (`constants.W0_CENTRAL_M`, v_th = sqrt(2 k T / m)),
   spin exchange is 270 times slower at the hottest set point and 1.6e4
   times slower at the coldest, so within one transit it cannot refill
   the ground hyperfine level the two-photon drive empties: the F-contrast
   term the producer reports as a bound is at most 0.4 per cent of the
   transit rate at 130 C on this ladder, 0.5 per cent on the Alcock
   ladder. What the collisions drive toward is the spin-temperature
   distribution and not equal populations ([walker1997](walker1997.md)).
2. **A worked example of the cell-density caution.** The total density is
   3.33e11 times (1 + 2.59) = 1.20e12 cm^-3 at 90 C, against 2.45e12 on
   Nesmeyanov's law and 3.11e12 on Alcock's at the same set point
   (calculated here): a factor 0.49, which in `density.py`'s language is a 10 K
   cold spot (d ln N / dT = 6.9 per cent per kelvin at 90 C). Two readings,
   both in the sources: the paper's own 10 C thermometry is exactly a
   factor 2 in density at 90 C. And the paper's own account (p. A112) is
   that the density at a given cell temperature depends on how the cell
   was prepared, the bare glass acting as a sink for the alkali, which is
   the observation [gallagher1973](gallagher1973.md) contradicts (p. 865)
   with the statement that equilibrium is reached in Pyrex from 310 to
   450 K once the walls have been saturated by running hot, and whose
   Fig. 5 plots this point below every curve. On either reading it is
   not evidence about the law. It is evidence that a cell can sit a
   factor 2 below it, which is the direction the record inflates its beta
   bound for.

## Conflicts with the record

None numerical. The D1 lifetime used here, 28.5(9) ns, is 2.9 per cent
above the record's `TAU_5P12_S` = 27.70 ns ([volz1996](volz1996.md)). Recomputing the paper's density with the modern value moves it up by that
fraction, immaterial at 11 per cent.
