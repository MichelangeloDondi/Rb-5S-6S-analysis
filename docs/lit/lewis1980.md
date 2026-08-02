---
citekey: lewis1980
type: article
authors:
  - Lewis, E.L.
title: 'Collisional relaxation of atomic excited states, line broadening and interatomic interactions'
journal: Phys. Rep.
volume: 58
number: 1
pages: 1--71
year: 1980
doi: 10.1016/0370-1573(80)90056-3
arxiv: null
pdf: PDF_papers/Lewis_1980_collisional-broadening-review-physics-reports.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'DOI taken from the ScienceDirect PII (0370157380900563) via search, not from the PDF itself, which carries no DOI. Volume/pages/year are printed on the PDF and match.'
verified_date: 2026-08-03
summary: >
  70-page review of collisional relaxation of atomic excited states: the
  density-matrix impact theory of line broadening, interatomic potentials,
  semiclassical and quantal S-matrix calculations, and a systematic
  comparison of theory against measured alkali and group-2b resonance and
  van der Waals broadening. Gives the general n=6 phase-shift van der Waals
  cross-section formula that our beta_self_vdw specializes, and is the
  source of the term "Lindholm-Foley" used in that module.
loci: []
section: collision-series
---

# lewis1980

**Read here 2026-08-03, in full (all 71 pages).** Verbatim, from the
conclusion: "Our survey of the above data indicates clearly that many
calculated potentials are capable of reproducing magnitudes and systematics
of collision cross-sections with considerably greater precision than long
range series approximations." The review's own summary of what it delivers,
and does not: reliable broadening coefficients from good long-range
potentials, not a probe of the inner (overlap) potential except in fine
structure transfer.

## What the review covers

A density-matrix derivation of the impact approximation for line width and
shift (Sec. 2), the multipole and Lennard-Jones forms used for interatomic
potentials with a note on how pseudopotential methods handle the core (Sec.
3), semiclassical (phase-shift, Anderson-approximation) and full quantal
partial-wave calculations of the collision S-matrix (Sec. 4), the
experimental methods (grating, Fabry-Perot, Hanle effect, level crossing,
magnetic resonance) used to extract cross-sections (Sec. 5), and a
comparison of theory against measurement in three families: resonance and
quasi-resonant broadening/depolarization of alkali and group-2b levels (Sec.
6.2), alkali D-line broadening and shift by the rare gases (Sec. 6.3-6.4),
and group-2b resonance lines broadened by rare gases and by their own vapor
(Sec. 6.5). It explicitly excludes non-resonant broadening/depolarization in
the rare gases as already reviewed elsewhere (Sec. 6.1).

## The coefficient formulas relevant to us

**1. Resonance dipole-dipole broadening does not apply to 5S-6S.** The
review's whole resonance-broadening apparatus starts from the first-order
dipole-dipole interaction, eq. (4.23):

    V(t) = -1/(4*pi*eps0*R^3(t)) * {3(d1.u)(d2.u) - d1.d2}

which is finite only "for the special case where the two systems are
identical only in different states which are connected by a dipole
transition" (Sec. 3.4, discussing the same term in the multipole series).
The resulting width formula, eq. (4.24),

    Dnu_1/2(Jg,Je;i) = K'(Jg,Je;i) * (1/pi) * sqrt[(2Jg+1)/(2Je+1)]
                        * e^2 * f_ge * N / (m*c^2*nu_eg)   [cm^-1]

carries the ground-to-excited oscillator strength f_ge directly, and K' is
close to unity for every case tabulated (Table 4.2). Since 5S-6S is an S-S
pair with no allowed dipole transition between the two states in question,
f_ge = 0 for this channel and the whole formula, and every K' constant in
Tables 4.2/4.3, is structurally inapplicable to a 5S-6S self-broadening
coefficient. This is the textual version of what weller2011.md already
argues from the physics: Weller's D1 beta_self is a resonance number and a
ceiling, not an estimate, for exactly this reason.

**2. The van der Waals formula our anchor specializes.** Section 4.2 derives
the semiclassical (Anderson, phase-shift) cross-section for a scalar power
law potential V = C_n/R^n. For straight-line trajectories and n > 3, eq.
(4.16)-(4.17):

    sigma_n(v) = pi^(n/(n-1)) * (C_n/(hbar*v))^(2/(n-1))
                 * [Gamma{(n-1)/2}/Gamma(n/2)]^(2/(n-1))
                 * Gamma((n-3)/(n-1)) * cos(pi/(n-1))

with the broadening and shift rates given by velocity averages, eq. (4.18):
gamma = <N*sigma_R(v)*v>, beta = <N*sigma_I(v)*v>. For n=6 (van der Waals)
the exponents collapse to (C6/hbar)^0.4 and v^0.6, exactly the powers used
in rb5s6s/vanderwaals.py's beta_self_vdw. Table 4.1 gives the two systematic
results this predicts for n=6 directly: the width-to-shift ratio
2*gamma/beta = 2.75, and the temperature exponent alpha = (n-3)/(2(n-1)) =
0.300, i.e. gamma, beta proportional to T^0.3 (equivalently v^0.6). Both are
checkable, potential-independent signatures of the n=6 law. Evaluating
(4.17) itself at n=6 gives a cross-section prefactor of pi^1.2 *
[Gamma(5/2)/Gamma(3)]^0.4 * Gamma(3/5) * cos(pi/5) = 4.04 (this note's
arithmetic, not printed in the source, so treat it as a candidate check
rather than a quoted number).

**3. Where the name "Lindholm-Foley" in our code comes from.** Section 4.3.2,
on the van der Waals interaction for excited J=1 states with J=0 ground
states, states: "The Lindholm-Foley [70] approximation which replaces the
square bracket by exp(-i*Phi_i) leads to results which overestimate the
cross-sections by about 4%" relative to full numerical integration of the
coupled equations. Ref. [70] is H.M. Foley, Phys. Rev. 69 (1946) 616. This
confirms the name is real literature usage, not a code-local label, but it
is quoted here for a J=1 angular average that our 5S/6S pair does not have:
S-states carry no such tensor force to average over, so the plain scalar
eq. (4.15)-(4.17) is exact in this framework, without the 4% correction.
That 4% is nonetheless the only quantified error bound the review gives for
this family of quoted prefactors, and it is far smaller than the ~17% gap
between M18's corrected prediction and Zameroski's measured 7S rate (the
prior "1.67x" reading of that gap was a double-applied HWHM->FWHM conversion
in the code, traced and fixed 2026-08-03, docs/PREREGISTRATION_RESULTS.md
Addendum 23) -- so the review's own numbers still argue the J=1 angular
average is not the source of the residual gap, which is instead attributed
to the dropped core/tail and the mean-speed approximation.

**4. A second tradition for the same kind of coefficient.** Section 6.5, eq.
(6.2), gives Byron and Foley's second-order (non-resonant) dipole-dipole
self-depolarization cross-section for group-2b triplet levels (Hg 6-3P1,
Cd, Zn against their own ground-state vapor):

    sigma^(2) = 1.70 * { e^2*a0^4/((Delta E)*hbar*v_bar)
                * [n1*(n1*+1/2)(n1*+1)/z1*^2][n2*(n2*+1/2)(n2*+1)/z2*^2] }^(2/5)

built from Slater effective quantum numbers n* and charges z* rather than a
sum-over-states polarizability. It is the review's closest analogue to "a
non-resonant excited state self-broadened by its own ground-state vapor",
our exact problem class, just calibrated on Hg/Cd/Zn rather than an alkali,
and it reproduces the same 2/5 power as eq. (4.17). Table 6.4 shows it
matching measured Zn/Cd self-depolarization to about 15%.

## Measured coefficients worth quoting

Table 4.3 carries a genuine Rb-Rb resonance measurement: Gallagher and Lewis
[75] measured 87Rb(2P1/2,3/2-2S1/2) depolarization perturbed by 85Rb ground
atoms, K'(1;I=3/2) = 0.97 +/- 0.08 for the 2P1/2 channel and 1.11 +/- 0.06
for 2P3/2, against theoretical values of 0.911 and 0.959. That is resonance
theory holding to 5-15% for a real Rb-Rb collision, but it is a dimensionless
K' cross-section ratio in the review's own units, not a Hz cm^3 coefficient,
so it is not directly comparable to Weller's 0.69e-7 Hz cm^3 without redoing
the eq. (4.27) unit conversion, which this note has not attempted. Table 4.2
adds a potassium self-broadening measurement, Lewis, Rebbeck and Vaughan
[116], K'(1/2,1/2) = K'(1/2,3/2) = 1.3 +/- 0.3 for K(2P-2S) perturbed by K,
confirming the same resonance formula to about 25% in a different alkali.

No van der Waals-type nS-n'S alkali self-broadening coefficient appears
anywhere in this review. Tables 6.2 and 6.3 are alkali D-line broadening by
rare gases (Li through Cs, against He-Xe), a van der Waals mechanism but a
different, heteronuclear system (alkali 2P/ground vs. rare-gas 1S0) from
Rb(5S)-Rb(6S)-Rb(5S). Lewis 1980 does not fill the gap the M18 docstring
names. Zameroski's 7S rate remains the only measured nS self-broadening
coefficient for an alkali.

## BRIDGES

The exponents in `vanderwaals.beta_self_vdw`, (C6/hbar)^0.4 and v^0.6, are
exactly Lewis's eq. (4.15)-(4.18) scalar phase-shift result specialized to
n=6, the standard Anderson/Weisskopf impact-theory power law for a -C6/R^6
potential. Lewis gives the closed form, eq. (4.17), with an explicit
numerical cross-section prefactor for general n, and Table 4.1 prints two
n=6-specific, potential-independent checks (2*gamma/beta = 2.75, alpha =
0.300) that our own code does not currently verify against. Doing so would
be a clean, purely-formulaic test of `beta_self_vdw` that needs no new
physics input.

The review is also a direct textual confirmation, not just a physical
argument, that the resonance-broadening machinery in Tables 4.2/4.3 (and the
whole apparatus behind Weller's D1 anchor) requires a dipole-allowed
ground-excited transition and so cannot apply to 5S-6S. That strengthens
the "ceiling, not an estimate" reading of weller2011.md's upper anchor.

The Gallagher and Lewis Rb-Rb self-collision measurement (Table 4.3) is a
genuine same-review, same-atom cross-check available nowhere else in this
repository's literature file, but it measures a resonance depolarization
K' ratio, not a van der Waals broadening coefficient, so it bears on the
Weller upper anchor's plausibility rather than on the M18 vdW C6 anchor
itself. Converting it to a Hz cm^3 number via eq. (4.27) is left undone
here and flagged as a possible follow-up.
