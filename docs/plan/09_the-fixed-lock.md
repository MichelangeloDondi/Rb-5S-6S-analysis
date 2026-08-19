*Chapter 9 of 11 of [the plan](../PLAN.md)*

## 10c. The fixed cavity lock, and the settings that follow from it

Written 2026-08-16 after the cavity lock was repaired. Section 10a sizes the
span and the record, 10b records what the acquisition must log, and this
section is about what the repaired lock and the two LeCroy oscilloscopes make
possible that the 2025 session could not attempt. Every number below is either
computed from a committed quantity, in which case its source is named, or
marked as a MEASUREMENT THE BENCH MUST SUPPLY. None of it is settled by
argument alone.

### 10c.1 THE PRIZE IS IDENTIFIABILITY, NOT A NARROWER LINE

The instinct that a better lock gives a narrower line is nearly wrong here,
and the arithmetic matters because it decides where the effort goes. The
natural width is 3.4925 MHz and it is the floor. Driving the laser
contribution from its committed median of 1.738 MHz down to 0.2 would move
the total width only from about 5.29 to 4.90 MHz, a nine per cent change, and
the transit kernel would rise from 17.6 to 19.0 per cent of the line. The
record length of section 10a is unaffected, and the transit cusp does not
become materially easier to resolve from the lock alone.

WHAT DOES CHANGE IS THE DEGENERACY. The collisional and laser widths trade
against each other inside every single-condition fit, at a correlation whose
median across the 32 committed conditions is -0.90 and whose range runs -0.92
to -0.63 (`results/linefit_conditions.csv`, column `corr`), and that is the
central obstacle of the whole analysis. AN EARLIER VERSION OF THIS SENTENCE
QUOTED -0.85 WITHOUT A SOURCE. The correction matters beyond the digit: three
different quantities in this repository can be called the correlation between
the two widths, namely this per-condition fit covariance, the global
identifiability map's own correlation, and the ridge direction the profile
likelihood traces, and they are different statistical objects with different
values. A number of this kind is only meaningful with its construction named, and
the pinning comparison now has a committed producer that names its own:
`scripts/run_width_pinning.py`, on a bright synthetic condition with
signal-dependent noise, returns a collisional-width scatter of 0.0073 MHz
with both widths free and 0.0021 MHz with the laser width KNOWN, a factor of
3.4. The factor, not the idealised absolutes, is the point: pinning the
laser width is the difference between reporting a bound and reporting a
measurement.

SO THE HIGHEST-VALUE ITEM IN THE CAMPAIGN IS AN INDEPENDENT MEASUREMENT OF THE
LASER WIDTH. A beat note against a second laser, a cavity ringdown, or a
delayed self-heterodyne, any of which the repaired lock makes viable and none
of which the 2025 session had. Deliverable C2 is an upper bound precisely
because no independent laser diagnostic existed, and this converts it.

A SECOND CONSEQUENCE, and it is a change to the fitting structure rather than
to the hardware. The statistics chapter shares the laser width per temperature
rather than globally, and says in terms that global sharing is what manufactures
a false detection when the laser drifts between blocks, while for a stable lock
global sharing becomes correct. If the repaired lock holds across a session,
the sharing level should be revisited, and the evidence for the change is a
measured drift rate rather than the fact of the repair.

### 10c.2 DRIFT, AND WHY THE SWEEP TIMING IS NOW A CHOICE

At the cavity-locked rate of the 2025-06-11 record, 0.19 MHz/min, a 28.4 s
sweep across 2400 MHz smears 0.090 MHz, which is comparable to the collisional
width's own error and is what made fast sweeps necessary rather than merely
useful. If the repaired lock reaches 0.02 MHz/min the same sweep smears 0.009
MHz and the argument dissolves.

MEASURE THE NEW DRIFT RATE BEFORE FIXING THE TIMING. Fast sweeping remains
worth having for its own reasons, more repeats per unit time, per-sweep centres
that absorb what drift remains, and an Allan deviation of line centres that
separates drift from jitter. It is no longer forced.

THE SPEED CEILING IS NO LONGER KNOWN TO BE THE DETECTION CHAIN. The noise
law's correlation time is 3.79 samples at the 2025 sampling, which is 1.9 ms,
and holding the line crossing at three times that would give about 0.94 MHz per
ms, roughly eleven times the 2025 rate, and a 2400 MHz sweep in about two and a
half seconds. **That ceiling assumed the 1.9 ms belongs to the chain, and the
rehearsal refutes the assumption.** The LeCroy sampled the same experiment at
10 us with the same 10^6 V/A gain, and its baseline correlation is 0.070 at
1 ms against the 0.99 an analogue corner would require, with 1/e decay inside a
single sample. The chain is faster than 10 us, so it is not the binding
constraint, and the 1.9 ms is a property of the campaign's acquisition mode
rather than of the detector.

The timing design is therefore less constrained than this chapter assumed, by
up to two orders of magnitude, and the binding limit is now unidentified rather
than known. Photon budget and lock drift are the candidates. The day-one step
response below is still worth taking, because a bound at the sampling limit is
not a measured time constant, but it is no longer the item the whole timing
plan waits on.

### 10c.3 THE TWO-SPEED SWEEP

Narrow features need dwell and the pedestal does not, so a uniform rate over a
2400 MHz span spends almost all of its time where there is nothing to resolve.
A sawtooth that slows across each line window and runs fast between them serves
both, and one direction only keeps the retrace mirror out of the band entirely,
which section 10a's third limit identifies as a cost of the triangular ramp.

Sweeping one way discards the return, so the duty cycle halves and the flyback
needs a settle segment whose length the bench must measure, by comparing tooth
spacing early and late in a comb block.

THE SLOW SEGMENT IS REQUIRED AND NOT MERELY CONVENIENT, and the reason is
measured rather than argued. A simulation of the detection lag across five
sweep rates, preregistered with a null test and a ceiling test, finds that at
0.94 MHz per ms the fitted width inflates by 24.6 per cent while the
standardised skew rises from 0.055 to 0.083. The observable the light shift is
read from therefore degrades at twice the fractional rate of the width, so the
fast segment belongs between the lines and never across them.

### 10c.3a THE SCAN AXIS, AND WHAT TO DO ABOUT ITS NONLINEARITY

The frequency scan is the laser's own internal cavity scan, driven from the
control software, which specifies the scan width in gigahertz rather than in
piezo volts. There is therefore a vendor calibration layer under this
experiment, and the question is not whether the piezo is linear but how linear
that calibration is over the span actually used. Each item below carries what
kind of statement it is.

KNOWN FROM 2025. Fitting one linear rate to all four components of the
2025-05-24 two-channel scan leaves an rms of 33 MHz over 5225 MHz, which is at
most 0.6 per cent integrated nonlinearity and includes the line-position
measurement error, so it is an upper bound rather than an estimate. The
2025 sweep nonlinearity is also mapped empirically in
`results/ruler_nlmap.csv`. Both were earned before the lock repair, so they
bound the repaired configuration rather than describing it.

DESIGN RULE, FIXED WAVEFORM. Nonlinearity that repeats is calibration and only
its sweep-to-sweep variation is noise, so every science sweep uses the same
width, centre, rate and direction. Changing a turning point mid-session
re-opens the hysteresis loop and invalidates the session's calibration, so a
narrow block and a wide block are different waveforms with different curves,
never one curve rescaled.

DESIGN RULE, THE AXIS IS FITTED FROM ITS ANCHORS. The frequency as a function
of the recorded ramp voltage is a smooth per-session spline through everything
the design already provides: the four line centres, both atomic pair
separations closing over different segments, the comb islands giving the local
rate at each line, and the ramp channel of 10b.1 recorded per block. The
oscilloscope monitor that carries the ramp is the resonator voltage the control
software already exposes, so this costs a channel and no hardware.

DESIGN RULE, THE TWO BRANCHES ARE FITTED SEPARATELY. If the ramp is
triangular, the up and down branches are never averaged blindly. Their
per-sweep disagreement is the hysteresis and lag monitor, and because it flips
sign with direction it is separable from the rate-scaled lag of 10c.3.

NEXT-CAMPAIGN TEST. The reproducibility of the axis is measured, not assumed:
an Allan deviation of the per-sweep line positions, which the sequence-mode
timestamps give at no extra cost, says how much of the curve repeats and
therefore how much of it calibration can remove. A useful pre-bench rehearsal
is to inject the measured `results/ruler_nlmap.csv` curve into the widescan
simulation and check that the spline plus anchors recovers it, preregistered in
the usual form.

WHY THIS MATTERS MOST FOR THE PEDESTAL. A 0.6 per cent distortion of the axis
moves a 942 MHz pedestal width by about 6 MHz, which is a few kelvin on the
thermometry of 10c.7, so the axis calibration is what protects that observable
in particular rather than a uniform refinement of everything.

### 10c.4 EOM PARAMETERS

The modulation depth stays at the carrier zero of 10b.3, beta near 1.202,
which is where the two-photon comb amplitude J_k(2 beta) has its first zero.

THE PEDESTAL NULLS WITH THE CARRIER, which had to be checked because a drive
that suppressed the pedestal would defeat the widescan's purpose. The
same-beam term that drives the pedestal obeys the same Bessel law, verified
numerically to six decimals, and the retro delay does not rescue the carrier:
even with the mirror a metre away at 13.5 MHz the residual central amplitude
is about three parts in a thousand.

THE COMB IS TWO ISLANDS AND NOT A CARPET. At beta near 1.202 only orders up to
about three carry more than one per cent of the power, so at the 27 MHz
spacing of 10b.4 the comb reaches about plus or minus 81 MHz around each line.
A comb spanning 2400 MHz would need a modulation depth no resonant modulator
will reach. The calibration therefore comes in three parts: the teeth give the
local rate near each line, the recorded ramp channel carries the shape between
them, and the atomic separation below fixes the global scale.

RUN THE WIDESCAN WITH THE MODULATOR OFF. A comb across a wide span scatters a
copy of the line and its pedestal through the very baseline the widescan
exists to identify. Calibration blocks and pedestal blocks are separate blocks,
bracketed as 10b.2 requires.

### 10c.5 TWO COMPONENTS IN ONE SWEEP, AND AN ATOMIC RULER

From the campaign file labels, the four components sit at 0, 911.3, 3220.0 and
5225.0 MHz on the transition axis. Two pairs fit inside a 2400 MHz span, and
one of them is special: 993.4192 and 993.4154 are BOTH the 85 isotope, so their
separation of 2308.7 MHz is fixed by the 85Rb hyperfine constants alone, with
no isotope shift in it. The identification test already locks those spacings to
about one per cent.

Catching that pair in one sweep puts an absolute frequency reference inside
every trace, independent of the modulator, the piezo and the wavemeter. The
piezo affords it: at the measured 11143 MHz per volt the full ramp reaches
about 7.4 GHz, so a span of 2400 to 2600 MHz is far from the rail.

ONE CAVEAT THAT MUST BE HANDLED ON THE DAY. The label-derived separation is
known to about 33 MHz, which is larger than one comb period, so whether a comb
tooth lands on the second line cannot be predicted in advance. Pin the
separation with one quick scan, then choose the drive frequency to keep the
teeth clear of both lines.

THE RULER'S PRECISION IS NOT THE LABEL'S. A same-isotope separation on the
transition axis is the ground hyperfine splitting minus the 6S splitting, and
both are measured quantities this repository already holds as constants. The
ground splittings are clock-grade definitions and the 6S constants are known to
2 kHz ([Ayachitula and co-workers](../lit/ayachitula2024.md)), so the separations
are 2318.537 MHz for the 85 pair and 5219.973 MHz for the 87 pair, each good to
a few kHz. The label-derived values sit 9.8 and 5.0 MHz away, well inside the
33 MHz the labels carry, so the two routes agree and the constants are the
precise one. THE AXIS IS THEREFORE ANCHORED BY THE CONSTANTS RATHER THAN
MEASURING THEM: at 2 kHz the excited-state constant is far stronger than
anything a sweep calibration will reach, so it is an input to the ruler and not
an output of it.

THE SECOND PAIR SPANS THE WHOLE MANIFOLD. 993.4207 and 993.4121 are both the 87
isotope, and their separation of 5219.973 MHz covers the entire four-component
structure. The piezo reaches it: at the measured 11143 MHz per volt the full
ramp covers about 7.4 GHz. So one wide sweep carries TWO independent rulers,
one closing across the middle of the span and one across all of it, and their
disagreement is a direct measurement of whatever axis nonlinearity survives the
calibration. That redundancy is the point: a single ruler can only be trusted,
while two rulers over different segments can be tested against each other.

TWO CONSEQUENCES OF RUNNING THE FULL SPAN. The cross-isotope separations in the
same trace carry the 5S to 6S ISOTOPE SHIFT, which is a by-product rather than
a target and needs a literature check before any claim about it is worth
making. And the baseline is no longer one pedestal: at 942 MHz of pedestal
width against a 911 MHz nearest separation the four pedestals overlap, so the
widescan baseline over the full manifold is a SUM of four pedestals. That is an
extension of the single-pedestal form the B1 simulation verified, not a
different model, but it is an extension the fit must carry explicitly.

---

*[The acquisition record](08_the-acquisition-record.md) · [The instrument and the session](10_the-fixed-lock-instrument.md)*
