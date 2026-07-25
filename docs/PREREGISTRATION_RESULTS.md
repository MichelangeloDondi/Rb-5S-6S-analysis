# Timestamp-audit report (pre-registered)

*Scored 2026-07-23 by `scripts/run_timestamp_audit.py` at commit `2e56815`
(committed before first contact with the backup; predictions committed at
`0af038b`, 2026-07-22 — the release that also carried them was later
withdrawn for unrelated scope reasons, see the pre-registration's §9). Quarantine copy frozen with a
SHA-256+MD5+size+epoch manifest before scoring. One run; this file is its
unedited output plus this provenance header.*


## What this document establishes — one page

*Added 2026-07-25 as a reader's entry point. Everything below it is the
original record, in the order it happened, including the readings it later
had to correct.*

**The situation.** The 2025 archive was frozen with no acquisition
timestamps. A backup that carried them surfaced a year later. Before opening
it, predictions were committed about what it would contain
([`PREREGISTRATION_timestamps.md`](PREREGISTRATION_timestamps.md), commit
`0af038b`); the quarantine copy was then frozen under a
SHA-256+MD5+size+epoch manifest and scored once.

**The audit voided.** Its own integrity gate — content identity between
archive and backup — failed at T1. That verdict stands unedited, and
everything after it is labelled **post-hoc**, with no pre-registered
standing. The gate did its job: it stopped a favourable-looking result from
being reported as a confirmed one.

**What the labelled post-hoc pass then established** (each reproducible from
a clone via `scripts/run_drift_settling.py`, off the committed
[`CLOCK.csv`](../data_recovered/CLOCK.csv)):

| finding | where |
|---|---|
| The recorded block order is **not** the acquisition order — the power ladder ran 225→25 mW | addendum 8 |
| The lock drift is **one constant**, +0.016 [0.007, 0.025] MHz/min (laser axis) — ~250× inside the pre-registered envelope | addenda 4–7 |
| The megahertz-scale motion was **not drift** but hand re-centring after lock dropouts | addendum 5 |
| That disturbance is **one transient re-armed by every re-lock**: B = 103 [78, 139] ms, τ = 97 [87, 118] min | addendum 12 |
| A **second, campaign-wide** timescale is absent, and bounded (< 0.4–1.9 MHz depending on assumed τ) | addendum 12 postscript |
| The four peaks of each dwell were acquired **54–76 min apart**, so the σ_laser-sharing assumption was never "close in time" | addendum 12 / [RESULTS.md](RESULTS.md) C1 |
| The detection chain carries a **61 Hz mains line at ~0.2 % of peak** — averaged over by a 60 ms line, harmless here | addendum 13 |
| The **P² two-photon law** holds in a third epoch (slopes 1.87–2.36) | addendum 14 |

**What it corrected about itself.** Three readings were withdrawn after
being published here: a "~32 ms satellite" structure that was an artifact of
the analysis's own peak-finder (addendum 11 postscript); a width-versus-power slope from
the rehearsal, retired once the dual-scan geometry showed its envelope is
~120× the linewidth (addendum 14); and a mains-line "epoch suppression"
claim that compared each chain to its own noise floor and inverted the
conclusion (correction inside addendum 13).

**What none of it changed.** No number in [`results/`](../results/) moved.
Widths are per-trace and centre steps do not enter them. The clock
characterises the instrument, dates a design flaw — four peaks spread over an
hour — and specifies its remedy in [`PLAN.md`](PLAN.md); it does not
re-open a fitted result.

---

**Contents** *(navigational aid, updated 2026-07-25 — the report below is unedited)*

- [What this document establishes — one page](#what-this-document-establishes--one-page)
- [Integrity gates](#integrity-gates)
- [Integrity gates](#integrity-gates-1)
- [Predictions](#predictions)
- [Post-hoc (no pre-registered standing)](#post-hoc-no-pre-registered-standing)
  - [Status of every derived analysis D0–D5](#status-of-every-derived-analysis-d0d5)
  - [Post-hoc reading (content-matched pass; no pre-registered standing)](#post-hoc-reading-content-matched-pass-no-pre-registered-standing)
- [Addendum, 2026-07-23 (post-release consistency check)](#addendum-2026-07-23-post-release-consistency-check)
- [Addendum 2, 2026-07-23 — what the backup holds that the analysed set does not](#addendum-2-2026-07-23--what-the-backup-holds-that-the-analysed-set-does-not)
- [Addendum 3, 2026-07-23 — the discards, tested on the fitted observable](#addendum-3-2026-07-23--the-discards-tested-on-the-fitted-observable)
- [Addendum 4, 2026-07-23 — the drift rate, recovered by differencing](#addendum-4-2026-07-23--the-drift-rate-recovered-by-differencing)
- [Addendum 5, 2026-07-23 — the model refined: the drift never settled; the hand did](#addendum-5-2026-07-23--the-model-refined-the-drift-never-settled-the-hand-did)
  - [Postscript to addendum 5, same day — the per-temperature question, split](#postscript-to-addendum-5-same-day--the-per-temperature-question-split)
  - [Second postscript to addendum 5 — the mechanism, recalled after the fit](#second-postscript-to-addendum-5--the-mechanism-recalled-after-the-fit)
- [Addendum 6, 2026-07-23 — the centre channels, attempted at the experimenter's insistence](#addendum-6-2026-07-23--the-centre-channels-attempted-at-the-experimenters-insistence)
- [Addendum 7, 2026-07-23 — the residual audit: the noise model was wrong, and it biased the drift](#addendum-7-2026-07-23--the-residual-audit-the-noise-model-was-wrong-and-it-biased-the-drift)
- [Addendum 8, 2026-07-24 — a second source folder closes the last absence](#addendum-8-2026-07-24--a-second-source-folder-closes-the-last-absence)
- [Addendum 9, 2026-07-24 — the backup grows: a dated duplicate, the pilot, and the program's prehistory](#addendum-9-2026-07-24--the-backup-grows-a-dated-duplicate-the-pilot-and-the-programs-prehistory)
- [Addendum 10, 2026-07-24 — consolidation: the clock becomes data, the backup becomes an archive](#addendum-10-2026-07-24--consolidation-the-clock-becomes-data-the-backup-becomes-an-archive)
- [Addendum 11, 2026-07-24 — the prehistory exploited: the clock validated in-file, the model tested out of sample](#addendum-11-2026-07-24--the-prehistory-exploited-the-clock-validated-in-file-the-model-tested-out-of-sample)
  - [Postscript to addendum 11, 2026-07-24 — two of its open questions closed by analysis](#postscript-to-addendum-11-2026-07-24--two-of-its-open-questions-closed-by-analysis)
- [Addendum 12, 2026-07-24 — the re-kick, fitted: one transient, restarted by every re-lock](#addendum-12-2026-07-24--the-re-kick-fitted-one-transient-restarted-by-every-re-lock)
  - [Postscript to addendum 12 — a second timescale, tested and bounded](#postscript-to-addendum-12--a-second-timescale-tested-and-bounded)
- [Addendum 13, 2026-07-25 — the detection chain's noise spectrum, and a mains line chased into the archive](#addendum-13-2026-07-25--the-detection-chains-noise-spectrum-and-a-mains-line-chased-into-the-archive)
- [Addendum 14, 2026-07-25 — the last extraction: one test that does not port, one that does](#addendum-14-2026-07-25--the-last-extraction-one-test-that-does-not-port-one-that-does)
- [Addendum 15, 2026-07-25 — the temperature notation resolved, and the cold spot given a first number](#addendum-15-2026-07-25--the-temperature-notation-resolved-and-the-cold-spot-given-a-first-number)
  - [Postscript to addendum 15, 2026-07-25 — the isotope route tested, and closed](#postscript-to-addendum-15-2026-07-25--the-isotope-route-tested-and-closed)
- [Addendum 16, 2026-07-25 — the cold spot by maximum likelihood, where slope-fitting failed](#addendum-16-2026-07-25--the-cold-spot-by-maximum-likelihood-where-slope-fitting-failed)
  - [Postscript to addendum 16 — "cross-session" is the wrong word for the 130 °C point](#postscript-to-addendum-16--cross-session-is-the-wrong-word-for-the-130-c-point)
- [Addendum 17, 2026-07-25 — the pilot ran hot: its oven label is a set point, not a reading](#addendum-17-2026-07-25--the-pilot-ran-hot-its-oven-label-is-a-set-point-not-a-reading)

---

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
one commit touched it (`f9918c8`), and `git diff` confirms zero lines of the
prediction/gate/consequence tables (§1–§8) changed — the edit rewrote only §9,
the release-provenance note, after the `v1.0.0`–`v1.2.0` withdrawals. The
freeze on the scientific content held; this ledger is the audit of that claim.

**Hash supersession, 2026-07-25 — a bookkeeping note, not a correction.** A
message-only history rewrite (commit-message register only; `git diff`
between every pre- and post-rewrite commit is empty, and all tree hashes
match 1:1 in order) changed the identity of every commit from
`2026-07-22` 06:xx onward, including ones this audit trail cites as
provenance. `docs/PREREGISTRATION_timestamps.md` is itself frozen — its own
header forbids editing it even for this — so its citations
(`fd45da6`, `0af038b`, `2e56815`, `4592296`) are left exactly as written;
their current identities are `ff505ea`, `6d68b4b`, `853cb72`, `29c8d45`
respectively, content-for-content identical (`git show --stat` on each new
hash reproduces the same file list and prose the old hash did). `9190b0b`
(the campaign chronology) predates the rewritten range and is unaffected.

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
"seemed quite bad", and the backup is now the only place they survive
*(no longer: since addendum 10 they are published in
`data_recovered/discarded_backup/` and preserved in the release asset)*.

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
width-selective curation — but the test cannot rule it out either, which is
why the claim above is "indistinguishable in the fitted
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

> **Superseded — final value in addendum 7:** the state-space refinement
> first found a constant +0.032 MHz/min laser and called these floors low
> (addendum 5); the residual audit then showed that number was biased by
> unmodelled moves, and the adequate model lands at
> **+0.016 [+0.007, +0.025] MHz/min — in agreement with these floor
> estimates after all.** The paragraph is left as written; the audit trail
> is below.

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

> **Superseded by addendum 7:** the residual audit found this noise model
> inadequate (three real end-of-ladder moves absorbed as drift, kurtosis +7);
> under the mixture model c = +0.38 [+0.17, +0.59] ms/min — a ~2σ indication,
> not a 3σ detection. The paragraph stands as written; the audit is below.

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
**+0.032 [+0.023, +0.040] MHz/min laser supersedes it** *(a claim addendum 7
itself supersedes: under the adequate noise model the constant is +0.016
[+0.007, +0.025], agreeing with those floors — the leak ran the other way)*.
The within-block
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

Two limits stand: mtimes cannot resolve any individual step into drop vs
deliberate move (during the transient the hour-1 hunting is plainly a mix),
and the τ-to-transient match is a scale agreement (86 [70, 104] min vs
"about 2 h"), not a calibration.

*Testimony: EXPERIMENTER, 2026-07-23, after the committed fit. Everything
else post-hoc as before.*


## Addendum 6, 2026-07-23 — the centre channels, attempted at the experimenter's insistence

The two-epoch framing writes the archive's centres off wholesale, and this
report had repeated that line without testing it. The experimenter pushed
back, arguing the centre observables deserved a real attempt before being
written off — correctly on both counts: no attempt had been made, and for
one of the three centre observables an attempt succeeds.

**1. The AC-Stark pull: a real bound, from centres alone.** The pull
(−⅔S₀, S₀ = κP) is a *differential* observable: it is locked to the power
ladder and repeats at four different times, so it separates from the
recapture random walk (zero-mean, blind to P) and from drift (which follows
elapsed time, not P). Adding a deterministic q·P term to the state-space
observation and profiling q:

- **q = +0.003 [−0.117, +0.123] ms/mW (95%)** → pull(225 mW) ∈ [−2.2, +2.4]
  MHz transition → **S₀(225 mW) < 3.5 MHz (95%) from the centre channel
  alone**.
- *(Addendum 7 re-profiles this under the adequate noise model:
  < 5.5 MHz — the mixture discounts the 25 mW anchors where the moves live.)*
- **Injection closure**: a pull injected into the real positions at 1×, 4×
  and 10× the predicted size is recovered to ±0.0001 ms/mW. The estimator is
  unbiased; only the recapture-noise floor limits it.
- The width-channel archival bound (M4e, profile likelihood) is
  S₀(225) < 0.63 MHz — so the centre channel is **~5.5× looser**, and the
  first draft of this addendum quoted the superseded Wald diagnostic
  (3.1) beside it until the canonical-value gate caught the stale citation.
  The two channels **corroborate each other through disjoint systematics** —
  ramp broadening in the widths, centroid displacement in the centres. The
  centre floor sits ~6× above the 0.59 MHz prediction, where the width
  channel already presses against it. A bound, not a measurement; but a
  bound from a channel the archive was declared incapable of producing.

**2. The collisional self-shift: attempted, and vacuous.** The bridges
between temperature dwells carry the measured re-kick noise (~8 MHz
transition RMS) against a density span of ~4.4×10¹² cm⁻³, giving an
achievable shift error of ~1.8 MHz per 10¹² — about **1800× above** the
~1 kHz per 10¹² expected from the Zameroski 7S scaling. The channel exists;
its information content at this noise is nil.

**3. The isotope shift / hyperfine intervals: structurally absent.** Peak
separations are of GHz scale; the scan window is ~43 MHz; every peak change
was a retune of unlogged magnitude. There is no differential term to fit —
this is the one claim of the two-epoch framing that survives untouched.

The corrected summary of what the clock buys the centres: **within-window
differential structure is recoverable (the pull bound); across-window
structure is not** (shifts across temperature, intervals across peaks). The
blanket "centres are dead" stands only in its across-window sense.

*Post-hoc; extraction prompted by the experimenter, 2026-07-23.
`run_drift_settling.py`, final stage; closure documented here, not re-run in
the script.*


## Addendum 7, 2026-07-23 — the residual audit: the noise model was wrong, and it biased the drift

The experimenter asked the right closing question: *are the residuals
Gaussian, and should they be?* They were not, they should not have been, and
fixing the model revises the headline.

**The audit.** The standardized one-step innovations of the state-space fit
fail normality decisively (skew +1.9, excess kurtosis +7.0, Jarque–Bera
p ≈ 10⁻⁵⁴) — but the failure is *localized*: the 15 gap innovations pass
cleanly (Shapiro–Wilk p = 0.44; the exponential σ_gap layer is adequate),
while the within-block steps carry the tails, and the worst offenders all sit
in **25 mW end-of-ladder blocks** (v up to +5.0). Those are not statistical
outliers; they are the rare *real* mid-block touches the model gave no
channel to — so the filter absorbed them into the drift. The bias was live:
excluding the 25 mW blocks moved the Gaussian c from +0.74 to +0.25, outside
its own 68% interval. A Gaussian within-block random-walk cannot fix this
(it fits to exactly zero — a shared variance is the wrong shape for sparse
events).

**The adequate model.** Within-block transitions get sparse-move mixture
noise, η ~ (1−π_w)·δ(0) + π_w·N(0, σ_m²), evaluated by a collapsed
Gaussian-sum filter (exact two-branch likelihood per step, moment-matched
collapse). ΔAIC = +35.5 over the Gaussian; π_w = 0.078, σ_m ≈ 19 ms; the
mixture-PIT innovations **pass** (skew +0.3, excess kurtosis +0.7,
Shapiro–Wilk p = 0.27); the observation scale drops 1.93 → 1.14, vindicating
the block MADs; and the filter flags exactly three posterior-certain moves —
all at 25 mW ladder ends, the same events the diagnostics fingered.
Within-block moves were rare, as remembered: 3 events in 78 transitions.

**The revised numbers, superseding addendum 5's:**

- **Drift: c = +0.38 [+0.17, +0.59] ms/min (68%), [−0.07, +0.83] (95%)
  = +0.0163 [+0.0073, +0.0252] MHz/min laser.** A **~2σ positive
  indication, no longer a firm detection** — the Gaussian 3σ rested on the
  three moves. Robustness now holds: dropping the 25 mW blocks gives +0.25
  (inside the interval, where the Gaussian model broke), LOO-4207 +0.44.
  And the methods converge: the segmented floor (+0.19…+0.37), the clean-pair
  cluster (+0.55 ± 0.17) and the mixture (+0.17…+0.59) now agree within
  errors — the Gaussian state space was the outlier, for a diagnosed reason.
- **Structure unchanged**: the 2×2 re-run under the mixture still picks
  drift-constant × interventions-exponential (settling ΔAIC +16.7; adding
  drift settling +4.0 against; τ_i ≈ 91 min). The etalon-transient story is
  untouched.
- **Pull bound, re-profiled under the mixture: q = −0.050 [−0.190, +0.070]
  ms/mW (95%) → S₀(225 mW) < 5.5 MHz transition** — looser than addendum 6's
  3.5 (the mixture rightly discounts the 25 mW anchor points where the moves
  live), now ~8× above the width channel and ~9× above the prediction.
- Persistence extrapolation: ~20 MHz laser over the 20.5 h (was ~39).
  D0 margin: ~250× on the laser axis (was ~125×).

*Why the residuals should never have been Gaussian:* the within-block
population is a mixture by construction — a quantised jitter core (0.5 ms
grid) plus rare discrete operator events — and the gap population is
drop-and-recapture, Gaussian only by the generosity of σ_gap(t). The model
now says so.

*Post-hoc; audit prompted by the experimenter's question, 2026-07-23.
`run_drift_settling.py` carries the mixture stage as the headline; the
Gaussian number is kept, labelled as the biased intermediate it was.*


## Addendum 8, 2026-07-24 — a second source folder closes the last absence

The experimenter added a folder, `RawData2`, to the Desktop backup on the
evening of 2026-07-23 (after the main quarantine was frozen; it has its own
read-only quarantine copy, `RawData2_QUARANTINE_2026-07-24`, hash- and
mtime-verified). Six files, all at the one condition this report has chased
since addendum 2 — and they close it.

| file (RawData2) | mtime | identity |
|---|---|---|
| `4192nm_225mw2…5.csv` | 2025-07-17 23:47:42–23:48:02 JST | byte-identical to the repo's canonical block; acquisition mtimes match the audit exactly |
| `4192nm_225mw1copy.csv` | 2025-08-16 18:51 CEST | byte-identical to the main backup's degraded copy |
| `4192nm_225mw1.csv` | 2025-08-16 22:15 CEST | **a fourth variant, nowhere else — and the analysed repo copy is this file byte-for-byte after CRLF→LF** |

**The T1 audit's one genuine absence is resolved.** The analysed
`p_sweep/4192nm_225mw1.csv` — whose bytes the main backup never contained —
now has a complete, dated lineage:

1. **2025-07-17 23:47:38 JST** — pristine acquisition (53.8 kB, uniform time
   axis; preserved in the main backup — addendum 2's find).
2. **2025-08-16 18:51 CEST** — a degraded, headerless re-export
   (`…copy.csv`, 39.5 kB, time axis at reduced precision → the 799 duplicate
   timestamps). This is the degradation event, and it is post-campaign
   processing: the same evening as the stray `Julia.code-workspace` in the
   backup root.
3. **2025-08-16 22:15 CEST** — the `jj,nj` header restored (RawData2's
   unique file, CRLF line endings).
4. **≤ 2025-08-23 22:05 CEST** — CRLF→LF, and mass-copied into the analysis
   dataset: the repo's working-tree mtimes carry the bulk stamp
   2025-08-23 22:05:18 across `p_sweep/` and `t_sweep/` (rulers
   2025-10-05) — a bonus provenance fact: **the analysed dataset was
   assembled on 2025-08-23, rulers added 2025-10-05**, which dates the
   post-campaign analysis epoch itself.

Every byte in the analysed archive now has a documented ancestor and a date.
No number moves: addendum 2 already measured the degradation's effect by
substituting the pristine original (+0.07σ on the condition's γ_coll,
+0.03σ on the β_self slope), and the new file *is* the analysed bytes modulo
line endings — there is nothing to re-fit.

*Names in the table refer to RawData2 / its quarantine, identified by hash —
the standing collision warning applies. The main quarantine remains frozen
as found; RawData2 is quarantined separately because it surfaced after that
freeze.*


## Addendum 9, 2026-07-24 — the backup grows: a dated duplicate, the pilot, and the program's prehistory

Two more folders surfaced in the Desktop backup overnight (experimenter,
2026-07-23/24). One is closure, the other is a prequel.

**`2025-07-17/` is the main backup, reorganised**: 325 files, 325
content-identical to the frozen quarantine, zero new. It needs no quarantine
of its own; recorded here so nobody re-audits it.

**`2025-07-16/` is a pilot session nobody's documentation mentioned** — 53
files, every one content-unique against the archive, the main backup and
RawData2 (read-only copy: `RawDataPilot_QUARANTINE_2026-07-24`). In
campaign-local time it is the morning *before* the campaign, and its
timestamps read like a lab notebook:

| JST (2025-07-17) | what | files |
|---|---|---|
| 04:18–04:24 | EOM ruler, `Initial attempts` (`eom_n*`, `eom_hr*`) | 10 |
| 06:20–06:23 | ruler, adjusted (`*_adj`) | 7 |
| 06:27–06:33 | **ruler, `Def`** — the configuration is frozen | 10 |
| 06:54–07:11 | **pilot power sweep, 4192 nm @ 91 °C** (order 210→035→070→105 mW) | 26 |

The frequency ruler this whole analysis stands on was commissioned in about
two hours, and its definitive form was bracketing real data twenty-one
minutes later. The main campaign began 23:47 JST the same day.

**Quick QC on the 26 pilot science traces** (descriptive; nothing enters
`results/`):

| power | n | median SNR | FWHM | height |
|---|---|---|---|---|
| 035 mW | 8 | 61 | 60.5 ms | 0.124 V |
| 070 mW | 6 | 128 | 61.5 ms | 0.487 V |
| 105 mW | 6 | 161 | 61.0 ms | 1.064 V |
| 210 mW | 6 | 208 | 60.5 ms | 4.215 V |

Two echoes of the archival results, from data the archive never saw: the
**width is flat across a 6× power span** (the C3 power-null, in pilot form)
and sits at ~61 ms across a day and a re-preparation (which campaign dwell
that width actually corresponds to is settled in **addendum 17**: not the
90 °C one); and the **amplitudes follow P²** (×34 measured vs ×36
predicted over the full span). The pilot rulers were exported with a
different scope template (`x-axis,1,2`, two-channel) that the archive loader
does not read — a format fact, flagged for any future use.

**And then the excavation reached the program's prehistory** (folders
`2025-07-03` and `2025-07-04`, added the same night; read-only copy
`RawDataPrehistory_QUARANTINE_2026-07-24`, 54 files, all content-unique):

- **2025-07-04, 03:37–03:43 JST — the EOM ruler's first trials.** Four
  scans at 4192 nm / 80 °C / 0.80 A, verbose filenames
  (`EOM, 993.4192 [nm], T 80 [C], A 0.80 [A], normal 1`), thirteen days
  before the `Initial attempts` folder. The July-17 "commissioning" was the
  *final* commissioning.
- **2025-07-04→05, 22:31–01:38 JST — a fifty-trace dress rehearsal**: four
  peaks × 90/180/270 mW (ten of twelve cells, five repeats each) at
  `T=130C(90C-0.65A)`, gain annotated `G=10^6` — the only known record of
  the PMT gain, anywhere. **Taken on a LeCroy WaveSurfer 3104z** (native
  header `LECROYWS3104z`, 500 001-point segments, ~9.6 MB per trace,
  unreadable to the archive loader) — **not** the archive's Keysight: the
  LeCroy recollection that `APPARATUS.md` had to correct for the campaign
  was not confabulation, it was the rehearsal epoch, and both attributions
  now stand with instrument-native evidence.
- **An open notation question for the experimenter**: the rehearsal names
  carry a two-zone temperature, `130C(90C-0.65A)`, and the pilot's `650ma`
  matches the `0.65A`. If the parenthetical is a reservoir / cold-point
  setpoint, it is the first numeric record of the cell's two-zone thermal
  configuration — and the density systematic (`N(T)`, the β_self lever)
  cares which zone the campaign's quoted temperatures refer to.

The program's full arc, now dated: EOM first light (Jul 4, 03:37 JST) →
LeCroy dress rehearsal that evening → ruler finalisation + 91 °C pilot
(Jul 17 morning) → **the campaign** (Jul 17 23:47 → Jul 18 20:26 JST) →
analysis epoch (Aug 16 degradation event, Aug 23 assembly, Oct 5 rulers).
The frozen archive was take four.

**Standing**: pilot and prehistory are *outside the frozen archive* —
different days, different or partly different hardware, alignment not
guaranteed. They move no number. Their value is provenance (the ruler's
history, the gain record, the two-zone notation, the LeCroy closure),
corroboration (the pilot echoes the width-flatness and P² laws), and
candidacy for labelled exploratory use only — never silent inclusion.

*All identities by content hash. Quarantines: main (frozen 2026-07-23),
RawData2, Pilot, and Prehistory (2026-07-24), each read-only; the Desktop
originals untouched.*


## Addendum 10, 2026-07-24 — consolidation: the clock becomes data, the backup becomes an archive

The two-folder problem (a frozen repo archive with no clock; a private
backup that *is* the clock) is resolved in four moves, all shipped:

1. **The clock is committed as data.** `data_recovered/CLOCK.csv` — content
   hash → FAT mtime for all 438 backup files across the four source trees,
   with the manifest identity wherever content matches the archive. Built
   deterministically by `scripts/build_clock_table.py`;
   `run_drift_settling.py` now reads the table first, so **a clone
   reproduces the entire drift arc (addenda 4–7) with no private folder** —
   verified by running the full report with the quarantines hidden:
   identical numbers.
2. **The recovered files are published.** `data_recovered/discarded_backup/`
   (the 16 backup-only discards behind the curation test, addendum 3) and
   `data_recovered/lineage_4192nm_225mw1/` (the four variants of the dated
   degradation chain, addendum 8), all hash-suffixed against the nine name
   collisions, mapped in `RECOVERED_MANIFEST.csv`. `data_raw/` itself is
   untouched.
3. **The full timestamped backup is preserved publicly**: release
   `raw-backup-2026-07-24`
   carries the complete tree verbatim (`tar.gz`, mtimes intact — verified
   inside the archive; 753 CSVs, ~460 MB unpacked, 77 MB packed), sha256
   `58d5315d8bde5fae0c3c0989e5b96c76e24f02645d546791878ba650f9cc08d1`.
   *(Note, 2026-07-25: that release was published from the working repository,
   which also carried the raw traces. This public repository ships the
   analysis, the manifest and the results without the traces; the archive and
   its release are held privately and available on request. The hash above
   still identifies it. Nothing about the audit's findings changes — they were
   derived from the clock, which remains committed as `CLOCK.csv`.)*
   Anyone can now re-run the audit from first principles, hashing included;
   and the clock no longer lives on a single disk.
4. **The folder roles are documented** (`DATA.md` §3a) and guarded
   (`tests/test_recovered_layer.py`): the clock's manifest identities must
   agree with `MANIFEST.csv` by hash, campaign rows must sit inside the
   pre-registered T2 window, every recovered file must hash to its recorded
   and name-embedded md5 and be absent from the frozen archive, and every
   recovered file must be datable through the clock.

One count sharpened in passing: the RECOVERED_MANIFEST makes visible that
the two degraded copies of addendum 2 (`…copy.csv` and `… - Copy.csv`) are
byte-identical to *each other* — so the backup's "19 unique files" are 19
files carrying 18 distinct contents. No conclusion touched; the lineage is
three contents (pristine → degraded re-export ×2 names → header-restored
intermediate), all published.

The Desktop original and the four quarantines stay private, read-only, and
untouched — the provenance roots the public record can always be checked
against.


## Addendum 11, 2026-07-24 — the prehistory exploited: the clock validated in-file, the model tested out of sample

A second push from the experimenter, two days later, argued the new backup
data was still being underexploited — right again. The pilot and prehistory
sessions, useless for the frozen fits, turn out to carry checks the archive
cannot perform on itself (`scripts/run_epoch_checks.py`; nothing enters `results/`):

**1. The clock is validated by a second clock, inside the data.** The LeCroy
rehearsal files embed wall-clock trigger times. Across 47 files:
**mtime(JST) − TrigTime = +4…+9 s (median +6 s)** — the save-after-trigger
delay — with one +145 s operator pause. Every timestamp conclusion in
addenda 1–9 rested on interpreting FAT mtimes as JST; an independent,
instrument-written clock now confirms that reading to seconds.

**2. The etalon-transient model passes an out-of-sample test.** The pilot's
science ran ~2.9 h after its morning lock-on — past the ~2 h transient — so
the disturbance model predicts recapture steps at the settled scale
(≲20 ms). Measured, on a session the model never saw:
**+14.0, −5.8, +0.2 ms.** Pass. (The campaign's hour-1 steps, for contrast:
±20–70 ms, with two window moves in the hundreds.)

**3. The frequency calibration is coherent across days.** The pilot-day
`Def` rulers give an ACF comb period of **144.2 ± 1.1 ms vs the campaign's
146.81 ms — the sweep rate agrees to 1.7%** across a day and a
re-preparation. That is exactly the wander M2's design anticipates: every
block carries its own rulers because the rate is only per-cent-stable
between sessions (and 0.6%-stable within one).

**4. The pilot laws** (from addendum 9, restated as checks): width flat at
60.5–61.5 ms across a 6× power span — the power-null — and amplitudes ×34 vs
×36 predicted P². Both are *internal* ratios, so neither depends on what the
pilot's `91c` label means; the reading of that label given here — that the
width sits at the campaign's own 90 °C width — is corrected in **addendum
17**, which finds the pilot ran far hotter than 90 °C.

**5. One non-result.** The rehearsal's dual-scan captures (fast
dither over a 5 s slow sweep) yield an envelope-centre observable whose
within-block scatter is largest in the first block (649 ms) and settles
mid-session (17–131 ms) — consistent with a fresh-lock transient — but the
final peak's blocks are noisy again (~200–380 ms) and the observable rests
on an unverified trigger-sync assumption. **No claim either way**; recorded
so nobody mistakes the suggestive half for a result.

**Open questions for the experimenter, surfaced by the data:** the ~32 ms
satellite structure beside each `Def`-comb tooth; the identity of the pilot
rulers' second channel (a 1.92 V DC level, 0.65% wiggle — power monitor?);
the two-zone temperature notation `130C(90C-0.65A)` (which zone do the
campaign's quoted temperatures name?); and the three corrupt `4192…270mW`
rehearsal files (binary content under a `.csv` name).

*Post-hoc, exploratory, outside the frozen archive throughout. The
disturbance model now has one confirmed out-of-sample prediction and one
inconclusive one — stated in that order.*


### Postscript to addendum 11, 2026-07-24 — two of its open questions closed by analysis

**The "~32 ms satellites" were an artifact of the analysis, not the bench.** The
autocorrelation — which detects any coherent periodic companion — shows a
satellite-band excess of +0.006 (pilot `Def` combs) and +0.004 (campaign
rulers) against a comb-period bump of ~0.4: **no coherent satellite above
the few-percent level, in either epoch.** The consistent "pairs" the
peak-finder reported were the two shoulders of ~60 ms-wide teeth under a
3.5 ms smoother — tooth *width*, not tooth *structure*. The question is
withdrawn; the M2 calibration carries no satellite systematic.

**The three binary `4192…270 mW` rehearsal files are unrecoverable
non-data**: 8.6 MB of pure `0xFF` each — allocation placeholders whose
content never flushed to the FAT medium (a save failure, consistent with the
LeCroy's remembered unreliability that evening). Nothing misnamed, nothing
to parse; the block simply holds 2 real traces of 5, both TrigTime-stamped.

*Remaining from addendum 11's list: the pilot rulers' 1.92 V DC channel
identity — still open. The two-zone temperature notation, the one carrying
the density-systematic stakes, is resolved in addendum 15.*


## Addendum 12, 2026-07-24 — the re-kick, fitted: one transient, restarted by every re-lock

The experimenter's original proposal carried a clause the analysis had only
half-answered: *"one exponential for each temperature value."* Addendum 5's
postscript could report per-dwell RMS step sizes but not fit them — the
T-session baselines are short and the ruler→science spans are
operator-contaminated. What makes the fit possible is a physical constraint,
not more data: **τ is the etalon's thermal time constant — a property of the
laser, not of the cell temperature — so it can be shared across epochs while
each epoch carries its own amplitude.**

Fitted on all **26 gap steps** (16 P-session adjacent-ladder pairs + 10
T-session ruler→science steps), with each epoch's clock restarting at its own
start — and the 90 °C epoch starting at the **photographed 17:03 re-lock**,
not at its first acquisition. The excursion scale σ(t) enters as
step ~ N(0, σ(t)² + measurement²):

| model | k | AIC |
|---|---|---|
| constant | 1 | 301.0 |
| one decay on the session clock (addendum 5's) | 2 | 298.4 |
| per-epoch **level**, no decay — *the control* | 4 | 303.1 |
| **re-kick: one amplitude, shared τ** | **2** | **282.4** |
| re-kick: per-epoch amplitudes | 5 | 284.6 |
| re-kick: two exponentials | 7 | 288.6 |

**The re-kick is real, and it is the decay that carries it.** It beats the
session-clock decay by ΔAIC +16 and the per-epoch-level control by +21 — so
the gain is not "epochs differ" (that control is the *worst* model of the
six) but "each epoch restarts a decay". A second exponential adds nothing.

**And the re-kick is universal, not per-temperature.** The winning model has
a single amplitude:

> **B = 103 [78, 139] ms = 4.4 MHz laser, τ = 97 [87, 118] min**

Letting each epoch keep its own amplitude (P 105, 110 °C 40, 90 °C 211,
70 °C 69 ms) buys 1.9 in log-likelihood for 3 parameters — a likelihood-ratio
p = 0.29, **consistent with equal**, and the profiled intervals overlap
heavily. So the proposal's *shape* is confirmed and its *labelling* refined:
the transient is not keyed to temperature, it is keyed to **re-locking**, and
each dwell change happened to involve one. One thermal transient, one
amplitude, one time constant, restarted every time the lock was re-acquired —
which is exactly what an etalon settling to a new set point should do, and
why τ ≈ 97 min lands on the ~2 h the experimenter independently recalled and
the wavemeter photographs show.

*Post-hoc; the drift itself remains unresolved per temperature (T-session
baselines too short; intra-block bounds ≲5 ms/min per dwell). Model selection
by AIC on 26 steps with an ordinary Gaussian scale likelihood; the 90 °C
epoch start is the one anchored by a photograph rather than by an
acquisition, and the P-session epoch start is its first acquisition, not a
known lock-on — both approximations stated because τ inherits them.*


### Postscript to addendum 12 — a second timescale, tested and bounded

The experimenter proposed going further: two time constants — *"a time
constant for the whole campaign and a second one specific for each subset
between two re-kicks"* — the natural picture for two servo loops (cavity and
etalon) with different thermal scales. It is a different model from the
two-exponential one addendum 12 rejected: that put both decays on the
**epoch** clock; this puts one on the **campaign** clock.

**Residuals first.** The one-timescale fit leaves nothing obvious to chase:
standardized residuals have sd 1.07, Shapiro–Wilk p = 0.13, two |z| > 2 where
1.2 are expected, none above 3, and no correlation of |z| with either clock
(session r = +0.13, p = 0.5; epoch r = +0.25, p = 0.2). Per-epoch residual
scale runs 0.76–1.60 (the 90 °C dwell, n = 3, is the loose one).

**Then the models.** Two independent disturbance processes add in *variance*,
so σ²(t) = A²e^{−2t_session/τ_camp} + B²e^{−2t_epoch/τ_kick}. At n = 26,
**AICc** (small-sample corrected) is the right criterion:

| model | k | −lnL | AICc |
|---|---|---|---|
| **re-kick only** | **2** | **139.17** | **282.9** |
| campaign **floor** + re-kick | 3 | 139.17 | 285.4 |
| campaign **decay** + re-kick (quadrature) | 4 | 139.17 | 288.3 |
| re-kick, τ **per subset** | 5 | 137.76 | 288.5 |
| campaign decay + per-subset τ | 7 | 137.92 | 296.1 |

**The second timescale's amplitude fits to zero.** Not "small" — zero: the
log-likelihood is *identical* to the one-timescale fit (139.17 in all three
campaign-component variants; LRT p = 1.00). Freeing τ per subset buys
2Δln L = 2.83 on 3 dof (p = 0.42) and leaves the τ's unidentified (one runs
to 10¹² min, one goes negative). The data does not merely fail to support a
second process; its best fit contains none.

**So the useful deliverable is a bound**, which is what a null of this shape
should produce. Profiling the campaign-component amplitude at assumed slow
timescales:

| assumed τ_campaign | 95% upper bound on its amplitude |
|---|---|
| 1 h | 211 ms (9.0 MHz laser) |
| 3 h | 44 ms (1.9 MHz) |
| 6 h | 20 ms (0.9 MHz) |
| flat (∞) | 10 ms (0.4 MHz) |

*(Bounds as `run_drift_settling.py` computes them by bisecting the 1-dof 95%
edge; the exploratory grid scan that first produced them agreed to one
millisecond.)*

Read that as: a *genuinely slow* campaign-wide disturbance is excluded below
~1 MHz, while a would-be "campaign" component with a ~1 h timescale is not
excluded at all — because at 1 h it is degenerate with the re-kick itself
(τ_kick = 97 min), and the fit simply assigns the variance to whichever term
is offered. **The archive cannot separate two processes at the same
timescale**; it can only say that nothing slower than the re-kick is present
above the bounds above.

*A campaign designed to answer this would log lock-state transitions
(§8.7 etalon discipline): with re-locks time-stamped, the two clocks stop
being degenerate. Post-hoc as always; the one-timescale model of addendum 12
stands.*


## Addendum 13, 2026-07-25 — the detection chain's noise spectrum, and a mains line chased into the archive

The rehearsal captures buy something the archive cannot give itself: 500 001
points at 10 µs, so **0.2 Hz – 50 kHz** on the same PMT + pre-amplifier chain,
with the gain (G = 10⁶) recorded in the filename. The archive's own traces are
2 000 points over 1 s — Nyquist 1 kHz — so its noise model (M1) has never seen
above that.

**What the chain looks like** (median over six rehearsal baselines, line
regions masked):

| band | amplitude spectral density |
|---|---|
| 10–100 Hz | 63 µV/√Hz |
| 100–1 000 Hz | 54–56 µV/√Hz |
| 1–5 kHz | 41 µV/√Hz |
| 5–20 kHz | 35 µV/√Hz |
| 20–49 kHz | 26 µV/√Hz |

Broadly flat with a gentle fall — no filter pole inside the band, no
resonance, nothing that would alias a 2 kSa/s acquisition. But it carries
**discrete mains lines: 61 Hz at 14.6× the local floor**, with harmonics at
119 Hz (5.6×) and 180 Hz (6.0×). Sixty hertz is correct for Okinawa.

**So the obvious question: does it reach the archive?** A 60 Hz ripple has a
16.7 ms period, and the two-photon line is ~60 ms wide — about 3.6 cycles
across it — so it is exactly the kind of coherent baseline structure a
lineshape fit could absorb. Chasing it in 120 archive baselines:

- the mains line is present but weak **relative to the archive's own noise
  floor — 1.9×** (harmonics 1.1–1.3×), against 14.6× in the rehearsal;
- its amplitude is **~0.5–0.6 mV rms against a ~310–360 mV median line
  height: 0.15–0.2 % of peak** (the range is the estimator's sensitivity to
  the Welch window on a 1 s record, not a disagreement about the physics);
- and because ~3.6 whole cycles span the line, it **averages rather than
  displacing the centroid** — it cannot bias a centre, and at ~0.2 % it sits
  far below the width systematics that dominate every C1/C3 bound.

**Verdict: identified, quantified, negligible.** Nothing in `results/` moves.

> **Correction, 2026-07-25 (the day after this addendum was written).** The
> paragraph that stood here concluded that "the archive's chain suppressed
> the same line by nearly an order of magnitude" — and built a
> factor-8-grounding story on it. **That was wrong, and wrong in the
> flattering direction.** It compared each epoch's line to *its own* noise
> floor, and the two floors differ by ~4×, so the comparison measures
> broadband noise as much as pickup. Normalised properly:
>
> | | mains rms | signal height | line / signal |
> |---|---|---|---|
> | rehearsal (LeCroy) | 105 µV | 81 mV | **0.13 %** |
> | archive (Agilent) | 633 µV | 306 mV | **0.21 %** |
>
> In absolute terms the archive's mains line is **6× larger**, and
> signal-normalised — the measure that matters for lineshape distortion — it
> is **1.6× worse, not 8× better**. The substantive conclusion survives
> untouched (0.2 % of peak, whole cycles across the line, no centroid bias),
> but the epoch comparison is retracted. *Lesson, recorded because it is the
> kind of error that reads as a result: a ratio-to-own-floor is not a pickup
> measurement across chains with different floors.*

**For the next campaign** the diagnostic is still worth its one long capture
— but for the opposite reason to the one first written here. The mains line
is at ~0.2 % of peak in the *archive* chain, larger than in the rehearsal,
and it is the kind of coherent baseline structure that a narrower line (a
fixed-lock session's goal) would no longer average over.

*Exploratory, outside the frozen archive; the rehearsal traces are release-
asset data (addendum 10). Baseline masking is a 25 %-of-peak threshold;
Welch PSD, nperseg 2¹⁵ (rehearsal) and 512 (archive).*


## Addendum 14, 2026-07-25 — the last extraction: one test that does not port, one that does

The extraction list closes with the rehearsal's own power sweep — four peaks
at 90/180/270 mW, a third epoch for the C3 laws. One of the two checks turns
out to be impossible, and saying which is the point.

**The width test does not port, for a geometric reason.** The rehearsal
captures are *dual-scan*: a fast dither riding a 5 s slow sweep, so what a
trace shows is a fringe train under an envelope, not a swept line. Measuring
that envelope gives a median FWHM of **445 ms**, and at the photographed
SolsTiS setting (3.5 GHz over 5.00 s — the scan panel in
[`APPARATUS.md`](APPARATUS.md) §1.1) that is **≈ 310 MHz — about 120× the
~2.6 MHz laser-axis linewidth.** The envelope measures the dither excursion,
not the line. Any "width versus power" fitted to it would be a statement
about the modulation depth wearing a physics label; the per-peak slopes it
produces (+16, +78, −4 ms per e-fold, all p > 0.25) are reported here only to
be retired. **The archive's C3 width-null cannot be corroborated by this
epoch, and the pilot session — a genuine single-scan sweep — remains the one
independent check of it** (addendum 9: flat at 60.5–61.5 ms across a 6× span).

**The amplitude test does port, and holds.** Peak height is a rate
observable, and the two-photon P² law survives the scan geometry: log-log
slopes **+2.33, +1.87, +2.36** across the three peaks with a full ladder,
bracketing 2 and sitting inside the archive's own 1.83–2.12. Three epochs
now agree on it — archive, pilot (×34 measured vs ×36 predicted over a 6×
span), and rehearsal — on three different scan configurations and two
different oscilloscopes.

*One data note: the 4192 nm / 270 mW block contributes n = 2 rather than 5,
the three missing files being the 0xFF placeholders of addendum 11's
postscript; its envelope is the outlier that drives the +78 slope above,
which is a further reason that slope means nothing.*

*Exploratory, outside the frozen archive. With this the extraction list
opened in addendum 11 is closed: clock validation, out-of-sample transient
test, cross-day calibration, the discards, the noise spectrum, and now the
power laws — leaving only the two questions that need the experimenter.*


## Addendum 15, 2026-07-25 — the temperature notation resolved, and the cold spot given a first number

The last physics-relevant open question is answered by the experimenter
(2026-07-25), and answering it opens a bigger one.

**The notation.** In `130C(90C-0.65A)` the parenthetical is **not a second
cell temperature**: it is the **variac set point and current**, whose
thermocouple sat *on the aluminium foil on the outside of the oven*. The
campaign temperatures — the value outside the parentheses — come from **four
thermocouples inside the oven**. So the quoted temperatures are internal
readings, which is the favourable answer: they are cell-relevant, not heater
control points. *(Recollection, not a log; the experimenter adds that he does
not know how far to trust the thermocouples — which is the right instinct,
and testable.)*

**But an internal thermocouple is not the cold spot**, and the cold spot is
what sets the density. `rb5s6s/density.py` has always said so, and has always
said the offset was "unpinned by the archive". It is no longer entirely
unpinned. The two-photon line **area is proportional to N**, so if the
readings tracked the cold spot exactly, d ln(area) / d ln N(T_read) would be
**1**. Measured across the three dwells, per peak:

| peak | slope | | peak | slope |
|---|---|---|---|---|
| 993.4121 | +0.93 ± 0.17 | | 993.4192 | +1.25 ± 0.03 |
| 993.4154 | +1.18 ± 0.14 | | 993.4207 | +1.22 ± 0.06 |

**Mean +1.14, sem 0.07 — consistent with 1 at about 2σ.** Taken at face value
the excess prefers a cold spot running **~20 K below the readings** (the
offset that drives the slope to exactly 1.00), with roughly ±10 K from the
slope error alone. Read conservatively: **the thermocouples are not grossly
wrong — no runaway offset, no failure of the vapour-pressure law — and an
offset anywhere from 0 to ~30 K is not excluded.**

**Why this matters more than the ×1.2 already carried.** The density-scale
systematic in the error budget (20 %, from the spread between published
vapour-pressure correlations) does *not* cover a cold-spot offset, and the
offset's leverage is far larger, because β_self is a slope against N and an
offset **compresses the whole N lever arm**:

| cold-spot offset | β_self inflation |
|---|---|
| 5 K | ×1.4 |
| 10 K | ×1.9 |
| 20 K | ×3.6 |
| 30 K | ×7.4 |

The direction is the unfavourable one already named in `density.py`:
N_true < N_assumed means the fitted β **understates** the truth, so an upper
bound must be **loosened**, not tightened. At the face-value ~20 K the
headline model-independent bound would move from < 0.44 to roughly **< 1.6**
(MHz per 10¹² cm⁻³).

**Three things this is not.** It is not a measurement of the offset: the
same slope excess would be produced by **radiation trapping** of the detected
795 nm fluorescence at high density (which suppresses signal at 110 °C and
would imply an even *larger* true offset), by any power or alignment drift
across dwells acquired 54–76 minutes apart, or by the 30–50 % between-block
amplitude wander that dominates the per-peak scatter above. The archive
cannot separate these. It is not a correction to any published number —
nothing in [`results/`](../results/) moves, and the bound stays a bound. And
it is not new in kind: it quantifies a systematic the error budget already
named and deliberately left unpropagated.

**What it changes is the priority.** An in-situ density measurement was one
item among several on the fixed-lock session's list
([`PLAN.md`](PLAN.md) §8.0). It should be near the top: at ×1.4–×7 leverage
on the headline C1 number, the cold spot is plausibly a **larger systematic
than the beam waist**, and unlike w₀ it is cheap to bound — a thermocouple on
the coldest accessible glass, or a Rb absorption measurement on a weak probe,
in the same session.

*Post-hoc, exploratory; the t_sweep power column is empty in the manifest, so
this test assumes the three dwells ran at one power — true by design, but not
recorded per-trace.*


### Postscript to addendum 15, 2026-07-25 — the isotope route tested, and closed

Addendum 15 left the cold-spot offset degenerate with radiation trapping. An
apparent way out: a cold spot is a **density-scale** error, so it shifts both
isotopes identically, while trapping scales with the ground-state D1 absorber
column and must hit ⁸⁵Rb (72 % abundance) about 2.6× harder than ⁸⁷Rb. The
isotope *difference* in the log-log slope should therefore separate them.

**It does not, and the reason is worth recording.** The sign of that
difference is not robust to two ordinary analysis choices — whether the
130 °C point (a *different session*) is included, and whether the fit is
weighted:

| 130 °C included | weighted | ⁸⁵Rb | ⁸⁷Rb | ⁸⁵−⁸⁷ | reads as |
|---|---|---|---|---|---|
| yes | yes | 0.883 | 0.978 | **−0.095** | trapping |
| yes | no | 1.071 | 1.044 | +0.027 | not trapping |
| no | yes | 1.103 | 0.961 | +0.142 | not trapping |
| no | no | 1.185 | 1.062 | +0.123 | not trapping |

Three of four combinations give one answer and the fourth gives the
opposite, with the spread comparable to the effect. **The archive cannot
separate cold spot from trapping by this route**, and any single cut that
appears to is selecting an answer rather than measuring one.

Two consequences, both corrections to things stated earlier in this
repository:

1. **A claim made earlier today is withdrawn.** On first running the
   unweighted, 70–110 °C version of this test it looked as though the archive
   *weakly favoured* the cold-spot interpretation over trapping. It does not.
   That reading was an artifact of the cut.
2. **M7's trapping hint inherits the same caveat.** The ledger records ⁸⁵Rb
   as "0.09 ± 0.08 more sublinear … right sign, ~1σ". That is the top row
   above — true for M7's committed choice (weighted, 130 °C in), and reversed
   by dropping either. It is not evidence for trapping; it is one cut among
   four.

**What this leaves.** The cold-spot offset stays bounded only by addendum
15's 0–30 K, with its ×1.4–×7.4 leverage on β_self, and the archive has now
exhausted its own routes to narrowing it. That is not a failure of the
analysis — it is the correct answer to "can this dataset settle it", and it
is precisely why `PLAN.md` §8.0 item 3 (D-line absorption thermometry,
measuring N directly and returning ΔT_cs as the offset from the
vapour-pressure prediction) is the measurement that does, and item 4
(fluorescence-area ÷ absorption) the one that separates trapping cleanly.

*Post-hoc, exploratory. Computed from the committed `amplitude_trapping.csv`;
the four-way table is reproducible from it in a few lines.*


## Addendum 16, 2026-07-25 — the cold spot by maximum likelihood, where slope-fitting failed

The postscript above closed the isotope route: its sign flipped under ordinary
analysis choices. That failure was diagnostic rather than fatal — it is what
ad-hoc slope comparisons do when they discard information and make arbitrary
cuts. The experimenter's response was the right one: **fit it properly.**

**The model.** For peak $i$ at temperature $T$,

$$A_i(T) = C_i \cdot N(T-\Delta T_\text{cs}) \cdot \exp\big[-\kappa \cdot a_i \cdot N(T-\Delta T_\text{cs})\big]$$

with $C_i$ a per-peak normalisation (collection efficiency, matrix element,
power), $\Delta T_\text{cs}$ the **cold-spot offset shared by all peaks** — a
temperature error cannot be peak-specific — and $\kappa$ a trapping strength
also shared, multiplied by the *fixed* natural abundance $a_i$ (0.722 for
⁸⁵Rb, 0.278 for ⁸⁷Rb) rather than fitted per isotope. That is what makes the
two effects separable in principle: the offset slides the $N(T)$ curve while
trapping bends it, and the bend is isotope-weighted.

Two things make the fit behave where the slope tests did not. The four $C_i$
are **linear in log space**, so they are profiled analytically instead of
being handed to an optimiser — which turns a flaky 7-parameter search into a
stable 3-parameter one. And the error model carries a **fitted excess scatter**
$s$, because the quoted within-block errors (1.9 %) under-describe the actual
residual scatter about $A\propto N$ (24 %) by a factor of 12 — the documented
block-to-block amplitude wander. Fitting with the raw errors gives
$\chi^2/\text{dof}\approx 470$ and is meaningless.

**Result.**

| | 70–110 °C only (n = 12) | all four densities (n = 16) |
|---|---|---|
| $\Delta T_\text{cs}$ | **+19.6 K** | **+20.8 K** |
| 95 % profile | [+5, +24] K | [+6, +24] K |
| $\Delta T=0$ rejected at | 2$\Delta\ln L$ = 5.5, **2.3σ** | 6.3, **2.5σ** |
| fitted scatter $s$ | 18 % | — |
| trapping $\kappa$ | **not needed** (freeing it changes nothing) | same |

Three things are worth more than the central value. **It is stable across the
130 °C inclusion choice** — the exact choice that reversed the isotope test —
which is the first sign in this whole thread that a result is being measured
rather than selected. **Trapping is not required**: with $\kappa$
free the fit puts it at zero and the likelihood is unchanged, so the
amplitude-vs-density behaviour is explained by the temperature offset alone.
And it converts addendum 15's hand-waved 0–30 K into a profile interval with
zero disfavoured at ~2.4σ.

**What it does not license.** 2.4σ is an indication, not a detection. The
upper edge (+24 K) sits against the constraint that $T-\Delta T$ stay above
rubidium's melting point at the 70 °C dwell, so it is truncated by
physics-validity rather than determined by data. The escape factor is
phenomenological, not Holstein — a different trapping form could partly mimic
the offset. And this is the amplitude channel, which this repository treats
cautiously everywhere else for good reason.

**Consequence for C1, stated plainly.** At $\Delta T_\text{cs}\approx 20$ K
the density lever compresses by ×3.6, so the headline model-independent bound
would move from $\beta_\text{self} < 0.44$ to roughly **< 1.6** MHz per
10¹² cm⁻³. The bound is not restated here — a 2.4σ indication from a
systematics-dominated channel is not grounds to move a headline — but it is
now the largest identified systematic on C1, ahead of the beam waist, and
`PLAN.md` §8.0 item 3 (D-line absorption thermometry) measures it directly.

*Post-hoc, exploratory. Reproducible from the committed `amplitude_trapping.csv`;
the per-peak normalisations are profiled analytically and the excess scatter is
fitted, not assumed.*


### Postscript to addendum 16 — "cross-session" is the wrong word for the 130 °C point

Written while labelling the table above, and corrected by the experimenter:
*"I would not say 130 °C was a different session."* He is right, and the
recovered clock makes the point sharper than testimony alone could.

The 130 °C density point is the power sweep's 225 mW block. The four density
points, in acquisition order:

| | when (JST) | gap to the next |
|---|---|---|
| 130 °C (= 225 mW) | 17 Jul 23:47 → 18 Jul 04:21 | **2.3 h** |
| 110 °C dwell | 18 Jul 06:37 → 07:42 | **9.6 h** |
| 90 °C dwell | 18 Jul 17:21 → 18:16 | 0.7 h |
| 70 °C dwell | 18 Jul 19:00 → 20:17 | — |

**The 130 °C point sits 2.3 h from the 110 °C dwell, while the two halves of
the supposedly "same-session" 70/90/110 sweep are split by 9.6 h — the
documented break.** All four are inside one continuous ~24 h campaign with
the Ti:Sapph on throughout. If a temporal caveat belongs anywhere it is on
the 110↔90 boundary, not on 130.

The natural grouping by elapsed time is therefore **{130, 110} — break —
{90, 70}**, not {70, 90, 110} — {130}. And note what that implies for the
confound this report has worried about elsewhere: across the whole campaign
the density sequence is *monotone decreasing in time*, with the long break in
its middle.

**This language predates the clock and should be retired.** The phrase
"cross-session 130 °C" appears in `DATA.md`, `PLAN.md` and the generated
`RESULTS.md` (via `make_results_ledger.py`), where the 130 °C lever variant
is described as "far tighter but carrying its documented cross-session
caveat". The tightness is real and so is the caution — a 4½-hour block
acquired before a lock re-acquisition is not interchangeable with a one-hour
dwell — but the *reason* stated is wrong, and by elapsed time it applies more
forcefully to the 90 °C dwell than to 130 °C. Correcting that wording is a
separate pass, flagged here rather than done silently inside an addendum.

---

## Addendum 17, 2026-07-25 — the pilot ran hot: its oven label is a set point, not a reading

**The gap this closes.** Addendum 15 resolved the rehearsal's
`130C(90C-0.65A)`: the parenthetical is the **variac set point and current**,
the headline the **internal thermocouple**. That resolution was never carried
back to the *pilot*, whose science files are named
`4192nm91c650ma035mw1` — a temperature and a current, together. That is the
parenthetical's structure, not the campaign's: campaign filenames carry a
temperature and **no current at all** (`4192nm_090c1`). And the two match on
their face — the pilot's `650ma` is the rehearsal's `0.65A`, its `91c` the
rehearsal's `90C`. Every one of the 26 pilot science traces carries the pair;
all 50 rehearsal science traces carry `0.65A`; not one of the 297 campaign
traces carries a current token.

And the rehearsal session settles the *structure* of that pair by writing it
out in words. Its four EOM ruler files are named

> `EOM, 993.4192 [nm], T 80 [C], A 0.80 [A], high resolution 1`

— a temperature and a current, labelled and dimensioned, in the same session
whose science files compress the same pair to `(90C-0.65A)`. Three filename
families across two days therefore share one notation: *(temperature, heater
current)*, which is what addendum 15 concluded from the experimenter's
account alone. (These rulers sit at a different setting — 80 °C at 0.80 A —
and the pairing is not monotonic against the science point's 90 °C at 0.65 A.
Recorded as an oddity, not explained: a variac dial and the current it draws
need not move together while an oven is away from equilibrium, and these are
ruler captures whose place in the day is not established.)

If the pilot's label is a set point, the pilot did not run near the
campaign's 90 °C dwell at all. It ran at the setting the rehearsal itself
records as **internal 130 °C**.

**Why it is worth testing rather than asserting.** Filename archaeology
argued the notation once already and got a reader's-eye answer; the
experimenter corrected it. So the claim is put to two observables that do not
read filenames. Only the first is load-bearing.

**Test 1 — linewidth thermometry** (immune to gain, alignment and collection
efficiency, which is what makes it the load-bearing half). The pilot's own
day-rulers calibrate its sweep rate (144.2 ms comb tooth vs the campaign's
146.81 ms, check 3), so its widths convert to MHz without borrowing the
campaign's scale. Pooling the four power blocks — legitimate, because width
is power-independent, the C3 null — gives
**2.638 ± 0.010 (block) ± 0.045 (cross-day rate) MHz**:

| campaign dwell (internal) | 4192 width | pilot − dwell | |
|---|---|---|---|
| 70 °C | 2.373 MHz | +0.265 ± 0.064 | +4.1σ |
| 90 °C | 2.533 MHz | +0.105 ± 0.054 | +1.9σ |
| **110 °C** | **2.629 MHz** | **+0.010 ± 0.053** | **+0.2σ** |
| 130 °C | 2.693 MHz | −0.054 ± 0.047 | −1.2σ |

The pilot lands on the 110 °C dwell, is comfortably consistent with 130 °C,
and sits 1.9σ from the 90 °C dwell it was previously read against. The
dominant error is the 1.7% cross-day rate agreement, not counting statistics
— tightening this would need the pilot's rulers re-reduced, not more traces.

**Test 2 — amplitude** (a ×12 density lever, but it buys that leverage with
an assumption). Against the 130 °C power ladder, amplitude/P² is
**0.979 V for the pilot vs 0.764 V for the campaign — a factor 1.28**. A
pilot sitting at internal 90 °C would be a factor ~9 below what is measured.
That looks decisive and is not, quite: the pilot files carry no gain token,
and one decade of transimpedance gain (the rehearsal's own files record
`G=10^6`) would mimic most of the density ratio. The test is therefore
**corroborating, not independent** — it agrees, and it would also agree if
the gain happened to differ by a decade in the convenient direction.

**Verdict.** Three strands — the filename structure, a gain-free linewidth
thermometer, and a gain-dependent amplitude — agree that the pilot ran at the
rehearsal's oven setting, internal ~110–130 °C. The pilot's `91 °C` is a
variac set point, exactly as addendum 15 read the rehearsal's parenthetical.
The notation resolution now rests on physics as well as on filename
structure, which is a stronger footing than it had.

**What this changes.** Two sentences of addendum 11, corrected in place above:
the pilot width was described as "sitting at the campaign's own 90 °C width",
and it does not — it sits at the 110 °C one. **Nothing in `results/` moves.**
The pilot's two laws are the power-null and the P² amplitude scaling, and
both are ratios *within* the pilot, so both survive the relabelling
untouched; they were never claims about which dwell the pilot matched.

**What it does not settle.** The width thermometer reads the **kinetic
temperature of atoms in the beam**; the cold spot that sets *density* is a
different location, and addendum 16's maximum-likelihood offset
(ΔT ≈ +20 K, the vapour colder than the readings) is untouched by anything
here. The campaign's own width-versus-temperature rise (×1.135 from 70 to
130 °C) is steeper than pure transit scaling predicts (×1.084), so width is
not a clean thermometer in absolute terms either — it is used here only
*differentially*, pilot against campaign, where the extra broadening is
common to both.

**Recorded as a caution.** Addendum 11's error was not a bad measurement; it
was reading a number off the nearest label without checking that the two
labels meant the same thing. The pilot's 61 ms and the campaign's 59.5 ms
looked close enough to call a match, and in raw milliseconds the 110 °C
dwell (61.75 ms) was *already* the nearer neighbour. The check that caught it
is `scripts/run_epoch_checks.py` check 5, which now computes the comparison
against all four dwells rather than asserting one.
