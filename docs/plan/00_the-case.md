*The opening summary of [the plan](../PLAN.md), before its eleven chapters*

# The case in ten minutes

This page states what the 2025 dataset established, what it could not
determine and why, which single measurement removes each ambiguity, what a
next campaign is projected to achieve, what stays out of reach, and which of
this record's own claims its own instruments refuted. Every number is a
committed result with its producer named. Where a quantity is bounded rather
than measured, it is written as a bound.

In one sentence: three quantities were bounded, none was detected, the
reason each stayed a bound is identified rather than suspected, and each
reason names the measurement that removes it.

## 1. What was measured

Three bounds, each quoted with the construction that produced it.

**Collisional self-broadening.** Below 0.05 MHz per 10¹² cm⁻³, the record's
conservative statement, taken as the loosest of a per-peak 95% range of 0.03
to 0.05 from a four-point 70/90/110/130 °C density lever in one
configuration (`scripts/run_beta_self.py`, `results/beta_self_probe.csv`).
That range includes the 20% density systematic. Before it the same limits run
0.024 to 0.041, and the record quotes the inflated form. The effective
coefficients themselves sit at 0.005 to 0.016, and every one of the four has
a signal-to-noise below 2 against its own standard error (0.73, 0.82, 1.18,
1.90), so none resolves a collisional width and every line is reported as a
bound.

**The 2025 laser width.** Below 2.4 MHz on the two-photon transition axis,
which is the axis the analysis works on, equivalently 1.2 MHz per photon
(`results/laser_epoch.csv`). This one rides the beam waist: it is quoted at
the adopted 64 µm lineage waist and rises with waist. The waist is the
record's largest open systematic.

**The AC-Stark coefficient.** S₀(225 mW) below 0.258 MHz at 95%, against
0.348 MHz predicted at the same waist, from a joint three-session
profile-likelihood fit at the unscaled 2.706 threshold
(`run_stark_joint.py`, `results/stark_joint.csv`). Every point of every
canonical power-sweep profile enters one maximum-likelihood fit with one
shared coefficient, per-peak physical widths under a prior taken from this
record's own collisional chain, per-trace free centres so that drift and
re-locks are profiled out exactly rather than modelled, and a per-session
detector-saturation nuisance.

The margin, and the two things that could dissolve it. The predicted
coefficient lies above the 95% limit with Δχ² ≈ 4, a two-sigma-level
exclusion rather than a comfortable one.

First, the subset spread, which is the dominant systematic: 0.258 MHz from
all three sessions, 0.240 with the red-wing nuisance marginalised, and 0.366
with peak 4192 dropped, which removes an entire session. That last subset does
not sit below the prediction. The primary is the reference because it is
the construction that uses every trace the record admits, and dropping a peak
is a robustness arm rather than an alternative headline.

Second, a term deliberately absent from the model. Atomic saturation broadens
with the same power signature as the light shift, so leaving it out makes
this bound loose by a measured factor: injecting a saturation term and
re-profiling moves the width-only bound by 2.8 and this joint bound by 2.21.
Neither committed bound was changed, because the injected law is the
two-level homogeneous form used with a two-photon Rabi frequency, which is
standard but an approximation rather than a derivation for this system. So
the quoted bound is conservative in the direction that matters, and the
exclusion above would tighten rather than dissolve if the term were licensed.

One question about this bound has its cause identified as of 2026-08-20. Rerunning the
construction under later code moved a subset bound by about a third, measured
2026-08-14 and recorded as a code-version instability. A sweep across the
commit range, holding one environment, found the cause. The construction's
point count changes at exactly one commit, 247783 to 247788 at an unchanged
172 traces, and that commit renamed a vocabulary across the tree while
regenerating the committed ruler CSVs as a side effect. Fitted ruler rates
moved in their eleventh digit, a frequency axis shifted by that much moves a
discrete trim boundary across a sample edge in a few traces, and five samples
enter. So the inputs were never identical and the arithmetic is not
defective. The sweep says something stronger: six commits spanning nine days
of development return the same chi-square to the last printed digit at a
common grid point, and the two on the far side of the boundary agree with
each other, so the code is bit-stable across the range and the only thing
that moved was the input set. How much of the reported movement five samples
account for is being measured, and the candidate amplifier is the
ill-conditioning the subset columns already carry. The primary bound is
untouched either way.


## 2. What is not identified, and why it survives

**The width split.** The laser and collisional contributions to the line
enter as a sum that the observable constrains almost perfectly and a split
that it barely constrains at all. In the production per-condition fit, which
holds the transit width at its waist-derived value, the two are correlated at
about −0.92. This is a property of the lineshape, a Lorentzian core convolved
with a Gaussian, not of the sample size, which is why more data does not fix
it. Free the transit width as well and the degeneracy moves rather than
lifting: `results/identifiability.csv` then reports −0.964 between the
collisional and transit widths and only +0.152 between the collisional and
laser widths, which is the same trade seen from a different corner.

**Transit against waist.** The transit width follows from the beam waist.
The waist is a lineage measurement rather than a measurement in this
campaign's interaction volume, and a wrong waist is absorbed by the other
widths rather than showing up as a misfit.

**The excluded sessions' absolute frequency axis.** Usable as fractional
changes, not as absolute positions, until the axis is repaired.

**Amplitude against detection.** The departure from the square-of-power law
orders by peak brightness rather than by branching ratio, which reads as a
detection signature rather than an atomic one. No single acquisition chain
can separate those two readings.

**Temperature.** The record carries variac set points rather than
temperatures. One session's internal temperature is a range from 110 to
130 °C, a factor 3.2 in vapour density, which propagates into every
density-linked quantity.


## 3. The one intervention that breaks each

| what is unidentified | the measurement that removes it | why it works |
|---|---|---|
| the width split | an independent laser-width measurement | it removes one side of a correlated pair instead of fitting both. An external constraint reduces the other side's variance to (1 − ρ²) of its joint value, so its uncertainty falls by 1/√(1 − ρ²). That factor rides the correlation, and the record carries three: 2.29 at the median ρ = −0.90 over the 32 committed conditions, 2.52 at the tutorial's synthetic design point ρ = −0.918, and 2.97 at the pinning simulation's bright condition ρ = −0.9417. Simulated rather than computed at that last condition, over nine seeds, it is 3.18 ± 0.20 |
| transit against waist | a beam profile in the interaction volume | one afternoon, no atoms required |
| the excluded axis | the frequency-axis repair, already scoped | the rulers exist in those traces and were not used |
| amplitude against detection | four peaks on one vertical range, and one photocurrent on two acquisition chains at once | the confound is the range switch and the chain, so hold both fixed |
| temperature | the wide-scan Doppler pedestal as an in-situ thermometer | one slow trace per block converts an adopted temperature into a measured one |

That factor of 2.5 replaced a claim in this repository's own tutorial, which
taught that widening the scan span breaks the width degeneracy. Run, it does not: the correlation moves from −0.9177 at
60 MHz to −0.9166 at 300 MHz, and ten times the traces reaches only −0.881.
The pinning result that replaced it is a committed function with a guarded
test, and a ratio quoted as an ensemble rather than as a single draw
(3.18 ± 0.20 over nine seeds, after the single-seed 3.4 that four documents
had carried turned out to be the largest of the nine).


## 4. What a next campaign is projected to achieve

Everything in this section is a projection from the forward model, not a
result, and each carries the condition that would defeat it. The projections
come from `rb5s6s/forecast.py` and the campaign twin, which is an
experiment-design and identifiability engine: it takes a set of experimental
controls, generates the data those controls would produce, runs the real
analysis on it, and reports what the analysis recovers and how often. Its
output is what the analysis would recover under the simulated world, which
is a weaker statement than what the campaign would establish.

* A one-range power ladder removes the range-switching confound from the
  width and amplitude channels. Projected gain about 2.6 from a snug bright
  range. Defeated if the dynamic range cannot be held across the ladder, in
  which case two overlapping blocks with shared rungs measure the offset
  instead of hiding it.
* The Doppler pedestal converts an adopted temperature into a measured one.
  A Doppler width scales as the square root of temperature, so 20 K at about
  400 K asks for a width fit good to 2.5%. Defeated if the pedestal does not
  separate from scattered light, or if cell gradients dominate the single
  number.

* Randomised ladder order breaks the power-against-time collinearity that
  makes every 2025 power trend equally a time trend. Defeated if drift
  remains correlated within blocks despite randomisation.

Every projected number above carries the condition that would defeat it.

## 5. What stays out of reach

A collisional measurement rather than a bound, at these densities and this
temperature lever. The width split without an external constraint, at any
sample size. An absolute cell temperature without an in-situ thermometer.
And the absolute frequency of the transition, which this apparatus was never
built to deliver and which the record does not claim.

## 6. Results this record refuted with its own instruments

Five claims were removed after being tested.

* **The wider-scan claim, in this repository's own tutorial.** Asserted that
  a wider span breaks the width degeneracy. Tested, false, and replaced by the
  pinning result with a guarded test behind it.
* **The factor-two optimisation alarm.** Independent optimisations appeared
  to disagree about the light-shift bound by a factor of two. Diagnosed as
  the diagnostic's own display normalisation: curves stored each against its
  own minimum cannot be compared, and the instrument's raw output carries
  absolute χ². Anchored, all five independent starts sit 4.66 to 26.29 above
  the production optimum at every coefficient tested and none enters the
  confidence region.
* **The megahertz-scale drift.** Read as laser drift, diagnosed as hand
  re-centring after cavity-lock dropouts. Between consecutive condition
  blocks, 99.8% of the position excursion is the oscilloscope's horizontal
  setting. Recomputing in the corrected frame flipped the sign of two of the
  three drift estimators.
* **A trend that survived until the samples were counted properly.**
  Dissolved to consistency with zero once the correlation between samples
  was propagated into the weights. The median integrated autocorrelation
  across the campaign's conditions is about 3.8 samples, so a trace carries
  roughly a quarter of the independent information its raw sample count
  suggests. Attributing that correlation to a mechanism has taken three
  attempts and is still open, which the record says rather than settling.
* **A figure of this repository's own, 2026-08-20.** `fig15` panel (c) drew
  the retracted drift constant as a point labelled "the measured bound",
  while the record's provenance note says that number is not a measured rate
  in either direction. It now draws the bound the record defends, and its
  source line names the sources it actually reads.


## Where to check any of this

`docs/RESULTS.md` for the claim ledger with status labels,
`docs/CLAIMS.md` for what is deliberately not claimed,
`docs/RESEARCH_DECISIONS.md` for every rejected alternative with its
argument, `docs/PREREGISTRATION_RESULTS.md` for the commitments made before
looking and the addenda that revised them, and `docs/REPRODUCING.md` for
what runs from a clone.
