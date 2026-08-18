*Chapter 7 of 8 of [the big picture](../BIG_PICTURE.md)*

**The question.** What does this dataset fail to determine, why does each
failure happen, and which measurement fixes which one?
**Takes.** The results of [what the 2025 dataset delivered](04_what-2025-delivered.md).
**Gives.** Six chains from a limitation to the measurement that removes it,
each with what would be learnt if it worked and if it did not.
**Skip if.** You want the summary rather than the argument, in which case
Part III of [the big picture](../BIG_PICTURE.md) is the table this chapter
expands.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

A limitation is only useful when it names its own cure. Each section below runs
from what the data cannot determine, through the physical reason, to the change
that would determine it, the machinery that would read the change, and the
outcome that change targets. THE OUTCOMES ARE TARGETS. None of these sessions
has been run, so every end state is what the design is for and not what the
record holds. Each section closes with both branches, because a design whose
failure teaches nothing is a design worth less than it costs.

## 1. The width split

**The limitation.** The collisional width and the laser width are not
separately determined. The archive fixes the total width to 0.0032 MHz and the
direction that divides it to only 0.0624 MHz, twenty times worse, at a
condition number of 390 across the three width parameters.

**The physical cause.** A Lorentzian collisional kernel and a Gaussian laser
kernel convolve into a profile whose shape barely distinguishes them at these
widths. The information that would separate them is not weakly present in the
lineshape. It is close to absent, which is why more data of the same kind does
not help. Inside a single condition the two trade at a correlation whose median
across the 32 conditions is -0.90.

**The change.** Measure one of them independently. The repaired cavity lock
makes a beat note against a second laser, a cavity ringdown, or a delayed
self-heterodyne measurement viable, and the 2025 session had none of them.

**The machinery.** Fit with the laser width pinned rather than free.
Simulated on a bright synthetic condition with signal-dependent noise
(`scripts/run_width_pinning.py`), the collisional width scatters by
0.0073 MHz across realisations when both are free and by 0.0021 MHz when the
laser width is known, a factor of 3.4 in an idealised condition whose ratio,
not whose absolutes, transfers to the real record.

**Target outcome.** The collisional width becomes separately identifiable, and
the bound of [Q-BETA-01](../BIG_PICTURE.md) becomes a measurement.

**If it works,** the whole width budget resolves, and the laser-width row stops
being conditional on the split it is part of. **If it does not,** and the
pinned fit's residual scatter fails to fall, that is informative rather than
wasted: it would place the missing information somewhere other than the laser
linewidth, most likely in the transit kernel of chain 4, and it would do so
with an independent measurement in hand rather than by inference.

## 2. The absolute frequency axis

**The limitation.** The archive has no absolute frequencies. Every axis is
differential, so line positions carry no information and only shapes do.

**The physical cause.** The lock drifted through the session and the wavemeter
was photographed rather than logged, so nothing ties the sweep to a known
frequency. This is a construction limit, not a noise limit.

**The change.** Catch two same-isotope pairs inside the sweep and log the
wavemeter to disk. The four components sit at 0, 911.3, 3220.0 and 5225.0 MHz
on the transition axis from the campaign labels. Two of them are both the
heavier isotope and two are both the lighter one, so each pair's separation is
fixed by hyperfine constants alone with no isotope shift in it.

**The machinery.** A same-isotope separation on the transition axis is the
ground hyperfine splitting minus the 6S splitting, and both are measured
quantities held as constants in this repository. The ground splittings are
clock-grade and the 6S constants are known to 2 kHz
([Ayachitula and co-workers](../lit/ayachitula2024.md)), giving 2318.537 MHz
for the lighter pair and 5219.973 MHz for the heavier one. The second of those
spans the entire four-component manifold and fits inside the piezo's measured
full-ramp reach of about 7.4 GHz, so ONE SWEEP CARRIES TWO INDEPENDENT RULERS
over different segments of the same axis.

**Target outcome.** The axis becomes calibratable to the accuracy of those
constants, under a validation ladder that is worth stating in order: the
heavier pair's ruler is validated on real sweeps, the excited-state constant's
uncertainty budget is verified, the scan software's span is confirmed to cover
the manifold, the axis model of the scan is validated, and the sweep-to-sweep
reproducibility is quantified. Until those are done this is a projection.

**If it works,** the two rulers agree within the projected nonlinearity, the
axis is anchored inside every trace rather than transferred from an
instrument, and the cross-isotope separations carry the isotope shift as a
by-product worth a literature check. **If it does not,** and the two rulers
disagree beyond the projected nonlinearity, that disagreement is the useful
result: it would say the axis model is wrong rather than imprecise, and it
would localise the error to the segment where the rulers diverge.

## 3. The baseline

**The limitation.** The Doppler pedestal underneath the line could be neither
measured nor excluded, so the baseline is a modelling choice rather than data.

**The physical cause.** The pedestal is 942 MHz wide and the archive's fit
window is a few tens of megahertz, so across the window the pedestal is almost
flat and the free per-trace background absorbs it entirely.

**The change.** Sweep wide enough that the pedestal curves inside the window,
and fit it as a pedestal rather than as a polynomial. Photon counting helps
here specifically, because the crossover below which counting beats the analog
chain sits at about 1.6 per cent of the peak, and the pedestal and the wings
live below that.

**The machinery.** Simulation of the wide fit at the measured noise law, with
the record length set by points across the line rather than points per trace.

**Target outcome.** The baseline becomes measured, so it stops being a source
of model error in every other quantity that shares the window.

**If it works,** the pedestal also becomes a thermometer of the atoms actually
probed, which is a different quantity from a thermocouple reading of the cell
wall. **If it does not,** and the wide fit fails to recover an injected
pedestal, the span was still too narrow or the baseline is not the assumed
form, and the injection test says which.

One thing this chain does NOT do, stated because an earlier version of this
record assumed it would: the pedestal is not the explanation of the
out-of-window excess. A ceiling test at twelve times the predicted pedestal
amplitude still leaves far less in the band than is measured there, so that
candidate is excluded and chain 6 is the one that addresses the anomaly.

## 4. The transit kernel

**The limitation.** The transit contribution rides on a beam waist that was
never measured on this bench, and the cusp shape of the thermally averaged
transit kernel is untested here.

**The physical cause.** The waist was adopted from the apparatus lineage and
supported by a consistency argument on the transit width. That makes it the
largest open systematic in the record, and every intensity-denominated
quantity inherits it.

**The change.** Profile the beam on the day, by knife edge or camera, and take
one cold and dim condition where the transit term is the largest fraction of
the width.

**The machinery.** The model comparison the record already specifies, plus
injection and recovery to establish what the comparison can actually
discriminate at the achieved precision.

**Target outcome.** A direct experimental handle on the transit model. THE
DISCRIMINATION POWER REMAINS A PROJECTION until the injection tests are run,
so the statement to make is that the measurement becomes possible, while its
verdict stays open.

**If it works,** the geometry stops being an assumption and every bound that
divides by the waist sharpens without any new physics run. **If it does not,**
and the comparison stays inconclusive, that bounds how much of the width budget
the transit kernel can be responsible for, which narrows chain 1's failure
branch in turn.

## 5. The light shift

**The limitation.** The light-shift amplitude is bounded and not measured. The
archive's limit at maximum power already sits below the predicted value, which
makes the absence of a measurement more interesting rather than less.

**The physical cause.** Two reasons compound. At a single drive power the
shift's broadening is degenerate with other terms that grow the same way with
power and with focus. And the asymmetry channel that would break that
degeneracy carries too little signal in one trace: at the archive's own bound
the asymmetry is smaller than the per-point noise.

**The change.** A randomised power ladder with more rungs and per-sweep
normalisation, under a lock that holds the centre still so the first-order
pull is no longer absorbed by a free per-scan centre.

**The machinery.** The joint fit across the ladder, with the projected
precisions recorded as design envelopes rather than derived here.

**Target outcome.** Measured rather than bounded, conditional on the projected
coverage holding in a joint-fit simulation. The projections put the
prediction-to-precision ratio at 1.89 for the smallest session considered and
5.35 for the largest.

**If it works,** the light shift becomes the first absolute coefficient this
line yields by this method. **If it does not,** and the per-sweep normalisation
scatter exceeds the pull it is meant to resolve, the limitation moves from the
lock to the power metrology, which is a cheaper problem to fix and a different
one to fix.

## 6. The band excess

**The limitation.** There is a real, reproducible excess in the residuals
outside the production fit window, between 0.10 and 0.29 per cent of the peak,
and it is not attributed to a specific physical term.

**The physical cause.** There is now a candidate, and it is the lineshape model
rather than the atom. A joint fit over every canonical trace, each granted its
own free polynomial baseline, leaves a shared excess standing at 3.6 sigma under
per-trace CUBIC freedom. Regressed on both competing predictors at once, that
excess tracks the model's own profile height inside the band at 8.65 sigma while
vapour density is a null predictor at -0.75 sigma, and a band re-cut in units of
each trace's own linewidth keeps the trend. A placebo band inside the fitted
window carries structure too, which a general profile mismatch predicts and a
far-wing collisional excess does not.
[The full construction and its controls](../notes/band_excess_is_model_form.md).

**This is a candidate mechanism and not an explanation**, so the limitation
stands. Nothing in `results/` moved on it. What it does settle is what the
excess is NOT: the pedestal is excluded as its source by the ceiling test of
chain 3, and the excess is not evidence for a collisional far wing, which
leaves that question open on theory rather than contaminated.

**The change.** Polarisation isolation. The two-photon rate goes as the squared
degree of linear polarisation and vanishes for circular light, which is
published for this transition in this lineage
([Rajasree and co-workers](../lit/rajasree2020spin.md)). Orthogonal linear
polarisation kills the cross term that drives the Doppler-free line while the
same-beam terms that drive the pedestal survive, so it is a pedestal-only
block. Circular polarisation removes the whole two-photon signal, which makes
it an extinction null in which everything the detector reports is background.

**The machinery.** The shaped-contaminant fitting already built for the
residual-structure work.

**Target outcome.** The anomaly becomes attributable, which is the projected
outcome and not an assured one.

**If it works,** the one open anomaly in the record acquires a mechanism, or is
shown to be instrumental. **If it does not,** and the isolated blocks carry the
same excess, that moves it out of the optics and into the detection chain,
which is a smaller space to search than the one it lives in now.

## 7. The acquisition itself, found 2026-08-18

The six limitations above are properties of the model and the data. This one
is a property of how the data were TAKEN, and it was found by reading the
quantisation step of the stored samples rather than any recorded setting.

**Power was confounded with time, and the vertical range moved under the
measurement.** In the campaign the power descends monotonically with elapsed
time, so any quantity measured against power is equally a measurement against
drift, and no analysis of that session alone can separate them. Independently,
the oscilloscope's vertical range was changed at every rung of every ladder,
by up to a factor of 596 in quantisation step against a signal spanning only
about 80, so a power ladder is five measurements on five instrument ranges
rather than one measurement at five powers.

**What it cost, precisely.** The concave width against power cannot be
established: it is 1.4 standard deviations under the between-block treatment
and neither independent ladder confirms it. The amplitude's departure from the
square law survives, because the 2025-07-04 rehearsal happens to have run its
ladders in alternating directions and shows the departure to be invariant
under acquisition order, but its ordering across lines follows their
brightness rather than any atomic quantity, which points at the ranging rather
than at the atom.

**Both halves are removable at almost no cost**, which is what makes this a
limitation rather than a fact of life: randomise the rung order and record the
seed, and hold one vertical range across a ladder, which needs a 12-bit
acquisition and is arithmetic rather than preference. The full design is in
[the acquisition-settings chapter](../plan/07_acquisition-settings.md).

**The general lesson the record should keep.** The archive's most informative
control was an accident: the rehearsal's alternating ladders were run that way
for convenience, and they are the only reason one of these two findings could
be adjudicated at all. A design that varies the nuisance on purpose costs
nothing and would not have depended on luck.

## A note on the density design, which is a seventh limitation

The collisional bound has a limitation that is neither degeneracy nor absence
but GEOMETRY. Density rises steeply with temperature, so the three lower
temperature blocks sit close together on the density axis and the highest one
sits far from them. An influence audit of that four-point design puts the
high-temperature anchor at a hat-matrix leverage of 0.996 on all four peaks,
which means a straight line through those points passes very nearly through
the anchor whatever the anchor says. THE CONSTRUCTION CANNOT CHECK ITS OWN
ANCHOR: an outlier planted there leaves almost no residual, and the audit's
power ladder failed to detect one at any size up to a hundred times the
point's own error bar.

The committed diagnostics already show the same thing from the other side.
Dropping one temperature moves the coefficient by up to 0.1338 MHz per 1e12
per cubic centimetre, while dropping one peak moves it by at most 0.0070, a
factor of nineteen between removing a density point and removing a whole
spectral line.

Nothing here says the anchor is wrong. It says the design cannot tell, which
is why the coefficient is published as a bound. The cure is spacing: a density
ladder whose points are spread evenly in DENSITY rather than evenly in
temperature, with the hot points the plan already wants for signal reasons
moving the far end of the lever and giving the fit a second constraint out
there.

## What none of this would fix

Two limits survive every session above, and they belong here so the chapter
does not read as a promise. The density scale that the collisional coefficient
divides by comes from vapour-pressure curves rather than from a measurement of
this cell, so an absorption channel is needed before that coefficient is
absolute rather than relative. And the archive itself cannot be improved: these
chains describe what a NEW session would determine, and the 2025 bounds stand
as bounds whatever happens next.

## A limitation this chapter does not carry

Every chain above is about a quantity the data fail to determine. One limitation
is about the CONSTRUCTION instead: whether the joint fit that produces the
light-shift bound is entitled to share one coefficient across three measurement
sessions, given that the coefficient goes as one over the beam waist squared and
no session measured its own waist. That question has its own chapter, [when a
joint fit is legitimate](08_when-a-joint-fit-is-legitimate.md), which also
generalises it into six questions to ask of any pooled fit.

---

*[The next nanofibre session](06_next-nanofibre.md) · [When a joint fit is legitimate](08_when-a-joint-fit-is-legitimate.md) · [the big picture](../BIG_PICTURE.md)*
