---
citekey: schmidt2015
type: article
authors:
  - Schmidt, Felix
  - Mayer, Daniel
  - Hohmann, Michael
  - Lausch, Tobias
  - Kindermann, Farina
  - Widera, Artur
title: 'Precision Measurement of the 87Rb Tune-Out Wavelength in the Hyperfine Ground State F=1 at 790 nm'
journal: null
volume: null
pages: null
year: 2015
doi: null
arxiv: '1512.03578'
pdf: PDF_papers/Schmidt_2015_Rb-tune-out-wavelength-F1-790nm.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - 'Held as the arXiv preprint (1512.03578v1, dated 11 December 2015). No
    journal record or DOI appears in the pages read, so both are left null.
    Pages 1-2 of 8 read against the PDF on 2026-09-20 (abstract, introduction
    and the ac-Stark-shift/polarizability formalism of section II). The
    Kapitza-Dirac experimental method (section III) and the results are not
    yet read.'
verified_date: null
summary: >
  Precision measurement, by Kapitza-Dirac scattering of a Rb Bose-Einstein
  condensate off a 1D optical lattice, of the D-line tune-out wavelength for
  87Rb in the F=1, mF=0 hyperfine ground state: 790.01858(23) nm, a ten-fold
  accuracy improvement over an earlier measurement, sensitive to vector and
  tensor polarizability and core-electron contributions that the scalar
  two-level approximation neglects. A precision, same-atom (87Rb) benchmark
  for the hyperfine-resolved ac-Stark/polarizability formalism this record's
  own AC-Stark ramp model needs, though at a different wavelength and
  ground-state manifold than the 5S-6S transition itself.
loci: []
section: method-anchors
---

# schmidt2015

## Values

| field | value | where in the paper |
|---|---|---|
| preprint identifier | arXiv:1512.03578v1 [quant-ph], 11 Dec 2015 | p. 1 |
| affiliation | Department of Physics and Research Center OPTIMAS, University of Kaiserslautern, Germany | p. 1 |
| measured tune-out wavelength, F=1, mF=0 | 790.01858(23) nm | p. 1 |
| accuracy improvement over the earlier measurement (ref. [23]) | factor of 10 | p. 1 |
| D-line wavelengths bracketing the tune-out point | D1 795 nm, D2 780 nm | p. 1 |
| ac Stark shift formula (hyperfine, Zeeman-resolved) | $V^{(2)} = -\left(\frac{E_0}{2}\right)^2\left[\alpha^s + \frac{Cm_F}{2F}\alpha^v - \frac{D\left(3m_F^2-F(F+1)\right)}{2F(2F-1)}\alpha^T\right]$ | p. 2, Eq. (3) |
| vector-ac-Stark-shift-induced tune-out splitting between mF=0 and mF=+/-1 (circular light) | up to 2 nm | p. 2 |
| lattice pulse duration / beam waist / power per beam | 12 us / 29 um / up to 450 mW | p. 2 |
| Raman-Nath validity range (lattice depth) | absolute lattice depth much less than 125 recoil energies | p. 2 |
| AOM frequency shift / resulting wavelength shift | -160 MHz +/- 1 Hz / +0.42 pm at 790 nm | p. 2 |
| BEC preparation | about 2.5x10^4 atoms, crossed dipole trap at 1064 nm, optically pumped to F=1, mF=+1 | p. 2 |

## What it says, in its own terms

The paper measures the tune-out wavelength of 87Rb -- the wavelength at which the scalar AC-Stark shifts from the D1 and D2 lines cancel -- in the F=1 hyperfine ground-state manifold, using Kapitza-Dirac diffraction of a Bose-Einstein condensate from a pulsed one-dimensional optical lattice as the probe. Rather than the common approximations of averaging the two D-line linewidths and neglecting hyperfine structure, the paper sums the AC-Stark shift over every dipole-allowed hyperfine transition explicitly, which separates the total shift into scalar, vector and tensor polarizability contributions, each with its own dependence on the magnetic sublevel mF and on the light's polarization and propagation geometry relative to the quantization axis.

Because the dominant scalar shifts from the two D lines cancel by construction at the tune-out point, what remains is exactly the set of smaller effects the paper is designed to isolate: vector and tensor polarizability, contributions from transitions to higher principal quantum numbers, and the influence of core, non-valence electrons -- effects usually neglected in a two-level treatment. The vector shift vanishes only for mF=0, so measuring the magnetically insensitive mF=0 tune-out wavelength isolates the scalar-plus-tensor part cleanly. The paper reports this at 790.01858(23) nm, a tenfold accuracy improvement over an earlier measurement. For mF=+/-1, the vector shift is strong enough to move the tune-out point by more than 2 nm under circularly polarized light, which the paper turns into a diagnostic: the size of that vector-shift-induced splitting gives an in-situ, sub-percent measurement of the lattice light's absolute polarization purity and of the residual magnetic field.

The measurement itself uses Kapitza-Dirac scattering: a short, 12 microsecond, pulse of a one-dimensional standing-wave lattice diffracts the condensate into discrete momentum orders with Bessel-function-distributed populations, in the Raman-Nath regime where atomic motion during the pulse is negligible, so the lattice depth, and hence the AC-Stark shift, can be read out from the observed diffraction pattern near the wavelength where that depth crosses zero.

## What it is worth here

This is a precision, same-atom benchmark for the hyperfine-resolved AC-Stark/polarizability formalism -- scalar, vector and tensor terms summed over dipole-allowed hyperfine transitions -- that any careful treatment of light shifts in Rb needs, including this record's own AC-Stark ramp model, though the measurement itself sits at a different wavelength (790 nm) and in a different manifold (the ground-state hyperfine structure) than the 5S-6S two-photon transition and its 993 nm drive. Its main value here is methodological, and as an independent precision cross-check on the Rb polarizability inputs (vector and tensor terms, core contributions) that feed a full hyperfine AC-Stark calculation, rather than as a number this record can use directly.
