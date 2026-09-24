---
citekey: ocola2024
type: article
authors:
  - Ocola, P. L.
  - Dimitrova, I.
  - Grinkemeyer, B.
  - Guardado-Sanchez, E.
  - Đorđević, T.
  - Samutpraphoot, P.
  - Vuletić, V.
  - Lukin, M. D.
title: 'Control and Entanglement of Individual Rydberg Atoms near a Nanoscale Device'
journal: Phys. Rev. Lett.
volume: 132
number: 11
pages: 113601
year: 2024
doi: 10.1103/PhysRevLett.132.113601
arxiv: '2210.12879'
pdf: PDF_papers/Ocola_2024_Rydberg-atoms-near-nanoscale-device-surface-fields.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:2210.12879v1 preprint (23 Oct 2022) with its supplementary materials;
    the published PRL record (volume, article number, DOI, author spelling) is Crossref''s, checked
    2026-09-22. Main text read in full on 2026-09-22, and supplementary sections 1 and 2 (setup, UV
    tuning, the effect of Rydberg production); supplementary sections 3 to 7 (coherence models,
    two-atom fidelity, the gradient model, the choice of n) are not read line by line, and nothing
    below rests on them beyond numbers the main text also states.'
verified_date: 2026-09-22
summary: >
  Single 87Rb atoms in tweezers, excited to 70S at 90 to 2600 um from a silicon-nitride photonic
  crystal hung on a tapered silica fibre, see a field like a point charge of 126 electrons on the
  device, quasi-static, removed by decoupling sequences, and a background field from the fibre that
  vanishes only at an optimal UV illumination and with a steady rate of Rydberg excitation. The
  nearest published measurement of charges on a tapered silica fibre sensed by Rydberg atoms, with
  the two controls, light and the atoms' own ionisation, that the fibre arm would need.
loci:
  - methods/09
section: deep-search
---

# ocola2024

VERIFIED against the held preprint (scope in `verify_flags`).

## The system

A nanophotonic cavity 31.5 um long, fabricated in silicon nitride, is suspended on a tapered silica fibre on a translation stage and positioned 90 to 2600 um from single atoms held in 815 nm tweezers. The atoms are driven to 70S, whose polarizability is 534 MHz/(V/cm)^2, by a two-photon transition at 420 and 1013 nm, and the Rydberg population is read by atom loss (their Fig. 1 and supplementary section 1).

## What it finds

The main text, verbatim: "Remarkably, the electric field from this nanoscale device resembles a point-charge of ∼ 200 single electron charges (e) with quasi-static fluctuations, enabling coherent control via decoupling pulse-sequences at distances as close as 100 µm from the device." The spectral shift against distance fits a point charge of 126(11) e (Fig. 1B), and the entangled-pair gradient measurement 190(10) e with a background field. The coherence data bound the device charge's fluctuation to at most 8 e, with a background-field standard deviation of 0.012 V/cm. A W state of two atoms 3.15 um apart reaches a corrected fidelity of 0.83(4) at 170 um, and a Carr-Purcell sequence removes any decay within 10 us at every distance measured.

The controls are two. On illumination, verbatim: "At each distance the shift is minimized by illuminating the experimental setup with a UV diode and optimizing its power (Fig. 1B, inset) [26]." From the supplement, verbatim: "After changing the power of the UV diode, the spectral shift takes about an hour to settle." Much more UV, 29 mW, raises the device's fitted charge to about 34 500 e. On the atoms themselves, verbatim: "Furthermore, the spectral shift is stable only with a relatively constant rate of Rydberg excitation, interpreted as Rydberg-atom ionization creating charges that neutralize the device surface [26]."

On the fibre, verbatim: "Therefore, the fiber surface likely harbors a charge distribution that creates a background electric field when using a UV power that slightly deviates from the optimal." And, verbatim: "Remarkably, we can repeatably stabilize to a configuration where the fiber has no remaining charge by choosing the UV power that minimizes the spectral shift [26]."

## Use in this record

For the fibre arm this is the closest measured case: Rydberg atoms near a tapered silica fibre carrying charge, with the charge set by UV light, settling over an hour, and neutralised by the Rydberg atoms' own ionisation, the same mechanism `sedlacek2016` found on quartz. It implies that a patch-potential term measured at the fibre is a state of the surface under the experiment's own illumination and excitation rate, to be recorded with them, and that an hour-scale settling time belongs in the campaign's schedule. Its atoms sit 90 um and more from the structure. An atom in a nanofibre's evanescent field is two orders closer, where the field of a surface charge distribution does not reduce to a point charge, so the paper gives controls and time scales, not a field.

Related on this shelf: `sedlacek2016` (slow electrons from Rydberg ionisation cancel an adsorbate field on quartz), `mamat2024` (UV photodesorption of electrons at a quartz cell), `davtyan2018` (stray-field control on an atom chip), `rajasree2020` and `vylegzhanin2023` (Rydberg atoms near a nanofibre).
