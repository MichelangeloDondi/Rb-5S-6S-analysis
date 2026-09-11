---
citekey: yudin2025
type: misc
authors:
  - Yudin, V. I.
  - Prudnikov, O. N.
  - Taichenachev, A. V.
  - Basalaev, M. Yu.
  - Kapusta, D. N.
  - Goncharov, A. N.
  - Radchenko, M. D.
  - "Pal'chikov, V. G."
  - Zhou, L.
  - Zhan, M. S.
title: 'Lineshape-asymmetry-caused shift in atomic interferometers'
journal: arXiv preprint
volume: null
pages: null
year: 2025
doi: null
arxiv: 2512.18476
pdf: PDF_papers/Yudin_2025_lineshape-asymmetry-caused-shift-atom-interferometers.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  A live competitor for the interferometry framing this record sketched, from
  Novosibirsk with Wuhan. A lineshape asymmetry shifts an atom
  interferometer's answer, and the mechanism is chirp DURING the Ramsey pulses
  rather than an intensity distribution across the beam. Its scaling is the
  finding: 1 over T cubed against interferometry's usual 1 over T squared, so
  it grows for short-baseline devices, reaching 0.1 to 1 Gal at T near 100
  microseconds for rubidium two-photon gravimeters.
loci: []
section: prior-art
---
# yudin2025

Held. Verified against the PDF, five pages, on 2026-09-10.

## What it claims and how far it reaches

The paper opens by saying the shift it treats "has not previously been
discussed in the scientific literature". The asymmetry arises because the laser
field is frequency-chirped not only during the free-evolution intervals but
also during the Ramsey pulses, so the effective detuning during a pulse depends
on the chirp rate.

The scaling is what makes it matter. The shift goes as `1/T^3` in the interval
between Ramsey pulses, against the `1/T^2` that is usual in atom
interferometry, so it grows relative to everything else as the baseline
shortens. For rubidium two-photon interferometer gravimeters they estimate
0.1 to 1 mGal at `T` near 1 ms, and 0.1 to 1 Gal at `T` near 100 microseconds.

## Where it sits against this record

**The mechanism is not ours and the territory is.** This record's asymmetry
comes from atoms sampling an intensity DISTRIBUTION across a Gaussian beam,
with the kernel following the shift. Yudin's comes from the chirp during the
pulses, in a device with no vapour cell and no transverse mixture. Two
different causes of one class of error, published three weeks apart in
subject, and a paper of ours in this direction has to say which cause it
treats in its first paragraph.

**The same group is already in this record** as `yudin2020`, which is worth
noting because it means the lineage was reachable and was not read until the
literature pass of 2026-09-10.
