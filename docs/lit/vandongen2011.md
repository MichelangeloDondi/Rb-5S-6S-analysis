---
citekey: vandongen2011
type: article
authors:
  - Van Dongen, J.
  - Zhu, C.
  - Clement, D.
  - Dufour, G.
  - Booth, J. L.
  - Madison, K. W.
title: 'Trap-depth determination from residual gas collisions'
journal: Phys. Rev. A
volume: 84
pages: 022708
year: 2011
doi: 10.1103/PhysRevA.84.022708
arxiv: null
pdf: PDF_papers/VanDongen_2011_trap-depth-from-residual-gas-collision-loss-rate.pdf
held: true
status: REPORTED
routing:
  - CITE
verify_flags:
  - Pages 1 and 2 read against the PDF on 2026-09-20 (title, abstract, introduction, the
    proposal in Sec. II, and the opening of Sec. III). The experimental sections (IV-V) on the
    photoassociative-loss cross-check and the measured trap depths themselves are not read.
  - 2026-09-20: adversarial audit_F corrected three defects. The trap-depth row carried a
    fabricated Kelvin-to-millikelvin conversion, claiming the abstract states "0.5 to 3 K" and
    that the true figure is 0.5 to 3 mK. Neither is right: the range is not in the abstract at
    all but in Sec. I, and it is 0.5 to 3 Kelvin as printed, corroborated on pp. 5-6 by the
    paper's own 2 K MOT depth against a 3 mK magnetic-trap depth and its 600 mK and 200 mK MOT
    figures.
    The fabricated conversion is removed and the row now states the plain value and its real
    location. All three C6 rows also gained the exponent the paper's own units carry (E_h a_B^6,
    not E_h a_B), and the two excited-state rows no longer assert a specific pairing between one
    J-level and one symmetry label, since the paper states both 5^2P1/2 and 5^2P3/2 together
    against both Sigma and Pi without making that assignment.
verified_date: null
summary: >
  The UBC Madison-group's foundational method paper for determining the depth of an atomic or
  molecular trap from the loss rate induced by collisions with a background gas of known
  composition and controllable density, validated on a Rb magneto-optical trap against an
  independent photoassociative-loss technique. It is the methodological ancestor of this
  list's stewart2022 and shen2023, and its own C6 values for Rb-Ar in the ground vs. two
  excited electronic states usefully illustrate, inside this record's own collision-series,
  how far an excited-state van der Waals coefficient can sit from its ground-state
  counterpart for the same atom pair. It is adjacent to this record: a cold-trap collision
  diagnostic, not a spectral-line self-broadening measurement.
loci: []
section: collision-series
---
# vandongen2011

## Values

| field | value | where in the paper |
|---|---|---|
| affiliation | UBC Physics & Astronomy; BCIT Physics | p. 1 |
| DOI (printed on the paper itself) | 10.1103/PhysRevA.84.022708 | p. 1 |
| C6, ground-state Rb (5^2S1/2) with Ar | 280.0 E_h a_B^6 | p. 2 |
| C6, excited-state Rb (5^2P1/2 or 5^2P3/2, Sigma) with Ar | 924.1 E_h a_B^6 | p. 2 |
| C6, excited-state Rb (5^2P1/2 or 5^2P3/2, Pi) with Ar | 545.1 E_h a_B^6 | p. 2 |
| trap-depth range validated with a MOT | about 0.5 to 3 K | p. 2, Sec. I |
| background gas used for the controlled study | 40Ar (zero nuclear spin, no spin-exchange channel) | p. 2 |

## What it says, in its own terms

**The proposal.** The total particle-loss rate from a trap is a sum, over background-gas
species, of each species' density times a velocity-averaged loss cross section that is itself
a monotonically decreasing function of the trap depth. Because of this monotonicity, a
measured loss rate at fixed background gas composition uniquely determines the trap depth: the
paper's central proposal is to invert a first-principles calculation of the loss-rate-vs-
depth dependence (built from the van der Waals interaction potential between trapped and
background species) to read off an unknown trap depth from a measured loss rate.

**The validation.** The method is demonstrated on a 87Rb magneto-optical trap and a magnetic
trap, using 40Ar as the introduced background gas specifically because argon's zero nuclear
spin removes any spin-exchange collision channel, leaving only elastic collisions to model.
The inferred trap depths are cross-checked against an independent photoassociative-loss
technique (adapted from Hoffmann et al.), with the paper reporting consistency between the two
routes (the quantitative comparison itself, in Sec. V, is not read here).

**The C6 values quoted.** The paper states C6 = 280.0 E_h a_B^6 for a ground-state
(5^2S1/2) Rb atom colliding with ground-state Ar, against C6 = 924.1 E_h a_B^6 (Sigma symmetry)
and 545.1 E_h a_B^6 (Pi symmetry) for Rb in its excited 5^2P1/2 or 5^2P3/2 state colliding with
Ar (p. 2), a factor of roughly two to three between the ground- and excited-state
coefficients for the identical atom pair, cited from refs [49, 50] rather than newly computed
here.

## What it is worth here

Adjacent, and useful mainly for one number. This is the methodological ancestor of stewart2022
and shen2023 in this list, establishing the collision-universality-based trap diagnostic those
later papers build on and extend to a self-calibrating pressure standard. None of the three is
a spectral-line self-broadening measurement, so nothing here is a beta_self input for this
record's own Rb 5S-6S line. What is genuinely useful is the Rb-Ar ground-vs-excited-state C6
contrast quoted above: it is a concrete, citable illustration that an excited-state van der
Waals coefficient need not resemble its ground-state counterpart for the same collision
partner, which is exactly the caution against reading stewart2022's ground-state Rb-Rb C6 as a
stand-in for this record's own excited-state self-broadening coefficient.
