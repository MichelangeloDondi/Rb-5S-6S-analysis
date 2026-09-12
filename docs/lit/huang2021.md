---
citekey: huang2021
type: article
authors:
  - Huang, Chang
  - Chai, Shijie
  - Lan, Shau-Yu
title: 'Dark-state sideband cooling in an atomic ensemble'
journal: Phys. Rev. A
volume: '103'
pages: '013305'
year: 2021
doi: null
arxiv: null
pdf: PDF_papers/Lan group/Huang_2021_dark-state-sideband-cooling-optical-lattice.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags: []
verified_date: 2026-09-11
summary: >
  What the host group can hand this experiment, in the one unit that matters to
  a lineshape. An ensemble of 85Rb in an optical lattice is cooled in a
  dark-state Lambda system to a sub-recoil temperature of 100 nanokelvin with a
  vibrational quantum number near zero. At that temperature the transit width
  at every waist this record considers is below a tenth of a kilohertz, against
  a natural width of 3.5 megahertz, so the transit term that half of this
  record's width degeneracy is built from disappears. The companion paper
  reaches the recoil limit in 2.4 milliseconds, which is the speed a repetition
  rate cares about.
loci:
  - methods/09
section: lan-platforms
---
# huang2021

Held. Verified against the PDF on 2026-09-11.

## The result

A dark state in a Lambda-type three-level system cools an ensemble of 85Rb in
an optical lattice. The abstract states, verbatim, that the common suppression of the
carrier transition lets the atoms "reach a sub-recoil temperature of 100 nK
after being released from the optical lattice", with a nearly zero vibrational
quantum number from time-of-flight and adiabatic expansion.

## The companion, and the speed

<!-- not-from-pdf: the quotation below is huang2018's, verified verbatim in
     its own note against its own PDF. It is repeated here for the reader and
     must not be checked against this paper. -->
`huang2018` cools 85Rb in a two-dimensional lattice by two-step degenerate
Raman sideband cooling at a Lamb-Dicke parameter of 0.45, and reports the
"cooling of spin-polarized" atoms "to the recoil temperature in both dimension
within 2.4 ms" with adiabatic cooling. Two and a half milliseconds is short
against any duty cycle this record's forecast uses.

## What it means here

The transit width goes as the square root of the temperature. At 100
nanokelvin it is below 0.1 kilohertz at every waist from 64 down to 16
microns, where a 130 degree cell gives 0.97 to 3.87 megahertz. The published
correlation between the collisional width and the transit width in this
record's fits is -0.958, and that degeneracy is a property of a warm sample:
on a sub-recoil ensemble the transit term is not a fitted width at all.

The collisional width goes with it, since the density of such a sample is
orders below a 130 degree vapour. What is left is the natural width, the laser
and the light shift, which is a far better conditioned problem than the one
the 2025 archive poses.

## What it does not say

Nothing about atom number in a probe volume, which is the cost side of the
same trade and is priced in `wang2020` and `xin2018`.
