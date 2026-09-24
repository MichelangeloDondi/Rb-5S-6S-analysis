---
citekey: debeauvoir1998
type: article
authors:
  - de Beauvoir, B.
  - Nez, F.
  - Hilico, L.
  - Julien, L.
  - Biraben, F.
  - Cagnac, B.
  - Zondy, J.-J.
  - Touahri, D.
  - Acef, O.
  - Clairon, A.
title: 'Transmission of an optical frequency through a 3 km long optical fiber'
journal: Eur. Phys. J. D
volume: 1
pages: 227--229
year: 1998
doi: 10.1007/s100530050085
arxiv: null
pdf: PDF_papers/DeBeauvoir_1998_optical-frequency-transmission-3km-fiber.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/debeauvoir1998.md  # full 3-page read checked against the PDF, 2026-09-22
author: agent
routing: []
verify_flags:
  - 'TANGENTIAL: flagged by the calling session before this note was drafted, and confirmed by
    reading the full paper. This is an engineering note about a fibre link''s own noise and
    frequency-transfer accuracy, not a result this record cites or builds on; routing is left
    empty rather than CITE/FEED because nothing here currently feeds or is expected to feed this
    record''s model, code or claims. Held and read in full (3 pages, 227-229). DOI confirmed via
    CrossRef (api.crossref.org/works/10.1007/s100530050085): title, all ten authors, journal,
    volume 1 and pages 227-229 match the held PDF exactly. A first automated web search summary
    guessed a DIFFERENT, wrong DOI (10.1007/s100530070043, actually a later, unrelated hydrogen
    1S-3S paper by an overlapping author list) for this same title; that guess is not used
    anywhere and is recorded here only as a caution against trusting an unverified search
    summary over a direct CrossRef lookup.'
verified_date: 2026-09-22
summary: >
  Characterizes a 3 km (6 km round-trip) optical fibre link between two Paris frequency-metrology
  laboratories, using the same 778 nm Rb two-photon standard as hilico1998 (five of that paper's
  six authors are repeated here) as the transferred reference. The fibre adds no measurable
  linewidth beyond the laser's own self-heterodyne beat (~4 kHz, limited by the laser, not the
  fibre); the fibre's own frequency shift, from 1000 one-second measurements, has mean 0.4 Hz and
  about 10 Hz of noise, i.e. transfer accuracy better than 1 part in 10^14, with day-to-day drift
  staying within about +-1 Hz over ten days.
loci: []
section: method-anchors
---

# debeauvoir1998

VERIFIED. Held and read in full, all 3 pages (227-229). Tangential to this record's own physics.
See the routing note above.

## What it does

B. de Beauvoir, F. Nez, L. Hilico, L. Julien, F. Biraben, B. Cagnac, J.-J. Zondy, D. Touahri,
O. Acef and A. Clairon (Laboratoire Kastler Brossel and BNM-LPTF, Paris), "Transmission of an
optical frequency through a 3 km long optical fiber," Eur. Phys. J. D **1**, 227-229 (1998):

> "A 3 km long optical fiber is used to connect two laboratories in Paris. We present the
> metrological properties of this optical link to transfer an optical frequency standard at
> 778 nm and we show that the frequency shift introduced by the fiber is only of few Hz." (p. 227,
> Abstract)

Two multimode-at-778nm fibres (3 km each) connect the LPTF and Kastler Brossel laboratories,
carrying the 778 nm two-photon Rb standard (the same instrument family as hilico1998, held
elsewhere in this record) round-trip. A beat note is formed between the light returned through the
fibre (frequency-shifted by an AOM) and the un-transmitted reference, read on either a spectrum
analyser or a frequency counter (Fig. 1, p. 228).

## Frequency broadening (Sect. 3)

Using a self-heterodyne argument (delay tau(k) ~ 37.4 us for the 6 km round trip, dispersion
~20 ns pulse broadening over the fibre, and the laser's own coherence time ~500 us via a
titanium-sapphire laser with 2 kHz jitter versus ~100 kHz for the grating diode laser), the paper
measures a self-heterodyne beat linewidth of about 4 kHz (Fig. 3, resolution bandwidth 3 kHz),
noting this "gives an upper limit of a possible frequency broadening due to the optical fiber" (p.
228): i.e. the observed linewidth is consistent with being set by the laser's own coherence, not
by fibre-added noise.

## Frequency shift (Sect. 4, Figs. 4-6)

A histogram of 1000 one-second measurements of the fibre-induced frequency shift under
undisturbed conditions (Fig. 5) gives a mean of 0.4 Hz with about 10 Hz of scatter. Over several
days (Fig. 6), the shift's day-to-day variation stays within roughly +-1 Hz, attributed to a
temperature-driven drift of the fibre's refractive index and delay: "a temperature variation of
0.03 K/hour induces a frequency shift of 1 Hz" (p. 229).

## Conclusion (p. 229), quoted

> "We have shown that it is possible to transfer, without any precaution, an optical frequency
> with an accuracy of" (the printed page places Fig. 6 and its caption in the middle of this
> sentence, a layout artefact, and the sentence continues past it) "few Hz, that is to say a relative
> accuracy better than 1 part in 10^14."

## Use in this record

Tangential. This paper documents a fibre-transfer engineering result for a different transition
(778 nm, 5S-5D) and a different apparatus purpose (distributing a frequency standard between two
buildings) than anything this record's own campaign does. It shares authors and instrumentation
with hilico1998 (the two-photon Rb 778 nm standard held elsewhere in this record) and is read here
only as background confirming that laboratory's broader metrology programme, not as a source of
any number, method, or claim this record uses. No further use is asserted.

## Limits

Nothing here should be read as this record citing or depending on the paper's results.
`routing: []` and `loci: []` above record that explicitly, and no claim surface in this record
should point to this citekey without first re-examining why.
