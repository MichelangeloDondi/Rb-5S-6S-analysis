# Ruler fit validity and residual-tail trimming: specification of record

**Status: pre-registered 2026-08-04, before the code was written and before any
number came out of it.** Every threshold below is fixed here, with its
justification, so that the run can only confirm or fail it. No value in this
note was chosen after seeing a fit.

Producers: [`rb5s6s/ruler.py`](../../rb5s6s/ruler.py) and
[`scripts/run_ruler.py`](../../scripts/run_ruler.py). Outputs:
`results/ruler_traces.csv`, `results/ruler_blocks.csv`,
`results/ruler_campaign.csv`, `results/ruler_nlmap.csv`.

## 1. The defect this specification answers

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
which is the one flag that would see a retrace crossing. The fitted tooth
heights were never written to disk, so no reader could audit the indexing after
the fact.

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
it left the verdict failing.

1. **Fit.** The existing constrained comb fit, unchanged.
2. **Trim.** Reserved for the residual-tail trimmer of section 5. Until that
   module lands, this step is a no-op and the trace passes through untouched.
3. **Verdict.** The top-three rule of section 2.
4. **Phase shifts.** Refit with the comb phase seeded at t0 plus j times Delta
   for j in minus two, minus one, plus one, plus two. A shift is accepted only
   if the refit passes the verdict AND does not raise the reduced chi-squared
   by more than `RULER_REINDEX_CHI2_TOL = 1e-3` of its own value. Among the
   accepted shifts the lowest reduced chi-squared wins. Both conditions are
   required because a re-index that rescues the verdict while worsening the fit
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
6. **Quarantine.** If the verdict still fails, the trace is quarantined with a
   reason from section 4.

Whether the ladder's answer is APPLIED or merely recorded is a single switch,
`RULER_TOP3_GATED`, which lands off. Section 10 says why and what would settle
it. Everything in this section runs either way, so the population can be
studied without the verdict touching a number.

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
| `no_excision_candidate` | the verdict fails and no outer slot qualifies as a mirror, so there is nothing to excise |
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
| `TRIM_SMOOTH_W` | 21 samples | the boxcar width the quality module already uses, adopted rather than tuned |
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
hold: the top-three verdict passes and is not marginal, the ladder took no
action, the trace is not quarantined, all seven fitted heights stand strictly
above the fit residual standard deviation with none railed, and the reduced
chi-squared is at most `RULER_FIG_CHI2_MAX = 2.0`. Eligible traces are ranked
by the smallest of the seven heights divided by the residual standard
deviation. A mirror cannot raise the smallest of seven heights, so the ranking
cannot be gamed by the defect the figure is being fixed for.

If the eligible set is empty, the figure is skipped and the reason is printed.
An empty set would be a finding about the ruler population and would go to the
owner rather than being worked around by loosening a threshold.

The empty set fired. Amendment 4 records the finding, the two measured causes,
and the owner's decision to relax the height clause to six standing teeth. The
text above stands as written.

## 8. Licensing for the width-against-rate figure

Each point on that figure needs a licensed scan rate and a licensed width. The
verdicts, fixed before the rebuild:

| source | rate | width | verdict |
|---|---|---|---|
| campaign 130 C, 20 traces | bracket rulers of its own session | retrace-safe contiguous span | enters the panel |
| morning pilot, 26 traces | its own 27 rulers, measured scale 1.0022(12) | single peak, contiguous | enters as a separately marked point with a horizontal count error bar, outside the fitted slope |
| rehearsal, 46 traces | fitted inside the joint fits, not measured | would inherit a fitted rate | stays out, with the reason printed on the panel |
| EOM ruler traces as lineshape data | measured | would need an amplitude model | stay out for this release |

The rehearsal verdict follows the licensing rule rather than the instruction to
use all available data, and the owner may overrule it. A width derived from a
rate that was fitted inside the same model is not model-independent, and the
rehearsal already enters the shift bounds where its rate is properly
marginalized.

The ruler verdict keeps the standing refusal of addendum 22: the tooth
amplitude law does not close on the power-session ruler population, and
licensing calibration traces as lineshape data inside the release that found
their indexing broken would invert the burden of proof. The seven fitted
heights are persisted for the first time by this work, which is the dataset a
future amplitude model would be tested against, and the panel says so.

## 9. Predictions, and the conditions that stop the work

Each prediction is checked against the outcome before any number is written
into any document. They apply to a run in which the verdict is gating. While it
is recorded only, the calibration is unchanged by construction and there is
nothing to check.

| quantity | current committed value | prediction |
|---|---|---|
| campaign laser-axis rate `rate_laser` | 0.042526 MHz/ms | moves by less than about 0.2%, direction NOT predicted |
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
statement about one corner of the parameter space presented as a statement
about the effect. It is withdrawn here rather than quietly relaxed later, and
no number produced under it is quoted anywhere.

**Stop conditions.** If `block_chi2_red` rises, the work stops and goes to the
owner, because a validity filter that makes the blocks agree less has removed
information rather than a defect. The same applies if `scatter_pct` rises, or
if the rate moves by more than the 0.2% bound above.

Nothing here is conditional on the beam waist, which stands open. The rate is a
frequency-axis calibration and does not read the waist. Every absolute width
downstream of it remains conditional on the waist exactly as before.

## 10. The open question the owner has to settle

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
tolerance would both be revisited before the verdict is allowed to gate.

Three courses are open, and the choice is the owner's: keep the rule and gate
on it, replace the gating instrument with one that separates a relabelling from
a mirror, or proceed as originally specified. Nothing in this landing forecloses
any of them.

---

# Amendment, 2026-08-04: the modulation index, and the ladder's acceptance ceiling

Everything above this line is the note as it landed. Nothing in it has been
edited. This amendment records a hypothesis the owner raised after reading the
census, the measurements that test it, one code change it warranted, and the
gated trial rerun under that change. Where it contradicts the body, this
amendment is the later record and says so explicitly.

## A1. The hypothesis

The owner's reading of the census in section 10 is that the population is not
telling us about amplitudes at all. With the RF drive power fixed for the whole
campaign, the modulation index is one campaign constant. The second-order teeth
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
TRUSTWORTHY population, meaning the 78 of 104 traces whose tallest fitted tooth
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
the k equal to zero tooth stands ABOVE the pure phase-modulation prediction
rather than below it. That is recorded as a measurement and is not interpreted
here, since the half-wave-plate trick suppressed the optical carrier of the
ruler light and the two-photon k equal to zero tooth is not the same quantity.

**Verdict on the J2 question: J_2 cannot outrank J_1 at the campaign
modulation index.** The measured index is a factor of 1.6 to 1.8 below the
crossing, and the gap is 30 or more bootstrap standard errors. The section 10
objection that the rule "fails clean synthetic combs once 2 beta exceeds about
2.7" is a true statement about the rule and an irrelevant one for this
campaign, because this campaign did not run there.

One independent check, stated with its assumption because the assumption is not
verified. `docs/APPARATUS.md` section 2 puts the campaign drive at 10.00 Vpp,
which the manufacturer certificates place at 54 to 60 per cent of full
modulation, and notes that the phase-modulation index scales as one over the
wavelength so the index at 993 nm is about 0.79 of the 780 nm figure. IF full
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
| top-three verdict PASS | 0 | 26 |
| top-three verdict FAIL or MARGINAL | 26 | 0 |

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
synthetics put five teeth in a seven-slot grid, so a one-slot shift trades an
empty slot for an empty slot and costs nothing. Campaign combs populate all
seven slots, and the comb spans 882 ms in a 999 ms window, so a one-slot shift
always trades a populated slot for one that is partly outside the window. Over
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

**The ordering is NOT wrong, and the obvious ordering fix is wrong.** Blocking
the excision rung whenever any phase shift passes the amplitude rule was tried
and it breaks fold recovery. On the ladder's own fold injector at apex 0.8 a
phase shift does pass the amplitude rule while keeping a spacing of 131.9 ms
against a truth of 147.3 ms. The chi-squared condition is what rejects it, and
the excision rung is what then recovers the true spacing on all eight seeds.
Spacing preservation was also tried as a replacement acceptance test and it
does not separate either, because the false rescue on a folded comb preserves
the CONTRACTED spacing by construction.

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
describes the superseded ceiling. That docstring needs correcting and is left
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
IMPROVES. The amplitude rule reads only the two first-order slots, so it cannot
see an implausible outer height, and the chi-squared ceiling only bounds
worsening. Two of the 26 traces in A3 fail this way. That is a known residual
limit of the ladder as it now stands, it affects a small number of traces, and
it is left recorded rather than patched with a third condition that has no
calibration behind it.

### What the committed tables have to do about it

`results/*.csv` were left untouched by this work and were verified
byte-identical afterwards. That leaves them stale against their own producer,
so `tests/test_results_fresh.py::test_committed_csvs_still_match_their_producers`
FAILS under `--runslow` until the producer is re-run and the status column is
re-annotated. The default suite is unaffected, since that test is slow-gated.
Every other test passes, 1470 of them.

Only `results/ruler_traces.csv` moves, and only in its ladder-diagnostic
columns. `reindex_action` and `delta_advised_ms` change on 18 rows,
`reindex_j`, `excised_k` and `n_refits` on 14, `quarantine_advised` and
`quarantine_reason` on 8. `ruler_blocks.csv`, `ruler_campaign.csv`,
`ruler_nlmap.csv` and `ruler_rate_model.csv` are unchanged in every cell,
which is the check that the fix moves no physics while the verdict is advisory.
Regenerating the tables is a commit the owner makes, not one this work makes on
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
| `scatter_pct` | 0.6176 | does not rise | 0.6524, ROSE | 0.6058 |
| 4207 before against after | 3.7 sigma | shrinks | 6.2 sigma | 5.6 sigma |

**None of the three stop conditions of section 9 fires under the fixed
ladder.** The rate moves by a tenth of its bound, the block consistency
improves, and the block rate spread falls instead of rising. The scatter rise
that stopped the earlier trial goes away exactly when the excision rung stops
firing. The two runs differ in no other mechanism, and on the one case examined
in detail the excision deleted a first-order tooth of 36.5 fit residual RMS, so
the rise is read here as the excisions and not as the verdict.

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
is calibrated on synthetics with known answers, and while the verdict is not
gating it changes no number in the repository. That was verified rather than
assumed.

Gating stays off for three reasons, and two of the three arguments in section
10 are now withdrawn.

Withdrawn. The first was that the rule "fails 54 of 104, so it is measuring the
population". It is not. Of the 52 failures, 44 are relabelled by a one-slot
comb-phase shift, and gated the census is 93 PASS, 3 MARGINAL and 8 FAIL. An
instrument that fires on 8 per cent of a population is a plausible defect
detector. The second was that the rule "fails clean combs above 2 beta of about
2.7". True of the rule, and irrelevant here, because section A2 measures the
campaign index at 1.62 and the crossing is at 2.63.

Standing. The third argument survives untouched and it is the decisive one. A
parallel measurement finds the rule PASSING an injected fold that costs 7.9 per
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
That trade does not favour gating today.

What would settle it is a sensitivity measurement rather than another
threshold. The rule needs to be shown to fire on injected folds across the full
range of apex positions, at the fold rate the archive actually supports, before
it decides which traces enter the frequency axis. Until then the ladder should
keep running and keep recording, which is what it does.

## A7. What changed in this note, and why

Section 3's justification for `RULER_REINDEX_CHI2_TOL` is superseded by A4. The
degeneracy argument in it is correct and the calibration behind it is not,
because the synthetics it was measured on cannot exhibit the cost. The number
1e-3 was not wrong by preference, it was measured on a case where the answer is
zero.

Section 10's first two reasons for landing the verdict ungated are withdrawn in
A6. Both were about the top-three rule firing too often, and both dissolve once
the modulation index is measured and the ladder stops mistaking relabellings
for mirrors.

Section 9's fourth prediction is recorded as FAILED in A5 rather than
reinterpreted. It was not a stop condition and the work does not stop on it,
but a prediction that fails is a prediction that failed.

Section 10's request that "the excision step and the chi-squared tolerance
would both be revisited before the verdict is allowed to gate" is discharged by
A4. The tolerance was revised, the excision step was guarded, and the verdict
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
   the verdict, exactly where section 3 reserved rung 2. The core is the fitted
   comb span, meaning the outermost fitted tooth centres, widened by
   `TRIM_CORE_GUARD_FWHM_MULT` fitted widths on each side. A trim triggers one
   refit through `fit_comb(mask=...)` and the trimmed fit becomes the fit the
   verdict judges.
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

`trim_start_ms` and `trim_end_ms` bound the KEPT interval, in both tables, so
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
campaign rate and `position_mismatch_relerr`. They do NOT fold in
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

Those columns are ALREADY the rule's own deviation: `sibling_zscores` centres
each metric on the median of the trace's siblings and scales it by their scaled
median absolute deviation, with the floor `QC_SIBLING_MAD_FLOOR_FRAC`. So the
centring and scaling step of the rule is already done and is NOT repeated. The
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
false-alarm rate below the 1-in-297 target at EVERY threshold on the grid, down
to 0.5, because an excursion that keeps accumulating for 40 samples is already
rare. "The smallest threshold meeting the target" would therefore have picked an
arbitrarily small number. The threshold is instead the smallest integer at which
the calibration produced no false alarm at all, which is strictly stronger than
what section 6 asked for. The largest null statistic over the 10,000 traces was
7.72.

One thing had to be settled that section 5 did not fix, and it moves the
threshold by a factor of twenty. Section 5 says the detector runs on "signed
smoothed normalized residuals" without saying whether the normalization comes
before or after the smoothing. Normalizing AFTER leaves the smoother's own
correlation inside the statistic, the null wanders to a threshold of 165, and
that threshold depends strongly on how much tail happens to be scanned.
Normalizing FIRST puts one unit of the statistic at one sample sigma, which is
the reading taken, and it lands on 8.

### B5.2 The trim census

| stage | population | trimmed | refused | untouched |
|---|---|---|---|---|
| ruler ladder | 104 fitted rulers | 2 | 2 | 100 |
| quality pass | 182 non-ruler traces | 34 | 0 | 148 |
| condition fit | 159 canonical lines | 0 | 1 | 158 |

**The ruler stage moves two traces and nothing else.**
`rulers_t/4207nm_eom_110c5.csv` gains 0.181 ms of spacing and
`rulers_t/4207nm_eom_090c6.csv` gains 0.016 ms. Both move UP, which is the
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

**The family reproduces the private red-team finding RT6 and implements its
recommendation.** RT6 measured five of these estimators against the previous
committed rate, found the choice of estimator moving the central value by up to
0.23 per cent while the scatter inflation widened only the error bar, and
concluded that the right remedy is to quote the estimator spread as a systematic
rather than to reject blocks. That is now a column.

`clipped3` clips nothing. The pre-registered definition drops blocks further
than three SAMPLE standard deviations from the running mean, and the most
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

Both consumers already carried a per-block STATISTICAL rate error, so
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

**The expected catch did NOT fire, and that is a failed prediction.** B4 named
`rulers_p/4207nm_eom_before5.csv` in advance. Its spacing of 145.40 ms sits
0.95 per cent below its block median of 146.80 ms, but the other four members of
that block spread over 146.49 to 147.08 ms, so the block's own scaled median
absolute deviation is 0.414 ms and the trace is 3.37 deviations out against a
threshold of 4.60. The rule does not see it. Amendment A5 reached the same trace
by a different instrument, the top-three amplitude verdict, which does flag it.
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
note exists to prevent. What the correction would be is stated above so the
owner can make it deliberately.

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
top-three verdict gates, which this is not, so it does not formally bind here.
It is reported as a stop-condition-shaped result anyway, because a filter that
makes the blocks agree less about the rate has not obviously removed a defect.
Amendment A5 read the same signal the same way when the excision rung raised
`scatter_pct` to 0.6524.

### B5.9 What the record now owes

The campaign rate moved, so the eight files that hand-type it are stale and
`tests/test_docs_canonical.py` says so for both the laser-axis and the
transition-axis entries. The tokens move from 0.04253, 0.042526 and 0.0425265
to 0.04252, 0.042524 and 0.0425243, and the transition axis from 0.085053 to
0.085049. The propagation is deliberately NOT done here. It belongs with the
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
median absolute deviation over the WHOLE group, including the member under test.
That is population A, the ruler spacings.

**The sibling scaling.** `rb5s6s.qc.sibling_zscores` centres and scales each
member on the OTHER n-1 members, and B4 fixed that those columns are the rule's
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
member exactly three siblings, so the scale IS a three-point median absolute
deviation and the pathology is back.

The value is carried as the null returns it rather than capped, which leaves the
rule inert at n of 4 for population B. The archive has one such group. Whether
groups of four should be tested on a sibling scaling at all is a policy question
and it is the owner's, not this amendment's, because raising a minimum group
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
again rather than reinterpreted. The top-three amplitude verdict still flags it,
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

## C7. The three observables, and the verdict on acting

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

**The removals are therefore APPLIED, not diagnostic.** A removed trace keeps
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
the tooth-count docstring keep their superseded values, which carry their own
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
is the test that says so, it compares against HEAD rather than the working tree,
and it stays red until the recompute lands and is committed.

# Amendment 4, 2026-08-04: the empty set fired, and the height clause is relaxed to six standing

## D1. What section 7 returned

Zero of the 104 fitted rulers are eligible under the rule as written. The
census by first failing clause: 54 fail the tooth-labelling verdict, 37 have a
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

The second cause is the ramp span, raised by the owner and confirmed by
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

The finding went to the owner as section 7 requires, with three options: relax
the clause to six standing, relax it and overlay the fitted Bessel envelope,
or drop the figure. The owner chose six standing with no envelope, with the
caption stating why the third order is below the noise. The owner also named
the span cause before the measurement confirmed it.

The amended clause: at least six of the seven fitted heights stand strictly
above the fit residual standard deviation, none railed. Every other clause is
unchanged, the clean-pass verdict, the ladder having taken no action, no
quarantine, the chi-squared ceiling, the ranking by the smallest of the seven
heights over the residual, and the untrimmed preference. The ranking keeps the
property the rule was built for, since a mirror in an outer slot cannot raise
the smallest of seven heights. The panel caption carries the two causes as
measured on the displayed trace.

## D4. What the amended rule selects

Seven traces are eligible under the amended clause. The winner is
`rulers_p/4192nm_eom_after1.csv`, six teeth standing, weakest tooth at 0.63 of
the fit residual, reduced chi-squared 1.01, clean verdict, no ladder action,
no railed slot, untrimmed. On this trace the standing k = +3 tooth sits in a
window the scan end clips, and the fully covered k = -3 tooth is the one below
the residual, so the two causes of section D2 are both visible on the panel
itself. The trace with the tallest weakest tooth, 0.71 on
`rulers_p/4154nm_eom_before_1.csv`, stands on six teeth and is still not the
winner, because it fails the tooth-labelling verdict and the ladder had to
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
