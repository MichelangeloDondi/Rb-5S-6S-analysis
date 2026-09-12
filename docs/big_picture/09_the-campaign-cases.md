*Chapter 9 of 9 of [the big picture](../BIG_PICTURE.md)*

## 9. The two campaign cases, side by side

**The question.** What does a new campaign add in total, if it is
cell-only, and what does the fibre add on top?
**Takes.** The per-measurement weighings of
[chapter 5](05_next-vapour-cell.md) and [chapter 6](06_next-nanofibre.md).
**Gives.** The two scenarios in three registers each, the paired
acquisition geometry's conditional verdict, and the comparison read
for the group whose fibre it is.
**Skip if.** You want single measurements costed, which is chapters 5
and 6, or the day-by-day schedule, which is [the plan](../PLAN.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

[Chapter 5](05_next-vapour-cell.md) weighs each vapour-cell measurement with its cost and
[chapter 6](06_next-nanofibre.md) does the same for the guided platform. This
chapter answers the question those two leave open: what does a new campaign
add in total, if it is cell-only, and what does the fibre add on top. Each
scenario is stated in three registers, the physics, the record, and the
instrumentation that outlives the campaign, because the three are different
kinds of gain and conflating them is how campaign cases go soft. Every
number is read from a committed file, named inline. Nothing below is
scheduled or agreed.

A reader with no fibre loses nothing on their path by stopping after the
first scenario. The fibre thread of this repository is the set of surfaces
[BIG_PICTURE.md](../BIG_PICTURE.md) declares, which is where the list is kept
and is not restated here, because a second copy drifts and this sentence
carried one that did. It
is deliberately separable: the analysis pipeline is platform-neutral, and
[ADAPTING.md](../ADAPTING.md) carries the seam map for a different
transition or a different geometry.

### Scenario one, a new vapour-cell campaign alone

**Why a new campaign and not a re-analysis, in one measurement.** The
fixed-lock workhorse is the mean pull, first order in the shift, which the 2025
drifting lock absorbed into free centres. The third cumulant is a skew hunt
the plan lists third and does not promise, and
[`results/moment_power_map.csv`](../../results/moment_power_map.csv) measures
why: across 432 configurations of the laser kernel, the noise level, the
oscilloscope, the analysis window and the model's own grid, at two thousand
traces on each of five shifts from 0.18 to 2.0 MHz, **the cubic law is not
recovered on a ladder that starts below the 2025 shift**. The fitted exponent
of the third cumulant comes back at 1.8 with a standard deviation of 0.7 across
the grid where the physics gives 3, because the magnitude of a cumulant smaller
than its own noise is inflated by that noise, and the rungs at and below the
archive's shift are that case. The archive took five traces a rung against the
map's two thousand, and a second map at forty thousand traces on a ladder from
the 2025 shift up
([`results/moment_power_map_deep_rungs.csv`](../../results/moment_power_map_deep_rungs.csv))
finds the 2025 rung a coin flip in every configuration and the channel opening
only between one and two megahertz of shift. What raises the shift is the
power and the tighter waist. What the repaired lock buys is the pull channel
that does not need it. **The forecast now exists and it reads three ways at once**
([`results/three_channel_forecast.csv`](../../results/three_channel_forecast.csv)),
one campaign lever at a time, each cell injecting a known coefficient and
reporting what each channel recovers with its scatter over four hundred trace
sets.

**The fitted centre is the campaign's channel.** It recovers the coefficient
the configuration implies to better than one per cent at every waist the
campaign proposes, in a world that carries the axial collection window and
the standing wave's fringe-resolved tail ([chapter 12](../plan/12_open-apparatus-items.md)):
the local ramp is mixed along the collected length and the fringe density
replaces the transverse law inside it, so the asymmetry at the tight waist is
the reversed and suppressed one the bench produces, not the pure ramp's. The centre's slope is inverted through the quiet curve's own centroid
slope, which those two terms leave at [0.98](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_64um::pull_factor_quiet"),
[0.89](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_40um::pull_factor_quiet"), [0.69](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_24um::pull_factor_quiet")
and [0.58](../../results/three_channel_forecast.csv "ref:three_channel_forecast:base::pull_factor_quiet") of the pure ramp's mean pull at
64, 40, 24 and 16 microns, so the recovery below is against that geometry. The
two-time computation in [the plan's intensity
chapter](../plan/04_intensity-and-light-shift.md) narrows the line by about
two per cent at the tightest waist and leaves the mean pull the composition's
by the first moment of that spectrum, so the chirp is not what the coefficient
there waits on. The channel is untouched by the term that decides the other
one, because power broadening is symmetric and does not move a centre.

| waist | injected | the centre recovers |
|---|---|---|
| 64 microns | [1.618](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_64um::kappa_true") | [1.63](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_64um::kappa_pull") plus or minus [0.11](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_64um::sd_pull") |
| 40 microns | [4.143](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_40um::kappa_true") | [4.15](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_40um::kappa_pull") plus or minus [0.12](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_40um::sd_pull") |
| 24 microns | [11.507](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_24um::kappa_true") | [11.49](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_24um::kappa_pull") plus or minus [0.18](../../results/three_channel_forecast.csv "ref:three_channel_forecast:waist_24um::sd_pull") |
| 16 microns | [25.891](../../results/three_channel_forecast.csv "ref:three_channel_forecast:base::kappa_true") | [25.89](../../results/three_channel_forecast.csv "ref:three_channel_forecast:base::kappa_pull") plus or minus [0.34](../../results/three_channel_forecast.csv "ref:three_channel_forecast:base::sd_pull") |

**Every number in this section carries one model-form caveat, the centre
numbers included, and at the tight waist it is the centre numbers that carry it
hardest.** The forecast composes each rung with a single homogeneous kernel,
which is exact only where that kernel is the same at every collected volume
element. It is not: the saturation companion is set by the light shift at each
element, and the light shift is what the ramp distributes, so the broad
elements are the shifted ones. The homogeneous width runs over a factor of
[3.247](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:homogeneous_width_span") across the collected volume at
16 microns.

Measured element by element against the same mixture with the kernel held
fixed, at 64, 40, 24 and 16 microns:

| what is read | 64 um | 40 um | 24 um | 16 um |
|---|---|---|---|---|
| the centroid, per cent | [0.000](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:centroid_pull_error") | [0.000](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w40um:centroid_pull_error") | [0.000](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w24um:centroid_pull_error") | [0.000](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:centroid_pull_error") |
| the fitted centre, per cent | [-0.265](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:fitted_centre_error") | [-1.906](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w40um:fitted_centre_error") | [-17.247](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w24um:fitted_centre_error") | [-56.972](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:fitted_centre_error") |
| the third cumulant, per cent | [106.911](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w64um:k3_error") | [103.337](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w40um:k3_error") | [96.452](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w24um:k3_error") | [89.701](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:k3_error") |

**The centroid is exactly immune and the estimator is not, and reading the
first as covering the second is the error this table replaces.** The first
moment of a mixture of symmetric kernels is the density's own mean, so a
broadening symmetric about each element's own centre cannot move it, at any
waist, exactly. A least-squares fit with a single width is a different quantity. It
sits on the mode, the mode is set by the narrow unshifted elements, and the
shifted elements are the broad ones. The pull rows above are that fit, through
`fit_condition` with the shift held at zero. So at the archive's waist both
channels are safe to a quarter of a per cent, and at the campaign's own 16
microns the standard channel reads the pull it inverts wrong by
[-56.972](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:fitted_centre_error") per cent,
which is larger than anything the moment channel's caveat carries.

**So neither family is quotable at 24 microns or below until the kernel follows
the shift inside the forecast's own mixture**, and the tight-waist rows above
are an upper bound on their own accuracy and not a result. The
cumulant figures are quoted against the most charitable single kernel there
is, the volume's own weighted mean. Against the kernel the twin actually
composes with, the companion at the on-axis shift, the cost at 16 microns is
[95.350](../../results/kernel_inhomogeneity.csv "ref:kernel_inhomogeneity:w16um:k3_error_forecast_kernel") per cent. The
uncertainties are the saturation companion's own, which the record carries at
the factor-of-three level, not a grid.

**The higher moments alone work only where the comb is on the trace.** At
the tight waist the light
shift is large enough that the transition saturates, and saturation broadens
the line in proportion to the power while the ramp's asymmetry grows as its
cube, so the third cumulant's own law flattens and the channel reads noise. A
phase-modulated comb holds the intensity constant, and with it the light
shift, while splitting the two-photon drive among the teeth. Each tooth's Rabi
frequency is then the root of its share, its saturation broadening falls with
it, and the asymmetry survives. Those cells are the twin's world with the
collection window and the fringe tail in it: at the tight waist the window
reverses the third cumulant's sign against the pure ramp and the fringes
suppress it further, and each admitted rung is inverted through the quiet
curve's own local law with the sign read from that curve, so the comb cells
are quoted against the bench's geometry. On the 40 MHz comb the moments recover
[25.8](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_40MHz::kappa_skew") plus or
minus [2.1](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_40MHz::sd_skew"), on
the 25 MHz comb [25.6](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_25MHz::kappa_skew")
plus or minus [2.4](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_25MHz::sd_skew"),
and on the 2025 spacing of 12.5 MHz, which the world without those terms
refused, [26.3](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_12.5MHz::kappa_skew") plus or minus
[4.4](../../results/three_channel_forecast.csv "ref:three_channel_forecast:eom_comb_12.5MHz::sd_skew"), twice the wide combs' scatter,
against the same injected coefficient the centre reads. **Without a comb the
channel is not refused, it is unreliable**: 13 comb-free cells recover a
coefficient and they span -0.6 to 37 per cent of the injected value, all but one of
them high, because the sign gate that admits a rung is one-sided. The one that
reads low is the widest analysis window of the producer's own scan, which is
where the truncation the gate compensates for is smallest. The comb is what makes the
channel accurate, not what makes it exist.

**The two combined are a check and not a result**, by the rule the campaign
wrote before the file existed. The combination moves the better single
channel's scatter by under a tenth, either way, in every cell that carries
both except the 2025 comb, where the two channels are comparably weak and it
gains 14 per cent. Elsewhere the centre is an order of magnitude the tighter
wherever the moments are alive at all. It confirms and it does not sharpen.
The producer is `scripts/run_three_channel_forecast.py`. Raising the
shift is what opens the channel, and raising it is what the higher power and
the repaired lock do.

**The physics.** Four conversions, from bounds to measurements.

* The beam waist, measured in an afternoon with no atoms, converts every
  intensity-denominated number in the record at once, since the light shift
  goes as one over the waist squared
  ([chapter 5](05_next-vapour-cell.md), item 1).
* The light-shift coefficient: one morning of randomised power cycling under
  the repaired lock detects the predicted shift at 3.8 sigma and separates
  the two disputed polarizability signs at 8 sigma if the shift is the
  predicted size, conditional on the lock's residual, which the plan spans from zero to 0.04 MHz per minute
  ([CLAIMS](../CLAIMS.md) section 3, `results/projections.csv`). That span
  is narrowed at no cost in beam time: the oscilloscope records four channels,
  the cavity error signal on one of them flags every in-loop excursion and
  dropout in the trace it happened in, and the hyperfine intervals the same
  sweep crosses measure the reference's own drift out of loop
  ([plan 7](../plan/07_acquisition-settings.md)).
* The collisional coefficient: same-session 150 to 170 C points with the
  block noise cut fourfold resolve the expected rate near 10 sigma. Both
  halves are needed, and with the noise floor uncut the reach is 3 sigma.
  Even resolved, the coefficient carries the 20 per cent density-scale
  systematic until an independent density measurement
  ([CLAIMS](../CLAIMS.md) section 3).
* The laser content: the kernel question is tested at one end-member and open in between (`results/laser_kernel.csv`). The cell campaign's own routes to
  the content are the lock's error signal and a fast-scan comb block
  ([plan chapter 7](../plan/07_acquisition-settings.md)).

**The record.** This scenario converts the flagship analysis from a method
with bounds into a method with measured coefficients, which is its strongest
single form, and it enables the matrix-element-by-null measurement at
1297.5 nm as a second, cheap result riding the same session
(`FUTURE_TRANSITIONS_titsapph.md` section 5.1: the 6S to 7P strength read at
1.8 per cent by frequency metrology, with a sign-reversal test of the
asymmetry channel and a calibrated shift injector as by-products).

**The instrumentation.** What outlives the campaign: a laser whose width
and drift budget are characterised against the atoms themselves, a measured
waist protocol for the bench, and the O-band shift injector as a standing
calibration tool, 3.6 kHz per picometre at a known crossing, usable by any
later experiment that needs a known injected shift.

### Scenario two, the fibre added

Everything in scenario one, plus five additions no cell can provide.

**The physics.**

* The laser's shape, measured independently. The cold trap-off line at the
  fibre is the known natural width plus the laser contribution, a
  73 to 98 kHz transit, and the atom-surface term, and the molasses
  temperature sweep turns the transit term into its own sqrt(T) ladder.
  **The atom-surface term makes a loaded trap a precondition, not an
  enhancement**, and the group's papers carry the trap's light without
  reporting a loading: untrapped, atoms sampling 50 to 300 nm carry an
  inhomogeneous red tail that is degenerate with the laser width, and at a
  fixed 200 nm it falls to 0.21 to 0.53 MHz and is largely common-mode
  (`results/onf_candidate.csv`). Fed back as a prior, it recovers
  the collisional coefficient's error to 0.36 of the free-kernel fit
  on the data already taken, against the exact floor of 0.585 that any
  single-component measurement hits (`results/kernel_identifiability.csv`,
  and **that prior is the one asking 0.01 MHz on each of the two kernel
  widths. That is the 69-minute trace, not the 2.78-minute working point the
  cost rows below quote. It is about 5.5 hours of acquisition, some
  twenty-four times the per-lever figure**,
  the joint rows). This addition improves the committed record
  retroactively, before any new cell point is taken. **The payback is on the
  collisional coefficient specifically**, and it is not a general claim that
  the fibre improves the record: on the width channel the twin measures the
  same Lorentzian-against-Gaussian correlation of about -0.94 in both arms
  ([chapter 6](06_next-nanofibre.md),
  `results/campaign_twin_forecast.csv`).
* The intercept budget closes. With density, the sqrt(T) ladder, the laser
  prior and geometry each pinning their own slot, the width intercept
  becomes overdetermined, and the sum of independently measured parts
  against the measured whole is a falsifiable closure test, not a
  decomposition argued from a fit.
* The near-surface lineshape. The two-peak pushing profile observed on this
  exact line at this exact platform ([Gokhroo 2022](../lit/gokhroo2022.md))
  has never been modelled, and the atom-surface potential on this platform
  class is now known to carry two components, Casimir-Polder plus a
  device-dependent electrostatic term
  ([Pennetta 2026](../lit/pennetta2026.md)). Completing that observation
  quantitatively, with the 6S surface coefficient as an output, is an open
  problem this pipeline is built for
  ([the sized candidate](../notes/onf_candidate.md)).
* Signal feasibility is not a projection: this transition has been driven
  through a 400 nm nanofibre with cold atoms at 25 to 40 counts per
  millisecond ([Rajasree 2020](../lit/rajasree2020spin.md)).
* **The acquisition geometry, a conditional default.** The candidate
  design puts the vapour cell on the fibre channel's own sweep: the
  surface shift is read as fibre minus cell within each sweep, the
  residual lock noise is common mode to first order, and the cell's
  carrier with its EOM comb is the in-sweep ruler. The twin forecasts this against
  unreferenced acquisition, the 2025 default, across the spans of
  both unmeasured lock quantities, the drift and the per-sweep
  excursion (`run_paired_reference_forecast.py`, simulation rung).
  The scopes' acquisition memory imposes no depth penalty, and the
  export path's 64 k cap sits under a factor of two above the
  recommended record length, its two-channel behaviour unstated in
  the record. Verdicts are against a
  [0.7](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:design:ratio_threshold")
  decisive-gain threshold. Each configuration is drawn at
  [6](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:design:grid_replicates")
  independent base seeds, concatenated, so these are not single draws.
  At the comb-limit excursion class the worst ratio is
  [0.705](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.028:worst_shift_ratio")
  ± [0.015](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.028:worst_shift_ratio:err")
  and the criterion reads
  [unresolved](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.028:criterion"):
  under one sigma from the bar, no side licensed. **That error is how
  well this forecast knows the number, not what one run would give.**
  A single campaign at the same configuration realises the ratio with a
  spread of
  [0.029](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:analog/j0.028/d0:shift_err_ratio_one_campaign:err"),
  twice the forecast's own, so a real run at this excursion class can
  land on either side of the bar while the forecast's knowledge of the
  mean does not move. The two are different quantities and the file
  carries both, per configuration. From the mid class it
  [clears](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.05:criterion"),
  [0.4727](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.05:worst_shift_ratio")
  ± [0.0097](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.05:worst_shift_ratio:err"),
  and it
  [clears](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.1:criterion")
  again at the ceiling class. Each row carries its own distance to the
  bar in sigma.
  With the cleanest spanned lock the pairing sits near parity on both
  branches,
  [0.997](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:limit:clean_lock_ratio_analog")
  ± [0.021](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:limit:clean_lock_ratio_analog:err")
  analog and
  [0.960](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:limit:clean_lock_ratio_counting")
  ± [0.020](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:limit:clean_lock_ratio_counting:err")
  counting. Each branch is measured against its own error
  decomposition, the analog against
  [0.96](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:check:clean_lock_decomposition_analog")
  and the counting against
  [0.94](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:check:clean_lock_decomposition_counting").
  At that limit the criterion
  [fails](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:span_j0.009:criterion"):
  the pairing buys no decisive gain, and the file carries how far. So
  the decision row reads
  [conditional](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:decision:adopt_paired_default"):
  the scheduled lock characterisation measures which class the
  apparatus is in (the drift item of
  [plan chapter 12](../plan/12_open-apparatus-items.md), whose same
  run reads the excursion), and the geometry choice follows it. The
  pairing removes the laser only: Stark, Zeeman and transit kernels
  stay modelled offsets. No width is shared, on the record's own
  sigma_laser caveat, and the width-error ratio measures at parity in
  [29](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:check:width_ratio_within_2sigma")
  of its
  [32](../../results/paired_reference_forecast.csv "ref:paired_reference_forecast:check:width_ratio_within_2sigma:err")
  rows, the three exceptions sitting between two and three sigma, which
  is about what that many draws give when parity holds. Two of the
  three are the analog branch at the comb best-fit excursion, at
  different drifts, and the third is the counting branch at the
  ceiling. That is a concentration, not an even scatter, so the
  best-fit excursion is where to look first if the count moves. (The
  comb-limit class, which the worst ratio above is quoted from, has no
  row past two sigma at all.)
  A cell reference on alternating separate sweeps sits between these
  modes, an unmodelled limit in the producer. The quartet spans
  gigahertz against a megahertz sweep and stays pinned across
  sweeps, as in 2025. What the geometry asks of
  the fibre itself is not costed here or elsewhere yet: the
  chapter-end comparison table carries acquisition hours only, and
  says so.

**The record.** The guided-platform study becomes two results in one: the
near-surface physics above, and the joint-metrology payback into the
committed cell record, quantified row by row in
`results/kernel_identifiability.csv`. A fibre measurement therefore
improves the committed record retroactively, before any new cell point is
taken. The scope is the collisional coefficient, not the record as a whole,
and no count of what else on this list does the same is made here because
none has been run.

**The instrumentation.** This register is where the fibre scenario is
strongest, because what it leaves behind is a set of working tools, not a
result. The first of them is conditional, and its condition is stated below
instead of promised here: the Casimir-Polder surface calibration reaches 6S only if
the repaired lock's residual drift is small enough, and at the 2025 archive's
rate it is not a calibration at all.

* A per-run calibration of the **Casimir-Polder** surface term at 6S
  sensitivity, on the same class of fibre that Rydberg-near-fibre
  experiments probe at far higher sensitivity, where that term is a known
  limiter ([Pennetta 2026](../lit/pennetta2026.md)). **It is not a
  measurement of the electrostatic surface charge**, and the distinction is
  worth stating to a group that has just published on the latter
  ([Raj 2026](../lit/raj2026.md)): at the 1.5 V/cm those authors recover at
  400 nm, the electrostatic shift of this transition is 0.32 Hz, against the
  72.5 kHz Casimir-Polder term the lever ranking computes. **The transition is
  blind to the systematic that limits their Rydberg work**, which is what
  makes it a clean probe of the dispersion term and not a rival
  electrometer.
* A real-time, atom-based monitor of surface adsorbate dynamics, which is
  the community-wide fibre-degradation problem, watched through the line
  while it happens.
* The upper state's polarizability at their proposed trap's tune-out
  wavelength, read directly from the line's shift under that light, since the
  ground state is unshifted there: a quantity no experiment has measured at any
  wavelength, conditional on the fictitious-field trap being built
  ([chapter 6](06_next-nanofibre.md)).
* The two-colour trap's magic power ratio for this transition, conditional on
  a loaded trap, which the group's papers carry as light without loading,
  computed from
  the committed polarizability engine (the differential polarizability
  changes sign between the trap colours, +3086 atomic units at 750 nm
  against -804 at 1064 nm, `rb5s6s/polarizability.py`), so the trap can be
  made shift-free for spectroscopy by tuning a ratio the bench already
  controls, and the same ratio scans the trap-surface distance.
* The quadratic Zeeman injector: the hyperfine mismatch between 5S and 6S
  makes a bias field a calculable line shifter at 1.9 and 4.2 kHz per gauss
  squared for the two isotopes, from committed constants, a free calibration
  channel for any line-centre instrument on this bench. **With one condition
  that matters on her platform.** Those coefficients carry the Breit-Rabi
  bracket, one minus four times the magnetic quantum number squared over the
  nuclear factor squared, which is zero at the stretched state. A trap holding
  atoms in the maximum projection, as the fictitious-field proposals do by
  construction, therefore feels no quadratic Zeeman shift at all and the
  channel is not available on those atoms. It is available on an unpolarised
  or optically pumped low-projection sample, and its own vanishing at the
  stretched state is the reason a trap built there is magic in the field.
* A characterised laser, as in scenario one, but now characterised through
  the same guided path that fibre experiments use, under the shared-path
  condition the candidate note states.

**One hardware line the table below does not carry, stated here so it is not
discovered on the bench.** The fibre's detector shares the cell's oscilloscope
only if the modulator's radio-frequency gate can be triggered from the sweep,
and otherwise it needs an instrument of its own, a cost the fibre case carries and
the cell case does not. What the fibre keeps from the same wave is the scan
actuator's bow measured in situ from the hyperfine and comb anchors the shared
sweep crosses, a calibration her programme reuses on any line.

### The comparison for the group whose fibre it is

**The question is not whether the fibre is interesting. It is whether the
fibre arm earns its beam time and its exposure, or whether the cell alone is
enough.** Both columns below are what a new campaign delivers, and the second
row is the one that matters to a group whose own programme is Rydberg atoms
near a nanofibre and not spectroscopy.

| | cell alone | cell plus nanofibre |
|---|---|---|
| **what the host group keeps afterwards** | nothing on their platform. The results are ours | a per-run calibration of the Casimir-Polder surface term at 6S sensitivity, the transition being blind to the electrostatic charge that limits their Rydberg probe, an atom-based monitor of adsorbate dynamics on the fibre, the two-colour trap's magic power ratio for this transition, a quadratic-Zeeman line shifter, a depth-ladder null test of the light shift demonstrated on their own modulator, and a laser characterised through their own guided path |
| **what it measures about the fibre** | nothing | the **fibre diameter**, the tolerance no held paper states and which every guided quantity depends on, to between [30.73](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.04:sigma_diameter_nm") nm at the 2025 drifting lock and [0.67](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.0:sigma_diameter_nm") nm at the photon floor, marginalised over the drive amplitude the scan cannot know. The repaired lock decides where in that span the campaign sits, and its residual is unmeasured. Also the light-shift coefficient, and the surface coefficient $C_3$ which is the weakest of the three (`results/onf_lever_ranking.csv`). **The diameter is not only obtainable this way**: the group's own scanning electron microscope gives it without atoms, and the published proximity to the 352 nm mode cutoff is a sharp independent diagnostic. What the atoms add is the quantity that actually enters the physics, measured in situ under the conditions of use, rather than a fibre characterised before it was installed ([chapter 6](06_next-nanofibre.md)) |
| **fibre time** | none | **acquisition only**, about [0.23](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:temperature_ladder:hours") hours per lever across three levers. Alignment, setup and the trap settling the distance scan needs between rungs are **not costed**, and the producer says so. The interval the host group would actually be asked to grant is an open item, not this number |
| **fibre exposure** | none | what can be quoted is integration time: about [2.78](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.02") minutes per trace at the working precision, and [69](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.004") +- [16](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.004_err") at cell-matching precision, the half-span of the committed 25 to 40 counts per ms band. **The degradation that time causes is a different quantity and is an open item**: rubidium adsorption against exposure bounds the whole arm and nothing here converts one into the other ([chapter 6](06_next-nanofibre.md)) |
| **what it settles for us** | the collisional and light-shift coefficients, from bounds to measurements | the same, plus the laser-shape confound acted on retroactively |

**The cell campaign is scheduled and the fibre arm is not yet.** The cell side is eight days, D1 to D8, each with its content and its deliverable, ordered so a truncation at any point leaves the higher-priority conversions done ([the plan](../PLAN.md), section 9). The fibre side has its acquisition hours from the lever ranking and no day plan, so the interval it would occupy is not yet a stated number. That is an open item and not an omission from this table.

**The row that decides it is the first one, and it carries a condition that
belongs beside it.** The Casimir-Polder calibration is available at
[4 to 9](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_requirement_4kHz:surface_shift_significance_at_400nm_band")
sigma once residual lock drift is at or below 4 kHz per minute, and at
[0 to 1](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_requirement_40kHz:surface_shift_significance_at_400nm_band")
sigma at the 2025 archive rate, where it is not a calibration at all. The
repaired lock's residual is unmeasured, so this item is offered as a span and
its first hour is what collapses it.

**And the same threshold decides what the campaign costs the fibre.** Below
about 4 kHz per minute the surface measurement is available **without moving
atoms closer to the glass**, which is the gentler configuration for the fibre.
Above it, reaching the same significance means working nearer the surface.
That is why the lock matters to the fibre's owner and not only to us: it sets
how close to the glass the atoms have to be.

The keep row is the currency a group lending a nanofibre is paid in. The
physics we gain is in the last row and is ours, not theirs.

**The keep row survives the mode solve unchanged.** Replacing the assumed
guided geometry with the solved one redrew the mode tables and the diameter
precision, left the cost rows standing, and moved nothing the host group
keeps, because that row is a set of calibrations and instruments and not a
precision. The corrections themselves are in the
private correction record.

**One more item joined the keep row on 2026-09-06, and it costs no beam time
at all.** The modulation depth separates the light shift from everything
driven by the excitation rate, because a phase modulation changes the spectrum
without changing the intensity, so the shift is the same at every depth while
the rate per tooth follows the Bessel weights and the power broadening follows
their square root
([the ramp chapter](../methods/03_the_ac_stark_ramp.md) derives it). It is a
null test, it uses the modulator the ruler already needs, and it transfers to
whatever line the host group drives next. It joins the keep row only in the
fibre scenario, where it is demonstrated on their own bench: in the cell
scenario it is a method in a paper, which is not the same currency.

**And the surface characterisation is not a by-product.** The near-fibre field
is what limits Rydberg spectroscopy on this platform, and the published state
of the art recovers it as a free parameter of a fit its own authors call
qualitative. A 5S-6S probe populates no Rydberg state, so it reads the same
environment without the population that complicates it.

### What decides between them

The cell-only scenario stands on its own and converts the record's bounds
into coefficients. The fibre adds the only lever that acts on the
laser-shape confound retroactively, the closure test, and the near-surface
programme, at the cost of fibre time and the transfer condition. The two
scenarios nest rather than compete: the second contains the first, and the
fibre items are exactly the ones
[chapter 7](07_limitations-and-identifiability.md) names as outside any
cell's reach.

### Two conditions on the tight-waist case, added 2026-09-12

Both scenarios above assume the model may be written as a convolution, and that
assumption has a boundary the earlier text did not carry.

**The waist band and the beam quality are one assumption, not two.** The
convolution holds while the transit width varies little over the collected
region, and that spread depends on the waist and the beam-quality factor only
through the collection ratio. A 55 µm waist sits at 1.7 per cent of spread at a
quality factor of 1 and at 5.8 at a factor of 2, against the 5.5 per cent edge
this record licenses, so the working band needs `w₀ ≳ 40 µm·√(M²)` and the
tight-waist configuration is the one that pays for a poor beam first. The
collection ratio carries its own 54 per cent uncertainty from the optics, so
near the boundary the case states a probability that its licence holds and not
a verdict.

**And the kernel form may be selectable, which the earlier text spanned.** On
the archive's own committed grid the cusp already leads the Voigt in AIC
(`docs/wiki/identifiability.md` carries the margin), so the data express a
preference where this case currently carries a spanned bar. Whether that
preference is strong enough to retire the bar is a measurement this record has
not committed, and the campaign is what would settle it: fixing the kernel by
measurement removes a systematic instead of widening an envelope.

---

*[When a joint fit is legitimate](08_when-a-joint-fit-is-legitimate.md) · [the big picture](../BIG_PICTURE.md)*
