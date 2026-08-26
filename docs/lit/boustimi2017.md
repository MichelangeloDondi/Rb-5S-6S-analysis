---
citekey: boustimi2017
type: inproceedings
authors:
  - Boustimi, M.
  - Loulou, M.
  - Natto, S.
  - Belafhal, A.
  - Baudon, J.
title: 'Van der Waals dispersion energy between atoms and nanoparticles'
journal: 'J. Phys.: Conf. Ser.'
volume: 869
pages: 012057
year: 2017
doi: 10.1088/1742-6596/869/1/012057
arxiv: null
pdf: PDF_papers/Boustimi_2017_J._Phys.__Conf._Ser._869_012057.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Author list completed 2026-07-31 from the paper''s own title block: M
    Boustimi, M Loulou, S Natto (Umm Al-Qura, Makkah), A Belafhal (Chouaib
    Doukkali, El Jadida) and J Baudon (LPL, Paris 13). Two earlier versions of
    this field were wrong and are recorded so the pattern is visible: the first
    guessed "Baudon, J.; Robert, J." from the author''s other work; the second
    took "M Boustimi, M Loulou, S Natto et al." from schmidt2011''s IOP citation
    list and truncated at "et al.". Baudon happens to be real -- which is
    exactly why the guess was not acceptable evidence.'
  - 'Its equations do not survive PDF text extraction (the reflection-coefficient
    and energy expressions come out as mojibake). Everything quoted below is
    from prose; the formulae themselves have not been read and must be taken
    from the rendered pages before use.'
verified_date: 2026-07-31
summary: >
  Open-access conference paper by the same author as the paywalled boustimi2002,
  presenting the same susceptibility-tensor framework for van der Waals
  dispersion energy and covering "sphere, cylinder and plane" geometries -- its
  section 2.2 treats an atom near a nanowire explicitly. Held as a
  possible free substitute for the method that sague2007 used to compute its own
  van der Waals shift. Carries the same limitation as the 2002 paper: the
  worked nanowire case is metallic, with the dispersion coefficients written to
  "carry the nonlocal behavior of the metal". So it supplies the framework, not
  a dielectric result. Replaced for the refit later the same day: frawley2012
  was found to be held, and is cylindrical, dielectric-capable and in a directly
  usable factorised form. Keep this only as an independent cross-check of the
  framework.
loci:
  - P2
section: method-anchors
---

# boustimi2017

Held. Verified from the prose. The equations did not survive PDF text extraction and have not been checked against the rendered pages.

## The system and method

An open-access conference paper by an author of the paywalled `boustimi2002`, presenting the same susceptibility-tensor framework for van der Waals dispersion energy and covering sphere, cylinder and plane geometries. Section 2.2, "Atom near a metallic nanowire," writes the atom-wire dispersive interaction (their Eq. 11) as an integral over the wire's reflection coefficient, with k_parallel the wave-vector component along the wire axis.

The worked case is metallic: the dispersion coefficients "carry the nonlocal behavior of the metal." Whether the reflection coefficient can be evaluated directly for a dielectric permittivity is not established in this paper.

## Use in this record

[sague2007](sague2007.md) computed its own van der Waals shift for the D2 line of Cs near a 500 nm dielectric cylinder, citing Boustimi's group for the method rather than for a number. [frawley2012](frawley2012.md) gives the same electrostatic approximation in cylindrical geometry, for both metal and dielectric, in the closed form U = -(C3/x0^3) mu, and supplies the numerical input used in the analysis. This paper is kept as an independent check on the susceptibility-tensor framework across sphere, cylinder and plane.
