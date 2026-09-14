---
citekey: vanderspek1988
type: article
authors:
  - van der Spek, A. M.
  - Mulders, J. J. L.
  - Steenhuysen, L. W. G.
title: 'Vapor pressure of rubidium between 250 and 298 K determined by combined fluorescence and absorption measurements'
journal: J. Opt. Soc. Am. B
volume: 5
number: 7
pages: 1478--1483
year: 1988
doi: null
arxiv: null
pdf: PDF_papers/vanderspek1988.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'No DOI is printed on the scan. The Optica pattern gives 10.1364/JOSAB.5.001478, verify at submission.'
  - 'The abstract quotes the literature heat of sublimation as 82.2 +- 0.4 kJ/mol and Table 2 (p. 1481) as 82.3 +- 0.4. The table is taken as the record.'
verified_date: 2026-09-14
summary: >
  The vapour pressure of solid rubidium from 250 to 298 K, a fluorescence
  curve pinned by one absolute absorption point (2.3e16 m^-3 at 296.6 K,
  4 per cent, cell temperature to 0.1 K) and the only such data the
  paper knows of. Bears on nothing in this record's 343 to 403 K range,
  where density.py refuses below the melting point anyway. Held as the
  low-temperature end of the rubidium curve, where it sits a factor 2
  above the Alcock solid law at room temperature and on it at 250 K.
loci: []
section: method-anchors
---
# vanderspek1988

Held, six pages, read in full against the PDF on 2026-09-14. Table 1 and
eq. (13) read twice.

## What it covers

Saturated vapour pressure of solid rubidium in a glass cell between 250
and 298 K. 85Rb ground-state atoms are excited on the D1 line at 795 nm
with a single-mode ring dye laser of about 10 MHz width (p. 1479). The
fluorescence against temperature gives the shape of the curve, and an
absolute absorption measurement at room temperature over the cell's
16.5 cm path (p. 1479) fixes its scale. The
thermodynamic analysis extracts the heat of sublimation at 0 K.

## The claims, with pages

1. Absolute anchor: 23e15 m^-3 at 296.6 K from absorption (p. 1480. Table 1 p. 1481 lists 2.300e16 m^-3 and 9.419e-5 Pa at 296.60 K), with
   4 per cent accuracy, the largest error being the absolute absorption
   itself (p. 1482). The cell temperature is known to 0.1 K and does not
   contribute (pp. 1479, 1482).
2. Table 1 (p. 1481): from 2.577e16 m^-3 (1.064e-4 Pa) at 299.05 K down
   to 3.091e13 m^-3 (1.068e-7 Pa) at 250.28 K, sixty-odd rows.
3. The fitted law, eq. (13) p. 1482: ln p = -9899.0/T + 2.5000 ln T
   - (1.2258e-3) T - 1.0961, p in bars, T in kelvin.
4. Heat of sublimation at 0 K, Table 2 (p. 1481): 82.3 +- 0.3 kJ/mol from
   the state sum without mixing entropy, against a literature 82.3 +- 0.4. The slope-based values (Clapeyron 87.5 +- 0.5, with Kirchhoff 85.0 +-
   0.5) are judged unreliable (p. 1482).
5. The paper states there are no other data on the vapour pressure of
   solid Rb (p. 1481), so its comparison with the literature is through
   the heat of sublimation.
6. Below about 260 K the points fall under the fitted line, read as
   adsorption on the Pyrex wall, a monolayer being about 1e13 atoms per
   cm^2 so that 1e-8 cm^2 of wall holds all the vapour at those
   temperatures (p. 1483). Above 296 K the departure is read as small
   thermal gradients in the cell (p. 1483).
7. Cell preparation (p. 1479): baked near 470 K for over 24 h, about 1 g
   of Rb distilled in, and cycled over 250 to 383 K several times before
   use to remove any influence of wall absorption. The temperature is
   read by two thermistors on the wall.

## Validity

A relative curve with one absolute point and a thermodynamic
cross-check. The absolute scale is 4 per cent at one temperature and the
shape is set by fluorescence, which the paper argues is linear in density
at these optical depths. All of it is below the melting point.

## What this record takes from it

Nothing numerical. `rb5s6s/density.py` refuses any temperature below
39.3 C, and the archive runs 70 to 130 C. What the paper fixes is the
size of the disagreement between sources at the cold end, which bounds
how far the record's laws can be trusted when extrapolated: against the
Alcock solid law that the held Steck (revision 2.3.4) tabulates,
log10 P/atm = 4.857 - 4215/T, the Table 1 densities are 1.02 times the
law at 250.3 K, 2.08 at 273.3 K, 2.10 at 296.6 K and 1.81 at 299.05 K
(calculated here), a factor 2 at room temperature from a measurement with 0.1 K
thermometry. Nothing in the record quotes a room-temperature Rb density,
and this is the reason it should not.

The method, a fluorescence ratio across the sweep pinned by a single
absolute absorption at one point, is the shape of the in-situ density
calibration the campaign plans (`docs/plan/`), and this is the paper that
did it for rubidium with a stated budget.

## Conflicts with the record

None.
