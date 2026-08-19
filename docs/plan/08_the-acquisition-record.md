*Chapter 8 of 11 of [the plan](../PLAN.md)*

**The question.** What must every block log, and which single omission cost a measurement?
**Takes.** The acquisition settings of chapter 7.
**Gives.** The per-block record, the comb bracket, the EOM drive, the sub-multiple coincidence design, the two-tone cascade and the mid-band alternative, the sweep-direction column, and the wavemeter shots.
**Skip if.** You want the span and sweep settings themselves, which is chapter 7.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 10b. The acquisition record itself, and the one setting whose absence cost a measurement

Section 10a sizes the span and the record length. This section is about what
must be WRITTEN DOWN while the traces are taken, and it exists because on
2026-08-16 a complete, deep, well-conditioned dataset turned out to be
uninterpretable for want of a single number nobody recorded.

### 10b.1 THE PIEZO AMPLITUDE IS RECORDED PER BLOCK, and this is not optional

The 2025-07-04 session holds fifty traces at 500,001 points, 5.000 s, 10 us
per sample: 250 times the record depth of the campaign, 50 times its time
resolution. It carries all four peaks at three powers with five repeats.

IT HAS NO EOM COMB, so its frequency axis is uncalibrated. The natural repair
is to calibrate it against the campaign's own line widths, which are known in
MHz, by measuring the same lines in ms. That works, passes its internal
consistency tests, and is DEGENERATE:

  * if the piezo ran at about three quarters of the campaign's amplitude, the
    rate is 0.0129 MHz per ms, the lines have the same width as the campaign's,
    and there is no crossing-time broadening
  * if the piezo ran at the SAME amplitude, the rate is 0.0170 MHz per ms, the
    lines are 1.26 times wider, and that width is what accumulated laser
    frequency noise would produce over a crossing 6.5 times longer.

Both reproduce the data to about one per cent. They differ only in the piezo
amplitude. A scan rate and a line width enter the observed trace as a product,
so calibrating one by assuming the other is the same degeneracy the fit already
has between the laser width and the collisional width, moved to a different
pair of variables.

ONE RECORDED NUMBER WOULD HAVE DECIDED IT. So:

  * **EXPORT THE RAMP CHANNEL WITH EVERY TRACE.** This is stricter and cheaper
    than writing the amplitude down, and 2026-08-16 showed why: the scope
    monitored the ramp during the deep session and the export took channel 2
    alone, so the number existed on the screen and never reached disk. A
    channel in the file cannot be mistranscribed, is timestamped with the data
    it belongs to, and measures the sweep nonlinearity for free, which the
    ruler currently has to reconstruct from comb residuals. Where a
    two-channel export is impossible, the amplitude goes in the block log as
    the fallback, never as the primary record.
  * The piezo response of this apparatus is MEASURED, from the 2025-05-24 two
    channel scan: 11143 MHz per volt on the transition axis, from all four
    hyperfine lines at their known separations, rms 33 MHz on a 5225 MHz span.
    So a recorded ramp in volts converts straight to a frequency axis with no
    comb at all, which makes the ramp channel a second, independent
    calibration rather than a convenience.
  * the piezo amplitude, its offset, and the ramp frequency are ALSO recorded
    in the block log, in the units the driver displays
  * so is the scope's timebase and record length, even though they are in the
    file header, because a header can be lost in a format conversion and a
    block log cannot
  * any change to any of them starts a new block, and the change is written
    down at the moment it is made rather than reconstructed afterwards.

### 10b.2 EVERY SESSION CARRIES A COMB, and it brackets the block

The 2025-07-04 session's real defect is not its missing amplitude, it is its
missing comb. A comb is the only calibration that does not borrow a number from
somewhere else, because the RF oscillator's frequency is exact.

  * NO SESSION SHIPS WITHOUT AN EOM RULER, taken at the start and at the end of
    every block, at the same scan settings as the science traces.
  * A ruler taken at different settings from the block it calibrates is not a
    ruler. The 2025-07-03 rulers share the 5 s window with the 2025-07-04
    science traces and are still useless for them: different day, different
    cell temperature, and no record that the piezo was unchanged.

### 10b.3 EOM DRIVE: modulation depth at the carrier zero

Set the modulation index to **beta = 2.405**, the first zero of the Bessel
function J0. Computed at that depth:

| tooth | amplitude | power fraction |
|---|---|---|
| carrier (n=0) | 0.0000 | 0 |
| n = +-1 | 0.5191 | 0.539 |
| n = +-2 | 0.4318 | 0.373 |
| n = +-3 | 0.1990 | 0.079 |

THE CARRIER VANISHES. That matters for three reasons. The comb becomes
symmetric with no dominant central tooth, so the fit is no longer trying to
measure weak teeth beside a strong one. The integer-fold ambiguity, which
numbered 54 of the 104 campaign combs one slot out until it was fixed in
August 2026, largely dissolves, because there is no carrier to misidentify. And
the carrier suppression no longer needs the polarisation axis to be rotated
against the crystal, which is a trick that costs power and couples the
modulation depth to an alignment.

Record the drive voltage that achieves beta = 2.405 and re-check it whenever
the crystal temperature is touched, since beta drifts with it.

### 10b.4 EOM RF FREQUENCY: raise it, and only with the wider span

The 2025 drive was 12.5 MHz. The teeth it produces sit 12.5 MHz apart on the
transition axis and 6.25 MHz apart on the laser axis, against a line 5.4 MHz
wide, which is the 2.3 linewidths this section is about.

**Why the two spacings differ, stated because an earlier version of this
section ran them together and halved every RF figure below.** The sidebands
sit at $\nu_c + n\Omega$ on each beam, and there is no optical component at
6.25 MHz anywhere in the light. A two-photon resonance needs
$\nu_a + \nu_b = \nu_0$, so $2\nu_c + s\Omega = \nu_0$ with $s = n + m$, and
the laser sits at $\nu_c = (\nu_0 - s\Omega)/2$. Consecutive $s$ move the
two-photon SUM by $\Omega$ and the LASER by $\Omega/2$. **The 6.25 MHz is
therefore a property of the scan axis rather than of any photon**, and a pair
such as $(+1,-1)$ has $s=0$ and lands on the carrier tooth rather than making
a new one. The drive is photographed at 12.500 000 000 0 MHz on the generator
and is the EOM's designed resonance ([`APPARATUS.md`](../APPARATUS.md)), and
`constants.OMEGA_EOM_HZ` carries it. The distinction is load-bearing here
because this section is a hardware recommendation, and the halved column would
have specified a modulator at half the frequency it needs. That is **2.3 linewidths between teeth**, and `rb5s6s/ruler.py`
records the consequence in its own docstring: a strong tooth's wing under a
weak neighbour is about twenty per cent of the weak peak, which is why the comb
fit has to be simultaneous over all seven teeth rather than tooth by tooth.

| separation wanted | RF drive | transition spacing | laser-axis spacing |
|---|---|---|---|
| 3 linewidths | 16.2 MHz | 16.2 MHz | 8.10 MHz |
| 4 linewidths | 21.6 MHz | 21.6 MHz | 10.80 MHz |
| **5 linewidths** | **27.0 MHz** | **27.0 MHz** | **13.50 MHz** |
| 6 linewidths | 32.4 MHz | 32.4 MHz | 16.20 MHz |

FIVE LINEWIDTHS IS THE RECOMMENDATION, a drive of about 27 MHz. At that separation a
neighbour's Lorentzian wing is a per cent rather than twenty, and each tooth
can be fitted alone as a cross-check on the simultaneous fit.

BUT THIS ONLY WORKS WITH THE WIDER SPAN, and the two changes have to be made
together:

| | drive 12.5 MHz | drive 27.0 MHz |
|---|---|---|
| teeth inside the 2025 span (85 MHz) | 6 | **3** |
| tooth POSITIONS inside the proposed span (2400 MHz) | 192 | 88 |
| teeth ABOVE NOISE in that span | 20 | 20 |

The last row is the one to read, and an earlier draft of this section did
not carry it. A tooth is a copy of an atomic line reached through a sideband
pair, so it needs both a position and a resonance, and its height falls as
$J_s(2\beta)^2$, which at the committed depth leaves about five usable teeth
per line whatever the drive. The comb is therefore FOUR CLUSTERS of five,
each spanning a few tens of MHz, with gaps of 456, 1003 and 1155 MHz on the
laser axis between them carrying no marks at all. Raising the drive widens
the clusters and never fills the gaps.

Three teeth is not a ruler. So raising the RF on the 2025 span would make the
calibration worse, and raising it on the proposed span costs nothing.

### 10b.4a A drive that is an exact sub-multiple of a pair separation

An optional measurement with its own deliverable, stated before the design
because the distinction decides whether hardware is worth buying. This
paragraph has been corrected twice and both corrections are on the record.
The first version justified the coincidence by a 185-tooth-spacing rate
extrapolation, which belongs to the 2025 narrow-span geometry alone. The
second version claimed the wide span retires the issue outright because 192
teeth join the pairs, and that conflated tooth POSITIONS with teeth: the
usable comb is four clusters of about five, and the gaps of up to 1155 MHz
between clusters carry no marks. What actually holds the pair integral in
the wide-span design is the pairs themselves as endpoint anchors, the local
rate measured inside four clusters, and INTERPOLATION between them, which
the nonlinearity map's own excess structure puts at the half-per-cent
level. Section 10b.4c is the design that converts that interpolation into a
measurement.

The division of labour that makes both rulers necessary and neither
sufficient: the atomic pairs are the ANCHOR, absolute and free but two marks
per isotope crossed tens of seconds apart, and the comb is the INTERPOLATOR
and the CLOCK, dense and local and exact against the synthesiser but carrying
no absolute frequency of its own.

What a coincidence adds is different in kind. Set the drive so that an
integer number of tooth spacings equals a same-isotope pair separation, and
tooth $n$ of one line lands ON the other line's carrier. The 85 pair is
2318.537 MHz on the transition axis and the 87 pair 5219.973 MHz, both known
to a few kHz, so the drives are exact:

| $n$ | drive for the 85 pair | drive for the 87 pair | best tooth height $J_n(2\beta)^2$ | at $2\beta$ |
|---|---|---|---|---|
| 1 | 2318.537 MHz | 5219.973 MHz | 0.339 | 1.84 |
| 2 | 1159.268 MHz | 2609.986 MHz | 0.237 | 3.05 |
| 3 | 772.846 MHz | 1739.991 MHz | 0.189 | 4.20 |
| 4 | 579.634 MHz | 1304.993 MHz | 0.160 | 5.32 |

**What it buys is a measurement, not a calibration.** The ground hyperfine
splittings are clock-grade, so a pair separation IS the 6S hyperfine
splitting, currently known to about 2 kHz through the constants of
[Ayachitula and co-workers](../lit/ayachitula2024.md). Under the coincidence
the tooth and the partner line are excited at the same laser frequency in the
same millisecond, so the 7 to 16 kHz the laser moves between ordinary pair
crossings drops out exactly, and the doublet splitting is read within one
crossing. At the measured per-crossing centre precision of 1.6 kHz, allowing
for the dimmer coincidence tooth, the splitting comes out near 3 kHz per
crossing, so one hundred crossings reach 0.3 kHz on the separation. That is a
factor of about six on the 6S hyperfine constant, a small, clean deliverable
separate from the broadening programme.

**The readout is light-shift-free at full power.** For these
$J=\tfrac12 \to J=\tfrac12$ lines under linear polarisation the two-photon
light shift is purely scalar, so it moves both members of the doublet
identically and cancels in the splitting to first order. The individual
positions carry the full shift. The splitting does not.

**The amplitude cost is mild.** The best achievable tooth height falls only
from 0.339 at $n=1$ to 0.160 at $n=4$, because the first maximum of $J_n$
falls roughly as $n^{-1/3}$. A fourth-order coincidence keeps 47 per cent of
what a first-order one could give, at a drive four times lower.

**One drive reaches both isotopes, but do not ask it to.** At 579.634 MHz the
85 pair coincides exactly at $n=4$ and the 87 pair falls at $n=9$, missing by
3.26 MHz, which is 0.94 linewidths and therefore a cleanly resolved doublet
whose splitting measures $\Delta_{87} - \tfrac94\Delta_{85}$ with no sweep
rate in it. The geometry works and the modulation depth does not: one
$2\beta$ has to feed both orders, and they want different ones. At the depth
that maximises the fourth-order tooth, 5.32, the ninth-order tooth is
$8\times10^{-5}$, which is nothing. The best compromise is $2\beta$ near 9.6,
where both sit at 0.070 and the 85 pair has lost 56 per cent. **The drive is a
synthesiser setting, so switch it rather than compromise it**: 579.634 MHz for
the 85 pair and 1304.993 MHz for the 87 pair, each at $2\beta$ near 5.3, is
two blocks and two optima.

**The table above holds only where the retro delay is negligible, and at
these drives it is not.** The weights $J_n(2\beta)^2$ assume every pathway
pair interferes with zero relative phase. With the modulator in the common
path the retro photon arrives late by $\tau(z)$, and the pathway sum
collapses exactly to a single tone at EFFECTIVE depth
$2\beta\cos(\pi f\tau)$, so an atom's tooth weights are
$J_n(2\beta\cos(\pi f\tau))^2$ averaged over the cell
(`rb5s6s.forecast.comb_tooth_weights`, with the identity tested against the
explicit pathway sum). At 12.5 MHz the phase is 0.04 to 0.09 rad and nothing
changes. At 579.634 MHz it spans 1.8 to 4.3 rad across a 10 cm cell behind a
7.5 cm standoff, the effective depth sweeps through zero, and the
fourth-order coincidence tooth collapses from 0.16 to 0.003, a factor of
fifty, killing the block as costed. The crossover pairs the zero-delay
interference had cancelled also return to the carrier, which keeps 0.62 of
its height at $2\beta = 3.05$ rather than 0.076, and never nulls at 2.405.

**The repair is placement, not power.** Put the coincidence modulator
BETWEEN THE CELL AND THE RETRO MIRROR. The forward photon is then
unmodulated, every pathway carries a distinct order, nothing interferes, and
the zero-delay weights are exact at any drive: the fourth-order tooth
returns to 0.16. The same placement makes the carrier-null depth diagnostic
valid at any frequency. The cost is one more optic in the retro path and its
3 mm aperture.

**The one magnetic systematic in this plan lives here.** The line barely
feels a laboratory field, first order doubly cancelled to under 140 Hz at
50 uT and second order under 3 kHz per state. The PAIR SEPARATION is less
lucky: it inherits the difference of the quadratic Zeeman terms, dominated
by the smaller 6S splitting, near 0.9 kHz for the 87 pair and 2.1 kHz for
the 85 pair at Earth field, against this block's 0.3 kHz target. The term
scales as the field squared, so nulling to about 15 uT with a coil pair buys
a factor of ten, and the fluxgate column of section 10b.4b supplies the
correction either way. No other block in this plan carries a magnetic term
at its own precision.

**Read it out detuned, not on the coincidence.** Two identical lines exactly
on top of each other broaden quadratically in their detuning, so the
coincidence itself is the least sensitive place to sit. Offsetting the drive
by about a linewidth over $n$, 872 kHz at $n=4$, resolves the pair and the
splitting is then read linearly.

**What it costs, as a three-option menu.** This paragraph has moved twice as
the adjudication sharpened, and the current form is a menu rather than a
single recommendation.

BASELINE, no purchase: the 12.5 MHz tank the bench has runs everything else
in this plan, with the tooth-overlap cost the simultaneous comb fit already
carries, and with the axis between the four line clusters interpolated over
stretches up to 1130 MHz.

BEST VALUE, one resonant modulator near 150 MHz, KEPT BESIDE the 12.5 tank:
at calibration depth ($2\beta$ 4.5 to 7) its clusters shrink the largest
unmarked stretch from 1130 to 255 MHz or to nothing, its teeth stand 28
linewidths apart so single-tooth fits become available, the fractional rate
per tooth pair improves twelvefold on the longer lever, and the tooth clock
marks every 1.8 s of the wide sweep instead of only four one-second islands.
The nearest accidental tooth misses the 85 pair by 13 linewidths and the 87
pair by 6, so nothing collides. 100 MHz FAILS the coverage margin, leaving
555 MHz stretches, so the band's usable edge is near 150. The 12.5 tank
stays for the fine clock band and for any narrow-span block, which are the
two jobs a 150 MHz spacing cannot do.

ONLY FOR THE METROLOGY BLOCK, a broadband modulator: the deliberate
coincidence needs 579.634 or 1304.993 MHz at $2\beta$ near 5.3, which no
resonant tank reaches, and the 6S-hyperfine-constant measurement of this
section is the one deliverable that justifies it. The 85 pair at 150 MHz
would need order sixteen, which is unreachable at any survivable depth.

### 10b.4b RECORD THE SWEEP DIRECTION, which costs one column

The manifest records no sweep direction, and one measurement is blocked
entirely on that omission. `run_tooth_scatter.py` reads the comb as a clock
and bounds the laser's non-repeating frequency excursion at the tooth spacing,
below 28.3 kHz on the transition axis at 0.15 s. That bound is on the
NON-LINEAR part only, because a linear drift within a sweep is exactly
degenerate with the sweep rate: a laser adding $at$ to an intended ramp $rt$
leaves the teeth uniformly spaced at $f_\text{EOM}/(r+a)$ and the fit returns
$r+a$.

The clock's band also scales with the sweep rate, and that is a design
lever rather than a curiosity. Within one block the clock band and the
width band scale together and their 3.6 ratio never closes. Across blocks
they compose, because the noise spectrum belongs to the laser rather than
to the scan: a block at ten times the 2025 rate puts the comb's clock at
68 Hz, and thirty times at 204 Hz, both inside the 24 Hz to 1.5 MHz band
the SCIENCE blocks' widths integrate at the ordinary rate. A fast block
therefore measures the laser's frequency noise where the slow blocks'
lineshapes absorb it, which no external instrument on this bench does, and
which is the in-situ half of resolving whether the laser kernel is Gaussian
at all. A rate ladder walks the probe across the decisive low edge of that
band.

The two halves of a triangular sweep return $r+a$ and $r-a$, so their
difference is the linear drift and their mean is the true rate. The data to do
this were taken in 2025, since the sweep is triangular and both halves are
recorded, and the separation cannot be run because nothing says which half a
trace is. **Log the direction per trace.** It is one column, it costs nothing,
and it converts an existing bound on the curvature into a measurement of the
drift itself.

**Log the ambient field once per session.** One three-axis fluxgate reading
per session, recorded beside the temperatures. The line itself is
magnetically quiet twice over, the scalar selection and the S-to-S g-factor
cancellation, so this column exists for the two places the field does act:
the vector-skew reversal test of [chapter 5](05_width-collision-amplitude.md)
and the coincidence block's quadratic Zeeman correction below.

**Log the mains phase too, and pick the fast rates off the alias grid.** A
periodic disturbance near a multiple of the tooth-crossing rate aliases into
the ladder fit's own offset and slope, where no residual test can see it,
and at the 2025 rate the 60 Hz mains sits almost exactly there. One more
column, the mains phase at trigger, lets any hum be folded coherently
across traces, and the fast-block rates of chapter 7's menu are chosen so
the tooth interval is NOT near an integer number of mains periods, which
costs nothing and keeps the clock's response at the one frequency a lab is
guaranteed to be asked about.

### 10b.4c TWO DRIVES IN CASCADE, which fills the gaps the single comb cannot

Drive the light with two tones at once, the 12.5 MHz tank and a broadband
modulator near 580 MHz in series, and the two-photon tooth amplitudes
FACTORISE: the tooth at sum offset $s_1\Omega_1 + s_2\Omega_2$ carries
$J_{s_1}(2\beta_1)^2 J_{s_2}(2\beta_2)^2$, verified numerically to five
digits. Each coarse order is therefore a displaced copy of the whole fine
cluster, and the four isolated clusters become a lattice across the span.

| $\Omega_2$ | $2\beta_2$ | placement | largest unmarked stretch | main-line survival |
|---|---|---|---|---|
| 579.6 MHz | 3.05 | common path, cell-averaged | 0 | 0.62 |
| 150 MHz | 4.5 | common path, cell-averaged | 405 MHz | 0.14 |
| 150 MHz | 7.0 | common path, cell-averaged | 0 | 0.06 |

The weights here are the cell-averaged ones of section 10b.4a rather than
the zero-delay Bessel values an earlier draft used, and the correction
CHANGES THE OPERATING MODE at the high drive. At 579.6 MHz the effective
depth sweeps through zero across the cell, so the drive is self-limiting:
the gaps fill completely at $2\beta_2$ near 3 while the main lines keep 62
per cent of their height, which is gentle enough to run DURING science
sweeps rather than only on interleaved calibration ones. At 150 MHz the
delay phase is small, the zero-delay picture nearly holds, and full gap
coverage still costs the main lines a factor near 16, so the
calibration-sweep mode stays for that option.

Two things the calibration sweeps buy that nothing else in this chapter can.
The axis between clusters becomes MEASURED rather than interpolated, which
is what the pedestal fit and the isotope-shift by-product of
[chapter 9](09_the-fixed-lock.md) ride on. And the tooth clock of section
10b.4b extends across the whole sweep: the wide sweep takes about a minute,
the single comb gives the clock marks only inside the four one-second
cluster crossings, and the cascade marks every 6.8 seconds of it, which is
exactly the stretch where the pair-separation integral accumulates drift.

The costs, stated. A second modulator in series adds insertion loss and a
second 3 mm aperture, and this bench has already met aperture clipping as a
waist systematic. And the cascade is no longer the only route to a measured
axis: a SINGLE resonant modulator near 150 MHz at calibration depth reaches
the same largest-unmarked-stretch figure, near 255 MHz, with cleaner teeth
and denser clock ticks, and 10b.4a's menu now carries it as the value
option. What the cascade alone preserves is the fine 0.15 s clock band
running simultaneously with the gap-filling lattice, and the coincidence
metrology keeps needing the broadband device either way.

### 10b.5 OSCILLOSCOPE: use the deep one, and say which one

The campaign used a 2000-point record. The 2025-07-04 session used a LeCroy
WaveSurfer 3104z at 500,001 points, and that instrument was available all
along. Record depth is a menu setting, and section 10a shows the 2025 span was
the binding constraint precisely because the record was too shallow to afford a
wider one.

  * USE THE DEEPEST RECORD THE EXPORT TOLERATES, and state the instrument model
    and the record length in the block log.
  * The 10 us sampling of the deep session puts about 45,000 points across the
    line against about 128 in the campaign, which is what makes a lineshape
    question answerable rather than arguable.
  * CHECK THE EXPORTED FILES BEFORE LEAVING THE BENCH. Three of the fifty
    LeCroy files are corrupt, two of them entirely filled with 0xFF, and this
    was found in 2026 because nothing had ever read them. A checksum and a
    line count at the end of each block would have caught it while the block
    could still be repeated.

### 10b.6 SCAN SPEED, and the two rates that must differ

Take at least one block at a DELIBERATELY DIFFERENT scan rate, with the piezo
amplitude recorded, at otherwise identical conditions.

A laser width accumulates over the time the scan takes to cross the line and a
collisional width does not, so two rates separate them where one cannot. This
is the physical lever of rule 19.22, and the whole 2026-08-15 width budget
failed to close for want of it. A factor of five in rate is ample and costs one
extra block.

The dwell requirement from 10a still applies: keep at least the 2025 0.5 ms per
point unless the detection bandwidth has been checked against a faster one,
because the transit cusp is a time-domain feature and a fast scan smears it.

## 11. Wavemeter calibration shots

The accuracy hierarchy is atoms (kHz, Ayachitula 2024) ≫ EOM comb (RF-exact
6.25 MHz teeth) ≫ wavemeter (~10 MHz), so the data calibrate the instrument,
never the reverse, and absolute calibration is a free byproduct rather than
the critical path. The session's targets are shifts, which ignore the
absolute offset. Three shots:

1. **Absolute offset**: wavemeter reading against an identified peak, once
   per session (the wavemeter has its own drift, and the atoms are in every
   scan).
2. **GHz-baseline linearity**: readings at all four peaks against the known
   hyperfine intervals.
3. **MHz transfer check during the shift grids**: log the wavemeter
   continuously and compare its reported shifts to the comb, which wins.

**The wavemeter is LOGGED to disk, never photographed.** The 2025 record's
wavemeter evidence is screen photographs digitised by hand, whose noise
floor near 3 MHz per sample is the digitiser rather than the laser, and one
adjudication of an apparent 50 s modulation spent a full analysis deciding
it was compatible with a display beat
([APPARATUS.md](../APPARATUS.md), the 06-11 notes). Three lines close that
class: log the wavemeter reading to disk at 0.1 Hz or faster with
timestamps, log the reference-cavity or air-handling duty cycle beside it
so any thermal or servo period has an independent channel to correlate
against, and record the block-gap timestamps precisely so a periodic term,
if one is ever confirmed, has a reconstructable phase per block rather than
a bound.

The comb calibrates the scan axis, not the wavemeter, so the wavemeter's own
scale must come from shot 2.

---

*[Acquisition settings](07_acquisition-settings.md) · [The fixed lock, and what it buys](09_the-fixed-lock.md)*
