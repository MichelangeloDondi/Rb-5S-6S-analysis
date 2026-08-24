# Ruler fit validity and residual-tail trimming: specification of record

**Status: pre-registered 2026-08-04, before the code was written and before any
number came out of it.** Every threshold below is fixed here, with its
justification, so that the run can only confirm or fail it. No value in this
note was chosen after seeing a fit.

`provenance: results/ruler_campaign.csv` - The body thresholds are true preregistration and every one was confirmed present in `rb5s6s/config.py`, `rb5s6s/ruler.py` or `make_figures.py`. The eight dated amendments report outcomes, and the four quantities section 9 exists to police match this CSV exactly. **Ten claims remain unaccounted**, among them the Bessel inversion table, the cusum null calibration, the per-member estimator family and amendment 8's adjudication statistics, which live in an unpublished review rather than in `results/`. **10 numeric claims on this page remain unaccounted for.** Recorded by an audit that read every numeric claim on this page against `results/` and `scripts/`. See `docs/HISTORY.md`.


**The question.** How can the frequency ruler be wrong in a way the data can
detect, and what rule catches each way?
**Takes.** [methods/05_the_frequency_ruler.md](../methods/05_the_frequency_ruler.md).
**Gives.** The validity rules, the residual-tail trimmer, the quarantine
vocabulary and the amendments that record what each rule returned when run.
**Skip if.** You are not auditing the frequency axis. The opening table is the
current state of every rule if you want only that.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Producers: [`rb5s6s/ruler.py`](../../rb5s6s/ruler.py) and
[`scripts/run_ruler.py`](../../scripts/run_ruler.py). Outputs:
`results/ruler_traces.csv`, `results/ruler_blocks.csv`,
`results/ruler_campaign.csv`, `results/ruler_nlmap.csv`.

## Where each rule now stands

The sections below are the specification as first written. Seven amendments
follow it, each dated and each recording what the rule returned when it ran.
Where an amendment changed a rule, the amendment governs and the original
text is left in place rather than edited, so the record shows what was fixed
in advance of the data and what was fixed after it. A reader who wants only
the current state can read this table and the amendment named in it.

| rule | where it is fixed | what it now says |
|---|---|---|
| tooth-labelling test | section 2, amendment 5, correction gate in amendment 6 section F4 | both first-order teeth must rank in the top three by height. It is diagnostic and does not gate the spacing, on the measurement of section E2. It is not the gate on the drawn numbering either: a panel corrects its numbering when the second-to-first height ratio the fit produced is unphysical or displaced and a whole-slot shift brings that ratio into the measured band, with the recorded numbering shown alongside |
| the modulation index | amendment A2, criterion sharpened in amendment 5 section E5, measured cleanly in amendment 6 section F1 | a tooth height is a two-photon signal, so it goes as J_k(2 beta) squared, and inverting the second-to-first height ratio through that law gives 2 beta = 1.569 median over the 41 correctly numbered well-resolved combs, standard deviation 0.058, range 2 beta = 1.449 to 2 beta = 1.730. One drive depth to four per cent, and second-order teeth at 0.159 to 0.249 of the first order across it. Any depth below the crossing at 2 beta = 2.630 makes a second-order tooth taller than a first-order tooth impossible, which identifies 54 displaced grids. What varies instead is the carrier, from 0.360 to 1.188 of the first order, which is residual amplitude modulation and identifies nothing |
| the re-index ladder | section 3, amendment A4 | a relabelled fit is accepted only if it passes the test and its chi-squared stays inside a noise-aware ceiling. The ceiling was too tight by a factor of thirty in the first version and rejected correct relabellings |
| the residual-tail trimmer | section 5, amendments B1 and B5.2, read correctly in amendment 7 section G1 | a one-sided cumulative sum on signed smoothed residuals, with a hard core guard and a refusal that routes to quarantine rather than eating signal. It acted on two calibration traces and on no line fit. That census is a fact about the order of the guards, not about the data: the line fit sets its own window inside the retrace crossing, so a rising tail is already outside the fitted samples before the trimmer is asked. Line traces with such a tail exist |
| the outlier rule | amendment B4, recalibrated in amendment 3 | median and median absolute deviation, thresholds calibrated against forty million null draws rather than a t-quantile. It removes three calibration traces and no lines |
| the rate error | amendment B2 | 0.2046 per cent, from an eight-member estimator family rather than one estimator's formal error |
| eligibility for the ruler figure | section 7, amendment 4 | six of the seven teeth standing above the fit residual with none railed, after the original all-seven demand proved unsatisfiable for two measured reasons |
| licensing for the width-against-rate figure | section 8 | the 130 C block enters the fit, the morning pilot enters marked and outside it, the rehearsal and the calibration combs stay out with their reasons on the panel |

## 1. The defect this specification answers

![the modulated comb on one trace, with the fitted tooth grid over it](../../figures/fig8_ruler.png)

*The object this whole specification is about. Seven modulation sidebands at a
known spacing turn the oscilloscope's time axis into a frequency axis, one
trace at a time. Everything below is about the ways the fit that places them
can be right about the spacing and wrong about which tooth is which, and about
which of those ways the data can detect.*

The comb fit places seven tooth centres on a rigid grid at t0 plus k times
Delta, for k from minus three to plus three, and assigns k by proximity to the
window centre alone. Nothing checks that the peak sitting in a slot is the
tooth that belongs there.

The scan is a triangle. When its apex falls inside the acquisition window, the
retrace re-crosses the same frequencies in reverse and every real tooth
acquires a mirror image reflected about the apex. A mirror that lands in an
outer slot is fitted as if it were a tooth. Because the mirror of an inner
tooth lands at a radius smaller than the slot it occupies, the rigid grid
contracts to reach it, Delta comes out too small, and the sweep rate, which is
6.25 MHz divided by Delta, comes out too high. That is the same sign as the
five-to-seven tooth correction of addendum 19, and every frequency the
repository quotes inherits it.

Three properties of the current pipeline let this through. Tooth indexing has
no amplitude check. Rulers are excluded from the second-structure quality flag,
which was written here as the one flag that would see a retrace crossing and is
not (corrected 2026-08-06, below). The fitted tooth heights were never written
to disk, so no reader could audit the indexing after the fact.

**The second-structure flag, corrected 2026-08-06.** A comb stands three
structures above half maximum by construction, so at the flag's single-peak
threshold of 1.5 it fires on 104 of 104 fitted rulers, 44 of 44 power and 60 of
60 temperature, and identifies nothing. Excluding rulers from it is the right
call, not the opening this section first called it, and no hard flag reads a
metric that would have seen the crossing. The metric underneath the flag does
separate a fold once it is scaled to a comb: `n_major` above 3.5 fires on zero
of those same 104 rulers, whose n_major is 3 on 88 and 2 on 16, and catches 39
of 48 injected folds while staying blind at apex 0.8, which is a second
instrument agreeing with amendment A6. The reason now sits beside the exclusion
in `rb5s6s/qc.py`. Measured in RT9 of
the frequency-calibration review (amendment 8).

What this specification is not. It is not a claim that the campaign rate is
wrong by any stated amount. It fixes the tests and the remedies. What they
return is an outcome, and section 9 states in advance which outcomes stop the
work.

## 2. The top-three rule and its one tolerance

**The rule.** Rank the seven fitted heights, largest first. The fit passes if
the height in slot k equal to minus one and the height in slot k equal to plus
one both rank third or better.

**Why those two slots.** The two first-order sidebands are the brightest teeth
a phase-modulated comb produces at the drive depth used here, and they are
symmetric by construction. A mirror that displaces either of them from the top
three has taken a place that physics says belongs to a real tooth. The rule
therefore reads amplitude, which is the one thing proximity indexing never
consults.

**What the rule deliberately does not require.** It does not require slot zero
to be the tallest. The carrier was suppressed on purpose by tilting the
half-wave plate, so a carrier below its own neighbours is expected physics and
must not be read as a fault.

**The one tolerance.** `RULER_TOP3_TIE_SIGMA = 1.0`. If a required tooth ranks
fourth but its height sits within one fit residual standard deviation of the
third-ranked height, the fit is recorded as a marginal pass. One residual
standard deviation is the scale on which two heights are not distinguishable,
so a tolerance of one is the smallest defensible allowance and the only one
this specification grants. A marginal pass counts as a pass for the pipeline
and as a failure for figure eligibility (section 7).

**Railing is reported, never used as the test.** The count of heights sitting
at their lower bound of zero is written to the trace table as `n_railed`. A
railed slot is expected whenever a slot falls outside the acquisition window,
so the count is a diagnostic and not a pass criterion.

## 3. The re-index ladder and its cap

Applied in this fixed order, per trace. Each step runs only if the step before
it left the labelling test failing.

1. **Fit.** The existing constrained comb fit, unchanged.
2. **Trim.** Reserved for the residual-tail trimmer of section 5. Until that
   module lands, this step is a no-op and the trace passes through untouched.
3. **Labelling test.** The top-three rule of section 2.
4. **Phase shifts.** Refit with the comb phase seeded at t0 plus j times Delta
   for j in minus two, minus one, plus one, plus two. A shift is accepted only
   if the refit passes the test and does not raise the reduced chi-squared
   by more than `RULER_REINDEX_CHI2_TOL = 1e-3` of its own value. Among the
   accepted shifts the lowest reduced chi-squared wins. Both conditions are
   required because a re-index that rescues the test while worsening the fit
   has moved the labelling to a different wrong answer, which is the failure
   mode this ladder is most likely to produce.

   The tolerance is not slack, and its size is set by the structure of the
   problem rather than by preference. Relabelling a rigid grid by whole slots
   is reduced-chi-squared degenerate, because the same seven free heights
   describe the same peaks and only the slots that fall outside the acquisition
   window differ. On the closure synthetics the correct relabelling costs 1e-4
   of the reduced chi-squared, with a sign set by numerical noise, so a
   strict-improvement test would decide the right answer by coin flip and
   quarantine clean combs. The tolerance must also stay tight enough to reject
   a relabelling of a contaminated grid, which can satisfy the amplitude rule
   while keeping the contracted spacing that caused the failure. That false
   rescue costs 4e-3 on the same synthetics, and the excision step then
   recovers the true spacing. The threshold sits an order of magnitude from
   each. It is calibrated on synthetic traces with a known answer and on no
   campaign data.
5. **Excision.** Identify the outer slot, meaning any slot with k of magnitude
   two or three, whose height exceeds the weaker of the two first-order teeth.
   Where several qualify, take the tallest. Mask the samples within half a
   tooth spacing of that slot centre and pin the slot height to zero, so the
   excised region can be neither fitted nor absorbed into a neighbouring
   tooth's wings, then refit and re-test.
6. **Quarantine.** If the test still fails, the trace is quarantined with a
   reason from section 4.

Whether the ladder's answer is applied or merely recorded is a single switch,
`RULER_TOP3_GATED`, which lands off. Section 10 says why and what would settle
it. Everything in this section runs either way, so the population can be
studied without the test touching a number.

**The cap.** `RULER_REINDEX_MAX_TRIALS = 5`. Four phase shifts plus one
excision is five refits, which is the full ladder, so the cap forbids any
search wider than the ladder rather than truncating it. A trace that needs more
than the ladder offers is a trace whose indexing is not recoverable by
re-indexing, and the right record for it is a quarantine reason rather than a
deeper search.

**What a quarantined trace does and does not do.** It keeps its row in
`results/ruler_traces.csv`, with every fitted quantity and the reason. It
contributes nothing to a block spacing, nothing to the campaign rate, and
nothing to the sweep-nonlinearity map. Removing a trace from the calibration
while keeping its record is the only treatment that lets a later reader check
the removal.

**Trimming and quarantine never enter `hard_flags`.** The hard-flag text is
load-bearing for the archive-wide fit, whose first admission gate excludes any
non-second-structure hard-flag class outright. A trim is a remedy and a
quarantine is a calibration decision. Neither is an exclusion of a science
trace, and writing either into `hard_flags` would silently empty that gate's
census. This is a forbidden change, named here so that it stays visible.

## 4. The quarantine reason vocabulary

Controlled and closed. A trace carries exactly one of these tokens in
`quarantine_reason`, and the empty string when it is not quarantined. Adding a
token is a change to this note first.

| token | meaning |
|---|---|
| `top_three_unrecoverable` | the full ladder ran and the top-three rule still fails |
| `no_excision_candidate` | the test fails and no outer slot qualifies as a mirror, so there is nothing to excise |
| `refit_failed` | the optimizer failed inside the ladder, so no re-indexed fit exists to judge |

## 5. The residual-tail trimmer, proposed

This section fixes the trimmer's parameters in advance. The module itself would
land after the validity work, and nothing in it is exercised by the ladder
until then.

The trimmer would walk outward from a guarded core on each side of a fit window
independently and cut from a sustained onset of positive residual to the window
end. Five parameters, each fixed without reference to campaign data.

| parameter | value | where the value comes from |
|---|---|---|
| `TRIM_SMOOTH_W` | 21 samples | the boxcar width the quality module already uses, accepted rather than tuned |
| `TRIM_CUSUM_DRIFT` | 0.5 | the standard allowance of a one-sided cumulative-sum detector, in units of the residual standard deviation |
| `TRIM_CUSUM_H` | set by the null calibration of section 6 | a false-alarm rate, not a chosen number |
| `TRIM_MIN_RUN` | 40 samples | 20 ms at the campaign sampling interval, which is below the narrowest physical feature the apparatus can produce, so nothing physical can be cut by a run shorter than this |
| `TRIM_CORE_GUARD_FWHM_MULT` | 1.0 | one fitted full width at half maximum either side of the fitted centre is inviolable, so the trimmer can never reach the line it is protecting |

The detector runs on signed smoothed normalized residuals and accumulates only
positive excursions, because a mirror adds signal and a single spike cannot
accumulate the threshold. Refusing rather than eating is the standing rule: a
trim that would reach past half the distance from the core guard to the window
edge is not taken at all, and the trace is reported untrimmed.

## 6. The cumulative-sum null calibration

`TRIM_CUSUM_H` is to be set by simulation on pure noise, never by inspection of
a campaign residual. The procedure, fixed here:

1. Generate 10,000 synthetic traces containing the fitted model plus noise
   drawn from the measured noise law, with no mirror and no tail.
2. Run the detector on each.
3. Choose the smallest threshold at which the fraction of traces reporting any
   onset is at most one in 297.

One in 297 is one false trim across the whole archive, since 297 is the
manifest trace count. The construction follows the precedent already set for
the step-detection threshold in the quality module, so the archive carries one
calibration idiom rather than two.

## 7. Eligibility for the ruler figure

The current selection rule for the displayed ruler trace scores candidates by
the smaller of the two outermost heights divided by the residual standard
deviation. That rule rewards exactly the pathology of section 1, because a
mirror in an outer slot raises an outer height. It is to be deleted.

The replacement, fixed here. A trace is eligible only if all of the following
hold: the top-three test passes and is not marginal, the ladder took no
action, the trace is not quarantined, all seven fitted heights stand strictly
above the fit residual standard deviation with none railed, and the reduced
chi-squared is at most `RULER_FIG_CHI2_MAX = 2.0`. Eligible traces are ranked
by the smallest of the seven heights divided by the residual standard
deviation. A mirror cannot raise the smallest of seven heights, so the ranking
cannot be gamed by the defect the figure is being fixed for.

If the eligible set is empty, the figure is skipped and the reason is printed.
An empty set would be a finding about the ruler population, to be recorded
rather than worked around by loosening a threshold.

The empty set fired. Amendment 4 records the finding, the two measured causes,
and the decision to relax the height clause to six standing teeth. The
text above stands as written.

## 8. Licensing for the width-against-rate figure

Each point on that figure needs a licensed scan rate and a licensed width. The
decisions, fixed before the rebuild:

| source | rate | width | disposition |
|---|---|---|---|
| campaign 130 C, 20 traces | bracket rulers of its own session | retrace-safe contiguous span | enters the panel |
| morning pilot, 26 traces | its own 27 rulers, measured scale 1.0022(12) | single peak, contiguous | enters as a separately marked point with a horizontal count error bar, outside the fitted slope |
| rehearsal, 46 traces | fitted inside the joint fits, not measured | would inherit a fitted rate | stays out, with the reason printed on the panel |
| EOM ruler traces as lineshape data | measured | would need an amplitude model | stay out for this release |

The rehearsal decision follows the licensing rule rather than the instruction to
use all available data, and it stays open to revision. A width derived from a
rate that was fitted inside the same model is not model-independent, and the
rehearsal already enters the shift bounds where its rate is properly
marginalized.

The ruler decision keeps the standing refusal of addendum 22: the tooth
amplitude law does not close on the power-session ruler population, and
licensing calibration traces as lineshape data inside the release that found
their indexing broken would invert the burden of proof. The seven fitted
heights are persisted for the first time by this work, which is the dataset a
future amplitude model would be tested against, and the panel says so. The same
refusal is what keeps all 105 canonical ruler traces out of the census in
[the full-archive fit specification](full_dataset_fit_prereg.md), so the two
notes stand or fall together on it.

## 9. Predictions, and the conditions that stop the work

Each prediction is checked against the outcome before any number is written
into any document. They apply to a run in which the test is gating. While it
is recorded only, the calibration is unchanged by construction and there is
nothing to check.

| quantity | current committed value | prediction |
|---|---|---|
| campaign laser-axis rate `rate_laser` | 0.042526 MHz/ms | moves by less than about 0.2%, direction not predicted |
| block-to-block consistency `block_chi2_red` | 8.078 | falls |
| block rate spread `scatter_pct` | 0.618 | does not rise |
| 993.4207 nm before-against-after spacing separation | 3.7 standard deviations | shrinks |

The two consistency measures improve because a pathology that strikes some
blocks and not others is a source of block-to-block disagreement. The 4207 nm
separation shrinks because the power-session brackets are where the retrace
crossing was first seen in this archive. The size bound on the rate follows
from the fold rate: at most about 6% of rulers can be folded at 95%
confidence, so a per-trace effect of a few parts in a thousand cannot move a
20-block inverse-variance mean by more than a couple of parts in a thousand.

**The direction of the rate change is deliberately not predicted, and an
earlier draft of this note got it wrong.** That draft predicted a fall, on the
argument that the mirror of an inner tooth lands at a smaller radius than the
outer slot it occupies, so the grid contracts, the spacing falls and the rate
rises. The argument is sound for that apex phase and only for that apex phase.
A parallel measurement of injected folds across the full range of apex
positions finds both signs occurring, with the sign set by where the apex sits
relative to the tooth grid. A one-directional prediction was therefore a
statement about one extreme of the parameter space presented as a statement
about the effect. It is withdrawn here rather than quietly relaxed later, and
no number produced under it is quoted anywhere.

**Stop conditions.** If `block_chi2_red` rises, the work stops, because a
validity filter that makes the blocks agree less has removed
information rather than a defect. The same applies if `scatter_pct` rises, or
if the rate moves by more than the 0.2% bound above.

Nothing here is conditional on the beam waist, which stands open. The rate is a
frequency-axis calibration and does not read the waist. Every absolute width
downstream of it remains conditional on the waist exactly as before.

## 10. The open question

**Is the top-three rule the right instrument, and should it gate?** It lands
switched off, as `RULER_TOP3_GATED = False`. The full ladder runs, every
outcome is written to `results/ruler_traces.csv`, and none of it touches a
block, the campaign rate or the nonlinearity map. Three measurements are the
reason.

1. The rule fails 54 of the 104 fitted campaign rulers. An instrument that
   fires on half of a population is measuring the population, not a defect in
   it. The dominant cause is a whole-comb relabelling: the comb phase is folded
   to the tooth nearest the acquisition window centre, and when the comb is not
   centred in its window the labelling shifts by a slot without changing the
   spacing at all.
2. It fails clean synthetic combs built from the repository's own tooth
   amplitude law once the modulation index 2 beta exceeds about 2.7, where the
   second-order sidebands legitimately outrank the first. There the rule is
   contradicting known physics rather than detecting a fault.
3. A parallel measurement finds it passing an injected fold that costs 7.9% in
   rate, which is the case it was written to catch.

There is a second finding that bears on the ladder rather than the rule. On
`rulers_p/4154nm_eom_before_1.csv` the correct relabelling was rejected by the
chi-squared condition of section 3, because on real data a relabelling is not
as degenerate as it is on a synthetic. The excision step then ran and removed a
real first-order tooth. That ordering is safe only while the phase-shift step
reliably catches a relabelling, so the excision step and the chi-squared
tolerance would both be revisited before the test is allowed to gate.

Three courses are open: keep the rule and gate
on it, replace the gating instrument with one that separates a relabelling from
a mirror, or proceed as originally specified. Nothing in this landing forecloses
any of them.

---

# Amendment, 2026-08-04: the modulation index, and the ladder's acceptance ceiling

Everything above this line is the note as it landed. Nothing in it has been
edited. This amendment records a hypothesis raised after reading the
census, the measurements that test it, one code change it warranted, and the
gated trial rerun under that change. Where it contradicts the body, this
amendment is the later record and says so explicitly.

## A1. The hypothesis

The reading of the census in section 10 that this amendment tests is that the
population is not telling us about amplitudes at all. With the RF drive power
fixed for the whole campaign, the modulation index is one campaign constant.
The second-order teeth
can outrank the first only above the first crossing of the two Bessel weights.
If the campaign index sits below that crossing, then the 26 traces whose
tallest fitted tooth lands in a slot of order two are not combs with unusual
amplitudes. They are combs whose grid is labelled one tooth out by the fold to
the window centre in `estimate_t0`. On that reading the fault is in the fit, not
in the modulation, and the top-three rule is reporting it correctly.

## A2. The modulation index, measured

The comb amplitude law this repository already uses is `A_k` proportional to
`J_k(2 beta)^2` (`docs/PLAN.md` section 7). The two Bessel weights first cross
at `2 beta = 2.6299`, and below that value `J_1` exceeds `J_2` everywhere, so
below it the second-order teeth cannot outrank the first for any reason
internal to the modulation.

The index was fitted to the median normalized height profile of the
trustworthy population, meaning the 78 of 104 traces whose tallest fitted tooth
sits at k of zero or plus or minus one. Each trace was normalized by the sum of
its own in-window heights, so trace brightness drops out, and each slot's
median was taken over the traces where that slot lies inside the acquisition
window. One free amplitude scale, and in the second variant one further factor
on k equal to zero for the half-wave-plate carrier trick.

| variant | 2 beta | 68% interval | relative misfit |
|---|---|---|---|
| one amplitude scale | 1.464 | 1.434 to 1.505 | 5.8% |
| plus a free carrier factor | 1.619 | 1.594 to 1.644 | 2.8% |

Intervals are from 600 bootstrap resamples of the 78 traces. Not one resample
of either variant reached 2.6299. The fitted carrier factor is 1.57, meaning
the k equal to zero tooth stands above the pure phase-modulation prediction
rather than below it. That is recorded as a measurement and is not interpreted
here, since the half-wave-plate trick suppressed the optical carrier of the
ruler light and the two-photon k equal to zero tooth is not the same quantity.

**On the J2 question: J_2 cannot outrank J_1 at the campaign
modulation index.** The measured index is a factor of 1.6 to 1.8 below the
crossing, and the gap is 30 or more bootstrap standard errors. The section 10
objection that the rule "fails clean synthetic combs once 2 beta exceeds about
2.7" is a true statement about the rule and an irrelevant one for this
campaign, because this campaign did not run there.

One independent check, stated with its assumption because the assumption is not
verified. `docs/APPARATUS.md` section 2 puts the campaign drive at 10.00 Vpp,
which the manufacturer certificates place at 54 to 60 per cent of full
modulation, and notes that the phase-modulation index scales as one over the
wavelength so the index at 993 nm is about 0.79 of the 780 nm figure. If full
modulation on those certificates means a half-wave retardation, beta of pi over
two, then the campaign index is about 2 beta equal to 1.4. That is consistent
with the measurement above. It is corroboration and not evidence, because the
reading of "100% modulation" has not been confirmed against the certificate.

## A3. The post-relabel census

Each of the 26 traces whose tallest tooth is at order two was refitted with the
comb phase seeded at t0 plus j times Delta for j of minus two, minus one, plus
one and plus two, and the amplitude rule was applied to each refit.

| quantity | before | after |
|---|---|---|
| tallest tooth at order one | 0 | 24 |
| tallest tooth at order two | 26 | 0 |
| tallest tooth at order three | 0 | 2 |
| top-three test PASS | 0 | 26 |
| top-three test FAIL or marginal | 26 | 0 |

Every one of the 26 is rescued by a phase shift, and every accepted shift is by
exactly one slot, 21 at j equal to plus one and 5 at j equal to minus one, with
the sign always matching the sign of the tall slot. A population of genuine
amplitude anomalies has no reason to be rescued by a single slot in the
direction of its own anomaly, every time, in 26 of 26 cases.

The median profiles say the same thing without any fit. Slots run from k equal
to minus three to plus three.

| population | k=-3 | k=-2 | k=-1 | k=0 | k=+1 | k=+2 | k=+3 |
|---|---|---|---|---|---|---|---|
| trustworthy, 78 traces | 0.008 | 0.058 | 0.300 | 0.281 | 0.289 | 0.064 | 0.009 |
| tallest at plus two, 21 traces | 0.008 | 0.004 | 0.060 | 0.309 | 0.210 | 0.322 | 0.067 |
| the same, relabelled by plus one | 0.004 | 0.060 | 0.309 | 0.210 | 0.322 | 0.067 | none |
| tallest at minus two, 5 traces | 0.067 | 0.339 | 0.209 | 0.322 | 0.062 | 0.004 | 0.004 |
| the same, relabelled by minus one | none | 0.067 | 0.339 | 0.209 | 0.322 | 0.062 | 0.004 |

Relabelled by one slot, both suspect subsets reproduce the trustworthy profile
slot for slot outside the carrier. They differ from it only at k equal to zero,
0.21 against 0.28, which is a deeper carrier suppression. That is the expected
direction: the more the carrier is suppressed, the less reliably the fold to
the window centre lands on it.

**The hypothesis is confirmed.** These 26 traces are mislabelled grids.

Two of the 26 land with their tallest tooth at order three after the shift, and
both carry an implausible height in that outer slot. The amplitude rule passes
them anyway, because it reads only the two first-order slots. That is a real
limit of the rule and it is why the acceptance ceiling below still has work to
do.

## A4. The ladder fix

Section 10 recorded that on `rulers_p/4154nm_eom_before_1.csv` the correct
relabelling was rejected by the chi-squared condition and the excision rung
then removed a real tooth. Both halves are confirmed, and the diagnosis is
below.

**The tolerance was calibrated on a case that cannot show the cost.** Section 3
argues that a whole-slot relabelling of a rigid grid is chi-squared degenerate.
That is true when the slots the relabel gains and loses are empty. The closure
synthetics put five teeth in a seven-slot grid, so a one-slot shift exchanges an
empty slot for an empty slot and costs nothing. Campaign combs populate all
seven slots, and the comb spans 882 ms in a 999 ms window, so a one-slot shift
always exchanges a populated slot for one that is partly outside the window. Over
the 26 mislabelled campaign traces of A3 the correct relabelling costs a median
of 6e-4 of chi2_red and reaches 5.8e-1. The tolerance of 1e-3 accepted 13 of
those 26 relabellings and rejected the other 13.

**The tolerance was also stated in the wrong units.** A reduced chi-squared on
`dof` degrees of freedom has standard deviation `sqrt(2/dof)`. On the campaign
geometry, 2000 samples and twelve free parameters, that is 0.032. A tolerance
of 1e-3 of chi2_red is about thirty times tighter than the noise on the very
quantity it tests, so it was rejecting refits that no measurement could call
worse. On `4154nm_eom_before_1` the correct relabelling costs 0.71 of one such
standard deviation.

**The ordering is not wrong, and the obvious ordering fix is wrong.** Blocking
the excision rung whenever any phase shift passes the amplitude rule was tried
and it breaks fold recovery. On the ladder's own fold injector at apex 0.8 a
phase shift does pass the amplitude rule while keeping a spacing of 131.9 ms
against a truth of 147.3 ms. The chi-squared condition is what rejects it, and
the excision rung is what then recovers the true spacing on all eight seeds.
Spacing preservation was also tried as a replacement acceptance test and it
does not separate either, because the false rescue on a folded comb preserves
the contracted spacing by construction.

**What is wrong in the ordering is that the destructive rung was the only
unguarded one.** The phase rung carried a chi-squared condition. The excision
rung, which deletes samples and pins a slot to zero, carried none. So a
relabelling rejected for costing 0.71 standard deviations fell through to a
rung that deleted a tooth of 36.5 fit residual RMS and worsened chi2_red by
13.6 standard deviations, and nothing in the ladder objected.

### The change

Two lines of substance in `rb5s6s/ruler.py`, and no change to the rung order.

1. The acceptance ceiling becomes `chi2_red` of the first fit plus
   `REINDEX_CHI2_NSIGMA` times `sqrt(2/dof)`, with the original
   `C.RULER_REINDEX_CHI2_TOL` retained as a floor so the change can only ever
   widen the acceptance and never narrow it. `REINDEX_CHI2_NSIGMA = 1.0` is
   pre-registered here.
2. The same ceiling now governs the excision rung.

`REINDEX_CHI2_NSIGMA = 1.0` is not a tuned number. One standard deviation of
the reduced chi-squared is the scale on which the question "is the relabelled
fit worse" is answerable at all, and one of it is the whole of it.

`rb5s6s/config.py` was outside the scope of this amendment, so
`RULER_REINDEX_CHI2_TOL` keeps its value of 1e-3 and its docstring still
describes the replaced ceiling. That docstring needs correcting and is left
flagged rather than silently fixed.

### Its calibration, on synthetics only

| population | n | cost of the accepted refit, in sqrt(2/dof) |
|---|---|---|
| A. clean one-slot mislabel, seven populated teeth | 48 | median 0.00, max 0.06 |
| C. clean five-tooth closure combs | 13 | median 0.00, max 0.04 |
| B. folds at apex 0.6, 0.8 and 0.9, the false rescue that must be rejected | 24 | median 2.41, max 8.13 |
| B. folds at apex 0.8, the excision that must be accepted | 8 | minus 85 to minus 96 |

One standard deviation sits a factor of 16 above the largest clean relabelling
cost and a factor of 2.4 below the median false-rescue cost. The clean side is
comfortable and the fold side is not, and that asymmetry is stated rather than
hidden. The fold side is carried by the excision rung, which on the same
injector improves chi2_red by 84 to 96 standard deviations, so guarding it
costs nothing there while blocking it on a clean comb where it would delete
signal.

The regression case is synthetic and its answer is known. Of 336 clean
seven-tooth combs placed around one spacing off the window centre, 23 had their
correct relabelling rejected by the old tolerance, fell through to excision, and
had a real first-order tooth of 22 to 23 fit residual RMS deleted at a
chi-squared cost of 1.2 to 5.5 standard deviations. Six of
those 23 are pinned in `tests/test_ruler.py` as
`_OLD_TOLERANCE_CASUALTIES`, with three new tests covering the ceiling, the
excision guard, and the widening-only property.

### What the fix does to the campaign census

Ungated, over the same 104 traces. The fit of record is unchanged, byte for
byte, which was checked.

| quantity | before the fix | after the fix |
|---|---|---|
| ladder action none | 60 | 60 |
| ladder action phase_shift | 30 | 44 |
| ladder action excision | 14 | 0 |
| quarantine advised | 8 | 8 |

Excision now fires on no campaign trace at all. Every campaign trace the old
ladder excised was a mislabelled grid, not a mirror. The advised quarantine
count is unchanged at 8, but four traces leave that list and four different
ones join it.

### What the fix does not do

A pure relabelling should not move the spacing at all. Across the 44 accepted
relabellings the spacing moves by a median of 4.7e-4 and by 2.5e-3 at the 90th
percentile, which is consistent with a refit of the same peaks. One trace,
`rulers_p/4121nm_eom_after3.csv`, moves 1.49 per cent, lands with its tallest
tooth in the outer slot at order three, and is accepted because its chi2_red
improves. The amplitude rule reads only the two first-order slots, so it cannot
see an implausible outer height, and the chi-squared ceiling only bounds
worsening. Two of the 26 traces in A3 fail this way. That is a known residual
limit of the ladder as it now stands, it affects a small number of traces, and
it is left recorded rather than patched with a third condition that has no
calibration behind it.

### What the committed tables have to do about it

`results/*.csv` were left untouched by this work and were verified
byte-identical afterwards. That leaves them stale against their own producer,
so `tests/test_results_fresh.py::test_committed_csvs_still_match_their_producers`
fails under `--runslow` until the producer is re-run and the status column is
re-annotated. The default suite is unaffected, since that test is slow-gated.
Every other test passes, 1470 of them.

Only `results/ruler_traces.csv` moves, and only in its ladder-diagnostic
columns. `reindex_action` and `delta_advised_ms` change on 18 rows,
`reindex_j`, `excised_k` and `n_refits` on 14, `quarantine_advised` and
`quarantine_reason` on 8. `ruler_blocks.csv`, `ruler_campaign.csv`,
`ruler_nlmap.csv` and `ruler_rate_model.csv` are unchanged in every cell,
which is the check that the fix moves no physics while the test is advisory.
Regenerating the tables is a separate commit, not one this work makes on
its own account.

## A5. The gated trial, rerun

One gated trial was run with every output redirected to a scratch directory.
The committed `results/*.csv` were hashed before and after and are unchanged.
The pre-fix ladder was reconstructed and run the same way, so the earlier
trial and the new one are comparable line by line.

| quantity | committed | prediction of section 9 | gated, old ladder | gated, fixed ladder |
|---|---|---|---|---|
| `rate_laser` | 0.042526 | moves less than about 0.2% | 0.042544, plus 0.042% | 0.042535, plus 0.019% |
| `block_chi2_red` | 8.078 | falls | 6.439 | 7.755 |
| `scatter_pct` | 0.6176 | does not rise | 0.6524, rose | 0.6058 |
| 4207 before against after | 3.7 sigma | shrinks | 6.2 sigma | 5.6 sigma |

**None of the three stop conditions of section 9 fires under the fixed
ladder.** The rate moves by a tenth of its bound, the block consistency
improves, and the block rate spread falls instead of rising. The scatter rise
that stopped the earlier trial goes away exactly when the excision rung stops
firing. The two runs differ in no other mechanism, and on the one case examined
in detail the excision deleted a first-order tooth of 36.5 fit residual RMS, so
the rise is read here as the excisions and not as the labelling test.

**The fourth prediction fails, and it is the one tied to the defect.** Section 9
predicted the 4207 before-against-after separation would shrink, on the ground
that the power-session brackets are where the retrace crossing was first seen.
It grows from 3.7 to 5.6 standard deviations. The mechanism is visible in the
blocks. Gating quarantines `rulers_p/4207nm_eom_before5.csv`, whose spacing of
145.40 ms sits about 1% below its own block, so the before bracket moves from
146.35 plus or minus 0.34 ms on five traces to 146.79 plus or minus 0.26 ms on
four, and the separation widens because the mean rose and the error fell. That
is not a retrace crossing being removed. It is one discrepant trace being
removed, and it moves the number the wrong way.

## A6. The recommendation on gating, revised

**`RULER_TOP3_GATED` should stay False for this release. The ladder fix should
land regardless.** These are separate decisions and the reasons differ.

The ladder fix lands because it is a correctness fix to a destructive rung, it
is calibrated on synthetics with known answers, and while the test is not
gating it changes no number in the repository. That was verified rather than
assumed.

Gating stays off for three reasons, and two of the three arguments in section
10 are now withdrawn.

Withdrawn. The first was that the rule "fails 54 of 104, so it is measuring the
population". It is not. Of the 52 failures, 44 are relabelled by a one-slot
comb-phase shift, and gated the census is 93 PASS, 3 marginal and 8 FAIL. An
instrument that fires on 8 per cent of a population is a plausible defect
detector. The second was that the rule "fails clean combs above 2 beta of about
2.7". True of the rule, and irrelevant here, because section A2 measures the
campaign index at 1.62 and the crossing is at 2.63.

Standing. The third argument survives untouched and it is the decisive one. A
parallel measurement finds the rule passing an injected fold that costs 7.9 per
cent in rate. The rule is not sensitive to the defect it was written for, and
gating on an insensitive instrument buys the appearance of a validity filter
without the substance of one. Two further findings point the same way. The
excision rung, which is the only rung that reads the mirror hypothesis at all,
now fires on zero campaign traces, so the whole effect of gating is eight
quarantines decided on amplitude alone. And the one prediction tied to the
defect's expected location fails, in the direction that says the traces being
removed are discrepant rather than folded.

What gating would buy is small and is now on the record: the rate moves 0.019
per cent, `block_chi2_red` falls from 8.078 to 7.755, and `scatter_pct` falls
from 0.618 to 0.606. What it costs is eight traces removed from the calibration
on a criterion with an unmeasured false-negative rate for the defect it names.
That exchange does not favour gating today.

What would settle it is a sensitivity measurement rather than another
threshold. The rule needs to be shown to fire on injected folds across the full
range of apex positions, at the fold rate the archive actually supports, before
it decides which traces enter the frequency axis. Until then the ladder should
keep running and keep recording, which is what it does.

## A7. What changed in this note, and why

Section 3's justification for `RULER_REINDEX_CHI2_TOL` is replaced by A4. The
degeneracy argument in it is correct and the calibration behind it is not,
because the synthetics it was measured on cannot exhibit the cost. The number
1e-3 was not wrong by preference, it was measured on a case where the answer is
zero.

Section 10's first two reasons for landing the test ungated are withdrawn in
A6. Both were about the top-three rule firing too often, and both dissolve once
the modulation index is measured and the ladder stops mistaking relabellings
for mirrors.

Section 9's fourth prediction is recorded as failed in A5 rather than
reinterpreted. It was not a stop condition and the work does not stop on it,
but a prediction that fails is a prediction that failed.

Section 10's request that "the excision step and the chi-squared tolerance
would both be revisited before the test is allowed to gate" is discharged by
A4. The tolerance was revised, the excision step was guarded, and the test
is still not gating.

---

# Amendment 2, 2026-08-04: the trimmer lands, the rate error gains an estimator spread, and one outlier rule

Everything above this line stands. Sections B1 to B4 below were written before
any of the code they describe existed, and no campaign number was consulted
while they were being fixed. Section B5 records what the rules returned once
they were run, and is the only part of this amendment written after the fact.

## B1. Where the trimmer is allowed to act

Section 5 fixed the trimmer's five parameters and section 6 fixed the
calibration that sets the sixth. Neither changes. What this section fixes is
the three places the module is wired in, and what each one may do.

The module is `rb5s6s/trim.py` and it has three functions. `cusum_onset` runs a
one-sided cumulative sum on signed smoothed normalized residuals and returns
the sample at which a sustained positive excursion begins, or nothing.
`tail_trim` walks outward from a guarded core on each side of a window
independently and turns an onset into a sample mask. `envelope_residual` builds
a residual without fitting a lineshape, so the quality pass stays physics
blind.

**Sustained means the accumulation lasts, not that it is large.** A run is
accepted only when the cumulative sum keeps rising for at least `TRIM_MIN_RUN`
samples after the onset. A point glitch is spread over `TRIM_SMOOTH_W` samples
by the smoother and can therefore accumulate for at most that many, which is
below the minimum run whatever the glitch's height. That is what makes the
detector immune to a spike rather than merely resistant to a small one, and it
is the property the spike test pins.

The three integration points.

1. **The ruler ladder.** Inside `validated_comb_fit`, between the first fit and
   the labelling test, exactly where section 3 reserved rung 2. The core is the fitted
   comb span, meaning the outermost fitted tooth centres, widened by
   `TRIM_CORE_GUARD_FWHM_MULT` fitted widths on each side. A trim triggers one
   refit through `fit_comb(mask=...)` and the trimmed fit becomes the fit the
   test judges.
2. **The condition fit.** `fit_condition` gains `trim_tails`, applied as a
   single second pass after the existing per-trace residual loop, with one
   refit. The adaptive fit window is unchanged, and the mirror-exclusion test
   that window exists for must keep passing.
3. **The quality pass.** `trace_metrics` gains `rf_on` and reports `trimmed`,
   `trim_start_ms`, `trim_end_ms` and `trim_reason` from `envelope_residual`.
   For a ruler it reports `not applicable, multi-peak trace` and computes
   nothing, because the ruler's authoritative trim record lives in
   `results/ruler_traces.csv` and two disagreeing records of the same decision
   are worse than one.

`trim_start_ms` and `trim_end_ms` bound the kept interval, in both tables, so
there is one convention in the repository rather than two. They are empty when
nothing was trimmed.

**The trim never enters `hard_flags`.** Section 3 already forbids this and the
prohibition is repeated here because this amendment is the one that writes the
code.

## B2. The estimator family behind the campaign rate

`results/ruler_campaign.csv` quotes one central rate and one error. The error is
the inverse-variance error with the standard scatter inflation, which is the
spread of the blocks about their own weighted mean. It says nothing about the
choice of estimator, and the choice of estimator is a real degree of freedom
that a reader cannot see.

Eight members, fixed here, all computed from the same block table.

| member | what it is |
|---|---|
| `invvar_pdg` | inverse-variance mean with scatter inflation, the central value, unchanged |
| `unweighted` | plain mean of the block rates |
| `median` | median of the block rates |
| `clipped3` | mean after iteratively dropping blocks more than three sample standard deviations from the running mean |
| `P_only` | inverse-variance mean over the power-session bracket blocks alone |
| `T_only` | inverse-variance mean over the temperature-session dwell blocks alone |
| `loo_min` | smallest of the leave-one-block-out inverse-variance means |
| `loo_max` | largest of the same |

Each asks a different question. The unweighted mean and the median do not read
the per-block errors at all, which matters because those errors are inflated
twice. The clipped mean asks whether one block carries the answer. The two
session splits ask whether the two acquisition epochs agree. The leave-one-out
range asks whether any single block is load bearing.

`rate_est_spread` is half the range of the eight. `rate_err_total` is
`rate_est_spread` and the existing `rate_laser_err` added in quadrature. Half
the range is the standard way to turn a family of estimators into a one-sigma
scale without asserting a distribution over estimators, and it is deliberately
crude, because the statement that holds is a size and not a probability.

## B3. The ruler-against-line position mismatch

The frequency axis is measured on ruler traces and applied to line traces. The
sweep is not exactly linear, and `results/ruler_nlmap.csv` measures the local
rate against position in the acquisition window. If the rulers and the lines sit
at different window positions then the rate measured on one is not the rate that
applies to the other. Nothing in the repository has carried that difference.

The rule, fixed here.

1. The ruler position is the count-weighted median of `pos_ms` over the map's
   own bins, which is where the campaign rate was measured.
2. The line position is the median `peak_pos_ms` over the canonical radio
   frequency off traces of `results/qc_metrics.csv`, which is where the lines
   sit.
3. The local relative rate at each position comes from linear interpolation of
   `rate_rel` against `pos_ms` in the map, and its error from the same
   interpolation of `rate_rel_err`.
4. `position_mismatch_relerr` is the larger of the absolute difference between
   the two interpolated rates and the quadrature sum of the two interpolated
   errors.

Taking the larger of the two refuses to quote a mismatch finer than the map's
own resolution. The quantity is a relative error, so it is dimensionless and
adds to the other fractional terms directly.

**Who consumes it.** `load_block_rates` in `run_linefit.py` and `load_t_rates`
in `run_beta_self.py` build a per-block relative rate error and use it as a
block-coherent fractional error on every width in the block. Both fold in the
fractional terms of `rate_err_total`, which are `rate_est_spread` divided by the
campaign rate and `position_mismatch_relerr`. They do not fold in
`rate_laser_err` itself, because the per-block statistical error is already in
their own budget and adding the campaign one would count it twice.

## B4. The outlier rule

One rule, two populations, one pass.

**The rule.** Within a group of `n` members, let `M` be the median of the tested
statistic and `s` be its median absolute deviation scaled by 1.4826. The
deviation of member `i` is `(x_i - M)` divided by a scale, and the scale is `s`
floored as stated per population below. The member with the largest absolute
deviation is removed when that deviation exceeds

    threshold(n, m) = max(3.0, t at 1 - 0.05 / (2 n m) on n - 1 degrees of freedom)

where `m` is the number of statistics tested on each member. At most one member
is removed per group, and there is one pass. Groups smaller than four members
are never tested, because with three members the median absolute deviation is a
single number and a rule built on it is not a measurement.

The threshold is a two-sided t quantile at five per cent, Bonferroni corrected
over the `n` members of the group and the `m` statistics tested on each, which
is the standard way to ask whether the most deviant of several members is
deviant. The floor of 3.0 keeps it from falling below the conventional three
sigma line as `n` grows.

| n | m = 1 | m = 2 |
|---|---|---|
| 4 | 5.392 | 6.895 |
| 5 | 4.604 | 5.598 |
| 6 | 4.219 | 4.983 |
| 7 | 3.997 | 4.632 |
| 8 | 3.855 | 4.408 |

**Population A, the radio frequency on rulers.** The group is the ruler block.
The statistic is the per-trace comb spacing `delta_ms`, one statistic per
member, so `m` is 1. The scale is floored at `OUTLIER_MAD_FLOOR_FRAC` times the
median spacing, with `OUTLIER_MAD_FLOOR_FRAC` fixed at 1e-3. The floor is set by
what the fit can resolve rather than by any campaign number. The rigid grid
places six spacings across a window sampled every 0.5 ms, so the spacing is
resolved to at best 0.5 divided by 6, which is 5.7e-4 of a 147 ms spacing. A
floor of one part in a thousand sits just above that and can therefore never be
reached by a real fit, while still leaving a one per cent disagreement visible
at ten scale units.

The expected catch is `rulers_p/4207nm_eom_before5.csv`, whose spacing sits
about one per cent below its own block and which section A5 already identified
as the trace that moves the 4207 bracket separation. Naming it in advance is
what makes the run a test rather than a description.

**Population B, the radio frequency off lines.** The group is the
condition-sibling group `run_qc.py` already builds. The statistics are the
sibling z scores `zsib_height_v` and `zsib_fwhm_ms` that
`results/qc_metrics.csv` already carries, so `m` is 2 and the tested quantity is
the larger of the two absolute values.

Those columns are already the rule's own deviation: `sibling_zscores` centres
each metric on the median of the trace's siblings and scales it by their scaled
median absolute deviation, with the floor `QC_SIBLING_MAD_FLOOR_FRAC`. So the
centring and scaling step of the rule is already done and is not repeated. The
threshold is applied directly to the larger absolute z score, and the single
largest member of a group is removed when it exceeds `threshold(n, 2)`. Only
canonical traces are tested, because the sibling groups are built from canonical
members.

**What removal means.** An outlier is excluded from block combination, from the
campaign rate, from the rate model, from the sweep-nonlinearity map and from the
condition fits. It keeps its row, marked `outlier` with an `outlier_reason` from
a closed vocabulary, in `results/ruler_traces.csv` for population A and in
`results/qc_metrics.csv` for population B, and it is listed in
`results/trim_report.csv` under stage `outlier`. The block combination is
printed both with and without the removals, so the size of every removal is on
the record next to the number it changed.

The vocabulary is closed. `spacing_outlier` for population A,
`sibling_outlier` for population B, and the empty string otherwise.

**What this rule is not.** It is not a quality judgement. A trace removed here
may be a perfectly good trace of something the block does not share, and the
with-and-without print is the place to look for that. It also does not touch
`hard_flags`, for the reason section 3 gives.

## B5. What the rules returned

Written after the run. Nothing above this heading was edited afterwards.

### B5.1 The cumulative-sum threshold, and a degenerate calibration

`TRIM_CUSUM_H = 8`. The section 6 procedure was run as written, 10,000 traces
of the fitted model plus noise with no tail, through the full two-sided trim
path at the longest scan any stage performs.

**The procedure as pre-registered returned a degenerate answer, and the
resolution is on the record rather than hidden.** `TRIM_MIN_RUN` alone holds the
false-alarm rate below the 1-in-297 target at every threshold on the grid, down
to 0.5, because an excursion that keeps accumulating for 40 samples is already
rare. "The smallest threshold meeting the target" would therefore have picked an
arbitrarily small number. The threshold is instead the smallest integer at which
the calibration produced no false alarm at all, which is strictly stronger than
what section 6 asked for. The largest null statistic over the 10,000 traces was
7.72.

One thing had to be settled that section 5 did not fix, and it moves the
threshold by a factor of twenty. Section 5 says the detector runs on "signed
smoothed normalized residuals" without saying whether the normalization comes
before or after the smoothing. Normalizing after leaves the smoother's own
correlation inside the statistic, the null wanders to a threshold of 165, and
that threshold depends strongly on how much tail happens to be scanned.
Normalizing first puts one unit of the statistic at one sample sigma, which is
the reading taken, and it lands on 8.

### B5.2 The trim census

| stage | population | trimmed | refused | untouched |
|---|---|---|---|---|
| ruler ladder | 104 fitted rulers | 2 | 2 | 100 |
| quality pass | 182 non-ruler traces | 34 | 0 | 148 |
| condition fit | 159 canonical lines | 0 | 1 | 158 |

**The ruler stage moves two traces and nothing else.**
`rulers_t/4207nm_eom_110c5.csv` gains 0.181 ms of spacing and
`rulers_t/4207nm_eom_090c6.csv` gains 0.016 ms. Both move up, which is the
direction removing contamination that contracted the grid predicts. Every other
fitted ruler is byte-identical to the untrimmed fit. The refusals are the
guarded-half rule working: a centred campaign comb spans 882 ms of a 999 ms
window, so one fitted width of guard leaves nothing to scan.

**The condition fit takes no trim on this archive.** That was measured before
the stage was enabled, so turning it on carries no change to any width, and the
integration is live rather than dormant. `run_linefit.py` prints the count it
takes and does not yet persist a per-trace record, so `results/trim_report.csv`
leaves its `linefit` rows empty rather than filling in a zero it cannot check.

**The quality-pass census is a diagnostic and it is not 34 retrace crossings.**
Those 34 sit in 8 blocks and arrive in whole blocks at a time, which is what a
real block-level feature looks like rather than noise. Six of the 34 carry more
than one half-maximum region and four carry more than one major bump, so the
quality module's own structure metrics see a second structure on a minority of
them. The trimmed set also has ten times the median background slope of the
untrimmed set and 1.6 times the median signal-to-noise, so brightness and
background are part of what is being detected. Nothing in this stage acts on any
number. It exists to be read next to the trace in the inspection gallery.

### B5.3 One change made after seeing an output

`envelope_residual` gained a linear background term, fitted on the wings,
after the first quality run. It is recorded here because it was a change made
after looking.

The reason is a defect rather than an outcome. Every physics fit in this
repository carries a linear background, so a model-free stand-in for them has to
carry one too. Without it the envelope is monotone while the trace is not, a
background rising by a per cent of the line height across the window violates
the model by construction, and on a bright trace that is several sigma of
sustained positive residual. The census fell from 38 to 34 and the trimmed set
still carries ten times the median background slope, so the term was necessary
and it was not sufficient. No threshold was touched.

### B5.4 The estimator family

| member | rate, MHz/ms | against the central value |
|---|---|---|
| `invvar_pdg` | 0.0425243 | reference |
| `unweighted` | 0.0426163 | plus 0.216 per cent |
| `median` | 0.0426331 | plus 0.256 per cent |
| `clipped3` | 0.0426163 | plus 0.216 per cent |
| `P_only` | 0.0425044 | minus 0.047 per cent |
| `T_only` | 0.0426264 | plus 0.240 per cent |
| `loo_min` | 0.0424921 | minus 0.076 per cent |
| `loo_max` | 0.0425580 | plus 0.079 per cent |

`rate_est_spread` is 7.048e-5, which is 0.166 per cent of the central rate.
`rate_laser_err` is 5.098e-5, which is 0.120 per cent. `rate_err_total` is
8.699e-5, which is 0.205 per cent and 1.71 times the statistical error alone.

**The family reproduces the unpublished review's finding RT6 and implements
its recommendation.** RT6 measured five of these estimators against the previous
committed rate, found the choice of estimator moving the central value by up to
0.23 per cent while the scatter inflation widened only the error bar, and
concluded that the right remedy is to quote the estimator spread as a systematic
rather than to reject blocks. That is now a column.

`clipped3` clips nothing. The pre-registered definition drops blocks further
than three sample standard deviations from the running mean, and the most
deviant block is 2.0 of them, so this member returns the unweighted mean exactly.
RT6's clip dropped four blocks because it clipped on the per-block errors rather
than on the sample spread. The member is kept as pre-registered and it adds
nothing to the range.

### B5.5 The ruler-against-line position mismatch

`position_mismatch_relerr` is 0.234 per cent. The rulers sit at a count-weighted
median window position of 214 ms and the lines at a median peak position of
40 ms. The interpolated local rates at those two positions differ by 0.049 per
cent, and the quadrature sum of the two map errors is 0.234 per cent, so the
quoted value is the map's own resolution rather than a resolved difference.
The systematic is real and it is currently a bound on a difference the map
cannot yet measure.

### B5.6 What the fold moved downstream

The two fractional terms combine to 0.287 per cent, and that is what
`load_block_rates` and `load_t_rates` fold into their block-coherent relative
rate errors. Before the fold those errors ran from 0.146 to 1.67 per cent with a
median of 0.401 per cent. After it they run from 0.322 to 1.69 per cent with a
median of 0.493 per cent. The growth is between 1.01 and 2.21 times, largest on
the tightest blocks, which is the expected shape: a systematic floor matters
most where the statistics are best. The 993.4154 nm power-session bracket grows
the most, from 0.146 to 0.322 per cent.

Both consumers already carried a per-block statistical rate error, so
`rate_laser_err` is not folded in on top of it. Only the two fractional terms
are, and `run_beta_self.py` folds them after the time-resolved rate model has
replaced the per-block error, so the model's own smaller error still gains the
same floor.

### B5.7 The outlier census, both populations

**Population A, the rulers.** Five traces removed, from five of the twenty
blocks, all of them temperature-session dwells.

| trace | block | spacing, ms | deviation | threshold |
|---|---|---|---|---|
| `rulers_t/4207nm_eom_110c3.csv` | T 4207 110 C | 147.96 | 12.17 | 4.60 |
| `rulers_t/4154nm_eom_090c2.csv` | T 4154 90 C | 144.30 | 9.23 | 4.60 |
| `rulers_t/4121nm_eom_110c4.csv` | T 4121 110 C | 145.98 | 8.80 | 4.60 |
| `rulers_t/4207nm_eom_070c4.csv` | T 4207 70 C | 147.40 | 5.91 | 4.60 |
| `rulers_t/4121nm_eom_070c2.csv` | T 4121 70 C | 147.34 | 5.74 | 4.60 |

**Population B, the lines.** Three traces removed, from three condition groups:
`p_sweep/4121nm_025mw5.csv` at 5.91 against 5.60, `t_sweep/4154nm_070c1.csv` at
11.74 against 6.90, and `t_sweep/4207nm_090c5.csv` at 6.14 against 5.60.

**The expected catch did not fire, and that is a failed prediction.** B4 named
`rulers_p/4207nm_eom_before5.csv` in advance. Its spacing of 145.40 ms sits
0.95 per cent below its block median of 146.80 ms, but the other four members of
that block spread over 146.49 to 147.08 ms, so the block's own scaled median
absolute deviation is 0.414 ms and the trace is 3.37 deviations out against a
threshold of 4.60. The rule does not see it. Amendment A5 reached the same trace
by a different instrument, the top-three amplitude test, which does flag it.
Two instruments disagreeing about one trace is the useful part of this result.

**The rule fires about twice as often as its nominal level, measured.** The
threshold is a t quantile, and the statistic is a deviation scaled by a median
absolute deviation on four to seven points, whose null distribution has far
heavier tails than a t. Simulated on 200,000 Gaussian groups: the per-group
false-alarm rate is 7.9 per cent at n of 4, 13.3 per cent at 5, 9.7 per cent at
6 and 12.5 per cent at 7, against the 5 per cent the Bonferroni construction
nominally buys. Over twenty blocks that is an expected 2.2 false positives
against the 5 observed. So some of the five are chance and the rule is not
calibrated for the statistic it is applied to. The correctly calibrated
threshold at n of 5 would be about 8.0 rather than 4.60, which would keep the
top three of the five and drop the other two.

This is left as measured rather than corrected, because correcting a
pre-registered threshold after seeing which traces it removed is the move this
note exists to prevent. What the correction would be is stated above so that
it can be made deliberately.

### B5.8 What moved in the calibration

| quantity | committed | trim only | outliers only | both |
|---|---|---|---|---|
| `rate_laser` | 0.04252649 | 0.04252635 | 0.04252445 | 0.04252431 |
| shift | reference | minus 0.00034% | minus 0.0048% | minus 0.0051% |
| `block_chi2_red` | 8.078 | 8.071 | 8.001 | 7.987 |
| `scatter_pct` | 0.6176 | 0.6173 | 0.6338 | 0.6328 |
| 4207 before against after | 3.7 sigma | 3.7 | 3.7 | 3.7 |

The rate moves by a fortieth of the 0.2 per cent bound section 9 set.
`block_chi2_red` falls. The 4207 bracket separation does not move.

**`scatter_pct` rises, and the outlier removal is what raises it.** It goes from
0.6176 to 0.6328, a rise of 2.5 per cent of itself. The trim alone lowers it.
The block-to-block spread of the rates is what a removal is supposed to reduce,
and removing the most deviant member of five blocks made it larger, because each
of those blocks then combines four traces instead of five and its mean moves.
Section 9's stop condition on `scatter_pct` is written for a run in which the
top-three test gates, which this is not, so it does not formally bind here.
It is reported as a stop-condition-shaped result anyway, because a filter that
makes the blocks agree less about the rate has not obviously removed a defect.
Amendment A5 read the same signal the same way when the excision rung raised
`scatter_pct` to 0.6524.

### B5.9 What the record now owes

The campaign rate moved, so the eight files that hand-type it are stale and
`tests/test_docs_canonical.py` says so for both the laser-axis and the
transition-axis entries. The tokens move from 0.04253, 0.042526 and 0.0425265
to 0.04252, 0.042524 and 0.0425243, and the transition axis from 0.085053 to
0.085049. The propagation is deliberately not done here. It belongs with the
recompute, alongside the sites the registry does not guard, and a partial
propagation would turn the guard green while leaving the unguarded sites stale,
which is the failure the guard exists to catch.

`results/linefit_conditions.csv` and everything downstream of it are stale
against their producers as well, because three canonical traces now leave the
condition fits. Those producers were not re-run here for the same reason.

---

# Amendment 3, 2026-08-04: the outlier threshold is recalibrated against the null

Everything above this line stands, unedited. This amendment replaces one
parameter of amendment 2, the outlier threshold, and nothing else. The rule, the
statistic, the populations, the one-pass structure, the at-most-one-per-group
cap, the minimum group size, the scale floors and the closed reason vocabulary
are all as B4 fixed them.

**The caught traces played no role in setting the new thresholds.** The
calibration below runs on synthetic Gaussian groups and never reads a campaign
number. Section C1 was written and the thresholds were fixed before any census
was re-run. The identities of the five traces amendment 2 removed, and of the
two that a stricter rule would keep, were not consulted, not inspected and not
used as a target. B5.7 refused to correct the threshold for exactly this reason,
and the correction is made here only because it can be made against the null.

## C1. Why the pre-registered threshold had to move

B4 set the threshold from a two-sided t quantile at five per cent, Bonferroni
corrected over the n members and the m statistics, on n-1 degrees of freedom.
B5.7 then measured what that construction actually delivers, on 200,000
Gaussian groups: a per-group false-alarm rate of 7.9 per cent at n of 4, 13.3
at 5, 9.7 at 6 and 12.5 at 7, against the 5 per cent the construction claimed.

The diagnosis in B5.7 is confirmed and is the whole of the reason. A deviation
scaled by a median absolute deviation on four to seven points is not a t. The
scale is a small-sample order statistic, it can come out far too small by
chance, and the ratio inherits a tail much heavier than the t distribution the
threshold was read from. The Bonferroni step is not what failed. The
distribution the quantile was taken from is.

**This is a miscalibration of the null, and nothing else.** It is not a
judgement that the rule caught the wrong traces, not a response to any trace it
caught, and not a change of level. The pre-registered level of `OUTLIER_ALPHA`
stays at five per cent. What changes is that five per cent is now measured
rather than assumed.

## C2. The null, and why there are two of it

The null is a group of n members carrying m statistics each, every value an
independent standard Gaussian. The group statistic is the largest deviation in
the group, maximized over the m statistics tested on each member, which is the
quantity the rule thresholds. The calibrated threshold is the 95th percentile of
that statistic, so the per-group false-alarm rate is five per cent by
construction.

The two populations do not compute the same deviation, and calibrating one null
for both would leave the other wrong.

**The group scaling.** `rb5s6s.qc.group_outlier` takes the median and the scaled
median absolute deviation over the whole group, including the member under test.
That is population A, the ruler spacings.

**The sibling scaling.** `rb5s6s.qc.sibling_zscores` centres and scales each
member on the other n-1 members, and B4 fixed that those columns are the rule's
own deviation and are not rescaled. That is population B, the lines. A member
left out of its own scale sits further from it than one included in it, and the
scale is built from one point fewer, so the same nominal level needs a
substantially higher threshold.

Both scalings are MAD-scaled Gaussian groups. Naming only one of them would have
been the same error a second time, on the other population.

Two properties of the calibration are worth stating because they bound its
direction. The null omits the `QC_SIBLING_MAD_FLOOR_FRAC` floor that population
B's z scores carry, and a floor can only shrink a deviation, so the calibrated
sibling thresholds cannot fire more often than five per cent on real groups.
And the floor of 3.0 that B4 put under the t quantile is retired, because every
calibrated value stands well above it and a floor that never binds is not a
floor.

## C3. The calibration, and its counts

2,000,000 Gaussian groups per cell, 10 cells per scaling, 2 scalings, so
40,000,000 groups in total. Monte Carlo error on each threshold is 0.005 to
0.03, except the two n=4 sibling cells at 0.19 and 0.44, where the statistic is
heavy tailed for the reason C5 gives.

The construction was checked against B5.7 before it was used. On the group
scaling at the retired thresholds it returns 7.91, 13.14, 9.84, 12.61 and 10.40
per cent at n of 4 to 8, against the 7.9, 13.3, 9.7 and 12.5 B5.7 reported. The
two measurements are the same measurement.

**The retired thresholds, kept visible.** These are B4's table, and they are
what every number in amendment 2's B5.7 census was measured against.

| n | retired, m = 1 | retired, m = 2 |
|---|---|---|
| 4 | 5.392 | 6.895 |
| 5 | 4.604 | 5.598 |
| 6 | 4.219 | 4.983 |
| 7 | 3.997 | 4.632 |
| 8 | 3.855 | 4.408 |

**The calibrated thresholds, group scaling.** Population A.

| n | m = 1 | m = 2 |
|---|---|---|
| 4 | 6.909 | 9.902 |
| 5 | 7.926 | 11.411 |
| 6 | 5.530 | 7.163 |
| 7 | 5.854 | 7.611 |
| 8 | 4.915 | 6.072 |

**The calibrated thresholds, sibling scaling.** Population B.

| n | m = 1 | m = 2 |
|---|---|---|
| 4 | 61.520 | 122.507 |
| 5 | 13.847 | 19.884 |
| 6 | 13.004 | 18.771 |
| 7 | 8.252 | 10.677 |
| 8 | 8.102 | 10.506 |

Every calibrated cell sits above the retired cell it replaces, so the
recalibration can only remove fewer traces than amendment 2 did, never more.
That is a property of the table and it is pinned by a test.

**Closure.** Each calibrated threshold was re-tested on a fresh, independent
draw of 500,000 groups of its own null. All twenty cells return between 4.93 and
5.05 per cent. The thresholds do what they were built to do.

**What one table for both populations would have cost.** Applying the group
scaling's table to the sibling statistic leaves population B firing at 49.1 per
cent at n of 4, 13.9 at 5, 27.1 at 6, 11.9 at 7 and 19.4 at 8. That is better
than the 63.3 to 36.3 per cent the retired table gave it and it is nowhere near
five.

**The non-monotonicity is real and is not noise.** The thresholds do not fall
smoothly with n. A median absolute deviation on an even number of points is an
average of two order statistics and comes out smaller and more variable than one
on an odd number, so the parity of the point count the scale is built from
alternates the tail weight. On the group scaling the scale reads all n points,
so n of 5 and 7 are the heavy ones. On the sibling scaling it reads n-1, so the
heavy sizes shift by one, to n of 5 and 7 again by way of their even sibling
counts. A smooth formula fitted through these would be wrong at half the sizes,
which is why the table is measured values and not a curve.

## C4. Where the code carries it

`config.OUTLIER_THRESHOLDS` holds the two tables. `qc.outlier_threshold` gains a
`scaling` argument naming which null to read, defaulting to `group`, and
`run_qc.py` passes `sibling`. `qc.group_outlier` is unchanged apart from its
docstring.

Two behaviours are new and both are refusals. A group below
`OUTLIER_MIN_GROUP` returns an infinite threshold, so it is never tested, which
is what B4 already specified. A group above the calibrated range of eight raises
instead of extrapolating, because the table is measured and there is nothing to
evaluate off its end. A ninth member would send someone back to the null, which
is the correct destination.

`config.RULER_REINDEX_CHI2_TOL` and its stale docstring, flagged in A4, are
still outside the scope of an amendment about the outlier rule and are still
flagged rather than silently fixed.

## C5. One finding the calibration produced, and one question it hands over

At n of 4 on the sibling scaling the calibrated threshold is 122.5, and a
threshold of 122.5 is not a threshold. It is the null telling us the statistic
has no useful scale there.

The mechanism is the one `OUTLIER_MIN_GROUP` was written for, displaced by one
step. B4 set the minimum group at four because with three members the scaled
median absolute deviation is a single number and a rule built on it reports the
arithmetic of three points. On the sibling scaling a group of four gives each
member exactly three siblings, so the scale is a three-point median absolute
deviation and the pathology is back.

The value is carried as the null returns it rather than capped, which leaves the
rule inert at n of 4 for population B. The archive has one such group. Whether
groups of four should be tested on a sibling scaling at all is a policy question
that this amendment does not settle, because raising a minimum group
size is a change to the rule and not to its calibration.

## C6. The census, both populations, under the calibrated rule

Written after the run.

**Population A, the rulers.** Three traces removed, from three of the twenty
blocks, all temperature-session dwells, all at n of 5 against a threshold of
7.926.

| trace | block | spacing, ms | deviation |
|---|---|---|---|
| `rulers_t/4207nm_eom_110c3.csv` | T 4207 110 C | 147.96 | 12.17 |
| `rulers_t/4154nm_eom_090c2.csv` | T 4154 90 C | 144.30 | 9.23 |
| `rulers_t/4121nm_eom_110c4.csv` | T 4121 110 C | 145.98 | 8.80 |

Two of amendment 2's five now stand: `rulers_t/4207nm_eom_070c4.csv` at 5.91
and `rulers_t/4121nm_eom_070c2.csv` at 5.74, both below 7.926 and both above the
retired 4.604.

**This is the outcome B5.7 stated in advance.** It wrote that the correctly
calibrated threshold at n of 5 would be about 8.0 and that it "would keep the
top three of the five and drop the other two". The calibration returns 7.926 and
the census keeps the top three and drops the other two. B5.7 named the answer
before the calibration was run, which is what makes this a check rather than a
description.

The trace B4 named in advance, `rulers_p/4207nm_eom_before5.csv`, is still not
caught. It sits at 3.37 deviations against 7.926, further outside the rule than
it was against 4.604. The failed prediction of B5.7 fails harder and is recorded
again rather than reinterpreted. The top-three amplitude test still flags it,
so the two instruments still disagree about that one trace.

**Population B, the lines.** No traces removed, against three under the retired
table.

| trace | group size | deviation | calibrated threshold |
|---|---|---|---|
| `t_sweep/4154nm_070c1.csv` | 4 | 11.74 | 122.507 |
| `p_sweep/4121nm_025mw5.csv` | 5 | 5.91 | 19.884 |
| `t_sweep/4207nm_090c5.csv` | 5 | 6.14 | 19.884 |

All three stand. The first of them is the n=4 group of C5, where the rule is
inert, and it would stand at 19.884 as well.

## C7. The three observables, and what to act on

The removals-off column is a real run with the rule disabled, written to a
scratch directory. The committed tables were hashed before and after it and are
unchanged, which was checked rather than assumed.

| quantity | section 9 baseline | section 9 prediction | removals off | removals on |
|---|---|---|---|---|
| `rate_laser` | 0.04252649 | moves less than about 0.2% | 0.04252635 | 0.04252426 |
| `block_chi2_red` | 8.078 | falls | 8.071 | 7.977 |
| `scatter_pct` | 0.6176 | does not rise | 0.6173 | 0.6167 |
| 4207 before against after | 3.7 sigma | shrinks | 3.7 | 3.7 |

**`scatter_pct` no longer rises, so the removals act.** It falls to 0.6167 from
the 0.6173 the same pipeline gives with the rule disabled, and it falls against
the 0.6176 of section 9's baseline. Under the retired threshold it rose to
0.6328, and B5.8 read that rise as a filter that made the blocks agree less
about the rate. The rise goes away exactly when the two chance catches go, which
is what a false-positive rate of two to three times nominal predicts.

The other two observables meet their predictions. The rate moves 0.0052 per
cent, a fortieth of the 0.2 per cent bound, and `block_chi2_red` falls. The
fourth prediction still does not fire in either direction: the 4207 bracket
separation does not move, as it did not in B5.8.

**The removals are therefore applied, not diagnostic.** A removed trace keeps
its row, its `outlier` mark and its reason, contributes nothing to a block
spacing, the campaign rate, the rate model or the sweep-nonlinearity map, and is
listed in `results/trim_report.csv` under stage `outlier`, exactly as B4
specified. The block combination is printed with and without the removals, and
`ruler_blocks.csv` carries both, so the size of every removal stays auditable.
The diagnostic-only fallback that would have applied had `scatter_pct` risen was
not needed and was not taken.

## C8. What this amendment leaves stale

The campaign rate moved again, from 0.04252431 to 0.04252426, and the tokens
`0.04252`, `0.042524` and `0.0425243` are unchanged from what B5.9 predicted
they would become, so the propagation B5.9 deferred is the propagation this
landing performs. The six registry-guarded sites now carry the working-tree
values and `tests/test_docs_canonical.py` is green. The historical addenda and
the tooth-count docstring keep their replaced values, which carry their own
context and which the registry does not guard.

`results/linefit_conditions.csv` is a special case worth naming. B5.9 recorded
it as stale because three canonical traces were leaving the condition fits.
Population B now removes nothing, so the exclusion set is empty again and the
condition fits face the same members they always did. The producer was still not
re-run here, and whether the fold of the changed rate error terms moves it is a
question for the recompute rather than an answer this amendment has.

**The downstream staleness is measured rather than guessed.** Two of the cheap
producers `scripts/verify_results_fresh.py` covers were re-run against the
current tables and both move.
`results/amplitude_ratios.csv` shifts its `err_total` by up to 0.7 per cent and
`results/sharing_bic.csv` moves `dBIC_eff_block_minus_T` from 62.4 to 61.3,
neither of which crosses a threshold either file quotes. Both were put back
unchanged, because re-running two of the downstream producers and not the nine
expensive ones would leave a tree that looks recomputed and is not. That is the
failure B5.9 named for the documents and it applies to the tables in the same
way. `tests/test_results_fresh.py::test_committed_csvs_still_match_their_producers`
is the test that says so, it compares against head rather than the working tree,
and it stays red until the recompute lands and is committed.

**Update, 2026-08-05.** All three entries above are discharged.
`results/amplitude_ratios.csv` and `results/sharing_bic.csv` were re-run and
committed in `0bf2502`, where `dBIC_eff_block_minus_T` reads 61.3, and both
stand unmodified in the working tree. `results/linefit_conditions.csv` is being
re-run by the Phase 5 recompute along with the four tables that fold it,
`resolving_power`, `projections`, `lever_crosscheck` and `sigma_laser_sharing`,
so the exception this section opened for it closes when that recompute is
committed. The deliberate staleness that remains is the historical record only:
the replaced values inside the earlier addenda, each of which carries its own
date, and the tooth-count docstring in `rb5s6s/ruler.py`, which quotes the
five-against-seven refit as it was measured on the day.

# Amendment 4, 2026-08-04: the empty set fired, and the height clause is relaxed to six standing

## D1. What section 7 returned

Zero of the 104 fitted rulers are eligible under the rule as written. The
census by first failing clause: 54 fail the tooth-labelling test, 37 have a
tooth below the fit residual, 13 have a slot railed on its zero bound. The
height clause is not merely selective, it is unsatisfiable. The tallest
weakest tooth in the whole population stands at 0.706 of its own fit residual
(`rulers_p/4154nm_eom_before_1.csv`) against the 1.0 the clause requires. The
standing-teeth census over all 104 combs: 21 traces stand on six teeth, 64 on
five, 1 on four, 18 on three. No recorded ruler stands on seven.

## D2. The two causes, both measured

The first cause is the drive depth. Amendment A2 fixed the modulation index at
2 beta = 1.62 from the height pattern itself, and at that depth the Bessel
weights put the third-order pair at J3 squared over J1 squared = 1.7 per cent
of the first-order power. On the trace section D4 selects, the k = -3 window
is covered in full by the kept samples and its tooth still stands at only 0.63
of the fit residual. The amplitude cause binds even where the span cause does
not.

The second cause is the ramp span, raised by the experimenter and confirmed by
measurement. For every fitted ruler, take the kept sample interval after any
recorded trim, the recorded `t0_ms` and `delta_ms`, and ask whether each outer
tooth window, centre plus or minus half a spacing, lies inside that interval.
Zero of the 104 combs cover both outer windows in full. The k = -3 window is
clipped by the ramp edge on 52 traces, the k = +3 window on 36, both on 16.
The median margin from the tighter outer slot centre to its ramp edge is 0.18
spacings, against the 0.50 a full window needs. The ramp is short enough that
one third-order window is always partial, and the drive is shallow enough
that a fully covered third-order tooth still sits below the noise.

## D3. The decision

The finding was put up for decision as section 7 requires, with three options:
relax the clause to six standing, relax it and overlay the fitted Bessel
envelope, or drop the figure. Six standing with no envelope was chosen, with
the caption stating why the third order is below the noise. The experimenter
also named the span cause before the measurement confirmed it.

The amended clause: at least six of the seven fitted heights stand strictly
above the fit residual standard deviation, none railed. Every other clause is
unchanged, the clean pass on the labelling test, the ladder having taken no action, no
quarantine, the chi-squared ceiling, the ranking by the smallest of the seven
heights over the residual, and the untrimmed preference. The ranking keeps the
property the rule was built for, since a mirror in an outer slot cannot raise
the smallest of seven heights. The panel caption carries the two causes as
measured on the displayed trace.

## D4. What the amended rule selects

Seven traces are eligible under the amended clause. The winner is
`rulers_p/4192nm_eom_after1.csv`, six teeth standing, weakest tooth at 0.63 of
the fit residual, reduced chi-squared 1.01, clean labelling test, no ladder action,
no railed slot, untrimmed. On this trace the standing k = +3 tooth sits in a
window the scan end clips, and the fully covered k = -3 tooth is the one below
the residual, so the two causes of section D2 are both visible on the panel
itself. The trace with the tallest weakest tooth, 0.71 on
`rulers_p/4154nm_eom_before_1.csv`, stands on six teeth and is still not the
winner, because it fails the tooth-labelling test and the ladder had to
re-index it, the one-slot mislabelling signature of amendment A2. The clause
the relaxation touched is not the clause holding that trace out. `tests/test_ruler.py` holds the amended clause the same way it
held the original, both directions, and the seven-standing assertion is
replaced by six-standing with the railed count still required to be zero.

## D5. What a seven-tooth comb would take

A ruler that stands on all seven teeth needs both knobs moved: a scan long
enough to hold seven full tooth windows with margin, and a drive deep enough
to lift the third-order pair above the residual. That is a statement about the
next campaign, and it is recorded in the campaign-planning documents rather
than argued here.

# Amendment 5, 2026-08-04: the labelling gate, decided on the within-bracket test

## E1. The objection

The inspection gallery drew a comb whose fitted grid is displaced by one
slot and titled it the fit of record, while the same panel printed that the
labelling test had failed and was not acting. That was rejected. A
record that computes the correct answer, prints that it has it, and then
uses the other one is not a diagnostic.

## E2. What gating the ladder would do to the calibration

Measured on the recomputed table, over the 52 combs whose recorded
labelling fails the test. Forty four of them land on a different tooth
spacing when the ladder's relabelled solution is taken instead, mean
difference -0.044 per cent, largest 1.49 per cent. On the campaign mean the
substitution moves the rate by +0.019 per cent, inside the 0.205 per cent
rate error already carried.

The decisive test is within a bracket group, where every trace shares one
physical scan rate, so a change that recovers the truth must tighten the
group. Over the eighteen groups holding at least one relabelled trace the
mean spread goes from 0.378 to 0.381 per cent, tighter in eight groups and
wider in nine. Relabelling is a coin flip on the spacing.

## E3. The decision

The spacing stays the fit of record, because the measurement above shows the
<!-- term-of-art: frozen preregistration record, and pitch is the comb's tooth spacing -->
pitch does not know about the labelling and no case exists for disturbing
the calibration. The tooth numbering is corrected wherever the labelling test
fails, on every panel that draws a comb, with the recorded numbering shown
alongside so the picture never hides the table. The correction is a display
of the amplitude evidence, not a refit.

<!-- term-of-art: frozen preregistration record, and pitch is the comb's tooth spacing -->
This separates two things the earlier amendments ran together. Which slot is
the carrier is settled by the sideband amplitudes at the measured modulation
index and is not in doubt. What the pitch is, is a fit result, and the
relabelled fits do not measure it better. Gating the ladder for the pitch
stays refused, on the evidence of section E2 rather than on the earlier
reasoning.

## E4. What is not decided here

Whether the fit of record should be seeded to land on the correct labelling
in the first place, so that the two never disagree, is a question for the
frequency-calibration review. It is the difference between a fit that is
right by construction and one that is right after inspection, and it is
worth a session of its own rather than a change made while a recompute is
running.

## E5. The criterion that identifies a displaced grid, stated exactly

Section E3 left the identification to the labelling test. Two independent
reviews of the rendered inspection panels showed that the test is the
wrong gate for it, in both directions, so the criterion is fixed here.

At 2 beta = 1.62 the Bessel weights are 0.444 for the carrier, 0.572 for the
first order, 0.262 for the second and 0.075 for the third. The expected
height ordering of a correctly labelled comb is therefore

    first order above carrier above second order above third order.

Two consequences, and the second is the one that was being got wrong.

A carrier weaker than its first-order pair is expected at this depth. It
identifies nothing. One reviewer, an expert reading the panels cold, flagged
a correctly labelled comb as defective on exactly that reading, because no
panel said the suppressed carrier was the physics of the drive. The panels
now say it.

What a displaced grid shows is a SECOND-order tooth taller than a
FIRST-order tooth, which the ordering above forbids. Applied to the
persisted heights this identifies 54 combs of 104, not the 52 the labelling
test marks. The two the test misses are recorded as marginal passes,
`rulers_t/4121nm_eom_070c5.csv` and `rulers_t/4154nm_eom_070c5.csv`, and
both were inside the calibration with the wrong first-order pair drawn and
no note. Both carry a clean one-slot signature, and shifting them by one
slot returns a textbook pattern.

The numbering correction is gated on this amplitude test rather than on the
recorded `verdict` string. The labelling test keeps its own job, which is to
say whether the
recorded fit named the teeth correctly. The amplitude test says which
naming is right. Nothing here touches the spacing, and the count of combs
whose spacing is taken from the record is unchanged at 104.

# Amendment 6, 2026-08-05: the modulation depth measured cleanly, and what varies instead

## F0. Inverting over every comb is circular, and its depth range is withdrawn

Inverting the second-to-first height ratio over every well-resolved comb,
including the 54 whose grids the amplitude test flags as displaced, is
circular. On a displaced comb the recorded second-order slot holds a
first-order tooth, so the recorded ratio is inflated by the very defect
under study, and feeding it into the Bessel inversion returns depths
reaching 2.9 that are the mislabelling reflected back, not the drive. The
measurement below therefore excludes the displaced grids. The earlier
conclusion that the depth spans 1.45 to 2.92 is withdrawn and appears
nowhere else.

## F1. The measurement, on correctly numbered combs only

The height law first, because two computations of the depth disagreed until
it was pinned down, and because the depth is always to be written as
`2 beta = ...` rather than as a bare depth in radians. A reviewer read one of
those bare statements as beta and got half the answer.

The comb-amplitude derivation of
[the frequency ruler](../methods/05_the_frequency_ruler.md) sums every
sideband pair m plus m prime equal to k and returns, by Neumann's addition
theorem, a two-photon amplitude of J_k(2 beta) for the tooth at k. A tooth
height is a two-photon signal, so the drawn height is the modulus squared of
that amplitude,

    h_k proportional to J_k(2 beta) squared,

with the Bessel weights taken at 2 beta and not at beta. The comb fit in
`ruler.py` reads those heights straight out of the recorded fluorescence with
no square root in between, so the persisted heights carry the square. The
second-to-first height ratio at depth 2 beta is therefore J_2(2 beta) squared
over J_1(2 beta) squared, and that is the function inverted below. The
synthetic combs the ladder is calibrated on in `tests/test_ruler.py` are built
from that same law, so the only place in the repository that read the heights
otherwise was one gallery constant.

Take the combs whose recorded labelling passes the labelling test cleanly, 41 of
them with the first-order pair above five times the fit residual, and invert
each one's second-to-first height ratio through that law on the unique branch
below the crossing. The implied depth is

    2 beta = 1.569 median, 2 beta = 1.579 mean, standard deviation 0.058,
    range 2 beta = 1.449 to 2 beta = 1.730.

The drive depth is one number to within four per cent. Amendment A2's pooled
2 beta = 1.62 sits at the upper edge of this band, and nothing downstream
that used it moves by more than its own quoted error. Across the range the
second-order teeth stand between 0.159 and 0.249 of the first order, and at
0.194 of it at the median. That band is what the numbering-correction gate of
section F4 holds a recorded ratio against.

Nothing but the law moves this answer. The resolution cut returns the same 41
combs whether it is applied to the smaller first-order member or to the pair
mean, the two marginal cases are not well resolved and never enter under
either cut, three different inversion brackets return the same roots because
no comb sits near an endpoint, and seven definitions of the ratio move the
median by at most 0.017. Reading the heights as the bare amplitude instead,
and at beta rather than at 2 beta, returns 2 beta = 1.511 median with
standard deviation 0.137 and range 2 beta = 1.251 to 2 beta = 1.914. That is
the number an earlier gallery constant carried. It lands close to the right
one because its two errors run opposite ways and nearly cancel, which is why
the disagreement went unseen.

The archive cannot arbitrate the law on its own, and saying so is better than
implying a test that does not exist. With the carrier excluded the fit sees
four teeth, k equal to minus two, minus one, plus one and plus two, and a
law with a free depth and a free amplitude fitting a pattern symmetric in k
can set only an overall scale and one second-to-first ratio. Both readings
sweep that ratio over the same range, so both reach the identical chi-squared
of 67.6 on 82 degrees of freedom, each at its own depth. That comparison
re-parametrises rather than discriminates. The third-order pair would break
the degeneracy and is not there to do it: its mean stands above the fit
residual on 2 of the 41 combs and above three times it on none, the ramp
clips the outermost window on every recorded ruler, and eight of the 41 rail
a height at zero. Admitting it moves the chi-squared by 3.25 over 164 degrees
of freedom, which is noise. The derivation settles the law. The one place the
data speak is the carrier, and they agree with the derivation: at
2 beta = 1.569 the signal law puts the carrier at 0.696 of the first order,
which is where the measured carriers sit and scatter, while the amplitude
reading would put it at 2.45 and demand that every recorded trace be
suppressed by more than a factor of two.

## F2. The displaced-grid criterion is safe, twice over

Section E5's test needs a second-order tooth taller than a first-order one
to be impossible, which requires the depth to stay below 2 beta = 2.630. The
largest correctly numbered depth is 2 beta = 1.730, a margin of 0.90. The
crossing does not depend on which reading of the height law is taken, since
both are monotone in the same J_2 over J_1 and both put the ratio at one
where the two weights are equal, so section E5 is untouched by section F1's
settlement, and so is the census below. Independently: on the combs the test
flags, 40 have a first-order pair whose mean stands above five times the fit
residual (the resolution cut here is on the mean of the pair, where section
F1's cut on the smaller member gives its 41), and the recorded ratio is
unphysical on 34 of those 40, meaning no depth below the crossing reproduces
it at all, and the remaining six sit within 0.18 of the crossing, at
2 beta = 2.451 to 2 beta = 2.612. A mislabelled grid does not merely shift the
implied depth, it pushes the recorded ratio outside what phase modulation
can produce, which is a second, independent signature of displacement.

## F3. What actually varies is the carrier, and that is amplitude modulation

At 2 beta = 1.569 pure phase modulation predicts a carrier-to-first height
ratio of 0.696. On the same 41 clean combs the measured ratio runs 0.360 to
1.188, and on ten of them the carrier stands taller than the first-order
mean. The fig8 winner, `rulers_p/4192nm_eom_after1.csv`, is one of the ten,
carrier 0.704 V over first-order teeth of 0.677 and 0.691 V. The
second-to-first ratio is tight while the carrier ratio is wide, which is the
signature of residual amplitude modulation at the carrier, the imperfection
of the carrier-suppression setting that the methods note already lists. The
experimenter's record that the input polarisation angle changed between sessions is
consistent with this, since the suppression working point depends on that
angle while the drive depth evidently did not.

Two withdrawals follow. The claim that a suppressed carrier is expected on
every trace is withdrawn, because the carrier height carries amplitude
modulation and can stand above the first order on a correctly numbered comb.
And any use of the carrier height as labelling evidence is withdrawn with
it. The first-order pair and the second-order ratio remain the reliable
amplitude evidence.

## F4. What follows for the panels and the gallery

The panel sentence states the measured depth with its four per cent spread,
states that the carrier height varies with residual amplitude modulation and
identifies nothing, and derives the tooth ordering from the first and second
orders only.

The population the gate acts on is stated here so that no count below floats
free, and there are two populations, one inside the other. The counts in
this note are over the 104 fitted combs persisted in the calibration table.
The gallery draws 115 combs, the same 104 plus ten from the aborted first
session and one whose export is too short for a table row, so its printed
census reads 55 flagged where this note reads 54, and its recorded-offset
count sits one higher for the same reason. Section E5's amplitude test
identifies 54 displaced grids among the 104 fitted combs. On 44 of the 54
the slot offset is the one the calibration record already carries, from the
trial that rescued the labelling, and on the remaining 10 the record carries
none and the offset is read off the tooth heights the panel itself draws.
Both routes end in the same test below.

The numbering-correction gate changes from a carrier test to a ratio test. A
correction is accepted when the corrected numbering brings the recorded
second-to-first ratio from unphysical or displaced into the measured band of
0.159 to 0.249, and the carrier height plays no part.

A draft of this section reported that five of the 54 corrections drew a tall
carrier at the centre, which read as a property of the data. It was a
property of the heuristic that produced it. That earlier gate chose the slot
offset that put a suppressed tooth between the two tallest teeth, so it
manufactured its own disagreements, and the five are an artefact of it rather
than a census of anything. Rebuilt on the ratio test, exactly one accepted
correction draws a carrier taller than its own first-order pair. That one is
accepted on its ratio like every other, because on the evidence of section F3
a tall carrier is residual amplitude modulation and says nothing about the
numbering in either direction.

Whether the residual amplitude modulation is large enough to bias the tooth
spacing rather than only the heights stays with the frequency-calibration
review. Nothing here touches the spacing, which is measured from tooth
positions and not from heights.

# Amendment 7, 2026-08-05: why the trimmer never fires on a line

## G1. The reading the census invites, and why it is wrong

Amendment B5.2 reports the trim census as two calibration traces trimmed and
zero line fits trimmed. Read plainly, zero line fits trimmed says the line
traces carry no rising residual tail. They do. On the five repeats of the
993.4207 nm line at 130 C and 25 mW, three carry an unmistakable one.

The tails are real and the census is right at the same time, because the
trimmer never sees them. The line fit sets its own window per trace, at three
and a half times that trace's own measured width, capped so that the sweep
retrace crossing about 40 MHz away is always outside it. On those five traces
the recorded sweep runs to about +58 MHz while the fitted window ends between
+30 and +35 MHz. The rising tail sits beyond the window edge, so it is
already excluded before the trimmer is asked, and the trimmer, which walks
outward only within the fitted samples, correctly finds nothing to cut.

## G2. What follows

Nothing changes in the pipeline. The window and the trimmer are two guards
against the same contamination and the window gets there first, which is the
order they should act in, since a fixed rule that excludes the retrace
by construction is better than a detector that has to notice it.

What changes is the statement. The census line means the window left the
trimmer nothing to do on any line, not that no line has a tail. Written the
first way it is a fact about the guards. Written the second way it is a
false claim about the data, and it was one sentence away from being made.

The inspection pages now mark the window explicitly, with a dashed vertical at
each edge of the span the model covers and a legend entry naming it, so a
reader can see which samples the fit was asked about. Drawing the unfitted
samples in a paler tone as well would say it more directly and has not been
done. A page that draws a model across samples the model was never fitted to
makes a sound fit look like a failing one, which is exactly how this was
found.

## G3. The question this left, answered 2026-08-06

Whether the window is in the right place is a separate question from whether
the trimmer works, and it was not settled here. The cap that excludes the
retrace is a fixed number of megahertz, and the retrace crossing moves with
the sweep rate, which the six-tooth correction had just re-measured. A cap
that is comfortable at one rate is not automatically comfortable at another.
The frequency-calibration review took this on, and the check was cheap: for
every canonical trace, the distance from the window edge to the nearest
recorded retrace crossing, in units of the fitted width.

It has now been run, in RT10 of
the frequency-calibration review (amendment 8), and
it names a different constant than the one this section worried about.

Neither clip is active on the archive. The 25 MHz cap binds on 0 of 159
canonical traces and the 9 MHz floor on 0 of 159, so every canonical window is
the plain 3.5 fitted widths. The measured crossing separations run 39.2 to
43.0 MHz, which is 7.64 to 8.54 fitted widths against a window edge at 3.50,
a minimum clearance of 4.14 widths.

The cap also cannot become the unsafe element. Under a re-measured rate on
fixed recorded traces, the cap is active only when 3.5 window-times of sweep
exceed 25 MHz, and the window is unsafe only when the crossing time falls
inside 25 MHz. Since 3.5 window-times is 3.50 widths against the crossing's
7.64, a factor 2.18 of margin, the two conditions are disjoint at every rate
calibration, and the clip can only narrow the window and so only improve the
clearance. The floor is the direction that widens, and there the two
conditions do overlap. Reaching it takes a rate of 0.0184 MHz/ms against the
measured 0.085 MHz/ms on the transition axis, a calibration wrong by 78 per
cent, which is why this is recorded and not acted on. The rate-sensitive
element in the widening direction is the 9 MHz floor, not the 25 MHz cap.

One residual sits outside what a clearance metric can see. On the
mirror-bearing traces the mirror's own Lorentzian wing leaks into the fitted
window at +0.0048 +/- 0.0023 of line height, against -0.0010 +/- 0.0063 on the
traces with no mirror, which is the size a Lorentzian at 4.2 widths standoff
predicts. Clearance in widths says the crossing is outside the window. It does
not say the crossing contributes nothing inside it.

## Amendment 8, 2026-08-06: the phase 7 adjudication, summarised

The frequency-calibration review ran against v3.4.0: twelve pre-scoped
targets, each finding adversarially adjudicated with re-derivation from
the committed tables. Six confirmed, five refuted, one open, a 42 per
cent refutation rate. The working note with full instruments and
adjudications is an internal review document and stays unpublished by the
standing rule. What binds here:

Six confirmed, five refuted, one OPEN (42 per cent refuted). Three findings moved. RT3 and RT6 fall from confirmed to refuted, and RT1 from confirmed to refuted. RT10 rises from refuted to confirmed. RT3 dies because its decisive supporting claim, that no in-window slot separates the sessions once brightness is accounted for, tested only the carrier's median. the carrier's spread separates them at Levene p = 0.019 with twice the distance from the phase-modulation prediction, which is amendment 6 F3's finding and its session-dependent polarisation cause, and its correct residue is RT7's, not its own. RT6 dies on three closures already in the archive: results/ruler_campaign.csv's rate_err_total of 0.205 per cent already exceeds the 0.146 per cent the excess-variance model wants, the +0.130 per cent centre shift sits inside amendment B2's rate_est_spread of 0.166 per cent, and B2 built its error-blind estimators for exactly this reason ("those errors are inflated twice"). RT1 dies because no published text states the benign condition as an iff, only a test docstring does, and section 9 already records that the fold's sign is set by apex phase. the live defect at that anchor is instead that addendum 26 says docs/DATA.md section 7 "now carries the corrected reading" and it does not, the two documents pointing at each other while the uncorrected "do not re-litigate" bullet stands. RT10 rises because it answers a question the specification parked and shows it named the wrong constant. The single most consequential finding is RT4. Two attempts to refute it both failed, and each produced worse news than the finding reported: reproducing the map cell for cell from raw traces and then printing the worst well-sampled window at each binning shows one localised, sign-coherent departure of −0.40 to −0.76 per cent near −40 to −85 ms at every resolution finer than the committed 12 bins (2.27, 2.62, 2.85 and 4.41 sigma at 10, 16, 20 bins and at frac 0.00), which the committed 125 ms bin averages down to −0.245 per cent, just inside the quoted 0.3 per cent, and that position lies inside the line-fit window, so the fig8 sparse-edge split does not reach it. The unqualified sentences at docs/RESULTS.md line 93 and docs/DATA.md line 646 are false against the archive's own map, and the two-sided ratchet at tests/test_ruler.py line 538 will keep pulling the published number down to whatever the current, unpre-registered gates produce.

The confirmed actions are implemented as of this date with one
exception, the amplitude-seeded fold construction (RT12), which was
evaluated and not accepted (addendum 27 of
[PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md): the
seeding reproduces RT12's demonstration, but the campaign rate moves
+61.5 ppm through the group-outlier rule, and the seed breaks the
fold detector on injected folds, so production stays on proximity
seeding and the rule stays as an explicit opt-in diagnostic). The RT6
statistic was re-derived at
implementation: the per-session reduced chi-squared ratio is 9.45 with
a two-sided F test on 7 and 11 degrees of freedom giving p = 0.0014,
and the ledger generator computes both from the committed block tables.
