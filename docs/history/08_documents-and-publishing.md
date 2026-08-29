# Documents and publishing

*[History](../HISTORY.md) · corrections to what the record said, not to what it measured*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The tutorial's width-degeneracy claim, 2026-08-19

An unreleased draft of `docs/TUTORIAL.md` claimed that widening the scan span breaks the degeneracy between the laser width and the collisional width. On synthetic data with known truth, the correlation runs -0.9177 at a 60 MHz span, -0.9166 at 300 MHz, and -0.881 at ten times the traces. Widening the span or the sample does not move it, since the degeneracy belongs to the lineshape, a Lorentzian core convolved with a Gaussian. The draft never reached a reader. The corrected result is `rb5s6s.forecast.external_constraint_gain`, the factor 1/sqrt(1-rho^2) by which pinning one width buys the other, guarded by a test written against the draft's claim.

## The case page's re-centring purchase factor, 2026-08-20

The ten-minute case page's re-centring table gave the purchase from an independent laser-width measurement as running "2.3 at the record's median $\rho = -0.90$ to 3.5 at the pinning simulation's own $-0.94$". The analytic value at that condition, $1/\sqrt{1-\rho^2}$ with $\rho=-0.9417$, is 2.97, and the nine-seed simulated value is $3.18 \pm 0.20$, both already stated in [chapter 7](../big_picture/07_limitations-and-identifiability.md) and [identifiability](../wiki/identifiability.md). The published 3.5 matches neither. It is 3.45, the largest of the nine draws already retired in [the pinning-factor entry](05_producers-and-provenance.md#the-width-pinning-factor-2026-08-19). All three correlations on the page now carry the construction each belongs to.

## The case page's two ungrounded numbers, 2026-08-23

`docs/plan/00_the-case.md` quoted two values with no committed row behind them: the digital twin's span-sweep correlations, -0.9177, -0.9166 and -0.881, printed on ten public surfaces, and a 99.8 per cent window-attribution figure. The span-sweep correlations are unchanged and still unregenerated. The page now states that no producer backs them. The window-attribution figure is now grounded, in `results/window_attribution.csv` (`run_window_attribution.py`), with the denominator defined as the mean square of the between-block steps. Cause: the page's first provenance sweep.

## The case-page headline statement, 2026-08-24

`docs/plan/00_the-case.md`'s headline sentence read "S₀(225 mW) below 0.258 MHz at 95%, against 0.348 MHz predicted". A claim-by-claim check against the page's own sources found that it left S₀ undefined, called a shift a coefficient, quoted three significant figures against a 0.13 MHz subset spread, and asserted an exclusion that the page's own drop-4192 robustness arm contradicts fifteen lines later, at 0.37 MHz, above the prediction, without saying so. The sentence now defines S₀, quotes two significant figures, and states the comparison together with the failing drop-4192 arm in the same passage, with its producer linked. No bound moved. **On 2026-08-27 that two-sigma strength gained two qualifications**: it is a range rather than a number, and it does not survive leaving one peak out. RESULTS.md C3f carries them.

## The band-excess significance pair, 2026-08-24

Six earlier entries in this file quote the band-excess pair, 8.65 sigma on profile height and 3.6 sigma cubic-surviving, as live numbers, including a table that weighs 8.65 against the unrelated 9.41 figure. Those entries are dated and closed and hold only what was believed when written. The live values are 3.05 sigma and 1.4 sigma, given in the reconstruction entry above ("The band-excess construction was reconstructed, and the digits did not survive"), because the note's original construction is not recoverable from its prose.

## The 64 µm waist's provenance, 2026-08-24

docs/wiki/the-beam-waist.md described the 64 µm beam waist as a transfer across apparatus, with Nieddu 2019 measuring it and [Rajasree 2020](../lit/rajasree2020thesis.md) reprinting it on a different laser five years later. It is a single same-bench Rajasree measurement, same optical table, laser and lenses, so the extra transfer uncertainty the page told readers to carry was never owed. No number moves. The correction rests on firsthand apparatus knowledge outranking a documented inference. The word that hid this, and three more like it, are banned from this corpus's prose by tests/test_prose_style_ratchet.py.

## Emphasis capitals in the corpus, 2026-08-24

The owner's rule bans all-capital emphasis words in this repository's prose unless they are required acronyms, held since by `tests/test_prose_style_ratchet.py` against the allowlist in `tests/_caps_allowlist.json`. A sweep found 3003 emphasis capitals across 130 tracked pages and lowered them. What stays capitalised is acronyms, the status vocabulary results ledgers are graded on (VERIFIED, REPORTED, CITE, FEED, BOUND, MEASURED, DIAGNOSTIC and siblings), provenance tags, underscored machine identifiers, atomic-state notation and document names.

## The 2025 laser width bound, renamed 2026-08-24

The bound called "the 2025 laser width" is not a laser measurement.
`laser_epoch.csv` calls it the Gaussian left over once transit is removed
at the measured waist, a degeneracy that falls to zero near a 16
micrometre waist. Independent evidence puts the laser two orders of
magnitude below it: a wavemeter holds 100 kHz standard deviation over 24
minutes, and the comb bounds the non-repeating excursion below 28.3 kHz.
The quantity is renamed to what it bounds, on the case page, in README,
and in the results ledger's C2. No number moves.

The same block also named a heated vapour cell with no trap "the shift the
trap beam imposes on the line". The apparatus noun is corrected on the
case page.

## The quantities pages disagreed with the record they index, 2026-08-26

Two pages under `docs/quantities/` stated values the rest of the record
contradicts, and both were found by an outside reading rather than by a
guard. `ac-stark-light-shift.md` presented the cited differential
polarizability as the value this repository adopts. The package default is
this record's own, opposite in sign, and
[THEORY_NOTE.md](../THEORY_NOTE.md) already said so.
`self-broadening.md` quoted the pooled collisional bound from the column
that omits the vapour-pressure scale systematic, while
[RESULTS.md](../RESULTS.md) and the design chapters quote the column that
carries it. Both pages now agree with the record. No committed number
changed, and no bound moved.

## The v4.3 and v4.4 release pages, withdrawn 2026-08-26

The v4.3 page and the first v4.4 page, published on both repositories, are
withdrawn against the form required by
[RELEASE_NOTE_STYLE.md](../RELEASE_NOTE_STYLE.md). **That form was not the
cause, and the entry below corrects it**: it names the physics, and the files
carrying the live values. Neither was republished. Their content
carries forward in the v4.5 page, which spans v4.2 to that tag. The v4.3
and v4.4 tags stand where they were, because nine places in the tree cite
them as the versions at which the exported API changed. No committed number
changed. Release pages before v4.3 stand as published, as the record of
what was said at the time.

## The withdrawn release notes were withdrawn for the physics, 2026-08-28

| the claim | where | was | is |
|---|---|---|---|
| why the v4.3 and v4.4 pages were withdrawn | the entry above | register: narrative voice, uncited numbers, unresolvable terms | the physics was wrong or confused, and the register was the smaller half |

**Cause: nobody checked the notes' claims against the record.** A one-sided
bound was divided by a point prediction and the quotient called the
disagreement. A waist was quoted that no producer computes. A ramp of red
shifts was asserted against a constant implying blue. A null was reported as a
measured size. The live values are in `results/stark_joint.csv`,
`results/polarizability.csv` and `results/band_excess.csv`.

**The rule was not missing.** The [release-note rules](../RELEASE_NOTE_STYLE.md) already required every
number to name its committed file, and that rule had no mechanism. It has one
now, and the same page carries what a person still reads.

## The release-note rules were not enforced as claimed, 2026-08-28

| the claim | where | was | is |
|---|---|---|---|
| the withdrawal's causes are enforced by a checker | the entry above | "now enforced by `scripts/check_release_notes.py`" | three of ten rules have a check, each in its narrowest reading |
| the body's word ceiling | `scripts/check_release_notes.py` | refused at 400 where the rule states 300 | refuses at the rule's own 300 |

**Cause: a note written to carry the defects that caused the withdrawal, while
avoiding the banned phrases and staying under the ceiling, passed the checker.**
The rule that every number names its committed file, and the fixed template,
have no mechanism at all. `RELEASE_NOTE_STYLE.md` gained a statement of which
rules are mechanised, and the rule the withdrawn pages broke, stated in
[the style guide](../RELEASE_NOTE_STYLE.md): a note reports a change and does
not perform the inference in front of the reader.

## Counts in prose, and the day three of them were wrong at once, 2026-08-28

A count written into a sentence goes stale the day the thing it counts grows,
and nothing reads a sentence.

| the claim | where | was | is |
|---|---|---|---|
| the test battery | `docs/methods.md`, twice | 2957, and "3072 fast + 41 slow" beside it, which sums to 3113 | 3103 collected, 3062 fast and 41 slow, measured by `pytest --collect-only`. This cell has been wrong three times, because a count of a thing that grows goes stale between measuring it and committing it |

**The repair is not a corrected number.** The tally moves to the thing that
holds it, and the prose states the rule: `docs/methods.md`'s figures are
compared against a real collection by a guard on every run. Three further
counts of the same class were corrected the same day in untracked working
notes, the same way.

## A summary drifted from the record it restated, 2026-08-28

A summary file restating the repository's own state was checked against that
state for the first time, and its headline claim was wrong: it gave one count
of an internal check's outcomes where the primary record held another. Found
by reading the primary instead of trusting the summary. A checker now compares
every claim in that summary that has a machine-readable primary, and reports a
claim it can no longer find as a broken check rather than as a pass. Live in `private/checks/summary_drift.py`, which is gitignored: the
archive holds it and a clone does not.

## A checker was described in three documents and did not exist, 2026-08-28

A tool for carrying rule text verbatim to an independent reader was named in
three documents, in the present tense, as though it existed. **It was not on
disk.** Third recorded instance of one class: the enforcement report's
rule-file precondition was described for a day before it existed, and the guard
census was asserted before it was counted. Live in `private/checks/reader_brief.py`, which is gitignored: the
archive holds it and a clone does not.

The file exists now. The rule that answers the class is not another instrument.
It is a constraint on tense: a document may state that a checker does something
only where a run of it is quoted beside it, or where the sentence is written as
a specification and not as a report.
