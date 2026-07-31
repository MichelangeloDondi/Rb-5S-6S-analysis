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

**Held and read in part 2026-07-31.** Created to fix a citekey conflation, not
because a new document arrived: the thesis has been in `PDF_papers/theses/`
without a lit file, while the claim that depends on it was filed under
[rajasree2020](rajasree2020.md) — a different paper.

## What it supplies, and why it is [FEED]

Section 5.2 is the warm-cell 993 nm spectroscopy chapter. Verbatim from it:

> "During the experiment, the vapour cell is maintained at 130°C. A 993 nm laser
> of 150 mW is focussed on to the vapour cell using L1 (f = 150 mm). The beam
> diameter is 128 µm, measured using a beam profiler (Thorlabs, BC106VIS). Using
> a concave mirror (CM, f_CM = 75 mm), placed at 2 f_CM from lens L1, the beam is
> retro-reflected."

Two things this repository takes from that:

**The beam geometry.** It is the same focused-and-retro-reflected single-colour
993 nm arrangement this campaign runs, and the beam size is **measured**, not
inferred — with the profiler named. Note it is a **diameter**: 128 µm, so a
radius of 64 µm, in the same range as this campaign's unmeasured
$w_0 \approx 50$ µm and a useful sanity check on it. It does not substitute for
the knife-edge, which remains the largest open systematic.

**The N(T) chain.** The thesis cites Steck's *Rubidium 87 D line data* for the Rb
data, which is the vapour-pressure route `rb5s6s/density.py` uses. That makes
this a corroborating source for the density chain rather than an independent
measurement of it.

## The conflation this file corrects

Three Rajasree 2020 documents are in play and they were not being kept apart:

| citekey | document |
|---|---|
| [rajasree2020](rajasree2020.md) | *PRR* **2**, 012038 — cold Rydberg atoms near an ONF. **No warm cell.** |
| `rajasree2020spin` | a separate paper on spin selection in single-frequency two-photon excitation |
| **`rajasree2020thesis`** (this file) | the OIST PhD thesis, whose §5.2 is the vapour-cell apparatus |

`LITERATURE.md` and `docs/lit/rajasree2020.md` both described "Rajasree-KP's OIST
PhD thesis" while pointing at the PRR paper's citekey. The prose named the right
document; the key resolved to the wrong one. Corrected in both places
2026-07-31.

[nieddu2019](nieddu2019.md) remains the **primary** apparatus source for this
lineage — same group, and the published 993 nm frequency-reference paper. This
thesis corroborates it.
