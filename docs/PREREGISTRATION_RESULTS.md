# Timestamp-audit report (pre-registered)

*Scored 2026-07-23 by `scripts/run_timestamp_audit.py` at commit `2e56815`
(committed before first contact with the backup; predictions committed at
`0af038b`, 2026-07-22 — the release that also carried them was later
withdrawn for unrelated scope reasons, see the pre-registration's §9). Quarantine copy frozen with a
SHA-256+MD5+size+epoch manifest before scoring. One run; this file is its
unedited output plus this provenance header.*

*This file covers the timestamp audit and the dated addenda that followed it.
The later analyses carry their own pre-registrations of record, each written
before its code and each holding the amendments that record what the rules
returned: the frequency ruler's fit validity and residual-tail trimming
([`notes/ruler_validity_and_trim_prereg.md`](notes/ruler_validity_and_trim_prereg.md),
where amendments 4 to 7 govern the current tooth rules) and the full-archive
fit ([`notes/full_archive_fit_prereg.md`](notes/full_archive_fit_prereg.md)).
A reader who wants the current state of a ruler rule should go to the first of
those and read its opening table.*


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

**The audit voided.** Its own integrity gate, content identity between
archive and backup, failed at T1. That verdict stands unedited, and
everything after it is labelled **post-hoc**, with no pre-registered
standing. The gate did its job: it stopped a favourable-looking result from
being reported as a confirmed one.

**What the labelled post-hoc pass then established** (each reproducible from
a clone via `scripts/run_drift_settling.py`, off the committed
[`CLOCK.csv`](../data_recovered/CLOCK.csv)):

| finding | where |
|---|---|
| The recorded block order is **not** the acquisition order — the power ladder ran 225→25 mW | addendum 8 |
| The held-lock drift is **bounded at order 0.02 MHz/min** (laser axis), sign undetermined — the earlier "+0.016, one constant" reading did not survive the window-reference audit | addenda 4–7; retraction in addendum 4's postscript |
| The megahertz-scale motion was **not drift** but hand re-centring after lock dropouts | addendum 5 |
| That disturbance is **one transient re-armed by every re-lock**: B = 103 [78, 139] ms, τ = 97 [87, 118] min | addendum 12 |
| A **second, campaign-wide** timescale is absent, and bounded (< 0.4–1.9 MHz depending on assumed τ) | addendum 12 postscript |
| The ruler’s tooth indexing was unprotected against the retrace. 54 of 104 combs carried a one-slot mislabelling, corrected display-side on a ratio test. The recomputed calibration is byte-identical and the primary bounds stand. The 4207 nm separation prediction FAILED and stands as a measured campaign property | addendum 26 |
| The four peaks of each dwell were acquired **54–76 min apart**, so the σ_laser-sharing assumption was never "close in time" | addendum 12 / [RESULTS.md](RESULTS.md) C1 |
| The detection chain carries a **61 Hz mains line at ~0.2 % of peak** — averaged over by a 60 ms line, harmless here | addendum 13 |
| The **P² two-photon law** holds in a third epoch (slopes 1.87–2.36) | addendum 14 |
| The `130C(90C-0.65A)` notation is a **thermocouple reading and a variac set point**, giving the cold-spot offset its first handle | addendum 15 |
| The cold spot fits at **ΔT ≈ +20 K [+5, +24]** by maximum likelihood, with radiation trapping unneeded | addendum 16 |
| The pilot session's `91 °C` is a **set point, not a cell temperature** — it ran at the rehearsal's internal ~130 °C, not the campaign's 90 °C | addendum 17 |
| **One ratio predicts every result's status**: dynamic range over block noise — amplitude 45, widths 1.5–5.3, matching where the archive reports numbers vs bounds | addendum 18 |
| The archive's composite lineshape describes the **pilot out of sample** at χ²_red 0.83–1.01, and reproduces its γ_coll↔σ_laser degeneracy at corr −0.97 | addendum 17 postscript |
| The **frequency ruler fitted five comb teeth where there are seven**, biasing the sweep rate high by 0.104%. Corrected to 0.042526 MHz/ms and the whole pipeline re-run | addendum 19 |
| Two flagged wing anomalies were **one un-converged fit**: a single start left the amplitude at 20x the true chi2. Multi-started, both vanish and C3g's closure is a null at every temperature | addendum 20 |
| The fit gallery shows a **symmetric centre excess on the brightest lines** (1.4% of peak, 3.7 sigma on 993.4192 nm), absorbed by the noise inflation. Saturation, width sharing, hyperfine and pedestal all ruled out. Open, moves nothing | addendum 21 |
| The EOM comb's **tooth spacings are proved exact** (velocity symmetry from forward=retro spectrum; worst-case pull 10^-6 of the spacing). Companion: power-session rulers fail the amplitude model, so rulers stay unlicensed as shape data | addendum 22 |
| The vdW module's 1.67x-high 7S closure was a **double-applied HWHM-to-FWHM conversion**, one line. Corrected, it closes to 17% low, inside the truncation's own envelope. The 3.53 kHz beta_self(6S) anchor and the 8-15x archival-bound comparison are unaffected, the doubled prefactor cancels in their ratio | addendum 23 |
| The v3.2.0 light-shift bound 0.151 MHz was **basin-inflated 32%**: its profile chains inherited a cold start 3,401 units off the true minimum, and the four-point rerun's 283,135-unit direction row was a stuck chain, not physics. Seeded re-profiling gives the bound of record S0(225 mW) < 0.27 MHz, minimum at zero shift, direction indifferent at 10.5 units | addendum 24 |
| The 2025-06-11 wavemeter record is a **sawtooth**, not twelve relaxations. The old mean model left a non-white residual (lag-1 ACF 0.68, runs z = -6.3), moved 19.8 in likelihood across seeds, and gave four of its twelve kick amplitudes nothing to do. A free level and free ramp per inter-lock interval, with one shared 2.6 s rise at each re-lock, leaves runs z = -0.21 at RMS 0.66 MHz. The settled floor is 0.62 MHz, essentially where it was, and the record stays diagnostic | addendum 25 |

**What it corrected about itself.** Six readings were withdrawn after being
published here: a "~32 ms satellite" structure that was an artifact of the
analysis's own peak-finder (addendum 11 postscript); a width-versus-power
slope from the rehearsal, retired once the dual-scan geometry showed its
envelope is ~120× the linewidth (addendum 14); a mains-line "epoch
suppression" claim that compared each chain to its own noise floor and
inverted the conclusion (correction inside addendum 13); an isotope-abundance
route to separating the cold spot from radiation trapping, which reversed
sign across cuts (addendum 15 postscript); the phrase "cross-session" for the
130 °C block, which the recovered clock contradicts (addendum 16
postscript); and a linewidth thermometry test, withdrawn once refitting
showed a crude QC width had manufactured its entire resolving power
(addendum 17 postscript). The last is the one worth reading: it was
published, called load-bearing, and was a null.

**What none of it changed.** No number in [`results/`](../results/) moved.
Widths are per-trace and centre steps do not enter them. The clock
characterises the instrument, dates a design flaw (four peaks spread over an
hour) and specifies its remedy in [`PLAN.md`](PLAN.md). It does not
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
  - [Postscript to addendum 16, 2026-07-25 — the excess scatter, recovered without the model](#postscript-to-addendum-16-2026-07-25--the-excess-scatter-recovered-without-the-model)
- [Addendum 17, 2026-07-25 — the pilot ran hot: its oven label is a set point, not a reading](#addendum-17-2026-07-25--the-pilot-ran-hot-its-oven-label-is-a-set-point-not-a-reading)
  - [Postscript to addendum 17, 2026-07-25 — the linewidth test refitted, and withdrawn](#postscript-to-addendum-17-2026-07-25--the-linewidth-test-refitted-and-withdrawn)
- [Addendum 18, 2026-07-25 — one ratio that predicts every result's status](#addendum-18-2026-07-25--one-ratio-that-predicts-every-results-status)
- [Addendum 19, 2026-08-01 — the frequency ruler fitted five teeth where there are seven](#addendum-19-2026-08-01--the-frequency-ruler-fitted-five-teeth-where-there-are-seven)
- [Addendum 20, 2026-08-02 — two flagged anomalies were one un-converged fit](#addendum-20-2026-08-02--two-flagged-anomalies-were-one-un-converged-fit)
- [Addendum 21, 2026-08-02 — a centre excess the statistics absorb and the eye does not](#addendum-21-2026-08-02--a-centre-excess-the-statistics-absorb-and-the-eye-does-not)
- [Addendum 22, 2026-08-03 — the frequency axis gets its theoretical receipt](#addendum-22-2026-08-03--the-frequency-axis-gets-its-theoretical-receipt)
  - [Postscript to addendum 18 — the same lens on the power axis, and an assumption nobody had tested](#postscript-to-addendum-18--the-same-lens-on-the-power-axis-and-an-assumption-nobody-had-tested)
- [Addendum 23, 2026-08-03 — the 1.67x anomaly was a factor-of-two of our own](#addendum-23-2026-08-03--the-167x-anomaly-was-a-factor-of-two-of-our-own)
- [Addendum 24, 2026-08-03: the light-shift bound was reading a starting point, not the data](#addendum-24-2026-08-03-the-light-shift-bound-was-reading-a-starting-point-not-the-data)
- [Addendum 25, 2026-08-03: the wavemeter record is a sawtooth, not a sequence of relaxations](#addendum-25-2026-08-03-the-wavemeter-record-is-a-sawtooth-not-a-sequence-of-relaxations)
- [Addendum 26, 2026-08-05: the six-tooth defect, the recalibration, and the full recompute](#addendum-26-2026-08-05-the-six-tooth-defect-the-recalibration-and-the-full-recompute)

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

> ### Frame caveat, standing — applies to addenda 4, 5, 6 and 12 (2026-07-30)
>
> Every position in these addenda is `peak_pos_ms`, and the exported
> InfiniiVision time axis is **window-referenced**: moving the scope's horizontal
> position re-zeros it. That setting is now a per-trace qc metric
> (`window_start_ms`); it changed 58 times across the campaign, and
> `run_drift_settling.py` never reads it. Its ">100 ms repositioning" rule is a
> rule on the *position series*, not on the setting: of the 22 recorded moves
> among the 99 traces the state space sees, it frees **2**, absorbs 13 into
> σ_gap as if they were laser motion, and gives the remaining 9 within-block
> moves no channel at all.
>
> The scale of the exposure, measured: across the 16 adjacent-block steps of the
> power session, RMS Δ(peak position) = **145.2 ms** while RMS Δ(window setting)
> = **145.9 ms** and RMS Δ(difference) = **6.3 ms**. Thirteen of the sixteen gaps
> carry a knob move. So **99.8% of the between-block variance these addenda model
> as "intervention" is the horizontal setting.** And the five "step-like" blocks
> of the table below are *exactly*, one for one, the five blocks whose window
> setting changes mid-block — set equality, no exceptions.
>
> **Two readings are admissible and this archive cannot choose between them.** If
> the knob merely relabels the axis, then `rel = peak_pos_ms − window_start_ms`
> is the physical position and the raw-frame numbers are artifacts. If the
> operator moved the knob to follow a line that had moved, `rel` is drift-scrubbed
> by construction and the rel-frame numbers are nulls guaranteed by the
> estimator. The licensing statistic — Δ(position)/Δ(window) = 1.005 over 15
> within-block moves — does not decide it: 99.5% of its leverage is two moves
> larger than 800 ms, and the 13 small moves that the dispute actually concerns
> (median 16 ms) give 1.06 with a 95% interval of [0.75, 1.19], which contains
> the alternative. Both readings predict a ratio of 1 to within ~0.002, against a
> per-move scatter of 11.5 ms. The test has no power. Nothing decides it because
> the triangle ramp was on scope **CH1 and only CH2 was exported** — the omission
> now recorded as Tier-0 item 0 in [PLAN](PLAN.md) §3.
>
> **Therefore: no quantity below that depends on a between-block position
> difference is a single number.** Each is a band spanned by the two frames.
> Recomputed both ways (and again excluding the 10 blocks whose setting changes
> mid-block, which changes little because neighbouring blocks still differ):
>
> | quantity | raw frame | rel frame | status |
> |---|---|---|---|
> | within-block drift, early / late | −2.3 ± 1.1 / +1.2 ± 0.7 | −2.8 ± 0.7 / +1.2 ± 0.7 | **survives** — frame-invariant |
> | bound \|r\| at every epoch | < 4 ms/min | < 4 ms/min | **survives** |
> | step-like blocks, early vs late | 4/10 vs 1/10 | 1/10 vs 1/10 | **withdrawn** |
> | hour-1 apparent rate, max | 9.15 ms/min | 4.05 ms/min | band |
> | settling τ (joint fit) | 73 min, ΔAIC +196 | ~2 min, ΔAIC +22 | **unidentifiable** |
> | settled floor, pair median | +0.50 ± 0.60 | −0.28 ± 0.41 | **sign flips** |
> | settled floor, tight cluster | +0.55 ± 0.17 | −0.28 ± 0.16 | **sign flips** |
> | state-space drift c | +0.74 [+0.54, +0.94] | +0.24 [+0.14, +0.34] | band −0.03 … +0.74 |
> | mixture drift c | +0.38 [+0.17, +0.59] | +0.00 [−0.21, +0.21] | **straddles zero** |
> | intervention settling | ΔAIC +17.1 (exp wins) | ΔAIC −2.9 (const wins) | **flips** |
> | σ_gap amplitude | 88 ms | 2.9 ms | factor 30 |
> | re-kick B, τ | 103 ms, 97 min | level control wins | **flips** |
>
> What survives all four cells: the within-block bounds and their agreement with
> the photographed ±0.19 MHz/min cavity-locked figure; that adding drift settling
> buys nothing (ΔAIC +4.0 everywhere); the ≥125× margin against the 4 MHz/min
> envelope, stated as a bound; the identification of the two 4207 nm excursions
> as window travel rather than frequency; that a session-wide clock is the wrong
> clock for the disturbance (+10 to +17 AIC everywhere); and the T-epoch
> per-dwell step sizes, which get *larger* under subtraction and so are not knob
> artifacts.
>
> **The headline drift rate is the main casualty.** "+0.016 [+0.007, +0.025]
> MHz/min", and the claim at the end of this addendum that the settled floor is
> "a detection, not a bound … positive in every one", do not survive: two of the
> three estimators change sign. What remains is a **bound of order
> 0.02 MHz/min on the laser axis with the sign undetermined.**

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
25 min), the two 4207 scan-window repositionings (+564 ms and −1151 ms of window
travel — **not** frequency; quoted here as +24 and −49 MHz until 2026-07-30, which was the retracted arithmetic, M21), and
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
excursion returns *mid-block*) freed exactly. *Caveat added 2026-07-30:* the
horizontal setting is now known per trace (`window_start_ms`) and it moved **58**
times, of which only **19** exceed 100 ms. The other 39 — median 42 ms, RMS
36 ms, i.e. ~1.5–1.8 MHz of *apparent* laser-axis motion — are not freed, and are
absorbed into the very σ_gap ("~1–4 MHz laser in hour 1") this fit reports as
hand re-centring. The fit should be redone with a free offset at every recorded
move, not at a threshold. The marginal likelihood is then
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

> **§1 WITHDRAWN 2026-07-30 (M21).** The pull bound below — 3.5 MHz here, 5.4 MHz
> under addendum 7's mixture — is retracted. Its observation model has no free
> offset at a scope horizontal-position move, and the exported time axis is
> referenced to that setting, so differencing centres across a move differences
> two numbers measured against different zeros (see `run_laser_history.py`'s
> retraction: the setting changed 58 times, and only 19 of those exceed the
> >100 ms threshold this fit frees). Redone with a free offset per display epoch,
> the pull is **unidentifiable**: the sign flips between drift models and the
> limit degrades from 9.49 to 17.65 MHz as the drift gains freedom
> (`results/stark_centres.csv`, tagged NULL). These numbers were tighter than the
> defensible ones precisely because they borrowed that invalid leverage — a
> tighter bound is not a better one. §2 and §3 below are unaffected.

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
  < 5.4 MHz — the mixture discounts the 25 mW anchors where the moves live.)*
- **Injection closure**: a pull injected into the real positions at 1×, 4×
  and 10× the predicted size is recovered to ±0.0001 ms/mW. The estimator is
  unbiased; only the recapture-noise floor limits it.
- The width-channel archival bound (M4e, profile likelihood) is
  S₀(225) < 0.64 MHz — so the centre channel is **~5.5× looser**, and the
  first draft of this addendum quoted the superseded Wald diagnostic
  (3.1) beside it until the canonical-value gate caught the stale citation.
  The two channels **corroborate each other through disjoint systematics** —
  ramp broadening in the widths, centroid displacement in the centres. The
  centre floor sits ~10× above the 0.35 MHz prediction, where the width
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

The corrected summary of what the clock buys the centres — *revised 2026-07-30,
because the first version's only worked example was the pull bound and that is
withdrawn.* The unit of comparability is not the scan window but the **display
epoch**: a run of unchanged scope horizontal position, since the exported time
axis is referenced to that setting. Inside one epoch a centre difference is a
frequency difference; across a boundary it is not, and the setting moved 58
times. The archive's power ladder puts two powers inside one epoch in only 3 of
26 cases, so the pull joins the self-shift and the intervals as **not
recoverable**. The blanket "centres are dead" is restored, now for a measured
reason rather than an assumed one. What the clock does still buy is real and
smaller: chronology, the descending power order, and the within-epoch stability
(0.17 MHz peak-to-peak over 3.4 min in the quietest well-sampled epoch).

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
  ms/mW (95%) → S₀(225 mW) < 5.4 MHz transition** — WITHDRAWN 2026-07-30 for the
  reason given at addendum 6 §1 (no free offset at a horizontal-position move);
  it was looser than addendum 6's
  3.5 (the mixture rightly discounts the 25 mW anchor points where the moves
  live), now ~9× above the width channel and ~16× above the prediction.
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
  carry a double temperature notation, `130C(90C-0.65A)`, and the pilot's `650ma`
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
history, the gain record, the double-temperature notation, the LeCroy closure),
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
   [`raw-backup-2026-07-24`](https://github.com/MichelangeloDondi/Rb-5S-6S-analysis/releases/tag/raw-backup-2026-07-24)
   carries the complete tree verbatim (`tar.gz`, mtimes intact — verified
   inside the archive; 753 CSVs, ~460 MB unpacked, 77 MB packed), sha256
   `58d5315d8bde5fae0c3c0989e5b96c76e24f02645d546791878ba650f9cc08d1`.
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
the double-temperature notation `130C(90C-0.65A)` (which reading do the
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
identity — still open. The double-temperature notation, the one carrying
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
([`PLAN.md`](PLAN.md) §3). It should be near the top: at ×1.4–×7 leverage
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
is precisely why `PLAN.md` §8 item 3 (D-line absorption thermometry,
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
`PLAN.md` §8 item 3 (D-line absorption thermometry) measures it directly.

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

### Postscript to addendum 16, 2026-07-25 — the excess scatter, recovered without the model

Addendum 16's fit needed a **24% excess scatter** term to describe residuals
against quoted errors of ~2%, and that term is doing a lot of work: it is
what widens ΔT to [+5, +24] K. A fitted nuisance that large deserves a check
that does not come from the same seven-parameter optimisation.

Here is one. A cold spot is a **density** error, so it rescales all four
peaks *identically* at a given temperature. Normalise each peak to its own
70 °C point and the density cancels exactly — whatever the cold spot is, the
four columns must then agree. They do not:

| | 4121 | 4154 | 4192 | 4207 | spread |
|---|---|---|---|---|---|
| 90 °C | 1.32 | 1.68 | 1.45 | 1.23 | ×1.37 |
| 110 °C | 0.79 | 1.50 | 1.84 | 1.78 | ×2.35 |
| 130 °C | 0.93 | 1.30 | 1.31 | 1.65 | ×1.78 |

The scatter of ln(A/N) about each row's mean is **25%** — against the same
~2% quoted errors, and recovered with no model at all beyond "the density
cancels". That it lands on addendum 16's fitted 24% is the check passing:
the excess-scatter term was measuring something real, not absorbing a bad
fit.

**And it is not trapping.** Radiation trapping is a property of a *line*, so
it would rank the four peaks the same way at every density. The ranking
reshuffles instead — Kendall's W = 0.42 across the three temperatures,
Friedman χ² = 3.8 on 3 dof, no significant agreement. That is the eyeball
non-monotonicity argument of `run_amplitude_trapping.py` discriminator (3)
put on a statistic, now added there as discriminator (4), and it is the third
independent route to the same place: trapping is not what these amplitudes
are showing (addendum 15's postscript closed the isotope route; addendum 16
found trapping unneeded).

**What it is, most likely.** The t_sweep power was **never recorded** —
`power_mW` is empty for every t_sweep row — and amplitude goes as P², so a
12% power difference alone makes 25%. Add that the four peaks of a dwell were
acquired 54–76 minutes apart under a hand-re-centred lock and the size is
unremarkable. PLAN §7f pre-registered exactly this: cross-peak systematics of
**30–50%**, to be cut to 2–4% by per-trace power logging. The measurement
sits inside the band the plan predicted for it, which is the more useful
outcome than a surprise would have been.

**Net effect on addendum 16: none, and that is the point.** ΔT ≈ +20 K with a
[+5, +24] K interval stands, its dominant uncertainty independently confirmed
rather than assumed.

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
read filenames.

> **Corrected — see the postscript below.** Test 1 as first written used the
> crude QC FWHM and reported the pilot at +0.2σ from the 110 °C dwell and
> 1.9σ from the 90 °C one, calling it the load-bearing half. Refitting both
> sides with the archive's own composite model removes that discrimination
> entirely: the pilot is within 0.7σ of **every** dwell from 90 to 130 °C.
> **Test 1 is a null.** The table below is kept as the record of the claim
> that was made; the corrected numbers are in the postscript.

**Test 1 — linewidth thermometry** (immune to gain, alignment and collection
efficiency). The pilot's own day-rulers calibrate its sweep rate (144.2 ms
comb tooth vs the campaign's 146.81 ms, check 3), so its widths convert to
MHz without borrowing the campaign's scale. Pooling the four power blocks —
legitimate, because width is power-independent, the C3 null — gives
**2.638 ± 0.010 (block) ± 0.045 (cross-day rate) MHz**:

| campaign dwell (internal) | 4192 width | pilot − dwell | |
|---|---|---|---|
| 70 °C | 2.373 MHz | +0.265 ± 0.064 | +4.1σ |
| 90 °C | 2.533 MHz | +0.105 ± 0.054 | +1.9σ |
| 110 °C | 2.629 MHz | +0.010 ± 0.053 | +0.2σ |
| 130 °C | 2.693 MHz | −0.054 ± 0.047 | −1.2σ |

*(Superseded. Two errors: the widths are crude QC FWHMs, and the 1.7%
cross-day figure is the rate DIFFERENCE, which the pilot's own ruler already
removes — the term that actually dominates, block-to-block reproducibility,
was missing.)*

**Test 2 — amplitude** (a ×12 density lever, but it buys that leverage with
an assumption). Against the 130 °C power ladder, amplitude/P² is
**0.979 V for the pilot vs 0.764 V for the campaign — a factor 1.28**. A
pilot sitting at internal 90 °C would be a factor ~9 below what is measured.
That looks decisive and is not, quite: the pilot files carry no gain token,
and one decade of transimpedance gain (the rehearsal's own files record
`G=10^6`) would mimic most of the density ratio. The test is therefore
**corroborating, not independent** — it agrees, and it would also agree if
the gain happened to differ by a decade in the convenient direction.

**Verdict** (as corrected). **Two** strands, not three: the filename
structure, and an amplitude ratio that is gain-dependent but same-day. They
agree that the pilot ran at the rehearsal's oven setting, internal
~110–130 °C, and that its `91 °C` is a variac set point exactly as addendum
15 read the rehearsal's parenthetical. The linewidth neither supports nor
contradicts this — it has no power to tell these dwells apart, which the
postscript establishes and which is itself worth knowing.

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

---

### Postscript to addendum 17, 2026-07-25 — the linewidth test refitted, and withdrawn

Addendum 17 called its linewidth comparison the load-bearing half. Refitting
it properly withdraws that. The conclusion survives on its other two strands;
the width strand does not.

**What was wrong.** Two things, compounding.

*The metric.* Both sides used `trace_metrics`' crude half-maximum FWHM — a
descriptive QC number, not a fitted width. On the campaign's own 4192 ladder
the two disagree systematically:

| dwell | crude QC | fitted composite |
|---|---|---|
| 70 °C | 2.373 MHz | 5.069 MHz |
| 90 °C | 2.533 | 5.276 |
| 110 °C | 2.629 | 5.260 |
| 130 °C | 2.693 | 5.433 |
| **70 → 130 growth** | **×1.135** | **×1.072** |

The crude metric climbs nearly twice as fast, and it is not peculiar to this
peak — every peak shows it, the crude-to-fitted growth ratio running 1.04 to
1.18 with a mean of **1.061**:

| peak | crude growth | fitted growth | ratio |
|---|---|---|---|
| 4121 | ×1.250 | ×1.063 | 1.176 |
| 4154 | ×1.192 | ×1.143 | 1.044 |
| 4192 | ×1.135 | ×1.072 | 1.059 |
| 4207 | ×1.124 | ×1.084 | 1.037 |

**The mechanism runs the opposite way to the obvious guess.** One expects a
half-maximum crossing on a noisy trace to be biased *outward*. It is biased
*inward*: a positive noise excursion near the peak inflates the measured
maximum, which lifts the half-maximum level and cuts the width narrow. So the
crude estimator **under-reports, worst where the signal is weakest** — and
across all 32 campaign conditions the crude-to-fitted ratio correlates with
signal-to-noise at **+0.66** in log SNR, the low-SNR end running ~6% narrow.
The campaign's smallest amplitudes are at 70 °C, so the bottom of the ladder
is pulled down and the whole climb is exaggerated. It also explains the
concave curve (ΔFWHM² of +0.78, +0.49, +0.34 per 20 K, which the fitted
widths show no trace of): a depressed 70 °C point inflates the first
increment. **That manufactured steepness was the entire source of the test's
apparent resolving power.**

*The error budget.* The 1.7% quoted as the dominant systematic is the
cross-day rate *difference* — which is precisely what the pilot's own ruler
removes, so counting it again was double-counting. The term that genuinely
dominates was absent: block-to-block width reproducibility, measurable
because the 130 °C ladder holds temperature fixed across five power blocks
where width is power-independent. It is **1.9%**, and it does not average
down.

**The corrected test.** Fitting the pilot's four blocks with the same
composite model, on its own frequency axis, gives **5.318 ± 0.019 (block SE)
± 0.103 (reproducibility) MHz** — and the fitted `total_fwhm` is genuinely
robust to the split, moving under 0.01 MHz whether the transit is evaluated
at an assumed 90, 110 or 130 °C:

| campaign dwell | fitted width | pilot − dwell | |
|---|---|---|---|
| 70 °C | 5.069 MHz | +0.249 ± 0.162 | +1.5σ |
| 90 °C | 5.276 | +0.042 ± 0.156 | +0.3σ |
| 110 °C | 5.260 | +0.058 ± 0.150 | +0.4σ |
| 130 °C | 5.433 | −0.115 ± 0.157 | −0.7σ |

The pilot is consistent with **every** dwell from 90 to 130 °C. The fitted
ladder spans 3% across 60 K while a single block reproduces to 2%, so the
observable never had the resolution the crude version appeared to give it.
**Test 1 is a null: linewidth cannot identify which dwell the pilot matched.**

**What survives, and is worth more.** Three things.

*The conclusion.* It rests on the filename structure — three families across
two days sharing one *(temperature, current)* notation, against a campaign
that never records a current — and on the amplitude, ~15× above what an
internal-90 °C pilot would give. That amplitude argument is stronger than
addendum 17 allowed: the gain caveat was raised against a decade of
transimpedance, but the pilot ran on **the morning of the campaign's own
day** (06:54–07:11; the campaign began 23:47 JST), not weeks away, so an
unrecorded decade change between them is a good deal less likely than the
caveat implied.

*An out-of-sample model validation.* The pilot fits the archive's composite
lineshape at **χ²_red 0.83–1.01** across all four power blocks — data the
archive never saw, a different day, a different sweep rate, its own noise
model. The model was built on the campaign and it describes the pilot without
adjustment. That is a better result than the thermometry would have been.

*The degeneracy, demonstrated out of sample.* Having the pilot fitted makes
one more check free, and it is the sharpest of them. Across the pilot's four
power blocks the fit's two width components swing hard and in opposite
directions — γ_coll 0.428 → 0.489 while σ_laser 1.027 → 0.744 — at
**corr = −0.97**, while their combination holds to **0.7%**:

| | γ_coll | σ_laser | total |
|---|---|---|---|
| 35 mW | 0.428 | 1.027 | 5.320 |
| 70 mW | 0.423 | 1.175 | 5.371 |
| 105 mW | 0.483 | 0.796 | 5.295 |
| 210 mW | 0.489 | 0.744 | 5.286 |
| **spread** | **8%** | **22%** | **0.7%** |

The archive reports this degeneracy at corr = −0.85 over its own 32
conditions and reports `total_fwhm` because of it. The pilot reproduces it on
a different day, at a different sweep rate, without being asked to — and it
settles one loose end. After the width test failed, the tempting next move is
to read the pilot's γ_coll (0.43–0.49) against the campaign's ladder (0.201 /
0.300 / 0.301 / 0.469), where it lands squarely on 130 °C and looks like the
missing third strand. **It is not evidence.** γ_coll varies 8% across blocks
that differ only in power, at fixed density, purely by trading against
σ_laser. A parameter that moves that much at constant density cannot measure
density.

*A limit worth recording.* Linewidth cannot be an **absolute** thermometer
here at all, and not for want of precision. Transit width goes as √T, so in
the quadrature approximation FWHM² = A²(T + δ) + B² — which is linear in T
for any δ, leaving the temperature offset δ exactly degenerate with B², the
T-independent width. No width-versus-temperature curve can separate them.
This is why the comparison was posed differentially in the first place, and
it closes off reading a cold-spot offset out of the widths: that route is
shut by algebra, not by noise.

**Does this reach the archive's own results?** Two of them use the same raw
estimator deliberately, and the answer is that the bias helps rather than
hurts. `run_beta_self.py` and `run_power_sweep.py` both take
`contiguous_fwhm_ms` as a *model-independent* width, which is the point — a
bound argued from raw widths does not inherit the lineshape model's
assumptions. The C1 headline is that widths grow far too little with density
to be collisions (a residual floor, hence a bound). Since the estimator
**exaggerates** the climb with temperature, the true climb is smaller still:
the bias pushes against the archive's own conclusion, so the bound is
conservative with respect to it. The C3 power-null is likewise safe — power
varies SNR within a dwell, but the pilot's four power blocks are flat under
the *fitted* width too (5.320 / 5.371 / 5.295 / 5.286 MHz at 35–210 mW), so
the null survives the change of estimator out of sample.

**Net effect on the archive: none.** No `results/` value moves; the pilot
sits outside the frozen archive, and its two laws remain internal ratios.
What changes is one strand of one argument, and a lesson that generalises —
**QC metrics are for triage, not for physics.** `trace_metrics` exists to
flag bad traces, and it is good at that; the moment a number of its was
carried into a quantitative comparison it brought a 6% systematic with it.
Where the repo compares widths for physics it uses the fitted composite, and
this is now the reason why, written down.

---

## Addendum 18, 2026-07-25 — one ratio that predicts every result's status

The pilot investigation kept colliding with the same wall in different
disguises: a single-temperature session whose normalisation is degenerate
with density; a QC width carrying an SNR bias; γ_coll degenerate with
σ_laser; a width-versus-temperature curve whose offset is degenerate with its
constant. Four objects that look informative and are not.

They share a form. **An observable can only answer a question if it moves
more across the conditions of interest than it scatters when nothing physical
is changing.** Both halves of that are measurable here, so it can be computed
rather than reasoned about.

The dynamic range is the per-dwell mean over the 70–130 °C sweep. The noise
floor is the block-to-block scatter at *fixed* conditions, and the 130 °C
power ladder supplies it — five blocks at one temperature, where width is
power-independent by the C3 null, so whatever separates them is
instrumental. Both in log space, since these are multiplicative quantities;
mixing a log ratio for one against a fractional range for another is what
made the first version of this table wrong.

| observable | dynamic range | block noise | ratio | |
|---|---|---|---|---|
| amplitude | 4.23 | 9.4% | **45.1** | resolves it |
| `total_fwhm` | 0.09 | 1.6% | 5.3 | marginal |
| `gamma_coll` | 0.64 | 17.5% | 3.6 | marginal |
| `sigma_laser` | 0.47 | 30.3% | 1.5 | cannot resolve it |

**The ratio reproduces the archive's own status assignments.** Amplitude
clears its floor 45× and is the single place the archive extracts a *number* —
the cold spot, ΔT ≈ +20 K (addendum 16). The widths sit between 1.5 and 5.3
and are exactly where it reports *bounds*: β_self from `total_fwhm`, the
residual floor from `gamma_coll`, the laser width from `sigma_laser`. Those
four statuses were each argued separately, by monotonicity tests, degeneracy
analysis and model comparison. One ratio, computed from block scatter,
recovers all of them.

That is a consistency check on the archive rather than a new physical result,
and it is worth having for the same reason the closure tests are: the
statuses are the load-bearing part of a bounds-heavy paper, and they now have
a second, independent justification that does not go through any lineshape
model.

**What it is actually for is the fixed-lock session.** The diagnostic is
predictive, and it
says something PLAN did not. The prescription has two halves — hot points at
150–170 °C to grow the signal, interleaving and per-trace power logging to
cut the block noise — and the temperature half has always read as the
headline. Against the measured floor of 0.086 MHz on a 5.3 MHz line:

| | per-block significance |
|---|---|
| 2025 as taken (Δγ ≈ 20 kHz) | 0.2σ |
| hot points alone | 0.8–2.9σ |
| hot points **and** the noise cut 4× | 3.2–11.6σ |

**Hot points alone do not deliver a measurement.** They move β_self from
invisible to marginal. The noise half is co-limiting, not a refinement of the
temperature half, and `PLAN.md` §3 Tier 1 now says so with these numbers
attached.

The one caveat to carry: the 0.07–0.25 MHz signal is itself derived from a
bounded β_self, so the projection inherits that range rather than resolving
it. It brackets the outcome; it does not predict a single value.

Computed by `scripts/run_resolving_power.py` into
`results/resolving_power.csv` (DIAGNOSTIC — it measures the experiment's
sensitivity, not the atom); summarised in [`RESULTS.md`](RESULTS.md) M17.

---

### Postscript to addendum 18 — the same lens on the power axis, and an assumption nobody had tested

The density axis was the comfortable one: the ratio reproduced the archive's
own statuses and the projection sharpened PLAN. Turned on the **power** axis
the lens finds something less comfortable, and it sits underneath a headline.

**The setup.** The AC-Stark bound (M4e) fits one shared κ to the width-versus-
power data and inflates its errors by √χ² — χ²_red ≈ 4.3 — to absorb the
block-to-block width scatter. That is the correct remedy for *independent*
noise, which averages down so the parameter error shrinks as 1/√N. It is the
wrong remedy for a systematic **common to all four peaks at a given power**,
which does not average at all.

Ordinarily that distinction would be a technicality. Here it is not, because
of a coincidence: the predicted ramp broadening at 225 mW is **~0.09 MHz**,
and one single-block width scatter is **0.088 MHz**. The effect the bound is
built to constrain is exactly one block's worth of noise. Everything the
bound achieves, it achieves by averaging — so whether the scatter averages is
not a detail of the error budget, it *is* the error budget.

**The test.** Take each peak's residuals about its own power-mean and permute
them across powers, independently per peak. That destroys any common
per-power component while preserving each peak's own distribution — the
independence null. The statistic is how much the scatter shrinks when the
four peaks are averaged: 2.0× under independence, 1.0× if the scatter is
entirely common.

| | variance reduction |
|---|---|
| observed | **1.39×** |
| independence null (median, 90% band) | 1.89× [1.29, 4.04] |
| p(≤ observed \| independence) | **0.11** |

**The verdict is a shrug, and the shrug is the finding.** A common component
is not established — p = 0.11 clears nothing. It is equally **not excluded**:
the null's own 90% band runs from 1.29 to 4.04, so the statistic is wildly
uncertain, and the observed 1.39 sits comfortably inside it. Four peaks by
five powers cannot resolve this question. The point estimate of the common
variance fraction is 36%, which is worth exactly nothing given that band.

The eye is drawn to the 225 mW column, where all four residuals are negative
(mean −0.104 MHz, 2.3σ) — and a systematically *narrow* line at the highest
power is the opposite sign to ramp broadening, so it would mask the effect
rather than mimic it. That is the most extreme of five columns, though;
look-elsewhere makes it unremarkable, and it is recorded as a thing to watch,
not a thing found.

**So the assumption stands untested rather than contradicted**, which is a
weaker statement than the bound's presentation implies and a stronger one
than "it is broken". Nothing in `results/` moves: the bound is not shown to
be wrong, and there is no better estimate to replace it with.

**What it buys is a cheap fix.** The 2025 ladder walked the power monotonically
and never returned. Re-measuring **one earlier condition later in the same
session** separates common from independent scatter directly, because the two
make different predictions about a repeat at identical settings. One block.
`PLAN.md` §7 now carries it, and it is the cheapest item on that page.

**One correction to that argument, made after checking it.** The first
version of this claimed that *every* bound absorbing block scatter makes the
same assumption, so one block would test them all. Four modules do inflate
for over-dispersion — `beta`, `global_fit`, `ruler`, `stark` — but the
assumption is only load-bearing where the effect being constrained is
*comparable to* one block scatter, because that is the regime in which the
averaging is what produces the answer:

| result | effect it constrains | ÷ one block (0.088 MHz) | averaging load-bearing? |
|---|---|---|---|
| S₀ (M4e) | 0.09 MHz, predicted ramp at 225 mW | **1.0** | **yes — the answer *is* the averaging** |
| β_self (M4) | 0.02 MHz, Δγ over 70–130 °C | 0.23 | no — four times below one block, so a bound either way |
| rate (M2) | 0.6% block scatter on a quantity known to 0.12% | — | no — nowhere near a decision boundary |

So it is **one** result that hangs on this, not all of them. β_self's status
does not move whichever way the question falls, though the *tightness* of its
bound still rides on the same averaging — and `beta.py` already carries an
explicit coverage correction for estimating that scatter on n − 2 degrees of
freedom, so it was not taken for granted there. The returned-to block is
still worth one block of beam time; the case for it is narrower than
the case first written here.

---

## Addendum 19, 2026-08-01 — the frequency ruler fitted five teeth where there are seven

**What happened.** `rb5s6s/ruler.py` modelled the EOM comb with five teeth,
orders $-2$ to $+2$, in all three places that touch tooth positions. The comb
runs to $\pm3$. The experimenter said so directly, and the traces agree.

**Why a truncation moves a spacing.** The sixth and seventh teeth sit just
outside the fitted set. Their tails still fall inside the fitting window, and
a five-tooth model has only one way to absorb signal it cannot name, which is
to push its outermost teeth outward. That makes the fitted spacing $\Delta$
too small, and since the rate is $\Omega/2\Delta$, it makes the rate too high.

**The measurement.** The same 24 ruler traces, refitted both ways on the raw
millisecond axis, before anything downstream was touched:

| tooth count | $\Delta$ | rate (laser axis) |
|---|---|---|
| five | 146.804 ms | 0.042574 MHz/ms |
| seven | 146.970 ms | 0.042526 MHz/ms |

The five-tooth number reproduces the committed 0.04257061 to 0.008%, which is
what identifies truncation as the cause rather than a difference in method.
Re-running M2 in full gives **0.04257061 → 0.04252649 MHz/ms, a $-0.104$%
shift**, and it is carried by every frequency this analysis quotes.

**How large is that.** About one standard error of the rate itself, and small
next to the beam waist. It matters because it is one-directional. Scatter
averages away across blocks and a bias does not, so it is corrected in the
code rather than carried in an error bar.

**How it surfaced.** Not from the ruler at all. The M25 global fit models the
ruler traces as combs, and with five teeth its collisional width railed at
exactly zero on all four peaks. A parameter pinned at a bound is a symptom
rather than a result, and following it back found the truncation. The same
fit with seven teeth returns physical widths.

**What was checked and not changed.** The EOM drive frequency is untouched:
$\Omega = 12.5$ MHz is a hardware certificate, and the tooth spacing measured
in frequency units still agrees with it to 0.1 to 0.5% across peaks. The
comb's own uniformity was tested by fitting the spacing free rather than
assuming it, and it is uniform. An earlier reading of these traces claimed a
retrace fold, which was an artifact of a threshold peak finder run at 3% on
unsmoothed data and is withdrawn.

**Status of everything downstream.** Every fitted number in the repository
rides on this rate, so the whole pipeline was re-run from `run_ruler` forward
rather than patched. Numbers shift by of order 0.1%, which is well inside
every quoted systematic and changes no conclusion, but the values in the
committed CSVs are the corrected ones from this date.

---

## Addendum 20, 2026-08-02 — two flagged anomalies were one un-converged fit

**What was reported.** The wing check (M24) carried two single-condition
anomalies it could not explain: a red-side wing fraction of 0.139 at
993.4192 nm / 110 °C, flagged on 2026-07-31, and 0.185 at 993.4207 nm /
130 °C, flagged the next day. Both were recorded rather than smoothed over,
and both were left standing as open items.

**The tell.** Each moved when something unrelated to it changed. The first
appeared after the beam-waist reprior. The second appeared after a 0.2%
change in the sweep rate, and in the same step the first vanished. A
quantity that responds to an input it does not depend on has not measured
anything.

**What it was.** The wing amplitude was started at zero and fitted once. On
the brightest conditions that start converges to a second, far worse local
minimum. Refitting 993.4207 nm / 130 °C from five starts, on identical data:

| start | fitted $f_w$ | $\chi^2$ |
|---|---|---|
| 0.00 | 0.194 | 30845 |
| 0.02 | 0.198 | 30756 |
| 0.10 | **0.000** | **1577** |
| 0.20 | 0.000 | 1577 |
| 0.40 | 0.000 | 1577 |

The committed value sat at twenty times the $\chi^2$ of the true optimum. It
was not a marginal preference between comparable fits, it was a failure to
converge, and it landed at exactly the density lever the C3g closure rests
on.

**The fix and its effect.** `fit_wing` now starts from a spread of
amplitudes and keeps the lowest $\chi^2$. Both anomalies disappear, and the
closure is a null at every temperature: the red-minus-blue asymmetry at
130 °C is $-0.0007 \pm 0.0013$ of peak, and no temperature exceeds 0.7σ.
C3g's conclusion is unchanged. What changed is that it no longer rests on a
number that a different starting guess would have moved.

**The general lesson, which is why this is an addendum and not a commit
message.** A bounded least-squares fit of an amplitude that can trade
against the core is not safe from one start at high signal-to-noise.
The failure is silent: the fitter returns, the error bar is small, and the
result reads as a detection. Two rounds of this report treated the output as
a physical anomaly worth flagging before anyone asked whether the fit had
converged. Check convergence before interpreting an outlier, and treat
sensitivity to an irrelevant input as evidence of a numerical problem rather
than a subtle physical one.

## Addendum 21, 2026-08-02 — a centre excess the statistics absorb and the eye does not

**What was seen.** The new fit-quality gallery (fig16) draws the global
archive model at its committed optimum over the brightest 225 mW / 130 °C
trace of each line, with residual panels. On 993.4192 nm the residuals show
a symmetric excess at line centre reaching 1.4% of peak (3.7σ against the
per-point noise), with negative shoulders near ±1–3 MHz. Three of the four
lines show the same signature at smaller amplitude, growing with peak
brightness. Every reduced χ² in the gallery is below 1, so the archive's
conservative noise inflation absorbs the structure entirely. The eye sees
what the statistics forgive.

**What it is not.** Four candidates were tested and each fails
quantitatively. Saturation mismodelling predicts a correction two orders of
magnitude below the observed excess at the recorded V_sat. A free extra
Lorentzian width is pulled by up to −127 kHz (4.2σ on 993.4192 nm) yet does
not remove the bump, so it is not a mis-shared width. A second hyperfine
component is closed by the selection rules this archive documents: for
J=1/2 to J=1/2 with identical photons only ΔF=0 survives, and the nearest
allowed neighbour sits 717–1615 MHz away against a fit window of ±25 MHz.
The co-propagating Doppler pedestal is GHz-wide and would surface in the
wings, which are clean. Separately, the antisymmetric near-centre structure
in the same panels was closed as shot noise: its fraction falls as
amplitude^-0.5 along both the power axis and the temperature axis, the
Poisson exponent, matching the committed residual-skew scaling of C3g.

**Why nothing moves.** The excess sits below the inflated noise at every
condition, biases neither the fitted widths nor the centres at the quoted
precision, and lies far under the Stark bounds of C3d and C3f. No committed
number depends on its resolution.

**Status and lesson.** Open and unattributed, the only such feature in the
gallery. The measured-prior refit and the fixed-lock session should both
look at it with fresh data. The lesson is the inverse of addendum 20's:
there a confident number hid a failure to converge, here a comfortable χ²
hides visible structure. Conservative error inflation buys robustness and
costs sensitivity, and a residual panel is the check the inflated
statistics cannot perform. The gallery stays in the pipeline so every
future fit faces it.

**Postscript, same day.** Freeing the Gaussian width per trace, multi-started
per addendum 20's lesson, halves the excess on the two affected lines
(993.4192 nm: a −287 ± 197 kHz pull at 4.6σ takes the excess from 1.45% to
0.83% of peak; 993.4154 nm similarly) and leaves the other two lines
unpulled. So the shared width is part of the artifact and not all of it.
Polarization admixture is closed on sign and size: the scalar operator makes
it rate-only at zero field, and the ambient-field Zeeman spread is of order
1 kHz, two orders too small, in the broadening direction besides. Residual
Doppler from retro overlap has the right sign and a credible size, the
kHz pulls imply 0.5–1.3 mrad of misalignment, but no timestamped alignment
record exists to test the epoch fingerprint, so it stays plausible rather
than confirmed. Two consequences are booked: the next joint refit fits the
Gaussian width per session and peak with a shrinkage prior instead of
pooling per temperature, and the fixed-lock session logs every retro
realignment with a timestamp, which is the record this test needed and the
archive does not have.

**Second postscript, same day.** Three more candidates were tested and each
misses cleanly. The archive's own slow-transit tail predicts a centre
residual of −0.0025% of peak, negative where the excess is positive and
30–300× too small, flat from 70 to 130 °C. EOM sideband leakage shows no
coherent structure at ±6.25 or ±12.5 MHz, all sixteen peak-offset points
below 1.4σ with incoherent signs, bounded under 0.4% of peak, and the ruler
rate's immunity to any such leak was verified in the code rather than
asserted. The time-resolved sweep-rate correction moves the excess by less
than its error bar in either direction. The unexplained half has now
survived a twelve-candidate elimination, every branch closed with a number,
and it stays exactly as stated above: open, below the inflation, moving
nothing. The fixed-lock session inherits it as a target, not a debt.

**Third postscript, 2026-08-03.** The per-(session, peak) sigma_laser layer
recommended above ran inside the full joint refit, each cell pulled toward
its block's pooled mean by the 150 kHz shrinkage prior. At camp130, the only
block the free-width probe had resolved, the refit reproduces the probe's
ordering exactly: 993.4121 nm pulls −14 kHz, 993.4154 nm −36 kHz, 993.4192 nm
−57 kHz, and 993.4207 nm +107 kHz, against the probe's unshrunk −287 kHz
pull on 993.4192 nm. The shrinkage prior moderates the amplitude as
designed, trading the probe's free-per-trace deviation for a value
disciplined by its block's mean. The attributed half of the excess is
confirmed structural. The unattributed remainder stands exactly as stated
above, open, below the inflated noise, and moving nothing.

## Addendum 22, 2026-08-03 — the frequency axis gets its theoretical receipt

**What was asked.** Every number in this archive rides on one assumption:
that the EOM comb's tooth spacings equal the modulation frequency exactly,
so the fitted spacing calibrates the sweep rate (M2). The teeth of a
phase-modulated standing wave are not simple copies of the line: the tooth
at offset n is fed by every counter-propagating sideband pair (k, m) with
k + m = n, the pathways are phase-coherent, and interference could in
principle pull tooth centroids differentially, which would bias the rate
and with it the whole axis. The assumption had never been derived.

**What the derivation shows.** The coherent pathway sum collapses by the
Bessel addition theorem to tooth amplitudes proportional to J_n(2beta)
squared. The centroid question closes on a symmetry: relabeling k to n-k
leaves each pathway weight unchanged (the sideband products commute) while
flipping the sign of the Doppler term, so every tooth's profile is exactly
symmetric in atomic velocity. The only ingredient is that the retro beam
carries the same sideband spectrum as the forward beam, which the
single-pass EOM followed by the retro mirror guarantees by construction.
Tooth spacings are exactly the modulation frequency.

**The numbers.** Feeding the measured sideband asymmetry into a worst-case
pull estimate gives 1 to 6 parts in 10^6 of the 6.25 MHz spacing, three to
four orders below the 0.1% level that would matter against the committed
rate. Residual first-order Doppler broadening for unequal pairs is about
11 Hz per unit of |k - m|, at most about 65 Hz against a 2.38 MHz tooth
width. One caveat stays open: amplitude modulation residuals on the EOM
drive would modulate the light shift itself, a different mechanism the
symmetry does not cover, listed as unquantified.

**A companion finding.** The same derivation was tested against the
measured tooth amplitude ratios. The temperature-session rulers fit
reasonably. The power-session bracket rulers do not fit at all, consistent
with the plan's own record that their light path differed from the science
light. The consequence is a refusal: ruler traces are not licensed as
lineshape data for now, because their model demonstrably does not close on
the power-session population, and a width extracted from a wrong model
would be a fabricated number. The axis calibration is untouched by this,
it needs only the spacings, which the symmetry protects.

**Status and lesson.** The axis assumption is now a proved property, not a
habit. The lesson is the same one this report keeps learning from both
directions: the difference between an assumption that has always worked
and a property that has been derived is one afternoon of algebra, and the
derivation also told us, for free, exactly which reuse of the same data is
not allowed.

## Addendum 23, 2026-08-03 — the 1.67x anomaly was a factor-of-two of our own

**What was suspected.** M18 (`rb5s6s/vanderwaals.py`) computes a van der
Waals beta_self for the 5S+6S asymptote and checks the machinery against
the one nS state with a measured self-broadening rate, Zameroski's 7S
number. The check had been failing by 1.67x, high, for longer than it
should have gone unresolved. The module's own docstring already named a
suspect: the Lindholm-Foley impact prefactor is quoted from the
pressure-broadening literature, not derived, and its HWHM/FWHM convention
was flagged as the most likely place for an error of that size to hide.

**What the audit traced.** A same-day audit (`private/reviews/digest/vdw_convention_audit.md`)
walked the chain end to end: the C6 integral, Lewis 1980's eq. (4.16)-(4.17)
cross-section prefactor (independently recomputed at 4.0414, matching
Lewis's own quoted 4.04 to four digits), and eq. (4.18)'s velocity-averaged
width. Lewis's own text calls that width a half-width, and Table 4.1's
width-to-shift ratio is written 2*gamma/beta, a leading 2 that is only
needed when gamma is a HWHM to begin with. The convention as written in
the module docstring was correct throughout.

**The double-count.** The bug was in applying the convention, not in
stating it. `LINDHOLM_FOLEY_PREFACTOR = 8.16` is not the bare eq. (4.17)
HWHM prefactor (4.04) but 2x that value (2 x 4.0414 = 8.083, matching 8.16
to 0.9%, ordinary literature rounding). The constant was already a FWHM
angular prefactor. `beta_self_vdw`'s return line then applied a second
factor of 2 on top of it, converting angular to ordinary units with
`hwhm_ang / (2*pi) * 2.0` when the trailing `* 2.0` had nothing left to
do. The HWHM to FWHM step was counted once inside the constant and once
again in the return statement.

**The corrected closure.** Removing the redundant `* 2.0` moves the 7S
prediction from 8.99 kHz per 1e12 cm^-3 to 4.50 kHz, against Zameroski's
measured 5.39. The mismatch flips from 67% high to 17% low, and the 17%
now sits close to (a bit past) the +-10-15% envelope the dropped
core/tail and the mean-speed-vs-full-Boltzmann-average approximation
already predict. What had read as an unexplained 1.67x anomaly closes
into an expected, small, low-side gap.

**What is unaffected, and why.** `beta_self_anchored` never used
`beta_self_vdw` for its headline number. It takes the absolute scale from
Zameroski's measurement and uses this module only for the ratio
C6(6S)/C6(7S) = 0.347, so beta_self(6S) = 3.53 +- 0.30 kHz per 1e12 cm^-3
is unchanged before and after the fix (verified directly: 3.5280870 kHz
both ways). The archival bound sitting 8-15x above that anchor is
likewise untouched, because the doubled prefactor cancels in the ratio
regardless of whether it is right or wrong. Both numbers were checked
against the running code as part of this fix, not assumed from the audit.

**Status and lesson.** A convention that the module's own docstring had
flagged as a live suspect was traced and fixed within a day of being
named. The fix touched one line, `rb5s6s/vanderwaals.py` line 190, plus
the comments and prose that had described the bug's symptom as a physical
discrepancy rather than a bookkeeping one. Nothing downstream of the
ratio-anchored numbers moved. The anomaly did not get explained away, it
dissolved into agreement.

## Addendum 24, 2026-08-03: the light-shift bound was reading a starting point, not the data

**What v3.2.0 shipped.** The joint three-session Stark fit (M23,
`scripts/run_stark_joint.py`) quoted S_0(225 mW) < 0.151 MHz. That number
is now retracted. It was not measuring the data alone. It was partly
measuring where its own optimiser started.

**How the fault surfaced.** The four-point refit was run with the
rehearsal direction check re-armed, and its robustness row came back at
283,135 units of chi square. That row is the largest gap between the
primary profile and the flipped-direction profile across the kappa grid.
No direction convention can cost a quarter of a million units on 247,783
points. The row was not comparing two directions. It was comparing a
stuck fit against a converged one.

**What the chains actually do.** Each profile family runs a cold forward
chain from the same default starting vector, a backward chain seeded from
the forward chain's last point, and, where a seed is supplied, a third
chain from that seed. The pointwise minimum of those chains is the
profile. For the primary layout, which carries the collision priors and
no red-wing nuisance, the cold start parked in a local minimum and stayed
there for the whole chain, forward and backward: 469,570.98 at kappa = 0
going up, 469,510.09 coming back down. The wing variant, which has two
more free parameters, escaped from the identical cold start and settled
at 186,370.45. The extra freedom opens a path out that the tighter layout
does not have.

**The measurement that proves it is a basin and not physics.** Seeding
the primary layout from the wing solution, with the two wing entries
deleted so the vector fits the narrower layout, reaches 186,370.03 at
kappa = 0. Same data, same priors, same objective, same number of free
parameters as the stuck chain, 283,140 units lower. A fit cannot disagree
with itself by that much for any physical reason.

**Where the excess is not.** The run writes a campaign-only chi square
alongside the total. Between the stuck solution and the true one it moves
from 31,485.43 to 31,477.36, eight units out of 283,140. Whatever the
cold chain was doing wrong, it was not doing it to the campaign traces.
That is consistent with the rehearsal free centres, the parking spot the
fitter's own docstring documents from an earlier run, though the gap has
not been formally decomposed session by session and this record does not
claim it has.

**The structural fix.** The wing variant now runs first, because a cold
start finds the true basin reliably there, and every other family is
seeded: the primary from the wing solution with the wing entries deleted,
the flipped direction from the converged primary, the flipped wing
variant from the wing solution. Each seeded chain runs in addition to the
cold ones and the pointwise minimum is kept, so a seed can only improve a
profile, never inflate one. The rule is recorded in RESEARCH_DECISIONS
section 11 and methods 06 section 4.12: no cold-start profile is quoted
without a seeded twin. A profile is only as good as its basin. The
corrected production run demonstrated the fix live: its cold primary
chains parked at 469,510 again, and its seeded twin walked straight to
186,370, so the artifact appeared and was disarmed in the same run.

**How far v3.2.0 was off.** The same disease was present in v3.2.0 at an
amplitude small enough to look like convergence. Its committed profile
point at kappa = 0 was 189,761.79. Re-profiling in the true basin under
v3.2.0's own priors, same direction and same layout, gives 186,360.89 at
the same kappa. v3.2.0 was mis-parked by 3,401 units, about one part in
fifty of its own chi square, which is why nothing flagged it.

**The discriminant: basin against priors.** The four-point refit changed
the collision priors at the same time as the basin fix, so the two
effects were separated by re-profiling in the true basin under v3.2.0's
own priors. That gives kappa < 0.982, which is S_0(225 mW) < 0.221 MHz.
Against the 0.151 MHz that shipped, the bound at the old priors is
46% looser, or equivalently v3.2.0's number was 32% tighter than its own
data and its own priors support. The basin effect dominates the change.
The prior update accounts only for the remaining step from 0.221 to the
production bound.

**The bound of record.** The corrected run (382 minutes, all four
families seeded, LOPO complete) puts the profile minimum at kappa = 0.00
exactly, with no chi-square preference for any positive shift. The 95%
upper limit is kappa < 1.192 MHz per W, which is

  S_0(225 mW) < 0.268 MHz.

The robustness family around it: campaign rows alone give 0.177 MHz, the
wing-marginalized profile gives 0.195 MHz, dropping peak 4192 (which
removes the entire pilot session) gives 0.355 MHz, and the rehearsal
direction row sits at 10.5 units of chi square across the whole grid,
indifference where the artifact printed 283,135. No single peak drives
the result (all leave-one-peak-out rows positive and similar). Two
features of the corrected basin are logged as observations: the joint
bound sits looser than its own campaign-only column, because the
rehearsal data mildly prefer a positive shift and drag the profile's
rise, and the pilot peak's collision width settles 4.7 prior sigmas
above its four-point prior.

**What the margin is.** The prediction at the adopted waist is
0.348 MHz at 225 mW. The primary bound sits 1.3x below it, against the
2.3x v3.2.0 claimed. The drop-4192 subset now reaches 0.355 MHz, slightly
above the predicted central value, so the statement that every subset
requires a lower intensity than the prior assumes is retracted along with
the headline: the primary and campaign-only subsets still sit below the
prediction, the most conservative subset no longer does. The predicted
coefficient kappa = 1.545 lies above the 95% limit but only by
delta-chi-square of about 4.0, an exclusion at roughly the two-sigma
level, not the comfortable rejection the inflated bound implied.

**One observation logged, not interpreted.** With the wing nuisance free,
the flipped-direction family settles about 54 units below its unflipped
twin, while the no-wing families are direction-indifferent. This pattern
touches the same near-core structure the C3g follow-up owns, and it is
left there.

**Lesson.** An optimiser's starting point is an input. The failure was
not caught by any residual plot, any coverage test, or any robustness
row, because all of them lived inside the same basin. It was caught by a
number that could not be physical, and only because a robustness check
was re-armed that compared two chains which happened to have parked in
different places.

---

## Addendum 25, 2026-08-03: the wavemeter record is a sawtooth, not a sequence of relaxations

**What the module claimed.** `scripts/run_wavemeter_reconstruction.py` (M22)
digitises the 2025-06-11 wavemeter photograph and fits the trace. Since
2026-08-02 it read the record as twelve re-locks, each kicking the frequency up
and then relaxing back on ONE shared time constant of 353 min, riding on a
record-wide quadratic background of drift and curvature, with a
three-parameter settling noise model on top. Nineteen parameters, fitted by
twenty restarts of L-BFGS-B over all nineteen at once. The number it published
was the settled floor on unmodelled laser motion, 0.63 MHz.

**What a model comparison found.** Fourteen alternatives were fitted against
the same 481 points, the same noise model and the same likelihood, with
whiteness of the residual as the gate rather than likelihood alone. The
relaxation model failed on four counts.

1. Its residual is not white. Lag-1 autocorrelation 0.68, and a runs test at
   z = -6.3, which is 172 sign runs where 241 are expected. Those are long
   same-sign stretches, the signature of a mean function that is the wrong
   shape rather than a noisy one.
2. Its optimiser is not stable. The best of twenty restarts moved by 19.8 in
   negative log-likelihood across five seeds. That is larger than the gap
   between the models the fit was being used to choose between, so the
   published number was partly reporting where its own search started.
3. Four of its twelve kick amplitudes do essentially nothing. Two sit exactly
   at zero and two more below 0.6 MHz, so a third of the events the model
   claims to describe are not being described by it.
4. Its relaxation cannot be resolved by this record in principle. A 353 min
   constant on a 54 min record decays by 14% end to end, which is a straight
   line wearing a curve's clothes.

**What replaces it.** A sawtooth. Between two re-locks the servo holds the
laser onto a reference that is itself settling thermally, so the frequency
ramps steadily through the whole interval at a rate that interval sets for
itself, and a re-lock ends the ramp with a step of finite rise. The fit is a
free level and a free ramp rate for each inter-lock interval, one shared rise
time for every step, no relaxation term, and the same three-parameter noise.
Twenty-eight parameters. The twelve detected kicks cut the record into
thirteen intervals, but the first kick lands at 0.222 min, inside the opening
0.4 min the likelihood already excluded as a digitisation edge effect, so
twelve intervals are fitted and eleven steps are measured.

**How it is fitted.** By profiled likelihood. Hold the rise time fixed and the
mean is linear in its twenty-four levels and ramps, so those are solved in
closed form by weighted least squares inside the objective and the outer search
covers four numbers: the rise time and the three noise parameters. A four
dimensional search replaces a nineteen dimensional one, which is what removes
defect 2 above rather than merely reducing it.

**Its numbers.** Residual RMS 0.660 MHz against the record's own kick-free
scatter of 0.55 MHz in the quiet tail. Runs test z = -0.21, that is 239 runs
where 241 are expected. Lag-1 autocorrelation 0.11. Pull width 1.000, so the
noise model is still right. Shared rise time 0.043 min, about 2.6 s, roughly
one digitised pixel. Settled floor 0.62 MHz. Ljung-Box over twenty lags is
still elevated, driven by the samples within one decimated step of a kick,
where the finder's mid-rise timing and the model's step disagree, so the
residual is called white enough to quote from rather than white.

**The event census, which the old model could not produce.** Its amplitudes
were bounded non-negative and its kick finder only looks for upward jumps, so
a downward step was unrepresentable. Of the eleven testable events, 8 step the
frequency up by more than 1 MHz and are re-locks proper, 1 steps it down by
1.1 MHz, and 2 do not step at all within 0.2 MHz. The two nulls are the end of
a steep ramp, which the finder reads as a jump.

**The background drift and curvature are retired as separate objects.** The old
model carried a shared linear drift of -1.44 MHz/min and a shared curvature of
0.0129 MHz/min^2 across the whole record, and the curvature was the term whose
absence had been called the biggest defect of the model before that one.
Neither survives. The per-interval ramps absorb both: they fall in
magnitude from -8.9 MHz/min in the first fitted interval to -0.4 MHz/min in
the last, and that fall IS the thermal settle the quadratic was standing in
for. Reading the settle interval by interval is what removes the need for a
record-wide background term, so the two rows are dropped from the output rather
than updated.

**What moves.** `results/wavemeter_reconstruction.csv` loses its
`relaxation_tau`, `background_drift` and `background_curvature` rows and gains
the rise time, the event census, the residual whiteness statistics and the
likelihood. `figures/fig14_wavemeter_reconstruction.png` panel (b) now
describes steps and ramps and prints the real event count, and panel (c) prints
the new floor. `figures/fig15_drift_story.png` panel (a) draws the same model
through its overlay and its label follows. `docs/APPARATUS.md` section 6
carries the new reading, the census and the floor.

**What does not move.** Nothing else in the repository. This record is a
photograph of a preliminary session five weeks before the campaign, it is
tagged diagnostic in the results tree, and no physics number rides on it. Every
headline bound stands untouched: the self-broadening coefficient, the
light-shift bound, the laser-width bound, the collisional widths, the frequency
ruler. The floor moved from 0.63 to 0.62 MHz, which is inside the rounding the
apparatus document already used, so even the one number this module publishes
did not really move. What moved is the story the record tells about the laser,
from a servo that overshoots and relaxes to a servo that holds a reference
which is itself still settling.

**Lesson.** A likelihood comparison between two wrong shapes will pick one of
them. The relaxation model was chosen on 2026-08-02 over its own predecessor by
a decisive likelihood margin at equal parameter count, and the residual audit
that chose it recorded the surviving lag-1 autocorrelation and attributed it to
the noise model rather than the mean. It was the mean. A whiteness gate
applied first would have rejected both forms and asked for a third, which is
what it did once it was applied.

## Addendum 26, 2026-08-05: the six-tooth defect, the recalibration, and the full recompute

**What was found.** The frequency ruler's showcase trace was fit and displayed
as a seven-tooth comb while one displayed tooth was the retrace mirror of a
real tooth, reflected about the scan ramp's apex. The fitted height at the
k = -2 slot railed at exactly zero and the selection rule then in force
actively rewarded the pathology. Nothing in the pipeline protected tooth
indexing against retrace contamination. The full account, the validity layer
that now exists, and its seven amendments are in
`docs/notes/ruler_validity_and_trim_prereg.md`. The corrected pipeline
re-fits every comb under a top-three verdict, a re-index ladder, a
core-guarded residual-tail trimmer, and a pre-registered outlier rule, and
the fitted heights of all combs are persisted for the first time.

**Scale of the labelling defect.** Under the sharpened criterion (a
second-order tooth taller than its first-order partner marks a displaced
grid), 54 of 104 recorded combs carry a one-slot displaced numbering (of which
the ratio gate corrects 45, refuses 1, and declines to decide 8, the
coldest), and
the modulation-depth measurement on the 41 clean combs (2 beta = 1.569,
standard deviation 0.058) shows the drive depth is one number across the
campaign, so the displaced grids are mislabelled, not physically different.
The correction is display-side tooth numbering gated on a Bessel ratio
test. The spacing fits, and therefore every rate, were re-derived under the
validity layer.

**What the recompute moved, and what it did not.** The recomputed ruler
layer is byte-identical to the committed tables (rate 0.042524 MHz per ms,
block reduced chi-squared 7.977, scatter 0.617 per cent, to every printed
digit), which is the reproduction statement: a full re-run from raw traces
lands on the identical calibration. The pre-registered directional
predictions of the ruler specification's section 9 were adjudicated at the
recalibration's landing and all met, with one exception recorded below. Of
the pole fits, the M28 primary bound is unchanged (the light shift at
225 mW stays below 0.212 MHz, census 231, gates B1 through B8 pass with B4
carrying its pre-existing 3.78 sigma prior tension), the M23 primary
tightens about four per cent (the 225 mW bound moves from 0.268 to
0.258 MHz), and the M25 global fit is byte-stable with the joint
self-broadening slope at 0.0183 MHz per 10^12 cm^-3. The no-rulers variant
of the global fit, in which the calibration combs contribute nothing as
data, lands at the same profile minimum with the joint slope at 0.0182, so
the physics bounds do not lean on the corrected traces. The subset
robustness variants (campaign-only and power-ladder-only) moved by 26 and
35 per cent between runs whose inputs differed by less than 0.001 per
cent. That pattern is not quoted anywhere until it is adjudicated: an
identical-input reproduction of M28 is pre-registered at a three per cent
threshold in `docs/notes/m28_reproducibility_prereg.md` and launches with
this release.

**The fold-robustness paragraph is superseded in place.** Its structural
argument (a symmetric triangle preserves tooth spacing under a fold) is
true of the ramp and false of a rigid-grid fit, whose window assignment is
exactly what a fold displaces. The bounded form survives: an apex landing
on a tooth is benign, and the validity layer's tests pin that case. The
section of `docs/DATA.md` that carried the claim carries the corrected
reading under the same anchor since 2026-08-06 (the phase 7 red team
found this sentence written before the edit it describes, and the edit
is now made).

**Relation to addendum 19.** Addendum 19 corrected a five-tooth fit to
seven and withdrew an earlier retrace claim as a threshold-finder artifact.
This addendum sits on top of it with a different instrument class: a
smoothed fit residual at +10 sigma at a slot whose fitted height rails at
zero, plus rank statistics under a null-calibrated change-point detector.
The exploration that first flagged the problem also ran a naive peak
finder that flagged 41 of 105 rulers, mostly cold-trace noise, and that
count is deliberately not quoted as evidence. What survives untouched:
addendum 22's spacing-symmetry receipt (a frequency-domain statement,
orthogonal to this time-axis defect) and its refusal to license ruler
combs as lineshape data, which the M28 census re-affirms.

**The one persisted prediction failure, read as agreed.** Section 9
predicted the 4207 nm before-against-after rate separation would shrink
under the corrected pipeline. It did not: it holds near 3.7 sigma. The
persisted 3.7 sigma is the largest of four instances of a measured
campaign property, not a 4207 defect. The four signed pair separations are
+2.65, -0.06, +2.56 and -3.67 sigma (pair-family reduced chi-squared about
6.9, the same scale as the block over-dispersion of 7.98 the archive
documents). The signs are incoherent across lines, so this is not
common-mode session drift. The separation survived the six-tooth
correction, so it is not mislabelling. What remains is genuine per-line
scan-rate wandering between brackets, of which 4207's -1.1 per cent swing
is the extreme case. The failed prediction carries information: the
separation was never fold contamination. On signal to noise: 4207's
bracket errors are already the largest of the set and it is still 3.7
sigma apart, so the excursion is real, and worst signal-to-noise means the
line is least able to diagnose itself, not that the excursion is noise. No
pipeline change ships in this release, and a fixed-lock session kills the
class outright, which the plan's Tier 0 may cite this excursion as
motivation for.

**Amended 2026-08-06 (RT11 of the frequency-calibration red team).** The
two supporting statements this paragraph first carried are both wrong, and
the conclusion is unchanged. The first was that combine_block's
square-root chi-squared inflation already prices the inconsistency into
4207's rate error and its power-session widths. It cannot: the inflation
enters as one block-coherent multiplier on a line's five widths while the
excursion is a gradient across them, and `_apply_rate_models` folds the
rate spread block-coherently for the same reason. The second was the
forward test, per-block interpolated rates against the bracket mean, read
out as whether 4207's width scatter drops. That observable is null by
construction rather than open. Both interpolations reconstructible from
committed data are linear in time, the power ladder ran 225 to 25 mW
monotonically in time, and a monotone multiplier over a monotone schedule
aliases into a slope against power and never into scatter. The measured
change in 4207's width scatter is -0.1 to -1.0 per cent, which is the
null it has to be. The observable that does move is the 225 minus 25 mW
width difference. Its consequence comes with its own cancellation: the
four per-line aliases carry incoherent signs, the shared-kappa fit floats
a per-line core width that absorbs the common part, and a read-only rerun
moves the 95 per cent upper bound on S0 at 225 mW from 0.632 to 0.627 MHz,
0.8 per cent, against a documented subset spread of 26 to 35 per cent.
Answering this took reading the construction rather than taking a
measurement, which is why it was forwarded as an open test at all.

**Gates, reported whether they fired.** Stop conditions: block reduced
chi-squared rising (did not fire, 8.078 to 7.977), scatter rising (did not
fire), the M28 primary moving beyond noise (did not fire, unchanged),
census departing 231 (did not fire). Fired and acted on: the seven-tooth
figure-eligibility clause returned the empty set and was relaxed to six
standing teeth by owner decision with two measured causes recorded
(amendment 4). Fired and standing: the 4207 separation prediction,
recorded as FAILED above.
