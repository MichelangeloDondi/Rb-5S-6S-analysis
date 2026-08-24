---
`provenance: DESIGN` - the spans, block counts and percentages here size a
proposed acquisition. Nothing on this page is a measurement of data.
title: The wide-scan block, sized so the next session can run it cold
status: DESIGN
---

# The wide-scan block, sized so the next session can run it cold

**The question.** What acquisition settings turn the 2025 dead ends into
measurements, and what should the traces look like on the day?
**Takes.** [PLAN section 10a](../PLAN.md), and the 2026-08-15 analysis of the
out-of-window residuals.
**Gives.** A record length, a span, a piezo shape, a forward-modelled trace,
and six go/no-go checks.
**Skip if.** You are not planning bench time. The short version is that the
2025 span, not its resolution, is what bounded the analysis, and span is a
knob.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Computed by `scripts/run_widescan_design.py`, which writes nothing and reads
every input from the record. Run it rather than trusting the numbers copied
here.

## Why the block exists

Three limits ended the 2026-08-15 analysis and all three were fixed at
acquisition time.

The out-of-window band that carries ridge-breaking information about the
collisional width is 17 MHz wide, from the fit half-width at 19 to the
retrace mirror at 36, out of a 43 MHz half-span. That was enough to show the
band prefers a lower collisional width than the core fit assigns, on 11 of 14
fresh conditions (p = 0.029), and not enough to say what lives in it.

The shaped-contaminant injection that would decide it has since run, and the
answer is that the preference is not shape-independent: injecting a contaminant
of a shape the measured band deficits allow reproduces the displacement without
touching the collisional width. A second measurement then found the band's own
offset is smaller than the swing produced by changing the per-trace background
from a line to a quadratic, a form the window data cannot identify. The band
cannot arbitrate the width while its baseline is extrapolated, which is a span
problem and is what this note sizes. [PLAN.md](../PLAN.md) limit one carries
the numbers.

The co-propagating Doppler pedestal is 942 MHz wide at 130 C. Across the
whole 85 MHz span it varies by 0.57 per cent of itself, so the free per-trace
background absorbs it. It is neither measurable nor excludable here, and it
is the standing candidate for the band excess.

And the fitted laser width is three to four times what this bench's
in-campaign wavemeter records allow, with the leading explanation, a tilted
retro, degenerate with the term it would replace.

## The settings

| requirement | value | why |
|---|---|---|
| span | 2400 MHz, plus or minus 1200 | three Gaussian sigma of the pedestal, set by the degeneracy calculation below and not by where the curve looks like it has fallen |
| record length | 10000 points, deeper preferred | keeping 22 points across the 5.4 MHz line at that span |
| piezo shape | sawtooth, or export one direction | a symmetric triangle images an off-centre line, which is the 40 MHz mirror that caps the fit window at 25 |
| dwell | at least the 2025 0.5 ms per point | the transit cusp is a time-domain feature and a fast scan smears it |
| rate or window | 28 times the 2025 piezo amplitude at a 1 s window, or a 28 s window at the 2025 rate | the same span reached two ways |

**Why three sigma and not one.** The per-trace background is free, so it
absorbs whatever is flat and the pedestal is measured only through its
curvature across the span. The cost is a Fisher ratio and not a haircut: with
y = A g(nu) + B and B free, the amplitude's signal-to-noise retains
sqrt(1 - <g>^2/<g^2>). That is 0.140 at one sigma of reach and 0.645 at three,
so a span chosen to make the pedestal look visible is not the same span that
makes it measurable. `background_degeneracy_factor` in the design script
computes it and a test pins the value.

(The earlier span and its assumed degeneracy factor are recorded in
[HISTORY.md](../HISTORY.md).)

The reach schedule, which is also the fallback if the piezo cannot reach three
sigma. Read off the widest row the hardware allows:

| reach | span | SNR retained | sigma per trace | points across the line |
|---|---|---|---|---|
| 1.0 sigma | 800 | 0.140 | 7 | 67 |
| 1.5 sigma | 1200 | 0.287 | 14 | 45 |
| 2.0 sigma | 1600 | 0.436 | 21 | 34 |
| 2.5 sigma | 2000 | 0.558 | 26 | 27 |
| **3.0 sigma** | **2400** | **0.645** | **31** | **22** |
| 4.0 sigma | 3200 | 0.749 | 36 | 17 |

at 10000 points and the record's median tau_int of 3.81. The knee is near three sigma: past it the retained fraction
gains little while the resolution keeps falling. Every row still detects the
pedestal in a five-trace block, so a narrower span degrades the measurement
without breaking it. The one thing not to do is keep the 2025 span, where
the retained fraction is 0.0013 and the pedestal is unmeasurable in principle
however long the block runs.

The sizing result worth carrying: at the 2025 record length of 2000 points
the span and the shape requirements are mutually exclusive. **No setting of a
2000-point record answers both questions at once.** A deeper record is a menu
setting on any modern instrument, and it dissolves the tradeoff entirely: one
trace then carries the Doppler-free line, its near wings, and the pedestal
together.

## What the trace should look like

The pedestal sits at 0.38 per cent of the line's peak height, from the
record's own retro ratio of 0.94 through the area ratio 4rho/(1+rho^2).

Against the measured single-point noise of 0.39 per cent of peak, a naive
count over the 36000 off-line points of a 40000-point record would promise 186
sigma. **Two corrections apply, and they bring it to about 61 sigma in one
trace and 137 in a five-trace block.** The noise is correlated: the record's 32
tau_int values run 1.31 to 19.81 with a median of 3.81, so the effective count
is about a quarter. And the free per-trace
background absorbs the flat part of any broad shape, so only the curvature is
fitted, which at three sigma of reach leaves 0.645 of the ideal information.

These figures rose on 2026-08-16 with the record length, when the shape
requirement was raised to the 90 points across the line that the B5 and B6
simulations support. What they replaced is recorded in
[HISTORY.md](../HISTORY.md).

The tau assumption is not load-bearing, and the range is wide enough that this
matters: at the record's best tau the detection is 105 sigma per trace, at its
median 61, and at its worst 27. Every one of those is decisive in a
five-trace block. Stating the naive 93 beside them is deliberate: it is the
number to distrust.

## What it buys

**An in-situ thermometer.** The pedestal width goes as the square root of the
temperature, so the gas temperature stops being an accepted number. At the
corrected significance the width lands to 3.2 per cent in one trace and the
temperature to 6.5 per cent, about 26 K at 130 C, improving to 12 K in a
five-trace block. Useful as a cross-check on the cold-spot model rather than
as a precision thermometry result.

**An in-situ retro ratio, weakly.** The area ratio 4rho/(1+rho^2) is flat in
rho near unity, with a derivative of 0.13 per unit rho at the accepted 0.94.
This is a poor handle unless rho is well away from one, and the block
register already lists that as this entry's empty case.

**Frequency reach for the band excess.** Any broad candidate must curve
somewhere inside 2400 MHz. A constant cannot. That is the discrimination the
2025 span could not provide.

## The go/no-go checks, on the day

1. the pedestal is visible in a single raw trace at the 0.38 per cent level.
   If not, the span or the record length did not take.
2. the line still has at least 10 points across its FWHM. If not, the record
   length lost to the span and the shape information is gone.
3. no second copy of the line anywhere in the span. If there is one, the
   retrace mirror survived the piezo change.
4. the EOM comb is still resolvable for the frequency axis. At 6.25 MHz
   spacing on the laser axis this is about 62 points per tooth at the
   proposed resolution, which is comfortable.
5. the per-trace timestamp is in the export. The archive had to recover the
   clock separately, and blocks turned out to be 54 to 76 minutes apart
   rather than minutes.
6. the ramp monitor is on its own channel and saved, per PLAN section 3
   item 0.

## What this block does not settle

The laser linewidth and the retro alignment. The 2026-08-15 analysis showed
that a retro tilt produces a Gaussian of the same functional form and width
as the fitted laser term, so the two are degenerate by construction and no
scan setting separates them. Those need a beat-note or self-heterodyne
measurement and an alignment check, both session-level, neither riding this
block.
