# How to read an uncertainty in this project

Every number here carries a grade and, where one is meaningful, an error. Two
vocabularies do that work, one for physical inputs and one for computed results,
and neither was written down in a place a reader would find until 2026-08-10.
This page is that place. It states what each tag licenses, which errors are
statistical and which are not, and where a stated uncertainty is deliberately
absent.

**The question.** What does a tag or an error column on a number in this
project actually license, and where is a stated uncertainty deliberately
absent rather than merely missing?
**Takes.** Nothing. This page is the reference the rest of the repository
points readers at.
**Gives.** The two provenance vocabularies, the five bound constructions and
when each is valid, what is mechanised, and what is not covered.
**Skip if.** You want the numbers themselves rather than what licenses them:
those live in [`RESULTS.md`](RESULTS.md) and the claim register in
[`CLAIMS.md`](CLAIMS.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 1. Physical inputs: the provenance tags in `constants.py`

Every constant carries one of these in its docstring. The definitions are the
module's own house rules, restated here so a reader need not open the source.

| tag | means | what it licenses |
|---|---|---|
| `ESTABLISHED` | a published or cited value, or an apparatus fact the experimenter verified from photographs, datasheets or direct confirmation | quotable as an input without further defence |
| `MEASURED-HERE` | extracted from the 2025 archival traces by this pipeline | quotable, but it inherits every conditionality of the fit that produced it |
| `CALCULATED` | derived; the derivation is stated where the value is first used | quotable if the derivation is quoted with it |
| `ENVELOPE` | order of magnitude only | may bound an argument, must never carry a published digit |
| `OPEN` | not settled | must never reach a published number |

Two of these are load-bearing in an unusual way. `ENVELOPE` is not a large error
bar, it is a statement that the quantity has no error bar worth quoting, so an
`ENVELOPE` input propagating into a result caps that result at `ENVELOPE` too.
And `OPEN` is a hard stop rather than a caution.

## 2. Computed results: the status column in `results/*.csv`

Every result row carries a `status`. The annotator refuses to write a row whose
quantity it has no mapping for, so this vocabulary is closed by construction and
a new quantity cannot ship untagged.

| status | means |
|---|---|
| `MEASURED` | a value with an error, from data, that the archive supports |
| `BOUND` | a one-sided limit. Not a measurement, and the construction matters, see section 4 |
| `NULL` | tested and not found, at a stated sensitivity |
| `PRELIM` | a real fit whose headline is not this file's to own, or which is conditional on an input the archive cannot pin |
| `CALIB` | an instrument calibration rather than a physics result |
| `DIAGNOSTIC` | an internal check, a count, a flag, or an error on another row. Never a result |
| `ENVELOPE` | as in section 1: an order of magnitude, re-derive before publication |
| `ARTIFACT` | identified as an instrumental or statistical artifact, kept so the identification stays visible. In the vocabulary and currently carried by no row: the one identified artifact, the shot-noise residual skew, is discussed in `RESULTS.md` C3c rather than tagged |

Counts across the ledger as of 2026-08-10: 3077 `DIAGNOSTIC`, 222 `PRELIM`, 208
`CALIB`, 139 `ENVELOPE`, 121 `BOUND`, 55 `MEASURED`, 21 `NULL`. The
preponderance of `DIAGNOSTIC` is expected and is not a weakness: most rows in
this ledger are checks, counts and errors-on-other-rows rather than results, and
the results are deliberately few.

**The rule a reader most needs.** A `DIAGNOSTIC` row is not a result, and no
reader-facing document should quote one as though it were. Several rows in the
ledger exist only to carry the uncertainty of a neighbouring row and are tagged
`DIAGNOSTIC` for that reason.

## 3. Where the error lives, and what kind it is

Uncertainty is stored three ways in this project, and the shape tells you the
kind.

**An `err` column** is a one-sigma error on the value in the same row. What it is
an error *of* is stated in that row's `unit` field, because the kinds genuinely
differ: `coverage.csv` carries binomial Monte-Carlo errors on a simulated
coverage fraction, `wavemeter_reconstruction.csv` carries a residual-bootstrap
standard error on a fitted noise floor, and the fit files carry the fit's own
parameter errors.

**An `err_lo16`/`err_hi84` pair** is a 16 to 84 per cent band from Monte-Carlo
draws over the inputs, used where the distribution is not symmetric and quoting a
single sigma would misrepresent it. `polarizability.csv` uses this throughout:
its bands come from drawing every matrix element, core and tail from its quoted
one-sigma and re-evaluating.

**A sibling row** whose quantity name ends in `_mc_err` is a Monte-Carlo error on
the row above it, used where the error is a property of the sampling rather than
of the physics. `fringe_tail.csv` uses this for all four of its pooled
quantities: each is estimated from the across-block scatter of sixteen
independent blocks, which is why it is zero when only one block is run.

**An `err_kind` column** names what the error is *of*, where the value's
uncertainty is dominated by something other than statistics. Two files carry it,
both from 2026-08-10, and they carry it because their two error bars are
different claims that a bare number could not distinguish.
`trapping_channels.csv` marks its halo rows `geometry`: the dominant unknown is
the standoff from the excitation region to the nearest way out, which was never
recorded, so the error is the spread over the 1 to 5 mm the record brackets and
not a repeatability. `blackbody_channels.csv` marks its shift rows
`polarizability`: that integral is converged, and what it is uncertain in is the
differential polarizability it integrates, so the error is the committed
`alpha_6s_static` band carried through rather than recomputed.

**And an `err_lo`/`err_hi` pair** where a range is not symmetric about the value
it belongs to. The halo rows use it: the point value sits at a 2 mm standoff
while the band runs over 1 to 5 mm, and since the halo is not linear in the
standoff the band is −0.58 and +0.78 about 1.07 at 130 °C. A single `err`
column stored half the range, which reconstructs [0.39, 1.75] where the interval
is [0.49, 1.85]. **The prose had it right and the machine-readable column had it
wrong**, which is the dangerous direction: a reader checking by eye would have
seen the correct band and a reader loading the CSV would not.

Three lessons from putting those bars on, all of which generalise. **A range
is not an error bar until you know the function is monotonic over it.** The halo
band was first taken at the two ends of the standoff range, and the halo is not
monotonic in the standoff, because below the Holstein cutoff the escape factor
is exactly one and the halo is exactly zero. At 90 °C that happens inside the
range, so the endpoint band excluded its own point value. It is sampled across
the range now, and `tests/test_radiation_environment_csv.py` checks that every
banded row brackets its own value. And **a number quoted in prose with no
producer is a defect even when it is right**: those numbers reached CLAIMS and
the methods chapters before either CSV existed, against this project's own rule
that prose quotes committed CSVs rather than restating them. And **a symmetric
error bar is a claim of symmetry**, which is a claim like any other and has to
be true. Where it is not, say both ends.

**A blank `err` is a claim, not an omission.** It says an error is not meaningful
for that row, and the row's `unit` field says why. Counts, flags and grid-read
sensitivities are the usual cases. A guard checks intervals rather than blanks,
see section 5.

## 4. Bounds: four constructions, and when each is valid

The project quotes several one-sided 95 per cent limits and they are not built
the same way. Quoting a bound without its construction is not reproducible, so
each site names it.

* **Profile likelihood**, the threshold at `dchi2 = 2.706`, scanning the
  parameter with all nuisances re-minimised at each point. This is the
  construction to prefer and the one the headline bounds use.
* **Profile likelihood with over-dispersion scaling**, the same threshold
  multiplied by the reduced chi-squared. Used where block-to-block scatter
  exceeds the per-point errors, which carries that scatter into the bound
  conservatively. It treats the over-dispersion as homogeneous, which it is not
  exactly, and a preregistered block bootstrap scored the construction rather
  than assuming it.
* **Linearised (Wald)**, value plus 1.645 sigma. **This one has a documented
  failure mode in this project and is retained only as a diagnostic**: where a
  fit rails at a boundary the width response has zero gradient there, so the
  finite-difference sigma is an artifact and the interval has no coverage. Every
  Wald number in the ledger sits beside the profile number that replaced it.
* **Bootstrap percentile**, used to score the constructions above rather than to
  produce a headline.
* **No bound at all, when the parameter is unidentifiable.** Not a fifth
  construction so much as the failure mode the other four share: every one of
  them assumes the profile has *some* slope in the parameter, and a parameter
  that enters the model only as a multiple of another parameter has none once
  that other parameter is itself consistent with zero. The preregistered
  companion refit hit this directly. Profiling the per-line pumping scale over
  the light shift it multiplies returns $\Delta\chi^2$ **exactly zero** at
  every scale from 0.5 to 16, because the fit sets the shift to zero and
  switches the scale's own effect off with it. There is no crossing to find,
  interpolate, or read off a grid, and reporting a bound anyway (by pinning the
  multiplying parameter at a value the data does not prefer) understates the
  problem rather than solving it. See
  [the refit's postscript](notes/companion_inclusive_refit_prereg.md) for the
  full profile and the general form of the failure.

### 4a. Reading a crossing off a grid, which is where two defects came from

Every construction above ends in the same small operation: a profile is
evaluated on a grid, and the edge is the point where it crosses a threshold.
That step went wrong twice in one day, both times in the direction that makes
an interval look better than the data support, so it is written out here rather
than left to the producer.

* **The edge is a crossing, not a membership test.** Taking the smallest and
  largest grid points that sit under the threshold reports the grid, not the
  likelihood, and where exactly one point qualifies it reports an interval of
  zero width (addendum 28).
* **Interpolate in the variable that is locally linear, which is not chi-square.**
  A profile is quadratic about its minimum, so a straight line drawn between two
  grid points reaches the threshold far too early. Interpolate
  $\sqrt{\Delta\chi^2}$ instead, which is linear on either side of a
  parabola's minimum. On the beta profile, where the neighbouring grid point sat
  561 above the threshold, the difference was a factor of 14.4 (addendum 30).
* **The grid has to be fine enough to see its own answer.** A step of 0.01
  cannot report an interval of width 0.001, and the minimum it reports is
  whichever grid point sat lowest rather than the minimum. Both arms of the
  archive fit now refine about the running minimum until the interval spans
  several steps, and write the step they resolved on into the CSV beside the
  interval.
* **The tell that needs no theory: an interval must contain its own point
  estimate.** Both defects above were visible without knowing either cause,
  because the file reported a best fit outside the interval three rows below it.
  That is now a guard.

### 4b. Reproducing a number is a question about an environment

The committed CSVs are checked against a fresh run of their producers. That
check had a flat tolerance until 2026-08-11, when raising the tested Python
version pulled in numpy 2.5 and four of sixteen files stopped matching. numpy
2.5 replaced the `np.convolve` implementation this whole lineshape model is
built on, and a different algorithm rounds differently.

**The committed digits were reproducible only near the numpy version that
produced them.** They still matched on 2.0 to 2.4 and failed on both 1.26 and
2.5. That is worth stating plainly rather than quietly widening a tolerance
until it stops complaining.

What the measurement showed is more reassuring than the failure suggested.
Re-running all sixteen producers and recording **every** differing column, 2421
moved at all and only six moved by more than 2 per cent. Those six are not
scattered: they are the Gaussian and exponential widths of the three-component
model form, and $\Delta\text{BIC}$. Both are quantities this record already refuses to
quote. The widths are the degenerate split that
[RESEARCH_DECISIONS.md](RESEARCH_DECISIONS.md) section 1 and
[fig10](../figures/fig10_degeneracy_vs_observable.png) exist to argue is not
physics, and $\Delta\text{BIC}$ is a difference of two BICs of order $10^4$, where
cancellation multiplies a $10^{-15}$ perturbation by $10^4$. Their
well-conditioned siblings, the total width and $\chi^2$, move by under 0.5 per
cent in the same runs, and every conclusion is unchanged.

**So the arithmetic is unstable exactly where the physics was already declared
unidentifiable**, and stable everywhere a number is quoted. The guard now
carries per-column tolerances that say which class each quantity is in and why,
rather than one constant that has to be loose enough for the worst case and is
therefore blind to the rest.

Two narrower lessons came out of the same pass. Whether a value counts as zero
is a question about its **column**, not an absolute threshold: the comb-tooth
amplitudes run from $10^{-37}$ to 0.3 and the ones below $10^{-10}$ are teeth
that are absent, whose remaining digits are optimizer noise, while the
blackbody channel rates are genuinely of order $10^{-12}$ and must not be
rounded away. And a number stored inside a text field cannot be compared as a
number: one file embedded its own effective sample size in a unit string, so a
count that moved by 2 in 13853 read as a changed label.

## 5. What is mechanised

Uncertainty handling is guarded, not merely documented.

* `tests/test_interval_sanity.py` refuses any committed interval whose upper edge
  does not exceed its lower edge, refuses one no wider than the grid that
  resolved it (reading that grid step from the producer's own CSV row rather
  than assuming one), and refuses any interval that does not contain its own
  point estimate at the same key in the same file. It exists because a 95 per
  cent interval once shipped with **zero width**, both edges having landed on
  the same grid point of a membership test that should have been a likelihood
  crossing, and because the interval that replaced it was still wrong in the
  same direction. Section 4a is the whole story.
* `scripts/annotate_results_status.py` raises rather than guessing when a result
  quantity has no status mapping, which is what keeps section 2's vocabulary
  closed.
* `tests/test_results_status.py` checks that every result file carries a
  provenance column at all, and that the statuses used are in the vocabulary.
* `tests/test_docs_canonical.py` pins the reader-facing numbers against the CSVs
  they come from, so a document cannot drift from its source.

## 6. What is not covered, stated rather than implied

**The waist conditionality is not a statistical error and is not in any `err`
column.** Every absolute result rides on the beam waist through the transit
width. The waist is a measurement on this apparatus lineage rather than a fit
output, so the results conditional on it are tagged `PRELIM` and the dependence
is mapped explicitly as a scan rather than propagated as a sigma. Read the
`w0_scan` rows of the joint-fit files to see how a result moves with it.

**Correlated inputs are not propagated as a covariance across files.** Several
results share the same few inputs, so their errors are not independent and
combining them in quadrature would understate the total. Where two results are
compared for consistency, the text says whether the comparison is independent by
construction.

**The `value` column is not always a number, and that is deliberate in every
case it happens.** A census on 2026-08-11 across all forty-six files found seven
rows whose `value` does not parse as a float, and they fall into two kinds. Four
are trace censuses written as one field, `100/59/46/26` and its siblings, which
say how many traces each session contributed and would lose their meaning split
across four columns. Three are a boolean or an absence, `False` and `none`,
answering a question that has no number. Neither kind is an error, and neither
carries an uncertainty, but a downstream reader parsing the column numerically
will meet them, so they are named here rather than discovered.

**Two files run their own status vocabulary and are outside the ledger's.**
`qc_metrics.csv` tags each trace with its role in the archive, `canonical` and
its siblings, which answers a different question from the eight words above, and
`laser_epoch.csv` likewise. Both sit in `annotate_results_status.py`'s skip list
by design, so a census of status words across the whole directory will report
them as violations and they are not.

**One quantity in the joint region is known to disagree with its own point
estimate**, `beta_self_joint` against `beta_self_min`, the second being the
minimum of a coarse two-dimensional grid and the first a direct fit. The gap is
the grid step and is not yet reconciled.

**One file used to sit outside all of this and no longer does.**
`results/laser_epoch.csv` carried its own header, a prose paragraph in the field
every other file uses for a status word, the inequality `<1.2` in a column the
rest of the ledger keeps numeric, and a transit width baked into a quantity name
to fifteen digits. It was normalised on 2026-08-10 to the shape above: the value
is a number, its one-sidedness is carried by the `BOUND` status where a reader
looks for it, and the waist label and transit width moved into the key and the
unit. It remains skipped by the status annotator because it writes its own
statuses, which are now drawn from the vocabulary in section 2.
