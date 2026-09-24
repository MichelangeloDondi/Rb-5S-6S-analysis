---
citekey: matveev2013
type: article
authors:
  - Matveev, Arthur
  - Parthey, Christian G.
  - Predehl, Katharina
  - Alnis, Janis
  - Beyer, Axel
  - Holzwarth, Ronald
  - Udem, Thomas
  - Wilken, Tobias
  - Kolachevsky, Nikolai
  - Abgrall, Michel
  - Rovera, Daniele
  - Salomon, Christophe
  - Laurent, Philippe
  - Grosche, Gesine
  - Terra, Osama
  - Legero, Thomas
  - Schnatz, Harald
  - Weyers, Stefan
  - Altschul, Brett
  - Hänsch, Theodor W.
title: 'Precision Measurement of the Hydrogen 1S-2S Frequency via a 920-km Fiber Link'
journal: Phys. Rev. Lett.
volume: 110
number: 23
pages: 230801
year: 2013
doi: 10.1103/PhysRevLett.110.230801
arxiv: null
pdf: PDF_papers/Matveev_2013_hydrogen-1S-2S-920km-fiber-link-remote-cesium-clock.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand/audits/matveev2013.md  # claim-by-claim against the held PDF, 2026-09-22: fixed a conflated Fig. 3 number in verify_flags (35(44) Hz, splicing two different rows, corrected to 35(10) Hz), tightened an overstated scope claim about parthey2011's own note ("only page 1" narrowed to that note's own stated scope); no exact quotation, Table I row, or SME equation needed correction
author: agent
routing: []
verify_flags:
  - 'The full 5-page held PDF (the published APS typeset version, PRL 110, 230801
    (2013), DOI 10.1103/PhysRevLett.110.230801 printed on p. 1, footer
    "0031-9007/13/110(23)/230801(5)") was read in full, all five pages, directly
    from the rendered page images on 2026-09-22: title, the full 20-author list
    and five affiliations, abstract, PACS numbers, Fig. 1 (apparatus schematic)
    and its caption, the entire two-column body through Table I and Figs. 2-3,
    the Lorentz-invariance (SME) derivation (Eqs. 2-4), the acknowledgments, and
    the 22-item reference list on p. 5.'
  - 'No arXiv identifier is printed anywhere on this held copy (an APS/Acrobat-
    Distiller typeset PDF with a "week ending" running head and a DOI line, not
    an arXiv preprint scan); the `arxiv` field is left null rather than filled
    from memory, unlike this record''s parthey2011 and fischer2004 notes, which
    hold arXiv preprints and cite their identifiers directly.'
  - 'The apparatus temperature this paper states for its own hydrogen beam, p. 2
    col. 1 ("a beam of cold 6 K hydrogen atoms"), differs from the figure each of
    the other two lineage papers already held here states for what is described
    as the same or a closely related apparatus: parthey2011''s Fig. 1 caption
    gives 5.8 K, fischer2004''s p. 2 text gives 5-6 K. All three numbers are
    quoted from their own source and none is adjusted to match another; the
    discrepancy is flagged here, not resolved.'
  - 'Self-consistency check performed here, not stated by the paper itself:
    Table I''s caption gives F_stat = 2466 061 102 474 893.1 Hz and Table I''s
    own Total row gives Delta_total = +310 712 125.2 Hz; their sum,
    2466 061 413 187 018.3 Hz, matches Eq. (1)''s headline value,
    2466 061 413 187 018(11) Hz, to the stated rounding.'
  - 'The November 2010 measurement campaign this paper reports (622 scans, 22-26
    November 2010) is a separate data-taking run from the "05/2010" campaign
    labelled in this paper''s own Fig. 3, which is Ref. [7] = parthey2011''s
    result (the red hollow point at 35(10) Hz, chi2/dof = 1.9). This paper''s own
    new result is the "11/2010" point (18(11) Hz, chi2/dof = 2.4). The two are
    not the same dataset re-analysed, despite sharing the apparatus and much of
    the author list.'
  - 'Cross-checked against this record''s own holdings: Ref. [6] in this paper''s
    bibliography (p. 5), "M. Fischer et al., Phys. Rev. Lett. 92, 230802 (2004)",
    and Ref. [7], "C. G. Parthey et al., Phys. Rev. Lett. 107, 203001 (2011)",
    match fischer2004 and parthey2011 as already held and VERIFIED in this
    repository''s own docs/lit/, field for field (journal, volume, page, year).'
verified_date: 2026-09-22
summary: >
  A 4.5e-15 measurement of hydrogen 1S-2S, f = 2466 061 413 187 018(11) Hz, on the
  same cryogenic atomic-beam apparatus as parthey2011 (this paper's own Ref. [7])
  but compared for the first time against a REMOTE cesium fountain (PTB's CSF1)
  via a new 920 km stabilized fibre link, with a photoelectron detector giving
  about a factor of 2 smaller statistical uncertainty. Dominant systematics:
  second-order Doppler (8.0 Hz, revised up from 5.1 Hz after a Faraday-cage
  stray-field finding) and the line-shape model (5.0 Hz). The ac-Stark budget
  separates a modelled, excitation-geometry-resolved quadratic term at 243 nm
  (-10.7(2.0) Hz, Monte Carlo) from a linear term removed by extrapolation to
  zero probe power, plus two 486 nm quench-beam terms (2.0 and 1.0 Hz). Also
  derives new Lorentz-boost-violation (SME) bounds from four measurement epochs,
  tangential to this record's own interest.
loci: []
section: transit-time
---

# matveev2013

VERIFIED. Held (the published PRL typeset PDF, 5 pages). Read in full, all five
pages, directly from the rendered PDF page images on 2026-09-22.

## What the paper reports, verbatim

The abstract, in full (p. 1): "We have measured the frequency of the extremely
narrow 1S-2S two-photon transition in atomic hydrogen using a remote cesium
fountain clock with the help of a 920 km stabilized optical fiber. With an
improved detection method we obtain" f1S−2S = 2466 061 413 187 018(11) Hz "with a
relative uncertainty of" 4.5×10⁻¹⁵, "confirming our previous measurement obtained
with a local cesium clock [C. G. Parthey et al., Phys. Rev. Lett. 107, 203001
(2011)]. Combining these results with older measurements, we constrain the
linear combinations of Lorentz boost symmetry violation parameters" c(TX) =
(3.1±1.9)×10⁻¹¹ and 0.92c(TY)+0.40c(TZ) = (2.6±5.3)×10⁻¹¹ "in the standard model
extension framework [D. Colladay, V. A. Kostelecky, Phys. Rev. D 58, 116002
(1998)]."

So the paper is explicitly framed as a confirmation of parthey2011's own result
(this record's own held parthey2011), obtained by an independent method (a
remote clock reached over a new fibre link, not a local mobile fountain), not a
supersession of it: the headline number, uncertainty, and the specific
comparison to Ref. [7] = parthey2011 are stated in the abstract's own words.
The paper's second half derives new Lorentz-invariance (SME) bounds from
combining this and three earlier hydrogen 1S-2S epochs.

## The apparatus and the two measurement campaigns

Page 2, col. 1, verbatim: "The current hydrogen beam apparatus has been
described before [7]. In brief, the two-photon 1S-2S transition is driven in a
beam of cold 6 K hydrogen atoms that travel collinearly within a standing wave
of the exciting laser to cancel the first order Doppler effect. A small
electric field (10 V/cm) at the end of the atomic beam deexcites the 2S state
at a well-defined point and forces the release of a 121 nm" Lyman-α "photon.
Previously, these photons were detected with a photomultiplier [4,6,7]. For
this measurement we instead detect photoelectrons created when the" Lyman-α
"photons hit the graphite coating covering the 2S detector inner walls. The
photoelectrons are collected by a channeltron whose front face is biased at
+270 V. The atomic beam is shielded from this voltage by a second Faraday cage
to maintain a well localized deexcitation point. With this detector we obtain
more than an order of magnitude larger signal due to its solid acceptance
angle of almost" 4π.

So the apparatus (cryogenic 6 K beam, standing-wave excitation, dc-field
deexcitation) is unchanged from Ref. [7] = parthey2011. What changed is the
detector (a channeltron-collected photoelectron detector replacing the
photomultiplier used in Refs. [4,6,7]), giving the order-of-magnitude signal
gain shown in Fig. 2's comparison of "the data scattering of the previous
photomultiplier detector (red circles) with the photoelectron detector (black
squares)" (Fig. 2 caption, p. 2).

Page 2, col. 1, continued, verbatim: "During five days from November 22 to 26
of 2010, the" 1S(F=1)-2S(F=1) "hyperfine line component has been scanned 622
times. The data evaluation to find the line centers follows that of Ref. [7].
To reduce the second order Doppler effect we periodically block the
excitation light and record photons from the excited state with certain time
delays."
And, p. 2 col. 2: "The signal counts are sorted into time delay bins τ1 =
10–210 μs, τ2 = 210–410 μs, ..., τ8 = 1410–1610 μs. We fit each hydrogen
spectral line with a Lorentzian which is a good approximation of the line
shape for delays τ4 = 610–810 μs and larger."

This November 2010 campaign is a separate data-taking run from the one
labelled '05/2010' in this paper's own Fig. 3 (which is Ref. [7] =
parthey2011's result). This paper's own new point is labelled '11/2010' (see
below). The two share the apparatus and most of the author list but are not
the same scans re-analysed.

## The systematic budget (Table I, p. 3)

Table I's caption, verbatim: "Corrections and uncertainties for the hydrogen
1S-2S transition frequency. Corrections are given relative to the value
obtained after statistical averaging" Fstat = 2466 061 102 474 893.1 Hz. The
caption adds that Δ denotes the correction and σ the uncertainty. The full
table, reproduced exactly (all nineteen rows plus the total):

| Effect | Δ (Hz) | σ (Hz) |
|---|---|---|
| Statistics | 0 | 3.3 |
| Second order Doppler effect | +34.2 | 8.0 |
| Line shape model | 0 | 5.0 |
| Quadratic ac Stark shift (243 nm) | −10.7 | 2.0 |
| ac Stark shift, 486 nm quench beam | 0 | 2.0 |
| Hyperfine correction | +310 712 229.4 | 1.7 |
| dc Stark effect | 0 | 1.0 |
| ac Stark shift, 486 nm scattered | 0 | 1.0 |
| Zeeman shift | 0 | 0.93 |
| Pressure shift | 0 | 0.5 |
| Blackbody radiation shift | +1.0 | 0.3 |
| Power modulation AOM chirp | 0 | 0.3 |
| rf discharge ac Stark shift | 0 | 0.03 |
| Higher order modes | 0 | 0.03 |
| Line pulling by mF=0 component | 0 | 0.004 |
| Recoil shift | 0 | 0.009 |
| CSF1 | 0 | 1.87 |
| Fiber link | 0 | 0.025 |
| Gravitational redshift | −128.70 | 0.11 |
| **Total** | **+310 712 125.2** | **10.8** |

The two dominant systematic uncertainties are the second-order Doppler effect
(8.0 Hz) and the line-shape model (5.0 Hz), followed by statistics (3.3 Hz).
The second-order-Doppler figure was revised upward during the analysis. Page
2, col. 2, verbatim: "After completion of the experiment we realized that the
shielding factor of the Faraday cage protecting the atoms from the channeltron
was insufficient. The additional field does not cause a significant dc Stark
shift, since it is well separated from the excitation region by a 2.1 mm diam
aperture. Most atoms contributing with delays larger than" τ3 = 410–610 μs "are
excited at the first half of the excitation region at distances of a few
centimeters from this aperture. However, this stray field increases the
uncertainty about the location of the deexcitation point which translates into
an additional uncertainty of the velocity distribution and hence the second
order Doppler effect. We thus increased its contribution to the error budget
from 5.1 to 8.0 Hz."

Immediately after Table I, p. 3, verbatim: "It should be noted that the
statistical uncertainty is smaller than in Ref. [7] due to the higher
detection efficiency. Summing up all uncertainties in quadrature and taking
into account frequency corrections [7] we find

f1S-2S = 2466 061 413 187 018(11) Hz     (1)

for the hyperfine centroid computed with the same hyperfine constants as in
the previous measurement [7]. ... The new measurement is in good agreement
with the measurement [7] made with a local cesium fountain clock but has
almost a factor of 2 smaller statistical uncertainty (3.3 Hz) as shown in
Figs. 2 and 3 due to the higher detection efficiency."

(Self-check, not stated by the paper: Fstat + Δtotal = 2466 061 102 474 893.1 +
310 712 125.2 = 2466 061 413 187 018.3 Hz, matching Eq. (1) to the stated
rounding.)

## The ac-Stark treatment specifically

The paper's own account of its ac-Stark systematic, p. 2 col. 2, verbatim, in
full: "The two dominating systematic effects are the ac Stark shift and the
residual second order Doppler effect. A small quadratic contribution to the ac
Stark shift is modelled and corrected with the help of a Monte Carlo
simulation, that takes into account the full excitation geometry and the
measured laser power. This leaves us with a purely linear ac Stark shift that
we extrapolate to zero laser power."

So the treatment splits the light shift into two pieces:

1. A **linear-in-power** term, handled the classical way: the fitted line
   center is extrapolated to zero probe-laser power, which removes it without
   needing a model of its size.
2. A **quadratic-in-power residual**, which is not removed by the
   extrapolation (a linear extrapolation cannot absorb a quadratic term) and
   is instead modelled and subtracted using a Monte Carlo simulation that
   "takes into account the full excitation geometry" (i.e., trajectory- and
   geometry-resolved, not a simple convolution) together with the measured
   laser power. This is Table I's "Quadratic ac Stark shift (243 nm)" row,
   −10.7(2.0) Hz.

Two further ac-Stark-labelled rows in Table I come from the auxiliary 486 nm
beam used (via the 2S-4P transition) to measure the 2S atoms' velocity
distribution for the second-order-Doppler correction (p. 2 col. 2: "The
remaining second order Doppler shift is corrected by using the measured
velocity distribution of the 2S atoms (via the 2S-4P transition) in
combination with Monte Carlo simulations that also takes into account a small
laser power dependence [7]"): "ac Stark shift, 486 nm quench beam", 0(2.0) Hz,
and "ac Stark shift, 486 nm scattered", 0(1.0) Hz. A fourth, much smaller row,
"rf discharge ac Stark shift", 0(0.03) Hz, budgets light from the rf discharge
source used to dissociate H2 into atomic hydrogen.

The paper does not state a single combined ac-Stark number. Quadrature-summing
the four ac-Stark-labelled rows (2.0, 2.0, 1.0, 0.03 Hz) gives 3.0 Hz, a
combination computed here and not printed in the source.

Note on scope: this record's own parthey2011 note (`private/cache/
lit_intake_2026-09-21/notes/parthey2011.md`) has read page 1 in full plus the
opening of the apparatus-description section, by its own account. Its
ac-Stark and second-order-Doppler systematic-correction sections (pp. 2-5) are
unread there, by that note's own verify_flags. So whether matveev2013's
linear/quadratic decomposition matches parthey2011's own wording cannot be
said. Only that "the data evaluation to find the line
centers follows that of Ref. [7]" (p. 2 col. 1) can be reported, i.e. the same
procedure family, without a verified textual comparison.

## The Lorentz-invariance (SME) result

Roughly the paper's second half (pp. 3-4) is a separate result, largely
tangential to this record: having four hydrogen 1S-2S measurement epochs at
different times of year (1999, 2003, '05/2010' = parthey2011, '11/2010' =
this paper), the authors constrain two linear combinations of Lorentz-boost
violation coefficients in the Standard Model Extension (Kostelecký et al.
framework, Eqs. 2-3, p. 3 col. 2 - p. 4 col. 1). From the 2010 measurements
alone, the paper states a constraint for the linear combination (p. 4 col. 1):
0.95c(TX) − 0.28c(TY) − 0.12c(TZ) = (2.1±1.8)×10⁻¹¹. From 1999 and 2003 (Eq.
unnumbered, p. 4 col. 1): 0.83c(TX)+0.51c(TY)+0.22c(TZ) = (4±8)×10⁻¹¹.
Combined (Eq. 4, p. 4): c(TX) = (3.1±1.9)×10⁻¹¹,
0.92c(TY)+0.40c(TZ) = (2.6±5.3)×10⁻¹¹, matching the abstract. The authors
also note (p. 3 col. 2 - p. 4 col. 1) that the 1999/2003 averaged value
differs from the 2010 averaged value by 2.4 standard deviations, attributed to
underestimated second-order-Doppler and ac-Stark systematics in the earlier
analyses using a different model, not to any change in apparatus.

## Fig. 3: the four-campaign record

Fig. 3 (p. 3) plots the hydrogen 1S-2S centroid frequency (relative to Fstat)
for four campaign clusters, with labelled weighted-mean points and their
χ²/dof:

- 07/1999: 109(44) Hz, χ²/dof = 5.9.
- 02/2003: 80(34) Hz, χ²/dof = 9.1.
- 05/2010 (parthey2011's own result, Ref. [7]): 35(10) Hz, χ²/dof = 1.9.
- 11/2010 (this paper's own new result): 18(11) Hz, χ²/dof = 2.4.

The caption cites [4,6,7] for the three earlier points. The 11/2010 point is original to
this Letter.

## Bibliographic cross-check against this record's own holdings

This paper's own reference list (p. 5) names, as Ref. [6], "M. Fischer et al.,
Phys. Rev. Lett. 92, 230802 (2004)" and, as Ref. [7], "C. G. Parthey et al.,
Phys. Rev. Lett. 107, 203001 (2011)". Both match fischer2004 and parthey2011
as already held and VERIFIED in this repository's docs/lit/, field for field.
Ref. [10] (the fibre-link characterisation) is K. Predehl et al., Science
336, 441 (2012), not currently held here.

## Use in this record

This is the next measurement, chronologically and by author list, in the
hydrogen 1S-2S / cryogenic-atomic-beam / trajectory-resolved-AC-Stark lineage
this shelf already carries: fischer2004 (2004, experimental sibling of the
unheld Haas et al. 2006 trajectory-resolved theory paper) → parthey2011 (2011,
local mobile cesium fountain, the '05/2010' campaign) → **matveev2013** (2013,
this paper, the same apparatus but a remote PTB cesium fountain reached via a
new 920 km fibre link, the '11/2010' campaign) → grinin2020 (the same group's
later 1S-3S measurement). What matveev2013 specifically adds to the shelf,
beyond confirming parthey2011's own number:

- A second, explicit statement (beyond parthey2011's own, unread here) of how
  this lineage's apparatus separates an ac-Stark systematic into a
  power-extrapolated linear part and a Monte-Carlo-modelled, excitation-
  geometry-resolved quadratic residual, a concrete worked example of
  trajectory/geometry-resolved treatment of a light shift, the same
  methodological family as this record's own non-convolving stance
  (`rb5s6s/ramp_transit.py`, `rb5s6s/lineshape.ramp_mixture`) instead of a
  simple convolution.
- A sharp contrast worth naming instead of a match: this lineage treats the
  ac-Stark shift purely as a systematic to be extrapolated or modelled away
  (Table I's ac-Stark rows all carry Δ=0 or a small correction, entering only
  the uncertainty budget). This record's own current direction is the
  opposite: per this repository's standing ruling that there is no light-
  shift ceiling and a shift comparable with the linewidth is signal, not a
  systematic to be extrapolated to zero, the AC-Stark ramp is fit jointly as
  one of the observables instead of removed by a zero-power extrapolation.
  matveev2013 is a precedent for the geometry-resolved modelling half of that
  stance, not for treating the shift as a measured quantity in its own right.
- A concrete instance of the discipline this record's own rules ask for
  elsewhere: a systematic re-examined and revised (the second-order-Doppler
  budget raised from 5.1 to 8.0 Hz) after a hardware flaw (insufficient
  Faraday-cage shielding) was found post hoc, with the revision stated
  plainly instead of absorbed silently.
- The apparatus-temperature figure this paper states for its own beam (6 K,
  p. 2) differs from the figures the other two lineage papers already held
  here state (parthey2011: 5.8 K, fischer2004: 5-6 K), flagged in
  `verify_flags` above, not resolved.

Numerically nothing transfers to this record's own model: this is atomic
hydrogen on a cryogenic beam at a wavelength (243 nm, the 4th harmonic of
972 nm) and apparatus entirely unlike this record's own heated Rb vapour
cell at 993 nm. What transfers is the methodological precedent, as for
fischer2004 and parthey2011 already on this shelf.
