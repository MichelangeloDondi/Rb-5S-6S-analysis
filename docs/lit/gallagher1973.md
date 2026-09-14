---
citekey: gallagher1973
type: article
authors:
  - Gallagher, A.
  - Lewis, E. L.
title: 'Determination of the vapor pressure of rubidium by optical absorption'
journal: J. Opt. Soc. Am.
volume: 63
number: 7
pages: 864--869
year: 1973
doi: null
arxiv: null
pdf: PDF_papers/gallagher1973.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'No DOI is printed on the scan. The Optica pattern for this volume and page gives 10.1364/JOSA.63.000864, verify at submission.'
  - 'The printed path-length line reads (0.213 +- 0.04) cm / cos(41.85 deg) = 0.286 +- 0.006 cm (p. 867). P. 866 gives the windows as 2.13 +- 0.04 mm apart, so the 0.04 on p. 867 is a misprint for 0.004.'
verified_date: 2026-09-14
summary: >
  Absolute rubidium densities from D-line absorption at 325.7 to 339.2 K,
  six points at 5 per cent each with 0.7 to 1.0 K thermometry, which fall
  4 per cent below Nesmeyanov's four-term correlation, the record's
  headline density law, and 33 to 38 per cent below the Alcock form. The
  only absolute measurement in the held set that supports the four-term
  law. Its 430 K resonance-broadening datum leans 20 per cent the other
  way, conditional on a theoretical cross section.
loci:
  - methods/07
section: method-anchors
---
# gallagher1973

Held, six pages, read in full against the PDF on 2026-09-14. Table I and
the oscillator strengths read twice.

## What it covers

Absolute absorption on the 85Rb D2 hyperfine component a at 7800 A (one
row on the D1 line at 7947 A) in a Pyrex cell, with a narrow-line lamp,
a Fabry-Perot analysis of the full line profile, and a line-centre optical
depth K read against calculated profiles (Figs. 3 and 4, p. 867). The
density follows from eq. (4), p. 867, with the absorption oscillator
strength and the cell length. A separate resonance-broadening
(Hanle-effect depolarisation) measurement gives one more density near
430 K, conditional on a theoretical cross section.

## The claims, with pages

1. Table I (p. 868), total density in units of 1e11 cm^-3, each 5 per
   cent: 1.32 at 325.7 +- 0.7 K. 1.43 at 327.0 +- 0.7 K. 2.72 at 334.3 +-
   0.8 K. 2.36 at 333.8 +- 0.8 K. 3.82 at 339.2 +- 1.0 K. 4.02 at 339.2 +-
   1.0 K on the 7947 A line. Total is 1.03 times the 85Rb density, with
   85Rb/87Rb = 32 in the cell (p. 867). The 5 per cent is the mean-square
   sum of about 3 per cent in K, 3 per cent in f and 2 per cent in L
   (p. 868).
2. Oscillator strengths from the authors' own Hanle-effect lifetimes:
   f(D1) = 0.317 +- 0.008 and f(D2) = 0.673 +- 0.015, each within 6 per
   cent of other values (p. 867). Most of the analysis is on the 7800 A
   line (p. 867), so the densities rest on f(D2).
3. Nesmeyanov's constants, Table II (p. 868), for eq. (5a) log10 p(torr)
   = -A/T - B log10 T + C + D T: A = 4529.6, B = 2.991, C = 15.8825,
   D = 0.00059, with a footnote that additional digits were rounded off.
   Ditchburn and Gilmour's constants A = 4302, B = 1.5, C = 11.722, D = 0
   fit Killian's data at 310 to 370 K. The two sets differ by 25 per cent
   in the data's region (p. 868). The paper's own reading is that
   Nesmeyanov's expression fits its data excellently, probably by
   coincidence (p. 868).
4. The comparison the paper states (p. 868): its values are about 25 per
   cent below Killian's in the same region and about 60 per cent above
   Scott's.
5. The 430 K resonance-broadening datum sits 20 per cent above
   Nesmeyanov's curve and 10 per cent above Ditchburn and Gilmour's, with
   about 5 per cent experimental uncertainty, an unestimated uncertainty
   in the theoretical cross section, and about 2 K in temperature, which
   is 10 per cent in density (p. 868).
6. Equilibrium in Pyrex: the measurements show an equilibrium Rb vapour
   pressure is reached in a Pyrex cell from 310 to 450 K, in contradiction
   of Jarrett's observation that the density depends on the cell's
   preparation ([jarrett1964](jarrett1964.md)), with the caution that the
   wall pumping must be saturated by running the cell hot (p. 865). This
   cell was held near 450 K for days first, and no dependence on its
   temperature history was seen (p. 866). The same page records that the
   coated cell of Gibbs and Hull reported pressures far below equilibrium
   (p. 865), a second instance of the cell-density caution.
7. Thermometry: four thermocouples on the cell, spread about 0.5 K, cell
   temperature to 0.8 K (p. 866). The per-row errors are in Table I.
8. K at line centre 0.96 +- 0.02 (Fig. 4 caption, p. 867). Path length
   0.286 +- 0.006 cm (p. 867, see the verify flag).

## Validity

An absolute density with the density-determining quantities (K, f, L)
each measured by the authors and a stated thermometry. The reservation is
the oscillator strength: against the record's `TAU_5P32_S` = 26.24 ns
([volz1996](volz1996.md)) the D2 absorption oscillator strength is 0.696
(calculated here from A lambda^2 m_e c epsilon_0 / (2 pi e^2) times the
statistical-weight ratio 2), 3.4 per cent above the paper's 0.673, so the
paper's densities revise down by 3.3 per cent when its f is replaced by
the modern one. The D1 value 0.317 is 7.3 per cent below the 0.342 the
record's `TAU_5P12_S` = 27.70 ns implies, three of its own sigma, but the
densities do not rest on it.

## What this record takes from it

1. **The first absolute support of the four-term law.** Against
   `rb5s6s.density.number_density_cm3` (Nesmeyanov's coefficients as
   `density.py` carries them) the six Table I points give measured over
   law = 0.998, 0.966, 0.990, 0.895, 0.932 and 0.981, mean 0.96 with a
   scatter of 0.04 (calculated here), 0.93 with the modern f(D2). The
   thermometry of 0.8 K is 6.8 per cent in density at 330 K, where
   d ln N / dT is 8.5 per cent per kelvin. So the record's headline law is
   supported at 326 to 339 K at the 4 to 7 per cent level, with a 5 per
   cent per-point bar and a 7 per cent thermometry bar.
   `results/density_laws.csv` carries no such row: its Nesmeyanov support
   is [siddons2008](siddons2008.md) with the note that no per cent on the
   density is stated. This paper states one.
2. **At 330 K it refuses the Alcock form.** The two-term law sits 1.38,
   1.36 and 1.33 times Nesmeyanov's at 325.7, 330 and 339.2 K
   (calculated here), a 3.6 K offset on the same d ln N / dT. The paper's stated
   0.8 K excludes an offset of that size, so at these temperatures the
   absorption arm is 4 sigma from the Alcock law on the paper's own
   budget. Its "25 per cent less than Killian" is that gap as the authors
   saw it, since the Alcock equation is Killian's lineage
   ([achar2025](achar2025.md)).
3. **At 430 K the other arm leans the other way.** Twenty per cent above
   Nesmeyanov at 430 K is within 1 per cent of the Alcock law, whose ratio
   to Nesmeyanov's is 1.19 there (calculated here). But that datum is
   conditional on a theoretical resonance-broadening cross section the
   paper cannot bound, and carries 10 per cent from 2 K.
4. **Neither arm reaches the archive.** The absorption points end at
   339 K, the resonance point sits at 430 K, and the archive runs 343 to
   403 K between them. Read for the joint fit's density prior: the
   four-term law is anchored at 7 per cent at 330 K and extrapolated 70 K
   upward, with one conditional datum at 430 K leaning 20 per cent toward
   the two-term law. The 20 per cent `N_SCALE_FRAC_SYST` in `density.py`
   is not refuted by this paper. What the paper refuses is the reading
   that the two laws are reconciled by a 3 to 4 K thermometry offset on
   this side, which [siddons2008](siddons2008.md) and the CSV's
   `ratio_as_kelvin` rows offer as the reconciliation: this paper's
   thermometry is stated and does not allow it, so the offset, if that is
   what it is, sits on the other side.

## Conflicts with the record

The `ratio_as_kelvin` reading above, which is a reading and not a cell.
No committed number moves. The record's `SIGMA_D1_CM2` (ENVELOPE, 1.5e-11
cm^2) is not touched by this paper, whose K is a line-centre optical
depth for a narrow-line source and not a Doppler-averaged cross section.
