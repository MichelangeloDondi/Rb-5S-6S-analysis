# The wavemeter and the frequency axis

*[wiki index](README.md) · technique*

**The question.** What separates an absolute frequency reference from a
differential one, and why the accuracy ordering runs atoms first, comb
second, wavemeter last.
**Takes.** What a phase-modulated sideband comb is, from
[EOM sidebands](eom-sidebands.md), the differential reference compared
here against a wavemeter.
**Gives.** The ordering of reference types by what a systematic error does
under a comparison, four calibration practices for a nonlinear piezo scan,
and where this repository's wavemeter numbers sit outside the frequency
axis.
**Skip if.** The comb's mechanics without the comparison to a wavemeter:
covered by [EOM sidebands](eom-sidebands.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A spectroscopy trace has no frequency axis attached: what gets recorded
is a detector signal against a ramp voltage or a time, and converting
that into frequency is a calibration problem separate from fitting the
line.

An absolute reference reports a single measurement, on its own: a
wavemeter, the standard instrument in a laser laboratory, is an
interferometer, periodically recalibrated against its own reference,
reporting a vacuum wavelength from one shot of light. Each reading stands
alone, not phase continuous with the next, so a handful of shots during a
sweep give only a few points, not its rate in between. A
differential reference instead compares two things: an atomic separation,
fixed by the atom, or a radio-frequency comb, whose spacing is set by a
synthesiser. A systematic error shifting both ends of an interval
together cancels out of the comparison, which is why the accuracy
ordering runs atoms first, a comb second, a wavemeter last.

A scan needs this because it is rarely linear: a piezoelectric actuator's
motion is not proportional to the driving voltage, creeping under
sustained voltage and tracing a different path up than down, a hysteresis
loop instead of a single curve. The distortion is usually smooth, not a
formula, so calibrating it is the practical choice. Four practices do
that:

- one scan waveform fixed per session, keeping nonlinearity reproducible
- frequency fitted against the ramp voltage through known-frequency
  anchors, evaluable anywhere
- the two branches of a triangular scan fitted separately, since
  hysteresis flips sign with direction
- an [Allan deviation](allan-deviation.md) of line positions across many
  sweeps, turning repeatability into a number

## What problem it solves

A plotted trace always has a frequency axis. The question is whether it
is the right one: whether a width or shift in volts or milliseconds
converts to megahertz without smuggling in the distortion the physics is
supposed to explain. An absolute reference alone cannot certify this:
knowing where a sweep starts and ends says nothing about how it moved in
between. The differential references answer it, leaving the wavemeter to
fix the offset a differential measurement cannot see on its own.

## Where this repository uses it

No committed frequency axis here comes from a wavemeter: every width,
shift and bound is built on the [EOM comb](eom-sidebands.md), the
ordering's second-place reference. The excited-state hyperfine constants
behind the two atomic-separation rulers of
[section 10c.5 of the fixed-lock chapter](../plan/09_the-fixed-lock.md) are
known to a couple of kilohertz, established by
[Ayachitula and co-workers](../lit/ayachitula2024.md), carried in
`A_6S_RB87_HZ` and `A_6S_RB85_HZ` in `rb5s6s/constants.py`.

![A wavemeter photograph record reconstructed into a laser-detuning time series](../../figures/fig14_wavemeter_reconstruction.png)

*The 2025-06-11 photographed wavemeter record reconstructed into a
laser-detuning time series, with re-lock steps modelled and the campaign
segment's residual scatter shown alongside it.*

The wavemeter's role is narrower: the four hyperfine components in
`rb5s6s/constants.py` (`PEAKS`) carry the 2025 campaign's file labels,
uncalibrated readings from the bench's HighFinesse ws-8. Comparing each
label to its named transition finds a common offset of mean +292 MHz and
spread about 19 MHz across the four (`label_offset_mhz`): one calibration
constant, not four separate errors. The photographs also bound laser
drift: `DRIFT_RATE_LASER_HZ_PER_MIN` is an envelope from ten such
records, one digitised and modelled to a settled noise floor once
re-lock steps and the per-interval ramp are removed, in
[`results/wavemeter_reconstruction.csv`](../../results/wavemeter_reconstruction.csv).
Neither number touches a trace's frequency axis: a photograph disciplines
how much drift is allowed for, not the sweep.

The next campaign's mitigation stack:

- [Section 11 of the acquisition record](../plan/08_the-acquisition-record.md)
  reserves the wavemeter for three shots: an absolute offset once per
  session, a linearity check against the four hyperfine intervals, and a
  continuous transfer check with the comb as final word
- [Section 10b](../plan/08_the-acquisition-record.md) requires the ramp
  channel exported with every trace instead of reconstructed afterwards
- [Section 10c.3a of the fixed-lock chapter](../plan/09_the-fixed-lock.md)
  writes the same four practices into the design, the Allan deviation of
  per-sweep line positions as its reproducibility test

The 2025 session's nonlinearity is mapped empirically in
[`results/ruler_nlmap.csv`](../../results/ruler_nlmap.csv): local scan
rate relative to its mean at a dozen ramp positions, each with its own
uncertainty and sample count.

## The comb as a clock

The comb's teeth sit at exact multiples of an RF drive, a ruler laid down
by an oscillator. Fitting each tooth centre freely, instead of on a rigid
grid, and subtracting the predicted ladder leaves the departures: the
optical frequency wandering against that oscillator while the sweep
crosses them, averaged over one tooth spacing.

![One EOM-ruler trace with its tooth-centre fit and scan-rate deviation](../../figures/fig8_ruler.png)

*One EOM-ruler trace with its seven-tooth comb fit and the local scan-rate
deviation used to build `results/ruler_nlmap.csv`.*

The departure splits in two:

    tooth departure = sweep nonlinearity + laser frequency excursion

The ramp repeats every sweep and the laser does not, so the mean over many
traces is the nonlinearity and the scatter about it is the laser. A
pipeline computing only the mean has measured the sweep and thrown away
the laser.

**What it cannot see.** A linear drift inside one sweep is exactly
degenerate with the sweep rate: if the laser adds $at$ to an intended ramp
$rt$, the teeth stay uniformly spaced at $f_\text{EOM}/(r+a)$, the fit
returns $r+a$, and only curvature survives. The two halves of a
triangular sweep return $r+a$ and $r-a$, separating them and needing the
sweep direction recorded.

**What it gave here.** Over 509 free-fitted tooth centres from 104 traces,
the scatter about the sweep map sits at $\chi^2/\text{dof} = 0.53$: no
excess, so the result is a limit, the non-repeating excursion below
28.3 kHz on the transition axis at 0.15 s averaging, $4.7\times10^{-11}$
fractional, set by the tooth-centre precision of about 96 kHz, not the
laser.

**Periodic disturbances alias into the fit.** A disturbance near a
multiple of the tooth-crossing rate aliases to a low frequency the fit
absorbs into its offset and slope: a 60 Hz mains line against a 6.8 Hz
tooth rate aliases to about 1.2 Hz, so a periodogram of the residuals
returns a null there because the instrument cannot respond, not the line
being absent. The ceiling test catches this: inject the signal into
synthetic data and confirm detection before trusting a real-data null. A
non-blind probe, FM-to-AM conversion on the line's flanks, is in
[laser frequency noise](laser-frequency-noise-and-the-linewidth.md).

**Why it matters beyond calibration.** The lineshape fits a Gaussian
kernel for the laser, produced by slow frequency noise. This limit
excludes the low-frequency-heavy spectra that would justify it, bearing
on the model form, not only the axis. See
[identifiability](identifiability.md) and
[the Allan deviation](allan-deviation.md) for how the width channel and
the reproducibility statistic use it.

## What can go wrong

The first failure treats a single wavemeter reading as though it
certified an entire sweep, not the one point it was taken from.

The second is a degeneracy from data insufficiency, not from any model: a
scan rate and a line width enter a trace as the same product when the
ramp channel is not saved, so calibrating one by assuming the other can
reproduce the data closely while being wrong.
[Section 10b.1's worked example](../plan/08_the-acquisition-record.md)
shows two assumed piezo amplitudes both passing an internal consistency
check while disagreeing on whether the line carries any crossing-time
broadening at all, the same shape of difficulty the composite line model
has between two of its own broadening terms. A handful of dated
photographs is likewise not a time series: only a saved log or a repeated
comb block gives a reproducibility statistic, per
[Allan deviation](allan-deviation.md).

The third is averaging the two branches of a triangular ramp before
separating them, since hysteresis flips sign with direction and the two
effects cancel toward a small, misleading number.

The fourth is changing any scan setting mid-session, reopening the
hysteresis loop and needing two calibrated waveforms, each needing its
own anchors. A comb also reaches only a couple of islands of teeth per
line, so a wide span needs the ramp channel and atomic separations to
carry the scale between them.

## How linear the axis must be, for the moment channel

This page's calibration practices say how to correct a nonlinear scan. This
section says how well, and the tolerance is far tighter than a centre fit
needs, because the third cumulant of the line reads an asymmetry and a
nonlinear sweep manufactures one.

Write the true frequency against the assumed axis as
$\nu = \hat\nu + \alpha\hat\nu^2$. The rate then varies across an analysis
window of half-width $W$ by a fraction $\epsilon$ equal to $2\alpha W$, and the
induced third cumulant is linear in that fraction. Measured on the production estimator against the same
composed line the campaign forecasts:

| configuration | window | the light shift's own third cumulant | rate variation that fakes it |
|---|---|---|---|
| 2025, 64 microns | 6 MHz | [0.00011901](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:k3_light_shift") MHz cubed | [0.00223](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:rate_variation_tolerance") per cent |
| campaign, 40 microns, the tightest licensed | 6 MHz | [0.00153465](../../results/sweep_linearity.csv "ref:sweep_linearity:campaign_40um:k3_light_shift") MHz cubed | [0.0290](../../results/sweep_linearity.csv "ref:sweep_linearity:campaign_40um:rate_variation_tolerance") per cent |
| campaign, 16 microns, outside the model's licence | 12 MHz | [0.574892](../../results/sweep_linearity.csv "ref:sweep_linearity:campaign_16um:k3_light_shift") MHz cubed | [1.238](../../results/sweep_linearity.csv "ref:sweep_linearity:campaign_16um:rate_variation_tolerance") per cent |

**A bow of two parts in a thousand of the actuator's travel already reaches
two parts in a hundred thousand across a 6 MHz window**, so the 2025 third
cumulant was unavailable on its frequency axis whatever its counts had been. The
campaign's licensed waist asks for a bow under about two per cent, which is a
different matter and a measurable one.

**The nonlinearity is the actuator's and not the scan's**, which the first
version of this section had backwards. A piezo's bow is a fraction of its
travel, so the same actuator scanned over a narrow sub-span at the same
position has the same rate variation across the same window: the producer's
sub-scan row reads [0.0240](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:eps_bow_eta2_subscan_200MHz_same_actuator") per cent against
[0.0240](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:eps_bow_eta2") on the full travel. Zooming costs nothing here. What the
wide sweep buys is anchors from which the bow is measured and corrected, and
that is the argument for it.

**The law, and what it asks of the actuator.** With the best-fit line removed
a quadratic bow gives a rate variation across a window of half-width W of
exactly twelve times the departure times W over the travel, on rung two. Over
a 6 GHz travel a bow of two per cent gives [0.0240](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:eps_bow_eta2") per cent across a
6 MHz window, which fails the 64 micron tolerance by eleven and clears the
40 micron one by 1.2, and a ten per cent bow fails 40 microns by four. So the
moment channel at the campaign's licensed waist needs an actuator linear to
about two per cent of its travel, or the bow taken out from the anchors.

**A short-scale departure does not dilute, and above a small amplitude it
reverses the sweep.** A ripple of N cycles across the travel replaces the
twelve by the square of two pi N. At fifty cycles a tenth of a per cent gives
[10.0664](../../results/sweep_linearity.csv "ref:sweep_linearity:archive:eps_ripple50_eta0.1_p95_over_phase") per cent, and above about a third of a per cent the
sweep runs backwards inside the window and no rate variation exists. The cubic
bow and the ripple of the worked example below are therefore not two
illustrations of one thing: the anchored polynomial recovers the first and
cannot see the second, and the second is what the moment channel reads.

**The design consequences.** The actuator's curvature, and not the span
scanned, sets whether the moment channel can be read. A wide sweep is worth
having for the anchors that measure it, and the ramp monitor earns a permanent
channel because ripple, creep and stick-slip are exactly what no anchor set
recovers.

## Try it

A synthetic scan with a cubic bow and a ripple, recovered from five
anchors and a low-order polynomial fit.

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
so one that stops working fails the suite instead of sitting here
misleading a reader.

## Further reading

- W. Demtröder, *Laser Spectroscopy 1: Basic Principles*, Springer, on
  scanning interferometers, wavemeters and frequency calibration.
- [Wikipedia: Wavemeter](https://en.wikipedia.org/wiki/Wavemeter), a short
  orientation on the instrument.

## See also

- [EOM sidebands](eom-sidebands.md), the comb mechanics treated here as
  the differential reference.
- [Allan deviation](allan-deviation.md), the reproducibility statistic
  this design relies on.
- [Sweep rate and detection lag](sweep-rate-and-detection-lag.md), the
  next page: another way the scan can distort a line.
- [The two-photon comb](the-two-photon-comb.md), the previous page, on
  why the comb reaches only a couple of islands.

---

[← The two-photon comb](the-two-photon-comb.md) · *Driving, modulating and detecting, 3 of 8* · [Laser frequency noise and the linewidth →](laser-frequency-noise-and-the-linewidth.md)
