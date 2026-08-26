# Documents and publishing

*[History](../HISTORY.md) · corrections to what the record said rather than to what it measured*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The tutorial's width-degeneracy claim, 2026-08-19

An unreleased draft of `docs/TUTORIAL.md` claimed that widening the scan span breaks the degeneracy between the laser width and the collisional width. On synthetic data with known truth, the correlation runs -0.9177 at a 60 MHz span, -0.9166 at 300 MHz, and -0.881 at ten times the traces. Widening the span or the sample does not move it, since the degeneracy belongs to the lineshape, a Lorentzian core convolved with a Gaussian. The draft never reached a reader. The corrected result is `rb5s6s.forecast.external_constraint_gain`, the factor 1/sqrt(1-rho^2) by which pinning one width buys the other, guarded by a test written against the draft's claim.

## The case page's re-centring purchase factor, 2026-08-20

The ten-minute case page's re-centring table gave the purchase from an independent laser-width measurement as running "2.3 at the record's median $\rho = -0.90$ to 3.5 at the pinning simulation's own $-0.94$". The analytic value at that condition, $1/\sqrt{1-\rho^2}$ with $\rho=-0.9417$, is 2.97, and the nine-seed simulated value is $3.18 \pm 0.20$, both already stated in [chapter 7](../big_picture/07_limitations-and-identifiability.md) and [identifiability](../wiki/identifiability.md). The published 3.5 matches neither. It is 3.45, the largest of the nine draws already retired in [the pinning-factor entry](05_producers-and-provenance.md#the-width-pinning-factor-2026-08-19). All three correlations on the page now carry the construction each belongs to.

## The case page's two ungrounded numbers, 2026-08-23

`docs/plan/00_the-case.md` quoted two values with no committed row behind them: the digital twin's span-sweep correlations, -0.9177, -0.9166 and -0.881, printed on ten public surfaces, and a 99.8 per cent window-attribution figure. The span-sweep correlations are unchanged and still unregenerated. The page now states that no producer backs them. The window-attribution figure is now grounded, in `results/window_attribution.csv` (`run_window_attribution.py`), with the denominator defined as the mean square of the between-block steps. Cause: the page's first provenance sweep.

## The case-page headline statement, 2026-08-24

`docs/plan/00_the-case.md`'s headline sentence read "S₀(225 mW) below 0.258 MHz at 95%, against 0.348 MHz predicted". A claim-by-claim check against the page's own sources found that it left S₀ undefined, called a shift a coefficient, quoted three significant figures against a 0.13 MHz subset spread, and asserted an exclusion that the page's own drop-4192 robustness arm contradicts fifteen lines later, at 0.37 MHz, above the prediction, without saying so. The sentence now defines S₀, quotes two significant figures, and states the exclusion's two-sigma strength together with the failing drop-4192 arm in the same passage, with its producer linked. No bound moved.

## The band-excess significance pair, 2026-08-24

Six earlier entries in this file quote the band-excess pair, 8.65 sigma on profile height and 3.6 sigma cubic-surviving, as live numbers, including a table that weighs 8.65 against the unrelated 9.41 figure. Those entries are dated and closed and hold only what was believed when written. The live values are 3.05 sigma and 1.4 sigma, given in the reconstruction entry above ("The band-excess construction was reconstructed, and the digits did not survive"), because the note's original construction is not recoverable from its prose.

## The 64 µm waist's provenance, 2026-08-24

docs/wiki/the-beam-waist.md described the 64 µm beam waist as a transfer across apparatus, with Nieddu 2019 measuring it and Rajasree 2020 reprinting it on a different laser five years later. It is a single same-bench Rajasree measurement, same optical table, laser and lenses, so the extra transfer uncertainty the page told readers to carry was never owed. No number moves. The correction rests on firsthand apparatus knowledge outranking a documented inference. The word that hid this, and three more like it, are banned from this corpus's prose by tests/test_prose_style_ratchet.py.

## Emphasis capitals in the corpus, 2026-08-24

The owner's rule bans all-capital emphasis words in this repository's prose unless they are required acronyms. A sweep found 3003 emphasis capitals across 130 tracked pages and lowered them. What stays capitalised is acronyms, the status vocabulary results ledgers are graded on (VERIFIED, REPORTED, CITE, FEED, BOUND, MEASURED, DIAGNOSTIC and siblings), provenance tags, underscored machine identifiers, atomic-state notation and document names.

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

## The v4.3 and v4.4 release pages, withdrawn and replaced 2026-08-26

The v4.3 page and the first v4.4 page, published on both repositories, are
withdrawn because both read as narratives with numbers naming no committed
file and terms a reader could not resolve, against the rules in
[RELEASE_NOTE_STYLE.md](../RELEASE_NOTE_STYLE.md), now enforced by
`scripts/check_release_notes.py`. A reconstructed v4.3 page and a
replacement v4.4 note, conforming to that style, stand in their place. The
v4.4 tag moves to the tree carrying this entry, with `CITATION.cff`
re-dated to match. No committed number changed. Release pages before v4.3
stand as published, as the record of what was said at the time.
