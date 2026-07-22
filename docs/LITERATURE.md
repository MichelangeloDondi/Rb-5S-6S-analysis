# Literature ledger — prior art, anchors, and the novelty delineation

Purpose: every external number or claim Paper 1 leans on, with provenance,
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
| Saturation | saturating + hole-burning entangled with the asymmetry | unsaturated throughout (C3: amplitude ∝ P² confirmed) |

The generic quasi-static law both regimes reduce to: signal weight ∝ Iⁿ over
a Gaussian envelope gives dA ∝ dI/I, hence **f(s) ∝ |s|^(n−1)** — uniform
for their n = 1, triangular for our n = 2. The triangular form is specific
to two-photon excitation; the same dA ∝ dI/I holds for a thin evanescent
shell, which is the geometry-independence bridge to Paper 2. CALCULATED
(README derivation to be extended with this comparison).

**What we take from it:** their FM framework settles our ⟨E²⟩ convention question.
Their Sec. IV/Fig. 6 analysis: an atom crossing standing-wave fringes sees
frequency modulation of depth ξ = ½αε₀² at rate Ω/2π = 2v/λ. For us:
λ/2 ≈ 0.50 µm fringes, axial thermal speed ~280 m/s → Ω/2π ≈ 0.56 GHz,
ξ = S₀ ≲ 1 MHz → **modulation index ξ/Ω ≲ 2×10⁻³ → pure carrier at the
time-averaged intensity**. So the shift is set by the fringe-averaged
intensity I₁ + I₂ = (1+ρ)I₁ — no coherent ×2 fringe enhancement. The
residual OPEN item is the measured retro ratio ρ (measured in a fixed-lock session, per
configuration). But the fringe-resolved tail is NOT a benign percent-level
broadening: near-transverse atoms (small axial speed) sample the node/antinode
arcsine, and because the fringe MULTIPLIES the shift (s → s(1+x), x arcsine) it
SUPPRESSES the ramp skew — κ₃ → S₀³(1/135 − f_res/10) at ρ=1, a −13.5·f_res
fractional leverage (∝ contrast², not contrast³ — the arcsine has E[cos³]=0; only
the product P = f_res·σ_x² is observable). Negligible at w₀=50 µm (~5–8% of an
already-below-noise skew), ~25% at w₀=16 µm, and same-sign-additive to the
beam-divergence correction — fit jointly at the small waist (quantified,
coherence-window bracketed, in `rb5s6s/fringe_tail.py`). CALCULATED 2026-07-17.

**[Hamilton et al., Phys. Rev. Applied 19, 054059 (2023)](lit/hamilton2023.md)**
(arXiv:2212.10743) — VERIFIED (full text read; PDF in PDF_papers). The
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
abstract/indices VERIFIED; full-text digits TO-PULL (paywalled; needs
university library access). Rb–Rb self-shift of 5S→7S: −17.82(81) kHz/mTorr,
converting to **−0.74 kHz per 10¹² cm⁻³** (−0.9 at 500 K — the conversion
needs their exact cell T from the full text). Scaling that self-shift
7S→6S (vdW impact, C₆ ~ n*⁷) gives the expected **β_self(6S) ~ 1 kHz per
10¹² cm⁻³** (ENVELOPE); the unit-conversion, Lindholm–Foley ratio-check, and
n*-scaling derivation are in the lit file.

Consequences (calibration against the theoretical expectation):
- The archival bound (< 40–110 kHz per 10¹² cm⁻³) sits **~40–100× above
  the physically expected value** — consistent, but NOT constraining. Paper
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
  ac-Stark determined by average not peak intensity; power-to-zero
  extrapolation mindset. REPORTED.
- **Cs 6S–6D (2018)**: 40 µm waist → significant transit broadening.
  Cross-check vs our M9: scaling by v/w₀ (Cs ~200 m/s @40 µm vs Rb ~280 m/s
  @32 µm) puts their transit at ~0.6× ours — consistent with our
  1.87 MHz @ 32 µm (flux-corrected). REPORTED (scaling CALCULATED); pin the exact citation.
- **Taiwan comb work (Opt. Lett. 30, 842 (2005) + successors)**: 5S→7S
  absolute frequency, Stark/collisions suppressed as systematics. REPORTED.

## 5. Revised novelty claims (post-Stalnaker, wording to defend)

1. **Closed-form triangular ramp** f(s) ∝ |s| for focused, retro-reflected,
   fringe-averaged two-photon vapor-cell geometry, with the |s|^(n−1)
   signal-exponent law and its evanescent-geometry invariance (Paper 2
   bridge). Not in Stalnaker (numerical, n = 1, fringe-resolved).
2. **Drift-immune moment method**: third cumulant carries S₀ and survives a
   reference too unstable for the center. No prior work frames the moment
   as the *measurement channel* — Stalnaker fit full shapes with a good
   reference; precision groups suppressed the shift.
3. **β_self(6S)**: completes the measured 5D/7S self-rate series — a
   modest addition to the measured series rather than a headline result. In the archive it is a bound ~40–100×
   above expectation; a measurement requires the high-T extension.
4. **EOM-comb-in-fine-scan** frequency axis (0.04257(5) MHz/ms laser-axis,
   per-block).

NOT claimable: "asymmetric lineshapes from distributed AC-Stark are new"
(Wieman 1987 / Stalnaker 2006 own it), or "first extraction of a
polarizability from the asymmetry" (Stalnaker did exactly that, Eq. 45).

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
- **Rajasree-KP 2020** ([`rajasree2020`](lit/rajasree2020.md), OIST PhD thesis)
  — repeats the same 993 nm cell setup and cites Steck for the Rb data,
  confirming both the beam geometry and the N(T) vapor-pressure chain our
  `density.py` uses. **[FEED]**
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
  * **ONF feasibility evidence for Paper 2:**
    [rajasree2020spin](lit/rajasree2020spin.md) demonstrates 5S–6S excitation
    in **cold ⁸⁷Rb around a 400 nm-waist nanofibre** (SM800-5.6-125, ~30%
    transmission at 993 nm) via the evanescent field — so ONF-mediated 5S–6S
    from atoms near the fibre is *demonstrated*, and the open Paper-2 question
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

## 8. The 2024–2026 landscape (Paper-1 positioning + future-transition frontier)

Source sweep: `PDF_papers/literature_intake/landscape_2026_...md` +
`RECENT_LITERATURE_2023-2026.md`. Strategy for the tunable Ti:Sapph:
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

**Positioning Paper 1 (our 993 nm 5S→6S).** No other group is currently working this line: the only active
group (USAFA/Knize — `ayachitula2024`; and the earlier McLaughlin 5S–6S absolute-
energy work, *J. Phys. B*-era, VERIFY vol/year via Ayachitula's ref list) reports
**null AC-Stark and density shifts at ~6 MHz resolution** (up to 10⁴ W/cm², N =
3×10¹¹–5×10¹³ cm⁻³). Our sensitivity to the light shift and β_self is therefore new.
The **novelty to claim** is the *inversion* of lineshape asymmetry from a nuisance
into a reference-free estimator:
- **`wieman1987`** — Wieman, Noecker, Masterson, Cooper, *PRL* **58**, 1738 (1987):
  ac-Stark lineshape asymmetry in standing waves, the foundational precedent
  (treated as a distortion). **[CITE]**
- [antypas2018](lit/antypas2018.md) — the ac-Stark-asymmetry elimination
  precedent (Yb) our method inverts. **[CITE]**
- **`bevilacqua2012`** — *PRA* **86**, 012501 (2012): Gaussian-beam transit-time
  two-photon gives a Voigt whose width is set solely by w₀ (curvature broadening
  cancels transit) — directly supports our w₀-as-dominant-systematic story. **[CITE]**

**The 778 nm 5S→5D clock frontier (the competition — all *active* AC-Stark
suppression; our passive method is the differentiator).** [FEED/CITE for §VI.D/§VII
contrast and for the future Paper A.]
- [andeweg2026](lit/andeweg2026.md) — Andeweg, Kitching, Hummon (NIST): the
  newest competitor method, active **power-modulation** ac-Stark suppression
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
  (intermediate detunings 75 → 1 THz; see the strategy doc).

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

**Nanofibre bridge to Paper 2** (Gokhroo/Le Kien/Nic Chormaic lineage):
[gokhroo2022](lit/gokhroo2022.md) (the ONF two-peak pushing-dip analog),
`li2024perspective` (*J. Phys. Photonics* **6**,
021002, the standard ONF review), `sadeghi2026` (ONF cascaded fluorescence,
power-dependent surface shift, arXiv:2412.01099). The clean cell lineshape is the
reference against which ONF surface/pushing effects are read.

**[FEED] Pennetta et al. 2026** ([pennetta2026](lit/pennetta2026.md)) — the
nearest-platform result to Paper 2, feeding two of its pillars; NO committed number
moved. Two details beyond the lit-file summary: radial trap ~7 kHz, atom ~280 nm
from the surface; the Ramsey/spin-echo coherence times are records for the
platform. The two feeds:
- **It puts quantified atom–surface content on the near-surface potential** —
  Casimir–Polder plus surface-charge electrostatics — which is exactly what
  `gokhroo2022` left at the hypothesis stage (its dip has "no Casimir-Polder or
  van der Waals content at all"): a concrete ingredient for any Paper-2
  near-surface *lineshape* model.
- **Its coherence gain is a suppression of the trapping-light differential light
  shift.** The paper states the decoherence it beats "arises from
  motional-state-dependent differential light shifts … proportional to the
  intensity of the trapping fields," cured by holding atoms in low-light regions
  — a real-world confirmation, on Paper-2's own platform, that the
  **inhomogeneous/differential light shift is the coherence-limiting systematic
  in guided-atom systems**, which is the premise of our light-shift-distribution
  method (THEORY_NOTE §3), the M16 magic-wavelength toolkit, and the guided-mode
  framing in `PAPER2_SKELETON.md` §V–VI.

Platform caveats (so we do not overclaim): Cs not Rb, a D2 hyperfine qubit not the
5S–6S two-photon line, a 450 nm fibre not the OIST 650 nm — the *physics* (surface
forces; differential-light-shift dephasing) transfers, the numbers do not.

**[FEED] Pache et al. 2026** ([pache2026](lit/pache2026.md)) — the same group's
companion, on the loading and cooling toolkit for this platform, and a direct feed
to the EIT-cooling / atom-source thread; NO committed number moved. Why it feeds us
beyond the lit-file summary: it again names the **residual differential light
shift of the trapping fields** as the limiting imperfection — the recurring
guided-mode theme. Cs / D2 again: the physics transfers, the numbers do not.

**Prior-art audit on the pushing dip (2026-07-16).** Because a near-surface
lineshape is the natural Paper-2 direction, we checked whether anyone has since
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

**Scope caveat, recorded so we do not overclaim later:** the dip is a
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

**Near-surface Casimir–Polder shift read FROM a lineshape — template for Paper 2 §IV:**
- **[Ton, Kestler, Steck & Barreiro 2026](lit/ton2026.md)** — the state-of-the-art
  template for extracting a surface shift from the line; D. A. Steck (our
  constants lineage) is a co-author. [CITE — the model template for Paper 2's
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
  the near-surface shift as a thermal-averaged distribution in Paper 2 §IV. [CITE]
- **[Dutta et al. 2024](lit/dutta2024.md)** — higher-order CP corrections at
  close range: the background for Paper 2's near-surface term. [FEED]
- **[Sargsyan, Momier & Sarkisyan 2025](lit/sargsyan2025.md)** — the
  experimental analogue of extracting a surface shift from the line. [CITE]
- **[Piotrowski, Bach, Vera Paz, Schneeweiss & Rauschenbeutel 2026](lit/piotrowski2026.md)**
  — a Paper-2 feasibility bound on the probe window/power. [CITE]
- **[Wang, Cao, Yuan, Wang, Xiao & Jia 2025](lit/wang2025.md)** — directly on
  our 5S–7S ladder (the 741/728 nm channels set the ladder magic wavelength)
  and a multi-channel-detection precedent for the amplitude work. [CITE]

**Still to verify:** Sargsyan/Sarkisyan 2026 (arXiv:2601.04661, a second nanocell
surface-shift paper) and Obaze et al. 2025 (Photonics **12**, 513, a second 778 nm
clock review). **Quarantined (do NOT cite): arXiv:2602.07161** (malformed, re-surfaced).

**The ONF community map (why the nearest-platform refs cluster here).** The two poles
of the optical-nanofibre cold-atom field are the **Rauschenbeutel group** (Humboldt
Berlin; `pennetta2026`, `pache2026`) and the **Nic Chormaic group** (OIST; `nieddu2019`,
`rajasree2020`, `gokhroo2022` — our own provenance and Paper 2's platform); they
co-organise the ONNA (Optical Nanofibre Applications) conference series. So the newest
nearest-platform work is from Paper 2's own community — engaging it well is both good
scholarship and the natural way this program is read by that community.
