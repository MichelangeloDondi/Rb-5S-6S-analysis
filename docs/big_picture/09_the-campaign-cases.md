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

**The physics.** Four conversions, from bounds to measurements.

* The beam waist, measured in an afternoon with no atoms, converts every
  intensity-denominated number in the record at once, since the light shift
  goes as one over the waist squared
  ([chapter 5](05_next-vapour-cell.md), item 1).
* The light-shift coefficient: one morning of randomised power cycling under
  the repaired lock detects the predicted shift at 3.8 sigma and separates
  the two disputed polarizability signs at 8 sigma if the shift is the
  predicted size, conditional on the lock holding 0.02 MHz per minute
  ([CLAIMS](../CLAIMS.md) section 3, `results/projections.csv`).
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
  **The atom-surface term makes the trap a precondition, not an
  enhancement**: untrapped, atoms sampling 50 to 300 nm carry an
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
instead of promised here: the surface-charge calibration reaches 6S only if
the repaired lock's residual drift is small enough, and at the 2025 archive's
rate it is not a calibration at all.

* A per-run calibration of the electrostatic surface-charge term at 6S
  sensitivity, on the same class of fibre that Rydberg-near-fibre
  experiments probe at far higher sensitivity, where that term is a known
  limiter ([Pennetta 2026](../lit/pennetta2026.md)).
* A real-time, atom-based monitor of surface adsorbate dynamics, which is
  the community-wide fibre-degradation problem, watched through the line
  while it happens.
* The two-colour trap's magic power ratio for this transition, computed from
  the committed polarizability engine (the differential polarizability
  changes sign between the trap colours, +3086 atomic units at 750 nm
  against -804 at 1064 nm, `rb5s6s/polarizability.py`), so the trap can be
  made shift-free for spectroscopy by tuning a ratio the bench already
  controls, and the same ratio scans the trap-surface distance.
* The quadratic Zeeman injector: the hyperfine mismatch between 5S and 6S
  makes a bias field a calculable line shifter at 1.9 and 4.2 kHz per gauss
  squared for the two isotopes, from committed constants, a free calibration
  channel for any line-centre instrument on this bench.
* A characterised laser, as in scenario one, but now characterised through
  the same guided path that fibre experiments use, under the shared-path
  condition the candidate note states.

### The comparison for the group whose fibre it is

**The question is not whether the fibre is interesting. It is whether the
fibre arm earns its beam time and its exposure, or whether the cell alone is
enough.** Both columns below are what a new campaign delivers, and the second
row is the one that matters to a group whose own programme is Rydberg atoms
near a nanofibre and not spectroscopy.

| | cell alone | cell plus nanofibre |
|---|---|---|
| **what the host group keeps afterwards** | nothing on their platform. The results are ours | a per-run calibration of the surface-charge term at 6S sensitivity, an atom-based monitor of adsorbate dynamics on the fibre, the two-colour trap's magic power ratio for this transition, a quadratic-Zeeman line shifter, and a laser characterised through their own guided path |
| **what it measures about the fibre** | nothing | the **fibre diameter**, the tolerance no held paper states and which every guided quantity depends on, to between [30.73](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.04:sigma_diameter_nm") nm at the 2025 drifting lock and [0.67](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.0:sigma_diameter_nm") nm at the photon floor, marginalised over the drive amplitude the scan cannot know. The repaired lock decides where in that span the campaign sits, and its residual is unmeasured. Also the light-shift coefficient, and the surface coefficient $C_3$ which is the weakest of the three (`results/onf_lever_ranking.csv`). **The diameter is not only obtainable this way**: the group's own scanning electron microscope gives it without atoms, and the published proximity to the 352 nm mode cutoff is a sharp independent diagnostic. What the atoms add is the quantity that actually enters the physics, measured in situ under the conditions of use, rather than a fibre characterised before it was installed ([chapter 6](06_next-nanofibre.md)) |
| **fibre time** | none | **acquisition only**, about [0.23](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:temperature_ladder:hours") hours per lever across three levers. Alignment, setup and the trap settling the distance scan needs between rungs are **not costed**, and the producer says so. The interval the host group would actually be asked to grant is an open item, not this number |
| **fibre exposure** | none | what can be quoted is integration time: about [2.78](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.02") minutes per trace at the working precision, and [69](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.004") +- [16](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:onf:minutes_per_trace_0.004_err") at cell-matching precision, the half-span of the committed 25 to 40 counts per ms band. **The degradation that time causes is a different quantity and is an open item**: rubidium adsorption against exposure bounds the whole arm and nothing here converts one into the other ([chapter 6](06_next-nanofibre.md)) |
| **what it settles for us** | the collisional and light-shift coefficients, from bounds to measurements | the same, plus the laser-shape confound acted on retroactively |

**The cell campaign is scheduled and the fibre arm is not yet.** The cell side is eight days, D1 to D8, each with its content and its deliverable, ordered so a truncation at any point leaves the higher-priority conversions done ([the plan](../PLAN.md), section 9). The fibre side has its acquisition hours from the lever ranking and no day plan, so the interval it would occupy is not yet a stated number. That is an open item and not an omission from this table.

**The row that decides it is the first one, and it carries a condition that
belongs beside it.** The surface-charge calibration is available at
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
precision. The corrections themselves are in
[the guided-geometry record](../history/09_the-guided-geometry.md).

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
