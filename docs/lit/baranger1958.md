---
citekey: baranger1958
type: article
authors:
  - Baranger, M.
title: General Impact Theory of Pressure Broadening
journal: Phys. Rev.
volume: 112
number: 3
pages: 855--865
year: 1958
doi: 10.1103/PhysRev.112.855
arxiv: null
pdf: PDF_papers/Baranger_1958_general-impact-theory-pressure-broadening.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-08-03
summary: >
  Full text read (Phys. Rev. 112, 855-865, 1958). Synthesizes Baranger's
  papers I (quantum-mechanical perturbers, elastic collisions only) and II
  (classical perturber paths, but inelastic collisions, degeneracy, and
  overlapping lines) into one general impact theory. When collisions are on
  average weak and well separated in time (Eqs. 41a/41b, equivalently the
  dilute-gas condition U << n^-1, Eq. 42, plus w, d << perturber kinetic
  energy, Eqs. 43a/43b), the line is Lorentzian, and for an isolated
  nondegenerate one-state line the width is w = (1/2) n v sigma via the
  optical theorem (Eq. 72c) -- explicitly linear in perturber density n. This
  is the specific result docs/methods/02_the_lineshape.md Sec. 2.2 invokes
  for gamma_coll = beta_self * N (the derivation now lives in
  docs/wiki/self-broadening.md), and it is also the n*v*sigma scaling
  rb5s6s/vanderwaals.py (M18) uses to turn a computed C6 into a predicted
  beta_self(6S). Baranger does not supply the C6-to-sigma step itself; that
  is the module's separately-flagged Lindholm-Foley prefactor.
loci:
  - THEORY
  - M4
  - M18
section: collision-series
---

# baranger1958

**Read in full from the held PDF (11 pp).**
Bibliographic metadata (title, journal, volume 112, number 3, pages 855-865,
November 1, 1958) all check out exactly against the printed masthead. The body
text below was originally written from a
secondary-source paraphrase, and it undersold the paper in one place, flagged
below.

## Abstract (verbatim)

"The work of two previous papers is extended and a theory of pressure
broadening is developed which treats the perturbers quantum mechanically and
allows for inelastic collisions, degeneracy, and overlapping lines. The
impact approximation is used. It consists in assuming that it takes, on the
average, many collisions to produce an appreciable disturbance in the wave
function of the atom, and it results in an isolated line having a Lorentz
shape. Validity criteria are given. When the approximation is valid, it is
allowable to replace the exact, fluctuating interaction of the perturbers
with the atom by a constant effective interaction. The effective interaction
is expressed in terms of the one-perturber quantum mechanical transition
amplitudes on and near the energy shell and its close relationship to the
scattering matrix is stressed. The calculation of the line shape in terms of
the effective interaction is the same as when the perturbers move on
classical paths. Results are written explicitly for isolated lines. If the
interaction of the perturbers with the final state can be neglected, the
shift and width are proportional to the real and imaginary part of the
forward elastic scattering amplitude, respectively. By the optical theorem,
the width can also be written in terms of the total cross section. When the
interaction in the final state cannot be neglected, the shift and width are
still given in terms of the elastic scattering amplitudes, in a slightly more
complicated fashion. Finally, rules are given for taking into account
rotational degeneracy of the radiating states."

## What it actually establishes

This is paper III of a series (I: Phys. Rev. 111, 481 (1958); II: Phys. Rev.
111, 494 (1958)). Paper I treated perturbers quantum mechanically but only
for elastic collisions on a nondegenerate atom. Paper II allowed inelastic
collisions, degeneracy, and overlapping lines, but moved the perturbers on
classical paths. This paper is the synthesis: quantum-mechanical perturbers
plus inelastic collisions, degeneracy, and overlapping lines together, needed
for a consistent theory of electron broadening (stated explicitly in the
introduction), but the machinery is general and not restricted to electrons.

The central formal step: when the impact approximation holds, the exact,
fluctuating atom-perturber interaction can be replaced by a constant,
non-Hermitian effective interaction, $\mathfrak{K} = nR_{Nu}$ (Eqs. 37-38),
built from the near-energy-shell one-perturber transition operator $R$,
averaged over the Boltzmann-weighted perturber velocity distribution and
scaled by the perturber density $n$. Once $\mathfrak{K}$ is known, the line
shape follows exactly as in the classical-path theory of paper II (Eq. 69).

For an **isolated, nondegenerate line, one-state case** (only the initial
atomic state interacts with the perturbers, i.e. the final state's
interaction is neglected), the shift and width are the real part and minus
the imaginary part of the diagonal element of $\mathfrak{K}$ (Eqs. 70a-b),
which reduce to the real and imaginary parts of the **forward elastic
scattering amplitude** $f(0)$ (Eqs. 71-72b), and, by the optical theorem, to

$$w = \left(\tfrac{1}{2}nv\sigma\right)_{Nu}$$

(Eq. 72c), the thermal (Boltzmann-)average over the total (elastic +
inelastic) cross section $\sigma$ and relative speed $v$ -- **explicitly
linear in the perturber density $n$**, since $n$ is a bare prefactor, not a
fit.

For the **two-state case** (both initial and final atomic states interact,
i.e. inelastic/state-changing collisions are allowed), the width is richer
than pure elastic dephasing (Eq. 77c):

$$w = \left\lbrace \tfrac12 nv\Big[\sigma_{i,\text{in}}+\sigma_{f,\text{in}}
 +\int d\Omega |f_i(\Omega)-f_f(\Omega)|^2\Big]\right \rbrace_{Nu}$$

i.e. the inelastic cross sections of *both* states add to the width directly
(they cannot be expected to add coherently with the elastic scattering), and
the elastic contribution enters not as a total cross section but as the
integral of the squared *difference* of the initial- and final-state elastic
amplitudes. This is the fully quantum generalization of "phase-interrupting
collisions add a rate to the coherence decay" -- correct as a description of
the pure-dephasing (one-state, elastic-only) limit, but the paper's actual
general result also lets genuinely inelastic, state-changing collisions
contribute to the width, on top of dephasing. The note's previous wording
implied phase interruption was the whole mechanism; it is the leading piece
of a more general formula.

## Validity conditions (Sec. 2)

Defining the collision time $\tau$ (via the "collision volume" $U=\tfrac12 v\sigma\tau$,
Eqs. 19-20 -- the time/volume over which a perturber's
wavefunction differs appreciably from a free plane wave), the impact
approximation requires

$$w\tau\ll1\ \ (41\mathrm{a}), \qquad d\tau\ll1\ \ (41\mathrm{b})$$

"Those are the same conditions we had in II." Condition (41a) is equivalent,
via (72c), to

$$U\ll n^{-1}\ \ (42)$$

"the same condition we had in I": the dilute-gas / binary-collision
condition, collision volume much smaller than volume per perturber.
Condition (41b) has **no analog in paper I**, because paper I's simplified
additive-force model made it automatic; here it must be imposed separately.
The paper is explicit that **the Lorentz shape itself needs only (41a)**;
(41b) is needed in addition for the effective interaction to reduce to the
simple near-shell scattering-amplitude formulas used above (otherwise "things
are more complicated," a case the paper does not pursue because it is rare
in practice).

Because $\tau$ can never be smaller than $\epsilon^{-1}$ ($\epsilon$ the
kinetic energy of a perturber, elastic or inelastically scattered), (41)
implies

$$w\ll\epsilon\ \ (43\mathrm{a}), \qquad d\ll\epsilon\ \ (43\mathrm{b})$$

width and shift must be small compared to the perturbers' own kinetic
energy. The paper also notes that when (41a) holds, the Boltzmann population
factor varies negligibly across the width of a line, so no correction for
finite-temperature population smearing is ever needed inside the impact
approximation -- a companion point to using $N(T)$ as a fixed input rather
than something the lineshape itself must correct for.

## Bridges to this repo

**What the repo's chain actually rests on.** `docs/methods/02_the_lineshape.md`
Sec. 2.2 and `docs/wiki/self-broadening.md`, which carries the derivation,
cite Baranger for $\gamma_\text{coll}=\beta_\text{self}N$: a
Lorentzian collisional term whose width grows linearly with density. That is
precisely the one-state, isolated-line result above, $w=(1/2)nv\sigma$ (Eq.
72c) -- not a generic textbook approximation but this paper's Eq. (72c)
itself, with $n$ the Rb density from `rb5s6s/density.py`. The same scaling,
$w\propto n v \sigma$, is exactly what `rb5s6s/vanderwaals.py` (M18) uses in
`beta_self_vdw` to turn a computed $C_6$ into a predicted broadening rate: the
function multiplies a cross-section-like quantity by $n$ and $v^{0.6}$ and
calls the LINDHOLM_FOLEY_PREFACTOR-scaled result a width, which is Baranger's
$w=(1/2)nv\sigma$ with $\sigma$ replaced by its van der Waals form.

**What Baranger does not supply.** The paper is explicit that computing the
scattering amplitudes/cross sections for any specific potential is "outside
the scope of pressure broadening" (Sec. 1) -- it hands back a general relation
between $w$ and $\sigma$, not $\sigma$ itself. The step from a $-C_6/R^6$
potential to a cross section is a separate, later semiclassical result (the
Lindholm-Foley impact formula), which `rb5s6s/vanderwaals.py`'s own docstring
flags as "quoted from the pressure-broadening literature, not derived." A
double-applied HWHM->FWHM conversion in `beta_self_vdw` (a code bug, traced
and fixed 2026-08-03, docs/PREREGISTRATION_RESULTS.md Addendum 23) had been
misread as a 1.7x over-prediction on the one state with a measured
self-broadening rate (7S, Zameroski 2014; see `docs/lit/zameroski2014.md`);
corrected, the module sits ~17% low against that measurement, inside the
envelope the valence-only truncation already predicts. `beta_self_anchored`
still cancels the quoted (not derived) prefactor in a $C_6(6S)/C_6(7S)$
ratio rather than trust the absolute value, independent of this fix.

**Validity check for our regime.** The vapour-cell density runs from about
$5.6\times10^{11} \text{cm}^{-3}$ at 70 C to about $2.9\times10^{13} \text{cm}^{-3}$
at 130 C (`rb5s6s/density.py`, Nesmeyanov/Steck), i.e. of
order $10^{13} \text{cm}^{-3}$ at the top of the sweep. Checking Baranger's
conditions there (worst case, 130 C, where the margins are smallest):

- **Dilute-gas condition (41a)/(42).** The mean interatomic spacing is
  $n^{-1/3}\approx326 \text{nm}$. The van der Waals interaction radius (where
  the collision phase becomes order unity, $\rho_W=(C_6/\hbar v)^{1/5}$, using
  $C_6(5S{+}6S)\approx2.9\times10^4 \text{a.u.}$ from M18) is
  $\rho_W\approx2.3 \text{nm}$. Spacing exceeds the interaction radius by a
  factor of $\sim140$ (a volume ratio of $\sim10^6$): well inside the
  binary-collision regime at every temperature in the sweep (the ratio only
  grows at lower $T$, where the density is smaller).
- **Energy condition (43a)/(43b).** $kT/h\approx8.4 \text{THz}$ at 130 C,
  versus widths of order kHz-MHz ($\beta_\text{self}$ itself and the archival
  bound alike): a margin of $10^7$ to $10^9$.

Both conditions hold by many orders of magnitude across the full 70-130 C
sweep, so the impact approximation's own validity is not in question for
this system, at any density this campaign reaches. What remains open is not
Baranger's theorem but the Lindholm-Foley $C_6\to\sigma$ conversion layered on
top of it in M18 -- consistent with the archival bound sitting 8-15x above the
$C_6$-anchored expectation (`docs/lit/zameroski2014.md`): a gap in an
unverified prefactor and a still-non-constraining bound, not a violation of
anything Baranger proved.
