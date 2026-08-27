# Producers and provenance

*[History](../HISTORY.md) · numbers without producers, and the instruments that found them*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## Documentation counts, 2026-08-19

Each row below is a published, quotable figure, corrected in one pass. No physics number moved.

| Item | Was | Now |
|---|---|---|
| Light-shift width-only bound (two documents) | 0.64 MHz | 0.63 MHz (0.632 committed, matching every other site) |
| Wiki index correction-section page count | 19 pages | 14 pages |
| Runner header stage count | 25 stages | 27 stages, matching its own loop |
| Methods summary module range | one module short of its own table | matches the table |
| Glossary module range | four modules short of its own table | matches the table |
| Reproduction guide CSV-to-script count | 12 CSVs credited to 12 scripts | 12 CSVs credited to 11 scripts |

Each was a stale count that had drifted from the page, table, or loop it should have matched.

## The width-pinning factor, 2026-08-19

The factor by which an independent laser-width measurement tightens the fitted collisional width, from `scripts/run_width_pinning.py`, was quoted in four documents as 3.4, the producer's single default-seed draw. Run at nine seeds of 200 trials each, the ratio is $3.18 \pm 0.20$ (range 2.86 to 3.48), and 3.4 is the largest of the nine. All four sites, and the producer's own default, now carry $3.18 \pm 0.20$ from the nine-seed ensemble. The value is set by the fit's correlation between the two widths. [identifiability](../wiki/identifiability.md) carries that arithmetic and the other correlations this record has quoted.

## The skew-scaling producer's default draw count, 2026-08-20

`run_skew_scaling.py` defaulted to 400 simulation draws, but the committed output file was made at 1500, the count its own docstring calls stable across five seeds. Rule 19.75 requires the quotable number to be the default invocation's number, so the default is now 1500 and the file is regenerated from it. The conclusion is unchanged.

| quantity | was | now |
|---|---|---|
| `run_skew_scaling.py` default draws | 400 | 1500 |
| fixed-amplitude exclusion, p | 0.010 | 0.011 |
| recovered scatter, shot-noise ceiling test | 0.301 | 0.532 |
| shot-noise p-value | 0.083 | 0.083, unchanged |

Three pages and the generated ledger carried the old p-value and now carry the new one, tied to the producer's cell by a registry entry.

## A published regression had no producer, 2026-08-23

[The band-excess note](../notes/band_excess_is_model_form.md) publishes a joint regression over 79 canonical traces: profile height at 8.65 sigma, vapour density null at -0.75, the two predictors correlated at 0.415, and a shared excess at 3.6 sigma under per-trace cubic freedom. No committed producer computes any of these and no `results/` row holds them, so no freshness check could see them. `results/kernel_k8.csv` had quoted 8.65 and -0.75 into its own note column beside its freshly computed 9.41 and 1.30. The note, the limitations chapter and the front page now state that the band pair stands on weaker footing than the K8 pair beside it. `tests/test_note_provenance_ratchet.py` now bounds unproduced numeric claims per file in `docs/notes/`. A producer for this analysis remains unbuilt.

## Seven of ten notes had no producer, 2026-08-23

An audit of `docs/notes/` against `results/` and `scripts/` checked ten notes carrying numeric claims with no stated source.

| Item | Was | Now | Cause |
|---|---|---|---|
| Notes with no producer | undeclared | 7 of 10 declared `NO_PRODUCER`; 3 of 10 have a `results/` home | no note stated what backed its numbers |
| Unaccounted claims | uncounted | 109 individual claims flagged, unresolved | claim-level accounting did not exist |
| `s0_block_bootstrap_prereg.md` factor 2.4 | undeclared in `docs/RESULTS.md` | `docs/RESULTS.md` states its only source is a gitignored run log | the value was hand-copied as a literal into `scripts/make_results_ledger.py` |
| `docs/notes/model_selection_prereg.md` | `dAIC = -24.6 - 18 = -6.6` | `dAIC = -24.6 + 18 = -6.6` (value unchanged) | wrong operator, correct result |

`tests/test_note_provenance_ratchet.py` holds the declaration budget at zero.

## A governed row about ungoverned numbers, 2026-08-23

The provenance declarations added earlier the same day lived only in prose, ungraded by any freshness instrument. `results/unregenerated_claims.csv` is new, derived by scanning `provenance:` tokens in `docs/notes/` instead of a hardcoded list.

| Count | Value |
|---|---|
| Notes carrying a declaration | 14 |
| Rest on numbers no committed producer regenerates | 8 |
| Have a real `results/` home | 3 |
| Design or index pages, none expected | 3 |
| Individual claims unaccounted for inside declared notes | 109 |

A forward pointer was added to "The in-window structure and the band excess share a predictor, 2026-08-23," linking it to that same-day resolution.

## Two results files were committed without their status column, 2026-08-23

`results/cooperative_channel.csv` and `results/orthogonal_levers.csv` were committed missing the `status` column the other results files carry, and the committed figures did not match the committed CSVs. No value was wrong.

Producers write CSVs without the status column, and `scripts/annotate_results_status.py` adds it afterward. A read-only investigation running several producers against the same working tree stripped the column before a `git add -A` commit captured that state. A first gate failed on eleven stale figures, a downstream symptom, and a second failed on the missing column, the actual defect. Producers and the annotator were re-run and figures redrawn. Values are unchanged.

## The provenance guard reported a clean corpus it could not see, 2026-08-23

`results/unregenerated_claims.csv` gained four rows and two of its counts moved. No measured number moved. The prior entry's budget of zero held only for notes whose claims matched its pattern, a decimal followed by "sigma" or "per cent," or a bolded signed decimal.

| Metric | Was | Now |
|---|---|---|
| Notes with a matched claim | 14 of 23 | 23 of 23 |
| Notes scored undeclared | 0 | 9 |
| Claims counted | none tallied | 252 |

The pattern was widened to also match MHz, kHz, mW, percentages, and plain counts. Separately, `docs/notes/vdw_difference_potential_and_4d_channel.md` was declared `NO_PRODUCER`, which was false. Its values 0.3473 and 0.3128 are reproduced by `rb5s6s/vanderwaals.py::beta_self_anchored()`, now recorded under a new `path.py::function` provenance kind. A test now refuses a declaration naming a `results/` file or function that does not exist.

## The provenance debt partition, 2026-08-23

`results/unregenerated_claims.csv` gained a partition of its orphan-claims count: most are too generic to check (under three significant figures) or already appear in some other committed CSV. Exactly one is an ungoverned value quoted on a reader-facing surface, the saturation companion's 0.6325 MHz, printed in `docs/RESULTS.md` and the saturation wiki page, both already disclosing it as unbacked. No value moved. Three budgets were added on top of the count, each allowed only to fall, tested by planting a violation of each.

## The provenance instrument's self-reference, 2026-08-23

`run_unregenerated_claims.py` read its own output file, `results/unregenerated_claims.csv`, when deciding whether a value was grounded: the partition's one reader-facing orphan is named in that file's own note column, so a second run over an unchanged tree counted the value as present in `results/` and reclassified it from orphan to quoted, moving the committed-CSV count from 40 to 41 with no code or data change. The committed-CSV test caught the mismatch. The producer now excludes its own output file from that check, so repeated runs agree. Cause: an instrument that writes to and reads from `results/` cannot treat its own presence there as evidence.

## The twin's span-sweep correlations, and the fibre wiki page, 2026-08-23

Three digital-twin correlations quoted on ten public surfaces, -0.9177, -0.9166 and -0.881, had no row: the run that produced them recorded neither truth parameters nor a seed, so the four decimals could not be regenerated. `scripts/run_twin_span_sweep.py` confirms the same claim from fresh inputs: a named condition from `linefit_conditions.csv`, the committed waist, and a fixed seed. It gives a correlation shift of 0.0075 over a five-times-wider span and 0.0000 at ten times the repeats, while the collisional-width uncertainty falls by 3.16, matching independent sampling. Widening the span at fixed point count instead worsens it 2.72-fold. The retired correlations stay quoted where printed, flagged as unreproduced. Same day, `wiki/guided-atoms-and-nanofibres.md` was added, setting the two guided geometries against each other.

## The note-provenance debt count, 2026-08-23

Three tracked counts moved, after the last nine undeclared notes in `docs/notes/` were checked against `results/` and given a status.

| count | was | now |
|---|---|---|
| notes_ungoverned_total | 15 | 7 |
| notes_no_producer | 6 | 7 |
| orphan_claims_total | 105 | 182 |

No value moved elsewhere. `notes_undeclared` is now zero. The two counts that rose reflect notes moving from undeclared to a graded status (results-CSV, DESIGN, PREREG, or NO_PRODUCER), not new debt. `notes_ungoverned_total` is the sum a ratchet holds and tracks only downward from here.
