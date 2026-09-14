---
citekey: alcock1984
type: article
authors:
  - Alcock, C. B.
  - Itkin, V. P.
  - Horrigan, M. K.
title: 'Vapour Pressure Equations for the Metallic Elements: 298-2500K'
journal: Can. Metall. Q.
volume: 23
number: 3
pages: 309--313
year: 1984
doi: null
arxiv: null
pdf: PDF_papers/alcock1984.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'No DOI is printed on the PDF. The publisher record for this article carries 10.1179/cmq.1984.23.3.309. verify at submission before it is entered.'
verified_date: 2026-09-14
summary: >
  The source of the two-term rubidium vapour-pressure law the record
  labels AIH, log10 P/atm = 4.312 - 4040/T for the liquid, with its own
  accuracy claim (better than 5 per cent for the practical two-term form,
  1 per cent for the precise four-term form) and the reading that claim
  deserves, a fit residual against evaluated thermochemical tables and
  not an experimental accuracy. The held Steck (revision 2.3.4) tabulates
  this law as its vapour-pressure model, citing this paper, which is not
  the law the record attributes to Steck.
loci:
  - methods/07
section: method-anchors
---
# alcock1984

Held, five pages, read in full against the PDF on 2026-09-14. Every Rb
coefficient below read twice.

## What it covers

Vapour-pressure equations for every metallic element to curium, from
298 K to 2500 K, each element given twice: a precise four-term form and a
practical two-term form. The input is evaluated thermochemical data
(Hultgren et al. 1973 and the authors' own assessments, refs 1 to 8 on
p. 309), not new measurements. The equations are intended for ideal gases
between 1e-15 and 1e-3 atm (abstract, p. 309).

## The claims, with pages

1. The form is log10 p(atm) = A + B/T + C log10 T + D T/1000, and the
   precise equations reproduce the evaluated data to better than 1 per
   cent. The practical equations, A + B/T only, to better than 5 per cent
   (abstract, p. 309). The 5 per cent is stated on p. 309 as the level
   selected to represent a reasonable experimental error, which makes it a
   fit criterion against the tables, not a measured accuracy. The same
   page adds that the equations are probably often over-precise once the
   experimental uncertainties of the original thermochemical data are
   taken into account.
2. Rubidium, practical (Table 2, p. 310): liquid A = 4.312, B = -4040,
   valid from the melting point to 550 K, refs 2 and 4. Solid A = 4.857,
   B = -4215, from 298 K to the melting point, refs 2, 4 and 8.
3. Rubidium, precise (Table 3, p. 312): liquid A = 8.316, B = -4275,
   C = -1.3102, no D term, melting point to 550 K.
4. The pressure window 1e-15 to 1e-3 atm (abstract). Rubidium at 130 C is
   2.0e-6 atm on this law (calculated here), inside it.

## Validity

The paper measures nothing. Its 5 per cent is how far the two-term form
strays from the four-term one and its 1 per cent how far the four-term
form strays from the selected tables. What those tables rest on for Rb is
the authors' own evaluation (ref 2, "to be published") and Gurvich's
compilation (ref 4). The absorption measurement of Gallagher and Lewis
1973 ([gallagher1973](gallagher1973.md)) sits about 25 per cent below the
Killian data this lineage descends from, and Achar et al. 2025
([achar2025](achar2025.md)) name the law as Killian's, later refined here.

## What this record takes from it

The record's envelope law is this paper's practical liquid equation, and
its rows reproduce it (calculated here here from the coefficients above against
`rb5s6s.density.number_density_cm3`): practical over Nesmeyanov is 1.320,
1.270, 1.234 and 1.209 at 70, 90, 110 and 130 C, matching
`results/density_laws.csv` `ratio_AIH_over_Steck` (1.3202, 1.2704, 1.2344,
1.2090) to 0.05 per cent. The precise form differs from the practical one
by -0.6, +0.6, +1.4 and +1.7 per cent at the same four temperatures, so
the record's choice of the two-term form costs under 2 per cent, inside
the paper's own 5 per cent. `scripts/run_density_laws.py` writes the torr
conversion as 2.881 where log10 760 = 2.8808, a 0.05 per cent rounding it
shares with Steck's own eq. (1).

## Conflicts with the record

1. **The name on the record's headline law.** The held Steck documents
   (`PDF_papers/Steck_2021_Rb85-D-line-data.pdf` and the 87Rb file, both
   revision 2.3.4 dated 8 August 2025 on their first page, while
   [steck_rb](steck_rb.md) carries `year: 2021`) give as their
   vapour-pressure model eq. (1), log10 Pv/torr = 2.881 + 4.312 - 4040/T
   for the liquid, cite this paper as their ref 5, and state the model as
   accurate to better than 5 per cent from 298 to 550 K.
   `rb5s6s/density.py` describes its four-term law as Nesmeyanov's
   correlation "as tabulated by Steck", `scripts/run_density_laws.py`
   labels that law `Steck` and this one `CRC`, and `docs/LITERATURE.md`
   section 7 calls Steck the vapour-pressure chain `density.py` uses. None
   of the three is true of the held Steck: it tabulates Alcock, and the
   four-term form is Nesmeyanov's as older Steck revisions and Siddons 2008
   Appendix A ([siddons2008](siddons2008.md)) carried it. The two laws and
   their 21 to 32 per cent gap over the archive are unchanged. What is
   wrong is the label, and a reader who checks `density.py` against the
   held Steck finds the other law under the name.
2. `results/density_laws.csv` row `support_alcock1984` reads the 5 per cent
   as "the law's own claim", which is correct, and should say it is a fit
   criterion against evaluated tables, since the row sits beside two rows
   that are comparisons with measured densities.
3. To check, not checked here: [cao2025](cao2025.md) says that paper takes
   its vapour pressure from Steck's 87Rb document. On any revision carrying
   eq. (1) that puts Cao's density axis on this law, beside Zameroski's, and
   the comparison table in `docs/quantities/self-broadening.md` does not
   say which axis each rung is on.
