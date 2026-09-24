---
citekey: lekien2013
type: article
authors:
  - Le Kien, F.
  - Schneeweiss, P.
  - Rauschenbeutel, A.
title: 'Dynamical polarizability of atoms in arbitrary light fields: general theory and application to cesium'
journal: Eur. Phys. J. D
volume: 67
number: 5
pages: 92
year: 2013
doi: 10.1140/epjd/e2013-30729-x
arxiv: '1211.2673'
pdf: PDF_papers/LeKien_2013_dynamical-polarizability-arbitrary-light-fields-vector-tensor.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1211.2673v2 preprint (6 Dec 2012); journal, volume, article number and DOI
    are Crossref''s record, checked 2026-09-22. Sections I to III read line by line on 2026-09-22; the
    appendices (the two-level derivation, the derivation of the tensor-component expressions, the
    static-field case and the data tables) are read for their role only, and no number below comes
    from them.'
verified_date: 2026-09-22
summary: >
  The ac Stark operator of a multilevel atom in a far-detuned field of arbitrary polarization, split
  into scalar, vector and tensor polarizabilities, with the conditions under which the hyperfine-level
  form holds, the vector part recast as a fictitious magnetic field along i E* x E, and the tensor part
  vanishing for J = 1/2; worked for cesium, with its magic and pure-vector wavelengths. The reference
  for why a nanofibre's elliptically polarised evanescent field adds a vector light shift that a
  linearly polarised cell beam does not.
loci:
  - methods/09
section: deep-search
---

# lekien2013

VERIFIED against the held preprint (scope in `verify_flags`).

## The frame

The introduction states the problem, verbatim: "In general, the light shift (ac Stark shift) depends not only on the dynamical polarizability of the atomic state and on the light intensity but also on the polarization of the field." And names the case this record meets, verbatim: "One example is nanofiber-based atom traps, which have recently been realized [5, 6] and in which the nanofiber-guided trapping light fields are evanescent waves in the fiber transverse plane [7]." The authors aim to put in one source the definitions that earlier treatments stated differently, among them the counter-rotating terms, the convention for reduced matrix elements and the coupling between hyperfine levels.

## What it derives

The second-order shift operator, written in the fine-structure basis, has scalar, vector and tensor parts built from reduced polarizabilities of rank 0, 1 and 2 (their Eqs. 10 to 16). The vector part carries i[u* x u] and so, verbatim for linear polarization, the vector product vanishes, "making the contribution of the vector polarizability to the ac Stark shift to be zero." For the tensor part, verbatim: "Thus, the tensor polarizability vanishes for J = 1/2 states (e.g., the ground states of alkali-metal atoms)." The form written in a single hyperfine level (Eq. 17) neglects the Stark coupling between hyperfine levels, and the authors rank it, verbatim: "Thus, Eq. (17) is less rigorous than Eq. (15)." Where Zeeman splittings dominate, the shift of a sublevel depends on the field's polarization through two numbers: the ellipticity in the transverse plane for the vector part, and one minus three times the squared longitudinal component for the tensor part, which vanishes when that component is 1/sqrt(3) (Eqs. 19 and 20). The vector part acts as a fictitious magnetic field along i[E* x E], the same for every hyperfine level of a fine-structure level and additive to a real field (Eqs. 21 to 26).

For cesium, with couplings to highly excited levels included, the static scalar polarizability of 6S1/2 comes out 398.9 a.u. against 399.8 and 398.2 from all-order theory and 401 measured, and 6P3/2 gives 1639.6 a.u. scalar and -260.4 tensor. The scalar curves cross at the magic wavelengths 686.3 and 935.2 nm, and the ground state's scalar polarizability vanishes at 880.2 nm while its vector one does not (Figs. 2 to 6). On the magnitudes, verbatim: "Due to this fact, the vector polarizability can contribute significantly to the Stark shift when the polarization of the field is not linear."

## Use in this record

The 5S to 6S line joins two J = 1/2 levels, so no tensor light shift enters, and in the cell's linearly polarised beams no vector shift does either. The chapter's differential polarizability is then the scalar one. In a nanofibre's evanescent field neither premise holds everywhere: the field is elliptically polarised with a longitudinal component, so each hyperfine sublevel gains a vector shift that differs between 5S and 6S and between F levels, which acts as a fictitious magnetic field and shifts and splits the line in ways the scalar term does not. The formalism here is what a fibre-arm line model needs to carry that term, and it names the approximation, neglecting hyperfine-level coupling, that must be checked when the light shift approaches the 6S hyperfine splitting. The paper's numbers are for cesium. Rubidium's vector polarizabilities at 993 nm are not in it.

Related on this shelf: `vylegzhanin2025` (a fictitious magnetic trap for ground and Rydberg atoms at a nanofibre), `pache2025` (a magic-wavelength two-colour nanofibre trap), `grimm2000` (the dipole-trap light-shift convention), and, from the reviewer's intake of 2026-09-21, `lacroute2012` and `goban2012` (state-insensitive nanofibre traps).
