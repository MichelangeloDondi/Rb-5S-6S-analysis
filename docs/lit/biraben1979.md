---
citekey: biraben1979
type: article
authors:
  - Biraben, F.
  - Bassini, M.
  - Cagnac, B.
title: 'Line-shapes in Doppler-free two-photon spectroscopy. The effect of finite transit time'
journal: J. Phys. (Paris)
volume: 40
number: 5
pages: 445-455
year: 1979
doi: null
arxiv: null
pdf: PDF_papers/Biraben_1979_transit-time-lineshape-doppler-free-two-photon.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags: []
verified_date: 2026-09-10
summary: >
  The source of this record's transit kernel, cited in rb5s6s/lineshape.py
  since long before the paper was held, and now read. It derives the
  finite-transit Doppler-free two-photon line as a Lorentzian convolved
  with a two-sided exponential, which is exactly the shipped
  transit_kind='exp'. It also states a validity condition this record had
  not carried against it: the observation length must be small compared
  with the Rayleigh range.
loci:
  - methods/02
  - M9
section: method-anchors
---
# biraben1979

Held. Read against the PDF, twelve pages (HAL scan of J. Phys. Paris 40, 445),
2026-09-10.

## What it derives, and it is our kernel

From the abstract, verbatim: the treatment applied to the finite
transit time "permits a precise expression to be obtained for the line-shape
(convolution of a Lorentzian curve and a double-exponential curve)."

That is `rb5s6s.lineshape`'s `transit_kind='exp'`, the two-sided exponential
`exp(-|nu|/b)` with its central cusp, and the module's provenance block has
named this paper as ESTABLISHED since before the PDF was on this disk. The
citation is now discharged from the source, which closes a link of the same
class as the Volz lifetimes.

## The condition it states, and which this record had not checked against it

Setting up the geometry, verbatim: "The atoms are observed in the vicinity of
the waist of the focussed Gaussian beam over a length L which is small
compared to the Rayleigh length".

**The derivation is therefore a thin-slice result, and this bench's own
collection geometry is the thing that decides whether it applies.**
`constants.collection_z_ratio` returns exactly that ratio:

| w0 | L / z_R | the paper's "small compared to" |
|---|---|---|
| 128 um | 0.065 | holds |
| **64 um, the archive** | **0.261** | holds |
| 40 um | 0.667 | marginal |
| 24 um | 1.853 | violated |
| **16 um, the campaign's tightest** | **4.169** | violated by an order of magnitude |

The archive sits inside the licence. The campaign's tight-waist
configurations do not, and they use the same analytic kernel, since
`composite_profile` defaults to `transit_kind='exp'` and the forecast path
calls it. `transit_mc.py` is the module built for exactly this, a Monte Carlo
over the full `w(z)` that "builds in" the idealisation, and it is not on the
forecast path.

**This is the same ratio that already governs the collection window and the
ramp's moments** (the master plan's 4b-bis, where 1.117 is the third
cumulant's sign flip and 1.69 the windowed variance's). One geometric number
now decides three separate validity questions, and only two of them were being
asked.

## What it does not settle

It is a single-waist, thin-slice, plane-crossing derivation. It says nothing
about a mixture whose homogeneous kernel varies across the collected volume,
which is this record's convolution condition and a separate failure at the
same tight waists.
