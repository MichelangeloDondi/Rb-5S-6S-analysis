---
citekey: siddons2008
type: article
authors:
  - Siddons, Paul
  - Adams, Charles S.
  - Ge, Chang
  - Hughes, Ifan G.
title: 'Absolute absorption on rubidium D lines: comparison between theory and experiment'
journal: J. Phys. B
volume: 41
number: 15
pages: 155004
year: 2008
doi: 10.1088/0953-4075/41/15/155004
arxiv: 0805.1139
pdf: PDF_papers/Siddons_2008_absolute-absorption-Rb-D-lines-theory-vs-experiment.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'the journal volume, issue and article number are taken from the journal record, the arXiv v1 is the copy held'
verified_date: 2026-09-13
summary: >
  The absolute Doppler-broadened D-line absorption of a thermal Rb cell
  modelled from the line strengths and the atomic motion and compared with
  experiment, in the weak-probe limit. Held for one thing: its appendix
  states the vapour-pressure relation it stands on, Nesmeyanov's liquid
  correlation as this record's density module carries it, and its agreement
  with experiment is therefore evidence about that law at a measured
  temperature, which is the reading the density-law producer needs.
loci: []
section: method-anchors
---
# siddons2008

Held, the arXiv version, checked against the PDF for the passages quoted.

## What it covers

A model of the absolute absorption and dispersion of a weak probe on the Rb
D lines in a thermal cell, every hyperfine transition of both isotopes
included, compared with measured absolute transmission. The abstract states,
verbatim, "Theory and experiment show excellent agreement, with an rms error
better than 0.2% for the D2 line at 16.5◦ C", and the weak-probe condition
is "an intensity under one thousandth of the saturation intensity".

## The passage this record uses

Appendix A gives the number density from the vapour pressure. For liquid
rubidium the paper's equation (A.2) is the same four-coefficient form
`density.py` carries (15.88253, 4529.635, 0.00058663, 2.99138), and the
density follows as (A.3), the pressure in torr times 133.323 over kT. So a
comparison of this paper's absolute absorption with its theory is a test of
Nesmeyanov's correlation at the paper's measured temperature and at its
thermometry, which the paper describes as "A thermocouple was used to
measure the approximate temperature of the cell."

## Why it is held beside Achar 2025 and not instead of it

Achar et al. (2025, microfabricated cells, 293 to 353 K) find their densities follow the
Alcock-Itkin-Horrigan relation, which sits 15 to 24 per cent above
Nesmeyanov's over this record's 70 to 130 C. Both cannot be "in agreement"
at the few per cent level unless each comparison is a comparison at a
measured temperature, and a kelvin is 5.6 to 7.8 per cent of the density
here: the two laws' gap is a three-to-four-kelvin thermometry offset between
the experiments that support them (`results/density_laws.csv`,
`ratio_as_kelvin`). That is why the record adopts one law for the anchor and
the archive and carries the other as the envelope, and why the campaign
measures its density by absorption in situ rather than from a law.
