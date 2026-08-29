# The case in ten minutes

**The question.** What the 2025 campaign established, what it could only
bound, and what the next measurement has to change to convert the second
into the first.
**Takes.** No prior familiarity with the apparatus. Every number is linked
to the file that produced it.
**Gives.** The three systematic limits with their status, the reason each
is a bound and not a value, and the design that lifts each one.
**Skip if.** The question is how a single quantity is constructed. Each has
its own page under [quantities](../quantities/), and the campaign design is
[chapter 2](02_priorities.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

This is a 2025 two-photon 5S-6S spectroscopy campaign in a rubidium vapour
cell. The three quantities below are the systematic limits on any precision
measurement built on the transition, and the question is not what they are
but what currently prevents measuring them.

Every number below is a committed result with its producer named, except
where this page says otherwise, and it says otherwise in three places: the
pinning factors of section 4, the independent-information fraction of
section 2, and the projected ladder gain of section 5. Those come from notes whose numbers no producer
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

**The unexplained Gaussian width, which is not the laser.** Below 2.4 MHz on the two-photon transition axis, the axis the
analysis works on, or [1.2](../../results/laser_epoch.csv "ref:laser_epoch:sigma_laser_bound:over_w0_band") MHz per photon
([`laser_epoch.csv`](../../results/laser_epoch.csv)). **The name matters
more than the number.** What the fit bounds is the Gaussian left over once
transit is removed at the measured waist, which is why the bound rises with
the waist and falls to zero near 16 µm. **The laser is not what fills that
slot.** A wavemeter record taken mid-acquisition holds a 100 kHz standard
deviation over 24 minutes, the comb read as a clock bounds the
non-repeating excursion below 28.3 kHz on this page's transition axis, and
the previous generation of this
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
0.12). The data give a 95% upper limit on S₀, the
shift an atom on the beam axis sees at the campaign's 225 mW, the deepest
anywhere in the beam:
**below [0.26](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_ub95:primary") MHz**
([`run_stark_joint.py`](../../scripts/run_stark_joint.py),
[`stark_joint.csv`](../../results/stark_joint.csv)). The limit is not read from where the
line sits: every trace keeps a free centre, profiling drift and re-locks
out exactly. An on-axis shift instead spreads the line into a ramp of red
shifts across the beam, broadening and skewing it as power rises, with no
waist needed.

The predicted shift does need one. At the 64 µm waist, measured by Rajasree
on this same optical table with the same laser and lenses, though not in
the cell at campaign time, which is why section 4 still asks for the
profile, the prediction is [0.364](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz, above the limit, and the limit lies below the whole predicted envelope,
1.404 to 1.760 in κ over the stated waist and retro band, so on the full
three-session fit the prediction is excluded at 95 per cent at every geometry
in that band. **Two things qualify that exclusion.**

**The strength is a range and not a number.** Δχ² runs 4.1 to 5.7 across the
envelope, 2.0 to 2.4 σ, and the same profile read as a posterior puts the
computed value in the upper 3 per cent, about 1.8 σ. What is withdrawn is a
single calibrated two-sigma, not the existence of a significance.

**The stronger reading of the same data is the full-archive fit**, over both
ladders and not three sessions: κ < 0.944, Δχ² of 6.5 to 10.5 across the
same envelope, 2.5 to 3.2 σ, and all four leave-one-out arms clearing the
threshold with margin. It carries a failing prior-tension gate of its own,
`gate_B4` at 3.78 σ on the collisional width, which is degenerate with the
channel the bound is read from, so it is the stronger construction and not an
unqualified one.

**On the three-session fit the exclusion is fragile to leaving one peak out.**
The leave-one-out Δχ² are 8.75, 2.27, 1.12 and 0.61 against a 2.706
threshold, at the pre-adjudication κ of 1.545 and not at this record's own
1.618. Each arm is a fit with one peak removed against its own minimum, so
they do not share the full profile's derivative. Carrying them to 1.618 needs no curvature model. Each arm's own committed pair, at 1.545 and at 2.62, brackets it between its value at 1.545 and that value plus its own secant slope across the gap, giving 4121 in [8.75, 10.05], 4192 in [2.27, 2.77], 4154 in [1.12, 1.35] and 4207 in [0.61, 0.86]. So 4121 clears at both ends, 4154 and 4207 fail at both ends, and 4192 straddles the threshold and is not callable. **No count of arms is quoted, because one arm's bracket straddles the
threshold.** That is the same lesson as the calibration withdrawn above, one
level down.

What the data support is the inversion. Taking the geometry as a stated
prior, the width channel puts the magnitude of the differential
polarizability below
[837](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:delta_alpha_abs_ub95_profile")
a.u. in the record's own construction and below
[1038](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:delta_alpha_abs_ub95_posterior")
a.u. read as a posterior, against the
[0.35](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:estimator:sigma_from_zero")
σ that separates the fit from zero. **The gap is real and what is withdrawn is the
number attached to it**: the computed 1145 a.u. sits in the upper tail
at
[0.0324](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:comparison:posterior_prob_above_computed_here")
under the posterior and at 0.017 under the crossing, so it is a real tension
under both readings and quotable to neither's third digit. Over the ±1σ box
in waist and retro ratio the prediction runs 0.32 to 0.40, all above the
primary limit, so reconciling through the geometry needs an effective waist
outside that box.

One caveat runs the other way and is easy to over-read. The limit bounds the
**sum** of three channels that all broaden as the square of the power, of
which the ramp is about a sixth. But width grows as the square of the shift,
so a bound on the coefficient scales as the square root of that budget: the
companions make the limit about 2.4 times conservative, not six.

The prediction stands on a polarizability whose sign this record's own
[THEORY_NOTE](../THEORY_NOTE.md) finds opposite to the published calculation.
It was adjudicated: this record's value is the package value, the published
one named beside it. **An adjudication is not a measurement.** The sign stays
unset by experiment, and the fixed-lock pull direction would set it, section
4. The cell linked above already carries that decision. The joint fit's own
prediction cells do not, and are 5 per cent low until their producer runs
again. No bound moves, since every bound here reads the magnitude.

So the excess of prediction over limit keeps three candidate readings, and
this page does not rank them, because no evidence here discriminates between
them. They are an effective intensity below
what the bench geometry implies, a polarizability magnitude smaller than
computed, and a forward model missing something that suppresses the width
response to power. A beam profile in the interaction volume separates the
first from the other two, and a longer power lever sharpens all three,
section 4.

**And there is a configuration that attacks the geometry directly.** Measure
the coefficient at two waists in one session: κ scales as 1/w₀², so in the
ratio κ(w₁)/κ(w₂) the polarizability cancels exactly and what is left is the
geometry. The full form of that identity carries (1+ρ₁)/(1+ρ₂) as well, and
changing the focus is exactly what moves ρ, so the pair measures w₀²/(1+ρ)
and not w₀² alone, which is the same degeneracy one level down. It still
falsifies a mis-scaled geometry, which no single-waist measurement can, and
the skew is what separates the ramp from its companions. The full argument
and its limits are in
[`docs/plan/02_priorities.md`](02_priorities.md).

The construction: every point of every canonical power-sweep profile enters
one three-session maximum-likelihood fit with one shared coefficient,
per-peak physical widths under a prior from the collisional chain, per-trace
free centres that profile out drift and re-locks, and a per-session
detector-saturation nuisance. The subset spread is the systematic this bound is
usually read on: 0.26 MHz from all three sessions, 0.15 from the
campaign rows alone, 0.24 with the red-wing nuisance marginalised, and 0.366
with peak 4192 dropped, which lands inside the predicted envelope and not
below it. A second systematic, the pooled construction's
pass-to-pass spread, is recorded in
[chapter 8](../big_picture/08_when-a-joint-fit-is-legitimate.md) and is not
among the reasons above: two diagnostics of near-identical size sit behind
that factor and one of them is a display-normalisation artefact, so the
record leans on neither. The primary uses every trace the
record admits, and dropping a peak is a robustness arm rather than an
alternative headline.

One term is deliberately absent, and its absence is conservative in the
direction that matters. Atomic saturation broadens with the same power
signature as the light shift: injecting the standard two-level term and
re-profiling tightens the width-only bound by a measured factor of
[2.75](../../results/saturation_companion.csv "ref:saturation_companion:C3d:factor_with_saturation_ratio_-1p2362"),
and the joint bound by about 2.2 in a 2026-08-10 run on data trees this
repository does not hold, reproduced by no producer here.
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
  blocks, 99.8% of the steps' mean square is the scope's horizontal
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
* **The acquisition-mode explanation, corrected on direct apparatus knowledge.** The
  record explained a 1.9 ms sample correlation as the scope's High Resolution
  mode smoothing adjacent points. That mechanism was
  wrong, and the instrument manual settled it instead: a disjoint
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
| the width split | an independent laser-width measurement | it removes one side of a correlated pair, and the other side's uncertainty falls by 1/√(1 − ρ²), about 1.3 to 2.5 across the 32 committed conditions, rising to about 3 at the design points the text below names |
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

This page opens [the plan](../PLAN.md), whose chapters carry the
designs behind sections 4 and 5.
