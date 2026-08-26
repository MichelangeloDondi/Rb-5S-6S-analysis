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

Held. Read in full (71 pages).

## Scope

- A density-matrix derivation of the impact approximation for line width
  and shift (Sec. 2).
- Multipole and Lennard-Jones interatomic potential forms, with a note on
  how pseudopotential methods treat the core (Sec. 3).
- Semiclassical (phase-shift, Anderson-approximation) and full quantal
  partial-wave calculations of the collision S-matrix (Sec. 4).
- Experimental methods used to extract cross-sections: grating,
  Fabry-Perot, Hanle effect, level crossing, and magnetic resonance
  (Sec. 5).
- A comparison of theory against measurement in three families:
  - resonance and quasi-resonant broadening and depolarization of alkali
    and group-2b levels (Sec. 6.2)
  - alkali D-line broadening and shift by the rare gases (Sec. 6.3-6.4)
  - group-2b resonance lines broadened by rare gases and by their own
    vapor (Sec. 6.5)

Non-resonant broadening and depolarization in the rare gases is excluded,
already covered elsewhere (Sec. 6.1).

From the conclusion: "Our survey of the above data indicates clearly that
many calculated potentials are capable of reproducing magnitudes and
systematics of collision cross-sections with considerably greater
precision than long range series approximations." The paper's own
account of what it delivers, and does not, is reliable broadening
coefficients from good long-range potentials, not a probe of the inner
(overlap) potential except in fine-structure transfer.

## The van der Waals formula

Section 4.2 derives the semiclassical (Anderson, phase-shift)
cross-section for a scalar power-law potential $V = C_n/R^n$. For
straight-line trajectories and $n\gt 3$, eq. (4.16)-(4.17):

    sigma_n(v) = pi^(n/(n-1)) * (C_n/(hbar*v))^(2/(n-1))
                 * [Gamma{(n-1)/2}/Gamma(n/2)]^(2/(n-1))
                 * Gamma((n-3)/(n-1)) * cos(pi/(n-1))

with the broadening and shift rates given by velocity averages, eq.
(4.18): gamma = <N*sigma_R(v)*v>, beta = <N*sigma_I(v)*v>. For n=6 (van
der Waals) the exponents collapse to (C6/hbar)^0.4 and v^0.6, the powers
used in `vanderwaals.beta_self_vdw`. Table 4.1 gives two
potential-independent signatures of the n=6 law directly: the
width-to-shift ratio 2*gamma/beta = 2.75, and the temperature exponent
alpha = (n-3)/(2(n-1)) = 0.300, so gamma and beta scale as T^0.3
(equivalently v^0.6). Evaluating (4.17) at n=6 gives a cross-section
prefactor of pi^1.2 * [Gamma(5/2)/Gamma(3)]^0.4 * Gamma(3/5) * cos(pi/5)
= 4.04, an arithmetic result not printed in the source.

## Resonance dipole-dipole broadening

The paper's resonance-broadening apparatus starts from the first-order
dipole-dipole interaction, eq. (4.23):

    V(t) = -1/(4*pi*eps0*R^3(t)) * {3(d1.u)(d2.u) - d1.d2}

which is finite only "for the special case where the two systems are
identical only in different states which are connected by a dipole
transition" (Sec. 3.4). The resulting width formula, eq. (4.24),

    Dnu_1/2(Jg,Je;i) = K'(Jg,Je;i) * (1/pi) * sqrt[(2Jg+1)/(2Je+1)]
                        * e^2 * f_ge * N / (m*c^2*nu_eg)   [cm^-1]

carries the ground-to-excited oscillator strength $f_{ge}$ directly, with
K' close to unity for every case tabulated (Table 4.2). Since 5S-6S is an
S-S pair with no allowed dipole transition between the two states,
$f_{ge}=0$ for this channel, and the whole formula, together with every
K' constant in Tables 4.2 and 4.3, does not apply to a 5S-6S
self-broadening coefficient.

Table 4.3 carries a Rb-Rb resonance measurement: Gallagher and Lewis
measured $^{87}\text{Rb}$($2P_{1/2,3/2}$ to $2S_{1/2}$) depolarization perturbed by
$^{85}\text{Rb}$ ground atoms, K'(1; I=3/2) = 0.97 ± 0.08 for the 2P1/2 channel
and 1.11 ± 0.06 for 2P3/2, against theoretical values of 0.911 and 0.959,
resonance theory holding to 5-15% for a real Rb-Rb collision. It is a
dimensionless K' cross-section ratio and not a Hz cm^3 coefficient,
so it bears on the plausibility of a resonance-based ceiling rather than
being directly comparable to a van der Waals coefficient. Converting it
via eq. (4.27) has not been carried out. Table 4.2 adds a potassium
self-broadening measurement (Lewis, Rebbeck and Vaughan), K'(1/2,1/2) =
K'(1/2,3/2) = 1.3 ± 0.3 for K(2P-2S) perturbed by K, confirming the same
resonance formula to about 25% in a different alkali.

No van der Waals-type nS-n'S alkali self-broadening coefficient appears
anywhere in this source: Tables 6.2 and 6.3 cover alkali D-line
broadening by rare gases, a van der Waals mechanism but a different,
heteronuclear system (alkali 2P/ground vs. rare-gas 1S0) from
Rb(5S)-Rb(6S)-Rb(5S). Zameroski's 7S rate remains the only measured nS
self-broadening coefficient for an alkali.

## The Lindholm-Foley approximation

Section 4.3.2, on the van der Waals interaction for excited J=1 states
with J=0 ground states, states: "The Lindholm-Foley [70] approximation
which replaces the square bracket by exp(-i*Phi_i) leads to results
which overestimate the cross-sections by about 4%" relative to full
numerical integration of the coupled equations (ref. [70]: H.M. Foley,
Phys. Rev. 69 (1946) 616). This is a J=1 angular average that the 5S/6S
pair does not have: S-states carry no such tensor force to average over,
so the plain scalar eq. (4.15)-(4.17) is exact in this framework, without
the 4% correction. That 4% is the only quantified error bound the paper
gives for this family of prefactors.

## The Byron-Foley cross-section

Section 6.5, eq. (6.2), gives Byron and Foley's second-order
(non-resonant) dipole-dipole self-depolarization cross-section for
group-2b triplet levels (Hg 6 $^3P_1$, Cd, Zn against their own
ground-state vapor):

    sigma^(2) = 1.70 * { e^2*a0^4/((Delta E)*hbar*v_bar)
                * [n1*(n1*+1/2)(n1*+1)/z1*^2][n2*(n2*+1/2)(n2*+1)/z2*^2] }^(2/5)

built from Slater effective quantum numbers $n^*$ and charges $z^*$
rather than a sum-over-states polarizability. It is this paper's closest
analogue to a non-resonant excited state self-broadened by its own
ground-state vapor, calibrated on Hg/Cd/Zn and not on an alkali, and
reproduces the same 2/5 power as eq. (4.17). Table 6.4 shows it matching
measured Zn/Cd self-depolarization to about 15%.

## Use in this record

The exponents in `vanderwaals.beta_self_vdw`, $(C_6/\hbar)^{0.4}$ and
$v^{0.6}$, are this paper's eq. (4.15)-(4.18) scalar phase-shift result
specialized to n=6. Table 4.1's two n=6-specific, potential-independent
checks, $2\gamma/\beta = 2.75$ and $\alpha = 0.300$, are not currently
verified against the module's own output. The paper's dipole-dipole
resonance apparatus (Tables 4.2, 4.3) requires an allowed
ground-to-excited dipole transition and so does not apply to 5S-6S, a
textual confirmation that the D1 self-broadening coefficient in
[weller2011](weller2011.md) is a ceiling rather than an estimate for this
channel. The Gallagher and Lewis Rb-Rb self-collision measurement (Table
4.3) bears on the plausibility of that ceiling rather than on the
module's van der Waals C6 anchor, since it is a resonance depolarization
ratio and not a broadening coefficient. The 4% Lindholm-Foley
correction bound (Sec. 4.3.2) is much smaller than the roughly 17% gap
between the module's corrected prediction and Zameroski's measured 7S
self-broadening rate (see [zameroski2014](zameroski2014.md)), so that
residual gap is not explained by the angular-averaging correction.
