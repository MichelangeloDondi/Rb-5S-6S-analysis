---
citekey: parthey2011
type: article
authors:
  - Parthey, Christian G.
  - Matveev, Arthur
  - Alnis, Janis
  - Bernhardt, Birgitta
  - Beyer, Axel
  - Holzwarth, Ronald
  - Maistrou, Aliaksei
  - Pohl, Randolf
  - Predehl, Katharina
  - Udem, Thomas
  - Wilken, Tobias
  - Kolachevsky, Nikolai
  - Abgrall, Michel
  - Rovera, Daniele
  - Salomon, Christophe
  - Laurent, Philippe
  - Hänsch, Theodor W.
title: 'Improved Measurement of the Hydrogen 1S-2S Transition Frequency'
journal: Phys. Rev. Lett.
volume: 107
number: 20
pages: 203001
year: 2011
doi: 10.1103/PhysRevLett.107.203001
arxiv: '1107.3101'
pdf: PDF_papers/Parthey_2011_hydrogen-1S-2S-improved-transition-frequency.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/parthey2011.md  # line-by-line against the held PDF, 2026-09-22: fixed a misattributed dc-Stark/quench claim (it is this paper's own text, not fischer2004's abstract), one verbatim-quote word restored ('lead', not 'led', matching the PDF), verify_flags paragraph count corrected. Extended 2026-09-22 to pp. 2-5 (the Monte Carlo systematic-correction paragraph and the Table I budget), see private/cache/lit_intake_2026-09-22_audits/parthey2011_extension.md
author: agent
routing: []
verify_flags:
  - 'Page 1 of the held arXiv:1107.3101v1 preprint (title, full author list,
    abstract, PACS numbers, the Fig. 1 beam-apparatus schematic and its
    caption, and the introduction in full -- three paragraphs, ending "a
    possible dc Stark shift within the nozzle" -- plus the opening of the
    apparatus-description section) read against the record on 2026-09-21.'
  - 'Pages 2-5 read in full on 2026-09-22 (pdftotext -layout extraction,
    single-column layout throughout), with pages 2, 3, 4 and 5 each
    additionally checked against the 150 dpi rendered page image. Page 2
    carries the Monte Carlo (MC) systematic-correction paragraph and the
    quadratic ac Stark paragraph (refs [16, 17], resolved on p. 5''s reference
    list to "N. Kolachevsky et al., Phys. Rev. A 74, 052504 (2006)" =
    kolachevsky2006 and "M. Haas et al., Phys. Rev. A 73, 052501 (2006)" =
    haas2006, both held). Page 3 carries the three-source quadrature breakdown
    of the second-order Doppler uncertainty (1.7, 0.8, 0.8 to 2.0, all x
    1e-15) and Fig. 3. Page 4 carries Table I, the full eighteen-row
    uncertainty budget. Page 5 carries the final result, Fig. 4, the
    acknowledgments and the numbered reference list including [16] and [17].'
verified_date: 2026-09-22
summary: >
  A 4.2e-15 measurement of hydrogen 1S-2S on a 5.8 K cryogenic atomic beam
  crossing a focused standing-wave excitation region (1/e^2 waist 292 um),
  quenched by a localized dc field. A Monte Carlo simulation (refs [16, 17] =
  kolachevsky2006 and haas2006) corrects the second-order Doppler effect and
  the quadratic ac Stark shift. Table I's full budget totals 10.4 Hz
  (4.2e-15), dominated by statistics (2.6e-15), the second-order Doppler
  effect (2.0e-15) and the line shape model (2.0e-15). Direct sibling of Haas
  et al. 2006's trajectory-resolved AC-Stark model (haas2006, held as of
  2026-09-22) and predecessor of Matveev 2013 (matveev2013, held as of
  2026-09-22) and Grinin 2020 (grinin2020). Improves on fischer2004 by a
  factor of 3.3.
loci: []
section: transit-time
---

# parthey2011

VERIFIED for the full letter. Page 1 (title, authors, abstract, PACS, Fig. 1
and its caption, introduction in full) was read on 2026-09-21. Pages 2-5,
including the Monte Carlo systematic-correction paragraph, the quadratic ac
Stark paragraph, and the Table I uncertainty budget, were read on 2026-09-22
(see the What-pages-2-5-add section below).

## What page 1 gives, verbatim

"We have measured the 1S − 2S transition frequency in atomic hydrogen via two
photon spectroscopy on a 5.8 K atomic beam. We obtain f1S−2S =
2 466 061 413 187 035 (10) Hz for the hyperfine centroid. This is a fractional
frequency uncertainty of 4.2 × 10⁻¹⁵ improving the previous measurement by our
own group [M. Fischer et al., Phys. Rev. Lett. 92, 230802 (2004)] by a factor
of 3.3. The probe laser frequency was phase coherently linked to the mobile
cesium fountain clock FOM via a frequency comb."

Figure 1's caption, in part, verbatim: "Schematic of the beam apparatus. A
standing laser wave at 243 nm (between grey mirrors) with a 1/e² waist radius
of w0 = 292 μm at the flat cavity front mirror excites the sharp 1S − 2S
transition in a co-linearly propagating cold thermal beam of atomic hydrogen
emerging from a cooled copper nozzle. The 2S state is detected after quenching
with a localized electric field which releases a Lyman-α photon."

The introduction's own framing, verbatim: "For the last five decades
spectroscopy on atomic hydrogen along with its calculable atomic structure
have been fueling the development and testing of quantum electrodynamics
(QED) and has lead" [sic] "to a precise determination of the Rydberg constant
and the proton charge radius."

## What pages 2-5 add, verbatim and from Table I

The Monte Carlo systematic correction, verbatim (p. 2): "The residual
uncertainty of this procedure was determined by evaluating a second data set
that was generated using a Monte Carlo (MC) simulation [16, 17] in exactly the
same way. For various simulation parameters such as temperature, geometry and
initial 1S velocity distributions we find the uncertainty to be smaller than
2.0 x 10^-15 which is below the current statistical uncertainty of 2.6 x
10^-15." Refs [16, 17] resolve, on p. 5's reference list, to "N. Kolachevsky et
al., Phys. Rev. A 74, 052504 (2006)" (kolachevsky2006, held) and "M. Haas et
al., Phys. Rev. A 73, 052501 (2006)" (haas2006, held): the same Monte Carlo of
10,000 trajectories through the Gaussian excitation mode that kolachevsky2006's
own note describes, integrating the two-photon Bloch equations of motion
haas2006 derives along each atom's path, with a time-dependent second-order
Doppler and ac Stark detuning and an intensity-dependent ionization loss.
<!-- rendered-page: p. 2 -->

The same paragraph continues into the quadratic ac Stark shift, verbatim
(p. 2): "However, a small quadratic contribution [16] must be taken into
account, before we can apply a linear extrapolation using the stable, but
otherwise not precisely calibrated laser power readings. The main contribution
to this non-linear ac Stark shift is due to ionization of the 2S atoms by a
third 243 nm photon that removes preferably atoms that see larger laser
powers. For excitation laser powers of 300 mW as present in our experiment the
quadratic ac Stark shift contributes on the order of 1 x 10^-14 as derived
from the MC simulations. This is sufficiently small to rely on these
simulations that assume a Maxwell distribution for the 1S atoms using the
absolute laser power within 20% relative uncertainty. Modeling and subtracting
the delay dependent quadratic ac Stark effect in this way then allows to
linearly extrapolate the line centers, without knowing the exact laser power
calibration. This procedure reduces the overall ac Stark shift uncertainty to
0.8 x 10^-15."
<!-- rendered-page: p. 2 -->

Page 3 breaks the "2nd order Doppler effect" row of Table I into three
quadrature components, verbatim: "The uncertainty in the second order Doppler
correction is caused by three main sources. First, the statistical
uncertainty obtained from linear regression analysis of ∆fdp(P) contributes
1.7 x 10^-15. Second, during the velocity measurements the 1S-2S spectroscopy
laser was kept on the resonance only within ±160 Hz. MC simulation reveals an
associated uncertainty of 0.8 x 10^-15. Third, the 45° angle between the
atomic beam and the laser beam used to measure the velocity distribution can
only be adjusted within ±1°. This translates to an uncertainty in the second
order Doppler effect of 0.8 x 10^-15. Summing in quadrature leads to an
overall uncertainty" of the second order Doppler correction, given on the
same page as "of the second order Doppler correction of 2.0 x 10^-15."
Only the middle of these three (0.8e-15, from laser-lock jitter during the
velocity measurement) is MC-determined. The other two are a linear-regression
statistical uncertainty and a mechanical angle tolerance.
<!-- rendered-page: p. 3 -->

Table I (p. 4), the full uncertainty budget, sigma in Hz and sigma/f_1S-2S in
units of 1e-15:

| contribution | sigma [Hz] | sigma/f [1e-15] |
|---|---|---|
| statistics | 6.3 | 2.6 |
| 2nd order Doppler effect | 5.1 | 2.0 |
| line shape model | 5.0 | 2.0 |
| quadratic ac Stark shift (243 nm) | 2.0 | 0.8 |
| ac Stark shift, 486 nm quench light | 2.0 | 0.8 |
| hyperfine correction | 1.7 | 0.69 |
| dc Stark effect | 1.0 | 0.4 |
| ac Stark shift, 486 nm scattered light | 1.0 | 0.4 |
| Zeeman shift | 0.93 | 0.38 |
| pressure shift | 0.5 | 0.2 |
| blackbody radiation shift | 0.3 | 0.12 |
| power modulation AOM chirp | 0.3 | 0.11 |
| rf discharge ac Stark shift | 0.03 | 0.012 |
| higher order modes | 0.03 | 0.012 |
| line pulling by mF = 0 component | 0.004 | 0.0016 |
| recoil shift | 0.009 | 0.0036 |
| `FOM` (fountain clock) | 2.0 | 0.81 |
| gravitational red shift | 0.04 | 0.077 |
| total | 10.4 | 4.2 |

The quadratic ac Stark row and the MC-determined piece of the second-order
Doppler row are the two places the Monte Carlo of refs [16, 17] enters Table I
directly. Every other row is measured or bounded by a separate method (Zeeman
field reversal, dc Stark field scan, blackbody temperature monitoring, and so
on, pp. 3-4), and the two largest rows (statistics, line shape model) do not
depend on the MC at all.

## Use in this record

This is the closest openly available instance of the precedent the search was
asked to find (priority 1): a Doppler-free two-photon transition measured on a
beam of atoms crossing a standing-wave excitation region, where the beam
geometry (the 292 μm 1/e² waist quoted above) sets a transit time that the fit
must treat jointly with the AC-Stark shift, not by convolution, exactly this
record's own methodological stance (`rb5s6s/ramp_transit.py`,
`rb5s6s/lineshape.ramp_mixture`). A possible dc Stark shift within the
nozzle, a systematic this paper's own introduction (p. 1) describes fixing
via a newly introduced quench laser ("a quench laser resetting the
population to the ground state right after the hydrogen nozzle was
introduced. This removes possible frequency shifts due to the high density
of atoms and a possible dc Stark shift within the nozzle"), is a direct
analogue of the ac field this record fits for, in a different (dc) regime.
This is parthey2011's own text describing its own improvement over the
previous apparatus, not something named in fischer2004's abstract:
fischer2004's abstract (independently verified, verbatim, in that paper's
own audited note) contains no quench or Stark content at all.
Fischer 2004 (fischer2004), Haas 2006 (haas2006, held and read in full as of
2026-09-22) and Matveev 2013 (matveev2013, held and read in full as of
2026-09-22) bracket it as the lineage's earlier and later members. The
"paywalled, not held" state carried here for both papers until 2026-09-21 is
retracted as of 2026-09-22, both having since been obtained.
Grinin 2020 (grinin2020) is the same group's most recent instance, on a
different line (1S-3S) with a frequency comb instead of a single cw laser.

For chapter 7's lineage paragraph: the Monte Carlo correction and Table I
above (pp. 2-4) are the quantitative anchor for this lineage's claim to carry
the trajectory and the light shift jointly, not by convolution afterward. The MC
of refs [16, 17] enters only two of Table I's eighteen rows (the quadratic ac
Stark shift, 0.8e-15, and part of the second-order Doppler row, also
0.8e-15), inside a 4.2e-15 total dominated by statistics (2.6e-15) and the
line shape model (2.0e-15), which are unrelated to it. The trajectory term is
carried explicitly and quantified, but it is not this measurement's dominant
uncertainty. The lineage paragraph's claim should be that carrying it
explicitly avoids a bias in the dominant terms, not that it dominates the
budget itself.
