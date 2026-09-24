---
citekey: sedlacek2016
type: article
authors:
  - Sedlacek, J. A.
  - Kim, E.
  - Rittenhouse, S. T.
  - Weck, P. F.
  - Sadeghpour, H. R.
  - Shaffer, J. P.
title: 'Electric Field Cancellation on Quartz by Rb Adsorbate-Induced Negative Electron Affinity'
journal: Phys. Rev. Lett.
volume: 116
number: 13
pages: 133201
year: 2016
doi: 10.1103/PhysRevLett.116.133201
arxiv: '1511.03754'
pdf: PDF_papers/Sedlacek_2016_Rb-adsorbate-quartz-negative-electron-affinity-field-cancellation.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1511.03754v1 preprint (12 Nov 2015), titled "Electric field cancellation
    on quartz: a Rb adsorbate induced negative electron affinity surface"; the published PRL title is
    the one above, from Crossref, checked 2026-09-22 with the volume, article number and DOI. Read in
    full on 2026-09-22, the Methods appended to the preprint included (experimental details, the DFT
    summary and the electrostatic estimate of the adatom dipole).'
verified_date: 2026-09-22
summary: >
  Cold Rb atoms 20 to 800 um from a single-crystal quartz surface, probed by Rydberg EIT on 81D, see
  a field from Rb adsorbates of 1.7 V/cm at 500 um and 28 C, with a desorption activation energy of
  0.66 eV; with many Rydberg atoms, blackbody-ionised slow electrons bind to the surface, which Rb
  coverage turns into a negative-electron-affinity surface, and cancel the field to as little as
  30 mV/cm at 20 um for hours. The mechanism by which a Rb-exposed silica surface near Rydberg atoms
  can charge-compensate itself, and a second activation energy beside obrecht2007's.
loci:
  - methods/09
section: deep-search
---

# sedlacek2016

VERIFIED against the held preprint (scope in `verify_flags`).

## The measurement

A mirror MOT loads a magnetic trap about 2 mm from the (0001) face of a quartz crystal, the atoms are moved toward the surface and released, and the Stark shift of the 81D5/2 level, read by Rydberg EIT on absorption images with 5.5 um resolution, gives the field as a function of distance (Figs. 2 and 3). The adsorbate field points away from the surface. At 28 C it is 1.7 +- 0.1 V/cm at 500 um. Modelling the adsorbates as a charged double sheet with the calculated low-coverage dipole of 12 D, the authors estimate a coverage of 11 per cent (the Methods give 12.7 D from a Bader charge transfer of 0.947 over a 2.79 angstrom Rb-O bond in the DFT, and 12 D from Pauling electronegativities), and the temperature dependence fitted to a Langmuir isobar gives a desorption activation energy of 0.66 +- 0.02 eV (Fig. 4).

## What it finds

The abstract, verbatim: "We show that the adsorbed Rb induces a negative electron affinity (NEA) on the quartz surface." And its consequence, verbatim: "The NEA surface allows low energy electrons to bind to the surface and cancel the electric field from the Rb adsorbates." The electrons come from the Rydberg atoms themselves, ionised mostly by blackbody radiation with kinetic energies of about 10 meV. Raising the Rydberg population cuts the field about thirtyfold at 28 C. In the text, verbatim: "We demonstrate that E-fields as small as 30 mV cm−1 can be obtained 20 µm from the surface." Density-functional and electrostatic estimates both put the Rb-induced shift of the vacuum level at electron volts for modest coverage, with the negative affinity setting in near half a monolayer in the DFT. The bound electrons persist, verbatim: "Over the temperature range investigated, 28◦ C < T < 80◦ C, the Rb-quartz system can bind electrons for several hours." Light at 400 nm removes them, at a rate with an Arrhenius activation energy of 0.7 +- 0.07 eV (Fig. 6).

## Use in this record

This is the counter-case to treating a Rb-exposed silica surface as a fixed patch potential: the surface's field depends on the Rydberg atoms' own ionisation, on temperature and on light, and it can fall by more than an order of magnitude under conditions an experiment sets itself. For the fibre arm that is both a warning, the patch term is not a constant of the fibre, and an opportunity this record's own list of what the OIST nanofibre programme keeps already names, an atom-based monitor of the fibre's surface. The crystal face, the flat geometry and the tens of micrometres of distance differ from an amorphous fibre surface a few hundred nanometres away, the calculated 12 D per adatom here is four times the 3.2 D `obrecht2007` measured on fused silica, and the activation energy here, 0.66 eV for desorption from crystalline quartz, sits beside `obrecht2007`'s 0.42 eV on fused silica, read there as surface diffusion. The two are different processes on different surfaces and neither transfers to the fibre by itself.

Related on this shelf: `obrecht2007`, `mcguirk2004`, `abel2011`, `mamat2024` (UV photodesorption of electrons from a quartz cell, the opposite sign of intervention), `ocola2024` (Rydberg atoms near a nanophotonic device).
