# The wavemeter and the frequency axis

*[wiki index](README.md) · technique*

## What it is

A spectroscopy trace does not arrive with a frequency axis attached. What
gets recorded is a detector signal against whatever the scan actually
drives, typically a ramp voltage or a time, and turning that into frequency
is a calibration problem of its own, separate from fitting the line. Two
kinds of instrument address it, and they are not interchangeable.

An absolute reference reports what a single measurement IS, on its own. A
wavemeter is the standard one in a laser laboratory: an interferometer,
periodically recalibrated against its own internal reference, that reports
a vacuum wavelength from one shot of light. Each reading stands alone and
is not phase continuous with the next, so a handful of shots taken during a
sweep give a few points ON the sweep rather than its rate in between. A
differential reference instead reports how two things compare: an atomic
separation, fixed by the atom, or a radio-frequency comb, whose spacing is
set by a synthesiser. A systematic error that shifts both ends of an
interval together cancels out of the comparison, which is why the accuracy
ordering runs atoms first, a comb second and a wavemeter last, and never
the other way round. Only the top two are differential, and that, not
instrument quality, is the gap between them.

The everyday reason a scan needs any of this is that it is rarely linear. A
common actuator for a laser sweep is a piezoelectric element, and its
motion is not simply proportional to the driving voltage: it creeps under a
sustained voltage, and it traces a different path going up than coming
down, a hysteresis loop rather than a single curve. A ramp linear in the
driver's own voltage units is therefore not linear in frequency, and the
distortion is usually smooth rather than a formula, which is what makes
calibrating it, rather than modelling it from first principles, the
practical route.

Four practices address that directly. Fixing one scan waveform for a whole
session turns the nonlinearity into something reproducible, and only a
reproducible distortion can be calibrated. Fitting frequency against the
recorded ramp voltage through anchors of known frequency turns that curve
into a function evaluable anywhere on the ramp. Treating the two branches
of a triangular scan separately, rather than averaging them, respects that
hysteresis flips sign with direction. And an [Allan deviation](allan-deviation.md)
of line positions across many sweeps turns "the calibration repeats" from
an assumption into a number.

## What problem it solves

The question is not whether a spectrum has a frequency axis. Every plotted
trace has one. The question is whether that axis is the RIGHT one: whether
a width or a shift measured in volts or in milliseconds converts to
megahertz without smuggling in the very distortion the physics is supposed
to explain. An absolute reference alone cannot answer this, because knowing
where a sweep starts and ends says nothing about how it moved in between,
and treating a wavemeter reading as though it certified the whole sweep is
the single most tempting shortcut this problem offers. The differential
references solve the actual question, and the wavemeter is left to do only
what it is good for: fixing the absolute offset a differential measurement
cannot see on its own.

## Where this repository uses it

No committed frequency axis in this repository comes from a wavemeter.
Every width, shift and bound is built on the [EOM comb](eom-sidebands.md)
instead, the differential reference the ordering above places second. The
top of that ordering is concrete here too: the excited-state hyperfine
constants behind the two atomic-separation rulers of
[section 10c.5 of the fixed-lock chapter](../plan/09_the-fixed-lock.md) are
known to a couple of kilohertz, established by
[Ayachitula and co-workers](../lit/ayachitula2024.md) and carried in
`A_6S_RB87_HZ` and `A_6S_RB85_HZ` in `rb5s6s/constants.py`.

The wavemeter's own role is narrower. The four hyperfine components in
`rb5s6s/constants.py` (`PEAKS`) carry the 2025 campaign's file labels,
direct uncalibrated readings of the bench's HighFinesse WS-8. Comparing
each label to the transition it names, rather than to a centroid that mixes
in real hyperfine structure, finds a common offset of mean +292 MHz and
spread about 19 MHz across the four components (`label_offset_mhz` in
`rb5s6s/constants.py`), one wavemeter calibration constant rather than four
separate errors. The photographs also bound laser drift, a different
quantity from the scan axis: `DRIFT_RATE_LASER_HZ_PER_MIN` in
`rb5s6s/constants.py` is an envelope built from ten such records, and one
of them has been digitised and modelled, finding a settled noise floor once
re-lock steps and the per-interval ramp are removed, whose value is in
[`results/wavemeter_reconstruction.csv`](../../results/wavemeter_reconstruction.csv).
Neither number touches a trace's frequency axis, which is the point: a
wavemeter photograph disciplines how much drift the analysis allows for
and does not calibrate a sweep.

The mitigation stack is written down in full for the next campaign.
[Section 11 of the acquisition record](../plan/08_the-acquisition-record.md)
reserves the wavemeter for three shots: an absolute offset once per
session, a linearity check against the four known hyperfine intervals, and
a continuous transfer check where the comb keeps the final word. [Section
10b of the same chapter](../plan/08_the-acquisition-record.md) requires the
ramp channel to be exported with every trace rather than reconstructed
afterwards, so a scan rate and a line width never again have to be
untangled from one degenerate product. [Section 10c.3a of the fixed-lock
chapter](../plan/09_the-fixed-lock.md) is the calibration design itself:
one fixed waveform per session, frequency fitted against the ramp voltage
through anchors, the two branches fitted separately, and an Allan deviation
of per-sweep line positions as the next-campaign reproducibility test. The
2025 session's own nonlinearity is already mapped empirically in
[`results/ruler_nlmap.csv`](../../results/ruler_nlmap.csv), the local scan
rate relative to its mean at a dozen positions across the ramp, each with
its own uncertainty and sample count.

## What can go wrong

The first failure is treating a single wavemeter reading as though it
certified an entire sweep rather than the one point it was taken at. A
reading is absolute and isolated, a scan is continuous, and no confidence
in the instrument turns the first into the second.

The second is a degeneracy that data insufficiency creates rather than any
model. Without a saved ramp channel, a scan rate and a line width enter a
trace as the same product, so calibrating one by assuming the other can
reproduce the data closely while being wrong, which
[section 10b.1's worked example](../plan/08_the-acquisition-record.md)
found directly: two different assumed piezo amplitudes each pass an
internal consistency check and disagree on whether the line carries any
crossing-time broadening at all, the same shape of difficulty the
composite line model has between two of its own broadening terms. Close
behind it is the record itself: a handful of dated photographs is not a
time series, so, as [Allan deviation](allan-deviation.md) explains, no
reproducibility statistic can run on it, only a saved wavemeter log or a
repeated comb block produces one.

The third is an implementation trap that looks like a simplification:
averaging the two branches of a triangular ramp before separating them.
Hysteresis flips sign with the direction of travel, so a positive offset
averaged against a negative one of similar size looks like a small,
well-behaved number instead of the two effects it actually is, and the lag
it was meant to reveal disappears into the arithmetic.

The fourth is an experimental limitation. Changing any scan setting
mid-session, in particular a turning point of the ramp, reopens the
hysteresis loop, so a block that changes span partway through is two
calibrated waveforms, not one, each needing its own anchors. And a comb
reaches only a couple of islands of usable teeth around each line, so a
much wider span needs the ramp channel and the atomic separations to carry
the scale between them.

## Try it

A synthetic scan with a smooth cubic bow and a small ripple, roughly the
shape a real piezo produces, recovered from five anchors and a low-order
polynomial fit.

```python
import numpy as np

# A monotonic nonlinear voltage-to-frequency map: a linear response, a
# cubic bow from the actuator, and a small ripple no low-order polynomial
# captures exactly.
def true_map(v):
    return 11000.0 * v + 900.0 * v ** 3 + 50.0 * np.sin(6.0 * v)

v_dense = np.linspace(-1.0, 1.0, 2001)
f_true = true_map(v_dense)

# A handful of anchors, the way section 10c.3a pins the axis: known
# frequencies, atomic separations or comb islands, at known ramp voltages.
v_anchor = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
f_anchor = true_map(v_anchor)

# The naive calibration: one straight line through the two endpoints.
linear_coef = np.polyfit(v_anchor[[0, -1]], f_anchor[[0, -1]], 1)
f_linear = np.polyval(linear_coef, v_dense)

# The anchored calibration: a low-order polynomial through all five anchors.
poly_coef = np.polyfit(v_anchor, f_anchor, 3)
f_poly = np.polyval(poly_coef, v_dense)

rms_linear = np.sqrt(np.mean((f_linear - f_true) ** 2))
rms_poly = np.sqrt(np.mean((f_poly - f_true) ** 2))

print(f"{'calibration':<28}{'rms residual (MHz)':>20}")
print(f"{'two-point linear':<28}{rms_linear:20.3f}")
print(f"{'five-anchor cubic':<28}{rms_poly:20.3f}")
print(f"anchors remove {100 * (1 - rms_poly / rms_linear):.1f} percent of "
      "the distortion the straight line leaves behind")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here
misleading a reader.

## Further reading

- W. Demtröder, *Laser Spectroscopy 1: Basic Principles*, Springer, for the
  general treatment of scanning interferometers, wavemeters and frequency
  calibration in a laser laboratory.
- [Wikipedia: Wavemeter](https://en.wikipedia.org/wiki/Wavemeter) for a
  short orientation on the instrument class.
- [EOM sidebands](eom-sidebands.md), the differential reference this
  repository's frequency axis is actually built on.
- [Allan deviation](allan-deviation.md), the statistic a scan's
  reproducibility is quantified with.

---

[← The two-photon comb](the-two-photon-comb.md) · *Driving, modulating and detecting, 3 of 8* · [Sweep rate and detection lag →](sweep-rate-and-detection-lag.md)
