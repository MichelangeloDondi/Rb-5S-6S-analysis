# Literature ledger

Every external number and every priority claim this analysis leans on, with its
provenance, so that no novelty sentence is written from memory. The decision
this file changes is what an introduction on the 993 nm 5S–6S line may claim,
and whom it must delineate against. Section 5 is the answer and the rest is the
evidence for it.

**The question.** What may a paper on this line claim as new, and whose work
must it position itself against?
**Takes.** Nothing.
**Gives.** Every external number this analysis leans on with its source, and
the delineation from the nearest prior art, which is closer than it first
looked.
**Skip if.** You are not writing or refereeing a claim of priority. Section 5
is the answer if you want only that.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Two clicks to the status of any statement. The map below routes to a section,
and the section names the paper with what it costs or supports.
[`LITERATURE_INDEX.md`](LITERATURE_INDEX.md) then gives every paper's status,
routing and locus in one table, each row linking to its note in
[`lit/`](lit/), where the full bibliographic record lives. The notes are the
single source of truth: the index and [`references.bib`](references.bib) are
generated from them by `scripts/build_lit_index.py`.

### Status vocabulary

One vocabulary, used here and in the index. A tag is a statement about what has
been done to a paper, never about how good it is.

| tag | meaning |
|---|---|
| VERIFIED | we read the source itself |
| REPORTED | a literature-scout summary we have not yet read in full. Cite nothing REPORTED until it is upgraded |
| held | the PDF is on disk. Held and unread is still REPORTED |
| to-pull | wanted, not obtained. The obstacle is named where the entry appears |
| [CITE] | belongs in the reference list of a paper from this programme |
| [FEED] | shapes an argument, a method or a figure without needing a citation |
| [OPEN] | a question this ledger has not settled, with the work that would settle it |
| QUARANTINED | an identifier that must not be used, kept visible so it cannot come back |

### Where things are

| section | what it settles |
|---|---|
| [1. Nearest prior art](#1-nearest-prior-art) | the three papers a referee reaches for first, each with the axis that separates it |
| [2. Collision-rate series](#2-collision-rate-series) | what β_self(6S) should be, and why the dataset's bound cannot measure it |
| [3. Transit-time lineshape](#3-transit-time-lineshape) | that the transit kernel is a published analytic form, not an assumption |
| [4. Anchors still at REPORTED](#4-anchors-still-at-reported-status) | what is quoted from a summary and must be read before it is cited |
| [5. What may be claimed](#5-what-may-be-claimed-and-what-may-not) | the novelty law: the concessions, the survivors, and the searches that found nothing |
| [6. Prior work on this line](#6-prior-work-on-this-line-5s6s-993-nm) | the two lineages that measured 5S–6S before us, OIST and USAFA |
| [7. Method anchors](#7-method-anchors) | the ruler, the trapping, the detection channels, the reference standards |
| [8. The 2024–2026 field](#8-the-20242026-field) | where a vapour-cell paper from here sits among the 778 nm clocks |
| [9. The nanofibre extension](#9-the-nanofibre-extension-and-the-onf-community-map) | the literature of the proposed extension, for which no data exist |

## 1. Nearest prior art

**[Stalnaker et al., Phys. Rev. A 73, 043416 (2006)](lit/stalnaker2006.md)**
(arXiv:physics/0512111). VERIFIED, lineage Wieman et al., PRL 58, 1738
(1987). One-photon forbidden Stark-induced transition (Yb 408 nm) in a
collimated beam, numerically fit to α = −0.312(34) Hz/(V/cm)². So the
asymmetry-as-observable idea exists in prior art, and the claim here must be
narrower than "first use of the asymmetry".

| Axis | Stalnaker 2006 | This work |
|---|---|---|
| Transition | 1-photon Stark-induced (signal ∝ I) | 2-photon (signal ∝ I²) |
| Ensemble | collimated beam, velocity-selective | thermal vapor cell |
| Regime | **fringe-resolved**: FM index ξ/Ω ≳ 1, Bessel sidebands, sub-Doppler features | **fringe-averaged**: ξ/Ω ~ 10⁻³, atoms see the time-averaged envelope |
| Lineshape | numerical Bloch, per-condition | **closed-form** shift density f(s) ∝ \|s\| on [−S₀,0] |
| Extraction | full-shape fit; needs β, cavity field, velocity model, per-scan free center | **closed-form ramp** fit with a per-trace free center; S₀ is read from the drift-invariant shape asymmetry, not the centre |
| Saturation | saturating + hole-burning entangled with the asymmetry | unsaturated throughout (C3: amplitude ∝ P², slopes 1.83–2.12) |

Both regimes reduce to the same quasi-static law: signal weight ∝ Iⁿ over a
Gaussian envelope gives dA ∝ dI/I, hence **f(s) ∝ |s|^(n−1)**, uniform for
their n = 1, triangular for our n = 2, and the same dA ∝ dI/I holds for a thin
evanescent shell, the geometry-independence bridge to the nanofibre extension.
Calculated.

Their FM framework (Sec. IV/Fig. 6) settles our ⟨E²⟩ convention: at
λ/2 ≈ 0.50 µm fringes and axial thermal speed ~280 m/s, Ω/2π ≈ 0.56 GHz against
ξ = S₀ ≲ 1 MHz gives modulation index ξ/Ω ≲ 2×10⁻³, so the shift is set by the
fringe-averaged intensity with no coherent ×2 enhancement. The fringe-resolved
tail is not benign, though: near-transverse atoms sample the node/antinode
arcsine, and because the fringe multiplies the shift it suppresses the ramp
skew, κ₃ → S₀³(1/135 − f_res/10) at ρ=1. As a fraction of the intrinsic +0.566
triangle skew that is negligible at w₀=64 µm (~7–14% of an
already-below-noise skew) but ~26–28% at w₀=16 µm, additive to the
beam-divergence correction (`rb5s6s/fringe_tail.py`). Calculated.

**[Hamilton et al., Phys. Rev. Applied 19, 054059 (2023)](lit/hamilton2023.md)**
(arXiv:2212.10743). VERIFIED. The nearest prior art for our specific
construction: a retro-reflected Rb-87 vapour two-photon line (5S→5D,
two-colour 780+776 nm) building the identical Iⁿ·(linear shift)·(r dr)
focus-average integral we reduce to the wedge. What is genuinely not in
Hamilton: they collapse the integral to a single spatially-averaged shift
without ever keeping the shift distribution, their signal is a two-colour
product rather than our degenerate single-colour I², and they never treat the
axial standing-wave fringes at all. Must be delineated in the introduction,
since a referee who knows Hamilton will see the integral parallel
immediately.

**Dounas-Frazer, Tsigutkin, Family, Budker, Phys. Rev. A 82, 062507 (2010)**
(arXiv:1009.5952). VERIFIED online, PDF to-pull. Extends "polarizability from
a standing-wave lineshape" to Yb 5d6s ³D₁, the same fringe-resolved
atomic-beam family as Stalnaker/Wieman, reinforcing that our novelty is
narrowed to the fringe-averaged closed form and the drift-immune moment.

## 2. Collision-rate series

[Zameroski et al., J. Phys. B 47, 225205 (2014)](lit/zameroski2014.md),
full text HELD and read 2026-07-27, correcting this entry's central number.
Zameroski measures the 5S→7S **self-BROADENING** rate directly:
**129 ± 11 kHz/mTorr**, i.e. **5.39 ± 0.46 kHz per 10¹² cm⁻³** at their cell
temperature. It is the only measured self-broadening rate for an nS state in Rb, and
exactly the observable β_self is. Their 7S self-*shift* "could not be extracted
from the experimental data". The −17.82(81) kHz/mTorr this entry previously
attributed to them is **Morzyński 2013's**, on the laser axis (Zameroski
restates it on the transition axis as −35.6 ± 1.6). Scaling the measured 7S
broadening to 6S by the computed C₆ ratio (M18, 0.313) gives the expected
**β_self(6S) = 3.4 ± 0.3 kHz per 10¹² cm⁻³**, anchored on a measurement, with
the suspect impact prefactor cancelling in the ratio. Derivation in the lit
file and in `rb5s6s/vanderwaals.beta_self_anchored`. The ratio is of van der
Waals *differences*, C₆(5S+nS) − C₆(5S+5S), because the impact phase is set by
the difference between the two levels' interactions with the perturber. That
correction landed 2026-08-05 and moved the anchor from 3.53 to 3.38 kHz per
10¹² cm⁻³, inside the quoted error. See
[the difference-potential note](notes/vdw_difference_potential_and_4d_channel.md).

Consequences (calibration against the theoretical expectation):
- The dataset's bound (0.03–0.05 MHz per 10¹² cm⁻³, the four-point
  70/90/110/130 °C headline since 2026-08-02, and 0.2–0.4 MHz on the
  earlier three-point 70–110 °C headline) sits **8–15× above
  the expected value**, consistent but not constraining. Paper wording must
  say exactly that. The value of the bound is methodological, since it
  quantifies the drift confound rather than constraining β.
- **Even the full 70–130 °C lever in the dataset cannot measure the expected β.**
  The lever is ΔN = 2.9×10¹³ cm⁻³ and the swing it buys is
  β_self·ΔN = 0.10 MHz on a 5.2 MHz line, which is why the bound sits an order
  of magnitude above the expectation rather than on it. A real measurement
  needs **150–170 °C points**, where N = 0.85–2.2×10¹⁴ cm⁻³ and β_self·N runs
  0.29–0.74 MHz. That is a fixed-lock-session shot-list change, subject to the
  cell and oven limits. Trapping grows there, and it moves amplitude rather
  than width.
  *These four numbers were recomputed 2026-08-05 from
  `rb5s6s.density.number_density_cm3` and
  `rb5s6s.vanderwaals.beta_self_anchored`. The previous set (Δγ ≈ 20 kHz,
  0.07–0.25 MHz) had been evaluated at the pre-anchor expectation of ~1 kHz per
  10¹² cm⁻³ and was stale by the factor 3.4 the Zameroski anchoring introduced.
  The conclusion is unchanged in both.*

**The theory behind the expectation.** Four questions a referee asks about a
self-broadening number, and the source that answers each.
- *Why the S→S self term is small, which is the physics behind an expectation
  of a few kHz rather than tens.*
  The 5S and 6S are both S states, so the 6S–5S pair has **no resonance
  dipole–dipole (C₃) self-broadening**. The self term is van-der-Waals (C₆),
  which is why it sits far below the resonance lines. [Sautenkov et al.
  2026](lit/sautenkov2026.md) makes the contrast concrete via their Rb D2
  resonance-line self-broadening decomposition. **[FEED]** for the
  resonance-vs-vdW contrast in §vi.A. Their static and collision-width split
  mirrors our transit(static-ish)/γ_coll(collision) decomposition.
- *Isotope effect on β (why β₈₅ = β₈₇ matches the theoretical prediction).* [Bala
  et al. 2026](lit/bala2026.md) give the theoretical isotope-dependence of
  collisional widths and shifts from reduced mass, C₆ and scattering length.
  In the thermal impact regime this predicts a negligible width isotope-effect,
  so our measured β₈₅ = β₈₇ null is the physically expected result.
  **[FEED]** for the isotope-null framing (their Hg–Rb ultracold system is a
  different regime, so cite the framework and not the numbers).
- *Impact-broadening theory lineage.* [Lewis 1980](lit/lewis1980.md)
  (*Phys. Rep.* **58**, 1–71) is now held and read in full 2026-08-03, no
  longer paywalled. It is the primary source for the (C₆/ħ)^0.4 v^0.6 scalar
  phase-shift cross-section `vanderwaals.beta_self_vdw` specialises (his eq.
  4.15–4.18, n=6). Table 4.1 also prints two n=6-specific, potential-free
  checks (width/shift ratio 2γ/β = 2.75, temperature exponent α = 0.300):
  see §2's β_self discussion and `docs/PLAN.md` §7 for what we do with them.
  Allard & Kielkopf 1982 (RMP 54, 1103) remains the companion review (still
  paywalled). The Allard–Kielkopf lineage's recent [Spiegelman, Allard &
  Kielkopf 2022](lit/spiegelman2022.md) is a **[FEED]** pointer to the
  quasistatic/satellite regime our low-density impact-regime Lorentzian
  assumption sits opposite to.
- *Why γ_coll is linear in N at all.* [Baranger 1958](lit/baranger1958.md) is
  the impact-theory result `methods/02` invokes. When collisions are on average
  weak and well separated in time the line is Lorentzian, and for an isolated
  nondegenerate line the width is w = (1/2)·n·v·σ, explicitly linear in
  perturber density. It does not supply the step from C₆ to σ, which is the
  separately flagged Lindholm-Foley prefactor in M18. **[CITE]**

### 2a. Calibration comparison, measured relatives of the bound

This table lives here rather than in `methods/02_the_lineshape.md` because it
compares external measurements against each other, not a step in this
repository's own derivation. Every number is read from the cited note, not
recomputed here.

| Source | Transition | Measured coefficient | Status | Comparability |
|---|---|---|---|---|
| [Zameroski 2014](lit/zameroski2014.md) | Rb 5S→7S (self) | 129 ± 11 kHz/mTorr = 5.39 ± 0.46 kHz per 10¹² cm⁻³ | VERIFIED | one state above the 6S pair studied here, C₆-scaled to the β_self(6S) anchor of 3.4 ± 0.3 kHz per 10¹² cm⁻³ used throughout this ledger |
| [Rahaman & Dutta 2022](lit/rahaman2022.md) | Cs 6S→7d₃/₂ (self) | −32.6 ± 2.0 kHz/mTorr collisional shift | VERIFIED | different alkali and a d state rather than an S–S pair, but the same two-photon vapour-cell class and the same convention as this work |
| [Lee et al. 2010](lit/lee2010.md) | Cs 6S→8S | −7.25 ± 0.45 Hz/(mW/mm²) light shift | VERIFIED | an AC-Stark coefficient, not a collisional one, kept here because it is the closest analogue experiment there is, the same retro-reflected two-photon vapour-cell architecture as this work |
| Lee et al., *J. Phys. B* (2010, the sibling to lee2010, not yet held) | Cs 6S→8S (self) | −588 ± 387 Hz/mPa pressure shift | REPORTED, abstract only | the direct collisional analogue to β_self, same group and line as lee2010, cite nothing further from it until the full text is read |
| [Weller et al. 2011](lit/weller2011.md) | Rb 5S→5P₁/₂ (D1, self) | (0.69 ± 0.04)×10⁻⁷ Hz cm³ = 69 kHz per 10¹² cm⁻³ | VERIFIED | resonant dipole–dipole on an allowed line, the largest self-broadening mechanism there is, so a ceiling rather than an estimate for an S–S pair |
| [Orson et al. 2021](lit/orson2021.md) | Rb 5S→6S (this exact transition) | null, no AC-Stark or density shift at 6 MHz resolution, N = 3×10¹¹–5×10¹³ cm⁻³ | VERIFIED | the only prior measurement attempt on this line, three orders of magnitude coarser than the bound below |
| This work | Rb 5S→6S (self) | 0.03–0.05 MHz per 10¹² cm⁻³ bound, four-point 70–130 °C dataset | BOUND, not a measurement | 8–15× above the 3.4 ± 0.3 kHz per 10¹² cm⁻³ expectation, consistent but not constraining |

## 3. Transit-time lineshape

Our transit kernel (lineshape.two_sided_exponential, the exp(−|ν|/b) that
convolves with the natural Lorentzian) follows the established treatment. It
is the established Doppler-free two-photon transit-time lineshape. Chain:

- [Bordé, C. R. Acad. Sci. Paris B 282, 341 (1976)](lit/borde1976.md), the
  original, general two-photon transit-time derivation, to be cited as the
  primary general treatment only. Citation from search cross-refs, to-pull (French,
  likely no open PDF).
- [Biraben, Bassini & Cagnac, J. Phys. (Paris) 40, 445–455 (1979)](lit/biraben1979.md)
  gives the canonical result: the finite-transit Doppler-free two-photon line is
  **exactly a Lorentzian ⊗ two-sided-exponential** ("double-exponential
  meeting at a cusp"). This is our model. Open access (hal jpa-00209125,
  access-gated to WebFetch but bibliographic data + the key "Lorentzian
  convolved with double-exponential" result VERIFIED via multiple search
  cross-refs 2026-07-12. Read the hal PDF to upgrade to fully VERIFIED).
- [K. K. Lehmann (sole author), J. Chem. Phys. 154, 104105 (2021),
  doi:10.1063/5.0040868](lit/lehmann2021.md), the "Lehmann lineshape"
  (README §2.5): modern closed analytic form in the transit-time limit for a
  TEM00 standing wave, simpler than Bordé's general case, with γ₀(T) ∝ √T
  matching our √T scaling law (transit_fwhm_at_T). Title/journal/vol/year/DOI
  and functional form VERIFIED via search cross-refs. PDF at
  par.nsf.gov/servlets/purl/10477667 (socket-hung on WebFetch, retry to
  fully verify and pull the exact γ₀(w₀,T) prefactor).

This upgrades the transit model from "assumed shape" to "literature-standard
analytic form," and makes the M8 Voigt-vs-Lehmann BIC test Gaussian-core
(Voigt) against the BBC-1979 cusp, a test between two *published* forms. Our
M9 Monte-Carlo then refines the BBC idealization for our exact 3D-mb + w(z) +
I² + collection conditions, finding the real kernel slightly more cusped
(excess kurtosis ~4.6). To-do before submission: pull the exact γ₀(w₀,T)
prefactor from Lehmann so the transit width is an absolute prediction, not a
placeholder.

## 4. Anchors still at REPORTED status

Everything quoted in this repository from a summary rather than from the paper,
in one place, so that no argument leans on one by accident. Nothing here may be
cited until it is read. Where the obstacle is known it is named.

- **Cheng-group, Cs 6S–8S "effects of light".** Lorentzian width constant near
  1.51 MHz while the Gaussian grows with intensity, which is the light-shift
  distribution absorbed into a symmetric second moment. Pull the full text
  before citing.
- **Cs 6S–6D (2018).** A 40 µm waist gives significant transit broadening, and
  scaling by v/w₀ puts their transit at about 0.6 times ours, consistent with
  the 1.87 MHz at 32 µm computed here. The scaling is calculated, the citation
  itself is not yet pinned.
- **Taiwan comb work, Opt. Lett. 30, 842 (2005) and successors.** 5S→7S
  absolute frequency, with Stark and collisional effects suppressed as
  systematics rather than measured.
- **Weber & Niemax, Z. Phys. A 307, 13 (1982),** the Rb nS and nD
  self-broadening series. To-pull. It is the n-scaling anchor that would make
  "6S completes the series" quotable, so §2 leans on its existence and on
  nothing further.

## 5. What may be claimed, and what may not

This is the novelty law of the programme. The four claims below are what a paper
from here may assert, followed by the list of what it may not. Each concession
has its own subsection, and they are placed in the order the argument runs
rather than in the order they were found:

- **[5.1](#51-narrowed-by-the-adversarial-audit-2026-07-26)** the precedents an
  external audit surfaced, which cost the first version of claim 1.
- **[5.2a](#52a-the-concession-runs-to-1980-and-the-closed-form-is-not-new-either)**
  the 1980 review that replaces even what 5.1 left standing. This is the
  binding precedent, and the later word on claim 1.
- **[5.3](#53-the-nearest-analogue-experiment-and-what-it-costs-claim-1)** the
  closest published experiment, which owns the phenomenon.
- **[5.2](#52-negative-searches-which-are-what-defend-the-rest)** the searches
  that found nothing, which is what defends the rest.

The subsection labels are cited from other documents and are therefore fixed.
A number here is an identifier, not a position.

1. **Narrowed 2026-07-30, and much narrower than it was. Read §5.2a first.**
   The old wording claimed the closed-form triangular ramp f(s) ∝ |s| and the
   |s|^(n−1) signal-exponent law as new. **They are not.** Both reduce exactly
   to Eq. (5.3) of [delone1980](lit/delone1980.md), a 1980 review, once the
   geometric P(I) ∝ 1/I of a Gaussian beam is substituted, verified against the
   shipped `stark_ramp` to 7×10⁻¹².
   What is claimable is the *evaluation and its consequences*, not the relation:
   **(a)** identifying that for a focused beam the shift distribution is fixed by
   geometry rather than by laser statistics, so Delone's integral, which they
   could only leave formal, P being their unknown, closes.
   **(b)** the resulting **analytic cumulants** on bounded support, in particular
   the intrinsic g₁ = +0.566 at n = 2, which is a number and not a fit.
   **(c)** the fringe-averaged treatment and the M19 result that a retro standing
   wave does not move the mean.
   **(d)** the evanescent-geometry invariance of the dA ∝ dI/I step (the nanofibre extension
   bridge), which Delone have no occasion to consider.
   Stalnaker remains distinct on other axes (numerical, n = 1, fringe-resolved),
   but he is no longer the binding precedent for this claim. Delone is.
2. **The asymmetry channel, claimed for specificity rather than sensitivity.**
   Narrowed 2026-07-30 twice over: first because
   [delone1980](lit/delone1980.md) is closer here than Stalnaker, then because
   "drift-immune" named only half the argument.
   *What is conceded.* Delone frame the lineshape as a read-out channel,
   twice, explicitly: "one can reconstruct the distribution P(F) from this
   relationship". Using a lineshape to read a shift distribution is theirs.
   *What is claimed, and it is two separate properties.* **(i) Translation
   immunity:** the ramp's first-order effect is a centroid pull, which a
   per-scan free centre absorbs, so in a drifted dataset the pull is degenerate
   with the drift. The asymmetry is not a translation and survives. That is the
   response to an unstable reference, a problem Delone do not have, and one
   precision groups solved the other way (Stalnaker fit full shapes against a
   good reference, others suppressed the shift).
   **(ii) Component specificity, which is the stronger half.** Every other
   factor in the model core (the natural and collisional Lorentzian, the laser
   kernel, the transit kernel) is **symmetric by construction**, and a
   symmetric factor cannot produce asymmetry at any width. The ramp is the only
   asymmetric factor, so the fitted asymmetry does **not** exchange against
   $\Gamma_{\rm nat}$, $\gamma_{\rm coll}$, $\sigma_{\rm laser}$ or the
   transit width, the four-way degeneracy that dominates the width channel.
   The single remaining exposure is an *asymmetric* misspecification of the
   core, which is checkable by BIC and the M8 cusp fit. See
   [THEORY_NOTE](THEORY_NOTE.md) §3.
   *And the width channel is not a weaker alternative. It is blind.* At 225 mW
   and the measured $w_0 = 64$ µm the ramp kernel is 0.20 MHz FWHM, which added
   in quadrature to the observed 5.2 MHz line is **0.004 MHz**, a part in
   1400. No width measurement reaches this signal at any precision.
   The same arithmetic settles a loose end in [lee2010](lit/lee2010.md): their
   power-dependent Gaussian growth of ~1.9 MHz is **4–9× larger** than the ramp
   their own measured light-shift coefficient can produce, so the intensity
   inhomogeneity they name (tentatively, "possibly", against velocity-dependent
   collisions as the alternative) is probably not its dominant cause.
   Preliminary: the span covers the retro and transition-vs-laser-axis
   conventions their text leaves open. **[OPEN]**
3. **β_self(6S)**: completes the measured 5D/7S self-rate series, a
   modest addition to the measured series rather than a headline result. In the dataset it is a bound 8–15×
   above expectation (four-point, 2026-08-02, was 57–113× on the earlier
   three-point construction). A measurement requires the high-T extension.
4. **EOM-comb-in-fine-scan** frequency axis (0.042524(51) MHz/ms laser-axis,
   per-block).

Not claimable: "asymmetric lineshapes from distributed AC-Stark are new"
(Wieman 1987 / Stalnaker 2006 own it), "first extraction of a
polarizability from the asymmetry" (Stalnaker did exactly that, Eq. 45), or,
both added 2026-07-30, **that intensity-inhomogeneity broadening of a two-photon
alkali line in a hot cell is a new observation** ([lee2010](lit/lee2010.md) owns
it, see §5.3), or **that reading a lineshape as a map of the underlying
distribution of AC-Stark shifts is a new frame**.

> **The mapping idea is 1992 at the latest, and for a two-photon transition.**
> [camparo1992](lit/camparo1992.md) §3:
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
> analytic cumulants. **The claim is the closed form and its cumulants, never
> the mapping, never the phenomenon.**
>
> Camparo attributes the mapping to Delone, Kovarskii, Masalov & Perel'man,
> *Sov. Phys. Usp.* **23**, 472 (1980). **That review is now held and read, and
> it is worse than the attribution suggested. See §5.2a.**

> **The concession stands, and it can be narrowed, but not yet.**
> [`wieman1987`](lit/wieman1987.md) has a note and a full record: *Asymmetric
> line shapes for weak transitions in strong standing-wave fields*, Wieman,
> Noecker, Masterson & Cooper, *Phys. Rev. Lett.* **58**, 1738 (1987),
> doi:10.1103/PhysRevLett.58.1738. It is **REPORTED, not VERIFIED**: the abstract
> and the record were read from the publisher, and the physics from the
> introduction of [`stalnaker2006`](lit/stalnaker2006.md), held, read, and
> self-described as generalising it, but the paper itself is 1987, predates
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
> $f(s)\propto|s|^{n-1}$, so $n=1$ (the case it already names as "a
> Stark-induced forbidden line") is the **uniform** distribution with
> $\kappa_3 = 0$, exactly zero skew. The triangular ramp and its $+0.566$ cannot
> be Wieman's effect. Theirs is the standing wave's node structure crossed with
> velocity, ours the $I^2$ weighting over a transverse Gaussian, with the
> standing wave shown not to move the mean at all (M19).
>
> The delineation is therefore left **conceded in general and narrowed in the
> note, not here**. Narrowing a priority claim on a paper nobody has read is the
> error this repository has spent the week correcting. Read the full text before
> the introduction here. The three things to check are listed at the end of the
> note.

### 5.1 Narrowed by the adversarial audit, 2026-07-26

An external deep-search audit found **two further precedents, both now read
here**, and claim 1 above had to give ground twice:

- [slepkov2010](lit/slepkov2010.md), Rb in a hollow-core fibre. Simulates the
  AC-Stark-shifted line through a Gaussian-core guided mode, and "the nonuniformity
  of the core mode is also seen to broaden and to steepen the line toward
  higher frequencies", and the data are fit by that simulated non-uniform-mode
  lineshape in preference to a flat-top model. **Keeping the distribution is
  not new**, and it has been done in a guided geometry.
- [wall2014](lit/wall2014.md), helium Rydberg states, and the stronger
  precedent of the two: it is **single-colour two-photon**, so the I²
  weighting is present too, alongside the "bunch up close to the unperturbed
  transition frequency" density-of-states argument. **The I² weighting is not
  new either.**
- [camparo1992](lit/camparo1992.md), a two-photon Stark-shift *distribution*
  giving "an asymmetric resonance line shape in a fashion analogous to
  inhomogeneous broadening", though over a stochastic field in time rather than
  position in a beam. Different mechanism. Cite it, do not conflate it.

**What survives, and it is narrow:** the **closed form**, an analytic
triangular weight with a calculable asymmetry coefficient, used to recover the
shift **when the frequency reference is unusable**. Checked in both PDFs:
Slepkov and Wall each reproduce their lineshape by numerical ensemble averaging,
describe the asymmetry qualitatively, keep the frequency axis intact, and never
invert the lineshape for the shift. Cite all three up front rather than let a
referee find them.

> **Replaced by §5.2a (2026-07-30). The closed form does not survive
> either.** [delone1980](lit/delone1980.md) carries it, and this repository's
> $f(s)\propto|s|^{n-1}$ is their Eq. (5.3) evaluated for the intensity
> distribution of a focused Gaussian beam. What is left standing is §5.2a's
> shorter list, not the closed form. §5.2a follows immediately below, so a
> reader arriving here meets the retraction next and should not take this
> paragraph as the later word. The reconciliation of claim 1 is itself still
> **[OPEN]** there.

### 5.2a The concession runs to 1980, and the closed form is not new either

[delone1980](lit/delone1980.md), read in full from the rendered pages,
contains four things this repository had treated as its own frame, and it is a
**review**, so they were established before it:

- **Eq. (4.5):** $K(\Omega) \sim P(-(\omega_{n1}-\Omega)/\alpha_{1f}\hbar)$.
  For a shift linear in intensity, the lineshape *is* the intensity
  distribution, rescaled by the polarizability.
- **Eq. (5.2):** the multiphoton rate as a shifted Lorentzian integrated over
  $P(F)$ with an **$F^{k}$ weight**, $k$ = number of photons absorbed. That is
  `THEORY_NOTE` §2's construction with $k$ in the role of $n$.
- **Eq. (5.3):** the shift-dominated limit,
  $W \sim (\omega_f-k\omega_0)^k P((\omega_f-k\omega_0)/\alpha_{1f}\hbar)$,
  which they describe as "an asymmetrically broadened line".
- **The inverse problem**, stated twice: "one can reconstruct the distribution
  $P(F)$ from this relationship."

**And the closed form reduces to theirs exactly (calculated 2026-07-30).** For
atoms uniform in space across a Gaussian profile the area measure gives
$2\pi r~{\rm d}r \propto {\rm d}I/I$, so $P(I)\propto 1/I$, verified
numerically to 1 part in $10^4$ over four decades. Substituting that into their
Eq. (5.3) gives $W(s)\propto s^{k}\cdot s^{-1} = s^{k-1}$, i.e.
$f(s)\propto|s|^{n-1}$ with $k=n$, and at $n=2$ it agrees with the shipped
`lineshape.stark_ramp` to $7\times10^{-12}$. **This repository's closed form is
Delone's Eq. (5.3) evaluated for the intensity distribution of a focused
Gaussian beam.** The introduction here must say so in those words.

**What survives, and it is narrower than claim 1 as written.** Delone treat
$P$ as the *unknown to be reconstructed*, their point being that the lineshape
measures the laser's statistics. This programme runs it backwards: $P$ is
**known from the geometry**, so the integral evaluates and the result carries
**analytic cumulants**, an intrinsic $g_1=+0.566$ on bounded support that is a
number rather than a fit. Delone cannot write that number because in their
setting it is exactly what is unknown. The defensible contributions are
therefore: evaluating a known general result for the geometry that actually
occurs, its cumulants in closed form, and using the **third** cumulant as a
drift-immune measurement channel, which answers an experimental problem (an
untrustworthy centre) that does not arise in Delone's setting. **Claim 1 above
should be narrowed accordingly before the introduction is drafted.** **[OPEN]**

### 5.3 The nearest analogue experiment, and what it costs claim 1

[lee2010](lit/lee2010.md), Lee, Chui, Chen, Chang & Tsai, *Opt. Commun.* **283**,
1788 (2010), held and read, is closer to this analysis than anything in §5.1. Not an
adjacent geometry: **the same experiment**, in Cs. A two-photon $nS \to n'S$
alkali line in a hot vapour cell, Doppler-free with a retro-reflected beam,
cascade-fluorescence detection, laser intensity and vapour density scanned as the
two independent variables, and a lineshape decomposition into a homogeneous part
and an intensity-dependent part. They attribute the intensity-dependent part
as one of two candidates, "the laser beam is not a plane wave. Therefore, the
Gaussian width is possibly obtained from the spatially inhomogeneous of laser
intensities", and they
report a light shift of $-7.25(45)$ Hz/(mW/mm²) and a power- and
pressure-independent Lorentzian of $1.53 \pm 0.08$ MHz. Their hedge is worth
keeping: they write the Gaussian is "*possibly*" from the intensity
inhomogeneity, and keep velocity-dependent collisions alive as the alternative.

**What this takes.** The *phenomenon*, that the transverse intensity
distribution broadens a two-photon alkali line, and that the broadening grows
with power while the homogeneous part does not, is theirs, sixteen years ago.
Any wording implying this programme first noticed that is indefensible.

**What survives, and it is the whole of claim 1.** They fit the effect as a
**Gaussian**: symmetric, $\kappa_3 = 0$, no closed form, no cumulants, and the
distribution treated as a nuisance parameter to be separated from the natural
width. The programme's derivation gives $f(s)\propto|s|^{n-1}$, triangular at
$n=2$, with intrinsic skew $g_1 = +0.566$, and a Voigt fit has no third moment
to put it in. So the claim to defend is **the shape and its cumulants**, never
the phenomenon. That is narrower than the §5 wording was, and it is the version
that survives contact with this paper.

**There is a check against their published data, but not the obvious one, and
this section first stated it wrongly.** The tempting argument (an AC-Stark
$W_G$ must be *linear in power*, their $W_G$ is not linear through the origin,
so something is missing) **is invalid**: $W_G$ is the total Gaussian component
of a Voigt fit, independent Gaussian terms add in quadrature, and so
$W_G(P)=\sqrt{W_{G0}^2+(aP)^2}$ is non-linear and misses the origin even when
the AC-Stark part is exactly linear. The correct test is $W_G^2$ against $P^2$,
whose intercept is the power-independent floor and whose slope carries
$\Delta\alpha$. Note their floor is *not* the 1 MHz laser bandwidth, which they
assign to the **Lorentzian**. Even done properly this probes the kernel's
*width*, not its *shape*. The shape needs residuals they do not publish.
**Nothing computed. Recorded as OPEN, not as evidence.**

**A caution that points back at us.** Their headline is that the Lorentzian is
invariant, read as the natural width. If the true intensity kernel is skewed and
is fitted as Gaussian, the misspecification has to go somewhere, and in a Voigt
fit that is usually the Lorentzian. Whether their 1.53 MHz bound survives a
correctly shaped kernel is open, and the same question is the `transit_kind`
model-form systematic on $\beta_{\rm self}$ (M4c/M8), where this repository
already differences the two-sided-exponential and Gaussian transit forms for
exactly this reason.

### 5.2 Negative searches, which are what defend the rest

The same audit searched and found nothing, which is worth stating explicitly in
any manuscript:

- **No other group working 5S–6S.** Precision work on this line remains the
  USAFA lineage (Orson, Ayachitula). No new entrants found.
- **No prior 5S–6S magic wavelength.** *Phrase the claim as 5S–6S
  specifically*, because the nearest prior number is close:
  [zang2012](lit/zang2012.md) (arXiv:1204.4354, held) tabulates magic
  wavelengths for the **6S–5p₁/₂,₃/₂** pairs of a four-level active clock and
  reports **six** of them between 1200 and 1600 nm: 1342 and 1421 nm for
  6S–5p₁/₂, and 1331, 1336, 1453, 1461 nm for 6S–5p₃/₂. **This work's 1339.6 nm
  is bracketed by two**, 1336 (−3.6) and 1342 (+2.4). *This entry previously
  recorded only 1342, which understated it.*
  What defuses it is structural rather than rhetorical: their Table I puts the
  5p₁/₂–6s₁/₂ resonance at 1323.88 nm and 5p₃/₂–6s₁/₂ at 1366.87 nm, so **every**
  6S-involving magic wavelength in the infrared is confined to that 43 nm window
  and few-nm separations inside it are forced by the level structure. Different
  state pair, different magic condition, but the claim must be phrased as
  5S–6S specifically, and should say why the proximity is expected rather than
  leaving a referee to wonder.
- **An external test set for M9, and it survives contact with the primaries**
  ([bandi2025](lit/bandi2025.md) Table 1). Ten Rb two-photon vapour-cell
  standards, tabulated with signal linewidth, cell temperature **and 1/e² beam
  waist**, the three quantities `transit_fwhm_from_w0` maps between. A first
  pass looked inconclusive, with Callejo's row apparently impossible (transit
  alone 597 kHz against a 450 kHz *total*). **Two rows were then run down to
  their primaries on 2026-07-30 and both check out.**
  [callejo2025](lit/callejo2025.md): the waist is genuinely ~100 µm, but their
  measured linewidth is **1.5–2.1 MHz, not the 450 kHz tabulated**, and that row
  conflates the mems microcell with the reference glass-blown cell. Against
  the primary numbers transit supplies 34–51% of the excess over the 330 kHz
  natural width, as it should. `lemke2022` (now held): w₀ = 2.1(3) mm, stated as
  an **intensity radius (1/e²)**, giving 13%, as a millimetre beam should.
  So Callejo's anomaly was a transcription error in the review, not a defect in
  M9. **But the column is not uniform**. A claim briefly written here that it
  was a radius throughout is withdrawn: Erickson's thesis states "310 kHz for
  230 µm beam **diameter**", against Lemke's explicit radius. Worse, at
  Erickson's geometry our `transit_fwhm_from_w0` gives 513 kHz against his
  310 kHz, a factor of 1.65 that is a **transit-definition** difference rather
  than a waist one. **No cross-paper transit number from this table is quotable
  until that definition is pinned down.**
  **Seven of the table's primaries are already held:**
  [gerginov2018](lit/gerginov2018.md), [callejo2025](lit/callejo2025.md),
  [beard2024](lit/beard2024.md), [poulin2002](lit/poulin2002.md),
  [martin2018](lit/martin2018.md), [erickson2024](lit/erickson2024.md) (the
  thesis, held under `PDF_papers/theses/`) and `lemke2022` (held, note
  pending), so finishing this is mostly a matter of reading what is on disk
  rather than fetching anything. **[OPEN]**
- **No profile-likelihood precedent** in vapour-cell two-photon metrology, and
  **no pre-registration or blind analysis** in atomic spectroscopy of this kind.
- **No 6S self-broadening coefficient** in a second targeted pass. Zameroski
  2014 (5D, 7S) remains the nearest. The gap is real, and
  [weller2011](lit/weller2011.md) now anchors the expected scale from above.

Not exhaustive: Japanese- and Russian-language 6S self-broadening theory was
not searched.

**Audit status of the notes these negative searches rest on.** `zang2012` was
checked line-by-line against its PDF and four defects were found and fixed,
enough to distrust the rest by default until checked. Every note on the list
has since been checked by hand and holds:
[stalnaker2006](lit/stalnaker2006.md) (Eq. 45 extracts a polarizability
*combination* from fitted lineshapes,
$\alpha_0^{ac}(^3D_1) + \alpha_2^{ac}(^3D_1) - \alpha_0^{ac}(^1S_0) = -0.312(34)$
Hz/(V/cm)², Eq. 37/38 match the quoted FM depth and rate, every Wieman
characterisation is verbatim), [biraben1979](lit/biraben1979.md) and
[lehmann2021](lit/lehmann2021.md) (the transit-kernel pair whose form
`bruvelis2012` had backwards, Biraben's Eq. 46 and Lehmann's stated cusp both
check out), [weller2011](lit/weller2011.md)
($\beta/2\pi = (0.69 \pm 0.04) \times 10^{-7}$ Hz cm³, the 0.73 theory value
and the 170 °C range all hold), [wall2014](lit/wall2014.md) and
[camparo1992](lit/camparo1992.md) (Camparo turned up the sentence that costs a
novelty claim, recorded in §5 above). Two attribution errors were found and
fixed outside the checked set: [saha2010](lit/saha2010.md) and
[slepkov2010](lit/slepkov2010.md) were both credited with an 18 µm
hollow-core mode field that appears in **neither** paper, which belongs
instead to the experimenter's own CRYST³ fibre at Bologna, an injection-beam
*radius* for the 1064 nm dipole-trap beam supplied by a held Nasoni 2026
thesis, not the guided mode of a two-photon probe. **[OPEN]**: the
delineation table and the fringe-tail derivation built on Stalnaker are this
repository's own inferences and still need checking against
`rb5s6s/fringe_tail.py`. One factor of two to carry into any paper sentence:
Stalnaker's carrier-only criterion is $\xi/2 \ll \Omega$, not
$\xi \ll \Omega$ (our index is $2\times10^{-3}$, so nothing shipped changes).

## 6. Prior work on this line (5S–6S, 993 nm)

Two distinct lineages measured our exact transition before us: the **OIST**
apparatus lineage (Nieddu and Rajasree, the direct provenance for the cell and
beam) and the **Usaf Academy** precision-metrology lineage (Orson 2021 and
Ayachitula 2024, hyperfine and isotope-shift metrology, and the prior AC-Stark
and density-shift nulls this dataset's bounds refine).

### 6a. OIST apparatus lineage, the provenance of the cell and beam

- **[Nieddu 2019](lit/nieddu2019.md)** (Opt. Express and OIST PhD thesis), the
  group's 993 nm two-photon *frequency-reference* demonstration on our exact
  line. **[CITE, established]** They measured **w₀ = 64 µm** (f₁ = 150 mm
  L1), the direct beam measurement corroborating our transit-physics w₀
  re-pin (32 µm excluded, dataset w₀ ~ 50–64 µm, see
  `docs/notes/transit_width_resolved.md`). Their four two-photon peaks
  (FWHM ~5 MHz transition axis) are consistent with our dataset's ~5.25 MHz.
  Their retro is a self-imaging concave mirror (f = 75 mm) at 2F. Ours (md,
  2026-07-14) is the lens-based equivalent, L1/L2 at f = 150 mm with a flat
  mirror at the ~1 mm intermediate waist, so ρ ≈ 1 is a design property in
  both. Their detection is the 780+795 nm cascades together, unlike our
  795-only dataset stack, so amplitude/trapping comparisons must not assume
  the same collection channel.
- **[Rajasree-KP 2020, OIST PhD thesis](lit/rajasree2020thesis.md)** (held)
  repeats the same 993 nm cell setup in its §5.2 (a measured 128 µm beam
  diameter, cell at 130 °C) and cites Steck for the Rb data, confirming both
  the beam geometry and the N(T) vapour-pressure chain `density.py` uses.
  **[FEED, VERIFIED]**
- **[Rajasree 2020, PRR 2, 033341](lit/rajasree2020spin.md)** (held), *spin
  selection in single-frequency two-photon excitation*, tested on our line.
  **[CITE, established]** The transition rate scales as the squared degree of
  linear polarization, D², exactly zero for circular light: a drifting
  polarization is a physically-motivated candidate for the M10 between-block
  amplitude wander, and a circular-light null (extinguishing the line) is a
  free fixed-lock-session diagnostic. Their K = 0, 1, 2 scalar-operator
  decomposition (with Le Kien) is the citable basis for our M10
  degeneracy-law claim. They also demonstrate 5S–6S excitation in cold ⁸⁷Rb
  around a 400 nm-waist nanofibre via the evanescent field, so ONF-mediated
  5S–6S is demonstrated feasibility for the nanofibre extension, though the
  evanescent-field transition is not extinguishable by polarization
  (longitudinal field components break the paraxial D² law).

### 6b. Usaf Academy precision-metrology lineage

This group did the precision hyperfine/isotope-shift metrology on our line
and looked for the AC-Stark and collisional shifts, reporting nulls at
MHz-scale resolution. Our dataset's bounds sit below their resolution, and our
two-epoch design turns those nulls into measured coefficients.

- **[Ayachitula 2024](lit/ayachitula2024.md)** (Phys. Rev. A **110**, 022803)
  is the kHz-precision Doppler-free two-photon remeasurement of the 6S₁/₂
  hyperfine structure, both isotopes, now the source of `A_6S_RB87/85_HZ` in
  `constants.py`, replacing Perez Galván 2008. **[CITE, established]**
  Their line-center drift control (<0.5 kHz over 50 min) is the benchmark
  for what a fixed lock buys.
- **[Orson 2021](lit/orson2021.md)** (J. Phys. B **54**, 175001, same USAFA
  group), absolute hyperfine energy levels and isotope shift of the 5S–6S
  transition. **[CITE]** Their prior AC-Stark and density-shift nulls (on our
  C3d and C1 channels) are consistent with, and refined by, our dataset's
  bounds (S₀ < 0.63 MHz by profile likelihood, β_self a bound). They are also
  the source of `DELTA_ALPHA_AU = +1093` (opposite sign by definition), and
  our `stark_shift_S0_mhz` reproduces their predicted shift to the digit
  (`test_stark_S0_reproduces_orson2021`). Prior groups looked for these
  shifts on this line and saw nulls at ~MHz resolution. The drift-immune
  ramp method and two-epoch design is the route to coefficients below that
  floor.

## 7. Method anchors

The ruler, the detection channels, the trapping systematic and the reference
standards this analysis runs on. Each entry says what it anchors, not what it
is about.

**The frequency ruler.**
- **FM-spectroscopy ancestry.** [Snadden, Bell, Clarke & Riis
  1996](lit/snadden1996.md), FM two-photon in cold Rb, alongside the paywalled
  Zapka 1983 (CW two-photon FM in Rb vapour) and Bjorklund 1980, the origin of
  FM spectroscopy. Both are to-pull. **[CITE]**
- **A modern ruler of the same kind.** [Yang et al. 2025](lit/yang2025.md),
  the frontier of the "internal ruler tracks a drifting axis" idea the EOM
  ruler here embodies. **[FEED]**

**Detection channels.** The 795 nm channel this dataset was taken on is
reabsorbed at high density, so the infrared cascades are the route to the
same line at temperatures the self-broadening measurement needs.
- **The 1.3 µm trapping-free channel.** [Hassanin et al.
  2023](lit/hassanin2023.md) is the direct precedent for the 6S→5P route: the
  reabsorption-free 5D→5P cascade lets the sibling 5S–5D line be probed at high
  density, which is what a collisional-broadening study needs. **[CITE]**
- **A second cascade precedent.** [Beard et al. 2024](lit/beard2024.md),
  776 nm 5D→6P fluorescence. **[CITE]**
- **Multi-channel detection on the 5S–7S ladder.** [Wang, Cao, Yuan, Wang,
  Xiao & Jia 2025](lit/wang2025.md), whose 741 and 728 nm channels set the
  ladder magic wavelength, is the precedent for the amplitude work. **[CITE]**

**Radiation trapping.**
- **The alkali-cloud anchor.** [Fioretti et al. 1998](lit/fioretti1998.md),
  the radiation-trapping anchor for M7 and the systematics section. **[CITE]**

**Reviews and reference standards.**
- **Doppler-free two-photon review.** [Biraben 2019](lit/biraben2019.md), the
  pioneer's own retrospective. **[CITE]**
- **Two-photon Rb in a confined geometry.** [Amy et al.
  2017](lit/amy2017.md). **[FEED]**
- **A sibling ladder with its own magic wavelengths.** [Duspayev, Owens, Dash
  & Raithel 2024](lit/duspayev2024.md), the 4D_J rung at 1033 nm, giving an
  independent magic-wavelength determination to cross-check M16. **[FEED]**
- **Critically evaluated matrix elements.** [Safronova & Safronova
  2011](lit/safronovaSS2011.md) is the independent published source for the
  M16 7S static polarizability near 3.2×10⁴ a.u., which nothing else here
  anchors. The 7S and 5D values still have to be pulled. **[FEED]**

**Constants and conventions.** These four set quantities the analysis treats as
given, so a reader checking a number ends up here rather than in a module.

- **Atomic data for Rb.** [Steck's Rb 85 and 87 D line data](lit/steck_rb.md),
  the reference line
  frequencies, natural widths and polarizabilities, and the vapour-pressure
  chain `density.py` uses. **[CITE]**
- **The intensity convention.** [Grimm, Weidemüller & Ovchinnikov
  2000](lit/grimm2000.md) fixes the ⟨E²⟩ convention accepted for S₀,
  ΔE = −(1/4)αE₀² = −αI/(2ε₀c). A shift quoted in the other convention differs
  by a factor of two, which is why the convention is named wherever S₀ appears.
  **[CITE]**
- **The 5S tune-out anchor.** [Leonard et al. 2015](lit/leonard2015.md) with
  its [2017 erratum](lit/leonard2017.md), which moves the measured tune-out to
  790.032326(32) nm and the matrix-element ratio to 1.99217(3). The erratum is
  the value `polarizability.py` validates against, and the pair is the worked
  example of why a replaced number has to be chased into every file that
  quotes it. **[CITE]**
- **An independent matrix-element set.** [Arora & Sahoo
  2012](lit/arora2012.md), coupled-cluster 6S-5P reduced elements and a 6S
  lifetime of 45.44(8) ns against the 45.57(17) ns measurement, the cross-check
  on the sum this analysis builds. **[FEED]**
- **Matrix elements for the 6S polarizability.**
  [Herold et al. 2012](lit/herold2012.md) supplies the 5S→6P reduced matrix
  elements 0.3235(9) and 0.5230(8) ea₀ that `rb5s6s/polarizability.py` uses,
  measured by light-shift cancellation at the 421 and 423 nm magic zeros.
  REPORTED, the record confirmed from the publisher listing and the source
  not read here. **[FEED]**

## 8. The 2024–2026 field

Where a vapour-cell paper from this programme sits among the groups working the
neighbouring lines, and which of them a referee will have read. The source sweep
is an untracked local literature-intake working file, and the options for the
tunable Ti:Sapph are in [`FUTURE_TRANSITIONS_titsapph.md`](FUTURE_TRANSITIONS_titsapph.md).

Six of the swept papers are now HELD PDFs: [andeweg2026](lit/andeweg2026.md),
[ahern2025](lit/ahern2025.md), [antypas2018](lit/antypas2018.md),
[chevrollier2012](lit/chevrollier2012.md), [araujo2021](lit/araujo2021.md),
and [safronova2004](lit/safronova2004.md), the benchmark that carries the
**6S dynamic polarizability**, a stronger Δα anchor for the 6S state than
safronova2006. Two IDs the compass synthesis got wrong are QUARANTINED and
must not be cited: the Li dual-interrogation arXiv, the real compensation-method
preprint being 2405.14281, a different paper, and `drago2026` (2602.07161,
malformed).

The same episode left a retired citekey behind. The dual-interrogation paper was
carried here as `lidou2024`, a key that names the wrong first author, until the
paper itself was held and read. It is [`li2024b`](lit/li2024b.md), by Ye Li and
colleagues, and the Dou Li compensation paper is [`li2024`](lit/li2024.md). The
key `lidou2024` is retired and appears here only so that a reader meeting it in
an older note knows which paper it meant.

### 8a. Positioning on the 993 nm line

**Positioning this analysis (our 993 nm 5S→6S).** No other group is currently working this line: the only active
group, USAFA/Knize with [`orson2021`](lit/orson2021.md), the absolute-hyperfine-energy
work with McLaughlin as second author, and its successor
[`ayachitula2024`](lit/ayachitula2024.md), the vol/year question resolved
2026-08-03, both held) reports
**null AC-Stark and density shifts at ~6 MHz resolution** (up to 10⁴ W/cm², N =
3×10¹¹–5×10¹³ cm⁻³). Our bounds sharpen those 6 MHz nulls by more than an
order of magnitude, and that sharpening is what is new here.

**Cross-alkali check, 2026-08-03.** [`kirankumar2011`](lit/kirankumar2011.md),
a K 4S→6S two-photon isotope-shift and hyperfine paper (a Δn=2 s-s line, the
same class as `zameroski2014`'s Rb 5S→7S, not a Δn=1 analogue of our line),
confirms the same-family scoping directly: it treats AC-Stark, blackbody and
pressure-broadening shifts entirely as calculated or extrapolated corrections
subtracted from a differential measurement, and reports no density- or
intensity-dependent coefficient of its own. That is the norm this
programme's environmental coefficients are being measured against, with
`lee2010`/`lee2012`'s Cs 6S→8S line standing as the one alkali s-s
two-photon exception that does carry a measured light shift and a
power/pressure Voigt decomposition. [`liu2001`](lit/liu2001.md), the same
K 4S→6S line a decade earlier (Liu & Baird, *Meas. Sci. Technol.* **12**
740, 2001), independently confirms the same scoping: its 17 MHz linewidth
is left undecomposed beyond a fixed 1 MHz transit-time estimate, at one
fixed cell density and one fixed laser power, with no self-broadening or
light-shift coefficient reported. The two K papers together, not
`kirankumar2011` alone, are what shows no measured s-s environmental
coefficient exists across the same-family alkali literature surveyed
here.

The novelty available here is narrower than an inversion claim, and §5.1
and §5.2a of this file govern: the map frame, the multiphoton weighting and
the asymmetric shift-dominated limit are [delone1980](lit/delone1980.md)
review material, so what stays claimable on the 778 nm line is the closed
form with its analytic cumulants, the reference-free extraction where the
frequency axis is unusable, and the third cumulant as a drift-immune
channel. A 2015 nanofibre-trap analysis (Lee, Grover,
Hoffman, Orozco, Rolston, *J. Phys. B* **48**, 165004) reads a position-weighted
light-shift distribution from lineshape asymmetry in trapped ⁸⁷Rb and is the
closest external precedent even to that narrower claim, REPORTED and not
held, so the language stays scoped until it is read in full:
- **`wieman1987`**, Wieman, Noecker, Masterson, Cooper, *PRL* **58**, 1738 (1987):
  AC-Stark lineshape asymmetry in standing waves, the foundational precedent
  (treated as a distortion). **[CITE]**
- [antypas2018](lit/antypas2018.md), the AC-Stark-asymmetry elimination
  precedent (Yb) our method inverts. **[CITE]**
- [`bruvelis2012`](lit/bruvelis2012.md), Bruvelis, Ulmanis, Bezuglov, Miculis,
  Andreeva, Mahrov, Tretyakov & Ekers, *PRA* **86**, 012501 (2012): two-photon
  excitation in a three-level ladder gives a Voigt whose width is set **solely by
  w₀**, because wavefront-curvature broadening is *exactly compensated* by the
  longer transit of particles farther off axis. **[CITE]**

  *Held and read, which weakened its use here.* The compensation is real and
  doubly validated (density-matrix numerics and experiment), but it is derived
  for a **cylindrical-lens sheet crossed by a collimated supersonic Na₂
  beam**, not a circular focus in a thermal vapour, and the paper itself notes
  the Voigt profile forms by different mechanisms in the two cases. So it is
  the right conclusion reached by a route this campaign does not share, and
  the in-repo support for the transit kernel is M19's own change-of-variables
  check rather than this paper.

### 8b. The 778 nm 5S→5D clock frontier

**The 778 nm 5S→5D clock frontier.** These are the competition, and all of them
suppress the AC-Stark shift *actively*, which is what the passive method here
contrasts with. **[FEED]** and **[CITE]** for the systematics and outlook
sections, and for the future Paper A.
- [andeweg2026](lit/andeweg2026.md), Andeweg, Kitching, Hummon (NIST): the
  newest competitor method, active **power-modulation** AC-Stark suppression
  (×1000). Contrast the passive approach here against it.
- [ahern2025](lit/ahern2025.md), Ahern et al. (Adelaide): two-color 5S–5D
  standard, 6×10⁻¹⁴/√τ, light-shift-limited.
- [feng2026](lit/feng2026.md), Feng et al., *Opt. Lett.* **51**, 1363–1366 (2026):
  5S–5D fiber-laser clock on the F=1→F′=1 sub-transition (3.6× smaller tensor
  ac-Stark than the usual F=2→F′=4), 6.6×10⁻¹⁵ at 10⁴ s matching a passive
  H-maser, He-equilibration collisional-shift control (300+ days baked at
  358 K, ~37× the ~8-day permeation time constant).
- **`yudin2020`**, *PRApplied* **14**, 024001 (2020): the power-modulation
  light-shift-suppression framework behind Andeweg. [li2024b](lit/li2024b.md) is Li, Liu, Wang and Kang, dual
  interrogation, *Opt. Express* **32**, 2766 (2024), VERIFIED and held [the
  compass artifact's arXiv:2310.10175 was wrong, flagged here, and the
  related *compensation-method* preprint, first author Dou Li, is
  [li2024](lit/li2024.md), a different paper, REPORTED with no DOI]. (With
  `gerginov2018`, `callejo2025`, `newman2021`,
  `martin2018/2019` already in §6/bib, and
  [hamilton2023](lit/hamilton2023.md)'s magic-wavelength target for the proposed
  Ti:Sapph asymmetry scan.)
- [bandi2025](lit/bandi2025.md), comprehensive review of Rb two-photon clock
  systematics and the stability benchmarks. **[CITE]** the single best field-survey
  citation.
- **`bjorkholm1976`**, *PRA* **14**, 751: two-photon lineshape with a near-resonant
  intermediate, the theory anchor for the future 6S(clean)-vs-5D(resonant) Paper C
  (intermediate detunings 75 → 1 THz, see `FUTURE_TRANSITIONS_titsapph.md`).

### 8c. Radiation trapping, the 795 nm systematic

**The modern Lévy-flight lineage** beyond the Holstein, Molisch and Fioretti
canon (Kaiser, Passerat de Silans), for the 795 nm trapping systematic:
- [chevrollier2012](lit/chevrollier2012.md), the canonical radiation-trapping /
  Lévy-flight review. **[CITE]** framework.
- [araujo2021](lit/araujo2021.md) (Lévy flights in He-broadened hot Rb, α≈0.5),
  **`weiss2018`** (*NJP* **20**, 063024, trapping against subradiance) and
  **`nunes2024`** (arXiv:2411.18570, frequency redistribution for Rb and Cs).
  **[FEED]** for modern Rb-specific trapping.

### 8D. Theory anchors and the Cs validation triangle

**Theory anchors.** [safronova2004](lit/safronova2004.md) joins
[safronova2006](lit/safronova2006.md) and [gomez2005](lit/gomez2005.md). There is
**no dedicated modern 6S polarizability at 993 nm**, a gap Paper B can flag.

On the trapping side, Yang et al. (*PRL* **117**, 123201, 2016) and Carr and
Saffman (*PRL* **117**, 150801, 2016) extend the same magic-condition logic to
state-insensitive optical traps, finding magic-intensity and doubly-magic
wavelength points that null a trap's own sensitivity to intensity or field
noise for Rb and Cs hyperfine qubits, tracing back to Derevianko's 2010
doubly-magic proposal (*PRL* **105**, 033002). All three are REPORTED, not
held. That is the trapping-side counterpart of this programme's
spectroscopy-side scalar magic wavelengths (M16), which null the probe's own
sensitivity to the 5S–6S transition rather than a qubit's sensitivity to the
trap.

**The Cs validation triangle (intake 2026-07-30).** The Δα sign-and-magnitude
dispute will not be closed by re-deriving Rb. What *can* be done is to show the
machinery reproduces a **measured** alkali $nS\to(n{+}1)S$ differential, which
removes "the code has a global sign or normalisation error" from the table of
explanations without settling the 993 nm answer itself. Caesium supplies such a
differential to about half a percent, from two directions:

- [quirk2024](lit/quirk2024.md), the measurement. $k = 0.72246(29)$ Hz/(V/cm)²
  at 0.04%, giving $\alpha_{7s} = 6207.9(2.4)$ against
  $\alpha_{6s} = 401.1(5)$, i.e. $\Delta\alpha({\rm Cs}\ 6s\to7s) = 5807~a_0^3$.
  Also revises $\tilde\beta = 27.043(36)~a_0^3$. **[FEED]**
- [iskrenovatchoukova2007](lit/iskrenovatchoukova2007.md), the first-principles
  side, all-order sd with evaluated uncertainties: $\alpha_{6s} = 398.4(7)$,
  $\alpha_{7s} = 6238(41)$, $\alpha_{8s} = 38270(280)~a_0^3$. Its differential
  $5840~a_0^3$ agrees with Quirk's measured $5807$ to **0.57%**. **[FEED]**
- `sieradzan2004`, Sieradzan, Havey & Safronova, *PRA* **69**, 022502 (2004),
  "Combined experimental and theoretical study of the $6p~^2P_j \to 8s~^2S_{1/2}$
  relative transition matrix elements in atomic Cs" (record confirmed via
  Crossref 2026-07-30). The experimental check on the matrix elements between
  $8s$ and $6p_j$, 17.78(7) and 24.56(10) $ea_0$, that feed $\alpha_{8s}$.
  **Not held**: an attempt to add it on 2026-07-30 did not reach
  `PDF_papers/`. **[CITE]**

`polarizability.py` must reproduce $\alpha_{7s}$ from Cs matrix elements before
the Rb 993 nm sign is argued from it. Both anchors are **static**, so neither
constrains the 993 nm cancellation directly. They validate the machine, not the
answer.

**The Cs 6S–8S line, the closest analogue experiment there is.**
[lee2010](lit/lee2010.md) (Tsai/Chui, NCKU Tainan) and its sister
[lee2012](lit/lee2012.md) run the same experiment in Cs: hot-cell,
retro-reflected, cascade-detected two-photon $nS\to n'S$ with laser intensity
and vapour density as independent variables. Their Voigt decomposition
separates a power- and pressure-independent Lorentzian (an upper bound on the
Cs 8S natural width) from a Gaussian that **grows with laser power**,
attributed to "the spatially inhomogeneous of laser intensities", which is the
physics here fitted with a symmetric shape (numbers in §2a and §5.3). Two
apparatus lessons transfer directly to any proposal: a **second cell at fixed
intensity** makes the light shift differential, exactly the failure mode that
forced the M20 retraction, and a **cold finger at 10 °C under a 65 °C body**
decouples vapour density from thermal velocity, the degeneracy this
campaign's temperature scan has to break by shape. **[CITE]**

A third group works the same Cs line with a comb.
[Fendel, Udem & Hänsch 2007](lit/fendel2007.md) (Opt. Lett. **32**, 701)
tested the peak intensity against the average and found the average correct,
−0.21 Hz/(mW/cm²). Their waist was a deliberately unfocused 0.72 mm, chosen to
keep the intensity distribution narrow, so the result constrains nothing about
a tight focus. It is used in [THEORY_NOTE](THEORY_NOTE.md) §6 for exactly that
reading. **[CITE]**


## 9. The nanofibre extension and the ONF community map

The proposed optical-nanofibre extension has no data. What it has is a
precedent chain, and this section is it. Nothing below licenses a claim about
this programme's own measurement.

### 9a. The precedent chain for an asymmetric line near a surface

The bridge runs through the Gokhroo, Le Kien and Nic Chormaic lineage:
[gokhroo2022](lit/gokhroo2022.md) (the ONF two-peak pushing-dip
analog), `li2024perspective` (the standard ONF review), and
[sadeghi2026](lit/sadeghi2026.md) (ONF delayed-feedback fluorescence, held
and read: linewidth ~16 MHz against a 5.2 MHz natural width, with
Γ₀ = 8.44 ± 0.80 MHz of non-atomic broadening). The clean cell lineshape is
the reference against which ONF surface/pushing effects are read.

- [patterson2018](lit/patterson2018.md), Patterson, Solano, Julienne, Orozco
  & Rolston, *PRA* **97**, 032509 (2018), held and read. It stands to the
  nanofibre extension as [wieman1987](lit/wieman1987.md) does to this
  analysis: cold Rb around a 240 nm nanofibre, where a static van der Waals
  surface potential red-shifts atoms nearer the silica and the transmission
  spectrum is built as a Lorentzian of position-dependent centre averaged
  over a density-times-coupling weight, the same shift-distribution
  convolution this programme uses with a static potential in place of the
  AC-Stark shift. So the concession §5 makes to `wieman1987` must be made
  again here, one step closer to home. What survives it: their shift is
  static and independent of probe intensity, whereas an AC-Stark shift *is*
  the intensity that weights the excitation, which is the discriminating
  signature a nanofibre extension would need to measure and nobody has yet.
  **[CITE]**
- **The open question it hands us.** Patterson measure Γ₀ = 8.1(3) MHz, the
  total homogeneous width in their model, and write they "consistently
  measure a 2 MHz increase from the natural linewidth which we do not yet
  understand" after excluding Doppler, superradiant, Purcell and Zeeman
  explanations one by one. [Sagué et al. 2007](lit/sague2007.md), held and
  read, saw a comparable ~1 MHz unexplained in Cs at first glance, but their
  model carries no fitted width parameter, so their 6.2 MHz (against 5.2
  natural) is a matched output rather than a residual, attributed outright to
  the van der Waals shift plus modified spontaneous emission, with a
  position-dependent γ(r) reaching +57% at the surface. Sagué therefore
  leaves the unexplained-width column, and the open case is Patterson plus a
  newly surfaced Liu *et al.* (2024/25, ⁸⁷Rb D2, fitted 2–4 MHz residual).
  **[OPEN]** The likely mechanism: Patterson's Eq. (10) integrates α(r), ρ(r)
  and δ_vdW(r) over r but passes Γ₀ in as a scalar, though their own Eq. (3)
  defines α(r) as a position-dependent decay rate used as the detection
  weight. An ensemble with a distribution of Γ₁D(r) fitted by one scalar
  returns a width that is too broad, symmetric and near-Lorentzian and
  survives every exclusion they list, because their Purcell argument bounds a
  mean and this is a variance. A refit of their published spectra is the
  falsification test, and is publishable either way.
- **The theory inputs a refit needs.** [Klimov & Ducloy
  2004](lit/klimovducloy2004.md), held, derives analytical transition rates
  in the subwavelength regime but licenses the closed form only for
  $ka$ below $1/\varepsilon$ (0.473 for fused silica), while Patterson sits at
  $ka = 0.967$ and Sagué at 1.844 (calculated), both in the band where
  guided-mode influence is substantial, so the closed form cannot simply be
  coded and the refit needs the paper's unread Section IV. For the van der
  Waals shift near a cylinder, [Frawley et al. 2012](lit/frawley2012.md)
  (*Phys. Scr.* **85**, 058103), held, gives closed analytical equations for
  metal and dielectric nanocylinders and replaces `boustimi2002` here
  (Sagué's own words are "we calculated the vdW shift", and both Boustimi
  papers are metallic while these fibres are silica). Frawley's correction
  factor μ tends to unity close to the surface and falls to about 0.5 at 5
  fibre radii, but its own electrostatic derivation is licensed only for
  $ka$ below 1, which Patterson's fibre meets marginally and Sagué's fails.
  **[OPEN]** Its concave counterpart
  [Afanasiev & Minogin 2010](lit/afanasiev2010.md) covers the hollow-core
  interior in the same factorised form, μ rising to 4 near the axis, and
  retires the sphere-to-cylinder extrapolation
  [schmidt2011](lit/schmidt2011.md) had been carrying (the cylinder figure is
  4, not the sphere's 6). The concave enhancement costs a hollow-core
  geometry nothing, since it multiplies an on-axis $C_3/x_0^3$ that is
  already $10^{-4}$ to $10^{-10}$ of the near-wall value for realistic bores.
- **[Perrella et al. 2013](lit/perrella2013.md)** (*PRA* **87**, 013818),
  two-photon spectroscopy of thermal Rb in a hollow-core photonic-crystal
  fibre, 10 MHz linewidths. Its true geometry, from the first author's
  open-access thesis, is a **45 µm kagomé core** at 90 °C, two-colour
  780+776 nm, so transit supplies only 3–4 MHz of the observed 10 MHz and the
  rest is likely higher-order-mode coupling from a curved fibre, not a
  transit-limited line. Its ~15 µm mode radius is the closest published
  analogue to this programme's own CRYST³ hollow core at Bologna (~18 µm, now
  sourced as a measured injection-beam radius for the 1064 nm trap beam in a
  held Nasoni 2026 thesis, an assumption rather than a measurement for a
  778 nm probe): transit there costs ~3–4 MHz against 0.93 MHz for the
  free-space $w_0=64$ µm, a factor of 3–5 rather than the 15–30× a tighter
  published core would impose, with Perrella's 10 MHz total warning that
  transit is not the whole budget in a real large-core fibre. **[CITE]**

**[FEED] Pennetta et al. 2026** ([pennetta2026](lit/pennetta2026.md)), the
nearest-platform result to the nanofibre extension, feeding two of its
pillars: radial trap ~7 kHz, atom ~280 nm from the surface, and record
Ramsey/spin-echo coherence times. It puts quantified atom–surface content
(Casimir–Polder plus surface-charge electrostatics) on the near-surface
potential where `gokhroo2022` left only a hypothesis, and its coherence gain
is a suppression of the trapping-light differential light shift, a
real-world confirmation on the nanofibre platform itself that inhomogeneous
differential light shift is the coherence-limiting systematic in guided-atom
systems, the premise of THEORY_NOTE §3 and the M16 toolkit. Platform
caveats: Cs not Rb, a D2 hyperfine qubit not 5S–6S, a 450 nm fibre not the
OIST 650 nm, so the physics transfers but the numbers do not.

**[FEED] Pache et al. 2026** ([pache2026](lit/pache2026.md)), the same
group's companion on the loading and cooling toolkit for this platform,
naming the same residual differential light shift of the trapping fields as
the limiting imperfection. Cs/D2 again, so the physics transfers, the
numbers do not.

**Prior-art audit on the pushing dip.** Crossref/OpenAlex list 6 citing
works for `gokhroo2022`, 4 unique, and **none models the dip**: Kestler *et
al.* (unrelated Sr ONF trap), Vylegzhanin *et al.* 2023/2025, and
`li2024perspective`, the group's own review, which cites `gokhroo2022` once
for the capability of observing the 5S₁∕₂–6S₁∕₂ transition and never
discusses the dip. Fam Le Kien, the theorist on the paper, has published no
follow-up. `gokhroo2022` itself stops at a hypothesis ("we speculate that …
resonance scattering induced pushing … becomes the dominant effect") and
contains no Casimir-Polder or van der Waals content at all. Scope caveat: the
dip is a density-depletion effect, atoms pushed out of the bright region,
whereas the ramp machinery describes the distribution of light shifts, so the
ramp is at most one ingredient of a full model, which also needs the
force/density dynamics.

### 9b. Reading a near-surface shift from a lineshape

- **[Ton, Kestler, Steck & Barreiro 2026](lit/ton2026.md)**, the state-of-the-art
  template for extracting a surface shift from the line, and the model to
  follow for the extension's surface term. D. A. Steck, of the constants
  lineage used here, is a co-author. **[CITE]**
- **[Dutta et al. 2025](lit/dutta2025.md)**, the direct template for reading
  the near-surface shift as a thermal-averaged distribution in the extension's
  surface section. **[CITE]**
- **[Dutta et al. 2024](lit/dutta2024.md)**, higher-order cp corrections at
  close range, the background for the extension's near-surface term. **[FEED]**
- **[Sargsyan, Momier & Sarkisyan 2025](lit/sargsyan2025.md)**, the
  experimental analogue of extracting a surface shift from the line. **[CITE]**
- **[Piotrowski, Bach, Vera Paz, Schneeweiss & Rauschenbeutel 2026](lit/piotrowski2026.md)**
  sets a nanofibre feasibility bound on the probe window and power. **[CITE]**

**Still to verify.** Sargsyan/Sarkisyan 2026 (arXiv:2601.04661, a second nanocell
surface-shift paper) and Obaze et al. 2025 (Photonics **12**, 513, a second 778 nm
clock review). **Quarantined (do not cite): arXiv:2602.07161** (malformed, re-surfaced).

### 9c. The ONF community map

Why the nearest-platform references cluster the way they do. The two poles
of the optical-nanofibre cold-atom field are the **Rauschenbeutel group** (Humboldt
Berlin, with `pennetta2026` and `pache2026`) and the **Nic Chormaic group** (OIST,
with `nieddu2019`, `rajasree2020` and `gokhroo2022`, the provenance of this
apparatus and the platform the extension would use). They
co-organise the ONNA (Optical Nanofibre Applications) conference series. So the newest
nearest-platform work is from the nanofibre community, and engaging it well is both good
scholarship and the natural way this program is read by that community.
