---
citekey: delone1980
type: article
authors:
  - Delone, N. B.
  - Kovarskii, V. A.
  - Masalov, A. V.
  - Perel'man, N. F.
title: 'An atom in the radiation field of a multifrequency laser'
journal: Sov. Phys. Usp.
volume: 23
pages: 472
year: 1980
doi: 10.1070/PU1980v023n08ABEH005024
arxiv: null
pdf: PDF_papers/Delone_1980_atom-in-multifrequency-laser-field-review.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'The held file is the English translation in Sov. Phys. Usp. 23(8), Aug 1980.
    Its OCR text layer is poor -- equations and
    Greek are mangled -- so everything below was read from the RENDERED pages,
    not from text extraction, and equation numbers are as printed on the page.'
  - 'The DOI above is the standard IOP record for this article and was NOT
    verified against Crossref. Author order is as printed on the article.'
verified_date: 2026-07-30
summary: >
  THE origin of this programme's theoretical frame, and it is a 1980 REVIEW,
  meaning the frame was already established then. Their Eq. (4.5) states that
  the absorption lineshape IS the intensity distribution rescaled by the
  polarizability, K(Omega) ~ P(-(omega_n1 - Omega)/(alpha_1f hbar)); their
  Eq. (5.2) writes the multiphoton rate as a shifted Lorentzian integrated over
  P(F) with an F^k intensity weight; and their Eq. (5.3) gives the
  shift-dominated limit as (detuning)^k P(detuning/alpha), described as "an
  asymmetrically broadened line" from which "in principle one can reconstruct
  the distribution P(F)". Lineshape-as-a-map, the k-photon weighting, the
  asymmetry, and the inverse problem are all there. What is NOT there is a
  GEOMETRIC distribution: their P(F) is the statistics of a fluctuating field,
  unknown a priori, where this programme's is set by the beam profile and
  therefore closes in form with analytic cumulants.
loci:
  - THEORY
  - P1
section: prior-art
---

# delone1980

**Read from the rendered pages of the held translation**, after
[camparo1992](camparo1992.md) was found to attribute the
lineshape-mapping idea to it. It overlaps this programme's construction more
than that attribution suggested.

**A gap this note has to declare.** <!-- not-from-pdf: OCR text layer is
unusable; all quotations here were transcribed by eye from the rendered pages. -->
`tests/test_lit_quotes_are_verbatim.py` cannot guard this note. Its text layer
is mangled — equations come out as noise like `Ρ (F) =-^ exp ( --j£-)`, and
"line shape", "Stark shift" and "map" all return **zero** hits on a paper that
plainly discusses all three. Every quotation below was therefore transcribed **by
eye from the rendered pages**, which is exactly the situation the machine check
exists to cover and cannot. Treat the transcriptions here as a grade below the
machine-verified ones elsewhere, and re-check them against the page images before
any of them reaches a manuscript.

## What it actually contains

**§4b, nonresonance perturbation, narrow spectrum.** Their Eq. (4.5):

$$K(\Omega) \sim P\left(-\frac{\omega_{n1}-\Omega}{\alpha_{1f}\hbar}\right), \qquad \frac{\Omega-\omega_{n1}}{\alpha_{1f}\hbar} \gt 0$$

with the text: "Just as in the case of resonance perturbation, the shape of the
line reflects the set of positions of the atomic level that are realized in the
ensemble of random values of the radiation intensity. It can be obtained by
averaging the shape of the line in a monochromatic field over the distribution
$P(F)$." For a level shift linear in intensity and a negligibly narrow
unperturbed line, **the lineshape simply *is* the intensity distribution,
rescaled by the polarizability**.

**The inverse problem, stated outright.** "The treatment that we have carried out
above of perturbation of atomic levels in a nonmonochromatic field allows the
general conclusion that one can **reconstruct the properties of the radiation
from perturbation data** in the narrow-spectrum case: in the resonance case one
can reconstruct the field amplitude distribution $\mathcal{P}(A)$, and the
intensity distribution $P(F)$ in the nonresonance case."

**§5, multiphoton excitation.** Their Eq. (5.2):

$$W \sim \int_0^{\infty} P(F)  F^{k}  \frac{\Gamma(F)}{[\omega_f - k\omega_0 + \delta\omega(F)]^2 + [\Gamma(F)]^2}  {\rm d}F$$

A Lorentzian whose centre is displaced by a shift $\delta\omega(F)$, integrated
over the distribution of $F$, **weighted by $F^{k}$ for a $k$-photon
transition**. And the shift-dominated limit $\delta\omega(F) \gg \Gamma(F)$,
their Eq. (5.3):

$$W \sim (\omega_f - k\omega_0)^{k}  P\left(\frac{\omega_f - k\omega_0}{\alpha_{1f}\hbar}\right)$$

described as amounting "to an **asymmetrically broadened line**", and again: "In
principle one can reconstruct the distribution $P(F)$ from this relationship."

## What this costs

Four things this repository has treated as its own frame are in a 1980 review,
which means they were established before it:

1. **The lineshape maps the distribution of AC-Stark shifts** — Eq. (4.5).
2. **The multiphoton construction**: a shifted Lorentzian integrated over the
   shift distribution with an $F^{k}$ weight for a $k$-photon transition —
   Eq. (5.2). This is structurally the same object as `THEORY_NOTE` §2's
   signal-weighted average, with $k$ playing the role of $n$.
3. **The shift-dominated limit is an asymmetric line** whose shape carries the
   distribution — Eq. (5.3).
4. **The inverse problem** — reading the distribution off the lineshape — stated
   twice, explicitly, as the point of the exercise.

The concession in `LITERATURE.md` §5 must therefore run to 1980, not to
`camparo1992` (1992) and not to `wieman1987`. Camparo's "the multiphoton
transition line shape may be expected to act as a map of the probability
distribution of Stark shifts" cites this, correctly, and is a restatement.

## What survives, and it is narrower but real

**Their $P(F)$ is a *statistical* distribution; ours is a *geometric* one.** In
Delone the spread of $F$ comes from the temporal fluctuations of a
multimode or chaotic laser — $P(F)$ is a property of the light source, generally
exponential for thermal light, and *not known a priori*. That is why their
results stay at the level of "one can reconstruct $P(F)$": the distribution is
the unknown being measured.

In this programme the spread comes from the **transverse intensity profile of a
coherent beam**. $P$ is therefore fixed by geometry rather than by laser
statistics, and that is what converts Eq. (5.2) from a formal integral into a
closed form: $f(s) \propto |s|^{ n-1}$ on a bounded support $[-S_0, 0]$,
triangular at $n = 2$, with **analytic cumulants** — an intrinsic skew
$g_1 = +0.566$ that is a number, not a fit. Delone cannot write that, because
they do not know their $P$.

So the defensible claim is not the machinery and not the mapping. It is:

- the **closed form and its cumulants** for the focused-Gaussian, retro-reflected,
  fringe-averaged two-photon geometry, and its $|s|^{n-1}$ generalisation;
- the use of a **specific cumulant as a drift-immune measurement channel** —
  reading $S_0$ from the third moment precisely because the centre is not
  trustworthy, which is a response to an experimental problem Delone does not
  have;
- everything experimental, and the fringe-averaging result (M19).

**The introduction here should cite this paper early and concede all four
points above explicitly.** The overlap is on the public record in the Soviet
nonlinear-optics literature, and the claim as previously worded does not survive
it.

## The change of variable, carried out — and it is exact

The question flagged on first reading was whether Delone's $F^{k}$ weight and
this programme's $I^{n}$ weight are the same thing. **They are, and the two
closed forms are the same equation.** Their §5 defines $k$ as "the number of
photons absorbed in the transition", identical to $n$. Carrying out the
substitution (CALCULATED 2026-07-30):

**Step 1 — the geometric distribution.** For atoms distributed uniformly in
space across a Gaussian transverse profile $I(r) = I_0 e^{-2r^2/w^2}$, the
area measure gives $2\pi r {\rm d}r \propto {\rm d}I/I$, so the
intensity distribution is $P(I) \propto 1/I$. Verified numerically: binning
$I$ over four decades with a $2\pi r$ weight, the product $P(I)\cdot I$ is
constant to **1 part in $10^4$**.

**Step 2 — substitute into their Eq. (5.3).** $W(s) \propto s^{k} P(s/\alpha\hbar)$
with $P \propto 1/s$ gives

$$W(s) \propto s^{k} \cdot s^{-1} = s^{ k-1}$$

which is $f(s) \propto |s|^{ n-1}$ — this repository's law, with $k = n$.

**Step 3 — check against the shipped code.** At $n = 2$, Delone's Eq. (5.3) with
the geometric $P$ agrees with `rb5s6s.lineshape.stark_ramp` to a maximum
absolute difference of $7 \times 10^{-12}$ on the normalised profile. They are
the same function.

**So the concession is as tight as it can be.** This repository's closed form is
Delone's Eq. (5.3) evaluated for the intensity distribution of a focused Gaussian
beam. That must be said in the introduction here in those words.

**The distribution-from-profile idea has independent roots outside atomic
physics too, and the modern general inverse framework is now held.** A. Efimov
and V. Khitrov, "Analytical formulas for describing the dispersion of glass
with refractive indices that observe the continuous nature of absorption,"
*Fiz. Khim. Stekla*, vol. 5, no. 5, pp. 583-588, 1979, made an early attempt at
treating inhomogeneous broadening as a probability distribution over a
lineshape's parameters. A second, independent root sits thirteen years later:
R. Brendel and D. Bormann, "An infrared dielectric function model for
amorphous solids," *J. Appl. Phys.*, vol. 71, no. 1, pp. 1-6, 1992, postulated
the same convolution integral for amorphous-solid infrared spectra, though its
closed form later turns out to be noncausal. [prokopeva2025](prokopeva2025.md)
picks both up and extends them well past atomic spectroscopy: a causal,
Kramers-Kronig-consistent framework that recovers the intrinsic homogeneous
linewidth and the inhomogeneous disorder distribution together from a
measured lineshape, correcting the Brendel-Bormann noncausality along the
way, for dielectric-function models in nanophotonic materials (Gauss-Lorentz,
Gauss-Debye, Gauss-Drude).

**A candidate for this family, read and rejected.**
[lahad2019](lahad2019.md), Phys. Rev. Lett. 123, 173203 (2019), looked like a
further cousin on the strength of its title,
"Recovering the Homogeneous Absorption of Inhomogeneous Media." A full
reading shows the opposite. Its spread parameter delta is a Doppler shift
whose width is taken as GIVEN from the temperature, never extracted from a
lineshape, and its measured observable is a single enhancement ratio
compared against a closed form model, not a reconstructed distribution. The
paper cancels the spread with a second, correlated light-shift field rather
than reading it, and its own introduction places the mechanism beside
Cohen-Tannoudji's 1978 Doppler-compensation proposal, not beside an inverse
problem. It is not a member of this family. The full account is in its own
note.

**What that leaves, stated precisely.** Delone give the general relation and
treat $P$ as the *unknown to be reconstructed* — their whole point is that the
lineshape measures the laser's statistics. This programme runs it the other way:
$P$ is **known from the geometry**, so the integral evaluates, and the result has
**analytic cumulants** — an intrinsic $g_1 = +0.566$ at $n=2$ on a bounded
support $[-S_0,0]$, which is a number rather than a fit. Delone cannot write that
number, because in their setting it is precisely what is not known. The
contributions that survive are therefore: evaluating a known general result for
the geometry that actually occurs; computing its cumulants in closed form; and
using the **third** cumulant as a drift-immune measurement channel, which
answers an experimental problem (an untrustworthy frequency centre) that does
not arise in Delone's setting at all. That is a real contribution and a much
smaller one than "a new lineshape law".

## Sections 3, 5 and 6c: what this note had not read, and why they matter

Added 2026-08-09, prompted by asking what a *third* 993 nm photon does in this
experiment. The answer turned out to be partly printed in this same review, in
sections the note had not reached. This is a reading gap rather than a
literature gap, which is the worse kind to leave open: the paper is held, cited
and marked VERIFIED, so anything in it is already ours to be responsible for.

**The frame has a stated validity condition, and the note did not carry it.**
Section 5 bounds the whole $F^k$ power-law picture: it holds if the
field-induced shifts and widths of the atomic levels are *smaller than the
natural widths*. In the opposite case, $\delta\omega(F)$ and $\Gamma(F)$ larger
than $\Gamma$, the induced shift and width govern the process and it is
explicitly **not of power-law type**. Section 3 closes with three named exits
from the frame: tunnelling character, intermediate resonances arising, and the
inapplicability of a rate description at long pulse duration.

This bears directly on the archive rather than only on the theory. At the
adopted waist the ramp edge is 0.348 MHz against a 3.4925 MHz natural width, so
the condition holds with about a factor of ten to spare, and the power-law frame
is licensed. It would stop being licensed at the tighter focus the fixed-lock
plan wants, which is the same place two other approximations already fail, and
it should be checked there rather than assumed.

**Equation (5.3) carries three conditions and this note quoted one.** Alongside
$\delta\omega(F) \gg \Gamma(F)$, which the note had, the printed conditions are
that resonance with the *shifted* level be realised, sign condition
$(\omega_f - k\omega_0)/(\alpha_{1f}\hbar) \gt 0$, and that
$|\omega_f - k\omega_0| \gg \Gamma(F)$. The reduction of this repository's
$f(s)\propto|s|^{n-1}$ to Eq. (5.3) is unaffected, because that reduction is an
identity between two closed forms and does not depend on which regime either is
used in.

**Section 6c is the resonance-enhanced multiphoton problem, written out.** It
treats $k = k_1 + k_2$ with a real intermediate resonance, which is exactly the
2+1 process a third 993 nm photon would drive from the real 6S population, and
it names all three field-induced perturbations of the resonant state with their
intensity scalings: a field width from the mixing of ground and resonant states,
$\Gamma_f = d_{01}F^{k_1/2}$ (Eq. 6.6), a nonresonance shift
$\delta\omega_{01} = \tfrac14\alpha F$ (Eq. 6.7, which is this repository's own
$\Delta E = -\tfrac14\alpha E_0^2$ convention arrived at independently), and an
ionization broadening $\Gamma_i = \alpha_{1E}F^{k_2}$ from the resonant state to
the continuum (Eq. 6.8). The prescription is to use the weak-field Lorentzian of
Eq. (6.5) with $\Gamma$ replaced by a combination of $\Gamma_f$ and $\Gamma_i$.

So the correct citation for the third-photon question is Section 6c, and the
right way to price it is their $\Gamma_i$, not a fresh derivation. For this
experiment all three terms are far below the natural width. The measured numbers
are in [THEORY_NOTE](../THEORY_NOTE.md) section 5.2: the third photon lands
345 cm^-1 above the real 6S to 8P3/2 transition, its 8P admixture is 1.7e-9 at
the campaign field, and every scattering channel together reaches 0.122 per
second against a 6S decay rate of 2.194e7 per second. The fourth-order shift
channel is of order 1e-3 Hz, eight orders below the light-shift bound.
