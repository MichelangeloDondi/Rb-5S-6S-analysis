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
  - 'The held file is the English translation in Sov. Phys. Usp. 23(8), Aug 1980,
    supplied by the experimenter. Its OCR text layer is poor -- equations and
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

**Read 2026-07-30** from the rendered pages of the held translation, fetched by
the experimenter after [camparo1992](camparo1992.md) was found to attribute the
lineshape-mapping idea to it. It costs the novelty claim more than the
attribution suggested.

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

$$K(\Omega) \sim P\left(-\frac{\omega_{n1}-\Omega}{\alpha_{1f}\hbar}\right), \qquad \frac{\Omega-\omega_{n1}}{\alpha_{1f}\hbar} > 0$$

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

**Paper 1's introduction should cite this paper early and concede all four
points above explicitly.** A referee who knows the Soviet nonlinear-optics
literature will otherwise find it, and the claim as previously worded would not
survive that.

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
beam. That must be said in Paper 1's introduction in those words.

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
