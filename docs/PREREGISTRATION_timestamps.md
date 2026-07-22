# Pre-registration — the recovered acquisition timestamps

*Written 2026-07-22, before the backup was opened. Repository state at writing:
`fd45da6`. Nothing in this document may be edited after the backup is first
read; corrections go in the results report that follows it.*

---

## 1. What happened, and why this document exists

Every analysis in this repository was built on the premise that the archive
carries **no acquisition clock**. `PLAN.md` §1 stated it flatly — block order
was the only time coordinate — and limitation row 5 recorded the direct cost:
the $\sigma_\text{laser}$ epoch-sharing assumption could not be tested at all.

A backup of the raw data carrying file timestamps has now surfaced
(2026-07-22). It has not been opened.

The campaign chronology in [`DATA.md`](DATA.md) §2 — the order of powers, the
cooling sequence, the claim that repeats were saved seconds apart — is
**experimenter recollection**, tagged as such since it was written. It has been
public since commit `9190b0b` (2026-07-13, release `v1.0.0`), **nine days
before the backup surfaced**, and unchanged in substance since.

That accident makes a genuine blind test available: a detailed, public,
timestamped account of when things were measured, and an independent clock that
can be checked against it. The value of that test survives only if the
predictions are fixed *before* the data is read — hence this document, and
hence the release tagged before the audit runs.

## 2. What this does NOT test

Stated first, because the temptation to over-read a recovered clock is the main
risk here.

- **Assumption A1 (trigger sync — file time $=$ ramp phase)** is untouched.
  A1 concerns the scope trigger's phase *within* a 1.000 s trace; a file's
  modification time carries no information about it. A1 remains open and is
  still listed as needing one word of experimenter confirmation.
- **Absolute trace positions across saves** remain meaningless (horizontal-knob
  and cavity-reference recentring between saves, `DATA.md` §2). A clock does
  not restore a frequency axis.
- **No archival result is expected to move.** The predictions below concern
  provenance and ordering. If one fails, what changes is a stated premise and
  its downstream caveats — named in §6 — not a fitted number.

## 3. Integrity gates (scored first; predictions are void if these fail)

| # | Gate | Pass criterion | If it fails |
|---|---|---|---|
| T1 | **Content identity** | SHA-256 of every backup file matches `data_raw/MANIFEST.csv` for basenames present in both | STOP. Red-team before any interpretation: a content difference means the backup is not the analysed data |
| T2 | **Clock plausibility** | mtimes fall inside the 2025 research-visit window | Timestamps are backup-copy times, not acquisition times. The audit is **void**; report that and stop |
| T3 | **Mass-copy signature** | no single mtime shared by an implausible fraction of files | Same as T2 — copy artifact, not acquisition clock |
| T4 | **Granularity** | record the quantisation (1 s, 2 s FAT, sub-second) | Not a failure; the spacing predictions (P5) are scored against the measured granularity, not against an assumed one |
| T5 | **Timezone discipline** | all comparisons in raw epoch seconds | Not a failure; a fixed convention recorded once. JST acquisition read on a CET machine displaces displayed times by 7–8 h — never compare rendered local strings |
| T6 | **Clock of record** | if original LeCroy `.trc` files are present, the header trigger time supersedes mtime and is used instead | Not a failure; the choice is recorded per prediction, since an embedded time survives copying and an mtime may not |

## 4. Predictions

Scored only if T1–T3 pass. Each is stated so that a single deterministic script
can return pass / fail / ambiguous with no judgement call at scoring time.

| # | Prediction (from `DATA.md` §2, public since 2026-07-13) | Pass |
|---|---|---|
| P1 | The whole 130 °C power session precedes every 110 / 90 / 70 °C acquisition | no cooling-block file predates any power-session file |
| P2 | Per peak, the power ladder runs before-rulers → 25 → 75 → 125 → 175 → 225 mW → after-rulers | holds for all four peaks, allowing the pre-registered "a few possible swaps": **≤ 3 adjacent-block inversions campaign-wide** |
| P3 | Cooling proceeds 110 → 90 → 70 °C | strictly monotonic in time |
| P4 | Temperature is monotonically decreasing with campaign time (130 first, 70 last) | no temperature increase between consecutive blocks |
| P5 | Repeats within a block are back-to-back, saved seconds apart | median intra-block gap smaller than median inter-block gap by **≥ 10×**, and intra-block gaps of order seconds-to-minutes at the T4 granularity |
| P6 | Ruler blocks bracket each peak's power session | each peak's before-ruler block precedes its first power block; its after-ruler block follows its last |
| P7 | The byte-identical double-saves (`DATA.md` §3.3, e.g. `temperature/4154nm_070c1 ≡ 070c2`) are re-saves within one block | each such pair's timestamps are mutually closer than that pair is to any other block |
| P8 | The cross-directory identity `temperature/*_130c{1..5}` $\equiv$ `power*/*_225mw{1..5}` (`DATA.md` §3.1) reflects curation-time renaming | curated-copy time equals, or postdates, its `raw/` source — a curated file predating its own source is incoherent and would indict the clock |

## 5. Scoring rules

- **One run.** The scoring script is committed, and its commit SHA recorded in
  the results report, before it is executed against the backup. Criteria are
  not adjusted after results are seen.
- **Everything is reported** — passes, failures, and any prediction that comes
  out ambiguous — not a selected subset.
- **Post-hoc is labelled post-hoc.** Anything the timestamps suggest beyond
  P1–P8 is interesting and is reported in a clearly separated section, carrying
  no pre-registered standing.
- Curation is audited symmetrically: if the backup holds acquisitions absent
  from `raw/`, they are examined under the same rules as the discards already
  documented in `DATA.md` §3.4, not quietly folded in.

## 6. Consequences, fixed in advance

| Outcome | What changes |
|---|---|
| P1, P3 or P4 fails | The collisional analysis's "temperature monotonic with time" premise breaks. `DATA.md` §2 loses experimenter-confirmed standing and is restated from the clock; the M4 stationarity probes are re-read against the true order; every downstream caveat that leans on monotonicity is revisited |
| P2 fails within the ≤ 3 allowance | The pre-registered uncertainty resolving as advertised. Repeat-index ordering is corrected; no conclusion moves |
| P2 fails beyond the allowance | Recollection and clock disagree materially. The clock wins; §2 is rewritten and the disagreement reported prominently rather than reconciled |
| P5 fails | "Repeats back-to-back, seconds apart" is wrong, and the 1.8 ms position-scatter reading built on it is re-examined |
| P7 or P8 fails | The double-save and cross-directory identities in `DATA.md` §3 need a different explanation than curation-time renaming |
| All pass | The chronology becomes **timestamp-verified** rather than experimenter-confirmed; limitation row 5 changes status and the $\sigma_\text{laser}$ epoch-sharing assumption becomes testable for the first time |

Whatever the outcome, `PLAN.md`'s "no timestamps exist anywhere" is already
superseded and has been corrected to describe what was available to the
archival analysis, with this audit named as pending.

---

## 7. Amendment, 2026-07-22 — the drift-rate observable

*Added the same day, still **before the backup was opened**, prompted by an
experimenter clarification. Recorded as an amendment rather than folded into
the text above so the order of events stays auditable.*

**The clarification.** Re-centring was not occasional: the lock drifted enough
that the transitions had to be brought back inside the scan window **many
times**. But **within a single 5-repeat block nothing was moved**.

That second half is what matters. It promotes the intra-block position scatter
from a nuisance to a **drift measurement** — with the block's elapsed time, the
2025 lock drift rate becomes measurable from the archive. `PLAN.md` §8.4 lists
measuring that rate as something only a future session could buy (item ii);
if the clock survives §3, the archive may yield it retroactively.

**A tension that already exists, stated before looking.** For 5 evenly spaced
traces under linear drift, scatter $= r \times T \times 0.354$. The measured
0.08 MHz and the `constants.DRIFT_RATE_LASER_HZ_PER_MIN` envelope of 4 MHz/min
are mutually consistent only for $T \approx 3.4$ s — shorter than the
$5\times1.000$ s of acquisition the block must contain. So:

> **Pre-data prediction D0.** The measured archival drift rate will come out
> **below 4 MHz/min**. For plausible block durations of 10–60 s it lands at
> **0.2–1.4 MHz/min**, i.e. 3–18× below the current envelope, which will need
> revising downward.

| # | Derived analysis (scored after P1–P8) | Method | Pre-registered expectation |
|---|---|---|---|
| D1 | **Drift rate** of the 2025 lock | intra-block position scatter ÷ block elapsed time, over all blocks | below the 4 MHz/min envelope (D0) |
| D2 | **Drift model** — linear vs random walk | how intra-block scatter scales with block duration across blocks of differing length: $\propto T$ linear, $\propto\sqrt{T}$ random walk | undeclared; `PLAN.md` §8.9 calls the archive's between-block swing "random/non-monotonic", which favours $\sqrt{T}$, but this is not a prediction |
| D3 | **Re-centring frequency** consistency | count between-block position discontinuities; compare with (rate × campaign elapsed) ÷ 43 MHz window | the count implied by D1 is consistent with "many times" as reported |

**If D1 and D3 disagree** — a drift rate too low to have forced the re-centring
the experimenter remembers — then either drift was episodic rather than steady,
or the intra-block scatter is dominated by lock jitter rather than drift. Both
are reportable outcomes, not failures; what is *not* permitted is choosing
between them after seeing which flatters the envelope.

**Scope.** D1–D3 are derived analyses, weaker in standing than P1–P8: they
depend on the clock being real (§3) and on the no-movement-within-a-block
protocol being right. They are pre-registered so that the drift rate cannot
later be quoted as though it had been predicted.

---

## 8. Integrity note, 2026-07-22 — D0 is no longer blind

*Recorded the same day §7 was written, before the backup was opened, and
before any prediction was scored.*

Setup photographs added to the working tree include a **HighFinesse WS8
long-term wavemeter record** (2025-07-23, 993.420860 nm, 3 h 30 min). It shows
the scan band's centre drifting **≈36 MHz downward over 3.5 h**, i.e.

> **≈0.17 MHz/min** (±20% on an off-screen read), against the
> `constants.DRIFT_RATE_LASER_HZ_PER_MIN` envelope of **4 MHz/min** — roughly
> **23× lower**.

This is an *independent* measurement of the quantity D0 predicts, and it was
read **after** D0 was written but **before** the timestamp audit runs.
Therefore:

- **D0 is downgraded from a blind prediction to a corroborated one.** If the
  timestamp audit later returns a rate below 4 MHz/min, that outcome must NOT
  be reported as a successful blind prediction. It was known, from another
  instrument, in advance.
- D0's *direction* is independently confirmed; its quoted band (0.2–1.4
  MHz/min) is already slightly high — the photo sits just below it.
- The corroboration does not come from the timestamps, so P1–P8 and D1–D3
  retain their standing. Only D0's epistemic status changes.

**A sharper prediction, still blind with respect to the timestamps.**
Combining the photo's drift rate with the measured 0.08 MHz intra-block
scatter — and assuming that scatter is drift-dominated and drift is locally
linear — gives a *block duration*:

> **D4.** A 5-repeat block spans **≈80 s** (≈16 s per saved trace), order
> 1 minute rather than order 5 s. Pass: median block duration in 40–160 s.

D4 is a genuine pre-data prediction about the timestamps and is the sharpest
test in this document: it takes a number from the wavemeter and predicts one
from the filesystem, with no free parameter between them. A large miss falsifies
either the drift-dominated reading of the intra-block scatter or the linear-drift
assumption, and says so.

**Open questions that gate all of this** (experimenter, not derivable here):
whether the lock was engaged during that record, whether 2025-07-23 falls inside
the acquisition campaign, and whether the oscillation visible in the trace is the
spectroscopy sweep. If the record is free-running rather than locked, it
constrains the free-running drift and D4 does not follow.

---

[← DATA.md](DATA.md) · [PLAN.md](PLAN.md) · [docs index](../README.md)
