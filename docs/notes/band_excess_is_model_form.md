# The band excess has a candidate mechanism, and it is the lineshape

Measured 2026-08-17. This replaces the statement, carried until now in
[the limitations chapter](../big_picture/07_limitations-and-identifiability.md),
that the excess in the residuals outside the fit window has no candidate
mechanism. It has one. **Nothing in `results/` moved on this and no committed
bound changed**, so the finding is diagnostic and the chapter's limitation
stands as a limitation.

`provenance: NO_PRODUCER` - the numbers ON THIS PAGE remain computed once, by a run that recorded neither its environment nor its construction details. **A documented reconstruction now exists**, `scripts/run_band_excess.py` writing `results/band_excess.csv` from the same committed inputs, and its outcome is the reason this declaration does NOT upgrade: **the census reproduces exactly, 79 traces, and the headline rows do not.** The low-order shared amplitude survives near six sigma, the cubic-surviving amplitude returns 1.4 sigma against this page's 3.6, the joint height significance returns 3.05 against 8.65, and the reconstructed predictors are collinear at 0.896 where this page reports 0.415, which says the height predictor built here is not the one the original run used. **The page under-specifies its own construction**, and until the original's exact choices are recovered, its digits stand as what one unrecorded run printed. The density NEGATIVE, which is what the finding turns on, is the one part both runs agree on.

## What was already known, and why it stalled

An earlier pass established that the excess is real and reproducible, then
stopped, because the offset was not robust to the BASELINE FORM: granting each
trace a quadratic swung it from +0.215 to -0.158, a change larger than the
offset itself. Two things limited that verdict, and both were properties of the
instrument rather than of the atom.

The error bar was the scatter across the five traces of ONE condition. An n of
five cannot separate a shared systematic from a per-trace one, whatever the
sample count inside each trace.

And the baseline forms were compared SEQUENTIALLY, one fitted after another.
That measures how much the offset MOVES with the form. It never asks what the
offset IS once the form is free, which is the question the record needs.

## The construction

One linear model over every canonical trace at once,

    resid_i(nu) = A * 1{nu in band} + sum_j b_ij nu^j

with `A` shared by all traces and the `b_ij` per trace and free to order k. The
model is linear in everything, so by the Frisch-Waugh-Lovell theorem the shared
amplitude has a closed form: project the polynomial basis out of both the
residual and the band indicator, per trace, then combine. No optimiser and no
iteration, and every trace keeps its own curvature.

Baseline curvature is a property of ONE trace and drifts in sign and size
between them. A physical band excess is COMMON, at the same detunings, in every
trace. Granting each trace its own free polynomial removes the curvature that
can imitate the offset, and what survives is only the part they share.

## What survives

79 canonical traces, peaks 4154 and 4192, per-trace baseline order k:

| k | A, per-trace mean | across-trace error | z |
|---|---|---|---|
| 0, constant | +0.00200 | 0.00028 | 7.1 |
| 1, linear, production's form | +0.00201 | 0.00028 | 7.1 |
| 2, quadratic | +0.00076 | 0.00021 | 3.7 |
| 3, cubic | +0.00075 | 0.00021 | **3.6** |

Granting curvature removes about three fifths of the amplitude, which is what
the earlier pass saw, and leaves the rest standing. Quadratic to cubic changes
nothing, so the ladder has converged.

**The error must be the across-trace one.** The noise-law error on the shared
amplitude is smaller by an order of magnitude, and a shared systematic does not
average down over samples within a trace. That correction was made once before
at n = 5 and is confirmed here at n = 79.

## The mechanism, from a joint regression

Each trace's own amplitude regressed on BOTH competing predictors at once,
standardised, n = 79, k = 3:

| predictor | coefficient | z |
|---|---|---|
| the model's own profile height inside the band | +0.00138 +/- 0.00016 | **+8.65** |
| log10 vapour number density | -0.00012 +/- 0.00016 | **-0.75** |

The two predictors correlate only +0.415, so this is a genuine separation and
not a collinearity artefact. **Density contributes nothing once profile height
is in the model, and its sign is negative.** Taken one at a time, density looks
significant at +2.2 sigma, and only the joint regression settles it.

## Two controls

**A band pinned in LINEWIDTH units.** The band runs from the fit half-width out
to 36 MHz in absolute frequency, and the line is far broader at the hot end, so
the same MHz sits nearer the core there. Re-cutting the band at a fixed multiple
of each trace's own FWHM removes that confound by construction. The trend
survives, and by temperature it runs -0.1, -0.5, +0.4, +3.5 sigma from cold to
hot. The band is not creeping toward the core.

**A placebo band INSIDE the fitted window** carries structure too. Whatever this
is, it is not confined to the extrapolated region, which is what a general
profile mismatch predicts and a far-wing collisional excess does not.

## What this changes

The excess acquires the candidate mechanism the record said it lacked, and the
candidate is the LINESHAPE MODEL rather than the atom. Three consequences:

  * The band is not evidence for a quasistatic collisional wing, which leaves
    that question open on theory rather than contaminated by a measurement that
    looked like an answer.
  * The lever that matters next is a better PROFILE, which is the model-ladder
    work in `scripts/run_modelform.py`, and not a longer collisional lever.
  * The limitation itself is unchanged: the excess is still unattributed to a
    specific physical term, and a candidate mechanism is not an explanation.

## What this does not establish

The traces are peaks 4154 and 4192 only, canonical, power and temperature
sweeps. The 130 C condition supplies 50 of the 79 and 39 of those sit at
225 mW, so temperature and power are confounded in the split tables and no
power statement is made. The profile-height predictor is built from the fitted
model, so it is not independent of the fit whose residuals it explains, and a
cleaner version would use an external profile. None of that weakens the
negative result on density, which is what the finding turns on.
