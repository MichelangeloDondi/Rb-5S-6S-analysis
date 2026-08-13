# Why the centre channel cannot be revived on this archive

Status: RECORD, 2026-08-10. Nothing here retracts a committed number. It closes a
question that had been left open in the shape "the centres are excluded" without
the exclusions ever being costed, and it names the one measurement that would
reopen it.

## The question

The line CENTRE is the strongest of the three AC-Stark channels: the pull goes as
the shift itself, where the width goes as its square and the skew as its cube. The
archive reports a width-channel bound and treats the centre channel as dead,
because the 2025 lock drifted and was re-centred by hand. The question put in
2026-08-10 was whether restricting to intervals between lock interventions, using
the recovered timestamps and the measured drift, and fitting the three sessions
jointly, could recover it.

The answer is no, and each session says no for a different reason. All three
reasons are now numbers rather than statements.

## The forecast, so the obstructions can be weighed against what it would buy

A Fisher calculation on the estimator the archive already uses, offset =
a + kappa*P + drift*t with the drift under its measured prior, at the archive's own
within-block centre jitter of 1.8 ms converted at the committed sweep rate:

| configuration | forecast sigma(kappa) |
|---|---|
| one campaign epoch, 50 mW contrast, 10 traces | 3.39 MHz/W |
| pilot, the two powers whose window setting matches | 4.87 |
| **pilot, all 26 traces, 175 mW contrast** | **0.87** |
| pilot, all 26, with a free offset per window setting | 4.83 |
| rehearsal, 46 traces, 180 mW contrast | 1.35 |

The width channel's bound is 1.147 MHz/W and the prediction is 1.545, so two of
those configurations would be worth having. The model is calibrated: it forecasts
3.39 for a campaign epoch and M27's three epochs returned 1.72, 2.94 and 3.75.

## The campaign: the power order is monotone, and that is the whole problem

All three multi-power display epochs run strictly downward in power with time.
Drift and pull then occupy one regression column and only their combination is
identified. M27 extracts what remains by holding to single epochs and importing
the independently measured drift as a prior, which is the right move, and it lands
where its own pre-fixed criteria send it: leave-one-out pulls range 1.16 to 3.40
sigma, a zero-signal control with a synthetic power label returns a comparable
2.69 sigma spurious pull, so the verdict is a BOUND of 8.65 MHz/W and not a
measurement. **That bound is 7.5 times weaker than the width channel's**, which is
why the centre channel contributes nothing as things stand.

One correction to M27 was found while writing this note and is recorded as
addendum 29. Its drift prior is directional, +0.016 +/- 0.009 MHz/min, and the
2026-07-30 window-reference correction had already withdrawn the licence for
that sign, leaving a two-sided bound of about 0.02 MHz/min. Refitting on the
sign-undetermined prior gives +6.63 +/- 3.40 rather than +4.75 +/- 2.37 MHz/W,
so the significance is unchanged at 1.95 sigma against 2.00 and the bound
LOOSENS to 12.21 MHz/W, 10.6 times weaker than the width channel. The
direction is the unfavourable one and it strengthens rather than weakens
everything below, since the channel is closed here on grounds that never
involve the prior.

## The pilot: the power order IS scrambled, and the frame eats it

Recovering the pilot's clock from its file times shows a power sequence of
**210, then 35, then 70, then 105 mW** across 16.8 minutes. That is not monotone,
power and time correlate at only -0.61 rather than the -1 that kills the campaign
epochs, and the variance inflation is a mere 1.6. Hence the 0.87 MHz/W forecast,
better than the width bound.

Two things spend it.

**The window setting moves by +14.0 ms at exactly the 210 to 35 transition**, and
by -4.0 ms at 35 to 70. That first transition carries nearly all of the power
lever. Projecting the moves through the estimator gives a frame systematic of
**-9.25 MHz/W**, eleven times the statistical error and six times the effect being
sought. The lever and the confound are the same contrast, which is the
response-versus-relabel ambiguity the record already names for this session, now
with a size attached. The one contrast whose window did not move, 70 to 105 mW,
forecasts 4.87 MHz/W on its own and buys nothing.

**And each power is visited exactly once.** So a free offset per block, which is
what an unmodelled re-centring in a between-block gap requires, is not merely
costly but unidentifiable: the offsets and the power contrast are the same
columns. Allowing one offset per window setting already takes the forecast from
0.87 to 4.83.

## The rehearsal: no trace can fix its own frequency origin

The rehearsal is the one session whose ladders ran in ALTERNATING directions,
which is exactly the design the campaign lacked, and it carries an
instrument-native trigger clock rather than a recovered file time. Its centres are
excluded for a reason unrelated to either: the scope auto-triggered, so the ramp
phase is random from trace to trace and an absolute position carries no frequency.

There is a way around that in principle, and the repository already uses it
elsewhere: a record containing BOTH the up-sweep and the down-sweep crossing of one
line fixes its own origin from the mirror-pair midpoint, which is a feature of the
ramp rather than of any knob, so it is immune to both trigger phase and window
setting. `rb5s6s/cavity_scan.py` does this arithmetic for a photograph.

**It is unavailable here, and the check is worth recording because a first pass
got it wrong.** A naive count of excursions above six sigma finds two features in
46 of the 50 records, which looks like the mirror pair. Measuring them settles it:
one feature is 330 to 405 ms wide, and the other is 5 to 8 ms wide at about
60 per cent of the amplitude. A genuine second crossing of the same line by the
same ramp must match in both width and height. It does not. At the rehearsal's
sweep rate a 6 ms feature is some tens of kilohertz across, more than fifty times
narrower than the 3.4925 MHz natural width, so it cannot be an atomic line at all.
The 5 s record therefore contains ONE crossing, and the archive's own segmentation
rule, which keeps the widest excursion, was right to keep one.

## Addendum, 2026-08-13: the pilot's own EOM rulers cannot be that reference

The programme notes parked one specific hope against the pilot: the pilot tree
carries its own EOM ruler folder, twenty-seven recovered rulers, and a ruler
bracketing a power step would supply exactly the knob-independent frequency
reference the section above says is missing, precisely where the frame problem
bites. Establishing whether one does was listed as the unlock. It does not.

Reading the acquisition clock off both folders:

| | span |
|---|---|
| the 27 rulers | 21:18:22 to 23:33:36 |
| the 26 power traces | 23:54:26 to 00:11:12 |

EVERY RULER PRECEDES THE ENTIRE POWER SWEEP, the last of them by 21 minutes.
Not one falls inside the sweep, so none brackets any of the three power steps,
whose gaps are 388 s at 210 to 35 mW, 170 s at 35 to 70, and 184 s at 70 to
105. The step that carries nearly all the lever, and whose window moves by
14.0 ms, has no ruler anywhere near it.

The file times are load-bearing here, so the check that they are acquisition
times rather than copy artifacts: within a power block the traces are 4 to 18 s
apart and between blocks 170 to 388 s, and the blocks appear in the order 210,
35, 70, 105. A bulk copy would order them by filename, which would put 035
first. It does not, so the clock survives the copy.

The rehearsal fails the same test for a different reason. Its 47 readable
power traces are single-channel, `Time,Ampl`, so no ramp monitor was recorded
alongside them, and the three that do not parse are the three already known to
be 0xff-corrupted on disk. The ramp channel exists in this programme only on
the EOM trial traces of the previous day, at 80 C and 0.80 A, whose scan
configuration the record already shows differs from the rehearsal's by a
factor of 2.2, so nothing transfers.

So the conclusion below is not merely unrefuted, it is now checked against the
one candidate reference the archive still contained.

## What would reopen it, and it is one thing

Every one of the three obstructions is the same shape: there is no frequency
reference that is independent of the knobs. The campaign needs one because its
power order is monotone, the pilot needs one because its window moved where its
lever is, and the rehearsal needs one because its trigger phase is random.

**The ramp-monitor channel is that reference, and it exists on the instrument but
was never exported.** `docs/PLAN.md` already lists its export among the fixed-lock
session's needs. This note upgrades it from a convenience to a precondition: with a
recorded ramp there is an apex in every trace, every centre becomes a frequency
rather than a position, and the pilot's own scrambled power order would deliver the
coefficient at the 0.9 MHz/W level from twenty-six traces and seventeen minutes of
bench time. Without it, no re-analysis of the 2025 archive can do better than the
bound M27 already reports.

## Two things this leaves for the record to fix

**M27's drift prior is one correction behind.** It uses +0.016 +/- 0.009 MHz/min
as a directional prior. The 2026-07-30 window-reference correction downgraded that
same quantity to a sign-undetermined bound of about 0.02 MHz/min, and M27, written
on 2026-08-02, did not pick the change up. Re-running under the corrected prior
should widen its interval and can only strengthen the bound-not-pull verdict, but
it has not been run.

**And M27's result has never been stated where a reader would find it.** The
number, and its rejection with it, live only in
`results/centre_stark.csv`. A reader following the reader-facing documents would
not learn that the centre channel has a bound at all, nor that its point estimate
was tested and refused. That is exactly the class of thing this project's own
preregistration ethos says must be visible, and it is fixed alongside this note.
