# The 2025 archive: provenance, decoding, and quarantine

*Everything in this file was established on 2026-07-10/11 by hash comparison
of the original archive plus direct answers from the experimenter
(Michelangelo). It is the background you need to trust `data_raw/MANIFEST.csv`.*

## 1. The experiment in one paragraph

Doppler-free two-photon spectroscopy of Rb 5S₁/₂→6S₁/₂ at 993.4 nm in a hot
vapor cell (retro-reflected geometry), detecting the 795 nm cascade
fluorescence (6S→5P₁/₂→5S) through 50 dB of 795 nm filtering on a PMT. Four
hyperfine components, labelled by their wavelengths: 4207 (⁸⁷Rb F=2→2), 4192
(⁸⁵Rb F=3→3), 4154 (⁸⁵Rb F=2→2), 4121 (⁸⁷Rb F=1→1). The laser (M Squared
SolsTiS) was scanned slowly across each line; an EOM at exactly 12.5 MHz was
toggled ON for separate "ruler" traces, whose two-photon comb teeth (6.25 MHz
apart on the laser axis) calibrate the sweep. The 2025 lock was misconfigured:
line CENTERS drift between scans and carry no metrological meaning; SHAPES
survive. Scope: LeCroy WaveSurfer 3104z; every trace is 2000 points, 0.5 ms
step, 1.000 s window.

## 2. Campaign design and chronology (experimenter-confirmed)

Per peak, in time order, all at 130 °C: **before-rulers → 25 → 75 → 125 →
175 → 225 mW → after-rulers** (each power = 5 back-to-back RF-off repeats;
each ruler block = ~5 back-to-back RF-on repeats). After the whole power
session: stepwise cooling **110 → 90 → 70 °C** at 225 mW, each temperature
with its own 5-repeat RF-off block and its own ruler block. Repeats were
saved seconds apart (measured position scatter within a block: 1.8 ms ≈
0.08 MHz laser). Between saves the experimenter sometimes moved the scope's
horizontal knob and manually recentered the cavity reference — so **absolute
trace positions carry no meaning across saves**; each trace's comb is its own
frequency axis.

Consequence for the collisional analysis: temperature is monotonic with time
across the whole campaign (130 °C first … 70 °C last), so ordering alone
cannot separate density effects from slow instrument drift — the plan's
stationarity probes (PLAN.md, M4) exist precisely for this.

## 3. What the hash comparison established

The original `data/` tree holds 722 CSVs in six directories with ~2×
duplication (367 unique basenames; fewer unique MD5s). Key identities, all
byte-exact:

1. **`temperature/*_130c{1..5}` ≡ `power*/*_225mw{1..5}`** (all 20 files):
   the temperature sweep's 130 °C point *is* the power sweep's 225 mW point.
   Fresh temperature acquisitions exist only for 70/90/110 °C.
2. **`temperature_EOM/*_eom_130c{1..12}` ≡ pooled `power_eom` brackets**
   (`after{...}` first, then `before{...}`): there are no separate 130 °C
   rulers; the pooled files are renames of the power-session bracket rulers.
   For 4154 the pooled set is the **underscore** re-take
   (`eom_before_`/`eom_after_`), which is therefore the canonical 4154
   bracket set.
3. **Double-saves — including inside the curated dirs.** Same-bytes-two-names
   pairs: `temperature/4154nm_070c1 ≡ 070c2` (so 4154@70 °C has only **4
   unique curated repeats** — the old N=5 filename counting was
   pseudo-replication), `temperature_EOM/4192nm_eom_090c3 ≡ 090c4`,
   `power_eom/4192nm_eom_after3 ≡ after4`, `raw/4154nm_130c_225mw4 ≡ 225mw5`.
   **Rule: always count repeats from manifest rows, never from filenames.**
4. **The curated dirs are a deliberate selection; `raw/` is everything.**
   The experimenter discarded some acquisitions at curation time because they
   "seemed quite bad" (statement, 2026-07-11) and renumbered the keepers —
   that is why `raw/`'s repeat numbering is shifted vs the curated dirs
   (e.g. `temperature/4207nm_090c1 ≡ raw/4207nm_090c6`) and why four
   raw-only traces exist. They live under `data_raw/discarded/` with
   `flag=discarded`; one of them is a 5th distinct shot for 4154@70 °C, so
   that condition runs on **N=4**. **Policy: discarded traces never enter
   headline fits.** The selection was made at curation time, blind to any
   fitted physics, so honoring it cannot bias results; the M0 objective QC
   is additionally run on them as a consistency check on the curation
   (reported in an appendix). Chronology: curated indices are chronological
   among the kept traces; where finer ordering matters, the raw-index
   aliases in `source_paths` are the better guide (small known exceptions,
   e.g. 4207@90 °C).

5. **LeCroy export quirks (found at first strict-parse contact, 2026-07-11).**
   (i) ~180 files contain 1–4 "time-without-voltage" rows at the window
   edges (a benign export artifact; the loader drops and counts them).
   (ii) `rulers_t/4192nm_eom_070c3.csv` is dropout-riddled: ~950 *interior*
   empty rows, only 1047 valid samples — hard-flagged, excluded from ruler
   pooling. (iii) `p_sweep/4192nm_225mw1.csv` is a nonstandard export
   (stray header `jj,nj`; time column printed at 3 significant figures so
   0.5 ms steps alias to duplicate timestamps) whose *content* is healthy —
   the loader rebuilds its time axis from the row index and records the
   salvage. The old pipeline's `genfromtxt`+NaN-drop parsing swallowed all
   of this silently.

## 4. Roles in `data_raw/`

| Folder | Content | Count |
|---|---|---|
| `t_sweep/` | RF-off lines, 70/90/110 °C × 4 peaks × 5 repeats | 59 (4154@70 °C has 4 — §3) |
| `p_sweep/` | RF-off lines, 130 °C, 5 powers × 4 peaks × 5 repeats; 225 mW rows carry `serves_t130=True` | 100 |
| `rulers_t/` | RF-on comb traces per temperature block | 61 |
| `rulers_p/` | RF-on bracket blocks (`before`/`after`) per peak | 44 |
| `quarantine/` | the aborted 4154 power attempt + its plausible rulers (§5) | 29 |
| `discarded/` | shots the experimenter rejected at curation (§3, item 4) | 4 |
| `review/` | anything that failed pattern classification | 0 |

Total: **297 unique traces** (from 722 archive files). The census is pinned by
`tests/test_manifest.py`; CI re-hashes every file on every push.

The `flag` column takes values `canonical` / `discarded` / `quarantined` /
`review`. **Only `canonical` rows may enter headline fits.**

## 5. Quarantine (pre-registered; never in headline fits)

- **`4154nm_130c_{025,125,225}mw*`** (~19 unique traces): an aborted first
  attempt at the power sweep. The experimenter does not remember why it was
  stopped and flags it as suspicious (2026-07-11). Potential future use, with
  care: a same-condition/different-hour reproducibility probe.
- **`4154nm_eom_before{1..5}` / `after{1..5}` (non-underscore)**: 4154 is the
  only peak with two bracket sets; the underscore re-take is the one pooled
  into the canonical rulers, so this set plausibly belongs to the aborted
  attempt. Held out pending clarification.

## 6. Facts that supersede the initial July brief

(Recorded because earlier numbers circulated before this analysis existed.)

**Error-plumbing hardening round (2026-07-16, follows the two entries below).**
Five smaller review items closed, none moving a headline: (i) the
block-coherent ruler-rate error (~0.5–1.8%) is now folded into every
width-type error in `linefit_conditions.csv` (γ_coll, σ_laser, total FWHM,
plus a `rate_relerr` column) — it was carried in `run_beta_self`/
`run_power_sweep` but dropped where the per-condition widths are made; the
remaining bare-rate consumers each carry an explicit justified-omission
comment (BIC: a common scale cancels; areas: dwarfed by the 20–40%
between-block systematic; hierarchical β: ≤0.0006 vs ±0.004 stat). (ii)
`noise_floor_limited` and `*_at_bound` flags now travel in
`linefit_conditions.csv`, `beta_self.csv` and `global_fit.csv`: scipy's
covariance ignores active bounds, so a parameter pinned at its zero rail
wears a symmetric error where the truth is one-sided — the flag makes that
visible per row. (iii) the transit-MC FWHM is now read with sub-grid
interpolation: the old raster read quantized it to the 0.01 MHz step, so the
committed "MC errors" were the grid quantum in disguise (exact multiples of
0.0041); the seed spread now measures genuine sampling noise. (iv) the noise
law's σ(V) floor rose from 0.2·a to a (the dark noise is the physical floor);
verified zero-churn — the one negative-c law turns over at 0.756 V, above its
own 0.525 V maximum level, so the floor never engages in-domain and the
hazard was only ever out-of-domain. (v) tests: a floor test past the
turnover; flags plumbed through the suite.

**The β_self bound gains proper coverage and the density systematic
(2026-07-16).** The headline per-peak bound changed **0.07–0.15 → 0.2–0.4 MHz
per 10¹² cm⁻³**, again with no change to data or fits — two coverage
corrections. (i) The between-block scatter that dominates the slope error is
estimated on **one residual degree of freedom** (3 density points, 2
parameters), so the one-sided 95% multiplier is the Student-t quantile
$t(0.95,1)=6.31$, not the hard-coded 2 — the old "≈2σ" under-covered, which is
exactly what its "~factor-2 own-uncertainty" prose flag was admitting; the
t-quantile turns the flag into the number. (ii) β ∝ 1/N, so the ~20% spread
between published vapor-pressure correlations (`density.py`,
`N_SCALE_FRAC_SYST`) moves every β by the same fraction; the cold-spot
direction makes the fitted β an *under*estimate, so the bound inflates on the
+ side (×1.2). The selection rule also flips: the *loosest* peak is the honest
single-number floor (the min of noisy 1-DOF estimates is the down-fluctuated
one), not the tightest. The cross-session 130 °C lever variant (dof = 2)
barely moves (0.03–0.05) but keeps its cross-session caveat. The hierarchical
global-fit β gains a `beta_nscale_syst` row (±20% of β). A constant cold-spot
offset also *tilts* the N(T) lever by ~2.3%/K of offset (slope, not scale) —
quantified in `density.py`, recorded, not propagated (second-order).

**AC-Stark bound reconstructed as a profile-likelihood limit (2026-07-16).**
The quoted archival bound changed **3.1 → 0.63 MHz** (95%, $S_0$ at 225 mW) with
**no change to the data or the fit** — only to the interval construction. The
best fit rails at $\kappa=0$, where the width handle ($\propto S_0^2$) has zero
gradient; a linearized (Wald) $\kappa+1.645\sigma$ interval evaluated there has
no valid coverage — its $\sigma$ is a finite-difference artifact, and it
happened to be a large one (the old 3.1). The profile-likelihood limit (scan
$\kappa$, re-minimize the per-peak cores, one-sided $\Delta\chi^2=2.706$ scaled
by $\chi^2_\text{red}\approx4.3$ for over-dispersion) crosses at 0.63 MHz —
checked smooth and grid-stable (identical to 0.1 MHz at half the frequency-grid
step). Physical reading: the archive's width data are already sensitive at the
scale of the predicted coefficient (0.59 MHz at the 50 µm prior); anything much
above the prediction is excluded, while the prediction itself and zero remain
allowed. The superseded Wald rows stay in `stark_sweep.csv` as labelled
diagnostics. Downstream, the $\Delta\alpha$ bracket tightens $\sim5800 \to
\sim1200$ a.u. (~1.1× the computed 1093), still $w_0$-conditional.

**Cross-check against the earlier analysis of this dataset (2026-07-16).** Per the
ground rule in `PLAN.md` (old *code* is never read; old *outputs* serve only as
external cross-check targets), the previous attempt's committed report and summary
CSVs — not its source — were reviewed after this analysis was complete. The
comparison is worth recording because it explains the two analyses' different
conclusions:

- **The earlier analysis modelled the line as an ordinary Doppler-broadened
  absorption profile.** Its report contains no mention of *two-photon*,
  *counter-propagating*, *retro-reflected*, *transit-time*, or *AC-Stark*, and it
  interprets the fitted Gaussian width as "a direct measurement of the atomic
  velocity distribution … compared to the Maxwell–Boltzmann distribution".
- **Its own numbers refute that reading.** At 70–130 °C the first-order Doppler
  FWHM on this line would be 430–466 MHz, whereas the Gaussian it fits is
  σ ≈ 0.81–0.88 MHz, i.e. an FWHM of ≈1.9–2.1 MHz — **~220× narrower than Doppler**.
  That factor is not an error in the fit; it is the Doppler-free geometry working
  as designed (§1.1 of `methods.md`): the first-order shift cancels for every atom,
  which is the entire purpose of retro-reflecting the beam. A Gaussian of ~2 MHz on
  this line therefore cannot be the velocity distribution.
- **What that Gaussian was actually absorbing.** With no transit-time kernel in the
  model, the single free Gaussian is the only component able to take up the transit
  width. Suggestively, its mean rises 8.4% from 70→130 °C where the √T transit law
  predicts 8.4% — though with ~0.07 MHz of peak-to-peak scatter and a *fall* from
  70→90 °C, four points do not establish this. Read it as consistent with transit +
  laser being absorbed into one Gaussian, not as a measurement of either.
- **Consequences for us:** the earlier per-condition widths remain usable as
  order-of-magnitude cross-check targets (their total widths are in the same few-MHz
  range as ours), but none of their *physical interpretations* transfer, and their
  reduced χ² of 2–5 is consistent with a missing model component. This is the
  clearest justification for the from-scratch re-derivation: the disagreement is not
  about fitting quality, it is about which mechanisms are in the model at all.

- **Scan rate**: comb teeth are ~147 ms apart ⇒ ≈ 0.043 MHz/ms on the laser
  axis (preliminary, finder-level) — ~11× slower than the brief's
  0.49 MHz/ms seed, which misread noise substructure as teeth. The brief's
  "two triplets 270–280 ms apart" were the two strong ±6.25 MHz sidebands.
- **Absolute widths**: e.g. 4154 at 110 °C/225 mW is ≈ 60.6 ms ≈ 5.2 MHz
  FWHM on the transition axis (finally consistent with the physics budget:
  3.49 natural + ~1.2 transit + collisions + laser). All absolute σ/γ values
  from the old pipeline are void (wrong axis scale; Lorentzian part below the
  natural floor); its *trends* may survive a single global rescale.
- **Power dependence**: the archival "FWHM null vs power" is the *predicted*
  behaviour (ramp-law inflation ≤2% across 25→225 mW); the third-moment/skew
  observable proposed in the brief is unmeasurable (≈1×10⁻⁴ vs noise floor
  ≈1×10⁻³) — power-shift physics moves to the fixed-lock session.
- Traces are 1.000 s / 2000 pts (brief said 840 ms — wrong).
- The sweep turnaround can sit **inside** the acquisition window: in the
  4207 nm 25 mW block the triangle folds at t ≈ 432 ms and the retrace
  re-crosses the line near the window edge (in 3 of 5 keepers and the
  discarded shot; verified independently from raw traces). "One window ≈ one
  up-ramp" holds for most blocks, not all — fits mask the retrace region.
- **Frequency axis (M2 real-data run, 2026-07-11)**: laser-axis sweep rate
  **0.04257 ± 0.00005 MHz/ms** (transition axis 0.08514; mean tooth spacing
  146.8 ms) — ~11× slower than the initial brief's 0.49 MHz/ms seed, which
  misread noise substructure as teeth. Blocks are NOT all consistent with a
  single rate (campaign χ²/block 6.8, 0.6% RMS spread) ⇒ M3 uses **per-block
  rates**, interpolated across bracket sequences for the power session. The
  4207 nm power session shows a coherent 5.5σ before→after spacing shift
  (146.7 → 144.6 ms) — a real ~1.4% in-session rate change, its own
  calibration systematic for 4207 power points. The fine-scan sweep is
  **linear to <0.4% across the window** (no piezo nonlinearity — the
  ruler-in-fine-scan design worked). Cold 70 °C rulers calibrate fine with
  correctly inflated errors (~2.5 ms vs ~0.3 ms warm).
- **β_self (M4, 2026-07-11) — the archival T-sweep BOUNDS it, does not
  measure it.** Model-independent raw line widths (smoothed half-max × the
  verified per-block rate, no fitting) rise only ~0.2–0.4 MHz across 70→110 °C
  and are **non-monotonic in density for 3 of 4 peaks** (e.g. 4207: 5.11→4.87→
  5.28 MHz — narrower at higher density, impossible for collisions). The
  within-block repeat scatter is tiny (~0.05 MHz), so each block is internally
  precise; the blocks simply disagree with a monotonic density trend. The
  culprit is **laser-width (σ_laser) drift between the cooling-session blocks
  (~0.06–0.16 MHz)**, comparable to the whole collisional trend. Result:
  β_self < ~0.04–0.11 MHz per 10¹² cm⁻³ (95%, per peak); a clean measurement
  needs the fixed-lock fixed-lock session — this is the archival data proving
  the two-epoch design was necessary, a Paper-1 result in itself. NOTE: the
  global Voigt fit (rb5s6s/beta.py) reports 4–10σ "detections" but those σ are
  OVERCONFIDENT — they assume one shared σ_laser across blocks and so omit the
  between-block drift the model-independent probe exposes.
- **RF-on rulers are fold-robust (checked 2026-07-11, do not re-litigate).**
  The rulers were taken with the same sweeps as their blocks, so one might
  worry the off-center-sweep fold (below) also corrupts the tooth-spacing
  fits — it does not, for a structural reason. The sweep is a symmetric
  triangle, so the up-ramp and down-ramp have the *same rate magnitude*; a
  fold therefore preserves the tooth *spacing* (6.25 MHz → ~146 ms on either
  ramp) and only scrambles which tooth is which index n, never the spacing
  that sets the rate. Empirically the 4207 ruler combs march at a uniform
  ~146 ms with no compression/reversal, and the 4207 ruler-fit χ² (mean 0.91)
  is no worse than any peak. So the 4207 before/after rate shift is a real
  in-session effect, not a fold artifact, and the ruler rates need no window.
  (Contrast: a single RF-off *line* has no such protection — it simply
  appears twice, which is why only the RF-off fits get a window.)
- **Off-center-sweep mirror crossings (user-flagged, 2026-07-11).** When the
  triangular sweep is not centered on the transition, the down-ramp re-crosses
  the line, leaving a mirror ~40 MHz from the main peak inside the window.
  Whole-dataset scan: 8 canonical RF-off traces, almost all in **4207** (the
  edge peak — the sweep centered on the quartet middle put it off-center):
  4207@25 mW has a **79%-of-peak** mirror in 4/5 traces, 4207@225 mW ~18% in
  3/5, plus one 4121@70 °C at 15%. Fits now use an ADAPTIVE window (±3.5×
  the trace's own FWHM, clipped to [9, 25] MHz — `linefit.adaptive_halfwidth`)
  to exclude the ~40 MHz mirror while keeping a fixed fraction of the
  Lorentzian wings regardless of line width; the raw-width probe was already
  retrace-safe. This was corrupting the 4207 fits specifically (χ² 6.7→1.0 at
  225 mW; γ_coll un-pinned from 0 at 25 mW) and was the sole cause of 4207's
  cross-peak-consistency outlier (χ²/dof 7.4→3.0 after the fix). Headline
  β_self bound unaffected (model-independent raw widths).
- Curation audit outcome (M0 + systematic curation audit, 2026-07-11):
  of the four discarded shots, only `4154nm_070c4` shows an objective
  signature (~27% dimmer than siblings, structurally clean); `4192nm_090c3`
  is fully clean (a supernumerary 6th repeat); the two 4207 discards are
  indistinguishable from their kept siblings (the flagged features — retrace
  crossing, slow baseline bow — are block-wide). All four stay excluded by
  pre-registration. On the keeper side no exclusion-worthy trace was found:
  the flags that survive are fit-time instructions (retrace masking; cold
  rulers → per-trace bright-tooth fits), and RF labels verified 297/297.
- **The lever test — the fitted γ_coll is a FLOOR; β_self is lever-dependent,
  hence a BOUND (M4d, 2026-07-12).** Per-condition fits (linefit_conditions):
  the 4-peak mean γ_coll is 0.41 / 0.41 / 0.46 / 0.61 MHz at 70/90/110/130 °C
  while the density rises ×52 — a ×1.5 rise where a real binary-collision
  width must be LINEAR in N. Consistently, the joint hierarchical β collapses
  0.036 → 0.014 when the ×53 130 °C anchor (`serves_t130`, 225 mW) is folded
  in (lever_crosscheck.csv: beta_lever_probe_130), and the 130 °C widths sit ON
  the near-flat trend — not a session outlier. Split-independent check: the
  pooled total FWHM grows only ~0.38 MHz across the span, below the
  ≥0.55 MHz minimum a linear β=0.036 demands (Voigt slope ≥0.5346) — see
  fig5 panel A and fig6. ⇒ the fitted "collisional" width is a residual floor
  (transit/laser model + block scatter), the apparent β shrinks as the lever
  lengthens, and the archival β is a BOUND — reinforcing, not adding to, the
  model-independent headline. A fixed-lock session: the 150–170 °C points must be taken
  inside ONE locked session (PLAN §8.4). RETRACTED framings (do not
  re-litigate): (i) "between-session systematic — the sessions cannot be
  combined" as the PRIMARY story (commit d711950) — the 130 °C widths lie
  on-trend, so leverage on a near-flat γ, not a session jump, drives the β
  drop (the session difference stays a secondary, unseparable caveat);
  (ii) a corr(γ, log N) > corr(γ, N) argument — fragile (993.4121 nm is
  non-monotonic and the pooled means reverse it); the robust metric is the
  rise factor ×1.5 over ×52 (lever_crosscheck.csv: gamma_rise_factor).
- **Discard/quarantine audit adjudicated + `qc_reason` column added (2026-07-12).**
  An external audit of the excluded traces was verified against the
  repo; its two central factual claims did NOT survive, in opposite directions
  (do not re-litigate either):
  (i) *"the four discards are MD5-superseded duplicate exports, not real
  discards"* — FALSE for 3 of 4: `4154nm_070c4`, `4192nm_090c3`,
  `4207nm_070c2` have no same-name canonical twin (their same-repeat matches
  are EOM *ruler* files — a role collision, not a duplicate), and e.g.
  4154 70 °C has only 4 canonical repeats *because* 070c4 was excluded as a
  shot. Only `4207nm_025mw2` is a genuine duplicate-name save superseded by a
  canonical twin (md5 26bf… vs 7ec1…). The committed curation audit
  (above) stands: four real excluded shots, one objective defect
  (070c4, zsib_height=−3.1), three kept-excluded by pre-registration.
  (ii) *"the 29 quarantined traces fail hard — 'peak cut by window
  (margin 0 ms)', snr=inf — independently confirmed"* — does NOT reproduce:
  recomputing `hard_flags` on all 29 gives ZERO flags (spot: edge_margin
  333 ms, snr=61), agreeing with the committed `qc_metrics.csv`. The
  quarantine is legitimate but SESSION-GRAIN (the aborted first 4154 130 °C
  power attempt, redone in full, plus its 10 EOM ruler brackets) — a curation
  fact, not a per-trace mechanical defect, and therefore NOT recomputable
  from the data. That is exactly why the audit's one *procedural* point was
  right and is now implemented: `MANIFEST.csv` carries a **`qc_reason`
  column** (`scripts/annotate_manifest_qc.py`, idempotent, self-checking: it
  re-verifies the discard map and the quarantine cleanliness before writing;
  guarded by `tests/test_manifest_qc.py`). Canonical rows are empty; all 33
  non-canonical rows carry their recorded reason. Also for the record: the
  manifest has no `status` column and never did (`flag` is the status) — the
  audit's "status reads `?`" was its own parse artifact.
- **Re-examined the 4154 130 °C quarantine on request (2026-07-12) — kept
  excluded, now for a concrete reason.** The question was whether the aborted
  first attempt is usable. Findings, all verified: (a) it is **redundant** — the
  canonical p_sweep already covers all five powers (25/75/125/175/225 mW), the
  aborted retry only 25/125/225 (stopped partway) and carries no `serves_t130`
  flag, so it is not a density-lever anchor; (b) at the **line level it is fine**
  — height, width and SNR match the redo to <2%, which is why it clears the
  mechanical QC; (c) but the **225 mW set has a baseline slope ~80× steeper**
  than the redo (mean ~0.07 vs 0.0009 V/s) — a high-power drift signature, the
  plausible abort cause. **Hard proof it does not matter:** folding the aborted
  traces into the power/Stark fit shifts the AC-Stark bound only at the
  few-% level (it *tightens* slightly, well within the bound's own scatter),
  leaves $\kappa$
  unchanged, and cannot touch $\beta$ (the headline uses the 70/90/110 cooling
  sweep, never this session). **Decision: keep quarantined.** Re-admitting
  previously-cut, drift-flagged data *because* it tightens a bound is the mirror
  image of cherry-picking (both are results-driven exclusion calls, which the
  pre-registration exists to prevent); the tightening is marginal and the
  conclusion ($S_0 < \sim2$ MHz) is unchanged, so nothing is lost by holding the
  clean decision. The `qc_reason` column now records this concretely.

- **Transit-MC flux bug fixed + w₀ re-pinned 32 → 50 µm (2026-07-13; full detail
  in `docs/notes/transit_width_resolved.md`).** The M9 transit Monte-Carlo was missing
  the atom-crossing flux factor and ran ~2× too narrow; the corrected transit
  (validated against Lehmann's 41.2 kHz NNO example) excludes the 32 µm nominal
  and re-centres w₀ to ~50 µm. Every w₀-conditional fit was re-run; the
  model-independent headlines (the C1 width-slope bound, the power-sweep FWHM/amp)
  are unchanged. An earlier "w₀ ≈ 90 µm" note was a spurious factor-of-2 —
  retracted.

- **Literature provenance dig (2026-07-13, digestion turn A).** The Nieddu 2019 /
  Rajasree-KP 2020 direct beam-waist measurement (w₀ = 64 µm) and the resolution
  of a since-debunked "Nieddu 2.5 MHz" note are documented in full in
  `docs/LITERATURE.md` §6a — both external corroborations of the archival w₀ re-pin
  and the observed line width, not raised here to avoid duplicating that entry.
  **N(T) chain confirmed:** `rb5s6s/density.py` uses the Steck/Nesmeyanov liquid-Rb correlation
  + ideal gas — exactly the T→P→N chain the theses use (Rajasree cites Steck); no
  change. The June-2025 `Lab_plan` is a 4-week project-management doc (planned
  40–80 °C; the campaign actually went to 130 °C) and does NOT pin the beam
  geometry — so the w₀ prior legitimately rests on the Gaussian estimate +
  Nieddu's measurement, not the plan.
