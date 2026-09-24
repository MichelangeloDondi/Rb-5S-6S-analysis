---
citekey: grinin2020
type: article
authors:
  - Grinin, Alexey
  - Matveev, Arthur
  - Yost, Dylan C.
  - Maisenbacher, Lothar
  - Wirthl, Vitaly
  - Pohl, Randolf
  - Hänsch, Theodor W.
  - Udem, Thomas
title: 'Two-photon frequency comb spectroscopy of atomic hydrogen'
journal: Science
volume: 370
number: 6520
pages: 1061-1066
year: 2020
doi: 10.1126/science.abc7776
arxiv: null
pdf: PDF_papers/Grinin_2020_hydrogen-1S-3S-two-photon-comb-spectroscopy-Rydberg-constant.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/grinin2020.md  # line-by-line against the held PDF, 2026-09-22: restored one sentence dropped from the boxed-abstract quotation ("The proton radius puzzle is..."), two provenance/framing candidates considered and refuted. Extended 2026-09-22 to pp. 2-7 (the per-scan Lorentzian fits, the Eq. 3 linear regression, and Table 1), see private/cache/lit_intake_2026-09-22_audits/grinin2020_extension.md
author: agent
routing: []
verify_flags:
  - 'Page 1 of the held PDF (title, full author byline, the boxed lede
    paragraph that serves as the abstract, and the start of the main text
    through the introduction of the QED energy-level expression) read against
    the record on 2026-09-21, downloaded from the co-author''s own
    (agpohl.physik.uni-mainz.de) hosted copy since no arXiv posting exists.'
  - 'Pages 2-7 read in full on 2026-09-22 (pdftotext -layout extraction of the
    two-column layout), with pages 2, 3, 4 and 5 each additionally checked
    against the 150 dpi rendered page image, since a two-column research
    article with floating figures is exactly where a text layer can
    misattribute a paragraph to the wrong page. Page 2 carries the general
    Lorentzian-line-shape-model validation sentence. Page 3 carries the
    per-scan Lorentzian fit (i = 1...4450 line scans, three detectors) and
    Fig. 4''s own inset Lorentzian fit. Both are on p. 3, not p. 2 as the
    intake brief for this pass assumed. Page 4 carries Eq. 2 (the chirp
    model), the saturation/ionization sentence, and Eq. 3 itself. Page 5
    carries the rest of the Eq. 3 fit discussion, Eq. 4-7 (the two transition
    frequencies, the Rydberg constant and the proton radius) and Table 1.
    Pages 6-7 are the numbered reference list, acknowledgments, and (p. 7) the
    journal''s auto-appended article-summary/tools page, which restates the
    abstract and adds no new physics content.'
verified_date: 2026-09-22
summary: >
  Direct frequency-comb two-photon UV spectroscopy of hydrogen 1S-3S,
  f_1S-3S = 2,922,743,278,665.79(72) kHz, combined with the 1S-2S frequency to
  give the Rydberg constant and a proton charge radius favouring the muonic
  value. Same MPQ/LMU lineage as fischer2004 and parthey2011 (Matveev and
  Hänsch/Udem are common authors), the most recent openly held instance of
  the group's trajectory-based two-photon line-shape programme. Its own
  reduction is the field's canonical two-step practice, not the
  trajectory-resolved-Monte-Carlo lineage: fit a Lorentzian per scan
  (i = 1...4450 scans) for each of three detectors, then a linear regression
  (Eq. 3) against auxiliary variables (temperature, cavity power, line
  amplitude) removes the chirp-induced residual first-order Doppler shift
  (`CIFODS`), the second-order Doppler shift (-3.20(26) kHz) and the ac Stark
  shift (+4.60(30) kHz) (Table 1). Saturation and ionization were negligible
  (<1 Hz) at the powers used.
loci: []
section: transit-time
---

# grinin2020

VERIFIED for the full article. Page 1 (title, authors, the boxed
abstract-equivalent paragraph, and the opening of the main text) was read on
2026-09-21. Pages 2-7, including the per-scan Lorentzian fits, the Eq. 3
linear regression and its systematic terms, and Table 1's error budget, were
read on 2026-09-22 (see the What-pages-2-7-add section below). No PDF-embedded `Title`
metadata field is set (pdfinfo returns only "Science Journals — AAAS"). The
title above is read directly off the page.

## What page 1 gives, verbatim

The boxed lede paragraph, which functions as this Science-format paper's
abstract: "We have performed two-photon ultraviolet direct frequency comb
spectroscopy on the 1S-3S transition in atomic hydrogen to illuminate the
so-called proton radius puzzle and to demonstrate the potential of this
method. The proton radius puzzle is a significant discrepancy between data
obtained with muonic hydrogen and regular atomic hydrogen that could not be
explained within the framework of quantum electrodynamics. By combining our
result [f1S-3S = 2,922,743,278,665.79(72) kilohertz] with a previous
measurement of the 1S-2S transition frequency, we obtained new values for the
Rydberg constant [R∞ = 10,973,731.568226(38) per meter] and the proton charge
radius [rp = 0.8482(38) femtometers]. This result favors the muonic value
over the world-average data as presented by the most recent published CODATA
2014 adjustment."

## What pages 2-7 add, verbatim and from Table 1

The Lorentzian line-shape model is validated on p. 2, verbatim: "In addition,
we used the simple Lorentzian line shape model and found the line center
within 10^-3 of the line width, which is a rather moderate value." This is a
general statement about the adequacy of a Lorentzian fit, not itself the
per-scan procedure.
<!-- rendered-page: p. 2 -->

The per-scan fit is on p. 3, not p. 2, verbatim: "Our dataset consists of
i = 1...4450 line scans like the one shown in the inset of Fig. 4, each of
≈36 sec duration. A large fraction of the data (2020 line scans) have been
recorded with a nozzle temperature of 7 K. As a first step of the evaluation,
we fit Lorentzians to the normalized signal to find the line widths,
amplitudes, constant offsets, and the center frequencies fj,i for the three
detectors (j = 1...3). The statistical uncertainties of the center
frequencies σj,i(f) are dominated by shot noise." Fig. 4's own caption (also
p. 3) independently confirms the same practice for a five-scan average:
"The inset shows an average of five line scans (3 min) within ±4 MHz of the
main component, normalized to the Doppler-broadened signal, together with a
Lorentzian fit."
<!-- rendered-page: p. 3 -->

Page 4 states saturation and ionization were negligible, verbatim: "Nonlinear
effects due to saturation and ionization were negligible (<1 Hz) at the power
levels used. Under average experimental conditions, the AC-Stark effect
shifts the resonance by 4.6 kHz." Eq. 3, the linear regression that removes
the systematics from the per-scan center frequencies of the main detector, is
printed on p. 4 as (transcribed from the rendered page image, not asserted as
a character-verbatim string since the two-column layout splits an inline
equation's glyphs out of reading order in text extraction):
`f1,i = f0 + kappa_DS(f2,i - f3,i) + kappa_SOD Ti + kappa_AC Pi + kappa_PS Ai`,
with its four coefficients and f0 all adjusted in one weighted fit to the measured
frequencies fj,i against the auxiliary variables Ti (nozzle temperature), Pi
(scan-averaged cavity power) and Ai (normalized line amplitude, used as a
density proxy for the pressure shift).

Table 1 (p. 5), the error budget of the 1S(F=1)-3S(F=1) measurement, all
values in kHz:

| contribution | average effect | correction | uncertainty |
|---|---|---|---|
| statistics | -- | -- | 0.11 |
| `CIFODS` | +0.79 | -- | 0.08 |
| `SOD` (second-order Doppler) | -3.20 | -- | 0.26 |
| AC-Stark | +4.60 | -- | 0.30 |
| pressure shift | +0.93 | -- | 0.30 |
| residual Doppler | -- | -- | 0.48 |
| DC-Stark | +0.031 | -0.031 | 0.015 |
| Zeeman shift | -0.002 | +0.002 | 0.002 |
| line pulling | -0.30 | +0.30 | 0.050 |
| multiparameter `CIFODS` | -- | -- | 0.10 |
| maser | -0.30 | +0.30 | 0.030 |
| total | -- | +0.57 | 0.72 |

The AC-Stark and second-order-Doppler rows are the two Table 1 asked to
extract: AC-Stark +4.60(30) kHz is Eq. 3's kappa_AC coefficient times the
average power, matching p. 4's own 4.6 kHz figure quoted above. The
second-order Doppler row, -3.20(26) kHz, is the weighted mean of the `SOD`
coefficient's own term across all evaluated data, distinct from (but
consistent with) p. 4's
separately stated "-2.9 kHz at a nozzle temperature of T = 7 K", which is
that shift computed for one specific temperature and not the Table 1
weighted average.
<!-- rendered-page: p. 4 -->

## Use in this record

Not named directly in the search priority list, but found while chasing its
named papers (Haas 2006, Parthey 2011): this is the same MPQ/LMU group's most
recent openly obtainable member of the trajectory-resolved two-photon
line-shape lineage, and the strongest still-active instance of the precedent
this record leans on for its own non-convolving model
(`rb5s6s/ramp_transit.py`, `rb5s6s/lineshape.py`). Held via the co-author's
own group page (agpohl.physik.uni-mainz.de) since Science does not post to
arXiv and no author preprint appears there either. Sits beside fischer2004
and parthey2011 (parthey2011) as the third openly-held member of a lineage
whose middle members, Haas 2006 (haas2006) and Matveev 2013 (matveev2013),
are now both held and read in full as of 2026-09-22. The paywalled-with-no-
OA-copy-found state carried here for them until 2026-09-21 is retracted as
of 2026-09-22. See the intake report.

For canonical practice beside hilico1998 and matveev2013, not the lineage
paragraph: the per-scan Lorentzian fit and the linear regression of Eq. 3
against auxiliary variables (temperature, power, amplitude) is the two-step
reduction pattern used broadly for Doppler-free two-photon systematic
budgets, the same genre as hilico1998's own error-budget table (light shift,
collisions, second-order Doppler, blackbody radiation, its Table 2, per that
note's own summary) and matveev2013, a systematic-budget paper for the same
1S-2S line, held and read in full as of 2026-09-22 but not re-read here for
its own methodology. What is specific to this record's own methodological
stance is not this two-step practice itself, which fits a single number (the
center frequency) per scan and regresses systematics afterward, but the earlier
trajectory-resolved lineage (kolachevsky2006, haas2006) that carries the
ac-Stark shift and the atomic trajectory through the same dynamics before any
fit is done. Grinin 2020's own per-scan Lorentzian fit is closer in kind to
the canonical practice than to that lineage: nothing on pp. 2-7 couples the
line-shape fit itself to a trajectory model, and the systematics (`CIFODS`,
the second-order Doppler shift, AC-Stark, pressure, DC-Stark, Zeeman, line
pulling, maser) are all removed afterward by the auxiliary-variable
regression of Eq. 3, not folded into the per-scan Lorentzian.
