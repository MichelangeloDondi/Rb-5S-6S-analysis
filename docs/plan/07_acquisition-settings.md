*Chapter 7 of 11 of [the plan](../PLAN.md)*

**The question.** What span, record length and sweep rate does the next session need?
**Takes.** Nothing beyond the block register of chapter 6.
**Gives.** The settings, and the simulations that fix each one.
**Skip if.** You want what was actually logged in 2025, which is chapter 8.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> **Question.** What span, record length and sweep rate does the next session need?
> **Design.** A span wide enough to curve the pedestal, at a record length set by points across the line.
> **Ambiguity removed.** The baseline absorbed into a free per-trace background.
> **Success.** An injected pedestal is recovered at the stated span and record.
> **Residual uncertainty.** The detection chain's own noise law, which must be re-measured on the day.

## 10a. Acquisition settings, and why 2025's choices bounded what could be learned

Added 2026-08-15, and every number below is derived from the committed
constants rather than recalled. This section exists because a full day of
analysis ended against limits that were set at acquisition time and could not
be undone afterwards. None of them needed new hardware.

### What 2025 actually acquired

| quantity | 2025 value | source |
|---|---|---|
| record length | 2000 points | `constants.TRACE_N_POINTS` |
| sample interval | 0.500 ms | `constants.TRACE_DT_S` |
| window | 1.000 s | the product |
| transition-axis sweep rate | 0.0852 MHz per ms | `linefit_conditions.csv` mean |
| full span | 85.2 MHz, plus or minus 42.6 | rate times window |
| resolution | 0.0426 MHz per point | rate times interval |
| line FWHM | 5.41 MHz | `linefit_conditions.csv` at 130 C, 225 mW |
| points across the line | 127 | the ratio |

127 points across the line is generous. The span is the binding constraint,
not the resolution, and every open question below is a span question.

### The three limits this cost, each measured

**One.** The out-of-window band that carries the ridge-breaking information
was 19 to 36 MHz, seventeen megahertz wide, out of a 43 MHz half-span. The
lower edge is the fit half-width and the upper edge stays clear of the
retrace mirror. That band was enough to show the band prefers a lower
collisional width than the core fit assigns, on 11 of 14 fresh conditions
(p = 0.029), and not enough to identify what lives in it.

The shaped-contaminant injection has since run, and it settles the reading in
the direction that costs the band its evidential value. Three contaminant
families were injected through the same pipeline at each condition's own
measured band deficit, all three sharing a band-mean so that only their shape
differed and the free per-trace background absorbed the same constant from
each. Both shaped families sit outside two combined standard errors of the flat
control, so the preference is not shape-independent: a contaminant of a shape
the measured deficits allow reproduces the displacement with no change in
collisional width at all. The pooled decision statistic returned partial rather
than a clean verdict, because it divides by each condition's own displacement
and five of those are comparable to the band's own resolution.

A second measurement narrows it further. Recomputing the band residuals under
the production model form leaves an offset that is positive on 15 of 16
conditions, from +0.04 to +0.29 per cent of peak, with the sixteenth at -0.36.
Retreating the retrace-mirror guard from 36 to 24 MHz fails to bring it below a
third of its value on any of the fourteen conditions where it is significant,
and the background's free slope absorbs none of it. But replacing that
background's line with a quadratic moves the offset from +0.215 to -0.158,
past zero and by more than the offset itself. The window spans 19 MHz of
half-width and the band runs to 36, so a curvature term is amplified by about
3.6 on the way out and the window data do not identify it.

Both RESULTS point at the same acquisition fix, and neither is a reason to
distrust the core fit. The band cannot arbitrate the collisional width while
its own baseline is an extrapolation rather than a measurement, and the span
below is what turns that baseline into data.

**Two.** The co-propagating Doppler pedestal is 942 MHz FWHM at 130 C
(`projections.csv`, `input_pedestal_width`). Across the entire 85 MHz span it
varies by under half a per cent of itself, so within these traces it is a
constant, absorbed by the free per-trace background. It can be neither
measured nor excluded within these traces. It is not, however, the source of
the unmodelled band excess, and an earlier version of this sentence called it
the standing candidate for it.

The arithmetic that excludes it is geometric rather than delicate. A 942 MHz
Gaussian is very nearly straight across a 36 MHz half-span, and the production
fit already gives every trace a free linear background over its window, so
subtracting a straight line from something almost straight leaves a residual
second order in the ratio of the window to the pedestal width. Carried through,
a pedestal leaves 0.001 per cent of peak in the 19 to 36 MHz band at its
predicted height and 0.010 per cent even at twelve times that, against a
measured band offset of 0.10 to 0.29 per cent. It is short by one to two orders
at every amplitude tested.

That agrees with the shaped-contaminant result above rather than competing with
it: the family that reproduces the displacement is linear in detuning, and a
pedestal is flat-and-quadratic near zero detuning, so it cannot supply a linear
term. The band excess remains unexplained, and the next campaign should treat
finding its shape as an open question rather than a confirmation exercise.

What the pedestal is good for, once a wide span makes it visible, is set out in
section 10c.

**Three.** The retrace mirror. The triangular ramp images the line about its
turning point, so a line sitting off centre in the sweep produces a copy at
twice its offset. In 2025 that copy sits near 40 MHz, which is why
`FIT_HALFWIDTH_MAX_MHZ` caps the fit window at 25. Centring the line in the
sweep, or scanning one direction only, returns the whole half-span for free.

### What the next campaign should set, with the arithmetic

Computed by `scripts/run_widescan_design.py` and written up with the
forward-modelled trace and the on-the-day checks in
[the wide-scan block design](../notes/widescan_block_design.md). Run the script
rather than trusting these numbers copied.

**Span.** Reach **three Gaussian sigma of the pedestal, so plus or minus 1200
MHz, a 2400 MHz span**, about 28 times the 2025 span. The reason is a
degeneracy and not an appearance: the per-trace background is free, so it
absorbs whatever is flat and the pedestal is measured only through its
curvature across the span. The amplitude's retained signal-to-noise is the
Fisher ratio sqrt(1 - <g>^2/<g^2>), which is 0.14 at one sigma of reach and
0.645 at three. A span chosen so the pedestal looks visible is not the span
that makes it measurable. The earlier figure and what replaced it
are recorded in [HISTORY.md](../HISTORY.md).

If the piezo cannot reach three sigma, the schedule in
[the design note](../notes/widescan_block_design.md) is also the fallback: take
the widest reach the hardware allows, since every row still detects the
pedestal in a five-trace block. Only the 2025 span is useless, at a retained
fraction of 0.0013.

**Record length.** **40000 points**, which gives 0.06 MHz per point and 90
points across the line at the 2400 MHz span.

![the same line sampled at two record lengths](../wiki/figures/wiki_sampling_the_line.png)

*The whole argument in one picture. A fixed record spread over a wider span
puts fewer samples on the line, and the width is fitted from those. At 10000
points the line carries 23 samples and the fitted width scatters by 0.062 MHz
over repeated draws at the measured noise law. At 40000 it carries 91 and the
scatter is 0.027. The curve is the same in both panels: what changes is how
many noisy samples the fit has to work from.* the span and the record are one
decision and not two, because widening the span at a fixed record thins the
sampling of the very line being measured, and the quantity to hold is points
across the line rather than points per trace. Simulated at this span with the
pedestal fitted correctly, 10000 points is 22 across the line and fails a
frozen recovery criterion, 20000 passes, and 40000 passes with margin. An
earlier version of this bullet specified 10000, which is the failing member
of that set. At the 2025 record of 2000 points the span and shape
requirements are mutually exclusive at any span.
Any modern oscilloscope offers megapoint records, so this is a menu setting
and not a purchase. Set it to the deepest record the export tolerates and the trade-off disappears: one trace then carries the Doppler-free line, its near
wings, and the pedestal together.

**Equivalently, if the record length cannot move:** hold the 2025 rate and
lengthen the window. 2400 MHz at 0.0845 MHz per ms is a 28.4 s trace, which
at the 2025 sample interval is about 57,000 points, so the same conclusion
arrives by another route. There is no setting of a 2000-point record that
answers both questions at once, and knowing that in advance is the point of
this section.

**Baseline identification, and the baseline model.** A consequence of the
second measurement in limit one, stated separately so it is not lost if the
span is ever trimmed for an unrelated reason. Two parts, and the second was
established by simulation after the first was written.

The baseline must be fitted on DATA the line does not reach, never
extrapolated from the fit window. The exclusion is computed rather than
eyeballed: treating the whole 5.41 MHz fitted width as Lorentzian, which
overstates the wing, the line is 1e-3 of peak at 86 MHz and does not fall to
1e-4 until 270 MHz. The offset at issue reaches only a few tenths of a per
cent of peak, so a 100 MHz exclusion would leave line wing inside the region
used to fix the baseline. Exclude 300 MHz, which the 2400 MHz span affords
with 1800 MHz to spare.

And the baseline model must be the pedestal, not a polynomial. A wider span
makes this more important rather than less, which is the opposite of what an
earlier version of this paragraph claimed. Simulated at the pedestal's own 942
MHz width and this record length, a straight baseline biases the recovered
collisional width by +0.91 MHz at the 2400 MHz span, against +0.004 MHz at the
2025 span, because a polynomial cannot follow a Gaussian pedestal and the
mismatch lands in the line. A quadratic halves that error and does not remove
it. Fitting the pedestal as a Gaussian of free amplitude and width recovers
the width at every span tested.

The on-the-day check, which costs one refit: fit the pedestal as a pedestal
and again as a polynomial, and confirm the recovered width agrees. If it does
not, the polynomial is the wrong model rather than the data being bad.

An earlier version of this paragraph added a pedestal-amplitude caveat, that
below about one per cent of line peak the check cannot resolve. It came from a
single realisation and does not survive sampling. Swept ten deep at each
amplitude, the pedestal model recovers the width at a 1200 MHz span for every
amplitude from 0.5 to 10 per cent. What the sweep found instead is in the next
requirement, and it is a sampling limit rather than an amplitude one.

**Piezo amplitude.** Set by the span requirement above. Record the amplitude
and the resulting rate per block, because the rate is what converts the time
axis to frequency and the archive had to reconstruct it from EOM combs after
the fact.

**Piezo scan speed and shape.** Two independent asks. Prefer a sawtooth or a
one-direction export over a symmetric triangle, which removes the retrace
mirror entirely and returns the excluded band. If the triangle must stay,
centre the line in the sweep so its mirror lands on top of it rather than at
a resolvable offset, and record which it is. Keep the per-point dwell no
shorter than 2025's 0.5 ms unless the detection bandwidth is checked against
it, since the cusp is a time-domain feature and a fast scan can smear it.

**Oscilloscope.** The archive is Agilent/Keysight InfiniiVision exports, two
header lines then time and volts, with the empty-voltage quirk
`ingest.load_trace` documents. The 2025-07-04 rehearsal used a Teledyne
LeCroy WaveSurfer 3104z, which is not the archive's instrument. Whichever is
used, the requirements are: a record length in the thousands of points at
minimum, a per-trace timestamp in the export (the archive had to recover the
clock separately, and `docs/RESULTS.md` records that block timing turned out
to be 54 to 76 minutes apart rather than minutes), a spare channel for the
ramp monitor (section 3 item 0), and a horizontal setting that is not
touched inside a block, since the 2025 window moved 58 times across the
campaign and line offsets are only meaningful within one scope-knob epoch.

### The two cheap measurements that would collapse a whole degeneracy

Both are session-level, neither is a scan setting, and either one alone
retires a question that cost a full day of analysis on 2026-08-15.

**Laser linewidth, once, by beat note or self-heterodyne.** The fitted
`sigma_laser` is 1.50 to 1.73 MHz on the transition axis. This bench's own
records put the laser at 0.19 to 0.47 MHz there. Of the eight wavemeter
records, only one falls inside the 17 to 18 July campaign (`APPARATUS.md`
section 6), and it is the panel reading 100 kHz short-term StdDev, which alone
puts the fit at three to four times the bench. The two scan-stopped records
giving RMS 0.04 to 0.05 MHz are from weeks earlier, and reaching a larger
multiple assumes they describe campaign-time behaviour. The core fit insists on the wide Gaussian, by 378 to 448 score
units. So a Gaussian-like component of about 1.5 MHz is in the data and is
not the laser, and the model has one Gaussian slot to put it in. One direct
linewidth measurement turns that from an inference into a fact.

**Retro alignment, checked and recorded.** Residual Doppler from a tilted retro
supplies the missing Gaussian. Two beams at angle theta to antiparallel carry
`|k1 + k2| = 2k sin(theta/2)`, so the residual width is `theta * v/lambda` =
0.471 MHz per mrad, half the co-propagating pedestal's coefficient because the
pedestal already carries `k_eff = 2k`. Closing the budget in quadrature needs
**3.2 to 3.5 mrad**, about 0.19 degrees.

That is large enough to notice on the bench and small enough that the signal
survives it: at 64 micron waist the Rayleigh range is 13.0 mm, a 3.2 mrad tilt
walks the return beam 41 microns over one Rayleigh range, which is 0.64 of a
waist, and the beams stay overlapped over 4.1 cm. So the existence of a
Doppler-free peak does not refute this candidate. Measure the tilt, or
deliberately scan it, and the hypothesis is settled either way.

**Third, and it is cheaper than either: the wing-noise discriminator.**
Half an hour, no atoms needed on the line. Detune far off resonance and
record the baseline against power, which isolates the light-linked $a$
term from anything the line contributes. Then record the monitor
photodiode of chapter 8 simultaneously and take the coherence between it
and the fluorescence baseline. A coherent share is intensity noise on the
background and regresses out of every trace offline, for free, forever. An
incoherent share growing linearly with power is shot noise on a background
that grows as the power squared, and it is attacked with the interference
filter, a pinhole at the collection image plane, and the retro dump. The
prize is the same eight-to-ten-times growth the budget measures across the
ladder, in the region where the pedestal and the band excess live, and
this record cannot currently tell the two mechanisms apart.

**And while the ruler is out:** measure u and v for the collection lens.
`config.py` derives the axial field of view as Z_c = L_par / 2m and its M is
an estimate, so Z_c is bracketed at 2.0 to 2.4 mm. The RECOLLECTION of the
f = 18 mm lens at about 50 mm from the PMT implies
M = 1.78 and Z_c = 3.4 mm, outside that bracket. Two ruler readings replace
an estimate that every ramp-geometry moment depends on.

### The vertical range is a physics setting, measured 2026-08-18

Everything above concerns the horizontal axis and the record length. The
vertical axis turns out to carry a systematic that nothing in the record had
looked for, and it was found by reading the quantisation step of the stored
samples rather than by any documented setting.

**Both 2025 sessions changed the vertical range at every rung of every power
ladder.** In the 2025-07-04 rehearsal the quantisation step grows by a factor
of 35 across the ladder while 172 to 210 digitiser steps are used per cell, so
the range tracked the signal. In the campaign the step ratio across a ladder
is 48 on 993.4121 nm, 112 on 993.4207 nm, 191 on 993.4154 nm and **596 on
993.4192 nm**, against a signal that spans only about 80, and the digitiser
steps actually used run from 486 to 3583.

**A power ladder acquired that way is not one measurement at five powers. It
is five measurements on five different instrument ranges**, and the fitted
power-law exponent inherits whatever range-to-range gain and offset error the
oscilloscope carries. Because each hyperfine line's brightness decides which
ranges it traverses, the resulting bias is ordered by brightness, which is
exactly the pattern
[the amplitude departure note](../notes/amplitude_departure_from_p2.md)
measures and could not otherwise explain.

**What this requires of the next session, in order of preference.**

1. **Hold one vertical range across a ladder.** Whether that is possible is
   arithmetic rather than taste. The signal goes as the square of the power,
   so a 25 to 225 mW ladder spans a factor of 81. With the brightest rung at
   80 per cent of full scale, an 8-bit digitiser leaves the dimmest rung
   **2.5 steps** and a 12-bit one leaves **40**, against the roughly 30 a rung
   needs before quantisation noise falls under the shot noise the record
   already fits. **So an 8-bit acquisition cannot hold one range across this
   ladder and a 12-bit one can**, which is a reason to prefer the
   higher-resolution LeCroy acquisition that is now available, stated as an
   experimental requirement rather than a convenience.
2. **If the range must change, bracket it.** Wherever the range changes,
   acquire one rung at both ranges. The ratio of two measurements of the same
   physical signal measures the range-to-range gain ratio directly, which
   converts an uncontrolled systematic into a measured calibration for about
   80 extra traces against the campaign's own 100.
3. **Never autoscale between the repeats of one cell.** Repeats measure the
   scatter, and a range change inside a cell puts an instrument step into it.
4. **Record the vertical scale, offset, coupling and any high-resolution or
   averaging mode with every trace.** Today's analysis had to recover the
   range from the quantisation step because none of it was stored, and the
   only gain record anywhere in the programme is one token in one session's
   filenames.

### The ladder order, and the one change that costs nothing

In the campaign the power descends with time, so every quantity measured
against power is also measured against elapsed time and no analysis can
separate them. That single choice is why the concave width against power
cannot be established, and it can be removed for free.

**Randomise or interleave the rung order within each ladder, and record the
seed.** Run at least one ladder in each direction per session, so that the
direction test exists by design. The archive shows what it is worth: the
rehearsal's alternating directions, run that way by convenience rather than
by intent, are the only reason the amplitude departure could be shown to be
invariant under acquisition order.

### Where the noise actually comes from, measured rather than assumed

The committed noise law is $\sigma^2 = a^2 + bV + cV^2$ per condition, with
$a$ the signal-independent term, $b$ the shot-like term proportional to
signal, and $c$ any excess multiplicative term such as laser intensity noise
on the fluorescence itself. Read across the 32 committed conditions of
[`noise_model.csv`](../../results/noise_model.csv), with the power scaling
of each term measured in
[`quantisation.csv`](../../results/quantisation.csv)'s budget rows:

  * **$a$ is not the dark floor, and reading it as one was this chapter's
    own error.** It grows linearly with laser power, from about 1.5 mV at
    25 mW to 12 to 15 mV at 225 mW, eight to ten times across the ladder.
    A dark and electronic floor cannot do that. What $a$ measures is
    light-linked background reaching the detector, and the true dark and
    electronics floor is its power-to-zero intercept, a few tenths of a
    millivolt, far below the light-linked term at any working power. **This
    is the term that limits the wings**, which is where every question this
    record leaves open lives.
  * **The excess term is absent, and that says less than it seems.** $c$ was
    needed in one of 32 conditions, so intensity noise on the fluorescence
    is below shot noise. It does not follow that laser amplitude noise buys
    nothing: intensity noise on the background enters through $a$, where it
    is degenerate with shot noise on that background, and this record has
    not separated them. The discriminator is item 9a of the day-one list,
    a coherence measurement against a monitor photodiode, and it decides
    which repair the wings need.
  * **Shot noise dominates on the line itself.** The signal-independent term
    and the shot term cross at about 8.8 mV. At a dim 20 mV signal the floor still
    contributes 31 per cent of the variance, and by 500 mV it is under 2 per
    cent. So above the dimmest rung of a power ladder this is a
    photon-counting problem, and the only lever is more photons: collection
    solid angle, quantum efficiency, or integration time.
  * **The noise is correlated over about 3.8 samples**, from the committed
    integrated autocorrelation. Effective sample counts are therefore about
    four times smaller than raw ones, which is already carried in the
    analysis and matters here for a different reason, below.

**What this means for reducing noise, in order of leverage.** Collect more
light, because the dominant term scales as the square root of the photon
number and nothing else in the budget responds. Spend nothing on amplitude
stabilisation. And at the dim end, where the floor is a third of the variance,
either raise the signal or move to counting, which
[photon counting](../wiki/photon-counting.md) sets out.

**The floor is not a dark floor, and that changes what to do about it.** The
noise law's $a$ term is nominally the zero-signal noise, and across the power
sweep it rises with power on every line, by 4.1 to 9.9 times from 25 to 225
mW. Two checks say what it is. It sits 6 to 485 times above the digitiser's
own quantisation noise, so it is not the ADC. And its log-log exponent against
power is **0.85 plus or minus 0.10**, where shot noise on a background linear
in power would give 0.5 and shot noise on a background going as the square of
the power would give 1.0. So the floor is **shot noise on a power-dependent
optical background**, dominated at the top of the range by a background that
scales roughly as the square of the power, which is what a two-photon signal
does.

**Which background, and the first candidate is refuted by its own
arithmetic.** The implied background level is $a^2/b$, which runs at a median
of 3.4 per cent of the narrow line's peak height across the twenty committed
cells. The Doppler pedestal is the obvious candidate and it is far too small:
the narrow line carries about twice the pedestal's area and is 175 times
narrower than the 941 MHz Doppler width at 130 C, so the pedestal's height
should be about 0.29 per cent of the line's, and the measurement is **11.9
times larger**. The pedestal is present and it is not what sets the floor.

**Radiation trapping was the next candidate and it is refuted too.** Trapping
is set by the optical depth, which grows with density, while the excitation is
not, so the temperature sweep separates them. Across 70, 90 and 110 C at fixed
power the floor scales as density to the power **0.42 plus or minus 0.10**,
which is the square-root scaling of shot noise on a background simply
proportional to the number of atoms, and the floor divided by the square root
of the line amplitude scales as density to the power **-0.14 plus or minus
0.07**, consistent with flat. Trapping requires that second quantity to rise
with density as the cell becomes optically thick. It does not.

**The floor is a directly measured quantity, not an artefact of the fit.**
The producer already computes the noise in the off-line region with no fitting
at all and prints its agreement with the fitted floor, and across all 32
conditions that ratio has a median of **0.953** in a range of 0.884 to 1.086.
The committed column is `sigma_wing_direct_V`. So the floor is the wing noise,
measured, and the same power scaling appears in that unfitted column directly,
at log-log exponents of 0.67 to 1.10 against power.

**So there is a real optical background and both candidates for it have
failed.** Combining the two sweeps, the background goes roughly as the atom
number to the first power and the laser power squared, which is the scaling of
the two-photon excitation rate itself. It is therefore two-photon fluorescence
that is not in the narrow line, which is what the same-beam pedestal is, and
the pedestal's magnitude is short by a factor of twelve.

**That discrepancy has an arithmetic consequence worth stating.** For the
pedestal alone to supply the measured background, the narrow-to-pedestal area
ratio would have to be 0.168 rather than the value near 2 that a good retro
reflector gives, and since that ratio is $4\rho/(1+\rho^2)$ it would require a
retro ratio near **0.04** against the accepted 0.94. Either the retro geometry
is far worse than the record assumes, which would be a significant apparatus
finding in its own right, or the background carries a component that is not
the same-beam pedestal. **This measurement cannot separate those two**, and
saying which it is needs the pedestal measured directly, which is what the
wide-scan block in this chapter already exists to do.

**A second channel disagrees with the first, and the disagreement is the most
useful thing in this section.** A constant background is absorbed by the
per-trace baseline in the mean, but not in the variance, so the fitted
baseline level and the wing noise are two independent measurements of the same
quantity. They do not agree. The background implied by the wing noise exceeds
the baseline actually sitting under the trace by a median factor of **2.7**,
and the discrepancy grows with power, from about 1.7 at 25 mW to between 4 and
23 at 225 mW.

Taken at face value that says **the off-line noise is larger than the shot
noise of the off-line signal**, by about 1.6 times in sigma at the median and
more at high power, so a component of it is not photon statistics on the
visible background at all and it grows with laser power.

**No mechanism is named for it here, deliberately.** Three interpretations of
this floor were proposed and refuted in a single evening, each because an
interpretation was reached for before the record's own measurements were
exhausted. What is established is a measurement: the wing noise is real,
directly measured, rises with power, exceeds the shot noise of the visible
background, and is not accounted for by the same-beam pedestal at the accepted
retro ratio.

**This is where analysis stops and the bench starts.** Three measurements
would close it, none of them expensive. A wide scan that resolves the pedestal
separates the background's size from the retro ratio. A detector response
curve with a calibrated source separates chain noise from optical noise. And a
trace taken with the atoms out of resonance but the laser at full power, which
costs one detuning step, separates light-dependent background from
atom-dependent background outright. Until at least one of them exists, further
analysis of these twenty cells will keep producing interpretations that the
next check refutes.

**None of this changes the practical conclusions above**, which rest on the
measurement rather than on its interpretation: the floor is not electronic,
not the digitiser, and rises with signal, so a quieter amplifier addresses
nothing and photons are the only lever.

Meanwhile $b$ is flat against power, with log-log exponents of -0.08 to +0.10
across the four lines, which is the signature of shot noise proper: $b$ is a
property of the detection chain rather than of the condition.

**What follows for noise management, and it is not what the word suggests.**

  * There is no electronic noise problem to solve. A quieter amplifier, a
    cooler detector and a better-shielded cable address a term that is not
    limiting anything.
  * The baseline and wing regions are limited by the pedestal's own shot
    noise, which is real two-photon signal at the same wavelength from the
    same atoms, so no optical filter touches it. This is the term that limits
    the wing and band-excess work specifically, not the line core.
  * The line core is limited by its own shot noise, so the lever there is
    photons. **Which way of getting them matters, and they are not equal:**
    see the ranking below, where power is linear in signal-to-noise and time
    is only square-root.
  * The retro ratio would in principle exchange pedestal against line, since the
    narrow-to-pedestal area ratio is $4\rho/(1+\rho^2)$, but that ratio is
    stationary at $\rho=1$ and the accepted 0.94 already sits within 0.2 per
    cent of its maximum. **That lever is exhausted** and is worth stating so
    nobody spends a session on it.

### Which acquisition knob actually controls the precision

The Sobol decomposition queued above has been run, over a forward model built
only from committed quantities: the measured noise law with its floor scaling
as the 0.85 power, a line height going as the square of the power and the
collection efficiency, and a width uncertainty scaling as the linewidth over
the peak signal-to-noise times the square root of the independent sample
count.

| input | first-order | total | reading |
|---|---|---|---|
| power | 0.514 | 0.648 | dominates |
| points across the line | 0.151 | 0.217 | second |
| collection efficiency | 0.101 | 0.160 | third |
| repeats | 0.083 | 0.122 | fourth |
| correlation length | 0.056 | 0.108 | least |

First-order indices sum to 0.91, so about nine per cent of the variance is
interaction and no input is a pure lever.

**Power controls two thirds of it**, which is the arithmetic behind the
recommendation to work at the top of the ladder and the reason the saturation
and light-shift costs of doing so are the binding constraint rather than the
noise. **Points across the line comes second and is nearly free**, since the
instrument is already oversampled seventy times, so the whole of that index is
available by choosing the span rather than by buying anything. Repeats and
correlation length are the smallest indices, which is worth knowing because
repeats are the most expensive thing on the list in session time and buy the
least precision per hour, while remaining essential for a different reason:
they are the only source of the within-cell error every fit here uses.

**Two things this table does not say, both of which the next section
measures.** It ranks the width of the line, so it serves what improves the
peak, and it assumes repeats are independent. Neither holds for the open
questions. The pedestal and the band excess live in the wings, where the
light-linked $a$ term rules and the ranking is different: attacking the
background is worth up to the eight-to-ten-times growth it shows across
the ladder, more than any index in this table. And back-to-back repeats
carry a condition-common share that no fit removes, so their real index is
lower still until the schedule interleaves them.

### Three ways to buy photons, and they are not equivalent

The statement that a shot-limited measurement needs more photons is true and
almost useless, because it does not say which way to get them. There are
three, and at equal total session time they differ by a factor that decides
how a session is spent.

Shot-limited means the signal-to-noise is the signal over the square root of
the signal, which is the square root of the signal.

| route | photons per bin | signal-to-noise |
|---|---|---|
| halve the scan rate | doubled | **times 1.41** |
| double the repeats | doubled | **times 1.41** |
| double the power | quadrupled | **times 2.00** |

**Slowing the scan and adding repeats are exactly equivalent in photons.**
Time is time, and the scan rate only decides how that time is distributed
across frequency. Anyone choosing between them is choosing on other grounds,
and there are strong ones below.

**Power is in a different class.** The two-photon signal goes as the square of
the power while the shot noise goes as the square root of the signal, so the
signal-to-noise goes as the power itself, linearly. Doubling the power is
worth quadrupling the time. This is the arithmetic behind the Sobol
decomposition above putting power at a total index of 0.648 while repeats sit
at 0.122, and it is why the binding constraints at the top of a power ladder
are saturation and the light shift rather than noise.

**And when time is the thing being spent, spend it on repeats rather than on a
slower scan.** They are equal in photons and unequal in everything else.

  * Repeats give the within-cell scatter, which is the only source of the
    per-condition error that every fit in this record uses. A single slow
    trace gives none, however many photons it contains.
  * Repeats average over drift. A slow scan integrates the drift into each
    trace, where nothing downstream can separate it again.
  * Repeats give independent line centres, and a slow trace gives one.
  * Five traces survive a glitch, an operator bump or a mode hop. One long
    trace does not.

**So the order is: more power until saturation and the light shift bite, then
more repeats, and the scan rate left alone.** That last clause is not laziness
about the rate, it is the measured result of the next section.

### Repeats obey root-n only when they are independent, and the schedule decides that

The bullets above earn repeats their place, and one measured fact bounds
what they buy. Back-to-back repeats share whatever is common to the visit,
the lock episode, the drift environment, the background, and the shared
part does not average down. The record measured the split for the
collisional chain ([`beta_self_probe.csv`](../../results/beta_self_probe.csv),
the pooled rows): per-repeat scatter 0.133 MHz against condition-common
0.073 MHz, a common fraction of 0.23, at which five back-to-back repeats
buy a factor 1.6 where independent ones would buy 2.24, with the gains
flattening beyond three or four. A joint fit does not repair this, and a
fit that models the repeats as independent reports the root-n it did not
earn ([the pooling page](../wiki/pooling-across-groups.md) carries the
arithmetic).

**So the schedule is part of the design: a condition's repeats are spread
across the session and the lock is re-acquired between visits**, which
converts common scatter into the kind that averages, at zero cost in
photons. Three or four back-to-back traces per visit for the within-visit
scatter, and the visits interleaved with other conditions, is the shape
that spends the same time and keeps root-n honest. The randomised rung
order above is this same rule one level up.

### Fast scans against slow scans, and why this is not the knob

The exchange has a hard limit at each end and the useful window between them is
enormous, which is the actual finding.

At the committed rate of 0.0850 MHz per ms on the transition axis, the 5.37
MHz line is crossed in **63 ms**, giving 126 samples across it at the
campaign's 0.5 ms sampling, of which only about **33 are independent** once
the measured correlation length of 3.8 samples is taken into account.

  * **The slow limit** is set by drift moving the line during one trace. At
    the held-lock drift of order 0.02 MHz per minute, keeping the movement
    under a tenth of the linewidth allows a trace of **27 minutes**, and under
    two per cent allows **5 minutes**.
  * **The fast limit** is set by the detection chain's time constant, which
    distorts and shifts the line once it approaches the line-crossing time.
    **It is genuinely unknown, and an earlier version of this chapter got it
    wrong.** The committed noise law's integrated autocorrelation is a median
    of 3.79 samples at the campaign's 0.5 ms sampling, about **1.9 ms**, and
    that was read here as the chain's response time. **It has
    since been confirmed that the archive was acquired in the oscilloscope's
    high-resolution mode**, which averages adjacent samples in hardware, so
    the 1.9 ms is a smoothing window rather than any property of the detector
    or the amplifier. The chain itself may be orders of magnitude faster and
    nothing in the archive says. The campaign's 63 ms line crossing sits 33
    smoothing windows inside the processing limit, so the acquisition as run
    was safe whatever the chain's own limit turns out to be.

**The campaign's 1 second trace therefore sits about 1600 times inside the
slow limit and at least 63 times inside the fast one.** Scan rate is not where
this experiment loses anything, and the knob people reach for first is the one
with the least to give. What the record's own
[sweep rate and detection lag](../wiki/sweep-rate-and-detection-lag.md) page
adds is that the lag degrades the skew faster than the width, so if the
asymmetry channel is ever spent the fast limit tightens and the chain's time
constant stops being optional to know.

**The one thing worth buying with rate**: more traces per unit time averages
over drift and gives more independent centre estimates, which is a real gain
that costs only the flyback.

### Triangular against sawtooth, and a control that comes free

A sawtooth ramps in one direction and flies back. A triangle ramps up and then
down, so every period yields two traces acquired in opposite directions.

**The argument for the triangle is exactly the argument this record has just
had to make the hard way.** The 2026-08-18 replication work turned on the
2025-07-04 rehearsal's alternating ladder directions, which were run that way
for convenience and are the only reason two power-dependence findings could be
separated. A triangular scan builds that control into every period: any
lineshape feature that reverses between the up-ramp and the down-ramp is a
property of the scan rather than of the atom, tested continuously and for
free.

**The argument against, and it is real.** The scanning element has hysteresis,
so the up-ramp and the down-ramp do not share a rate calibration. Averaging
the two halves naively broadens the line by the hysteresis offset and
manufactures exactly the kind of width systematic this record has spent
weeks on. A triangle therefore requires **per-direction rulers**, which the
EOM comb already supplies at no extra cost since each half-period carries its
own teeth.

**Recommendation.** Triangular, with the two directions fitted and reported
separately and never averaged before their rate calibrations are compared. The
difference between them is a measurement of the hysteresis rather than a
nuisance, and the record already treats scan hysteresis as an open quantity
in [the wavemeter reconstruction](../../results/wavemeter_reconstruction.csv).
If the two directions cannot be separately calibrated, use the sawtooth and
accept the flyback dead time, because a triangle whose halves are merged is
worse than a sawtooth.

### One campaign against several, from this record's own experience

The 2025 archive holds one frozen campaign and two excluded sessions, and the
2026-08-18 work measured what that structure costs and what it buys.

**What one campaign cannot do.** It cannot separate a parameter from anything
collinear with it. The campaign's power descends with time, so no analysis of
that session alone can distinguish power dependence from drift, and the
concave width against power is provisional for exactly that reason.

**What several campaigns buy.** Replication under changed nuisances is the
only way to establish that an effect belongs to the atom. The amplitude
departure from the square-of-power law survives precisely because a second
session with a different scope, a different power range and opposite ladder
directions reproduces it.

**What several campaigns cost, and the cost is measurable.** They introduce a
between-session offset that must be modelled rather than ignored: the same
amplitude exponent shifts by 0.165 between the campaign and the rehearsal
while the ordering across lines is identical at a rank correlation of 1.00. A
pooled fit that shares a parameter across sessions assumes an equality the
sessions may not satisfy, which is the whole subject of
[when a joint fit is legitimate](../big_picture/08_when-a-joint-fit-is-legitimate.md).

**Recommendation.** Several sessions, deliberately differing in the nuisances
and identical in the physics, with per-session nuisance parameters and a
shared physical one, and with at least one quantity measured in every session
to serve as the cross-session anchor. One long campaign gives precision that
cannot be checked, and that is the exchange this record has already paid for
once.

### How much of the triangle goes in one trace, and how many periods

**Take the whole up-and-down in one trace.** The two ramps then share the same
drift epoch, the same vertical range, the same baseline and the same
acquisition settings, separated only by the turnaround, so the direction
comparison becomes a within-trace control rather than a within-session one.
That is the strongest form of the control the 2026-08-18 replication work had
to find by luck, and it costs only record length, which the instrument has in
abundance: the rehearsal's own files are 500001 samples over 5 s at 10 µs
per sample.

**How many periods fit is not a memory question.** At the committed rate a 5 s
record spans 425 MHz on the transition axis and crosses the 5.37 MHz line in
63 ms, which is 6318 samples and about 1663 independent points once the
measured correlation length is taken into account. Against the record's own
requirement of about 90 points across the line, a single ramp is **oversampled
by a factor of 70**, so memory alone would allow about 35 up-and-down periods
per record.

**A processing limit rather than a physical one, and the difference matters.**
Each period added shortens the line crossing proportionally while the 1.9 ms
smoothing window does not shrink with it. That window belongs to the
high-resolution mode rather than to the chain, so it is a setting and not a
constraint, and choosing less smoothing raises the ceiling:

| periods per record | points across the line | line crossed in | chain time constants |
|---|---|---|---|
| 1 | 3159 | 63.2 ms | 33 |
| 2 | 1579 | 31.6 ms | 17 |
| 4 | 790 | 15.8 ms | 8 |
| 8 | 395 | 7.9 ms | 4 |
| 16 | 197 | 4.0 ms | 2 |

**So the answer is two to four periods per trace at the archive's smoothing**,
not thirty-five, and the ceiling rises if the smoothing is reduced. Two has
margin at seventeen windows and already gives two independent up-and-down
pairs inside one trace. Four is the point at which the lag begins
to matter for the asymmetry channel before it matters for the width, which is
the ordering the sweep-rate page sets out. Beyond eight the chain is
integrating across the line and the lineshape is no longer the atom's.

**The measurement that would raise this ceiling** is the same one named
earlier: a measured detector response curve, which turns the 1.9 ms inference
into a number and would license more periods if the chain is faster than the
noise correlation suggests. Until then, treat the noise correlation as the
bound and take two.

### High-resolution mode, yes. Averaging mode, no

These are different things and the answer differs.

**High-resolution mode averages adjacent samples in hardware**, exchanging
bandwidth for effective bits, and **the archive was acquired with it on**, a
fact recovered from direct recollection rather than from any stored setting.
Measured from the stored quantisation steps it delivered a median of about
**9.5 effective bits** against the instrument's native eight, reaching twelve
on the dimmest cell.

**The exchange it made was not obviously the right one.** The bits it bought were
not needed, since quantisation sits 6 to 485 times below the noise floor in
every committed condition, so finer steps bought nothing the noise did not
already swamp. What it spent was bandwidth, and that 1.9 ms window is what
caps the triangle at two to four periods above.

**It costs no signal-to-noise, which is worth stating because it looks as
though it should.** Averaging adjacent samples of white noise loses no
information: four samples at one sigma become one sample at half a sigma, and
a fit recovers the same precision either way. What is lost is only the ability
to resolve features faster than the window, and the line is crossed in 63 ms
against a 1.9 ms window.

**So keep it for a single-ramp design, reduce it if many triangle periods are
wanted, and in either case record the setting per trace.** The archive did not,
which is why that 1.9 ms was read here as a property of the detector. Every
correlation length, effective sample count and design-effect correction
downstream rests on a number that was nowhere written down.

**Averaging mode averages successive sweeps**, and it should not be used.
The reasons are specific to this analysis rather than general.

  * The within-cell error in every fit here is the scatter across repeats.
    Averaging sweeps in hardware destroys exactly that quantity and replaces
    it with nothing.
  * The residual skew is used as a shot-noise diagnostic, and averaging
    changes the noise distribution it diagnoses.
  * Drift between sweeps becomes invisible rather than measurable, and this
    record has already had to reconstruct drift it could not observe directly.
  * The operation is irreversible in the wrong direction. Individual traces
    can always be averaged offline, and an averaged trace can never be
    separated. Anything averaging mode offers is available afterwards at no
    cost, and everything it destroys is unavailable forever.

**Take single-shot traces and average offline if wanted.**

### Four peaks in one trace, which the current bench can do

The repaired cavity lock and the LeCroy's ability to hold all four peaks in a single acquisition, with the EOM on and off, change two things
at once. The known hyperfine splittings become an in-trace frequency ruler, so
every trace carries its own absolute anchor and its own nonlinearity check
without needing RF-off traces. And **all four lines are then digitised on one
range in one acquisition**, which is the cheapest available test of the
brightness-ordered departure: if its peak ordering vanishes when the four
lines share a range, the detection explanation is confirmed outright.

### The two trace kinds, sized against the instruments 

The owner asked four questions at once: which instrument for the one-peak and
the four-peak traces, how many of each, what the one-peak traces still add,
and which scanning rates. The sections around this one carry most of the
evidence, so this is the consolidation, with the instrument facts now read
from the three manufacturer manuals (held in the private tree, models and
provenance in [APPARATUS.md](../APPARATUS.md)).

**What each instrument can store per trace, and with what vertical mechanism.**

| | points per trace | vertical resolution, by mechanism |
|---|---|---|
| Agilent dso-x 3054a | 1999 used in 2025. MegaZoom memory is 2 Mpts interleaved, upgradeable to 4, and the CSV export capped at 64 K in the bench test below | 8-bit ADC. High Resolution boxcars the samples inside each stored interval, disjoint blocks, ceiling **12 bits at or above 20 us/div** printed as a table in the manual. The campaign sat four decades past the threshold, so its 11.86 measured bits are the ceiling |
| LeCroy WS3104z | **500 001 points over 5 s measured** in the rehearsal files | 8-bit ADC raw. **ERes is a moving-average FIR across stored samples**, 0.5 to 3.0 bits in half-bit steps, each step halving bandwidth. It correlates neighbouring points by construction, which is the artefact class the mode correction just removed from this record, **so the LeCroy runs raw and any smoothing happens offline**, where the kernel is known and disjoint |
| R&S RTM3004 | record length selectable **5 k to 80 MSample** | High Resolution is decimation, the average of the samples behind each stored point, same disjoint family as the Agilent, and the stored words go 8-bit to **16-bit**. Sixteen-bit words are not sixteen effective bits, and the native ADC depth is a datasheet item the manual does not print. Has Average+hr combined and a segmented HISTORY mode |

**Which instrument for which kind.** The quantitative one-peak ladders stay on
the **Agilent**: its High Resolution is disjoint and documented, its export
signature is the provenance anchor this archive already keys on, and staying
on the 2025 chain keeps the new ladders comparable with the committed ones.
The **four-peak traces go to the LeCroy**, whose measured half-million points
hold all four peaks at fine spacing, run raw with offline smoothing. **If
the RTM3004 is borrowable it takes the LeCroy's place**, on three documented
counts: disjoint high resolution at 16-bit words, the record length menu, and
HISTORY segments, which capture a whole ladder without touching the horizontal
control, the exact practice that severed the 2025 centre record. **The
dual-chain subset runs on both at once**, one split signal, because a
nonlinearity is a property of the chain and a shape error is not, and that
comparison is the one design the 2025 record cannot support.

**What the one-peak traces still add, once four-peak traces exist.** Points
density where the width lives: at fixed record length a one-peak span puts
several times more points across the line, and the collisional ladder rides
the width error linearly. Continuity: the committed beta_self construction is
built from one-peak conditions, so the next campaign's ladders splice into it
only if taken the same way. And the per-condition noise law is fitted per
trace-set, which wants repeats of the same narrow condition. **The four-peak
traces add what no one-peak trace can**: the known splittings as an in-trace
frequency ruler, every trace carrying its own absolute anchor and its own
nonlinearity check, all four lines digitised on one range in one acquisition,
which is the direct test of the brightness-ordered departure, and cross-line
height ratios free of the between-block gain drift that made the committed
amplitude ratios untestable, swinging 30 to 50 per cent between blocks.

**How many, stated as the design defaults with their sources.** Per one-peak
condition, **five repeats**, the 2025 practice the noise model is fitted on,
in blocks interleaved a-b-a so power and elapsed time stop being collinear.
**Split those five across two visits, three and two, with the lock
re-acquired between them**, because the repeats section above measures the
condition-common share at 0.23 and five back-to-back repeats therefore buy
1.6 where independent ones buy 2.24. Three within a visit still give the
within-visit scatter every fit uses, and the second visit is what makes the
pair of visits behave like independent samples. It costs no photons, only
the schedule.
Per block, **eight science and four ruler traces** at 2025-like proportions,
which the modulation menu above puts at a free 1.26 to 1.33 width-statistics
gain since the brackets exist anyway. Four-peak blocks of **five traces**, the
size at which every row of the wide-scan reach schedule still detects its
target. The dual-chain subset is **one full power ladder duplicated on both
chains**, twenty traces, prospective until the second chain is on the bench.
Counts scale as the square root, so doubling any of them buys 1.4, and the
place to spend remains power, which buys linearly.

**Rates, one setting per purpose, from the menu above.** Science and
four-peak traces at the ordinary rate, triangular, both halves kept, because
the up-down splitting measures the detection lag on a causal chain trace by
trace, which is why no separate rate ladder is needed for lag. **One block at
ten times the rate**, whose tooth clock samples at 68 Hz inside the very band
the slow blocks integrate, the single cheapest discriminator this record has
for whether the fitted Gaussian is laser noise. **The drive frequency decides
whether that block reaches at all, and it is the easier half of the setting
to get wrong.** The reach rows of
[`kernel_k7.csv`](../../results/kernel_k7.csv) weigh all four combinations
against the band: at ten times the rate the 0.5 MHz drive samples 1.70 kHz
while the 12.5 MHz drive reaches only 0.068 kHz, a factor 25 apart, because
finer teeth clock the axis more often. At the ordinary rate neither drive
reaches. **So the fast block runs the 0.5 MHz drive, and a fast block on
the 12.5 MHz teeth is a block that cannot answer the question it was taken
for.** And the fast-record
diagnostics stay on the LeCroy at 10 us sampling, which is what bounded the
chain below 10 us in the rehearsal.

## The three oscilloscopes, and what actually separates them

Three instruments are on the bench. The comparison is measured
instrument-native on both sides, from the files each scope wrote, because the
datasheet headline figures are not the deciding ones and two plausible
readings of them are both wrong.

**Provenance.** The Agilent rows come from the 100 committed `p_sweep` traces.
The LeCroy rows come from the 47 usable files of the 2025-07-04 rehearsal,
which carry the native `LECROYWS3104z` header, are unreadable to the archive
loader and live in the quarantine tree rather than under `data_raw/`. Three of
the 50 rehearsal files failed to parse and are excluded and counted here rather
than dropped silently. The LeCroy rows are therefore a measurement of a
quarantined session and carry that session's standing.

| measured per trace, median | LeCroy WS3104z | Agilent dso-x 3054a |
|---|---|---|
| record length | 500 001 points | 1999 points |
| record duration | 5.00 s | 1.00 s |
| sample rate | 100 kSa/s | 2 kSa/s |
| steps across the signal swing | 214 | **3730** |
| bits across the swing | 7.74 | **11.86** |
| baseline noise, detrended | 5505 uV | 3683 uV |
| noise over quantisation step | 1.37 | 30.1 |
| fraction of record above half maximum | 7.91 % | 5.90 % |

### The first trap, reading this as a memory-depth result

The LeCroy holds 250 times the samples, which makes it look like the
better-configured instrument. It is not. Its voltage grid is coarser by a
factor of 22, and 214 steps across a signal swing is raw eight-bit behaviour.
**The instrument with the deeper record delivered four fewer bits.** Record
length does not buy resolution on either instrument, because the smoothing
modes decimate from the internal converter rate rather than from the stored
record. The four-bit gap is the difference between a session with the smoothing
mode on and a session without it, which is a menu item rather than silicon.

### The second trap, then preferring the Agilent on bit depth

Quantisation is harmless whenever the step is small against the noise, because
the noise dithers the grid and averaging recovers what the grid discarded. The
quantisation contribution is the step over the square root of twelve, and it
adds in quadrature:

| | noise over step | quantisation as a share of noise | resulting inflation of the noise |
|---|---|---|---|
| LeCroy WS3104z | 1.37 | 19.2 % | 1.83 % |
| Agilent dso-x 3054a | 30.1 | 1.3 % | 0.008 % |

**Neither instrument was resolution-limited as it was used, and this now
holds campaign-wide**: [`quantisation.csv`](../../results/quantisation.csv)
runs the same check over all 35 quality-passed conditions, noise over step
5.2 to 246 with median 37, worst inflation 0.155 per cent, and its budget
rows carry what binds instead, the light-linked wing noise growing linearly
with power and the independent-sample count under the 1.9 ms correlation.
**Neither instrument was resolution-limited as it was used.** The Agilent's four
extra bits bought nothing on the traces that were taken. The LeCroy's 1.8 per
cent is small but is not zero, and it is the one place where the missing
smoothing mode has a measurable cost.

### Where the four bits would matter

The bits are unspent headroom rather than waste, and one specific measurement
would spend them. Holding a single vertical range across the power ladder is
the fix for the range-switching confound, and it pushes the dimmest rung far
down the screen. Whether it survives the trip was measured rather than modelled.

| rung | quantisation step | baseline noise | peak amplitude | noise over step |
|---|---|---|---|---|
| 25 mW | 20.1 uV | 1488 uV | 0.0309 V | 74.0 |
| 75 mW | 54.6 uV | 2353 uV | 0.2482 V | 43.1 |
| 125 mW | 134.3 uV | 3887 uV | 0.6757 V | 28.9 |
| 175 mW | 492.4 uV | 6973 uV | 1.3621 V | 14.2 |
| 225 mW | 1502.5 uV | 13583 uV | 2.3615 V | 9.0 |

The step spans a factor of 347 across the ladder, and on the LeCroy a factor of
35. **That spread is the direct signature of the range switching**, visible in
the recorded samples without any model of the instrument, and it is the
cleanest available evidence that a power ladder was also five instrument
settings.

Every rung as taken sits between 9 and 74 on noise over step, so quantisation
never bit anywhere in the data. The cross-rung case is tighter. Setting one
range to hold the brightest rung gives a step of 1502.5 uV, and the dimmest
rung's noise is 1487.5 uV, so the dim rung arrives at a ratio of **0.99**,
exactly at the boundary, with about 21 codes across the dim line. Feasible,
with no margin.

The margin is recoverable, because the bright range was set loosely. The 225 mW
trace occupies 38 per cent of its screen, so setting the bright range tight to
the signal buys back a factor of about 2.6 and turns marginal into safe. The
requirement is therefore two settings rather than either instrument: **the
smoothing mode on, and the bright range tight.** With both right, either scope
holds one range across the ladder. With either wrong, neither does with margin.

### The vertical range is a measured covariate, and it breaks its own confound

The quantisation step is recoverable per trace from the raw file with no fit of
any kind, which makes the vertical range an instrument covariate that can enter
an analysis rather than a setting that merely worries it.

Two facts make it useful. Within a single cell, at identical power, peak and
alignment, four of the twenty campaign cells contain traces taken on different
ranges: 4121 at 25 mW by a factor of 4.0, 4192 at 125 mW by 8.0, and 4207 at
25 mW and 175 mW by 2.0 each. More usefully, at fixed power the step differs
across the four peaks by factors of 2.3, 4.7, 3.0, 5.0 and 8.0 at 25, 75, 125,
175 and 225 mW respectively. **Peak identity is not power**, so the vertical
range is not collinear with power along the peak dimension even though it is
along the ladder.

The complication is stated rather than hidden. Range tracks brightness, and so
does the amplitude departure from the square-of-power law, so the two are
confounded with each other and the ordering evidence cannot separate them on
its own. Four different ranges at one power is the handle that can, and it uses
only data already taken.

### What the manuals say, and one thing they settle

The comparison above is measured from the files. The instrument documentation
adds three facts that measurement alone cannot supply, and one of them corrects
a reading given earlier in this chapter's history.

| from the manuals | Agilent dso-x 3054a | LeCroy WS3104z | LeCroy WaveSurfer 10 |
|---|---|---|---|
| converter | 8 bit | 8 bit | 8 bit |
| acquisition memory | 2 Mpts interleaved, 1 Mpts per channel, upgradable to 4 and 2 | fills automatically at slow timebase | 10 Mpts per channel, 20 interleaved (16 and 32 on the 10m) |
| smoothing is a | **acquisition mode** | **math function** | math function |
| ceiling on delivered bits | **12** | **11**, being 8 plus at most 3 | 11 |
| phase response of the smoothing | not stated, causal average | **exactly zero phase** | zero phase |

**Smoothing lives in a different place on the two makes.** On the Agilent, High
Resolution is an acquisition mode, so the stored samples themselves carry the
extra bits, and the campaign's measured 11.86 bits confirm it was in use. On the
LeCroy, ERes is reached by "the usual steps to set up a math function, selecting
Eres from the Filter submenu", so it produces a separate trace and a saved
channel carries eight bits whatever is on the screen.

**What that does not establish is why the rehearsal reads 7.74 bits.** Two
explanations fit the measurement equally well: ERes was configured and the
channel rather than the math trace was exported, or ERes was not enabled at all.
Nothing in the stored files distinguishes them, and an earlier version of this
section asserted the first. It is recorded as unresolved. What survives either
way is the operational point, that on this instrument a smoothed display does
not imply a smoothed export, so the file has to be checked rather than the
front panel.

**The ceilings differ by one bit and in the opposite direction to the
capability.** The Agilent's averaging table runs 2 averages to 8 bits, 4 to 9,
16 to 10, 64 to 11 and 256 or more to 12. ERes offers 0.5 to 3.0 bits in
half-bit steps, so 11 is the LeCroy ceiling. Against a dither ratio of 30 on
the traces as taken, neither ceiling binds.

**The bandwidth cost is quantified on one side only.** ERes states it exactly,
each half bit halving the passband: 0.5 bit leaves 0.5 of Nyquist, 1.0 leaves
0.241, 2.0 leaves 0.058 and 3.0 leaves 0.016, with filter lengths of 2, 5, 24
and 117 samples. The Agilent manual says only that High Resolution "limits the
oscilloscope's real-time bandwidth because it effectively acts like a low-pass
filter". For a line crossed in tens of milliseconds neither cost is reachable.

### The manuals settle the triangular-scan lag, against the earlier reading

This chapter argued that an acquisition-side filter would displace the apparent
line centre in opposite directions on the two halves of a triangular scan, and
that the splitting would therefore measure the lag. **That holds on the Agilent
and does not hold on the LeCroy.** ERes is a constant-phase FIR whose manual
states that the filters "do not distort the relative position of different
events in the waveform" and that the usual filtering delay "can be exactly
compensated during the computation". A zero-phase filter produces no
direction-dependent shift, so on the LeCroy the up and down halves give two
independent crossings and no lag calibration, because there is no lag to
calibrate. The Agilent's mode carries no such guarantee.

Two smaller manual facts bear on the design. ERes discards samples equal to the
filter length at each end of the record, between 2 and 117, which is negligible
against 500 001 points but is a reason not to place a line near a record
boundary. And the LeCroy sets its own sample rate at slow timebase so that "the
maximum number of data samples is maintained over time", which is why the
rehearsal holds 500 001 points without anyone choosing that number, whereas the
Agilent's 2000-point records were a setting.

### What actually decides the choice

Bandwidth and sample rate decide nothing here. The line is crossed in tens of
milliseconds, so a 500 MHz front end is seven orders of magnitude faster than
the signal, and the WaveSurfer 10's extra sample rate buys a fraction of a bit
against a cap already reached.

One chain property separates them on measured evidence rather than on
specification, and it is mains pickup. Addendum 13 of the preregistration
record normalises the 60 Hz line to the signal it sits on, and the LeCroy chain
carries 105 uV of mains rms on an 81 mV line against the Agilent chain's 633 uV
on a 306 mV line, which is 0.13 per cent against 0.21 per cent. The Agilent
chain is six times worse in absolute terms and 1.6 times worse once normalised.

That comparison is quoted with its own history, because the paragraph it
replaced in that addendum concluded the opposite by a factor of eight, having
compared each epoch's line to its own noise floor when the two floors differ by
about four times. It is also quoted with its own limit. For the archive as
taken the verdict is identified, quantified and negligible, because about 3.6
whole mains cycles span the line and therefore average rather than displace the
centroid. **The pickup difference is a conditional advantage rather than a
current one.** It becomes a real discriminator only for a narrower line, which
is precisely what a fixed-lock session is meant to produce, and at that point
the coherent baseline structure would no longer average away.

**The four-peak trace is a property of the laser scan, not of either
oscilloscope**, and an earlier version of this section miscast it as a 3104z
capability. The rehearsal demonstrated it on the 3104z, but a scope records
whatever span the laser sweeps. What the two instruments offer that sweep is
what differs. The Agilent writes about twelve bits into the saved file, gains
bits as the sweep slows, and exports at most 64k points. The 3104z stores half
a million points and more but exports eight bits from the channel, the smoothed
trace being reachable only through the math-function export. For a slow
four-peak sweep, resolution is the scarce quantity and points are not, so the
sweep that tests the brightness ordering belongs on the Agilent too.

**Recommendation, by role rather than by instrument.**

The quantitative campaign stays on the **Agilent**. The ladder on one vertical
range is feasible at twelve delivered bits and is not on an eight-bit channel
export, the archive's calibration and loader carry over unchanged, and a slow
sweep gains resolution exactly where the wide scans want it. Set the export
Length to its 64k limit, hold one tight range, randomise the ladder, keep both
triangle halves. A wide sweep that keeps the Doppler pedestal in frame turns
the pedestal's width into an in-situ temperature, which no 2025 session
measured, and the twelve bits are what make the low broad pedestal and the
tall narrow peaks readable on one range.

The thermometer's arithmetic is modest and worth stating. A Doppler width
scales as the square root of temperature, so the fractional width moves at
half the fractional temperature, and resolving 20 K at around 400 K asks for
a width fit good to about 2.5 per cent, which a twelve-bit wide scan supports
with room to spare. That precision is exactly what the archive lacked: the pilot's
internal temperature is carried as a range from 110 to 130 C, a factor of 3.2
in vapour density, because the record holds variac set points and no measured
temperature. One pedestal sweep per temperature block closes that class of
uncertainty for the next campaign at the cost of one slow trace each.

The **3104z** earns its place in the roles that use its actual strengths, the
deep record and the fast sampling. The day-one chain step response is its job,
since the existing bound of faster than 10 us is that instrument's sampling
limit and converting the bound into a time constant needs the fast record.
Long noise and drift captures, whose PSD frequency resolution is set by record
length, and mains monitoring are its job for the same reason.

**The strongest use of owning both is to record the same light on the two
chains at once.** Split the detector signal into both scopes for a subset of
conditions. The amplitude departure reads as a detection signature, and two
different acquisition chains digitising one photocurrent is the direct
discriminator: what appears in both records belongs to the experiment, and
what differs between them belongs to acquisition. No single instrument can
make that separation at any setting.

Four practicalities decide whether the comparison means anything.

  * **Both inputs at 1 MOhm.** A tee into one high-impedance input and one
    50 Ohm input builds a divider that changes the signal for both records,
    and the transimpedance output is not meant to drive 50 Ohm. Two
    high-impedance inputs load the source equally and negligibly.
  * **Trigger both from the same edge**, the sweep ramp, so the two records
    align sample for sample and a per-trace comparison needs no registration
    step.
  * **Compare shapes, not volts.** The two chains have different gains and
    offsets, so the observable is the ratio structure inside each record, the
    four peak amplitudes against each other per instrument, and the line
    widths. Those are dimensionless within one record and chain gain cancels.
  * **Match the smoothing philosophy, not the setting.** One range on each
    instrument, smoothing enabled on each, and the LeCroy side exported from the
    math trace, since the comparison is between best configurations and not
    between defaults.

The reading is pre-stated so the outcome cannot be argued backwards. If the
brightness-ordered amplitude departure appears with the same ordering and
magnitude in both records, it belongs to the light or the shared detector and
the 2025 finding generalises. If it differs between the records, it is
acquisition, and the difference measures which stage. Either outcome retires
the open question, which is what makes a handful of dual-recorded conditions
worth their bench time.

Repair the 3104z frequency axis before its widths are read as absolute rather
than as fractional changes. The WaveSurfer 10 offers this measurement nothing
the 3104z does not.

## Duty cycle, the largest measured inefficiency

Across the 100 campaign traces the fraction of the one second record standing
above half maximum is 5.57 per cent by mean and 5.90 per cent by median. Each
trace spends about 56 ms on the line and 944 ms on baseline, with one line per
trace on a single ramp. The rehearsal is comparable at 7.91 per cent.

Baseline is not wasted time, since it anchors the offset and supplies the wing
noise the noise law is built from, but ninety-four per cent is far more than
either use requires. Two remedies apply and they multiply. Carrying four peaks
in one trace raises the on-line fraction fourfold at no cost in acquisition
time, and trimming the scan span toward the occupied region raises it again.
Together they are worth more than any plausible gain from scanning slower,
because scanning slower buys the square root of time and these cost nothing.

## The correlation time is not the smoothing mode

Measured on baseline alone, away from the line, the integrated autocorrelation
is 2.34 samples, which is 1.17 ms at the campaign's sample interval. A boxcar
average taken to the stored sample rate returns statistically independent
samples for white input, so the smoothing mode does not account for this on its
own, and the detection chain is the obvious suspect.

**The rehearsal refutes the chain.** The LeCroy sampled at 10 us, a hundred
times finer than the campaign, and its baseline autocorrelation across 47
traces is 0.070 at a lag of 1 ms, where an analogue pole at that timescale
would require about 0.99. Its 1/e decay is 10.0 us, one single sample, so the
correlation is already gone at the instrument's own resolution limit. The
rehearsal filenames record a transimpedance gain of 10^6 V/A, which is the same
gain the campaign is presumed to have used, so **the analogue stage at that
gain does not produce a millisecond correlation.**

What survives is the acquisition mode rather than the detector. The remaining
candidate is a smoothing filter longer than the stored sample interval, which
would correlate adjacent stored samples without any analogue cause. One caveat
is carried rather than buried: the campaign's gain is recorded nowhere in the
programme, so what the rehearsal refutes is precisely the 10^6 V/A stage, not
every possible chain.

If an analogue lag is the cause, it has a consequence for triangular scans
which is worth stating because it is free to test. A lag of order 1 ms on a
line crossed in 56 ms displaces the apparent centre by roughly two per cent of
the width, and in opposite directions on the ascending and descending halves.
The midpoint of the two halves cancels the displacement and the splitting
between them measures the lag, so acquiring both halves self-calibrates the
delay in addition to giving two independent line crossings.

---

## The settings card for the next campaign

One table to carry to the bench. Every entry is justified in the sections above
and the evidence column names what it rests on rather than asserting authority.

| setting | do this | why, and on what evidence |
|---|---|---|
| vertical range | **one range for the whole ladder**, set tight to the brightest rung | the step spans a factor of 347 across the 2025 ladder, which is the range switching written into the samples |
| smoothing | **on**, and verify it reached the file | acquisition mode on the Agilent, math function on the LeCroy, and only one of those exports smoothed |
| record length | more points across the line, **not** for resolution | the CSV export caps at 64k and its Length control was low, but points buy time resolution rather than bits |
| peaks per trace | **all four, one range, EOM on and off** | 5.57 per cent duty measured, and it is the direct test of the brightness ordering |
| scan shape | triangular, keep both halves | two crossings per trace, and on a causal filter the splitting measures the lag |
| ladder order | **cycle the power several times inside a single display epoch**, not merely randomise across the session | power and elapsed time were collinear by construction in 2025, and the cost is measured in [`centre_fisher.csv`](../../results/centre_fisher.csv) (`run_centre_fisher.py`). Letting each display epoch carry a free linear drift instead of a level alone inflates the error on the light-shift amplitude by [7.3](../../results/centre_fisher.csv "ref:centre_fisher:inflation_linear_over_constant:measured")x, because a single power step and a line differ only through the arrangement of points around the change. The mechanism is sharper than collinearity: each epoch took every repeat of one power back to back, so its traces sit in two tight time clusters with one power in each. A line through two clusters is fixed by the difference of their means, and so is a one-time step. Cycling the power through the epoch separates them, since a line cannot follow a zig-zag. On the campaign's own traces and times, with nothing changed but the order, the re-ordering is forecast to be worth [7.2](../../results/centre_fisher.csv "ref:centre_fisher:ladder_order_gain:cycled_over_as_taken")x, and the rows carry that label: the light-shift error would fall from the measured [3.48](../../results/centre_fisher.csv "ref:centre_fisher:sigma_amplitude:linear_per_epoch") to [0.48](../../results/centre_fisher.csv "ref:centre_fisher:sigma_amplitude_forecast:linear_drift_cycled"), crossing the threshold at which this channel says anything at all. It is the cheapest design change in this chapter, because it costs only the order the powers are written down in. The scatter is not what limits this: it runs [0.025](../../results/centre_fisher.csv "ref:centre_fisher:sigma_per_trace_mhz:epoch_28") to [0.065](../../results/centre_fisher.csv "ref:centre_fisher:sigma_per_trace_mhz:epoch_33") MHz per trace, and with the drift pinned to a level the three multi-power epochs together separate the predicted shift from no shift at [2.1](../../results/centre_fisher.csv "ref:centre_fisher:prediction_significance_sigma:constant_per_epoch") sigma. **An earlier version of this row said a factor of 48 and a three-sigma effect per epoch, and both were wrong**: the 48 divided by a fixed-lock baseline this archive cannot evaluate, since a centre here already has its per-epoch mean removed, and the significance was quoted across a 100 mW power change that no single epoch contains. The design conclusion is unchanged, which is why the numbers moved and the recommendation did not |
| where to spend | **power first** | signal-to-noise is linear in power and square-root in everything else |
| chopping | no | the noise is 83 to 97 per cent white, and a chopper costs half the photons |
| transimpedance gain | leave it | it cancels in the shot-limited regime |

### The modulation and rate menu, one setting per purpose

The card above holds per setting. Two of its knobs, the modulation depth and
the scan rate, want different values for different purposes, and treating
either as one number wastes one channel to serve another. The menu below is
computed against the measured noise law and the corrected tooth-weight model
(`rb5s6s.forecast.comb_tooth_weights`), with the constructions stated.

**Depth costs width information per sweep, and the right frame is marginal.**
Phase modulation conserves the two-photon signal exactly and the detector
floor still taxes every copy, so a sweep whose only job is widths runs RF
off or shallow: at the 2025 depth an RF-on trace carries 0.52 of an RF-off
trace's width information on the brightest rung and 0.27 on the dimmest.
The design question is different, though, because the RF-on sweeps exist
anyway: the brackets are mandatory calibration, and M25 already ingests
ruler traces into the joint likelihood, with the no-rulers arm as the
robustness check. Their width information is therefore free and additive.
At 2025-like proportions, eight science and four ruler traces per block,
the free gain is a factor 1.26 to 1.33 in width statistics, an error factor
0.87 to 0.89, and the collisional coefficient rides the width error
linearly.

**So the depth splits by the trace's job.** The ruler information is
lever-weighted, tooth $s$ pulling on the spacing with arm $s$, so it keeps
climbing with depth: 0.48 at the 2025 depth against 0.87 to 1.48 at $2\beta$
of 2.2 to 3.0, where the width contribution still joins the fit at 0.4 to
0.5. Brackets therefore go deep. An in-block RF-on interleave leans the
other way, $2\beta$ near 1.0 to 1.3, keeping 0.65 of a science trace's
widths while still carrying its own ladder. Two depths, one joint fit.

**The teeth also clean the amplitude channel, which may be worth more than
the widths.** Within one RF-on trace every tooth and every line shares one
detector gain. The tooth pattern is RF-predicted, so intra-trace deviations
calibrate detector nonlinearity and the am admixture, and cross-line height
ratios in a wide-span RF-on trace are free of the gain drift that makes the
committed amplitude ratios swing 30 to 50 per cent between blocks. The
in-trace ladder likewise removes the sweep rate from the centre channel per
trace, which was the axis systematic that dominated 2025.

**Rate is free to first order, so it buys band placement.** Information per
crossing falls as one over the rate and crossings per hour rise with it, so
the rate is chosen by systematics, and there is a prize. Within any one
block the clock band and the width band both scale with the rate and their
ratio never closes, but the laser's noise spectrum is a property of the
laser, so the bands of different blocks compose: a block at ten times the
2025 rate has its tooth clock sampling at 68 Hz, inside the 24 Hz to 1.5 MHz
band that the science blocks' widths integrate at the ordinary rate. One
fast block therefore measures, in situ, part of the very noise that
broadens the slow blocks' lines. If the fitted Gaussian is slow laser noise
the fast clock sees excursions near 180 kHz, if it is fast noise it sees
near 4 kHz, and tooth centres resolve 96 kHz each, so a single block
separates the two readings of the laser kernel
([CLAIMS.md](../CLAIMS.md) section 2) by a factor near forty-five. It needs
no hardware beyond a knob and a record length that keeps the points per
tooth.

| scan purpose | drive and depth | rate | what it delivers |
|---|---|---|---|
| width blocks | 12.5 MHz at $2\beta$ near 1.0, RF off on dim rungs | the 2025 rate, both halves | widths at 0.65 of RF-off information, axis self-calibrated |
| pull blocks | 12.5 MHz at $2\beta$ near 1.6 | ten times, many triangles | ladder-anchored centres, and the clock inside the science blocks' width band |
| axis calibration, interleaved | the chapter 8 option in force, deep | the 2025 rate | gaps measured, whole-sweep clock |
| lag characterisation | either | one fast and one slow block | detection lag from the up against down split, linear in rate |
| depth diagnostic, occasional | $2\beta = 2.405$ | any | the carrier null pins the depth, valid at low drive or single-arm placement only |

Dim rungs run RF off because the floor makes every tooth copy a pure loss
there, and the carrier-null diagnostic moved to the last row because the
null exists only where the retro-delay phase is small
([chapter 8 section 10b.4a](08_the-acquisition-record.md)).

**The card has an executable form.** Every row above is a setting that this
card asserts is better, and an assertion about an acquisition is testable
before the acquisition happens. `examples/campaign_twin.py` builds the dataset
this card would produce, with the hyperfine amplitudes, the cascade depletion,
the saturation companions, the Stark ramp, the blackbody shift, the measured
noise law, the one-range quantisation and a session drift all present, and
fits it back. Its verdict lines report whether the design detects the predicted
light shift, whether it stays quiet when nothing is injected, and whether the
recovered widths match what was put in. A row of this card that the twin cannot
justify is a row to reconsider, and the twin is where to reconsider it, since
it costs minutes rather than a session.

### 1. The vertical range, which is the one change that matters most

Hold one range across the whole power ladder. This is first because it is the
only setting that changed a published analysis, and because it costs nothing.

The campaign switched range at every rung, and the recorded quantisation step
therefore spans a factor of 347 from the dimmest to the brightest condition. A
power ladder taken that way is five measurements on five instrument
configurations, and any trend across it carries the range change as a confound.

Feasibility was measured rather than assumed. A single range set to hold the
brightest rung gives a step of 1502.5 uV against a dim-rung noise of 1487.5 uV,
so the dim rung arrives at a dither ratio of 0.99, which is exactly the boundary
of usefulness. The margin is recoverable because the bright range was set
loosely: the 225 mW trace occupied 38 per cent of its screen, and setting that
range tight returns a factor of about 2.6. **Tight bright range plus one fixed
range is the whole of the fix.**

If the dynamic range genuinely cannot be held in one setting, split the ladder
into two overlapping blocks with at least two rungs measured on both ranges, so
the range change becomes a measurable offset rather than a confound.

### 2. Smoothing, which the campaign already had, and the check that it reached the file

**The 2025 campaign ran High Resolution and the files confirm it.** The
quantisation grid gives 11.86 bits across the signal swing, which an eight-bit
converter cannot produce at any record length. This section is therefore a
statement of what to keep rather than what to change, and it is written that
way because an earlier draft of this chapter implied the opposite.

**The digitiser was never the limitation, and would not have been at eight
bits either.** What decides that is not the bit count but the **dither ratio**,
the baseline noise divided by the quantisation step. Above about 3 the grid has
stopped mattering, because the noise moves the signal across codes and averaging
recovers what rounding discarded. The campaign ran at 30, where quantisation
contributes 0.008 per cent of the noise. The rehearsal ran at 1.37, where it
contributes 1.8 per cent. Neither session was resolution-limited.

**The check that matters is on the saved file, not the front panel**, because
the two makes put the feature in different places. An acquisition mode writes
its bits into the stored samples. A math function does not, so the channel
export carries none of it however smooth the display looks. One pass over a file
settles it: the smallest nonzero voltage difference is the quantisation step,
and the noise divided by that step is the dither ratio.

**More exported points do not buy resolution.** High Resolution averages
converter samples into each record point, so every stored point already carries
its extra bits independently of how many points are written out. The Agilent's
CSV export has a Length control and the manual caps that format at 64k points,
so the campaign's 2000 could have been larger. What that would have bought is
time resolution, more points across the line, and not vertical resolution. At
0.5 ms per point the 2025 records already placed roughly 110 points across a
56 ms crossing, which is adequate, so this is a refinement rather than a defect.

### 3. Duty cycle, which is the cheapest factor of four available

Only 5.57 per cent of each 2025 record stands above half maximum. Each trace
spent about 56 ms on the line and 944 ms on baseline, one line at a time.

Carrying all four hyperfine peaks in one trace multiplies the time on line by
four at no cost in acquisition time, and trimming the scan span toward the
occupied region multiplies it again. Both beat scanning slower, which buys only
the square root of time, and both are free.

The four-peak trace also does something no amount of averaging can. It places
every peak on one vertical range in one trace, which is the direct test of
whether the amplitude departure follows brightness rather than branching ratio.
Take it with the EOM on and off.

### 4. Scan shape and the two halves

Use a triangular scan and keep both halves rather than discarding the return.
Each half is an independent crossing of the same line under the same conditions,
so a trace yields two centre measurements instead of one.

What the two halves are worth beyond that depends on the filter's phase, and
this is the one place the choice of instrument changes the protocol. A causal
average delays features by about half its window, so the ascending and
descending halves disagree about the centre by twice that lag: their midpoint
recovers the true centre and their splitting measures the lag, which is a free
calibration. A zero-phase filter, which is what ERes specifies, produces no such
displacement, so on that instrument the two halves are simply two crossings and
there is nothing to calibrate.

Take several periods per trace where the record allows it, since periods are
repeats that cost no extra dead time.

### 5. Ladder order, and the confound to avoid repeating

In 2025 the power descended monotonically and time advanced monotonically, so
every quantity measured against power was equally a quantity measured against
elapsed time. Nothing in that dataset can separate them.

Randomise the rung order, or interleave ascending and descending blocks. At
minimum, repeat the extreme rungs at the end of the session: if the first and
last measurements of the same nominal condition disagree, the session drifted,
and that is worth knowing before the analysis rather than after. The 2025-07-04
rehearsal already ran its ladders in alternating directions and is the reason
this is stated as a requirement rather than a preference.

### 6. Where to spend the session's time

The two-photon rate goes as the square of intensity, so signal-to-noise is
linear in power and only square-root in time. Doubling the power is worth four
doublings of integration.

A sensitivity analysis over the acquisition inputs put power at 0.648, points
across the line at 0.217, collection efficiency at 0.160 and repeats at 0.122.
Between the two square-root options, prefer repeats over slower scans: they cost
the same in time and additionally deliver a direct estimate of the
trace-to-trace scatter, which a single long scan cannot give at any length.

### 7. What not to do, with the reason

Do not chop the light. The noise is 83 to 97 per cent white across the
conditions, so a lock-in has almost no excess low-frequency noise to reject, and
a chopper discards half the photons to buy it. Modulate the detuning instead if
a modulation scheme is wanted.

Do not change the transimpedance gain hoping for signal-to-noise. In the
shot-limited regime the gain multiplies signal and noise together and cancels.
Choose it for range and bandwidth, and then record it.

Do not select an instrument on sample rate or bandwidth. Both exceed what this
measurement needs by orders of magnitude.

### 8. Record what 2025 did not, which is the cheapest improvement of all

The largest single deficiency of the existing archive is not any setting. It is
that the settings were not written down, so they had to be recovered from the
samples years later, and some cannot be recovered at all.

Record per trace, in the filename or an accompanying line:

  * **vertical range**, which is recoverable from the quantisation step but
    should not have to be
  * **transimpedance gain**, for which the entire programme holds exactly one
    record, `G = 10^6` in the rehearsal filenames, so the campaign's own gain is
    simply unknown
  * **acquisition mode and its depth**, since the apparatus record currently
    carries two mutually exclusive readings of what the campaign ran
  * **cell temperature as measured**, distinguished from the variac set point,
    two of which have already been mistaken for temperatures
  * **the order and the wall-clock time** of every acquisition, which is what
    makes a drift test possible at all

None of this costs bench time. All of it decides whether a future analysis can
separate a physical effect from an instrument setting.

---

*[Session sizing and spending rules](06_sizing-and-spending-rules.md) · [The acquisition record](08_the-acquisition-record.md)*
