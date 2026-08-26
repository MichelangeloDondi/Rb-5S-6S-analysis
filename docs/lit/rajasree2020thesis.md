---
citekey: rajasree2020thesis
type: misc
authors:
  - Rajasree, Kritika Kumari Sharma
title: 'Rydberg Excitation and Other Multiphoton Processes in Cold Rubidium Atoms Near an Optical Nanofibre'
journal: 'PhD thesis, Okinawa Institute of Science and Technology Graduate University'
volume: null
pages: null
year: 2020
doi: null
arxiv: null
pdf: PDF_papers/theses/Rajasree-KP_2020_PhD-thesis_Rydberg-multiphoton-cold-Rb-nanofibre_OIST.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Disambiguation, and the reason this file exists. The citekey rajasree2020
    is a different document -- Phys. Rev. Research 2, 012038, "Generation of
    cold Rydberg atoms at submicron distances from an optical nanofiber", a
    cold-atom nanofibre experiment with no warm vapour cell. Until 2026-07-31
    both LITERATURE.md and docs/lit/rajasree2020.md attributed this thesis''s
    993 nm vapour-cell apparatus to that citekey. There is also
    rajasree2020spin, a third Rajasree 2020 document. Check which is meant.'
  - 'The author''s name is given here as printed on the OIST record. Thesis
    front matter and the PRR paper use different orderings of the same name;
    confirm the preferred form before formal citation.'
verified_date: 2026-07-31
summary: >
  OIST PhD thesis (Nic Chormaic group), 149 pp, September 2020. Its Chapter 5
  is the warm-cell half of the OIST 993 nm lineage: section 5.2,
  "Single-Frequency, Two-Photon Spectroscopy in a Rubidium Vapour Cell",
  repeats the apparatus this programme's density chain leans on -- a 150 mW
  993 nm beam focused by L1 (f = 150 mm) to a MEASURED 128 um beam diameter
  (Thorlabs BC106VIS profiler), retro-reflected by a concave mirror
  (f_CM = 75 mm) at 2 f_CM, with the cell held at 130 C -- and cites Steck for
  the Rb data, which is the N(T) vapour-pressure chain rb5s6s/density.py uses.
  Created 2026-07-31 to carry a FEED claim that had been misattributed to the
  PRR paper's citekey.
loci:
  - M7
  - P1
section: oist-lineage
---

# rajasree2020thesis

Held. Section 5.2 verified against the PDF.

## The system

OIST PhD thesis (Nic Chormaic group), September 2020, 149 pp. Section 5.2, "Single-Frequency, Two-Photon Spectroscopy in a Rubidium Vapour Cell," describes a warm-cell 993 nm two-photon spectroscopy apparatus. This document is distinct from the citekey [rajasree2020](rajasree2020.md) (Phys. Rev. Research 2, 012038), which reports cold Rydberg atoms near an optical nanofibre with no warm vapour cell, and from rajasree2020spin, a separate paper on spin selection in single-frequency two-photon excitation.

## The apparatus

The vapour cell is held at 130°C. A 993 nm laser at 150 mW is focused onto the cell by lens L1 (f = 150 mm) to a beam diameter of 128 µm, measured with a Thorlabs BC106VIS beam profiler. A concave mirror (f_CM = 75 mm), placed at 2 f_CM from L1, retro-reflects the beam. The thesis cites Steck's *Rubidium 87 D Line Data* for the rubidium vapour-pressure data.

## Use in this record

This thesis is the source of record for the beam waist this repository uses. Its measured beam diameter of 128 µm, radius 64 µm, was taken on the same optical table, the same laser and the same lenses as the 2025 campaign, so `W0_MEASURED_M` in [`rb5s6s/constants.py`](../../rb5s6s/constants.py) is a same-bench measurement rather than a value carried across apparatus. [nieddu2019](nieddu2019.md) is kept for lineage and is not the measurement. What the campaign did not do is read the waist off its own beam at its own time, so drift or realignment since remains open and is the record's largest stated systematic, traced on [the beam waist](../wiki/the-beam-waist.md). The vapour-pressure route in `rb5s6s/density.py` and the cell apparatus described here both draw on Steck's *Rubidium 87 D Line Data*.
