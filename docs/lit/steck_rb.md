---
citekey: steck_rb
type: misc
authors:
  - Steck, Daniel Adam
title: 'Rubidium 85 D Line Data and Rubidium 87 D Line Data'
journal: null
year: 2021
doi: null
arxiv: null
pdf: PDF_papers/Steck_Rb85_D-line-data.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags: []
verified_date: 2026-09-10
summary: >
  The source of the ground-state hyperfine constants that rule this
  record's frequency axis, held for both isotopes and now read. Its two
  magnetic dipole constants, multiplied by (I + 1/2), give the 5S
  splittings this record carries to the digit, and subtracting
  Ayachitula's 6S splittings from them reproduces both shift-immune ruler
  pairs to better than a kilohertz.
loci:
  - constants
  - methods/05
section: method-anchors
---
# steck_rb

Held for both isotopes, `Steck_Rb85_D-line-data.pdf` and
`Steck_Rb87_D-line-data.pdf`, and checked against both.

## What is taken

The ground-state magnetic dipole constants, verbatim from the data tables:

    Magnetic Dipole Constant, 5 2S1/2   A 5 2S1/2   h . 1.011 910 813 0(20) GHz
    Magnetic Dipole Constant, 5 2S1/2   A 5 2S1/2   h . 3.417 341 305 452 145(45) GHz

the first for 85Rb and the second for 87Rb.

## The chain this closes

A ground-state hyperfine splitting is `(I + 1/2) A`, so `3A` for 85Rb at
`I = 5/2` and `2A` for 87Rb at `I = 3/2`:

| isotope | from Steck | this record carries |
|---|---|---|
| 85Rb 5S | 3035.732439 MHz | 3035.732439 |
| 87Rb 5S | 6834.682611 MHz | 6834.682610 |

The second differs in the last digit by 1 Hz of rounding.

**And that is only half the ruler.** The two shift-immune pairs the frequency
axis is built on are the 5S splitting minus the 6S splitting for each isotope,
with the 6S values from [ayachitula2024](ayachitula2024.md):

    3035.732439 - 717.195(3)  = 2318.5374 MHz    against the record's 2318.537
    6834.682611 - 1614.709(3) = 5219.9736 MHz    against the record's 5219.973

**So the axis is sourced end to end**, a sub-hertz atomic constant on the 5S
side and a 3 kHz measurement on the 6S side, and the record's claim that the
pairs are good to a few kilohertz is the 6S measurement's error and nothing
else. The residuals above, 0.44 and 0.61 kHz, are the rounding of the values
as carried.

## Why the pairs are shift-immune, which is the point of using them

Both members of a pair share an upper state and differ only in the ground
hyperfine level, so a light shift common to the pair cancels from their
separation while a frequency-axis error does not. That is what makes them a
ruler and not a line, and it is why the axis does not need the wavemeter
whose labels identify the peaks but do not measure them.

## What it does not settle

Steck tabulates the D lines. The 6S state is not in it, so the other half of
each pair is a separate measurement with a separate error, and no part of this
closes the 6S branching or the 6S-5P matrix elements.
