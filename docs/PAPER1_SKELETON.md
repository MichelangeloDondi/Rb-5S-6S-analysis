# Paper 1 — manuscript skeleton

**Status:** scaffold for Michelangelo (lead) + Síle to fill. This is the *narrative
structure* — the argument section by section, with each committed result slotted as
evidence and each figure assigned — not prose to submit. Numbers here are the
verified session values (see `docs/RESULTS.md` for the auto-generated ledger they
come from); provenance tags follow the house convention
(MEASURED-HERE / CALCULATED / ESTABLISHED / ENVELOPE / OPEN). Port to the journal
LaTeX template when structure is agreed. **Everything absolute is PRELIMINARY** —
it rides on the OPEN beam waist $w_0$; the fixed-lock session is what turns
the archival brackets into measurements, so several sections are written as
"archive brackets → a fixed-lock session resolves".

---

## 0. Framing decisions to settle first (not for the manuscript)

- **Central contribution / thesis.** The novel, defensible claim is a *method*, not a
  number: a **drift-immune lineshape-metrology method** built on the AC-Stark "ramp"
  of a focused two-photon transition (closed-form triangular law + moment method),
  demonstrated on a 2025 archive that *brackets* the collisional and AC-Stark
  coefficients and pins the systematics, then completed by a fixed-lock campaign. We
  do **not** claim to have measured either coefficient in the archive (both are
  bounds), and we do **not** claim the asymmetry's existence (Stalnaker *et al.* 2006
  precede us — §novelty).
- **Scope / journal.** Full paper (PRA-length). The archive gives **P1-min** (method +
  bounds, ready now = the thesis core); adding a fixed-lock session gives
  **P1-full** (the measured coefficients — the flagship). Default: **hold for P1-full**,
  one combined paper (§VII stubbed as predictions until such data exists),
  because the 5S–6S light shift / β_self is un-scooped and the field is not racing on
  this line. Fallback: publish P1-min now if a deadline/scoop forces it — and note this
  fallback is the *only* branch fully under our control, since no session is scheduled
  or agreed. The full contingency map — P1-min/full, the ONF Paper 2, and the Ti:Sapph
  5D/7S papers (A/B/C), as a function of which sessions happen — is in
  **`docs/PAPERS_PORTFOLIO.md`**. (Thesis vs papers: the thesis rides on the archive
  alone; any further session, whenever and by whoever it is run, feeds the papers.)
- **Author list & contributions**, target journal, and whether the ramp theory is a
  co-submitted companion or an appendix here (currently: appendix + `THEORY_NOTE.md`
  as the standalone version for a theorist reader).

---

## Title (candidates)

1. *Drift-immune lineshape metrology of the Rb 5S–6S two-photon transition via the
   AC-Stark ramp*
2. *Bounding collisional and AC-Stark shifts of Rb 5S₁/₂–6S₁/₂ from a drifted-lock
   archive, and a fixed-lock route to measurement*
3. *Two-epoch two-photon metrology: shapes without centres, then centres*

## Abstract (draft — honest, ~150 words)

> We study the Doppler-free 5S₁/₂→6S₁/₂ two-photon transition of Rb at 993 nm in a
> vapour cell as a testbed for lineshape metrology. A focused, retro-reflected beam
> imprints a spatially varying AC-Stark shift whose intensity-averaged distribution is
> a closed-form triangular "ramp"; we give its cumulants and show they furnish a
> **drift-immune** measurement channel. From a 2025 archive taken with a slowly
> drifting lock — line *shapes* intact, absolute *centres* lost — we bound the
> collisional self-broadening ($\beta_\text{self}\lesssim$ [X] MHz per $10^{12}$
> cm⁻³), show the fitted collisional width is a density-independent floor rather than
> a resolved rate, bound the laser linewidth, and confirm the ramp's power-law
> signatures, yielding an upper bound on the AC-Stark coefficient. Every absolute
> value is limited by the beam waist; we describe the fixed-lock, calibrated-waist
> campaign that converts these brackets into measurements. **[Fill X and the σ_laser,
> S₀ numbers from §VI once the headline framing is agreed.]**

---

## I. Introduction

- The 5S→6S two-photon transition: why it matters (a forbidden-ish, narrow, metrology-
  relevant line; the 6S state; relation to the 5D/7S self-shift series — Zameroski,
  ESTABLISHED). One paragraph.
- **Prior work on this exact line, and the gap we fill.** The USAF Academy group did
  precision hyperfine/isotope-shift metrology on 5S–6S (Orson 2021; Ayachitula 2024 —
  kHz $A(6S)$, our source for the hyperfine constants) and, directly relevant here,
  *looked* for the AC-Stark and collisional-density shifts and reported **nulls at
  ~6 MHz resolution** (Orson 2021, over $N \gtrsim 3\times10^{11}$ cm$^{-3}$). The
  OIST group demonstrated a 993 nm frequency reference on it (Nieddu 2019). Our angle
  is orthogonal to all of these: a *drift-immune* method that turns the archive's
  shape information into bounds on those very shifts *below* the prior resolution
  floor, plus the two-epoch route to the coefficients themselves.
- The problem this paper is really about: **absolute frequency metrology in a drifting
  system.** A slow lock drift destroys line *centres* but not *shapes*. In a focused
  beam the AC-Stark shift is not one number but a *ramp* (edge→centre = 0→S₀), which
  leaves three fingerprints on the line: the **pull** (centroid −⅔S₀, ∝S₀), the
  **width** (∝S₀²) and the **asymmetry/skew** (∝S₀³). The pull is a position and dies
  with the drifting centre; the width and skew are *shape* properties and survive. So
  the honest question the archive answers: what can the drift-invariant shape deliver,
  and what still needs a stable lock? — the two-epoch idea. Frame it here.
- **The AC-Stark ramp as an observable, not a nuisance — stated honestly.** The
  precision-clock community treats this shift as *the* systematic to suppress, almost
  always *actively* (power modulation — Andeweg 2026, Yudin 2020; dual interrogation —
  Gerginov 2018, Li 2024; two-color/magic-wavelength — Ahern 2025, Hamilton 2023), and
  the asymmetry itself has been treated as a distortion to *eliminate* (Antypas 2018).
  We instead read the shift off the drift-invariant shape — a **passive, reference-free,
  no-extra-hardware** route. **Be precise about the novelty (do not overclaim):** the
  asymmetric AC-Stark lineshape is not new (Wieman 1987), and a polarizability has
  already been *extracted from it* (Stalnaker 2006, with a stable reference and a
  full-shape numerical fit). What is genuinely ours is (i) extraction from the shape
  *alone*, surviving a reference too unstable for the centre; (ii) a **closed-form
  two-photon** triangular ramp law (signal ∝ I², vs Stalnaker's numerical one-photon
  standing wave); (iii) the **two-epoch** design. The method is *complementary* to the
  active schemes — its systematics are orthogonal and it needs no feedback or second
  laser — **not** a precision competitor to them.
- **What the archive can and cannot do (set expectations early).** The drift-invariant
  handles are weak: width ∝S₀² and skew ∝S₀³, and the skew is further contaminated by
  shot-noise skewness (∝1/√counts) and instrument asymmetry. At the archival S₀ ≈ 0.6
  MHz they are **below detection → the archival AC-Stark result is a BOUND, not a
  measurement**, and β_self likewise. This is not a hedge but the point: the archive
  rigorously delivers *bounds + a validated method*; the fixed-lock small-waist epoch
  (S₀ several MHz — skew ~×64 — with the pull resurrected) delivers the *coefficients*.
- Contributions list (3–4 bullets): the closed-form fringe-averaged two-photon ramp
  law; the drift-immune moment method + its honest reach (bounds now, values in
  a fixed-lock session); the archival bounds + systematics catalogue; the two-epoch/fixed-lock
  route. End of intro.

## II. The two-epoch design (methodological spine)

> **First-pass prose drafted** in [`paper1/drafts/II_two_epoch.md`](paper1/drafts/II_two_epoch.md) — for MD/Síle to revise. The stubs below are the outline it expands.

- **Epoch 1 (2025, this archive):** lock drifts ~MHz/min. Centres dead → *shapes* and
  *relative* structure survive; every per-scan centre is a free nuisance. What this
  licenses: widths, power/density scalings, ramp *shape* moments. What it forbids:
  absolute shifts.
- **Epoch 2 (Oct 2026, fixed lock):** centres → the first absolute AC-Stark and
  collisional self-shift coefficients; a knife-edge $w_0$ sets every absolute scale.
- State plainly: **the dominant systematic throughout is the OPEN beam waist $w_0$**
  (beam clipped by the 3 mm EOM aperture, tens-of-% uncertain). Every "absolute"
  archival number is conditional on it. This is the honest through-line of the paper.

## III. Lineshape model and the AC-Stark ramp *(theory — full derivation in App. A; `THEORY_NOTE.md`)*

- The composite line: natural Lorentzian ($\Gamma_\text{nat}=3.4926$ MHz, ESTABLISHED)
  $\otimes$ transit kernel $\otimes$ laser Gaussian $\otimes$ AC-Stark ramp, on the
  transition (two-photon-sum) axis.
- **Transit kernel** (ESTABLISHED, not phenomenological): Lorentzian $\otimes$
  two-sided exponential = Biraben–Bassini–Cagnac (1979); modern closed transit-limit
  form = Lehmann (2021). Cite, don't reinvent (App. B / LITERATURE.md).
- **The ramp law** (the novel core, CALCULATED): signal $\propto I^2$, shift
  $\propto I$, volume measure $\Rightarrow$ density $f(s)\propto|s|^{n-1}$ on
  $[-S_0,0]$; the triangle for $n=2$. Cumulants: pull $-\tfrac{2}{3}S_0$, excess
  variance $S_0^2/18$, third cumulant $S_0^3/135$; standardized skew $g_1=0.566$
  (vs 0 for the one-photon uniform ramp — the skew *exists* only because the signal
  goes as $I^2$).
- **The drift-immune method:** in a drifted archive the first-order pull is degenerate
  with the free per-scan centre and *absorbed*; the **skew** is the drift-immune
  handle (∝$S_0^3$, below the archival floor → a bound). With a fixed lock
  un-absorbs the pull (the sensitive handle). The "principled hybrid": fit ONE $S_0$
  per condition, check pull/variance/skew as three analytic functionals of it.
- **The $\langle E^2\rangle$ convention, pinned** (CALCULATED): standard AMO
  $\Delta E=-\tfrac14\alpha E_0^2$; $S_0=\Delta\alpha\cdot I_\text{eff}/(2\varepsilon_0 c h)$,
  $I_\text{eff}=(1{+}\rho)\cdot 2P/(\pi w_0^2)$; no coherent $\times2$ (fringe-averaged,
  Stalnaker FM regime). $\Rightarrow S_0=0.59$ MHz at 225 mW, 50 µm, $\rho{=}1$
  (5.7 MHz at 16 µm). Sign set by $\mathrm{sign}(\Delta\alpha)>0$ (red). *[App. A]*

## IV. Apparatus and the 2025 archive

- Cell, oven (70–130 °C), 993 nm laser, EOM retro-reflection (retro ratio $\rho$),
  fluorescence collection. The EOM 3 mm aperture → the $w_0$ clip (tie to §II).
- The archive: 297 unique traces (MD5-deduped from 722 files), 4 hyperfine peaks —
  ⁸⁵Rb (993.4154, 993.4192 nm) and ⁸⁷Rb (993.4121, 993.4207 nm) — a temperature
  sweep (70/90/110 °C) and a power sweep (25–225 mW at 130 °C). Chronology: P-session
  at 130 °C first, then cooling.
- **Provenance & curation** (App. C): pre-registered hard/soft QC; 4 curation
  discards + 29 session-grain quarantines (the aborted 130 °C attempt), each with a
  committed `qc_reason`. Emphasise the exclusion granularity (whole bad sessions, not
  inconvenient points) as the anti-cherry-pick control.

## V. Analysis

> **First-pass prose drafted** in [`paper1/drafts/V_analysis.md`](paper1/drafts/V_analysis.md) — for MD/Síle to revise. The stubs below are the outline it expands.

- **Frequency axis (MEASURED-HERE):** EOM sidebands as a ruler → 0.04257(5) MHz/ms
  laser-axis (0.08514 transition), per-block, sweep linear to <0.4%. The fold-robust
  ruler argument (symmetric triangle) and the adaptive window for off-centre-sweep
  mirror crossings. *[one figure-free subsection]*
- **Noise model:** per-condition variance law + correlation time $\tau_\text{int}$
  weighting; the low-power residual skew is Poisson shot noise (∝$1/\sqrt{\text{counts}}$),
  *identified*, not the ramp (§VI.C).
- **The fit hierarchy & its degeneracies.** Per-trace amplitude/centre/baseline
  (drift lives here); shared $\gamma_\text{coll}(T){=}\beta N(T)$, $\sigma_\text{laser}(T)$,
  transit($\sqrt T$). The $\sigma_\text{laser}\leftrightarrow\gamma_\text{coll}$ Voigt
  degeneracy (corr $\approx-0.85$) and the transit$\leftrightarrow w_0$ degeneracy —
  state honestly that the *total* width is robust, the *split* is not. Covariances
  fold in the anticorrelation (App. D).

## VI. Results

### VI.A Collisional self-broadening $\beta_\text{self}$ — a bound *(headline archival result)* — Figs. 1, 5, 6

> **First-pass prose drafted** in [`paper1/drafts/VI-A_beta.md`](paper1/drafts/VI-A_beta.md) — for MD/Síle to revise. The stubs below are the outline it expands.

- **Model-independent width-slope bound** (the headline): raw widths are non-monotonic
  in density for 3/4 peaks — impossible for real collisions — because between-block
  $\sigma_\text{laser}$ drift ($\sim0.06$–$0.16$ MHz) $\approx$ the whole collisional
  trend. $\Rightarrow \beta_\text{self}\lesssim 0.2$–$0.4$ MHz per $10^{12}$ cm⁻³
  (95% per peak: $t(1)=6.31$ on the 1-DOF scatter, ×1.2 density scale)
  ($\approx2\sigma$, per peak). Each bound carries a factor-$\sim$2 own-uncertainty
  (1–2 residual DOF) — quote to 2 figures.
- **The lever test (why it is a *bound*, not a value)** — Fig. 6. The fitted
  $\gamma_\text{coll}$ rises only $\times1.5$ across a $\times52$ density span
  (70→130 °C): a residual *floor*, not the linear scaling a real binary-collision
  width demands. Consistently, the hierarchical $\beta$ collapses $0.036\to0.014$ when
  the (cross-session) 130 °C lever is added; per-condition $\beta\sim0.01$. So $\beta$
  is lever- and model-dependent — the definition of a bound.
- **Hierarchical cross-check + isotope test:** $\beta_{85}=\beta_{87}=0.036(4)$
  (STAT-only), no isotope dependence ($0.0\sigma$); four separate error bars
  (statistical / transit model-form $\pm0.033$ / density scale $\pm0.007$ /
  $w_0$-band $[0.004,0.055]$, the largest). Robust to leave-one-**peak**-out (4207 moves $\beta_{87}$ by $-0.004$,
  $<1\sigma$; drops neither $\beta$ nor the $\sigma_\text{laser}(T)$ trend).
- **Expectation context:** Zameroski 7S scaling ⇒ expected $\beta_\text{self}(6S)\sim$
  1 kHz per $10^{12}$ cm⁻³ ⇒ the bound is $\sim$40–100× above expectation (consistent,
  not constraining). A fixed-lock session needs same-session 150–170 °C points (Δγ measurable).
- *Message:* the archive *proves the two-epoch design was necessary* — this bound is
  a Paper-1 result in itself, and the naive global Voigt fit's 4–10σ "detection" is
  the cautionary tale.

### VI.B The 2025 laser linewidth $\sigma_\text{laser}$ — an upper bound — Fig. 5B

- $\sigma_\text{laser}\lesssim 1.1$ MHz laser-axis (ENVELOPE / OPEN via $w_0$;
  $=0$ if $w_0\lesssim16$ µm). Slow within-scan drift is *not* the cause ($\sim0.01$
  MHz/scan). The per-T sharing across peaks is M4c-validated ($\chi^2/\text{dof}<1$);
  the $\sigma_\text{laser}(T)$ trend is the $\beta\leftrightarrow\sigma_\text{laser}$
  degeneracy, not physical drift. A baseline for the ONF/Paper-2 work.

### VI.C Power sweep — the ramp-law predictions confirmed — Fig. 2

> **First-pass prose drafted** (with §VI.D) in [`paper1/drafts/VI-CD_power_stark.md`](paper1/drafts/VI-CD_power_stark.md) — for MD/Síle to revise. The stubs below are the outline it expands.

- **C3a** linewidth flat ($\lesssim2\%$ over $9\times$ power — the ramp adds
  $\propto S_0^2$, negligible). **C3b** amplitude $\propto P^2$ (log-log slopes
  1.83–2.12; 4121 low end = saturation-vs-trapping degeneracy, say "consistent with").
  **C3c** asymmetry below the archival floor — a bound; the large low-power residual
  skew is **shot noise** (∝amp$^{-0.5}$), identified, opposite sign+scaling to the
  ramp. The old "power null" recast as *confirmed prediction*.

### VI.D AC-Stark coefficient — a bound from the power lever — (Fig. 2 inset / new panel)

> **First-pass prose drafted** (with §VI.C) in [`paper1/drafts/VI-CD_power_stark.md`](paper1/drafts/VI-CD_power_stark.md).

- Joint fit of one $\kappa$ ($S_0=\kappa P$) to the four peaks' width-vs-power:
  **$S_0(225\text{ mW}) < 0.63$ MHz (95%, profile likelihood)**, fit $0.0$, sitting
  just above the predicted 0.59. A bound (the pull is dead; only the $\propto S_0^2$
  width handle is live); the fit rails at $\kappa=0$, so the limit is a profile scan
  ($\Delta\chi^2 = 2.706\times\chi^2_\text{red}$), not a Wald interval.
  Via §III's convention at nominal $w_0=50$ µm ⇒ $\Delta\alpha < \sim1200$ a.u.,
  consistent with the computed 1093 — the archive does **not** contradict the theory,
  and its width data are already sensitive at the scale of the predicted coefficient.

### VI.E Supporting / systematics — Figs. 3, 4

- Transit-broadening Monte Carlo (Fig. 3): the flux-corrected transit adds
  $\sim2.1$ MHz@32 µm (which OVERSHOOTS the observed line, excluding 32 µm) and
  $\sim1.2$@50 µm — degenerate with $\sigma_\text{laser}$ through $w_0$ (crossover
  $\sim18$–20 µm). Sets the transit subtraction the fixed-lock session's knife-edge $w_0$ enables.
- Degeneracy-law amplitude ratios (Fig. 4): predicted abundance$\times(2F{+}1)$;
  measured ratios swing 30–50% between blocks (drift) → untestable in the archive, a
  cross-peak systematic interleaving in a fixed-lock session fixes. Bounds cross-peak comparisons.

## VII. The fixed-lock session *(predictions & what it would resolve)*

*Written as predictions against a session that is specified but not scheduled
(`PLAN.md` §8) — if no such data exists by writing time, this section either
states the predictions as future work (P1-min) or is dropped.*

- **Knife-edge $w_0$** (+ collection profile): collapses the transit$\leftrightarrow
  \sigma_\text{laser}$ degeneracy, sets every absolute scale. Highest priority of
  the specification, and the one item worth doing even standalone.
- **Fixed-lock centres:** first absolute AC-Stark shift (the pull $\propto S_0$,
  un-absorbed) and collisional self-shift. Small waist ($S_0$ 4× larger) makes the
  $\propto S_0^3$ skew a detection; the axial-averaged ramp predicts a **skew
  sign-flip** with collection window (a config-differential test immune to
  instrumental asymmetry).
- **Same-session high-density (150–170 °C):** the only way to resolve the collisional
  slope (the archive's cross-session lever does not combine — §VI.A).
- **Interleaved peaks + logged power/timestamps:** cross-peak systematics 30–50% →
  few %, enabling the degeneracy-law and trapping tests. *(Design of record: PLAN §8.)*

## VIII. Conclusion

- What the archive rigorously delivers (bounds on β and $\sigma_\text{laser}$;
  confirmed ramp power laws; an $S_0$ bracket; a validated method and systematics
  catalogue) vs what needs the fixed lock. The two-epoch design as a transferable
  template for metrology in drifting systems. Bridge to the nanofibre lineshape
  (Paper 2).

## Appendices

- **A. The ramp law derivation** — $I^2$-excitation/$I$-shift → $f(s)\propto|s|^{n-1}$;
  cumulants; the $\langle E^2\rangle$ convention; the diverging-beam axial average and
  the OPEN $Z_c/z_R$ (from `THEORY_NOTE.md` §§2,3,5,7).
- **B. The transit kernel** — Biraben/Bordé/Lehmann provenance (`LITERATURE.md` §3).
- **C. QC, curation, and provenance** — the pre-registered hard/soft policy; the 4
  discards + 29 quarantines with committed `qc_reason`; the curation audit.
- **D. Degeneracies and honest covariances** — the Voigt and transit/$w_0$
  degeneracies; why the naive global Voigt fit is overconfident (§4.5 cautionary tale).

---

## Figure assignments (all committed, `figures/`)

| # | file | section | one-line role |
|---|---|---|---|
| 1 | `fig1_width_vs_density.png` | VI.A | per-peak width vs density (the raw non-monotonicity) |
| 2 | `fig2_power_sweep.png` | VI.C | width flat / amp ∝P² / skew vs power |
| 3 | `fig3_transit_mc.png` | VI.E | transit-broadening MC vs $w_0$ |
| 4 | `fig4_amplitude_ratios.png` | VI.E | degeneracy-law area ratios (drift-limited) |
| 5 | `fig5_pooled_width.png` | VI.A/B | pooled width vs density + $\sigma_\text{laser}(T)$ companion |
| 6 | `fig6_gamma_floor.png` | VI.A | the lever test — $\gamma_\text{coll}$ is a floor |

*Possible additions:* a VI.D panel (κ / $S_0$ bound vs power) if VI.D grows beyond an
inset; a §III schematic of the ramp geometry + the triangular $f(s)$.

## Key numbers to keep synchronized with `docs/RESULTS.md` (do not hand-retype elsewhere)

- $\beta_\text{self}$ bound $0.2$–$0.4$ (95%, t + N-scale); hierarchical $0.036(4)$; lever $\to 0.014$;
  γ rise $\times1.85$ / $\times53$. — $\sigma_\text{laser}\lesssim1.0$ laser.
- $S_0(225) < 0.63$ MHz (95%, profile), pred. 0.59; $\Delta\alpha < \sim1200$ a.u.
- rate $0.04257(5)$ MHz/ms laser; $\Gamma_\text{nat}=3.4926$ MHz; $w_0$ nominal 50 µm (OPEN).

## Reference anchors (BibTeX in [`references.bib`](references.bib); prose ledger in `LITERATURE.md`)

Biraben, Bassini & Cagnac, *J. Phys. (Paris)* **40**, 445 (1979) · Bordé, *C. R. Acad.
Sci. B* **282**, 341 (1976) · Lehmann, *J. Chem. Phys.* **154**, 104105 (2021) ·
Stalnaker *et al.*, *Phys. Rev. A* **73**, 043416 (2006) · Grimm, Weidemüller &
Ovchinnikov, *Adv. At. Mol. Opt. Phys.* **42**, 95 (2000) · Zameroski *et al.*,
*J. Phys. B* **47**, 225205 (2014) · Gokhroo, Le Kien & Nic Chormaic, *J. Phys. B*
**55**, 125301 (2022) [Paper 2].
