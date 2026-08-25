# Grids and discretisation

*[wiki index](README.md) · method*

**The question.** How many grid points across a feature's own width are
enough to recover that feature with a fit, rather than merely to draw it on
a plot.
**Takes.** Nothing beyond a general sense of what a grid and a fit are. No
prior wiki page is required.
**Gives.** The points-per-feature-width ratio that governs a fit's
precision, and the simulation test that checks it rather than asserts it.
**Skip if.** The reader wants the three-setting acquisition design problem
this ratio feeds into. That is
[designing an acquisition](designing-an-acquisition.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A grid step is a number with no meaning on its own. Reported alone, a
spacing of 0.05 MHz says nothing about whether it is fine or coarse, because
fineness is a comparison against the narrowest feature the grid has to
represent, not a property of the step by itself. The only question worth
asking of a grid is how many of its points fall across that feature's own
width, $n = w / \delta$ for a feature of width $w$ sampled at step $\delta$,
and a sound design decision follows from that ratio rather than from either
number alone.

The distinction that matters is between a grid fine enough to draw a curve
and one fine enough to fit it. A plot interpolates between the recorded
points, so a display can look smooth with the feature carried by a handful
of samples or by hundreds, because the eye supplies whatever curvature the
gaps leave out. A fit gets none of that help. It estimates a width, an
asymmetry or a centre from the scatter of the actual samples sitting on the
feature, so its precision is set by how many independent points are really
there, and that count can be thin even when the same trace, plotted, looks
entirely convincing.

The same ratio governs a purely numerical grid as much as a physical
acquisition. A model that evaluates a lineshape on its own internal grid,
for instance to convolve two kernels together, meets the identical question
in miniature: how many grid points fall across the narrowest kernel being
convolved, not how many points the grid carries in total.

## What problem it solves

Stating a requirement as points across a whole record, or as a span, or as
a sampling rate on its own, treats three coupled quantities as though they
were independent, and a design built on any one of them can satisfy that
number while starving the feature the whole exercise exists to measure.
Restating the same requirement as points across the feature width collapses
span, record length and resolution back into the one ratio that actually
sets a fit's precision, so a design choice is checked against a single
number instead of three, and the general remedy is to test that number by
simulation, recovering a known truth at the proposed density, rather than
to assert it because it sounds generous.

## What can go wrong

Too coarse a step relative to the feature biases a fitted width. Samples
that miss the narrow region right at a peak systematically understate the
sampled maximum, and a half-maximum criterion applied to that lower peak
finds its crossing further out than the true half-maximum would sit, so the
recovered width comes out too wide well before a trace stops looking
plausible when plotted. The same undersampling can fold genuine structure
to the wrong place entirely rather than only broaden it: content that
oscillates faster than the grid resolves reappears in a fit at an apparent
frequency set by the grid rather than by the line, the general aliasing
failure of any regular sampling below the feature's own Nyquist rate.

Span and resolution exchange against each other at a fixed record length, and
widening a window for a good reason, to reach a wing or a companion feature
further out, is not free. Every point spent on the wider reach is a point
no longer spent on the narrow feature at the centre, so the same total
record that resolves a line easily at one span can leave it thinly
sampled at another, with nothing about the wider window itself announcing
the loss.

A feature sitting near the boundary of a window carries a further and
separate hazard. Whatever lies outside the window, a slowly varying
background, a wider companion feature, an instrument offset, has to be
assumed or extrapolated rather than measured, because the window carries no
data there to constrain it. A narrow window fitted right up to a feature's
own edge is fitted against a baseline the window itself cannot determine,
and the result then depends on the form assumed for that baseline as much
as on the data actually inside the window.

## Where this repository uses it

The wide-scan record length in
[chapter 7 of the plan](../plan/07_acquisition-settings.md) was set by this
exact ratio, and the chapter is worth reading for how the number moved. An
earlier version of that chapter fixed the record at 10000 points, a figure
set before any simulation had tested it. Simulated later against a frozen
recovery criterion, at the span the chapter proposes, 10000 points leaves
22 points across the line and fails the criterion, 20000 points passes, and
40000 points passes with margin, so the record length in force rose several
times over from a starting figure nobody had yet checked.

The same ratio governs a grid this repository builds itself rather than
digitizes. `GRID_STEPS_PER_KERNEL` in
[`rb5s6s/lineshape.py`](../../rb5s6s/lineshape.py) fixes the internal
convolution grid at 12 steps across the narrowest kernel width being
convolved, named as a constant rather than left as a literal because a
coarsened version of the same grid, at 4 steps across the kernel, shifted
the composite line width by about 0.1 percent with the rest of the test
suite still green, a change nothing else in the suite was positioned to
catch.

## Try it

A Lorentzian sampled at several densities relative to its own width, with
the half-maximum width read straight off the samples the way an unfitted
measurement would read it. The departure from the true width grows as the
grid coarsens, negligible at the couple of hundred points a plot would use
and already several percent at the handful of points a thin record leaves
across a real feature.

```python
import numpy as np
from rb5s6s.lineshape import lorentzian, GRID_STEPS_PER_KERNEL


def measured_fwhm(points_per_width, true_fwhm=1.0, phase=0.31):
    """Sample a Lorentzian on a grid of the given density and read its
    half-maximum width straight off the samples, the way an unfitted
    measurement would."""
    step = true_fwhm / points_per_width
    n = int(np.ceil(8 * true_fwhm / step)) + 2
    nu = step * (np.arange(-n, n + 1) + phase)
    y = lorentzian(nu, true_fwhm)
    i_peak = np.argmax(y)
    half = 0.5 * y[i_peak]

    i = i_peak
    while y[i] >= half:
        i -= 1
    x_lo = nu[i] + (half - y[i]) * (nu[i + 1] - nu[i]) / (y[i + 1] - y[i])

    i = i_peak
    while y[i] >= half:
        i += 1
    x_hi = nu[i - 1] + (half - y[i - 1]) * (nu[i] - nu[i - 1]) / (y[i] - y[i - 1])

    return x_hi - x_lo


true_fwhm = 1.0
print(f"true Lorentzian FWHM: {true_fwhm:.3f} MHz")
print(f"{'points/width':>14}{'grid step':>14}{'measured FWHM':>16}{'departure':>13}")
for points_per_width in (200, 40, 20, 12, 8, 6, 4, 3, 2, 1.5):
    fwhm_meas = measured_fwhm(points_per_width, true_fwhm)
    departure_pct = 100.0 * (fwhm_meas - true_fwhm) / true_fwhm
    flag = ("  <- this repository's own convolution-grid density"
             if points_per_width == GRID_STEPS_PER_KERNEL else "")
    print(f"{points_per_width:14.1f}{true_fwhm / points_per_width:14.4f}"
          f"{fwhm_meas:16.5f}{departure_pct:12.2f}%{flag}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## The ratio that was asserted rather than tested once

This page's own remedy for a coupled span-resolution-record exchange is to test
the points-across-the-feature ratio by simulation rather than assert it
because a number sounds generous. On the wide-scan design in
[chapter 7 of the plan](../plan/07_acquisition-settings.md), that remedy was
skipped once and applied afterward, and [HISTORY.md](../HISTORY.md) dates
both steps. On 2026-08-15 the span widened from 800 MHz to 2400 MHz, and the
record length, previously 3000 points sized against a stated requirement of
20 points across the line FWHM at the old span, rose to 10000 points to
preserve that same 20-point ratio at the new one. Nothing in that move asked
whether 20 was ever the right target for a fit to recover a width from, only
whether the ratio matched a number nobody had checked.

On 2026-08-16 two simulation runs, labelled B5 and B6 in that day's
work queue, asked that question directly, simulating
the width recovery a 10000-point record delivers at the committed noise law.
The ratio came out to about 22 points across the line, and 22 fails a frozen
recovery criterion. The requirement was replaced by 90 points across the
line, and the record length that delivers it, 40000 points, is the one this
page's "Where this repository uses it" section above already names. The
20-point figure had been carried through two design revisions as though
restating it in a new form made it correct, when the ratio it named had
never actually been run through the injection-recovery test this page
recommends. Running that test before the number entered the design script,
rather than after two revisions had already built on it, would have caught
the shortfall at its first appearance instead of at its second.

## Further reading

- P. R. Bevington and D. K. Robinson, *Data Reduction and Error Analysis for
  the Physical Sciences*, 3rd ed. (McGraw-Hill, 2003), for how a fitted
  parameter's precision depends on the number and placement of the samples
  behind it.
- J. S. Bendat and A. G. Piersol, *Random Data: Analysis and Measurement
  Procedures*, 4th ed. (Wiley, 2010), for sampling, aliasing and record
  length in a digitized measurement generally.
- [Designing an acquisition](designing-an-acquisition.md), the three-setting
  design problem this same ratio resolves for a physical scan.
- [Injection-recovery testing](injection-recovery.md), the general technique
  a grid requirement is tested against rather than asserted.
- [Chapter 7 of the plan](../plan/07_acquisition-settings.md), the record
  length case worked through in full, with the simulation that moved it.

## See also

- [Designing an acquisition](designing-an-acquisition.md), the three-setting
  acquisition problem this same ratio resolves for a physical scan.
- [Injection-recovery testing](injection-recovery.md), the general technique
  a grid requirement is tested against rather than asserted.
- [Optimiser convergence](optimiser-convergence.md), the second question a
  fit built on a well-resolved grid still has to survive.
- [Compute budgets and failure modes](compute-budgets-and-failure-modes.md),
  the resource cost of testing a candidate grid density by simulation before
  running it at full scale.

---

[← The digital twin of an experiment](the-digital-twin.md) · *Simulation and computation, 3 of 5* · [Optimiser convergence →](optimiser-convergence.md)
