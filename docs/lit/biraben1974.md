---
citekey: biraben1974
type: article
authors:
  - Biraben, F.
  - Cagnac, B.
  - Grynberg, G.
title: 'Experimental Evidence of Two-Photon Transition without Doppler Broadening'
journal: Phys. Rev. Lett.
volume: 32
pages: 643
year: 1974
doi: 10.1103/PhysRevLett.32.643
arxiv: null
pdf: PDF_papers/Biraben_1974_first-doppler-free-two-photon-Na.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: '2026-08-03'
summary: >
  The founding experimental demonstration of Doppler-free two-photon
  spectroscopy: the 3S-5S transition in sodium vapour, driven by a
  retro-reflected dye laser, shows two narrow hyperfine-resolved peaks that
  survive only when the atom is forced to take one photon from each of the
  two counter-propagating beams (opposite circular polarisations eliminate
  the residual Doppler pedestal entirely). Confirms the 1970/1973 theoretical
  prediction. Contains the Doppler-cancellation algebra our methods/01
  rederives, but no transit-time lineshape, no fitted width, and no moments
  -- that is biraben1979, five years later.
loci:
  - P1
  - methods/01
section: method-anchors
---

# biraben1974

**VERIFIED, 2026-08-03**, read in full from the four-page PRL (32, 643-645,
25 March 1974, received 28 January 1974). This is the founding paper of the
whole technique this repository's measurement rests on. It shares its PRL
pages with an independent companion demonstration, [M. D. Levenson and
N. Bloembergen, "Observation of Two-Photon Absorption without Doppler
Broadening on the 3S-5S Transition in Sodium Vapor," *ibid.* 645](https://doi.org/10.1103/PhysRevLett.32.645),
printed immediately after it in the same issue: two groups, same transition,
same conclusion, same week.

**Abstract, verbatim** (the italic paragraph under the byline: PRLs of this
era carry a short abstract rather than none).
<!-- not-from-pdf: this scan's OCR text layer garbles glyphs inside the
abstract itself ("3S-5S" reads as "3$-5S"; elsewhere "Universite" as
"Vnizersite", "Nationale" as "¹tionale"), so
test_lit_quotes_are_verbatim.py cannot match it against extracted text; the
quotation is transcribed by eye from the rendered page. -->
"Experiments on the 3S-5S
two-photon transition in sodium give evidence that Doppler broadening is
eliminated if the atom absorbs two photons propagating in opposite
directions. The proof is given by the comparison of the two-photon
absorption line shape in traveling and standing waves."

**What it did.** Drove the 3S to 5S two-photon transition in sodium vapour
(cell at about 220 C) with a flashlamp-pumped rhodamine-6G dye laser at
6022.3 A, multimode (three or four longitudinal modes, about 240 MHz apart,
calibrated by a Michelson interferometer), retro-reflected by a mirror to
form a standing wave. The 5S population was read out via fluorescence at
6154/6160 A (decay to 3P1/2, 3P3/2) on a photomultiplier, with the signal Q
integrated over a 300 ns pulse and plotted as Q/P^2 against laser frequency,
since the two-photon rate scales as the square of the laser power P. Three
configurations are compared directly (Fig. 2). First, one traveling wave
only, no mirror, giving a broad Doppler-spread pedestal, about 2000 MHz wide,
weak, plotted at 10x expansion. Second, a standing wave with linear
polarisation, giving two narrow hyperfine-resolved peaks (the two allowed
Delta-F=0 transitions, F=1 to F'=1 and F=2 to F'=2) sitting on top of a much
weaker residual Doppler pedestal, from atoms absorbing both photons out of
the same traveling wave. Third, a standing wave with the two
counter-propagating waves given opposite circular polarisations
(sigma+ / sigma-) via quarter-wave plates, which makes the Delta-mF=0
selection rule forbid absorbing two photons from the same wave, so every
absorbing atom is forced to take one photon from each direction, and the
Doppler pedestal vanishes completely, leaving signal only at the two narrow
peaks. Removing the mirror in this third configuration kills the signal
outright, confirming the mechanism. This progression from the first
configuration to the third is the paper's proof: the narrow Doppler-free
feature is not an artifact of the standing wave generally, but specifically
of forcing one photon from each direction.

**Key numbers.** Sodium 3S ground-state hyperfine splitting, 1771 MHz
(known). 5S hyperfine splitting, not previously measured, estimated at about
155 MHz from the Fermi-Segre formula, giving a predicted 1616 MHz separation
between the F=1 to F'=1 and F=2 to F'=2 two-photon lines and hence an
expected ~800 MHz separation between the two observed peaks (the two-photon
frequency axis is half the transition energy). No quantitative linewidth or
fitted hyperfine value is reported: the paper states explicitly that "the
present uncertainty in the laser frequency prevents us from giving any
significance to the experimental widths of the peaks, or assigning a precise
value to the hyperfine structure of the 5S level." This is a proof-of-concept
demonstration, not a precision measurement. The closing paragraph says as
much, that laser bandwidth keeps the result short of "the ultimate precision
inherent in this method."

**Theoretical lineage, for provenance.** The paper opens by citing the
prediction it confirms: "Doppler-broadening elimination in multiphoton
transitions has been theoretically studied in a recent paper," giving Cagnac,
Grynberg and Biraben, J. Phys. (Paris) 34, 845 (1973), and behind that,
Vasilenko, Chebotaev and Shishaev, Pis'ma Zh. Eksp. Teor. Fiz. 12, 161 (1970)
[JETP Lett. 12, 113 (1970)]. This note is the first experimental test of that
prediction, not its origin.

## Bridges to this repository

Our [methods/01](../methods/01_the_measurement.md) drives the Rb
5S1/2 to 6S1/2 two-photon transition Doppler-free by retro-reflecting a
993 nm beam onto itself, and section 1.1 rederives the cancellation
condition from scratch: an atom absorbing one photon from each
counter-propagating direction sees

nu(1 + v/c) + nu(1 - v/c) = 2 nu,

with the velocity term cancelling exactly to first order for every atom.
That is, algebraically, this paper's Eq. (1),

h-omega_e - h-omega_g = h-omega(1 - v_x/c) + h-omega(1 + v_x/c) = 2 h-omega,

restated for our own beam geometry rather than cited. Nothing else in this
repository's docs currently cites this paper by name. The founding-history
role is instead carried by [biraben2019](biraben2019.md), Biraben's own 2019
retrospective review, a secondary source written 45 years after the fact.
`docs/BIG_PICTURE.md` and `docs/THEORY_NOTE.md` both label the transit
lineshape "textbook (Biraben-Cagnac)" and link that phrase to
[biraben1979](biraben1979.md), a *different*, later paper by an overlapping
author list. Nothing in this repository's method docs has, until now,
distinguished "the 1974 paper that first demonstrated the technique" from
"the 1979 paper that derived our transit kernel" from "the 2019 review that
narrates both." This note is that distinction, held against the primary
1974 text rather than inferred from the review.

What this paper establishes, precisely: the Doppler-cancellation argument
itself (the same two-line algebra our methods/01 uses), and the experimental
proof that forcing one photon from each counter-propagating direction -- not
merely illuminating with a standing wave -- is what kills the Doppler
pedestal. That second point, the polarisation-selection control experiment
in Fig. 2(c), is stronger than anything our own methods chapter argues from
first principles alone: it is a direct experimental exclusion of the
"standing wave alone is enough" alternative.

What it does **not** contain, so nothing here should be attributed to it
beyond the above: no transit-time lineshape, no cusp, no Lorentzian-convolved-
with-exponential kernel, no analytic lineshape of any kind -- the words
"transit" and "cusp" do not appear, and the only lineshape objects are a
hand-drawn Doppler envelope for the broadened trace and two data peaks with
no fitted width. No moments, no cumulants, no AC-Stark or standing-wave
intensity-weighting discussion of the kind in
[wieman1987](wieman1987.md). No second-order Doppler estimate. No rubidium
-- this is sodium, the 3S-5S line at 6022.3 A, not 5S-6S. Every one of those
belongs to a later paper (biraben1979 for the transit kernel, biraben2019
for the retrospective synthesis) and should keep citing that paper, not this
one.
