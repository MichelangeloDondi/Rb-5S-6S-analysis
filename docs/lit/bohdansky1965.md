---
citekey: bohdansky1965
type: article
authors:
  - Bohdansky, J.
  - Schins, H. E. J.
title: 'New Method for Vapor-Pressure Measurements at High Temperature and High Pressure'
journal: J. Appl. Phys.
volume: 36
number: 11
pages: 3683--3684
year: 1965
doi: 10.1063/1.1703066
arxiv: null
pdf: PDF_papers/Bohdansky_1965_heat-pipe-vapour-pressure-high-temperature.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - The full two-page communication (pp. 3683-3684) read against the PDF on 2026-09-20,
    including Tables I and II. It shares p. 3684 with the start of an unrelated second
    communication (Ferry, Young and Dougal, on microwave emission from InSb), which is not
    part of this note.
  - Table I's four metal columns (Cs, Li, Pb, Ag) are populated at different starting
    pressures (Ag from 40 Torr, Cs and Pb from 50 Torr, Li from 100 Torr), so the extracted
    text runs the columns together with uneven row lengths. Only the p = 100 Torr row, where
    all four columns are unambiguously populated and internally consistent with each metal's
    known boiling point ordering, is quoted below. The rest of the table is described only in
    aggregate (temperature and pressure spans), not cell by cell, to avoid mis-pairing a
    pressure with the wrong metal's temperature.
  - 2026-09-20: adversarial audit_A corrected two errors. The starting-pressure claim for
    Table I's columns read "Ag and Pb from 40 Torr, Cs from 50 Torr, Li from 70 Torr", when a
    column-position check against a rendered page shows Ag alone starts at 40 Torr, Cs and Pb
    both start at 50 Torr, and Li starts at 100 Torr. And "3683" in the overall-span row is the
    journal's own page-footer number, not a table entry, so the table's true maximum
    temperature is Pb at 2180 K, with Ag's own last entry at 2150 K.
verified_date: null
summary: >
  A short technique paper (CCR-Euratom, Ispra) describing a "heat pipe" method for measuring
  metal vapour pressures at high temperature and high pressure (above 500 Torr, above 600 C),
  using an inert-gas (argon) backing pressure that a working heat pipe separates cleanly from
  the metal vapour, so the vapour pressure equals the measured room-temperature gas pressure.
  Demonstrated on caesium, lithium, lead and silver, in good agreement with Nesmeyanov's
  calculated values. The method's own stated operating window (tube diameter under 1 cm,
  pressure above 50-100 Torr) sits far above the archive's own Rb regime (a small fraction of
  1 Torr at 70-130 C), so, like narsimhan1967 in this list, it is held as a vapour-pressure-
  metrology precedent that does not apply to this record's own density ladder.
loci: []
section: unsorted
---
# bohdansky1965

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | CCR-Euratom, Direct Conversion Group, Ispra (Varese), Italy | p. 3683 |
| DOI (from the citation record) | 10.1063/1.1703066 | p. 3683 (citation page) |
| received | 20 May 1965 | p. 3683 |
| stated operating regime | pressure above 500 Torr, temperature above 600 C, for prior methods; this method needs tube diameter below 1 cm and pressure above 50-100 Torr (material-dependent) for a sharp hot/cold transition | p. 3683 |
| hot-zone temperature uniformity | better than 5 C, for all four tested materials | p. 3683 |
| wall-to-vapour temperature difference (radiation cooling) | smaller than 4 C, for all four tested materials | p. 3683 |
| pressure drop needed to sustain the vapour stream | less than 1 Torr | p. 3683 |
| representative table row, p = 100 Torr | Cs 769 K; Li 1374 K; Pb 1710 K; Ag 2085 K | p. 3683, Table I |
| overall span of Table I | pressures from 40 to about 3660 Torr; temperatures from about 723 K (Cs, lowest tabulated) to about 2180 K (Pb, its highest tabulated point, at p = 1840 Torr; Ag's own last tabulated point is 2150 K at p = 150 Torr and does not reach the table's high-pressure end) | p. 3683, Table I |
| materials measured | caesium, lithium, lead, silver | p. 3683-3684 |
| purity of Ag and Pb samples | 99.999%, spectrographically standardized | p. 3684, Table II |

## What it says, in its own terms

**The method.** A vertical "test tube" holding the metal sample, with a capillary structure at
its lower end for evaporation, is connected to an argon reservoir and a room-temperature
manometer, and can be evacuated. Heating the lower part with an RF coil establishes, above a
material-dependent threshold argon pressure, a hot zone of essentially constant temperature
separated from a cold upper zone by a sharp transition: the outward vapour stream, condensing
on the radiation-cooled wall above the hot zone, pushes the inert gas ahead of it, cleanly
separating vapour from gas (an effect the paper attributes to an observation by Grover et al.
in a working "heat pipe"). Because the hot-zone temperature is set by the argon backing
pressure alone (heat input instead controls only the hot zone's length), the metal's vapour
pressure is read directly off the room-temperature argon gauge, with two small corrections:
a wall-condensation temperature offset (under 4 C for radiation cooling) and a pressure drop
needed to sustain the vapour flow (under 1 Torr), both estimated from the energy balance and
the temperature profile in the hot zone.

**The demonstration.** The technique is applied to caesium, lithium, lead and silver, with
wall temperature read by a thermocouple (Cs, Li) or a pyrometer (Pb, Ag). Table I tabulates
vapour pressure against temperature for each metal from about 40 Torr up to several thousand
Torr, and the paper states the results agree well with Nesmeyanov's calculated values,
without quoting a percentage difference.

## What it is worth here

Little, and for the same reason as narsimhan1967 in this list: a real vapour-pressure
technique paper whose own operating window does not reach this record's regime. The method
needs pressures above roughly 50 to 100 Torr to produce the sharp hot/cold transition it
relies on, while the archive's Rb cells run at 70-130 C, where Rb's vapour pressure is a small
fraction of 1 Torr, several orders of magnitude below this method's floor. None of the four
measured metals is rubidium. What is worth keeping on file is the general point that an
independent, high-temperature technique found good agreement with Nesmeyanov's calculated
vapour pressures for a different set of elements, consistent with this record's own reliance
on Nesmeyanov's four-term law as its headline Rb density model, but this paper supplies no
Rb-specific number and its method cannot be adapted to the archive's pressure range.
