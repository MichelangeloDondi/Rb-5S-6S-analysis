# From-scratch analysis plan — Rb 5S₁/₂→6S₁/₂ two-photon, 2025 archival campaign

*Analysis plan of record for the 2025 archive, v1.1 (2026-07-11); §§7–9 are a
specification for possible future sessions. Supersedes the initial-brief pipeline (§6) where they conflict. Old code in the previous repository is never read or reused; old outputs serve only as external cross-check targets.*

## 0. What the analysis is for (Paper 1 claims)

From the 2025 archival data:
- **C1** First determination — or bound — of collisional self-broadening β_self of the 5S→6S line vs Rb density (T-sweep).
- **C2** Quantitative characterization of the 2025-epoch laser (within-scan kernel + drift diary). Supporting deliverable; also the starting linewidth baseline for any ONF work on this line.
- **C3** Power sweep tested against the ramp law: the law PREDICTS FWHM inflation ≤2% and asymmetry ≈10⁻⁴ across 25–225 mW; the archive OBSERVES a 3–8% non-monotonic width spread (block scatter, no significant power slope) and an asymmetry below its ~10⁻³ noise floor. A null, a consistency check and a bound — not three confirmations.

Reserved for a fixed-lock session (specified in §8; not scheduled): AC-Stark coefficient (P up to ~1 W, ramp-cliff regime), collisional self-shift, direct high-power lineshape test, Lehmann-cusp attempt. The pipeline below must ingest such data unchanged.

**What this produces**: the archive alone yields the method + bounds (a self-contained core result); a fixed-lock session would upgrade the bounds to measured coefficients; an ONF campaign would extend the method to the nanofibre line (`PAPER2_SKELETON.md`); a 5D/7S session would extend it up the ladder (`FUTURE_TRANSITIONS_titsapph.md`). None of these sessions is scheduled or agreed.

## 1. Ground rules

- **Axis**: transition (sum) frequency everywhere; laser axis = ×½, stated once in the paper.
- **Provenance tags** on every number: ESTABLISHED / MEASURED-HERE / CALCULATED / ENVELOPE / OPEN / DESCOPED.
- **Closure testing before real data**: every module passes synthetic-data closure tests (known truth injected, recovered within quoted errors) before touching a real trace. End-to-end: a full synthetic campaign (drift + sweep nonlinearity + noise model included) must return the injected β_self and laser widths inside error bars.
- **Quarantine**: `4154nm_130c_{025,125,225}mw*` (aborted first attempt) and the non-underscore `4154nm_eom_before/after` brackets are excluded from all headline fits.
- **Discarded shots**: traces the experimenter rejected at curation time ("seemed quite bad") never enter headline fits — the selection predates the analysis, so honoring it cannot bias results. Four survive in the old `raw/` dump and are published under `data_raw/discarded/`; the recovered backup preserves sixteen more (not in the repo; see the results report, addendum 3). M0's objective QC runs on the published four only as an appendix consistency check on the curation.
- **Engineering**: separate clean repository; physics constants in `rb5s6s/constants.py`, tunables in `rb5s6s/config.py`, nothing numeric hard-coded elsewhere; verbose bus-test documentation (a new operator must be able to take over); pytest battery + CI on every push; functions/modules per pipeline stage.

## 2. Data manifest

See `docs/DATA.md` for the full decoded-archive story and `data_raw/MANIFEST.csv`
for the per-trace table (role, condition, chronology, flags, MD5, original paths).

Chronology (single ~24 h run, 17–18 July 2025, Ti:Sapph on throughout — experimenter-confirmed 2026-07-22): P-session at 130 °C (per peak: before-block → 225→175→125→75→25 → after-block — DESCENDING; corrected 2026-07-23 from the recovered timestamps, the recollection had it reversed), then stepwise cooling 110 → 90 → 70. Repeat indices chronological (a few possible swaps). Repeats within a block are back-to-back (measured position scatter 1.8 ms ≈ 0.08 MHz laser). No acquisition clock was available to the archival analysis; block order is its only time coordinate. (A backup carrying file timestamps surfaced 2026-07-22, after every result here was fixed, and was opened 2026-07-23 under the pre-registered audit — verdict: **integrity void at gate T1** (24 of 297 manifest rows absent or byte-different), so the predictions were not scored; the clock itself passed T2/T3 — docs/PREREGISTRATION_RESULTS.md. Nothing below uses it.) Scope horizontal-knob and cavity-reference recenters occurred between saves — MANY times, the lock drifting enough to push the transitions out of the scan window repeatedly — ⇒ absolute positions carry no meaning across saves. Within a 5-repeat block the reference was USUALLY not moved (a tendency, not a protocol — experimenter-confirmed 2026-07-22), and the archive shows both populations: 24 of 32 RF-off science blocks scatter (median 1.79 ms) while 8 step mid-block, two of them by ~1 s. In the scatter-like blocks the variation shows no trend with repeat index (p = 0.33), so it is laser JITTER, not accumulated drift — `scripts/run_intrablock_trend.py`.

**Assumption A1 (to confirm, one word)**: scope triggered on the sweep sync, so file time = ramp phase. A ramp-monitor channel existed on the scope — a 2025-06-10 photograph shows the triangular sweep on one channel and the fluorescence on another, peaks mirrored about the apex — but it was **not saved** with the archival traces (experimenter 2026-07-23), so A1 stays an assumption for the archive. Recording it in a future session would retire A1 and make the retrace region a measured per-trace quantity; it is worth one spare channel and no more, since the EOM comb already carries the frequency axis ([APPARATUS.md](APPARATUS.md) §4.2). Evidence: frozen repeat positions; window (1.000 s) ≈ one up-ramp (~43 MHz laser at measured rate, consistent with an earlier "~45 MHz" estimate). If false, Module M2 degrades gracefully to per-trace calibration.

## 3. Modules (each gates the next)

**M0 — Ingest & QC.** Parse (2-line header, 2000 pts, 0.5 ms), per-trace QC (baseline level/slope, wing noise, clipping, peak-in-window), manifest with block IDs + chronological order. Output: tidy per-trace table. *(Import + manifest implemented in `scripts/import_data.py`; QC metrics to follow.)*

**M1 — Noise model.** *(runs before the axis fits so every fit inherits correct weights)* Detrended within-trace residual variance vs signal level, per condition (RF-off traces first — single smooth line, easy detrend); noise(V) curve + residual autocorrelation scale → weighted least squares and error inflation for every fit in this pipeline; check growth of Fano-like factor with T (radiation-trapping proxy). Old residuals already show signal-correlated noise (±1% wings → ±5% peak). One noise↔fit refinement iteration allowed; its convergence verified on synthetics.

**M2 — Frequency axis (ruler).** EOM traces are used *only* as frequency ruler and drift/stationarity monitors; their heights/widths never enter physics fits except as cross-checks. Staged per-trace protocol — no threshold peak-picking at any stage (design decision, 2026-07-11):
1. *Robust init*: autocorrelation of the baseline-subtracted trace → tooth period Δ (uses all teeth at once; indifferent to a weak/suppressed carrier); cross-correlation against a synthetic comb template → comb phase t₀; grid-search fallback on (Δ, t₀).
2. *Constrained comb fit (workhorse)*: ONE simultaneous model — centers t₀ + nΔ (+ optional quadratic axis term), n = −2..+2, one shared lineshape, free per-tooth heights, linear background, weights from M1. Simultaneous fitting is mandatory: teeth ~147 ms apart at ~60 ms width overlap at the wing level (a strong tooth's Lorentzian wing under a weak neighbor ≈ 20% of the weak peak → O(ms) center pull if teeth are fit singly or read as maxima).
3. *Shape ladder*: shared shape Lorentzian → Voigt → exponential-wing (transit-like); selection by BIC; spread across shape choices booked as a model systematic.
4. *Free-center diagnostic*: refit with per-tooth free centers (shape still shared); center-vs-n residuals measure local sweep nonlinearity and validate stage 2's axis term.
5. *Tooth count*: extend to n = ±3/±4 (7- or 9-tooth model) when BIC favors it — wider lever arm for Δ and curvature (one n=−4 candidate already sighted).
6. *Combination & errors*: per-trace Δ → block-level inverse-variance mean with scatter inflation when block χ²_red > 1; before-vs-after consistency per peak (discrepancy → interpolate across the block sequence and book the difference as systematic); ensemble stitch of the ν(t) nonlinearity map (requires A1; else per-trace linear axes). Outlier policy pre-registered: QC-based, never result-based. Coverage of all quoted errors verified on synthetic rulers (known Δ, curvature, noise(V), suppressed carrier, missing teeth).

Per-trace rate = 6.25 MHz / Δ (laser axis; CALCULATED from Ω/2 selection rules, locked by the observed 5-tooth amplitude pattern). Deliverables: axis function per block, stat + syst; target ≤1% axis systematic. Quick-look seeds — finder-level, possibly carrying ms-scale overlap bias, to be superseded by this module: spacing ≈ 146 ± 1 ms (warm blocks), rate ≈ 0.0428 MHz/ms laser, block spread 0.6% RMS (MEASURED-HERE, preliminary).

*Verified refinements (independent audit, 2026-07-11):* cross-correlation alignment of ruler repeats must restrict the lag search to < half a tooth period — naive global alignment locked 3/5 cold-ruler traces one tooth off. Pooled cold-block traces calibrate tooth SPACING only (real ±13 ms inter-trace drift smears pooled centers; SNR gain ≈1.6×, not √N); per-trace fits of the 2–3 brightest teeth converge even at SNR 2–3 and are the preferred cold-block estimator (cold spacing ≈145 ms, consistent with the campaign rate). `4192nm_eom_070c3` is a partial ruler (1 valid tooth, tail lost to export dropout; RF label verified) — unusable for spacing. **The sweep turnaround can sit INSIDE the window**: in the 4207 nm 25 mW block the triangle folds at t ≈ 432 ms and the retrace re-crosses the line near the window edge ⇒ the ν(t) map must be fold-aware, and folded blocks provide a free up/down-ramp consistency check.

**M3 — Lineshape model & decomposition.** Physics-anchored convolution, transition axis: Lorentzian Γ_nat = 3.494 MHz (fixed; ESTABLISHED) ⊛ Lehmann transit kernel (exponential-wing shape fixed; one global width parameter with enforced √T scaling; prior from w₀ ≈ 50 µm, tens-of-% — a Nieddu-lineage estimate, OPEN until a direct beam-profile measurement) ⊛ laser kernel per block (Gaussian core + optional Lorentzian tail) ⊛ AC-Stark ramp (fixed prediction per power; f(s) ∝ |s| on [−S₀,0]) + linear background. Joint fit per condition: shared shape across the 5 repeats, per-trace amplitude/center/background. Closure test must demonstrate σ_laser ↔ γ_coll separability at SNR 130 and quantify leakage (this is the fit-level face of the confound). *Verified additions (2026-07-11):* mask sweep-retrace crossings (second above-half region — real signal, confirmed in the 4207 nm 25 mW block) rather than excluding traces; allow a low-order (quadratic) baseline where a block shows a shared slow bow (verified ~0.5 mV across the entire 4207 nm 70 °C block, keepers and discard alike).

**M4 — β_self & the confound program.** γ_coll = β_self·N(T), N(T) from a stated vapor-pressure correlation (carry its systematic; add cell cold-spot caveat). **Temperature is monotonic with time across the whole campaign (130 first … 70 last): ordering de-confounds nothing.** Stationarity probes instead: (i) P-session widths vs block order at fixed 130 °C — hours-scale drift monitor, since power's true width effect is ≤2% (CALCULATED); (ii) before/after bracket tooth *widths* per peak — fixed-condition drift over each peak's session; (iii) cross-peak γ consistency at fixed T (four lines, one density); (iv) σ_laser(block) time series from M3. **Pre-registered rule: quote a measurement iff the probes bound the drift contribution ≤ ~⅓ of the observed γ(T) trend; otherwise a bound.** Bonus replicate: ruler tooth widths vs T form a hidden second T-sweep (cross-check only).

*M4 addendum — hierarchical `fit_global` design (2026-07-11).*
The cross-TEMPERATURE pooling already exists (`fit_beta_self`: one β_self and
one σ_laser shared across a peak's T-sweep). The reviewer's proposed extension
— pooling all 4 peaks × 5 repeats — is accepted with one amendment **our own
M4 result forces**: σ_laser must NOT be shared across time-separated blocks in
the 2025 epoch. The model-independent probe showed between-block σ_laser drift
(~0.06–0.16 MHz) is the dominant systematic; sharing one σ_laser is exactly
why the global fit reported 4–10σ where the correct answer is a bound. Sharing
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
4. **Does the 2025 archive hold a per-peak wavemeter reading?** (asked 2026-07-11). If the wide identification scans logged the HighFinesse value at each of the four peaks, those four readings vs the known hyperfine intervals give a free GHz-baseline linearity check of the 2025 wavemeter (§7.2). Check the archive, or ask the group. If absent, this cross-check waits for a fixed-lock session — no loss, since archival centers are dead anyway.

## 6. Verification

Synthetic closure per module; end-to-end synthetic campaign (full trace count, injected β_self, laser kernels, nonlinear axis, noise model, drift + recenters) recovered within quoted errors; only then real data. Real-data acceptance checks: rate consistency across the ~22 ruler blocks; cross-peak γ agreement at fixed T; M6 nulls.

## 7. Wavemeter calibration (shot list)

**Direction of calibration:** the accuracy hierarchy
is atoms (5S→6S hyperfine centers, ~kHz — Ayachitula 2024) ≫ EOM comb
(6.25 MHz laser-axis teeth, RF-exact intervals) ≫ HighFinesse wavemeter
(~10 MHz). The wavemeter is the LEAST accurate reference, so our data
calibrate the instrument, never the reverse. Absolute wavemeter calibration
is a near-free **byproduct**, NOT on the critical path — Paper 1's fixed-lock-session
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
run it. It is written as a specification, executable
in whole or — following the priority order in §8.0 — as far down the list as the
available time allows. Each item names the archival bound it converts into a
measurement, so a *partial* session is still worth running and its value is
predictable in advance.

**What already stands without any new data, and the smallest tranche that adds
to it.** The analysis of record is complete and under continuous test (public
repository, full pytest battery + CI); §0's pipeline ingests fixed-lock data
*unchanged*, so a session carries no analysis risk and requires no
re-derivation — only shots. What the **archive alone** already supports is
**P1-min**: the drift-immune moment/bounds framework, the self-calibrating EOM
ruler, the identifiability and coverage analyses, and the computed 5S–6S
dynamic polarizabilities and magic wavelengths (`THEORY_NOTE.md` §5).
That is a self-contained result — the core deliverable and a methods
paper — and it depends on **no** further data being taken. A fixed-lock
session is therefore an *upgrade*, not a prerequisite: it converts the named
bounds into measured coefficients (**P1-full**). The **smallest tranche that
converts even one bound into a measurement** is the config-L width program — a
geometry-setup block plus the *two opposite-order* T-grid days (§8.5 D1–D3) —
which by itself yields β_self (or a much-tightened bound) and the fixed-lock
σ_laser; a single same-direction day does **not**, because §8.4's
bound→measurement guarantee needs the opposite-order pair (no single element
is sufficient alone). Value is monotone in shots: a session truncated at any point still
leaves the higher-priority conversions done (§8.0), and if none is ever run,
P1-min stands unchanged. The archive-only analysis (P1-min) is already complete and does not depend on
this specification; a session only decides whether the coefficients are
*measured* or remain *bounded*.

### Objections and responses

*The objections a skeptical PI or co-author would raise, in their words. Each is
answered by conceding what is true first — the campaign is not worth running if
these do not survive. Supporting detail lives where cited.*

**"Orson (USAFA, 2021) already published nulls on this exact line. Your bounds
just say 'we also saw nothing,' slower."** Conceded: **as pure numbers the
archival bounds are confirmatory of Orson's nulls** — same direction, tighter.
The increment is by channel. (a) *Method*: a closed-form fringe-averaged
two-photon triangular-ramp lineshape law plus a reference-free, drift-immune
moment readout — not pursued elsewhere, and distinct from Orson's absolute-frequency and
mean-shift work (the axis-by-axis delineation vs Stalnaker is in `LITERATURE.md`
§1; the not-claimable list in §5). (b) *An order-of-magnitude tighter S₀ bound*
(< 0.63 MHz vs Orson's ~6 MHz null) extracted **from shape alone under a
drifting, hand-re-centred lock**. (c) *With a fixed-lock session*, the **first measured
light shift on this line** — the pull ∝ S₀ is a positive observable, not a
sharper null — plus the collisional self-*shift*, two positive observables Orson
only nulled. In summary: **P1-min's acceptance rides on the method being
judged novel; the measured coefficients need the session.**

**"The lock's line walked MHz-scale all night and destroyed the centres — that
IS why you have bounds. What stops a new session repeating 2025?"** Conceded: "the lock is fixed"
is *asserted* for any future session — but the 2025 root cause is no longer
unknown: the recovered backup clock diagnosed it (cavity-lock dropouts during
the ~2 h etalon thermal transient, held-lock drift only ~0.016 MHz/min —
`APPARATUS.md` §6, results report addenda 4–7), and the §8.7 etalon-discipline
item is the procedural fix. What remains asserted is only that the discipline
will be followed. And the session's value
does not hinge on a *perfect* lock. (a) The pull is a **differential**
measurement (shift vs power) needing minutes of stability, not hours. (b) The
pre-registered bracket veto (§8.4) **excludes** any block whose ruler tooth moved
> 0.2 MHz — drift-jump blocks are cut, not averaged. (c) The sentinel condition
(§8.7.6) turns residual drift into a directly-monitored observable. (d) Existence
proof: Ayachitula (2024), doing precision metrology on **this same transition**,
reports a lock stable to < 0.5 kHz over 50 min — a stable lock here is
demonstrated-achievable, not hoped-for. (e) Fail-safe: even if the lock drifts
again, the D1 beam-profile w₀ + ρ **retroactively sharpen the 2025 archive and
stand alone** (worth doing with only the beam). The worst case is therefore *a
sharpened archive plus a diagnosed lock*.

**"MHz/min drift does not politely stay out of the shape — it skews the line
within a scan, and skew is your observable."** Right in principle; answered by
the timescale separation. A scan window is ~1 s (one up-ramp), and even the
envelope's MHz/min is ~0.017 MHz/s, so within-scan drift is **~0.01 MHz** at
worst — the measured constant rate is ~60× lower again — negligible against the
~5.25 MHz width, and each block is self-calibrated by its own EOM ruler. The
drift manifests **between** blocks (0.06–0.16 MHz scatter), which is exactly why
β_self is currently reported as a bound (`RESULTS.md` C1). The clean closure — inject a
within-scan drift ramp into synthetic data and confirm the recovered moments are
unbiased — is the one check that would seal this; it is flagged as the
next test, not claimed as done.

**"Your Δα bracket ~1200 a.u. is 'consistent with' Orson's computed 1093 — a
bracket that wide discriminates nothing."** Conceded fully: the archival S₀ bound
**excludes only S₀(225 mW) > 0.63 MHz** (Δα above ~1200), the tight-waist top of
the prediction band; every value from **zero** up to 1093 remains allowed, so it
discriminates nothing among reasonable theories (`RESULTS.md` C3d states this).
"Consistent with 1093" confirms the pipeline's scale, not a physics result —
the measured coefficient still needs the session.

**"Your own recompute flips the sign of Δα against the one published computation.
Bug, or should I not trust your pipeline?"** Not a bug. The recompute (M16) is an
independent sum-over-states calculation validated on anchors it does **not** fit
— it reproduces the *measured* 5S tune-out (790.032 nm, see `THEORY_NOTE.md` §5
for the source) to ~2 pm and the static polarizabilities — so its magnitude (within 5% of Orson) and its magic-wavelength
outputs are trustworthy. It agrees with Orson's magnitude and disagrees on the
*sign* of α₆ₛ(993) through an identified mechanism. Crucially **every 2025 result
is sign-immune** (the asymmetry null is symmetric; the S₀ bound and prediction
band use |Δα|), so the disagreement touches no archival number; the sign is a
flagged open **theory** item — one line for a theorist — not a pipeline fault and
not a blocker for the session (`THEORY_NOTE.md` §5).

**"You went dark for a year; the analysis lives in a pipeline only you
understand; put a student on this and it strands them with un-analysed shots."**
Conceded plainly: fair — and the spec deliberately names no operator, no dates,
no handover, because those are a *project* commitment, not a document artifact,
and belong in the direct conversation, not here. What the document *can* put
against the stall risk: the pipeline is built to a **bus-test standard** (a new
operator can take it over — that was a design requirement, §1), it **ingests
session data unchanged** (no re-derivation — §0), and the smallest tranche
(§8.5 D1–D3) has a **defined standalone deliverable**, so a partial or truncated
session yields a finished result, not orphaned data. The analysis is complete; a
session would add data collection, not new modelling.

**"The numbers keep moving — β went from ~0.07 to ~0.4 this month. How do I know
they are frozen?"** They moved because the **error treatment was made more
conservative** — Student-t on one residual degree of freedom replacing a naive
√n, and the beam-waist re-pin — so the bounds loosened, the
opposite of tuning a number down. Every headline is auto-generated from the
committed CSVs (prose cannot drift from data), the clean repository is tagged,
and a submission tag freezes the science snapshot. Every revision moved in
that same conservative direction — toward a looser bound, never a tighter one.

Constraint set: no more power (225 mW ceiling); telescope before the EOM and
lens swaps ARE allowed; repeats across days and orders are allowed. Core
architecture: **the telescope is an intensity
knob** — I ∝ P/w₀² buys the intensity sweep the power budget denies — and
**the opposite-order T grid** breaks the drift-density degeneracy that limited
2025. Three fixes are built in below: an orthogonal absolute
intensity calibration (§8.2), the skew hunt demoted from promised headline to
a sized detection attempt inside a moment hierarchy (§8.3), and a closing
time budget with two waists, not three (§8.5).

### 8.0 Impact priorities (ranked) — what to protect if the budget shrinks

The session's job is **bounds → measurements**. Rank effort by *which bound becomes a
measurement, and how absolute* — not by data volume. If a day is lost, cut from the
bottom of this list, never the top. (This section ranks *observables*; §8.7 ranks
the *sampling currencies* — repeats vs blocks vs days vs orders — against the
measured 2025 failure modes.)

**Tier 0 — the systematic floor (protect first; the single biggest impact, and not a "more data" knob):**
1. **Knife-edge + camera beam-profile w₀, per config (§8.1b).** $S_0\propto 1/w_0^2$ and β_self rides on transit($w_0$),
   so w₀ sets the systematic on *every* absolute number (a 10% w₀ error → **20% on Δα**)
   *and* collapses the transit↔σ_laser degeneracy (the only reason σ_laser is a bound).
   This is the difference between "w₀-conditional bracket" and "absolute measurement."
2. **Retro-ratio ρ in situ, per config — and it drifts with temperature.**
   $S_0\propto(1+\rho)$, so ρ scales the coefficient directly; without it the
   absolute Δα carries a ~2× ambiguity. ρ is **not** constant across a T-sweep.
   The retro leg is exit-window → lens → mirror → lens → exit-window, so
   $\rho = T_\text{win}^2 T_\text{lens}^2 R_\text{mirror}$ (only the *exit*
   window enters, and it enters *twice*; the entrance window attenuates forward
   and retro equally and cancels). The exit window accumulates a Rb film that
   thickens as the cell cools — windows sit below the reservoir at low T — so a
   film transmission falling ~0.99→0.90 per pass takes ρ from ~0.90 at 130 °C to
   ~0.75 at 70 °C: $(1+\rho)$ goes 1.90→1.75, an **~8% drift in $S_0$ across the
   sweep from optics alone**. Uncorrected, that reads as a temperature-dependent
   light shift — the exact confound the self-shift program must not inherit.

   *How to measure it (decompose stable from drifting):* **(a)** the retro optics
   $T_\text{lens}^2R_\text{mirror}$ **once, before the campaign** — power into vs
   back out of the lens–mirror–lens cat's-eye — since they do not drift; **(b)**
   the window transmission **at every condition, before *and* after the cell (not
   only after)** — the live before/after ratio gives $T_\text{win}$ at that
   (T, dwell), where a value taken once, or only downstream, is already stale by
   the next condition; before-and-after also separates entrance- from exit-window
   filming if they differ. Then $\rho(T)=T_\text{win}(T)^2 [T_\text{lens}^2 R_\text{mirror}]$.
   *With no symmetry assumption:* a pick-off before the cell reading
   **both** the outgoing and the returning beam gives ρ directly. Cheap, essential.

**Tier 1 — enablers (the measurement does not exist without them):**
3. **150–170 °C, SAME session, INTERLEAVED T order.** The β_self / self-shift lever:
   70–130 °C gives Δγ ≈ 20 kHz (invisible); 150–170 °C gives 0.07–0.25 MHz (measurable).
   Same-session (cross-session is what turned the archival β into a bound) and
   interleaved (de-confounds T from time-drift). Also unlocks the collisional
   self-*shift* (the drift made it unmeasurable in 2025).
4. **The fixed lock itself** (the epoch premise) — resurrects the *pull* (∝S₀), the
   strong AC-Stark handle that was dead in the archive.

**Tier 2 — handle strength ($S_0\propto(1+\rho)P/w_0^2$), served by two waists:**
5. **Small waist (16 µm) = the Stark/skew/form config** — ~14× more S₀ than 60 µm, so
   the skew (∝S₀³) and, if the collection geometry allows (#4), the g₁ sign-flip
   become measurable and, at the cliff
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
   would remove the archive's *dominant* error (σ_laser drift), so this is not drift
   rescue. Never trade the high-T lever or the beam-profile measurement for averaging days.

**Impact ceiling (aim the effort right):** the **AC-Stark coefficient Δα is the
strongest observable** (MHz-scale S₀, strong pull under a fixed lock) — point the
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
- **M (archival, w₀ ≈ 50 µm)** — half-day spot check only: knife-edge + camera +
  P grid + one 130 °C point, for direct 2025-epoch continuity.

Telescope sized so the beam enters the EOM at ≤1 mm waist (3 mm aperture
≥ 3w → clipping negligible at the source). Per config: knife-edge at ≥5 z
positions through the focus (w(z) hyperbola gives w₀ AND z_R; consistency
z_R = πw₀²/λ cross-checks the stage scale — a knife-scale error k and stage
error s must satisfy s = k² to hide), a **camera beam-profile z-scan**
through the same focus for shape / ellipticity / astigmatism / beam-quality M²
(§8.1b below), **lens separations calipered at both setup
and teardown** (§8.1a below), retro ratio ρ measured IN SITU at the
cell position (both directions; return-path clipping differs per waist), collection geometry measured, not only photographed — the lens–beam distance u, the lens–detector distance v, the detector's effective aperture AND its rotational orientation: the PMT of record is the side-on Hamamatsu R636-10 ([Nieddu 2019](lit/nieddu2019.md); datasheet TPMS1016E) whose cathode is a 3 × 12 mm rectangle, so the axial field of view Z_c = L∥/(2M) (L∥ = cathode extent lying along the beam image, M = v/u) changes ×4 with tube rotation. These numbers feed both the transit MC and the ramp-geometry moments (§8.3 #4) — and
**polarization logged (or fixed with a clean polarizer) at the cell**: the
paraxial two-photon rate goes as the squared degree of linear polarization and
is exactly zero for circular light (Rajasree 2020, PRR **2**, 033341 — measured
on this line), so polarization drift is a specific candidate for the archival
30–50% between-block amplitude wander, and one QWP turn to circular per config
is a free extinction null test (any residual peak = polarization impurity or
background) — expanded, with the plate placement that makes it work, in §8.1.1.

#### 8.1a Lens separations as a geometry consistency check (caliper, setup + teardown)

**Prescription.** At every configuration setup *and* teardown, caliper (or read
off marked rail positions) the two lens separations that bracket the cell — the
focusing lens to the cell, and the retro lens to the folding mirror — and log
them beside the knife-edge. The design geometry is fixed and known: the group's
993 nm lineage focuses with a plano-convex lens of f = 150 mm and retro-images
with the mirror placed at 2f from the focus, so the beam self-images back onto
its own waist (ρ ≈ 1 by construction; Nieddu 2019, verified from the published
setup). The measured separations must reproduce that layout.

**What it does and does not buy.** A tape/caliper is good to only ~1–2 mm
absolutely, so it does **not** pin w₀ — the knife-edge does. Two things still
make it worth the thirty seconds:
- **Coarse waist-position closure, and it bites hardest exactly where it
  matters.** On-axis intensity falls as I(z) = I₀/(1+(z/z_R)²). At config S
  (z_R ≈ 0.8 mm) a 1 mm placement error drops the intensity to
  1/(1+(1/0.8)²) ≈ 0.4 — a **>2× intensity error** the knife-edge would
  otherwise have to catch unaided, and directly a shift in S₀ ∝ I; at config L
  (z_R ≈ 11 mm) the same millimetre is <1%. So it is a strong constraint at S
  and a loose sanity check at L — cheap insurance against a gross mispositioning
  between the knife-edge scan and the science blocks.
- **Differential creep detector (the real value).** Caliper *repeatability* on
  fixed fiducial marks is <0.1 mm — far better than its absolute accuracy — so a
  setup-vs-teardown change flags mechanical drift of the focus or the retro
  overlap *during* the run. That is the mechanism behind a within-config S₀ or ρ
  walk that a single knife-edge, taken once at setup, cannot see. The retro
  lens-to-mirror separation specifically gates the self-imaging condition that
  sets ρ and the standing-wave overlap, so its teardown reproducibility is a
  direct, independent check on ρ stability (§8.0 #2) — complementary to the
  in-situ ρ pick-off, and free.

Book any setup↔teardown separation change alongside the ρ before/after ratio as
a per-config mechanical-stability line; a config whose lenses moved is a config
whose w₀ and ρ are suspect for its science blocks.

#### 8.1b Beam-profile metrology: knife-edge and camera, and why both

**Prescription.** Profile w₀ with *two* instruments at every config: the
knife-edge (§8.1 — power-integrated error-function scan at ≥5 z through the
focus, in two orientations 0°/90° so ellipticity is not aliased into the waist)
*and* a camera beam profiler (CCD/CMOS, ND-attenuated below saturation)
z-scanned through the same focus. Run the camera first — it finds the focus, the
beam-quality M², and the ellipticity/astigmatism in seconds — then place the
knife-edge cuts through the focus it located. Cross-calibrate the camera
pixel→µm scale against the knife-edge stage at config L (both reliable there),
and thereafter trust the camera's *shape* at config S, where only it resolves
two dimensions.

**Why w₀ specifically earns two methods.** It is the dominant systematic of the
whole analysis — every absolute number rides on it (RESULTS, README §2.5). S₀ ∝
1/w₀² and transit ∝ v̄/w₀, so a fractional waist error *doubles* into the Stark
coefficient; the open 45–70 µm band is the entire width of both the AC-Stark
prediction (0.30–0.72 MHz, C3d) and the σ_laser bound (0.4–1.1 MHz). The one
thing you must not do to your dominant systematic is measure it once, with a
single instrument that has a single failure mode. The knife-edge and the camera
fail *differently*: run both and they either agree (you believe w₀) or disagree
(you caught the error before it silently biased every downstream number).

**What each buys, and its blind spot.**
- **Knife-edge — absolute size, blind to shape.** Power integration gives the
  1/e² radius in true optical-power units, with the dynamic range and small-spot
  reach (config S, ~16 µm) a pixel array cannot match — the number that anchors
  S₀ and the transit width. But it integrates power along a cut: a non-Gaussian
  profile (clip wings, a second lobe, a fringe) fits an error function acceptably
  and returns a "waist" that is not the second-moment waist that actually sets
  f(s). Two orientations catch ellipticity; no handful of 1D cuts catches the
  full 2D field.
- **Camera — shape, blind at small size.** One frame gives ellipticity and its
  axis, astigmatism (a per-axis focus split the knife-edge sees only as a
  z-dependent width), M², non-Gaussian structure, and — unique to this
  standing-wave setup — the forward/retro overlap and pointing that back ρ ≈ 1
  (§8.0 #2) and the fringe-tail correction (THEORY_NOTE §5). But its pixel pitch
  under-samples config S (16 µm on a ~4 µm pixel is a few pixels), and
  saturation/blooming and camera-response nonlinearity corrupt exactly the wings
  a power-size needs. The camera is weakest precisely where the knife-edge is
  strongest, and the reverse.

**What the pair buys that neither does alone.**
- **It validates the Gaussian the analysis integrates over.** The moment method,
  the M9 transit MC, and the Stark ramp f(s) all assume one intensity
  distribution (Gaussian, ρ ≈ 1 standing wave), and f(s) is a *functional of that
  profile* — an elliptical, astigmatic, or clipped beam changes the ramp shape
  and its moments, the exact object the drift-immune method reads. The camera is
  the only instrument that checks that profile directly; the knife-edge then
  sizes it once the shape is trusted. This directly checks the model's central
  assumption.
- **A third independent length scale.** §8.1 already crosses the knife stage
  against z_R = πw₀²/λ (a stage error s and knife-scale error k must satisfy
  s = k² to hide). The camera pixel scale (a calibrated target) is a third,
  mechanically unrelated ruler; a scale error in any one must now be mimicked by
  *two* others to pass unseen.

**What it does not buy.** The camera does not replace the knife-edge for absolute
small-waist size (it under-samples S), and the knife-edge does not validate the
2D shape (it integrates it away). Neither alone suffices for a dominant
systematic; the point of both is that each covers the other's single failure
mode. Book the camera M²/ellipticity beside the two-orientation knife w(z) per
config: a beam round and Gaussian on the camera *and* self-consistent between the
knife stage and z_R is a w₀ you can put under every absolute number — and a
disagreement is the warning you want before, not after, the science blocks.

#### 8.1.1 Polarization management, and the plate before the retro mirror

**Why polarization is a first-order knob here, not a detail.** For these
S₁/₂ → S₁/₂ lines the two-photon operator carries only a scalar (rank-0) and a
vector (rank-1) part; the strong ΔF = 0 main lines are driven by the **scalar**
term, whose amplitude ∝ ε_f·ε_b (the dot product of the forward and retro photon
polarizations). Rajasree 2020 measured on this exact line that the rate scales as
the squared degree of *linear* polarization and is exactly zero for circular.
So the retro polarization relative to the forward is not cosmetic: it multiplies
the Doppler-free signal by ε_f·ε_b, and any birefringence in the retro path
walks that number.

**The configuration table (Nieddu 2019 mapped all of these on this cell; verified
from the paper).** With the forward beam linear:

| Config | Plates | Doppler-free peak | Background | Peak height | Note |
|---|---|---|---|---|---|
| **π–π** | none (forward ∥ retro linear) | **yes** | Doppler-broadened pedestal (same-beam pairs) | **1.0** (ref) | the 2025 archival config; B-field-impervious |
| π–π′ | one QWP after cell @45° → retro ⊥ forward | **no** | two Doppler pedestals (2×) | — | ε_f·ε_b = 0 kills the cross term |
| σ | QWP before cell, retro blocked | — | — | **0** | forbidden: 2 photons from one beam carry 2ℏ |
| σ–σ | QWP before cell, retro on | **no** | — | **0** | forbidden: counter-prop same-handed, 2ℏ |
| **σ–σ′** | QWP before cell **and** QWP before mirror | **yes** | **background-less** | **0.5** | opposite-circular; the *vector* channel |

The two verified facts that decide the question: Nieddu reports σ–σ′ gives a
"background-less, Doppler-free spectrum," at half the π–π peak height, and that
for the plate before the mirror "the orientation of the waveplate's axis is
irrelevant."

**So, is it worth a plate between the post-cell lens and the retro mirror?**
Two-part answer, and the parts point opposite ways:

1. **A plate there *alone* is counterproductive — it deletes the signal.** A
   single QWP before the mirror double-passes to a net half-wave rotation, so
   the retro returns *orthogonal* to the forward: that is the π–π′ column, and
   the Doppler-free peak vanishes (ε_f·ε_b = 0). One plate before the mirror
   does not improve the standard configuration; it removes the signal. The useful
   circular configuration needs QWPs before **both** the cell and the mirror —
   Nieddu's two-slot design — not one plate before the mirror.

2. **The σ–σ′ configuration (both plates) is genuinely valuable — as a
   *removable diagnostic*, never the default — because its two properties map
   one-to-one onto two of our open systematics:**
   - **Background-less ⇒ a pedestal-subtraction cross-check.** σ–σ′ removes the
     broad Doppler-broadened pedestal that sits under the narrow line in π–π.
     Refitting center/width/moments with the pedestal present (π–π) vs absent
     (σ–σ′) at the same condition is a direct test that the
     pedestal is not biasing the line shape our M3 baseline models.
   - **No intensity standing wave ⇒ an on/off switch for the fringe
     systematic.** Forward σ⁺ and retro σ⁻ make a σ⁺–σ⁻ field whose *intensity
     is spatially uniform* (a rotating-linear corkscrew, not an intensity
     grating), so the standing-wave intensity fringes are **off**; π–π (parallel
     linear) has them fully **on**. Because the AC-Stark shift follows the local
     |E|², the fringe imprint that `fringe_tail`/THEORY_NOTE §5 price (the
     fringe-resolved skew suppression, the fringe-affected transit) is present
     in π–π and absent in σ–σ′. Comparing the two at matched power **measures**
     that fringe contribution instead of only modelling it — it should vanish in
     σ–σ′ and reappear in π–π by the predicted amount. This is the cheapest
     possible experimental test of the whole standing-wave/fringe analysis.

   Three caveats keep σ–σ′ off the precision path:
   - **Half the signal** (SNR cost).
   - **It is the vector channel** (opposite spins), so the effective coupling,
     the AC-Stark ramp coefficient, and the transit weighting differ from the
     scalar π channel: the π-vs-σ–σ′ comparison tests *fringes × coupling
     change*, and the coupling change (computable from the polarizability
     tensor) must be divided out before the residual is attributed to fringes.
     It is not a pure single-knob switch.
   - **Circular light carries a vector, m_F-dependent AC-Stark shift and is
     B-field sensitive** — it splits/broadens rather than cleanly shifts, which
     is unacceptable for the scalar Δα measurement. The Stark/Δα program (config S)
     therefore stays on **linear (π)**; σ–σ′ is a config-L diagnostic at matched,
     modest power.

3. **A subtler reason a plate can matter even for the linear default:
   retardance robustness.** In π–π, any birefringence in the exit window + retro
   lens + mirror (all double-passed) elliptizes the retro away from parallel,
   pulling ε_f·ε_b below 1 — which both lowers the Doppler-free amplitude *and
   lets it drift* as those optics warm and the exit window films: a concrete
   candidate for the 30–50% between-block amplitude wander (§8.7 item 10).
   Nieddu's "orientation-irrelevant" result says σ–σ′ is insensitive to the
   mirror-plate axis and hence far more tolerant of small retro-path retardance,
   so σ–σ′ may *stabilize* the amplitude that π lets wander — a hypothesis to
   test, not a claimed cure (residual retardance still perturbs circular purity).

**Prescriptions for the session.**
- **Default π (parallel linear), polarization DEFINED by a polarizer/PBS at the
  cell, not merely logged**, with a per-config extinction null: the σ or σ–σ
  *forbidden* setting must give zero signal — any residual is polarization
  impurity or stray background, and it calibrates ε_f·ε_b.
- **Characterize the retro-path retardance** by polarization tomography — rotate
  a QWP and reconstruct the Stokes vector of the *returning* beam (Nieddu's
  thesis method, §5) — to quantify the window+lens+mirror birefringence the
  amplitude-wander rides on, and to decide whether a fixed compensating plate is
  needed to restore ε_f·ε_b → 1 for the linear science.
- **Fit QWP slots before the focusing lens and before the retro mirror on
  removable/flip mounts** (Nieddu's two-slot layout), so σ–σ′ is available on
  demand for the pedestal cross-check, the fringe on/off test, and the
  retardance-robustness test — without disturbing the default linear science
  blocks.

#### 8.1.2 Magnetic field and m_F — a systematic to bound, not an axis to scan

Neither an applied B field nor m_F state preparation earns a place as a science
axis here, and the reason is symmetry, not only the (real) difficulty of holding
a prepared state in a hot, collisional, transit-limited cell.

**The line is m_F-blind by construction.** For 5S₁/₂ → 6S₁/₂ with identical
photons the two-photon operator is purely scalar (rank-2 cannot connect
J=½→½): every m_F has the same per-atom rate and the same scalar light shift —
the very degeneracy that makes the area ∝ (2F+1) law (§8.4a) parameter-free. The
Δα is a scalar shift between two J=½ states, and J=½ carries **zero
tensor polarizability**, so there is no tensor Stark structure for m_F selection
to resolve. m_F preparation therefore sharpens nothing the campaign measures, and
it would actively break the degeneracy-law amplitude test (which needs thermal,
equal-m_F population); optical pumping into one m_F would deplete, not boost, the
scalar-summed signal.

**The main line barely responds to B either.** 5S₁/₂ and 6S₁/₂ are both ns₁/₂
with essentially identical g_J (they differ only by a relativistic/QED correction
~10⁻⁴), and the nuclear term cancels, so the ΔF=0, Δm_F=0 transition shift scales
as Δg_J — **sub-kHz per Gauss**, three-plus orders below the linewidth. A B-scan
resolves nothing on β_self, σ_laser, or the scalar shift (this is Nieddu's
"impervious to stray magnetic fields"). What *does* move with B is (i) the
individual m_F sublevels at ~0.7 MHz/G — which cancels in the Δm_F=0 transition
unless (ii) a **circular-polarization impurity** opens Δm_F=±1 vector satellites
that walk at ~±0.7 MHz/G. So B enters the lineshape only as
(polarization impurity) × B — a wing distortion to suppress, never a handle.

**But a real systematic hides here: the heater is a B source, and its field
tracks temperature.** Heater current scales with heater power scales with T, so a
resistive, non-bifilar winding puts a T-correlated stray field on the atoms along
the very axis of the self-shift measurement; combined with any circular impurity
it produces T-dependent vector satellites — a confound that mimics a
temperature-dependent shift/width, exactly what the self-shift program must not
inherit. The prescription is a **bound, not a scan**:
- **Kill or characterize the heater field:** bifilar (AC) winding cancels it for
  free; else a magnetometer/Hall reading at the cell, or a modest mu-metal shield.
- **One deliberate B-systematic block:** apply a few *known* fields (±a few Gauss
  from a coil) at one condition, measure dν/dB, dΓ/dB and any satellite growth → a
  pre-registered empirical bound on the residual B-sensitivity and the heater
  contribution. It doubles as a polarization-purity gauge (satellites appear only
  if circular impurity × B ≠ 0), tying into §8.1.1.

The one physics a field *would* unlock — the 6S vector polarizability and the
differential g_J(6S−5S) — needs circular light (signal-halving, B-sensitive) and
belongs on a cold, trapped, field-controlled platform, not the hot cell
(`PAPER2_SKELETON.md`, the trapped-platform extensions).

### 8.2 The intensity axis (the collapse test is blind to common scale)

The shift-vs-(P/w₀²) collapse across configs catches only RELATIVE waist
errors; a common knife-edge scale error passes it silently. Orthogonal
absolute anchor: **differential transit width**. width(S) − width(L) at the
same session ≈ transit(S) − transit(L) ≈ 1.7 MHz — σ_laser, collisions, and
natural width cancel in the difference (brackets verify the laser held);
transit ∝ v̄/w₀ from thermal physics, no knife-edge involved. Measured to
±5–7% → intensity axis absolute to ~15%, independent of the stage. The
knife-edge, the w(z) self-consistency, the lens-separation geometry (§8.1a), and
the transit difference must agree before any Stark coefficient in physical units
is quoted. Note the split:
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
3. **Skew hunt at S**: the third cumulant grows steeply with S₀, but the naive
   ×64 reading is superseded — the axial average changes its magnitude and sign
   (#4 below). NOT a promised result: the ⟨E²⟩
   amplitude convention still spans a factor 2 in S₀ = factor 8 in skew
   (predicted significance ~0.8–50σ; the fringe-averaged **mean** is settled
   — LITERATURE.md — but the fringe-*resolved* tail **suppresses** the
   small-waist skew ~26–28% (THEORY_NOTE §5, `fringe_tail`), same-sign-additive to
   the item-4 divergence correction; the residual ⟨E²⟩ convention factor is
   fixed in the written derivation + an external theory check). **Session sized for the pessimistic
   end**: ≥ 15× the 2025-equivalent trace count at one condition (~110 °C,
   225 mW) so even 0.8σ-per-2025-block becomes ≥3σ — enough for a detection or a meaningful bound either way.
4. **Geometry correction at S** (computing it
   upgraded the test, 2026-07-12). The z-average of transverse ramps has the
   closed form f(s) ∝ |s|^(n−1)·[ζₘ + ζₘ³/3], ζₘ = min(Z_c/z_R, √(S₀/|s|−1))
   (lineshape.stark_ramp_axial; table from scripts/run_ramp_geometry.py).
   At the planned configs, with the Z_c = 2 mm placeholder (OPEN — see next
   paragraph): L stays clean (mean/S₀ −0.66, g1 +0.56); the re-pinned 50 µm
   archival M geometry carries only a few-% correction (g1 +0.558 — an
   earlier "10–40% modified, g1 +0.40" figure belonged to the superseded
   32 µm nominal; the −⅔S₀ / +S₀³/135 numbers are the Z→0 limit); and at S
   **the skewness flips sign** (g1 ≈ −0.35 at the placeholder; crossover at
   Z_c/z_R ≈ 1.12): the long window piles weight at weak out-of-focus
   shifts with a tail toward −S₀.

   **The flip at S is conditional on the collection geometry, which is
   unmeasured — measure it before pre-registering the skew moments.** Z_c
   is not a free parameter: for a lens imaging the beam onto the detector
   it is the axial field of view in object space, Z_c = r_PMT/M with
   M = v/u (u = lens–beam, v = lens–detector, 1/u + 1/v = 1/f), so the
   flip condition at config S reads **r_PMT/M > 1.12 z_R ≈ 0.9 mm**
   (z_R = 0.81 mm at w₀ = 16 µm; for the R636-10's rectangular 3 × 12 mm
   cathode, r_PMT → L∥/2, the half-extent lying along the beam image —
   tube rotation changes it ×4, §8.1 — but the tube was never rotated
   during the 2025 campaign (experimenter-confirmed), so Z_c is ONE fixed
   unknown shared by every archival config, not a per-config nuisance).
   That matters more than the ignorance does: with Z_c fixed and z_R set by
   w₀, the flip between L and S needs only **0.90 mm < Z_c < 12.7 mm — a
   window spanning ×14**, since z_R differs ×14 between the two waists. The
   test does not require knowing Z_c, only that it lands in that window.
   Plausible layouts land on BOTH sides of it: the 2025 single f = 18 mm
   lens worked close-in (large solid angle) and therefore at high M, where
   even the long axis gives Z_c ≲ 0.7 mm — just BELOW the lower edge, no
   flip; a 1:1 relay gives Z_c up to 6 mm — mid-window, strong flip. That
   the archival collection sits just outside is the argument for the
   rebuild below.
   The solid-angle weighting varies <2% across any such window, so the
   top-hat form is fair: the width is the only unknown.

   **Prescription — collect with a two-lens relay, not the bare f18.**
   Keep the f = 18 mm as L1 at its focal distance (it sets the collection
   NA and holds it fixed); add L2 (f₂ ≈ 35–50 mm, 2" to avoid vignetting)
   focusing onto the PMT, with the existing 795 nm bandpass stack in the collimated
   segment (normal incidence — no angle-shifted cutoff). Then M = f₂/f₁
   decouples the field of view from the light collection, and swapping L2
   moves Z_c without touching efficiency — a clean knob. Best practice: an
   adjustable slit at the image plane in front of the cathode sets
   Z_c = (slit half-width)/M as hardware, replaces the cathode's soft
   photometric edge with a sharp one, and *scanning the slit measures the
   collection profile* this section lists as OPEN. With the 12 mm axis (or
   the slit) along the beam and f₂ = 35–50 mm: M ≈ 1.9–2.8, Z_c ≈ 2.1–3.1
   mm → g1 ≈ −0.37 to −0.42 at S, while at L and archival-M the flip is
   unreachable for ANY achievable field of view (needs Z_c > 12.7 / 8.8 mm
   ≫ L∥/2 = 6 mm) — so the sign-flip contrast is guaranteed by hardware,
   not by tuning. (Imaging formulas are approximate at the f18's working
   NA — a plano-convex singlet aberrates — which is one more reason the
   slit + profile scan, not the geometry calculation, is the number of
   record.)

   **Install decision — cathode LANDSCAPE (12 mm axis along the beam).**
   *Confirmed (experimenter, 2026-07-23): the Thorlabs PXT1/M module houses the
   R636-10, so the 3 × 12 mm rectangle stands — and the 2025 archive was taken
   in **landscape** already, so this recommendation continues the existing
   configuration rather than changing it. Consequence for the archive: with
   L∥ = 12 mm and the bare f18 close-in (high M), Z_c ≲ 1 mm, giving
   g1 = +0.565 to +0.566 at the archival waist — even nearer the pure triangle
   (+0.5657) than the ±2 mm placeholder's +0.558, so no archival number moves.
   The tube sits in a commercial housing, so orientation means rotating the
   module; that is how it is already mounted.*
   Orientation is a ×4 lever on Z_c and the one collection choice awkward to
   revisit mid-campaign (rotating the tube re-does the alignment and, worse,
   breaks the single-fixed-Z_c property that makes the cross-config
   comparison clean). Numbers from `run_ramp_geometry.py`:

   | orientation | M | Z_c | g1 @ L (60 µm) | g1 @ S (16 µm) | flip |
   |---|---|---|---|---|---|
   | landscape (12 mm) | 1.9 | 3.16 mm | +0.555 | **−0.421** | yes |
   | landscape (12 mm) | 2.8 | 2.14 mm | +0.563 | **−0.367** | yes |
   | portrait (3 mm) | 1.9 | 0.79 mm | +0.566 | +0.103 | no |
   | portrait (3 mm) | 2.8 | 0.54 mm | +0.566 | +0.367 | no |

   Portrait sits below the 0.90 mm threshold at every plausible M: it does
   not weaken the sign-flip test, it removes it. The intuition that a
   shorter window is *cleaner* (less axial averaging, closer to the pure
   triangle) is correct, but is better bought by closing the slit, which
   keeps the option; rotating the tube spends it.

   The margins are asymmetric, which is the sturdier reason to pick
   landscape: it keeps the flip for any M < 6.6 (2.4× headroom over the
   envelope's top), whereas portrait would need M < 1.66 to reach the
   threshold at all — only 14% below the envelope's *bottom*, i.e. f₂ ≲ 30
   mm, which fights the vignetting margin L2 was sized for. Landscape is
   robust to how the relay actually gets built; portrait is not.

   On signal: landscape views ×4 the length, so a background uniform along
   the beam (stray 993, hot-cell IR) also goes ×4, while signal does not —
   the two-photon rate per unit length is Lorentzian in z, hence
   concentrated within ~z_R. Collected fraction 3.0% → 11.8% at L (×4.0:
   the window is the limiting aperture) but 37% → 77% at S (×2.1: the beam
   is already shorter than the window). So the SNR gain is real at L (≈×2
   if background-limited) and roughly a wash at S (×1.0 background-limited,
   up to ×1.4 if signal-shot-noise-limited) — landscape is chosen for the
   flip and for L's signal, not for S's.

   **Measurement — the slit scan is a skew observable, not just a
   calibration.** With landscape the cathode is never the limiting
   aperture, so the slit sets Z_c, and at the SMALL waist alone:

   | slit → Z_c | g1 @ L | g1 @ S | signal @ S |
   |---|---|---|---|
   | 0.5 mm | +0.566 | **+0.402** | 35% |
   | 1.0 mm | +0.566 | −0.071 | 57% |
   | 2.0 mm | +0.564 | −0.354 | 76% |
   | 3.0 mm | +0.557 | −0.416 | 83% |

   g1 walks from **+0.40 through zero to −0.42 on a slit alone**, at fixed
   atoms, power, lock and waist, losing no signal — a cleaner test than the
   two-waist flip, which unavoidably moves S₀, transit time and sampled
   density together. Predicted zero crossing at Z_c = 1.12 z_R ≈ 0.90 mm.
   The same scan measures the collection profile, so it calibrates its own
   x-axis. Two caveats: the top-hat collection model, and the singlet's
   aberration at working NA — both reasons the scan, not the imaging
   formula, is the number of record. Placed at D5 (§8.5).

   Geometry permitting, the skew program is a **sign-flip test
   between configs** — g1 > 0 at L, g1 < 0 at S — which no instrumental
   asymmetry (blind to z_R) can mimic. Two
   caveats travel with it: the naive ×64 small-waist scaling used before
   this correction was wrong in sign (the placeholder-geometry third
   cumulant at S is large AND negative), and config S is already saturated
   at 225 mW (§8.0), so the effective exponent n < 2 there *strengthens*
   the negative skew while breaking the parameter-free n = 2 magnitudes —
   at S the sign is the robust observable; the magnitudes belong to L/M.

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
"worked." This addresses the §8.3-#4 geometry concern: at
small waist a bare skew detection is suspect (diverging-beam collection breaks
the clean triangle), but if the robust pull measured at the *same* condition
implies an S₀ consistent with the skew's S₀, the fragile skew is corroborated
by a more-robust lower-order moment — "pull, variance and skew jointly
consistent with one triangular ramp S₀(P)."
**Explicitly REJECTED:** hybridizing the *extraction method* for one moment
(fit-parameter vs windowed numerical moment, then combine or pick the higher-
significance one) — those are correlated estimators of one quantity from the
same photons, the numerical one is strictly worse (window-dependent), and
"pick the best" is a multiple-comparisons problem that produces false
detections this close to the floor. One estimator per observable (the fitted
one); the hybrid is across the moment hierarchy, never across methods.

### 8.4 Width/collision program (with literature calibration)

- **T grid at L only**, twice, different days, OPPOSITE directions (day A
  70→…, day B …→70). Cancels drift components monotonic in time; brackets
  (RF-off before/after each set + EOM ruler per block) catch jumps, with a
  **pre-registered per-block veto**: bracket tooth moves > 0.2 MHz within a
  block → block excluded (jump-like drift does not average out — review
  #4 accepted: opposite-order + brackets + veto + interleave jointly earn a
  measurement, no single element does).
- **Buy degrees of freedom first — the cheapest cure for the t(0.95,1)=6.31
  penalty is more T blocks, not statistical cleverness.** The archival bound's
  ×6.31 multiplier exists only because the between-block scatter is estimated
  on ONE residual DOF (3 densities, 2 fit params); **≥5 T blocks per peak**
  gives t(0.95,3)=2.35 — a ~2.7× tightening before any drift compensation is
  even considered.
- **The ruler teeth as a width monitor — a designed compensator, prescribed
  here, NOT applied to the archive.** Each ruler tooth is a copy of the line,
  so its fitted width is a contemporaneous linewidth monitor that could cancel
  between-block σ_laser drift as a control variate. On the 2025 archive this
  fails on two measured/structural grounds. (i) **Hardware mismatch by
  construction:** every 2025 ruler trace was taken with the half-wave plate
  rotated (AM admixture suppressing the optical carrier by 2–3 orders) —
  necessary because at the achievable modulation index the sidebands were
  buried in the central tooth's tails — so the ruler light had a *different
  polarization and power* at the atoms than the science light, and its width
  fluctuations track HWP/power partition as much as σ_laser (the mechanical
  channel behind the anomalous, wrong-sign monitor–line correlation, a ~2σ
  fluctuation with all identified fit/rate artifacts positive and ≤ +0.03).
  (ii) **No resolution:** per-block tooth-width SEM 0.06–0.36 MHz (~5
  repeats) at or above the 0.12 MHz drift signal — block-level reliability
  measured ≈ 0. The HWP-cancelling *(after − before)* bracket-width difference was
  measured too (the shared HWP setting cancels the polarization offset in the
  difference) and is no better: per-difference error 0.05–0.14 MHz ≈ the drift,
  only 1 of 4 peaks resolvable (`docs/DATA.md`), since it inherits √2× the
  width noise — so it serves as a within-session drift *bound* (≤ ~0.17 MHz), not
  a block-by-block correction.

  **The corrected design (fixed-lock session):**
  1. **Drive the EOM at β ≈ 1.20 instead of rotating the HWP.** The pure-PM
     two-photon comb obeys A_k ∝ J_k(2β)² (methods §3): at β ≈ 1.202 the
     central tooth **nulls by coherent pair interference** (comb
     0 : 1.00 : 0.69 : 0.15), so the sidebands stand tall with the ruler
     light **identical in polarization and power to the science light** —
     the HWP trick becomes obsolete, and with it the hardware mismatch.
     If the 12.5 MHz tank cannot reach β ≈ 1.2, a higher-frequency EOM
     helps twice: more index headroom AND tooth spacing ≥ 3–4× the
     laser-axis linewidth un-buries the tooth *widths* from overlap.
  2. **Interleave rulers with science blocks** (not only bracket) at ~10×
     the 2025 repeat count, RF power logged; monitor modulation purity live
     via the exact pure-PM symmetry A₊ₖ = A₋ₖ (the 2025 traces violate it —
     the AM fingerprint — so the asymmetry is a per-block purity gauge).
  3. **λ from a dedicated calibration, never fitted:** dither the lock to
     impose known σ_laser excursions, record both width types, fix the
     control-variate coefficient before science data.
  4. **Decision rules frozen before first data**, with the asymmetry rule: a
     correction may widen a bound but may never, by itself, flip BOUND to
     MEASUREMENT. Until all of this exists the ruler widths serve as the
     per-block QC veto above (a gate, not a variate).
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
- **Per-scan timestamps — recorded in hardware metadata, not just the notebook
  (the fix for 2025 post-mortem #5).** The analysed exports carry *no* acquisition time
  on any trace, so block order was the only clock available to the analysis —
  (a recovered backup later supplied file timestamps; the audit voided at T1,
  and its post-hoc pass showed block order is not even the acquisition order:
  the power ladder ran 225 → 25 mW) — and that is the single reason
  the σ_laser-sharing the hierarchical β rests on is untestable: the four peaks at
  a given T could have co-drifted between acquisitions and still agree (M4c), so
  the sharing check is necessary-not-sufficient (RESULTS.md). A wall-clock time on
  every scan buys four things. (i) It turns σ_laser-sharing into a *tested* fact —
  confirm the four interleaved peaks were acquired close enough in time that the
  accumulated drift across the set (elapsed time × drift rate) is a small fraction
  of the width, so a common σ_laser is forced, not assumed. (ii) It reconstructs
  the drift diary — the only way to separate between-scan drift (free centres
  absorb it) from within-scan drift (the residual skew channel; THEORY_NOTE §3,
  `tests/test_intrascan_drift.py`) — and lets us *measure* the lock drift rate
  properly — the recovered 2025 clock already yields a constant
  +0.016 [+0.007, +0.025] MHz/min (laser, ~2σ) with the settling attributed to
  the operator's re-centring, not the lock (`run_drift_settling.py`,
  state-space stage); a logged clock plus an untouched reference would make
  the drift diary exact rather than model-mediated. (iii) It makes the T↔time collinearity (post-mortem
  #3) checkable, so the opposite-order days can regress drift out of the density
  lever. (iv) It time-orders the interleaved four-peak / per-trace-power blocks
  (§8.4a) the degeneracy-law and trapping discriminators (M7/M10) pair on.
- **Etalon-lock thermal discipline (measured + experimenter-confirmed,
  2026-07-23).** The 2025 disturbance was not the drift (a constant
  ~0.02 MHz/min laser once the lock held) but **cavity-lock dropouts during
  the etalon temperature transient** — about 2 h of lock-on after ≥3 h of
  lock-off, dropping every few tens of minutes inside it, with MHz-scale
  recapture excursions (the blind state-space fit found the same settling
  scale, τ ≈ 86 [70, 104] min, before the recollection — and the model then
  passed an out-of-sample test on the recovered pilot session: predicted
  post-transient steps ≲20 ms, measured +14.0/−5.8/+0.2 ms, addendum 11).
  Protocol
  consequences: (i) engage the etalon lock **≥2 h before first data**, and
  after *any* ≥3 h pause budget the transient again — the 2025 evening dwells
  ran entirely inside a fresh post-break transient and paid 3–6 MHz re-kicks
  per block for it; (ii) once past the transient, **hands off the reference**
  — at the measured held-lock drift a 43 MHz window lasts tens of hours
  (~40 h if the ~0.016 MHz/min rate persists), so the
  all-night re-centring was fighting the transient and itself, not the drift;
  (iii) **log the lock state** (even a TTL on a spare channel): with drops
  time-stamped, the drift diary needs no state-space model at all. Keep
  the timestamp in the trace *metadata*, not only the filename, so a re-save or
  rename cannot strip it.
- **How, on our scope (Agilent/Keysight InfiniiVision DSO-X 3054A).** The
  archival traces were taken on the Agilent, not the LeCroy on the same bench —
  the LeCroy would not trigger reliably (experimenter, 2026-07-23), and the CSV
  export signature confirms it (`x-axis,N` / `second,Volt` is InfiniiVision's
  format, not LeCroy's). The scope timestamps every acquisition in hardware;
  the 2025 loss was the *export* — the minimal CSV we saved is a 2-line
  `second,Volt` header (`config.CSV_HEADER_LINES`) with no time field.
  Preserve it one of two ways. **(a) Save the native `.h5`**, which carries
  per-waveform acquisition metadata the plain CSV drops, so the ingest loader
  gains a per-trace time column for free — the guaranteed route on this scope.
  *Either scope is available for a future session (experimenter, 2026-07-23).*
  **If the LeCroy's trigger problem can be resolved, prefer it for this
  purpose**: its native `.trc` WAVEDESC carries an explicit per-trace
  `TRIGGER_TIME` (calendar date to a fractional second, read back by
  `lecroyparser`/`readTrc`), and a segmented acquisition stores a per-segment
  `TRIGTIME` array — inter-scan elapsed time recorded directly, at higher
  resolution than any file clock. That is a better timestamp story than the
  Agilent's, and it is the one thing the LeCroy would be chosen for.
  **(b)** Take each back-to-back set (the repeats, or the four interleaved
  peaks) as one **segmented** acquisition, so the scope stores a per-segment
  trigger time, recording the *inter-scan* elapsed time directly — exactly the quantity the σ_laser-co-drift
  test needs, and immune to any file-clock rounding. Precondition for both: set
  the scope real-time clock (Utilities setup) at session start, and still note
  each block's start time in the notebook as an independent check, so a mis-set
  scope clock is caught rather than trusted.
- **The LeCroy timestamp story is now demonstrated, not assumed** (addendum 11):
  the 2025-07-04 dress rehearsal ran on the LeCroy, and its files carry a
  readable per-trace `TRIGGER_TIME` — 47 of them were read, and
  mtime(JST) − TrigTime = +4…+9 s, which is what validated the whole
  FAT-mtime clock reconstruction. So the LeCroy would hand you, for free, the
  exact provenance whose *absence* cost this entire audit.
- **But its file weight buys nothing for this signal, measured.** A LeCroy
  trace is ~250× the bytes of an Agilent one — and that is **sample count, not
  precision** (500,001 pts at 100 kSa/s over 5 s vs 2,000 at 2 kSa/s over 1 s;
  per *sample* the Agilent CSV is the heavier of the two). The two-photon line
  is a ~60 ms feature in sweep time, which the Agilent already samples ~120×;
  the LeCroy's ~6,000× is pure redundancy, and binning it to equal resolution
  recovers the same noise. Both are 8-bit — no vertical-resolution edge either
  way. So the LeCroy's real strengths (GHz bandwidth, GS/s, deep memory) are
  wasted on a slow swept-fluorescence signal, at a cost of gigabytes for a
  many-hundred-trace campaign (vs tens of MB) and a more fragile export — three
  of the 50 rehearsal files were silently binary-corrupt under a `.csv` name.
- **Recommendation (acquisition hardware).** The one thing that mattered —
  per-trace time — is obtainable on the lean Agilent by *either* saving its
  native `.h5` (metadata carries the time column) *or* logging wall-clock
  externally (the TTL of §(iii) above). Take the science on the Agilent that
  way. Reach for the LeCroy only if the external time-log proves unreliable in
  practice (then its embedded TrigTime is worth the disk) **or** if a fast
  auxiliary channel — a photodiode transient, the ramp monitor at full
  bandwidth — actually needs the GS/s. Do not choose it for the science traces
  on a quality argument; there isn't one for a 60 ms feature.

### 8.4a Amplitude program — the archive's weakest observable, made into levers

Amplitudes were useless in 2025 for one measured reason: within-block statistics
are excellent (1–3%, photon-limited, falling as amp⁻⁰·⁵), but **between-block gain +
power + polarization drift wanders 30–50%**, so the clean amplitude physics was
explicitly deferred to a fixed-lock session. The fixed lock, the interleaved
four-peak blocks, and the defined polarization (§8.1.1) would remove the common-mode
drift, and every exploit below is designed around a **ratio, a within-block slope, or a
monitored quantity** so the 30–50% wander cancels identically. Nothing here rests
on absolute cross-block amplitude.

**Two new measurements (the headline amplitude results):**
1. **The degeneracy-law test — the deferred clean scalar-operator measurement.**
   The S→S two-photon operator is pure scalar (rank-2 forbidden for J=½→½; rank-1
   nulled by identical π-π polarization), so line *areas* are pure initial
   population: within one isotope the ratios are parameter-free — exactly
   **5/3 (⁸⁷Rb) and 7/5 (⁸⁵Rb)**. On the four *interleaved* lines (common block,
   intensity, gain) the ratio precision drops from the archive's 30–50%
   between-block swing to the 1–3% within-block floor, turning an untestable
   prediction into a genuine test that the operator is pure scalar. *Corrected
   null:* the cross-isotope **total** area ratio (both lines of each isotope
   summed) is the flat abundance ratio **2.59, constant in T** — the (2I+1)(2J+1)
   normalizations cancel the (2F+1) sums, so it is 2.59, not any
   degeneracy-weighted number; its constancy licenses area-as-density and its
   onset of curvature flags PMT nonlinearity.
2. **The four-line common-slope Δα fit, with √area as the per-trace intensity
   proxy.** Δα is electronic and scalar, hyperfine-independent
   to ppm, so all four interleaved lines share **one** Stark slope dS/dI: a
   4×-over-determined Δα, with radiation-trapping / blend-induced center pulls
   isolated as the *line-specific* residual. And since area ∝ I²·(ε_f·ε_b)²,
   **√area tracks the delivered intensity of the same trace** (including waist
   drift: area ∝ 1/w⁴, S ∝ 1/w², so √area ∝ I), so regressing the center shift on
   √area rather than on the coarse power setpoint is an errors-in-variables
   de-biasing that soaks up the block-to-block intensity/alignment wander inflating
   the shift-vs-P slope. Within a block √(area/area_ref) = I/I_ref cancels gain,
   density and polarization exactly — no absolute amplitude enters. Valid only where
   area ∝ I² holds (config L, PMT-linear); config S is saturated, so the proxy is
   disqualified there — a pre-registered admissibility gate.

**Two systematic attacks on the density axis** (need a weak auxiliary D-line
absorption channel — a probe laser + pickoff photodiode):

3. **Absorption-channel N(T) → cold-spot detection.** Transmission on a photodiode
   is a ratio immune to PMT gain (the dominant wander) and power-self-normalized;
   its log-slope vs 1/T returns the vapor-pressure latent heat. A cold spot lagging
   the set temperature flattens the high-T end and depresses the fitted slope, so
   the offset from the Steck prediction **measures the cold-spot lag ΔT_cs** —
   converting the dominant N(T) systematic on β_self from an assumption into an
   in-situ-verified curve. Use the **D-line linear probe, not 993 depletion** (the
   two-photon cross-section is not known to metrology precision — anchoring on it
   would be circular). One long soak-verified fixed point on the same channel gives
   an absolute column-density anchor, replacing the ±5% Steck absolute-N assumption.
4. **Fluorescence-area ÷ absorption → clean radiation-trapping separation.**
   Absorption sees true N (incident-beam depletion, undistorted by trapping of the
   *emitted* photons); fluorescence sees the trapping-distorted emission. Their
   within-block ratio cancels N and leaves the trapping-modified collection
   efficiency η_coll(N) — the deferred clean trapping test, sharpest at the new
   150–170 °C lever. Discriminant: real trapping is *smooth/monotonic* in density;
   drift is random/non-monotonic (the archive's 1.10→0.98→2.53→1.97 swing was drift).
5. **1.3 µm cascade detection — a trapping-free channel, the cleanest arbiter of
   the ratios.** The 6S decays first to 5P (6S→5P₁/₂ 1324 nm, 6S→5P₃/₂ 1367 nm) and
   only then to ground (the detected 780/795 nm D-line photons). The 780/795 channel
   sits on a **ground-resonant** line, so those photons are radiation-trapped in the
   dense vapour — the M7 distortion, density- and isotope-dependent (⁸⁵Rb has ~2.6×
   the D-line absorbers, so the **2.59 cross-isotope ratio is the most
   trapping-vulnerable**). The **6S→5P (1.3 µm) photon is resonant with nothing
   populated** (5P is only transient), so it escapes freely: detecting it is
   **trapping-free**, and the common 6S→5P branching cancels in the ratios. So 1.3 µm
   measures the degeneracy law without the trapping confound, and **running 795 and
   1.3 µm at the same condition turns an off-ratio into a verdict** — a deviation that
   vanishes at 1.3 µm was trapping, one that persists is real (polarization impurity
   opening the vector channel, or a genuine operator effect); the 795/1.3 µm ratio
   itself measures the trapping factor. It is the direct twin of exploit 4 (detect the
   untrapped signal rather than correct the trapped one). **This is an established
   technique, not a new one:** Hassanin et al. (2023, Phys. Rev. A **107**, 043104)
   detect the sibling **5D→5P infrared cascade** in a hot Rb cell precisely because it
   "does not suffer from reabsorption," which is what lets them study collisions at
   high density; Beard et al. (2024, Opt. Express, DOI 10.1364/OE.513974) stabilise a
   5D clock on the 776 nm (5D→6P) cascade. So the 1.3 µm channel is a *proven*
   trapping-free readout — the only new element here is turning it onto the
   degeneracy-law / amplitude-ratio test on the 6S line. **Cost:** 1.3 µm is past
   silicon → an **InGaAs detector** (single-photon sensitivity below a Si/GaAs PMT at
   795; the hot-cell IR background needs filtering); broadband 1.32–1.37 µm catches
   both fine-structure branches.

**Enabling and defensive (cheap, protect the headlines):**
- **Polarization-purity gauge:** the forbidden σ / σ–σ configs must read zero (the
  null residual sets the impurity ε directly) and π-π : σ–σ′ must be 2:1 (§8.1.1) —
  turning polarization drift from an unbounded systematic into a measured,
  subtractable number feeding exploits 1–2.
- **Radiation-trapping sentinel:** a pre-registered density/T threshold above which
  the reabsorbed skirt inflates the fitted width beyond tolerance (e.g. >2%),
  fencing the high-T β_self points — trapping is strongest exactly at the 150–170 °C
  lever the campaign depends on.
- **Area, not peak height,** is the drift/width-robust observable (peak confounds
  with the changing width that *is* the β_self signal); the area-minus-peak-ratio
  gap is a live lineshape-distortion monitor.
- **PMT-nonlinearity certificate:** a back-to-back calibrated-ND linearity check
  spanning the campaign's full fluorescence range (worst at high T) with a
  pre-registered counts ceiling, plus an A/P² within-block watchdog that admits a
  Stark block only if its intensity axis held.

*Hardware note:* exploits 1–2 and the defensive set need only the already-planned
interleaved blocks (12–16 reps) and per-trace power logging; exploits 3–4 add a
weak D-line absorption probe + photodiode — moderate, and the single highest-value
addition because it attacks the N(T) systematic that limits β_self.

### 8.5 Indicative sizing (the programme is sized to ~8 days of cell time)

*Not a schedule and not a booking: an ordering that shows the full programme fits
in roughly eight days at the cell, and which shots depend on which. Run it in this
order and a session truncated at any point still leaves the higher-priority bounds
(§8.0) converted. Day labels are relative, not calendar dates.*

- **D1**: **first, before anything else: test whether the ECD lock works** —
  it was never engaged in 2025 (suspected faulty, untested; APPARATUS §1.1),
  and if it functions, engaging it is the zero-hardware-cost upgrade the whole
  fixed-lock design assumes; if not, that repair becomes the critical path.
  Then telescope install; **collection rebuild — f18 as L1 + relay lens L2
  + image-plane slit, 795 nm bandpass moved into the collimated segment, PMT long
  (12 mm) cathode axis set along the beam — LANDSCAPE, the install decision
  argued in §8.3 #4; then the slit scan that *measures*
  the collection profile and fixes Z_c** (§8.3 #4 — this is the Tier-0 input
  the whole skew program is conditional on, so it precedes the science
  blocks); config L: knife-edge w(z) + camera beam-profile
  z-scan (§8.1b), lens separations calipered (§8.1a), ρ in situ, polarization
  defined at the cell + retro-path retardance tomography and the σ/σ–σ
  extinction null (§8.1.1). While the oven settles: the drift-characterization
  block (§8.7.5) → freeze the RF bracket cadence.
- **D2**: T grid day A at L, ascending, 4 peaks interleaved + mini-P excursion
  per dwell (§8.7.4), sentinel ×3 (§8.7.6) (incl. 150/170 °C if oven allows).
- **D3**: T grid day B at L, descending; sentinel ×3.
- **D4**: P grid at L (randomized, ~8 powers), am. Reconfigure → S:
  knife-edge + camera, ρ, pm.
- **D5**: skew deep-integration session at S (sized per §8.3); **slit scan
  g1(Z_c) at S — 4–5 settings spanning Z_c ≈ 0.5–3 mm, which walks the
  predicted g1 from +0.40 through zero (Z_c ≈ 0.90 mm) to −0.42 with atoms,
  power, lock and waist all held fixed** (§8.3 #4; the same scan measures the
  collection profile, so it doubles as a cross-check of the D1 calibration at
  the config that matters); P grid at S.
  Overnight: cool for cusp.
- **D6**: cold-dim cusp session at S (low T, low P — Lehmann vs Voigt);
  the same data anchor the differential-transit intensity calibration.
- **D7**: config M spot check (knife-edge + camera, P grid, 130 °C point); wavemeter
  GHz-linearity shots (§7).
- **D8**: contingency — re-run whatever the bracket veto excluded.
Dropped by design: full third waist; T grids at S and M; any shot whose
loss silently degrades a headline (the compression path no longer sacrifices
the novel results first).

### 8.6 Deliverables map

L T-grid → β_self measurement (or bound) + σ_laser (fixed-lock epoch);
S skew session → S₀ magnitude + skew detection attempt; L/M mean-pull +
variance → ramp-law form test (the actual novelty claim); S−L width difference
→ absolute intensity axis → Δα in physical units; interleaved blocks →
degeneracy-law + trapping test; M spot → archive ↔ fixed-lock epoch bridge;
cusp session → M8 closure. Amplitude program (§8.4a): interleaved four-line
areas → the parameter-free degeneracy-law test (5/3, 7/5) + the four-line
common-slope Δα (√area intensity proxy); D-line absorption channel → in-situ
N(T) / cold-spot lag + clean radiation-trapping separation + the high-T β_self
trapping sentinel.

### 8.7 Resource allocation — what bit in 2025, and what each hour buys

The prescriptions above each cure one 2025 failure; this section is the ledger
that connects them. It states what actually bit — in measured numbers, with the
module that measured it — and then prices the four ways cell time can be spent
(repetitions, blocks, days/orders, interleaves), so that when the schedule
compresses the cuts follow the priority ranking in §8.0/§8.7.7.

#### 8.7.1 The 2025 post-mortem (measured, not remembered)

| # | What bit | Measured size | Consequence | Cure (where) |
|---|----------|---------------|-------------|--------------|
| 1 | Between-block width scatter from the drifting lock | σ_B ≈ 0.12 MHz vs within-block SEM ≈ 0.05 MHz (`coverage.py`, archive-calibrated) | widths drift-limited, not photon-limited; σ_laser a bound | fixed lock; brackets + veto (§8.4) |
| 2 | Only 3 densities → 1 residual DOF | t(0.95,1) = 6.31 error multiplier | β_self a bound | ≥5 T blocks (§8.4) |
| 3 | T monotonic in time (one sweep direction, ever) | density slope exactly collinear with drift | monotonicity guard had to carry the claim | opposite-order days (§8.4) |
| 4 | Cross-session high-density anchor | joint β collapses 0.036 → 0.014 when folded in (M4d lever test) | high-T lever unusable | 150–170 °C same-session (§8.4) |
| 5 | No acquisition clock available to the analysis | block order the only clock | σ_laser-sharing assumption untestable **as analysed**; the recovered backup was audited 2026-07-23 — integrity void at T1, so this row is unchanged (PREREGISTRATION_RESULTS.md) | log scope clock + notebook (§8.4) |
| 6 | Ruler traces HWP-rotated (AM trick) | monitor reliability ≈ 0; wrong-sign correlation ~2σ | no drift compensator on the archive | β ≈ 1.20 pure-PM null (§8.4; methods §3) |
| 7 | w₀ never measured | tens-of-% prior | every absolute number conditional | beam-profile first (§8.0 #1) |
| 8 | ρ(T) never measured | ~8% S₀ drift across the sweep from window filming alone | optics drift masquerades as physics | T_win before AND after, per condition (§8.0 #2) |
| 9 | P sweep at a single T (130 °C) | trapping-immunity argument untested across density | discriminators data-starved | mini-P excursion in every dwell (§8.7.4) |
| 10 | Between-block amplitude wander | 30–50% (polarization the specific suspect: retro-path retardance walks ε_f·ε_b) | amplitude observables noisy | polarization defined at cell + retardance tomography + σ–σ′ robustness test (§8.1.1); 12–16 reps (§8.4) |

Items 1–3 share one root cause: **2025 spent statistics against a
systematics-limited experiment.** Within-block noise was already 2.4× below the
block-to-block scatter — the campaign kept buying the cheap term.

#### 8.7.2 The variance budget — why repetition stopped paying at n ≈ 5

For any block-mean observable, Var(mean) = σ_w²/n + σ_B²: repetition divides
only the first term. At the archive numbers (σ_w/√5 ≈ 0.05, σ_B ≈ 0.12 MHz)
the block error is 0.13 MHz; **doubling the repeats buys 4% for 100% more
time**, and infinite repeats saturate at 0.12. The same hour spent on one more
T block divides σ_B by √N AND buys a residual DOF — and the t ladder is where
the archive bled: t(0.95, dof) = 6.31, 2.92, 2.35, 2.13, 2.02 for dof = 1…5.
Going 3 → 5 T blocks is a ~2.7× tightening from the quantile alone (§8.4),
before the averaging gain. Diminishing returns set in near dof ≈ 5 (2.02 vs
the asymptotic 1.96) — hence "≥5 blocks" in §8.4, not "as many as possible."

**Stopping rule (freeze it in the run notebook): repeat a condition until
σ_w/√n < σ_B/2, then stop — past that point the statistical term inflates the
block error by ≤ 12%, so even infinite further repeats recover at most that.**
With 2025-like per-trace noise that is n ≈ 4–5 for width blocks, exactly where
§8.4 already caps them.

Where repetition IS the right currency — the observables that are genuinely
photon- or gain-limited, not drift-limited: the skew deep-integration at S
(third moment, 1/√N), amplitude-ratio blocks (gain scatter → 12–16
reps, §8.4), and the tooth-width monitor (needs ~10× the 2025 count to reach
reliability > 0, §8.4). Know which regime an observable is in before spending.

#### 8.7.3 Bias vs. variance — what ordering buys that repetition cannot

Within a single sweep direction, drift monotonic in time is **exactly
collinear** with physics monotonic in T: no number of repetitions separates
them, because collinearity is a rank problem, not a noise problem (this is 2025
item 3, and why the archive needed a guard instead of a measurement). Day A
ascending + day B descending cancels every drift component linear in time in
the (A+B)/2 mean, and the A−B difference *measures* the residual — a
systematic error bar earned, not assumed. Two days in opposite orders
therefore beat four days in the same order. Full T randomization would be
marginally better on paper but each extra T reversal costs thermal settling
(tens of minutes); the single reversal buys most of the protection at zero
extra settling. Randomize freely only the free knobs (P order, peak order —
§8.4 already does).

#### 8.7.4 Loop structure — T outside (it is the expensive axis), everything else inside the dwell

Thermal settling makes T the only slow knob; power, peak selection, and RF are
seconds-scale. So T is the outer loop by necessity, and each dwell must
extract everything cheap while the cell sits there:

- 4 peaks interleaved, minutes apart (§8.4);
- **a mini-P excursion — 2–3 powers, randomized, ~10 min**: this converts the
  2025 single-T power sweep into width-vs-P *at every temperature*, which is
  precisely the data the trapping/degeneracy discriminators (M7/M10) were
  starved of. The full ~8-point P grid keeps its own block (D4) at the
  reference T; the excursions buy the T-resolved slope;
- matched-PM ruler brackets and interleaves (§8.4; cadence from §8.7.5);
- the window-transmission before/after reading (§8.0 #2).

Never the converse (P outer, T inner): re-thermalizing per power point
multiplies dead time by the grid size for nothing.

#### 8.7.5 RF cadence — bracket at a *measured* cadence; do not strictly alternate

Strict on-off-on-off alternation halves science time for monitor information
that saturates within a few brackets. With the β ≈ 1.20 matched-PM design an
RF-on trace is no longer dead time (sweep rate + tooth widths + purity from
the A₊ₖ = A₋ₖ symmetry, all at science polarization and power), but tooth
overlap at Ω/2 = 6.25 MHz spacing still contaminates the *moment* observables
— skew and the drift-immune centered moments come from RF-off traces only. So
the pattern per block is: [on] – a few off traces (peaks interleaved) – [on] –
…, and the open question is only the cadence. **Make it a measurement, not a
guess: spend the first ~30–45 min of D1, while the oven settles, on a
dedicated drift-characterization block** — alternate on/off at one fixed
condition and compute the Allan deviation of tooth width and sweep rate vs
lag; set the bracket spacing where the drift deviation crosses the few-trace
SEM. Freeze the cadence before the first science block — the §8.4
frozen-rules discipline applies to sampling, not only to vetoes.

#### 8.7.6 The sentinel condition — a drift ruler across days (new prescription)

Pick ONE condition (e.g. 90 °C, 125 mW, peak 4192, config L) and re-measure it
at the start, middle, and end of every day, identically. Cost: ~3 short blocks
per day. It delivers three things the 2025 archive structurally lacks: (i) a
within-day drift time series with real DOF at fixed physics — the natural
calibration set for the §8.4 control-variate λ; (ii) the day-to-day
reproducibility number that §8.0 Tier 3 says must be *earned* before averaging
days together; (iii) the common level that ties the D2 and D3 opposite-order
grids to each other. Every 2025 drift statement is an inference through the
lineshape model because no condition was ever revisited; the sentinel makes
drift a direct observable.

#### 8.7.7 The currency table (cut from the bottom, never the top)

| Currency | Attacks | Marginal value at archive numbers | Verdict |
|----------|---------|-----------------------------------|---------|
| Beam-profile (knife-edge + camera) + ρ + high-T same-session (Tier 0/1) | the systematic floor | converts bounds → absolute measurements | never cut |
| Second day, opposite T order | time-monotone bias | removes what NO averaging can; measures the residual | mandatory, costs no settling |
| More T blocks (to ~6) | DOF + σ_B averaging | ~2.7× from the t quantile alone | the best statistical buy |
| Interleaves (peaks, mini-P, rulers) | cross-condition systematics | 30–50% → 2–4% at near-zero dwell cost | always on |
| More repeats, same condition | photon noise only | 4% for 2× time (past the crossover) | only for skew / amplitudes / ruler monitor |
| Strict RF alternation | monitor variance | saturates; halves science time | no — bracket at the §8.7.5 measured cadence |

**Summary: spend structure before statistics — orders before days, blocks
before repeats, interleaves before points, and one measured cadence instead
of a guessed alternation.**

## 9. Beyond 993 nm — the tunable-Ti:Sapph frontier (forward-looking)

The drive laser is a **tunable Ti:Sapphire**, so future sessions are not locked to
5S→6S (993 nm). The reachable Rb two-photon lines — **5S→5D (778 nm)**, **5S→7S
(760 nm)**, plus 6S at the red edge — and the papers they enable are worked out in
**`docs/FUTURE_TRANSITIONS_titsapph.md`**. The 778 nm 5S→5D clock
transition is the most actively worked AC-Stark line (all *active* suppression), and
our passive drift-immune asymmetry method + the Ti:Sapph tunability could give a
**reference-free magic-wavelength determination** (asymmetry sign-flip across
Hamilton 2023's 776 nm magic λ) — the most distinctive next experiment. It
needs 420 nm detection and the near-resonant-intermediate lineshape correction
(the 6S-clean → 5D-resonant ladder, a methods companion). 2024–2026 landscape refs:
`LITERATURE.md` §8.
