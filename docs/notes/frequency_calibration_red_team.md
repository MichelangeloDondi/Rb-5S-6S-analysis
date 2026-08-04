# The frequency-calibration red team

**Status: adversarial audit, run 2026-08-04 against the tree at commit
`6320903`, which is the state BEFORE the ruler-validity release.** Every
finding below carries five fields: the claim under attack, the instrument used
against it, the prior art the finding has to engage, the adversarial check run
on the finding itself, and a verdict of CONFIRMED, REFUTED or OPEN. Findings
that failed their own adversarial check are recorded as REFUTED and kept, not
deleted.

Seventeen findings are recorded across the nine targets, carrying twenty-one
verdicts because four of them split. Twelve verdicts are CONFIRMED, six are
REFUTED and three are OPEN. The six refutations are collected at the end so
that the next reader does not reopen them.

## Method, and one thing this note does not have

Eight of the nine targets need the seven fitted tooth heights per ruler trace.
`results/ruler_traces.csv` does not carry them. Rather than wait, the 104
canonical RF-on rulers were refitted in a scratch tree with the production
code path (`rb5s6s.ruler.fit_comb` under each block's own
`condition_noise_model` law, the same block grouping and the same hard-flag
skip that `scripts/run_ruler.py` applies). The refit reproduces every
committed `delta_ms` to zero difference and every committed block rate to zero
difference, so the height matrix used here is the production height matrix.
The 105th canonical ruler is the one `hard_flags` rejects as "no comb in RF-on
ruler", which the pipeline also drops.

**Persisting those heights in `results/ruler_traces.csv` is a separate piece of
work and lands separately.** Nothing in this note asserts that it has landed.

The refit was repeated at the end of the audit against a working tree in which
the validity stage was already being added, and it returned the same 104
spacings and the same 728 heights to zero difference, so the defaults do
preserve the committed behaviour and nothing here depends on which of the two
trees it is read against. The railed-height count is the same at a tolerance of
1e-6 and 1e-9, so it does not depend on where the rail threshold is put.

Scratch scripts and their outputs live outside the repository. Every number
below is reproducible from the committed pipeline plus the refit described
above.

---

## RT1. The fold-robustness paragraph, bounded

### RT1-A. The paragraph is right on a set twice as large as expected, and measure zero either way

**Claim under attack.** `docs/DATA.md` states that a retrace fold "preserves
the tooth spacing and only scrambles which tooth is which index n, never the
spacing that sets the rate".

**Instrument.** Algebra, then a synthetic scan. A symmetric triangle folding at
apex time `t_a` re-crosses a tooth at `t_k` at the time `2*t_a - t_k`. The
mirrored comb therefore has the same spacing and a phase offset of
`2*(t_a - t0)` relative to the real one. The two combs are commensurate, so
that every mirrored tooth lands exactly on a real grid slot, when
`2*(t_a - t0)/Delta` is an integer. That happens at apex phase 0, the apex
sitting on a tooth, and also at apex phase 1/2, the apex sitting exactly
halfway between two teeth. The scan injects a fold into a synthetic seven-tooth
comb at 16 apex phases under four height patterns and refits with production
`fit_comb`.

**Prior art engaged.** The plan's context bounds the paragraph by "the apex
lands on a tooth". That is half the benign set. The anti-node case is benign
for the same reason and the plan's bounded-claim test
(`test_apex_on_a_tooth_is_not_flagged`) should have a phase-1/2 twin, otherwise
the trimmer and the re-index ladder will fire on a configuration that costs
nothing.

**Adversarial check.** The commensurate phases are benign only if the residual
rate error there is small compared with the campaign precision. Checked
directly: at phase 0 and phase 1/2 the recovered rate is wrong by 0.026 to
0.157 per cent across the four height patterns, against 0.120 per cent quoted
precision. So the benign set is benign to about one quoted sigma, not exactly.
The residual comes from the doubled heights changing the effective weighting
and from one mirror falling partly outside the window.

**Verdict: CONFIRMED, with the benign set widened.** The paragraph is right at
apex phase 0 and 1/2 and wrong everywhere else. At the worst phase, near 0.16,
the recovered rate is wrong by between 4.7 and 8.6 per cent depending on the
height pattern (MEASURED-HERE, synthetic).

### RT1-B. The plan's stated sign for the fold bias does not hold

**Claim under attack.** The plan's context states that a mirrored peak in an
outer slot "biases the tooth spacing low and the sweep rate HIGH (the same sign
as addendum 19's +0.113 per cent five-to-seven correction)".

**Instrument.** The same apex-phase scan, reading the sign of the rate error at
each phase.

**Prior art engaged.** Addendum 19's correction is a genuine one-directional
truncation bias. The fold is a different mechanism and inherits none of that
directionality.

**Adversarial check.** Tested whether the sign is an artifact of where the apex
was placed. It is not a placement artifact, it is a phase effect: with the apex
two teeth to the right of the comb centre, phases 0.06 to 0.31 give a rate that
is too LOW by 0.3 to 3.8 per cent, and phase 0.44 gives a rate that is too HIGH
by 1.0 to 1.4 per cent under every one of the four height patterns tested. Both
signs occur under every pattern.

**Verdict: REFUTED.** The fold bias has no fixed sign. Any prose that pairs the
fold with addendum 19's sign, and any test that pins a bias DIRECTION for a
folded comb, has to name the apex phase it assumes. The plan's
`test_folded_comb_biases_delta_low` will pass or fail depending on the phase
its injector happens to use.

### RT1-C. There is no detectable fold anywhere in the canonical ruler archive

**Claim under attack.** That the archive contains folded rulers at a rate that
justifies a campaign-wide recompute.

**Instrument.** A matched-filter apex scan. For each trace, hold `t0`, `Delta`
and the tooth width at their fitted values, scan a candidate apex across the
central 70 per cent of the window in 4 ms steps, add one Lorentzian column per
mirrored tooth that lands inside the window, solve the whitened linear problem
for all heights plus a linear baseline, and take the largest chi-square drop
per added degree of freedom. Null calibration: the identical scan on
mirror-free synthetics built from each trace's own fitted model plus its own
residuals circularly shifted. Positive control: the identical scan on traces
with a fold injected at apex phase 0.125, refitted with `fit_comb` first so the
control sees the same wrong `Delta` the pipeline would have seen.

**Prior art engaged.** Addendum 19 withdrew an earlier retrace claim as a
threshold-peak-finder artifact. This instrument is a different class, which is
the plan's own argument for reopening the question, so it has to be able to
answer in either direction. It does: the positive control detects 58 of 104
injected folds.

**Adversarial check.** Three. First, the statistic could be dominated by model
mis-specification rather than mirrors, which is why the null is built from the
same fixed-parameter model and not from an idealised trace. Second, an earlier
version of this scan used a noiseless positive control and a null whose sigma
floor was wrong, which inflated the control's power by a factor of seven. Both
were fixed and the numbers below are from the corrected run. Third, the power
is only 56 per cent, so absence of detections bounds the fold fraction rather
than excluding it.

**Verdict: CONFIRMED as a bound, and it constrains the premise of the
recompute.** Real traces: median statistic 9.4, 90th percentile 37.0, maximum
399.4. Mirror-free null: median 11.7, 90th percentile 54.4, maximum 363.0. The
real population sits at or below the null at every quantile. Exactly 1 of 104
real traces exceeds the null 99th percentile of 285.1, against a chance
expectation of 1.0. With a detection efficiency of 0.558 against the injected
fold and a Poisson upper limit of 3.7 signal events on 1 observed over 1.04
background, the folded fraction of the canonical rulers is **below about 6 per
cent at 95 per cent confidence** (MEASURED-HERE). The single highest-scoring
trace is `rulers_t/4207nm_eom_110c2.csv`.

The same scan puts the trace fig8 currently selects,
`rulers_p/4207nm_eom_before5.csv`, at rank 11 of 104 with a statistic of 37.1
against the 285.1 threshold. Its residual carries no mirror signature.

### RT1-D. A fold that matters is invisible in the fit chi-square

**Claim under attack.** The implicit assumption that a bad comb fit announces
itself. The per-trace comb-fit `chi2_red` over the 104 canonical rulers runs
from 0.61 to 1.20, which reads as a clean population.

**Instrument.** Fold injection into the real traces, using each trace's own
residuals as the noise realization and its own block law as the weights, so the
resulting `chi2_red` is on exactly the scale the real traces are measured on.

**Prior art engaged.** A first pass of this check used noiseless synthetics and
reported fold chi-squares of 130 to 1500 against a real maximum of 1.20, which
would have made chi-square a sufficient guard and the whole recompute
unnecessary. That reading was wrong: with no noise the whitening sigma
collapses and the chi-square scale is meaningless.

**Adversarial check.** The corrected injection is the check. It reverses the
conclusion.

**Verdict: CONFIRMED, and it supports the plan.** At apex phase 0.125 the
injected fold moves the rate by a median of 5.87 per cent and leaves a median
`chi2_red` of 1.04, with 62.5 per cent of injected traces sitting at or below
the 1.20 that the real population maximum reaches. Of the 104 injections, 40
both move the rate by more than 0.5 per cent and stay under the RT1-C detection
threshold. Nothing currently in the pipeline would notice them.

---

## RT2. The k-labelling census on the persisted heights

### RT2-A. The census

**Claim under attack.** None yet. This is the measurement the other findings
are read against.

**Instrument.** The 104 by 7 height matrix from the refit.

**Prior art engaged.** `rb5s6s/constants.py` still describes a "5-tooth
pattern, weak outer teeth bracketing three strong inner teeth". That
description does not survive the census and is separately stale after addendum
19.

**Adversarial check.** A tooth whose centre falls outside the acquisition
window can rail at zero correctly rather than pathologically, so the railing
count was recomputed restricted to teeth inside the window. It does not change:
all 30 railed teeth are on in-window slots. A second check asked whether any
trace puts significant height on an out-of-window tooth, which would mean the
fit was using an unseen Lorentzian wing to model in-window structure. The
largest such fraction anywhere is 0.15 of the trace maximum, so it does not
happen.

**Verdict: CONFIRMED (MEASURED-HERE).**

| quantity | value |
|---|---|
| traces | 104 |
| tallest tooth is k = 0 | 33 |
| tallest tooth is k = plus or minus 1 | 45 |
| tallest tooth is k = plus or minus 2 | 26 |
| tallest tooth is k = plus or minus 3 | 0 |
| traces with at least one railed height | 29 (30 teeth) |
| all seven tooth centres inside the window | 92, the other 12 have six |
| k = minus 1 ranks fourth or worse | 42 of 104 |
| k = plus 1 ranks fourth or worse | 12 of 104 |

### RT2-B. The proposed top-three rule fails half the ruler population

**Claim under attack.** The plan's `top_three_verdict`, which passes a trace
only when the heights at k = minus 1 and k = plus 1 are both inside the top
three of the seven.

**Instrument.** The rule applied to the census, with the plan's own tie-break
and no tolerance.

**Prior art engaged.** The plan states the rule "deliberately does NOT require
k=0 tallest (suppressed carrier is expected physics)" and prescribes a test,
`test_clean_combs_all_pass_top_three`, asserting zero false positives across
the existing synthetics.

**Adversarial check.** Two, in opposite directions. First, false positives:
clean unfolded combs were generated with heights taken from the exact
two-photon law `J_k(2 beta)^2` and refitted. The rule passes at 2 beta = 0.6,
1.2, 1.74 and 2.4, and FAILS at 2 beta = 3.0, 3.8 and 5.0, because past the
first crossing of `J_1` and `J_2` near 2 beta = 2.7 the second-order teeth are
genuinely taller than the first-order ones. The spacing is recovered exactly
(147.000 ms against a truth of 147.000) in every one of those cases. Second,
false negatives: a folded comb with a 7.87 per cent rate error PASSES the rule
under the carrier-suppressed height pattern at apex phase 0.188.

**Verdict: CONFIRMED, and the rule is not fit for the job it is given.** Only
50 of 104 canonical rulers pass it. The rule is not specific, because the
repository's own amplitude law breaks it on clean combs at modulation index
above 2 beta of about 2.7. It is not sensitive either, because folds that cost
7.9 per cent in rate pass it. `test_clean_combs_all_pass_top_three` would pass
only because the existing synthetics happen to sit below that modulation index.
If the rule ships as written, the re-index ladder and the quarantine vocabulary
will be exercised on more than half the calibration set for reasons that are
not indexing.

---

## RT3. The Bessel amplitude law against the session heights

**Claim under attack.** Addendum 22's companion finding, that the tooth
amplitude law fits the temperature-session rulers reasonably and does not fit
the power-session bracket rulers at all, which is the stated basis for refusing
to license ruler traces as lineshape data.

**Instrument.** Two tests per trace. First, a one-parameter fit of
`A_k proportional to J_k(2 beta)^2` to the in-window heights, with the overall
scale solved analytically and beta profiled, reporting the root-mean-square
residual over the mean modelled height. Second, the law's parameter-free
prediction that the comb is symmetric, `h(+k) = h(-k)`, which needs no beta at
all.

**Prior art engaged.** Neither `results/` nor `scripts/` contains an artefact
of addendum 22's amplitude comparison. `results/amplitude_ratios.csv` is M10's
cross-peak line-area ratio table, a different quantity. The addendum's
statement is not reproducible from the committed record.

**Adversarial check.** The obvious objection is that pure phase modulation is
not expected to hold at all, because the 2025 setup admixed amplitude
modulation with a half-wave plate to suppress the optical carrier, and
`rb5s6s/constants.py` already names the resulting asymmetry. That objection is
correct and it cuts both ways: it predicts the law should fail on both
sessions, which is what the test finds, and it removes the ground for a
P-versus-T contrast. A second objection is that the k = plus or minus 3 heights
are poorly constrained, so the fit was restricted to in-window teeth.

**Verdict: OPEN, and the direction of the addendum's contrast is not
reproduced.** Median relative misfit is 61 per cent for the power session and
109 per cent for the temperature session. On the symmetry test the temperature
session is the WORSE of the two, median absolute k = plus or minus 1 asymmetry
0.387 against 0.193 for the power session (MEASURED-HERE). The refusal to
license ruler traces as lineshape data survives on the stronger ground that the
law fails on both populations. The specific P-versus-T claim needs a committed
producer before anything else leans on it.

---

## RT4. The absent free-centre spacing gate

**Claim under attack.** That `scripts/run_ruler.py` builds the sweep-linearity
map from adjacent free-centre pairs with no gate beyond `c2 - c1 > 0`, and that
this leaves the quoted 0.3 per cent bound exposed.

**Instrument.** The 399 adjacent free-centre pairs from the refit, gated at
seven thresholds on `|dc/Delta - 1|`, with the map rebuilt at each threshold
and the maximum well-sampled deviation and the chi-square against a flat sweep
recomputed. The ungated rebuild reproduces the committed
`results/ruler_nlmap.csv` to zero difference.

**Prior art engaged.** `tests/test_ruler.py::test_linearity_bound_matches_the_wellsampled_windows`
pins the bound inside (0.20, 0.30] per cent and names the four surfaces that
have to move together. `make_figures.N_WELL_SAMPLED = 19` defines the split.

**Adversarial check.** The check that matters is whether a gate is legitimate
at all. It is not. Because the local rate ratio is `Delta_block / dc`, gating on
`|dc/Delta - 1| <= g` is arithmetically a gate on the map value itself, so any
such gate censors the observable it is supposed to protect. That is visible in
the numbers: tightening to g = 0.03 discards 9 per cent of pairs and pushes the
maximum well-sampled deviation UP to 0.430 per cent, outside the quoted bound,
while the overall chi-square falls.

**Verdict: CONFIRMED that no gate is needed, REFUTED as a defect.** The pair
deviations have median 0.0074, 90th percentile 0.0265 and maximum 0.158, and
the inverse-variance weighting gives the tail no leverage. Gates from 1.00 down
to 0.05 leave the maximum well-sampled deviation between 0.241 and 0.249 per
cent, unchanged at the quoted precision. The absence of a gate is the correct
design and should be stated as a decision rather than left as an omission.

### RT4-B. The stdout nonlinearity verdict disagrees with the quoted bound

**Claim under attack.** `run_ruler`'s printed verdict, which computes the
chi-square against a flat sweep over all 12 map bins and prints "significant
curvature" above 3.

**Instrument.** The same rebuild, split by bin population.

**Prior art engaged.** The fig8 test's own reasoning, that "the sparse edge
windows cannot test a bound their own errors exceed", which is why the figure
draws them differently and excludes them from the bound.

**Adversarial check.** Asked whether the well-sampled restriction is
post-selection. It is not: the split is `N_WELL_SAMPLED = 19`, fixed in
`make_figures.py` and asserted in the test suite before this note existed.

**Verdict: CONFIRMED.** Over all 12 bins the chi-square per bin is 3.45, so
`run_ruler` prints "significant curvature". Over the 7 well-sampled bins it is
0.50, and a weighted straight line through them has a slope of 1.12 sigma,
0.279 per cent across the sampled span. The sweep is consistent with exactly
linear. The printed verdict is carried by the two sparsest bins, populated by 4
and 6 tooth pairs out of 399, which the figure and the test both exclude. **The
0.3 per cent is an upper bound set by the map's own errors, not a measured
curvature**, and the stdout line should say so.

---

## RT5. Rigid-grid bias under the measured sweep nonlinearity

This is the decisive target, so it is reported at length.

### RT5-A. The answer

**Claim under attack.** That fitting a rigid, uniform-in-time grid to a comb
whose teeth are uniform in FREQUENCY biases `Delta`, and therefore the campaign
rate, at or above the 0.120 per cent the rate is quoted to.

**Instrument.** Injection and refit. For each of the 104 traces, take its
fitted `t0`, `Delta`, width, seven heights and linear baseline, then re-place
the teeth so they are equally spaced in frequency under an injected rate
profile `r(t)`, anchoring k = 0 at the fitted `t0`. Every profile is normalised
to the same window-average rate, so the profiles differ only in shape. Refit
with production `fit_comb` under the block law and compare against the chord
rate over the comb span, `6 x 6.25 MHz / (t_+3 - t_-3)`.

Five profiles: flat as a machinery control, the committed
`results/ruler_nlmap.csv` point estimates interpolated in absolute window time,
a linear ramp of 0.3 per cent peak to peak, a quadratic bowl of 0.3 per cent
peak to peak, and the best-fit linear slope of the well-sampled bins.

**Prior art engaged.** RT4-B, which establishes that 0.3 per cent is the
envelope the data permit rather than a curvature the data show. Also
`docs/methods/05_the_frequency_ruler.md`, which already argues that everything
afflicting the line afflicts every tooth equally and that the free-centres map
bounds any tooth-dependent pull. That argument covers common-mode pulls. It
does not cover the estimator's response to a non-uniform grid, which is what
this target tests.

**Adversarial check.** Four.

1. *The injection is too kind, because a nonlinear sweep also changes each
   tooth's WIDTH in time.* Rerun with per-tooth widths scaled by `r0 / r(t_k)`,
   so the shared-width model is mis-specified in shape as well as in position.
   The answer moves by 0.0001 per cent.
2. *The result is a noiseless artifact.* Rerun with each trace's own residuals
   added. The flat control then shows a noise-induced floor of minus 0.0144 per
   cent, and subtracting that floor leaves the profile answers within 0.017 per
   cent of the noiseless ones.
3. *The full nonlinear fit could be doing something the mechanism does not
   explain.* Cross-checked with an analytic weighted straight-line fit to the
   tooth TIMES alone, weights proportional to the square of the height, which
   is what the comb fit reduces to. It reproduces the full-fit answer to within
   10 per cent of the answer in every profile.
4. *The scaling could be quadratic in the nonlinearity, in which case a 0.3 per
   cent envelope would be safe by construction and the finding would be
   vacuous.* Tested at 3 per cent. The bias grows by a factor 10.5 for the
   linear profile and 10.6 for the quadratic one, so the response is LINEAR in
   the nonlinearity amplitude and the answer scales.

**Verdict: CONFIRMED. A 0.3 per cent nonlinearity does NOT bias `Delta` at the
0.12 per cent quoted precision. The worst shape the data allow costs 0.052 per
cent, which is 0.43 of one quoted sigma** (MEASURED-HERE).

| injected sweep shape | rigid-grid bias in the rate | in units of the 0.120 per cent precision |
|---|---|---|
| flat, machinery control | plus 0.0002 per cent | 0.00 |
| committed nlmap point estimates | plus 0.0021 per cent | 0.02 |
| linear ramp, 0.3 per cent peak to peak | plus 0.0110 per cent | 0.09 |
| quadratic bowl, 0.3 per cent peak to peak | minus 0.0516 per cent | 0.43 |
| best-fit slope of the well-sampled bins | plus 0.0136 per cent | 0.11 |
| linear ramp, 3 per cent (scaling probe) | plus 0.115 per cent | 0.96 |
| quadratic bowl, 3 per cent (scaling probe) | minus 0.548 per cent | 4.56 |

The mechanism is worth stating because it explains why the two shapes differ by
a factor five at the same envelope. A linear rate gradient makes the tooth
times quadratic in the index n. A quadratic term is even in n and therefore
almost orthogonal to the slope the fit is estimating, so it survives only
through the height asymmetry, which is why the linear-profile answer is small
and its trace-to-trace scatter is comparatively large. A quadratic rate profile
makes the tooth times CUBIC in n. A cubic term is odd in n and not orthogonal
to the slope at all, so it biases `Delta` directly and consistently, which is
why the quadratic-profile answer is five times larger and its scatter is five
times smaller.

Two consequences follow. First, the margin is a factor of about 2.3, not a
factor of ten, so if the recompute tightens the rate precision as the plan
predicts, this term stops being negligible and has to be carried explicitly.
Second, a future sweep-linearity claim should bound the CURVATURE separately
from the slope, because the two cost very different amounts.

### RT5-B. A second channel, which is larger than the first and is uncorrected

**Claim under attack.** That the rigid-grid question is the whole of the
nonlinearity exposure.

**Instrument.** Measured positions. The height-weighted centroid of each ruler
comb, against the smoothed peak position of each of the 159 canonical RF-off
line traces.

**Prior art engaged.** `docs/methods/05_the_frequency_ruler.md` argues that
laser drift during a trace is "not a bias but part of the measured effective
rate", because the line fits use their own block's rate. That argument holds
for drift in time. It does not cover a rate that varies with position WITHIN
the window, because then the rulers measure the sweep where the combs are and
the lines are calibrated where the lines are.

**Adversarial check.** Whether the difference is significant. It is not. The
two bins of `ruler_nlmap.csv` that bracket the relevant positions carry errors
of about 0.17 per cent each, so the rate difference between the two positions
is 0.079 plus or minus about 0.16 per cent. The channel is bounded, not
detected. A second check asked whether the RF-off peak position is corrupted by
the known 4207 mirror crossing. The RF-off peak positions are tightly clustered
(inter-quartile range plus 34 to plus 60 ms), so the argmax is not landing on
mirrors.

**Verdict: OPEN, with a bound.** The ruler combs sit at a median window
position of plus 150 ms (inter-quartile plus 63 to plus 226). The RF-off lines
sit at a median of plus 40 ms (inter-quartile plus 34 to plus 60). The offset
is 110 ms and it is systematic, not random. Under the committed map the local
rate differs between those two positions by minus 0.079 per cent, which is 0.66
of one quoted sigma, bounded at about 1.3 sigma by the map's own errors
(ENVELOPE). Nothing in the repository carries this term. It is larger than the
rigid-grid bias RT5-A measures, and the v3.4.0 plan does not address it.

---

## RT6. Block combination with no outlier rejection at chi-square 8.1

**Claim under attack.** That the campaign rate, an inverse-variance mean over
20 blocks whose chi-square per degree of freedom is 8.078, is robust enough for
the 0.120 per cent it is quoted to.

**Instrument.** The same 20 block rates under five estimators: the published
inverse-variance mean, the unweighted mean, the median, an iterated 3-sigma
clip, and the session split.

**Prior art engaged.** Three pieces. `scripts/run_ruler.py` carries a comment
recording that a naive unweighted mean once drifted the headline to 0.04265
against the weighted 0.04257, so the estimator sensitivity is already known.
`scripts/make_results_ledger.py` already computes and prints the effect of
dropping the single largest outlier, so the leave-one-out is already in the
record. `docs/DATA.md` states that the blocks are NOT all consistent with a
single rate and that M3 therefore uses per-block rates.

**Adversarial check.** Three, and two of them soften the finding.

1. *The unweighted mean is a strawman.* Correct. Block errors span a factor of
   about 6 between warm and cold blocks, so ignoring them is not a fair
   alternative. The median is the fairer robust comparator and it moves the
   rate by a similar amount.
2. *The 3-sigma clip is the wrong remedy.* Correct, and this is the substantive
   objection. The clip drops 4 of 20 blocks including the 4207 after-bracket,
   and `docs/DATA.md` argues on independent grounds that the 4207 before-to-after
   shift is a real in-session rate change rather than an outlier. Clipping would
   discard physics.
3. *The campaign rate may not matter, because M3 uses per-block rates.* Partly.
   It is read by `run_laser_history`, `run_stark_centres`, `run_drift_settling`,
   `run_epoch_checks`, `make_figures` and `make_results_ledger`, so it is a
   working number in six places, not only a headline.

**Verdict: CONFIRMED as an estimator systematic, REFUTED as a call for outlier
rejection.** Against a published 0.04252649 plus or minus 0.00005101, which is
0.120 per cent:

| estimator | rate | shift from published |
|---|---|---|
| inverse-variance mean, published | 0.04252649 | reference |
| unweighted mean | 0.04261222 | plus 0.202 per cent |
| median | 0.04262519 | plus 0.232 per cent |
| iterated 3-sigma clip, 4 blocks dropped | 0.04257868 | plus 0.123 per cent |
| power session only, 8 blocks | 0.04250435 | minus 0.052 per cent |
| temperature session only, 12 blocks | 0.04263296 | plus 0.250 per cent |
| leave-one-block-out, full range | 0.04249 to 0.04256 | 0.153 per cent wide |

Three blocks pull by more than 3 sigma and the largest,
the 4207 after-bracket, pulls by 7.83 sigma. The point is not that the
published estimator is wrong. It is that the choice of estimator moves the
central value by up to 0.23 per cent, roughly twice the quoted uncertainty,
while the PDG inflation widens only the error bar and leaves the central value
at the least robust of the five. The session split alone is 0.30 per cent, 2.5
quoted sigma. The right remedy is to quote the estimator spread as a systematic
on the campaign rate, not to reject blocks.

---

## RT7. The power-session pathology rate, pre-registered

The three predictions and their reasoning were written down and timestamped
before any statistic was broken down by session. They are transcribed here
unedited, then the outcome.

### The pre-registration, written first

> Metric M1, indexing pathology: fraction of traces whose k = minus 1 and
> k = plus 1 heights are not both inside the top three of the seven.
> Metric M2, railed heights: fraction of traces with at least one fitted height
> at the zero bound. Metric M3, height asymmetry: median of
> `|h(+1) - h(-1)| / (h(+1) + h(-1))`.
>
> **M1: P greater than T, by at least a factor 1.5.** Reason: addendum 22 found
> the amplitude law fits the T-session rulers and fails on the P-session
> bracket rulers, attributed to the half-wave-plate carrier-suppression trick
> putting the P ruler light at a different polarization and power. A comb whose
> amplitude law is broken is a comb whose height ranking can put an outer tooth
> above an inner one, which is what M1 counts. The fig8 defect trace that opened
> this plan is a P-session trace.
>
> **M2: T greater than P, by more than a factor 2.** Reason: the cold 70 C
> rulers are T-session only and run at SNR 2 to 6. This prediction runs
> OPPOSITE to M1 on purpose: if both fire, the two metrics are measuring
> different things and neither is a proxy for the other.
>
> **M3: P greater than T.** Same reason as M1.
>
> Falsification: if M1 comes out T greater than or equal to P, the story that
> the fig8 defect is a P-session pathology loses its population-level support
> and the defect has to be argued trace by trace.

### The outcome

| metric | power session, n = 44 | temperature session, n = 60 | prediction |
|---|---|---|---|
| M1, top-three failure | 50.0 per cent | 53.3 per cent | REFUTED |
| M2, any railed height | 15.9 per cent | 36.7 per cent | CONFIRMED, factor 2.3 |
| M3, median k = plus or minus 1 asymmetry | 0.193 | 0.387 | REFUTED |

**Adversarial check.** M2's confirmation could be a temperature artifact rather
than a session artifact, so the temperature session was split: cold 70 C rulers
rail at 47.4 per cent and warm 90 and 110 C rulers at 31.7 per cent. The cold
subset is the worst, as predicted, but the warm temperature-session traces
still rail at twice the power-session rate, so low SNR is not the whole cause.
M1's refutation could be a power problem, but at 50 versus 53 per cent on 44
and 60 traces the two rates are not separable and the predicted factor of 1.5
is excluded.

**Verdict: two of three predictions REFUTED.** The falsification condition
fired. The top-three pathology is campaign-wide at about 52 per cent, not a
power-session specialty, and the k = plus or minus 1 asymmetry is larger in the
temperature session. The fig8 defect has to be argued as a property of that
trace, not as a draw from a pathological sub-population.

---

## RT8. The k-asymmetry as an amplitude-modulation probe

**Claim under attack.** `rb5s6s/constants.py`: "pure PM would give exactly
`A_k ~ J_k(2 beta)^2` with `A(+k) = A(-k)`, and the observed asymmetry is the
AM-admixture fingerprint".

**Instrument.** The asymmetry `A_k = (h(+k) - h(-k)) / (h(+k) + h(-k))`
regressed on the comb phase `(t0 - window centre) / Delta`, with a permutation
test on the correlation, at four margins requiring each tooth centre to sit a
given number of fitted widths inside the window edge.

**Prior art engaged.** The docstring above, and `docs/methods/05` which lists
sideband amplitude imbalance as absorbed by the free per-tooth heights so that
"amplitude never enters the spacing". The second statement is unaffected by
what follows. Only the attribution of the asymmetry is at issue.

**Adversarial check.** Two confounds and one exclusion.

1. *Window truncation.* A comb sitting right of centre has its plus-side teeth
   nearer the window edge, which lowers their fitted heights and manufactures a
   positive-to-negative asymmetry gradient. This is the confound the margin
   scan is for.
2. *Baseline slope.* The fitted linear background can trade against a
   left-to-right height imbalance. Correlation of `A_1` with the fitted slope
   is minus 0.194, weak against the minus 0.577 with comb phase.
3. *The k = plus or minus 3 asymmetry is not usable at all.* Median clearance
   from the window edge is 0.76 widths on the minus side and 1.31 on the plus
   side, and requiring one full width of clearance on both leaves 4 traces of
   104. Any k = plus or minus 3 statement rests on truncated teeth.

**Verdict: CONFIRMED that a phase-independent asymmetry exists, OPEN on whether
the phase-dependent part is instrumental.** At k = plus or minus 1 the mean
asymmetry is plus 0.151 (t = 3.91) and it correlates with comb phase at minus
0.577, permutation p below 1 in 8000. Regressing the phase out leaves an
intercept of plus 0.133 at zero phase, so a real asymmetry survives. At
k = plus or minus 2 the same picture holds, mean plus 0.281, correlation minus
0.557, intercept plus 0.252, and the intercept is stable at plus 0.243 when
every tooth is required to sit two widths inside the edge.

The open part is that the phase-dependent component is of the same size as the
phase-independent one, and the archive cannot say what it is. Window truncation
explains it. So does a real variation of laser intensity with scan position,
which would make the teeth genuinely unequal in a way that tracks where the
comb sits. All the traces share nearly the same acquisition window, so the two
are degenerate. **The constants docstring attributes the asymmetry entirely to
amplitude modulation, and about half of it tracks comb position instead.** The
k = plus or minus 3 contrast between sessions reported at margin zero (plus
0.293 power against plus 0.096 temperature) is withdrawn, because it rests on
teeth that are truncated by the window.

---

## RT9. The rf_on exclusion from the second-structure flag

**Claim under attack.** `rb5s6s/qc.py:346`, `if (not rf_on) and m["n_major"] >
1.5`, which excludes rulers from the second-structure flag without saying why.

**Instrument.** Read the code against its neighbours, then compute `n_major`
over all 264 canonical traces.

**Prior art engaged.** The three neighbouring gates in the same function each
justify their `rf_on` branch in a comment: the SNR gate explains that rulers
route to M2's pooled path, the baseline-slope gate explains that M2's per-trace
background absorbs the drift, and the wing-level-step gate explains that ruler
background integrity is checked model-aware in M2 instead. The second-structure
gate is the only one that takes the branch silently.

**Adversarial check.** The finding as first written was that removing the gate
would have caught the fold. That is wrong, and the metric says so. `n_major`
counts strongly smoothed local maxima with a hysteresis re-arm, and over the
105 canonical rulers it returns 3 for 88 traces, 2 for 16 and 1 for 1. It never
exceeds 3 despite seven real teeth, so it has no dynamic range on a comb and
cannot distinguish seven teeth from eight. Removing the gate would flag 104 of
105 rulers and inform nothing.

**Verdict: CONFIRMED as a documentation gap, REFUTED as a missed detection.**
The gate is inert rather than wrong. What is missing is the one-line reason its
three neighbours all carry. A ruler second-structure check is still worth
having, and it needs a statistic with range on a comb, which the RT1-C apex
scan supplies at a cost of about 0.1 second per trace.

One stale site found while reading this function and not on the plan's list:
the wing-level-step comment at `rb5s6s/qc.py:319` still says "the weak n=+-2
teeth sit INSIDE the signal-free mask". The weak teeth are n = plus or minus 3
since addendum 19. The plan's stale-prose sweep names `ruler.py`,
`constants.py`, `_m25_norulers.py` and `run_global_archive_fit.py`, and this
one belongs with them.

---

## What this says about the v3.4.0 plan

Three points, offered as findings rather than as instructions.

**The premise holds but the population is smaller than the plan assumes.** No
fold is detectable anywhere in the canonical ruler archive above the
mirror-free null, and the folded fraction is bounded below about 6 per cent
(RT1-C). At the same time a fold that costs 5.9 per cent in rate leaves a
`chi2_red` inside the range the real traces occupy (RT1-D), so the absence of
detections is not the same as safety and the validity work is warranted. What
is not warranted is prose describing the fold as campaign-wide.

**The proposed selection rule would do more harm than the defect it targets.**
`top_three_verdict` fails 54 of 104 canonical rulers, fails clean combs
generated from the repository's own amplitude law above 2 beta of about 2.7,
and passes a fold costing 7.9 per cent (RT2-B). Shipping it as the gate on
re-indexing, quarantine and fig8 eligibility would put the calibration set
through a ladder for reasons unrelated to indexing. The plan's predicted
outcome, that the top-three rule is a clean discriminator, is not supported by
the heights.

**Two systematics larger than the defect are left untouched.** The estimator
spread on the campaign rate is about 0.2 per cent, roughly twice the quoted
uncertainty, and the PDG inflation widens the error bar without moving the
central value off the least robust of five estimators (RT6). The ruler combs
calibrate the sweep 110 ms away from where the RF-off lines sit, worth up to
0.08 per cent under the committed map and bounded at about 0.16 per cent
(RT5-B). Both are larger than the rigid-grid bias this note was asked to
quantify, which is 0.052 per cent in the worst shape the data permit and 0.002
per cent under the map as measured (RT5-A).

## Ledger of refutations

Six findings were opened and then withdrawn or reversed by their own
adversarial check. They are listed so that the next reader does not reopen
them.

1. That the fold bias shares addendum 19's sign. Both signs occur, set by the
   apex phase (RT1-B).
2. That the comb-fit chi-square already protects against folds. That reading
   came from noiseless synthetics, where the whitening sigma collapses. At real
   noise the protection is absent (RT1-D).
3. That the fig8 trace puts its tallest fitted tooth outside the acquisition
   window. Its window runs from minus 104 to plus 895 ms, not the more common
   minus 448 to plus 551, and all seven teeth are inside. Across the archive no
   out-of-window tooth carries more than 0.15 of a trace maximum (RT2-A).
4. That the missing free-centre spacing gate is a defect. A spacing gate is
   arithmetically a gate on the map value, so it censors the observable, and
   the bound is stable without one (RT4).
5. That block combination needs outlier rejection. Clipping drops the 4207
   after-bracket, which DATA.md argues on separate grounds is a real in-session
   rate change (RT6).
6. That removing the `rf_on` gate on the second-structure flag would have
   caught the fold. The metric saturates at 3 on a seven-tooth comb (RT9).
