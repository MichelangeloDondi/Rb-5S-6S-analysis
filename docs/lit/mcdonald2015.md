---
citekey: mcdonald2015
type: article
authors:
  - McDonald, M.
  - McGuyer, B. H.
  - Iwata, G. Z.
  - Zelevinsky, T.
title: 'Thermometry via Light Shifts in Optical Lattices'
journal: Phys. Rev. Lett.
volume: 114
number: 2
pages: 023001
year: 2015
doi: 10.1103/PhysRevLett.114.023001
arxiv: null
pdf: PDF_papers/mcdonald2015.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: 2026-09-10
summary: >
  The closest existing instance of a light-shift DISTRIBUTION used as the
  observable. A differential light shift between two states maps a trapped
  ensemble's energy distribution onto the line, and the carrier width
  inverts to the temperature. Prior art for the CONCEPT, and it runs the
  inference the other way: they know the coupling and solve for the
  distribution's parameter, where this record knows the distribution's form
  and solves for the coupling. It is also the closest published precedent
  for the guided in-trap thermometry this programme proposes, so it
  supports that proposal instead of pre-empting it.
loci: []
section: prior-art
---
# mcdonald2015

Held. Read against the PDF, five pages, 2026-09-10.

## What they do

Atoms or molecules in an optical lattice, where the ground and excited states
have polarizabilities `alpha` and `alpha'`. When the trap is not magic the
two differ, every trap level shifts by a different amount, and the thermal
population of trap levels is written onto the line. From the abstract,
verbatim: "a differential spectroscopic light shift can map temperature onto
the line shape with a low sensitivity to trap anharmonicity."

Their carrier thermometry is one equation. Verbatim: "This temperature
determination requires only the polarizability ratio" for the excited and
ground states at the trap conditions, "and the full-width-at-half-maximum
(FWHM)" of the carrier line shape, giving

    T_C ~ 0.295 Gamma_C / |sqrt(alpha'/alpha) - 1| x h / k_B

with four stated conditions: Boltzmann statistics in deep lattices, the
resolved-sideband regime, an unbroadened carrier width small against the
thermal one, and transverse sidebands not excited.

## Why this record must cite it, and where it bites

**It is the same CONCEPT with the inference reversed, and the overlap is
narrower than it first looks.** What is shared is the concept: a differential
light shift writes a distribution onto a line and the line can be inverted for
it. That is prior art, it is cited, and that is the whole of the overlap.

**The inference runs the other way.** They KNOW the coupling, the
polarizability ratio at the trap conditions, and solve for the DISTRIBUTION's
parameter, the temperature. This record knows the distribution's FORM, which
the beam profile fixes a priori, and solves for the COUPLING, the differential
polarizability, or for the geometry that sets it. Knowing the distribution is
this record's asset and their difficulty. It is reversed for the unknown.

**And the distributions are different mathematical objects, not the same one
with different parameters.** Their Eq. (10) is
`dE_x = (alpha'/alpha - 1) hbar omega_x (n_x + 1/2)`: a Boltzmann population
of DISCRETE harmonic-oscillator levels, mapped LINEARLY in the level index,
with the square root in their result coming from `omega` going as the root of
the polarizability. This record's ramp is a continuous geometric measure over
a Gaussian beam's intensity, `f(s)` proportional to `|s|`, whose cumulants
close in form. Neither derivation reaches the other.

**The observable differs, and that difference cuts this record's way.** They
invert the carrier FWHM, a WIDTH. On this line the width channel's WHOLE signal
at the predicted shift is 6.48 kHz on the Gaussian branch and 7.23 on the cusp
branch (`results/identifiability.csv`, `width_signature_broadening_khz`),
against a line of about 5.4 MHz: about one part in eight hundred, and the same
widths carry the collisional and laser nuisances at full strength. So the
construction that works in their lattice would, on this line, read the
nuisances and report them as the answer. That the shift lives in the odd
moments here and not in the width is this record's own methodological result,
and it is absent from their paper because their system does not have the
problem.

**Their regime is not this bench's**: deep lattice, resolved-sideband, an
unbroadened carrier narrow against the thermal width, transverse sidebands
unexcited. Four stated conditions, none of which a warm vapour cell meets.

**Delone 1980 remains the real constraint on novelty here** and this paper is
not a second one of the same size: same system class, same distribution form,
and this record's `f(s)` proportional to `|s|^(n-1)` reduces to its Eq. (5.3)
exactly. Conflating the two understates one and overstates the other.

**What differs, stated so the surviving claim is the honest one:**

| | mcdonald2015 | this record |
|---|---|---|
| the distribution | THERMAL, Boltzmann over trap levels | GEOMETRIC, set by the beam profile and known a priori |
| what is unknown | the temperature | the polarizability, or the waist |
| the observable | the carrier FWHM, a width | the mean pull and the third cumulant |
| the setting | deep lattice, resolved sideband, ultracold | warm vapour, Doppler-free two-photon |
| the kernel | narrow molecular line | Lorentzian, so the moments need a window |

The distribution being known in form is this record's asset and their
difficulty, and it runs the other way for the unknown. So the surviving
statement is not "reading a light-shift distribution off a lineshape is new".
It is that the distribution here closes in form, which yields an analytic
cumulant ladder and lets the SHAPE be inverted for a parameter of the
apparatus rather than of the ensemble.

## Two things worth taking

**The anharmonicity remark is the same structural point this record makes
about the centroid.** They note the temperature is "insensitive to
leading-order trap anharmonicities". This record's own version is that a
symmetric broadening about each element's own centre does not move a
mixture's mean, so the centroid survives a kernel that varies over the
volume while the third cumulant does not. Both are statements that one
moment is protected from a perturbation the neighbouring moment feels.

**Carrier cooling.** They reduce the temperature by a factor of 1.5 by weakly
exciting the hotter molecules in the tail of the line shape. Nothing in the
vapour-cell work needs it, but it is the clearest demonstration that the tail
of such a line IS the tail of the distribution, which is the assumption the
whole inversion rests on.

**AND IT IS THE PRECEDENT FOR THE GUIDED PROPOSAL, WHICH IS THE READING THE
FIRST DRAFT MISSED.** The forward-looking case for a two-photon probe inside a
hollow-core fibre is exactly this measurement: atoms held in a 1064 nm lattice,
a differential light shift between the probe's two states, and the line
inverted for the ensemble's temperature. That is what this paper demonstrates,
in a lattice, in a refereed letter, with the anharmonicity sensitivity priced.
So for the guided arm it is support and not competition, and the honest framing
of that proposal cites it as the method's demonstration instead of avoiding
it. The transfer is not free: their insensitivity to anharmonicity is a
property of harmonic-oscillator eigenstates, and a guided trap's radial motion
is neither cooled nor harmonic far from the axis, so the guided case owes its
own version of that argument.

## What was NOT checked here

The 0.295 was not re-derived and is quoted as theirs. The paper's lattice-clock
accuracy discussion is read but not used, since this record's line is not a
clock transition and the geometry is not a lattice.
