---
citekey: patterson2018
type: article
authors:
  - Patterson, B. D.
  - Solano, P.
  - Julienne, P. S.
  - Orozco, L. A.
  - Rolston, S. L.
title: 'Spectral asymmetry of atoms in the van der Waals potential of an optical nanofiber'
journal: Phys. Rev. A
volume: 97
pages: 032509
year: 2018
doi: 10.1103/PhysRevA.97.032509
arxiv: '1801.01585'
pdf: PDF_papers/Patterson_2018_ONF-vdW-spectral-asymmetry-Rb.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags:
  - 'Held as arXiv v1 (1801.01585, 4 January 2018). The journal fields are the
    published PRA reference as given by the citing paper sadeghi2026 and should
    be confirmed against the published article before formal citation; the arXiv
    record carries no journal-ref.'
verified_date: 2026-07-30
summary: >
  The direct precedent for Paper 2: an ASYMMETRIC lineshape produced by a
  spatially distributed level shift in an optical-nanofibre geometry, quantified
  and fitted. Cold Rb-87 around a 240 nm ONF; the van der Waals surface
  potential U = -C3/r^3 red-shifts atoms nearer the silica, and the transmission
  spectrum is modelled as a Lorentzian of position-dependent centre averaged
  over a density times coupling weight -- structurally the same construction as
  this programme's shift-distribution convolution, with a static surface
  potential in place of the AC-Stark shift. Reports an integral asymmetry
  parameter A = (L-R)/(L+R) rising to 0.36 and back down as the desorption laser
  is powered, and an UNEXPLAINED ~2 MHz of excess width (their Gamma_0 = 8.1(3)
  MHz is the total homogeneous width; the Rb D2 natural 6.065 MHz is supplied
  here, not by them) after Doppler, collective, Purcell, continuum-atom and
  Zeeman explanations are each excluded.
loci:
  - P2
  - THEORY
section: oist-lineage
---

# patterson2018

**Read 2026-07-30** from the held arXiv v1. Joint Quantum Institute (Maryland /
NIST). Surfaced the previous day as ref [25] of
[sadeghi2026](sadeghi2026.md); the PDF was supplied by the experimenter.

## The system

A ⁸⁷Rb MOT (~10⁸ atoms, few hundred µK) overlapping an optical nanofibre of
diameter **240 ± 20 nm**. A weak near-resonant 780 nm probe is launched *through
the guided mode* and its transmission recorded across the
5S₁∕₂ F=2 → 5P₃∕₂ F′=3 line; a far-off-resonance **750 nm laser in the same
guided mode heats the fibre**, thermally exciting physisorbed atoms into van der
Waals bound states. Probe intensity is held below a tenth of saturation so there
is no power broadening.

## The construction, which is the reason this note matters

The surface potential is $U(r) = -C_3/r^3$, with
$C_3 = 4.94 \times 10^{-49}$ J·m³ for 5S₁∕₂ and $7.05 \times 10^{-49}$ for
5P₃∕₂ — larger for the excited state, so the shift is **red**. Their spectrum is
then (their Eqs. 8–9)

$$P_{\rm abs}(\omega) = \int r {\rm d}r ~ p_{\rm abs}(r,\omega) ~ \rho_{\rm tot}(r) ~ \alpha(r),$$

where $p_{\rm abs}$ is a Lorentzian whose detuning is
$\delta_{\rm vdW}(r) + \delta_L$, $\rho_{\rm tot}(r)$ is the atomic density and
$\alpha(r) \propto I(r)$ is the emission-enhancement weight. In words: a
homogeneous Lorentzian, convolved with a **signal-weighted distribution of level
shifts**. That is this repository's method, in another laboratory, on another
mechanism. They even name the regime — the atoms in high bound states move
slowly enough to use "the quasistatic theory of line broadening", so — their
words exactly — "the spectrum is given only by the local potential felt by the
atoms". *This note first rendered that quotation with "local frequency shift"
in place of "local potential"; the phrase "frequency shift" appears nowhere in
the paper.* The correction matters rather than being pedantry, because for them
the local potential is van der Waals and its conversion to a frequency shift is
a separate step (their $\delta_{\rm vdW} = (U_e - U_g)/\hbar$), whereas in the
AC-Stark case the potential and the shift are the same object up to a constant.
With that repaired, the sentence is still the assumption
[THEORY_NOTE](../THEORY_NOTE.md) §2 makes, and it is still rare to be able to
cite it from a measurement.

Their density model is worth recording separately because it is not ours:
$\rho(r) \propto 1/(1 - U(r)/E)$ with $E = k_BT/2$ (atoms *accelerate* into the
surface, so the density there **falls**), plus a bound-state term
$u_0 r^{-3/2}$, the exponent following from the $r^{-3}$ potential.

## The numbers

| heating power (µW) | $\Gamma_0/2\pi$ (MHz) | $u_0$ | $A$ | $\chi^2_r$ |
|---|---|---|---|---|
| 0 | 8.1 ± 0.3 | 0 (fixed) | 0.14 | 1.11 |
| 40 | 8.1 (fixed) | 0.19 ± 0.09 | 0.19 | 1.16 |
| 120 | 9.2 ± 1.0 | 7182 ± 269 | 0.36 | 1.91 |
| 250 | 8.4 ± 0.9 | 5897 ± 612 | 0.26 | 1.32 |
| 350 | 9.5 ± 2.4 | 0.11 ± 0.11 | 0.12 | 1.29 |

The MOT-only spectrum has FWHM **8.9 ± 0.2 MHz** and "very little asymmetry".

**The asymmetry parameter** is $A = (L-R)/(L+R)$, with $L$ and $R$ the absorption
integrated red and blue of centre (their Eq. 11) — zero for a symmetric line,
strictly positive here because van der Waals shifts red.

**The power dependence is non-monotonic** — in the **heating** beam, the 750 nm
desorption laser scanned 0–350 µW, peaking near 120 µW. The probe is a separate
laser held below a tenth of saturation and **never scanned**, so nothing here is
a probe-power dependence. Their explanation
is thermal, not spectroscopic: too cold and atoms cannot climb into the high
bound states, too hot and they are desorbed and fly away, so an intermediate
nanofibre temperature maximises the bound population. They also note the
blue-detuned heating beam's own repulsive dipole potential limits how many atoms
reach the surface, giving $N \propto 1 - {\rm Erf}[b_o\sqrt{P}]$ with
$T \propto P^{1/g}$. They report **two distinct fits**, which this note first
collapsed into one: the primary fit holds $b_o$ at its calculated 0.142 and frees
only an amplitude and the exponent, giving $g = 2.26 \pm 0.05$; a second fit
frees $b_o$ as well and gives $b_o = 0.156 \pm 0.019$ with
$g = 2.15 \pm 0.136$, which they note is consistent within errors. The
expectation is $g < 3$.

## The concession Paper 2 must make

`LITERATURE.md` §5 already concedes that asymmetric lineshapes from a distributed
AC-Stark shift are not new, on the strength of [wieman1987](wieman1987.md). This
paper forces the *same* concession one step closer to home: **asymmetry from a
distributed potential, in an optical nanofibre, quantified by an explicit
parameter and fitted with a shift-distribution convolution, is done.** And unlike
[antypas2018](antypas2018.md) — whose title is asymmetry *elimination* — Patterson
*use* the asymmetry as an information channel about the spatial distribution,
which is exactly this programme's stance. That similarity should be stated
plainly rather than discovered by a referee.

## Where it differs, and the difference is real

1. **The shift is not made of the light.** Van der Waals is a *static* property
   of the dielectric: the weight $\alpha(r) \propto I(r)$ and the shift
   $\delta_{\rm vdW}(r) \propto r^{-3}$ are independent functions that merely
   share a coordinate. In the AC-Stark case the shift **is** proportional to the
   intensity that weights the excitation, and that self-consistency is what
   collapses the whole geometry into the closed form
   $f(s) \propto |s|^{n-1}$ with its analytic cumulants. Patterson have no such
   reduction and integrate numerically. This is the sharpest available statement
   of what the closed form is worth.
2. **Two different power knobs, and the discrimination is an inference not a
   measurement.** Their asymmetry rises and falls with *heating* power through a
   thermal population; an AC-Stark asymmetry would grow with *probe* power
   because the shift itself scales with intensity. **Patterson never scan probe
   power at all**, so the two behaviours have never been put head to head. The
   argument is structural rather than empirical: a static van der Waals shift is
   independent of probe intensity by construction, so a monotone rise of
   asymmetry with probe power cannot be the van der Waals mechanism. That makes
   it a **discriminating signature for Paper 2 to measure** — not a result to
   cite. Stating it as though Patterson had measured it would be the same class
   of error as running their two power axes together.
3. **One photon, cold atoms.** 5S→5P at 330 µK: $n = 1$, transit time
   irrelevant, no Doppler pedestal. Ours is $n = 2$ in a hot cell where transit
   through $w_0$ is the dominant systematic.

## The thing to take from it, which may be worth more than the citation

**Patterson report an excess width they cannot explain, and say so.** Their
$\Gamma_0 = 8.1 \pm 0.3$ MHz (Table I, 0 µW) is the *total* homogeneous width in
their model, and they write that they "consistently measure a 2 MHz increase from
the natural linewidth which we do not yet understand" — the ⁸⁷Rb D2 natural width
being 6.065 MHz, a number supplied here and **not** stated anywhere in their
paper. They exclude, one at a time: Doppler (would need 72 mK against a measured
few hundred µK), collective/superradiant enhancement (linear in atom number, and
varying the MOT density does not move the width), Purcell modification (measured
at ~10% for similar distributions, though they note Sagué saw ~20% in Cs),
continuum hot atoms (hundreds of MHz, so a broadband background), and Zeeman
broadening (no response to the MOT coils). The probe is below a tenth of
saturation, so it is not power broadening either.

Sagué *et al.* (2007, their ref [8]) is the one comparable case: 6.2 MHz in Cs
where 5.2 is natural, i.e. **~1 MHz**, likewise unaccounted for. Two experiments,
eleven years apart, ~1–2 MHz each.

**A third case that this note first mis-stated, and which is a contrast rather
than a confirmation.** [sadeghi2026](sadeghi2026.md) fit
$W(s_0) = \Gamma\sqrt{s_0+1} + \Gamma_0$ with $\Gamma = 6.45 \pm 1.17$ MHz and
$\Gamma_0 = 8.44 \pm 0.80$ MHz. **Their $\Gamma_0$ is an additive excess, not a
total width**, so setting it against 5.2 MHz — as this note originally did — is a
category error: at their $s_0 = 0.4$ the formula gives
$6.45\sqrt{1.4} + 8.44 = 16.1$ MHz, reproducing the ~16 MHz width they quote and
confirming the reading. Their unexplained-plus-attributed surplus over natural is
therefore of order **10 MHz**, four to five times Patterson's, and they *do*
attribute it (surface interactions, magnetic gradients, laser linewidth) rather
than leaving it open. The near-equality of Patterson's 8.1 and Sadeghi's 8.44 is
a coincidence of notation between two different quantities.

So the defensible statement is narrower than "three experiments agree": **two ONF
experiments report ~1–2 MHz of genuinely unexplained width, and a third reports a
much larger surplus that it does attribute.** Whether the small unexplained
residual and the large attributed one are the same physics at different scales is
**OPEN** — this repository has not checked them against a common model, and doing
so is the work, not the observation. It remains a better premise for Paper 2 than
"we measure a lineshape in an ONF too".

**A second, smaller borrowing.** Their probe scan runs red→blue then blue→red
within one cycle, explicitly "to rule out transient effects such as increase or
decrease of the average number of atoms". That is the same diagnostic as this
campaign's triangular sweep and its retrace, arrived at independently — a
citable precedent for a test the pipeline already runs rather than a new idea.

**Also worth adopting: their asymmetry statistic.** $A = (L-R)/(L+R)$ is an
*integral* measure — no third moment, no cubic tail weighting — so it is far more
robust to the wings than the skewness $g_1$ this programme reports, at the cost
of having no closed-form prediction attached. Computing $A$ alongside $g_1$ on
the campaign lines would put a number in the same units as a published one.
Deliberately **not** done yet: it is a new statistic on data whose absolute
frame is still `BOUND` on the open $w_0$, and it should be pre-registered before
it is computed, not added to a results table after the fact.
