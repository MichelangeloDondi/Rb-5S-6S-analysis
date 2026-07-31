# Literature ledger — prior art, anchors, and the novelty delineation

Purpose: every external number or claim this analysis leans on, with provenance,
so no novelty sentence is written from memory. House rules apply: VERIFIED
means we read the source itself; REPORTED means a literature-scout summary
we have not yet read in full — cite nothing REPORTED until it is upgraded.

## 1. Nearest prior art — MUST cite and delineate

**[Stalnaker et al., Phys. Rev. A 73, 043416 (2006)](lit/stalnaker2006.md)**
(arXiv:physics/0512111) — VERIFIED (full text read 2026-07-12); lineage
Wieman et al., PRL 58, 1738 (1987), Cs 6S→7S parity violation. One-photon
forbidden Stark-induced transition (Yb 408 nm), collimated atomic beam,
cavity standing wave, numerically fit to extract α = −0.312(34) Hz/(V/cm)²
— so the asymmetry-as-observable idea EXISTS in prior art; the claim
must be narrower than "first use of the asymmetry".

Delineation (what is genuinely not in Stalnaker/Wieman):

| Axis | Stalnaker 2006 | This work |
|---|---|---|
| Transition | 1-photon Stark-induced (signal ∝ I) | 2-photon (signal ∝ I²) |
| Ensemble | collimated beam, velocity-selective | thermal vapor cell |
| Regime | **fringe-resolved**: FM index ξ/Ω ≳ 1, Bessel sidebands, sub-Doppler features | **fringe-averaged**: ξ/Ω ~ 10⁻³, atoms see the time-averaged envelope |
| Lineshape | numerical Bloch, per-condition | **closed-form** shift density f(s) ∝ \|s\| on [−S₀,0] |
| Extraction | full-shape fit; needs β, cavity field, velocity model, per-scan free center | **closed-form ramp** fit with a per-trace free center; the ramp SHIFT is absorbed by the free center, so S₀ is read from the drift-invariant SHAPE ASYMMETRY (skew) — the stable-lock pull is the fixed-lock session's separate, larger handle |
| Saturation | saturating + hole-burning entangled with the asymmetry | unsaturated throughout (C3: amplitude consistent with ∝ P², slopes 1.83–2.12) |

The generic quasi-static law both regimes reduce to: signal weight ∝ Iⁿ over
a Gaussian envelope gives dA ∝ dI/I, hence **f(s) ∝ |s|^(n−1)** — uniform
for their n = 1, triangular for our n = 2. The triangular form is specific
to two-photon excitation; the same dA ∝ dI/I holds for a thin evanescent
shell, which is the geometry-independence bridge to the nanofibre extension. CALCULATED
(README derivation to be extended with this comparison).

**What we take from it:** their FM framework settles our ⟨E²⟩ convention question.
Their Sec. IV/Fig. 6 analysis: an atom crossing standing-wave fringes sees
frequency modulation of depth ξ = ½αε₀² at rate Ω/2π = 2v/λ. For us:
λ/2 ≈ 0.50 µm fringes, axial thermal speed ~280 m/s → Ω/2π ≈ 0.56 GHz,
ξ = S₀ ≲ 1 MHz → **modulation index ξ/Ω ≲ 2×10⁻³ → pure carrier at the
time-averaged intensity**. So the shift is set by the fringe-averaged
intensity I₁ + I₂ = (1+ρ)I₁ — no coherent ×2 fringe enhancement. The
residual OPEN item is the retro ratio ρ, which a fixed-lock session would
measure in situ per configuration (none is scheduled). But the fringe-resolved tail is NOT a benign percent-level
broadening: near-transverse atoms (small axial speed) sample the node/antinode
arcsine, and because the fringe MULTIPLIES the shift (s → s(1+x), x arcsine) it
SUPPRESSES the ramp skew — κ₃ → S₀³(1/135 − f_res/10) at ρ=1, a −13.5·f_res
fractional leverage (∝ contrast², not contrast³ — the arcsine has E[cos³]=0; only
the product P = f_res·σ_x² is observable). Negligible at w₀=50 µm (~5–8% of an
already-below-noise skew), ~26–28% at w₀=16 µm, and same-sign-additive to the
beam-divergence correction — fit jointly at the small waist (quantified,
coherence-window bracketed, in `rb5s6s/fringe_tail.py`). CALCULATED 2026-07-17.

**[Hamilton et al., Phys. Rev. Applied 19, 054059 (2023)](lit/hamilton2023.md)**
(arXiv:2212.10743) — VERIFIED (full text read). The
nearest prior art for our specific CONSTRUCTION, and geometrically closer
than Stalnaker: a RETRO-REFLECTED Rb-87 vapour two-photon line (5S→5D,
two-colour 780+776 nm), building the identical focus average — the same
Iⁿ·(linear shift)·(r dr) integral we reduce to the wedge.

Delineation (what is genuinely NOT in Hamilton) — see
[lit/hamilton2023.md](lit/hamilton2023.md): they collapse the integral to a
single spatially-averaged shift without ever keeping the shift DISTRIBUTION
(the novelty is "keep the distribution, close it in form, read the
drift-immune skew", not "set up the integral"); their signal is a
two-colour PRODUCT I₇₈₀·I₇₇₆, not the degenerate single-colour I² of our
993 nm 5S→6S virtual-state two-photon; and they do not treat the axial
standing-wave fringes at all (fringe-*ignored*, not fringe-*averaged*,
which reinforces rather than threatens our fringe delineation).

MUST be delineated in the paper's introduction: a referee who knows Hamilton will
see the integral parallel immediately, so we state up front what we add.

**Dounas-Frazer, Tsigutkin, Family, Budker, Phys. Rev. A 82, 062507 (2010)**
(arXiv:1009.5952) — VERIFIED online (ADS 2010PhRvA..82f2507D; PDF TO-PULL).
Extends "polarizability from a standing-wave lineshape" to Yb 5d6s ³D₁ (dynamic
scalar + tensor), same fringe-resolved atomic-beam family as Stalnaker/Wieman.
Reinforces that polarizability-from-asymmetry is established prior art — so our
novelty is narrowed to the fringe-AVERAGED closed-form + drift-immune moment.

## 2. Collision-rate series — calibrates what β_self should BE

[Zameroski et al., J. Phys. B 47, 225205 (2014)](lit/zameroski2014.md) —
full text HELD and read 2026-07-27, correcting this entry's central number.
Zameroski measures the 5S→7S **self-BROADENING** rate directly:
**129 ± 11 kHz/mTorr**, i.e. **5.39 ± 0.46 kHz per 10¹² cm⁻³** at their cell
temperature — the only measured self-broadening rate for an nS state in Rb, and
exactly the observable β_self is. Their 7S self-*shift* "could not be extracted
from the experimental data"; the −17.82(81) kHz/mTorr this entry previously
attributed to them is **Morzyński 2013's**, on the laser axis (Zameroski
restates it on the transition axis as −35.6 ± 1.6). Scaling the measured 7S
broadening to 6S by the computed C₆ ratio (M18, 0.347) gives the expected
**β_self(6S) = 3.5 ± 0.3 kHz per 10¹² cm⁻³** — anchored on a measurement, with
the suspect impact prefactor cancelling in the ratio. Derivation in the lit
file and in `rb5s6s/vanderwaals.beta_self_anchored`.

Consequences (calibration against the theoretical expectation):
- The archival bound (0.2–0.4 MHz per 10¹² cm⁻³) sits **57–113× above
  the expected value** — consistent, but NOT constraining. Paper
  wording must say exactly that; the bound's value is methodological (it
  quantifies the drift confound), not a physics constraint on β.
- **The 70–130 °C lever is insufficient to MEASURE the expected β**:
  ΔN ≈ 2×10¹³ cm⁻³ → Δγ ≈ 20 kHz, invisible under any realistic width
  budget. A real measurement needs **150–170 °C points** (N ≈ 0.7–2.7×10¹⁴
  cm⁻³ → Δγ ≈ 0.07–0.25 MHz) — a fixed-lock-session shot-list change, subject to
  cell/oven limits. Trapping grows there but affects amplitude, not width.
- Weber & Niemax, Z. Phys. A 307, 13 (1982) (Rb nS/nD self-broadening
  series) — TO-PULL; it is the n-scaling anchor that makes "6S completes
  the series" quotable.

**Broadening-theory backdrop + new anchors (intake 2026-07-13):**
- *Why the S→S self term is small (the physics behind the ~1 kHz expectation).*
  The 5S and 6S are both S states, so the 6S–5S pair has **no resonance
  dipole–dipole (C₃) self-broadening** — the self term is van-der-Waals (C₆),
  which is why it sits far below the resonance lines. [Sautenkov et al.
  2026](lit/sautenkov2026.md) makes the contrast concrete via their Rb D2
  resonance-line self-broadening decomposition. **[FEED]** for the
  resonance-vs-vdW contrast in §VI.A; their static+collision-width split
  mirrors our transit(static-ish)/γ_coll(collision) decomposition.
- *Isotope effect on β (why β₈₅ = β₈₇ matches the theoretical prediction).* [Bala
  et al. 2026](lit/bala2026.md) give the theoretical isotope-dependence of
  collisional widths/shifts from reduced mass + C₆ + scattering length; in
  the thermal impact regime this predicts a negligible width isotope-effect,
  so our measured β₈₅ = β₈₇ null is the physically expected result.
  **[FEED]** for the isotope-null framing (their Hg–Rb ultracold system is a
  different regime; cite the framework, not the numbers).
- *Impact-broadening theory lineage.* Lewis 1980 (Phys. Rep. 58, 1) and Allard &
  Kielkopf 1982 (RMP 54, 1103) are the standard reviews (both paywalled); the
  Allard–Kielkopf lineage's recent [Spiegelman, Allard & Kielkopf
  2022](lit/spiegelman2022.md) is a **[FEED]** pointer to the
  quasistatic/satellite regime our low-density impact-regime Lorentzian
  assumption sits opposite to.

## 3. Transit-time lineshape — the analytic pedigree of our transit kernel

Our transit kernel (lineshape.two_sided_exponential, the exp(−|ν|/b) that
convolves with the natural Lorentzian) follows the established treatment — it
is the established Doppler-free two-photon transit-time lineshape. Chain:

- [Bordé, C. R. Acad. Sci. Paris B 282, 341 (1976)](lit/borde1976.md) — the
  original, general two-photon transit-time derivation; cite as the primary
  general treatment only. Citation from search cross-refs; TO-PULL (French,
  likely no open PDF).
- [Biraben, Bassini & Cagnac, J. Phys. (Paris) 40, 445–455 (1979)](lit/biraben1979.md)
  — the canonical result: the finite-transit Doppler-free two-photon line is
  **exactly a Lorentzian ⊗ two-sided-exponential** ("double-exponential
  meeting at a cusp"); this IS our model. Open access (HAL jpa-00209125,
  access-gated to WebFetch but bibliographic data + the key "Lorentzian
  convolved with double-exponential" result VERIFIED via multiple search
  cross-refs 2026-07-12; read the HAL PDF to upgrade to fully VERIFIED).
- [K. K. Lehmann (sole author), J. Chem. Phys. 154, 104105 (2021),
  doi:10.1063/5.0040868](lit/lehmann2021.md) — the "Lehmann lineshape"
  (README §2.5): modern closed analytic form in the transit-time limit for a
  TEM00 standing wave, simpler than Bordé's general case, with γ₀(T) ∝ √T
  matching our √T scaling law (transit_fwhm_at_T). Title/journal/vol/year/DOI
  + functional form VERIFIED via search cross-refs; PDF at
  par.nsf.gov/servlets/purl/10477667 (socket-hung on WebFetch — retry to
  fully VERIFY and pull the exact γ₀(w₀,T) prefactor).

Why this matters for the paper: it upgrades the transit model from "assumed
shape" to "literature-standard analytic form," and it means the M8 Voigt-vs-
Lehmann BIC test is Gaussian-core (Voigt) vs the BBC-1979 cusp — a test
between two *published* forms, not against a made-up one. Our M9 Monte-Carlo
then refines the BBC idealization for our exact 3D-MB + w(z) + I² + collection
conditions (finding the real kernel slightly MORE cusped, excess kurtosis
~4.6). TO-DO before submission: read the Biraben and Lehmann PDFs to (a) fully
VERIFY, (b) pull the exact γ₀(w₀,T) prefactor so the transit width is an
absolute prediction, not a placeholder, and (c) confirm the b→FWHM and the
√T law match our transit_fwhm_at_T convention.

## 4. Anchors still at REPORTED status (upgrade before citing)

- **Cheng-group, Cs 6S–8S "effects of light"**: Lorentzian width constant
  (~1.51 MHz) while Gaussian grows with intensity — i.e. they absorbed the
  light-shift distribution into a symmetric second moment. Prior art that
  confirms the phenomenon while missing the asymmetry. REPORTED (2026-07-12);
  pull full text — a referee-critical citation.
- **Fendel/Udem/Hänsch, Opt. Lett. 32, 701 (2007)** (Cs 6S–8S comb):
  published paper text read directly (`lit/fendel2007.md`, VERIFIED). They
  *tested* peak against average and found the average correct,
  −0.21 Hz/(mW/cm²) against average single-beam intensity, cross-checked
  against cw and theory. Their waist was a deliberately unfocused 0.72 mm,
  chosen to keep the intensity distribution narrow — so the result holds where
  the distribution is narrow and says nothing about a tight focus. Cited in
  THEORY_NOTE §6; the nearest prior art on the peak-vs-average question.
- **Cs 6S–6D (2018)**: 40 µm waist → significant transit broadening.
  Cross-check vs our M9: scaling by v/w₀ (Cs ~200 m/s @40 µm vs Rb ~280 m/s
  @32 µm) puts their transit at ~0.6× ours — consistent with our
  1.87 MHz @ 32 µm (flux-corrected). REPORTED (scaling CALCULATED); pin the exact citation.
- **Taiwan comb work (Opt. Lett. 30, 842 (2005) + successors)**: 5S→7S
  absolute frequency, Stark/collisions suppressed as systematics. REPORTED.

## 5. Revised novelty claims (post-Stalnaker, wording to defend)

1. **REWORDED 2026-07-30 and much narrower than it was — read §5.2a first.**
   The old wording claimed the closed-form triangular ramp f(s) ∝ |s| and the
   |s|^(n−1) signal-exponent law as new. **They are not.** Both reduce exactly
   to Eq. (5.3) of [delone1980](lit/delone1980.md), a 1980 review, once the
   geometric P(I) ∝ 1/I of a Gaussian beam is substituted — verified against the
   shipped `stark_ramp` to 7×10⁻¹².
   What is claimable is the *evaluation and its consequences*, not the relation:
   **(a)** identifying that for a focused beam the shift distribution is fixed by
   geometry rather than by laser statistics, so Delone's integral — which they
   could only leave formal, P being their unknown — closes;
   **(b)** the resulting **analytic cumulants** on bounded support, in particular
   the intrinsic g₁ = +0.566 at n = 2, which is a number and not a fit;
   **(c)** the fringe-averaged treatment and the M19 result that a retro standing
   wave does not move the mean; and
   **(d)** the evanescent-geometry invariance of the dA ∝ dI/I step (the nanofibre extension
   bridge), which Delone have no occasion to consider.
   Stalnaker remains distinct on other axes (numerical, n = 1, fringe-resolved),
   but he is no longer the binding precedent for this claim — Delone is.
2. **The asymmetry channel, claimed for SPECIFICITY rather than sensitivity.**
   Reworded 2026-07-30 twice over: first because
   [delone1980](lit/delone1980.md) is closer here than Stalnaker, then because
   "drift-immune" named only half the argument.
   *What is conceded.* Delone frame the lineshape as a read-out channel —
   twice, explicitly: "one can reconstruct the distribution P(F) from this
   relationship". Using a lineshape to read a shift distribution is theirs.
   *What is claimed, and it is two separate properties.* **(i) Translation
   immunity:** the ramp's first-order effect is a centroid pull, which a
   per-scan free centre absorbs, so in a drifted archive the pull is degenerate
   with the drift; the asymmetry is not a translation and survives. That is the
   response to an unstable reference — a problem Delone do not have, and one
   precision groups solved the other way (Stalnaker fit full shapes against a
   good reference; others suppressed the shift).
   **(ii) Component specificity, which is the stronger half.** Every other
   factor in the model core — the natural and collisional Lorentzian, the laser
   kernel, the transit kernel — is **symmetric by construction**, and a
   symmetric factor cannot produce asymmetry at any width. The ramp is the only
   asymmetric factor, so the fitted asymmetry does **not** trade against
   $\Gamma_{\rm nat}$, $\gamma_{\rm coll}$, $\sigma_{\rm laser}$ or the
   transit width — the four-way degeneracy that dominates the width channel.
   The single remaining exposure is an *asymmetric* misspecification of the
   core, which is checkable by BIC and the M8 cusp fit. See
   [THEORY_NOTE](THEORY_NOTE.md) §3.
   *And the width channel is not a weaker alternative — it is blind.* At 225 mW
   and $w_0 = 50$ µm the ramp kernel is 0.33 MHz FWHM, which added in
   quadrature to the observed 5.2 MHz line is **0.010 MHz**, a part in 500. No
   width measurement reaches this signal at any precision.
   The same arithmetic settles a loose end in [lee2010](lit/lee2010.md): their
   power-dependent Gaussian growth of ~1.9 MHz is **4–9× larger** than the ramp
   their own measured light-shift coefficient can produce, so the intensity
   inhomogeneity they name — tentatively, "possibly", against velocity-dependent
   collisions as the alternative — is probably not its dominant cause.
   PRELIMINARY: the span covers the retro and transition-vs-laser-axis
   conventions their text leaves open. **[OPEN]**
3. **β_self(6S)**: completes the measured 5D/7S self-rate series — a
   modest addition to the measured series rather than a headline result. In the archive it is a bound 57–113×
   above expectation; a measurement requires the high-T extension.
4. **EOM-comb-in-fine-scan** frequency axis (0.04257(5) MHz/ms laser-axis,
   per-block).

NOT claimable: "asymmetric lineshapes from distributed AC-Stark are new"
(Wieman 1987 / Stalnaker 2006 own it), "first extraction of a
polarizability from the asymmetry" (Stalnaker did exactly that, Eq. 45), or —
both added 2026-07-30 — **that intensity-inhomogeneity broadening of a two-photon
alkali line in a hot cell is a new observation** ([lee2010](lit/lee2010.md) owns
it; see §5.3), or **that reading a lineshape as a map of the underlying
distribution of AC-Stark shifts is a new frame**.

> **The mapping idea is 1992 at the latest, and for a two-photon transition
> (found 2026-07-30 while auditing).** [camparo1992](lit/camparo1992.md) §3:
> "the multiphoton transition line shape may be expected to act as a map of the
> probability distribution of Stark shifts, which will follow the asymmetric
> distribution of $(1+\epsilon)^2$." That is materially closer to this analysis'
> frame than `wieman1987` or `stalnaker2006`, both of which are one-photon, and
> the concession must name it.
>
> What survives is the same narrow thing §5.3 leaves standing. Camparo's
> distribution is over **temporal** fluctuations of a stochastic multimode
> field, its inhomogeneous character is contingent on an adiabaticity criterion
> $\Omega \gg 1/\tau_{\rm coh}$, the distribution is the field's own
> $(1+\epsilon)^2$ statistics, and the treatment is Monte-Carlo. This
> programme's is over the **spatial** transverse profile of a coherent beam,
> quasistatic by construction, with a closed form $f(s)\propto|s|^{n-1}$ and
> analytic cumulants. **The claim is the closed form and its cumulants — never
> the mapping, never the phenomenon.**
>
> Camparo attributes the mapping to Delone, Kovarskii, Masalov & Perel'man,
> *Sov. Phys. Usp.* **23**, 472 (1980). **That review is now held and read, and
> it is worse than the attribution suggested — see below.**

> ### 5.2a The concession runs to 1980, and the closed form is not new either
>
> [delone1980](lit/delone1980.md), read 2026-07-30 from the rendered pages,
> contains four things this repository had treated as its own frame — and it is a
> **review**, so they were established before it:
>
> - **Eq. (4.5):** $K(\Omega) \sim P(-(\omega_{n1}-\Omega)/\alpha_{1f}\hbar)$ —
>   for a shift linear in intensity, the lineshape *is* the intensity
>   distribution, rescaled by the polarizability.
> - **Eq. (5.2):** the multiphoton rate as a shifted Lorentzian integrated over
>   $P(F)$ with an **$F^{k}$ weight**, $k$ = number of photons absorbed. That is
>   `THEORY_NOTE` §2's construction with $k$ in the role of $n$.
> - **Eq. (5.3):** the shift-dominated limit,
>   $W \sim (\omega_f-k\omega_0)^k P((\omega_f-k\omega_0)/\alpha_{1f}\hbar)$,
>   which they describe as "an asymmetrically broadened line".
> - **The inverse problem**, stated twice: "one can reconstruct the distribution
>   $P(F)$ from this relationship."
>
> **And the closed form reduces to theirs exactly (CALCULATED 2026-07-30).** For
> atoms uniform in space across a Gaussian profile the area measure gives
> $2\pi r~{\rm d}r \propto {\rm d}I/I$, so $P(I)\propto 1/I$ — verified
> numerically to 1 part in $10^4$ over four decades. Substituting that into their
> Eq. (5.3) gives $W(s)\propto s^{k}\cdot s^{-1} = s^{k-1}$, i.e.
> $f(s)\propto|s|^{n-1}$ with $k=n$; and at $n=2$ it agrees with the shipped
> `lineshape.stark_ramp` to $7\times10^{-12}$. **This repository's closed form is
> Delone's Eq. (5.3) evaluated for the intensity distribution of a focused
> Gaussian beam.** the introduction here must say so in those words.
>
> **What survives, and it is narrower than claim 1 as written.** Delone treat
> $P$ as the *unknown to be reconstructed* — their point is that the lineshape
> measures the laser's statistics. This programme runs it backwards: $P$ is
> **known from the geometry**, so the integral evaluates and the result carries
> **analytic cumulants**, an intrinsic $g_1=+0.566$ on bounded support that is a
> number rather than a fit. Delone cannot write that number because in their
> setting it is exactly what is unknown. The defensible contributions are
> therefore: evaluating a known general result for the geometry that actually
> occurs; its cumulants in closed form; and using the **third** cumulant as a
> drift-immune measurement channel — which answers an experimental problem (an
> untrustworthy centre) that does not arise in Delone's setting. **Claim 1 above
> should be reworded accordingly before the introduction is drafted.** **[OPEN]**

> **The concession stands, and it can be narrowed — but not yet (2026-07-30).**
> [`wieman1987`](lit/wieman1987.md) now has a note and a full record: *Asymmetric
> line shapes for weak transitions in strong standing-wave fields*, Wieman,
> Noecker, Masterson & Cooper, *Phys. Rev. Lett.* **58**, 1738 (1987),
> doi:10.1103/PhysRevLett.58.1738. It is **REPORTED, not VERIFIED**: the abstract
> and the record were read from the publisher, and the physics from the
> introduction of [`stalnaker2006`](lit/stalnaker2006.md) — held, read, and
> self-described as generalising it — but the paper itself is 1987, predates
> arXiv, and APS returns 403 without a subscription.
>
> What that establishes: they excited the **forbidden 6S → 7S M1 and
> Stark-induced** line in Cs where an atomic beam crosses an intense **standing
> wave**, whose spatial variation makes the shift position- *and*
> velocity-dependent, and modelled the resulting Doppler-free distortion with
> optical Bloch equations. So the general concession is correct and nothing here
> is first at "asymmetry from a distributed AC-Stark shift".
>
> What it also shows is that the *mechanism* is not the same one. Theirs is a
> **one-photon** rate, and [THEORY_NOTE](THEORY_NOTE.md) §2 gives
> $f(s)\propto|s|^{n-1}$, so $n=1$ — the case it already names as "a
> Stark-induced forbidden line" — is the **uniform** distribution with
> $\kappa_3 = 0$, exactly zero skew. The triangular ramp and its $+0.566$ cannot
> be Wieman's effect; theirs is the standing wave's node structure crossed with
> velocity, ours the $I^2$ weighting over a transverse Gaussian, with the
> standing wave shown not to move the mean at all (M19).
>
> The delineation is therefore left **conceded in general and narrowed in the
> note, not here** — narrowing a priority claim on a paper nobody has read is the
> error this repository has spent the week correcting. Read the full text before
> the introduction here. The three things to check are listed at the end of the
> note.

### 5.1 Narrowed again by the adversarial audit (2026-07-26)

An external deep-search audit found **two further precedents, both now read
here**, and claim 1 above had to give ground twice:

- [slepkov2010](lit/slepkov2010.md) — Rb in a hollow-core fibre. Simulates the
  AC-Stark-shifted line through a Gaussian-core guided mode; "the nonuniformity
  of the core mode is also seen to broaden and to steepen the line toward
  higher frequencies", and the data are fit by that simulated non-uniform-mode
  lineshape in preference to a flat-top model. **Keeping the distribution is
  not new**, and it has been done in a guided geometry.
- [wall2014](lit/wall2014.md) — helium Rydberg states, and the stronger
  precedent of the two: it is **single-colour two-photon**, so the I²
  weighting is present too, alongside the "bunch up close to the unperturbed
  transition frequency" density-of-states argument. **The I² weighting is not
  new either.**
- [camparo1992](lit/camparo1992.md) — a two-photon Stark-shift *distribution*
  giving "an asymmetric resonance line shape in a fashion analogous to
  inhomogeneous broadening", though over a stochastic field in time rather than
  position in a beam. Different mechanism; cite it, do not conflate it.

**What survives, and it is narrow:** the **closed form** — an analytic
triangular weight with a calculable asymmetry coefficient — used to recover the
shift **when the frequency reference is unusable**. Checked in both PDFs:
Slepkov and Wall each reproduce their lineshape by numerical ensemble averaging,
describe the asymmetry qualitatively, keep the frequency axis intact, and never
invert the lineshape for the shift. Cite all three up front rather than let a
referee find them.

### 5.2 Negative searches — record these, they are what defend the rest

The same audit searched and found nothing, which is worth stating explicitly in
any manuscript:

- **No other group working 5S–6S.** Precision work on this line remains the
  USAFA lineage (Orson, Ayachitula). No new entrants found.
- **No prior 5S–6S magic wavelength.** *Phrase the claim as 5S–6S
  specifically*, because the nearest prior number is close:
  [zang2012](lit/zang2012.md) (arXiv:1204.4354, held) tabulates magic
  wavelengths for the **6s–5p₁/₂,₃/₂** pairs of a four-level active clock and
  reports **six** of them between 1200 and 1600 nm: 1342 and 1421 nm for
  6s–5p₁/₂, and 1331, 1336, 1453, 1461 nm for 6s–5p₃/₂. **This work's 1339.6 nm
  is bracketed by two** — 1336 (−3.6) and 1342 (+2.4). *This entry previously
  recorded only 1342, which understated it.*
  What defuses it is structural rather than rhetorical: their Table I puts the
  5p₁/₂–6s₁/₂ resonance at 1323.88 nm and 5p₃/₂–6s₁/₂ at 1366.87 nm, so **every**
  6S-involving magic wavelength in the infrared is confined to that 43 nm window
  and few-nm separations inside it are forced by the level structure. Different
  state pair, different magic condition — but the claim must be phrased as
  5S–6S specifically, and should say why the proximity is expected rather than
  leaving a referee to wonder.
- **An external test set for M9, and it survives contact with the primaries**
  ([bandi2025](lit/bandi2025.md) Table 1). Ten Rb two-photon vapour-cell
  standards, tabulated with signal linewidth, cell temperature **and 1/e² beam
  waist** — the three quantities `transit_fwhm_from_w0` maps between. A first
  pass looked inconclusive, with Callejo's row apparently impossible (transit
  alone 597 kHz against a 450 kHz *total*). **Two rows were then run down to
  their primaries on 2026-07-30 and both check out.**
  [callejo2025](lit/callejo2025.md): the waist is genuinely ~100 µm, but their
  measured linewidth is **1.5–2.1 MHz, not the 450 kHz tabulated** — that row
  conflates the MEMS microcell with the reference glass-blown cell — and against
  the primary numbers transit supplies 34–51% of the excess over the 330 kHz
  natural width, as it should. `lemke2022` (now held): w₀ = 2.1(3) mm, stated as
  an **intensity radius (1/e²)**, giving 13%, as a millimetre beam should.
  So Callejo's anomaly was a transcription error in the review, not a defect in
  M9. **But the column is not uniform** — a claim briefly written here that it
  was a radius throughout is withdrawn: Erickson's thesis states "310 kHz for
  230 µm beam **diameter**", against Lemke's explicit radius. Worse, at
  Erickson's geometry our `transit_fwhm_from_w0` gives 513 kHz against his
  310 kHz, a factor of 1.65 that is a **transit-definition** difference rather
  than a waist one. **No cross-paper transit number from this table is quotable
  until that definition is pinned down.**
  **Seven of the table's primaries are already held** —
  [gerginov2018](lit/gerginov2018.md), [callejo2025](lit/callejo2025.md),
  [beard2024](lit/beard2024.md), [poulin2002](lit/poulin2002.md),
  [martin2018](lit/martin2018.md), [erickson2024](lit/erickson2024.md) (the
  thesis, held under `PDF_papers/theses/`) and `lemke2022` (held, note
  pending) — so finishing this is mostly a matter of reading what is on disk
  rather than fetching anything. **[OPEN]**
- **No profile-likelihood precedent** in vapour-cell two-photon metrology, and
  **no pre-registration or blind analysis** in atomic spectroscopy of this kind.
- **No 6S self-broadening coefficient** in a second targeted pass; Zameroski
  2014 (5D, 7S) remains the nearest. The gap is real, and
  [weller2011](lit/weller2011.md) now anchors the expected scale from above.

Not exhaustive: Japanese- and Russian-language 6S self-broadening theory was
not searched.

**Audit status of the notes these negative searches rest on (2026-07-30).**
`zang2012` was checked line-by-line against its PDF and four defects were found
and fixed, including the one corrected immediately above — a two-value reading
of a six-value table, in the note carrying a negative-search claim. That is
enough to distrust the rest by default. **Still unaudited, and load-bearing:**
[stalnaker2006](lit/stalnaker2006.md) (on which the "first extraction of a
polarizability from the asymmetry" concession rests, via its Eq. 45),
only. Everything on the list has now been checked by hand.
[stalnaker2006](lit/stalnaker2006.md) was checked on the claims §5 leans on and
they hold — Eq. (45) extracts a polarizability *combination* from fitted
lineshapes, Eq. (37) and Eq. (38) are the FM depth and rate as this repository
quotes them, and every Wieman characterisation sourced from its introduction is
verbatim. **What remains OPEN there is narrower and is ours, not theirs:** the
delineation table and the "Gift #1" fringe-tail derivation are this
repository's own inferences built on the paper, so they need checking against
`rb5s6s/fringe_tail.py` as well as against the PDF. One factor of two to carry
into any paper sentence: their carrier-only criterion is $\xi/2 \ll \Omega$, not
$\xi \ll \Omega$ (our index is $2\times10^{-3}$, so nothing shipped changes).
An unsourced "20–60 min per lineshape" computation time was removed from the
note; no such figure is in the paper. **[OPEN]**
  *Cleared by hand the same day, all three correct as written:*
  [biraben1979](lit/biraben1979.md) and [lehmann2021](lit/lehmann2021.md) — the
  transit-kernel pair whose form `bruvelis2012` had backwards — check out, with
  Biraben's abstract and Eq. (46) both giving the Lorentzian ⊗
  double-exponential and Lehmann stating the cusp explicitly. Biraben also
  contains the sentence that explains the `bruvelis2012` error: a Voigt *is*
  there, as the per-velocity-class profile, and the double exponential appears
  only after averaging over radial velocities.
  [weller2011](lit/weller2011.md) checks out too — its quotation is verbatim and
  $\beta/2\pi = (0.69 \pm 0.04) \times 10^{-7}$ Hz cm³, the 0.73 theory value,
  the 0.1% agreement to $3\times10^{14}$ cm⁻³ and the 170 °C all hold. So do
  [wall2014](lit/wall2014.md) (record, authorship and the "bunch up" passage all
  exact) and [camparo1992](lit/camparo1992.md) — though Camparo turned up a
  sentence that costs a novelty claim, recorded in §5 above.
  **Two attribution errors were found outside the checked set and fixed:**
  [saha2010](lit/saha2010.md) and [slepkov2010](lit/slepkov2010.md) were both
  credited with an 18 µm hollow-core mode field that appears in **neither**
  paper — Saha's own fibre is a 6 µm Crystal Fiber AIR-6-800, and "CRYST3" is
  not in Slepkov at all. The 18 µm belongs to the experimenter's own CRYST³
  fibre at Bologna; it was unsourced in this repository until 2026-07-31, when a
  held master's thesis on that apparatus (Nasoni 2026) supplied it as the
  **injection beam waist of the 1064 nm dipole-trap beam** — a **radius**. The
  thesis calls ~18 µm the *target*; its ideal thin-lens value is 13.6 ± 0.1 µm,
  but the measurement on the same page is 17.1 ± 0.7 µm by 19.3 ± 0.4 µm, so
  ~18 µm is the figure to carry. It is an injection waist for the *trap* beam,
  not the guided mode of a two-photon probe.
  [stalnaker2006](lit/stalnaker2006.md) was spot-checked on the two claims §5
  leans on: its Eq. (45) does extract a polarizability combination from fitted
  lineshapes — $\alpha_0^{ac}(^3D_1) + \alpha_2^{ac}(^3D_1) - \alpha_0^{ac}(^1S_0) = -0.312(34)$
  Hz/(V/cm)² — so the concession stands, and
  every characterisation of Wieman that [wieman1987](lit/wieman1987.md) sources
  from its introduction is verbatim. A full pass on it is still outstanding.

### 5.3 The nearest analogue experiment, and what it costs claim 1 (2026-07-30)

[lee2010](lit/lee2010.md) — Lee, Chui, Chen, Chang & Tsai, *Opt. Commun.* **283**,
1788 (2010), held and read, is closer to this analysis than anything in §5.1. Not an
adjacent geometry: **the same experiment**, in Cs. A two-photon $nS \to n'S$
alkali line in a hot vapour cell, Doppler-free with a retro-reflected beam,
cascade-fluorescence detection, laser intensity and vapour density scanned as the
two independent variables, and a lineshape decomposition into a homogeneous part
and an intensity-dependent part. They attribute the intensity-dependent part
as one of two candidates — "the laser beam is not a plane wave. Therefore, the
Gaussian width is possibly obtained from the spatially inhomogeneous of laser
intensities" — and
report a light shift of $-7.25(45)$ Hz/(mW/mm²) and a power- and
pressure-independent Lorentzian of $1.53 \pm 0.08$ MHz. Their hedge is worth
keeping: they write the Gaussian is "*possibly*" from the intensity
inhomogeneity, and keep velocity-dependent collisions alive as the alternative.

**What this takes.** The *phenomenon* — that the transverse intensity
distribution broadens a two-photon alkali line, and that the broadening grows
with power while the homogeneous part does not — is theirs, sixteen years ago.
Any wording implying this programme first noticed that is indefensible.

**What survives, and it is the whole of claim 1.** They fit the effect as a
**Gaussian**: symmetric, $\kappa_3 = 0$, no closed form, no cumulants, and the
distribution treated as a nuisance parameter to be separated from the natural
width. The programme's derivation gives $f(s)\propto|s|^{n-1}$ — triangular at
$n=2$, with intrinsic skew $g_1 = +0.566$ — and a Voigt fit has no third moment
to put it in. So the claim to defend is **the shape and its cumulants**, never
the phenomenon. That is narrower than the §5 wording was, and it is the version
that survives contact with this paper.

**There is a check against their published data, but not the obvious one, and
this section first stated it wrongly.** The tempting argument — an AC-Stark
$W_G$ must be *linear in power*, their $W_G$ is not linear through the origin,
so something is missing — **is invalid**: $W_G$ is the total Gaussian component
of a Voigt fit, independent Gaussian terms add in quadrature, and so
$W_G(P)=\sqrt{W_{G0}^2+(aP)^2}$ is non-linear and misses the origin even when
the AC-Stark part is exactly linear. The correct test is $W_G^2$ against $P^2$,
whose intercept is the power-independent floor and whose slope carries
$\Delta\alpha$. Note their floor is *not* the 1 MHz laser bandwidth, which they
assign to the **Lorentzian**. Even done properly this probes the kernel's
*width*, not its *shape*; the shape needs residuals they do not publish.
**Nothing computed. Recorded as OPEN, not as evidence.**

**A caution that points back at us.** Their headline is that the Lorentzian is
invariant, read as the natural width. If the true intensity kernel is skewed and
is fitted as Gaussian, the misspecification has to go somewhere, and in a Voigt
fit that is usually the Lorentzian. Whether their 1.53 MHz bound survives a
correctly shaped kernel is open — and the same question is the `transit_kind`
model-form systematic on $\beta_{\rm self}$ (M4c/M8), where this repository
already differences the two-sided-exponential and Gaussian transit forms for
exactly this reason.

## 6. Prior work on THIS line (5S–6S, 993 nm)

Two distinct lineages measured our exact transition before us: the **OIST**
apparatus lineage (Nieddu, Rajasree — direct provenance for our cell/beam) and
the **USAF Academy** precision-metrology lineage (Orson 2021, Ayachitula 2024 —
hyperfine/isotope-shift metrology, and the prior AC-Stark/density-shift NULLS our
archival bounds refine).

### 6a. OIST apparatus lineage (our provenance + a corroborating data point)

- **Nieddu 2019** (Opt. Express, [`nieddu2019`](lit/nieddu2019.md); + his OIST
  PhD thesis) — the group's 993 nm two-photon *frequency-reference*
  demonstration on our exact line. **[CITE, ESTABLISHED]** Load-bearing facts
  extracted (2026-07-13):
  * **Beam geometry:** they measured **w₀ = 64 µm** (f₁ = 150 mm plano-convex
    L1) — see [nieddu2019](lit/nieddu2019.md). This is the direct beam
    measurement that corroborates our transit-physics w₀ re-pin (32 µm is
    excluded; archival w₀ ~ 50–64 µm — see
    `docs/notes/transit_width_resolved.md`).
  * **Line width:** their four two-photon peaks (FWHM ~5 MHz transition axis
    — see [nieddu2019](lit/nieddu2019.md)) are CONSISTENT with our archival
    ~5.25 MHz (an external corroboration of the observed width). Their
    reference laser had a ~100 kHz linewidth (vs the drifted 2025 lock).
  * They state the two-photon mapping explicitly ("relative frequency differences
    of the peaks are half the actual energy differences") — the laser↔transition
    factor of 2 we carry project-wide.
  * NB: a saved in-repo Q&A note claiming Nieddu's "2.5 MHz" is a
    stability/factor-2 artifact was **debunked** on reading the paper — 2.5 MHz is
    a real two-photon FWHM (laser axis); the note wrongly used the 795 nm D1
    *detection*-photon width as a floor on the *resonance* width (see DATA.md).
  * **Apparatus:** [nieddu2019](lit/nieddu2019.md)'s retro is a concave mirror
    (f = 75 mm) at 2f from the focal plane — a self-imaging arrangement, the
    same idea as ours, implemented differently. Ours (MD, 2026-07-14) is the
    **lens-based equivalent** — L1 (f = 150 mm) focuses into the cell, L2
    (f = 150 mm) after the cell maps the waist to a ~1 mm intermediate waist,
    and a **flat mirror** at that flat wavefront time-reverses the beam so it
    retraces and re-forms the original waist (methods §2.6). So ρ ≈ 1 is a
    *design property* in both experiments, and the forward/return **mode
    match is by construction** in ours too; ρ departs from 1 only through
    losses (extra L2 and window passes, mirror reflectivity), never
    characterized for the archive. Residual sensitivity is mirror **tilt**,
    not longitudinal placement (the intermediate beam's z_R ≈ 2.8 m makes the
    mirror position forgiving to tens of cm). A fixed-lock session would measure ρ
    in situ (PLAN §8.1).
  * Their detection ([nieddu2019](lit/nieddu2019.md)) is the **780 nm and
    795 nm cascades together** through an 800 nm short-pass (Hamamatsu
    R636-10) — unlike the 2025 archival 795-only narrowband stack — so
    amplitude/trapping comparisons against Nieddu must not assume the same
    collection channel (the 780/D2 branch sees a different optical depth than
    795/D1). QWP slots exist before L1 and before the CM.
- **Rajasree-KP 2020, OIST PhD thesis**
  ([`rajasree2020thesis`](lit/rajasree2020thesis.md), held) — its §5.2 repeats
  the same 993 nm cell setup (L1 with $f = 150$ mm, a **measured** 128 µm beam
  *diameter*, concave-mirror retro at $f_{\rm CM} = 75$ mm, cell at 130 °C) and
  cites Steck for the Rb data, confirming both the beam geometry and the N(T)
  vapour-pressure chain our `density.py` uses. **[FEED, VERIFIED from the held
  PDF]** *Corrected 2026-07-31:* this entry carried the citekey
  [`rajasree2020`](lit/rajasree2020.md), which is a different document — *PRR*
  **2**, 012038, cold Rydberg atoms near an ONF, with no warm cell. The prose
  named the thesis; the key resolved to the paper.
- **Rajasree 2020, PRR 2, 033341** ([`rajasree2020spin`](lit/rajasree2020spin.md),
  held) — *spin selection in single-frequency two-photon excitation*, tested on
  OUR line in two configs. **[CITE, ESTABLISHED]** Three load-bearing
  consequences:
  * **The polarization amplitude law (paraxial, warm cell):** the transition
    rate scales as the **squared degree of linear polarization, D²** — exactly
    zero for circular light (see [rajasree2020spin](lit/rajasree2020spin.md)).
    Two uses for us: (i) a drifting polarization (thermally stressed cell
    windows, waveplate drift) is a *specific, physically-motivated* candidate
    for the M10 between-block amplitude wander — common-mode per block, but
    the archival peaks were taken hours apart, so it does not cancel in the
    cross-peak ratios; a fixed-lock session should **log (or fix with a clean
    polarizer) the polarization at the cell**. (ii) A free fixed-lock-session
    diagnostic: rotating to circular must **extinguish** the two-photon line —
    any residual is polarization impurity or background, a null test that costs
    one waveplate turn per config.
  * **The scalar-operator basis, published in-lineage:** their K = 0, 1, 2
    two-photon operator decomposition (with Le Kien) is the citable basis for
    our M10 degeneracy-law claim (identical photons on S→S: vector and tensor
    parts vanish, only the scalar survives ⇒ areas ∝ abundance × (2F+1)).
  * **ONF feasibility evidence for the nanofibre extension:**
    [rajasree2020spin](lit/rajasree2020spin.md) demonstrates 5S–6S excitation
    in **cold ⁸⁷Rb around a 400 nm-waist nanofibre** (SM800-5.6-125, ~30%
    transmission at 993 nm) via the evanescent field — so ONF-mediated 5S–6S
    from atoms near the fibre is *demonstrated*, and the open nanofibre question
    is the quantitative near-surface *lineshape* program (pushing dip, surface
    shift), not whether the signal exists. Nonparaxial twist: in the
    evanescent field the transition is **not extinguishable** by polarization
    — the longitudinal field components break the paraxial D² law, itself a
    lineshape-relevant fact for any ONF campaign.

### 6b. USAF Academy precision-metrology lineage (Knize/Lindsay group)

*This group did the precision hyperfine/isotope-shift metrology on our line, and —
directly relevant to us — looked for the AC-Stark and collisional shifts and
reported NULLS at MHz-scale resolution. Our archival BOUNDS sit below their
resolution; our two-epoch design turns those nulls into measured coefficients.*

- **Ayachitula 2024** ([`ayachitula2024`](lit/ayachitula2024.md), Phys. Rev. A
  **110**, 022803) — the kHz-precision Doppler-free two-photon remeasurement
  of the 6S₁/₂ hyperfine structure, both isotopes; now the source of
  `A_6S_RB87/85_HZ` in `constants.py` (swapped in 2026-07-13, superseding
  Perez Galván 2008 — see [ayachitula2024](lit/ayachitula2024.md) for the raw
  values). **[CITE, ESTABLISHED]** Their line-center drift control (<0.5 kHz
  over 50 min; centers stable to 3 kHz) is a benchmark for what a fixed lock
  buys — exactly the target for a fixed-lock session.
- **Orson 2021** ([`orson2021`](lit/orson2021.md), J. Phys. B **54**, 175001;
  same USAFA group) — absolute hyperfine energy levels + isotope shift of the
  5S–6S transition. **[CITE]** Their prior AC-Stark and density-shift nulls
  (see [orson2021](lit/orson2021.md) for the exact quotes and resolution) are
  on our C3d (AC-Stark) and C1 (collisional self-shift) channels — consistent
  with, and refined below, by our archival bounds (S₀ < 0.63 MHz, profile
  likelihood; β_self a bound). They are also the **source of our
  `DELTA_ALPHA_AU = +1093`** (opposite sign by definition; the value was never
  a loose in-house estimate), and our `stark_shift_S0_mhz` reproduces their
  predicted shift **to the digit** — locked by
  `test_stark_S0_reproduces_orson2021`. (Their 63 µm waist coincidentally
  echoes Nieddu's 64 µm, though a different apparatus.) **Intro framing:**
  prior groups looked for these shifts on THIS line and saw nulls at ~MHz
  resolution; our drift-immune ramp method + two-epoch design is the route to
  the coefficients *below* that floor.

## 7. Method anchors (intake 2026-07-13): FM ruler, radiation trapping, the two-photon review

- **FM-spectroscopy ruler ancestry (§V).** [Snadden, Bell, Clarke & Riis 1996](lit/snadden1996.md)
  — FM two-photon in cold Rb, EOM-ruler ancestry, alongside the (paywalled) Zapka
  1983 (CW two-photon FM in Rb vapour) and Bjorklund 1980 (the FM-spectroscopy
  origin). **[CITE]** for the ruler lineage; together they pre-empt a "has FM been
  used on this system?" referee question.
- **Radiation trapping (§VI.D / M7).** [Fioretti et al. 1998](lit/fioretti1998.md)
  — the alkali-cloud radiation-trapping anchor for M7/VI.D. **[CITE]** (now in
  hand; was a Tier-2 chase).
- **Doppler-free two-photon review (Intro).** [Biraben 2019](lit/biraben2019.md)
  — the pioneer's own retrospective review. **[CITE]**
- **Two-photon Rb in a confined/perturbed geometry.** [Amy et al. 2017](lit/amy2017.md)
  — two-photon Rb under confinement (context). **[FEED]**

## 8. The 2024–2026 landscape (vapour-cell positioning + future-transition frontier)

Source sweep: the local literature-intake landscape note (untracked, a `RECENT_LITERATURE`
working file not part of the repo). Options for the tunable Ti:Sapph:
`docs/FUTURE_TRANSITIONS_titsapph.md`. **DOI note:** the new APS "coden" DOIs
(e.g. 10.1103/25md-vv43) need a publisher check; arXiv IDs below are the reliable
handles.

**Update 2026-07-13 — 6 of these are now HELD PDFs** (each arXiv ID verified
before fetching; [bandi2025](lit/bandi2025.md) is MDPI-OA, grab from the page):
[andeweg2026](lit/andeweg2026.md), [ahern2025](lit/ahern2025.md),
[antypas2018](lit/antypas2018.md), [chevrollier2012](lit/chevrollier2012.md),
[araujo2021](lit/araujo2021.md), and [safronova2004](lit/safronova2004.md) — the
benchmark that carries the **6S dynamic polarizability**, a stronger Δα anchor for
the 6S state than safronova2006. Two IDs the compass synthesis got wrong are
QUARANTINED (do not cite): the Li dual-interrogation arXiv (real
compensation-method preprint is 2405.14281, a different paper) and `drago2026`
(2602.07161, malformed).

**Positioning this analysis (our 993 nm 5S→6S).** No other group is currently working this line: the only active
group (USAFA/Knize — `ayachitula2024`; and the earlier McLaughlin 5S–6S absolute-
energy work, *J. Phys. B*-era, VERIFY vol/year via Ayachitula's ref list) reports
**null AC-Stark and density shifts at ~6 MHz resolution** (up to 10⁴ W/cm², N =
3×10¹¹–5×10¹³ cm⁻³). Our sensitivity to the light shift and β_self is therefore new.
The **novelty to claim** is the *inversion* of lineshape asymmetry from a nuisance
into a reference-free estimator:
- **`wieman1987`** — Wieman, Noecker, Masterson, Cooper, *PRL* **58**, 1738 (1987):
  AC-Stark lineshape asymmetry in standing waves, the foundational precedent
  (treated as a distortion). **[CITE]**
- [antypas2018](lit/antypas2018.md) — the AC-Stark-asymmetry elimination
  precedent (Yb) our method inverts. **[CITE]**
- [`bruvelis2012`](lit/bruvelis2012.md) — Bruvelis, Ulmanis, Bezuglov, Miculis,
  Andreeva, Mahrov, Tretyakov & Ekers, *PRA* **86**, 012501 (2012): two-photon
  excitation in a three-level ladder gives a Voigt whose width is set **solely by
  w₀**, because wavefront-curvature broadening is *exactly compensated* by the
  longer transit of particles farther off axis — directly supports our
  w₀-as-dominant-systematic story. **[CITE]**
  *Corrected 2026-07-30: carried here as `bevilacqua2012` until then. Volume,
  page, year and physics were right; there is no Bevilacqua among the authors.
  Note also that the validation is a supersonic **Na₂ molecular beam**, not a
  vapour cell — the transfer is geometric.*

**The 778 nm 5S→5D clock frontier (the competition — all *active* AC-Stark
suppression; our passive method is the differentiator).** [FEED/CITE for §VI.D/§VII
contrast and for the future Paper A.]
- [andeweg2026](lit/andeweg2026.md) — Andeweg, Kitching, Hummon (NIST): the
  newest competitor method, active **power-modulation** AC-Stark suppression
  (×1000); contrast our passive approach against it.
- [ahern2025](lit/ahern2025.md) — Ahern et al. (Adelaide): two-color 5S–5D
  standard, 6×10⁻¹⁴/√τ, light-shift-limited.
- **`feng2026`** — Feng et al., *Opt. Lett.* **51**, 1363 (2026): 5S–5D fiber-laser
  clock, He-equilibration collisional-shift control.
- **`yudin2020`** — *PRApplied* **14**, 024001 (2020): the power-modulation
  light-shift-suppression framework behind Andeweg. **`lidou2024`** — dual-region
  interrogation, *Opt. Express* **32**, 2766 (2024) [cite the OE DOI; the compass
  artifact's arXiv:2310.10175 was WRONG — we flagged it — the related
  *compensation-method* preprint is arXiv:2405.14281, a different paper]. (With
  `gerginov2018`, `callejo2025`, `newman2021`,
  `martin2018/2019` already in §6/bib, and
  [hamilton2023](lit/hamilton2023.md)'s magic-wavelength target for the proposed
  Ti:Sapph asymmetry scan.)
- [bandi2025](lit/bandi2025.md) — comprehensive review of Rb two-photon clock
  systematics and the stability benchmarks. **[CITE]** the single best landscape
  citation.
- **`bjorkholm1976`** — *PRA* **14**, 751: two-photon lineshape with a near-resonant
  intermediate — the theory anchor for the future 6S(clean)-vs-5D(resonant) Paper C
  (intermediate detunings 75 → 1 THz; see `FUTURE_TRANSITIONS_titsapph.md`).

**Radiation-trapping updates (795 nm systematic, M7/§VI.D) — the modern Lévy-flight
lineage** beyond the Holstein/Molisch/Fioretti canon (Kaiser & Passerat de Silans):
- [chevrollier2012](lit/chevrollier2012.md) — the canonical radiation-trapping /
  Lévy-flight review. **[CITE]** framework.
- [araujo2021](lit/araujo2021.md) (Lévy flights in He-broadened hot Rb, α≈0.5),
  **`weiss2018`** (*NJP* **20**, 063024 — trapping vs subradiance), **`nunes2024`**
  (arXiv:2411.18570 — frequency-redistribution for Rb/Cs). **[FEED]** modern
  Rb-specific trapping.

**Theory anchors.** [safronova2004](lit/safronova2004.md) joins
[safronova2006](lit/safronova2006.md) and [gomez2005](lit/gomez2005.md); we note
**no dedicated modern 6S polarizability at 993 nm** — a gap Paper B can flag.

**The Cs validation triangle (intake 2026-07-30).** The Δα sign-and-magnitude
dispute will not be closed by re-deriving Rb. What *can* be done is to show the
machinery reproduces a **measured** alkali $nS\to(n{+}1)S$ differential, which
removes "the code has a global sign or normalisation error" from the table of
explanations without settling the 993 nm answer itself. Caesium supplies such a
differential to about half a percent, from two directions:

- [quirk2024](lit/quirk2024.md) — the measurement. $k = 0.72246(29)$ Hz/(V/cm)²
  at 0.04%, giving $\alpha_{7s} = 6207.9(2.4)$ against
  $\alpha_{6s} = 401.1(5)$, i.e. $\Delta\alpha({\rm Cs}\ 6s\to7s) = 5807~a_0^3$.
  Also revises $\tilde\beta = 27.043(36)~a_0^3$. **[FEED]**
- [iskrenovatchoukova2007](lit/iskrenovatchoukova2007.md) — the first-principles
  side, all-order SD with evaluated uncertainties: $\alpha_{6s} = 398.4(7)$,
  $\alpha_{7s} = 6238(41)$, $\alpha_{8s} = 38270(280)~a_0^3$. Its differential
  $5840~a_0^3$ agrees with Quirk's measured $5807$ to **0.57%**. **[FEED]**
- `sieradzan2004` — Sieradzan, Havey & Safronova, *PRA* **69**, 022502 (2004),
  "Combined experimental and theoretical study of the $6p~^2P_j \to 8s~^2S_{1/2}$
  relative transition matrix elements in atomic Cs" (record confirmed via
  Crossref 2026-07-30). The experimental check on the $8s$–$6p_j$ matrix
  elements — 17.78(7) and 24.56(10) $ea_0$ — that feed $\alpha_{8s}$.
  **Not held**: an attempt to add it on 2026-07-30 did not reach
  `PDF_papers/`. **[CITE]**

`polarizability.py` must reproduce $\alpha_{7s}$ from Cs matrix elements before
the Rb 993 nm sign is argued from it. Both anchors are **static**, so neither
constrains the 993 nm cancellation directly — they validate the machine, not the
answer.

**The Cs 6S–8S line, which is the closest analogue experiment there is.**
[lee2010](lit/lee2010.md) (Tsai/Chui, NCKU Tainan) and its sister
[lee2012](lit/lee2012.md) run a hot-cell, retro-reflected, cascade-detected
two-photon $nS\to n'S$ alkali line with laser intensity and vapour density as
independent variables, which is the experiment here, in Cs. They measure a light shift
of $-7.25(45)$ Hz/(mW/mm²) against a theoretical $-6.58$; this repository's
pinned $\Delta\alpha = 1093.0$ a.u. gives 5.12 Hz/(mW/mm²) on the transition
axis, the same order, which is a magnitude sanity check and **not** a sign test.
Their Voigt decomposition separates a power- and pressure-independent Lorentzian
(1.53 ± 0.08 MHz, an upper bound on the Cs 8S natural width) from a Gaussian that
**grows with laser power**, which they attribute to "the spatially inhomogeneous
of laser intensities". **That is our physics fitted with a symmetric shape.**
§5's novelty wording should therefore concede the *phenomenon* to `lee2010` as it
concedes asymmetry to `wieman1987`, and claim only the closed-form distribution
$f(s)\propto|s|^{n-1}$ and its cumulants — a narrower and far more defensible
claim. Two apparatus lessons transfer directly and belong in any proposal: a
**second cell at fixed intensity** makes the light shift differential, which is
exactly the failure mode that forced the M20 retraction; and a **cold finger at
10 °C under a 65 °C body** decouples vapour density from thermal velocity, the
degeneracy this campaign's temperature scan has to break by shape. **[CITE]**

**Nanofibre bridge to the nanofibre extension** (Gokhroo/Le Kien/Nic Chormaic lineage):
[gokhroo2022](lit/gokhroo2022.md) (the ONF two-peak pushing-dip analog),
`li2024perspective` (*J. Phys. Photonics* **6**,
021002, the standard ONF review), [sadeghi2026](lit/sadeghi2026.md) (ONF
delayed-feedback fluorescence, arXiv:2412.01099 — **now held and read**: the ONF
linewidth is ~16 MHz against a 5.2 MHz natural width, with Γ₀ = 8.44 ± 0.80 MHz
of non-atomic broadening, and a power-dependent shift of (0.25 ± 0.06) MHz slope
attributed to surface-shifted atoms being excited preferentially at higher
drive). The clean cell lineshape is the reference against which ONF
surface/pushing effects are read.

- [patterson2018](lit/patterson2018.md) — Patterson, Solano, Julienne, Orozco &
  Rolston, *PRA* **97**, 032509 (2018), "Spectral asymmetry of atoms in the van
  der Waals potential of an optical nanofiber". Surfaced 2026-07-30 from
  `sadeghi2026`'s ref [25], **held and read 2026-07-30**. It stands to the nanofibre extension as
  [wieman1987](lit/wieman1987.md) does to this analysis: cold Rb around a 240 nm
  nanofibre, where the van der Waals surface potential red-shifts atoms nearer
  the silica and the transmission spectrum is built as a Lorentzian of
  position-dependent centre averaged over a density-times-coupling weight — the
  same shift-distribution convolution this programme uses, with a static surface
  potential in place of the AC-Stark shift, and the quasistatic assumption stated
  outright. They quantify the asymmetry as $A = (L-R)/(L+R)$ and, like us and
  unlike [antypas2018](lit/antypas2018.md), treat it as an information channel
  rather than a defect. **So the concession §5 makes to `wieman1987` must be made
  again here, one step closer to home.** What survives it: their shift is
  *static*, so weight and shift are independent functions sharing a coordinate,
  whereas an AC-Stark shift **is** the intensity that weights the excitation —
  which is what yields the closed form $f(s)\propto|s|^{n-1}$ they have no
  analogue of. And their asymmetry is *non-monotonic* in **heating** power — the
  750 nm desorption beam that warms the fibre, scanned 0–350 µW with the
  asymmetry peaking at 0.36 near 120 µW — through a thermal bound-state
  population. **Their probe is held below a tenth of saturation and is never
  scanned**, so the two knobs must not be run together: this is a
  *cross-mechanism inference*, not a measured head-to-head. The argument is that
  a static van der Waals shift is by construction independent of probe intensity,
  so a monotone rise of asymmetry with **probe** power cannot be the van der
  Waals mechanism, a discriminating signature for the nanofibre extension to *measure*, and one
  nobody has measured yet. **[CITE]**
- **The open question it hands us, worth more than the citation.** Patterson
  measure $\Gamma_0 = 8.1(3)$ MHz — the *total* homogeneous width in their model —
  and write that they "consistently measure a 2 MHz increase from the natural
  linewidth which we do not yet understand", after excluding Doppler,
  collective/superradiant, Purcell, continuum-atom and Zeeman explanations one by
  one. (The 6.065 MHz Rb D2 natural width is supplied by us; their paper never
  states it.) Sagué *et al.* (2007) saw 6.2 MHz in Cs against 5.2 natural, i.e.
  ~1 MHz, likewise unaccounted for. **Two ONF experiments, eleven years apart,
  ~1–2 MHz of genuinely unexplained width each.**
  *A third case is a contrast, not a confirmation, and this section first got it
  wrong.* [sadeghi2026](lit/sadeghi2026.md) fit
  $W(s_0) = \Gamma\sqrt{s_0+1} + \Gamma_0$ with $\Gamma = 6.45(1.17)$ and
  $\Gamma_0 = 8.44(80)$ MHz — $\Gamma_0$ there is an **additive excess, not a
  total width**, so setting it against 5.2 MHz is a category error (at their
  $s_0 = 0.4$ the formula returns 16.1 MHz, reproducing their quoted ~16 MHz).
  Their surplus over natural is of order **10 MHz**, four to five times
  Patterson's, and they *do* attribute it. The near-equality of 8.1 and 8.44 is a
  coincidence of notation between different quantities.
  Whether the small unexplained residual and the large attributed one are the
  same physics at different scales is **OPEN**; this repository has not checked
  them against a common model. Even narrowed, it is a better premise for the nanofibre extension
  than measuring one more ONF lineshape. **[OPEN]**
- **The premise narrowed twice more on 2026-07-30, and gained a mechanism.** An
  external literature pass found no post-2018 paper explaining the residual, and
  two things that change the framing.
  *First, Sagué may not belong in the table at all.* Reportedly their model
  carries **no fitted width parameter**, so their 6.2 MHz is a model *output*
  that matched, not a residual — and they attribute it to van der Waals shift
  plus modified spontaneous emission, with a position-dependent $\gamma(r)$
  reaching **+57% at the surface**. If so the count is Patterson plus a newly
  surfaced Liu *et al.* (2024/25, ⁸⁷Rb D2, fitted 2–4 MHz residual), and the
  question sharpens usefully to *what does Patterson's model contain that
  Sagué's does not*. **REPORTED — Sagué is not held and none of this is checked
  against it.**
  *Second, and verified here in the equations:* Patterson's Eq. (10) integrates
  $\alpha(r)$, $\rho(r)$ and $\delta_{\rm vdW}(r)$ over $r$ but passes
  $\Gamma_0$ in as a **scalar**, while their own Eq. (3) defines
  $\alpha(r) = \Gamma_{\rm 1D}(r)/\Gamma_0$ — a position-dependent decay rate
  used as the detection *weight* and omitted from the *width*. An ensemble with
  a distribution of $\Gamma_{\rm 1D}(r)$ fitted by one scalar returns a width
  that is too broad, symmetric, near-Lorentzian, and independent of density,
  temperature and field — surviving every exclusion they list, because their
  Purcell argument bounds a **mean** and this is a **variance**. See
  [patterson2018](lit/patterson2018.md) for the falsification test, which is a
  refit of their published spectra and is publishable either way. **[OPEN]**
- **The contrast is already in the literature, and it settles the mechanism's
  plausibility (intake 2026-07-30).** [sague2007](lit/sague2007.md) — held and
  read — puts $\gamma(r)$ **inside** the spatial integral of its Eq. (1),
  predicts a **57% enhancement at the fibre surface**, fits with only two free
  parameters (atom number and a frequency offset, **no width parameter at all**),
  and closes its budget: its 6.2 MHz against 5.2 natural is "explained by
  surface interactions, i.e. the vdW shift ... and the modification of the
  spontaneous emission rate", the two being of "the same magnitude". Patterson,
  eleven years later in the same geometry with a *tighter* fibre, passes
  $\Gamma_0$ as a scalar and is left with 2 MHz. **So Sagué leaves the
  unexplained column** — a correction now made from the source rather than on
  report — and what remains is Patterson plus Liu *et al.*
  The two theory inputs a refit needs are
  [klimovducloy2004](lit/klimovducloy2004.md) for $\gamma_{\rm free}(r)$, now
  **held**, with its quasistatic section and Conclusion read 2026-07-31 — it
  derives analytical transition rates in the subwavelength regime with
  guided-mode contributions exponentially small, **but licenses that closed form
  only for $ka < 1/\varepsilon$** (VERIFIED, its Conclusion), which for fused
  silica is 0.473 while Patterson sits at $ka = 0.967$ and Sagué at 1.844
  (CALCULATED). Both fall in the band where that paper says guided-mode
  influence is *substantial*, which is why Sagué carries a separate
  $\gamma_{\rm guid}$. So the closed form **cannot simply be coded**; the refit
  needs his Section IV, held and unread. And, for the van
  der Waals shift near a cylinder, [frawley2012](lit/frawley2012.md) — *Phys.
  Scr.* **85**, 058103, Nic Chormaic and Minogin — which gives closed analytical
  equations for **metal and dielectric** nanocylinders in the electrostatic
  approximation, and **is held** — supplied by the experimenter on 2026-07-31
  after being named as the top outstanding want. (A claim that it "was in
  `PDF_papers/` all along" stood here briefly and was wrong: the file's birth
  time is 01:21 that night.) It replaces `boustimi2002` here: Sagué's own words are "we
  **calculated** the vdW shift", so Boustimi is a method citation and not a
  source of numbers, and both Boustimi papers work the *metallic* wire while
  these fibres are silica. Frawley factorises the answer as
  $U = -(C_3/x_0^3)\mu$; the correction $\mu$ tends to **unity** close in, where
  "the curvature of the surface is of no importance", falling below 0.75 only at
  $x_0 = R$, to "a little more than 0.5" at $x_0 = 5R$, and to about 0.2 at
  $x_0 = 100R$ (VERIFIED, body text) — so a flat-surface form is adequate near a
  nanofibre, and it is far from the surface that curvature bites. *A claim that
  a flat-surface $C_3/r^3$ **overestimates** the shift at nanofibre distances by
  about a factor of two stood in this ledger for a few hours on 2026-07-31,
  taken from a paraphrase of Frawley's abstract; it is withdrawn — the body
  says the opposite.* Note too that Frawley's own electrostatic derivation is
  licensed only for $ka < 1$, which Patterson's fibre meets marginally (0.967)
  and Sagué's fails (1.844). **[OPEN]** — the Bessel integrands must
  be read off the rendered page before coding; they do not extract reliably.
  Its **concave** counterpart [afanasiev2010](lit/afanasiev2010.md) (*PRA*
  **82**, 052903, Minogin with Afanasiev) was supplied the same day and covers
  the *hollow-core* interior in the identical factorised form: $\mu \to 1$ at the
  wall again, rising to **4** near the axis (and 2× the two-parallel-plane
  result). Together the two settle both curvatures from primary sources and
  retire the sphere→cylinder extrapolation that
  [schmidt2011](lit/schmidt2011.md) had been carrying — the cylinder figure is 4,
  not the sphere's 6. **The concave enhancement would cost a hollow-core
  geometry nothing:** it multiplies $C_3/x_0^3$ on the axis, which for bores from 250 nm
  to 22.5 µm is $10^{-4}$ to $10^{-10}$ of the near-wall value (CALCULATED).
  *Caution attached to the canonical number:* the 8.1 ± 0.3 comes from the row
  whose $\omega_0/2\pi = 5.9 \pm 0.2$ MHz is a five-fold outlier against the
  other four, and covariance between those two was not reported.
- [perrella2013](lit/perrella2013.md) — Perrella, Light, Anstie, Stace, Benabid &
  Luiten, *PRA* **87**, 013818 (2013), two-photon spectroscopy of thermal Rb in a
  hollow-core photonic-crystal fibre: 10 MHz linewidths resolving 5D₅∕₂ hyperfine
  structure, with >90% nonlinear absorption observed (and "substantial" absorption
  maintained to 9 GHz detuning — the abstract's two clauses carry different
  quantifiers). The high-resolution counterpart to [saha2010](lit/saha2010.md)
  in the same hollow-core class — but a **different fibre** (Saha's 6 µm PBG core
  against Perrella's 45 µm kagomé) and, more to the point, a **different
  excitation**: two-colour 780 + 776 nm here against Saha's degenerate 778 nm.

  **The geometry is now known, and it is not what this entry said (2026-07-31).**
  The paper is paywalled, but the first author's open-access UWA PhD thesis
  reprints it, and states the setup outright: a **kagomé HC-PCF of 45 µm core
  diameter**, 40 cm long, at **90 °C**, excited **two-colour at 780 + 776 nm**.
  So the mode radius is ~15 µm, not the few microns this entry twice inferred by
  reading the geometry backwards out of the 10 MHz. Through the repo's own
  `transit_fwhm_from_w0`, **transit supplies only 3–4 MHz of their 10 MHz**
  (3.98 MHz at $w_0 = 14.6$ µm, 3.69 at 15.8). Perrella is therefore **not an
  example of a transit-limited hollow-core line**, and cannot be cited as one.
  The thesis names a likely source of the remainder: the fibre was curved, and
  that with the large core "resulted in coupling to higher-order transverse
  optical modes". Pressure broadening they put at ≈12 kHz.

  **That correction makes this paper *more* useful, not less.** Its ~15 µm mode
  radius is close to the 18 µm quoted for this programme's own CRYST³ hollow core
  at Bologna — so it is the **closest published analogue to the fibre actually
  contemplated**, far closer than Saha's 6 µm Crystal Fiber AIR-6-800 (~28 MHz)
  or Slepkov's $10^{-7}$ cm² area (~1.8 µm, ~33 MHz). The trade is now: transit
  at this programme's contemplated core costs **~3.1–4.3 MHz** across the
  thesis's ideal, target and measured waists
  against **1.18 MHz** for the free-space $w_0 = 50$ µm — a factor of 3–4, not
  the 15–30× that the tighter published cores would impose — but Perrella's
  total of 10 MHz is a warning that **transit is not the whole budget in a real
  large-core fibre**, and higher-order-mode coupling is the term to design
  against. **The 18 µm is no longer unsourced (2026-07-31):** a held master's
  thesis on the apparatus (Nasoni 2026, co-supervised by the experimenter) gives
  it as an **injection beam waist**, i.e. a **radius**, and it is *measured* —
  $w_x = 17.1 \pm 0.7$ µm and $w_y = 19.3 \pm 0.4$ µm, slightly elliptical from
  AOM distortion, against an ideal thin-lens 13.6 ± 0.1 µm and an 18 µm design
  target. **The caveat is the beam, not the number: it is the 1064 nm
  optical-dipole-trap beam, not a two-photon probe**, and a hollow-core mode is
  wavelength-dependent, so using it as the transit waist for a 778 nm line is an
  assumption rather than a measurement of the relevant mode. Taken at face value
  the measured pair gives 3.1–3.4 MHz. The source is an unpublished thesis, so
  the experimenter should confirm before any published claim rests on it.
  The qualitative trade is unaffected: $w_0$ becomes a characterised component
  property rather than a daily alignment. VERIFIED via the thesis. **[CITE]**

**[FEED] Pennetta et al. 2026** ([pennetta2026](lit/pennetta2026.md)) — the
nearest-platform result to the nanofibre extension, feeding two of its pillars. NO committed number
moved. Two details beyond the lit-file summary: radial trap ~7 kHz, atom ~280 nm
from the surface; the Ramsey/spin-echo coherence times are records for the
platform. The two feeds:
- **It puts quantified atom–surface content on the near-surface potential** —
  Casimir–Polder plus surface-charge electrostatics — which is exactly what
  `gokhroo2022` left at the hypothesis stage (its dip has "no Casimir-Polder or
  van der Waals content at all"): a concrete ingredient for any nanofibre
  near-surface *lineshape* model.
- **Its coherence gain is a suppression of the trapping-light differential light
  shift.** The paper states the decoherence it beats "arises from
  motional-state-dependent differential light shifts … proportional to the
  intensity of the trapping fields," cured by holding atoms in low-light regions
  a real-world confirmation, on the nanofibre platform itself, that the
  **inhomogeneous/differential light shift is the coherence-limiting systematic
  in guided-atom systems**, which is the premise of our light-shift-distribution
  method (THEORY_NOTE §3), the M16 magic-wavelength toolkit, and the guided-mode
  framing of the trapped-platform extensions.

Platform caveats: Cs not Rb, a D2 hyperfine qubit not the
5S–6S two-photon line, a 450 nm fibre not the OIST 650 nm — the *physics* (surface
forces; differential-light-shift dephasing) transfers, the numbers do not.

**[FEED] Pache et al. 2026** ([pache2026](lit/pache2026.md)) — the same group's
companion, on the loading and cooling toolkit for this platform, and a direct feed
to the EIT-cooling / atom-source thread; NO committed number moved. Why it feeds us
beyond the lit-file summary: it again names the **residual differential light
shift of the trapping fields** as the limiting imperfection — the recurring
guided-mode theme. Cs / D2 again: the physics transfers, the numbers do not.

**Prior-art audit on the pushing dip (2026-07-16).** Because a near-surface
lineshape is the natural nanofibre direction, we checked whether anyone has since
modelled the `gokhroo2022` dip. Crossref/OpenAlex list **6 citing works, 4 unique**
(two are preprint/published pairs), and **none models the dip**: Kestler *et al.*
(UCSD, Sr state-insensitive ONF trap — unrelated); Vylegzhanin *et al.* 2023
(*Optica Quantum*, ONF Rydberg excitation); `li2024perspective`; and Vylegzhanin
*et al.* 2025 (*NJP*, fictitious-field trap). Fam Le Kien — the theorist on the
paper, and the person most likely to complete it — has published no follow-up; his
ONF force work predates it (2018 and earlier). Two facts sharpen what is and is
not open:

- **The demonstration is published; the model is not.** `li2024perspective` — the
  group's own review — cites `gokhroo2022` exactly once in its body, for the
  *capability*: "the nanofibre-based multilevel cascade atomic system allows us to
  observe two-photon guided-mode coupled excitation of the 5S₁∕₂–6S₁∕₂ transition
  in ⁸⁷Rb". It never discusses the dip, and never calls it solved or open.
- **`gokhroo2022` itself stops at a hypothesis** ("We speculate that … resonance
  scattering induced pushing … becomes the dominant effect"), compares dip
  positions with dressed-state resonances, and contains no Casimir-Polder or van
  der Waals content at all.

**Scope caveat:** the dip is a
*density-depletion* effect (atoms pushed out of the bright region), whereas the
ramp machinery describes the *distribution of light shifts* in an inhomogeneous
field. The ramp is at most one ingredient of a quantitative treatment — a full
model also needs the force/density dynamics. "Nobody has modelled it" is
established; "our framework is the missing model" is not.

## 9. Deep-search intake (2026-07-17) — verified finds + the ONF community map

A systematic sweep for relevant work not already held; only verified-real finds are
given citekeys.

**Cascade / IR detection to beat radiation trapping — ESTABLISHED prior art (now
cited in PLAN §8.4a; corrects our 1.3 µm exploit's novelty framing):**
- **[Hassanin et al. 2023](lit/hassanin2023.md)** — the direct precedent for our
  1.3 µm (6S→5P) trapping-free channel: the reabsorption-free 5D→5P cascade lets
  the sibling 5S–5D line be probed at high density, enabling collisional-
  broadening/energy-transfer studies. [CITE]
- **[Beard et al. 2024](lit/beard2024.md)** — a second cascade-detection
  precedent (776 nm 5D→6P fluorescence). [CITE]

**Near-surface Casimir–Polder shift read FROM a lineshape, the template for the nanofibre extension §IV:**
- **[Ton, Kestler, Steck & Barreiro 2026](lit/ton2026.md)** — the state-of-the-art
  template for extracting a surface shift from the line; D. A. Steck (our
  constants lineage) is a co-author. [CITE. The model template for the nanofibre extension's
  surface term]

**Sibling cold-atom two-photon clock (ladder / magic-λ context):**
- **[Duspayev, Owens, Dash & Raithel 2024](lit/duspayev2024.md)** — a direct
  sibling to our ladder (the 4D_J = 1033 nm rung) and an independent magic-λ
  determination to cross-check M16. [FEED]

**Polarizability validation source:**
- **[Safronova & Safronova 2011](lit/safronovaSS2011.md)** — the independent
  published source to validate the M16 7S static (~3.2×10⁴ a.u.) we could not
  otherwise anchor. [FEED — pull the 7S/5D values]

**Self-calibrated frequency tracking (ruler-method context):**
- **[Yang et al. 2025](lit/yang2025.md)** — the modern frontier of the
  "internal ruler tracks a drifting axis" idea our EOM ruler embodies.
  [FEED — Intro/method context]

**Verified and folded in (2026-07-18) — the near-surface CP-lineshape cluster + the
7S cascade study (all PDFs held):**
- **[Dutta et al. 2025](lit/dutta2025.md)** — the direct template for reading
  the near-surface shift as a thermal-averaged distribution in the nanofibre extension §IV. [CITE]
- **[Dutta et al. 2024](lit/dutta2024.md)** — higher-order CP corrections at
  close range: the background for the nanofibre extension's near-surface term. [FEED]
- **[Sargsyan, Momier & Sarkisyan 2025](lit/sargsyan2025.md)** — the
  experimental analogue of extracting a surface shift from the line. [CITE]
- **[Piotrowski, Bach, Vera Paz, Schneeweiss & Rauschenbeutel 2026](lit/piotrowski2026.md)**
  A nanofibre feasibility bound on the probe window and power. [CITE]
- **[Wang, Cao, Yuan, Wang, Xiao & Jia 2025](lit/wang2025.md)** — directly on
  our 5S–7S ladder (the 741/728 nm channels set the ladder magic wavelength)
  and a multi-channel-detection precedent for the amplitude work. [CITE]

**Still to verify:** Sargsyan/Sarkisyan 2026 (arXiv:2601.04661, a second nanocell
surface-shift paper) and Obaze et al. 2025 (Photonics **12**, 513, a second 778 nm
clock review). **Quarantined (do NOT cite): arXiv:2602.07161** (malformed, re-surfaced).

**The ONF community map (why the nearest-platform refs cluster here).** The two poles
of the optical-nanofibre cold-atom field are the **Rauschenbeutel group** (Humboldt
Berlin; `pennetta2026`, `pache2026`) and the **Nic Chormaic group** (OIST; `nieddu2019`,
`rajasree2020`, `gokhroo2022`, our own provenance and the nanofibre extension's platform); they
co-organise the ONNA (Optical Nanofibre Applications) conference series. So the newest
nearest-platform work is from the nanofibre community, and engaging it well is both good
scholarship and the natural way this program is read by that community.
