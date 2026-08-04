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
