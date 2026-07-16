# From-scratch analysis plan — Rb 5S₁/₂→6S₁/₂ two-photon, 2025 archival campaign

*Analysis plan of record for the 2025 archive, v1.1 (2026-07-11); §§7–9 are a
specification for possible future sessions, not a schedule or an agreement.
Supersedes the initial-brief pipeline (§6) where they conflict. Old code in the
previous repository is never read or reused; old outputs serve only as external
cross-check targets.*

## 0. What the analysis is for (Paper 1 claims)

From the 2025 archival data:
- **C1** First determination — or honest bound — of collisional self-broadening β_self of the 5S→6S line vs Rb density (T-sweep).
- **C2** Quantitative characterization of the 2025-epoch laser (within-scan kernel + drift diary). Supporting deliverable; also the starting linewidth baseline for any ONF work on this line.
- **C3** Power nulls as *predictions confirmed*: FWHM inflation ≤2% and asymmetry ≤10⁻⁴ across 25–225 mW, as required by the intensity-averaging (ramp) law. Measured sensitivity quoted alongside.

Reserved for a fixed-lock session (specified in §8; not scheduled): AC-Stark coefficient (P up to ~1 W, ramp-cliff regime), collisional self-shift, direct high-power lineshape test, Lehmann-cusp attempt. The pipeline below must ingest such data unchanged.

**Which papers this produces under which sessions (a fixed-lock cell session × ONF × the Ti:Sapph 5D/7S extension) is mapped in `docs/PAPERS_PORTFOLIO.md`** — the archive alone is P1-min (method + bounds = the thesis core); a fixed-lock session gives P1-full (measured coefficients); ONF gives Paper 2; a 5D/7S session gives Papers A/B/C (`FUTURE_TRANSITIONS_titsapph.md`). None of these sessions is scheduled or agreed.

## 1. Ground rules

- **Axis**: transition (sum) frequency everywhere; laser axis = ×½, stated once in the paper.
- **Provenance tags** on every number: ESTABLISHED / MEASURED-HERE / CALCULATED / ENVELOPE / OPEN / DESCOPED.
- **Closure testing before real data**: every module passes synthetic-data closure tests (known truth injected, recovered within quoted errors) before touching a real trace. End-to-end: a full synthetic campaign (drift + sweep nonlinearity + noise model included) must return the injected β_self and laser widths inside error bars.
- **Dedupe by MD5** at ingest (two byte-identical double-saves exist).
- **Quarantine**: `4154nm_130c_{025,125,225}mw*` (aborted first attempt, user-flagged suspicious) and the non-underscore `4154nm_eom_before/after` brackets (plausibly its rulers) are excluded from all headline fits. Revisit only if their origin is clarified.
- **Discarded shots**: traces the experimenter rejected at curation time ("seemed quite bad"; they exist only in the old `raw/` dump) live under `data_raw/discarded/` and likewise never enter headline fits — the selection predates the analysis, so honoring it cannot bias results. M0's objective QC runs on them only as an appendix consistency check on the curation.
- **Engineering** (user directive 2026-07-11): separate clean repository; physics constants in `rb5s6s/constants.py`, tunables in `rb5s6s/config.py`, nothing numeric hard-coded elsewhere; verbose bus-test documentation (Zohreh must be able to take over); pytest battery + CI on every push; functions/modules per pipeline stage.

## 2. Data manifest

See `docs/DATA.md` for the full decoded-archive story and `data_raw/MANIFEST.csv`
for the per-trace table (role, condition, chronology, flags, MD5, original paths).

Chronology (user): P-session at 130 °C (per peak: before-block → 25→75→125→175→225 → after-block), then stepwise cooling 110 → 90 → 70. Repeat indices chronological (a few possible swaps). Repeats within a block are back-to-back (measured position scatter 1.8 ms ≈ 0.08 MHz laser). No timestamps exist anywhere; block order is the only time coordinate. Scope horizontal-knob and cavity-reference recenters occurred between saves ⇒ absolute positions carry no meaning across saves.

**Assumption A1 (to confirm, one word)**: scope triggered on the sweep sync, so file time = ramp phase. Evidence: frozen repeat positions; window (1.000 s) ≈ one up-ramp (~43 MHz laser at measured rate ≈ user's "~45 MHz"). If false, Module M2 degrades gracefully to per-trace calibration.

## 3. Modules (each gates the next)

**M0 — Ingest & QC.** Parse (2-line header, 2000 pts, 0.5 ms), MD5-dedupe, per-trace QC (baseline level/slope, wing noise, clipping, peak-in-window), manifest with block IDs + chronological order. Output: tidy per-trace table. *(Import + manifest implemented in `scripts/import_data.py`; QC metrics to follow.)*

**M1 — Noise model.** *(runs before the axis fits so every fit inherits correct weights)* Detrended within-trace residual variance vs signal level, per condition (RF-off traces first — single smooth line, easy detrend); noise(V) curve + residual autocorrelation scale → weighted least squares and error inflation for every fit in this pipeline; check growth of Fano-like factor with T (radiation-trapping proxy). Old residuals already show signal-correlated noise (±1% wings → ±5% peak). One noise↔fit refinement iteration allowed; its convergence verified on synthetics.

**M2 — Frequency axis (ruler).** EOM traces are used *only* as frequency ruler and drift/stationarity monitors; their heights/widths never enter physics fits except as cross-checks. Staged per-trace protocol — no threshold peak-picking at any stage (user directive 2026-07-11):
1. *Robust init*: autocorrelation of the baseline-subtracted trace → tooth period Δ (uses all teeth at once; indifferent to a weak/suppressed carrier); cross-correlation against a synthetic comb template → comb phase t₀; grid-search fallback on (Δ, t₀).
2. *Constrained comb fit (workhorse)*: ONE simultaneous model — centers t₀ + nΔ (+ optional quadratic axis term), n = −2..+2, one shared lineshape, free per-tooth heights, linear background, weights from M1. Simultaneous fitting is mandatory: teeth ~147 ms apart at ~60 ms width overlap at the wing level (a strong tooth's Lorentzian wing under a weak neighbor ≈ 20% of the weak peak → O(ms) center pull if teeth are fit singly or read as maxima).
3. *Shape ladder*: shared shape Lorentzian → Voigt → exponential-wing (transit-like); selection by BIC; spread across shape choices booked as a model systematic.
4. *Free-center diagnostic*: refit with per-tooth free centers (shape still shared); center-vs-n residuals measure local sweep nonlinearity and validate stage 2's axis term.
5. *Tooth count*: extend to n = ±3/±4 (7- or 9-tooth model) when BIC favors it — wider lever arm for Δ and curvature (one n=−4 candidate already sighted).
6. *Combination & errors*: per-trace Δ → block-level inverse-variance mean with scatter inflation when block χ²_red > 1; before-vs-after consistency per peak (discrepancy → interpolate across the block sequence and book the difference as systematic); ensemble stitch of the ν(t) nonlinearity map (requires A1; else per-trace linear axes). Outlier policy pre-registered: QC-based, never result-based. Coverage of all quoted errors verified on synthetic rulers (known Δ, curvature, noise(V), suppressed carrier, missing teeth).

Per-trace rate = 6.25 MHz / Δ (laser axis; CALCULATED from Ω/2 selection rules, locked by the observed 5-tooth amplitude pattern). Deliverables: axis function per block, stat + syst; target ≤1% axis systematic. Quick-look seeds — finder-level, possibly carrying ms-scale overlap bias, to be superseded by this module: spacing ≈ 146 ± 1 ms (warm blocks), rate ≈ 0.0428 MHz/ms laser, block spread 0.6% RMS (MEASURED-HERE, preliminary).

*Verified refinements (independent audit, 2026-07-11):* cross-correlation alignment of ruler repeats must restrict the lag search to < half a tooth period — naive global alignment locked 3/5 cold-ruler traces one tooth off. Pooled cold-block traces calibrate tooth SPACING only (real ±13 ms inter-trace drift smears pooled centers; SNR gain ≈1.6×, not √N); per-trace fits of the 2–3 brightest teeth converge even at SNR 2–3 and are the preferred cold-block estimator (cold spacing ≈145 ms, consistent with the campaign rate). `4192nm_eom_070c3` is a partial ruler (1 valid tooth, tail lost to export dropout; RF label verified) — unusable for spacing. **The sweep turnaround can sit INSIDE the window**: in the 4207 nm 25 mW block the triangle folds at t ≈ 432 ms and the retrace re-crosses the line near the window edge ⇒ the ν(t) map must be fold-aware, and folded blocks provide a free up/down-ramp consistency check.

**M3 — Lineshape model & decomposition.** Physics-anchored convolution, transition axis: Lorentzian Γ_nat = 3.494 MHz (fixed; ESTABLISHED) ⊛ Lehmann transit kernel (exponential-wing shape fixed; one global width parameter with enforced √T scaling; prior from w₀ ≈ 50 µm, tens-of-% — OPEN until knife-edge) ⊛ laser kernel per block (Gaussian core + optional Lorentzian tail) ⊛ AC-Stark ramp (fixed prediction per power; f(s) ∝ |s| on [−S₀,0]) + linear background. Joint fit per condition: shared shape across the 5 repeats, per-trace amplitude/center/background. Closure test must demonstrate σ_laser ↔ γ_coll separability at SNR 130 and quantify leakage (this is the fit-level face of the confound). *Verified additions (2026-07-11):* mask sweep-retrace crossings (second above-half region — real signal, confirmed in the 4207 nm 25 mW block) rather than excluding traces; allow a low-order (quadratic) baseline where a block shows a shared slow bow (verified ~0.5 mV across the entire 4207 nm 70 °C block, keepers and discard alike).

**M4 — β_self & the confound program.** γ_coll = β_self·N(T), N(T) from a stated vapor-pressure correlation (carry its systematic; add cell cold-spot caveat). **Temperature is monotonic with time across the whole campaign (130 first … 70 last): ordering de-confounds nothing.** Stationarity probes instead: (i) P-session widths vs block order at fixed 130 °C — hours-scale drift monitor, since power's true width effect is ≤2% (CALCULATED); (ii) before/after bracket tooth *widths* per peak — fixed-condition drift over each peak's session; (iii) cross-peak γ consistency at fixed T (four lines, one density); (iv) σ_laser(block) time series from M3. **Pre-registered rule: quote a measurement iff the probes bound the drift contribution ≤ ~⅓ of the observed γ(T) trend; otherwise a bound.** Bonus replicate: ruler tooth widths vs T form a hidden second T-sweep (cross-check only).

*M4 addendum — hierarchical `fit_global` design (2026-07-11).*
The cross-TEMPERATURE pooling already exists (`fit_beta_self`: one β_self and
one σ_laser shared across a peak's T-sweep). The reviewer's proposed extension
— pooling all 4 peaks × 5 repeats — is accepted with one amendment **our own
M4 result forces**: σ_laser must NOT be shared across time-separated blocks in
the 2025 epoch. The model-independent probe showed between-block σ_laser drift
(~0.06–0.16 MHz) is the dominant systematic; sharing one σ_laser is exactly
why the global fit reported 4–10σ where the honest answer is a bound. Sharing
structure for a future `fit_global`: **β_self per isotope** (per-line as a
tested variant — collision physics does not license one global β); **transit
shared globally** (same beam, √T scaling); **s0(P) shared globally** with
per-line residuals (= the differential-Stark signal); **σ_laser per block**
with a drift hyperprior (penalty scale ≈ the measured 0.1 MHz, a poor-man's
random effect); amplitude/center/tilted baseline per trace, as now. Plus a
leave-one-condition-out diagnostic on every shared parameter, and per-block
ruler-rate uncertainties propagated into the stack. For a fixed-lock session
the reviewer's structure applies verbatim — σ_laser genuinely global.

**M5 — 2025 laser epoch.** Laser kernel per block from M3 (two-photon ×2 convention explicit); coarse drift diary from bracket comb positions (upper bound only — knob moves alias). Deliverable table + figure.

**M6 — Power sweep as prediction test.** Width vs P against the ≤2% ramp-law prediction; fitted-asymmetry bound (expected 10⁻⁴, sensitivity ~10⁻³); amplitude vs P against ∝P² (saturation/linearity check). Turns the old null into C3.

**M7 — Amplitudes vs density.** Peak amplitudes across T per peak; ratios against Nieddu's same-channel baseline; radiation-trapping rollover curve (with M1's Fano trend as corroboration).

**M8 — Outputs.** Per-module CSV/JSON + figures, provenance-tagged; final table with stat/syst split; comparison appendix vs rescaled old-pipeline trends (external check only).

## 4. Non-goals (archival)

Line centers and absolute frequencies (drift; knob moves); skew as a *measurement* (bound only — dead at 10⁻⁴ vs 10⁻³ noise, CALCULATED); EOM modulation depth β (drive voltage unrecorded — DESCOPED, revives in a fixed-lock session); wide scans (identification already closed by the hyperfine label-spacing check, CALCULATED ~1%, encoded as a permanent test).

## 5. Standing micro-questions (non-blocking)

1. A1 trigger-sync confirmation (one word).
2. Peak order within each session (4207→4192→4154→4121?) — refines drift interpolation, not required.
3. If the aborted 4154 attempt's story ever resurfaces: did the underscore bracket re-take follow it?
4. **Does the 2025 archive hold a per-peak wavemeter reading?** (asked 2026-07-11). If the wide identification scans logged the HighFinesse value at each of the four peaks, those four readings vs the known hyperfine intervals give a free GHz-baseline linearity check of the 2025 wavemeter (§7.2). Check the archive / ask Zohreh. If absent, this cross-check waits for a fixed-lock session — no loss, since archival centers are dead anyway.

## 6. Verification

Synthetic closure per module; end-to-end synthetic campaign (full trace count, injected β_self, laser kernels, nonlinear axis, noise model, drift + recenters) recovered within quoted errors; only then real data. Real-data acceptance checks: rate consistency across the ~22 ruler blocks; cross-peak γ agreement at fixed T; M6 nulls.

## 7. Wavemeter calibration (shot list)

**Direction of calibration (the load-bearing point):** the accuracy hierarchy
is atoms (5S→6S hyperfine centers, ~kHz — Ayachitula 2024) ≫ EOM comb
(6.25 MHz laser-axis teeth, RF-exact intervals) ≫ HighFinesse wavemeter
(~10 MHz). The wavemeter is the LEAST accurate reference, so our data
calibrate the instrument, never the reverse. Absolute wavemeter calibration
is a near-free **byproduct**, NOT on the critical path — Paper 1's a fixed-lock session
targets are frequency *shifts* (AC-Stark vs P, collisional vs density), which
are differences that ignore the wavemeter's absolute offset; and absolute
centers belong to Ayachitula 2024 at kHz (a declared non-goal, §4).

For the shift grids use a **three-way chain**, not the wavemeter alone:
EOM comb = fine axis *within* a scan (the arbiter of the shift); atoms = one
absolute anchor; wavemeter = the **transfer standard** that tracks frequency
*between* scans (across P / T settings), its scale checked against the four
peaks and its offset anchored by the atoms.

Shots (add to the Week-1 cell list):
1. **Absolute offset (byproduct).** At a reference condition, record the
   wavemeter reading against a cleanly-identified peak → wavemeter offset
   = W_read − ν₀(known). Re-anchor per session (HighFinesse has its own
   temperature/pressure drift; the atoms, present in every scan, are the
   reference to lean on).
2. **GHz-baseline linearity.** Record the wavemeter at all four peaks; the
   known hyperfine intervals (kHz) test the wavemeter's scale over ~GHz.
3. **MHz cross-check during the shift grids.** Log the wavemeter continuously
   and compare its reported shifts to the EOM comb — the comb wins; this only
   validates that the wavemeter is a faithful *transfer* standard over the
   small (MHz) shift range, where it is normally too coarse to be the ruler.

Caveat: the comb calibrates the SCAN/scope axis (already done by M2), not the
wavemeter directly — so the wavemeter's own scale must come from shot 2, not
from the comb.

## 8. What a fixed-lock session must measure (specification, revised 2026-07-12)

**Status: a specification, not a schedule or an agreement.** Nothing below has been
agreed with the group, no date is assumed, and no particular person is assumed to
run it. It is written so that whoever has the cell and the beam time can execute it,
in whole or — following the priority order in §8.0 — as far down the list as the
available time allows. Each item names the archival bound it converts into a
measurement, so a *partial* session is still worth running and its value is
predictable in advance.

Constraint set: no more power (225 mW ceiling); telescope before the EOM and
lens swaps ARE allowed; repeats across days and orders are allowed. Core
architecture (survived review): **the telescope is an intensity
knob** — I ∝ P/w₀² buys the intensity sweep the power budget denies — and
**the opposite-order T grid** attacks the drift-density confound that killed
2025. Three fixes are built in below: an orthogonal absolute
intensity calibration (§8.2), the skew hunt demoted from promised headline to
a sized detection attempt inside a moment hierarchy (§8.3), and a closing
time budget with two waists, not three (§8.5).

### 8.0 Impact priorities (ranked) — what to protect if the budget shrinks

The session's job is **bounds → measurements**. Rank effort by *which bound becomes a
measurement, and how absolute* — not by data volume. If a day is lost, cut from the
bottom of this list, never the top.

**Tier 0 — the systematic floor (protect first; the single biggest impact, and not a "more data" knob):**
1. **Knife-edge w₀, per config.** $S_0\propto 1/w_0^2$ and β_self rides on transit($w_0$),
   so w₀ sets the systematic on *every* absolute number (a 10% w₀ error → **20% on Δα**)
   *and* collapses the transit↔σ_laser degeneracy (the only reason σ_laser is a bound).
   This is the difference between "w₀-conditional bracket" and "absolute measurement."
2. **Retro-ratio ρ in situ, per config.** $S_0\propto(1+\rho)$; without ρ the absolute
   Δα carries a ~2× ambiguity. Cheap, essential.

**Tier 1 — enablers (the measurement does not exist without them):**
3. **150–170 °C, SAME session, INTERLEAVED T order.** The β_self / self-shift lever:
   70–130 °C gives Δγ ≈ 20 kHz (invisible); 150–170 °C gives 0.07–0.25 MHz (measurable).
   Same-session (cross-session is what turned the archival β into a bound) and
   interleaved (de-confounds T from time-drift). Also unlocks the collisional
   self-*shift* (the drift killed it in 2025).
4. **The fixed lock itself** (the epoch premise) — resurrects the *pull* (∝S₀), the
   strong AC-Stark handle that was dead in the archive.

**Tier 2 — handle strength ($S_0\propto(1+\rho)P/w_0^2$), served by two waists:**
5. **Small waist (16 µm) = the Stark/skew/form config** — ~14× more S₀ than 60 µm, so
   the skew (∝S₀³) and the g₁ geometry sign-flip become measurable and, at the cliff
   (S₀ ≫ linewidth), the **triangular ramp lineshape is directly visible** (the cleanest
   test of the closed-form law). **60 µm = the clean-κ / width / β_self workhorse.**
6. **Power** — see the ceiling question below. If liftable, higher power is a *cleaner*
   second intensity lever than lens swaps (continuous, easy to calibrate, no realignment).

**Tier 3 — sampling & precision (refine what is already measurable; do not enable):**
7. **More power points:** a ~6–8-point log grid spanning into the cliff + a *linearity*
   check (is S₀ really ∝ P?) beats many crowded points. Fast diminishing returns.
8. **More T points:** *reaching* 150–170 °C ≫ point count; the real limit is *knowing* N
   (the cold-spot + ±5% Steck density floor). Spend effort on the density axis, not T count.
9. **Multiple days:** value is (i) *earning the systematic error bar* — a day-reproducible
   shift is a quantifiable systematic, one that is not is a limitation you must quote —
   and (ii) the 32 µm **epoch-bridge** repeat to 2025. Budget 1–2 days; the fixed lock
   already killed the archive's *dominant* error (σ_laser drift), so this is not drift
   rescue. Never trade the high-T lever or the knife-edge for averaging days.

**Honest impact ceiling (aim the effort right):** the **AC-Stark coefficient Δα is the
robust flagship** (MHz-scale S₀, strong pull under a fixed lock) — point the
small-waist / high-intensity effort here. **β_self(6S) is intrinsically ~kHz** → a
modest first measurement or a much tighter bound even at 170 °C; frame it as completing
the nS/nD self-rate series, do not over-invest expecting headline precision.

**⚠️ Power-ceiling question — ANALYSED 2026-07-13 (likely LIFTABLE; verify the EOM).**
This §8 v2 froze a **225 mW ceiling** + telescope-as-sole-intensity-knob, but the drive
is a SolsTiS + 18 W Verdi V18 (watt-capable) and §0 says "P up to ~1 W" — so 225 mW is
almost certainly an *assumption*, not a physics cap. Mechanism check (see the 2026-07-13
analysis):
- **Photoionization of 6S: EXCLUDED.** 993 nm (1.25 eV) is below the 6S ionization
  threshold (1.68 eV → 738 nm); 6S+one photon reaches a bound Rydberg level, not the
  continuum; and even if allowed the rate would be ~800× below the 6S decay. Not it.
- **Two-photon saturation: real but waist-dependent, NOT the 225 mW number.** S₀~Ω₂ph;
  at 50–60 µm, S₀(225 mW)=0.4–0.6 MHz ≪ Γ=3.49 MHz → *unsaturated with ~1–2 W headroom*
  (and the archival C3 amplitude∝P² up to 225 mW proves it empirically). At 16 µm,
  225 mW already gives S₀≈5.7 MHz > Γ → *already saturated* there, so power is not the
  knob at 16 µm (the waist is). Caveat: the 4121 slope 1.83 hints at onset — **measure
  the P² bend to find the empirical ceiling; don't assume 1 W is clean at 60 µm.**
- **Detector/PMT: plausible current limiter, trivially liftable** — P² → 225 mW→1 W is
  ×20 fluorescence; attenuate / drop gain / ND filter (worse at high T via trapping).
- **The real hardware suspect (not on the original list): the EOM** (resonant-tank
  ruler) optical-power/damage rating — the one in-beam part with a plausible ~sub-watt
  limit. **CHECK ITS DATASHEET** (also isolator, retro coatings, any fibre).

**Actionable:** lift 225 mW *if the EOM allows*; at the **60 µm workhorse** push toward
~1 W (a ~4× longer, cleaner AC-Stark lever than the archive) while watching the P² bend;
at **16 µm** keep power modest (you are saturated) and let the small waist set intensity.
Changes §8.2/§8.3. Optics-set constraints: `docs/FUTURE_TRANSITIONS_titsapph.md`.

### 8.1 Configurations

Two working waists + one continuity spot-check (third full waist DROPPED by
design, not triage):

- **L (large, target w₀ ≈ 60 µm, z_R ≈ 11 mm)** — the width workhorse.
  Transit ~0.5 MHz and collection sits inside z_R (clean geometry). Runs the
  full two-day T grid.
- **S (small, target w₀ ≈ 15–16 µm, z_R ≈ 0.8 mm)** — the Stark/skew/cusp
  config. S₀ several-fold vs 2025; transit ~3.7 MHz bare (the intensity anchor, §8.2).
- **M (archival, w₀ ≈ 50 µm)** — half-day spot check only: knife-edge +
  P grid + one 130 °C point, for direct 2025-epoch continuity.

Telescope sized so the beam enters the EOM at ≤1 mm waist (3 mm aperture
≥ 3w → clipping negligible at the source). Per config: knife-edge at ≥5 z
positions through the focus (w(z) hyperbola gives w₀ AND z_R; consistency
z_R = πw₀²/λ cross-checks the stage scale — a knife-scale error k and stage
error s must satisfy s = k² to hide), retro ratio ρ measured IN SITU at the
cell position (both directions; return-path clipping differs per waist), collection geometry photographed and measured for the MC, and
**polarization logged (or fixed with a clean polarizer) at the cell**: the
paraxial two-photon rate goes as the squared degree of linear polarization and
is exactly zero for circular light (Rajasree 2020, PRR **2**, 033341 — measured
on this line), so polarization drift is a specific candidate for the archival
30–50% between-block amplitude wander, and one QWP turn to circular per config
is a free extinction null test (any residual peak = polarization impurity or
background).

### 8.2 The intensity axis (the collapse test is blind to common scale)

The shift-vs-(P/w₀²) collapse across configs catches only RELATIVE waist
errors; a common knife-edge scale error passes it silently. Orthogonal
absolute anchor: **differential transit width**. width(S) − width(L) at the
same session ≈ transit(S) − transit(L) ≈ 1.7 MHz — σ_laser, collisions, and
natural width cancel in the difference (brackets verify the laser held);
transit ∝ v̄/w₀ from thermal physics, no knife-edge involved. Measured to
±5–7% → intensity axis absolute to ~15%, independent of the stage. The
knife-edge, the w(z) self-consistency, and the transit difference must agree
before any Stark coefficient in physical units is quoted. Note the split:
the ramp-law FORM tests (§8.3) never need absolute intensity — only the
coefficient Δα does.

### 8.3 Stark ramp program (no promised σ; geometry breaks the clean triangle at S)

The pure triangular ramp f(s) ∝ |s| predicts a PARAMETER-FREE moment
hierarchy on the ramp component: mean pull = −(2/3)S₀ (linear in P),
variance/mean² = 1/8, standardized skewness = 18^{3/2}/135 ≈ 0.566. The
one-photon uniform ramp (n=1, Stalnaker's case) predicts skew = 0 — the
skewness exists at all only because signal ∝ I². Test the hierarchy in
order of statistical cost:
1. **Mean pull vs P** (centers alive under the fixed lock): first-order in
   S₀, the workhorse form test, config M/L where the transverse derivation
   is clean.
2. **Excess variance vs P²** (the Cheng-style symmetric reading, config L/M).
3. **Skew hunt at S**: S₀³ ×64 vs 2025. NOT a promised headline: the ⟨E²⟩
   amplitude convention still spans a factor 2 in S₀ = factor 8 in skew
   (predicted significance ~0.8–50σ; the fringe-averaging physics is settled
   — LITERATURE.md — the residual is algebra convention, to be fixed in the
   written derivation + Etienne check). **Session sized for the pessimistic
   end**: ≥ 15× the 2025-equivalent trace count at one condition (~110 °C,
   225 mW) so even 0.8σ-per-2025-block becomes ≥3σ. Decisive either way.
4. **Geometry correction at S** (computing it
   upgraded the test, 2026-07-12). The z-average of transverse ramps has the
   closed form f(s) ∝ |s|^(n−1)·[ζₘ + ζₘ³/3], ζₘ = min(Z_c/z_R, √(S₀/|s|−1))
   (lineshape.stark_ramp_axial; table from scripts/run_ramp_geometry.py).
   At the planned configs (Z_c = 2 mm placeholder, OPEN): L stays clean
   (mean/S₀ −0.66, g1 +0.56); the 2025 archival M geometry is already
   10–40% modified (g1 +0.40 — the −⅔S₀ / +S₀³/135 numbers are the Z→0
   limit and now carry this caveat); and at S **the skewness flips sign**
   (g1 ≈ −0.35; crossover near Z_c/z_R ≈ 1.2): the long window piles weight
   at weak out-of-focus shifts with a tail toward −S₀. The a fixed-lock session skew
   program is therefore a **sign-flip test between configs** — g1 > 0 at L,
   g1 < 0 at S, crossover set by the measured collection profile — which no
   instrumental asymmetry (blind to z_R) can mimic. The absolute third
   cumulant at S is ~47× the 2025 triangle value in magnitude AND opposite
   in sign; the naive ×64 scaling used before this correction was wrong in
   sign.

**The principled hybrid (analysis design, reviewed 2026-07-12).** The four
items above are ONE fit, not four. Per condition, fit the ramp⊗core profile
with a single ramp amplitude S₀; the pull, excess-variance and third-cumulant
are then three analytic functionals of that S₀ at the measured geometry
(`lineshape.ramp_moment_contributions`), each compared to the data's measured
moment with its own error, and a χ² tests their **mutual consistency against
the one S₀**. Pre-register (before fitting) which moment is PRIMARY at which
(P, w₀): the lowest-order moment above its own floor — the pull where S₀ is
small (linear, robust, needs the fixed lock), the skew only at small waist
where P³ has climbed clear of noise. Report the primary as the measurement,
the others as consistency checks; do NOT choose post hoc which moment
"worked." This is the argument that defeats the §8.3-#4 geometry worry: at
small waist a bare skew detection is suspect (diverging-beam collection breaks
the clean triangle), but if the robust pull measured at the *same* condition
implies an S₀ consistent with the skew's S₀, the fragile skew is corroborated
by a more-robust lower-order moment — "pull, variance and skew jointly
consistent with one triangular ramp S₀(P)," which survives a referee.
**Explicitly REJECTED:** hybridizing the *extraction method* for one moment
(fit-parameter vs windowed numerical moment, then combine or pick the higher-
significance one) — those are correlated estimators of one quantity from the
same photons, the numerical one is strictly worse (window-dependent), and
"pick the best" is the multiple-comparisons trap that manufactures false
detections this close to the floor. One estimator per observable (the fitted
one); the hybrid is across the moment hierarchy, never across methods.

### 8.4 Width/collision program (with literature calibration)

- **T grid at L only**, twice, different days, OPPOSITE directions (day A
  70→…, day B …→70). Kills drift components monotonic in time; brackets
  (RF-off before/after each set + EOM ruler per block) catch jumps, with a
  **pre-registered per-block veto**: bracket tooth moves > 0.2 MHz within a
  block → block excluded (jump-like drift does not average out — review
  #4 accepted: opposite-order + brackets + veto + interleave jointly earn a
  measurement, no single element does).
- **High-T extension 150 → 170 °C** (oven/cell permitting): the Zameroski
  calibration (LITERATURE.md) puts expected β_self(6S) ~1 kHz per
  10¹² cm⁻³, so 70–130 °C yields Δγ ≈ 20 kHz — unmeasurable; 150–170 °C
  yields 0.07–0.25 MHz — measurable.
- **High-density points must be SAME-SESSION — mandatory, not preferable
  (M4d lever test, 2026-07-12: measured, not anticipated).** The archival
  γ_coll rises only ×1.85 across the ×52 density span 70→130 °C (a residual
  floor, not resolved collisions), and the joint β collapses 0.036 → 0.014
  when the ×53 cross-session 130 °C anchor is folded in (DATA.md lever-test
  entry; fig6). Cross-session anchors are diagnostics only: the 150–170 °C
  points go inside the SAME locked, bracketed session as the rest of the
  T grid, or they cannot be combined and the collisional slope stays a bound.
- σ_laser at L: transit removed by geometry,
  and the collision term is bounded EXTERNALLY at ~tens of kHz by the
  literature scale — three orders below the 2025 σ_laser bound. Quote
  σ_laser with that prior stated explicitly (ENVELOPE, not our data), or as
  a bound; never as an assumption-free measurement.
- **Four peaks interleaved within every block** (minutes apart, per-trace
  power logging): cross-peak systematics 30–50% → 2–4%; enables the
  degeneracy-law and trapping discriminators (M7/M10). Amplitude-ratio
  blocks get **12–16 repeats** (they are gain-scatter-limited);
  width blocks 8. Randomized P order (free — no thermalization).
- Timestamps logged (scope clock + notebook) — the 2025 σ_laser-sharing
  assumption was unverifiable without them.

### 8.5 Indicative sizing (the programme closes in ~8 days of cell time)

*Not a schedule and not a booking: an ordering that shows the full programme fits
in roughly eight days at the cell, and which shots depend on which. Run it in this
order and a session truncated at any point still leaves the higher-priority bounds
(§8.0) converted. Day labels are relative, not calendar dates.*

- **D1**: telescope install; config L: knife-edge w(z), ρ in situ.
- **D2**: T grid day A at L, ascending, 4 peaks interleaved (incl. 150/170 °C
  if oven allows).
- **D3**: T grid day B at L, descending.
- **D4**: P grid at L (randomized, ~8 powers), am. Reconfigure → S:
  knife-edge, ρ, pm.
- **D5**: skew deep-integration session at S (sized per §8.3); P grid at S.
  Overnight: cool for cusp.
- **D6**: cold-dim cusp session at S (low T, low P — Lehmann vs Voigt);
  the same data anchor the differential-transit intensity calibration.
- **D7**: config M spot check (knife-edge, P grid, 130 °C point); wavemeter
  GHz-linearity shots (§7).
- **D8**: contingency — re-run whatever the bracket veto killed.
Dropped by design: full third waist; T grids at S and M; any shot whose
loss silently degrades a headline (the compression path no longer sacrifices
the novel results first).

### 8.6 Deliverables map

L T-grid → β_self measurement (or honest bound) + σ_laser(2026); S skew
session → S₀ magnitude + skew detection attempt; L/M mean-pull + variance →
ramp-law form test (the actual novelty claim); S−L width difference → absolute
intensity axis → Δα in physical units; interleaved blocks → degeneracy-law +
trapping test; M spot → 2025↔2026 epoch bridge; cusp session → M8 closure.

## 9. Beyond 993 nm — the tunable-Ti:Sapph frontier (forward-looking)

The drive laser is a **tunable Ti:Sapphire**, so future sessions are not locked to
5S→6S (993 nm). The reachable Rb two-photon lines — **5S→5D (778 nm)**, **5S→7S
(760 nm)**, plus 6S at the red edge — and the papers they enable are worked out in
**`docs/FUTURE_TRANSITIONS_titsapph.md`**. Headline: the 778 nm 5S→5D clock
transition is the field's hot AC-Stark battleground (all *active* suppression), and
our passive drift-immune asymmetry method + the Ti:Sapph tunability could give a
**reference-free magic-wavelength determination** (asymmetry sign-flip across
Hamilton 2023's 776 nm magic λ) — the single most compelling next experiment. It
needs 420 nm detection and the near-resonant-intermediate lineshape correction
(the 6S-clean → 5D-resonant ladder, a methods companion). 2024–2026 landscape refs:
`LITERATURE.md` §8.
