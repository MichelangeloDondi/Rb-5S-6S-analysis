*Chapter 8 of 11 of [the plan](../PLAN.md)*

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

The 2025 RF was 6.25 MHz, which is 12.5 MHz on the transition axis, against a
line 5.4 MHz wide. That is **2.3 linewidths between teeth**, and `rb5s6s/ruler.py`
records the consequence in its own docstring: a strong tooth's wing under a
weak neighbour is about twenty per cent of the weak peak, which is why the comb
fit has to be simultaneous over all seven teeth rather than tooth by tooth.

| separation wanted | RF | transition spacing |
|---|---|---|
| 3 linewidths | 8.10 MHz | 16.2 MHz |
| 4 linewidths | 10.80 MHz | 21.6 MHz |
| **5 linewidths** | **13.50 MHz** | **27.0 MHz** |
| 6 linewidths | 16.20 MHz | 32.4 MHz |

FIVE LINEWIDTHS IS THE RECOMMENDATION, about 13.5 MHz. At that separation a
neighbour's Lorentzian wing is a per cent rather than twenty, and each tooth
can be fitted alone as a cross-check on the simultaneous fit.

BUT THIS ONLY WORKS WITH THE WIDER SPAN, and the two changes have to be made
together:

| | RF 6.25 MHz | RF 13.5 MHz |
|---|---|---|
| teeth inside the 2025 span (85 MHz) | 6 | **3** |
| teeth inside the proposed span (2400 MHz) | 192 | 88 |

Three teeth is not a ruler. So raising the RF on the 2025 span would make the
calibration worse, and raising it on the proposed span costs nothing.

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

The comb calibrates the scan axis, not the wavemeter, so the wavemeter's own
scale must come from shot 2.

---

*[Acquisition settings](07_acquisition-settings.md) · [The fixed lock, and what it buys](09_the-fixed-lock.md)*
