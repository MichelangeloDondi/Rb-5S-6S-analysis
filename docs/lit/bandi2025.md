---
citekey: bandi2025
type: article
authors:
  - Obaze-Adeleke, A. C.
  - Semon, B.
  - Bandi, T. N.
title: 'A comprehensive review of rubidium two-photon vapor cell optical clock: long-term performance limitations and potential improvements'
journal: Photonics
volume: 12
number: 5
pages: 513
year: 2025
doi: 10.3390/photonics12050513
arxiv: null
pdf: PDF_papers/Bandi_2025_Rb-two-photon-vapor-cell-clock-review.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'CITEKEY NAMES THE CORRESPONDING AUTHOR, NOT THE FIRST (noted
    2026-07-30). The record here is correct and checked against the held
    PDF: the paper is Obaze-Adeleke, Semon and Bandi, and T. N. Bandi is
    the corresponding author, not the first. The key follows how the
    review is known rather than this repository''s usual first-author
    convention. Consequence to watch: docs cite it in prose as "Bandi
    2025", and expanding that to "Bandi et al. (2025)" in a manuscript
    would be WRONG -- it is "Obaze-Adeleke et al. (2025)". Do not rename
    the key (it is used in three documents); render the citation from the
    authors field, not from the key.'
  - 'Quotes Hamilton''s 5S-5D magic wavelength as 778.179(5) nm; Hamilton 2023
    itself says 776.179(5) nm in its abstract and conclusions. Transposition in
    the review -- cite Hamilton directly, not this.'
verified_date: 2026-07-26
summary: >
  Field/systematics review for the Rb two-photon clock. Names the AC Stark
  shift, the temperature-induced shift and laser drift together as the
  medium-to-long-term limiters; targets better than 1e-15 at a day.
loci:
  - P1
section: landscape-24-26
---

# bandi2025

MDPI open access. The single best
landscape/systematics-benchmark review for the Rb two-photon clock.

**Full text read** (44 pp).

**What it actually ranks.** The abstract lists three limiters without ordering
them, but the body does order them:

> "light shift variations (stemming from fluctuations in the laser optical power
> that probe the rubidium transition) [117,120,136,157] and vapor-cell
> temperature variations [136] **predominantly limit performance for medium- to
> long-term averaging**."

So the pair -- light shift AND cell temperature -- is named as predominant
together, above laser drift and the rest. Both halves matter here: the light
shift is what the ramp method reads, and the cell-temperature term is the
density-coefficient territory this archive bounds.

**Numbers worth having.** The 5S-5D two-photon working linewidth is quoted as
**~330 kHz**, against the 3.49 MHz natural width of 5S-6S -- the 778 nm line is
roughly an order of magnitude narrower, which is the quantitative form of why
993 nm is not a better clock line. Field target: better than 1e-15 at one day.
Reported temperature coefficient -1.09(4)e-12 per K; He collisional shift
0.55e-8.

**A transcription error to route around.** The review reports Hamilton's 5S-5D
magic wavelength as "an experimental magic wavelength of 778.179(5) nm and a
theoretical magic wavelength of 776.21 nm". Hamilton 2023 (held here) says
**776.179(5) nm** experimental and 776.21 nm theoretical, repeatedly, in both
abstract and conclusions -- the review has transposed a digit. `constants.py`
carries 776.179, which is correct. Hamilton also reports a SECOND magic
wavelength at 790.26 nm, close to the 5S tune-out.

**Coverage gap, confirmed by search.** 5S-6S / 993 nm appears nowhere in the
body -- the only hits are reference titles (Nez 1993, a 5S-5D3/2 paper). The
review is a 5S-5D landscape; it does not touch this line.

**Citation scope.** <!-- not-from-pdf: the two strings below are OUR claim
wordings under discussion, not passages quoted from the paper. -->
The claim "the review identifies light shift and cell temperature as
predominantly limiting medium-to-long-term performance" is **supported**, though
it is a paraphrase and not a quotation; the paper's own sentence is "light shift
variations (stemming from fluctuations in the laser optical power that probe the
rubidium transition) and vapor-cell temperature variations predominantly limit
performance for medium- to long-term averaging". *The word "verbatim" was
attached to our paraphrase here until 2026-07-30, when a mechanical check
against the PDF caught it.* The stronger claim "the review identifies the light
shift as THE limiting systematic" is **not** supported -- it was written and
withdrawn on 2026-07-26, before the full text was available.

**A line worth carrying into this analysis, found while checking the above.** The
review states: "The natural linewidth of the two-photon transition in Rb is
[approximately] 330 kHz; however, as shown in Table 1, the measured linewidths
consistently exceed this intrinsic value." That is a *third* setting -- Rb
two-photon vapour-cell clocks, alongside the nanofibre cases in
[patterson2018](patterson2018.md) -- where measured linewidths sit above the
intrinsic value across a whole table of published work. Whether the causes are
shared is OPEN and almost certainly not; the point is that "the measured line is
wider than it should be, consistently, and the field notes it" is a broader
premise than this programme had realised.

## Their Table 1 is an external test set for M9 — and it does not come out clean

Their Table 1 tabulates, for ten Rb two-photon vapour-cell standards, the signal
linewidth **together with the cell temperature and the 1/e² beam waist**. Those
are precisely the three quantities `rb5s6s.constants.transit_fwhm_from_w0` maps
between, so it is a chance to test M9's transit model against somebody else's
apparatus. Against a natural linewidth of ≈330 kHz (their figure, for 5S→5D),
taking the tabulated waist as a *radius* (CALCULATED here):

| work | observed | excess over natural | transit predicted |
|---|---|---|---|
| Poulin 2002 | 410 kHz | 80 | 138 |
| Callejo 2024 | 450 | 120 | **597** |
| Lemke 2022 | 550 | 220 | 28 |
| Li 2024 | 618 | 288 | 74 |
| Erickson 2024 | 774 | 444 | 256 |
| Gerginov 2018 | 795 | 465 | 145 |
| Maurice 2020 | 2200 | 1870 | 574 |

**This is recorded as a DIAGNOSTIC, not as a validation and not as a
refutation.** Two things stop it being either.

First, transit is only one term. Bandi attribute the broadening to "transit-time
broadening due to the finite interaction period of atoms with the laser and
self-collisional broadening, as well as the laser's linewidth", so the
prediction should sit *below* the excess — which it does in five of seven rows,
by factors of 2 to 8. That is the expected direction but says nothing sharp,
because the missing factor is unconstrained.

Second — **and this was run down to its source on 2026-07-30, with a result that
indicts the review rather than the formula.** Callejo's row looked impossible: a
100 µm waist at 110 °C gives 597 kHz of transit on its own, against a *total*
tabulated linewidth of 450 kHz. Reading the primary
([callejo2025](callejo2025.md), held) resolves it. Their waist is genuine —
"the waist of the laser beam (w0 ∼ 100 µm)", focused into a 2 mm × 1.5 mm MEMS
cavity — but **their measured linewidth is "in the 1.5 - 2.1 MHz range", not
450 kHz**, and the "25 mm diameter, 70 mm length" cell in this table row is
their *reference glass-blown* cell, used for comparison, not the microcell.
The row conflates two cells and reports a width matching neither.

With the primary numbers the row is **consistent**: 597 kHz of transit against
1170–1770 kHz of excess over the 330 kHz natural width, i.e. transit supplying
34–51% and the rest going to collisions in a microcell plus laser width.
`lemke2022` likewise checks out once read at source: w₀ = 2.1(3) mm, stated as
an **intensity radius (1/e²)**, giving 28 kHz of transit against 220 kHz of
excess — 13%, as a beam that large should.

**But the waist column is NOT uniform, and a third primary shows it.** A claim
first written here — that the column is a radius throughout — was wrong, and
Erickson's thesis (held, `theses/`) says so explicitly: his transit contribution
is "310 kHz for 230 µm beam **diameter** at 100 °C". Lemke states a radius,
Erickson states a diameter, both unambiguously, in the same tabulated column.
**Every row must be taken to its own primary; the column cannot be read as one
convention.**

**And a second, deeper mismatch that the same line exposes.** At Erickson's
physical geometry — 230 µm diameter, so $w_0 = 115$ µm — this repository's
`transit_fwhm_from_w0` gives **513 kHz** against his stated **310 kHz**, a factor
of 1.65. That is not a waist-convention error; it is a difference in what
"transit-time broadening" *means*, and the candidates are well known (a 1/e²
crossing time, a FWHM, the Biraben–Cagnac two-sided-exponential width, a Gaussian
approximation to it). **Until that is pinned down, no cross-paper transit
comparison from this table is quotable**, including the two rows above, whose
apparent agreement may be a coincidence of matched conventions.

Erickson is the most useful row regardless, because he publishes a **complete
budget** rather than a total: 762 kHz observed (cw), from natural 330 kHz,
transit 310 kHz, helium collisional 200 kHz at 4 mTorr, Rb collisional 16 kHz,
Zeeman negligible. That is the only row that can be checked term by term.

**The lesson is about the review, not the physics.** Three primaries read, one
review row simply wrong, and a column that mixes conventions. Any further use of
this table should go to the primaries — seven of which are **already held here**:
[gerginov2018](gerginov2018.md), [callejo2025](callejo2025.md),
[beard2024](beard2024.md), [poulin2002](poulin2002.md),
[martin2018](martin2018.md), [erickson2024](erickson2024.md) (thesis) and
[lemke2022](lemke2022.md) (note pending).

**What would make this worth doing properly**, and it is cheap: take the three or
four rows whose primary sources are held or obtainable, read the waist
definition out of each paper rather than the review, and redo the comparison. A
transit model that reproduces published linewidths across four independent
apparatus would be a far stronger statement about M9 than any internal
consistency check — and the same exercise would put a real prior on $w_0$, which
is the open systematic every absolute result in this repository is bound on.
**Not attempted here. Recorded as OPEN.**

