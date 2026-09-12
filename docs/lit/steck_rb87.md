---
citekey: steck_rb87
type: misc
authors:
  - Steck, Daniel Adam
title: 'Rubidium 87 D Line Data'
journal: null
year: 2021
doi: null
arxiv: null
pdf: PDF_papers/Steck_2021_Rb87-D-line-data.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags: []
verified_date: 2026-09-11
summary: >
  The 87Rb half of the D-line data this record's frequency axis rests on,
  separated from [[steck_rb]] so that the 87Rb magnetic dipole constant is
  checked against the document that actually carries it. Its value times
  (I + 1/2) gives the 5S splitting the ruler's second shift-immune pair is
  built from.
loci:
  - constants
  - methods/05
section: method-anchors
---
# steck_rb87

Held and checked. The companion note is [steck_rb](steck_rb.md), which carries
the 85Rb document and the chain both isotopes feed.

## What is taken

The ground-state magnetic dipole constant, verbatim from the data table:
"Magnetic Dipole Constant, 5 2S1/2 A5 2S1/2 h · 3.417 341 305 452 145(45) GHz".

## Why it is a separate note

A note names one held document, and a passage marked verbatim is read against
that one. The 87Rb constant therefore needs the note whose file carries it, or
half the frequency axis rests on a document no note names.

## The chain it closes

At `I = 3/2` the ground-state splitting is `2A`, so 6834.682611 MHz against the
6834.682610 this record carries, a 1 Hz difference of rounding. Subtracting
Ayachitula's 6S splitting gives the second shift-immune ruler pair,
6834.682611 - 1614.709(3) = 5219.9736 MHz against the record's 5219.973.

## What it does not settle

Steck tabulates the D lines. The 6S state is not in it, so the other half of
the pair is a separate measurement with its own error, and nothing here bears
on the 6S branching or the 6S-5P matrix elements.
