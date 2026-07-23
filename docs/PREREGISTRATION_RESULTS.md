# Timestamp-audit report (pre-registered)

*Scored 2026-07-23 by `scripts/run_timestamp_audit.py` at commit `2e56815`
(committed before first contact with the backup; predictions committed at
`0af038b`, 2026-07-22 — the release that also carried them was later
withdrawn for unrelated scope reasons, see the pre-registration's §9). Quarantine copy frozen with a
SHA-256+MD5+size+epoch manifest before scoring. One run; this file is its
unedited output plus this provenance header.*

Backup (quarantine copy): `/Users/michelangelodondi/Documents/RawDataBackUp_QUARANTINE_2026-07-23`  ·  manifest rows: 297
Backup files seen: 325 (325 distinct basenames)

Manifest rows matched to backup: 282; missing: 15
  missing (first 10): rulers_t/4154nm_eom_070c1.csv, rulers_t/4154nm_eom_070c2.csv, rulers_t/4154nm_eom_070c3.csv, rulers_t/4154nm_eom_070c4.csv, rulers_t/4154nm_eom_070c5.csv, rulers_t/4192nm_eom_070c1.csv, rulers_t/4192nm_eom_070c2.csv, rulers_t/4192nm_eom_070c3.csv, rulers_t/4192nm_eom_070c4.csv, rulers_t/4192nm_eom_070c5.csv

## Integrity gates

* **T1 content identity: FAIL** — 273/297 rows byte-identical (MD5); 9 mismatched, 15 absent.
  mismatched (first 10): p_sweep/4121nm_125mw5.csv, p_sweep/4121nm_175mw3.csv, p_sweep/4121nm_075mw1.csv, p_sweep/4121nm_075mw2.csv, p_sweep/4121nm_075mw3.csv, p_sweep/4121nm_075mw4.csv, p_sweep/4121nm_075mw5.csv, p_sweep/4192nm_225mw1.csv, p_sweep/4192nm_075mw5.csv
* **T2 clock plausibility: PASS** — 282/282 mtimes inside 17–18 July 2025 (JST). Range seen: 2025-07-17 22:48:12 JST → 2025-07-18 20:26:34 JST.
* **T3 mass-copy signature: PASS** — largest shared-mtime fraction 0.4% (threshold 20%).
* **T4 granularity (recorded)** — 0/282 carry sub-second parts; 0 odd integer seconds (0 would suggest FAT 2 s).
* **T5**: all comparisons in raw epoch seconds; JST used for display only.
* **T6 clock of record** — native scope files present: 0 (mtimes are the clock of record if 0).

**INTEGRITY VOID — predictions deliberately not scored (per the gate table).**

---

# Timestamp audit — POST-HOC content-matched pass (NO pre-registered standing)

Backup (quarantine copy): `/Users/michelangelodondi/Documents/RawDataBackUp_QUARANTINE_2026-07-23`  ·  manifest rows: 297
Backup files seen: 325 (325 distinct basenames)

Manifest rows matched to backup: 296; missing: 1
  missing (first 10): p_sweep/4192nm_225mw1.csv

## Integrity gates

* **T1 content identity: FAIL** — 296/297 rows byte-identical (MD5); 0 mismatched, 1 absent.
* **T2 clock plausibility: PASS** — 296/296 mtimes inside 17–18 July 2025 (JST). Range seen: 2025-07-17 22:48:12 JST → 2025-07-18 20:26:34 JST.
* **T3 mass-copy signature: PASS** — largest shared-mtime fraction 0.3% (threshold 20%).
* **T4 granularity (recorded)** — 0/296 carry sub-second parts; 0 odd integer seconds (0 would suggest FAT 2 s).
* **T5**: all comparisons in raw epoch seconds; JST used for display only.
* **T6 clock of record** — native scope files present: 0 (mtimes are the clock of record if 0).

*POST-HOC MODE: scoring proceeds despite 1 absent row(s) (listed above and excluded); these verdicts carry no pre-registered standing.*

## Predictions

* **P1: PASS** — 0 cooling files predate the last power-session file (last P: 2025-07-18 05:01:38 JST; first T: 2025-07-18 06:14:36 JST)
* **P2: FAIL** — 16 adjacent inversions (4121:4/7st, 4154:4/7st, 4192:4/7st, 4207:4/7st; allowance ≤3)
* **P3: PASS** — 110°C 2025-07-18 07:08:43 JST < 90°C 2025-07-18 17:57:38 JST < 70°C 2025-07-18 19:40:19 JST
* **P4: PASS** — 0 temperature increases along the time-ordered block sequence
* **P5: PASS** — median intra-block gap 8.0 s vs inter-block 383.0 s → ratio 47.9 (needs ≥10)
* **P6: PASS** — all four peaks bracketed
* **P7: AMBIGUOUS** — 4154nm_070c1.csv|4154nm_070c2.csv absent from backup
* **P8: FAIL** — 4/194 curated copies predate their raw/ source
* **D5: PASS** — median 5-repeat block span 34.0 s (needs <70 s; range 20–148 s)

## Post-hoc (no pre-registered standing)

* step block p_sweep 4121 T=130 P=25: intra-block gaps [10, 16, 22, 12] s
* step block p_sweep 4192 T=130 P=125: intra-block gaps [30, 32, 10, 22] s
* step block p_sweep 4207 T=130 P=25: intra-block gaps [62, 20, 10, 20, 10] s
* step block p_sweep 4207 T=130 P=175: intra-block gaps [8, 128, 6, 6] s
* step block p_sweep 4207 T=130 P=225: intra-block gaps [14, 14, 8, 12] s
* step block t_sweep 4121 T=70 P=—: intra-block gaps [24, 6, 6, 6] s
* step block t_sweep 4192 T=70 P=—: intra-block gaps [10, 6, 6, 6] s
* step block t_sweep 4192 T=110 P=—: intra-block gaps [34, 18, 6, 6] s

*One run, everything reported. Scored by scripts/run_timestamp_audit.py at the commit recorded in the results report; criteria are the pre-registered ones and were not adjusted after seeing the data.*


### Status of every derived analysis D0–D5

The pre-registration listed six derived analyses. For completeness, since a
report that scores only the one that passed would be selective reporting:

| # | claim | status |
|---|---|---|
| **D0** | the archival drift rate lands below 4 MHz/min | **not scored** — withdrawn before the data was opened (§8.2/§8.3): the corroborating wavemeter photographs proved to be outside the campaign window, and the in-campaign record is consistent with the 4 MHz/min envelope |
| **D1** | measure the drift rate from intra-block scatter ÷ block duration | **void** — the archive itself showed the intra-block scatter is jitter, not accumulated drift (§8.4), so it cannot be divided by a duration to give a rate |
| **D2** | drift model, $T$ vs $\sqrt{T}$ scaling of intra-block scatter | **void with D1**, for the same reason: jitter does not scale with block duration |
| **D3** | re-centring frequency consistent with rate × elapsed ÷ window | **not scored** — depends on D1's rate, which has no route |
| **D4** | 5-repeat block ≈ 80 s, from scatter ÷ drift rate | **VOID** — its premise (that the scatter is drift) was tested and falsified before the backup was opened (§8.4) |
| **D5** | median 5-repeat block span under ~70 s | **PASS** — median 34 s (post-hoc pass above) |

D1–D3 were declared in §7 as "weaker in standing than P1–P8", and all three
died on the same finding, which was itself made and recorded before opening
the backup. None of them was retired after seeing the timestamps.

### Post-hoc reading (content-matched pass; no pre-registered standing)

* **The recollected power ladder was direction-reversed.** The clock shows
  **descending** power — before-rulers → 225 → 175 → 125 → 75 → 25 mW →
  after-rulers — on **all four peaks** (a 5-rung reversal = 4 adjacent
  inversions per peak = the 16 scored). Peak order 4192 → 4207 → 4154 → 4121,
  17 July 23:41 → 18 July 05:00 JST; cooling 110 → 90 → 70 °C through 18 July
  daytime. Recollection and clock agree on everything *except the direction*,
  which was remembered reversed — the pre-registered §6 consequence applies:
  the clock wins, `DATA.md` §2 is rewritten, and the disagreement is reported
  rather than reconciled.
* **P5 lands emphatically**: median 8 s between repeats vs 383 s between
  blocks (ratio 48) — "back-to-back, seconds apart" confirmed, and the 1.8 ms
  position-scatter reading built on it stands.
* **D5 lands**: median 5-repeat block span 34 s, under the ~70 s bound derived
  from the no-drift-trend result at the cavity-locked drift rate.
* **T1's 24 failures resolve at content level into curation history**: 15
  naming variants (`4154_eom_070c*` without "nm"), 8 re-takes renamed into
  canonical slots (`075mw_1→075mw1`, `125mw6→125mw5`, …) — the DATA.md §3.4
  renumbering, now directly visible — and **one genuine absence**:
  `p_sweep/4192nm_225mw1.csv`'s analysed bytes are nowhere in this backup.
* P8's 4 flagged rows are a name-collision artifact of content-mode matching
  (a consistent-name recheck finds zero curated-before-raw violations);
  P7 is AMBIGUOUS because the pair names are naming-variant casualties.
* The backup carries a workspace file literally named
  `2025-07-17-Julia.code-workspace`, and every mtime has even seconds — the
  FAT 2 s signature of the stick it lived on.

---

## Addendum, 2026-07-23 (post-release consistency check)

**Edit ledger for the frozen pre-registration.** Its header forbids edits
after the backup is read, with corrections directed here. Post-run, exactly
one commit touched it (`d50366d`), and `git diff` confirms zero lines of the
prediction/gate/consequence tables (§1–§8) changed — the edit rewrote only §9,
the release-provenance note, after the `v1.0.0`–`v1.2.0` withdrawals. The
freeze on the scientific content held; this ledger is the audit of that claim.

**Corrected step-block listing.** The post-hoc section above was produced by a
scorer whose step-block filter used `"25.0"`-style power strings against a
manifest storing bare integers, so its five `p_sweep` entries silently matched
nothing and only the three `t_sweep` blocks printed. With the filter fixed
(same commit series), the full eight:

* step block p_sweep 4121 T=130 P=25: intra-block gaps [10, 16, 22, 12] s
* step block p_sweep 4192 T=130 P=125: intra-block gaps [30, 32, 10, 22] s
* step block p_sweep 4207 T=130 P=25: intra-block gaps [62, 20, 10, 20, 10] s
* step block p_sweep 4207 T=130 P=175: intra-block gaps [8, 128, 6, 6] s
* step block p_sweep 4207 T=130 P=225: intra-block gaps [14, 14, 8, 12] s
* step block t_sweep 4121 T=70 P=—: intra-block gaps [24, 6, 6, 6] s
* step block t_sweep 4192 T=70 P=—: intra-block gaps [10, 6, 6, 6] s
* step block t_sweep 4192 T=110 P=—: intra-block gaps [34, 18, 6, 6] s

One reading falls out (post-hoc, no standing): the block with the largest
position step — `4207 @175 mW`, whose axis offset jumps ~1140 ms between
repeats 2 and 3 — shows a **128 s pause at exactly that boundary**, against
6–14 s everywhere else in the block. The step and the pause coincide: the
scope was adjusted during a two-minute interruption, which is precisely the
"usually, not always" form of the no-touch tendency the experimenter reported.

---

## Addendum 2, 2026-07-23 — what the backup holds that the analysed set does not

A propagation check asked whether every audit finding had reached the
documents. Two had not, and chasing the second overturned a claim made in
Addendum 1.

**34 backup-only CSVs.** Names present in the backup but in neither the
manifest nor the local `data/` tree. Of these, 24 are byte-identical to an
analysed trace (the curation renaming, already documented in `DATA.md` §3.3–3.4
and now directly visible), and **10 carry content that exists nowhere in the
analysed set** — mostly extra repeats at 993.4121 nm / 75 mW (a 6th–9th, plus
an eight-file re-take series). They sit inside the campaign window. These are
the curation-time discards: the repo says they were dropped because they
"seemed quite bad", and the backup is now the only place they survive.

> **Corrected by addendum 3: the figure is 19, not 10.** This count was
> made by matching filenames, which hid an entire re-taken series behind
> names identical to analysed files. Content hashing is the only correct
> test. The paragraph is left as written; the correction is below.

**The one T1 absence is not a loss — it is the reverse.** Addendum 1 recorded
that `p_sweep/4192nm_225mw1.csv`'s analysed bytes are absent from the backup,
and called it a genuine absence. That is true but misleading. The backup
contains a file of that name, and it is the **pristine original**; the analysed
copy is a degraded export of it:

| | analysed copy (`data/raw/`, `power/`, `power copy/`) | backup original |
|---|---|---|
| size | 37 558 B | **53 841 B** |
| header | `jj,nj` — corrupted | `x-axis,2` — standard InfiniiVision |
| time values | `-4.68E-01` (3 s.f.) | `-468.0000E-03` (7 s.f.) |
| duplicate timestamps | **799 of 1999** | **0** |
| distinct Δt | 3 | 1 (uniform) |

Both hold 1999 points over the same −0.468 → +0.531 s window, and the voltages
agree to 5.0 mV — which is the quantisation of the degraded copy, about 0.3× that
trace's own wing noise (16.0 mV), so the amplitude penalty is modest. The time
axis is the real damage: a third of the samples carry a duplicated timestamp,
which is precisely the aliasing `DATA.md` §3.2 describes and which
`rb5s6s/ingest.py` special-cases for this one file.

So the repo has been treating a recoverable export defect as an inherent
property of the data.

**And it then turned out not to matter — measured, not assumed.** The obvious
next question is whether the pristine original changes anything, so it was
substituted for the degraded copy and the affected fits re-run (read-only; the
analysed tree was not modified):

| quantity | analysed (degraded) | with backup original | shift |
|---|---|---|---|
| γ_coll, 4192 @ 225 mW | 0.4379 ± 0.0222 MHz | 0.4395 ± 0.0221 | **+0.07σ** |
| σ_laser, same condition | 0.9797 ± 0.0765 MHz | 0.9770 ± 0.0763 | **−0.04σ** |
| β_self slope, 4192 density lever | +0.00695 ± 0.00186 | +0.00701 ± 0.00186 | **+0.03σ** |

The trace is flagged `serves_t130`, so it also anchors the hot end of that
peak's density lever — the β_self headline — which is why the lever was tested
too and not just the power condition. Every shift is far inside the noise.

The defect was real, recoverable, and harmless. `ingest.py`'s special-casing
of this file was doing its job. Nothing is retracted, nothing is re-issued,
and the analysed tree is left exactly as it was — but the question is now
closed with a number instead of an assumption, which is the difference between
"documented" and "checked".

*Post-hoc throughout; no pre-registered standing.*

---

## Addendum 3, 2026-07-23 — the discards, tested on the fitted observable

Addendum 2 said 10 backup files "carry content that exists nowhere in the
analysed set". **That undercounts: the correct figure is 19.** The error was
matching on filenames — an entire re-taken series hides behind names identical
to analysed files. The backup's `4121nm_075mw1.csv` and the analysed
`p_sweep/4121nm_075mw1.csv` share a name and differ in content: the analysed
copy descends from `4121nm_075mw_1.csv`, the *underscore* re-take. Content
hashing is the only correct test; 19 of 320 backup CSVs are unique.

**This makes assumption 8 testable for the first time.** The methods chapter
holds that discards are curation-time (pre-analysis) decisions and therefore
"cannot bias the fits"; `DATA.md` §3.4 records the reason given — the dropped
acquisitions "seemed quite bad". Until the backup surfaced no audit could see
them. At 993.4121 nm / 75 mW it holds **two complete takes**:

| group | n | median SNR | median height | median FWHM | fate |
|---|---|---|---|---|---|
| first take (`075mw1–9`) | 9 | 59.1 | 0.1220 V | **63.50 ms** | all discarded |
| re-take (`_1,_2,_3,_5,_6`) | 5 | 64.9 | 0.1356 V | **63.50 ms** | kept as canonical |
| re-take (`_4,_7,_8`) | 3 | 65.6 | 0.1347 V | **63.50 ms** | dropped |

Mann–Whitney, kept vs each dropped group:

| | SNR | height | **FWHM** |
|---|---|---|---|
| vs first take | p = 0.0020 | p = 0.0010 | **p = 0.89** |
| vs re-take dropped | p = 0.39 | p = 0.79 | **p = 0.76** |

**The decisive column is the last one.** The first take is genuinely dimmer —
significantly so in brightness, which vindicates "seemed quite bad" — but the
**linewidth is identical across all three groups**. Width is what the pipeline
fits: γ_coll, σ_laser and β_self are width observables, and amplitude enters
only the separate M7/M10 ratio work. A discard that does not move the fitted
observable cannot bias the fit that uses it, whatever it does to brightness.

The three re-take traces dropped to reach N = 5 differ from the kept five in
nothing at all — the signature of truncation, not cherry-picking.

**The other seven unique files, checked the same way.** Twelve of the 19 are
the two takes above. Of the remaining seven, one is the pristine original of
`4192nm_225mw1.csv` and two are its degraded unreadable copies (Addendum 2);
the last four are single surplus acquisitions, one per condition. Each is
compared with the five kept repeats *at its own condition*, since width is
power-broadened and pooling across conditions would be wrong.

> **Read the names carefully.** Nine of these 19 filenames *also exist in
> `data_raw/`, holding different traces* — that is exactly how the re-take
> history stayed hidden until content hashing exposed it. Every file named
> in this addendum is the **backup copy**, identified by content hash, never
> by name. Opening the same-named file in `data_raw/` will give different
> numbers, and that is a collision, not a contradiction.

| surplus discard (backup copy) | its FWHM | kept five at that condition | z of the discard vs those five |
|---|---|---|---|
| `4121nm_125mw5` <br/>`md5 2acede0b…` | 64.50 ms | 63.80 ± 1.20 ms | +0.58 |
| `4121nm_175mw3` <br/>`md5 7afa9e0f…` | 64.00 ms | 62.90 ± 1.08 ms | +1.01 |
| `4121nm_225mw6` <br/>`md5 cdf0b163…` | 61.50 ms | 62.80 ± 0.84 ms | −1.55 |
| `4192nm_075mw5` <br/>`md5 17646bc8…` | 62.50 ms | 64.60 ± 0.65 ms | **−3.22** |

Three are central. **The fourth is not, and is reported rather than smoothed
over.** Tested properly — a 95% prediction interval for a sixth draw from five
points, not a z against a five-point σ — it falls outside by 0.12 ms, which is
*less than the 0.50 ms quantisation of the metric itself*; its SNR (127) is
indistinguishable from its siblings' median (129), so it was surplus, not a
quality cut. Had it been kept, that block's mean width would move by −0.54%,
against an archive-wide observed linewidth spread of 3–8%. One boundary case
in four, smaller than the metric's own resolution, is not evidence of
width-selective curation — but it is the honest limit of what this test can
say, and it is why the claim above is "indistinguishable in the fitted
quantity", not "identical".

**An independent set, which this addendum first overlooked.** The claim that
only backup-preserved discards can be tested was wrong: `data_raw/discarded/`
has published four raw-only discards since the archive was built, from the
temperature sweeps, with no connection to the backup — and the curation audit
of 2026-07-11 had already examined them, finding `4154nm_070c4` about 27%
dimmer than its siblings and the other three clean (`DATA.md` §6). What is
new here is not the look but the axis: that audit judged them on brightness
and structure, this one on the quantity the fits actually use. Run against
the kept repeats at their own conditions:

| discarded (already public) | its FWHM | kept at that condition | z | its SNR vs kept median |
|---|---|---|---|---|
| `4154nm_070c4` | 59.00 ms | 55.38 ± 2.66 ms (n=4) | +1.36 | 20.5 vs 25.2 |
| `4192nm_090c3` | 60.00 ms | 61.00 ± 1.66 ms (n=5) | −0.60 | 114.8 vs 115.9 |
| `4207nm_025mw2` | 60.00 ms | 61.80 ± 3.93 ms (n=5) | −0.46 | 14.8 vs 14.5 |
| `4207nm_070c2` | 56.50 ms | 59.60 ± 2.07 ms (n=5) | −1.49 | 15.6 vs 14.4 |

All four sit inside their conditions' spread, at SNRs indistinguishable from
their siblings. Different sweeps, different peaks, a provenance independent of
the backup — and the same answer.

**The count, stated once and exactly.** Of the 19 unique backup files, three
are not discards (the pristine `4192nm_225mw1` original and its two degraded
copies), leaving **16 discarded acquisitions**; `data_raw/discarded/` holds
**4** more. All **20** have now been tested — 12 as two takes by rank test,
8 individually against their own conditions. Seven of the eight individual
cases are central; the eighth is the boundary case above.

One limit still stands: this half-max width is a QC metric, coarser than the
model widths the fits report. And 20 is what survives — not what was taken.

So assumption 8 holds on the evidence, and for a sharper reason than
"curation was pre-analysis": the discarded material is *indistinguishable in
the fitted quantity*. That is consistent with the repo's stated exclusion rule
(`rb5s6s/qc.py`: "QC-based, never result-based").

*Method note, recorded because it was caught rather than avoided: the first
version of this analysis compared SNR and height and declared the discard
"justified". SNR and height are not what the analysis fits. The grouping was
also wrong — a regex silently matched nothing and pooled all 17 traces into
one bin, so the p-values in that draft were computed on a mis-partitioned set.
Both were corrected before this addendum was committed; the corrected result
is stronger than the flawed one, which is luck, not method.*

*Post-hoc throughout; no pre-registered standing. Nothing re-fitted, nothing
retracted.*


## Addendum 4, 2026-07-23 — the drift rate, recovered by differencing

**The estimator is the experimenter's, proposed after Addendum 3:** treat the
hand re-centrings as offset steps that move the frequency but leave the
underlying drift untouched, and difference positions inside spans the steps
cannot reach — the steps then cancel identically, and the drift rate survives.
The archive alone had no clock to difference against;
`run_intrablock_trend.py` closed with "no lever on the drift rate at all".
The recovered timestamps restore the lever. (`scripts/run_drift_settling.py`,
stdout-only, skips cleanly where the backup is absent.)

Two differencing baselines exist in the power session, and they disagree —
the disagreement is what identifies the interventions:

| probe | baseline | what it contains | result |
|---|---|---|---|
| within blocks, vs real time | ~30 s | pure drift (nothing moved inside a block) | −2.3 ± 1.1 ms/min early, +1.2 ± 0.7 late — **bounds**: below 4 ms/min in magnitude at every epoch |
| between adjacent blocks of one ladder | 3–14 min | drift **plus re-centrings** (the reference was moved in exactly those gaps, while power was being changed) | 6–9 ms/min apparent in hour 1, collapsing to +0.4–0.7 after hour 3.7 |

The hour-1 between-block rates exceed the within-block bound severalfold, so
they are not drift: they are the **operator interventions**, both signs,
±20–70 ms (±1–3 MHz on the laser axis). Their signature is independent:
mid-block position steps concentrate early (4 of 10 early blocks vs 1 of 10
late).

**What settles is the disturbance — and the refined fit makes that
quantitative.** Taking the proposal to trace level, all 99 timestamped
positions enter one segmented joint fit: per-segment offsets absorb the
interventions, one smooth r(t) is shared by every segment, the segmentation
is found iteratively (≥4σ standardized steps, per-trace σ from each block's
own robust scatter), and the same segmentation serves both rate laws so the
AIC compares models, not segmentations. The exponential wins decisively —
**ΔAIC ≈ +196** (scale-profiled likelihood), **τ = 73 [54, 102] min** — the
same ~1–1.5 h thermal settling scale the wavemeter photographs show after a
retune (`APPARATUS.md` §6). One caveat is structural, and the layering above
exists because of it: a gap-step consistent with the fitted r(t) is absorbed
*as* drift, so sub-threshold interventions can masquerade — and in one early
block the within-block slope disagrees with the fitted rate at ~3σ. The
within-block bounds, not the joint fit, own the pure-drift claim; τ
describes drift and forced re-centrings jointly.

> **Superseded by addendum 5:** the state-space refinement finds the drift
> is one *constant* +0.032 [+0.023, +0.040] MHz/min laser — these floor
> estimates sat 1–1.5σ low because their exponentials leaked early drift.
> The paragraph is left as written; the refinement is below.

**The settled floor is a detection, not a bound, and it agrees across all
three estimators**: joint fit **+0.30 [+0.19, +0.37]**, pair median
+0.50 ± 0.60, tight-cluster mean +0.55 ± 0.17 ms/min — positive in every
one, i.e. **0.013–0.023 MHz/min on the laser axis (0.03–0.05 transition)**.
Over a 32 s block that is ~0.2–0.3 ms of centre walk, below the 1.8 ms
jitter, which is why the pre-registered intra-block test rightly returned
JITTER (§8.4's verdict stands untouched).

**The intervention census falls out of the same fit**: 13 segments over four
ladders — hour-1 hunting on 4192 (steps of −1.6 and +1.0 MHz laser within
25 min), the two 4207 scan-window repositionings (+24 and −49 MHz), and
end-of-ladder nudges of ±0.2–0.9 MHz — frequent early, nearly absent after
hour 4.

**Concordance with the wavemeter photographs** (`APPARATUS.md` §6), fully
independent evidence: the early-epoch archive bound (≲0.17 MHz/min laser)
matches the photographed cavity-locked figure (±0.19 MHz/min); the settled
0.013–0.023 MHz/min sits an order below, as an hours-deep lock should; and
the joint fit's τ matches the photographed post-retune settling time.

**Per-temperature re-kicks — the "one exponential per temperature" half of
the proposal — remain unresolved.** The T-session ruler→science spans are
operator-contaminated (the reference was adjusted *between* ruler and science
acquisition: those spans jump ±100 ms both signs in two minutes), and the
intra-block bounds there (|r| ≲ 5 ms/min per dwell) leave no room to test a
re-kick smaller than that. Not confirmed, not refuted, bounded.

**D0 postscript.** D0 — declared genuinely uncertain before the backup was
opened — is post-hoc satisfied in every epoch probed: settled 0.05, early
≲ 0.34 (transition axis), envelope 4 MHz/min *[correction, same day: the
envelope constant is laser-axis — the mislabel does not change the verdict,
the margin is ~60× either way]*.

No shipped number moves: widths are per-trace, and centre steps do not enter
them. *Post-hoc throughout; estimator proposed by the experimenter
2026-07-23; scored by no pre-registered rule.*


## Addendum 5, 2026-07-23 — the model refined: the drift never settled; the hand did

Addendum 4 fitted one smooth r(t) with hard-segmented offsets and declined to
split drift from re-centrings. The refinement replaces the greedy
segmentation with the model the data actually implies: **a state-space
formulation** in which the cumulative-intervention offset is a random walk
whose steps live at the between-block gaps, η ~ N(0, σ_gap(t)²), with
scan-window repositionings (steps >100 ms, wherever they occur — the 4207
excursion returns *mid-block*) freed exactly. The marginal likelihood is then
exact (Kalman filter), no segmentation is chosen by hand, and — the point —
**drift and intervention amplitude each get their own time law**, so "what
settles?" becomes a 2×2 model comparison:

| drift law | intervention law | AIC |
|---|---|---|
| constant | constant | 634.6 |
| **constant** | **exponential** | **617.5** |
| exponential | constant | 638.6 |
| exponential | exponential | 621.5 |

**The drift is one constant.** Adding a drift-settling term buys nothing
(ΔAIC +4.0 — pure parameter penalty, the amplitude fits to zero);
intervention settling is decisive (ΔAIC +17.1). The claim addendum 4
declined is now made, in both directions:

- **Drift: c = +0.74 [+0.54, +0.94] ms/min (68%, profile likelihood; 95%
  [+0.24, +1.24]) = +0.032 [+0.023, +0.040] MHz/min laser axis** — one
  constant rate across the five-hour power session, the span the fit sees
  (the T-session probes are operator-contaminated and give only bounds,
  ≲0.2 MHz/min, which contain it). If it persisted, ~39 MHz laser across
  the 20.5 hours — the scale that forced the all-night re-centring. Robust:
  dropping
  peak 4207 entirely moves c by +0.013; window-move thresholds of 60 and
  150 ms move it by less than 0.02.
- **Interventions: σ_gap ≈ 88 ms × exp(−t/86 min)** — per-gap re-centring
  RMS ~1–4 MHz laser in hour 1, ≲0.2 MHz after hour 4. τ_i is the least
  stable number (≈70–160 min across the same variants, trading against the
  amplitude on only ~14 constrained gaps); the *structure* — interventions
  settle, drift does not — survives every variant.

**What this corrects in the earlier addenda, stated plainly:** the τ ≈ 73 min
exponential of addendum 4 was the *operator's* settling, not the laser's —
consistent with it matching the wavemeter's post-retune scale, since re-lock
transients are exactly when the operator re-centres hardest. The earlier
"settled floor" of 0.013–0.023 MHz/min sits 1–1.5σ below the constant
because those decompositions leaked early drift into their exponentials;
**+0.032 [+0.023, +0.040] MHz/min laser supersedes it.** The within-block
bounds (|r| ≲ 4 ms/min) contain the constant comfortably and stay the
model-free anchor. D0's envelope, compared on its own axis: measured
constant 0.032 [0.023, 0.040] vs 4 MHz/min laser — **~125× inside**.

The observation-noise scale fits at 1.93× the block MADs — effective
per-trace noise 1.5–3 ms, consistent with the 1.8 ms jitter figure, closing
the loop with §8.4.

*Post-hoc; same estimator lineage (experimenter, 2026-07-23), model
refinement requested the same day. `scripts/run_drift_settling.py`, final
stage; runs in seconds; skips cleanly without the backup.*


### Postscript to addendum 5, same day — the per-temperature question, split

The refined model splits the last unresolved item of addendum 4 in two, and
answers one half. For the **drift**, per-temperature re-kicks stay untestable
(the T-session baselines are too short; intra-block bounds ≲5 ms/min per
dwell). For the **operator**, the answer was hiding in the discarded probe:
under the state-space reading, the ruler→science steps that *contaminate* the
drift estimate simply *are* the intervention amplitude — and it re-kicks at
every dwell:

| dwell | steps (n) | RMS step | in frequency |
|---|---|---|---|
| 110 °C (t ≈ 6.6–7.9 h) | 4 | 74 ms | 3.1 MHz laser |
| 90 °C (after the 9.6 h break) | 3 | 137 ms | 5.8 MHz laser |
| 70 °C | 3 | 106 ms | 4.5 MHz laser |

Against the ≲20 ms the amplitude had settled to by late P-session, every
dwell is an order larger; the single biggest step (237 ms ≈ 10 MHz) lands
immediately after the 9.6 h break — the freshest re-lock, the same one
IMG_2896 photographed mid-transient. Each temperature change, with its
per-peak retunes, begins a fresh re-acquisition transient: **the "one
exponential per temperature" of the original proposal holds — for the
disturbance, not the laser.**

*Descriptive RMS over 3–4 single steps per dwell, retunes and window moves
included; not a fitted σ_gap. Same post-hoc standing as the rest.*


### Second postscript to addendum 5 — the mechanism, recalled after the fit

Later the same day, the experimenter supplied what the model could not:
**the cavity lock was dropping out on its own, typically within a few tens of
minutes — especially while the etalon temperature transient (about 2 h of
lock-on after ≥3 h of lock-off) had not yet passed.**

The order matters, so it is recorded: the state-space fit found the
disturbance amplitude settling with **τ = 86 [70, 104] min, blind** — the
recollection of a **~2 h transient** came after, unprompted by the number.
That is a corroboration, not a fit to testimony.

It also re-reads the whole disturbance story one level deeper:

- σ_gap(t) is physical: **the typical frequency excursion per
  drop-and-recapture cycle.** A recapture onto an unchanged set point lands
  small; a drop mid-transient, with the etalon still walking, lands MHz-large.
  The decay of σ_gap is the etalon thermalising.
- The timeline agrees in detail. The P session opened inside a transient
  (hour-1 chaos, 4 of 10 blocks stepped mid-block); its late ladders sat past
  one (σ_gap ≲ 20 ms). After the 9.6 h daytime break — far longer than the
  3 h that resets the etalon — the re-lock at ~17:03 (IMG_2896, photographed
  mid-settling) restarted the clock, and **both evening dwells ran inside or
  at the edge of that fresh transient** (90 °C at 18–73 min after re-lock,
  70 °C at 118–195 min). That is why the 70 °C dwell never calmed to
  late-P-session quietness — the puzzle the first postscript left open.
- "The hand settled" therefore sharpens to: **the lock's dropout disturbance
  settled with the etalon; the hand executed the recaptures.** The constant
  +0.032 MHz/min laser is the drift of the *held* lock, which is exactly why
  it matches the cavity-locked wavemeter photograph.

Two honest limits: mtimes cannot resolve any individual step into drop vs
deliberate move (during the transient the hour-1 hunting is plainly a mix),
and the τ-to-transient match is a scale agreement (86 [70, 104] min vs
"about 2 h"), not a calibration.

*Testimony: EXPERIMENTER, 2026-07-23, after the committed fit. Everything
else post-hoc as before.*
