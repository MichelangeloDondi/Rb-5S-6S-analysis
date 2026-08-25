# The case in ten minutes

This is a 2025 two-photon 5S-6S spectroscopy campaign in a rubidium vapour
cell. The three quantities below are the systematic limits on any precision
measurement built on the transition, and the question is not what they are
but what currently prevents measuring them.

Every number below is a committed result with its producer named, except
where this page says otherwise, and it says otherwise in four places: the
pinning factors of section 4, the excursion percentage and the
independent-information fraction of section 2, and the projected ladder
gain of section 5. Those come from notes whose numbers no producer
regenerates, which the record's own provenance audit established and
[`unregenerated_claims.csv`](../../results/unregenerated_claims.csv)
counts. Where a quantity is bounded rather than measured, it is written as
a bound.

In one sentence: for each of three quantities the campaign could bound but
not measure, this record identifies why, as a property of the lineshape, the
apparatus or the sampling, and names the single measurement that removes
each limit.

1. [What was measured](#1-what-was-measured)
2. [How these numbers were stress-tested](#2-how-these-numbers-were-stress-tested)
3. [What is not identified, and why it survives](#3-what-is-not-identified-and-why-it-survives)
4. [The one measurement that breaks each](#4-the-one-measurement-that-breaks-each)
5. [What a next campaign is projected to achieve](#5-what-a-next-campaign-is-projected-to-achieve)
6. [What stays out of reach](#6-what-stays-out-of-reach)

## 1. What was measured

Three bounds, each with the construction that produced it.

**Collisional self-broadening.** Below [0.030](../../results/beta_self_probe.csv "ref:beta_self_probe:pooled_slope::bound95_nscale") MHz per 10¹² cm⁻³ at 95%,
pooled across the four hyperfine lines by a shared-slope construction
preregistered before computation, from the four-point 70 to 130 °C density
lever ([`run_beta_self.py`](../../scripts/run_beta_self.py),
[`beta_self_probe.csv`](../../results/beta_self_probe.csv)). The pooling is
licensed by physics, one R⁻⁶ slope for hyperfine components of one
parity-forbidden line, and checked in the data. The loosest per-peak bound,
below 0.05, stands beside it as the geometry-robust floor, and both include
the 20% density systematic. The effective coefficients sit at 0.005 to
0.016, each below 2 sigma against its own standard error, so nothing
resolves a collisional width and every number here is a bound.

**The unexplained Gaussian width, which this record used to call the laser
width.** Below 2.4 MHz on the two-photon transition axis, the axis the
analysis works on, or [1.2](../../results/laser_epoch.csv "ref:laser_epoch:sigma_laser_bound:over_w0_band") MHz per photon
([`laser_epoch.csv`](../../results/laser_epoch.csv)). **The name matters
more than the number.** What the fit bounds is the Gaussian left over once
transit is removed at the measured waist, which is why the bound rises with
the waist and falls to zero near 16 µm. **The laser is not what fills that
slot.** A wavemeter record taken mid-acquisition holds a 100 kHz standard
deviation over 24 minutes, the comb read as a clock bounds the
non-repeating excursion below 28.3 kHz, and the previous generation of this
laser, at about 100 kHz, produced a line of **4.9 to 5.2 MHz on this page's
transition axis** (2.4 to 2.6 per photon), which is where the 2025 line sits
at about 5.25. The axis matters and the natural width settles it: at
3.49 MHz on the transition axis, a 2.4 MHz line would be narrower than
natural and therefore impossible, so the comparison only closes when both
numbers are read on the same axis. **A laser two orders of magnitude
narrower than this bound reproduces the observed line**, and about a
megahertz of Gaussian width is unaccounted for. The record's leading
candidate is residual Doppler from a retro tilt of 3.2 to 3.5 mrad, about
0.19 degrees, which section 4 measures directly. The waist enters here too,
and it is the record's largest open systematic (its own standing is in the
next block).

**The light shift.** The joint three-session fit detects no shift: the
best-fit power coefficient is consistent with zero (Δχ² against zero of
0.12). What the data give is a 95% upper limit, S₀ at the campaign's
225 mW operating power **below [0.26](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_ub95:primary") MHz**
([`run_stark_joint.py`](../../scripts/run_stark_joint.py),
[`stark_joint.csv`](../../results/stark_joint.csv)). The limit comes from
how the line moves with power and needs no waist.

The predicted shift does need one. At the 64 µm waist, measured by Rajasree
on this same optical table with the same laser and lenses, though not in
the cell at campaign time, which is why section 4 still asks for the
profile, the prediction is [0.35](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_pred:prediction") MHz, above the limit, so the prediction is excluded at 95%, at
about two sigma. Over the waist measurement's own 62 to 68 µm band the
prediction runs 0.30 to 0.38, all of it above the limit, so reconciling at
95% needs a waist outside its stated band. One robustness arm weakens the
exclusion: dropping peak 4192 removes a whole session and raises
the limit to 0.37, which does not exclude the prediction. And the
prediction stands on a polarizability whose sign this record's own
[THEORY_NOTE](../THEORY_NOTE.md) finds opposite to the published
calculation. The experimenter settled it, taking this
record's value as the package value and keeping the published one named
beside it. **An adjudication is not a measurement.** The sign stays unset by
experiment, and what would settle it is the fixed-lock pull direction,
section 4. The prediction cell linked above was computed before that
decision, which raises it by about 5 per cent. Its producer needs two
sessions held outside this repository and carries the change when it next
runs. No bound moves either way, because every bound here reads the
magnitude. So the excess of prediction over limit
has three candidate readings, a waist error beyond its band, a
polarizability magnitude error, or the 5% fluctuation, and the measurements
that decide it are a beam profile in the interaction volume and a longer
power lever, section 4.

The construction: every point of every canonical power-sweep profile enters
one three-session maximum-likelihood fit with one shared coefficient,
per-peak physical widths under a prior from the collisional chain, per-trace
free centres that profile out drift and re-locks, and a per-session
detector-saturation nuisance. The subset spread is the dominant systematic on this bound:
0.26 MHz from all three sessions, 0.24 with the red-wing nuisance
marginalised, 0.37 with peak 4192 dropped. The primary uses every trace the
record admits, and dropping a peak is a robustness arm rather than an
alternative headline.

One term is deliberately absent, and its absence is conservative in the
direction that matters. Atomic saturation broadens with the same power
signature as the light shift: injecting the standard two-level term and
re-profiling moves the width-only bound by a measured 2.8 and this joint
bound by 2.21
([`saturation_companion.csv`](../../results/saturation_companion.csv)).
The term stays out because for this system that law is an underived
approximation, and licensing it would only tighten the bound.

A reported instability in this bound was an input artefact, five samples
crossing a trim boundary, and the primary bound is untouched. The diagnosis
is entry three of the next section, because the atom does not appear in it.

## 2. How these numbers were stress-tested

Each entry reads the same way: a number was believed, an instrument was
pointed at it, and here is what came back. The full audit trail is in
[HISTORY.md](../HISTORY.md).

* **The factor-two optimisation alarm.** Independent optimisations appeared
  to disagree about the light-shift bound by a factor of two. Diagnosed as
  the diagnostic's own display normalisation, curves each stored against its
  own minimum. Anchored in absolute χ², all five independent starts sit
  well above the production optimum and none enters the confidence region.
* **The megahertz-scale drift.** Read as laser drift, diagnosed as hand
  re-centring after cavity-lock dropouts: between consecutive condition
  blocks, 99.8% of the position excursion is the oscilloscope's horizontal
  setting. The corrected frame flipped the sign of two of the three drift
  estimators.
* **The code-version instability that was not one.** Rerunning the
  light-shift construction under later code moved a subset bound by about a
  third. A commit-range sweep found the cause: one commit regenerated the
  committed ruler CSVs as a side effect of a rename, fitted rates moved in
  their eleventh digit, and an axis shifted by that much walks a discrete
  trim boundary across a sample edge, admitting five samples. The code
  itself is bit-stable across the range. How much of the movement five
  samples account for is still being measured.
* **A trend that dissolved when the samples were counted properly.**
  Consistent with zero once the correlation between samples was propagated
  into the weights: at a median integrated autocorrelation of 3.8 samples, a
  trace carries roughly a quarter of the independent information its raw
  count suggests. Attributing that correlation to a mechanism has failed
  three times and stays marked open.
* **The record's own provenance, audited to the row.** Every published
  numeric claim in this record now declares what regenerates it, a committed
  instrument counts the declarations and names the seven notes whose numbers
  nothing regenerates
  ([`unregenerated_claims.csv`](../../results/unregenerated_claims.csv)). One
  published regression failed its reconstruction outright and every surface
  that quotes it says so.
* **The acquisition-mode explanation, corrected by the experimenter.** The
  record explained a 1.9 ms sample correlation as the scope's High Resolution
  mode smoothing adjacent points. The experimenter said the mechanism was
  wrong, and the instrument manual settled it his way: a disjoint
  per-interval average, capped at twelve bits, exactly where the campaign's
  files sit. Direct apparatus knowledge outranked a documented inference,
  and the correlation is unexplained, the decimation stage the
  candidate.

## 3. What is not identified, and why it survives

![which lever breaks which degeneracy](../../figures/fig35_orthogonal_information.png)

*The record's degeneracies and the lever that breaks each, drawn from the
committed results.*

**The width split.** The laser and collisional contributions to the line
enter as a sum that the observable constrains almost perfectly and a split
that it barely constrains at all. In the production per-condition fit, which
holds the transit width at its waist-derived value, the two are correlated at
about −0.92. A property of the lineshape, a Lorentzian core convolved with a Gaussian,
not of the sample size, so more data does not fix it
([the identifiability page](../wiki/identifiability.md)).
Free the transit width as well and the degeneracy moves instead of lifting:
[`identifiability.csv`](../../results/identifiability.csv) then reports
−0.958 between the collisional and transit widths, the same exchange seen from
a different direction.

**Transit against waist.** The transit width follows from the waist.
The 64 µm value is Rajasree's measurement on this same optical table, laser
and lenses. What this campaign did not do is re-measure it in its own
interaction volume at its own time. A wrong waist is absorbed by the other
widths, so it never shows up as a misfit.

**The excluded sessions' absolute frequency axis.** Usable as fractional
changes, not absolute positions, until the axis is repaired.

**Amplitude against detection.** The departure from the square-of-power law
follows peak brightness where branching ratio would be the atomic ordering,
so it points at the detection chain. No single acquisition chain
can separate those two readings.

**Temperature.** The cell was instrumented, four thermocouples between the
vapour cell and its metal case inside a cubic foil-wrapped oven, and what
the dataset carries per block is the set point, not a logged thermocouple
series. One session's internal temperature spans 110 to 130 °C, a factor
3.2 in vapour density, propagating into every density-linked quantity.

## 4. The one measurement that breaks each

| what is unidentified | the measurement that removes it | why it works |
|---|---|---|
| the width split | an independent laser-width measurement | it removes one side of a correlated pair, and the other side's uncertainty falls by 1/√(1 − ρ²), about 2.5 to 3 across the committed conditions |
| transit against waist | a beam profile in the interaction volume | one afternoon, no atoms required |
| the excluded axis | the frequency-axis repair, already scoped | the rulers exist in those traces and were not used |
| amplitude against detection | four peaks on one vertical range, and one photocurrent on two acquisition chains at once | the confound is the range switch and the chain, so hold both fixed |
| temperature | the wide-scan Doppler pedestal as an in-situ thermometer | one slow trace per block converts an set-point temperature into a measured one |

The width-split factor rides the correlation: 2.29 at the median ρ = −0.90
over the 32 committed conditions, 2.52 at the tutorial's design point, and
2.97 at the pinning simulation's bright condition, where nine seeds give
3.18 ± 0.20, quoted as an ensemble because a single seed of the same
simulation returns the largest of the nine.

The tutorial's own claim that widening the scan span breaks this degeneracy
did not survive being run: the correlation barely moves with span or with
ten times the traces
([`twin_span_sweep.csv`](../../results/twin_span_sweep.csv) regenerates the
sweep from a named committed condition).

## 5. What a next campaign is projected to achieve

Everything in this section is a projection from the forward model
([`forecast.py`](../../rb5s6s/forecast.py) and
[the campaign twin](../wiki/the-digital-twin.md)), not a result, and each
carries the condition that would break it. The twin generates the data a
set of experimental controls would produce, runs the real analysis on it,
and reports what it recovers and how often, a weaker statement than what
the campaign would establish.

* A one-range power ladder removes the range-switching confound from the
  width and amplitude channels, projected gain about 2.6 from a tight bright
  range. Broken if the dynamic range cannot be held, in which case two
  overlapping blocks with shared rungs measure the offset instead.
* The Doppler pedestal converts an set-point temperature into a measured one.
  A Doppler width scales as the square root of temperature, so 20 K at
  400 K asks for a width fit good to 2.5%. Broken if the pedestal does not
  separate from scattered light, or if cell gradients dominate the single
  number.
* Randomised ladder order breaks the power-against-time collinearity that
  makes every 2025 power trend equally a time trend. Broken if drift
  remains correlated within blocks despite randomisation.

## 6. What stays out of reach

A measured collisional coefficient, at these densities and this
temperature lever. The width split without an external constraint, at any
sample size. An absolute cell temperature without an in-situ thermometer.
And the absolute optical frequency of the transition, a different quantity
from the scan-axis repair of section 4, which this apparatus was never
built to deliver and which the record does not claim.

## Where to check any of this

[RESULTS.md](../RESULTS.md) for the results ledger, every value read from
its producing CSV,
[CLAIMS.md](../CLAIMS.md) for the claim ledger, what is claimed and what
deliberately is not,
[RESEARCH_DECISIONS.md](../RESEARCH_DECISIONS.md) for every rejected
alternative,
[PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md) for the
commitments made before looking, and
[REPRODUCING.md](../REPRODUCING.md) for what runs from a clone.

This page opens [the plan](../PLAN.md), whose eleven chapters carry the
designs behind sections 4 and 5.
