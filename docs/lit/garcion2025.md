---
citekey: garcion2025
type: article
authors:
  - Garcion, Charles
  - Gill, Sukhjovan S.
  - Misslisch, Magdalena
  - Heidt, Alexander
  - Papadakis, Ioannis
  - Piest, Baptist
  - Schkolnik, Vladimir
  - Wendrich, Thijs
  - Prat, Arnau
  - Bleeke, Kai
  - Müntinga, Hauke
  - Krutzik, Markus
  - Chiow, Sheng-wey
  - Yu, Nan
  - Lotz, Christoph
  - Gaaloul, Naceur
  - Rasel, Ernst M.
title: 'Dark energy search by atom interferometry in the Einstein-elevator'
journal: EPJ Quantum Technology
volume: 12
pages: 65
year: 2025
doi: 10.1140/epjqt/s40507-025-00371-0
pdf: PDF_papers/atom_interferometry/Garcion_2025_dark-energy-chameleon-atom-interferometry-einstein-elevator.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/garcion2025.md  # line-by-line against the held PDF, 2026-09-22, with one page-citation defect found and fixed (the Bragg-pulses and payload-reuse sentence), all other page and equation citations and both headline numbers confirmed exactly against 150 dpi page renders
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published, open-access article, EPJ Quantum Technology (2025)
    12:65, DOI 10.1140/epjqt/s40507-025-00371-0, printed in the running header of every
    page and in the PDF Subject metadata. 21 pages (pdfinfo), received 28 February 2025,
    accepted 21 May 2025. No arXiv identifier appears anywhere in the extracted text.'
  - 'All 21 pages read in full via pdftotext -layout. Equations (1)-(3) (pp. 2-3), (7)
    and the per-run sensitivity numbers (p. 6), the source-mass geometry and Fig. 3
    (p. 7), (8)-(10) (pp. 9-10), (13)-(15) (p. 11), and (16)-(17) with the
    Casimir-Polder numbers (p. 12) additionally checked against 150 dpi page renders,
    since pdftotext does not reliably preserve sub- and superscripts.'
verified_date: 2026-09-22
summary: >
  A proposal and sensitivity study for a chameleon dark-energy search that sends a
  Bose-Einstein condensate through a periodically structured source mass while the
  payload free-falls inside a Hannover drop-tower facility. A pair of multiloop atom
  interferometers, synchronized to the source mass's own spatial period, reads the
  crest-to-trough difference of the combined gravitational and chameleon potential as
  a differential phase, a construction shown to be independent of the potential's exact
  shape, immune to laser and vibration noise common to both interferometers, and immune
  to the quadratic term of any smooth background potential. The projected per-run
  sensitivity is about 6.87x10^-12 m^2/s^2 on that potential difference, expected to
  extend the excludable chameleon coupling by up to about 20 dB in places over a
  conventional vacuum-chamber source mass. Its systematics content concerns the source
  mass's own geometry, alignment and near-field surface potential, and it does not
  address laser intensity, interrogation-beam size or wavefront quality.
loci: []
section: unsorted
---

# garcion2025

VERIFIED. Held (published PDF, 2025), 21 pages. Read in full on 2026-09-22.

## What it does

The paper proposes and projects the sensitivity of a drop-tower test of chameleon scalar-field
dark energy. A Bose-Einstein condensate of rubidium-87 is produced on an atom chip, then sent
through a specially shaped source mass while the whole payload free-falls inside a microgravity
facility at Hannover offering up to 4.0 seconds of free fall and up to about 100 drops per working
day (p. 1, p. 13). The chameleon field is screened in dense environments, a thin-shell effect that
makes it hard to detect near bulk matter, but the screening weakens for a single free atom
(p. 2-3). The source mass is additively manufactured from a titanium alloy with a periodic,
corrugated inner bore, so both the ordinary gravitational potential and the hypothetical chameleon
potential vary periodically along the beam axis. Attaching or removing external rings of a dense
metal around the source mass changes the gravitational potential's periodicity and amplitude while
leaving the chameleon potential unchanged, because the chameleon field from the rings is screened
by the source mass's own wall (p. 7-9). A pair of multiloop atom interferometers, their pulse
timing synchronized to the source mass's spatial period, reads the crest-to-trough difference of
the combined potential as a differential phase (p. 4-6). That differential construction does not
depend on the detailed shape of the potential, only on the crest-to-trough difference, and the
paper argues this sidesteps the precision limit earlier chameleon searches hit from the
6.67430(15)x10^-11 m^3 kg^-1 s^-2 uncertainty on Newton's constant, which otherwise limits how
precisely the ordinary gravitational background can be modeled and subtracted (p. 2).

The interferometer beamsplitters are Bragg pulses (p. 17), which transfer momentum without
changing the atom's internal state. The payload reuses control electronics, software and part of
the laser architecture from an earlier space-flown Bose-Einstein-condensate mission, though its
own interferometry laser system was replaced (p. 2, p. 14, p. 17).

## The numbers

The projected per-run sensitivity chain, all on p. 6:

| quantity | value |
|---|---|
| interferometer time available, $2NT$ | 1.9 s |
| atomic mass | 87 amu (rubidium-87) |
| phase-to-potential scale factor | phi = 2.6x10^9 x delta-Vp |
| atom number per interferometer (assumed) | 5x10^4 |
| contrast (assumed) | 0.5 |
| per-run uncertainty on the crest-to-trough potential difference | 6.87x10^-12 m^2/s^2 |

Source mass geometry, p. 7: the outer radius is fixed at 11 mm by the clearance of the reused
payload's magnetic coils. The constraint that a beamsplitter transferring up to 4 photon momenta
must complete within the 1.9 s available sets the spatial period at or below 11.2 mm, and the paper
adopts 11 mm. The source mass is titanium alloy Ti-6Al-4V.

Casimir-Polder check, p. 11-12: for a rubidium-87 atom 2.5 mm from an idealized perfectly
conducting wall at 300 K, using a static ground-state polarizability of about 5.25x10^-39
J(m/V)^2, the potential is about 3.1x10^-42 J and the resulting acceleration about 2.6x10^-14
m/s^2, well below the targeted chameleon signal.

Expected exclusion reach, p. 12-13: for chameleon exponent n_ch = 1, the periodic source mass is
projected to improve the excludable coupling beta by up to about 20 dB near beta = 10^8 over a
conventional smooth spherical vacuum chamber, but the paper reports this advantage reversing for
beta > 10^10, where the chameleon force is very short-ranged. A further exclusion plot is given at
a fixed chameleon energy scale of 2.4 meV. The paper notes its own numerical convergence is poor
for negative values of n_ch.

Time budget, p. 16 (Table 1): the planned in-microgravity sequence sums to 3820 ms against the
4000 ms available, with the multiloop interferometry step itself budgeted at 1900 ms.

## Systematics

The paper is a design and sensitivity projection for an apparatus described as still being adapted
from earlier hardware, not a report of a completed measurement, so what follows is what the paper
characterizes or bounds in advance, not a finished error budget.

Intensity or differential light shift: not discussed. The beamsplitters are two-photon Bragg
pulses, which do not change the atom's internal state, so there is no Raman-type differential
light shift between two internal states of the kind a state-changing interferometer must budget.
The only laser intensity number given anywhere is the trapping beams' peak intensity, about
42 mW/cm^2 against a saturation intensity of about 3.576 mW/cm^2 for the rubidium-87 D2 line
(p. 15), and that number is used only to check the trap's scattering force can hold the atoms
against the drop capsule's launch acceleration, not to bound an interferometer phase.

Finite size of the interrogation beam: not discussed as a phase or contrast budget. The only beam
size given anywhere is the same trapping beams' waist radius, about 5.5 mm (p. 15), used for the
same mechanical check and not for the Bragg pulses that drive the multiloop sequence.

Wavefront, curvature or flatness: not mentioned anywhere in the paper. No such term appears in the
Taylor expansion of the background potential (Eq. 8, p. 9) or anywhere else, and no optical quality
or flatness specification is given for the interferometry beams.

Source mass position, alignment and the chameleon force's own screening length: this is the
paper's central systematics theme, argued three ways. First, the measured crest-to-trough
potential difference is shown not to depend on the detailed shape of the background potential
(p. 5), and the paired differential interferometer is built to reject laser phase noise and
vibration common to both halves (Eq. 7, p. 6). Second, for an even number of loops the dual
interferometer is shown to be algebraically immune to the quadratic term of a Taylor-expanded
background potential (Eq. 8-10, p. 9-10), removing the influence of the spatial variation of the
surrounding apparatus, the support platform, and any distant mass, and leaving only cubic and
higher terms that fall further with the loop count. Third, because the method depends on matching
the interferometer's own spatial period to the source mass's period, the paper proposes surveying
the pulse separation time to scan that match, fitting the resulting phase profile to a selectivity
curve that scales as the loop number squared (Eq. 15, p. 11), and separately scanning the
interferometer's starting position inside the periodic structure to project the measured phase
onto the expected signature. Both surveys are stated to further suppress systematic errors
(p. 11). The source mass's own near-field surface potential is checked and bounded through the
Casimir-Polder estimate above (p. 11-12), and a black-body-radiation potential from the source
mass's own thermal environment is argued away on the grounds that its temperature distribution is
not expected to share the source mass's own spatial periodicity, so the resonant,
periodicity-matched detection would not pick it up (p. 12). The chameleon force's own
characteristic length scale enters the model explicitly through a screening factor (Eq. 3, p. 3),
and the paper argues, as a critique of earlier contour-line estimates in the field, that an
interferometer's physical size can be orders of magnitude larger than the chameleon force's own
range at some points in parameter space, which its own point-by-point numerical evaluation of the
expected signal is built to handle correctly (p. 12).

## Routing

`private/INTERFEROMETRY_EXCHANGE_2026-09-22.md` synthesizes what this record's own work can offer
to, and draw from, the wider atom-interferometry community, for this application. This paper is
lineage only. It is a chameleon dark-energy search built around a drop-tower Bose-Einstein-
condensate interferometer and a periodically structured source mass, and it feeds no number into
this record's own rubidium 5S-6S two-photon vapor-cell model. Its own systematics content sits
almost entirely in the source mass's geometry, alignment and screening length, which has no
counterpart in a vapor-cell spectroscopy record: there is no source mass, no screening mechanism
and no periodic potential to match here. Its silence on differential light shift,
interrogation-beam size and wavefront quality means it offers no parallel to draw on for the
interferometry exchange's own light-shift-inhomogeneity or aperture-clipping items, unlike some of
the other held interferometry papers.

The paired differential interferometer of Eq. (7) (p. 6) rejects laser phase noise and vibration
because both interferometers share the same laser pulses, the same common-mode logic behind
reading several channels off one shared laser and one shared trace that this record's own
programme uses to separate a systematic from a genuine signal. The two are the same design
principle applied to unrelated hardware and unrelated physics, not a tested or shared method.

## Limits

The facility's mechanical and thermal specifications, the payload's power and vacuum systems, and
the laser system's module-by-module layout (Section 4, p. 13-19) were read in full but are not
carried here beyond the microgravity time budget, since they describe engineering feasibility and
not the systematics classes or the headline sensitivity estimate above.
