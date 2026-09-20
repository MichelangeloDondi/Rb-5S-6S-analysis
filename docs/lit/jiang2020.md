---
citekey: jiang2020
type: article
authors:
  - Jiang, J.
  - Li, X.-J.
  - Wang, X.
  - Dong, C.-Z.
  - Wu, Z. W.
title: 'Tune-out wavelengths of the hyperfine components of the ground level of 133Cs atoms'
year: 2020
doi: null
arxiv: '2010.11005'
pdf: PDF_papers/Jiang_2020_tune-out-wavelengths-Cs-ground-hyperfine.pdf
held: true
status: REPORTED
routing: []
verify_flags:
  - Pages 1 and 2 of the arXiv:2010.11005v1 preprint read against the PDF on
    2026-09-20. No publisher journal reference appears on either page, so
    journal/volume/pages are left unset rather than guessed. The numerical
    results tables beyond Table II and the tune-out-wavelength calculations
    themselves (Secs. III onward) are not read.
verified_date: null
summary: >
  A semiempirical relativistic configuration-interaction-plus-core-polarization
  calculation of the static and dynamic polarizabilities and tune-out
  wavelengths of the 133Cs ground level, resolved by hyperfine component. It
  is Cs-only, ground-state-only, and has no connection to the 5S-6S
  transition or to this repository's vapour-cell lineshape work. Its only
  point of contact is conceptual, since a tune-out wavelength is the same
  kind of zero-crossing object herold2012 uses to pin down Rb matrix
  elements, and this paper illustrates how much hyperfine structure can
  perturb such a crossing.
loci: []
section: unsorted
---
# jiang2020

## Values

| field | value | where in the paper |
|---|---|---|
| hyperfine shift of the first primary tune-out wavelength, one component | about -0.0135 nm | p. 1, abstract |
| hyperfine shift of the first primary tune-out wavelength, other component | about 0.0106 nm | p. 1, abstract |
| tensor-polarizability contribution to the tune-out wavelengths | about 1e-5 to 1e-6 nm | p. 1, abstract |
| core static dipole polarizability, alpha_core^(1) | 15.8(1) a.u. | p. 2 |
| core static quadrupole polarizability, alpha_core^(2) | 86.4 a.u. | p. 2 |
| cutoff parameter rho for the modified dipole operator | 3.6280 a.u. | p. 2 |
| target static ground-state polarizability used to fix rho | 400.8(4) a.u. | p. 2 |

## What it says, in its own terms

The paper calculates static and dynamic electric-dipole polarizabilities and
tune-out wavelengths (wavelengths at which the dynamic polarizability, and
so the optical dipole force, vanishes) for the ground level of 133Cs, using
a semiempirical relativistic configuration-interaction-plus-core-polarization
method: a Dirac-Fock Cs+ core plus a valence electron in a model potential
with a semiempirical, angular-momentum-dependent polarization term,
diagonalized in a large L-spinor basis. The valence dipole matrix elements
use a modified transition operator with a core-polarization correction,
whose cutoff radius is tuned so the calculated static ground-state
polarizability matches the measured value of 400.8(4) a.u.

Its specific contribution is adding hyperfine structure: computing the E1
matrix elements between hyperfine sublevels and evaluating the hyperfine
Stark shifts and tune-out wavelengths of the individual hyperfine components
of the 6s1/2 ground level, rather than of the level as a whole. It finds the
hyperfine components of the lowest ("first primary") tune-out wavelength are
shifted from each other by about -0.0135 nm and 0.0106 nm, comparable in
size to the hyperfine interaction energies themselves, while the
tensor-polarizability contribution to the tune-out wavelength is much
smaller, of order 1e-5 to 1e-6 nm.

## What it is worth here

An atomic-structure methods paper on caesium's ground-state hyperfine
tune-out wavelengths, with no rubidium content and no connection to the
5S-6S transition, the ac-Stark ramp, or the collisional lineshape work this
repository does. Its only point of contact is conceptual: a tune-out
(zero-crossing) wavelength is the same kind of object as the magic-zero
wavelengths herold2012 uses to pin down Rb matrix elements, and this paper
is one illustration of how hyperfine structure perturbs such a crossing at
the part-per-thousand level, a caution to carry qualitatively rather than a
number to import.
