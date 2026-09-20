---
citekey: sinha2026
type: misc
authors:
  - Sinha, Shivam
  - Achar, Sumit
  - Satheesh, Sankar
  - Sharma, Arijit
title: 'Precision Measurement of the Saturation Intensity in Rubidium at 420 nm'
journal: arXiv preprint
year: 2026
doi: null
arxiv: '2606.30871'
pdf: PDF_papers/Sinha_2026_Rb-420nm-5S-6P32-saturation-intensity-6P-hyperfine-constants.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1, 2, 3, 8, 10 and 11 read against the PDF on 2026-09-20 (title/abstract,
    introduction, the saturation-intensity theory section, the systematic-uncertainty table
    and isotope comparison table, the hyperfine-constant results table, and the conclusion).
    The experimental-setup section (temperature control, beam geometry, frequency calibration)
    and the theory of the hyperfine constants themselves are not read.
  - No journal is named anywhere in the held PDF, which carries only the arXiv identifier
    2606.30871v3, dated 21 Jul 2026, so it is recorded here as an arXiv preprint with no DOI.
  - 'Adversarial re-audit, 2026-09-20: one page-range correction. "Section II, pp. 2-3" for
    the branching-ratio-corrected saturation-intensity derivation understated the span --
    the general two-level/Wigner-Eckart machinery is on pp. 2-3, but the branching-ratio
    correction itself (Eqs. (11)-(13), the beta ~= 0.23 factor for the open 6P3/2 decay
    topology) is on p. 4, so the citation is widened to pp. 2-4. Every other value, quote and
    page reference in this note was checked against the PDF (via pypdf, cross-checked with
    pdftotext -layout for the arXiv/date fields) and found correct. No other change made.'
verified_date: null
summary: >
  The first reported experimental measurement of the saturation intensity of the Rb
  5S1/2 -> 6P3/2 transition at 420 nm, for both isotopes, together with a fresh measurement of
  the 6P3/2 hyperfine constants A and B that agrees with prior literature including this
  record's own held glaser2019. The 6P3/2 state is the one this record's glaser2019 note
  already places inside the 6S-6P group of the Delta-alpha(993) polarizability sum, so this
  paper is useful background on that same state's structure and decay (natural linewidth,
  branching ratio) even though its own new numbers, the saturation intensity and the hyperfine
  constants, do not themselves enter any calculation this record currently performs.
loci: []
section: method-anchors
---
# sinha2026

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | Indian Institute of Technology Tirupati | p. 1 |
| dated | July 23, 2026 | p. 1 |
| Isat, 87Rb F=2 -> F'=3 (measured, weighted mean) | 23.54 +- 1.03 mW/cm^2 | p. 1 abstract and p. 11 |
| Isat, 87Rb F=2 -> F'=3 (theory) | 23.45 mW/cm^2 | p. 8, Table II |
| Isat, 85Rb F=3 -> F'=4 (measured, weighted mean) | 25.39 +- 1.16 mW/cm^2 | p. 1 abstract and p. 11 |
| Isat, 85Rb F=3 -> F'=4 (theory) | 25.54 mW/cm^2 | p. 8, Table II |
| optimal operating temperature | 82.02 +- 0.73 C | p. 1 abstract |
| total systematic uncertainty | 4.47% (85Rb), 4.28% (87Rb) | p. 8, Table I |
| 6P3/2 natural linewidth (cited, not measured here) | 1.42 MHz | p. 1 |
| 6P3/2 -> 5S1/2 branching ratio (cited, not measured here) | about 23% | p. 1 |
| Isat, D2 line 87Rb F=2 -> F'=3 (cited, for comparison) | about 3.58 mW/cm^2 | p. 8 |
| A(87Rb), 6P3/2 (this work) | 27.75(03) MHz | p. 10, Table III |
| B(87Rb), 6P3/2 (this work) | 3.94(05) MHz | p. 10, Table III |
| A(85Rb), 6P3/2 (this work) | 8.21(006) MHz | p. 10, Table III |
| B(85Rb), 6P3/2 (this work) | 8.15(03) MHz | p. 10, Table III |
| A(87Rb), 6P3/2, comparison (Glaser et al., i.e. glaser2019) | 27.71(15) MHz | p. 10, Table III |
| B(87Rb), 6P3/2, comparison (Glaser et al.) | 4.03(04) MHz | p. 10, Table III |
| A(85Rb), 6P3/2, comparison (Glaser et al.) | 8.16(01) MHz | p. 10, Table III |
| B(85Rb), 6P3/2, comparison (Glaser et al.) | 8.13(05) MHz | p. 10, Table III |

## What it says, in its own terms

**Why 420 nm.** The 5S1/2 -> 6P3/2 transition gives direct optical access to a state with a
narrow linewidth (1.42 MHz) and is the decay channel used as the primary detection mechanism
in recent 5S1/2 -> 5D5/2 two-photon optical clocks at 778.1 nm (p. 1). Despite that role, the
paper states the saturation intensity of the 420 nm line itself had not been experimentally
determined before this work, with prior estimates in the literature "spanning more than an
order of magnitude" (p. 2), partly because the multiple decay channels out of 6P3/2 complicate
defining an effective two-level transition strength.

**The method.** Doppler-free saturated-absorption spectroscopy (SAS) on both isotopes in a
100 mm vapour cell, with a first-principles calculation of Isat built up from the two-level
result through the Wigner-Eckart theorem, branching-ratio-corrected for the open decay
topology of 6P3/2 (Section II, pp. 2-4: the general two-level derivation is on pp. 2-3,
the branching-ratio correction itself, Eqs. (11)-(13) and beta = 0.23, is on p. 4). The
saturation intensity is extracted from the
power-broadening of the Doppler-free Lamb dip, fitting linewidth vs. power and extrapolating
to zero intensity for the natural linewidth. Systematic uncertainty is dominated by beam-
diameter measurement and frequency calibration (Table I, p. 8), combined in quadrature to
4.47% (85Rb) and 4.28% (87Rb).

**The result.** Measured Isat values agree with the paper's own first-principles calculation
to within the stated uncertainty for both isotopes (Table II, p. 8), and are about six to
seven times larger than the well-known D2-line value, attributed to the weaker effective
coupling from the omega^3 scaling of the spontaneous-emission rate and the much smaller (23%)
branching ratio back to the ground state. The same Doppler-free spectra also yield the
6P3/2 hyperfine constants A and B for both isotopes (Table III, p. 10), in agreement with five
prior literature values including Glaser et al. (this record's own glaser2019), Safronova,
Arimondo, Sansonetti and Navarro-Navarrete.

## What it is worth here

Useful background on a state this record's atomic-structure ladder already touches, not a
number this record currently consumes. glaser2019's own note in this list states that Rb
6P level positions enter the 6S polarizability sum through the 6S-6P coupling, the larger half
of the Delta-alpha(993) cancellation. This paper characterises that same 6P3/2 state's
saturation behaviour and hyperfine structure with fresh, independent precision, and its
Table III cross-validates glaser2019's own A and B values to within their combined
uncertainties. Nothing here is a lifetime or a dipole-matrix-element measurement, so it does
not directly refine the polarizability-sum term glaser2019 feeds. It is useful chiefly as
corroboration that the 6P3/2 structure this record's polarizability calculation relies on is
solid, and as a pointer to the natural linewidth and branching ratio (1.42 MHz, 23%) should
either number ever need a citation.
