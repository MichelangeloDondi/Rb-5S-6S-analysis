---
citekey: fendel2007
type: article
authors:
  - Fendel, P.
  - Bergeson, S. D.
  - Udem, Th.
  - Hänsch, T. W.
title: 'Two-photon frequency comb spectroscopy of the 6s-8s transition in cesium'
journal: Opt. Lett.
volume: 32
number: 6
pages: 701
year: 2007
doi: null
arxiv: null
pdf: PDF_papers/Fendel_2007_Cs-6s-8s-two-photon-comb-average-not-peak-AC-Stark.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-07-29
summary: >
  Cs 6s-8s single-colour two-photon in a hot vapour cell -- the same experiment
  as this programme, one element to the left, driven by a frequency COMB. The
  AC-Stark shift follows the AVERAGE rather than the much larger PEAK intensity
  (-0.21 Hz/(mW/cm^2) against average single-beam intensity) -- and that
  peak-vs-average is the comb's TEMPORAL pulse train, ns spacing against a
  ~50 ns atomic response: the fast-modulation limit of Camparo 1992, realised.
  The SPATIAL distribution was engineered away with an unfocused 0.72 mm waist.
loci: []
section: prior-art
---

# fendel2007

**The closest experimental analogue found anywhere, and the paper a referee is
most likely to cite back.** Single-colour two-photon nS->n'S in a hot alkali
vapour cell with fluorescence detection: this programme's experiment, in
caesium.

**Why it is a threat.** The framing used here is that the field collapses the
light-shift distribution to a mean without justification. Fendel *et al.* did
not merely collapse it -- they **tested peak against average and published the
result**, measuring -0.21 Hz/(mW/cm^2) against average single-beam intensity,
cross-checked against independent cw measurements and theory, and concluding
that "the average, rather than the peak power must be used for its evaluation".
That is prior art on the specific peak-versus-average question, and a much
stronger position than "nobody considered it".

**The counter, which must be made explicitly rather than left implicit.** They
used an **unfocused** beam -- Gaussian waist **0.72 mm** -- chosen precisely to
minimise the effect. Their finding is therefore *in a near-collimated beam,
where the intensity distribution is narrow, the average suffices*. It says
nothing about a tight focus, where the distribution is wide and the I^2
weighting is severe. Read that way the paper is **evidence for this
programme's premise**: a first-rate group met the focused-beam distribution
problem and engineered around it rather than modelling it, which is the gap
claimed here.

**A coincidence worth checking before it is noticed for us.** Fendel quote a
2.9 kHz shift for **225 mW** incident on the cell -- the same power figure as
this archive's S_0(225 mW) < 0.64 MHz bound. Whether that is coincidence or a
convention inherited from this literature, it makes the two numbers directly
comparable and a reviewer will see it.

**ACTION: cite in the framing paragraph and draw the focused/unfocused
distinction in one sentence.** Per the audit this is the single largest
remaining referee risk in the light-shift argument. Obtain the PDF: the waist,
the intensity definition (single-beam vs total) and the 225 mW figure all need
reading first-hand before the comparison is put in print.

**Read in full 2026-07-29** from the PDF supplied by the experimenter; the
key numbers verify verbatim (-0.21 Hz/(mW/cm^2) against average single-beam
intensity; unfocused 0.72 mm 1/e^2 waist; 2.9 kHz shift at 225 mW incident).

**The full text sharpens what "average not peak" means, and the distinction
matters for how it is cited.** Their peak-vs-average is the frequency comb's
TEMPORAL structure -- pulsed excitation against cw -- not the spatial profile:
the pulse spacing is nanoseconds against a ~50 ns atomic response, so the atom
integrates the pulse train and shifts with the average intensity. That is the
fast-modulation limit of [Camparo 1992](camparo1992.md), realised in exactly
this class of experiment (and the same physics M19 checks for atoms crossing a
standing wave: modulation fast compared with the response leaves the mean).

The SPATIAL question -- the distribution of shifts across a focused profile,
which is this programme's subject -- they did not test but engineered away:
the 0.72 mm waist keeps the intensity distribution narrow enough that its
spread never matters. So the paper settles the temporal question, supports
the fast-limit physics, and leaves the focused-beam spatial distribution
exactly as open as the programme claims.
