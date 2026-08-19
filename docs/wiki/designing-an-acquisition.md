# Designing an acquisition

*[wiki index](README.md) · method*

**The question.** How do span, resolution and record length trade against
each other, and which acquisition choices cannot be revisited once a
session has run.
**Takes.** The idea of a digitized sweep, an oscilloscope trace or a
lock-in scan. No other wiki page is required first.
**Gives.** The single relation linking span, resolution and record length,
points across the feature as the governing quantity, and the choices a
later analysis can never repair.
**Skip if.** You want the frequency axis a record's grid is calibrated
against, rather than how densely that grid is sampled. That is
[the wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A digitizing scan (an oscilloscope trace, a lock-in sweep, anything that
turns a continuous signal into a finite list of numbers) is set by three
menu items that look independent and are not. The SPAN is the frequency
range the sweep covers. The RECORD LENGTH is how many points the instrument
digitizes. The RESOLUTION is what falls out once the other two are chosen,
the frequency step between neighbouring points, span divided by record
length. Fixing any two fixes the third, so span, resolution and record
length are one decision wearing three knobs, not three decisions.

$$\delta = \frac{S}{N}, \qquad n_{\text{line}} = \frac{w}{\delta} = \frac{wN}{S}$$

Here $S$ is the span, $N$ the record length, $\delta$ the resulting
resolution and $w$ the width of the feature a fit will extract a parameter
from. The governing quantity for a fit is $n_{\text{line}}$, points across
that feature, not points across the whole trace. A trace with a generous
total point count can still starve the one feature the analysis actually
needs, because $n_{\text{line}}$ scales with the record length and falls
directly with the span. Widening the span at a fixed record length, to
reach a wing, a pedestal or a reference line further out, spreads the same
point budget over more frequency and thins the sampling of the narrow
feature in exact proportion. Nothing about that trade is visible on the
instrument's own display, since a screen redraws the same number of pixels
whatever the record length is doing underneath it.

The distinction that matters is between drawing a curve and fitting one.
Plotting interpolates between the recorded points, and a display looks
smooth with the feature sampled generously or sparsely alike, because the
eye supplies whatever curvature the gaps leave out. A fit does not get that
help. It treats every point as one noisy observation of the underlying
shape and estimates a width from how those observations scatter around it,
so the precision of that estimate is set by how many independent points sit
on the feature, and it degrades as that count falls, roughly as the inverse
square root of the count for an otherwise well-conditioned fit. A record
that draws a convincing line at a given span can still return a width whose
uncertainty is too large to be useful, with nothing in the picture to say
so.

What an acquisition stores, not only how densely, is a second decision made
once and never revisited. An irreversible on-instrument average, a
"high-resolution" or peak-detect acquisition mode, folds several raw sweeps
into the single record that reaches disk before any later analysis sees
them, and the individual sweeps are then gone rather than merely
uncollected. A bandwidth limit is a different operation: set comfortably
above the signal's own bandwidth, it removes noise power from a band the
signal never occupied and leaves the signal itself untouched, so it costs
nothing and is safe to leave on. And a per-sweep timestamp is one channel or
one logged column that a later stability statistic consumes directly.
Without it, the only surviving order is the sequence files were saved in,
which says nothing about how much time actually separated them.

## What problem it solves

It turns three settings that look like separate line items on an
instrument's menu into one design question with a numeric, testable answer,
worked out before any bench time is spent rather than discovered afterward
in a fit that will not converge to a useful precision. It also protects the
decisions that cannot be revisited once a session has run. A raw sweep
folded into an on-instrument average cannot be un-averaged, and a trace
exported with no clock can never gain one, so both are worth deciding
correctly before the first point is digitized rather than repaired in
analysis.

## Where this repository uses it

[Chapter 7 of the plan](../plan/07_acquisition-settings.md) sizes the
wide-scan record for the next campaign exactly this way, and its own
history is the case study worth telling, because the requirement it states
was raised once, and only once a simulation had actually tested it.

The 2025 record length is `TRACE_N_POINTS` in
[`rb5s6s/constants.py`](../../rb5s6s/constants.py), 2000 points, and at the
2025 span that chapter reports 127 points across the line's measured width,
comfortable for the fit the campaign ran. Holding that same record length
fixed while widening the span to reach a co-propagating Doppler pedestal, as
the Try it block below computes directly from the constant, collapses the
points-across-the-line count toward single digits, which is the concrete
form of the trade above and the reason chapter 7 calls the 2000-point record
unable to answer the span question and the shape question at once.

An earlier version of that chapter fixed the wider-span record length at
10000 points, a number set before any simulation had tested it. Simulated
later against a frozen recovery criterion, 10000 points leaves 22 points
across the line and fails the criterion, 20000 points passes, and 40000
points passes with margin, so the adopted record length is 40000, several
times the figure the requirement carried before it was tested, giving about
90 points across the line at the proposed 2400 MHz span
([chapter 7](../plan/07_acquisition-settings.md)). The number this
simulation produced is corroborated rather than contradicted by
[the wide-scan block design note](../notes/widescan_block_design.md), which
records the same 90-points-across target as what its own B5 and B6
simulations support.

The raw-storage question is written down for the ramp channel specifically.
[Section 10b.1 of the acquisition record](../plan/08_the-acquisition-record.md)
requires the piezo ramp to be exported as its own channel with every trace,
never reconstructed afterward from the line widths it drove, because a scan
rate folded into an assumption is exactly the kind of information an
on-instrument average would also destroy irreversibly. The [joint fit](joint-fit.md)
is what raw per-sweep records are for downstream, sharing a line shape
across a condition's repeats while leaving an amplitude, a centre and a
background free per trace, which needs the individual sweeps intact.

Per-sweep timestamps are asked for directly.
[Item 7g of the width and collision-amplitude chapter](../plan/05_width-collision-amplitude.md)
requires a per-scan timestamp in hardware metadata rather than only a
notebook entry, because the 2025 exports carried no acquisition time at all.
[RESULTS.md](../RESULTS.md) records what that omission cost: a clock
recovered after the fact dates the four peak-blocks of a dwell 54 to 76
minutes apart, not the few minutes a sharing assumption in the fit hierarchy
needed. [Allan deviation](allan-deviation.md) describes the same limit from
the other side, that no reproducibility statistic can run on a record that
is not a time series, however deep that record is in points.

## Sizing a design by simulating it

Everything above sizes a setting by an argument. The arguments are checkable,
and checking them costs minutes rather than a session:
[`rb5s6s/forecast.py`](../../rb5s6s/forecast.py) generates the traces a
proposed design would record and fits them back, so span, point count, repeat
count and power can each be varied and the resulting parameter uncertainty
read off rather than predicted. [The digital twin](the-digital-twin.md) is
the method and its limits, and the one result worth carrying back to this
page is that a design study reports what more data buys and will never tell
you that a parameter pair stays degenerate. Read the correlation beside every
forecast.

## What can go wrong

The first failure is a model one, conflating a record's ability to draw a
convincing curve with its ability to fit one. A trace with a thin
points-across-the-line count can still plot smoothly, because plotting
interpolates and the eye fills the gaps, so nothing in the picture warns
that the same points carry too little independent information to pin down
a width.

The second is data insufficiency wearing the shape of a reasonable request.
Widening a span for a good reason, to reach a wing, a pedestal or a
reference feature, without lengthening the record to match, thins the
sampling of the narrow feature in direct proportion and can turn a
well-conditioned fit into a poorly conditioned one without changing
anything about the line itself. Span, resolution and record length are read
off an instrument's menu as three settings, and treating them as three
independent choices rather than the one relation above is the mistake this
page exists to head off.

The third is an implementation trap that a default menu setting invites.
Many oscilloscopes ship with an on-instrument averaging or high-resolution
acquisition mode enabled, and it folds several raw sweeps into the single
record that reaches disk before a joint fit ever gets to see them. By the
time the loss is noticed, the individual sweeps are not merely uncollected,
they no longer exist to be collected.

The fourth is an experimental limitation that no downstream analysis can
repair. A record acquired with no per-sweep timestamp cannot gain one
afterward, and the only substitute, reconstructing elapsed time from
whatever other trace of it survives, is exactly the kind of after-the-fact
recovery this repository had to perform once and would rather not perform
again.

## Try it

For a fixed record length, read from this repository's own 2025 constant
rather than typed from memory, points across a stated line width at several
spans, and the record length a target points-across-the-line count would
need at the widest of them.

```python
from rb5s6s.constants import TRACE_N_POINTS


def points_across_line(record_length, span_mhz, line_fwhm_mhz):
    resolution_mhz_per_point = span_mhz / record_length
    return line_fwhm_mhz / resolution_mhz_per_point


line_fwhm_mhz = 5.4  # a representative Doppler-free line width on this bench
spans_mhz = (85, 400, 800, 1600, 2400)

print(f"record length fixed at {TRACE_N_POINTS} points "
      f"(rb5s6s.constants.TRACE_N_POINTS)")
print(f"{'span (MHz)':>12}{'resolution (MHz/pt)':>22}{'points across line':>22}")
for span in spans_mhz:
    resolution = span / TRACE_N_POINTS
    n_line = points_across_line(TRACE_N_POINTS, span, line_fwhm_mhz)
    print(f"{span:12.0f}{resolution:22.4f}{n_line:22.1f}")

print("a wider span at the same record length samples the line more thinly")

target_points_across_line = 90
required_record = target_points_across_line * 2400 / line_fwhm_mhz
print(f"holding {target_points_across_line} points across a {line_fwhm_mhz} MHz "
      f"line at a 2400 MHz span needs a record of {required_record:.0f} points")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## The requirement that was stated before it was tested

The chapter 7 case study above reports that the adopted record length is
40000 points, several times the number the requirement carried before it was
tested, without dating the steps it passed through. [HISTORY.md](../HISTORY.md)
carries the dates. On 2026-08-15 the wide-scan span moved from 800 MHz to
2400 MHz, and the record length that had stood at 3000 points, sized against
a shape requirement of 20 points across the line FWHM evaluated at the old
span, moved to 10000 points to hold that same 20-point target at the new one.
On 2026-08-16 the 20-point requirement itself was tested for the first time:
the B5 and B6 runs measured the width recovery a 10000-point record actually
delivers at the committed noise law, found about 22 points across the line,
and found that 22 fails a frozen recovery criterion. The requirement was
replaced by 90 points, the figure the adopted 40000-point record delivers.

The mistake was not an error in dividing a span by a record length. It was
treating "20 points across the line" as a specification rather than as an
untested guess, a number moved twice to match a span before anyone asked
whether it recovered a known width at all. This page's own distinction,
between a record that draws a convincing curve and one that fits it, names
exactly the gap the requirement fell into: a 22-point record can still plot
smoothly, and nothing about the plot would have shown that the fit behind it
needed four and a half times as many points. Testing the requirement by
simulated recovery before it was written into a design script, rather than
after, would have caught the factor of four before it reached the plan.

## Further reading

- P. R. Bevington and D. K. Robinson, *Data Reduction and Error Analysis for
  the Physical Sciences*, 3rd ed. (McGraw-Hill, 2003), for how a fitted
  parameter's precision depends on the number and placement of the samples
  behind it.
- J. S. Bendat and A. G. Piersol, *Random Data: Analysis and Measurement
  Procedures*, 4th ed. (Wiley, 2010), for sampling, bandwidth limiting and
  record length in a digitized measurement generally.
- [The Voigt profile](voigt-profile.md), the lineshape a record's points are
  spent fitting.
- [Weighted least squares](weighted-least-squares.md), the fit whose
  precision this page's sampling trade feeds directly.
- [The joint fit](joint-fit.md), what a raw per-sweep record is kept intact
  for.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md),
  turning an acquired record's own grid into a calibrated frequency axis.
- [Allan deviation](allan-deviation.md), the statistic a per-sweep timestamp
  channel makes possible.

## See also

- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md),
  turning an acquired record's grid into a calibrated frequency axis.
- [Photon counting](photon-counting.md), the detection choice sized before
  the same acquisition is designed.
- [The joint fit](joint-fit.md), what an intact per-sweep record is kept
  for downstream.
- [Allan deviation](allan-deviation.md), the statistic a per-sweep
  timestamp channel makes possible.

---

[← Sweep rate and detection lag](sweep-rate-and-detection-lag.md) · *Driving, modulating and detecting, 6 of 8* · [Bessel functions →](bessel-functions.md)
